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
