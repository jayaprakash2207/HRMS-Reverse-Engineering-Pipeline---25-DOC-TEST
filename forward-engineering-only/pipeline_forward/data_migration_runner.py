"""
Forward Engineering — Batch 2, Step 9: Data Migration (CONDITIONAL)
Only relevant where a legacy system with real data is being replaced.

HONEST SCOPE LIMIT — this step does NOT connect to any real database or move
any real data. That would require live credentials, which this pipeline has no
safe mechanism to hold or use (a gap we flagged explicitly and have not solved).
What it DOES do: generate the migration script itself, as reviewable code, plus
a notes file stating in plain terms that a human with real database access must
run and verify it — first against a COPY of production data, never live data
directly.

Disabled by default. Only runs when the orchestrator is given --migrate-data.

STATIC/DYNAMIC prompt split — see backend_dev_runner.py's module docstring for
why: role framing + target stack + the legacy schema dump are identical
across every sprint's migration call this run (the schema isn't filtered per
sprint — same text, same truncation, every time) and go via
--append-system-prompt (cacheable); only the sprint identity and this
sprint's own new-file list genuinely change call to call.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fwd_base import (call_claude, load_target_stack, load_prior_output,
                       write_file_bundle, load_sprint_manifest, save_sprint_manifest)

NEW_APP_DIRNAME = "new_app"

STATIC_PROMPT = """\
You are the Data Migration agent for ONE sprint (bounded context). Write a migration
SCRIPT (not execute anything) that would move existing rows from the ORIGINAL schema
below into the NEW schema this sprint just built.

Target stack: {target_stack}

Original database objects (from the legacy system) — this sprint's relevant tables
may be a subset of this; use only what applies to the sprint named in the next
message:
{old_schema}

Write:
1. A migration script appropriate to the target stack's tooling (e.g. an Alembic
   migration for a Python/SQLAlchemy stack, a Flyway/Liquibase script, or plain SQL
   if no migration framework applies) that maps each old column to its new
   equivalent, including any type conversions.
2. A DATA_MIGRATION_NOTES.md explaining, in plain language for a non-specialist
   reader: what this script does, and that it MUST be run and verified against a
   COPY of the production data first (row-count and spot-check verification)
   before anyone runs it against live data. State plainly that this script does
   not include database credentials and none should ever be committed alongside it.

Output using this exact marker format, nothing else outside the markers:

=== FILE: <relative/path/from/project/root> ===
<full file content>
"""

TRIGGER = """\
Sprint: {sprint_name}

New schema just implemented this sprint (reference — do not modify):
{new_files}

Write the migration script and notes now.
"""


def run(sprint: dict, input_dir: str, output_dir: str, migrate_data: bool = False) -> dict:
    sprint_name = sprint["name"]

    if not migrate_data:
        print(f"\n[Data Migration] Sprint '{sprint_name}' — skipped (not requested; "
              "pass --migrate-data to the orchestrator to enable).")
        return {"status": "skipped", "reason": "not_requested"}

    old_db_path = Path(input_dir) / "Source_Extraction" / "Database.json"
    if not old_db_path.exists():
        print(f"\n[Data Migration] Sprint '{sprint_name}' — skipped (no legacy Database.json found; "
              "nothing to migrate from).")
        return {"status": "skipped", "reason": "no_legacy_schema"}

    print(f"\n[Data Migration] Sprint '{sprint_name}' — generating migration script (script only, "
          "no live database is touched by this step)...")

    target_stack = load_target_stack(output_dir)
    old_schema = old_db_path.read_text(encoding="utf-8")

    manifest = load_sprint_manifest(output_dir, sprint_name)
    backend_files = manifest.get("backend_files", [])
    new_app_dir = Path(output_dir) / NEW_APP_DIRNAME
    new_files_text = "\n".join(backend_files) if backend_files else "(no backend files recorded)"

    system_prompt = STATIC_PROMPT.format(target_stack=target_stack, old_schema=old_schema[:20000])
    user_prompt = TRIGGER.format(sprint_name=sprint_name, new_files=new_files_text)

    output = call_claude(user_prompt, label=f"Data Migration — {sprint_name}", timeout=1200,
                          allow_tools=False, system_prompt=system_prompt, output_dir=output_dir)
    written = write_file_bundle(output, str(new_app_dir))

    manifest["migration_files"] = sorted(set(manifest.get("migration_files", [])) | set(written))
    save_sprint_manifest(output_dir, sprint_name, manifest)

    print(f"  {len(written)} migration-related files written. NOT executed against any database.")
    return {"status": "done", "files_written": written}
