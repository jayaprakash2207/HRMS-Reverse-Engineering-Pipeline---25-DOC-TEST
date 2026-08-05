# 08 — Entity Relationship Diagram
**System:** Acme Corporation HRMS (Oracle 19c)
**Version:** 1.0 — Derived from DA Track schema-catalogue, BA Deep Analyst, and AA Quality Review
**Scope:** 30 confirmed DDL tables; 7 inferred RPT_* reporting tables noted separately; 2 implied integration staging tables noted where relevant
**Confidence:** High for structural relationships (FK-enforced); Medium for business-rule relationships (enforced only in PL/SQL); Low for inferred tables (no DDL recovered)

---

## 1. Master ERD — All 30 Tables

```mermaid
erDiagram

    %% ── REFERENCE / LOOKUP ──────────────────────────────────────────────────
    LOOKUP_VALUES {
        number(10)   LOOKUP_ID PK
        varchar2(50) LOOKUP_TYPE
        varchar2(50) LOOKUP_CODE
        varchar2(200) LOOKUP_DESCRIPTION
        number(3)    DISPLAY_ORDER
        char(1)      ACTIVE_FLAG
    }

    TERMINATION_CODES {
        varchar2(10)  CODE PK
        varchar2(100) DESCRIPTION
        varchar2(20)  CATEGORY
        char(1)       ACTIVE_FLAG
    }

    SYSTEM_PARAMETERS {
        varchar2(50)  PARAM_NAME PK
        varchar2(200) PARAM_VALUE
        varchar2(50)  PARAM_GROUP
        varchar2(200) DESCRIPTION
        varchar2(30)  MODIFIED_BY
        date          MODIFIED_DATE
    }

    SYSTEM_CONFIG {
        number(10)    CONFIG_ID PK
        varchar2(50)  CONFIG_KEY
        varchar2(500) CONFIG_VALUE
        varchar2(100) DESCRIPTION
        varchar2(30)  MODIFIED_BY
        date          MODIFIED_DATE
    }

    %% ── ORGANISATIONAL CORE ─────────────────────────────────────────────────
    JOB_GRADES {
        number(10)    GRADE_ID PK
        number(2)     GRADE_LEVEL
        varchar2(50)  GRADE_NAME
        number(12,2)  MIN_SALARY
        number(12,2)  MID_SALARY
        number(12,2)  MAX_SALARY
        char(1)       ACTIVE_FLAG
    }

    DEPARTMENTS {
        number(10)    DEPARTMENT_ID PK
        varchar2(100) DEPARTMENT_NAME
        varchar2(20)  DEPARTMENT_CODE
        number(10)    PARENT_DEPARTMENT_ID FK
        number(10)    MANAGER_ID FK
        varchar2(20)  COST_CENTER
        char(1)       ACTIVE_FLAG
        date          CREATED_DATE
    }

    JOB_POSITIONS {
        number(10)    POSITION_ID PK
        varchar2(100) POSITION_TITLE
        varchar2(20)  POSITION_CODE
        number(2)     MIN_GRADE
        number(2)     MAX_GRADE
        number(10)    DEPARTMENT_ID FK
        char(1)       ACTIVE_FLAG
    }

    EMPLOYEES {
        number(10)    EMPLOYEE_ID PK
        varchar2(20)  EMPLOYEE_NUMBER
        varchar2(50)  FIRST_NAME
        varchar2(50)  LAST_NAME
        varchar2(50)  MIDDLE_NAME
        date          DATE_OF_BIRTH
        varchar2(500) SSN_ENCRYPTED
        varchar2(100) EMAIL
        varchar2(20)  PHONE
        varchar2(200) ADDRESS_LINE1
        varchar2(200) ADDRESS_LINE2
        varchar2(100) CITY
        varchar2(2)   STATE
        varchar2(10)  ZIP_CODE
        date          HIRE_DATE
        date          TERMINATION_DATE
        varchar2(20)  EMPLOYMENT_STATUS
        varchar2(100) JOB_TITLE
        number(10)    DEPARTMENT_ID FK
        number(10)    MANAGER_ID FK
        number(2)     GRADE
        varchar2(500) BANK_ACCOUNT_NUMBER
        varchar2(500) BANK_ROUTING_NUMBER
        varchar2(20)  MARITAL_STATUS
        varchar2(30)  TAX_FILING_STATUS
        varchar2(100) EMERGENCY_CONTACT_NAME
        varchar2(20)  EMERGENCY_CONTACT_PHONE
        varchar2(10)  TERMINATION_REASON FK
        char(1)       ACTIVE_FLAG
        date          CREATED_DATE
        date          UPDATED_DATE
        varchar2(50)  UPDATED_BY
    }

    EMPLOYEE_HISTORY {
        number(10)    HISTORY_ID PK
        number(10)    EMPLOYEE_ID FK
        varchar2(50)  CHANGE_TYPE
        varchar2(200) OLD_VALUE
        varchar2(200) NEW_VALUE
        date          CHANGE_DATE
        varchar2(50)  CHANGED_BY
    }

    %% ── COMPENSATION ────────────────────────────────────────────────────────
    SALARY_RECORDS {
        number(10)    SALARY_ID PK
        number(10)    EMPLOYEE_ID FK
        number(12,2)  BASE_SALARY
        date          EFFECTIVE_DATE
        date          END_DATE
        varchar2(20)  SALARY_TYPE
        varchar2(200) CHANGE_REASON
        number(10)    APPROVED_BY FK
        date          CREATED_DATE
    }

    EMPLOYEE_PAY_ELEMENTS {
        number(10)    ELEMENT_ID PK
        varchar2(100) ELEMENT_NAME
        varchar2(20)  ELEMENT_TYPE
        varchar2(20)  GL_ACCOUNT_CODE
        char(1)       ACTIVE_FLAG
    }

    PAYROLL_RUNS {
        number(10)    RUN_ID PK
        varchar2(100) RUN_NAME
        date          PAY_PERIOD_START
        date          PAY_PERIOD_END
        date          RUN_DATE
        varchar2(20)  STATUS
        number(15,2)  TOTAL_GROSS
        number(15,2)  TOTAL_NET
        number(15,2)  TOTAL_DEDUCTIONS
        date          CALCULATED_DATE
        number(10)    APPROVED_BY FK
        date          APPROVED_DATE
    }

    PAYROLL_DETAILS {
        number(10)    DETAIL_ID PK
        number(10)    RUN_ID FK
        number(10)    EMPLOYEE_ID FK
        number(10)    ELEMENT_ID FK
        number(12,2)  AMOUNT
        varchar2(20)  STATUS
        varchar2(200) ERROR_MESSAGE
    }

    DEDUCTION_RECORDS {
        number(10)    DEDUCTION_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    RUN_ID FK
        varchar2(50)  DEDUCTION_TYPE
        number(12,2)  AMOUNT
        date          EFFECTIVE_DATE
        varchar2(200) NOTES
    }

    EMPLOYEE_BANK_ACCOUNTS {
        number(10)    BANK_ACCT_ID PK
        number(10)    EMP_ID FK
        varchar2(100) BANK_NAME
        varchar2(20)  ROUTING_NUMBER
        varchar2(200) ACCOUNT_NUMBER_ENC
        varchar2(20)  ACCOUNT_TYPE
        varchar2(20)  DEPOSIT_TYPE
        number(12,2)  DEPOSIT_AMOUNT
        number(5,2)   DEPOSIT_PERCENTAGE
        number(2)     PRIORITY_ORDER
        char(1)       PRENOTE_SENT
        date          PRENOTE_DATE
        char(1)       ACTIVE_FLAG
        varchar2(30)  CREATED_BY
        date          CREATED_DATE
        varchar2(30)  MODIFIED_BY
        date          MODIFIED_DATE
    }

    %% ── LEAVE ────────────────────────────────────────────────────────────────
    LEAVE_TYPES {
        number(10)    LEAVE_TYPE_ID PK
        varchar2(50)  LEAVE_TYPE_NAME
        varchar2(20)  LEAVE_CODE
        number(5,2)   ANNUAL_ENTITLEMENT
        number(5,2)   ACCRUAL_RATE
        char(1)       REQUIRES_DOCUMENT
        char(1)       ACTIVE_FLAG
    }

    LEAVE_BALANCES {
        number(10)    BALANCE_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    LEAVE_TYPE_ID FK
        number(5,2)   OPENING_BALANCE
        number(5,2)   ACCRUED
        number(5,2)   TAKEN
        number(5,2)   PENDING
        number(4)     CALENDAR_YEAR
        date          LAST_ACCRUAL_DATE
    }

    LEAVE_REQUESTS {
        number(10)    REQUEST_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    LEAVE_TYPE_ID FK
        date          START_DATE
        date          END_DATE
        number(5,2)   DAYS_REQUESTED
        varchar2(20)  STATUS
        varchar2(500) REASON
        varchar2(500) SUPPORTING_DOC_PATH
        number(10)    APPROVED_BY FK
        date          APPROVED_DATE
        date          CREATED_DATE
        varchar2(30)  CREATED_BY
    }

    %% ── PERFORMANCE ─────────────────────────────────────────────────────────
    REVIEW_CYCLES {
        number(10)    CYCLE_ID PK
        varchar2(100) CYCLE_NAME
        date          START_DATE
        date          END_DATE
        varchar2(20)  STATUS
        varchar2(30)  CREATED_BY
        date          CREATED_DATE
    }

    PERFORMANCE_REVIEWS {
        number(10)    REVIEW_ID PK
        number(10)    CYCLE_ID FK
        number(10)    EMPLOYEE_ID FK
        number(10)    REVIEWER_EMP_ID FK
        varchar2(30)  REVIEW_TYPE
        number(3,1)   OVERALL_RATING
        varchar2(20)  RATING_LABEL
        number(3,1)   CALIBRATED_RATING
        clob          CALIBRATION_NOTES
        clob          SELF_ASSESSMENT
        clob          MANAGER_ASSESSMENT
        clob          STRENGTHS
        clob          AREAS_FOR_IMPROVEMENT
        clob          DEVELOPMENT_PLAN
        clob          EMPLOYEE_COMMENTS
        date          EMPLOYEE_ACK_DATE
        varchar2(20)  STATUS
        varchar2(30)  CREATED_BY
        date          CREATED_DATE
        varchar2(30)  MODIFIED_BY
        date          MODIFIED_DATE
    }

    PERFORMANCE_GOALS {
        number(10)    GOAL_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    CYCLE_ID FK
        varchar2(200) GOAL_TITLE
        clob          GOAL_DESCRIPTION
        date          TARGET_DATE
        varchar2(20)  STATUS
        number(3,1)   PROGRESS_PCT
        varchar2(30)  CREATED_BY
        date          CREATED_DATE
    }

    GOAL_REVIEWS {
        number(10)    GOAL_REVIEW_ID PK
        number(10)    GOAL_ID FK
        number(10)    REVIEW_ID FK
        number(3,1)   ACHIEVEMENT_RATING
        clob          COMMENTS
        date          REVIEWED_DATE
        varchar2(30)  REVIEWED_BY
    }

    %% ── BENEFITS ─────────────────────────────────────────────────────────────
    BENEFIT_PLANS {
        number(10)    PLAN_ID PK
        varchar2(100) PLAN_NAME
        varchar2(50)  PLAN_TYPE
        date          EFFECTIVE_DATE
        date          END_DATE
        number(10,2)  EMPLOYER_CONTRIBUTION
        char(1)       ACTIVE_FLAG
    }

    BENEFIT_ENROLLMENTS {
        number(10)    ENROLLMENT_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    PLAN_ID FK
        date          ENROLLMENT_DATE
        date          END_DATE
        varchar2(20)  STATUS
        number(10,2)  EMPLOYEE_CONTRIBUTION
        varchar2(30)  CREATED_BY
        date          CREATED_DATE
    }

    EMPLOYEE_DEPENDENTS {
        number(10)    DEPENDENT_ID PK
        number(10)    EMP_ID FK
        varchar2(50)  FIRST_NAME
        varchar2(50)  LAST_NAME
        varchar2(20)  RELATIONSHIP
        date          DATE_OF_BIRTH
        varchar2(200) SSN_ENCRYPTED
        char(1)       BENEFITS_ENROLLED
        char(1)       ACTIVE_FLAG
        varchar2(30)  CREATED_BY
        date          CREATED_DATE
        varchar2(30)  MODIFIED_BY
        date          MODIFIED_DATE
    }

    %% ── SECURITY & AUDIT ────────────────────────────────────────────────────
    USER_CREDENTIALS {
        number(10)    EMP_ID PK_FK
        varchar2(200) PASSWORD_HASH
        date          CREATED_DATE
        date          MODIFIED_DATE
    }

    USER_SESSIONS {
        varchar2(36)  SESSION_ID PK
        number(10)    EMP_ID FK
        date          LOGIN_TIME
        date          LAST_ACTIVITY
        varchar2(20)  STATUS
        varchar2(50)  IP_ADDRESS
    }

    AUDIT_LOG {
        number(10)    LOG_ID PK
        varchar2(50)  LOG_TYPE
        varchar2(50)  TABLE_NAME
        number(10)    RECORD_ID
        varchar2(50)  ACTION
        clob          OLD_VALUES
        clob          NEW_VALUES
        varchar2(50)  PERFORMED_BY
        date          LOG_DATE
        varchar2(50)  SESSION_ID
    }

    %% ── NOTIFICATIONS ────────────────────────────────────────────────────────
    NOTIFICATION_TEMPLATES {
        number(10)    TEMPLATE_ID PK
        varchar2(50)  TEMPLATE_CODE
        varchar2(100) SUBJECT
        clob          BODY_TEMPLATE
        varchar2(20)  CHANNEL
        char(1)       ACTIVE_FLAG
    }

    NOTIFICATION_QUEUE {
        number(10)    NOTIFICATION_ID PK
        number(10)    RECIPIENT_ID FK
        varchar2(20)  CHANNEL
        varchar2(200) SUBJECT
        clob          BODY
        varchar2(20)  STATUS
        number(3)     RETRY_COUNT
        date          CREATED_DATE
        date          SENT_DATE
        varchar2(500) ERROR_MESSAGE
    }

    %% ── RELATIONSHIPS ────────────────────────────────────────────────────────

    EMPLOYEES ||--o{ EMPLOYEES               : "manages (self-ref)"
    DEPARTMENTS ||--o{ DEPARTMENTS            : "parent department (self-ref)"
    EMPLOYEES }o--|| DEPARTMENTS             : "belongs to"
    EMPLOYEES }o--|| TERMINATION_CODES       : "terminated with"
    DEPARTMENTS }o--|| EMPLOYEES             : "managed by"
    JOB_POSITIONS }o--|| DEPARTMENTS         : "belongs to"
    JOB_POSITIONS }o--|| JOB_GRADES          : "grade band (soft)"

    EMPLOYEES ||--o{ EMPLOYEE_HISTORY        : "has history"
    EMPLOYEES ||--o{ SALARY_RECORDS          : "has salary history"
    EMPLOYEES ||--o{ PAYROLL_DETAILS         : "paid in"
    EMPLOYEES ||--o{ DEDUCTION_RECORDS       : "has deductions"
    EMPLOYEES ||--o{ EMPLOYEE_BANK_ACCOUNTS  : "has bank accounts"

    PAYROLL_RUNS ||--o{ PAYROLL_DETAILS      : "contains"
    PAYROLL_RUNS ||--o{ DEDUCTION_RECORDS    : "contains"
    EMPLOYEE_PAY_ELEMENTS ||--o{ PAYROLL_DETAILS : "used in"

    EMPLOYEES ||--o{ LEAVE_BALANCES          : "has balances"
    LEAVE_TYPES ||--o{ LEAVE_BALANCES        : "type of"
    EMPLOYEES ||--o{ LEAVE_REQUESTS          : "submits"
    LEAVE_TYPES ||--o{ LEAVE_REQUESTS        : "type of"

    REVIEW_CYCLES ||--o{ PERFORMANCE_REVIEWS : "contains"
    EMPLOYEES ||--o{ PERFORMANCE_REVIEWS     : "is reviewed in"
    EMPLOYEES ||--o{ PERFORMANCE_REVIEWS     : "reviews as manager"
    EMPLOYEES ||--o{ PERFORMANCE_GOALS       : "owns"
    REVIEW_CYCLES ||--o{ PERFORMANCE_GOALS   : "scoped to"
    PERFORMANCE_GOALS ||--o{ GOAL_REVIEWS    : "assessed in"
    PERFORMANCE_REVIEWS ||--o{ GOAL_REVIEWS  : "part of"

    EMPLOYEES ||--o{ BENEFIT_ENROLLMENTS     : "enrolled in"
    BENEFIT_PLANS ||--o{ BENEFIT_ENROLLMENTS : "enrolls via"
    EMPLOYEES ||--o{ EMPLOYEE_DEPENDENTS     : "has dependents"

    EMPLOYEES ||--|{ USER_CREDENTIALS        : "authenticated by"
    EMPLOYEES ||--o{ USER_SESSIONS           : "has sessions"

    EMPLOYEES ||--o{ NOTIFICATION_QUEUE      : "receives"
```

