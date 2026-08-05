# Use Case Specification
## Oracle HRMS — Acme Corporation
**Document ID:** 03_USE_CASE_SPECIFICATION  
**Version:** 1.0  
**Status:** Draft  
**Prepared By:** Business Analysis Team  
**System:** Acme Corporation HRMS (Oracle 19c / Oracle Forms 12c)  
**Date:** 2026-08-05

---

## Table of Contents

1. [Actor Catalogue](#1-actor-catalogue)
2. [Use Case Summary Table](#2-use-case-summary-table)
3. [Detailed Use Cases](#3-detailed-use-cases)
   - UC-001: Hire Employee
   - UC-002: Process Monthly Payroll
   - UC-003: Submit Leave Request
   - UC-004: Approve Leave Request
   - UC-005: Terminate Employee
   - UC-006: Conduct Performance Review
   - UC-007: Update Salary
   - UC-008: Authenticate User
   - UC-009: Generate Reports
   - UC-010: Manage Benefits Enrollment
   - UC-011: Rehire Employee
   - UC-012: Process Deductions
   - UC-013: Manage Job Positions
   - UC-014: Run Payroll Audit
   - UC-015: Manage Leave Types
4. [Use Case Dependency Diagram](#4-use-case-dependency-diagram)
5. [Business Rule Cross-Reference](#5-business-rule-cross-reference)

---

## 1. Actor Catalogue

This section defines every actor that interacts with the Acme HRMS system. Actors are categorised as Primary (initiates use cases), Secondary (participates in use cases), or External (outside the system boundary).

---

### 1.1 HR Manager

| Attribute | Detail |
|-----------|--------|
| **Actor ID** | ACT-001 |
| **Name** | HR Manager |
| **Category** | Primary |
| **Oracle Grade** | Grade 8 or above |
| **HRMS Access Level** | Full access — read and write to all HR functions |
| **Authentication** | Oracle Forms session via PKG_SECURITY.authenticate; session token enforced |
| **Description** | Responsible for the full employee lifecycle including hiring, transfers, salary adjustments, terminations, performance cycle management, leave approvals, and regulatory compliance. The HR Manager is the primary initiator of most administrative use cases. Grade ≥ 8 grants full schema-level access enforced by PKG_SECURITY.has_permission. |
| **Typical Goals** | Hire and onboard new staff; approve or reject leave; run payroll; manage organisational structure; generate compliance reports |
| **Constraints** | Cannot terminate employees without a valid TERMINATION_CODE; cannot create payroll runs for closed pay periods; salary changes must fall within JOB_GRADES band (soft warning only — see BR-74) |
| **Associated Packages** | PKG_EMPLOYEE, PKG_PAYROLL, PKG_LEAVE, PKG_PERFORMANCE, PKG_REPORTING, PKG_SECURITY |

---

### 1.2 Employee

| Attribute | Detail |
|-----------|--------|
| **Actor ID** | ACT-002 |
| **Name** | Employee |
| **Category** | Primary |
| **Oracle Grade** | Grade 1–7 |
| **HRMS Access Level** | Restricted — own records only (Grade < 5); view-all for Grades 5–7 |
| **Authentication** | Oracle Forms / Self-Service Portal session via PKG_SECURITY.authenticate |
| **Description** | Any current active employee of Acme Corporation with a valid EMPLOYMENT_STATUS = 'ACTIVE' record. Employees can access the self-service portal to submit leave requests, view their own payslips, update personal details, submit self-assessments during performance review cycles, and acknowledge completed performance reviews. |
| **Typical Goals** | Submit leave requests; view pay history; update personal contact details; participate in performance reviews; view leave balances |
| **Constraints** | Can only view and modify own records unless Grade 5–7 (view-all); cannot approve their own leave; cannot initiate payroll; cannot terminate other employees |
| **Associated Packages** | PKG_LEAVE, PKG_SECURITY (session management) |

---

### 1.3 Payroll Administrator

| Attribute | Detail |
|-----------|--------|
| **Actor ID** | ACT-003 |
| **Name** | Payroll Administrator |
| **Category** | Primary |
| **Oracle Grade** | Grade 6–8 (typically) |
| **HRMS Access Level** | Full access to Compensation bounded context; view access to Employee Identity |
| **Authentication** | Oracle Forms session; Grade-based RBAC via PKG_SECURITY.has_permission |
| **Description** | Specialist HR staff responsible for processing monthly payroll runs, managing pay elements, configuring deductions, approving payroll calculations before disbursement, generating GL journal feeds for Oracle Financials, and running payroll audits. The Payroll Administrator owns the compensation lifecycle from pay period open through to GL export. |
| **Typical Goals** | Create and calculate monthly payroll runs; review and approve payroll; generate GL journal file; configure deduction types and rates; audit payroll accuracy |
| **Constraints** | Cannot disburse payroll directly (no EMPLOYEE_BANK_ACCOUNTS read procedure implemented — critical gap); cannot process final pay for terminated employees without manual workaround (PKG_PAYROLL.calculate_final_pay not implemented) |
| **Associated Packages** | PKG_PAYROLL, PKG_INTEGRATION, PKG_REPORTING |

---

### 1.4 System Administrator

| Attribute | Detail |
|-----------|--------|
| **Actor ID** | ACT-004 |
| **Name** | System Administrator |
| **Category** | Primary |
| **Oracle Grade** | Grade 10 (DBA / system owner) |
| **HRMS Access Level** | Full Oracle schema-level access; manages SYSTEM_PARAMETERS, LOOKUP_VALUES, reference data |
| **Authentication** | Oracle DBA credentials; Oracle Forms session for application-layer tasks |
| **Description** | Responsible for system configuration, reference data maintenance (LOOKUP_VALUES, SYSTEM_PARAMETERS), user account management, database health, job scheduler configuration (DBMS_SCHEDULER), and resolving data integrity issues. The System Administrator also manages integration endpoints and Oracle Forms deployment. |
| **Typical Goals** | Configure system parameters; maintain lookup/reference data; manage job scheduler; resolve data quality issues; administer user accounts and access grants |
| **Constraints** | Changes to SYSTEM_PARAMETERS require testing as many timeout and behavioural settings are hard-coded in PL/SQL and not read from the table (known defect — session timeout ignores SYSTEM_PARAMETERS); no CI/CD pipeline exists so all deployments are manual |
| **Associated Packages** | PKG_COMMON, PKG_SECURITY, all packages (DBA access) |

---

### 1.5 Secondary and External Actors

| Actor ID | Name | Type | Role |
|----------|------|------|------|
| ACT-005 | Direct Manager | Secondary | Approves leave requests; conducts manager review in performance cycles; appears as REVIEWER_EMP_ID in PERFORMANCE_REVIEWS |
| ACT-006 | Oracle DBMS Scheduler | Secondary | Executes scheduled jobs (monthly accruals, notification dispatch, queue processing); no human interaction |
| ACT-007 | ADP Benefits Provider | External | Receives fixed-width 203-character benefits feed file from PKG_INTEGRATION.export_benefits_feed |
| ACT-008 | Oracle Financials GL | External | Receives pipe-delimited GL journal import file from PKG_INTEGRATION.generate_gl_journal |
| ACT-009 | Time & Attendance System | External | Provides CSV import file read by PKG_INTEGRATION.import_time_attendance (stub — not functional) |
| ACT-010 | SMTP Mail Server | External | Receives notification emails dispatched from PKG_NOTIFICATION via UTL_SMTP; email channel only (SMS channel unimplemented) |

---

## 2. Use Case Summary Table

| UC ID | Use Case Name | Primary Actor | Secondary Actor | Priority | Status | Bounded Context |
|-------|--------------|---------------|-----------------|----------|--------|-----------------|
| UC-001 | Hire Employee | HR Manager | System (PKG_EMPLOYEE) | Critical | Implemented | Employee Identity |
| UC-002 | Process Monthly Payroll | Payroll Administrator | HR Manager, Oracle Financials GL | Critical | Implemented (with gaps) | Compensation |
| UC-003 | Submit Leave Request | Employee | — | High | Implemented | Leave Management |
| UC-004 | Approve Leave Request | Direct Manager / HR Manager | Employee | High | Implemented | Leave Management |
| UC-005 | Terminate Employee | HR Manager | System (PKG_EMPLOYEE) | Critical | Implemented (with critical gaps) | Employee Identity |
| UC-006 | Conduct Performance Review | Direct Manager | Employee, HR Manager | High | Implemented (calibration absent) | Performance |
| UC-007 | Update Salary | HR Manager | Payroll Administrator | High | Implemented (soft validation only) | Compensation |
| UC-008 | Authenticate User | Employee / HR Manager / Payroll Admin / System Admin | System (PKG_SECURITY) | Critical | Implemented (auth stub — critical defect) | Security & Access |
| UC-009 | Generate Reports | HR Manager / Payroll Administrator | System (PKG_REPORTING) | High | Implemented | Reporting |
| UC-010 | Manage Benefits Enrollment | HR Manager | Employee, ADP Benefits Provider | Medium | Partially implemented | Benefits |
| UC-011 | Rehire Employee | HR Manager | System (PKG_EMPLOYEE) | Medium | Implemented | Employee Identity |
| UC-012 | Process Deductions | Payroll Administrator | System (PKG_PAYROLL) | High | Implemented | Compensation |
| UC-013 | Manage Job Positions | HR Manager / System Admin | — | Medium | Implemented | Org Structure |
| UC-014 | Run Payroll Audit | Payroll Administrator | HR Manager | High | Implemented | Compensation |
| UC-015 | Manage Leave Types | System Admin / HR Manager | — | Medium | Implemented | Leave Management |

---

## 3. Detailed Use Cases

---

### UC-001: Hire Employee

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-001 |
| **Use Case Name** | Hire Employee |
| **Actor(s)** | HR Manager (primary) |
| **Priority** | Critical |
| **Frequency** | As required; typically several times per month |
| **Implementing Package** | PKG_EMPLOYEE.create_employee |
| **Related Business Rules** | BR-01, BR-02, BR-03, BR-11, BR-12, BR-74 |

**Brief Description**  
The HR Manager creates a new employee record in the HRMS system following an accepted job offer. The system generates a unique employee identifier, initialises leave balances, and creates the first salary record.

**Preconditions**
1. The HR Manager is authenticated with an active session (Grade ≥ 8).
2. The job position exists and is active in JOB_POSITIONS.
3. The target department exists and is active in DEPARTMENTS.
4. A valid JOB_GRADE entry exists for the proposed salary range.
5. A valid TERMINATION_CODE does not apply (employee must not already exist in the system with ACTIVE status for the same national ID / SSN).

**Main Flow**
1. HR Manager navigates to the HRMS_EMPLOYEE form and selects "New Employee."
2. HR Manager enters mandatory fields: FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, SSN (plaintext — encrypted on save via PKG_SECURITY.encrypt_value using AES-256), EMAIL, HIRE_DATE, DEPARTMENT_ID, JOB_TITLE, GRADE, BASE_SALARY, EMPLOYMENT_TYPE.
3. HR Manager optionally enters: MIDDLE_NAME, PHONE, ADDRESS details, MARITAL_STATUS, TAX_FILING_STATUS, MANAGER_ID.
4. HR Manager selects a JOB_POSITION from the LOV (LOV_POSITIONS filtered by ACTIVE_FLAG = 'Y').
5. System validates HIRE_DATE is not in the future (BR-11).
6. System validates GRADE is within the MIN_GRADE–MAX_GRADE range for the selected JOB_POSITION. **Note:** this is a soft warning (MESSAGE) not a blocking error (BR-74 / TD-74 defect).
7. System validates EMAIL uniqueness across EMPLOYEES table.
8. System validates BASE_SALARY > 0.
9. System calls PKG_EMPLOYEE.create_employee which:
   a. Generates EMPLOYEE_NUMBER via sequence SQ_EMPLOYEE_ID.
   b. Inserts row into EMPLOYEES with EMPLOYMENT_STATUS = 'ACTIVE' and ACTIVE_FLAG = 'Y'.
   c. Inserts initial row into SALARY_RECORDS (EFFECTIVE_DATE = HIRE_DATE, END_DATE = NULL).
   d. Calls PKG_LEAVE.initialize_balances to create LEAVE_BALANCES rows for all active LEAVE_TYPES.
   e. Writes audit record to AUDIT_LOG via PKG_COMMON.log_info.
10. System displays the newly generated EMPLOYEE_NUMBER to the HR Manager.
11. System triggers a welcome notification via PKG_NOTIFICATION if NOTIFICATION_TEMPLATES contains a hire template.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-001-A | EMAIL already exists for an ACTIVE employee | System raises ORA-20001 "Email already exists"; HR Manager must supply a unique email |
| AF-001-B | GRADE outside JOB_POSITION grade range | System displays a warning MESSAGE (non-blocking); HR Manager may proceed — **known defect, should be blocking** |
| AF-001-C | TAX_FILING_STATUS = 'HEAD_OF_HOUSEHOLD' | Federal tax will calculate as $0 for this employee — critical defect (BR-19). HR Manager is not warned at hire time |
| AF-001-D | No LEAVE_TYPE records exist | PKG_LEAVE.initialize_balances inserts zero rows; employee has no leave balances — HR Manager must manually initialise |

**Postconditions**
1. A new row exists in EMPLOYEES with EMPLOYMENT_STATUS = 'ACTIVE'.
2. A corresponding row exists in SALARY_RECORDS with END_DATE = NULL.
3. LEAVE_BALANCES rows exist for all active leave types for the new employee.
4. An AUDIT_LOG entry records the creation event.
5. EMPLOYEE_NUMBER is assigned and returned to the HR Manager.

**Business Rules**
- BR-01: EMPLOYEE_NUMBER must be system-generated and unique.
- BR-02: SSN is encrypted at rest using AES-256-CBC-PKCS5 via PKG_SECURITY.encrypt_value.
- BR-03: EMAIL must be unique across EMPLOYEES.
- BR-11: HIRE_DATE must not be in the future.
- BR-74 (defect): Grade–salary band validation is soft warning only; should be a blocking error.

**Open Issues**
- OI-001-1: TAX_FILING_STATUS = 'HEAD_OF_HOUSEHOLD' produces $0 federal tax (confirmed defect). Must be resolved before next payroll run for any HOH employee.
- OI-001-2: Direct deposit bank details entered at hire are stored in EMPLOYEES.BANK_ACCOUNT_NUMBER (encrypted) but no disbursement procedure exists; payroll disbursement is entirely manual.

---

### UC-002: Process Monthly Payroll

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-002 |
| **Use Case Name** | Process Monthly Payroll |
| **Actor(s)** | Payroll Administrator (primary); HR Manager (approval) |
| **Priority** | Critical |
| **Frequency** | Monthly |
| **Implementing Package** | PKG_PAYROLL.create_payroll_run, calculate_payroll, approve_payroll, PKG_INTEGRATION.generate_gl_journal |
| **Related Business Rules** | BR-15, BR-16, BR-17, BR-18, BR-19, BR-20, BR-21 |

**Brief Description**  
The Payroll Administrator initiates, calculates, reviews, and approves the monthly payroll run for all active employees. Upon approval, a GL journal file is generated for import into Oracle Financials.

**Preconditions**
1. Payroll Administrator is authenticated with Grade ≥ 6 session.
2. No existing PAYROLL_RUN exists with STATUS = 'DRAFT' or 'CALCULATED' for the same pay period.
3. All active employees have a SALARY_RECORDS row with END_DATE = NULL.
4. Pay period start and end dates are valid and do not overlap with a closed period.
5. TAX_BRACKETS reference data is populated for the current tax year.

**Main Flow**
1. Payroll Administrator opens HRMS_PAYROLL form and selects "New Payroll Run."
2. Payroll Administrator enters RUN_NAME, PAY_PERIOD_START, PAY_PERIOD_END.
3. System calls PKG_PAYROLL.create_payroll_run; inserts PAYROLL_RUNS row with STATUS = 'DRAFT'.
4. Payroll Administrator selects "Calculate Payroll."
5. System calls PKG_PAYROLL.calculate_payroll which loops over all EMPLOYMENT_STATUS = 'ACTIVE' employees and for each:
   a. Retrieves current BASE_SALARY from SALARY_RECORDS (MAX(EFFECTIVE_DATE), END_DATE IS NULL).
   b. Calculates GROSS_PAY = BASE_SALARY / 12.
   c. Applies federal income tax using TAX_BRACKETS lookup (MARITAL_STATUS + FILING_STATUS).
   d. Applies flat-rate state income tax by STATE code.
   e. Calculates Social Security (6.2% up to wage base) and Medicare (1.45%).
   f. Applies any active deductions from DEDUCTION_RECORDS.
   g. Reads OVERALL_RATING from PERFORMANCE_REVIEWS to determine merit eligibility (rating ≥ 3.0 required).
   h. Inserts row into PAYROLL_DETAILS with STATUS = 'CALCULATED'.
6. System updates PAYROLL_RUNS.STATUS to 'CALCULATED' and sets CALCULATED_DATE.
7. Payroll Administrator reviews summary totals (TOTAL_GROSS, TOTAL_NET, TOTAL_DEDUCTIONS) in HRMS_PAYROLL.
8. HR Manager (or Payroll Administrator with Grade ≥ 8) calls approve_payroll.
9. System updates PAYROLL_RUNS.STATUS to 'APPROVED'; sets APPROVED_BY, APPROVED_DATE.
10. Payroll Administrator triggers GL journal generation via PKG_INTEGRATION.generate_gl_journal.
11. System writes pipe-delimited GL journal file to Oracle Directory GL_JOURNAL_OUT.
12. System updates PAYROLL_RUNS.STATUS to 'GL_GENERATED'.
13. Payroll Administrator manually imports GL file into Oracle Financials (external step — no automated handshake).

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-002-A | Employee has HEAD_OF_HOUSEHOLD tax status | Federal tax calculated as $0 (confirmed defect — BR-19). Payroll completes but tax amount is incorrect |
| AF-002-B | Employee has no current SALARY_RECORDS row | PKG_PAYROLL raises exception; employee is skipped; error written to AUDIT_LOG; run continues for remaining employees |
| AF-002-C | PAYROLL_RUN already exists for period | System raises duplicate period error; Payroll Administrator must delete the existing DRAFT run first |
| AF-002-D | GL file generation fails (UTL_FILE error) | No STATUS update to PAYROLL_RUNS; no retry mechanism; Payroll Administrator must re-trigger manually; no GL_FEED_STATUS column to track success (known gap — TD-80) |
| AF-002-E | Employee terminated during pay period | No prorated pay calculation exists (PKG_PAYROLL.calculate_final_pay is not implemented); final pay must be calculated manually outside the system |

**Postconditions**
1. PAYROLL_RUNS.STATUS = 'GL_GENERATED' (or 'APPROVED' if GL step not yet run).
2. One PAYROLL_DETAILS row exists per active employee for this run.
3. GL journal file written to GL_JOURNAL_OUT Oracle directory.
4. AUDIT_LOG entries exist for run creation, calculation, approval, and GL generation steps.

**Business Rules**
- BR-15: Gross pay = BASE_SALARY / 12 for MONTHLY salary type.
- BR-16: Federal tax calculated using graduated TAX_BRACKETS by filing status.
- BR-17: Social Security tax rate = 6.2% up to annual wage base.
- BR-18: Medicare tax rate = 1.45% (no high-earner surcharge implemented).
- BR-19 (defect): HEAD_OF_HOUSEHOLD filing status produces $0 federal tax.
- BR-20: State income tax applied as flat rate by STATE code.

**Open Issues**
- OI-002-1: No direct deposit disbursement — EMPLOYEE_BANK_ACCOUNTS table is never read during payroll (PP-BA-01 / DISC-009 critical).
- OI-002-2: PKG_PAYROLL.calculate_final_pay does not exist; terminated employee final pay is fully manual.
- OI-002-3: No GL_FEED_STATUS field on PAYROLL_RUNS — missed GL feeds are invisible to the system.

---

### UC-003: Submit Leave Request

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-003 |
| **Use Case Name** | Submit Leave Request |
| **Actor(s)** | Employee (primary) |
| **Priority** | High |
| **Frequency** | Several times per month per employee |
| **Implementing Package** | PKG_LEAVE.submit_leave_request |
| **Related Business Rules** | BR-30, BR-31, BR-32, BR-33, BR-34 |

**Brief Description**  
An active employee submits a leave request for a specific leave type, date range, and number of days, via the self-service portal or HRMS_LEAVE form.

**Preconditions**
1. Employee is authenticated with EMPLOYMENT_STATUS = 'ACTIVE'.
2. A valid LEAVE_TYPE exists and is active (ACTIVE_FLAG = 'Y').
3. Employee has a LEAVE_BALANCES row for the requested leave type.
4. Employee's available balance (OPENING + ACCRUED - TAKEN - PENDING) ≥ requested days.

**Main Flow**
1. Employee logs into the self-service portal or HRMS_LEAVE form.
2. Employee selects leave type from LOV (filtered to leave types where employee has a balance).
3. Employee enters START_DATE, END_DATE, and optionally REASON.
4. System calculates REQUESTED_DAYS = working days between START_DATE and END_DATE (excluding weekends; public holidays not implemented).
5. System checks available balance ≥ REQUESTED_DAYS.
6. System calls PKG_LEAVE.submit_leave_request:
   a. Inserts row into LEAVE_REQUESTS with STATUS = 'PENDING'.
   b. Updates LEAVE_BALANCES.PENDING = PENDING + REQUESTED_DAYS.
   c. Writes audit log entry.
7. System triggers notification to the employee's direct manager via PKG_NOTIFICATION (EMAIL channel only; SMS unimplemented).
8. System confirms submission to employee and displays the LEAVE_REQUEST_ID.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-003-A | Insufficient balance | System raises ORA-20301 "Insufficient leave balance"; request is not created |
| AF-003-B | LEAVE_TYPE requires documentation (REQUIRES_DOCUMENT = 'Y') | FMLA leave: REQUIRES_DOCUMENT is currently seeded as 'N' for FMLA — documentation is not enforced (TD-71 defect); no block occurs |
| AF-003-C | Overlapping leave request already PENDING or APPROVED | System should reject overlapping dates; overlap check implementation status is unconfirmed — validate with development team |
| AF-003-D | Manager notification fails (SMTP error) | Leave request is still created; notification failure is logged to AUDIT_LOG; employee is not informed of notification failure |

**Postconditions**
1. LEAVE_REQUESTS row exists with STATUS = 'PENDING'.
2. LEAVE_BALANCES.PENDING incremented by REQUESTED_DAYS.
3. Notification sent to direct manager.
4. AUDIT_LOG entry recorded.

**Business Rules**
- BR-30: Leave request requires an active LEAVE_TYPE with an existing balance row.
- BR-31: Available balance must cover the requested days.
- BR-32: PENDING balance is updated at submission, not at approval, to prevent double-booking.
- BR-33: Leave requests cannot be submitted by employees with EMPLOYMENT_STATUS ≠ 'ACTIVE'.
- BR-34: Supporting document enforcement controlled by LEAVE_TYPES.REQUIRES_DOCUMENT flag (FMLA defect: flag seeded as 'N').

---

### UC-004: Approve Leave Request

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-004 |
| **Use Case Name** | Approve Leave Request |
| **Actor(s)** | Direct Manager or HR Manager (primary); Employee (notified) |
| **Priority** | High |
| **Frequency** | Several times per month |
| **Implementing Package** | PKG_LEAVE.approve_leave_request, reject_leave_request |
| **Related Business Rules** | BR-35, BR-36, BR-37 |

**Brief Description**  
A direct manager or HR Manager reviews a pending leave request and either approves or rejects it. Upon approval, the employee's leave balance is updated.

**Preconditions**
1. An active LEAVE_REQUEST with STATUS = 'PENDING' exists.
2. Approver is authenticated with appropriate Grade and is the employee's manager or an HR Manager (Grade ≥ 8).
3. Approver cannot be the same person as the requestor.

**Main Flow**
1. Manager receives email notification or navigates to HRMS_LEAVE approval queue.
2. Manager reviews the leave request details (employee, dates, type, reason, current balance).
3. Manager selects "Approve."
4. System calls PKG_LEAVE.approve_leave_request:
   a. Updates LEAVE_REQUESTS.STATUS = 'APPROVED'.
   b. Updates LEAVE_BALANCES: TAKEN = TAKEN + REQUESTED_DAYS; PENDING = PENDING - REQUESTED_DAYS.
   c. Sets APPROVED_BY, APPROVED_DATE.
   d. Writes audit log.
5. System triggers notification to employee confirming approval.
6. System returns updated leave balance summary.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-004-A | Manager selects "Reject" | System calls PKG_LEAVE.reject_leave_request; STATUS = 'REJECTED'; LEAVE_BALANCES.PENDING reversed; employee notified of rejection |
| AF-004-B | Leave request already approved or rejected | System raises error; manager redirected to current status view |
| AF-004-C | Employee terminated between submission and approval | EMPLOYMENT_STATUS check not performed at approval time — potential data quality issue; HR Manager should cancel pending leave on termination |
| AF-004-D | Approver is requestor's subordinate | No organisational hierarchy check exists in PKG_LEAVE — any authenticated Grade ≥ 5 user can approve any request (access control gap) |

**Postconditions**
1. LEAVE_REQUESTS.STATUS = 'APPROVED' or 'REJECTED'.
2. LEAVE_BALANCES.TAKEN and PENDING updated correctly.
3. Employee notified via email.
4. AUDIT_LOG entry recorded with approver identity.

**Business Rules**
- BR-35: Approval transitions PENDING balance to TAKEN balance atomically.
- BR-36: Only one APPROVED request per employee per date range (overlap rule — implementation unconfirmed).
- BR-37: Approved_by must reference a valid EMPLOYEES row.

---

### UC-005: Terminate Employee

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-005 |
| **Use Case Name** | Terminate Employee |
| **Actor(s)** | HR Manager (primary) |
| **Priority** | Critical |
| **Frequency** | As required; typically several times per month |
| **Implementing Package** | PKG_EMPLOYEE.terminate_employee |
| **Related Business Rules** | BR-40, BR-41, BR-42, BR-43, BR-73; BR-TERM-01 through BR-TERM-09 |

**Brief Description**  
The HR Manager records the termination of an employee, setting the termination date, reason, and updating employment status. Multiple downstream steps (COBRA, final pay, access revocation) have critical implementation gaps.

**Preconditions**
1. HR Manager is authenticated with Grade ≥ 8.
2. Employee exists with EMPLOYMENT_STATUS = 'ACTIVE'.
3. A valid TERMINATION_CODE exists for the reason (VOLUNTARY, INVOLUNTARY, RETIREMENT, etc.).
4. TERMINATION_DATE is not before HIRE_DATE.

**Main Flow**
1. HR Manager opens HRMS_EMPLOYEE form and locates the employee record.
2. HR Manager selects "Terminate Employee."
3. HR Manager enters TERMINATION_DATE, TERMINATION_CODE, and optional TERMINATION_NOTES.
4. System calls PKG_EMPLOYEE.terminate_employee which:
   a. Updates EMPLOYEES.EMPLOYMENT_STATUS = 'TERMINATED'.
   b. Sets EMPLOYEES.TERMINATION_DATE = p_termination_date.
   c. Sets EMPLOYEES.TERMINATION_REASON = p_termination_code.
   d. Cancels all PENDING leave requests (LEAVE_REQUESTS.STATUS = 'CANCELLED').
   e. Writes an EMPLOYEE_HISTORY row capturing the pre-termination state.
   f. Writes AUDIT_LOG entry.
5. System side-effect: PKG_SECURITY.authenticate will now refuse all future login attempts for this employee (checks EMPLOYMENT_STATUS = 'ACTIVE' — BR-73). New logins are blocked immediately after commit.
6. HR Manager is shown confirmation with effective termination date.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-005-A | Active session exists at time of termination | Session remains valid for up to 30 minutes (session timeout window — BR-72 gap); PKG_SECURITY.revoke_access referenced in code does not exist |
| AF-005-B | COBRA notification required | TODO comment only; no COBRA notification is generated; federal 14-day notification window begins but system takes no action — **critical compliance gap (PP-TERM-01)** |
| AF-005-C | Final pay required | PKG_PAYROLL.calculate_final_pay does not exist — all final pay must be calculated manually **outside the system (PP-TERM-03 critical)** |
| AF-005-D | Employee has active dependents | EMPLOYEE_DEPENDENTS records are NOT updated; terminated employee's dependents remain ACTIVE_FLAG = 'Y' and continue appearing in ADP benefits feed — **compliance gap (BR-DEP-09)** |
| AF-005-E | Employee has bank accounts | EMPLOYEE_BANK_ACCOUNTS records are NOT inactivated on termination |

**Postconditions**
1. EMPLOYEES.EMPLOYMENT_STATUS = 'TERMINATED'; TERMINATION_DATE populated.
2. All PENDING leave requests cancelled.
3. EMPLOYEE_HISTORY row created.
4. Future logins blocked by authentication check.
5. AUDIT_LOG entry created.
6. **Not postconditioned** (gaps): COBRA notification; final pay; access session revocation; dependent inactivation; bank account inactivation.

**Business Rules**
- BR-40: TERMINATION_DATE must be on or after HIRE_DATE.
- BR-41: A valid TERMINATION_CODE is mandatory.
- BR-42: Employee history must be preserved; hard delete is not permitted.
- BR-43: All PENDING leave requests must be cancelled on termination.
- BR-73: Authentication gate checks EMPLOYMENT_STATUS = 'ACTIVE' — blocks re-login immediately post-commit.
- BR-TERM-01: COBRA qualifying event occurs on every termination; 14-day notification rule applies.
- BR-TERM-06: Termination procedure does not touch USER_SESSIONS, USER_CREDENTIALS, EMPLOYEE_DEPENDENTS, or EMPLOYEE_BANK_ACCOUNTS.

---

### UC-006: Conduct Performance Review

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-006 |
| **Use Case Name** | Conduct Performance Review |
| **Actor(s)** | Direct Manager (primary); Employee (self-assessment); HR Manager (cycle management) |
| **Priority** | High |
| **Frequency** | Annually (or per REVIEW_CYCLES configuration) |
| **Implementing Package** | PKG_PERFORMANCE.create_review, submit_self_assessment, submit_manager_review, acknowledge_review |
| **Related Business Rules** | BR-50, BR-51, BR-52, BR-53, BR-54 |

**Brief Description**  
A performance review cycle is opened by HR, employees complete self-assessments, managers submit ratings, and employees acknowledge results. Calibration columns exist in the schema but no calibration workflow is implemented.

**Preconditions**
1. An active REVIEW_CYCLE exists with STATUS = 'OPEN'.
2. HR Manager has called PKG_PERFORMANCE.create_review for the employee/reviewer pair.
3. Employee has EMPLOYMENT_STATUS = 'ACTIVE'.
4. Reviewer (manager) is a different employee from the reviewee.

**Main Flow**
1. HR Manager opens a REVIEW_CYCLE (CREATE_CYCLE or annual batch via scheduler).
2. HR Manager creates individual PERFORMANCE_REVIEWS rows via PKG_PERFORMANCE.create_review for each employee; STATUS = 'NOT_STARTED'.
3. Employee receives notification to complete self-assessment.
4. Employee logs in and calls PKG_PERFORMANCE.submit_self_assessment:
   a. Enters free-text SELF_ASSESSMENT.
   b. Updates PERFORMANCE_REVIEWS.STATUS = 'SELF_REVIEW'.
5. Manager receives notification to complete manager review.
6. Manager calls PKG_PERFORMANCE.submit_manager_review:
   a. Enters OVERALL_RATING (1.0–5.0 range; raises ORA-20403 if out of range).
   b. System maps OVERALL_RATING to RATING_LABEL (Exceptional/Exceeds/Meets/Needs Improvement/Unsatisfactory).
   c. Enters MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN.
   d. Updates STATUS = 'COMPLETED'.
7. Employee receives notification to acknowledge review.
8. Employee calls PKG_PERFORMANCE.acknowledge_review:
   a. Optionally enters EMPLOYEE_COMMENTS.
   b. Sets EMPLOYEE_ACK_DATE = SYSDATE; STATUS = 'ACKNOWLEDGED'.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-006-A | OVERALL_RATING outside 1.0–5.0 | System raises ORA-20403; manager must re-enter a valid rating |
| AF-006-B | Calibration required by HR | CALIBRATED_RATING and CALIBRATION_NOTES columns exist in schema but NO procedure writes to them; no CALIBRATION status transition exists — **calibration workflow entirely unimplemented** |
| AF-006-C | Rating distribution report requested | PKG_REPORTING.get_rating_distribution reads OVERALL_RATING, not CALIBRATED_RATING — reports show pre-calibration ratings even if calibration were implemented |
| AF-006-D | Employee does not acknowledge within deadline | No deadline enforcement mechanism in current implementation; STATUS remains 'COMPLETED' indefinitely |

**Postconditions**
1. PERFORMANCE_REVIEWS.STATUS = 'ACKNOWLEDGED'.
2. OVERALL_RATING, RATING_LABEL, EMPLOYEE_ACK_DATE populated.
3. Review available for payroll merit eligibility check (OVERALL_RATING ≥ 3.0).
4. AUDIT_LOG entries at each status transition.

**Business Rules**
- BR-50: OVERALL_RATING must be between 1.0 and 5.0.
- BR-51: RATING_LABEL is system-derived from OVERALL_RATING thresholds (not user-entered).
- BR-52: Self-assessment must be submitted before manager review can be entered.
- BR-53: Employee must acknowledge before STATUS = 'ACKNOWLEDGED'.
- BR-54: CALIBRATED_RATING is a schema column with no implementing procedure — dead column in current codebase.

---

### UC-007: Update Salary

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-007 |
| **Use Case Name** | Update Salary |
| **Actor(s)** | HR Manager (primary) |
| **Priority** | High |
| **Frequency** | As required; promotion cycles, merit awards |
| **Implementing Package** | PKG_EMPLOYEE.update_salary (or direct SALARY_RECORDS insert) |
| **Related Business Rules** | BR-60, BR-61, BR-74 |

**Brief Description**  
The HR Manager records a salary change for an employee, creating a new SALARY_RECORDS row and closing the previous one. Salary-grade band validation is advisory only (known defect).

**Preconditions**
1. HR Manager is authenticated with Grade ≥ 8.
2. Employee exists with EMPLOYMENT_STATUS = 'ACTIVE'.
3. A current SALARY_RECORDS row exists (END_DATE = NULL).
4. New salary amount is > 0.

**Main Flow**
1. HR Manager opens HRMS_EMPLOYEE form, navigates to Compensation tab.
2. HR Manager enters new BASE_SALARY, EFFECTIVE_DATE, CHANGE_REASON, and APPROVED_BY.
3. System calls HRMS_VALIDATION_LIB.validate_salary_range to check new salary against JOB_GRADES.MIN_SALARY and MAX_SALARY for the employee's current grade.
4. If salary is outside grade band, system displays a warning MESSAGE — **does not block save** (BR-74 defect).
5. System closes the existing SALARY_RECORDS row: END_DATE = EFFECTIVE_DATE - 1.
6. System inserts new SALARY_RECORDS row with EFFECTIVE_DATE = p_effective_date, END_DATE = NULL.
7. System writes AUDIT_LOG entry capturing old salary, new salary, approver, and reason.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-007-A | New salary below JOB_GRADES.MIN_SALARY or above MAX_SALARY | Non-blocking warning message only; HR Manager can proceed with out-of-band salary |
| AF-007-B | EFFECTIVE_DATE is in the past | System allows backdated salary changes; no lock on closed pay periods from the salary update path |
| AF-007-C | EFFECTIVE_DATE is in the future | Future-dated salary records are permitted; calculate_payroll uses MAX(EFFECTIVE_DATE) ≤ PAY_PERIOD_END |

**Postconditions**
1. Previous SALARY_RECORDS row has END_DATE set.
2. New SALARY_RECORDS row has END_DATE = NULL.
3. AUDIT_LOG entry captures salary change event.

**Business Rules**
- BR-60: Only one SALARY_RECORDS row per employee may have END_DATE = NULL at any time.
- BR-61: Historical salary records must be preserved (no hard deletes).
- BR-74: Salary-grade band validation must be enforced as a blocking error — currently only a soft warning (defect requiring remediation before next audit).

---

### UC-008: Authenticate User

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-008 |
| **Use Case Name** | Authenticate User |
| **Actor(s)** | Any user (Employee, HR Manager, Payroll Admin, System Admin) |
| **Priority** | Critical |
| **Frequency** | Every system session |
| **Implementing Package** | PKG_SECURITY.authenticate, is_session_valid |
| **Related Business Rules** | BR-70, BR-71, BR-72, BR-73; BR-042 (critical defect) |

**Brief Description**  
A user provides credentials via the HRMS_LOGIN form or self-service portal to establish an authenticated session. A critical defect exists: the authentication procedure never verifies the password against stored credentials.

**Preconditions**
1. User has a valid EMAIL address in EMPLOYEES.
2. User's EMPLOYMENT_STATUS = 'ACTIVE'.
3. No existing ACTIVE session for the same employee (single concurrent session policy — implementation unconfirmed).

**Main Flow**
1. User opens HRMS_LOGIN form and enters EMAIL and PASSWORD.
2. System calls PKG_SECURITY.authenticate(p_email, p_password):
   a. Queries EMPLOYEES by EMAIL to retrieve EMP_ID and GRADE.
   b. Checks EMPLOYMENT_STATUS = 'ACTIVE'; raises ORA-20301 if not active.
   c. **CRITICAL DEFECT (BR-042):** Password is NEVER verified against USER_CREDENTIALS. Any string submitted as p_password succeeds if the email matches an active employee.
   d. Inserts row into USER_SESSIONS with STATUS = 'ACTIVE', LOGIN_TIME = SYSDATE.
   e. Returns SESSION_ID to caller.
3. System stores SESSION_ID in Oracle Forms global variable.
4. Subsequent API calls pass SESSION_ID to PKG_SECURITY.is_session_valid before processing.
5. is_session_valid checks LOGIN_TIME + INTERVAL '30' MINUTE >= SYSDATE; returns FALSE if expired.
6. Session is invalidated by PKG_SECURITY.logout or 30-minute inactivity timeout.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-008-A | EMAIL does not match any EMPLOYEES row | System raises ORA-20301 "Authentication failed" (same error as wrong password — timing attack possible; username enumeration via response time) |
| AF-008-B | Two ACTIVE employees share same EMAIL | System silently authenticates as the employee with the lowest EMP_ID (BR-043b); the other employee cannot authenticate |
| AF-008-C | Employee is TERMINATED | EMPLOYMENT_STATUS check fails; login rejected with ORA-20301 |
| AF-008-D | Session expires (30-minute timeout) | is_session_valid returns FALSE; caller must redirect to login; e_session_expired exception is declared but never raised (BR-045 defect) |
| AF-008-E | change_password called | Old password is never verified before replacement — any authenticated session can change any password (DQ-029 / BR-044 defect) |

**Postconditions**
1. USER_SESSIONS row with STATUS = 'ACTIVE' and SESSION_ID created.
2. SESSION_ID available to all subsequent PKG_* calls for authorisation.

**Business Rules**
- BR-70: All API calls must pass a valid SESSION_ID to is_session_valid before processing.
- BR-71: SESSION_ID must be a system-generated unique token.
- BR-72: Session timeout = 30 minutes from LOGIN_TIME (hard-coded; SYSTEM_PARAMETERS value is ignored).
- BR-73: EMPLOYMENT_STATUS = 'ACTIVE' is enforced at authentication time.
- BR-042 (CRITICAL DEFECT): Password is never verified — any valid email grants access regardless of password.
- BR-044: change_password never verifies old password before replacement.

**Open Issues**
- OI-008-1: BR-042 authentication bypass must be treated as a Priority 1 security defect. Immediate remediation required before any production deployment.
- OI-008-2: AES-256 key is hard-coded as `HR$ystem_3ncrypt10n_K3y_2024!!` in PKG_SECURITY (DQ-001/TD-01) — must be moved to Oracle Wallet before go-live.
- OI-008-3: Password hashing uses MD5 (DQ-010) — must be replaced with bcrypt or Argon2 before go-live.

---

### UC-009: Generate Reports

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-009 |
| **Use Case Name** | Generate Reports |
| **Actor(s)** | HR Manager / Payroll Administrator (primary) |
| **Priority** | High |
| **Frequency** | Daily to monthly depending on report type |
| **Implementing Package** | PKG_REPORTING (headcount_report, compensation_summary, turnover_report, new_hires_report, leave_utilization_report, payroll_summary_report, eeo_compliance_report) |
| **Related Business Rules** | BR-043, BR-044, BR-045 (RPT_* stub) |

**Brief Description**  
HR Managers and Payroll Administrators run on-demand reports against live OLTP data. Seven report procedures are available. A nightly reporting refresh (PKG_REPORTING.refresh_reporting_tables) exists as a stub only.

**Preconditions**
1. User is authenticated with Grade ≥ 5 (view-all) or Grade ≥ 8 for full access.
2. Report parameters (date ranges, department filters) are provided.
3. OLTP tables contain current data.

**Main Flow**
1. User opens HRMS_REPORTS form or Oracle Reports (.rdf) interface.
2. User selects a report type from the available list.
3. User enters applicable parameters (e.g., AS_OF_DATE for headcount; pay period for payroll summary).
4. System calls the corresponding PKG_REPORTING procedure which:
   a. Opens a REF CURSOR (t_report_cursor) against live OLTP tables.
   b. Joins EMPLOYEES, DEPARTMENTS, SALARY_RECORDS, etc. as required.
   c. Returns cursor to Oracle Reports / HRMS_REPORTS form for rendering.
5. Report is rendered and optionally exported to PDF or CSV via Oracle Reports.

**Available Reports**

| Report | Procedure | Key Data Sources | Notable Logic |
|--------|-----------|-----------------|---------------|
| Headcount | headcount_report | EMPLOYEES, DEPARTMENTS, LOCATIONS | FT/PT/CONTRACT/gender splits; avg tenure; AS_OF_DATE filter |
| Compensation Summary | compensation_summary | + JOB_TITLES, JOB_GRADES, SALARY_RECORDS | COMPA_RATIO = AVG(salary/grade_midpoint)×100; Oracle MEDIAN() aggregate |
| Turnover | turnover_report | EMPLOYEES, DEPARTMENTS | Non-standard denominator (hires-to-end-date, not avg headcount — BR-044); not SHRM-comparable |
| New Hires | new_hires_report | + JOB_TITLES, LOCATIONS, SALARY_RECORDS | Row-level; self-join for manager name |
| Leave Utilisation | leave_utilization_report | LEAVE_BALANCES, EMPLOYEES, DEPARTMENTS, LEAVE_TYPES | UTILIZATION_PCT = AVG(USED)×100 / AVG(OPENING+ACCRUED) |
| Payroll Summary | payroll_summary_report | PAYROLL_DETAILS, PAYROLL_RUNS | Magic numbers: ELEMENT_ID 100/101/102/103 undocumented |
| EEO Compliance | eeo_compliance_report | EMPLOYEES, JOB_TITLES | Groups by EEO_CATEGORY; includes NULL gender as NOT_DISCLOSED |

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-009-A | refresh_reporting_tables called (nightly scheduled job) | Stub only — logs "Reporting tables refreshed" but writes NO data to RPT_* tables; RPT_* tables may not contain data; reports always run against OLTP (BR-043) |
| AF-009-B | Compensation report on PostgreSQL/SQL Server (migration scenario) | Oracle MEDIAN() aggregate has no direct equivalent on target platforms (MC-02b) |
| AF-009-C | RPT_* tables queried directly | No PL/SQL access check at table level; RPT_NEW_HIRES exposes salary alongside PII — direct SELECT is unguarded |

**Postconditions**
1. REF CURSOR returned with report data.
2. No OLTP data modified by report generation.
3. Audit log entry for report execution (if configured).

---

### UC-010: Manage Benefits Enrollment

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-010 |
| **Use Case Name** | Manage Benefits Enrollment |
| **Actor(s)** | HR Manager (primary); Employee (self-service); ADP Benefits Provider (external) |
| **Priority** | Medium |
| **Frequency** | Annual open enrollment; ad-hoc life events |
| **Implementing Package** | PKG_INTEGRATION.export_benefits_feed |
| **Related Business Rules** | BR-DEP-03, BR-DEP-05, BR-DEP-09 |

**Brief Description**  
HR Managers enrol employees and their dependents in benefit plans. The benefits data is exported to ADP via a fixed-width feed file.

**Preconditions**
1. Employee exists with EMPLOYMENT_STATUS = 'ACTIVE'.
2. BENEFIT_PLANS records exist for available plans.
3. Employee and relevant dependents have active records (ACTIVE_FLAG = 'Y').

**Main Flow**
1. HR Manager opens benefits enrollment screen for the employee.
2. HR Manager selects BENEFIT_PLAN and TIER for the employee.
3. HR Manager adds eligible dependents from EMPLOYEE_DEPENDENTS (relationship validated against CHK_RELATIONSHIP constraint).
4. System inserts BENEFIT_ENROLLMENTS row with EFFECTIVE_DATE.
5. Dependents: EMPLOYEE_DEPENDENTS.BENEFITS_ENROLLED flag is available but is **never read** by export_benefits_feed (BR-DEP-05 gap).
6. On nightly schedule (or manual trigger), PKG_INTEGRATION.export_benefits_feed runs:
   a. Queries EMPLOYEES JOIN BENEFIT_ENROLLMENTS JOIN EMPLOYEE_DEPENDENTS (ACTIVE_FLAG = 'Y').
   b. Generates 203-character fixed-width ADP format records.
   c. Writes to BENEFITS_FEED_OUT Oracle directory as BENEFITS_YYYYMMDD.txt.
7. ADP processes the file and updates benefits coverage (external, not tracked by HRMS).

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-010-A | BENEFITS_ENROLLED = 'N' for a dependent | Dependent is still exported in the feed because the filter is ACTIVE_FLAG = 'Y' only; ADP may receive un-enrolled dependent records |
| AF-010-B | Dependent SSN required by ADP | SSN_ENCRYPTED exists on EMPLOYEE_DEPENDENTS but no decrypt procedure is available for dependent SSNs; ADP feed exports name, relationship, DOB only |
| AF-010-C | Employee terminated | Dependents remain ACTIVE_FLAG = 'Y'; they continue appearing in the ADP feed after termination (BR-DEP-09 gap) |
| AF-010-D | ADP format version changes | No file version header; no record count trailer; no checksum in export file (TD-73 gap) |

**Postconditions**
1. BENEFIT_ENROLLMENTS rows created for employee and selected plans.
2. Benefits feed file written to BENEFITS_FEED_OUT directory.
3. ADP provider receives coverage data.

---

### UC-011: Rehire Employee

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-011 |
| **Use Case Name** | Rehire Employee |
| **Actor(s)** | HR Manager (primary) |
| **Priority** | Medium |
| **Frequency** | Infrequent |
| **Implementing Package** | PKG_EMPLOYEE.rehire_employee |
| **Related Business Rules** | BR-05, BR-06, BR-07 |

**Brief Description**  
An HR Manager reinstates a previously terminated employee, restoring their ACTIVE status and resetting leave balances.

**Preconditions**
1. HR Manager is authenticated with Grade ≥ 8.
2. Employee exists with EMPLOYMENT_STATUS = 'TERMINATED'.
3. A new HIRE_DATE (rehire date) is provided.

**Main Flow**
1. HR Manager locates the terminated employee record in HRMS_EMPLOYEE.
2. HR Manager selects "Rehire Employee."
3. HR Manager enters new HIRE_DATE (rehire date), new JOB_TITLE, DEPARTMENT_ID, GRADE, BASE_SALARY.
4. System calls PKG_EMPLOYEE.rehire_employee:
   a. Updates EMPLOYEES.EMPLOYMENT_STATUS = 'ACTIVE'.
   b. Clears EMPLOYEES.TERMINATION_DATE and TERMINATION_REASON.
   c. Inserts new SALARY_RECORDS row with new EFFECTIVE_DATE.
   d. Calls PKG_LEAVE.initialize_balances to create fresh LEAVE_BALANCES rows.
   e. Writes EMPLOYEE_HISTORY row recording the rehire event.
   f. Writes AUDIT_LOG entry.
5. System confirms rehire with updated employee summary.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-011-A | Employee is ACTIVE (not terminated) | System raises error; cannot rehire an active employee |
| AF-011-B | Previous leave balances exist | PKG_LEAVE.initialize_balances creates new rows; whether previous balance history is retained or zeroed depends on initialise logic |
| AF-011-C | Bank account records exist from prior employment | EMPLOYEE_BANK_ACCOUNTS rows remain from previous tenure; HR Manager should review and update |

**Postconditions**
1. EMPLOYEES.EMPLOYMENT_STATUS = 'ACTIVE'; TERMINATION_DATE cleared.
2. New SALARY_RECORDS row with new effective date.
3. Fresh LEAVE_BALANCES rows created.
4. EMPLOYEE_HISTORY records the rehire event.

---

### UC-012: Process Deductions

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-012 |
| **Use Case Name** | Process Deductions |
| **Actor(s)** | Payroll Administrator (primary) |
| **Priority** | High |
| **Frequency** | Monthly, aligned with payroll run |
| **Implementing Package** | PKG_PAYROLL (deduction calculation within calculate_employee_pay) |
| **Related Business Rules** | BR-17, BR-18, BR-20, BR-21 |

**Brief Description**  
The Payroll Administrator configures and applies pre-tax and post-tax deductions for each employee, including benefits premiums, retirement contributions, and garnishments. Deductions are applied automatically during payroll calculation.

**Preconditions**
1. Payroll Administrator is authenticated.
2. DEDUCTION_RECORDS exist for affected employees with appropriate DEDUCTION_TYPE and AMOUNT/PERCENTAGE.
3. A PAYROLL_RUN exists with STATUS = 'DRAFT'.

**Main Flow**
1. Payroll Administrator reviews DEDUCTION_RECORDS for the upcoming period.
2. Payroll Administrator adds, modifies, or inactivates deduction rows as required.
3. During PKG_PAYROLL.calculate_payroll (see UC-002), calculate_employee_pay:
   a. Retrieves all active DEDUCTION_RECORDS for each employee.
   b. Applies pre-tax deductions (retirement, FSA) before tax calculation.
   c. Applies post-tax deductions (garnishments, voluntary deductions) after tax.
   d. Inserts PAYROLL_DETAILS rows for each deduction element (ELEMENT_ID 100–103).
   e. Accumulates total deductions into PAYROLL_RUNS.TOTAL_DEDUCTIONS.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-012-A | Deduction exceeds net pay | No minimum net pay protection logic confirmed; could result in negative net pay |
| AF-012-B | ELEMENT_ID assignment for new deduction type | GL account coding scheme (5100/2100/2200) is undocumented; incorrect ELEMENT_ID assignment causes GL misposting (TD-57) |

**Postconditions**
1. PAYROLL_DETAILS rows created for all deduction elements.
2. PAYROLL_RUNS.TOTAL_DEDUCTIONS updated.
3. NET_PAY = GROSS_PAY - TOTAL_DEDUCTIONS - TOTAL_TAXES.

---

### UC-013: Manage Job Positions

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-013 |
| **Use Case Name** | Manage Job Positions |
| **Actor(s)** | HR Manager / System Administrator (primary) |
| **Priority** | Medium |
| **Frequency** | As required; typically during reorganisations |
| **Implementing Package** | Direct DML on JOB_POSITIONS; HRMS_EMPLOYEE form LOV management |
| **Related Business Rules** | BR-12, BR-13, BR-74; TD-72 |

**Brief Description**  
HR Managers or System Administrators create, modify, and retire job positions within the organisational structure, including grade ranges and department assignments.

**Preconditions**
1. Actor is authenticated with Grade ≥ 8.
2. Relevant DEPARTMENTS record exists (if assigning to a department).
3. JOB_GRADES record exists for the target grade range.

**Main Flow**
1. HR Manager opens the Job Position maintenance screen.
2. HR Manager enters POSITION_TITLE, POSITION_CODE, MIN_GRADE, MAX_GRADE, optional DEPARTMENT_ID.
3. System validates POSITION_CODE is unique.
4. System validates MIN_GRADE ≤ MAX_GRADE.
5. System inserts JOB_POSITIONS row with ACTIVE_FLAG = 'Y'.
6. New position becomes available in LOV_POSITIONS for employee assignment.

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-013-A | Retiring a position with active employees assigned | ACTIVE_FLAG = 'N' prevents new hires to the position but does not enforce migration of existing employees — HR must manually reassign |
| AF-013-B | LOV_MANAGERS selection | LOV_MANAGERS in HRMS_EMPLOYEE.xml includes all active employees regardless of grade — an Intern can be set as manager for a VP (TD-72 defect); no minimum grade check exists |

**Postconditions**
1. JOB_POSITIONS row created or updated.
2. Position available in employee assignment LOVs.

---

### UC-014: Run Payroll Audit

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-014 |
| **Use Case Name** | Run Payroll Audit |
| **Actor(s)** | Payroll Administrator / HR Manager (primary) |
| **Priority** | High |
| **Frequency** | After each payroll run; pre-approval |
| **Implementing Package** | PKG_REPORTING.payroll_summary_report; AUDIT_LOG queries |
| **Related Business Rules** | BR-043 (RPT_* stub); TD-80 (no GL feed status) |

**Brief Description**  
The Payroll Administrator reviews the payroll run for accuracy before approval, comparing gross pay totals, deductions, tax withholdings, and identifying anomalies.

**Preconditions**
1. A PAYROLL_RUN with STATUS = 'CALCULATED' exists.
2. Payroll Administrator is authenticated with appropriate Grade.

**Main Flow**
1. Payroll Administrator runs PKG_REPORTING.payroll_summary_report for the calculated run.
2. Report returns aggregated view by department and element type (using ELEMENT_ID 100–103).
3. Payroll Administrator reviews:
   a. Gross pay totals against expected headcount × average salary.
   b. Tax withholdings for reasonableness.
   c. Deduction totals.
   d. Any STATUS = 'ERROR' rows in PAYROLL_DETAILS (excluded from totals).
4. Payroll Administrator queries AUDIT_LOG for any exceptions raised during calculation.
5. If anomalies found: Payroll Administrator investigates individual PAYROLL_DETAILS rows.
6. Once satisfied, Payroll Administrator proceeds to approval (UC-002 step 8).

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-014-A | ERROR rows found in PAYROLL_DETAILS | Payroll summary excludes ERROR rows from totals; admin must resolve and re-calculate affected employees or accept the run with exceptions |
| AF-014-B | GL feed status check | No GL_FEED_STATUS field on PAYROLL_RUNS; no way to confirm which prior runs were successfully imported into Oracle Financials (TD-80 gap) |
| AF-014-C | HEAD_OF_HOUSEHOLD employees | Federal tax = $0 for these employees; will appear as anomaly in audit; currently no automated flag |

**Postconditions**
1. Payroll anomalies documented (manual process — no workflow tracking).
2. Payroll Administrator proceeds to approve or investigate further.

---

### UC-015: Manage Leave Types

| Field | Detail |
|-------|--------|
| **Use Case ID** | UC-015 |
| **Use Case Name** | Manage Leave Types |
| **Actor(s)** | System Administrator / HR Manager (primary) |
| **Priority** | Medium |
| **Frequency** | Infrequent; typically annually during policy review |
| **Implementing Package** | Direct DML on LEAVE_TYPES; PKG_LEAVE.initialize_balances (consumers) |
| **Related Business Rules** | BR-LIB-01 through BR-LIB-10; TD-71 (FMLA documentation flag) |

**Brief Description**  
System Administrators configure available leave types including accrual rates, carry-over rules, documentation requirements, and eligibility criteria. Leave types drive balance initialisation and accrual.

**Preconditions**
1. System Administrator is authenticated with Grade ≥ 8.
2. No conflicting leave type with the same code exists.

**Main Flow**
1. System Administrator opens leave type configuration screen.
2. System Administrator enters LEAVE_TYPE_CODE, LEAVE_TYPE_NAME, ACCRUAL_RATE, MAX_CARRY_OVER, REQUIRES_DOCUMENT, ACTIVE_FLAG.
3. System inserts LEAVE_TYPES row.
4. New leave type is available for future PKG_LEAVE.initialize_balances calls (existing employees do not automatically receive balances — manual backfill required).

**Alternate Flows**

| Flow ID | Trigger | Behaviour |
|---------|---------|-----------|
| AF-015-A | Modifying ACCRUAL_RATE on existing type | Existing LEAVE_BALANCES rows are NOT retroactively updated; change applies to next accrual cycle only |
| AF-015-B | Setting REQUIRES_DOCUMENT = 'Y' for FMLA | Current seed data has REQUIRES_DOCUMENT = 'N' for FMLA; PKG_LEAVE.submit_leave_request does not enforce document upload even if flag is 'Y' (TD-71 defect) |
| AF-015-C | Deactivating a leave type with pending requests | LEAVE_REQUESTS with STATUS = 'PENDING' referencing the leave type remain; no cascade update |
| AF-015-D | Monthly accrual run | DBMS_SCHEDULER calls PKG_LEAVE.run_monthly_accrual; defect BR-LIB-05 — accrual retry block uses assignment (=) instead of increment (+=) which would silently overwrite existing accrual if retry condition fires |

**Postconditions**
1. LEAVE_TYPES row created or updated.
2. ACTIVE_FLAG controls availability in leave request LOVs.
3. New employees hired after this change will receive balances for the new type on initialise_balances.

**Business Rules**
- BR-LIB-05 (DEFECT): run_monthly_accrual retry uses SET ACCRUED = v_accrued instead of SET ACCRUED = ACCRUED + v_accrued — silently destructive on concurrent retry.
- TD-71: FMLA REQUIRES_DOCUMENT seeded as 'N'; documentation requirement is unenforced.

---

## 4. Use Case Dependency Diagram

The following ASCII diagram shows which use cases must be completed or have preconditions that depend on other use cases.

```
SYSTEM FOUNDATION
══════════════════════════════════════════════════════════════════════════
UC-008: Authenticate User
  │
  ├── [required by ALL use cases — session must be valid before any action]
  │
  └── UC-013: Manage Job Positions
        │
        └── [position catalogue required before hiring]

EMPLOYEE LIFECYCLE
══════════════════════════════════════════════════════════════════════════
UC-001: Hire Employee ─────────────────────────────────────────┐
  │                                                             │
  ├── initialises LEAVE_BALANCES ──────────────────────────────┼──► UC-003: Submit Leave Request
  │                                                             │         │
  │                                                             │         └──► UC-004: Approve Leave Request
  │                                                             │
  ├── creates SALARY_RECORDS ──────────────────────────────────┼──► UC-002: Process Monthly Payroll
  │                                                             │         │
  ├── requires JOB_POSITIONS (UC-013) ─────────────────────────┘         ├──► UC-012: Process Deductions
  │                                                                        │
  │                                                                        └──► UC-014: Run Payroll Audit
  │
  ├──► UC-007: Update Salary ────────────────────────────────────────────► UC-002 (new salary on next run)
  │
  ├──► UC-006: Conduct Performance Review
  │         │
  │         └── OVERALL_RATING ≥ 3.0 ────────────────────────────────────► UC-002 merit eligibility gate
  │
  ├──► UC-010: Manage Benefits Enrollment ──────────────────────────────── ADP external feed
  │
  └──► UC-005: Terminate Employee
            │
            ├── cancels pending LEAVE_REQUESTS (UC-003/UC-004 flows closed)
            ├── blocks authentication (UC-008 — EMPLOYMENT_STATUS gate)
            ├── [GAP: no COBRA trigger — federal compliance risk]
            ├── [GAP: no final pay — UC-002 final pay unavailable]
            └──► UC-011: Rehire Employee (if employee reinstated later)

CONFIGURATION & ADMINISTRATION
══════════════════════════════════════════════════════════════════════════
UC-015: Manage Leave Types
  │
  └── initialises balances via UC-001 (hire) and PKG_LEAVE.initialize_balances

UC-013: Manage Job Positions
  │
  └── provides position catalogue for UC-001, UC-011, UC-007

REPORTING
══════════════════════════════════════════════════════════════════════════
UC-009: Generate Reports
  │
  ├── reads PAYROLL_RUNS/DETAILS (depends on UC-002)
  ├── reads LEAVE_BALANCES (depends on UC-003, UC-004)
  ├── reads PERFORMANCE_REVIEWS (depends on UC-006)
  └── reads EMPLOYEES/SALARY_RECORDS (depends on UC-001, UC-007, UC-005)

UC-014: Run Payroll Audit
  │
  └── depends on UC-002 (PAYROLL_RUN STATUS = 'CALCULATED')
```

**Dependency Summary Table**

| Use Case | Depends On (must exist first) | Enables (unlocked by this UC) |
|----------|-------------------------------|-------------------------------|
| UC-001 | UC-008, UC-013 | UC-002, UC-003, UC-004, UC-005, UC-006, UC-007, UC-010, UC-011 |
| UC-002 | UC-001, UC-008, UC-012 | UC-014, UC-009 (payroll reports) |
| UC-003 | UC-001, UC-008, UC-015 | UC-004 |
| UC-004 | UC-003, UC-008 | — |
| UC-005 | UC-001, UC-008 | UC-011 |
| UC-006 | UC-001, UC-008 | UC-002 (merit gate) |
| UC-007 | UC-001, UC-008 | UC-002 (updated salary on next run) |
| UC-008 | — (foundation) | All other use cases |
| UC-009 | UC-002, UC-001, UC-006 | — |
| UC-010 | UC-001, UC-008 | ADP benefits feed |
| UC-011 | UC-005, UC-008 | UC-001 lifecycle restart |
| UC-012 | UC-001, UC-008 | UC-002 |
| UC-013 | UC-008 | UC-001 |
| UC-014 | UC-002, UC-008 | UC-002 approval decision |
| UC-015 | UC-008 | UC-001 (leave balance initialisation), UC-003 |

---

## 5. Business Rule Cross-Reference

The following table maps critical business rules (from BA_Deep_Analyst.md) to the use cases that enforce, violate, or are affected by them.

| Rule ID | Rule Summary | Enforced In | Gap / Defect? |
|---------|-------------|-------------|---------------|
| BR-001 | EMPLOYEE_NUMBER must be unique and system-generated | UC-001 | No |
| BR-002 | SSN encrypted at rest (AES-256) | UC-001 | Yes — key hard-coded (DQ-001) |
| BR-003 | EMAIL unique across EMPLOYEES | UC-001, UC-008 | Yes — duplicate EMAIL causes silent auth as lowest EMP_ID (BR-043b) |
| BR-019 | HEAD_OF_HOUSEHOLD produces $0 federal tax | UC-002 | Yes — critical calculation defect |
| BR-042 | authenticate() never verifies password | UC-008 | Yes — CRITICAL security defect |
| BR-043 | refresh_reporting_tables is a stub | UC-009 | Yes — RPT_* tables never populated |
| BR-044 | change_password never verifies old password | UC-008 | Yes — security defect |
| BR-045 | e_session_expired never raised | UC-008 | Yes — exception handlers dead |
| BR-072 | Session timeout = 30 minutes (hard-coded) | UC-008 | Yes — SYSTEM_PARAMETERS ignored |
| BR-073 | Authentication checks EMPLOYMENT_STATUS = ACTIVE | UC-005, UC-008 | No — working as designed |
| BR-074 | Salary-grade band is soft warning, not blocking | UC-007 | Yes — should be blocking |
| BR-DEP-05 | BENEFITS_ENROLLED never read by benefits feed | UC-010 | Yes — un-enrolled dependents exported |
| BR-DEP-09 | Termination does not inactivate dependents | UC-005 | Yes — COBRA and feed exposure |
| BR-LIB-05 | Accrual retry uses assignment not increment | UC-015 | Yes — potential data corruption |
| BR-TERM-01 | COBRA notification gap on every termination | UC-005 | Yes — federal compliance risk |
| BR-TERM-06 | Final pay procedure does not exist | UC-005, UC-002 | Yes — critical operational gap |
| BR-BA-01 | Direct deposit non-functional | UC-002 | Yes — EMPLOYEE_BANK_ACCOUNTS never read |
| BR-ORG-02 | sync_org_structure logs false success | — | Yes — stub masquerades as completed |

---

*End of Use Case Specification — 03_USE_CASE_SPECIFICATION.md*  
*Document prepared by Business Analysis Team | Acme HRMS Reverse Engineering Pipeline | 2026-08-05*
