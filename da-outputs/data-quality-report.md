# HRMS Data Quality Report

**Schema:** HRMS  **DB:** Oracle 19c  **Extracted:** 2026-08-04  
**Method:** CODE-ONLY  
**Severity:** CRITICAL / HIGH / MEDIUM / LOW

---

## Executive Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 4 |
| HIGH | 9 |
| MEDIUM | 10 |
| LOW | 6 |
| **Total** | **29** |

*DA Agent 2 (pass 2) added DQ-027 (MEDIUM) and DQ-028 (LOW). DQ-006 was also corrected to note TWO CHK_CHANGE_TYPE violations (JOB_CHANGE and DEPARTMENT_CHANGE) not one, and to correct the recommended fix. DQ-031 (HIGH) added from PKG_INTEGRATION.pkb source recovery — import_time_attendance TODO stub.*

---

## CRITICAL Issues

### DQ-001 — Hard-Coded Encryption Key in Source Code
**Severity:** CRITICAL  
**Table/Object:** PKG_SECURITY (affects EMPLOYEES.SSN_ENCRYPTED, EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED, EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC)  
**Description:** The AES-256 encryption key is a string literal `'HR$ystem_3ncrypt10n_K3y_2024!!'` in the package body. Anyone with access to source code can decrypt all SSN and bank account data.  
**Impact:** All encrypted PII is effectively unprotected. Key rotation requires code change plus full re-encryption of all records.  
**Recommendation:** Move key to Oracle Wallet / HSM. Rotate immediately.

### DQ-002 — SQL Injection Vulnerability in search_employees
**Severity:** CRITICAL  
**Table/Object:** PKG_EMPLOYEE.search_employees, EMPLOYEES  
**Description:** `p_last_name` and `p_first_name` parameters are concatenated directly into a dynamic SQL string without sanitization. An attacker can inject arbitrary SQL via these fields.  
**Example:** `p_last_name => 'Smith'' OR 1=1 --'` dumps all records.  
**Impact:** Complete data exfiltration risk. All EMPLOYEES data accessible to any user who can invoke this function.  
**Recommendation:** Replace string concatenation with bind variables (:p_last_name).

### DQ-003 — Password Authentication Not Implemented
**Severity:** CRITICAL  
**Table/Object:** PKG_SECURITY.authenticate, USER_CREDENTIALS  
**Description:** The `authenticate()` function references USER_CREDENTIALS table but does not actually verify the supplied password hash against the stored hash. Authentication is effectively bypassed — any password is accepted.  
**Impact:** Any user who knows a valid username can log in without a password.  
**Recommendation:** Implement full authentication: retrieve stored hash, compare with DBMS_CRYPTO hash of supplied password.

### DQ-004 — Cleartext FTP Credentials in SYSTEM_PARAMETERS
**Severity:** CRITICAL  
**Table/Object:** SYSTEM_PARAMETERS (PARAM_GROUP='INTEGRATION', PARAM_CODE='FTP_PASSWORD'), PKG_INTEGRATION  
**Description:** FTP server credentials for the ADP benefits feed transfer are stored unencrypted in the SYSTEM_PARAMETERS table. Any user with SELECT on this table can read the credentials.  
**Impact:** FTP credential theft → unauthorized access to benefits data on external FTP server.  
**Recommendation:** Encrypt FTP credentials using same AES mechanism (after fixing DQ-001); restrict SELECT on SYSTEM_PARAMETERS by PARAM_GROUP.

---

## HIGH Issues

### DQ-005 — Race Condition in Employee Number Generation
**Severity:** HIGH  
**Table/Object:** PKG_EMPLOYEE.generate_emp_number, EMPLOYEES.EMP_NUMBER  
**Description:** `generate_emp_number` uses `SELECT MAX(EMP_NUMBER)+1` instead of `SEQ_EMP_NUMBER.NEXTVAL`. Under concurrent inserts, two sessions can read the same MAX and generate identical EMP_NUMBERs.  
**Impact:** Duplicate EMP_NUMBER inserts will fail on the UK_EMP_NUMBER constraint, causing hire transactions to roll back. Under load this can cause systematic hire failures.  
**Recommendation:** Replace MAX+1 logic with `SEQ_EMP_NUMBER.NEXTVAL`. The sequence already exists but is unused.

