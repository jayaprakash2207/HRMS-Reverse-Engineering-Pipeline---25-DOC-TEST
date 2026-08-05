# Forward Engineering Input Map
**System:** Acme Corporation HRMS (Oracle 19c → Target Platform TBD)
**Document Version:** 1.0 — Compiled from BA, DA, TA, AA, and Cross-Validation Tracks
**Compiled By:** Solution Architect — Multi-Track Synthesis
**Date:** 2026-08-05
**Status:** DRAFT — Pending human review of all Open Questions before code generation

---

## Table of Contents

1. [Analysis Output → Deliverable Mapping](#1-analysis-output--deliverable-mapping)
2. [Source of Truth Declarations](#2-source-of-truth-declarations)
3. [Contradiction Resolution Log](#3-contradiction-resolution-log)
4. [Confidence Levels per Domain](#4-confidence-levels-per-domain)
5. [Assumptions Made](#5-assumptions-made)
6. [Open Questions Requiring Human Review](#6-open-questions-requiring-human-review)
7. [Data Quality Assessment](#7-data-quality-assessment)
8. [Recommended Enrichment Actions](#8-recommended-enrichment-actions)

---

## 1. Analysis Output → Deliverable Mapping

This table maps every analysis output artefact produced across all four tracks (BA, DA, TA, AA) and the cross-validation supplement to the specific forward engineering deliverable(s) it feeds. Each row includes a confidence rating for the mapping.

### 1.1 Business Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| `BA_Deep_Analyst.md` (BR-01–BR-107, Pass 1) | 107 core business rules covering payroll, leave, performance, security, notifications | BRD (Business Requirements Document); Use Case Specifications; Domain Model; Business Rules Engine specification | HIGH |
| `BA_Deep_Analyst.md` (BR-108–BR-140, Pass 2 — Edge Cases) | 33 edge-case business rules including concurrent access, boundary conditions, exception flows | BRD addendum; Test Case Specification; NFR Specification (error handling) | HIGH |
| `BA_Deep_Analyst.md` — Discrepancy Log (DISC-001–DISC-009) | 9 data discrepancies across tracks, including payroll PAID status orphaning (DISC-009) | Gap Analysis Report; Data Migration Specification; BRD open issues | HIGH |
| `BA_Deep_Analyst_Edge.md` — EMPLOYEE_DEPENDENTS supplement | 10 business rules (BR-DEP-01–10), pain points, automation opportunities, validation queue | API Contract for dependents management; Data Model (EMPLOYEE_DEPENDENTS entity); Benefits feed integration spec | HIGH |
| `BA_Deep_Analyst_Edge.md` — PKG_INTEGRATION.sync_org_structure supplement | 5 business rules (BR-ORG-01–05) — stub procedure, false success log | Integration Architecture Specification; Operational Runbook (DO NOT SCHEDULE); NFR Spec | HIGH |
| `BA_Deep_Analyst_Edge.md` — EMPLOYEE_BANK_ACCOUNTS supplement | 12 business rules (BR-BA-01–12), ACH/NACHA gap analysis | Payroll Disbursement API Spec; ACH Integration Design; Data Model | HIGH |
| `BA_Deep_Analyst_Edge.md` — PKG_EMPLOYEE.terminate_employee TODOs | 9 business rules (BR-TERM-01–09), COBRA gap, access revocation, final pay | Termination Workflow Specification; Compliance Checklist (COBRA); Off-boarding API Design | HIGH |
| `BA_Deep_Analyst_Edge.md` — PERFORMANCE_REVIEWS calibration gap | Calibration workflow completely absent from code; CALIBRATED_RATING dead column | Performance Management Specification; Calibration Session UI Design; Reporting Correction | HIGH |
| `BA_Deep_Analyst_Edge.md` — PKG_LEAVE.initialize_balances supplement | 10 business rules (BR-LIB-01–10), accrual retry defect (BR-LIB-05) | Leave Accrual Engine Specification; Defect Fix Specification (critical) | HIGH |
| `BA_Deep_Analyst_Edge.md` — Pass 2 Edge Case Summary | Grouped table of all 33 edge rules by theme, top-5 severity findings | BRD Appendix; Risk Register input | HIGH |

### 1.2 Data Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| `DA_Data_Reviewer.md` (Passes 1–3, RC-001–RC-011) | 35 total corrections: 22 corrected / 8 added / 5 enriched across three review passes | Data Dictionary (authoritative); ERD; Data Migration Specification | HIGH |
| `da-outputs/review-summary.md` | Gate G1 open questions (G1-01–G1-10), quality score progression, pass-by-pass change totals | Forward Engineering Readiness Report; Human Review Checklist | HIGH |
| `da-outputs/data-dictionary.md` | Full column inventory for all 30 confirmed DDL tables, 6 views, inferred tables | Data Dictionary deliverable (06_DATA_DICTIONARY); ERD input; API Contract data shapes | HIGH |
| `da-outputs/schema-catalogue.json` | Structured JSON: all tables, constraints, FK relationships, inferred tables (38 total) | ERD (08_ERD); Data Model Specification (07); Technology Blueprint DB schema section | HIGH |
| `da-outputs/hidden-business-rules.json` | BR-041–BR-046: security rules, stub rules, missing constraints (44 total rules) | BRD supplement; Security Architecture Specification; Test Case Specification | HIGH |
| `da-outputs/data-quality-report.md` | DQ-001–DQ-032: 32 data quality findings including 9 HIGH severity | Data Migration Specification (pre-conditions); NFR Specification; Defect Register | HIGH |
| `da-outputs/pii-inventory.json` | PII classification for all columns including RPT_* inferred tables | Privacy Impact Assessment; Security Architecture; Encryption Specification | HIGH |
| `da-outputs/access-control-matrix.md` | RBAC rules, grade-based access, PKG_SECURITY gaps, RPT_* table-level access | Authorization Specification; API Security Design; RBAC Implementation Guide | HIGH |
| `da-outputs/storage-pattern-analysis.md` | Soft-delete pattern, audit column pattern, denormalized RPT_* layer (§9) | Data Model Specification; Migration Strategy; Archival Policy | MEDIUM |
| `da-outputs/data-flow-map.md` | 14 sections covering all data flows including stub flows (§13 on-demand, §14 nightly) | Data Flow Diagram (09_DFD); Integration Architecture Specification | HIGH |
| `da-outputs/data-source-inventory.json` | DS-01–DS-10, Gate G1 questions G1-NEW-01–03, RPT_* data source | Technology Blueprint; Integration Inventory | MEDIUM |
| `da-outputs/migration-complexity.json` | MC-01, MC-02b (Oracle MEDIAN() no direct equivalent) | Technology Blueprint; Migration Risk Register; Target Platform Selection | HIGH |
| `da-outputs/USER_CREDENTIALS` supplement | DQ-029–030, BR-043b, BR-044–045 — auth stub, password bypass, dead exceptions | Security Architecture Specification; Authentication API Design | HIGH |
| `da-outputs/TIME_ATTENDANCE_RECORDS` supplement | DQ-031, BR-046 — stub import, false audit trail, no DDL | Integration Design (Time & Attendance); Gap Report | HIGH |
| `da-outputs/RPT_*` supplements | DQ-032, BR-043–045 (RPT_* context), CALENDAR_YEAR projection gap | Reporting Specification; BI Architecture Design; Data Warehouse Design | MEDIUM |

### 1.3 Technology Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| TA output — TD-01–TD-36 (Critical/High items) | Hard-coded AES key, cleartext FTP credentials, SQL injection vectors, auth stub | Security Architecture Specification; Penetration Test Checklist; Remediation Roadmap | HIGH |
| TA output — TD-37–TD-57 (Medium items) | Audit log mixing, EEO constraint gap, salary validation soft-check | NFR Specification; Data Model corrections; Operational Runbook | HIGH |
| TA output — TD-58–TD-81 (Medium/Low edge cases) | Oracle Forms LOV gap (TD-72), ADP no-validation (TD-73), GL feed gaps (TD-79–80), portal auth (TD-81) | Integration Contract Specification; Forms Migration Specification; Operational Runbook | HIGH |
| TA output — CI/CD Pipeline Maturity Assessment | 0 of 14 capabilities present; 6 Critical gaps (build, test, SAST, secret scan, deploy, rollback) | DevOps Architecture Specification; CI/CD Pipeline Design; Technology Blueprint | HIGH |
| TA output — Observability Coverage Assessment | No structured logging, no correlation ID, no distributed tracing | NFR Specification (observability); Technology Blueprint; Operations Design | HIGH |
| TA output — Forms compilation gap (TD-76) | No build script for Oracle Forms .fmb → .fmx | Build System Specification; Technology Blueprint | MEDIUM |
| TA output — FMLA REQUIRES_DOCUMENT='N' (TD-71) | FMLA seed data allows undocumented leave — compliance risk | Configuration Management Specification; Compliance Checklist | HIGH |
| TA output — Session stale cleanup gap (TD-75) | No DBMS_SCHEDULER sweep for expired USER_SESSIONS | Operational Architecture Specification; Scheduled Job Design | HIGH |

### 1.4 Application Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| `quality-review.md` (QR-001–QR-033, Passes 1–3) | 33 quality findings including architecture violations, risk items, component boundary issues | Architecture Violation Register (input); Forward Engineering Specification (15_FES) | HIGH |
| `final-sanity-check.md` (§11 Pass 3) | 8 edge-case findings marked [EDGE-CASE-FOUND] | Forward Engineering Readiness Report; Risk Register | HIGH |
| `executive-summary-for-review.md` | Multi-pass summary, overall verdict PARTIAL | Forward Engineering Readiness Report (17_FERR); Stakeholder Briefing | HIGH |
| `architecture-violation-register.json` (AV-001–AV-025) | 25 violations including AV-024 (direct deposit unimplemented) and AV-025 (encryption path missing) | Architecture Specification; Remediation Roadmap; NFR Specification | HIGH |
| `application-risk-register.json` (RISK-001–RISK-014) | 14 risks, 9 HIGH severity including ACH missing and bank account decryption unknown | Risk Register; Forward Engineering Readiness Report; Project Charter input | HIGH |
| `component-registry.json` | All major components (COMP-001–COMP-N), risk flags per component | Component Architecture Diagram; Technology Blueprint | HIGH |
| `module-boundary-map.json` (MOD-001–MOD-N) | Module boundaries, open questions for EMPLOYEE_BANK_ACCOUNTS | Bounded Context Map; API Contract boundaries | MEDIUM |
| `extraction-audit.md` | Coverage matrix, violation counts | Forward Engineering Readiness Report; Audit Trail | MEDIUM |
| `forward-engineering-input-map.md` | Early draft with payroll section, bank accounts critical migration requirements | This document (supersedes early draft) | HIGH |

### 1.5 Cross-Validation Supplement Outputs

| Supplement | Tracks Reconciled | Key Finding | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|---|
| EMPLOYEE_DEPENDENTS (BA↔DA, DA↔AA) | BA, DA, AA | BENEFITS_ENROLLED never read; dependent SSN decrypt path missing; termination doesn't touch dependents | Benefits Integration Spec; Termination Workflow; Data Model | HIGH |
| PKG_INTEGRATION.sync_org_structure (BA supplement) | BA | Entire procedure is placeholder — logs false success | Integration Spec (exclude/flag); Operational Runbook | HIGH |
| EMPLOYEE_BANK_ACCOUNTS (BA↔AA, DA↔AA) | BA, DA, AA | Table completely unused — direct deposit non-functional | ACH Disbursement Design; Critical Gap Report | HIGH |
| PKG_EMPLOYEE.terminate_employee TODOs (BA supplement) | BA | COBRA gap, access revocation partial, calculate_final_pay does not exist | Termination API Design; Compliance Specification | HIGH |
| PERFORMANCE_REVIEWS calibration (BA supplement) | BA, DA | CALIBRATED_RATING dead column; reporting reads wrong column (pre-calibration) | Performance Specification; Reporting Correction | HIGH |
| PKG_LEAVE.initialize_balances (BA supplement) | BA | Accrual retry defect: assignment vs. increment bug | Leave Engine Defect Fix; Test Case | HIGH |
| USER_CREDENTIALS (DA supplement, two passes) | BA, DA | Auth stub (BR-042) — any valid username authenticates regardless of password; MD5; change_password never verifies old password | Security Architecture; Authentication API; Critical Security Remediation | HIGH |
| RPT_* tables (DA supplement) | BA, DA | refresh_reporting_tables is pure stub; all reports query OLTP directly; CALENDAR_YEAR missing from leave utilization cursor | Reporting Architecture; BI Design; Data Warehouse Spec | MEDIUM |
| TIME_ATTENDANCE_RECORDS (AA→DA) | AA, DA | No DDL for import target; stub logs false success | Integration Design; Time & Attendance Module Spec | HIGH |
| RPT_HEADCOUNT / RPT_COMPENSATION / RPT_LEAVE_UTIL (BA→DA) | BA, DA | Oracle MEDIAN() migration issue (MC-02b); non-standard turnover denominator | Technology Blueprint; Migration Risk | MEDIUM |

---

## 2. Source of Truth Declarations

The following table declares, for each major topic, which single document is the authoritative source for forward engineering. All conflicting information in other documents must defer to the declared source of truth.

| Topic | Source of Truth Document | Rationale | Override Condition |
|---|---|---|---|
| Business rules (functional) — BR-01–BR-107 | `BA_Deep_Analyst.md` Pass 1 | First-pass analysis with direct code evidence citations; unchanged in all subsequent passes | None — authoritative |
| Business rules (edge cases) — BR-108–BR-140 | `BA_Deep_Analyst.md` Pass 2 section | Dedicated edge-case pass with [EDGE-CASE-FOUND] markers; additive to Pass 1 | None — authoritative |
| Database schema — table definitions, constraints | `da-outputs/schema-catalogue.json` | Most granular, structured representation with FK graph; reviewed through three DA passes | DDL source files if direct schema conflict arises |
| Column-level business meaning | `da-outputs/data-dictionary.md` | Three-pass reviewed; covers all 30 confirmed tables, 6 views, and inferred tables | Supersedes any earlier BRD column descriptions |
| PII classification | `da-outputs/pii-inventory.json` | Explicit PII flags per column including RPT_* inferred table exposure; consistent with GDPR/CCPA framing | Legal review may reclassify |
| Security business rules | `da-outputs/hidden-business-rules.json` (BR-041–046) + TA critical findings | DA track captured security rules from code inspection; TA confirmed and extended | Penetration test findings supersede theoretical analysis |
| RBAC / access control | `da-outputs/access-control-matrix.md` | Derived from PKG_SECURITY code; grade-based logic confirmed in both BA and DA tracks | Any new role definition from business must be added here |
| Data quality defects | `da-outputs/data-quality-report.md` (DQ-001–DQ-032) | Three-pass reviewed; most current and complete; each finding has severity and corrective recommendation | — |
| Bounded context boundaries | `results/Foundation_KnowledgeGraph/` + Domain Model (05_DOMAIN_MODEL) | Context map derived from package boundaries; confirmed against schema FK clusters | — |
| Architecture violations | `architecture-violation-register.json` (AV-001–AV-025) | AA track systematic; cross-validated with DA and TA findings | — |
| Integration contracts (current state) | `da-outputs/data-flow-map.md` §1–§14 | Most complete integration picture; covers all stubs and real flows explicitly | PKG_INTEGRATION.pkb source if conflict |
| Technology risk items | TA track outputs (TD-01–TD-81) | Systematic two-pass TA analysis; covers CI/CD, observability, configuration, security | — |
| Performance calibration gap | BA_Deep_Analyst_Edge.md calibration supplement | Most complete statement of what is missing and what the implied process should be | — |
| Termination workflow gaps | BA_Deep_Analyst_Edge.md terminate_employee supplement | Most complete gap analysis including COBRA, access revocation, final pay | — |
| Payroll disbursement gap | `BA_Deep_Analyst_Edge.md` EMPLOYEE_BANK_ACCOUNTS supplement + AV-024/AV-025 | Cross-validated: BA rules, AA architecture violations, and DA data quality findings all concur | — |
| EMPLOYEE_DEPENDENTS data rules | BA_Deep_Analyst_Edge.md + AA cross-validation supplement | Full table definition, integration usage, and gap analysis confirmed across three tracks | — |

---

## 3. Contradiction Resolution Log

Each entry records a contradiction found across analysis tracks and the resolution applied for forward engineering purposes.

| Contradiction ID | Topic | Track A Statement | Track B Statement | Resolution | Resolved By |
|---|---|---|---|---|---|
| CONT-001 | EMPLOYEES.BANK_ACCOUNT_NUMBER encryption | DA data-dictionary: `BANK_ACCOUNT_NUMBER VARCHAR2(500)` AES-256 encrypted; decrypt procedure not found | BA track: EMPLOYEE_BANK_ACCOUNTS is a separate table (not a column on EMPLOYEES); all procedures reference the separate table | Both are true: the EMPLOYEES table has a legacy `BANK_ACCOUNT_NUMBER` column AND a separate EMPLOYEE_BANK_ACCOUNTS table exists; the column is residual. Forward engineering: migrate to EMPLOYEE_BANK_ACCOUNTS model; deprecate the EMPLOYEES column | Architecture team judgment; confirmed by DA schema catalogue showing both |
| CONT-002 | Direct deposit functionality | BA track originally described payroll as functional through PAID status | DA track (DQ-009), AA track (AV-024), and EMPLOYEE_BANK_ACCOUNTS supplement all confirm: no procedure reads EMPLOYEE_BANK_ACCOUNTS; PAID status is orphaned | Forward engineering treats direct deposit as **not implemented** — new ACH disbursement module must be designed from scratch; PAID status transition logic must be tied to successful ACH file generation | DA/AA cross-validation concurrence |
| CONT-003 | PKG_SECURITY.authenticate password check | BA track (BR-42): "password is verified against stored hash" — implied | DA track (BR-042/DQ-003): authenticate() never queries USER_CREDENTIALS; any valid username authenticates regardless of password | DA track wins — code inspection is authoritative over implied BA behavior. Forward engineering: authentication module must be completely rewritten | Direct code evidence in PKG_SECURITY.pkb |
| CONT-004 | HRMS_VALIDATION_LIB.validate_salary_range caching | TA track (TD-52): comment in code says "cached" | DA/TA code inspection: body shows live DB query to JOB_GRADES — no caching | Live query is the actual behavior. Forward engineering: no caching assumption; performance NFR must account for per-validation DB round trips | TD-52 code evidence |
| CONT-005 | Performance rating used in payroll (merit) | BA track: OVERALL_RATING ≥ 3 required for merit eligibility | AA/DA calibration supplement: CALIBRATED_RATING column exists but is dead; reporting reads OVERALL_RATING; no calibration step exists | Forward engineering: merit calculation currently uses OVERALL_RATING (the raw manager rating). If calibration workflow is implemented, the merit eligibility rule must be updated to reference CALIBRATED_RATING post-implementation | Architecture team decision required (see OQ-009) |
| CONT-006 | USER_SESSIONS timeout enforcement | TA track (TD-75): session timeout only evaluated on next is_session_valid call — no background sweep | DA track (BR-026): timeout is hard-coded 30 minutes, ignoring SYSTEM_PARAMETERS | Both are true simultaneously. Forward engineering: (a) implement DBMS_SCHEDULER sweep; (b) wire timeout to SYSTEM_PARAMETERS; (c) implement explicit session invalidation on PKG_SECURITY.revoke_access | Composite finding |
| CONT-007 | RPT_* tables and reporting query source | BA track: described a nightly reporting refresh cycle as production behavior | DA/TA inspection: refresh_reporting_tables is a pure stub; all 7 report procedures query OLTP directly; RPT_* tables may never have held data | Forward engineering: treat current reporting as **OLTP-direct only**; RPT_* table design is aspirational. Confirm with DBA whether RPT_* tables exist in production DDL (see OQ-012) | DA code inspection overrides BA description |
| CONT-008 | PKG_INTEGRATION.sync_org_structure scheduling | BA track: procedure exists in integration package | BA supplement: procedure is a complete placeholder — only logs false success; zero actual logic | Forward engineering: **do not schedule** this procedure; the org structure sync capability is entirely unimplemented and logging false success is actively dangerous | BA supplement code inspection |
| CONT-009 | COBRA notification timing | BA supplement (BR-TERM-01): COBRA requires 14-day notification | No implementation exists anywhere | No contradiction — this is a pure gap. Forward engineering: implement COBRA notification as a new capability; 14-day SLA is the target NFR | Regulatory requirement |
| CONT-010 | Password change old-password verification | BA track: assumed change_password validates the old password | DA supplement (DQ-029/BR-044): p_old_password is received but never compared; any authenticated session can replace any credential silently | DA code evidence is authoritative. Forward engineering: implement old-password verification as mandatory step in the new authentication module | Direct code inspection |
| CONT-011 | ADP benefits feed BENEFITS_ENROLLED filter | BA description: benefits feed exports enrolled dependents | AA/DA cross-validation: export_benefits_feed uses LEFT JOIN with d.ACTIVE_FLAG='Y' but does NOT filter on BENEFITS_ENROLLED; all active dependents are exported regardless of enrollment status | DA/AA code inspection is authoritative. Forward engineering: add BENEFITS_ENROLLED='Y' filter unless business confirms all active dependents should always be exported (see OQ-007) | Cross-track code evidence |
| CONT-012 | Turnover report denominator | BA reporting capability description: turnover percentage | DA supplement (BR-044): turnover_report uses hires-up-to-end-date as denominator, not average headcount — non-standard vs SHRM definition | Documented as known non-standard behavior. Forward engineering: the new turnover report should offer both calculation methods; flag denominator choice in UI | DA code inspection |

---

## 4. Confidence Levels per Domain

### 4.1 Confidence Summary Table

| Domain | Confidence Level | Key Evidence Base | Limiting Factors |
|---|---|---|---|
| Employee Master Data | HIGH | Schema confirmed, PKG_EMPLOYEE fully analysed, BA rules 1–30 solid | EMERGENCY_CONTACTS table status unclear |
| Payroll Calculation Engine | HIGH | PKG_PAYROLL.pkb partially recovered; tax brackets confirmed; deduction logic confirmed | Procedure body truncated mid-source; final-pay procedure does not exist |
| Payroll Disbursement (ACH) | LOW | EMPLOYEE_BANK_ACCOUNTS schema confirmed; zero procedure references confirmed | Entire disbursement layer is unimplemented — must be designed net-new |
| Leave Management | HIGH | PKG_LEAVE fully analysed; leave types, accruals, balances confirmed; initialize_balances defect found | Accrual retry defect (BR-LIB-05) needs confirmation of real-world data impact |
| Performance Management | MEDIUM | PKG_PERFORMANCE fully analysed; OVERALL_RATING workflow confirmed | CALIBRATED_RATING entirely unimplemented; calibration business process not defined by business stakeholders |
| Security & Authentication | LOW | PKG_SECURITY analysed; critical auth stub confirmed (BR-042); MD5 confirmed; hardcoded key confirmed | Authentication is fundamentally broken — must be rewritten entirely; no trustworthy baseline |
| Benefits Integration (ADP) | MEDIUM | PKG_INTEGRATION.export_benefits_feed confirmed; ADP 203-char format confirmed | BENEFITS_ENROLLED filter gap unresolved; ADP spec version unknown |
| GL / Oracle Financials Integration | MEDIUM | PKG_INTEGRATION.generate_gl_journal confirmed; pipe-delimited format confirmed | Journal Source/Category values undocumented (TD-79); no GL_FEED_STATUS tracking (TD-80) |
| Org Structure Sync | LOW | PKG_INTEGRATION.sync_org_structure confirmed as complete placeholder | No implementation whatsoever; no LDAP parameters; scope undefined |
| Time & Attendance Import | LOW | PKG_INTEGRATION.import_time_attendance stub confirmed; CSV format partially inferred | No DDL for destination table; no link to PAYROLL_DETAILS; must be designed net-new |
| Reporting Layer | MEDIUM | 7 report procedures confirmed with full SQL; RPT_* inferred column shapes confirmed | RPT_* tables may not exist in production; refresh stub never populates them; CALENDAR_YEAR projection gap |
| Notifications | MEDIUM | PKG_NOTIFICATION confirmed; NOTIFICATION_QUEUE confirmed; template system confirmed | SMS channel declared but handler not implemented; no retry-exhaustion escalation |
| COBRA & Termination Compliance | LOW | Termination procedure analysed; COBRA TODO confirmed; calculate_final_pay confirmed as non-existent | Federal compliance gap on every termination processed; must be designed from scratch |
| Database Schema (structural) | HIGH | Three-pass DA review; 30 tables confirmed DDL; 6 views confirmed; 8 inferred tables documented | USER_CREDENTIALS DDL not recovered (inferred from package references); schema-catalogue.json marks these explicitly |
| Data Quality | HIGH | DQ-001–DQ-032 systematically catalogued; severity and corrective action per finding | RPT_* production DDL unconfirmed |
| CI/CD and DevOps | HIGH | 0 of 14 capabilities — absence is definitively confirmed | No ambiguity; everything is manual |
| Oracle Forms Layer | MEDIUM | XML exports analysed; key LOVs and triggers documented; 81 TA defects catalogued | .fmb source files cannot be compiled without Oracle Forms Builder 12c; no build pipeline |
| PII and Privacy | HIGH | PII inventory complete; encryption pattern confirmed; RPT_* PII exposure documented | Hard-coded AES-256 key means all encrypted data is theoretically compromised |

### 4.2 Detailed Domain Confidence Reasoning

#### Employee Master Data — HIGH
The EMPLOYEES table schema is confirmed through multiple independent sources: DDL in `01_core_tables.sql`, references in PKG_EMPLOYEE, PKG_PAYROLL, PKG_SECURITY, and PKG_LEAVE. The BA rules covering hire, transfer, termination, and grade changes (BR-01–BR-30 range) are consistent with the DA schema. Three cross-track supplements all resolved to consistent findings. The only gap is EMERGENCY_CONTACTS, which the DA schema catalogues but the BA track does not assign business rules to.

#### Payroll Disbursement — LOW
This domain deserves special attention. EMPLOYEE_BANK_ACCOUNTS has a well-designed schema (four DEPOSIT_TYPEs, PRIORITY_ORDER, PRENOTE_SENT) that appears production-ready at the DDL level. However, confirmed by three independent analysis tracks: zero PL/SQL procedures reference this table. The PAID status in PAYROLL_RUNS is orphaned with no downstream action. Forward engineering for this domain is effectively greenfield design, constrained only by the existing schema shape.

#### Security & Authentication — LOW
The confidence rating is LOW not because the analysis is incomplete but because the current system provides almost no trustworthy foundation. The auth stub (BR-042) means the current password field is meaningless. The MD5 hash means stored passwords are trivially reversible. The hardcoded AES key (TD-01) means all encrypted PII is theoretically accessible to anyone who reads the source code. The forward engineering team inherits a security posture that must be treated as compromised.

#### Performance Management — MEDIUM
The rating workflow (create → self-assessment → manager review → acknowledge) is well-documented and consistently confirmed across tracks. Confidence is MEDIUM rather than HIGH solely because of the calibration gap: CALIBRATED_RATING and CALIBRATION_NOTES are schema columns with no implementation and no BA-defined process. The business stakeholder must define whether calibration is required, who owns it, and whether it blocks acknowledgement. Until that decision is made, the complete performance management specification cannot be written.

---

## 5. Assumptions Made

This section distinguishes inferred items (derived from code analysis without explicit business confirmation) from confirmed items (directly evidenced in source).

### 5.1 Schema and Data Model Assumptions

| ID | Assumption | Basis | Risk if Wrong | Validation Required |
|---|---|---|---|---|
| ASM-001 | USER_CREDENTIALS table exists in production with columns EMP_ID, PASSWORD_HASH, and audit columns | Inferred from PKG_SECURITY.pkb package references; DDL not recovered | Schema migration would miss this table; data loss on migration | DBA must confirm DDL |
| ASM-002 | EMPLOYEE_BANK_ACCOUNTS is the intended single source of truth for direct deposit; the EMPLOYEES.BANK_ACCOUNT_NUMBER column is a legacy artifact to be deprecated | Inferred from EMPLOYEE_BANK_ACCOUNTS design quality vs. EMPLOYEES residual column | If both are in active use by an unreviewed form, two data sources must be reconciled | Confirm with HR team which forms populate bank data |
| ASM-003 | RPT_* tables (7 inferred) may not exist in the production database; they are aspirational based on the stub refresh procedure | refresh_reporting_tables body has zero DML; no confirming DDL found | If RPT_* tables do exist and hold stale data, migration may need to handle them | DBA must confirm via `SELECT table_name FROM user_tables WHERE table_name LIKE 'RPT_%'` |
| ASM-004 | SEQUENCE objects (SQ_EMPLOYEE_ID and equivalents) exist for all PK columns | Standard Oracle pattern; PKG_EMPLOYEE references sequence usage | If sequences are missing or at wrong NEXTVAL, PK collision on migration | DBA must confirm all sequences exist and current values |
| ASM-005 | TIME_ATTENDANCE_RECORDS does not exist as a physical table | No DDL found; import stub only implies the table via CSV column comment | If the table does exist in production with data, it must be migrated | DBA must confirm via `SELECT table_name FROM user_tables WHERE table_name = 'TIME_ATTENDANCE_RECORDS'` |
| ASM-006 | EMERGENCY_CONTACTS data is stored in EMPLOYEES columns (EMERGENCY_CONTACT_NAME, EMERGENCY_CONTACT_PHONE) not in a separate normalized table | Both columns confirmed on EMPLOYEES DDL; no separate table DDL found | If a separate EMERGENCY_CONTACTS table exists, it is undocumented | DBA confirmation |
| ASM-007 | All audit columns (CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE) are populated by triggers not yet recovered from source | Trigger pattern is referenced; triggers not fully analysed | Missing audit data on migration if trigger logic must be replicated | Confirm trigger existence via database metadata |

### 5.2 Business Logic Assumptions

| ID | Assumption | Basis | Risk if Wrong | Validation Required |
|---|---|---|---|---|
| ASM-008 | COBRA notification timing is 14 days from qualifying event (termination) | Standard US federal COBRA requirement; BA supplement states this | If company has a different administered plan with extended notice periods, the NFR is wrong | Legal/HR review |
| ASM-009 | ACH prenote requirement applies to all new bank account activations (Nacha rule) | Standard Nacha requirement; PRENOTE_SENT column design implies this | If prenote is not required by the company's banking agreement, the prenote module is unnecessary scope | Confirm with payroll administrator |
| ASM-010 | Calibration is intended to occur between COMPLETED and ACKNOWLEDGED in the performance review workflow | Standard HR practice; CALIBRATED_RATING column placement in schema implies this position | If calibration is post-acknowledgement or optional, the status machine design changes | Business stakeholder decision required (OQ-009) |
| ASM-011 | The hard-coded AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` is the only encryption key in use for all encrypted columns | All encrypted columns reference PKG_SECURITY.encrypt_value which uses a single key | If multiple keys were ever used, encrypted data cannot be uniformly decrypted without key history | DBA and security team must confirm key management history |
| ASM-012 | TAX_BRACKETS and LEAVE_TYPES are maintained as reference/seed data and are not expected to change during migration | Pattern of reference data in 01_reference_data.sql; values are table-driven | If brackets change mid-migration, in-flight payroll calculations may produce incorrect results | Confirm with payroll team — freeze tax bracket data during migration |
| ASM-013 | Oracle Forms (.fmb) functionality is fully captured by the XML exports and the PL/SQL package layer | TA analysis and AA analysis treated XML exports as equivalent to source; PL/SQL was primary logic layer | If Oracle Forms hold custom PL/SQL not captured in .pkb files, logic is missing from all analysis tracks | Full Oracle Forms Builder access required for validation |
| ASM-014 | The self-service portal connects to the database using the HRMS application schema user | No portal source code available; TD-81 flags the risk | If portal connects as a separate limited user, some assumed access gaps do not apply | Confirm portal DB connection credentials with infrastructure team |

### 5.3 Integration Assumptions

| ID | Assumption | Basis | Risk if Wrong | Validation Required |
|---|---|---|---|---|
| ASM-015 | ADP receives benefits feed at the BENEFITS_FEED_OUT Oracle directory path; no API acknowledgement | PKG_INTEGRATION.export_benefits_feed writes to UTL_FILE; no acknowledgement read path found | If ADP has changed to API-based integration, the flat-file export is obsolete | Confirm with ADP account manager |
| ASM-016 | Oracle Financials GL Journal Import expects the specific pipe-delimited format currently generated | PKG_INTEGRATION.generate_gl_journal produces a pipe-delimited format; Oracle GL Journal Import standard format inferred | If Oracle Financials was upgraded or the GL import format changed, the feed is generating rejected files | Confirm with Oracle Financials DBA/admin |
| ASM-017 | sync_org_structure was never scheduled and has never successfully executed | Procedure is a complete stub; false log message would look like successes | If it was scheduled, the AUDIT_LOG contains misleading records of "successful" syncs | Query AUDIT_LOG: `SELECT * FROM AUDIT_LOG WHERE LOG_MESSAGE = 'Org structure sync completed'` |

---

## 6. Open Questions Requiring Human Review

The following questions **must be answered by human reviewers before code generation begins**. They are grouped by priority: Mandatory (code generation cannot start without these answers) and High (answers significantly affect design but generation can proceed with documented assumptions).

### 6.1 Mandatory Questions — Code Generation Blocked

| OQ ID | Question | Domain | Who Must Answer | Impact if Not Answered |
|---|---|---|---|---|
| OQ-001 | Does `USER_CREDENTIALS` DDL exist in the production database? What are the exact column definitions, especially the hash algorithm column and lockout columns? | Security | DBA | Authentication module cannot be designed; migration script cannot be written |
| OQ-002 | Confirm the AES-256 key management history. Has `HR$ystem_3ncrypt10n_K3y_2024!!` ever been rotated? Are there any rows encrypted with a different key? | Security / Data Migration | DBA + Security Team | All encrypted column migration (SSN, bank account, dependent SSN) is blocked; data may be permanently unreadable if key history is lost |
| OQ-003 | Is `PKG_INTEGRATION.sync_org_structure` currently scheduled in DBMS_SCHEDULER or any external job scheduler? Provide the schedule definition. | Operations | DBA | Risk of false-positive log pollution; schedule must be removed before go-live |
| OQ-004 | Does `PKG_PAYROLL.calculate_final_pay` need to exist? What is the current process for calculating final pay on termination? Is it manual, in a separate system, or through an undiscovered procedure? | Payroll / Business | Payroll Administrator + HR | Termination workflow specification cannot be completed |
| OQ-005 | Confirm the intended ACH disbursement flow. Does the organization use NACHA ACH files? Which bank? What is the current actual disbursement mechanism for net pay if EMPLOYEE_BANK_ACCOUNTS is unused? | Payroll / Finance | Payroll Administrator + Finance | ACH module cannot be designed; PAID status transition logic is undefined |
| OQ-006 | What is the COBRA administration process? Is it handled by a third-party benefits administrator (and if so, what notification API or file format do they require)? What is the qualifying event reporting SLA? | Compliance / HR | HR / Legal | COBRA notification module cannot be designed; every termination is currently a compliance violation |
| OQ-007 | Should `export_benefits_feed` filter on `BENEFITS_ENROLLED = 'Y'` or should all active dependents always be exported to ADP? | Benefits / Business | HR / Benefits Administrator | ADP feed specification cannot be finalized |

### 6.2 High Priority Questions — Proceed with Documented Assumption

| OQ ID | Question | Domain | Who Must Answer | Current Assumption | Impact if Assumption Wrong |
|---|---|---|---|---|---|
| OQ-008 | Do RPT_* tables (RPT_HEADCOUNT, RPT_COMPENSATION, etc.) exist in the production database and do they currently hold data? | Reporting | DBA | Tables do not exist or hold no data | Migration must handle historical report snapshots |
| OQ-009 | Is performance calibration a required business process? If yes: who initiates it, what is the workflow, is it mandatory before acknowledgement, and who can modify CALIBRATED_RATING? | Performance / HR | HR Leadership | Calibration is aspirational / future feature; not required for initial forward engineering | Performance specification must be rewritten to include calibration gate |
| OQ-010 | Confirm the intended merge behavior for VQ-DEP-04: should dependent records be inactivated immediately on employee termination or held active during a COBRA election window? | Benefits / Compliance | HR / Legal | Inactivate immediately (consistent with ACTIVE_FLAG soft-delete pattern) | Benefits feed will include/exclude dependents of terminated employees incorrectly |
| OQ-011 | Is `TIME_ATTENDANCE_RECORDS` an existing production table? Is time and attendance data currently imported? If so, what is the source system and what is the data currently used for? | HR / Operations | HR Operations | Table does not exist; feature is unimplemented | Migration must include time and attendance data |
| OQ-012 | Confirm whether the portal authenticates via PKG_SECURITY.authenticate and passes session_id to PKG_LEAVE calls, or whether it connects directly to the database with its own credentials. | Security / Architecture | Application Owner / DBA | Portal connects as HRMS application user with full schema access | Portal security model is more restrictive than assumed; some TD-81 risks may not apply |
| OQ-013 | Is the GL Journal Import integration currently functional? Has Oracle Financials ever successfully processed a file from HRMS? If yes, confirm Journal Source and Journal Category values expected. | Finance / Integration | Oracle Financials DBA + Finance | Journal Source/Category are correctly set in the undiscovered values | GL feed produces rejected files in Oracle Financials |
| OQ-014 | Confirm the target platform for forward engineering. Is this a rewrite on a new RDBMS (PostgreSQL, SQL Server) or a modernization within Oracle? This affects: Oracle MEDIAN() migration (MC-02b), CONNECT BY usage, UTL_FILE dependencies, and Oracle Forms replacement strategy. | Architecture | Solution Owner / CTO | Oracle database retained; Oracle Forms replaced with web UI | All Oracle-specific functions require rewrite if platform changes |
| OQ-015 | What is the fiscal year start date? The TA analysis found October 1 hard-coded in PKG_REPORTING — is this the correct fiscal year for all reporting calculations? | Finance | Finance / Accounting | October 1 fiscal year start | All year-to-date calculations in reporting are wrong |

---

## 7. Data Quality Assessment

This section rates the trustworthiness of each analysis input and calls out specific concerns that affect forward engineering reliability.

### 7.1 Overall Input Quality Rating

| Analysis Track | Overall Quality | Pass Count | Findings Count | Trustworthiness Reasoning |
|---|---|---|---|---|
| BA (Business Analysis) | HIGH | 2 passes + 7 supplements | 140 BR + 40 supplement rules | Direct code citation for all rules; edge-case pass specifically targeted gaps; supplements resolved all cross-validation gaps |
| DA (Data Analysis) | HIGH | 3 passes + 8 supplements | 32 DQ findings + 46 business rules | Three-pass review with Gate G1 quality gating; structured JSON outputs; cross-validated against other tracks |
| TA (Technology Analysis) | HIGH | 2 passes | 81 TD items | Systematic risk register with evidence citations; two-pass edge-case extension; CI/CD and observability assessments are definitively complete |
| AA (Application Analysis) | HIGH | 3 passes | 33 QR findings + 25 AV + 14 RISK | Multi-pass with explicit [EDGE-CASE-FOUND] markers; risk registers are quantified |
| Cross-Validation | HIGH | Single systematic pass | 14 gaps identified; all 14 resolved | All gaps have explicit resolution status; supplements are integrated into parent track documents |

### 7.2 Per-Domain Data Quality Details

| Domain | Quality | Concerns | Effect on Forward Engineering |
|---|---|---|---|
| EMPLOYEES table definition | HIGH — 3 independent confirmations | Dual bank-account representation (column + separate table) creates one ambiguity | Resolve CONT-001 before writing migration script |
| PAYROLL_RUNS + PAYROLL_DETAILS schema | HIGH | GL_FEED_SENT_DATE column does not exist yet (recommended addition) | New columns required; no migration concern for existing data |
| PERFORMANCE_REVIEWS schema | MEDIUM | CALIBRATED_RATING DDL could not be confirmed from schema-catalogue.json ([Not found in deep scan]) | Forward engineering spec must treat calibration columns as unconfirmed; validate with DBA before creating new tables |
| USER_CREDENTIALS schema | MEDIUM — inferred | DDL not recovered; all column definitions derived from package code references | Schema migration must be validated column-by-column against production before executing |
| RPT_* tables | MEDIUM — inferred | All 7 RPT_* column shapes are inferred from SELECT lists; no DDL confirmed | Do not include in migration until DBA confirms table existence and production data status |
| TIME_ATTENDANCE_RECORDS | LOW — entirely inferred | No DDL; no confirmed production table; stub only reads from a file not a table | Treat as new module design, not migration |
| AUDIT_LOG contents | LOW | Contaminated by false-positive success messages from sync_org_structure, refresh_reporting_tables, import_time_attendance, and potentially others | Audit log history cannot be trusted for operational reconstruction; do not use for migration data sourcing |
| SYSTEM_PARAMETERS | MEDIUM | Some parameters are ignored in code (session timeout consumed but overridden by hard-coded value); APP_VERSION is a static row | Forward engineering must map which parameters are actually consumed before propagating them to the new system |
| Encrypted column data | LOW — key risk | All encrypted data (SSN, bank account numbers, dependent SSNs) is protected by a key that is committed in plain text in the repository | Assume all encrypted data is compromised; plan for re-encryption with a new key management system immediately after migration |
| Oracle Forms logic | MEDIUM | XML exports are not the canonical source; .fmb files were never recovered; client-side validation logic may be missing | Some business rules may be encoded only in Forms triggers — the AA analysis acknowledges this gap explicitly |

### 7.3 Data Quality Metric Summary

| Metric | Value | Notes |
|---|---|---|
| Total DQ findings | 32 (DQ-001–DQ-032) | Three-pass DA review |
| Critical severity DQ findings | 4 | DQ-001 (hard-coded key), DQ-003 (auth stub), DQ-010 (MD5), DQ-009 (PAID orphan) |
| HIGH severity DQ findings | 9 | Post-Pass-3 tally |
| Total business rules identified | 184 | BR-01–140 (BA) + 44 in hidden-business-rules.json (DA) |
| Architecture violations logged | 25 | AV-001–AV-025 |
| Application risks logged | 14 | RISK-001–RISK-014 |
| Technology debt items | 81 | TD-01–TD-81 |
| Cross-validation gaps resolved | 14/14 | 100% resolution rate |
| Gate G1 open questions | 10 | G1-01–G1-10; split mandatory/non-blocking |
| Confirmed DDL tables | 30 | Via three-pass DA review |
| Inferred/unconfirmed tables | 8 | RPT_* (7) + TIME_ATTENDANCE_RECORDS (1) + USER_CREDENTIALS (partially) |

---

## 8. Recommended Enrichment Actions

These actions, if completed before code generation begins, would materially increase confidence and reduce rework risk. They are ordered by priority.

### 8.1 Critical Priority — Complete Before Architecture Design

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-001 | DBA: Run full DDL extraction from production database (`DBMS_METADATA.GET_DDL` for all tables, sequences, triggers, synonyms, grants) | Definitive schema including USER_CREDENTIALS, RPT_* confirmation, sequence current values, all triggers | Resolves ASM-001, ASM-003, ASM-005, ASM-006, ASM-007; elevates 6 MEDIUM domains to HIGH | 2–4 hours DBA time |
| ENR-002 | Security team: Conduct AES-256 key history audit. Identify all encryption key values ever used, which rows were encrypted with each key, and confirm whether `HR$ystem_3ncrypt10n_K3y_2024!!` is the only historical value | Key management manifest with per-batch coverage | Resolves ASM-011; unblocks all PII migration planning | 1–2 days security + DBA |
| ENR-003 | HR + Legal: Define the COBRA notification process and timeline. Document whether a third-party administrator handles COBRA elections, the required notification format, and the qualifying event SLA | COBRA business process definition | Resolves OQ-006; unblocks termination workflow specification | 1 workshop |
| ENR-004 | Payroll Administrator: Document the current actual disbursement mechanism. Answer: how are employees actually paid if EMPLOYEE_BANK_ACCOUNTS is never read? Provide the manual process or identify the undiscovered system | Current disbursement process document | Resolves OQ-005; unblocks ACH module design (or removes it from scope) | 2-hour interview |
| ENR-005 | DBA: Check DBMS_SCHEDULER for any scheduled jobs referencing `sync_org_structure`, `refresh_reporting_tables`, or `import_time_attendance` | Scheduler job inventory with status and last run times | Resolves OQ-003 and ASM-017; enables accurate AUDIT_LOG quality assessment | 30 minutes DBA time |

### 8.2 High Priority — Complete Before Detailed Design

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-006 | Oracle Forms Builder access: Open and compile all .fmb files; extract all WHEN-VALIDATE-ITEM, WHEN-BUTTON-PRESSED, and PRE-COMMIT triggers to a plain-text extract | Forms trigger catalogue | Resolves ASM-013; may surface business rules not captured in any track | 1–2 days Forms analyst |
| ENR-007 | HR Leadership: Calibration workshop. Define whether calibration is required, who owns it, what the workflow is, and whether CALIBRATED_RATING replaces or supplements OVERALL_RATING in reports and merit calculations | Calibration process definition | Resolves OQ-009; unblocks performance management specification | 2-hour workshop |
| ENR-008 | Finance: Confirm fiscal year start date, GL Journal Source and Category values expected by Oracle Financials, and confirm whether the GL integration has ever successfully run | GL integration confirmation document | Resolves OQ-013, OQ-015; elevates GL integration confidence from MEDIUM to HIGH | 1-hour Finance interview |
| ENR-009 | Solution Owner / CTO: Platform decision — Oracle retained vs. migration to PostgreSQL/SQL Server | Platform decision record | Resolves OQ-014; unblocks MC-02b Oracle MEDIAN() resolution, UTL_FILE replacement, CONNECT BY replacement, Forms replacement strategy | Architecture decision meeting |
| ENR-010 | HR / Benefits: Confirm BENEFITS_ENROLLED filter intent for ADP feed | Benefits feed specification clarification | Resolves OQ-007 (CONT-011); final ADP feed spec can be written | 1-hour Benefits interview |
| ENR-011 | Payroll Administrator: Confirm bank account data entry channel. Are employees entering bank accounts via a form that populates EMPLOYEE_BANK_ACCOUNTS? Or via EMPLOYEES.BANK_ACCOUNT_NUMBER? Or via an external HR portal? | Data entry channel map | Resolves CONT-001; determines which columns are live and which are legacy | 30-minute interview |

### 8.3 Medium Priority — Complete Before Development Sprints

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-012 | DBA: Sample AUDIT_LOG to identify false-positive entries. Query for `LOG_MESSAGE = 'Org structure sync completed'` and `LOG_MESSAGE = 'Reporting tables refreshed'` and `LOG_MESSAGE = 'Time attendance import completed'` — count frequency and date range | Audit log contamination report | Confirms operational impact of CONT-008 and stub false-positive findings | 1 hour DBA |
| ENR-013 | Infrastructure team: Document portal database connection credentials and schema access grants | Portal connection security profile | Resolves OQ-012; determines whether TD-81 security gap is theoretical or exploitable | 2-hour infrastructure review |
| ENR-014 | ADP account manager: Obtain current ADP benefits feed specification including format version, field mapping, expected file naming, and delivery method | ADP technical specification document | Confirms or refutes 203-char fixed-width format; resolves TD-73 no-trailer risk; resolves ASM-015 | ADP vendor engagement |
| ENR-015 | Payroll team: Review TAX_BRACKETS reference data for current-year accuracy. Confirm federal brackets, state flat rates, FICA wage bases, and Medicare rates against IRS Publication 15 | Tax bracket validation report | Determines whether tax calculation defects are limited to structural bugs (HOH $0 federal) or also include stale rate data | 4-hour payroll review |
| ENR-016 | HR team: Confirm FMLA REQUIRES_DOCUMENT='N' intent (TD-71). Is document collection intentionally waived, or is this a misconfiguration? | FMLA configuration decision | Resolves TD-71; if misconfiguration, seed data must be corrected before go-live | 30-minute HR interview |
| ENR-017 | Security team: Confirm whether the Oracle HTTP Server / Application Server hosting Oracle Forms applies SSL/TLS termination and whether network-layer database connections are encrypted | Network security profile | Context for security architecture specification; determines whether DB-layer encryption is the only control | Network/infrastructure review |

### 8.4 Low Priority — Good to Have Before Testing Phase

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-018 | BA team: Interview HR operations staff to validate the 140 business rules against actual daily workflows. Specifically validate: leave request approval chains, salary grade override scenarios, and manager hierarchy edge cases | Business rule validation sign-off | Converts BA-documented rules from code-inferred to business-confirmed | 2-day interview series |
| ENR-019 | DBA: Document all existing Oracle DB roles, grants, synonyms, and public/private database links | Database security inventory | Provides complete RBAC baseline; DA access-control-matrix currently covers only application-layer RBAC | 4-hour DBA documentation effort |
| ENR-020 | Infrastructure team: Confirm Oracle version (19c confirmed vs. production exact release), OS, server specs, and any Oracle-licensed features currently in use (Advanced Security, Label Security, etc.) | Infrastructure baseline document | Informs technology blueprint licensing and migration complexity | 2-hour infrastructure review |
| ENR-021 | DBA: Extract DBMS_SCHEDULER job definitions, frequencies, and last execution timestamps for all current scheduled jobs | Scheduler inventory | Provides complete picture of what runs automatically; supplements TA operational architecture assessment | 1 hour DBA |
| ENR-022 | Dev team: Confirm source control history for PKG_PAYROLL — specifically whether `calculate_final_pay` was ever implemented in a prior commit or whether it was always a stub | Git/source control history report | If ever implemented and deleted, the business logic can be recovered; changes design approach | 1 hour git archaeology |

---

## Appendix A: Document Traceability

| Forward Engineering Deliverable | Primary Input Files | Cross-Track Validation Status |
|---|---|---|
| 01_BRD | BA_Deep_Analyst.md (all passes) + BA_Deep_Analyst_Edge.md | Validated — all 14 cross-validation gaps resolved |
| 02_BUSINESS_CAPABILITY_MODEL | BA + Domain Model (05_DOMAIN_MODEL) | Validated |
| 03_USE_CASE_SPECIFICATION | BA_Deep_Analyst.md BR-01–BR-140 | Validated |
| 06_DATA_DICTIONARY | da-outputs/data-dictionary.md (three-pass reviewed) | HIGH confidence |
| 07_DATA_MODEL_SPECIFICATION | da-outputs/schema-catalogue.json + DA_Data_Reviewer.md | MEDIUM — 8 tables unconfirmed |
| 08_ERD | da-outputs/schema-catalogue.json | MEDIUM — inferred tables dashed |
| 09_DATA_FLOW_DIAGRAM | da-outputs/data-flow-map.md §1–§14 | HIGH — stubs documented explicitly |
| 11_API_CONTRACT_SPECIFICATION | BA rules + DA data shapes + AA module boundaries | MEDIUM — portal auth model unconfirmed |
| 12_TECHNOLOGY_BLUEPRINT | TA outputs + da-outputs/migration-complexity.json | Platform decision (OQ-014) required |
| 14_NFR_SPECIFICATION | TA CI/CD + observability + BA edge cases | HIGH — gaps are clearly documented |
| 15_FORWARD_ENGINEERING_SPECIFICATION | All tracks synthesized | Requires resolution of all Mandatory OQs |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | da-outputs/review-summary.md + AA executive-summary | Current verdict: PARTIAL — see OQ-001–OQ-007 |

---

## Appendix B: Critical Risk Summary for Executives

The following five items represent the highest-risk findings from the combined analysis and must be communicated to leadership before any forward engineering commitment is made:

1. **Authentication is completely broken (BR-042):** The current system allows any active employee to log in as any other active employee without knowing their password. Every access log since system deployment must be treated as untrustworthy. This is not a forward engineering risk — it is a live production security incident.

2. **All PII is potentially exposed (DQ-001/TD-01):** The AES-256 encryption key is committed in plain text in the source repository. Every encrypted field (SSN, bank account numbers, dependent SSNs) should be treated as disclosed to anyone who has ever had repository access.

3. **Direct deposit has never worked (AV-024):** EMPLOYEE_BANK_ACCOUNTS is a complete schema with zero code references. How employees are actually paid must be determined by interviewing the payroll team before any forward engineering work on the payroll module begins.

4. **Every termination creates a federal COBRA compliance violation (PP-TERM-01):** The COBRA notification step is a TODO comment with no implementation. If the company has terminated employees through this system, those qualifying events should be reviewed with legal counsel.

5. **The system has zero automated testing, zero CI/CD, and no rollback capability:** Any deployment to the system is irreversible without manual DBA intervention. The forward engineering effort must include full CI/CD pipeline design as a prerequisite to any production deployment of the rewritten system.

---

*End of Forward Engineering Input Map — Version 1.0*
*Next review gate: After resolution of OQ-001 through OQ-007 (Mandatory Questions)*
*Document owner: Solution Architect*
*Stakeholder distribution: Engineering Lead, HR Systems Owner, CISO, Payroll Administrator, Legal (COBRA section)*
