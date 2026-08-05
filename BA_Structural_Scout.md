# BA_Structural_Scout.md
**Agent:** BA Agent 1 — Business Structure Scout v3.0  
**Date:** 2026-08-04  
**Source:** Oracle HRMS — Acme Corporation (PL/SQL + Oracle Forms)

---

## 🔍 Agent 1 — Project Scan Summary

| Field | Value |
|---|---|
| Language(s) | PL/SQL (Oracle 19c), Oracle Forms 12c (12.2.1.4) |
| Framework(s) | Oracle Forms, PL/SQL packages, UTL_FILE, UTL_SMTP, DBMS_CRYPTO |
| Architecture style | Monolith (single HRMS schema, Oracle Forms client) |
| Total files scanned | ~40 (27 tables + 22 package files + 6 triggers + 1 views file + 1 sequences file + 6 form XML + 2 libraries + 1 menu + 2 seed data files) |
| Domains identified | 5 — Core HR, Payroll, Leave Management, Performance Management, Cross-Cutting (Security / Audit / Notification / Reporting / Integration) |
| Chunks processed | 5 |

---

## OUTPUT 1 — Domain Architecture Map

| Domain | Tables Owned | Packages Owned | Forms / UIs | External Interfaces |
|---|---|---|---|---|
| **Core HR** | EMPLOYEES, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS, EMERGENCY_CONTACTS, DEPARTMENTS, LOCATIONS, JOB_GRADES, JOB_TITLES | PKG_EMPLOYEE, PKG_VALIDATION | HRMS_EMPLOYEE.fmb | — |
| **Payroll** | SALARY_RECORDS, PAY_ELEMENTS, EMPLOYEE_PAY_ELEMENTS, PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS, TAX_BRACKETS, EMPLOYEE_TAX_INFO, EMPLOYEE_BANK_ACCOUNTS | PKG_PAYROLL | HRMS_PAYROLL.fmb | GL feed (UTL_FILE), ADP Benefits feed (UTL_FILE), Time & Attendance import (UTL_FILE stub) |
| **Leave Management** | LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS, LEAVE_ACCRUAL_LOG, HOLIDAYS | PKG_LEAVE | HRMS_LEAVE.fmb | — |
| **Performance Management** | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS | PKG_PERFORMANCE | HRMS_PERFORMANCE.fmb | — |
| **Cross-Cutting: Security / Auth** | USER_SESSIONS | PKG_SECURITY | HRMS_LOGIN.fmb | — |
| **Cross-Cutting: Audit** | AUDIT_LOG | PKG_AUDIT | — | — |
| **Cross-Cutting: Notification** | NOTIFICATION_QUEUE | PKG_NOTIFICATION | — | UTL_SMTP (smtp.internal.company.com:25) |
| **Cross-Cutting: Reporting** | _(reads all domains)_ | PKG_REPORTING | — | — |
| **Cross-Cutting: Integration** | _(reads SYSTEM_PARAMETERS)_ | PKG_INTEGRATION | — | GL_FEED_OUT dir, BENEFITS_FEED_OUT dir, FTP (creds in SYSTEM_PARAMETERS) |
| **Cross-Cutting: Common / Config** | SYSTEM_PARAMETERS, LOOKUP_VALUES | PKG_COMMON | HRMS_MENU.fmb | — |

**Domain dependency flow (high-level):**
```
Core HR <---- Payroll
Core HR <---- Leave Management
Core HR <---- Performance Management
Core HR <---- Security/Auth
All domains ---> Audit (PRAGMA AUTONOMOUS_TRANSACTION)
All domains ---> Notification (async queue)
All domains ---> Common / Config (PKG_COMMON utilities)
Payroll ---> Integration (GL feed, Benefits feed)
```

**Circular dependency (known):** PKG_EMPLOYEE <-> PKG_PAYROLL — mutual procedure calls; Oracle resolves at runtime via forward declaration. Flagged LOW confidence — see Validation Queue.

---

## OUTPUT 2 — Entity Inventory

