# 02 — Business Capability Model
**System:** Acme Corporation HRMS (Oracle 19c — Legacy)
**Author:** Business Architecture Track
**Source basis:** BA_Deep_Analyst.md (BR-01–BR-140), BA_Deep_Analyst_Edge.md (cross-validation supplements), DA_Data_Reviewer.md, TA_Deep_Analyst outputs, AA_Quality_Review outputs, 05_DOMAIN_MODEL, 06_DATA_DICTIONARY
**Date:** 2026-08-05

---

## 1. Business Capability Map

A business capability describes **what** the organisation does, independent of how or who does it. The map below is derived entirely from evidence found in the Oracle HRMS source — tables, packages, business rules, and cross-validation findings — organised into two levels.

### L1 / L2 Capability Table

| L1 Capability | L2 Capability | Description |
|---|---|---|
| **1. Workforce Management** | 1.1 Employee Onboarding | Hire employee, assign ID, set grade, create initial salary record |
| | 1.2 Employee Offboarding / Termination | Process voluntary/involuntary termination, update status, inactivate sessions |
| | 1.3 Employee Data Maintenance | Update personal data, contact info, marital status, emergency contacts |
| | 1.4 Organisational Assignment | Assign/transfer employee to department, position, and manager |
| | 1.5 Employee History & Audit Trail | Maintain change history (EMPLOYEE_HISTORY), audit timestamps |
| | 1.6 Dependent Management | Record employee dependents, relationship, DOB, benefits enrollment flag |
| **2. Compensation & Payroll** | 2.1 Salary Administration | Set, change, and version salary records; grade-band validation |
| | 2.2 Payroll Run Processing | Create run, calculate gross/net per employee, apply deductions |
| | 2.3 Tax Calculation | Federal and state income tax computation from filing status and rate tables |
| | 2.4 Deduction Management | Pre-tax and post-tax deductions (health, dental, 401k, etc.) |
| | 2.5 Final Pay Calculation | Prorated wages and PTO payout on termination |
| | 2.6 Direct Deposit Disbursement | Disburse net pay to employee bank accounts via ACH/NACHA |
| | 2.7 Payroll GL Export | Generate pipe-delimited GL journal feed to Oracle Financials |
| **3. Leave Management** | 3.1 Leave Type Administration | Define leave types, accrual rules, carry-over limits |
| | 3.2 Leave Balance Initialisation | Create opening balances on hire; annual rollover |
| | 3.3 Leave Accrual | Monthly accrual of entitled leave days |
| | 3.4 Leave Request & Approval | Submit, approve, reject, or cancel leave requests |
| | 3.5 FMLA Administration | Track federally-protected FMLA leave, enforce 12-week entitlement |
| | 3.6 Leave Balance Reporting | Report available, used, and pending leave per employee |
| **4. Performance Management** | 4.1 Review Cycle Administration | Create and manage annual/mid-year review cycles |
| | 4.2 Goal Setting & Tracking | Define employee goals, link to review cycle |
| | 4.3 Self-Assessment | Employee submits self-evaluation and rating |
| | 4.4 Manager Review & Rating | Manager submits overall rating and narrative |
| | 4.5 Rating Calibration | Cross-team calibration of ratings for fairness |
| | 4.6 Performance Reporting | Rating distribution, headcount by rating band |
| | 4.7 Merit Eligibility Gate | Determine compensation eligibility from performance rating |
| **5. Benefits Administration** | 5.1 Benefit Plan Catalogue | Maintain plan types, tiers, and eligibility rules |
| | 5.2 Benefits Enrolment | Enrol or change employee benefit elections |
| | 5.3 Dependent Benefits Eligibility | Link dependents to benefit plans, validate enrollment status |
| | 5.4 COBRA Administration | Notify and track COBRA continuation rights on qualifying events |
| | 5.5 Benefits Feed Export | Generate ADP fixed-width benefits file for third-party carrier |
| **6. Organisational Structure** | 6.1 Department Management | Create/maintain departments, hierarchy, cost-centres |
| | 6.2 Job Position Catalogue | Maintain job titles, grade ranges, EEO categories |
| | 6.3 Org Hierarchy Reporting | CONNECT BY hierarchy traversal; reporting lines |
| | 6.4 LDAP / AD Org Sync | Synchronise org structure changes to directory services |
| **7. Security & Access Control** | 7.1 Authentication | Login with email/password; session creation and validation |
| | 7.2 Authorisation / RBAC | Grade-based role enforcement across all packages |
| | 7.3 Credential Management | Password creation, complexity enforcement, password change |
| | 7.4 Session Lifecycle Management | 30-minute idle timeout; session invalidation on termination |
| | 7.5 Data Encryption Services | AES-256 encryption/decryption of SSN, bank account data |
| | 7.6 Audit Logging | Log all DML, errors, and security events to AUDIT_LOG |
| **8. Reporting & Analytics** | 8.1 Headcount Reporting | Active headcount by department, type, and as-of date |
| | 8.2 Compensation Analytics | Salary summary, compa-ratio, median pay by grade |
| | 8.3 Turnover Reporting | Hire/termination counts and turnover percentage |
| | 8.4 New Hire Reporting | Row-level new hire details with salary and location |
| | 8.5 Leave Utilisation Reporting | Leave usage percentages by type and department |
| | 8.6 Payroll Summary Reporting | Payroll run totals by element and department |
| | 8.7 EEO Compliance Reporting | Gender and EEO category distribution by job classification |
| **9. Integration & Interoperability** | 9.1 Benefits Feed (ADP) | Fixed-width employee + dependent export to ADP |
| | 9.2 Payroll GL Feed (Oracle Financials) | Pipe-delimited journal entry file for Oracle GL import |
| | 9.3 Time & Attendance Import | CSV-based import of time records into payroll staging |
| | 9.4 Org Structure Sync (LDAP/AD) | Push org hierarchy changes to directory services |
| | 9.5 Reporting Table Refresh | Nightly truncate-and-repopulate of RPT_* snapshot tables |
| **10. Notifications** | 10.1 Notification Queue Management | Enqueue and dispatch notifications via multiple channels |
| | 10.2 Template Management | Maintain parameterised notification templates |
| | 10.3 Payslip Distribution | Email payslip PDF or link to employee on payroll completion |
| | 10.4 Leave Decision Notification | Notify employee of leave approval/rejection |

