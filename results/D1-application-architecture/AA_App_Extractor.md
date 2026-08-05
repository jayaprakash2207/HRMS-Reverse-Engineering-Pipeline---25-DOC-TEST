# AA_App_Extractor.md — Application Architecture Extraction Agent Log
**Agent:** AA Agent 1 — Application Architecture Extractor
**System:** Oracle HRMS v4.2 (Build 2024.03.15)
**Extraction Date:** 2026-08-04
**Status:** COMPLETE

---

## Agent Mission

Extract a complete, production-grade application architecture picture of Oracle HRMS v4.2 from the following provided source artifacts — without modifying any source code, without inventing facts, and marking all unknowns explicitly.

**Input artifacts analyzed:**
- Layer 1 JSON summary (system metadata)
- 4 DDL scripts (tables, sequences, views)
- 2 trigger files (6 triggers total)
- 11 PL/SQL package specs (.pks) and 11 bodies (.pkb)
- 2 Oracle Forms PL/SQL libraries (.pll)
- 1 Oracle Forms menu module (.mmb)
- 6 Oracle Forms XML exports (.fmb → XML)

**Output root:** `results/D1-application-architecture/`

---

## Extraction Methodology

### Step 1 — System Boundary Identification
Identified the system perimeter from the Layer 1 JSON and HRMS_MENU.xml version string. Confirmed: single Oracle schema monolith with 4 external integration points.

### Step 2 — Component Inventory
Enumerated all named components: 11 packages, 6 forms, 2 libraries, 1 menu, 22 tables, 6 views, 6 triggers, 30 sequences. Classified each by type, layer, and domain module.

### Step 3 — Dependency Mapping
Traced all cross-package call references in package bodies. Identified the PKG_EMPLOYEE ↔ PKG_PAYROLL circular dependency explicitly. Mapped form-to-package call relationships from form trigger code. Identified external dependencies: UTL_FILE (4 directory objects), UTL_SMTP, DBMS_CRYPTO, DBMS_SCHEDULER (implied).

### Step 4 — Call Flow Reconstruction
Reconstructed 6 key end-to-end flows by tracing form trigger handlers through package call chains to DB DML and external I/O.

### Step 5 — Pattern Analysis
Identified primary architecture style (N-Tier Oracle Forms Monolith), secondary patterns (Anemic Domain Model, soft-delete, AUTONOMOUS_TRANSACTION audit, async notification queue), and anti-patterns.

### Step 6 — Violation and Risk Registration
Catalogued 23 architectural violations (5 CRITICAL, 7 HIGH, 7 MEDIUM, 4 LOW) and 12 risks (3 CRITICAL, 7 HIGH, 2 MEDIUM), each with explicit source evidence and remediation guidance.

### Step 7 — Strangler Candidate Ranking
Ranked all 10 modules by coupling score, data encapsulation quality, feature completeness, and business value to produce a migration sequence recommendation.

### Step 8 — Forward Engineering Input
Produced per-module modernization guidance covering target architecture patterns, data migration considerations, and API surface design.

### Step 9 — Open Questions
Catalogued 30+ questions that cannot be resolved from source alone, grouped by: missing forms, missing DB objects, deployment topology, scheduler jobs, integration details, data quality, and business context.

### Step 10 — Diagram Generation
Produced 5 Mermaid/C4 diagrams: system context, container view, component view, full dependency graph (with circular dep highlighted), and call-flow sequence diagram.

---

## Hallucination Control Attestation

I attest that every finding in every output file satisfies the following:

| Rule | Compliance |
|---|---|
| Every architectural claim has a named source file as evidence | COMPLIANT |
| No module ownership was invented | COMPLIANT |
| No deployment topology was guessed | COMPLIANT — marked "unknown" throughout |
| No API behaviour was fabricated | COMPLIANT |
| No business rule was invented | COMPLIANT — only rules explicitly stated in code |
| No security detail was invented | COMPLIANT — all security findings cite exact package/line |
| Unknown USER_CREDENTIALS table structure | COMPLIANT — marked unknown, not guessed |
| Missing HRMS_ADMIN.fmb and HRMS_REPORTS.fmb | COMPLIANT — marked missing, not invented |
| Scheduler job details | COMPLIANT — inferred existence from comments only; definition marked unknown |
| No legacy source code was modified | COMPLIANT |

---

## Output File Manifest

| File | Lines (approx) | Status |
|---|---|---|
| system-inventory.json | 125 | COMPLETE |
| module-boundary-map.json | 422 | COMPLETE |
| component-registry.json | 610 | COMPLETE |
| application-interface-catalogue.json | 336 | COMPLETE |
| dependency-graph.json | 99 | COMPLETE |
| call-flow-map.json | 200 | COMPLETE |
| architecture-pattern-report.md | 180 | COMPLETE |
| architecture-violation-register.json | 380 | COMPLETE |
| application-risk-register.json | 230 | COMPLETE |
| strangler-candidate-report.md | 200 | COMPLETE |
| forward-engineering-input-map.md | 250 | COMPLETE |
| open-questions.md | 180 | COMPLETE |
| extraction-audit.md | 130 | COMPLETE |
| application-architecture-summary.md | 200 | COMPLETE |
| diagrams/system-context.mmd | 25 | COMPLETE |
| diagrams/container-view.mmd | 25 | COMPLETE |
| diagrams/component-view.mmd | 45 | COMPLETE |
| diagrams/dependency-view.mmd | 75 | COMPLETE |
| diagrams/call-flow-view.mmd | 65 | COMPLETE |
| AA_App_Extractor.md | (this file) | COMPLETE |

---

## Key Findings Summary for Downstream Agents

**For DA Agent (Data Architecture):**
- Single schema HRMS; 22 tables; soft-delete on EMPLOYEES; virtual computed column on LEAVE_BALANCES
- SSN stored as AES-256-CBC encrypted blob with HARD-CODED KEY — key must be rotated before data migration
- YTD fields in PAYROLL_DETAILS are always 0 — historical YTD must be reconstructed from line-item sums
- USER_CREDENTIALS table structure unknown — DDL not provided

**For TA Agent (Technology Architecture):**
- Oracle Forms 12c (12.2.1.4) — Forms Server version and OS unknown
- Oracle DB version unknown
- 4 Oracle Directory objects on OS filesystem — paths unknown
- SMTP: smtp.internal.company.com:25 (plaintext)
- No Oracle Net encryption status known
- DBMS_SCHEDULER jobs not in source — must be recovered from production

**For Security Deep-Dive Agent:**
- 5 CRITICAL security violations requiring immediate remediation before any migration
- Authentication is effectively non-functional (any password accepted)
- SSN encryption key in plaintext source
- SQL injection attack surface in employee search

**For BRD / Business Rules Agent:**
- Fiscal year starts October 1 (confirmed in PKG_COMMON.get_fiscal_year)
- 2024 US tax law embedded: SS wage base $168,600 @ 6.2%; Medicare 1.45% + 0.9% > $200k; standard deductions $14,600 single / $29,200 MFJ
- Soft-delete enforced by trigger — no physical employee deletes allowed
- Leave overlap detection has a known half-day bug
- Leave carryover expiry has a known double-expiry bug
- Change password validation implemented but credential update not persisted