---

## 2. ERD Narrative — Entity Descriptions and Key Relationships

### 2.1 Employee Identity Cluster

**EMPLOYEES** is the aggregate root of the entire system. Every domain object in HRMS references an employee either directly via `EMPLOYEE_ID` (FK) or indirectly through a dependent table. The entity carries 33 columns including soft-delete (`ACTIVE_FLAG`), three-part active filter (`HIRE_DATE`, `TERMINATION_DATE`, `EMPLOYMENT_STATUS`), AES-256-encrypted PII (`SSN_ENCRYPTED`), and the critical `GRADE` column that drives RBAC across all packages.

The self-referential `MANAGER_ID` FK enables an unbounded reporting hierarchy. PL/SQL uses Oracle `CONNECT BY` to traverse it, with known performance degradation beyond 500 employees.

**DEPARTMENTS** is a second self-referential tree (via `PARENT_DEPARTMENT_ID`) enabling multi-level cost-centre hierarchies. DEPARTMENTS and EMPLOYEES share a bidirectional dependency: employees belong to departments, and departments are managed by employees. This creates a shared-kernel pattern between BC-01 (Employee Identity) and BC-07 (Organisational Structure).

**JOB_POSITIONS** acts as the job catalogue, defining permissible grade ranges (`MIN_GRADE`, `MAX_GRADE`) for each position. The relationship to JOB_GRADES is enforced in PL/SQL only — there is no DDL FK. This is a referential integrity gap (see section 5).

