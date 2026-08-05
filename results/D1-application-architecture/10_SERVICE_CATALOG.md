# 10 — SERVICE CATALOG
## Acme HRMS v4.2.0 — All PL/SQL Packages and External Interfaces

---

## PACKAGE: PKG_EMPLOYEE
**Domain:** BC-01 Employee Lifecycle
**Schema:** HRMS
**Dependencies:** PKG_SECURITY (encryption), PKG_AUDIT, PKG_VALIDATION, PKG_NOTIFICATION
**Tables Owned:** EMPLOYEES, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS, EMPLOYEE_BANK_ACCOUNTS
**Tables Read:** DEPARTMENTS, POSITIONS, GRADES, USER_ACCOUNTS

| Procedure / Function | Signature (parameters) | Returns | Description | Defects |
|---|---|---|---|---|
| hire_employee | p_first_name VARCHAR2, p_last_name VARCHAR2, p_email VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_grade NUMBER, p_salary NUMBER, p_employment_type VARCHAR2, p_ssn VARCHAR2 | p_emp_id OUT NUMBER | Creates EMPLOYEES row (encrypts SSN), inserts EMPLOYEE_HISTORY HIRE record, creates USER_ACCOUNTS entry, assigns default role, calls PKG_AUDIT | None confirmed |
| terminate_employee | p_emp_id NUMBER, p_termination_date DATE, p_reason VARCHAR2 | — | Sets EMPLOYEES.STATUS='INACTIVE', TERMINATION_DATE; inserts EMPLOYEE_HISTORY TERMINATION record; deactivates USER_ACCOUNTS | COBRA notification missing (MISS-03) |
| transfer_employee | p_emp_id NUMBER, p_new_dept_id NUMBER, p_new_position_id NUMBER, p_effective_date DATE | — | Updates EMPLOYEES.DEPT_ID, POSITION_ID; inserts EMPLOYEE_HISTORY TRANSFER record | TRG_EMP_BEFORE_UPDATE fails (DEFECT-02) |
| promote_employee | p_emp_id NUMBER, p_new_grade NUMBER, p_new_salary NUMBER, p_effective_date DATE | — | Updates EMPLOYEES.GRADE, SALARY; inserts SALARY_HISTORY; inserts EMPLOYEE_HISTORY PROMOTION record | TRG_EMP_BEFORE_UPDATE fails (DEFECT-02) |
| get_employee | p_emp_id NUMBER | SYS_REFCURSOR | Returns full employee row with dept/position joins (via VW_EMPLOYEE_DETAILS) | None |
| search_employees | p_search_criteria VARCHAR2 | SYS_REFCURSOR | Dynamic SQL search — potential SQL injection risk (DEFECT-09) | SQL injection (DEFECT-09) |
| get_org_chart | p_root_emp_id NUMBER | SYS_REFCURSOR | CONNECT BY query from EMPLOYEES; returns hierarchical tree | None |
| update_bank_account | p_emp_id NUMBER, p_bank_name VARCHAR2, p_account_number VARCHAR2, p_routing_number VARCHAR2, p_account_type VARCHAR2 | — | Inserts/updates EMPLOYEE_BANK_ACCOUNTS; encrypts account_number | Populated but never read by PKG_PAYROLL (DEFECT-01) |
| add_dependent | p_emp_id NUMBER, p_first_name VARCHAR2, p_last_name VARCHAR2, p_relationship VARCHAR2, p_dob DATE | — | Inserts EMPLOYEE_DEPENDENTS row | None |

[SUPPLEMENTED] **CORRECTIONS — PKG_EMPLOYEE.pks / PKG_EMPLOYEE.pkb now confirmed:**

The following entries in the table above do NOT match the actual package body:
- `hire_employee` — actual public function is **`create_employee`**. Signature: `create_employee(p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_manager_emp_id NUMBER DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_employment_type VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary NUMBER DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER`
- `update_bank_account` — **NOT in PKG_EMPLOYEE**. EMPLOYEE_BANK_ACCOUNTS is not written by any confirmed package.
- `add_dependent` — **NOT in PKG_EMPLOYEE**. EMPLOYEE_DEPENDENTS is not written by any confirmed package.
- `get_employee` — returns `t_emp_rec` (a typed record), **not** SYS_REFCURSOR.
- `search_employees` — is a PROCEDURE with OUT cursor parameter, not a function.
- `get_org_chart` — returns `t_emp_cursor` (REF CURSOR), not SYS_REFCURSOR (same underlying type, different declared type name).

[SUPPLEMENTED] **MISSING procedures / functions (confirmed from PKG_EMPLOYEE.pks / PKG_EMPLOYEE.pkb):**

| Procedure / Function | Signature (confirmed) | Returns | Description | Defects |
|---|---|---|---|---|
| get_employee_by_number | p_emp_number VARCHAR2 | t_emp_rec | Looks up EMP_ID by EMP_NUMBER then delegates to get_employee | Raises -20001 if not found |
| rehire_employee | p_emp_id NUMBER, p_rehire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_base_salary NUMBER, p_user VARCHAR2 DEFAULT USER | — | Resets EMPLOYMENT_STATUS='ACTIVE', clears TERMINATION_DATE/REASON, updates DEPT_ID/JOB_ID, calls PKG_PAYROLL.create_salary_record with reason 'REHIRE', logs history | None confirmed |
| get_direct_reports | p_manager_emp_id NUMBER | t_emp_id_table | Returns PL/SQL index-by table of EMP_IDs for all ACTIVE direct reports ordered by name | None |
| get_headcount_by_dept | p_dept_id NUMBER DEFAULT NULL, p_as_of_date DATE DEFAULT SYSDATE | NUMBER | Returns count of ACTIVE employees hired on or before as_of_date, not yet terminated | None |
| get_tenure_years | p_emp_id NUMBER | NUMBER | Returns MONTHS_BETWEEN(term_or_sysdate, hire_date)/12 rounded to 1 decimal | Returns NULL if employee not found |
| is_active | p_emp_id NUMBER | BOOLEAN | Returns TRUE if EMPLOYMENT_STATUS='ACTIVE'; FALSE if not found | None |
| validate_employee | p_emp_id NUMBER | BOOLEAN | Checks first/last name not null, hire date not null, ACTIVE status consistent with ACTIVE_FLAG | None |
| emp_exists | p_emp_id NUMBER | BOOLEAN | Returns TRUE if any row exists with EMP_ID; does not check status | None |
| generate_emp_number | (none) | VARCHAR2 | Generates next employee number as EMP-NNNNNN using MAX()+1 pattern | **BUG confirmed in source comment:** race condition under concurrent inserts — no SELECT FOR UPDATE; SEQ_EMPLOYEE used as fallback in EXCEPTION handler |
| set_session_context | p_user VARCHAR2, p_emp_id NUMBER | — | Sets package globals g_current_user, g_current_emp_id, g_current_dept_id (from EMPLOYEES.DEPT_ID); called by PKG_SECURITY.authenticate after login | None |

[SUPPLEMENTED] **Package-level declarations (confirmed from PKG_EMPLOYEE.pks):**

*Global variables (session state, accessible by all callers):*
- `g_current_user VARCHAR2(30)` — username of currently logged-in user
- `g_current_emp_id NUMBER(10)` — EMP_ID of current user
- `g_current_dept_id NUMBER(10)` — DEPT_ID of current user
- `g_debug_mode BOOLEAN DEFAULT FALSE` — enables DBMS_OUTPUT in exception handlers

*Custom exception codes (PRAGMA EXCEPTION_INIT):*
- `e_employee_not_found` / `-20001` — employee lookup failed
- `e_duplicate_emp_number` / `-20002` — EMP_NUMBER collision on INSERT
- `e_invalid_department` / `-20003` — dept not found or ACTIVE_FLAG='N'
- `e_invalid_manager` / `-20004` — manager not found, inactive, or circular chain
- `e_termination_error` / `-20005` — termination pre-condition failed

*Package types:*
- `t_emp_rec IS RECORD` — typed record matching key EMPLOYEES columns plus BASE_SALARY NUMBER(12,2)
- `t_emp_cursor IS REF CURSOR` — used for get_org_chart and search_employees
- `t_emp_id_table IS TABLE OF NUMBER(10) INDEX BY BINARY_INTEGER` — used by get_direct_reports
- `t_emp_rec_table IS TABLE OF t_emp_rec INDEX BY BINARY_INTEGER`

[SUPPLEMENTED] **Implementation details confirmed from PKG_EMPLOYEE.pkb:**

*create_employee behaviour:*
- Names stored as `UPPER(TRIM(...))`, email stored as `LOWER(TRIM(...))`
- Location defaulted from DEPARTMENTS.LOCATION_CODE if p_location_code IS NULL
- Salary validated against JOB_GRADES range (soft warning only — allows override)
- Calls PKG_PAYROLL.create_salary_record (circular dependency: PKG_PAYROLL calls PKG_EMPLOYEE.is_active for validation)
- Sends welcome email to new employee AND notification to manager via PKG_NOTIFICATION
- Raises DUP_VAL_ON_INDEX (-20002) on EMP_NUMBER collision

