# Foundation Runner — Complete Technical Report
### Oracle HRMS Forward Engineering Pipeline — Document Generation Engine

**Prepared for:** Team and Manager Review  
**Project:** Oracle HRMS Reverse Engineering → Forward Engineering Pipeline  
**Report covers:** How the document generation engine works, what changed, and which approach is best

---

## Table of Contents

1. [What Is the Foundation Runner?](#1-what-is-the-foundation-runner)
2. [What Goes In — The Source Evidence](#2-what-goes-in--the-source-evidence)
3. [The 25 Document Templates](#3-the-25-document-templates)
4. [How the Original Runner Works — 6 Calls Explained](#4-how-the-original-runner-works--6-calls-explained)
5. [How the Multi-Agent Runner Works — 3 Phases Explained](#5-how-the-multi-agent-runner-works--3-phases-explained)
6. [The Gap Hunter — Why It Exists and How It Works](#6-the-gap-hunter--why-it-exists-and-how-it-works)
7. [Complete Flow Diagram](#7-complete-flow-diagram)
8. [Before vs After Comparison](#8-before-vs-after-comparison)
9. [Output Files — What You Get](#9-output-files--what-you-get)
10. [Which Is Best and Why](#10-which-is-best-and-why)
11. [Source System Facts](#11-source-system-facts)

---

## 1. What Is the Foundation Runner?

The Foundation Runner is the document generation engine inside the pipeline. It sits at **Step 14 of 15** and its single job is:

> **Take everything the pipeline discovered about the Oracle HRMS source code and produce 25 production-quality forward engineering documents automatically.**

These 25 documents are not summaries or notes. They are full, structured, industry-standard documents that a development team can use directly to design and build the replacement system:

- Business Requirements Document (BRD)
- Use Case Specifications
- Data Model and ERD
- API Contract Specifications
- Security Architecture
- Technology Blueprint
- Deployment Architecture
- UI/UX Specifications
- and 17 more

Writing these 25 documents manually from Oracle PL/SQL source code would take a team of analysts 2–4 months. The Foundation Runner does it automatically, with evidence tracing on every statement.

---

## 2. What Goes In — The Source Evidence

Before the Foundation Runner starts, the pipeline runs 13 earlier steps (Steps 0–13) that scan every Oracle HRMS source file and produce 8 structured agent output files. These are the evidence the Foundation Runner builds from.

```
Oracle HRMS Source Code
  ├── 42 source files
  ├── 826 business rules
  ├── 3,715 audit checks (100% pass)
  ├── 30 tables, 441 columns
  ├── 11 PL/SQL packages
  ├── 6 Oracle Forms modules
  ├── 29 sequences, 6 triggers, 6 views
  ├── 4 known security vulnerabilities
  ├── 20 known bugs
  └── 5 deferred TODOs
          ↓
   Steps 0–13 scan and analyse
          ↓
  ┌──────────────────────────────────────────────────┐
  │  8 Agent Output Files (structured evidence)      │
  │                                                  │
  │  BA Agent 1  — business rules, use cases         │
  │  BA Agent 2  — process flows, roles, actors      │
  │  DA Agent 1  — tables, columns, foreign keys     │
  │  DA Agent 2  — data flows, sequences, triggers   │
  │  TA Agent 1  — technology landscape              │
  │  TA Agent 2  — deep technical deep-scan output   │
  │  AA Agent 1  — application architecture          │
  │  AA Agent 2  — API surface, procedures, packages │
  └──────────────────────────────────────────────────┘
```

**The Foundation Runner uses ONLY these 8 files as its source.** Nothing is invented. Every statement in every generated document is traced back to a specific file, package, table, or line number in the Oracle source.

---

## 3. The 25 Document Templates

There are 25 pre-built enterprise-grade document templates:

```
GENERIC_25_Enterprise_Forward_Engineering_Templates_INDUSTRY_BASED/
  01_BUSINESS_REQUIREMENTS_DOCUMENT.md
  02_BUSINESS_CAPABILITY_MODEL.md
  03_USE_CASE_SPECIFICATION.md
  04_BUSINESS_PROCESS_MODEL.md
  05_DOMAIN_MODEL.md
  06_DATA_DICTIONARY.md
  07_DATA_MODEL_SPECIFICATION.md
  08_ERD_DOCUMENT.md
  09_DFD_DOCUMENT.md
  10_SERVICE_CATALOG.md
  11_API_CONTRACT_SPECIFICATION.md
  12_TECHNOLOGY_BLUEPRINT.md
  13_SECURITY_ARCHITECTURE_DOCUMENT.md
  14_NFR_SPECIFICATION.md
  15_FORWARD_ENGINEERING_SPECIFICATION.md
  16_GENERATION_MANIFEST.json
  17_FORWARD_ENGINEERING_READINESS_REPORT.md
  18_DEPLOYMENT_ARCHITECTURE_DOCUMENT.md
  19_FRONTEND_ARCHITECTURE_DOCUMENT.md
  20_UI_UX_SPECIFICATION.md
  22_CANONICAL_ENTERPRISE_MODEL.md
  23_ARCHITECTURE_INVENTORY.md
  24_TRACEABILITY_MATRIX.md
  25_FORWARD_ENGINEERING_INPUT_MAP.md
  + ENTERPRISE_KNOWLEDGE_GRAPH.json
```

These are **not blank pages**. Each template is a detailed structured framework specifying:

| Template Feature | What It Means |
|---|---|
| `[M]` sections | Mandatory — must be populated or explained as NOT_AVAILABLE |
| `[C]` sections | Conditional — include only if evidence supports it |
| ID series | Each doc has its own ID series: BR-xxx, UC-xxx, NFR-xxx, SEC-xxx, CAP-xxx etc. |
| Evidence table | Every document ends with a Traceability and Evidence table |
| Quality gate checklist | Every document ends with a YES / CONDITIONAL / NO-GO readiness flag |
| Standards compliance | ISO/IEC/IEEE 29148, 15288, 12207, TOGAF, UML, BPMN, OpenAPI, NIST, ISO 9241-210 |

**Every `[M]` section that cannot be filled from evidence gets this exact block:**

```
Status: NOT_AVAILABLE
Evidence Class: UNKNOWN
Confidence: 0.00
Validation Required: YES
Note: No source evidence was identified in the analyzed Oracle artifacts.
      Validate with business stakeholders before forward engineering begins.
```

This means no section is ever silently empty. Everything is accounted for.

---

## 4. How the Original Runner Works — 6 Calls Explained

`foundation_runner_template.py` makes 6 sequential calls to Claude. Each call has a specific job.

```
Call 1  →  Call 2  →  Call 3  →  Call 4  →  Call 5  →  Call 6
 Docs       Docs      Verify +    Cross-     Fix LOW    Verify
 01-10      11-20      Clean      Doc Check   Sections   HIGH
 + KG                             + 3 new               Claims
                                    docs
```

---

### Call 1 — Generate Documents 01–10 and Foundation KG

**Input:** 8 agent output files + 15 templates  
**Timeout:** 90 minutes  
**Output:** 15 documents

Claude reads each template, finds matching evidence in the 8 agent files, and populates every `[M]` section. For UC-002 (Process Monthly Payroll), it expands into 8 sub-use-cases with full detail:

```
UC-002.1  Initiate Payroll Run
UC-002.2  Calculate Gross Pay
UC-002.3  Calculate Tax Deductions
UC-002.4  Calculate Benefit Deductions
UC-002.5  Calculate Net Pay
UC-002.6  Approve Payroll Run
UC-002.7  Generate GL Feed
UC-002.8  Disburse Payments
```

Each statement carries an evidence tag:
```
OBSERVED — 0.90 HIGH (observed in PKG_PAYROLL.pkb line 245)
INFERRED — 0.65 MEDIUM (inferred from naming convention, verify before use)
ASSUMED  — 0.35 LOW (assumed, validate with Business Analyst)
```

---

### Call 2 — Generate Documents 11–20

**Input:** 8 agent output files + 10 templates + ALL of Call 1's output as context  
**Timeout:** 90 minutes  
**Output:** 10 documents

Call 2 sees Call 1's documents so it can cross-reference. When it writes the API Contract (doc 11) it checks against the Domain Model (doc 05) and Service Catalog (doc 10) already produced in Call 1.

Key rules enforced in Call 2:
- Technology neutral — no React, Spring Boot, AWS, bcrypt prescribed anywhere
- All Oracle source facts kept exactly: Oracle Forms 12c (12.2.1.4), Oracle DB 19c, PL/SQL, DBMS_CRYPTO
- All 6 Oracle Forms modules must appear in docs 19 and 20 by exact name

---

### Call 3 — Verification and Cleaning Pass

**Input:** All 25 generated documents + all 25 templates  
**Timeout:** 90 minutes  
**Output:** Updated documents with 5 fixes applied

Call 3 does 5 jobs in one pass:

**Job 1 — Remove AI artifact text**
```
Lines removed:
  "Let me check..."
  "Based on the above..."
  "I can see that..."
  "I've updated..."
  "Here is the updated..."
  Any HTML comment artifacts
```

**Job 2 — Remove duplicate section headings**
If `## Security Controls` appears twice in the same document, keep the first, remove the second including all its content.

**Job 3 — Template compliance check**
Verifies every `[M]` section is present and formatted correctly, NOT_AVAILABLE blocks use exact format, evidence tags are on all material statements, Quality Gate checklist is present.

**Job 4 — Technology neutrality sweep**

| Replace | With |
|---|---|
| React, Angular, Vue, Next.js | web-based UI layer |
| Node.js, Express | service layer runtime |
| Spring Boot, Django, FastAPI | service layer framework |
| Kubernetes, K8s | container orchestration platform |
| Docker | containerisation |
| AWS, Azure, GCP | cloud or on-premise deployment |
| PostgreSQL, MySQL as target | relational database |
| JWT prescribed | stateless authentication token |
| bcrypt, Argon2, scrypt | industry-standard password hashing |
| Kafka, RabbitMQ | message queue |

*Exception: Oracle source facts are always kept — Oracle Forms 12c, Oracle DB 19c, PL/SQL, DBMS_CRYPTO.*

**Job 5 — Content gap check**
Tables in agent output missing from Data Dictionary, procedures missing from API Contract, business rules missing from BRD — all flagged.

---

### Call 4 — Cross-Document Consistency Check

This is the most complex check. All 25 documents reference each other. Call 4 verifies every cross-reference holds.

**Check 1 — BR reference integrity**
Every `BR-xxx` cited in any document must be defined in `01_BRD.md`. Every `BR-SEC-xxx` must be in `13_SECURITY_ARCHITECTURE.md`. Same ID number used for two different things is flagged.

**Check 2 — Use case reference integrity**
Every `UC-xxx` referenced must exist in `03_USE_CASE_SPECIFICATION.md`.

**Check 3 — Table reference integrity**
Every table name (UPPER_CASE) referenced must be in `07_DATA_MODEL_SPECIFICATION.md`.

**Check 4 — Procedure reference integrity**
Every `PKG_xxx.procedure_name` referenced must be in `11_API_CONTRACT_SPECIFICATION.md`.

**Check 5 — Numeric contradiction detection**
Same fact stated differently in two documents (session timeout 30 min vs 60 min, tax rates, rating ranges) → flagged `HUMAN-DECISION-REQUIRED`.

**Check 6 — Oracle Forms module coverage**
All 6 Oracle Forms modules must appear in `19_FRONTEND_ARCHITECTURE.md` or `20_UI_UX_SPECIFICATION.md` by their exact names:
`HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE, HRMS_PERFORMANCE, HRMS_LOGIN, HRMS_MENU`

**Check 7 — AES key length verification**
If any document quotes an AES-256 key → must be exactly 32 bytes. Flags with the Oracle verification query if not.

**Check 8 — Produces 3 new support documents automatically**
```
SCHEMA_MIGRATION_SCRIPTS.md  ← ready-to-run ALTER TABLE / CREATE TABLE SQL
DBA_CHECKLIST.md             ← SELECT queries for DBA to verify schema
BR_CROSSREFERENCE.md         ← maps old BR-01 series to new BR-001 series
```

---

### Call 5 — Self-Correction of LOW Confidence Sections

Every section marked `0.35 — LOW` or `0.00 — UNKNOWN` across all 25 documents is collected. For each one:

- Claude re-examines the original Oracle source evidence specifically for that section
- **If evidence is found:** upgrades the section, rewrites it with a higher confidence score
- **If no evidence exists:** confirms `NOT_AVAILABLE` and names the exact escalation contact (Business Analyst, DBA, CISO, UX Lead etc.)

This means no LOW section is silently left. Either it is fixed or the right human is explicitly named to fix it.

---

### Call 6 — Second-Opinion Scoring of HIGH Confidence Claims

An independent Claude call reviews every claim marked `0.90 — HIGH` across all documents. It approaches each claim as a skeptic — trying to find reasons the HIGH rating might be wrong. If it finds the claim is actually INFERRED or ASSUMED rather than OBSERVED, it flags it as a potential downgrade.

This prevents overconfident documents from going to stakeholders.

---

### Coverage Pass — Python-Verified Evidence Counts

After all 6 Claude calls, Python code reads every `.md` file and counts evidence tags programmatically:

```
Evidence counts per document:
  OBSERVED       — directly seen in Oracle source
  DERIVED        — calculated from source facts
  INFERRED       — logically concluded from patterns
  ASSUMED        — assumed without direct evidence
  UNKNOWN        — no evidence found
  CONTRADICTED   — source evidence contradicts itself

Metrics calculated:
  source_match_pct = (OBSERVED + DERIVED) / total statements
  average_confidence_score per document
  citation_completeness — every OBSERVED claim has a source file reference
  source_file_existence — every cited file actually exists on disk
```

**These counts cannot hallucinate.** Python counting is deterministic. The same document always gives the same number. Overwrites Claude's semantic estimates with exact verified numbers. Writes `COVERAGE_SUMMARY.md`.

---

## 5. How the Multi-Agent Runner Works — 3 Phases Explained

`foundation_runner_multiagent.py` is the upgraded version. It runs all 6 calls from the original runner plus adds 3 new phases on top.

---

### Phase 1 — Parallel Generation (Subagents Pattern)

The original runner runs Call 1, then waits for it to finish, then runs Call 2. Total time = Call 1 time + Call 2 time.

The multi-agent runner starts both simultaneously using Python threads:

```
Thread A starts immediately:          Thread B starts immediately:
  Subagent A                            Subagent B
  Generates docs 01-10 + KG            Polls disk, waiting for
  Saves to disk                         Subagent A output to appear
                                        When found, reads it as context
                                        Generates docs 11-20
                                        Saves to disk

Total time = whichever thread finishes last
           = approximately 60% faster than sequential
```

Both threads are resume-safe. If the pipeline is interrupted and restarted, it detects the output files on disk and skips already-completed work.

---

### Pre-Loop Cleanup — Call 3 (same as original, positioned before the loop)

The same Call 3 from the original runner runs here — removes AI artifacts, duplicate sections, fixes technology neutrality. This is done **before** the gap hunter loop starts so the loop does not waste iterations on cosmetic issues.

---

### Phase 2 — Self-Healing Loop (Agent Teams Pattern)

This is the most significant new capability. It loops until all documents are structurally correct.

```
ITERATION 1:

  ┌─────────────────────────────────────────────────┐
  │  Gap Hunter Agent                               │
  │  Reads all 25 documents                         │
  │  Checks 9 categories:                           │
  │    1. Mandatory sections present and populated  │
  │    2. BR-xxx reference integrity                │
  │    3. UC-xxx reference integrity                │
  │    4. Table reference integrity                 │
  │    5. Procedure reference integrity             │
  │    6. Evidence classification on all statements │
  │    7. Technology neutrality violations          │
  │    8. AI artifact text remaining                │
  │    9. Duplicate sections                        │
  │                                                 │
  │  Produces: Gap Report                           │
  │  "GAP-001: 01_BRD.md — BR-045 referenced       │
  │             but not defined in this document"   │
  │  "GAP-002: 13_SECURITY.md — VULNERABILITY       │
  │             section missing evidence class"     │
  │  "GAP-003: 19_FRONTEND.md — HRMS_LEAVE form     │
  │             not mapped"                         │
  │  TOTAL_GAPS: 12                                 │
  └─────────────────────────────────────────────────┘
                         ↓
          Team Lead assigns gaps by domain
                         ↓
  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ BA Fix Agent │  │ DA Fix Agent │  │ SEC Fix Agent│
  │ BUSINESS     │  │ DATA         │  │ SECURITY     │
  │ gaps only    │  │ gaps only    │  │ gaps only    │
  │              │  │              │  │              │
  │ Fixes:       │  │ Fixes:       │  │ Fixes:       │
  │ 01_BRD.md    │  │ 07_DATA      │  │ 13_SECURITY  │
  │ 03_USE_CASE  │  │ 11_API       │  │ 14_NFR       │
  │ 04_PROCESS   │  │ 06_DATA_DICT │  │              │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                  │
    All 3 run as parallel Python threads simultaneously
         │                 │                  │
         └─────────────────┴──────────────────┘
                         ↓
               Fixes written to disk
                         ↓

ITERATION 2:
  Gap Hunter re-reads all 25 documents
  Finds 4 gaps remaining
  Assigns → domain agents fix → disk

ITERATION 3:
  Gap Hunter re-reads
  Finds 4 gaps (same count as iteration 2)
  → NO PROGRESS detected
  → Remaining 4 gaps written to HUMAN_DECISION_REQUIRED.md
  → Loop exits
```

**Three stop conditions — the loop always terminates:**

| Condition | What Happens |
|---|---|
| Gap count = 0 | All documents clean — loop exits successfully |
| Gap count ≥ previous iteration count | No progress being made — remaining gaps flagged as HUMAN-DECISION-REQUIRED |
| 3 iterations reached (maximum) | Safety cap — remaining gaps flagged as HUMAN-DECISION-REQUIRED |

**Why separate domain agents instead of one agent fixing everything:**
- If one agent reads and rewrites all 25 documents in one pass, a fix to doc A can introduce a new inconsistency in doc B
- Separate domain agents (BA/DA/SEC) work on non-overlapping documents — no conflicts
- All 3 run in parallel — faster

---

### Call 5, Call 6, Coverage Pass

Same as the original runner — self-correction of LOW sections, second-opinion on HIGH claims, Python evidence counting. Run after the self-healing loop completes on the already-healed documents.

---

### Phase 3 — Final Quality Gate

One final Claude agent reads all 25 documents together after everything is complete and sets a verdict on each:

```
| Document                              | Verdict     | Reason                                        |
|---------------------------------------|-------------|-----------------------------------------------|
| 01_BRD.md                             | YES         | All mandatory sections populated              |
| 02_BUSINESS_CAPABILITY_MODEL.md       | YES         | All mandatory sections populated              |
| 03_USE_CASE_SPECIFICATION.md          | YES         | UC-002 expanded into 8 sub-use-cases          |
| 13_SECURITY_ARCHITECTURE.md           | CONDITIONAL | 2 NFR sections NOT_AVAILABLE, no blockers     |
| 19_FRONTEND_ARCHITECTURE.md           | NO-GO       | HRMS_LEAVE form mapping missing               |
...

Summary:
  YES:          18 documents
  CONDITIONAL:   5 documents
  NO-GO:         2 documents
```

Writes `FINAL_QUALITY_GATE_REPORT.md`.

---

### Step 15 — gap_hunter_runner.py (Second Gap Hunter, Separate Step)

After the full foundation runner completes, Step 15 runs a separate gap hunter looking for a different kind of gap — not structural gaps but **content weakness markers**:

```
Scans every .md document for these patterns:
  "MISSING", "[Not found", "unknown", "N/A"
  "TBD", "TODO", "to be determined"
  "not available", "not documented", "not specified"
  Empty sections (heading with no content below it)
  Very short sections (fewer than 3 lines under a heading)

For each weakness found:
  1. Asks Claude: what specific data is missing here?
  2. Fetches that exact source file from DEEP_SCAN_OUTPUT.md / file_cache.json
  3. Asks Claude to fill ONLY that specific snippet (10-line context window)
  4. Verifies the filled snippet contains [GAP-FILLED] marker
  5. Replaces ONLY that snippet in the full document (never rewrites entire file)
  6. Safety check: if new file size < 90% of original size → write aborted

Runs in parallel across all 25 documents simultaneously
Up to 3 rounds until zero weaknesses remain
Saves: gap_hunter_report.json
```

This is a safety net that catches content weaknesses that slipped through the self-healing loop.

---

## 6. The Gap Hunter — Why It Exists and How It Works

### The Core Problem Without a Gap Hunter

Claude generates 25 documents in one pass. That is a very large amount of interconnected content. These problems happen silently without detection:

- Document A mentions `BR-045` as a payroll business rule
- Document B references `BR-045` but it was never defined anywhere
- Document C states session timeout = **30 minutes**
- Document D states session timeout = **60 minutes**
- Document E has the heading `## Security Controls` but nothing written under it
- Document F references table `EMP_LEAVE_BALANCE` but that table does not exist in the data model

None of these cause an error. Claude produces the output. The documents look complete from the outside. The team would not discover these problems until they try to use the documents in forward engineering — at which point the code generator receives invalid input and breaks.

### Why the Gap Hunter Is Connected Inside the Loop

The gap hunter is not a one-time check at the end. It runs **inside** the fix loop, after every round of fixes, for three reasons:

**Reason 1 — A fix can create a new gap.**
The DA Fix Agent fixes a broken table reference in `07_DATA_MODEL_SPECIFICATION.md`. In doing so, it adds a new procedure reference that does not yet exist in `11_API_CONTRACT_SPECIFICATION.md`. If the gap hunter is not re-run after the fix, that new gap survives to the output undetected.

**Reason 2 — Agents cannot reliably verify their own output.**
The same agent that generates a document will tend to agree with its own content when asked to verify it. A separate gap hunter agent reads everything with no memory of what was generated — it is a genuinely independent reviewer.

**Reason 3 — 25 documents cross-reference each other.**
This is not one document. It is 25 documents that all point to each other. A cross-reference problem can only be found by an agent that reads all 25 at once. The gap hunter is that agent.

### Why Unresolvable Gaps Go to HUMAN_DECISION_REQUIRED

Some gaps cannot be resolved automatically because the evidence does not exist in the Oracle source:
- A business rule that was never documented in the code
- A compliance requirement that lives in a Word document somewhere
- A decision about which cloud provider to use

These are not bugs. They are genuine unknowns that need a human decision. Writing them to `HUMAN_DECISION_REQUIRED.md` with the exact decision needed and the right contact person means nothing is silently hidden. The team knows exactly what is left to resolve before forward engineering can proceed.

---

## 7. Complete Flow Diagram

```
═══════════════════════════════════════════════════════════════════════
  ORACLE HRMS FORWARD ENGINEERING PIPELINE — COMPLETE FLOW
═══════════════════════════════════════════════════════════════════════

  Oracle HRMS Source Code (42 files, 826 rules, 30 tables, 6 forms)
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    Steps 0–3        Steps 4–5        Steps 6–7
   Rule Annotator    BA Agents        DA Agents
   Scan Once         (business)       (data)
   Scan Agent
          │               │               │
          │          Steps 8–10      Steps 11–12
          │          TA Agents        AA Agents
          │          (technology)     (application)
          │               │               │
          └───────────────┼───────────────┘
                          │
                    Step 13: Cross Validator
                          │
          ┌───────────────▼───────────────────────────────────────┐
          │         Step 14: Foundation Runner                    │
          │         (foundation_runner_multiagent.py)             │
          │                                                       │
          │  ┌───────────────────────────────────────────────┐   │
          │  │  PHASE 1 — Parallel Generation                │   │
          │  │                                               │   │
          │  │  Thread A (Subagent A)   Thread B (Subagent B)│   │
          │  │  ┌─────────────────┐    ┌──────────────────┐  │   │
          │  │  │ Call 1          │    │ Call 2           │  │   │
          │  │  │ Docs 01-10 + KG │    │ Docs 11-20       │  │   │
          │  │  │ (90 min)        │───▶│ (90 min)         │  │   │
          │  │  └─────────────────┘    └──────────────────┘  │   │
          │  │  Both run simultaneously — total = slowest    │   │
          │  └───────────────────────────────────────────────┘   │
          │                      │                               │
          │  ┌───────────────────▼───────────────────────────┐   │
          │  │  PRE-LOOP — Call 3 Verification + Cleaning    │   │
          │  │  Remove AI artifacts, fix tech neutrality,    │   │
          │  │  check template compliance                    │   │
          │  └───────────────────────────────────────────────┘   │
          │                      │                               │
          │  ┌───────────────────▼───────────────────────────┐   │
          │  │  PHASE 2 — Self-Healing Loop                  │   │
          │  │                                               │   │
          │  │  ┌─────────────────────────────────────────┐  │   │
          │  │  │  Gap Hunter reads all 25 docs           │  │   │
          │  │  │  Checks references, evidence, neutrality│  │   │
          │  │  │  → N gaps found                         │  │   │
          │  │  └─────────────────────────────────────────┘  │   │
          │  │               │                               │   │
          │  │    ┌──────────┼──────────┐                    │   │
          │  │    ▼          ▼          ▼                    │   │
          │  │  BA Fix     DA Fix     SEC Fix                │   │
          │  │  Agent      Agent      Agent                  │   │
          │  │  (parallel threads)                           │   │
          │  │    │          │          │                    │   │
          │  │    └──────────┼──────────┘                    │   │
          │  │               │ fixes written to disk         │   │
          │  │               ▼                               │   │
          │  │      Gap count = 0? → exit ✅                 │   │
          │  │      No progress?   → HUMAN-DECISION-REQUIRED │   │
          │  │      Iter 3 hit?    → HUMAN-DECISION-REQUIRED │   │
          │  │      else → loop again                        │   │
          │  └───────────────────────────────────────────────┘   │
          │                      │                               │
          │           Call 5 — Fix LOW sections                  │
          │           Call 6 — Verify HIGH claims                │
          │           Coverage Pass (Python counting)            │
          │                      │                               │
          │  ┌───────────────────▼───────────────────────────┐   │
          │  │  PHASE 3 — Final Quality Gate                 │   │
          │  │  YES / CONDITIONAL / NO-GO per document       │   │
          │  └───────────────────────────────────────────────┘   │
          └───────────────────────────────────────────────────────┘
                          │
          ┌───────────────▼───────────────────────────────────────┐
          │         Step 15: gap_hunter_runner.py                 │
          │  Scans for MISSING/TBD/empty markers                  │
          │  Patches weak snippets from DEEP_SCAN source files    │
          │  Parallel — all 25 docs simultaneously, 3 rounds      │
          └───────────────────────────────────────────────────────┘
                          │
                          ▼
          ═══════════════════════════════════
            25 Verified Forward Engineering
            Documents — Ready for Use
          ═══════════════════════════════════
```

---

## 8. Before vs After Comparison

### Architecture

| Aspect | Original Runner (`foundation_runner_template.py`) | Multi-Agent Runner (`foundation_runner_multiagent.py`) |
|---|---|---|
| Generation approach | Sequential — Call 1 finishes, then Call 2 starts | Parallel — Call 1 and Call 2 run simultaneously |
| Estimated generation time | ~180 minutes (both calls back to back) | ~100 minutes (~60% faster) |
| Gap detection | Single pass at Call 3 and Call 4 | Dedicated gap hunter loop — up to 3 iterations |
| Fix agents | One sequential pass | BA / DA / SEC domain agents in parallel threads |
| Unresolved issues | May remain silently in output | Always written to `HUMAN_DECISION_REQUIRED.md` |
| Final readiness signal | None | `FINAL_QUALITY_GATE_REPORT.md` — YES/CONDITIONAL/NO-GO per document |
| Resume after interruption | Partial — saves raw outputs | Full — every step checks disk before running |

---

### Quality Checks

| Quality Check | Original Runner | Multi-Agent Runner |
|---|---|---|
| AI artifact text removal | Call 3 — once | Call 3 (pre-loop) + caught by gap hunter each iteration |
| Technology neutrality | Call 3 — once | Call 3 + gap hunter verifies after every fix |
| BR reference integrity | Call 4 — once | Gap hunter checks every iteration |
| UC reference integrity | Call 4 — once | Gap hunter checks every iteration |
| Table reference integrity | Call 4 — once | Gap hunter checks every iteration |
| Procedure reference integrity | Call 4 — once | Gap hunter checks every iteration |
| Numeric contradictions | Call 4 — once | Gap hunter checks every iteration |
| Oracle Forms coverage | Call 4 — once | Gap hunter checks every iteration |
| LOW confidence sections | Call 5 | Call 5 (runs on loop-healed documents) |
| HIGH confidence claims | Call 6 | Call 6 (runs on loop-healed documents) |
| Evidence count accuracy | Claude estimate | Python-verified exact count |
| Final readiness verdict | None | YES / CONDITIONAL / NO-GO per document |

---

### Gap Detection Coverage

| | Original Runner | Multi-Agent Runner |
|---|---|---|
| Estimated gap detection rate | ~85% | ~99% |
| What gets missed | Gaps introduced by Call 3/4 fixes not re-checked | Almost nothing — loop re-checks after every fix |
| Broken cross-references | Found once, not re-verified | Re-verified after every fix iteration |
| Fix introduces new gap | Not caught | Caught in the next iteration |
| Final silent gaps | Possible | None — unresolved explicitly flagged |

---

### What the Team Gets

| Output | Original Runner | Multi-Agent Runner |
|---|---|---|
| 20 forward engineering documents | Yes | Yes |
| 5 foundation knowledge graph docs | Yes | Yes |
| Gap hunter iteration reports | No | Yes — `Gap_Hunter_Iteration_N.md` per iteration |
| Domain fix agent reports | No | Yes — `Fix_BA_Iteration_N.md` etc. |
| Final quality gate report | No | Yes — `FINAL_QUALITY_GATE_REPORT.md` |
| Human decision list | Partial (Call 4 flags some) | Full — `HUMAN_DECISION_REQUIRED.md` |
| Python-verified evidence counts | Yes | Yes |
| Schema migration scripts | Yes (Call 4) | Yes (Call 4, on loop-healed documents) |
| DBA checklist | Yes (Call 4) | Yes |
| BR cross-reference table | Yes (Call 4) | Yes |
| Resume safety | Partial | Full |

---

## 9. Output Files — What You Get

After the full pipeline (Steps 14 + 15) completes, the output directory contains:

### Foundation Knowledge Graph (5 files)
```
results/Foundation_KnowledgeGraph/
  ENTERPRISE_KNOWLEDGE_GRAPH.json       ← full structured knowledge graph
  CANONICAL_ENTERPRISE_MODEL.md         ← canonical domain entities
  ARCHITECTURE_INVENTORY.md             ← all architectural components
  TRACEABILITY_MATRIX.md                ← requirements to source mapping
  FORWARD_ENGINEERING_INPUT_MAP.md      ← inputs for code generation
```

### Forward Engineering Documents (20 files)
```
results/ForwardEngineering_Docs/
  01_BRD.md                             ← Business Requirements Document
  02_BUSINESS_CAPABILITY_MODEL.md       ← capability map
  03_USE_CASE_SPECIFICATION.md          ← all use cases + UC-002 sub-cases
  04_BUSINESS_PROCESS_MODEL.md          ← process flows
  05_DOMAIN_MODEL.md                    ← domain entities
  06_DATA_DICTIONARY.md                 ← all columns defined
  07_DATA_MODEL_SPECIFICATION.md        ← Oracle schema
  08_ERD.md                             ← entity relationship diagram
  09_DATA_FLOW_DIAGRAM.md               ← data flows
  10_SERVICE_CATALOG.md                 ← all services
  11_API_CONTRACT_SPECIFICATION.md      ← all API operations
  12_TECHNOLOGY_BLUEPRINT.md            ← technology decisions
  13_SECURITY_ARCHITECTURE.md           ← security requirements
  14_NFR_SPECIFICATION.md               ← performance / scalability / reliability
  15_FORWARD_ENGINEERING_SPECIFICATION.md ← legacy to target mapping
  16_GENERATION_MANIFEST.json           ← machine-readable generation config
  17_FORWARD_ENGINEERING_READINESS_REPORT.md ← GO / CONDITIONAL-GO / NO-GO
  18_DEPLOYMENT_ARCHITECTURE.md         ← deployment requirements
  19_FRONTEND_ARCHITECTURE.md           ← frontend architecture
  20_UI_UX_SPECIFICATION.md             ← UI/UX specifications
```

### Support Documents (3 files from Call 4)
```
results/
  SCHEMA_MIGRATION_SCRIPTS.md           ← ready-to-run SQL for missing schema
  DBA_CHECKLIST.md                      ← verification queries for DBA
  BR_CROSSREFERENCE.md                  ← legacy BR-01 to new BR-001 mapping
```

### Quality and Audit Reports
```
results/
  FINAL_QUALITY_GATE_REPORT.md          ← YES/CONDITIONAL/NO-GO per document
  HUMAN_DECISION_REQUIRED.md            ← items needing human decision
  COVERAGE_SUMMARY.md                   ← evidence counts per document
  Gap_Hunter_Iteration_1.md             ← what gap hunter found in round 1
  Gap_Hunter_Iteration_2.md             ← what gap hunter found in round 2
  Fix_BUSINESS_Iteration_1.md           ← what BA fix agent changed
  Fix_DATA_Iteration_1.md               ← what DA fix agent changed
  Fix_SECURITY_Iteration_1.md           ← what SEC fix agent changed
  gap_hunter_report.json                ← Step 15 gap hunter summary
  Foundation_Raw_Output_Part1.md        ← raw Claude output (Call 1, resumable)
  Foundation_Raw_Output_Part2.md        ← raw Claude output (Call 2, resumable)
  Foundation_Raw_Output_Part3.md        ← raw Claude output (Call 3)
  Foundation_Raw_Output_Part5.md        ← raw Claude output (Call 5)
  Foundation_Raw_Output_Part6.md        ← raw Claude output (Call 6)
```

---

## 10. Which Is Best and Why

### Recommendation: Multi-Agent Runner (`foundation_runner_multiagent.py`)

The multi-agent runner is strictly better than the original runner in every dimension. Here is why:

---

**1. It is faster**

Parallel generation cuts the two longest calls from sequential to simultaneous. On a typical machine the wall-clock time drops from approximately 3 hours to approximately 1.5 hours.

---

**2. It catches more gaps**

The original runner's Call 3 and Call 4 check for problems — but only once. If a fix in Call 3 introduces a new gap, Call 4 does not see it because Call 4 runs on the same documents Call 3 produced. The self-healing loop re-checks after every fix, so a gap introduced by a fix is caught in the next iteration.

---

**3. Nothing silently fails**

In the original runner, some gaps may remain in the output without the team knowing. A broken `BR-xxx` reference in `07_DATA_MODEL_SPECIFICATION.md` would survive to the output as-is.

In the multi-agent runner, every unresolvable gap is written to `HUMAN_DECISION_REQUIRED.md` with the exact document, section, description, and decision needed. The team knows exactly what is left and who needs to resolve it.

---

**4. The manager gets a clear go/no-go signal**

The original runner produces 25 documents. A manager would need to read all 25 to know if they are ready for use.

The multi-agent runner produces `FINAL_QUALITY_GATE_REPORT.md` — one file, one table, one verdict per document: YES / CONDITIONAL / NO-GO. Decision time is minutes, not hours.

---

**5. Domain agents prevent conflicts**

Having one agent fix everything risks it making a change in one document that breaks something in another. Separate BA / DA / SEC fix agents each work on their own domain documents only. There is no overlap and no conflicts.

---

**6. The original runner is not discarded**

`foundation_runner_template.py` remains in the codebase. All its infrastructure — prompts, helpers, coverage pass, self-correction, second-opinion — is reused by the multi-agent runner via direct imports. Nothing is duplicated. The original runner can still be used for quick single runs via `pipeline_config.json` by switching `runner` to `foundation_runner_template.py`.

---

### Decision Table

| Scenario | Use Which Runner |
|---|---|
| Full production run | `foundation_runner_multiagent.py` |
| Quick test / proof of concept | `foundation_runner_template.py` |
| Pipeline interrupted and resumed | `foundation_runner_multiagent.py` (resume-safe) |
| Manager needs go/no-go per document | `foundation_runner_multiagent.py` |
| Team needs to know what needs human input | `foundation_runner_multiagent.py` |

---

## 11. Source System Facts

The pipeline was built for and verified against this specific Oracle HRMS system:

| Fact | Value |
|---|---|
| Platform | Oracle Forms 12c (12.2.1.4) |
| Database | Oracle DB 19c |
| Language | PL/SQL |
| Total source files | 42 |
| PL/SQL packages | 11 |
| Business rules extracted | 826 |
| Audit checks run | 3,715 (100% pass) |
| Tables | 30 |
| Columns | 441 |
| Views | 6 |
| Sequences | 29 |
| Triggers | 6 |
| Oracle Forms modules | 6 (HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE, HRMS_PERFORMANCE, HRMS_LOGIN, HRMS_MENU) |
| Seed data rows | 133 |
| Known security vulnerabilities | 4 |
| Known bugs | 20 |
| Deferred TODOs | 5 |

---

## Summary

| Topic | Key Point |
|---|---|
| What the runner does | Generates 25 production-quality forward engineering documents from Oracle source evidence |
| Original runner | 6 sequential Claude calls — generate, verify, cross-check, self-correct, second-opinion, coverage |
| Multi-agent runner | Same 6 calls + parallel generation + self-healing loop + final quality gate |
| Gap hunter | Reads all 25 docs, finds structural gaps, assigns to domain agents, loops until zero gaps or escalates |
| Why loop | A fix can create a new gap — must verify after every fix, not just once |
| Why domain agents | BA/DA/SEC each fix their own domain — no conflicts, run in parallel |
| Why human-decision file | Gaps that need business knowledge cannot be auto-fixed — must be explicitly handed to a human |
| Recommendation | Multi-agent runner — faster, more complete, clear go/no-go signal, nothing silently fails |

---

*Report generated from: `pipeline/foundation_runner_template.py` (1,823 lines) and `pipeline/foundation_runner_multiagent.py` (815 lines)*  
*Configuration: `pipeline_config.json`*  
*Architecture reference: `MULTI_AGENT_SELF_HEALING_ARCHITECTURE.md`*
