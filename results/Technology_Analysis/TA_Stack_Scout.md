transfer_employee, promote_employee, terminate_employee, rehire_employee, get_direct_reports, get_org_chart, get_headcount_by_dept, get_tenure_years, is_active, validate_employee, emp_exists, generate_emp_number, set_session_context + all PKG_PAYROLL, PKG_LEAVE, PKG_PERFORMANCE, PKG_SECURITY, PKG_REPORTING, PKG_COMMON, PKG_VALIDATION, PKG_INTEGRATION, PKG_AUDIT methods).

**Oracle Forms Modules (6 XML exports provided of 18 declared in README):**

| Form File | Purpose | Libraries Attached | Menu Module |
|---|---|---|---|
| HRMS_LOGIN.fmb | Authentication entry point | None | None |
| HRMS_MENU.fmb | MDI shell / navigation hub | HRMS_COMMON_LIB | MENU_MAIN |
| HRMS_EMPLOYEE.fmb | Employee master-detail maintenance | HRMS_COMMON_LIB, HRMS_VALIDATION_LIB | HRMS_MENU |
| HRMS_LEAVE.fmb | Leave request, approval, balance | HRMS_COMMON_LIB | HRMS_MENU |
| HRMS_PAYROLL.fmb | Pay period, payroll runs, approval | HRMS_COMMON_LIB | HRMS_MENU |
| HRMS_PERFORMANCE.fmb | Review cycles, goals, ratings | HRMS_COMMON_LIB | HRMS_MENU |

**Forms not in provided source (referenced via OPEN_FORM in menu):**
- HRMS_REPORTS — report parameter launcher
- HRMS_ADMIN — system administration
- HRMS_DEPARTMENT — department management

**PLL Libraries:**

| Library | Purpose | Dependencies |
|---|---|---|
| HRMS_COMMON_LIB.pll | Toolbar navigation, error handling, session check, date/name formatting | PKG_COMMON.log_error, PKG_SECURITY.is_session_valid |
| HRMS_VALIDATION_LIB.pll | Client-side field validation (email, phone, SSN, salary range, future date) | JOB_GRADES table (direct SELECT) |

**Oracle Forms Trigger Types observed:**
- WHEN-NEW-FORM-INSTANCE, WHEN-VALIDATE-ITEM, WHEN-BUTTON-PRESSED, POST-QUERY, PRE-INSERT, PRE-UPDATE, ON-ERROR, KEY-EXIT, KEY-NEXT-ITEM

**Oracle Built-in Packages used in application layer:**
- DBMS_CRYPTO (hash/encrypt/decrypt — HASH_MD5, ENCRYPT_AES256+CBC+PKCS5)
- DBMS_OUTPUT (debug/fallback logging)
- DBMS_SCHEDULER (implied — process_queue every 5 min, run_monthly_accrual 1st of month)
- UTL_FILE (file I/O — PAYROLL_OUTPUT, GL_FEED_OUT, BENEFITS_FEED_OUT, TIME_ATTENDANCE_IN directory objects)
- UTL_SMTP (email delivery — smtp.internal.company.com:25)
- UTL_RAW (crypto support)
- SYS_CONTEXT (IP_ADDRESS, SESSIONID — audit logging)

**Custom exception code ranges:**
- -20001 to -20005: PKG_EMPLOYEE
- -20010 to -20012: PKG_EMPLOYEE (create/transfer)
- -20101 to -20104: PKG_PAYROLL
- -20201 to -20204: PKG_LEAVE
- -20301 to -20304: PKG_SECURITY
- -20310 to -20312: PKG_SECURITY (password)
- -20401 to -20403: PKG_PERFORMANCE
- -20501 to -20504: Database triggers (TRG_EMP_*)
- -20900: PKG_COMMON (set_param non-editable)

**DISCREPANCY — Hire date future limit:**
- HRMS_EMPLOYEE.xml WHEN-VALIDATE-ITEM: `HIRE_DATE > SYSDATE + 90` → 90 days
- TRG_EMP_BEFORE_INSERT: `HIRE_DATE > SYSDATE + 180` → 180 days
- **DISC-001: hire date future limit declared as 90 days in Forms trigger; 180 days in database trigger. Both sources provided. Agent 2 to determine authoritative rule.**

**DISCREPANCY — EMPLOYEE_HISTORY column structure:**
- DDL (01_core_tables.sql): columns EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, etc. (typed columns)
- TRG_EMP_BEFORE_UPDATE: inserts into CHANGE_DATE, OLD_VALUE (VARCHAR2), NEW_VALUE (VARCHAR2) — flat string columns
- **DISC-002: trigger and DDL describe different column layouts for EMPLOYEE_HISTORY. Agent 2 to determine which is authoritative.**

---

### Chunk Inventory — Application Layer
- Technology components found: PL/SQL 19c (Oracle), Oracle Forms 12c (12.2.1.4), Oracle Forms PLL libraries ×2, DBMS_CRYPTO, DBMS_SCHEDULER, UTL_FILE, UTL_SMTP, UTL_RAW, SYS_CONTEXT, DBMS_OUTPUT
- Data stores found: None new (all Oracle DB HRMS)
- Integrations found: UTL_SMTP → smtp.internal.company.com:25 (email); UTL_FILE → Oracle directory objects PAYROLL_OUTPUT, GL_FEED_OUT, BENEFITS_FEED_OUT, TIME_ATTENDANCE_IN
- CI/CD tool invocations: None
- Reusable workflows followed: None
- Cross-layer dependencies: UTL_FILE Oracle directory objects imply OS filesystem paths set by DBA (no IaC found)
- VERSION CONFLICTS: DISC-001 (hire date), DISC-002 (EMPLOYEE_HISTORY columns)
- LOW CONFIDENCE items: PKG_DEPARTMENT — source not provided; HRMS_REPORTS, HRMS_ADMIN, HRMS_DEPARTMENT forms — not in provided source set

---

## Agent 1 - Chunk 2 of 6 - Data Layer

**Carried Forward:**
- Technology components: Oracle DB 19c, Forms 12c, WebLogic 12c, UTL_FILE, UTL_SMTP, DBMS_CRYPTO, DBMS_SCHEDULER
- Data stores: Oracle Database 19c (HRMS schema)
- Integrations: SMTP, 4 UTL_FILE directory objects
- LOW CONFIDENCE items: 3

---

**Tables — Complete Enumeration:**

**Core Tables (01_core_tables.sql) — 6 tables:**

| Table | Columns | PK | Key Constraints |
|---|---|---|---|
| DEPARTMENTS | DEPT_ID, DEPT_CODE, DEPT_NAME, PARENT_DEPT_ID, COST_CENTER, MANAGER_EMP_ID, LOCATION_CODE, ACTIVE_FLAG, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | DEPT_ID | UK_DEPT_CODE; CHK_DEPT_ACTIVE IN ('Y','N'); self-ref via PARENT_DEPT_ID |
| LOCATIONS | LOCATION_CODE, LOCATION_NAME, ADDRESS_LINE1, ADDRESS_LINE2, CITY, STATE_PROVINCE, POSTAL_CODE, COUNTRY_CODE, PHONE_NUMBER, TIMEZONE (DEFAULT 'America/New_York'), ACTIVE_FLAG, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | LOCATION_CODE | — |
| JOB_GRADES | GRADE_ID, GRADE_CODE, GRADE_NAME, MIN_SALARY NUMBER(12,2), MAX_SALARY NUMBER(12,2), OVERTIME_ELIGIBLE CHAR(1) DEFAULT 'N', ACTIVE_FLAG, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | GRADE_ID | UK_GRADE_CODE; CHK_SALARY_RANGE: MAX_SALARY >= MIN_SALARY |
| JOB_TITLES | JOB_ID, JOB_CODE, JOB_TITLE, JOB_FAMILY, GRADE_ID (FK→JOB_GRADES), EEO_CATEGORY, FLSA_STATUS DEFAULT 'EXEMPT', ACTIVE_FLAG, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | JOB_ID | UK_JOB_CODE; FK_JOB_GRADE |
| EMPLOYEES | EMP_ID, EMP_NUMBER, FIRST_NAME, MIDDLE_NAME, LAST_NAME, DATE_OF_BIRTH, GENDER CHAR(1) CHK IN ('M','F','O'), MARITAL_STATUS, NATIONALITY, SSN_ENCRYPTED VARCHAR2(200), EMAIL, PHONE_WORK, PHONE_MOBILE, ADDRESS_LINE1, ADDRESS_LINE2, CITY, STATE_PROVINCE, POSTAL_CODE, COUNTRY_CODE, HIRE_DATE NOT NULL, TERMINATION_DATE, TERMINATION_REASON, DEPT_ID (FK→DEPARTMENTS), JOB_ID (FK→JOB_TITLES), MANAGER_EMP_ID (FK→EMPLOYEES self-ref), LOCATION_CODE (FK→LOCATIONS), EMPLOYMENT_TYPE DEFAULT 'FULL_TIME' CHK IN ('FULL_TIME','PART_TIME','CONTRACT','INTERN'), EMPLOYMENT_STATUS DEFAULT 'ACTIVE' CHK IN ('ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED'), PHOTO_BLOB BLOB, NOTES CLOB, ACTIVE_FLAG, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | EMP_ID | UK_EMP_NUMBER; FK_EMP_DEPT, FK_EMP_JOB, FK_EMP_MANAGER, FK_EMP_LOCATION; CHK_EMP_STATUS, CHK_EMP_TYPE, CHK_EMP_GENDER |
| EMPLOYEE_HISTORY | HIST_ID NUMBER(15), EMP_ID (FK→EMPLOYEES), CHANGE_TYPE VARCHAR2(30) CHK IN ('HIRE','TRANSFER','PROMOTION','DEMOTION','SALARY_CHANGE','TERMINATION','REHIRE','LEAVE_START','LEAVE_END','STATUS_CHANGE'), EFFECTIVE_DATE NOT NULL, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY NUMBER(12,2), NEW_SALARY NUMBER(12,2), OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS VARCHAR2(4000), CREATED_BY, CREATED_DATE | HIST_ID | FK_HIST_EMP; CHK_CHANGE_TYPE |
| EMPLOYEE_DEPENDENTS | DEPENDENT_ID, EMP_ID (FK→EMPLOYEES), FIRST_NAME, LAST_NAME, RELATIONSHIP CHK IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER'), DATE_OF_BIRTH, SSN_ENCRYPTED VARCHAR2(200), BENEFITS_ENROLLED DEFAULT 'N', ACTIVE_FLAG, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | DEPENDENT_ID | FK_DEP_EMP; CHK_RELATIONSHIP |
| EMERGENCY_CONTACTS | CONTACT_ID, EMP_ID (FK→EMPLOYEES), CONTACT_NAME, RELATIONSHIP, PHONE_PRIMARY NOT NULL, PHONE_SECONDARY, EMAIL, PRIORITY_ORDER DEFAULT 1, ACTIVE_FLAG, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | CONTACT_ID | FK_EC_EMP |

