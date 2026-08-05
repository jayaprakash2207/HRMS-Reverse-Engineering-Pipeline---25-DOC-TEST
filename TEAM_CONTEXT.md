# Team Context — Oracle HRMS Reverse Engineering Pipeline
# HANDOVER GUIDE — Read this before touching anything

Last updated: 2026-08-05
Status: **STEPS 1–14 COMPLETE ✅ — Step 15 pending fix + run**

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

### ✅ FULLY COMPLETE (Steps 1–14)

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
| Step 14 — Foundation Docs | results/ForwardEngineering_Docs/ (21 files) + results/Foundation_KnowledgeGraph/ (5 files) | ✅ Done |

### ✅ ALL 25 FOUNDATION DOCUMENTS GENERATED

**ForwardEngineering_Docs/ (21 files):**
```
01_BRD.md                                    436 lines   59 KB
01_BRD_SUPPLEMENT.md                         140 lines   26 KB
02_BUSINESS_CAPABILITY_MODEL.md              629 lines   55 KB
03_USE_CASE_SPECIFICATION.md               1,094 lines   64 KB
04_BUSINESS_PROCESS_MODEL.md                 223 lines   10 KB
05_DOMAIN_MODEL.md                           317 lines   27 KB
06_DATA_DICTIONARY.md                        406 lines   33 KB
07_DATA_MODEL_SPECIFICATION.md             1,130 lines   68 KB
08_ERD.md                                  1,218 lines   57 KB
09_DATA_FLOW_DIAGRAM.md                    1,062 lines   58 KB
10_SERVICE_CATALOG.md                        369 lines   27 KB
11_API_CONTRACT_SPECIFICATION.md           1,963 lines   60 KB
12_TECHNOLOGY_BLUEPRINT.md                   722 lines   48 KB
13_SECURITY_ARCHITECTURE.md                  190 lines   21 KB
14_NFR_SPECIFICATION.md                      645 lines   50 KB
15_FORWARD_ENGINEERING_SPECIFICATION.md      983 lines   55 KB
16_GENERATION_MANIFEST.json                  798 lines   48 KB
17_FORWARD_ENGINEERING_READINESS_REPORT.md   564 lines   62 KB
18_DEPLOYMENT_ARCHITECTURE.md               297 lines   10 KB
19_FRONTEND_ARCHITECTURE.md                  261 lines   11 KB
20_UI_UX_SPECIFICATION.md                    534 lines   29 KB
```

**Foundation_KnowledgeGraph/ (5 files):**
```
ENTERPRISE_KNOWLEDGE_GRAPH.json              210 lines   22 KB
ARCHITECTURE_INVENTORY.md                    539 lines   49 KB
CANONICAL_ENTERPRISE_MODEL.md                421 lines   47 KB
FORWARD_ENGINEERING_INPUT_MAP.md             395 lines   56 KB
TRACEABILITY_MATRIX.md                       543 lines   65 KB
```

### ✅ HUMAN REVIEW FILES (docs/ folder — 7 files)

Pre-populated with real findings from this pipeline run. Teammates review and sign off
before code generation begins.

```
docs/HUMAN_REVIEW_GUIDE.md                  — Overview + 5 critical blockers
docs/01_REVIEW_Business_Analysis.md         — Business rules, BRD, use cases
docs/02_REVIEW_Data_Analysis.md             — Tables, columns, PII inventory
docs/03_REVIEW_Technology_Analysis.md       — Tech stack, architecture violations
docs/04_REVIEW_Application_Analysis.md      — 5 critical bugs to fix
docs/05_REVIEW_Foundation_Documents.md      — All 25 docs checklist
docs/06_REVIEW_Gap_Reports.md               — 7 contradictions (MUST resolve before codegen)
```

### ⚠️ PENDING (Step 15)

Step 15 (Gap Hunter) has a bug — it overwrites entire files instead of patching only the
gap section. **Do NOT run `python pipeline/gap_hunter_runner.py` without fixing this bug first.**

**The bug:** In `pipeline/gap_hunter_runner.py`, the file write after gap-filling replaces
the whole document with just the patched section. Fix: do a targeted section replacement,
not a full file overwrite.

**After fixing the bug:**
```bash
python pipeline/gap_hunter_runner.py --output ./results
```
This runs up to 3 rounds, patching any TBD/MISSING/unknown markers in all 25 docs.

---

## HOW TO PICK UP AND FINISH

### Option A — Fix Step 15 bug and run it (~30 min)

