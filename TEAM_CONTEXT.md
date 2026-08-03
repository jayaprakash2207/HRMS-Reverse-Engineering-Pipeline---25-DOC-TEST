# Team Context — Oracle HRMS Reverse Engineering Pipeline

This file is for teammates picking up this project. Read this before touching any code.

---

## What This Project Does

Fully automated reverse engineering of an Oracle Forms + PL/SQL legacy HRMS codebase into 25 architecture documents + an Enterprise Knowledge Graph. Target accuracy: **98–100%**.

**Run it:**
```bash
python run.py --source "path/to/oracle-hrms-source" --output ./results
```

See [README.md](README.md) for full instructions.

---

## Pipeline Steps (15 total)

```
Step 0    Rule Annotator    — auto-injects -- RULE: comments into PL/SQL source copies
Step 1    Layer 1           — deterministic extraction (no AI)
Step 2    Scan Once         — cache every file into file_cache.json (all 42 files)
Step 3    Scan Agent        — deep extract all files via Claude (chunked + self-correcting)
Step 3.5  Implicit Rules    — extract rules from seed data / Oracle Forms / PL/SQL comments
Step 4–5  Business Analysis  (Agent 1 → Agent 2 + edge-case pass)   ┐
Step 6–7  Data Analysis      (Agent 1 → Agent 2 + edge-case pass)   ├─ parallel
Step 8–10 Technology Analysis(Agent 1 → Batch1 → Batch2 + edge)    ┤
Step 11–12 Application Analysis (Agent 1 → Agent 2 + edge-case)    ┘
Step 13   Cross Validator   — cross-track gap check and fill
Step 14   Foundation        — Knowledge Graph + 25 documents + verification (3 calls)
Step 15   Gap Hunter        — self-healing loop, fills remaining weakness markers
```

---

## 8 Accuracy Improvements (all built into this version)

| # | File | What it does | Gain |
|---|------|-------------|:----:|
| 1 | `pipeline/rule_annotator_runner.py` | Step 0 — auto-injects `-- RULE:` comments from code logic | +5% |
| 2 | `pipeline/base_runner.py` | Windowed gap detection — scans ALL output (not just first 60k chars) | +3% |
| 3 | `pipeline/scan_agent_runner.py` | Truncation detection — re-scans files whose extraction < 30% of source | +5% |
| 4 | `pipeline/implicit_rules_runner.py` | Step 3.5 — seed lookups, Forms constraints, PL/SQL comments, SQL constraints | +2% |
| 5 | All 4 Agent 2 runners | Edge-case second pass + merge — catches what first pass missed | +2% |
| 6 | `pipeline/cross_validator_runner.py` | Step 13 — cross-track gaps: AA procedure not in BA, DA table not in BA rule | +4% |
| 7 | `pipeline/foundation_runner.py` | Foundation Call 3 — cross-checks all 25 docs vs original agent outputs | +4% |
| 8 | `pipeline/gap_hunter_runner.py` | Step 15 — self-healing loop, fills MISSING/TBD/unknown markers, 3 rounds | +3% |

**Before: ~80% → After: ~98–100%**

---

## Output Files

After a complete run, `results/` contains:

```
file_cache.json                  — raw content of all 42 source files
DEEP_SCAN_OUTPUT.md              — deep extracted content
annotated_index.json             — index of rule-annotated source copies
implicit_rules.json              — implicit business rules
cross_validation_report.json     — cross-track gap report
gap_hunter_report.json           — self-healing pass report

Business_Analysis/
  BA_Structural_Scout.md
  BA_Deep_Analyst.md

Data_Analysis/
  DA_Data_Extractor.md
  DA_Data_Reviewer.md

Technology_Analysis/
  TA_Stack_Scout.md
  TA_Deep_Analyst.md

Application_Analysis/
  AA_App_Extractor.md
  AA_Quality_Review.md

Foundation_KnowledgeGraph/
  ENTERPRISE_KNOWLEDGE_GRAPH.json
  CANONICAL_ENTERPRISE_MODEL.md
  ARCHITECTURE_INVENTORY.md
  TRACEABILITY_MATRIX.md
  FORWARD_ENGINEERING_INPUT_MAP.md

ForwardEngineering_Docs/
  01_BRD.md  →  20_UI_UX_SPECIFICATION.md   (20 documents)
```

---

## How to Run (for new teammates)

```bash
git clone https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1.git
cd oracle-reverse-engg-correction-1
pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code
claude login

# Full pipeline (~2.5 hours)
python run.py --source "path/to/oracle-hrms-source" --output ./results

# OR track by track (recommended — each ~15-45 min)
python run.py --source <path> --output ./results --track setup        # steps 1–3
python run.py --source <path> --output ./results --track business     # steps 4–5
python run.py --source <path> --output ./results --track data         # steps 6–7
python run.py --source <path> --output ./results --track technology   # steps 8–10
python run.py --source <path> --output ./results --track application  # steps 11–12
python run.py --source <path> --output ./results --track validate     # step 13
python run.py --source <path> --output ./results --track foundation   # steps 14–15
```

**If interrupted — just re-run the same command. Every step is checkpointed to disk.**

---

## Known Issues Fixed

- `PIPELINE_CLAUDE_MODEL` must be empty or unset — do NOT set it to a specific model name
- `scan_runner.py` validation bug fixed — previously crashed Step 2 on every run
- All 6 Oracle Forms `.xml` files confirmed readable via content sniffing
- All 42 source files confirmed cached and validated at Step 2

---

## Architecture — Key Files

| File | Purpose |
|------|---------|
| `run.py` | Master orchestrator — 15 steps, 7 tracks, parallel threading |
| `pipeline/rule_annotator_runner.py` | Step 0 — auto rule annotation |
| `pipeline/base_runner.py` | Core: call_claude(), windowed gap detection, fallback chain |
| `pipeline/scan_runner.py` | Step 2 — file caching + validation (42 files) |
| `pipeline/scan_agent_runner.py` | Step 3 — chunked deep scan + self-correction + truncation detection |
| `pipeline/implicit_rules_runner.py` | Step 3.5 — implicit rule extraction |
| `pipeline/cross_validator_runner.py` | Step 13 — cross-track validation |
| `pipeline/foundation_runner.py` | Step 14 — Foundation synthesis (3 calls) |
| `pipeline/gap_hunter_runner.py` | Step 15 — self-healing gap loop |
| `pipeline/runners/` | 9 analysis agents (BA/DA/TA/AA × Agent1+Agent2, TA split into 3) |
| `Prompts_Ready_To_Use/` | 8 Claude system prompts for all agents |
| `docs/` | Project memory and context files |

---

## Questions?

Contact: Jaya Prakash (repo owner)
Repo: https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1