**Payroll Tables (02_payroll_tables.sql) — 8 tables:**

| Table | Columns (key) | PK | Key Constraints |
|---|---|---|---|
| SALARY_RECORDS | SALARY_ID, EMP_ID (FK), EFFECTIVE_DATE, END_DATE, BASE_SALARY NUMBER(12,2) NOT NULL, CURRENCY_CODE DEFAULT 'USD', PAY_FREQUENCY DEFAULT 'MONTHLY' CHK IN ('WEEKLY','BIWEEKLY','SEMIMONTHLY','MONTHLY'), SALARY_BASIS DEFAULT 'ANNUAL' CHK IN ('ANNUAL','HOURLY'), CHANGE_REASON, CHANGE_PCT NUMBER(5,2), APPROVED_BY, APPROVAL_DATE, ACTIVE_FLAG, audit cols | SALARY_ID | FK_SAL_EMP |
| PAY_ELEMENTS | ELEMENT_ID, ELEMENT_CODE UNIQUE, ELEMENT_NAME, ELEMENT_TYPE CHK IN ('EARNING','DEDUCTION','TAX','BENEFIT','REIMBURSEMENT'), CALCULATION_TYPE CHK IN ('FLAT','PERCENTAGE','HOURS','FORMULA'), DEFAULT_AMOUNT NUMBER(12,2), DEFAULT_PERCENTAGE NUMBER(5,2), TAXABLE_FLAG DEFAULT 'Y', PRETAX_FLAG DEFAULT 'N', EMPLOYER_PAID DEFAULT 'N', GL_ACCOUNT_CODE VARCHAR2(30), PRIORITY_ORDER DEFAULT 100, ACTIVE_FLAG, audit cols | ELEMENT_ID | UK_PAY_ELEM_CODE; CHK_ELEM_TYPE; CHK_CALC_TYPE |
| EMPLOYEE_PAY_ELEMENTS | EMP_ELEMENT_ID, EMP_ID (FK), ELEMENT_ID (FK), EFFECTIVE_DATE, END_DATE, AMOUNT NUMBER(12,2), PERCENTAGE NUMBER(5,2), OVERRIDE_AMOUNT NUMBER(12,2), ACTIVE_FLAG, audit cols | EMP_ELEMENT_ID | FK_EPE_EMP; FK_EPE_ELEMENT |
| PAY_PERIODS | PERIOD_ID, PERIOD_NAME, PAY_FREQUENCY, PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE, STATUS DEFAULT 'OPEN' CHK IN ('OPEN','PROCESSING','CLOSED','REVERSED'), CLOSED_BY, CLOSED_DATE, audit cols | PERIOD_ID | CHK_PERIOD_STATUS |
| PAYROLL_RUNS | RUN_ID, PERIOD_ID (FK), RUN_TYPE DEFAULT 'REGULAR' CHK IN ('REGULAR','SUPPLEMENTAL','BONUS','FINAL'), RUN_DATE, STATUS DEFAULT 'PENDING' CHK IN ('PENDING','CALCULATING','CALCULATED','APPROVED','PAID','REVERSED','ERROR'), TOTAL_GROSS NUMBER(15,2), TOTAL_DEDUCTIONS NUMBER(15,2), TOTAL_NET NUMBER(15,2), TOTAL_EMPLOYER_COST NUMBER(15,2), EMPLOYEE_COUNT, ERROR_COUNT DEFAULT 0, SUBMITTED_BY, SUBMITTED_DATE, APPROVED_BY, APPROVED_DATE, audit cols | RUN_ID | FK_PR_PERIOD; CHK_RUN_TYPE; CHK_RUN_STATUS |
| PAYROLL_DETAILS | DETAIL_ID NUMBER(15), RUN_ID (FK), EMP_ID (FK), ELEMENT_ID (FK), ELEMENT_TYPE NOT NULL, HOURS_WORKED NUMBER(6,2), RATE NUMBER(12,4), AMOUNT NUMBER(12,2) NOT NULL, YTD_AMOUNT NUMBER(15,2), STATUS DEFAULT 'CALCULATED', ERROR_MESSAGE VARCHAR2(4000), CREATED_BY, CREATED_DATE | DETAIL_ID | FK_PD_RUN; FK_PD_EMP; FK_PD_ELEMENT |
| TAX_BRACKETS | BRACKET_ID, TAX_YEAR NUMBER(4), FILING_STATUS CHK IN ('SINGLE','MARRIED_JOINT','MARRIED_SEPARATE','HEAD_OF_HOUSEHOLD'), BRACKET_MIN NUMBER(12,2), BRACKET_MAX NUMBER(12,2) nullable=no upper bound, TAX_RATE NUMBER(5,4), BASE_TAX NUMBER(12,2) DEFAULT 0, STATE_CODE VARCHAR2(3) nullable=federal, ACTIVE_FLAG, CREATED_BY, CREATED_DATE | BRACKET_ID | CHK_FILING_STATUS |
| EMPLOYEE_TAX_INFO | TAX_INFO_ID, EMP_ID (FK), TAX_YEAR NUMBER(4), FILING_STATUS, FEDERAL_ALLOWANCES DEFAULT 0, STATE_ALLOWANCES DEFAULT 0, ADDITIONAL_FED_WH DEFAULT 0, ADDITIONAL_STATE_WH DEFAULT 0, EXEMPT_FLAG DEFAULT 'N', STATE_CODE, W4_RECEIVED_DATE, ACTIVE_FLAG, audit cols | TAX_INFO_ID | FK_ETI_EMP; UK_EMP_TAX_YEAR (EMP_ID, TAX_YEAR) |
| EMPLOYEE_BANK_ACCOUNTS | BANK_ACCT_ID, EMP_ID (FK), BANK_NAME, ROUTING_NUMBER NOT NULL, ACCOUNT_NUMBER_ENC VARCHAR2(200) NOT NULL encrypted, ACCOUNT_TYPE DEFAULT 'CHECKING' CHK IN ('CHECKING','SAVINGS'), DEPOSIT_TYPE DEFAULT 'FULL' CHK IN ('FULL','PARTIAL_AMOUNT','PARTIAL_PERCENT','REMAINDER'), DEPOSIT_AMOUNT, DEPOSIT_PERCENTAGE, PRIORITY_ORDER DEFAULT 1, PRENOTE_SENT DEFAULT 'N', PRENOTE_DATE, ACTIVE_FLAG, audit cols | BANK_ACCT_ID | FK_BA_EMP; CHK_ACCT_TYPE; CHK_DEPOSIT_TYPE |

**Leave Tables (03_leave_tables.sql) — 5 tables:**