| # | Table Name | Domain | Primary Key | Row Count (seed) | Soft-Delete? | Notes |
|---|---|---|---|---|---|---|
| 1 | EMPLOYEES | Core HR | EMP_ID (SEQ_EMPLOYEE) | 25 | Yes — ACTIVE_FLAG='N'; TRG_EMP_INSTEAD_OF_DELETE blocks hard delete | Self-referencing MANAGER_ID FK; SSN_ENCRYPTED (AES-256) |
| 2 | EMPLOYEE_HISTORY | Core HR | HIST_ID (SEQ_EMP_HISTORY) | — | No | DDL column names (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID...) mismatch trigger INSERT columns — pre-existing defect |
| 3 | EMPLOYEE_DEPENDENTS | Core HR | DEPENDENT_ID (SEQ_DEPENDENT) | — | No | FK to EMPLOYEES |
| 4 | EMERGENCY_CONTACTS | Core HR | CONTACT_ID (SEQ_CONTACT) | — | No | FK to EMPLOYEES |
| 5 | DEPARTMENTS | Core HR | DEPT_ID (SEQ_DEPARTMENT) | 10 | No | Self-referencing PARENT_DEPT_ID; MANAGER_ID FK to EMPLOYEES |
| 6 | LOCATIONS | Core HR | LOCATION_ID (SEQ_LOCATION) | 3 | No | HQ/NY, CHI, SF |
| 7 | JOB_GRADES | Core HR | GRADE_ID | 10 | No | Entry Level ($35K-$55K) through C-Suite ($300K-$600K) |
| 8 | JOB_TITLES | Core HR | JOB_ID (SEQ_JOB) | 26 | No | FK to JOB_GRADES |
| 9 | SALARY_RECORDS | Payroll | SALARY_ID (SEQ_SALARY) | 23 | No | FREQ: ANNUAL/MONTHLY; all seed records ANNUAL |
| 10 | PAY_ELEMENTS | Payroll | ELEMENT_ID | 11 | No | Fixed IDs: 1=BASE_PAY, 100-103=taxes, 6=401K, 7=MED, 8=DENTAL, 9=VISION, 10=LIFE, 11=HSA |
| 11 | EMPLOYEE_PAY_ELEMENTS | Payroll | EMP_ELEMENT_ID (SEQ_EMP_PAY_ELEMENT) | — | No | Employee-level override of pay elements |
| 12 | PAY_PERIODS | Payroll | PERIOD_ID (SEQ_PAY_PERIOD) | — | No | STATUS: OPEN/CLOSED/PROCESSING |
| 13 | PAYROLL_RUNS | Payroll | RUN_ID (SEQ_PAYROLL_RUN) | — | No | Status lifecycle: PENDING->CALCULATING->CALCULATED->APPROVED->PAID / REVERSED / ERROR |
| 14 | PAYROLL_DETAILS | Payroll | DETAIL_ID (SEQ_PAYROLL_DETAIL) | — | No | FK to PAYROLL_RUNS + EMPLOYEES + PAY_ELEMENTS |
| 15 | TAX_BRACKETS | Payroll | BRACKET_ID | — | No | 2024 US Federal; TODO: PKG_PAYROLL currently uses hard-coded brackets, not this table |
| 16 | EMPLOYEE_TAX_INFO | Payroll | TAX_INFO_ID (SEQ_TAX_INFO) | — | No | W-4 elections |
| 17 | EMPLOYEE_BANK_ACCOUNTS | Payroll | ACCOUNT_ID (SEQ_BANK_ACCOUNT) | — | No | For direct deposit; routing/account numbers |
| 18 | LEAVE_TYPES | Leave | LEAVE_TYPE_ID | 6 | No | PTO, SICK, COMP, FMLA, JURY, BEREAVE |
| 19 | LEAVE_BALANCES | Leave | BALANCE_ID (SEQ_LEAVE_BALANCE) | — | No | Virtual column: AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING |
| 20 | LEAVE_REQUESTS | Leave | REQUEST_ID (SEQ_LEAVE_REQUEST) | — | No | STATUS lifecycle: PENDING->APPROVED/REJECTED/CANCELLED |
| 21 | LEAVE_ACCRUAL_LOG | Leave | ACCRUAL_ID (SEQ_LEAVE_ACCRUAL) | — | No | Monthly batch accrual records |
| 22 | HOLIDAYS | Leave | HOLIDAY_ID (SEQ_HOLIDAY) | 10 | No | 2024 US Federal holidays |
| 23 | REVIEW_CYCLES | Performance | CYCLE_ID (SEQ_REVIEW_CYCLE) | — | No | STATUS: DRAFT->OPEN->CLOSED |
| 24 | PERFORMANCE_REVIEWS | Performance | REVIEW_ID (SEQ_PERFORMANCE_REVIEW) | — | No | STATUS: NOT_STARTED->SELF_REVIEW->MANAGER_REVIEW->COMPLETED->ACKNOWLEDGED |
| 25 | PERFORMANCE_GOALS | Performance | GOAL_ID (SEQ_PERFORMANCE_GOAL) | — | No | FK to PERFORMANCE_REVIEWS |
| 26 | AUDIT_LOG | Cross-Cutting | LOG_ID (SEQ_AUDIT) | — | No | CACHE 100; stores ERROR_LOG + INFO_LOG + audit events |
| 27 | SYSTEM_PARAMETERS | Cross-Cutting | PARAM_CODE | 10 | No | Key params: FISCAL_YEAR_START='10', SESSION_TIMEOUT='30', MAX_LOGIN_ATTEMPTS='5', SMTP_SERVER, FTP_* (cleartext — security issue) |
| 28 | NOTIFICATION_QUEUE | Cross-Cutting | NOTIFICATION_ID (SEQ_NOTIFICATION) | — | No | STATUS: PENDING/SENT/FAILED/CANCELLED; max 3 retries |
| 29 | USER_SESSIONS | Cross-Cutting | SESSION_ID (SEQ_SESSION) | — | No | 30-min timeout from LOGIN_TIME (non-sliding) |
| 30 | LOOKUP_VALUES | Cross-Cutting | LOOKUP_ID | — | No | Generic key-value reference data |

**Views (6):**

| View | Domain | Purpose | Notable Issue |
|---|---|---|---|
| VW_ACTIVE_EMPLOYEES | Core HR | Active employees with dept/job/grade | Filters ACTIVE_FLAG='A' |
| VW_ORG_HIERARCHY | Core HR | Full org tree via CONNECT BY | Performance warning >500 employees |
| VW_EMPLOYEE_COMPENSATION | Payroll | Salary + compa-ratio | Compa-ratio = ROUND(BASE_SALARY / ((MIN+MAX)/2)*100, 1) |
| VW_LEAVE_SUMMARY | Leave | Leave balances per employee | AVAILABLE omits PENDING (discrepancy vs virtual column) |
| VW_PAYROLL_LATEST | Payroll | Latest payroll run per employee | — |
| VW_PENDING_APPROVALS | Cross-Cutting | UNION ALL: pending leaves + pending reviews | — |

---