**JOB_GRADES** provides the salary band definitions (`MIN_SALARY`, `MID_SALARY`, `MAX_SALARY`) used by the compensation and reporting modules. The `compa_ratio` calculation in `PKG_REPORTING.compensation_summary` divides current salary by `MID_SALARY` to produce a market-position index.

**TERMINATION_CODES** is a reference table for coded termination reasons (`VOLUNTARY`, `INVOLUNTARY`, etc.) linked to `EMPLOYEES.TERMINATION_REASON` via FK. It is populated via seed data in `01_reference_data.sql`.

**EMPLOYEE_HISTORY** provides a full audit trail of attribute changes to employee records. It is written by the trigger on the EMPLOYEES table (or by PKG_EMPLOYEE procedures) and captures old/new values per change event.

**LOOKUP_VALUES** is the generic key-value store for enumerated values not deserving their own table (e.g. gender codes, marital status values, notification channel codes). It underpins several check-constraint equivalents enforced only at the application layer.

---

### 2.2 Compensation Cluster

**SALARY_RECORDS** implements point-in-time salary history. The current salary for an employee is the row where `END_DATE IS NULL`. When a salary changes, the old row is closed (`END_DATE = new effective date - 1`) and a new row is inserted. `SALARY_TYPE` drives the payroll calculation branch: MONTHLY divides annual by 12, HOURLY uses a different formula, and CONTRACT uses yet another path.

**EMPLOYEE_PAY_ELEMENTS** is the reference catalogue for pay components (base salary, overtime, bonus, federal tax, state tax, benefits deduction, etc.). Each element carries a `GL_ACCOUNT_CODE` for the Oracle Financials feed. The undocumented numeric coding scheme (5100-series for earnings, 2100/2200 for liabilities) is currently maintained only by convention with no DDL constraint.

**PAYROLL_RUNS** is the header record for each payroll cycle. Its `STATUS` column implements the payroll lifecycle: `DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED`. No `PAID` status exists despite `EMPLOYEE_BANK_ACCOUNTS` implying direct deposit capability — this is a critical functional gap.

**PAYROLL_DETAILS** holds one row per employee per pay element per run. It is the most granular compensation record and is the source for the GL journal feed and payslip notifications.

**DEDUCTION_RECORDS** stores voluntary and statutory deductions (health insurance, 401k, garnishments) outside the pay element structure. The relationship to PAYROLL_RUNS allows deduction totals to reconcile against `PAYROLL_RUNS.TOTAL_DEDUCTIONS`.

**EMPLOYEE_BANK_ACCOUNTS** stores direct deposit configuration supporting split-deposit across multiple accounts via four `DEPOSIT_TYPE` values: `FULL`, `PARTIAL_AMOUNT`, `PARTIAL_PERCENT`, and `REMAINDER`. Despite the table's complete schema design, no PL/SQL procedure in the recovered codebase reads this table during payroll disbursement — direct deposit is non-functional.

---

### 2.3 Leave Cluster

**LEAVE_TYPES** is the master configuration for each type of leave (Annual, Sick, FMLA, Parental, Bereavement, etc.). The `REQUIRES_DOCUMENT` flag controls whether a supporting document path is mandatory on submission. Notably, FMLA's `REQUIRES_DOCUMENT` is seeded as `'N'` in the reference data, which contradicts federal compliance requirements (a configuration-risk finding).

**LEAVE_BALANCES** stores per-employee, per-leave-type, per-calendar-year accrual state. The formula `AVAILABLE = OPENING_BALANCE + ACCRUED - TAKEN - PENDING` is enforced in PL/SQL but not as a computed column in DDL. A defect exists in `PKG_LEAVE.run_monthly_accrual`: the retry path uses assignment (`SET ACCRUED = v_accrued`) rather than increment (`SET ACCRUED = ACCRUED + v_accrued`), which silently resets balances on concurrent accrual retries.

**LEAVE_REQUESTS** records individual leave applications. The `STATUS` lifecycle is `PENDING → APPROVED / REJECTED / CANCELLED`. The `SUPPORTING_DOC_PATH` column stores a file system path, which is vulnerable to path traversal if not sanitised on input (TD-47).

---

### 2.4 Performance Cluster

**REVIEW_CYCLES** defines the boundaries of each performance review period (annual, mid-year, quarterly). It is the parent record for all review activity within that period.

**PERFORMANCE_REVIEWS** is the central record for a single review of a single employee within a cycle. It carries both `OVERALL_RATING` (the raw manager-submitted rating, 1.0–5.0 with auto-populated `RATING_LABEL`) and `CALIBRATED_RATING` (the adjusted post-calibration rating). The critical gap: no PL/SQL procedure writes to `CALIBRATED_RATING` or `CALIBRATION_NOTES`, and the reporting procedure `get_rating_distribution` aggregates on `OVERALL_RATING` — meaning all published distributions reflect uncalibrated ratings.

**PERFORMANCE_GOALS** stores SMART goals for each employee within a cycle. Goals are linked to review cycles for scope and to employees for ownership.

**GOAL_REVIEWS** is the intersection entity linking individual goals to performance reviews, carrying a per-goal achievement rating and comments. This enables granular goal-by-goal assessment within the broader review.

---

### 2.5 Benefits Cluster

**BENEFIT_PLANS** defines available benefit offerings (medical, dental, vision, life, 401k, etc.) with effective date ranges and employer contribution amounts.

**BENEFIT_ENROLLMENTS** is the many-to-many resolution between employees and benefit plans. Each enrollment row records the employee's contribution, enrollment date, and end date. The ADP benefits feed (203-character fixed-width) reads from EMPLOYEES joined to BENEFIT_ENROLLMENTS joined to EMPLOYEE_DEPENDENTS via `PKG_INTEGRATION.export_benefits_feed`.

**EMPLOYEE_DEPENDENTS** stores family member data for benefits coverage. The `RELATIONSHIP` column is constrained to five values. Critically, the `BENEFITS_ENROLLED` flag (`'Y'`/`'N'`, default `'N'`) is collected but never read by the benefits export — all active dependents are exported regardless of enrollment status, risking incorrect ADP data.

---

### 2.6 Security Cluster

**USER_CREDENTIALS** stores the password hash for each employee. The hash uses MD5 via `DBMS_CRYPTO.HASH_MD5`, which is cryptographically broken and unsuitable for password storage. The authentication procedure (`PKG_SECURITY.authenticate`) does not query this table — any valid username authenticates regardless of password. This is a critical security defect.

**USER_SESSIONS** tracks active login sessions with a 30-minute timeout checked lazily (only on the next `is_session_valid` call). Sessions opened before a termination event remain valid for up to 30 minutes after the employee is terminated. No background cleanup job sweeps stale sessions.

