# Project Progress Summary
**Project:** Oracle HRMS Reverse Engineering + Forward Engineering Pipeline  
**Date:** 2026-08-13  
**Prepared for:** Manager Review

---

## What This Project Does (One Paragraph)

We built an automated AI pipeline that takes an existing Oracle HRMS system (Oracle Forms 12c + Oracle DB 19c) — 42 source files — and reverse-engineers it into 25 structured, industry-standard enterprise documents. These documents then serve as the complete specification for rebuilding or migrating the system to any modern technology stack. The entire process runs with a single command: `python fresh_run_template.py`.

---

## Before vs Now — What Changed

### BEFORE (Original State)
| Area | What Existed |
|---|---|
| Pipeline | `foundation_runner.py` — single freeform runner. Claude generated documents with no enforced structure. |
| Templates | `HRMS_25_Enterprise_Forward_Engineering_Templates_FULL/` — HRMS-specific, not reusable for other projects. |
| Output quality | Claude decided the structure itself — sections could be missing, inconsistent, or differently named across runs. |
| Evidence tracking | No standardised evidence classification or confidence scoring. |
| Coverage | No measurement of how well documents matched the source code. |
| Missing evidence | "Validate with stakeholders" — vague, no named owner. |
| Entry point | `fresh_run.py` only — one mode, no template enforcement. |
| Worked examples | None in templates — Claude had no concrete reference for what a completed section looks like. |
| ID consistency | No cross-reference hints — BR-* IDs could be created in multiple documents inconsistently. |
| Quality gate | No per-section pass/fail criteria — no way to know if a section was actually complete. |

### NOW (Current State)
| Area | What Was Built |
|---|---|
| Pipeline | `foundation_runner_template.py` — template-driven runner. Every [M] mandatory section is enforced. |
| Templates | `GENERIC_25_Enterprise_Forward_Engineering_Templates_INDUSTRY_BASED/` — domain-neutral, works for HRMS, Finance, Logistics, Healthcare, or any project. |
| Output quality | Claude populates exact template skeletons — structure is guaranteed and consistent across every run. |
| Evidence tracking | Every claim has: evidence class (OBSERVED/DERIVED/INFERRED/ASSUMED/UNKNOWN/CONTRADICTED) + source reference + confidence score (0.00–0.95). |
| Coverage | Hybrid engine: Claude semantic estimate (Call 3) + Python exact counts (after Call 4) → `COVERAGE_SUMMARY.md` with CRITICAL / MEDIUM / NOT_AVAILABLE sections. |
| Missing evidence | Exact escalation table per section type: BA for business rules / DBA for schema / CISO for security / Architect for technology. |
| Entry point | `fresh_run_template.py` — new entry point; `fresh_run.py` untouched for legacy runs. |
| Worked examples | 2+ worked example rows in every complex section — concrete placeholder rows Claude can follow. |
| ID consistency | Cross-reference hints at every section where IDs are created — tells Claude exactly which other documents must use the same IDs. |
| Quality gate | Section-level acceptance criteria on every major section — inline pass/fail test. |
| Anti-patterns | Explicit "DO NOT" warnings per document — e.g. "Do NOT prescribe technology", "Do NOT mix BR-* and BR-SEC-*". |

### Key Numbers
| Metric | Before | Now |
|---|---|---|
| Templates | 25 (HRMS-specific, no examples) | 25 (generic, with examples + rubrics + 6 accuracy layers) |
| Reusable for other projects | No | Yes — any domain |
| Evidence classification | Not enforced | Mandatory on every claim |
| Confidence scoring | Not present | Standardised 0.00–0.95 scale across all 25 docs |
| Coverage measurement | None | Hybrid (semantic + exact count) per document |
| Human review guidance | Vague | Named stakeholder + specific question per section type |
| Worked examples per template | 0 | 1–2 per major section |
| Cross-reference enforcement | None | Present in every section that creates IDs |
| Anti-pattern warnings | None | 4–6 per document |
| Section acceptance criteria | None | Present on every key section |

---

## What We Have Built — End to End

### 1. Source Analysis (Already Done — Teammates' Work)
8 specialist AI agent reports are fed into the pipeline as inputs:

| Agent File | What It Covers |
|---|---|
| `BA_Structural_Scout.md` | High-level business structure scan |
| `BA_Deep_Analyst.md` | Deep business logic analysis |
| `DA_Data_Extractor.md` | Database schema and data extraction |
| `DA_Data_Reviewer.md` | Data quality and validation review |
| `TA_Stack_Scout.md` | Technology stack identification |
| `TA_Deep_Analyst.md` | Deep technical analysis |
| `AA_App_Extractor.md` | Application module extraction |
| `AA_Quality_Review.md` | Application quality review |