| Table | Key Columns | PK | Key Constraints |
|---|---|---|---|
| LEAVE_TYPES | LEAVE_TYPE_ID, LEAVE_TYPE_CODE UNIQUE, LEAVE_TYPE_NAME, PAID_FLAG DEFAULT 'Y', ACCRUAL_FLAG DEFAULT 'Y', ACCRUAL_RATE NUMBER(6,2), ACCRUAL_FREQUENCY CHK IN ('MONTHLY','BIWEEKLY','ANNUAL',NULL), MAX_BALANCE NUMBER(6,2), CARRYOVER_MAX NUMBER(6,2), CARRYOVER_EXPIRY NUMBER(3) = months, MIN_TENURE_DAYS DEFAULT 0, REQUIRES_APPROVAL DEFAULT 'Y', REQUIRES_DOCUMENT DEFAULT 'N', ACTIVE_FLAG, audit cols | LEAVE_TYPE_ID | UK_LEAVE_TYPE_CODE; CHK_ACCRUAL_FREQ |
| LEAVE_BALANCES | BALANCE_ID, EMP_ID (FK), LEAVE_TYPE_ID (FK), CALENDAR_YEAR NUMBER(4), OPENING_BALANCE NUMBER(6,2) DEFAULT 0, ACCRUED DEFAULT 0, USED DEFAULT 0, ADJUSTMENT DEFAULT 0, PENDING DEFAULT 0, AVAILABLE **VIRTUAL COLUMN** = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING, CARRYOVER_FROM_PREV DEFAULT 0, CARRYOVER_EXPIRY_DT, CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE | BALANCE_ID | UK_LEAVE_BAL (EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR); FK_LB_EMP; FK_LB_TYPE |
| LEAVE_REQUESTS | REQUEST_ID, EMP_ID (FK), LEAVE_TYPE_ID (FK), START_DATE, END_DATE, TOTAL_DAYS NUMBER(5,1), HALF_DAY_FLAG DEFAULT 'N', HALF_DAY_PERIOD CHK IN ('AM','PM',NULL), STATUS DEFAULT 'PENDING' CHK IN ('PENDING','APPROVED','REJECTED','CANCELLED','TAKEN'), REASON VARCHAR2(4000), SUPPORTING_DOC_PATH, APPROVER_EMP_ID (FK→EMPLOYEES), APPROVAL_DATE, APPROVAL_COMMENTS VARCHAR2(4000), CANCEL_REASON VARCHAR2(4000), CANCELLED_DATE, audit cols | REQUEST_ID | CHK_LR_STATUS; CHK_LR_DATES: END_DATE >= START_DATE; CHK_HALF_DAY |
| LEAVE_ACCRUAL_LOG | ACCRUAL_ID NUMBER(15), EMP_ID (FK), LEAVE_TYPE_ID (FK), ACCRUAL_DATE, ACCRUAL_AMOUNT NUMBER(6,2), BALANCE_AFTER NUMBER(6,2), RUN_ID (no FK defined), CREATED_BY, CREATED_DATE | ACCRUAL_ID | FK_LAL_EMP; FK_LAL_TYPE |
| HOLIDAYS | HOLIDAY_ID, HOLIDAY_DATE, HOLIDAY_NAME, LOCATION_CODE nullable=global if NULL, FLOATING_FLAG DEFAULT 'N', ACTIVE_FLAG, CREATED_BY, CREATED_DATE | HOLIDAY_ID | — |

**Performance / System Tables (04_performance_tables.sql) — 8 tables:**

| Table | Key Columns | PK | Key Constraints |
|---|---|---|---|
| REVIEW_CYCLES | CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, CALIBRATION_DUE, STATUS DEFAULT 'DRAFT' CHK IN ('DRAFT','OPEN','IN_PROGRESS','CALIBRATION','CLOSED'), audit cols | CYCLE_ID | CHK_CYCLE_STATUS |
| PERFORMANCE_REVIEWS | REVIEW_ID, CYCLE_ID (FK), EMP_ID (FK), REVIEWER_EMP_ID (FK), REVIEW_TYPE DEFAULT 'ANNUAL', STATUS DEFAULT 'NOT_STARTED' CHK IN ('NOT_STARTED','SELF_REVIEW','MANAGER_REVIEW','MEETING_SCHEDULED','COMPLETED','ACKNOWLEDGED'), OVERALL_RATING NUMBER(2,1) CHK BETWEEN 1.0 AND 5.0, RATING_LABEL VARCHAR2(50), SELF_ASSESSMENT CLOB, MANAGER_ASSESSMENT CLOB, STRENGTHS CLOB, AREAS_FOR_IMPROVEMENT CLOB, DEVELOPMENT_PLAN CLOB, EMPLOYEE_COMMENTS CLOB, EMPLOYEE_ACK_DATE, CALIBRATED_RATING NUMBER(2,1), CALIBRATION_NOTES VARCHAR2(4000), audit cols | REVIEW_ID | FK_PR_CYCLE; FK_PR_EMP; FK_PR_REVIEWER; CHK_REVIEW_STATUS; CHK_RATING_RANGE |
| PERFORMANCE_GOALS | GOAL_ID, REVIEW_ID (FK), EMP_ID (FK), GOAL_TITLE NOT NULL, GOAL_DESCRIPTION CLOB, GOAL_CATEGORY CHK IN ('BUSINESS','DEVELOPMENT','LEADERSHIP','INNOVATION','COMPLIANCE'), WEIGHT_PCT DEFAULT 0, TARGET_DATE, STATUS DEFAULT 'NOT_STARTED' CHK IN ('NOT_STARTED','IN_PROGRESS','COMPLETED','DEFERRED','CANCELLED'), PROGRESS_PCT DEFAULT 0, SELF_RATING NUMBER(2,1), MANAGER_RATING NUMBER(2,1), COMMENTS CLOB, audit cols | GOAL_ID | FK_PG_REVIEW; FK_PG_EMP; CHK_GOAL_STATUS; CHK_GOAL_CATEGORY |
| AUDIT_LOG | AUDIT_ID NUMBER(15), TABLE_NAME VARCHAR2(60), RECORD_ID NUMBER(15), ACTION_TYPE CHK IN ('INSERT','UPDATE','DELETE'), OLD_VALUES CLOB, NEW_VALUES CLOB, CHANGED_BY NOT NULL, CHANGED_DATE DEFAULT SYSDATE, IP_ADDRESS VARCHAR2(50), SESSION_ID VARCHAR2(100) | AUDIT_ID | CHK_AUDIT_ACTION |
| SYSTEM_PARAMETERS | PARAM_ID, PARAM_GROUP VARCHAR2(50), PARAM_CODE VARCHAR2(50), PARAM_VALUE VARCHAR2(4000) NOT NULL, PARAM_DESCRIPTION, DATA_TYPE DEFAULT 'VARCHAR2', EDITABLE_FLAG DEFAULT 'Y', audit cols | PARAM_ID | UK_PARAM_CODE (PARAM_GROUP, PARAM_CODE) |
| NOTIFICATION_QUEUE | NOTIFICATION_ID NUMBER(15), RECIPIENT_EMP_ID, RECIPIENT_EMAIL, NOTIFICATION_TYPE CHK IN ('EMAIL','IN_APP','SMS'), SUBJECT NOT NULL, BODY CLOB NOT NULL, STATUS DEFAULT 'PENDING' CHK IN ('PENDING','SENT','FAILED','CANCELLED'), PRIORITY DEFAULT 5, SENT_DATE, ERROR_MESSAGE VARCHAR2(4000), RETRY_COUNT DEFAULT 0, REFERENCE_TABLE, REFERENCE_ID, CREATED_BY, CREATED_DATE | NOTIFICATION_ID | CHK_NOTIF_STATUS; CHK_NOTIF_TYPE |
| USER_SESSIONS | SESSION_ID NUMBER(15), EMP_ID (FK), USERNAME NOT NULL, LOGIN_TIME NOT NULL, LOGOUT_TIME, IP_ADDRESS, FORMS_MODULE, SESSION_STATUS DEFAULT 'ACTIVE', CREATED_DATE | SESSION_ID | FK_US_EMP |
| LOOKUP_VALUES | LOOKUP_ID, LOOKUP_TYPE VARCHAR2(50), LOOKUP_CODE VARCHAR2(50), LOOKUP_VALUE VARCHAR2(200), DISPLAY_ORDER DEFAULT 0, PARENT_LOOKUP_ID nullable, ACTIVE_FLAG, CREATED_BY, CREATED_DATE | LOOKUP_ID | UK_LOOKUP (LOOKUP_TYPE, LOOKUP_CODE) |

**Total tables: 35 (confirmed from DDL). README states 42 — 7 tables referenced in packages but not in provided DDL files:**
- EMPLOYEE_PAY_ELEMENTS (referenced in PKG_EMPLOYEE.terminate_employee, PKG_PAYROLL)
- LOW: inferred from package body references — DDL file not provided for this table
- Additional missing tables inferred from package bodies: RPT_* denormalized reporting tables (referenced in PKG_REPORTING.refresh_reporting_tables — not present in DDL)

**Sequences — Complete List (29 total, all from hrms_sequences.sql):**

