=== CHUNK METADATA ===
Chunk: 17            (chunk count is budget-driven, not a fixed file count)
Type group: schema
Expected files (2):
  1. [schema] ts-plsql-oracle-forms-hrms-main/schema/tables/04_performance_tables.sql (10817 chars written)
  2. [schema] ts-plsql-oracle-forms-hrms-main/schema/views/hrms_views.sql (6835 chars written)
Total source content: 15911 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/04_performance_tables.sql ===

**IDENTITY:**
  KIND: schema script (DDL)
  PURPOSE: creates HRMS performance-management, audit, configuration, notification, session-tracking, and generic lookup tables

**STRUCTURES:**
  REVIEW_CYCLES — KIND: table; TYPE: N/A
  **REVIEW_CYCLES columns:**
  CYCLE_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (PK)
  CYCLE_NAME — KIND: column; TYPE: VARCHAR2(100) NOT NULL
  CYCLE_YEAR — KIND: column; TYPE: NUMBER(4) NOT NULL
  START_DATE — KIND: column; TYPE: DATE NOT NULL
  END_DATE — KIND: column; TYPE: DATE NOT NULL
  SELF_REVIEW_DUE — KIND: column; TYPE: DATE
  MANAGER_REVIEW_DUE — KIND: column; TYPE: DATE
  CALIBRATION_DUE — KIND: column; TYPE: DATE
  STATUS — KIND: column; TYPE: VARCHAR2(20) DEFAULT 'DRAFT'
  CREATED_BY — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  CREATED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL
  MODIFIED_BY — KIND: column; TYPE: VARCHAR2(30)
  MODIFIED_DATE — KIND: column; TYPE: DATE

  PERFORMANCE_REVIEWS — KIND: table; TYPE: N/A
  **PERFORMANCE_REVIEWS columns:**
  REVIEW_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (PK)
  CYCLE_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (FK -> REVIEW_CYCLES.CYCLE_ID)
  EMP_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (FK -> EMPLOYEES.EMP_ID)
  REVIEWER_EMP_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (FK -> EMPLOYEES.EMP_ID)
  REVIEW_TYPE — KIND: column; TYPE: VARCHAR2(20) DEFAULT 'ANNUAL'
  STATUS — KIND: column; TYPE: VARCHAR2(20) DEFAULT 'NOT_STARTED'
  OVERALL_RATING — KIND: column; TYPE: NUMBER(2,1)
  RATING_LABEL — KIND: column; TYPE: VARCHAR2(50)
  SELF_ASSESSMENT — KIND: column; TYPE: CLOB
  MANAGER_ASSESSMENT — KIND: column; TYPE: CLOB
  STRENGTHS — KIND: column; TYPE: CLOB
  AREAS_FOR_IMPROVEMENT — KIND: column; TYPE: CLOB
  DEVELOPMENT_PLAN — KIND: column; TYPE: CLOB
  EMPLOYEE_COMMENTS — KIND: column; TYPE: CLOB
  EMPLOYEE_ACK_DATE — KIND: column; TYPE: DATE
  CALIBRATED_RATING — KIND: column; TYPE: NUMBER(2,1)
  CALIBRATION_NOTES — KIND: column; TYPE: VARCHAR2(4000)
  CREATED_BY — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  CREATED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL
  MODIFIED_BY — KIND: column; TYPE: VARCHAR2(30)
  MODIFIED_DATE — KIND: column; TYPE: DATE

  PERFORMANCE_GOALS — KIND: table; TYPE: N/A
  **PERFORMANCE_GOALS columns:**
  GOAL_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (PK)
  REVIEW_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (FK -> PERFORMANCE_REVIEWS.REVIEW_ID)
  EMP_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (FK -> EMPLOYEES.EMP_ID)
  GOAL_TITLE — KIND: column; TYPE: VARCHAR2(200) NOT NULL
  GOAL_DESCRIPTION — KIND: column; TYPE: CLOB
  GOAL_CATEGORY — KIND: column; TYPE: VARCHAR2(30)
  WEIGHT_PCT — KIND: column; TYPE: NUMBER(5,2) DEFAULT 0
  TARGET_DATE — KIND: column; TYPE: DATE
  STATUS — KIND: column; TYPE: VARCHAR2(20) DEFAULT 'NOT_STARTED'
  PROGRESS_PCT — KIND: column; TYPE: NUMBER(5,2) DEFAULT 0
  SELF_RATING — KIND: column; TYPE: NUMBER(2,1)
  MANAGER_RATING — KIND: column; TYPE: NUMBER(2,1)
  COMMENTS — KIND: column; TYPE: CLOB
  CREATED_BY — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  CREATED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL
  MODIFIED_BY — KIND: column; TYPE: VARCHAR2(30)
  MODIFIED_DATE — KIND: column; TYPE: DATE

  AUDIT_LOG — KIND: table; TYPE: N/A
  **AUDIT_LOG columns:**
  AUDIT_ID — KIND: column; TYPE: NUMBER(15) NOT NULL (PK)
  TABLE_NAME — KIND: column; TYPE: VARCHAR2(60) NOT NULL
  RECORD_ID — KIND: column; TYPE: NUMBER(15) NOT NULL
  ACTION_TYPE — KIND: column; TYPE: VARCHAR2(10) NOT NULL
  OLD_VALUES — KIND: column; TYPE: CLOB
  NEW_VALUES — KIND: column; TYPE: CLOB
  CHANGED_BY — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  CHANGED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL
  IP_ADDRESS — KIND: column; TYPE: VARCHAR2(50)
  SESSION_ID — KIND: column; TYPE: VARCHAR2(100)

  SYSTEM_PARAMETERS — KIND: table; TYPE: N/A
  **SYSTEM_PARAMETERS columns:**
  PARAM_ID — KIND: column; TYPE: NUMBER(5) NOT NULL (PK)
  PARAM_GROUP — KIND: column; TYPE: VARCHAR2(50) NOT NULL
  PARAM_CODE — KIND: column; TYPE: VARCHAR2(50) NOT NULL
  PARAM_VALUE — KIND: column; TYPE: VARCHAR2(4000) NOT NULL
  PARAM_DESCRIPTION — KIND: column; TYPE: VARCHAR2(200)
  DATA_TYPE — KIND: column; TYPE: VARCHAR2(20) DEFAULT 'VARCHAR2'
  EDITABLE_FLAG — KIND: column; TYPE: CHAR(1) DEFAULT 'Y'
  CREATED_BY — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  CREATED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL
  MODIFIED_BY — KIND: column; TYPE: VARCHAR2(30)
  MODIFIED_DATE — KIND: column; TYPE: DATE

  NOTIFICATION_QUEUE — KIND: table; TYPE: N/A
  **NOTIFICATION_QUEUE columns:**
  NOTIFICATION_ID — KIND: column; TYPE: NUMBER(15) NOT NULL (PK)
  RECIPIENT_EMP_ID — KIND: column; TYPE: NUMBER(10)
  RECIPIENT_EMAIL — KIND: column; TYPE: VARCHAR2(100)
  NOTIFICATION_TYPE — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  SUBJECT — KIND: column; TYPE: VARCHAR2(200) NOT NULL
  BODY — KIND: column; TYPE: CLOB NOT NULL
  STATUS — KIND: column; TYPE: VARCHAR2(20) DEFAULT 'PENDING'
  PRIORITY — KIND: column; TYPE: NUMBER(2) DEFAULT 5
  SENT_DATE — KIND: column; TYPE: DATE
  ERROR_MESSAGE — KIND: column; TYPE: VARCHAR2(4000)
  RETRY_COUNT — KIND: column; TYPE: NUMBER(3) DEFAULT 0
  REFERENCE_TABLE — KIND: column; TYPE: VARCHAR2(60)
  REFERENCE_ID — KIND: column; TYPE: NUMBER(15)
  CREATED_BY — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  CREATED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL

  USER_SESSIONS — KIND: table; TYPE: N/A
  **USER_SESSIONS columns:**
  SESSION_ID — KIND: column; TYPE: NUMBER(15) NOT NULL (PK)
  EMP_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (FK -> EMPLOYEES.EMP_ID)
  USERNAME — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  LOGIN_TIME — KIND: column; TYPE: DATE NOT NULL
  LOGOUT_TIME — KIND: column; TYPE: DATE
  IP_ADDRESS — KIND: column; TYPE: VARCHAR2(50)
  FORMS_MODULE — KIND: column; TYPE: VARCHAR2(100)
  SESSION_STATUS — KIND: column; TYPE: VARCHAR2(20) DEFAULT 'ACTIVE'
  CREATED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL

  LOOKUP_VALUES — KIND: table; TYPE: N/A
  **LOOKUP_VALUES columns:**
  LOOKUP_ID — KIND: column; TYPE: NUMBER(10) NOT NULL (PK)
  LOOKUP_TYPE — KIND: column; TYPE: VARCHAR2(50) NOT NULL
  LOOKUP_CODE — KIND: column; TYPE: VARCHAR2(50) NOT NULL
  LOOKUP_VALUE — KIND: column; TYPE: VARCHAR2(200) NOT NULL
  DISPLAY_ORDER — KIND: column; TYPE: NUMBER(5) DEFAULT 0
  PARENT_LOOKUP_ID — KIND: column; TYPE: NUMBER(10)
  ACTIVE_FLAG — KIND: column; TYPE: CHAR(1) DEFAULT 'Y' NOT NULL
  CREATED_BY — KIND: column; TYPE: VARCHAR2(30) NOT NULL
  CREATED_DATE — KIND: column; TYPE: DATE DEFAULT SYSDATE NOT NULL