## OUTPUT 3 — State & Status Registry

### EMPLOYEES.EMPLOYMENT_STATUS
| Value | Label | Transition Rules |
|---|---|---|
| `ACTIVE` | Active | Set on hire/rehire; TRG blocks direct TERMINATED->ACTIVE |
| `INACTIVE` | Inactive | Set on leave of absence |
| `TERMINATED` | Terminated | Set by PKG_EMPLOYEE.terminate_employee; auto-cancels PENDING leaves; TRG blocks direct reactivation |
| `PENDING` | Pending (onboarding) | Set during onboarding |

### EMPLOYEES.EMPLOYMENT_TYPE
| Value | Label |
|---|---|
| `FULL_TIME` | Full Time |
| `PART_TIME` | Part Time |
| `CONTRACT` | Contractor |
| `INTERN` | Intern |

### PAYROLL_RUNS.STATUS
| Value | Transitions To | Notes |
|---|---|---|
| `PENDING` | CALCULATING | Initial state on run creation; only state that allows recalculate |
| `CALCULATING` | CALCULATED, ERROR | System processing state |
| `CALCULATED` | APPROVED, PENDING | Review state; can revert to PENDING for recalc |
| `APPROVED` | PAID, REVERSED | Requires APPROVE permission (Grade >= 8) |
| `PAID` | REVERSED | Terminal (normal) |
| `REVERSED` | — | Terminal (reversal) |
| `ERROR` | PENDING | Error recovery — resubmit |

### PAY_PERIODS.STATUS
| Value | Notes |
|---|---|
| `OPEN` | Accepting time entries |
| `PROCESSING` | Payroll run in progress |
| `CLOSED` | Period locked |

### LEAVE_REQUESTS.STATUS
| Value | Transitions To | Notes |
|---|---|---|
| `PENDING` | APPROVED, REJECTED, CANCELLED | Increments LEAVE_BALANCES.PENDING on submit |
| `APPROVED` | CANCELLED | Decrements PENDING, increments USED |
| `REJECTED` | — | Decrements PENDING; terminal |
| `CANCELLED` | — | Decrements PENDING (or USED if was APPROVED); terminal |

### REVIEW_CYCLES.STATUS
| Value | Transitions To |
|---|---|
| `DRAFT` | OPEN |
| `OPEN` | CLOSED |
| `CLOSED` | — (terminal) |

### PERFORMANCE_REVIEWS.STATUS
| Value | Transitions To | Notes |
|---|---|---|
| `NOT_STARTED` | SELF_REVIEW | Initial state |
| `SELF_REVIEW` | MANAGER_REVIEW | Employee self-assessment submitted |
| `MANAGER_REVIEW` | COMPLETED | Manager assessment submitted |
| `COMPLETED` | ACKNOWLEDGED | Awaiting employee acknowledgement |
| `ACKNOWLEDGED` | — (terminal) | Review cycle complete |

### NOTIFICATION_QUEUE.STATUS
| Value | Notes |
|---|---|
| `PENDING` | Awaiting process_queue batch |
| `SENT` | Successfully delivered via UTL_SMTP |
| `FAILED` | Delivery failed; retry_failed re-queues if attempts < 3 |
| `CANCELLED` | Manually cancelled |

### EMPLOYEES.ACTIVE_FLAG (soft-delete)
| Value | Meaning |
|---|---|
| `A` | Active record |
| `N` | Soft-deleted (logically inactive) |

### Performance Rating Scale (PKG_PERFORMANCE)
| Range | Label |
|---|---|
| >= 4.5 | Exceptional |
| >= 3.5 | Exceeds Expectations |
| >= 2.5 | Meets Expectations |
| >= 1.5 | Needs Improvement |
| < 1.5 | Unsatisfactory |

---

## OUTPUT 4 — Role & Permission Snapshot

### Grade-Based Permission Model

| Grade | Level Label | Permission Tier | Key Capabilities |
|---|---|---|---|
| 10 | C-Suite | FULL + ADMIN | All operations; admin menu access |
| 9 | Director | FULL + ADMIN | All operations; admin menu access |
| 8 | Manager | FULL | Approve payroll, approve leaves, run reports, view all data |
| 7 | Senior Staff | VIEW_ALL + LIMITED_EDIT | View all employees; edit own records |
| 6 | Staff | VIEW_ALL + LIMITED_EDIT | View all employees; edit own records |
| 5 | Junior Staff | VIEW_ALL | View all employee data; no edits beyond own |
| 4 | Entry/Associate | VIEW_OWN | View own data only |
| 3 | Entry | VIEW_OWN | View own data only |
| 2 | Entry | VIEW_OWN | View own data only |
| 1 | Entry Level | VIEW_OWN | View own data only |

### Permission Constants (PKG_SECURITY.has_permission)

| Permission Name | Minimum Grade | Checked By |
|---|---|---|
| `VIEW` | 5 | HRMS_PAYROLL form entry, reporting |
| `EDIT` | 5 | General data modification |
| `APPROVE` | 8 | Payroll approval, leave approval |
| `ADMIN` | 8 | HRMS_MENU Admin menu items |
| `REPORTS` | 5 | HRMS_MENU Reports menu items |
| `PAYROLL` | 5 | HRMS_MENU Payroll module access |

### Oracle Forms Menu Gates (HRMS_MENU.mmb)