| Sequence | Start | Increment | Cache | Used By |
|---|---|---|---|---|
| SEQ_DEPARTMENT | 100 | 1 | NOCACHE | DEPARTMENTS.DEPT_ID |
| SEQ_LOCATION | 100 | 1 | NOCACHE | LOCATIONS |
| SEQ_JOB_GRADE | 100 | 1 | NOCACHE | JOB_GRADES.GRADE_ID |
| SEQ_JOB_TITLE | 100 | 1 | NOCACHE | JOB_TITLES.JOB_ID |
| SEQ_EMPLOYEE | 10000 | 1 | NOCACHE | EMPLOYEES.EMP_ID |
| SEQ_EMP_HISTORY | 1 | 1 | NOCACHE | EMPLOYEE_HISTORY.HIST_ID |
| SEQ_DEPENDENT | 1 | 1 | NOCACHE | EMPLOYEE_DEPENDENTS.DEPENDENT_ID |
| SEQ_EMERGENCY_CONTACT | 1 | 1 | NOCACHE | EMERGENCY_CONTACTS.CONTACT_ID |
| SEQ_EMP_NUMBER | 1000 | 1 | NOCACHE | Employee number generation (race condition bug — PKG_EMPLOYEE uses MAX()+1 instead) |
| SEQ_SALARY | 1 | 1 | NOCACHE | SALARY_RECORDS.SALARY_ID |
| SEQ_PAY_ELEMENT | 1 | 1 | NOCACHE | PAY_ELEMENTS.ELEMENT_ID |
| SEQ_EMP_PAY_ELEMENT | 1 | 1 | NOCACHE | EMPLOYEE_PAY_ELEMENTS |
| SEQ_PAY_PERIOD | 1 | 1 | NOCACHE | PAY_PERIODS.PERIOD_ID |
| SEQ_PAYROLL_RUN | 1 | 1 | NOCACHE | PAYROLL_RUNS.RUN_ID |
| SEQ_PAYROLL_DETAIL | 1 | 1 | NOCACHE | PAYROLL_DETAILS.DETAIL_ID |
| SEQ_TAX_BRACKET | 1 | 1 | NOCACHE | TAX_BRACKETS.BRACKET_ID |
| SEQ_LEAVE_TYPE | 1 | 1 | NOCACHE | LEAVE_TYPES.LEAVE_TYPE_ID |
| SEQ_LEAVE_BALANCE | 1 | 1 | NOCACHE | LEAVE_BALANCES.BALANCE_ID |
| SEQ_LEAVE_REQUEST | 1 | 1 | NOCACHE | LEAVE_REQUESTS.REQUEST_ID |
| SEQ_LEAVE_ACCRUAL | 1 | 1 | NOCACHE | LEAVE_ACCRUAL_LOG.ACCRUAL_ID |
| SEQ_HOLIDAY | 1 | 1 | NOCACHE | HOLIDAYS.HOLIDAY_ID |
| SEQ_REVIEW_CYCLE | 1 | 1 | NOCACHE | REVIEW_CYCLES.CYCLE_ID |
| SEQ_PERF_REVIEW | 1 | 1 | NOCACHE | PERFORMANCE_REVIEWS.REVIEW_ID |
| SEQ_PERF_GOAL | 1 | 1 | NOCACHE | PERFORMANCE_GOALS.GOAL_ID |
| SEQ_AUDIT | 1 | 1 | CACHE 100 | AUDIT_LOG.AUDIT_ID (only cached sequence) |
| SEQ_NOTIFICATION | 1 | 1 | NOCACHE | NOTIFICATION_QUEUE.NOTIFICATION_ID |
| SEQ_USER_SESSION | 1 | 1 | NOCACHE | USER_SESSIONS.SESSION_ID |
| SEQ_SYSTEM_PARAM | 1 | 1 | NOCACHE | SYSTEM_PARAMETERS.PARAM_ID |
| SEQ_LOOKUP | 1 | 1 | NOCACHE | LOOKUP_VALUES.LOOKUP_ID |

**Views — Complete List (6 provided from hrms_views.sql; README states 15):**

| View | Definition Summary | Notable Formula |
|---|---|---|
| VW_ACTIVE_EMPLOYEES | Denormalized active employee + dept + job + grade + manager + location + current salary | TENURE_YEARS = TRUNC(MONTHS_BETWEEN(SYSDATE, HIRE_DATE)/12, 1); current salary = SALARY_RECORDS where ACTIVE_FLAG='Y' AND EFFECTIVE_DATE<=SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE) |
| VW_ORG_HIERARCHY | Hierarchical CONNECT BY traversal of active employees | START WITH MANAGER_EMP_ID IS NULL; SYS_CONNECT_BY_PATH; performance warning >500 employees |
| VW_EMPLOYEE_COMPENSATION | Active employees + salary + grade min/max + compa-ratio | COMPA_RATIO = ROUND(BASE_SALARY / ((MIN_SALARY + MAX_SALARY)/2) * 100, 1) |
| VW_LEAVE_SUMMARY | Current year leave balances per active employee | AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT (NOTE: does NOT subtract PENDING — differs from virtual column formula — DISC-003) |
| VW_PAYROLL_LATEST | Latest approved run gross/tax/deductions/net per employee | Latest = MAX(RUN_ID) WHERE STATUS='APPROVED' |
| VW_PENDING_APPROVALS | UNION ALL of pending leave requests + manager_review performance reviews | APPROVAL_TYPE IN ('LEAVE','PERFORMANCE') |

**DISC-003: VW_LEAVE_SUMMARY AVAILABLE formula omits PENDING deduction; LEAVE_BALANCES virtual column includes it. Both in same schema. Agent 2 to determine which is authoritative for reporting.**

**Database Triggers (from provided files):**

| Trigger | Table | Timing | Events | Key Business Rules |
|---|---|---|---|---|
| TRG_SALARY_AUDIT | SALARY_RECORDS | AFTER | INSERT, UPDATE, DELETE | Calls PKG_AUDIT.log_action with JSON old/new values |
| TRG_LEAVE_REQUEST_AUDIT | LEAVE_REQUESTS | AFTER | UPDATE OF STATUS | Calls PKG_AUDIT.log_action on every status change |
| TRG_DEPARTMENT_AUDIT | DEPARTMENTS | AFTER | INSERT, UPDATE, DELETE | Calls PKG_AUDIT.log_action (no old/new JSON values) |
| TRG_EMP_BEFORE_INSERT | EMPLOYEES | BEFORE | INSERT | Defaults CREATED_BY, CREATED_DATE, ACTIVE_FLAG='Y', EMPLOYMENT_STATUS='ACTIVE'; hire date > SYSDATE+180 blocked (-20501); email uniqueness check among active employees (-20502) |
| TRG_EMP_BEFORE_UPDATE | EMPLOYEES | BEFORE | UPDATE | Auto-stamps MODIFIED_BY/MODIFIED_DATE; blocks TERMINATED→ACTIVE direct reactivation (-20503); writes EMPLOYEE_HISTORY for STATUS_CHANGE, DEPARTMENT_CHANGE, JOB_CHANGE |
| TRG_EMP_INSTEAD_OF_DELETE | EMPLOYEES | BEFORE | DELETE | Blocks all physical deletes (-20504); soft delete only via ACTIVE_FLAG='N' |

**README states 200+ triggers — only 6 provided in source files. The remaining 194+ triggers are not in the provided source set.**

**Seed Data — Business Reference Values:**
- 3 locations (HQ/New York, Chicago, San Francisco)
- 10 job grades (Entry Level $35k-$55k through C-Suite $300k-$600k)
- 10 departments (EXEC, HR, FIN, IT, ITDEV, ITOPS, SALES, MKT, OPS, LEGAL)
- 26 job titles (INTERN through CEO)
- 6 leave types (PTO 1.25 days/month; SICK 0.833/month; COMP 90-day tenure gate; FMLA 365-day tenure gate; JURY no approval; BEREAVE no approval)
- 11 pay elements (BASE_PAY; 4 TAX elements; 401k 6% pretax; Medical $250 pretax; Dental $45 pretax; Vision $15 pretax; Life $25 not pretax; HSA $150 pretax)
- 10 holidays (2024 US federal calendar, all locations)
- 10 system parameters (APP_VERSION=4.2.0; COMPANY_NAME=Acme Corporation; DEFAULT_PAY_FREQUENCY=MONTHLY; FISCAL_YEAR_START=10; SESSION_TIMEOUT_MIN=30; PASSWORD_MIN_LENGTH=8; SMTP_HOST=smtp.internal.company.com; FROM_ADDRESS=hrms-noreply@company.com; GL_FEED_STATUS=ACTIVE; BENEFITS_FEED_STATUS=ACTIVE)
- 25 employees (24 active, 1 terminated)
- 23 salary records (all MONTHLY, ANNUAL basis)

---

### Chunk Inventory — Data Layer
- Technology components: Oracle Database 19c DDL (tables, sequences, views, triggers), Oracle virtual columns, CONNECT BY hierarchical queries
- Data stores: 35 tables confirmed in DDL (42 per README — 7 missing from source set)
- Integrations: None new
- Infrastructure: Oracle directory objects PAYROLL_OUTPUT, GL_FEED_OUT, BENEFITS_FEED_OUT, TIME_ATTENDANCE_IN (filesystem paths managed by DBA; no IaC)
- Environments: None declared
- VERSION CONFLICTS: DISC-003 (VW_LEAVE_SUMMARY vs LEAVE_BALANCES virtual column AVAILABLE formula)
- LOW CONFIDENCE: 7 missing DDL tables (EMPLOYEE_PAY_ELEMENTS confirmed used but DDL not in source set); 9 missing views (15 declared in README, 6 provided); 194+ missing triggers

---

## Agent 1 - Chunk 3 of 6 - Infrastructure Layer

**Carried Forward:**
- Technology components: Oracle DB 19c, Forms 12c, WebLogic 12c, UTL_FILE, UTL_SMTP, DBMS_CRYPTO, DBMS_SCHEDULER
- Data stores: Oracle DB 19c HRMS (35 DDL tables, 29 sequences, 6 views, 5 triggers provided)
- Integrations: SMTP smtp.internal.company.com:25, UTL_FILE×4 Oracle directory objects
- LOW CONFIDENCE items: 10+

---

**Infrastructure artifacts found:** None — no Dockerfile, no docker-compose, no Kubernetes manifests, no Terraform, no CloudFormation, no Pulumi files in provided source.

**ARCHITECTURE NOTE: No infrastructure-as-code found.** Deployment configuration is managed externally (Oracle Forms Application Server, Oracle WebLogic, Oracle Database 19c installation are all assumed to be configured by DBA/sysadmin tooling outside this repository).

**Inferred infrastructure from source code references only:**

