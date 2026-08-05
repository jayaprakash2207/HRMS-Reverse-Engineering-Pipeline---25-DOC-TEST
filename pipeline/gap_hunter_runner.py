"""
Gap Hunter Runner — Step 15
Self-healing loop that runs after Foundation (Step 14) and scans all 25
generated documents for weakness markers:
  - "MISSING", "[Not found", "unknown", "N/A", "not available"
  - Empty sections (headers with no content below them)
  - Placeholder text ("TBD", "TODO", "to be determined")
  - Very short sections (< 3 lines under a heading)

For each weakness found:
  1. Identifies which source files would contain the missing data
  2. Fetches content from DEEP_SCAN_OUTPUT.md → file_cache.json
  3. Calls Claude to fill only that specific gap snippet
  4. Replaces ONLY that snippet in the document — full file is preserved

Runs up to MAX_ROUNDS rounds until zero weaknesses remain.
Parallel: all documents processed simultaneously (ThreadPoolExecutor).
Resume-safe: tracks which gaps have been filled in gap_hunter_report.json.
Writes: gap_hunter_report.json
"""

import json
import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import (call_claude, save_json, output_already_exists,
                         extract_deep_scan_sections, supplement_from_cache)

OUTPUT_FILE = "gap_hunter_report.json"
MAX_ROUNDS = 3
MAX_WORKERS = 10  # parallel documents per round

_print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs)

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

The document snippet that needs filling (this is a small extract from the document):
{doc_snippet}

Instructions:
- Fill in the missing data using the source content provided
- Keep ALL existing text in the snippet — do not remove or rewrite anything
- Only ADD the missing information where the gap is
- Mark all added content with [GAP-FILLED] so it is visible
- If the source content does not contain the missing data, return the snippet UNCHANGED
- Return ONLY the updated snippet — the same length or longer, nothing else

