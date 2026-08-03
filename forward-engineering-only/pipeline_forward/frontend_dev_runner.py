"""
Forward Engineering — Batch 2, Step 8: Frontend Developer agent
Builds the screens/components for this sprint, wired to the API surface the
Backend Developer agent already produced. Reads backend files as REFERENCE ONLY
(to know what endpoints exist) — does not modify them.

STATIC/DYNAMIC prompt split — see backend_dev_runner.py's module docstring for
why: role framing + contract + scoped UI/UX doc are identical across calls for
this sprint and go via --append-system-prompt (cacheable); the backend
reference code and any retry feedback genuinely change call to call, so they
stay in the actual turn.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwd_base import (call_claude, load_target_stack, load_prior_output, load_learnings_text,
                       load_reverse_engineering_docs, has_reverse_engineering_docs,
                       load_all_sprints, scope_doc_to_sprint,
                       write_file_bundle, read_files_bundle,
                       load_sprint_manifest, save_sprint_manifest)

NEW_APP_DIRNAME = "new_app"

STATIC_PROMPT = """\
You are the Frontend Developer agent for ONE sprint (bounded context). Build the
screens/components needed for this sprint, wired to the backend API endpoints
already implemented (shown in the next message as reference — do not modify them).

Target stack: {target_stack}

Stack Mapping Contract (follow its frontend/UI convention if specified; otherwise
choose a convention consistent with the rest of the contract and state your choice
in a code comment at the top of the main entry file):
{contract}

{learnings}

Sprint: {sprint_name}

UI/UX requirements for this sprint (sections belonging to other sprints' bounded
contexts have already been trimmed out; cross-cutting sections are kept regardless
of sprint):
--- UI/UX SPECIFICATION ---
{uiux_doc}

Output format: every frontend file using this exact marker format, nothing else
outside the markers. Place frontend files under a "frontend/" folder at the
project root unless the stack mapping contract specifies a different convention.
Do NOT prefix paths with "new_app/" or "forward_results/" — those directories are
the root itself, already implied; repeating them creates a wrong, duplicated
nested path. Paths should look like "frontend/src/features/.../Foo.tsx", not
"new_app/frontend/..." or "src/...":

=== FILE: <relative/path/from/project/root> ===
<full file content>
"""

FIRST_PASS_TRIGGER = """\
Backend API surface for this sprint (reference only — do not modify these files):
{backend_reference}

Build this sprint's screens now. Output EVERY frontend file needed for it.
"""

RETRY_TRIGGER = """\
IMPORTANT — this is a CORRECTION pass, not the first attempt. A review found a
specific problem with your previous output:
{feedback}

Backend API surface for this sprint (reference only — do not modify these files):
{backend_reference}

Your own previous frontend output for this sprint is shown below. Fix ONLY this
specific issue — do not rewrite unrelated code. Output ONLY the file(s) you
actually change, using the marker format described above; leave every other file
untouched and unmentioned. If nothing here actually needs to change, output
nothing.

{current_files}
"""


def run(sprint: dict, input_dir: str, output_dir: str, feedback: str = None) -> dict:
    sprint_name = sprint["name"]
    print(f"\n[Frontend Dev] Sprint '{sprint_name}' — building screens...")

    target_stack = load_target_stack(output_dir)
    contract = load_prior_output(output_dir, "STACK_MAPPING_CONTRACT.md") or "(not available)"
    learnings_text = load_learnings_text(output_dir)
    learnings_block = f"\n{learnings_text}\n" if learnings_text else ""
    all_sprints = load_all_sprints(output_dir)

    if has_reverse_engineering_docs(input_dir):
        docs = load_reverse_engineering_docs(input_dir).get("forward_docs", {})
        uiux_doc = docs.get("20_UI_UX_SPECIFICATION.md", "(not available)")
    else:
        lw = Path(output_dir) / "Lightweight_Docs"
        uiux_doc = (lw / "04_UIUX_REFERENCE_NOTES.md").read_text(encoding="utf-8") \
            if (lw / "04_UIUX_REFERENCE_NOTES.md").exists() else "(not available)"

    uiux_doc = scope_doc_to_sprint(uiux_doc, sprint, all_sprints)

    system_prompt = STATIC_PROMPT.format(
        sprint_name=sprint_name, target_stack=target_stack, contract=contract,
        learnings=learnings_block, uiux_doc=uiux_doc,
    )

    manifest = load_sprint_manifest(output_dir, sprint_name)
    backend_files = manifest.get("backend_files", []) + manifest.get("security_files", [])
    new_app_dir = Path(output_dir) / NEW_APP_DIRNAME
    backend_reference = read_files_bundle(str(new_app_dir), backend_files) if backend_files \
        else "(no backend files recorded yet for this sprint)"

    if feedback:
        prior_files = read_files_bundle(str(new_app_dir), manifest.get("frontend_files", []))
        user_prompt = RETRY_TRIGGER.format(feedback=feedback, backend_reference=backend_reference,
                                            current_files=prior_files)
    else:
        user_prompt = FIRST_PASS_TRIGGER.format(backend_reference=backend_reference)

    output = call_claude(user_prompt, label=f"Frontend Dev — {sprint_name}", timeout=1800,
                          allow_tools=False, system_prompt=system_prompt, output_dir=output_dir)
    written = write_file_bundle(output, str(new_app_dir))

    if not written:
        if feedback:
            print("  No frontend changes were necessary for this fix.")
            return {"status": "done", "files_written": []}
        print("  [Warning] No files parsed from Frontend Dev output.")
        return {"status": "failed", "reason": "no_files_parsed"}

    manifest["frontend_files"] = sorted(set(manifest.get("frontend_files", [])) | set(written))
    save_sprint_manifest(output_dir, sprint_name, manifest)

    print(f"  {len(written)} frontend files written/updated.")
    return {"status": "done", "files_written": written}
