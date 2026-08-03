---
name: project-oracle-pipeline
description: Oracle HRMS reverse engineering pipeline — full project context, 15-step pipeline, 8 accuracy improvements, architecture, teammate handoff guide, known issues
metadata:
  type: project
---

## Project: Oracle HRMS Reverse Engineering Pipeline

**Repo:** https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1.git
**Entry point:** `run.py`

**Why:** Automate full reverse engineering of an Oracle Forms + PL/SQL legacy HRMS codebase (42 source files: 6 .xml Oracle Forms, 22 .pkb/.pks packages, triggers, schema, seed data) into 25 architecture documents + an Enterprise Knowledge Graph. Target: 98-100% accuracy.

---

## 15-Step Pipeline

| Step | File | Description |
|------|------|-------------|
| 0 | `pipeline/rule_annotator_runner.py` | Auto-inject -- RULE: comments into PL/SQL source copies |
| 1 | `pipeline/layer1/` | Deterministic source extraction (no AI) |
| 2 | `pipeline/scan_runner.py` | Cache every file into file_cache.json (42 files, validated) |
| 3 | `pipeline/scan_agent_runner.py` | Deep scan — chunked + self-correction + truncation detection |
| 3.5 | `pipeline/implicit_rules_runner.py` | Extract implicit rules from seed/forms/comments/schema |
| 4–5 | `pipeline/runners/ba_agent*.py` | Business Analysis (Agent1 + Agent2 + edge-case pass) |
| 6–7 | `pipeline/runners/da_agent*.py` | Data Analysis (Agent1 + Agent2 + edge-case pass) |
| 8–10 | `pipeline/runners/ta_agent*.py` | Technology Analysis (Agent1 + Batch1 + Batch2+edge) |
| 11–12 | `pipeline/runners/aa_agent*.py` | Application Analysis (Agent1 + Agent2 + edge-case pass) |
| 13 | `pipeline/cross_validator_runner.py` | Cross-track gap validation and fill |
| 14 | `pipeline/foundation_runner.py` | Foundation KG + 25 docs (3 calls + verification) |
| 15 | `pipeline/gap_hunter_runner.py` | Self-healing gap loop (3 rounds, fills MISSING/TBD markers) |

Steps 4–12 run in parallel threads (BA/DA/TA/AA simultaneously).

---

## 8 Accuracy Improvements (all built, all pushed to GitHub)

1. **Rule Annotator** — Step 0. Auto-injects -- RULE: / -- CONSTRAINT: / -- BUSINESS: comments from code logic (IF conditions, RAISE errors, thresholds). +5%
2. **Windowed gap detection** — base_runner.py scans ALL 60k windows (was: only first 60k chars). +3%
3. **Truncation detection** — scan_agent_runner.py re-scans files extracted < 30% of raw source. +5%
4. **Implicit rules** — Step 3.5. Seed data, Forms constraints, PL/SQL comments, SQL constraints → implicit_rules.json. +2%
5. **Edge-case pass** — All 4 Agent 2 runners run second Claude call focused on edge cases, merge both passes. +2%
6. **Cross-track validator** — Step 13. Finds and fills inter-track gaps. → cross_validation_report.json. +4%
7. **Foundation Call 3** — Verification: all 25 docs cross-checked vs 8 agent outputs. +4%
8. **Gap Hunter** — Step 15. Self-healing loop: fills MISSING/N/A/TBD markers, up to 3 rounds. → gap_hunter_report.json. +3%

**Total: ~80% baseline → ~98-100% target**

---

## Key Files

- `pipeline/base_runner.py` — call_claude(), supplement_from_cache(), detect_and_fill_gaps(), save_json()
- `pipeline/scan_agent_runner.py` — CHUNK_SIZE=15, _correct_chunk(), _check_file_truncation()
- `pipeline/foundation_runner.py` — CALL1/2/3_PROMPT, _fill_document_gaps(), _reload_filled_docs(), _split_documents_updates()
- `run.py` — _TOTAL_STEPS=15, _TRACKS, orchestrate(), parallel threading

---

## Tracks (--track flag)

```
setup        steps 1–3    Layer 1 + Scan Once + Scan Agent + Implicit Rules
business     steps 4–5    BA (+ edge-case pass)
data         steps 6–7    DA (+ edge-case pass)
technology   steps 8–10   TA (+ edge-case pass)
application  steps 11–12  AA (+ edge-case pass)
validate     step  13     Cross-track validator
foundation   steps 14–15  Foundation + Gap Hunter
```

Note: Step 0 (Rule Annotator) runs with --track setup.

---

## Known Issues Fixed

- scan_runner.py validation falsely crashed Step 2 — fixed (path comparison bug)
- All 6 Oracle Forms .xml files confirmed detected via content sniffing
- PIPELINE_CLAUDE_MODEL must be empty or unset — specific model names cause API errors
- BA Agent 2 timeout: 3600s. Foundation: 7200s. TA Agent 2 Batch 2: 14400s.

---

## Full Fallback Chain

```
source files → file_cache.json → annotated_sources/ → DEEP_SCAN_OUTPUT.md
→ implicit_rules.json → Agent 1 → Agent 2 (+ edge pass) → gap detection (windowed)
→ cross_validator → Foundation (3 calls) → gap_hunter (3 rounds)
```

---

## How to Run

```bash
git clone https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1.git
cd oracle-reverse-engg-correction-1
pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code
claude login

# Full pipeline (~2.5 hours)
python run.py --source "path/to/oracle-hrms-source" --output ./results

# Or track by track (recommended)
python run.py --source <path> --output ./results --track setup
python run.py --source <path> --output ./results --track business
python run.py --source <path> --output ./results --track data
python run.py --source <path> --output ./results --track technology
python run.py --source <path> --output ./results --track application
python run.py --source <path> --output ./results --track validate
python run.py --source <path> --output ./results --track foundation

# Resume interrupted run — just re-run same command
```

Every step is checkpointed. If interrupted, re-run the same command.