---

## 2. Capability Heat Map

**Risk rating key:**

| Rating | Meaning |
|---|---|
| CRITICAL | Capability is broken, unimplemented, or creates legal/compliance exposure — must fix before go-live |
| HIGH | Significant defect, security hole, or data quality gap — high migration risk |
| MEDIUM | Partial implementation or quality issue — needs design attention |
| OK | Implemented and adequate for current needs |
| NOT IMPLEMENTED | Capability is designed (tables/columns exist) but contains zero functional code |

| L1 | L2 Capability | Heat | Primary Evidence |
|---|---|---|---|
| 1. Workforce Mgmt | 1.1 Employee Onboarding | OK | PKG_EMPLOYEE.create_employee functional |
| | 1.2 Employee Offboarding | HIGH | COBRA absent (PP-TERM-01); calculate_final_pay non-existent (PP-TERM-03); sessions not revoked (BR-TERM); dependents not inactivated (BR-DEP-09) |
| | 1.3 Employee Data Maintenance | OK | PKG_EMPLOYEE update paths present |
| | 1.4 Organisational Assignment | OK | Transfer procedure present |
| | 1.5 Employee History & Audit Trail | MEDIUM | Trigger-driven, but no structured log format; AUDIT_LOG mixes types (TD-37) |
| | 1.6 Dependent Management | HIGH | BENEFITS_ENROLLED never read (BR-DEP-05); SSN decrypt path missing for dependents (BR-DEP-06); termination does not inactivate dependents (BR-DEP-09) |
| 2. Compensation | 2.1 Salary Administration | MEDIUM | Grade-band validation is soft warning only (TD-74); salary range logic debug-mode only |
| | 2.2 Payroll Run Processing | MEDIUM | Core run functional; PAID status orphaned (DISC-009) when bank accounts unused |
| | 2.3 Tax Calculation | HIGH | HEAD_OF_HOUSEHOLD branch returns $0 federal tax (defect in BA rules); state tax is flat-rate only |
| | 2.4 Deduction Management | MEDIUM | Pre/post-tax deductions implemented; no cross-check of deduction totals vs. gross |
| | 2.5 Final Pay Calculation | CRITICAL | `PKG_PAYROLL.calculate_final_pay` does not exist (PP-TERM-03); all termination pay is manual |
| | 2.6 Direct Deposit Disbursement | CRITICAL | EMPLOYEE_BANK_ACCOUNTS table never read during payroll (BR-BA-12 / PP-BA-01); no ACH/NACHA file generated |
| | 2.7 Payroll GL Export | HIGH | GL feed generated but no GL_FEED_SENT status tracked (TD-80); Journal Source/Category undocumented (TD-79) |
| 3. Leave Mgmt | 3.1 Leave Type Administration | OK | LEAVE_TYPES table and seed data present |
| | 3.2 Leave Balance Initialisation | MEDIUM | initialize_balances functional; accrual retry block has assignment bug (BR-LIB-05) |
| | 3.3 Leave Accrual | HIGH | Retry path uses `SET ACCRUED = v_accrued` instead of increment (BR-LIB-05) — data-destructive under concurrency |
| | 3.4 Leave Request & Approval | OK | PKG_LEAVE submit/approve/reject implemented |
| | 3.5 FMLA Administration | MEDIUM | FMLA leave type exists; REQUIRES_DOCUMENT='N' in seed data (TD-71); no document enforcement |
| | 3.6 Leave Balance Reporting | OK | leave_utilization_report present |
| 4. Performance Mgmt | 4.1 Review Cycle Administration | OK | PKG_PERFORMANCE.create_review functional |
| | 4.2 Goal Setting & Tracking | OK | PERFORMANCE_GOALS table; goal_reviews linkage present |
| | 4.3 Self-Assessment | OK | submit_self_assessment present |
| | 4.4 Manager Review & Rating | OK | submit_manager_review with 1–5 rating enforced |
| | 4.5 Rating Calibration | CRITICAL | CALIBRATED_RATING column exists but no procedure writes to it; no calibration status; get_rating_distribution reads pre-calibration OVERALL_RATING (dead column / wrong reporting) |
| | 4.6 Performance Reporting | HIGH | get_rating_distribution reads OVERALL_RATING not CALIBRATED_RATING — reports uncalibrated figures |
| | 4.7 Merit Eligibility Gate | MEDIUM | Rating ≥ 3 conformist link to compensation exists but is not formally enforced in a single authoritative rule |
| 5. Benefits Admin | 5.1 Benefit Plan Catalogue | OK | BENEFIT_PLANS table and data present |
| | 5.2 Benefits Enrolment | OK | BENEFIT_ENROLLMENTS table; PKG_INTEGRATION exports data |
| | 5.3 Dependent Benefits Eligibility | HIGH | BENEFITS_ENROLLED flag collected but never enforced (BR-DEP-05); all active dependents sent to ADP regardless of enrollment |
| | 5.4 COBRA Administration | CRITICAL | Zero code — no notification, no 14-day timer, no qualifying event record; federal compliance gap on every termination (PP-TERM-01) |
| | 5.5 Benefits Feed Export | MEDIUM | ADP feed functional but no format version header, no record count trailer, no checksum (TD-73) |
| 6. Org Structure | 6.1 Department Management | OK | PKG_EMPLOYEE handles department CRUD |
| | 6.2 Job Position Catalogue | OK | JOB_POSITIONS table and seed data present |
| | 6.3 Org Hierarchy Reporting | MEDIUM | CONNECT BY in use; performance degrades >500 employees |
| | 6.4 LDAP / AD Org Sync | CRITICAL | `sync_org_structure` is a placeholder — zero DML, logs false success on every call (BR-ORG-01/02) |
| 7. Security & Access | 7.1 Authentication | CRITICAL | `authenticate()` never verifies password — any username authenticates regardless of credential (BR-042) |
| | 7.2 Authorisation / RBAC | MEDIUM | Grade-based RBAC present but LOV_MANAGERS has no grade filter (TD-72); Intern can be assigned as VP manager |
| | 7.3 Credential Management | HIGH | `change_password` never verifies old password (DQ-029/BR-044); direct INSERT bypasses complexity rules (BR-041) |
| | 7.4 Session Lifecycle Management | HIGH | No background sweep; sessions orphaned after window close (TD-75); e_session_expired never raised (BR-045) |
| | 7.5 Data Encryption Services | HIGH | AES-256 key hard-coded in source (TD-01/DQ-001); MD5 used for passwords (DQ-010); routing number plaintext (TD-46); bank account decrypt path missing |
| | 7.6 Audit Logging | MEDIUM | AUDIT_LOG operational but mixes all log types; no structured JSON format; no correlation IDs |
| 8. Reporting | 8.1 Headcount Reporting | OK | headcount_report functional and direct-to-OLTP |
| | 8.2 Compensation Analytics | OK | compensation_summary with MEDIAN(); Oracle-specific syntax |
| | 8.3 Turnover Reporting | MEDIUM | Non-standard denominator (hires-to-date not avg headcount) — figures non-comparable with SHRM standard (BR-044) |
| | 8.4 New Hire Reporting | OK | new_hires_report functional |
| | 8.5 Leave Utilisation Reporting | MEDIUM | CALENDAR_YEAR not projected in cursor — RPT_LEAVE_UTIL cannot support multi-year snapshots (DQ-032) |
| | 8.6 Payroll Summary Reporting | MEDIUM | Magic element IDs 100/101/102/103 hard-coded; no tolerance for element catalogue changes |
| | 8.7 EEO Compliance Reporting | OK | eeo_compliance_report present; gender null shown as NOT_DISCLOSED |
| 9. Integration | 9.1 Benefits Feed (ADP) | MEDIUM | Functional but lacks validation, version header, and trailer (TD-73); BENEFITS_ENROLLED ignored |
| | 9.2 Payroll GL Feed | HIGH | Generated but no acknowledged receipt tracking; Journal Source/Category undocumented (TD-79/TD-80) |
| | 9.3 Time & Attendance Import | CRITICAL | `import_time_attendance` is a stub — reads file, loops rows, performs zero DML, logs false success (DQ-031/BR-046) |
| | 9.4 Org Structure Sync | CRITICAL | `sync_org_structure` placeholder — same as 6.4 above (BR-ORG-01/02) |
| | 9.5 Reporting Table Refresh | CRITICAL | `refresh_reporting_tables` is a stub — zero DML, logs false success (BR-043/DQ-031) |
| 10. Notifications | 10.1 Queue Management | MEDIUM | NOTIFICATION_QUEUE and PKG_NOTIFICATION exist; retry logic present |
| | 10.2 Template Management | OK | NOTIFICATION_TEMPLATES table with parameterised payloads |
| | 10.3 Payslip Distribution | MEDIUM | SMS channel referenced but handler not implemented; email path present |
| | 10.4 Leave Decision Notification | OK | Approval/rejection notifications enqueued |

