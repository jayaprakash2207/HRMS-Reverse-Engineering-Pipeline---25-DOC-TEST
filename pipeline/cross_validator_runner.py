"""
Cross-Track Validator — Step 12.5
Runs AFTER all 4 Agent 2 outputs are complete and BEFORE Foundation (Step 13).

Reads all 4 Agent 2 outputs simultaneously and finds:
  - Procedures in AA not documented in BA
  - Tables in DA not referenced in BA business rules
  - Business rules in BA with no matching table/column in DA
  - Packages in AA not covered by TA technology analysis
  - Cross-track contradictions (e.g. AA says 11 packages, TA says 9)

For each gap found: fetches the relevant source files from DEEP_SCAN → file_cache
and appends the recovered data to the relevant agent output file.

Resume-safe: if cross_validation_report.json already exists, skips entirely.
Writes: cross_validation_report.json
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import (call_claude, save_json, load_prior_output,
                         output_already_exists, extract_deep_scan_sections,
                         supplement_from_cache)

OUTPUT_FILE = "cross_validation_report.json"

CROSS_VALIDATION_PROMPT = """\
You are a cross-track validation agent. You have been given the outputs of 4 independent
analysis tracks (Business, Data, Technology, Application) for the same Oracle HRMS codebase.

Your job: find INCONSISTENCIES and GAPS between the tracks.

Specifically identify:
1. Procedures/packages mentioned in Application Analysis (AA) but NOT documented in Business Analysis (BA)
2. Tables documented in Data Analysis (DA) but NOT referenced in any BA business rule
3. Business rules in BA that reference columns/tables NOT found in DA
4. PL/SQL packages in AA whose procedures are NOT covered by Technology Analysis (TA)
5. Counts that don't match (e.g. AA says PKG_EMPLOYEE has 15 procedures, BA only documents 10)
6. Any domain/module in one track with NO corresponding coverage in another track

For each gap found, specify:
- which_track_has_it: the track that has the information
- which_track_is_missing_it: the track that should have it but doesn't
- entity_type: "procedure" | "table" | "business_rule" | "package" | "form"
- entity_name: exact name
- suggested_source_files: list of file paths that would contain the missing data
- severity: "HIGH" | "MEDIUM" | "LOW"

Return ONLY valid JSON:
{
  "gaps": [
    {
      "which_track_has_it": "AA",
      "which_track_is_missing_it": "BA",
      "entity_type": "procedure",
      "entity_name": "PKG_PAYROLL.PROCESS_PAYROLL_RUN",
      "suggested_source_files": ["path/to/PKG_PAYROLL.pkb"],
      "severity": "HIGH"
    }
  ],
  "contradictions": [
    {
      "description": "AA reports 15 procedures in PKG_EMPLOYEE but BA only documents 10",
      "track_a": "AA",
      "track_b": "BA",
      "entity": "PKG_EMPLOYEE",
      "severity": "MEDIUM"
    }
  ],
  "summary": "X gaps and Y contradictions found"
}

Return [] for gaps if none found. Return [] for contradictions if none found.