**METHODS:**
  **FILE-LEVEL EFFECT** [SOURCE: L1-182]
  - What it does: Runs as a schema-migration/DDL script. Creates 8 tables in the HRMS schema: REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS, AUDIT_LOG, SYSTEM_PARAMETERS, NOTIFICATION_QUEUE, USER_SESSIONS, LOOKUP_VALUES, with their primary keys, foreign keys, unique constraints, and CHECK constraints as declared.
  - Business rules: REVIEW_CYCLES.STATUS must be one of DRAFT, OPEN, IN_PROGRESS, CALIBRATION, CLOSED [L25]. PERFORMANCE_REVIEWS.STATUS must be one of NOT_STARTED, SELF_REVIEW, MANAGER_REVIEW, MEETING_SCHEDULED, COMPLETED, ACKNOWLEDGED [L57]; OVERALL_RATING must be between 1.0 and 5.0 inclusive [L58]. PERFORMANCE_GOALS.STATUS must be one of NOT_STARTED, IN_PROGRESS, COMPLETED, DEFERRED, CANCELLED [L85]; GOAL_CATEGORY must be one of BUSINESS, DEVELOPMENT, LEADERSHIP, INNOVATION, COMPLIANCE [L86]. AUDIT_LOG.ACTION_TYPE must be one of INSERT, UPDATE, DELETE [L104]. SYSTEM_PARAMETERS enforces uniqueness of (PARAM_GROUP, PARAM_CODE) [L123]. NOTIFICATION_QUEUE.STATUS must be one of PENDING, SENT, FAILED, CANCELLED [L146]; NOTIFICATION_TYPE must be one of EMAIL, IN_APP, SMS [L147]. LOOKUP_VALUES enforces uniqueness of (LOOKUP_TYPE, LOOKUP_CODE) [L181].
  - Numbers & thresholds: Column precision/size limits — REVIEW_CYCLES: CYCLE_ID NUMBER(10), CYCLE_NAME VARCHAR2(100), CYCLE_YEAR NUMBER(4). PERFORMANCE_REVIEWS: REVIEW_ID/CYCLE_ID/EMP_ID/REVIEWER_EMP_ID NUMBER(10), OVERALL_RATING/CALIBRATED_RATING NUMBER(2,1) with CHECK range 1.0–5.0, RATING_LABEL VARCHAR2(50), CALIBRATION_NOTES VARCHAR2(4000). PERFORMANCE_GOALS: GOAL_TITLE VARCHAR2(200), WEIGHT_PCT/PROGRESS_PCT NUMBER(5,2) default 0, SELF_RATING/MANAGER_RATING NUMBER(2,1). AUDIT_LOG: AUDIT_ID/RECORD_ID NUMBER(15), TABLE_NAME VARCHAR2(60), SESSION_ID VARCHAR2(100). SYSTEM_PARAMETERS: PARAM_ID NUMBER(5), PARAM_VALUE VARCHAR2(4000), default DATA_TYPE = 'VARCHAR2', default EDITABLE_FLAG = 'Y'. NOTIFICATION_QUEUE: NOTIFICATION_ID NUMBER(15), PRIORITY NUMBER(2) default 5, RETRY_COUNT NUMBER(3) default 0, BODY CLOB NOT NULL, default STATUS='PENDING'. USER_SESSIONS: SESSION_ID NUMBER(15), default SESSION_STATUS='ACTIVE'. LOOKUP_VALUES: DISPLAY_ORDER NUMBER(5) default 0, default ACTIVE_FLAG='Y'. All CREATED_DATE/CHANGED_DATE columns default to SYSDATE.
  - Security & error handling: No grants/roles defined in this file. Data integrity enforced only via NOT NULL, CHECK, UNIQUE and FK constraints listed above; any INSERT/UPDATE violating them is rejected by the database with a constraint-violation error (ORA-02290/ORA-00001/etc.) — no application-level handling present here.
  - Data in/out: Output — 8 new tables and their constraints created in the HRMS schema. No data rows are inserted by this file.