---

### 2. The Pipeline — `pipeline/foundation_runner_template.py`
The core engine. It runs 4 sequential Claude AI calls:

| Call | What It Generates |
|---|---|
| **Call 1** | Knowledge Graph (KG) + Documents 01–10 |
| **Call 2** | Documents 11–20 |
| **Call 3** | Verification pass + Coverage estimation (Claude semantic) |
| **Call 4** | Cross-document consistency pass |
| **Post-run** | Python exact coverage counts → `COVERAGE_SUMMARY.md` |

**Resume capability:** If the run is interrupted, it checks for existing Part 1/2/3/4 raw output files and skips completed calls — no work is lost.

---

### 3. The 25 Output Documents

**Foundation Knowledge Graph (5 documents):**

| # | Document | Purpose |
|---|---|---|
| 1 | Enterprise Knowledge Graph (JSON) | Machine-readable map of all entities, services, rules |
| 2 | Business Requirements Document | All BR-* business requirements |
| 3 | Business Capability Model | CAP-* capability catalog |
| 4 | Domain Model | DOM-* business concepts and relationships |
| 5 | Data Dictionary | DE-* canonical field definitions |

**Forward Engineering Docs (20 documents):**

| # | Document | Purpose |
|---|---|---|
| 6 | Use Case Specification | UC-* actor interactions |
| 7 | Business Process Model | PRC-* process flows |
| 8 | Data Model Specification | ENT-* entity/table specs |
| 9 | ERD Document | Entity Relationship Diagram spec |
| 10 | DFD Document | Data Flow Diagram spec |
| 11 | Service Catalog | SVC-* service registry |
| 12 | API Contract Specification | IF-*/OP-* interface definitions |
| 13 | Technology Blueprint | Architecture layers and components |
| 14 | Security Architecture | BR-SEC-* security requirements |
| 15 | NFR Specification | NFR-* non-functional requirements |
| 16 | Forward Engineering Specification | Source-to-target transformation rules |
| 17 | Generation Manifest (JSON) | Machine-readable generation instructions |
| 18 | Forward Engineering Readiness Report | GO/CONDITIONAL/BLOCKED decision |
| 19 | Deployment Architecture | Environment and deployment model |
| 20 | Frontend Architecture | UI module architecture |
| 21 | UI/UX Specification | Screen and field specifications |
| 22 | Canonical Enterprise Model | Master vocabulary and semantic mappings |
| 23 | Architecture Inventory | ARCH-* component inventory |
| 24 | Traceability Matrix | End-to-end BR-* to source traceability |
| 25 | Forward Engineering Input Map | FEI-* input registry for code generation |

---

### 4. The 25 Generic Industry Templates
Folder: `GENERIC_25_Enterprise_Forward_Engineering_Templates_INDUSTRY_BASED/`

Each of the 25 output documents is driven by a corresponding template. These templates are:
- **Technology-neutral** — no React, AWS, Spring Boot, or vendor lock-in
- **Domain-neutral** — work for HRMS, Finance, Logistics, Healthcare, or any domain
- **Industry-standard** — aligned with ISO/IEC/IEEE 29148, 15288, 12207, ISO 25010, TOGAF, BPMN, UML, NIST

**What each template contains:**

| Section | Purpose |
|---|---|
| Document conventions | Mandatory/Conditional/Optional markers, evidence classes |
| Common Mistakes to Avoid | Anti-pattern warnings specific to that document type |
| NOT_AVAILABLE Escalation Path | Who to contact (BA / DBA / CISO / Architect) when evidence is missing |
| Evidence and Traceability Rules | Every claim needs a source reference, evidence class, and confidence score |
| Confidence Calibration Guide | DDL evidence → 0.90–0.95 / Inferred → 0.50–0.70 / Unknown → 0.00 |
| Document Dependencies | What feeds this doc (upstream) and what it feeds (downstream) |
| Content sections | All mandatory [M] sections with worked examples |
| Cross-reference hints | Exact instruction on which IDs must match which other documents |
| Section-level acceptance criteria | Pass/fail test for each major section |
| Assumptions / Contradictions / Open Questions | Explicit uncertainty tracking |
| Readiness Scoring | 0–3 scale per dimension; READY / CONDITIONAL / BLOCKED decision |
| Quality Gate checklist | Pre-flight checklist before marking document complete |
| Traceability Matrix | End-to-end trace links |

---

### 5. Accuracy Improvements Built Into Every Template

Six targeted improvements were added to all 25 templates to maximize output quality:

| # | Improvement | What It Does |
|---|---|---|
| 1 | **Anti-pattern warnings** | Tells Claude exactly what NOT to do in each document (e.g. "Do NOT prescribe technology", "Do NOT merge BR-* and BR-SEC-* ID series") |
| 2 | **More worked examples** | Complex documents (03, 06, 11, 13) have 2+ worked example rows showing real placeholder structures |
| 3 | **Cross-reference hints** | At each section where IDs are created, an explicit note names the other documents that must use the same IDs |
| 4 | **Confidence calibration guide** | Standardized confidence scale (0.00–0.95) in every document — prevents over-confident inferences |
| 5 | **Section-level acceptance criteria** | Every major section has an inline pass/fail test — e.g. "At least 3 entities defined, each with PK, lifecycle, and source reference" |
| 6 | **NOT_AVAILABLE escalation path** | Instead of generic "validate with stakeholders", specifies exactly who: BA for business rules / DBA for schema / CISO for security |

---

### 6. Hybrid Coverage Engine
After all 4 calls complete, the pipeline calculates how well each document matches the source evidence:

**Option 1 — Claude Semantic Estimate (during Call 3)**
- Claude reviews its own output and estimates coverage qualitatively
- Fast, context-aware

**Option 2 — Python Exact Counts (after Call 4)**
- Counts every `OBSERVED`, `DERIVED`, `INFERRED`, `ASSUMED`, `UNKNOWN`, `CONTRADICTED` tag
- Calculates: `Source Match % = (OBSERVED + DERIVED) / total evidence tags × 100`
- Averages confidence scores per document
- Overwrites Option 1 estimates with exact numbers

**Output: `COVERAGE_SUMMARY.md`** — three action sections:
- `CRITICAL (< 60%)` — Human review required immediately
- `MEDIUM (60–79%)` — Human review recommended
- `NOT_AVAILABLE sections` — Stakeholder input needed
- Full ranked table (lowest match first)

---

### 7. Entry Points

| File | What It Runs | When to Use |
|---|---|---|
| `fresh_run_template.py` | Template-driven pipeline (new) | **Use this** — enforces all 25 templates |
| `fresh_run.py` | Freeform pipeline (original) | Legacy — Claude decides structure freely |

---

### 8. ID Series — Never Mix These

| ID Series | Belongs In | Meaning |
|---|---|---|
| `BR-*` | 01_BRD | Business requirements |
| `BR-SEC-*` | 13_SECURITY_ARCHITECTURE | Security defects/requirements |
| `BRL-*` | 01_BRD Section 8 | Business rules |
| `CAP-*` | 02_BUSINESS_CAPABILITY_MODEL | Capabilities |
| `UC-*` | 03_USE_CASE_SPECIFICATION | Use cases |
| `PRC-*` | 04_BUSINESS_PROCESS_MODEL | Processes |
| `DOM-*` | 05_DOMAIN_MODEL | Domain concepts |
| `DE-*` | 06_DATA_DICTIONARY | Data elements |
| `ENT-*` | 07_DATA_MODEL_SPECIFICATION | Entities |
| `SVC-*` | 10_SERVICE_CATALOG | Services |
| `IF-*/OP-*` | 11_API_CONTRACT | Interface operations |
| `NFR-*` | 14_NFR_SPECIFICATION | Non-functional requirements |
| `ARCH-*` | 23_ARCHITECTURE_INVENTORY | Architecture components |
| `FEI-*` | 25_FORWARD_ENGINEERING_INPUT_MAP | Generation inputs |

---

## Current Status

| Component | Status |
|---|---|
| Pipeline engine (`foundation_runner_template.py`) | COMPLETE |
| 25 generic industry templates | COMPLETE |
| 6 accuracy improvements on all templates | COMPLETE |
| Hybrid coverage engine | COMPLETE |
| Entry point (`fresh_run_template.py`) | COMPLETE |
| Source input files (8 agent reports) | WAITING — teammates to supply |

**Next step:** Teammates send the 8 agent input files into `results_fresh/` subfolders. Then run:
```
python fresh_run_template.py
```

---

## What This Delivers to the Business

- **Complete engineering specification** for rebuilding the HRMS system — 25 documents covering business, data, security, architecture, and UX
- **Technology-neutral** — the team chooses the target stack; this pipeline does not lock anyone in
- **Reusable for any project** — templates work for Finance, Logistics, Healthcare, or any domain, not just HRMS
- **Auditable quality** — every claim has an evidence class, source reference, and confidence score
- **Clear escalation** — when evidence is missing, the document names the exact stakeholder to contact
- **Readiness gate** — each document produces a GO / CONDITIONAL / BLOCKED decision before forward engineering begins

---

*Generated by Claude Code — for questions contact the pipeline team.*
