"""
Implicit Rules Runner — Step 3.5
Extracts business rules that exist OUTSIDE of PL/SQL procedure bodies:
  - Seed/reference data (lookup values, valid states, reference codes)
  - Oracle Forms field constraints (required, max length, LOV values)
  - PL/SQL comments containing rules (-- RULE:, -- BUSINESS:, -- CONSTRAINT:)
  - Hard-coded threshold values in SQL WHERE clauses and CHECK constraints

Writes: implicit_rules.json
This file is fed into all 4 Agent 1 runners as additional context so they
start with a complete picture of implicit business rules.

Runs AFTER Step 3 (scan_agent_runner) and BEFORE Steps 4-12 (analysis agents).
Resume-safe: if implicit_rules.json already exists, skips entirely.
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import call_claude, save_json, output_already_exists

OUTPUT_FILE = "implicit_rules.json"

SEED_DATA_PROMPT = """\
You are an expert Oracle HRMS analyst. Analyse the following seed/reference data SQL files
and extract ALL implicit business rules encoded in the data:

- Every lookup type and its valid values (e.g. EMPLOYEE_STATUS: ACTIVE, INACTIVE, TERMINATED)
- Every reference code table and what each code means
- Numeric reference values (e.g. probation_days=90, max_leave_days=30)
- Date-based rules encoded in seed data
- Hierarchy or ordering implied by sequence numbers

Return a JSON object:
{
  "lookup_values": [
    {"type": "LOOKUP_TYPE", "code": "CODE", "meaning": "MEANING", "source_file": "path"}
  ],
  "reference_rules": [
    {"rule": "description of implicit rule", "evidence": "exact value from data", "source_file": "path"}
  ]
}

Source files:
"""

FORM_CONSTRAINTS_PROMPT = """\
You are an expert Oracle Forms analyst. Analyse the following Oracle Forms XML files
and extract ALL field-level business rules and constraints:

- Required fields (REQUIRED=TRUE or MANDATORY)
- Maximum field lengths (MAXIMUM_LENGTH values)
- List of Values (LOV) constraints — what values a field can take
- Default values encoded in forms
- Field-level validation triggers (WHEN-VALIDATE-ITEM)
- Navigation rules that imply business process order

Return a JSON object:
{
  "form_constraints": [
    {
      "form": "form_name",
      "block": "block_name",
      "field": "field_name",
      "constraint_type": "REQUIRED|MAX_LENGTH|LOV|DEFAULT|VALIDATION",
      "constraint_value": "the actual constraint value",
      "source_file": "path"
    }
  ]
}

Source files:
"""

COMMENT_RULES_PROMPT = """\
You are an expert PL/SQL analyst. Scan the following PL/SQL source files for business rules
documented in comments. Extract:

- Lines starting with -- RULE:, -- BUSINESS:, -- CONSTRAINT:, -- NOTE:
- Comments that describe WHY logic exists (not just what it does)
- Comments containing numeric thresholds or limits
- TODO/FIXME comments that reveal known business rule gaps
- Comments describing regulatory or compliance requirements

Return a JSON object:
{
  "comment_rules": [
    {
      "rule": "the business rule from the comment",
      "comment_text": "exact comment text",
      "source_file": "path",
      "approximate_line": "line number if visible"
    }
  ]
}

Source files:
"""

SQL_CONSTRAINTS_PROMPT = """\
You are an expert Oracle database analyst. Analyse the following SQL schema files and extract
ALL implicit business rules encoded in the schema:

- CHECK constraints and what business rule they enforce
- NOT NULL constraints on columns (what is always required)
- UNIQUE constraints (what must be unique as a business rule)
- DEFAULT values (what the system assumes when not specified)
- Foreign key relationships that imply business ownership
- Sequence start/increment values that imply business rules

Return a JSON object:
{
  "schema_constraints": [
    {
      "table": "TABLE_NAME",
      "column": "COLUMN_NAME",
      "constraint_type": "CHECK|NOT_NULL|UNIQUE|DEFAULT|FK|SEQUENCE",
      "business_rule": "what business rule this enforces",
      "constraint_value": "the actual constraint definition",
      "source_file": "path"
    }
  ]
}

