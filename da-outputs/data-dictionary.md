# HRMS Data Dictionary

**Schema:** HRMS  **DB:** Oracle 19c  **Extracted:** 2026-08-04  
**Method:** CODE-ONLY

---

## How to Read This Dictionary

Each table section lists:
- **Purpose:** Business meaning of the table
- **Key columns:** Business-significant columns (PK/FK/constrained columns; audit columns omitted for readability)
- **Business rules captured here:** Rules enforced by this table's DDL or triggers

Audit columns (`CREATED_BY`, `CREATED_DATE`, `MODIFIED_BY`, `MODIFIED_DATE`) are present on all tables unless noted; not repeated in each section.

---

## EMPLOYEES — Master Employee Record

**Purpose:** Central entity. Stores all HR-relevant information about every person employed (past or present). Physical deletes are blocked; terminated employees remain with `EMPLOYMENT_STATUS='TERMINATED'` and `ACTIVE_FLAG='N'`.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| EMP_ID | NUMBER(10) PK | Surrogate key (SEQ_EMPLOYEE) |
| EMP_NUMBER | VARCHAR2(20) UNIQUE | Human-facing business key, format EMP-NNNNNN |
| FIRST_NAME | VARCHAR2(50) NOT NULL | Stored uppercase-trimmed |
| MIDDLE_NAME | VARCHAR2(50) | Optional middle name |
| LAST_NAME | VARCHAR2(50) NOT NULL | Stored uppercase-trimmed |
| DATE_OF_BIRTH | DATE | Used for benefits eligibility; PII |
| GENDER | CHAR(1) | M/F/O — EEOC reporting |
| MARITAL_STATUS | VARCHAR2(10) | Affects tax filing status defaulting |
| NATIONALITY | VARCHAR2(50) | I-9 eligibility documentation |
| SSN_ENCRYPTED | VARCHAR2(200) | AES-256-CBC encrypted Social Security Number; decrypted only by PKG_SECURITY.decrypt_ssn |
| EMAIL | VARCHAR2(100) | Stored lowercase-trimmed; doubles as login username; unique among active employees |
| PHONE_WORK / PHONE_MOBILE | VARCHAR2(30) | Contact numbers |
| ADDRESS_LINE1-2, CITY, STATE_PROVINCE, POSTAL_CODE | VARCHAR2 | Home address; PII |
| COUNTRY_CODE | VARCHAR2(3) | ISO 3-char |
| HIRE_DATE | DATE NOT NULL | Cannot be more than 180 days future. Overwritten on rehire. |
| TERMINATION_DATE | DATE | Set on termination |
| TERMINATION_REASON | VARCHAR2(50) | VOLUNTARY used in turnover reports |
| DEPT_ID | NUMBER(10) FK→DEPARTMENTS | Current department assignment |
| JOB_ID | NUMBER(10) FK→JOB_TITLES | Current job title |
| MANAGER_EMP_ID | NUMBER(10) FK→EMPLOYEES | Direct manager; NULL = top of hierarchy |
| LOCATION_CODE | VARCHAR2(10) FK→LOCATIONS | Work location |
| EMPLOYMENT_TYPE | VARCHAR2(20) | FULL_TIME / PART_TIME / CONTRACT / INTERN |
| EMPLOYMENT_STATUS | VARCHAR2(20) | ACTIVE / ON_LEAVE / SUSPENDED / TERMINATED |
| PHOTO_BLOB | BLOB | Employee photo |
| NOTES | CLOB | Free-text HR notes — may contain sensitive information |
| ACTIVE_FLAG | CHAR(1) | Y = active; N = terminated/deactivated |

---

## DEPARTMENTS — Organizational Units

**Purpose:** Defines the company's organizational hierarchy. Departments are self-referencing (PARENT_DEPT_ID) to support unlimited hierarchy depth. Manager assignment is a soft reference — no FK to EMPLOYEES.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| DEPT_ID | NUMBER(10) PK | |
| DEPT_CODE | VARCHAR2(20) UNIQUE | Short code used in reporting |
| DEPT_NAME | VARCHAR2(100) | Full department name |
| PARENT_DEPT_ID | NUMBER(10) | Parent department for org chart (soft self-ref, no FK) |
| COST_CENTER | VARCHAR2(20) | GL integration code for journal entries |
| MANAGER_EMP_ID | NUMBER(10) | Department head (soft ref; not cleared on termination) |
| LOCATION_CODE | VARCHAR2(10) | Primary location (soft ref) |
| ACTIVE_FLAG | CHAR(1) | |

**Seed data:** 10 departments seeded. DEPT_ID values: 1 (EXEC — Executive), 10 (HR — Human Resources), 20 (FIN — Finance), 30 (IT — Information Technology), 31 (ITDEV — IT Development), 32 (ITOPS — IT Operations), 40 (SALES — Sales), 50 (MKT — Marketing), 60 (OPS — Operations), 70 (LEGAL — Legal). Note: "Customer Service" and "R&D" departments do not exist in this schema. *CORRECTED by DA Agent 2 — prior text stated DEPT_ID range 100-190 which is incorrect.*

---

## LOCATIONS — Physical Work Locations

**Purpose:** Defines offices and work sites. Used for holiday filtering (location-specific holidays) and employee assignment.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| LOCATION_CODE | VARCHAR2(10) PK | Natural key: HQ, CHI, SF |
| LOCATION_NAME | VARCHAR2(100) | |
| ADDRESS_LINE1-2, CITY, STATE_PROVINCE, POSTAL_CODE | VARCHAR2 | Physical address |
| COUNTRY_CODE | VARCHAR2(3) | ISO |
| TIMEZONE | VARCHAR2(50) | IANA timezone; default 'America/New_York' |
| ACTIVE_FLAG | CHAR(1) | |

**Seed data:** HQ (New York), CHI (Chicago), SF (San Francisco).

---

## JOB_GRADES — Compensation Bands and Permission Levels

