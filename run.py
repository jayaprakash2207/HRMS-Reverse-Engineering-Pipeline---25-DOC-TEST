"""
Standard Forward Engineering Pipeline — Master Orchestrator
============================================================
Sequential pipeline — 13 steps, fully resumable at every checkpoint.
Step numbers below are what actually prints as "[STEP N]" at runtime —
keep this list in sync with the _banner() calls in orchestrate() below.

Steps:
  Step  0  — Rule Annotator    (Claude — auto-inject -- RULE: comments into source copies)
  Step  1  — Layer 1           (Python, no AI — extract names/signatures)
  Step  2  — Scan Once         (Python, no AI — cache every file in full)
  Step  3  — Scan Agent        (Claude, chunk by chunk — deep extract all files)
  Step  3.5— Implicit Rules    (Claude — extract seed/forms/comment/schema rules)
  Step  4  — BA Agent 1        (Claude T1+T2 — produce BA_Structural_Scout.md)
  Step  5  — BA Agent 2        (Claude T1+T2+edge — produce BA_Deep_Analyst.md)
  Step  6  — DA Agent 1        (Claude T1+T2 — produce DA_Data_Extractor.md)
  Step  7  — DA Agent 2        (Claude T1+T2+edge — produce DA_Data_Reviewer.md)
  Step  8  — TA Agent 1        (Claude T1+T2 — produce TA_Stack_Scout.md)
  Step  9  — TA Agent 2 Batch 1 (Claude — file list + first-half deep analysis)
  Step 10  — TA Agent 2 Batch 2 (Claude — second-half + synthesis + edge → TA_Deep_Analyst.md)
  Step 11  — AA Agent 1        (Claude T1+T2 — produce AA_App_Extractor.md)
  Step 12  — AA Agent 2        (Claude T1+T2+edge — produce AA_Quality_Review.md)
  Step 13  — Cross Validator   (Claude — cross-track consistency check, fills gaps)
  Step 14  — Foundation        (Claude, multi-agent — parallel generation + self-healing loop + quality gate)
  Step 15  — Gap Hunter        (Claude — self-healing loop, fills remaining weaknesses)

TA Agent 2 is split into two processes (steps 9-10) instead of one giant
Turn-2 call: step 9 gets the file list and deep-analyses the first half of
requested files; step 10 analyses the second half and runs the synthesis
pass. Each half is saved to disk immediately, so if step 10 fails, re-running
never redoes step 9's file list or first-half analysis — only the failed
piece is retried.

Usage:
  # Run full pipeline
  python run.py --source "https://github.com/org/repo" --output ./results

  # Run specific steps only (batch mode)
  python run.py --source "C:/path/to/repo" --output ./results --from-step 1 --to-step 3
  python run.py --source "C:/path/to/repo" --output ./results --from-step 4 --to-step 7
  python run.py --source "C:/path/to/repo" --output ./results --from-step 8 --to-step 13

  # Skip Layer 1 if already extracted
  python run.py --source "C:/path/to/repo" --output ./results --skip-layer1

Batch suggestions:
  Batch 1 (Setup)     : --from-step 1  --to-step 3   (Layer1 + Scan Once + Scan Agent)
  Batch 2 (Business)  : --from-step 4  --to-step 5   (BA Agent 1 + BA Agent 2)
  Batch 3 (Data)      : --from-step 6  --to-step 7   (DA Agent 1 + DA Agent 2)
  Batch 4 (Tech)      : --from-step 8  --to-step 10  (TA Agent 1, TA Agent 2 Batch 1+2)
  Batch 5 (App)       : --from-step 11 --to-step 12  (AA Agent 1 + AA Agent 2)
  Batch 5.5 (CrossVal): --from-step 13 --to-step 13  (Cross-track validator — Step 12.5)
  Batch 6 (Synthesis) : --from-step 14 --to-step 14  (Foundation KG + 25 docs + verify)
"""