### DQ-006 — EMPLOYEE_HISTORY Trigger Column Mismatch AND Check Constraint Violations (×2)
**Severity:** HIGH  
**Table/Object:** TRG_EMP_BEFORE_UPDATE, EMPLOYEE_HISTORY  
**Description:** The trigger has TWO classes of defect:  
1. **Column name mismatch:** The trigger inserts using column names (HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE) that do not match the DDL column names (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID/OLD_JOB_ID/etc.). The trigger will raise ORA-00904 (invalid identifier) at runtime on every employee update.  
2. **CHK_CHANGE_TYPE constraint violations (TWO values invalid)** *(CORRECTED by DA Agent 2 second pass)*: The trigger uses three CHANGE_TYPE values: 'STATUS_CHANGE', 'DEPARTMENT_CHANGE', and 'JOB_CHANGE'. The actual CHK_CHANGE_TYPE constraint per DDL/schema-catalogue.json is: `CHANGE_TYPE IN ('HIRE','TRANSFER','PROMOTION','DEMOTION','SALARY_CHANGE','TERMINATION','REHIRE','LEAVE_START','LEAVE_END','STATUS_CHANGE')`. Both 'DEPARTMENT_CHANGE' **and** 'JOB_CHANGE' are absent from this list — two ORA-02290 violations per qualifying update, not one. *(Note: a prior review pass incorrectly listed the constraint as `('STATUS_CHANGE','SALARY_CHANGE','DEPT_CHANGE','JOB_CHANGE','MANAGER_CHANGE','REHIRE')` — that list does not match the DDL. 'DEPT_CHANGE' and 'JOB_CHANGE' do not exist as allowed values. The correct trigger values for dept/job changes are 'TRANSFER' and 'PROMOTION'/'DEMOTION' respectively, which ARE in the constraint.)*  
**Impact:** All employee STATUS_CHANGE, DEPARTMENT_CHANGE, and JOB_CHANGE history records fail (the first due to column name mismatch; the latter two also fail even after column names are fixed). EMPLOYEE_HISTORY is likely empty in production.  
**Recommendation:** (1) Align trigger INSERT column list with actual DDL column names (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID, etc.). (2) Replace 'DEPARTMENT_CHANGE' with 'TRANSFER' and 'JOB_CHANGE' with the appropriate value ('PROMOTION' or 'DEMOTION') — OR add new allowed values to the CHK_CHANGE_TYPE constraint if richer history granularity is desired. (3) Do NOT use 'DEPT_CHANGE' — it is not in the real constraint.

### DQ-007 — VW_LEAVE_SUMMARY Balance Formula Discrepancy
**Severity:** HIGH  
**Table/Object:** VW_LEAVE_SUMMARY, LEAVE_BALANCES  
**Description:** The view computes available balance as `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT` — omitting PENDING. The LEAVE_BALANCES.AVAILABLE virtual column correctly includes `-PENDING`. The view overstates available balance for employees with pending requests.  
**Impact:** Employees and managers see inflated leave balances in reports. Double-booking of leave is possible.  
**Recommendation:** Update VW_LEAVE_SUMMARY to subtract PENDING.

### DQ-008 — Partial Payroll Commit Risk
**Severity:** HIGH  
**Table/Object:** PKG_PAYROLL.calculate_payroll, PAYROLL_RUNS, PAYROLL_DETAILS  
**Description:** The payroll calculation commits every 50 employees. If the run fails after the 51st employee, the first 50 are permanently committed in a CALCULATING state while the run overall shows ERROR. The run cannot be re-run safely without reversing the partial commit.  
**Impact:** Inconsistent payroll state; employees may be paid twice or not at all during recovery.  
**Recommendation:** Remove intermediate commits; use a SAVEPOINT pattern or process in a single transaction. Consider a staging table approach.

### DQ-009 — Leave Carryover Double-Expiry Bug
**Severity:** HIGH  
**Table/Object:** PKG_LEAVE.expire_carryover  
**Description:** Running `expire_carryover` twice on the same day will expiry the same carryover days twice, producing a negative OPENING_BALANCE or removing valid balances.  
**Impact:** Employee leave balances can go negative or be zeroed incorrectly if the scheduled job is re-run (e.g. after a failure retry).  
**Recommendation:** Add idempotency guard: check whether expiry has already been applied for this calendar year before updating.

### DQ-010 — MD5 Password Hashing
**Severity:** HIGH  
**Table/Object:** PKG_SECURITY (USER_CREDENTIALS)  
**Description:** Passwords are hashed with MD5. MD5 is cryptographically broken for password storage. Pre-image attacks and rainbow tables exist.  
**Impact:** If USER_CREDENTIALS table is exfiltrated, all passwords are recoverable.  
**Recommendation:** Migrate to bcrypt or PBKDF2 with at least 100,000 iterations.

