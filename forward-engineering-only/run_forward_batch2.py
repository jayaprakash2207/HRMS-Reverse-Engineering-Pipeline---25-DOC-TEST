"""
Forward Engineering Pipeline — Batch 2: Per-Sprint Development Cycle
======================================================================
Runs AFTER run_forward.py (Batch 1) has produced a confirmed target stack,
a Stack Mapping contract, a scaffolded project, and an ordered SPRINT_BACKLOG.json.

For each sprint, in backlog order:
  6.  Backend Developer agent      — domain, business rules, API endpoints
  7.  Security Reviewer agent      — access control (kept separate on purpose)
  8.  Frontend Developer agent     — screens, wired to the backend's API surface
  9.  Data Migration (conditional) — only with --migrate-data; script only, never
                                      touches a real database
  10. Test-Writer agent            — unit / integration / e2e tests
  11. Test Executor                — REAL subprocess build + test run, no LLM
  12. Independent Review           — 3 blind, parallel reviewers, reconciled
  13. Fix loop                     — ONLY the agent(s) (6/7/8) a finding actually
                                      named are re-invoked, not all three every
                                      time — each reviewer/test-executor finding
                                      carries a "layer" tag for this. Capped at
                                      --max-retries. Every finding quotes the real
                                      tool output (both streams — mvn/npm/pytest
                                      report failures on stdout), because an agent
                                      cannot correct a defect it was not shown. If
                                      an attempt reproduces its input findings
                                      exactly, the fix didn't land: the next attempt
                                      escalates to all layers with an explicit
                                      no-progress notice rather than re-issuing a
                                      request already shown not to work.
  14. Learnings write-back         — root cause logged so later sprints don't
                                      repeat it

A sprint that still fails after the retry cap is marked FAILED_BLOCKED in the
sprint ledger and the run CONTINUES to independent sprints — one stuck sprint
does not stop the whole batch. Every write to the ledger is atomic (temp file +
rename) — a crash mid-write can never be mistaken for a completed sprint.

Interruption resume: each attempt's step-by-step progress (which of
backend/security/frontend/migration/test_writer/test_executor/review already
ran) is checkpointed to sprints/<slug>/progress.json as it happens. Killing the
batch mid-sprint (out of budget, network drop, Ctrl+C) and re-running the same
command resumes that attempt from the first step that hadn't finished yet,
instead of re-doing the whole sprint from "backend" again.

Usage:
  python run_forward_batch2.py --input ./results --output ./forward_results
  python run_forward_batch2.py --input ./results --output ./forward_results --migrate-data
  python run_forward_batch2.py --input ./results --output ./forward_results --max-retries 2
  python run_forward_batch2.py --input ./results --output ./forward_results --only "Basket Context"
"""

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "pipeline_forward"))
from fwd_base import (load_ledger, update_ledger_entry, append_learning,  # noqa: E402
                       load_sprint_progress, save_sprint_progress, clear_sprint_progress,
                       mark_step_done, sprint_output_missing)

import backend_dev_runner  # noqa: E402
import security_review_runner  # noqa: E402
import frontend_dev_runner  # noqa: E402
import data_migration_runner  # noqa: E402
import test_writer_runner  # noqa: E402
import test_executor_runner  # noqa: E402
import review_runner  # noqa: E402
import environment_check_runner  # noqa: E402
import scaffold_runner  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_USE_COLOR = sys.stdout.isatty()


def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def green(t): return _c("32", t)
def yellow(t): return _c("33", t)
def red(t): return _c("31", t)
def bold(t): return _c("1", t)
def cyan(t): return _c("36", t)
def dim(t): return _c("2", t)


def _banner(sprint_idx, total, name, attempt=None):
    label = f"SPRINT {sprint_idx}/{total} — {name}"
    if attempt:
        label += f"  (fix-loop attempt {attempt})"
    print(f"\n{'#' * 70}")
    print(bold(cyan(label)))
    print(f"{'#' * 70}")


