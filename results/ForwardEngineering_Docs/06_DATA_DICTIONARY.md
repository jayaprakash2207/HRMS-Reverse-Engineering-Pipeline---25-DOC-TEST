The actual DDL tells the full story. The real `NOTIFICATION_QUEUE` table has no `PAYLOAD` column and no `TEMPLATE_ID` — callers construct the full body inline via string concatenation and pass it as `p_body CLOB` directly to `send_notification`. Here is the complete updated document section:

---

# 06 — Data Dictionary
**System:** Acme Corporation HRMS (Oracle 19c)
**Scope:** All confirmed DDL tables (30), confirmed views (6), inferred tables noted.
**Convention:** PK = Primary Key; FK = Foreign Key; UK = Unique Key; NN = NOT NULL; CHK = Check constraint; VIR = Virtual column; PII = Personal data; ENC = Encrypted at rest.

---

## Table: EMPLOYEES

Business meaning: Master record for every current and former employee. The central aggregate root; nearly every other table carries EMPLOYEE_ID as a foreign key.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| EMPLOYEE_ID | NUMBER(10) | PK, NN | No | System-generated surrogate key. Source: SQ_EMPLOYEE_ID (NOCACHE). |
| EMPLOYEE_NUMBER | VARCHAR2(20) | UK, NN | No | Human-readable HR identifier (e.g. "EMP-00042"). |
| FIRST_NAME | VARCHAR2(50) | NN | Yes | Legal first name as on employment contract. |
| LAST_NAME | VARCHAR2(50) | NN | Yes | Legal last name. |
| MIDDLE_NAME | VARCHAR2(50) | — | Yes | Optional middle name. |
| DATE_OF_BIRTH | DATE | — | Yes | Used for age-related benefit eligibility. Not exposed in standard reports. |
| SSN | VARCHAR2(500) | — | Yes/ENC | Social Security Number. Stored as AES-256-CBC-PKCS5 ciphertext via PKG_SECURITY.encrypt_value. Decrypted only at point-of-use (benefits feed, tax reporting). |
| EMAIL | VARCHAR2(100) | UK | Yes | Corporate email. Used as notification recipient address. |
| PHONE | VARCHAR2(20) | — | Yes | Work or personal phone. SMS channel references this; handler not implemented. |
| ADDRESS_LINE1 | VARCHAR2(200) | — | Yes | Primary mailing address line 1. |
| ADDRESS_LINE2 | VARCHAR2(200) | — | Yes | Mailing address line 2 (suite, apt). |
| CITY | VARCHAR2(100) | — | Yes | City for state tax rate lookup. |
| STATE | VARCHAR2(2) | — | Yes | 2-char US state code. Drives flat-rate state income tax. |
| ZIP_CODE | VARCHAR2(10) | — | Yes | ZIP/postal code. |
| HIRE_DATE | DATE | NN | No | Date employee became active. Used in 3-part active filter. |
| TERMINATION_DATE | DATE | — | No | NULL while active. Set by PKG_EMPLOYEE.terminate_employee. |
| EMPLOYMENT_STATUS | VARCHAR2(20) | NN, CHK | No | Values: ACTIVE, TERMINATED, ON_LEAVE, SUSPENDED. Drives active filter. |
| JOB_TITLE | VARCHAR2(100) | — | No | Free-text job title (denormalised from JOB_POSITIONS). |
| DEPARTMENT_ID | NUMBER(10) | FK→DEPARTMENTS | No | Current department assignment. |
| MANAGER_ID | NUMBER(10) | FK→EMPLOYEES(self) | No | Direct manager employee ID. NULL for top of hierarchy. |
| GRADE | NUMBER(2) | NN | No | Compensation band and RBAC driver. Range 1–10. Grade ≥ 8 = full access. |
| BANK_ACCOUNT_NUMBER | VARCHAR2(500) | — | Yes/ENC | AES-256 encrypted bank account for direct deposit. No decryption procedure implemented. |
| BANK_ROUTING_NUMBER | VARCHAR2(500) | — | Yes/ENC | AES-256 encrypted routing number. Same gap as above. |
| MARITAL_STATUS | VARCHAR2(20) | — | No | Drives federal tax filing status in payroll calculation. |
| TAX_FILING_STATUS | VARCHAR2(30) | CHK | No | Values: SINGLE, MARRIED_FILING_JOINTLY, MARRIED_FILING_SEPARATELY, HEAD_OF_HOUSEHOLD. Critical: HOH branch returns $0 federal tax (defect). |
| EMERGENCY_CONTACT_NAME | VARCHAR2(100) | — | Yes | Next-of-kin name. |
| EMERGENCY_CONTACT_PHONE | VARCHAR2(20) | — | Yes | Next-of-kin phone. |
| TERMINATION_REASON | VARCHAR2(10) | FK→TERMINATION_CODES | No | Coded reason (VOLUNTARY, INVOLUNTARY, etc.). |
| ACTIVE_FLAG | VARCHAR2(1) | NN, CHK('Y','N') | No | Soft-delete flag. 'Y' for all records including terminated employees (history retention). |
| CREATED_DATE | DATE | NN | No | Row creation timestamp. |
| UPDATED_DATE | DATE | — | No | Last modification timestamp. Set by audit trigger. |
| UPDATED_BY | VARCHAR2(50) | — | No | Oracle session user who last modified the row. Set by audit trigger. |