**Purpose:** Defines salary bands and security permission levels. GRADE_ID is used by PKG_SECURITY.has_permission to determine access. Grades 1-10 where 8+ = Director/VP/C-Suite with full system access.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| GRADE_ID | NUMBER(5) PK | 1 = Entry Level, 10 = C-Suite |
| GRADE_CODE | VARCHAR2(10) UNIQUE | Short code |
| GRADE_NAME | VARCHAR2(50) | |
| MIN_SALARY | NUMBER(12,2) | Annual salary band floor |
| MAX_SALARY | NUMBER(12,2) | Annual salary band ceiling; must be ≥ MIN |
| OVERTIME_ELIGIBLE | CHAR(1) | Y/N — tied to FLSA status indirectly |

---

## JOB_TITLES — Job Roles

**Purpose:** Catalog of job roles in the organization. Each role is associated with a grade (determines compensation band and permissions).

| Column | Type | Business Meaning |
|--------|------|-----------------|
| JOB_ID | NUMBER(10) PK | |
| JOB_CODE | VARCHAR2(20) UNIQUE | |
| JOB_TITLE | VARCHAR2(100) | Display name |
| JOB_FAMILY | VARCHAR2(50) | Functional grouping (e.g. Engineering, Finance) |
| GRADE_ID | NUMBER(5) FK→JOB_GRADES | Determines compensation band and security permissions |
| EEO_CATEGORY | VARCHAR2(10) | EEOC category code for regulatory reporting |
| FLSA_STATUS | VARCHAR2(10) | EXEMPT (salaried) / NON-EXEMPT (hourly/overtime eligible) |

---

## EMPLOYEE_HISTORY — Employee Change Log

**Purpose:** Audit trail of all significant changes to an employee's record (transfers, promotions, salary changes, status changes). Written by TRG_EMP_BEFORE_UPDATE. **Known issue:** trigger column names do not match DDL — records may not be inserting correctly.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| HIST_ID | NUMBER(15) PK | |
| EMP_ID | NUMBER(10) FK→EMPLOYEES | |
| CHANGE_TYPE | VARCHAR2(30) | HIRE / TRANSFER / PROMOTION / DEMOTION / SALARY_CHANGE / TERMINATION / REHIRE / STATUS_CHANGE |
| EFFECTIVE_DATE | DATE | When the change took effect |
| OLD_DEPT_ID / NEW_DEPT_ID | NUMBER(10) | Before/after department |
| OLD_JOB_ID / NEW_JOB_ID | NUMBER(10) | Before/after job title |
| OLD_SALARY / NEW_SALARY | NUMBER(12,2) | Before/after salary |
| OLD_LOCATION / NEW_LOCATION | VARCHAR2(10) | Before/after location |
| REASON_CODE | VARCHAR2(30) | Reason for change |
| COMMENTS | VARCHAR2(4000) | Free-text notes |

---

## EMPLOYEE_DEPENDENTS — Dependent Persons

**Purpose:** Records dependents covered under employee benefits. Includes encrypted SSN for benefits enrollment with ADP.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| DEPENDENT_ID | NUMBER(10) PK | |
| EMP_ID | NUMBER(10) FK→EMPLOYEES | |
| FIRST_NAME / LAST_NAME | VARCHAR2(50) | PII — third-party data subject |
| RELATIONSHIP | VARCHAR2(20) | SPOUSE / CHILD / PARENT / DOMESTIC_PARTNER / OTHER |
| DATE_OF_BIRTH | DATE | PII — used for benefits age gating |
| SSN_ENCRYPTED | VARCHAR2(200) | AES-256 encrypted; same key as EMPLOYEES.SSN_ENCRYPTED |
| BENEFITS_ENROLLED | CHAR(1) | Y/N — whether this dependent is on active benefits |

---

## EMERGENCY_CONTACTS — Emergency Contact Persons

**Purpose:** Emergency contact information for employees. Third-party personal data.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| CONTACT_ID | NUMBER(10) PK | |
| EMP_ID | NUMBER(10) FK→EMPLOYEES | |
| CONTACT_NAME | VARCHAR2(100) | PII |
| RELATIONSHIP | VARCHAR2(30) | |
| PHONE_PRIMARY | VARCHAR2(30) | Required; PII |
| PHONE_SECONDARY / EMAIL | VARCHAR2 | Optional; PII |
| PRIORITY_ORDER | NUMBER(2) | 1 = highest priority (first to call) |

---

## SALARY_RECORDS — Salary History

**Purpose:** Full salary history maintained as dated ranges. Each salary change closes the prior record (END_DATE = new_date - 1) and inserts a new active row (END_DATE = NULL). Always stored as ANNUAL amount.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| SALARY_ID | NUMBER(10) PK | |
| EMP_ID | NUMBER(10) FK→EMPLOYEES | |
| EFFECTIVE_DATE | DATE NOT NULL | When this salary takes effect |
| END_DATE | DATE | NULL = currently active; set to new_effective-1 on change |
| BASE_SALARY | NUMBER(12,2) NOT NULL | Annual amount; must be > 0 |
| CURRENCY_CODE | VARCHAR2(3) | Default USD |
| PAY_FREQUENCY | VARCHAR2(20) | WEEKLY / BIWEEKLY / SEMIMONTHLY / MONTHLY |
| SALARY_BASIS | VARCHAR2(20) | Always ANNUAL (PKG_PAYROLL forces this) |
| CHANGE_REASON | VARCHAR2(50) | Reason code |
| CHANGE_PCT | NUMBER(5,2) | % change from prior salary |
| APPROVED_BY | NUMBER(10) | EMP_ID of approver (soft ref, no FK) |

---

## PAY_ELEMENTS — Payroll Component Catalog