### DQ-011 — Tax Bracket Logic Hard-Coded (2024 Only)
**Severity:** HIGH  
**Table/Object:** PKG_PAYROLL, TAX_BRACKETS  
**Description:** Federal income tax brackets, standard deductions ($14,600/$29,200), and SS wage base ($168,600) are hard-coded as private constants in PKG_PAYROLL. The TAX_BRACKETS table exists and is seeded but is never read.  
**Impact:** In 2025+, all payroll calculations will use incorrect 2024 tax parameters until the package is recompiled with new constants.  
**Recommendation:** Implement TAX_BRACKETS lookup in PKG_PAYROLL using TAX_YEAR parameter.

### DQ-012 — Session Timeout Based on Login Time, Not Last Activity
**Severity:** HIGH  
**Table/Object:** PKG_SECURITY.is_session_valid, USER_SESSIONS  
**Description:** Session expiry checks `LOGIN_TIME + timeout_minutes` rather than `last_activity_time + timeout_minutes`. An active user working continuously will be timed out; an idle user will not be timed out earlier than a busy user.  
**Impact:** Incorrect timeout behavior; security gap for abandoned sessions. Active users experience unexpected session drops.  
**Recommendation:** Add LAST_ACTIVITY_DATE column to USER_SESSIONS; update on each PKG_SECURITY call; check against last activity.

---

## MEDIUM Issues

### DQ-013 — SALARY_RECORDS Missing Uniqueness Constraint on (EMP_ID, EFFECTIVE_DATE)
**Severity:** MEDIUM  
**Table/Object:** SALARY_RECORDS  
**Description:** Nothing prevents two salary records for the same employee on the same effective date. PKG_PAYROLL's `get_current_salary` may return arbitrary results if duplicates exist.  
**Recommendation:** Add UNIQUE constraint on (EMP_ID, EFFECTIVE_DATE) where END_DATE IS NULL, or at minimum on (EMP_ID, EFFECTIVE_DATE).

### DQ-014 — HOLIDAYS Missing Uniqueness Constraint on (HOLIDAY_DATE, LOCATION_CODE)
**Severity:** MEDIUM  
**Table/Object:** HOLIDAYS  
**Description:** Duplicate holiday entries for the same date and location are possible. PKG_LEAVE.calculate_business_days would double-count holidays.  
**Recommendation:** Add UNIQUE constraint on (HOLIDAY_DATE, LOCATION_CODE).

### DQ-015 — VW_PAYROLL_LATEST Uses MAX(RUN_ID) for Latest Run AND Returns Wrong Employees
**Severity:** MEDIUM  
**Table/Object:** VW_PAYROLL_LATEST  
**Description:** The view has two compounding problems: (1) **ID vs date ordering**: The view identifies the "latest" payroll run using `MAX(RUN_ID)`. If supplemental or bonus runs are inserted out of sequence, the "latest" run by ID may not be the most recent by run date. (2) **Global scope, not per-employee** *(ENRICHED by DA Agent 2)*: The subquery `SELECT MAX(pr2.RUN_ID) FROM PAYROLL_RUNS pr2 WHERE pr2.STATUS = 'APPROVED'` returns a single global RUN_ID applied to ALL employee rows. Employees processed in different payroll runs (e.g. biweekly vs monthly cycles) will have no data or zero-pay results for the globally-latest run. The view does not partition by PERIOD_ID or employee pay frequency.  
**Recommendation:** Rewrite using ROW_NUMBER() OVER (PARTITION BY pd.EMP_ID ORDER BY pr.RUN_DATE DESC) to select the latest approved run per employee rather than the global maximum.

### DQ-016 — rehire_employee Overwrites Original HIRE_DATE
**Severity:** MEDIUM  
**Table/Object:** PKG_EMPLOYEE.rehire_employee, EMPLOYEES  
**Description:** Rehire sets `HIRE_DATE = p_rehire_date`, destroying the original hire date. Tenure calculations (benefits eligibility, leave accrual, service awards) will use the rehire date rather than original hire date.  
**Recommendation:** Add ORIGINAL_HIRE_DATE column to EMPLOYEES; populate on hire; never overwrite. Use HIRE_DATE for most-recent employment period.