**AUDIT_LOG** is the single shared table for all logging: DML audit trails, application errors, and informational messages. The absence of log-type partitioning means a single purge policy applies to all log categories — DML audit trails and operational INFO messages are deleted together.

**SYSTEM_CONFIG** and **SYSTEM_PARAMETERS** are separate configuration stores used by different packages. `SYSTEM_PARAMETERS` uses a `PARAM_GROUP` column for namespacing (e.g. `INTEGRATION`, `PAYROLL`). The session timeout is stored in `SYSTEM_PARAMETERS` but is ignored by `PKG_SECURITY`, which hard-codes 30 minutes.

---

### 2.7 Notifications Cluster

**NOTIFICATION_TEMPLATES** stores reusable message templates with subject lines and body content. Templates are identified by `TEMPLATE_CODE` and associated with a delivery channel (`EMAIL`, `SMS`, `IN_APP`).

**NOTIFICATION_QUEUE** is the dispatch queue for all outbound messages. Records are inserted with `STATUS = 'PENDING'` and processed by `PKG_NOTIFICATION`. The SMS handler (`send_via_sms`) logs a stub message and does nothing. The `RETRY_COUNT` column supports at-least-once delivery for email, capped at a configurable maximum.

---

## 3. Core Entity Cluster Diagrams

### 3.1 Employee Core Cluster

```mermaid
erDiagram
    JOB_GRADES {
        number(10)   GRADE_ID PK
        number(2)    GRADE_LEVEL
        varchar2(50) GRADE_NAME
        number(12,2) MIN_SALARY
        number(12,2) MID_SALARY
        number(12,2) MAX_SALARY
    }

    DEPARTMENTS {
        number(10)    DEPARTMENT_ID PK
        varchar2(100) DEPARTMENT_NAME
        varchar2(20)  DEPARTMENT_CODE
        number(10)    PARENT_DEPARTMENT_ID FK
        number(10)    MANAGER_ID FK
        varchar2(20)  COST_CENTER
        char(1)       ACTIVE_FLAG
    }

    JOB_POSITIONS {
        number(10)    POSITION_ID PK
        varchar2(100) POSITION_TITLE
        varchar2(20)  POSITION_CODE
        number(2)     MIN_GRADE
        number(2)     MAX_GRADE
        number(10)    DEPARTMENT_ID FK
        char(1)       ACTIVE_FLAG
    }

    EMPLOYEES {
        number(10)   EMPLOYEE_ID PK
        varchar2(20) EMPLOYEE_NUMBER
        varchar2(50) FIRST_NAME
        varchar2(50) LAST_NAME
        date         HIRE_DATE
        date         TERMINATION_DATE
        varchar2(20) EMPLOYMENT_STATUS
        number(10)   DEPARTMENT_ID FK
        number(10)   MANAGER_ID FK
        number(2)    GRADE
        char(1)      ACTIVE_FLAG
    }

    EMPLOYEE_HISTORY {
        number(10)    HISTORY_ID PK
        number(10)    EMPLOYEE_ID FK
        varchar2(50)  CHANGE_TYPE
        varchar2(200) OLD_VALUE
        varchar2(200) NEW_VALUE
        date          CHANGE_DATE
        varchar2(50)  CHANGED_BY
    }

    EMPLOYEES ||--o{ EMPLOYEES          : "manager (self-ref)"
    DEPARTMENTS ||--o{ DEPARTMENTS      : "parent dept (self-ref)"
    EMPLOYEES }o--|| DEPARTMENTS        : "assigned to"
    DEPARTMENTS }o--|| EMPLOYEES        : "managed by"
    JOB_POSITIONS }o--|| DEPARTMENTS    : "belongs to"
    JOB_POSITIONS }o--o| JOB_GRADES     : "grade band (PL/SQL only)"
    EMPLOYEES ||--o{ EMPLOYEE_HISTORY   : "has audit trail"
```

---

### 3.2 Payroll Cluster

```mermaid
erDiagram
    EMPLOYEES {
        number(10)   EMPLOYEE_ID PK
        varchar2(20) EMPLOYMENT_STATUS
        number(2)    GRADE
    }

    SALARY_RECORDS {
        number(10)    SALARY_ID PK
        number(10)    EMPLOYEE_ID FK
        number(12,2)  BASE_SALARY
        date          EFFECTIVE_DATE
        date          END_DATE
        varchar2(20)  SALARY_TYPE
        number(10)    APPROVED_BY FK
    }

    EMPLOYEE_PAY_ELEMENTS {
        number(10)    ELEMENT_ID PK
        varchar2(100) ELEMENT_NAME
        varchar2(20)  ELEMENT_TYPE
        varchar2(20)  GL_ACCOUNT_CODE
        char(1)       ACTIVE_FLAG
    }

    PAYROLL_RUNS {
        number(10)    RUN_ID PK
        varchar2(100) RUN_NAME
        date          PAY_PERIOD_START
        date          PAY_PERIOD_END
        varchar2(20)  STATUS
        number(15,2)  TOTAL_GROSS
        number(15,2)  TOTAL_NET
        number(15,2)  TOTAL_DEDUCTIONS
        number(10)    APPROVED_BY FK
    }

    PAYROLL_DETAILS {
        number(10)    DETAIL_ID PK
        number(10)    RUN_ID FK
        number(10)    EMPLOYEE_ID FK
        number(10)    ELEMENT_ID FK
        number(12,2)  AMOUNT
        varchar2(20)  STATUS
    }

    DEDUCTION_RECORDS {
        number(10)    DEDUCTION_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    RUN_ID FK
        varchar2(50)  DEDUCTION_TYPE
        number(12,2)  AMOUNT
        date          EFFECTIVE_DATE
    }

    EMPLOYEE_BANK_ACCOUNTS {
        number(10)    BANK_ACCT_ID PK
        number(10)    EMP_ID FK
        varchar2(20)  DEPOSIT_TYPE
        number(2)     PRIORITY_ORDER
        char(1)       PRENOTE_SENT
        char(1)       ACTIVE_FLAG
    }

    EMPLOYEES ||--o{ SALARY_RECORDS         : "has salary history"
    EMPLOYEES ||--o{ PAYROLL_DETAILS        : "paid via"
    EMPLOYEES ||--o{ DEDUCTION_RECORDS      : "has deductions"
    EMPLOYEES ||--o{ EMPLOYEE_BANK_ACCOUNTS : "has bank accounts"
    PAYROLL_RUNS ||--o{ PAYROLL_DETAILS     : "contains line items"
    PAYROLL_RUNS ||--o{ DEDUCTION_RECORDS   : "contains deductions"
    EMPLOYEE_PAY_ELEMENTS ||--o{ PAYROLL_DETAILS : "element type of"
```

---

### 3.3 Leave Cluster

```mermaid
erDiagram
    EMPLOYEES {
        number(10)   EMPLOYEE_ID PK
        varchar2(20) EMPLOYMENT_STATUS
        number(10)   DEPARTMENT_ID FK
    }

    LEAVE_TYPES {
        number(10)   LEAVE_TYPE_ID PK
        varchar2(50) LEAVE_TYPE_NAME
        varchar2(20) LEAVE_CODE
        number(5,2)  ANNUAL_ENTITLEMENT
        number(5,2)  ACCRUAL_RATE
        char(1)      REQUIRES_DOCUMENT
        char(1)      ACTIVE_FLAG
    }

    LEAVE_BALANCES {
        number(10)   BALANCE_ID PK
        number(10)   EMPLOYEE_ID FK
        number(10)   LEAVE_TYPE_ID FK
        number(5,2)  OPENING_BALANCE
        number(5,2)  ACCRUED
        number(5,2)  TAKEN
        number(5,2)  PENDING
        number(4)    CALENDAR_YEAR
        date         LAST_ACCRUAL_DATE
    }

    LEAVE_REQUESTS {
        number(10)    REQUEST_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    LEAVE_TYPE_ID FK
        date          START_DATE
        date          END_DATE
        number(5,2)   DAYS_REQUESTED
        varchar2(20)  STATUS
        varchar2(500) SUPPORTING_DOC_PATH
        number(10)    APPROVED_BY FK
        date          APPROVED_DATE
    }

    LEAVE_TYPES ||--o{ LEAVE_BALANCES   : "balance type"
    LEAVE_TYPES ||--o{ LEAVE_REQUESTS   : "request type"
    EMPLOYEES ||--o{ LEAVE_BALANCES     : "holds balance"
    EMPLOYEES ||--o{ LEAVE_REQUESTS     : "submits request"
    EMPLOYEES }o--o{ LEAVE_REQUESTS     : "approves (manager)"
```

