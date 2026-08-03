"""
Forward Engineering — Batch 2, Step 6: Backend Developer agent
Implements domain entities, business rules, and API endpoints for ONE sprint
(bounded context). Domain/Rules/API are merged into a single agent — they are
one continuous line of work; Security stays separate (see security_review_runner.py)
specifically because access-control requirements are easy to silently drop when
bundled with feature work.

The prompt is split into a STATIC part (sent via --append-system-prompt) and a
DYNAMIC part (sent as the actual turn). The static part — role framing, the
Stack Mapping Contract, and this sprint's scoped requirement docs — is
byte-identical across every call for this sprint (and the contract is
identical for the whole run), which makes it eligible for Claude Code's own
prompt caching. Only the parts that truly change call to call (retry feedback,
this agent's own prior output) go in the dynamic part. See fwd_base.call_claude
and pipeline/base_runner.claude_cmd for how this is wired.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwd_base import (call_claude, load_target_stack, load_learnings_text,
                       load_reverse_engineering_docs, has_reverse_engineering_docs,
                       load_prior_output, load_all_sprints, scope_doc_to_sprint,
                       write_file_bundle, read_files_bundle,
                       load_sprint_manifest, save_sprint_manifest)

NEW_APP_DIRNAME = "new_app"

STATIC_PROMPT = """\
You are the Backend Developer agent, working on ONE sprint (bounded context) of a
larger system. Implement ONLY what this sprint covers — domain entities, business
rules, and API endpoints — do not touch unrelated areas of the codebase.

Target stack: {target_stack}

Stack Mapping Contract — follow this exactly for conventions (persistence, routing,
DI, validation, naming, folder layout, error handling):
{contract}

{learnings}

Sprint: {sprint_name}
Why this sprint, and its place in the build order: {rationale}

Relevant requirements and design documents for this sprint (sections belonging to
other sprints' bounded contexts have already been trimmed out below; cross-cutting
sections are kept regardless of sprint):

--- DOMAIN MODEL ---
{domain_model}

--- DATA MODEL / SCHEMA ---
{data_model}

--- BUSINESS REQUIREMENTS ---
{brd}

--- API CONTRACT SPECIFICATION ---
{api_contract}

Output format: every file as plain text using this exact marker format, nothing
else outside the markers. Paths are relative to the project root the Scaffolder
already created — place new files alongside the existing structure, don't recreate
config files that already exist unless you are intentionally changing them. Do NOT
prefix paths with "new_app/" or "forward_results/" — those directories are the root
itself, already implied; repeating them creates a wrong, duplicated nested path. If
a backend/ subfolder already exists (check the existing structure), your paths
should start with "backend/", e.g. "backend/src/main/java/.../Foo.java" — not just
"src/...".

=== FILE: <relative/path/from/project/root> ===
<full file content>
"""

FIRST_PASS_TRIGGER = (
    "Implement this sprint now. Output EVERY file needed for it, following the "
    "format described above."
)

RETRY_TRIGGER = """\
IMPORTANT — this is a CORRECTION pass, not the first attempt. A review found a
specific problem with your previous output:
{feedback}

Your own previous output for this sprint is shown below. Fix ONLY this specific
issue — do not rewrite unrelated code. Output ONLY the file(s) you actually
change, using the marker format described above; leave every other file
untouched and unmentioned. If nothing here actually needs to change, output
nothing.

{current_files}
"""


def run(sprint: dict, input_dir: str, output_dir: str, feedback: str = None) -> dict:
    sprint_name = sprint["name"]
    print(f"\n[Backend Dev] Sprint '{sprint_name}' — implementing domain, rules, and API...")

    target_stack = load_target_stack(output_dir)
    contract = load_prior_output(output_dir, "STACK_MAPPING_CONTRACT.md") or "(not available)"
    learnings_text = load_learnings_text(output_dir)
    learnings_block = f"\n{learnings_text}\n" if learnings_text else ""
    all_sprints = load_all_sprints(output_dir)

    if has_reverse_engineering_docs(input_dir):
        docs = load_reverse_engineering_docs(input_dir).get("forward_docs", {})
        domain_model = docs.get("05_DOMAIN_MODEL.md", "(not available)")
        data_model = docs.get("07_DATA_MODEL_SPECIFICATION.md", "(not available)")
        brd = docs.get("01_BRD.md", "(not available)")
        api_contract = docs.get("11_API_CONTRACT_SPECIFICATION.md", "(not available)")
    else:
        lw = Path(output_dir) / "Lightweight_Docs"
        domain_model = (lw / "02_DOMAIN_DATA_MODEL_SKETCH.md").read_text(encoding="utf-8") \
            if (lw / "02_DOMAIN_DATA_MODEL_SKETCH.md").exists() else "(not available)"
        data_model = domain_model  # lightweight scenario folds these together
        brd = (lw / "01_FEATURE_REQUIREMENTS_BRIEF.md").read_text(encoding="utf-8") \
            if (lw / "01_FEATURE_REQUIREMENTS_BRIEF.md").exists() else "(not available)"
        api_contract = (lw / "03_API_SERVICE_SKETCH.md").read_text(encoding="utf-8") \
            if (lw / "03_API_SERVICE_SKETCH.md").exists() else "(not available)"

    domain_model = scope_doc_to_sprint(domain_model, sprint, all_sprints)
    data_model = scope_doc_to_sprint(data_model, sprint, all_sprints)
    brd = scope_doc_to_sprint(brd, sprint, all_sprints)
    api_contract = scope_doc_to_sprint(api_contract, sprint, all_sprints)

    system_prompt = STATIC_PROMPT.format(
        sprint_name=sprint_name, rationale=sprint.get("rationale", ""),
        target_stack=target_stack, contract=contract, learnings=learnings_block,
        domain_model=domain_model, data_model=data_model, brd=brd, api_contract=api_contract,
    )

    new_app_dir = Path(output_dir) / NEW_APP_DIRNAME
    manifest = load_sprint_manifest(output_dir, sprint_name)

    if feedback:
        prior_files = read_files_bundle(str(new_app_dir), manifest.get("backend_files", []))
        user_prompt = RETRY_TRIGGER.format(feedback=feedback, current_files=prior_files)
    else:
        user_prompt = FIRST_PASS_TRIGGER

    output = call_claude(user_prompt, label=f"Backend Dev — {sprint_name}", timeout=1800,
                          allow_tools=False, system_prompt=system_prompt, output_dir=output_dir)
    written = write_file_bundle(output, str(new_app_dir))

    if not written:
        if feedback:
            print("  No backend changes were necessary for this fix.")
            return {"status": "done", "files_written": []}
        print("  [Warning] No files parsed from Backend Dev output.")
        return {"status": "failed", "reason": "no_files_parsed"}

    manifest["backend_files"] = sorted(set(manifest.get("backend_files", [])) | set(written))
    save_sprint_manifest(output_dir, sprint_name, manifest)

    print(f"  {len(written)} backend files written/updated.")
    return {"status": "done", "files_written": written}
