# TA Agent 1 — Stack Scout Output
> Target system: "Oracle Forms Legacy HR System" (HRMS) — reference codebase provided via deep-scan file extraction
> Pair with: TA_Agent2_DeepAnalyst_v2.md | Scan version: v2

---

## Agent 1 - Project Scan Summary
- Language(s):                 PL/SQL (Oracle Database 19c built-in); Oracle Forms PL/SQL (client-side, Oracle Forms 12c runtime)
- Framework(s):                Oracle Forms 12c (12.2.1.4); Oracle Reports 12c
- Architecture style:          Monolith — HIGH confidence. Single Oracle schema (HRMS), single Forms application server, no service boundaries.
- Deployment target:           Oracle WebLogic 12c Application Server + Oracle Database 19c; on-premises or private data centre (no cloud IaC found)
- Total files scanned:         31 (README, 2 seed SQL, 2 PLL libraries, 5 form XML exports, 1 menu MMB, 7 package specs/bodies, 1 reporting package, 1 security package, 2 trigger files, 1 sequence file, 4 table DDL files, 1 view file)
- Technology layers found:     4 — Application (Forms + PL/SQL), Data (Oracle 19c schema), Security (PKG_SECURITY + DBMS_CRYPTO), Observability (AUDIT_LOG + NOTIFICATION_QUEUE)
- Chunks processed:            4 (Application, Data, Security, Observability)
- External integrations found: 3 (SMTP relay, GL feed, Benefits feed)
- Data stores identified:      1 (Oracle Database 19c, HRMS schema)
- Services / components found: 3 (Oracle Forms App Server, Oracle WebLogic 12c, Oracle Database 19c)
- CI/CD pipeline files read:   0 (none found in repository)
- CI/CD tool invocations found: None

---

## Agent 1 - Chunk 0 - Project-Wide Structural Scan

**Folder/Module Structure (2 levels):**
```
ts-plsql-oracle-forms-hrms-main/
├── README.md
├── data/
│   └── seed/
│       ├── 01_reference_data.sql
│       └── 02_employee_data.sql
├── forms/
│   ├── libraries/
│   │   ├── HRMS_COMMON_LIB.pll.sql
│   │   └── HRMS_VALIDATION_LIB.pll.sql
│   ├── menus/
│   │   └── HRMS_MENU.mmb.sql
│   └── xml-exports/
│       ├── HRMS_EMPLOYEE.xml
│       ├── HRMS_LEAVE.xml
│       ├── HRMS_LOGIN.xml
│       ├── HRMS_MENU.xml
│       ├── HRMS_PAYROLL.xml
│       └── HRMS_PERFORMANCE.xml
├── plsql/
│   ├── packages/
│   │   ├── PKG_AUDIT.pkb / .pks
│   │   ├── PKG_COMMON.pkb / .pks
│   │   ├── PKG_EMPLOYEE.pkb / .pks          [NOT FOUND in scan]
│   │   ├── PKG_INTEGRATION.pkb / .pks       [NOT FOUND in scan]
│   │   ├── PKG_LEAVE.pkb / .pks             [NOT FOUND in scan]
│   │   ├── PKG_NOTIFICATION.pkb / .pks      [NOT FOUND in scan]
│   │   ├── PKG_PAYROLL.pkb / .pks           [NOT FOUND in scan]
│   │   ├── PKG_PERFORMANCE.pkb / .pks       [NOT FOUND in scan]
│   │   ├── PKG_REPORTING.pkb / .pks
│   │   ├── PKG_SECURITY.pkb / .pks
│   │   └── PKG_VALIDATION.pkb / .pks
│   └── triggers/
│       ├── trg_audit.sql
│       └── trg_employees.sql
└── schema/
    ├── sequences/
    │   └── hrms_sequences.sql
    ├── tables/
    │   ├── 01_core_tables.sql
    │   ├── 02_payroll_tables.sql
    │   ├── 03_leave_tables.sql
    │   └── 04_performance_tables.sql
    └── views/
        └── hrms_views.sql
```

**Technology Layers Present:**
- Application: Oracle Forms 12c (.fmb/.fmx compiled, .xml exports), Oracle Reports 12c (.rdf/.rep), PL/SQL Packages (12), Forms PL/SQL Libraries (PLL)
- Data: Oracle Database 19c (HRMS schema) — 30 tables found in DDL (README states 42), 6 views found (README states 15), 29 sequences, 6 triggers provided (README states 200+)
- Infrastructure: Oracle WebLogic 12c (from README only — no IaC files found)
- Security: PKG_SECURITY (authentication, session, encryption), DBMS_CRYPTO
- Observability: AUDIT_LOG table, NOTIFICATION_QUEUE table, PKG_AUDIT package
- CI/CD: NONE FOUND

**Manifest/Config files:** SYSTEM_PARAMETERS table (runtime config); no external config files (appsettings, .env, yaml) found
**IaC files:** NONE FOUND
**CI/CD pipeline files:** NONE FOUND
**API contract files:** NONE FOUND

**Deployable services:** 1 (monolithic Oracle Forms application)
**Data stores:** 1 (Oracle Database 19c)
**External integrations:** 3 confirmed (SMTP, GL feed, Benefits feed)

**Chunk Plan (highest information density first):**
1. Data Layer — schema DDL, sequences, views, seed data (highest density — 30 tables, 29 sequences, 6 views)
2. Application Layer — PL/SQL packages, Forms XML, PLL libraries (business logic surface)
3. Security Layer — PKG_SECURITY, DBMS_CRYPTO, session management
4. Observability Layer — PKG_AUDIT, AUDIT_LOG, NOTIFICATION_QUEUE

---

## Agent 1 - Chunk 1 of 4 - Data Layer

**Carried Forward from Prior Chunks:**
- Technology components: Oracle Database 19c, Oracle Forms 12c, Oracle WebLogic 12c
- Data stores: (none yet — established this chunk)
- Integrations: (none yet)
- LOW CONFIDENCE items: 0

---

### Tables Found

**Core Tables (01_core_tables.sql):**

| # | Table | PK Column | Key Columns |
|---|---|---|---|
| 1 | DEPARTMENTS | DEPT_ID NUMBER(10) | DEPT_CODE VARCHAR2(20) UK, DEPT_NAME, PARENT_DEPT_ID (self-ref FK), COST_CENTER, MANAGER_EMP_ID, LOCATION_CODE, ACTIVE_FLAG CHAR(1) DEFAULT 'Y'; CHECK ACTIVE_FLAG IN ('Y','N') |
| 2 | LOCATIONS | LOCATION_CODE VARCHAR2(10) | LOCATION_NAME, ADDRESS_LINE1/2, CITY, STATE_PROVINCE, POSTAL_CODE, COUNTRY_CODE VARCHAR2(3), PHONE_NUMBER, TIMEZONE DEFAULT 'America/New_York', ACTIVE_FLAG |
| 3 | JOB_GRADES | GRADE_ID NUMBER(5) | GRADE_CODE UK, GRADE_NAME, MIN_SALARY NUMBER(12,2) NOT NULL, MAX_SALARY NUMBER(12,2) NOT NULL, OVERTIME_ELIGIBLE CHAR(1) DEFAULT 'N', ACTIVE_FLAG; CHECK MAX_SALARY >= MIN_SALARY |
| 4 | JOB_TITLES | JOB_ID NUMBER(10) | JOB_CODE UK, JOB_TITLE, JOB_FAMILY, GRADE_ID FK→JOB_GRADES, EEO_CATEGORY VARCHAR2(10), FLSA_STATUS DEFAULT 'EXEMPT', ACTIVE_FLAG |
| 5 | EMPLOYEES | EMP_ID NUMBER(10) | EMP_NUMBER UK, FIRST_NAME NOT NULL, MIDDLE_NAME, LAST_NAME NOT NULL, DATE_OF_BIRTH, GENDER CHAR(1) CHECK IN ('M','F','O'), MARITAL_STATUS, NATIONALITY, SSN_ENCRYPTED VARCHAR2(200), EMAIL VARCHAR2(100), PHONE_WORK/MOBILE VARCHAR2(30), ADDRESS_LINE1/2 VARCHAR2(200), CITY/STATE/POSTAL/COUNTRY, HIRE_DATE NOT NULL, TERMINATION_DATE, TERMINATION_REASON VARCHAR2(50), DEPT_ID FK, JOB_ID FK, MANAGER_EMP_ID self-ref FK, LOCATION_CODE FK, EMPLOYMENT_TYPE VARCHAR2(20) DEFAULT 'FULL_TIME' CHECK IN ('FULL_TIME','PART_TIME','CONTRACT','INTERN'), EMPLOYMENT_STATUS VARCHAR2(20) DEFAULT 'ACTIVE' CHECK IN ('ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED'), PHOTO_BLOB, NOTES CLOB, ACTIVE_FLAG DEFAULT 'Y' |
| 6 | EMPLOYEE_HISTORY | HIST_ID NUMBER(15) | EMP_ID FK, CHANGE_TYPE CHECK IN ('HIRE','TRANSFER','PROMOTION','DEMOTION','SALARY_CHANGE','TERMINATION','REHIRE','LEAVE_START','LEAVE_END','STATUS_CHANGE'), EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY NUMBER(12,2), NEW_SALARY NUMBER(12,2), OLD_LOCATION VARCHAR2(10), NEW_LOCATION VARCHAR2(10), REASON_CODE VARCHAR2(30), COMMENTS VARCHAR2(4000) |
| 7 | EMPLOYEE_DEPENDENTS | DEPENDENT_ID NUMBER(10) | EMP_ID FK, FIRST_NAME/LAST_NAME NOT NULL, RELATIONSHIP CHECK IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER'), DATE_OF_BIRTH, SSN_ENCRYPTED, BENEFITS_ENROLLED CHAR(1) DEFAULT 'N', ACTIVE_FLAG |
| 8 | EMERGENCY_CONTACTS | CONTACT_ID NUMBER(10) | EMP_ID FK, CONTACT_NAME NOT NULL, RELATIONSHIP, PHONE_PRIMARY NOT NULL, PHONE_SECONDARY, EMAIL, PRIORITY_ORDER DEFAULT 1, ACTIVE_FLAG |

**Payroll Tables (02_payroll_tables.sql):**

| # | Table | PK Column | Key Columns |
|---|---|---|---|
| 9 | SALARY_RECORDS | SALARY_ID NUMBER(10) | EMP_ID FK, EFFECTIVE_DATE NOT NULL, END_DATE, BASE_SALARY NUMBER(12,2) NOT NULL, CURRENCY_CODE DEFAULT 'USD', PAY_FREQUENCY CHECK IN ('WEEKLY','BIWEEKLY','SEMIMONTHLY','MONTHLY') DEFAULT 'MONTHLY', SALARY_BASIS CHECK IN ('ANNUAL','HOURLY') DEFAULT 'ANNUAL', CHANGE_REASON VARCHAR2(50), CHANGE_PCT NUMBER(5,2), APPROVED_BY NUMBER(10), APPROVAL_DATE, ACTIVE_FLAG |
| 10 | PAY_ELEMENTS | ELEMENT_ID NUMBER(10) | ELEMENT_CODE UK, ELEMENT_NAME, ELEMENT_TYPE CHECK IN ('EARNING','DEDUCTION','TAX','BENEFIT','REIMBURSEMENT'), CALCULATION_TYPE CHECK IN ('FLAT','PERCENTAGE','HOURS','FORMULA'), DEFAULT_AMOUNT NUMBER(12,2), DEFAULT_PERCENTAGE NUMBER(5,2), TAXABLE_FLAG DEFAULT 'Y', PRETAX_FLAG DEFAULT 'N', EMPLOYER_PAID DEFAULT 'N', GL_ACCOUNT_CODE VARCHAR2(30), PRIORITY_ORDER DEFAULT 100 |
| 11 | EMPLOYEE_PAY_ELEMENTS | EMP_ELEMENT_ID NUMBER(10) | EMP_ID FK, ELEMENT_ID FK, EFFECTIVE_DATE, END_DATE, AMOUNT, PERCENTAGE, OVERRIDE_AMOUNT, ACTIVE_FLAG |
| 12 | PAY_PERIODS | PERIOD_ID NUMBER(10) | PERIOD_NAME VARCHAR2(50), PAY_FREQUENCY, PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE NOT NULL, STATUS CHECK IN ('OPEN','PROCESSING','CLOSED','REVERSED') DEFAULT 'OPEN', CLOSED_BY, CLOSED_DATE |
| 13 | PAYROLL_RUNS | RUN_ID NUMBER(10) | PERIOD_ID FK, RUN_TYPE CHECK IN ('REGULAR','SUPPLEMENTAL','BONUS','FINAL') DEFAULT 'REGULAR', RUN_DATE NOT NULL, STATUS CHECK IN ('PENDING','CALCULATING','CALCULATED','APPROVED','PAID','REVERSED','ERROR') DEFAULT 'PENDING', TOTAL_GROSS/DEDUCTIONS/NET/EMPLOYER_COST NUMBER(15,2), EMPLOYEE_COUNT, ERROR_COUNT DEFAULT 0, SUBMITTED_BY/DATE, APPROVED_BY/DATE |
| 14 | PAYROLL_DETAILS | DETAIL_ID NUMBER(15) | RUN_ID FK, EMP_ID FK, ELEMENT_ID FK, ELEMENT_TYPE NOT NULL, HOURS_WORKED NUMBER(6,2), RATE NUMBER(12,4), AMOUNT NUMBER(12,2) NOT NULL, YTD_AMOUNT, STATUS DEFAULT 'CALCULATED', ERROR_MESSAGE VARCHAR2(4000) |
| 15 | TAX_BRACKETS | BRACKET_ID NUMBER(10) | TAX_YEAR NUMBER(4), FILING_STATUS CHECK IN ('SINGLE','MARRIED_JOINT','MARRIED_SEPARATE','HEAD_OF_HOUSEHOLD'), BRACKET_MIN/MAX NUMBER(12,2), TAX_RATE NUMBER(5,4), BASE_TAX DEFAULT 0, STATE_CODE VARCHAR2(3) (NULL=federal), ACTIVE_FLAG |
| 16 | EMPLOYEE_TAX_INFO | TAX_INFO_ID NUMBER(10) | EMP_ID FK, TAX_YEAR NUMBER(4), FILING_STATUS, FEDERAL_ALLOWANCES DEFAULT 0, STATE_ALLOWANCES DEFAULT 0, ADDITIONAL_FED_WH/STATE_WH DEFAULT 0, EXEMPT_FLAG DEFAULT 'N', STATE_CODE, W4_RECEIVED_DATE, ACTIVE_FLAG; UK (EMP_ID, TAX_YEAR) |
| 17 | EMPLOYEE_BANK_ACCOUNTS | BANK_ACCT_ID NUMBER(10) | EMP_ID FK, BANK_NAME, ROUTING_NUMBER NOT NULL, ACCOUNT_NUMBER_ENC VARCHAR2(200) NOT NULL (encrypted), ACCOUNT_TYPE CHECK IN ('CHECKING','SAVINGS') DEFAULT 'CHECKING', DEPOSIT_TYPE CHECK IN ('FULL','PARTIAL_AMOUNT','PARTIAL_PERCENT','REMAINDER') DEFAULT 'FULL', DEPOSIT_AMOUNT, DEPOSIT_PERCENTAGE, PRIORITY_ORDER DEFAULT 1, PRENOTE_SENT DEFAULT 'N', PRENOTE_DATE, ACTIVE_FLAG |

