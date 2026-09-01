# Knowledge Transfer — Architecture Deep-Dive Session (2026-09-01)

**Purpose of this document:** A different laptop, a different person, or a different AI
session should be able to read this file alone and know exactly what was investigated,
what was verified against the actual code (not just the project's own marketing docs),
what bugs were found, and what is still open — without re-reading the full chat history.

**Type of session:** Read-only research and verification. **No pipeline code was changed
by this session** (except the one restoration described in "Housekeeping" below). No
pipeline steps were re-run. This was pure investigation to build an accurate mental model
of a project whose own documentation, as this session discovered, does not always match
what the code actually does.

---

## 1. What This Repository Actually Contains

Two related but separate systems live in this working folder:

1. **`automated-reverse-engineering-pipeline-main/`** (this repo) — an AI pipeline that
   reads a legacy **Oracle Forms 12c + PL/SQL 19c HRMS** codebase (42 files, under
   `source/ts-plsql-oracle-forms-hrms/`) and produces 25 architecture documents + an
   Enterprise Knowledge Graph, then optionally forward-engineers a
   **Java 17/Spring Boot 3 + React 18/TypeScript + PostgreSQL** replacement application.
2. **`graphify + oracle parser/`** ("OSIRIS", sibling folder, own project, not in this
   git repo) — a standalone, dependency-free, deterministic Python parser
   (`oracle_deep_parser.py`) that extracts the same source into verified structured JSON
   (`business_rules.json` — 812 rules — plus `schema_deep.json`, `plsql_deep.json`,
   `forms_deep.json`, etc.), cross-checked by 3,715 automated audit assertions (100%
   pass). This is the "ground truth" data layer the AI pipeline is meant to build on.

GitHub remote for this repo: `https://github.com/jayaprakash2207/HRMS-Reverse-Engineering-Pipeline---25-DOC-TEST.git`
(remotes `origin` and `github-test` both point here). Branch: `master`.

---

## 2. The 15-Step Reverse-Engineering Pipeline (`run.py`)

Real execution order (not numeric order): **1 → 2 → 0 → 3 → 3.5 → [4–12 in parallel] → 13 → 14 → 15**.

| # | Step | What it does | AI? |
|---|------|--------------|-----|
| 1 | Layer 1 | Deterministic, regex/parser-based extraction | No |
| 2 | Scan Once | Reads every source file in full → `file_cache.json` (single source of truth for every later step) | No |
| 0 | Rule Annotator | 6 parallel threads inject `-- RULE:` comments into `annotated_sources/` — **verified: this output is never actually read by any downstream step** (see Finding F1) | Yes |
| 3 | Scan Agent | Chunked (15 files/chunk) deep extraction with self-correction (missing-file retry, truncation retry) → `DEEP_SCAN_OUTPUT.md` | Yes |
| 3.5 | Implicit Rules | 4 category passes (seed data, Forms constraints, PL/SQL comments, SQL constraints) → `implicit_rules.json` | Yes |
| 4–12 | BA/DA/TA/AA tracks | 4 real OS threads run concurrently, each a two-turn "pick files → analyze" agent pattern | Yes |
| 13 | Cross Validator | Verified directly — see §3 | Yes |
| 14 | Foundation | Verified directly — see §4 | Yes |
| 15 | Gap Hunter | Verified directly — see §5 | Yes |

Steps 4–12 are **genuine parallel threads** — `run.py` starts one `threading.Thread` per
track, each blocking on its own `subprocess.run()` calls to the `claude` CLI, joined
before Step 13 starts.

Resume logic: no central checkpoint file. Each step independently checks whether its own
known output file already exists on disk and skips if so (finer-grained resume exists
inside some steps, e.g. per-chunk in Step 3, per-document in Step 15).

---

## 3. Step 13 — Cross Validator (`pipeline/cross_validator_runner.py`) — verified in full

**Purpose:** After the 4 tracks finish independently, find where they disagree and patch
whichever track is missing something another track already knows.

- Loads all 4 tracks' final outputs (`BA_Deep_Analyst.md`, `DA_Data_Reviewer.md`,
  `TA_Deep_Analyst.md`, `AA_Quality_Review.md`). If fewer than 2 exist, writes an empty
  "skipped" report and stops.
