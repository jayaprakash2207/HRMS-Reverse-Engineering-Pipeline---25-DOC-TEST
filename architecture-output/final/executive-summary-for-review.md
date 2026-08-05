# Executive Summary — Oracle HRMS v4.2 Architecture Review

**Prepared by:** Agent 06 — Quality Review Agent  
**Date:** 2026-08-04  
**System:** HRMS (Human Resource Management System), Oracle Forms 12c / Oracle Database PL/SQL  
**Version:** v4.2 Build 2024.03.15

---

## What Was Extracted

The D1 Application Architecture extraction produced a complete structural map of the HRMS system from 38 source files. The following was confirmed:

**Found: 11 packages, 118 public procedures/functions, 6 forms, 2 form libraries, 6 DB triggers, 22 tables, 6 views, 30 sequences, 11 business modules, 23 violations, 12 risks**

The system is a monolithic Oracle Forms / PL/SQL HRMS covering six functional domains: Employee lifecycle, Leave management, Payroll, Performance reviews, Reporting, and External integration. All business logic resides in the Oracle Database. The Oracle Forms application is a thick-client UI that talks directly to PL/SQL packages via stored procedure calls. There is no REST API, no middleware, no microservices, and no caching layer.

---

## Critical Security Findings (Present Production Vulnerabilities — Act Immediately)

Three security issues must be remediated before the system is exposed to any non-isolated network. These are not migration risks — they are active vulnerabilities in the currently running system.

**1. Authentication Does Not Work (AV-004, RISK-001 — CRITICAL)**  
`PKG_SECURITY.authenticate` creates a valid session for any user who knows another user's email address. The password parameter is accepted but never compared to a stored hash. Any person with network access to Oracle Forms can log in as any employee by supplying their email alone.

**2. SSN Encryption Key Is Exposed in Source Code (AV-002, RISK-002 — CRITICAL)**  
The AES-256 key used to encrypt every stored SSN is the string literal `HR$ystem_3ncrypt10n_K3y_2024!!` embedded in `PKG_SECURITY.pkb`. Any developer or DBA with package source read access can decrypt the entire SSN dataset. The key must be rotated and stored in Oracle Wallet; all `SSN_ENCRYPTED` column values must be re-encrypted before migration.

**3. SQL Injection in Employee Search (AV-001, RISK-003 — CRITICAL)**  
`PKG_EMPLOYEE.search_employees` concatenates `p_last_name` and `p_first_name` directly into a dynamic SQL string. Any authenticated user can inject arbitrary SQL through the employee search form and access or modify any data in the HRMS schema. Fix is a one-line change: replace concatenation with bind variables.

---

## System Inventory

| Domain | Package | Public Members | Key Tables | Status |
|---|---|---|---|---|
| Employee | PKG_EMPLOYEE | 18 | EMPLOYEES, DEPARTMENTS, JOB_TITLES, JOB_GRADES, EMPLOYEE_HISTORY | Functional — SQL injection |
| Leave | PKG_LEAVE | 14 | LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES, HOLIDAYS | Functional — half-day overlap bug |
| Payroll | PKG_PAYROLL | 18 | PAYROLL_RUNS, PAYROLL_DETAILS, SALARY_RECORDS, PAY_PERIODS | Functional — YTD always zero |
| Performance | PKG_PERFORMANCE | 12 | PERFORMANCE_REVIEWS, REVIEW_CYCLES, PERFORMANCE_GOALS | Functional |
| Notification | PKG_NOTIFICATION | 4 | NOTIFICATION_QUEUE | Functional — no SMTP pooling |
| Integration | PKG_INTEGRATION | 5 | — | 2 of 5 procedures are stubs (T&A, org sync) |
| Reporting | PKG_REPORTING | 8 | 6 views | Functional — refresh_reporting_tables is stub |
| Security | PKG_SECURITY | 8 | USER_SESSIONS | Non-functional authentication |
| Audit | PKG_AUDIT | 3 | AUDIT_LOG | Functional — 365-day default retention |
| Validation | PKG_VALIDATION | 8 | — | Functional — server/client validation drift |
| Common | PKG_COMMON | 17 | SYSTEM_PARAMETERS | Functional |
| **Total** | **11 packages** | **118** | **22 tables, 6 views, 30 sequences** | |

