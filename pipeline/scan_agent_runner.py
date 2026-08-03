"""
Scan Agent Runner — Step 3
Reads file_cache.json, splits all files into chunks of 30, sends each chunk
to Claude for full extraction. Saves Chunk_N_Output.md immediately after each
chunk. Merges all chunks into DEEP_SCAN_OUTPUT.md when all chunks are done.

Resume logic: if Chunk_N_Output.md exists → skip that chunk.
              if DEEP_SCAN_OUTPUT.md exists → skip entire step.
"""

import json
import math
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import call_claude, output_already_exists

CHUNK_SIZE = 15
SCAN_DIR_NAME = "Scan"
DEEP_SCAN_FILE = "DEEP_SCAN_OUTPUT.md"

SCAN_CHUNK_PROMPT = """\
You are the Scan Agent. Your job is to read every file provided and extract
ALL of the following for each file:

- Every class, interface, enum, struct — with all fields and properties
- Every method signature AND full method body logic
- Every business rule, validation, constraint found in code
- Every dependency injected or referenced
- Every configuration key used
- Every database entity, table, column reference
- Every API endpoint, route, HTTP verb
- Every exception thrown and why
- Every external service called

Be thorough and complete. Do not summarise or skip anything.
This extraction is used by all downstream analysis agents — if you miss it
here, no agent will ever see it.

NUMERIC LITERALS — REPRODUCE, NEVER SUMMARISE:
Every number hard-coded in the logic IS a business rule, and it is unrecoverable
once dropped. Reproduce EVERY numeric literal exactly as written: rates AND the
boundaries they apply between AND the cumulative base amounts added to them,
plus thresholds, limits, caps, floors, multipliers, day/month counts, retention
periods and magic numbers.

When the code contains a bracket / tier / band / lookup table, output EVERY ROW
of it, with all columns. A rate on its own is useless — "22%" cannot be applied
without knowing which income range it covers and what fixed amount is added to
it, so a reader who has only the rates cannot reproduce the calculation and the
rule is effectively lost.

NEVER write "full table reproduced in code", "see code for values", "brackets as
per 2024 rates", or any other pointer BACK to the source. The source is exactly
what the downstream agents will not have. If a table has 7 rows and 3 columns,
write all 21 values.

Correct:
  Bracket 3, SINGLE: taxable 47,150-100,525 -> tax = 5,426 + (taxable - 47,150) * 0.22
Wrong:
  Progressive brackets (10%/12%/22%/24%/32%/35%/37%) - full tables in code

Format each file as:

=== FILE: <relative/path/to/file> ===
<your complete extraction>

Process every file below now.

"""


def _format_chunk(files: dict) -> str:
    parts = [SCAN_CHUNK_PROMPT]
    for path, content in files.items():
        MAX_FILE_CHARS = 50_000
        if len(content) > MAX_FILE_CHARS:
            content = content[:MAX_FILE_CHARS] + f"\n\n[... FILE TRUNCATED AT {MAX_FILE_CHARS} CHARS — {len(content) - MAX_FILE_CHARS} chars omitted ...]"
        parts.append(f"--- SOURCE: {path} ---\n{content}\n")
    return "\n".join(parts)


