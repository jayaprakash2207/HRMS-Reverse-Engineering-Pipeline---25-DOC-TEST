=== CHUNK METADATA ===
Chunk: 18            (chunk count is budget-driven, not a fixed file count)
Type group: seed
Expected files (1):
  1. [seed] ts-plsql-oracle-forms-hrms-main/data/seed/01_reference_data.sql (13084 chars written)
Total source content: 22241 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/data/seed/01_reference_data.sql ===

**IDENTITY:**
  KIND: seed data
  PURPOSE: reference data load for locations, job grades, departments, job titles, leave types, pay elements, holidays, and system parameters (run order 01, before employee data)

**STRUCTURES:**
  **LOCATIONS — all rows:**
  | LOCATION_CODE | LOCATION_NAME | ADDRESS_LINE1 | CITY | STATE_PROVINCE | POSTAL_CODE | COUNTRY_CODE | PHONE | ACTIVE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|---|---|---|---|
  | HQ | Corporate Headquarters | 100 Main Street | New York | NY | 10001 | US | 212-555-1000 | Y | SYSTEM | SYSDATE |
  | CHI | Chicago Regional Office | 200 Michigan Avenue | Chicago | IL | 60601 | US | 312-555-2000 | Y | SYSTEM | SYSDATE |
  | SF | San Francisco Branch | 50 California Street | San Francisco | CA | 94111 | US | 415-555-3000 | Y | SYSTEM | SYSDATE |

  **JOB_GRADES — all rows (salary bands are business rules):**
  | GRADE_ID | GRADE_NAME | GRADE_LEVEL | MIN_SALARY | MAX_SALARY | ACTIVE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|---|
  | 1 | Entry Level | 1 | 35000 | 55000 | Y | SYSTEM | SYSDATE |
  | 2 | Junior | 2 | 45000 | 70000 | Y | SYSTEM | SYSDATE |
  | 3 | Mid-Level | 3 | 60000 | 90000 | Y | SYSTEM | SYSDATE |
  | 4 | Senior | 4 | 80000 | 120000 | Y | SYSTEM | SYSDATE |
  | 5 | Lead | 5 | 95000 | 145000 | Y | SYSTEM | SYSDATE |
  | 6 | Manager | 6 | 110000 | 170000 | Y | SYSTEM | SYSDATE |
  | 7 | Senior Manager | 7 | 130000 | 200000 | Y | SYSTEM | SYSDATE |
  | 8 | Director | 8 | 160000 | 250000 | Y | SYSTEM | SYSDATE |
  | 9 | VP | 9 | 200000 | 350000 | Y | SYSTEM | SYSDATE |
  | 10 | C-Suite | 10 | 300000 | 600000 | Y | SYSTEM | SYSDATE |

  **DEPARTMENTS — all rows:**
  | DEPT_ID | DEPT_CODE | DEPT_NAME | COST_CENTER | PARENT_DEPT_ID | MANAGER_EMP_ID | LOCATION_CODE | ACTIVE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|---|---|---|
  | 1 | EXEC | Executive Office | CC-1000 | NULL | NULL | HQ | Y | SYSTEM | SYSDATE |
  | 10 | HR | Human Resources | CC-1100 | 1 | NULL | HQ | Y | SYSTEM | SYSDATE |
  | 20 | FIN | Finance & Accounting | CC-1200 | 1 | NULL | HQ | Y | SYSTEM | SYSDATE |
  | 30 | IT | Information Technology | CC-1300 | 1 | NULL | CHI | Y | SYSTEM | SYSDATE |
  | 31 | ITDEV | IT - Development | CC-1310 | 30 | NULL | CHI | Y | SYSTEM | SYSDATE |
  | 32 | ITOPS | IT - Operations | CC-1320 | 30 | NULL | CHI | Y | SYSTEM | SYSDATE |
  | 40 | SALES | Sales | CC-1400 | 1 | NULL | SF | Y | SYSTEM | SYSDATE |
  | 50 | MKT | Marketing | CC-1500 | 1 | NULL | SF | Y | SYSTEM | SYSDATE |
  | 60 | OPS | Operations | CC-1600 | 1 | NULL | CHI | Y | SYSTEM | SYSDATE |
  | 70 | LEGAL | Legal & Compliance | CC-1700 | 1 | NULL | HQ | Y | SYSTEM | SYSDATE |

  **JOB_TITLES — all rows:**
  | JOB_ID | JOB_CODE | JOB_TITLE | GRADE_ID | EEO_CATEGORY | ACTIVE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|---|
  | 1 | CEO | Chief Executive Officer | 10 | 1.1 | Y | SYSTEM | SYSDATE |
  | 2 | CFO | Chief Financial Officer | 10 | 1.1 | Y | SYSTEM | SYSDATE |
  | 3 | CIO | Chief Information Officer | 10 | 1.1 | Y | SYSTEM | SYSDATE |
  | 10 | VP-HR | VP of Human Resources | 9 | 1.1 | Y | SYSTEM | SYSDATE |
  | 11 | VP-FIN | VP of Finance | 9 | 1.1 | Y | SYSTEM | SYSDATE |
  | 12 | VP-SALES | VP of Sales | 9 | 1.1 | Y | SYSTEM | SYSDATE |
  | 20 | DIR-IT | Director of IT | 8 | 1.2 | Y | SYSTEM | SYSDATE |
  | 21 | DIR-HR | Director of HR | 8 | 1.2 | Y | SYSTEM | SYSDATE |
  | 30 | MGR-DEV | Development Manager | 6 | 1.2 | Y | SYSTEM | SYSDATE |
  | 31 | MGR-OPS | Operations Manager | 6 | 1.2 | Y | SYSTEM | SYSDATE |
  | 32 | MGR-PAY | Payroll Manager | 6 | 1.2 | Y | SYSTEM | SYSDATE |
  | 33 | MGR-SALES | Sales Manager | 6 | 1.2 | Y | SYSTEM | SYSDATE |
  | 40 | SR-DEV | Senior Developer | 4 | 2.0 | Y | SYSTEM | SYSDATE |
  | 41 | SR-DBA | Senior DBA | 4 | 2.0 | Y | SYSTEM | SYSDATE |
  | 42 | SR-ACCT | Senior Accountant | 4 | 2.0 | Y | SYSTEM | SYSDATE |
  | 43 | SR-SALES | Senior Sales Rep | 4 | 2.0 | Y | SYSTEM | SYSDATE |
  | 50 | DEV | Software Developer | 3 | 2.0 | Y | SYSTEM | SYSDATE |
  | 51 | QA | QA Analyst | 3 | 2.0 | Y | SYSTEM | SYSDATE |
  | 52 | ACCT | Accountant | 3 | 2.0 | Y | SYSTEM | SYSDATE |
  | 53 | HR-SPEC | HR Specialist | 3 | 2.0 | Y | SYSTEM | SYSDATE |
  | 54 | SALES-REP | Sales Representative | 3 | 2.0 | Y | SYSTEM | SYSDATE |
  | 60 | JR-DEV | Junior Developer | 2 | 2.0 | Y | SYSTEM | SYSDATE |
  | 61 | HR-ASST | HR Assistant | 2 | 5.0 | Y | SYSTEM | SYSDATE |
  | 62 | ACCT-CLK | Accounting Clerk | 2 | 5.0 | Y | SYSTEM | SYSDATE |
  | 70 | INTERN | Intern | 1 | 2.0 | Y | SYSTEM | SYSDATE |
  | 71 | RECEPT | Receptionist | 1 | 5.0 | Y | SYSTEM | SYSDATE |

  **LEAVE_TYPES — all rows:**
  | LEAVE_TYPE_ID | LEAVE_TYPE_CODE | LEAVE_TYPE_NAME | ACCRUAL_FLAG | ACCRUAL_RATE | ACCRUAL_FREQUENCY | MAX_BALANCE | CARRYOVER_MAX | CARRYOVER_EXPIRY | REQUIRES_APPROVAL | MIN_TENURE_DAYS | ACTIVE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | 1 | PTO | Paid Time Off | Y | 1.25 | MONTHLY | 20 | 5 | 3 | Y | 0 | Y | SYSTEM | SYSDATE |
  | 2 | SICK | Sick Leave | Y | 0.833 | MONTHLY | 10 | 10 | NULL | Y | 0 | Y | SYSTEM | SYSDATE |
  | 3 | COMP | Compensatory Time | N | NULL | NULL | NULL | 0 | NULL | Y | 90 | Y | SYSTEM | SYSDATE |
  | 4 | FMLA | Family Medical Leave | N | NULL | NULL | NULL | 0 | NULL | Y | 365 | Y | SYSTEM | SYSDATE |
  | 5 | JURY | Jury Duty | N | NULL | NULL | NULL | 0 | NULL | N | 0 | Y | SYSTEM | SYSDATE |
  | 6 | BEREAVE | Bereavement | N | NULL | NULL | NULL | 0 | NULL | N | 0 | Y | SYSTEM | SYSDATE |

  **PAY_ELEMENTS — all rows:**
  | ELEMENT_ID | ELEMENT_CODE | ELEMENT_NAME | ELEMENT_TYPE | CALCULATION_TYPE | DEFAULT_AMOUNT | DEFAULT_PERCENTAGE | GL_ACCOUNT_CODE | PRIORITY_ORDER | PRETAX_FLAG | ACTIVE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | 1 | BASE_PAY | Base Salary | EARNING | FLAT | NULL | NULL | 5100-100 | 1 | N | Y | SYSTEM | SYSDATE |
  | 100 | FED_TAX | Federal Income Tax | TAX | FORMULA | NULL | NULL | 2100-100 | 10 | N | Y | SYSTEM | SYSDATE |
  | 101 | STATE_TAX | State Income Tax | TAX | FORMULA | NULL | NULL | 2100-200 | 11 | N | Y | SYSTEM | SYSDATE |
  | 102 | FICA | Social Security (FICA) | TAX | FORMULA | NULL | NULL | 2100-300 | 12 | N | Y | SYSTEM | SYSDATE |
  | 103 | MEDICARE | Medicare | TAX | FORMULA | NULL | NULL | 2100-400 | 13 | N | Y | SYSTEM | SYSDATE |
  | 200 | 401K_EE | 401(k) Employee Contribution | DEDUCTION | PERCENTAGE | NULL | 6 | 2200-100 | 20 | Y | Y | SYSTEM | SYSDATE |
  | 201 | MED_EE | Medical Insurance (Employee) | BENEFIT | FLAT | 250 | NULL | 2200-200 | 21 | Y | Y | SYSTEM | SYSDATE |
  | 202 | DENTAL_EE | Dental Insurance (Employee) | BENEFIT | FLAT | 45 | NULL | 2200-300 | 22 | Y | Y | SYSTEM | SYSDATE |
  | 203 | VISION_EE | Vision Insurance (Employee) | BENEFIT | FLAT | 15 | NULL | 2200-400 | 23 | Y | Y | SYSTEM | SYSDATE |
  | 204 | LIFE_INS | Life Insurance | BENEFIT | FLAT | 25 | NULL | 2200-500 | 24 | N | Y | SYSTEM | SYSDATE |
  | 205 | HSA | Health Savings Account | DEDUCTION | FLAT | 150 | NULL | 2200-600 | 25 | Y | Y | SYSTEM | SYSDATE |

  **HOLIDAYS — all rows (section header at L156 reads "HOLIDAYS (2024-2025)" but only 2024 rows are loaded):**
  | HOLIDAY_ID | HOLIDAY_NAME | HOLIDAY_DATE | LOCATION_CODE | ACTIVE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|
  | 1 | New Year's Day | 2024-01-01 | NULL | Y | SYSTEM | SYSDATE |
  | 2 | Martin Luther King Jr. Day | 2024-01-15 | NULL | Y | SYSTEM | SYSDATE |
  | 3 | Presidents' Day | 2024-02-19 | NULL | Y | SYSTEM | SYSDATE |
  | 4 | Memorial Day | 2024-05-27 | NULL | Y | SYSTEM | SYSDATE |
  | 5 | Independence Day | 2024-07-04 | NULL | Y | SYSTEM | SYSDATE |
  | 6 | Labor Day | 2024-09-02 | NULL | Y | SYSTEM | SYSDATE |
  | 7 | Thanksgiving | 2024-11-28 | NULL | Y | SYSTEM | SYSDATE |
  | 8 | Day After Thanksgiving | 2024-11-29 | NULL | Y | SYSTEM | SYSDATE |
  | 9 | Christmas Eve | 2024-12-24 | NULL | Y | SYSTEM | SYSDATE |
  | 10 | Christmas Day | 2024-12-25 | NULL | Y | SYSTEM | SYSDATE |

  **SYSTEM_PARAMETERS — all rows:**
  | PARAM_ID | PARAM_GROUP | PARAM_CODE | PARAM_VALUE | DESCRIPTION | EDITABLE_FLAG | CREATED_BY | CREATED_DATE |
  |---|---|---|---|---|---|---|---|
  | 1 | SYSTEM | APP_VERSION | 4.2.0 | Application version | N | SYSTEM | SYSDATE |
  | 2 | SYSTEM | COMPANY_NAME | Acme Corporation | Company name | Y | SYSTEM | SYSDATE |
  | 3 | PAYROLL | DEFAULT_PAY_FREQUENCY | MONTHLY | Default payroll frequency | Y | SYSTEM | SYSDATE |
  | 4 | PAYROLL | FISCAL_YEAR_START | 10 | Fiscal year start month | Y | SYSTEM | SYSDATE |
  | 5 | SECURITY | SESSION_TIMEOUT_MIN | 30 | Session timeout in minutes | Y | SYSTEM | SYSDATE |
  | 6 | SECURITY | PASSWORD_MIN_LENGTH | 8 | Minimum password length | Y | SYSTEM | SYSDATE |
  | 7 | NOTIFICATION | SMTP_HOST | smtp.internal.company.com | SMTP server hostname | Y | SYSTEM | SYSDATE |
  | 8 | NOTIFICATION | FROM_ADDRESS | hrms-noreply@company.com | Default from address | Y | SYSTEM | SYSDATE |
  | 9 | INTEGRATION | GL_FEED_STATUS | ACTIVE | GL integration status | Y | SYSTEM | SYSDATE |
  | 10 | INTEGRATION | BENEFITS_FEED_STATUS | ACTIVE | Benefits feed status | Y | SYSTEM | SYSDATE |