import argparse
import subprocess
import sys
import time
import threading
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR   = Path(__file__).parent.resolve()
PIPELINE_DIR = SCRIPT_DIR / "pipeline"
RUNNERS_DIR  = PIPELINE_DIR / "runners"

# ── ANSI colours ───────────────────────────────────────────────────────────────
_USE_COLOR = sys.stdout.isatty()

def _c(code, text): return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text
def green(t):  return _c("32", t)
def yellow(t): return _c("33", t)
def red(t):    return _c("31", t)
def bold(t):   return _c("1",  t)
def cyan(t):   return _c("36", t)
def dim(t):    return _c("2",  t)

_TOTAL_STEPS = 15

def _banner(step, label):
    print(f"\n{'─' * 64}")
    print(bold(cyan(f"[STEP {step}/{_TOTAL_STEPS}]  {label}")))
    print(f"{'─' * 64}")


# ── Subprocess runner ──────────────────────────────────────────────────────────

def _run(cmd: list, label: str, timeout: int = 3600, cwd: str = None) -> dict:
    t0 = time.monotonic()
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            check=False, timeout=timeout, cwd=cwd,
        )
        return {
            "label":      label,
            "returncode": proc.returncode,
            "stdout":     proc.stdout or "",
            "stderr":     proc.stderr or "",
            "duration_s": time.monotonic() - t0,
        }
    except subprocess.TimeoutExpired:
        return {"label": label, "returncode": -1, "stdout": "",
                "stderr": f"Timed out after {timeout}s", "duration_s": time.monotonic() - t0}
    except Exception as exc:
        return {"label": label, "returncode": -1, "stdout": "",
                "stderr": str(exc), "duration_s": time.monotonic() - t0}


def _print_result(r: dict):
    ok  = r["returncode"] == 0
    dur = f"{r['duration_s']:.1f}s"
    sep = "=" * 64
    status = green("COMPLETE") if ok else red("FAILED")
    print(f"\n{sep}")
    print(f"{bold(r['label'])} — {status}  {dim('(' + dur + ')')}")
    print(sep)
    if r["stdout"].strip():
        for line in r["stdout"].rstrip().splitlines():
            print(f"  {line}")
    if not ok and r["stderr"].strip():
        # Python tracebacks put the actual exception message LAST, not
        # first — truncating from the front (the old behaviour) showed
        # nothing but stack frames and hid the one line that explains the
        # failure. Show the tail instead.
        stderr = r["stderr"].strip()
        shown = stderr[-2000:]
        if len(stderr) > 2000:
            shown = "...(truncated)...\n" + shown
        print(f"\n  {red('[stderr]')}\n{shown}")
    print()


def _run_or_exit(cmd: list, label: str, timeout: int = 3600, cwd: str = None) -> dict:
    r = _run(cmd, label, timeout, cwd=cwd)
    _print_result(r)
    if r["returncode"] != 0:
        print(red(f"\nPIPELINE STOPPED — {label} failed. Fix the issue and re-run."))
        sys.exit(1)
    return r


# ── Input resolver ─────────────────────────────────────────────────────────────

def _is_url(source: str) -> bool:
    s = source.lower()
    return s.startswith("http://") or s.startswith("https://") or s.startswith("git@")


def clone_repo(url: str, output_dir: Path) -> str:
    clone_dir = output_dir / "repo-clone" / "repo"
    clone_dir.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Cloning {url} → {clone_dir}")
    r = _run(["git", "clone", "--depth", "1", url, str(clone_dir)],
             label="git clone", timeout=600)
    _print_result(r)
    if r["returncode"] != 0:
        raise RuntimeError(f"Clone failed: {r['stderr'][:400]}")
    return str(clone_dir)


# ── Individual steps ───────────────────────────────────────────────────────────

py = sys.executable