def _correct_chunk(
    chunk_file: "Path",
    chunk_paths: list,
    cache: dict,
    label: str,
    total_chunks: int,
) -> str:
    """
    After a chunk has been written (or loaded from disk on resume), check whether
    every expected file appears as an '=== FILE: <path> ===' marker.  If any are
    missing, re-scan only those files and append the result — up to 3 attempts.

    Returns the final (possibly corrected) content of the chunk file.
    """
    import re as _re

    MAX_ATTEMPTS = 3
    expected_count = len(chunk_paths)
    chunk_num = label  # e.g. "Chunk 02"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        content = chunk_file.read_text(encoding="utf-8", errors="replace")

        # Collect which paths already appear in the output
        found_paths = set(_re.findall(r"=== FILE:\s*(.+?)\s*===", content))

        missing = [p for p in chunk_paths if p not in found_paths]
        found_count = expected_count - len(missing)

        if not missing:
            # All files present — nothing to do
            break

        print(
            f"  [{chunk_num}/{total_chunks:02d}] Missing {len(missing)}/{expected_count} files"
            f" — re-scanning missing files..."
        )
        print(f"  [{chunk_num}/{total_chunks:02d}] Self-correction attempt {attempt}/{MAX_ATTEMPTS}...")

        missing_files = {p: cache[p] for p in missing}
        re_scan_prompt = _format_chunk(missing_files)
        extra_output = call_claude(
            re_scan_prompt,
            label=f"{chunk_num} correction {attempt}",
            timeout=2700,
        )

        # Append the extra output to the chunk file
        with chunk_file.open("a", encoding="utf-8") as fh:
            fh.write("\n\n")
            fh.write(extra_output)

    return chunk_file.read_text(encoding="utf-8", errors="replace")


def _check_file_truncation(
    chunk_file: "Path",
    chunk_paths: list,
    cache: dict,
    label: str,
    total_chunks: int,
) -> None:
    """
    Detect files whose extracted content in the chunk is significantly shorter
    than their raw source — indicating Claude truncated mid-file.

    For each such file, re-scan it alone in its own Claude call and append
    the recovered full extraction. Up to 2 attempts per file.

    Threshold: extracted chars < 30% of raw source chars (and raw > 500 chars).
    """
    import re as _re

    content = chunk_file.read_text(encoding="utf-8", errors="replace")
    truncated = []

    for fp in chunk_paths:
        raw_len = len(cache.get(fp, ""))
        if raw_len < 500:
            continue  # small file — not worth checking

        # Find extracted section for this file
        pattern = _re.compile(
            r"=== FILE:\s*" + _re.escape(fp) + r"\s*===(.*?)(?====\s*FILE:|\Z)",
            _re.DOTALL | _re.IGNORECASE,
        )
        m = pattern.search(content)
        if not m:
            continue  # already handled by _correct_chunk
        extracted_len = len(m.group(1).strip())

        # If extracted is less than 30% of raw source — likely truncated
        if extracted_len < raw_len * 0.30:
            truncated.append((fp, raw_len, extracted_len))

    if not truncated:
        return

    print(f"  [{label}/{total_chunks:02d}] Truncation check: {len(truncated)} file(s) appear truncated — re-scanning each individually...")

    for fp, raw_len, extracted_len in truncated:
        print(f"    Truncated: {fp} (raw={raw_len} chars, extracted={extracted_len} chars, {int(extracted_len/raw_len*100)}%)")
        for attempt in range(1, 3):
            single_prompt = (
                f"{SCAN_CHUNK_PROMPT}\n\n"
                f"IMPORTANT: Extract this file COMPLETELY — do not stop until the entire file is processed.\n\n"
                f"--- SOURCE: {fp} ---\n{cache[fp]}\n"
            )
            recovered = call_claude(
                single_prompt,
                label=f"{label} truncation-fix {fp[-30:]} attempt {attempt}",
                timeout=2700,
            )
            if recovered.strip():
                with chunk_file.open("a", encoding="utf-8") as fh:
                    fh.write(f"\n\n[TRUNCATION RECOVERY — attempt {attempt}]\n\n")
                    fh.write(recovered)
                print(f"    Recovered: {fp} — appended to chunk.")
                break


