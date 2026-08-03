"""
Forward Engineering — Batch 2, Step 12: Independent Review
Three reviewers run BLIND and IN PARALLEL — none sees the others' verdict —
so agreement is real signal, not one opinion echoed three times:
  1. Correctness  — does the code match the original requirements/business rules?
  2. Code Quality — structure, maintainability, Stack Mapping compliance?
  3. Security/Performance — access control and NFR targets held up?

Findings are reconciled deterministically in Python (not by another LLM call)
into ONE consolidated set of corrections, so the Fix loop gets one clear
instruction rather than three possibly-conflicting reports.

Each finding also carries a "layer" tag (backend/security/frontend/tests) so
run_forward_batch2.py's fix loop can re-invoke only the agent(s) actually
implicated by a finding instead of redoing the whole sprint every retry.

STATIC/DYNAMIC prompt split — see backend_dev_runner.py's module docstring for
why: role framing + scoped requirement docs are identical across calls and go
via --append-system-prompt (cacheable); the code under review and test results
genuinely change call to call, so they stay in the actual turn.
"""

import concurrent.futures
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwd_base import (call_claude, load_prior_output, load_reverse_engineering_docs,
                       has_reverse_engineering_docs, load_all_sprints, scope_doc_to_sprint,
                       read_files_bundle, load_sprint_manifest)

NEW_APP_DIRNAME = "new_app"
_VALID_LAYERS = {"backend", "security", "frontend", "tests"}

_VERDICT_JSON_INSTRUCTION = """\
Reply with ONLY a JSON object, no markdown, no explanation, in this exact shape:
{{"verdict": "PASS" or "CORRECTIONS_REQUIRED", "findings": [{{"layer": "backend|security|frontend|tests", "detail": "<specific, actionable finding>"}}]}}
"layer" must name whichever of backend/security/frontend/tests actually needs to
change to fix that finding (the fix loop uses this to know which agent to
re-invoke — pick the one that's actually wrong, not just where the symptom
showed up). An empty findings list is required if verdict is "PASS".
"""

CORRECTNESS_STATIC = """\
You are an independent reviewer checking CORRECTNESS ONLY — does this sprint's code
actually implement the original requirements and business rules? You do not see any
other reviewer's opinion; give your own independent verdict.

""" + _VERDICT_JSON_INSTRUCTION + """

Sprint: {sprint_name}

Original requirements (sections belonging to other sprints' bounded contexts have
already been trimmed out below; cross-cutting sections are kept regardless of
sprint):
{requirements}
"""

QUALITY_STATIC = """\
You are an independent reviewer checking CODE QUALITY AND MAINTAINABILITY ONLY —
structure, readability, and compliance with the stack's conventions. You do not see
any other reviewer's opinion; give your own independent verdict.

Stack Mapping Contract (the conventions this code must follow):
{contract}

""" + _VERDICT_JSON_INSTRUCTION + """

Sprint: {sprint_name}
"""

SECURITY_PERF_STATIC = """\
You are an independent reviewer checking SECURITY AND PERFORMANCE ONLY — is access
control correctly enforced, and are there obvious performance red flags against the
stated NFRs? You do not see any other reviewer's opinion; give your own independent
verdict.

""" + _VERDICT_JSON_INSTRUCTION + """

Sprint: {sprint_name}

Security requirements (sections belonging to other sprints' bounded contexts have
already been trimmed out below; cross-cutting sections are kept regardless of
sprint):
{security_doc}

NFR targets:
{nfr_doc}
"""

CORRECTNESS_DYNAMIC = """\
Real test results from actually running the test suite:
{test_results}

Code under review:
{code}
"""

QUALITY_DYNAMIC = """\
Code under review:
{code}
"""

SECURITY_PERF_DYNAMIC = """\
Code under review:
{code}
"""