---

## Table: DEPARTMENTS

Business meaning: Organisational unit registry. Used for cost-centre assignment, reporting hierarchy, and GL journal routing.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| DEPARTMENT_ID | NUMBER(10) | PK | No | Surrogate key. |
| DEPARTMENT_NAME | VARCHAR2(100) | NN, UK | No | Full department name. |
| DEPARTMENT_CODE | VARCHAR2(20) | UK | No | Short code used in GL journal cost-centre field. |
| PARENT_DEPARTMENT_ID | NUMBER(10) | FK→DEPARTMENTS(self) | No | Enables multi-level org hierarchy via CONNECT BY. Degrades >500 employees. |
| MANAGER_ID | NUMBER(10) | FK→EMPLOYEES | No | Department head employee ID. |
| COST_CENTER | VARCHAR2(20) | — | No | Accounting cost-centre code passed to Oracle Financials GL feed. |
| ACTIVE_FLAG | VARCHAR2(1) | CHK('Y','N') | No | Soft-delete. |
| CREATED_DATE | DATE | NN | No | Creation timestamp. |

---

## Table: JOB_POSITIONS

Business meaning: Job catalogue defining grade ranges and titles. Referenced at hire and transfer.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| POSITION_ID | NUMBER(10) | PK | No | Surrogate key. |
| POSITION_TITLE | VARCHAR2(100) | NN | No | Canonical job title. |
| POSITION_CODE | VARCHAR2(20) | UK | No | Short code. |
| MIN_GRADE | NUMBER(2) | NN | No | Minimum grade allowed for this position. |
| MAX_GRADE | NUMBER(2) | NN | No | Maximum grade allowed for this position. |
| DEPARTMENT_ID | NUMBER(10) | FK→DEPARTMENTS | No | Owning department (optional association). |
| ACTIVE_FLAG | VARCHAR2(1) | CHK | No | Soft-delete. |

---

## Table: SALARY_RECORDS

Business meaning: Point-in-time salary history. One row per salary change event per employee. Current salary = MAX(EFFECTIVE_DATE) row where END_DATE IS NULL.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| SALARY_ID | NUMBER(10) | PK | No | Surrogate key. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Employee receiving salary. |
| BASE_SALARY | NUMBER(12,2) | NN | No | Annual base salary in USD. Divided by 12 for monthly gross. |
| EFFECTIVE_DATE | DATE | NN | No | Date this salary row became active. |
| END_DATE | DATE | — | No | NULL = currently active row. Set when superseded. |
| SALARY_TYPE | VARCHAR2(20) | CHK | No | Values: MONTHLY, HOURLY, CONTRACT. Payroll calculation logic varies by type. |
| CHANGE_REASON | VARCHAR2(200) | — | No | Free-text reason for salary change (promotion, merit, correction). |
| APPROVED_BY | NUMBER(10) | FK→EMPLOYEES | No | Approving manager. |
| CREATED_DATE | DATE | NN | No | Audit timestamp. |

---

## Table: PAYROLL_RUNS

Business meaning: Header record for each payroll execution cycle. One row per pay period.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| RUN_ID | NUMBER(10) | PK | No | Surrogate key. |
| RUN_NAME | VARCHAR2(100) | NN | No | Human label e.g. "PAYROLL_2024_01". |
| PAY_PERIOD_START | DATE | NN | No | First day of pay period. |
| PAY_PERIOD_END | DATE | NN | No | Last day of pay period. |
| RUN_DATE | DATE | NN | No | Date payroll was processed. |
| STATUS | VARCHAR2(20) | CHK | No | DRAFT / CALCULATED / APPROVED / GL_GENERATED / COMPLETED. |
| TOTAL_GROSS | NUMBER(15,2) | — | No | Sum of all employee gross pay for this run. |
| TOTAL_NET | NUMBER(15,2) | — | No | Sum of all employee net pay. |
| TOTAL_DEDUCTIONS | NUMBER(15,2) | — | No | Sum of all deductions. |
| CALCULATED_DATE | DATE | — | No | Timestamp when STATUS moved to CALCULATED. |
| APPROVED_BY | NUMBER(10) | FK→EMPLOYEES | No | HR Manager who approved. |
| APPROVED_DATE | DATE | — | No | Approval timestamp. |
| CREATED_BY | NUMBER(10) | FK→EMPLOYEES | No | User who initiated the run. |
| CREATED_DATE | DATE | NN | No | Creation timestamp. |
| GL_FEED_SENT_DATE | DATE | — | No | [GAP-FILLED] Timestamp when the GL journal file was successfully written and handed off to Oracle Financials. NULL until `PKG_INTEGRATION.generate_gl_journal` completes. Required for GL reconciliation audit trail. Currently absent from the schema — no procedure writes this value (confirmed: BR-GL-80; see also BC-02 event table and BC-09 event table in CANONICAL_ENTERPRISE_MODEL). |