**Leave Tables (03_leave_tables.sql):**

| # | Table | PK Column | Key Columns |
|---|---|---|---|
| 18 | LEAVE_TYPES | LEAVE_TYPE_ID NUMBER(5) | LEAVE_TYPE_CODE UK, LEAVE_TYPE_NAME, PAID_FLAG DEFAULT 'Y', ACCRUAL_FLAG DEFAULT 'Y', ACCRUAL_RATE NUMBER(6,2), ACCRUAL_FREQUENCY CHECK IN ('MONTHLY','BIWEEKLY','ANNUAL',NULL), MAX_BALANCE NUMBER(6,2), CARRYOVER_MAX, CARRYOVER_EXPIRY NUMBER(3), MIN_TENURE_DAYS DEFAULT 0, REQUIRES_APPROVAL DEFAULT 'Y', REQUIRES_DOCUMENT DEFAULT 'N', ACTIVE_FLAG |
| 19 | LEAVE_BALANCES | BALANCE_ID NUMBER(10) | EMP_ID FK, LEAVE_TYPE_ID FK, CALENDAR_YEAR NUMBER(4), OPENING_BALANCE DEFAULT 0, ACCRUED DEFAULT 0, USED DEFAULT 0, ADJUSTMENT DEFAULT 0, PENDING DEFAULT 0, AVAILABLE — VIRTUAL GENERATED ALWAYS AS (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING), CARRYOVER_FROM_PREV DEFAULT 0, CARRYOVER_EXPIRY_DT; UK (EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR) |
| 20 | LEAVE_REQUESTS | REQUEST_ID NUMBER(10) | EMP_ID FK, LEAVE_TYPE_ID FK, START_DATE/END_DATE NOT NULL, TOTAL_DAYS NUMBER(5,1) NOT NULL, HALF_DAY_FLAG DEFAULT 'N', HALF_DAY_PERIOD CHECK IN ('AM','PM',NULL), STATUS CHECK IN ('PENDING','APPROVED','REJECTED','CANCELLED','TAKEN') DEFAULT 'PENDING', REASON VARCHAR2(4000), SUPPORTING_DOC_PATH, APPROVER_EMP_ID FK→EMPLOYEES, APPROVAL_DATE, APPROVAL_COMMENTS, CANCEL_REASON, CANCELLED_DATE; CHECK END_DATE >= START_DATE |
| 21 | LEAVE_ACCRUAL_LOG | ACCRUAL_ID NUMBER(15) | EMP_ID FK, LEAVE_TYPE_ID FK, ACCRUAL_DATE NOT NULL, ACCRUAL_AMOUNT NUMBER(6,2) NOT NULL, BALANCE_AFTER, RUN_ID |
| 22 | HOLIDAYS | HOLIDAY_ID NUMBER(5) | HOLIDAY_DATE NOT NULL, HOLIDAY_NAME NOT NULL, LOCATION_CODE VARCHAR2(10) (NULL=global), FLOATING_FLAG DEFAULT 'N', ACTIVE_FLAG; 10 rows seeded (2024 US federal holidays) |

**Performance & System Tables (04_performance_tables.sql):**

| # | Table | PK Column | Key Columns |
|---|---|---|---|
| 23 | REVIEW_CYCLES | CYCLE_ID NUMBER(10) | CYCLE_NAME, CYCLE_YEAR NUMBER(4), START_DATE/END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, CALIBRATION_DUE, STATUS CHECK IN ('DRAFT','OPEN','IN_PROGRESS','CALIBRATION','CLOSED') DEFAULT 'DRAFT' |
| 24 | PERFORMANCE_REVIEWS | REVIEW_ID NUMBER(10) | CYCLE_ID FK, EMP_ID FK, REVIEWER_EMP_ID FK, REVIEW_TYPE DEFAULT 'ANNUAL', STATUS CHECK IN ('NOT_STARTED','SELF_REVIEW','MANAGER_REVIEW','MEETING_SCHEDULED','COMPLETED','ACKNOWLEDGED') DEFAULT 'NOT_STARTED', OVERALL_RATING NUMBER(2,1) CHECK BETWEEN 1.0 AND 5.0, RATING_LABEL VARCHAR2(50), SELF_ASSESSMENT CLOB, MANAGER_ASSESSMENT CLOB, STRENGTHS CLOB, AREAS_FOR_IMPROVEMENT CLOB, DEVELOPMENT_PLAN CLOB, EMPLOYEE_COMMENTS CLOB, EMPLOYEE_ACK_DATE, CALIBRATED_RATING NUMBER(2,1), CALIBRATION_NOTES VARCHAR2(4000) |
| 25 | PERFORMANCE_GOALS | GOAL_ID NUMBER(10) | REVIEW_ID FK, EMP_ID FK, GOAL_TITLE VARCHAR2(200) NOT NULL, GOAL_DESCRIPTION CLOB, GOAL_CATEGORY CHECK IN ('BUSINESS','DEVELOPMENT','LEADERSHIP','INNOVATION','COMPLIANCE'), WEIGHT_PCT NUMBER(5,2) DEFAULT 0, TARGET_DATE, STATUS CHECK IN ('NOT_STARTED','IN_PROGRESS','COMPLETED','DEFERRED','CANCELLED') DEFAULT 'NOT_STARTED', PROGRESS_PCT DEFAULT 0, SELF_RATING NUMBER(2,1), MANAGER_RATING NUMBER(2,1), COMMENTS CLOB |
| 26 | AUDIT_LOG | AUDIT_ID NUMBER(15) | TABLE_NAME VARCHAR2(60) NOT NULL, RECORD_ID NUMBER(15) NOT NULL, ACTION_TYPE CHECK IN ('INSERT','UPDATE','DELETE'), OLD_VALUES CLOB, NEW_VALUES CLOB, CHANGED_BY VARCHAR2(30) NOT NULL, CHANGED_DATE DEFAULT SYSDATE, IP_ADDRESS VARCHAR2(50), SESSION_ID VARCHAR2(100) |
| 27 | SYSTEM_PARAMETERS | PARAM_ID NUMBER(5) | PARAM_GROUP VARCHAR2(50), PARAM_CODE VARCHAR2(50), PARAM_VALUE VARCHAR2(4000) NOT NULL, PARAM_DESCRIPTION, DATA_TYPE DEFAULT 'VARCHAR2', EDITABLE_FLAG DEFAULT 'Y'; UK (PARAM_GROUP, PARAM_CODE) |
| 28 | NOTIFICATION_QUEUE | NOTIFICATION_ID NUMBER(15) | RECIPIENT_EMP_ID, RECIPIENT_EMAIL VARCHAR2(100), NOTIFICATION_TYPE CHECK IN ('EMAIL','IN_APP','SMS'), SUBJECT VARCHAR2(200) NOT NULL, BODY CLOB NOT NULL, STATUS CHECK IN ('PENDING','SENT','FAILED','CANCELLED') DEFAULT 'PENDING', PRIORITY DEFAULT 5, SENT_DATE, ERROR_MESSAGE VARCHAR2(4000), RETRY_COUNT DEFAULT 0, REFERENCE_TABLE VARCHAR2(60), REFERENCE_ID NUMBER(15) |
| 29 | USER_SESSIONS | SESSION_ID NUMBER(15) | EMP_ID FK, USERNAME VARCHAR2(30) NOT NULL, LOGIN_TIME NOT NULL, LOGOUT_TIME, IP_ADDRESS VARCHAR2(50), FORMS_MODULE VARCHAR2(100), SESSION_STATUS DEFAULT 'ACTIVE' |
| 30 | LOOKUP_VALUES | LOOKUP_ID NUMBER(10) | LOOKUP_TYPE VARCHAR2(50), LOOKUP_CODE VARCHAR2(50), LOOKUP_VALUE VARCHAR2(200) NOT NULL, DISPLAY_ORDER DEFAULT 0, PARENT_LOOKUP_ID self-ref, ACTIVE_FLAG; UK (LOOKUP_TYPE, LOOKUP_CODE) |

**Tables referenced in code but NOT in provided DDL:**
- USER_CREDENTIALS — referenced in PKG_SECURITY.change_password (LOW — stub implementation; DDL absent)
- RPT_* tables — referenced in PKG_REPORTING.refresh_reporting_tables as denormalized reporting tables (LOW — DDL absent)

---

**Views (hrms_views.sql — 6 of 15 stated in README):**

| View | Purpose | Key Formula / Business Rule |
|---|---|---|
| VW_ACTIVE_EMPLOYEES | Denormalized active employee detail with dept, job, manager, location, salary | TENURE_YEARS = TRUNC(MONTHS_BETWEEN(SYSDATE, HIRE_DATE) / 12, 1); salary join: ACTIVE_FLAG='Y' AND EFFECTIVE_DATE <= SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE) |
| VW_ORG_HIERARCHY | Hierarchical org chart via Oracle CONNECT BY | ORG_PATH separator = ' > '; START WITH MANAGER_EMP_ID IS NULL; Performance warning documented: degrades >500 employees |
| VW_EMPLOYEE_COMPENSATION | Current compensation with compa-ratio | COMPA_RATIO = ROUND(BASE_SALARY / ((MIN_SALARY + MAX_SALARY) / 2) * 100, 1) |
| VW_LEAVE_SUMMARY | Current-year leave balances with utilisation | AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT (omits PENDING — DISC-001); UTILIZATION_PCT = ROUND(USED * 100 / NULLIF(OPENING_BALANCE + ACCRUED, 0), 1) |
| VW_PAYROLL_LATEST | Latest approved payroll run per employee | Latest = MAX(RUN_ID) WHERE STATUS='APPROVED'; ABS() applied to TAX/DEDUCTION/BENEFIT amounts |
| VW_PENDING_APPROVALS | Unified pending approvals (LEAVE + PERFORMANCE) | UNION ALL: lr.STATUS='PENDING' for leave; pr.STATUS='MANAGER_REVIEW' for performance |

---

**Sequences (hrms_sequences.sql — 29 total):**

| Sequence | Start With | Increment By | Cache | Used By |
|---|---|---|---|---|
| SEQ_DEPARTMENT | 100 | 1 | NOCACHE | DEPARTMENTS.DEPT_ID |
| SEQ_LOCATION | 100 | 1 | NOCACHE | LOCATIONS surrogate |
| SEQ_JOB_GRADE | 100 | 1 | NOCACHE | JOB_GRADES.GRADE_ID |
| SEQ_JOB_TITLE | 100 | 1 | NOCACHE | JOB_TITLES.JOB_ID |
| SEQ_EMPLOYEE | 10000 | 1 | NOCACHE | EMPLOYEES.EMP_ID |
| SEQ_EMP_HISTORY | 1 | 1 | NOCACHE | EMPLOYEE_HISTORY.HIST_ID |
| SEQ_DEPENDENT | 1 | 1 | NOCACHE | EMPLOYEE_DEPENDENTS.DEPENDENT_ID |
| SEQ_EMERGENCY_CONTACT | 1 | 1 | NOCACHE | EMERGENCY_CONTACTS.CONTACT_ID |
| SEQ_EMP_NUMBER | 1000 | 1 | NOCACHE | EMP_NUMBER generation — BUG: PKG_EMPLOYEE uses MAX()+1 instead; race condition |
| SEQ_SALARY | 1 | 1 | NOCACHE | SALARY_RECORDS.SALARY_ID |
| SEQ_PAY_ELEMENT | 1 | 1 | NOCACHE | PAY_ELEMENTS.ELEMENT_ID |
| SEQ_EMP_PAY_ELEMENT | 1 | 1 | NOCACHE | EMPLOYEE_PAY_ELEMENTS.EMP_ELEMENT_ID |
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
| SEQ_AUDIT | 1 | 1 | CACHE 100 | AUDIT_LOG.AUDIT_ID — only cached sequence |
| SEQ_NOTIFICATION | 1 | 1 | NOCACHE | NOTIFICATION_QUEUE.NOTIFICATION_ID |
| SEQ_USER_SESSION | 1 | 1 | NOCACHE | USER_SESSIONS.SESSION_ID |
| SEQ_SYSTEM_PARAM | 1 | 1 | NOCACHE | SYSTEM_PARAMETERS.PARAM_ID |
| SEQ_LOOKUP | 1 | 1 | NOCACHE | LOOKUP_VALUES.LOOKUP_ID |

---

**Database Triggers (6 provided; README states 200+ total):**

| Trigger | Table | Timing / Event | Purpose |
|---|---|---|---|
| TRG_SALARY_AUDIT | SALARY_RECORDS | AFTER INSERT OR UPDATE OR DELETE, FOR EACH ROW | Logs salary changes to AUDIT_LOG as JSON |
| TRG_LEAVE_REQUEST_AUDIT | LEAVE_REQUESTS | AFTER UPDATE OF STATUS, FOR EACH ROW | Logs leave status changes to AUDIT_LOG |
| TRG_DEPARTMENT_AUDIT | DEPARTMENTS | AFTER INSERT OR UPDATE OR DELETE, FOR EACH ROW | Logs department changes to AUDIT_LOG |
| TRG_EMP_BEFORE_INSERT | EMPLOYEES | BEFORE INSERT, FOR EACH ROW | Sets audit cols; validates HIRE_DATE <= SYSDATE+180; enforces email uniqueness |
| TRG_EMP_BEFORE_UPDATE | EMPLOYEES | BEFORE UPDATE, FOR EACH ROW | Sets MODIFIED_BY/DATE; prevents TERMINATED→ACTIVE; logs STATUS/DEPT/JOB changes to EMPLOYEE_HISTORY |
| TRG_EMP_INSTEAD_OF_DELETE | EMPLOYEES | BEFORE DELETE, FOR EACH ROW | Blocks all direct DELETEs; enforces soft-delete pattern |

### Chunk Inventory - Data Layer
- Technology components found this chunk: Oracle Database 19c (HRMS schema)
- Data stores found this chunk: Oracle Database 19c — 30 tables DDL-defined, 6 views, 29 sequences, 6 triggers provided
- Integrations found this chunk: GL_ACCOUNT_CODE on PAY_ELEMENTS; SMTP_HOST in SYSTEM_PARAMETERS
- Infrastructure resources found: None (no IaC)
- Environments identified: None
- CI/CD tool invocations found: None
- Reusable workflows followed: None
- Cross-layer dependencies flagged: AUDIT_LOG written by PKG_AUDIT, PKG_COMMON, and all 6 triggers — shared across Data + Observability
- Newly flagged as SHARED COMPONENT: AUDIT_LOG; SYSTEM_PARAMETERS
- VERSION CONFLICTS detected: None
- LOW CONFIDENCE items raised this chunk:
  - LOW: USER_CREDENTIALS table absent from DDL; referenced in PKG_SECURITY
  - LOW: RPT_* tables absent from DDL; referenced in PKG_REPORTING
  - LOW: 12 tables missing (README states 42; 30 found)
  - LOW: 9 views missing (README states 15; 6 found)
  - LOW: ~194 triggers missing (README states 200+; 6 provided)
  - DISC-001: VW_LEAVE_SUMMARY.AVAILABLE omits PENDING vs LEAVE_BALANCES virtual column — Agent 2 to resolve

