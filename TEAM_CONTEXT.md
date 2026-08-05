# Team Context — Oracle HRMS Reverse Engineering Pipeline
# HANDOVER GUIDE — Read this before touching anything

Last updated: 2026-08-05
Status: **PARTIALLY COMPLETE — teammate needs to finish Step 14 docs + Step 15**

---

## What This Project Does

Fully automated reverse engineering of an Oracle Forms + PL/SQL legacy HRMS codebase.
It reads 42 source files and produces 25 architecture documents + an Enterprise Knowledge Graph
using Claude AI — zero manual work.

**Run command:**
```bash
cd automated-reverse-engineering-pipeline-main
python run.py --source "./source" --output ./results
```

---

## CURRENT STATE — What Is Done vs What Is Pending

### ✅ FULLY COMPLETE (Steps 1–13)

| Step | Output | Status |
|------|--------|--------|
| Step 1 — Source Extraction | results/Source_Extraction/ | ✅ Done |
| Step 2 — File Cache | results/file_cache.json (366KB, 42 files) | ✅ Done |
| Step 0 — Rule Annotator | results/annotated_sources/ (29 files annotated) | ✅ Done |
| Step 3 — Deep Scan | results/DEEP_SCAN_OUTPUT.md | ✅ Done |
| Step 3.5 — Implicit Rules | results/implicit_rules.json (310 rules) | ✅ Done |
| Steps 4–5 — BA Track | results/Business_Analysis/ | ✅ Done |
| Steps 6–7 — DA Track | results/Data_Analysis/ | ✅ Done |
| Steps 8–10 — TA Track | results/Technology_Analysis/ | ✅ Done |
| Steps 11–12 — AA Track | results/Application_Analysis/ | ✅ Done |
| Step 13 — Cross Validator | results/cross_validation_report.json | ✅ Done |

### ⚠️ PARTIALLY COMPLETE (Step 14)

Step 14 ran but Claude ran out of context mid-way. Only 12 of 25 documents were generated.

**Generated (keep these):**
```
results/ForwardEngineering_Docs/
  01_BRD.md                          ← partial content, needs expansion
  01_BRD_SUPPLEMENT.md               ← verified supplement
  04_BUSINESS_PROCESS_MODEL.md
  05_DOMAIN_MODEL.md
  06_DATA_DICTIONARY.md              ← good, 486 lines
  09_DATA_FLOW_DIAGRAM.md            ← thin, needs expansion
  10_SERVICE_CATALOG.md              ← good, 369 lines
  13_SECURITY_ARCHITECTURE.md        ← good, 190 lines
  17_FORWARD_ENGINEERING_READINESS_REPORT.md
  18_DEPLOYMENT_ARCHITECTURE.md
  19_FRONTEND_ARCHITECTURE.md
  20_UI_UX_SPECIFICATION.md

results/Foundation_KnowledgeGraph/
  ENTERPRISE_KNOWLEDGE_GRAPH.json    ← generated
```

**MISSING (need to generate these 13 docs):**
```
ForwardEngineering_Docs/
  02_BUSINESS_CAPABILITY_MODEL.md
  03_USE_CASE_SPECIFICATION.md
  07_DATA_MODEL_SPECIFICATION.md
  08_ERD.md
  11_API_CONTRACT_SPECIFICATION.md
  12_TECHNOLOGY_BLUEPRINT.md
  14_NFR_SPECIFICATION.md
  15_FORWARD_ENGINEERING_SPECIFICATION.md
  16_GENERATION_MANIFEST.json

Foundation_KnowledgeGraph/
  CANONICAL_ENTERPRISE_MODEL.md
  ARCHITECTURE_INVENTORY.md
  TRACEABILITY_MATRIX.md
  FORWARD_ENGINEERING_INPUT_MAP.md
```

### ❌ NOT RUN (Step 15)

Step 15 (Gap Hunter) has not been run. Run it after Step 14 is complete.

---

## HOW TO PICK UP AND FINISH

### Option A — Re-run full pipeline (simplest, ~2 hours)
Steps 1–13 will all skip instantly (already done). Only Steps 14–15 will run.

```bash
python run.py --source "./source" --output ./results
```

**BUT FIRST — delete the stale Step 14 raw outputs so it regenerates cleanly:**
```bash
del results\Foundation_Raw_Output_Part1.md
del results\Foundation_Raw_Output_Part2.md
del results\Foundation_Raw_Output_Part3.md
rmdir /s /q results\ForwardEngineering_Docs
rmdir /s /q results\Foundation_KnowledgeGraph
python run.py --source "./source" --output ./results
```