**DEPENDENCIES:**
  Data touched:
  - Reads: HRMS.EMPLOYEES — referenced by FK constraints FK_PR_EMP, FK_PR_REVIEWER, FK_PG_EMP, FK_US_EMP for referential validation
  - Reads: HRMS.REVIEW_CYCLES — referenced by FK_PR_CYCLE (within this same file)
  - Reads: HRMS.PERFORMANCE_REVIEWS — referenced by FK_PG_REVIEW (within this same file)
  - Writes: HRMS.REVIEW_CYCLES — table created
  - Writes: HRMS.PERFORMANCE_REVIEWS — table created
  - Writes: HRMS.PERFORMANCE_GOALS — table created
  - Writes: HRMS.AUDIT_LOG — table created
  - Writes: HRMS.SYSTEM_PARAMETERS — table created
  - Writes: HRMS.NOTIFICATION_QUEUE — table created
  - Writes: HRMS.USER_SESSIONS — table created
  - Writes: HRMS.LOOKUP_VALUES — table created

  Config/env: None
  External integrations: None

**GAPS:**
  UNKNOWN: NOTIFICATION_QUEUE.RECIPIENT_EMP_ID has no FK constraint to EMPLOYEES despite its naming, unlike other EMP_ID columns in this file — unclear if intentional (to allow notifications to non-employee recipients) or an oversight.
  UNRESOLVED: LOOKUP_VALUES.PARENT_LOOKUP_ID appears intended as a self-referencing hierarchy pointer but no FK constraint is declared for it.
  NOT_ANALYZED: Sequences, indexes (beyond PK/UK), and grants for these tables are not present in this file and are presumably defined elsewhere.
  EXTERNAL: The logic that actually populates AUDIT_LOG (e.g., triggers or a logging package) is not in this file.