---

## Agent 1 - Chunk 2 of 4 - Application Layer

**Carried Forward:**
- Technology components: Oracle Database 19c, Oracle Forms 12c, Oracle WebLogic 12c
- Data stores: Oracle Database 19c (HRMS schema — 30 tables, 6 views, 29 sequences)
- Integrations: GL feed (ACTIVE), Benefits feed (ACTIVE), SMTP relay
- LOW CONFIDENCE items: 6

---

### PL/SQL Packages

**PKG_AUDIT** (base package — no cross-package deps; spec + body provided):
- `log_action(table_name, record_id, action, user DEFAULT USER, old_values CLOB DEFAULT NULL, new_values CLOB DEFAULT NULL)` — PRAGMA AUTONOMOUS_TRANSACTION; INSERT to AUDIT_LOG; captures SYS_CONTEXT('USERENV','IP_ADDRESS') and SYS_CONTEXT('USERENV','SESSIONID')
- `purge_old_records(days_to_keep NUMBER DEFAULT 365, user)` — DELETE FROM AUDIT_LOG WHERE CHANGED_DATE < SYSDATE - p_days_to_keep; business rule: default retention 365 days
- `get_change_history(table_name, record_id, from_date, to_date) RETURN SYS_REFCURSOR`

**PKG_COMMON** (base package — no cross-package deps; spec + body provided):
- `log_error / log_info` — PRAGMA AUTONOMOUS_TRANSACTION; INSERT to AUDIT_LOG; message truncated at 3000 chars
- `get_param(group, code) RETURN VARCHAR2` — SELECT PARAM_VALUE FROM SYSTEM_PARAMETERS
- `get_param_number / get_param_date` — wrappers on get_param
- `set_param(group, code, value, user)` — UPDATE SYSTEM_PARAMETERS WHERE EDITABLE_FLAG='Y'; raises -20900 if not editable
- `business_days_between(start_date, end_date) RETURN NUMBER` — loop; excludes SAT/SUN; NLS forced to AMERICAN
- `add_business_days(date, days) RETURN DATE`
- `get_fiscal_year(date) RETURN NUMBER` — IF MONTH >= 10: RETURN YEAR+1 ELSE RETURN YEAR (fiscal year starts October)
- `get_fiscal_quarter(date) RETURN NUMBER` — Q1=Oct-Dec, Q2=Jan-Mar, Q3=Apr-Jun, Q4=Jul-Sep
- `format_phone` — 10-digit: (NNN) NNN-NNNN; 11-digit starting 1: +1 (NNN) NNN-NNNN
- `format_ssn_masked` — returns '***-**-' || LAST_4_DIGITS
- `format_currency` — USD=$, EUR=€ (CHR(8364)), GBP=£ (CHR(163))
- `format_name(first, last, format DEFAULT 'FL')` — 'FL'=First Last, 'LF'=Last, First (INITCAP applied)
- `is_valid_email` — REGEXP_LIKE('^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') — accepts subdomains (more permissive than client-side)
- `is_valid_phone` — LENGTH(REGEXP_REPLACE non-digits) BETWEEN 10 AND 11
- `is_valid_ssn` — REGEXP_LIKE stripped digits against '^\d{9}$'

**PKG_VALIDATION** (deps: PKG_COMMON; spec + body provided):
- `validate_date_range(start, end) RETURN BOOLEAN` — end >= start; both required
- `validate_salary_for_grade(salary, grade_id) RETURN VARCHAR2` — queries JOB_GRADES; format mask 'FM$999,999,990.00'; returns NULL if valid
- `validate_email_format` — delegates to PKG_COMMON.is_valid_email
- `validate_phone_format` — delegates to PKG_COMMON.is_valid_phone
- `validate_emp_number_format` — REGEXP_LIKE('^EMP-\d{6}$'); exactly 6 digits after 'EMP-'
- `is_future_date(date) RETURN BOOLEAN` — TRUNC(date) > TRUNC(SYSDATE); same-day NOT considered future
- `is_business_day(date, location_code DEFAULT NULL) RETURN BOOLEAN` — excludes SAT/SUN + HOLIDAYS table lookup
- `validate_required_fields(table_name, record_id) RETURN VARCHAR2` — only EMPLOYEES handled; checks FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID

**PKG_REPORTING** (deps: PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON; spec + body provided):
- `headcount_report` — returns HEADCOUNT, FT/PT/CONTRACT counts, MALE/FEMALE counts, AVG_TENURE_YEARS
- `compensation_summary` — COMPA_RATIO = AVG(BASE_SALARY / ((MIN+MAX)/2)) * 100 rounded to 1 decimal
- `turnover_report` — TURNOVER_PCT = terminations / employees_hired_on_or_before_end_date * 100; NULLIF prevents divide-by-zero
- `new_hires_report`, `leave_utilization_report`, `payroll_summary_report`, `eeo_compliance_report`
- `refresh_reporting_tables` — STUB; calls log_info only; intended to populate RPT_* tables nightly
- Known issue: denormalized reporting tables stale during business hours; some reports hard-code fiscal year start Oct 1

**PKG_SECURITY** — documented in Chunk 3 (Security Layer).

**Packages NOT found — body and spec absent (7 of 12):**

| Package | Evidence of Existence | Inferred Signatures |
|---|---|---|
| PKG_EMPLOYEE | README + HRMS_EMPLOYEE PRE-INSERT + PKG_SECURITY.authenticate call | generate_emp_number() RETURN VARCHAR2; set_session_context(username, emp_id) |
| PKG_LEAVE | README + HRMS_LEAVE form calls | cancel_leave_request(request_id, reason, user); submit_leave_request(emp_id, leave_type_id, start_date, end_date, half_day_flag, reason, user) RETURN NUMBER |
| PKG_PAYROLL | README + HRMS_PAYROLL form calls | create_payroll_run(period_id, run_type, user) RETURN NUMBER; calculate_payroll(run_id, user); approve_payroll(run_id, user) |
| PKG_PERFORMANCE | README + partial body content in scan | create_review, submit_self_assessment, complete_review, acknowledge_review, add_goal, update_goal_progress, get_team_reviews, get_rating_distribution, generate_reviews_for_cycle |
| PKG_NOTIFICATION | README + NOTIFICATION_QUEUE table | (unknown — table implies send_notification or queue_notification procedures) |
| PKG_INTEGRATION | README + SYSTEM_PARAMETERS GL_FEED_STATUS / BENEFITS_FEED_STATUS | (unknown — GL and Benefits feed implementation entirely absent) |

**PKG_PERFORMANCE partial body content found in scan (source unclear — LOW confidence):**
- Rating thresholds: >=4.5 Exceptional; 3.5–4.5 Exceeds Expectations; 2.5–3.5 Meets Expectations; 1.5–2.5 Needs Improvement; <1.5 Unsatisfactory
- Review status lifecycle: NOT_STARTED → SELF_REVIEW → MANAGER_REVIEW → COMPLETED → ACKNOWLEDGED
- Sequences used: SEQ_REVIEW_CYCLE, SEQ_PERF_REVIEW, SEQ_PERF_GOAL
- Rating business rule: must be between 1.0 and 5.0 inclusive

---

### Oracle Forms Libraries

**HRMS_COMMON_LIB.pll** (attached to all forms; standalone — no cross-package deps except PKG_COMMON.log_error and PKG_SECURITY.is_session_valid):
- `handle_error(module, location)` — calls PKG_COMMON.log_error; calls MESSAGE() twice (documented: Oracle Forms requires 2 calls for status bar display); raises FORM_TRIGGER_FAILURE; inner exception block swallows recursion errors silently
- Toolbar procedures: toolbar_save (COMMIT_FORM), toolbar_clear (CLEAR_FORM), toolbar_query (ENTER/EXECUTE_QUERY), toolbar_first/prev/next/last, toolbar_insert (CREATE_RECORD), toolbar_delete (DELETE_RECORD), toolbar_exit (EXIT_FORM)
- `format_date(date)` → TO_CHAR(date, 'MM/DD/YYYY')
- `format_datetime(date)` → TO_CHAR(date, 'MM/DD/YYYY HH24:MI:SS')
- `get_current_user()` → NVL(:GLOBAL.current_user, USER)
- `get_session_id()` → TO_NUMBER(:GLOBAL.session_id)
- `check_session()` — calls PKG_SECURITY.is_session_valid; raises FORM_TRIGGER_FAILURE if invalid/expired
- `refresh_lov(lov_name)` — derives RG_ prefix; calls POPULATE_GROUP

**HRMS_VALIDATION_LIB.pll** (attached to all forms; client-side only):
- `validate_email` — BUG: rejects valid subdomains (e.g. user@mail.company.com) — known drift from PKG_COMMON.is_valid_email
- `validate_phone` — 10 or 11 digits after stripping non-digits
- `validate_ssn` — 9 digits; rejects all-zero area (000), group (00), or serial (0000) numbers
- `validate_date_not_future` — TRUNC(date) <= TRUNC(SYSDATE)
- `validate_salary_range` — live DB query to JOB_GRADES (comment says "cached local data" but code does live query — comment/code mismatch)

---

### Oracle Forms Modules (6 of 18 provided)

| Form Binary | Purpose | Attached Libraries | Key DB Tables | Package Dependencies |
|---|---|---|---|---|
| HRMS_LOGIN.fmb | Authentication; sets GLOBAL.session_id/current_user/current_emp_id | None | EMPLOYEES | PKG_SECURITY.authenticate |
| HRMS_MENU.fmb | MDI shell; navigation hub; permission-based menu/button visibility | HRMS_COMMON_LIB | None | PKG_SECURITY.has_permission, PKG_SECURITY.logout |
| HRMS_EMPLOYEE.fmb | Employee master-detail maintenance | HRMS_COMMON_LIB, HRMS_VALIDATION_LIB | EMPLOYEES, SALARY_RECORDS, DEPARTMENTS, JOB_TITLES, JOB_GRADES, LOCATIONS | PKG_SECURITY, PKG_EMPLOYEE.generate_emp_number, PKG_VALIDATION.validate_email_format; SEQ_EMPLOYEE |
| HRMS_LEAVE.fmb | Leave requests, approvals, balances, team calendar | HRMS_COMMON_LIB | LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES | PKG_SECURITY, PKG_LEAVE.cancel_leave_request, PKG_LEAVE.submit_leave_request |
| HRMS_PAYROLL.fmb | Pay period management; payroll run creation, calculation, approval | HRMS_COMMON_LIB | PAY_PERIODS, PAYROLL_RUNS | PKG_SECURITY, PKG_PAYROLL.create_payroll_run, PKG_PAYROLL.calculate_payroll, PKG_PAYROLL.approve_payroll |
| HRMS_PERFORMANCE.fmb | Performance review cycles, self-assessments, manager reviews, goals | HRMS_COMMON_LIB | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS, EMPLOYEES | PKG_SECURITY.is_session_valid |

**Forms not provided (12 of 18):** HRMS_DEPARTMENT, HRMS_REPORTS, HRMS_LOV, HRMS_TOOLBAR (object library), HRMS_ADMIN (referenced in menus), plus 7 additional forms to reach README total of 18.

**Global Variables (Forms runtime state — set by HRMS_LOGIN, read everywhere):**
- `:GLOBAL.session_id` — numeric session token
- `:GLOBAL.current_user` — authenticated username (employee email)
- `:GLOBAL.current_emp_id` — authenticated employee ID

**Application Version:** HRMS v4.2 / APP_VERSION=4.2.0 / Build 2024.03.15

**Oracle Forms Trigger Types Used:** WHEN-NEW-FORM-INSTANCE, WHEN-VALIDATE-ITEM, WHEN-BUTTON-PRESSED, POST-QUERY, PRE-INSERT, PRE-UPDATE, ON-ERROR, KEY-EXIT, KEY-NEXT-ITEM

**Oracle Built-in Packages Used:** DBMS_OUTPUT, UTL_FILE, UTL_MAIL (README), DBMS_CRYPTO (PKG_SECURITY), UTL_RAW (PKG_SECURITY)

**Custom Error Code Range:** -20000 to -20999 (from README); specific codes documented:
-20301 invalid credentials, -20302 account locked, -20303 session expired, -20304 insufficient priv, -20310 password too short, -20311 no uppercase, -20312 no digit, -20501 hire date >180 days future, -20502 email duplicate, -20503 reactivation blocked, -20504 delete blocked, -20900 parameter not editable

### Chunk Inventory - Application Layer
- Technology components found: Oracle Forms 12c (12.2.1.4), Oracle Reports 12c, PL/SQL (Oracle 19c), DBMS_CRYPTO, UTL_FILE, UTL_MAIL, DBMS_OUTPUT, UTL_RAW
- Data stores: No new stores; cross-layer access confirmed to all 30 tables
- Integrations: SMTP (UTL_MAIL, smtp.internal.company.com); GL Feed (PKG_INTEGRATION ref); Benefits Feed (PKG_INTEGRATION ref)
- CI/CD tool invocations found: None
- Cross-layer dependencies flagged: PKG_COMMON logs to AUDIT_LOG; PKG_SECURITY reads EMPLOYEES + JOB_TITLES; PKG_VALIDATION reads JOB_GRADES
- Newly flagged as SHARED COMPONENT: EMPLOYEES (accessed by all 6 forms + multiple packages); JOB_GRADES (PKG_VALIDATION, PKG_REPORTING, views)
- VERSION CONFLICTS detected: None
- LOW CONFIDENCE items raised this chunk:
  - LOW: PKG_EMPLOYEE body absent — generate_emp_number signature inferred from form PRE-INSERT only
  - LOW: PKG_LEAVE body absent — signatures inferred from form calls only
  - LOW: PKG_PAYROLL body absent — signatures inferred from form calls only
  - LOW: PKG_NOTIFICATION body absent — purpose inferred from NOTIFICATION_QUEUE only
  - LOW: PKG_INTEGRATION body absent — GL/Benefits feed implementation unknown
  - DISC-002: Hire date future limit — HRMS_EMPLOYEE form enforces 90 days; TRG_EMP_BEFORE_INSERT enforces 180 days — UNRESOLVED CONFLICT

---

## Agent 1 - Chunk 3 of 4 - Security Layer

**Carried Forward:**
- Technology components: Oracle Database 19c, Oracle Forms 12c, Oracle WebLogic 12c, PL/SQL, DBMS_CRYPTO, UTL_FILE, UTL_MAIL, UTL_RAW
- Data stores: Oracle Database 19c (HRMS schema)
- Integrations: SMTP, GL Feed, Benefits Feed
- LOW CONFIDENCE items: 11

---

### PKG_SECURITY Detail