**Heat Summary:**

| Rating | Count | Capabilities |
|---|---|---|
| CRITICAL | 8 | 2.5, 2.6, 4.5, 5.4, 6.4, 7.1, 9.3, 9.4/9.5 |
| HIGH | 12 | 1.2, 1.6, 2.3, 2.7, 3.3, 4.6, 5.3, 7.3, 7.4, 7.5, 9.2, (+ 6.4 variant) |
| MEDIUM | 13 | 1.5, 2.1, 2.2, 2.4, 3.2, 3.5, 4.7, 5.5, 6.3, 7.2, 7.6, 8.3, 8.5, 8.6, 9.1, 10.1, 10.3 |
| OK | 17 | Remaining |

---

## 3. Capability-to-System Mapping

This table maps each L2 capability to the Oracle HRMS package(s), schema tables, and Oracle Forms screens that implement it in the current system.

| L2 Capability | Oracle Package(s) | Key Tables | Forms Screen |
|---|---|---|---|
| 1.1 Employee Onboarding | PKG_EMPLOYEE.create_employee | EMPLOYEES, JOB_POSITIONS, SALARY_RECORDS | HRMS_EMPLOYEE |
| 1.2 Employee Offboarding | PKG_EMPLOYEE.terminate_employee | EMPLOYEES, EMPLOYEE_HISTORY, USER_SESSIONS | HRMS_EMPLOYEE |
| 1.3 Employee Data Maintenance | PKG_EMPLOYEE.update_employee | EMPLOYEES | HRMS_EMPLOYEE |
| 1.4 Organisational Assignment | PKG_EMPLOYEE.transfer_employee | EMPLOYEES, DEPARTMENTS | HRMS_EMPLOYEE |
| 1.5 Employee History & Audit Trail | TRG_EMPLOYEE_AUDIT (trigger) | EMPLOYEE_HISTORY, AUDIT_LOG | — |
| 1.6 Dependent Management | PKG_INTEGRATION.export_benefits_feed | EMPLOYEE_DEPENDENTS | HRMS_EMPLOYEE (assumed) |
| 2.1 Salary Administration | PKG_EMPLOYEE, PKG_COMPENSATION | SALARY_RECORDS, JOB_GRADES | HRMS_EMPLOYEE |
| 2.2 Payroll Run Processing | PKG_PAYROLL.create_payroll_run, calculate_payroll, approve_payroll | PAYROLL_RUNS, PAYROLL_DETAILS | HRMS_PAYROLL |
| 2.3 Tax Calculation | PKG_PAYROLL (inline logic) | PAYROLL_DETAILS, TAX_BRACKETS | — |
| 2.4 Deduction Management | PKG_PAYROLL | DEDUCTION_RECORDS, PAY_ELEMENTS | HRMS_PAYROLL |
| 2.5 Final Pay Calculation | **None — does not exist** | — | — |
| 2.6 Direct Deposit Disbursement | **None — does not exist** | EMPLOYEE_BANK_ACCOUNTS (unused) | — |
| 2.7 Payroll GL Export | PKG_INTEGRATION.generate_gl_journal | PAYROLL_RUNS, PAYROLL_DETAILS, DEPARTMENTS | — |
| 3.1 Leave Type Administration | — (data only) | LEAVE_TYPES | HRMS_LEAVE (assumed) |
| 3.2 Leave Balance Initialisation | PKG_LEAVE.initialize_balances | LEAVE_BALANCES | — |
| 3.3 Leave Accrual | PKG_LEAVE.run_monthly_accrual | LEAVE_BALANCES | — |
| 3.4 Leave Request & Approval | PKG_LEAVE.submit_leave_request, approve_leave_request | LEAVE_REQUESTS, LEAVE_BALANCES | HRMS_LEAVE |
| 3.5 FMLA Administration | PKG_LEAVE (partial) | LEAVE_TYPES, LEAVE_REQUESTS | HRMS_LEAVE |
| 3.6 Leave Balance Reporting | PKG_REPORTING.leave_utilization_report | LEAVE_BALANCES, LEAVE_TYPES | HRMS_REPORTS |
| 4.1 Review Cycle Administration | PKG_PERFORMANCE.create_review | REVIEW_CYCLES, PERFORMANCE_REVIEWS | HRMS_PERFORMANCE |
| 4.2 Goal Setting & Tracking | PKG_PERFORMANCE (goal procedures) | PERFORMANCE_GOALS, GOAL_REVIEWS | HRMS_PERFORMANCE |
| 4.3 Self-Assessment | PKG_PERFORMANCE.submit_self_assessment | PERFORMANCE_REVIEWS | HRMS_PERFORMANCE |
| 4.4 Manager Review & Rating | PKG_PERFORMANCE.submit_manager_review | PERFORMANCE_REVIEWS | HRMS_PERFORMANCE |
| 4.5 Rating Calibration | **None — dead column** | PERFORMANCE_REVIEWS.CALIBRATED_RATING (unused) | — |
| 4.6 Performance Reporting | PKG_REPORTING.get_rating_distribution | PERFORMANCE_REVIEWS | HRMS_REPORTS |
| 4.7 Merit Eligibility Gate | PKG_PERFORMANCE → PKG_PAYROLL (conformist link) | PERFORMANCE_REVIEWS | — |
| 5.1 Benefit Plan Catalogue | — (data only) | BENEFIT_PLANS | — |
| 5.2 Benefits Enrolment | — (data only) | BENEFIT_ENROLLMENTS | — |
| 5.3 Dependent Benefits Eligibility | PKG_INTEGRATION.export_benefits_feed (partial) | EMPLOYEE_DEPENDENTS, BENEFIT_ENROLLMENTS | — |
| 5.4 COBRA Administration | **None — zero code** | — | — |
| 5.5 Benefits Feed Export | PKG_INTEGRATION.export_benefits_feed | EMPLOYEES, EMPLOYEE_DEPENDENTS, BENEFIT_ENROLLMENTS | — |
| 6.1 Department Management | PKG_EMPLOYEE | DEPARTMENTS | HRMS_EMPLOYEE |
| 6.2 Job Position Catalogue | — (data only) | JOB_POSITIONS, JOB_GRADES, JOB_TITLES | — |
| 6.3 Org Hierarchy Reporting | PKG_EMPLOYEE (CONNECT BY query) | DEPARTMENTS, EMPLOYEES | — |
| 6.4 LDAP / AD Org Sync | PKG_INTEGRATION.sync_org_structure | **None — stub only** | — |
| 7.1 Authentication | PKG_SECURITY.authenticate | EMPLOYEES, USER_SESSIONS | HRMS_LOGIN |
| 7.2 Authorisation / RBAC | PKG_SECURITY.has_permission | EMPLOYEES (GRADE column), SYSTEM_PARAMETERS | — |
| 7.3 Credential Management | PKG_SECURITY.change_password | USER_CREDENTIALS | — |
| 7.4 Session Lifecycle Management | PKG_SECURITY.is_session_valid, logout | USER_SESSIONS | — |
| 7.5 Data Encryption Services | PKG_SECURITY.encrypt_value, decrypt_value | — (utility) | — |
| 7.6 Audit Logging | PKG_COMMON.log_error, log_info, log_action | AUDIT_LOG | — |
| 8.1 Headcount Reporting | PKG_REPORTING.headcount_report | EMPLOYEES, DEPARTMENTS, LOCATIONS | HRMS_REPORTS |
| 8.2 Compensation Analytics | PKG_REPORTING.compensation_summary | SALARY_RECORDS, JOB_GRADES | HRMS_REPORTS |
| 8.3 Turnover Reporting | PKG_REPORTING.turnover_report | EMPLOYEES, DEPARTMENTS | HRMS_REPORTS |
| 8.4 New Hire Reporting | PKG_REPORTING.new_hires_report | EMPLOYEES, JOB_TITLES, LOCATIONS, SALARY_RECORDS | HRMS_REPORTS |
| 8.5 Leave Utilisation Reporting | PKG_REPORTING.leave_utilization_report | LEAVE_BALANCES, LEAVE_TYPES | HRMS_REPORTS |
| 8.6 Payroll Summary Reporting | PKG_REPORTING.payroll_summary_report | PAYROLL_DETAILS, PAYROLL_RUNS | HRMS_REPORTS |
| 8.7 EEO Compliance Reporting | PKG_REPORTING.eeo_compliance_report | EMPLOYEES, JOB_TITLES | HRMS_REPORTS |
| 9.1 Benefits Feed (ADP) | PKG_INTEGRATION.export_benefits_feed | EMPLOYEES, EMPLOYEE_DEPENDENTS | — |
| 9.2 Payroll GL Feed | PKG_INTEGRATION.generate_gl_journal | PAYROLL_RUNS, PAYROLL_DETAILS, DEPARTMENTS | — |
| 9.3 Time & Attendance Import | PKG_INTEGRATION.import_time_attendance | TIME_ATTENDANCE_RECORDS (inferred, unused) | — |
| 9.4 Org Structure Sync | PKG_INTEGRATION.sync_org_structure | — (stub) | — |
| 9.5 Reporting Table Refresh | PKG_REPORTING.refresh_reporting_tables | RPT_* tables (inferred) | — |
| 10.1 Notification Queue | PKG_NOTIFICATION | NOTIFICATION_QUEUE | — |
| 10.2 Template Management | PKG_NOTIFICATION | NOTIFICATION_TEMPLATES | — |
| 10.3 Payslip Distribution | PKG_NOTIFICATION (partial) | NOTIFICATION_QUEUE | — |
| 10.4 Leave Decision Notification | PKG_NOTIFICATION, PKG_LEAVE | NOTIFICATION_QUEUE | — |

