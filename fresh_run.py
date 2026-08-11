"""
fresh_run.py
------------
Run the foundation pipeline in a completely separate folder (results_fresh/).
The original results/ folder is NEVER touched.

Usage:
    python fresh_run.py

Before running:
    1. Copy your 8 input files into results_fresh/ subfolders:

       results_fresh/Business_Analysis/BA_Structural_Scout.md
       results_fresh/Business_Analysis/BA_Deep_Analyst.md
       results_fresh/Data_Analysis/DA_Data_Extractor.md
       results_fresh/Data_Analysis/DA_Data_Reviewer.md
       results_fresh/Technology_Analysis/TA_Stack_Scout.md
       results_fresh/Technology_Analysis/TA_Deep_Analyst.md
       results_fresh/Application_Analysis/AA_App_Extractor.md
       results_fresh/Application_Analysis/AA_Quality_Review.md

    Optional (fallback if any agent file is missing):
       results_fresh/DEEP_SCAN_OUTPUT.md
       results_fresh/file_cache.json

Output will be written to:
    results_fresh/ForwardEngineering_Docs/   (20 documents)
    results_fresh/Foundation_KnowledgeGraph/ (5 documents)
"""

import sys
from pathlib import Path

FRESH_DIR = Path(__file__).parent / "results_fresh"

REQUIRED_FILES = [
    FRESH_DIR / "Business_Analysis"    / "BA_Structural_Scout.md",
    FRESH_DIR / "Business_Analysis"    / "BA_Deep_Analyst.md",
    FRESH_DIR / "Data_Analysis"        / "DA_Data_Extractor.md",
    FRESH_DIR / "Data_Analysis"        / "DA_Data_Reviewer.md",
    FRESH_DIR / "Technology_Analysis"  / "TA_Stack_Scout.md",
    FRESH_DIR / "Technology_Analysis"  / "TA_Deep_Analyst.md",
    FRESH_DIR / "Application_Analysis" / "AA_App_Extractor.md",
    FRESH_DIR / "Application_Analysis" / "AA_Quality_Review.md",
]

FALLBACK_FILES = [
    FRESH_DIR / "DEEP_SCAN_OUTPUT.md",
    FRESH_DIR / "file_cache.json",
]

def check_inputs():
    print("\n=== Checking input files in results_fresh/ ===\n")
    all_ok = True
    for f in REQUIRED_FILES:
        if f.exists() and f.stat().st_size > 0:
            print(f"  [OK]      {f.relative_to(FRESH_DIR)}")
        else:
            print(f"  [MISSING] {f.relative_to(FRESH_DIR)}")
            all_ok = False

    print()
    has_fallback = False
    for f in FALLBACK_FILES:
        if f.exists() and f.stat().st_size > 0:
            print(f"  [OK - fallback] {f.relative_to(FRESH_DIR)}")
            has_fallback = True
        else:
            print(f"  [missing - optional fallback] {f.relative_to(FRESH_DIR)}")

    if not all_ok:
        if has_fallback:
            print("\n  WARNING: Some agent files are missing.")
            print("  Pipeline will use DEEP_SCAN_OUTPUT.md or file_cache.json as fallback.")
            print("  Documents may be less complete than a full 8-file run.")
        else:
            print("\n  ERROR: Required input files are missing and no fallback available.")
            print("  Please copy your input files into results_fresh/ subfolders first.")
            print("  See instructions at the top of this file.")
            sys.exit(1)

    return all_ok

def run():
    print("\n" + "="*60)
    print("  FRESH RUN — Oracle HRMS Foundation Pipeline")
    print("  Output folder: results_fresh/")
    print("  Original results/ folder: UNTOUCHED")
    print("="*60)

    check_inputs()

    # Confirm before running
    print("\n  This will generate 25 documents into results_fresh/")
    print("  Old results/ folder will NOT be affected.\n")
    confirm = input("  Proceed? (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        print("  Aborted.")
        sys.exit(0)

    # Add pipeline folder to path and run
    pipeline_dir = Path(__file__).parent / "pipeline"
    sys.path.insert(0, str(pipeline_dir))

    from foundation_runner import run as foundation_run
    foundation_run(str(FRESH_DIR))

    print("\n" + "="*60)
    print("  DONE")
    print(f"  Forward Engineering Docs: {FRESH_DIR / 'ForwardEngineering_Docs'}")
    print(f"  Foundation Knowledge Graph: {FRESH_DIR / 'Foundation_KnowledgeGraph'}")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