---

## Migration-Blocking Issues (6 Total)

These must be resolved before or during migration. Migrating around them will produce a system that fails in production:

| Blocker ID | Description | Resolution |
|---|---|---|
| AV-001 | SQL injection in `search_employees` via string concatenation | Replace concatenation with `:p_last_name` bind variables |
| AV-002 | SSN encryption key hard-coded in source | Move key to Oracle Wallet; re-encrypt all SSN_ENCRYPTED rows |
| AV-003 | MD5 used for password hashing (unsalted, broken) | Replace with bcrypt/PBKDF2; rehash on next login |
| AV-004 | Password check not implemented in `authenticate` | Implement hash comparison against USER_CREDENTIALS |
| AV-005 | FTP credentials stored cleartext in SYSTEM_PARAMETERS | Move to Oracle Wallet or secrets manager |
| AV-010 | PKG_EMPLOYEE ↔ PKG_PAYROLL circular dependency | Must be broken before either module can be independently deployed |

---

## Data Integrity Warnings

**YTD fields always zero.** Every `get_payslip` response returns `YTD_GROSS = 0` and `YTD_NET = 0` — these are hard-coded placeholder values in `PKG_PAYROLL.calculate_employee_pay`. W-2 generation, tax compliance reporting, and any YTD compensation display is non-functional. Historical YTD must be reconstructed by summing `PAYROLL_DETAILS` by employee and calendar year before migration.

**Partial payroll commits produce irrecoverable state.** `calculate_payroll` commits after every 50 employees. A mid-run failure leaves some employees calculated and others not, with no automated detection or repair path. The target system must implement idempotent re-run capability or a staging table pattern.

**Time & Attendance import never runs.** `PKG_INTEGRATION.import_time_attendance` opens the CSV file but the parsing logic is a TODO comment stub. No time data has ever been imported through this path.

---

## Key Business Rules (Source-Verified Numeric Values)

| Rule | Value | Source |
|---|---|---|
| Fiscal year start | October 1 — month >= 10 → FY = calendar year + 1 | `PKG_COMMON.get_fiscal_year` |
| Leave backdating limit | 5 calendar days past | `PKG_LEAVE.submit_leave_request` error -20211 |
| Session timeout | 30 minutes from LOGIN_TIME — no activity refresh | `PKG_SECURITY.is_session_valid`, constant `c_session_timeout_min` |
| Hire date future limit — form | 90 days | `HRMS_EMPLOYEE.xml` WHEN-VALIDATE-ITEM |
| Hire date future limit — database | 180 days | `TRG_EMP_BEFORE_INSERT` error -20501 — **CONFLICT with form** |
| SS wage base 2024 | $168,600 | `PKG_PAYROLL` constant `c_ss_wage_base_2024` |
| SS employee rate | 6.2% | `PKG_PAYROLL` constant `c_ss_rate` |
| Medicare base rate | 1.45% | `PKG_PAYROLL` constant `c_medicare_rate` |
| Medicare additional rate | 0.9% above $200,000 YTD | `PKG_PAYROLL` constants `c_medicare_addl_rate`, `c_medicare_addl_threshold` |
| Federal standard deduction — single | $14,600 | `PKG_PAYROLL` constant `c_standard_deduction_single` |
| Federal standard deduction — married joint | $29,200 | `PKG_PAYROLL` constant `c_standard_deduction_married` |
| Per W-4 allowance reduction | $4,300 | `PKG_PAYROLL` constant `c_allowance_amount` |
| Audit retention default | 365 days | `PKG_AUDIT.purge_old_records` default parameter |
| Notification retry max | 3 attempts | `PKG_NOTIFICATION.retry_failed` default parameter |
| EMP_NUMBER format | EMP-NNNNNN (6-digit zero-padded) | `PKG_VALIDATION.validate_emp_number_format` regex |

**DISC-001 — Hire Date Conflict (Unresolved):** Form validation blocks hire dates more than 90 days in the future. The database trigger permits up to 180 days. A direct SQL insert or future API call with a date between day 91 and day 180 would succeed at the DB layer but fail through the form. The authoritative rule must be decided by the business before the target system is designed.