**Purpose:** Master catalog of all pay components — earnings, deductions, taxes, benefits. Every PAYROLL_DETAILS row references an element here. Fixed IDs: 1=BASE_PAY, 100=FED_TAX, 101=STATE_TAX, 102=FICA, 103=MEDICARE.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| ELEMENT_ID | NUMBER(10) PK | |
| ELEMENT_CODE | VARCHAR2(30) UNIQUE | Business key |
| ELEMENT_NAME | VARCHAR2(100) | Display name |
| ELEMENT_TYPE | VARCHAR2(20) | EARNING / DEDUCTION / TAX / BENEFIT / REIMBURSEMENT |
| CALCULATION_TYPE | VARCHAR2(20) | FLAT / PERCENTAGE / HOURS / FORMULA |
| DEFAULT_AMOUNT | NUMBER(12,2) | Used if no per-employee override exists |
| DEFAULT_PERCENTAGE | NUMBER(5,2) | Used if CALCULATION_TYPE=PERCENTAGE |
| TAXABLE_FLAG | CHAR(1) | Y=taxable earning |
| PRETAX_FLAG | CHAR(1) | Y=applied before tax calculation (e.g. 401k) |
| EMPLOYER_PAID | CHAR(1) | Y=employer cost (not employee deduction) |
| GL_ACCOUNT_CODE | VARCHAR2(30) | Used by PKG_INTEGRATION for GL journal |
| PRIORITY_ORDER | NUMBER(5) | Processing order within payroll calc |

---

## EMPLOYEE_PAY_ELEMENTS — Per-Employee Pay Overrides

**Purpose:** Individual employee-level overrides for pay elements. Effective-dated to support historical tracking.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| EMP_ELEMENT_ID | NUMBER(10) PK | |
| EMP_ID | NUMBER(10) FK | |
| ELEMENT_ID | NUMBER(10) FK→PAY_ELEMENTS | |
| EFFECTIVE_DATE / END_DATE | DATE | Validity window; END_DATE=NULL = active |
| AMOUNT | NUMBER(12,2) | Override flat amount |
| PERCENTAGE | NUMBER(5,2) | Override percentage |
| OVERRIDE_AMOUNT | NUMBER(12,2) | Takes priority over AMOUNT and PERCENTAGE |

---

## PAY_PERIODS — Payroll Calendar

**Purpose:** Defines the pay calendar — each period has a start date, end date, and scheduled pay date.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| PERIOD_ID | NUMBER(10) PK | |
| PERIOD_NAME | VARCHAR2(50) | Human-readable e.g. '2024-01 (Jan)' |
| PAY_FREQUENCY | VARCHAR2(20) | MONTHLY / BIWEEKLY / etc. |
| PERIOD_START_DATE / PERIOD_END_DATE | DATE | Payroll period boundaries |
| PAY_DATE | DATE | Actual disbursement date; moved to preceding Friday if weekend |
| STATUS | VARCHAR2(20) | OPEN / PROCESSING / CLOSED / REVERSED |

---

## PAYROLL_RUNS — Payroll Execution Instances

**Purpose:** Tracks each execution of the payroll calculation. A period can have multiple runs (regular + supplemental).

| Column | Type | Business Meaning |
|--------|------|-----------------|
| RUN_ID | NUMBER(10) PK | |
| PERIOD_ID | NUMBER(10) FK→PAY_PERIODS | |
| RUN_TYPE | VARCHAR2(20) | REGULAR / SUPPLEMENTAL / BONUS / FINAL |
| RUN_DATE | DATE | When the run was executed |
| STATUS | VARCHAR2(20) | PENDING→CALCULATING→CALCULATED→APPROVED→PAID→REVERSED |
| TOTAL_GROSS / TOTAL_DEDUCTIONS / TOTAL_NET | NUMBER(15,2) | Aggregate run totals |
| EMPLOYEE_COUNT / ERROR_COUNT | NUMBER | Statistics |
| APPROVED_BY | VARCHAR2(30) | Username of approver (VARCHAR2 — inconsistent with SALARY_RECORDS) |

---

## PAYROLL_DETAILS — Per-Employee Per-Element Payroll Lines

**Purpose:** The detailed payroll calculation results. One row per employee per pay element per run. Positive amounts = earnings; negative = deductions/taxes.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| DETAIL_ID | NUMBER(15) PK | High-volume table |
| RUN_ID | NUMBER(10) FK→PAYROLL_RUNS | |
| EMP_ID | NUMBER(10) FK→EMPLOYEES | |
| ELEMENT_ID | NUMBER(10) FK→PAY_ELEMENTS | |
| ELEMENT_TYPE | VARCHAR2(20) | Denormalized copy from PAY_ELEMENTS at time of run |
| HOURS_WORKED | NUMBER(6,2) | For hourly elements |
| RATE | NUMBER(12,4) | Hourly/unit rate |
| AMOUNT | NUMBER(12,2) | Calculated amount (positive=earning, negative=deduction) |
| YTD_AMOUNT | NUMBER(15,2) | Year-to-date total — currently hard-coded 0 (unimplemented) |

---

## TAX_BRACKETS — Annual Tax Rate Tables

**Purpose:** Intended to store federal and state tax brackets by year and filing status. Currently unused — PKG_PAYROLL hard-codes 2024 brackets instead.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| BRACKET_ID | NUMBER(10) PK | |
| TAX_YEAR | NUMBER(4) | Calendar year |
| FILING_STATUS | VARCHAR2(30) | SINGLE / MARRIED_JOINT / MARRIED_SEPARATE / HEAD_OF_HOUSEHOLD |
| BRACKET_MIN / BRACKET_MAX | NUMBER(12,2) | Income range; MAX=NULL for top bracket |
| TAX_RATE | NUMBER(5,4) | Marginal rate as decimal (0.2200 = 22%) |
| BASE_TAX | NUMBER(12,2) | Cumulative tax at bracket floor |
| STATE_CODE | VARCHAR2(3) | NULL = federal; state code = state bracket |

---

## EMPLOYEE_TAX_INFO — W-4 Tax Elections

**Purpose:** Stores employee W-4 withholding elections per tax year.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| TAX_INFO_ID | NUMBER(10) PK | |
| EMP_ID | NUMBER(10) FK | |
| TAX_YEAR | NUMBER(4) | Unique per (EMP_ID, TAX_YEAR) |
| FILING_STATUS | VARCHAR2(30) | From W-4 |
| FEDERAL_ALLOWANCES / STATE_ALLOWANCES | NUMBER(3) | W-4 allowances |
| ADDITIONAL_FED_WH / ADDITIONAL_STATE_WH | NUMBER(12,2) | Extra per-period withholding |
| EXEMPT_FLAG | CHAR(1) | Y = employee claims tax exemption |
| W4_RECEIVED_DATE | DATE | Date W-4 form was received |