**Authentication mechanism:**
- Username = employee EMAIL (UPPER(EMAIL) match against EMPLOYEES WHERE EMPLOYMENT_STATUS='ACTIVE')
- Password: MD5-hashed via DBMS_CRYPTO.HASH_MD5 — documented weakness; actual authenticate() stub does NOT validate password against stored hash; any password accepted for active employees
- Session token = SEQ_USER_SESSION.NEXTVAL (numeric integer, not GUID/JWT)
- Session stored in USER_SESSIONS; timeout = 30 minutes (constant c_session_timeout_min = 30; also in SYSTEM_PARAMETERS SESSION_TIMEOUT_MIN='30')
- Timeout formula: (SYSDATE - LOGIN_TIME) * 24 * 60 > 30

**Encryption:**
- SSN encrypted with AES-256-CBC + PKCS5 padding (DBMS_CRYPTO.ENCRYPT_AES256 + CHAIN_CBC + PAD_PKCS5)
- Encryption key: RAW(32) — HARD-CODED literal 'HR$ystem_3ncrypt10n_K3y_2024!!' in PKG_SECURITY.pkb body
- Bank account numbers: column ACCOUNT_NUMBER_ENC implies encryption; mechanism not found in provided packages (LOW)

**Authorization model (grade-based, PKG_SECURITY.has_permission):**
- GRADE_ID >= 8: full access all modules, all actions
- GRADE_ID >= 5 AND action='VIEW': VIEW access all modules
- GRADE_ID < 5: LEAVE CREATE/VIEW and EMPLOYEE VIEW only
- No ROLES/PERMISSIONS junction table — documented as simplified model; grade from JOB_TITLES JOIN

**Password complexity rules (change_password):**
- Minimum 8 characters (error -20310)
- Must contain [A-Z] uppercase (error -20311)
- Must contain [0-9] digit (error -20312)
- Old password parameter accepted but NOT validated (stub)

**SECRETS MANAGEMENT PATTERN DETECTED:**
- AES-256 encryption key hard-coded in PKG_SECURITY.pkb as source-visible RAW literal
- No vault, HSM, or external secrets manager referenced anywhere in codebase

**Documented security weaknesses (all in source comments):**
1. MD5 password hashing — should be bcrypt/scrypt
2. Encryption key hard-coded in package body
3. No account lockout after failed attempts
4. Timing attack: different code path for unknown user vs wrong password
5. Password validation is a stub (old password not verified)
6. No CAPTCHA or 2FA support
7. Password transmitted in cleartext (Oracle Forms applet limitation)
8. Session timeout uses DB server time, not app server time

### Chunk Inventory - Security Layer
- Technology components: DBMS_CRYPTO (AES-256-CBC, MD5), Oracle session management (USER_SESSIONS)
- Data stores: USER_SESSIONS (SHARED); USER_CREDENTIALS (LOW — referenced, DDL absent)
- Cross-layer dependencies: PKG_SECURITY reads EMPLOYEES + JOB_TITLES; calls PKG_AUDIT.log_action; calls PKG_EMPLOYEE.set_session_context
- SHARED COMPONENT: USER_SESSIONS; EMPLOYEES
- LOW CONFIDENCE items:
  - LOW: No TLS configuration found — WebLogic handles TLS but no config available
  - LOW: USER_CREDENTIALS table DDL absent; password validation is a confirmed stub
  - SECRETS MANAGEMENT: AES-256 key hard-coded in source

---

## Agent 1 - Chunk 4 of 4 - Observability Layer

**Carried Forward:**
- Technology components: Oracle Database 19c, Oracle Forms 12c, Oracle WebLogic 12c, PL/SQL, DBMS_CRYPTO, UTL_FILE, UTL_MAIL, UTL_RAW
- Data stores: Oracle Database 19c (HRMS schema — 30 tables)
- Integrations: SMTP, GL Feed, Benefits Feed
- LOW CONFIDENCE items: 13

---

### Audit Logging

- All audit writes via PRAGMA AUTONOMOUS_TRANSACTION (never rolls back calling transaction)
- Captures: TABLE_NAME, RECORD_ID, ACTION_TYPE, OLD_VALUES (CLOB JSON), NEW_VALUES (CLOB JSON), CHANGED_BY, CHANGED_DATE, IP_ADDRESS (SYS_CONTEXT USERENV/IP_ADDRESS), SESSION_ID (SYS_CONTEXT USERENV/SESSIONID)
- Error log: TABLE_NAME='ERROR_LOG', RECORD_ID=0 in AUDIT_LOG
- Info log: TABLE_NAME='INFO_LOG', RECORD_ID=0 in AUDIT_LOG
- Default retention: 365 days (PKG_AUDIT.purge_old_records DEFAULT 365)
- SEQ_AUDIT is the only CACHE 100 sequence (all others NOCACHE)

**Tables with trigger-based audit:**
- SALARY_RECORDS — TRG_SALARY_AUDIT (all DML, JSON old/new salary + effective date)
- LEAVE_REQUESTS — TRG_LEAVE_REQUEST_AUDIT (UPDATE OF STATUS only)
- DEPARTMENTS — TRG_DEPARTMENT_AUDIT (all DML, dept_id only — no JSON)
- EMPLOYEES — TRG_EMP_BEFORE_UPDATE (writes STATUS/DEPT/JOB changes to EMPLOYEE_HISTORY)

### Notification System

- NOTIFICATION_QUEUE table supports EMAIL, IN_APP, SMS
- Status lifecycle: PENDING → SENT / FAILED / CANCELLED; RETRY_COUNT starts at 0
- SMTP host: smtp.internal.company.com; from: hrms-noreply@company.com
- PKG_NOTIFICATION body absent — queue population mechanism unknown

### No External Monitoring Platform Found

No Prometheus, Grafana, Oracle EM, Datadog, Splunk, New Relic, or equivalent tool configured. All observability is DB-internal (AUDIT_LOG table + NOTIFICATION_QUEUE).

### Chunk Inventory - Observability Layer
- Technology components: AUDIT_LOG (Oracle table, CLOB-based JSON), NOTIFICATION_QUEUE (Oracle table), SMTP relay (UTL_MAIL)
- Data stores: AUDIT_LOG (SHARED across all layers)
- Integrations: SMTP relay — smtp.internal.company.com / hrms-noreply@company.com
- LOW CONFIDENCE items:
  - LOW: No external monitoring platform — all observability DB-internal
  - LOW: Oracle Reports (.rdf/.rep) — 8 referenced in README; no files provided
  - LOW: PKG_NOTIFICATION body absent — NOTIFICATION_QUEUE population mechanism unknown

---

## OUTPUT 1 - Technology Stack Inventory

| Component Name | Version | Category | Layer | Package Manager / Source | Source File | Confidence |
|---|---|---|---|---|---|---|
| Oracle Database | 19c | Relational Database Engine | Data | Oracle licensing | README.md | HIGH |
| Oracle Forms | 12c (12.2.1.4) | UI Application Framework | Application | Oracle licensing | forms/xml-exports/HRMS_EMPLOYEE.xml | HIGH |
| Oracle WebLogic | 12c | Application Server | Infrastructure | Oracle licensing | README.md | HIGH — version from README only; no server config file found |
| Oracle Reports | 12c | Reporting Engine | Application | Oracle licensing | README.md | HIGH — co-versioned with Forms 12c suite |
| PL/SQL | Oracle 19c built-in | Stored Procedure Language | Application | Oracle Database | schema/tables/01_core_tables.sql | HIGH |
| DBMS_CRYPTO | Oracle 19c built-in | Cryptography Library | Security | Oracle Database | plsql/packages/PKG_SECURITY.pkb | HIGH |
| DBMS_OUTPUT | Oracle 19c built-in | Debug / Console Output | Application | Oracle Database | plsql/packages/PKG_AUDIT.pkb | HIGH |
| UTL_FILE | Oracle 19c built-in | File I/O | Application | Oracle Database | README.md | HIGH |
| UTL_MAIL | Oracle 19c built-in | SMTP Email Client | Application | Oracle Database | README.md | HIGH — referenced in README; PKG_NOTIFICATION body absent |
| UTL_RAW | Oracle 19c built-in | Raw Data Conversion | Security | Oracle Database | plsql/packages/PKG_SECURITY.pkb | HIGH |
| SYS_CONTEXT (USERENV) | Oracle 19c built-in | Session Context | Security / Observability | Oracle Database | plsql/packages/PKG_AUDIT.pkb | HIGH |
| HRMS_COMMON_LIB | N/A (PLL library) | Forms Shared Library | Application | Oracle Forms | forms/libraries/HRMS_COMMON_LIB.pll.sql | HIGH |
| HRMS_VALIDATION_LIB | N/A (PLL library) | Forms Client-side Validation Library | Application | Oracle Forms | forms/libraries/HRMS_VALIDATION_LIB.pll.sql | HIGH |
| PKG_AUDIT | HRMS app v4.2.0 | Audit Trail Package | Observability | Oracle PL/SQL | plsql/packages/PKG_AUDIT.pks | HIGH |
| PKG_COMMON | HRMS app v4.2.0 | Shared Utility Package | Application | Oracle PL/SQL | plsql/packages/PKG_COMMON.pks | HIGH |
| PKG_SECURITY | HRMS app v4.2.0 | Authentication / Session / Encryption Package | Security | Oracle PL/SQL | plsql/packages/PKG_SECURITY.pks | HIGH |
| PKG_VALIDATION | HRMS app v4.2.0 | Centralised Validation Package | Application | Oracle PL/SQL | plsql/packages/PKG_VALIDATION.pks | HIGH |
| PKG_REPORTING | HRMS app v4.2.0 | Report Generation Package | Application | Oracle PL/SQL | plsql/packages/PKG_REPORTING.pks | HIGH |
| PKG_EMPLOYEE | HRMS app v4.2.0 | Employee Business Logic Package | Application | Oracle PL/SQL | plsql/packages/PKG_EMPLOYEE.pks | LOW — spec/body not found; inferred from form calls and README |
| PKG_LEAVE | HRMS app v4.2.0 | Leave Management Package | Application | Oracle PL/SQL | plsql/packages/PKG_LEAVE.pks | LOW — spec/body not found; inferred from form calls and README |
| PKG_PAYROLL | HRMS app v4.2.0 | Payroll Calculation Package | Application | Oracle PL/SQL | plsql/packages/PKG_PAYROLL.pks | LOW — spec/body not found; inferred from form calls and README |
| PKG_PERFORMANCE | HRMS app v4.2.0 | Performance Review Package | Application | Oracle PL/SQL | plsql/packages/PKG_PERFORMANCE.pks | LOW — spec/body not found; partial body content in scan |
| PKG_NOTIFICATION | HRMS app v4.2.0 | Notification / Email Queue Package | Application | Oracle PL/SQL | plsql/packages/PKG_NOTIFICATION.pks | LOW — spec/body not found; inferred from NOTIFICATION_QUEUE table |
| PKG_INTEGRATION | HRMS app v4.2.0 | External Integration Package | Application | Oracle PL/SQL | plsql/packages/PKG_INTEGRATION.pks | LOW — spec/body not found; inferred from SYSTEM_PARAMETERS GL/BENEFITS feed status |
| HRMS Application | v4.2.0 / Build 2024.03.15 | HR Management System (monolith) | Application | — | forms/xml-exports/HRMS_MENU.xml | HIGH |

---

## OUTPUT 2 - Component & Service Map

| Service / Component Name | Type | Exposed Port(s) | Communication Protocol(s) | Primary Technology | Source File | Notes |
|---|---|---|---|---|---|---|
| Oracle Forms Application Server | Application Server | UNKNOWN — no server config found | HTTP/HTTPS (browser to WebLogic); Oracle Forms applet protocol (client to Forms server) | Oracle Forms 12c | README.md | Serves 18 Oracle Forms modules (.fmb/.fmx) to ~200 concurrent users; 3 regional offices |
| Oracle WebLogic Server | Application Server | UNKNOWN — no server config found | HTTP/HTTPS | Oracle WebLogic 12c | README.md | Hosts Oracle Forms runtime; TLS handled at this layer (LOW — no config to confirm) |
| Oracle Database 19c (HRMS schema) | Relational Database | 1521 (default Oracle listener — LOW, not declared in any config file) | Oracle Net / SQL*Net | Oracle Database 19c | schema/tables/01_core_tables.sql | Single schema HRMS; 30 DDL-defined tables, 29 sequences, 6 views; ~200 concurrent users |
| SMTP Relay | Internal Email Relay | 25 (standard SMTP — LOW, not explicitly declared) | SMTP | UTL_MAIL (Oracle built-in) | data/seed/01_reference_data.sql | Host: smtp.internal.company.com; from: hrms-noreply@company.com |

---

## OUTPUT 3 - Data Store Registry

| Store Name | Category | Engine / Technology | Version | Declared Database / Collection Name | Connected Services | Source File | Confidence |
|---|---|---|---|---|---|---|---|
| HRMS Oracle Database | Relational Database | Oracle Database | 19c | HRMS (schema) | Oracle Forms App Server, Oracle WebLogic, Oracle Reports | README.md; schema/tables/01_core_tables.sql | HIGH |
| AUDIT_LOG | Audit / Log Store (Oracle table, CLOB JSON) | Oracle Database | 19c | HRMS.AUDIT_LOG | PKG_AUDIT, PKG_COMMON, TRG_SALARY_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_DEPARTMENT_AUDIT, TRG_EMP_BEFORE_UPDATE | plsql/packages/PKG_AUDIT.pkb | HIGH — SHARED COMPONENT |
| NOTIFICATION_QUEUE | Message / Notification Queue (Oracle table) | Oracle Database | 19c | HRMS.NOTIFICATION_QUEUE | PKG_NOTIFICATION (body absent) | schema/tables/04_performance_tables.sql | HIGH — queue mechanism confirmed; PKG_NOTIFICATION population logic absent |

---

## OUTPUT 4 - Infrastructure & Deployment Blueprint

### Compute & Container Resources

| Resource Name | Resource Type | Platform / Provider | Image / Runtime Version | Environments Declared | Key Configuration (non-secret) | Source File | Confidence |
|---|---|---|---|---|---|---|---|
| Oracle WebLogic Server | Application Server | Oracle WebLogic | 12c | UNKNOWN — no deployment config found | Hosts Oracle Forms 12c runtime; ~200 concurrent users; 3 regional offices | README.md | HIGH — version from README only; no server config file |
| Oracle Database Server | Database Server | Oracle Database | 19c | UNKNOWN — no IaC found | Schema: HRMS; session timeout 30 min; fiscal year start October; audit retention 365 days; app version 4.2.0 | README.md; schema/ | HIGH — version from README |
| Oracle Forms Application Server | Application Server | Oracle Forms | 12c (12.2.1.4) | UNKNOWN | 18 form modules; 8 Oracle Reports; 12 PL/SQL packages; 2 PLL libraries | README.md; forms/ | HIGH |

**ARCHITECTURE NOTE: No infrastructure-as-code found — no Dockerfile, docker-compose, Kubernetes manifests, or Terraform/Pulumi/CloudFormation files. Deployment is manual or managed externally / in a separate repository.**

### Environments Identified

| Environment Name | Trigger / Target | Source File |
|---|---|---|
| UNKNOWN | No CI/CD pipeline files found in this repository | N/A |

### CI/CD Pipeline Inventory