---

## Table: PAYROLL_DETAILS

Business meaning: Line-item breakdown of every pay element for each employee in a payroll run. One row per (run, employee, pay element).

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| DETAIL_ID | NUMBER(10) | PK | No | Surrogate key. |
| RUN_ID | NUMBER(10) | FK→PAYROLL_RUNS, NN | No | Parent payroll run. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Employee this line applies to. |
| ELEMENT_ID | NUMBER(10) | FK→PAY_ELEMENTS (inferred) | No | Pay element type. Known values: 100=BASE_PAY, 200=FEDERAL_TAX, 210=STATE_TAX, 220=SOCIAL_SECURITY, 230=MEDICARE. |
| ELEMENT_NAME | VARCHAR2(50) | — | No | Denormalised element name (string copy at time of run). |
| AMOUNT | NUMBER(12,2) | NN | No | Positive = earnings; negative convention not confirmed for deductions. |
| CREATED_DATE | DATE | NN | No | Insert timestamp. |

---

## Table: DEDUCTION_RECORDS

Business meaning: Per-employee standing deduction configuration. Drives pre-tax and post-tax deduction amounts in payroll calculation.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| DEDUCTION_ID | NUMBER(10) | PK | No | Surrogate key. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Employee record. |
| DEDUCTION_TYPE | VARCHAR2(50) | NN | No | E.g. 401K, MEDICAL, DENTAL, VISION, HSA, ROTH_401K, GARNISHMENT. |
| AMOUNT | NUMBER(10,2) | NN | No | Per-period deduction amount. |
| IS_PRETAX | VARCHAR2(1) | CHK('Y','N') | No | Drives whether deducted before or after taxable gross. |
| EFFECTIVE_DATE | DATE | NN | No | Start of deduction. |
| END_DATE | DATE | — | No | NULL = active. |
| CREATED_DATE | DATE | — | No | Audit timestamp. |

---

## Table: LEAVE_TYPES

Business meaning: Leave type catalogue (Annual, Sick, Parental, etc.) with accrual configuration.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| LEAVE_TYPE_ID | NUMBER(10) | PK | No | Surrogate key. |
| LEAVE_TYPE_NAME | VARCHAR2(50) | NN, UK | No | Display name. |
| ACCRUAL_RATE | NUMBER(5,2) | — | No | Days accrued per month. Used by PKG_LEAVE.accrue_leave. |
| MAX_BALANCE | NUMBER(5,2) | — | No | Cap on accrued balance. NULL = uncapped. |
| IS_PAID | VARCHAR2(1) | CHK | No | 'Y' = paid leave; drives final-pay PTO payout (not yet implemented). |
| CARRY_FORWARD | VARCHAR2(1) | CHK | No | 'Y' = balance carries to next year. Logic not yet implemented. |
| ACTIVE_FLAG | VARCHAR2(1) | CHK | No | Soft-delete. |

---

## Table: LEAVE_BALANCES

Business meaning: Running balance of leave for each employee per leave type per calendar year.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| BALANCE_ID | NUMBER(10) | PK | No | Surrogate key. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Employee. |
| LEAVE_TYPE_ID | NUMBER(10) | FK→LEAVE_TYPES, NN | No | Leave type. |
| LEAVE_YEAR | NUMBER(4) | NN | No | Calendar year. |
| OPENING_BALANCE | NUMBER(5,2) | NN | No | Balance at start of year. |
| ACCRUED | NUMBER(5,2) | NN, default 0 | No | Days accrued to date this year. |
| USED | NUMBER(5,2) | NN, default 0 | No | Days taken (approved and completed). |
| PENDING | NUMBER(5,2) | NN, default 0 | No | Days approved but not yet taken. |
| ADJUSTMENT | NUMBER(5,2) | default 0 | No | Manual HR adjustment (positive or negative). |
| AVAILABLE | NUMBER(5,2) | VIR | No | OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING. Virtual column; read-only. |
| UPDATED_DATE | DATE | — | No | Last update timestamp. |