- **One** Claude call (not threaded), all 4 outputs concatenated (25,000 chars each,
  truncated), asks for `gaps` (entity in one track missing from another) and
  `contradictions` (count mismatches) as JSON.
- **Only HIGH/MEDIUM severity gaps get fixed automatically. LOW gaps and ALL
  contradictions are recorded but never resolved automatically** — contradictions are
  handed to humans (`docs/06_REVIEW_Gap_Reports.md`), never auto-fixed.
- For each gap fixed: fetches the named source files (deep-scan → file-cache fallback
  chain), makes a **separate** Claude call to extract the specific missing content, and
  **appends** it to the bottom of the track file that was missing it, under a
  `## [CROSS-VALIDATION SUPPLEMENT]` heading. Never touches the track that already had
  the correct data — always additive to the track that was missing it.
- Writes `cross_validation_report.json`. Resume-safe (skips entirely if that file exists).

---

## 4. Step 14 — Foundation Runner (`pipeline/foundation_runner_multiagent.py`) — read in full, twice, independently, both readings agree

Per `pipeline_config.json`, this is the **currently configured** Step 14 runner (an older
`foundation_runner_template.py` also exists in the codebase and still works — the
multiagent one is meant to be the upgrade).

### 4.1 The three phases as implemented

```
Phase 1 — 2 threads (not 3 — see Finding F2)
  Thread A: Call 1 → docs 01-10 + Knowledge Graph docs (21-25)
  Thread B: polls disk for Thread A's output file, then uses it as context
            → Call 2 → docs 11-20
  (staggered in practice — the two Claude subprocesses barely overlap, see F3)

Pre-loop cleanup — 1 Claude call strips AI leftover text, duplicate sections,
                   technology-neutrality violations, before the loop starts

Phase 2 — self-healing loop, up to 3 rounds:
  1. Reload all 25 docs from disk
  2. ONE Claude call — "Gap Hunter" — reads all 25, outputs a structured gap list,
     each gap tagged with a domain (BUSINESS/DATA/SECURITY/APPLICATION/CROSS)
  3. Stop checks in this order:
       gap_count == 0                    → done
       gap_count >= previous round       → no progress, escalate to
                                            HUMAN_DECISION_REQUIRED.md, stop
       iteration == 3 (max)              → escalate, stop — WITHOUT attempting
                                            a fix this round (see Finding F4)
  4. Otherwise: gaps are routed to domain buckets by a plain Python dict lookup
     on the "Domain:" field the Gap Hunter itself already wrote (no LLM
     "Team Lead" call — see Finding F5)
  5. One Claude call per non-empty domain bucket, each in its own thread — these
     DO run genuinely concurrently (real parallelism, this part is accurate)
  6. Each domain agent outputs full rewritten documents; applied straight to disk

Call 5 — rewrites LOW-confidence sections
Call 6 — independent re-scoring of HIGH-confidence claims
Coverage pass — pure Python evidence-tag counting, no AI

Phase 3 — 1 final Claude call reads all 25 docs, stamps YES/CONDITIONAL/NO-GO per doc
```

### 4.2 Verified findings — code vs. the project's own design docs

The project has a design doc (`MULTI_AGENT_SELF_HEALING_ARCHITECTURE.md`) and a status
report (`FOUNDATION_RUNNER_COMPLETE_REPORT.md`) describing this runner. Both were checked
line-by-line against the actual code (`pipeline/foundation_runner_multiagent.py`, read in
full twice by two independent passes in this session, plus the imported function
signatures in `foundation_runner_template.py`). Confirmed discrepancies:

- **F2 — Only 2 subagents exist, not 3.** The design doc diagrams Subagent A (docs
  01–10), B (docs 11–20), C (docs 21–25/KG). The code only spawns 2 threads — the KG
  docs are folded into Call 1 (Thread A).
- **F3 — "Parallel" Phase 1 is not really parallel.** Thread B explicitly polls
  (`while not part1_raw.exists(): sleep(5)`, up to 600s) for Thread A's output file and
  injects it as context before doing its own real work. Wall-clock time ≈ Call1 + Call2,
  not `max(Call1, Call2)` as the docstring and design doc both claim.