---

## EMPLOYEE_BANK_ACCOUNTS — Direct Deposit Accounts

**Purpose:** Bank accounts for direct deposit. Supports split-deposit (multiple accounts with priority ordering).

| Column | Type | Business Meaning |
|--------|------|-----------------|
| BANK_ACCT_ID | NUMBER(10) PK | |
| EMP_ID | NUMBER(10) FK | |
| BANK_NAME | VARCHAR2(100) | |
| ROUTING_NUMBER | VARCHAR2(20) | Bank routing number — stored PLAIN TEXT |
| ACCOUNT_NUMBER_ENC | VARCHAR2(200) | Bank account number — AES-256 encrypted |
| ACCOUNT_TYPE | VARCHAR2(20) | CHECKING / SAVINGS |
| DEPOSIT_TYPE | VARCHAR2(20) | FULL / PARTIAL_AMOUNT / PARTIAL_PERCENT / REMAINDER |
| DEPOSIT_AMOUNT / DEPOSIT_PERCENTAGE | NUMBER | For partial deposit configurations |
| PRIORITY_ORDER | NUMBER(2) | 1 = first account funded |
| PRENOTE_SENT | CHAR(1) | Y = ACH pre-note sent to bank |

---

## LEAVE_TYPES — Leave Category Definitions

**Purpose:** Master catalog of leave categories with accrual rules, tenure gates, and carryover policies.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| LEAVE_TYPE_ID | NUMBER(5) PK | |
| LEAVE_TYPE_CODE | VARCHAR2(20) UNIQUE | PTO / SICK / COMP / FMLA / JURY / BEREAVE — **CORRECTED by DA Agent 2**: prior version listed ANNUAL/MATERNITY/PATERNITY which do not exist; actual codes per seed data are PTO (id=1), SICK (id=2), COMP (id=3), FMLA (id=4), JURY (id=5), BEREAVE (id=6) |
| PAID_FLAG | CHAR(1) | Y = paid leave |
| ACCRUAL_FLAG | CHAR(1) | Y = accrues over time |
| ACCRUAL_RATE | NUMBER(6,2) | Days per ACCRUAL_FREQUENCY |
| ACCRUAL_FREQUENCY | VARCHAR2(20) | MONTHLY / BIWEEKLY / ANNUAL |
| MAX_BALANCE | NUMBER(6,2) | Balance cap; NULL = no cap |
| CARRYOVER_MAX | NUMBER(6,2) | Max days to carry to next year; NULL = no limit |
| CARRYOVER_EXPIRY | NUMBER(3) | Months after Jan 1 before carryover expires; NULL = never |
| MIN_TENURE_DAYS | NUMBER(5) | Days employed before this leave type is available |
| REQUIRES_APPROVAL | CHAR(1) | Y = manager must approve |
| REQUIRES_DOCUMENT | CHAR(1) | Y = supporting documentation required; RC-010 CORRECTED: applies to FMLA (id=4) and COMP (id=3) per seed data — "maternity" leave type does not exist in this schema |

---

## LEAVE_BALANCES — Employee Leave Balances by Year

**Purpose:** Running leave balances per employee, per leave type, per calendar year. AVAILABLE is a virtual column.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| BALANCE_ID | NUMBER(10) PK | |
| EMP_ID / LEAVE_TYPE_ID / CALENDAR_YEAR | FK / FK / NUMBER | Unique combination (UK constraint) |
| OPENING_BALANCE | NUMBER(6,2) | Balance at start of year (carry-forward) |
| ACCRUED | NUMBER(6,2) | Total accrued this year |
| USED | NUMBER(6,2) | Total approved leave taken |
| ADJUSTMENT | NUMBER(6,2) | Manual HR adjustments |
| PENDING | NUMBER(6,2) | Sum of submitted-but-not-yet-approved requests |
| AVAILABLE | NUMBER(6,2) | VIRTUAL: OPENING+ACCRUED-USED+ADJUSTMENT-PENDING |
| CARRYOVER_FROM_PREV | NUMBER(6,2) | Amount carried from prior year |
| CARRYOVER_EXPIRY_DT | DATE | Date when carryover expires (if applicable) |

---

## LEAVE_REQUESTS — Leave Request Records

**Purpose:** Individual leave requests with full status lifecycle.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| REQUEST_ID | NUMBER(10) PK | |
| EMP_ID | NUMBER(10) FK | Employee requesting leave |
| LEAVE_TYPE_ID | NUMBER(5) FK | |
| START_DATE / END_DATE | DATE | Cannot backdate > 5 days; END ≥ START |
| TOTAL_DAYS | NUMBER(5,1) | Business days calculated by PKG_LEAVE; 0.5 = half day |
| HALF_DAY_FLAG | CHAR(1) | Y = half-day request |
| HALF_DAY_PERIOD | VARCHAR2(10) | AM or PM |
| STATUS | VARCHAR2(20) | PENDING → APPROVED / REJECTED; can be CANCELLED / TAKEN |
| APPROVER_EMP_ID | NUMBER(10) FK→EMPLOYEES | Manager who approved/rejected |
| APPROVAL_DATE | DATE | |
| CANCEL_REASON | VARCHAR2(4000) | Populated by PKG_EMPLOYEE.terminate_employee for auto-cancels |
| SUPPORTING_DOC_PATH | VARCHAR2(500) | Filesystem path to attached document |

---

## LEAVE_ACCRUAL_LOG — Leave Accrual History