| Component | Type | Evidence | Confidence |
|---|---|---|---|
| Oracle Database 19c server | On-premises RDBMS | README + all DDL | HIGH — explicitly declared |
| Oracle Forms 12c Application Server | On-premises Forms AS | README + .fmb/.fmx artifacts | HIGH — explicitly declared |
| Oracle WebLogic 12c | J2EE App Server | README | HIGH — explicitly declared |
| Oracle Reports (.rdf/.rep) — 8 reports | Reporting engine | README (8 reports declared; no .rdf files in source) | LOW — named in README, source not provided |
| Oracle Directory: PAYROLL_OUTPUT | OS filesystem path | UTL_FILE.FOPEN calls in PKG_PAYROLL, PKG_INTEGRATION | HIGH — confirmed in two packages; DBA manages OS path mapping |
| Oracle Directory: GL_FEED_OUT | OS filesystem path | UTL_FILE.FOPEN in PKG_INTEGRATION.generate_gl_journal | HIGH |
| Oracle Directory: BENEFITS_FEED_OUT | OS filesystem path | UTL_FILE.FOPEN in PKG_INTEGRATION.export_benefits_feed | HIGH |
| Oracle Directory: TIME_ATTENDANCE_IN | OS filesystem path | UTL_FILE.FOPEN in PKG_INTEGRATION.import_time_attendance | HIGH |
| SMTP server smtp.internal.company.com | Internal mail relay | PKG_NOTIFICATION + SYSTEM_PARAMETERS.SMTP_HOST | HIGH |
| DBMS_SCHEDULER job — process_queue | Scheduled job | PKG_NOTIFICATION.process_queue "called every 5 minutes" comment | LOW — referenced in comments, no scheduler DDL provided |
| DBMS_SCHEDULER job — run_monthly_accrual | Scheduled job | PKG_LEAVE.run_monthly_accrual "scheduled on 1st of each month" comment | LOW — referenced in comments, no scheduler DDL provided |
| Oracle Financials GL import process | External batch consumer | PKG_INTEGRATION.generate_gl_journal produces pipe-delimited .dat files | HIGH — file format fully specified; consumer is Oracle Financials batch import |
| ADP Benefits system | External vendor | PKG_INTEGRATION.export_benefits_feed produces fixed-width ADP-format file | HIGH — vendor explicitly named in package body |
| Time & Attendance system | External inbound feed | PKG_INTEGRATION.import_time_attendance reads CSV from TIME_ATTENDANCE_IN | HIGH — partially implemented (CSV parsing TODO) |
| Self-service portal | Web application | Referenced in PKG_LEAVE header "Called by: self-service portal" | LOW — no source, no configuration in this repository |

**Deployment topology (inferred from all sources):**

```
[Client Browser / Forms Runtime] → [Oracle Forms AS 12c + WebLogic 12c] → [Oracle DB 19c (HRMS schema)]
                                                                                    ↓
                                                              [OS Filesystem — Oracle Directory Objects]
                                                                    PAYROLL_OUTPUT/GL_FEED_OUT → [Oracle Financials]
                                                                    BENEFITS_FEED_OUT → [ADP]
                                                                    TIME_ATTENDANCE_IN ← [Time & Attendance system]
                                                                    ↓
                                                              [SMTP — smtp.internal.company.com:25]
                                                                    → Email recipients
```

---

### Chunk Inventory — Infrastructure Layer
- Technology components found: Oracle Forms AS 12c, Oracle WebLogic 12c, Oracle DB 19c, DBMS_SCHEDULER (implied), Oracle Directory objects ×4, SMTP server
- Data stores: No new
- Integrations: Oracle Financials (GL batch import, pipe-delimited .dat); ADP (benefits, fixed-width 203-char records); Time & Attendance system (inbound CSV, partially implemented)
- Infrastructure resources: 4 Oracle directory objects; 2 implied DBMS_SCHEDULER jobs (no DDL)
- Environments: None declared in any file
- CI/CD tool invocations: None — no CI/CD layer found
- LOW CONFIDENCE: Self-service portal (referenced but not in repo); Oracle Reports 8×.rdf (named in README, no source); DBMS_SCHEDULER jobs (comments only, no DDL); 194+ DB triggers (6 provided)

---

## Agent 1 - Chunk 4 of 6 - CI/CD Layer

**LAYER NOT FOUND — no CI/CD artifacts detected in this repository.**

No `.github/`, no `Jenkinsfile`, no `.gitlab-ci.yml`, no `azure-pipelines.yml`, no `.circleci/`, no `bitbucket-pipelines.yml`, no pipeline shell scripts.

**CI/CD tool invocations found:** None.
**Reusable workflows followed:** None.
**Environments declared in CI/CD:** None.

All deployment and batch scheduling is handled via Oracle database mechanisms (DBMS_SCHEDULER) or external administrative processes, neither of which have source representation in this repository.

---

## Agent 1 - Chunk 5 of 6 - Security Layer

**Carried Forward:** all prior components, data stores, integrations as listed above.

---

**Authentication mechanism:** Custom Oracle Forms session — PKG_SECURITY.authenticate creates session in USER_SESSIONS table. Login matched by UPPER(EMAIL) against EMPLOYEES table.

**Password storage:** MD5 hash via DBMS_CRYPTO.HASH_MD5 (documented as weak; bcrypt/scrypt recommended).

**Encryption:** AES-256 CBC PKCS5 via DBMS_CRYPTO.ENCRYPT — used for SSN_ENCRYPTED on EMPLOYEES and EMPLOYEE_DEPENDENTS, and ACCOUNT_NUMBER_ENC on EMPLOYEE_BANK_ACCOUNTS.

**Hard-coded encryption key:** `HR$ystem_3ncrypt10n_K3y_2024!!` in PKG_SECURITY package body — HIGH severity vulnerability.

**Session management:** USER_SESSIONS table; 30-minute timeout from LOGIN_TIME (not last activity — no session refresh). Timeout evaluated on each is_session_valid call.

**Authorization:** Grade-based model in PKG_SECURITY.has_permission:
- Grade >= 8: full access all modules/actions
- Grade >= 5 and < 8: VIEW on all modules
- Any grade: CREATE+VIEW on LEAVE; VIEW on EMPLOYEE
- All others: denied

**Permission checks by module observed in Forms:**

| Module | Permission Required | Where Checked |
|---|---|---|
| PAYROLL | VIEW (form open), APPROVE | HRMS_PAYROLL WHEN-NEW-FORM-INSTANCE; BTN_APPROVE |
| EMPLOYEE | EDIT | HRMS_EMPLOYEE WHEN-NEW-FORM-INSTANCE |
| REPORTS | VIEW | HRMS_MENU BTN_REPORTS, MI_REPORTS |
| ADMIN | VIEW | HRMS_MENU WHEN-NEW-FORM-INSTANCE, MI_ADMIN |
| LEAVE | None (all users) | No permission check on HRMS_LEAVE open |
| PERFORMANCE | None (all users) | No permission check on HRMS_PERFORMANCE open |

**Password complexity rules (PKG_SECURITY.change_password):**
- Minimum length: 8 characters
- Must contain at least one uppercase letter [A-Z]
- Must contain at least one digit [0-9]
- No special character requirement
- Old password accepted as parameter but not verified (stub — USER_CREDENTIALS update not implemented)

**Known security vulnerabilities (explicitly documented in source):**
1. Password field transmitted in cleartext in HRMS_LOGIN form (Oracle Forms applet limitation)
2. No account lockout after N failed authentication attempts
3. No CAPTCHA or 2FA support
4. MD5 password hashing (cryptographically weak)
5. AES-256 encryption key hard-coded in PKG_SECURITY package body source
6. SQL injection vulnerability in PKG_EMPLOYEE.search_employees (p_last_name and p_first_name concatenated into dynamic SQL without bind variables)
7. FTP credentials for integration stored in SYSTEM_PARAMETERS table (plaintext per PKG_INTEGRATION header comment)
8. ROWNUM=1 on login silently selects first match among duplicate emails
9. Session timeout based on LOGIN_TIME not last activity (no session refresh mechanism)
10. Timing attack: NO_DATA_FOUND (unknown user) returns faster than valid-user path

**Audit trail:** PKG_AUDIT.log_action — PRAGMA AUTONOMOUS_TRANSACTION throughout; captures IP_ADDRESS via SYS_CONTEXT('USERENV','IP_ADDRESS'); captures SESSION_ID; default retention 365 days (purge_old_records); failures silently suppressed. Error logs written to AUDIT_LOG with TABLE_NAME='ERROR_LOG'; info logs to TABLE_NAME='INFO_LOG'.

**Database-level security:** SSN_ENCRYPTED VARCHAR2(200) on EMPLOYEES (AES-256); ACCOUNT_NUMBER_ENC VARCHAR2(200) on EMPLOYEE_BANK_ACCOUNTS (encrypted); SSN_ENCRYPTED on EMPLOYEE_DEPENDENTS.

---

### Chunk Inventory — Security Layer
- Authentication: Custom Oracle Forms session via PKG_SECURITY + USER_SESSIONS table
- Encryption: DBMS_CRYPTO (AES-256 CBC for SSN/bank account; MD5 for passwords)
- Secrets management: Hard-coded AES key in package body; FTP credentials in SYSTEM_PARAMETERS (plaintext)
- Network security declarations: None (no TLS config, no firewall rules, no CORS config found — on-premises Oracle Forms, no web API layer)
- Compliance flags: SSN encrypted at rest (EMPLOYEES, EMPLOYEE_DEPENDENTS); bank account number encrypted; ACTIVE_FLAG soft-delete pattern; AUDIT_LOG with IP capture; EEO_CATEGORY on JOB_TITLES; GENDER, DATE_OF_BIRTH, MARITAL_STATUS, NATIONALITY stored on EMPLOYEES (PII)
- LOW CONFIDENCE: No RBAC junction table (has_permission uses grade thresholds only); USER_CREDENTIALS table referenced but DDL not provided; LDAP/AD sync in PKG_INTEGRATION.sync_org_structure is a stub