def step_layer1(source: str, pipeline_out: Path) -> dict:
    pipeline_out.mkdir(parents=True, exist_ok=True)
    return _run_or_exit(
        [py, "-m", "layer1", "--source", source, "--output", str(pipeline_out)],
        label="[STEP 1] Layer 1 — Source Extraction",
        cwd=str(PIPELINE_DIR),
    )


def step_scan_once(repo_root: str, output_dir: Path) -> dict:
    cache_path = output_dir / "file_cache.json"
    if cache_path.exists() and cache_path.stat().st_size > 0:
        print(f"\n[STEP 2] Scan Once — already done (file_cache.json exists), skipping.")
        return {"label": "[STEP 2] Scan Once", "returncode": 0,
                "stdout": "skipped", "stderr": "", "duration_s": 0.0}
    return _run_or_exit(
        [py, str(PIPELINE_DIR / "scan_runner.py"),
         "--repo-root", repo_root, "--output", str(output_dir)],
        label="[STEP 2] Scan Once — Cache All Files",
    )


def step_scan_agent(output_dir: Path) -> dict:
    deep_scan = output_dir / "DEEP_SCAN_OUTPUT.md"
    if deep_scan.exists() and deep_scan.stat().st_size > 0:
        print(f"\n[STEP 3] Scan Agent — already done (DEEP_SCAN_OUTPUT.md exists), skipping.")
        return {"label": "[STEP 3] Scan Agent", "returncode": 0,
                "stdout": "skipped", "stderr": "", "duration_s": 0.0}
    return _run_or_exit(
        [py, str(PIPELINE_DIR / "scan_agent_runner.py"), "--output", str(output_dir)],
        label="[STEP 3] Scan Agent — Deep Extract All Files",
        timeout=7200,
    )


def _agent_step(runner: str, label: str, input_dir: Path, output_dir: Path,
                scan_dir: Path, timeout: int = 3600) -> dict:
    # --output is this agent's own subfolder (where its .md gets saved);
    # --scan-dir is the pipeline ROOT, where file_cache.json and
    # DEEP_SCAN_OUTPUT.md actually live. These are NOT the same directory —
    # passing only --output here used to make every agent look for
    # file_cache.json inside its own subfolder, where it never existed.
    return _run_or_exit(
        [py, str(RUNNERS_DIR / runner),
         "--input", str(input_dir), "--output", str(output_dir),
         "--scan-dir", str(scan_dir)],
        label=label,
        timeout=timeout,
    )


def step_rule_annotator(output_dir: Path) -> dict:
    index_path = output_dir / "annotated_index.json"
    if index_path.exists() and index_path.stat().st_size > 0:
        print(f"\n[STEP 0] Rule Annotator — already done (annotated_index.json exists), skipping.")
        return {"label": "[STEP 0] Rule Annotator", "returncode": 0,
                "stdout": "skipped", "stderr": "", "duration_s": 0.0}
    return _run_or_exit(
        [py, str(PIPELINE_DIR / "rule_annotator_runner.py"), "--output", str(output_dir)],
        label="[STEP 0] Rule Annotator — Auto-Inject Business Rule Comments",
        timeout=7200,
    )


def step_gap_hunter(output_dir: Path) -> dict:
    report_path = output_dir / "gap_hunter_report.json"
    if report_path.exists() and report_path.stat().st_size > 0:
        print(f"\n[STEP 15] Gap Hunter — already done (gap_hunter_report.json exists), skipping.")
        return {"label": "[STEP 15] Gap Hunter", "returncode": 0,
                "stdout": "skipped", "stderr": "", "duration_s": 0.0}
    return _run_or_exit(
        [py, str(PIPELINE_DIR / "gap_hunter_runner.py"), "--output", str(output_dir)],
        label="[STEP 15] Gap Hunter — Self-Healing Gap Detection Loop",
        timeout=5400,
    )