---

## Table: LEAVE_REQUESTS

Business meaning: Individual leave application record. Tracks application-to-completion lifecycle.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| REQUEST_ID | NUMBER(10) | PK | No | Surrogate key. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Requesting employee. |
| LEAVE_TYPE_ID | NUMBER(10) | FK→LEAVE_TYPES, NN | No | Type of leave requested. |
| START_DATE | DATE | NN | No | First day of requested leave. |
| END_DATE | DATE | NN | No | Last day. |
| DAYS_REQUESTED | NUMBER(5,2) | NN | No | Computed at apply time. No half-day validation — whole integers only in practice. |
| STATUS | VARCHAR2(20) | CHK | No | PENDING / APPROVED / REJECTED / CANCELLED / TAKEN. |
| REASON | VARCHAR2(500) | — | No | Employee-provided reason. |
| APPLIED_DATE | DATE | NN | No | Date request submitted. |
| APPROVED_BY | NUMBER(10) | FK→EMPLOYEES | No | Manager who approved/rejected. |
| APPROVED_DATE | DATE | — | No | Approval timestamp. |
| REJECTION_REASON | VARCHAR2(500) | — | No | Free-text if rejected. |

---

## Table: PERFORMANCE_REVIEWS

Business meaning: Individual performance review record. One row per (employee, review cycle).

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| REVIEW_ID | NUMBER(10) | PK | No | Surrogate key. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Employee being reviewed. |
| CYCLE_ID | NUMBER(10) | FK→REVIEW_CYCLES, NN | No | Parent review cycle. |
| SELF_RATING | NUMBER(2,1) | CHK(1–5) | No | Employee self-assessment rating. |
| SELF_COMMENTS | VARCHAR2(4000) | — | No | Narrative self-assessment. |
| MANAGER_RATING | NUMBER(2,1) | CHK(1–5) | No | Manager's rating. |
| MANAGER_COMMENTS | VARCHAR2(4000) | — | No | Manager's narrative. |
| OVERALL_RATING | NUMBER(2,1) | CHK(1–5), NN | No | Final rating used for merit eligibility (≥ 3 required). |
| CALIBRATED_RATING | NUMBER(2,1) | — | No | Post-calibration rating. No write procedure exists. Currently always NULL. |
| CALIBRATION_NOTES | VARCHAR2(500) | — | No | Calibration discussion notes. Same gap. |
| REVIEW_STATUS | VARCHAR2(20) | CHK | No | PENDING / SELF_COMPLETE / MANAGER_COMPLETE / CALIBRATED / FINAL. |
| REVIEWED_DATE | DATE | — | No | Date manager completed review. |
| CREATED_DATE | DATE | NN | No | Row creation timestamp. |

---

## Table: REVIEW_CYCLES

Business meaning: Umbrella record for an annual or periodic review programme. Employees are reviewed within a cycle.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| CYCLE_ID | NUMBER(10) | PK | No | Surrogate key. |
| CYCLE_NAME | VARCHAR2(100) | NN | No | E.g. "2024 Annual Review". |
| REVIEW_YEAR | NUMBER(4) | NN | No | Calendar year. |
| START_DATE | DATE | NN | No | Cycle open date. |
| END_DATE | DATE | NN | No | Cycle close date. |
| STATUS | VARCHAR2(20) | CHK | No | OPEN / UNDER_REVIEW / CALIBRATING / CLOSED. |
| CLOSE_DATE | DATE | — | No | Actual close timestamp. |
| CREATED_BY | NUMBER(10) | FK→EMPLOYEES | No | HR Admin who created cycle. |
| CREATED_DATE | DATE | NN | No | Audit timestamp. |

---

## Table: PERFORMANCE_GOALS

Business meaning: Individual goals attached to employees. Can be linked to a review cycle.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| GOAL_ID | NUMBER(10) | PK | No | Surrogate key. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Owner of goal. |
| GOAL_TITLE | VARCHAR2(200) | NN | No | Short goal name. |
| GOAL_DESCRIPTION | VARCHAR2(4000) | — | No | Full description. |
| TARGET_DATE | DATE | — | No | Intended completion date. |
| COMPLETION_PERCENTAGE | NUMBER(3) | CHK(0–100) | No | Free-entry completion; not milestone-driven. |
| STATUS | VARCHAR2(20) | CHK | No | ACTIVE / COMPLETED / CANCELLED. |
| CREATED_DATE | DATE | NN | No | Audit timestamp. |

---

## Table: GOAL_REVIEWS