---

## 4. Capability Gaps

These are capabilities needed by the future system that are entirely absent or critically broken in the current Oracle HRMS. They are gaps to be **built**, not merely migrated.

| Gap ID | Missing Capability | Business Need | Severity | Evidence |
|---|---|---|---|---|
| GAP-01 | Direct Deposit Disbursement (ACH/NACHA) | Payroll completion — net pay must reach employees | CRITICAL | EMPLOYEE_BANK_ACCOUNTS never read; no disbursement procedure; no NACHA file generation (BR-BA-12, PP-BA-01) |
| GAP-02 | Final Pay Calculation on Termination | Legal obligation to pay wages owed at separation | CRITICAL | `PKG_PAYROLL.calculate_final_pay` does not exist (PP-TERM-03) |
| GAP-03 | COBRA Notification & Tracking | Federal ACA/COBRA compliance — 14-day notification window | CRITICAL | Zero code for COBRA in terminate_employee; every termination is an unreported qualifying event (PP-TERM-01) |
| GAP-04 | Rating Calibration Workflow | HR fairness across managers before official rating is published | CRITICAL | CALIBRATED_RATING is a dead column; no status, no procedure, no UI |
| GAP-05 | Password Authentication | Basic security — users must be verified against stored credential | CRITICAL | `authenticate()` never queries USER_CREDENTIALS; all users authenticate with any password (BR-042) |
| GAP-06 | Time & Attendance Data Import | Payroll accuracy for hourly/contract employees | CRITICAL | `import_time_attendance` performs zero DML; time data is never loaded (BR-046) |
| GAP-07 | Org Structure Sync (LDAP/AD) | IT provisioning, access reviews, org chart tools | CRITICAL | `sync_org_structure` is a placeholder; logs false success (BR-ORG-01/02) |
| GAP-08 | Reporting Snapshot Refresh | Stable, performant reporting layer for BI tools | CRITICAL | `refresh_reporting_tables` stub; all reports query OLTP directly (BR-043) |
| GAP-09 | Session Revocation on Termination | Immediate access cut-off for terminated employees | HIGH | `PKG_SECURITY.revoke_access` does not exist; 30-minute window remains (PP-TERM-02) |
| GAP-10 | ACH Prenote Process | Nacha compliance before first live disbursement to a bank account | HIGH | PRENOTE_SENT/PRENOTE_DATE columns exist but no procedure populates them (PP-BA-03) |
| GAP-11 | Bank Account Validation (DEPOSIT_TYPE / distribution totals) | Prevent partial/percent splits that sum to ≠ 100% | HIGH | No cross-column or totalling constraint (BR-BA-09, BR-BA-11, PP-BA-04/05) |
| GAP-12 | Dependent Inactivation on Termination | Prevent terminated employees' dependents from receiving benefits | HIGH | terminate_employee does not touch EMPLOYEE_DEPENDENTS (BR-DEP-09) |
| GAP-13 | FMLA Document Enforcement | Audit compliance — FMLA requests must have supporting documentation | MEDIUM | FMLA seed data has REQUIRES_DOCUMENT='N'; no document path enforcement (TD-71) |
| GAP-14 | GL Feed Acknowledgement & Reconciliation | Confirm payroll data reached Oracle Financials | MEDIUM | No GL_FEED_SENT_DATE on PAYROLL_RUNS; no receipt file (TD-80) |
| GAP-15 | Multi-year Leave Snapshot | Historical trend analysis requires year dimension in reporting snapshots | MEDIUM | CALENDAR_YEAR not projected in leave_utilization cursor (DQ-032) |
| GAP-16 | Structured Audit Logging (JSON, correlation ID) | Operational observability; SIEM integration | MEDIUM | AUDIT_LOG uses free-text; no severity levels; no correlation ID (TA observability findings) |
| GAP-17 | CI/CD Pipeline | Repeatable builds, SAST, secret scanning, automated deployment | HIGH | Zero CI/CD capability found across entire repository (TA CI/CD assessment) |
| GAP-18 | Encryption Key Management (external vault) | Remove hard-coded AES key from source | CRITICAL | AES key `HR$ystem_3ncrypt10n_K3y_2024!!` in source (TD-01) |
| GAP-19 | Routing Number Encryption | Protect full ACH credentials at rest | MEDIUM | ROUTING_NUMBER stored plaintext while ACCOUNT_NUMBER_ENC is encrypted (TD-46) |
| GAP-20 | Background Session Cleanup Job | Sweep and expire stale sessions | MEDIUM | No DBMS_SCHEDULER job for session sweep (TD-75) |