def _load_sprint_backlog(output_dir: Path) -> list:
    path = output_dir / "SPRINT_BACKLOG.json"
    if not path.exists():
        print(red(f"\nERROR: {path} not found. Run Batch 1 (run_forward.py) first."))
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_BUILD_LAYERS = ("backend", "security", "frontend")

# Per-stream cap on the test output quoted into a fix-loop finding. Big enough for
# a Surefire failure block or a compiler error list — the agent cannot fix what it
# was not shown, and this excerpt lands in the (uncached) dynamic turn, so it does
# not disturb the static prompt's cacheability.
_FAILURE_EXCERPT_CHARS = 2000

_STALLED_NOTICE = (
    "Your previous correction pass did NOT change the outcome — the failures below "
    "reproduced identically, byte for byte. Do not repeat the same edit. Re-read the "
    "failing output carefully, question your earlier assumption about the cause, and "
    "if the real defect is in a file you did not touch last time, change that file "
    "instead."
)


# Substrings that identify a failure as environmental rather than a defect in the
# generated code. Matched against the exception text, so they must stay specific
# enough not to catch a genuine code problem. Note what is deliberately ABSENT:
# rate limits and transient network errors, because call_claude already retries
# those internally and a later attempt really can succeed.
_INFRA_ERROR_MARKERS = (
    "claude cli not found",
    "npm install -g @anthropic-ai/claude-code",
    "claude login",
    "not authenticated",
    "authentication_error",
    "invalid api key",
    "oauth token has expired",
)


class _InfrastructureFailure(Exception):
    """Aborts the WHOLE batch, not just one sprint.

    An unresolvable or unauthenticated Claude CLI fails every sprint identically
    and instantly. Letting the loop continue turns one missing tool into a backlog
    where every sprint is marked FAILED_BLOCKED — which then gets SKIPPED on the
    next run (main() skips terminal statuses, and sprint_output_missing() returns
    False when no manifest was ever written), so the run silently does nothing
    until someone hand-resets the ledger. Stop at the first one instead.
    """


def _is_infrastructure_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(marker in text for marker in _INFRA_ERROR_MARKERS)


def _feedback_text(findings: list) -> str:
    return "\n".join(f"- [{f.get('source', '?')}] {f['detail']}" for f in findings)


def _test_failure_detail(test_result: dict) -> str:
    """Describe a test failure in terms an agent can act on.

    This used to quote `stderr_tail` only, which is close to useless: mvn, npm and
    pytest all write compile errors and failing-assertion reports to STDOUT, so the
    finding almost always read "Real test run failed (exit code 1):" with nothing
    after the colon — the fix loop then asked an agent to correct a defect it had
    never been shown, and every retry reproduced the same failure. Quote both
    streams, and say where the full log lives when neither has anything.
    """
    if test_result.get("status") == "done":
        parts = [f"Real test run failed (exit code {test_result.get('returncode')})."]
    else:
        reason = test_result.get("message") or test_result.get("reason") or "unknown"
        parts = [f"Test execution failed: {reason}."]

    for stream in ("stdout", "stderr"):
        tail = (test_result.get(f"{stream}_tail") or "").strip()
        if tail:
            parts.append(f"--- {stream} (tail) ---\n{tail[-_FAILURE_EXCERPT_CHARS:]}")

    if len(parts) == 1:
        parts.append(f"(the test runner captured no output; full log: "
                      f"{test_result.get('log_path', 'sprints/<sprint>/test_log.txt')})")
    return "\n".join(parts)


def _findings_signature(findings: list) -> str:
    """Stable identity for a finding set, so an attempt that reproduced exactly the
    failures it was asked to fix can be recognized as having made no progress.

    The no-progress notice itself is excluded: it is commentary the loop injected,
    not an observed failure. Counting it would make an escalated attempt's finding
    set differ from the plain one that follows, and a second consecutive stall would
    then go undetected."""
    return json.dumps(sorted(
        (f.get("layer", ""), f.get("detail", "")) for f in findings
        if f.get("detail") != _STALLED_NOTICE
    ))