Source files:
"""


def _get_files_by_type(cache: dict) -> dict:
    """Categorize cached files by type for targeted extraction."""
    categories = {
        "seed_data": {},
        "forms": {},
        "plsql": {},
        "schema": {},
    }
    for path, content in cache.items():
        p = path.lower()
        if any(x in p for x in ["seed", "reference_data", "lookup", "data/"]):
            categories["seed_data"][path] = content
        elif any(p.endswith(ext) for ext in [".frmxml", ".xml", ".mmxml", ".pllxml"]):
            categories["forms"][path] = content
        elif any(p.endswith(ext) for ext in [".pks", ".pkb", ".pkg", ".prc", ".fnc", ".trg"]):
            categories["plsql"][path] = content
        elif p.endswith(".sql") and any(x in p for x in ["schema", "table", "create", "ddl", "constraint"]):
            categories["schema"][path] = content
        elif p.endswith(".sql"):
            categories["schema"][path] = content
    return categories


def _format_files_for_prompt(files: dict, max_chars: int = 80000) -> str:
    parts = []
    total = 0
    for path, content in files.items():
        entry = f"--- FILE: {path} ---\n{content[:10000]}\n"
        if total + len(entry) > max_chars:
            break
        parts.append(entry)
        total += len(entry)
    return "\n".join(parts)


def run(output_dir: str) -> dict:
    if output_already_exists(output_dir, OUTPUT_FILE):
        print(f"\n[Implicit Rules] Already done — skipping (found {OUTPUT_FILE})")
        existing = json.loads((Path(output_dir) / OUTPUT_FILE).read_text(encoding="utf-8"))
        return existing

    cache_path = Path(output_dir) / "file_cache.json"
    if not cache_path.exists():
        raise RuntimeError(f"file_cache.json not found at '{cache_path}'. Run Step 2 first.")

    with open(cache_path, encoding="utf-8") as f:
        cache = json.load(f)

    print(f"\n[Implicit Rules] Extracting implicit business rules from {len(cache)} files...")
    categories = _get_files_by_type(cache)

    results = {
        "lookup_values": [],
        "reference_rules": [],
        "form_constraints": [],
        "comment_rules": [],
        "schema_constraints": [],
        "summary": {
            "seed_files_scanned": len(categories["seed_data"]),
            "form_files_scanned": len(categories["forms"]),
            "plsql_files_scanned": len(categories["plsql"]),
            "schema_files_scanned": len(categories["schema"]),
        }
    }

    # Pass 1: Seed data
    if categories["seed_data"]:
        print(f"  [Implicit Rules] Pass 1: Seed/reference data ({len(categories['seed_data'])} files)...")
        prompt = SEED_DATA_PROMPT + _format_files_for_prompt(categories["seed_data"])
        response = call_claude(prompt, label="Implicit Rules — seed data", timeout=600)
        try:
            data = json.loads(response.strip())
            results["lookup_values"].extend(data.get("lookup_values", []))
            results["reference_rules"].extend(data.get("reference_rules", []))
            print(f"    Found: {len(results['lookup_values'])} lookup values, {len(results['reference_rules'])} reference rules")
        except Exception:
            m = re.search(r'\{[\s\S]*\}', response)
            if m:
                try:
                    data = json.loads(m.group())
                    results["lookup_values"].extend(data.get("lookup_values", []))
                    results["reference_rules"].extend(data.get("reference_rules", []))
                except Exception:
                    pass
    else:
        print("  [Implicit Rules] Pass 1: No seed data files found — skipping.")

    # Pass 2: Oracle Forms constraints
    if categories["forms"]:
        print(f"  [Implicit Rules] Pass 2: Oracle Forms constraints ({len(categories['forms'])} files)...")
        prompt = FORM_CONSTRAINTS_PROMPT + _format_files_for_prompt(categories["forms"])
        response = call_claude(prompt, label="Implicit Rules — forms", timeout=600)
        try:
            data = json.loads(response.strip())
            results["form_constraints"].extend(data.get("form_constraints", []))
            print(f"    Found: {len(results['form_constraints'])} form constraints")
        except Exception:
            m = re.search(r'\{[\s\S]*\}', response)
            if m:
                try:
                    data = json.loads(m.group())
                    results["form_constraints"].extend(data.get("form_constraints", []))
                except Exception:
                    pass
    else:
        print("  [Implicit Rules] Pass 2: No Oracle Forms files found — skipping.")

    # Pass 3: PL/SQL comment rules
    if categories["plsql"]:
        print(f"  [Implicit Rules] Pass 3: PL/SQL comment rules ({len(categories['plsql'])} files)...")
        prompt = COMMENT_RULES_PROMPT + _format_files_for_prompt(categories["plsql"])
        response = call_claude(prompt, label="Implicit Rules — comments", timeout=600)
        try:
            data = json.loads(response.strip())
            results["comment_rules"].extend(data.get("comment_rules", []))
            print(f"    Found: {len(results['comment_rules'])} comment rules")
        except Exception:
            m = re.search(r'\{[\s\S]*\}', response)
            if m:
                try:
                    data = json.loads(m.group())
                    results["comment_rules"].extend(data.get("comment_rules", []))
                except Exception:
                    pass
    else:
        print("  [Implicit Rules] Pass 3: No PL/SQL files found — skipping.")

    # Pass 4: SQL schema constraints
    if categories["schema"]:
        print(f"  [Implicit Rules] Pass 4: SQL schema constraints ({len(categories['schema'])} files)...")
        prompt = SQL_CONSTRAINTS_PROMPT + _format_files_for_prompt(categories["schema"])
        response = call_claude(prompt, label="Implicit Rules — schema", timeout=600)
        try:
            data = json.loads(response.strip())
            results["schema_constraints"].extend(data.get("schema_constraints", []))
            print(f"    Found: {len(results['schema_constraints'])} schema constraints")
        except Exception:
            m = re.search(r'\{[\s\S]*\}', response)
            if m:
                try:
                    data = json.loads(m.group())
                    results["schema_constraints"].extend(data.get("schema_constraints", []))
                except Exception:
                    pass
    else:
        print("  [Implicit Rules] Pass 4: No schema SQL files found — skipping.")

    # Update summary counts
    results["summary"]["total_rules_found"] = (
        len(results["lookup_values"]) +
        len(results["reference_rules"]) +
        len(results["form_constraints"]) +
        len(results["comment_rules"]) +
        len(results["schema_constraints"])
    )

    save_json(output_dir, OUTPUT_FILE, results)
    print(f"\n[Implicit Rules] Complete — {results['summary']['total_rules_found']} implicit rules extracted → {OUTPUT_FILE}")
    return results


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(args.output)