Business meaning: Pivot table linking performance goals to review cycles. Allows a goal to be assessed across multiple cycles.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| GOAL_REVIEW_ID | NUMBER(10) | PK | No | Surrogate key. |
| GOAL_ID | NUMBER(10) | FK→PERFORMANCE_GOALS | No | Goal being assessed. |
| CYCLE_ID | NUMBER(10) | FK→REVIEW_CYCLES | No | Review cycle. |
| REVIEW_COMMENTS | VARCHAR2(2000) | — | No | Cycle-specific assessment of goal progress. |
| CREATED_DATE | DATE | NN | No | Audit timestamp. |

---

## Table: BENEFIT_PLANS

Business meaning: Catalogue of available benefit plans (medical, dental, vision, 401k, etc.).

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| PLAN_ID | NUMBER(10) | PK | No | Surrogate key. |
| PLAN_CODE | VARCHAR2(20) | UK, NN | No | Short code sent to ADP in fixed-width feed (positions 105–110). |
| PLAN_NAME | VARCHAR2(100) | NN | No | Display name. |
| PLAN_TYPE | VARCHAR2(50) | — | No | MEDICAL / DENTAL / VISION / RETIREMENT / HSA. |
| CARRIER | VARCHAR2(100) | — | No | Insurance carrier name. |
| EFFECTIVE_DATE | DATE | NN | No | Plan availability start. |
| END_DATE | DATE | — | No | NULL = still available. |
| ACTIVE_FLAG | VARCHAR2(1) | CHK | No | Soft-delete. |

---

## Table: BENEFIT_ENROLLMENTS

Business meaning: Employee-to-plan enrollment records. Drives ADP benefits feed extraction.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| ENROLLMENT_ID | NUMBER(10) | PK | No | Surrogate key. |
| EMPLOYEE_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Enrolled employee. |
| PLAN_ID | NUMBER(10) | FK→BENEFIT_PLANS, NN | No | Plan enrolled in. |
| COVERAGE_TIER | VARCHAR2(30) | — | No | EMPLOYEE_ONLY / EMPLOYEE_SPOUSE / FAMILY. Sent to ADP at positions 111–120. |
| ENROLLMENT_STATUS | VARCHAR2(20) | CHK | No | ENROLLED / TERMINATED / PENDING. |
| EFFECTIVE_DATE | DATE | NN | No | Enrollment start date. Sent to ADP at positions 121–130. |
| END_DATE | DATE | — | No | Enrollment end date. NULL = active. |
| CREATED_DATE | DATE | NN | No | Audit timestamp. |

---

## Table: USER_SESSIONS (TBL-022)

**[GAP-FILLED]** Table DDL not found in deep scan (`plsql/jobs/session_cleanup_job.sql` not found; `plsql/schema/scheduler_jobs.sql` not found). Column catalogue recovered from `PKG_SECURITY.pkb`: `INSERT` statement in `authenticate` confirms SESSION_ID, EMP_ID, USERNAME, LOGIN_TIME, IP_ADDRESS, SESSION_STATUS, CREATED_DATE; `UPDATE` statements in `logout` and `is_session_valid` confirm LOGOUT_TIME and SESSION_STATUS values CLOSED/EXPIRED. Sequence confirmed: SEQ_USER_SESSION.NEXTVAL.