### DQ-017 — business_days_between vs calculate_business_days Holiday Inconsistency
**Severity:** MEDIUM  
**Table/Object:** PKG_COMMON.business_days_between, PKG_LEAVE.calculate_business_days  
**Description:** PKG_COMMON.business_days_between does NOT subtract public holidays from the count. PKG_LEAVE.calculate_business_days does subtract holidays. Two business-day calculations for the same date range will produce different results depending on which function is called.  
**Recommendation:** Standardize on one implementation. Prefer PKG_LEAVE's holiday-aware version.

### DQ-018 — SSN Validation Divergence Between Client and Server
**Severity:** MEDIUM  
**Table/Object:** HRMS_VALIDATION_LIB.pll (validate_ssn), PKG_COMMON.is_valid_ssn  
**Description:** Client-side validate_ssn rejects all-zero segments (000-xx-xxxx, xxx-00-xxxx, xxx-xx-0000). Server-side is_valid_ssn does not check this rule. Invalid SSNs accepted by server can pass server-side validation even if rejected by the form.  
**Recommendation:** Align PKG_COMMON.is_valid_ssn to include all-zero segment checks.

### DQ-019 — Email Validation Subdomain Rejection in Client Lib
**Severity:** MEDIUM  
**Table/Object:** HRMS_VALIDATION_LIB.pll  
**Description:** Client-side email validation rejects valid subdomains (e.g. user@mail.company.com). Server-side does not have this restriction. Employees with subdomain email addresses may be unable to enter their correct email.  
**Recommendation:** Update client-side validation regex to allow subdomains per RFC 5322.

### DQ-020 — DEPT_ID=30 Manager Set Twice in Seed Data
**Severity:** MEDIUM  
**Table/Object:** data/seed/02_employee_data.sql, DEPARTMENTS  
**Description:** The seed script sets DEPT_ID=30 manager to EMP_ID=3 (Michael OConnor) then overwrites it with EMP_ID=30 (Rachel Thompson). The first assignment is dead data; intent is ambiguous.  
**Recommendation:** Review seed data; remove redundant UPDATE; document intended department manager.

### DQ-021 — Terminated Employee Brian Foster Inconsistency
**Severity:** MEDIUM  
**Table/Object:** data/seed/02_employee_data.sql, EMPLOYEES  
**Description:** Brian Foster (EMP-000099) is seeded as TERMINATED with date 2023-06-30. ACTIVE_FLAG is set to 'N'. However, the seed data sets EMPLOYMENT_STATUS in a separate UPDATE — if the first INSERT fails, the UPDATE still runs and ACTIVE_FLAG='N' without a TERMINATION_DATE, creating an inconsistent record.  
**Recommendation:** Combine all fields in a single INSERT; validate seed data produces consistent state.

---

## LOW Issues

### DQ-022 — YTD Amounts in Payslip Hard-Coded as 0
**Severity:** LOW  
**Table/Object:** PKG_PAYROLL (payslip generation)  
**Description:** Year-to-date salary and tax figures in payslip output are hard-coded as 0. Employees receive payslips with incorrect YTD figures.  
**Recommendation:** Implement YTD aggregation from PAYROLL_DETAILS filtered by EMP_ID and calendar year.

### DQ-023 — Missing Account Lockout on Authentication Failure
**Severity:** LOW (escalates to HIGH if DQ-003 is fixed)  
**Table/Object:** PKG_SECURITY.authenticate  
**Description:** No failed-attempt counter or lockout mechanism exists. Unlimited brute-force login attempts are possible.  
**Recommendation:** Add LOGIN_ATTEMPTS and LOCKED_UNTIL columns to USER_CREDENTIALS; lock after 5 failures for 30 minutes.

### DQ-024 — SEQ_AUDIT is Only Cached Sequence
**Severity:** LOW  
**Table/Object:** SEQ_AUDIT (CACHE 100), all other sequences (NOCACHE)  
**Description:** All 28 non-audit sequences use NOCACHE, causing a redo log write for every single sequence fetch. Under concurrent payroll processing (batching 50 employees) this creates significant I/O overhead.  
**Recommendation:** Add CACHE 20 to high-frequency sequences: SEQ_PAYROLL_DETAIL, SEQ_LEAVE_ACCRUAL, SEQ_NOTIFICATION, SEQ_EMP_HISTORY.

### DQ-025 — CONNECT BY Hierarchy Query Known Timeout
**Severity:** LOW  
**Table/Object:** VW_ORG_HIERARCHY  
**Description:** VW_ORG_HIERARCHY uses CONNECT BY for org chart traversal. A comment in the codebase notes this degrades for >500 employees.  
**Recommendation:** For scaling, replace with a materialized path (LTREE-style) or pre-computed hierarchy table updated by triggers.