| Menu Item | Permission Required | Notes |
|---|---|---|
| File / Edit / Query / Navigate | None | Available to all authenticated users |
| Modules -> Payroll | `PAYROLL` (Grade >= 5) | Runtime check via PKG_SECURITY.has_permission |
| Admin menu | `ADMIN` (Grade >= 8) | Entire Admin submenu gated |
| Reports menu | `REPORTS` (Grade >= 5) | |
| HRMS_PERFORMANCE form | None | **No permission check on form open** — LOW confidence |

### Session Model

| Parameter | Value | Source |
|---|---|---|
| Session timeout | 30 minutes | SYSTEM_PARAMETERS SESSION_TIMEOUT='30' |
| Timeout type | Fixed from LOGIN_TIME | Non-sliding — activity does not reset clock |
| Session ID source | SEQ_SESSION | USER_SESSIONS.SESSION_ID |
| Global var (Forms) | :GLOBAL.current_user, :GLOBAL.session_id, :GLOBAL.current_emp_id | HRMS_COMMON_LIB.pll |
| Password hash | MD5 | PKG_SECURITY — known weak; no brute-force lockout |
| Max login attempts | 5 | SYSTEM_PARAMETERS MAX_LOGIN_ATTEMPTS='5' — **not enforced in code** |

---

## OUTPUT 5 — Capability & Service Skeleton

### PKG_EMPLOYEE
```
PROCEDURE create_employee(p_first_name, p_last_name, p_email, p_hire_date, p_dept_id, p_job_id, p_manager_id, p_location_id, p_emp_type) -> EMP_ID out
PROCEDURE update_employee(p_emp_id, p_first_name, p_last_name, p_email, p_phone, p_address, p_dept_id, p_job_id, p_manager_id, p_location_id)
PROCEDURE transfer_employee(p_emp_id, p_new_dept_id, p_new_job_id, p_new_manager_id, p_effective_date, p_reason)
PROCEDURE promote_employee(p_emp_id, p_new_job_id, p_new_salary, p_effective_date, p_reason)
PROCEDURE terminate_employee(p_emp_id, p_termination_date, p_reason, p_termination_type [VOLUNTARY/INVOLUNTARY])
PROCEDURE rehire_employee(p_emp_id, p_rehire_date, p_dept_id, p_job_id, p_salary)
FUNCTION  get_employee(p_emp_id) RETURN EMPLOYEES%ROWTYPE
FUNCTION  search_employees(p_last_name, p_first_name, p_dept_id, p_status) RETURN SYS_REFCURSOR  [SECURITY: SQL injection via string concat]
FUNCTION  get_org_chart(p_root_emp_id) RETURN SYS_REFCURSOR  [CONNECT BY]
FUNCTION  get_direct_reports(p_manager_id) RETURN SYS_REFCURSOR
FUNCTION  get_employee_history(p_emp_id) RETURN SYS_REFCURSOR
PROCEDURE add_dependent(p_emp_id, p_name, p_relationship, p_dob, p_ssn)
PROCEDURE add_emergency_contact(p_emp_id, p_name, p_relationship, p_phone, p_alt_phone)
FUNCTION  generate_emp_number RETURN VARCHAR2  [BUG: race condition — MAX+1 pattern, not sequence]
PROCEDURE set_session_context(p_emp_id, p_session_id)
PROCEDURE log_history(p_emp_id, p_change_type, p_old_value, p_new_value)  [PRAGMA AUTONOMOUS_TRANSACTION]
```

### PKG_PAYROLL
```
FUNCTION  create_pay_period(p_period_name, p_start_date, p_end_date, p_pay_date) RETURN NUMBER
PROCEDURE open_pay_period(p_period_id)
PROCEDURE close_pay_period(p_period_id)
FUNCTION  create_payroll_run(p_period_id, p_run_name) RETURN NUMBER
PROCEDURE calculate_payroll(p_run_id)  [sets status CALCULATING->CALCULATED; calls calc_employee_pay for each active emp]
PROCEDURE calc_employee_pay(p_run_id, p_emp_id)  [BASE_PAY + deductions + taxes]
FUNCTION  calculate_federal_tax(p_gross, p_filing_status, p_allowances) RETURN NUMBER  [hard-coded 2024 brackets]
FUNCTION  calculate_state_tax(p_gross, p_state) RETURN NUMBER  [flat-rate table: CA=7.25%, NY=6.85%, TX/FL/WA=0%, IL=4.95%, PA=3.07%, OH=4.00%, NJ=6.37%, MA=5.00%, default=5.00%]
FUNCTION  calculate_fica(p_gross, p_ytd_gross) RETURN NUMBER  [6.2% up to $168,600 wage base]
FUNCTION  calculate_medicare(p_gross, p_ytd_gross) RETURN NUMBER  [1.45% + 0.9% additional above $200K YTD]
PROCEDURE approve_payroll(p_run_id)  [requires APPROVE permission]
PROCEDURE reverse_payroll(p_run_id, p_reason)
PROCEDURE generate_pay_register(p_run_id)  [UTL_FILE to GL_FEED_OUT]
FUNCTION  get_ytd_totals(p_emp_id, p_year) RETURN NUMBER  [BUG: returns 0 placeholder]
FUNCTION  get_payroll_run(p_run_id) RETURN PAYROLL_RUNS%ROWTYPE
FUNCTION  get_run_details(p_run_id) RETURN SYS_REFCURSOR
```