---

## 5. Investment Priority

Priorities are assigned based on: legal/compliance exposure, blocking dependencies, frequency of use, and migration risk. Three tiers are used.

### Tier 1 — Must-Have Before Go-Live (Blockers)

These gaps create legal liability, security breaches, or render core processes non-functional. The new system cannot go live without them.

| Priority | Capability | Gap(s) | Rationale |
|---|---|---|---|
| P1-01 | Password Authentication | GAP-05 | Authentication stub means zero access security. Any user can log in as any other. Must be replaced before migration is even testable. |
| P1-02 | Encryption Key Management | GAP-18 | Hard-coded AES key must be replaced with vault-managed key before migrating any encrypted data (SSN, bank accounts). Prerequisite for all data migration steps. |
| P1-03 | Direct Deposit Disbursement (ACH) | GAP-01, GAP-10, GAP-11 | Payroll is the primary system function. Without disbursement, the system has never fully paid employees. |
| P1-04 | Final Pay Calculation | GAP-02 | Every employee termination requires manual payroll intervention. Legal wage payment obligation. |
| P1-05 | COBRA Notification | GAP-03 | Federal law (ERISA/ACA) — 14-day notification window; non-compliance fines per employee per event. |
| P1-06 | COBRA Tracking | GAP-03 | Required continuation period monitoring post-notification. |
| P1-07 | Rating Calibration Workflow | GAP-04 | Without calibration, published ratings are uncalibrated manager scores. Reporting is misleading. Blocks merit eligibility accuracy. |
| P1-08 | Time & Attendance Import | GAP-06 | Hourly and contract employee payroll accuracy depends on this. Current stub means all time data is manual. |
| P1-09 | Session Revocation on Termination | GAP-09 | Terminated employees retain session access for up to 30 minutes. Security requirement. |
| P1-10 | Dependent Inactivation on Termination | GAP-12 | Benefits fraud exposure — terminated employees' dependents remain on active feed to ADP. |