---

### 3.4 Performance Cluster

```mermaid
erDiagram
    EMPLOYEES {
        number(10)   EMPLOYEE_ID PK
        varchar2(20) EMPLOYMENT_STATUS
        number(2)    GRADE
    }

    REVIEW_CYCLES {
        number(10)    CYCLE_ID PK
        varchar2(100) CYCLE_NAME
        date          START_DATE
        date          END_DATE
        varchar2(20)  STATUS
    }

    PERFORMANCE_REVIEWS {
        number(10)    REVIEW_ID PK
        number(10)    CYCLE_ID FK
        number(10)    EMPLOYEE_ID FK
        number(10)    REVIEWER_EMP_ID FK
        number(3,1)   OVERALL_RATING
        varchar2(20)  RATING_LABEL
        number(3,1)   CALIBRATED_RATING
        clob          CALIBRATION_NOTES
        varchar2(20)  STATUS
    }

    PERFORMANCE_GOALS {
        number(10)    GOAL_ID PK
        number(10)    EMPLOYEE_ID FK
        number(10)    CYCLE_ID FK
        varchar2(200) GOAL_TITLE
        varchar2(20)  STATUS
        number(3,1)   PROGRESS_PCT
    }

    GOAL_REVIEWS {
        number(10)    GOAL_REVIEW_ID PK
        number(10)    GOAL_ID FK
        number(10)    REVIEW_ID FK
        number(3,1)   ACHIEVEMENT_RATING
        clob          COMMENTS
    }

    REVIEW_CYCLES ||--o{ PERFORMANCE_REVIEWS : "scopes"
    REVIEW_CYCLES ||--o{ PERFORMANCE_GOALS   : "scopes"
    EMPLOYEES ||--o{ PERFORMANCE_REVIEWS     : "reviewed in"
    EMPLOYEES ||--o{ PERFORMANCE_REVIEWS     : "reviews as manager"
    EMPLOYEES ||--o{ PERFORMANCE_GOALS       : "owns"
    PERFORMANCE_GOALS ||--o{ GOAL_REVIEWS    : "assessed via"
    PERFORMANCE_REVIEWS ||--o{ GOAL_REVIEWS  : "contains"
```

---

### 3.5 Security Cluster

```mermaid
erDiagram
    EMPLOYEES {
        number(10)   EMPLOYEE_ID PK
        varchar2(20) EMPLOYMENT_STATUS
        number(2)    GRADE
        varchar2(100) EMAIL
    }

    USER_CREDENTIALS {
        number(10)    EMP_ID PK_FK
        varchar2(200) PASSWORD_HASH
        date          CREATED_DATE
        date          MODIFIED_DATE
    }

    USER_SESSIONS {
        varchar2(36)  SESSION_ID PK
        number(10)    EMP_ID FK
        date          LOGIN_TIME
        date          LAST_ACTIVITY
        varchar2(20)  STATUS
        varchar2(50)  IP_ADDRESS
    }

    AUDIT_LOG {
        number(10)    LOG_ID PK
        varchar2(50)  LOG_TYPE
        varchar2(50)  TABLE_NAME
        number(10)    RECORD_ID
        varchar2(50)  ACTION
        varchar2(50)  PERFORMED_BY
        date          LOG_DATE
        varchar2(50)  SESSION_ID
    }

    SYSTEM_CONFIG {
        number(10)    CONFIG_ID PK
        varchar2(50)  CONFIG_KEY
        varchar2(500) CONFIG_VALUE
    }

    SYSTEM_PARAMETERS {
        varchar2(50)  PARAM_NAME PK
        varchar2(200) PARAM_VALUE
        varchar2(50)  PARAM_GROUP
    }

    EMPLOYEES ||--|{ USER_CREDENTIALS  : "has credentials (1:1)"
    EMPLOYEES ||--o{ USER_SESSIONS     : "has sessions"
    USER_SESSIONS }o--o{ AUDIT_LOG     : "referenced in log (soft)"
```

---

## 4. Relationship Cardinalities Explained

| Relationship | Cardinality | Enforcement | Notes |
|---|---|---|---|
| EMPLOYEES → DEPARTMENTS | Many-to-one (N:1) | FK DDL | Each employee belongs to exactly one department; department can have zero employees |
| EMPLOYEES → EMPLOYEES (manager) | Many-to-one (N:0..1) | FK DDL self-ref | Manager can be NULL (top of hierarchy); one manager can manage many employees |
| DEPARTMENTS → DEPARTMENTS (parent) | Many-to-one (N:0..1) | FK DDL self-ref | Root department has NULL parent; arbitrarily deep nesting permitted |
| DEPARTMENTS → EMPLOYEES (manager) | Many-to-one (N:0..1) | FK DDL | Department can exist with no manager assigned; one employee can manage many departments in theory |
| JOB_POSITIONS → DEPARTMENTS | Many-to-one (N:0..1) | FK DDL | Position-to-department association is optional; a position can span departments |
| JOB_POSITIONS → JOB_GRADES | Many-to-one (N:0..1) | PL/SQL only | No DDL FK; grade band enforced in PKG_EMPLOYEE at hire/transfer only |
| EMPLOYEES → SALARY_RECORDS | One-to-many (1:N) | FK DDL | One employee has N salary records over time; current = MAX(EFFECTIVE_DATE) WHERE END_DATE IS NULL |
| EMPLOYEES → PAYROLL_DETAILS | One-to-many (1:N) | FK DDL | One employee appears once per pay element per payroll run |
| PAYROLL_RUNS → PAYROLL_DETAILS | One-to-many (1:N) | FK DDL | One run contains N detail lines (one per employee per element) |
| PAYROLL_RUNS → DEDUCTION_RECORDS | One-to-many (1:N) | FK DDL | One run contains N deduction lines |
| EMPLOYEES → EMPLOYEE_BANK_ACCOUNTS | One-to-many (1:N) | FK DDL | Split-deposit supports multiple active accounts per employee |
| EMPLOYEES → LEAVE_BALANCES | One-to-many (1:N) | FK DDL | One balance row per employee per leave type per calendar year |
| LEAVE_TYPES → LEAVE_BALANCES | One-to-many (1:N) | FK DDL | One leave type has N balance rows across employees and years |
| EMPLOYEES → LEAVE_REQUESTS | One-to-many (1:N) | FK DDL | One employee can submit N leave requests |
| EMPLOYEES → PERFORMANCE_REVIEWS | One-to-many (1:N) | FK DDL (as reviewee) | One employee has N reviews across cycles |
| EMPLOYEES → PERFORMANCE_REVIEWS | One-to-many (1:N) | FK DDL (as reviewer) | One manager conducts N reviews |
| REVIEW_CYCLES → PERFORMANCE_REVIEWS | One-to-many (1:N) | FK DDL | One cycle contains N reviews (one per employee in scope) |
| PERFORMANCE_GOALS → GOAL_REVIEWS | One-to-many (1:N) | FK DDL | One goal can be assessed in N reviews (multi-cycle scenario) |
| EMPLOYEES → EMPLOYEE_DEPENDENTS | One-to-many (1:N) | FK DDL | One employee can have N dependents |
| EMPLOYEES → BENEFIT_ENROLLMENTS | One-to-many (1:N) | FK DDL | One employee can have N benefit plan enrollments |
| BENEFIT_PLANS → BENEFIT_ENROLLMENTS | One-to-many (1:N) | FK DDL | One plan has N enrollments across the employee base |
| EMPLOYEES → USER_CREDENTIALS | One-to-one (1:1) | FK DDL (PK/FK same column) | Credentials row is keyed by EMP_ID; one employee, one credential record |
| EMPLOYEES → USER_SESSIONS | One-to-many (1:N) | FK DDL | One employee can have N session records (historical and active) |
| EMPLOYEES → NOTIFICATION_QUEUE | One-to-many (1:N) | FK DDL | One employee receives N notifications over time |
| EMPLOYEES → EMPLOYEE_HISTORY | One-to-many (1:N) | FK DDL | Full audit trail of attribute changes |
| EMPLOYEES → TERMINATION_CODES | Many-to-one (N:0..1) | FK DDL | Termination reason is NULL while employed; references code on termination |

---

## 5. Referential Integrity Gaps

The following gaps were identified where business relationships exist but are not enforced by DDL foreign key constraints. Each gap represents a potential for orphan records or silent data inconsistency.

### Gap 1 — JOB_POSITIONS to JOB_GRADES (No FK)

**Tables:** `JOB_POSITIONS.MIN_GRADE` / `MAX_GRADE` → `JOB_GRADES.GRADE_LEVEL`