### PKG_LEAVE
```
FUNCTION  submit_leave_request(p_emp_id, p_leave_type_id, p_start_date, p_end_date, p_half_day, p_reason) RETURN NUMBER
PROCEDURE approve_leave(p_request_id, p_approver_id, p_comments)
PROCEDURE reject_leave(p_request_id, p_approver_id, p_reason)
PROCEDURE cancel_leave(p_request_id, p_cancelled_by, p_reason)
FUNCTION  get_leave_balance(p_emp_id, p_leave_type_id) RETURN NUMBER
FUNCTION  get_leave_requests(p_emp_id, p_status, p_from_date, p_to_date) RETURN SYS_REFCURSOR
FUNCTION  get_team_calendar(p_dept_id, p_from_date, p_to_date) RETURN SYS_REFCURSOR
PROCEDURE run_monthly_accrual(p_accrual_date)  [batch; accrues per LEAVE_TYPES.ACCRUAL_RATE]
PROCEDURE process_carryover(p_emp_id, p_leave_type_id, p_year)  [applies MAX_CARRY_FORWARD cap]
PROCEDURE process_expiry(p_emp_id, p_leave_type_id)
FUNCTION  calculate_business_days(p_start_date, p_end_date) RETURN NUMBER
FUNCTION  check_leave_eligibility(p_emp_id, p_leave_type_id) RETURN BOOLEAN  [COMP>=90d tenure, FMLA>=365d tenure]
```

### PKG_PERFORMANCE
```
FUNCTION  create_review_cycle(p_cycle_name, p_start_date, p_end_date, p_review_type) RETURN NUMBER
PROCEDURE open_review_cycle(p_cycle_id)
PROCEDURE close_review_cycle(p_cycle_id)
FUNCTION  create_review(p_cycle_id, p_emp_id, p_reviewer_id) RETURN NUMBER
PROCEDURE submit_self_review(p_review_id, p_self_rating, p_self_comments)
PROCEDURE submit_manager_review(p_review_id, p_manager_rating, p_manager_comments, p_overall_rating)
PROCEDURE complete_review(p_review_id)
PROCEDURE acknowledge_review(p_review_id, p_emp_comments)
FUNCTION  add_goal(p_review_id, p_goal_title, p_goal_description, p_target_date, p_weight) RETURN NUMBER
PROCEDURE update_goal_progress(p_goal_id, p_progress_pct, p_status, p_comments)
FUNCTION  get_review(p_review_id) RETURN PERFORMANCE_REVIEWS%ROWTYPE
FUNCTION  get_cycle_reviews(p_cycle_id, p_status) RETURN SYS_REFCURSOR
FUNCTION  get_employee_reviews(p_emp_id) RETURN SYS_REFCURSOR
FUNCTION  get_rating_label(p_rating NUMBER) RETURN VARCHAR2  [>=4.5->Exceptional ... <1.5->Unsatisfactory]
```

### PKG_AUDIT
```
PROCEDURE log_action(p_table_name, p_action, p_record_id, p_old_values, p_new_values, p_user_id)  [PRAGMA AUTONOMOUS_TRANSACTION]
PROCEDURE purge_audit_log(p_days_to_keep DEFAULT 365)
FUNCTION  get_change_history(p_table_name, p_record_id) RETURN SYS_REFCURSOR
```

### PKG_COMMON
```
PROCEDURE log_error(p_source, p_error_code, p_error_message, p_additional_info)  [PRAGMA AUTONOMOUS_TRANSACTION -> AUDIT_LOG type ERROR_LOG]
PROCEDURE log_info(p_source, p_message)  [PRAGMA AUTONOMOUS_TRANSACTION -> AUDIT_LOG type INFO_LOG]
FUNCTION  get_param(p_param_code) RETURN VARCHAR2
PROCEDURE set_param(p_param_code, p_param_value)
FUNCTION  get_next_business_day(p_date) RETURN DATE  [no holiday exclusion — see VQ-07]
FUNCTION  get_fiscal_year(p_date) RETURN NUMBER  [Oct 1 start]
FUNCTION  get_fiscal_year_start(p_year) RETURN DATE
FUNCTION  get_fiscal_year_end(p_year) RETURN DATE
FUNCTION  format_phone(p_phone) RETURN VARCHAR2
FUNCTION  format_ssn_masked(p_ssn) RETURN VARCHAR2  [returns XXX-XX-NNNN]
FUNCTION  format_currency(p_amount) RETURN VARCHAR2
FUNCTION  format_name(p_first, p_last) RETURN VARCHAR2
FUNCTION  validate_email_format(p_email) RETURN BOOLEAN  [REGEXP_LIKE]
FUNCTION  validate_phone_format(p_phone) RETURN BOOLEAN
FUNCTION  validate_ssn_format(p_ssn) RETURN BOOLEAN
```

### PKG_SECURITY
```
FUNCTION  authenticate(p_username, p_password, p_ip_address) RETURN VARCHAR2  [session_id; inserts USER_SESSIONS; credential check against USER_CREDENTIALS table — impl gap, see VQ-19]
FUNCTION  is_session_valid(p_session_id) RETURN BOOLEAN  [30-min fixed timeout from LOGIN_TIME]
PROCEDURE invalidate_session(p_session_id)
FUNCTION  has_permission(p_emp_id, p_permission) RETURN BOOLEAN  [grade-based lookup]
FUNCTION  encrypt_ssn(p_ssn) RETURN RAW  [DBMS_CRYPTO AES-256 CBC PKCS5; hard-coded key — SECURITY RISK]
FUNCTION  decrypt_ssn(p_encrypted_ssn) RETURN VARCHAR2
PROCEDURE change_password(p_emp_id, p_old_password, p_new_password)  [min 8 chars, 1 upper, 1 digit — stub implementation]
FUNCTION  get_current_user RETURN VARCHAR2
```