---

## Agent 1 - Chunk 6 of 6 - Observability Layer

**AUDIT_LOG table:** Single table captures all DML audit events. Populated via:
- PKG_AUDIT.log_action (PRAGMA AUTONOMOUS_TRANSACTION) — called by all 11 packages
- TRG_SALARY_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_DEPARTMENT_AUDIT (3 of 200+ triggers)
- TABLE_NAME='ERROR_LOG' and TABLE_NAME='INFO_LOG' used as synthetic "tables" for PKG_COMMON log_error/log_info

**Logging approach:** DBMS_OUTPUT for fallback/debug (PKG_COMMON.log_error, PKG_AUDIT.purge_old_records, PKG_INTEGRATION, PKG_PERFORMANCE). No structured logging framework; no log aggregation tool.

**Monitoring:** No Prometheus, Grafana, Datadog, New Relic, or any observability tooling configuration found. No health check endpoints (Oracle Forms is a thick client — no HTTP health endpoints).

**Alerting:** None declared in source. SMTP-based notifications via NOTIFICATION_QUEUE are business notifications, not operational alerts.

**Performance instrumentation:** None. Known performance issue documented in source: VW_ORG_HIERARCHY and PKG_EMPLOYEE.get_org_chart degrade significantly with >500 employees.

**ARCHITECTURE NOTE: No observability-as-code found.** Operational monitoring assumed to be Oracle Enterprise Manager (OEM) or equivalent DBA tooling external to this repository.

---

### Chunk Inventory — Observability Layer
- Technology: AUDIT_LOG table (operational + security + error audit in one table), DBMS_OUTPUT (debug fallback), NOTIFICATION_QUEUE (async SMTP delivery — business notifications, not ops alerts)
- No external monitoring/APM tools detected
- No distributed tracing
- No health check endpoints (thick client architecture — N/A)
- LOW CONFIDENCE: Oracle Enterprise Manager assumed but not confirmed from source

---

## Agent 1 - Project Scan Summary

- **Language(s):** PL/SQL (Oracle 19c), Oracle Forms procedural language (PLL)
- **Framework(s):** Oracle Forms 12c (12.2.1.4), Oracle WebLogic 12c
- **Architecture style:** Monolith — HIGH. Single HRMS schema; no service boundaries; all business logic in Oracle DB packages and Forms triggers.
- **Deployment target:** On-premises Oracle infrastructure (Oracle Forms AS 12c + WebLogic 12c + Oracle DB 19c). No cloud, no containers.
- **Total files scanned:** 33 (all provided in source set)
- **Technology layers found:** 4 — Application, Data, Security, Observability/Audit. CI/CD layer: ABSENT. Infrastructure-as-code layer: ABSENT. Containerization layer: ABSENT.
- **Chunks processed:** 6
- **External integrations found:** 4 — Oracle Financials GL (outbound flat file), ADP Benefits (outbound fixed-width), Time & Attendance (inbound CSV, partially implemented), SMTP (internal relay smtp.internal.company.com:25)
- **Data stores identified:** 1 — Oracle Database 19c, HRMS schema
- **Services / components found:** 1 deployable application (Oracle Forms + WebLogic), 1 Oracle DB instance, 4 Oracle directory objects (filesystem), 1 SMTP relay
- **CI/CD pipeline files read:** 0
- **CI/CD tool invocations found:** None

---

## OUTPUT 1 — Technology Stack Inventory