**Expected relationship:** A job position should reference valid grade levels from JOB_GRADES. Currently, `MIN_GRADE` and `MAX_GRADE` are plain `NUMBER(2)` columns with no FK to `JOB_GRADES`. A grade band of `MIN_GRADE=5, MAX_GRADE=99` would be inserted without error.

**Risk:** Salary band validation in `HRMS_VALIDATION_LIB.validate_salary_range` performs a live `SELECT FROM JOB_GRADES` using `GRADE_LEVEL`. If `JOB_POSITIONS` holds an invalid grade number, the query returns no rows and the salary validation silently passes without checking any bounds.

**Recommended fix:** Add FK constraint `JOB_POSITIONS.MIN_GRADE_ID REFERENCES JOB_GRADES(GRADE_ID)` and `MAX_GRADE_ID REFERENCES JOB_GRADES(GRADE_ID)`. Alternatively, replace the numeric grade columns with proper FK columns pointing to `JOB_GRADES.GRADE_ID`.

---

### Gap 2 — PERFORMANCE_REVIEWS.CALIBRATED_RATING (No write path)

**Tables:** `PERFORMANCE_REVIEWS.CALIBRATED_RATING` / `CALIBRATION_NOTES`

**Expected relationship:** The calibration rating should be populated by a calibration workflow, and reporting procedures should reference `CALIBRATED_RATING` for official distributions rather than `OVERALL_RATING`.

**Risk:** `get_rating_distribution` aggregates `OVERALL_RATING` — the raw, uncalibrated manager-submitted value. Every distribution report published to leadership reflects pre-calibration data. If calibration intent is that the adjusted score replaces the raw score for official purposes, every historical distribution report is incorrect.

**Recommended fix:** Implement the calibration workflow: add a `CALIBRATION` status between `COMPLETED` and `ACKNOWLEDGED`; create a `calibrate_review` procedure that writes `CALIBRATED_RATING` and `CALIBRATION_NOTES`; update `get_rating_distribution` to use `COALESCE(CALIBRATED_RATING, OVERALL_RATING)`.

---

### Gap 3 — EMPLOYEE_BANK_ACCOUNTS (No payroll read path)

**Tables:** `EMPLOYEE_BANK_ACCOUNTS` → `PAYROLL_RUNS` / `PAYROLL_DETAILS`

**Expected relationship:** After a payroll run is approved, the system should read `EMPLOYEE_BANK_ACCOUNTS` to generate an ACH disbursement file and advance the run to `PAID` status.

**Risk:** No such relationship exists in the current codebase. `PAYROLL_RUNS.STATUS` has no `PAID` value (only `DRAFT`, `CALCULATED`, `APPROVED`, `GL_GENERATED`, `COMPLETED`). Every disbursement happens entirely outside the system via manual processes.

**Recommended fix:** Create `PKG_PAYROLL.generate_ach_file` procedure; add `PAID` status to the payroll run lifecycle; add `GL_FEED_SENT_DATE` and `GL_FEED_FILE_NAME` columns to `PAYROLL_RUNS` for reconciliation.

---

### Gap 4 — USER_CREDENTIALS (Authentication never uses it)

**Tables:** `USER_CREDENTIALS.PASSWORD_HASH` → `PKG_SECURITY.authenticate`

**Expected relationship:** `authenticate(p_username, p_password)` should compare a hash of `p_password` against `USER_CREDENTIALS.PASSWORD_HASH` for the resolved employee.

**Risk:** The current `authenticate` function never queries `USER_CREDENTIALS`. Any valid username authenticates regardless of the password supplied. This renders the entire credential table meaningless from an access-control perspective.

**Recommended fix:** Implement password verification in `authenticate`: `SELECT PASSWORD_HASH INTO v_stored_hash FROM USER_CREDENTIALS WHERE EMP_ID = v_emp_id`; compare against `PKG_SECURITY.hash_password(p_password)`. Simultaneously, replace MD5 with a proper password hash (bcrypt or PBKDF2 via external Java stored procedure, since Oracle DBMS_CRYPTO does not natively support bcrypt).

---

### Gap 5 — EMPLOYEE_DEPENDENTS.BENEFITS_ENROLLED (Never read)

**Tables:** `EMPLOYEE_DEPENDENTS.BENEFITS_ENROLLED` → `PKG_INTEGRATION.export_benefits_feed`

**Expected relationship:** The benefits feed should filter to dependents where `BENEFITS_ENROLLED = 'Y'`.

**Risk:** The current JOIN in `export_benefits_feed` uses only `d.ACTIVE_FLAG = 'Y'` as the filter. All active dependents are exported to ADP regardless of whether they are enrolled in a benefit plan. ADP may activate coverage for un-enrolled dependents.

**Recommended fix:** Add `AND d.BENEFITS_ENROLLED = 'Y'` to the `export_benefits_feed` JOIN condition. Requires prior data remediation to confirm `BENEFITS_ENROLLED` is correctly set for all existing dependents.

---

### Gap 6 — DEDUCTION_RECORDS to BENEFIT_ENROLLMENTS (No FK)

**Tables:** `DEDUCTION_RECORDS.DEDUCTION_TYPE` → `BENEFIT_PLANS`

**Expected relationship:** Benefit-related deductions in `DEDUCTION_RECORDS` should reference the specific benefit plan that generated them, enabling reconciliation between what was deducted from pay and what was enrolled in.

**Risk:** `DEDUCTION_TYPE` is a free-text `VARCHAR2(50)`. Deduction records cannot be reconciled to benefit enrollments by SQL join; reconciliation requires string matching on `DEDUCTION_TYPE` values, which are subject to inconsistent naming.

**Recommended fix:** Add optional FK column `DEDUCTION_RECORDS.PLAN_ID REFERENCES BENEFIT_PLANS(PLAN_ID)`. Populate it for benefit-related deductions; leave NULL for statutory deductions (federal tax, state tax, garnishments).

---

### Gap 7 — LEAVE_REQUESTS approval path (No manager FK constraint)

**Tables:** `LEAVE_REQUESTS.APPROVED_BY` → `EMPLOYEES`

**Expected relationship:** The approver should be the employee's direct manager or an HR administrator — enforced by the application but not constrained in DDL.

**Risk:** The FK `APPROVED_BY REFERENCES EMPLOYEES(EMPLOYEE_ID)` ensures the approver is a valid employee, but nothing prevents an employee from approving their own leave request at the DDL level. The constraint is in PKG_LEAVE only.

**Recommended fix:** Add a DDL-level check constraint: `CONSTRAINT CHK_LEAVE_SELF_APPROVAL CHECK (APPROVED_BY != EMPLOYEE_ID)`. For the manager validation, maintain the PL/SQL enforcement in `PKG_LEAVE.approve_leave_request`.

---

### Gap 8 — NOTIFICATION_QUEUE lacks TEMPLATE_ID FK

**Tables:** `NOTIFICATION_QUEUE` → `NOTIFICATION_TEMPLATES`

**Expected relationship:** Each notification in the queue could trace back to the template from which it was generated, enabling template performance tracking and re-generation.

**Risk:** The queue stores the already-rendered body inline (`BODY CLOB`). No `TEMPLATE_ID` column exists. If a template is updated, there is no way to identify which queued or historical messages were generated from the old version.

**Recommended fix:** Add `TEMPLATE_ID NUMBER(10) REFERENCES NOTIFICATION_TEMPLATES(TEMPLATE_ID)` as a nullable column on `NOTIFICATION_QUEUE`. Populate it at message-generation time in `PKG_NOTIFICATION.send_notification`.

---

### Gap 9 — No PAYROLL_RUNS.GL_FEED_STATUS tracking

**Tables:** `PAYROLL_RUNS` → Oracle Financials GL feed

**Expected relationship:** After `PKG_INTEGRATION.generate_gl_journal` generates the pipe-delimited feed file, the payroll run row should record whether the file was generated, when, and whether it was acknowledged.

**Risk:** If the GL feed fails silently (UTL_FILE error, Oracle Financials rejection), there is no indicator in `PAYROLL_RUNS`. Payroll administrators have no SQL-queryable view of which runs have been successfully fed to the GL.

**Recommended fix:** Add `GL_FEED_SENT_DATE DATE`, `GL_FEED_FILE_NAME VARCHAR2(200)`, and `GL_FEED_STATUS VARCHAR2(20)` columns to `PAYROLL_RUNS`. Update them at successful `UTL_FILE.FCLOSE`.

---