- **F4 — The self-healing loop's 3rd iteration never attempts a fix.** The
  `iteration == max_iterations` stop-check fires *before* domain-fix agents are
  dispatched. With the default `max_iterations=3`, only 2 rounds ever fix anything; the
  3rd is diagnosis-only. Contradicts the design doc's claim that "Iteration 3 catches
  edge cases from iteration 2."
- **F5 — No "Team Lead" agent, no shared task list, no inter-agent communication.**
  `_assign_gaps_to_domains()` is a 5-line Python dict-bucketing function — no LLM call.
  Domain fix-agent threads receive their gap bucket as a fixed function argument up
  front; nothing is "claimed" dynamically. **There is no code anywhere that lets one
  domain thread read or react to another domain thread's in-progress work** — the only
  shared object is a `threading.Lock()` guarding a results dict, written to only after
  each thread finishes. If two domains' fixes touch the same document, whichever result
  lands last in that dict silently overwrites the other — **no merge or conflict
  detection exists**, directly contradicting the design doc's claim that this exact
  failure mode is "prevented."
  → **See §6 below for the full "which diagram pattern" verdict — this was the single
  most-discussed finding of the session.**
- **F6 — `CALL4_PROMPT` (cross-document consistency check) is imported but never called**
  in this runner. It's silently dropped in multiagent mode, not "absorbed into every loop
  iteration" as the docs imply.
- **F7 — Confirmed run-stopping bug, verified against the actual function signatures.**
  Lines 764 and 767 of `foundation_runner_multiagent.py` call:
  ```python
  _run_self_correction_pass(output_dir, layers, foundation_dir, fwd_eng_dir)
  downgrades = _run_second_opinion_pass(output_dir, layers, foundation_dir, fwd_eng_dir)
  ```
  But the real signatures (confirmed by reading `foundation_runner_template.py` lines
  1025–1030 and 1377–1382) are:
  ```python
  def _run_self_correction_pass(foundation_dir: Path, fwd_eng_dir: Path, output_dir: str, layers: dict)
  def _run_second_opinion_pass(foundation_dir: Path, fwd_eng_dir: Path, output_dir: str, layers: dict)
  ```
  Both call sites pass arguments in the wrong order (positional). `foundation_dir`
  receives a plain string (`output_dir`); the function immediately does
  `directory.glob("*.md")` on it → `AttributeError: 'str' object has no attribute
  'glob'`, uncaught, crashing Step 14 right there. **This means Phase 3 (final quality
  gate) never actually executes in the current code — `FINAL_QUALITY_GATE_REPORT.md` is
  never produced on a real run.** This is the highest-priority code fix identified this
  session — a one-line argument-order swap in two call sites.
- **F1 (Step 0, noted above)** — `rule_annotator_runner.py`'s own docstring claims
  downstream steps read from `annotated_sources/`; a full-repo check shows every
  downstream step actually reads `file_cache.json` / `DEEP_SCAN_OUTPUT.md` directly.
  Step 0's Claude-generated annotations currently appear to be discarded output.

---

## 5. Step 15 — Gap Hunter (`pipeline/gap_hunter_runner.py`) — verified in full

**Important distinction:** this is a completely separate, simpler mechanism from the
"Gap Hunter" inside Step 14's Phase 2 — same name, different code, different technique,
runs after Step 14 finishes on the finished 25 documents.

- **Detection is regex, not AI.** A hardcoded pattern list (`\bMISSING\b`, `\bTBD\b`,
  `\bN/A\b`, `unknown`, `placeholder`, `[Not found`, etc.) scans every line of every
  `.md` document (JSON files skipped entirely). Each hit gets an 11-line context window
  built around it; near-duplicates are deduplicated.
- **Classification is AI, but only HIGH severity ever gets touched.** Up to 5 weakness
  contexts per document are sent to Claude to describe what's missing and rate severity;
  LOW-severity findings are simply discarded.
- **Filling is a surgical snippet patch, not a document rewrite.** Source content is
  fetched (deep-scan → cache fallback chain again), Claude is given just the ~10-line
  weak snippet plus source, and its reply must literally contain the marker
  `[GAP-FILLED]` or the fill is discarded. The original snippet is then replaced via a
  **verbatim string `.replace()`** inside the full document; if the exact text no longer
  matches (e.g. it changed since the read), the fill is appended at the document's end
  under an HTML comment instead of being lost.