def _parse_verdict(text: str) -> dict:
    try:
        data = json.loads(text.strip())
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        try:
            data = json.loads(m.group()) if m else {}
        except Exception:
            data = {}

    findings = []
    for f in data.get("findings", []):
        if isinstance(f, dict):
            layer = str(f.get("layer", "")).strip().lower()
            if layer not in _VALID_LAYERS:
                # Model didn't (or couldn't) name a specific layer — treat as
                # "could be anything" rather than silently defaulting to one
                # layer and possibly never re-invoking the agent actually at fault.
                layer = "all"
            findings.append({"layer": layer, "detail": str(f.get("detail", "")).strip()
                              or "(no detail given)"})
        else:
            findings.append({"layer": "all", "detail": str(f)})

    verdict = data.get("verdict", "CORRECTIONS_REQUIRED")
    if not findings and verdict != "PASS":
        findings = [{"layer": "all",
                     "detail": "Reviewer output could not be parsed — treating as unresolved."}]
    return {"verdict": verdict, "findings": findings}


def _load_all_sprint_code(output_dir: str, sprint_name: str) -> str:
    manifest = load_sprint_manifest(output_dir, sprint_name)
    all_files = (
        manifest.get("backend_files", []) + manifest.get("security_files", [])
        + manifest.get("frontend_files", []) + manifest.get("test_files", [])
    )
    new_app_dir = Path(output_dir) / NEW_APP_DIRNAME
    return read_files_bundle(str(new_app_dir), all_files) if all_files else "(no files recorded)"


def run(sprint: dict, input_dir: str, output_dir: str, test_result: dict) -> dict:
    sprint_name = sprint["name"]
    print(f"\n[Review] Sprint '{sprint_name}' — dispatching 3 independent reviewers in parallel...")

    code = _load_all_sprint_code(output_dir, sprint_name)
    test_summary = (
        f"Exit code: {test_result.get('returncode')}, passed={test_result.get('passed')}\n"
        f"stdout (tail): {test_result.get('stdout_tail', '')[-1500:]}\n"
        f"stderr (tail): {test_result.get('stderr_tail', '')[-1500:]}"
    )

    all_sprints = load_all_sprints(output_dir)
    docs = {}
    if has_reverse_engineering_docs(input_dir):
        docs = load_reverse_engineering_docs(input_dir).get("forward_docs", {})
    requirements = scope_doc_to_sprint(docs.get("01_BRD.md", "(not available)"), sprint, all_sprints)
    security_doc = scope_doc_to_sprint(docs.get("13_SECURITY_ARCHITECTURE.md", "(not available)"),
                                        sprint, all_sprints)
    nfr_doc = scope_doc_to_sprint(docs.get("14_NFR_SPECIFICATION.md", "(not available)"),
                                   sprint, all_sprints)
    contract_text = load_prior_output(output_dir, "STACK_MAPPING_CONTRACT.md") or "(not available)"

    system_prompts = {
        "correctness": CORRECTNESS_STATIC.format(sprint_name=sprint_name, requirements=requirements),
        "quality": QUALITY_STATIC.format(sprint_name=sprint_name, contract=contract_text),
        "security_performance": SECURITY_PERF_STATIC.format(
            sprint_name=sprint_name, security_doc=security_doc, nfr_doc=nfr_doc),
    }
    user_prompts = {
        "correctness": CORRECTNESS_DYNAMIC.format(test_results=test_summary, code=code),
        "quality": QUALITY_DYNAMIC.format(code=code),
        "security_performance": SECURITY_PERF_DYNAMIC.format(code=code),
    }

    def _call(name):
        return call_claude(user_prompts[name], label=f"Review[{name}] — {sprint_name}",
                            timeout=1200, allow_tools=False, system_prompt=system_prompts[name],
                            output_dir=output_dir)

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(_call, name): name for name in user_prompts}
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            try:
                results[name] = _parse_verdict(future.result())
            except Exception as exc:
                results[name] = {"verdict": "CORRECTIONS_REQUIRED",
                                  "findings": [{"layer": "all", "detail": f"Reviewer call failed: {exc}"}]}

    overall_pass = all(r["verdict"] == "PASS" for r in results.values())
    consolidated = []
    for name, r in results.items():
        if r["verdict"] != "PASS":
            for f in r["findings"]:
                consolidated.append({"source": name, "layer": f["layer"], "detail": f["detail"]})

    print(f"  Verdicts — correctness: {results['correctness']['verdict']}, "
          f"quality: {results['quality']['verdict']}, "
          f"security/performance: {results['security_performance']['verdict']}")

    return {
        "status": "done",
        "overall": "PASS" if overall_pass else "CORRECTIONS_REQUIRED",
        "raw_reviews": results,
        "consolidated_findings": consolidated,
    }