### Tier 2 — High Value, Required within First Release Cycle

These are significant operational gaps that must be closed in the first production release cycle (0–3 months post-go-live).

| Priority | Capability | Gap(s) | Rationale |
|---|---|---|---|
| P2-01 | GL Feed Acknowledgement | GAP-14 | Finance cannot confirm payroll journal entries landed in Oracle Financials. Reconciliation is manual. |
| P2-02 | ACH Prenote Implementation | GAP-10 | Nacha compliance before first live direct deposit. Can run parallel with Tier 1 disbursement build. |
| P2-03 | Org Structure Sync (LDAP/AD) | GAP-07 | IT provisioning depends on this; currently a stub that logs false success every run — active deception of monitoring. |
| P2-04 | Reporting Snapshot Refresh | GAP-08 | All 7 reports currently query OLTP directly. Performance and consistency risk at scale. |
| P2-05 | Background Session Cleanup | GAP-20 | Operational hygiene; prevents session table growth; closes the stale-session window. |
| P2-06 | Routing Number Encryption | GAP-19 | ACH credentials should be fully encrypted; routing number is the remaining plaintext half. |
| P2-07 | CI/CD Pipeline | GAP-17 | Without build automation, every deployment is a manual DBA script run. SAST and secret scanning prevent credential re-introduction. |
| P2-08 | FMLA Document Enforcement | GAP-13 | HR audit compliance; document upload and validation at leave submission. |