def step_implicit_rules(output_dir: Path) -> dict:
    implicit_path = output_dir / "implicit_rules.json"
    if implicit_path.exists() and implicit_path.stat().st_size > 0:
        print(f"\n[STEP 3.5] Implicit Rules — already done (implicit_rules.json exists), skipping.")
        return {"label": "[STEP 3.5] Implicit Rules", "returncode": 0,
                "stdout": "skipped", "stderr": "", "duration_s": 0.0}
    return _run_or_exit(
        [py, str(PIPELINE_DIR / "implicit_rules_runner.py"), "--output", str(output_dir)],
        label="[STEP 3.5] Implicit Rules — Extract Implicit Business Rules",
        timeout=1800,
    )


def step_cross_validator(output_dir: Path) -> dict:
    report_path = output_dir / "cross_validation_report.json"
    if report_path.exists() and report_path.stat().st_size > 0:
        print(f"\n[STEP 13] Cross Validator — already done (cross_validation_report.json exists), skipping.")
        return {"label": "[STEP 13] Cross Validator", "returncode": 0,
                "stdout": "skipped", "stderr": "", "duration_s": 0.0}
    return _run_or_exit(
        [py, str(PIPELINE_DIR / "cross_validator_runner.py"), "--output", str(output_dir)],
        label="[STEP 13] Cross Validator — Cross-Track Consistency Check",
        timeout=3600,
    )


def step_foundation(output_dir: Path) -> dict:
    return _run_or_exit(
        [py, str(PIPELINE_DIR / "foundation_runner_multiagent.py"), "--output", str(output_dir)],
        label="[STEP 14] Foundation — Knowledge Graph + 25 Documents + Multi-Agent Self-Healing",
        timeout=7200,
    )


# ── Final summary ──────────────────────────────────────────────────────────────

def _count(path: Path) -> int:
    return sum(1 for _ in path.rglob("*") if _.is_file()) if path.exists() else 0