| Pipeline File | Job / Stage Name | Tool Invocations | Actions Used | Runs On Condition | Source |
|---|---|---|---|---|---|
| NONE FOUND | N/A | N/A | N/A | N/A | N/A |

**ARCHITECTURE NOTE: No CI/CD pipeline files found. No .github/workflows/, Jenkinsfile, .gitlab-ci.yml, azure-pipelines.yml, or equivalent. All testing is manual via Oracle Forms (README: "No unit tests — all testing is manual via Forms").**

### Network Topology (declared configuration only — no inference)
- No ingress / load balancer declarations found
- No internal network / service mesh / DNS declarations found
- No VPC / subnet / security group declarations found
- No TLS termination point declared (WebLogic handles TLS — inferred from architecture pattern, not confirmed by config)
- 3 physical office locations: HQ New York (212-555-1000), Chicago Regional (312-555-2000), San Francisco Branch (415-555-3000)

---

## OUTPUT 5 - Integration & Dependency Graph

### External Integrations

| Integration Name | Category | Protocol / Interface | Direction | Config Key / Env Var | Source File | Confidence |
|---|---|---|---|---|---|---|
| SMTP Internal Relay | Email Provider | SMTP (UTL_MAIL) | Outbound | SYSTEM_PARAMETERS: PARAM_CODE='SMTP_HOST' value='smtp.internal.company.com'; PARAM_CODE='FROM_ADDRESS' value='hrms-noreply@company.com' | data/seed/01_reference_data.sql | HIGH |
| GL Feed (General Ledger) | ERP / Financial System Integration | UNKNOWN — PKG_INTEGRATION body absent | Outbound (inferred) | SYSTEM_PARAMETERS: PARAM_CODE='GL_FEED_STATUS' value='ACTIVE'; GL_ACCOUNT_CODE on PAY_ELEMENTS | data/seed/01_reference_data.sql | LOW — feed ACTIVE but integration mechanism, target system, and protocol entirely unknown |
| Benefits Administration Feed | Benefits Provider Integration | UNKNOWN — PKG_INTEGRATION body absent | Outbound (inferred) | SYSTEM_PARAMETERS: PARAM_CODE='BENEFITS_FEED_STATUS' value='ACTIVE' | data/seed/01_reference_data.sql | LOW — feed ACTIVE but integration mechanism entirely unknown |

### Internal Service Dependencies

