"""
Forward Engineering — Batch 2, Step 10: Test-Writer agent
Writes unit, integration, and end-to-end tests for everything built in this
sprint (backend + security + frontend), grounded in the original requirements.

STATIC/DYNAMIC prompt split — see backend_dev_runner.py's module docstring for
why: role framing + scoped requirements/use-cases are identical across calls
for this sprint and go via --append-system-prompt (cacheable); the current
sprint code and any retry feedback genuinely change call to call, so they stay
in the actual turn.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwd_base import (call_claude, load_target_stack, load_learnings_text,
                       load_reverse_engineering_docs, has_reverse_engineering_docs,
                       load_all_sprints, scope_doc_to_sprint,
                       write_file_bundle, read_files_bundle,
                       load_sprint_manifest, save_sprint_manifest)

NEW_APP_DIRNAME = "new_app"

STATIC_PROMPT = """\
You are the Test-Writer agent for ONE sprint (bounded context). Write unit,
integration, and end-to-end tests covering everything built for this sprint.

Target stack: {target_stack}

{learnings}

Sprint: {sprint_name}

Original requirements this sprint must satisfy (sections belonging to other
sprints' bounded contexts have already been trimmed out; cross-cutting sections
are kept regardless of sprint):
--- REQUIREMENTS ---
{requirements}

Use case / acceptance criteria relevant to this sprint:
--- USE CASES ---
{use_cases}

Write tests following the target stack's standard test framework and conventions
(e.g. pytest for Python, JUnit for Java, Jest for JS/TS). Cover: business rule
edge cases (not just the happy path), API contract compliance, and access-control
enforcement.

Output format: using this exact marker format, nothing else outside the markers.
Mirror the existing source layout shown in the next message under "All files
implemented for this sprint" — if the source lives under
"backend/src/main/java/...", its test belongs under "backend/src/test/java/..."
(same prefix), not directly under "src/test/java/...". Do NOT prefix paths with
"new_app/" or "forward_results/" — those directories are the root itself, already
implied; repeating them creates a wrong, duplicated nested path:

=== FILE: <relative/path/from/project/root> ===
<full file content>
"""

FIRST_PASS_TRIGGER = """\
All files implemented for this sprint (backend, security, frontend combined):
{all_files}

Write the tests now.
"""

RETRY_TRIGGER = """\
IMPORTANT — this is a CORRECTION pass. A review found a specific test gap:
{feedback}
Address ONLY this specific gap.

All files implemented for this sprint (backend, security, frontend combined):
{all_files}
"""


def run(sprint: dict, input_dir: str, output_dir: str, feedback: str = None) -> dict:
    sprint_name = sprint["name"]
    print(f"\n[Test-Writer] Sprint '{sprint_name}' — authoring tests...")

    target_stack = load_target_stack(output_dir)
    learnings_text = load_learnings_text(output_dir)
    learnings_block = f"\n{learnings_text}\n" if learnings_text else ""
    all_sprints = load_all_sprints(output_dir)

    if has_reverse_engineering_docs(input_dir):
        docs = load_reverse_engineering_docs(input_dir).get("forward_docs", {})
        requirements = docs.get("01_BRD.md", "(not available)")
        use_cases = docs.get("03_USE_CASE_SPECIFICATION.md", "(not available)")
    else:
        lw = Path(output_dir) / "Lightweight_Docs"
        requirements = (lw / "01_FEATURE_REQUIREMENTS_BRIEF.md").read_text(encoding="utf-8") \
            if (lw / "01_FEATURE_REQUIREMENTS_BRIEF.md").exists() else "(not available)"
        use_cases = requirements  # lightweight scenario folds acceptance criteria into the brief

    requirements = scope_doc_to_sprint(requirements, sprint, all_sprints)
    use_cases = scope_doc_to_sprint(use_cases, sprint, all_sprints)

    system_prompt = STATIC_PROMPT.format(
        sprint_name=sprint_name, target_stack=target_stack, learnings=learnings_block,
        requirements=requirements, use_cases=use_cases,
    )

    manifest = load_sprint_manifest(output_dir, sprint_name)
    all_sprint_files = (
        manifest.get("backend_files", []) + manifest.get("security_files", [])
        + manifest.get("frontend_files", [])
    )
    new_app_dir = Path(output_dir) / NEW_APP_DIRNAME
    all_files_text = read_files_bundle(str(new_app_dir), all_sprint_files) if all_sprint_files \
        else "(no files recorded for this sprint yet)"

    if feedback:
        user_prompt = RETRY_TRIGGER.format(feedback=feedback, all_files=all_files_text)
    else:
        user_prompt = FIRST_PASS_TRIGGER.format(all_files=all_files_text)

    output = call_claude(user_prompt, label=f"Test-Writer — {sprint_name}", timeout=1800,
                          allow_tools=False, system_prompt=system_prompt, output_dir=output_dir)
    written = write_file_bundle(output, str(new_app_dir))

    if not written:
        print("  [Warning] No test files parsed.")
        return {"status": "failed", "reason": "no_files_parsed"}

    manifest["test_files"] = sorted(set(manifest.get("test_files", [])) | set(written))
    save_sprint_manifest(output_dir, sprint_name, manifest)

    print(f"  {len(written)} test files written.")
    return {"status": "done", "files_written": written}
