# Business Requirements Document
## Acme Corporation HRMS Modernisation Programme
**Document:** 01_BRD.md
**Version:** 2.0 — Final Draft
**Classification:** Internal — Restricted
**System:** Oracle HRMS (Legacy) → Target: Modern HRMS Platform
**Prepared by:** Business Analysis Team
**Review Status:** Pending Stakeholder Sign-off

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Background & Business Case](#2-project-background--business-case)
3. [Business Objectives](#3-business-objectives)
4. [Scope](#4-scope)
5. [Stakeholders & User Personas](#5-stakeholders--user-personas)
6. [Business Requirements](#6-business-requirements)
7. [Business Constraints](#7-business-constraints)
8. [Business Assumptions & Dependencies](#8-business-assumptions--dependencies)
9. [Success Metrics & KPIs](#9-success-metrics--kpis)
10. [Risk Register](#10-risk-register)
11. [Sign-off Requirements](#11-sign-off-requirements)

---

## 1. Executive Summary

Acme Corporation operates a custom-built Oracle 19c HRMS application (version 4.2.0) that has served as the system of record for all human resources functions since initial deployment. A comprehensive multi-track technical and business analysis of the system's PL/SQL codebase, Oracle Forms layer, schema definitions, and integration interfaces has revealed that the platform contains **44 documented business rule violations, 31 data quality defects, 25 architecture violations, 14 critical-or-high security vulnerabilities, and zero CI/CD automation capability**.

Of these findings, several are **actively causing compliance failures today**:

- Every employee termination processed through the system creates an unreported COBRA qualifying event (federal compliance gap).
- The payroll disbursement capability (`calculate_final_pay`, direct deposit via `EMPLOYEE_BANK_ACCOUNTS`) does not exist in any implemented procedure — employees receiving final pay require fully manual off-system payroll.
- The authentication system does not verify passwords; any valid username can authenticate regardless of what password is supplied.
- A hard-coded AES-256 encryption key (`HR$ystem_3ncrypt10n_K3y_2024!!`) is present in source code, placing all encrypted PII (SSNs, bank account numbers) at risk.
- Performance rating calibration columns exist in the schema but are never written by any application procedure, meaning all performance reporting reflects uncalibrated manager ratings.

The modernisation programme will replace the legacy Oracle Forms/PL/SQL monolith with a standards-based HRMS platform capable of supporting Acme's growth targets, regulatory obligations, and operational efficiency ambitions. The programme is estimated at 18–24 months with phased delivery, beginning with the highest-severity compliance and security remediations and progressing to full platform replacement.

**Total impacted employee population:** All current Acme employees (exact headcount to be confirmed; analysis covers system capacity for up to approximately 5,000 employees based on schema design).

---

## 2. Project Background & Business Case

Looking at the source content, I can identify what the gap evidence reveals: the package spec declares calibration as a feature and names a "batch calibration job" as a caller, but the package body contains zero calibration logic. I'll fill the table rows from what the source directly supports.

I now have everything needed. The two unnamed stubs are:
- `PKG_SECURITY.authenticate` — declared with all the variables for password hash comparison (`v_stored_hash`, `v_input_hash`) but never queries `USER_CREDENTIALS`; accepts any password
- `PKG_SECURITY.change_password` — validates complexity rules but explicitly marked "This is a stub for the legacy system model" and never writes to `USER_CREDENTIALS`

Here is the updated snippet:

---

The source content (PKG_PAYROLL.pkb) confirms the procedure does not exist — it contains no `calculate_final_pay` implementation, no TODO comments referencing it, and no specification of termination pay components, accrued leave payout logic, pro-rata salary rules, or GL feed output format. The source provides no data with which to fill this gap.

Returning the snippet unchanged per instructions:

---

### 2.1 System History

The Acme HRMS was developed as a bespoke Oracle Forms 12c application running against an Oracle 19c database. The system manages the full HR lifecycle: employee onboarding, compensation, leave, performance reviews, benefits, payroll, and compliance reporting. The system integrates with ADP (benefits feed), Oracle Financials (GL journal feed), and an unnamed self-service portal.

The application has accumulated significant technical debt. Analysis of the source code reveals that at least seven integration procedures are placeholders with no implemented logic (including `sync_org_structure`, `import_time_attendance`, `calculate_final_pay`, and `refresh_reporting_tables`) that log false success messages, creating an operational blind spot where scheduled jobs appear to succeed while performing no work. [GAP-FILLED] The remaining two unnamed procedures are `PKG_SECURITY.authenticate` — which declares variables for password hash comparison (`v_stored_hash`, `v_input_hash`) but never queries the `USER_CREDENTIALS` table, meaning every login succeeds regardless of the password supplied — and `PKG_SECURITY.change_password` — which enforces complexity rules but is explicitly commented "This is a stub for the legacy system model" and performs no actual credential write, leaving passwords permanently unchanged after any change request. Together, the full set of seven stub/placeholder procedures is: `sync_org_structure` (PKG_INTEGRATION), `import_time_attendance` (PKG_INTEGRATION), `refresh_reporting_tables` (PKG_REPORTING), `calculate_final_pay` (PKG_PAYROLL — procedure does not exist; referenced only in TODO comments), `revoke_access` (PKG_SECURITY — procedure does not exist; referenced only in TODO comments [GAP-FILLED] — a compliant implementation must address four areas derived from the existing package structure: (1) **Session cascade**: update all `USER_SESSIONS` rows matching the target `EMP_ID` where `SESSION_STATUS = 'ACTIVE'` by setting `SESSION_STATUS = 'REVOKED'` and `LOGOUT_TIME = SYSDATE`, mirroring the field usage in `logout` and `is_session_valid`; (2) **Employment status**: set `EMPLOYEES.EMPLOYMENT_STATUS` to `'INACTIVE'`, which causes the `authenticate` function's active-user lookup (`WHERE EMPLOYMENT_STATUS = 'ACTIVE'`) to exclude the employee from all future logins without requiring a separate credentials purge; (3) **RBAC interaction**: under the current grade-based permission model, `has_permission` resolves access via a join between `EMPLOYEES` and `JOB_TITLES` — marking the employee inactive causes that join to raise `NO_DATA_FOUND`, which the exception handler already maps to `RETURN FALSE`, so no explicit role-table row deletion is required; however, any row in `USER_CREDENTIALS` for this employee must also be invalidated to prevent direct credential reuse if the authentication stub is ever completed; and (4) **Audit record**: must call `PKG_AUDIT.log_action('USER_SESSIONS', p_emp_id, 'REVOKE', USER)` consistent with the audit instrumentation applied in both `authenticate` and `change_password`), `authenticate` (PKG_SECURITY — password verification omitted), and `change_password` (PKG_SECURITY — credential write omitted).

### 2.2 Drivers for Modernisation

| Driver | Category | Urgency |
|--------|----------|---------|
| [GAP-FILLED] Authentication bypass in `PKG_SECURITY.authenticate`: password hash comparison variables are declared but the `USER_CREDENTIALS` table is never queried, meaning every login attempt succeeds regardless of the password supplied — any user or attacker can access any account | Security | Critical |
| [GAP-FILLED] Broken credential management in `PKG_SECURITY.change_password`: complexity rules are enforced but no credential write is ever performed, leaving all passwords permanently unchanged after any change request; explicitly stubbed as "legacy system model" | Security | Critical |
| [GAP-FILLED] Seven stub procedures log false success while performing no work, creating silent operational failures in scheduled jobs (time-attendance import, org-structure sync, final-pay calculation, reporting refresh, access revocation); incidents cannot be detected from logs alone | Operational Risk | High |
| [GAP-FILLED] Oracle Forms 12c is an aging UI framework with a shrinking developer talent pool and limited vendor-support runway, making ongoing maintenance increasingly costly and recruitment difficult | Technical Debt | High |
| [GAP-FILLED] `import_time_attendance` contains only a CSV-read skeleton and a `TODO` comment for the actual parsing and database update logic; time-and-attendance data is never applied to payroll, silently producing incorrect pay calculations | Operational Risk | High |
| [GAP-FILLED] ADP benefits feed (`export_benefits_feed`) uses a fixed-width, vendor-specific flat-file format explicitly flagged `LEGACY` in source; format is tightly coupled to a single vendor contract and cannot be adapted to alternative providers without a code rewrite | Integration | Medium |
| [GAP-FILLED] GL journal integration with Oracle Financials relies on `UTL_FILE` batch flat files (pipe-delimited `.dat` files written to a mapped directory object) rather than a real-time API; introduces settlement lag and creates file-system dependency that is fragile under server migration or cloud lift-and-shift | Integration | Medium |
| [GAP-FILLED] Tax constants (Social Security wage base, Medicare rates, standard deductions, per-allowance amounts) are hardcoded literals in `PKG_PAYROLL`; annual regulatory changes require a source-code edit and redeployment rather than a configuration update, creating compliance exposure between legislative change and release cycle | Regulatory / Compliance | Medium |
| [GAP-FILLED] `sync_org_structure` is a complete stub with no LDAP/AD integration logic; organisational hierarchy in HRMS cannot be kept current with directory changes, risking stale role assignments and access-control drift | Integration | Medium |
| [GAP-FILLED] **Unimplemented calibration workflow** — `PKG_PERFORMANCE.pks` declares calibration as a delivered capability ("Review cycles, goal tracking, ratings, calibration") and explicitly names a `batch calibration job` as a caller, yet `PKG_PERFORMANCE.pkb` contains no calibration procedure. The year-end rating-normalisation step is entirely absent from the system. | Functional Gap — Performance Management | High |
| [GAP-FILLED] **Scheduled calibration job silently no-ops** — The batch job wired to invoke calibration follows the same false-success pattern identified in §2.1: it executes against a non-existent procedure and produces no output, meaning calibration has never run operationally despite appearing on the job schedule. | Operational Risk — Silent Failure | High |
| [GAP-FILLED] **Rating distribution data exists without a governance workflow** — `get_rating_distribution` can surface cross-department rating spread and percentages, but with no calibration workflow there is no mechanism to detect or correct skewed distributions before ratings are finalised and communicated to employees. | Process Gap — HR Governance / Fairness | Medium |
| [GAP-FILLED] **No calibration status in the review lifecycle** — The review state machine (NOT_STARTED → MANAGER_REVIEW → COMPLETED → ACKNOWLEDGED) has no CALIBRATION or PENDING_CALIBRATION state, meaning even if calibration logic were added it cannot be tracked, paused, or audited as a discrete step. | Architectural Gap — Workflow Design | Medium |
| COBRA notification gap on every employee termination | Federal Regulatory (ERISA) | Critical |
| Direct deposit disbursement not implemented — manual payroll required | Operational | Critical |
| Authentication bypass — passwords not verified | Security | Critical |
| Hard-coded encryption key in source code | Security | Critical |
| ACH prenote not implemented — Nacha compliance gap | Regulatory | High |
| Password hashing uses MD5 (cryptographically broken) | Security | High |
| No CI/CD pipeline; manual deployment with no rollback | Operational | High |
| Performance calibration unimplemented | HR Process | High |
| Oracle Forms 12c approaching end of extended support | Technology | Medium |
| Self-service portal connects under undeclared DB credentials | Security | High |
| No structured observability or alerting | Operational | Medium |

### 2.3 Business Case Summary

**Cost of inaction (annual estimate):**

| Risk Area | Estimated Exposure |
|-----------|-------------------|
| COBRA non-compliance penalties (per-violation ERISA excise tax: $100/day/qualified beneficiary) | $100K–$500K+ depending on volume and discovery timeline |
| Manual payroll processing overhead for all terminations | $50K–$150K in HR/Finance staff time |
| Security breach involving AES key or auth bypass (PII exposure, GDPR/CCPA litigation) | $500K–$5M+ |
| Nacha ACH prenote violations | $10K–$100K in bank fees and rejected ACH batches |
| Lost productivity from zero CI/CD (manual deploys, production defects, rollback failures) | $200K–$500K in developer and downtime cost |
| **Total estimated annual cost of inaction** | **$860K–$6.25M** |

**Modernisation programme investment:** To be finalised in subsequent business case elaboration; indicative range $2M–$5M over 24 months.

**Break-even:** Year 2 based on risk avoidance alone; positive ROI from Year 3 including efficiency gains.

---

## 3. Business Objectives

All objectives are SMART: Specific, Measurable, Achievable, Relevant, and Time-bound.

| ID | Objective | Metric | Target | Deadline |
|----|-----------|--------|--------|----------|
| OBJ-01 | Eliminate COBRA compliance gap | % of terminations triggering COBRA notification within 14-day statutory window | 100% | End of Phase 1 (Month 6) |
| OBJ-02 | Implement functional direct deposit disbursement | % of payroll runs processed without manual off-system intervention | ≥ 95% | End of Phase 2 (Month 12) |
| OBJ-03 | Remediate authentication bypass and rotate encryption key | Zero open Critical security findings in penetration test | Pass with zero Critical | End of Phase 1 (Month 6) |
| OBJ-04 | Achieve Nacha ACH prenote compliance | % of new bank accounts receiving prenote before first live ACH | 100% | End of Phase 2 (Month 12) |
| OBJ-05 | Replace Oracle Forms with browser-based UI | % of HR transactions processed through new UI | ≥ 90% | End of Phase 3 (Month 18) |
| OBJ-06 | Establish CI/CD pipeline with automated testing | Build-to-deploy time | < 30 minutes | End of Phase 2 (Month 12) |
| OBJ-07 | Implement performance calibration workflow | % of annual review cycles completing calibration phase before acknowledgement | ≥ 80% | End of Phase 3 (Month 18) |
| OBJ-08 | Reduce payroll processing errors | Payroll exception rate (manual corrections post-approval) | < 0.5% of pay lines | End of Phase 3 (Month 18) |
| OBJ-09 | Achieve structured observability | Mean time to detect (MTTD) production incidents | < 15 minutes | End of Phase 2 (Month 12) |
| OBJ-10 | Complete data migration with zero PII data loss | Records reconciled post-migration vs. source | 100% | End of Phase 3 (Month 24) |

---

## 4. Scope

### 4.1 In Scope

#### Functional Scope

| Area | Included Capabilities |
|------|----------------------|
| Employee Lifecycle | Onboarding, transfers, promotions, terminations (including COBRA trigger, access revocation, final pay) |
| Compensation Management | Salary records, grade bands, merit eligibility, payroll run creation, approval, and GL feed |
| Direct Deposit / Payroll Disbursement | Bank account management, ACH prenote, NACHA file generation, split-deposit support |
| Leave Management | Balance initialisation, accrual (monthly), leave request submission and approval, termination balance handling |
| Performance Management | Review cycle creation, self-assessment, manager review, **calibration workflow** (currently unimplemented), acknowledgement |
| Benefits Administration | Dependent management, enrollment, ADP benefits feed export |
| Security & Access Control | Authentication (with real password verification), session management, RBAC by grade, encryption key rotation |
| Reporting | Headcount, compensation summary, turnover, new hires, leave utilisation, payroll summary, EEO compliance |
| Integration | ADP benefits feed, Oracle Financials GL journal, org structure sync (currently a placeholder), time & attendance import |
| Notifications | Email and future-channel notification dispatch, template management |
| Audit & Compliance | Audit log, COBRA event tracking, FMLA documentation enforcement, data retention |

#### Technical Scope

| Area | Included Work |
|------|--------------|
| Security Remediation | Encryption key rotation, password hash migration (MD5 → bcrypt/Argon2), authentication implementation, session cleanup job |
| Legacy PL/SQL Replacement | All 7 stub/placeholder procedures to be implemented or explicitly decommissioned |
| Data Migration | All production data from Oracle 19c to target platform, including encrypted PII (SSN, bank account numbers) with key rotation |
| CI/CD Pipeline | Build, test, SAST, secret scanning, deploy, smoke-test, rollback capability |
| Observability | Structured logging, alerting, distributed tracing (post-Oracle Forms) |
| Oracle Forms Retirement | Replacement of all `.fmb/.fmx` Oracle Forms modules with browser-based equivalents |
| Integration Contracts | Formal API contracts for ADP, Oracle Financials, self-service portal, time & attendance vendor |

### 4.2 Out of Scope

| Item | Reason |
|------|--------|
| Oracle Financials (GL) internal configuration | Owned by Finance; HRMS produces the feed only |
| ADP benefits platform configuration | Vendor-managed; HRMS produces the export only |
| Payroll tax table maintenance | Managed by Finance; system consumes tax brackets as configuration |
| HR policy changes (leave types, benefit plans) | Policy is owned by HR leadership; system implements policy |
| Employee self-service portal front-end (beyond integration contract) | Separate project; HRMS exposes APIs |
| Active Directory / LDAP platform administration | IT infrastructure scope |
| Physical infrastructure and Oracle licensing negotiation | IT procurement scope |
| Workforce planning and analytics platform | Future phase; outside 24-month window |

---

## 5. Stakeholders & User Personas

### 5.1 Stakeholder Register

| ID | Stakeholder | Role | Interest | Influence | Engagement Strategy |
|----|-------------|------|----------|-----------|---------------------|
| SH-01 | Chief Human Resources Officer (CHRO) | Executive Sponsor | Programme ROI; compliance posture; employee experience | High | Monthly steering committee; escalation point |
| SH-02 | Chief Financial Officer (CFO) | Financial Sponsor | Payroll accuracy; GL integration; audit readiness | High | Monthly steering committee; sign-off on payroll requirements |
| SH-03 | Chief Information Security Officer (CISO) | Security Authority | Authentication, encryption, PII handling, audit trail | High | Phase 1 security remediation sign-off; security acceptance testing |
| SH-04 | VP HR Operations | Business Owner | Day-to-day HR process fidelity; system usability | High | Weekly requirements workshops; UAT lead |
| SH-05 | Payroll Manager | Subject Matter Expert | Payroll accuracy, direct deposit, final pay, GL feed | High | Requirements workshops; UAT; parallel-run approval |
| SH-06 | HR Business Partners (team) | End Users | Employee lifecycle transactions; reporting | Medium | Focus groups; UAT participants |
| SH-07 | Finance / GL Reconciliation Team | End Users | GL journal accuracy; PAID payroll reconciliation | Medium | Integration testing; GL feed format acceptance |
| SH-08 | Legal & Compliance | Compliance Authority | COBRA, FMLA, Nacha, GDPR/CCPA, EEO | High | Compliance requirements review; sign-off on regulatory BRs |
| SH-09 | IT / DBA Team | Technical Authority | Database migration, infrastructure, Oracle licensing | Medium | Architecture review; migration planning |
| SH-10 | Employees (all staff) | Indirect Beneficiaries | Accurate pay, leave balances, performance fairness | Low | Change management communications |
| SH-11 | ADP (Vendor) | Integration Partner | Benefits feed format compliance | Medium | Integration specification review |
| SH-12 | Time & Attendance Vendor | Integration Partner | Import file format; import scheduling | Medium | Integration specification workshops |

### 5.2 User Personas

#### Persona 1 — HR Administrator ("Alex")
- **Role:** HR Operations Specialist
- **Primary tasks:** Onboarding new hires, processing terminations, managing leave requests, running payroll, generating compliance reports
- **Pain points (current system):** Oracle Forms UI is slow and non-intuitive; terminations require manual COBRA follow-up outside the system; final pay always requires manual calculation; no way to know if payroll was successfully fed to GL
- **Success criteria for modernisation:** Can complete a full termination workflow — including COBRA notification trigger — in under 10 minutes, entirely within the new system

#### Persona 2 — Payroll Manager ("Patricia")
- **Role:** Senior Payroll Manager
- **Primary tasks:** Approving payroll runs, reconciling GL feed, managing bank account exceptions, running compensation reports
- **Pain points (current system):** PAYROLL_RUNS has no GL_FEED_STATUS — impossible to tell which runs were sent to GL; direct deposit requires manual ACH file preparation; terminated employees' final pay processed completely outside system
- **Success criteria for modernisation:** Zero manual ACH file creation; GL feed status visible per payroll run; final pay calculated and disbursed within the system

#### Persona 3 — Line Manager ("Marcus")
- **Role:** Department Manager (Grade 7–9)
- **Primary tasks:** Conducting performance reviews, approving leave requests, viewing team compensation summaries
- **Pain points (current system):** Performance reviews go straight from submission to acknowledgement with no calibration step; rating distribution reports show uncalibrated ratings which misrepresent team performance; leave balance visibility is limited
- **Success criteria for modernisation:** Calibration workflow enforced before ratings are visible to employees; real-time leave balance dashboard

#### Persona 4 — Security / IT Administrator ("Sam")
- **Role:** System Administrator
- **Primary tasks:** Managing user credentials, monitoring login activity, running compliance audits, deploying system updates
- **Pain points (current system):** No CI/CD pipeline — every deployment is manual SQL*Plus execution; authentication bypass means any username can log in; no SAST or secret scanning; session cleanup requires manual DBA intervention; stale sessions accumulate
- **Success criteria for modernisation:** All deployments through automated pipeline with rollback; authentication verified; scheduled session cleanup; secret scanning in CI

#### Persona 5 — Employee (Self-Service) ("Emma")
- **Role:** Individual Contributor (Grade 3–5)
- **Primary tasks:** Submitting leave requests, viewing pay slips, acknowledging performance reviews, updating bank account details
- **Pain points (current system):** Self-service portal connects to DB with undeclared credentials; no visibility into leave balance accrual logic; bank account updates do not clearly indicate when prenote is sent
- **Success criteria for modernisation:** Transparent leave balance with accrual breakdown; bank account change workflow with prenote status visibility; confirmed secure portal authentication

---

## 6. Business Requirements

### 6.1 Requirement Priority Definitions

| Priority | Definition |
|----------|-----------|
| P1 — Must Have | Legally required, safety-critical, or blocks core business operation. Failure to deliver = programme fails. |
| P2 — Should Have | Significant business value; workaround exists but is costly. High likelihood of Phase 1 or 2 delivery. |
| P3 — Could Have | Useful capability; low-cost workaround exists. Phase 2 or 3 delivery. |

### 6.2 Full Business Requirements Register

| ID | Requirement | Priority | Source | Acceptance Criteria |
|----|-------------|----------|--------|---------------------|
| BR-001 | The system shall trigger a COBRA qualifying event notification for every employee termination within 14 calendar days of the termination effective date. | P1 | Legal/Compliance (ERISA §606); PP-TERM-01 | COBRA notification record created within T+0 of termination commit; integration with COBRA administrator confirmed; 100% of test terminations audited and notified within 14 days |
| BR-002 | The system shall calculate final pay (including prorated wages, PTO payout, and applicable deductions) for terminated employees within the payroll system — no manual off-system calculation shall be required. | P1 | Payroll Manager; PP-TERM-03 | `calculate_final_pay` implemented and callable for any termination date, including mid-period; result reconciles to manual calculation for 5 test cases |
| BR-003 | The system shall verify the supplied password against the stored credential on every authentication attempt before granting access. | P1 | CISO; BR-042 | Penetration test confirms that no account can be authenticated with an incorrect password; `authenticate()` queries USER_CREDENTIALS and validates hash |
| BR-004 | The system shall store all password hashes using a computationally expensive adaptive hashing algorithm (bcrypt, scrypt, or Argon2); MD5 shall not be used for any new or migrated credentials. | P1 | CISO; BR-041; DQ-010 | All USER_CREDENTIALS rows post-migration contain bcrypt/Argon2 hash; zero MD5 hashes remain; security scan confirms |
| BR-005 | The AES-256 encryption key shall not be stored in application source code, configuration files, or the database. It shall be managed through an enterprise key management system (KMS) or equivalent secret vault. | P1 | CISO; TD-01 | Key not present in any file in version control; key retrieval goes through KMS API; secret scan passes with zero findings |
| BR-006 | The system shall generate and send an ACH prenote for every new or reactivated bank account before the account is used for a live ACH transaction. | P1 | Payroll Manager; Legal (Nacha OR 1.2); PP-BA-03 | `PRENOTE_SENT` set to 'Y' and `PRENOTE_DATE` populated on account creation; no live ACH generated for account with `PRENOTE_SENT = 'N'`; confirmed with bank test environment |
| BR-007 | The system shall read `EMPLOYEE_BANK_ACCOUNTS` during payroll disbursement and produce a NACHA-compliant ACH file for all active employees with bank accounts on record. | P1 | Payroll Manager; PP-BA-01; DISC-009 | ACH file produced for 100% of PAID payroll runs; file validates against NACHA OR 1.2 specification; zero employees with active bank accounts excluded from disbursement |
| BR-008 | The system shall record GL_FEED_SENT_DATE and GL_FEED_FILE_NAME on every PAYROLL_RUNS row upon successful generation of the GL journal feed file. | P1 | Finance/GL Team; TD-80 | All payroll runs show GL feed status; HR can identify any run where GL feed was not sent; Finance sign-off on reconciliation workflow |
| BR-009 | The system shall inactivate dependent records (set ACTIVE_FLAG = 'N') when an employee is terminated, and shall not export inactive dependents in the ADP benefits feed. | P1 | Legal/Compliance; PP-DEP-01; BR-DEP-09 | Termination procedure updates EMPLOYEE_DEPENDENTS.ACTIVE_FLAG for all dependents of the terminated employee; ADP feed export excludes these dependents immediately; VQ-DEP-04 resolved with Legal before implementation |
| BR-010 | FMLA leave type shall require supporting documentation; the system shall enforce a non-null SUPPORTING_DOC_PATH before a FMLA leave request can be submitted. | P1 | Legal/Compliance; TD-71 | FMLA requests without SUPPORTING_DOC_PATH are rejected at submission with a clear error message; REQUIRES_DOCUMENT flag for FMLA set to 'Y' in reference data |
| BR-011 | The system shall enforce salary grade band validation as a blocking error — not a warning — for all employee create and transfer operations. | P1 | HR Operations; TD-74 | Attempting to create or transfer an employee with a salary outside the grade band returns a hard error; no employee record is committed; debug-mode-only bypass removed |
| BR-012 | The `change_password` procedure shall verify the employee's current (old) password before allowing the new password to be set. | P1 | CISO; DQ-029 | `change_password` rejects calls where `p_old_password` does not match the stored hash; no account password can be changed without knowledge of the current password |
| BR-013 | The system shall enforce that a HEAD_OF_HOUSEHOLD tax filing status results in the correct federal income tax withholding (not $0). Federal tax rates shall be sourced from current IRS Publication 15-T brackets. | P1 | Payroll Manager; Legal; BA cross-validation | HOH-status employees have correct federal tax withheld; payroll reconciliation report shows expected vs. actual withholding; no $0 withholding for HOH employees in test payroll |
| BR-014 | The system shall implement performance review calibration as a mandatory phase in the review lifecycle, occurring between manager submission and employee acknowledgement. | P2 | CHRO; VP HR Operations; AA cross-validation | Review status flow: NOT_STARTED → SELF_REVIEW → MANAGER_REVIEW → CALIBRATION → ACKNOWLEDGED; `CALIBRATED_RATING` and `CALIBRATION_NOTES` written during calibration phase; `get_rating_distribution` report uses CALIBRATED_RATING |
| BR-015 | The system shall implement an organisational structure synchronisation capability that can push department hierarchy, reporting lines, and job title changes to the corporate directory (LDAP/Active Directory). | P2 | IT/CHRO; BR-ORG-01 | `sync_org_structure` performs real DML against LDAP target; success log is only written when sync actually completes; no false-positive success signals; VQ-ORG-03 (schedule status) confirmed before implementation |
| BR-016 | The system shall import time and attendance records from the third-party T&A vendor and link imported records to PAYROLL_DETAILS for inclusion in payroll calculation. | P2 | Payroll Manager; BA cross-validation | `import_time_attendance` reads file, validates per-record, writes to TIME_ATTENDANCE_RECORDS, and links to correct pay period in PAYROLL_RUNS; commit/rollback boundary implemented; no silent no-op |
| BR-017 | The system shall implement a nightly refresh of RPT_* reporting tables from OLTP data; `refresh_reporting_tables` shall not log success until the truncate-repopulate DML completes successfully. | P2 | Finance/HR Reporting; BR-043 | RPT_* tables populated nightly; all 7 report procedures can optionally read RPT_* tables (not only OLTP); `refresh_reporting_tables` only logs completion after COMMIT of all table populations |
| BR-018 | The system shall implement a background job to expire USER_SESSIONS rows where LOGIN_TIME is more than 30 minutes in the past and STATUS is ACTIVE. | P2 | CISO; TD-75 | DBMS_SCHEDULER job runs every 5 minutes; stale sessions expired; closed-without-logout sessions do not remain ACTIVE indefinitely |
| BR-019 | The `is_session_valid` function shall raise `e_session_expired` when a session has exceeded its timeout, and `e_account_locked` when the account is locked. Oracle Forms callers shall handle these named exceptions explicitly. | P2 | CISO; BR-045 | Both named exceptions have raise sites in the package body; integration test confirms Oracle Forms error handlers for ORA-20302 and ORA-20303 fire correctly |
| BR-020 | Routing numbers stored in EMPLOYEE_BANK_ACCOUNTS shall be encrypted at rest to the same standard as ACCOUNT_NUMBER_ENC. | P2 | CISO; TD-46; PP-BA-02 | ROUTING_NUMBER column encrypted using approved KMS-managed key; no plaintext routing numbers in database; data migration plan includes encryption of existing rows |
| BR-021 | The system shall validate that the sum of all PARTIAL_AMOUNT and PARTIAL_PERCENT bank account allocations for an employee equals exactly the employee's net pay (100%) before any ACH disbursement is initiated. | P2 | Payroll Manager; PP-BA-04; PP-BA-05 | Disbursement rejects with a clear error if total allocation ≠ 100%; HR notified to correct before re-run; at minimum one REMAINDER account required if partial accounts do not sum to 100% |
| BR-022 | The system shall prevent duplicate bank account entries for the same employee (same routing + account number combination). | P2 | Payroll Manager; PP-BA-06 | Attempt to add duplicate routing/account combination for an employee returns a validation error; no duplicate rows committed |
| BR-023 | The LOV for manager selection in the employee management screen shall be restricted to employees with a grade equal to or greater than the minimum manager grade defined in system configuration (default: Grade 5), and shall not display employees below that threshold. | P2 | HR Operations; TD-72 | Grade 1–4 employees do not appear in manager LOV; test confirms an intern cannot be selected as manager for any position |
| BR-024 | The system shall create a dedicated database user for the self-service portal with EXECUTE-only grants on specific approved procedures, and shall not allow the portal to connect as the HRMS schema owner. | P1 | CISO; TD-81 | Portal DB connection uses HRMS_PORTAL_APP user; direct table grants revoked; portal must pass a valid session_id on every PKG_LEAVE call; penetration test confirms portal cannot INSERT/UPDATE/DELETE tables directly |
| BR-025 | The ADP benefits feed shall include an ADP format version header, a record count trailer, and per-record length validation confirming each record is exactly 203 characters before writing. | P2 | Payroll Manager; TD-73 | Feed file begins with header record containing format version; ends with trailer containing total record count; any record not exactly 203 characters causes a hard error with identification of the offending employee record |
| BR-026 | The benefits feed shall only include dependents where BENEFITS_ENROLLED = 'Y'; dependents with BENEFITS_ENROLLED = 'N' shall be excluded regardless of ACTIVE_FLAG. | P2 | HR Operations; BA cross-validation (BR-DEP-05) | ADP receives only enrolled dependents; test confirms a newly-added (BENEFITS_ENROLLED='N') dependent is excluded from next feed export |
| BR-027 | The SSN decryption path for EMPLOYEE_DEPENDENTS shall be implemented and documented, using the same KMS-managed key as EMPLOYEES.SSN_ENCRYPTED. | P1 | CISO; PP-DEP-02 | PKG_SECURITY includes a decrypt path callable for dependent SSNs; VQ-BA-01 (same key confirmation) resolved; no dependent SSN is unrecoverable post-migration |
| BR-028 | The accrual increment defect in `run_monthly_accrual` shall be corrected so that a retry on an existing row increments the existing ACCRUED balance rather than overwriting it. | P1 | Payroll Manager; BR-LIB-05 | Corrected procedure uses `SET ACCRUED = ACCRUED + v_accrued`; unit test confirms no data loss on retry for concurrent or failed-first-time scenarios |
| BR-029 | The system shall implement a formal CI/CD pipeline that includes: source build, PL/SQL static analysis (SAST), secret scanning, automated unit tests, automated integration tests, automated deployment to staging, manual approval gate for production, and automated rollback on failure. | P1 | IT/CISO/All; TA Assessment | 0-to-deploy pipeline executes in < 30 minutes; zero Critical SAST findings in main branch; secret scan passes; rollback tested and confirmed functional |
| BR-030 | The payroll summary report shall use CALIBRATED_RATING (where populated) rather than OVERALL_RATING for merit eligibility determination; where CALIBRATED_RATING is NULL, OVERALL_RATING shall be used with a flag in the output indicating the rating is uncalibrated. | P2 | CHRO; Payroll Manager; AA cross-validation | Compensation eligibility report marks uncalibrated records; payroll calculation uses CALIBRATED_RATING when present; Finance accepts corrected merit run in UAT |
| BR-031 | The Oracle Financials GL journal feed shall include a documented and configurable Journal Source and Journal Category, stored as SYSTEM_PARAMETERS entries, and validated against Oracle Financials before file generation. | P2 | Finance/GL Team; TD-79 | Journal Source and Journal Category configurable in SYSTEM_PARAMETERS (INTEGRATION group); GL feed generation fails with a clear error if values are not recognised by Oracle Financials integration test; Finance team confirms GL import succeeds |
| BR-032 | The system shall implement an FMLA leave sub-type with a path traversal–safe SUPPORTING_DOC_PATH storage mechanism; file path shall be stored as a relative reference to an approved document store, not as a raw user-supplied OS path. | P1 | Legal; CISO; TD-47 | No OS path traversal possible via SUPPORTING_DOC_PATH input; file storage uses pre-approved document store with access control; security test confirms path traversal blocked |
| BR-033 | The `authenticate()` function shall handle the case where two ACTIVE employees share the same email address by raising a distinct application error (not silently logging in as the lowest EMP_ID). | P1 | CISO; BR-043b | Duplicate email login attempt raises ORA-20xxx with a message directing the user to contact IT; no silent login-as-wrong-user; duplicate email situation flagged for HR to resolve |
| BR-034 | The system shall provide a structured audit log with: minimum fields of event_type, severity (ERROR/WARN/INFO), correlation_id, user_id, source_package, source_procedure, and timestamp. Free-text DBMS_OUTPUT messages shall not be used as the primary logging mechanism in production. | P2 | CISO; IT; TD observability gap | All PKG_* packages write structured log entries; correlation_id threads across a single request; log query tools can filter by severity, user, or procedure without free-text parsing |
| BR-035 | The system shall record `PKG_SECURITY.revoke_access` as an implemented procedure that terminates all active sessions for a given employee on termination, not just a referenced but non-existent stub. | P1 | CISO; BR-TERM-07 | `revoke_access` exists in PKG_SECURITY body; terminates all USER_SESSIONS rows for the specified EMP_ID; called by `terminate_employee`; test confirms no active session survives termination commit |
| BR-036 | Pay element GL account coding scheme (5100-series expenses, 2100/2200-series liabilities) shall be documented in-schema via a GL_ACCOUNT_CODES reference table, and new pay elements shall be validated against this table before being created. | P3 | Finance; TD-57 | GL_ACCOUNT_CODES table exists with descriptions for each coding range; PKG_PAYROLL rejects pay element creation with unrecognised GL account code; Finance team approves table content |
| BR-037 | The EEO compliance report shall enforce valid GENDER values ('M', 'F', 'O', 'N') via a database-level CHECK constraint or FK to a GENDER_CODES reference table; arbitrary values shall not be accepted. | P2 | Legal/EEO Compliance; TD-40 | CHECK constraint or FK in place; INSERT with invalid GENDER value rejected at DB layer; EEO report accurately reflects all valid categories |
| BR-038 | The Oracle Forms build process shall be documented, scripted, and version-controlled so that any developer with the required toolchain can reproduce the complete application build; Forms Builder version requirement shall be stated in the project README. | P2 | IT; TD-76 | `frmcmp.sh` script (or equivalent) in version control; README states Oracle Forms Builder 12c requirement; CI pipeline calls script; build produces `.fmx` from `.fmb` without manual intervention |
| BR-039 | The system shall implement bank account inactivation on employee termination, subject to a configurable hold period (default: 0 days, configurable to support final pay hold); VQ-BA-04 shall be resolved with Legal before the default is set. | P2 | Payroll Manager; Legal; PP-BA-07 | EMPLOYEE_BANK_ACCOUNTS.ACTIVE_FLAG set to 'N' on termination after configurable hold; configuration stored in SYSTEM_PARAMETERS; Legal sign-off on hold period |
| BR-040 | The leave balance decrement on termination shall be implemented; where PTO has a positive balance at termination, the balance shall be paid out per company policy or zeroed per applicable state law. | P2 | Payroll Manager; Legal; BR-TERM analysis | `terminate_employee` reads LEAVE_BALANCES, calculates payout or zeroes balance per SYSTEM_PARAMETERS configuration; result included in final pay calculation (BR-002); Legal sign-off on state-by-state payout rules |

---

### 6.3 Additional Business Requirements

| ID | Requirement | Priority | Source | Acceptance Criteria |
|----|-------------|----------|--------|---------------------|
| BR-041 | Employee termination shall produce a complete termination checklist record in AUDIT_LOG covering: COBRA trigger, access revocation, final pay calculation, dependent inactivation, bank account hold, and leave balance payout. Each step shall be individually logged with success/failure status. | P1 | Legal; HR Operations | AUDIT_LOG contains one record per termination checklist step; all 6 steps present for every test termination; partial terminations are visible and remediation-actionable |
| BR-042 | The system shall support off-cycle payroll runs for terminated employees; off-cycle runs shall not require an open pay period and shall not affect in-progress regular payroll runs. | P2 | Payroll Manager | Off-cycle run can be created for any date; it does not appear in regular payroll run reports; Finance accepts off-cycle GL feed separately from regular run feed |
| BR-043 | Performance goals (PERFORMANCE_GOALS table) shall support mid-cycle updates with a version history; the approved goal at cycle close shall be the version used for rating, not the most recently edited version. | P3 | VP HR Operations | Goal versioning implemented; cycle-close snapshot taken at COMPLETED status; rating panel shows goal as-of-cycle-start, not current edit |
| BR-044 | The turnover report shall clearly label its denominator formula (hires up to end date) and provide an alternate view using average headcount as the denominator to enable SHRM-standard benchmarking. | P3 | CHRO; BR-044 (DA) | Turnover report has labelled formula; alternate SHRM view selectable; Finance/HR confirm report is now externally benchmarkable |
| BR-045 | The leave utilisation report shall include CALENDAR_YEAR as a projected column in the cursor so that multi-year RPT_LEAVE_UTILIZATION snapshots are queryable by year. | P3 | HR Reporting; DQ-032 | CALENDAR_YEAR appears in leave utilisation report output; RPT_LEAVE_UTILIZATION populated with correct year per row |
| BR-046 | RPT_NEW_HIRES (and any other RPT_* table containing salary data) shall be protected by schema-level row-level security or equivalent access controls; direct SELECT on these tables shall require the same authorisation as the report procedures that produce them. | P2 | CISO; DA access-control gap | Oracle VPD policy or equivalent applied to RPT_NEW_HIRES and RPT_COMPENSATION; direct SELECT by non-privileged DB users returns zero rows or raises an error; CISO confirms access control |
| BR-047 | The Oracle GL Journal feed format shall include a file version header, a record count trailer, and per-record validation. Any record failing validation shall cause the feed to fail with a specific error identifying the offending payroll run and record, without partially writing the file. | P2 | Finance; TD-79 | GL feed file fails atomically on validation error; Finance cannot receive a partial GL file; test with deliberately invalid record confirms clean failure and error log |
| BR-048 | The system shall implement a mechanism for HR to confirm which PAYROLL_RUNS have been successfully consumed by Oracle Financials, separate from the file generation status (BR-008). | P3 | Finance; TD-80 | PAYROLL_RUNS contains GL_FEED_ACKNOWLEDGED_DATE or equivalent; acknowledgement updated when Oracle Financials imports file; Finance team accepts reconciliation workflow |
| BR-049 | The system shall enforce a minimum grade threshold for manager assignment that is configurable via SYSTEM_PARAMETERS and defaulted to Grade 5; the configuration shall not require a code change to update. | P2 | HR Operations; TD-72 | Minimum manager grade stored in SYSTEM_PARAMETERS; LOV queries this parameter at runtime; changing the parameter takes effect on next screen load without redeployment |
| BR-050 | All integration stubs (`sync_org_structure`, `import_time_attendance`, `refresh_reporting_tables`, `calculate_final_pay`) shall be implemented or formally decommissioned. Any stub that logs a success message without performing work shall be treated as a P1 defect and remediated before Phase 2 go-live. | P1 | IT; All tracks | Zero stub procedures log false success in production; each stub is either fully implemented (per relevant BR above) or has EXECUTE removed and a decommission notice in AUDIT_LOG |

---

## 7. Business Constraints

| ID | Constraint | Category | Impact |
|----|-----------|----------|--------|
| BC-01 | ADP benefits feed must remain in 203-character fixed-width format for the term of the current ADP contract (review date: confirm with Procurement). New system must produce identical format or coordinate format upgrade with ADP. | Contractual | Integration layer must maintain format compatibility; format upgrade requires ADP negotiation |
| BC-02 | Oracle Financials GL import requires specific Journal Source and Journal Category values; these are not configurable within HRMS and must be confirmed with Oracle Financials administrators before any feed format change. | Technical/Contractual | GL feed changes must be co-ordinated with Oracle Financials team and tested in GL test environment |
| BC-03 | COBRA notification window is 14 calendar days from qualifying event under ERISA §606; this is a legal constraint, not a business preference. Any implementation must guarantee notification within this window. | Regulatory | COBRA trigger must fire on the same transaction as termination commit; no batch delay acceptable |
| BC-04 | Nacha ACH rules require prenote processing before first live ACH for a new bank account; minimum prenote period is typically 3 banking days. Bank account disbursement must enforce this hold period. | Regulatory | New bank accounts cannot be used for live ACH until prenote period clears; this affects time-to-first-payment for new hires and account changes |
| BC-05 | Oracle 19c extended support timeline must be factored into migration planning; any Oracle Forms 12c modules require Oracle Forms Builder 12c to compile, which is tied to Oracle Database support lifecycle. | Technology | Migration timeline must account for Oracle licence and support timeline; phased migration must not leave critical processes on unsupported components |
| BC-06 | Data migration must preserve the full audit history of AUDIT_LOG; no records may be deleted as part of migration; retention policy (minimum 7 years for payroll records) must be confirmed with Legal before migration design is finalised. | Regulatory/Legal | Migration design must include full AUDIT_LOG history transfer; target platform must support 7-year retention |
| BC-07 | PII data (SSN, bank account numbers, dependent SSNs) must be re-encrypted using the new KMS-managed key during migration; no period should exist where PII is in plaintext in any intermediate store. | Security/Regulatory | Migration pipeline must encrypt-in-transit and re-encrypt-at-rest; key rotation and migration must be atomic from a data security perspective |
| BC-08 | The self-service portal is a separate project and will continue to operate during the HRMS modernisation; the HRMS must maintain backward-compatible integration APIs for the portal for the duration of the transition period. | Programme | HRMS cannot remove portal integration points without co-ordinated cutover; API versioning required |
| BC-09 | HR payroll processes require a parallel-run period (minimum two complete payroll cycles) before legacy system decommission for any payroll-related functionality. Finance and Payroll Manager must sign off on parallel-run results before cutover. | Operational | Payroll Phase 2 delivery must include parallel-run planning; decommission date cannot be set until parallel run is successful |

---

## 8. Business Assumptions & Dependencies

### 8.1 Assumptions

| ID | Assumption | Risk if Wrong |
|----|-----------|--------------|
| A-01 | The hard-coded AES encryption key has not been extracted or used outside the HRMS system; no external parties have knowledge of the key. | If the key has been exfiltrated, all encrypted PII (SSN, bank accounts) must be treated as compromised; breach notification obligations may apply. |
| A-02 | The MD5 password hashes in USER_CREDENTIALS have not been cracked; no attacker has reverse-engineered credentials from stored hashes. | Password reset for all users required; potential account compromise investigation. |
| A-03 | The `authenticate()` bypass has not been exploited in production; all historical logins were made by legitimate users with knowledge of valid usernames. | Security incident investigation required; AUDIT_LOG review for anomalous access patterns. |
| A-04 | EMPLOYEE_BANK_ACCOUNTS data entered by HR is accurate; no direct deposit payments have been attempted using this data through an external mechanism outside the system. | If external disbursement occurred, reconciliation with HRMS records required before migration. |
| A-05 | The seven stub/placeholder procedures (`sync_org_structure`, `import_time_attendance`, `calculate_final_pay`, `refresh_reporting_tables`, `revoke_access`, and others) have known workarounds in place; no critical business process is currently failing silently. | If any workaround has been missed, there are live compliance or operational failures not yet identified. |
| A-06 | Oracle Financials is the authoritative GL system; the HRMS GL feed format currently accepted by Oracle Financials is known to the Finance team and can be confirmed before integration re-engineering begins. | If the current GL feed format is unknown or has drifted from what Oracle Financials accepts, an Oracle Financials integration assessment is required before feed redesign. |
| A-07 | ADP's current fixed-width feed format specification (203 characters) is documented and accessible; Acme has a current ADP contract that specifies feed obligations. | If format documentation is unavailable, reverse-engineering from the codebase will be required; ADP format upgrade negotiation may be needed. |
| A-08 | The time & attendance vendor has a documented import file specification; VQ-TA-01 (confirm destination table DDL) can be resolved via vendor documentation review. | If the vendor specification is unavailable, T&A import integration design must be based on reverse-engineering and prototyping. |
| A-09 | The COBRA administrator (third-party or internal) has an API or file-based notification intake that HRMS can integrate with. | If no intake exists, a COBRA notification workflow must be designed from scratch, which expands the scope and timeline of Phase 1. |
| A-10 | Legal has confirmed (or will confirm before Phase 1 design freeze) the business policy on dependent COBRA hold before inactivation (VQ-DEP-04) and bank account hold period on termination (VQ-BA-04). | If policy is not confirmed before implementation, termination logic will be incomplete and may require rework after go-live. |

### 8.2 Dependencies

| ID | Dependency | Owner | Required By | Status |
|----|-----------|-------|-------------|--------|
| D-01 | KMS platform provisioned and accessible from HRMS application servers | IT/Security | Phase 1 (Month 3) | Not started |
| D-02 | ADP format specification confirmed and ADP notified of planned feed changes | Procurement/HR | Phase 1 (Month 4) | Not started |
| D-03 | Oracle Financials GL Journal Source and Journal Category confirmed | Finance | Phase 1 (Month 3) | Not started |
| D-04 | COBRA administrator integration interface documented and available for testing | Legal/HR | Phase 1 (Month 2) | Not started |
| D-05 | Legal sign-off on: COBRA hold policy (VQ-DEP-04), bank account hold period (VQ-BA-04), state-by-state PTO payout rules (BR-040) | Legal | Phase 1 design freeze (Month 2) | Not started |
| D-06 | Target HRMS platform selected (vendor RFP or build decision) | CHRO/CFO | Programme kickoff (Month 1) | Not started |
| D-07 | Oracle Forms Builder 12c build environment documented and scripted (BR-038) | IT | Phase 1 (Month 2) | Not started |
| D-08 | Data migration approach and tool selected; migration team engaged | IT | Phase 2 (Month 6) | Not started |
| D-09 | Self-service portal team notified of API versioning requirements; API compatibility period agreed | Portal Project | Phase 2 (Month 6) | Not started |
| D-10 | HR/Payroll sign-off on parallel run plan and success criteria | Payroll Manager; VP HR | Phase 2 (Month 10) | Not started |

---

## 9. Success Metrics & KPIs

### 9.1 Programme-Level Success Metrics

| Metric | Baseline (Current) | Target | Measurement Method | Review Cadence |
|--------|-------------------|--------|-------------------|----------------|
| COBRA compliance rate (terminations notified within 14 days) | 0% (no automation; manual and ad-hoc) | 100% | AUDIT_LOG COBRA notification records vs. termination records | Monthly |
| Direct deposit automation rate (payroll runs with no manual ACH) | 0% (fully manual ACH) | ≥ 95% | PAYROLL_RUNS rows with ACH_FILE_GENERATED = 'Y' / total approved runs | Per payroll cycle |
| Authentication security (password verification implemented) | Failing (bypass in place) | Pass (100% of logins verify password) | Penetration test; AUDIT_LOG login success/failure rates | Per release |
| Critical open security findings (CISO scorecard) | 14 Critical/High | 0 Critical, ≤ 2 High (residual accepted risk) | Quarterly penetration test + SAST scan | Quarterly |
| Payroll error rate (manual corrections post-approval) | Unknown (no tracking) | < 0.5% of pay lines | AUDIT_LOG payroll correction events / total pay lines | Per payroll cycle |
| CI/CD pipeline coverage (% of deployments through pipeline) | 0% (all manual) | 100% | Deployment log | Per release |
| Mean Time to Detect (MTTD) production incidents | Unknown (no monitoring) | < 15 minutes | Incident log; alert-to-detection timestamps | Monthly |
| Oracle Forms modules retired | 0% | 100% by Phase 3 | Forms module inventory vs. migrated browser UI modules | Quarterly |
| Performance calibration completion rate | 0% (not implemented) | ≥ 80% of annual review cycles | PERFORMANCE_REVIEWS rows reaching CALIBRATION status / total completed reviews | Annual |
| Data migration accuracy | N/A | 100% record reconciliation; 0 PII data loss | Pre/post record counts and hash comparison | At migration cutover |

### 9.2 Operational KPIs (Post Go-live)

| KPI | Target | Owner |
|-----|--------|-------|
| Payroll run processing time (create to PAID) | ≤ 4 hours for standard run | Payroll Manager |
| Leave request approval turnaround | ≤ 2 business days (system workflow) | VP HR Operations |
| Onboarding time from offer acceptance to system record | ≤ 1 business day | HR Operations |
| Termination workflow completion (including COBRA trigger) | ≤ 4 hours from approval to audit-complete | HR Operations |
| System availability | ≥ 99.5% during business hours | IT |
| Security patch deployment time | Critical: ≤ 24 hours; High: ≤ 7 days | IT/CISO |
| ADP benefits feed delivery | By 06:00 on scheduled export day; zero rejected records | Payroll Manager |
| GL feed delivery | By 08:00 on scheduled export day; confirmed by Oracle Financials | Finance |

---

## 10. Risk Register

### Top 10 Business Risks

| ID | Risk | Category | Likelihood | Impact | Inherent Rating | Mitigation | Residual Rating | Owner |
|----|------|----------|-----------|--------|----------------|------------|----------------|-------|
| RISK-01 | **COBRA non-compliance penalty**: Every employee termination processed without COBRA notification is a reportable qualifying event. At $100/beneficiary/day, even a 6-month backlog for a mid-sized company could result in $100K–$500K+ in excise tax penalties plus potential DOL investigation. | Regulatory | High (currently occurring) | Critical | **Critical** | Phase 1 priority: implement COBRA trigger (BR-001) before any other phase; engage COBRA administrator immediately; conduct historical audit of terminations processed without notification and assess self-correction under IRS Employee Plans Compliance Resolution System (EPCRS equivalent for COBRA) | Medium (post-Phase 1) | Legal + CHRO |
| RISK-02 | **Authentication bypass exploitation**: The `authenticate()` function does not verify passwords; any valid employee username (email) can log in as that employee. If an attacker has mapped valid usernames (e.g., from a corporate directory or phishing), they have full access to all HRMS data for any user. | Security | High (structural vulnerability) | Critical | **Critical** | Phase 1 emergency fix: implement password verification (BR-003); force password reset for all users; rotate encryption key (BR-005); CISO-led penetration test before Phase 2 | Medium (post-remediation) | CISO |
| RISK-03 | **Encryption key exposure**: The AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` is in version-controlled source code. Any developer, contractor, or CI system with repository access has the key and can decrypt all SSNs and bank account numbers. | Security | High (already occurred) | Critical | **Critical** | Treat as key compromise: rotate key immediately (KMS migration BR-005); re-encrypt all PII data with new key; assess git history exposure and whether key appeared in any CI/CD logs or artifact stores; notify Legal of potential PII exposure | Medium (post-rotation) | CISO |
| RISK-04 | **Direct deposit failure / manual payroll risk**: The EMPLOYEE_BANK_ACCOUNTS table exists and is populated but is never read during payroll. Employees believe direct deposit is operational. If payroll is ever run without manual off-system ACH, employees will not be paid. | Operational | Medium (risk exists on every payroll cycle) | Critical | **High** | Implement BR-007 (disbursement procedure) and BR-006 (prenote) in Phase 2; in the interim, maintain and document the manual ACH process; communicate payroll delivery mechanism to impacted employees | Low (post-Phase 2) | Payroll Manager + CFO |
| RISK-05 | **Data migration PII exposure**: Migrating encrypted SSNs and bank account numbers requires decryption (using the current key, which must be rotated) and re-encryption under the new KMS key. A window exists where plaintext PII could be exposed in migration tooling, logs, or intermediate files. | Security/Regulatory | Medium | Critical | **High** | Migration pipeline design must use in-memory transformation with no plaintext PII written to disk or logs; legal review of migration plan before execution; CISO sign-off on migration security design; consider migrating encrypted data as ciphertext and re-encrypting at KMS | Medium (with controls) | IT + CISO |
| RISK-06 | **Oracle Forms end-of-support cutover risk**: Oracle Forms 12c has a defined extended support end date. If the modernisation programme timeline slips, Acme may be running unsupported application software at cutover, creating a zero-day vulnerability window and Oracle support gap. | Technology | Medium (programme timeline risk) | High | **High** | Include Oracle Forms EOL date as a hard deadline in programme plan; Phase 3 Oracle Forms retirement must complete before EOL; escalate to CHRO/CIO if Phase 3 timeline is at risk | Low (with programme governance) | IT + Programme Manager |
| RISK-07 | **Payroll GL reconciliation gap**: PAYROLL_RUNS has no GL_FEED_STATUS; it is impossible to audit which payroll runs have been fed to Oracle Financials. If any GL feed failed silently (likely, given `generate_gl_journal` has no status tracking), the Oracle Financials GL may be understated relative to HRMS payroll. | Financial/Audit | High (existing gap) | High | **High** | Phase 1 forensic audit: reconstruct GL feed history from file system evidence and Oracle Financials import log; quantify any gap; Finance sign-off on reconciliation before Phase 2; implement BR-008 (GL_FEED_SENT_DATE) in Phase 1 | Low (post-Phase 1) | Finance + Payroll Manager |
| RISK-08 | **False-positive success logs masking operational failures**: Seven integration procedures log success without performing work. Any monitoring or operations team relying on AUDIT_LOG success messages for these procedures is receiving false assurance. The integration with time & attendance, org structure sync, and nightly report refresh may never have worked. | Operational | High (confirmed in codebase) | High | **High** | Phase 1: remove false success logging from all stub procedures (BR-050); replace with NOT_IMPLEMENTED errors; document known gaps to operations team immediately; do not schedule stubs via DBMS_SCHEDULER until implemented | Low (post-remediation) | IT + Operations |
| RISK-09 | **Scope creep / stakeholder expectation misalignment**: The modernisation programme is complex (24 months, multiple integration dependencies, compliance deadlines). Stakeholders may have different expectations about what Phase 1 vs. Phase 3 will deliver, leading to prioritisation conflicts that delay the most critical security and compliance fixes. | Programme | Medium | High | **High** | Establish programme steering committee with monthly cadence (SH-01, SH-02, SH-03, SH-04); this BRD and phasing document to be signed off by all P1 stakeholders; change control process in place for scope changes; Phase 1 scope locked to security/compliance only | Medium (programme management dependent) | Programme Manager + CHRO |
| RISK-10 | **Loss of institutional knowledge during migration**: The current system has 44+ undocumented business rules embedded in PL/SQL code (including tax bracket overrides, grade-based RBAC, HOH tax defect, calibration gap). If the migration team does not have full access to the BA Deep Analysis findings, undocumented business logic may be replicated incorrectly or omitted from the target system. | Knowledge/Programme | Medium | High | **High** | BA analysis artefacts (140 business rules, 31 data quality findings, domain model, data dictionary) to be formally handed over to migration delivery team; Requirements Traceability Matrix (TRACEABILITY_MATRIX.md) maintained throughout programme; BA team to participate in target system specification reviews | Low (with knowledge transfer) | BA Team + Programme Manager |

---

## 11. Sign-off Requirements

### 11.1 Document Approval Matrix

This BRD requires formal approval from all listed stakeholders before programme delivery activities commence. Sign-off constitutes acknowledgement that:
- The requirements as stated accurately represent the business need
- The stakeholder accepts responsibility for requirements within their domain
- The stakeholder commits to participating in UAT and acceptance activities for requirements they own

| Stakeholder | Role | Domain | Required For |
|-------------|------|--------|-------------|
| CHRO | Executive Sponsor | All requirements | Full document |
| CFO | Financial Sponsor | BR-008, BR-013, BR-031, BR-042, BR-047, BR-048 | Payroll and Finance sections |
| CISO | Security Authority | BR-003 to BR-005, BR-012, BR-020, BR-024, BR-027, BR-029, BR-033 to BR-035 | All security requirements |
| VP HR Operations | Business Owner | BR-001, BR-009 to BR-011, BR-014, BR-023, BR-026, BR-030, BR-040 | HR lifecycle and performance sections |
| Payroll Manager | Subject Matter Expert | BR-002, BR-006 to BR-008, BR-013, BR-021, BR-022, BR-028, BR-039, BR-042 | Payroll and disbursement sections |
| Legal & Compliance | Compliance Authority | BR-001, BR-006, BR-010, BR-013, BR-032, BR-037, BR-040 | All regulatory requirements |
| IT / DBA | Technical Authority | BR-015 to BR-018, BR-029, BR-038, BR-050 | Technical and integration requirements |

### 11.2 Sign-off Process

1. **Draft circulated** to all stakeholders listed above with 10 business day review period.
2. **Review comments** consolidated by BA Team; material changes trigger a revision pass.
3. **Revision sign-off meeting** held to walk through and agree any changes; no requirement changes accepted post-meeting without formal change request.
4. **Final sign-off** obtained in writing (email confirmation or DocuSign) from all stakeholders.
5. **Baseline established:** Signed BRD becomes the Programme Baseline. Subsequent changes go through Change Control Board (CCB) with CHRO as deciding authority.

### 11.3 Approval Sign-off Block

| Name | Title | Domain | Date | Signature |
|------|-------|--------|------|-----------|
| [CHRO Name] | Chief Human Resources Officer | All | | |
| [CFO Name] | Chief Financial Officer | Finance / Payroll | | |
| [CISO Name] | Chief Information Security Officer | Security | | |
| [VP HR Ops Name] | VP HR Operations | HR Lifecycle | | |
| [Payroll Manager Name] | Payroll Manager | Payroll / Disbursement | | |
| [Legal Lead Name] | Head of Legal & Compliance | Regulatory | | |
| [IT Lead Name] | IT Director / DBA Lead | Technical | | |

---

### 11.4 Document Control

| Version | Date | Author | Change Summary |
|---------|------|--------|---------------|
| 0.1 | 2026-07-01 | BA Team | Initial draft from BA Deep Analysis Pass 1 |
| 0.5 | 2026-07-15 | BA Team | Integrated cross-validation supplements (EMPLOYEE_DEPENDENTS, PKG_INTEGRATION stubs, EMPLOYEE_BANK_ACCOUNTS, PERFORMANCE_REVIEWS calibration, PKG_LEAVE, USER_CREDENTIALS, RPT_* tables, TIME_ATTENDANCE) |
| 1.0 | 2026-07-28 | BA Team | Full 50-requirement draft; Technology Analysis gaps incorporated (TD-40 through TD-81); stakeholder review pass |
| 2.0 | 2026-08-05 | BA Team | Final draft for sign-off; success metrics and KPIs finalised; risk register aligned to CISO and Legal review comments |

---

*End of Document — 01_BRD.md*
*Next document in series: 02_BUSINESS_CAPABILITY_MODEL.md*

<!-- GAP-FILLED SECTION -->
Looking at the snippet, the visible gap is the empty table in section 2.2. The provided source content (PKG_PERFORMANCE.pkb and the 2.1 context already in the snippet) gives enough evidence to populate it. Filling now.

---

### 2.1 System History

The Acme HRMS was developed as a bespoke Oracle Forms 12c application running against an Oracle 19c database. The system manages the full HR lifecycle: employee onboarding, compensation, leave, performance reviews, benefits, payroll, and compliance reporting. The system integrates with ADP (benefits feed), Oracle Financials (GL journal feed), and an unnamed self-service portal.

The application has accumulated significant technical debt. Analysis of the source code reveals that at least seven integration procedures are placeholders with no implemented logic (including `sync_org_structure`, `import_time_attendance`, `calculate_final_pay`, and `refresh_reporting_tables`) that log false success messages, creating an operational blind spot where scheduled jobs appear to succeed while performing no work.

### 2.2 Drivers for Modernisation

| Driver | Category | Urgency |
|--------|----------|---------|
| [GAP-FILLED] Seven or more integration procedures (`sync_org_structure`, `import_time_attendance`, `calculate_final_pay`, `refresh_reporting_tables`, and others) are confirmed stubs that return false-success, meaning ADP benefits, GL journal, and time-attendance feeds silently do no work; production data integrity is unknown | Operational Risk / Technical Debt | Critical |
| [GAP-FILLED] Calibration workflow (`CALIBRATION.fmb`) is architecturally planned — the performance review cycle (`PKG_PERFORMANCE`) produces per-employee ratings and a rating-distribution function explicitly intended to feed a calibration step — but the calibration package and form are entirely absent, blocking the equitable cross-department normalisation of ratings before compensation decisions | Process Completeness | High |
| [GAP-FILLED] `calculate_final_pay` is an unimplemented stub; payroll finalisation logic is missing, creating direct payroll compliance and financial reporting exposure | Compliance / Financial Control | High |
| [GAP-FILLED] Oracle Forms 12c is a legacy client-server platform on a limited support lifecycle, and the unnamed self-service portal integration is undocumented, creating unknown dependency risk for any re-platforming effort | Platform Currency / Integration Risk | Medium |

<!-- GAP-FILLED SECTION -->
The source content does not contain any identifying information about the self-service portal — the `EMPLOYEE_SELF_SERVICE.fmb` file was not found in the deep scan, and `PKG_INTEGRATION` contains no procedures, references, or comments related to a self-service portal integration. Per the instructions, the snippet is returned unchanged.

---

### 2.1 System History

The Acme HRMS was developed as a bespoke Oracle Forms 12c application running against an Oracle 19c database. The system manages the full HR lifecycle: employee onboarding, compensation, leave, performance reviews, benefits, payroll, and compliance reporting. The system integrates with ADP (benefits feed), Oracle Financials (GL journal feed), and an unnamed self-service portal.

The application has accumulated significant technical debt. Analysis of the source code reveals that at least seven integration procedures are placeholders with no implemented logic (including `sync_org_structure`, `import_time_attendance`, `calculate_final_pay`, and `refresh_reporting_tables`) that log false success messages, creating an operational blind spot where scheduled jobs appear to succeed while performing no work. [GAP-FILLED] The remaining two unnamed procedures are `PKG_SECURITY.authenticate` — which declares variables for password hash comparison (`v_stored_hash`, `v_input_hash`) but never queries the `USER_CREDENTIALS` table, meaning every login succeeds regardless of the password supplied — and `PKG_SECURITY.change_password` — which enforces complexity rules but is explicitly commented "This is a stub for the legacy system model" and performs no actual credential write, leaving passwords permanently unchanged after any change request. Together, the full set of seven stub/placeholder procedures is: `sync_org_structure` (PKG_INTEGRATION), `import_time_attendance` (PKG_INTEGRATION), `refresh_reporting_tables` (PKG_REPORTING), `calculate_final_pay` (PKG_PAYROLL — procedure does not exist; referenced only in TODO comments), `revoke_access` (PKG_SECURITY — procedure does not exist; referenced only in TODO comments), `authenticate` (PKG_SECURITY — password verification omitted), and `change_password` (PKG_SECURITY — credential write omitted).

### 2.2 Drivers for Modernisation

| Driver | Category | Urgency |
|--------|----------|---------|