### Gap 10 — EMPLOYEE_DEPENDENTS has no unique constraint on singular relationships

**Tables:** `EMPLOYEE_DEPENDENTS` — `(EMP_ID, RELATIONSHIP)` combination

**Expected relationship:** An employee should not have two active SPOUSE dependents simultaneously.

**Risk:** The schema permits `INSERT INTO EMPLOYEE_DEPENDENTS (EMP_ID, RELATIONSHIP) VALUES (42, 'SPOUSE')` twice. The ADP benefits feed would export both rows, potentially creating duplicate benefit enrollments at the vendor.

**Recommended fix:** Add partial unique constraint for singular relationships:
```sql
CREATE UNIQUE INDEX UIX_DEP_UNIQUE_SPOUSE
  ON EMPLOYEE_DEPENDENTS (EMP_ID, RELATIONSHIP)
  WHERE RELATIONSHIP IN ('SPOUSE', 'DOMESTIC_PARTNER')
    AND ACTIVE_FLAG = 'Y';
```

---

## 6. Recommended New Tables for the Modernised System

The following tables are recommended to close functional gaps, resolve referential integrity issues, and support compliance requirements identified across the BA, DA, TA, and AA analysis tracks.

### 6.1 PAYROLL_DISBURSEMENTS

**Closes:** Gap 3 (EMPLOYEE_BANK_ACCOUNTS unused), BR-BA-01 (direct deposit non-functional), DISC-009 (PAID status orphaned).

```
PAYROLL_DISBURSEMENTS
  DISBURSEMENT_ID       NUMBER(10)      PK
  RUN_ID                NUMBER(10)      FK → PAYROLL_RUNS
  EMP_ID                NUMBER(10)      FK → EMPLOYEES
  BANK_ACCT_ID          NUMBER(10)      FK → EMPLOYEE_BANK_ACCOUNTS
  NET_AMOUNT            NUMBER(12,2)    NN
  DISBURSEMENT_METHOD   VARCHAR2(20)    CHK ('ACH', 'CHECK', 'WIRE')
  ACH_TRACE_NUMBER      VARCHAR2(30)
  STATUS                VARCHAR2(20)    CHK ('PENDING', 'SUBMITTED', 'CONFIRMED', 'FAILED', 'REVERSED')
  NACHA_FILE_NAME       VARCHAR2(200)
  SUBMITTED_DATE        DATE
  CONFIRMED_DATE        DATE
  ERROR_CODE            VARCHAR2(50)
  ERROR_MESSAGE         VARCHAR2(500)
  CREATED_BY            VARCHAR2(30)    NN
  CREATED_DATE          DATE            NN
```

**Rationale:** Enables end-to-end tracking of each employee disbursement within a payroll run. The `NACHA_FILE_NAME` links the record to the ACH file submitted to the bank. `ACH_TRACE_NUMBER` supports return item reconciliation per Nacha Rule R-codes.

---

### 6.2 COBRA_EVENTS

**Closes:** PP-TERM-01 (COBRA compliance gap on every termination), VQ-TERM-02, VQ-DEP-04.

```
COBRA_EVENTS
  COBRA_EVENT_ID        NUMBER(10)      PK
  EMP_ID                NUMBER(10)      FK → EMPLOYEES
  QUALIFYING_EVENT_TYPE VARCHAR2(50)    CHK ('TERMINATION', 'HOURS_REDUCTION', 'DIVORCE', 'DEPENDENT_AGING_OUT', 'DEATH')
  QUALIFYING_EVENT_DATE DATE            NN
  NOTICE_REQUIRED_DATE  DATE            GENERATED ALWAYS AS (QUALIFYING_EVENT_DATE + 14)
  NOTICE_SENT_DATE      DATE
  ELECTION_DEADLINE     DATE            GENERATED ALWAYS AS (QUALIFYING_EVENT_DATE + 60)
  ELECTION_RECEIVED     CHAR(1)         DEFAULT 'N' CHK ('Y', 'N')
  ELECTION_DATE         DATE
  COVERAGE_START        DATE
  COVERAGE_END          DATE
  CREATED_BY            VARCHAR2(30)    NN
  CREATED_DATE          DATE            NN
```

**Rationale:** Federal COBRA requires qualified beneficiary notification within 14 days of a qualifying event, with a 60-day election window. Every call to `terminate_employee` should insert a row here. The computed columns expose compliance deadlines without requiring procedural calculation.

---

### 6.3 ACH_PRENOTE_HISTORY

**Closes:** PP-BA-03 (ACH prenote not implemented), BR-BA-05 (PRENOTE_SENT never set), Nacha compliance requirement.

```
ACH_PRENOTE_HISTORY
  PRENOTE_ID            NUMBER(10)      PK
  BANK_ACCT_ID          NUMBER(10)      FK → EMPLOYEE_BANK_ACCOUNTS
  PRENOTE_FILE_NAME     VARCHAR2(200)
  SUBMITTED_DATE        DATE            NN
  SETTLEMENT_DATE       DATE
  STATUS                VARCHAR2(20)    CHK ('SUBMITTED', 'SETTLED', 'RETURNED')
  RETURN_CODE           VARCHAR2(10)
  RETURN_REASON         VARCHAR2(200)
  CREATED_BY            VARCHAR2(30)    NN
  CREATED_DATE          DATE            NN
```

**Rationale:** Nacha rules require a zero-dollar prenote to be sent 3 banking days before the first live ACH credit to a new account. This table tracks the prenote lifecycle separately from the disbursement, enabling automated prenote scheduling and return-item handling.

Looking at the gap description and inferring column patterns from `PKG_PERFORMANCE.pkb` (status lifecycle, audit fields, rating label constants, org/employee FK patterns seen throughout the package).

---

### 6.4 CALIBRATION_SESSIONS

**Closes:** PERFORMANCE_REVIEWS.CALIBRATED_RATING gap (Gap 2), missing calibration workflow.

```
CALIBRATION_SESSIONS
  SESSION_ID            NUMBER(10)      PK
  CYCLE_ID              NUMBER(10)      FK → REVIEW_CYCLES
  SESSION_STATUS        VARCHAR2(20)    NOT NULL  -- [GAP-FILLED] 'DRAFT','IN_PROGRESS','COMPLETED','CANCELLED'
  SESSION_DATE          DATE            NOT NULL  -- [GAP-FILLED] scheduled date of calibration meeting
  FACILITATOR_EMP_ID    NUMBER(10)      FK → EMPLOYEES  -- [GAP-FILLED] HR facilitator running the session
  DEPT_ID               NUMBER(10)      FK → DEPARTMENTS  -- [GAP-FILLED] org unit / department scope
  CNT_EXCEPTIONAL       NUMBER(5)       DEFAULT 0  -- [GAP-FILLED] rating distribution snapshot: 'Exceptional'
  CNT_EXCEEDS           NUMBER(5)       DEFAULT 0  -- [GAP-FILLED] 'Exceeds Expectations'
  CNT_MEETS             NUMBER(5)       DEFAULT 0  -- [GAP-FILLED] 'Meets Expectations'
  CNT_NEEDS_IMPROVEMENT NUMBER(5)       DEFAULT 0  -- [GAP-FILLED] 'Needs Improvement'
  CNT_UNSATISFACTORY    NUMBER(5)       DEFAULT 0  -- [GAP-FILLED] 'Unsatisfactory'
  COMPLETION_DATE       DATE                       -- [GAP-FILLED] timestamp when session status set to COMPLETED
  CREATED_BY            VARCHAR2(50)    NOT NULL   -- [GAP-FILLED]
  CREATED_DATE          DATE            DEFAULT SYSDATE  -- [GAP-FILLED]
  MODIFIED_BY           VARCHAR2(50)               -- [GAP-FILLED]
  MODIFIED_DATE         DATE                       -- [GAP-FILLED]
```
  FACILITATED_BY        NUMBER(10)      FK → EMPLOYEES
  SESSION_DATE          DATE            NN
  STATUS                VARCHAR2(20)    CHK ('PLANNED', 'IN_PROGRESS', 'COMPLETED')
  CREATED_BY            VARCHAR2(30)    NN
  CREATED_DATE          DATE            NN

CALIBRATION_ADJUSTMENTS
  ADJUSTMENT_ID         NUMBER(10)      PK
  SESSION_ID            NUMBER(10)      FK → CALIBRATION_SESSIONS
  REVIEW_ID             NUMBER(10)      FK → PERFORMANCE_REVIEWS
  ORIGINAL_RATING       NUMBER(3,1)
  CALIBRATED_RATING     NUMBER(3,1)     NN
  ADJUSTMENT_REASON     VARCHAR2(500)
  ADJUSTED_BY           NUMBER(10)      FK → EMPLOYEES
  ADJUSTED_DATE         DATE            NN