### PKG_VALIDATION
```
FUNCTION  validate_date_range(p_start_date, p_end_date) RETURN BOOLEAN
FUNCTION  validate_salary_for_grade(p_salary, p_grade_id) RETURN BOOLEAN
FUNCTION  validate_email_format(p_email) RETURN BOOLEAN  [delegates to PKG_COMMON]
FUNCTION  validate_phone_format(p_phone) RETURN BOOLEAN
FUNCTION  validate_emp_number_format(p_emp_number) RETURN BOOLEAN  [regex: ^EMP-\d{6}$]
FUNCTION  is_future_date(p_date) RETURN BOOLEAN
FUNCTION  is_business_day(p_date) RETURN BOOLEAN  [checks HOLIDAYS table]
FUNCTION  validate_required_fields(p_emp_id) RETURN BOOLEAN  [EMPLOYEES only: FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID]
```

### PKG_NOTIFICATION
```
PROCEDURE send_notification(p_recipient_id, p_notification_type, p_subject, p_message, p_reference_id, p_reference_type)  [PRAGMA AUTONOMOUS_TRANSACTION; enqueues to NOTIFICATION_QUEUE]
PROCEDURE process_queue(p_batch_size DEFAULT 50)  [UTL_SMTP batch send; smtp.internal.company.com:25]
PROCEDURE retry_failed(p_max_attempts DEFAULT 3)
PROCEDURE cancel_notification(p_notification_id)
FUNCTION  get_pending_count RETURN NUMBER
```

### PKG_REPORTING
```
FUNCTION  headcount_report(p_dept_id, p_as_of_date) RETURN SYS_REFCURSOR
FUNCTION  compensation_summary(p_dept_id, p_grade_id) RETURN SYS_REFCURSOR  [includes compa-ratio]
FUNCTION  turnover_report(p_from_date, p_to_date, p_dept_id) RETURN SYS_REFCURSOR  [voluntary vs involuntary]
FUNCTION  new_hires_report(p_from_date, p_to_date, p_dept_id) RETURN SYS_REFCURSOR
FUNCTION  leave_utilization_report(p_leave_type_id, p_from_date, p_to_date) RETURN SYS_REFCURSOR
FUNCTION  payroll_summary_report(p_run_id) RETURN SYS_REFCURSOR
FUNCTION  eeo_compliance_report(p_as_of_date) RETURN SYS_REFCURSOR
PROCEDURE refresh_reporting_tables  [stub — not implemented]
```

### PKG_INTEGRATION
```
PROCEDURE generate_gl_journal(p_run_id)  [UTL_FILE pipe-delimited; H/D/T format -> GL_FEED_OUT]
PROCEDURE export_benefits_feed(p_as_of_date)  [UTL_FILE fixed-width 203-char ADP records -> BENEFITS_FEED_OUT]
PROCEDURE import_time_attendance(p_file_name)  [UTL_FILE CSV -> STUB; TODO not implemented]
PROCEDURE sync_org_structure  [placeholder — not implemented]
FUNCTION  get_integration_status(p_integration_name) RETURN VARCHAR2  [reads SYSTEM_PARAMETERS]
```

---

## OUTPUT 6 — Integration & Dependency Map

### Inbound Integrations
| Integration | Direction | Method | Status | Notes |
|---|---|---|---|---|
| Time & Attendance Import | Inbound | UTL_FILE CSV read from filesystem | **STUB — not implemented** | PKG_INTEGRATION.import_time_attendance; TODO comment in source |
| Oracle Forms UI | Inbound | Oracle Forms 12c applet -> DB packages | Production | All 6 forms call DB packages directly via PL/SQL |

### Outbound Integrations
| Integration | Direction | Method | File Format | Destination |
|---|---|---|---|---|
| GL Journal Feed | Outbound | UTL_FILE write | Pipe-delimited, H/D/T records | GL_FEED_OUT Oracle directory object |
| ADP Benefits Feed | Outbound | UTL_FILE write | Fixed-width 203 chars/record | BENEFITS_FEED_OUT Oracle directory object |
| Pay Register | Outbound | UTL_FILE write (generate_pay_register) | Pipe-delimited | GL_FEED_OUT Oracle directory object |
| Email Notifications | Outbound | UTL_SMTP | RFC 2822 email | smtp.internal.company.com:25; from hrms-noreply@company.com |
| FTP (implied) | Outbound | FTP (creds in SYSTEM_PARAMETERS) | Unknown | FTP_HOST/FTP_USER/FTP_PASSWORD stored cleartext in SYSTEM_PARAMETERS — SECURITY RISK |

### Internal Package Dependencies
| Package | Calls / Uses |
|---|---|
| PKG_EMPLOYEE | PKG_AUDIT, PKG_COMMON, PKG_NOTIFICATION, PKG_PAYROLL (circular) |
| PKG_PAYROLL | PKG_AUDIT, PKG_COMMON, PKG_EMPLOYEE (circular), PKG_NOTIFICATION |
| PKG_LEAVE | PKG_AUDIT, PKG_COMMON, PKG_NOTIFICATION, PKG_VALIDATION |
| PKG_PERFORMANCE | PKG_AUDIT, PKG_COMMON, PKG_NOTIFICATION |
| PKG_SECURITY | PKG_AUDIT, PKG_COMMON (get_param for SESSION_TIMEOUT), DBMS_CRYPTO |
| PKG_VALIDATION | PKG_COMMON (validate_email delegates) |
| PKG_NOTIFICATION | PKG_COMMON (log_error), UTL_SMTP |
| PKG_REPORTING | PKG_COMMON, reads all domain tables/views |
| PKG_INTEGRATION | PKG_COMMON (get_param), UTL_FILE |
| PKG_AUDIT | DBMS_UTILITY, SYS_CONTEXT (no package deps — base layer) |
| PKG_COMMON | DBMS_CRYPTO (format_ssn_masked), UTL_FILE (no package deps — base layer) |

