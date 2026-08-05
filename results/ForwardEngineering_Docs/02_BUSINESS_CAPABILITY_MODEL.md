# 02 — Business Capability Model
**System:** Acme Corporation HRMS (Oracle 19c / Oracle Forms 12c)
**Version:** 1.0
**Date:** 2026-08-05
**Author:** Business Architecture Track
**Scope:** Full capability inventory derived from BA, DA, TA, and AA multi-pass analysis of the Acme HRMS Oracle codebase (PKG_EMPLOYEE, PKG_PAYROLL, PKG_LEAVE, PKG_PERFORMANCE, PKG_SECURITY, PKG_INTEGRATION, PKG_NOTIFICATION, PKG_REPORTING, PKG_COMMON, Oracle Forms 12c, and all supporting schema objects).

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Capability Map — L1 and L2](#2-business-capability-map)
3. [Capability Heat Map — Risk and Improvement Status](#3-capability-heat-map)
4. [Capability-to-System Mapping](#4-capability-to-system-mapping)
5. [Capability Gaps — Future System Requirements](#5-capability-gaps)
6. [Investment Priority — Migration Sequencing](#6-investment-priority)
7. [Capability Maturity Assessment — Current vs. Target](#7-capability-maturity-assessment)
8. [Appendix — Evidence Trail](#8-appendix-evidence-trail)

---

## 1. Executive Summary

The Acme HRMS Oracle system was designed to cover nine L1 business domains. Across those domains the analysis team identified **44 confirmed business rules, 80+ technical debt items, 32 data quality defects, and 25 architecture violations**. The headline finding is structural: **four of the nine L1 capabilities are partially or entirely unimplemented in production code despite being represented in the schema or user interface**. Specifically:

- **Payroll Disbursement** — `EMPLOYEE_BANK_ACCOUNTS` is fully modelled but never read during payroll; every net-pay disbursement is manual.
- **Workforce Offboarding** — COBRA notification, final-pay calculation (`calculate_final_pay` does not exist), and access revocation are all TODO stubs.
- **Performance Calibration** — `CALIBRATED_RATING` and `CALIBRATION_NOTES` exist in the schema but no PL/SQL procedure writes to either column.
- **Workforce Integration** — `sync_org_structure`, `import_time_attendance`, and `refresh_reporting_tables` are stubs that log false-success messages.

The target migration must close these gaps before go-live. The investment priority model below sequences capability delivery to close critical compliance risks first, then operational gaps, then strategic improvements.

---

## 2. Business Capability Map

### 2.1 L1 Capability Domains

| L1 ID | L1 Capability Domain | Description |
|-------|----------------------|-------------|
| L1-01 | Workforce Management | Hiring, position management, org structure, and employee lifecycle |
| L1-02 | Compensation & Payroll | Salary administration, payroll calculation, tax, and disbursement |
| L1-03 | Leave & Absence Management | Leave accrual, balance tracking, request workflows, and approvals |
| L1-04 | Performance Management | Review cycles, goal setting, rating, and calibration |
| L1-05 | Benefits Administration | Plan management, enrollment, dependent tracking, and vendor feeds |
| L1-06 | Security & Identity | Authentication, authorisation, session management, and audit |
| L1-07 | Organisational Intelligence | Reporting, analytics, compliance reporting, and dashboards |
| L1-08 | System Integration | External system feeds, data import/export, and API surfaces |
| L1-09 | Platform Operations | Configuration, monitoring, logging, CI/CD, and deployment |

---

### 2.2 L2 Capability Detail

#### L1-01 — Workforce Management

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-01-01 | Employee Record Management | **Implemented** | PKG_EMPLOYEE.create_employee, update_employee; EMPLOYEES table |
| L2-01-02 | New Hire Onboarding | **Partial** | create_employee populates EMPLOYEES; no onboarding checklist, no provisioning workflow |
| L2-01-03 | Employee Transfer & Promotion | **Implemented** | PKG_EMPLOYEE.transfer_employee, promote_employee |
| L2-01-04 | Employment Termination | **Partial** — 3 of 6 sub-steps are stubs | terminate_employee: COBRA=TODO, calculate_final_pay=nonexistent, revoke_access procedure=nonexistent |
| L2-01-05 | Organisational Structure Maintenance | **Stub only** | DEPARTMENTS table maintained; PKG_INTEGRATION.sync_org_structure is a 2-line stub that logs "Org structure sync completed" and does nothing else |
| L2-01-06 | Position & Grade Management | **Implemented** | JOB_POSITIONS, JOB_TITLES, JOB_GRADES; grade-based salary range enforcement (soft warning only — TD-74) |
| L2-01-07 | Headcount & Workforce Reporting | **Partial** | PKG_REPORTING.headcount_report queries OLTP directly; RPT_HEADCOUNT table exists but is never populated |
| L2-01-08 | Workforce Compliance Tracking | **Absent** | No FMLA document requirement enforcement (FMLA seed REQUIRES_DOCUMENT='N' — TD-71); no EEO tracking outside ad-hoc report |

#### L1-02 — Compensation & Payroll

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-02-01 | Salary Record Administration | **Implemented** | SALARY_RECORDS with effective-dated history; PKG_COMPENSATION |
| L2-02-02 | Salary Grade Band Enforcement | **Partial** | Grade range checked in PKG_EMPLOYEE.create_employee debug mode only; validate_salary_range emits MESSAGE not FORM_TRIGGER_FAILURE (TD-74) |
| L2-02-03 | Payroll Run Execution | **Implemented** | PKG_PAYROLL.create_payroll_run, calculate_payroll, approve_payroll; PAYROLL_RUNS/PAYROLL_DETAILS |
| L2-02-04 | Tax Calculation | **Partial** | Federal and state tax computed; HEAD_OF_HOUSEHOLD branch returns $0 federal tax (defect — BR-xx); state flat rate, no local tax |
| L2-02-05 | Deduction Processing | **Implemented** | DEDUCTION_RECORDS, PKG_PAYROLL pay element handling |
| L2-02-06 | Net Pay Disbursement (ACH/Direct Deposit) | **Absent** | EMPLOYEE_BANK_ACCOUNTS fully modelled; zero PL/SQL references to the table in payroll path; prenote never sent; no NACHA file generation (BA supplement — BR-BA-12, PP-BA-01) |
| L2-02-07 | Final Pay Calculation on Termination | **Absent** | PKG_PAYROLL.calculate_final_pay does not exist; termination procedure references it as a TODO comment (BR-TERM-07) |
| L2-02-08 | Off-Cycle Payroll | **Absent** | No off-cycle capability; no support for mid-period termination pay |
| L2-02-09 | Payroll GL Feed | **Implemented** | PKG_INTEGRATION.generate_gl_journal produces pipe-delimited file; no confirmation/status feedback to PAYROLL_RUNS (TD-80) |
| L2-02-10 | Merit Pay (Performance-Linked) | **Partial** | Rating ≥ 3 gates merit eligibility (conformist link BC-04→BC-02); CALIBRATED_RATING never used |

#### L1-03 — Leave & Absence Management

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-03-01 | Leave Balance Initialisation | **Implemented** | PKG_LEAVE.initialize_balances |
| L2-03-02 | Leave Accrual (Monthly) | **Partial — defect** | run_monthly_accrual has accrual overwrite defect: uses SET ACCRUED = v_accrued instead of += v_accrued on retry (BR-LIB-05) |
| L2-03-03 | Leave Request Submission | **Implemented** | PKG_LEAVE.submit_leave_request; LEAVE_REQUESTS table |
| L2-03-04 | Leave Approval Workflow | **Implemented** | Manager approval path in PKG_LEAVE |
| L2-03-05 | FMLA Leave Enforcement | **Partial** | FMLA leave type exists in LEAVE_TYPES; REQUIRES_DOCUMENT='N' in seed data — FMLA documentation not required (TD-71) |
| L2-03-06 | Leave Balance Reporting | **Partial** | PKG_REPORTING.leave_utilization_report; CALENDAR_YEAR missing from projection — multi-year snapshots unsupported (DA DQ-032) |
| L2-03-07 | Leave Balance Payout on Termination | **Absent** | terminate_employee does not read or modify LEAVE_BALANCES |

#### L1-04 — Performance Management

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-04-01 | Review Cycle Management | **Implemented** | PKG_PERFORMANCE.create_review; REVIEW_CYCLES, PERFORMANCE_REVIEWS |
| L2-04-02 | Self-Assessment Submission | **Implemented** | PKG_PERFORMANCE.submit_self_assessment |
| L2-04-03 | Manager Review Submission | **Implemented** | PKG_PERFORMANCE.submit_manager_review; OVERALL_RATING 1–5, RATING_LABEL mapped |
| L2-04-04 | Employee Acknowledgement | **Implemented** | PKG_PERFORMANCE.acknowledge_review |
| L2-04-05 | Goal Setting & Tracking | **Partial** | PERFORMANCE_GOALS, GOAL_REVIEWS tables exist; goal-to-review linkage present |
| L2-04-06 | Rating Calibration | **Absent** | CALIBRATED_RATING and CALIBRATION_NOTES columns exist in schema; zero write paths in PKG_PERFORMANCE; no calibration status transition; get_rating_distribution reads OVERALL_RATING (pre-calibration value) |
| L2-04-07 | Team & Org Rating Distribution | **Partial** | get_rating_distribution and get_team_reviews implemented; reads wrong (uncalibrated) column |
| L2-04-08 | Performance-to-Compensation Linkage | **Partial** | Rating read by PKG_PAYROLL as eligibility gate; no automated merit-increase calculation |

#### L1-05 — Benefits Administration

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-05-01 | Benefit Plan Management | **Implemented** | BENEFIT_PLANS table; plan configuration |
| L2-05-02 | Benefit Enrolment | **Implemented** | BENEFIT_ENROLLMENTS; PKG_INTEGRATION references |
| L2-05-03 | Dependent Management | **Partial** | EMPLOYEE_DEPENDENTS fully modelled; BENEFITS_ENROLLED flag never read in export; SSN decrypt path for dependents undocumented |
| L2-05-04 | ADP Benefits Feed Export | **Implemented — gaps** | PKG_INTEGRATION.export_benefits_feed produces 203-char fixed-width ADP file; BENEFITS_ENROLLED filter absent; no record count trailer; no format version (TD-73) |
| L2-05-05 | COBRA Administration | **Absent** | terminate_employee has TODO comment; zero COBRA notification logic; federal 14-day notification deadline not met on any termination (PP-TERM-01, BR-TERM-01) |
| L2-05-06 | Open Enrolment Management | **Absent** | No open enrolment workflow, eligibility event processing, or enrolment window management found |
| L2-05-07 | Benefits Eligibility Rules | **Partial** | Dependent relationship constrained to 5 values; age-based or employment-status-based eligibility not implemented |

#### L1-06 — Security & Identity

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-06-01 | User Authentication | **Stub** | PKG_SECURITY.authenticate never verifies password against USER_CREDENTIALS; any valid username authenticates (BR-042, DQ-003) |
| L2-06-02 | Session Management | **Partial** | USER_SESSIONS created on login; 30-min timeout hard-coded (BR-026); timeout evaluated only on next call, not background sweep; stale sessions accumulate (TD-75) |
| L2-06-03 | Role-Based Access Control | **Partial** | Grade-based RBAC: Grade ≥ 8 full, 5–7 view-all, < 5 own-only (BR-021); coarse-grained — no fine-grained object permissions |
| L2-06-04 | Password Management | **Partial — defect** | change_password enforces complexity (min 8, uppercase, digit) but never verifies old password (BR-044, DQ-029); MD5 hashing (DQ-010) |
| L2-06-05 | Account Lockout & Brute-Force Protection | **Absent** | No lockout mechanism; LOGIN_ATTEMPTS column not tracked; e_account_locked declared but never raised (BR-045, DQ-023) |
| L2-06-06 | Encryption at Rest | **Partial** | AES-256 for employee SSN, bank account numbers; routing numbers stored plaintext (TD-46); hard-coded encryption key in source (TD-01, DQ-001) |
| L2-06-07 | Access Revocation on Termination | **Partial** | New logins blocked by EMPLOYMENT_STATUS check; active sessions survive up to 30 min; PKG_SECURITY.revoke_access procedure does not exist (BR-TERM-06) |
| L2-06-08 | Audit Logging | **Partial** | PKG_COMMON.log_error / log_info write to AUDIT_LOG; ERROR, INFO, and DML events mixed in one table (TD-37); no structured format; no correlation ID |
| L2-06-09 | Privileged Access Management | **Absent** | No DBA/elevated-privilege workflow; no portal DB user separation; portal likely connects as schema owner (TD-81) |

#### L1-07 — Organisational Intelligence

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-07-01 | Headcount Reporting | **Implemented** | PKG_REPORTING.headcount_report; FT/PT/CONTRACT/gender splits, tenure |
| L2-07-02 | Compensation Analytics | **Implemented** | PKG_REPORTING.compensation_summary; compa-ratio, median (Oracle MEDIAN()) |
| L2-07-03 | Turnover Reporting | **Partial** | PKG_REPORTING.turnover_report implemented; non-standard denominator (hires, not avg headcount) makes SHRM comparison invalid (BR-044) |
| L2-07-04 | New Hire Reporting | **Implemented** | PKG_REPORTING.new_hires_report; row-level, includes manager, salary, location |
| L2-07-05 | Leave Utilisation Reporting | **Partial — defect** | PKG_REPORTING.leave_utilization_report; CALENDAR_YEAR missing from projection (DQ-032) |
| L2-07-06 | Payroll Summary Reporting | **Partial** | PKG_Reporting.payroll_summary_report; magic numbers for element IDs 100–103; excludes ERROR rows silently |
| L2-07-07 | EEO Compliance Reporting | **Partial** | eeo_compliance_report implemented; GENDER has no CHECK constraint — arbitrary values distort output (TD-40) |
| L2-07-08 | Denormalised Reporting Layer (RPT_* tables) | **Stub** | 7 RPT_* tables inferred from code; refresh_reporting_tables logs "Reporting tables refreshed" and does nothing; all reports query OLTP directly (DA BR-043) |
| L2-07-09 | Executive Dashboards | **Absent** | No dashboard layer; no BI tool integration; RPT_* stub prevents any offline/ad-hoc reporting without OLTP load |
| L2-07-10 | Predictive Workforce Analytics | **Absent** | No ML/AI capability; no trend analysis; not in scope for current system |

#### L1-08 — System Integration

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-08-01 | ADP Benefits File Export | **Implemented — gaps** | See L2-05-04 |
| L2-08-02 | Oracle Financials GL Feed | **Implemented — gaps** | generate_gl_journal; no GL_FEED_STATUS feedback column; no missed-feed detection (TD-80) |
| L2-08-03 | NACHA ACH Payroll Disbursement | **Absent** | No NACHA file generation; EMPLOYEE_BANK_ACCOUNTS never read; prenote not implemented (PP-BA-01, PP-BA-03) |
| L2-08-04 | Time & Attendance Import | **Stub** | PKG_INTEGRATION.import_time_attendance: UTL_FILE CSV read, per-line error continuation, but no INSERT to any table; destination TIME_ATTENDANCE_RECORDS table has no DDL; no link to PAYROLL_DETAILS (DA DQ-031) |
| L2-08-05 | LDAP / Active Directory Sync | **Absent** | sync_org_structure: 2-line stub, no LDAP connection parameters, logs false success (BR-ORG-01, BR-ORG-02) |
| L2-08-06 | API Surface (REST/SOAP) | **Absent** | No REST or SOAP endpoint definitions found; all integration via flat file or direct DB call |
| L2-08-07 | Inbound Data Validation | **Absent** | No file format version, no record count validation on ADP or GL feeds; silent truncation possible (TD-73) |
| L2-08-08 | Integration Error Handling & Retry | **Partial** | Per-line error continuation in import_time_attendance; no retry queue; no dead-letter concept |

#### L1-09 — Platform Operations

| L2 ID | L2 Capability | Current Status | Key Evidence |
|-------|---------------|----------------|--------------|
| L2-09-01 | Configuration Management | **Partial** | SYSTEM_PARAMETERS table; APP_VERSION static row; some params ignored at runtime (session timeout hard-coded) |
| L2-09-02 | Automated Build | **Absent** | No build pipeline; Oracle Forms .fmb→.fmx compilation is manual; no build script (TD-76) |
| L2-09-03 | Automated Testing | **Absent** | Zero test files in repository; no test framework |
| L2-09-04 | Continuous Integration | **Absent** | No CI tooling (GitHub Actions, Jenkins, GitLab CI, etc.) |
| L2-09-05 | Automated Deployment | **Absent** | Manual DBA SQL*Plus script application; no deployment automation |
| L2-09-06 | Secret / Credential Management | **Absent** | AES-256 key hard-coded in source (TD-01); FTP credentials cleartext (TD-10); no secret manager integration |
| L2-09-07 | Structured Observability | **Absent** | DBMS_OUTPUT for debug; AUDIT_LOG for events; no structured log format; no correlation ID; no APM tooling |
| L2-09-08 | Alerting & Incident Response | **Absent** | No alerting; no on-call tooling integration |
| L2-09-09 | Database Backup & Recovery | **Unknown** | No backup scripts in repository; assumed to be DBA-managed outside application layer |
| L2-09-10 | Rollback / Disaster Recovery | **Absent** | No rollback mechanism in application; schema changes require manual DBA intervention |

---

## 3. Capability Heat Map

The heat map categorises each L2 capability by **current health** (Green / Amber / Red / Black) and **business risk if unchanged** (Low / Medium / High / Critical).

| Colour | Meaning |
|--------|---------|
| Green | Implemented and functioning correctly |
| Amber | Implemented with known defects or gaps |
| Red | Partially implemented — material functionality missing |
| Black | Stub or entirely absent — capability does not exist |

### 3.1 Heat Map Table

| L2 ID | Capability | Health | Business Risk | Primary Risk Driver |
|-------|-----------|--------|---------------|---------------------|
| L2-01-01 | Employee Record Management | Green | Low | — |
| L2-01-02 | New Hire Onboarding | Amber | Medium | No provisioning workflow |
| L2-01-03 | Employee Transfer & Promotion | Green | Low | — |
| L2-01-04 | Employment Termination | Red | **Critical** | COBRA, final pay, access revocation all absent |
| L2-01-05 | Org Structure Maintenance | Black | High | Sync stub logs false success |
| L2-01-06 | Position & Grade Management | Amber | Medium | Salary band validation is non-blocking |
| L2-01-07 | Headcount Reporting | Amber | Low | RPT tables never populated |
| L2-01-08 | Workforce Compliance | Black | High | FMLA document enforcement absent |
| L2-02-01 | Salary Record Administration | Green | Low | — |
| L2-02-02 | Salary Grade Band Enforcement | Amber | Medium | Validation is warning-only in debug mode |
| L2-02-03 | Payroll Run Execution | Green | Low | — |
| L2-02-04 | Tax Calculation | Amber | High | HEAD_OF_HOUSEHOLD $0 federal tax defect |
| L2-02-05 | Deduction Processing | Green | Low | — |
| L2-02-06 | Net Pay Disbursement (ACH) | Black | **Critical** | Bank accounts never read; all pay is manual |
| L2-02-07 | Final Pay on Termination | Black | **Critical** | Procedure does not exist |
| L2-02-08 | Off-Cycle Payroll | Black | High | No off-cycle capability at all |
| L2-02-09 | Payroll GL Feed | Amber | Medium | No feed-status tracking; missed feed undetectable |
| L2-02-10 | Merit Pay | Amber | Medium | Calibrated rating never used |
| L2-03-01 | Leave Balance Initialisation | Green | Low | — |
| L2-03-02 | Leave Accrual | Amber | High | Overwrite defect on accrual retry |
| L2-03-03 | Leave Request Submission | Green | Low | — |
| L2-03-04 | Leave Approval Workflow | Green | Low | — |
| L2-03-05 | FMLA Leave Enforcement | Amber | High | Document not required by seed data |
| L2-03-06 | Leave Balance Reporting | Amber | Medium | Multi-year reporting broken |
| L2-03-07 | Leave Balance Payout on Termination | Black | High | Termination ignores leave balances |
| L2-04-01 | Review Cycle Management | Green | Low | — |
| L2-04-02 | Self-Assessment Submission | Green | Low | — |
| L2-04-03 | Manager Review Submission | Green | Low | — |
| L2-04-04 | Employee Acknowledgement | Green | Low | — |
| L2-04-05 | Goal Setting & Tracking | Amber | Medium | Goal-to-outcome linkage incomplete |
| L2-04-06 | Rating Calibration | Black | High | Dead columns; no workflow implemented |
| L2-04-07 | Rating Distribution | Amber | Medium | Reads uncalibrated column |
| L2-04-08 | Performance-to-Compensation Linkage | Amber | Medium | No automated calculation |
| L2-05-01 | Benefit Plan Management | Green | Low | — |
| L2-05-02 | Benefit Enrolment | Green | Low | — |
| L2-05-03 | Dependent Management | Amber | High | BENEFITS_ENROLLED not filtered; SSN decrypt gap |
| L2-05-04 | ADP Benefits Feed Export | Amber | Medium | No trailer, no version, BENEFITS_ENROLLED ignored |
| L2-05-05 | COBRA Administration | Black | **Critical** | Federal compliance gap on every termination |
| L2-05-06 | Open Enrolment Management | Black | High | Entirely absent |
| L2-05-07 | Benefits Eligibility Rules | Amber | Medium | No age/status eligibility enforcement |
| L2-06-01 | User Authentication | Black | **Critical** | Password never verified — any username authenticates |
| L2-06-02 | Session Management | Amber | High | Stale sessions accumulate; no background sweep |
| L2-06-03 | Role-Based Access Control | Amber | Medium | Coarse grade-based only; no object-level permissions |
| L2-06-04 | Password Management | Amber | High | Old password not verified; MD5 hashing |
| L2-06-05 | Account Lockout | Black | **Critical** | Zero brute-force protection |
| L2-06-06 | Encryption at Rest | Amber | High | Hard-coded key; routing numbers plaintext |
| L2-06-07 | Access Revocation on Termination | Amber | High | Active sessions survive; revoke procedure absent |
| L2-06-08 | Audit Logging | Amber | Medium | Mixed table; no structure; no correlation |
| L2-06-09 | Privileged Access Management | Black | High | Portal likely connects as schema owner |
| L2-07-01 | Headcount Reporting | Green | Low | — |
| L2-07-02 | Compensation Analytics | Green | Low | — |
| L2-07-03 | Turnover Reporting | Amber | Medium | Non-standard denominator |
| L2-07-04 | New Hire Reporting | Green | Low | — |
| L2-07-05 | Leave Utilisation Reporting | Amber | Medium | Multi-year projection broken |
| L2-07-06 | Payroll Summary Reporting | Amber | Medium | Magic element IDs; silent ERROR exclusion |
| L2-07-07 | EEO Compliance Reporting | Amber | High | No GENDER check constraint; arbitrary values |
| L2-07-08 | Reporting Layer (RPT_*) | Black | High | Stub; all reports hit OLTP directly |
| L2-07-09 | Executive Dashboards | Black | Medium | Not present |
| L2-07-10 | Predictive Analytics | Black | Low | Out of scope for current system |
| L2-08-01 | ADP Benefits Feed | Amber | Medium | See L2-05-04 |
| L2-08-02 | Oracle Financials GL Feed | Amber | Medium | No status tracking; missed feeds invisible |
| L2-08-03 | NACHA ACH Disbursement | Black | **Critical** | Not implemented |
| L2-08-04 | Time & Attendance Import | Black | High | Stub; no INSERT anywhere |
| L2-08-05 | LDAP / AD Sync | Black | High | Stub; logs false success |
| L2-08-06 | API Surface | Black | Medium | No REST/SOAP layer |
| L2-08-07 | Inbound Data Validation | Black | Medium | No file validation anywhere |
| L2-08-08 | Integration Error Handling | Red | Medium | Per-line only; no retry; no dead-letter |
| L2-09-01 | Configuration Management | Amber | Medium | Runtime ignores some params |
| L2-09-02 | Automated Build | Black | High | 100% manual; no reproducible build |
| L2-09-03 | Automated Testing | Black | **Critical** | Zero tests in entire repository |
| L2-09-04 | Continuous Integration | Black | High | No CI tooling |
| L2-09-05 | Automated Deployment | Black | High | 100% manual |
| L2-09-06 | Secret Management | Black | **Critical** | Key hard-coded in source; cleartext FTP creds |
| L2-09-07 | Structured Observability | Black | High | Free-text only; no APM |
| L2-09-08 | Alerting & Incident Response | Black | Medium | None present |
| L2-09-09 | DB Backup & Recovery | Unknown | High | Outside application scope |
| L2-09-10 | Rollback / DR | Black | High | Manual DBA only |

### 3.2 Heat Map Summary

| Health | Count | % of L2 Capabilities |
|--------|-------|-----------------------|
| Green | 14 | 20% |
| Amber | 24 | 34% |
| Red | 2 | 3% |
| Black | 30 | 43% |

**Critical Business Risk items (must be resolved before migration go-live): 7**
- L2-01-04 Employment Termination
- L2-02-06 Net Pay Disbursement (ACH)
- L2-02-07 Final Pay on Termination
- L2-05-05 COBRA Administration
- L2-06-01 User Authentication
- L2-06-05 Account Lockout
- L2-09-06 Secret Management

---

## 4. Capability-to-System Mapping

This section maps each L1 domain to the Oracle HRMS packages, tables, and Forms components that support it.

### 4.1 Mapping Table

| L1 Domain | L2 Capability | Oracle Package(s) | Key Tables | Oracle Forms | Integration Target |
|-----------|---------------|-------------------|------------|-------------|-------------------|
| L1-01 Workforce | Employee Record Management | PKG_EMPLOYEE | EMPLOYEES, EMPLOYEE_HISTORY | HRMS_EMPLOYEE | — |
| L1-01 Workforce | Onboarding | PKG_EMPLOYEE | EMPLOYEES | HRMS_EMPLOYEE | PKG_NOTIFICATION (welcome email) |
| L1-01 Workforce | Transfer & Promotion | PKG_EMPLOYEE | EMPLOYEES, SALARY_RECORDS | HRMS_EMPLOYEE | — |
| L1-01 Workforce | Termination | PKG_EMPLOYEE | EMPLOYEES | HRMS_EMPLOYEE | PKG_PAYROLL (final pay — stub), PKG_SECURITY (revoke — stub) |
| L1-01 Workforce | Org Structure | PKG_INTEGRATION | DEPARTMENTS | — | LDAP/AD (stub) |
| L1-01 Workforce | Position & Grade | PKG_EMPLOYEE | JOB_POSITIONS, JOB_TITLES, JOB_GRADES | HRMS_EMPLOYEE | HRMS_VALIDATION_LIB |
| L1-02 Compensation | Salary Administration | PKG_COMPENSATION | SALARY_RECORDS | HRMS_SALARY | — |
| L1-02 Compensation | Payroll Execution | PKG_PAYROLL | PAYROLL_RUNS, PAYROLL_DETAILS | HRMS_PAYROLL | — |
| L1-02 Compensation | Tax Calculation | PKG_PAYROLL | PAYROLL_DETAILS, TAX_BRACKETS | HRMS_PAYROLL | — |
| L1-02 Compensation | Deductions | PKG_PAYROLL | DEDUCTION_RECORDS, DEDUCTION_TYPES | HRMS_PAYROLL | — |
| L1-02 Compensation | ACH Disbursement | (none) | EMPLOYEE_BANK_ACCOUNTS (unused) | — | NACHA (absent) |
| L1-02 Compensation | GL Feed | PKG_INTEGRATION | PAYROLL_RUNS, PAYROLL_DETAILS | — | Oracle Financials GL Import |
| L1-03 Leave | Balance Management | PKG_LEAVE | LEAVE_BALANCES, LEAVE_TYPES | HRMS_LEAVE | — |
| L1-03 Leave | Request Workflow | PKG_LEAVE | LEAVE_REQUESTS | HRMS_LEAVE, Self-Service Portal | PKG_NOTIFICATION |
| L1-04 Performance | Review Lifecycle | PKG_PERFORMANCE | PERFORMANCE_REVIEWS, REVIEW_CYCLES | HRMS_PERFORMANCE | PKG_NOTIFICATION |
| L1-04 Performance | Goal Management | PKG_PERFORMANCE | PERFORMANCE_GOALS, GOAL_REVIEWS | HRMS_PERFORMANCE | — |
| L1-04 Performance | Rating Calibration | (none) | PERFORMANCE_REVIEWS.CALIBRATED_RATING (unused) | — | — |
| L1-05 Benefits | Plan & Enrolment | PKG_INTEGRATION (partial) | BENEFIT_PLANS, BENEFIT_ENROLLMENTS | HRMS_BENEFITS | ADP (flat file export) |
| L1-05 Benefits | Dependent Management | PKG_INTEGRATION | EMPLOYEE_DEPENDENTS | HRMS_BENEFITS | ADP benefits feed |
| L1-05 Benefits | COBRA | (none) | — | — | External COBRA administrator (absent) |
| L1-06 Security | Authentication | PKG_SECURITY | USER_CREDENTIALS, USER_SESSIONS | HRMS_LOGIN | — |
| L1-06 Security | Session Management | PKG_SECURITY | USER_SESSIONS | All Forms | — |
| L1-06 Security | RBAC | PKG_SECURITY | EMPLOYEES.GRADE | All packages | — |
| L1-06 Security | Encryption | PKG_SECURITY | EMPLOYEES (SSN), EMPLOYEE_BANK_ACCOUNTS | — | — |
| L1-06 Security | Audit | PKG_COMMON | AUDIT_LOG | — | — |
| L1-07 Reporting | Operational Reports | PKG_REPORTING | EMPLOYEES, DEPARTMENTS, PAYROLL_*, LEAVE_*, PERFORMANCE_REVIEWS | HRMS_REPORTS | Oracle Reports .rdf |
| L1-07 Reporting | Reporting Snapshot Layer | PKG_REPORTING (stub) | RPT_HEADCOUNT, RPT_COMPENSATION, RPT_TURNOVER, RPT_NEW_HIRES, RPT_LEAVE_UTIL, RPT_PAYROLL_SUMMARY, RPT_EEO_COMPLIANCE (all inferred, never populated) | — | BI Tools (absent) |
| L1-08 Integration | ADP Benefits Feed | PKG_INTEGRATION | EMPLOYEES, EMPLOYEE_DEPENDENTS, BENEFIT_ENROLLMENTS | — | ADP |
| L1-08 Integration | GL Journal | PKG_INTEGRATION | PAYROLL_RUNS, PAYROLL_DETAILS | — | Oracle Financials |
| L1-08 Integration | Time & Attendance | PKG_INTEGRATION (stub) | TIME_ATTENDANCE_RECORDS (DDL absent) | — | External T&A system |
| L1-08 Integration | LDAP/AD | PKG_INTEGRATION (stub) | — | — | LDAP/Active Directory |
| L1-09 Platform | Configuration | — | SYSTEM_PARAMETERS | — | — |
| L1-09 Platform | Logging | PKG_COMMON | AUDIT_LOG | — | — |
| L1-09 Platform | Notification Dispatch | PKG_NOTIFICATION | NOTIFICATION_QUEUE, NOTIFICATION_TEMPLATES | — | Email (UTL_MAIL), SMS (stub) |

### 4.2 Package-to-Capability Coverage Matrix

| Package | Primary L1 Domain | L2 Capabilities Supported | Critical Gaps |
|---------|------------------|---------------------------|---------------|
| PKG_EMPLOYEE | L1-01 | L2-01-01, -02, -03, -04 (partial) | Termination sub-steps |
| PKG_PAYROLL | L1-02 | L2-02-01, -03, -04, -05 | L2-02-06, -07, -08 |
| PKG_LEAVE | L1-03 | L2-03-01, -02 (defect), -03, -04 | L2-03-07 |
| PKG_PERFORMANCE | L1-04 | L2-04-01 through -04, -05 (partial) | L2-04-06 (calibration) |
| PKG_SECURITY | L1-06 | L2-06-02, -03, -04, -06, -08 (partial) | L2-06-01, -05, -09 |
| PKG_INTEGRATION | L1-08 | L2-08-01, -02, -04 (stub), -05 (stub) | L2-08-03, -06, -07 |
| PKG_REPORTING | L1-07 | L2-07-01 through -07 (partial) | L2-07-08, -09 |
| PKG_NOTIFICATION | L1-08 | Notification dispatch | SMS channel stub |
| PKG_COMMON | L1-09 | L2-09-07 (partial) | All other platform ops |

---

## 5. Capability Gaps — Future System Requirements

This section lists capabilities that are required in the target system but either absent or critically deficient in the current Oracle HRMS.

### 5.1 Compliance Gaps (Regulatory / Legal Risk)

| Gap ID | Capability Required | Current State | Regulatory Driver | Severity |
|--------|-------------------|---------------|-------------------|----------|
| GAP-C-01 | COBRA Notification on Termination | Absent — TODO stub | ERISA / ACA; 14-day notification window | Critical |
| GAP-C-02 | NACHA ACH Payroll Disbursement | Absent — bank accounts never read | NACHA Operating Rules | Critical |
| GAP-C-03 | ACH Prenote Verification | Absent — PRENOTE_SENT never set | NACHA Operating Rules | High |
| GAP-C-04 | FMLA Documentation Enforcement | REQUIRES_DOCUMENT='N' in seed | FMLA (29 CFR Part 825) | High |
| GAP-C-05 | EEO Gender Field Constraint | No CHECK constraint | EEO-1 Reporting | High |
| GAP-C-06 | Password Authentication | Any username authenticates | SOC 2 / ISO 27001 | Critical |
| GAP-C-07 | Brute-Force Account Lockout | Absent | SOC 2 CC6.1 | Critical |
| GAP-C-08 | Encryption Key Management | Hard-coded key in source | PCI-DSS / HIPAA if benefits data in scope | Critical |
| GAP-C-09 | Routing Number Encryption | Stored plaintext | NACHA / PCI | High |
| GAP-C-10 | Dependent SSN Decryption Path | Encrypted but no decrypt procedure | HIPAA if benefits data in scope | High |

### 5.2 Operational Gaps (Unimplemented Features)

| Gap ID | Capability Required | Current State | Business Impact | Severity |
|--------|-------------------|---------------|----------------|----------|
| GAP-O-01 | Final Pay Calculation on Termination | Procedure does not exist | Every termination requires fully manual payroll | Critical |
| GAP-O-02 | Leave Balance Payout on Termination | Not in terminate_employee | Payout amount unknown; manual process | High |
| GAP-O-03 | Off-Cycle Payroll Run | Not implemented | Can't process mid-period terminations | High |
| GAP-O-04 | Performance Rating Calibration Workflow | Dead schema columns | HR cannot run calibration; OVERALL_RATING used in reports | High |
| GAP-O-05 | Time & Attendance to Payroll Integration | Stub — no INSERT anywhere | Manual re-keying of hours; error risk | High |
| GAP-O-06 | LDAP / AD Org Structure Sync | Stub | Manual org updates; identity drift | High |
| GAP-O-07 | Denormalised Reporting Layer | refresh_reporting_tables is a stub | All reports load OLTP directly; performance / availability risk | High |
| GAP-O-08 | GL Feed Confirmation Tracking | No status on PAYROLL_RUNS | Missed GL feeds invisible until month-end reconciliation | Medium |
| GAP-O-09 | Open Enrolment Management | Not present | Annual open enrolment is fully manual | High |
| GAP-O-10 | Multi-Year Leave Reporting | CALENDAR_YEAR not projected | Cannot produce year-over-year leave reports | Medium |
| GAP-O-11 | Session Cleanup Background Job | No sweeper job | Stale sessions accumulate; USER_SESSIONS grows unbounded | Medium |
| GAP-O-12 | Salary Band Enforcement (Hard Block) | Warning-only; debug mode | Salaries outside grade band accepted silently | Medium |
| GAP-O-13 | Benefits Enrolment Filter on ADP Feed | BENEFITS_ENROLLED not read | Un-enrolled dependents sent to ADP | Medium |

### 5.3 Architecture Gaps (Target System Design Requirements)

| Gap ID | Capability Required | Rationale |
|--------|-------------------|-----------|
| GAP-A-01 | CI/CD Pipeline (build, test, deploy) | 0 of 14 pipeline capabilities present; builds and deploys are 100% manual |
| GAP-A-02 | Automated Test Suite | Zero tests; no regression safety net for migration |
| GAP-A-03 | Secret / Vault Management | Hard-coded key must be externalised before migration |
| GAP-A-04 | Structured Logging with Correlation IDs | Current free-text AUDIT_LOG unsearchable at scale |
| GAP-A-05 | REST API Layer | No external system integration path without flat file |
| GAP-A-06 | Dedicated Portal Database User | Portal likely has schema-owner access; principle of least privilege violated |
| GAP-A-07 | Fine-Grained RBAC | Grade-based RBAC too coarse for multi-role HR org |
| GAP-A-08 | Oracle MEDIAN() Migration Equivalence | PostgreSQL / SQL Server lack direct equivalent; must be translated |
| GAP-A-09 | Oracle Forms Replacement | Forms 12c is end-of-life trajectory; target system requires web UI |
| GAP-A-10 | Distributed Transaction Handling | Monolithic shared DB; no compensation/saga pattern for multi-step operations |

---

## 6. Investment Priority

Capabilities are ordered by a combination of **compliance risk** (regulatory penalty / legal liability), **operational impact** (number of employees / processes affected per day), and **migration dependency** (whether other capabilities depend on this being built first).

### 6.1 Priority Tiers

| Tier | Label | Criteria |
|------|-------|---------|
| P0 | Block-the-Migration | Must be resolved before the new system can legally or safely go live |
| P1 | Go-Live Critical | Must be ready at go-live for core HR operations |
| P2 | Go-Live Important | Should be ready at go-live; manual workaround is unacceptable long-term |
| P3 | Post-Go-Live | Can be phased in 0–6 months after go-live |
| P4 | Strategic | 6–18 months post-go-live; competitive or analytical differentiators |

### 6.2 Priority Matrix

| Priority | Gap / Capability | Capability IDs | Rationale |
|----------|-----------------|----------------|-----------|
| **P0** | Implement Real Password Authentication | GAP-C-06, L2-06-01 | System allows any username to authenticate; migration cannot go live with this defect |
| **P0** | Externalise Encryption Key (Vault) | GAP-C-08, GAP-A-03 | Hard-coded AES key in source; routing numbers plaintext |
| **P0** | Automated Test Suite (Pre-Migration Baseline) | GAP-A-02, L2-09-03 | Cannot validate migration correctness without tests |
| **P0** | COBRA Notification on Termination | GAP-C-01, L2-05-05 | Federal compliance; every termination is currently a violation |
| **P0** | NACHA ACH Payroll Disbursement | GAP-C-02, GAP-C-03, L2-02-06 | Direct deposit non-functional; manual disbursement is a critical operational risk at any scale |
| **P1** | Final Pay Calculation on Termination | GAP-O-01, L2-02-07 | calculate_final_pay does not exist; every termination requires fully manual payroll |
| **P1** | Account Lockout & Brute-Force Protection | GAP-C-07, L2-06-05 | Zero brute-force protection on any account |
| **P1** | Fix HEAD_OF_HOUSEHOLD Tax Defect | L2-02-04 | $0 federal tax for HOH employees; IRS liability |
| **P1** | FMLA Documentation Enforcement | GAP-C-04, L2-03-05 | FMLA REQUIRES_DOCUMENT='N' creates audit exposure |
| **P1** | Access Revocation on Termination | L2-06-07 | revoke_access procedure absent; active sessions survive termination |
| **P1** | Leave Balance Payout on Termination | GAP-O-02, L2-03-07 | Linked to final pay; must be coordinated |
| **P1** | Salary Band Enforcement (Hard Block) | GAP-O-12, L2-02-02 | Currently a non-blocking warning; grade band violations accepted |
| **P2** | Fix Leave Accrual Overwrite Defect | L2-03-02 | Silent data corruption on accrual retry (BR-LIB-05) |
| **P2** | Performance Calibration Workflow | GAP-O-04, L2-04-06 | Dead CALIBRATED_RATING column; org-wide ratings report reads wrong value |
| **P2** | Off-Cycle Payroll Capability | GAP-O-03, L2-02-08 | Required to process mid-period termination pay |
| **P2** | EEO Gender CHECK Constraint | GAP-C-05, L2-07-07 | Arbitrary GENDER values distort EEO-1 reports |
| **P2** | Portal Dedicated DB User | GAP-A-06, L2-06-09 | Principle of least privilege; portal likely has schema-owner access |
| **P2** | BENEFITS_ENROLLED Filter on ADP Feed | GAP-O-13, L2-05-03 | Un-enrolled dependents exported to ADP |
| **P2** | GL Feed Status Tracking | GAP-O-08, L2-02-09 | Missed GL feeds undetectable |
| **P2** | ACH Routing Number Encryption | GAP-C-09, TD-46 | Full ACH credentials exposed if DB breached |
| **P3** | Time & Attendance to Payroll Integration | GAP-O-05, L2-08-04 | Manual re-keying; import stub does nothing |
| **P3** | LDAP / AD Org Sync | GAP-O-06, L2-08-05 | Manual org maintenance; false-success log from stub |
| **P3** | Open Enrolment Management | GAP-O-09, L2-05-06 | Annual open enrolment is fully manual |
| **P3** | Denormalised Reporting Layer | GAP-O-07, L2-07-08 | RPT_* stub; OLTP load from all reports |
| **P3** | Session Cleanup Background Job | GAP-O-11, L2-06-02 | Stale sessions accumulate unbounded |
| **P3** | Structured Logging & Observability | GAP-A-04, L2-09-07 | AUDIT_LOG free-text unsearchable at scale |
| **P3** | CI/CD Pipeline | GAP-A-01, L2-09-02 through -05 | Manual build, test, deploy; no regression gate |
| **P4** | REST API Surface | GAP-A-05, L2-08-06 | Enables modern integrations beyond flat file |
| **P4** | Fine-Grained RBAC | GAP-A-07, L2-06-03 | Grade-based access too coarse |
| **P4** | Executive Dashboards | L2-07-09 | Strategic analytics layer |
| **P4** | Predictive Workforce Analytics | L2-07-10 | ML/AI capability; post-stabilisation |

### 6.3 Migration Dependency Graph (Key Dependencies)

```
P0: Real Authentication ──────────────────────────────────────────► All other P0/P1 security work
P0: Vault / Secret Management ──────────────► ACH encryption, Routing number encryption
P0: Automated Test Suite ────────────────────► All migration validation
P0: COBRA ─────────────────────────────────────────────────────────► P1: Access Revocation (sequence matters)
P0: NACHA ACH ─────────────────────────────────────────────────────► P1: Final Pay, P2: Off-Cycle Payroll
P1: Final Pay on Termination ──────────────────────────────────────► P1: Leave Payout (same transaction)
P2: Performance Calibration ───────────────────────────────────────► P4: Merit Pay Automation
P3: Reporting Layer ────────────────────────────────────────────────► P4: Dashboards
P3: CI/CD ──────────────────────────────────────────────────────────► P4: All ongoing delivery
```

---

## 7. Capability Maturity Assessment — Current vs. Target

The maturity model uses a 5-point scale based on the Capability Maturity Model Integration (CMMI) framework, adapted for business capability assessment.

| Level | Label | Description |
|-------|-------|-------------|
| 1 | Initial | Ad hoc; undocumented; success depends on individual effort |
| 2 | Managed | Basic process in place; repeatable but inconsistent |
| 3 | Defined | Standardised, documented process; consistent execution |
| 4 | Measured | Quantitative metrics; controlled; predictable outcomes |
| 5 | Optimising | Continuous improvement; automated feedback loops |

### 7.1 Maturity Assessment Table

| L2 ID | Capability | Current Maturity | Target Maturity | Gap | Key Actions to Close Gap |
|-------|-----------|-----------------|----------------|-----|--------------------------|
| L2-01-01 | Employee Record Management | 3 — Defined | 4 — Measured | +1 | Add audit completeness metrics; automated data quality checks |
| L2-01-02 | New Hire Onboarding | 2 — Managed | 4 — Measured | +2 | Add provisioning workflow; checklist; SLA tracking |
| L2-01-03 | Transfer & Promotion | 3 — Defined | 4 — Measured | +1 | Add approval workflow metrics |
| L2-01-04 | Employment Termination | 1 — Initial | 4 — Measured | +3 | Implement COBRA, final pay, access revocation; add SLA metrics |
| L2-01-05 | Org Structure Maintenance | 1 — Initial | 3 — Defined | +2 | Implement LDAP sync; replace stub |
| L2-01-06 | Position & Grade Management | 2 — Managed | 3 — Defined | +1 | Make salary band enforcement a hard block |
| L2-01-07 | Headcount Reporting | 3 — Defined | 4 — Measured | +1 | Populate RPT_HEADCOUNT; add refresh schedule |
| L2-01-08 | Workforce Compliance | 1 — Initial | 4 — Measured | +3 | Implement FMLA enforcement; EEO tracking; audit dashboard |
| L2-02-01 | Salary Administration | 3 — Defined | 4 — Measured | +1 | Add grade band violation alerting |
| L2-02-02 | Grade Band Enforcement | 2 — Managed | 4 — Measured | +2 | Harden to blocking error; add exception approval workflow |
| L2-02-03 | Payroll Run Execution | 3 — Defined | 4 — Measured | +1 | Add reconciliation checks; SLA metrics |
| L2-02-04 | Tax Calculation | 2 — Managed | 4 — Measured | +2 | Fix HOH defect; add multi-state; quarterly reconciliation |
| L2-02-05 | Deduction Processing | 3 — Defined | 4 — Measured | +1 | Add deduction audit report |
| L2-02-06 | ACH Disbursement | 1 — Initial | 4 — Measured | +3 | Implement full NACHA pipeline; prenote; confirmation |
| L2-02-07 | Final Pay on Termination | 1 — Initial | 4 — Measured | +3 | Build calculate_final_pay; PTO payout; off-cycle integration |
| L2-02-08 | Off-Cycle Payroll | 1 — Initial | 3 — Defined | +2 | Implement off-cycle run capability |
| L2-02-09 | Payroll GL Feed | 2 — Managed | 4 — Measured | +2 | Add GL_FEED_STATUS; reconciliation report |
| L2-02-10 | Merit Pay | 2 — Managed | 4 — Measured | +2 | Use CALIBRATED_RATING; automate merit calculation |
| L2-03-01 | Leave Balance Initialisation | 3 — Defined | 3 — Defined | 0 | Maintain |
| L2-03-02 | Leave Accrual | 2 — Managed | 4 — Measured | +2 | Fix overwrite defect; add monthly reconciliation check |
| L2-03-03 | Leave Request Submission | 3 — Defined | 4 — Measured | +1 | Add SLA; conflict detection |
| L2-03-04 | Leave Approval | 3 — Defined | 4 — Measured | +1 | Add escalation; SLA metrics |
| L2-03-05 | FMLA Enforcement | 1 — Initial | 4 — Measured | +3 | Fix seed data; enforce documentation; audit trail |
| L2-03-06 | Leave Balance Reporting | 2 — Managed | 4 — Measured | +2 | Fix CALENDAR_YEAR projection; multi-year support |
| L2-03-07 | Leave Payout on Termination | 1 — Initial | 3 — Defined | +2 | Integrate with terminate_employee; calculate payout |
| L2-04-01 | Review Cycle Management | 3 — Defined | 4 — Measured | +1 | Add completion rate metrics |
| L2-04-02 | Self-Assessment | 3 — Defined | 3 — Defined | 0 | Maintain |
| L2-04-03 | Manager Review | 3 — Defined | 4 — Measured | +1 | Add rating quality checks |
| L2-04-04 | Acknowledgement | 3 — Defined | 3 — Defined | 0 | Maintain |
| L2-04-05 | Goal Setting & Tracking | 2 — Managed | 4 — Measured | +2 | Complete goal-to-outcome linkage; add progress tracking |
| L2-04-06 | Rating Calibration | 1 — Initial | 4 — Measured | +3 | Implement calibration workflow; status transition; reporting fix |
| L2-04-07 | Rating Distribution | 2 — Managed | 4 — Measured | +2 | Read CALIBRATED_RATING; add normalisation checks |
| L2-04-08 | Performance-to-Compensation Linkage | 2 — Managed | 4 — Measured | +2 | Automate merit calculation from calibrated rating |
| L2-05-01 | Benefit Plan Management | 3 — Defined | 3 — Defined | 0 | Maintain |
| L2-05-02 | Benefit Enrolment | 3 — Defined | 4 — Measured | +1 | Add eligibility validation; effective date enforcement |
| L2-05-03 | Dependent Management | 2 — Managed | 4 — Measured | +2 | Add BENEFITS_ENROLLED filter; implement SSN decrypt for dependents |
| L2-05-04 | ADP Benefits Feed | 2 — Managed | 4 — Measured | +2 | Add trailer record; format version; BENEFITS_ENROLLED filter |
| L2-05-05 | COBRA Administration | 1 — Initial | 4 — Measured | +3 | Implement full COBRA workflow; notification tracking; deadline monitoring |
| L2-05-06 | Open Enrolment | 1 — Initial | 3 — Defined | +2 | Design and build enrolment window management |
| L2-05-07 | Benefits Eligibility Rules | 2 — Managed | 4 — Measured | +2 | Add age/status-based eligibility engine |
| L2-06-01 | User Authentication | 1 — Initial | 5 — Optimising | +4 | Implement real credential verification; MFA; adaptive auth |
| L2-06-02 | Session Management | 2 — Managed | 4 — Measured | +2 | Add background sweep; session metrics; forced logout on termination |
| L2-06-03 | RBAC | 2 — Managed | 4 — Measured | +2 | Fine-grained permissions; role management UI |
| L2-06-04 | Password Management | 2 — Managed | 4 — Measured | +2 | Fix old-password check; upgrade from MD5 to bcrypt/Argon2 |
| L2-06-05 | Account Lockout | 1 — Initial | 4 — Measured | +3 | Implement attempt counter; lockout; unlock workflow |
| L2-06-06 | Encryption at Rest | 2 — Managed | 4 — Measured | +2 | Externalise key; encrypt routing numbers |
| L2-06-07 | Access Revocation | 2 — Managed | 4 — Measured | +2 | Implement revoke_access; immediate session invalidation |
| L2-06-08 | Audit Logging | 2 — Managed | 4 — Measured | +2 | Structured logs; correlation IDs; separate tables by type |
| L2-06-09 | Privileged Access Management | 1 — Initial | 4 — Measured | +3 | Create HRMS_PORTAL_APP user; least-privilege grants; PAM tooling |
| L2-07-01 | Headcount Reporting | 3 — Defined | 4 — Measured | +1 | Move to RPT_HEADCOUNT; add as-of-date flexibility |
| L2-07-02 | Compensation Analytics | 3 — Defined | 4 — Measured | +1 | Migrate Oracle MEDIAN() to target DB equivalent |
| L2-07-03 | Turnover Reporting | 2 — Managed | 4 — Measured | +2 | Fix denominator to SHRM standard; add trend period comparison |
| L2-07-04 | New Hire Reporting | 3 — Defined | 4 — Measured | +1 | Add RPT_NEW_HIRES population |
| L2-07-05 | Leave Utilisation | 2 — Managed | 4 — Measured | +2 | Fix CALENDAR_YEAR projection; multi-year support |
| L2-07-06 | Payroll Summary | 2 — Managed | 4 — Measured | +2 | Replace magic element IDs with named constants; add ERROR row handling |
| L2-07-07 | EEO Compliance | 2 — Managed | 4 — Measured | +2 | Add GENDER constraint; align with current EEO-1 categories |
| L2-07-08 | Reporting Layer | 1 — Initial | 4 — Measured | +3 | Implement RPT_* population; schedule nightly refresh; monitor staleness |
| L2-07-09 | Executive Dashboards | 1 — Initial | 4 — Measured | +3 | Build dashboard layer on RPT_* foundation |
| L2-07-10 | Predictive Analytics | 1 — Initial | 3 — Defined | +2 | Phase in after stable data foundation |
| L2-08-01 | ADP Benefits Feed | 2 — Managed | 4 — Measured | +2 | See L2-05-04 |
| L2-08-02 | Oracle Financials GL Feed | 2 — Managed | 4 — Measured | +2 | Add status tracking; reconciliation; missed-feed alerting |
| L2-08-03 | NACHA ACH Disbursement | 1 — Initial | 4 — Measured | +3 | Full NACHA pipeline; prenote; bank verification; confirmation |
| L2-08-04 | T&A Import | 1 — Initial | 3 — Defined | +2 | Implement CSV import to TIME_ATTENDANCE_RECORDS; link to payroll |
| L2-08-05 | LDAP/AD Sync | 1 — Initial | 3 — Defined | +2 | Implement sync procedure; replace false-success stub |
| L2-08-06 | API Surface | 1 — Initial | 3 — Defined | +2 | Design REST API layer for key entities |
| L2-08-07 | Inbound Data Validation | 1 — Initial | 3 — Defined | +2 | Add file format version; record count validation; checksum |
| L2-08-08 | Integration Error Handling | 2 — Managed | 4 — Measured | +2 | Implement retry queue; dead-letter; alerting |
| L2-09-01 | Configuration Management | 2 — Managed | 4 — Measured | +2 | Ensure all parameters are runtime-honoured; add parameter audit |
| L2-09-02 | Automated Build | 1 — Initial | 4 — Measured | +3 | Script Forms compilation; PL/SQL deployment; version tagging |
| L2-09-03 | Automated Testing | 1 — Initial | 4 — Measured | +3 | Build full test suite before migration begins |
| L2-09-04 | Continuous Integration | 1 — Initial | 4 — Measured | +3 | CI pipeline with test, SAST, secret scanning gates |
| L2-09-05 | Automated Deployment | 1 — Initial | 4 — Measured | +3 | Scripted deployments; zero-downtime strategy |
| L2-09-06 | Secret / Credential Management | 1 — Initial | 5 — Optimising | +4 | Vault integration; rotation; audit |
| L2-09-07 | Structured Observability | 1 — Initial | 4 — Measured | +3 | Structured logs; correlation IDs; APM; dashboards |
| L2-09-08 | Alerting & Incident Response | 1 — Initial | 4 — Measured | +3 | Alerting on error rates; SLA breaches; payroll failures |
| L2-09-09 | DB Backup & Recovery | Unknown | 4 — Measured | TBD | Confirm DBA backup policy; RTO/RPO targets |
| L2-09-10 | Rollback / DR | 1 — Initial | 4 — Measured | +3 | Application-level rollback; blue-green or canary strategy |

### 7.2 Maturity Summary by Domain

| L1 Domain | Avg Current Maturity | Avg Target Maturity | Avg Gap | Maturity Risk |
|-----------|---------------------|--------------------|---------|----|
| L1-01 Workforce Management | 1.9 | 3.6 | +1.7 | High |
| L1-02 Compensation & Payroll | 2.0 | 3.8 | +1.8 | Critical |
| L1-03 Leave & Absence | 2.3 | 3.7 | +1.4 | High |
| L1-04 Performance Management | 2.4 | 3.8 | +1.4 | High |
| L1-05 Benefits Administration | 1.8 | 3.6 | +1.8 | Critical |
| L1-06 Security & Identity | 1.7 | 4.1 | +2.4 | Critical |
| L1-07 Organisational Intelligence | 2.2 | 3.9 | +1.7 | High |
| L1-08 System Integration | 1.5 | 3.4 | +1.9 | High |
| L1-09 Platform Operations | 1.2 | 4.0 | +2.8 | Critical |

**Overall HRMS Maturity: Current 1.9 / Target 3.8 — gap of +1.9 levels across all capabilities.**

---

## 8. Appendix — Evidence Trail

### 8.1 Key Source Artefacts Referenced

| Artefact | Relevance to Capability Model |
|----------|-------------------------------|
| `plsql/packages/PKG_EMPLOYEE.pkb` | L1-01: hire, transfer, promote, terminate |
| `plsql/packages/PKG_PAYROLL.pkb` | L1-02: payroll run, tax, deduction logic |
| `plsql/packages/PKG_LEAVE.pkb` | L1-03: accrual, request, approval |
| `plsql/packages/PKG_PERFORMANCE.pkb` | L1-04: review lifecycle; calibration gap evidence |
| `plsql/packages/PKG_SECURITY.pkb` | L1-06: auth stub (BR-042), session, RBAC, encryption |
| `plsql/packages/PKG_INTEGRATION.pkb` | L1-08: ADP feed, GL journal, all stubs |
| `plsql/packages/PKG_REPORTING.pkb` | L1-07: all report procedures; RPT_* stub |
| `plsql/packages/PKG_NOTIFICATION.pkb` | L1-08: notification dispatch |
| `schema/tables/01_core_tables.sql` | EMPLOYEES, DEPARTMENTS, EMPLOYEE_DEPENDENTS DDL |
| `schema/tables/02_payroll_tables.sql` | EMPLOYEE_BANK_ACCOUNTS, PAYROLL_RUNS DDL |
| `forms/xml-exports/HRMS_EMPLOYEE.xml` | LOV_MANAGERS gap (TD-72); Forms layer capability coverage |
| `forms/xml-exports/HRMS_LOGIN.xml` | Authentication UI; error handler gap (TD-53) |
| `reference-data/01_reference_data.sql` | FMLA REQUIRES_DOCUMENT='N' (TD-71) |
| `BA_Deep_Analyst.md` (merged) | BR-01 through BR-140; all pain points; gap evidence |
| `BA_Deep_Analyst_Edge.md` | Cross-validation supplements: EMPLOYEE_DEPENDENTS, EMPLOYEE_BANK_ACCOUNTS, PKG_INTEGRATION stubs, PKG_LEAVE.initialize_balances |
| `DA_Data_Reviewer.md` (merged) | DQ-001 through DQ-032; PII inventory; schema catalogue |
| `TA_Deep_Analyst.md` | TD-01 through TD-81; CI/CD assessment; observability gap |
| `AA_Quality_Review.md` (merged) | QR-001 through QR-033; architecture violations AV-001 through AV-025 |

### 8.2 Business Rule to Capability Cross-Reference

| Business Rule | Affected Capability | Severity |
|--------------|---------------------|----------|
| BR-042 (auth never verifies password) | L2-06-01 | Critical |
| BR-044 (change_password skips old-password check) | L2-06-04 | High |
| BR-TERM-01 (COBRA TODO stub) | L2-05-05 | Critical |
| BR-TERM-07 (calculate_final_pay nonexistent) | L2-02-07 | Critical |
| BR-BA-12 (EMPLOYEE_BANK_ACCOUNTS never read) | L2-02-06 | Critical |
| BR-ORG-02 (sync_org_structure logs false success) | L2-01-05, L2-08-05 | High |
| BR-LIB-05 (accrual overwrite defect) | L2-03-02 | High |
| DQ-001 (hard-coded AES key) | L2-06-06, L2-09-06 | Critical |
| DQ-029 (old password not verified) | L2-06-04 | High |
| DQ-031 (import_time_attendance logs false success) | L2-08-04 | High |
| TD-71 (FMLA REQUIRES_DOCUMENT='N') | L2-03-05 | High |
| TD-74 (salary validation soft warning) | L2-02-02 | Medium |
| TD-81 (portal schema-owner access) | L2-06-09 | High |

---

*Document ends. All capability assessments are evidence-based and derived from multi-pass static analysis of the Acme HRMS Oracle codebase. Line counts and severities are drawn directly from the BA, DA, TA, and AA analysis tracks cited above.*
