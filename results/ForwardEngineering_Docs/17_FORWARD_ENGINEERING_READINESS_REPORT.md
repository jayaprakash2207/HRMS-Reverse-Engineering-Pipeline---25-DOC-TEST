# Forward Engineering Readiness Report
## Acme Corporation HRMS — Oracle 19c / PL/SQL System
### Document ID: 17_FORWARD_ENGINEERING_READINESS_REPORT.md
### Classification: Internal — Solution Architecture
### Report Version: 1.0 (Multi-Pass Merged Analysis Edition)
### Analysis Basis: BA Pass 1+2 (BR-01–140), DA Pass 1–3, TA Pass 1–3, AA Pass 1–3, Cross-Validation (14 gaps resolved)

---

## Table of Contents

1. [Executive Readiness Summary](#1-executive-readiness-summary)
2. [Readiness Scorecard](#2-readiness-scorecard)
3. [Analysis Completeness Assessment](#3-analysis-completeness-assessment)
4. [Critical Blockers](#4-critical-blockers-before-code-generation-can-start)
5. [Recommended Pre-Generation Actions](#5-recommended-pre-generation-actions)
6. [Confidence Levels per Domain](#6-confidence-levels-per-domain)
7. [Assumptions Requiring Validation](#7-assumptions-requiring-validation)
8. [Open Questions for Business Stakeholders](#8-open-questions-for-business-stakeholders)
9. [Open Questions for Technical Stakeholders](#9-open-questions-for-technical-stakeholders)
10. [Risk Assessment](#10-risk-assessment-for-forward-engineering)
11. [Recommended Pilot / POC Scope](#11-recommended-pilot--poc-scope)
12. [Go / No-Go Recommendation](#12-go--no-go-recommendation-with-conditions)

---

## 1. Executive Readiness Summary

The Acme Corporation HRMS reverse-engineering pipeline has completed four analysis passes across Business, Data, Technology, and Application dimensions, with cross-validation resolving 14 inter-track gaps. The aggregate picture is one of a **partially functional legacy system with critical compliance and security deficiencies that must be resolved prior to any forward engineering code generation effort**.

The system is an Oracle 19c / PL/SQL monolith with Oracle Forms 12c as the presentation layer. It manages approximately ten bounded contexts: Employee Identity, Compensation, Leave Management, Performance, Benefits, Security & Access, Organisational Structure, Notifications, Integration & Export, and Reporting. The codebase has version `4.2.0` declared in `SYSTEM_PARAMETERS`, indicating a mature lineage, but the analysis has surfaced **81 technology defect items**, **140 business rules with 33 edge-case additions**, **46 hidden data rules**, and **33 quality-review findings** across the application layer.

**Three findings alone constitute existential risk to a direct code-generation exercise:**
- Direct deposit disbursement is architecturally designed (schema exists, DEPOSIT_TYPE split model is complete) but **operationally absent** — no PL/SQL procedure reads `EMPLOYEE_BANK_ACCOUNTS` during payroll. Every payroll run that reaches `APPROVED` status has no disbursement path. This is not a bug; it is an unimplemented capability.
- `PKG_SECURITY.authenticate()` **never verifies the password** — any user with a valid username can authenticate regardless of what credential is submitted. This is documented in the codebase with the comment *"we simulate authentication against a simplified model."* The system is currently operating without any real authentication gate.
- COBRA notification is not implemented. Every employee termination processed through `PKG_EMPLOYEE.terminate_employee` constitutes an unreported qualifying event under federal ERISA/COBRA requirements. The 14-day notification window is being missed systemically.

These three issues are not forward-engineering design decisions — they are **current production deficiencies** that the forward-engineered system must either replicate (to maintain business continuity) or supersede (to remediate compliance exposure). Forward engineering without a clear policy decision on each will produce a system that either inherits the defects or breaks existing process expectations.

Below these blockers, the analysis found the system to be architecturally coherent enough that forward engineering is **feasible** with appropriate scoping and sequencing. The domain model is well-bounded, the data model is normalised, and the key business logic is recoverable. However, the delivery risk is **HIGH** without the pre-generation actions described in Section 5.

**Overall Readiness Posture: CONDITIONAL — NOT READY for immediate code generation.**

---

## 2. Readiness Scorecard

### 2.1 Domain-by-Domain Readiness

| Domain | Readiness Score | Grade | Evidence Basis | Key Risk |
|--------|----------------|-------|----------------|----------|
| Business Analysis | 68 / 100 | C+ | 140 BR documented; 33 edge-case BRs; 9 discrepancy entries | 15 unresolved validation-queue items; COBRA, direct deposit, final pay policy undefined |
| Data Architecture | 61 / 100 | C | 30 confirmed tables, 7 inferred RPT_* tables, 1 implied TIME_ATTENDANCE; 46 hidden rules | 32 DQ findings; PII handling gaps; 3 inferred tables with no DDL confirmation |
| Technology Architecture | 44 / 100 | D+ | 81 TD items catalogued; full CI/CD gap; security vulnerability map complete | 0/14 CI/CD capabilities; hard-coded encryption key; no test suite; 6 Critical TD items |
| Application Quality | 57 / 100 | C- | 33 QR findings; violation register (25 AV items); risk register (14 risks) | 9 HIGH architecture violations; authentication bypass; 5 Critical application risks |
| Integration Completeness | 35 / 100 | F | 4 of 7 integration procedures are confirmed stubs; bank account disbursement missing | sync_org_structure, refresh_reporting_tables, import_time_attendance, calculate_final_pay all non-functional |
| Security Posture | 22 / 100 | F | Hard-coded AES key; MD5 passwords; auth bypass; no brute-force lockout; no SAST | Multiple OWASP Top 10 violations confirmed |

### 2.2 Capability Readiness by HRMS Module

| Module | Implementation Status | Gaps | Forward-Engineering Priority |
|--------|-----------------------|------|------------------------------|
| Employee Hire / Onboarding | Functionally complete | Minor: no prenote on bank account creation | Medium |
| Employee Termination | Partially complete | Critical: COBRA absent, final pay absent, access revocation partial | HIGH — resolve before generation |
| Payroll Calculation | Core logic present | High: direct deposit missing; HOH tax defect ($0 federal tax) | HIGH — resolve before generation |
| Leave Management | Core logic present | Medium: accrual retry defect (BR-LIB-05); FMLA doc not enforced | Medium |
| Performance Reviews | Partially complete | High: calibration workflow entirely absent; rating distribution reports wrong column | Medium |
| Benefits Feed (ADP) | Functional (stub caveat) | Medium: BENEFITS_ENROLLED not filtered; no format version/trailer | Medium |
| GL Feed (Oracle Financials) | Functional | Medium: Journal Source/Category undeclared; no GL_FEED_SENT_DATE | Medium |
| Org Structure Sync (LDAP) | Non-functional stub | Critical: zero lines of sync code; logs false success | LOW priority to replicate |
| Reporting (RPT_*) | Reports run live against OLTP | Medium: nightly refresh is a stub; MEDIAN() portability issue | Medium |
| Time & Attendance Import | Non-functional stub | Critical: destination DDL absent; no payroll link | LOW priority to replicate |
| Authentication / Security | Critically deficient | Critical: password never verified; MD5 hashing; hard-coded key | BLOCKER — resolve before generation |
| Notifications | Framework present | Medium: SMS channel not implemented; template rendering confirmed | Low |

### 2.3 Forward Engineering Readiness Radar (Narrative)

- **Business Rules Capture:** 79% complete. Core transactional logic (hire, transfer, payroll calculation, leave accrual, review lifecycle) is fully recovered. Compliance-adjacent rules (COBRA sequencing, NACHA prenote, FMLA documentation enforcement) are identified as gaps, not unrecoverable.
- **Data Model Confidence:** 76% of tables have confirmed DDL. 7 RPT_* tables are inferred from SELECT lists and have high confidence shapes. `TIME_ATTENDANCE_RECORDS` has no DDL at all. `USER_CREDENTIALS` column set is inferred from package references. `EMPLOYEE_PAY_ELEMENTS` is referenced in domain model analysis but DDL not confirmed.
- **Technology Baseline:** The technology stack is fully identified (Oracle 19c, Forms 12c, UTL_FILE, DBMS_CRYPTO, DBMS_SCHEDULER, Oracle Reports .rdf). Migration-complexity risks are catalogued (MEDIAN() aggregate, CONNECT BY hierarchy, Oracle-specific encryption). The delivery infrastructure (CI/CD, testing, secret management) is absent and must be built from scratch.
- **Application Behaviour:** The application's happy-path behaviour is recoverable. Edge-case behaviour (concurrent session handling, split-deposit routing, COBRA window, final-pay calculation) is either absent or defective and requires design decisions before forward engineering.

---

## 3. Analysis Completeness Assessment

### 3.1 What Was Found

| Analysis Artifact | Count | Status |
|-------------------|-------|--------|
| Business Rules (Total) | 140 (BR-01–BR-140) | Complete — two passes merged |
| Business Rules — Edge Cases | 33 (BR-108–BR-140) | Appended and marked [EDGE-CASE-FOUND] |
| Supplemental BA Rules (DEP, ORG, BA, TERM, PERF, LIB) | ~65 additional BRs across sub-documents | Complete |
| Discrepancy Log Entries | 9 (DISC-001–DISC-009) | Complete |
| Data Quality Findings | 32 (DQ-001–DQ-032) | Complete |
| Hidden Business Rules (DA track) | 46 (BR-DA-001–BR-DA-046) | Complete |
| Technology Defect Items | 81 (TD-01–TD-81) | Complete — three passes |
| Application Quality Reviews | 33 (QR-001–QR-033) | Complete — three passes |
| Architecture Violations | 25 (AV-001–AV-025) | Complete |
| Application Risks | 14 (RISK-001–RISK-014) | Complete |
| Cross-Validation Gaps Identified | 14 | All resolved |
| Confirmed DDL Tables | 30 | High confidence |
| Inferred Tables (RPT_*) | 7 | Medium confidence — shapes derivable from SELECT lists |
| Implied Tables (no DDL recovered) | 2 (TIME_ATTENDANCE_RECORDS, USER_CREDENTIALS partial) | Low confidence on column set |
| Confirmed Views | 6 | High confidence |
| Confirmed Packages Analysed | 9 (PKG_EMPLOYEE, PKG_PAYROLL, PKG_LEAVE, PKG_PERFORMANCE, PKG_SECURITY, PKG_NOTIFICATION, PKG_COMMON, PKG_INTEGRATION, PKG_REPORTING) | Complete |
| Oracle Forms Analysed | 4+ (HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LOGIN, partial others) | Partial — XML exports only, no compiled .fmb |
| PII Inventory Entries | 15+ data elements confirmed across 6 tables | Complete |
| Bounded Contexts Identified | 10 (BC-01–BC-10) | Complete |
| Integration Touch-Points | 7 (ADP benefits, Oracle Financials GL, LDAP org sync, time attendance import, NACHA ACH, Oracle Reports .rdf, self-service portal) | Complete — stub status noted per integration |

### 3.2 Confirmed Gaps Remaining After Three Passes

| Gap ID | Description | Severity | Impact on Forward Engineering |
|--------|-------------|----------|-------------------------------|
| GAP-01 | `TIME_ATTENDANCE_RECORDS` — no DDL anywhere in recovered source | HIGH | Cannot generate migration scripts; integration pattern must be redesigned |
| GAP-02 | `USER_CREDENTIALS` — column set inferred, not confirmed from DDL | HIGH | Password migration strategy unknowable without confirmed schema |
| GAP-03 | `EMPLOYEE_PAY_ELEMENTS` — referenced in domain model but no DDL confirmed | HIGH | Payroll element configuration for forward system is undefined |
| GAP-04 | Oracle Forms `.fmb` source files not in repository — only XML exports | HIGH | UI regeneration requires Oracle Forms Builder 12c; no build-reproducible artifact |
| GAP-05 | Calibration workflow business rules entirely absent | MEDIUM | PERFORMANCE_REVIEWS.CALIBRATED_RATING is a dead column; no policy to implement |
| GAP-06 | `PKG_PAYROLL.calculate_final_pay` procedure does not exist | CRITICAL | Termination payroll cannot be modelled without knowing expected calculation |
| GAP-07 | COBRA notification timing and sequencing policy is undefined | CRITICAL | Cannot generate compliant termination flow without federal requirement mapping |
| GAP-08 | NACHA ACH prenote process undefined — no procedure exists | HIGH | Direct deposit cannot go live without prenote protocol documented |
| GAP-09 | Oracle Financials GL Journal Source and Journal Category values are undocumented | MEDIUM | GL feed may be generating files that Oracle Financials rejects in production |
| GAP-10 | `schema-catalogue.json` shows `total_rules_found` at 43–46 across versions | LOW | Minor inconsistency; does not block generation but should be reconciled |
| GAP-11 | Self-service portal database user, grants, and connection model are undeclared | HIGH | Security architecture for the portal tier cannot be forward-engineered without this |
| GAP-12 | Oracle Reports `.rdf` files not in repository | MEDIUM | Reporting layer regeneration scope is unknown |
| GAP-13 | `DBMS_SCHEDULER` job definitions not in repository source | MEDIUM | Background job topology (accrual runs, queue processing frequency) is inferred, not confirmed |

### 3.3 Inter-Track Consistency After Cross-Validation

All 14 cross-validation gaps have been resolved and documented. Post-resolution, the four tracks are internally consistent on table ownership, procedure signatures, and business rule attributions. The primary residual inconsistency is the `total_rules_found` counter discrepancy in `hidden-business-rules.json` (values of 42, 43, 44, and 46 appear across document versions), which is a documentation artefact and does not affect substance.

---

## 4. Critical Blockers Before Code Generation Can Start

The following items are **hard blockers** — forward engineering cannot produce a correct, compliant, or safe system unless each is resolved before generation begins. They are listed in descending order of severity.

---

### BLOCKER-01: Authentication Bypass — System Has No Real Authentication

**Severity:** CRITICAL — SECURITY  
**Evidence:** BR-042, DQ-003, BA_Deep_Analyst.md, hidden-business-rules.json  
**Finding:** `PKG_SECURITY.authenticate()` never queries `USER_CREDENTIALS`. The procedure comment reads *"we simulate authentication against a simplified model."* Any caller with a valid username in the `EMPLOYEES` table is granted a session regardless of password. This means the currently deployed system has no password gate.  
**Why it blocks generation:** The forward-engineered system's authentication architecture cannot be decided without knowing whether the intent is to (a) fix this defect and implement real credential verification, (b) replace authentication with an identity provider (LDAP/SSO/OAuth2), or (c) maintain the current behaviour for a transitional period. Each path has radically different implementation implications.  
**Resolution required:** Business and security stakeholders must decide on the target authentication model before any security module is generated.

---

### BLOCKER-02: Direct Deposit Disbursement is Unimplemented

**Severity:** CRITICAL — FINANCIAL  
**Evidence:** BR-BA-12, PP-BA-01, AV-024, RISK-013, DISC-009  
**Finding:** `EMPLOYEE_BANK_ACCOUNTS` is a fully-designed table with split-deposit support (FULL / PARTIAL_AMOUNT / PARTIAL_PERCENT / REMAINDER deposit types, PRIORITY_ORDER, ACH prenote columns). Zero PL/SQL procedures read this table. The payroll lifecycle ends at GL feed generation with PAYROLL_RUNS.STATUS = 'PAID' but no actual disbursement occurs. The system appears to be operating with manual payroll disbursement outside the application.  
**Why it blocks generation:** The forward-engineered payroll module must include disbursement. The shape of that disbursement (NACHA ACH file, banking API, manual process continuation) is a business decision that determines which tables and procedures are generated. Additionally, the decryption path for `ACCOUNT_NUMBER_ENC` is not implemented anywhere in the recovered source — this must be confirmed or designed before migration.  
**Resolution required:** Confirm intended disbursement mechanism. Confirm whether `PKG_SECURITY.decrypt_value` covers bank account numbers or a separate key is required. Document ACH prenote policy.

---

### BLOCKER-03: COBRA Notification Gap — Federal Compliance Exposure

**Severity:** CRITICAL — LEGAL / COMPLIANCE  
**Evidence:** PP-TERM-01, BR-TERM-01–BR-TERM-09, VQ-TERM-02  
**Finding:** `PKG_EMPLOYEE.terminate_employee` contains a single `-- TODO: Send COBRA notification` comment with no implementation. Federal law (ERISA/COBRA) requires qualifying event notification within 14 days of a termination. Every termination processed through the system since deployment has created an unreported qualifying event.  
**Why it blocks generation:** The forward-engineered termination workflow requires a compliant COBRA notification step. The timing (immediate vs. after COBRA election period), recipient list (employee + all enrolled dependents — cross-reference `EMPLOYEE_DEPENDENTS`), and delivery channel (mail, email, third-party COBRA administrator) are all policy questions. The system also cannot correctly implement COBRA without resolving VQ-DEP-04 (whether dependents should be held active for COBRA administration before inactivation).  
**Resolution required:** Legal/HR must define COBRA notification policy, timing, and responsible party. This may require an integration with a COBRA administration vendor.

---

### BLOCKER-04: `PKG_PAYROLL.calculate_final_pay` Does Not Exist

**Severity:** CRITICAL — FINANCIAL / OPERATIONAL  
**Evidence:** PP-TERM-03, AO-TERM-03, BR-TERM-08  
**Finding:** `PKG_EMPLOYEE.terminate_employee` contains a TODO comment calling `PKG_PAYROLL.calculate_final_pay`. This procedure has never been created. There is no prorated wage calculation, no PTO payout logic, and no mechanism for processing a termination that falls mid-pay-period. Every termination currently requires fully manual payroll calculation outside the system.  
**Why it blocks generation:** The forward-engineered system must include final pay calculation. The business rules for proration, PTO payout eligibility, state-law variation (California immediate payment requirement vs. others), and off-cycle payroll run handling are entirely undocumented.  
**Resolution required:** HR / Payroll must define final pay calculation rules. Legal must confirm which state regulations apply to the workforce.

---

### BLOCKER-05: Hard-Coded AES-256 Encryption Key

**Severity:** CRITICAL — SECURITY  
**Evidence:** TD-01, DQ-001, SEC-03  
**Finding:** The AES-256 encryption key `HR$ystem_3ncrypt10n_K3y_2024!!` is hard-coded in `PKG_SECURITY`. All PII encrypted in the current database (SSNs, bank account numbers, dependent SSNs) is encrypted with this key. If the key is rotated as part of forward engineering, all existing ciphertext becomes unreadable without a re-encryption migration step.  
**Why it blocks generation:** The forward-engineered system must use a proper key management solution (Oracle Wallet, AWS KMS, HashiCorp Vault, or equivalent). The migration path requires decrypting all existing PII with the old key and re-encrypting with the new key management infrastructure — a high-risk, tightly sequenced operation that must be planned before generation begins.  
**Resolution required:** Decide on key management solution. Plan the re-encryption migration. Assess whether current key exposure has compromised the data (the key is visible in source control).

---

### BLOCKER-06: No Test Infrastructure of Any Kind

**Severity:** CRITICAL — DELIVERY  
**Evidence:** TA Output 8 — CI/CD Pipeline Maturity (0/14 capabilities present)  
**Finding:** There are no unit tests, no integration tests, no test automation framework, no CI/CD pipeline, no SAST tooling, and no secret scanner in the repository. All testing is manual. The hard-coded AES key and FTP credentials in source are a direct consequence of no secret scanner being present.  
**Why it blocks generation:** Any forward-engineered system will require a test suite to validate correctness of migrated business logic. Without baseline tests on the existing system, there is no regression baseline to validate against. The forward-engineering pipeline cannot produce a verified system if there is no way to verify it.  
**Resolution required:** Establish test framework (utPLSQL for PL/SQL, or target-platform equivalent). Write smoke tests for the 10 most critical procedures before generation begins. Establish CI/CD pipeline with secret scanner.

---

### BLOCKER-07: MD5 Password Hashing in USER_CREDENTIALS

**Severity:** HIGH — SECURITY  
**Evidence:** DQ-010, BR-042, hidden-business-rules.json  
**Finding:** `PKG_SECURITY.hash_password` uses `DBMS_CRYPTO.HASH_MD5` via `RAWTOHEX(DBMS_CRYPTO.HASH(...))`. MD5 is cryptographically broken and is not acceptable for password storage under any current security standard (NIST SP 800-63B, OWASP ASVS). All current password hashes in production are crackable with commodity hardware.  
**Why it blocks generation:** The forward-engineered system must migrate to bcrypt/scrypt/Argon2 or equivalent. This requires invalidating all existing password hashes and forcing a password reset for all users — a coordinated operational event that must be planned before go-live.  
**Resolution required:** Decide on target password hashing algorithm. Plan forced password reset event. This is linked to BLOCKER-01 (authentication model decision).

---

## 5. Recommended Pre-Generation Actions

The following actions are ordered by priority. Actions in Priority Band 1 are prerequisites for Blockers 1–7. Actions in Priority Band 2 address HIGH-severity issues. Priority Band 3 actions are required for a production-grade system but can be deferred to a later sprint.

### Priority Band 1 — Must Complete Before Any Code Generation

| Action ID | Action | Owner | Estimated Effort | Unblocks |
|-----------|--------|-------|-----------------|---------|
| PGA-01 | Convene security architecture workshop: decide on target authentication model (local credential store with bcrypt, LDAP/AD, OAuth2/OIDC, or SAML federation) | CISO + Architect | 1 week | BLOCKER-01, BLOCKER-07 |
| PGA-02 | Define direct deposit disbursement mechanism: NACHA ACH file, real-time payment API, or manual continuation. Document prenote policy and Nacha compliance requirements | Payroll Manager + Architect | 2 weeks | BLOCKER-02 |
| PGA-03 | Legal/HR sign-off on COBRA notification policy: timing, recipient set, delivery channel, and whether a COBRA administrator integration is required | HR Director + Legal Counsel | 2 weeks | BLOCKER-03 |
| PGA-04 | Document `calculate_final_pay` business rules: proration formula, PTO payout eligibility table, state-law variations, off-cycle run handling | Payroll Manager | 1 week | BLOCKER-04 |
| PGA-05 | Key management infrastructure decision: select Oracle Wallet / KMS / Vault; plan re-encryption migration for all PII ciphertext in production; assess current key exposure impact | CISO + DBA | 2 weeks | BLOCKER-05 |
| PGA-06 | Establish utPLSQL (or equivalent) test framework in a development environment; write smoke tests for PKG_EMPLOYEE.create_employee, PKG_PAYROLL.calculate_payroll, PKG_SECURITY.authenticate, PKG_LEAVE.submit_leave_request | Lead Developer | 2 weeks | BLOCKER-06 |
| PGA-07 | Implement secret scanner (gitleaks or trufflehog) in repository as pre-commit hook; rotate the hard-coded AES key immediately (coordinate with PGA-05 re-encryption plan) | DevSecOps | 3 days | BLOCKER-05, BLOCKER-07 |

### Priority Band 2 — Complete Before First Sprint of Code Generation

| Action ID | Action | Owner | Estimated Effort | Addresses |
|-----------|--------|-------|-----------------|---------|
| PGA-08 | Recover or reconstruct DDL for `USER_CREDENTIALS`, `TIME_ATTENDANCE_RECORDS`, and `EMPLOYEE_PAY_ELEMENTS` from DBA production schema export | DBA | 3 days | GAP-01, GAP-02, GAP-03 |
| PGA-09 | Confirm Oracle Financials GL Journal Source and Journal Category values required by the GL feed import; document in SYSTEM_PARAMETERS | Finance Systems + DBA | 1 week | GAP-09, TD-79 |
| PGA-10 | Confirm whether `EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC` uses the same PKG_SECURITY key as SSN or a different key; document decrypt procedure path | DBA + Architect | 2 days | VQ-BA-01, BLOCKER-02 |
| PGA-11 | Define PERFORMANCE_REVIEWS calibration workflow: who triggers calibration, mandatory or optional, how CALIBRATED_RATING relates to OVERALL_RATING, does `get_rating_distribution` report pre- or post-calibration ratings | HR Director | 1 week | GAP-05 |
| PGA-12 | Confirm whether dependent inactivation on termination should be immediate or held for COBRA election period (VQ-DEP-04); this decision determines whether terminate_employee touches EMPLOYEE_DEPENDENTS | HR Director + Legal | 3 days | VQ-DEP-04, BLOCKER-03 |
| PGA-13 | Document DBMS_SCHEDULER job topology: which jobs exist, their schedules, and which packages they call; confirm whether sync_org_structure and refresh_reporting_tables are currently scheduled | DBA | 2 days | GAP-13, BR-ORG-02 (false-positive success log risk) |
| PGA-14 | Create dedicated portal database user (HRMS_PORTAL_APP) with EXECUTE-only grants on specific PKG_LEAVE procedures; remove any direct table grants for portal connection; document session-id passing convention | DBA + Architect | 3 days | TD-81, security architecture |
| PGA-15 | Fix HOH (Head of Household) federal tax defect: the current `calculate_employee_pay` returns $0 federal tax for HOH filing status. This is an active financial defect, not a forward-engineering design question | Lead Developer | 1 day | Active defect in production |
| PGA-16 | Fix accrual retry defect in `run_monthly_accrual` (BR-LIB-05): `SET ACCRUED = v_accrued` should be `SET ACCRUED = ACCRUED + v_accrued` in the retry block | Lead Developer | 1 day | Active defect in production |

### Priority Band 3 — Complete Before Production Readiness of Forward-Engineered System

| Action ID | Action | Owner | Estimated Effort | Addresses |
|-----------|--------|-------|-----------------|---------|
| PGA-17 | Establish CI/CD pipeline baseline: build (Forms compilation script), lint (PL/SQL static analysis), SAST (SonarQube or Semgrep), automated deploy to dev/test environments | DevOps | 2–3 weeks | TA Output 8 (0/14 CI/CD capabilities) |
| PGA-18 | Design NACHA ACH file generation: implement PKG_PAYROLL disbursement procedure reading EMPLOYEE_BANK_ACCOUNTS; implement prenote send/validation cycle | Lead Developer | 3–4 weeks | PP-BA-01, PP-BA-03 |
| PGA-19 | Implement COBRA notification: integrate with COBRA administrator or build internal notification generation; connect to NOTIFICATION_QUEUE; handle dependent inactivation sequencing | Lead Developer + HR | 3–4 weeks | BLOCKER-03 |
| PGA-20 | Implement `calculate_final_pay`: build the procedure with proration, PTO payout, and off-cycle payroll run capability | Lead Developer + Payroll | 2–3 weeks | BLOCKER-04 |
| PGA-21 | Fix `change_password` old-password verification gap (DQ-029 / BR-044): add comparison against stored credential before allowing password change | Lead Developer | 1 day | Active security defect |
| PGA-22 | Implement DBMS_SCHEDULER cleanup job for stale USER_SESSIONS (TD-75): sweep every 5 minutes, set STATUS='EXPIRED' for rows exceeding 30-minute timeout | DBA | 2 hours | TD-75 |
| PGA-23 | Add `GL_FEED_SENT_DATE` and `GL_FEED_FILE_NAME` columns to PAYROLL_RUNS; update generate_gl_journal to stamp on successful completion | Lead Developer | 1 day | TD-80 |
| PGA-24 | Elevate salary-grade validation from soft warning to blocking error in both PKG_EMPLOYEE and HRMS_VALIDATION_LIB (TD-74) | Lead Developer | 1 day | TD-74 |
| PGA-25 | Encrypt ROUTING_NUMBER in EMPLOYEE_BANK_ACCOUNTS using same key management solution chosen in PGA-05 | DBA + Lead Developer | 1 day | TD-46, PP-BA-02 |

---

## 6. Confidence Levels per Domain

### 6.1 Business Domain Confidence

**Overall: MEDIUM**

| Sub-domain | Confidence | Evidence | Rationale |
|------------|-----------|---------|-----------|
| Employee Lifecycle (hire, transfer, terminate) | MEDIUM-HIGH | BR-01–BR-30, PKG_EMPLOYEE full recovery | Core rules recovered; COBRA and final pay gaps reduce confidence |
| Payroll Calculation | MEDIUM | BR-31–BR-65, PKG_PAYROLL partial recovery | Tax bracket logic confirmed; HOH defect confirmed; disbursement absent |
| Leave Management | MEDIUM-HIGH | BR-66–BR-85, PKG_LEAVE full recovery | Core logic solid; accrual retry defect identified; FMLA doc enforcement absent |
| Performance Reviews | LOW-MEDIUM | BR-86–BR-107, PKG_PERFORMANCE full recovery | Base review cycle confirmed; calibration workflow entirely absent |
| Benefits / ADP Integration | MEDIUM | BR-DEP-01–BR-DEP-10, export_benefits_feed | Feed logic confirmed; BENEFITS_ENROLLED not filtered (potential ADP data issue) |
| Security / Authentication | LOW | BR-041–BR-045, PKG_SECURITY full recovery | Architecture confirmed but fundamentally defective; cannot represent current intent |
| Reporting | MEDIUM | PKG_REPORTING full recovery | 7 report procedures confirmed; RPT_* refresh stub confirmed |
| Notifications | MEDIUM-HIGH | PKG_NOTIFICATION analysis | Core template/queue/dispatch pattern confirmed; SMS not implemented |

**Why not HIGH:** Fifteen validation-queue items remain UNRESOLVED. These include foundational policy decisions (COBRA, direct deposit, calibration, final pay) that directly determine how the forward-engineered system must behave. Business confidence cannot reach HIGH until these are answered.

### 6.2 Data Domain Confidence

**Overall: MEDIUM**

| Sub-domain | Confidence | Evidence | Rationale |
|------------|-----------|---------|-----------|
| Core HRMS tables (30 confirmed) | HIGH | 01_core_tables.sql, 02_payroll_tables.sql, 04_performance_tables.sql | DDL confirmed; constraints catalogued; PII tagged |
| RPT_* tables (7 inferred) | MEDIUM | Column shapes derived from PKG_REPORTING SELECT lists | No CREATE TABLE statements; shapes are derivable but not confirmed |
| USER_CREDENTIALS | LOW-MEDIUM | Column set inferred from PKG_SECURITY references | DDL not recovered; missing columns (PASSWORD_CHANGED_DATE, LOCKED_UNTIL) are inferred gaps |
| TIME_ATTENDANCE_RECORDS | LOW | 7 columns inferred from CSV comment in PKG_INTEGRATION | No DDL anywhere; destination table may not exist in production |
| PII Inventory | HIGH | 15+ confirmed PII elements across 6 tables | Thorough; encryption gaps (routing number plain text, bank decryption missing) noted |
| Data Quality | HIGH | 32 DQ findings across 3 passes | Comprehensive; cross-validated across tracks |
| Data Flow Map | HIGH | Confirmed for 9 packages; 7 integration flows mapped | Stub flows explicitly marked as non-functional |

**Why not HIGH:** Three tables with no confirmed DDL, 32 active DQ findings, and 46 hidden business rules that deviate from documented behaviour all represent residual uncertainty.

### 6.3 Technology Domain Confidence

**Overall: MEDIUM-HIGH** (confidence in the *assessment*, not in the system's fitness)

| Sub-domain | Confidence | Evidence | Rationale |
|------------|-----------|---------|-----------|
| Technology Stack Identification | HIGH | TA Output 1–3; package headers confirm Oracle 19c, Forms 12c, UTL_FILE, DBMS_CRYPTO, DBMS_SCHEDULER | Stack is fully identified with version pinning |
| Security Vulnerability Map | HIGH | 81 TD items; hard-coded key confirmed by source quote | Comprehensive and cross-validated with DA track |
| CI/CD and Test Infrastructure | HIGH (absence confirmed) | TA Output 8: 0/14 capabilities present | Confidence is in the confirmed *absence* |
| Migration Complexity | MEDIUM-HIGH | MC-01, MC-02b; CONNECT BY, MEDIAN(), DBMS_CRYPTO, Oracle Forms noted | Most risks identified; Oracle Forms compilation dependency is a HIGH risk that may be underestimated |
| Integration Architecture | MEDIUM | 7 integration flows identified; 4 confirmed stubs | Stub status is certain; what the stubs *should* do is partially uncertain |
| Deployment Architecture | LOW | No IaC, no deployment scripts, no documented server topology | Current production infrastructure is entirely undocumented in the repository |

### 6.4 Application Domain Confidence

**Overall: MEDIUM**

| Sub-domain | Confidence | Evidence | Rationale |
|------------|-----------|---------|-----------|
| Happy-path application flows | HIGH | QR-001–QR-015 (Pass 1); application risk register | Core screens and flows are recoverable |
| Edge-case behaviour | LOW-MEDIUM | QR-016–QR-033; 9 HIGH architecture violations | Many edge cases are either absent (calibration, final pay, COBRA) or defective (HOH tax, concurrent session, duplicate email auth) |
| Oracle Forms UI behaviour | MEDIUM | HRMS_EMPLOYEE.xml, HRMS_PAYROLL.xml, HRMS_LOGIN.xml analysis | XML exports capture structure; exact widget behaviour, LOV cascades, and trigger sequences require Forms Builder to confirm |
| Module boundary adherence | MEDIUM | module-boundary-map.json | Boundaries are defined but not always enforced (shared kernel BC-01/BC-07) |
| Component registry completeness | HIGH | component-registry.json; all 9 packages catalogued | Complete with risk flags |

---

## 7. Assumptions Requiring Validation

The following assumptions have been made by the analysis pipeline. If any are incorrect, the corresponding forward engineering artefacts will require revision.

| Assumption ID | Assumption Statement | Domain | Risk if Wrong | Validation Method |
|--------------|---------------------|--------|--------------|-------------------|
| ASM-01 | The hard-coded AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` is the only key used for all AES encryption in the system | Security / Data | Bank account numbers may use a different key; migration plan would need revision | DBA: `SELECT DISTINCT parameter_name FROM SYSTEM_PARAMETERS WHERE parameter_group = 'SECURITY'`; code review of all `PKG_SECURITY` calls |
| ASM-02 | `EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC` uses the same `PKG_SECURITY.encrypt_value` / `decrypt_value` pattern as `EMPLOYEES.SSN_ENCRYPTED` | Data / Payroll | If no decrypt path exists or a different key is used, bank account migration is infeasible | VQ-BA-01: confirm with DBA and security review |
| ASM-03 | All 30 confirmed DDL tables are present in the production Oracle schema | Data | If tables were dropped or renamed in production, migration scripts will fail | DBA: export `ALL_TABLES WHERE OWNER = 'HRMS'` from production |
| ASM-04 | RPT_* tables (7 inferred) have never held production data — reports query OLTP directly in production | Reporting | If RPT_* tables are populated in production, migration must include their data and the refresh mechanism | DBA: `SELECT COUNT(*) FROM RPT_HEADCOUNT` (etc.) in production |
| ASM-05 | `sync_org_structure` and `refresh_reporting_tables` are **not** currently scheduled in production DBMS_SCHEDULER | Operations | If scheduled, they are writing false-success audit log entries on every execution, creating a misleading audit trail | DBA: `SELECT JOB_NAME, ENABLED FROM DBA_SCHEDULER_JOBS WHERE OWNER='HRMS'` |
| ASM-06 | The Oracle Forms `.fmb` compiled files are deployed from the XML exports in the repository, meaning the XML exports are the authoritative source | Application | If undocumented `.fmb` edits were made outside source control, the XML exports do not reflect current production behaviour | Oracle Forms Builder: compile XML exports and diff against deployed `.fmx` files |
| ASM-07 | The self-service portal connects to the Oracle database using the HRMS application schema owner with full privileges | Security | If a restricted portal user already exists, the security gap described in TD-81 may already be mitigated | DBA: enumerate Oracle users and their grants; check `ALL_TAB_PRIVS` |
| ASM-08 | The `GRADE` column in `EMPLOYEES` is the sole driver of RBAC decisions in `PKG_SECURITY.has_permission` | Security | If an additional permission table or role system exists outside the analysed source, the access-control model is incomplete | Full code search for RBAC logic outside `PKG_SECURITY` |
| ASM-09 | Oracle Reports `.rdf` files (referenced in PKG_REPORTING spec as callers) are not in the repository and their structure is unknown | Reporting | If .rdf files contain business logic (calculated columns, query modifications), reporting requirements are underspecified | Locate Oracle Reports .rdf files in the build/deployment directory on the application server |
| ASM-10 | The `SYSTEM_PARAMETERS` table accurately reflects current production configuration values | Configuration | Hard-coded values in code (30-minute session timeout, fiscal year start) override SYSTEM_PARAMETERS in production — the table may have been updated without corresponding code changes | DBA + code review: confirm which parameters are actually read vs. hard-coded |
| ASM-11 | `EMPLOYEE_NUMBER` uniqueness and the `SQ_EMPLOYEE_ID` sequence are coordinated — no manual insertions have created gaps or duplicates | Data Integrity | If gap rows or duplicate employee numbers exist in production, the migration uniqueness constraints will fail | DBA: run uniqueness audit `SELECT EMPLOYEE_NUMBER, COUNT(*) FROM EMPLOYEES GROUP BY EMPLOYEE_NUMBER HAVING COUNT(*) > 1` |
| ASM-12 | The `AUTHENTICATION` path in `PKG_SECURITY` is the only authentication gate — no LDAP, SSO, or Oracle Application Server authentication wraps the Forms application | Security | If Oracle AS / WebGate / LDAP authentication is applied at the infrastructure layer, the authentication stub is not the actual gate | Infrastructure team: confirm whether any middleware authentication exists in front of Oracle Forms |

---

## 8. Open Questions for Business Stakeholders

These questions require answers from HR, Legal, Finance, and operational leadership before forward engineering can proceed. They are not technical questions — the development team cannot make these decisions.

| QID | Question | Domain | Priority | Blocks |
|-----|----------|--------|----------|--------|
| BQ-01 | When an employee is terminated, should the system immediately inactivate their dependents in EMPLOYEE_DEPENDENTS, or hold them active for a COBRA election window (typically 60 days)? What is the company's COBRA administration process and which vendor/system handles notification? | HR / Legal | CRITICAL | BLOCKER-03, PGA-03 |
| BQ-02 | How is employee net pay currently disbursed? Is it via manual ACH file submission, direct bank integration, or a payroll service bureau? What is the intended mechanism in the forward-engineered system? | Finance / Payroll | CRITICAL | BLOCKER-02, PGA-02 |
| BQ-03 | When an employee is terminated mid-pay-period, how is final pay calculated? Is PTO paid out? Are there state-specific rules that apply to the workforce (e.g., California's immediate final pay requirement)? | Payroll / Legal | CRITICAL | BLOCKER-04, PGA-04 |
| BQ-04 | Is the performance rating calibration process (CALIBRATED_RATING column) a current business process that should be implemented in the forward-engineered system? If yes, who runs calibration sessions, is it mandatory per cycle, and does the official rating distribution report use the calibrated or the uncalibrated manager rating? | HR Director | HIGH | GAP-05, PGA-11 |
| BQ-05 | Should all active dependents be exported to ADP in the benefits feed, or only those with BENEFITS_ENROLLED = 'Y'? The current feed exports all active dependents regardless of enrollment flag. | HR / Benefits | HIGH | BR-DEP-05, G-1 (AA track) |
| BQ-06 | Are there currently employees with MARITAL_STATUS = 'HEAD_OF_HOUSEHOLD' in the system? Are they receiving correct payroll? The current system calculates $0 federal income tax for this filing status. | Payroll / Finance | HIGH | Active defect — HOH tax |
| BQ-07 | What is the business intent of the org structure sync capability (`PKG_INTEGRATION.sync_org_structure`)? Is this feature still planned? If yes, what is the source system (Active Directory, LDAP, Workday), and what constitutes the sync scope (departments, reporting lines, job titles)? | HR / IT | MEDIUM | BR-ORG-01–BR-ORG-05 |
| BQ-08 | What is the intended use of the `BENEFITS_ENROLLED` flag on `EMPLOYEE_DEPENDENTS`? No current process reads or enforces it. Is it meant to gate the ADP export, gate benefit cost calculations, or is it a legacy field that should be removed? | HR / Benefits | MEDIUM | BR-DEP-05 |
| BQ-09 | Is the time and attendance import functionality (PKG_INTEGRATION.import_time_attendance) a current operational process or a planned feature? If current, what system generates the CSV file, and where does the imported data go after parsing? | Operations / Payroll | MEDIUM | GAP-01, TIME_ATTENDANCE_RECORDS |
| BQ-10 | Are there employees whose EMPLOYMENT_STATUS is neither ACTIVE, TERMINATED, ON_LEAVE, nor SUSPENDED currently in the production database? The `leave_of_absence` status referenced in one branch of PKG_LEAVE is not in the CHECK constraint. | HR | MEDIUM | Data integrity |
| BQ-11 | What is the intended scope of Head of Household payroll tax handling going forward — should the system implement the correct 2024 federal tax table for this filing status, or is there a reason this population is excluded from federal withholding? | Payroll / Finance / Legal | HIGH | Active defect with potential legal exposure |
| BQ-12 | Does the company have an obligation to implement NACHA prenote (pre-notification) validation for new bank accounts before first ACH disbursement, or does the current process rely on bank account verification through another means? | Finance / Payroll | HIGH | PP-BA-03, NACHA compliance |

---

## 9. Open Questions for Technical Stakeholders

These questions require answers from the DBA team, infrastructure team, and development leads. They are resolvable by examining the production environment.

| QID | Question | Domain | Priority | Blocks |
|-----|----------|--------|----------|--------|
| TQ-01 | What is the confirmed DDL for `USER_CREDENTIALS`, `TIME_ATTENDANCE_RECORDS`, and `EMPLOYEE_PAY_ELEMENTS` in the production schema? Run `DBMS_METADATA.GET_DDL('TABLE', 'USER_CREDENTIALS', 'HRMS')` against production and provide output. | Data / Security | CRITICAL | GAP-01, GAP-02, GAP-03 |
| TQ-02 | Is `sync_org_structure` scheduled in production DBMS_SCHEDULER? Run `SELECT JOB_NAME, ENABLED, LAST_RUN_DATE, NEXT_RUN_DATE FROM DBA_SCHEDULER_JOBS WHERE OWNER='HRMS'` and share the output. Every scheduled execution logs a false `'Org structure sync completed'` success message. | DBA / Operations | CRITICAL | BR-ORG-02, false audit trail |
| TQ-03 | What is the current production deploy process for PL/SQL packages? Is it SQL*Plus scripts applied by the DBA, Oracle SQL Developer, or another tool? Is there a change control log? | DBA / DevOps | HIGH | CI/CD gap context |
| TQ-04 | What is the confirmed decryption path for `EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC`? Does `PKG_SECURITY.decrypt_value` cover this column, or is there a separate procedure? If no decrypt procedure exists, the bank account data is effectively locked (unreadable) and migration requires the original key and a new decrypt implementation. | DBA / Lead Developer | CRITICAL | BLOCKER-02, PGA-10 |
| TQ-05 | Do the RPT_* tables (RPT_HEADCOUNT, RPT_COMPENSATION, RPT_TURNOVER, RPT_NEW_HIRES, RPT_LEAVE_UTILIZATION, RPT_PAYROLL_SUMMARY, RPT_EEO_COMPLIANCE) exist in the production schema, and do they contain any data? `refresh_reporting_tables` is confirmed as a no-op stub. | DBA | HIGH | GAP, RPT_* inferred table confidence |
| TQ-06 | What server infrastructure runs the Oracle Forms application? Is there an Oracle Application Server / WebLogic instance, or is Oracle Forms running in standalone mode? Does any middleware (Oracle Access Manager, WebGate, reverse proxy) sit in front of it? | Infrastructure | HIGH | ASM-12, authentication model |
| TQ-07 | Are there Oracle Reports `.rdf` files in the application server deployment directory? These are referenced in `PKG_REPORTING.pks` as callers of the report procedures. Their content is not in the repository. | DBA / App Server Admin | MEDIUM | GAP-12 |
| TQ-08 | What Oracle DB user does the self-service portal use to connect? What grants does that user have? `SHOW GRANTS FOR <portal_user>` or `SELECT * FROM DBA_SYS_PRIVS WHERE GRANTEE='<portal_user>'` | DBA | HIGH | TD-81, ASM-07 |
| TQ-09 | What is the confirmed Oracle Financials GL Journal Source name and Journal Category values expected by the GL import process? The HRMS GL feed generates files without this information explicitly documented. | Finance Systems DBA | HIGH | GAP-09, TD-79 |
| TQ-10 | Does the production database have any active foreign-key violations or orphan rows? Run the referential integrity audit script (check EMPLOYEE_DEPENDENTS for orphaned EMP_IDs, PAYROLL_DETAILS for orphaned RUN_IDs, LEAVE_BALANCES for orphaned EMP_IDs). | DBA | MEDIUM | Data migration risk assessment |
| TQ-11 | What is the actual Oracle version and patch level in production? The analysis assumes Oracle 19c based on package compilation requirements. Confirm: `SELECT BANNER FROM V$VERSION`. | DBA | MEDIUM | Migration platform compatibility |
| TQ-12 | Are there any database triggers on `EMPLOYEES` or `EMPLOYEE_DEPENDENTS` beyond the audit triggers identified? `SELECT TRIGGER_NAME, TRIGGERING_EVENT, STATUS FROM ALL_TRIGGERS WHERE TABLE_NAME IN ('EMPLOYEES','EMPLOYEE_DEPENDENTS')` | DBA | MEDIUM | Behaviour completeness |
| TQ-13 | What is the current production AES key rotation policy? Is the key `HR$ystem_3ncrypt10n_K3y_2024!!` the original deployment key, or has it been rotated? How many records in production contain ciphertext encrypted with this key? | DBA / CISO | CRITICAL | BLOCKER-05, key rotation planning |
| TQ-14 | Are there any Oracle Database Vault policies, Fine-Grained Auditing rules, or Virtual Private Database (VPD) policies in the production schema that are not visible in the application source code? | DBA | MEDIUM | Behaviour completeness, security model |

---

## 10. Risk Assessment for Forward Engineering

### 10.1 Risk Register Summary

| Risk ID | Risk | Likelihood | Impact | Severity | Mitigation |
|---------|------|-----------|--------|---------|-----------|
| FE-RISK-01 | Forward-engineered system inherits authentication bypass if BLOCKER-01 is not resolved | HIGH | CRITICAL | CRITICAL | Do not generate authentication module until PGA-01 is complete |
| FE-RISK-02 | Bank account data is unreadable if `ACCOUNT_NUMBER_ENC` decrypt path is not confirmed before migration | MEDIUM | CRITICAL | CRITICAL | Confirm decrypt path (TQ-04) before writing migration scripts |
| FE-RISK-03 | COBRA compliance gap continues in forward-engineered system if BQ-01/PGA-03 unresolved | HIGH | CRITICAL | CRITICAL | Federal legal exposure; must be resolved before termination workflow is generated |
| FE-RISK-04 | Hard-coded AES key is in source control history; even after rotation, historical commits expose the key | HIGH | HIGH | HIGH | Evaluate git history scrub; confirm whether key has been used for production data accessible to unauthorised parties |
| FE-RISK-05 | Oracle Forms UI behaviour cannot be fully verified without compiled .fmb files | MEDIUM | HIGH | HIGH | Prioritise forms testing; consider Oracle Forms → APEX or web migration as scope question |
| FE-RISK-06 | Time attendance records have no DDL — generated import integration cannot be validated | MEDIUM | HIGH | HIGH | Obtain DDL from production (TQ-01); do not generate import integration without confirmed schema |
| FE-RISK-07 | `calculate_employee_pay` truncation in source means payroll element logic may be partially missing from the analysis | MEDIUM | HIGH | HIGH | Obtain complete PKG_PAYROLL source from production before generating payroll module |
| FE-RISK-08 | Oracle MEDIAN() aggregate in PKG_REPORTING has no direct PostgreSQL/SQL Server equivalent if platform migration is in scope | MEDIUM | MEDIUM | HIGH | Resolve target platform decision before generating reporting module; document MEDIAN() → PERCENTILE_CONT(0.5) translation |
| FE-RISK-09 | RPT_* table data model is inferred — if actual DDL differs from column shapes derived from SELECT lists, generated migration will fail | LOW | MEDIUM | MEDIUM | Confirm RPT_* DDL from production (TQ-05) before generating reporting tables |
| FE-RISK-10 | Stale FMLA seed data (REQUIRES_DOCUMENT='N') may be exploited if forward-engineered system retains this configuration | MEDIUM | MEDIUM | MEDIUM | Correct seed data in PGA-17 data load scripts |
| FE-RISK-11 | CONNECT BY hierarchy performance degrades above 500 employees; forward-engineered system may use same pattern if not explicitly redesigned | MEDIUM | MEDIUM | MEDIUM | Define employee headcount target; use recursive CTE or materialised path for organisations above 500 |
| FE-RISK-12 | Duplicate email address in EMPLOYEES causes silent wrong-user login (BR-043b); this defect must not be carried forward | LOW | HIGH | HIGH | Add unique constraint on EMAIL before migration; audit for existing duplicates (TQ-10) |
| FE-RISK-13 | No regression test baseline means forward-engineered system correctness cannot be objectively verified against current behaviour | HIGH | HIGH | HIGH | PGA-06 is a prerequisite for any generation sprint |
| FE-RISK-14 | Multiple stub procedures (sync_org_structure, refresh_reporting_tables, import_time_attendance) log false success; if monitoring alerts are based on these log entries, they will miss actual failures | HIGH | MEDIUM | HIGH | Add `-- STUB` annotation and change log message to `'NOT_IMPLEMENTED'` before generation; TQ-02 must be answered |

### 10.2 Compliance Risk Summary

| Compliance Area | Current Status | Risk Level | Required Action |
|----------------|---------------|-----------|----------------|
| ERISA / COBRA | Non-compliant — every termination is an unreported qualifying event | CRITICAL | PGA-03 + PGA-19 |
| NACHA ACH | Non-compliant — prenote not implemented; disbursement absent | CRITICAL | PGA-02 + PGA-18 |
| NIST SP 800-63B (Password) | Non-compliant — MD5 hashing; no lockout; auth bypass | CRITICAL | PGA-01 + PGA-07 |
| IRS Payroll Tax (HOH) | Non-compliant — $0 federal tax withheld for HOH filing status | HIGH | PGA-15 |
| FMLA Documentation | Non-compliant — REQUIRES_DOCUMENT='N' for FMLA | MEDIUM | TD-72 / seed data correction |
| SOX / Financial Controls | At risk — no GL_FEED_SENT_DATE; no audit trail on payroll disbursement | HIGH | PGA-23 |
| Data Privacy (PII) | At risk — plain-text routing numbers; hard-coded encryption key | HIGH | PGA-05 + PGA-25 |
| EEO Reporting | Potential gap — gender CHECK constraint absent; reporting reads wrong column if calibration intended | MEDIUM | TD-40 / BQ-04 |

---

## 11. Recommended Pilot / POC Scope

Given the breadth of issues identified, a full-system forward engineering attempt without validation would be high-risk. The recommended approach is a **three-phase scoped POC** designed to validate the forward engineering pipeline against lower-risk modules before committing to the full HRMS scope.

### Phase 1 POC: Leave Management Module (4–6 weeks)

**Why this module:** `PKG_LEAVE` is the most self-contained bounded context (BC-03). It has no critical blockers, no compliance dependencies beyond FMLA (a medium-priority item), no financial transaction risk, and a well-defined data model (`LEAVE_BALANCES`, `LEAVE_REQUESTS`, `LEAVE_TYPES`). The business rules are largely complete (BR-66–BR-85 plus BR-LIB-01–BR-LIB-10), and the two known defects (accrual retry bug BR-LIB-05, FMLA doc gap) are easily fixable and provide a concrete demonstration of defect correction through forward engineering.

**POC Deliverables:**
- Generated data model for BC-03 on target platform
- Generated service layer for `submit_leave_request`, `approve_leave_request`, `run_monthly_accrual`, `initialize_balances`
- Fix for BR-LIB-05 (accrual retry defect) demonstrated in generated code
- FMLA documentation enforcement implemented (upgrading from no-op to blocking validation)
- Unit test suite covering happy-path and the three known edge cases
- Migration script for `LEAVE_BALANCES`, `LEAVE_REQUESTS`, `LEAVE_TYPES` from Oracle 19c

**Success Criteria:**
- All business rules BR-66–BR-85 verifiably implemented in the generated module
- BR-LIB-05 defect not present in generated code
- Unit test coverage ≥ 80% on service layer
- Migration script executes successfully in a test environment against production data extract

---

### Phase 2 POC: Employee Identity Module (6–8 weeks)

**Why this module:** BC-01 is the root aggregate; validating it second ensures that downstream modules (Compensation, Performance, Leave) can be built on a solid foundation. It is more complex than Leave (self-referential MANAGER_ID hierarchy, termination workflow, grade-based RBAC interaction) but has no unsolvable blockers once PGA-04 (final pay rules) and PGA-03 (COBRA policy) are resolved.

**POC Deliverables:**
- Generated data model for EMPLOYEES, DEPARTMENTS, JOB_POSITIONS with hierarchy support (recursive CTE replacing CONNECT BY)
- Generated service layer for `create_employee`, `transfer_employee`, `terminate_employee` (with COBRA notification stub wired to notification queue)
- Authentication service using target credential store (bcrypt if local; LDAP/OIDC adapter if federated) — replacing the auth bypass
- Migration scripts for EMPLOYEES, DEPARTMENTS, JOB_POSITIONS with PII re-encryption using new key management
- Duplicate EMAIL audit and unique constraint addition

**Dependency:** BLOCKER-01 (auth model), BLOCKER-03 (COBRA policy), BLOCKER-05 (key management) must be resolved before Phase 2 starts.

---

### Phase 3 POC: Payroll Calculation Module (8–10 weeks)

**Why this module last in POC sequence:** Payroll is the highest-risk module due to financial implications, the missing disbursement procedure, the HOH tax defect, the `calculate_final_pay` gap, and the dependency on bank account decryption. By the time Phase 3 begins, Phases 1 and 2 will have validated the forward engineering pipeline approach and resolved the key management and authentication blockers.

**POC Deliverables:**
- Generated `calculate_payroll` / `calculate_employee_pay` with corrected HOH tax handling
- Generated `calculate_final_pay` (new procedure) based on business rules resolved in PGA-04
- Generated NACHA ACH file generation reading `EMPLOYEE_BANK_ACCOUNTS` (post prenote validation)
- Migration scripts for PAYROLL_RUNS, PAYROLL_DETAILS, SALARY_RECORDS, DEDUCTION_RECORDS
- Bank account re-encryption using new key management (tied to Phase 2 PGA-05 output)
- GL feed with `GL_FEED_SENT_DATE` stamping

**Dependency:** PGA-02 (disbursement mechanism), PGA-04 (final pay rules), PGA-18 (NACHA design), BLOCKER-05 (key management) must be resolved.

---

### Modules Excluded from POC Scope (Deferred to Full Implementation)

| Module | Reason for Deferral |
|--------|-------------------|
| Performance Reviews — Calibration | BQ-04 not answered; calibration workflow undefined |
| Org Structure Sync (LDAP) | Complete stub; requires external system integration design |
| Time & Attendance Import | No DDL; destination table architecture undefined |
| RPT_* Reporting Refresh | Nightly refresh is a stub; requires decision on reporting architecture (OLTP-direct vs. materialised layer) |

---

## 12. Go / No-Go Recommendation with Conditions

### Current Status: **NO-GO**

The system analysis is complete and the knowledge base is sufficiently rich to support forward engineering. However, **seven critical blockers** and **twelve open technical questions** represent risks that would compromise the quality, compliance posture, and security of any system generated today.

A code generation sprint started without resolving these would produce a system that:
1. Has no real authentication gate (BLOCKER-01)
2. Cannot disburse payroll electronically (BLOCKER-02)
3. Violates federal COBRA law on every termination (BLOCKER-03)
4. Cannot calculate final pay for terminated employees (BLOCKER-04)
5. Carries a compromised encryption key into the new system (BLOCKER-05)
6. Has no regression baseline to validate against (BLOCKER-06)
7. Stores passwords in a broken hash format (BLOCKER-07)

Each of these is a **go-live disqualifier**, not a post-launch improvement. Generating code now and addressing these later would require fundamental rework, not incremental remediation.

---

### Conditions for GO Decision

A GO decision is authorised when the following conditions are met. They are grouped into **Gate 1** (must be met before any generation begins) and **Gate 2** (must be met before the POC is expanded to production scope).

#### Gate 1 — Prerequisite for Generation Start

| Condition | Owner | Target Date | Verification |
|-----------|-------|-------------|--------------|
| G1-C01: Authentication model decision documented and signed off (BLOCKER-01) | CISO + Architecture | TBD | Architecture Decision Record published |
| G1-C02: Direct deposit disbursement mechanism confirmed in writing (BLOCKER-02) | Finance / Payroll Director | TBD | Integration specification or deferral decision document |
| G1-C03: COBRA notification policy defined with Legal sign-off (BLOCKER-03) | HR Director + Legal | TBD | Policy document with timing, recipients, delivery channel |
| G1-C04: `calculate_final_pay` business rules documented (BLOCKER-04) | Payroll Manager | TBD | Business rules document covering proration, PTO, state law |
| G1-C05: Key management solution selected; re-encryption plan drafted (BLOCKER-05) | CISO + DBA | TBD | Architecture Decision Record + migration plan |
| G1-C06: utPLSQL (or equivalent) test framework installed; smoke tests passing for 5 core procedures (BLOCKER-06) | Lead Developer | TBD | CI build with passing test report |
| G1-C07: Secret scanner active in repository; hard-coded AES key removed from current branch (BLOCKER-07) | DevSecOps | TBD | Clean scan report + confirmed key rotation |
| G1-C08: Confirmed DDL for USER_CREDENTIALS, EMPLOYEE_PAY_ELEMENTS provided by DBA (TQ-01) | DBA | TBD | `DBMS_METADATA.GET_DDL` output reviewed by Architect |
| G1-C09: Production schema table list confirmed — all 30 tables plus RPT_* existence verified (TQ-05) | DBA | TBD | `SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER='HRMS'` output |
| G1-C10: HOH tax defect (PGA-15) and accrual retry defect (PGA-16) patched in current production system | Lead Developer | TBD | Deployed patch confirmed by Payroll Manager |

#### Gate 2 — Prerequisite for Production Scope Expansion

| Condition | Owner | Target Date | Verification |
|-----------|-------|-------------|--------------|
| G2-C01: Phase 1 POC (Leave Management) complete with all success criteria met | Architecture + Dev | TBD | POC review sign-off |
| G2-C02: Calibration workflow business rules defined and signed off (BQ-04) | HR Director | TBD | Business rules document |
| G2-C03: ADP benefits feed BENEFITS_ENROLLED filtering policy confirmed (BQ-05) | HR / Benefits | TBD | Written policy decision |
| G2-C04: Oracle GL Journal Source and Journal Category values confirmed (TQ-09) | Finance Systems DBA | TBD | GL integration specification |
| G2-C05: Self-service portal database user and grant model redesigned and deployed (PGA-14) | DBA + Architect | TBD | Grant script deployed; penetration test of portal completed |
| G2-C06: Full CI/CD pipeline operational for development environment (PGA-17) | DevOps | TBD | Pipeline status page with passing build |

---

### Summary Recommendation

| Dimension | Status | Condition |
|-----------|--------|-----------|
| Analysis Quality | ADEQUATE | Knowledge base supports generation once blockers are resolved |
| Security Posture | NOT READY | Authentication bypass, hard-coded key, MD5 hashing must be resolved |
| Compliance Posture | NOT READY | COBRA, NACHA prenote, HOH tax are active compliance exposures |
| Data Readiness | CONDITIONAL | 30/30 confirmed tables adequate; 3 inferred/absent tables need DDL confirmation |
| Delivery Infrastructure | NOT READY | 0/14 CI/CD capabilities; no test baseline |
| Business Rules Completeness | CONDITIONAL | 15 VQ items unresolved; core rules are recoverable |
| **Overall** | **NO-GO → CONDITIONAL GO** | **Estimated 4–6 weeks to resolve Gate 1 conditions; then Phase 1 POC can begin** |

The recommended path is:
1. Resolve Gate 1 conditions in parallel over 4–6 weeks (all 10 conditions can be worked concurrently by different owners)
2. Begin Phase 1 POC (Leave Management) immediately after Gate 1 is cleared
3. Resolve outstanding BQ and TQ items during Phase 1 (most are independent of the Leave module)
4. Begin Phase 2 POC (Employee Identity) after Phase 1 success criteria are met and BLOCKER-01/03/05 are resolved
5. Begin Phase 3 POC (Payroll) after Phase 2 and BLOCKER-02/04 are resolved
6. Gate 2 conditions are typically achievable during Phase 2–3 execution

With this sequencing, a production-ready forward-engineered system is achievable within **16–22 weeks** of Gate 1 clearance, assuming standard development team capacity and no new blockers surfaced during DBA fact-finding.

---

*Report compiled from: BA_Deep_Analyst.md (merged, 140 BRs), BA_Deep_Analyst_Edge.md (supplemental extractions), DA_Data_Reviewer.md (3 passes, DQ-001–DQ-032), TA_Deep_Analyst.md (TD-01–TD-81), AA_Quality_Review.md (QR-001–QR-033), cross-validation supplements (14 gaps resolved), domain-model.md, data-dictionary.md, schema-catalogue.json, component-registry.json, application-risk-register.json, architecture-violation-register.json, migration-complexity.json.*

*Solution Architect sign-off required before this document is used to initiate code generation.*
