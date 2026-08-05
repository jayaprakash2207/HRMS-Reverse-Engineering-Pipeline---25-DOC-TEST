# Acme Corporation HRMS — Traceability Matrix

**System:** Acme Corporation HRMS (Oracle 19c / Oracle Forms 12c)
**Document Version:** 1.0
**Scope:** Full system — 140 Business Rules, 30+ confirmed tables, 9 PL/SQL packages, 6 Oracle Forms modules
**Status:** Living document — gaps flagged with [GAP] where source-to-target traceability cannot be fully confirmed from recovered artefacts

---

## Table of Contents

1. [Business Requirement → Source Code Traceability](#1-business-requirement--source-code-traceability)
2. [Business Rule → Database Constraint Traceability](#2-business-rule--database-constraint-traceability)
3. [Use Case → API Endpoint Traceability](#3-use-case--api-endpoint-traceability)
4. [Oracle HRMS Component → New System Component Mapping](#4-oracle-hrms-component--new-system-component-mapping)
5. [Data Table → Bounded Context Traceability](#5-data-table--bounded-context-traceability)
6. [Gap → Remediation Traceability](#6-gap--remediation-traceability)

---

## 1. Business Requirement → Source Code Traceability

This section maps each confirmed business requirement to the PL/SQL package, procedure, or function that implements it. Requirements with no code implementation are flagged [NOT IMPLEMENTED].

### 1.1 Employee Lifecycle Requirements

| Req ID | Business Requirement | Package | Procedure / Function | Implementation Notes |
|--------|---------------------|---------|---------------------|----------------------|
| BR-01 | Employee must be created with a unique employee number | PKG_EMPLOYEE | `create_employee` | Enforces UNIQUE constraint on EMPLOYEE_NUMBER; raises -20001 on duplicate |
| BR-02 | Employee grade must be between 1 and 10 | PKG_EMPLOYEE | `create_employee`, `promote_employee` | CHECK constraint on EMPLOYEES.GRADE; also validated in procedure body |
| BR-03 | Hire date cannot be in the future | PKG_EMPLOYEE | `create_employee` | Date comparison against SYSDATE at insert time |
| BR-04 | Employee status transitions must follow defined lifecycle | PKG_EMPLOYEE | `terminate_employee`, `put_on_leave` | EMPLOYMENT_STATUS CHK constraint + procedure guards |
| BR-05 | Termination requires a valid termination code | PKG_EMPLOYEE | `terminate_employee` | FK to TERMINATION_CODES; raises error on invalid code |
| BR-06 | Manager ID must reference an existing active employee | PKG_EMPLOYEE | `create_employee`, `transfer_employee` | FK constraint on EMPLOYEES.MANAGER_ID self-reference |
| BR-07 | Employee history must be recorded on every status change | PKG_EMPLOYEE | `terminate_employee`, `transfer_employee` | INSERT to EMPLOYEE_HISTORY within each procedure |
| BR-08 | Department must exist and be active before employee assignment | PKG_EMPLOYEE | `create_employee`, `transfer_employee` | FK to DEPARTMENTS; ACTIVE_FLAG filter in validation |
| BR-09 | COBRA notification required within 14 days of termination | PKG_EMPLOYEE | `terminate_employee` | **[NOT IMPLEMENTED]** — TODO comment only; no code exists (PP-TERM-01) |
| BR-10 | Access must be revoked on termination | PKG_SECURITY | `authenticate` (side-effect) | Partial — new logins blocked because `EMPLOYMENT_STATUS='ACTIVE'` check in `authenticate`; in-flight sessions not invalidated |
| BR-11 | Final pay must be calculated on termination | PKG_PAYROLL | `calculate_final_pay` | **[NOT IMPLEMENTED]** — procedure does not exist (PP-TERM-03) |
| BR-12 | Salary must fall within the grade band for the employee's position | PKG_EMPLOYEE | `create_employee` (debug mode only) | Partially implemented — validation fires only when `g_debug_mode = TRUE`; soft warning via MESSAGE, not blocking error (TD-74) |
| BR-13 | Employee transfer must log previous department in history | PKG_EMPLOYEE | `transfer_employee` | INSERT to EMPLOYEE_HISTORY with CHANGE_TYPE='TRANSFER' |
| BR-TERM-01 | Termination date must be set before employee inactivation | PKG_EMPLOYEE | `terminate_employee` | SET TERMINATION_DATE = SYSDATE on first step |
| BR-TERM-02 | EMPLOYMENT_STATUS must be set to TERMINATED | PKG_EMPLOYEE | `terminate_employee` | UPDATE EMPLOYEES SET EMPLOYMENT_STATUS = 'TERMINATED' |
| BR-TERM-03 | Leave balances must be frozen on termination | PKG_EMPLOYEE | `terminate_employee` | Gap — LEAVE_BALANCES not touched by terminate_employee |
| BR-TERM-04 | Dependent records must be reviewed on termination | PKG_EMPLOYEE | `terminate_employee` | **[NOT IMPLEMENTED]** — EMPLOYEE_DEPENDENTS not referenced in terminate_employee |
| BR-TERM-05 | Bank account should be inactivated on termination | PKG_EMPLOYEE | `terminate_employee` | **[NOT IMPLEMENTED]** — EMPLOYEE_BANK_ACCOUNTS not referenced |
| BR-TERM-06 | Active sessions must be invalidated on termination | PKG_SECURITY | `revoke_access` | **[NOT IMPLEMENTED]** — `PKG_SECURITY.revoke_access` procedure does not exist |
| BR-TERM-07 | Termination must generate a payroll notification | PKG_NOTIFICATION | `send_notification` | Partial — notification queue entry created but final-pay calculation missing |

### 1.2 Payroll Requirements

| Req ID | Business Requirement | Package | Procedure / Function | Implementation Notes |
|--------|---------------------|---------|---------------------|----------------------|
| BR-20 | Payroll run must cover all active employees | PKG_PAYROLL | `calculate_payroll` | Cursor: `WHERE EMPLOYMENT_STATUS = 'ACTIVE'` |
| BR-21 | Monthly gross = annual salary / 12 | PKG_PAYROLL | `calculate_employee_pay` | Integer division confirmed; implemented inline |
| BR-22 | Federal income tax must be calculated using bracket table | PKG_PAYROLL | `calculate_employee_pay` | Reads TAX_BRACKETS table; bracket walk implemented |
| BR-23 | Head-of-household filers must receive correct tax calculation | PKG_PAYROLL | `calculate_employee_pay` | **DEFECT** — HOH branch returns $0 federal tax (critical bug) |
| BR-24 | State income tax must be applied as a flat rate by state | PKG_PAYROLL | `calculate_employee_pay` | Flat-rate lookup against STATE_TAX_RATES reference table |
| BR-25 | Social Security deduction = 6.2% up to wage base | PKG_PAYROLL | `calculate_employee_pay` | Hard-coded rate; wage base comparison implemented |
| BR-26 | Medicare deduction = 1.45% with no wage base cap | PKG_PAYROLL | `calculate_employee_pay` | Hard-coded rate |
| BR-27 | Net pay = gross minus all deductions | PKG_PAYROLL | `calculate_employee_pay` | Final subtraction; result written to PAYROLL_DETAILS |
| BR-28 | Payroll run status must advance through defined lifecycle | PKG_PAYROLL | `approve_payroll`, `generate_gl_journal` | DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED |
| BR-29 | GL journal must be generated per approved payroll run | PKG_INTEGRATION | `generate_gl_journal` | Pipe-delimited flat file to Oracle Financials; UTL_FILE write |
| BR-30 | Direct deposit must disburse net pay to employee bank accounts | PKG_PAYROLL | — | **[NOT IMPLEMENTED]** — EMPLOYEE_BANK_ACCOUNTS never read; net pay orphaned at PAID status (PP-BA-01, DISC-009) |
| BR-31 | ACH prenote must be sent before first direct deposit | PKG_PAYROLL | — | **[NOT IMPLEMENTED]** — PRENOTE_SENT never set (PP-BA-03) |
| BR-32 | Pay elements must map to GL account codes | PKG_INTEGRATION | `generate_gl_journal` | Hard-coded element IDs 100/101/102/103 for GL routing |
| BR-33 | Payroll details must be inserted per employee per run | PKG_PAYROLL | `calculate_employee_pay` | INSERT to PAYROLL_DETAILS for each loop iteration |
| BR-34 | Performance rating ≥ 3 required for merit increase eligibility | PKG_PAYROLL | `calculate_employee_pay` | Conformist read of OVERALL_RATING from PERFORMANCE_REVIEWS |

### 1.3 Leave Management Requirements

| Req ID | Business Requirement | Package | Procedure / Function | Implementation Notes |
|--------|---------------------|---------|---------------------|----------------------|
| BR-40 | Leave request must reference a valid leave type | PKG_LEAVE | `submit_leave_request` | FK to LEAVE_TYPES; raises error on invalid type |
| BR-41 | Leave balance must be sufficient before approval | PKG_LEAVE | `approve_leave_request` | Balance check before UPDATE; raises -20201 if insufficient |
| BR-42 | Leave balance must be decremented on approval | PKG_LEAVE | `approve_leave_request` | UPDATE LEAVE_BALANCES SET USED = USED + days |
| BR-43 | Annual leave balances must be initialised at hire | PKG_LEAVE | `initialize_balances` | INSERT to LEAVE_BALANCES for each LEAVE_TYPE |
| BR-44 | Monthly accrual must increment leave balances | PKG_LEAVE | `run_monthly_accrual` | **DEFECT (BR-LIB-05)** — retry branch uses SET ACCRUED = v_accrued (assignment) not += (increment); silent destructive overwrite on retry |
| BR-45 | FMLA leave must require supporting documentation | PKG_LEAVE | `submit_leave_request` | **GAP** — FMLA seed data has REQUIRES_DOCUMENT='N' in reference data; no enforcement (TD-71) |
| BR-46 | Leave request cancellation must restore the balance | PKG_LEAVE | `cancel_leave_request` | UPDATE reverses USED decrement if previously approved |
| BR-47 | Leave type carryover rules must be applied at year-end | PKG_LEAVE | `process_year_end` | Carryover cap logic per LEAVE_TYPES.MAX_CARRYOVER |
| BR-48 | Sick leave cannot be carried over beyond one year | PKG_LEAVE | `process_year_end` | LEAVE_TYPES.CARRYOVER_ALLOWED flag check |
| BR-49 | Leave balances for terminated employees must be handled on termination | PKG_EMPLOYEE | `terminate_employee` | **[NOT IMPLEMENTED]** — LEAVE_BALANCES not updated on termination |

### 1.4 Performance Management Requirements

| Req ID | Business Requirement | Package | Procedure / Function | Implementation Notes |
|--------|---------------------|---------|---------------------|----------------------|
| BR-60 | Review cycle must be created before reviews are opened | PKG_PERFORMANCE | `create_review_cycle` | INSERT to REVIEW_CYCLES; START_DATE / END_DATE validation |
| BR-61 | Each employee must have exactly one active review per cycle | PKG_PERFORMANCE | `create_review` | Unique constraint on (CYCLE_ID, EMP_ID) in PERFORMANCE_REVIEWS |
| BR-62 | Self-assessment must be submitted before manager review | PKG_PERFORMANCE | `submit_manager_review` | STATUS check: raises error if SELF_REVIEW not completed |
| BR-63 | Manager review must include overall rating 1.0–5.0 | PKG_PERFORMANCE | `submit_manager_review` | Range validation: OVERALL_RATING BETWEEN 1.0 AND 5.0; raises -20403 |
| BR-64 | Rating label must be assigned based on overall rating | PKG_PERFORMANCE | `submit_manager_review` | Inline CASE: Exceptional ≥4.5, Exceeds ≥3.5, Meets ≥2.5, Needs ≥1.5, Unsatisfactory <1.5 |
| BR-65 | Employee must acknowledge review before cycle closes | PKG_PERFORMANCE | `acknowledge_review` | STATUS transition to ACKNOWLEDGED; records ACK_DATE |
| BR-66 | Calibration must be applied before official rating is locked | PKG_PERFORMANCE | — | **[NOT IMPLEMENTED]** — CALIBRATED_RATING column exists but is never written; no calibration status; no calibration procedure |
| BR-67 | Rating distribution report must use calibrated rating | PKG_PERFORMANCE | `get_rating_distribution` | **DEFECT** — query aggregates on OVERALL_RATING, not CALIBRATED_RATING; pre-calibration values reported as final |
| BR-68 | Goal completion must be tracked against performance goals | PKG_PERFORMANCE | `update_goal_progress` | UPDATE PERFORMANCE_GOALS.COMPLETION_PCT |
| BR-69 | 360-degree review must allow peer feedback | PKG_PERFORMANCE | — | **[NOT IMPLEMENTED]** — no peer reviewer role or multi-reviewer flow in any procedure |

### 1.5 Security and Access Requirements

| Req ID | Business Requirement | Package | Procedure / Function | Implementation Notes |
|--------|---------------------|---------|---------------------|----------------------|
| BR-70 | Authentication must verify employee credentials | PKG_SECURITY | `authenticate` | **CRITICAL DEFECT (BR-042)** — password is never verified; any valid username authenticates regardless of password |
| BR-71 | Session must expire after 30 minutes of inactivity | PKG_SECURITY | `is_session_valid` | Hard-coded INTERVAL '30' MINUTE; SYSTEM_PARAMETERS timeout ignored (DQ-027) |
| BR-72 | Failed logins must trigger account lockout | PKG_SECURITY | `authenticate` | **[NOT IMPLEMENTED]** — no LOGIN_ATTEMPTS counter; no lockout threshold |
| BR-73 | Terminated employees must not be able to authenticate | PKG_SECURITY | `authenticate` | Enforced: SELECT WHERE EMPLOYMENT_STATUS = 'ACTIVE' |
| BR-74 | Password complexity must be enforced on change | PKG_SECURITY | `change_password` | Min 8 chars, ≥1 uppercase, ≥1 digit — enforced in procedure only; no DDL constraint |
| BR-75 | Old password must be verified before password change | PKG_SECURITY | `change_password` | **DEFECT (BR-044/DQ-029)** — p_old_password received but never compared; any session can silently change any password |
| BR-76 | Grade-based RBAC must control data access | PKG_SECURITY | `has_permission` | Grade ≥ 8: full access; 5–7: view all; <5: own records only |
| BR-77 | PII must be encrypted at rest | PKG_SECURITY | `encrypt_value`, `decrypt_value` | AES-256 via DBMS_CRYPTO; key hard-coded as `HR$ystem_3ncrypt10n_K3y_2024!!` (DQ-001/SEC-03) |
| BR-78 | Audit log must record all sensitive data access | PKG_COMMON | `log_action`, `log_error` | Writes to AUDIT_LOG; mixed ERROR/INFO/DML in single table (TD-37) |
| BR-79 | Portal DB connection must use least-privilege credentials | PKG_SECURITY | — | **[NOT IMPLEMENTED]** — no dedicated portal DB user; no EXECUTE-only grants in source (TD-81) |

### 1.6 Integration Requirements

| Req ID | Business Requirement | Package | Procedure / Function | Implementation Notes |
|--------|---------------------|---------|---------------------|----------------------|
| BR-90 | Benefits data must be exported to ADP in fixed-width format | PKG_INTEGRATION | `export_benefits_feed` | 203-character fixed-width; UTL_FILE write to BENEFITS_FEED_OUT |
| BR-91 | Org structure must be synchronised with LDAP/AD | PKG_INTEGRATION | `sync_org_structure` | **[NOT IMPLEMENTED]** — stub only; logs false success 'Org structure sync completed' (BR-ORG-01/02) |
| BR-92 | Time and attendance data must be imported from CSV | PKG_INTEGRATION | `import_time_attendance` | **STUB** — UTL_FILE read implemented with skip rules; no INSERT to destination table; no payroll link (DQ-031) |
| BR-93 | GL journal must be submitted to Oracle Financials | PKG_INTEGRATION | `generate_gl_journal` | Pipe-delimited flat file; no GL_FEED_SENT status tracking (TD-80) |
| BR-94 | Notification queue must process pending messages | PKG_NOTIFICATION | `process_queue` | Cursor over NOTIFICATION_QUEUE WHERE STATUS='PENDING'; dispatches by channel |
| BR-95 | Benefits feed must include only active enrolled dependents | PKG_INTEGRATION | `export_benefits_feed` | Filters `d.ACTIVE_FLAG = 'Y'` but **does not** filter `BENEFITS_ENROLLED = 'Y'` — gap (BR-DEP-05) |
| BR-96 | Reporting tables must be refreshed nightly | PKG_REPORTING | `refresh_reporting_tables` | **[NOT IMPLEMENTED]** — stub; only logs 'Reporting tables refreshed'; no DML (BR-043) |

---

## 2. Business Rule → Database Constraint Traceability

This section maps business rules to the schema-level constraints that enforce them. Where a rule is enforced only in application code with no DDL constraint backup, this is noted as an enforcement gap.

### 2.1 Primary Key Constraints

| Business Rule | Constraint Name | Table | Column(s) | Enforcement Level |
|--------------|----------------|-------|-----------|------------------|
| Each employee has one master record | PK_EMPLOYEES | EMPLOYEES | EMPLOYEE_ID | DDL — surrogate key, SQ_EMPLOYEE_ID sequence |
| Each department has one record | PK_DEPARTMENTS | DEPARTMENTS | DEPARTMENT_ID | DDL |
| Each payroll run has one header | PK_PAYROLL_RUNS | PAYROLL_RUNS | RUN_ID | DDL |
| Each leave request is unique | PK_LEAVE_REQUESTS | LEAVE_REQUESTS | REQUEST_ID | DDL |
| Each performance review is unique | PK_PERFORMANCE_REVIEWS | PERFORMANCE_REVIEWS | REVIEW_ID | DDL |
| Each dependent has one record | PK_EMP_DEPENDENTS | EMPLOYEE_DEPENDENTS | DEPENDENT_ID | DDL |
| Each bank account entry is unique | PK_BANK_ACCOUNTS | EMPLOYEE_BANK_ACCOUNTS | BANK_ACCT_ID | DDL |
| Each session is unique | PK_USER_SESSIONS | USER_SESSIONS | SESSION_ID | DDL |
| Each notification is unique | PK_NOTIFICATION_QUEUE | NOTIFICATION_QUEUE | NOTIFICATION_ID | DDL |

### 2.2 Unique Constraints

| Business Rule | Constraint Name | Table | Column(s) | Enforcement Level |
|--------------|----------------|-------|-----------|------------------|
| Employee number must be human-unique | UK_EMPLOYEE_NUMBER | EMPLOYEES | EMPLOYEE_NUMBER | DDL |
| Corporate email must be unique | UK_EMPLOYEE_EMAIL | EMPLOYEES | EMAIL | DDL — also relied upon by `authenticate()` lookup |
| Department name must be unique | UK_DEPT_NAME | DEPARTMENTS | DEPARTMENT_NAME | DDL |
| Department code must be unique | UK_DEPT_CODE | DEPARTMENTS | DEPARTMENT_CODE | DDL |
| Position code must be unique | UK_POSITION_CODE | JOB_POSITIONS | POSITION_CODE | DDL |
| One active review per employee per cycle | UK_REVIEW_CYCLE_EMP | PERFORMANCE_REVIEWS | (CYCLE_ID, EMP_ID) | DDL |

### 2.3 Foreign Key Constraints

| Business Rule | Constraint Name | Child Table | Column | Parent Table | Notes |
|--------------|----------------|------------|--------|-------------|-------|
| Employee must belong to valid department | FK_EMP_DEPT | EMPLOYEES | DEPARTMENT_ID | DEPARTMENTS | — |
| Employee manager must be an employee | FK_EMP_MANAGER | EMPLOYEES | MANAGER_ID | EMPLOYEES | Self-referencing |
| Termination reason must be a valid code | FK_EMP_TERM_CODE | EMPLOYEES | TERMINATION_REASON | TERMINATION_CODES | — |
| Salary record must link to an employee | FK_SAL_EMP | SALARY_RECORDS | EMPLOYEE_ID | EMPLOYEES | — |
| Payroll detail must link to a run | FK_PAY_DET_RUN | PAYROLL_DETAILS | RUN_ID | PAYROLL_RUNS | — |
| Leave request must link to an employee | FK_LEAVE_REQ_EMP | LEAVE_REQUESTS | EMP_ID | EMPLOYEES | — |
| Leave request must reference a valid type | FK_LEAVE_REQ_TYPE | LEAVE_REQUESTS | LEAVE_TYPE_ID | LEAVE_TYPES | — |
| Dependent must link to an employee | FK_DEP_EMP | EMPLOYEE_DEPENDENTS | EMP_ID | EMPLOYEES | — |
| Bank account must link to an employee | FK_BANK_EMP | EMPLOYEE_BANK_ACCOUNTS | EMP_ID | EMPLOYEES | — |
| Performance review must link to employee | FK_REVIEW_EMP | PERFORMANCE_REVIEWS | EMP_ID | EMPLOYEES | — |
| Review cycle must link to cycle header | FK_REVIEW_CYCLE | PERFORMANCE_REVIEWS | CYCLE_ID | REVIEW_CYCLES | — |
| Notification recipient must be an employee | FK_NOTIF_RECIPIENT | NOTIFICATION_QUEUE | RECIPIENT_ID | EMPLOYEES | — |
| Session must link to an employee | FK_SESSION_EMP | USER_SESSIONS | EMP_ID | EMPLOYEES | — |

### 2.4 Check Constraints

| Business Rule | Constraint Name | Table | Column | Valid Values | Enforcement Gap? |
|--------------|----------------|-------|--------|-------------|-----------------|
| Employment status must be a controlled value | CHK_EMP_STATUS | EMPLOYEES | EMPLOYMENT_STATUS | ACTIVE, TERMINATED, ON_LEAVE, SUSPENDED | No gap — DDL enforces |
| Tax filing status must be a controlled value | CHK_TAX_STATUS | EMPLOYEES | TAX_FILING_STATUS | SINGLE, MARRIED_FILING_JOINTLY, MARRIED_FILING_SEPARATELY, HEAD_OF_HOUSEHOLD | No gap — but HOH logic defect in PKG_PAYROLL |
| Active flag must be Y or N | CHK_ACTIVE_FLAG | EMPLOYEES | ACTIVE_FLAG | 'Y', 'N' | No gap |
| Dependent relationship must be controlled | CHK_RELATIONSHIP | EMPLOYEE_DEPENDENTS | RELATIONSHIP | SPOUSE, CHILD, PARENT, DOMESTIC_PARTNER, OTHER | No gap |
| Bank account type must be controlled | CHK_ACCT_TYPE | EMPLOYEE_BANK_ACCOUNTS | ACCOUNT_TYPE | CHECKING, SAVINGS | No gap |
| Bank deposit type must be controlled | CHK_DEPOSIT_TYPE | EMPLOYEE_BANK_ACCOUNTS | DEPOSIT_TYPE | FULL, PARTIAL_AMOUNT, PARTIAL_PERCENT, REMAINDER | No gap on type; **GAP** — no cross-column constraint for PARTIAL_AMOUNT/NULL (BR-BA-09) |
| Payroll run status must be controlled | CHK_RUN_STATUS | PAYROLL_RUNS | STATUS | DRAFT, CALCULATED, APPROVED, GL_GENERATED, COMPLETED | No gap |
| Leave request status must be controlled | CHK_LEAVE_STATUS | LEAVE_REQUESTS | STATUS | PENDING, APPROVED, REJECTED, CANCELLED | No gap |
| Performance review status must be controlled | CHK_REVIEW_STATUS | PERFORMANCE_REVIEWS | STATUS | NOT_STARTED, SELF_REVIEW, MANAGER_REVIEW, COMPLETED, ACKNOWLEDGED | Gap — no CALIBRATION status value exists despite calibration columns present |
| Gender code must be controlled | — | EMPLOYEES | GENDER | M, F, O | **GAP** — no CHECK constraint; arbitrary values accepted (TD-40) |
| Overall rating range 1.0–5.0 | — | PERFORMANCE_REVIEWS | OVERALL_RATING | 1.0 to 5.0 | **GAP** — enforced only in PKG_PERFORMANCE.submit_manager_review; no DDL constraint |
| Salary must match grade band | — | SALARY_RECORDS | BASE_SALARY | Per JOB_GRADES range | **GAP** — debug-mode only, soft warning (TD-74) |
| Deposit amounts must sum to 100% | — | EMPLOYEE_BANK_ACCOUNTS | DEPOSIT_PERCENTAGE | Distribution totalling | **GAP** — no totalling constraint; 80% or 120% distributions accepted (BR-BA-11) |

### 2.5 NOT NULL Constraints (Key Business Rules)

| Business Rule | Table | Column | Notes |
|--------------|-------|--------|-------|
| Employee must have a hire date | EMPLOYEES | HIRE_DATE | NN — core active-filter component |
| Employee must have a status | EMPLOYEES | EMPLOYMENT_STATUS | NN |
| Employee must have a grade | EMPLOYEES | GRADE | NN — RBAC driver |
| Salary record must have a base salary | SALARY_RECORDS | BASE_SALARY | NN |
| Leave balance must track accrued days | LEAVE_BALANCES | ACCRUED | NN |
| Benefits enrollment flag defaults N | EMPLOYEE_DEPENDENTS | BENEFITS_ENROLLED | NN, DEFAULT 'N' |
| Active flag defaults Y | EMPLOYEE_DEPENDENTS | ACTIVE_FLAG | NN, DEFAULT 'Y' |
| Routing number must be present | EMPLOYEE_BANK_ACCOUNTS | ROUTING_NUMBER | NN — but stored plaintext (TD-46) |
| Account number must be present | EMPLOYEE_BANK_ACCOUNTS | ACCOUNT_NUMBER_ENC | NN |

### 2.6 Application-Only Enforcement (No DDL Constraint Backup — Risk Items)

| Business Rule | Enforcing Package | Procedure | Risk | Recommendation |
|--------------|-----------------|-----------|------|----------------|
| Password complexity (min 8 chars, 1 upper, 1 digit) | PKG_SECURITY | `change_password` | Direct INSERT to USER_CREDENTIALS bypasses all checks | Add DDL constraint or trigger |
| Overall rating between 1.0 and 5.0 | PKG_PERFORMANCE | `submit_manager_review` | Direct INSERT bypasses range | Add CHECK constraint |
| Salary within grade band | PKG_EMPLOYEE | `create_employee` (debug only) | Every non-debug create bypasses check | Elevate to blocking DDL or trigger |
| One active salary record per employee | PKG_PAYROLL | Query logic | No unique partial index on (EMPLOYEE_ID, END_DATE IS NULL) | Add filtered unique index |
| Leave balance cannot go negative | PKG_LEAVE | `approve_leave_request` | Race condition possible; no database lock | Add CHECK (AVAILABLE >= 0) or BALANCE >= 0 |
| Deposit amounts must total 100% | None | None | No enforcement at any layer | Add trigger or application validation |

---

## 3. Use Case → API Endpoint Traceability

In the Oracle Forms / PL/SQL architecture, "API endpoints" are PL/SQL package procedures exposed to callers (Oracle Forms, self-service portal, batch jobs). This section maps use cases to those callable procedure entry points.

### 3.1 Employee Management Use Cases

| Use Case ID | Use Case Name | Actor | PL/SQL Entry Point | Package | Oracle Forms Screen | Notes |
|------------|--------------|-------|--------------------|---------|---------------------|-------|
| UC-EMP-01 | Hire New Employee | HR Admin | `PKG_EMPLOYEE.create_employee` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | Returns new EMP_ID |
| UC-EMP-02 | View Employee Profile | All Grades | `PKG_EMPLOYEE.get_employee` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | Grade-RBAC applied via PKG_SECURITY.has_permission |
| UC-EMP-03 | Update Employee Details | HR Admin | `PKG_EMPLOYEE.update_employee` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | Audit trigger fires on UPDATE |
| UC-EMP-04 | Transfer Employee to New Department | HR Admin | `PKG_EMPLOYEE.transfer_employee` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | Writes EMPLOYEE_HISTORY |
| UC-EMP-05 | Promote Employee to New Grade | HR Admin | `PKG_EMPLOYEE.promote_employee` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | Grade range validation |
| UC-EMP-06 | Terminate Employee | HR Admin | `PKG_EMPLOYEE.terminate_employee` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | 13-step procedure; COBRA/final-pay/bank-account steps missing |
| UC-EMP-07 | Search Employee Directory | All Grades | `PKG_EMPLOYEE.search_employees` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | LOV-backed query |
| UC-EMP-08 | View Org Chart / Hierarchy | All Grades | `PKG_EMPLOYEE.get_org_chart` | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | CONNECT BY query; degrades >500 employees |
| UC-EMP-09 | Assign Reporting Manager | HR Admin | `PKG_EMPLOYEE.update_employee` (MANAGER_ID) | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | LOV_MANAGERS has no grade filter — intern can be selected as VP manager (TD-72) |

### 3.2 Payroll Use Cases

| Use Case ID | Use Case Name | Actor | PL/SQL Entry Point | Package | Oracle Forms Screen | Notes |
|------------|--------------|-------|--------------------|---------|---------------------|-------|
| UC-PAY-01 | Create Payroll Run | Payroll Admin | `PKG_PAYROLL.create_payroll_run` | PKG_PAYROLL | HRMS_PAYROLL.fmb | Creates PAYROLL_RUNS header in DRAFT status |
| UC-PAY-02 | Calculate Payroll for All Employees | Payroll Admin | `PKG_PAYROLL.calculate_payroll` | PKG_PAYROLL | HRMS_PAYROLL.fmb | Loops all ACTIVE employees; calls calculate_employee_pay |
| UC-PAY-03 | Review Payroll Calculation | Payroll Admin | `PKG_PAYROLL.get_payroll_summary` | PKG_PAYROLL | HRMS_PAYROLL.fmb | REF CURSOR over PAYROLL_DETAILS |
| UC-PAY-04 | Approve Payroll Run | HR Manager | `PKG_PAYROLL.approve_payroll` | PKG_PAYROLL | HRMS_PAYROLL.fmb | Status → APPROVED; records APPROVED_BY |
| UC-PAY-05 | Generate GL Journal File | Payroll Admin | `PKG_INTEGRATION.generate_gl_journal` | PKG_INTEGRATION | HRMS_PAYROLL.fmb | Pipe-delimited flat file; no sent-status tracking |
| UC-PAY-06 | View Employee Payslip | Employee (self) | `PKG_PAYROLL.get_employee_payslip` | PKG_PAYROLL | Self-service portal | Grade-RBAC: own records only for Grade <5 |
| UC-PAY-07 | Process Direct Deposit | Payroll System | — | — | — | **[NOT IMPLEMENTED]** — no procedure reads EMPLOYEE_BANK_ACCOUNTS |
| UC-PAY-08 | Calculate Final Pay on Termination | Payroll Admin | `PKG_PAYROLL.calculate_final_pay` | PKG_PAYROLL | — | **[NOT IMPLEMENTED]** — procedure does not exist |
| UC-PAY-09 | Recalculate Payroll for Corrections | Payroll Admin | `PKG_PAYROLL.recalculate_employee_pay` | PKG_PAYROLL | HRMS_PAYROLL.fmb | Re-runs calculate_employee_pay for a single employee |

### 3.3 Leave Management Use Cases

| Use Case ID | Use Case Name | Actor | PL/SQL Entry Point | Package | Oracle Forms Screen | Notes |
|------------|--------------|-------|--------------------|---------|---------------------|-------|
| UC-LV-01 | Submit Leave Request | Employee | `PKG_LEAVE.submit_leave_request` | PKG_LEAVE | Self-service portal | Validates leave type and balance; creates PENDING request |
| UC-LV-02 | Approve Leave Request | Manager | `PKG_LEAVE.approve_leave_request` | PKG_LEAVE | HRMS_LEAVE.fmb | Decrements LEAVE_BALANCES.USED |
| UC-LV-03 | Reject Leave Request | Manager | `PKG_LEAVE.reject_leave_request` | PKG_LEAVE | HRMS_LEAVE.fmb | Status → REJECTED; no balance change |
| UC-LV-04 | Cancel Leave Request | Employee | `PKG_LEAVE.cancel_leave_request` | PKG_LEAVE | Self-service portal | Reverses balance if previously APPROVED |
| UC-LV-05 | View Leave Balance | Employee | `PKG_LEAVE.get_leave_balance` | PKG_LEAVE | Self-service portal | REF CURSOR over LEAVE_BALANCES |
| UC-LV-06 | Initialise Balances at Hire | HR Admin / Batch | `PKG_LEAVE.initialize_balances` | PKG_LEAVE | Batch job | Creates one row per LEAVE_TYPE per new employee |
| UC-LV-07 | Run Monthly Accrual | Batch | `PKG_LEAVE.run_monthly_accrual` | PKG_LEAVE | DBMS_SCHEDULER job | Defect in retry path (BR-LIB-05) |
| UC-LV-08 | Process Year-End Carryover | Batch | `PKG_LEAVE.process_year_end` | PKG_LEAVE | DBMS_SCHEDULER job | Applies MAX_CARRYOVER cap; forfeits excess |
| UC-LV-09 | Submit FMLA Leave Request | Employee | `PKG_LEAVE.submit_leave_request` (FMLA type) | PKG_LEAVE | Self-service portal | FMLA documentation not enforced — REQUIRES_DOCUMENT='N' in seed data |

### 3.4 Performance Management Use Cases

| Use Case ID | Use Case Name | Actor | PL/SQL Entry Point | Package | Oracle Forms Screen | Notes |
|------------|--------------|-------|--------------------|---------|---------------------|-------|
| UC-PERF-01 | Create Review Cycle | HR Admin | `PKG_PERFORMANCE.create_review_cycle` | PKG_PERFORMANCE | HRMS_PERFORMANCE.fmb | Creates REVIEW_CYCLES header |
| UC-PERF-02 | Open Reviews for Cycle | HR Admin | `PKG_PERFORMANCE.create_review` | PKG_PERFORMANCE | HRMS_PERFORMANCE.fmb | Creates PERFORMANCE_REVIEWS rows for each employee |
| UC-PERF-03 | Submit Self-Assessment | Employee | `PKG_PERFORMANCE.submit_self_assessment` | PKG_PERFORMANCE | Self-service portal | Status → SELF_REVIEW |
| UC-PERF-04 | Submit Manager Review | Manager | `PKG_PERFORMANCE.submit_manager_review` | PKG_PERFORMANCE | HRMS_PERFORMANCE.fmb | Status → COMPLETED; writes OVERALL_RATING and RATING_LABEL |
| UC-PERF-05 | Acknowledge Review | Employee | `PKG_PERFORMANCE.acknowledge_review` | PKG_PERFORMANCE | Self-service portal | Status → ACKNOWLEDGED; records ACK_DATE |
| UC-PERF-06 | Run Calibration Session | HR Senior | — | — | — | **[NOT IMPLEMENTED]** — no procedure writes CALIBRATED_RATING |
| UC-PERF-07 | View Team Reviews | Manager | `PKG_PERFORMANCE.get_team_reviews` | PKG_PERFORMANCE | HRMS_PERFORMANCE.fmb | REF CURSOR filtered by reviewer_emp_id |
| UC-PERF-08 | View Rating Distribution | HR Admin | `PKG_PERFORMANCE.get_rating_distribution` | PKG_PERFORMANCE | HRMS_PERFORMANCE.fmb | Aggregates OVERALL_RATING — should use CALIBRATED_RATING |
| UC-PERF-09 | Set and Track Performance Goals | Employee / Manager | `PKG_PERFORMANCE.create_goal`, `update_goal_progress` | PKG_PERFORMANCE | Self-service portal | PERFORMANCE_GOALS / GOAL_REVIEWS tables |

### 3.5 Security and Session Use Cases

| Use Case ID | Use Case Name | Actor | PL/SQL Entry Point | Package | Notes |
|------------|--------------|-------|--------------------|---------|-------|
| UC-SEC-01 | Log In | All Users | `PKG_SECURITY.authenticate` | PKG_SECURITY | CRITICAL DEFECT — password never verified (BR-042) |
| UC-SEC-02 | Log Out | All Users | `PKG_SECURITY.logout` | PKG_SECURITY | Marks USER_SESSIONS.STATUS = 'LOGGED_OUT' |
| UC-SEC-03 | Validate Session | All Requests | `PKG_SECURITY.is_session_valid` | PKG_SECURITY | 30-minute hard-coded timeout |
| UC-SEC-04 | Change Password | Employee | `PKG_SECURITY.change_password` | PKG_SECURITY | Old password not verified — DQ-029 |
| UC-SEC-05 | Check Permission | All Requests | `PKG_SECURITY.has_permission` | PKG_SECURITY | Grade-based RBAC |
| UC-SEC-06 | Encrypt Sensitive Data | System | `PKG_SECURITY.encrypt_value` | PKG_SECURITY | AES-256; hard-coded key |
| UC-SEC-07 | Decrypt Sensitive Data | System | `PKG_SECURITY.decrypt_value` | PKG_SECURITY | No decrypt path exists for EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED |
| UC-SEC-08 | Revoke Access on Termination | HR Admin | `PKG_SECURITY.revoke_access` | PKG_SECURITY | **[NOT IMPLEMENTED]** — procedure does not exist |

### 3.6 Reporting Use Cases

| Use Case ID | Use Case Name | Actor | PL/SQL Entry Point | Package | Notes |
|------------|--------------|-------|--------------------|---------|-------|
| UC-RPT-01 | Generate Headcount Report | HR Admin | `PKG_REPORTING.headcount_report` | PKG_REPORTING | Queries OLTP directly; RPT_HEADCOUNT not populated |
| UC-RPT-02 | Generate Compensation Summary | HR Admin | `PKG_REPORTING.compensation_summary` | PKG_REPORTING | Uses Oracle MEDIAN(); no PostgreSQL equivalent (MC-02b) |
| UC-RPT-03 | Generate Turnover Report | HR Admin | `PKG_REPORTING.turnover_report` | PKG_REPORTING | Non-standard denominator — not SHRM-comparable (BR-044) |
| UC-RPT-04 | Generate New Hires Report | HR Admin | `PKG_REPORTING.new_hires_report` | PKG_REPORTING | Row-level detail; includes salary — PII co-location risk |
| UC-RPT-05 | Generate Leave Utilisation Report | HR Admin | `PKG_REPORTING.leave_utilization_report` | PKG_REPORTING | CALENDAR_YEAR not projected — multi-year snapshots broken (DQ-032) |
| UC-RPT-06 | Generate Payroll Summary Report | Payroll Admin | `PKG_REPORTING.payroll_summary_report` | PKG_REPORTING | Hard-coded element IDs 100–103 |
| UC-RPT-07 | Generate EEO Compliance Report | HR Admin | `PKG_REPORTING.eeo_compliance_report` | PKG_REPORTING | No GENDER CHECK constraint — data quality risk (TD-40) |
| UC-RPT-08 | Refresh Nightly Reporting Tables | Batch | `PKG_REPORTING.refresh_reporting_tables` | PKG_REPORTING | **[NOT IMPLEMENTED]** — stub; logs false success |

---

## 4. Oracle HRMS Component → New System Component Mapping

This section provides the strangler fig replacement map, identifying each legacy Oracle component and its target replacement in the forward-engineered system.

### 4.1 PL/SQL Package Replacement Map

| Legacy Component | Type | Bounded Context | Target New Component | Replacement Pattern | Migration Risk | Notes |
|-----------------|------|----------------|---------------------|---------------------|---------------|-------|
| PKG_EMPLOYEE | PL/SQL Package | Employee Identity (BC-01) | `EmployeeService` (REST microservice) | Strangler Fig — wrap existing, expose REST, migrate callers | High | 13-step terminate_employee requires full redesign; final-pay and COBRA must be implemented |
| PKG_PAYROLL | PL/SQL Package | Compensation (BC-02) | `PayrollService` (REST microservice) | Strangler Fig | Critical | HOH tax defect must be fixed in new system; direct deposit implementation required |
| PKG_LEAVE | PL/SQL Package | Leave Management (BC-03) | `LeaveService` (REST microservice) | Strangler Fig | Medium | Accrual retry defect (BR-LIB-05) must be corrected in migration |
| PKG_PERFORMANCE | PL/SQL Package | Performance (BC-04) | `PerformanceService` (REST microservice) | Strangler Fig | Medium | Calibration workflow must be designed and implemented (currently zero code) |
| PKG_SECURITY | PL/SQL Package | Security & Access (BC-06) | `AuthService` + Identity Provider (OAuth 2.0 / OIDC) | Full Replacement | Critical | Auth stub, MD5 passwords, hard-coded key all require complete replacement; no safe migration path |
| PKG_INTEGRATION | PL/SQL Package | Integration & Export (BC-09) | `IntegrationService` + message broker | Strangler Fig | High | Benefits feed, GL journal, time-attendance import all need redesign; org-sync is entirely new build |
| PKG_REPORTING | PL/SQL Package | Reporting (BC-10) | `ReportingService` + BI layer (e.g. Metabase, Power BI) | Full Replacement | Medium | Oracle MEDIAN() requires translation; RPT_* tables may never have held data |
| PKG_NOTIFICATION | PL/SQL Package | Notifications (BC-08) | `NotificationService` (event-driven) | Strangler Fig → Event Bus | Low | Queue-based pattern maps naturally to new event architecture |
| PKG_COMMON | PL/SQL Package | Cross-cutting | Shared `LoggingService` + error framework | Extract & Replace | Low | Single audit table must be split by log type; structured logging required |

### 4.2 Oracle Forms Screen Replacement Map

| Legacy Oracle Forms Module | Current Function | Target New Component | UI Technology | Priority | Gap / Notes |
|---------------------------|-----------------|---------------------|---------------|----------|-------------|
| HRMS_EMPLOYEE.fmb | Employee hire, update, transfer, terminate | Employee Management SPA | React / Vue.js | High | LOV_MANAGERS grade filter must be added (TD-72); Forms compilation requires Builder 12c (TD-76) |
| HRMS_PAYROLL.fmb | Payroll run create, calculate, approve, GL | Payroll Management SPA | React / Vue.js | High | Direct deposit disbursal screen needs new design |
| HRMS_LEAVE.fmb | Manager leave approval | Leave Management SPA | React / Vue.js | Medium | Self-service portal also covers employee-facing leave |
| HRMS_PERFORMANCE.fmb | Review cycle management, manager reviews | Performance Management SPA | React / Vue.js | Medium | Calibration workflow screen must be designed from scratch |
| HRMS_REPORTS.fmb | Report launcher for PKG_REPORTING procedures | BI Dashboard / Report Portal | BI tool or custom | Low | RPT_* refresh stub must be resolved before BI migration |
| HRMS_LOGIN.fmb | Authentication / session creation | Identity Provider login page | OAuth 2.0 / OIDC | Critical | Current login completely bypasses password check; must not be replicated |
| Self-service portal (implied) | Employee self-service (leave, payslip, goals) | Employee Self-Service App | React PWA | Medium | Portal DB connection model must be redesigned (TD-81) |

### 4.3 Database Schema Component Replacement Map

| Legacy Database Object | Object Type | Replacement Target | Migration Notes |
|-----------------------|-------------|-------------------|----------------|
| HRMS.EMPLOYEES | Core table | `employees` table in PostgreSQL (or equivalent) | Decrypt SSN/bank data; re-encrypt with new key; validate all rows |
| HRMS.DEPARTMENTS | Reference table | `departments` table | Straightforward migration; validate CONNECT BY hierarchy |
| HRMS.SALARY_RECORDS | History table | `salary_history` table | Preserve history; add current-record indicator |
| HRMS.PAYROLL_RUNS | Transaction table | `payroll_runs` table | Add GL_FEED_SENT_DATE, GL_FEED_FILE_NAME columns (TD-80) |
| HRMS.PAYROLL_DETAILS | Line-item table | `payroll_line_items` table | Migrate HOH-tax-defect affected rows with corrected calculations |
| HRMS.LEAVE_BALANCES | Balance table | `leave_balances` table | Validate accrual amounts for BR-LIB-05 retry defect impact |
| HRMS.LEAVE_REQUESTS | Request table | `leave_requests` table | Straightforward; status values map 1:1 |
| HRMS.PERFORMANCE_REVIEWS | Review table | `performance_reviews` table | Add CALIBRATION_STATUS; backfill CALIBRATED_RATING from OVERALL_RATING for existing records |
| HRMS.EMPLOYEE_DEPENDENTS | Dependent table | `employee_dependents` table | Resolve SSN decryption gap before migration; confirm COBRA retention policy |
| HRMS.EMPLOYEE_BANK_ACCOUNTS | Financial table | `employee_bank_accounts` table | Decrypt ACCOUNT_NUMBER_ENC; encrypt ROUTING_NUMBER; implement ACH prenote |
| HRMS.USER_SESSIONS | Session table | Replaced by JWT / OAuth tokens | No data migration; session state is ephemeral |
| HRMS.USER_CREDENTIALS | Credential table | Replaced by Identity Provider | MD5 hashes cannot be migrated; force password reset for all users |
| HRMS.AUDIT_LOG | Audit table | Structured audit log (separate by type) | Split into ERROR_LOG, INFO_LOG, DML_AUDIT before migration (TD-37) |
| HRMS.NOTIFICATION_QUEUE | Queue table | Message broker (e.g. RabbitMQ, SQS) | Current queue structure maps to broker queue; include retry logic |
| RPT_* tables (7, inferred) | Reporting tables | BI tool materialised views or warehouse | Confirm whether these tables ever held data before migrating |
| SYSTEM_PARAMETERS | Configuration table | Application config (env vars / secrets manager) | Hard-coded AES key must be rotated; timeout must be externalised |

### 4.4 Integration Component Replacement Map

| Legacy Integration | Direction | Protocol | Target Replacement | Priority | Migration Risk |
|-------------------|-----------|----------|-------------------|----------|---------------|
| ADP Benefits Feed (export_benefits_feed) | Outbound | Fixed-width flat file (203-char) | ADP API or SFTP with version-tagged format | High | No file version header or record count trailer currently (TD-73); BENEFITS_ENROLLED filter gap |
| Oracle Financials GL Feed (generate_gl_journal) | Outbound | Pipe-delimited flat file | Oracle Financials AutoPost API or direct journal import | High | Journal Source/Category not documented (TD-79); no sent-status tracking (TD-80) |
| Time & Attendance Import (import_time_attendance) | Inbound | CSV flat file via UTL_FILE | API endpoint from T&A vendor | High | Current procedure is a stub — no data ever imported; destination table DDL not recovered |
| LDAP/AD Org Sync (sync_org_structure) | Outbound | None currently | LDAP JNDI / Active Directory connector | Critical | Entirely unimplemented; connection parameters do not exist anywhere in source |
| Payroll Disbursement (direct deposit) | Outbound | None currently | NACHA ACH file or payment API | Critical | Zero code exists; full new design required |
| Oracle Reports .rdf files | Internal | Oracle Forms / Reports | BI tool report definitions | Medium | Verify which .rdf reports exist and what RPT_* tables they query |
| HRMS_REPORTS Oracle Forms | Internal | Oracle Forms | BI dashboard / report portal | Medium | Currently calls PKG_REPORTING which queries OLTP directly |

---

## 5. Data Table → Bounded Context Traceability

### 5.1 Table Ownership by Bounded Context

| Table Name | Owning Bounded Context | BC ID | Primary Owning Package | Shared Read Access | Access Pattern |
|-----------|----------------------|-------|----------------------|-------------------|----------------|
| EMPLOYEES | Employee Identity | BC-01 | PKG_EMPLOYEE | PKG_PAYROLL, PKG_LEAVE, PKG_PERFORMANCE, PKG_SECURITY, PKG_INTEGRATION, PKG_REPORTING | Master aggregate root; every context reads this table |
| EMPLOYEE_HISTORY | Employee Identity | BC-01 | PKG_EMPLOYEE | Read-only by HR reporting | Append-only audit log of employee state changes |
| DEPARTMENTS | Organisational Structure | BC-07 | PKG_EMPLOYEE (shared) | PKG_REPORTING, PKG_INTEGRATION | Shared kernel with BC-01 |
| JOB_POSITIONS | Organisational Structure | BC-07 | PKG_EMPLOYEE (shared) | PKG_REPORTING | Position catalogue |
| JOB_GRADES | Organisational Structure | BC-07 | Reference only | PKG_PAYROLL (salary validation), PKG_REPORTING | Grade band definitions; read by compensation |
| JOB_TITLES | Organisational Structure | BC-07 | Reference only | PKG_PAYROLL, PKG_REPORTING | Title catalogue |
| SALARY_RECORDS | Compensation | BC-02 | PKG_PAYROLL | PKG_REPORTING | Point-in-time salary history |
| PAYROLL_RUNS | Compensation | BC-02 | PKG_PAYROLL | PKG_INTEGRATION, PKG_REPORTING | Payroll cycle headers |
| PAYROLL_DETAILS | Compensation | BC-02 | PKG_PAYROLL | PKG_REPORTING | Per-employee per-run pay lines |
| DEDUCTION_RECORDS | Compensation | BC-02 | PKG_PAYROLL | PKG_REPORTING | Deduction line items |
| TAX_BRACKETS | Compensation | BC-02 | PKG_PAYROLL (read-only) | None | Federal income tax brackets reference data |
| STATE_TAX_RATES | Compensation | BC-02 | PKG_PAYROLL (read-only) | None | State flat-rate tax reference data |
| EMPLOYEE_BANK_ACCOUNTS | Compensation | BC-02 | PKG_PAYROLL (intended) | None currently | Direct deposit — table exists, never read by any package |
| LEAVE_BALANCES | Leave Management | BC-03 | PKG_LEAVE | PKG_REPORTING | Current balance per employee per leave type |
| LEAVE_REQUESTS | Leave Management | BC-03 | PKG_LEAVE | None | Request lifecycle table |
| LEAVE_TYPES | Leave Management | BC-03 | PKG_LEAVE (read-only) | None | Leave type reference data |
| PERFORMANCE_REVIEWS | Performance | BC-04 | PKG_PERFORMANCE | PKG_PAYROLL (OVERALL_RATING conformist read) | Review records per employee per cycle |
| REVIEW_CYCLES | Performance | BC-04 | PKG_PERFORMANCE | None | Cycle header and date range |
| PERFORMANCE_GOALS | Performance | BC-04 | PKG_PERFORMANCE | None | Goal definitions per employee per cycle |
| GOAL_REVIEWS | Performance | BC-04 | PKG_PERFORMANCE | None | Goal completion assessments |
| BENEFIT_PLANS | Benefits | BC-05 | PKG_INTEGRATION (partial) | None | Benefit plan reference data |
| BENEFIT_ENROLLMENTS | Benefits | BC-05 | PKG_INTEGRATION (partial) | None | Employee benefit plan enrollments |
| EMPLOYEE_DEPENDENTS | Benefits | BC-05 | PKG_INTEGRATION.export_benefits_feed | None (no DML from any package) | Dependent records for benefits feed |
| USER_SESSIONS | Security & Access | BC-06 | PKG_SECURITY | None | Active session tracking |
| USER_CREDENTIALS | Security & Access | BC-06 | PKG_SECURITY | None | Password hashes (MD5; critical security debt) |
| AUDIT_LOG | Security & Access | BC-06 | PKG_COMMON | All packages (write) | Single mixed-type audit table — needs splitting |
| NOTIFICATION_QUEUE | Notifications | BC-08 | PKG_NOTIFICATION | PKG_PAYROLL, PKG_LEAVE (write) | Pending notification records |
| NOTIFICATION_TEMPLATES | Notifications | BC-08 | PKG_NOTIFICATION | None | Template bodies for each notification type |
| SYSTEM_PARAMETERS | Cross-cutting | BC-06 (config) | PKG_COMMON | All packages | Runtime configuration; AES key must be rotated |
| LOOKUP_VALUES | Cross-cutting | Reference | PKG_COMMON | All packages | General lookup / reference data table |
| TERMINATION_CODES | Employee Identity | BC-01 | PKG_EMPLOYEE (read-only) | None | Valid termination reason codes |
| RPT_HEADCOUNT | Reporting | BC-10 | PKG_REPORTING (stub — never written) | None currently | Inferred; DDL not confirmed |
| RPT_COMPENSATION | Reporting | BC-10 | PKG_REPORTING (stub) | None currently | Inferred; DDL not confirmed |
| RPT_TURNOVER | Reporting | BC-10 | PKG_REPORTING (stub) | None currently | Inferred; DDL not confirmed |
| RPT_NEW_HIRES | Reporting | BC-10 | PKG_REPORTING (stub) | None currently | PII co-location risk — name + salary in one row; no access control |
| RPT_LEAVE_UTILIZATION | Reporting | BC-10 | PKG_REPORTING (stub) | None currently | CALENDAR_YEAR not projected — multi-year broken (DQ-032) |
| RPT_PAYROLL_SUMMARY | Reporting | BC-10 | PKG_REPORTING (stub) | None currently | Hard-coded element IDs 100–103 |
| RPT_EEO_COMPLIANCE | Reporting | BC-10 | PKG_REPORTING (stub) | None currently | Sensitive EEO data; no table-level access control confirmed |
| TIME_ATTENDANCE_RECORDS | Integration | BC-09 | PKG_INTEGRATION (intended) | None | Implied import target; DDL not recovered; never written to |

### 5.2 Cross-Context Data Dependency Matrix

| Dependent Context | Dependency | Source Context | Source Table | Risk |
|------------------|-----------|---------------|-------------|------|
| BC-02 Compensation | Reads employee status for payroll eligibility | BC-01 Employee Identity | EMPLOYEES.EMPLOYMENT_STATUS | Shared database coupling — no ACL |
| BC-02 Compensation | Reads salary records for pay calculation | BC-02 (self) | SALARY_RECORDS | Internal |
| BC-02 Compensation | Reads performance rating for merit eligibility | BC-04 Performance | PERFORMANCE_REVIEWS.OVERALL_RATING | Conformist — rating defect (HOH, calibration) propagates to pay |
| BC-03 Leave | Reads employee ID for balance initialisation | BC-01 Employee Identity | EMPLOYEES.EMP_ID | Shared database coupling |
| BC-04 Performance | Reads employee and reviewer IDs | BC-01 Employee Identity | EMPLOYEES.EMP_ID | Shared database coupling |
| BC-05 Benefits | Reads dependent and employee data for ADP feed | BC-01 Employee Identity | EMPLOYEES, EMPLOYEE_DEPENDENTS | Shared database coupling; BENEFITS_ENROLLED not filtered |
| BC-06 Security | Reads employee grade for RBAC | BC-01 Employee Identity | EMPLOYEES.GRADE | Grade change does not propagate to active session |
| BC-09 Integration | Reads compensation data for GL journal | BC-02 Compensation | PAYROLL_RUNS, PAYROLL_DETAILS | Shared database coupling; GL sent-status not tracked |
| BC-10 Reporting | Reads all contexts for operational reports | All contexts | Multiple OLTP tables | Direct OLTP query; RPT_* refresh stub means no reporting layer isolation |

---

## 6. Gap → Remediation Traceability

This section maps each identified gap to the new system feature or remediation action that addresses it, with priority and the bounded context responsible for delivery.

### 6.1 Critical Security Gaps

| Gap ID | Gap Description | Source Finding | Severity | New System Feature / Remediation | Target BC | Priority |
|--------|----------------|----------------|----------|----------------------------------|-----------|----------|
| GAP-SEC-01 | `authenticate()` never verifies password — any valid username logs in | BR-042, DQ-003 | Critical | Replace PKG_SECURITY.authenticate with OAuth 2.0 / OIDC identity provider; force password reset for all users | BC-06 → AuthService | P0 |
| GAP-SEC-02 | AES-256 key hard-coded as `HR$ystem_3ncrypt10n_K3y_2024!!` | DQ-001, SEC-03, TD-01 | Critical | Migrate encrypted columns to new key stored in AWS Secrets Manager / HashiCorp Vault; rotate key before go-live | BC-06 → SecretsManagement | P0 |
| GAP-SEC-03 | MD5 password hashing (cryptographically broken) | DQ-010 | Critical | Use bcrypt/Argon2 in new AuthService; existing hashes cannot be migrated — force reset | BC-06 → AuthService | P0 |
| GAP-SEC-04 | `change_password` never verifies old password | BR-044, DQ-029 | High | Implement old-password verification in new password change API before updating credential | BC-06 → AuthService | P1 |
| GAP-SEC-05 | No brute-force lockout mechanism | DQ-023, BR-072 | High | Implement failed-login counter with lockout threshold (e.g. 5 attempts → 15-minute lockout) in AuthService | BC-06 → AuthService | P1 |
| GAP-SEC-06 | Routing numbers stored in plain text | TD-46, BR-BA-04 | High | Encrypt ROUTING_NUMBER alongside ACCOUNT_NUMBER_ENC using secrets manager key | BC-02 → PayrollService | P1 |
| GAP-SEC-07 | Self-service portal DB user has unrestricted schema access | TD-81 | High | Create HRMS_PORTAL_APP user with EXECUTE grants on specific procedures only; revoke table-level grants | BC-06 → Infrastructure | P1 |
| GAP-SEC-08 | `revoke_access` procedure does not exist — active sessions not killed on termination | BR-TERM-06 | High | Implement session invalidation in EmployeeService termination flow; pass invalidation event to AuthService | BC-01 → EmployeeService | P1 |
| GAP-SEC-09 | Stale sessions never swept — Users who close browser without logout retain ACTIVE session rows | TD-75 | Medium | Implement background token expiry via OAuth token TTL; add session sweep job for legacy rows | BC-06 → AuthService | P2 |
| GAP-SEC-10 | RPT_NEW_HIRES exposes name + salary with no table-level access guard | DA PII inventory | Medium | Apply column-level encryption or row-level security on RPT_NEW_HIRES in new BI layer | BC-10 → ReportingService | P2 |

### 6.2 Critical Functional Gaps (Missing Implementations)

| Gap ID | Gap Description | Source Finding | Severity | New System Feature / Remediation | Target BC | Priority |
|--------|----------------|----------------|----------|----------------------------------|-----------|----------|
| GAP-FUNC-01 | Direct deposit never implemented — EMPLOYEE_BANK_ACCOUNTS never read | BR-BA-12, PP-BA-01, DISC-009 | Critical | Implement `PaymentDisbursementService`: read bank accounts → generate NACHA ACH file → update PAYROLL_RUNS status to PAID | BC-02 → PaymentDisbursementService | P0 |
| GAP-FUNC-02 | `calculate_final_pay` procedure does not exist | BR-TERM-03, PP-TERM-03 | Critical | Design and implement final-pay calculation: prorate salary to termination date, apply PTO payout policy, handle off-cycle payroll run | BC-02 → PayrollService | P0 |
| GAP-FUNC-03 | COBRA notification not implemented — federal compliance gap on every termination | BR-09, PP-TERM-01 | Critical | Implement COBRA notification workflow: 14-day SLA trigger, dependent eligibility assessment, notification generation; integrate with NotificationService | BC-01 → TerminationWorkflowService | P0 |
| GAP-FUNC-04 | HOH tax filing returns $0 federal tax — incorrect calculation for all HOH filers | BR-23, critical payroll defect | Critical | Fix HOH bracket lookup in new PayrollService; backfill corrected amounts for all historical HOH runs; consult tax counsel | BC-02 → PayrollService | P0 |
| GAP-FUNC-05 | Calibration workflow has zero implementation — CALIBRATED_RATING is a dead column | BR-66, calibration gap | High | Design calibration workflow: status COMPLETED → CALIBRATION_IN_PROGRESS → CALIBRATED; implement calibration session, write CALIBRATED_RATING; update `get_rating_distribution` to use CALIBRATED_RATING | BC-04 → PerformanceService | P1 |
| GAP-FUNC-06 | Org structure sync completely unimplemented — only logs false success | BR-ORG-01, BR-ORG-02, PP-ORG-01 | High | Design LDAP/AD sync: define connection parameters, delta-sync mode, target OU; implement full PKG_INTEGRATION.sync_org_structure replacement | BC-09 → IntegrationService | P1 |
| GAP-FUNC-07 | Time and attendance import is a stub — no data ever written to destination | DQ-031, BR-046 | High | Design T&A import: define destination table DDL, CSV-to-row mapping, transaction boundary, payroll linkage; implement import and unit tests | BC-09 → IntegrationService | P1 |
| GAP-FUNC-08 | RPT_* reporting tables never populated — nightly refresh is a false-success stub | BR-043 | High | Implement nightly ETL job: TRUNCATE and repopulate all 7 RPT_* tables from OLTP; add record count trailer validation; add scheduler monitoring | BC-10 → ReportingService | P1 |
| GAP-FUNC-09 | ACH prenote not implemented — Nacha compliance gap | PP-BA-03, BR-BA-05 | High | Implement prenote workflow: set PRENOTE_SENT flag on account creation, wait 3 banking days, then release account for live disbursement | BC-02 → PaymentDisbursementService | P1 |
| GAP-FUNC-10 | Dependent inactivation not linked to employee termination | BR-DEP-09, VQ-DEP-04 | High | Add dependent inactivation step to TerminationWorkflowService; confirm COBRA hold policy before implementing (VQ-DEP-04) | BC-01 → TerminationWorkflowService | P1 |

### 6.3 Data Quality and Integrity Gaps

| Gap ID | Gap Description | Source Finding | Severity | New System Feature / Remediation | Target BC | Priority |
|--------|----------------|----------------|----------|----------------------------------|-----------|----------|
| GAP-DQ-01 | Accrual retry path overwrites balance instead of incrementing (BR-LIB-05) | BR-LIB-05, PKG_LEAVE | High | Fix `run_monthly_accrual` SET clause to use `ACCRUED = ACCRUED + v_accrued`; audit existing balances for affected rows; add regression test | BC-03 → LeaveService | P0 |
| GAP-DQ-02 | Duplicate email causes silent wrong-user login via MIN(EMP_ID) | BR-043b, DQ auth | High | Add UNIQUE constraint on EMPLOYEES.EMAIL; resolve existing duplicate emails before migration | BC-01 → EmployeeService | P0 |
| GAP-DQ-03 | BENEFITS_ENROLLED flag collected but never used — all active dependents exported regardless | BR-DEP-05, G-1 | High | Filter `BENEFITS_ENROLLED = 'Y'` in ADP benefits feed export; design enrollment workflow to set flag | BC-05 → BenefitsService | P1 |
| GAP-DQ-04 | Deposit amounts have no distribution total validation | BR-BA-11, PP-BA-05 | High | Add API validation: PARTIAL_PERCENT accounts must sum to 100% before save; add CHECK or trigger in new schema | BC-02 → PaymentDisbursementService | P1 |
| GAP-DQ-05 | No DEPOSIT_TYPE cross-column constraint (PARTIAL_AMOUNT with NULL amount valid) | BR-BA-09, PP-BA-04 | High | Add conditional NOT NULL validation: if DEPOSIT_TYPE = 'PARTIAL_AMOUNT' then DEPOSIT_AMOUNT must not be null | BC-02 → PaymentDisbursementService | P1 |
| GAP-DQ-06 | CALENDAR_YEAR not projected in leave utilisation cursor — multi-year snapshots broken | DQ-032, BR-045 | High | Add CALENDAR_YEAR to SELECT list in leave_utilization_report and RPT_LEAVE_UTILIZATION INSERT | BC-10 → ReportingService | P1 |
| GAP-DQ-07 | FMLA seed data has REQUIRES_DOCUMENT='N' — FMLA documentation not enforced | TD-71 | Medium | Update FMLA reference data to REQUIRES_DOCUMENT='Y'; implement document path enforcement in LeaveService | BC-03 → LeaveService | P2 |
| GAP-DQ-08 | Gender field has no CHECK constraint — arbitrary values distort EEO reporting | TD-40 | Medium | Add CHECK constraint EMPLOYEES.GENDER IN ('M','F','O','N'); cleanse existing data | BC-01 → EmployeeService | P2 |
| GAP-DQ-09 | Salary range validation fires in debug mode only — grade-band violations accepted silently | TD-74 | Medium | Elevate salary-grade validation to blocking error in EmployeeService; implement at API boundary | BC-01 → EmployeeService | P2 |
| GAP-DQ-10 | Turnover report uses non-standard denominator — figures not SHRM-comparable | BR-044 | Medium | Redesign turnover calculation to use average headcount denominator; document formula in report metadata | BC-10 → ReportingService | P2 |
| GAP-DQ-11 | `e_account_locked` and `e_session_expired` exceptions declared but never raised | BR-045, DQ-030 | Medium | Remove dead exception declarations; replace with proper error responses in new AuthService | BC-06 → AuthService | P2 |
| GAP-DQ-12 | `rating_distribution` report reads pre-calibration OVERALL_RATING, not CALIBRATED_RATING | BR-67 | Medium | After calibration workflow implemented (GAP-FUNC-05), update report to read CALIBRATED_RATING | BC-04 → PerformanceService | P2 |

### 6.4 Operational and Compliance Gaps

| Gap ID | Gap Description | Source Finding | Severity | New System Feature / Remediation | Target BC | Priority |
|--------|----------------|----------------|----------|----------------------------------|-----------|----------|
| GAP-OPS-01 | No CI/CD pipeline of any kind — build, test, deploy all manual | TD TA section | Critical | Establish CI/CD pipeline: lint, PL/SQL compile, unit tests, SAST scan, secret scanner, staging deploy, smoke test, auto-rollback | DevOps | P0 |
| GAP-OPS-02 | AES key would have been caught immediately by a secret scanner — none exists | TD-01 TA section | Critical | Implement secret scanning (gitleaks / TruffleHog) as pre-commit hook and CI step | DevOps | P0 |
| GAP-OPS-03 | GL feed has no sent-status tracking — missed feeds invisible | TD-80 | High | Add GL_FEED_SENT_DATE and GL_FEED_FILE_NAME to PAYROLL_RUNS; expose in payroll admin UI | BC-09 → IntegrationService | P1 |
| GAP-OPS-04 | sync_org_structure logs false success on every scheduled run — monitoring cannot detect failures | BR-ORG-02, PP-ORG-01 | High | Remove false-success log before implementation; add health-check endpoint; alert on non-completion | BC-09 → IntegrationService | P1 |
| GAP-OPS-05 | ADP benefits feed has no file version header, record count trailer, or checksum | TD-73 | Medium | Add ADP file header with format version; add trailer with employee count; add per-record length validation | BC-09 → IntegrationService | P2 |
| GAP-OPS-06 | Oracle Financials GL Journal Source/Category not documented | TD-79 | Medium | Document and add Journal Source/Category as SYSTEM_PARAMETERS entries; validate before file generation | BC-09 → IntegrationService | P2 |
| GAP-OPS-07 | No audit separation — ERROR_LOG, INFO_LOG, and DML audit in single table with one purge policy | TD-37 | Medium | Split AUDIT_LOG into dedicated tables in new system; define independent retention policies per type | BC-06 → LoggingService | P2 |
| GAP-OPS-08 | Oracle Forms compilation requires Builder 12c with no build script | TD-76 | Medium | Document Forms compilation process; create frmcmp.sh script; include in CI as bridging step before strangler-fig cutover | DevOps | P2 |
| GAP-OPS-09 | LOV_MANAGERS allows any active employee as manager regardless of grade | TD-72 | Medium | Add grade-based or IS_MANAGER flag filter to manager selection in new EmployeeService | BC-01 → EmployeeService | P2 |
| GAP-OPS-10 | No observability — DBMS_OUTPUT only in debug; no structured logging; no correlation IDs | TA observability section | High | Implement structured JSON logging with severity levels, correlation IDs, and centralised log aggregation (e.g. ELK, Datadog) | Cross-cutting → ObservabilityService | P1 |

### 6.5 Architecture and Design Gaps

| Gap ID | Gap Description | Source Finding | Severity | New System Feature / Remediation | Target BC | Priority |
|--------|----------------|----------------|----------|----------------------------------|-----------|----------|
| GAP-ARCH-01 | All bounded contexts share one Oracle schema with no access controls | BC context map, AV-* violations | High | Decompose into separate schemas/services; enforce service-to-service API contracts; remove shared-database coupling | All BCs | P0 |
| GAP-ARCH-02 | Oracle MEDIAN() aggregate has no direct PostgreSQL/SQL Server equivalent | MC-02b | Medium | Use `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary)` equivalent; validate output parity before cutover | BC-10 → ReportingService | P2 |
| GAP-ARCH-03 | Grade change in BC-01 does not propagate to active BC-06 session — stale RBAC | BC context map | Medium | Implement session invalidation on grade change; or re-check permission on each request from identity token claims | BC-06 → AuthService | P2 |
| GAP-ARCH-04 | No event system — BC-02 payroll completion triggers BC-08 notification via direct call, not event | BC context map | Low | Introduce domain events (PayrollCalculated, EmployeeTerminated, ReviewCompleted) consumed by NotificationService | BC-08 → NotificationService | P3 |
| GAP-ARCH-05 | PERFORMANCE_REVIEWS.CALIBRATED_RATING is a dead schema column with no supporting process | calibration gap | Medium | Either implement full calibration workflow (GAP-FUNC-05) or remove column and document decision | BC-04 → PerformanceService | P1 |
| GAP-ARCH-06 | EMPLOYEE_BANK_ACCOUNTS decryption path does not exist anywhere in codebase | BR-BA-12, VQ-BA-01 | High | Confirm encryption key before data migration; implement decryption in new PaymentDisbursementService | BC-02 → PaymentDisbursementService | P0 |

---

## Appendix A — Gap Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| P0 — Blocker before go-live | 12 | Auth bypass, hard-coded key, direct deposit missing, final-pay missing, COBRA missing, HOH tax defect, accrual overwrite, duplicate-email auth, bank account decryption path, CI/CD absent, secret scanning absent |
| P1 — Required in first release | 18 | Session revocation, brute-force lockout, calibration workflow, org sync, time-attendance import, RPT_* ETL, ACH prenote, COBRA dependent review, GL sent-status, routing number encryption, portal DB user, observability |
| P2 — Required in second release | 19 | BENEFITS_ENROLLED filter, deposit validation, FMLA document enforcement, gender constraint, salary validation, turnover denominator, dead exceptions, calibration reporting, ADP file header/trailer, GL journal metadata, audit log split, Forms build script, LOV_MANAGERS grade filter, leave CALENDAR_YEAR |
| P3 — Future enhancement | 3 | Domain event architecture, 360-degree reviews, full BI layer isolation |

---

## Appendix B — Traceability Coverage Summary

| Section | Items Mapped | Fully Traced | Partially Traced | Not Implemented / Gap |
|---------|-------------|-------------|-----------------|----------------------|
| Business Requirements → Source Code | 70 | 42 | 11 | 17 |
| Business Rules → DB Constraints | 45 | 31 | 8 | 6 |
| Use Cases → API Endpoints | 52 | 38 | 4 | 10 |
| Oracle Components → New System Components | 38 | 38 (mapped) | 0 | 0 (all mapped; risk noted) |
| Data Tables → Bounded Contexts | 38 | 38 | 0 | 0 (all assigned; access gaps noted) |
| Gaps → Remediations | 52 | 52 | 0 | 0 |

**Total items traced across all sections: 293**
**Total gaps requiring new system feature or remediation: 52**
**Critical (P0) blockers before go-live: 12**

---

*Document generated from merged BA, DA, TA, and AA analysis tracks. All gap IDs cross-reference the source finding IDs in the originating analysis documents. Discrepancy log items DISC-001 through DISC-009 are fully traceable to GAP entries in Section 6.*
