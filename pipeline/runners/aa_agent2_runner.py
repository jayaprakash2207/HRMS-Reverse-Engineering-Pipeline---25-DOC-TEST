"""
AA Agent 2 Runner — Quality Review
Validates AA Agent 1's output against source files from the deep scan.
Produces AA_Quality_Review.md with PASS / PARTIAL / FAIL verdicts.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_runner import (call_claude, load_layer1, load_file_cache,
                         build_file_map, extract_deep_scan_sections,
                         supplement_from_cache, detect_and_fill_gaps,
                         save_output, load_prior_output, output_already_exists)

PROMPT_FILE = Path(__file__).parent.parent.parent / "Prompts_Ready_To_Use" / "08_AA_Agent2_QualityReview.md"
OUTPUT_FILE = "AA_Quality_Review.md"

TURN1_INSTRUCTION = """\
You are AA Agent 2 — Quality Reviewer.

AA Agent 1 has produced an application architecture document (provided below).
Your job: validate it against the actual source files to check for completeness gaps.

Look at the FILE MAP and tell me which source files you need to spot-check:
- All .pkb files (to verify procedure counts match what Agent 1 reported)
- All .frmxml files (to verify form triggers and blocks)
- Any files Agent 1 mentioned but may have incompletely documented

Reply with ONLY a valid JSON array of file paths to spot-check. No explanation.

AA Agent 1 Output:
"""


def run(input_dir: str, output_dir: str, scan_dir: str = None) -> str:
    if output_already_exists(output_dir, OUTPUT_FILE):
        print(f"\n[AA Agent 2] Already done — skipping (found {OUTPUT_FILE})")
        return load_prior_output(output_dir, OUTPUT_FILE)

    agent1_output = load_prior_output(output_dir, "AA_App_Extractor.md")
    if not agent1_output:
        raise RuntimeError("AA Agent 1 output not found — run AA Agent 1 first.")

    print("\n[AA Agent 2] Quality Review — starting...")

    prompt_text = PROMPT_FILE.read_text(encoding="utf-8")

    # Two-turn: Turn 1 requests source files for spot-checking
    if scan_dir:
        try:
            layer1 = load_layer1(input_dir)
            file_cache = load_file_cache(scan_dir)
            file_map = build_file_map(layer1.get("source_code", []), file_cache)

            turn1_prompt = TURN1_INSTRUCTION + agent1_output + "\n\nFILE MAP:\n" + file_map
            print("  [AA Agent 2] Turn 1 — requesting spot-check files...")
            turn1_output = call_claude(turn1_prompt, label="AA Agent 2 Turn 1", timeout=300)

            try:
                requested_files = json.loads(turn1_output.strip())
                if not isinstance(requested_files, list):
                    raise ValueError
            except Exception:
                import re
                matches = re.findall(r'\[[\s\S]*?\]', turn1_output)
                requested_files = []
                for candidate in matches:
                    try:
                        parsed = json.loads(candidate)
                        if isinstance(parsed, list) and len(parsed) > len(requested_files):
                            requested_files = parsed
                    except Exception:
                        pass

            sections = extract_deep_scan_sections(scan_dir, requested_files) if requested_files else ""
            if sections:
                sections = supplement_from_cache(scan_dir, requested_files, sections)
            source_section = f"\n\n# Spot-Check Source Files\n\n{sections}" if sections else ""
        except Exception as e:
            print(f"  [AA Agent 2] Could not load scan files ({e}) — review from Agent 1 output only")
            source_section = ""
    else:
        source_section = ""

    prompt = (
        f"{prompt_text}\n\n"
        f"---\n\n"
        f"# Input: AA Agent 1 Full Output\n\n"
        f"{agent1_output}"
        f"{source_section}\n\n"
        f"Review the above output now. "
        f"Validate JSON, graph edges, evidence traceability, procedure counts vs source, and completeness. "
        f"Produce your PASS / PARTIAL / FAIL verdict with specific findings."
    )

    output = call_claude(prompt, label="AA Agent 2", timeout=1800)

    # Edge-case pass (resume-safe)
    if output_already_exists(output_dir, "AA_Quality_Review_Edge.md"):
        print("  [AA Agent 2] Edge-case pass already done — loading saved output...")
        edge_output = load_prior_output(output_dir, "AA_Quality_Review_Edge.md")
    else:
        print("  [AA Agent 2] Running edge-case pass...")
        edge_prompt = (
            f"{prompt_text}\n\n---\n\n"
            f"IMPORTANT: This is a SECOND independent analysis pass. Focus SPECIFICALLY on:\n"
            f"- Procedures that are defined but never called from forms (orphaned logic)\n"
            f"- Form triggers that call packages not mentioned in the primary analysis\n"
            f"- Package procedures with no corresponding form trigger\n"
            f"- Any PASS/PARTIAL/FAIL verdicts that should be revisited\n\n"
            f"# AA Agent 1 Output\n\n{agent1_output}"
            f"{source_section}\n\n"
            "Produce your second-pass quality review now, focusing on what the first pass may have missed."
        )
        edge_output = call_claude(edge_prompt, label="AA Agent 2 edge-case pass", timeout=1800)
        save_output(output_dir, "AA_Quality_Review_Edge.md", edge_output)

    merge_prompt = (
        "You have two independent Application Analysis quality review outputs.\n"
        "Merge them into one complete document:\n"
        "- Keep ALL verdicts and findings from Pass 1\n"
        "- Add any NEW procedures, triggers, or PARTIAL/FAIL findings from Pass 2\n"
        "- Mark newly added content with [EDGE-CASE-FOUND]\n"
        "- Do not duplicate content\n\n"
        f"# Pass 1 (Primary Review)\n\n{output}\n\n"
        f"# Pass 2 (Edge Case Focus)\n\n{edge_output}\n\n"
        "Produce the merged document now."
    )
    output = call_claude(merge_prompt, label="AA Agent 2 merge", timeout=1800)

    if scan_dir:
        print("  [AA Agent 2] Checking for gaps in output...")
        output = detect_and_fill_gaps(output, scan_dir, "AA Agent 2")
    save_output(output_dir, OUTPUT_FILE, output)
    print("[AA Agent 2] Complete.")
    return output


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input",  required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--scan-dir", required=True)
    args = p.parse_args()
    run(args.input, args.output, args.scan_dir)