def _implicated_layers(findings: list) -> set:
    """Which of backend/security/frontend actually need to be re-invoked, based
    on the layer tag each finding carries. A "tests"-only finding doesn't imply
    any of these need to change (Test-Writer always re-runs regardless); an
    "all"/unrecognized layer means we genuinely can't tell, so — same as the
    old behavior — implicate everything rather than risk skipping the real
    culprit."""
    layers = set()
    for f in findings:
        if f["layer"] == "all":
            return set(_BUILD_LAYERS)
        if f["layer"] in _BUILD_LAYERS:
            layers.add(f["layer"])
    return layers


def _seed_next_attempt(output_dir: str, sprint_name: str, next_attempt: int, findings: list) -> None:
    """Persist what the NEXT attempt needs to know (which findings caused the
    retry, which layers they implicate) before that attempt starts — so if the
    process dies between attempts, or partway through the next one, a restart
    still has this instead of losing it (it only ever lived in a local
    variable before)."""
    # An EMPTY list is a real, meaningful answer here — "no build layer needs to
    # change, only the Test-Writer does" — so it must be stored as-is. It used to
    # be `or list(_BUILD_LAYERS)`, which turned every tests-only finding into a
    # full backend+security+frontend rewrite: the opposite of what
    # _implicated_layers computes, and a chance to break working code. Only a
    # genuinely empty finding set (which shouldn't happen on a retry) falls back
    # to "re-run everything".
    implicated = sorted(_implicated_layers(findings)) if findings else list(_BUILD_LAYERS)
    save_sprint_progress(output_dir, sprint_name, {
        "attempt": next_attempt, "completed_steps": [], "test_result": None, "review": None,
        "findings": findings, "implicated": implicated,
    })