```

**Rationale:** Calibration is a structured group process. Separating session metadata (`CALIBRATION_SESSIONS`) from individual adjustments (`CALIBRATION_ADJUSTMENTS`) allows: tracking who facilitated, which reviews were discussed, who made each rating change, and what the rationale was. The final `CALIBRATED_RATING` from this table should be written back to `PERFORMANCE_REVIEWS.CALIBRATED_RATING` after session completion.

---

### 6.5 GL_FEED_RECONCILIATION

**Closes:** Gap 9 (no GL feed status on PAYROLL_RUNS), TD-80.

```
GL_FEED_RECONCILIATION
  RECONCILIATION_ID     NUMBER(10)      PK
  RUN_ID                NUMBER(10)      FK → PAYROLL_RUNS
  FEED_TYPE             VARCHAR2(20)    CHK ('PAYROLL', 'BENEFITS', 'LEAVE_ACCRUAL')
  FILE_NAME             VARCHAR2(200)   NN
  GENERATED_DATE        DATE            NN
  RECORD_COUNT          NUMBER(10)
  TOTAL_AMOUNT          NUMBER(15,2)
  SUBMISSION_DATE       DATE
  ACKNOWLEDGEMENT_DATE  DATE
  GL_BATCH_NUMBER       VARCHAR2(50)
  STATUS                VARCHAR2(20)    CHK ('GENERATED', 'SUBMITTED', 'ACKNOWLEDGED', 'REJECTED', 'RECONCILED')
  REJECTION_REASON      VARCHAR2(500)
  CREATED_BY            VARCHAR2(30)    NN
  CREATED_DATE          DATE            NN
```

**Rationale:** Provides an auditable reconciliation trail for every file sent to Oracle Financials. `RECORD_COUNT` and `TOTAL_AMOUNT` enable balancing checks: the imported GL batch total in Oracle Financials must match these values. `GL_BATCH_NUMBER` is the acknowledgement reference returned by Oracle Financials Journal Import.

---

### 6.6 PASSWORD_HISTORY

**Closes:** MD5 replacement migration, no password age tracking, `change_password` stub.

```
PASSWORD_HISTORY
  HISTORY_ID            NUMBER(10)      PK
  EMP_ID                NUMBER(10)      FK → EMPLOYEES
  PASSWORD_HASH         VARCHAR2(200)   NN
  HASH_ALGORITHM        VARCHAR2(20)    NN
  CHANGED_DATE          DATE            NN
  CHANGED_BY            VARCHAR2(50)    NN
  CHANGE_REASON         VARCHAR2(50)    CHK ('USER_INITIATED', 'ADMIN_RESET', 'FORCED_EXPIRY', 'MIGRATION')
```

**Rationale:** Required for: (a) password reuse prevention (reject new password if hash matches last N entries), (b) tracking the algorithm migration from MD5 to bcrypt/PBKDF2 during modernisation (the `HASH_ALGORITHM` column distinguishes old from new hashes), and (c) compliance reporting on password change frequency.

---

### 6.7 LEAVE_PAYOUT_RECORDS

**Closes:** VQ-TERM-05 (PTO payout on termination), PP-TERM-03 (calculate_final_pay non-existent).

```
LEAVE_PAYOUT_RECORDS
  PAYOUT_ID             NUMBER(10)      PK
  EMP_ID                NUMBER(10)      FK → EMPLOYEES
  LEAVE_TYPE_ID         NUMBER(10)      FK → LEAVE_TYPES
  TERMINATION_DATE      DATE            NN
  BALANCE_AT_TERMINATION NUMBER(5,2)    NN
  PAYOUT_POLICY         VARCHAR2(20)    CHK ('FULL', 'CAPPED', 'NONE')
  HOURS_PAID_OUT        NUMBER(5,2)
  PAYOUT_AMOUNT         NUMBER(12,2)
  INCLUDED_IN_RUN_ID    NUMBER(10)      FK → PAYROLL_RUNS
  CREATED_BY            VARCHAR2(30)    NN
  CREATED_DATE          DATE            NN
```

**Rationale:** When `PKG_EMPLOYEE.terminate_employee` is called, leave balances at termination must be captured before `PKG_LEAVE.initialize_balances` can clear or close them. This table creates an immutable record of what was owed, the policy applied, and which payroll run disbursed the payout.

---

### 6.8 Inferred Reporting Tables (RPT_*)

These seven tables are referenced in `PKG_REPORTING.refresh_reporting_tables` but the refresh procedure is a stub — it writes no data. The tables are inferred from the SELECT lists of the seven live reporting procedures. They should be formally created with DDL in the modernised system.

| Table | Source Report Procedure | Key Columns |
|---|---|---|
| `RPT_HEADCOUNT` | `headcount_report` | DEPARTMENT_NAME, AS_OF_DATE, FT_COUNT, PT_COUNT, CONTRACT_COUNT, TOTAL_COUNT, AVG_TENURE_YEARS, GENDER_M, GENDER_F, GENDER_OTHER |
| `RPT_COMPENSATION` | `compensation_summary` | DEPARTMENT_NAME, GRADE_LEVEL, EMPLOYEE_COUNT, AVG_SALARY, MEDIAN_SALARY, MIN_SALARY, MAX_SALARY, COMPA_RATIO |
| `RPT_TURNOVER` | `turnover_report` | DEPARTMENT_NAME, PERIOD_START, PERIOD_END, HIRES, TERMINATIONS, VOLUNTARY_TERMS, INVOLUNTARY_TERMS, TURNOVER_PCT |
| `RPT_NEW_HIRES` | `new_hires_report` | EMPLOYEE_NUMBER, FULL_NAME, HIRE_DATE, DEPARTMENT_NAME, JOB_TITLE, LOCATION, STARTING_SALARY, MANAGER_NAME |
| `RPT_LEAVE_UTILIZATION` | `leave_utilization_report` | DEPARTMENT_NAME, LEAVE_TYPE_NAME, CALENDAR_YEAR, AVG_ENTITLEMENT, AVG_TAKEN, UTILIZATION_PCT |
| `RPT_PAYROLL_SUMMARY` | `payroll_summary_report` | RUN_NAME, PAY_PERIOD_START, PAY_PERIOD_END, DEPARTMENT_NAME, TOTAL_GROSS, TOTAL_DEDUCTIONS, TOTAL_NET, EMPLOYEE_COUNT |
| `RPT_EEO_COMPLIANCE` | `eeo_compliance_report` | EEO_CATEGORY, JOB_TITLE, TOTAL_COUNT, GENDER_M, GENDER_F, GENDER_OTHER, GENDER_NOT_DISCLOSED |

**Important note for modernisation:** `RPT_COMPENSATION` uses Oracle `MEDIAN()` aggregate, which has no direct equivalent in PostgreSQL (`PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary)`) or SQL Server (`PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) OVER (PARTITION BY ...)`). The translation is non-trivial and must be tested against large datasets.

`RPT_LEAVE_UTILIZATION` does not project `CALENDAR_YEAR` in its cursor output. If the RPT table is to support multi-year snapshots, the year must be injected as a separate column at INSERT time during the nightly refresh.

---

## 7. Summary of Findings

| Category | Count | Top Issue |
|---|---|---|
| Total confirmed DDL tables | 30 | — |
| Total inferred / staging tables | 9 (7 RPT_* + 2 integration) | No DDL recovered |
| DDL-enforced FK relationships | 22 | All listed in section 4 |
| PL/SQL-only enforced relationships | 6 | JOB_POSITIONS→JOB_GRADES is the highest risk |
| Referential integrity gaps identified | 10 | EMPLOYEE_BANK_ACCOUNTS unused (Gap 3) |
| Recommended new tables | 7 confirmed + 7 RPT_* formalised | COBRA_EVENTS (federal compliance) |
| Dead columns (schema present, no write path) | 3 | CALIBRATED_RATING, BENEFITS_ENROLLED, PRENOTE_SENT/DATE |
| Critical data model defects | 2 | authenticate() ignores USER_CREDENTIALS; direct deposit non-functional |

---

*Document prepared by: Data Architecture Track*
*Based on: schema-catalogue.json (DA), BA_Deep_Analyst.md (BA), PKG_* source analysis (TA/AA)*
*Cross-validated against: DA_Data_Reviewer.md (three-pass review, 35 corrections applied)*