### DQ-026 — PKG_AUDIT Silently Swallows All Errors
**Severity:** LOW  
**Table/Object:** PKG_AUDIT.log_action, PKG_AUDIT.log_error  
**Description:** All audit logging is wrapped in EXCEPTION WHEN OTHERS THEN NULL — failures are never surfaced. If the AUDIT_LOG table fills up or encounters an error, data operations continue without any audit trail silently.  
**Recommendation:** At minimum, log to V$SESSION or call DBMS_OUTPUT in dev mode; consider a secondary alert mechanism for audit failures.

### DQ-027 — SESSION_TIMEOUT_MIN System Parameter is Dead Configuration
**Severity:** MEDIUM  
**Table/Object:** PKG_SECURITY.is_session_valid, SYSTEM_PARAMETERS (SECURITY.SESSION_TIMEOUT_MIN)  
**Description:** ADDED by DA Agent 2 (pass 2). `PKG_SECURITY` declares a private constant `c_session_timeout_min := 30` and uses it directly in `is_session_valid`. The function never calls `PKG_COMMON.get_param('SECURITY','SESSION_TIMEOUT_MIN')`. The SYSTEM_PARAMETERS row with value '30' is documentation only — changing it has no runtime effect. Administrators who update this parameter believe they are changing the timeout, but the hard-coded constant is never overridden.  
**Impact:** Runtime session timeout is always exactly 30 minutes regardless of SYSTEM_PARAMETERS value. The same defect was noted for `PASSWORD_MIN_LENGTH` — `change_password` checks `LENGTH(p_new_password) < 8` as a literal, never reading the parameter.  
**Recommendation:** Replace `c_session_timeout_min := 30` with `c_session_timeout_min := NVL(PKG_COMMON.get_param_number('SECURITY','SESSION_TIMEOUT_MIN'), 30)`. Apply the same fix to password minimum length.

### DQ-028 — Tenure Calculation Rounding Divergence: VW_ACTIVE_EMPLOYEES vs PKG_EMPLOYEE
**Severity:** LOW  
**Table/Object:** VW_ACTIVE_EMPLOYEES, PKG_EMPLOYEE.get_tenure_years  
**Description:** ADDED by DA Agent 2 (pass 2). Two tenure-year calculations exist with different rounding functions: `VW_ACTIVE_EMPLOYEES` uses `TRUNC(MONTHS_BETWEEN(SYSDATE, HIRE_DATE) / 12, 1)` (truncates to 1 decimal); `PKG_EMPLOYEE.get_tenure_years` uses `ROUND(MONTHS_BETWEEN(v_end_date, HIRE_DATE) / 12, 1)` (rounds to 1 decimal). For an employee hired 2 years and 8 months ago, the view returns 2.6 and the function returns 2.7. Reports and leave eligibility checks may show different tenure depending on which source is used.  
**Impact:** Minor reporting inconsistency; leave tenure gate calculations use the PKG_EMPLOYEE function (authoritative); the view is for display only.  
**Recommendation:** Standardize on ROUND for tenure display; update VW_ACTIVE_EMPLOYEES TENURE_YEARS formula to match PKG_EMPLOYEE.get_tenure_years.

### DQ-029 — change_password Accepts Old Password Without Verifying It
**Severity:** HIGH  
**Table/Object:** PKG_SECURITY.change_password, USER_CREDENTIALS  
**Description:** ADDED from PKG_SECURITY.pkb source recovery. `change_password(p_emp_id, p_old_password, p_new_password)` accepts a `p_old_password` parameter but never uses it. The procedure applies complexity checks and logs an audit record, but does not verify that `p_old_password` matches the value stored in USER_CREDENTIALS. Any authenticated session can change any employee's password without knowing the current password — the old-password field is purely cosmetic.  
**Impact:** Privilege escalation: a compromised session for any employee can silently reset credentials. Combined with the authentication bypass (DQ-003), the system has no effective password security.  
**Recommendation:** Implement old-password verification: retrieve the stored hash for `p_emp_id` from USER_CREDENTIALS, hash `p_old_password` with `hash_password()`, and raise `ORA-20313` if they do not match before proceeding with the update.

### DQ-031 — import_time_attendance Is a TODO Stub That Silently Claims Success