- **Two real safety checks:** per-gap, if the new document would shrink by more than 10%,
  the write is aborted. Per-round, every document's size is re-verified afterward and any
  shrink is logged as a warning.
- **Real parallelism confirmed:** all 25 documents processed simultaneously via
  `ThreadPoolExecutor(max_workers=10)` — genuine concurrent execution across documents,
  unlike Step 14's threading (which is either staggered or pre-assigned-and-isolated).
- Up to `MAX_ROUNDS = 3`, stops early the moment a round finds zero gaps. Writes
  `gap_hunter_report.json`.

---

## 6. The Core Question of the Session: Subagents vs. Agent Teams Pattern

A diagram was shown contrasting two Claude Code multi-agent patterns:
- **Subagents** — Main Agent spawns independent workers, each does isolated work,
  reports a result back. No peer-to-peer communication between workers.
- **Agent Teams** — Main Agent (Team Lead) spawns a team around a **shared, live task
  list**; teammates communicate with each other and claim tasks from that list while
  working, explicitly to avoid conflicting fixes.

**Verified answer, by reading the actual code twice (once via an independent research
pass, once by reading the full 814-line file directly in this session):
this project uses the Subagents pattern in both Phase 1 and Phase 2 — never the Agent
Teams pattern — despite Phase 2 being explicitly named "Agent Teams" in the module's own
docstring** (`foundation_runner_multiagent.py` lines 12–24, which narrates "Domain agents
claim, fix, communicate via shared gap list" — this narration does not match the code
directly below it).

The defining feature of Agent Teams — a persistent, shared, mutable task list that
workers actively claim from and communicate through mid-task — does not exist anywhere in
this codebase. What exists is a one-time gap list computed once (`_assign_gaps_to_domains`,
plain Python, no LLM), handed out once to fixed threads, with zero communication between
those threads while they run. This is Subagents behavior with different variable names.

---

## 7. Data Quality Findings (from the project's own internal `TEST_REPORT.md`, cross-referenced during this session)