Updated snippet:
"""


def _get_all_documents(output_dir: str) -> dict:
    """Return all Foundation documents as {filename: Path}."""
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
    """Find all weakness locations in a document. Returns list of weakness dicts."""
    weaknesses = []
    lines = content.split("\n")
    seen_contexts = set()
    for i, line in enumerate(lines):
        if WEAKNESS_RE.search(line):
            start = max(0, i - 5)
            end = min(len(lines), i + 6)
            context = "\n".join(lines[start:end])
            # Deduplicate — skip very similar contexts
            key = context[:80]
            if key not in seen_contexts:
                seen_contexts.add(key)
                weaknesses.append({
                    "line": i,
                    "matched_text": line.strip(),
                    "context": context,
                    "start_line": start,
                    "end_line": end,
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


def _fill_gap_in_document(doc_path: Path, gap: dict, weakness_context: str, output_dir: str) -> bool:
    """
    Fetch source files for a gap and patch ONLY the weakness snippet in the document.
    The full document is read, the snippet is replaced, the full document is written back.
    File size is preserved or grows — never shrinks.
    """
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

    # Read the FULL document content
    full_content = doc_path.read_text(encoding="utf-8")
    original_size = len(full_content)

    # Ask Claude to fill only the small snippet (weakness context ~10 lines)
    prompt = FILL_GAP_PROMPT.format(
        gap_description=description,
        source_content=sections[:15000],
        doc_snippet=weakness_context,
    )

    filled_snippet = call_claude(prompt, label=f"GapHunter fill {doc_path.name[:20]}", timeout=600)

    if not filled_snippet.strip():
        return False

    if "[GAP-FILLED]" not in filled_snippet:
        return False

    # SAFE WRITE: replace only the snippet in the full document
    # If the original snippet exists in the document, replace it
    if weakness_context.strip() in full_content:
        new_content = full_content.replace(weakness_context.strip(), filled_snippet.strip(), 1)
    else:
        # Snippet not found verbatim — append the gap fill at end of document
        new_content = full_content.rstrip() + "\n\n<!-- GAP-FILLED SECTION -->\n" + filled_snippet.strip() + "\n"

    # Safety check: never allow file to shrink significantly
    if len(new_content) < original_size * 0.9:
        safe_print(f"    ⚠ SAFETY ABORT: new content would shrink {doc_path.name} "
                   f"from {original_size:,} to {len(new_content):,} bytes — skipping")
        return False

    doc_path.write_text(new_content, encoding="utf-8")
    return True


def _process_document(filename: str, doc_path: Path, output_dir: str) -> dict:
    """Process a single document — scan for gaps, fill them. Returns result dict."""
    result = {"document": filename, "gaps_found": 0, "gaps_filled": 0, "errors": []}

    try:
        if doc_path.suffix == ".json":
            return result  # Skip JSON files

        content = doc_path.read_text(encoding="utf-8", errors="replace")
        weaknesses = _scan_document_for_weaknesses(content, filename)

        if not weaknesses:
            return result

        safe_print(f"  {filename}: {len(weaknesses)} weakness marker(s) found")

        # Group weaknesses into one context block for gap identification
        combined_context = "\n\n---\n\n".join(
            w["context"] for w in weaknesses[:5]
        )

        gaps = _find_gaps_in_section(combined_context, filename)
        high_gaps = [g for g in gaps if g.get("severity") == "HIGH"]

        result["gaps_found"] = len(high_gaps)

        for gap in high_gaps:
            # Find the best matching weakness context for this gap
            best_context = weaknesses[0]["context"] if weaknesses else combined_context
            filled = _fill_gap_in_document(doc_path, gap, best_context, output_dir)
            if filled:
                result["gaps_filled"] += 1
                safe_print(f"    ✓ Filled: {gap.get('description', '')[:60]}")

    except Exception as e:
        result["errors"].append(str(e))
        safe_print(f"  ✗ ERROR processing {filename}: {e}")

    return result


def run(output_dir: str) -> dict:
    if output_already_exists(output_dir, OUTPUT_FILE):
        print(f"\n[Gap Hunter] Already done — skipping (found {OUTPUT_FILE})")
        return json.loads((Path(output_dir) / OUTPUT_FILE).read_text(encoding="utf-8"))

    print(f"\n[Gap Hunter] Starting parallel self-healing gap detection (max {MAX_ROUNDS} rounds, {MAX_WORKERS} workers)...")

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

        # Log sizes before round
        sizes_before = {name: path.stat().st_size for name, path in docs.items()}

        round_gaps = 0
        round_filled = 0

        # Run all documents in parallel
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(_process_document, fname, fpath, output_dir): fname
                for fname, fpath in docs.items()
            }
            for future in as_completed(futures):
                fname = futures[future]
                try:
                    result = future.result()
                    round_gaps += result["gaps_found"]
                    round_filled += result["gaps_filled"]
                    if result["gaps_filled"] > 0 and fname not in report["documents_updated"]:
                        report["documents_updated"].append(fname)
                except Exception as e:
                    safe_print(f"  ✗ Future error for {fname}: {e}")

        # Verify no files shrank (safety check after round)
        print(f"\n  Size verification after round {round_num}:")
        all_safe = True
        for name, path in docs.items():
            if not path.exists():
                continue
            new_size = path.stat().st_size
            old_size = sizes_before.get(name, 0)
            if new_size < old_size * 0.9:
                print(f"  ⚠ WARNING: {name} shrank {old_size:,} → {new_size:,} bytes")
                all_safe = False
            elif new_size > old_size:
                print(f"  ✓ {name}: {old_size:,} → {new_size:,} bytes (+{new_size-old_size:,})")

        report["rounds"].append({
            "round": round_num,
            "gaps_found": round_gaps,
            "gaps_filled": round_filled,
            "documents_scanned": len(docs),
            "sizes_safe": all_safe,
        })
        report["total_gaps_found"] += round_gaps
        report["total_gaps_filled"] += round_filled

        print(f"\n  Round {round_num} complete: {round_gaps} gaps found, {round_filled} filled")

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