### Option B — Generate only missing docs (~40 min)
Use the script already created for this:

```bash
python generate_missing_docs.py
```

This script reads all existing analysis results and calls Claude only for the
13 missing documents. No full re-run needed. **The prompts are fixed to force
Claude to output raw Markdown directly (not describe what it wrote).**

Then run Step 15 manually:
```bash
python pipeline/gap_hunter_runner.py --output ./results
```

---

## KEY FILES TO KNOW

| File | What it does |
|------|-------------|
| `run.py` | Master orchestrator — runs all 15 steps |
| `pipeline/base_runner.py` | call_claude() function — all AI calls go through here |
| `pipeline/rule_annotator_runner.py` | Step 0 — parallelized (6 threads), annotates PL/SQL files |
| `pipeline/foundation_runner.py` | Step 14 — generates 25 docs (3 Claude calls) |
| `pipeline/gap_hunter_runner.py` | Step 15 — self-healing loop |
| `generate_missing_docs.py` | Utility — generates missing Step 14 docs individually |
| `reextract_foundation_docs.py` | Utility — re-parses raw foundation outputs to extract docs |
| `results/file_cache.json` | All 42 source files cached — pipeline reads from here, not source/ |
| `results/cross_validation_report.json` | 18 gaps + 7 contradictions found across tracks |

---

## IMPORTANT KNOWN ISSUES

### 1. Step 14 context overflow
Step 14 sends huge context (all 8 analysis outputs) to Claude in 3 calls.
Claude sometimes runs out of context and produces partial output with no doc markers.
**Fix:** Run `generate_missing_docs.py` which generates each doc individually.

### 2. Claude describes instead of writing
Sometimes Claude responds with "Here is the document I wrote..." instead of
outputting the actual document. `generate_missing_docs.py` has auto-retry logic for this.
If it happens again, the fix is adding this to the start of the prompt:
```
Output ONLY the raw Markdown. Start with # title on line 1. No preamble.
```

### 3. Step 0 timeout
Step 0 (Rule Annotator) was increased to 7200s timeout in run.py.
It uses 6 parallel threads and takes ~25 min. Do not reduce the timeout.

### 4. Resume safety
Every step checks if output exists before running. To force a step to re-run,
delete its output file/folder first.

---

## RESULTS SUMMARY (what was found)

- **42 source files** analysed (22 PL/SQL packages, 6 Oracle Forms, 11 SQL schema, triggers, seed data)
- **140 business rules** extracted (BA track)
- **310 implicit rules** extracted (Step 3.5)
- **30 database tables** mapped (DA track)
- **18 gaps** found between analysis tracks (13 auto-resolved)
- **7 contradictions** found between tracks (e.g. hire date: 90 days in form vs 180 days in trigger)
- **33 quality findings** + 25 architecture violations + 14 risks (AA track)

### Critical findings for the new system:
1. `HEAD_OF_HOUSEHOLD` employees pay $0 federal tax (critical bug in PKG_PAYROLL)
2. `EMPLOYEE_HISTORY` column mismatch — trigger references columns that don't exist in DDL (ORA-00904)
3. `rehire_employee` procedure is completely broken — trigger blocks it
4. AES-256 encryption key is hardcoded in PKG_SECURITY (security risk)
5. Race condition in `generate_emp_number` — no SELECT FOR UPDATE

---

## PIPELINE ARCHITECTURE

```
source/ (42 files)
    │
    ▼
Step 1 → Step 2 (file_cache.json) → Step 0 (annotate) → Step 3 (deep scan) → Step 3.5 (implicit rules)
    │
    ├── BA Track (Steps 4–5)  ─┐
    ├── DA Track (Steps 6–7)   ├── run in parallel threads
    ├── TA Track (Steps 8–10)  │
    └── AA Track (Steps 11–12) ┘
    │
    ▼
Step 13 (Cross Validator — finds gaps/contradictions between tracks)
    │
    ▼
Step 14 (Foundation — 25 documents + Knowledge Graph)
    │
    ▼
Step 15 (Gap Hunter — self-healing loop)
    │
    ▼
results/ (50+ output files)
```

---

## CONTACTS

- Repo owner: Jaya Prakash
- Repo: https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1
- Word document (full pipeline explanation): ORACLE_HRMS_PIPELINE_EXPLAINED.docx