### Tier 3 — Quality Improvements (Post-Stabilisation)

These address data quality, observability, and reporting accuracy. Plan for months 4–12 post-go-live.

| Priority | Capability | Gap(s) | Rationale |
|---|---|---|---|
| P3-01 | Structured Audit Logging | GAP-16 | Enables SIEM integration, alerting, and compliance dashboards. Current free-text AUDIT_LOG is not machine-parseable. |
| P3-02 | Multi-year Leave Snapshots | GAP-15 | Year dimension needed for trend reporting in BI. Quick schema fix but requires ETL/reporting redesign. |
| P3-03 | Turnover Report Denominator Fix | — (BR-044) | Align turnover calculation with SHRM standard denominator (average headcount). Needed for benchmarking. |
| P3-04 | Salary Grade Validation (blocking) | TD-74 | Elevate soft warning to blocking error in both PKG_EMPLOYEE and HRMS_VALIDATION_LIB. Prevents compensation band violations. |
| P3-05 | EEO Gender Constraint | TD-40 | Add CHECK constraint on EMPLOYEES.GENDER to prevent arbitrary values distorting EEO reporting. |
| P3-06 | ADP Feed Validation (header/trailer/checksum) | TD-73 | Add format version header, record count trailer, and per-record length validation to benefits feed. |
| P3-07 | Bank Account Validation Rules | GAP-11 | Cross-column and totalling constraints for split-deposit configurations. |
| P3-08 | Password Change — Old Password Verification | DQ-029 | `change_password` must verify the current credential before accepting a new one. |