| Component Name | Version | Category | Layer | Package Manager / Source | Source File | Confidence |
|---|---|---|---|---|---|---|
| Oracle Database | 19c | RDBMS | Data | Oracle installer | README.md | HIGH |
| Oracle Forms | 12c (12.2.1.4) | UI Framework / Application Runtime | Application | Oracle installer | README.md, forms/xml-exports/*.xml | HIGH |
| Oracle WebLogic | 12c | Application Server | Infrastructure | Oracle installer | README.md | HIGH |
| PL/SQL | Oracle 19c dialect | Server-side Language | Application | Oracle DB built-in | plsql/packages/*.pkb | HIGH |
| DBMS_CRYPTO | Oracle 19c built-in | Cryptography Library | Security | Oracle DB built-in | plsql/packages/PKG_SECURITY.pkb | HIGH |
| DBMS_OUTPUT | Oracle 19c built-in | Debug / Fallback Logging | Observability | Oracle DB built-in | multiple .pkb files | HIGH |
| DBMS_SCHEDULER | Oracle 19c built-in | Job Scheduler | Infrastructure | Oracle DB built-in | Comments in PKG_NOTIFICATION, PKG_LEAVE | LOW — referenced in comments; no scheduler DDL provided |
| UTL_FILE | Oracle 19c built-in | File I/O Library | Integration | Oracle DB built-in | PKG_PAYROLL.pkb, PKG_INTEGRATION.pkb | HIGH |
| UTL_SMTP | Oracle 19c built-in | SMTP Client Library | Integration | Oracle DB built-in | PKG_NOTIFICATION.pkb | HIGH |
| UTL_RAW | Oracle 19c built-in | Raw Data Utility | Security | Oracle DB built-in | PKG_SECURITY.pkb | HIGH |
| SYS_CONTEXT | Oracle 19c built-in | Session Context Function | Security | Oracle DB built-in | PKG_AUDIT.pkb | HIGH |
| HRMS_COMMON_LIB | (project, no version) | Oracle Forms PLL Library | Application | Oracle Forms compiler | forms/libraries/HRMS_COMMON_LIB.pll.sql | HIGH |
| HRMS_VALIDATION_LIB | (project, no version) | Oracle Forms PLL Library | Application | Oracle Forms compiler | forms/libraries/HRMS_VALIDATION_LIB.pll.sql | HIGH |

---

## OUTPUT 2 — Component & Service Map

| Service / Component Name | Type | Exposed Port(s) | Communication Protocol(s) | Primary Technology | Source File | Notes |
|---|---|---|---|---|---|---|
| HRMS Oracle Forms Application | Frontend App / Thick Client | N/A (Oracle Forms applet) | Oracle Net / JDBC to DB; HTTP/HTTPS to Forms AS | Oracle Forms 12c + WebLogic 12c | README.md | Entry point for all 200 concurrent users across 3 offices |
| HRMS Database Schema | Database | Oracle default (1521 typical) | Oracle Net (SQL*Net) | Oracle Database 19c | schema/tables/*.sql | Single HRMS schema; all 35+ tables reside here |
| SMTP Mail Relay | Email Service | 25 | SMTP | Internal company SMTP server | PKG_NOTIFICATION.pkb | smtp.internal.company.com; no TLS declared |
| GL_FEED_OUT (Oracle Directory) | File Integration Endpoint | N/A | Flat file (pipe-delimited .dat) | UTL_FILE / Oracle Financials batch import | PKG_INTEGRATION.pkb | Outbound; format: H/D/T records; consumer: Oracle Financials |
| BENEFITS_FEED_OUT (Oracle Directory) | File Integration Endpoint | N/A | Flat file (fixed-width, 203 chars) | UTL_FILE / ADP | PKG_INTEGRATION.pkb | Outbound weekly; ADP vendor format |
| TIME_ATTENDANCE_IN (Oracle Directory) | File Integration Endpoint | N/A | Flat file (CSV) | UTL_FILE | PKG_INTEGRATION.pkb | Inbound; CSV parsing not implemented (TODO) |
| PAYROLL_OUTPUT (Oracle Directory) | File Output Endpoint | N/A | CSV | UTL_FILE | PKG_PAYROLL.pkb | Pay register CSV output |
| Self-Service Portal | Web Application | UNKNOWN | UNKNOWN | UNKNOWN | PKG_LEAVE.pks (header comment) | LOW — referenced but no source in this repository |

---

## OUTPUT 3 — Data Store Registry

| Store Name | Category | Engine / Technology | Version | Declared Database / Collection Name | Connected Services | Source File | Confidence |
|---|---|---|---|---|---|---|---|
| HRMS Oracle Database | Relational Database | Oracle Database | 19c | HRMS (schema) | All Oracle Forms modules; all PL/SQL packages; Oracle Reports; integration batch jobs | README.md, schema/tables/*.sql | HIGH |

---

## OUTPUT 4 — Infrastructure & Deployment Blueprint

### Compute & Container Resources

| Resource Name | Resource Type | Platform / Provider | Image / Runtime Version | Environments Declared | Key Configuration (non-secret) | Source File | Confidence |
|---|---|---|---|---|---|---|---|
| Oracle Forms Application Server | Application Server | Oracle Forms AS 12c | Oracle Forms 12c (12.2.1.4) | UNKNOWN | Hosts .fmx compiled form binaries; WebLogic 12c underlying; ~200 concurrent users | README.md | HIGH |
| Oracle WebLogic Server | J2EE Application Server | Oracle WebLogic | 12c | UNKNOWN | Underpins Forms AS deployment | README.md | HIGH |
| Oracle Database Server | RDBMS | Oracle Database | 19c | UNKNOWN | HRMS schema; 35+ tables; 29 sequences; 6+ views; 200+ triggers; 29 sequences all NOCACHE except SEQ_AUDIT CACHE 100 | README.md, schema/ | HIGH |
| Oracle Directory: PAYROLL_OUTPUT | OS Filesystem Mount | Oracle Directory Object | N/A | UNKNOWN | Max file line: 32767 bytes; CSV format | PKG_PAYROLL.pkb | HIGH — object name declared; OS path managed by DBA |
| Oracle Directory: GL_FEED_OUT | OS Filesystem Mount | Oracle Directory Object | N/A | UNKNOWN | Max file line: 32767 bytes; pipe-delimited .dat format | PKG_INTEGRATION.pkb | HIGH |
| Oracle Directory: BENEFITS_FEED_OUT | OS Filesystem Mount | Oracle Directory Object | N/A | UNKNOWN | Max file line: 32767 bytes; fixed-width 203-char records | PKG_INTEGRATION.pkb | HIGH |
| Oracle Directory: TIME_ATTENDANCE_IN | OS Filesystem Mount | Oracle Directory Object | N/A | UNKNOWN | Max file line: 32767 bytes; CSV; comment lines prefixed '#' | PKG_INTEGRATION.pkb | HIGH |
| DBMS_SCHEDULER Job: process_queue | Scheduled Database Job | Oracle DBMS_SCHEDULER | 19c | UNKNOWN | Frequency: every 5 minutes; batch size: 50 notifications per run | PKG_NOTIFICATION.pkb (comment) | LOW — no scheduler DDL provided |
| DBMS_SCHEDULER Job: run_monthly_accrual | Scheduled Database Job | Oracle DBMS_SCHEDULER | 19c | UNKNOWN | Frequency: 1st of each month; commit batch: every 100 employees | PKG_LEAVE.pkb (comment) | LOW — no scheduler DDL provided |

### Environments Identified

| Environment Name | Trigger / Target | Source File |
|---|---|---|
| (None declared) | No environment declarations found in any source file | N/A |

### CI/CD Pipeline Inventory

| Pipeline File | Job / Stage Name | Tool Invocations | Actions Used | Runs On Condition | Source |
|---|---|---|---|---|---|
| (None found) | LAYER NOT FOUND — no CI/CD pipeline files in repository | — | — | — | — |

### Network Topology (declared configuration only)

- No load balancer declarations found
- No service mesh or internal DNS declarations found
- No VPC/subnet/security group declarations found (on-premises deployment)
- No TLS termination point declared; SMTP connection to port 25 (no TLS/STARTTLS declared in PKG_NOTIFICATION)
- Oracle Forms applet communicates to WebLogic/Forms AS via HTTP (port not declared in source)
- Oracle DB listener port not declared in source (Oracle default 1521 inferred but not confirmed)

---

## OUTPUT 5 — Integration & Dependency Graph

### External Integrations

| Integration Name | Category | Protocol / Interface | Direction | Config Key / Env Var | Source File | Confidence |
|---|---|---|---|---|---|---|
| Oracle Financials GL | ERP / General Ledger | Flat file (pipe-delimited .dat, UTL_FILE) | Outbound | INTEGRATION.GL_FEED_STATUS in SYSTEM_PARAMETERS | PKG_INTEGRATION.pkb | HIGH |
| ADP Benefits System | HR / Benefits Provider | Flat file (fixed-width 203-char, UTL_FILE) | Outbound | INTEGRATION.BENEFITS_FEED_STATUS in SYSTEM_PARAMETERS | PKG_INTEGRATION.pkb | HIGH |
| Time & Attendance System | Workforce Management | Flat file (CSV, UTL_FILE) | Inbound | N/A | PKG_INTEGRATION.pkb | HIGH — file format declared; parsing logic TODO |
| SMTP Internal Mail Relay | Email Provider | SMTP (UTL_SMTP, port 25) | Outbound | NOTIFICATION.SMTP_HOST=smtp.internal.company.com; NOTIFICATION.FROM_ADDRESS=hrms-noreply@company.com | PKG_NOTIFICATION.pkb, 01_reference_data.sql | HIGH |
| Self-Service Portal | Web Application (assumed intranet) | UNKNOWN | Inbound (calls PKG_LEAVE) | N/A | PKG_LEAVE.pks header | LOW — no source or config in this repository |
| LDAP / Active Directory | Identity Directory | UNKNOWN (sync_org_structure stub) | Inbound (intended) | N/A | PKG_INTEGRATION.pkb | LOW — stub only; not implemented |

### Internal Service Dependencies

| Caller | Target | Protocol | Dependency Type | Notes |
|---|---|---|---|---|
| PKG_EMPLOYEE | PKG_PAYROLL (create_salary_record) | In-process PL/SQL | Synchronous | Called during create_employee, promote_employee, rehire_employee |
| PKG_EMPLOYEE | PKG_AUDIT (log_action) | In-process PL/SQL | Synchronous | All employee mutations |
| PKG_EMPLOYEE | PKG_NOTIFICATION (send_notification) | In-process PL/SQL | Asynchronous (queued) | New hire, termination notifications |
| PKG_EMPLOYEE | PKG_COMMON (log_error) | In-process PL/SQL | Synchronous | Error handling |
| PKG_PAYROLL | PKG_EMPLOYEE (is_active) | In-process PL/SQL | Synchronous | **CIRCULAR DEPENDENCY** — also PKG_EMPLOYEE calls PKG_PAYROLL |
| PKG_PAYROLL | PKG_AUDIT (log_action) | In-process PL/SQL | Synchronous | All payroll mutations |
| PKG_LEAVE | PKG_EMPLOYEE (implied — employee validation) | In-process PL/SQL | Synchronous | — |
| PKG_LEAVE | PKG_AUDIT (log_action) | In-process PL/SQL | Synchronous | All leave request mutations |
| PKG_LEAVE | PKG_NOTIFICATION (send_notification) | In-process PL/SQL | Asynchronous (queued) | Approval/rejection notifications |
| PKG_PERFORMANCE | PKG_AUDIT (log_action) | In-process PL/SQL | Synchronous | Review cycle mutations |
| PKG_PERFORMANCE | PKG_NOTIFICATION (send_notification) | In-process PL/SQL | Asynchronous (queued) | Review initiation/completion |
| PKG_SECURITY | PKG_EMPLOYEE (set_session_context) | In-process PL/SQL | Synchronous | Called on authenticate |
| PKG_SECURITY | PKG_AUDIT (log_action) | In-process PL/SQL | Synchronous | Session creation, password change |
| PKG_NOTIFICATION | UTL_SMTP | Oracle built-in | Synchronous (per email) | Each email opens its own SMTP connection — no pooling |
| PKG_INTEGRATION | UTL_FILE | Oracle built-in | Synchronous | GL journal, benefits feed, time import |
| All packages | PKG_COMMON (log_error, log_info) | In-process PL/SQL | Synchronous | Base logging utility |
| All packages | PKG_AUDIT (log_action) | In-process PL/SQL | Autonomous Transaction | Base audit trail |
| Forms (HRMS_COMMON_LIB) | PKG_SECURITY (is_session_valid) | PL/SQL call from Forms trigger | Synchronous | Session validation on every form open |

### Build & Developer Toolchain

| Tool | Version | Purpose | Source File |
|---|---|---|---|
| Oracle Forms Builder | 12c (12.2.1.4) | Compile .fmb → .fmx; edit forms, libraries, menus | forms/xml-exports/*.xml (export metadata) |
| Oracle SQL*Plus / SQL Developer | (not declared) | PL/SQL compilation, schema deployment | plsql/packages/*.pkb, schema/ |
| Oracle Reports Builder | (not declared) | Compile .rdf → .rep | README.md (8 reports declared; .rdf not in source) |

---

## OUTPUT 6 — Security & Configuration Snapshot

### Authentication & Authorisation Mechanisms

| Mechanism Name | Type | Provider / Library | Scope | Config Key / Annotation | Source File | Confidence |
|---|---|---|---|---|---|---|
| Oracle Forms Custom Session Auth | Authentication | PKG_SECURITY + USER_SESSIONS table | All forms | SESSION_TIMEOUT_MIN=30 in SYSTEM_PARAMETERS | PKG_SECURITY.pkb, 01_reference_data.sql | HIGH |
| MD5 Password Hash | Authentication | Oracle DBMS_CRYPTO.HASH_MD5 | Application (password storage) | (no config key — algorithm hard-coded) | PKG_SECURITY.pkb | HIGH — documented as weak; bcrypt recommended |
| Grade-based Permission Model | Authorisation | PKG_SECURITY.has_permission (custom, grade thresholds) | All modules | (no config key — thresholds hard-coded: grade>=8 full; grade>=5 VIEW all) | PKG_SECURITY.pkb | HIGH — simplified model; no RBAC table |
| AES-256 CBC PKCS5 SSN Encryption | Data Protection | Oracle DBMS_CRYPTO.ENCRYPT_AES256 | SSN fields (EMPLOYEES, EMPLOYEE_DEPENDENTS); bank account numbers (EMPLOYEE_BANK_ACCOUNTS) | c_encryption_key hard-coded in PKG_SECURITY.pkb | PKG_SECURITY.pkb | HIGH — key management is a CRITICAL vulnerability |

### Secrets & Configuration Management

| Approach | Tool / Service | Scope | Config Key / Reference | Source File | Confidence |
|---|---|---|---|---|---|
| Oracle SYSTEM_PARAMETERS table | Custom DB table (PKG_COMMON.get_param) | Application runtime config | SMTP_HOST, FROM_ADDRESS, GL_FEED_STATUS, BENEFITS_FEED_STATUS, SESSION_TIMEOUT_MIN, PASSWORD_MIN_LENGTH | 01_reference_data.sql, PKG_COMMON.pkb | HIGH |
| Hard-coded constant in package body | None | SSN/bank AES-256 key | c_encryption_key = 'HR$ystem_3ncrypt10n_K3y_2024!!' in PKG_SECURITY.pkb | PKG_SECURITY.pkb | HIGH — CRITICAL SECURITY VULNERABILITY |
| SYSTEM_PARAMETERS table (plaintext) | Custom DB table | FTP credentials for integration | (key names not specified in source beyond header comment) | PKG_INTEGRATION.pks header | HIGH — documented vulnerability |
| SECRETS MANAGEMENT PATTERN DETECTED: SSN stored encrypted at column level; bank account numbers encrypted; no vault or HSM integration found |

### Network Security Declarations

| Declaration | Type | Value (non-secret only) | Source File | Confidence |
|---|---|---|---|---|
| SMTP port 25, no TLS | Network protocol | smtp.internal.company.com:25 — no STARTTLS or TLS declared | PKG_NOTIFICATION.pkb | HIGH |
| Password cleartext transmission | Application Security | Oracle Forms applet transmits password in cleartext (documented limitation) | HRMS_LOGIN.xml | HIGH |
| No CORS policy | (N/A) | Oracle Forms thick client — no web API layer; CORS not applicable | N/A | HIGH |
| Session timeout 30 minutes | Session Security | 30 minutes from LOGIN_TIME (not last activity) | PKG_SECURITY.pkb, SYSTEM_PARAMETERS | HIGH |
| Password min length 8 chars | Password Policy | 8 characters minimum | PKG_SECURITY.change_password, SYSTEM_PARAMETERS | HIGH |
| Password: must contain uppercase + digit | Password Policy | [A-Z] + [0-9] required; no special char; no max length | PKG_SECURITY.change_password | HIGH |

### Compliance & Audit Flags

| Item | Type | Detail | Source File |
|---|---|---|---|
| AUDIT_LOG table — IP capture, all DML | Audit Logging | PKG_AUDIT.log_action records IP via SYS_CONTEXT('USERENV','IP_ADDRESS'); captures SESSION_ID; PRAGMA AUTONOMOUS_TRANSACTION; retention default 365 days | PKG_AUDIT.pkb |
| SSN stored encrypted (EMPLOYEES, EMPLOYEE_DEPENDENTS) | GDPR / PII | AES-256 encrypted; decrypted only via PKG_SECURITY.decrypt_ssn | schema/tables/01_core_tables.sql |
| Bank account numbers encrypted (EMPLOYEE_BANK_ACCOUNTS) | PCI-adjacent | ACCOUNT_NUMBER_ENC encrypted; routing number stored plaintext | schema/tables/02_payroll_tables.sql |
| Gender, Date of Birth, Marital Status, Nationality on EMPLOYEES | GDPR / PII | Stored as plain columns; no encryption or masking | schema/tables/01_core_tables.sql |
| EEO_CATEGORY on JOB_TITLES | EEO Compliance | EEO category codes (1.1, 1.2, 2.0, 5.0) on all job titles; PKG_REPORTING.eeo_compliance_report | schema/tables/01_core_tables.sql |
| Soft-delete pattern (ACTIVE_FLAG='N') | Data Retention / Audit | ACTIVE_FLAG on all major tables; physical deletes blocked by TRG_EMP_INSTEAD_OF_DELETE | trg_employees.sql |
| SSN format_ssn_masked returns '***-**-XXXX' | PII Masking | Only last 4 digits exposed in formatted output | PKG_COMMON.pkb |
| AUDIT_LOG purge at 365 days | Data Retention | PKG_AUDIT.purge_old_records(DEFAULT 365) — configurable | PKG_AUDIT.pkb |

---

## Validation Queue

| ID | Item | Chunk | Reason |
|---|---|---|---|
| DISC-001 | Hire date future limit: 90 days (HRMS_EMPLOYEE WHEN-VALIDATE-ITEM) vs 180 days (TRG_EMP_BEFORE_INSERT) | 1 | Two sources declare different limits for same business rule |
| DISC-002 | EMPLOYEE_HISTORY column layout: DDL has EFFECTIVE_DATE + typed OLD_/NEW_ columns; TRG_EMP_BEFORE_UPDATE inserts into CHANGE_DATE + OLD_VALUE/NEW_VALUE VARCHAR2 flat strings | 2 | Trigger and DDL are inconsistent; one of them would fail at runtime |
| DISC-003 | VW_LEAVE_SUMMARY AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT (omits PENDING); LEAVE_BALANCES virtual column includes -PENDING | 2 | View and table disagree on available balance formula |
| LOW-001 | PKG_DEPARTMENT — declared in README, not provided in source set | 1 | Missing source |
| LOW-002 | HRMS_REPORTS, HRMS_ADMIN, HRMS_DEPARTMENT forms — referenced via OPEN_FORM; source not provided | 1 | Missing source |
| LOW-003 | Oracle Reports 8×.rdf files — declared in README; not in source set | 3 | Missing source |
| LOW-004 | 194+ database triggers — README states 200+; only 6 provided | 2 | Missing source |
| LOW-005 | 9 missing views — README states 15; 6 provided | 2 | Missing source |
| LOW-006 | EMPLOYEE_PAY_ELEMENTS — DDL not provided; confirmed used in PKG_EMPLOYEE.terminate_employee and PKG_PAYROLL.calculate_employee_pay | 2 | Missing DDL |
| LOW-007 | RPT_* denormalized reporting tables — referenced in PKG_REPORTING.refresh_reporting_tables; no DDL provided | 2 | Missing DDL |
| LOW-008 | DBMS_SCHEDULER job DDL — two jobs referenced in comments (process_queue every 5 min; run_monthly_accrual monthly); no scheduler CREATE JOB scripts provided | 3 | Missing DDL |
| LOW-009 | FTP credentials in SYSTEM_PARAMETERS — key names not specified in source; only referenced in PKG_INTEGRATION.pks header comment | 3 | Incomplete source; security risk |
| LOW-010 | Self-service portal — referenced in PKG_LEAVE.pks; no source, URL, or config in this repository | 3 | Missing source |
| LOW-011 | USER_CREDENTIALS table — referenced in PKG_SECURITY.change_password (password update stubbed); no DDL provided | 5 | Missing DDL |
| LOW-012 | SEQ_EMP_NUMBER race condition — sequence defined; PKG_EMPLOYEE.generate_emp_number uses MAX()+1 instead; concurrent inserts can produce duplicate EMP_NUMBER | 2 | Known bug documented in source |
| LOW-013 | Oracle Enterprise Manager or equivalent DBA monitoring — implied by production Oracle deployment; no config in repository | 6 | No observability-as-code found |
| ARCH-001 | ARCHITECTURE NOTE: No CI/CD found — all deployment is manual or via Oracle DBA tooling external to this repository | 4 | No pipeline files present |
| ARCH-002 | ARCHITECTURE NOTE: No IaC found — Oracle Forms AS, WebLogic, DB server configurations are not in this repository | 3 | No Terraform/CloudFormation/etc. |
| ARCH-003 | ARCHITECTURE NOTE: Business logic split between Forms triggers and DB packages with no clear boundary — documented in README as known technical debt | 1 | Architectural anti-pattern |
| ARCH-004 | Circular package dependency: PKG_EMPLOYEE calls PKG_PAYROLL.create_salary_record; PKG_PAYROLL calls PKG_EMPLOYEE.is_active | 1 | Documented in both package headers |
| ARCH-005 | SQL injection vulnerability in PKG_EMPLOYEE.search_employees — p_last_name and p_first_name string-concatenated into dynamic SQL | 5 | Documented in source code comment |
| ARCH-006 | Hard-coded AES-256 encryption key in PKG_SECURITY package body source | 5 | Critical security vulnerability |
| ARCH-007 | YTD_GROSS and YTD_NET are hard-coded 0 in all payslip outputs — documented as placeholder not yet implemented | 1 | Incomplete feature |

---

## Handoff Note to Agent 2

This is a legacy Oracle Forms 12c monolith (circa 2002, currently on Forms 12c + Oracle DB 19c) serving as a full-cycle HR management system for ~200 concurrent users across 3 offices. The entire application runs in a single HRMS Oracle schema: 35 DDL-confirmed tables (42 per README — 7 missing from source set), 29 sequences (all NOCACHE except SEQ_AUDIT), 11 PL/SQL packages fully sourced, 6 of 18 Forms modules sourced, and 6 of 200+ database triggers sourced.

The three most critical issues for Agent 2 to investigate first: (1) **DISC-001/DISC-002** — the hire date limit (90 vs 180 days) and EMPLOYEE_HISTORY column layout divergence between triggers and DDL represent runtime contradictions, not theoretical concerns; (2) **ARCH-006** — the AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` is hard-coded in PKG_SECURITY package body source, meaning any developer with source access can decrypt all SSNs and bank account numbers; (3) **ARCH-005** — confirmed SQL injection in PKG_EMPLOYEE.search_employees affects first/last name parameters. CI/CD, containerization, and IaC layers are entirely absent — all deployment is presumed manual.

**Recommended starting layer for Agent 2:** Security Layer — the combination of hard-coded encryption key, MD5 password hashing, no account lockout, cleartext SMTP, and SQL injection constitute the highest-density risk surface and should be assessed before architectural pattern analysis.

---

*Agent 1 Scan Complete.*
*Agent 2 may now begin deep analysis using the 6 output files above.*
*Recommended starting point: Security Layer — reason: hard-coded AES key, SQL injection, MD5 passwords, no lockout, and cleartext transmission constitute the highest-risk surface in this codebase.*