### Database Triggers -> Package Calls
| Trigger | Fire Event | Calls |
|---|---|---|
| TRG_EMP_BEFORE_INSERT | BEFORE INSERT on EMPLOYEES | SEQ_EMPLOYEE; email uniqueness check; 180-day hire limit |
| TRG_EMP_BEFORE_UPDATE | BEFORE UPDATE on EMPLOYEES | PKG_AUDIT.log_action; writes EMPLOYEE_HISTORY (column mismatch bug — VQ-01) |
| TRG_EMP_INSTEAD_OF_DELETE | INSTEAD OF DELETE on EMPLOYEES | Raises -20504 (blocks all deletes) |
| TRG_SALARY_AUDIT | AFTER I/U/D on SALARY_RECORDS | PKG_AUDIT.log_action |
| TRG_LEAVE_REQUEST_AUDIT | AFTER UPDATE OF STATUS on LEAVE_REQUESTS | PKG_AUDIT.log_action |
| TRG_DEPARTMENT_AUDIT | AFTER I/U/D on DEPARTMENTS | PKG_AUDIT.log_action |

### Oracle Forms -> Package/Table Dependencies
| Form | Primary Package(s) Called | Tables Queried Directly |
|---|---|---|
| HRMS_EMPLOYEE.fmb | PKG_EMPLOYEE, PKG_SECURITY | JOB_GRADES, DEPARTMENTS, EMPLOYEES (LOVs) |
| HRMS_LEAVE.fmb | PKG_LEAVE, PKG_SECURITY | LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS |
| HRMS_LOGIN.fmb | PKG_SECURITY | EMPLOYEES (by EMAIL, ROWNUM=1) |
| HRMS_MENU.fmb | PKG_SECURITY (has_permission) | — |
| HRMS_PAYROLL.fmb | PKG_PAYROLL, PKG_SECURITY | PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS |
| HRMS_PERFORMANCE.fmb | PKG_PERFORMANCE | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS |

---

## Validation Queue

Items requiring Agent 2 confirmation or deep investigation:

| ID | Severity | Item | Location | Issue |
|---|---|---|---|---|
| VQ-01 | MEDIUM | EMPLOYEE_HISTORY trigger column mismatch | TRG_EMP_BEFORE_UPDATE / EMPLOYEE_HISTORY DDL | Trigger inserts HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE (VARCHAR2) but DDL has HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID (typed columns). Pre-existing defect — trigger may silently fail on every status/dept/job change |
| VQ-02 | MEDIUM | VW_LEAVE_SUMMARY AVAILABLE formula | hrms_views.sql vs LEAVE_BALANCES virtual column | View excludes PENDING; virtual column includes PENDING in subtraction. Two inconsistent formulas in production |
| VQ-03 | MEDIUM | PKG_EMPLOYEE <-> PKG_PAYROLL circular dependency | PKG_EMPLOYEE.pkb + PKG_PAYROLL.pkb | Mutual calls; confirm actual compilation succeeds without unresolved forward declarations |
| VQ-04 | MEDIUM | generate_emp_number race condition | PKG_EMPLOYEE.generate_emp_number | Uses MAX(EMP_NUMBER)+1 not SEQ_EMP_NUMBER. Two concurrent inserts can generate the same number |
| VQ-05 | LOW | DEPT_ID=30 manager double-update | data/seed/02_employee_data.sql | IT dept manager set to EMP_ID=3 then overwritten to EMP_ID=30. Final = EMP_ID=30 (Rachel Thompson). Confirm intentional |
| VQ-06 | LOW | HRMS_PERFORMANCE form — no permission check | HRMS_PERFORMANCE.xml | Other forms check PKG_SECURITY.has_permission on open; performance form does not. Intentional design or omission? |
| VQ-07 | LOW | get_next_business_day ignores holidays | PKG_COMMON | Advances past weekends only; does NOT check HOLIDAYS table. PKG_VALIDATION.is_business_day DOES check HOLIDAYS. Inconsistency between two utility functions |
| VQ-08 | HIGH | get_ytd_totals returns 0 placeholder | PKG_PAYROLL.get_ytd_totals | Explicitly returns 0; affects YTD_GROSS/YTD_NET in pay register. SS wage base cutoff ($168,600) and Additional Medicare (above $200K) never correctly applied |
| VQ-09 | LOW | refresh_reporting_tables stub | PKG_REPORTING.refresh_reporting_tables | Declared but empty. Are materialized views / summary tables expected but not built? |
| VQ-10 | MEDIUM | import_time_attendance stub | PKG_INTEGRATION | TODO comment — CSV import not implemented. Unclear if manual workaround exists in production |
| VQ-11 | MEDIUM | HRMS_LOGIN.fmb password sent cleartext | Oracle Forms client | Oracle Forms applet sends credentials in cleartext unless SSL configured at app server level. Verify transport encryption |
| VQ-12 | HIGH | TAX_BRACKETS table unused | PKG_PAYROLL + TAX_BRACKETS DDL | Table created but PKG_PAYROLL uses hard-coded 2024 brackets. Will produce incorrect taxes in 2025+ without code change |
| VQ-13 | CRITICAL | Hard-coded AES-256 encryption key | PKG_SECURITY.encrypt_ssn | DBMS_CRYPTO key hard-coded in package body. Anyone with EXECUTE on PKG_SECURITY or source access can decrypt all employee SSNs |
| VQ-14 | CRITICAL | MD5 password hashing | PKG_SECURITY.change_password | MD5 is cryptographically broken; rainbow table attack feasible for any password |
| VQ-15 | CRITICAL | SQL injection | PKG_EMPLOYEE.search_employees | p_last_name and p_first_name concatenated into dynamic SQL without bind variables |
| VQ-16 | CRITICAL | Cleartext FTP credentials | SYSTEM_PARAMETERS (FTP_HOST, FTP_USER, FTP_PASSWORD) | Any DB user with SELECT on SYSTEM_PARAMETERS can read production FTP credentials |
| VQ-17 | MEDIUM | EMPLOYEES.EMAIL uniqueness — no DB constraint | TRG_EMP_BEFORE_INSERT | Trigger checks with SELECT/COUNT before insert (TOCTOU gap); no unique constraint on EMAIL column confirmed in DDL |
| VQ-18 | MEDIUM | Hire date limit discrepancy | TRG_EMP_BEFORE_INSERT (180 days) vs HRMS_EMPLOYEE.xml WHEN-VALIDATE-ITEM (90 days) | Two different future-hire limits enforced at different layers; which is authoritative? |
| VQ-19 | HIGH | PKG_SECURITY.authenticate — credential check gap | PKG_SECURITY.pkb | Code creates session but actual password hash comparison against USER_CREDENTIALS not visible in provided source. Missing package or inline SQL? |
| VQ-20 | MEDIUM | SESSION_TIMEOUT non-sliding | PKG_SECURITY.is_session_valid | Checks LOGIN_TIME + 30 min; does not reset on activity. Active users can be silently expired mid-task |