A prior QA pass on a real pipeline output run found **6 of 10 tests passing**. Concrete,
still-open defects in the generated documents:
- AI leftover artifact text ("Looking at the source content...", "Here is the updated
  snippet") embedded directly in 18+ of the 25 generated documents.
- `01_BRD.md` has a triplicated section (`### 2.1 System History` / `### 2.2 Drivers for
  Modernisation` appear 3 times each) from repeated gap-fill injections.
- A confirmed **BR-042 ID collision**: `01_BRD.md` defines BR-042 as an off-cycle payroll
  requirement; every other document (Use Cases, NFR Spec, Readiness Report, Security
  Architecture) defines BR-042 as the critical authentication-bypass defect. These are
  two different things sharing one ID — a human decision is required to renumber one of
  them (documented in `docs/06_REVIEW_Gap_Reports.md`).
- `19_FRONTEND_ARCHITECTURE.md` never names the actual Oracle Forms modules
  (HRMS_EMPLOYEE, HRMS_PAYROLL) it's replacing — only the new SPA route names.

Overall verdict in that report: **"NOT READY for forward engineering"** until the
artifact-text and duplicate-section issues are cleaned and BR-042 is resolved.

---

## 8. Forward Engineering Half — Current Real Status

`forward-engineering-only/` takes the 25 documents and drives code generation:
**Batch 1** (`run_forward.py`) — stack selection → elaboration → conventions → scaffold →
sprint plan. **Batch 2** (`run_forward_batch2.py`) — per sprint: Backend Dev → Security
Review → Frontend Dev → Test Writer → real `mvn test`/`npm test` execution → 3 parallel
independent reviewers → fix loop → learnings write-back.

Target stack already decided: **Java 17, Spring Boot 3.x / React 18 + TypeScript /
PostgreSQL 15 / JWT + AES-256 + RBAC / Flyway migrations**.

**Verified directly against `forward-engineering-only/forward_results/sprint_ledger.json`
on disk: all 6 planned sprints (Security/Identity, Employee Management, Leave Management,
Payroll, Performance, Action Audit Logging) are currently `FAILED_BLOCKED`, 3 attempts
each, last updated 2026-07-29.** This contradicts `.claude/memory/project_pipeline_state.md`,
which claims Phase 2 forward engineering is "NOT STARTED" and that `forward_results/`
"does NOT exist — was deleted 2026-07-27 for clean run." **The memory file is stale —
do not trust it over the actual `sprint_ledger.json` on disk.** A prior run happened after
that memory was written, and it failed on every sprint.

`.claude/memory/project_fixes_applied.md` documents 10 real fixes already applied for
recurring forward-engineering failure modes (portable JDK/Maven resolver, duplicate Jest
configs, `import.meta` Jest incompatibility, missing default export, code-fence artifacts
leaking into source files, `=== END FILE ===` markers leaking into source files, orphan
test folders, missing npm packages, stale `node_modules`, and a Turn-1 file-selection
completeness fix that raised reverse-engineering coverage from ~60–65% to ~85–90%). These
fixes are real prior-session work and should not be reverted if forward engineering is
retried.

---

## 9. Recommended Next Steps (Priority Order)

1. **Fix the Step 14 argument-order bug (Finding F7)** — swap the argument order at the
   two call sites in `foundation_runner_multiagent.py` (lines ~764, ~767) to match the
   real function signatures. Until this is fixed, `foundation_runner_multiagent.py`
   cannot reach Phase 3 on a real run.
2. **Decide whether "Agent Teams" behavior is actually wanted for Phase 2.** If yes, it
   needs to be built — a real shared/mutable gap list plus a conflict-detection or
   merge step when two domain agents' fixes touch the same document. If the current
   Subagents-style behavior is acceptable, the docstring/design docs should be corrected
   to stop claiming otherwise, to avoid misleading future readers (including future AI
   sessions).
3. **Resolve BR-042 and the other items in `docs/06_REVIEW_Gap_Reports.md`** before any
   forward-engineering re-run — these are explicitly documented human-decision blockers.
4. **Strip AI artifact text and the BRD's triplicated section** — flagged as blocking in
   `TEST_REPORT.md`.
5. **Investigate why all 6 forward-engineering sprints are `FAILED_BLOCKED`** before
   retrying — `sprint_ledger.json` has no per-sprint failure notes recorded (`"notes": []`
   for every sprint), so the actual failure reason isn't captured anywhere and will need
   to be re-diagnosed (check `forward_results/LEARNINGS.json` and the per-sprint
   `forward_results/sprints/<slug>/manifest.json` files first).
6. **Wire Step 0's rule-annotator output into the pipeline, or remove the step** —
   currently it costs real Claude-call time and produces output nothing downstream reads
   (Finding F1).

---

## 10. How To Resume From Here

- Read this file first, in full.
- Repository root: `automated-reverse-engineering-pipeline-main/automated-reverse-engineering-pipeline-main/`.
- `TEAM_CONTEXT.md` and `.claude/memory/*.md` in that same folder contain earlier
  session handovers — useful for history, but **cross-check dates and current on-disk
  state before trusting them**, as this session found at least one stale claim (§8 above).
- The most architecturally important files to read directly (not secondhand) before
  making any change: `pipeline/foundation_runner_multiagent.py`,
  `pipeline/foundation_runner_template.py`, `pipeline/base_runner.py`, `run.py`,
  `pipeline_config.json`.
- No pipeline run was executed this session — `results/` on disk reflects whatever the
  last real run produced, not anything from this investigation.

---

## Housekeeping note for this commit

While reviewing pending local changes before this push, one unrelated, already-pending
(uncommitted) edit to
`GENERIC_25_Enterprise_Forward_Engineering_Templates_INDUSTRY_BASED/01_BUSINESS_REQUIREMENTS_DOCUMENT.md`
was found to contain what looked like an accidental paste of conversational chat text
into a section heading (`### 2.5 Organizational/Geographic Boundary` had a stray sentence
appended to it in place of the `[C]` marker). This was reverted to its original text
as part of this commit, on explicit confirmation.

*Session date: 2026-09-01. Investigation only — see §1 for scope.*
