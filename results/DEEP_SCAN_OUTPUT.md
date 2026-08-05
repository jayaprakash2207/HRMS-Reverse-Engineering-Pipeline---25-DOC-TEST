=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/data/seed/01_reference_data.sql ===

**Tables Written To:**
- LOCATIONS
- JOB_GRADES
- DEPARTMENTS
- JOB_TITLES
- LEAVE_TYPES
- PAY_ELEMENTS
- HOLIDAYS
- SYSTEM_PARAMETERS

---

**LOCATIONS — all rows:**

| LOCATION_CODE | LOCATION_NAME | ADDRESS_LINE1 | CITY | STATE_PROVINCE | POSTAL_CODE | COUNTRY_CODE | PHONE | ACTIVE_FLAG | CREATED_BY |
|---|---|---|---|---|---|---|---|---|---|
| HQ | Corporate Headquarters | 100 Main Street | New York | NY | 10001 | US | 212-555-1000 | Y | SYSTEM |
| CHI | Chicago Regional Office | 200 Michigan Avenue | Chicago | IL | 60601 | US | 312-555-2000 | Y | SYSTEM |
| SF | San Francisco Branch | 50 California Street | San Francisco | CA | 94111 | US | 415-555-3000 | Y | SYSTEM |

---

**JOB_GRADES — all rows (salary bands are business rules):**

| GRADE_ID | GRADE_NAME | GRADE_LEVEL | MIN_SALARY | MAX_SALARY | ACTIVE_FLAG |
|---|---|---|---|---|---|
| 1 | Entry Level | 1 | 35000 | 55000 | Y |
| 2 | Junior | 2 | 45000 | 70000 | Y |
| 3 | Mid-Level | 3 | 60000 | 90000 | Y |
| 4 | Senior | 4 | 80000 | 120000 | Y |
| 5 | Lead | 5 | 95000 | 145000 | Y |
| 6 | Manager | 6 | 110000 | 170000 | Y |
| 7 | Senior Manager | 7 | 130000 | 200000 | Y |
| 8 | Director | 8 | 160000 | 250000 | Y |
| 9 | VP | 9 | 200000 | 350000 | Y |
| 10 | C-Suite | 10 | 300000 | 600000 | Y |

---

**DEPARTMENTS — all rows:**

| DEPT_ID | DEPT_CODE | DEPT_NAME | COST_CENTER | PARENT_DEPT_ID | LOCATION_CODE | ACTIVE_FLAG |
|---|---|---|---|---|---|---|
| 1 | EXEC | Executive Office | CC-1000 | NULL | HQ | Y |
| 10 | HR | Human Resources | CC-1100 | 1 | HQ | Y |
| 20 | FIN | Finance & Accounting | CC-1200 | 1 | HQ | Y |
| 30 | IT | Information Technology | CC-1300 | 1 | CHI | Y |
| 31 | ITDEV | IT - Development | CC-1310 | 30 | CHI | Y |
| 32 | ITOPS | IT - Operations | CC-1320 | 30 | CHI | Y |
| 40 | SALES | Sales | CC-1400 | 1 | SF | Y |
| 50 | MKT | Marketing | CC-1500 | 1 | SF | Y |
| 60 | OPS | Operations | CC-1600 | 1 | CHI | Y |
| 70 | LEGAL | Legal & Compliance | CC-1700 | 1 | HQ | Y |

All MANAGER_EMP_ID values are NULL at insert time (set later by UPDATE in 02_employee_data.sql).

---

**JOB_TITLES — all rows:**

| JOB_ID | JOB_CODE | JOB_TITLE | GRADE_ID | EEO_CATEGORY | ACTIVE_FLAG |
|---|---|---|---|---|---|
| 1 | CEO | Chief Executive Officer | 10 | 1.1 | Y |
| 2 | CFO | Chief Financial Officer | 10 | 1.1 | Y |
| 3 | CIO | Chief Information Officer | 10 | 1.1 | Y |
| 10 | VP-HR | VP of Human Resources | 9 | 1.1 | Y |
| 11 | VP-FIN | VP of Finance | 9 | 1.1 | Y |
| 12 | VP-SALES | VP of Sales | 9 | 1.1 | Y |
| 20 | DIR-IT | Director of IT | 8 | 1.2 | Y |
| 21 | DIR-HR | Director of HR | 8 | 1.2 | Y |
| 30 | MGR-DEV | Development Manager | 6 | 1.2 | Y |
| 31 | MGR-OPS | Operations Manager | 6 | 1.2 | Y |
| 32 | MGR-PAY | Payroll Manager | 6 | 1.2 | Y |
| 33 | MGR-SALES | Sales Manager | 6 | 1.2 | Y |
| 40 | SR-DEV | Senior Developer | 4 | 2.0 | Y |
| 41 | SR-DBA | Senior DBA | 4 | 2.0 | Y |
| 42 | SR-ACCT | Senior Accountant | 4 | 2.0 | Y |
| 43 | SR-SALES | Senior Sales Rep | 4 | 2.0 | Y |
| 50 | DEV | Software Developer | 3 | 2.0 | Y |
| 51 | QA | QA Analyst | 3 | 2.0 | Y |
| 52 | ACCT | Accountant | 3 | 2.0 | Y |
| 53 | HR-SPEC | HR Specialist | 3 | 2.0 | Y |
| 54 | SALES-REP | Sales Representative | 3 | 2.0 | Y |
| 60 | JR-DEV | Junior Developer | 2 | 2.0 | Y |
| 61 | HR-ASST | HR Assistant | 2 | 5.0 | Y |
| 62 | ACCT-CLK | Accounting Clerk | 2 | 5.0 | Y |
| 70 | INTERN | Intern | 1 | 2.0 | Y |
| 71 | RECEPT | Receptionist | 1 | 5.0 | Y |

---

**LEAVE_TYPES — all rows (all numeric fields are business rules):**

| LEAVE_TYPE_ID | LEAVE_TYPE_CODE | LEAVE_TYPE_NAME | ACCRUAL_FLAG | ACCRUAL_RATE | ACCRUAL_FREQUENCY | MAX_BALANCE | CARRYOVER_MAX | CARRYOVER_EXPIRY (months) | REQUIRES_APPROVAL | MIN_TENURE_DAYS |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | PTO | Paid Time Off | Y | 1.25 | MONTHLY | 20 | 5 | 3 | Y | 0 |
| 2 | SICK | Sick Leave | Y | 0.833 | MONTHLY | 10 | 10 | NULL | Y | 0 |
| 3 | COMP | Compensatory Time | N | NULL | NULL | NULL | 0 | NULL | Y | 90 |
| 4 | FMLA | Family Medical Leave | N | NULL | NULL | NULL | 0 | NULL | Y | 365 |
| 5 | JURY | Jury Duty | N | NULL | NULL | NULL | 0 | NULL | N | 0 |
| 6 | BEREAVE | Bereavement | N | NULL | NULL | NULL | 0 | NULL | N | 0 |

Business rules embedded:
- PTO accrues 1.25 days/month; max balance 20 days; carry-over max 5 days; carry-over expires after 3 months; no minimum tenure.
- SICK accrues 0.833 days/month; max balance 10 days; carry-over max 10 days (no expiry); no minimum tenure.
- COMP does not accrue; no carry-over; requires approval; employee must have 90+ days of tenure.
- FMLA does not accrue; no carry-over; requires approval; employee must have 365+ days of tenure (1 year).
- JURY and BEREAVE require no approval and no minimum tenure.

---

**PAY_ELEMENTS — all rows (all numeric fields are business rules):**

| ELEMENT_ID | ELEMENT_CODE | ELEMENT_NAME | ELEMENT_TYPE | CALCULATION_TYPE | DEFAULT_AMOUNT | DEFAULT_PERCENTAGE | GL_ACCOUNT_CODE | PRIORITY_ORDER | PRETAX_FLAG |
|---|---|---|---|---|---|---|---|---|---|
| 1 | BASE_PAY | Base Salary | EARNING | FLAT | NULL | NULL | 5100-100 | 1 | N |
| 100 | FED_TAX | Federal Income Tax | TAX | FORMULA | NULL | NULL | 2100-100 | 10 | N |
| 101 | STATE_TAX | State Income Tax | TAX | FORMULA | NULL | NULL | 2100-200 | 11 | N |
| 102 | FICA | Social Security (FICA) | TAX | FORMULA | NULL | NULL | 2100-300 | 12 | N |
| 103 | MEDICARE | Medicare | TAX | FORMULA | NULL | NULL | 2100-400 | 13 | N |
| 200 | 401K_EE | 401(k) Employee Contribution | DEDUCTION | PERCENTAGE | NULL | 6 | 2200-100 | 20 | Y |
| 201 | MED_EE | Medical Insurance (Employee) | BENEFIT | FLAT | 250 | NULL | 2200-200 | 21 | Y |
| 202 | DENTAL_EE | Dental Insurance (Employee) | BENEFIT | FLAT | 45 | NULL | 2200-300 | 22 | Y |
| 203 | VISION_EE | Vision Insurance (Employee) | BENEFIT | FLAT | 15 | NULL | 2200-400 | 23 | Y |
| 204 | LIFE_INS | Life Insurance | BENEFIT | FLAT | 25 | NULL | 2200-500 | 24 | N |
| 205 | HSA | Health Savings Account | DEDUCTION | FLAT | 150 | NULL | 2200-600 | 25 | Y |

Business rules embedded:
- 401(k) employee default contribution: 6% of earnings; pre-tax.
- Medical insurance default employee deduction: $250/period; pre-tax.
- Dental insurance default employee deduction: $45/period; pre-tax.
- Vision insurance default employee deduction: $15/period; pre-tax.
- Life insurance default employee deduction: $25/period; NOT pre-tax.
- HSA default contribution: $150/period; pre-tax.

---

**HOLIDAYS — all rows (2024 calendar; LOCATION_CODE = NULL = all locations):**

| HOLIDAY_ID | HOLIDAY_NAME | HOLIDAY_DATE |
|---|---|---|
| 1 | New Year's Day | 2024-01-01 |
| 2 | Martin Luther King Jr. Day | 2024-01-15 |
| 3 | Presidents' Day | 2024-02-19 |
| 4 | Memorial Day | 2024-05-27 |
| 5 | Independence Day | 2024-07-04 |
| 6 | Labor Day | 2024-09-02 |
| 7 | Thanksgiving | 2024-11-28 |
| 8 | Day After Thanksgiving | 2024-11-29 |
| 9 | Christmas Eve | 2024-12-24 |
| 10 | Christmas Day | 2024-12-25 |

All 10 holidays apply to all locations (LOCATION_CODE = NULL).

---

**SYSTEM_PARAMETERS — all rows:**

| PARAM_ID | PARAM_GROUP | PARAM_CODE | PARAM_VALUE | EDITABLE_FLAG |
|---|---|---|---|---|
| 1 | SYSTEM | APP_VERSION | 4.2.0 | N |
| 2 | SYSTEM | COMPANY_NAME | Acme Corporation | Y |
| 3 | PAYROLL | DEFAULT_PAY_FREQUENCY | MONTHLY | Y |
| 4 | PAYROLL | FISCAL_YEAR_START | 10 | Y |
| 5 | SECURITY | SESSION_TIMEOUT_MIN | 30 | Y |
| 6 | SECURITY | PASSWORD_MIN_LENGTH | 8 | Y |
| 7 | NOTIFICATION | SMTP_HOST | smtp.internal.company.com | Y |
| 8 | NOTIFICATION | FROM_ADDRESS | hrms-noreply@company.com | Y |
| 9 | INTEGRATION | GL_FEED_STATUS | ACTIVE | Y |
| 10 | INTEGRATION | BENEFITS_FEED_STATUS | ACTIVE | Y |

Business rules embedded:
- Application version: 4.2.0 (non-editable).
- Default payroll frequency: MONTHLY.
- Fiscal year start month: 10 (October).
- Session timeout: 30 minutes.
- Minimum password length: 8 characters.
- APP_VERSION is non-editable; all other parameters are editable.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/data/seed/02_employee_data.sql ===

**Tables Written To:**
- EMPLOYEES (INSERT)
- SALARY_RECORDS (INSERT)
- DEPARTMENTS (UPDATE — manager assignments)

---

**EMPLOYEES — all rows:**

| EMP_ID | EMP_NUMBER | FIRST_NAME | LAST_NAME | EMAIL | PHONE_WORK | HIRE_DATE | DEPT_ID | JOB_ID | MANAGER_EMP_ID | LOCATION_CODE | EMPLOYMENT_TYPE | EMPLOYMENT_STATUS | GENDER | DATE_OF_BIRTH | MARITAL_STATUS | ACTIVE_FLAG | TERMINATION_DATE | TERMINATION_REASON |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EMP-000001 | JAMES | RICHARDSON | james.richardson@company.com | 212-555-1001 | 2010-03-15 | 1 | 1 | NULL | HQ | FULL_TIME | ACTIVE | M | 1968-07-22 | MARRIED | Y | — | — |
| 2 | EMP-000002 | SARAH | CHEN | sarah.chen@company.com | 212-555-1002 | 2012-06-01 | 20 | 2 | 1 | HQ | FULL_TIME | ACTIVE | F | 1975-11-03 | MARRIED | Y | — | — |
| 3 | EMP-000003 | MICHAEL | OCONNOR | michael.oconnor@company.com | 312-555-2001 | 2011-09-12 | 30 | 3 | 1 | CHI | FULL_TIME | ACTIVE | M | 1972-03-18 | DIVORCED | Y | — | — |
| 10 | EMP-000010 | PATRICIA | WILLIAMS | patricia.williams@company.com | 212-555-1101 | 2013-02-18 | 10 | 10 | 1 | HQ | FULL_TIME | ACTIVE | F | 1978-09-14 | SINGLE | Y | — | — |
| 11 | EMP-000011 | DAVID | MARTINEZ | david.martinez@company.com | 212-555-1102 | 2016-08-22 | 10 | 53 | 10 | HQ | FULL_TIME | ACTIVE | M | 1985-04-30 | MARRIED | Y | — | — |
| 12 | EMP-000012 | EMILY | JOHNSON | emily.johnson@company.com | 212-555-1103 | 2019-01-07 | 10 | 61 | 10 | HQ | FULL_TIME | ACTIVE | F | 1994-12-08 | SINGLE | Y | — | — |
| 20 | EMP-000020 | ROBERT | KUMAR | robert.kumar@company.com | 212-555-1201 | 2014-05-12 | 20 | 11 | 2 | HQ | FULL_TIME | ACTIVE | M | 1980-01-25 | MARRIED | Y | — | — |
| 21 | EMP-000021 | JENNIFER | PARK | jennifer.park@company.com | 212-555-1202 | 2017-03-20 | 20 | 32 | 20 | HQ | FULL_TIME | ACTIVE | F | 1983-06-17 | MARRIED | Y | — | — |
| 22 | EMP-000022 | THOMAS | BAKER | thomas.baker@company.com | 212-555-1203 | 2018-09-10 | 20 | 42 | 21 | HQ | FULL_TIME | ACTIVE | M | 1987-02-14 | SINGLE | Y | — | — |
| 23 | EMP-000023 | LISA | WONG | lisa.wong@company.com | 212-555-1204 | 2020-11-02 | 20 | 52 | 21 | HQ | FULL_TIME | ACTIVE | F | 1992-08-21 | SINGLE | Y | — | — |
| 24 | EMP-000024 | ANDREW | PATEL | andrew.patel@company.com | 212-555-1205 | 2022-06-15 | 20 | 62 | 21 | HQ | FULL_TIME | ACTIVE | M | 1997-10-30 | SINGLE | Y | — | — |
| 30 | EMP-000030 | RACHEL | THOMPSON | rachel.thompson@company.com | 312-555-2101 | 2015-01-05 | 30 | 20 | 3 | CHI | FULL_TIME | ACTIVE | F | 1979-05-12 | MARRIED | Y | — | — |
| 31 | EMP-000031 | KEVIN | GARCIA | kevin.garcia@company.com | 312-555-2102 | 2016-04-18 | 31 | 30 | 30 | CHI | FULL_TIME | ACTIVE | M | 1984-11-07 | MARRIED | Y | — | — |
| 32 | EMP-000032 | MARIA | RODRIGUEZ | maria.rodriguez@company.com | 312-555-2103 | 2017-07-24 | 31 | 40 | 31 | CHI | FULL_TIME | ACTIVE | F | 1986-03-29 | SINGLE | Y | — | — |
| 33 | EMP-000033 | DANIEL | LEE | daniel.lee@company.com | 312-555-2104 | 2018-02-12 | 31 | 41 | 31 | CHI | FULL_TIME | ACTIVE | M | 1982-09-05 | MARRIED | Y | — | — |
| 34 | EMP-000034 | JESSICA | NGUYEN | jessica.nguyen@company.com | 312-555-2105 | 2019-05-06 | 31 | 50 | 31 | CHI | FULL_TIME | ACTIVE | F | 1991-07-15 | SINGLE | Y | — | — |
| 35 | EMP-000035 | CHRIS | ANDERSON | chris.anderson@company.com | 312-555-2106 | 2020-08-17 | 31 | 50 | 31 | CHI | FULL_TIME | ACTIVE | M | 1993-01-22 | SINGLE | Y | — | — |
| 36 | EMP-000036 | PRIYA | SHARMA | priya.sharma@company.com | 312-555-2107 | 2021-03-22 | 31 | 51 | 31 | CHI | FULL_TIME | ACTIVE | F | 1995-06-10 | SINGLE | Y | — | — |
| 37 | EMP-000037 | ALEX | TAYLOR | alex.taylor@company.com | 312-555-2108 | 2022-01-10 | 31 | 60 | 31 | CHI | FULL_TIME | ACTIVE | M | 1998-04-18 | SINGLE | Y | — | — |
| 40 | EMP-000040 | MARK | DAVIS | mark.davis@company.com | 415-555-3101 | 2014-11-03 | 40 | 12 | 1 | SF | FULL_TIME | ACTIVE | M | 1977-08-09 | MARRIED | Y | — | — |
| 41 | EMP-000041 | ASHLEY | BROWN | ashley.brown@company.com | 415-555-3102 | 2017-06-19 | 40 | 33 | 40 | SF | FULL_TIME | ACTIVE | F | 1985-02-28 | SINGLE | Y | — | — |
| 42 | EMP-000042 | JASON | WILSON | jason.wilson@company.com | 415-555-3103 | 2019-09-16 | 40 | 43 | 41 | SF | FULL_TIME | ACTIVE | M | 1989-12-01 | MARRIED | Y | — | — |
| 43 | EMP-000043 | SAMANTHA | MOORE | samantha.moore@company.com | 415-555-3104 | 2021-02-08 | 40 | 54 | 41 | SF | FULL_TIME | ACTIVE | F | 1993-10-25 | SINGLE | Y | — | — |
| 99 | EMP-000099 | BRIAN | FOSTER | brian.foster@company.com | 312-555-2199 | 2018-04-02 | 31 | 50 | 31 | CHI | FULL_TIME | TERMINATED | M | 1990-05-14 | SINGLE | N | 2023-06-30 | VOLUNTARY |

Total: 25 employees (24 active, 1 terminated).

---

**SALARY_RECORDS — all rows (all BASE_SALARY values are business data):**

| SALARY_ID | EMP_ID | EFFECTIVE_DATE | END_DATE | BASE_SALARY (USD, ANNUAL) | PAY_FREQUENCY | SALARY_BASIS | CHANGE_REASON |
|---|---|---|---|---|---|---|---|
| 1 | 1 | 2023-01-01 | NULL | 450000 | MONTHLY | ANNUAL | Annual review |
| 2 | 2 | 2023-01-01 | NULL | 380000 | MONTHLY | ANNUAL | Annual review |
| 3 | 3 | 2023-01-01 | NULL | 370000 | MONTHLY | ANNUAL | Annual review |
| 10 | 10 | 2023-07-01 | NULL | 240000 | MONTHLY | ANNUAL | Promotion |
| 11 | 11 | 2023-01-01 | NULL | 78000 | MONTHLY | ANNUAL | Annual review |
| 12 | 12 | 2023-01-01 | NULL | 52000 | MONTHLY | ANNUAL | Annual review |
| 20 | 20 | 2023-01-01 | NULL | 260000 | MONTHLY | ANNUAL | Annual review |
| 21 | 21 | 2023-01-01 | NULL | 135000 | MONTHLY | ANNUAL | Annual review |
| 22 | 22 | 2023-01-01 | NULL | 95000 | MONTHLY | ANNUAL | Annual review |
| 23 | 23 | 2023-01-01 | NULL | 72000 | MONTHLY | ANNUAL | Annual review |
| 24 | 24 | 2022-06-15 | NULL | 48000 | MONTHLY | ANNUAL | New hire |
| 30 | 30 | 2023-01-01 | NULL | 195000 | MONTHLY | ANNUAL | Annual review |
| 31 | 31 | 2023-01-01 | NULL | 145000 | MONTHLY | ANNUAL | Annual review |
| 32 | 32 | 2023-01-01 | NULL | 115000 | MONTHLY | ANNUAL | Annual review |
| 33 | 33 | 2023-01-01 | NULL | 110000 | MONTHLY | ANNUAL | Annual review |
| 34 | 34 | 2023-01-01 | NULL | 82000 | MONTHLY | ANNUAL | Annual review |
| 35 | 35 | 2023-01-01 | NULL | 78000 | MONTHLY | ANNUAL | Annual review |
| 36 | 36 | 2023-01-01 | NULL | 70000 | MONTHLY | ANNUAL | Annual review |
| 37 | 37 | 2022-01-10 | NULL | 55000 | MONTHLY | ANNUAL | New hire |
| 40 | 40 | 2023-01-01 | NULL | 280000 | MONTHLY | ANNUAL | Annual review |
| 41 | 41 | 2023-01-01 | NULL | 130000 | MONTHLY | ANNUAL | Annual review |
| 42 | 42 | 2023-01-01 | NULL | 105000 | MONTHLY | ANNUAL | Annual review |
| 43 | 43 | 2023-01-01 | NULL | 65000 | MONTHLY | ANNUAL | Annual review |

All records have END_DATE = NULL (current, open-ended). ACTIVE_FLAG = 'Y' on all.

---

**DEPARTMENTS UPDATE statements (manager assignments):**

```
UPDATE DEPARTMENTS SET MANAGER_EMP_ID = 10 WHERE DEPT_ID = 10;   -- HR mgr = Patricia Williams
UPDATE DEPARTMENTS SET MANAGER_EMP_ID = 2  WHERE DEPT_ID = 20;   -- Finance mgr = Sarah Chen
UPDATE DEPARTMENTS SET MANAGER_EMP_ID = 3  WHERE DEPT_ID = 30;   -- IT mgr = Michael OConnor
UPDATE DEPARTMENTS SET MANAGER_EMP_ID = 30 WHERE DEPT_ID = 30;   -- IT also set to Rachel Thompson (overrides prior)
UPDATE DEPARTMENTS SET MANAGER_EMP_ID = 31 WHERE DEPT_ID = 31;   -- ITDEV mgr = Kevin Garcia
UPDATE DEPARTMENTS SET MANAGER_EMP_ID = 40 WHERE DEPT_ID = 40;   -- Sales mgr = Mark Davis
UPDATE DEPARTMENTS SET MANAGER_EMP_ID = 1  WHERE DEPT_ID = 1;    -- Exec mgr = James Richardson
```

Note: DEPT_ID=30 is updated twice in sequence — first to EMP_ID=3 (Michael OConnor/CIO), then to EMP_ID=30 (Rachel Thompson/Dir-IT). Final effective value is EMP_ID=30.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql ===

**Type:** Oracle Forms PL/SQL Library (PLL). Attached to all HRMS forms via ATTACH_LIBRARY. No cross-package dependencies (standalone).

**Dependencies:**
- PKG_COMMON.log_error (called from handle_error)
- PKG_SECURITY.is_session_valid (called from check_session)
- Global variables: :GLOBAL.current_user, :GLOBAL.session_id

**Global variables read:**
- :GLOBAL.current_user
- :GLOBAL.session_id
- :SYSTEM.MODE (in toolbar_query)
- :SYSTEM.FORM_STATUS (not shown here but referenced by callers)

---

**Procedures:**

**handle_error(p_module VARCHAR2, p_location VARCHAR2)**
- Reads SQLCODE into v_errcode (NUMBER), SQLERRM into v_errmsg (VARCHAR2(500)).
- Calls PKG_COMMON.log_error(p_module, p_location, v_errmsg, NVL(:GLOBAL.current_user, USER)) inside a nested BEGIN/EXCEPTION block that suppresses any logging failure (WHEN OTHERS THEN NULL).
- Calls MESSAGE() twice with the text `p_module || '.' || p_location || ': ' || v_errmsg`. (Intentionally called twice — Oracle Forms requires two calls to display on the status bar.)
- Raises FORM_TRIGGER_FAILURE.

**toolbar_save()**
- Calls COMMIT_FORM.

**toolbar_clear()**
- Calls CLEAR_FORM(ASK_COMMIT).

**toolbar_query()**
- IF :SYSTEM.MODE = 'NORMAL' THEN ENTER_QUERY.
- ELSIF :SYSTEM.MODE = 'ENTER-QUERY' THEN EXECUTE_QUERY.

**toolbar_first()** — calls FIRST_RECORD.
**toolbar_prev()** — calls PREVIOUS_RECORD.
**toolbar_next()** — calls NEXT_RECORD.
**toolbar_last()** — calls LAST_RECORD.
**toolbar_insert()** — calls CREATE_RECORD.
**toolbar_delete()** — calls DELETE_RECORD.
**toolbar_exit()** — calls EXIT_FORM(ASK_COMMIT).

**format_date(p_date DATE) RETURN VARCHAR2**
- Returns TO_CHAR(p_date, 'MM/DD/YYYY').

**format_datetime(p_date DATE) RETURN VARCHAR2**
- Returns TO_CHAR(p_date, 'MM/DD/YYYY HH24:MI:SS').

**get_current_user() RETURN VARCHAR2**
- Returns NVL(:GLOBAL.current_user, USER).

**get_session_id() RETURN NUMBER**
- Returns TO_NUMBER(:GLOBAL.session_id).
- Exception WHEN VALUE_ERROR: returns NULL.

**check_session()**
- Calls get_session_id(); if NULL, MESSAGE('No active session. Please log in.') then RAISE FORM_TRIGGER_FAILURE.
- Calls PKG_SECURITY.is_session_valid(get_session_id()); if returns FALSE, MESSAGE('Session has expired. Please log in again.') then RAISE FORM_TRIGGER_FAILURE.

**refresh_lov(p_lov_name VARCHAR2)**
- Constructs v_rg_name = 'RG_' || UPPER(REPLACE(p_lov_name, 'LOV_', '')).
- If FIND_GROUP(v_rg_name) is not null (ID_NULL check), calls POPULATE_GROUP(v_rg_name).

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_VALIDATION_LIB.pll.sql ===

**Type:** Oracle Forms PL/SQL Library (PLL). Client-side validation. Attached to all HRMS forms. Note documented in file: many validations duplicate PKG_VALIDATION server-side logic; they can drift out of sync.

**Dependencies:**
- JOB_GRADES table (direct SELECT in validate_salary_range)
- No package dependencies.

---

**Functions:**

**validate_email(p_email VARCHAR2) RETURN BOOLEAN**
- If p_email IS NULL: returns TRUE (NULL treated as valid; required check is separate).
- Finds position of '@' using INSTR. Returns FALSE if:
  - v_at_pos = 0 (no '@')
  - v_at_pos = 1 ('@' is first character)
  - v_at_pos = LENGTH(p_email) ('@' is last character)
- Finds position of '.' after '@' using INSTR(p_email, '.', v_at_pos). Returns FALSE if:
  - v_dot_pos = 0 (no '.' after '@')
  - v_dot_pos = v_at_pos + 1 ('.' immediately after '@')
  - v_dot_pos = LENGTH(p_email) ('.' is last character)
- Returns TRUE otherwise.
- **Known bug documented in code:** Only checks for one dot after '@'. Rejects valid emails with subdomains (e.g. user@mail.company.com). Server-side PKG_VALIDATION uses REGEXP_LIKE with a more permissive pattern. These can drift.

**validate_phone(p_phone VARCHAR2) RETURN BOOLEAN**
- If p_phone IS NULL: returns TRUE.
- Strips non-digits using TRANSLATE(p_phone, '0123456789()-. +x', '0123456789') into v_digits VARCHAR2(20).
- Returns FALSE if LENGTH(v_digits) NOT IN (10, 11).
- Returns TRUE otherwise.
- Business rule: US phone must be 10 or 11 digits.

**validate_ssn(p_ssn VARCHAR2) RETURN BOOLEAN**
- If p_ssn IS NULL: returns TRUE.
- Strips non-digits using TRANSLATE(p_ssn, '0123456789-', '0123456789') into v_digits VARCHAR2(20).
- Returns FALSE if LENGTH(v_digits) != 9.
- Returns FALSE if SUBSTR(v_digits, 1, 3) = '000' (area segment all zeros).
- Returns FALSE if SUBSTR(v_digits, 4, 2) = '00' (group segment all zeros).
- Returns FALSE if SUBSTR(v_digits, 6, 4) = '0000' (serial segment all zeros).
- Returns TRUE otherwise.
- Business rules: SSN must be exactly 9 digits; none of the three segments (positions 1-3, 4-5, 6-9) may be all zeros.

**validate_date_not_future(p_date DATE) RETURN BOOLEAN**
- Returns TRUE if p_date IS NULL OR TRUNC(p_date) <= TRUNC(SYSDATE).
- Returns FALSE if TRUNC(p_date) > TRUNC(SYSDATE).

**validate_salary_range(p_salary NUMBER, p_grade_id NUMBER) RETURN VARCHAR2**
- Returns NULL string if valid; returns error message string if invalid.
- If p_salary IS NULL OR p_grade_id IS NULL: returns NULL (no validation).
- Executes: `SELECT MIN_SALARY, MAX_SALARY INTO v_min, v_max FROM JOB_GRADES WHERE GRADE_ID = p_grade_id`
- If p_salary < v_min: returns `'Below minimum (' || TO_CHAR(v_min, 'FM$999,999') || ')'`
- If p_salary > v_max: returns `'Exceeds maximum (' || TO_CHAR(v_max, 'FM$999,999') || ')'`
- Returns NULL if within range.
- EXCEPTION WHEN NO_DATA_FOUND: returns 'Invalid grade'.
- **Known bug documented in code:** Comment says "Uses a hard-coded cache populated at form startup and never refreshed." Code actually performs a direct DB query (not a cache). Comment/code mismatch — the code is the authoritative behavior.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/menus/HRMS_MENU.mmb.sql ===

**Type:** Oracle Forms Menu Module source representation (compiled binary = HRMS_MENU.mmb). This file is a comment-only documentation of menu structure; no executable PL/SQL code.

**Menu Bar: MAIN_MENUBAR**

**File menu:**
- Save → COMMIT_FORM
- Save & Exit → COMMIT_FORM; EXIT_FORM
- Print → RUN_PRODUCT
- Exit → EXIT_FORM

**Edit menu:**
- Clear Record → CLEAR_RECORD
- Duplicate Record → DUPLICATE_RECORD
- Delete Record → DELETE_RECORD
- Insert Record → CREATE_RECORD

**Query menu:**
- Enter Query → ENTER_QUERY
- Execute Query → EXECUTE_QUERY
- Cancel Query → EXIT_FORM
- Count Matching → COUNT_QUERY
- Fetch Next Set → SCROLL_DOWN

**Navigate menu:**
- First Record → FIRST_RECORD
- Previous Record → PREVIOUS_RECORD
- Next Record → NEXT_RECORD
- Last Record → LAST_RECORD
- Previous Block → PREVIOUS_BLOCK
- Next Block → NEXT_BLOCK

**Modules menu:**
- Employee Management → OPEN_FORM('HRMS_EMPLOYEE')
- Payroll Processing → OPEN_FORM('HRMS_PAYROLL')
- Leave Management → OPEN_FORM('HRMS_LEAVE')
- Performance Reviews → OPEN_FORM('HRMS_PERFORMANCE')
- Reports & Analytics → OPEN_FORM('HRMS_REPORTS')
- System Admin → OPEN_FORM('HRMS_ADMIN')

**Admin menu:**
- Change Password → SHOW_WINDOW('WIN_CHANGE_PWD')
- System Parameters → requires ADMIN permission
- User Management → requires ADMIN permission

**Help menu:**
- Contents → WEB.SHOW_DOCUMENT
- About HRMS → SHOW_ALERT('ALT_ABOUT')
- Support → WEB.SHOW_DOCUMENT

**Security:** Menu items are enabled/disabled at runtime based on PKG_SECURITY.has_permission() checks in WHEN-NEW-FORM-INSTANCE.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml ===

**Type:** Oracle Forms Module (HRMS_EMPLOYEE.fmb). Exported from Oracle Forms Builder 12c (12.2.1.4). Purpose: Employee maintenance master-detail form.

**Attached Libraries:** HRMS_COMMON_LIB, HRMS_VALIDATION_LIB

**Menu Module:** HRMS_MENU (MenuSource="File")

**Data Blocks:**
- EMPLOYEE (master), SALARY (detail), DEPENDENTS, EMERGENCY_CONTACTS, EMP_HISTORY (latter three defined but not shown in extract)

**Canvases:**
- CVS_MAIN (Tab canvas, 700×500): tab pages TP_PERSONAL ("Personal Information"), TP_JOB ("Job & Compensation"), TP_DEPENDENTS ("Dependents"), TP_HISTORY ("Employment History")
- CVS_TOOLBAR (Horizontal Toolbar, 700×38)

**Windows:**
- WIN_EMPLOYEE: Document style, 720×550, PrimaryCanvas=CVS_MAIN

**Alerts:**
- ALT_CONFIRM_EXIT: Caution style, "You have unsaved changes. Save before exiting?" — Button1="Save", Button2="Discard", Button3="Cancel"
- ALT_CONFIRM_DELETE: Stop style, "Are you sure you want to delete this employee record?" — Button1="Yes", Button2="No"

---

**FORM-LEVEL TRIGGERS:**

**WHEN-NEW-FORM-INSTANCE (FireInEnterQueryMode=No)**
- Gets session ID from GET_APPLICATION_PROPERTY(USERNAME) converted to NUMBER.
- Calls PKG_SECURITY.is_session_valid(v_session_id); if FALSE: MESSAGE('Session expired. Please log in again.') then RAISE FORM_TRIGGER_FAILURE.
- Sets MDI window title to 'HRMS - Employee Maintenance [' || :GLOBAL.current_user || ']'.
- Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'EMPLOYEE', 'EDIT'); if FALSE: sets EMPLOYEE block INSERT_ALLOWED, UPDATE_ALLOWED, DELETE_ALLOWED all to PROPERTY_FALSE.
- Sets EMPLOYEE block DEFAULT_WHERE = `'EMPLOYMENT_STATUS = ''ACTIVE'' AND ACTIVE_FLAG = ''Y'''`.
- Calls POPULATE_GROUP for RG_DEPARTMENTS, RG_JOB_TITLES, RG_LOCATIONS.
- Navigates to EMPLOYEE block and executes query.

**ON-ERROR (FireInEnterQueryMode=Yes)**
- v_errcode = ERROR_CODE; v_errtype = ERROR_TYPE (VARCHAR2(3)); v_errmsg = ERROR_TEXT (VARCHAR2(200)).
- errcode 40202 ("Field is protected against update"): NULL — suppressed silently.
- errcode 40401 ("No changes to save"): MESSAGE('No changes to save.').
- errcode 40501 ("Oracle error: unable to reserve record"): MESSAGE('Record is locked by another user. Please try again.').
- All other codes: MESSAGE(v_errtype || '-' || TO_CHAR(v_errcode) || ': ' || v_errmsg) then RAISE FORM_TRIGGER_FAILURE.

**KEY-EXIT (FireInEnterQueryMode=Yes)**
- If :SYSTEM.FORM_STATUS = 'CHANGED':
  - If SHOW_ALERT('ALT_CONFIRM_EXIT') = ALERT_BUTTON1: COMMIT_FORM.
  - Elsif SHOW_ALERT('ALT_CONFIRM_EXIT') = ALERT_BUTTON2: CLEAR_FORM(NO_VALIDATE).
  - Else: RAISE FORM_TRIGGER_FAILURE (cancel exit).
- Calls EXIT_FORM.

---

**BLOCK: EMPLOYEE**
- QueryDataSourceType=Table, QueryDataSourceName=HRMS.EMPLOYEES
- DMLDataTargetName=HRMS.EMPLOYEES
- QueryAllRecords=No, RecordsDisplayed=1, NavigationStyle=Same Record
- KeyMode=Unique, EnforcePrimaryKey=Yes
- InsertAllowed=Yes, UpdateAllowed=Yes, DeleteAllowed=Yes, QueryAllowed=Yes

**Items in EMPLOYEE block:**

| Item Name | Item Type | DataType | MaxLen | Required | Canvas/Tab | Visible | DB | Notes |
|---|---|---|---|---|---|---|---|---|
| EMP_ID | Text Field | Number | 10 | Yes | (hidden) | No | Yes | PK; InsertAllowed=No, UpdateAllowed=No |
| EMP_NUMBER | Text Field | Char | 20 | Yes | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | InsertAllowed=No, UpdateAllowed=No (auto-generated) |
| FIRST_NAME | Text Field | Char | 50 | Yes | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | CaseRestriction=Upper |
| LAST_NAME | Text Field | Char | 50 | Yes | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | CaseRestriction=Upper |
| DATE_OF_BIRTH | Text Field | Date | 11 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | FormatMask=MM/DD/YYYY |
| GENDER | List Item | Char | 1 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | Values: M=Male, F=Female, O=Other |
| MARITAL_STATUS | List Item | Char | 10 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | Values: SINGLE, MARRIED, DIVORCED, WIDOWED |
| EMAIL | Text Field | Char | 100 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | CaseRestriction=Lower |
| PHONE_WORK | Text Field | Char | 30 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | — |
| PHONE_MOBILE | Text Field | Char | 30 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | — |
| ADDRESS_LINE1 | Text Field | Char | 200 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | — |
| ADDRESS_LINE2 | Text Field | Char | 200 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | — |
| CITY | Text Field | Char | 100 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | — |
| STATE_PROVINCE | Text Field | Char | 100 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | — |
| POSTAL_CODE | Text Field | Char | 20 | No | CVS_PERSONAL/TP_PERSONAL | Yes | Yes | — |
| HIRE_DATE | Text Field | Date | 11 | Yes | CVS_JOB/TP_JOB | Yes | Yes | FormatMask=MM/DD/YYYY |
| DEPT_ID | Text Field | Number | 10 | Yes | CVS_JOB/TP_JOB | Yes | Yes | LOV=LOV_DEPARTMENTS |
| DEPT_NAME_DISP | Display Item | Char | 100 | No | CVS_JOB/TP_JOB | Yes | No | Non-DB display item |
| JOB_ID | Text Field | Number | 10 | Yes | CVS_JOB/TP_JOB | Yes | Yes | LOV=LOV_JOB_TITLES |
| JOB_TITLE_DISP | Display Item | Char | 100 | No | CVS_JOB/TP_JOB | Yes | No | Non-DB display item |
| MANAGER_EMP_ID | Text Field | Number | 10 | No | CVS_JOB/TP_JOB | Yes | Yes | LOV=LOV_MANAGERS |
| MANAGER_NAME_DISP | Display Item | Char | 101 | No | CVS_JOB/TP_JOB | Yes | No | Non-DB display item |
| LOCATION_CODE | Text Field | Char | 10 | No | CVS_JOB/TP_JOB | Yes | Yes | LOV=LOV_LOCATIONS |
| EMPLOYMENT_TYPE | List Item | Char | 20 | No | CVS_JOB/TP_JOB | Yes | Yes | Values: FULL_TIME, PART_TIME, CONTRACT, INTERN |
| EMPLOYMENT_STATUS | List Item | Char | 20 | No | CVS_JOB/TP_JOB | Yes | Yes | UpdateAllowed=No; Values: ACTIVE, ON_LEAVE, SUSPENDED, TERMINATED |
| TERMINATION_DATE | Text Field | Date | 11 | No | CVS_JOB/TP_JOB | Yes | Yes | UpdateAllowed=No; FormatMask=MM/DD/YYYY |
| ACTIVE_FLAG | Text Field | Char | 1 | No | (hidden) | No | Yes | — |
| CREATED_BY | Text Field | Char | 30 | No | (hidden) | No | Yes | InsertAllowed=Yes, UpdateAllowed=No |
| CREATED_DATE | Text Field | Date | — | No | (hidden) | No | Yes | InsertAllowed=Yes, UpdateAllowed=No |
| MODIFIED_BY | Text Field | Char | 30 | No | (hidden) | No | Yes | — |
| MODIFIED_DATE | Text Field | Date | — | No | (hidden) | No | Yes | — |

**Block Trigger — PRE-INSERT:**
```
:EMPLOYEE.EMP_ID := SEQ_EMPLOYEE.NEXTVAL;
:EMPLOYEE.EMP_NUMBER := PKG_EMPLOYEE.generate_emp_number;
:EMPLOYEE.ACTIVE_FLAG := 'Y';
:EMPLOYEE.EMPLOYMENT_STATUS := 'ACTIVE';
:EMPLOYEE.CREATED_BY := :GLOBAL.current_user;
:EMPLOYEE.CREATED_DATE := SYSDATE;
```
Business rules: EMP_ID from sequence SEQ_EMPLOYEE; EMP_NUMBER generated by PKG_EMPLOYEE.generate_emp_number; new employees always set ACTIVE_FLAG='Y' and EMPLOYMENT_STATUS='ACTIVE'.

**Block Trigger — PRE-UPDATE:**
```
:EMPLOYEE.MODIFIED_BY := :GLOBAL.current_user;
:EMPLOYEE.MODIFIED_DATE := SYSDATE;
```

**Block Trigger — POST-QUERY:**
- Populates DEPT_NAME_DISP via `SELECT DEPT_NAME FROM DEPARTMENTS WHERE DEPT_ID = :EMPLOYEE.DEPT_ID` (NO_DATA_FOUND → NULL).
- Populates JOB_TITLE_DISP via `SELECT JOB_TITLE FROM JOB_TITLES WHERE JOB_ID = :EMPLOYEE.JOB_ID` (NO_DATA_FOUND → NULL).
- Populates MANAGER_NAME_DISP via `SELECT FIRST_NAME || ' ' || LAST_NAME FROM EMPLOYEES WHERE EMP_ID = :EMPLOYEE.MANAGER_EMP_ID` (NO_DATA_FOUND → NULL).

**Block Trigger — WHEN-VALIDATE-ITEM (FireInEnterQueryMode=No):**
- Reads :SYSTEM.TRIGGER_ITEM into v_item.
- If EMPLOYEE.EMAIL and not null: calls PKG_VALIDATION.validate_email_format(:EMPLOYEE.EMAIL); if FALSE: MESSAGE('Invalid email format') then RAISE FORM_TRIGGER_FAILURE.
- If EMPLOYEE.HIRE_DATE: if :EMPLOYEE.HIRE_DATE > SYSDATE + 90: MESSAGE('Hire date cannot be more than 90 days in the future') then RAISE FORM_TRIGGER_FAILURE. **Business rule: hire date may not be more than 90 days in the future.**
- If EMPLOYEE.DEPT_ID: `SELECT DEPT_NAME FROM DEPARTMENTS WHERE DEPT_ID = :EMPLOYEE.DEPT_ID AND ACTIVE_FLAG = 'Y'`; NO_DATA_FOUND → MESSAGE('Invalid department') then RAISE FORM_TRIGGER_FAILURE. Populates DEPT_NAME_DISP.
- If EMPLOYEE.JOB_ID: `SELECT JOB_TITLE FROM JOB_TITLES WHERE JOB_ID = :EMPLOYEE.JOB_ID AND ACTIVE_FLAG = 'Y'`; NO_DATA_FOUND → MESSAGE('Invalid job title') then RAISE FORM_TRIGGER_FAILURE. Populates JOB_TITLE_DISP.

---

**BLOCK: SALARY**
- QueryDataSourceName=HRMS.SALARY_RECORDS
- RecordsDisplayed=5, NavigationStyle=Change Block
- InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No (read-only from form)

Items: SALARY_ID (hidden PK), EMP_ID (hidden), EFFECTIVE_DATE (Date, FormatMask=MM/DD/YYYY), END_DATE (Date, FormatMask=MM/DD/YYYY), BASE_SALARY (Number, FormatMask=$999,999,990.00), CHANGE_REASON (Char), CHANGE_PCT (Number, FormatMask=990.00%).

Relation EMP_SALARY_REL: JoinCondition=`SALARY.EMP_ID = EMPLOYEE.EMP_ID`; DeleteRecordBehavior=Cascading; AutoQuery=Yes.

---

**LOVs:**

**LOV_DEPARTMENTS** (Title="Select Department", 400×300):
- Query: `SELECT DEPT_ID, DEPT_CODE, DEPT_NAME, COST_CENTER FROM HRMS.DEPARTMENTS WHERE ACTIVE_FLAG = 'Y' ORDER BY DEPT_NAME`
- Mappings: DEPT_ID → EMPLOYEE.DEPT_ID; DEPT_NAME → EMPLOYEE.DEPT_NAME_DISP

**LOV_JOB_TITLES** (Title="Select Job Title", 450×300):
- Query: `SELECT j.JOB_ID, j.JOB_CODE, j.JOB_TITLE, g.GRADE_NAME FROM HRMS.JOB_TITLES j JOIN HRMS.JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID WHERE j.ACTIVE_FLAG = 'Y' ORDER BY j.JOB_TITLE`
- Mappings: JOB_ID → EMPLOYEE.JOB_ID; JOB_TITLE → EMPLOYEE.JOB_TITLE_DISP

**LOV_MANAGERS** (Title="Select Manager", 400×300):
- Query: `SELECT EMP_ID, EMP_NUMBER, FIRST_NAME || ' ' || LAST_NAME AS MANAGER_NAME FROM HRMS.EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' ORDER BY LAST_NAME`
- Mappings: EMP_ID → EMPLOYEE.MANAGER_EMP_ID; MANAGER_NAME → EMPLOYEE.MANAGER_NAME_DISP
- Business rule: only ACTIVE employees appear as selectable managers.

**LOV_LOCATIONS** (Title="Select Location", 400×300):
- Query: `SELECT LOCATION_CODE, LOCATION_NAME, CITY, STATE_PROVINCE FROM HRMS.LOCATIONS WHERE ACTIVE_FLAG = 'Y' ORDER BY LOCATION_NAME`
- Mappings: LOCATION_CODE → EMPLOYEE.LOCATION_CODE

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml ===

**Type:** Oracle Forms Module (HRMS_LEAVE.fmb). Exported from Oracle Forms Builder 12c (12.2.1.4). Purpose: Leave request submission, approval workflow, balance inquiry, team calendar.

**Attached Libraries:** HRMS_COMMON_LIB

**Menu Module:** HRMS_MENU

**Canvases:**
- CVS_MAIN (Tab canvas, 700×480): TP_MY_REQUESTS ("My Requests"), TP_NEW_REQUEST ("Submit Request"), TP_APPROVALS ("Pending Approvals"), TP_CALENDAR ("Team Calendar")

**Windows:**
- WIN_LEAVE: Document style, 720×520, PrimaryCanvas=CVS_MAIN

**Alerts:**
- ALT_CONFIRM_CANCEL: Caution style, "Are you sure you want to cancel this leave request?" — Button1="Yes", Button2="No"

---

**FORM-LEVEL TRIGGER — WHEN-NEW-FORM-INSTANCE:**
- Calls PKG_SECURITY.is_session_valid(TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME))); if FALSE: MESSAGE('Session expired.') then RAISE FORM_TRIGGER_FAILURE.
- Sets MDI title to 'HRMS - Leave Management [' || :GLOBAL.current_user || ']'.
- Sets LEAVE_REQUEST DEFAULT_WHERE = `'EMP_ID = ' || :GLOBAL.current_emp_id || ' ORDER BY CREATED_DATE DESC'`. Business rule: user sees only their own leave requests by default.
- Calls POPULATE_GROUP('RG_LEAVE_TYPES').
- Navigates to LEAVE_REQUEST block, executes query.
- Navigates to LEAVE_BALANCE block, executes query, then returns to LEAVE_REQUEST.

---

**BLOCK: LEAVE_REQUEST**
- QueryDataSourceName=HRMS.LEAVE_REQUESTS
- RecordsDisplayed=8, InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No (read-only)

Items: REQUEST_ID (hidden PK), EMP_ID (hidden), LEAVE_TYPE_NAME_DISP (Display Item, 120px), START_DATE (Date, MM/DD/YYYY), END_DATE (Date, MM/DD/YYYY), TOTAL_DAYS (Number, FormatMask=990.0), STATUS (Char, 100px), REASON (Char, 200px).

**BTN_CANCEL_REQUEST trigger (WHEN-BUTTON-PRESSED):**
- Business rule: If :LEAVE_REQUEST.STATUS NOT IN ('PENDING', 'APPROVED'): MESSAGE('Only pending or approved requests can be cancelled.') then RAISE FORM_TRIGGER_FAILURE. Only PENDING or APPROVED requests can be cancelled.
- If SHOW_ALERT('ALT_CONFIRM_CANCEL') = ALERT_BUTTON1: calls PKG_LEAVE.cancel_leave_request(:LEAVE_REQUEST.REQUEST_ID, 'Cancelled by employee', :GLOBAL.current_user); MESSAGE('Leave request cancelled.'); EXECUTE_QUERY.

**POST-QUERY trigger:**
```sql
SELECT lt.LEAVE_TYPE_NAME INTO :LEAVE_REQUEST.LEAVE_TYPE_NAME_DISP
FROM LEAVE_TYPES lt
JOIN LEAVE_REQUESTS lr ON lt.LEAVE_TYPE_ID = lr.LEAVE_TYPE_ID
WHERE lr.REQUEST_ID = :LEAVE_REQUEST.REQUEST_ID;
```
NO_DATA_FOUND → LEAVE_TYPE_NAME_DISP := 'Unknown'.

---

**BLOCK: NEW_REQUEST (control block — no DB table)**
- InsertAllowed=Yes, UpdateAllowed=No, DeleteAllowed=No, RecordsDisplayed=1

Items: NR_LEAVE_TYPE_ID (Number, LOV=LOV_LEAVE_TYPES), NR_LEAVE_TYPE_DISP (Display Item, 150px), NR_START_DATE (Date, MM/DD/YYYY), NR_END_DATE (Date, MM/DD/YYYY), NR_HALF_DAY (Check Box, CheckBoxMapping=Y/N), NR_REASON (Char, MaxLen=500, MultiLine=Yes, 300×60px), NR_CALC_DAYS (Display Item, Number), NR_BALANCE_DISP (Display Item, Number).

**BTN_SUBMIT trigger (WHEN-BUTTON-PRESSED):**
- Validates NR_LEAVE_TYPE_ID IS NOT NULL: MESSAGE('Please select a leave type.') then RAISE FORM_TRIGGER_FAILURE.
- Validates NR_START_DATE IS NOT NULL: MESSAGE('Please enter a start date.') then RAISE FORM_TRIGGER_FAILURE.
- Validates NR_END_DATE IS NOT NULL: MESSAGE('Please enter an end date.') then RAISE FORM_TRIGGER_FAILURE.
- Calls:
```sql
PKG_LEAVE.submit_leave_request(
    p_emp_id        => :GLOBAL.current_emp_id,
    p_leave_type_id => :NEW_REQUEST.NR_LEAVE_TYPE_ID,
    p_start_date    => :NEW_REQUEST.NR_START_DATE,
    p_end_date      => :NEW_REQUEST.NR_END_DATE,
    p_half_day_flag => NVL(:NEW_REQUEST.NR_HALF_DAY, 'N'),
    p_reason        => :NEW_REQUEST.NR_REASON,
    p_user          => :GLOBAL.current_user
)
```
- Returns v_request_id. MESSAGE('Leave request #' || v_request_id || ' submitted successfully.').
- Clears block (CLEAR_BLOCK(NO_VALIDATE)), then navigates to LEAVE_REQUEST and re-executes query.

---

**BLOCK: LEAVE_BALANCE**
- QueryDataSourceName=HRMS.LEAVE_BALANCES
- RecordsDisplayed=6, InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No (read-only)

Items: LEAVE_TYPE_NAME_DISP (Display), OPENING_BALANCE (Number, FormatMask=990.0), ACCRUED (Number, FormatMask=990.0), USED (Number, FormatMask=990.0), PENDING (Number, FormatMask=990.0), AVAILABLE (Number, FormatMask=990.0).

---

**LOVs:**

**LOV_LEAVE_TYPES** (Title="Select Leave Type", 350×250):
- Query: `SELECT LEAVE_TYPE_ID, LEAVE_TYPE_CODE, LEAVE_TYPE_NAME FROM HRMS.LEAVE_TYPES WHERE ACTIVE_FLAG = 'Y' ORDER BY LEAVE_TYPE_NAME`
- Mappings: LEAVE_TYPE_ID → NEW_REQUEST.NR_LEAVE_TYPE_ID; LEAVE_TYPE_NAME → NEW_REQUEST.NR_LEAVE_TYPE_DISP

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml ===

**Type:** Oracle Forms Module (HRMS_LOGIN.fmb). Exported from Oracle Forms Builder 12c (12.2.1.4). Purpose: Authentication form; opens main menu on success.

**Known issues documented in file:**
- Password field transmitted in cleartext (Forms applet limitation).
- No account lockout after failed attempts.
- No CAPTCHA or 2FA support.

**Canvas:** CVS_LOGIN (Content canvas, 700×300, BackgroundColor=white)

**Window:** WIN_LOGIN: Dialog style, 700×320, Closeable=No, Minimizable=No, Maximizable=No, MoveAllowed=Yes, ResizeAllowed=No.

---

**FORM-LEVEL TRIGGER — WHEN-NEW-FORM-INSTANCE:**
- Sets MDI window title to 'HRMS Login'.
- Sets WIN_LOGIN WINDOW_STATE to NORMAL.
- Navigates to LOGIN.USERNAME.

---

**BLOCK: LOGIN (control block — no DB table)**
- InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No, RecordsDisplayed=1, NavigationStyle=Same Record

Items:
- COMPANY_LOGO: Image item (GIF, Original depth, 200×60px)
- USERNAME: Text Field, Char, MaxLen=100, Required=Yes, 200×24px
- PASSWORD: Text Field, Char, MaxLen=100, Required=Yes, 200×24px, **ConcealData=Yes**
- ERROR_MSG: Display Item, Char, MaxLen=200, 300×20px, ForegroundColor=red, FontWeight=Bold
- BTN_LOGIN: Push Button, 100×30px

**BTN_LOGIN trigger (WHEN-BUTTON-PRESSED):**
- Clears :LOGIN.ERROR_MSG to NULL.
- If :LOGIN.USERNAME IS NULL OR :LOGIN.PASSWORD IS NULL: :LOGIN.ERROR_MSG := 'Please enter username and password.' then RAISE FORM_TRIGGER_FAILURE.
- Calls:
```sql
v_session_id := PKG_SECURITY.authenticate(
    :LOGIN.USERNAME,
    :LOGIN.PASSWORD,
    GET_APPLICATION_PROPERTY(CLIENT_HOST)
)
```
- Stores result: :GLOBAL.session_id := TO_CHAR(v_session_id); :GLOBAL.current_user := :LOGIN.USERNAME.
- Queries: `SELECT EMP_ID INTO :GLOBAL.current_emp_id FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(:LOGIN.USERNAME) AND EMPLOYMENT_STATUS = 'ACTIVE' AND ROWNUM = 1`
- Business rule: login username matched against employee EMAIL (case-insensitive); only ACTIVE employees can log in. ROWNUM = 1 means first match if duplicates exist.
- Calls: `OPEN_FORM('HRMS_MENU', ACTIVATE, SESSION)`
- WHEN OTHERS (any exception in the entire block): :LOGIN.ERROR_MSG := 'Invalid username or password.'; clears :LOGIN.PASSWORD; navigates to LOGIN.PASSWORD; RAISE FORM_TRIGGER_FAILURE. (Error message is generic — does not distinguish authentication failure from employee lookup failure.)

**KEY-NEXT-ITEM trigger:**
- If :SYSTEM.CURSOR_ITEM = 'LOGIN.PASSWORD': DO_KEY('WHEN-BUTTON-PRESSED') — pressing Enter on password field triggers login.
- Otherwise: NEXT_ITEM.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml ===

**Type:** Oracle Forms Module (HRMS_MENU.fmb). Exported from Oracle Forms Builder 12c (12.2.1.4). Purpose: MDI parent form / application shell after login.

**Attached Libraries:** HRMS_COMMON_LIB

**Canvas:** CVS_MAIN (Content canvas, 740×400)

**Window:** WIN_MAIN: Document style, 760×420.

**Global variables read:** :GLOBAL.current_user, :GLOBAL.session_id, :GLOBAL.current_emp_id

---

**FORM-LEVEL TRIGGER — WHEN-NEW-FORM-INSTANCE:**
- Sets MDI title to `'Human Resource Management System (HRMS) v4.2 - ' || :GLOBAL.current_user || ' - Session: ' || :GLOBAL.session_id`.
- Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'VIEW'); if FALSE: SET_MENU_ITEM_PROPERTY('MENU_MAIN.MI_PAYROLL', ENABLED, PROPERTY_FALSE).
- Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'ADMIN', 'VIEW'); if FALSE: SET_MENU_ITEM_PROPERTY('MENU_MAIN.MI_ADMIN', ENABLED, PROPERTY_FALSE).
- Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'REPORTS', 'VIEW'); if FALSE: SET_MENU_ITEM_PROPERTY('MENU_MAIN.MI_REPORTS', ENABLED, PROPERTY_FALSE).
- Navigates to MENU_CONTROL block.

---

**BLOCK: MENU_CONTROL (control block — no DB table)**
- InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No, RecordsDisplayed=1

Items:
- WELCOME_TEXT: Display Item, Default="Welcome to the Human Resource Management System", 600×30px, FontSize=14, FontWeight=Bold
- USER_INFO: Display Item, 400×20px

**Module buttons (all 200×60px):**

**BTN_EMPLOYEES (WHEN-BUTTON-PRESSED):**
- `OPEN_FORM('HRMS_EMPLOYEE', ACTIVATE, SESSION)`

**BTN_PAYROLL (WHEN-BUTTON-PRESSED):**
- Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'VIEW'); if FALSE: MESSAGE('Access denied.') then RAISE FORM_TRIGGER_FAILURE.
- `OPEN_FORM('HRMS_PAYROLL', ACTIVATE, SESSION)`

**BTN_LEAVE (WHEN-BUTTON-PRESSED):**
- `OPEN_FORM('HRMS_LEAVE', ACTIVATE, SESSION)` (no permission check — all users can access leave)

**BTN_PERFORMANCE (WHEN-BUTTON-PRESSED):**
- `OPEN_FORM('HRMS_PERFORMANCE', ACTIVATE, SESSION)` (no permission check)

**BTN_REPORTS (WHEN-BUTTON-PRESSED):**
- Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'REPORTS', 'VIEW'); if FALSE: MESSAGE('Access denied.') then RAISE FORM_TRIGGER_FAILURE.
- `OPEN_FORM('HRMS_REPORTS', ACTIVATE, SESSION)`

**BTN_LOGOUT (WHEN-BUTTON-PRESSED):**
- Calls `PKG_SECURITY.logout(TO_NUMBER(:GLOBAL.session_id))`.
- `EXIT_FORM`

---

**MenuModule MENU_MAIN:**

File menu (FILE_MENU):
- MI_LOGOUT: `PKG_SECURITY.logout(TO_NUMBER(:GLOBAL.session_id)); EXIT_FORM;`

Modules menu (MODULES_MENU):
- MI_EMPLOYEES: `OPEN_FORM('HRMS_EMPLOYEE', ACTIVATE, SESSION);`
- MI_PAYROLL: `OPEN_FORM('HRMS_PAYROLL', ACTIVATE, SESSION);`
- MI_LEAVE: `OPEN_FORM('HRMS_LEAVE', ACTIVATE, SESSION);`
- MI_PERFORMANCE: `OPEN_FORM('HRMS_PERFORMANCE', ACTIVATE, SESSION);`
- MI_REPORTS: `OPEN_FORM('HRMS_REPORTS', ACTIVATE, SESSION);`

Admin menu (ADMIN_MENU):
- MI_ADMIN: `OPEN_FORM('HRMS_ADMIN', ACTIVATE, SESSION);`
- MI_CHANGE_PWD: `SHOW_WINDOW('WIN_CHANGE_PWD');`

Help menu (HELP_MENU):
- MI_ABOUT: `MESSAGE('HRMS v4.2 - Build 2024.03.15');` — **hardcoded build string: v4.2, Build 2024.03.15**

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml ===

**Type:** Oracle Forms Module (HRMS_PAYROLL.fmb). Exported from Oracle Forms Builder 12c (12.2.1.4). Purpose: Pay period management, payroll run creation, calculation, approval, pay register.

**Attached Libraries:** HRMS_COMMON_LIB

**Menu Module:** HRMS_MENU

**Canvases:**
- CVS_MAIN (Tab canvas, 750×520): TP_PERIODS ("Pay Periods"), TP_RUNS ("Payroll Runs"), TP_DETAILS ("Pay Details")

**Windows:**
- WIN_PAYROLL: Document style, 770×560, PrimaryCanvas=CVS_MAIN

---

**FORM-LEVEL TRIGGER — WHEN-NEW-FORM-INSTANCE:**
- Gets session ID, calls PKG_SECURITY.is_session_valid(v_session_id); if FALSE: MESSAGE('Session expired. Please log in again.') then RAISE FORM_TRIGGER_FAILURE.
- Business rule: Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'VIEW'); if FALSE: MESSAGE('You do not have permission to access the Payroll module.') then RAISE FORM_TRIGGER_FAILURE. Payroll requires explicit VIEW permission.
- Sets MDI title to 'HRMS - Payroll Processing [' || :GLOBAL.current_user || ']'.
- Navigates to PAY_PERIOD block; sets DEFAULT_WHERE = `'STATUS = ''OPEN'' ORDER BY PERIOD_START_DATE DESC'`; executes query. Business rule: default view shows only OPEN pay periods.

---

**BLOCK: PAY_PERIOD**
- QueryDataSourceName=HRMS.PAY_PERIODS
- RecordsDisplayed=10, InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No (read-only)

Items: PERIOD_ID (hidden PK), PERIOD_NAME (Char, 150px), PERIOD_START_DATE (Date, MM/DD/YYYY), PERIOD_END_DATE (Date, MM/DD/YYYY), PAY_DATE (Date, MM/DD/YYYY), STATUS (Char, 80px).

---

**BLOCK: PAYROLL_RUN**
- QueryDataSourceName=HRMS.PAYROLL_RUNS
- RecordsDisplayed=5, InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No (read-only)

Items: RUN_ID (hidden PK), PERIOD_ID (hidden), RUN_TYPE (Char, 100px), RUN_DATE (Date, FormatMask=MM/DD/YYYY HH24:MI, 140px), STATUS (Char, 100px), EMPLOYEE_COUNT (Number, 60px), TOTAL_GROSS (Number, FormatMask=$999,999,990.00), TOTAL_NET (Number, FormatMask=$999,999,990.00).

**BTN_CREATE_RUN trigger (WHEN-BUTTON-PRESSED):**
- Calls: `v_run_id := PKG_PAYROLL.create_payroll_run(:PAY_PERIOD.PERIOD_ID, 'REGULAR', :GLOBAL.current_user)`
- MESSAGE('Payroll run ' || v_run_id || ' created successfully.')
- Navigates to PAYROLL_RUN block, executes query.

**BTN_CALCULATE trigger (WHEN-BUTTON-PRESSED):**
- Business rule: If :PAYROLL_RUN.STATUS != 'PENDING': MESSAGE('Can only calculate runs in PENDING status.') then RAISE FORM_TRIGGER_FAILURE. Calculation only allowed when status is PENDING.
- MESSAGE('Calculating payroll... Please wait.'); SYNCHRONIZE.
- Calls: `PKG_PAYROLL.calculate_payroll(:PAYROLL_RUN.RUN_ID, :GLOBAL.current_user)`
- MESSAGE('Payroll calculation complete.'); EXECUTE_QUERY.

**BTN_APPROVE trigger (WHEN-BUTTON-PRESSED):**
- Business rule: Calls PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'PAYROLL', 'APPROVE'); if FALSE: MESSAGE('You do not have permission to approve payroll.') then RAISE FORM_TRIGGER_FAILURE. Approval requires distinct APPROVE permission on PAYROLL.
- Calls: `PKG_PAYROLL.approve_payroll(:PAYROLL_RUN.RUN_ID, :GLOBAL.current_user)`
- MESSAGE('Payroll run approved.'); EXECUTE_QUERY.

Relation PERIOD_RUN_REL: JoinCondition=`PAYROLL_RUN.PERIOD_ID = PAY_PERIOD.PERIOD_ID`; AutoQuery=Yes.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PERFORMANCE.xml ===

**Type:** Oracle Forms Module (HRMS_PERFORMANCE.fmb). Exported from Oracle Forms Builder 12c (12.2.1.4). Purpose: Performance review cycles, self-assessments, manager reviews, goal tracking, rating calibration.

**Attached Libraries:** HRMS_COMMON_LIB

**Menu Module:** HRMS_MENU

**Canvases:**
- CVS_MAIN (Tab canvas, 750×520): TP_CYCLES ("Review Cycles"), TP_REVIEWS ("My Reviews"), TP_GOALS ("Goals")

**Windows:**
- WIN_PERFORMANCE: Document style, 770×560.

---

**FORM-LEVEL TRIGGER — WHEN-NEW-FORM-INSTANCE:**
- Calls PKG_SECURITY.is_session_valid(TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME))); if FALSE: MESSAGE('Session expired.') then RAISE FORM_TRIGGER_FAILURE.
- Sets MDI title to 'HRMS - Performance Management [' || :GLOBAL.current_user || ']'.
- Navigates to REVIEW_CYCLE block; sets DEFAULT_WHERE = `'STATUS IN (''OPEN'', ''DRAFT'') ORDER BY CYCLE_YEAR DESC'`; executes query. Business rule: default view shows OPEN and DRAFT review cycles only.

---

**BLOCK: REVIEW_CYCLE**
- QueryDataSourceName=HRMS.REVIEW_CYCLES
- RecordsDisplayed=5, InsertAllowed=No, UpdateAllowed=No, DeleteAllowed=No (read-only)

Items: CYCLE_ID (hidden PK), CYCLE_NAME (Char, 200px), CYCLE_YEAR (Number, 50px), START_DATE (Date, MM/DD/YYYY), END_DATE (Date, MM/DD/YYYY), STATUS (Char, 80px).

---

**BLOCK: PERFORMANCE_REVIEW**
- QueryDataSourceName=HRMS.PERFORMANCE_REVIEWS
- RecordsDisplayed=8, InsertAllowed=No, UpdateAllowed=Yes, DeleteAllowed=No

Items: REVIEW_ID (hidden PK), CYCLE_ID (hidden), EMP_ID (hidden), EMP_NAME_DISP (Display Item, 180px), STATUS (Char, 120px, UpdateAllowed=No), OVERALL_RATING (Number, FormatMask=9.0, 50px), RATING_LABEL (Display Item/DB, 150px), SELF_ASSESSMENT (Char, 300×80px, MultiLine=Yes), MANAGER_ASSESSMENT (Char, 300×80px, MultiLine=Yes).

**POST-QUERY trigger:**
```sql
SELECT FIRST_NAME || ' ' || LAST_NAME INTO :PERFORMANCE_REVIEW.EMP_NAME_DISP
FROM EMPLOYEES WHERE EMP_ID = :PERFORMANCE_REVIEW.EMP_ID;
```
NO_DATA_FOUND → EMP_NAME_DISP := 'Unknown'.

Relation CYCLE_REVIEW_REL: JoinCondition=`PERFORMANCE_REVIEW.CYCLE_ID = REVIEW_CYCLE.CYCLE_ID`; AutoQuery=Yes.

---

**BLOCK: PERFORMANCE_GOAL**
- QueryDataSourceName=HRMS.PERFORMANCE_GOALS
- RecordsDisplayed=5, InsertAllowed=Yes, UpdateAllowed=Yes, DeleteAllowed=No

Items: GOAL_ID (hidden PK), REVIEW_ID (hidden), GOAL_TITLE (Char, 250px), GOAL_CATEGORY (List Item, Poplist: BUSINESS, DEVELOPMENT, LEADERSHIP), WEIGHT_PCT (Number, FormatMask=990, 50px), PROGRESS_PCT (Number, FormatMask=990, 50px), STATUS (Char, 100px).

Relation REVIEW_GOAL_REL: JoinCondition=`PERFORMANCE_GOAL.REVIEW_ID = PERFORMANCE_REVIEW.REVIEW_ID`; AutoQuery=Yes.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pks ===

**Package:** HRMS.PKG_AUDIT
**Type:** Package specification
**Dependencies:** None (base package). Called by all other packages and database triggers.

**Procedures and Functions:**

**log_action(p_table_name VARCHAR2, p_record_id NUMBER, p_action VARCHAR2, p_user VARCHAR2 DEFAULT USER, p_old_values CLOB DEFAULT NULL, p_new_values CLOB DEFAULT NULL)**
- Records DML operations to audit log.

**purge_old_records(p_days_to_keep NUMBER DEFAULT 365, p_user VARCHAR2 DEFAULT USER)**
- Purges old audit records. Default retention: 365 days.

**get_change_history(p_table_name VARCHAR2, p_record_id NUMBER, p_from_date DATE DEFAULT NULL, p_to_date DATE DEFAULT NULL) RETURN SYS_REFCURSOR**
- Returns change history cursor for a specific table/record within optional date range.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pkb ===

**Package:** HRMS.PKG_AUDIT
**Type:** Package body

**Dependencies:**
- AUDIT_LOG table
- SEQ_AUDIT sequence
- SYS_CONTEXT('USERENV', 'IP_ADDRESS')
- SYS_CONTEXT('USERENV', 'SESSIONID')
- DBMS_OUTPUT (for fallback in purge_old_records)

---

**PROCEDURE log_action(p_table_name, p_record_id, p_action, p_user DEFAULT USER, p_old_values DEFAULT NULL, p_new_values DEFAULT NULL)**
- PRAGMA AUTONOMOUS_TRANSACTION — runs in its own transaction.
- INSERT INTO AUDIT_LOG: AUDIT_ID=SEQ_AUDIT.NEXTVAL, TABLE_NAME, RECORD_ID, ACTION_TYPE, OLD_VALUES, NEW_VALUES, CHANGED_BY=p_user, CHANGED_DATE=SYSDATE, IP_ADDRESS=SYS_CONTEXT('USERENV','IP_ADDRESS'), SESSION_ID=SYS_CONTEXT('USERENV','SESSIONID').
- COMMIT.
- EXCEPTION WHEN OTHERS: ROLLBACK. (Audit logging must never fail the calling transaction.)

**PROCEDURE purge_old_records(p_days_to_keep NUMBER DEFAULT 365, p_user VARCHAR2 DEFAULT USER)**
- Business rule: Default retention period is 365 days.
- `DELETE FROM AUDIT_LOG WHERE CHANGED_DATE < SYSDATE - p_days_to_keep`
- Captures SQL%ROWCOUNT into v_deleted. COMMIT.
- DBMS_OUTPUT.PUT_LINE('Purged ' || v_deleted || ' audit records older than ' || p_days_to_keep || ' days').

**FUNCTION get_change_history(p_table_name, p_record_id, p_from_date DEFAULT NULL, p_to_date DEFAULT NULL) RETURN SYS_REFCURSOR**
- Opens cursor:
```sql
SELECT AUDIT_ID, TABLE_NAME, RECORD_ID, ACTION_TYPE,
       OLD_VALUES, NEW_VALUES, CHANGED_BY, CHANGED_DATE, IP_ADDRESS
FROM AUDIT_LOG
WHERE TABLE_NAME = p_table_name
AND RECORD_ID = p_record_id
AND (p_from_date IS NULL OR CHANGED_DATE >= p_from_date)
AND (p_to_date IS NULL OR CHANGED_DATE <= p_to_date)
ORDER BY CHANGED_DATE DESC
```
- Returns cursor.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pks ===

**Package:** HRMS.PKG_COMMON
**Type:** Package specification
**Dependencies:** None (base package — no cross-package dependencies). Called by all other packages and all forms.

**Types declared:**
```
TYPE t_error_rec IS RECORD (
    error_id       NUMBER,
    package_name   VARCHAR2(60),
    procedure_name VARCHAR2(60),
    error_message  VARCHAR2(4000),
    error_date     DATE,
    username       VARCHAR2(30)
);
```

**Logging procedures:**
- `log_error(p_package VARCHAR2, p_procedure VARCHAR2, p_message VARCHAR2, p_user VARCHAR2 DEFAULT USER)`
- `log_info(p_package VARCHAR2, p_procedure VARCHAR2, p_message VARCHAR2, p_user VARCHAR2 DEFAULT USER)`

**Configuration functions/procedures:**
- `get_param(p_group VARCHAR2, p_code VARCHAR2) RETURN VARCHAR2`
- `get_param_number(p_group VARCHAR2, p_code VARCHAR2) RETURN NUMBER`
- `get_param_date(p_group VARCHAR2, p_code VARCHAR2) RETURN DATE`
- `set_param(p_group VARCHAR2, p_code VARCHAR2, p_value VARCHAR2, p_user VARCHAR2 DEFAULT USER)`

**Date utility functions:**
- `business_days_between(p_start_date DATE, p_end_date DATE) RETURN NUMBER`
- `add_business_days(p_date DATE, p_days NUMBER) RETURN DATE`
- `get_fiscal_year(p_date DATE DEFAULT SYSDATE) RETURN NUMBER`
- `get_fiscal_quarter(p_date DATE DEFAULT SYSDATE) RETURN NUMBER`

**Formatting functions:**
- `format_phone(p_phone VARCHAR2) RETURN VARCHAR2`
- `format_ssn_masked(p_ssn VARCHAR2) RETURN VARCHAR2`
- `format_currency(p_amount NUMBER, p_currency_code VARCHAR2 DEFAULT 'USD') RETURN VARCHAR2`
- `format_name(p_first_name VARCHAR2, p_last_name VARCHAR2, p_format VARCHAR2 DEFAULT 'FL') RETURN VARCHAR2` — FL=First Last, LF=Last, First

**Validation functions:**
- `is_valid_email(p_email VARCHAR2) RETURN BOOLEAN`
- `is_valid_phone(p_phone VARCHAR2) RETURN BOOLEAN`
- `is_valid_ssn(p_ssn VARCHAR2) RETURN BOOLEAN`

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb ===

**Package:** HRMS.PKG_COMMON
**Type:** Package body

**Dependencies:**
- AUDIT_LOG table (for log_error and log_info)
- SEQ_AUDIT sequence
- SYSTEM_PARAMETERS table (for get_param, set_param)
- DBMS_OUTPUT (fallback in log_error)

---

**PROCEDURE log_error(p_package, p_procedure, p_message, p_user DEFAULT USER)**
- PRAGMA AUTONOMOUS_TRANSACTION.
- INSERT INTO AUDIT_LOG: AUDIT_ID=SEQ_AUDIT.NEXTVAL, TABLE_NAME='ERROR_LOG', RECORD_ID=0, ACTION_TYPE='INSERT', OLD_VALUES=NULL, NEW_VALUES=JSON-like string:
  `'{"package":"' || p_package || '","procedure":"' || p_procedure || '","message":"' || REPLACE(SUBSTR(p_message, 1, 3000), '"', '\"') || '"}'`
- p_message truncated to 3000 characters via SUBSTR; double-quotes escaped.
- COMMIT.
- EXCEPTION WHEN OTHERS: DBMS_OUTPUT.PUT_LINE('ERROR LOG FAILED: ' || p_package || '.' || p_procedure || ': ' || p_message); ROLLBACK.

**PROCEDURE log_info(p_package, p_procedure, p_message, p_user DEFAULT USER)**
- PRAGMA AUTONOMOUS_TRANSACTION.
- INSERT INTO AUDIT_LOG: TABLE_NAME='INFO_LOG', RECORD_ID=0, ACTION_TYPE='INSERT', NEW_VALUES=JSON-like string (no escaping of quotes, no OLD_VALUES column).
- p_message truncated to 3000 characters via SUBSTR.
- COMMIT.
- EXCEPTION WHEN OTHERS: ROLLBACK.

**FUNCTION get_param(p_group VARCHAR2, p_code VARCHAR2) RETURN VARCHAR2**
- `SELECT PARAM_VALUE INTO v_value FROM SYSTEM_PARAMETERS WHERE PARAM_GROUP = p_group AND PARAM_CODE = p_code`
- Returns v_value. EXCEPTION WHEN NO_DATA_FOUND: returns NULL.

**FUNCTION get_param_number(p_group VARCHAR2, p_code VARCHAR2) RETURN NUMBER**
- Returns TO_NUMBER(get_param(p_group, p_code)).
- EXCEPTION WHEN VALUE_ERROR: returns NULL.

**FUNCTION get_param_date(p_group VARCHAR2, p_code VARCHAR2) RETURN DATE**
- Returns TO_DATE(get_param(p_group, p_code), 'YYYY-MM-DD').
- EXCEPTION WHEN OTHERS: returns NULL.

**PROCEDURE set_param(p_group, p_code, p_value, p_user DEFAULT USER)**
- `UPDATE SYSTEM_PARAMETERS SET PARAM_VALUE = p_value, MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE PARAM_GROUP = p_group AND PARAM_CODE = p_code AND EDITABLE_FLAG = 'Y'`
- Business rule: only parameters with EDITABLE_FLAG = 'Y' can be updated.
- If SQL%ROWCOUNT = 0: RAISE_APPLICATION_ERROR(-20900, 'Parameter not found or not editable: ' || p_group || '.' || p_code).
- Exception number: **-20900**.

**FUNCTION business_days_between(p_start_date DATE, p_end_date DATE) RETURN NUMBER**
- Loops from TRUNC(p_start_date) to TRUNC(p_end_date) one day at a time.
- Increments v_count for each day where TO_CHAR(v_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN') NOT IN ('SAT', 'SUN').
- Returns v_count. (Does NOT exclude public holidays — counts only weekdays.)

**FUNCTION add_business_days(p_date DATE, p_days NUMBER) RETURN DATE**
- Starts at TRUNC(p_date), advances v_result by 1 day at a time.
- Increments v_added only when day is NOT 'SAT' or 'SUN'.
- Stops when v_added = p_days.
- Returns v_result. (Does NOT skip public holidays.)

**FUNCTION get_fiscal_year(p_date DATE DEFAULT SYSDATE) RETURN NUMBER**
- Business rule: Fiscal year starts October 1 (month 10).
- If EXTRACT(MONTH FROM p_date) >= 10: returns EXTRACT(YEAR FROM p_date) + 1.
- Else: returns EXTRACT(YEAR FROM p_date).
- Examples: October 2024 → FY 2025; September 2024 → FY 2024.

**FUNCTION get_fiscal_quarter(p_date DATE DEFAULT SYSDATE) RETURN NUMBER**
- Business rule (fiscal year starts October):
  - Months 10, 11, 12 → Q1
  - Months 1, 2, 3 → Q2
  - Months 4, 5, 6 → Q3
  - Months 7, 8, 9 → Q4

**FUNCTION format_phone(p_phone VARCHAR2) RETURN VARCHAR2**
- Strips non-digits using REGEXP_REPLACE(p_phone, '[^0-9]', '') into v_digits.
- If LENGTH(v_digits) = 10: returns `'(' || SUBSTR(v_digits, 1, 3) || ') ' || SUBSTR(v_digits, 4, 3) || '-' || SUBSTR(v_digits, 7, 4)`
- If LENGTH(v_digits) = 11 AND first digit = '1': returns `'+1 (' || SUBSTR(v_digits, 2, 3) || ') ' || SUBSTR(v_digits, 5, 3) || '-' || SUBSTR(v_digits, 8, 4)`
- Otherwise: returns p_phone unchanged.

**FUNCTION format_ssn_masked(p_ssn VARCHAR2) RETURN VARCHAR2**
- If p_ssn IS NULL OR LENGTH(p_ssn) < 4: returns '***-**-****'.
- Otherwise: returns '***-**-' || SUBSTR(p_ssn, -4) — shows only last 4 digits.

**FUNCTION format_currency(p_amount NUMBER, p_currency_code VARCHAR2 DEFAULT 'USD') RETURN VARCHAR2**
- Prepends currency symbol:
  - 'USD' → '$'
  - 'EUR' → CHR(8364) (€)
  - 'GBP' → CHR(163) (£)
  - Other → p_currency_code || ' '
- Appends TO_CHAR(p_amount, 'FM999,999,990.00').

**FUNCTION format_name(p_first_name VARCHAR2, p_last_name VARCHAR2, p_format VARCHAR2 DEFAULT 'FL') RETURN VARCHAR2**
- If p_format = 'LF': returns INITCAP(p_last_name) || ', ' || INITCAP(p_first_name).
- Else (any other value including 'FL'): returns INITCAP(p_first_name) || ' ' || INITCAP(p_last_name).

**FUNCTION is_valid_email(p_email VARCHAR2) RETURN BOOLEAN**
- Returns REGEXP_LIKE(p_email, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$').
- More permissive than client-side validate_email in HRMS_VALIDATION_LIB (accepts subdomains; min 2-char TLD).

**FUNCTION is_valid_phone(p_phone VARCHAR2) RETURN BOOLEAN**
- Strips non-digits: REGEXP_REPLACE(p_phone, '[^0-9]', '').
- Returns TRUE if LENGTH BETWEEN 10 AND 11.

**FUNCTION is_valid_ssn(p_ssn VARCHAR2) RETURN BOOLEAN**
- Returns REGEXP_LIKE(REGEXP_REPLACE(p_ssn, '[^0-9]', ''), '^\d{9}$').
- Note: does NOT check for all-zero segments (unlike client-side validate_ssn). Divergence between client and server validation.

---

**Cross-cutting observations for downstream agents:**

1. **Validation drift:** Client-side (HRMS_VALIDATION_LIB.validate_email) rejects valid subdomains; server-side (PKG_COMMON.is_valid_email) accepts them. Client-side validate_ssn checks for all-zero segments; server-side is_valid_ssn does not.

2. **Security gaps in login:** No account lockout on failed attempts; password transmitted in cleartext; ROWNUM=1 silently swallows duplicate email matches.

3. **Permission model:** Three tiers for PAYROLL — VIEW (form access), EDIT (implied), APPROVE (explicit). EMPLOYEE uses EDIT. ADMIN and REPORTS use VIEW. Leave and Performance have no permission checks on form open.

4. **Fiscal year:** Starts October 1. Month >= 10 → FY = calendar year + 1.

5. **Pay elements with defaults (numeric):** 401k default 6%; Medical $250; Dental $45; Vision $15; Life $25; HSA $150. All except Life Insurance are pre-tax.

6. **Leave tenure gates:** COMP requires 90 days minimum; FMLA requires 365 days minimum.

7. **Error codes handled explicitly:** 40202 (protected field — suppressed), 40401 (no changes — informational), 40501 (record locked — retry message). Application error -20900 reserved for non-editable parameter updates.

8. **Audit logging:** Uses PRAGMA AUTONOMOUS_TRANSACTION throughout. Failures are silently swallowed (never propagate to caller). Records IP via SYS_CONTEXT. Default retention 365 days. Error logs go to TABLE_NAME='ERROR_LOG', info logs to 'INFO_LOG', both with RECORD_ID=0.

9. **Sequence names seen:** SEQ_EMPLOYEE (employee PK), SEQ_AUDIT (audit log PK).

10. **Package dependencies called from forms:** PKG_SECURITY (authenticate, is_session_valid, has_permission, logout), PKG_EMPLOYEE (generate_emp_number), PKG_LEAVE (submit_leave_request, cancel_leave_request), PKG_PAYROLL (create_payroll_run, calculate_payroll, approve_payroll), PKG_VALIDATION (validate_email_format), PKG_COMMON (log_error), PKG_AUDIT (log_action).


MP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, pp.PERIOD_NAME, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION', 'TAX', 'BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS, SUM(pd.AMOUNT) AS NET_PAY, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE, 0 AS YTD_GROSS, 0 AS YTD_NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND (p_emp_id IS NULL OR pd.EMP_ID = p_emp_id) GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME ORDER BY e.LAST_NAME

Business rules:
- YTD_GROSS and YTD_NET are placeholder 0 values (not yet implemented)
- ELEMENT_ID 100/101/102/103 mapped to federal/state/SS/Medicare respectively

Tables referenced: PAYROLL_DETAILS (EMP_ID, ELEMENT_TYPE, ELEMENT_ID, AMOUNT, RUN_ID, STATUS), EMPLOYEES (EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME), PAYROLL_RUNS (RUN_ID, PERIOD_ID), PAY_PERIODS (PERIOD_ID, PERIOD_NAME)

---

**FUNCTION get_ytd_earnings(p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
- SELECT NVL(SUM(pd.AMOUNT), 0) FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.EMP_ID = p_emp_id AND pd.ELEMENT_TYPE = 'EARNING' AND pd.STATUS = 'CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
- RETURN v_ytd

Business rule: YTD earnings = sum of all EARNING elements with STATUS = 'CALCULATED' in the given tax year, matched by PERIOD_START_DATE year

Tables referenced: PAYROLL_DETAILS (EMP_ID, ELEMENT_TYPE, STATUS, RUN_ID, AMOUNT), PAYROLL_RUNS (RUN_ID, PERIOD_ID), PAY_PERIODS (PERIOD_ID, PERIOD_START_DATE)

---

**PROCEDURE generate_pay_register(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Purpose: Writes CSV pay register to flat file. LEGACY — should be replaced with modern reporting.

Logic:
1. SELECT pp.PERIOD_NAME FROM PAYROLL_RUNS pr JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pr.RUN_ID = p_run_id
2. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS') || '.csv'
3. v_file := UTL_FILE.FOPEN('PAYROLL_OUTPUT', v_filename, 'W', 32767)
4. Write header: 'EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY'
5. FOR rec IN (SELECT e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, d.DEPT_NAME, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FED, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SS, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MED, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION', 'BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS DEDS, SUM(pd.AMOUNT) AS NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' GROUP BY e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, d.DEPT_NAME ORDER BY e.LAST_NAME)
6. Write CSV line: EMP_NUMBER,"{EMP_NAME}","{DEPT_NAME}",{GROSS:FM999999990.00},{FED},{STATE},{SS},{MED},{DEDS},{NET}
7. UTL_FILE.FCLOSE; DBMS_OUTPUT.PUT_LINE('Pay register generated: ' || v_filename)
8. EXCEPTION WHEN OTHERS: close file, PKG_COMMON.log_error, RAISE

Oracle directory used: 'PAYROLL_OUTPUT'
File format: CSV with quoted name fields
Tables referenced: PAYROLL_RUNS (RUN_ID, PERIOD_ID), PAY_PERIODS (PERIOD_ID, PERIOD_NAME), PAYROLL_DETAILS, EMPLOYEES (EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID), DEPARTMENTS (DEPT_ID, DEPT_NAME)
File I/O: UTL_FILE, max line 32767
External service calls: UTL_FILE, DBMS_OUTPUT.PUT_LINE, PKG_COMMON.log_error

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks ===

**Package:** HRMS.PKG_PERFORMANCE
**Schema:** HRMS
**Purpose:** Performance Review Management — review cycles, goal tracking, ratings, calibration

**Dependencies:** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
**Called by:** HRMS_PERFORMANCE form, batch calibration job

**Type:** `t_review_cursor` — REF CURSOR

**Public Method Signatures:**

`FUNCTION create_review_cycle(p_cycle_name VARCHAR2, p_cycle_year NUMBER, p_start_date DATE, p_end_date DATE, p_self_review_due DATE DEFAULT NULL, p_manager_review_due DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE open_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE close_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)`

`FUNCTION create_review(p_cycle_id NUMBER, p_emp_id NUMBER, p_reviewer_emp_id NUMBER, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE submit_self_assessment(p_review_id NUMBER, p_self_assessment CLOB, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE submit_manager_review(p_review_id NUMBER, p_overall_rating NUMBER, p_manager_assessment CLOB, p_strengths CLOB DEFAULT NULL, p_improvement_areas CLOB DEFAULT NULL, p_development_plan CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE acknowledge_review(p_review_id NUMBER, p_emp_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)`

`FUNCTION add_goal(p_review_id NUMBER, p_emp_id NUMBER, p_goal_title VARCHAR2, p_goal_description CLOB DEFAULT NULL, p_goal_category VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct NUMBER DEFAULT 0, p_target_date DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE update_goal_progress(p_goal_id NUMBER, p_progress_pct NUMBER, p_status VARCHAR2 DEFAULT NULL, p_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id NUMBER, p_cycle_id NUMBER)`

`FUNCTION get_rating_distribution(p_cycle_id NUMBER, p_dept_id NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR`

`PROCEDURE generate_reviews_for_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)`

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb ===

**Package Body:** HRMS.PKG_PERFORMANCE

---

**FUNCTION create_review_cycle(...) RETURN NUMBER**

Logic:
1. SELECT SEQ_REVIEW_CYCLE.NEXTVAL INTO v_cycle_id FROM DUAL
2. INSERT INTO REVIEW_CYCLES (CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_cycle_id, p_cycle_name, p_cycle_year, p_start_date, p_end_date, p_self_review_due, p_manager_review_due, 'DRAFT', p_user, SYSDATE)
3. PKG_AUDIT.log_action('REVIEW_CYCLES', v_cycle_id, 'INSERT', p_user)
4. RETURN v_cycle_id

Business rule: New review cycles start in 'DRAFT' status

Tables referenced: REVIEW_CYCLES (CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE)
Sequences used: SEQ_REVIEW_CYCLE
External service calls: PKG_AUDIT.log_action

---

**PROCEDURE open_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE REVIEW_CYCLES SET STATUS = 'OPEN', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id AND STATUS = 'DRAFT'
2. IF SQL%ROWCOUNT = 0 → RAISE_APPLICATION_ERROR(-20401, 'Cannot open cycle - must be in DRAFT status')

Business rule: Only DRAFT cycles can be opened

Tables referenced: REVIEW_CYCLES (CYCLE_ID, STATUS, MODIFIED_BY, MODIFIED_DATE)
Exceptions thrown: -20401

---

**PROCEDURE close_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic: UPDATE REVIEW_CYCLES SET STATUS = 'CLOSED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id

Tables referenced: REVIEW_CYCLES

---

**FUNCTION create_review(p_cycle_id NUMBER, p_emp_id NUMBER, p_reviewer_emp_id NUMBER, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER**

Logic:
1. SELECT SEQ_PERF_REVIEW.NEXTVAL INTO v_review_id FROM DUAL
2. INSERT INTO PERFORMANCE_REVIEWS (REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_review_id, p_cycle_id, p_emp_id, p_reviewer_emp_id, 'ANNUAL', 'NOT_STARTED', p_user, SYSDATE)
3. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => p_emp_id, p_type => 'EMAIL', p_subject => 'Performance Review Initiated', p_body => 'Your annual performance review has been initiated. Please complete your self-assessment.', p_user => p_user)
4. RETURN v_review_id

Business rules:
- REVIEW_TYPE always 'ANNUAL' in this path
- Initial STATUS = 'NOT_STARTED'
- Employee notified on review creation

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE)
Sequences used: SEQ_PERF_REVIEW
External service calls: PKG_NOTIFICATION.send_notification

---

**PROCEDURE submit_self_assessment(p_review_id NUMBER, p_self_assessment CLOB, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_REVIEWS SET SELF_ASSESSMENT = p_self_assessment, STATUS = 'MANAGER_REVIEW', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS IN ('NOT_STARTED', 'SELF_REVIEW')
2. IF SQL%ROWCOUNT = 0 → RAISE_APPLICATION_ERROR(-20402, 'Review not found or not in correct status')
3. SELECT REVIEWER_EMP_ID FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id → v_manager_id
4. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => v_manager_id, p_type => 'EMAIL', p_subject => 'Self-Assessment Submitted - Ready for Manager Review', p_body => 'An employee has completed their self-assessment. Please proceed with the manager review.', p_user => p_user)

Business rules:
- Can submit self-assessment when status is 'NOT_STARTED' or 'SELF_REVIEW'
- Status transitions to 'MANAGER_REVIEW' on submission
- Manager notified on submission

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, SELF_ASSESSMENT, STATUS, REVIEWER_EMP_ID, MODIFIED_BY, MODIFIED_DATE)
External service calls: PKG_NOTIFICATION.send_notification
Exceptions thrown: -20402

---

**PROCEDURE submit_manager_review(...)**

Parameters: p_review_id NUMBER, p_overall_rating NUMBER, p_manager_assessment CLOB, p_strengths CLOB DEFAULT NULL, p_improvement_areas CLOB DEFAULT NULL, p_development_plan CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

Logic:
1. IF p_overall_rating < 1.0 OR p_overall_rating > 5.0 → RAISE_APPLICATION_ERROR(-20403, 'Rating must be between 1.0 and 5.0')
2. UPDATE PERFORMANCE_REVIEWS SET OVERALL_RATING = p_overall_rating, RATING_LABEL = CASE WHEN p_overall_rating >= 4.5 THEN 'Exceptional' WHEN p_overall_rating >= 3.5 THEN 'Exceeds Expectations' WHEN p_overall_rating >= 2.5 THEN 'Meets Expectations' WHEN p_overall_rating >= 1.5 THEN 'Needs Improvement' ELSE 'Unsatisfactory' END, MANAGER_ASSESSMENT = p_manager_assessment, STRENGTHS = p_strengths, AREAS_FOR_IMPROVEMENT = p_improvement_areas, DEVELOPMENT_PLAN = p_development_plan, STATUS = 'COMPLETED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id
3. SELECT EMP_ID FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id → v_emp_id
4. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => v_emp_id, p_type => 'EMAIL', p_subject => 'Performance Review Completed', p_body => 'Your manager has completed your performance review. Please review and acknowledge.', p_user => p_user)

Business rules — Rating scale (exact boundaries):
| Rating Value | Label |
|---|---|
| >= 4.5 | Exceptional |
| >= 3.5 and < 4.5 | Exceeds Expectations |
| >= 2.5 and < 3.5 | Meets Expectations |
| >= 1.5 and < 2.5 | Needs Improvement |
| < 1.5 (and >= 1.0) | Unsatisfactory |

- Valid rating range: 1.0 – 5.0 (inclusive)
- Status transitions to 'COMPLETED'
- Employee notified on completion

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, OVERALL_RATING, RATING_LABEL, MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN, STATUS, EMP_ID, MODIFIED_BY, MODIFIED_DATE)
External service calls: PKG_NOTIFICATION.send_notification
Exceptions thrown: -20403

---

**PROCEDURE acknowledge_review(p_review_id NUMBER, p_emp_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)**

Logic:
- UPDATE PERFORMANCE_REVIEWS SET EMPLOYEE_COMMENTS = p_emp_comments, EMPLOYEE_ACK_DATE = SYSDATE, STATUS = 'ACKNOWLEDGED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS = 'COMPLETED'

Business rule: Only COMPLETED reviews can be acknowledged; status transitions to 'ACKNOWLEDGED'

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE, STATUS, MODIFIED_BY, MODIFIED_DATE)

---

**FUNCTION add_goal(...) RETURN NUMBER**

Parameters: p_review_id NUMBER, p_emp_id NUMBER, p_goal_title VARCHAR2, p_goal_description CLOB DEFAULT NULL, p_goal_category VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct NUMBER DEFAULT 0, p_target_date DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

Logic:
1. SELECT SEQ_PERF_GOAL.NEXTVAL INTO v_goal_id FROM DUAL
2. INSERT INTO PERFORMANCE_GOALS (GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE) VALUES (v_goal_id, p_review_id, p_emp_id, p_goal_title, p_goal_description, p_goal_category, p_weight_pct, p_target_date, 'NOT_STARTED', 0, p_user, SYSDATE)
3. RETURN v_goal_id

Business rules:
- Default category 'BUSINESS'
- Default weight 0
- Initial STATUS = 'NOT_STARTED', PROGRESS_PCT = 0

Tables referenced: PERFORMANCE_GOALS (GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE)
Sequences used: SEQ_PERF_GOAL

---

**PROCEDURE update_goal_progress(p_goal_id NUMBER, p_progress_pct NUMBER, p_status VARCHAR2 DEFAULT NULL, p_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)**

Logic:
- UPDATE PERFORMANCE_GOALS SET PROGRESS_PCT = p_progress_pct, STATUS = NVL(p_status, CASE WHEN p_progress_pct >= 100 THEN 'COMPLETED' WHEN p_progress_pct > 0 THEN 'IN_PROGRESS' ELSE STATUS END), COMMENTS = NVL(p_comments, COMMENTS), MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE GOAL_ID = p_goal_id

Business rules:
- If explicit status not provided: progress >= 100 → 'COMPLETED'; progress > 0 → 'IN_PROGRESS'; progress = 0 → unchanged
- Comments only updated if p_comments IS NOT NULL

Tables referenced: PERFORMANCE_GOALS (GOAL_ID, PROGRESS_PCT, STATUS, COMMENTS, MODIFIED_BY, MODIFIED_DATE)

---

**PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id NUMBER, p_cycle_id NUMBER)**

Logic:
- OPEN p_cursor FOR SELECT pr.REVIEW_ID, pr.EMP_ID, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME, j.JOB_TITLE, d.DEPT_NAME, pr.STATUS, pr.OVERALL_RATING, pr.RATING_LABEL FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pr.REVIEWER_EMP_ID = p_manager_id AND pr.CYCLE_ID = p_cycle_id ORDER BY e.LAST_NAME

Tables referenced: PERFORMANCE_REVIEWS, EMPLOYEES, JOB_TITLES, DEPARTMENTS

---

**FUNCTION get_rating_distribution(p_cycle_id NUMBER, p_dept_id NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR**

Logic:
- OPEN v_cursor FOR SELECT pr.RATING_LABEL, COUNT(*) AS COUNT, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID WHERE pr.CYCLE_ID = p_cycle_id AND pr.OVERALL_RATING IS NOT NULL AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) GROUP BY pr.RATING_LABEL ORDER BY MIN(pr.OVERALL_RATING) DESC
- RETURN v_cursor

Business rule: Percentage uses analytic SUM OVER () for cross-group total; ordered by minimum rating value descending

Tables referenced: PERFORMANCE_REVIEWS (CYCLE_ID, OVERALL_RATING, RATING_LABEL, EMP_ID), EMPLOYEES (EMP_ID, DEPT_ID)

---

**PROCEDURE generate_reviews_for_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. FOR emp_rec IN (SELECT EMP_ID, MANAGER_EMP_ID FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' AND MANAGER_EMP_ID IS NOT NULL):
   - v_review_id := create_review(p_cycle_id, emp_rec.EMP_ID, emp_rec.MANAGER_EMP_ID, p_user); v_count + 1
   - EXCEPTION WHEN DUP_VAL_ON_INDEX → NULL (review already exists)
2. COMMIT
3. DBMS_OUTPUT.PUT_LINE('Generated ' || v_count || ' reviews for cycle ' || p_cycle_id)

Business rule: Only active employees with a manager get reviews (MANAGER_EMP_ID IS NOT NULL); duplicate reviews silently skipped

Tables referenced: EMPLOYEES (EMP_ID, EMPLOYMENT_STATUS, MANAGER_EMP_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks ===

**Package:** HRMS.PKG_REPORTING
**Schema:** HRMS
**Purpose:** Report Generation — headcount, compensation, turnover, compliance reporting

**Dependencies:** PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON
**Called by:** HRMS_REPORTS form, Oracle Reports (.rdf), batch jobs

**Known issues:**
- Denormalized reporting tables refreshed nightly; stale during business hours
- Some reports use hard-coded fiscal year start (Oct 1)

**Type:** `t_report_cursor` — REF CURSOR

**Public Method Signatures:**

`PROCEDURE headcount_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE, p_dept_id NUMBER DEFAULT NULL, p_location VARCHAR2 DEFAULT NULL)`

`PROCEDURE compensation_summary(p_cursor OUT t_report_cursor, p_dept_id NUMBER DEFAULT NULL, p_grade_id NUMBER DEFAULT NULL)`

`PROCEDURE turnover_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)`

`PROCEDURE new_hires_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)`

`PROCEDURE leave_utilization_report(p_cursor OUT t_report_cursor, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE), p_dept_id NUMBER DEFAULT NULL)`

`PROCEDURE payroll_summary_report(p_cursor OUT t_report_cursor, p_period_id NUMBER)`

`PROCEDURE eeo_compliance_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE)`

`PROCEDURE refresh_reporting_tables(p_user VARCHAR2 DEFAULT USER)`

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pkb ===

**Package Body:** HRMS.PKG_REPORTING

---

**PROCEDURE headcount_report(...)**

Query: SELECT d.DEPT_NAME, d.COST_CENTER, l.LOCATION_NAME, l.CITY, l.STATE_PROVINCE, COUNT(*) AS HEADCOUNT, SUM(CASE WHEN e.EMPLOYMENT_TYPE = 'FULL_TIME' THEN 1 ELSE 0 END) AS FT_COUNT, SUM(CASE WHEN e.EMPLOYMENT_TYPE = 'PART_TIME' THEN 1 ELSE 0 END) AS PT_COUNT, SUM(CASE WHEN e.EMPLOYMENT_TYPE = 'CONTRACT' THEN 1 ELSE 0 END) AS CONTRACT_COUNT, SUM(CASE WHEN e.GENDER = 'M' THEN 1 ELSE 0 END) AS MALE_COUNT, SUM(CASE WHEN e.GENDER = 'F' THEN 1 ELSE 0 END) AS FEMALE_COUNT, ROUND(AVG(MONTHS_BETWEEN(p_as_of_date, e.HIRE_DATE) / 12), 1) AS AVG_TENURE_YEARS FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID LEFT JOIN LOCATIONS l ON e.LOCATION_CODE = l.LOCATION_CODE WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.HIRE_DATE <= p_as_of_date AND (e.TERMINATION_DATE IS NULL OR e.TERMINATION_DATE > p_as_of_date) AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) AND (p_location IS NULL OR e.LOCATION_CODE = p_location) GROUP BY d.DEPT_NAME, d.COST_CENTER, l.LOCATION_NAME, l.CITY, l.STATE_PROVINCE ORDER BY d.DEPT_NAME

Business rules:
- Active employees only, hired on or before as-of date
- Terminated on or before as-of date are excluded
- Gender codes: 'M', 'F'; others not explicitly counted
- Employment type codes: 'FULL_TIME', 'PART_TIME', 'CONTRACT'
- Average tenure in years (1 decimal place), calculated vs p_as_of_date

Tables referenced: EMPLOYEES, DEPARTMENTS, LOCATIONS

---

**PROCEDURE compensation_summary(...)**

Query: SELECT d.DEPT_NAME, g.GRADE_NAME, j.JOB_TITLE, COUNT(*) AS EMP_COUNT, g.MIN_SALARY AS GRADE_MIN, g.MAX_SALARY AS GRADE_MAX, MIN(sr.BASE_SALARY) AS ACTUAL_MIN, MAX(sr.BASE_SALARY) AS ACTUAL_MAX, ROUND(AVG(sr.BASE_SALARY), 2) AS AVG_SALARY, ROUND(MEDIAN(sr.BASE_SALARY), 2) AS MEDIAN_SALARY, ROUND(AVG(sr.BASE_SALARY / ((g.MIN_SALARY + g.MAX_SALARY) / 2)) * 100, 1) AS COMPA_RATIO FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID JOIN JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y' WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) AND (p_grade_id IS NULL OR g.GRADE_ID = p_grade_id) GROUP BY d.DEPT_NAME, g.GRADE_NAME, j.JOB_TITLE, g.MIN_SALARY, g.MAX_SALARY ORDER BY d.DEPT_NAME, g.GRADE_NAME

Business rule: Compa-ratio = AVG(actual salary / midpoint) × 100, where midpoint = (MIN_SALARY + MAX_SALARY) / 2

Tables referenced: EMPLOYEES, DEPARTMENTS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS

---

**PROCEDURE turnover_report(...)**

Query: SELECT d.DEPT_NAME, COUNT(CASE WHEN e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) AS TERMINATIONS, COUNT(CASE WHEN e.EMPLOYMENT_STATUS = 'ACTIVE' THEN 1 END) AS CURRENT_HC, ROUND(COUNT(CASE WHEN e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN e.HIRE_DATE <= p_end_date THEN 1 END), 0), 1) AS TURNOVER_PCT, COUNT(CASE WHEN e.TERMINATION_REASON = 'VOLUNTARY' AND e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) AS VOLUNTARY, COUNT(CASE WHEN e.TERMINATION_REASON != 'VOLUNTARY' AND e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) AS INVOLUNTARY, ROUND(AVG(CASE WHEN e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN MONTHS_BETWEEN(e.TERMINATION_DATE, e.HIRE_DATE) / 12 END), 1) AS AVG_TENURE_AT_EXIT FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) AND e.HIRE_DATE <= p_end_date GROUP BY d.DEPT_NAME HAVING COUNT(CASE WHEN e.HIRE_DATE <= p_end_date THEN 1 END) > 0 ORDER BY TURNOVER_PCT DESC NULLS LAST

Business rules:
- Turnover % = terminations in period / all employees hired on or before end date × 100
- Voluntary = TERMINATION_REASON = 'VOLUNTARY'; involuntary = everything else (including NULL termination reason if terminated in period)
- Average tenure at exit measured in years (1 decimal)
- Groups with zero eligible employees excluded (HAVING)
- NULLS LAST in ORDER BY for departments with no terminations

Tables referenced: EMPLOYEES (EMP_ID, DEPT_ID, TERMINATION_DATE, EMPLOYMENT_STATUS, TERMINATION_REASON, HIRE_DATE), DEPARTMENTS (DEPT_ID, DEPT_NAME)

---

**PROCEDURE new_hires_report(...)**

Query: SELECT e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, e.HIRE_DATE, d.DEPT_NAME, j.JOB_TITLE, l.LOCATION_NAME, e.EMPLOYMENT_TYPE, sr.BASE_SALARY, e.MANAGER_EMP_ID, m.FIRST_NAME || ' ' || m.LAST_NAME AS MANAGER_NAME FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID LEFT JOIN LOCATIONS l ON e.LOCATION_CODE = l.LOCATION_CODE LEFT JOIN EMPLOYEES m ON e.MANAGER_EMP_ID = m.EMP_ID LEFT JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y' WHERE e.HIRE_DATE BETWEEN p_start_date AND p_end_date AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) ORDER BY e.HIRE_DATE DESC

Tables referenced: EMPLOYEES (self-join for manager), DEPARTMENTS, JOB_TITLES, LOCATIONS, SALARY_RECORDS

---

**PROCEDURE leave_utilization_report(...)**

Query: SELECT d.DEPT_NAME, lt.LEAVE_TYPE_NAME, COUNT(DISTINCT lb.EMP_ID) AS EMP_COUNT, ROUND(AVG(lb.OPENING_BALANCE + lb.ACCRUED), 1) AS AVG_ENTITLED, ROUND(AVG(lb.USED), 1) AS AVG_USED, ROUND(AVG(lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT), 1) AS AVG_REMAINING, ROUND(AVG(lb.USED) * 100.0 / NULLIF(AVG(lb.OPENING_BALANCE + lb.ACCRUED), 0), 1) AS UTILIZATION_PCT FROM LEAVE_BALANCES lb JOIN EMPLOYEES e ON lb.EMP_ID = e.EMP_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN LEAVE_TYPES lt ON lb.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID WHERE lb.CALENDAR_YEAR = p_year AND e.EMPLOYMENT_STATUS = 'ACTIVE' AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) GROUP BY d.DEPT_NAME, lt.LEAVE_TYPE_NAME ORDER BY d.DEPT_NAME, lt.LEAVE_TYPE_NAME

Business rules:
- Entitled = OPENING_BALANCE + ACCRUED
- Remaining = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT
- Utilization % = AVG_USED / AVG_ENTITLED × 100 (NULLIF prevents divide-by-zero)

Tables referenced: LEAVE_BALANCES, EMPLOYEES, DEPARTMENTS, LEAVE_TYPES

---

**PROCEDURE payroll_summary_report(p_cursor OUT t_report_cursor, p_period_id NUMBER)**

Query: SELECT d.DEPT_NAME, COUNT(DISTINCT pd.EMP_ID) AS EMP_COUNT, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS TOTAL_GROSS, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_FED_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_STATE_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_SS, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_MEDICARE, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS, SUM(pd.AMOUNT) AS TOTAL_NET FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pr.PERIOD_ID = p_period_id AND pd.STATUS != 'ERROR' GROUP BY d.DEPT_NAME ORDER BY d.DEPT_NAME

Tables referenced: PAYROLL_DETAILS, PAYROLL_RUNS, EMPLOYEES, DEPARTMENTS

---

**PROCEDURE eeo_compliance_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE)**

Query: SELECT j.EEO_CATEGORY, COUNT(*) AS TOTAL, SUM(CASE WHEN e.GENDER = 'M' THEN 1 ELSE 0 END) AS MALE, SUM(CASE WHEN e.GENDER = 'F' THEN 1 ELSE 0 END) AS FEMALE, SUM(CASE WHEN e.GENDER = 'O' THEN 1 ELSE 0 END) AS OTHER_GENDER, SUM(CASE WHEN e.GENDER IS NULL THEN 1 ELSE 0 END) AS NOT_DISCLOSED, ROUND(SUM(CASE WHEN e.GENDER = 'F' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS FEMALE_PCT FROM EMPLOYEES e JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.HIRE_DATE <= p_as_of_date GROUP BY j.EEO_CATEGORY ORDER BY j.EEO_CATEGORY

Business rules:
- Gender codes: 'M' (male), 'F' (female), 'O' (other), NULL (not disclosed)
- Female % = female count / total × 100 (1 decimal)
- Grouped by EEO_CATEGORY from JOB_TITLES table

Tables referenced: EMPLOYEES (EMP_ID, GENDER, EMPLOYMENT_STATUS, HIRE_DATE, JOB_ID), JOB_TITLES (JOB_ID, EEO_CATEGORY)

---

**PROCEDURE refresh_reporting_tables(p_user VARCHAR2 DEFAULT USER)**

Logic: Placeholder — calls PKG_COMMON.log_info('PKG_REPORTING', 'refresh_reporting_tables', 'Reporting tables refreshed', p_user)

Note: In production, truncates and repopulates RPT_* denormalized reporting tables. Not implemented here.

External service calls: PKG_COMMON.log_info

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb ===

**Package:** HRMS.PKG_SECURITY (body only — no .pks provided in source set)
**Schema:** HRMS
**Purpose:** Authentication and Authorization

---

**Private Constants:**
- `c_encryption_key` — RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!') **VULNERABILITY: hard-coded encryption key in source**
- `c_session_timeout_min` — NUMBER := 30 (session timeout in minutes)

---

**FUNCTION hash_password(p_password VARCHAR2) RETURN VARCHAR2**

Logic: RETURN RAWTOHEX(DBMS_CRYPTO.HASH(UTL_RAW.CAST_TO_RAW(p_password), DBMS_CRYPTO.HASH_MD5))

Security weakness: Uses MD5 — should use stronger algorithm (SHA-256 or bcrypt)
External calls: DBMS_CRYPTO.HASH (HASH_MD5), UTL_RAW.CAST_TO_RAW, RAWTOHEX

---

**FUNCTION authenticate(p_username VARCHAR2, p_password VARCHAR2, p_ip_address VARCHAR2 DEFAULT NULL) RETURN NUMBER**

Logic:
1. SELECT EMP_ID FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(p_username) AND EMPLOYMENT_STATUS = 'ACTIVE'; EXCEPTION WHEN NO_DATA_FOUND → RAISE_APPLICATION_ERROR(-20301, 'Invalid username or password'); WHEN TOO_MANY_ROWS → SELECT MIN(EMP_ID) ... (picks lowest EMP_ID among duplicates)
2. SELECT SEQ_USER_SESSION.NEXTVAL INTO v_session_id FROM DUAL
3. INSERT INTO USER_SESSIONS (SESSION_ID, EMP_ID, USERNAME, LOGIN_TIME, IP_ADDRESS, SESSION_STATUS, CREATED_DATE) VALUES (v_session_id, v_emp_id, p_username, SYSDATE, p_ip_address, 'ACTIVE', SYSDATE)
4. PKG_EMPLOYEE.set_session_context(p_username, v_emp_id)
5. PKG_AUDIT.log_action('USER_SESSIONS', v_session_id, 'INSERT', p_username)
6. RETURN v_session_id

Security vulnerabilities:
- No brute-force protection (no lockout after N failed attempts)
- Timing attack: NO_DATA_FOUND (invalid user) returns immediately while valid-user/invalid-password path would differ — response times distinguishable
- Authentication appears to not actually verify p_password against a stored hash (comment says passwords in separate USER_CREDENTIALS table — actual check not implemented here)

Tables referenced: EMPLOYEES (EMAIL, EMPLOYMENT_STATUS, EMP_ID), USER_SESSIONS (SESSION_ID, EMP_ID, USERNAME, LOGIN_TIME, IP_ADDRESS, SESSION_STATUS, CREATED_DATE)
Sequences used: SEQ_USER_SESSION
External service calls: PKG_EMPLOYEE.set_session_context, PKG_AUDIT.log_action
Exceptions thrown: -20301

---

**PROCEDURE logout(p_session_id NUMBER)**

Logic: UPDATE USER_SESSIONS SET LOGOUT_TIME = SYSDATE, SESSION_STATUS = 'CLOSED' WHERE SESSION_ID = p_session_id

Tables referenced: USER_SESSIONS (SESSION_ID, LOGOUT_TIME, SESSION_STATUS)

---

**FUNCTION is_session_valid(p_session_id NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT SESSION_STATUS, LOGIN_TIME FROM USER_SESSIONS WHERE SESSION_ID = p_session_id → v_status, v_login_time
2. IF v_status != 'ACTIVE' → RETURN FALSE
3. IF (SYSDATE - v_login_time) * 24 * 60 > 30 (c_session_timeout_min): UPDATE USER_SESSIONS SET SESSION_STATUS = 'EXPIRED', LOGOUT_TIME = SYSDATE WHERE SESSION_ID = p_session_id; RETURN FALSE
4. RETURN TRUE
5. EXCEPTION WHEN NO_DATA_FOUND → RETURN FALSE

Business rule: Session expires after 30 minutes of inactivity from login time (note: based on LOGIN_TIME, not last activity — no session refresh/touch implemented)

Tables referenced: USER_SESSIONS (SESSION_ID, SESSION_STATUS, LOGIN_TIME, LOGOUT_TIME)

---

**FUNCTION has_permission(p_emp_id NUMBER, p_module VARCHAR2, p_action VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN**

Logic:
1. SELECT e.DEPT_ID, j.GRADE_ID FROM EMPLOYEES e JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE e.EMP_ID = p_emp_id
2. Permission rules (simplified grade-based model):
   - IF v_grade_id >= 8 → RETURN TRUE (senior management, full access to all modules)
   - IF p_action = 'VIEW' AND v_grade_id >= 5 → RETURN TRUE (mid-level can view all)
   - IF p_module = 'LEAVE' AND p_action IN ('CREATE', 'VIEW') → RETURN TRUE (everyone can submit/view own leave)
   - IF p_module = 'EMPLOYEE' AND p_action = 'VIEW' → RETURN TRUE (everyone can view own profile)
   - RETURN FALSE
3. EXCEPTION WHEN NO_DATA_FOUND → RETURN FALSE

Business rules — Permission tiers:
| Grade | Access Level |
|---|---|
| >= 8 | Full access to all modules and all actions |
| >= 5 and < 8 | VIEW action on all modules |
| Any grade | CREATE and VIEW on LEAVE module |
| Any grade | VIEW on EMPLOYEE module |
| All others | No access |

Note: This is declared as a simplified model; production would use a ROLES / PERMISSIONS junction table

Tables referenced: EMPLOYEES (EMP_ID, DEPT_ID, JOB_ID), JOB_TITLES (JOB_ID, GRADE_ID)

---

**FUNCTION encrypt_ssn(p_ssn VARCHAR2) RETURN VARCHAR2**

Logic:
- v_raw := DBMS_CRYPTO.ENCRYPT(src => UTL_RAW.CAST_TO_RAW(p_ssn), typ => DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC + DBMS_CRYPTO.PAD_PKCS5, key => c_encryption_key)
- RETURN RAWTOHEX(v_raw)

Algorithm: AES-256, CBC mode, PKCS5 padding
Security vulnerability: Encryption key 'HR$ystem_3ncrypt10n_K3y_2024!!' hard-coded in source

External calls: DBMS_CRYPTO.ENCRYPT, UTL_RAW.CAST_TO_RAW, RAWTOHEX

---

**FUNCTION decrypt_ssn(p_encrypted VARCHAR2) RETURN VARCHAR2**

Logic:
- v_raw := DBMS_CRYPTO.DECRYPT(src => HEXTORAW(p_encrypted), typ => DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC + DBMS_CRYPTO.PAD_PKCS5, key => c_encryption_key)
- RETURN UTL_RAW.CAST_TO_VARCHAR2(v_raw)
- EXCEPTION WHEN OTHERS → RETURN '***DECRYPT_ERROR***'

External calls: DBMS_CRYPTO.DECRYPT, HEXTORAW, UTL_RAW.CAST_TO_VARCHAR2

---

**PROCEDURE change_password(p_emp_id NUMBER, p_old_password VARCHAR2, p_new_password VARCHAR2)**

Logic:
1. IF LENGTH(p_new_password) < 8 → RAISE_APPLICATION_ERROR(-20310, 'Password must be at least 8 characters')
2. IF NOT REGEXP_LIKE(p_new_password, '[A-Z]') → RAISE_APPLICATION_ERROR(-20311, 'Password must contain an uppercase letter')
3. IF NOT REGEXP_LIKE(p_new_password, '[0-9]') → RAISE_APPLICATION_ERROR(-20312, 'Password must contain a number')
4. PKG_AUDIT.log_action('USER_CREDENTIALS', p_emp_id, 'UPDATE', USER)

Password complexity rules:
- Minimum length: 8 characters
- Must contain at least one uppercase letter [A-Z]
- Must contain at least one digit [0-9]
- No maximum length constraint
- No special character requirement
- Old password is accepted as parameter but not verified (stub implementation — actual update to USER_CREDENTIALS not implemented)

External service calls: PKG_AUDIT.log_action
Exceptions thrown: -20310 (too short), -20311 (no uppercase), -20312 (no number)


- No status pre-check; any run can be reversed
- p_reason parameter accepted but not stored (no column update with it)
- Both run and all detail lines marked 'REVERSED'

Database references:
- Table: PAYROLL_RUNS; columns: RUN_ID, STATUS, MODIFIED_BY, MODIFIED_DATE
- Table: PAYROLL_DETAILS; columns: RUN_ID, STATUS

External services called:
- PKG_AUDIT.log_action

---

**FUNCTION calculate_federal_tax(...) RETURN NUMBER**

Logic:
1. v_periods := CASE p_pay_frequency WHEN 'WEEKLY' THEN 52 WHEN 'BIWEEKLY' THEN 26 WHEN 'SEMIMONTHLY' THEN 24 WHEN 'MONTHLY' THEN 12 ELSE 12 END
2. v_annualized := p_taxable_income * v_periods
3. v_std_deduction := CASE WHEN p_filing_status IN ('MARRIED_JOINT') THEN 29200 ELSE 14600 END
4. v_taxable := v_annualized - v_std_deduction - (p_allowances * 4300)
5. IF v_taxable <= 0 THEN RETURN 0
6. Apply 2024 brackets:

**SINGLE / MARRIED_SEPARATE brackets (2024, annualized taxable income):**
| Bracket | Income Range | Tax |
|---|---|---|
| 1 | 0 – 11,600 | taxable × 0.10 |
| 2 | 11,600.01 – 47,150 | 1,160 + (taxable − 11,600) × 0.12 |
| 3 | 47,150.01 – 100,525 | 5,426 + (taxable − 47,150) × 0.22 |
| 4 | 100,525.01 – 191,950 | 17,168.50 + (taxable − 100,525) × 0.24 |
| 5 | 191,950.01 – 243,725 | 39,110.50 + (taxable − 191,950) × 0.32 |
| 6 | 243,725.01 – 609,350 | 55,678.50 + (taxable − 243,725) × 0.35 |
| 7 | 609,350.01 + | 183,647.25 + (taxable − 609,350) × 0.37 |

**MARRIED_JOINT brackets (2024, annualized taxable income):**
| Bracket | Income Range | Tax |
|---|---|---|
| 1 | 0 – 23,200 | taxable × 0.10 |
| 2 | 23,200.01 – 94,300 | 2,320 + (taxable − 23,200) × 0.12 |
| 3 | 94,300.01 – 201,050 | 10,852 + (taxable − 94,300) × 0.22 |
| 4 | 201,050.01 – 383,900 | 34,337 + (taxable − 201,050) × 0.24 |
| 5 | 383,900.01 – 487,450 | 78,221 + (taxable − 383,900) × 0.32 |
| 6 | 487,450.01 – 731,200 | 111,357 + (taxable − 487,450) × 0.35 |
| 7 | 731,200.01 + | 196,669.50 + (taxable − 731,200) × 0.37 |

7. v_tax := ROUND(v_tax / v_periods, 2)
8. v_tax := v_tax + NVL(p_additional_wh, 0)
9. RETURN v_tax

Business rules:
- Income is annualized first, then de-annualized after bracket calculation
- Standard deduction: 29,200 for MARRIED_JOINT; 14,600 for all others (SINGLE, MARRIED_SEPARATE, or any other value)
- Each allowance reduces annualized taxable income by exactly 4,300
- If v_taxable <= 0 after deductions and allowances, tax = 0
- Additional withholding (from W-4) added per-period after de-annualizing
- Filing status not in SINGLE/MARRIED_SEPARATE/MARRIED_JOINT yields v_tax = 0 (no branch matches)
- Note: TODO in code — should read from TAX_BRACKETS table instead of hard-coded values

---

**FUNCTION calculate_state_tax(...) RETURN NUMBER**

Logic:
1. v_rate := CASE p_state_code WHEN 'CA' THEN 0.0725 WHEN 'NY' THEN 0.0685 WHEN 'TX' THEN 0 WHEN 'FL' THEN 0 WHEN 'WA' THEN 0 WHEN 'IL' THEN 0.0495 WHEN 'PA' THEN 0.0307 WHEN 'OH' THEN 0.04 WHEN 'NJ' THEN 0.0637 WHEN 'MA' THEN 0.05 ELSE 0.05 END
2. RETURN ROUND(p_taxable_income * v_rate, 2)

**State flat rate table:**
| State | Rate |
|---|---|
| CA | 7.25% |
| NY | 6.85% |
| TX | 0% (no state income tax) |
| FL | 0% (no state income tax) |
| WA | 0% (no state income tax) |
| IL | 4.95% |
| PA | 3.07% |
| OH | 4.00% |
| NJ | 6.37% |
| MA | 5.00% |
| All others | 5.00% (default) |

Business rules:
- Simplified flat rates — noted in code that actual implementation would be bracket-based
- p_allowances and p_filing_status parameters accepted but NOT used in calculation
- Unknown states default to 5.00%
- Applied directly to per-period taxable income (not annualized)

---

**FUNCTION calculate_fica(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER**

Logic:
1. IF p_ytd_gross >= 168600 THEN RETURN 0 — already exceeded 2024 SS wage base
2. v_taxable := LEAST(p_gross_pay, 168600 - p_ytd_gross) — cap at remaining wage base
3. RETURN ROUND(v_taxable * 0.062, 2)

Business rules:
- 2024 Social Security wage base: **168,600**
- Employee rate: **6.2%** (0.062)
- Once YTD gross >= 168,600, no further SS tax withheld
- Partial period handling: only taxes wages up to the wage base ceiling

---

**FUNCTION calculate_medicare(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER**

Logic:
1. v_base_tax := ROUND(p_gross_pay * 0.0145, 2)
2. IF p_ytd_gross + p_gross_pay > 200000 THEN:
   - IF p_ytd_gross >= 200000 THEN: v_addl_tax := ROUND(p_gross_pay * 0.009, 2)
   - ELSE: v_addl_tax := ROUND((p_ytd_gross + p_gross_pay - 200000) * 0.009, 2)
3. RETURN v_base_tax + v_addl_tax

Business rules:
- Base Medicare rate: **1.45%** (0.0145) — no wage base cap
- Additional Medicare rate: **0.9%** (0.009) on wages above **200,000**
- Partial-period threshold crossing: only the amount above 200,000 in the current period is taxed at additional rate
- Additional tax threshold: 200,000 (note: IRS threshold is actually 200,000 for single/250,000 for MFJ — code uses single flat threshold for all filing statuses)

---

**PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)**

Logic:
1. OPEN p_cursor FOR: SELECT pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, pp.PERIOD_NAME, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','TAX','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS, SUM(pd.AMOUNT) AS NET_PAY, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE, 0 AS YTD_GROSS, 0 AS YTD_NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND (p_emp_id IS NULL OR pd.EMP_ID = p_emp_id) GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME ORDER BY e.LAST_NAME

Business rules:
- YTD_GROSS and YTD_NET are hard-coded to 0 (placeholder — not yet implemented)
- Tax breakdown uses fixed ELEMENT_ID assignments: 100=federal, 101=state, 102=SS, 103=Medicare
- Excludes ERROR status payroll details
- Optional filter by p_emp_id; if NULL returns all employees in the run

Database references:
- Table: PAYROLL_DETAILS; columns: EMP_ID, RUN_ID, ELEMENT_TYPE, ELEMENT_ID, AMOUNT, STATUS
- Table: EMPLOYEES; columns: EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME
- Table: PAYROLL_RUNS; columns: RUN_ID, PERIOD_ID
- Table: PAY_PERIODS; columns: PERIOD_ID, PERIOD_NAME

---

**FUNCTION get_ytd_earnings(p_emp_id IN NUMBER, p_tax_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
1. SELECT NVL(SUM(pd.AMOUNT), 0) INTO v_ytd FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.EMP_ID = p_emp_id AND pd.ELEMENT_TYPE = 'EARNING' AND pd.STATUS = 'CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
2. RETURN v_ytd

Business rules:
- YTD uses PERIOD_START_DATE year for tax year assignment
- Only STATUS = 'CALCULATED' records counted (excludes REVERSED, ERROR)
- Only ELEMENT_TYPE = 'EARNING' amounts summed

Database references:
- Table: PAYROLL_DETAILS; columns: EMP_ID, RUN_ID, ELEMENT_TYPE, AMOUNT, STATUS
- Table: PAYROLL_RUNS; columns: RUN_ID, PERIOD_ID
- Table: PAY_PERIODS; columns: PERIOD_ID, PERIOD_START_DATE

---

**PROCEDURE generate_pay_register(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT pp.PERIOD_NAME FROM PAYROLL_RUNS pr JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pr.RUN_ID = p_run_id
2. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS') || '.csv'
3. UTL_FILE.FOPEN('PAYROLL_OUTPUT', v_filename, 'W', 32767)
4. Write CSV header: 'EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY'
5. Query: SELECT e.EMP_NUMBER, e.FIRST_NAME||' '||e.LAST_NAME AS EMP_NAME, d.DEPT_NAME, SUM(EARNING amounts) AS GROSS, SUM(ELEMENT_ID=100) AS FED, SUM(ELEMENT_ID=101) AS STATE, SUM(ELEMENT_ID=102) AS SS, SUM(ELEMENT_ID=103) AS MED, SUM(DEDUCTION/BENEFIT amounts) AS DEDS, SUM(all AMOUNT) AS NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e JOIN DEPARTMENTS d WHERE RUN_ID = p_run_id AND STATUS != 'ERROR' GROUP BY EMP_NUMBER, EMP_NAME, DEPT_NAME ORDER BY LAST_NAME
6. Write each row: EMP_NUMBER,"EMP_NAME","DEPT_NAME",GROSS,FED,STATE,SS,MED,DEDS,NET (amounts formatted with 'FM999999990.00')
7. UTL_FILE.FCLOSE; DBMS_OUTPUT.PUT_LINE('Pay register generated: ' || v_filename)
8. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

Business rules:
- Output directory Oracle object name: 'PAYROLL_OUTPUT'
- Filename format: PAY_REGISTER_{run_id}_{YYYYMMDD_HH24MISS}.csv
- CSV — EMPLOYEE_NAME and DEPT_NAME are double-quoted; numeric amounts are not quoted
- Amount format mask: 'FM999999990.00'
- File buffer: 32767 bytes

Database references:
- Table: PAYROLL_RUNS; columns: RUN_ID, PERIOD_ID
- Table: PAY_PERIODS; columns: PERIOD_ID, PERIOD_NAME
- Table: PAYROLL_DETAILS; columns: RUN_ID, EMP_ID, ELEMENT_TYPE, ELEMENT_ID, AMOUNT, STATUS
- Table: EMPLOYEES; columns: EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID
- Table: DEPARTMENTS; columns: DEPT_ID, DEPT_NAME

External services called:
- UTL_FILE (Oracle directory: PAYROLL_OUTPUT)
- PKG_COMMON.log_error

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks ===

**Package:** HRMS.PKG_PERFORMANCE
**Type:** Package Specification

**Type Definitions:**
`t_review_cursor IS REF CURSOR`

**Public Method Signatures:**

`FUNCTION create_review_cycle(p_cycle_name IN VARCHAR2, p_cycle_year IN NUMBER, p_start_date IN DATE, p_end_date IN DATE, p_self_review_due IN DATE DEFAULT NULL, p_manager_review_due IN DATE DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE open_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE close_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)`

`FUNCTION create_review(p_cycle_id IN NUMBER, p_emp_id IN NUMBER, p_reviewer_emp_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE submit_self_assessment(p_review_id IN NUMBER, p_self_assessment IN CLOB, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE submit_manager_review(p_review_id IN NUMBER, p_overall_rating IN NUMBER, p_manager_assessment IN CLOB, p_strengths IN CLOB DEFAULT NULL, p_improvement_areas IN CLOB DEFAULT NULL, p_development_plan IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE acknowledge_review(p_review_id IN NUMBER, p_emp_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)`

`FUNCTION add_goal(p_review_id IN NUMBER, p_emp_id IN NUMBER, p_goal_title IN VARCHAR2, p_goal_description IN CLOB DEFAULT NULL, p_goal_category IN VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct IN NUMBER DEFAULT 0, p_target_date IN DATE DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE update_goal_progress(p_goal_id IN NUMBER, p_progress_pct IN NUMBER, p_status IN VARCHAR2 DEFAULT NULL, p_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id IN NUMBER, p_cycle_id IN NUMBER)`

`FUNCTION get_rating_distribution(p_cycle_id IN NUMBER, p_dept_id IN NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR`

`PROCEDURE generate_reviews_for_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)`

**Dependencies declared in spec comments:**
- PKG_EMPLOYEE
- PKG_COMMON
- PKG_AUDIT
- PKG_NOTIFICATION

**Callers declared in spec comments:**
- HRMS_PERFORMANCE form
- batch calibration job

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb ===

**Package:** HRMS.PKG_PERFORMANCE
**Type:** Package Body

---

**FUNCTION create_review_cycle(...) RETURN NUMBER**

Logic:
1. SELECT SEQ_REVIEW_CYCLE.NEXTVAL INTO v_cycle_id FROM DUAL
2. INSERT INTO REVIEW_CYCLES (CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_cycle_id, p_cycle_name, p_cycle_year, p_start_date, p_end_date, p_self_review_due, p_manager_review_due, 'DRAFT', p_user, SYSDATE)
3. PKG_AUDIT.log_action('REVIEW_CYCLES', v_cycle_id, 'INSERT', p_user)
4. RETURN v_cycle_id

Business rules:
- Initial status: 'DRAFT'

Database references:
- Table: REVIEW_CYCLES; columns: CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE
- Sequence: SEQ_REVIEW_CYCLE

External services called:
- PKG_AUDIT.log_action

---

**PROCEDURE open_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE REVIEW_CYCLES SET STATUS = 'OPEN', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id AND STATUS = 'DRAFT'
2. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20401, 'Cannot open cycle - must be in DRAFT status')

Business rules:
- Only DRAFT cycles can be opened

Exceptions thrown:
- -20401: Cannot open cycle — must be in DRAFT status

Database references:
- Table: REVIEW_CYCLES; columns: CYCLE_ID, STATUS, MODIFIED_BY, MODIFIED_DATE

---

**PROCEDURE close_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE REVIEW_CYCLES SET STATUS = 'CLOSED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id

Business rules:
- No status pre-check — any cycle can be closed regardless of current status

Database references:
- Table: REVIEW_CYCLES; columns: CYCLE_ID, STATUS, MODIFIED_BY, MODIFIED_DATE

---

**FUNCTION create_review(p_cycle_id IN NUMBER, p_emp_id IN NUMBER, p_reviewer_emp_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER**

Logic:
1. SELECT SEQ_PERF_REVIEW.NEXTVAL INTO v_review_id FROM DUAL
2. INSERT INTO PERFORMANCE_REVIEWS (REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_review_id, p_cycle_id, p_emp_id, p_reviewer_emp_id, 'ANNUAL', 'NOT_STARTED', p_user, SYSDATE)
3. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => p_emp_id, p_type => 'EMAIL', p_subject => 'Performance Review Initiated', p_body => 'Your annual performance review has been initiated. Please complete your self-assessment.')
4. RETURN v_review_id

Business rules:
- REVIEW_TYPE always set to 'ANNUAL'
- Initial STATUS: 'NOT_STARTED'
- Employee notified on review creation

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE
- Sequence: SEQ_PERF_REVIEW

External services called:
- PKG_NOTIFICATION.send_notification

---

**PROCEDURE submit_self_assessment(p_review_id IN NUMBER, p_self_assessment IN CLOB, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_REVIEWS SET SELF_ASSESSMENT = p_self_assessment, STATUS = 'MANAGER_REVIEW', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS IN ('NOT_STARTED', 'SELF_REVIEW')
2. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20402, 'Review not found or not in correct status')
3. SELECT REVIEWER_EMP_ID INTO v_manager_id FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id
4. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => v_manager_id, p_type => 'EMAIL', p_subject => 'Self-Assessment Submitted - Ready for Manager Review', p_body => 'An employee has completed their self-assessment. Please proceed with the manager review.')

Business rules:
- Self-assessment can be submitted from NOT_STARTED or SELF_REVIEW status
- Status transitions to 'MANAGER_REVIEW' on submission
- Manager notified on self-assessment submission

Exceptions thrown:
- -20402: Review not found or not in correct status

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, STATUS, SELF_ASSESSMENT, REVIEWER_EMP_ID, MODIFIED_BY, MODIFIED_DATE

External services called:
- PKG_NOTIFICATION.send_notification

---

**PROCEDURE submit_manager_review(...)**

Logic:
1. IF p_overall_rating < 1.0 OR p_overall_rating > 5.0 THEN RAISE_APPLICATION_ERROR(-20403, 'Rating must be between 1.0 and 5.0')
2. UPDATE PERFORMANCE_REVIEWS SET OVERALL_RATING = p_overall_rating, RATING_LABEL = CASE WHEN p_overall_rating >= 4.5 THEN 'Exceptional' WHEN p_overall_rating >= 3.5 THEN 'Exceeds Expectations' WHEN p_overall_rating >= 2.5 THEN 'Meets Expectations' WHEN p_overall_rating >= 1.5 THEN 'Needs Improvement' ELSE 'Unsatisfactory' END, MANAGER_ASSESSMENT = p_manager_assessment, STRENGTHS = p_strengths, AREAS_FOR_IMPROVEMENT = p_improvement_areas, DEVELOPMENT_PLAN = p_development_plan, STATUS = 'COMPLETED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id
3. SELECT EMP_ID INTO v_emp_id FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id
4. PKG_NOTIFICATION.send_notification(employee, 'EMAIL', 'Performance Review Completed', 'Your manager has completed your performance review. Please review and acknowledge.')

Business rules — rating scale (1.0–5.0) and labels:
| Threshold | Label |
|---|---|
| >= 4.5 | Exceptional |
| >= 3.5 (and < 4.5) | Exceeds Expectations |
| >= 2.5 (and < 3.5) | Meets Expectations |
| >= 1.5 (and < 2.5) | Needs Improvement |
| < 1.5 (1.0–1.49) | Unsatisfactory |

- Rating must be between 1.0 and 5.0 (inclusive)
- No status pre-check on the UPDATE (any review can have manager assessment submitted)
- Status set to 'COMPLETED' on submission
- Employee notified by email

Exceptions thrown:
- -20403: Rating must be between 1.0 and 5.0

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, EMP_ID, OVERALL_RATING, RATING_LABEL, MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN, STATUS, MODIFIED_BY, MODIFIED_DATE

External services called:
- PKG_NOTIFICATION.send_notification

---

**PROCEDURE acknowledge_review(p_review_id IN NUMBER, p_emp_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_REVIEWS SET EMPLOYEE_COMMENTS = p_emp_comments, EMPLOYEE_ACK_DATE = SYSDATE, STATUS = 'ACKNOWLEDGED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS = 'COMPLETED'

Business rules:
- Only COMPLETED reviews can be acknowledged
- Silently does nothing if review not in COMPLETED status (no error raised)
- EMPLOYEE_ACK_DATE recorded as SYSDATE

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, STATUS, EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE, MODIFIED_BY, MODIFIED_DATE

---

**FUNCTION add_goal(...) RETURN NUMBER**

Logic:
1. SELECT SEQ_PERF_GOAL.NEXTVAL INTO v_goal_id FROM DUAL
2. INSERT INTO PERFORMANCE_GOALS (GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE) VALUES (v_goal_id, p_review_id, p_emp_id, p_goal_title, p_goal_description, p_goal_category, p_weight_pct, p_target_date, 'NOT_STARTED', 0, p_user, SYSDATE)
3. RETURN v_goal_id

Business rules:
- Initial status: 'NOT_STARTED'
- Initial PROGRESS_PCT: 0
- Default category: 'BUSINESS'
- Default weight: 0

Database references:
- Table: PERFORMANCE_GOALS; columns: GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE
- Sequence: SEQ_PERF_GOAL

---

**PROCEDURE update_goal_progress(p_goal_id IN NUMBER, p_progress_pct IN NUMBER, p_status IN VARCHAR2 DEFAULT NULL, p_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_GOALS SET PROGRESS_PCT = p_progress_pct, STATUS = NVL(p_status, CASE WHEN p_progress_pct >= 100 THEN 'COMPLETED' WHEN p_progress_pct > 0 THEN 'IN_PROGRESS' ELSE STATUS END), COMMENTS = NVL(p_comments, COMMENTS), MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE GOAL_ID = p_goal_id

Business rules — auto status derivation (when p_status IS NULL):
- PROGRESS_PCT >= 100 → STATUS = 'COMPLETED'
- PROGRESS_PCT > 0 (and < 100) → STATUS = 'IN_PROGRESS'
- PROGRESS_PCT = 0 → STATUS unchanged
- p_status overrides auto-derivation when provided
- p_comments: NULL input preserves existing comment

Database references:
- Table: PERFORMANCE_GOALS; columns: GOAL_ID, PROGRESS_PCT, STATUS, COMMENTS, MODIFIED_BY, MODIFIED_DATE

---

**PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id IN NUMBER, p_cycle_id IN NUMBER)**

Logic:
1. OPEN p_cursor FOR: SELECT pr.REVIEW_ID, pr.EMP_ID, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME, j.JOB_TITLE, d.DEPT_NAME, pr.STATUS, pr.OVERALL_RATING, pr.RATING_LABEL FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pr.REVIEWER_EMP_ID = p_manager_id AND pr.CYCLE_ID = p_cycle_id ORDER BY e.LAST_NAME

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, EMP_ID, REVIEWER_EMP_ID, CYCLE_ID, STATUS, OVERALL_RATING, RATING_LABEL
- Table: EMPLOYEES; columns: EMP_ID, FIRST_NAME, LAST_NAME, JOB_ID, DEPT_ID
- Table: JOB_TITLES; columns: JOB_ID, JOB_TITLE
- Table: DEPARTMENTS; columns: DEPT_ID, DEPT_NAME

---

**FUNCTION get_rating_distribution(p_cycle_id IN NUMBER, p_dept_id IN NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR**

Logic:
1. OPEN v_cursor FOR: SELECT pr.RATING_LABEL, COUNT(*) AS COUNT, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID WHERE pr.CYCLE_ID = p_cycle_id AND pr.OVERALL_RATING IS NOT NULL AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) GROUP BY pr.RATING_LABEL ORDER BY MIN(pr.OVERALL_RATING) DESC
2. RETURN v_cursor

Business rules:
- Only reviews with non-null OVERALL_RATING included
- Percentage calculated using analytic SUM OVER () — window over all returned groups
- Percentage rounded to 1 decimal place
- Ordered by MIN(OVERALL_RATING) DESC — places 'Exceptional' first

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, CYCLE_ID, EMP_ID, RATING_LABEL, OVERALL_RATING
- Table: EMPLOYEES; columns: EMP_ID, DEPT_ID

---

**PROCEDURE generate_reviews_for_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. Loop: SELECT EMP_ID, MANAGER_EMP_ID FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' AND MANAGER_EMP_ID IS NOT NULL
2. For each employee: v_review_id := create_review(p_cycle_id, EMP_ID, MANAGER_EMP_ID, p_user); v_count++
3. EXCEPTION WHEN DUP_VAL_ON_INDEX: NULL (review already exists — skip)
4. COMMIT
5. DBMS_OUTPUT.PUT_LINE('Generated ' || v_count || ' reviews for cycle ' || p_cycle_id)

Business rules:
- Only active employees with a manager are assigned reviews
- Top-level employees (MANAGER_EMP_ID IS NULL) are excluded
- Idempotent: duplicate reviews silently skipped via DUP_VAL_ON_INDEX handler
- Bulk commit at end (single COMMIT after all employees processed)

Database references:
- Table: EMPLOYEES; columns: EMP_ID, EMPLOYMENT_STATUS, MANAGER_EMP_ID

---

**Complete cross-package dependency map:**

| Package | Calls |
|---|---|
| PKG_EMPLOYEE | PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification, PKG_COMMON.log_error |
| PKG_PAYROLL | PKG_AUDIT.log_action, PKG_COMMON.log_error, PKG_COMMON.log_info |
| PKG_LEAVE | PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action |
| PKG_INTEGRATION | PKG_COMMON.log_info, PKG_COMMON.log_error, PKG_COMMON.get_param |
| PKG_NOTIFICATION | PKG_COMMON.log_error |
| PKG_PERFORMANCE | PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action |

**Circular dependency:** PKG_EMPLOYEE → PKG_PAYROLL.create_salary_record; PKG_PAYROLL may call PKG_EMPLOYEE.is_active for validation.

**Complete database table inventory:**

EMPLOYEES, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS, EMPLOYEE_PAY_ELEMENTS, EMPLOYEE_TAX_INFO, DEPARTMENTS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS, LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES, LEAVE_ACCRUAL_LOG, HOLIDAYS, PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS, PAY_ELEMENTS, NOTIFICATION_QUEUE, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS, REVIEW_CYCLES

**Complete sequence inventory:**

SEQ_EMPLOYEE, SEQ_EMP_HISTORY, SEQ_SALARY, SEQ_PAY_PERIOD, SEQ_PAYROLL_RUN, SEQ_PAYROLL_DETAIL, SEQ_LEAVE_REQUEST, SEQ_LEAVE_BALANCE, SEQ_LEAVE_ACCRUAL, SEQ_NOTIFICATION, SEQ_PERF_REVIEW, SEQ_PERF_GOAL, SEQ_REVIEW_CYCLE

**Oracle directory objects used:**

GL_FEED_OUT (GL journal output), BENEFITS_FEED_OUT (benefits export), TIME_ATTENDANCE_IN (time import), PAYROLL_OUTPUT (pay register)


=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks ===

**Package:** HRMS.PKG_EMPLOYEE
**Schema:** HRMS
**Type:** Package Specification

---

**Global Package Variables (session state):**
- `g_current_user` — VARCHAR2(30)
- `g_current_emp_id` — NUMBER(10)
- `g_current_dept_id` — NUMBER(10)
- `g_debug_mode` — BOOLEAN, default FALSE

---

**Custom Exceptions:**

| Name | Code | PRAGMA binding |
|---|---|---|
| e_employee_not_found | -20001 | PRAGMA EXCEPTION_INIT |
| e_duplicate_emp_number | -20002 | PRAGMA EXCEPTION_INIT |
| e_invalid_department | -20003 | PRAGMA EXCEPTION_INIT |
| e_invalid_manager | -20004 | PRAGMA EXCEPTION_INIT |
| e_termination_error | -20005 | PRAGMA EXCEPTION_INIT |

---

**Type Definitions:**

`TYPE t_emp_rec IS RECORD`:
- emp_id — EMPLOYEES.EMP_ID%TYPE
- emp_number — EMPLOYEES.EMP_NUMBER%TYPE
- first_name — EMPLOYEES.FIRST_NAME%TYPE
- last_name — EMPLOYEES.LAST_NAME%TYPE
- hire_date — EMPLOYEES.HIRE_DATE%TYPE
- dept_id — EMPLOYEES.DEPT_ID%TYPE
- job_id — EMPLOYEES.JOB_ID%TYPE
- manager_emp_id — EMPLOYEES.MANAGER_EMP_ID%TYPE
- employment_status — EMPLOYEES.EMPLOYMENT_STATUS%TYPE
- base_salary — NUMBER(12,2)

`TYPE t_emp_cursor IS REF CURSOR`

`TYPE t_emp_id_table IS TABLE OF NUMBER(10) INDEX BY BINARY_INTEGER`

`TYPE t_emp_rec_table IS TABLE OF t_emp_rec INDEX BY BINARY_INTEGER`

---

**Public Procedure/Function Signatures:**

| Name | Kind | Parameters | Returns |
|---|---|---|---|
| create_employee | FUNCTION | p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_manager_emp_id NUMBER DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_employment_type VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary NUMBER DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER |
| update_employee | PROCEDURE | p_emp_id NUMBER, p_first_name VARCHAR2 DEFAULT NULL, p_last_name VARCHAR2 DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_phone_work VARCHAR2 DEFAULT NULL, p_phone_mobile VARCHAR2 DEFAULT NULL, p_address_line1 VARCHAR2 DEFAULT NULL, p_address_line2 VARCHAR2 DEFAULT NULL, p_city VARCHAR2 DEFAULT NULL, p_state_province VARCHAR2 DEFAULT NULL, p_postal_code VARCHAR2 DEFAULT NULL, p_country_code VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| get_employee | FUNCTION | p_emp_id NUMBER | t_emp_rec |
| get_employee_by_number | FUNCTION | p_emp_number VARCHAR2 | t_emp_rec |
| search_employees | PROCEDURE | p_cursor OUT t_emp_cursor, p_last_name VARCHAR2 DEFAULT NULL, p_first_name VARCHAR2 DEFAULT NULL, p_dept_id NUMBER DEFAULT NULL, p_status VARCHAR2 DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_hire_date_from DATE DEFAULT NULL, p_hire_date_to DATE DEFAULT NULL | — |
| transfer_employee | PROCEDURE | p_emp_id NUMBER, p_new_dept_id NUMBER, p_new_job_id NUMBER DEFAULT NULL, p_new_manager_id NUMBER DEFAULT NULL, p_new_location VARCHAR2 DEFAULT NULL, p_effective_date DATE DEFAULT SYSDATE, p_reason_code VARCHAR2 DEFAULT NULL, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| promote_employee | PROCEDURE | p_emp_id NUMBER, p_new_job_id NUMBER, p_new_salary NUMBER, p_effective_date DATE DEFAULT SYSDATE, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| terminate_employee | PROCEDURE | p_emp_id NUMBER, p_termination_date DATE, p_reason VARCHAR2, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| rehire_employee | PROCEDURE | p_emp_id NUMBER, p_rehire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_base_salary NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_direct_reports | FUNCTION | p_manager_emp_id NUMBER | t_emp_id_table |
| get_org_chart | FUNCTION | p_root_emp_id NUMBER, p_max_depth NUMBER DEFAULT 10 | t_emp_cursor |
| get_headcount_by_dept | FUNCTION | p_dept_id NUMBER DEFAULT NULL, p_as_of_date DATE DEFAULT SYSDATE | NUMBER |
| get_tenure_years | FUNCTION | p_emp_id NUMBER | NUMBER |
| is_active | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| validate_employee | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| emp_exists | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| generate_emp_number | FUNCTION | (none) | VARCHAR2 |
| set_session_context | PROCEDURE | p_user VARCHAR2, p_emp_id NUMBER | — |

---

**Dependencies declared in header comments:**
- PKG_COMMON
- PKG_AUDIT
- PKG_NOTIFICATION
- PKG_PAYROLL

**Called by (per header):**
- HRMS_EMPLOYEE form
- HRMS_DEPARTMENT form
- Batch jobs

**Known issues (per header):**
- Circular dependency with PKG_PAYROLL (salary validation)
- get_org_chart uses recursive SQL that times out for deep hierarchies

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb ===

**Package:** HRMS.PKG_EMPLOYEE
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value |
|---|---|---|
| c_emp_number_prefix | VARCHAR2(3) | 'EMP' |
| c_max_hierarchy_depth | NUMBER | 15 |

---

**Private Forward Declarations:**
- PROCEDURE log_history (full signature below)
- PROCEDURE validate_dept(p_dept_id IN NUMBER)
- PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)
- FUNCTION get_next_emp_id RETURN NUMBER

---

### FUNCTION generate_emp_number RETURN VARCHAR2

**Logic:**
1. SELECT NVL(MAX(TO_NUMBER(SUBSTR(EMP_NUMBER, 5))), 0) + 1 INTO v_max_num FROM EMPLOYEES WHERE EMP_NUMBER LIKE c_emp_number_prefix || '-%' (i.e., LIKE 'EMP-%')
2. Construct: v_new_number := 'EMP' || '-' || LPAD(v_max_num, 6, '0')  — zero-padded to 6 digits, format EMP-NNNNNN
3. Return v_new_number
4. EXCEPTION WHEN OTHERS: fallback — RETURN 'EMP-' || LPAD(SEQ_EMPLOYEE.NEXTVAL, 6, '0')

**Known bug:** Race condition under concurrent inserts — no SELECT FOR UPDATE.

**Database tables accessed:** EMPLOYEES (read)
**Sequences used:** SEQ_EMPLOYEE (in exception fallback)

---

### FUNCTION get_next_emp_id RETURN NUMBER

**Logic:**
1. SELECT SEQ_EMPLOYEE.NEXTVAL INTO v_id FROM DUAL
2. RETURN v_id

**Sequences used:** SEQ_EMPLOYEE

---

### PROCEDURE validate_dept(p_dept_id IN NUMBER)

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id AND ACTIVE_FLAG = 'Y'
2. IF v_count = 0 THEN RAISE_APPLICATION_ERROR(-20003, 'Invalid or inactive department: ' || p_dept_id)

**Business rules:**
- Department must exist in DEPARTMENTS table with ACTIVE_FLAG = 'Y'

**Exceptions thrown:**
- -20003 'Invalid or inactive department: [id]' — department not found or ACTIVE_FLAG != 'Y'

**Database tables accessed:** DEPARTMENTS (read)

---

### PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)

**Logic:**
1. IF p_manager_id IS NULL THEN RETURN — NULL manager is valid (top-level employee)
2. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE EMP_ID = p_manager_id AND EMPLOYMENT_STATUS = 'ACTIVE'
3. IF v_count = 0 THEN RAISE_APPLICATION_ERROR(-20004, 'Invalid or inactive manager: ' || p_manager_id)
4. Circular reporting check (only when p_emp_id IS NOT NULL):
   - v_current_mgr := p_manager_id, v_depth := 0
   - WHILE v_current_mgr IS NOT NULL AND v_depth < 15 LOOP
     - IF v_current_mgr = p_emp_id THEN RAISE_APPLICATION_ERROR(-20004, 'Circular reporting chain detected: Employee [p_emp_id] cannot report to [p_manager_id]')
     - SELECT MANAGER_EMP_ID INTO v_current_mgr FROM EMPLOYEES WHERE EMP_ID = v_current_mgr; EXCEPTION WHEN NO_DATA_FOUND THEN v_current_mgr := NULL
     - v_depth := v_depth + 1
   - End loop at depth 15 (c_max_hierarchy_depth)

**Business rules:**
- Manager must exist in EMPLOYEES with EMPLOYMENT_STATUS = 'ACTIVE'
- Circular reporting chains are forbidden; checked up to depth 15

**Exceptions thrown:**
- -20004 'Invalid or inactive manager: [id]'
- -20004 'Circular reporting chain detected: Employee [id] cannot report to [id]'

**Database tables accessed:** EMPLOYEES (read — two separate queries)

---

### PROCEDURE log_history (PRAGMA AUTONOMOUS_TRANSACTION)

**Signature:**
```
p_emp_id        IN NUMBER,
p_change_type   IN VARCHAR2,
p_effective_date IN DATE,
p_old_dept_id   IN NUMBER DEFAULT NULL,
p_new_dept_id   IN NUMBER DEFAULT NULL,
p_old_job_id    IN NUMBER DEFAULT NULL,
p_new_job_id    IN NUMBER DEFAULT NULL,
p_old_manager   IN NUMBER DEFAULT NULL,
p_new_manager   IN NUMBER DEFAULT NULL,
p_old_salary    IN NUMBER DEFAULT NULL,
p_new_salary    IN NUMBER DEFAULT NULL,
p_old_location  IN VARCHAR2 DEFAULT NULL,
p_new_location  IN VARCHAR2 DEFAULT NULL,
p_reason_code   IN VARCHAR2 DEFAULT NULL,
p_comments      IN VARCHAR2 DEFAULT NULL,
p_user          IN VARCHAR2 DEFAULT USER
```

**Logic:**
1. INSERT INTO EMPLOYEE_HISTORY (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE) VALUES (SEQ_EMP_HISTORY.NEXTVAL, ...)
2. COMMIT
3. EXCEPTION WHEN OTHERS: ROLLBACK; IF g_debug_mode THEN print warning; END IF — history logging never fails the main transaction

**PRAGMA:** AUTONOMOUS_TRANSACTION — runs in its own transaction, independent of caller

**Sequences used:** SEQ_EMP_HISTORY

**Database tables written:** EMPLOYEE_HISTORY

---

### FUNCTION create_employee(...) RETURN NUMBER

**Full parameter list:**
- p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_manager_emp_id NUMBER DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_employment_type VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary NUMBER DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic (step by step):**
1. Validate: IF p_first_name IS NULL OR p_last_name IS NULL THEN RAISE_APPLICATION_ERROR(-20010, 'First name and last name are required')
2. Call validate_dept(p_dept_id)
3. Call validate_manager(p_manager_emp_id) — NULL is allowed
4. Validate job: SELECT GRADE_ID INTO v_grade_id FROM JOB_TITLES WHERE JOB_ID = p_job_id AND ACTIVE_FLAG = 'Y'; EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20011, 'Invalid or inactive job: ' || p_job_id)
5. Validate salary vs grade range (soft warning only, not an error):
   - IF p_base_salary IS NOT NULL THEN
     - SELECT MIN_SALARY, MAX_SALARY INTO v_min, v_max FROM JOB_GRADES WHERE GRADE_ID = v_grade_id
     - IF p_base_salary < v_min OR p_base_salary > v_max THEN IF g_debug_mode THEN print warning (no error raised — soft check, override allowed with manager approval)
6. Determine location: IF p_location_code IS NULL THEN SELECT LOCATION_CODE INTO v_location FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id; ELSE v_location := p_location_code
7. v_emp_id := get_next_emp_id()
8. v_emp_number := generate_emp_number()
9. INSERT INTO EMPLOYEES: EMP_ID=v_emp_id, EMP_NUMBER=v_emp_number, FIRST_NAME=UPPER(TRIM(p_first_name)), LAST_NAME=UPPER(TRIM(p_last_name)), HIRE_DATE=p_hire_date, DEPT_ID=p_dept_id, JOB_ID=p_job_id, MANAGER_EMP_ID=p_manager_emp_id, LOCATION_CODE=v_location, EMPLOYMENT_TYPE=p_employment_type, EMPLOYMENT_STATUS='ACTIVE', EMAIL=LOWER(TRIM(p_email)), ACTIVE_FLAG='Y', CREATED_BY=p_user, CREATED_DATE=SYSDATE
10. IF p_base_salary IS NOT NULL THEN call PKG_PAYROLL.create_salary_record(p_emp_id=>v_emp_id, p_effective_date=>p_hire_date, p_base_salary=>p_base_salary, p_change_reason=>'NEW_HIRE', p_user=>p_user)
11. Call log_history(p_emp_id=>v_emp_id, p_change_type=>'HIRE', p_effective_date=>p_hire_date, p_new_dept_id, p_new_job_id, p_new_manager, p_new_salary, p_new_location, p_user)
12. Call PKG_AUDIT.log_action(p_table_name=>'EMPLOYEES', p_record_id=>v_emp_id, p_action=>'INSERT', p_user=>p_user)
13. Call PKG_NOTIFICATION.send_notification(p_recipient_emp_id=>v_emp_id, p_type=>'EMAIL', p_subject=>'Welcome to the Company', p_body=>'Dear [first_name], Welcome aboard! Your employee number is [emp_number].', p_user=>p_user)
14. IF p_manager_emp_id IS NOT NULL THEN call PKG_NOTIFICATION.send_notification to manager with subject='New Direct Report: [first] [last]', body='[first] [last] has been added as your direct report, starting [hire_date MM/DD/YYYY].'
15. RETURN v_emp_id
16. EXCEPTION WHEN DUP_VAL_ON_INDEX THEN RAISE_APPLICATION_ERROR(-20002, 'Duplicate employee number generated. Please retry.')
17. EXCEPTION WHEN OTHERS THEN call PKG_COMMON.log_error('PKG_EMPLOYEE','create_employee',SQLERRM,p_user); RAISE

**Business rules:**
- First name and last name are required (not null)
- Department must be valid and active
- Manager (if provided) must be active; no circular chains
- Job must be active in JOB_TITLES
- Salary range check is a soft warning only; override is allowed with manager approval
- First name and last name stored as UPPER(TRIM(...))
- Email stored as LOWER(TRIM(...))
- Default EMPLOYMENT_TYPE = 'FULL_TIME'
- Default EMPLOYMENT_STATUS = 'ACTIVE' on creation
- Default ACTIVE_FLAG = 'Y' on creation
- Location defaults from department if not specified

**Exceptions thrown:**
- -20010 'First name and last name are required'
- -20003 (from validate_dept)
- -20004 (from validate_manager)
- -20011 'Invalid or inactive job: [id]'
- -20002 'Duplicate employee number generated. Please retry.'

**External services called:**
- PKG_PAYROLL.create_salary_record (if salary provided)
- PKG_AUDIT.log_action
- PKG_NOTIFICATION.send_notification (to employee and, conditionally, to manager)
- PKG_COMMON.log_error (on error)

**Sequences used:** SEQ_EMPLOYEE (via get_next_emp_id, generate_emp_number)

**Database tables written:** EMPLOYEES

**Known issue:** Circular dependency — calls PKG_PAYROLL.create_salary_record which may call PKG_EMPLOYEE.is_active for validation.

---

### PROCEDURE update_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_first_name VARCHAR2 DEFAULT NULL, p_last_name VARCHAR2 DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_phone_work VARCHAR2 DEFAULT NULL, p_phone_mobile VARCHAR2 DEFAULT NULL, p_address_line1 VARCHAR2 DEFAULT NULL, p_address_line2 VARCHAR2 DEFAULT NULL, p_city VARCHAR2 DEFAULT NULL, p_state_province VARCHAR2 DEFAULT NULL, p_postal_code VARCHAR2 DEFAULT NULL, p_country_code VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. IF NOT emp_exists(p_emp_id) THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)
2. UPDATE EMPLOYEES SET FIRST_NAME=NVL(UPPER(TRIM(p_first_name)),FIRST_NAME), LAST_NAME=NVL(UPPER(TRIM(p_last_name)),LAST_NAME), EMAIL=NVL(LOWER(TRIM(p_email)),EMAIL), PHONE_WORK=NVL(p_phone_work,PHONE_WORK), PHONE_MOBILE=NVL(p_phone_mobile,PHONE_MOBILE), ADDRESS_LINE1=NVL(p_address_line1,ADDRESS_LINE1), ADDRESS_LINE2=NVL(p_address_line2,ADDRESS_LINE2), CITY=NVL(p_city,CITY), STATE_PROVINCE=NVL(p_state_province,STATE_PROVINCE), POSTAL_CODE=NVL(p_postal_code,POSTAL_CODE), COUNTRY_CODE=NVL(p_country_code,COUNTRY_CODE), MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
3. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20001, 'Employee update failed: ' || p_emp_id)
4. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

**Business rules:**
- Partial update pattern — only non-NULL parameters overwrite existing values (NVL pattern)
- FIRST_NAME and LAST_NAME stored as UPPER(TRIM(...))
- EMAIL stored as LOWER(TRIM(...))
- Employee must exist

**Exceptions thrown:**
- -20001 'Employee not found: [id]'
- -20001 'Employee update failed: [id]'

**Database tables written:** EMPLOYEES

---

### FUNCTION get_employee(p_emp_id IN NUMBER) RETURN t_emp_rec

**Logic:**
1. SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, e.JOB_ID, e.MANAGER_EMP_ID, e.EMPLOYMENT_STATUS, (subquery for BASE_SALARY) INTO v_rec FROM EMPLOYEES e WHERE e.EMP_ID = p_emp_id
2. Subquery for BASE_SALARY: SELECT sr.BASE_SALARY FROM SALARY_RECORDS sr WHERE sr.EMP_ID = e.EMP_ID AND sr.ACTIVE_FLAG = 'Y' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE) AND ROWNUM = 1
3. RETURN v_rec
4. EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)

**Business rules:**
- Current salary = SALARY_RECORDS where ACTIVE_FLAG='Y' AND EFFECTIVE_DATE <= SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE), first row only (ROWNUM=1, no ORDER BY — non-deterministic if multiple rows)

**Exceptions thrown:**
- -20001 'Employee not found: [id]'

**Database tables accessed:** EMPLOYEES, SALARY_RECORDS

---

### FUNCTION get_employee_by_number(p_emp_number IN VARCHAR2) RETURN t_emp_rec

**Logic:**
1. SELECT EMP_ID INTO v_emp_id FROM EMPLOYEES WHERE EMP_NUMBER = p_emp_number
2. RETURN get_employee(v_emp_id)
3. EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_number)

**Database tables accessed:** EMPLOYEES

---

### PROCEDURE search_employees(...)

**Full parameter list:**
- p_cursor OUT t_emp_cursor, p_last_name VARCHAR2 DEFAULT NULL, p_first_name VARCHAR2 DEFAULT NULL, p_dept_id NUMBER DEFAULT NULL, p_status VARCHAR2 DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_hire_date_from DATE DEFAULT NULL, p_hire_date_to DATE DEFAULT NULL

**Logic — dynamic SQL construction:**
1. Base query:
   ```
   SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, d.DEPT_NAME, j.JOB_TITLE, e.EMPLOYMENT_STATUS, e.LOCATION_CODE
   FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE 1=1
   ```
2. IF p_last_name IS NOT NULL: append `AND UPPER(e.LAST_NAME) LIKE UPPER('` || p_last_name || `%')`
3. IF p_first_name IS NOT NULL: append `AND UPPER(e.FIRST_NAME) LIKE UPPER('` || p_first_name || `%')`
4. IF p_dept_id IS NOT NULL: append `AND e.DEPT_ID = ` || p_dept_id
5. IF p_status IS NOT NULL: append `AND e.EMPLOYMENT_STATUS = '` || p_status || `'`
6. IF p_location_code IS NOT NULL: append `AND e.LOCATION_CODE = '` || p_location_code || `'`
7. IF p_hire_date_from IS NOT NULL: append `AND e.HIRE_DATE >= TO_DATE('` || TO_CHAR(p_hire_date_from,'YYYY-MM-DD') || `','YYYY-MM-DD')`
8. IF p_hire_date_to IS NOT NULL: append `AND e.HIRE_DATE <= TO_DATE('` || TO_CHAR(p_hire_date_to,'YYYY-MM-DD') || `','YYYY-MM-DD')`
9. Append `ORDER BY e.LAST_NAME, e.FIRST_NAME`
10. OPEN p_cursor FOR v_sql (dynamic)

**SECURITY VULNERABILITY:** String concatenation for p_last_name and p_first_name instead of bind variables — SQL injection possible via those parameters. Note in code: "Forms LOV passes validated values, but direct calls are vulnerable."

**Database tables accessed:** EMPLOYEES, DEPARTMENTS, JOB_TITLES

---

### PROCEDURE transfer_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_new_dept_id NUMBER, p_new_job_id NUMBER DEFAULT NULL, p_new_manager_id NUMBER DEFAULT NULL, p_new_location VARCHAR2 DEFAULT NULL, p_effective_date DATE DEFAULT SYSDATE, p_reason_code VARCHAR2 DEFAULT NULL, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT * INTO v_old_rec FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE NOWAIT
2. IF v_old_rec.EMPLOYMENT_STATUS != 'ACTIVE' THEN RAISE_APPLICATION_ERROR(-20012, 'Cannot transfer non-active employee. Status: ' || v_old_rec.EMPLOYMENT_STATUS)
3. Call validate_dept(p_new_dept_id)
4. v_new_job_id := NVL(p_new_job_id, v_old_rec.JOB_ID) — defaults to current job if not provided
5. v_new_location := NVL(p_new_location, v_old_rec.LOCATION_CODE) — defaults to current location
6. IF p_new_manager_id IS NOT NULL THEN call validate_manager(p_new_manager_id, p_emp_id) — circular check included
7. UPDATE EMPLOYEES SET DEPT_ID=p_new_dept_id, JOB_ID=v_new_job_id, MANAGER_EMP_ID=NVL(p_new_manager_id, MANAGER_EMP_ID), LOCATION_CODE=v_new_location, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
8. Call log_history with CHANGE_TYPE='TRANSFER', old and new values for dept, job, manager, location
9. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error('PKG_EMPLOYEE','transfer_employee',SQLERRM,p_user); RAISE

**Business rules:**
- Only ACTIVE employees can be transferred
- Row-level locking with NOWAIT (fails immediately if locked)
- Job defaults to current if not specified
- Location defaults to current if not specified
- Manager validation (including circular chain check) only if new manager explicitly provided

**Exceptions thrown:**
- -20012 'Cannot transfer non-active employee. Status: [status]'
- -20003 (from validate_dept)
- -20004 (from validate_manager)

**Database tables accessed/written:** EMPLOYEES (lock + update), EMPLOYEE_HISTORY (via log_history)

---

### PROCEDURE promote_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_new_job_id NUMBER, p_new_salary NUMBER, p_effective_date DATE DEFAULT SYSDATE, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT JOB_ID INTO v_old_job_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. Get current salary: SELECT BASE_SALARY INTO v_old_salary FROM SALARY_RECORDS WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' AND ROWNUM=1 ORDER BY EFFECTIVE_DATE DESC; EXCEPTION WHEN NO_DATA_FOUND THEN v_old_salary := 0
3. UPDATE EMPLOYEES SET JOB_ID=p_new_job_id, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
4. Call PKG_PAYROLL.create_salary_record(p_emp_id, p_effective_date, p_new_salary, 'PROMOTION', p_change_pct=CASE WHEN v_old_salary > 0 THEN ROUND(((p_new_salary - v_old_salary) / v_old_salary) * 100, 2) ELSE NULL END, p_user)
5. Call log_history with CHANGE_TYPE='PROMOTION', old/new job_id, old/new salary
6. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

**Business rules:**
- Salary change percentage calculated as ROUND(((new - old) / old) * 100, 2) — only when old > 0
- No active-status check before promotion (contrast with transfer_employee)

**External services called:** PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action

**Database tables accessed/written:** EMPLOYEES (read + update), SALARY_RECORDS (read)

---

### PROCEDURE terminate_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_termination_date DATE, p_reason VARCHAR2, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE
2. IF v_emp.EMPLOYMENT_STATUS = 'TERMINATED' THEN RAISE_APPLICATION_ERROR(-20005, 'Employee [id] is already terminated')
3. SELECT COUNT(*) INTO v_pending_leave FROM LEAVE_REQUESTS WHERE EMP_ID=p_emp_id AND STATUS='PENDING'
4. IF v_pending_leave > 0 THEN UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON='Auto-cancelled due to termination', CANCELLED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND STATUS='PENDING'
5. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='TERMINATED', TERMINATION_DATE=p_termination_date, TERMINATION_REASON=p_reason, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
6. UPDATE SALARY_RECORDS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
7. UPDATE EMPLOYEE_PAY_ELEMENTS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
8. Call log_history with CHANGE_TYPE='TERMINATION'
9. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. IF v_emp.MANAGER_EMP_ID IS NOT NULL THEN call PKG_NOTIFICATION.send_notification to manager with subject='Employee Termination: [first] [last]', body='[first] [last] termination effective [date MM/DD/YYYY]'
11. TODOs noted: integrate with benefits system for COBRA, revoke system access via PKG_SECURITY, calculate final pay via PKG_PAYROLL.calculate_final_pay
12. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error; RAISE

**Business rules:**
- Cannot terminate an already-TERMINATED employee
- All PENDING leave requests are auto-cancelled with reason 'Auto-cancelled due to termination'
- All active salary records end-dated to p_termination_date
- All active pay elements end-dated to p_termination_date
- ACTIVE_FLAG set to 'N'
- Manager notified via email

**Exceptions thrown:**
- -20005 'Employee [id] is already terminated'

**Incomplete integrations (TODOs):**
- Benefits/COBRA
- PKG_SECURITY access revocation
- PKG_PAYROLL.calculate_final_pay

**Database tables accessed/written:** EMPLOYEES, LEAVE_REQUESTS, SALARY_RECORDS, EMPLOYEE_PAY_ELEMENTS, EMPLOYEE_HISTORY

---

### PROCEDURE rehire_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_rehire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_base_salary NUMBER, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. Call validate_dept(p_dept_id)
2. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='ACTIVE', HIRE_DATE=p_rehire_date, TERMINATION_DATE=NULL, TERMINATION_REASON=NULL, DEPT_ID=p_dept_id, JOB_ID=p_job_id, ACTIVE_FLAG='Y', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
3. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found for rehire: ' || p_emp_id)
4. Call PKG_PAYROLL.create_salary_record(p_emp_id, p_rehire_date, p_base_salary, 'REHIRE', p_user)
5. Call log_history with CHANGE_TYPE='REHIRE', new dept, job, salary
6. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

**Business rules:**
- HIRE_DATE is overwritten with p_rehire_date on rehire
- TERMINATION_DATE and TERMINATION_REASON are cleared (set to NULL)
- Department must be valid and active

**Exceptions thrown:**
- -20001 'Employee not found for rehire: [id]'
- -20003 (from validate_dept)

---

### FUNCTION get_direct_reports(p_manager_emp_id IN NUMBER) RETURN t_emp_id_table

**Logic:**
1. Initialize v_result (t_emp_id_table), v_idx := 0
2. FOR r IN (SELECT EMP_ID FROM EMPLOYEES WHERE MANAGER_EMP_ID = p_manager_emp_id AND EMPLOYMENT_STATUS = 'ACTIVE' ORDER BY LAST_NAME, FIRST_NAME) LOOP
   - v_idx := v_idx + 1; v_result(v_idx) := r.EMP_ID
3. RETURN v_result

**Business rules:**
- Only ACTIVE employees returned

**Database tables accessed:** EMPLOYEES

---

### FUNCTION get_org_chart(p_root_emp_id IN NUMBER, p_max_depth IN NUMBER DEFAULT 10) RETURN t_emp_cursor

**Logic:**
1. OPEN v_cursor FOR hierarchical query:
   ```
   SELECT LEVEL AS depth, EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID, JOB_ID, MANAGER_EMP_ID
   FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE'
   START WITH EMP_ID = p_root_emp_id
   CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID AND LEVEL <= p_max_depth
   ORDER SIBLINGS BY LAST_NAME, FIRST_NAME
   ```
2. RETURN v_cursor

**Business rules:**
- Only ACTIVE employees included
- Default max depth = 10
- Absolute max enforced via CONNECT BY condition

**Known bug:** Times out for orgs with >500 employees.

---

### FUNCTION get_headcount_by_dept(p_dept_id IN NUMBER DEFAULT NULL, p_as_of_date IN DATE DEFAULT SYSDATE) RETURN NUMBER

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE (p_dept_id IS NULL OR DEPT_ID = p_dept_id) AND EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= p_as_of_date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)
2. RETURN v_count

**Business rules:**
- If p_dept_id is NULL, counts all departments
- Excludes future hires (HIRE_DATE > as_of_date) and terminated employees whose termination date <= as_of_date

---

### FUNCTION get_tenure_years(p_emp_id IN NUMBER) RETURN NUMBER

**Logic:**
1. SELECT HIRE_DATE, NVL(TERMINATION_DATE, SYSDATE) INTO v_hire_date, v_end_date FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN ROUND(MONTHS_BETWEEN(v_end_date, v_hire_date) / 12, 1)
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN NULL

**Business rules:**
- Tenure calculated in years, rounded to 1 decimal place
- For active employees, end date is SYSDATE; for terminated, uses TERMINATION_DATE

---

### FUNCTION is_active(p_emp_id IN NUMBER) RETURN BOOLEAN

**Logic:**
1. SELECT EMPLOYMENT_STATUS INTO v_status FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_status = 'ACTIVE'
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN FALSE

---

### FUNCTION validate_employee(p_emp_id IN NUMBER) RETURN BOOLEAN

**Logic:**
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. IF v_emp.FIRST_NAME IS NULL OR v_emp.LAST_NAME IS NULL THEN RETURN FALSE
3. IF v_emp.HIRE_DATE IS NULL THEN RETURN FALSE
4. IF v_emp.EMPLOYMENT_STATUS = 'ACTIVE' AND v_emp.ACTIVE_FLAG != 'Y' THEN RETURN FALSE
5. RETURN TRUE
6. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN FALSE

**Business rules:**
- Valid employee: first name not null, last name not null, hire date not null
- If EMPLOYMENT_STATUS is 'ACTIVE', ACTIVE_FLAG must also be 'Y' (consistency check)

---

### FUNCTION emp_exists(p_emp_id IN NUMBER) RETURN BOOLEAN

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_count > 0

---

### PROCEDURE set_session_context(p_user IN VARCHAR2, p_emp_id IN NUMBER)

**Logic:**
1. g_current_user := p_user
2. g_current_emp_id := p_emp_id
3. SELECT DEPT_ID INTO g_current_dept_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
4. EXCEPTION WHEN NO_DATA_FOUND THEN g_current_dept_id := NULL

**Side effects:** Sets package-level global variables g_current_user, g_current_emp_id, g_current_dept_id

---

**All database tables referenced in PKG_EMPLOYEE:**

| Table | Operations |
|---|---|
| EMPLOYEES | SELECT, INSERT, UPDATE |
| DEPARTMENTS | SELECT |
| JOB_TITLES | SELECT |
| JOB_GRADES | SELECT |
| SALARY_RECORDS | SELECT |
| EMPLOYEE_HISTORY | INSERT (via log_history) |
| LEAVE_REQUESTS | SELECT, UPDATE |
| EMPLOYEE_PAY_ELEMENTS | UPDATE |

**All sequences used:**
- SEQ_EMPLOYEE
- SEQ_EMP_HISTORY

**All external packages called:**
- PKG_PAYROLL.create_salary_record
- PKG_AUDIT.log_action
- PKG_NOTIFICATION.send_notification
- PKG_COMMON.log_error

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks ===

**Package:** HRMS.PKG_INTEGRATION
**Schema:** HRMS
**Type:** Package Specification

---

**Type Definitions:**

`TYPE t_gl_entry IS RECORD`:
- journal_date — DATE
- account_code — VARCHAR2(30)
- debit_amount — NUMBER(15,2)
- credit_amount — NUMBER(15,2)
- description — VARCHAR2(200)
- reference — VARCHAR2(100)

`TYPE t_gl_entry_table IS TABLE OF t_gl_entry INDEX BY BINARY_INTEGER`

---

**Public Procedure/Function Signatures:**

| Name | Kind | Parameters |
|---|---|---|
| generate_gl_journal | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER |
| export_benefits_feed | PROCEDURE | p_effective_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER |
| import_time_attendance | PROCEDURE | p_file_name VARCHAR2, p_user VARCHAR2 DEFAULT USER |
| sync_org_structure | PROCEDURE | p_user VARCHAR2 DEFAULT USER |
| get_integration_status | FUNCTION | p_integration_name VARCHAR2 → RETURN VARCHAR2 |

---

**Dependencies (per header):** PKG_COMMON, PKG_PAYROLL, PKG_EMPLOYEE

**Called by (per header):** Batch scheduler (nightly GL feed, weekly benefits sync)

**Known issues (per header):**
- GL posting uses flat file exchange (UTL_FILE) instead of API
- Benefits feed format is vendor-specific (ADP format)
- No retry logic for failed file transfers
- FTP credentials stored in SYSTEM_PARAMETERS table (cleartext) — security vulnerability

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb ===

**Package:** HRMS.PKG_INTEGRATION
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value |
|---|---|---|
| c_gl_output_dir | VARCHAR2(30) | 'GL_FEED_OUT' |
| c_benefits_output_dir | VARCHAR2(30) | 'BENEFITS_FEED_OUT' |
| c_time_input_dir | VARCHAR2(30) | 'TIME_ATTENDANCE_IN' |

These are Oracle directory object names (mapped to OS filesystem paths by DBA).

---

### PROCEDURE generate_gl_journal(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** Creates GL journal entries from payroll run and writes to pipe-delimited flat file consumed by Oracle Financials batch import.

**Logic:**
1. v_filename := 'GL_JOURNAL_' || p_run_id || '_' || TO_CHAR(SYSDATE,'YYYYMMDD') || '.dat'
2. v_file := UTL_FILE.FOPEN(c_gl_output_dir [='GL_FEED_OUT'], v_filename, 'W', 32767) — write mode, max line 32767 chars
3. Write header record: `H|HRMS_PAYROLL|[YYYY-MM-DD]|[run_id]`
4. Cursor loop over aggregated payroll data:
   ```sql
   SELECT d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE,
          SUM(pd.AMOUNT) AS TOTAL_AMOUNT, pp.PERIOD_NAME
   FROM PAYROLL_DETAILS pd
   JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
   JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID
   JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
   JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
   JOIN PAY_ELEMENTS pe ON pd.ELEMENT_ID = pe.ELEMENT_ID
   WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND pe.GL_ACCOUNT_CODE IS NOT NULL
   GROUP BY d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE, pp.PERIOD_NAME
   ```
5. For each row:
   - If ELEMENT_TYPE = 'EARNING': write `D|[COST_CENTER]|[GL_ACCOUNT_CODE]|[ABS(TOTAL_AMOUNT) format FM999999990.00]|0.00|Payroll [PERIOD_NAME]|RUN-[run_id]`
   - Else (deductions/taxes/liability accounts): write `D|[COST_CENTER]|[GL_ACCOUNT_CODE]|0.00|[ABS(TOTAL_AMOUNT) format FM999999990.00]|Payroll [PERIOD_NAME]|RUN-[run_id]`
6. Write trailer record: `T|[v_entries]`
7. UTL_FILE.FCLOSE(v_file)
8. PKG_COMMON.log_info(...)
9. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

**File format (pipe-delimited):**
- Header: `H|HRMS_PAYROLL|YYYY-MM-DD|run_id`
- Detail (earning/debit): `D|cost_center|gl_account|debit_amount|0.00|description|reference`
- Detail (deduction/credit): `D|cost_center|gl_account|0.00|credit_amount|description|reference`
- Trailer: `T|count`

**Business rules:**
- Earnings → debit to expense accounts (debit column populated, credit = 0.00)
- Deductions/taxes → credit to liability accounts (debit = 0.00, credit column populated)
- ERROR rows excluded (pd.STATUS != 'ERROR')
- Only elements with GL_ACCOUNT_CODE assigned are included

**External services:** UTL_FILE (Oracle directory object 'GL_FEED_OUT'), PKG_COMMON

**Database tables accessed:** PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS, EMPLOYEES, DEPARTMENTS, PAY_ELEMENTS

---

### PROCEDURE export_benefits_feed(p_effective_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** ADP-format benefits enrollment file. LEGACY: Fixed-width format, specific to ADP vendor.

**Logic:**
1. v_filename := 'BENEFITS_' || TO_CHAR(SYSDATE,'YYYYMMDD') || '.txt'
2. v_file := UTL_FILE.FOPEN(c_benefits_output_dir [='BENEFITS_FEED_OUT'], v_filename, 'W', 32767)
3. Cursor loop:
   ```sql
   SELECT e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.DATE_OF_BIRTH, e.HIRE_DATE,
          e.EMPLOYMENT_STATUS, e.MARITAL_STATUS, e.GENDER,
          d.FIRST_NAME AS DEP_FIRST_NAME, d.LAST_NAME AS DEP_LAST_NAME,
          d.RELATIONSHIP, d.DATE_OF_BIRTH AS DEP_DOB
   FROM EMPLOYEES e LEFT JOIN EMPLOYEE_DEPENDENTS d ON e.EMP_ID = d.EMP_ID AND d.ACTIVE_FLAG = 'Y'
   WHERE e.EMPLOYMENT_STATUS = 'ACTIVE'
   ORDER BY e.EMP_NUMBER, d.DEPENDENT_ID
   ```
4. For each row, write fixed-width record:

| Field | Width | Source |
|---|---|---|
| EMP_NUMBER | 10 | RPAD |
| FIRST_NAME | 30 | RPAD |
| LAST_NAME | 30 | RPAD |
| DATE_OF_BIRTH | 10 | RPAD(TO_CHAR(...,'YYYY-MM-DD')) |
| HIRE_DATE | 10 | RPAD(TO_CHAR(...,'YYYY-MM-DD')) |
| EMPLOYMENT_STATUS | 12 | RPAD |
| MARITAL_STATUS | 10 | RPAD |
| GENDER | 1 | RPAD |
| DEP_FIRST_NAME | 30 | RPAD |
| DEP_LAST_NAME | 30 | RPAD |
| RELATIONSHIP | 20 | RPAD |
| DEP_DOB | 10 | RPAD(TO_CHAR(...,'YYYY-MM-DD')) |

Total fixed record width: 10+30+30+10+10+12+10+1+30+30+20+10 = 203 characters

5. UTL_FILE.FCLOSE; PKG_COMMON.log_info
6. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

**Business rules:**
- Only ACTIVE employees included
- Dependents joined with LEFT JOIN — employee appears once per dependent (one row per dependent, or one row if no dependents)
- Only active dependents (ACTIVE_FLAG='Y') included
- Null values padded with spaces

**Database tables accessed:** EMPLOYEES, EMPLOYEE_DEPENDENTS

---

### PROCEDURE import_time_attendance(p_file_name IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. v_file := UTL_FILE.FOPEN(c_time_input_dir [='TIME_ATTENDANCE_IN'], p_file_name, 'R', 32767)
2. LOOP:
   - UTL_FILE.GET_LINE(v_file, v_line)
   - If line not null and first character != '#' (skip comment lines)
   - Expected CSV format: emp_number, date, hours_regular, hours_overtime
   - TODO: actual parsing and database update not implemented
   - v_imported := v_imported + 1
   - EXCEPTION WHEN NO_DATA_FOUND THEN EXIT (end of file)
   - EXCEPTION WHEN OTHERS THEN v_errors := v_errors + 1; PKG_COMMON.log_error(...)
3. UTL_FILE.FCLOSE; PKG_COMMON.log_info

**Known limitation:** Actual CSV parsing and database update is a TODO — not implemented.

**File format (CSV):** emp_number, date, hours_regular, hours_overtime
**Comment prefix:** Lines beginning with '#' are skipped

---

### PROCEDURE sync_org_structure(p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
- Placeholder only — calls PKG_COMMON.log_info('Org structure sync completed')
- Intended for LDAP/AD sync but not implemented

---

### FUNCTION get_integration_status(p_integration_name IN VARCHAR2) RETURN VARCHAR2

**Logic:**
1. RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS')

**Configuration key pattern:** 'INTEGRATION', '[integration_name]_STATUS' — stored in SYSTEM_PARAMETERS (via PKG_COMMON.get_param)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks ===

**Package:** HRMS.PKG_LEAVE
**Schema:** HRMS
**Type:** Package Specification

---

**Custom Exceptions:**

| Name | Code |
|---|---|
| e_insufficient_balance | -20201 |
| e_overlapping_leave | -20202 |
| e_invalid_leave_type | -20203 |
| e_approval_error | -20204 |

`TYPE t_leave_cursor IS REF CURSOR`

---

**Public Signatures:**

| Name | Kind | Parameters | Returns |
|---|---|---|---|
| submit_leave_request | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_half_day_flag CHAR DEFAULT 'N', p_half_day_period VARCHAR2 DEFAULT NULL, p_reason VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER |
| approve_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| reject_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| cancel_leave_request | PROCEDURE | p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| get_leave_balance | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| adjust_leave_balance | PROCEDURE | p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| initialize_balances | PROCEDURE | p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| run_monthly_accrual | PROCEDURE | p_accrual_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER | — |
| process_carryover | PROCEDURE | p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| expire_carryover | PROCEDURE | p_user VARCHAR2 DEFAULT USER | — |
| get_pending_requests | PROCEDURE | p_cursor OUT t_leave_cursor, p_approver_id NUMBER | — |
| get_team_calendar | PROCEDURE | p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE | — |
| calculate_business_days | FUNCTION | p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL | NUMBER |
| check_leave_overlap | FUNCTION | p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL | BOOLEAN |

---

**Dependencies (per header):** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION

**Called by (per header):** HRMS_LEAVE form, self-service portal, batch accrual job

**Known issues:**
- Overlapping leave detection does not account for half-day requests
- Carryover expiry job sometimes double-expires if run twice on same day
- Holiday detection only checks exact date match, not observed dates

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb ===

**Package:** HRMS.PKG_LEAVE
**Schema:** HRMS
**Type:** Package Body

---

### FUNCTION calculate_business_days(p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL) RETURN NUMBER

**Logic:**
1. v_count := 0; v_date := TRUNC(p_start_date)
2. WHILE v_date <= TRUNC(p_end_date) LOOP:
   - IF TO_CHAR(v_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN') NOT IN ('SAT','SUN') THEN (skip weekends)
     - SELECT COUNT(*) INTO v_holiday_count FROM HOLIDAYS WHERE HOLIDAY_DATE = v_date AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)
     - IF v_holiday_count = 0 THEN v_count := v_count + 1
   - v_date := v_date + 1
3. RETURN v_count

**Business rules:**
- Weekends (Saturday, Sunday) are not business days
- Holidays from HOLIDAYS table (where ACTIVE_FLAG='Y') are excluded
- Holiday can be global (LOCATION_CODE IS NULL) or location-specific
- Date language for day-of-week check is always AMERICAN

**Known bug:** Does not handle "observed" holidays (e.g., if July 4 falls Saturday, observed Friday not excluded).

**Database tables accessed:** HOLIDAYS

---

### FUNCTION check_leave_overlap(p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL) RETURN BOOLEAN

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM LEAVE_REQUESTS WHERE EMP_ID=p_emp_id AND STATUS IN ('PENDING','APPROVED') AND (p_exclude_request_id IS NULL OR REQUEST_ID != p_exclude_request_id) AND START_DATE <= p_end_date AND END_DATE >= p_start_date
2. RETURN v_count > 0

**Business rules:**
- Overlap exists if any PENDING or APPROVED request for same employee spans any part of requested date range
- Excludes a specific request_id (used when updating an existing request)

**Known limitation:** Does not account for half-day requests (per .pks known issues)

---

### FUNCTION submit_leave_request(...) RETURN NUMBER

**Full parameter list:**
- p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_half_day_flag CHAR DEFAULT 'N', p_half_day_period VARCHAR2 DEFAULT NULL, p_reason VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT * INTO v_emp_rec FROM EMPLOYEES WHERE EMP_ID=p_emp_id AND EMPLOYMENT_STATUS='ACTIVE'; EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found or not active: ' || p_emp_id)
2. SELECT * INTO v_leave_type FROM LEAVE_TYPES WHERE LEAVE_TYPE_ID=p_leave_type_id AND ACTIVE_FLAG='Y'; EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20203, 'Invalid leave type: ' || p_leave_type_id)
3. Minimum tenure check: IF v_leave_type.MIN_TENURE_DAYS > 0 AND SYSDATE - v_emp_rec.HIRE_DATE < v_leave_type.MIN_TENURE_DAYS THEN RAISE_APPLICATION_ERROR(-20203, 'Minimum tenure of [N] days not met for leave type: [name]')
4. IF p_start_date > p_end_date THEN RAISE_APPLICATION_ERROR(-20210, 'Start date must be before or equal to end date')
5. Backdating check: IF p_start_date < TRUNC(SYSDATE) AND TRUNC(SYSDATE) - p_start_date > 5 THEN RAISE_APPLICATION_ERROR(-20211, 'Cannot submit leave requests more than 5 days in the past')
6. Calculate total days:
   - IF p_half_day_flag = 'Y' THEN v_total_days := 0.5
   - ELSE v_total_days := calculate_business_days(p_start_date, p_end_date, v_emp_rec.LOCATION_CODE)
7. IF v_total_days <= 0 THEN RAISE_APPLICATION_ERROR(-20212, 'No business days in the selected range')
8. IF check_leave_overlap(p_emp_id, p_start_date, p_end_date) THEN RAISE_APPLICATION_ERROR(-20202, 'Leave request overlaps with an existing request')
9. Balance check (accrual-based types only): IF v_leave_type.ACCRUAL_FLAG = 'Y' THEN v_balance := get_leave_balance(p_emp_id, p_leave_type_id); IF v_balance < v_total_days THEN RAISE_APPLICATION_ERROR(-20201, 'Insufficient leave balance. Available: [n], Requested: [n]')
10. SELECT SEQ_LEAVE_REQUEST.NEXTVAL INTO v_request_id FROM DUAL
11. v_manager_id := v_emp_rec.MANAGER_EMP_ID
12. INSERT INTO LEAVE_REQUESTS: (REQUEST_ID, EMP_ID, LEAVE_TYPE_ID, START_DATE, END_DATE, TOTAL_DAYS, HALF_DAY_FLAG, HALF_DAY_PERIOD, STATUS, REASON, APPROVER_EMP_ID, CREATED_BY, CREATED_DATE) VALUES (..., STATUS = CASE WHEN v_leave_type.REQUIRES_APPROVAL = 'Y' THEN 'PENDING' ELSE 'APPROVED' END, ...)
13. UPDATE LEAVE_BALANCES SET PENDING = PENDING + v_total_days WHERE EMP_ID=p_emp_id AND LEAVE_TYPE_ID=p_leave_type_id AND CALENDAR_YEAR = EXTRACT(YEAR FROM p_start_date)
14. IF v_manager_id IS NOT NULL AND v_leave_type.REQUIRES_APPROVAL = 'Y' THEN send notification to manager: subject='Leave Request Pending Approval', body='[name] has requested [n] day(s) of [type] from [start MM/DD/YYYY] to [end MM/DD/YYYY].'
15. IF v_leave_type.REQUIRES_APPROVAL = 'N' THEN call approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user)
16. PKG_AUDIT.log_action('LEAVE_REQUESTS', v_request_id, 'INSERT', p_user)
17. RETURN v_request_id

**Business rules:**
- Employee must be ACTIVE
- Leave type must be active (ACTIVE_FLAG='Y')
- Minimum tenure enforced per leave type (MIN_TENURE_DAYS, in days since hire)
- Start date must be <= end date
- Backdating allowed up to **5 days** in the past; more than 5 days back is rejected
- Half-day = exactly 0.5 days (independent of business day calculation)
- At least 1 business day must be in the range
- Overlapping PENDING or APPROVED requests are blocked
- Balance checked only for ACCRUAL_FLAG='Y' leave types
- Auto-approve immediately if REQUIRES_APPROVAL='N'
- PENDING balance incremented at submission time

**Numeric literals:**
- 0.5 — half-day value
- 5 — maximum days in the past for backdated submission

**Exceptions thrown:**
- -20001 'Employee not found or not active: [id]'
- -20203 'Invalid leave type: [id]'
- -20203 'Minimum tenure of [N] days not met for leave type: [name]'
- -20210 'Start date must be before or equal to end date'
- -20211 'Cannot submit leave requests more than 5 days in the past'
- -20212 'No business days in the selected range'
- -20202 'Leave request overlaps with an existing request'
- -20201 'Insufficient leave balance. Available: [n], Requested: [n]'

**Sequences:** SEQ_LEAVE_REQUEST

**Database tables accessed/written:** EMPLOYEES (read), LEAVE_TYPES (read), LEAVE_REQUESTS (insert), LEAVE_BALANCES (update)

---

### PROCEDURE approve_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID=p_request_id FOR UPDATE
2. IF v_request.STATUS != 'PENDING' THEN RAISE_APPLICATION_ERROR(-20204, 'Cannot approve request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='APPROVED', APPROVER_EMP_ID=p_approver_emp_id, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS=p_comments, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE REQUEST_ID=p_request_id
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS, USED = USED + v_request.TOTAL_DAYS WHERE EMP_ID=v_request.EMP_ID AND LEAVE_TYPE_ID=v_request.LEAVE_TYPE_ID AND CALENDAR_YEAR = EXTRACT(YEAR FROM v_request.START_DATE)
5. Send notification to employee: subject='Leave Request Approved', body='Your leave request from [start MM/DD/YYYY] to [end MM/DD/YYYY] has been approved.'
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

**Business rules:**
- Only PENDING requests can be approved
- On approval: PENDING balance decremented, USED balance incremented by TOTAL_DAYS

**Exceptions thrown:** -20204 'Cannot approve request in status: [status]'

---

### PROCEDURE reject_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID=p_request_id FOR UPDATE
2. IF v_request.STATUS != 'PENDING' THEN RAISE_APPLICATION_ERROR(-20204, 'Cannot reject request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='REJECTED', APPROVER_EMP_ID, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS, MODIFIED_BY, MODIFIED_DATE WHERE REQUEST_ID=p_request_id
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND CALENDAR_YEAR=EXTRACT(YEAR FROM v_request.START_DATE)
5. Send notification to employee: subject='Leave Request Rejected', body='Your leave request has been rejected. Reason: [comments]'
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

**Business rules:**
- Only PENDING requests can be rejected
- On rejection: PENDING balance released (decremented)

**Exceptions thrown:** -20204 'Cannot reject request in status: [status]'

---

### PROCEDURE cancel_leave_request(p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID=p_request_id FOR UPDATE
2. IF v_request.STATUS NOT IN ('PENDING','APPROVED') THEN RAISE_APPLICATION_ERROR(-20204, 'Cannot cancel request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON=p_reason, CANCELLED_DATE=SYSDATE, MODIFIED_BY, MODIFIED_DATE WHERE REQUEST_ID=p_request_id
4. Balance restoration:
   - IF v_request.STATUS = 'PENDING' THEN UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS ... (release pending)
   - ELSIF v_request.STATUS = 'APPROVED' THEN UPDATE LEAVE_BALANCES SET USED = USED - v_request.TOTAL_DAYS ... (restore used back)
5. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

**Business rules:**
- Only PENDING or APPROVED requests can be cancelled (not REJECTED, CANCELLED, TAKEN)
- Cancelled PENDING request: PENDING balance decremented
- Cancelled APPROVED request: USED balance decremented (balance restored)

**Exceptions thrown:** -20204 'Cannot cancel request in status: [status]'

---

### FUNCTION get_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER

**Logic:**
1. SELECT OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING INTO v_balance FROM LEAVE_BALANCES WHERE EMP_ID=p_emp_id AND LEAVE_TYPE_ID=p_leave_type_id AND CALENDAR_YEAR=p_year
2. RETURN NVL(v_balance, 0)
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0

**Balance formula:** OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING

---

### PROCEDURE adjust_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT + p_adjustment WHERE EMP_ID=p_emp_id AND LEAVE_TYPE_ID=p_leave_type_id AND CALENDAR_YEAR=EXTRACT(YEAR FROM SYSDATE)
2. IF SQL%ROWCOUNT = 0 THEN call initialize_balances(p_emp_id, EXTRACT(YEAR FROM SYSDATE), p_user); then retry UPDATE
3. PKG_AUDIT.log_action('LEAVE_BALANCES', p_emp_id, 'UPDATE', p_user)

---

### PROCEDURE initialize_balances(p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. FOR lt IN (SELECT LEAVE_TYPE_ID FROM LEAVE_TYPES WHERE ACTIVE_FLAG='Y') LOOP:
   - INSERT INTO LEAVE_BALANCES: (BALANCE_ID=SEQ_LEAVE_BALANCE.NEXTVAL, EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR=p_year, OPENING_BALANCE=0, ACCRUED=0, USED=0, ADJUSTMENT=0, PENDING=0, CREATED_BY, CREATED_DATE)
   - EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL (skip if already exists)

**Sequences:** SEQ_LEAVE_BALANCE

---

### PROCEDURE run_monthly_accrual(p_accrual_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** Batch job — accrues leave for all active employees. Typically scheduled via DBMS_SCHEDULER on the 1st of each month.

**Logic:**
1. For each active employee (EMPLOYMENT_STATUS='ACTIVE' AND ACTIVE_FLAG='Y'):
   - For each leave type with ACCRUAL_FLAG='Y' AND ACCRUAL_FREQUENCY='MONTHLY':
     - Check tenure: IF TRUNC(p_accrual_date) - emp_rec.HIRE_DATE >= lt_rec.MIN_TENURE_DAYS THEN:
       - v_current_balance := get_leave_balance(emp_rec.EMP_ID, lt_rec.LEAVE_TYPE_ID, EXTRACT(YEAR FROM p_accrual_date))
       - If MAX_BALANCE is NULL OR v_current_balance + ACCRUAL_RATE <= MAX_BALANCE: v_accrued := ACCRUAL_RATE
       - Else: v_accrued := GREATEST(0, MAX_BALANCE - v_current_balance) — cap to not exceed max
       - IF v_accrued > 0:
         - UPDATE LEAVE_BALANCES SET ACCRUED = ACCRUED + v_accrued WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND CALENDAR_YEAR=EXTRACT(YEAR FROM p_accrual_date)
         - IF SQL%ROWCOUNT=0: call initialize_balances and retry with ACCRUED=v_accrued (not +=)
         - INSERT INTO LEAVE_ACCRUAL_LOG: (ACCRUAL_ID=SEQ_LEAVE_ACCRUAL.NEXTVAL, EMP_ID, LEAVE_TYPE_ID, ACCRUAL_DATE=p_accrual_date, ACCRUAL_AMOUNT=v_accrued, CREATED_BY, CREATED_DATE)
   - COMMIT every 100 employees (MOD(v_total_employees, 100) = 0)
2. Final COMMIT

**Business rules:**
- Only employees with EMPLOYMENT_STATUS='ACTIVE' AND ACTIVE_FLAG='Y' are processed
- Only MONTHLY frequency accrual types processed (separate runs would handle WEEKLY etc.)
- Minimum tenure enforced per leave type (days since hire)
- Accrual amount capped to MAX_BALANCE if specified
- GREATEST(0,...) prevents negative accrual

**Numeric literals:**
- 100 — commit batch size

**Sequences used:** SEQ_LEAVE_ACCRUAL

**Database tables accessed/written:** EMPLOYEES (read), LEAVE_TYPES (read), LEAVE_BALANCES (update), LEAVE_ACCRUAL_LOG (insert)

---

### PROCEDURE process_carryover(p_year NUMBER, p_user VARCHAR2 DEFAULT USER)

**Purpose:** Runs at year-end to carry over unused leave to next year.

**Logic:**
1. v_next_year := p_year + 1
2. FOR bal_rec IN (SELECT lb.EMP_ID, lb.LEAVE_TYPE_ID, lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT AS REMAINING, lt.CARRYOVER_MAX, lt.CARRYOVER_EXPIRY FROM LEAVE_BALANCES lb JOIN LEAVE_TYPES lt ON lb.LEAVE_TYPE_ID=lt.LEAVE_TYPE_ID WHERE lb.CALENDAR_YEAR=p_year AND REMAINING > 0) LOOP:
   - v_carryover := bal_rec.REMAINING
   - IF CARRYOVER_MAX IS NOT NULL THEN v_carryover := LEAST(v_carryover, CARRYOVER_MAX) — cap carryover
   - IF v_carryover > 0 THEN:
     - initialize_balances(EMP_ID, v_next_year, p_user)
     - UPDATE LEAVE_BALANCES SET CARRYOVER_FROM_PREV=v_carryover, OPENING_BALANCE=v_carryover, CARRYOVER_EXPIRY_DT = CASE WHEN CARRYOVER_EXPIRY IS NOT NULL THEN ADD_MONTHS(TO_DATE(v_next_year||'-01-01','YYYY-MM-DD'), CARRYOVER_EXPIRY) ELSE NULL END WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND CALENDAR_YEAR=v_next_year
3. COMMIT

**Business rules:**
- Carryover is remaining balance (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT), not counting PENDING
- Capped at CARRYOVER_MAX if specified per leave type
- Carryover expiry date = next_year Jan 1 + CARRYOVER_EXPIRY months

---

### PROCEDURE expire_carryover(p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT - CARRYOVER_FROM_PREV, CARRYOVER_FROM_PREV=0 WHERE CARRYOVER_EXPIRY_DT <= TRUNC(SYSDATE) AND CARRYOVER_FROM_PREV > 0
2. COMMIT

**Known bug:** If run twice on same day, can double-subtract (since CARRYOVER_FROM_PREV is set to 0 only on the first run, but a second run would still match rows where... wait, actually CARRYOVER_FROM_PREV = 0 after first run so WHERE CARRYOVER_FROM_PREV > 0 would not match. The bug described in the header may refer to a different scenario, or the bug exists if the COMMIT doesn't happen before a second call within the same session).

---

### PROCEDURE get_pending_requests(p_cursor OUT t_leave_cursor, p_approver_id NUMBER)

**Logic:**
1. OPEN p_cursor FOR:
   ```sql
   SELECT lr.REQUEST_ID, lr.EMP_ID, e.FIRST_NAME||' '||e.LAST_NAME AS EMPLOYEE_NAME,
          lt.LEAVE_TYPE_NAME, lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS,
          lr.REASON, lr.CREATED_DATE
   FROM LEAVE_REQUESTS lr
   JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
   JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
   WHERE lr.STATUS = 'PENDING' AND lr.APPROVER_EMP_ID = p_approver_id
   ORDER BY lr.CREATED_DATE
   ```

---

### PROCEDURE get_team_calendar(p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE)

**Logic:**
1. OPEN p_cursor FOR:
   ```sql
   SELECT e.EMP_ID, e.FIRST_NAME||' '||e.LAST_NAME AS EMPLOYEE_NAME,
          lt.LEAVE_TYPE_NAME, lt.LEAVE_TYPE_CODE,
          lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS, lr.STATUS, lr.HALF_DAY_FLAG
   FROM LEAVE_REQUESTS lr
   JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
   JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
   WHERE e.MANAGER_EMP_ID = p_manager_id
   AND lr.STATUS IN ('APPROVED','TAKEN')
   AND lr.START_DATE <= p_end_date AND lr.END_DATE >= p_start_date
   ORDER BY lr.START_DATE, e.LAST_NAME
   ```

---

**All database tables referenced in PKG_LEAVE:**

| Table | Operations |
|---|---|
| EMPLOYEES | SELECT |
| LEAVE_TYPES | SELECT |
| LEAVE_REQUESTS | SELECT, INSERT, UPDATE |
| LEAVE_BALANCES | SELECT, INSERT, UPDATE |
| LEAVE_ACCRUAL_LOG | INSERT |
| HOLIDAYS | SELECT |

**Sequences:** SEQ_LEAVE_REQUEST, SEQ_LEAVE_BALANCE, SEQ_LEAVE_ACCRUAL

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks ===

**Package:** HRMS.PKG_NOTIFICATION
**Schema:** HRMS
**Type:** Package Specification

**Dependencies (per header):** PKG_COMMON
**Called by (per header):** PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE

**Known issues (per header):**
- UTL_MAIL configuration hard-coded to legacy SMTP server
- No rate limiting — bulk operations can flood the queue
- HTML email templates stored as string constants (maintenance nightmare)

---

**Public Signatures:**

| Name | Kind | Parameters |
|---|---|---|
| send_notification | PROCEDURE | p_recipient_emp_id NUMBER DEFAULT NULL, p_recipient_email VARCHAR2 DEFAULT NULL, p_type VARCHAR2 DEFAULT 'EMAIL', p_subject VARCHAR2, p_body CLOB, p_priority NUMBER DEFAULT 5, p_reference_table VARCHAR2 DEFAULT NULL, p_reference_id NUMBER DEFAULT NULL, p_user VARCHAR2 DEFAULT USER |
| process_queue | PROCEDURE | p_batch_size NUMBER DEFAULT 50, p_user VARCHAR2 DEFAULT USER |
| retry_failed | PROCEDURE | p_max_retries NUMBER DEFAULT 3, p_user VARCHAR2 DEFAULT USER |
| cancel_notification | PROCEDURE | p_notification_id NUMBER, p_user VARCHAR2 DEFAULT USER |

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb ===

**Package:** HRMS.PKG_NOTIFICATION
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value |
|---|---|---|
| c_smtp_host | VARCHAR2(100) | 'smtp.internal.company.com' |
| c_smtp_port | NUMBER | 25 |
| c_from_address | VARCHAR2(100) | 'hrms-noreply@company.com' |
| c_from_name | VARCHAR2(100) | 'HRMS System' |

---

### PROCEDURE send_notification(...) — PRAGMA AUTONOMOUS_TRANSACTION

**Full parameter list:**
- p_recipient_emp_id NUMBER DEFAULT NULL, p_recipient_email VARCHAR2 DEFAULT NULL, p_type VARCHAR2 DEFAULT 'EMAIL', p_subject VARCHAR2, p_body CLOB, p_priority NUMBER DEFAULT 5, p_reference_table VARCHAR2 DEFAULT NULL, p_reference_id NUMBER DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. PRAGMA AUTONOMOUS_TRANSACTION
2. Email resolution: IF p_recipient_email IS NULL AND p_recipient_emp_id IS NOT NULL THEN SELECT EMAIL INTO v_email FROM EMPLOYEES WHERE EMP_ID=p_recipient_emp_id; EXCEPTION WHEN NO_DATA_FOUND THEN v_email := NULL; ELSE v_email := p_recipient_email
3. INSERT INTO NOTIFICATION_QUEUE: (NOTIFICATION_ID=SEQ_NOTIFICATION.NEXTVAL, RECIPIENT_EMP_ID, RECIPIENT_EMAIL=v_email, NOTIFICATION_TYPE=p_type, SUBJECT, BODY, STATUS='PENDING', PRIORITY=p_priority, REFERENCE_TABLE, REFERENCE_ID, CREATED_BY=p_user, CREATED_DATE=SYSDATE)
4. COMMIT
5. EXCEPTION WHEN OTHERS: ROLLBACK; PKG_COMMON.log_error('PKG_NOTIFICATION','send_notification','Failed to queue notification: '||SQLERRM, p_user) — notification failures never block business operations

**Business rules:**
- Notification is queued, not sent immediately (async delivery)
- Default priority = 5
- Default type = 'EMAIL'
- Notification failure is silently swallowed (never propagates to caller)
- Email resolved from employee record if not provided directly

**Sequences:** SEQ_NOTIFICATION

**Database tables written:** NOTIFICATION_QUEUE
**Database tables accessed:** EMPLOYEES (read, for email lookup)

---

### PROCEDURE process_queue(p_batch_size IN NUMBER DEFAULT 50, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** Sends pending notifications via UTL_SMTP. Called by DBMS_SCHEDULER job every 5 minutes.

**Logic:**
1. FOR notif_rec IN (SELECT NOTIFICATION_ID, RECIPIENT_EMAIL, SUBJECT, BODY, NOTIFICATION_TYPE FROM NOTIFICATION_QUEUE WHERE STATUS='PENDING' AND NOTIFICATION_TYPE='EMAIL' AND RECIPIENT_EMAIL IS NOT NULL ORDER BY PRIORITY ASC, CREATED_DATE ASC FETCH FIRST p_batch_size ROWS ONLY) LOOP:
   - v_connection := UTL_SMTP.OPEN_CONNECTION('smtp.internal.company.com', 25)
   - UTL_SMTP.HELO(v_connection, 'smtp.internal.company.com')
   - UTL_SMTP.MAIL(v_connection, 'hrms-noreply@company.com')
   - UTL_SMTP.RCPT(v_connection, RECIPIENT_EMAIL)
   - UTL_SMTP.OPEN_DATA; write headers: From, To, Subject, Content-Type: text/plain; charset=UTF-8; blank line; Body
   - UTL_SMTP.CLOSE_DATA; UTL_SMTP.QUIT
   - UPDATE NOTIFICATION_QUEUE SET STATUS='SENT', SENT_DATE=SYSDATE WHERE NOTIFICATION_ID=...
   - v_sent := v_sent + 1
   - EXCEPTION WHEN OTHERS: UPDATE NOTIFICATION_QUEUE SET STATUS='FAILED', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000), RETRY_COUNT=RETRY_COUNT+1 WHERE NOTIFICATION_ID=...; v_failed := v_failed + 1; try UTL_SMTP.QUIT(v_connection)
2. COMMIT
3. Log if any sent or failed

**Business rules:**
- Only processes EMAIL type, PENDING status, with non-null RECIPIENT_EMAIL
- Processing order: lowest priority number first (ORDER BY PRIORITY ASC), then oldest first
- Default batch size = 50 per invocation
- Each email opens/closes its own SMTP connection (no connection pooling)
- SMTP connection per email — inefficient but isolated failures
- Failed emails: STATUS='FAILED', RETRY_COUNT incremented, ERROR_MESSAGE stored (truncated to 4000 chars)

**Numeric literals:**
- 50 — default batch size
- 4000 — max error message length (SUBSTR)

**External services called:** UTL_SMTP (to smtp.internal.company.com:25), UTL_TCP (for CRLF constant)

**Database tables written:** NOTIFICATION_QUEUE

---

### PROCEDURE retry_failed(p_max_retries IN NUMBER DEFAULT 3, p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE NOTIFICATION_QUEUE SET STATUS='PENDING', ERROR_MESSAGE=NULL WHERE STATUS='FAILED' AND RETRY_COUNT < p_max_retries
2. COMMIT

**Business rules:**
- Maximum retry attempts = 3 (default)
- Resets failed notifications back to PENDING if under retry limit
- Clears error message on reset

---

### PROCEDURE cancel_notification(p_notification_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE NOTIFICATION_QUEUE SET STATUS='CANCELLED' WHERE NOTIFICATION_ID=p_notification_id AND STATUS='PENDING'
2. (No COMMIT — relies on caller's transaction)

**Business rules:**
- Only PENDING notifications can be cancelled

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks ===

**Package:** HRMS.PKG_PAYROLL
**Schema:** HRMS
**Type:** Package Specification

---

**Custom Exceptions:**

| Name | Code |
|---|---|
| e_invalid_salary | -20101 |
| e_period_closed | -20102 |
| e_run_already_paid | -20103 |
| e_calculation_error | -20104 |

---

**Type Definitions:**

`TYPE t_payslip_rec IS RECORD`:
- emp_id — NUMBER(10)
- emp_number — VARCHAR2(20)
- emp_name — VARCHAR2(101)
- period_name — VARCHAR2(50)
- gross_pay — NUMBER(12,2)
- total_deductions — NUMBER(12,2)
- net_pay — NUMBER(12,2)
- federal_tax — NUMBER(12,2)
- state_tax — NUMBER(12,2)
- social_security — NUMBER(12,2)
- medicare — NUMBER(12,2)
- ytd_gross — NUMBER(15,2)
- ytd_net — NUMBER(15,2)

`TYPE t_payslip_cursor IS REF CURSOR`

---

**Public Signatures:**

| Name | Kind | Parameters | Returns |
|---|---|---|---|
| create_salary_record | PROCEDURE | p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2 DEFAULT NULL, p_change_pct NUMBER DEFAULT NULL, p_currency_code VARCHAR2 DEFAULT 'USD', p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| get_current_salary | FUNCTION | p_emp_id NUMBER | NUMBER |
| get_salary_as_of | FUNCTION | p_emp_id NUMBER, p_as_of DATE | NUMBER |
| create_pay_periods | PROCEDURE | p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| close_pay_period | PROCEDURE | p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_current_period | FUNCTION | (none) | NUMBER |
| create_payroll_run | FUNCTION | p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER | NUMBER |
| calculate_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| calculate_employee_pay | PROCEDURE | p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| approve_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| reverse_payroll | PROCEDURE | p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| calculate_federal_tax | FUNCTION | p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_state_tax | FUNCTION | p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_fica | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| calculate_medicare | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| get_payslip | PROCEDURE | p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL | — |
| get_ytd_earnings | FUNCTION | p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| generate_pay_register | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |

---

**Dependencies (per header):** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION

**Known issues (per header):**
- Circular dependency with PKG_EMPLOYEE (is_active check)
- Tax calculation uses hard-coded 2024 brackets in some paths
- Overtime calculation does not account for holidays correctly
- YTD accumulation resets incorrectly for mid-year hires in some edge cases

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb ===

**Package:** HRMS.PKG_PAYROLL
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value | Description |
|---|---|---|---|
| c_ss_wage_base_2024 | NUMBER | 168600 | Social Security 2024 wage base |
| c_ss_rate | NUMBER | 0.062 | Employee SS rate (6.2%) |
| c_medicare_rate | NUMBER | 0.0145 | Employee Medicare rate (1.45%) |
| c_medicare_addl_rate | NUMBER | 0.009 | Additional Medicare tax rate (0.9%) |
| c_medicare_addl_threshold | NUMBER | 200000 | Threshold triggering additional Medicare tax |
| c_standard_deduction_single | NUMBER | 14600 | 2024 standard deduction for Single/MFS |
| c_standard_deduction_married | NUMBER | 29200 | 2024 standard deduction for Married Filing Jointly |
| c_allowance_amount | NUMBER | 4300 | Per-allowance reduction amount |

---

### PROCEDURE create_salary_record(...)

**Full parameter list:**
- p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2 DEFAULT NULL, p_change_pct NUMBER DEFAULT NULL, p_currency_code VARCHAR2 DEFAULT 'USD', p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER

**Logic:**
1. IF p_base_salary <= 0 THEN RAISE_APPLICATION_ERROR(-20101, 'Salary must be positive: ' || p_base_salary)
2. UPDATE SALARY_RECORDS SET END_DATE=p_effective_date-1, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' AND EFFECTIVE_DATE < p_effective_date — end-date previous active salary record
3. INSERT INTO SALARY_RECORDS: (SALARY_ID=SEQ_SALARY.NEXTVAL, EMP_ID, EFFECTIVE_DATE, BASE_SALARY, CURRENCY_CODE, PAY_FREQUENCY, SALARY_BASIS='ANNUAL', CHANGE_REASON, CHANGE_PCT, ACTIVE_FLAG='Y', CREATED_BY, CREATED_DATE)
4. PKG_AUDIT.log_action('SALARY_RECORDS', SEQ_SALARY.CURRVAL, 'INSERT', p_user)

**Business rules:**
- Salary must be > 0
- SALARY_BASIS is always 'ANNUAL'
- Default currency = 'USD'
- Default pay frequency = 'MONTHLY'
- Previous active record for that employee end-dated to effective_date - 1

**Exceptions thrown:** -20101 'Salary must be positive: [n]'

**Sequences:** SEQ_SALARY

**Database tables accessed/written:** SALARY_RECORDS

---

### FUNCTION get_current_salary(p_emp_id IN NUMBER) RETURN NUMBER

**Logic:**
1. SELECT BASE_SALARY INTO v_salary FROM SALARY_RECORDS WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' AND EFFECTIVE_DATE <= SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. RETURN v_salary
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0

---

### FUNCTION get_salary_as_of(p_emp_id IN NUMBER, p_as_of IN DATE) RETURN NUMBER

**Logic:**
1. SELECT BASE_SALARY INTO v_salary FROM SALARY_RECORDS WHERE EMP_ID=p_emp_id AND EFFECTIVE_DATE <= p_as_of AND (END_DATE IS NULL OR END_DATE >= p_as_of) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. RETURN v_salary
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0

---

### PROCEDURE create_pay_periods(p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER)

**Logic (MONTHLY):**
1. FOR i IN 1..12 LOOP:
   - v_start_date := TO_DATE(year||'-'||LPAD(i,2,'0')||'-01','YYYY-MM-DD')
   - v_end_date := LAST_DAY(v_start_date)
   - v_pay_date := v_end_date
   - IF TO_CHAR(v_pay_date,'DY') = 'SAT' THEN v_pay_date := v_pay_date - 1 (move to Friday)
   - ELSIF TO_CHAR(v_pay_date,'DY') = 'SUN' THEN v_pay_date := v_pay_date - 2 (move to Friday)
   - v_period_num := v_period_num + 1
   - INSERT INTO PAY_PERIODS: (PERIOD_ID=SEQ_PAY_PERIOD.NEXTVAL, PERIOD_NAME=year||'-'||LPAD(i,2,'0')||' ('||Mon||')', PAY_FREQUENCY, PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE, STATUS='OPEN', CREATED_BY, CREATED_DATE)

**Logic (BIWEEKLY):**
1. v_start_date := TO_DATE(year||'-01-01','YYYY-MM-DD')
2. WHILE TO_CHAR(v_start_date,'DY') != 'FRI' LOOP v_start_date := v_start_date + 1 END LOOP — find first Friday
3. v_start_date := v_start_date - 13 — back to start of pay period (period ends on Friday, starts 2 weeks prior day)
4. WHILE EXTRACT(YEAR FROM v_start_date) <= p_year LOOP:
   - v_end_date := v_start_date + 13 — 14-day period (0..13)
   - v_pay_date := v_end_date + 5 — pay 5 days after period end
   - v_period_num := v_period_num + 1
   - IF year of start OR end = p_year THEN INSERT INTO PAY_PERIODS: (PERIOD_NAME=year||'-BW-'||LPAD(num,2,'0'), STATUS='OPEN', ...)
   - v_start_date := v_end_date + 1
5. COMMIT

**Business rules:**
- MONTHLY: 12 periods per year, each covering full calendar month
- MONTHLY: Pay date = last day of month, moved to preceding Friday if weekend
- BIWEEKLY: 14-day periods ending on Friday
- BIWEEKLY: Pay date = 5 days after period end
- All new periods have STATUS='OPEN'

**Sequences:** SEQ_PAY_PERIOD

---

### PROCEDURE close_pay_period(p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT STATUS INTO v_status FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id FOR UPDATE
2. IF v_status = 'CLOSED' THEN RAISE_APPLICATION_ERROR(-20102, 'Period already closed: ' || p_period_id)
3. UPDATE PAY_PERIODS SET STATUS='CLOSED', CLOSED_BY=p_user, CLOSED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE PERIOD_ID=p_period_id

**Exceptions thrown:** -20102 'Period already closed: [id]'

---

### FUNCTION get_current_period RETURN NUMBER

**Logic:**
1. SELECT PERIOD_ID INTO v_period_id FROM PAY_PERIODS WHERE SYSDATE BETWEEN PERIOD_START_DATE AND PERIOD_END_DATE AND STATUS='OPEN' AND ROWNUM=1
2. RETURN v_period_id
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN NULL

---

### FUNCTION create_payroll_run(p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER) RETURN NUMBER

**Logic:**
1. SELECT STATUS INTO v_status FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id
2. IF v_status = 'CLOSED' THEN RAISE_APPLICATION_ERROR(-20102, 'Cannot create run for closed period: ' || p_period_id)
3. SELECT SEQ_PAYROLL_RUN.NEXTVAL INTO v_run_id FROM DUAL
4. INSERT INTO PAYROLL_RUNS: (RUN_ID, PERIOD_ID, RUN_TYPE, RUN_DATE=SYSDATE, STATUS='PENDING', SUBMITTED_BY=p_user, SUBMITTED_DATE=SYSDATE, CREATED_BY, CREATED_DATE)
5. RETURN v_run_id

**Exceptions thrown:** -20102 'Cannot create run for closed period: [id]'

**Sequences:** SEQ_PAYROLL_RUN

---

### PROCEDURE calculate_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT PERIOD_ID, RUN_TYPE INTO v_period_id, v_run_type FROM PAYROLL_RUNS WHERE RUN_ID=p_run_id
2. UPDATE PAYROLL_RUNS SET STATUS='CALCULATING' WHERE RUN_ID=p_run_id; COMMIT
3. FOR emp_rec IN (SELECT e.EMP_ID FROM EMPLOYEES e WHERE e.EMPLOYMENT_STATUS='ACTIVE' AND e.ACTIVE_FLAG='Y' ORDER BY e.EMP_ID) LOOP:
   - BEGIN calculate_employee_pay(p_run_id, emp_rec.EMP_ID, v_period_id, p_user); v_emp_count := v_emp_count+1
   - EXCEPTION WHEN OTHERS: v_error_count := v_error_count+1; INSERT INTO PAYROLL_DETAILS error row (ELEMENT_ID=0, ELEMENT_TYPE='ERROR', AMOUNT=0, STATUS='ERROR', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000))
   - IF MOD(v_emp_count, 50) = 0 THEN COMMIT (every 50 employees)
4. UPDATE PAYROLL_RUNS SET STATUS = CASE WHEN v_error_count > 0 THEN 'ERROR' ELSE 'CALCULATED' END, EMPLOYEE_COUNT=v_emp_count, ERROR_COUNT=v_error_count, TOTAL_GROSS=(SUM of EARNING elements excluding ERROR status), TOTAL_DEDUCTIONS=(SUM of DEDUCTION/TAX elements excluding ERROR), TOTAL_NET=(net sum), MODIFIED_BY, MODIFIED_DATE WHERE RUN_ID=p_run_id
5. COMMIT

**Business rules:**
- Processes only ACTIVE employees with ACTIVE_FLAG='Y'
- Error in one employee does not stop processing of others
- TOTAL_GROSS = SUM of ELEMENT_TYPE='EARNING' WHERE STATUS != 'ERROR'
- TOTAL_DEDUCTIONS = SUM ABS of ELEMENT_TYPE IN ('DEDUCTION','TAX') WHERE STATUS != 'ERROR'
- TOTAL_NET = SUM of (EARNING amounts + -(DEDUCTION/TAX amounts)) WHERE STATUS != 'ERROR'
- Final STATUS = 'ERROR' if any employee errored, else 'CALCULATED'

**Numeric literals:**
- 50 — commit batch interval
- 4000 — max error message length

**Known issues:**
- Row-by-row cursor loop — should use BULK COLLECT + FORALL
- Partial commits mean a failure leaves payroll half-calculated

---

### PROCEDURE calculate_employee_pay(p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT PERIOD_START_DATE, PERIOD_END_DATE, PAY_FREQUENCY INTO ... FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id
2. v_periods_per_year := CASE PAY_FREQUENCY WHEN 'WEEKLY' THEN 52 WHEN 'BIWEEKLY' THEN 26 WHEN 'SEMIMONTHLY' THEN 24 WHEN 'MONTHLY' THEN 12 ELSE 12 END
3. v_annual_salary := get_salary_as_of(p_emp_id, v_period_end)
4. IF v_annual_salary = 0 THEN RAISE_APPLICATION_ERROR(-20104, 'No active salary record for employee ' || p_emp_id)
5. v_period_gross := ROUND(v_annual_salary / v_periods_per_year, 2)
6. INSERT INTO PAYROLL_DETAILS: (ELEMENT_ID=1, ELEMENT_TYPE='EARNING', AMOUNT=v_period_gross, STATUS='CALCULATED')
7. v_ytd_gross := get_ytd_earnings(p_emp_id, EXTRACT(YEAR FROM v_period_end))
8. Get tax info from EMPLOYEE_TAX_INFO WHERE EMP_ID=p_emp_id AND TAX_YEAR=year AND ACTIVE_FLAG='Y'; DEFAULT IF NONE: filing_status='SINGLE', fed_allowances=0, state_code=NULL, state_allowances=0, addl_fed_wh=0
9. v_taxable_income := v_period_gross (simplified — should subtract pretax deductions)
10. v_federal_tax := calculate_federal_tax(v_taxable_income, v_filing_status, v_fed_allowances, v_addl_fed_wh, v_pay_frequency)
11. IF v_federal_tax > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=100, ELEMENT_TYPE='TAX', AMOUNT=-v_federal_tax)
12. IF v_state_code IS NOT NULL: v_state_tax := calculate_state_tax(v_taxable_income, v_state_code, v_filing_status, v_state_allowances, v_pay_frequency); IF v_state_tax > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=101, ELEMENT_TYPE='TAX', AMOUNT=-v_state_tax)
13. v_ss_tax := calculate_fica(v_period_gross, v_ytd_gross); IF > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=102, ELEMENT_TYPE='TAX', AMOUNT=-v_ss_tax)
14. v_medicare_tax := calculate_medicare(v_period_gross, v_ytd_gross); IF > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=103, ELEMENT_TYPE='TAX', AMOUNT=-v_medicare_tax)
15. FOR ded_rec IN (SELECT ... FROM EMPLOYEE_PAY_ELEMENTS epe JOIN PAY_ELEMENTS pe ON epe.ELEMENT_ID=pe.ELEMENT_ID WHERE epe.EMP_ID=p_emp_id AND epe.ACTIVE_FLAG='Y' AND pe.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') AND epe.EFFECTIVE_DATE <= v_period_end AND (epe.END_DATE IS NULL OR epe.END_DATE >= v_period_start) ORDER BY pe.PRIORITY_ORDER) LOOP:
    - IF OVERRIDE_AMOUNT IS NOT NULL: v_ded_amount := OVERRIDE_AMOUNT
    - ELSIF CALCULATION_TYPE = 'FLAT': v_ded_amount := NVL(AMOUNT, DEFAULT_AMOUNT)
    - ELSIF CALCULATION_TYPE = 'PERCENTAGE': v_ded_amount := ROUND(v_period_gross * NVL(PERCENTAGE, DEFAULT_PERCENTAGE) / 100, 2)
    - ELSE: v_ded_amount := NVL(AMOUNT, 0)
    - IF v_ded_amount > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID, ELEMENT_TYPE, AMOUNT=-v_ded_amount)
16. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error; RAISE

**Fixed ELEMENT_ID assignments:**

| Element ID | Meaning |
|---|---|
| 1 | Base gross pay (EARNING) |
| 100 | Federal income tax (TAX) |
| 101 | State income tax (TAX) |
| 102 | Social Security / FICA (TAX) |
| 103 | Medicare (TAX) |

**Business rules:**
- Period gross = ROUND(annual_salary / periods_per_year, 2)
- Deduction amounts: override > flat > percentage; percentage is of period gross
- Tax amounts stored as negative values in PAYROLL_DETAILS
- Deductions processed in PRIORITY_ORDER
- Only elements effective during the period (EFFECTIVE_DATE <= end AND END_DATE >= start or null) are included
- Default filing status 'SINGLE' with 0 allowances if no EMPLOYEE_TAX_INFO record

**Known issue:** v_taxable_income = v_period_gross (pretax deductions not subtracted — simplified)

---

### FUNCTION calculate_federal_tax(p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER

**Logic:**
1. v_periods := CASE p_pay_frequency WHEN 'WEEKLY' THEN 52 WHEN 'BIWEEKLY' THEN 26 WHEN 'SEMIMONTHLY' THEN 24 WHEN 'MONTHLY' THEN 12 ELSE 12 END
2. v_annualized := p_taxable_income * v_periods
3. v_std_deduction := CASE WHEN p_filing_status IN ('MARRIED_JOINT') THEN 29200 ELSE 14600 END
4. v_taxable := v_annualized - v_std_deduction - (p_allowances * 4300)
5. IF v_taxable <= 0 THEN RETURN 0

**2024 Federal Tax Brackets — SINGLE or MARRIED_SEPARATE:**

| Taxable Income Range | Tax Calculation |
|---|---|
| 0 – 11,600 | taxable × 0.10 |
| 11,601 – 47,150 | 1,160 + (taxable − 11,600) × 0.12 |
| 47,151 – 100,525 | 5,426 + (taxable − 47,150) × 0.22 |
| 100,526 – 191,950 | 17,168.50 + (taxable − 100,525) × 0.24 |
| 191,951 – 243,725 | 39,110.50 + (taxable − 191,950) × 0.32 |
| 243,726 – 609,350 | 55,678.50 + (taxable − 243,725) × 0.35 |
| 609,351 and above | 183,647.25 + (taxable − 609,350) × 0.37 |

**2024 Federal Tax Brackets — MARRIED_JOINT:**

| Taxable Income Range | Tax Calculation |
|---|---|
| 0 – 23,200 | taxable × 0.10 |
| 23,201 – 94,300 | 2,320 + (taxable − 23,200) × 0.12 |
| 94,301 – 201,050 | 10,852 + (taxable − 94,300) × 0.22 |
| 201,051 – 383,900 | 34,337 + (taxable − 201,050) × 0.24 |
| 383,901 – 487,450 | 78,221 + (taxable − 383,900) × 0.32 |
| 487,451 – 731,200 | 111,357 + (taxable − 487,450) × 0.35 |
| 731,201 and above | 196,669.50 + (taxable − 731,200) × 0.37 |

6. v_tax := ROUND(v_tax / v_periods, 2) — convert annual tax back to per-period
7. v_tax := v_tax + NVL(p_additional_wh, 0) — add any additional withholding
8. RETURN v_tax

**Business rules:**
- Annualize income, apply standard deduction and allowances, apply bracket, de-annualize
- Standard deduction: 14,600 (single/MFS), 29,200 (married joint)
- Per-allowance reduction: 4,300
- Additional withholding added on top of bracket-calculated amount
- Brackets are 2024 rates, hard-coded (TODO: read from TAX_BRACKETS table)

---

### FUNCTION calculate_state_tax(p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER

**Logic:**
1. v_rate := CASE p_state_code:
   - 'CA' → 0.0725 (7.25%)
   - 'NY' → 0.0685 (6.85%)
   - 'TX' → 0 (no state income tax)
   - 'FL' → 0 (no state income tax)
   - 'WA' → 0 (no state income tax)
   - 'IL' → 0.0495 (4.95%)
   - 'PA' → 0.0307 (3.07%)
   - 'OH' → 0.04 (4.00%)
   - 'NJ' → 0.0637 (6.37%)
   - 'MA' → 0.05 (5.00%)
   - ELSE → 0.05 (5.00% default for unknown states)
2. RETURN ROUND(p_taxable_income * v_rate, 2)

**Business rules:**
- Simplified flat-rate by state; no progressive brackets (noted as simplified)
- Unknown/unrecognized state codes default to 5.00% flat rate
- TX, FL, WA have no state income tax (0%)

---

### FUNCTION calculate_fica(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER

**Logic:**
1. IF p_ytd_gross >= 168600 THEN RETURN 0 — already exceeded SS wage base
2. v_taxable := LEAST(p_gross_pay, 168600 - p_ytd_gross) — cap at remaining wage base
3. RETURN ROUND(v_taxable * 0.062, 2) — 6.2% employee share

**Business rules:**
- Social Security wage base 2024: 168,600
- Rate: 6.2% (employee portion only)
- Earnings above the wage base are not subject to SS tax

---

### FUNCTION calculate_medicare(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER

**Logic:**
1. v_base_tax := ROUND(p_gross_pay * 0.0145, 2) — 1.45% on all earnings (no wage base)
2. Additional Medicare (0.9%) on high earners:
   - IF p_ytd_gross + p_gross_pay > 200,000 THEN:
     - IF p_ytd_gross >= 200,000 THEN v_addl_tax := ROUND(p_gross_pay * 0.009, 2) — entire period over threshold
     - ELSE v_addl_tax := ROUND((p_ytd_gross + p_gross_pay - 200,000) * 0.009, 2) — only the portion above threshold
3. RETURN v_base_tax + v_addl_tax

**Business rules:**
- Base Medicare: 1.45% on all wages, no cap
- Additional Medicare: 0.9% on wages exceeding 200,000 YTD
- Additional rate applies only to the portion of current period wages that pushed YTD over 200,000

---

### PROCEDURE approve_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT STATUS INTO v_status FROM PAYROLL_RUNS WHERE RUN_ID=p_run_id FOR UPDATE
2. IF v_status NOT IN ('CALCULATED') THEN RAISE_APPLICATION_ERROR(-20103, 'Cannot approve run in status: ' || v_status)
3. UPDATE PAYROLL_RUNS SET STATUS='APPROVED', APPROVED_BY=p_user, APPROVED_DATE=SYSDATE WHERE RUN_ID=p_run_id

**Business rules:**
- Only 'CALCULATED' runs can be approved (not PENDING, ERROR, REVERSED, etc.)

**Exceptions thrown:** -20103 'Cannot approve run in status: [status]'

---

### PROCEDURE reverse_payroll(p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE PAYROLL_RUNS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id
2. UPDATE PAYROLL_DETAILS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id
3. PKG_AUDIT.log_action('PAYROLL_RUNS', p_run_id, 'UPDATE', p_user)

**Business rules:**
- No status check before reversing (can reverse from any status)
- All detail lines set to 'REVERSED'

---

### PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL)

**Logic:**
1. OPEN p_cursor FOR:
   ```sql
   SELECT pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME||' '||e.LAST_NAME AS EMP_NAME,
          pp.PERIOD_NAME,
          SUM(CASE WHEN pd.ELEMENT_TYPE='EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY,
          SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','TAX','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS,
          SUM(pd.AMOUNT) AS NET_PAY,
          SUM(CASE WHEN pd.ELEMENT_ID=100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX,
          SUM(CASE WHEN pd.ELEMENT_ID=101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX,
          SUM(CASE WHEN pd.ELEMENT_ID=102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY,
          SUM(CASE WHEN pd.ELEMENT_ID=103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE,
          0 AS YTD_GROSS,  -- Placeholder (not implemented)
          0 AS YTD_NET     -- Placeholder (not implemented)
   FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ... JOIN PAYROLL_RUNS pr ... JOIN PAY_PERIODS pp ...
   WHERE pd.RUN_ID=p_run_id AND pd.STATUS != 'ERROR' AND (p_emp_id IS NULL OR pd.EMP_ID=p_emp_id)
   GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME||' '||e.LAST_NAME, pp.PERIOD_NAME
   ORDER BY e.LAST_NAME
   ```

**Known limitations:** YTD_GROSS and YTD_NET are hard-coded 0 (placeholders not implemented)

---

### FUNCTION get_ytd_earnings(p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER

**Logic:**
1. SELECT NVL(SUM(pd.AMOUNT),0) INTO v_ytd FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ... JOIN PAY_PERIODS pp ... WHERE pd.EMP_ID=p_emp_id AND pd.ELEMENT_TYPE='EARNING' AND pd.STATUS='CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
2. RETURN v_ytd

---

### PROCEDURE generate_pay_register(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Purpose:** Writes pay register to UTL_FILE CSV output. LEGACY: flat file — should be replaced with modern reporting.

**Logic:**
1. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE,'YYYYMMDD_HH24MISS') || '.csv'
2. v_file := UTL_FILE.FOPEN('PAYROLL_OUTPUT', v_filename, 'W', 32767)
3. Write CSV header: `EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY`
4. FOR rec IN (aggregated pay data per employee with dept) LOOP:
   - Write CSV line: EMP_NUMBER,"EMPLOYEE_NAME","DEPT_NAME",GROSS,FED,STATE,SS,MED,DEDS,NET (amounts formatted FM999999990.00)
5. UTL_FILE.FCLOSE; DBMS_OUTPUT.PUT_LINE confirmation message
6. EXCEPTION WHEN OTHERS: close file; PKG_COMMON.log_error; RAISE

**Oracle directory object used:** 'PAYROLL_OUTPUT'

**File format (CSV):**
- Header row with 10 columns
- Detail: EMP_NUMBER (unquoted), EMP_NAME (double-quoted), DEPT_NAME (double-quoted), 8 numeric columns

---

**All database tables referenced in PKG_PAYROLL:**

| Table | Operations |
|---|---|
| SALARY_RECORDS | SELECT, INSERT, UPDATE |
| PAY_PERIODS | SELECT, INSERT, UPDATE |
| PAYROLL_RUNS | SELECT, INSERT, UPDATE |
| PAYROLL_DETAILS | SELECT, INSERT, UPDATE |
| EMPLOYEES | SELECT |
| DEPARTMENTS | SELECT |
| EMPLOYEE_TAX_INFO | SELECT |
| EMPLOYEE_PAY_ELEMENTS | SELECT |
| PAY_ELEMENTS | SELECT |

**All sequences:**
- SEQ_SALARY
- SEQ_PAY_PERIOD
- SEQ_PAYROLL_RUN
- SEQ_PAYROLL_DETAIL

**External packages called:**
- PKG_AUDIT.log_action
- PKG_COMMON.log_error, PKG_COMMON.log_info

**External Oracle features used:**
- UTL_FILE (directory objects: PAYROLL_OUTPUT)
- DBMS_SCHEDULER (implied — scheduler calls process_queue every 5 minutes per PKG_NOTIFICATION)

---

**Cross-package dependency summary:**

| Package | Calls | Called by |
|---|---|---|
| PKG_EMPLOYEE | PKG_PAYROLL, PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON | PKG_LEAVE (employee validation), PKG_PAYROLL (is_active), forms, batch |
| PKG_PAYROLL | PKG_EMPLOYEE (is_active — circular), PKG_AUDIT, PKG_COMMON | PKG_EMPLOYEE (create_salary_record), forms, batch |
| PKG_LEAVE | PKG_EMPLOYEE, PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON | Forms, self-service portal, batch |
| PKG_NOTIFICATION | PKG_COMMON, UTL_SMTP | PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE |
| PKG_INTEGRATION | PKG_COMMON, UTL_FILE | Batch scheduler |

**Referenced but not provided in source:**
- PKG_AUDIT (log_action)
- PKG_COMMON (log_error, log_info, get_param)
- PKG_PERFORMANCE (referenced in PKG_NOTIFICATION header)
- PKG_SECURITY (TODO in terminate_employee)
- DBMS_SCHEDULER (scheduling context)
- SYSTEM_PARAMETERS table (FTP credentials stored here per integration header)


=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks ===

**Package:** HRMS.PKG_EMPLOYEE
**Schema:** HRMS

**Package-Level Global Variables:**
- `g_current_user` VARCHAR2(30) — session state
- `g_current_emp_id` NUMBER(10) — session state
- `g_current_dept_id` NUMBER(10) — session state
- `g_debug_mode` BOOLEAN := FALSE — session state

**Custom Exceptions:**
| Exception Name | Error Code | PRAGMA |
|---|---|---|
| e_employee_not_found | -20001 | PRAGMA EXCEPTION_INIT |
| e_duplicate_emp_number | -20002 | PRAGMA EXCEPTION_INIT |
| e_invalid_department | -20003 | PRAGMA EXCEPTION_INIT |
| e_invalid_manager | -20004 | PRAGMA EXCEPTION_INIT |
| e_termination_error | -20005 | PRAGMA EXCEPTION_INIT |

**Types:**

`TYPE t_emp_rec IS RECORD:`
- emp_id: EMPLOYEES.EMP_ID%TYPE
- emp_number: EMPLOYEES.EMP_NUMBER%TYPE
- first_name: EMPLOYEES.FIRST_NAME%TYPE
- last_name: EMPLOYEES.LAST_NAME%TYPE
- hire_date: EMPLOYEES.HIRE_DATE%TYPE
- dept_id: EMPLOYEES.DEPT_ID%TYPE
- job_id: EMPLOYEES.JOB_ID%TYPE
- manager_emp_id: EMPLOYEES.MANAGER_EMP_ID%TYPE
- employment_status: EMPLOYEES.EMPLOYMENT_STATUS%TYPE
- base_salary: NUMBER(12,2)

`TYPE t_emp_cursor IS REF CURSOR`

`TYPE t_emp_id_table IS TABLE OF NUMBER(10) INDEX BY BINARY_INTEGER`

`TYPE t_emp_rec_table IS TABLE OF t_emp_rec INDEX BY BINARY_INTEGER`

**Public Method Signatures:**

| Method | Kind | Parameters | Returns |
|---|---|---|---|
| create_employee | FUNCTION | p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_manager_emp_id NUMBER DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_employment_type VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary NUMBER DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER |
| update_employee | PROCEDURE | p_emp_id NUMBER, p_first_name VARCHAR2 DEFAULT NULL, p_last_name VARCHAR2 DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_phone_work VARCHAR2 DEFAULT NULL, p_phone_mobile VARCHAR2 DEFAULT NULL, p_address_line1 VARCHAR2 DEFAULT NULL, p_address_line2 VARCHAR2 DEFAULT NULL, p_city VARCHAR2 DEFAULT NULL, p_state_province VARCHAR2 DEFAULT NULL, p_postal_code VARCHAR2 DEFAULT NULL, p_country_code VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| get_employee | FUNCTION | p_emp_id NUMBER | t_emp_rec |
| get_employee_by_number | FUNCTION | p_emp_number VARCHAR2 | t_emp_rec |
| search_employees | PROCEDURE | p_cursor OUT t_emp_cursor, p_last_name VARCHAR2 DEFAULT NULL, p_first_name VARCHAR2 DEFAULT NULL, p_dept_id NUMBER DEFAULT NULL, p_status VARCHAR2 DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_hire_date_from DATE DEFAULT NULL, p_hire_date_to DATE DEFAULT NULL | — |
| transfer_employee | PROCEDURE | p_emp_id NUMBER, p_new_dept_id NUMBER, p_new_job_id NUMBER DEFAULT NULL, p_new_manager_id NUMBER DEFAULT NULL, p_new_location VARCHAR2 DEFAULT NULL, p_effective_date DATE DEFAULT SYSDATE, p_reason_code VARCHAR2 DEFAULT NULL, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| promote_employee | PROCEDURE | p_emp_id NUMBER, p_new_job_id NUMBER, p_new_salary NUMBER, p_effective_date DATE DEFAULT SYSDATE, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| terminate_employee | PROCEDURE | p_emp_id NUMBER, p_termination_date DATE, p_reason VARCHAR2, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| rehire_employee | PROCEDURE | p_emp_id NUMBER, p_rehire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_base_salary NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_direct_reports | FUNCTION | p_manager_emp_id NUMBER | t_emp_id_table |
| get_org_chart | FUNCTION | p_root_emp_id NUMBER, p_max_depth NUMBER DEFAULT 10 | t_emp_cursor |
| get_headcount_by_dept | FUNCTION | p_dept_id NUMBER DEFAULT NULL, p_as_of_date DATE DEFAULT SYSDATE | NUMBER |
| get_tenure_years | FUNCTION | p_emp_id NUMBER | NUMBER |
| is_active | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| validate_employee | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| emp_exists | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| generate_emp_number | FUNCTION | (none) | VARCHAR2 |
| set_session_context | PROCEDURE | p_user VARCHAR2, p_emp_id NUMBER | — |

**Dependencies declared in header:**
- PKG_COMMON
- PKG_AUDIT
- PKG_NOTIFICATION
- PKG_PAYROLL

**Callers declared in header:**
- HRMS_EMPLOYEE form
- HRMS_DEPARTMENT form
- Batch jobs

**Known issues documented in header:**
- Circular dependency with PKG_PAYROLL (salary validation)
- get_org_chart uses recursive SQL that times out for deep hierarchies

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb ===

**Package:** HRMS.PKG_EMPLOYEE (body)

**Private Constants:**
| Constant | Type | Value |
|---|---|---|
| c_emp_number_prefix | VARCHAR2(3) | 'EMP' |
| c_max_hierarchy_depth | NUMBER | 15 |

**Private Forward Declarations:**
- PROCEDURE log_history(...) — full signature matches public-facing logic below
- PROCEDURE validate_dept(p_dept_id IN NUMBER)
- PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)
- FUNCTION get_next_emp_id RETURN NUMBER

---

**FUNCTION generate_emp_number RETURN VARCHAR2**

Logic:
1. SELECT NVL(MAX(TO_NUMBER(SUBSTR(EMP_NUMBER, 5))), 0) + 1 INTO v_max_num FROM EMPLOYEES WHERE EMP_NUMBER LIKE 'EMP-%'
   - Parses numeric suffix starting at character position 5 (after 'EMP-')
2. Formats as: 'EMP-' || LPAD(v_max_num, 6, '0') — zero-padded to 6 digits
3. EXCEPTION WHEN OTHERS: fallback to 'EMP-' || LPAD(SEQ_EMPLOYEE.NEXTVAL, 6, '0')

Documented bug: race condition under concurrent inserts — no SELECT FOR UPDATE.

Database tables read: EMPLOYEES
Sequences used: SEQ_EMPLOYEE

---

**FUNCTION get_next_emp_id RETURN NUMBER**

Logic:
1. SELECT SEQ_EMPLOYEE.NEXTVAL INTO v_id FROM DUAL
2. RETURN v_id

Sequences used: SEQ_EMPLOYEE

---

**PROCEDURE validate_dept(p_dept_id IN NUMBER)**

Logic:
1. SELECT COUNT(*) INTO v_count FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id AND ACTIVE_FLAG = 'Y'
2. IF v_count = 0 THEN RAISE_APPLICATION_ERROR(-20003, 'Invalid or inactive department: ' || p_dept_id)

Business rule: Department must exist and have ACTIVE_FLAG = 'Y'.

Database tables read: DEPARTMENTS (DEPT_ID, ACTIVE_FLAG)
Exceptions thrown: -20003 — department not found or inactive

---

**PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)**

Logic:
1. IF p_manager_id IS NULL THEN RETURN — NULL manager is valid (top-level employee)
2. SELECT COUNT(*) FROM EMPLOYEES WHERE EMP_ID = p_manager_id AND EMPLOYMENT_STATUS = 'ACTIVE'
   - If count = 0: RAISE_APPLICATION_ERROR(-20004, 'Invalid or inactive manager: ' || p_manager_id)
3. Circular chain check (only when p_emp_id IS NOT NULL):
   - v_current_mgr := p_manager_id; v_depth := 0
   - WHILE v_current_mgr IS NOT NULL AND v_depth < 15 LOOP
     - IF v_current_mgr = p_emp_id: RAISE_APPLICATION_ERROR(-20004, 'Circular reporting chain detected: Employee ' || p_emp_id || ' cannot report to ' || p_manager_id)
     - SELECT MANAGER_EMP_ID INTO v_current_mgr FROM EMPLOYEES WHERE EMP_ID = v_current_mgr
       - EXCEPTION WHEN NO_DATA_FOUND: v_current_mgr := NULL
     - v_depth := v_depth + 1
   - Loop terminates when v_current_mgr IS NULL or v_depth reaches 15 (c_max_hierarchy_depth)

Business rules:
- Manager must be an ACTIVE employee.
- Hierarchy must not be circular.
- Circular detection traverses at most 15 levels deep.

Database tables read: EMPLOYEES (EMP_ID, EMPLOYMENT_STATUS, MANAGER_EMP_ID)
Exceptions thrown:
- -20004 — invalid/inactive manager
- -20004 — circular reporting chain detected

---

**PROCEDURE log_history(...) — PRAGMA AUTONOMOUS_TRANSACTION**

Parameters (all):
- p_emp_id IN NUMBER
- p_change_type IN VARCHAR2
- p_effective_date IN DATE
- p_old_dept_id IN NUMBER DEFAULT NULL
- p_new_dept_id IN NUMBER DEFAULT NULL
- p_old_job_id IN NUMBER DEFAULT NULL
- p_new_job_id IN NUMBER DEFAULT NULL
- p_old_manager IN NUMBER DEFAULT NULL
- p_new_manager IN NUMBER DEFAULT NULL
- p_old_salary IN NUMBER DEFAULT NULL
- p_new_salary IN NUMBER DEFAULT NULL
- p_old_location IN VARCHAR2 DEFAULT NULL
- p_new_location IN VARCHAR2 DEFAULT NULL
- p_reason_code IN VARCHAR2 DEFAULT NULL
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. PRAGMA AUTONOMOUS_TRANSACTION — runs in a separate transaction
2. INSERT INTO EMPLOYEE_HISTORY (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE) VALUES (SEQ_EMP_HISTORY.NEXTVAL, ...)
3. COMMIT
4. EXCEPTION WHEN OTHERS: ROLLBACK; if g_debug_mode then DBMS_OUTPUT.PUT_LINE warning; end

Business rule: History logging never fails the main transaction (exceptions are swallowed).

Database tables written: EMPLOYEE_HISTORY
Sequences used: SEQ_EMP_HISTORY
Columns inserted: HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE

---

**FUNCTION create_employee(...) RETURN NUMBER**

Parameters:
- p_first_name IN VARCHAR2
- p_last_name IN VARCHAR2
- p_hire_date IN DATE
- p_dept_id IN NUMBER
- p_job_id IN NUMBER
- p_manager_emp_id IN NUMBER DEFAULT NULL
- p_location_code IN VARCHAR2 DEFAULT NULL
- p_employment_type IN VARCHAR2 DEFAULT 'FULL_TIME'
- p_base_salary IN NUMBER DEFAULT NULL
- p_email IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. Validate p_first_name IS NOT NULL AND p_last_name IS NOT NULL — else RAISE_APPLICATION_ERROR(-20010, 'First name and last name are required')
2. Call validate_dept(p_dept_id)
3. Call validate_manager(p_manager_emp_id) — no p_emp_id passed (new hire, no circular check needed)
4. SELECT GRADE_ID INTO v_grade_id FROM JOB_TITLES WHERE JOB_ID = p_job_id AND ACTIVE_FLAG = 'Y'
   - EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20011, 'Invalid or inactive job: ' || p_job_id)
5. Salary vs. grade validation (soft warning, not an error):
   - If p_base_salary IS NOT NULL:
     - SELECT MIN_SALARY, MAX_SALARY INTO v_min, v_max FROM JOB_GRADES WHERE GRADE_ID = v_grade_id
     - IF p_base_salary < v_min OR p_base_salary > v_max: log debug warning only
     - Business rule: Salary outside grade range is a WARNING, not a hard error; override allowed with manager approval; the Forms trigger WHEN-VALIDATE-ITEM shows a warning dialog
6. Default location from department if p_location_code IS NULL:
   - SELECT LOCATION_CODE INTO v_location FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id
7. v_emp_id := get_next_emp_id()
8. v_emp_number := generate_emp_number()
9. INSERT INTO EMPLOYEES (EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID, MANAGER_EMP_ID, LOCATION_CODE, EMPLOYMENT_TYPE, EMPLOYMENT_STATUS, EMAIL, ACTIVE_FLAG, CREATED_BY, CREATED_DATE)
   - FIRST_NAME stored as UPPER(TRIM(p_first_name))
   - LAST_NAME stored as UPPER(TRIM(p_last_name))
   - EMAIL stored as LOWER(TRIM(p_email))
   - EMPLOYMENT_STATUS = 'ACTIVE'
   - ACTIVE_FLAG = 'Y'
10. If p_base_salary IS NOT NULL: call PKG_PAYROLL.create_salary_record(p_emp_id, p_hire_date, p_base_salary, 'NEW_HIRE', p_user)
    - Documented circular dependency: PKG_PAYROLL.create_salary_record may call PKG_EMPLOYEE.is_active
11. Call log_history(p_emp_id, 'HIRE', p_hire_date, new_dept/job/manager/salary/location)
12. Call PKG_AUDIT.log_action('EMPLOYEES', v_emp_id, 'INSERT', p_user)
13. Call PKG_NOTIFICATION.send_notification to employee: type='EMAIL', subject='Welcome to the Company', body includes first_name and emp_number
14. If p_manager_emp_id IS NOT NULL: call PKG_NOTIFICATION.send_notification to manager: subject='New Direct Report: <first> <last>', body includes hire_date formatted as MM/DD/YYYY
15. RETURN v_emp_id

Exceptions:
- -20010 — first/last name null
- -20011 — invalid/inactive job
- DUP_VAL_ON_INDEX → RAISE_APPLICATION_ERROR(-20002, 'Duplicate employee number generated. Please retry.')
- WHEN OTHERS → PKG_COMMON.log_error('PKG_EMPLOYEE', 'create_employee', SQLERRM, p_user) then RAISE

Database tables read: DEPARTMENTS (DEPT_ID, ACTIVE_FLAG, LOCATION_CODE), JOB_TITLES (JOB_ID, ACTIVE_FLAG, GRADE_ID), JOB_GRADES (GRADE_ID, MIN_SALARY, MAX_SALARY)
Database tables written: EMPLOYEES
Sequences: SEQ_EMPLOYEE (via get_next_emp_id), implicit via generate_emp_number
External services called: PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification (twice)

---

**PROCEDURE update_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_first_name IN VARCHAR2 DEFAULT NULL
- p_last_name IN VARCHAR2 DEFAULT NULL
- p_email IN VARCHAR2 DEFAULT NULL
- p_phone_work IN VARCHAR2 DEFAULT NULL
- p_phone_mobile IN VARCHAR2 DEFAULT NULL
- p_address_line1 IN VARCHAR2 DEFAULT NULL
- p_address_line2 IN VARCHAR2 DEFAULT NULL
- p_city IN VARCHAR2 DEFAULT NULL
- p_state_province IN VARCHAR2 DEFAULT NULL
- p_postal_code IN VARCHAR2 DEFAULT NULL
- p_country_code IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. Call emp_exists(p_emp_id); if FALSE: RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)
2. UPDATE EMPLOYEES SET:
   - FIRST_NAME = NVL(UPPER(TRIM(p_first_name)), FIRST_NAME)
   - LAST_NAME = NVL(UPPER(TRIM(p_last_name)), LAST_NAME)
   - EMAIL = NVL(LOWER(TRIM(p_email)), EMAIL)
   - PHONE_WORK = NVL(p_phone_work, PHONE_WORK)
   - PHONE_MOBILE = NVL(p_phone_mobile, PHONE_MOBILE)
   - ADDRESS_LINE1 = NVL(p_address_line1, ADDRESS_LINE1)
   - ADDRESS_LINE2 = NVL(p_address_line2, ADDRESS_LINE2)
   - CITY = NVL(p_city, CITY)
   - STATE_PROVINCE = NVL(p_state_province, STATE_PROVINCE)
   - POSTAL_CODE = NVL(p_postal_code, POSTAL_CODE)
   - COUNTRY_CODE = NVL(p_country_code, COUNTRY_CODE)
   - MODIFIED_BY = p_user
   - MODIFIED_DATE = SYSDATE
   WHERE EMP_ID = p_emp_id
3. IF SQL%ROWCOUNT = 0: RAISE_APPLICATION_ERROR(-20001, 'Employee update failed: ' || p_emp_id)
4. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

Business rule: Partial update pattern — only non-NULL input parameters overwrite existing values (NVL pattern).

Database tables written: EMPLOYEES
External services: PKG_AUDIT.log_action

---

**FUNCTION get_employee(p_emp_id IN NUMBER) RETURN t_emp_rec**

Logic:
1. SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, e.JOB_ID, e.MANAGER_EMP_ID, e.EMPLOYMENT_STATUS, (subquery for BASE_SALARY) FROM EMPLOYEES e WHERE e.EMP_ID = p_emp_id
2. Salary subquery: SELECT sr.BASE_SALARY FROM SALARY_RECORDS sr WHERE sr.EMP_ID = e.EMP_ID AND sr.ACTIVE_FLAG = 'Y' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE) AND ROWNUM = 1
3. EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)

Database tables read: EMPLOYEES, SALARY_RECORDS

---

**FUNCTION get_employee_by_number(p_emp_number IN VARCHAR2) RETURN t_emp_rec**

Logic:
1. SELECT EMP_ID INTO v_emp_id FROM EMPLOYEES WHERE EMP_NUMBER = p_emp_number
2. RETURN get_employee(v_emp_id)
3. EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_number)

Database tables read: EMPLOYEES

---

**PROCEDURE search_employees(...)**

Parameters:
- p_cursor OUT t_emp_cursor
- p_last_name IN VARCHAR2 DEFAULT NULL
- p_first_name IN VARCHAR2 DEFAULT NULL
- p_dept_id IN NUMBER DEFAULT NULL
- p_status IN VARCHAR2 DEFAULT NULL
- p_location_code IN VARCHAR2 DEFAULT NULL
- p_hire_date_from IN DATE DEFAULT NULL
- p_hire_date_to IN DATE DEFAULT NULL

Logic (dynamic SQL via string concatenation):
1. Base query: SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, d.DEPT_NAME, j.JOB_TITLE, e.EMPLOYMENT_STATUS, e.LOCATION_CODE FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE 1=1
2. If p_last_name IS NOT NULL: AND UPPER(e.LAST_NAME) LIKE UPPER('<p_last_name>%') — VULNERABILITY: string concatenation, not bind variable
3. If p_first_name IS NOT NULL: AND UPPER(e.FIRST_NAME) LIKE UPPER('<p_first_name>%') — VULNERABILITY: string concatenation
4. If p_dept_id IS NOT NULL: AND e.DEPT_ID = <p_dept_id>
5. If p_status IS NOT NULL: AND e.EMPLOYMENT_STATUS = '<p_status>' — VULNERABILITY: string concatenation
6. If p_location_code IS NOT NULL: AND e.LOCATION_CODE = '<p_location_code>' — VULNERABILITY: string concatenation
7. If p_hire_date_from IS NOT NULL: AND e.HIRE_DATE >= TO_DATE('<YYYY-MM-DD>', 'YYYY-MM-DD')
8. If p_hire_date_to IS NOT NULL: AND e.HIRE_DATE <= TO_DATE('<YYYY-MM-DD>', 'YYYY-MM-DD')
9. ORDER BY e.LAST_NAME, e.FIRST_NAME
10. OPEN p_cursor FOR v_sql (dynamic OPEN)

Documented bug: SQL injection possible via p_last_name (and all other VARCHAR2 parameters). Forms LOV passes validated values; direct PL/SQL calls are vulnerable.

Database tables read: EMPLOYEES, DEPARTMENTS, JOB_TITLES

---

**PROCEDURE transfer_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_new_dept_id IN NUMBER
- p_new_job_id IN NUMBER DEFAULT NULL
- p_new_manager_id IN NUMBER DEFAULT NULL
- p_new_location IN VARCHAR2 DEFAULT NULL
- p_effective_date IN DATE DEFAULT SYSDATE
- p_reason_code IN VARCHAR2 DEFAULT NULL
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT * INTO v_old_rec FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE NOWAIT
2. IF v_old_rec.EMPLOYMENT_STATUS != 'ACTIVE': RAISE_APPLICATION_ERROR(-20012, 'Cannot transfer non-active employee. Status: ' || v_old_rec.EMPLOYMENT_STATUS)
3. validate_dept(p_new_dept_id)
4. v_new_job_id := NVL(p_new_job_id, v_old_rec.JOB_ID)
5. v_new_location := NVL(p_new_location, v_old_rec.LOCATION_CODE)
6. If p_new_manager_id IS NOT NULL: validate_manager(p_new_manager_id, p_emp_id)
7. UPDATE EMPLOYEES SET DEPT_ID=p_new_dept_id, JOB_ID=v_new_job_id, MANAGER_EMP_ID=NVL(p_new_manager_id, MANAGER_EMP_ID), LOCATION_CODE=v_new_location, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
8. log_history(p_emp_id, 'TRANSFER', p_effective_date, old/new dept/job/manager/location, reason, comments)
9. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error then RAISE

Business rules:
- Only ACTIVE employees can be transferred.
- Locking via FOR UPDATE NOWAIT (fails immediately if row locked).
- Job and location default to current values if not specified.

Exceptions thrown:
- -20012 — cannot transfer non-active employee
- -20003 — invalid department (from validate_dept)
- -20004 — invalid manager or circular chain (from validate_manager)

Database tables read/written: EMPLOYEES
External services: PKG_AUDIT.log_action, PKG_COMMON.log_error

---

**PROCEDURE promote_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_new_job_id IN NUMBER
- p_new_salary IN NUMBER
- p_effective_date IN DATE DEFAULT SYSDATE
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT JOB_ID INTO v_old_job_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. SELECT BASE_SALARY INTO v_old_salary FROM SALARY_RECORDS WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y' AND ROWNUM = 1 ORDER BY EFFECTIVE_DATE DESC
   - EXCEPTION WHEN NO_DATA_FOUND: v_old_salary := 0
3. UPDATE EMPLOYEES SET JOB_ID = p_new_job_id, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID = p_emp_id
4. PKG_PAYROLL.create_salary_record(p_emp_id, p_effective_date, p_new_salary, 'PROMOTION', p_change_pct=ROUND(((p_new_salary - v_old_salary) / v_old_salary) * 100, 2) when v_old_salary > 0 else NULL, p_user)
5. log_history(p_emp_id, 'PROMOTION', p_effective_date, old/new job, old/new salary, comments)
6. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

Business rule: Change percentage computed as ROUND(((new - old) / old) * 100, 2); only computed when old_salary > 0.

Database tables read: EMPLOYEES, SALARY_RECORDS
Database tables written: EMPLOYEES
External services: PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action

---

**PROCEDURE terminate_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_termination_date IN DATE
- p_reason IN VARCHAR2
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE
2. IF v_emp.EMPLOYMENT_STATUS = 'TERMINATED': RAISE_APPLICATION_ERROR(-20005, 'Employee ' || p_emp_id || ' is already terminated')
3. SELECT COUNT(*) INTO v_pending_leave FROM LEAVE_REQUESTS WHERE EMP_ID = p_emp_id AND STATUS = 'PENDING'
4. If v_pending_leave > 0: UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON='Auto-cancelled due to termination', CANCELLED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND STATUS='PENDING'
5. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='TERMINATED', TERMINATION_DATE=p_termination_date, TERMINATION_REASON=p_reason, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
6. UPDATE SALARY_RECORDS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
7. UPDATE EMPLOYEE_PAY_ELEMENTS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
8. log_history(p_emp_id, 'TERMINATION', p_termination_date, reason, comments)
9. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. If v_emp.MANAGER_EMP_ID IS NOT NULL: PKG_NOTIFICATION.send_notification to manager: subject='Employee Termination: <first> <last>', body includes termination date formatted MM/DD/YYYY
11. TODO comments (not implemented): benefits system COBRA integration, security access revocation via PKG_SECURITY, final pay via PKG_PAYROLL.calculate_final_pay
12. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error then RAISE

Business rules:
- Already-terminated employee cannot be terminated again.
- All PENDING leave requests are auto-cancelled on termination.
- Active salary record end-dated to p_termination_date.
- All active pay elements end-dated to p_termination_date.

Exceptions: -20005 — already terminated

Database tables read/written: EMPLOYEES, LEAVE_REQUESTS, SALARY_RECORDS, EMPLOYEE_PAY_ELEMENTS
External services: PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action, PKG_COMMON.log_error

---

**PROCEDURE rehire_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_rehire_date IN DATE
- p_dept_id IN NUMBER
- p_job_id IN NUMBER
- p_base_salary IN NUMBER
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. validate_dept(p_dept_id)
2. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='ACTIVE', HIRE_DATE=p_rehire_date, TERMINATION_DATE=NULL, TERMINATION_REASON=NULL, DEPT_ID=p_dept_id, JOB_ID=p_job_id, ACTIVE_FLAG='Y', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
3. IF SQL%ROWCOUNT = 0: RAISE_APPLICATION_ERROR(-20001, 'Employee not found for rehire: ' || p_emp_id)
4. PKG_PAYROLL.create_salary_record(p_emp_id, p_rehire_date, p_base_salary, 'REHIRE', p_user)
5. log_history(p_emp_id, 'REHIRE', p_rehire_date, new_dept/job/salary)
6. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

Business rule: Rehire clears TERMINATION_DATE and TERMINATION_REASON; resets HIRE_DATE to rehire date; sets ACTIVE_FLAG='Y'.

Database tables written: EMPLOYEES
External services: PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action

---

**FUNCTION get_direct_reports(p_manager_emp_id IN NUMBER) RETURN t_emp_id_table**

Logic:
1. Cursor loop: SELECT EMP_ID FROM EMPLOYEES WHERE MANAGER_EMP_ID = p_manager_emp_id AND EMPLOYMENT_STATUS = 'ACTIVE' ORDER BY LAST_NAME, FIRST_NAME
2. Accumulates into indexed table v_result(v_idx) := r.EMP_ID
3. Returns populated table

Business rule: Only ACTIVE employees are included.

Database tables read: EMPLOYEES

---

**FUNCTION get_org_chart(p_root_emp_id IN NUMBER, p_max_depth IN NUMBER DEFAULT 10) RETURN t_emp_cursor**

Logic:
1. Opens ref cursor with hierarchical query:
   SELECT LEVEL AS depth, EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID, JOB_ID, MANAGER_EMP_ID FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' START WITH EMP_ID = p_root_emp_id CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID AND LEVEL <= p_max_depth ORDER SIBLINGS BY LAST_NAME, FIRST_NAME

Documented issue: Known to time out for orgs with >500 employees.

Database tables read: EMPLOYEES

---

**FUNCTION get_headcount_by_dept(p_dept_id IN NUMBER DEFAULT NULL, p_as_of_date IN DATE DEFAULT SYSDATE) RETURN NUMBER**

Logic:
1. SELECT COUNT(*) FROM EMPLOYEES WHERE (p_dept_id IS NULL OR DEPT_ID = p_dept_id) AND EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= p_as_of_date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)

Business rule: Active employees hired on or before as_of_date, and either not terminated or terminated after as_of_date.

Database tables read: EMPLOYEES

---

**FUNCTION get_tenure_years(p_emp_id IN NUMBER) RETURN NUMBER**

Logic:
1. SELECT HIRE_DATE, NVL(TERMINATION_DATE, SYSDATE) INTO v_hire_date, v_end_date FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN ROUND(MONTHS_BETWEEN(v_end_date, v_hire_date) / 12, 1)
3. EXCEPTION WHEN NO_DATA_FOUND: RETURN NULL

Business rule: Tenure in years = ROUND(MONTHS_BETWEEN(end_date, hire_date) / 12, 1). Uses SYSDATE as end date for active employees.

Database tables read: EMPLOYEES

---

**FUNCTION is_active(p_emp_id IN NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT EMPLOYMENT_STATUS INTO v_status FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_status = 'ACTIVE'
3. EXCEPTION WHEN NO_DATA_FOUND: RETURN FALSE

Database tables read: EMPLOYEES

---

**FUNCTION validate_employee(p_emp_id IN NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. IF v_emp.FIRST_NAME IS NULL OR v_emp.LAST_NAME IS NULL: RETURN FALSE
3. IF v_emp.HIRE_DATE IS NULL: RETURN FALSE
4. IF v_emp.EMPLOYMENT_STATUS = 'ACTIVE' AND v_emp.ACTIVE_FLAG != 'Y': RETURN FALSE
5. RETURN TRUE
6. EXCEPTION WHEN NO_DATA_FOUND: RETURN FALSE

Business rules:
- Must have first and last name.
- Must have hire date.
- If EMPLOYMENT_STATUS = 'ACTIVE', ACTIVE_FLAG must be 'Y'.

Database tables read: EMPLOYEES

---

**FUNCTION emp_exists(p_emp_id IN NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_count > 0

Database tables read: EMPLOYEES

---

**PROCEDURE set_session_context(p_user IN VARCHAR2, p_emp_id IN NUMBER)**

Logic:
1. g_current_user := p_user
2. g_current_emp_id := p_emp_id
3. SELECT DEPT_ID INTO g_current_dept_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
4. EXCEPTION WHEN NO_DATA_FOUND: g_current_dept_id := NULL

Database tables read: EMPLOYEES

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks ===

**Package:** HRMS.PKG_INTEGRATION

**Types:**

`TYPE t_gl_entry IS RECORD:`
- journal_date: DATE
- account_code: VARCHAR2(30)
- debit_amount: NUMBER(15,2)
- credit_amount: NUMBER(15,2)
- description: VARCHAR2(200)
- reference: VARCHAR2(100)

`TYPE t_gl_entry_table IS TABLE OF t_gl_entry INDEX BY BINARY_INTEGER`

**Public Method Signatures:**

| Method | Kind | Parameters |
|---|---|---|
| generate_gl_journal | PROCEDURE | p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER |
| export_benefits_feed | PROCEDURE | p_effective_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER |
| import_time_attendance | PROCEDURE | p_file_name IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER |
| sync_org_structure | PROCEDURE | p_user IN VARCHAR2 DEFAULT USER |
| get_integration_status | FUNCTION | p_integration_name IN VARCHAR2 → RETURN VARCHAR2 |

**Dependencies:** PKG_COMMON, PKG_PAYROLL, PKG_EMPLOYEE
**Callers:** Batch scheduler (nightly GL feed, weekly benefits sync)

**Known issues documented:**
- GL posting uses flat file exchange (UTL_FILE) instead of API
- Benefits feed format is vendor-specific (ADP format)
- No retry logic for failed file transfers
- FTP credentials stored in SYSTEM_PARAMETERS table (cleartext)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb ===

**Package:** HRMS.PKG_INTEGRATION (body)

**Private Constants:**
| Constant | Type | Value |
|---|---|---|
| c_gl_output_dir | VARCHAR2(30) | 'GL_FEED_OUT' |
| c_benefits_output_dir | VARCHAR2(30) | 'BENEFITS_FEED_OUT' |
| c_time_input_dir | VARCHAR2(30) | 'TIME_ATTENDANCE_IN' |

These map to Oracle directory objects.

---

**PROCEDURE generate_gl_journal(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. v_filename := 'GL_JOURNAL_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD') || '.dat'
2. Open UTL_FILE in directory 'GL_FEED_OUT', mode 'W', buffer 32767
3. Write header: 'H|HRMS_PAYROLL|<YYYY-MM-DD>|<p_run_id>'
4. Cursor query:
   ```
   SELECT d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE,
          SUM(pd.AMOUNT) AS TOTAL_AMOUNT, pp.PERIOD_NAME
   FROM PAYROLL_DETAILS pd
   JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
   JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID
   JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
   JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
   JOIN PAY_ELEMENTS pe ON pd.ELEMENT_ID = pe.ELEMENT_ID
   WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND pe.GL_ACCOUNT_CODE IS NOT NULL
   GROUP BY d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE, pp.PERIOD_NAME
   ```
5. For each row:
   - If ELEMENT_TYPE = 'EARNING': write 'D|<COST_CENTER>|<GL_ACCOUNT_CODE>|<debit_amount>|0.00|Payroll <PERIOD_NAME>|RUN-<p_run_id>'
   - Else: write 'D|<COST_CENTER>|<GL_ACCOUNT_CODE>|0.00|<credit_amount>|Payroll <PERIOD_NAME>|RUN-<p_run_id>'
   - Amounts formatted with TO_CHAR(ABS(TOTAL_AMOUNT), 'FM999999990.00')
6. Write trailer: 'T|<v_entries>'
7. Close file
8. Log info via PKG_COMMON.log_info
9. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

File format: Pipe-delimited. Consumed by Oracle Financials batch import.
Business rule: Earnings generate debit entries to expense accounts; Deductions/Taxes generate credit entries to liability accounts.

Database tables read: PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS, EMPLOYEES, DEPARTMENTS, PAY_ELEMENTS
External file I/O: UTL_FILE write to Oracle directory 'GL_FEED_OUT'
External services: PKG_COMMON.log_info, PKG_COMMON.log_error

---

**PROCEDURE export_benefits_feed(p_effective_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. v_filename := 'BENEFITS_' || TO_CHAR(SYSDATE, 'YYYYMMDD') || '.txt'
2. Open UTL_FILE in directory 'BENEFITS_FEED_OUT', mode 'W', buffer 32767
3. Cursor query:
   ```
   SELECT e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.DATE_OF_BIRTH, e.HIRE_DATE,
          e.EMPLOYMENT_STATUS, e.MARITAL_STATUS, e.GENDER,
          d.FIRST_NAME AS DEP_FIRST_NAME, d.LAST_NAME AS DEP_LAST_NAME,
          d.RELATIONSHIP, d.DATE_OF_BIRTH AS DEP_DOB
   FROM EMPLOYEES e
   LEFT JOIN EMPLOYEE_DEPENDENTS d ON e.EMP_ID = d.EMP_ID AND d.ACTIVE_FLAG = 'Y'
   WHERE e.EMPLOYMENT_STATUS = 'ACTIVE'
   ORDER BY e.EMP_NUMBER, d.DEPENDENT_ID
   ```
4. For each row, write fixed-width record:

   | Field | Width | Notes |
   |---|---|---|
   | EMP_NUMBER | 10 (RPAD) | |
   | FIRST_NAME | 30 (RPAD) | |
   | LAST_NAME | 30 (RPAD) | |
   | DATE_OF_BIRTH | 10 (RPAD) | formatted 'YYYY-MM-DD' |
   | HIRE_DATE | 10 (RPAD) | formatted 'YYYY-MM-DD' |
   | EMPLOYMENT_STATUS | 12 (RPAD) | |
   | MARITAL_STATUS | 10 (RPAD) | |
   | GENDER | 1 (RPAD) | |
   | DEP_FIRST_NAME | 30 (RPAD) | |
   | DEP_LAST_NAME | 30 (RPAD) | |
   | RELATIONSHIP | 20 (RPAD) | |
   | DEP_DOB | 10 (RPAD) | formatted 'YYYY-MM-DD' |
   | **Total record width** | **193** | |

5. Close file; log info; EXCEPTION WHEN OTHERS: close file; log_error; RAISE

File format: Fixed-width, ADP vendor format (legacy).

Database tables read: EMPLOYEES (EMP_NUMBER, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, HIRE_DATE, EMPLOYMENT_STATUS, MARITAL_STATUS, GENDER), EMPLOYEE_DEPENDENTS (EMP_ID, ACTIVE_FLAG, FIRST_NAME, LAST_NAME, RELATIONSHIP, DATE_OF_BIRTH, DEPENDENT_ID)
External file I/O: UTL_FILE write to Oracle directory 'BENEFITS_FEED_OUT'
External services: PKG_COMMON.log_info, PKG_COMMON.log_error

---

**PROCEDURE import_time_attendance(p_file_name IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. Open UTL_FILE in directory 'TIME_ATTENDANCE_IN', filename p_file_name, mode 'R', buffer 32767
2. Loop:
   - UTL_FILE.GET_LINE(v_file, v_line)
   - EXCEPTION WHEN NO_DATA_FOUND: EXIT (end of file)
   - Skip blank lines and lines starting with '#'
   - TODO: Parse CSV: emp_number, date, hours_regular, hours_overtime — actual parsing and database update NOT implemented
   - v_imported := v_imported + 1 on each valid-looking line
   - EXCEPTION WHEN OTHERS per line: v_errors := v_errors + 1; PKG_COMMON.log_error per line
3. Close file; log summary (Imported: N, Errors: N)
4. EXCEPTION WHEN OTHERS: close file; log_error; RAISE

Business rule: Lines beginning with '#' are treated as comments and skipped.
Note: Actual parsing and DB update is NOT implemented (TODO).

External file I/O: UTL_FILE read from Oracle directory 'TIME_ATTENDANCE_IN'
External services: PKG_COMMON.log_error, PKG_COMMON.log_info

---

**PROCEDURE sync_org_structure(p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. Placeholder only — logs 'Org structure sync completed'
2. PKG_COMMON.log_info('PKG_INTEGRATION', 'sync_org_structure', 'Org structure sync completed', p_user)

Note: Intended for LDAP/Active Directory sync; not implemented.

External services: PKG_COMMON.log_info

---

**FUNCTION get_integration_status(p_integration_name IN VARCHAR2) RETURN VARCHAR2**

Logic:
1. RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS')

Configuration key pattern: INTEGRATION.<p_integration_name>_STATUS (from SYSTEM_PARAMETERS via PKG_COMMON.get_param)

External services: PKG_COMMON.get_param

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks ===

**Package:** HRMS.PKG_LEAVE

**Custom Exceptions:**
| Exception Name | Error Code |
|---|---|
| e_insufficient_balance | -20201 |
| e_overlapping_leave | -20202 |
| e_invalid_leave_type | -20203 |
| e_approval_error | -20204 |

**Types:**
`TYPE t_leave_cursor IS REF CURSOR`

**Public Method Signatures:**

| Method | Kind | Parameters | Returns |
|---|---|---|---|
| submit_leave_request | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_half_day_flag CHAR DEFAULT 'N', p_half_day_period VARCHAR2 DEFAULT NULL, p_reason VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER (request_id) |
| approve_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| reject_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| cancel_leave_request | PROCEDURE | p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| get_leave_balance | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| adjust_leave_balance | PROCEDURE | p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| initialize_balances | PROCEDURE | p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| run_monthly_accrual | PROCEDURE | p_accrual_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER | — |
| process_carryover | PROCEDURE | p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| expire_carryover | PROCEDURE | p_user VARCHAR2 DEFAULT USER | — |
| get_pending_requests | PROCEDURE | p_cursor OUT t_leave_cursor, p_approver_id NUMBER | — |
| get_team_calendar | PROCEDURE | p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE | — |
| calculate_business_days | FUNCTION | p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL | NUMBER |
| check_leave_overlap | FUNCTION | p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL | BOOLEAN |

**Dependencies:** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
**Callers:** HRMS_LEAVE form, self-service portal, batch accrual job

**Known issues documented:**
- Overlapping leave detection does not account for half-day requests
- Carryover expiry job sometimes double-expires if run twice on same day
- Holiday detection only checks exact date match, not observed dates

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb ===

**Package:** HRMS.PKG_LEAVE (body)

---

**FUNCTION calculate_business_days(p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL) RETURN NUMBER**

Logic:
1. v_date := TRUNC(p_start_date)
2. WHILE v_date <= TRUNC(p_end_date) LOOP:
   - IF TO_CHAR(v_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN') NOT IN ('SAT', 'SUN') THEN:
     - SELECT COUNT(*) FROM HOLIDAYS WHERE HOLIDAY_DATE = v_date AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)
     - If holiday count = 0: v_count := v_count + 1
   - v_date := v_date + 1
3. RETURN v_count

Business rules:
- Weekends (SAT, SUN) are not business days.
- Dates in HOLIDAYS table with ACTIVE_FLAG='Y' and matching LOCATION_CODE (or global holidays where LOCATION_CODE IS NULL) are excluded.

Documented bug: Does not handle "observed" holidays (e.g., if July 4 falls on Saturday, the observed Friday is not excluded).

Database tables read: HOLIDAYS (HOLIDAY_DATE, ACTIVE_FLAG, LOCATION_CODE)

---

**FUNCTION check_leave_overlap(p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL) RETURN BOOLEAN**

Logic:
1. SELECT COUNT(*) FROM LEAVE_REQUESTS WHERE EMP_ID = p_emp_id AND STATUS IN ('PENDING', 'APPROVED') AND (p_exclude_request_id IS NULL OR REQUEST_ID != p_exclude_request_id) AND START_DATE <= p_end_date AND END_DATE >= p_start_date
2. RETURN v_count > 0

Business rule: Overlap check covers PENDING and APPROVED requests using date range intersection.

Database tables read: LEAVE_REQUESTS (EMP_ID, STATUS, REQUEST_ID, START_DATE, END_DATE)

---

**FUNCTION submit_leave_request(...) RETURN NUMBER**

Parameters:
- p_emp_id IN NUMBER
- p_leave_type_id IN NUMBER
- p_start_date IN DATE
- p_end_date IN DATE
- p_half_day_flag IN CHAR DEFAULT 'N'
- p_half_day_period IN VARCHAR2 DEFAULT NULL
- p_reason IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT * INTO v_emp_rec FROM EMPLOYEES WHERE EMP_ID = p_emp_id AND EMPLOYMENT_STATUS = 'ACTIVE'
   - EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20001, 'Employee not found or not active: ' || p_emp_id)
2. SELECT * INTO v_leave_type FROM LEAVE_TYPES WHERE LEAVE_TYPE_ID = p_leave_type_id AND ACTIVE_FLAG = 'Y'
   - EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20203, 'Invalid leave type: ' || p_leave_type_id)
3. Tenure check: IF v_leave_type.MIN_TENURE_DAYS > 0 AND SYSDATE - v_emp_rec.HIRE_DATE < v_leave_type.MIN_TENURE_DAYS THEN RAISE_APPLICATION_ERROR(-20203, 'Minimum tenure of ' || MIN_TENURE_DAYS || ' days not met for leave type: ' || LEAVE_TYPE_NAME)
4. Validate dates: IF p_start_date > p_end_date: RAISE_APPLICATION_ERROR(-20210, 'Start date must be before or equal to end date')
5. Backdated request limit: IF p_start_date < TRUNC(SYSDATE) AND TRUNC(SYSDATE) - p_start_date > 5: RAISE_APPLICATION_ERROR(-20211, 'Cannot submit leave requests more than 5 days in the past')
6. Calculate total days:
   - If p_half_day_flag = 'Y': v_total_days := 0.5
   - Else: v_total_days := calculate_business_days(p_start_date, p_end_date, v_emp_rec.LOCATION_CODE)
7. IF v_total_days <= 0: RAISE_APPLICATION_ERROR(-20212, 'No business days in the selected range')
8. Overlap check: IF check_leave_overlap(p_emp_id, p_start_date, p_end_date): RAISE_APPLICATION_ERROR(-20202, 'Leave request overlaps with an existing request')
9. Balance check (only if v_leave_type.ACCRUAL_FLAG = 'Y'):
   - v_balance := get_leave_balance(p_emp_id, p_leave_type_id)
   - IF v_balance < v_total_days: RAISE_APPLICATION_ERROR(-20201, 'Insufficient leave balance. Available: ' || v_balance || ', Requested: ' || v_total_days)
10. SELECT SEQ_LEAVE_REQUEST.NEXTVAL INTO v_request_id FROM DUAL
11. v_manager_id := v_emp_rec.MANAGER_EMP_ID
12. INSERT INTO LEAVE_REQUESTS (REQUEST_ID, EMP_ID, LEAVE_TYPE_ID, START_DATE, END_DATE, TOTAL_DAYS, HALF_DAY_FLAG, HALF_DAY_PERIOD, STATUS, REASON, APPROVER_EMP_ID, CREATED_BY, CREATED_DATE)
    - STATUS = CASE WHEN v_leave_type.REQUIRES_APPROVAL = 'Y' THEN 'PENDING' ELSE 'APPROVED' END
13. UPDATE LEAVE_BALANCES SET PENDING = PENDING + v_total_days WHERE EMP_ID = p_emp_id AND LEAVE_TYPE_ID = p_leave_type_id AND CALENDAR_YEAR = EXTRACT(YEAR FROM p_start_date)
14. If v_manager_id IS NOT NULL AND REQUIRES_APPROVAL = 'Y': PKG_NOTIFICATION.send_notification to manager: subject='Leave Request Pending Approval', body includes employee name, days, leave type name, dates in MM/DD/YYYY format
15. If REQUIRES_APPROVAL = 'N': call approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user)
16. PKG_AUDIT.log_action('LEAVE_REQUESTS', v_request_id, 'INSERT', p_user)
17. RETURN v_request_id

Business rules:
- Employee must be ACTIVE.
- Leave type must be ACTIVE.
- Minimum tenure (in days) must be met.
- End date must be >= start date.
- Backdating limit: maximum 5 days in the past.
- Half-day requests = 0.5 days (fixed); full requests = calculated business days.
- Zero business days is rejected.
- Overlapping PENDING or APPROVED requests block submission.
- Balance check applies only to accrual-based leave types (ACCRUAL_FLAG = 'Y').
- If REQUIRES_APPROVAL = 'N', auto-approved immediately.
- LEAVE_BALANCES.PENDING incremented on submission (regardless of REQUIRES_APPROVAL).

Exceptions:
- -20001 — employee not found or not active
- -20203 — invalid leave type or tenure not met
- -20210 — start date after end date
- -20211 — more than 5 days in the past
- -20212 — no business days in range
- -20202 — overlapping leave request
- -20201 — insufficient balance

Sequences: SEQ_LEAVE_REQUEST
Database tables read: EMPLOYEES, LEAVE_TYPES, LEAVE_BALANCES
Database tables written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_NOTIFICATION.send_notification, approve_leave_request (self-call), PKG_AUDIT.log_action

---

**PROCEDURE approve_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE
2. IF v_request.STATUS != 'PENDING': RAISE_APPLICATION_ERROR(-20204, 'Cannot approve request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='APPROVED', APPROVER_EMP_ID=p_approver_emp_id, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS=p_comments, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE REQUEST_ID=p_request_id
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS, USED = USED + v_request.TOTAL_DAYS WHERE EMP_ID=v_request.EMP_ID AND LEAVE_TYPE_ID=v_request.LEAVE_TYPE_ID AND CALENDAR_YEAR=EXTRACT(YEAR FROM v_request.START_DATE)
5. PKG_NOTIFICATION.send_notification to employee: subject='Leave Request Approved', body includes start/end dates in MM/DD/YYYY
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

Business rules:
- Only PENDING requests can be approved.
- Balance moves from PENDING to USED on approval.

Exceptions: -20204 — cannot approve in current status

Database tables read/written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action

---

**PROCEDURE reject_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT * FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE
2. IF STATUS != 'PENDING': RAISE_APPLICATION_ERROR(-20204, 'Cannot reject request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='REJECTED', APPROVER_EMP_ID=p_approver_emp_id, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS=p_comments, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS (release pending balance)
5. PKG_NOTIFICATION.send_notification to employee: subject='Leave Request Rejected', body='Your leave request has been rejected. Reason: ' || p_comments
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

Business rules:
- Only PENDING requests can be rejected.
- Pending balance released on rejection.

Exceptions: -20204 — cannot reject in current status

Database tables written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action

---

**PROCEDURE cancel_leave_request(p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT * FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE
2. IF STATUS NOT IN ('PENDING', 'APPROVED'): RAISE_APPLICATION_ERROR(-20204, 'Cannot cancel request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON=p_reason, CANCELLED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE
4. Balance restoration:
   - If was PENDING: UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS
   - If was APPROVED: UPDATE LEAVE_BALANCES SET USED = USED - v_request.TOTAL_DAYS
5. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

Business rules:
- Only PENDING or APPROVED requests can be cancelled.
- Cancelling PENDING restores PENDING balance.
- Cancelling APPROVED restores USED balance.

Exceptions: -20204 — cannot cancel in current status

Database tables written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_AUDIT.log_action

---

**FUNCTION get_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
1. SELECT OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING INTO v_balance FROM LEAVE_BALANCES WHERE EMP_ID = p_emp_id AND LEAVE_TYPE_ID = p_leave_type_id AND CALENDAR_YEAR = p_year
2. RETURN NVL(v_balance, 0)
3. EXCEPTION WHEN NO_DATA_FOUND: RETURN 0

Business rule (balance formula): Available Balance = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING

Database tables read: LEAVE_BALANCES (OPENING_BALANCE, ACCRUED, USED, ADJUSTMENT, PENDING)

---

**PROCEDURE adjust_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT + p_adjustment WHERE EMP_ID = p_emp_id AND LEAVE_TYPE_ID = p_leave_type_id AND CALENDAR_YEAR = EXTRACT(YEAR FROM SYSDATE)
2. IF SQL%ROWCOUNT = 0: initialize_balances(p_emp_id, EXTRACT(YEAR FROM SYSDATE), p_user) then retry same UPDATE
3. PKG_AUDIT.log_action('LEAVE_BALANCES', p_emp_id, 'UPDATE', p_user)

Database tables written: LEAVE_BALANCES
External services: PKG_AUDIT.log_action

---

**PROCEDURE initialize_balances(p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. For each LEAVE_TYPES row where ACTIVE_FLAG = 'Y':
   - INSERT INTO LEAVE_BALANCES (BALANCE_ID, EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR, OPENING_BALANCE, ACCRUED, USED, ADJUSTMENT, PENDING, CREATED_BY, CREATED_DATE) VALUES (SEQ_LEAVE_BALANCE.NEXTVAL, p_emp_id, lt.LEAVE_TYPE_ID, p_year, 0, 0, 0, 0, 0, p_user, SYSDATE)
   - EXCEPTION WHEN DUP_VAL_ON_INDEX: NULL (skip if already exists)

Business rule: All active leave types get a balance record initialized to zeros.

Sequences: SEQ_LEAVE_BALANCE
Database tables read: LEAVE_TYPES (LEAVE_TYPE_ID, ACTIVE_FLAG)
Database tables written: LEAVE_BALANCES

---

**PROCEDURE run_monthly_accrual(p_accrual_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. Outer cursor: all ACTIVE employees with ACTIVE_FLAG = 'Y'
2. Inner cursor: LEAVE_TYPES where ACTIVE_FLAG='Y' AND ACCRUAL_FLAG='Y' AND ACCRUAL_FREQUENCY='MONTHLY'
   - Columns read: LEAVE_TYPE_ID, ACCRUAL_RATE, ACCRUAL_FREQUENCY, MAX_BALANCE, MIN_TENURE_DAYS
3. For each employee × leave type:
   a. Check tenure: IF TRUNC(p_accrual_date) - emp.HIRE_DATE >= lt.MIN_TENURE_DAYS
   b. Get current balance via get_leave_balance(emp.EMP_ID, lt.LEAVE_TYPE_ID, EXTRACT(YEAR FROM p_accrual_date))
   c. Determine accrual amount:
      - If MAX_BALANCE IS NULL OR current_balance + ACCRUAL_RATE <= MAX_BALANCE: v_accrued := ACCRUAL_RATE
      - Else: v_accrued := GREATEST(0, MAX_BALANCE - current_balance)  — caps at maximum
   d. If v_accrued > 0:
      - UPDATE LEAVE_BALANCES SET ACCRUED = ACCRUED + v_accrued WHERE EMP_ID=emp.EMP_ID AND LEAVE_TYPE_ID=lt.LEAVE_TYPE_ID AND CALENDAR_YEAR=EXTRACT(YEAR FROM p_accrual_date)
      - If SQL%ROWCOUNT = 0: initialize_balances then retry UPDATE with ACCRUED = v_accrued (not += on retry)
      - INSERT INTO LEAVE_ACCRUAL_LOG (ACCRUAL_ID, EMP_ID, LEAVE_TYPE_ID, ACCRUAL_DATE, ACCRUAL_AMOUNT, CREATED_BY, CREATED_DATE)
4. COMMIT every 100 employees (MOD(v_total_employees, 100) = 0)
5. Final COMMIT
6. DBMS_OUTPUT progress messages

Business rules:
- Only MONTHLY accrual frequency processed.
- Tenure gate: employee must meet MIN_TENURE_DAYS before accruing.
- Accrual is capped at MAX_BALANCE; partial accrual allowed (GREATEST(0, MAX_BALANCE - current)).
- Commits every 100 employees (partial-commit risk on failure).

Sequences: SEQ_LEAVE_ACCRUAL
Database tables read: EMPLOYEES, LEAVE_TYPES, LEAVE_BALANCES
Database tables written: LEAVE_BALANCES, LEAVE_ACCRUAL_LOG

---

**PROCEDURE process_carryover(p_year NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. v_next_year := p_year + 1
2. Cursor:
   ```
   SELECT lb.EMP_ID, lb.LEAVE_TYPE_ID,
          lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT AS REMAINING,
          lt.CARRYOVER_MAX, lt.CARRYOVER_EXPIRY
   FROM LEAVE_BALANCES lb
   JOIN LEAVE_TYPES lt ON lb.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
   WHERE lb.CALENDAR_YEAR = p_year
   AND lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT > 0
   ```
3. v_carryover := bal_rec.REMAINING
4. If CARRYOVER_MAX IS NOT NULL: v_carryover := LEAST(v_carryover, CARRYOVER_MAX)
5. If v_carryover > 0:
   - initialize_balances(emp_id, next_year, p_user)
   - UPDATE LEAVE_BALANCES SET CARRYOVER_FROM_PREV = v_carryover, OPENING_BALANCE = v_carryover, CARRYOVER_EXPIRY_DT = CASE WHEN CARRYOVER_EXPIRY IS NOT NULL THEN ADD_MONTHS(TO_DATE(next_year || '-01-01', 'YYYY-MM-DD'), CARRYOVER_EXPIRY) ELSE NULL END WHERE EMP_ID=emp_id AND LEAVE_TYPE_ID=lt_id AND CALENDAR_YEAR=next_year
6. COMMIT

Business rules:
- Only positive remaining balances are carried over.
- Carryover is capped by CARRYOVER_MAX if set.
- Expiry date = January 1 of next year + CARRYOVER_EXPIRY months (if set).
- OPENING_BALANCE for next year is set to carryover amount.

Database tables read: LEAVE_BALANCES, LEAVE_TYPES
Database tables written: LEAVE_BALANCES

---

**PROCEDURE expire_carryover(p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT - CARRYOVER_FROM_PREV, CARRYOVER_FROM_PREV = 0, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE CARRYOVER_EXPIRY_DT <= TRUNC(SYSDATE) AND CARRYOVER_FROM_PREV > 0
2. COMMIT

Documented bug: If run twice on same day, can double-subtract (CARRYOVER_FROM_PREV is set to 0 after first run so second run WHERE CARRYOVER_FROM_PREV > 0 would not match — the bug is actually in the description but examining the code: after setting CARRYOVER_FROM_PREV = 0, second run WHERE CARRYOVER_FROM_PREV > 0 should not match. However, the expiry date check <= SYSDATE means within a single transaction window it could be a concern).

Database tables written: LEAVE_BALANCES

---

**PROCEDURE get_pending_requests(p_cursor OUT t_leave_cursor, p_approver_id NUMBER)**

Logic: Opens ref cursor:
```sql
SELECT lr.REQUEST_ID, lr.EMP_ID,
       e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME,
       lt.LEAVE_TYPE_NAME,
       lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS,
       lr.REASON, lr.CREATED_DATE
FROM LEAVE_REQUESTS lr
JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
WHERE lr.STATUS = 'PENDING'
AND lr.APPROVER_EMP_ID = p_approver_id
ORDER BY lr.CREATED_DATE
```

Database tables read: LEAVE_REQUESTS, EMPLOYEES, LEAVE_TYPES

---

**PROCEDURE get_team_calendar(p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE)**

Logic: Opens ref cursor:
```sql
SELECT e.EMP_ID, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME,
       lt.LEAVE_TYPE_NAME, lt.LEAVE_TYPE_CODE,
       lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS,
       lr.STATUS, lr.HALF_DAY_FLAG
FROM LEAVE_REQUESTS lr
JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
WHERE e.MANAGER_EMP_ID = p_manager_id
AND lr.STATUS IN ('APPROVED', 'TAKEN')
AND lr.START_DATE <= p_end_date
AND lr.END_DATE >= p_start_date
ORDER BY lr.START_DATE, e.LAST_NAME
```

Database tables read: LEAVE_REQUESTS, EMPLOYEES, LEAVE_TYPES

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks ===

**Package:** HRMS.PKG_NOTIFICATION

**Dependencies:** PKG_COMMON
**Callers:** PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE

**Known issues:**
- UTL_MAIL configuration hard-coded to legacy SMTP server
- No rate limiting — bulk operations can flood the queue
- HTML email templates stored as string constants (maintenance nightmare)

**Public Method Signatures:**

| Method | Kind | Parameters |
|---|---|---|
| send_notification | PROCEDURE | p_recipient_emp_id NUMBER DEFAULT NULL, p_recipient_email VARCHAR2 DEFAULT NULL, p_type VARCHAR2 DEFAULT 'EMAIL', p_subject VARCHAR2, p_body CLOB, p_priority NUMBER DEFAULT 5, p_reference_table VARCHAR2 DEFAULT NULL, p_reference_id NUMBER DEFAULT NULL, p_user VARCHAR2 DEFAULT USER |
| process_queue | PROCEDURE | p_batch_size NUMBER DEFAULT 50, p_user VARCHAR2 DEFAULT USER |
| retry_failed | PROCEDURE | p_max_retries NUMBER DEFAULT 3, p_user VARCHAR2 DEFAULT USER |
| cancel_notification | PROCEDURE | p_notification_id NUMBER, p_user VARCHAR2 DEFAULT USER |

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb ===

**Package:** HRMS.PKG_NOTIFICATION (body)

**Private Constants:**
| Constant | Type | Value |
|---|---|---|
| c_smtp_host | VARCHAR2(100) | 'smtp.internal.company.com' |
| c_smtp_port | NUMBER | 25 |
| c_from_address | VARCHAR2(100) | 'hrms-noreply@company.com' |
| c_from_name | VARCHAR2(100) | 'HRMS System' |

Note: Hard-coded values; documented that they should be in SYSTEM_PARAMETERS.

---

**PROCEDURE send_notification(...) — PRAGMA AUTONOMOUS_TRANSACTION**

Parameters:
- p_recipient_emp_id IN NUMBER DEFAULT NULL
- p_recipient_email IN VARCHAR2 DEFAULT NULL
- p_type IN VARCHAR2 DEFAULT 'EMAIL'
- p_subject IN VARCHAR2
- p_body IN CLOB
- p_priority IN NUMBER DEFAULT 5
- p_reference_table IN VARCHAR2 DEFAULT NULL
- p_reference_id IN NUMBER DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. PRAGMA AUTONOMOUS_TRANSACTION
2. Resolve email: if p_recipient_email IS NULL AND p_recipient_emp_id IS NOT NULL: SELECT EMAIL INTO v_email FROM EMPLOYEES WHERE EMP_ID = p_recipient_emp_id; EXCEPTION WHEN NO_DATA_FOUND: v_email := NULL
3. Else: v_email := p_recipient_email
4. INSERT INTO NOTIFICATION_QUEUE (NOTIFICATION_ID, RECIPIENT_EMP_ID, RECIPIENT_EMAIL, NOTIFICATION_TYPE, SUBJECT, BODY, STATUS, PRIORITY, REFERENCE_TABLE, REFERENCE_ID, CREATED_BY, CREATED_DATE) VALUES (SEQ_NOTIFICATION.NEXTVAL, ..., 'PENDING', p_priority, ...)
5. COMMIT
6. EXCEPTION WHEN OTHERS: ROLLBACK; PKG_COMMON.log_error — notification failures never block business operations

Business rules:
- Email resolved from EMPLOYEES table if not provided directly.
- Notification is async — written to queue with STATUS='PENDING'.
- Errors are silently swallowed (autonomous transaction rolls back; main transaction unaffected).
- Default priority: 5.

Sequences: SEQ_NOTIFICATION
Database tables read: EMPLOYEES (EMAIL)
Database tables written: NOTIFICATION_QUEUE
External services: PKG_COMMON.log_error

---

**PROCEDURE process_queue(p_batch_size NUMBER DEFAULT 50, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. Cursor: SELECT NOTIFICATION_ID, RECIPIENT_EMAIL, SUBJECT, BODY, NOTIFICATION_TYPE FROM NOTIFICATION_QUEUE WHERE STATUS='PENDING' AND NOTIFICATION_TYPE='EMAIL' AND RECIPIENT_EMAIL IS NOT NULL ORDER BY PRIORITY ASC, CREATED_DATE ASC FETCH FIRST p_batch_size ROWS ONLY
2. For each notification:
   a. v_connection := UTL_SMTP.OPEN_CONNECTION('smtp.internal.company.com', 25)
   b. UTL_SMTP.HELO(v_connection, 'smtp.internal.company.com')
   c. UTL_SMTP.MAIL(v_connection, 'hrms-noreply@company.com')
   d. UTL_SMTP.RCPT(v_connection, RECIPIENT_EMAIL)
   e. UTL_SMTP.OPEN_DATA(v_connection)
   f. Write headers:
      - 'From: HRMS System <hrms-noreply@company.com>' + CRLF
      - 'To: ' + RECIPIENT_EMAIL + CRLF
      - 'Subject: ' + SUBJECT + CRLF
      - 'Content-Type: text/plain; charset=UTF-8' + CRLF
      - CRLF (blank line)
   g. Write body
   h. UTL_SMTP.CLOSE_DATA; UTL_SMTP.QUIT
   i. UPDATE NOTIFICATION_QUEUE SET STATUS='SENT', SENT_DATE=SYSDATE WHERE NOTIFICATION_ID=...
   j. v_sent := v_sent + 1
   k. EXCEPTION WHEN OTHERS: UPDATE NOTIFICATION_QUEUE SET STATUS='FAILED', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000), RETRY_COUNT=RETRY_COUNT+1; v_failed++; try UTL_SMTP.QUIT
3. COMMIT
4. Log if sent > 0 OR failed > 0 via PKG_COMMON.log_info

Business rules:
- Batch size default: 50 records per invocation.
- Only EMAIL type with non-null RECIPIENT_EMAIL are processed.
- Priority order: lower number = higher priority (ORDER BY PRIORITY ASC).
- Within same priority: oldest first (CREATED_DATE ASC).
- One SMTP connection opened per message (inefficient; no connection reuse).
- Failed messages have RETRY_COUNT incremented.

External services called: UTL_SMTP (OPEN_CONNECTION, HELO, MAIL, RCPT, OPEN_DATA, WRITE_DATA, CLOSE_DATA, QUIT), UTL_TCP (CRLF constant), PKG_COMMON.log_info
Database tables written: NOTIFICATION_QUEUE

---

**PROCEDURE retry_failed(p_max_retries NUMBER DEFAULT 3, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE NOTIFICATION_QUEUE SET STATUS='PENDING', ERROR_MESSAGE=NULL WHERE STATUS='FAILED' AND RETRY_COUNT < p_max_retries
2. COMMIT

Business rule: Failed notifications with RETRY_COUNT < 3 (default) are reset to PENDING for reprocessing.

Database tables written: NOTIFICATION_QUEUE

---

**PROCEDURE cancel_notification(p_notification_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE NOTIFICATION_QUEUE SET STATUS='CANCELLED' WHERE NOTIFICATION_ID = p_notification_id AND STATUS = 'PENDING'

Business rule: Only PENDING notifications can be cancelled.

Database tables written: NOTIFICATION_QUEUE

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks ===

**Package:** HRMS.PKG_PAYROLL

**Custom Exceptions:**
| Exception Name | Error Code |
|---|---|
| e_invalid_salary | -20101 |
| e_period_closed | -20102 |
| e_run_already_paid | -20103 |
| e_calculation_error | -20104 |

**Types:**

`TYPE t_payslip_rec IS RECORD:`
- emp_id: NUMBER(10)
- emp_number: VARCHAR2(20)
- emp_name: VARCHAR2(101)
- period_name: VARCHAR2(50)
- gross_pay: NUMBER(12,2)
- total_deductions: NUMBER(12,2)
- net_pay: NUMBER(12,2)
- federal_tax: NUMBER(12,2)
- state_tax: NUMBER(12,2)
- social_security: NUMBER(12,2)
- medicare: NUMBER(12,2)
- ytd_gross: NUMBER(15,2)
- ytd_net: NUMBER(15,2)

`TYPE t_payslip_cursor IS REF CURSOR`

**Public Method Signatures:**

| Method | Kind | Parameters | Returns |
|---|---|---|---|
| create_salary_record | PROCEDURE | p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2 DEFAULT NULL, p_change_pct NUMBER DEFAULT NULL, p_currency_code VARCHAR2 DEFAULT 'USD', p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| get_current_salary | FUNCTION | p_emp_id NUMBER | NUMBER |
| get_salary_as_of | FUNCTION | p_emp_id NUMBER, p_as_of DATE | NUMBER |
| create_pay_periods | PROCEDURE | p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| close_pay_period | PROCEDURE | p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_current_period | FUNCTION | (none) | NUMBER |
| create_payroll_run | FUNCTION | p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER | NUMBER |
| calculate_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| calculate_employee_pay | PROCEDURE | p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| approve_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| reverse_payroll | PROCEDURE | p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| calculate_federal_tax | FUNCTION | p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_state_tax | FUNCTION | p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_fica | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| calculate_medicare | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| get_payslip | PROCEDURE | p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL | — |
| get_ytd_earnings | FUNCTION | p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| generate_pay_register | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |

**Dependencies:** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
**Callers:** HRMS_PAYROLL form, batch scheduler (DBMS_SCHEDULER)

**Known issues documented:**
- Circular dependency with PKG_EMPLOYEE (is_active check)
- Tax calculation uses hard-coded 2024 brackets in some paths
- Overtime calculation does not account for holidays correctly
- YTD accumulation resets incorrectly for mid-year hires in some edge cases

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb ===

**Package:** HRMS.PKG_PAYROLL (body)

**Private Constants:**
| Constant | Type | Value | Description |
|---|---|---|---|
| c_ss_wage_base_2024 | NUMBER | 168600 | Social Security wage base (2024) |
| c_ss_rate | NUMBER | 0.062 | Employee SS share: 6.2% |
| c_medicare_rate | NUMBER | 0.0145 | Employee Medicare share: 1.45% |
| c_medicare_addl_rate | NUMBER | 0.009 | Additional Medicare tax: 0.9% |
| c_medicare_addl_threshold | NUMBER | 200000 | Threshold for additional Medicare tax |
| c_standard_deduction_single | NUMBER | 14600 | 2024 standard deduction — single/separate |
| c_standard_deduction_married | NUMBER | 29200 | 2024 standard deduction — married filing jointly |
| c_allowance_amount | NUMBER | 4300 | Per-allowance reduction amount |

---

**PROCEDURE create_salary_record(...)**

Parameters:
- p_emp_id IN NUMBER
- p_effective_date IN DATE
- p_base_salary IN NUMBER
- p_change_reason IN VARCHAR2 DEFAULT NULL
- p_change_pct IN NUMBER DEFAULT NULL
- p_currency_code IN VARCHAR2 DEFAULT 'USD'
- p_pay_frequency IN VARCHAR2 DEFAULT 'MONTHLY'
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. IF p_base_salary <= 0: RAISE_APPLICATION_ERROR(-20101, 'Salary must be positive: ' || p_base_salary)
2. UPDATE SALARY_RECORDS SET END_DATE = p_effective_date - 1, ACTIVE_FLAG = 'N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y' AND EFFECTIVE_DATE < p_effective_date
3. INSERT INTO SALARY_RECORDS (SALARY_ID, EMP_ID, EFFECTIVE_DATE, BASE_SALARY, CURRENCY_CODE, PAY_FREQUENCY, SALARY_BASIS, CHANGE_REASON, CHANGE_PCT, ACTIVE_FLAG, CREATED_BY, CREATED_DATE) VALUES (SEQ_SALARY.NEXTVAL, p_emp_id, p_effective_date, p_base_salary, p_currency_code, p_pay_frequency, 'ANNUAL', p_change_reason, p_change_pct, 'Y', p_user, SYSDATE)
4. PKG_AUDIT.log_action('SALARY_RECORDS', SEQ_SALARY.CURRVAL, 'INSERT', p_user)

Business rules:
- Salary must be positive (> 0).
- Previous active salary end-dated to p_effective_date - 1.
- SALARY_BASIS always stored as 'ANNUAL'.
- Default currency: 'USD'. Default frequency: 'MONTHLY'.

Exceptions: -20101 — salary must be positive

Sequences: SEQ_SALARY
Database tables written: SALARY_RECORDS
External services: PKG_AUDIT.log_action

---

**FUNCTION get_current_salary(p_emp_id NUMBER) RETURN NUMBER**

Logic:
1. SELECT BASE_SALARY FROM SALARY_RECORDS WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y' AND EFFECTIVE_DATE <= SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. EXCEPTION WHEN NO_DATA_FOUND: RETURN 0

Database tables read: SALARY_RECORDS

---

**FUNCTION get_salary_as_of(p_emp_id NUMBER, p_as_of DATE) RETURN NUMBER**

Logic:
1. SELECT BASE_SALARY FROM SALARY_RECORDS WHERE EMP_ID = p_emp_id AND EFFECTIVE_DATE <= p_as_of AND (END_DATE IS NULL OR END_DATE >= p_as_of) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. EXCEPTION WHEN NO_DATA_FOUND: RETURN 0

Database tables read: SALARY_RECORDS

---

**PROCEDURE create_pay_periods(p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER)**

Logic — MONTHLY branch:
- Loop i IN 1..12:
  - v_start_date := TO_DATE(p_year || '-' || LPAD(i, 2, '0') || '-01', 'YYYY-MM-DD')
  - v_end_date := LAST_DAY(v_start_date)
  - v_pay_date := v_end_date
  - If pay date = SAT: v_pay_date := v_pay_date - 1 (move to Friday)
  - If pay date = SUN: v_pay_date := v_pay_date - 2 (move to Friday)
  - v_period_num := v_period_num + 1
  - INSERT INTO PAY_PERIODS (PERIOD_ID, PERIOD_NAME, PAY_FREQUENCY, PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE, STATUS, CREATED_BY, CREATED_DATE)
    - PERIOD_NAME = '<year>-<MM> (<Mon>)'
    - STATUS = 'OPEN'

Logic — BIWEEKLY branch:
- Start from Jan 1 of year; advance to first Friday of year
- Back up 13 days to start of that pay period (v_start_date := first_friday - 13)
- Loop while EXTRACT(YEAR FROM v_start_date) <= p_year:
  - v_end_date := v_start_date + 13 (14-day period: days 0-13)
  - v_pay_date := v_end_date + 5 (pay 5 days after period end)
  - v_period_num := v_period_num + 1
  - Insert if start or end is in target year:
    - PERIOD_NAME = '<year>-BW-<NN>'
    - STATUS = 'OPEN'
  - v_start_date := v_end_date + 1
- COMMIT at end

Business rules:
- Monthly periods: pay date = last day of month, adjusted to Friday if weekend.
- Biweekly periods: 14-day periods, pay date = period end + 5 days.
- All new periods start with STATUS = 'OPEN'.

Sequences: SEQ_PAY_PERIOD
Database tables written: PAY_PERIODS

---

**PROCEDURE close_pay_period(p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT STATUS FROM PAY_PERIODS WHERE PERIOD_ID = p_period_id FOR UPDATE
2. IF STATUS = 'CLOSED': RAISE_APPLICATION_ERROR(-20102, 'Period already closed: ' || p_period_id)
3. UPDATE PAY_PERIODS SET STATUS='CLOSED', CLOSED_BY=p_user, CLOSED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE PERIOD_ID=p_period_id

Exceptions: -20102 — period already closed

Database tables written: PAY_PERIODS

---

**FUNCTION get_current_period RETURN NUMBER**

Logic:
1. SELECT PERIOD_ID FROM PAY_PERIODS WHERE SYSDATE BETWEEN PERIOD_START_DATE AND PERIOD_END_DATE AND STATUS = 'OPEN' AND ROWNUM = 1
2. EXCEPTION WHEN NO_DATA_FOUND: RETURN NULL

Database tables read: PAY_PERIODS

---

**FUNCTION create_payroll_run(p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER) RETURN NUMBER**

Logic:
1. SELECT STATUS FROM PAY_PERIODS WHERE PERIOD_ID = p_period_id
2. IF STATUS = 'CLOSED': RAISE_APPLICATION_ERROR(-20102, 'Cannot create run for closed period: ' || p_period_id)
3. SELECT SEQ_PAYROLL_RUN.NEXTVAL INTO v_run_id FROM DUAL
4. INSERT INTO PAYROLL_RUNS (RUN_ID, PERIOD_ID, RUN_TYPE, RUN_DATE, STATUS, SUBMITTED_BY, SUBMITTED_DATE, CREATED_BY, CREATED_DATE) VALUES (v_run_id, p_period_id, p_run_type, SYSDATE, 'PENDING', p_user, SYSDATE, p_user, SYSDATE)
5. RETURN v_run_id

Exceptions: -20102 — cannot create run for closed period

Sequences: SEQ_PAYROLL_RUN
Database tables read: PAY_PERIODS
Database tables written: PAYROLL_RUNS

---

**PROCEDURE calculate_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT PERIOD_ID, RUN_TYPE FROM PAYROLL_RUNS WHERE RUN_ID = p_run_id
2. UPDATE PAYROLL_RUNS SET STATUS='CALCULATING' WHERE RUN_ID=p_run_id; COMMIT
3. Cursor loop (documented bug: should use BULK COLLECT + FORALL):
   SELECT e.EMP_ID FROM EMPLOYEES e WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.ACTIVE_FLAG = 'Y' ORDER BY e.EMP_ID
4. For each employee: call calculate_employee_pay(p_run_id, emp_rec.EMP_ID, v_period_id, p_user)
   - EXCEPTION WHEN OTHERS: INSERT error record into PAYROLL_DETAILS (ELEMENT_ID=0, ELEMENT_TYPE='ERROR', AMOUNT=0, STATUS='ERROR', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000)); v_error_count++
5. COMMIT every 50 employees (MOD(v_emp_count, 50) = 0)
   - Documented issue: partial commits mean failure leaves payroll half-calculated
6. UPDATE PAYROLL_RUNS SET:
   - STATUS = CASE WHEN v_error_count > 0 THEN 'ERROR' ELSE 'CALCULATED' END
   - EMPLOYEE_COUNT = v_emp_count
   - ERROR_COUNT = v_error_count
   - TOTAL_GROSS = SUM of PAYROLL_DETAILS WHERE ELEMENT_TYPE='EARNING' AND STATUS!='ERROR'
   - TOTAL_DEDUCTIONS = SUM of ABS(AMOUNT) WHERE ELEMENT_TYPE IN ('DEDUCTION','TAX') AND STATUS!='ERROR'
   - TOTAL_NET = SUM of CASE WHEN EARNING THEN AMOUNT WHEN DEDUCTION/TAX THEN -ABS(AMOUNT) ELSE 0 END WHERE STATUS!='ERROR'
7. COMMIT

Business rules:
- All ACTIVE + ACTIVE_FLAG='Y' employees are processed.
- Individual employee errors are recorded but do not stop the run.
- Run status = 'ERROR' if any employee failed; 'CALCULATED' if all succeeded.

Database tables read: PAYROLL_RUNS, EMPLOYEES
Database tables written: PAYROLL_RUNS, PAYROLL_DETAILS
External services: calculate_employee_pay (internal)

---

**PROCEDURE calculate_employee_pay(p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT PERIOD_START_DATE, PERIOD_END_DATE, PAY_FREQUENCY FROM PAY_PERIODS WHERE PERIOD_ID = p_period_id
2. Determine v_periods_per_year:
   | PAY_FREQUENCY | v_periods_per_year |
   |---|---|
   | 'WEEKLY' | 52 |
   | 'BIWEEKLY' | 26 |
   | 'SEMIMONTHLY' | 24 |
   | 'MONTHLY' | 12 |
   | default | 12 |
3. v_annual_salary := get_salary_as_of(p_emp_id, v_period_end)
4. IF v_annual_salary = 0: RAISE_APPLICATION_ERROR(-20104, 'No active salary record for employee ' || p_emp_id)
5. v_period_gross := ROUND(v_annual_salary / v_periods_per_year, 2)
6. INSERT PAYROLL_DETAILS: ELEMENT_ID=1, ELEMENT_TYPE='EARNING', AMOUNT=v_period_gross, STATUS='CALCULATED'
7. v_ytd_gross := get_ytd_earnings(p_emp_id, EXTRACT(YEAR FROM v_period_end))
8. Get tax info from EMPLOYEE_TAX_INFO WHERE EMP_ID=p_emp_id AND TAX_YEAR=EXTRACT(YEAR FROM v_period_end) AND ACTIVE_FLAG='Y'
   - Fields: FILING_STATUS, FEDERAL_ALLOWANCES, STATE_CODE, STATE_ALLOWANCES, ADDITIONAL_FED_WH
   - EXCEPTION WHEN NO_DATA_FOUND: defaults: FILING_STATUS='SINGLE', FEDERAL_ALLOWANCES=0, STATE_CODE=NULL, STATE_ALLOWANCES=0, ADDITIONAL_FED_WH=0
9. v_taxable_income := v_period_gross (simplified — does not subtract pretax deductions)
10. v_federal_tax := calculate_federal_tax(v_taxable_income, v_filing_status, v_fed_allowances, v_addl_fed_wh, v_pay_frequency)
11. If v_federal_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=100, ELEMENT_TYPE='TAX', AMOUNT=-v_federal_tax
12. If v_state_code IS NOT NULL:
    - v_state_tax := calculate_state_tax(v_taxable_income, v_state_code, v_filing_status, v_state_allowances, v_pay_frequency)
    - If v_state_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=101, ELEMENT_TYPE='TAX', AMOUNT=-v_state_tax
13. v_ss_tax := calculate_fica(v_period_gross, v_ytd_gross)
    - If v_ss_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=102, ELEMENT_TYPE='TAX', AMOUNT=-v_ss_tax
14. v_medicare_tax := calculate_medicare(v_period_gross, v_ytd_gross)
    - If v_medicare_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=103, ELEMENT_TYPE='TAX', AMOUNT=-v_medicare_tax
15. Deductions loop: SELECT FROM EMPLOYEE_PAY_ELEMENTS epe JOIN PAY_ELEMENTS pe WHERE epe.EMP_ID=p_emp_id AND epe.ACTIVE_FLAG='Y' AND pe.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') AND epe.EFFECTIVE_DATE <= v_period_end AND (epe.END_DATE IS NULL OR epe.END_DATE >= v_period_start) ORDER BY pe.PRIORITY_ORDER
    - For each: calculate v_ded_amount:
      - If OVERRIDE_AMOUNT IS NOT NULL: v_ded_amount := OVERRIDE_AMOUNT
      - Elif CALCULATION_TYPE = 'FLAT': v_ded_amount := NVL(AMOUNT, DEFAULT_AMOUNT)
      - Elif CALCULATION_TYPE = 'PERCENTAGE': v_ded_amount := ROUND(v_period_gross * NVL(PERCENTAGE, DEFAULT_PERCENTAGE) / 100, 2)
      - Else: v_ded_amount := NVL(AMOUNT, 0)
    - If v_ded_amount > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=ded_rec.ELEMENT_ID, ELEMENT_TYPE=ded_rec.ELEMENT_TYPE, AMOUNT=-v_ded_amount
16. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error; RAISE

**PAYROLL_DETAILS ELEMENT_ID assignments (hard-coded):**
| ELEMENT_ID | Type | Description |
|---|---|---|
| 1 | EARNING | Base gross pay |
| 0 | ERROR | Error placeholder |
| 100 | TAX | Federal income tax |
| 101 | TAX | State income tax |
| 102 | TAX | Social Security (FICA) |
| 103 | TAX | Medicare |

Business rules:
- No active salary = error, stops employee processing.
- W-4 defaults if no EMPLOYEE_TAX_INFO on file: SINGLE, 0 allowances, no additional withholding.
- Taxable income simplified to gross (pretax deductions NOT subtracted — documented simplification).
- Deductions applied in PRIORITY_ORDER.
- Override amount takes precedence over all other calculation methods.
- Deduction amounts stored as negative values in PAYROLL_DETAILS.

Exceptions: -20104 — no active salary record

Database tables read: PAY_PERIODS, SALARY_RECORDS (via get_salary_as_of), EMPLOYEE_TAX_INFO, EMPLOYEE_PAY_ELEMENTS, PAY_ELEMENTS
Database tables written: PAYROLL_DETAILS
External services: PKG_COMMON.log_error

---

**PROCEDURE approve_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT STATUS FROM PAYROLL_RUNS WHERE RUN_ID = p_run_id FOR UPDATE
2. IF STATUS NOT IN ('CALCULATED'): RAISE_APPLICATION_ERROR(-20103, 'Cannot approve run in status: ' || v_status)
3. UPDATE PAYROLL_RUNS SET STATUS='APPROVED', APPROVED_BY=p_user, APPROVED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE

Business rule: Only CALCULATED runs can be approved.

Exceptions: -20103 — run not in CALCULATED status

Database tables written: PAYROLL_RUNS

---

**PROCEDURE reverse_payroll(p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PAYROLL_RUNS SET STATUS='REVERSED', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE RUN_ID=p_run_id
2. UPDATE PAYROLL_DETAILS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id
3. PKG_AUDIT.log_action('PAYROLL_RUNS', p_run_id, 'UPDATE', p_user)

Database tables written: PAYROLL_RUNS, PAYROLL_DETAILS
External services: PKG_AUDIT.log_action

---

**FUNCTION calculate_federal_tax(p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER**

Logic:
1. Determine v_periods:
   | p_pay_frequency | v_periods |
   |---|---|
   | 'WEEKLY' | 52 |
   | 'BIWEEKLY' | 26 |
   | 'SEMIMONTHLY' | 24 |
   | 'MONTHLY' | 12 |
   | default | 12 |
2. v_annualized := p_taxable_income * v_periods
3. v_std_deduction := 29200 if p_filing_status = 'MARRIED_JOINT'; else 14600
4. v_taxable := v_annualized - v_std_deduction - (p_allowances * 4300)
5. IF v_taxable <= 0: RETURN 0
6. Apply 2024 tax brackets:

   **SINGLE or MARRIED_SEPARATE:**
   | Bracket | Annual Taxable Income Range | Tax Calculation |
   |---|---|---|
   | 1 | 0 – 11,600 | v_taxable * 0.10 |
   | 2 | 11,600.01 – 47,150 | 1,160 + (v_taxable - 11,600) * 0.12 |
   | 3 | 47,150.01 – 100,525 | 5,426 + (v_taxable - 47,150) * 0.22 |
   | 4 | 100,525.01 – 191,950 | 17,168.50 + (v_taxable - 100,525) * 0.24 |
   | 5 | 191,950.01 – 243,725 | 39,110.50 + (v_taxable - 191,950) * 0.32 |
   | 6 | 243,725.01 – 609,350 | 55,678.50 + (v_taxable - 243,725) * 0.35 |
   | 7 | > 609,350 | 183,647.25 + (v_taxable - 609,350) * 0.37 |

   **MARRIED_JOINT:**
   | Bracket | Annual Taxable Income Range | Tax Calculation |
   |---|---|---|
   | 1 | 0 – 23,200 | v_taxable * 0.10 |
   | 2 | 23,200.01 – 94,300 | 2,320 + (v_taxable - 23,200) * 0.12 |
   | 3 | 94,300.01 – 201,050 | 10,852 + (v_taxable - 94,300) * 0.22 |
   | 4 | 201,050.01 – 383,900 | 34,337 + (v_taxable - 201,050) * 0.24 |
   | 5 | 383,900.01 – 487,450 | 78,221 + (v_taxable - 383,900) * 0.32 |
   | 6 | 487,450.01 – 731,200 | 111,357 + (v_taxable - 487,450) * 0.35 |
   | 7 | > 731,200 | 196,669.50 + (v_taxable - 731,200) * 0.37 |

7. v_tax := ROUND(v_tax / v_periods, 2) — convert annual tax back to per-period
8. v_tax := v_tax + NVL(p_additional_wh, 0) — add additional withholding
9. RETURN v_tax

Business rules:
- Income annualized before bracket lookup.
- Standard deduction subtracted: 14,600 (single/separate), 29,200 (married joint).
- Each W-4 allowance reduces taxable income by 4,300.
- Brackets are hard-coded 2024 values.
- Head-of-household and other filing statuses not modeled (fall into single/default path or no branch matches → v_tax remains 0).

---

**FUNCTION calculate_state_tax(p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER**

Logic: Flat rate lookup by state code (simplified; documented as not bracket-based):

| State Code | Rate |
|---|---|
| 'CA' | 0.0725 (7.25%) |
| 'NY' | 0.0685 (6.85%) |
| 'TX' | 0 (no state income tax) |
| 'FL' | 0 (no state income tax) |
| 'WA' | 0 (no state income tax) |
| 'IL' | 0.0495 (4.95%) |
| 'PA' | 0.0307 (3.07%) |
| 'OH' | 0.04 (4.00%) |
| 'NJ' | 0.0637 (6.37%) |
| 'MA' | 0.05 (5.00%) |
| default (any other state) | 0.05 (5.00%) |

Returns: ROUND(p_taxable_income * v_rate, 2)

Business rule: p_filing_status and p_allowances are accepted parameters but NOT used in the calculation (flat rate only).

---

**FUNCTION calculate_fica(p_gross_pay NUMBER, p_ytd_gross NUMBER) RETURN NUMBER**

Logic:
1. IF p_ytd_gross >= 168600: RETURN 0 (already exceeded 2024 SS wage base)
2. v_taxable := LEAST(p_gross_pay, 168600 - p_ytd_gross) — cap at remaining wage base
3. RETURN ROUND(v_taxable * 0.062, 2)

Business rules:
- 2024 Social Security wage base: 168,600
- Employee SS rate: 6.2%
- No SS tax once YTD exceeds 168,600.
- Partial period calculation when crossing the wage base.

---

**FUNCTION calculate_medicare(p_gross_pay NUMBER, p_ytd_gross NUMBER) RETURN NUMBER**

Logic:
1. v_base_tax := ROUND(p_gross_pay * 0.0145, 2)
2. Additional Medicare (0.9%) on high earners:
   - IF p_ytd_gross + p_gross_pay > 200,000 THEN:
     - IF p_ytd_gross >= 200,000: v_addl_tax := ROUND(p_gross_pay * 0.009, 2) — full period above threshold
     - ELSE: v_addl_tax := ROUND((p_ytd_gross + p_gross_pay - 200,000) * 0.009, 2) — partial period crossing threshold
   - ELSE: v_addl_tax := 0
3. RETURN v_base_tax + v_addl_tax

Business rules:
- Base Medicare rate: 1.45% on all wages (no wage base cap).
- Additional Medicare rate: 0.9% on wages exceeding 200,000 YTD.
- Partial period calculation when crossing the 200,000 threshold.

---

**PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL)**

Logic: Opens ref cursor with aggregation query:
```sql
SELECT pd.EMP_ID, e.EMP_NUMBER,
       e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME,
       pp.PERIOD_NAME,
       SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY,
       SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','TAX','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS,
       SUM(pd.AMOUNT) AS NET_PAY,
       SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX,
       SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX,
       SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY,
       SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE,
       0 AS YTD_GROSS,  -- Placeholder (not calculated)
       0 AS YTD_NET     -- Placeholder (not calculated)
FROM PAYROLL_DETAILS pd
JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID
WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR'
AND (p_emp_id IS NULL OR pd.EMP_ID = p_emp_id)
GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME
ORDER BY e.LAST_NAME
```

Note: YTD_GROSS and YTD_NET are hard-coded 0 (placeholders, not implemented).

Database tables read: PAYROLL_DETAILS, EMPLOYEES, PAYROLL_RUNS, PAY_PERIODS

---

**FUNCTION get_ytd_earnings(p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
1. SELECT NVL(SUM(pd.AMOUNT), 0) FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.EMP_ID = p_emp_id AND pd.ELEMENT_TYPE = 'EARNING' AND pd.STATUS = 'CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
2. RETURN v_ytd

Database tables read: PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS

---

**PROCEDURE generate_pay_register(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT pp.PERIOD_NAME FROM PAYROLL_RUNS pr JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pr.RUN_ID = p_run_id
2. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS') || '.csv'
3. Open UTL_FILE in directory 'PAYROLL_OUTPUT', mode 'W', buffer 32767
4. Write CSV header: 'EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY'
5. Detail query (aggregated per employee):
   ```sql
   SELECT e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME,
          d.DEPT_NAME,
          SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS,
          SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FED,
          SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE,
          SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SS,
          SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MED,
          SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS DEDS,
          SUM(pd.AMOUNT) AS NET
   FROM PAYROLL_DETAILS pd
   JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
   JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
   WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR'
   GROUP BY e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, d.DEPT_NAME
   ORDER BY e.LAST_NAME
   ```
6. Each line: EMP_NUMBER,"EMPLOYEE_NAME","DEPT_NAME",GROSS,FED,STATE,SS,MED,DEDS,NET — amounts with TO_CHAR format 'FM999999990.00'
7. Close file; DBMS_OUTPUT.PUT_LINE('Pay register generated: ' || v_filename)
8. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

Note: TAX-type amounts (ELEMENT_ID 100-103) are excluded from the DEDS column in the register; DEDS only covers DEDUCTION and BENEFIT types.

Oracle directory object used: 'PAYROLL_OUTPUT'

Database tables read: PAYROLL_RUNS, PAY_PERIODS, PAYROLL_DETAILS, EMPLOYEES, DEPARTMENTS
External file I/O: UTL_FILE write to Oracle directory 'PAYROLL_OUTPUT'
External services: PKG_COMMON.log_error, DBMS_OUTPUT.PUT_LINE

---

**Summary of all database tables referenced across all files:**

| Table | Operations |
|---|---|
| EMPLOYEES | SELECT, INSERT, UPDATE |
| EMPLOYEE_HISTORY | INSERT |
| EMPLOYEE_DEPENDENTS | SELECT |
| EMPLOYEE_TAX_INFO | SELECT |
| EMPLOYEE_PAY_ELEMENTS | SELECT, UPDATE |
| DEPARTMENTS | SELECT |
| JOB_TITLES | SELECT |
| JOB_GRADES | SELECT |
| SALARY_RECORDS | SELECT, INSERT, UPDATE |
| LEAVE_REQUESTS | SELECT, INSERT, UPDATE |
| LEAVE_BALANCES | SELECT, INSERT, UPDATE |
| LEAVE_TYPES | SELECT |
| LEAVE_ACCRUAL_LOG | INSERT |
| HOLIDAYS | SELECT |
| PAYROLL_RUNS | SELECT, INSERT, UPDATE |
| PAYROLL_DETAILS | SELECT, INSERT, UPDATE |
| PAY_PERIODS | SELECT, INSERT, UPDATE |
| PAY_ELEMENTS | SELECT |
| NOTIFICATION_QUEUE | SELECT, INSERT, UPDATE |

**Summary of all sequences referenced:**

| Sequence | Used In |
|---|---|
| SEQ_EMPLOYEE | generate_emp_number, get_next_emp_id |
| SEQ_EMP_HISTORY | log_history |
| SEQ_LEAVE_REQUEST | submit_leave_request |
| SEQ_LEAVE_BALANCE | initialize_balances |
| SEQ_LEAVE_ACCRUAL | run_monthly_accrual |
| SEQ_SALARY | create_salary_record |
| SEQ_PAY_PERIOD | create_pay_periods |
| SEQ_PAYROLL_RUN | create_payroll_run |
| SEQ_PAYROLL_DETAIL | calculate_employee_pay, calculate_payroll |
| SEQ_NOTIFICATION | send_notification |

**Summary of all external packages/services called:**

| Package | Methods Called From |
|---|---|
| PKG_PAYROLL.create_salary_record | PKG_EMPLOYEE (create_employee, promote_employee, rehire_employee) |
| PKG_AUDIT.log_action | PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL (many procedures) |
| PKG_NOTIFICATION.send_notification | PKG_EMPLOYEE (create_employee, terminate_employee), PKG_LEAVE (submit, approve, reject) |
| PKG_COMMON.log_error | PKG_EMPLOYEE, PKG_INTEGRATION, PKG_LEAVE (none direct), PKG_PAYROLL, PKG_NOTIFICATION |
| PKG_COMMON.log_info | PKG_INTEGRATION, PKG_NOTIFICATION |
| PKG_COMMON.get_param | PKG_INTEGRATION.get_integration_status |
| UTL_FILE | PKG_INTEGRATION (generate_gl_journal, export_benefits_feed, import_time_attendance), PKG_PAYROLL (generate_pay_register) |
| UTL_SMTP | PKG_NOTIFICATION.process_queue |
| UTL_TCP | PKG_NOTIFICATION.process_queue (CRLF constant) |
| DBMS_OUTPUT | PKG_LEAVE.run_monthly_accrual, PKG_PAYROLL.generate_pay_register, PKG_EMPLOYEE.log_history (debug) |


=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks ===

**Package:** HRMS.PKG_SECURITY
**Schema:** HRMS
**Type:** Package Specification (header only; body not provided)

**Purpose:** Authentication, authorization, session management, role-based access, encryption.

**Dependencies:**
- PKG_COMMON (referenced in comments)
- PKG_AUDIT (referenced in comments)

**Called By:**
- HRMS_LOGIN form
- All forms (session validation)

---

**Known Issues / Constraints (from inline comments):**
- Password stored as MD5 hash (should be bcrypt/scrypt)
- Session timeout check uses DB server time, not application server time
- No account lockout after failed attempts
- DBMS_CRYPTO key hard-coded in package body

---

**Custom Exceptions:**

| Exception Name          | Error Code | PRAGMA Init |
|-------------------------|------------|-------------|
| e_invalid_credentials   | -20301     | Yes         |
| e_account_locked        | -20302     | Yes         |
| e_session_expired       | -20303     | Yes         |
| e_insufficient_priv     | -20304     | Yes         |

---

**Functions and Procedures:**

1. `FUNCTION authenticate(p_username IN VARCHAR2, p_password IN VARCHAR2, p_ip_address IN VARCHAR2 DEFAULT NULL) RETURN NUMBER`
   - Authenticates user by username/password; optionally records IP address; returns a session identifier (NUMBER)

2. `PROCEDURE logout(p_session_id IN NUMBER)`
   - Terminates the session identified by p_session_id

3. `FUNCTION is_session_valid(p_session_id IN NUMBER) RETURN BOOLEAN`
   - Returns TRUE if the given session is still active/not expired

4. `FUNCTION has_permission(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN`
   - Returns TRUE if the employee has the requested permission on the given module
   - Default action is 'VIEW'

5. `FUNCTION encrypt_ssn(p_ssn IN VARCHAR2) RETURN VARCHAR2`
   - Encrypts a plain-text SSN; returns encrypted VARCHAR2

6. `FUNCTION decrypt_ssn(p_encrypted IN VARCHAR2) RETURN VARCHAR2`
   - Decrypts an encrypted SSN; returns plain-text VARCHAR2

7. `FUNCTION hash_password(p_password IN VARCHAR2) RETURN VARCHAR2`
   - Returns a hash (MD5 per known issue) of the plain-text password

8. `PROCEDURE change_password(p_emp_id IN NUMBER, p_old_password IN VARCHAR2, p_new_password IN VARCHAR2)`
   - Changes the employee's password after verifying the old password

---

**External Packages Referenced:**
- DBMS_CRYPTO (body; key hard-coded)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb ===

**Package:** HRMS.PKG_VALIDATION
**Type:** Package Body

**Dependencies:**
- PKG_COMMON (called for email/phone validation)
- Tables: JOB_GRADES, EMPLOYEES, HOLIDAYS

---

**Function: validate_date_range**
```
FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN
```
Logic:
- IF p_start_date IS NULL OR p_end_date IS NULL → RETURN FALSE
- RETURN p_end_date >= p_start_date

Business Rule: Both dates required; end date must be on or after start date.

---

**Function: validate_salary_for_grade**
```
FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2
```
Logic:
- IF p_salary IS NULL OR p_grade_id IS NULL → RETURN 'Salary and grade are required'
- SELECT MIN_SALARY, MAX_SALARY, GRADE_NAME FROM JOB_GRADES WHERE GRADE_ID = p_grade_id
- IF p_salary < v_min → RETURN 'Salary ' || formatted_salary || ' is below minimum for grade ' || v_grade_name || ' (' || formatted_min || ')'
- ELSIF p_salary > v_max → RETURN 'Salary ' || formatted_salary || ' exceeds maximum for grade ' || v_grade_name || ' (' || formatted_max || ')'
- RETURN NULL (valid)
- EXCEPTION WHEN NO_DATA_FOUND → RETURN 'Invalid grade ID: ' || p_grade_id

Number format mask used: `'FM$999,999,990.00'`

Tables accessed: JOB_GRADES (columns: MIN_SALARY, MAX_SALARY, GRADE_NAME, GRADE_ID)

Business Rule: Salary must be within the min/max band defined in JOB_GRADES for the given grade.

---

**Function: validate_email_format**
```
FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN
```
Logic: Delegates entirely to PKG_COMMON.is_valid_email(p_email)

---

**Function: validate_phone_format**
```
FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN
```
Logic: Delegates entirely to PKG_COMMON.is_valid_phone(p_phone)

---

**Function: validate_emp_number_format**
```
FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN
```
Logic: RETURN REGEXP_LIKE(p_emp_number, '^EMP-\d{6}$')

Business Rule: Employee number must exactly match the pattern `EMP-` followed by exactly 6 digits. Example valid value: `EMP-001234`.

---

**Function: is_future_date**
```
FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN
```
Logic: RETURN TRUNC(p_date) > TRUNC(SYSDATE)

Business Rule: A date is "future" only if its truncated (time-stripped) value is strictly greater than today.

---

**Function: is_business_day**
```
FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN
```
Logic:
1. v_day := TO_CHAR(p_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN')
2. IF v_day IN ('SAT', 'SUN') → RETURN FALSE
3. SELECT COUNT(*) FROM HOLIDAYS WHERE HOLIDAY_DATE = TRUNC(p_date) AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)
4. RETURN v_holiday_count = 0

Tables accessed: HOLIDAYS (columns: HOLIDAY_DATE, ACTIVE_FLAG, LOCATION_CODE)

Business Rules:
- Saturday and Sunday are never business days.
- Any active holiday matching the date (either global or matching the provided location code) is not a business day.
- Location-specific holidays override nothing — both global (LOCATION_CODE IS NULL) and location-specific holidays are checked.

---

**Function: validate_required_fields**
```
FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2
```
Logic (for p_table_name = 'EMPLOYEES'):
- SELECT * FROM EMPLOYEES WHERE EMP_ID = p_record_id into v_rec
- IF v_rec.FIRST_NAME IS NULL → RETURN 'First Name is required'
- IF v_rec.LAST_NAME IS NULL → RETURN 'Last Name is required'
- IF v_rec.HIRE_DATE IS NULL → RETURN 'Hire Date is required'
- IF v_rec.DEPT_ID IS NULL → RETURN 'Department is required'
- IF v_rec.JOB_ID IS NULL → RETURN 'Job Title is required'
- EXCEPTION WHEN NO_DATA_FOUND → RETURN 'Record not found'
- RETURN NULL (all required fields populated)

Comment: "Simplified validation — in production would use data dictionary to check NOT NULL columns"
Only the EMPLOYEES table case is currently implemented.

Tables accessed: EMPLOYEES (columns: EMP_ID, FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID)

Business Rules for EMPLOYEES required fields: FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID are all mandatory.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pks ===

**Package:** HRMS.PKG_VALIDATION
**Type:** Package Specification

**Dependencies:** PKG_COMMON

**Called By:** All forms (WHEN-VALIDATE-ITEM triggers), PKG_EMPLOYEE, PKG_PAYROLL

**Functions Declared:**

1. `FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN`

2. `FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2`
   - Returns NULL if valid; error message string if invalid

3. `FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN`

4. `FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN`

5. `FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN`

6. `FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN`

7. `FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN`

8. `FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2`
   - Returns NULL if all required fields populated; error message otherwise

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql ===

**File Type:** Database Triggers (3 triggers)

---

**Trigger: TRG_SALARY_AUDIT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_SALARY_AUDIT
AFTER INSERT OR UPDATE OR DELETE ON HRMS.SALARY_RECORDS
FOR EACH ROW
```
Firing: After INSERT, UPDATE, or DELETE on HRMS.SALARY_RECORDS, for each row.

Logic:
- INSERTING:
  - v_action := 'INSERT'
  - v_new_json := `{"emp_id":<:NEW.EMP_ID>,"salary":<:NEW.BASE_SALARY>,"effective":"<:NEW.EFFECTIVE_DATE YYYY-MM-DD>"}`
- UPDATING:
  - v_action := 'UPDATE'
  - v_old_json := `{"salary":<:OLD.BASE_SALARY>,"active":"<:OLD.ACTIVE_FLAG>"}`
  - v_new_json := `{"salary":<:NEW.BASE_SALARY>,"active":"<:NEW.ACTIVE_FLAG>"}`
- DELETING:
  - v_action := 'DELETE'
  - v_old_json := `{"emp_id":<:OLD.EMP_ID>,"salary":<:OLD.BASE_SALARY>}`
- Calls: PKG_AUDIT.log_action('SALARY_RECORDS', NVL(:NEW.SALARY_ID, :OLD.SALARY_ID), v_action, NVL(:NEW.MODIFIED_BY, USER), v_old_json, v_new_json)

Tables: HRMS.SALARY_RECORDS (columns referenced: EMP_ID, SALARY_ID, BASE_SALARY, EFFECTIVE_DATE, ACTIVE_FLAG, MODIFIED_BY)

External Package Called: PKG_AUDIT.log_action

Business Rule: All salary record changes (insert, update, delete) are captured in JSON format for compliance audit trail.

---

**Trigger: TRG_LEAVE_REQUEST_AUDIT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_LEAVE_REQUEST_AUDIT
AFTER UPDATE OF STATUS ON HRMS.LEAVE_REQUESTS
FOR EACH ROW
```
Firing: After UPDATE of STATUS column only on HRMS.LEAVE_REQUESTS, for each row.

Logic:
- Calls PKG_AUDIT.log_action('LEAVE_REQUESTS', :NEW.REQUEST_ID, 'STATUS_CHANGE', NVL(:NEW.MODIFIED_BY, USER), '{"status":"<:OLD.STATUS>"}', '{"status":"<:NEW.STATUS>"}')

Tables: HRMS.LEAVE_REQUESTS (columns: REQUEST_ID, STATUS, MODIFIED_BY)

External Package Called: PKG_AUDIT.log_action

Business Rule: All leave request status changes are audited.

---

**Trigger: TRG_DEPARTMENT_AUDIT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_DEPARTMENT_AUDIT
AFTER INSERT OR UPDATE OR DELETE ON HRMS.DEPARTMENTS
FOR EACH ROW
```
Firing: After INSERT, UPDATE, or DELETE on HRMS.DEPARTMENTS, for each row.

Logic:
- INSERTING → v_action := 'INSERT'
- UPDATING → v_action := 'UPDATE'
- DELETING → v_action := 'DELETE'
- Calls PKG_AUDIT.log_action('DEPARTMENTS', NVL(:NEW.DEPT_ID, :OLD.DEPT_ID), v_action, USER)
  - Note: no old/new JSON values passed; only USER (not MODIFIED_BY) is used as the changed_by

Tables: HRMS.DEPARTMENTS (columns: DEPT_ID)

External Package Called: PKG_AUDIT.log_action

Business Rule: All department structure changes are audited.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_employees.sql ===

**File Type:** Database Triggers (3 triggers on HRMS.EMPLOYEES)

**Comment:** Logic here duplicates PKG_EMPLOYEE and Forms triggers — noted as a common anti-pattern in legacy Oracle Forms applications.

---

**Trigger: TRG_EMP_BEFORE_INSERT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_EMP_BEFORE_INSERT
BEFORE INSERT ON HRMS.EMPLOYEES
FOR EACH ROW
```
Firing: Before each INSERT on HRMS.EMPLOYEES.

Logic:
1. IF :NEW.CREATED_BY IS NULL → :NEW.CREATED_BY := USER
2. IF :NEW.CREATED_DATE IS NULL → :NEW.CREATED_DATE := SYSDATE
3. IF :NEW.ACTIVE_FLAG IS NULL → :NEW.ACTIVE_FLAG := 'Y'
4. IF :NEW.EMPLOYMENT_STATUS IS NULL → :NEW.EMPLOYMENT_STATUS := 'ACTIVE'
5. IF :NEW.HIRE_DATE > SYSDATE + 180 → RAISE_APPLICATION_ERROR(-20501, 'Hire date cannot be more than 180 days in the future')
6. Uniqueness check:
   - SELECT COUNT(*) FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(:NEW.EMAIL) AND ACTIVE_FLAG = 'Y'
   - IF v_count > 0 → RAISE_APPLICATION_ERROR(-20502, 'Email address already in use: ' || :NEW.EMAIL)

Business Rules:
- CREATED_BY defaults to current DB user (USER).
- CREATED_DATE defaults to SYSDATE.
- ACTIVE_FLAG defaults to 'Y'.
- EMPLOYMENT_STATUS defaults to 'ACTIVE'.
- Hire date may not be more than **180 days** in the future (error code -20501).
- Email address must be unique among active employees (case-insensitive; error code -20502). Note: also enforced by a UNIQUE constraint, but trigger gives a better message.

Tables accessed: HRMS.EMPLOYEES (SELECT for email uniqueness check; columns: EMAIL, ACTIVE_FLAG)

Custom Exceptions:
| Code   | Message                                                              |
|--------|----------------------------------------------------------------------|
| -20501 | Hire date cannot be more than 180 days in the future                |
| -20502 | Email address already in use: \<email\>                             |

---

**Trigger: TRG_EMP_BEFORE_UPDATE**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_EMP_BEFORE_UPDATE
BEFORE UPDATE ON HRMS.EMPLOYEES
FOR EACH ROW
```
Firing: Before each UPDATE on HRMS.EMPLOYEES.

Logic:
1. :NEW.MODIFIED_BY := NVL(:NEW.MODIFIED_BY, USER)
2. :NEW.MODIFIED_DATE := SYSDATE
3. IF :OLD.EMPLOYMENT_STATUS = 'TERMINATED' AND :NEW.EMPLOYMENT_STATUS = 'ACTIVE' →
   RAISE_APPLICATION_ERROR(-20503, 'Cannot directly reactivate a terminated employee. Use the rehire process.')
4. IF :OLD.EMPLOYMENT_STATUS != :NEW.EMPLOYMENT_STATUS →
   INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)
   VALUES (SEQ_EMP_HISTORY.NEXTVAL, :NEW.EMP_ID, 'STATUS_CHANGE', SYSDATE, :OLD.EMPLOYMENT_STATUS, :NEW.EMPLOYMENT_STATUS, NVL(:NEW.MODIFIED_BY, USER), 'Triggered by status update')
5. IF NVL(:OLD.DEPT_ID, -1) != NVL(:NEW.DEPT_ID, -1) →
   INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)
   VALUES (SEQ_EMP_HISTORY.NEXTVAL, :NEW.EMP_ID, 'DEPARTMENT_CHANGE', SYSDATE, TO_CHAR(:OLD.DEPT_ID), TO_CHAR(:NEW.DEPT_ID), NVL(:NEW.MODIFIED_BY, USER), 'Department transfer')
6. IF NVL(:OLD.JOB_ID, -1) != NVL(:NEW.JOB_ID, -1) →
   INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)
   VALUES (SEQ_EMP_HISTORY.NEXTVAL, :NEW.EMP_ID, 'JOB_CHANGE', SYSDATE, TO_CHAR(:OLD.JOB_ID), TO_CHAR(:NEW.JOB_ID), NVL(:NEW.MODIFIED_BY, USER), 'Job title change')

Business Rules:
- MODIFIED_BY and MODIFIED_DATE are auto-stamped on every update.
- Direct reactivation of a TERMINATED employee to ACTIVE via UPDATE is blocked (error -20503); must use rehire process.
- Any change to EMPLOYMENT_STATUS writes a 'STATUS_CHANGE' history record to EMPLOYEE_HISTORY.
- Any change to DEPT_ID writes a 'DEPARTMENT_CHANGE' history record to EMPLOYEE_HISTORY.
- Any change to JOB_ID writes a 'JOB_CHANGE' history record to EMPLOYEE_HISTORY.
- NULL DEPT_ID and NULL JOB_ID are compared using sentinel value -1 (i.e., NVL(col, -1)) to treat NULL→NULL as no change.

Tables accessed / written:
- HRMS.EMPLOYEES (read :OLD/:NEW values)
- HRMS.EMPLOYEE_HISTORY (INSERT; columns: HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)

Sequences used: SEQ_EMP_HISTORY.NEXTVAL

Custom Exceptions:
| Code   | Message                                                                                      |
|--------|----------------------------------------------------------------------------------------------|
| -20503 | Cannot directly reactivate a terminated employee. Use the rehire process.                   |

---

**Trigger: TRG_EMP_INSTEAD_OF_DELETE (named TRG_EMP_BEFORE_DELETE in comments)**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_EMP_INSTEAD_OF_DELETE
BEFORE DELETE ON HRMS.EMPLOYEES
FOR EACH ROW
```
Firing: Before each DELETE on HRMS.EMPLOYEES.

Logic:
- Unconditionally: RAISE_APPLICATION_ERROR(-20504, 'Direct deletion not allowed. Use termination process or set ACTIVE_FLAG to N.')

Business Rule: Direct physical deletion of EMPLOYEES rows is prohibited; all "deletes" must go through the termination process or set ACTIVE_FLAG = 'N' (soft delete pattern).

Known Bug (from inline comment): Trigger is declared as BEFORE DELETE (not INSTEAD OF), which prevents any DELETEs; Oracle Forms workaround is to set ACTIVE_FLAG = 'N' then CLEAR_RECORD instead of DELETE_RECORD.

Custom Exceptions:
| Code   | Message                                                                          |
|--------|----------------------------------------------------------------------------------|
| -20504 | Direct deletion not allowed. Use termination process or set ACTIVE_FLAG to N.  |

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/README.md ===

**Application Name:** HR Management System (HRMS)
**Platform:** Oracle Forms 12c / Oracle WebLogic 12c / Oracle Database 19c
**Schema:** HRMS
**Concurrent Users:** approximately 200 across 3 regional offices

**Module List:**
- Employee Records — hire, transfer, terminate, personal details, job history
- Department & Organization — department hierarchy, cost centers, reporting lines
- Payroll Processing — salary calculations, deductions, tax withholding, pay runs
- Leave Management — leave requests, approvals, balance tracking, accrual rules
- Performance Reviews — annual review cycles, ratings, goal tracking
- Reporting — headcount, compensation analysis, turnover, compliance

**Version History:**
- Originally Oracle Forms 6i, circa 2002
- Upgraded to Forms 11g in 2012
- Currently Forms 12c on Oracle Database 19c

**Architecture (from diagram):**
- Oracle Forms 12c Application Server
- Oracle WebLogic 12c Server
- Three artifact layers: Forms Modules (.fmb/.fmx) — 18 forms; PL/SQL Packages & Procedures — 12 packages; Oracle Reports (.rdf/.rep) — 8 reports
- Oracle Database 19c (HRMS schema): 42 tables, 15 views, 200+ triggers

**Forms Files (xml-exports):**
- HRMS_EMPLOYEE.xml — Employee maintenance form
- HRMS_DEPARTMENT.xml — Department management form
- HRMS_PAYROLL.xml — Payroll processing form
- HRMS_LEAVE.xml — Leave request and approval form
- HRMS_PERFORMANCE.xml — Performance review form
- HRMS_LOGIN.xml — Login and authentication form
- HRMS_MENU.xml — Main menu navigation form
- HRMS_REPORTS.xml — Report parameter and launcher form
- HRMS_LOV.xml — Shared List of Values library
- HRMS_TOOLBAR.xml — Shared toolbar object library

**PL/SQL Packages:**
- PKG_EMPLOYEE.pks/.pkb
- PKG_DEPARTMENT.pks/.pkb
- PKG_PAYROLL.pks/.pkb
- PKG_LEAVE.pks/.pkb
- PKG_PERFORMANCE.pks/.pkb
- PKG_SECURITY.pks/.pkb
- PKG_AUDIT.pks/.pkb
- PKG_NOTIFICATION.pks/.pkb
- PKG_REPORTING.pks/.pkb
- PKG_COMMON.pks/.pkb
- PKG_VALIDATION.pks/.pkb
- PKG_INTEGRATION.pks/.pkb

**Oracle Forms Technical Characteristics:**
- Triggers: WHEN-NEW-FORM-INSTANCE, WHEN-VALIDATE-ITEM, WHEN-BUTTON-PRESSED, POST-QUERY, PRE-INSERT, PRE-UPDATE
- LOV (List of Values): Record groups with dynamic WHERE clauses
- Canvas/block architecture: Multiple data blocks per form, master-detail relationships
- PLL libraries: Shared PL/SQL libraries attached to all forms
- Menu modules (.mmb): Role-based menu system with security

**PL/SQL Patterns:**
- Heavy use of DBMS_OUTPUT, UTL_FILE, UTL_MAIL built-in packages
- Cursor-based processing (row-by-row) for batch operations
- Exception handling with custom error codes (-20000 to -20999)
- Dynamic SQL via EXECUTE IMMEDIATE
- Global package variables for session state management
- Implicit cursors and %ROWTYPE / %TYPE declarations

**Database Patterns:**
- Surrogate keys via sequences + BEFORE INSERT triggers
- Soft deletes (ACTIVE_FLAG CHAR(1) DEFAULT 'Y')
- Audit columns on every table (CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE)
- History tables (_HIST suffix) for change tracking
- Denormalized reporting tables refreshed nightly by batch jobs

**Known Technical Debt:**
- No unit tests; all testing is manual via Forms
- Business logic split between Forms triggers and database packages with no clear boundary
- Several packages exceed 3,000 lines
- Hard-coded configuration values in package bodies
- VARCHAR2(4000) used as catch-all for text fields
- Mixed naming conventions (some CAMELCASE, some UNDERSCORE_CASE)
- Dead code from decommissioned modules still present
- Circular package dependencies between PKG_EMPLOYEE and PKG_PAYROLL

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/sequences/hrms_sequences.sql ===

**Schema:** HRMS
**All sequences use NOCACHE unless noted.**

**Known Bug:** SEQ_EMP_NUMBER uses NOCACHE causing gaps, but PKG_EMPLOYEE.generate_emp_number uses MAX()+1 instead, creating a race condition.

**Complete Sequence List:**

| Sequence Name            | Start With | Increment By | Cache   | Purpose                                              |
|--------------------------|------------|--------------|---------|------------------------------------------------------|
| SEQ_DEPARTMENT           | 100        | 1            | NOCACHE | DEPARTMENTS surrogate key                            |
| SEQ_LOCATION             | 100        | 1            | NOCACHE | LOCATIONS surrogate key                              |
| SEQ_JOB_GRADE            | 100        | 1            | NOCACHE | JOB_GRADES surrogate key                             |
| SEQ_JOB_TITLE            | 100        | 1            | NOCACHE | JOB_TITLES surrogate key                             |
| SEQ_EMPLOYEE             | 10000      | 1            | NOCACHE | EMPLOYEES surrogate key                              |
| SEQ_EMP_HISTORY          | 1          | 1            | NOCACHE | EMPLOYEE_HISTORY surrogate key                       |
| SEQ_DEPENDENT            | 1          | 1            | NOCACHE | EMPLOYEE_DEPENDENTS surrogate key                    |
| SEQ_EMERGENCY_CONTACT    | 1          | 1            | NOCACHE | EMERGENCY_CONTACTS surrogate key                     |
| SEQ_EMP_NUMBER           | 1000       | 1            | NOCACHE | Employee number generation (EMP-XXXXXX format); has race condition bug |
| SEQ_SALARY               | 1          | 1            | NOCACHE | SALARY_RECORDS surrogate key                         |
| SEQ_PAY_ELEMENT          | 1          | 1            | NOCACHE | PAY_ELEMENTS surrogate key                           |
| SEQ_EMP_PAY_ELEMENT      | 1          | 1            | NOCACHE | EMPLOYEE_PAY_ELEMENTS surrogate key                  |
| SEQ_PAY_PERIOD           | 1          | 1            | NOCACHE | PAY_PERIODS surrogate key                            |
| SEQ_PAYROLL_RUN          | 1          | 1            | NOCACHE | PAYROLL_RUNS surrogate key                           |
| SEQ_PAYROLL_DETAIL       | 1          | 1            | NOCACHE | PAYROLL_DETAILS surrogate key                        |
| SEQ_TAX_BRACKET          | 1          | 1            | NOCACHE | TAX_BRACKETS surrogate key                           |
| SEQ_LEAVE_TYPE           | 1          | 1            | NOCACHE | LEAVE_TYPES surrogate key                            |
| SEQ_LEAVE_BALANCE        | 1          | 1            | NOCACHE | LEAVE_BALANCES surrogate key                         |
| SEQ_LEAVE_REQUEST        | 1          | 1            | NOCACHE | LEAVE_REQUESTS surrogate key                         |
| SEQ_LEAVE_ACCRUAL        | 1          | 1            | NOCACHE | LEAVE_ACCRUAL_LOG surrogate key                      |
| SEQ_HOLIDAY              | 1          | 1            | NOCACHE | HOLIDAYS surrogate key                               |
| SEQ_REVIEW_CYCLE         | 1          | 1            | NOCACHE | REVIEW_CYCLES surrogate key                          |
| SEQ_PERF_REVIEW          | 1          | 1            | NOCACHE | PERFORMANCE_REVIEWS surrogate key                    |
| SEQ_PERF_GOAL            | 1          | 1            | NOCACHE | PERFORMANCE_GOALS surrogate key                      |
| SEQ_AUDIT                | 1          | 1            | CACHE 100 | AUDIT_LOG surrogate key (only cached sequence)     |
| SEQ_NOTIFICATION         | 1          | 1            | NOCACHE | NOTIFICATION_QUEUE surrogate key                     |
| SEQ_USER_SESSION         | 1          | 1            | NOCACHE | USER_SESSIONS surrogate key                          |
| SEQ_SYSTEM_PARAM         | 1          | 1            | NOCACHE | SYSTEM_PARAMETERS surrogate key                      |
| SEQ_LOOKUP               | 1          | 1            | NOCACHE | LOOKUP_VALUES surrogate key                          |

**Total sequences:** 29

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/01_core_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.DEPARTMENTS**

| Column           | Data Type       | Constraints / Default       | Notes                                    |
|------------------|-----------------|------------------------------|------------------------------------------|
| DEPT_ID          | NUMBER(10)      | NOT NULL, PK                |                                          |
| DEPT_CODE        | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_DEPT_CODE) |                                       |
| DEPT_NAME        | VARCHAR2(100)   | NOT NULL                    |                                          |
| PARENT_DEPT_ID   | NUMBER(10)      | nullable                    | Self-referencing FK for dept hierarchy   |
| COST_CENTER      | VARCHAR2(20)    | nullable                    | Financial cost center code for GL integration |
| MANAGER_EMP_ID   | NUMBER(10)      | nullable                    |                                          |
| LOCATION_CODE    | VARCHAR2(10)    | nullable                    |                                          |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y', CHECK IN ('Y','N') |                            |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                    |                                          |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE   |                                          |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                    |                                          |
| MODIFIED_DATE    | DATE            | nullable                    |                                          |

Constraints: PK_DEPARTMENTS (DEPT_ID), UK_DEPT_CODE (DEPT_CODE), CHK_DEPT_ACTIVE (ACTIVE_FLAG IN ('Y','N'))

Table comment: 'Organization departments and cost centers'
Column comments: PARENT_DEPT_ID — 'Self-referencing FK for department hierarchy'; COST_CENTER — 'Financial cost center code for GL integration'

---

**Table: HRMS.LOCATIONS**

| Column           | Data Type       | Constraints / Default         |
|------------------|-----------------|-------------------------------|
| LOCATION_CODE    | VARCHAR2(10)    | NOT NULL, PK                  |
| LOCATION_NAME    | VARCHAR2(100)   | NOT NULL                      |
| ADDRESS_LINE1    | VARCHAR2(200)   | nullable                      |
| ADDRESS_LINE2    | VARCHAR2(200)   | nullable                      |
| CITY             | VARCHAR2(100)   | nullable                      |
| STATE_PROVINCE   | VARCHAR2(100)   | nullable                      |
| POSTAL_CODE      | VARCHAR2(20)    | nullable                      |
| COUNTRY_CODE     | VARCHAR2(3)     | nullable                      |
| PHONE_NUMBER     | VARCHAR2(30)    | nullable                      |
| TIMEZONE         | VARCHAR2(50)    | DEFAULT 'America/New_York'    |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'         |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                      |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE     |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                      |
| MODIFIED_DATE    | DATE            | nullable                      |

Constraints: PK_LOCATIONS (LOCATION_CODE)

---

**Table: HRMS.JOB_GRADES**

| Column           | Data Type       | Constraints / Default                     |
|------------------|-----------------|-------------------------------------------|
| GRADE_ID         | NUMBER(5)       | NOT NULL, PK                              |
| GRADE_CODE       | VARCHAR2(10)    | NOT NULL, UNIQUE (UK_GRADE_CODE)          |
| GRADE_NAME       | VARCHAR2(50)    | NOT NULL                                  |
| MIN_SALARY       | NUMBER(12,2)    | NOT NULL                                  |
| MAX_SALARY       | NUMBER(12,2)    | NOT NULL                                  |
| OVERTIME_ELIGIBLE| CHAR(1)         | DEFAULT 'N'                               |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                     |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                  |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                 |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                  |
| MODIFIED_DATE    | DATE            | nullable                                  |

Constraints: PK_JOB_GRADES (GRADE_ID), UK_GRADE_CODE (GRADE_CODE), CHK_SALARY_RANGE (MAX_SALARY >= MIN_SALARY)

Business Rule: Maximum salary must be greater than or equal to minimum salary (CHECK constraint CHK_SALARY_RANGE).

---

**Table: HRMS.JOB_TITLES**

| Column           | Data Type       | Constraints / Default                        |
|------------------|-----------------|----------------------------------------------|
| JOB_ID           | NUMBER(10)      | NOT NULL, PK                                 |
| JOB_CODE         | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_JOB_CODE)               |
| JOB_TITLE        | VARCHAR2(100)   | NOT NULL                                     |
| JOB_FAMILY       | VARCHAR2(50)    | nullable                                     |
| GRADE_ID         | NUMBER(5)       | NOT NULL, FK → JOB_GRADES(GRADE_ID)          |
| EEO_CATEGORY     | VARCHAR2(10)    | nullable                                     |
| FLSA_STATUS      | VARCHAR2(10)    | DEFAULT 'EXEMPT'                             |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                        |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                     |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                    |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                     |
| MODIFIED_DATE    | DATE            | nullable                                     |

Constraints: PK_JOB_TITLES (JOB_ID), UK_JOB_CODE (JOB_CODE), FK_JOB_GRADE (GRADE_ID → JOB_GRADES.GRADE_ID)

---

**Table: HRMS.EMPLOYEES**

| Column              | Data Type       | Constraints / Default                                                                     |
|---------------------|-----------------|-------------------------------------------------------------------------------------------|
| EMP_ID              | NUMBER(10)      | NOT NULL, PK                                                                              |
| EMP_NUMBER          | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_EMP_NUMBER)                                                          |
| FIRST_NAME          | VARCHAR2(50)    | NOT NULL                                                                                  |
| MIDDLE_NAME         | VARCHAR2(50)    | nullable                                                                                  |
| LAST_NAME           | VARCHAR2(50)    | NOT NULL                                                                                  |
| DATE_OF_BIRTH       | DATE            | nullable                                                                                  |
| GENDER              | CHAR(1)         | nullable, CHECK IN ('M','F','O')                                                          |
| MARITAL_STATUS      | VARCHAR2(10)    | nullable                                                                                  |
| NATIONALITY         | VARCHAR2(50)    | nullable                                                                                  |
| SSN_ENCRYPTED       | VARCHAR2(200)   | nullable; AES-256 encrypted SSN, decrypted only in PKG_SECURITY                          |
| EMAIL               | VARCHAR2(100)   | nullable                                                                                  |
| PHONE_WORK          | VARCHAR2(30)    | nullable                                                                                  |
| PHONE_MOBILE        | VARCHAR2(30)    | nullable                                                                                  |
| ADDRESS_LINE1       | VARCHAR2(200)   | nullable                                                                                  |
| ADDRESS_LINE2       | VARCHAR2(200)   | nullable                                                                                  |
| CITY                | VARCHAR2(100)   | nullable                                                                                  |
| STATE_PROVINCE      | VARCHAR2(100)   | nullable                                                                                  |
| POSTAL_CODE         | VARCHAR2(20)    | nullable                                                                                  |
| COUNTRY_CODE        | VARCHAR2(3)     | nullable                                                                                  |
| HIRE_DATE           | DATE            | NOT NULL                                                                                  |
| TERMINATION_DATE    | DATE            | nullable                                                                                  |
| TERMINATION_REASON  | VARCHAR2(50)    | nullable                                                                                  |
| DEPT_ID             | NUMBER(10)      | NOT NULL, FK → DEPARTMENTS(DEPT_ID)                                                      |
| JOB_ID              | NUMBER(10)      | NOT NULL, FK → JOB_TITLES(JOB_ID)                                                        |
| MANAGER_EMP_ID      | NUMBER(10)      | nullable, FK → EMPLOYEES(EMP_ID) (self-referencing)                                      |
| LOCATION_CODE       | VARCHAR2(10)    | nullable, FK → LOCATIONS(LOCATION_CODE)                                                   |
| EMPLOYMENT_TYPE     | VARCHAR2(20)    | DEFAULT 'FULL_TIME', CHECK IN ('FULL_TIME','PART_TIME','CONTRACT','INTERN')               |
| EMPLOYMENT_STATUS   | VARCHAR2(20)    | DEFAULT 'ACTIVE', CHECK IN ('ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED')                 |
| PHOTO_BLOB          | BLOB            | nullable                                                                                  |
| NOTES               | CLOB            | nullable                                                                                  |
| ACTIVE_FLAG         | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                     |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                                  |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                                 |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                                  |
| MODIFIED_DATE       | DATE            | nullable                                                                                  |

Constraints:
- PK_EMPLOYEES (EMP_ID)
- UK_EMP_NUMBER (EMP_NUMBER)
- FK_EMP_DEPT → DEPARTMENTS(DEPT_ID)
- FK_EMP_JOB → JOB_TITLES(JOB_ID)
- FK_EMP_MANAGER → EMPLOYEES(EMP_ID)
- FK_EMP_LOCATION → LOCATIONS(LOCATION_CODE)
- CHK_EMP_STATUS: EMPLOYMENT_STATUS IN ('ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED')
- CHK_EMP_TYPE: EMPLOYMENT_TYPE IN ('FULL_TIME','PART_TIME','CONTRACT','INTERN')
- CHK_EMP_GENDER: GENDER IN ('M','F','O')

Table comment: 'Master employee records - core entity of the HRMS system'
Column comments:
- SSN_ENCRYPTED: 'AES-256 encrypted SSN - decrypted only in PKG_SECURITY'
- EMPLOYMENT_STATUS: 'Current status: ACTIVE, ON_LEAVE, SUSPENDED, TERMINATED'

---

**Table: HRMS.EMPLOYEE_HISTORY**

| Column           | Data Type       | Constraints / Default                                                                                |
|------------------|-----------------|------------------------------------------------------------------------------------------------------|
| HIST_ID          | NUMBER(15)      | NOT NULL, PK                                                                                         |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                     |
| CHANGE_TYPE      | VARCHAR2(30)    | NOT NULL, CHECK IN ('HIRE','TRANSFER','PROMOTION','DEMOTION','SALARY_CHANGE','TERMINATION','REHIRE','LEAVE_START','LEAVE_END','STATUS_CHANGE') |
| EFFECTIVE_DATE   | DATE            | NOT NULL                                                                                             |
| OLD_DEPT_ID      | NUMBER(10)      | nullable                                                                                             |
| NEW_DEPT_ID      | NUMBER(10)      | nullable                                                                                             |
| OLD_JOB_ID       | NUMBER(10)      | nullable                                                                                             |
| NEW_JOB_ID       | NUMBER(10)      | nullable                                                                                             |
| OLD_MANAGER_ID   | NUMBER(10)      | nullable                                                                                             |
| NEW_MANAGER_ID   | NUMBER(10)      | nullable                                                                                             |
| OLD_SALARY       | NUMBER(12,2)    | nullable                                                                                             |
| NEW_SALARY       | NUMBER(12,2)    | nullable                                                                                             |
| OLD_LOCATION     | VARCHAR2(10)    | nullable                                                                                             |
| NEW_LOCATION     | VARCHAR2(10)    | nullable                                                                                             |
| REASON_CODE      | VARCHAR2(30)    | nullable                                                                                             |
| COMMENTS         | VARCHAR2(4000)  | nullable                                                                                             |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                                                                             |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                                                                            |

Constraints:
- PK_EMP_HISTORY (HIST_ID)
- FK_HIST_EMP → EMPLOYEES(EMP_ID)
- CHK_CHANGE_TYPE: CHANGE_TYPE IN ('HIRE','TRANSFER','PROMOTION','DEMOTION','SALARY_CHANGE','TERMINATION','REHIRE','LEAVE_START','LEAVE_END','STATUS_CHANGE')

Note: The trigger TRG_EMP_BEFORE_UPDATE uses a column named CHANGE_DATE (not EFFECTIVE_DATE) and writes to OLD_VALUE/NEW_VALUE (VARCHAR2) — but the DDL here has EFFECTIVE_DATE and typed old/new columns. This is a discrepancy between the trigger and the DDL (the trigger appears to be inserting into a differently-structured version of the table or columns are aliases).

---

**Table: HRMS.EMPLOYEE_DEPENDENTS**

| Column           | Data Type       | Constraints / Default                                                       |
|------------------|-----------------|-----------------------------------------------------------------------------|
| DEPENDENT_ID     | NUMBER(10)      | NOT NULL, PK                                                                |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                            |
| FIRST_NAME       | VARCHAR2(50)    | NOT NULL                                                                    |
| LAST_NAME        | VARCHAR2(50)    | NOT NULL                                                                    |
| RELATIONSHIP     | VARCHAR2(20)    | NOT NULL, CHECK IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER')   |
| DATE_OF_BIRTH    | DATE            | nullable                                                                    |
| SSN_ENCRYPTED    | VARCHAR2(200)   | nullable                                                                    |
| BENEFITS_ENROLLED| CHAR(1)         | DEFAULT 'N'                                                                 |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                       |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                                                    |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                                                   |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                                                    |
| MODIFIED_DATE    | DATE            | nullable                                                                    |

Constraints: PK_EMP_DEPENDENTS (DEPENDENT_ID), FK_DEP_EMP → EMPLOYEES(EMP_ID), CHK_RELATIONSHIP (RELATIONSHIP IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER'))

---

**Table: HRMS.EMERGENCY_CONTACTS**

| Column           | Data Type       | Constraints / Default                    |
|------------------|-----------------|------------------------------------------|
| CONTACT_ID       | NUMBER(10)      | NOT NULL, PK                             |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)         |
| CONTACT_NAME     | VARCHAR2(100)   | NOT NULL                                 |
| RELATIONSHIP     | VARCHAR2(30)    | nullable                                 |
| PHONE_PRIMARY    | VARCHAR2(30)    | NOT NULL                                 |
| PHONE_SECONDARY  | VARCHAR2(30)    | nullable                                 |
| EMAIL            | VARCHAR2(100)   | nullable                                 |
| PRIORITY_ORDER   | NUMBER(2)       | DEFAULT 1                                |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                    |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                 |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                 |
| MODIFIED_DATE    | DATE            | nullable                                 |

Constraints: PK_EMERGENCY_CONTACTS (CONTACT_ID), FK_EC_EMP → EMPLOYEES(EMP_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/02_payroll_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.SALARY_RECORDS**

| Column           | Data Type       | Constraints / Default                                                            |
|------------------|-----------------|----------------------------------------------------------------------------------|
| SALARY_ID        | NUMBER(10)      | NOT NULL, PK                                                                     |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                 |
| EFFECTIVE_DATE   | DATE            | NOT NULL                                                                         |
| END_DATE         | DATE            | nullable                                                                         |
| BASE_SALARY      | NUMBER(12,2)    | NOT NULL                                                                         |
| CURRENCY_CODE    | VARCHAR2(3)     | DEFAULT 'USD'                                                                    |
| PAY_FREQUENCY    | VARCHAR2(20)    | DEFAULT 'MONTHLY', CHECK IN ('WEEKLY','BIWEEKLY','SEMIMONTHLY','MONTHLY')        |
| SALARY_BASIS     | VARCHAR2(20)    | DEFAULT 'ANNUAL', CHECK IN ('ANNUAL','HOURLY')                                   |
| CHANGE_REASON    | VARCHAR2(50)    | nullable                                                                         |
| CHANGE_PCT       | NUMBER(5,2)     | nullable                                                                         |
| APPROVED_BY      | NUMBER(10)      | nullable                                                                         |
| APPROVAL_DATE    | DATE            | nullable                                                                         |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                            |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                                                         |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                                                        |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                                                         |
| MODIFIED_DATE    | DATE            | nullable                                                                         |

Constraints: PK_SALARY_RECORDS (SALARY_ID), FK_SAL_EMP → EMPLOYEES(EMP_ID), CHK_PAY_FREQ, CHK_SAL_BASIS

---

**Table: HRMS.PAY_ELEMENTS**

| Column             | Data Type       | Constraints / Default                                                                     |
|--------------------|-----------------|-------------------------------------------------------------------------------------------|
| ELEMENT_ID         | NUMBER(10)      | NOT NULL, PK                                                                              |
| ELEMENT_CODE       | VARCHAR2(30)    | NOT NULL, UNIQUE (UK_PAY_ELEM_CODE)                                                       |
| ELEMENT_NAME       | VARCHAR2(100)   | NOT NULL                                                                                  |
| ELEMENT_TYPE       | VARCHAR2(20)    | NOT NULL, CHECK IN ('EARNING','DEDUCTION','TAX','BENEFIT','REIMBURSEMENT')                |
| CALCULATION_TYPE   | VARCHAR2(20)    | NOT NULL, CHECK IN ('FLAT','PERCENTAGE','HOURS','FORMULA')                                |
| DEFAULT_AMOUNT     | NUMBER(12,2)    | nullable                                                                                  |
| DEFAULT_PERCENTAGE | NUMBER(5,2)     | nullable                                                                                  |
| TAXABLE_FLAG       | CHAR(1)         | DEFAULT 'Y'                                                                               |
| PRETAX_FLAG        | CHAR(1)         | DEFAULT 'N'                                                                               |
| EMPLOYER_PAID      | CHAR(1)         | DEFAULT 'N'                                                                               |
| GL_ACCOUNT_CODE    | VARCHAR2(30)    | nullable                                                                                  |
| PRIORITY_ORDER     | NUMBER(5)       | DEFAULT 100                                                                               |
| ACTIVE_FLAG        | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                     |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                                                  |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                                                 |
| MODIFIED_BY        | VARCHAR2(30)    | nullable                                                                                  |
| MODIFIED_DATE      | DATE            | nullable                                                                                  |

Constraints: PK_PAY_ELEMENTS (ELEMENT_ID), UK_PAY_ELEM_CODE (ELEMENT_CODE), CHK_ELEM_TYPE, CHK_CALC_TYPE

---

**Table: HRMS.EMPLOYEE_PAY_ELEMENTS**

| Column           | Data Type       | Constraints / Default                    |
|------------------|-----------------|------------------------------------------|
| EMP_ELEMENT_ID   | NUMBER(10)      | NOT NULL, PK                             |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)         |
| ELEMENT_ID       | NUMBER(10)      | NOT NULL, FK → PAY_ELEMENTS(ELEMENT_ID)  |
| EFFECTIVE_DATE   | DATE            | NOT NULL                                 |
| END_DATE         | DATE            | nullable                                 |
| AMOUNT           | NUMBER(12,2)    | nullable                                 |
| PERCENTAGE       | NUMBER(5,2)     | nullable                                 |
| OVERRIDE_AMOUNT  | NUMBER(12,2)    | nullable                                 |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                    |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                 |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                 |
| MODIFIED_DATE    | DATE            | nullable                                 |

Constraints: PK_EMP_PAY_ELEMENTS (EMP_ELEMENT_ID), FK_EPE_EMP → EMPLOYEES(EMP_ID), FK_EPE_ELEMENT → PAY_ELEMENTS(ELEMENT_ID)

---

**Table: HRMS.PAY_PERIODS**

| Column             | Data Type       | Constraints / Default                                              |
|--------------------|-----------------|---------------------------------------------------------------------|
| PERIOD_ID          | NUMBER(10)      | NOT NULL, PK                                                        |
| PERIOD_NAME        | VARCHAR2(50)    | NOT NULL                                                            |
| PAY_FREQUENCY      | VARCHAR2(20)    | NOT NULL                                                            |
| PERIOD_START_DATE  | DATE            | NOT NULL                                                            |
| PERIOD_END_DATE    | DATE            | NOT NULL                                                            |
| PAY_DATE           | DATE            | NOT NULL                                                            |
| STATUS             | VARCHAR2(20)    | DEFAULT 'OPEN', CHECK IN ('OPEN','PROCESSING','CLOSED','REVERSED') |
| CLOSED_BY          | VARCHAR2(30)    | nullable                                                            |
| CLOSED_DATE        | DATE            | nullable                                                            |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                            |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                           |
| MODIFIED_BY        | VARCHAR2(30)    | nullable                                                            |
| MODIFIED_DATE      | DATE            | nullable                                                            |

Constraints: PK_PAY_PERIODS (PERIOD_ID), CHK_PERIOD_STATUS

---

**Table: HRMS.PAYROLL_RUNS**

| Column              | Data Type       | Constraints / Default                                                              |
|---------------------|-----------------|------------------------------------------------------------------------------------|
| RUN_ID              | NUMBER(10)      | NOT NULL, PK                                                                       |
| PERIOD_ID           | NUMBER(10)      | NOT NULL, FK → PAY_PERIODS(PERIOD_ID)                                              |
| RUN_TYPE            | VARCHAR2(20)    | DEFAULT 'REGULAR', CHECK IN ('REGULAR','SUPPLEMENTAL','BONUS','FINAL')             |
| RUN_DATE            | DATE            | NOT NULL                                                                           |
| STATUS              | VARCHAR2(20)    | DEFAULT 'PENDING', CHECK IN ('PENDING','CALCULATING','CALCULATED','APPROVED','PAID','REVERSED','ERROR') |
| TOTAL_GROSS         | NUMBER(15,2)    | nullable                                                                           |
| TOTAL_DEDUCTIONS    | NUMBER(15,2)    | nullable                                                                           |
| TOTAL_NET           | NUMBER(15,2)    | nullable                                                                           |
| TOTAL_EMPLOYER_COST | NUMBER(15,2)    | nullable                                                                           |
| EMPLOYEE_COUNT      | NUMBER(10)      | nullable                                                                           |
| ERROR_COUNT         | NUMBER(10)      | DEFAULT 0                                                                          |
| SUBMITTED_BY        | VARCHAR2(30)    | nullable                                                                           |
| SUBMITTED_DATE      | DATE            | nullable                                                                           |
| APPROVED_BY         | VARCHAR2(30)    | nullable                                                                           |
| APPROVED_DATE       | DATE            | nullable                                                                           |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                           |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                          |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                           |
| MODIFIED_DATE       | DATE            | nullable                                                                           |

Constraints: PK_PAYROLL_RUNS (RUN_ID), FK_PR_PERIOD → PAY_PERIODS(PERIOD_ID), CHK_RUN_TYPE, CHK_RUN_STATUS

---

**Table: HRMS.PAYROLL_DETAILS**

| Column           | Data Type       | Constraints / Default                        |
|------------------|-----------------|----------------------------------------------|
| DETAIL_ID        | NUMBER(15)      | NOT NULL, PK                                 |
| RUN_ID           | NUMBER(10)      | NOT NULL, FK → PAYROLL_RUNS(RUN_ID)          |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)             |
| ELEMENT_ID       | NUMBER(10)      | NOT NULL, FK → PAY_ELEMENTS(ELEMENT_ID)      |
| ELEMENT_TYPE     | VARCHAR2(20)    | NOT NULL                                     |
| HOURS_WORKED     | NUMBER(6,2)     | nullable                                     |
| RATE             | NUMBER(12,4)    | nullable                                     |
| AMOUNT           | NUMBER(12,2)    | NOT NULL                                     |
| YTD_AMOUNT       | NUMBER(15,2)    | nullable                                     |
| STATUS           | VARCHAR2(20)    | DEFAULT 'CALCULATED'                         |
| ERROR_MESSAGE    | VARCHAR2(4000)  | nullable                                     |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                     |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                    |

Constraints: PK_PAYROLL_DETAILS (DETAIL_ID), FK_PD_RUN → PAYROLL_RUNS(RUN_ID), FK_PD_EMP → EMPLOYEES(EMP_ID), FK_PD_ELEMENT → PAY_ELEMENTS(ELEMENT_ID)

---

**Table: HRMS.TAX_BRACKETS**

| Column         | Data Type       | Constraints / Default                                                                    |
|----------------|-----------------|------------------------------------------------------------------------------------------|
| BRACKET_ID     | NUMBER(10)      | NOT NULL, PK                                                                             |
| TAX_YEAR       | NUMBER(4)       | NOT NULL                                                                                 |
| FILING_STATUS  | VARCHAR2(30)    | NOT NULL, CHECK IN ('SINGLE','MARRIED_JOINT','MARRIED_SEPARATE','HEAD_OF_HOUSEHOLD')     |
| BRACKET_MIN    | NUMBER(12,2)    | NOT NULL                                                                                 |
| BRACKET_MAX    | NUMBER(12,2)    | nullable (NULL = no upper bound, i.e., top bracket)                                      |
| TAX_RATE       | NUMBER(5,4)     | NOT NULL                                                                                 |
| BASE_TAX       | NUMBER(12,2)    | DEFAULT 0                                                                                |
| STATE_CODE     | VARCHAR2(3)     | nullable (NULL = federal)                                                                |
| ACTIVE_FLAG    | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                    |
| CREATED_BY     | VARCHAR2(30)    | NOT NULL                                                                                 |
| CREATED_DATE   | DATE            | NOT NULL, DEFAULT SYSDATE                                                                |

Constraints: PK_TAX_BRACKETS (BRACKET_ID), CHK_FILING_STATUS

Note: TAX_RATE is NUMBER(5,4) — stores rates as decimal fractions (e.g., 0.2200 for 22%). BASE_TAX stores the cumulative tax already owed at the start of this bracket. Actual bracket data is populated via data/seed scripts (not present in this file).

---

**Table: HRMS.EMPLOYEE_TAX_INFO**

| Column               | Data Type       | Constraints / Default                                                                    |
|----------------------|-----------------|------------------------------------------------------------------------------------------|
| TAX_INFO_ID          | NUMBER(10)      | NOT NULL, PK                                                                             |
| EMP_ID               | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                         |
| TAX_YEAR             | NUMBER(4)       | NOT NULL                                                                                 |
| FILING_STATUS        | VARCHAR2(30)    | NOT NULL                                                                                 |
| FEDERAL_ALLOWANCES   | NUMBER(3)       | DEFAULT 0                                                                                |
| STATE_ALLOWANCES     | NUMBER(3)       | DEFAULT 0                                                                                |
| ADDITIONAL_FED_WH    | NUMBER(12,2)    | DEFAULT 0                                                                                |
| ADDITIONAL_STATE_WH  | NUMBER(12,2)    | DEFAULT 0                                                                                |
| EXEMPT_FLAG          | CHAR(1)         | DEFAULT 'N'                                                                              |
| STATE_CODE           | VARCHAR2(3)     | nullable                                                                                 |
| W4_RECEIVED_DATE     | DATE            | nullable                                                                                 |
| ACTIVE_FLAG          | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                    |
| CREATED_BY           | VARCHAR2(30)    | NOT NULL                                                                                 |
| CREATED_DATE         | DATE            | NOT NULL, DEFAULT SYSDATE                                                                |
| MODIFIED_BY          | VARCHAR2(30)    | nullable                                                                                 |
| MODIFIED_DATE        | DATE            | nullable                                                                                 |

Constraints: PK_EMP_TAX_INFO (TAX_INFO_ID), FK_ETI_EMP → EMPLOYEES(EMP_ID), UK_EMP_TAX_YEAR (EMP_ID, TAX_YEAR) — one tax info record per employee per year.

---

**Table: HRMS.EMPLOYEE_BANK_ACCOUNTS**

| Column              | Data Type       | Constraints / Default                                                           |
|---------------------|-----------------|---------------------------------------------------------------------------------|
| BANK_ACCT_ID        | NUMBER(10)      | NOT NULL, PK                                                                    |
| EMP_ID              | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                |
| BANK_NAME           | VARCHAR2(100)   | nullable                                                                        |
| ROUTING_NUMBER      | VARCHAR2(20)    | NOT NULL                                                                        |
| ACCOUNT_NUMBER_ENC  | VARCHAR2(200)   | NOT NULL (encrypted)                                                            |
| ACCOUNT_TYPE        | VARCHAR2(20)    | DEFAULT 'CHECKING', CHECK IN ('CHECKING','SAVINGS')                             |
| DEPOSIT_TYPE        | VARCHAR2(20)    | DEFAULT 'FULL', CHECK IN ('FULL','PARTIAL_AMOUNT','PARTIAL_PERCENT','REMAINDER')|
| DEPOSIT_AMOUNT      | NUMBER(12,2)    | nullable                                                                        |
| DEPOSIT_PERCENTAGE  | NUMBER(5,2)     | nullable                                                                        |
| PRIORITY_ORDER      | NUMBER(2)       | DEFAULT 1                                                                       |
| PRENOTE_SENT        | CHAR(1)         | DEFAULT 'N'                                                                     |
| PRENOTE_DATE        | DATE            | nullable                                                                        |
| ACTIVE_FLAG         | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                           |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                        |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                       |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                        |
| MODIFIED_DATE       | DATE            | nullable                                                                        |

Constraints: PK_EMP_BANK_ACCTS (BANK_ACCT_ID), FK_BA_EMP → EMPLOYEES(EMP_ID), CHK_ACCT_TYPE, CHK_DEPOSIT_TYPE

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/03_leave_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.LEAVE_TYPES**

| Column             | Data Type       | Constraints / Default                                                  |
|--------------------|-----------------|------------------------------------------------------------------------|
| LEAVE_TYPE_ID      | NUMBER(5)       | NOT NULL, PK                                                           |
| LEAVE_TYPE_CODE    | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_LEAVE_TYPE_CODE)                                  |
| LEAVE_TYPE_NAME    | VARCHAR2(50)    | NOT NULL                                                               |
| PAID_FLAG          | CHAR(1)         | DEFAULT 'Y'                                                            |
| ACCRUAL_FLAG       | CHAR(1)         | DEFAULT 'Y'                                                            |
| ACCRUAL_RATE       | NUMBER(6,2)     | nullable                                                               |
| ACCRUAL_FREQUENCY  | VARCHAR2(20)    | nullable, CHECK IN ('MONTHLY','BIWEEKLY','ANNUAL', NULL)               |
| MAX_BALANCE        | NUMBER(6,2)     | nullable                                                               |
| CARRYOVER_MAX      | NUMBER(6,2)     | nullable                                                               |
| CARRYOVER_EXPIRY   | NUMBER(3)       | nullable (number of days before carryover expires)                     |
| MIN_TENURE_DAYS    | NUMBER(5)       | DEFAULT 0                                                              |
| REQUIRES_APPROVAL  | CHAR(1)         | DEFAULT 'Y'                                                            |
| REQUIRES_DOCUMENT  | CHAR(1)         | DEFAULT 'N'                                                            |
| ACTIVE_FLAG        | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                  |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                               |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                              |
| MODIFIED_BY        | VARCHAR2(30)    | nullable                                                               |
| MODIFIED_DATE      | DATE            | nullable                                                               |

Constraints: PK_LEAVE_TYPES (LEAVE_TYPE_ID), UK_LEAVE_TYPE_CODE (LEAVE_TYPE_CODE), CHK_ACCRUAL_FREQ

Business Rules embedded:
- MIN_TENURE_DAYS: employee must have been employed at least this many days to use this leave type.
- CARRYOVER_EXPIRY: number of days after which carried-over leave expires.
- MAX_BALANCE: cap on accrued leave balance.
- CARRYOVER_MAX: maximum days allowed to carry over to next year.

---

**Table: HRMS.LEAVE_BALANCES**

| Column              | Data Type       | Constraints / Default                                                        |
|---------------------|-----------------|------------------------------------------------------------------------------|
| BALANCE_ID          | NUMBER(10)      | NOT NULL, PK                                                                 |
| EMP_ID              | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                             |
| LEAVE_TYPE_ID       | NUMBER(5)       | NOT NULL, FK → LEAVE_TYPES(LEAVE_TYPE_ID)                                    |
| CALENDAR_YEAR       | NUMBER(4)       | NOT NULL                                                                     |
| OPENING_BALANCE     | NUMBER(6,2)     | DEFAULT 0                                                                    |
| ACCRUED             | NUMBER(6,2)     | DEFAULT 0                                                                    |
| USED                | NUMBER(6,2)     | DEFAULT 0                                                                    |
| ADJUSTMENT          | NUMBER(6,2)     | DEFAULT 0                                                                    |
| PENDING             | NUMBER(6,2)     | DEFAULT 0                                                                    |
| AVAILABLE           | NUMBER(6,2)     | VIRTUAL: GENERATED ALWAYS AS (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING) |
| CARRYOVER_FROM_PREV | NUMBER(6,2)     | DEFAULT 0                                                                    |
| CARRYOVER_EXPIRY_DT | DATE            | nullable                                                                     |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                     |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                    |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                     |
| MODIFIED_DATE       | DATE            | nullable                                                                     |

Constraints: PK_LEAVE_BALANCES (BALANCE_ID), FK_LB_EMP → EMPLOYEES(EMP_ID), FK_LB_TYPE → LEAVE_TYPES(LEAVE_TYPE_ID), UK_LEAVE_BAL (EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR)

Business Rule (virtual column formula): AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING

---

**Table: HRMS.LEAVE_REQUESTS**

| Column               | Data Type       | Constraints / Default                                                       |
|----------------------|-----------------|-----------------------------------------------------------------------------|
| REQUEST_ID           | NUMBER(10)      | NOT NULL, PK                                                                |
| EMP_ID               | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                            |
| LEAVE_TYPE_ID        | NUMBER(5)       | NOT NULL, FK → LEAVE_TYPES(LEAVE_TYPE_ID)                                   |
| START_DATE           | DATE            | NOT NULL                                                                    |
| END_DATE             | DATE            | NOT NULL                                                                    |
| TOTAL_DAYS           | NUMBER(5,1)     | NOT NULL                                                                    |
| HALF_DAY_FLAG        | CHAR(1)         | DEFAULT 'N'                                                                 |
| HALF_DAY_PERIOD      | VARCHAR2(10)    | nullable, CHECK IN ('AM','PM', NULL)                                        |
| STATUS               | VARCHAR2(20)    | DEFAULT 'PENDING', CHECK IN ('PENDING','APPROVED','REJECTED','CANCELLED','TAKEN') |
| REASON               | VARCHAR2(4000)  | nullable                                                                    |
| SUPPORTING_DOC_PATH  | VARCHAR2(500)   | nullable                                                                    |
| APPROVER_EMP_ID      | NUMBER(10)      | nullable, FK → EMPLOYEES(EMP_ID)                                            |
| APPROVAL_DATE        | DATE            | nullable                                                                    |
| APPROVAL_COMMENTS    | VARCHAR2(4000)  | nullable                                                                    |
| CANCEL_REASON        | VARCHAR2(4000)  | nullable                                                                    |
| CANCELLED_DATE       | DATE            | nullable                                                                    |
| CREATED_BY           | VARCHAR2(30)    | NOT NULL                                                                    |
| CREATED_DATE         | DATE            | NOT NULL, DEFAULT SYSDATE                                                   |
| MODIFIED_BY          | VARCHAR2(30)    | nullable                                                                    |
| MODIFIED_DATE        | DATE            | nullable                                                                    |

Constraints: PK_LEAVE_REQUESTS (REQUEST_ID), FK_LR_EMP → EMPLOYEES(EMP_ID), FK_LR_TYPE → LEAVE_TYPES(LEAVE_TYPE_ID), FK_LR_APPROVER → EMPLOYEES(EMP_ID), CHK_LR_STATUS, CHK_LR_DATES (END_DATE >= START_DATE), CHK_HALF_DAY (HALF_DAY_PERIOD IN ('AM','PM', NULL))

Business Rules:
- END_DATE must be >= START_DATE (CHK_LR_DATES).
- Half-day leave must specify 'AM' or 'PM' period.
- Valid status lifecycle: PENDING → APPROVED / REJECTED / CANCELLED → TAKEN.

---

**Table: HRMS.LEAVE_ACCRUAL_LOG**

| Column           | Data Type       | Constraints / Default                            |
|------------------|-----------------|--------------------------------------------------|
| ACCRUAL_ID       | NUMBER(15)      | NOT NULL, PK                                     |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                 |
| LEAVE_TYPE_ID    | NUMBER(5)       | NOT NULL, FK → LEAVE_TYPES(LEAVE_TYPE_ID)        |
| ACCRUAL_DATE     | DATE            | NOT NULL                                         |
| ACCRUAL_AMOUNT   | NUMBER(6,2)     | NOT NULL                                         |
| BALANCE_AFTER    | NUMBER(6,2)     | nullable                                         |
| RUN_ID           | NUMBER(10)      | nullable (references a batch run, not FK defined)|
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                         |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                        |

Constraints: PK_LEAVE_ACCRUAL_LOG (ACCRUAL_ID), FK_LAL_EMP → EMPLOYEES(EMP_ID), FK_LAL_TYPE → LEAVE_TYPES(LEAVE_TYPE_ID)

---

**Table: HRMS.HOLIDAYS**

| Column           | Data Type       | Constraints / Default        |
|------------------|-----------------|------------------------------|
| HOLIDAY_ID       | NUMBER(5)       | NOT NULL, PK                 |
| HOLIDAY_DATE     | DATE            | NOT NULL                     |
| HOLIDAY_NAME     | VARCHAR2(100)   | NOT NULL                     |
| LOCATION_CODE    | VARCHAR2(10)    | nullable (NULL = global)     |
| FLOATING_FLAG    | CHAR(1)         | DEFAULT 'N'                  |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'        |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                     |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE    |

Constraints: PK_HOLIDAYS (HOLIDAY_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/04_performance_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.REVIEW_CYCLES**

| Column              | Data Type       | Constraints / Default                                                  |
|---------------------|-----------------|------------------------------------------------------------------------|
| CYCLE_ID            | NUMBER(10)      | NOT NULL, PK                                                           |
| CYCLE_NAME          | VARCHAR2(100)   | NOT NULL                                                               |
| CYCLE_YEAR          | NUMBER(4)       | NOT NULL                                                               |
| START_DATE          | DATE            | NOT NULL                                                               |
| END_DATE            | DATE            | NOT NULL                                                               |
| SELF_REVIEW_DUE     | DATE            | nullable                                                               |
| MANAGER_REVIEW_DUE  | DATE            | nullable                                                               |
| CALIBRATION_DUE     | DATE            | nullable                                                               |
| STATUS              | VARCHAR2(20)    | DEFAULT 'DRAFT', CHECK IN ('DRAFT','OPEN','IN_PROGRESS','CALIBRATION','CLOSED') |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                               |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                              |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                               |
| MODIFIED_DATE       | DATE            | nullable                                                               |

Constraints: PK_REVIEW_CYCLES (CYCLE_ID), CHK_CYCLE_STATUS

---

**Table: HRMS.PERFORMANCE_REVIEWS**

| Column                 | Data Type       | Constraints / Default                                                                                 |
|------------------------|-----------------|-------------------------------------------------------------------------------------------------------|
| REVIEW_ID              | NUMBER(10)      | NOT NULL, PK                                                                                          |
| CYCLE_ID               | NUMBER(10)      | NOT NULL, FK → REVIEW_CYCLES(CYCLE_ID)                                                                |
| EMP_ID                 | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                      |
| REVIEWER_EMP_ID        | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                      |
| REVIEW_TYPE            | VARCHAR2(20)    | DEFAULT 'ANNUAL'                                                                                      |
| STATUS                 | VARCHAR2(20)    | DEFAULT 'NOT_STARTED', CHECK IN ('NOT_STARTED','SELF_REVIEW','MANAGER_REVIEW','MEETING_SCHEDULED','COMPLETED','ACKNOWLEDGED') |
| OVERALL_RATING         | NUMBER(2,1)     | nullable, CHECK BETWEEN 1.0 AND 5.0                                                                   |
| RATING_LABEL           | VARCHAR2(50)    | nullable                                                                                              |
| SELF_ASSESSMENT        | CLOB            | nullable                                                                                              |
| MANAGER_ASSESSMENT     | CLOB            | nullable                                                                                              |
| STRENGTHS              | CLOB            | nullable                                                                                              |
| AREAS_FOR_IMPROVEMENT  | CLOB            | nullable                                                                                              |
| DEVELOPMENT_PLAN       | CLOB            | nullable                                                                                              |
| EMPLOYEE_COMMENTS      | CLOB            | nullable                                                                                              |
| EMPLOYEE_ACK_DATE      | DATE            | nullable                                                                                              |
| CALIBRATED_RATING      | NUMBER(2,1)     | nullable                                                                                              |
| CALIBRATION_NOTES      | VARCHAR2(4000)  | nullable                                                                                              |
| CREATED_BY             | VARCHAR2(30)    | NOT NULL                                                                                              |
| CREATED_DATE           | DATE            | NOT NULL, DEFAULT SYSDATE                                                                             |
| MODIFIED_BY            | VARCHAR2(30)    | nullable                                                                                              |
| MODIFIED_DATE          | DATE            | nullable                                                                                              |

Constraints: PK_PERFORMANCE_REVIEWS (REVIEW_ID), FK_PR_CYCLE → REVIEW_CYCLES(CYCLE_ID), FK_PR_EMP → EMPLOYEES(EMP_ID), FK_PR_REVIEWER → EMPLOYEES(EMP_ID), CHK_REVIEW_STATUS, CHK_RATING_RANGE (OVERALL_RATING BETWEEN 1.0 AND 5.0)

Business Rule: Rating must be between 1.0 and 5.0 inclusive.

---

**Table: HRMS.PERFORMANCE_GOALS**

| Column            | Data Type       | Constraints / Default                                                                               |
|-------------------|-----------------|-----------------------------------------------------------------------------------------------------|
| GOAL_ID           | NUMBER(10)      | NOT NULL, PK                                                                                        |
| REVIEW_ID         | NUMBER(10)      | NOT NULL, FK → PERFORMANCE_REVIEWS(REVIEW_ID)                                                       |
| EMP_ID            | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                    |
| GOAL_TITLE        | VARCHAR2(200)   | NOT NULL                                                                                            |
| GOAL_DESCRIPTION  | CLOB            | nullable                                                                                            |
| GOAL_CATEGORY     | VARCHAR2(30)    | nullable, CHECK IN ('BUSINESS','DEVELOPMENT','LEADERSHIP','INNOVATION','COMPLIANCE')                |
| WEIGHT_PCT        | NUMBER(5,2)     | DEFAULT 0                                                                                           |
| TARGET_DATE       | DATE            | nullable                                                                                            |
| STATUS            | VARCHAR2(20)    | DEFAULT 'NOT_STARTED', CHECK IN ('NOT_STARTED','IN_PROGRESS','COMPLETED','DEFERRED','CANCELLED')    |
| PROGRESS_PCT      | NUMBER(5,2)     | DEFAULT 0                                                                                           |
| SELF_RATING       | NUMBER(2,1)     | nullable                                                                                            |
| MANAGER_RATING    | NUMBER(2,1)     | nullable                                                                                            |
| COMMENTS          | CLOB            | nullable                                                                                            |
| CREATED_BY        | VARCHAR2(30)    | NOT NULL                                                                                            |
| CREATED_DATE      | DATE            | NOT NULL, DEFAULT SYSDATE                                                                           |
| MODIFIED_BY       | VARCHAR2(30)    | nullable                                                                                            |
| MODIFIED_DATE     | DATE            | nullable                                                                                            |

Constraints: PK_PERF_GOALS (GOAL_ID), FK_PG_REVIEW → PERFORMANCE_REVIEWS(REVIEW_ID), FK_PG_EMP → EMPLOYEES(EMP_ID), CHK_GOAL_STATUS, CHK_GOAL_CATEGORY

---

**Table: HRMS.AUDIT_LOG**

| Column         | Data Type       | Constraints / Default                             |
|----------------|-----------------|---------------------------------------------------|
| AUDIT_ID       | NUMBER(15)      | NOT NULL, PK                                      |
| TABLE_NAME     | VARCHAR2(60)    | NOT NULL                                          |
| RECORD_ID      | NUMBER(15)      | NOT NULL                                          |
| ACTION_TYPE    | VARCHAR2(10)    | NOT NULL, CHECK IN ('INSERT','UPDATE','DELETE')   |
| OLD_VALUES     | CLOB            | nullable                                          |
| NEW_VALUES     | CLOB            | nullable                                          |
| CHANGED_BY     | VARCHAR2(30)    | NOT NULL                                          |
| CHANGED_DATE   | DATE            | NOT NULL, DEFAULT SYSDATE                         |
| IP_ADDRESS     | VARCHAR2(50)    | nullable                                          |
| SESSION_ID     | VARCHAR2(100)   | nullable                                          |

Constraints: PK_AUDIT_LOG (AUDIT_ID), CHK_AUDIT_ACTION

---

**Table: HRMS.SYSTEM_PARAMETERS**

| Column            | Data Type       | Constraints / Default                            |
|-------------------|-----------------|--------------------------------------------------|
| PARAM_ID          | NUMBER(5)       | NOT NULL, PK                                     |
| PARAM_GROUP       | VARCHAR2(50)    | NOT NULL                                         |
| PARAM_CODE        | VARCHAR2(50)    | NOT NULL                                         |
| PARAM_VALUE       | VARCHAR2(4000)  | NOT NULL                                         |
| PARAM_DESCRIPTION | VARCHAR2(200)   | nullable                                         |
| DATA_TYPE         | VARCHAR2(20)    | DEFAULT 'VARCHAR2'                               |
| EDITABLE_FLAG     | CHAR(1)         | DEFAULT 'Y'                                      |
| CREATED_BY        | VARCHAR2(30)    | NOT NULL                                         |
| CREATED_DATE      | DATE            | NOT NULL, DEFAULT SYSDATE                        |
| MODIFIED_BY       | VARCHAR2(30)    | nullable                                         |
| MODIFIED_DATE     | DATE            | nullable                                         |

Constraints: PK_SYSTEM_PARAMS (PARAM_ID), UK_PARAM_CODE (PARAM_GROUP, PARAM_CODE)

---

**Table: HRMS.NOTIFICATION_QUEUE**

| Column             | Data Type       | Constraints / Default                                          |
|--------------------|-----------------|----------------------------------------------------------------|
| NOTIFICATION_ID    | NUMBER(15)      | NOT NULL, PK                                                   |
| RECIPIENT_EMP_ID   | NUMBER(10)      | nullable                                                       |
| RECIPIENT_EMAIL    | VARCHAR2(100)   | nullable                                                       |
| NOTIFICATION_TYPE  | VARCHAR2(30)    | NOT NULL, CHECK IN ('EMAIL','IN_APP','SMS')                    |
| SUBJECT            | VARCHAR2(200)   | NOT NULL                                                       |
| BODY               | CLOB            | NOT NULL                                                       |
| STATUS             | VARCHAR2(20)    | DEFAULT 'PENDING', CHECK IN ('PENDING','SENT','FAILED','CANCELLED') |
| PRIORITY           | NUMBER(2)       | DEFAULT 5                                                      |
| SENT_DATE          | DATE            | nullable                                                       |
| ERROR_MESSAGE      | VARCHAR2(4000)  | nullable                                                       |
| RETRY_COUNT        | NUMBER(3)       | DEFAULT 0                                                      |
| REFERENCE_TABLE    | VARCHAR2(60)    | nullable                                                       |
| REFERENCE_ID       | NUMBER(15)      | nullable                                                       |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                       |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                      |

Constraints: PK_NOTIF_QUEUE (NOTIFICATION_ID), CHK_NOTIF_STATUS, CHK_NOTIF_TYPE

---

**Table: HRMS.USER_SESSIONS**

| Column           | Data Type       | Constraints / Default                    |
|------------------|-----------------|------------------------------------------|
| SESSION_ID       | NUMBER(15)      | NOT NULL, PK                             |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)         |
| USERNAME         | VARCHAR2(30)    | NOT NULL                                 |
| LOGIN_TIME       | DATE            | NOT NULL                                 |
| LOGOUT_TIME      | DATE            | nullable                                 |
| IP_ADDRESS       | VARCHAR2(50)    | nullable                                 |
| FORMS_MODULE     | VARCHAR2(100)   | nullable                                 |
| SESSION_STATUS   | VARCHAR2(20)    | DEFAULT 'ACTIVE'                         |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                |

Constraints: PK_USER_SESSIONS (SESSION_ID), FK_US_EMP → EMPLOYEES(EMP_ID)

---

**Table: HRMS.LOOKUP_VALUES**

| Column           | Data Type       | Constraints / Default                          |
|------------------|-----------------|------------------------------------------------|
| LOOKUP_ID        | NUMBER(10)      | NOT NULL, PK                                   |
| LOOKUP_TYPE      | VARCHAR2(50)    | NOT NULL                                       |
| LOOKUP_CODE      | VARCHAR2(50)    | NOT NULL                                       |
| LOOKUP_VALUE     | VARCHAR2(200)   | NOT NULL                                       |
| DISPLAY_ORDER    | NUMBER(5)       | DEFAULT 0                                      |
| PARENT_LOOKUP_ID | NUMBER(10)      | nullable                                       |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                          |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                       |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                      |

Constraints: PK_LOOKUP_VALUES (LOOKUP_ID), UK_LOOKUP (LOOKUP_TYPE, LOOKUP_CODE)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/views/hrms_views.sql ===

**Schema:** HRMS
**Used by:** Oracle Reports (.rdf), Forms LOVs, external reporting tools

---

**View: HRMS.VW_ACTIVE_EMPLOYEES**

Purpose: Denormalized view of active employees with department, job, manager, location, and current salary.

Columns returned:
- e.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME, e.LAST_NAME
- e.FIRST_NAME || ' ' || e.LAST_NAME AS FULL_NAME
- e.EMAIL, e.PHONE_WORK, e.PHONE_MOBILE
- e.HIRE_DATE
- TRUNC(MONTHS_BETWEEN(SYSDATE, e.HIRE_DATE) / 12, 1) AS TENURE_YEARS
- e.EMPLOYMENT_TYPE, e.EMPLOYMENT_STATUS
- e.DEPT_ID, d.DEPT_NAME, d.DEPT_CODE, d.COST_CENTER
- e.JOB_ID, j.JOB_TITLE, j.JOB_CODE
- g.GRADE_ID, g.GRADE_NAME
- e.MANAGER_EMP_ID
- m.FIRST_NAME || ' ' || m.LAST_NAME AS MANAGER_NAME
- e.LOCATION_CODE
- l.LOCATION_NAME, l.CITY, l.STATE_PROVINCE, l.COUNTRY_CODE
- sr.BASE_SALARY AS CURRENT_SALARY
- sr.CURRENCY_CODE, sr.PAY_FREQUENCY

Joins:
- EMPLOYEES e (base)
- JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
- JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID
- JOIN JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID
- LEFT JOIN EMPLOYEES m ON e.MANAGER_EMP_ID = m.EMP_ID
- LEFT JOIN LOCATIONS l ON e.LOCATION_CODE = l.LOCATION_CODE
- LEFT JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE)

WHERE: e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.ACTIVE_FLAG = 'Y'

Tenure formula: TRUNC(MONTHS_BETWEEN(SYSDATE, HIRE_DATE) / 12, 1) — truncated to 1 decimal place in years.

Current salary logic: active salary record (ACTIVE_FLAG='Y') where EFFECTIVE_DATE <= SYSDATE and either END_DATE is NULL or END_DATE > SYSDATE.

---

**View: HRMS.VW_ORG_HIERARCHY**

Purpose: Hierarchical org chart using CONNECT BY.

Warning (from comment): Performance degrades significantly with >500 employees.

Columns: EMP_ID, EMP_NUMBER, FIRST_NAME || ' ' || LAST_NAME AS EMP_NAME, MANAGER_EMP_ID, DEPT_ID, LEVEL AS ORG_LEVEL, SYS_CONNECT_BY_PATH(FIRST_NAME || ' ' || LAST_NAME, ' > ') AS ORG_PATH, CONNECT_BY_ISLEAF AS IS_LEAF

FROM: EMPLOYEES

WHERE: EMPLOYMENT_STATUS = 'ACTIVE'

Hierarchical traversal:
- START WITH MANAGER_EMP_ID IS NULL (top of hierarchy = no manager)
- CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID
- ORDER SIBLINGS BY LAST_NAME

---

**View: HRMS.VW_EMPLOYEE_COMPENSATION**

Purpose: Current compensation with compa-ratio calculation.

Columns:
- e.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME
- d.DEPT_NAME, j.JOB_TITLE, g.GRADE_NAME
- sr.BASE_SALARY
- g.MIN_SALARY AS GRADE_MIN
- g.MAX_SALARY AS GRADE_MAX
- (g.MIN_SALARY + g.MAX_SALARY) / 2 AS GRADE_MIDPOINT
- ROUND(sr.BASE_SALARY / ((g.MIN_SALARY + g.MAX_SALARY) / 2) * 100, 1) AS COMPA_RATIO
- sr.EFFECTIVE_DATE AS SALARY_EFFECTIVE_DATE
- sr.CHANGE_REASON AS LAST_CHANGE_REASON
- sr.CHANGE_PCT AS LAST_CHANGE_PCT

Compa-ratio formula: ROUND(BASE_SALARY / ((MIN_SALARY + MAX_SALARY) / 2) * 100, 1)
- Numerator: BASE_SALARY
- Denominator: (MIN_SALARY + MAX_SALARY) / 2 (grade midpoint)
- Result: percentage, rounded to 1 decimal place.

Joins:
- EMPLOYEES e → DEPARTMENTS d (DEPT_ID)
- EMPLOYEES e → JOB_TITLES j (JOB_ID)
- JOB_TITLES j → JOB_GRADES g (GRADE_ID)
- EMPLOYEES e → SALARY_RECORDS sr (EMP_ID, ACTIVE_FLAG = 'Y')

WHERE: e.EMPLOYMENT_STATUS = 'ACTIVE'

---

**View: HRMS.VW_LEAVE_SUMMARY**

Purpose: Current calendar year leave balances with utilization percentage.

Columns:
- e.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME
- d.DEPT_NAME
- lt.LEAVE_TYPE_NAME
- lb.OPENING_BALANCE
- lb.ACCRUED
- lb.USED
- lb.ADJUSTMENT
- lb.PENDING
- lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT AS AVAILABLE
- ROUND(lb.USED * 100 / NULLIF(lb.OPENING_BALANCE + lb.ACCRUED, 0), 1) AS UTILIZATION_PCT

Note: AVAILABLE formula in this view does NOT subtract PENDING (unlike the virtual column in LEAVE_BALANCES which does subtract PENDING). This is a discrepancy between the view and the table definition.

Utilization formula: ROUND(USED * 100 / NULLIF(OPENING_BALANCE + ACCRUED, 0), 1) — protected against divide-by-zero via NULLIF.

WHERE: lb.CALENDAR_YEAR = EXTRACT(YEAR FROM SYSDATE) AND e.EMPLOYMENT_STATUS = 'ACTIVE'

---

**View: HRMS.VW_PAYROLL_LATEST**

Purpose: Latest approved payroll run details per employee with gross/tax/deduction/net breakdown.

Columns:
- pd.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME
- pp.PERIOD_NAME
- SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY
- SUM(CASE WHEN pd.ELEMENT_TYPE = 'TAX' THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_TAXES
- SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS
- SUM(pd.AMOUNT) AS NET_PAY

Logic:
- "Latest" is determined by: pr.RUN_ID = (SELECT MAX(pr2.RUN_ID) FROM PAYROLL_RUNS pr2 WHERE pr2.STATUS = 'APPROVED')
- Excludes detail rows with pd.STATUS = 'ERROR'
- TAX and DEDUCTION/BENEFIT amounts are shown as absolute values (ABS)
- NET_PAY = sum of all signed amounts (earnings positive, deductions/taxes negative)

GROUP BY: pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME

---

**View: HRMS.VW_PENDING_APPROVALS**

Purpose: Unified view of items pending approval across leave and performance modules.

Columns: APPROVAL_TYPE, ITEM_ID, APPROVER_ID, REQUESTOR_NAME, ITEM_DESCRIPTION, REQUEST_DATE, DETAILS

Part 1 — Leave requests:
- APPROVAL_TYPE = 'LEAVE'
- ITEM_ID = lr.REQUEST_ID
- APPROVER_ID = lr.APPROVER_EMP_ID
- REQUESTOR_NAME = e.FIRST_NAME || ' ' || e.LAST_NAME
- ITEM_DESCRIPTION = lt.LEAVE_TYPE_NAME
- REQUEST_DATE = lr.CREATED_DATE
- DETAILS = lr.TOTAL_DAYS || ' day(s) ' || TO_CHAR(lr.START_DATE, 'MM/DD') || '-' || TO_CHAR(lr.END_DATE, 'MM/DD')
- WHERE lr.STATUS = 'PENDING'

Part 2 — Performance reviews:
- APPROVAL_TYPE = 'PERFORMANCE'
- ITEM_ID = pr.REVIEW_ID
- APPROVER_ID = pr.REVIEWER_EMP_ID
- REQUESTOR_NAME = e.FIRST_NAME || ' ' || e.LAST_NAME
- ITEM_DESCRIPTION = 'Performance Review - ' || rc.CYCLE_NAME
- REQUEST_DATE = pr.CREATED_DATE
- DETAILS = pr.STATUS
- WHERE pr.STATUS = 'MANAGER_REVIEW'

Combined via UNION ALL.