**Purpose:** Detailed log of every leave accrual event. Written monthly by PKG_LEAVE.run_monthly_accrual.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| ACCRUAL_ID | NUMBER(15) PK | High-volume |
| EMP_ID / LEAVE_TYPE_ID | FK | |
| ACCRUAL_DATE | DATE | Date accrual was calculated |
| ACCRUAL_AMOUNT | NUMBER(6,2) | Days accrued in this event |
| BALANCE_AFTER | NUMBER(6,2) | Balance after this accrual |
| RUN_ID | NUMBER(10) | Soft ref to batch run (no FK) |

---

## HOLIDAYS — Public Holiday Calendar

**Purpose:** Company holiday calendar used by PKG_LEAVE.calculate_business_days to exclude non-working days.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| HOLIDAY_ID | NUMBER(5) PK | |
| HOLIDAY_DATE | DATE | |
| HOLIDAY_NAME | VARCHAR2(100) | |
| LOCATION_CODE | VARCHAR2(10) | NULL = global/all locations; otherwise location-specific |
| FLOATING_FLAG | CHAR(1) | Y = floating holiday employee can use on any date |

**Seed data:** 10 US federal holidays for 2024, all with LOCATION_CODE=NULL (global).

---

## REVIEW_CYCLES — Performance Review Campaign

**Purpose:** Defines a performance review cycle (annual, mid-year). Controls dates and status for creating individual reviews.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| CYCLE_ID | NUMBER(10) PK | |
| CYCLE_NAME / CYCLE_YEAR | VARCHAR2 / NUMBER | |
| START_DATE / END_DATE | DATE | Review window |
| SELF_REVIEW_DUE / MANAGER_REVIEW_DUE / CALIBRATION_DUE | DATE | Deadline milestones |
| STATUS | VARCHAR2(20) | DRAFT→OPEN→IN_PROGRESS→CALIBRATION→CLOSED |

---

## PERFORMANCE_REVIEWS — Individual Employee Reviews

**Purpose:** One row per employee per review cycle. Tracks self-assessment, manager assessment, rating, and calibration.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| REVIEW_ID | NUMBER(10) PK | |
| CYCLE_ID | NUMBER(10) FK | |
| EMP_ID | NUMBER(10) FK | Reviewee |
| REVIEWER_EMP_ID | NUMBER(10) FK→EMPLOYEES | Reviewing manager |
| STATUS | VARCHAR2(20) | NOT_STARTED→SELF_REVIEW→MANAGER_REVIEW→COMPLETED→ACKNOWLEDGED |
| OVERALL_RATING | NUMBER(2,1) | 1.0-5.0 CHECK constraint |
| RATING_LABEL | VARCHAR2(50) | Derived: Exceptional/Exceeds/Meets/Needs Improvement/Unsatisfactory |
| SELF_ASSESSMENT | CLOB | Employee's self-written assessment |
| MANAGER_ASSESSMENT | CLOB | Manager's written assessment |
| CALIBRATED_RATING | NUMBER(2,1) | Post-calibration override; supersedes OVERALL_RATING |
| EMPLOYEE_ACK_DATE | DATE | Date employee acknowledged the review |

---

## PERFORMANCE_GOALS — Goals Within a Review

**Purpose:** Individual performance goals associated with a review. Supports weight-based scoring contribution.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| GOAL_ID | NUMBER(10) PK | |
| REVIEW_ID | NUMBER(10) FK | |
| EMP_ID | NUMBER(10) FK | Redundant with REVIEW.EMP_ID — denormalized |
| GOAL_TITLE / GOAL_DESCRIPTION | VARCHAR2/CLOB | |
| GOAL_CATEGORY | VARCHAR2(30) | BUSINESS / DEVELOPMENT / LEADERSHIP / INNOVATION / COMPLIANCE |
| WEIGHT_PCT | NUMBER(5,2) | % contribution to overall rating |
| TARGET_DATE | DATE | Due date |
| STATUS | VARCHAR2(20) | NOT_STARTED→IN_PROGRESS→COMPLETED/DEFERRED/CANCELLED |
| PROGRESS_PCT | NUMBER(5,2) | 0-100 |
| SELF_RATING / MANAGER_RATING | NUMBER(2,1) | Per-goal ratings |

---

## AUDIT_LOG — System-Wide Audit Trail

**Purpose:** Append-only audit trail of all data modifications. Also used as application error/info log (TABLE_NAME='ERROR_LOG' / 'INFO_LOG'). Purged after 365 days.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| AUDIT_ID | NUMBER(15) PK | SEQ_AUDIT (CACHE 100) |
| TABLE_NAME | VARCHAR2(60) | Target table, or 'ERROR_LOG' / 'INFO_LOG' |
| RECORD_ID | NUMBER(15) | PK of affected row; 0 for log entries |
| ACTION_TYPE | VARCHAR2(10) | INSERT / UPDATE / DELETE |
| OLD_VALUES | CLOB | JSON string of old column values |
| NEW_VALUES | CLOB | JSON string of new column values |
| CHANGED_BY | VARCHAR2(30) | Username |
| CHANGED_DATE | DATE | |
| IP_ADDRESS | VARCHAR2(50) | From SYS_CONTEXT USERENV.IP_ADDRESS |
| SESSION_ID | VARCHAR2(100) | From SYS_CONTEXT USERENV.SESSIONID |

---

## SYSTEM_PARAMETERS — Application Configuration

**Purpose:** Key-value store for application configuration. Only EDITABLE_FLAG='Y' rows can be updated via PKG_COMMON.set_param. Contains SMTP host, session timeout, FTP credentials (security risk).

| Column | Type | Business Meaning |
|--------|------|-----------------|
| PARAM_ID | NUMBER(5) PK | |
| PARAM_GROUP | VARCHAR2(50) | Category: EMAIL / SECURITY / PAYROLL / INTEGRATION |
| PARAM_CODE | VARCHAR2(50) | Parameter name (unique with PARAM_GROUP) |
| PARAM_VALUE | VARCHAR2(4000) | Value as string regardless of type |
| DATA_TYPE | VARCHAR2(20) | Type hint: VARCHAR2 / NUMBER / DATE / BOOLEAN |
| EDITABLE_FLAG | CHAR(1) | Y = can be updated; N = system-locked |