**METHODS:**
  **FILE-LEVEL EFFECT** [SOURCE: L1-203]
  - What it does: A SQL*Plus seed script (`SET DEFINE OFF` at L6 disables `&`-substitution so literal text like addresses isn't misinterpreted) that runs before employee data load (per the L3 run-order comment). It inserts, in order: 3 LOCATIONS rows, 10 JOB_GRADES rows, 10 DEPARTMENTS rows, 26 JOB_TITLES rows, 6 LEAVE_TYPES rows, 11 PAY_ELEMENTS rows, 10 HOLIDAYS rows, and 10 SYSTEM_PARAMETERS rows, then COMMITs at L203.
  - Business rules: Every JOB_TITLES row's GRADE_ID must reference an existing JOB_GRADES.GRADE_ID (e.g. CEO/CFO/CIO → grade 10, INTERN/RECEPT → grade 1). Every non-root DEPARTMENTS row's PARENT_DEPT_ID references another DEPARTMENTS row (e.g. ITDEV/ITOPS → parent 30/IT); all MANAGER_EMP_ID values are NULL at seed time (assigned later once employees exist). Each DEPARTMENTS row's LOCATION_CODE must reference a seeded LOCATIONS row. All HOLIDAYS rows have LOCATION_CODE = NULL, i.e. company-wide holidays. LEAVE_TYPES.REQUIRES_APPROVAL is 'Y' for PTO/SICK/COMP/FMLA and 'N' for JURY/BEREAVE. PAY_ELEMENTS.PRETAX_FLAG is 'Y' for the 401K_EE, MED_EE, DENTAL_EE, VISION_EE, and HSA elements, and 'N' for BASE_PAY, the four TAX elements, and LIFE_INS.
  - Numbers & thresholds: The section header comment at L156 reads "HOLIDAYS (2024-2025)" — referencing fiscal/calendar years 2024 and 2025 — but only 2024-dated rows (HOLIDAY_ID 1-10, 2024-01-01 through 2024-12-25) are actually inserted; no 2025 holiday rows exist in this file. JOB_GRADES salary bands and all other numeric seed values are reproduced verbatim in the tables above, including: LEAVE_TYPES accrual rates 1.25 (PTO, MONTHLY) and 0.833 (SICK, MONTHLY); MAX_BALANCE caps 20 (PTO) and 10 (SICK); CARRYOVER_MAX 5 (PTO), 10 (SICK), 0 (COMP/FMLA/JURY/BEREAVE); CARRYOVER_EXPIRY 3 months (PTO only); MIN_TENURE_DAYS 90 (COMP) and 365 (FMLA); PAY_ELEMENTS DEFAULT_PERCENTAGE 6 (401K_EE) and DEFAULT_AMOUNT 250/45/15/25/150 (MED_EE/DENTAL_EE/VISION_EE/LIFE_INS/HSA); SYSTEM_PARAMETERS APP_VERSION '4.2.0', FISCAL_YEAR_START month 10, SESSION_TIMEOUT_MIN 30, PASSWORD_MIN_LENGTH 8.
  - Security & error handling: None — no exception handling; a PK or FK violation on any INSERT would abort the script before the single COMMIT at L203, leaving no partial data committed for this run.
  - Data in/out: No inputs (all values are hardcoded literals plus SYSDATE). Output — rows inserted into LOCATIONS, JOB_GRADES, DEPARTMENTS, JOB_TITLES, LEAVE_TYPES, PAY_ELEMENTS, HOLIDAYS, and SYSTEM_PARAMETERS as listed above, then committed.

**DEPENDENCIES:**
  Data touched:
  - Reads: None
  - Writes: LOCATIONS — 3 location rows; JOB_GRADES — 10 grade/salary-band rows; DEPARTMENTS — 10 department rows; JOB_TITLES — 26 job title rows; LEAVE_TYPES — 6 leave type rows; PAY_ELEMENTS — 11 pay element rows; HOLIDAYS — 10 holiday rows; SYSTEM_PARAMETERS — 10 parameter rows

  Config/env: SYSTEM_PARAMETERS rows themselves seed application config values (APP_VERSION, COMPANY_NAME, DEFAULT_PAY_FREQUENCY, FISCAL_YEAR_START, SESSION_TIMEOUT_MIN, PASSWORD_MIN_LENGTH, SMTP_HOST, FROM_ADDRESS, GL_FEED_STATUS, BENEFITS_FEED_STATUS) that other components presumably read at runtime.
  External integrations: None called directly by this file; SMTP_HOST/FROM_ADDRESS and GL_FEED_STATUS/BENEFITS_FEED_STATUS are seeded status/config values for notification and GL/benefits feed integrations implemented elsewhere.

**GAPS:**
  UNRESOLVED: L156's section comment "HOLIDAYS (2024-2025)" implies 2025 holidays should also be seeded, but no 2025-dated HOLIDAYS rows appear in this file — unclear whether they were dropped, deferred to a later script, or the comment is simply stale. NOT_ANALYZED: which downstream files/components consume the SYSTEM_PARAMETERS config keys.

*[pipeline status — type: seed · pass: correction · attempt: 2 · coverage: 100% (numbers 103/103 · tables 8/8 · units 1/1 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 1
Files delivered: 1
  Full coverage on first pass: 0
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/data/seed/01_reference_data.sql
  Still incomplete after max attempts: 0
Raw source: 22241 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===