---

## Recommended Migration Sequence (Strangler Fig)

Based on module coupling scores from `dependency-graph.json`:

| Phase | Module(s) | Rationale |
|---|---|---|
| 1 | Notification, Audit | Zero outbound dependencies. Pure infrastructure concerns. Notification maps directly to a message broker + email API. Audit maps to an append-only event log. |
| 2 | Leave, Performance | Low coupling. Standard bounded contexts. Both only read Employee data; neither mutates it. |
| 3 | Reporting, Integration | Reporting is read-only; replace with a BI tool. Integration is mostly stubs — rewrite from scratch against target APIs. |
| 4 | Security | Can be replaced with OAuth2/OIDC independently of domain modules once the other modules expose API boundaries. |
| 5 (Last) | Employee + Payroll together | Circular dependency means these cannot be migrated independently. Must redesign both simultaneously, or introduce a shared lower-layer service to break the cycle first. SSN re-encryption must precede this phase. |

**Do not migrate Employee without Payroll.** The call chain `create_employee → create_salary_record` and `calculate_payroll → is_active` create a bidirectional runtime dependency. Both packages must be live in the same deployment context or the cycle must be broken by a shared intermediate service first.

---

## Open Questions (Cannot Be Answered From Source Alone)

| # | Question | Why It Matters |
|---|---|---|
| 1 | Where is USER_CREDENTIALS DDL? | PKG_SECURITY references it; if it exists, password hashes need migration or reset |
| 2 | HRMS_ADMIN.fmb content? | Administration functionality is a complete unknown |
| 3 | HRMS_REPORTS.fmb content? | Reporting UI is a complete unknown |
| 4 | DBMS_SCHEDULER job definitions? | Monthly accrual, 5-minute notification dispatch — must be documented from DBA_SCHEDULER_JOBS before migration |
| 5 | Oracle Directory OS filesystem paths? | GL_FEED_OUT, BENEFITS_FEED_OUT, TIME_ATTENDANCE_IN, PAYROLL_OUTPUT are object names; actual server paths are unknown |
| 6 | Is the authentication stub intentional? | If the system is in production with no password check, there is likely an external auth layer (proxy, middleware) not visible in source |
| 7 | Is TAX_BRACKETS table populated? | The table is defined in DDL; PKG_PAYROLL does not use it; if it contains historical data it must be assessed for migration |

---

## Pass 2 Findings: Additional Critical Observations [EDGE-CASE-FOUND]

A second independent analysis pass identified the following gaps not present in the first pass:

**[EDGE-CASE-FOUND] CF-002 (Hire New Employee) is inaccurate for the form-driven path.** HRMS_EMPLOYEE.fmb PRE-INSERT calls `generate_emp_number` and commits via Oracle Forms block DML. It does NOT call `PKG_EMPLOYEE.create_employee`. This means steps 5–7 of CF-002 (salary record creation, audit, welcome email notification, manager notification) do not fire through the form. A new hire created through the UI has no initial salary record and receives no welcome email.

**[EDGE-CASE-FOUND] HRMS_PERFORMANCE.fmb bypasses PKG_PERFORMANCE procedures entirely.** The PERFORMANCE_REVIEW block is UpdateAllowed=Yes and users save assessments via direct Oracle Forms DML (COMMIT_FORM). `PKG_PERFORMANCE.submit_self_assessment` and `submit_manager_review` are never called through the form, meaning the notification side-effects (manager notified of self-assessment; employee notified of review completion) never fire in normal use.

**[EDGE-CASE-FOUND] DISC-002 (SSN Validation Drift) — new undocumented conflict.** Client-side HRMS_VALIDATION_LIB.validate_ssn checks that SSN segments (area, group, serial) are not all-zeros. Server-side PKG_COMMON.is_valid_ssn does not. SSNs with zero-segment values can be stored via non-form paths but will fail form validation on retrieval. Comparable to the documented email drift (AV-014) but absent from the violation register.

**[EDGE-CASE-FOUND] 21+ package procedures have no confirmed form entry point.** Lifecycle-critical operations — `terminate_employee`, `transfer_employee`, `promote_employee` — are not called from any confirmed form. Their notification and integration side-effects (manager termination alert, COBRA TODO, access revocation TODO, salary change on promotion) are never triggered through the UI.

