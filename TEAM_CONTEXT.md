# Team Context — Oracle HRMS Reverse Engineering Pipeline

This file is for teammates picking up this project. Read this before touching any code.

---

## What This Project Does

Fully automated reverse engineering of an Oracle Forms + PL/SQL legacy HRMS codebase into 25 architecture documents + an Enterprise Knowledge Graph. Target accuracy: **98–100%**.

**Run it:** `python run.py --source "path/to/oracle-hrms-source" --output ./results`

See [README.md](README.md) for full instructions.

---

## Pipeline Steps (14 total)

```
Step 1    Layer 1 extraction (deterministic, no AI)
Step 2    Scan Once — cache every file into file_cache.json
Step 3    Scan Agent — deep extract all files via Claude (chunked)
Step 3.5  Implicit Rules — extract rules from seed data / Oracle Forms / PL/SQL comments
Step 4–5  Business Analysis (Agent 1 → Agent 2)      ┐
Step 6–7  Data Analysis (Agent 1 → Agent 2)           ├─ run in parallel
Step 8–10 Technology Analysis (Agent 1 → Batch1+2)   ┤
Step 11–12 Application Analysis (Agent 1 → Agent 2)  ┘
Step 13   Cross Validator — cross-track gap check + fill
Step 14   Foundation — Knowledge Graph + 25 documents + verification pass
```

---

## 5 Accuracy Improvements (built into this version)

| # | File | What it does |
|---|------|-------------|
| 1 | `pipeline/base_runner.py` | Windowed gap detection — scans ALL output (not just first 60k chars) |
| 2 | `pipeline/scan_agent_runner.py` | Truncation detection — re-scans files whose extraction was < 30% of source |
| 3 | `pipeline/implicit_rules_runner.py` | NEW Step 3.5 — seed lookups, Forms constraints, PL/SQL comments, SQL constraints |
| 4 | `pipeline/cross_validator_runner.py` | NEW Step 13 — cross-track gaps: AA procedure not in BA, DA table not in BA rule |
| 5 | `pipeline/foundation_runner.py` | Call 3 verification — cross-checks all 25 docs vs original agent outputs |

---

## Output Files

After a complete run, `results/` contains:

- `file_cache.json` — raw content of every source file
- `DEEP_SCAN_OUTPUT.md` — deep extracted content
- `implicit_rules.json` — implicit business rules (NEW)
- `cross_validation_report.json` — cross-track gap report (NEW)
- `Business_Analysis/` — BA_Structural_Scout.md, BA_Deep_Analyst.md
- `Data_Analysis/` — DA_Data_Extractor.md, DA_Data_Reviewer.md
- `Technology_Analysis/` — TA_Stack_Scout.md, TA_Deep_Analyst.md
- `Application_Analysis/` — AA_App_Extractor.md, AA_Quality_Review.md
- `Foundation_KnowledgeGraph/` — ENTERPRISE_KNOWLEDGE_GRAPH.json + 4 foundation docs
- `ForwardEngineering_Docs/` — 01_BRD.md through 20_UI_UX_SPECIFICATION.md

---

## Resume After Interruption

Every step checkpoints to disk. Re-run the exact same command and it continues from where it stopped.

---

## Known Issues Fixed

- `PIPELINE_CLAUDE_MODEL` must be empty (or unset) to use the CLI default model — do NOT set it to a specific Claude model unless you know the exact valid ID
- BA Agent 2 timeout: 3600s. Foundation timeout: 7200s. TA Agent 2 Batch 2: 14400s.
- If a chunk has fewer files than expected → `_correct_chunk()` auto-fixes it (up to 3 attempts)

---

## Architecture — Key Files

| File | Purpose |
|------|---------|
| `run.py` | Master orchestrator — 14 steps, parallel threading |
| `pipeline/base_runner.py` | Core helpers: call_claude(), fallback chain, gap detection |
| `pipeline/scan_agent_runner.py` | Chunked deep scan with self-correction + truncation detection |
| `pipeline/implicit_rules_runner.py` | NEW: implicit business rule extraction |
| `pipeline/cross_validator_runner.py` | NEW: cross-track validation and gap filling |
| `pipeline/foundation_runner.py` | Foundation synthesis: 3 Claude calls, 25 documents |
| `pipeline/runners/` | 8 analysis agents (BA/DA/TA/AA × Agent1+Agent2) |
| `Prompts_Ready_To_Use/` | Claude system prompts for all 8 agents |

---

## Questions?

Contact: Jaya Prakash (repo owner)  
Repo: https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1
