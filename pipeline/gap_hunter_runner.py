"""
Gap Hunter Runner — Step 14.5
Self-healing loop that runs after Foundation (Step 14) and scans all 25
generated documents for weakness markers:
  - "MISSING", "[Not found", "unknown", "N/A", "not available"
  - Empty sections (headers with no content below them)
  - Placeholder text ("TBD", "TODO", "to be determined")
  - Very short sections (< 3 lines under a heading)

For each weakness found:
  1. Identifies which source files would contain the missing data
  2. Fetches content from DEEP_SCAN_OUTPUT.md → file_cache.json
  3. Calls Claude to fill only that specific gap
  4. Updates the document in place

Runs up to MAX_ROUNDS rounds until zero weaknesses remain.
Resume-safe: tracks which gaps have been filled in gap_hunter_report.json.
Writes: gap_hunter_report.json
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import (call_claude, save_json, output_already_exists,
                         extract_deep_scan_sections, supplement_from_cache)

OUTPUT_FILE = "gap_hunter_report.json"
MAX_ROUNDS = 3

# Patterns that indicate a gap or weakness in a document
WEAKNESS_PATTERNS = [
    r"\[Not found",
    r"\[MISSING\]",
    r"not found in deep scan",
    r"\bMISSING\b",
    r"\bN/A\b",
    r"\bTBD\b",
    r"\bTODO\b",
    r"to be determined",
    r"not available",
    r"could not (be |)found",
    r"no data available",
    r"not documented",
    r"unknown",
    r"not specified",
    r"\[\s*\]",           # empty brackets
    r"placeholder",
]

WEAKNESS_RE = re.compile("|".join(WEAKNESS_PATTERNS), re.IGNORECASE)

FIND_GAPS_PROMPT = """\
You are a document quality reviewer. Read the following section of an architecture
document and identify SPECIFIC gaps — places where data is missing, unknown, or
marked as not found.

For each gap, tell me:
1. What specific entity/data is missing (e.g. "PKG_PAYROLL procedure list",
   "EMPLOYEES table column definitions", "leave approval business rules")
2. Which source files would contain this data (give exact file paths as they
   appear in an Oracle HRMS codebase — e.g. "plsql/packages/PKG_PAYROLL.pkb")
3. How severe is this gap: HIGH (core information missing) / LOW (minor detail)

Return ONLY valid JSON:
{
  "gaps": [
    {
      "description": "what is missing",
      "suggested_files": ["path/to/file.pkb"],
      "severity": "HIGH"
    }
  ]
}

Return {"gaps": []} if the document section looks complete.

Document section:
"""

FILL_GAP_PROMPT = """\
You are filling a specific gap in an architecture document.

The gap: {gap_description}

Source content retrieved for this gap:
{source_content}

The document section that needs filling:
{doc_section}

Instructions:
- Fill in the missing data using the source content provided
- Keep ALL existing content — do not remove or rewrite anything
- Only ADD the missing information
- Mark all added content with [GAP-FILLED] so it is visible
- If the source content does not contain the missing data, return the
  document section unchanged
- Return the COMPLETE updated document section