def _run_one_sprint(sprint: dict, input_dir: str, output_dir: str,
                     migrate_data: bool, max_retries: int) -> str:
    """Returns final status string: PASSED | FAILED_BLOCKED"""
    sprint_name = sprint["name"]

    # Resume mid-flight if a previous run was interrupted while this sprint was
    # IN_PROGRESS — ledger "attempts" = attempts completed BEFORE the one that
    # got interrupted, so that attempt is where we pick back up. Anything else
    # (fresh sprint, or a stale ledger entry) starts clean at attempt 1.
    prior_ledger_entry = load_ledger(output_dir).get(sprint_name, {})
    if prior_ledger_entry.get("status") == "IN_PROGRESS":
        start_attempt = prior_ledger_entry.get("attempts", 0) + 1
    else:
        start_attempt = 1

    for attempt in range(start_attempt, max_retries + 2):  # attempt 1 = first try, then up to max_retries fixes
        is_retry = attempt > 1
        progress = load_sprint_progress(output_dir, sprint_name, attempt)
        resuming = bool(progress["completed_steps"])

        if resuming:
            print(yellow(f"\n  -- Resuming '{sprint_name}' attempt {attempt} after an interruption "
                         f"(already done this attempt: {progress['completed_steps']}) --"))
        elif is_retry:
            print(yellow(f"\n  -- Fix-loop attempt {attempt - 1}/{max_retries} for '{sprint_name}' --"))

        update_ledger_entry(output_dir, sprint_name, status="IN_PROGRESS", attempts=attempt - 1)

        findings = progress.get("findings") or []
        # Distinguish "key absent" (first pass — build everything) from "key present
        # but empty" (a tests-only retry — build nothing, only re-run the
        # Test-Writer). A falsiness check would collapse those two into each other.
        stored_implicated = progress.get("implicated")
        if stored_implicated is None:
            implicated = set(_BUILD_LAYERS)
            progress["implicated"] = sorted(implicated)
            save_sprint_progress(output_dir, sprint_name, progress)
        else:
            implicated = set(stored_implicated)

        def _feedback_for(layer):
            relevant = [f for f in findings if f["layer"] in (layer, "all")]
            return _feedback_text(relevant) if relevant else None

        try:
            if "backend" not in progress["completed_steps"]:
                if "backend" in implicated:
                    backend_dev_runner.run(sprint, input_dir, output_dir, feedback=_feedback_for("backend"))
                else:
                    print(dim("  [Backend Dev] not implicated by last attempt's findings — skipped."))
                mark_step_done(output_dir, sprint_name, progress, "backend")

            if "security" not in progress["completed_steps"]:
                if "security" in implicated:
                    security_review_runner.run(sprint, input_dir, output_dir, feedback=_feedback_for("security"))
                else:
                    print(dim("  [Security Review] not implicated by last attempt's findings — skipped."))
                mark_step_done(output_dir, sprint_name, progress, "security")

            if "frontend" not in progress["completed_steps"]:
                if "frontend" in implicated:
                    frontend_dev_runner.run(sprint, input_dir, output_dir, feedback=_feedback_for("frontend"))
                else:
                    print(dim("  [Frontend Dev] not implicated by last attempt's findings — skipped."))
                mark_step_done(output_dir, sprint_name, progress, "frontend")

            if "migration" not in progress["completed_steps"]:
                data_migration_runner.run(sprint, input_dir, output_dir, migrate_data=migrate_data)
                mark_step_done(output_dir, sprint_name, progress, "migration")

            if "test_writer" not in progress["completed_steps"]:
                test_writer_runner.run(sprint, input_dir, output_dir, feedback=_feedback_for("tests"))
                mark_step_done(output_dir, sprint_name, progress, "test_writer")

            if "test_executor" not in progress["completed_steps"]:
                test_result = test_executor_runner.run(sprint, output_dir)
                mark_step_done(output_dir, sprint_name, progress, "test_executor", test_result=test_result)
            else:
                test_result = progress["test_result"]
        except Exception as exc:
            # Deliberately broad: a hard Claude CLI failure (RuntimeError from
            # call_claude), an encoding crash, a None where a string was
            # expected — whatever shape the next unforeseen bug takes, it
            # should not crash the whole multi-sprint batch. Treat it like a
            # failed attempt and let the existing retry loop below decide
            # whether to try again or give up on just this one sprint.
            print(red(f"\n  Sprint '{sprint_name}' attempt {attempt} raised an unhandled error: {exc}"))

            # Environment/tooling failure — the same reasoning as the `blocked`
            # test-result path below: retrying re-raises the identical error with no
            # work done in between, so the fix loop can only burn its budget. Bail out
            # of the entire run rather than the sprint, and deliberately do NOT
            # append_learning() — "claude CLI not found on PATH" is not a code lesson,
            # and writing it would inject that noise into every later agent's cached
            # system prompt via load_learnings_text().
            if _is_infrastructure_error(exc):
                print(red("  This is an environment/tooling failure, not a code defect — "
                           "retrying cannot fix it."))
                update_ledger_entry(output_dir, sprint_name, status="NOT_STARTED", attempts=0,
                                     notes=[f"Run aborted by an environment failure (not a code "
                                            f"defect): {str(exc)[:300]}"])
                clear_sprint_progress(output_dir, sprint_name)
                raise _InfrastructureFailure(str(exc)) from exc

            if attempt - 1 >= max_retries:
                update_ledger_entry(output_dir, sprint_name, status="FAILED_BLOCKED", attempts=attempt - 1)
                append_learning(
                    output_dir, sprint_name,
                    issue="Unhandled agent-call failure",
                    root_cause=str(exc)[:800],
                    fix_applied=f"None successful within {max_retries} attempts",
                    outcome="FAILED_BLOCKED",
                )
                clear_sprint_progress(output_dir, sprint_name)
                print(red(f"\n  Sprint '{sprint_name}' — FAILED_BLOCKED after {max_retries} "
                           f"fix-loop attempts (unhandled errors)."))
                return "FAILED_BLOCKED"
            _seed_next_attempt(output_dir, sprint_name, attempt + 1, [
                {"source": "pipeline", "layer": "all",
                 "detail": f"The previous attempt failed with an unexpected error, not a review "
                           f"finding: {exc}"},
            ])
            continue

        if test_result["status"] == "blocked":
            # Environment/tooling problem, not a code problem — retrying won't help.
            update_ledger_entry(output_dir, sprint_name, status="FAILED_BLOCKED",
                                 notes=[f"Test Executor blocked: {test_result.get('message')}"])
            append_learning(output_dir, sprint_name,
                             issue="Could not execute tests",
                             root_cause=test_result.get("message", "unknown tooling issue"),
                             fix_applied="none — needs environment fix, not a code fix",
                             outcome="FAILED_BLOCKED")
            clear_sprint_progress(output_dir, sprint_name)
            return "FAILED_BLOCKED"

        if "review" not in progress["completed_steps"]:
            review = review_runner.run(sprint, input_dir, output_dir, test_result)
            mark_step_done(output_dir, sprint_name, progress, "review", review=review)
        else:
            review = progress["review"]

        if test_result.get("passed") and review["overall"] == "PASS":
            update_ledger_entry(output_dir, sprint_name, status="PASSED", attempts=attempt - 1)
            clear_sprint_progress(output_dir, sprint_name)
            print(green(f"\n  Sprint '{sprint_name}' — PASSED (attempt {attempt})"))
            return "PASSED"

        # Not passing — build the (layer-tagged) finding set for the next attempt.
        next_findings = list(review.get("consolidated_findings", []))
        if not test_result.get("passed"):
            test_layers = test_result.get("failed_layers") or ["all"]
            detail = _test_failure_detail(test_result)
            for layer in test_layers:
                next_findings.append({"source": "test-executor", "layer": layer, "detail": detail})

        # If this attempt reproduced exactly the findings that were fed INTO it, the
        # correction it was asked to make didn't land. Seeding the next attempt with
        # the same findings would rebuild an identical prompt over identical files —
        # the loop would then burn every remaining retry re-issuing one request that
        # has already been shown not to work. Escalate instead: the "all"-layer notice
        # both widens _implicated_layers to every agent and tells them plainly that
        # the last edit changed nothing.
        if findings and _findings_signature(next_findings) == _findings_signature(findings):
            print(yellow(f"  Attempt {attempt} reproduced attempt {attempt - 1}'s findings "
                          f"exactly — escalating to all layers with a no-progress notice."))
            next_findings = [{"source": "pipeline", "layer": "all",
                              "detail": _STALLED_NOTICE}] + next_findings

        if attempt - 1 >= max_retries:
            update_ledger_entry(output_dir, sprint_name, status="FAILED_BLOCKED", attempts=attempt - 1)
            append_learning(
                output_dir, sprint_name,
                issue="Sprint failed review/tests after retry cap",
                root_cause=_feedback_text(next_findings)[:800],
                fix_applied=f"None successful within {max_retries} attempts",
                outcome="FAILED_BLOCKED",
            )
            clear_sprint_progress(output_dir, sprint_name)
            print(red(f"\n  Sprint '{sprint_name}' — FAILED_BLOCKED after {max_retries} fix-loop attempts."))
            return "FAILED_BLOCKED"

        _seed_next_attempt(output_dir, sprint_name, attempt + 1, next_findings)

    return "FAILED_BLOCKED"  # unreachable, defensive