Business meaning: Server-side session store for all authenticated HRMS users. One row is inserted per successful login event. Session validity (30-minute timeout) is checked lazily — only when `PKG_SECURITY.is_session_valid` is next called for that session. Sessions opened by terminated employees remain STATUS = ACTIVE for up to 30 minutes after termination because `PKG_EMPLOYEE.terminate_employee` does not touch this table. No background sweep job removes stale rows; the table accumulates indefinitely (gap evidence: TD-75, GAP-O-11 in `02_BUSINESS_CAPABILITY_MODEL.md`, BR-008 in `01_BRD.md`, REC-S07 in `07_DATA_MODEL_SPECIFICATION.md`).

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| SESSION_ID | NUMBER(15) | PK | No | **[GAP-FILLED]** Surrogate key. Source: SEQ_USER_SESSION.NEXTVAL (confirmed via `PKG_SECURITY.authenticate`). Returned to the caller as the opaque session token; passed back on every subsequent API call. |
| EMP_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | **[GAP-FILLED]** Authenticated employee. Resolved via EMPLOYEES.EMAIL = p_username lookup in `authenticate`. |
| USERNAME | VARCHAR2(100) | NN | Yes | **[GAP-FILLED]** Email address supplied at login (mirrors EMPLOYEES.EMAIL). Denormalised into the session row for audit forensics so the audit trail survives an email change on the EMPLOYEES record. |
| LOGIN_TIME | DATE | NN | No | **[GAP-FILLED]** Timestamp of successful authentication (set to SYSDATE in `authenticate`). Used by `is_session_valid` to calculate elapsed minutes against the hard-coded 30-minute constant `c_session_timeout_min`. Not driven by SYSTEM_PARAMETERS — the parameter table row for SESSION_TIMEOUT_MINUTES is non-functional (DQ-027 in `07_DATA_MODEL_SPECIFICATION.md`). |
| LOGOUT_TIME | DATE | — | No | **[GAP-FILLED]** Null on insert. Set to SYSDATE by `logout` (STATUS → CLOSED) or by `is_session_valid` on timeout detection (STATUS → EXPIRED). Remains NULL for any session that is abandoned without an explicit logout and never polled again — which is the common browser-close scenario. |
| IP_ADDRESS | VARCHAR2(45) | — | Yes | **[GAP-FILLED]** Client IP address at login time (accepts IPv4 or IPv6 string; 45 chars covers full IPv6 notation). Passed as p_ip_address DEFAULT NULL in `authenticate`. PII — retained for 90 days per data-retention policy (`07_DATA_MODEL_SPECIFICATION.md` §retention, `09_DATA_FLOW_DIAGRAM.md` §data-at-rest). |
| SESSION_STATUS | VARCHAR2(20) | CHK | No | **[GAP-FILLED]** Confirmed values: ACTIVE (set on insert), CLOSED (set by `logout`), EXPIRED (set by `is_session_valid` on timeout). Values are not normalised via LOOKUP_VALUES. No DDL CHECK constraint text recovered, but the three string literals are the only values written by `PKG_SECURITY`. No trigger or background job transitions ACTIVE rows to EXPIRED; a session remains ACTIVE in the table until the next `is_session_valid` call for that specific SESSION_ID. |
| CREATED_DATE | DATE | NN | No | **[GAP-FILLED]** Row insert timestamp (set to SYSDATE in `authenticate`, same instant as LOGIN_TIME in current implementation). |

**[GAP-FILLED] Missing background cleanup job — HRMS_SESSION_CLEANUP:** No `DBMS_SCHEDULER` or `DBMS_JOB` definition was found anywhere in the source tree. `plsql/jobs/session_cleanup_job.sql` was not found in the deep scan; `plsql/schema/scheduler_jobs.sql` was not found. Consequence: USER_SESSIONS rows with SESSION_STATUS = 'ACTIVE' are never swept by a background process. The table grows without bound. A terminated employee's session tokens remain technically valid for up to 30 minutes post-termination and no automated mechanism closes them sooner. BR-008 in `01_BRD.md` requires a job named `HRMS_SESSION_CLEANUP` running every 5 minutes to expire rows where `LOGIN_TIME < SYSDATE - INTERVAL '30' MINUTE AND SESSION_STATUS = 'ACTIVE'`; that job is entirely absent from the confirmed source. REC-S07 in `07_DATA_MODEL_SPECIFICATION.md` (Medium priority) and GAP-O-11 in `02_BUSINESS_CAPABILITY_MODEL.md` independently document the same gap. The job must be created as part of schema deployment. Cross-references: BR-008, TD-75, GAP-O-11, L2-06-02, DQ-027, REC-S07.

---

## Table: NOTIFICATION_QUEUE

**[GAP-FILLED] Architecture correction:** The data dictionary entry below reflects the *intended* design (template + payload pattern). The confirmed DDL (`schema/tables/04_performance_tables.sql`, lines 129–148) and the implemented package body (`PKG_NOTIFICATION.pkb`) reveal a materially different *as-built* schema. The actual table carries no `TEMPLATE_ID`, no `PAYLOAD`, and no `RECIPIENT_ID` column. The as-built columns are: `NOTIFICATION_ID`, `RECIPIENT_EMP_ID`, `RECIPIENT_EMAIL`, `NOTIFICATION_TYPE`, `SUBJECT`, `BODY CLOB NOT NULL`, `STATUS`, `PRIORITY`, `SENT_DATE`, `ERROR_MESSAGE`, `RETRY_COUNT`, `REFERENCE_TABLE`, `REFERENCE_ID`, `CREATED_BY`, `CREATED_DATE`. The as-built dispatch procedure (`PKG_NOTIFICATION.send_notification`) accepts a fully-rendered `p_body IN CLOB`; all callers (PKG_EMPLOYEE, PKG_LEAVE, PKG_PERFORMANCE) construct the message body inline via PL/SQL string concatenation before the call. No template-merge step exists at runtime.