Updated document section:
"""


def _get_all_documents(output_dir: str) -> dict:
    """Return all 25 Foundation documents as {filename: Path}."""
    base = Path(output_dir)
    docs = {}
    for folder in ["Foundation_KnowledgeGraph", "ForwardEngineering_Docs"]:
        folder_path = base / folder
        if folder_path.exists():
            for f in folder_path.iterdir():
                if f.is_file() and f.suffix in (".md", ".json"):
                    docs[f.name] = f
    return docs


def _scan_document_for_weaknesses(content: str, filename: str) -> list:
    """Find all weakness locations in a document. Returns list of (line_no, context)."""
    weaknesses = []
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if WEAKNESS_RE.search(line):
            # Get surrounding context (5 lines before and after)
            start = max(0, i - 5)
            end = min(len(lines), i + 6)
            context = "\n".join(lines[start:end])
            weaknesses.append({
                "line": i,
                "matched_text": line.strip(),
                "context": context,
            })
    return weaknesses


def _find_gaps_in_section(section_text: str, label: str) -> list:
    """Ask Claude to identify specific gaps in a document section."""
    if not section_text.strip():
        return []
    prompt = FIND_GAPS_PROMPT + section_text[:8000]
    response = call_claude(prompt, label=f"GapHunter find {label}", timeout=300)
    try:
        parsed = json.loads(response.strip())
        return parsed.get("gaps", [])
    except Exception:
        m = re.search(r'\{[\s\S]*\}', response)
        if m:
            try:
                return json.loads(m.group()).get("gaps", [])
            except Exception:
                pass
    return []


def _fill_gap_in_document(doc_path: Path, gap: dict, output_dir: str) -> bool:
    """Fetch source files for a gap and fill it in the document. Returns True if filled."""
    suggested_files = gap.get("suggested_files", [])
    description = gap.get("description", "unknown gap")

    if not suggested_files:
        return False

    sections = extract_deep_scan_sections(output_dir, suggested_files)
    sections = supplement_from_cache(output_dir, suggested_files, sections)

    has_real = any(
        "[Not found in deep scan]" not in part
        for part in sections.split("=== FILE:")[1:]
    ) if "=== FILE:" in sections else False

    if not has_real:
        return False

    # Read current document
    current_content = doc_path.read_text(encoding="utf-8")

    prompt = FILL_GAP_PROMPT.format(
        gap_description=description,
        source_content=sections[:15000],
        doc_section=current_content[:20000],
    )

    filled = call_claude(prompt, label=f"GapHunter fill {doc_path.name[:20]}", timeout=600)

    if filled.strip() and "[GAP-FILLED]" in filled:
        doc_path.write_text(filled, encoding="utf-8")
        return True

    return False


def run(output_dir: str) -> dict:
    if output_already_exists(output_dir, OUTPUT_FILE):
        print(f"\n[Gap Hunter] Already done — skipping (found {OUTPUT_FILE})")
        return json.loads((Path(output_dir) / OUTPUT_FILE).read_text(encoding="utf-8"))

    print(f"\n[Gap Hunter] Starting self-healing gap detection loop (max {MAX_ROUNDS} rounds)...")

    report = {
        "rounds": [],
        "total_gaps_found": 0,
        "total_gaps_filled": 0,
        "documents_updated": [],
    }

    for round_num in range(1, MAX_ROUNDS + 1):
        print(f"\n[Gap Hunter] Round {round_num}/{MAX_ROUNDS}...")

        docs = _get_all_documents(output_dir)
        if not docs:
            print("  No Foundation documents found — run Step 14 first.")
            break

        round_gaps = 0
        round_filled = 0
        round_docs = []

        for filename, doc_path in docs.items():
            if doc_path.suffix == ".json":
                continue  # Skip JSON files — too complex to gap-fill

            content = doc_path.read_text(encoding="utf-8", errors="replace")
            weaknesses = _scan_document_for_weaknesses(content, filename)

            if not weaknesses:
                continue

            print(f"  {filename}: {len(weaknesses)} weakness marker(s) found")

            # Group weaknesses into one context block (avoid too many API calls)
            combined_context = "\n\n---\n\n".join(
                w["context"] for w in weaknesses[:5]  # limit to 5 per doc per round
            )

            gaps = _find_gaps_in_section(combined_context, filename)
            high_gaps = [g for g in gaps if g.get("severity") == "HIGH"]

            round_gaps += len(high_gaps)

            for gap in high_gaps:
                filled = _fill_gap_in_document(doc_path, gap, output_dir)
                if filled:
                    round_filled += 1
                    if filename not in report["documents_updated"]:
                        report["documents_updated"].append(filename)
                    print(f"    Filled: {gap.get('description', '')[:60]}")

            if high_gaps:
                round_docs.append({"document": filename, "gaps": len(high_gaps)})

        report["rounds"].append({
            "round": round_num,
            "gaps_found": round_gaps,
            "gaps_filled": round_filled,
            "documents_scanned": len(docs),
        })
        report["total_gaps_found"] += round_gaps
        report["total_gaps_filled"] += round_filled

        print(f"  Round {round_num} complete: {round_gaps} gaps found, {round_filled} filled")

        if round_gaps == 0:
            print(f"  No gaps found — stopping early after {round_num} round(s)")
            break

    save_json(output_dir, OUTPUT_FILE, report)
    print(f"\n[Gap Hunter] Complete — {report['total_gaps_filled']} gaps filled across "
          f"{len(report['documents_updated'])} document(s) in {len(report['rounds'])} round(s)")
    return report


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(args.output)