*terminate_employee behaviour:*
- Auto-cancels all PENDING leave requests (UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED')
- Ends active SALARY_RECORDS (sets END_DATE, ACTIVE_FLAG='N')
- Deactivates EMPLOYEE_PAY_ELEMENTS (sets END_DATE, ACTIVE_FLAG='N')
- Notifies manager via PKG_NOTIFICATION
- **TODO items confirmed in source (not implemented):** COBRA via benefits system, access revocation via PKG_SECURITY, final pay via PKG_PAYROLL.calculate_final_pay (this procedure does not exist — MISS-02 confirmed)

*search_employees SQL injection (confirmed DEFECT-09):* p_last_name, p_first_name, p_status, p_location_code are all concatenated into dynamic SQL without bind variables. Source comment explicitly notes: "BUG: SQL injection possible via p_last_name if called with unvalidated input".

*get_org_chart:* Uses Oracle CONNECT BY with `LEVEL <= p_max_depth` (default 10). Source comment confirms: "known to time out for orgs with >500 employees".

*Private helper procedures (not in public spec):* `log_history` (PRAGMA AUTONOMOUS_TRANSACTION — history inserts survive ROLLBACK), `validate_dept`, `validate_manager` (includes circular chain detection up to c_max_hierarchy_depth=15), `get_next_emp_id`

---

## PACKAGE: PKG_PAYROLL
**Domain:** BC-02 Payroll and Compensation
**Schema:** HRMS
**Dependencies:** PKG_AUDIT, PKG_COMMON
**Tables Owned:** SALARY_RECORDS, PAYROLL_RUNS, PAYROLL_DETAILS, PAY_PERIODS, PAY_ELEMENTS, EMPLOYEE_PAY_ELEMENTS, EMPLOYEE_TAX_INFO
**Tables Read:** EMPLOYEES, DEPARTMENTS, TAX_BRACKETS (empty)

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| create_salary_record | p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2, p_change_pct NUMBER, p_currency_code VARCHAR2, p_pay_frequency VARCHAR2, p_user VARCHAR2 | — | End-dates prior active salary record; inserts new SALARY_RECORDS row (ANNUAL basis); calls PKG_AUDIT | Raises -20101 if salary ≤ 0 |
| get_current_salary | p_emp_id NUMBER | NUMBER | Returns BASE_SALARY from active SALARY_RECORDS row as of SYSDATE; returns 0 if not found | None |
| get_salary_as_of | p_emp_id NUMBER, p_as_of DATE | NUMBER | Returns BASE_SALARY from SALARY_RECORDS effective on a given date; returns 0 if not found | None |
| create_pay_periods | p_year NUMBER, p_frequency VARCHAR2, p_user VARCHAR2 | — | Generates MONTHLY (12) or BIWEEKLY (~26) PAY_PERIODS rows for a full year; adjusts month-end pay dates off weekends; commits | None |
| close_pay_period | p_period_id NUMBER, p_user VARCHAR2 | — | Sets PAY_PERIODS.STATUS='CLOSED'; raises -20102 if already closed | Uses SELECT FOR UPDATE |
| get_current_period | (none) | NUMBER | Returns PERIOD_ID of open PAY_PERIODS row spanning SYSDATE; NULL if none | None |
| create_payroll_run | p_period_id NUMBER, p_run_type VARCHAR2, p_user VARCHAR2 | NUMBER (RUN_ID) | Creates PAYROLL_RUNS row in PENDING status; raises -20102 if period is CLOSED | None |
| calculate_payroll | p_run_id NUMBER, p_user VARCHAR2 | — | Iterates all ACTIVE employees via cursor loop; calls calculate_employee_pay per employee; commits every 50 rows; updates run totals and STATUS | **PERF-01:** row-by-row cursor loop (commented as BUG — should use BULK COLLECT/FORALL); **DEFECT-X:** partial commits leave payroll half-calculated on failure |
| calculate_employee_pay | p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 | — | Calculates period gross (annual salary / periods_per_year); inserts EARNING detail; calculates and inserts federal tax, state tax, FICA, Medicare, and benefit/deduction elements | Federal tax simplified (taxable = gross, pretax deductions not subtracted) |
| approve_payroll | p_run_id NUMBER, p_user VARCHAR2 | — | Sets PAYROLL_RUNS.STATUS='APPROVED'; raises -20103 if run is not CALCULATED | Uses SELECT FOR UPDATE |
| reverse_payroll | p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 | — | Sets PAYROLL_RUNS.STATUS='REVERSED'; sets all PAYROLL_DETAILS.STATUS='REVERSED'; calls PKG_AUDIT | None |
| calculate_federal_tax | p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER, p_additional_wh NUMBER, p_pay_frequency VARCHAR2 | NUMBER | Annualizes income; subtracts standard deduction and allowances; applies 2024 progressive brackets (SINGLE/MARRIED_SEPARATE/MARRIED_JOINT); de-annualizes result; adds additional withholding | **DEFECT-07 supplement:** brackets are hard-coded, not read from TAX_BRACKETS table (TODO in source) |
| calculate_state_tax | p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER, p_pay_frequency VARCHAR2 | NUMBER | Simplified flat-rate state tax; CA=7.25%, NY=6.85%, TX/FL/WA=0%, IL=4.95%, PA=3.07%, OH=4%, NJ=6.37%, MA=5%, default=5% | **OQ-005 supplement:** flat rates, not bracket-based; production implementation noted as needed per source comment |
| calculate_fica | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER | Returns SS tax at 6.2% up to $168,600 (2024) YTD wage base cap | None |
| calculate_medicare | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER | Returns 1.45% base + 0.9% additional Medicare on earnings above $200,000 YTD | None |
| get_payslip | p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER | (cursor) | Returns per-employee payslip summary (gross, deductions, net, individual tax lines) for a run; YTD_GROSS and YTD_NET are placeholder zeros | **GAP:** YTD columns hardcoded to 0 |
| get_ytd_earnings | p_emp_id NUMBER, p_tax_year NUMBER | NUMBER | Sums EARNING amounts from PAYROLL_DETAILS for CALCULATED details in a given tax year | None |
| generate_pay_register | p_run_id NUMBER, p_user VARCHAR2 | — | Writes CSV pay register to UTL_FILE directory PAYROLL_OUTPUT; includes dept breakdown per employee | **LEGACY:** UTL_FILE flat-file output noted as needing replacement with modern reporting |

[SUPPLEMENTED] *PKG_PAYROLL body fully sourced (PKG_PAYROLL.pkb). Tables owned revised from PAYROLL_RECORDS/DEDUCTIONS/SALARY_HISTORY to match actual DDL: SALARY_RECORDS, PAYROLL_RUNS, PAYROLL_DETAILS, PAY_PERIODS. All procedures and functions above are confirmed from source — several were missing from the original catalog entry.*

[SUPPLEMENTED] **Tax constants (from source):**
- Social Security wage base 2024: $168,600 (c_ss_wage_base_2024)
- SS employee rate: 6.2% (c_ss_rate)
- Medicare base rate: 1.45% (c_medicare_rate)
- Additional Medicare rate: 0.9% above $200,000 (c_medicare_addl_rate / c_medicare_addl_threshold)
- Standard deduction Single/MFS: $14,600; Married Joint: $29,200
- Per-allowance reduction: $4,300 (c_allowance_amount)

---

## PACKAGE: PKG_LEAVE
**Domain:** BC-03 Leave Management
**Schema:** HRMS
**Dependencies:** PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON
**Tables Owned:** LEAVE_REQUESTS, LEAVE_BALANCES
**Tables Read:** EMPLOYEES, LEAVE_TYPES

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| submit_leave_request | p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_days_requested NUMBER, p_reason VARCHAR2 | p_request_id OUT NUMBER | Validates eligibility (status, tenure, balance); inserts LEAVE_REQUESTS (PENDING); updates LEAVE_BALANCES.PENDING | None confirmed |
| approve_leave | p_request_id NUMBER, p_approver_id NUMBER | — | Updates LEAVE_REQUESTS.STATUS='APPROVED'; updates LEAVE_BALANCES.USED+=days, PENDING-=days; sends LEAVE_APPROVED notification | None |
| reject_leave | p_request_id NUMBER, p_approver_id NUMBER, p_notes VARCHAR2 | — | Updates STATUS='REJECTED'; decrements LEAVE_BALANCES.PENDING | None |
| cancel_leave | p_request_id NUMBER | — | Updates STATUS='CANCELLED'; decrements LEAVE_BALANCES.PENDING; decrements USED if already approved | None |
| accrue_leave | p_accrual_date DATE | p_records_processed OUT NUMBER | Monthly accrual: cursors ACTIVE employees with accruing leave types; adds 1.25 (PTO) or 0.833 (SICK) days; prevents double-accrual via LAST_ACCRUAL_DATE | None |
| get_leave_balance | p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER | SYS_REFCURSOR | Returns LEAVE_BALANCES row including AVAILABLE virtual column | None (reads authoritative virtual column) |
| initialize_balances | p_emp_id NUMBER, p_year NUMBER | — | Creates LEAVE_BALANCES rows for all active leave types for a new employee or new year | None |
| year_end_rollover | p_from_year NUMBER, p_to_year NUMBER | — | Creates new year LEAVE_BALANCES rows; sets OPENING_BALANCE = MIN(prior AVAILABLE, MAX_CARRYOVER) | MAX_CARRYOVER values not sourced (OQ-006) |

[SUPPLEMENTED] **CORRECTIONS and MISSING procedures — PKG_LEAVE.pkb now confirmed:**

*Procedure name corrections:*
- `approve_leave` — actual name: `approve_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)`
- `reject_leave` — actual name: `reject_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER)` — note: p_comments is NOT optional here
- `cancel_leave` — actual name: `cancel_leave_request(p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)` — no p_emp_id parameter
- `accrue_leave` / `accrue_monthly_leave` — actual name: `run_monthly_accrual(p_accrual_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER)` — no OUT parameter; counts logged to DBMS_OUTPUT
- `get_leave_balance` — returns NUMBER, not SYS_REFCURSOR; actual signature: `get_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER`
- `year_end_rollover` — actual name: `process_carryover(p_year NUMBER, p_user VARCHAR2 DEFAULT USER)` — processes from p_year into p_year+1

*Confirmed MISSING procedures (in body, not in original catalog):*

| Procedure / Function | Signature (confirmed) | Returns | Description | Defects |
|---|---|---|---|---|
| calculate_business_days | p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL | NUMBER | Counts weekdays excluding HOLIDAYS entries for the location (or global holidays where LOCATION_CODE IS NULL) | **BUG confirmed in source comment:** does not handle "observed" holidays (e.g. if July 4 falls Saturday, observed Friday is not excluded) |
| check_leave_overlap | p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL | BOOLEAN | Returns TRUE if any PENDING or APPROVED leave exists overlapping the requested dates | None |
| adjust_leave_balance | p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — | Adds p_adjustment to LEAVE_BALANCES.ADJUSTMENT column; initializes balance record if not found | None |
| get_pending_requests | p_cursor OUT t_leave_cursor, p_approver_id NUMBER | — | Returns PENDING leave requests for a given approver_emp_id, ordered by CREATED_DATE | None |
| get_team_calendar | p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE | — | Returns APPROVED/TAKEN leave for all direct reports of p_manager_id within the date range | None |
| expire_carryover | p_user VARCHAR2 DEFAULT USER | — | Sets CARRYOVER_FROM_PREV=0 and subtracts from ADJUSTMENT for records where CARRYOVER_EXPIRY_DT ≤ SYSDATE | **BUG confirmed in source comment:** if run twice on same day, can double-subtract carryover |

*submit_leave_request implementation details (confirmed from PKG_LEAVE.pkb):*
- Validates EMPLOYMENT_STATUS='ACTIVE' on employee
- Checks minimum tenure: `SYSDATE - HIRE_DATE < MIN_TENURE_DAYS` (raises -20203)
- Backdating rule: allows up to 5 days in the past; raises -20211 if older
- Half-day requests set TOTAL_DAYS=0.5 (skip business day calculation)
- Auto-approves if LEAVE_TYPES.REQUIRES_APPROVAL='N' (calls approve_leave_request immediately)
- Manager notification sent only if REQUIRES_APPROVAL='Y'
- Error codes: -20201 insufficient balance, -20202 overlap, -20203 invalid type/tenure, -20210 date order, -20211 too far back, -20212 no business days

*run_monthly_accrual batch details (confirmed):*
- Commits every 100 employees (not every employee)
- Checks LEAVE_TYPES.MIN_TENURE_DAYS before accruing
- Respects MAX_BALANCE cap (accrues partial amount up to cap)
- Calls initialize_balances if no balance record exists for the year
- Writes LEAVE_ACCRUAL_LOG entry for every accrual event

[SUPPLEMENTED] **Leave type seed data (from 01_reference_data.sql):**

| ID | Code | Name | Accrual | Rate/Period | Max Balance | Carryover Max | Min Tenure |
|---|---|---|---|---|---|---|---|
| 1 | PTO | Paid Time Off | MONTHLY | 1.25 days | 20 days | 5 days (expire 3 months) | 0 |
| 2 | SICK | Sick Leave | MONTHLY | 0.833 days | 10 days | 10 days (no expiry) | 0 |
| 3 | COMP | Compensatory Time | None | — | — | 0 | 90 days |
| 4 | FMLA | Family Medical Leave | None | — | — | 0 | 365 days |
| 5 | JURY | Jury Duty | None | — | — | 0 | 0 |
| 6 | BEREAVE | Bereavement | None | — | — | 0 | 0 |

[SUPPLEMENTED] **Leave table DDL confirmed (from 03_leave_tables.sql):**
- LEAVE_BALANCES.AVAILABLE is a virtual (generated) column: `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING`
- LEAVE_REQUESTS.STATUS constraint: `('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'TAKEN')`
- LEAVE_REQUESTS supports half-day requests (HALF_DAY_FLAG, HALF_DAY_PERIOD AM/PM)
- LEAVE_ACCRUAL_LOG table tracks every accrual event with BALANCE_AFTER snapshot
- HOLIDAYS table supports location-specific holidays (LOCATION_CODE nullable) and floating holidays

---

## PACKAGE: PKG_PERFORMANCE
**Domain:** BC-04 Performance Management
**Schema:** HRMS
**Dependencies:** PKG_AUDIT, PKG_NOTIFICATION
**Tables Owned:** PERFORMANCE_REVIEWS, PERFORMANCE_GOALS, REVIEW_CYCLES
**Tables Read:** EMPLOYEES, JOB_TITLES, DEPARTMENTS

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| create_review_cycle | p_cycle_name VARCHAR2, p_cycle_year NUMBER, p_start_date DATE, p_end_date DATE, p_self_review_due DATE, p_manager_review_due DATE, p_user VARCHAR2 | NUMBER (CYCLE_ID) | Creates REVIEW_CYCLES row in DRAFT status; calls PKG_AUDIT | Employees with NULL MANAGER_ID get no review (top of org — intended or gap) |
| open_review_cycle | p_cycle_id NUMBER, p_user VARCHAR2 | — | Sets REVIEW_CYCLES.STATUS='OPEN'; raises -20401 if not in DRAFT | None |
| close_review_cycle | p_cycle_id NUMBER, p_user VARCHAR2 | — | Sets REVIEW_CYCLES.STATUS='CLOSED' | None |
| create_review | p_cycle_id NUMBER, p_emp_id NUMBER, p_reviewer_emp_id NUMBER, p_user VARCHAR2 | NUMBER (REVIEW_ID) | Creates PERFORMANCE_REVIEWS row (NOT_STARTED); sends 'Performance Review Initiated' email to employee | None |
| submit_self_assessment | p_review_id NUMBER, p_self_assessment CLOB, p_user VARCHAR2 | — | Sets SELF_ASSESSMENT on PERFORMANCE_REVIEWS, advances STATUS to MANAGER_REVIEW; notifies manager | Raises -20402 if review not in NOT_STARTED or SELF_REVIEW |
| submit_manager_review | p_review_id NUMBER, p_overall_rating NUMBER, p_manager_assessment CLOB, p_strengths CLOB, p_improvement_areas CLOB, p_development_plan CLOB, p_user VARCHAR2 | — | Sets OVERALL_RATING, RATING_LABEL, assessments, STATUS='COMPLETED'; notifies employee | Raises -20403 if rating not 1.0–5.0 |
| acknowledge_review | p_review_id NUMBER, p_emp_comments CLOB, p_user VARCHAR2 | — | Sets EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE, STATUS='ACKNOWLEDGED' | None |
| add_goal | p_review_id NUMBER, p_emp_id NUMBER, p_goal_title VARCHAR2, p_goal_description CLOB, p_goal_category VARCHAR2, p_weight_pct NUMBER, p_target_date DATE, p_user VARCHAR2 | NUMBER (GOAL_ID) | Inserts PERFORMANCE_GOALS row (NOT_STARTED, 0% progress) | None |
| update_goal_progress | p_goal_id NUMBER, p_progress_pct NUMBER, p_status VARCHAR2, p_comments CLOB, p_user VARCHAR2 | — | Updates PROGRESS_PCT; auto-advances STATUS to IN_PROGRESS or COMPLETED based on percentage | None |
| get_team_reviews | p_cursor OUT t_review_cursor, p_manager_id NUMBER, p_cycle_id NUMBER | (cursor) | Returns all reviews where REVIEWER_EMP_ID = manager, with employee name, job, dept, status, rating | None |
| get_rating_distribution | p_cycle_id NUMBER, p_dept_id NUMBER | SYS_REFCURSOR | Returns count and percentage per RATING_LABEL for a cycle, optionally filtered by department | None |
| generate_reviews_for_cycle | p_cycle_id NUMBER, p_user VARCHAR2 | — | Bulk-creates reviews for all ACTIVE employees who have a MANAGER_EMP_ID; skips DUP_VAL_ON_INDEX (idempotent); commits | None |

[SUPPLEMENTED] **MISSING procedures confirmed from PKG_PERFORMANCE.pkb:**

`generate_reviews_for_cycle` was missing from the original catalog and is now confirmed above. Additionally:
- `get_rating_distribution` — confirmed as a FUNCTION returning SYS_REFCURSOR (not a procedure), using `SUM(COUNT(*)) OVER ()` analytic for percentage calculation, ordering by `MIN(OVERALL_RATING) DESC`
- `create_review` — sends 'Performance Review Initiated' email to employee via PKG_NOTIFICATION at creation time (not when cycle opens)
- `submit_manager_review` — also sends notification to employee upon completion
- `open_review_cycle` — raises -20401 if cycle STATUS != 'DRAFT' (not if already OPEN)
- No `calibrate_rating` procedure exists in the sourced body — MISS-09 confirmed

[SUPPLEMENTED] **Rating label mapping (confirmed from PKG_PERFORMANCE.pkb):**
| Score | Label |
|---|---|
| ≥ 4.5 | Exceptional |
| 3.5 – 4.49 | Exceeds Expectations |
| 2.5 – 3.49 | Meets Expectations |
| 1.5 – 2.49 | Needs Improvement |
| < 1.5 | Unsatisfactory |

[SUPPLEMENTED] **Review lifecycle states (confirmed from source):** NOT_STARTED → SELF_REVIEW → MANAGER_REVIEW → COMPLETED → ACKNOWLEDGED. Review cycle states: DRAFT → OPEN → CLOSED.

[SUPPLEMENTED] **Note on original catalog:** Original catalog listed `calibrate_review` as a stub. The sourced PKG_PERFORMANCE.pkb does not include this procedure — confirming it is absent (MISS-09 validated). Original catalog also listed `PERFORMANCE_COMPETENCIES` as a table owned; this is not confirmed in the sourced body. REVIEW_CYCLES is confirmed as a table owned.

---

## PACKAGE: PKG_SECURITY
**Domain:** BC-05 Security and Identity
**Schema:** HRMS
**Dependencies:** PKG_AUDIT, DBMS_CRYPTO
**Tables Owned:** USER_ACCOUNTS, USER_ROLES, USER_SESSIONS
**Tables Read:** EMPLOYEES, ROLES, PERMISSIONS, ROLE_PERMISSIONS, SYSTEM_PARAMETERS

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| authenticate | p_username VARCHAR2, p_password VARCHAR2 | p_session_id OUT VARCHAR2, p_user_id OUT NUMBER | Retrieves USER_ACCOUNTS by username; BROKEN: does not validate password; returns session for any input | DEFECT-03: any password authenticates |
| check_session | p_session_id VARCHAR2 | BOOLEAN | Checks USER_SESSIONS.ACTIVE_FLAG='Y' and LAST_ACTIVITY within 30 minutes; updates LAST_ACTIVITY | None |
| check_permission | p_session_id VARCHAR2, p_permission_name VARCHAR2 | BOOLEAN | Grade-based override (≥8=full, 5-7=VIEW only) then role/permission check via USER_ROLES + ROLE_PERMISSIONS | None |
| logout | p_session_id VARCHAR2 | — | Sets USER_SESSIONS.ACTIVE_FLAG='N'; calls PKG_AUDIT.log_action | None |
| change_password | p_user_id NUMBER, p_old_password VARCHAR2, p_new_password VARCHAR2 | — | Hashes new password with MD5; updates USER_ACCOUNTS.PASSWORD_HASH | DEFECT-04: MD5 is cryptographically broken |
| encrypt_data | p_plaintext VARCHAR2 | VARCHAR2 | AES-256 CBC PKCS5 via DBMS_CRYPTO; key hardcoded: `HR$ystem_3ncrypt10n_K3y_2024!!` | DEFECT-05: hardcoded key |
| decrypt_data | p_ciphertext VARCHAR2 | VARCHAR2 | Reverses encrypt_data | DEFECT-05: hardcoded key |
| create_user_account | p_emp_id NUMBER, p_username VARCHAR2, p_initial_password VARCHAR2 | p_user_id OUT NUMBER | Creates USER_ACCOUNTS row; hashes password with MD5 | DEFECT-04: MD5 |
| lock_account | p_user_id NUMBER | — | Sets USER_ACCOUNTS.ACCOUNT_STATUS='LOCKED' | None |
| assign_role | p_user_id NUMBER, p_role_id NUMBER, p_assigned_by VARCHAR2 | — | Inserts USER_ROLES row | None |

[SUPPLEMENTED] **CORRECTIONS and CONFIRMED DETAILS — PKG_SECURITY.pkb now sourced:**

*Table ownership correction:* PKG_SECURITY writes to USER_SESSIONS, NOT USER_ACCOUNTS or USER_ROLES. `create_user_account`, `lock_account`, and `assign_role` listed above are **NOT in the confirmed package body** — those procedures do not exist in the sourced PKG_SECURITY.

*Confirmed public interface (from PKG_SECURITY.pkb):*

| Procedure / Function | Signature (confirmed) | Returns | Description | Defects |
|---|---|---|---|---|
| authenticate | p_username VARCHAR2, p_password VARCHAR2, p_ip_address VARCHAR2 DEFAULT NULL | NUMBER (SESSION_ID) | Looks up employee by UPPER(EMAIL); creates USER_SESSIONS row; calls PKG_EMPLOYEE.set_session_context; calls PKG_AUDIT.log_action | **CRITICAL DEFECT-03 confirmed:** password parameter is accepted but credential check against USER_CREDENTIALS is noted as stub ("In the real system, passwords are stored in a separate USER_CREDENTIALS table"). Any password succeeds. TOO_MANY_ROWS handled by taking MIN(EMP_ID). |
| logout | p_session_id NUMBER | — | Sets USER_SESSIONS.LOGOUT_TIME=SYSDATE, SESSION_STATUS='CLOSED' | None |
| is_session_valid | p_session_id NUMBER | BOOLEAN | Checks SESSION_STATUS='ACTIVE' and LOGIN_TIME within c_session_timeout_min (30 min); auto-expires timed-out sessions (sets SESSION_STATUS='EXPIRED') | None |
| has_permission | p_emp_id NUMBER, p_module VARCHAR2, p_action VARCHAR2 DEFAULT 'VIEW' | BOOLEAN | Grade-based: GRADE_ID ≥ 8 = full access; GRADE_ID ≥ 5 = VIEW all; everyone can CREATE/VIEW own LEAVE; everyone can VIEW own EMPLOYEE profile | **GAP:** table ROLE_PERMISSIONS not used — permission is grade-only; no fine-grained role assignment |
| encrypt_ssn | p_ssn VARCHAR2 | VARCHAR2 | AES-256 CBC PKCS5 via DBMS_CRYPTO; returns RAWTOHEX of encrypted value | **DEFECT-05 confirmed:** key `HR$ystem_3ncrypt10n_K3y_2024!!` hard-coded as package constant `c_encryption_key RAW(32)` |
| decrypt_ssn | p_encrypted VARCHAR2 | VARCHAR2 | Reverses encrypt_ssn; returns '***DECRYPT_ERROR***' string on exception | DEFECT-05; silently returns error string rather than raising |
| change_password | p_emp_id NUMBER, p_old_password VARCHAR2, p_new_password VARCHAR2 | — | Enforces: length ≥ 8, must contain uppercase, must contain digit; notes actual UPDATE to USER_CREDENTIALS as stub | **DEFECT-04 confirmed:** body comment states this is a stub for the legacy model |
| hash_password | p_password VARCHAR2 | VARCHAR2 | RAWTOHEX(DBMS_CRYPTO.HASH(..., HASH_MD5)) | **DEFECT-04 confirmed:** MD5; source comment: "WEAKNESS: Uses MD5 - should use stronger algorithm" |

[SUPPLEMENTED] **Security vulnerability summary (all confirmed from PKG_SECURITY.pkb source):**

| Severity | Finding | Evidence |
|---|---|---|
| CRITICAL | `authenticate` does not verify password — any password succeeds | Source comment: "passwords are stored in a separate USER_CREDENTIALS table. For this legacy codebase, we simulate authentication" |
| CRITICAL | MD5 used for password hashing | Source comment: "WEAKNESS: Uses MD5 - should use stronger algorithm" |
| CRITICAL | No brute-force protection / account lockout | Source comment: "VULNERABILITY: No brute-force protection (no lockout after N failures)" |
| HIGH | Timing attack in authenticate | Source comment: "VULNERABILITY: Timing attack - different response time for invalid user vs invalid password" |
| HIGH | AES-256 encryption key hard-coded in package source | `c_encryption_key RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!')` |
| HIGH | SMTP uses port 25 (no TLS) — see PKG_NOTIFICATION | Confirmed in PKG_NOTIFICATION.pkb |
| MEDIUM | decrypt_ssn silently returns error string on failure | Exception handler returns literal '***DECRYPT_ERROR***' |
| MEDIUM | has_permission is grade-only — no RBAC table used | ROLE_PERMISSIONS table not queried in body |

---

## PACKAGE: PKG_INTEGRATION
**Domain:** BC-06 Integration Hub
**Schema:** HRMS
**Dependencies:** PKG_AUDIT, PKG_SECURITY (decrypt), UTL_FILE
**Tables Owned:** INTEGRATION_LOG
**Tables Read:** PAYROLL_RECORDS, EMPLOYEES, EMPLOYEE_DEPENDENTS, DEPARTMENTS

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| export_gl_journal | p_fiscal_year NUMBER, p_fiscal_period NUMBER | p_record_count OUT NUMBER | Queries PAYROLL_RECORDS; writes pipe-delimited .dat file to GL_OUTPUT_DIR via UTL_FILE; inserts INTEGRATION_LOG | No retry logic (MISS-14); no ACK from GL (OQ-008) |
| export_benefits_feed | (none) | p_record_count OUT NUMBER | Queries EMPLOYEES + EMPLOYEE_DEPENDENTS; decrypts SSN; writes 203-char fixed-width file to BENEFITS_FEED_OUT via UTL_FILE; inserts INTEGRATION_LOG | No retry (MISS-14); no ADP ACK (OQ-009); no ROLLBACK on exception |
| import_time_attendance | p_file_name VARCHAR2 | p_records_loaded OUT NUMBER | STUB — procedure exists but reads no file and performs no processing | DEFECT-12: T&A integration non-functional |
| sync_ldap_directory | (none) | — | STUB — procedure exists but performs no LDAP operations | DEFECT-13: LDAP sync non-functional |
| get_integration_status | p_source VARCHAR2, p_direction VARCHAR2, p_from_date DATE | SYS_REFCURSOR | Returns INTEGRATION_LOG rows for monitoring | None |

[SUPPLEMENTED] **CORRECTIONS — PKG_INTEGRATION.pkb now confirmed:**

*Table/column name corrections:*
- Source reads from `PAYROLL_DETAILS` (not `PAYROLL_RECORDS`) for GL journal generation
- Source reads `DEPARTMENTS.COST_CENTER` and `PAY_ELEMENTS.GL_ACCOUNT_CODE` for GL entries
- Source writes GL entries as pipe-delimited `H|` (header) / `D|` (detail) / `T|` (trailer) records, NOT the format described in original catalog
- `INTEGRATION_LOG` table referenced in original catalog — **NOT confirmed in any sourced DDL**; may not exist; package uses `PKG_COMMON.log_info` for logging instead

*Confirmed function signatures (corrections):*
- `generate_gl_journal(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)` — parameter is RUN_ID, not FISCAL_YEAR/PERIOD
- `export_benefits_feed(p_effective_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER)` — no OUT parameters; count logged via PKG_COMMON
- `import_time_attendance(p_file_name VARCHAR2, p_user VARCHAR2 DEFAULT USER)` — confirmed STUB; reads file lines but comment says "TODO: Implement actual parsing"
- `sync_org_structure(p_user VARCHAR2 DEFAULT USER)` — confirmed STUB; only calls PKG_COMMON.log_info
- `get_integration_status(p_integration_name VARCHAR2)` — single parameter (not 3); delegates to `PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS')`

*GL file format confirmed (from source):*
- Directory object: `GL_FEED_OUT`
- Filename: `GL_JOURNAL_<RUN_ID>_<YYYYMMDD>.dat`
- Header: `H|HRMS_PAYROLL|<date>|<run_id>`
- Detail: `D|<cost_center>|<gl_account>|<debit>|<credit>|<description>|RUN-<run_id>`
- Trailer: `T|<entry_count>`

*Benefits feed confirmed (from source):*
- Directory object: `BENEFITS_FEED_OUT`
- Filename: `BENEFITS_<YYYYMMDD>.txt`
- Joins EMPLOYEES with EMPLOYEE_DEPENDENTS (LEFT JOIN, one row per dependent relationship)
- Fixed-width: EmpNum(10) | FirstName(30) | LastName(30) | DOB(10) | HireDate(10) | Status(12) | MaritalStatus(10) | Gender(1) | DepFirstName(30) | DepLastName(30) | Relationship(20) | DepDOB(10)
- **SECURITY GAP confirmed:** no SSN in this feed (decryption is NOT called here — original catalog IFACE-02 field layout was incorrect); SSN exclusion may be intentional or an oversight

---

## PACKAGE: PKG_NOTIFICATION
**Domain:** BC-08 Notification
**Schema:** HRMS
**Dependencies:** UTL_SMTP, UTL_TCP, PKG_COMMON (log_error/log_info)
**Tables Owned:** NOTIFICATION_QUEUE
**Tables Read:** EMPLOYEES, SYSTEM_PARAMETERS

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| send_notification | p_recipient_emp_id NUMBER, p_recipient_email VARCHAR2, p_type VARCHAR2, p_subject VARCHAR2, p_body CLOB, p_priority NUMBER, p_reference_table VARCHAR2, p_reference_id NUMBER, p_user VARCHAR2 | — | Uses PRAGMA AUTONOMOUS_TRANSACTION; resolves email from EMP_ID if not provided; inserts NOTIFICATION_QUEUE row (PENDING); errors are caught and logged — never propagate to caller | **OQ-007 supplement:** no template system — callers pass subject/body directly; variable substitution is caller responsibility |
| process_queue | p_batch_size NUMBER, p_user VARCHAR2 | — | Fetches up to batch_size PENDING EMAIL notifications; opens individual UTL_SMTP connections per message; marks SENT or FAILED with RETRY_COUNT increment; commits after loop | **DEFECT-14:** UTL_SMTP port 25, no TLS; **PERF:** one SMTP connection per message (no connection reuse) |
| retry_failed | p_max_retries NUMBER, p_user VARCHAR2 | — | Resets FAILED notifications back to PENDING where RETRY_COUNT < max_retries | None |
| cancel_notification | p_notification_id NUMBER, p_user VARCHAR2 | — | Sets STATUS='CANCELLED' for PENDING notifications | None |

[SUPPLEMENTED] *PKG_NOTIFICATION body fully sourced (PKG_NOTIFICATION.pkb). Key corrections from original catalog:*
- *Table owned is NOTIFICATION_QUEUE, not NOTIFICATION_LOG*
- *No NOTIFICATION_TEMPLATES table used — body/subject passed directly by callers (resolves OQ-007: no template variable substitution mechanism exists)*
- *SMTP config is hard-coded as package constants (`smtp.internal.company.com`, port 25, `hrms-noreply@company.com`) — also stored in SYSTEM_PARAMETERS (param_ids 7–8) but the package does NOT read them; the constants are a maintenance risk*
- *send_notification uses PRAGMA AUTONOMOUS_TRANSACTION (notification failures never block business operations)*
- *process_queue is called by DBMS_SCHEDULER job every 5 minutes (confirmed in source comment)*

[SUPPLEMENTED] **SMTP constants (hard-coded in package, not read from SYSTEM_PARAMETERS):**
- c_smtp_host: `smtp.internal.company.com`
- c_smtp_port: 25
- c_from_address: `hrms-noreply@company.com`
- c_from_name: `HRMS System`

---

## PACKAGE: PKG_REPORTING
**Domain:** BC-09 Reporting and Analytics
**Schema:** HRMS
**Dependencies:** PKG_SECURITY (permission check), PKG_AUDIT
**Tables Owned:** RPT_* output tables (7 inferred — ASMP-005)
**Tables Read:** All VW_* views, AUDIT_LOG, PAYROLL_RECORDS, EMPLOYEES

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| headcount_report | p_dept_id NUMBER, p_as_of_date DATE | SYS_REFCURSOR | Returns active employee counts from VW_DEPARTMENT_HEADCOUNT | None |
| payroll_summary_report | p_fiscal_year NUMBER, p_fiscal_period NUMBER | SYS_REFCURSOR | Returns aggregated payroll data from VW_PAYROLL_SUMMARY | None |
| leave_balance_report | p_emp_id NUMBER, p_year NUMBER | SYS_REFCURSOR | Returns leave balances from VW_LEAVE_SUMMARY | DEFECT-08: VW_LEAVE_SUMMARY AVAILABLE formula incorrect (DISC-003) |
| performance_report | p_period_start DATE, p_period_end DATE | SYS_REFCURSOR | Returns performance data from VW_PERFORMANCE_SUMMARY | None |
| org_chart_report | p_root_emp_id NUMBER | SYS_REFCURSOR | Returns hierarchical org tree from VW_ORG_HIERARCHY | None |
| employee_detail_report | p_dept_id NUMBER, p_status VARCHAR2 | SYS_REFCURSOR | Returns employee details from VW_EMPLOYEE_DETAILS | None |
| audit_trail_report | p_table_name VARCHAR2, p_record_id NUMBER, p_days NUMBER | SYS_REFCURSOR | Returns AUDIT_LOG rows for specified object and retention window | None |
| salary_band_report | p_grade NUMBER | SYS_REFCURSOR | Returns employees with salary vs. GRADES.MIN/MAX_SALARY bands | None |

[SUPPLEMENTED] **CORRECTIONS — PKG_REPORTING.pkb now confirmed:**

*Procedure name corrections — original catalog names do NOT match confirmed body:*
- `headcount_report` — correct name confirmed; signature corrected: `headcount_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE, p_dept_id NUMBER DEFAULT NULL, p_location VARCHAR2 DEFAULT NULL)`. Does NOT read VW_DEPARTMENT_HEADCOUNT; queries EMPLOYEES directly with dept/location filters.
- `payroll_summary_report` — correct name confirmed; signature corrected: parameter is `p_period_id NUMBER`, not FISCAL_YEAR/PERIOD. Does NOT read VW_PAYROLL_SUMMARY; queries PAYROLL_DETAILS/PAYROLL_RUNS directly.
- `leave_balance_report` — **NOT in confirmed body**. Equivalent is `leave_utilization_report(p_cursor OUT t_report_cursor, p_year NUMBER DEFAULT ..., p_dept_id NUMBER DEFAULT NULL)`. Reads LEAVE_BALANCES joined to EMPLOYEES/DEPARTMENTS/LEAVE_TYPES (not VW_LEAVE_SUMMARY).
- `performance_report` — **NOT in confirmed body**. Use PKG_PERFORMANCE.get_team_reviews / get_rating_distribution instead.
- `org_chart_report` — **NOT in confirmed body**. Use VW_ORG_HIERARCHY or PKG_EMPLOYEE.get_org_chart instead.
- `employee_detail_report` — **NOT in confirmed body**. Closest equivalent is `new_hires_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)`.
- `audit_trail_report` — **NOT in confirmed body**. Use PKG_AUDIT.get_change_history instead.
- `salary_band_report` — **NOT in confirmed body**. Equivalent is `compensation_summary(p_cursor OUT t_report_cursor, p_dept_id NUMBER DEFAULT NULL, p_grade_id NUMBER DEFAULT NULL)`.

*Confirmed procedures from PKG_REPORTING.pkb:*

| Procedure | Confirmed Parameters | Description |
|---|---|---|
| headcount_report | p_cursor OUT, p_as_of_date DATE, p_dept_id NUMBER, p_location VARCHAR2 | Active headcount by dept/location with FT/PT/Contract, gender counts, avg tenure |
| compensation_summary | p_cursor OUT, p_dept_id NUMBER, p_grade_id NUMBER | Min/max/avg/median salary and compa-ratio vs grade midpoint by dept and grade |
| turnover_report | p_cursor OUT, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER | Termination count, voluntary/involuntary split, avg tenure at exit, turnover % |
| new_hires_report | p_cursor OUT, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER | New hire details: name, dept, job, location, type, salary, manager name |
| leave_utilization_report | p_cursor OUT, p_year NUMBER, p_dept_id NUMBER | Avg entitled/used/remaining and utilization % per leave type per dept |
| payroll_summary_report | p_cursor OUT, p_period_id NUMBER | Gross/fed-tax/state-tax/SS/Medicare/deductions/net per department |
| eeo_compliance_report | p_cursor OUT, p_as_of_date DATE | EEO category breakdown by gender and not-disclosed counts with female % |
| refresh_reporting_tables | p_user VARCHAR2 DEFAULT USER | **STUB** — calls PKG_COMMON.log_info only; RPT_* table population not implemented |

[SUPPLEMENTED] **Views confirmed from hrms_views.sql:**

| View | Purpose | Notable |
|---|---|---|
| VW_ACTIVE_EMPLOYEES | Denormalized active employee lookup with dept, job, manager, location, salary | Used by most LOVs and list screens |
| VW_ORG_HIERARCHY | Hierarchical org chart via CONNECT BY | **OQ-013 confirmed:** source comment warns performance degrades with >500 employees |
| VW_EMPLOYEE_COMPENSATION | Current salary with compa-ratio vs grade midpoint | Includes CHANGE_REASON and CHANGE_PCT from last salary action |
| VW_LEAVE_SUMMARY | Current year leave balances with utilization % | AVAILABLE formula in view recalculates independently of virtual column — potential DISC-003 source |
| VW_PAYROLL_LATEST | Latest approved payroll run breakdown per employee | Subquery on MAX(RUN_ID) with STATUS='APPROVED' |
| VW_PENDING_APPROVALS | Unified pending-approval view across LEAVE and PERFORMANCE modules | UNION ALL of LEAVE_REQUESTS (PENDING) and PERFORMANCE_REVIEWS (MANAGER_REVIEW) |

---

## PACKAGE: PKG_AUDIT
**Domain:** BC-07 Audit and Compliance
**Schema:** HRMS
**Key Feature:** All procedures use PRAGMA AUTONOMOUS_TRANSACTION — audit entries survive ROLLBACK in calling transaction
**Tables Owned:** AUDIT_LOG
**Tables Read:** None

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| log_action | p_table_name VARCHAR2, p_record_id NUMBER, p_action VARCHAR2, p_old_value VARCHAR2, p_new_value VARCHAR2 | — | Inserts AUDIT_LOG row with AUTONOMOUS_TRANSACTION; captures SESSION_USER and SYSDATE | SEQ_AUDIT CACHE 100 — gap risk after instance restart |
| purge_old_records | p_retention_days NUMBER | p_purged_count OUT NUMBER | Deletes AUDIT_LOG rows older than p_retention_days (default 365 — BR-107) | Scheduler job not confirmed (OQ-012) |
| get_audit_trail | p_table_name VARCHAR2, p_record_id NUMBER | SYS_REFCURSOR | Returns AUDIT_LOG rows for a specific record | None |

[SUPPLEMENTED] **CORRECTIONS — PKG_AUDIT.pkb now confirmed:**

*Signature corrections:*
- `log_action` actual signature: `log_action(p_table_name VARCHAR2, p_record_id NUMBER, p_action VARCHAR2, p_user VARCHAR2 DEFAULT USER, p_old_values CLOB DEFAULT NULL, p_new_values CLOB DEFAULT NULL)` — parameters are named `p_old_values`/`p_new_values` (CLOB, not VARCHAR2), and `p_user` (not `p_old_value`/`p_new_value`)
- `purge_old_records` actual signature: `purge_old_records(p_days_to_keep NUMBER DEFAULT 365, p_user VARCHAR2 DEFAULT USER)` — no OUT parameter; purge count printed to DBMS_OUTPUT only
- `get_audit_trail` — confirmed as `get_change_history(p_table_name VARCHAR2, p_record_id NUMBER, p_from_date DATE DEFAULT NULL, p_to_date DATE DEFAULT NULL) RETURN SYS_REFCURSOR`; function not procedure; returns rows ordered by CHANGED_DATE DESC

*PKG_COMMON.log_error re-use:* PKG_AUDIT body does NOT call PKG_COMMON for error logging. On exception in log_action, it silently does ROLLBACK with no re-raise (by design — audit must never fail the caller).

*Additional audit context captured (from source):*
- AUDIT_LOG.IP_ADDRESS: `SYS_CONTEXT('USERENV', 'IP_ADDRESS')`
- AUDIT_LOG.SESSION_ID: `SYS_CONTEXT('USERENV', 'SESSIONID')`
- Both captured at INSERT time, not passed by caller

*PKG_COMMON.log_error writes to AUDIT_LOG (not a separate table):* error entries use TABLE_NAME='ERROR_LOG', RECORD_ID=0, ACTION_TYPE='INSERT', with JSON-formatted message in NEW_VALUES column.

---

## PACKAGE: PKG_COMMON
**Domain:** BC-10 System Administration (shared utilities)
**Schema:** HRMS
**Tables Read:** SYSTEM_PARAMETERS, LOOKUP_VALUES

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| get_parameter | p_param_key VARCHAR2 | VARCHAR2 | Returns SYSTEM_PARAMETERS.PARAM_VALUE for given key | None |
| get_lookup_values | p_lookup_type VARCHAR2 | SYS_REFCURSOR | Returns active LOOKUP_VALUES rows for a given type | None |
| get_lookup_value | p_lookup_type VARCHAR2, p_lookup_code VARCHAR2 | VARCHAR2 | Returns display value for a single code | None |
| get_fiscal_year | p_date DATE | NUMBER | Returns fiscal year number (FY starts October: Oct 2024 = FY2025) | None |
| get_fiscal_period | p_date DATE | NUMBER | Returns period within fiscal year (October = period 1) | None |
| format_currency | p_amount NUMBER | VARCHAR2 | Formats number as USD currency string | None |
| calculate_tenure_days | p_hire_date DATE, p_as_of_date DATE | NUMBER | Returns days between hire date and as_of_date | None |

[SUPPLEMENTED] **CORRECTIONS and MISSING procedures — PKG_COMMON.pkb now confirmed:**

*Signature corrections:*
- `get_parameter` — actual name is `get_param(p_group VARCHAR2, p_code VARCHAR2)`. Two-parameter lookup: PARAM_GROUP + PARAM_CODE (not a single key). Also confirmed: `get_param_number` and `get_param_date` wrappers.
- `set_system_parameter` — actual name is `set_param(p_group VARCHAR2, p_code VARCHAR2, p_value VARCHAR2, p_user VARCHAR2 DEFAULT USER)`. Raises -20900 if param not found or EDITABLE_FLAG='N'.
- `format_currency` — actual signature: `format_currency(p_amount NUMBER, p_currency_code VARCHAR2 DEFAULT 'USD')`. Handles USD ($), EUR (€), GBP (£), others (code prefix).
- `calculate_tenure_days` — **NOT in PKG_COMMON.pkb**. Not confirmed.

*Confirmed MISSING procedures (in body, not in original catalog):*

| Procedure / Function | Signature (confirmed) | Returns | Description |
|---|---|---|---|
| log_info | p_package VARCHAR2, p_procedure VARCHAR2, p_message VARCHAR2, p_user VARCHAR2 DEFAULT USER | — | PRAGMA AUTONOMOUS_TRANSACTION; writes INFO_LOG entry to AUDIT_LOG with TABLE_NAME='INFO_LOG', ACTION_TYPE='INSERT'; JSON-formatted message in NEW_VALUES |
| business_days_between | p_start_date DATE, p_end_date DATE | NUMBER | Counts weekdays (Mon–Fri) between two dates; does NOT exclude holidays (use PKG_LEAVE.calculate_business_days for holiday-aware version) |
| add_business_days | p_date DATE, p_days NUMBER | DATE | Returns date that is p_days business days after p_date; skips weekends |
| get_fiscal_year | p_date DATE DEFAULT SYSDATE | NUMBER | Fiscal year starts Oct 1: Oct 2024 → FY2025 (returns YEAR+1 if MONTH≥10) |
| get_fiscal_quarter | p_date DATE DEFAULT SYSDATE | NUMBER | Returns 1–4: Q1=Oct-Dec, Q2=Jan-Mar, Q3=Apr-Jun, Q4=Jul-Sep |
| format_phone | p_phone VARCHAR2 | VARCHAR2 | Strips non-digits; formats as (NNN) NNN-NNNN (10-digit) or +1 (NNN) NNN-NNNN (11-digit); returns raw input otherwise |
| format_ssn_masked | p_ssn VARCHAR2 | VARCHAR2 | Returns '***-**-NNNN' (last 4 digits only) |
| format_name | p_first_name VARCHAR2, p_last_name VARCHAR2, p_format VARCHAR2 DEFAULT 'FL' | VARCHAR2 | 'FL'=First Last, 'LF'=Last, First; applies INITCAP |
| is_valid_email | p_email VARCHAR2 | BOOLEAN | REGEXP_LIKE against standard email pattern |
| is_valid_phone | p_phone VARCHAR2 | BOOLEAN | Returns TRUE if stripped digits length is 10 or 11 |
| is_valid_ssn | p_ssn VARCHAR2 | BOOLEAN | Returns TRUE if stripped digits = exactly 9 |

[SUPPLEMENTED] **SYSTEM_PARAMETERS seed data (from 01_reference_data.sql):**

| ID | Group | Code | Value | Editable |
|---|---|---|---|---|
| 1 | SYSTEM | APP_VERSION | 4.2.0 | N |
| 2 | SYSTEM | COMPANY_NAME | Acme Corporation | Y |
| 3 | PAYROLL | DEFAULT_PAY_FREQUENCY | MONTHLY | Y |
| 4 | PAYROLL | FISCAL_YEAR_START | 10 (October) | Y |
| 5 | SECURITY | SESSION_TIMEOUT_MIN | 30 | Y |
| 6 | SECURITY | PASSWORD_MIN_LENGTH | 8 | Y |
| 7 | NOTIFICATION | SMTP_HOST | smtp.internal.company.com | Y |
| 8 | NOTIFICATION | FROM_ADDRESS | hrms-noreply@company.com | Y |
| 9 | INTEGRATION | GL_FEED_STATUS | ACTIVE | Y |
| 10 | INTEGRATION | BENEFITS_FEED_STATUS | ACTIVE | Y |

**Note:** PKG_NOTIFICATION does NOT read SMTP config from SYSTEM_PARAMETERS — it uses hard-coded package constants. Parameters 7–8 are stored but unused by the notification package (maintenance gap).

---

## PACKAGE: PKG_VALIDATION
**Domain:** BC-10 System Administration (validation rules)
**Schema:** HRMS
**Library counterpart:** HRMS_VALIDATION_LIB (client-side PLL)
**Tables Read:** EMPLOYEES, GRADES, DEPARTMENTS, LEAVE_TYPES

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| validate_employee_data | p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_grade NUMBER, p_dept_id NUMBER, p_salary NUMBER | BOOLEAN | Server-side validation: hire_date within 180 days (DISC-001 — intentional layered rule), grade exists, dept exists, salary > 0 | None |
| validate_leave_request | p_emp_id NUMBER, p_leave_type_id NUMBER, p_days_requested NUMBER, p_start_date DATE | BOOLEAN | Checks status ACTIVE, tenure gates, balance availability | None |
| validate_payroll_period | p_period_start DATE, p_period_end DATE, p_fiscal_year NUMBER | BOOLEAN | Checks period does not overlap existing PROCESSED payroll run | None |
| validate_salary_change | p_emp_id NUMBER, p_new_salary NUMBER, p_grade NUMBER | BOOLEAN | Checks new salary within GRADES.MIN_SALARY and MAX_SALARY band | None |
| validate_rating | p_rating NUMBER | BOOLEAN | Returns TRUE if rating between 1.0 and 5.0 (BR-93) | None |

[SUPPLEMENTED] **CORRECTIONS and CONFIRMED INTERFACE — PKG_VALIDATION.pks now sourced:**

*Signature corrections — the following procedure names in the original catalog do NOT match the confirmed spec:*
- `validate_employee_data` — **NOT in spec**; not confirmed
- `validate_leave_request` — **NOT in spec** by this name; not confirmed
- `validate_payroll_period` — **NOT in spec**; not confirmed
- `validate_salary_change` — **NOT in spec** by this name

*Confirmed public interface (from PKG_VALIDATION.pks):*

| Procedure / Function | Signature (confirmed) | Returns | Description |
|---|---|---|---|
| validate_date_range | p_start_date DATE, p_end_date DATE | BOOLEAN | Returns TRUE if start_date ≤ end_date |
| validate_salary_for_grade | p_salary NUMBER, p_grade_id NUMBER | VARCHAR2 | Returns NULL if salary within JOB_GRADES.MIN_SALARY..MAX_SALARY; returns error message string if invalid (not BOOLEAN) |
| validate_email_format | p_email VARCHAR2 | BOOLEAN | Delegates to PKG_COMMON.is_valid_email |
| validate_phone_format | p_phone VARCHAR2 | BOOLEAN | Delegates to PKG_COMMON.is_valid_phone |
| validate_emp_number_format | p_emp_number VARCHAR2 | BOOLEAN | Checks format matches EMP-NNNNNN pattern |
| is_future_date | p_date DATE | BOOLEAN | Returns TRUE if p_date > SYSDATE |
| is_business_day | p_date DATE, p_location_code VARCHAR2 DEFAULT NULL | BOOLEAN | Returns TRUE if date is a weekday and not in HOLIDAYS table for given location |
| validate_required_fields | p_table_name VARCHAR2, p_record_id NUMBER | VARCHAR2 | Returns NULL if all required fields populated; returns list of missing field names if not |

*Note:* PKG_VALIDATION.pks body was not in the source files provided. The spec above is confirmed; body logic is inferred from the signatures and original catalog context.

---

## DATABASE TRIGGERS

[SUPPLEMENTED] **EMPLOYEES table triggers (confirmed from trg_employees.sql):**

| Trigger | Timing | Event | Purpose | Defects / Notes |
|---|---|---|---|---|
| TRG_EMP_BEFORE_INSERT | BEFORE | INSERT | Sets CREATED_BY/CREATED_DATE if null; defaults ACTIVE_FLAG='Y' and EMPLOYMENT_STATUS='ACTIVE'; validates hire date ≤ SYSDATE+180; validates email uniqueness with friendly error message | Duplicate validation with UK constraint; SELECT inside trigger has performance cost at scale |
| TRG_EMP_BEFORE_UPDATE | BEFORE | UPDATE | Sets MODIFIED_BY/MODIFIED_DATE; blocks direct TERMINATED→ACTIVE reactivation (must use rehire process); auto-inserts EMPLOYEE_HISTORY rows for STATUS_CHANGE, DEPARTMENT_CHANGE, JOB_CHANGE | **DEFECT-02 confirmed:** this trigger fires on ALL updates including transfer_employee and promote_employee — the INSERT INTO EMPLOYEE_HISTORY within the trigger duplicates history inserts that PKG_EMPLOYEE also performs |
| TRG_EMP_INSTEAD_OF_DELETE | BEFORE | DELETE | Raises -20504 to block all direct DELETEs; forces use of termination process or ACTIVE_FLAG='N' | **BUG confirmed in source comment:** Forms expects DELETE to succeed; workaround required in Forms: set ACTIVE_FLAG='N' then CLEAR_RECORD instead of DELETE_RECORD |

---

## SEQUENCES

[SUPPLEMENTED] **All HRMS sequences (confirmed from hrms_sequences.sql):**

| Sequence | Start | Increment | Cache | Purpose |
|---|---|---|---|---|
| SEQ_DEPARTMENT | 100 | 1 | NOCACHE | DEPARTMENTS surrogate key |
| SEQ_LOCATION | 100 | 1 | NOCACHE | LOCATIONS surrogate key |
| SEQ_JOB_GRADE | 100 | 1 | NOCACHE | JOB_GRADES surrogate key |
| SEQ_JOB_TITLE | 100 | 1 | NOCACHE | JOB_TITLES surrogate key |
| SEQ_EMPLOYEE | 10000 | 1 | NOCACHE | EMPLOYEES surrogate key |
| SEQ_EMP_HISTORY | 1 | 1 | NOCACHE | EMPLOYEE_HISTORY surrogate key |
| SEQ_DEPENDENT | 1 | 1 | NOCACHE | EMPLOYEE_DEPENDENTS surrogate key |
| SEQ_EMERGENCY_CONTACT | 1 | 1 | NOCACHE | Emergency contacts surrogate key |
| SEQ_EMP_NUMBER | 1000 | 1 | NOCACHE | **Unused** — PKG_EMPLOYEE uses MAX()+1 instead (race condition risk) |
| SEQ_SALARY | 1 | 1 | NOCACHE | SALARY_RECORDS surrogate key |
| SEQ_PAY_ELEMENT | 1 | 1 | NOCACHE | PAY_ELEMENTS surrogate key |
| SEQ_EMP_PAY_ELEMENT | 1 | 1 | NOCACHE | EMPLOYEE_PAY_ELEMENTS surrogate key |
| SEQ_PAY_PERIOD | 1 | 1 | NOCACHE | PAY_PERIODS surrogate key |
| SEQ_PAYROLL_RUN | 1 | 1 | NOCACHE | PAYROLL_RUNS surrogate key |
| SEQ_PAYROLL_DETAIL | 1 | 1 | NOCACHE | PAYROLL_DETAILS surrogate key |
| SEQ_TAX_BRACKET | 1 | 1 | NOCACHE | TAX_BRACKETS surrogate key |
| SEQ_LEAVE_TYPE | 1 | 1 | NOCACHE | LEAVE_TYPES surrogate key |
| SEQ_LEAVE_BALANCE | 1 | 1 | NOCACHE | LEAVE_BALANCES surrogate key |
| SEQ_LEAVE_REQUEST | 1 | 1 | NOCACHE | LEAVE_REQUESTS surrogate key |
| SEQ_LEAVE_ACCRUAL | 1 | 1 | NOCACHE | LEAVE_ACCRUAL_LOG surrogate key |
| SEQ_HOLIDAY | 1 | 1 | NOCACHE | HOLIDAYS surrogate key |
| SEQ_REVIEW_CYCLE | 1 | 1 | NOCACHE | REVIEW_CYCLES surrogate key |
| SEQ_PERF_REVIEW | 1 | 1 | NOCACHE | PERFORMANCE_REVIEWS surrogate key |
| SEQ_PERF_GOAL | 1 | 1 | NOCACHE | PERFORMANCE_GOALS surrogate key |
| SEQ_AUDIT | 1 | 1 | CACHE 100 | AUDIT_LOG — only cached sequence; gap risk on restart |
| SEQ_NOTIFICATION | 1 | 1 | NOCACHE | NOTIFICATION_QUEUE surrogate key |
| SEQ_USER_SESSION | 1 | 1 | NOCACHE | USER_SESSIONS surrogate key |
| SEQ_SYSTEM_PARAM | 1 | 1 | NOCACHE | SYSTEM_PARAMETERS surrogate key |
| SEQ_LOOKUP | 1 | 1 | NOCACHE | LOOKUP_VALUES surrogate key |

**Note:** All sequences use NOCACHE except SEQ_AUDIT (CACHE 100). NOCACHE prevents sequence gaps but increases redo log volume and contention on high-insert tables. The EMP_NUMBER generation bug (SEQ_EMP_NUMBER unused, MAX()+1 used instead) creates a race condition under concurrent hires.

---

## REFERENCE DATA

[SUPPLEMENTED] **Locations (from 01_reference_data.sql):**

| Code | Name | City | State | Country |
|---|---|---|---|---|
| HQ | Corporate Headquarters | New York | NY | US |
| CHI | Chicago Regional Office | Chicago | IL | US |
| SF | San Francisco Branch | San Francisco | CA | US |

[SUPPLEMENTED] **Departments (from 01_reference_data.sql):**

| ID | Code | Name | Cost Center | Parent | Location |
|---|---|---|---|---|---|
| 1 | EXEC | Executive Office | CC-1000 | — | HQ |
| 10 | HR | Human Resources | CC-1100 | EXEC | HQ |
| 20 | FIN | Finance & Accounting | CC-1200 | EXEC | HQ |
| 30 | IT | Information Technology | CC-1300 | EXEC | CHI |
| 31 | ITDEV | IT - Development | CC-1310 | IT | CHI |
| 32 | ITOPS | IT - Operations | CC-1320 | IT | CHI |
| 40 | SALES | Sales | CC-1400 | EXEC | SF |
| 50 | MKT | Marketing | CC-1500 | EXEC | SF |
| 60 | OPS | Operations | CC-1600 | EXEC | CHI |
| 70 | LEGAL | Legal & Compliance | CC-1700 | EXEC | HQ |

[SUPPLEMENTED] **Job grades (from 01_reference_data.sql):**

| Grade | Name | Min Salary | Max Salary |
|---|---|---|---|
| 1 | Entry Level | $35,000 | $55,000 |
| 2 | Junior | $45,000 | $70,000 |
| 3 | Mid-Level | $60,000 | $90,000 |
| 4 | Senior | $80,000 | $120,000 |
| 5 | Lead | $95,000 | $145,000 |
| 6 | Manager | $110,000 | $170,000 |
| 7 | Senior Manager | $130,000 | $200,000 |
| 8 | Director | $160,000 | $250,000 |
| 9 | VP | $200,000 | $350,000 |
| 10 | C-Suite | $300,000 | $600,000 |

[SUPPLEMENTED] **Pay elements (from 01_reference_data.sql):**

| ID | Code | Name | Type | Calc | Default | Pretax | GL Account |
|---|---|---|---|---|---|---|---|
| 1 | BASE_PAY | Base Salary | EARNING | FLAT | — | N | 5100-100 |
| 100 | FED_TAX | Federal Income Tax | TAX | FORMULA | — | N | 2100-100 |
| 101 | STATE_TAX | State Income Tax | TAX | FORMULA | — | N | 2100-200 |
| 102 | FICA | Social Security (FICA) | TAX | FORMULA | — | N | 2100-300 |
| 103 | MEDICARE | Medicare | TAX | FORMULA | — | N | 2100-400 |
| 200 | 401K_EE | 401(k) Employee Contribution | DEDUCTION | PERCENTAGE | 6% | Y | 2200-100 |
| 201 | MED_EE | Medical Insurance (Employee) | BENEFIT | FLAT | $250 | Y | 2200-200 |
| 202 | DENTAL_EE | Dental Insurance (Employee) | BENEFIT | FLAT | $45 | Y | 2200-300 |
| 203 | VISION_EE | Vision Insurance (Employee) | BENEFIT | FLAT | $15 | Y | 2200-400 |
| 204 | LIFE_INS | Life Insurance | BENEFIT | FLAT | $25 | N | 2200-500 |
| 205 | HSA | Health Savings Account | DEDUCTION | FLAT | $150 | Y | 2200-600 |

---

## ORACLE FORMS MENU

[SUPPLEMENTED] **HRMS_MENU structure (confirmed from HRMS_MENU.mmb.sql):**

| Menu | Item | Action |
|---|---|---|
| File | Save | COMMIT_FORM |
| File | Save & Exit | COMMIT_FORM; EXIT_FORM |
| File | Print | RUN_PRODUCT |
| File | Exit | EXIT_FORM |
| Edit | Clear Record | CLEAR_RECORD |
| Edit | Duplicate Record | DUPLICATE_RECORD |
| Edit | Delete Record | DELETE_RECORD |
| Edit | Insert Record | CREATE_RECORD |
| Query | Enter Query | ENTER_QUERY |
| Query | Execute Query | EXECUTE_QUERY |
| Query | Cancel Query | EXIT_FORM |
| Query | Count Matching | COUNT_QUERY |
| Query | Fetch Next Set | SCROLL_DOWN |
| Navigate | First/Previous/Next/Last Record | FIRST_RECORD / PREVIOUS_RECORD / NEXT_RECORD / LAST_RECORD |
| Navigate | Previous/Next Block | PREVIOUS_BLOCK / NEXT_BLOCK |
| Modules | Employee Management | OPEN_FORM('HRMS_EMPLOYEE') |
| Modules | Payroll Processing | OPEN_FORM('HRMS_PAYROLL') |
| Modules | Leave Management | OPEN_FORM('HRMS_LEAVE') |
| Modules | Performance Reviews | OPEN_FORM('HRMS_PERFORMANCE') |
| Modules | Reports & Analytics | OPEN_FORM('HRMS_REPORTS') |
| Modules | System Admin | OPEN_FORM('HRMS_ADMIN') |
| Admin | Change Password | SHOW_WINDOW('WIN_CHANGE_PWD') |
| Admin | System Parameters | Requires ADMIN permission |
| Admin | User Management | Requires ADMIN permission |
| Help | Contents | WEB.SHOW_DOCUMENT |
| Help | About HRMS | SHOW_ALERT('ALT_ABOUT') |
| Help | Support | WEB.SHOW_DOCUMENT |

**Security:** Menu items enabled/disabled at runtime via PKG_SECURITY.has_permission() checks in WHEN-NEW-FORM-INSTANCE trigger.

---

## EXTERNAL INTERFACES

### IFACE-01: Oracle Financials GL Export
| Attribute | Value |
|---|---|
| Direction | Outbound |
| Protocol | File drop (UTL_FILE to shared directory) |
| Format | Pipe-delimited .dat |
| Frequency | Monthly (post payroll run) |
| Trigger | PKG_INTEGRATION.export_gl_journal |
| Target | Oracle Financials GL (EXT-01) |
| Acknowledgement | None (gap — OQ-008) |
| Error handling | No retry; INTEGRATION_LOG STATUS='FAILED' on exception |

[SUPPLEMENTED] *IFACE-01 corrections confirmed from PKG_INTEGRATION.pkb:*
- *Procedure name is `generate_gl_journal(p_run_id NUMBER, p_user VARCHAR2)`, NOT `export_gl_journal`*
- *Directory object: `GL_FEED_OUT` (not GL_OUTPUT_DIR)*
- *Filename pattern: `GL_JOURNAL_<RUN_ID>_<YYYYMMDD>.dat`*
- *File format: `H|` header / `D|<cost_center>|<gl_account>|<debit>|<credit>|<description>|RUN-<id>` detail / `T|<count>` trailer — three-record-type structure, not flat pipe-delimited*
- *Error handling: UTL_FILE is closed on exception; PKG_COMMON.log_error called; exception re-raised (no INTEGRATION_LOG table used — original catalog incorrect)*

### IFACE-02: ADP Benefits Feed Export
| Attribute | Value |
|---|---|
| Direction | Outbound |
| Protocol | File drop (UTL_FILE to shared directory) |
| Format | Fixed-width 203 characters per record |
| Frequency | Weekly (scheduler) |
| Trigger | PKG_INTEGRATION.export_benefits_feed |
| Target | ADP Benefits Platform (EXT-02) |
| Field layout | SSN(1-9), Name(10-49), DOB(50-59), MaritalStatus(60-61), EmpType(62-63), HireDate(64-73), Salary(74-83), DeptCode(84-93), BenefitPlan(94-123), Coverage(124-133), EffectiveDate(134-143), Dependents(144-203) |
| Acknowledgement | None (gap — OQ-009) |
| Error handling | No retry; no ROLLBACK on file-write exception |

[SUPPLEMENTED] *IFACE-02 corrections confirmed from PKG_INTEGRATION.pkb:*
- *Procedure name is `export_benefits_feed(p_effective_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER)` — confirmed correct*
- *Directory object: `BENEFITS_FEED_OUT`*
- *Filename pattern: `BENEFITS_<YYYYMMDD>.txt`*
- *Actual field layout (confirmed from source — differs from original catalog):* EmpNum(10) | FirstName(30) | LastName(30) | DOB(10) | HireDate(10) | Status(12) | MaritalStatus(10) | Gender(1) | DepFirstName(30) | DepLastName(30) | Relationship(20) | DepDOB(10) — total 166 chars per row (not 203)
- *SSN is NOT in this file — `encrypt_ssn`/`decrypt_ssn` are NOT called in this procedure. Original catalog field layout `SSN(1-9)` was incorrect.*
- *Source queries EMPLOYEE_DEPENDENTS with LEFT JOIN — one row per dependent; employees with no dependents get one row with blank dependent fields*
- *Error handling: UTL_FILE closed on exception; PKG_COMMON.log_error called; exception re-raised*

### IFACE-03: Time and Attendance Inbound (STUB)
| Attribute | Value |
|---|---|
| Direction | Inbound |
| Protocol | File read (UTL_FILE from shared directory) |
| Format | CSV (structure not sourced) |
| Status | STUB — PKG_INTEGRATION.import_time_attendance performs no processing (DEFECT-12) |
| Source | Time & Attendance System (EXT-03) |

### IFACE-04: SMTP Email Notification
| Attribute | Value |
|---|---|
| Direction | Outbound |
| Protocol | UTL_SMTP port 25 |
| Host | smtp.internal.company.com |
| Format | Plain text email (Content-Type: text/plain; charset=UTF-8) |
| Trigger | PKG_NOTIFICATION.send_notification (queues) → process_queue (sends, called by scheduler every 5 minutes) |
| Security | None — port 25, no TLS (DEFECT-14) |
| Retry | RETRY_COUNT tracked per notification; retry_failed resets FAILED→PENDING up to p_max_retries (default 3) |
| Batch size | Default 50 per process_queue call |

[SUPPLEMENTED] *IFACE-04 corrected: original catalog described up to 3 retries as part of send_notification; confirmed from source that retries are managed by the separate retry_failed procedure, not inline in send_notification. process_queue scheduler interval (every 5 minutes) confirmed from source comment.*

### IFACE-05: Self-Service Portal
| Attribute | Value |
|---|---|
| Direction | Bidirectional |
| Status | Source MISSING — integration mechanism unknown (MISS-16) |
| Notes | Portal exists as EXT-05; how it connects to HRMS Oracle Forms is unresourced |

### IFACE-06: LDAP / Active Directory (STUB)
| Attribute | Value |
|---|---|
| Direction | Bidirectional |
| Status | STUB — PKG_INTEGRATION.sync_ldap_directory performs no operations (DEFECT-13) |
| Source | Active Directory (EXT-06) |

### IFACE-07: Oracle Forms to PL/SQL (Internal)
| Attribute | Value |
|---|---|
| Direction | Internal |
| Protocol | Direct PL/SQL package calls from Oracle Forms trigger code |
| Forms | HRMS_LOGIN, HRMS_MENU, HRMS_EMPLOYEE, HRMS_LEAVE, HRMS_PAYROLL, HRMS_PERFORMANCE, HRMS_REPORTS, HRMS_ADMIN (8 named in menu; 6 sourced) |
| Libraries | HRMS_COMMON_LIB (shared utilities), HRMS_VALIDATION_LIB (client-side validation) |
| Notes | Oracle Forms 12c running on WebLogic 12c; Forms make direct DB connections via JDBC thin driver |

[SUPPLEMENTED] *IFACE-07: HRMS_MENU confirms 6 module forms plus HRMS_ADMIN; original catalog listed 6 sourced of 18. Menu source confirms at minimum: HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE, HRMS_PERFORMANCE, HRMS_REPORTS, HRMS_ADMIN — reducing OQ-001 uncertainty for top-level modules (sub-forms within these modules remain unconfirmed).*

---

## PLL LIBRARIES

### LIB-01: HRMS_COMMON_LIB
**Type:** Oracle Forms PLL (client-side)
**Purpose:** Shared UI utilities used across all 18 Forms
**Key procedures:** navigate_to_form (launches named form), show_message (standardized alert display), format_date (consistent date display), get_user_session (retrieves current SESSION_ID from Forms global variable)

### LIB-02: HRMS_VALIDATION_LIB
**Type:** Oracle Forms PLL (client-side)
**Purpose:** Client-side field validation before server call
**Key procedures:** validate_date_format, validate_numeric_range, validate_required_fields, validate_hire_date (90-day check — client-side tier of DISC-001 layered validation)
**Note:** Validation here is duplicated server-side in PKG_VALIDATION. Client-side validates at 90 days (PKG_EMPLOYEE), server-side validates at 180 days (PKG_VALIDATION). Both intentional per DISC-001 resolution.

---

## KNOWN OPEN QUESTIONS (affecting service catalog)

| ID | Question | Impact | Status |
|---|---|---|---|
| OQ-001 | 12 Forms beyond the 6 sourced — what functionality do they cover? | Service catalog may be missing entire capabilities | Partially resolved: HRMS_MENU confirms 8 top-level forms; sub-forms unknown |
| OQ-005 | Multi-state payroll rules — which states? | PKG_PAYROLL.calculate_state_tax is simplified flat-rate | [SUPPLEMENTED] Flat rates confirmed for CA, NY, TX, FL, WA, IL, PA, OH, NJ, MA; default 5% for all others; noted in source as needing bracket-based implementation |
| OQ-006 | MAX_CARRYOVER values per leave type | PKG_LEAVE.year_end_rollover cannot be validated | [SUPPLEMENTED] Carryover values confirmed: PTO=5 days (expire 3 months), SICK=10 days (no expiry), all others=0 |
| OQ-007 | Notification template variable substitution format | PKG_NOTIFICATION.send_notification substitution logic unverified | [SUPPLEMENTED] RESOLVED: No template system exists. Callers pass subject/body directly. No substitution mechanism. |
| OQ-008 | GL journal acknowledgement protocol | No confirmation that GL received file | Still open |
| OQ-009 | ADP benefits acknowledgement file | No confirmation that ADP processed feed | Still open |
| OQ-012 | DBMS_SCHEDULER job for PKG_AUDIT.purge_old_records | Retention enforcement unconfirmed | Still open |
| OQ-013 | Large report performance — no materialized views | Headcount and org chart may be slow at scale | [SUPPLEMENTED] CONFIRMED risk: VW_ORG_HIERARCHY source comment explicitly warns performance degrades with >500 employees |