Business meaning: Outbox for all system-generated notifications. Read by PKG_NOTIFICATION.process_notification_queue.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| NOTIFICATION_ID | NUMBER(10) | PK | No | Surrogate key. |
| RECIPIENT_ID | NUMBER(10) | FK→EMPLOYEES | No | Target employee. |
| TEMPLATE_ID | NUMBER(10) | FK→NOTIFICATION_TEMPLATES | No | Message template. |
| CHANNEL | VARCHAR2(20) | CHK | No | EMAIL / SMS / IN_APP. SMS and IN_APP handlers not implemented. |
| STATUS | VARCHAR2(20) | CHK | No | PENDING / SENT / FAILED. No retry logic. |
| PAYLOAD | CLOB | — | No | **[GAP-FILLED]** This column does not exist in the confirmed DDL (`04_performance_tables.sql` lines 129–148). The as-built table uses a pre-rendered `BODY CLOB NOT NULL` column instead. No PAYLOAD column, no TEMPLATE_ID column, and no template-merge step are present in the implemented schema. The description "JSON key-value pairs merged into template at dispatch time" reflects design intent only — it was never implemented. Callers pass a fully-composed body string to `PKG_NOTIFICATION.send_notification(p_body IN CLOB)` directly. `NOTIFICATION_PAYLOAD_T.sql` was not found in the deep scan, consistent with the type never having been created. |
| CREATED_DATE | DATE | NN | No | Enqueue timestamp. |
| SENT_DATE | DATE | — | No | Set on successful dispatch. |
| ERROR_MESSAGE | VARCHAR2(4000) | — | No | SQLERRM captured on failure. |

---

## Table: NOTIFICATION_TEMPLATES

**[GAP-FILLED]** `notification_templates.sql` was not found in the deep scan, and no DDL for this table exists in the confirmed source. The table is referenced as a foreign key target by the intended design of `NOTIFICATION_QUEUE.TEMPLATE_ID`, but that FK column itself is absent from the as-built DDL. The template-based notification architecture (TEMPLATE_CODE, placeholder tokens, PAYLOAD merge) was not implemented; `PKG_NOTIFICATION.pkb` contains a hard-coded note that "HTML email templates [are] stored as string constants (maintenance nightmare)", confirming templates were inlined into package source rather than stored in a database table. The column catalogue below cannot be populated from available source and should be treated as unimplemented design intent.

Business meaning: Message templates for all notification types. Placeholders merged with PAYLOAD at dispatch. **[GAP-FILLED]** As-built: this table does not exist. Template bodies are string constants embedded in the calling packages (PKG_EMPLOYEE, PKG_LEAVE, PKG_PERFORMANCE). No TEMPLATE_CODE catalogue, no per-template token inventory, and no dispatch-time merge procedure have been found in the source.

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| TEMPLATE_ID | NUMBER(10) | PK | No | **[GAP-FILLED]** Column definition not recoverable — DDL source not found. |

---

## Table: EMPLOYEE_DEPENDENTS (TBL-019)

Business meaning: Records dependents (spouse, child, parent, domestic partner, other) covered under an employee's benefit plans. Each row is a named third-party data subject. The table feeds the ADP benefits integration via `PKG_INTEGRATION.generate_benefits_file`, which includes dependent rows whose `ACTIVE_FLAG = 'Y'` for all currently ACTIVE employees. Two structural gaps are present: (1) the `BENEFITS_ENROLLED` flag is stored but never enforced or acted upon by any procedure; (2) the termination flow does not touch this table, leaving dependent rows in their pre-termination state after an employee is terminated.

DDL source: `schema/tables/01_core_tables.sql` lines 182–199 (confirmed).

