<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=280&section=header&text=Oracle%20HRMS%20Reverse%20Engineering%20Pipeline&fontSize=36&fontColor=ffffff&fontAlignY=38&desc=Fully%20automated%20reverse%20engineering%20of%20Oracle%20Forms%20%2B%20PL%2FSQL%20legacy%20systems%20into%2025%20architecture%20documents&descAlignY=60&descSize=14&animation=fadeIn" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Claude AI](https://img.shields.io/badge/Claude-AI%20Powered-D97706?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Oracle](https://img.shields.io/badge/Oracle-Forms%20%2B%20PL%2FSQL-F80000?style=for-the-badge&logo=oracle&logoColor=white)](https://oracle.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

<br/>

> **Point this pipeline at any Oracle Forms + PL/SQL legacy codebase. Walk away.  
> Come back to 25 complete architecture documents + an Enterprise Knowledge Graph — fully automated.**

<br/>

[🚀 Quick Start](#-quick-start) · [🧠 How It Works](#-how-it-works) · [🛡️ Fallback Chain](#️-fallback-chain-nothing-gets-missed) · [📄 What It Produces](#-what-it-produces) · [🏗️ Architecture](#️-architecture) · [👥 Team Setup](#-team-setup)

</div>

---

## ✨ What This Does

Point this pipeline at your **Oracle Forms + PL/SQL legacy HRMS source code** and it:

1. Reads every source file — `.frmxml`, `.pks`, `.pkb`, `.sql`, triggers, schema — with **zero manual work**
2. Extracts all business logic, procedures, tables, rules, and form triggers into a structured deep scan
3. Runs **4 analysis tracks in parallel** (Business, Data, Technology, Application)
4. Synthesises everything into **25 architecture documents** + an **Enterprise Knowledge Graph**

Every gap at every stage is automatically detected and filled from lower layers — nothing is lost.

<br/>

<div align="center">

| | Manual (traditional) | This Pipeline |
|---|:---:|:---:|
| ⏱️ Time to full architecture | **2–4 weeks** | **~1.5 hours** |
| 👤 Human involvement | Every step | **Zero** |
| 📄 Documents produced | Varies | **25 docs + KG** |
| 🔁 Resume after interruption | Start over | **Continues exactly where it stopped** |
| 🔍 Evidence-cited findings | Depends on analyst | **Every single finding** |
| 🛡️ Missing data handling | Analyst notices manually | **Auto-detected + auto-filled** |

</div>

---

## 🚀 Quick Start

### Prerequisites

```bash
# 1. Python 3.9+
pip install -r requirements.txt

# 2. Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 3. Authenticate
claude login
```

### Run the Pipeline

```bash
# Point at your Oracle HRMS source folder
python run.py --source "C:/your-project/oracle-hrms-source" --output ./results
```

That's it. The pipeline runs all 13 steps automatically (~1.5 hours).

### Run Individual Steps (optional)

```bash
python run.py --source <source> --output ./results --track setup        # Steps 1–3: scan + cache
python run.py --source <source> --output ./results --track business     # Steps 4–5: BA analysis
python run.py --source <source> --output ./results --track data         # Steps 6–7: DA analysis
python run.py --source <source> --output ./results --track technology   # Steps 8–10: TA analysis
python run.py --source <source> --output ./results --track application  # Steps 11–12: AA analysis
python run.py --source <source> --output ./results --track foundation   # Step 13: 25 documents
```

### Resume After Interruption

Kill the pipeline at any time — re-run the **same command** and it continues from exactly where it stopped. Every step is checkpointed to disk.

---

## 🧠 How It Works

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          13-STEP PIPELINE                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 1  ─► Layer 1 Extraction   (deterministic, zero AI)                   │
│              Walks source tree, extracts structure into Source_Code.json     │
│              Auto-detects: Oracle Forms, PL/SQL, SQL, triggers, schema       │
│                                                                              │
│  Step 2  ─► Scan Once            (file_cache.json)                          │
│              Reads EVERY file in full — raw content, no truncation           │
│              Validates 100%: re-walks disk and confirms every file cached    │
│                                                                              │
│  Step 3  ─► Scan Agent           (DEEP_SCAN_OUTPUT.md)                      │
│              Splits files into chunks → Claude extracts procedures/rules     │
│              Self-corrects: detects missing files, re-scans up to 3×         │
│                                                                              │
│  ┌── Steps 4–12: ALL 4 TRACKS RUN IN PARALLEL ──────────────────────────┐  │
│  │                                                                        │  │
│  │  Steps  4–5  ► Business Analysis    Agent 1 → Agent 2 (+ gap fill)   │  │
│  │  Steps  6–7  ► Data Analysis        Agent 1 → Agent 2 (+ gap fill)   │  │
│  │  Steps  8–10 ► Technology Analysis  Agent 1 → Batch1 → Batch2+Synth  │  │
│  │  Steps 11–12 ► Application Analysis Agent 1 → Agent 2 (+ gap fill)   │  │
│  │                                                                        │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  Step 13 ─► Foundation Synthesis                                            │
│              Call 1: Enterprise KG + 5 foundation docs + docs 01–10         │
│              Call 2: docs 11–20  (receives gap-filled docs from Call 1)      │
│              Each of 25 documents independently detects and fills its gaps   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### The Two-Turn Agent Pattern

Every analysis agent (Steps 4–12) uses an efficient two-turn design:

```
Turn 1 — File Selection
  Agent sees:   FILE MAP (one line per file, no content)
  Agent replies: JSON array of exactly which files it needs
  Result:        Only relevant files are fetched — zero wasted tokens

Turn 2 — Deep Analysis
  Agent receives: only the requested file sections (from DEEP_SCAN + file_cache fallback)
  Agent produces: BA_Structural_Scout.md / DA_Data_Extractor.md / etc.
  After output:   Gap detection runs — missing items are fetched and supplemented
```

---

## 🛡️ Fallback Chain — Nothing Gets Missed

This is the core reliability feature. At **every layer**, if data is missing it automatically falls back to the layer below:

```
source files (42 Oracle HRMS files)
      │
      ▼
file_cache.json          ← raw content of every file, 100% complete, validated
      │  if DEEP_SCAN missed a file
      ▼
DEEP_SCAN_OUTPUT.md      ← Claude's extraction of every file (procedures, rules, logic)
      │  if chunk was incomplete (self-corrects up to 3×)
      ▼
Agent 1 (Scout)          ← broad map: what exists
      │
      ▼
Agent 2 (Analyst)        ← deep meaning: what it means
      │
      ├── gap detected in output?
      │         ▼
      │   DEEP_SCAN_OUTPUT.md    ← check if scan captured it
      │         │
      │         ├── still missing?
      │                   ▼
      │             file_cache.json  ← get raw content of that exact file
      │                   │
      │                   ▼
      │             Claude supplements only the missing parts
      │
      ▼
Foundation (25 documents)
      │
      └── each document independently:
                gap detected? → DEEP_SCAN → file_cache → fill only that gap
                Call 1 docs gap-filled → reloaded from disk → Call 2 gets complete context
```

**This applies identically to all 4 tracks:**

```
BA Agent 2 ──(gap)──► DEEP_SCAN ──(gap)──► file_cache → source
DA Agent 2 ──(gap)──► DEEP_SCAN ──(gap)──► file_cache → source
TA Agent 2 ──(gap)──► DEEP_SCAN ──(gap)──► file_cache → source
AA Agent 2 ──(gap)──► DEEP_SCAN ──(gap)──► file_cache → source
```

**Foundation — per-document (each of 25 files independently):**

```
01_BRD.md              ──(gap)──► DEEP_SCAN ──(gap)──► file_cache
06_DATA_DICTIONARY.md  ──(gap)──► DEEP_SCAN ──(gap)──► file_cache
ENTERPRISE_KG.json     ──(gap)──► DEEP_SCAN ──(gap)──► file_cache
... all 25 documents independently
```

---

## 📄 What It Produces

```
results/
│
├── file_cache.json                         ← full raw content of every source file
├── DEEP_SCAN_OUTPUT.md                     ← deep extracted content, self-corrected
│
├── Business_Analysis/
│   ├── BA_Structural_Scout.md              ← domains, entities, state machines, DDD
│   └── BA_Deep_Analyst.md                  ← all business rules, validations, processes
│
├── Data_Analysis/
│   ├── DA_Data_Extractor.md                ← all tables, columns, constraints, PII
│   └── DA_Data_Reviewer.md                 ← verified schema, data flows, quality
│
├── Technology_Analysis/
│   ├── TA_Stack_Scout.md                   ← Oracle Forms version, PL/SQL stack, DB
│   └── TA_Deep_Analyst.md                  ← NFR, security posture, tech debt map
│
├── Application_Analysis/
│   ├── AA_App_Extractor.md                 ← all packages, procedures, form triggers
│   └── AA_Quality_Review.md                ← completeness PASS/PARTIAL/FAIL verdicts
│
├── Foundation_KnowledgeGraph/
│   ├── ENTERPRISE_KNOWLEDGE_GRAPH.json     ← full KG: every node, cross-linked, evidence-cited
│   ├── CANONICAL_ENTERPRISE_MODEL.md       ← human-readable entity summary
│   ├── ARCHITECTURE_INVENTORY.md           ← every table, package, form, trigger
│   ├── TRACEABILITY_MATRIX.md              ← capability → process → entity → API → DB
│   └── FORWARD_ENGINEERING_INPUT_MAP.md    ← known / inferred / missing
│
└── ForwardEngineering_Docs/
    ├── 01_BRD.md                           ← Business Requirements Document
    ├── 02_BUSINESS_CAPABILITY_MODEL.md
    ├── 03_USE_CASE_SPECIFICATION.md
    ├── 04_BUSINESS_PROCESS_MODEL.md
    ├── 05_DOMAIN_MODEL.md                  ← DDD bounded contexts + Mermaid maps
    ├── 06_DATA_DICTIONARY.md               ← every table, every column, every constraint
    ├── 07_DATA_MODEL_SPECIFICATION.md      ← physical schema + SQL DDL
    ├── 08_ERD.md
    ├── 09_DATA_FLOW_DIAGRAM.md
    ├── 10_SERVICE_CATALOG.md
    ├── 11_API_CONTRACT_SPECIFICATION.md    ← full REST contracts for all endpoints
    ├── 12_TECHNOLOGY_BLUEPRINT.md
    ├── 13_SECURITY_ARCHITECTURE.md         ← RBAC model + modernisation plan
    ├── 14_NFR_SPECIFICATION.md
    ├── 15_FORWARD_ENGINEERING_SPECIFICATION.md
    ├── 16_GENERATION_MANIFEST.json
    ├── 17_FORWARD_ENGINEERING_READINESS_REPORT.md
    ├── 18_DEPLOYMENT_ARCHITECTURE.md
    ├── 19_FRONTEND_ARCHITECTURE.md
    └── 20_UI_UX_SPECIFICATION.md
```

**Total: 5 Foundation docs + 20 Forward Engineering docs + 1 Enterprise Knowledge Graph**

---

## 🏗️ Architecture

### Repository Structure

```
automated-reverse-engineering-pipeline/
│
├── run.py                                  ← Master orchestrator (13 steps, parallel tracks)
├── requirements.txt
│
├── pipeline/
│   ├── base_runner.py                      ← Core: call_claude(), fallback chain helpers
│   │   ├── supplement_from_cache()         ← fills DEEP_SCAN gaps from file_cache
│   │   └── detect_and_fill_gaps()          ← post-generation gap detection + supplement
│   │
│   ├── scan_runner.py                      ← Step 2: file_cache.json + completeness validation
│   ├── scan_agent_runner.py                ← Step 3: chunked deep scan + self-correction
│   ├── foundation_runner.py                ← Step 13: 25 docs + per-doc gap detection
│   │   ├── _fill_document_gaps()           ← per-document independent gap detection
│   │   └── _reload_filled_docs()           ← ensures Call 2 gets gap-filled Call 1 context
│   │
│   ├── layer1/                             ← Step 1: deterministic extraction (no AI)
│   │   ├── oracle_forms_extractor.py       ← .frmxml parser
│   │   ├── plsql_extractor.py              ← .pks/.pkb parser
│   │   ├── database_extractor.py           ← SQL DDL, Oracle packages
│   │   └── ...
│   │
│   └── runners/                            ← Steps 4–12: 8 specialised agents
│       ├── ba_agent1_runner.py             ← BA Scout (Turn 1 + Turn 2 + cache fallback)
│       ├── ba_agent2_runner.py             ← BA Analyst (+ detect_and_fill_gaps)
│       ├── da_agent1_runner.py / da_agent2_runner.py
│       ├── ta_agent1_runner.py
│       ├── ta_agent2_batch1_runner.py      ← TA Analyst Batch 1
│       ├── ta_agent2_batch2_runner.py      ← TA Analyst Batch 2 + Synthesis (+ gap fill)
│       ├── aa_agent1_runner.py / aa_agent2_runner.py
│
└── Prompts_Ready_To_Use/                   ← 8 Claude agent system prompts
    ├── 01_BA_Agent1_StructuralScout.md
    ├── 02_BA_Agent2_DeepAnalyst.md
    ├── 03_DA_Agent1_DataExtractor.md
    ├── 04_DA_Agent2_DataReviewer.md
    ├── 05_TA_Agent1_StackScout.md
    ├── 06_TA_Agent2_DeepAnalyst.md
    ├── 07_AA_Agent1_AppExtractor.md
    └── 08_AA_Agent2_QualityReview.md
```

### Supported Source Files (Oracle HRMS)

| File Type | Extension | What Gets Extracted |
|-----------|-----------|---------------------|
| Oracle Forms | `.frmxml` | Form blocks, items, triggers, buttons, LOVs |
| PL/SQL Package Specs | `.pks` | Package name, procedure signatures, types |
| PL/SQL Package Bodies | `.pkb` | Full procedure logic, business rules, validations |
| SQL Schema | `.sql` | Tables, columns, constraints, indexes, sequences |
| Triggers | `.trg` | Trigger type, event, business logic |
| Views | `.vw` | View definition, joins, business purpose |

---

## 🔧 Configuration

### Environment Variables

```bash
# Override Claude model (default: CLI default)
set PIPELINE_CLAUDE_MODEL=claude-opus-4-8

# Windows — set before running
set PIPELINE_CLAUDE_MODEL=
python run.py --source ./source --output ./results
```

### Run Options Reference

```bash
# Full pipeline — all 13 steps
python run.py --source <path> --output ./results

# Individual tracks
python run.py --source <path> --output ./results --track setup
python run.py --source <path> --output ./results --track business
python run.py --source <path> --output ./results --track data
python run.py --source <path> --output ./results --track technology
python run.py --source <path> --output ./results --track application
python run.py --source <path> --output ./results --track foundation

# Run a specific step range
python run.py --source <path> --output ./results --from-step 9 --to-step 9
```

---

## 👥 Team Setup

### Clone and Run

```bash
git clone https://github.com/jayaprakash2207/oracle-reverse-engg-correction-1.git
cd oracle-reverse-engg-correction-1

pip install -r requirements.txt
npm install -g @anthropic-ai/claude-code
claude login

python run.py --source "path/to/your/oracle-hrms-source" --output ./results
```

### What Each Team Member Gets

After the pipeline completes, share the `results/` folder. Each team member can open:

| Role | Most Relevant Documents |
|------|------------------------|
| **Business Analyst** | `01_BRD.md`, `02_BUSINESS_CAPABILITY_MODEL.md`, `03_USE_CASE_SPECIFICATION.md`, `04_BUSINESS_PROCESS_MODEL.md` |
| **Data Architect** | `06_DATA_DICTIONARY.md`, `07_DATA_MODEL_SPECIFICATION.md`, `08_ERD.md` |
| **Solution Architect** | `ENTERPRISE_KNOWLEDGE_GRAPH.json`, `12_TECHNOLOGY_BLUEPRINT.md`, `18_DEPLOYMENT_ARCHITECTURE.md` |
| **Security Team** | `13_SECURITY_ARCHITECTURE.md`, `14_NFR_SPECIFICATION.md` |
| **Developer** | `11_API_CONTRACT_SPECIFICATION.md`, `15_FORWARD_ENGINEERING_SPECIFICATION.md` |
| **Project Manager** | `17_FORWARD_ENGINEERING_READINESS_REPORT.md`, `TRACEABILITY_MATRIX.md` |
| **UX Designer** | `19_FRONTEND_ARCHITECTURE.md`, `20_UI_UX_SPECIFICATION.md` |

### If the Pipeline Is Interrupted

Just re-run the same command — it picks up exactly where it stopped:

```bash
python run.py --source "path/to/source" --output ./results
```

Every step writes its output to disk before moving to the next. Nothing is lost.

---

## 🎯 Key Design Decisions

### Why file_cache.json?
Every source file is read **once** at Step 2 and stored in full. No file is ever read from disk again. This means:
- Agents never hit file-not-found errors
- Every downstream step works from the same consistent snapshot
- If a source file changes, re-run Step 2 to refresh

### Why chunk self-correction?
Claude can stop mid-chunk when output is large. `scan_agent_runner.py` detects which files are missing from each chunk's output, re-scans only those files (not the whole chunk), and retries up to 3 times. This prevents one incomplete chunk from creating invisible gaps in all 8 downstream agents.

### Why parallel execution?
Steps 4–12 (the 4 analysis tracks) are completely independent — BA doesn't need DA's output and vice versa. Running them in parallel threads cuts total wall-clock time by ~4x.

### Why per-document gap detection in Foundation?
The 25 Foundation documents are each a different document type (BRD vs ERD vs API contracts). A gap in the Data Dictionary is irrelevant to the Deployment Architecture. Running gap detection independently on each document means:
- A thin ERD doesn't force a re-fetch of data that the BRD already covers
- Each document fetches only the specific files it is missing
- No document depends on another document's gap-fill completing first

### Why _reload_filled_docs?
Call 1 generates docs 1–10, gap-fills them, and saves to disk. But the in-memory `docs1` variable was parsed from the raw output — before gap filling. Without `_reload_filled_docs()`, Call 2 would receive incomplete versions of docs 1–10 as context, undoing all the gap-fill work. The reload step re-reads every Call 1 doc from disk (the enriched versions) before building Call 2's context.

---

## 📊 Anti-Hallucination Rules

Every node in the Enterprise Knowledge Graph must:
- **Cite** the exact source file and section it was found in
- **Grade** confidence: `HIGH` (direct code evidence) / `MEDIUM` (inferred) / `LOW` (assumed)
- **List** unverifiable assumptions separately in `assumptions[]` — never silently in the main graph
- **Mark** genuinely missing data as `MISSING` — never invent a plausible value

Agents are instructed: **"If you do not know → say unknown, not a guess."**

---

## 🤝 Contributing

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Commit your changes with descriptive messages
4. Push and open a Pull Request

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=120&section=footer" width="100%"/>

**Built with Claude AI · Python · Oracle Forms · PL/SQL**

⭐ **Star this repo if it saved your team weeks of manual analysis work!**

</div>