---

## NOTIFICATION_QUEUE — Async Email/Message Queue

**Purpose:** Table-as-queue for outbound notifications. Dequeued by DBMS_SCHEDULER every 5 minutes via PKG_NOTIFICATION.process_queue.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| NOTIFICATION_ID | NUMBER(15) PK | |
| RECIPIENT_EMP_ID | NUMBER(10) | Soft ref to EMPLOYEES; nullable for external recipients |
| RECIPIENT_EMAIL | VARCHAR2(100) | Resolved from EMPLOYEES.EMAIL if not provided |
| NOTIFICATION_TYPE | VARCHAR2(30) | EMAIL / IN_APP / SMS |
| SUBJECT | VARCHAR2(200) | |
| BODY | CLOB | HTML email body |
| STATUS | VARCHAR2(20) | PENDING→SENT / FAILED / CANCELLED |
| PRIORITY | NUMBER(2) | Lower = higher priority |
| RETRY_COUNT | NUMBER(3) | Max 3 retries |
| REFERENCE_TABLE / REFERENCE_ID | VARCHAR2/NUMBER | Source entity for traceability |

---

## USER_SESSIONS — Active Login Sessions

**Purpose:** Tracks user login sessions for the Oracle Forms application. Session validity checked on every form operation.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| SESSION_ID | NUMBER(15) PK | |
| EMP_ID | NUMBER(10) FK | Logged-in employee |
| USERNAME | VARCHAR2(30) | Equals EMPLOYEES.EMAIL (lowercase) |
| LOGIN_TIME | DATE | Session start |
| LOGOUT_TIME | DATE | Session end (NULL = still active) |
| IP_ADDRESS | VARCHAR2(50) | Client IP |
| FORMS_MODULE | VARCHAR2(100) | Which Oracle Forms module was active |
| SESSION_STATUS | VARCHAR2(20) | ACTIVE / EXPIRED / CLOSED |

---

## USER_CREDENTIALS — Employee Authentication Credentials

**Purpose:** Stores the per-employee hashed password used by PKG_SECURITY to authenticate Oracle Forms logins. Kept separate from EMPLOYEES to isolate credential data. Table DDL not recovered from schema files — structure is inferred from PKG_SECURITY.pkb references and comments.

| Column | Type | Business Meaning |
|--------|------|-----------------|
| EMP_ID | NUMBER(10) PK/FK | One credential row per employee; FK to EMPLOYEES.EMP_ID (inferred) |
| PASSWORD_HASH | VARCHAR2(200) | MD5 hash of the plaintext password, produced by DBMS_CRYPTO.HASH_MD5 → RAWTOHEX inside PKG_SECURITY.hash_password |
| CREATED_DATE | DATE | Row creation timestamp (inferred audit column) |
| MODIFIED_DATE | DATE | Updated on each PKG_SECURITY.change_password call |

**Business rules captured here:**

- Password complexity is enforced **only in PKG_SECURITY.change_password** (not at DDL level): minimum 8 characters; at least one uppercase letter; at least one digit. Errors raised: ORA-20310 / ORA-20311 / ORA-20312.
- PKG_SECURITY.hash_password always uses **MD5** (DBMS_CRYPTO.HASH_MD5). MD5 is cryptographically broken for password storage — migration to PBKDF2 or bcrypt required (DQ-010).
- PKG_SECURITY.authenticate **does not query USER_CREDENTIALS** to verify the supplied password. The check is stubbed out — any password is accepted for a valid username (DQ-003, CRITICAL).
- PKG_SECURITY.change_password's DML is also a stub: the audit call `PKG_AUDIT.log_action('USER_CREDENTIALS', p_emp_id, 'UPDATE', USER)` fires, but the actual UPDATE statement is commented as pending implementation.
- No `LOGIN_ATTEMPTS` or `LOCKED_UNTIL` columns exist → unlimited brute-force attempts are possible (DQ-023).
- No `PASSWORD_CHANGED_DATE` column → no password age enforcement is possible.
- Timing attack: authenticate() raises a different exception path for unknown username vs wrong password, enabling username enumeration.
- Duplicate email fallback: if two ACTIVE employees share the same email, authenticate() silently selects `MIN(EMP_ID)` and logs in as the earliest employee — the second employee cannot authenticate as themselves (BR-043b).
- Old-password bypass: `change_password(p_emp_id, p_old_password, p_new_password)` accepts `p_old_password` but never verifies it against the stored hash. Any authenticated session can overwrite any employee's credential without knowing the current password (DQ-029, BR-044).
- Dead exceptions: `e_account_locked` (ORA-20302) and `e_session_expired` (ORA-20303) are declared in the package spec but raised nowhere in the body. Callers handling these named exceptions will never trigger those handlers (DQ-030, BR-045).
- Audit: all credential changes are logged to AUDIT_LOG via PKG_AUDIT with TABLE_NAME='USER_CREDENTIALS'.

---

## LOOKUP_VALUES — General Reference Code Table

**Purpose:** Catch-all reference table for lookup lists (marital status values, termination reasons, etc.). Self-referencing for hierarchical lookups (no FK).

| Column | Type | Business Meaning |
|--------|------|-----------------|
| LOOKUP_ID | NUMBER(10) PK | |
| LOOKUP_TYPE | VARCHAR2(50) | Category: MARITAL_STATUS / TERMINATION_REASON / etc. |
| LOOKUP_CODE | VARCHAR2(50) | Code value (unique with LOOKUP_TYPE) |
| LOOKUP_VALUE | VARCHAR2(200) | Display label |
| DISPLAY_ORDER | NUMBER(5) | UI sort order |
| PARENT_LOOKUP_ID | NUMBER(10) | Self-ref for hierarchy (no FK constraint) |

---

## TIME_ATTENDANCE_RECORDS — Implied Import Target (DDL not recovered)

**Status:** IMPLIED. No DDL exists anywhere in the codebase. Inferred as the destination table for `PKG_INTEGRATION.import_time_attendance`, which reads CSV records from the Oracle directory object `TIME_ATTENDANCE_IN`. The procedure body is a TODO stub — no INSERT or UPDATE DML is present. Column definitions are inferred from the CSV comment in the procedure body: `emp_number,date,hours_regular,hours_overtime`.