1. Fix `pipeline/gap_hunter_runner.py` — change the file write to patch only the gap section
2. Run it: `python pipeline/gap_hunter_runner.py --output ./results`
3. Verify no files shrunk (compare sizes before/after)
4. Then proceed to human review in `docs/`

### Option B — Skip Step 15, go straight to human review (~0 min)

The 25 documents are already 400–1963 lines of complete content.
Step 15 would only add marginal improvements. You can skip it and go straight to:
1. Open `docs/HUMAN_REVIEW_GUIDE.md`
2. Complete each review file (fill in Reviewer Action columns)
3. Resolve all 7 contradictions in `docs/06_REVIEW_Gap_Reports.md`
4. Start code generation from `results/ForwardEngineering_Docs/16_GENERATION_MANIFEST.json`

### Option C — Full re-run (not recommended — wastes ~2 hours)

Steps 1–13 will all skip instantly (already done). Only Steps 14–15 will run.
But you'll lose the existing documents. Not recommended unless something is broken.

---

## KEY FILES TO KNOW

| File | What it does |
|------|-------------|
| `run.py` | Master orchestrator — runs all 15 steps |
| `pipeline/base_runner.py` | call_claude() function — all AI calls go through here |
| `pipeline/rule_annotator_runner.py` | Step 0 — parallelised (6 threads), annotates PL/SQL files |
| `pipeline/foundation_runner.py` | Step 14 — generates 25 docs (3 Claude calls) |
| `pipeline/gap_hunter_runner.py` | Step 15 — self-healing loop (**has file-overwrite bug**) |
| `generate_missing_docs.py` | Utility — generates missing/thin docs individually (parallel, 5 workers) |
| `results/file_cache.json` | All 42 source files cached — pipeline reads from here, not source/ |
| `results/cross_validation_report.json` | 18 gaps + 7 contradictions found across tracks |
| `docs/HUMAN_REVIEW_GUIDE.md` | Start here for human review |
| `docs/06_REVIEW_Gap_Reports.md` | All 7 contradictions — must resolve before codegen |

---

## IMPORTANT KNOWN ISSUES

### 1. Step 15 file-overwrite bug
`gap_hunter_runner.py` replaces entire files with just the patched gap section when filling gaps.
**Must fix before running.** The documents are safe as long as Step 15 is not run.

### 2. Step 14 context overflow (historical — already fixed)
Step 14 originally sent huge context to Claude in 3 calls, causing truncation.
Fix was applied: `generate_missing_docs.py` generates each doc individually (one call per doc, 5 parallel workers).

### 3. Claude describes instead of writing (historical — already fixed)
Sometimes Claude responded with "Here is the document I wrote..." instead of the actual document.
Fix applied in `generate_missing_docs.py`: DIRECT_INSTRUCTION prefix + auto-retry logic.

### 4. Step 0 timeout
Step 0 (Rule Annotator) uses 6 parallel threads and takes ~25 min. Timeout is set to 7200s.
Do not reduce the timeout.

### 5. Resume safety
Every step checks if output exists before running. To force a step to re-run,
delete its output file/folder first.

### 6. Foundation_Raw_Output_Part*.md
These intermediate Step 14 files are in .gitignore (they cause false-skip on fresh clone).
If they appear in your results/ folder, it is safe to delete them.

---

## RESULTS SUMMARY (what was found)

- **42 source files** analysed (22 PL/SQL packages, 6 Oracle Forms, 11 SQL schema, triggers, seed data)
- **140 business rules** extracted (BA track)
- **310 implicit rules** extracted (Step 3.5)
- **30 database tables** mapped (DA track)
- **18 gaps** found between analysis tracks (13 auto-resolved)
- **7 contradictions** found between tracks — ALL need human decision (see docs/06_REVIEW_Gap_Reports.md)
- **33 quality findings** + 25 architecture violations + 14 risks (AA track)

### Critical findings for the new system (MUST FIX):
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
Step 14 (Foundation — 25 documents + Knowledge Graph)  ← generate_missing_docs.py used here
    │
    ▼
Step 15 (Gap Hunter — self-healing loop)  ← has bug, needs fix
    │
    ▼
results/ (50+ output files)
    │
    ▼
docs/ (Human Review — 7 files, pre-populated)
    │
    ▼
Code Generation (using 16_GENERATION_MANIFEST.json)
```

---

## CONTACTS

- Repo owner: Jaya Prakash
- Repo: https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1
- Word document (full pipeline explanation): ORACLE_HRMS_PIPELINE_EXPLAINED.docx