| Column | Type | Constraints | PII | Business Meaning |
|--------|------|-------------|-----|-----------------|
| DEPENDENT_ID | NUMBER(10) | PK, NN | No | Surrogate key. Source: SEQ_DEPENDENT.NEXTVAL. |
| EMP_ID | NUMBER(10) | FK→EMPLOYEES, NN | No | Parent employee. FK_DEP_EMP with ON DELETE NO ACTION — deletion of the parent employee row is blocked if dependents exist. |
| FIRST_NAME | VARCHAR2(50) | NN | Yes | Dependent's legal first name. Third-party data subject. |
| LAST_NAME | VARCHAR2(50) | NN | Yes | Dependent's legal last name. Third-party data subject. |
| RELATIONSHIP | VARCHAR2(20) | NN, CHK_RELATIONSHIP | No | Values: SPOUSE / CHILD / PARENT / DOMESTIC_PARTNER / OTHER. Confirmed via `CHK_RELATIONSHIP` in DDL source line 198. Cross-references BR-120 in `BA_Deep_Analyst_FINAL.md`. |
| DATE_OF_BIRTH | DATE | — | Yes | PII — intended for benefits age-gating (e.g. child age-out rules). No procedure performs age-gate validation against this column in the confirmed source. |
| SSN_ENCRYPTED | VARCHAR2(200) | — | Yes/ENC | AES-256 encrypted Social Security Number of the dependent. Uses the same hard-coded key constant as EMPLOYEES.SSN_ENCRYPTED (PKG_SECURITY — PP-06 in BA analysis). No decryption procedure for dependents was found in the confirmed source. |
| BENEFITS_ENROLLED | CHAR(1) | — (nullable, default 'N') | No | **[GAP-FILLED] Flag without enforcement:** Y = this dependent is enrolled in active benefits; N = not enrolled (default). This column is present in the confirmed DDL (`01_core_tables.sql` line 190) and in `da-outputs/schema-catalogue.json`. No procedure in any confirmed package (PKG_EMPLOYEE, PKG_INTEGRATION, PKG_PAYROLL, PKG_SECURITY, PKG_NOTIFICATION, PKG_COMMON, PKG_AUDIT) reads this flag to gate, validate, or act upon it. `PKG_INTEGRATION.generate_benefits_file` (the ADP feed) selects dependent rows solely on `ACTIVE_FLAG = 'Y'` — it does not filter on `BENEFITS_ENROLLED`. The flag is therefore collected but entirely unenforced. A dependent with `BENEFITS_ENROLLED = 'N'` would still be sent to ADP as long as `ACTIVE_FLAG = 'Y'`. Forward engineering must decide: either enforce this flag as the ADP inclusion gate (and backfill existing rows) or remove it as misleading dead data. |
| ACTIVE_FLAG | CHAR(1) | NN, default 'Y' | No | Soft-delete flag. 'Y' = dependent is active and will be included in the ADP benefits feed. 'N' = logically deleted. `PKG_INTEGRATION.generate_benefits_file` filters on `ACTIVE_FLAG = 'Y'` (confirmed: `PKG_INTEGRATION.pkb` line 124). |
| CREATED_BY | VARCHAR2(30) | NN | No | Oracle session user who inserted the row. |
| CREATED_DATE | DATE | NN, default SYSDATE | No | Row creation timestamp. |
| MODIFIED_BY | VARCHAR2(30) | — | No | Oracle session user who last modified the row. |
| MODIFIED_DATE | DATE | — | No | Last modification timestamp. |

**[GAP-FILLED] Missing cascade-close logic on termination:** `PKG_EMPLOYEE.terminate_employee` (confirmed source: `PKG_EMPLOYEE.pkb` lines 681–786) executes the following UPDATE statements in sequence: LEAVE_REQUESTS (cancel PENDING), EMPLOYEES (set TERMINATED/ACTIVE_FLAG='N'), SALARY_RECORDS (end-date active rows), EMPLOYEE_PAY_ELEMENTS (end-date active rows). It does not issue any UPDATE or write to EMPLOYEE_DEPENDENTS. After termination, every dependent row for the terminated employee remains with its pre-termination `ACTIVE_FLAG` and `BENEFITS_ENROLLED` values unchanged. Practical consequences:

1. **ADP over-reporting:** The next `generate_benefits_file` run selects dependents via `LEFT JOIN EMPLOYEE_DEPENDENTS d ON e.EMP_ID = d.EMP_ID AND d.ACTIVE_FLAG = 'Y'` filtered to `e.EMPLOYMENT_STATUS = 'ACTIVE'`. The parent employee filter (`EMPLOYMENT_STATUS = 'ACTIVE'`) will correctly exclude the terminated employee's row from the feed — so ADP will not receive the terminated employee's record. However, if the `EMPLOYEES.ACTIVE_FLAG` filter is ever relaxed or a report queries EMPLOYEE_DEPENDENTS directly without joining to EMPLOYEES, terminated-employee dependents remain silently visible with `ACTIVE_FLAG = 'Y'`.

2. **No COBRA trigger path:** The `terminate_employee` procedure includes a `-- TODO: Integrate with benefits system to trigger COBRA` comment (line 778) but no dependent close-out has been implemented. Forward engineering must add: `UPDATE EMPLOYEE_DEPENDENTS SET ACTIVE_FLAG = 'N', BENEFITS_ENROLLED = 'N', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y'` as part of the termination transaction, alongside the COBRA notification hook.

3. **No procedure for BENEFITS_ENROLLED enforcement:** No `validate_dependent_enrollment`, `enroll_dependent`, or equivalent procedure was found in any package. The flag can only be set via direct DML against the table; there is no business-logic layer managing its lifecycle.

Cross-references: BR-22/BR-23/BR-24 (termination rules, `BA_Deep_Analyst_FINAL.md`); PP-03 (COBRA not implemented); `PKG_EMPLOYEE.pkb` lines 778–780 (TODO comments); `PKG_INTEGRATION.pkb` lines 119–128 (ADP feed query).
