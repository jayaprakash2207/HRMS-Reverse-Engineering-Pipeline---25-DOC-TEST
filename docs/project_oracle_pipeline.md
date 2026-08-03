---
name: project-oracle-pipeline
description: "Oracle HRMS reverse engineering pipeline — full project context, architecture, accuracy improvements, and teammate handoff guide"
metadata: 
  node_type: memory
  type: project
  originSessionId: 2cd486ca-28c9-4492-9199-24f2be735ccf
---

## Project: Oracle HRMS Reverse Engineering Pipeline

**Repo:** https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1.git  
**Local path:** `c:\rev-eng1 test oracle new\automated-reverse-engineering-pipeline-main\automated-reverse-engineering-pipeline-main\`  
**Entry point:** `run.py`

**Why:** Automate full reverse engineering of an Oracle Forms + PL/SQL legacy HRMS codebase (42 source files: 6 .frmxml, 11 .pks/.pkb, triggers, schema) into 25 architecture documents + an Enterprise Knowledge Graph. Target: 98-100% accuracy.

**How to apply:** When continuing this project, assume the pipeline is in a runnable state. Start by reading run.py and the files below for current state.

---

## 14-Step Pipeline

| Step | File | Description |
|------|------|-------------|
| 1 | `pipeline/layer1/` | Deterministic source extraction (no AI) |
| 2 | `pipeline/scan_runner.py` | Cache every file into file_cache.json |
| 3 | `pipeline/scan_agent_runner.py` | Deep scan — chunked Claude extraction |
| 3.5 | `pipeline/implicit_rules_runner.py` | Extract implicit rules from seed/forms/comments |
| 4–5 | `pipeline/runners/ba_agent*.py` | Business Analysis track |
| 6–7 | `pipeline/runners/da_agent*.py` | Data Analysis track |
| 8–10 | `pipeline/runners/ta_agent*.py` | Technology Analysis track |
| 11–12 | `pipeline/runners/aa_agent*.py` | Application Analysis track |
| 13 | `pipeline/cross_validator_runner.py` | Cross-track gap validation |
| 14 | `pipeline/foundation_runner.py` | Foundation KG + 25 docs + verification |

Steps 4–12 run in parallel threads (BA/DA/TA/AA simultaneously).

---

## 5 Accuracy Improvements (built Aug 2026)

1. **Windowed gap detection** — `base_runner.py:detect_and_fill_gaps()` now scans ALL 60k windows of output (was: only first 60k chars). +3% accuracy.

2. **Truncation detection** — `scan_agent_runner.py:_check_file_truncation()` compares extracted char count vs raw source; if < 30% of raw and raw > 500 chars → re-scans alone. +5% accuracy.

3. **Implicit rules** — NEW `pipeline/implicit_rules_runner.py` (Step 3.5). 4 passes: seed data lookups, Oracle Forms constraints, PL/SQL `-- RULE:` comments, SQL CHECK/NOT NULL. Writes `implicit_rules.json`. +2% accuracy.

4. **Cross-track validator** — NEW `pipeline/cross_validator_runner.py` (Step 13). Reads all 4 Agent 2 outputs, finds cross-track gaps, supplements missing agent outputs from source files. Writes `cross_validation_report.json`. +4% accuracy.

5. **Foundation Call 3** — `pipeline/foundation_runner.py` now has a 3rd verification call after Calls 1+2. Reads all 25 generated docs + original 8 agent outputs, finds anything missing, produces targeted document updates. +4% accuracy.

---

## Key Files

- `pipeline/base_runner.py` — call_claude(), supplement_from_cache(), detect_and_fill_gaps(), extract_deep_scan_sections(), save_output(), load_prior_output()
- `pipeline/scan_agent_runner.py` — CHUNK_SIZE=15, MAX_FILE_CHARS=50000, _correct_chunk(), _check_file_truncation()
- `pipeline/foundation_runner.py` — CALL1_PROMPT, CALL2_PROMPT, CALL3_PROMPT, _fill_document_gaps(), _reload_filled_docs(), _split_documents(), _split_documents_updates()
- `run.py` — _TOTAL_STEPS=14, _TRACKS dict, orchestrate(), parallel threading via threading.Thread

---

## Full Fallback Chain

```
source files → file_cache.json → DEEP_SCAN_OUTPUT.md → implicit_rules.json
→ Agent 1 → Agent 2 → gap detection (windowed) → cross_validator → Foundation (3 calls)
```

Each layer falls back to the one below. No data is ever truly lost.

---

## Known Issues / History

- claude-sonnet-5 model ID was invalid — set PIPELINE_CLAUDE_MODEL="" to use CLI default
- BA Agent 2 timeout increased to 3600s; Foundation timeout to 7200s
- UnboundLocalError on `end` variable in scan_agent_runner was fixed
- Chunk 02 only 5/15 files — fixed with _correct_chunk() self-correction

---

## How to Run (for teammates)

```bash
git clone https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1.git
cd oracle-reverse-engg-correction-1
pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code
claude login

# Full pipeline (~2 hours)
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