*[pipeline status — type: schema · pass: original · attempt: 1 · coverage: 100% (numbers 11/11 · tables 1/1 · units 1/1 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/views/hrms_views.sql ===

**IDENTITY:**
  KIND: schema script (view definitions)
  PURPOSE: Creates reporting/lookup views over the HRMS schema for use by Oracle Reports (.rdf), Forms LOVs, and external reporting tools.

**STRUCTURES:**
  HRMS.VW_ACTIVE_EMPLOYEES — KIND: view; TYPE: N/A
  HRMS.VW_ORG_HIERARCHY — KIND: view; TYPE: N/A
  HRMS.VW_EMPLOYEE_COMPENSATION — KIND: view; TYPE: N/A
  HRMS.VW_LEAVE_SUMMARY — KIND: view; TYPE: N/A
  HRMS.VW_PAYROLL_LATEST — KIND: view; TYPE: N/A
  HRMS.VW_PENDING_APPROVALS — KIND: view; TYPE: N/A

**METHODS:**
  **FILE-LEVEL EFFECT** [SOURCE: L1-159]
  - What it does: Runs six `CREATE OR REPLACE VIEW` statements in HRMS schema, no procedural logic. (1) VW_ACTIVE_EMPLOYEES [L10-40] joins EMPLOYEES to DEPARTMENTS, JOB_TITLES, JOB_GRADES, a self-join to EMPLOYEES for the manager's name, LOCATIONS, and the employee's active SALARY_RECORDS row, computing full name via concatenation and tenure in years via `TRUNC(MONTHS_BETWEEN(SYSDATE, HIRE_DATE)/12, 1)`; filtered to EMPLOYMENT_STATUS='ACTIVE' and ACTIVE_FLAG='Y'. A COMMENT ON TABLE documents it as "Denormalized view of active employees with department, job, manager, location, and salary" [L39-40]. (2) VW_ORG_HIERARCHY [L47-57] walks the manager/report tree on EMPLOYEES using `START WITH MANAGER_EMP_ID IS NULL CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID`, filtered to EMPLOYMENT_STATUS='ACTIVE', producing ORG_LEVEL via `LEVEL`, an indented path string via `SYS_CONNECT_BY_PATH`, and a leaf flag via `CONNECT_BY_ISLEAF`, ordered siblings by LAST_NAME. A comment warns performance degrades significantly above 500 employees [L45]. (3) VW_EMPLOYEE_COMPENSATION [L63-80] joins EMPLOYEES to DEPARTMENTS, JOB_TITLES, JOB_GRADES, and the active SALARY_RECORDS row, computing GRADE_MIDPOINT as `(MIN_SALARY+MAX_SALARY)/2` and COMPA_RATIO as `ROUND(BASE_SALARY / GRADE_MIDPOINT * 100, 1)`; filtered to EMPLOYMENT_STATUS='ACTIVE'. (4) VW_LEAVE_SUMMARY [L86-103] joins LEAVE_BALANCES to EMPLOYEES, DEPARTMENTS, and LEAVE_TYPES, computing AVAILABLE as `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT` and UTILIZATION_PCT as `ROUND(USED*100/NULLIF(OPENING_BALANCE+ACCRUED,0), 1)`; filtered to CALENDAR_YEAR = current-year (`EXTRACT(YEAR FROM SYSDATE)`) and EMPLOYMENT_STATUS='ACTIVE'. (5) VW_PAYROLL_LATEST [L109-129] joins PAYROLL_DETAILS to EMPLOYEES, PAYROLL_RUNS, and PAY_PERIODS, restricted to the single latest APPROVED run via a `MAX(RUN_ID)` correlated subquery on PAYROLL_RUNS filtered to STATUS='APPROVED', excludes detail rows with STATUS='ERROR', and aggregates per employee/period: GROSS_PAY = SUM of amounts where ELEMENT_TYPE='EARNING', TOTAL_TAXES = SUM of ABS(amount) where ELEMENT_TYPE='TAX', TOTAL_DEDUCTIONS = SUM of ABS(amount) where ELEMENT_TYPE IN ('DEDUCTION','BENEFIT'), NET_PAY = SUM of all amounts. (6) VW_PENDING_APPROVALS [L135-159] is a UNION ALL of two branches tagged by a literal APPROVAL_TYPE: 'LEAVE' rows from LEAVE_REQUESTS (joined to EMPLOYEES and LEAVE_TYPES) filtered to STATUS='PENDING', with DETAILS built as `<TOTAL_DAYS> day(s) <MM/DD START>-<MM/DD END>`; and 'PERFORMANCE' rows from PERFORMANCE_REVIEWS (joined to EMPLOYEES and REVIEW_CYCLES) filtered to STATUS='MANAGER_REVIEW', with ITEM_DESCRIPTION built as `'Performance Review - ' || CYCLE_NAME`.
  - Business rules: VW_ACTIVE_EMPLOYEES only includes employees with EMPLOYMENT_STATUS='ACTIVE' and ACTIVE_FLAG='Y', and only attaches a salary row that is ACTIVE_FLAG='Y', EFFECTIVE_DATE<=SYSDATE, and (END_DATE IS NULL OR END_DATE>SYSDATE) [L32-35]. VW_ORG_HIERARCHY only includes EMPLOYMENT_STATUS='ACTIVE' employees and roots the hierarchy at employees with no manager (MANAGER_EMP_ID IS NULL) [L54-56]. VW_EMPLOYEE_COMPENSATION only includes EMPLOYMENT_STATUS='ACTIVE' employees and only their ACTIVE_FLAG='Y' salary record [L79-80]. VW_LEAVE_SUMMARY is scoped to the current calendar year and EMPLOYMENT_STATUS='ACTIVE' employees [L102-103]. VW_PAYROLL_LATEST is scoped to only the most recent APPROVED payroll run and excludes ERROR-status detail lines [L121-126]. VW_PENDING_APPROVALS surfaces only LEAVE_REQUESTS with STATUS='PENDING' and PERFORMANCE_REVIEWS with STATUS='MANAGER_REVIEW' [L147, L159].
  - Numbers & thresholds: Tenure calculation divides months-between by 12 and truncates to 1 decimal place [L15]. Documented performance-degradation threshold for VW_ORG_HIERARCHY: ">500 employees" [L45] (a comment/warning, not an enforced limit). COMPA_RATIO = `BASE_SALARY / ((MIN_SALARY+MAX_SALARY)/2) * 100`, rounded to 1 decimal [L71]. UTILIZATION_PCT = `USED * 100 / (OPENING_BALANCE + ACCRUED)`, rounded to 1 decimal, with divide-by-zero guarded via NULLIF [L97]. Latest payroll run selection uses `MAX(RUN_ID)` among STATUS='APPROVED' runs [L121-125].
  - Security & error handling: None — no grants, access checks, or exception handling in the file; it is pure DDL.
  - Data in/out: Input — existing rows in EMPLOYEES, DEPARTMENTS, JOB_TITLES, JOB_GRADES, LOCATIONS, SALARY_RECORDS, LEAVE_BALANCES, LEAVE_TYPES, LEAVE_REQUESTS, PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS, PERFORMANCE_REVIEWS, REVIEW_CYCLES. Output — (re)creates the six views listed under STRUCTURES as schema objects in HRMS; VW_ACTIVE_EMPLOYEES additionally gets a table-level COMMENT [L39-40].

**DEPENDENCIES:**
  Data touched:
  - Reads: EMPLOYEES — employee identity, status, hire date, manager link
  - Reads: DEPARTMENTS — department name/code/cost center
  - Reads: JOB_TITLES — job title/code, links to JOB_GRADES
  - Reads: JOB_GRADES — grade name and MIN_SALARY/MAX_SALARY band
  - Reads: LOCATIONS — location name/city/state/country
  - Reads: SALARY_RECORDS — current active salary, currency, pay frequency, change history
  - Reads: LEAVE_BALANCES — opening balance, accrued, used, adjustment, pending, calendar year
  - Reads: LEAVE_TYPES — leave type name
  - Reads: LEAVE_REQUESTS — pending leave request details (dates, days, status)
  - Reads: PAYROLL_DETAILS — per-employee payroll line items (element type, amount, status)
  - Reads: PAYROLL_RUNS — run status, used to find latest APPROVED run
  - Reads: PAY_PERIODS — period name
  - Reads: PERFORMANCE_REVIEWS — review status, dates, reviewer
  - Reads: REVIEW_CYCLES — cycle name
  - Writes: None (no DML; creates view definitions VW_ACTIVE_EMPLOYEES, VW_ORG_HIERARCHY, VW_EMPLOYEE_COMPENSATION, VW_LEAVE_SUMMARY, VW_PAYROLL_LATEST, VW_PENDING_APPROVALS as schema objects)

  Config/env: None
  External integrations: None (header comment states these views are consumed by Oracle Reports .rdf files, Forms LOVs, and external reporting tools [L2-3], but this file does not itself call out to them)

**GAPS:**
  UNKNOWN which specific Oracle Reports (.rdf) or Forms LOVs consume each view — only the general statement in the header comment [L2-3] is available; NOT_ANALYZED without those report/form files in scope.

*[pipeline status — type: schema · pass: correction · attempt: 2 · coverage: 100% (numbers 3/3 · tables 0/0 · units 1/1 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 2
Files delivered: 2
  Full coverage on first pass: 1
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/schema/views/hrms_views.sql
  Still incomplete after max attempts: 0
Raw source: 15911 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===