---

## Handoff Note to Agent 2

**From:** BA Agent 1 — Business Structure Scout  
**To:** BA Agent 2 — Deep Analyst  
**Codebase:** Oracle HRMS (Acme Corporation) — PL/SQL 19c + Oracle Forms 12c monolith

### What Agent 1 has established

The structural inventory above is complete. HIGH confidence items:
- All 30 tables (including LOOKUP_VALUES) with PKs, domains, soft-delete patterns
- All 11 package signatures (specs + body analysis)
- All state/status lifecycles with full transition rules
- Grade-based permission model (Grades 1-10, 5 permission constants)
- All 5+ integration channels (GL feed, ADP, T&A stub, SMTP, FTP, Forms UI)
- 20 validation queue items including 4 CRITICAL security vulnerabilities

### Priority investigations for Agent 2

1. **VQ-13/14/15/16 — Security vulnerabilities (CRITICAL)**: Hard-coded AES key, MD5 passwords, SQL injection, cleartext FTP creds. Agent 2 should assess exploitability and estimate remediation effort for the business risk register.

2. **VQ-01 — Trigger column mismatch (HIGH DATA RISK)**: TRG_EMP_BEFORE_UPDATE inserts into EMPLOYEE_HISTORY with wrong column names. This fires on every STATUS/DEPT/JOB change. If silently failing, EMPLOYEE_HISTORY table may be empty or corrupted — critical for data integrity assessment before any migration.

3. **VQ-02 — Leave AVAILABLE formula split**: Two different AVAILABLE calculations exist (view vs virtual column). The business rule for available leave is ambiguous. Agent 2 should determine which drives actual approvals, reports, and the employee-visible balance screen.

4. **VQ-08 — YTD zero placeholder (HIGH PAYROLL ACCURACY RISK)**: get_ytd_totals returns 0, meaning SS wage base cutoff and Additional Medicare surcharge are never triggered. All employees earning > $168,600 are being over-taxed on SS; those > $200K are missing the 0.9% Medicare surcharge.

5. **VQ-19 — PKG_SECURITY authenticate gap**: The authentication flow creates a session but the actual password hash comparison is not visible in provided source. Agent 2 should search for USER_CREDENTIALS table DDL or any missing package that performs the actual check.

6. **VQ-12 — Tax brackets hard-coded for 2024**: Annual maintenance risk. Agent 2 should confirm whether there is a deployment procedure to update these each January, or if this is a manual code change.

7. **VQ-10 — Time & Attendance import stub**: If payroll depends on T&A data, a manual workaround must exist in production. Agent 2 should investigate whether payroll is operating without T&A integration or if there is a separate mechanism.

8. **VQ-03/04 — Circular dependency + EMP_NUMBER race condition**: Confirm compilation succeeds and determine whether the MAX+1 pattern has produced duplicate EMP_NUMBERs in the seed or production data.

### Data to pass forward

- Seed dataset: 25 employees (24 active, 1 terminated — Brian Foster EMP-000099), 10 departments, 10 job grades, 26 job titles, 3 locations, 6 leave types, 11 pay elements, 10 holidays, 10 system parameters
- Version string: `HRMS v4.2 - Build 2024.03.15` (hard-coded in HRMS_MENU.xml)
- Fiscal year: Oct 1 start (PARAM_CODE='FISCAL_YEAR_START'='10')
- Schema name: HRMS (Oracle 19c)
- Application server: Oracle Forms 12c (12.2.1.4)
- SMTP server: smtp.internal.company.com:25
- Email sender: hrms-noreply@company.com
- Social Security wage base 2024: $168,600 at 6.2%
- Additional Medicare threshold: $200,000 YTD at 0.9%

---

*BA_Structural_Scout.md — generated by BA Agent 1 v3.0 — 2026-08-04*