**Source procedure:** `PKG_INTEGRATION.import_time_attendance(p_file_name, p_user)`

**Input file:** `TIME_ATTENDANCE_IN/<p_file_name>` — CSV, hash-prefixed comment lines skipped (`SUBSTR(v_line,1,1) != '#'`)

**Business context:** Time and attendance data for hourly payroll. Currently unimplemented — `PAYROLL_DETAILS` hours values (for hourly employees) have no automated import path. Whether this table was ever created in production, or whether hourly payroll is processed via a different mechanism, is unknown.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| EMP_NUMBER | VARCHAR2(20) | FK to EMPLOYEES.EMP_NUMBER (business key, not EMP_ID) — positional column 1 of CSV |
| ATTENDANCE_DATE | DATE | Positional column 2 — format inferred (YYYY-MM-DD or similar) |
| HOURS_REGULAR | NUMBER | Positional column 3 — regular hours worked |
| HOURS_OVERTIME | NUMBER | Positional column 4 — overtime hours |
| SOURCE_FILE | VARCHAR2(100) | Likely staging column for audit trail — inferred |
| IMPORT_DATE | DATE | Likely staging column — inferred |
| STATUS | VARCHAR2(20) | Likely staging column (PENDING/PROCESSED/ERROR) — inferred |

**Business rules captured here:**

- Lines beginning with `#` are treated as comments and skipped by the importer.
- Empty lines (`v_line IS NOT NULL` guard) are also skipped.
- Per-line errors are caught individually (`EXCEPTION WHEN OTHERS`) and counted as `v_errors`; the import continues through remaining lines (no all-or-nothing transaction).
- The procedure logs a summary `Imported: N, Errors: M` via `PKG_COMMON.log_info` on completion.
- No transaction control (COMMIT/ROLLBACK) is visible — stub has no DML so no isolation boundary exists yet.
- **Critical gap:** No link to PAYROLL_DETAILS or PAYROLL_RUNS is implemented. Even when the stub is completed, the mechanism for converting imported attendance rows into payroll elements is undefined.

**Migration note:** This table does not need to be migrated (no production data exists). The integration pattern itself — CSV drop into an OS directory, read by UTL_FILE — must be redesigned for any non-Oracle target (S3 ingest, SFTP, message queue, or direct API call from the time system).

---

## RPT_* Tables — Inferred Denormalized Reporting Layer (7 tables, DDL not recovered)

**Status:** INFERRED. DDL not found in Tables.sql. Implied by the comment inside `PKG_REPORTING.refresh_reporting_tables`: _"Placeholder for nightly refresh of denormalized reporting tables. In production, this truncates and repopulates RPT_* tables."_

**Key fact:** The stub procedure is never executed — it contains only a `PKG_COMMON.log_info` call and no DML. Whether these tables exist in production, and whether they have ever been populated, is unknown.

Column shapes below are inferred from the SELECT lists of the 7 corresponding `PKG_REPORTING` report procedures.

---

### RPT_HEADCOUNT — Headcount Snapshot by Dept/Location

Mirrors `PKG_REPORTING.headcount_report`. Sources: EMPLOYEES, DEPARTMENTS, LOCATIONS.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| DEPT_NAME | VARCHAR2(100) | |
| COST_CENTER | VARCHAR2(20) | |
| LOCATION_NAME | VARCHAR2(100) | |
| CITY | VARCHAR2(100) | |
| STATE_PROVINCE | VARCHAR2(100) | |
| HEADCOUNT | NUMBER | COUNT(*) of ACTIVE employees at snapshot date |
| FT_COUNT | NUMBER | EMPLOYMENT_TYPE='FULL_TIME' |
| PT_COUNT | NUMBER | EMPLOYMENT_TYPE='PART_TIME' |
| CONTRACT_COUNT | NUMBER | EMPLOYMENT_TYPE='CONTRACT' |
| MALE_COUNT | NUMBER | GENDER='M' |
| FEMALE_COUNT | NUMBER | GENDER='F' |
| AVG_TENURE_YEARS | NUMBER(6,1) | ROUND(AVG(MONTHS_BETWEEN(snap_date, HIRE_DATE)/12), 1) |
| SNAPSHOT_DATE | DATE | As-of date (inferred) |
| LOAD_TIMESTAMP | DATE | Nightly refresh timestamp (inferred) |

---

### RPT_COMPENSATION — Compensation Summary by Dept/Grade/Job

Mirrors `PKG_REPORTING.compensation_summary`. Sources: EMPLOYEES, DEPARTMENTS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| DEPT_NAME | VARCHAR2(100) | |
| GRADE_NAME | VARCHAR2(100) | |
| JOB_TITLE | VARCHAR2(100) | |
| EMP_COUNT | NUMBER | |
| GRADE_MIN / GRADE_MAX | NUMBER(12,2) | JOB_GRADES band boundaries |
| ACTUAL_MIN / ACTUAL_MAX | NUMBER(12,2) | Actual min/max salary in group |
| AVG_SALARY | NUMBER(12,2) | ROUND(AVG(BASE_SALARY),2) |
| MEDIAN_SALARY | NUMBER(12,2) | ROUND(MEDIAN(BASE_SALARY),2) — Oracle aggregate |
| COMPA_RATIO | NUMBER(6,1) | AVG(salary/grade_midpoint)×100 |
| LOAD_TIMESTAMP | DATE | Nightly refresh timestamp (inferred) |

---

### RPT_TURNOVER — Turnover Metrics by Dept/Period