def print_summary(output_dir: Path, all_results: list, total_s: float):
    sep = "═" * 64
    print(f"\n{sep}")
    print(bold(green("STANDARD FORWARD ENGINEERING PIPELINE — COMPLETE")))
    print(sep)

    print(f"\n{bold('Step results:')}")
    for r in all_results:
        icon = green("OK  ") if r["returncode"] == 0 else red("FAIL")
        dur = f"({r['duration_s']:.1f}s)"
        print(f"  {icon}  {r['label']}  {dim(dur)}")

    print(f"\n{bold('Output folders:')}")
    for label, folder in [
        ("Business Analysis",    output_dir / "Business_Analysis"),
        ("Data Analysis",        output_dir / "Data_Analysis"),
        ("Technology Analysis",  output_dir / "Technology_Analysis"),
        ("Application Analysis", output_dir / "Application_Analysis"),
        ("Foundation / KG",      output_dir / "Foundation_KnowledgeGraph"),
        ("Forward Engineering",  output_dir / "ForwardEngineering_Docs"),
    ]:
        n = _count(folder)
        status = green(f"{n:>3} files") if n > 0 else dim("  —  not created")
        print(f"  {status}  {label:<24}  {dim(str(folder))}")

    mins, secs = int(total_s // 60), int(total_s % 60)
    print(f"\n  Total wall time: {bold(f'{mins}m {secs}s')}")
    print(f"\n{bold('Output root:')}  {output_dir}")
    print(sep + "\n")


# ── Main orchestrator ──────────────────────────────────────────────────────────

def orchestrate(source: str, output_dir: Path, skip_layer1: bool,
                from_step: int = 1, to_step: int = _TOTAL_STEPS,
                track: str = None) -> int:
    output_dir   = output_dir.resolve()
    pipeline_out = output_dir / "Source_Extraction"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not _is_url(source):
        source = str(Path(source).resolve())

    all_results = []
    t0 = time.monotonic()

    print(f"\n{'═' * 64}")
    print(bold(cyan("STANDARD FORWARD ENGINEERING PIPELINE")))
    print(f"{'═' * 64}")
    print(f"  Source      : {source}")
    print(f"  Output root : {output_dir}")
    print(f"  Skip Layer1 : {skip_layer1}")
    if track:
        print(bold(yellow(f"  Track       : --track {track}  (steps {from_step}–{to_step})")))
    elif from_step > 1 or to_step < _TOTAL_STEPS:
        print(bold(yellow(f"  Batch mode  : steps {from_step} – {to_step} only")))
    print(f"{'═' * 64}\n")

    def _should_run(step: int) -> bool:
        return from_step <= step <= to_step

    def _skip(step: int, label: str):
        print(yellow(f"\n  [STEP {step}] {label} — skipped (outside batch range)"))
        return {"label": f"[STEP {step}] {label}", "returncode": 0,
                "stdout": "skipped (batch)", "stderr": "", "duration_s": 0.0}

    # Resolve local repo path (needed for steps 1-2; ok to skip for later batches)
    repo_root = source
    if _is_url(source) and _should_run(1):
        print(bold("Cloning remote repository..."))
        try:
            repo_root = clone_repo(source, output_dir)
            print(green(f"  Local repo: {repo_root}\n"))
        except RuntimeError as exc:
            print(red(f"  Clone failed: {exc}"))
            repo_root = ""
    elif _is_url(source):
        # Later batch — the clone must already exist
        clone_dir = output_dir / "repo-clone" / "repo"
        if clone_dir.exists():
            repo_root = str(clone_dir)

    # Output sub-folders
    ba_out = output_dir / "Business_Analysis"
    da_out = output_dir / "Data_Analysis"
    ta_out = output_dir / "Technology_Analysis"
    aa_out = output_dir / "Application_Analysis"
    for d in (ba_out, da_out, ta_out, aa_out):
        d.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Layer 1 ───────────────────────────────────────────────────────
    _banner(1, "Layer 1 — Deterministic Source Extraction")
    if not _should_run(1):
        all_results.append(_skip(1, "Layer 1"))
    elif skip_layer1:
        print(yellow("  Skipped (--skip-layer1)\n"))
        all_results.append({"label": "[STEP 1] Layer 1", "returncode": 0,
                             "stdout": "skipped", "stderr": "", "duration_s": 0.0})
    else:
        all_results.append(step_layer1(repo_root or source, pipeline_out))

    # ── Step 2: Scan Once ─────────────────────────────────────────────────────
    _banner(2, "Scan Once — Cache Every File (no truncation)")
    if not _should_run(2):
        all_results.append(_skip(2, "Scan Once"))
    else:
        all_results.append(step_scan_once(repo_root, output_dir))

    # ── Step 0: Rule Annotator (runs after file_cache.json is created in Step 2) ──
    print(f"\n{'─' * 64}")
    print(bold(cyan(f"[STEP 0/{_TOTAL_STEPS}]  Rule Annotator — Auto-Inject Business Rule Comments")))
    print(f"{'─' * 64}")
    if not _should_run(1):
        print(yellow(f"\n  [STEP 0] Rule Annotator — skipped (outside batch range)"))
        all_results.append({"label": "[STEP 0] Rule Annotator", "returncode": 0,
                             "stdout": "skipped (batch)", "stderr": "", "duration_s": 0.0})
    else:
        all_results.append(step_rule_annotator(output_dir))

    # ── Step 3: Scan Agent ────────────────────────────────────────────────────
    _banner(3, "Scan Agent — Deep Extract All Files (chunk by chunk)")
    if not _should_run(3):
        all_results.append(_skip(3, "Scan Agent"))
    else:
        all_results.append(step_scan_agent(output_dir))

    # ── Step 3.5: Implicit Rules (runs after scan agent, before analysis tracks) ──
    # Uses _should_run(3) because it's part of the "setup" track (steps 1-3)
    print(f"\n{'─' * 64}")
    print(bold(cyan(f"[STEP 3.5/{_TOTAL_STEPS}]  Implicit Rules — Extract Rules from Seeds/Forms/PL/SQL")))
    print(f"{'─' * 64}")
    if not _should_run(3):
        print(yellow(f"\n  [STEP 3.5] Implicit Rules — skipped (outside batch range)"))
        all_results.append({"label": "[STEP 3.5] Implicit Rules", "returncode": 0,
                             "stdout": "skipped (batch)", "stderr": "", "duration_s": 0.0})
    else:
        all_results.append(step_implicit_rules(output_dir))

    # ── Steps 4-12: Analysis tracks — run BA / DA / TA / AA in parallel ─────────
    # Each track reads only from shared read-only files (DEEP_SCAN_OUTPUT.md,
    # file_cache.json, Source_Extraction/, implicit_rules.json) and writes to its
    # own output folder. No cross-track dependencies until Step 13.

    # Determine which tracks have any steps in the requested range
    ba_needed = any(_should_run(s) for s in (4, 5))
    da_needed = any(_should_run(s) for s in (6, 7))
    ta_needed = any(_should_run(s) for s in (8, 9, 10))
    aa_needed = any(_should_run(s) for s in (11, 12))

    track_results = {}  # track_name -> list of result dicts
    lock = threading.Lock()

    def _run_ba():
        results = []
        _banner(4, "BA Agent 1 — Structural Scout  [PARALLEL]")
        if _should_run(4):
            results.append(_agent_step("ba_agent1_runner.py",
                                       "[STEP 4] BA Agent 1 — Structural Scout",
                                       pipeline_out, ba_out, output_dir))
        else:
            results.append(_skip(4, "BA Agent 1"))

        _banner(5, "BA Agent 2 — Deep Analyst  [PARALLEL]")
        if _should_run(5):
            results.append(_agent_step("ba_agent2_runner.py",
                                       "[STEP 5] BA Agent 2 — Deep Analyst",
                                       pipeline_out, ba_out, output_dir))
        else:
            results.append(_skip(5, "BA Agent 2"))
        with lock:
            track_results["ba"] = results

    def _run_da():
        results = []
        _banner(6, "DA Agent 1 — Data Extractor  [PARALLEL]")
        if _should_run(6):
            results.append(_agent_step("da_agent1_runner.py",
                                       "[STEP 6] DA Agent 1 — Data Extractor",
                                       pipeline_out, da_out, output_dir))
        else:
            results.append(_skip(6, "DA Agent 1"))

        _banner(7, "DA Agent 2 — Data Reviewer  [PARALLEL]")
        if _should_run(7):
            results.append(_agent_step("da_agent2_runner.py",
                                       "[STEP 7] DA Agent 2 — Data Reviewer",
                                       pipeline_out, da_out, output_dir))
        else:
            results.append(_skip(7, "DA Agent 2"))
        with lock:
            track_results["da"] = results

    def _run_ta():
        results = []
        _banner(8, "TA Agent 1 — Stack Scout  [PARALLEL]")
        if _should_run(8):
            results.append(_agent_step("ta_agent1_runner.py",
                                       "[STEP 8] TA Agent 1 — Stack Scout",
                                       pipeline_out, ta_out, output_dir))
        else:
            results.append(_skip(8, "TA Agent 1"))

        _banner(9, "TA Agent 2 Batch 1 — Deep Analyst  [PARALLEL]")
        if _should_run(9):
            results.append(_agent_step("ta_agent2_batch1_runner.py",
                                       "[STEP 9] TA Agent 2 Batch 1 — Deep Analyst",
                                       pipeline_out, ta_out, output_dir, timeout=9000))
        else:
            results.append(_skip(9, "TA Agent 2 Batch 1"))

        _banner(10, "TA Agent 2 Batch 2 — Deep Analyst  [PARALLEL]")
        if _should_run(10):
            results.append(_agent_step("ta_agent2_batch2_runner.py",
                                       "[STEP 10] TA Agent 2 Batch 2 — Deep Analyst",
                                       pipeline_out, ta_out, output_dir, timeout=14400))
        else:
            results.append(_skip(10, "TA Agent 2 Batch 2"))
        with lock:
            track_results["ta"] = results

    def _run_aa():
        results = []
        _banner(11, "AA Agent 1 — App Extractor  [PARALLEL]")
        if _should_run(11):
            results.append(_agent_step("aa_agent1_runner.py",
                                       "[STEP 11] AA Agent 1 — App Extractor",
                                       pipeline_out, aa_out, output_dir, timeout=3600))
        else:
            results.append(_skip(11, "AA Agent 1"))

        _banner(12, "AA Agent 2 — Quality Review  [PARALLEL]")
        if _should_run(12):
            results.append(_agent_step("aa_agent2_runner.py",
                                       "[STEP 12] AA Agent 2 — Quality Review",
                                       pipeline_out, aa_out, output_dir))
        else:
            results.append(_skip(12, "AA Agent 2"))
        with lock:
            track_results["aa"] = results

    # Launch all needed tracks simultaneously
    active_tracks = []
    if ba_needed:
        active_tracks.append(("BA", threading.Thread(target=_run_ba, daemon=True)))
    if da_needed:
        active_tracks.append(("DA", threading.Thread(target=_run_da, daemon=True)))
    if ta_needed:
        active_tracks.append(("TA", threading.Thread(target=_run_ta, daemon=True)))
    if aa_needed:
        active_tracks.append(("AA", threading.Thread(target=_run_aa, daemon=True)))

    if active_tracks:
        names = " + ".join(n for n, _ in active_tracks)
        print(f"\n{'═' * 64}")
        print(bold(cyan(f"PARALLEL ANALYSIS — running {names} simultaneously")))
        print(f"{'═' * 64}\n")
        for _, t in active_tracks:
            t.start()
        for name, t in active_tracks:
            t.join()
            print(green(f"  [{name} track] complete"))

    # Collect results in step order
    for key in ("ba", "da", "ta", "aa"):
        all_results.extend(track_results.get(key, []))

    # ── Step 13: Cross Validator ──────────────────────────────────────────────
    _banner(13, "Cross Validator — Cross-Track Consistency Check")
    if not _should_run(13):
        all_results.append(_skip(13, "Cross Validator"))
    else:
        all_results.append(step_cross_validator(output_dir))

    # ── Step 14: Foundation ───────────────────────────────────────────────────
    _banner(14, "Foundation — Knowledge Graph + 25 Documents + Verification + Consistency Check")
    if not _should_run(14):
        all_results.append(_skip(14, "Foundation"))
    else:
        all_results.append(step_foundation(output_dir))

    # ── Step 15: Gap Hunter ───────────────────────────────────────────────────
    _banner(15, "Gap Hunter — Self-Healing Gap Detection Loop")
    if not _should_run(15):
        all_results.append(_skip(15, "Gap Hunter"))
    else:
        all_results.append(step_gap_hunter(output_dir))

    # ── Summary ───────────────────────────────────────────────────────────────
    print_summary(output_dir, all_results, time.monotonic() - t0)

    failed = [r for r in all_results if r["returncode"] != 0]
    return 0 if not failed else 1


# ── Track map ─────────────────────────────────────────────────────────────────

_TRACKS = {
    "setup":       (1,  3),   # Layer 1 + Scan Once + Scan Agent + Implicit Rules
    "business":    (4,  5),   # BA Agent 1 + BA Agent 2 (+ edge-case pass)
    "data":        (6,  7),   # DA Agent 1 + DA Agent 2 (+ edge-case pass)
    "technology":  (8,  10),  # TA Agent 1 + TA Agent 2 Batch 1 + Batch 2 (+ edge-case pass)
    "application": (11, 12),  # AA Agent 1 + AA Agent 2 (+ edge-case pass)
    "validate":    (13, 13),  # Cross-track validator (Step 13)
    "foundation":  (14, 15),  # Foundation KG + 25 docs + verification + Gap Hunter
}


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Standard Forward Engineering Pipeline — fully automated reverse engineering.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline (recommended for first run)
  python run.py --source "https://github.com/dotnet-architecture/eShopOnWeb" --output ./results
  python run.py --source "C:/projects/legacy-app" --output ./results

  # Track mode — run one architecture domain at a time (RECOMMENDED)
  python run.py --source "C:/projects/legacy-app" --output ./results --track setup
  python run.py --source "C:/projects/legacy-app" --output ./results --track business
  python run.py --source "C:/projects/legacy-app" --output ./results --track data
  python run.py --source "C:/projects/legacy-app" --output ./results --track technology
  python run.py --source "C:/projects/legacy-app" --output ./results --track application
  python run.py --source "C:/projects/legacy-app" --output ./results --track foundation

  Available tracks:
    setup        steps 1–3   Layer 1 + Scan Once + Scan Agent + Implicit Rules  ~30 min
    business     steps 4–5   BA Agent 1 + BA Agent 2                            ~30 min
    data         steps 6–7   DA Agent 1 + DA Agent 2                            ~30 min
    technology   steps 8–10  TA Agent 1 + TA Agent 2 (Batch 1 + Batch 2)        ~30 min
    application  steps 11–12 AA Agent 1 + AA Agent 2                            ~30 min
    validate     step  13    Cross-track validator (gaps + contradictions)       ~15 min
    foundation   step  14    Foundation KG + 25 documents + verification         ~45 min

  # Step range mode — power users (re-run a single step, custom ranges)
  python run.py --source "C:/projects/legacy-app" --output ./results --from-step 9 --to-step 9
""",
    )
    parser.add_argument("--source",      required=True,
                        help="GitHub URL or local folder path")
    parser.add_argument("--output",      default="./forward-engineering-output",
                        help="Root output directory (default: ./forward-engineering-output)")
    parser.add_argument("--skip-layer1", action="store_true", default=False,
                        help="Skip Layer 1 extraction (use when already extracted)")
    parser.add_argument("--track",
                        choices=list(_TRACKS.keys()),
                        metavar="TRACK",
                        help=("Run one architecture track: "
                              + ", ".join(_TRACKS.keys())))
    parser.add_argument("--from-step",  type=int, default=None,
                        metavar="N",
                        help=f"First step to run (1–{_TOTAL_STEPS}). Ignored when --track is set.")
    parser.add_argument("--to-step",    type=int, default=None,
                        metavar="N",
                        help=f"Last step to run (1–{_TOTAL_STEPS}). Ignored when --track is set.")
    args = parser.parse_args()

    # Resolve from_step / to_step from --track or --from-step/--to-step
    if args.track:
        from_step, to_step = _TRACKS[args.track]
    else:
        from_step = args.from_step if args.from_step is not None else 1
        to_step   = args.to_step   if args.to_step   is not None else _TOTAL_STEPS

    if not (1 <= from_step <= _TOTAL_STEPS):
        parser.error(f"--from-step must be between 1 and {_TOTAL_STEPS} (14 = Foundation)")
    if not (1 <= to_step <= _TOTAL_STEPS):
        parser.error(f"--to-step must be between 1 and {_TOTAL_STEPS} (14 = Foundation)")
    if from_step > to_step:
        parser.error("--from-step cannot be greater than --to-step")

    code = orchestrate(
        source      = args.source,
        output_dir  = Path(args.output),
        skip_layer1 = args.skip_layer1,
        from_step   = from_step,
        to_step     = to_step,
        track       = args.track,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