---

## Appendix A — Capability Coverage Matrix

| L1 Domain | Total L2 Caps | OK | Medium | High | Critical | Not Implemented |
|---|---|---|---|---|---|---|
| 1. Workforce Mgmt | 6 | 3 | 1 | 2 | 0 | 0 |
| 2. Compensation & Payroll | 7 | 1 | 2 | 2 | 2 | 2 |
| 3. Leave Management | 6 | 3 | 2 | 1 | 0 | 0 |
| 4. Performance Mgmt | 7 | 4 | 1 | 1 | 1 | 1 |
| 5. Benefits Admin | 5 | 2 | 1 | 1 | 1 | 0 |
| 6. Org Structure | 4 | 2 | 1 | 0 | 1 | 0 |
| 7. Security & Access | 6 | 0 | 2 | 3 | 1 | 0 |
| 8. Reporting & Analytics | 7 | 4 | 3 | 0 | 0 | 0 |
| 9. Integration | 5 | 0 | 1 | 1 | 3 | 0 |
| 10. Notifications | 4 | 2 | 2 | 0 | 0 | 0 |
| **Total** | **57** | **21** | **16** | **11** | **9** | **3** |

**37% of capabilities are rated High or Critical risk.** Security (domain 7) and Integration (domain 9) are the weakest domains with 0 OK-rated capabilities between them.

---

## Appendix B — Cross-Reference: Capability Gap → Business Rule

| Gap ID | Business Rule(s) | Severity |
|---|---|---|
| GAP-01 | BR-BA-12, PP-BA-01, AV-024 | CRITICAL |
| GAP-02 | PP-TERM-03, BR-TERM-07 | CRITICAL |
| GAP-03 | PP-TERM-01, BR-TERM-01 | CRITICAL |
| GAP-04 | (calibration workflow gap — no BR assigned) | CRITICAL |
| GAP-05 | BR-042 | CRITICAL |
| GAP-06 | BR-046, DQ-031 | CRITICAL |
| GAP-07 | BR-ORG-01, BR-ORG-02 | CRITICAL |
| GAP-08 | BR-043, DQ-031 | CRITICAL |
| GAP-09 | PP-TERM-02, BR-TERM-05 | HIGH |
| GAP-10 | PP-BA-03, BR-BA-05 | HIGH |
| GAP-11 | BR-BA-09, BR-BA-11 | HIGH |
| GAP-12 | BR-DEP-09, PP-DEP-04 | HIGH |
| GAP-13 | TD-71 | MEDIUM |
| GAP-14 | TD-80, TD-79 | MEDIUM |
| GAP-15 | DQ-032 | MEDIUM |
| GAP-16 | TD-37, TA observability | MEDIUM |
| GAP-17 | TA CI/CD section | HIGH |
| GAP-18 | TD-01, DQ-001 | CRITICAL |
| GAP-19 | TD-46 | MEDIUM |
| GAP-20 | TD-75 | MEDIUM |