Mirrors `PKG_REPORTING.turnover_report`. Sources: EMPLOYEES, DEPARTMENTS.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| DEPT_NAME | VARCHAR2(100) | |
| REPORT_START_DATE / REPORT_END_DATE | DATE | Period boundaries (inferred for snapshot) |
| TERMINATIONS | NUMBER | Count of terminations in period |
| CURRENT_HC | NUMBER | ACTIVE employees at end of period |
| TURNOVER_PCT | NUMBER(6,1) | ROUND(terminations×100.0 / headcount_at_start, 1) |
| VOLUNTARY | NUMBER | TERMINATION_REASON='VOLUNTARY' |
| INVOLUNTARY | NUMBER | TERMINATION_REASON != 'VOLUNTARY' |
| AVG_TENURE_AT_EXIT | NUMBER(6,1) | Avg tenure at termination date |
| LOAD_TIMESTAMP | DATE | Nightly refresh timestamp (inferred) |

---

### RPT_NEW_HIRES — New Hire Detail by Period

Mirrors `PKG_REPORTING.new_hires_report`. Row-level (one row per hire). Sources: EMPLOYEES, DEPARTMENTS, JOB_TITLES, LOCATIONS, SALARY_RECORDS.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| EMP_NUMBER | VARCHAR2(20) | |
| EMP_NAME | VARCHAR2(101) | FIRST_NAME \|\| ' ' \|\| LAST_NAME |
| HIRE_DATE | DATE | |
| DEPT_NAME | VARCHAR2(100) | |
| JOB_TITLE | VARCHAR2(100) | |
| LOCATION_NAME | VARCHAR2(100) | |
| EMPLOYMENT_TYPE | VARCHAR2(20) | |
| BASE_SALARY | NUMBER(12,2) | From SALARY_RECORDS (active row) |
| MANAGER_EMP_ID | NUMBER(10) | |
| MANAGER_NAME | VARCHAR2(101) | Manager full name |
| REPORT_START_DATE / REPORT_END_DATE | DATE | Hire-window boundaries (inferred) |
| LOAD_TIMESTAMP | DATE | Nightly refresh timestamp (inferred) |

---

### RPT_LEAVE_UTILIZATION — Leave Utilization by Dept/Type/Year

Mirrors `PKG_REPORTING.leave_utilization_report`. Sources: LEAVE_BALANCES, EMPLOYEES, DEPARTMENTS, LEAVE_TYPES.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| DEPT_NAME | VARCHAR2(100) | |
| LEAVE_TYPE_NAME | VARCHAR2(100) | |
| CALENDAR_YEAR | NUMBER(4) | |
| EMP_COUNT | NUMBER | COUNT(DISTINCT EMP_ID) with balances |
| AVG_ENTITLED | NUMBER(6,1) | AVG(OPENING_BALANCE + ACCRUED) |
| AVG_USED | NUMBER(6,1) | AVG(USED) |
| AVG_REMAINING | NUMBER(6,1) | AVG(OPENING+ACCRUED-USED+ADJUSTMENT) |
| UTILIZATION_PCT | NUMBER(6,1) | AVG(USED)×100 / AVG(OPENING+ACCRUED) |
| LOAD_TIMESTAMP | DATE | Nightly refresh timestamp (inferred) |

---

### RPT_PAYROLL_SUMMARY — Payroll Summary by Dept/Period

Mirrors `PKG_REPORTING.payroll_summary_report`. Sources: PAYROLL_DETAILS, PAYROLL_RUNS, EMPLOYEES, DEPARTMENTS.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| DEPT_NAME | VARCHAR2(100) | |
| PERIOD_ID | NUMBER(10) | FK to PAY_PERIODS (inferred) |
| EMP_COUNT | NUMBER | COUNT(DISTINCT EMP_ID) in run |
| TOTAL_GROSS | NUMBER(15,2) | SUM where ELEMENT_TYPE='EARNING' |
| TOTAL_FED_TAX | NUMBER(15,2) | SUM where ELEMENT_ID=100 |
| TOTAL_STATE_TAX | NUMBER(15,2) | SUM where ELEMENT_ID=101 |
| TOTAL_SS | NUMBER(15,2) | SUM where ELEMENT_ID=102 |
| TOTAL_MEDICARE | NUMBER(15,2) | SUM where ELEMENT_ID=103 |
| TOTAL_DEDUCTIONS | NUMBER(15,2) | SUM where ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') |
| TOTAL_NET | NUMBER(15,2) | SUM of all PAYROLL_DETAILS.AMOUNT |
| LOAD_TIMESTAMP | DATE | Nightly refresh timestamp (inferred) |

---

### RPT_EEO_COMPLIANCE — EEO Workforce Composition Snapshot

Mirrors `PKG_REPORTING.eeo_compliance_report`. Used for EEOC filings. Sources: EMPLOYEES, JOB_TITLES.

| Inferred Column | Type | Notes |
|----------------|------|-------|
| EEO_CATEGORY | VARCHAR2(100) | JOB_TITLES.EEO_CATEGORY |
| TOTAL | NUMBER | Total ACTIVE employees in category |
| MALE | NUMBER | GENDER='M' |
| FEMALE | NUMBER | GENDER='F' |
| OTHER_GENDER | NUMBER | GENDER='O' |
| NOT_DISCLOSED | NUMBER | GENDER IS NULL |
| FEMALE_PCT | NUMBER(5,1) | ROUND(FEMALE×100.0/TOTAL, 1) |
| SNAPSHOT_DATE | DATE | As-of date (inferred) |
| LOAD_TIMESTAMP | DATE | Nightly refresh timestamp (inferred) |

**Business rules captured here:**

- All 7 RPT_* tables share a truncate-and-repopulate refresh pattern (implied by comment). No incremental/delta merge is described.
- `refresh_reporting_tables` is currently a stub with no DML. Any scheduler job firing it would log an INFO message and leave all RPT_* tables untouched.
- The 7 `PKG_REPORTING` report procedures query OLTP tables directly and do NOT read RPT_* tables. Reports function correctly without the denormalized layer, but are subject to OLTP locking and longer query times under load.
- ELEMENT_ID magic numbers (100=FED_TAX, 101=STATE_TAX, 102=SS, 103=MEDICARE) are embedded in RPT_PAYROLL_SUMMARY aggregations, inheriting the same fragility as PKG_PAYROLL (see BR-014).