def main():
    parser = argparse.ArgumentParser(
        prog="run_forward_batch2.py",
        description="Forward Engineering Pipeline — Batch 2 (per-sprint development cycle).",
    )
    parser.add_argument("--input", default="./results")
    parser.add_argument("--output", default="./forward_results")
    parser.add_argument("--migrate-data", action="store_true", default=False,
                        help="Enable Data Migration script generation (still never touches a real DB)")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--only", default=None,
                        help="Run just one sprint by name (for testing a single sprint)")
    parser.add_argument("--skip-environment-check", action="store_true", default=False,
                        help="Skip the preflight check for required build tools (java, node, ...)")
    args = parser.parse_args()

    input_dir = str(Path(args.input).resolve())
    output_dir = Path(args.output).resolve()

    if not args.skip_environment_check:
        env_result = environment_check_runner.run(str(output_dir))
        if env_result["status"] != "ok":
            print(yellow(bold(
                "\nSTOPPED before any sprint work — one or more required build tools are missing.\n"
                "See the Environment Check output above for exactly what to install (or what was "
                "just installed and needs a fresh terminal), then re-run this exact command."
            )))
            sys.exit(3)

    # Safety net for running Batch 2 standalone (without run_forward.py):
    # scaffold_runner.run() is itself skip-checked and now verifies new_app/
    # actually still has files, not just that SCAFFOLD_MANIFEST.md exists —
    # so this is a fast no-op when everything's intact, and only does real
    # work if the project skeleton was deleted/reset since the last run.
    scaffold_result = scaffold_runner.run(input_dir, str(output_dir))
    if scaffold_result["status"] not in ("done",):
        print(red(f"\nSTOPPED — could not confirm/build the project skeleton "
                   f"({scaffold_result.get('reason', scaffold_result['status'])}). "
                   "Run run_forward.py (Batch 1) first, or fix the issue above and re-run."))
        sys.exit(1)

    backlog = _load_sprint_backlog(output_dir)
    if args.only:
        backlog = [s for s in backlog if s["name"] == args.only]
        if not backlog:
            print(red(f"No sprint named {args.only!r} found in SPRINT_BACKLOG.json"))
            sys.exit(1)

    print(f"\n{'=' * 70}")
    print(bold(cyan("FORWARD ENGINEERING PIPELINE — BATCH 2 (PER-SPRINT DEVELOPMENT)")))
    print(f"{'=' * 70}")
    print(f"  Sprints planned : {len(backlog)}")
    print(f"  Max retries     : {args.max_retries}")
    print(f"  Data migration  : {'enabled (script-only)' if args.migrate_data else 'disabled'}")
    print(f"{'=' * 70}\n")

    ledger = load_ledger(str(output_dir))
    t0 = time.monotonic()
    results = {}

    for idx, sprint in enumerate(backlog, start=1):
        name = sprint["name"]
        existing = ledger.get(name, {}).get("status")
        if existing in ("PASSED", "FAILED_BLOCKED"):
            if sprint_output_missing(str(output_dir), name):
                # The ledger remembers a result, but the files it's based on
                # are gone (new_app/ was deleted/reset since that run) — a
                # stale entry, not a reason to skip forever. Reset and rerun.
                print(yellow(f"\n[Sprint {idx}/{len(backlog)}] '{name}' was marked {existing}, but "
                              "its generated files no longer exist (deleted since that run) — "
                              "treating this as stale and running it fresh instead of skipping."))
                update_ledger_entry(str(output_dir), name, status="NOT_STARTED", attempts=0, notes=[])
                clear_sprint_progress(str(output_dir), name)
            else:
                print(dim(f"\n[Sprint {idx}/{len(backlog)}] '{name}' — already {existing}, skipping."))
                results[name] = existing
                continue

        _banner(idx, len(backlog), name)
        try:
            status = _run_one_sprint(sprint, input_dir, str(output_dir), args.migrate_data,
                                      args.max_retries)
        except _InfrastructureFailure as exc:
            print(red(bold(f"\n{'=' * 70}\nRUN ABORTED — environment/tooling failure\n{'=' * 70}")))
            print(red(f"  {exc}"))
            print(yellow(
                "\n  Every remaining sprint would fail this same way, so the run stopped here "
                f"at sprint {idx}/{len(backlog)} instead of marking the whole backlog "
                "FAILED_BLOCKED.\n"
                "  No sprint was recorded as failed — this is not a code defect — so once the "
                "issue above is fixed, just re-run the same command."))
            sys.exit(4)
        results[name] = status

    total = time.monotonic() - t0
    passed = sum(1 for s in results.values() if s == "PASSED")
    blocked = sum(1 for s in results.values() if s == "FAILED_BLOCKED")

    print(f"\n{'=' * 70}")
    print(bold(green("BATCH 2 — RUN COMPLETE")))
    print("=" * 70)
    for name, status in results.items():
        icon = green("PASSED") if status == "PASSED" else red("FAILED_BLOCKED")
        print(f"  {icon:<20} {name}")
    print(f"\n  {passed} passed, {blocked} blocked, out of {len(results)} sprints")
    print(f"  Total time: {int(total // 60)}m {int(total % 60)}s")
    print(f"  Ledger    : {output_dir / 'sprint_ledger.json'}")
    print(f"  Learnings : {output_dir / 'LEARNINGS.md'}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