**4 additional violations identified in Pass 2** (see quality-review.md QR-018a, QR-019, QR-021, QR-022): HRMS_PERFORMANCE bypass; SSN validation drift DISC-002; PKG_SECURITY.authenticate TOO_MANY_ROWS account-takeover path; PKG_PAYROLL.reverse_payroll silently discarding the reversal reason.

---

## Pass 3 Findings: Schema and Operational Correctness [EDGE-CASE-FOUND]

A third independent analysis pass identified 8 further findings not present in passes 1 or 2:

**DISC-003 (Critical) — EMPLOYEE_HISTORY write-path schema conflict.** `TRG_EMP_BEFORE_UPDATE` inserts into EMPLOYEE_HISTORY using column names `HISTORY_ID`, `CHANGE_DATE`, `OLD_VALUE`, `NEW_VALUE` (generic schema). `PKG_EMPLOYEE.log_history` inserts using `HIST_ID`, `EFFECTIVE_DATE`, `OLD_DEPT_ID`, `NEW_DEPT_ID`, `OLD_JOB_ID`, etc. (typed schema). Both use SEQ_EMP_HISTORY for the PK. One of these INSERT statements fails at runtime with ORA-00904 (invalid column name). The actual EMPLOYEE_HISTORY DDL in the live database must be inspected to determine which path is broken. Any data migration reading EMPLOYEE_HISTORY for lifecycle history must account for this.

**QR-030 (Medium) — run_monthly_accrual is non-idempotent.** A duplicate DBMS_SCHEDULER execution doubles leave accrual balances for all active employees. This is the same idempotency gap as AV-016 (expire_carryover) but higher-impact because it affects all employees monthly.

**QR-032 (Medium) — change_password does not verify the old password.** `p_old_password` is never checked against stored credentials. Once AV-004 is fixed (password verification implemented), this becomes an authenticated privilege escalation vector. **AV-004 must not be deployed without simultaneously fixing change_password, or any authenticated user can reset any other user's password without knowing it.**

**QR-028 (Medium) — reverse_payroll has no status gate.** Every other PKG_PAYROLL state-mutation procedure checks the run's current status before proceeding. `reverse_payroll` does not. An approved, GL-exported, funded payroll run can be reversed unconditionally by any authenticated session.

**QR-027 (Medium) — Business-day function holiday parity gap.** `PKG_COMMON.business_days_between` and `add_business_days` do not query the HOLIDAYS table. `PKG_LEAVE.calculate_business_days` does. Any migration target that replaces PKG_COMMON date utilities without replicating holiday awareness will silently produce wrong business-day counts outside the leave module.

**QR-029 (Low) — Non-EMAIL notifications queue forever.** `process_queue` only dispatches `NOTIFICATION_TYPE='EMAIL'`. All other type values accumulate in NOTIFICATION_QUEUE indefinitely.

**QR-031 (Low) — promote_employee has no status check.** A terminated or suspended employee can receive a promotion, creating an active salary record without a rehire.

**QR-033 (Low) — Double EMPLOYEE_HISTORY writes.** Package lifecycle procedures (transfer, terminate, promote) each call `log_history` and then perform a DML UPDATE that fires `TRG_EMP_BEFORE_UPDATE`, which also writes to EMPLOYEE_HISTORY. Each lifecycle event produces two history records. Audit queries and migration tooling will count double.

---

## Extraction Quality

The D1 extraction by Agent 1 is assessed **PARTIAL** by the quality review gate across all three passes. The structural extraction is accurate and evidence-backed. Pass 1 identified 3 minor count inconsistencies. Pass 2 identified 4 high/medium analysis-layer gaps: CF-002 call-flow inaccuracy, HRMS_PERFORMANCE bypass of notification procedures, SSN validation drift absent from violation register, and orphaned lifecycle procedure inventory missing. Pass 3 identified 8 further findings including one critical schema inconsistency (DISC-003: EMPLOYEE_HISTORY broken write path) and a fix-order dependency between AV-004 and QR-032 that must be understood before any security remediation begins. See `quality-review.md` for the complete issue register (QR-001 through QR-033).
