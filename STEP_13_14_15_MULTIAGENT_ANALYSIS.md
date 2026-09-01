# Steps 13–15 — Multi-Agent / Parallel / Self-Looping / Self-Healing — Checked Against Each Step

**Date:** 2026-09-01
**Scope:** This document rates Steps 13, 14, and 15 of the reverse-engineering pipeline
(`run.py`) against four specific properties often used loosely to describe this kind of
system: **multi-agent**, **parallel**, **self-looping**, and **self-healing**. All claims
below come from reading the actual runner source files in full
(`pipeline/cross_validator_runner.py`, `pipeline/foundation_runner_multiagent.py`,
`pipeline/gap_hunter_runner.py`), not from the project's own design docs or docstrings,
which — as documented separately in `KT_SESSION_2026-09-01_ARCHITECTURE_DEEP_DIVE.md` —
do not always match what the code does.

---

## Verdict at a Glance

| Step | Multi-agent? | Parallel? | Self-looping? | Self-healing? |
|---|---|---|---|---|
| 13 — Cross Validator | No — 1 agent, 1 call | No | No — runs once | Partial — fixes gaps, never re-checks |
| 14 — Foundation Runner | Yes — several role-specific Claude calls | Yes, in places | **Yes — up to 3 rounds** | **Yes — this is the real one** |
| 15 — Gap Hunter | No — 1 role, run per-document | **Yes — 10 documents at once** | **Yes — up to 3 rounds** | Yes, narrowly (snippet-level only) |

Only **Step 14** genuinely earns the full description "multi-agent, parallel, self-looping,
self-healing system." Step 13 is a single-pass validator. Step 15 is parallel and loops,
but is a narrow text-pattern safety net, not a full semantic reviewer.

---

## Step 13 — Cross Validator (single-shot, not looping)

**File:** `pipeline/cross_validator_runner.py`

**What it does:** After the 4 independent analysis tracks (Business/Data/Technology/
Application) finish, checks whether they agree with each other.

**How:** One Claude call reads all 4 tracks' outputs together and returns a JSON list of
`gaps` (something one track knows that another is missing) and `contradictions`
(conflicting counts/facts). For every HIGH/MEDIUM severity gap, a second Claude call
fetches the missing content from source and **appends** it to the track that was
missing it.

**Why it's not "self-healing multi-agent":** it's one role, one pass, no loop, and no
re-verification of its own fix. Contradictions are never auto-fixed at all — they're
only recorded, for a human to decide (`docs/06_REVIEW_Gap_Reports.md`). This is a single
proofreader doing one comparison pass, not a team.

---

## Step 14 — Foundation Runner (`foundation_runner_multiagent.py`) — the genuine article

This is the step that actually matches the "multi-agent parallel self-looping
self-healing" description — real parallel agent calls, and a real self-healing loop with
proper stop conditions and human escalation.

### Multi-agent, parallel (Phase 1 — generation)

Two Claude calls run in separate threads — one writes documents 01–10 + the Knowledge
Graph, the other writes documents 11–20.

*Caveat, confirmed from the code:* the second thread waits for the first thread's output
file to appear before doing its own real work, so the two calls are staggered in
practice rather than fully simultaneous — but they are still two distinct role-based
agents, not one, and do run as separate threads.

### Self-looping, self-healing (Phase 2 — this is the real loop)

```
ROUND (up to 3 times):
  1 "Gap Hunter" agent reads all 25 finished documents → lists every problem
    (broken cross-references, missing sections, contradictions, leftover AI text)
  → gaps sorted by topic: BUSINESS / DATA / SECURITY / APPLICATION
  → a Claude call per topic runs IN PARALLEL, each rewriting only its own documents
  → all fixes written to disk
  → loop back to step 1 — re-read everything fresh and check again

STOPS when: zero gaps remain, OR the gap count stops shrinking round to round,
            OR 3 rounds have run — whichever comes first.
Anything still broken when it stops is written to HUMAN_DECISION_REQUIRED.md
instead of being silently left wrong.
```

This is real self-healing: it does not just fix once and hope — it re-verifies its own
fix on the next round and keeps going until either everything is clean or it explicitly
admits it cannot fix something further and hands it to a human.

**Accuracy note, confirmed by directly reading the code:** the parallel fix-agents in
this loop do not communicate with each other while working — each receives its own list
of assigned gaps and works in isolation, then reports back. If two of them happen to edit
the same document in the same round, whichever one finishes last simply overwrites the
other, with no merge. So it is genuinely parallel and genuinely self-healing round to
round, but the agents are not coordinating live within a single round (this is discussed
in full, with a direct comparison to the "Subagents vs. Agent Teams" pattern, in
`KT_SESSION_2026-09-01_ARCHITECTURE_DEEP_DIVE.md` §6).

After the loop: two more single Claude calls polish confidence scores (self-correction of
LOW sections, independent re-scoring of HIGH claims), then one final call stamps a
YES/CONDITIONAL/NO-GO verdict on each of the 25 documents.

---

## Step 15 — Gap Hunter (separate mechanism from Step 14's internal one — same name, different job)

**File:** `pipeline/gap_hunter_runner.py`

**Multi-agent?** Not really — it is one role (find-and-patch-weak-text) applied
repeatedly across documents, not several different specialist agents the way Step 14 has.

**Parallel — yes, and this is the most concurrent step in the whole pipeline:**
All 25 documents are scanned and patched **at the same time**, using a real thread pool
of 10 workers (`ThreadPoolExecutor(max_workers=10)`) — genuinely more parallel in
practice than Step 14, where the "parallel" threads are either staggered (Phase 1) or
working through a coordinator (Phase 2).

**Self-looping, self-healing — yes, but narrower in scope:**

```
ROUND (up to 3 times):
  Scan every document for weak-text patterns (MISSING, TBD, N/A, "unknown", etc.)
  — this detection step is plain text-pattern matching, not AI
  For each weak spot found, ask Claude: is this a real gap, and how severe?
  Only HIGH-severity gaps get fixed; LOW ones are simply dropped
  Fetch the real source data, patch just that ~10-line snippet, verify the reply
  actually contains the [GAP-FILLED] marker before accepting it
  Re-scan next round — stop early the moment a round finds zero weak spots
```

Two safety nets are built in that Step 14 does not have: if a fix would shrink a
document by more than 10%, it is aborted; and every document's size is re-checked after
every round to catch accidental damage.

**Why it is narrower than Step 14's healing:** it can only fix a document that literally
contains the word "MISSING" or "TBD" or similar — it has no concept of "this BR-042
reference doesn't match the BRD" the way Step 14's internal Gap Hunter does. It is a
safety net for leftover placeholder text, not a structural-consistency checker.

---

## One-Paragraph Summary

Step 13 is a single validator, not multi-agent or self-healing. **Step 14 is the step
that genuinely earns the "multi-agent, parallel, self-looping, self-healing" description**
— real parallel agent calls, a real self-healing loop with proper stop conditions and
human escalation — though the agents within a round work in isolation rather than truly
coordinating with each other. Step 15 is the most parallel of the three (10 documents
processed simultaneously) and does loop and heal, but only against a narrow class of
leftover-placeholder-text problems, using cheap regex detection rather than a full
semantic review.

---

*See also: `KT_SESSION_2026-09-01_ARCHITECTURE_DEEP_DIVE.md` for the full session
knowledge-transfer document, including verified bug findings (F1–F7) in
`foundation_runner_multiagent.py` and the "Subagents vs. Agent Teams" pattern analysis
referenced above.*
