"""
Forward Engineering — Batch 2, Step 7: Security & Access Control Review
Kept as its OWN agent, deliberately not folded into Backend Dev — access-control
requirements are the thing most commonly and silently dropped when bundled with
general feature work. Reads the files Backend Dev just wrote (plus its own prior
patches, if any) and applies authentication/authorization on top of them.

STATIC/DYNAMIC prompt split — see backend_dev_runner.py's module docstring for
why: role framing + contract + scoped security doc are identical across calls
for this sprint and go via --append-system-prompt (cacheable); the current code
under review and any retry feedback genuinely change call to call, so they stay
in the actual turn.
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
You are the Security & Access Control Reviewer agent for ONE sprint (bounded context).
Your ONLY job is to apply authentication, authorization, and data-protection controls
to the code shown in the next message — do not change business logic, do not add
features.

Target stack: {target_stack}

Stack Mapping Contract (follow its authentication/access-control convention exactly):
{contract}

{learnings}

Sprint: {sprint_name}

Security requirements for this sprint (sections belonging to other sprints' bounded
contexts have already been trimmed out; cross-cutting sections are kept regardless
of sprint):
--- SECURITY ARCHITECTURE ---
{security_doc}

Output format: every file you modify (only the ones you change) using this exact
marker format, nothing else outside the markers:

=== FILE: <relative/path/from/project/root> ===
<full file content>

If no security changes are needed, output nothing (no file blocks at all).
"""

FIRST_PASS_TRIGGER = """\
Current files as written by the Backend Developer agent for this sprint — modify
ONLY where a security or access-control gap exists; re-emit the file in full even
if you only add a few lines:

{current_files}
"""

RETRY_TRIGGER = """\
IMPORTANT — this is a CORRECTION pass. A review found a specific security problem
with your previous output:
{feedback}
Fix ONLY this specific issue.

Current files for this sprint (backend + your own prior security patches):

{current_files}
"""


def run(sprint: dict, input_dir: str, output_dir: str, feedback: str = None) -> dict:
    sprint_name = sprint["name"]
    print(f"\n[Security Review] Sprint '{sprint_name}' — applying access control...")

    manifest = load_sprint_manifest(output_dir, sprint_name)
    backend_files = manifest.get("backend_files", [])
    if not backend_files:
        print("  [Skip] No backend files recorded for this sprint yet.")
        return {"status": "skipped", "reason": "no_backend_files"}

    target_stack = load_target_stack(output_dir)
    contract = load_prior_output(output_dir, "STACK_MAPPING_CONTRACT.md") or "(not available)"
    learnings_text = load_learnings_text(output_dir)
    learnings_block = f"\n{learnings_text}\n" if learnings_text else ""
    all_sprints = load_all_sprints(output_dir)

    if has_reverse_engineering_docs(input_dir):
        docs = load_reverse_engineering_docs(input_dir).get("forward_docs", {})
        security_doc = docs.get("13_SECURITY_ARCHITECTURE.md", "(not available)")
    else:
        lw = Path(output_dir) / "Lightweight_Docs"
        security_doc = (lw / "05_SECURITY_ACCESS_NOTES.md").read_text(encoding="utf-8") \
            if (lw / "05_SECURITY_ACCESS_NOTES.md").exists() else "(not available)"

    security_doc = scope_doc_to_sprint(security_doc, sprint, all_sprints)

    system_prompt = STATIC_PROMPT.format(
        sprint_name=sprint_name, target_stack=target_stack, contract=contract,
        learnings=learnings_block, security_doc=security_doc,
    )

    new_app_dir = Path(output_dir) / NEW_APP_DIRNAME
    # Own prior patches (if any) count as "current state" too — a file security
    # added outright (not just modified) wouldn't be in backend_files at all.
    files_in_scope = sorted(set(backend_files) | set(manifest.get("security_files", [])))
    current_files = read_files_bundle(str(new_app_dir), files_in_scope)

    if feedback:
        user_prompt = RETRY_TRIGGER.format(feedback=feedback, current_files=current_files)
    else:
        user_prompt = FIRST_PASS_TRIGGER.format(current_files=current_files)

    output = call_claude(user_prompt, label=f"Security Review — {sprint_name}", timeout=1200,
                          allow_tools=False, system_prompt=system_prompt, output_dir=output_dir)
    written = write_file_bundle(output, str(new_app_dir))

    manifest["security_files"] = sorted(set(manifest.get("security_files", [])) | set(written))
    save_sprint_manifest(output_dir, sprint_name, manifest)

    print(f"  {len(written)} files updated with security controls." if written
          else "  No security changes required.")
    return {"status": "done", "files_written": written}