"""


def _load_agent2_outputs(output_dir: str) -> dict:
    """Load all 4 Agent 2 final outputs."""
    base = Path(output_dir)
    outputs = {}
    files = {
        "BA": ("Business_Analysis", "BA_Deep_Analyst.md"),
        "DA": ("Data_Analysis", "DA_Data_Reviewer.md"),
        "TA": ("Technology_Analysis", "TA_Deep_Analyst.md"),
        "AA": ("Application_Analysis", "AA_Quality_Review.md"),
    }
    for track, (folder, filename) in files.items():
        path = base / folder / filename
        if path.exists():
            outputs[track] = path.read_text(encoding="utf-8")
            print(f"  Loaded: {folder}/{filename} ({len(outputs[track])} chars)")
        else:
            outputs[track] = ""
            print(f"  Missing: {folder}/{filename} — cross-validation will be partial")
    return outputs


def _append_to_agent_output(output_dir: str, track: str, supplement: str, entity_name: str) -> None:
    """Append recovered content to the relevant agent output file."""
    track_map = {
        "BA": ("Business_Analysis", "BA_Deep_Analyst.md"),
        "DA": ("Data_Analysis", "DA_Data_Reviewer.md"),
        "TA": ("Technology_Analysis", "TA_Deep_Analyst.md"),
        "AA": ("Application_Analysis", "AA_Quality_Review.md"),
    }
    if track not in track_map:
        return
    folder, filename = track_map[track]
    path = Path(output_dir) / folder / filename
    if path.exists():
        existing = path.read_text(encoding="utf-8")
        addition = (
            f"\n\n---\n## [CROSS-VALIDATION SUPPLEMENT] — {entity_name}\n"
            f"*Added by cross-track validator — this data was present in another track "
            f"but missing from this document.*\n\n{supplement}\n"
        )
        path.write_text(existing + addition, encoding="utf-8")
        print(f"    Supplemented: {folder}/{filename} with data for {entity_name}")


def run(output_dir: str) -> dict:
    if output_already_exists(output_dir, OUTPUT_FILE):
        print(f"\n[Cross Validator] Already done — skipping (found {OUTPUT_FILE})")
        return json.loads((Path(output_dir) / OUTPUT_FILE).read_text(encoding="utf-8"))

    print("\n[Cross Validator] Loading all 4 Agent 2 outputs...")
    agent_outputs = _load_agent2_outputs(output_dir)

    loaded = [t for t, v in agent_outputs.items() if v]
    if len(loaded) < 2:
        print(f"  [Cross Validator] Only {len(loaded)} track(s) available — need at least 2 for cross-validation. Skipping.")
        result = {"gaps": [], "contradictions": [], "summary": "Skipped — insufficient track outputs", "tracks_validated": loaded}
        save_json(output_dir, OUTPUT_FILE, result)
        return result

    print(f"\n[Cross Validator] Running cross-track validation across {loaded} tracks...")

    # Build combined prompt
    combined = CROSS_VALIDATION_PROMPT
    for track, content in agent_outputs.items():
        if content:
            combined += f"\n\n## {track} Agent 2 Output\n\n{content[:25000]}"

    response = call_claude(combined, label="Cross Validator", timeout=900)

    # Parse response
    validation_result = {"gaps": [], "contradictions": [], "summary": "", "tracks_validated": loaded}
    try:
        parsed = json.loads(response.strip())
        validation_result.update(parsed)
    except Exception:
        m = re.search(r'\{[\s\S]*\}', response)
        if m:
            try:
                parsed = json.loads(m.group())
                validation_result.update(parsed)
            except Exception:
                validation_result["raw_response"] = response[:2000]

    gaps = validation_result.get("gaps", [])
    contradictions = validation_result.get("contradictions", [])
    print(f"  [Cross Validator] Found {len(gaps)} gap(s) and {len(contradictions)} contradiction(s)")

    # For each HIGH/MEDIUM severity gap — fetch source files and supplement the missing track
    high_gaps = [g for g in gaps if g.get("severity") in ("HIGH", "MEDIUM")]
    print(f"  [Cross Validator] Resolving {len(high_gaps)} HIGH/MEDIUM gap(s)...")

    for gap in high_gaps:
        missing_track = gap.get("which_track_is_missing_it", "")
        source_files = gap.get("suggested_source_files", [])
        entity_name = gap.get("entity_name", "unknown")

        if not source_files or not missing_track:
            continue

        print(f"    Fetching data for: {entity_name} → {missing_track} track")
        sections = extract_deep_scan_sections(output_dir, source_files)
        sections = supplement_from_cache(output_dir, source_files, sections)

        has_real = any(
            "[Not found in deep scan]" not in part
            for part in sections.split("=== FILE:")[1:]
        )
        if not has_real:
            print(f"    No source content found for {entity_name} — skipping supplement")
            continue

        # Ask Claude to extract the specific missing data
        extract_prompt = (
            f"Extract all information about '{entity_name}' from the following source files. "
            f"This data needs to be added to the {missing_track} analysis track. "
            f"Be specific and complete — include all procedures, rules, tables, or logic "
            f"related to '{entity_name}'.\n\n{sections}"
        )
        extracted = call_claude(extract_prompt, label=f"Cross-validate extract {entity_name}", timeout=600)

        if extracted.strip():
            _append_to_agent_output(output_dir, missing_track, extracted, entity_name)
            gap["resolved"] = True
        else:
            gap["resolved"] = False

    resolved = len([g for g in high_gaps if g.get("resolved")])
    print(f"  [Cross Validator] Resolved {resolved}/{len(high_gaps)} gaps")

    validation_result["resolved_count"] = resolved
    save_json(output_dir, OUTPUT_FILE, validation_result)
    print(f"\n[Cross Validator] Complete → {OUTPUT_FILE}")
    return validation_result


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(args.output)