**Severity:** HIGH  
**Table/Object:** PKG_INTEGRATION.import_time_attendance, TIME_ATTENDANCE_RECORDS (implied destination)  
**Description:** ADDED from PKG_INTEGRATION.pkb source recovery. `import_time_attendance` reads each line of the input CSV and increments `v_imported` for every non-comment, non-empty line, but contains no INSERT, UPDATE, or MERGE statement — only a `TODO: Implement actual parsing and database update` comment. After the loop completes, `PKG_COMMON.log_info` logs `'Imported: N, Errors: 0'` where N equals the number of valid CSV lines. The procedure reports success while writing nothing to the database. There is no destination table (TIME_ATTENDANCE_RECORDS) in the DDL, and no link to PAYROLL_DETAILS or PAYROLL_RUNS is defined anywhere in the codebase.  
**Impact:** Any scheduler job or operator invoking `import_time_attendance` will receive a success log entry and believe time data was loaded. Hourly payroll calculations have no automated data feed. If operators are relying on this import for payroll correctness, hours data has never been written to the database through this path.  
**Recommendation:** (1) Determine whether a live time and attendance system exists and whether it feeds the database via a separate mechanism. (2) If this procedure is intended to be active, create the TIME_ATTENDANCE_RECORDS table (DDL needed) and implement the CSV parse + INSERT logic. (3) Add a COMMIT or SAVEPOINT boundary so per-line errors can be isolated without silent data loss. (4) Change the success log message to distinguish "lines read" from "rows inserted" so operators are not misled.

---

### DQ-032 — leave_utilization_report Does Not Project CALENDAR_YEAR; RPT_LEAVE_UTILIZATION Cannot Be Multi-Year

**Severity:** MEDIUM  
**Table/Object:** `PKG_REPORTING.leave_utilization_report`, `RPT_LEAVE_UTILIZATION` (inferred)  
**Description:** ADDED from PKG_REPORTING.pkb analysis. `leave_utilization_report` filters `LEAVE_BALANCES` on `WHERE lb.CALENDAR_YEAR = p_year` but the `SELECT` list does not project `CALENDAR_YEAR` as a cursor column. The REF CURSOR result therefore contains no column identifying which calendar year each row belongs to. If `refresh_reporting_tables` is ever implemented and populates `RPT_LEAVE_UTILIZATION` by iterating years and loading cursor output, consecutive year loads would produce indistinguishable rows — the only way to separate years would be by `LOAD_TIMESTAMP`, which is fragile.  
**Impact:** Any year-over-year leave trend report reading `RPT_LEAVE_UTILIZATION` directly would be unable to correctly filter or pivot by year. A correct implementation of the refresh procedure must inject `CALENDAR_YEAR` as an explicit INSERT column, which means the cursor output alone is insufficient — the procedure must carry the year value as a separate bind variable when writing to the snapshot table.  
**Recommendation:** Add `lb.CALENDAR_YEAR` to the `SELECT` list of `leave_utilization_report` (no logic change — just project the grouped/filtered value). Add a `CALENDAR_YEAR NUMBER(4)` column to the `RPT_LEAVE_UTILIZATION` DDL when it is created. Include `CALENDAR_YEAR` in the `GROUP BY` clause (it is already a filter, so adding it to `GROUP BY` is a no-op semantically but makes the projection explicit).

---

### DQ-030 — Declared Exceptions e_account_locked and e_session_expired Are Never Raised
**Severity:** MEDIUM  
**Table/Object:** PKG_SECURITY (package spec), USER_CREDENTIALS  
**Description:** ADDED from PKG_SECURITY.pks source recovery. The package specification declares `e_account_locked` (ORA-20302) and `e_session_expired` (ORA-20303) as named exceptions. Neither is raised anywhere in the package body. `authenticate()` never triggers `e_account_locked` regardless of failed attempts (no lockout logic exists — see DQ-023). `is_session_valid()` returns FALSE for expired sessions rather than raising `e_session_expired`. Callers that catch these exceptions by name are never triggered; callers that rely on the exception being raised will miss the expiry/lockout condition entirely.  
**Impact:** Any Oracle Forms caller that branches on `WHEN PKG_SECURITY.e_session_expired` will never execute that branch. Session expiry silently returns FALSE with no exception path, risking silent access continuation if the caller does not check the BOOLEAN return value.  
**Recommendation:** Raise `e_session_expired` inside `is_session_valid` instead of returning FALSE, and raise `e_account_locked` once a lockout counter is implemented (DQ-023).