def run(output_dir: str) -> None:
    out = Path(output_dir)
    scan_dir = out / SCAN_DIR_NAME
    scan_dir.mkdir(parents=True, exist_ok=True)
    deep_scan_path = out / DEEP_SCAN_FILE

    # Resume: entire merge already done
    if deep_scan_path.exists() and deep_scan_path.stat().st_size > 0:
        print(f"\n[Scan Agent] DEEP_SCAN_OUTPUT.md exists — skipping entire step.")
        return

    # Load file cache
    cache_path = out / "file_cache.json"
    if not cache_path.exists():
        raise RuntimeError(
            f"file_cache.json not found: '{cache_path}'.\n"
            f"This is produced by Step 2 (Scan Once).\n"
            f"Likely cause: Step 2 hasn't completed for this --output folder, or --output points "
            f"somewhere different than where Step 2 actually wrote its results.\n"
            f"Fix: run Step 2 again, e.g.\n"
            f"  python run.py --source <your-source> --output \"{output_dir}\" --track setup"
        )

    with open(cache_path, encoding="utf-8") as f:
        cache = json.load(f)

    all_paths = list(cache.keys())
    total_files = len(all_paths)
    total_chunks = math.ceil(total_files / CHUNK_SIZE)

    print(f"\n[Scan Agent] {total_files} files → {total_chunks} chunks of {CHUNK_SIZE}")

    import re as _re

    # Process each chunk
    for chunk_idx in range(1, total_chunks + 1):
        chunk_file = scan_dir / f"Chunk_{chunk_idx:02d}_Output.md"
        label = f"Chunk {chunk_idx:02d}"

        start = (chunk_idx - 1) * CHUNK_SIZE
        end   = min(start + CHUNK_SIZE, total_files)
        chunk_paths = all_paths[start:end]
        chunk_files_dict = {p: cache[p] for p in chunk_paths}

        # Resume: chunk already done — validate it has the expected number of FILE markers
        if chunk_file.exists() and chunk_file.stat().st_size > 0:
            content_check = chunk_file.read_text(encoding="utf-8", errors="replace")
            found_markers = len(_re.findall(r"=== FILE:", content_check))
            expected_count = end - start
            if found_markers == 0:
                print(f"  [{label}/{total_chunks:02d}] Corrupted (no FILE markers) — reprocessing.")
                chunk_file.unlink()
            elif found_markers < expected_count:
                print(f"  [{label}/{total_chunks:02d}] Incomplete ({found_markers}/{expected_count} files) — running self-correction.")
                _correct_chunk(chunk_file, chunk_paths, cache, label, total_chunks)
                _check_file_truncation(chunk_file, chunk_paths, cache, label, total_chunks)
                print(f"  [{label}/{total_chunks:02d}] Self-correction done — skipping re-scan.")
                continue
            else:
                print(f"  [{label}/{total_chunks:02d}] Already done ({found_markers} files) — skipping.")
                continue

        print(f"  [{label}/{total_chunks:02d}] Processing files {start+1}–{end} ...")

        prompt = _format_chunk(chunk_files_dict)
        output = call_claude(prompt, label=f"Scan {label}", timeout=2700)

        chunk_file.write_text(output, encoding="utf-8")
        print(f"  [{label}/{total_chunks:02d}] Saved → {chunk_file}")

        # Self-correction: ensure every expected file has a marker
        _correct_chunk(chunk_file, chunk_paths, cache, label, total_chunks)
        # Truncation check: re-scan files whose extracted content is suspiciously short
        _check_file_truncation(chunk_file, chunk_paths, cache, label, total_chunks)

    # Merge all chunks into DEEP_SCAN_OUTPUT.md
    print(f"\n[Scan Agent] Merging {total_chunks} chunks into {DEEP_SCAN_FILE} ...")
    with open(deep_scan_path, "w", encoding="utf-8") as out_f:
        for chunk_idx in range(1, total_chunks + 1):
            chunk_file = scan_dir / f"Chunk_{chunk_idx:02d}_Output.md"
            if chunk_file.exists():
                out_f.write(chunk_file.read_text(encoding="utf-8"))
                out_f.write("\n\n")

    print(f"[Scan Agent] DEEP_SCAN_OUTPUT.md saved → {deep_scan_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True)
    args = p.parse_args()
    run(args.output)
