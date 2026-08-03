"""
Rule Annotator Runner — Step 0
Reads every PL/SQL, SQL, and Oracle Forms source file and automatically
injects structured -- RULE: comments into annotated copies stored in
annotated_sources/ subfolder of output_dir.

The pipeline then reads from annotated_sources/ instead of raw source,
so Step 3.5 (implicit_rules_runner) captures ALL inferred business rules —
not just the ones developers explicitly documented.

What it finds and annotates:
  - IF/CASE conditions that enforce a business constraint
  - RAISE_APPLICATION_ERROR calls (explicit business rule violations)
  - Hard-coded numeric/date thresholds (probation days, max leave, etc.)
  - Cursor/query WHERE clauses that filter by status or type
  - PL/SQL exceptions that have business meaning
  - Validation checks (NVL, DECODE, CASE WHEN checks on status columns)

Resume-safe: if annotated_sources/ already has files, skips entirely.
Writes: annotated_sources/<original_path> for every source file.
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import call_claude, output_already_exists

OUTPUT_MARKER = "annotated_sources"

ANNOTATE_PROMPT = """\
You are a PL/SQL business rule extraction expert. Read the following source file
and insert structured comments that document every business rule, constraint, and
validation you can infer from the code logic.

Rules for annotation:
1. Add -- RULE: <description> immediately above any IF/CASE condition that
   enforces a business constraint (e.g. status checks, balance checks, date checks)
2. Add -- RULE: <description> above any RAISE_APPLICATION_ERROR call
3. Add -- CONSTRAINT: <description> above any hard-coded threshold value
   (e.g. numbers like 90, 30, 365 used in business logic comparisons)
4. Add -- BUSINESS: <description> above any cursor or query WHERE clause
   that filters by status, type, or category columns
5. Add -- VALIDATION: <description> above any NVL/DECODE/CASE that performs
   a business validation

Rules for the descriptions:
- Write in plain English, not code
- Be specific: "Employee must be ACTIVE to process payroll" not "status check"
- If you cannot determine the business meaning, skip it — do not guess
- Do NOT change any existing code — only add comment lines
- Do NOT remove any existing comments
- Return the COMPLETE file with your annotations inserted

If the file has no business logic worth annotating (e.g. pure DDL, pure data),
return it unchanged.

Source file path: {file_path}

Source file content:
{content}
"""


def _already_annotated(output_dir: str) -> bool:
    annotated_dir = Path(output_dir) / OUTPUT_MARKER
    if not annotated_dir.exists():
        return False
    files = list(annotated_dir.rglob("*"))
    actual = [f for f in files if f.is_file()]
    return len(actual) > 0


def run(output_dir: str) -> dict:
    if _already_annotated(output_dir):
        annotated_dir = Path(output_dir) / OUTPUT_MARKER
        files = [f for f in annotated_dir.rglob("*") if f.is_file()]
        print(f"\n[Rule Annotator] Already done — skipping ({len(files)} annotated files exist)")
        return {"annotated": len(files), "skipped": 0}

    cache_path = Path(output_dir) / "file_cache.json"
    if not cache_path.exists():
        raise RuntimeError(f"file_cache.json not found at '{cache_path}'. Run Step 2 first.")

    with open(cache_path, encoding="utf-8") as f:
        cache = json.load(f)

    # Only annotate files that contain business logic
    ANNOTATE_EXTENSIONS = {".pkb", ".pks", ".pkg", ".prc", ".fnc", ".trg", ".sql"}
    SKIP_KEYWORDS = ["migration", "baseline", "V1.", "V2."]  # skip forward-eng migration files

    candidates = {}
    for path, content in cache.items():
        ext = Path(path).suffix.lower()
        if ext not in ANNOTATE_EXTENSIONS:
            continue
        if any(kw in path for kw in SKIP_KEYWORDS):
            continue
        if len(content.strip()) < 100:
            continue
        candidates[path] = content

    print(f"\n[Rule Annotator] Annotating {len(candidates)} source files with inferred business rules...")

    annotated_dir = Path(output_dir) / OUTPUT_MARKER
    annotated_dir.mkdir(parents=True, exist_ok=True)

    annotated_count = 0
    skipped_count = 0

    for path, content in candidates.items():
        # Check if already annotated in this run
        out_path = annotated_dir / path.replace("/", "_").replace("\\", "_")
        if out_path.exists():
            skipped_count += 1
            continue

        print(f"  Annotating: {path} ({len(content)} chars)...")
        prompt = ANNOTATE_PROMPT.format(file_path=path, content=content[:40000])

        try:
            annotated = call_claude(prompt, label=f"Annotate {Path(path).name}", timeout=600)
            if annotated.strip() and len(annotated) > 50:
                out_path.write_text(annotated, encoding="utf-8")
                annotated_count += 1
                # Count how many RULE/CONSTRAINT/BUSINESS/VALIDATION annotations were added
                rule_count = annotated.count("-- RULE:") + annotated.count("-- CONSTRAINT:") + \
                             annotated.count("-- BUSINESS:") + annotated.count("-- VALIDATION:")
                orig_count = content.count("-- RULE:") + content.count("-- CONSTRAINT:") + \
                             content.count("-- BUSINESS:") + content.count("-- VALIDATION:")
                new_rules = rule_count - orig_count
                print(f"    Done — {new_rules} new rule annotations added")
            else:
                # Save original if Claude returns empty
                out_path.write_text(content, encoding="utf-8")
                skipped_count += 1
        except Exception as e:
            print(f"    Skipped ({e}) — saving original")
            out_path.write_text(content, encoding="utf-8")
            skipped_count += 1

    # Also copy non-annotated files (forms XML, seed data) to annotated_sources unchanged
    for path, content in cache.items():
        out_path = annotated_dir / path.replace("/", "_").replace("\\", "_")
        if not out_path.exists():
            out_path.write_text(content, encoding="utf-8")

    # Write an index so downstream steps know the annotated paths
    index = {
        "annotated_count": annotated_count,
        "total_files": len(cache),
        "annotated_dir": str(annotated_dir),
        "file_map": {
            path: str(annotated_dir / path.replace("/", "_").replace("\\", "_"))
            for path in cache.keys()
        }
    }
    index_path = Path(output_dir) / "annotated_index.json"
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"\n[Rule Annotator] Complete — {annotated_count} files annotated, {skipped_count} unchanged")
    print(f"  Annotations saved to: {annotated_dir}")
    print(f"  Index written to: {index_path}")
    return {"annotated": annotated_count, "skipped": skipped_count}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(args.output)