| Caller | Target | Protocol | Dependency Type | Details | Source File |
|---|---|---|---|---|---|
| All Oracle Forms | PKG_SECURITY | Oracle PL/SQL call | Synchronous | is_session_valid + has_permission on every WHEN-NEW-FORM-INSTANCE | forms/xml-exports/*.xml |
| HRMS_LOGIN | PKG_SECURITY | Oracle PL/SQL call | Synchronous | authenticate(username, password, client_host) → session_id | forms/xml-exports/HRMS_LOGIN.xml |
| HRMS_EMPLOYEE | PKG_EMPLOYEE | Oracle PL/SQL call | Synchronous | generate_emp_number() in PRE-INSERT | forms/xml-exports/HRMS_EMPLOYEE.xml |
| HRMS_LEAVE | PKG_LEAVE | Oracle PL/SQL call | Synchronous | submit_leave_request, cancel_leave_request | forms/xml-exports/HRMS_LEAVE.xml |
| HRMS_PAYROLL | PKG_PAYROLL | Oracle PL/SQL call | Synchronous | create_payroll_run, calculate_payroll, approve_payroll | forms/xml-exports/HRMS_PAYROLL.xml |
| PKG_COMMON | AUDIT_LOG | SQL INSERT | Synchronous (AUTONOMOUS_TRANSACTION) | log_error, log_info | plsql/packages/PKG_COMMON.pkb |
| PKG_AUDIT | AUDIT_LOG | SQL INSERT/DELETE/SELECT | Synchronous (AUTONOMOUS_TRANSACTION) | log_action, purge_old_records, get_change_history | plsql/packages/PKG_AUDIT.pkb |
| PKG_SECURITY | DBMS_CRYPTO | Oracle built-in call | Synchronous | AES-256-CBC encrypt/decrypt SSN; MD5 hash password | plsql/packages/PKG_SECURITY.pkb |
| PKG_SECURITY | PKG_AUDIT | Oracle PL/SQL call | Synchronous | log_action called on authenticate | plsql/packages/PKG_SECURITY.pkb |
| PKG_SECURITY | PKG_EMPLOYEE | Oracle PL/SQL call | Synchronous | set_session_context(username, emp_id) called in authenticate | plsql/packages/PKG_SECURITY.pkb |
| PKG_VALIDATION | PKG_COMMON | Oracle PL/SQL call | Synchronous | validate_email_format, validate_phone_format delegate to PKG_COMMON | plsql/packages/PKG_VALIDATION.pkb |
| PKG_REPORTING | PKG_COMMON | Oracle PL/SQL call | Synchronous | log_info in refresh_reporting_tables stub | plsql/packages/PKG_REPORTING.pkb |
| All packages | PKG_COMMON | Oracle PL/SQL call | Synchronous | log_error in EXCEPTION handlers | Multiple |
| DB Triggers (6 provided) | PKG_AUDIT | Oracle PL/SQL call | Synchronous | log_action on DML events | plsql/triggers/trg_audit.sql; trg_employees.sql |

**Known circular dependency (documented in README):**
PKG_EMPLOYEE ↔ PKG_PAYROLL — circular package dependency; compilation order impact to be assessed by Agent 2.

### Build & Developer Toolchain

| Tool | Version | Purpose | Source File |
|---|---|---|---|
| Oracle Forms Builder | 12c (12.2.1.4) | Compiles .fmb → .fmx; exports .xml; packages .pll libraries | forms/xml-exports/HRMS_EMPLOYEE.xml |
| Oracle Reports Builder | 12c | Compiles .rdf → .rep report executables | README.md |
| SQL*Plus / SQL Developer | UNKNOWN | DDL execution, package deployment, seed data loading | schema/; data/seed/ (inferred from file types) |

---

## OUTPUT 6 - Security & Configuration Snapshot

### Authentication & Authorisation Mechanisms

| Mechanism Name | Type | Provider / Library | Scope | Config Key / Annotation | Source File | Confidence |
|---|---|---|---|---|---|---|
| Oracle Forms Session Authentication | Authentication | PKG_SECURITY.authenticate (custom PL/SQL) | All Forms modules | :GLOBAL.session_id (Forms global variable) | forms/xml-exports/HRMS_LOGIN.xml; plsql/packages/PKG_SECURITY.pkb | HIGH |
| Email-based username lookup | Authentication | EMPLOYEES table (UPPER(EMAIL) match) | Login only | EMPLOYMENT_STATUS='ACTIVE' filter; ROWNUM=1 for duplicate emails | plsql/packages/PKG_SECURITY.pkb | HIGH |
| MD5 Password Hashing | Authentication | DBMS_CRYPTO.HASH_MD5 | User credentials (USER_CREDENTIALS table — DDL absent) | (internal to PKG_SECURITY) | plsql/packages/PKG_SECURITY.pkb | HIGH — confirmed weakness; authenticate() is a stub that does NOT validate password |
| Grade-based Permission Model | Authorisation | PKG_SECURITY.has_permission (custom PL/SQL) | All modules, all actions | GRADE_ID from JOB_TITLES; no ROLES table | plsql/packages/PKG_SECURITY.pkb | HIGH — simplified model documented as production debt |
| Numeric Session Token | Authentication | SEQ_USER_SESSION (Oracle sequence) | All forms | :GLOBAL.session_id | plsql/packages/PKG_SECURITY.pkb | HIGH — numeric, predictable; not a GUID or JWT |
| AES-256-CBC SSN Encryption | Data Encryption | DBMS_CRYPTO.ENCRYPT_AES256 + CHAIN_CBC + PAD_PKCS5 | EMPLOYEES.SSN_ENCRYPTED, EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED | c_encryption_key (HARD-CODED RAW literal in PKG_SECURITY.pkb) | plsql/packages/PKG_SECURITY.pkb | HIGH — algorithm is strong; key management is a critical vulnerability |
| Bank Account Encryption | Data Encryption | UNKNOWN — no encrypt_bank_account function found | EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC | (not declared) | schema/tables/02_payroll_tables.sql | LOW — inferred from column name _ENC suffix only |

### Secrets & Configuration Management

| Approach | Tool / Service | Scope | Config Key / Reference | Source File | Confidence |
|---|---|---|---|---|---|
| SYSTEM_PARAMETERS table | Oracle DB table (PKG_COMMON.get_param / set_param) | Application runtime config | PARAM_GROUP + PARAM_CODE composite; EDITABLE_FLAG='Y' required for updates | data/seed/01_reference_data.sql; plsql/packages/PKG_COMMON.pkb | HIGH |
| Hard-coded encryption key in PL/SQL source | None (anti-pattern) | SSN encryption/decryption only | c_encryption_key RAW(32) literal 'HR$ystem_3ncrypt10n_K3y_2024!!' in PKG_SECURITY.pkb | plsql/packages/PKG_SECURITY.pkb | HIGH — SECRETS MANAGEMENT VULNERABILITY: key in source control |
| Oracle Forms Global Variables | Oracle Forms runtime | Session state across all forms | :GLOBAL.session_id, :GLOBAL.current_user, :GLOBAL.current_emp_id | forms/xml-exports/HRMS_LOGIN.xml | HIGH |

### Network Security Declarations

| Declaration | Type | Value (non-secret only) | Source File | Confidence |
|---|---|---|---|---|
| Session timeout | Session Security | 30 minutes (c_session_timeout_min=30 constant; SYSTEM_PARAMETERS SESSION_TIMEOUT_MIN='30'; timeout = (SYSDATE - LOGIN_TIME) * 24 * 60 > 30) | plsql/packages/PKG_SECURITY.pkb; data/seed/01_reference_data.sql | HIGH |
| Password minimum length | Password Policy | 8 characters (SYSTEM_PARAMETERS PASSWORD_MIN_LENGTH='8'; enforced in change_password error -20310) | data/seed/01_reference_data.sql; plsql/packages/PKG_SECURITY.pkb | HIGH |
| Password complexity | Password Policy | Requires [A-Z] uppercase (error -20311) AND [0-9] digit (error -20312) | plsql/packages/PKG_SECURITY.pkb | HIGH |
| TLS / CORS / HSTS | Network Security | NOT DECLARED in any application-level file | N/A | LOW — WebLogic handles TLS at server layer; no application-level declaration found |

### Compliance & Audit Flags

| Item | Type | Detail | Source File |
|---|---|---|---|
| Audit log — all DML on key tables | Audit Logging | PKG_AUDIT.log_action: TABLE_NAME, RECORD_ID, ACTION_TYPE, OLD_VALUES CLOB, NEW_VALUES CLOB, CHANGED_BY, CHANGED_DATE, IP_ADDRESS (SYS_CONTEXT), SESSION_ID (SYS_CONTEXT); PRAGMA AUTONOMOUS_TRANSACTION | plsql/packages/PKG_AUDIT.pkb |
| Audit log default retention | Data Retention | 365 days default (PKG_AUDIT.purge_old_records p_days_to_keep DEFAULT 365) | plsql/packages/PKG_AUDIT.pkb |
| Salary change audit | Audit Logging | TRG_SALARY_AUDIT: AFTER INSERT OR UPDATE OR DELETE on SALARY_RECORDS; JSON old/new salary + effective date | plsql/triggers/trg_audit.sql |
| Leave status change audit | Audit Logging | TRG_LEAVE_REQUEST_AUDIT: AFTER UPDATE OF STATUS on LEAVE_REQUESTS | plsql/triggers/trg_audit.sql |
| Employee history tracking | Audit Logging | TRG_EMP_BEFORE_UPDATE: inserts to EMPLOYEE_HISTORY on STATUS_CHANGE, DEPARTMENT_CHANGE, JOB_CHANGE | plsql/triggers/trg_employees.sql |
| SSN encryption (PII) | PII Protection | AES-256-CBC; EMPLOYEES.SSN_ENCRYPTED + EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED | schema/tables/01_core_tables.sql |
| Bank account encryption (PII) | PII Protection | EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC — mechanism inferred from column name only | schema/tables/02_payroll_tables.sql |
| EEO compliance reporting | Compliance | EMPLOYEES.GENDER (M/F/O/NULL); JOB_TITLES.EEO_CATEGORY; PKG_REPORTING.eeo_compliance_report gender distribution by EEO category | plsql/packages/PKG_REPORTING.pkb |
| FMLA eligibility | Compliance | LEAVE_TYPES: FMLA MIN_TENURE_DAYS=365, REQUIRES_APPROVAL='Y', ACCRUAL_FLAG='N' | data/seed/01_reference_data.sql |
| Soft-delete enforcement | Data Integrity | TRG_EMP_INSTEAD_OF_DELETE: blocks all direct DELETE on EMPLOYEES; -20504 error raised | plsql/triggers/trg_employees.sql |

---

## Validation Queue

| ID | Item | Chunk | Reason |
|---|---|---|---|
| VQ-01 | 12 tables missing from DDL | Chunk 1 | README states 42 tables; DDL files provide 30. Missing tables likely include RPT_* denormalized reporting tables and additional support tables. |
| VQ-02 | 9 views missing | Chunk 1 | README states 15 views; hrms_views.sql provides 6. |
| VQ-03 | ~194 triggers missing | Chunk 1 | README states 200+ triggers; 6 provided. BEFORE INSERT surrogate key triggers (SEQ.NEXTVAL pattern) are the largest expected missing category. |
| VQ-04 | USER_CREDENTIALS table absent | Chunk 1 + 3 | PKG_SECURITY.authenticate and change_password reference this table; DDL not provided. Authentication confirmed as a STUB — no actual password validation implemented. |
| VQ-05 | RPT_* denormalized tables absent | Chunk 1 | PKG_REPORTING.refresh_reporting_tables references these; DDL not provided. |
| VQ-06 | PKG_EMPLOYEE body absent | Chunk 2 | Called by HRMS_EMPLOYEE form (generate_emp_number) and PKG_SECURITY.authenticate (set_session_context). Circular dependency with PKG_PAYROLL documented in README. |
| VQ-07 | PKG_LEAVE body absent | Chunk 2 | Called by HRMS_LEAVE form. submit_leave_request and cancel_leave_request parameter signatures inferred only. |
| VQ-08 | PKG_PAYROLL body absent | Chunk 2 | Called by HRMS_PAYROLL form. create_payroll_run, calculate_payroll, approve_payroll signatures inferred only. Circular dependency with PKG_EMPLOYEE. |
| VQ-09 | PKG_NOTIFICATION body absent | Chunk 2 + 4 | NOTIFICATION_QUEUE populated by this package; EMAIL/IN_APP/SMS routing logic entirely unknown. |
| VQ-10 | PKG_INTEGRATION body absent | Chunk 2 | GL Feed and Benefits Feed are ACTIVE per SYSTEM_PARAMETERS; integration protocol, target system, and data format entirely unknown. |
| VQ-11 | Oracle Reports (.rdf/.rep) absent | Chunk 4 | README states 8 reports; no files provided. Report definitions, queries, parameters unknown. |
| VQ-12 | DISC-001: VW_LEAVE_SUMMARY.AVAILABLE omits PENDING | Chunk 1 | View: OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT (4 terms). LEAVE_BALANCES virtual column: same minus PENDING (5 terms). Different available balance results for employees with pending requests. Agent 2 to determine authoritative. |
| VQ-13 | DISC-002: Hire date future limit conflict | Chunk 2 | HRMS_EMPLOYEE form WHEN-VALIDATE-ITEM: 90 days. TRG_EMP_BEFORE_INSERT: 180 days. Error -20501 message says "180 days"; form message says "90 days". Agent 2 to determine authoritative business rule. |
| VQ-14 | DISC-003: EMPLOYEE_HISTORY column mismatch | Chunk 1 | TRG_EMP_BEFORE_UPDATE writes (HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON). DDL defines (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, etc.). Column names differ — trigger will fail at runtime with ORA error. |
| VQ-15 | Hard-coded AES-256 encryption key | Chunk 3 | c_encryption_key RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!') in PKG_SECURITY.pkb. Key is in source control — all encrypted SSNs are compromised if source is exposed. |
| VQ-16 | MD5 password hashing | Chunk 3 | DBMS_CRYPTO.HASH_MD5 used for password hashing. MD5 is cryptographically broken for this use case. |
| VQ-17 | Password validation is a stub | Chunk 3 | PKG_SECURITY.authenticate does NOT compare password to stored hash. Any password authenticates any active employee. |
| VQ-18 | No CI/CD or automated testing | Chunk 0 | No pipeline files, no test frameworks, no test scripts. README confirms all testing is manual via Oracle Forms. |
| VQ-19 | No external monitoring platform | Chunk 4 | All observability DB-internal (AUDIT_LOG table). No APM, log aggregation, or alerting tool declared. |
| VQ-20 | SEQ_EMP_NUMBER race condition | Chunk 1 | Sequence exists but PKG_EMPLOYEE.generate_emp_number uses MAX(EMP_NUMBER)+1 — race condition under concurrent inserts. Agent 2 to assess impact. |
| VQ-21 | PKG_PERFORMANCE partial content ambiguity | Chunk 2 | Procedures (create_review, submit_self_assessment, etc.) found in scan but PKG_PERFORMANCE.pks/.pkb listed as not found. Source of extracted content ambiguous. Agent 2 should re-read PKG_PERFORMANCE files directly. |
| VQ-22 | Bank account encryption mechanism unknown | Chunk 3 | EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC implies encryption but no encrypt_bank_account function found in any provided package. Agent 2 to locate implementation. |
| VQ-23 | No TLS/CORS/network security declarations | Chunk 3 + 4 | Oracle WebLogic 12c handles TLS at server layer; no application-level TLS version, cipher suite, CORS, or CSP declaration found. |

---

## Handoff Note to Agent 2

This is a legacy Oracle Forms 12c monolith — a single-schema HRMS application (Acme Corporation, ~200 concurrent users, 3 offices: New York, Chicago, San Francisco) running on Oracle Database 19c with Oracle WebLogic 12c as the application server. The codebase originates circa 2002 (upgraded from Forms 6i → 11g → 12c) with all business logic split between Oracle Forms triggers, client-side PLL libraries, and 12 server-side PL/SQL packages. There is no CI/CD, no automated testing, no containerisation, and no external observability platform.

Three areas demand immediate investigation: (1) **Security** — password validation is a confirmed stub (any password authenticates active employees), the AES-256 encryption key is hard-coded in source code, and MD5 is used for password hashing; (2) **Runtime correctness** — DISC-003 (VQ-14) identifies that TRG_EMP_BEFORE_UPDATE writes column names that do not match the EMPLOYEE_HISTORY DDL, meaning this trigger will fail at runtime for every employee update; and (3) **Missing package bodies** — PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_NOTIFICATION, and PKG_INTEGRATION are entirely absent from the scan and collectively hold the core payroll calculation, leave management, and external integration logic. The circular dependency between PKG_EMPLOYEE and PKG_PAYROLL (documented in README) also requires compilation-order analysis before any modernisation effort begins.

---
Agent 1 Scan Complete.
Agent 2 may now begin deep analysis using the 6 output files above.
Recommended starting point: Security Layer — reason: confirmed critical vulnerabilities (stub authentication, hard-coded encryption key, MD5 hashing) require immediate assessment before any other architectural judgement can be made safely.


## Agent 1 - Chunk 0 - Project-Wide Structural Scan

**Documented directory layout (per README.md):**
```
forms/xml-exports/     - 10 forms documented, 6 scanned (+1 menu-as-.mmb)
forms/libraries/       - 2 PLL shared libraries scanned
forms/menus/           - 1 menu module scanned
plsql/packages/        - 12 packages documented, 0 scanned (spec/body not provided)
plsql/triggers/         - 2 trigger files scanned
schema/tables/          - 4 table DDL files scanned
schema/views/           - 1 views DDL file scanned
schema/sequences/       - 1 sequences DDL file scanned
schema/indexes/         - referenced in README, not present in scanned set
schema/constraints/     - referenced in README, not present (constraints found inline in table DDL instead)
data/seed/              - 2 seed DML files scanned
config/                 - referenced in README, not scanned
docs/                   - referenced in README, not scanned
```

**Detected:**
- Primary language/tooling: Oracle Forms (PL/SQL-based 4GL), Oracle PL/SQL, Oracle SQL DDL/DML
- Framework/platform: Oracle Forms 12c (App Server) on Oracle WebLogic Server 12c
- Database: Oracle Database 19c (schema `HRMS`)
- Reporting: Oracle Reports (.rdf/.rep) — referenced in README only, no report files in scanned set
- Architecture style: **Monolith** (fat-client/3-tier Forms architecture: Forms Server → WebLogic → {Forms Modules, PL/SQL Packages, Oracle Reports} → single Oracle DB) — HIGH confidence (explicit architecture diagram in README)
- Deployment target: **On-prem Oracle Forms/WebLogic** per README narrative — LOW confidence for deployment specifics (no IaC/container/VM config scanned to confirm)

**Technology layers present in scanned set:**
- Application Layer — YES (Forms XML exports, PLL libraries, menu module, PL/SQL triggers)
- Data Layer — YES (table/view/sequence DDL, seed DML)
- Infrastructure Layer — **NOT FOUND** (no Dockerfile, compose, Kubernetes, Terraform, or any IaC file in scanned set)
- CI/CD Layer — **NOT FOUND** (no pipeline files of any kind in scanned set)
- Security Layer — PARTIAL (embedded as `PKG_SECURITY` calls throughout Forms triggers; package body itself unscanned)
- Observability Layer — **NOT FOUND** (no monitoring/logging/tracing config in scanned set)

**Manifest/container/IaC/CI-CD/config files located:** NONE — no `package.json`-equivalent exists for Oracle Forms/PL/SQL; there is no build manifest in this technology stack for Agent 1 to parse in full per the Reading Depth Rules.

**Estimated technology surface:** 1 deployable application tier (Oracle Forms), 1 data store (Oracle DB 19c), 6 Forms modules scanned (of 10 documented), 12 PL/SQL packages referenced but unscanned, 3 external integration flags (SMTP, GL feed, benefits feed) declared only as config rows.

**Chunk Plan (highest information density first):**
1. Application Layer (Forms XML, PLL libraries, menu module, PL/SQL triggers)
2. Data Layer (tables, views, sequences, seed data)
3. Infrastructure Layer — flagged NOT FOUND, no chunk content
4. CI/CD Layer — flagged NOT FOUND, no chunk content
5. Security Layer (cross-cutting `PKG_SECURITY`/auth touchpoints, consolidated from Chunks 1–2)
6. Observability Layer — flagged NOT FOUND, no chunk content

---

## Agent 1 - Chunk 1 of 2 - Application Layer

**Carried Forward from Prior Chunks:**
- Technology components: None yet
- Data stores: None yet
- Integrations: None yet
- LOW CONFIDENCE items: 0

---

### Forms Libraries (PLL — attached to all HRMS forms)
- `HRMS_COMMON_LIB.pll.sql` — toolbar handlers, error handling (`handle_error` → `PKG_COMMON.log_error`), session check (`check_session` → `PKG_SECURITY.is_session_valid`), date formatting, LOV refresh helper.
- `HRMS_VALIDATION_LIB.pll.sql` — client-side validators: `validate_email`, `validate_phone`, `validate_ssn`, `validate_date_not_future`, `validate_salary_range` (queries `JOB_GRADES` directly, contradicting its own header comment about a startup-cached lookup).

### Menu Module
- `HRMS_MENU.mmb.sql` — `MAIN_MENUBAR` structure; File/Edit/Query/Navigate/Modules/Admin/Help menus; module launch points to `HRMS_EMPLOYEE`, `HRMS_PAYROLL`, `HRMS_LEAVE`, `HRMS_PERFORMANCE`, `HRMS_REPORTS`, `HRMS_ADMIN` via `OPEN_FORM`.

### Forms (XML exports of .fmb)
| Form Module | Purpose | Attached Libraries | Menu | Key Package Calls |
|---|---|---|---|---|
| HRMS_LOGIN | Authentication entry point | (none) | — | `PKG_SECURITY.authenticate` |
| HRMS_MENU | MDI shell / navigation | HRMS_COMMON_LIB | MENU_MAIN | `PKG_SECURITY.has_permission`, `.logout` |
| HRMS_EMPLOYEE | Employee maintenance | HRMS_COMMON_LIB, HRMS_VALIDATION_LIB | HRMS_MENU | `PKG_SECURITY.*`, `PKG_EMPLOYEE.generate_emp_number`, `PKG_VALIDATION.validate_email_format` |
| HRMS_LEAVE | Leave request/approval | HRMS_COMMON_LIB | HRMS_MENU | `PKG_SECURITY.is_session_valid`, `PKG_LEAVE.submit_leave_request`, `.cancel_leave_request` |
| HRMS_PAYROLL | Payroll run processing | HRMS_COMMON_LIB | HRMS_MENU | `PKG_SECURITY.*`, `PKG_PAYROLL.create_payroll_run`, `.calculate_payroll`, `.approve_payroll` |
| HRMS_PERFORMANCE | Performance review cycles | HRMS_COMMON_LIB | HRMS_MENU | `PKG_SECURITY.is_session_valid` only |

**Referenced but NOT present in scanned set** (LOW confidence — flagged, not scanned):
- Forms: `HRMS_DEPARTMENT`, `HRMS_REPORTS`, `HRMS_ADMIN`, `HRMS_LOV`, `HRMS_TOOLBAR` — referenced via `OPEN_FORM` calls in HRMS_MENU.xml/.mmb.sql but not provided.
- Packages (all 12 documented in README, 0 scanned): `PKG_EMPLOYEE`, `PKG_DEPARTMENT`, `PKG_PAYROLL`, `PKG_LEAVE`, `PKG_PERFORMANCE`, `PKG_SECURITY`, `PKG_AUDIT`, `PKG_NOTIFICATION`, `PKG_REPORTING`, `PKG_COMMON`, `PKG_VALIDATION`, `PKG_INTEGRATION`.

### PL/SQL Triggers (DB layer, but grouped here as they encode application business rules)
- `trg_audit.sql`: `TRG_SALARY_AUDIT`, `TRG_LEAVE_REQUEST_AUDIT`, `TRG_DEPARTMENT_AUDIT` → all call `PKG_AUDIT.log_action` (4-arg and 6-arg call signatures observed — implies overload).
- `trg_employees.sql`: `TRG_EMP_BEFORE_INSERT`, `TRG_EMP_BEFORE_UPDATE`, `TRG_EMP_INSTEAD_OF_DELETE` (mislabeled in comment as AFTER_DELETE) — enforce hire-date window, email uniqueness among active rows, block reactivation of terminated employees, log to `EMPLOYEE_HISTORY`, and unconditionally block physical deletes.

---

### Chunk Inventory - Application Layer
- Technology components found this chunk: Oracle Forms 12c (HIGH), Oracle Forms PLL Libraries ×2 (HIGH), Oracle Forms Menu Module ×1 (HIGH), Oracle Forms Modules ×6 scanned / 4 referenced-only (HIGH/LOW), PL/SQL DB Triggers ×6 (HIGH)
- Data stores found this chunk: None directly declared here (see Chunk 2)
- Integrations found this chunk: None directly declared here (see Chunk 2 — SYSTEM_PARAMETERS)
- Infrastructure resources found: None
- Environments identified: None identified
- CI/CD tool invocations found (this chunk): N/A — no CI/CD artifacts in scanned set
- Reusable workflows followed: N/A
- Cross-layer dependencies flagged: Forms triggers → `EMPLOYEE_HISTORY` table (Data Layer, Chunk 2); Forms → `PKG_SECURITY`/`PKG_AUDIT`/etc. (unscanned Application sub-layer)
- Newly flagged as SHARED COMPONENT: `PKG_SECURITY` (called from HRMS_COMMON_LIB, HRMS_LOGIN, HRMS_MENU, HRMS_EMPLOYEE, HRMS_LEAVE, HRMS_PAYROLL, HRMS_PERFORMANCE — appears across nearly every scanned file)
- VERSION CONFLICTS detected: Hire-date future-date threshold — Forms `WHEN-VALIDATE-ITEM` in HRMS_EMPLOYEE.xml enforces 90 days vs. DB trigger `TRG_EMP_BEFORE_INSERT` enforces 180 days — flagged for Agent 2
- LOW CONFIDENCE items raised this chunk:
  - All 12 PL/SQL packages — referenced throughout but package spec/body files not in scanned set; behavior inferred only from call sites
  - 4 additional Forms modules (`HRMS_DEPARTMENT`, `HRMS_REPORTS`, `HRMS_ADMIN`, `HRMS_LOV`, `HRMS_TOOLBAR`) referenced via `OPEN_FORM`/menu bindings but not scanned
  - HRMS_LEAVE.xml, HRMS_PAYROLL.xml, HRMS_PERFORMANCE.xml each declare more tab pages / data blocks in header comments than are actually implemented in the scanned XML (stub/incomplete blocks)

---

## Agent 1 - Chunk 2 of 2 - Data Layer

**Carried Forward from Prior Chunks:**
- Technology components: Oracle Forms 12c, 2 PLL libraries, 1 menu module, 6 Forms modules, 6 DB triggers (see Chunk 1)
- Data stores: None yet
- Integrations: None yet
- LOW CONFIDENCE items: 3 categories (packages, unscanned forms, stub blocks)

---

### Sequences (`schema/sequences/hrms_sequences.sql`)
24 sequences total, all `NOCACHE` except `SEQ_AUDIT` (`CACHE 100`). Covers core (`SEQ_EMPLOYEE`, `SEQ_DEPARTMENT`, etc.), payroll, leave, performance, and system domains. `SEQ_EMP_NUMBER` flagged as possibly orphaned (see Validation Queue).

### Tables (`schema/tables/01-04_*.sql`)
29 tables scanned across 4 files: `DEPARTMENTS`, `LOCATIONS`, `JOB_GRADES`, `JOB_TITLES`, `EMPLOYEES`, `EMPLOYEE_HISTORY`, `EMPLOYEE_DEPENDENTS`, `EMERGENCY_CONTACTS`, `SALARY_RECORDS`, `PAY_ELEMENTS`, `EMPLOYEE_PAY_ELEMENTS`, `PAY_PERIODS`, `PAYROLL_RUNS`, `PAYROLL_DETAILS`, `TAX_BRACKETS`, `EMPLOYEE_TAX_INFO`, `EMPLOYEE_BANK_ACCOUNTS`, `LEAVE_TYPES`, `LEAVE_BALANCES`, `LEAVE_REQUESTS`, `LEAVE_ACCRUAL_LOG`, `HOLIDAYS`, `REVIEW_CYCLES`, `PERFORMANCE_REVIEWS`, `PERFORMANCE_GOALS`, `AUDIT_LOG`, `SYSTEM_PARAMETERS`, `NOTIFICATION_QUEUE`, `USER_SESSIONS`, `LOOKUP_VALUES` (README documents 42 tables total — 13 not in scanned set).

PII-bearing columns: `EMPLOYEES.SSN_ENCRYPTED`, `EMPLOYEES.PHOTO_BLOB`, `EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED`, `EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC`.

### Views (`schema/views/hrms_views.sql`)
6 views scanned: `VW_ACTIVE_EMPLOYEES`, `VW_ORG_HIERARCHY` (documented `CONNECT BY` performance warning >500 employees), `VW_EMPLOYEE_COMPENSATION`, `VW_LEAVE_SUMMARY`, `VW_PAYROLL_LATEST`, `VW_PENDING_APPROVALS` (README documents 15 views total — 9 not in scanned set).

### Seed Data (`data/seed/01_reference_data.sql`, `02_employee_data.sql`)
Static reference data (locations, job grades, departments, job titles, leave types, pay elements, holidays, system parameters) and 25 sample employees + salary records + department manager FK patch-up UPDATEs. Multiple column-name mismatches against the table DDL found (see Validation Queue).

### Config-as-Data: `SYSTEM_PARAMETERS` rows (only structured config source in scanned set — no `config.json`/appsettings provided)
| PARAM_GROUP.PARAM_CODE | Value | Purpose signal |
|---|---|---|
| SYSTEM.APP_VERSION | 4.2.0 | App version marker |
| SYSTEM.COMPANY_NAME | Acme Corporation | Tenant/company name |
| PAYROLL.DEFAULT_PAY_FREQUENCY | MONTHLY | Payroll config |
| PAYROLL.FISCAL_YEAR_START | 10 | Payroll config |
| SECURITY.SESSION_TIMEOUT_MIN | 30 | Session policy |
| SECURITY.PASSWORD_MIN_LENGTH | 8 | Password policy |
| NOTIFICATION.SMTP_HOST | smtp.internal.company.com | Email integration endpoint |
| NOTIFICATION.FROM_ADDRESS | hrms-noreply@company.com | Email integration sender |
| INTEGRATION.GL_FEED_STATUS | ACTIVE | External GL integration flag |
| INTEGRATION.BENEFITS_FEED_STATUS | ACTIVE | External benefits integration flag |

---

### Chunk Inventory - Data Layer
- Technology components found this chunk: Oracle Database 19c (HIGH), 24 sequences (HIGH), 29 tables (HIGH), 6 views (HIGH)
- Data stores found this chunk: Oracle Database 19c — schema `HRMS` (HIGH)
- Integrations found this chunk: SMTP mail relay (LOW — config key only), GL feed (LOW — flag only), Benefits feed (LOW — flag only)
- Infrastructure resources found: None
- Environments identified: None identified
- CI/CD tool invocations found (this chunk): N/A
- Reusable workflows followed: N/A
- Cross-layer dependencies flagged: `EMPLOYEE_HISTORY` DDL shape vs. `TRG_EMP_BEFORE_UPDATE` insert shape (Application Layer, Chunk 1) — mismatch; `AUDIT_LOG.CHK_AUDIT_ACTION` vs. `TRG_LEAVE_REQUEST_AUDIT` action value (Chunk 1) — possible constraint violation
- Newly flagged as SHARED COMPONENT: `SYSTEM_PARAMETERS` table (config source referenced conceptually by Security, Payroll, Notification, Integration domains)
- VERSION CONFLICTS detected: None additional this chunk (see Chunk 1 hire-date conflict)
- LOW CONFIDENCE items raised this chunk:
  - 13 of 42 documented tables and 9 of 15 documented views not present in scanned set
  - `schema/indexes/`, `schema/constraints/` directories referenced in README but not found as separate artifacts (constraints appear inline in table DDL instead)
  - Multiple seed-script column names do not match target table DDL (see Validation Queue) — INSERT statements as written would fail

---

## Agent 1 - Project Scan Summary
- Language(s): Oracle Forms 4GL / PL/SQL (Oracle Database 19c native) — no version conflict between DB and Forms citations
- Framework(s): Oracle Forms 12c, Oracle WebLogic Server 12c (App Server), Oracle Reports (referenced only, version undeclared)
- Architecture style: **Monolith** — HIGH confidence
- Deployment target: **On-prem Oracle Forms/WebLogic** (per README narrative) — LOW confidence (no IaC/deployment config scanned to confirm)
- Total files scanned: 14 (1 README, 2 PLL libraries, 1 menu module, 6 Forms XML, 2 trigger files, 1 sequence file, 4 table DDL files, 1 view file, 2 seed files — note: 20 listed individually above; README + 2 libraries + 1 menu + 6 forms + 2 triggers + 1 sequences + 4 tables + 1 views + 2 seed = 20 files)
- Technology layers found: 2 confirmed (Application, Data) + 1 partial (Security, embedded) — 3 layers NOT FOUND (Infrastructure, CI/CD, Observability)
- Chunks processed: 2 (Application Layer, Data Layer) + Chunk 0
- External integrations found: 3 (SMTP mail relay, GL feed, Benefits feed) — all LOW confidence, config-flag only
- Data stores identified: 1 (Oracle Database 19c, schema HRMS)
- Services / components found: 6 Forms modules scanned + 1 menu module + 2 shared libraries; 5 additional forms and 12 PL/SQL packages referenced but unscanned
- CI/CD pipeline files read: 0 (none exist in scanned set; 0 reusable workflows followed)
- CI/CD tool invocations found: None — no CI/CD artifacts present

---

## OUTPUT 1 - Technology Stack Inventory

| Component Name | Version | Category | Layer | Package Manager / Source | Source File | Confidence |
|---|---|---|---|---|---|---|
| Oracle Forms | 12c | RAD Application Framework / Runtime | Application | Oracle (proprietary, licensed) | README.md | HIGH |
| Oracle WebLogic Server | 12c | Java EE Application Server | Application/Infrastructure | Oracle (proprietary, licensed) | README.md | HIGH |
| Oracle Database | 19c | RDBMS | Data | Oracle (proprietary, licensed) | README.md, schema/tables/*.sql | HIGH |
| Oracle Reports | UNKNOWN | Reporting Engine (.rdf/.rep) | Application | Oracle (proprietary, licensed) | README.md | LOW - VERSION UNKNOWN, no report files scanned |
| PL/SQL | Oracle DB 19c native | Procedural Language | Application/Data | Bundled with Oracle DB | plsql/*, schema/*, forms/libraries/*.pll.sql | HIGH |
| HRMS_COMMON_LIB (PLL) | N/A (no version metadata in export) | Forms Shared Library | Application | Oracle Forms Builder export | forms/libraries/HRMS_COMMON_LIB.pll.sql | HIGH |
| HRMS_VALIDATION_LIB (PLL) | N/A | Forms Client-side Validation Library | Application | Oracle Forms Builder export | forms/libraries/HRMS_VALIDATION_LIB.pll.sql | HIGH |
| HRMS_MENU (Menu Module) | N/A | Forms Menu Module (.mmb) | Application | Oracle Forms Builder export | forms/menus/HRMS_MENU.mmb.sql | HIGH |
| PKG_SECURITY | UNKNOWN | Auth/Session PL/SQL Package | Security | Oracle (custom) | Referenced in all Forms + HRMS_COMMON_LIB | LOW - inferred from call sites; package body not scanned |
| PKG_COMMON | UNKNOWN | Shared Utility PL/SQL Package | Application | Oracle (custom) | Referenced in HRMS_COMMON_LIB.pll.sql | LOW - referenced only, not scanned |
| PKG_EMPLOYEE | UNKNOWN | Domain Logic PL/SQL Package | Application | Oracle (custom) | Referenced in HRMS_EMPLOYEE.xml | LOW - referenced only, not scanned |
| PKG_VALIDATION | UNKNOWN | Server-side Validation PL/SQL Package | Application | Oracle (custom) | Referenced in HRMS_EMPLOYEE.xml | LOW - referenced only, not scanned |
| PKG_LEAVE | UNKNOWN | Domain Logic PL/SQL Package | Application | Oracle (custom) | Referenced in HRMS_LEAVE.xml | LOW - referenced only, not scanned |
| PKG_PAYROLL | UNKNOWN | Domain Logic PL/SQL Package | Application | Oracle (custom) | Referenced in HRMS_PAYROLL.xml | LOW - referenced only, not scanned |
| PKG_AUDIT | UNKNOWN | Audit Logging PL/SQL Package | Security | Oracle (custom) | Referenced in plsql/triggers/trg_audit.sql | LOW - referenced only, not scanned |
| PKG_DEPARTMENT, PKG_PERFORMANCE, PKG_NOTIFICATION, PKG_REPORTING, PKG_INTEGRATION | UNKNOWN | Domain/Integration PL/SQL Packages | Application | Oracle (custom) | Listed only in README.md directory layout | LOW - listed in documentation only; no call sites found in scanned files |

---

## OUTPUT 2 - Component & Service Map

| Service / Component Name | Type | Exposed Port(s) | Communication Protocol(s) | Primary Technology | Source File | Notes |
|---|---|---|---|---|---|---|
| Oracle Forms App Server | Application Server | N/A (not declared) | Forms client protocol over HTTP(S) (per README diagram, undeclared in scanned config) | Oracle Forms 12c | README.md | LOW - architecture diagram only, no server config scanned |
| Oracle WebLogic Server | App Server / Servlet Container | N/A (not declared) | HTTP(S) | WebLogic 12c | README.md | LOW - narrative only |
| HRMS_LOGIN | Forms Module (auth entry point) | N/A | Forms client protocol | Oracle Forms 12c | forms/xml-exports/HRMS_LOGIN.xml | Documented cleartext password limitation, no lockout/2FA |
| HRMS_MENU | Forms Module (MDI shell/navigation) | N/A | Forms client protocol | Oracle Forms 12c | forms/xml-exports/HRMS_MENU.xml | Entry point after login; permission-gated menu items |
| HRMS_EMPLOYEE | Forms Module (Employee CRUD) | N/A | Forms client protocol | Oracle Forms 12c | forms/xml-exports/HRMS_EMPLOYEE.xml | Master-detail with SALARY_RECORDS |
| HRMS_LEAVE | Forms Module (Leave request/approval) | N/A | Forms client protocol | Oracle Forms 12c | forms/xml-exports/HRMS_LEAVE.xml | Stub tabs: Pending Approvals, Team Calendar not implemented |
| HRMS_PAYROLL | Forms Module (Payroll run processing) | N/A | Forms client protocol | Oracle Forms 12c | forms/xml-exports/HRMS_PAYROLL.xml | Stub tab: Pay Details not implemented |
| HRMS_PERFORMANCE | Forms Module (Performance reviews) | N/A | Forms client protocol | Oracle Forms 12c | forms/xml-exports/HRMS_PERFORMANCE.xml | Stub block: Review Detail not implemented |
| HRMS_DEPARTMENT, HRMS_REPORTS, HRMS_ADMIN, HRMS_LOV, HRMS_TOOLBAR | Forms Modules (referenced, unscanned) | N/A | Forms client protocol (assumed) | Oracle Forms 12c (assumed) | Referenced in HRMS_MENU.xml / .mmb.sql | LOW - not in scanned file set; existence unconfirmed beyond call sites |
| Oracle Database (HRMS schema) | Relational Database | N/A (not declared) | Oracle Net / SQL*Net (assumed) | Oracle Database 19c | schema/tables/*.sql | Backing store for all Forms modules |

---

## OUTPUT 3 - Data Store Registry

| Store Name | Category | Engine / Technology | Version | Declared Database / Collection Name | Connected Services (if detectable) | Source File | Confidence |
|---|---|---|---|---|---|---|---|
| HRMS Schema | Relational Database | Oracle Database | 19c | HRMS (schema name, per README) | All 6 scanned Forms modules; all PL/SQL triggers; all views | schema/tables/*.sql, schema/views/hrms_views.sql, schema/sequences/hrms_sequences.sql, data/seed/*.sql | HIGH |

**Note:** Single data store identified in scanned set (29 tables, 6 views, 24 sequences scanned; README documents 42 tables / 15 views total system-wide — 13 tables and 9 views not present in this scan and thus not itemized above). No secondary data stores (cache, queue, search engine, object storage) were found or referenced anywhere in the scanned artifacts.

---

## OUTPUT 4 - Infrastructure & Deployment Blueprint

### Compute & Container Resources
**LAYER NOT FOUND** - no Dockerfile, docker-compose, Kubernetes manifest, Terraform/Bicep/CloudFormation/CDK file, or any other IaC artifact was present in the scanned file set. The README's architecture diagram names "Oracle Forms 12c App Server" and "Oracle WebLogic 12c Server" as compute components, but no deployment configuration exists to confirm resource sizing, replica count, or provider.

### Environments Identified
| Environment Name | Trigger / Target | Source File |
|---|---|---|
| None identified | N/A | N/A |

### CI/CD Pipeline Inventory
**LAYER NOT FOUND** - no `.github/workflows/`, Jenkinsfile, `.gitlab-ci.yml`, `azure-pipelines.yml`, `.circleci/config.yml`, or `bitbucket-pipelines.yml` present in scanned set. README documents "No unit tests — manual testing only via Forms" as a self-reported known issue, consistent with the absence of any CI/CD configuration.

### Network Topology (declared configuration only - no inference)
- No ingress/load balancer declarations found
- No internal network/service mesh/DNS declarations found
- No VPC/subnet/security group declarations found
- No TLS termination point declared (HRMS_LOGIN.xml documents cleartext password transmission as a known limitation — implies no TLS termination is confirmed at the Forms applet layer)

---

## OUTPUT 5 - Integration & Dependency Graph

### External Integrations
| Integration Name | Category | Protocol / Interface | Direction | Config Key / Env Var | Source File | Confidence |
|---|---|---|---|---|---|---|
| SMTP Mail Relay | Email Provider | SMTP (assumed from key name) | Outbound | NOTIFICATION.SMTP_HOST, NOTIFICATION.FROM_ADDRESS | data/seed/01_reference_data.sql | LOW - config row only; no UTL_MAIL/UTL_SMTP call sites scanned |
| GL Feed | ERP / General Ledger Integration | UNKNOWN | Outbound (assumed) | INTEGRATION.GL_FEED_STATUS | data/seed/01_reference_data.sql | LOW - status flag only, no endpoint/protocol declared |
| Benefits Feed | Benefits Provider Integration | UNKNOWN | Outbound (assumed) | INTEGRATION.BENEFITS_FEED_STATUS | data/seed/01_reference_data.sql | LOW - status flag only, no endpoint/protocol declared |

### Internal Service Dependencies (for multi-service / microservice projects)
Not applicable — this is a monolithic Oracle Forms application backed by a single Oracle Database; no internal service-to-service network calls were found or are architecturally expected in this stack.

### Build & Developer Toolchain
**NONE FOUND** - no build tool, linter, test framework, or packaging tool configuration was present in the scanned set (consistent with README's self-reported "no unit tests" technical debt item).

---

## OUTPUT 6 - Security & Configuration Snapshot

### Authentication & Authorisation Mechanisms
| Mechanism Name | Type | Provider / Library | Scope | Config Key / Annotation | Source File | Confidence |
|---|---|---|---|---|---|---|
| PKG_SECURITY.authenticate | Authentication | Custom PL/SQL package (body unscanned) | Application (Forms login) | Called from HRMS_LOGIN.xml BTN_LOGIN | forms/xml-exports/HRMS_LOGIN.xml | LOW - call signature only, implementation unscanned |
| PKG_SECURITY.is_session_valid | Session Validation | Custom PL/SQL package (body unscanned) | All Forms | Called in WHEN-NEW-FORM-INSTANCE of every scanned form + HRMS_COMMON_LIB.check_session | Multiple (HRMS_COMMON_LIB.pll.sql, all 5 non-login forms) | HIGH - call site confirmed across 6 files |
| PKG_SECURITY.has_permission | Authorisation (RBAC-style) | Custom PL/SQL package (body unscanned) | Module/button level | Called in HRMS_MENU.xml, HRMS_EMPLOYEE.xml, HRMS_PAYROLL.xml | Multiple | HIGH - call site confirmed, uses (emp_id, module, action) signature |
| PKG_SECURITY.logout | Session Termination | Custom PL/SQL package (body unscanned) | Application | Called from HRMS_MENU.xml BTN_LOGOUT / MI_LOGOUT | forms/xml-exports/HRMS_MENU.xml | HIGH - call site confirmed |

### Secrets & Configuration Management
| Approach | Tool / Service | Scope | Config Key / Reference | Source File | Confidence |
|---|---|---|---|---|---|
| Database-table-based configuration | HRMS.SYSTEM_PARAMETERS (custom, no external secrets manager) | Application (Payroll, Security, Notification, Integration domains) | PARAM_GROUP/PARAM_CODE/PARAM_VALUE rows | schema/tables/04_performance_tables.sql, data/seed/01_reference_data.sql | HIGH |
| Column-level encryption (custom) | Referenced as "AES-256 ... decrypted only in PKG_SECURITY" (comment only) | Data (PII columns) | EMPLOYEES.SSN_ENCRYPTED, EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED, EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC | schema/tables/01_core_tables.sql, schema/tables/02_payroll_tables.sql | LOW - encryption mechanism asserted in a column comment only; decrypt logic in unscanned PKG_SECURITY body |

### Network Security Declarations
| Declaration | Type | Value (non-secret only) | Source File | Confidence |
|---|---|---|---|---|
| Password field transmitted in cleartext (documented limitation) | TLS/Transport | "Password field transmitted in cleartext (Forms applet limitation)" | forms/xml-exports/HRMS_LOGIN.xml (header comment) | HIGH - explicitly documented |
| No account lockout after failed attempts (documented limitation) | Auth Hardening | Not implemented | forms/xml-exports/HRMS_LOGIN.xml (header comment) | HIGH - explicitly documented |
| No CAPTCHA / 2FA support (documented limitation) | Auth Hardening | Not implemented | forms/xml-exports/HRMS_LOGIN.xml (header comment) | HIGH - explicitly documented |

### Compliance & Audit Flags
| Item | Type | Detail | Source File |
|---|---|---|---|
| AUDIT_LOG table + PKG_AUDIT.log_action + 3 audit triggers | Audit Logging | Salary changes, leave status changes, and department changes are logged via `TRG_SALARY_AUDIT`, `TRG_LEAVE_REQUEST_AUDIT`, `TRG_DEPARTMENT_AUDIT` → `PKG_AUDIT.log_action`; granularity of captured old/new values varies by table | plsql/triggers/trg_audit.sql, schema/tables/04_performance_tables.sql |
| PII fields present on master tables | PII / Data Privacy | SSN (encrypted), date of birth, home address, bank account (encrypted), phone numbers stored directly on EMPLOYEES / EMPLOYEE_DEPENDENTS / EMPLOYEE_BANK_ACCOUNTS | schema/tables/01_core_tables.sql, schema/tables/02_payroll_tables.sql |
| EMPLOYEE_HISTORY compliance trail | Audit / Data Retention | Table exists to record status/department/job change history, but is fed by a trigger whose insert column list and CHECK-constraint values do not match the table's actual DDL (see Validation Queue) — compliance trail is at risk of silently failing or throwing at runtime | schema/tables/01_core_tables.sql, plsql/triggers/trg_employees.sql |

---

## Validation Queue

| # | Item | Chunk | Reason |
|---|---|---|---|
| 1 | Oracle Reports version unknown | 0 | Referenced in README only, no .rdf/.rep files scanned |
| 2 | Hire-date future-date threshold conflict: 90 days (Forms WHEN-VALIDATE-ITEM, HRMS_EMPLOYEE.xml) vs. 180 days (DB trigger TRG_EMP_BEFORE_INSERT, trg_employees.sql) | 1 | Business-rule drift between UI and DB validation layers |
| 3 | `TRG_EMP_BEFORE_UPDATE` inserts into `EMPLOYEE_HISTORY` using columns (`HISTORY_ID`, `CHANGE_DATE`, `OLD_VALUE`, `NEW_VALUE`, `CHANGED_BY`, `CHANGE_REASON`) that do not exist on the table (actual: `HIST_ID`, `EFFECTIVE_DATE`, typed old/new columns, `CREATED_BY`, `REASON_CODE`, `COMMENTS`) | 1/2 | Cross-file schema mismatch — this INSERT would fail as documented |
| 4 | Same trigger uses `CHANGE_TYPE` values `'DEPARTMENT_CHANGE'`/`'JOB_CHANGE'`, neither present in `CHK_CHANGE_TYPE`'s allowed list on `EMPLOYEE_HISTORY` | 1/2 | CHECK constraint violation risk |
| 5 | `TRG_LEAVE_REQUEST_AUDIT` passes `'STATUS_CHANGE'` as the action value into `PKG_AUDIT.log_action`; `AUDIT_LOG.CHK_AUDIT_ACTION` only allows INSERT/UPDATE/DELETE | 1/2 | Possible CHECK constraint violation (inferred — `PKG_AUDIT` body unscanned, mapping assumed) |
| 6 | Seed script inserts `LOCATIONS.PHONE`; DDL column is `PHONE_NUMBER` | 2 | Seed/DDL column-name mismatch |
| 7 | Seed script inserts `JOB_GRADES.GRADE_NAME`/`GRADE_LEVEL`, omits required `GRADE_CODE`; DDL has no `GRADE_LEVEL` column | 2 | Seed/DDL column-name mismatch, missing NOT NULL column |
| 8 | Seed script inserts `SYSTEM_PARAMETERS.DESCRIPTION`; DDL column is `PARAM_DESCRIPTION`; `DATA_TYPE` also omitted | 2 | Seed/DDL column-name mismatch |
| 9 | No FK constraints on `DEPARTMENTS.PARENT_DEPT_ID`, `MANAGER_EMP_ID`, `LOCATION_CODE` despite conceptual relationships (inconsistent with `EMPLOYEES`, which does declare equivalent FKs) | 2 | Inconsistent referential-integrity enforcement |
| 10 | No FK on `HOLIDAYS.LOCATION_CODE`, `NOTIFICATION_QUEUE.RECIPIENT_EMP_ID`, `LEAVE_ACCRUAL_LOG.RUN_ID`, `LOOKUP_VALUES.PARENT_LOOKUP_ID` | 2 | Same pattern — undeclared conceptual FKs |
| 11 | No unique constraint on `EMPLOYEES.EMAIL`; uniqueness enforced only by `TRG_EMP_BEFORE_INSERT` and only among `ACTIVE_FLAG='Y'` rows | 1/2 | Terminated employees' emails can be reused without conflict |
| 12 | `LEAVE_BALANCES.AVAILABLE` (virtual column) subtracts `PENDING`; `VW_LEAVE_SUMMARY.AVAILABLE` (hand-rolled) omits `PENDING` | 2 | Formula divergence between table and view when PENDING != 0 |
| 13 | `VW_EMPLOYEE_COMPENSATION` joins `SALARY_RECORDS` on `ACTIVE_FLAG='Y'` only, without the `EFFECTIVE_DATE`/`END_DATE` scoping used by `VW_ACTIVE_EMPLOYEES` | 2 | Possible duplicate rows or premature inclusion of not-yet-effective salary |
| 14 | `VW_PAYROLL_LATEST` defines "latest" as global `MAX(RUN_ID)` among APPROVED runs | 2 | May not generalize to multiple parallel/off-cycle payroll runs |
| 15 | `SEQ_EMP_NUMBER` may be orphaned/unused if `PKG_EMPLOYEE.generate_emp_number` uses `MAX()+1` logic instead (per README/comment; package body unscanned) | 1/2 | Documented concurrency/race-condition risk, not independently verifiable |
| 16 | `EMPLOYEES.EMP_ID` has no DEFAULT/sequence tie at the DB level; relies on Forms `PRE-INSERT` trigger | 1/2 | Non-Forms inserts (batch, ad hoc SQL) would require EMP_ID supplied explicitly |
| 17 | `TRG_EMP_INSTEAD_OF_DELETE` unconditionally blocks all physical deletes on EMPLOYEES; comment mislabels it as an AFTER_DELETE trigger | 1 | Documented UX/maintenance trap — any real DELETE against EMPLOYEES fails |
| 18 | Client-side `HRMS_VALIDATION_LIB.validate_email` vs. server-side `PKG_VALIDATION.validate_email_format` are independently maintained, differently named functions | 1 | Documented validation-drift risk between Forms library and DB package |
| 19 | `HRMS_VALIDATION_LIB.validate_salary_range` header comment claims cached local data; code performs a direct `SELECT` against `JOB_GRADES` | 1 | Comment/code mismatch |
| 20 | HRMS_LEAVE.xml, HRMS_PAYROLL.xml, HRMS_PERFORMANCE.xml header comments each reference more data blocks/tab pages than are actually implemented | 1 | Stub/incomplete forms relative to their own documentation |
| 21 | HRMS_PERFORMANCE.xml `GOAL_CATEGORY` poplist offers only 3 of the 5 values allowed by `CHK_GOAL_CATEGORY` (missing INNOVATION, COMPLIANCE) | 1/2 | UI cannot set values the DB permits |
| 22 | HRMS_PAYROLL.xml `BTN_CREATE_RUN`/`BTN_CALCULATE` have no explicit permission check beyond form-level VIEW gate, while `BTN_APPROVE` requires explicit PAYROLL/APPROVE permission | 1 | Inconsistent depth of authorization within the same form |
| 23 | HRMS_PERFORMANCE.xml has no module-level `has_permission` check and no edit-specific authorization gate on ratings/assessments | 1 | Any authenticated user can open and edit; weaker gating than Payroll/Employee forms |
| 24 | HRMS_MENU.xml button path (Payroll/Reports) has disabled-state + runtime permission check; menu-bar path relies only on disabled-state property | 1 | Differing depth of defense between two access paths to the same forms |
| 25 | All 12 documented PL/SQL packages referenced across forms/triggers/libraries have no spec/body files in the scanned set | 1 | Package internals (business logic, error handling, calculations) are entirely unverified |
| 26 | 5 Forms referenced via `OPEN_FORM`/menu bindings (`HRMS_DEPARTMENT`, `HRMS_REPORTS`, `HRMS_ADMIN`, `HRMS_LOV`, `HRMS_TOOLBAR`) not present in scanned set | 1 | Existence and implementation unconfirmed |
| 27 | ARCHITECTURE NOTE: No infrastructure-as-code, container, or CI/CD artifacts found anywhere in the scanned set | 0 | Deployment configuration may be manual, externally managed, or in a separate repository |
| 28 | ARCHITECTURE NOTE: `config/` and `docs/` directories referenced in README's documented layout were not included in the scanned file set | 0 | Unknown additional configuration/documentation may exist outside this scan |
| 29 | Seed script `02_employee_data.sql` issues two consecutive `UPDATE DEPARTMENTS ... WHERE DEPT_ID=30` statements (setting `MANAGER_EMP_ID` to 3, then to 30) | 2 | First UPDATE is dead/no-op |
| 30 | HRMS_EMPLOYEE.xml `KEY-EXIT` trigger appears to invoke `SHOW_ALERT('ALT_CONFIRM_EXIT')` in both an IF and its ELSIF condition expression | 1 | Possible duplicate alert/dialog behavior |
| 31 | `ALT_CONFIRM_DELETE` alert is defined in HRMS_EMPLOYEE.xml but no trigger in the scanned file invokes it | 1 | Possibly dead alert, or invoked from unscanned code |

---

## Handoff Note to Agent 2

This is a **monolithic Oracle Forms 12c / PL/SQL / Oracle Database 19c** HR system (no microservices, no containers, no cloud infrastructure, no CI/CD — all three of those layers are confirmed absent from the scanned set, not merely unscanned). The primary language/framework is Oracle Forms backed by Oracle DB 19c; the only data store is the single `HRMS` schema (29 tables / 6 views scanned of 42/15 documented). No CI/CD tool invocations exist because no pipeline files were found, consistent with the README's self-reported absence of automated testing. The Validation Queue is unusually dense with **concrete, verifiable cross-file defects** (not just documentation gaps) — most notably a trigger (`TRG_EMP_BEFORE_UPDATE`) whose INSERT into `EMPLOYEE_HISTORY` uses column names and CHECK-constraint values that do not exist on that table, three seed-script/DDL column-name mismatches, an hire-date business-rule conflict between Forms and DB validation layers, and a formula divergence between a virtual column and its corresponding view. All 12 PL/SQL packages that carry the actual business logic (`PKG_EMPLOYEE`, `PKG_PAYROLL`, `PKG_SECURITY`, etc.) are referenced pervasively but were not included in this scan — Agent 2 should treat every finding that depends on package internals as inferred, not confirmed, and should flag package unavailability as a standing analysis constraint.

---
Agent 1 Scan Complete.
Agent 2 may now begin deep analysis using the 6 output files above.
Recommended starting point: **Data Layer** — reason: highest concentration of concrete, cross-file structural defects (schema/trigger column-shape mismatches, CHECK constraint violations, seed/DDL mismatches, missing FK enforcement) that carry direct data-integrity risk and should be triaged before Application-layer business-rule drift or the (absent) Infrastructure/CI-CD/Observability layers.
