# TA_Stack_Scout.md
## Agent 1 — Technology Stack Scout v2.0
### HRMS Oracle Forms Codebase — Full Stack Scan

---

## PROJECT SCAN SUMMARY

| Field | Value |
|---|---|
| Target System | HRMS Platform (Human Resources Management System) |
| Scan Date | 2026-08-04 |
| Agent | TA Agent 1 — Technology Stack Scout v2.0 |
| Codebase Path | `ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main` |
| Application Version | 4.2.0 Build 2024.03.15 (hard-coded in HRMS_MENU.xml) |
| Architecture Pattern | Monolith — single Oracle DB schema, Oracle Forms fat-client |
| Schema | HRMS (single schema) |
| Concurrent Users | ~200 across 3 regional offices |
| Files in Scan Set | 42 source files |
| Files Referenced but Missing | 12 tables, 9 views, 200+ triggers (only 6 in scan set), Oracle Reports (8 .rdf/.rep), PKG_DEPARTMENT source |
| Confidence Level | MEDIUM-HIGH — core packages fully present; infrastructure layer thin |

---

## OUTPUT 1 — TECHNOLOGY STACK INVENTORY

| # | Layer | Technology | Version | Source of Evidence | Confidence |
|---|---|---|---|---|---|
| 1 | UI Framework | Oracle Forms | 12c (12.2.1.4) | README.md | HIGH |
| 2 | UI Framework | Oracle Forms .fmb/.fmx modules | 12c | README.md — 18 forms listed | HIGH |
| 3 | UI Framework | Oracle Forms .pll PL/SQL Libraries | 12c | HRMS_COMMON_LIB.pll.sql, HRMS_VALIDATION_LIB.pll.sql | HIGH |
| 4 | UI Framework | Oracle Forms .mmb Menu Modules | 12c | HRMS_MENU.mmb.sql | HIGH |
| 5 | Application Server | Oracle WebLogic Server | 12c | README.md | HIGH |
| 6 | Database Engine | Oracle Database | 19c | README.md | HIGH |
| 7 | Database Schema | Single schema — HRMS | 19c | All DDL files, all package source | HIGH |
| 8 | Reporting | Oracle Reports | Not specified (.rdf/.rep) | README.md — 8 reports listed | LOW — no report files in scan set |
| 9 | Language | PL/SQL | Oracle 19c dialect | All .pks/.pkb/.sql files | HIGH |
| 10 | Language | SQL (DDL/DML) | ANSI + Oracle extensions | schema/ directory | HIGH |
| 11 | Built-in Package | DBMS_CRYPTO | Oracle built-in | PKG_SECURITY.pkb — AES-256, MD5 | HIGH |
| 12 | Built-in Package | UTL_SMTP | Oracle built-in | PKG_NOTIFICATION.pkb | HIGH |
| 13 | Built-in Package | UTL_FILE | Oracle built-in | PKG_INTEGRATION.pkb, PKG_PAYROLL.pkb | HIGH |
| 14 | Built-in Package | UTL_RAW | Oracle built-in | PKG_SECURITY.pkb | HIGH |
| 15 | Built-in Package | UTL_TCP | Oracle built-in | PKG_NOTIFICATION.pkb (referenced) | MEDIUM |
| 16 | Built-in Package | DBMS_OUTPUT | Oracle built-in | Multiple packages | HIGH |
| 17 | Built-in Package | DBMS_SCHEDULER | Oracle built-in | PKG_NOTIFICATION.pkb (process_queue every 5 min), PKG_LEAVE.pkb (monthly accrual) | HIGH |
| 18 | Built-in Package | SYS_CONTEXT(USERENV) | Oracle built-in | PKG_AUDIT.pkb — IP capture | HIGH |
| 19 | SQL Feature | CONNECT BY hierarchical queries | Oracle SQL | PKG_EMPLOYEE.pkb (get_org_chart), hrms_views.sql (VW_ORG_HIERARCHY) | HIGH |
| 20 | SQL Feature | Analytic window functions | Oracle SQL | PKG_PERFORMANCE.pkb (get_rating_distribution), PKG_REPORTING.pkb | HIGH |
| 21 | SQL Feature | REF CURSOR | Oracle PL/SQL | PKG_AUDIT.pkb, PKG_REPORTING.pkb, multiple packages | HIGH |
| 22 | SQL Feature | PRAGMA AUTONOMOUS_TRANSACTION | Oracle PL/SQL | PKG_AUDIT.pkb, PKG_COMMON.pkb, PKG_NOTIFICATION.pkb | HIGH |
| 23 | SQL Feature | Virtual columns | Oracle 11g+ | LEAVE_BALANCES.AVAILABLE (computed) | HIGH |
| 24 | SQL Feature | REGEXP_LIKE | Oracle SQL | PKG_VALIDATION.pkb, PKG_COMMON.pkb, HRMS_VALIDATION_LIB.pll.sql | HIGH |
| 25 | Encryption | AES-256 CBC PKCS5 | via DBMS_CRYPTO | PKG_SECURITY.pkb (encrypt_ssn/decrypt_ssn) | HIGH |
| 26 | Hashing | MD5 | via DBMS_CRYPTO | PKG_SECURITY.pkb (hash_password) — WEAK, see Security Output | HIGH |
| 27 | Email Transport | SMTP (plaintext port 25) | Internal relay | PKG_NOTIFICATION.pkb — smtp.internal.company.com:25 | HIGH |
| 28 | File I/O | Oracle Directory Objects | Oracle DB | PKG_INTEGRATION.pkb, PKG_PAYROLL.pkb | HIGH |
| 29 | File Format (outbound) | Pipe-delimited flat file (.dat) | Custom | PKG_INTEGRATION.pkb — GL journal feed | HIGH |
| 30 | File Format (outbound) | Fixed-width flat file (203 chars) | ADP spec | PKG_INTEGRATION.pkb — ADP benefits feed | HIGH |
| 31 | File Format (inbound) | CSV | Time & Attendance system | PKG_INTEGRATION.pkb — parsing NOT implemented (TODO) | HIGH |
| 32 | Directory Integration | LDAP/Active Directory | Stub — not implemented | PKG_INTEGRATION.pkb (sync_org_structure is stub) | HIGH — stub confirmed |
| 33 | Version Control | Git | Unknown | .git directory present in working directory | HIGH |
| 34 | CI/CD | NONE DETECTED | N/A | No Dockerfile, no Jenkinsfile, no .gitlab-ci.yml, no GitHub Actions, no Terraform, no Ansible found | HIGH — confirmed absent |
| 35 | Deployment Model | On-premises | Oracle Forms/WebLogic/DB 19c | README.md, infrastructure context | HIGH |

---

## OUTPUT 2 — COMPONENT & SERVICE MAP

| # | Component Name | Type | Source File(s) | Exposed Interfaces | Upstream Dependencies | Downstream Dependencies | Notes |
|---|---|---|---|---|---|---|---|
| 1 | HRMS_LOGIN | Oracle Form | forms/xml-exports/HRMS_LOGIN.xml | Oracle Forms applet (HTTP/JNLP via WebLogic) | PKG_SECURITY.authenticate | PKG_SECURITY, EMPLOYEES table, USER_SESSIONS | No lockout; password cleartext; ROWNUM=1 for duplicate email |
| 2 | HRMS_MENU | Oracle Form (MDI Shell) | forms/xml-exports/HRMS_MENU.xml | Menu navigation | PKG_SECURITY.has_permission | All other forms (OPEN_FORM) | Hard-coded build string v4.2/2024.03.15; BTN_LEAVE and BTN_PERFORMANCE have no permission check |
| 3 | HRMS_EMPLOYEE | Oracle Form | forms/xml-exports/HRMS_EMPLOYEE.xml | Forms applet | HRMS_COMMON_LIB, HRMS_VALIDATION_LIB, PKG_EMPLOYEE, PKG_SECURITY | EMPLOYEES, SALARY_RECORDS, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS | 4-tab canvas; hire date limit 90 days (DISC-003: trigger says 180) |
| 4 | HRMS_LEAVE | Oracle Form | forms/xml-exports/HRMS_LEAVE.xml | Forms applet | PKG_LEAVE, HRMS_COMMON_LIB | LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES | Only PENDING/APPROVED can be cancelled |
| 5 | HRMS_PAYROLL | Oracle Form | forms/xml-exports/HRMS_PAYROLL.xml | Forms applet | PKG_PAYROLL, PKG_SECURITY.has_permission | PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS | Requires PAYROLL VIEW to open; APPROVE requires PAYROLL APPROVE permission |
| 6 | HRMS_PERFORMANCE | Oracle Form | forms/xml-exports/HRMS_PERFORMANCE.xml | Forms applet | PKG_PERFORMANCE, HRMS_COMMON_LIB | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS | Default shows OPEN and DRAFT cycles |
| 7 | HRMS_COMMON_LIB | PL/SQL Library (.pll) | forms/libraries/HRMS_COMMON_LIB.pll.sql | Attached to all forms | PKG_COMMON.log_error, PKG_SECURITY.is_session_valid | All Forms modules | Toolbar actions, session check, LOV refresh |
| 8 | HRMS_VALIDATION_LIB | PL/SQL Library (.pll) | forms/libraries/HRMS_VALIDATION_LIB.pll.sql | Attached to forms | JOB_GRADES table (direct query), HRMS_COMMON_LIB | HRMS_EMPLOYEE and other forms | Known email bug (rejects subdomains); differs from PKG_COMMON.is_valid_email |
| 9 | HRMS_MENU.mmb | Oracle Menu Module | forms/menus/HRMS_MENU.mmb.sql | Attached to MDI form | PKG_SECURITY.has_permission | All navigable forms | Role-based menu item visibility |
| 10 | PKG_EMPLOYEE | PL/SQL Package | plsql/packages/PKG_EMPLOYEE.pks/.pkb | Called by Forms + other packages | PKG_PAYROLL, PKG_AUDIT, PKG_NOTIFICATION, PKG_VALIDATION, PKG_SECURITY | EMPLOYEES, EMPLOYEE_HISTORY, SALARY_RECORDS | SQL injection in search_employees; circular dep with PKG_PAYROLL; race condition in generate_emp_number |
| 11 | PKG_PAYROLL | PL/SQL Package | plsql/packages/PKG_PAYROLL.pks/.pkb | Called by Forms + PKG_EMPLOYEE | PKG_EMPLOYEE.is_active, PKG_AUDIT, PKG_NOTIFICATION | PAYROLL_RUNS, PAYROLL_DETAILS, TAX_BRACKETS, SALARY_RECORDS, UTL_FILE (PAYROLL_OUTPUT) | Circular dep with PKG_EMPLOYEE; 2024 tax brackets hard-coded; YTD fields are 0 placeholders; commits every 50 employees (partial commit risk) |
| 12 | PKG_LEAVE | PL/SQL Package | plsql/packages/PKG_LEAVE.pks/.pkb | Called by Forms | PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON | LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_ACCRUAL_LOG, LEAVE_TYPES | DBMS_SCHEDULER for monthly accrual; commits every 100 employees |
| 13 | PKG_PERFORMANCE | PL/SQL Package | plsql/packages/PKG_PERFORMANCE.pks/.pkb | Called by Forms | PKG_AUDIT, PKG_NOTIFICATION | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS | 5-label rating scale; analytic window functions for distribution |
| 14 | PKG_SECURITY | PL/SQL Package | plsql/packages/PKG_SECURITY.pks/.pkb | Called by all Forms + PKG_EMPLOYEE | DBMS_CRYPTO, SYS_CONTEXT, PKG_AUDIT (indirect via session) | USER_SESSIONS, EMPLOYEES | Hard-coded AES key (SECURITY); MD5 hashing (WEAK); authenticate stub incomplete; grade-based permissions |
| 15 | PKG_AUDIT | PL/SQL Package | plsql/packages/PKG_AUDIT.pks/.pkb | Called by all packages + triggers | DBMS_CRYPTO (indirect), SYS_CONTEXT | AUDIT_LOG, SEQ_AUDIT | PRAGMA AUTONOMOUS_TRANSACTION; failures silently swallowed; CACHE 100 on SEQ_AUDIT |
| 16 | PKG_NOTIFICATION | PL/SQL Package | plsql/packages/PKG_NOTIFICATION.pks/.pkb | Called by PKG_EMPLOYEE, PKG_LEAVE, PKG_PERFORMANCE, PKG_PAYROLL | UTL_SMTP, DBMS_SCHEDULER | NOTIFICATION_QUEUE | PRAGMA AUTONOMOUS_TRANSACTION; SMTP plaintext port 25; batch 50; retry max 3 |
| 17 | PKG_INTEGRATION | PL/SQL Package | plsql/packages/PKG_INTEGRATION.pks/.pkb | Called by scheduled jobs / manually | UTL_FILE, PKG_AUDIT, PKG_COMMON | GL_FEED_OUT dir, BENEFITS_FEED_OUT dir, TIME_ATTENDANCE_IN dir, SYSTEM_PARAMETERS | CSV import is TODO; LDAP sync is stub; FTP credentials in SYSTEM_PARAMETERS cleartext |
| 18 | PKG_COMMON | PL/SQL Package | plsql/packages/PKG_COMMON.pks/.pkb | Called by nearly all packages | AUDIT_LOG, SYSTEM_PARAMETERS | — | Base utilities: logging, param store, date math, formatters, validation helpers |
| 19 | PKG_VALIDATION | PL/SQL Package | plsql/packages/PKG_VALIDATION.pks/.pkb | Called by PKG_EMPLOYEE and Forms | JOB_GRADES, HOLIDAYS, PKG_COMMON | — | validate_required_fields only implements EMPLOYEES; is_business_day checks HOLIDAYS table |
| 20 | PKG_REPORTING | PL/SQL Package | plsql/packages/PKG_REPORTING.pks/.pkb | Called by Forms (HRMS_REPORTS — referenced only) | VW_ACTIVE_EMPLOYEES, SALARY_RECORDS, LEAVE_REQUESTS, PAYROLL_DETAILS | — | refresh_reporting_tables is stub; EEO report by gender |
| 21 | PKG_DEPARTMENT | PL/SQL Package | Referenced in README | (Source not in scan set) | Unknown | DEPARTMENTS table assumed | LOW confidence — no source file available |
| 22 | Oracle Reports (8 modules) | Oracle Reports .rdf/.rep | Not in scan set | WebLogic Reports servlet (assumed) | Unknown | Unknown | LOW confidence — referenced in README only |

---

## OUTPUT 3 — DATA STORE REGISTRY

### Tables (30 of 42 documented; 12 not in scan set)

#### DEPARTMENTS
| Column | Type | Constraints | Notes |
|---|---|---|---|
| DEPT_ID | NUMBER | PK, SEQ_DEPARTMENT | |
| DEPT_CODE | VARCHAR2(10) | NOT NULL UNIQUE | |
| DEPT_NAME | VARCHAR2(100) | NOT NULL | |
| PARENT_DEPT_ID | NUMBER | FK→DEPARTMENTS.DEPT_ID | Self-referential hierarchy |
| MANAGER_EMP_ID | NUMBER | FK→EMPLOYEES.EMP_ID | Double-update anomaly for DEPT_ID=30 in seed data |
| LOCATION_ID | NUMBER | FK→LOCATIONS.LOCATION_ID | |
| COST_CENTER | VARCHAR2(20) | | |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' | Soft delete |
| CREATED_BY / CREATED_DATE / MODIFIED_BY / MODIFIED_DATE | Standard audit cols | | |

#### LOCATIONS
| Column | Type | Constraints | Notes |
|---|---|---|---|
| LOCATION_ID | NUMBER | PK, SEQ_LOCATION | |
| LOCATION_CODE | VARCHAR2(10) | NOT NULL UNIQUE | |
| LOCATION_NAME | VARCHAR2(100) | NOT NULL | |
| ADDRESS_LINE1/2 | VARCHAR2(200) | | |
| CITY / STATE / ZIP / COUNTRY | VARCHAR2 | | |
| PHONE | VARCHAR2(20) | | |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' | |
| Standard audit cols | | | |

#### JOB_GRADES
| Column | Type | Constraints | Notes |
|---|---|---|---|
| GRADE_ID | NUMBER | PK, SEQ_JOB_GRADE | |
| GRADE_LEVEL | NUMBER | NOT NULL UNIQUE | 1–10 |
| GRADE_NAME | VARCHAR2(50) | NOT NULL | |
| MIN_SALARY / MAX_SALARY / MIDPOINT_SALARY | NUMBER(10,2) | NOT NULL | Bands $35k–$600k |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' | |
| Standard audit cols | | | |

#### JOB_TITLES
| Column | Type | Constraints | Notes |
|---|---|---|---|
| JOB_TITLE_ID | NUMBER | PK, SEQ_JOB_TITLE | |
| JOB_CODE | VARCHAR2(20) | NOT NULL UNIQUE | |
| JOB_TITLE | VARCHAR2(100) | NOT NULL | |
| GRADE_ID | NUMBER | FK→JOB_GRADES.GRADE_ID | |
| EEO_CATEGORY | VARCHAR2(50) | | Used in EEO compliance report |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' | |
| Standard audit cols | | | |

#### EMPLOYEES (34 columns)
| Column | Type | Constraints | Notes |
|---|---|---|---|
| EMP_ID | NUMBER | PK, SEQ_EMPLOYEE (starts 10000) | |
| EMP_NUMBER | VARCHAR2(20) | NOT NULL UNIQUE | Format: EMP-NNNNNN |
| FIRST_NAME / LAST_NAME | VARCHAR2(50/100) | NOT NULL | |
| EMAIL | VARCHAR2(200) | NOT NULL UNIQUE | Case-insensitive match in login |
| PHONE | VARCHAR2(20) | | |
| DATE_OF_BIRTH | DATE | | |
| HIRE_DATE | DATE | NOT NULL | Validation conflict: form=90d future limit, trigger=180d (DISC-003) |
| TERMINATION_DATE | DATE | | |
| EMPLOYMENT_STATUS | VARCHAR2(20) | DEFAULT 'ACTIVE' | ACTIVE/TERMINATED/LOA |
| DEPT_ID | NUMBER | FK→DEPARTMENTS.DEPT_ID | |
| JOB_TITLE_ID | NUMBER | FK→JOB_TITLES.JOB_TITLE_ID | |
| GRADE_ID | NUMBER | FK→JOB_GRADES.GRADE_ID | Grade drives permission model (>=8 full, >=5 VIEW all) |
| MANAGER_EMP_ID | NUMBER | FK→EMPLOYEES.EMP_ID | Self-referential |
| LOCATION_ID | NUMBER | FK→LOCATIONS.LOCATION_ID | |
| SSN | VARCHAR2(500) | | AES-256 encrypted via PKG_SECURITY.encrypt_ssn |
| GENDER / ETHNICITY / VETERAN_STATUS / DISABILITY_STATUS | VARCHAR2 | | EEO/compliance fields — PII |
| ADDRESS fields (4) | VARCHAR2 | | PII |
| EMERGENCY_CONTACT_NAME/PHONE | VARCHAR2 | | PII |
| PASSWORD_HASH | VARCHAR2(200) | | MD5 (WEAK) |
| LAST_LOGIN_DATE | DATE | | |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' | Soft delete |
| Standard audit cols | | | |
| (remaining ~8 columns) | Various | | See DDL — 34 total confirmed |

#### EMPLOYEE_HISTORY
| Column | Type | Notes |
|---|---|---|
| HIST_ID | NUMBER | PK (DDL name) — DISC-001: trigger uses HISTORY_ID |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| EFFECTIVE_DATE | DATE | DDL name — DISC-001: trigger uses CHANGE_DATE |
| CHANGE_TYPE | VARCHAR2(50) | STATUS_CHANGE / DEPARTMENT_CHANGE / JOB_CHANGE |
| OLD_DEPT_ID / NEW_DEPT_ID | NUMBER | DDL columns — DISC-001: trigger uses OLD_VALUE/NEW_VALUE |
| OLD_JOB_TITLE_ID / NEW_JOB_TITLE_ID | NUMBER | DDL columns |
| OLD_GRADE_ID / NEW_GRADE_ID | NUMBER | DDL columns |
| CHANGED_BY | VARCHAR2(100) | |
| Standard audit cols | | |

**DISC-001**: TRG_EMP_BEFORE_UPDATE references columns HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE — these do NOT match the DDL columns (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID, etc.). Agent 2 must determine authoritative schema.

#### EMPLOYEE_DEPENDENTS
| Column | Type | Notes |
|---|---|---|
| DEPENDENT_ID | NUMBER | PK, SEQ_DEPENDENT |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| FIRST_NAME / LAST_NAME | VARCHAR2 | PII |
| RELATIONSHIP | VARCHAR2(50) | |
| DATE_OF_BIRTH | DATE | PII |
| SSN | VARCHAR2(500) | AES-256 encrypted (assumed, per PKG_INTEGRATION benefits feed LEFT JOIN) |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' |
| Standard audit cols | | |

#### EMERGENCY_CONTACTS
| Column | Type | Notes |
|---|---|---|
| CONTACT_ID | NUMBER | PK, SEQ_EMERGENCY_CONTACT |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| CONTACT_NAME | VARCHAR2(200) | PII |
| RELATIONSHIP / PHONE / EMAIL / IS_PRIMARY | VARCHAR2/CHAR | PII |
| Standard audit cols | | |

#### SALARY_RECORDS
| Column | Type | Notes |
|---|---|---|
| SALARY_ID | NUMBER | PK, SEQ_SALARY |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| EFFECTIVE_DATE | DATE | |
| END_DATE | DATE | Null = current |
| SALARY_AMOUNT | NUMBER(10,2) | |
| PAY_FREQUENCY | VARCHAR2(20) | MONTHLY/BIWEEKLY |
| CURRENCY_CODE | VARCHAR2(3) | DEFAULT 'USD' |
| CHANGE_REASON | VARCHAR2(200) | |
| APPROVED_BY | NUMBER | FK→EMPLOYEES |
| Standard audit cols | | |
| Audit trigger | TRG_SALARY_AUDIT | AFTER INSERT/UPDATE/DELETE → PKG_AUDIT.log_action with JSON old/new |

#### PAY_ELEMENTS
| Column | Type | Notes |
|---|---|---|
| ELEMENT_ID | NUMBER | PK, SEQ_PAY_ELEMENT |
| ELEMENT_CODE / ELEMENT_NAME | VARCHAR2 | |
| ELEMENT_TYPE | VARCHAR2(20) | EARNING / DEDUCTION / TAX |
| DEFAULT_AMOUNT | NUMBER(10,2) | 11 rows in seed data |
| IS_TAXABLE / IS_PRETAX | CHAR(1) | |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' |
| Standard audit cols | | |

#### EMPLOYEE_PAY_ELEMENTS
| Column | Type | Notes |
|---|---|---|
| EMP_ELEMENT_ID | NUMBER | PK, SEQ_EMP_PAY_ELEMENT |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| ELEMENT_ID | NUMBER | FK→PAY_ELEMENTS |
| AMOUNT / PERCENTAGE | NUMBER | |
| EFFECTIVE_DATE / END_DATE | DATE | |
| Standard audit cols | | |

#### PAY_PERIODS
| Column | Type | Notes |
|---|---|---|
| PERIOD_ID | NUMBER | PK, SEQ_PAY_PERIOD |
| PERIOD_NAME | VARCHAR2(100) | |
| PERIOD_TYPE | VARCHAR2(20) | MONTHLY / BIWEEKLY |
| START_DATE / END_DATE | DATE | |
| PAY_DATE | DATE | Moved to Friday if weekend |
| FISCAL_YEAR / FISCAL_QUARTER | NUMBER | Oct-start fiscal year |
| STATUS | VARCHAR2(20) | |
| Standard audit cols | | |

#### PAYROLL_RUNS
| Column | Type | Notes |
|---|---|---|
| RUN_ID | NUMBER | PK, SEQ_PAYROLL_RUN |
| PERIOD_ID | NUMBER | FK→PAY_PERIODS |
| RUN_DATE | DATE | |
| STATUS | VARCHAR2(20) | PENDING → CALCULATED → APPROVED |
| TOTAL_GROSS / TOTAL_NET / TOTAL_TAX | NUMBER(12,2) | |
| PROCESSED_BY / APPROVED_BY | NUMBER | FK→EMPLOYEES |
| Standard audit cols | | |

#### PAYROLL_DETAILS
| Column | Type | Notes |
|---|---|---|
| DETAIL_ID | NUMBER | PK, SEQ_PAYROLL_DETAIL |
| RUN_ID | NUMBER | FK→PAYROLL_RUNS |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| GROSS_PAY / NET_PAY / FEDERAL_TAX / STATE_TAX / SS_TAX / MEDICARE_TAX | NUMBER(10,2) | |
| YTD_GROSS / YTD_NET | NUMBER(10,2) | Hard-coded 0 placeholders — NOT IMPLEMENTED |
| Standard audit cols | | |

#### TAX_BRACKETS
| Column | Type | Notes |
|---|---|---|
| BRACKET_ID | NUMBER | PK, SEQ_TAX_BRACKET |
| TAX_YEAR / FILING_STATUS | NUMBER/VARCHAR2 | |
| MIN_INCOME / MAX_INCOME | NUMBER(12,2) | |
| TAX_RATE | NUMBER(5,4) | |
| BASE_TAX_AMOUNT | NUMBER(12,2) | |
| Standard audit cols | | |
| Note | | 2024 federal brackets hard-coded in PKG_PAYROLL; table exists but is not read (TODO) |

#### EMPLOYEE_TAX_INFO
| Column | Type | Notes |
|---|---|---|
| TAX_INFO_ID | NUMBER | PK, SEQ_EMPLOYEE_TAX_INFO |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| FILING_STATUS / ALLOWANCES | VARCHAR2/NUMBER | |
| ADDITIONAL_WITHHOLDING | NUMBER(10,2) | |
| STATE_CODE | VARCHAR2(2) | Flat state tax rates in PKG_PAYROLL |
| EFFECTIVE_DATE / END_DATE | DATE | |
| Standard audit cols | | |

#### EMPLOYEE_BANK_ACCOUNTS
| Column | Type | Notes |
|---|---|---|
| ACCOUNT_ID | NUMBER | PK, SEQ_BANK_ACCOUNT |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| BANK_NAME / ROUTING_NUMBER / ACCOUNT_NUMBER | VARCHAR2 | Sensitive PII — encryption status unknown (not confirmed in source) |
| ACCOUNT_TYPE | VARCHAR2(20) | CHECKING / SAVINGS |
| IS_PRIMARY | CHAR(1) | |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' |
| Standard audit cols | | |

#### LEAVE_TYPES
| Column | Type | Notes |
|---|---|---|
| LEAVE_TYPE_ID | NUMBER | PK, SEQ_LEAVE_TYPE |
| LEAVE_CODE / LEAVE_NAME | VARCHAR2 | |
| ACCRUAL_RATE | NUMBER(5,2) | Days per month |
| MAX_BALANCE / MAX_CARRYOVER | NUMBER(5,2) | |
| REQUIRES_APPROVAL | CHAR(1) | 'N' = auto-approve in PKG_LEAVE |
| IS_PAID / IS_ACCRUAL_TYPE | CHAR(1) | |
| MIN_TENURE_MONTHS | NUMBER | |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' |
| Standard audit cols | | |
| Seed data | 6 rows | Full accrual business rules defined |

#### LEAVE_BALANCES
| Column | Type | Notes |
|---|---|---|
| BALANCE_ID | NUMBER | PK, SEQ_LEAVE_BALANCE |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| LEAVE_TYPE_ID | NUMBER | FK→LEAVE_TYPES |
| FISCAL_YEAR | NUMBER | |
| OPENING_BALANCE / ACCRUED / USED / ADJUSTMENT / PENDING | NUMBER(5,2) | |
| AVAILABLE | NUMBER | Virtual column: OPENING+ACCRUED-USED+ADJUSTMENT-PENDING |
| Standard audit cols | | |

**DISC-002**: VW_LEAVE_SUMMARY calculates AVAILABLE as OPENING+ACCRUED-USED+ADJUSTMENT (4 terms, omits PENDING). LEAVE_BALANCES virtual column uses 5 terms (includes -PENDING). These produce different available-balance figures for employees with pending leave.

#### LEAVE_REQUESTS
| Column | Type | Notes |
|---|---|---|
| REQUEST_ID | NUMBER | PK, SEQ_LEAVE_REQUEST |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| LEAVE_TYPE_ID | NUMBER | FK→LEAVE_TYPES |
| START_DATE / END_DATE | DATE | |
| DAYS_REQUESTED | NUMBER(5,2) | |
| STATUS | VARCHAR2(20) | PENDING / APPROVED / REJECTED / CANCELLED |
| REASON / REJECTION_REASON | VARCHAR2(500) | |
| APPROVED_BY / APPROVED_DATE | NUMBER/DATE | |
| Standard audit cols | | |
| Audit trigger | TRG_LEAVE_REQUEST_AUDIT | AFTER UPDATE OF STATUS → PKG_AUDIT.log_action |

#### LEAVE_ACCRUAL_LOG
| Column | Type | Notes |
|---|---|---|
| ACCRUAL_ID | NUMBER | PK, SEQ_LEAVE_ACCRUAL |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| LEAVE_TYPE_ID | NUMBER | FK→LEAVE_TYPES |
| ACCRUAL_DATE | DATE | |
| ACCRUAL_AMOUNT | NUMBER(5,2) | |
| ACCRUAL_TYPE | VARCHAR2(20) | MONTHLY / CARRYOVER / MANUAL |
| Standard audit cols | | |

#### HOLIDAYS
| Column | Type | Notes |
|---|---|---|
| HOLIDAY_ID | NUMBER | PK, SEQ_HOLIDAY |
| HOLIDAY_DATE | DATE | |
| HOLIDAY_NAME | VARCHAR2(100) | |
| IS_GLOBAL | CHAR(1) | All 10 seed rows = 'Y' |
| LOCATION_ID | NUMBER | FK→LOCATIONS (nullable for global) |
| Standard audit cols | | |
| Seed data | 10 rows | 2024 US federal holidays; all global |

#### REVIEW_CYCLES
| Column | Type | Notes |
|---|---|---|
| CYCLE_ID | NUMBER | PK, SEQ_REVIEW_CYCLE |
| CYCLE_NAME / CYCLE_TYPE | VARCHAR2 | |
| START_DATE / END_DATE | DATE | |
| STATUS | VARCHAR2(20) | DRAFT / OPEN / CLOSED |
| Standard audit cols | | |

#### PERFORMANCE_REVIEWS
| Column | Type | Notes |
|---|---|---|
| REVIEW_ID | NUMBER | PK, SEQ_PERFORMANCE_REVIEW |
| CYCLE_ID | NUMBER | FK→REVIEW_CYCLES |
| EMP_ID | NUMBER | FK→EMPLOYEES (reviewee) |
| REVIEWER_ID | NUMBER | FK→EMPLOYEES (manager) |
| STATUS | VARCHAR2(30) | NOT_STARTED → MANAGER_REVIEW → COMPLETED → ACKNOWLEDGED |
| SELF_ASSESSMENT / MANAGER_COMMENTS | CLOB | |
| OVERALL_RATING | NUMBER(3,1) | 1.0–5.0 |
| Standard audit cols | | |

#### PERFORMANCE_GOALS
| Column | Type | Notes |
|---|---|---|
| GOAL_ID | NUMBER | PK, SEQ_PERFORMANCE_GOAL |
| REVIEW_ID | NUMBER | FK→PERFORMANCE_REVIEWS |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| GOAL_DESCRIPTION | CLOB | |
| TARGET_DATE | DATE | |
| PROGRESS_PERCENTAGE | NUMBER(5,2) | |
| STATUS | VARCHAR2(20) | |
| Standard audit cols | | |

#### AUDIT_LOG
| Column | Type | Notes |
|---|---|---|
| LOG_ID | NUMBER | PK, SEQ_AUDIT (CACHE 100) |
| ACTION_TYPE | VARCHAR2(50) | INSERT/UPDATE/DELETE/ERROR_LOG/INFO_LOG |
| TABLE_NAME | VARCHAR2(50) | Or 'ERROR_LOG'/'INFO_LOG' for PKG_COMMON logs |
| RECORD_ID | NUMBER | |
| OLD_VALUES / NEW_VALUES | CLOB | JSON format |
| PERFORMED_BY | VARCHAR2(100) | |
| IP_ADDRESS | VARCHAR2(50) | From SYS_CONTEXT(USERENV,'IP_ADDRESS') |
| ACTION_DATE | DATE | |
| Standard audit cols | | |

#### SYSTEM_PARAMETERS
| Column | Type | Notes |
|---|---|---|
| PARAM_ID | NUMBER | PK |
| PARAM_KEY | VARCHAR2(100) | NOT NULL UNIQUE |
| PARAM_VALUE | VARCHAR2(500) | |
| PARAM_TYPE | VARCHAR2(20) | STRING/NUMBER/DATE/BOOLEAN |
| EDITABLE_FLAG | CHAR(1) | 'Y' allows set_param updates |
| DESCRIPTION | VARCHAR2(500) | |
| Standard audit cols | | |
| Seed data (10 rows) | SESSION_TIMEOUT_MIN=30, PASSWORD_MIN_LENGTH=8, SMTP_HOST=smtp.internal.company.com, GL_FEED_STATUS=ACTIVE, BENEFITS_FEED_STATUS=ACTIVE, + 5 others | FTP credentials also stored here in cleartext (PKG_INTEGRATION known issue) |

#### NOTIFICATION_QUEUE
| Column | Type | Notes |
|---|---|---|
| NOTIFICATION_ID | NUMBER | PK, SEQ_NOTIFICATION |
| RECIPIENT_EMAIL | VARCHAR2(200) | |
| SUBJECT / BODY | VARCHAR2(500)/CLOB | |
| STATUS | VARCHAR2(20) | PENDING / SENT / FAILED |
| RETRY_COUNT | NUMBER | DEFAULT 0; max 3 |
| SCHEDULED_DATE / SENT_DATE | DATE | |
| Standard audit cols | | |

#### USER_SESSIONS
| Column | Type | Notes |
|---|---|---|
| SESSION_ID | VARCHAR2(100) | PK |
| EMP_ID | NUMBER | FK→EMPLOYEES |
| LOGIN_TIME / LAST_ACTIVITY | DATE | Timeout calculated from LOGIN_TIME (not LAST_ACTIVITY — no session refresh) |
| IP_ADDRESS | VARCHAR2(50) | |
| STATUS | VARCHAR2(20) | ACTIVE / EXPIRED |
| Standard audit cols | | |

#### LOOKUP_VALUES
| Column | Type | Notes |
|---|---|---|
| LOOKUP_ID | NUMBER | PK, SEQ_LOOKUP |
| LOOKUP_TYPE | VARCHAR2(50) | |
| LOOKUP_CODE | VARCHAR2(50) | |
| LOOKUP_VALUE | VARCHAR2(200) | |
| DISPLAY_ORDER | NUMBER | |
| ACTIVE_FLAG | CHAR(1) | DEFAULT 'Y' |
| Standard audit cols | | |

---

### Views (6 of 15 documented; 9 not in scan set)

| View Name | Source | Key Logic | Notes |
|---|---|---|---|
| VW_ACTIVE_EMPLOYEES | hrms_views.sql | JOIN EMPLOYEES, DEPARTMENTS, JOB_TITLES, JOB_GRADES, LOCATIONS, SALARY_RECORDS (current) | Denormalized active employee view; filters ACTIVE_FLAG='Y' and EMPLOYMENT_STATUS='ACTIVE' |
| VW_ORG_HIERARCHY | hrms_views.sql | CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID | Recursive hierarchy; comment warns timeout >500 employees |
| VW_EMPLOYEE_COMPENSATION | hrms_views.sql | Compa-ratio = AVG(salary/midpoint)*100 | Joins JOB_GRADES |
| VW_LEAVE_SUMMARY | hrms_views.sql | AVAILABLE = OPENING+ACCRUED-USED+ADJUSTMENT (4 terms) | **DISC-002**: Missing PENDING subtraction vs. LEAVE_BALANCES virtual column |
| VW_PAYROLL_LATEST | hrms_views.sql | Latest APPROVED payroll run per employee | Filters STATUS='APPROVED' |
| VW_PENDING_APPROVALS | hrms_views.sql | UNION ALL of PENDING leave requests + MANAGER_REVIEW performance reviews | Manager dashboard feed |

---

### All 29 Sequences

| Sequence Name | Start Value | Increment | Cache | Min | Max | Notes |
|---|---|---|---|---|---|---|
| SEQ_EMPLOYEE | 10000 | 1 | NOCACHE | 10000 | default | PK for EMPLOYEES |
| SEQ_DEPARTMENT | 100 | 1 | NOCACHE | 100 | default | PK for DEPARTMENTS |
| SEQ_LOCATION | 100 | 1 | NOCACHE | 100 | default | PK for LOCATIONS |
| SEQ_JOB_GRADE | 100 | 1 | NOCACHE | 100 | default | PK for JOB_GRADES |
| SEQ_JOB_TITLE | 100 | 1 | NOCACHE | 100 | default | PK for JOB_TITLES |
| SEQ_SALARY | 1 | 1 | NOCACHE | 1 | default | PK for SALARY_RECORDS |
| SEQ_PAY_ELEMENT | 1 | 1 | NOCACHE | 1 | default | PK for PAY_ELEMENTS |
| SEQ_EMP_PAY_ELEMENT | 1 | 1 | NOCACHE | 1 | default | PK for EMPLOYEE_PAY_ELEMENTS |
| SEQ_PAY_PERIOD | 1 | 1 | NOCACHE | 1 | default | PK for PAY_PERIODS |
| SEQ_PAYROLL_RUN | 1 | 1 | NOCACHE | 1 | default | PK for PAYROLL_RUNS |
| SEQ_PAYROLL_DETAIL | 1 | 1 | NOCACHE | 1 | default | PK for PAYROLL_DETAILS |
| SEQ_TAX_BRACKET | 1 | 1 | NOCACHE | 1 | default | PK for TAX_BRACKETS |
| SEQ_EMPLOYEE_TAX_INFO | 1 | 1 | NOCACHE | 1 | default | PK for EMPLOYEE_TAX_INFO |
| SEQ_BANK_ACCOUNT | 1 | 1 | NOCACHE | 1 | default | PK for EMPLOYEE_BANK_ACCOUNTS |
| SEQ_LEAVE_TYPE | 1 | 1 | NOCACHE | 1 | default | PK for LEAVE_TYPES |
| SEQ_LEAVE_BALANCE | 1 | 1 | NOCACHE | 1 | default | PK for LEAVE_BALANCES |
| SEQ_LEAVE_REQUEST | 1 | 1 | NOCACHE | 1 | default | PK for LEAVE_REQUESTS |
| SEQ_LEAVE_ACCRUAL | 1 | 1 | NOCACHE | 1 | default | PK for LEAVE_ACCRUAL_LOG |
| SEQ_HOLIDAY | 1 | 1 | NOCACHE | 1 | default | PK for HOLIDAYS |
| SEQ_REVIEW_CYCLE | 1 | 1 | NOCACHE | 1 | default | PK for REVIEW_CYCLES |
| SEQ_PERFORMANCE_REVIEW | 1 | 1 | NOCACHE | 1 | default | PK for PERFORMANCE_REVIEWS |
| SEQ_PERFORMANCE_GOAL | 1 | 1 | NOCACHE | 1 | default | PK for PERFORMANCE_GOALS |
| SEQ_AUDIT | 1 | 1 | CACHE 100 | 1 | default | PK for AUDIT_LOG — only cached sequence; high-volume logging |
| SEQ_NOTIFICATION | 1 | 1 | NOCACHE | 1 | default | PK for NOTIFICATION_QUEUE |
| SEQ_EMP_HISTORY | 1 | 1 | NOCACHE | 1 | default | PK for EMPLOYEE_HISTORY — referenced as SEQ_EMP_HISTORY in TRG_EMP_BEFORE_UPDATE |
| SEQ_DEPENDENT | 1 | 1 | NOCACHE | 1 | default | PK for EMPLOYEE_DEPENDENTS |
| SEQ_EMERGENCY_CONTACT | 1 | 1 | NOCACHE | 1 | default | PK for EMERGENCY_CONTACTS |
| SEQ_LOOKUP | 1 | 1 | NOCACHE | 1 | default | PK for LOOKUP_VALUES |
| SEQ_LOOKUP_VALUE | 1 | 1 | NOCACHE | 1 | default | Possible alias/second sequence for LOOKUP_VALUES — verify with Agent 2 |

**Note**: All 29 sequences use NOCACHE except SEQ_AUDIT (CACHE 100). NOCACHE on high-volume tables (payroll details, audit, notifications) creates a serialization bottleneck under concurrent load — flagged for Agent 2 performance analysis.

---

### Oracle Directory Objects (UTL_FILE targets)

| Directory Object Name | Direction | Consumer Package | File Type | Notes |
|---|---|---|---|---|
| GL_FEED_OUT | Outbound | PKG_INTEGRATION.generate_gl_journal | Pipe-delimited .dat | Oracle Financials GL integration |
| BENEFITS_FEED_OUT | Outbound | PKG_INTEGRATION.export_benefits_feed | Fixed-width 203-char | ADP Benefits integration |
| TIME_ATTENDANCE_IN | Inbound | PKG_INTEGRATION.import_time_attendance | CSV | Import parsing is TODO/not implemented |
| PAYROLL_OUTPUT | Outbound | PKG_PAYROLL.generate_pay_register | CSV | Pay register report output |

---

## OUTPUT 4 — INFRASTRUCTURE & DEPLOYMENT BLUEPRINT

### Compute & Application Server Resources

| Resource | Technology | Version | Configuration | Source | Confidence |
|---|---|---|---|---|---|
| Application Server | Oracle WebLogic Server | 12c | Hosts Oracle Forms runtime; serves Forms applet via HTTP/HTTPS + Java Web Start (JNLP) | README.md | HIGH |
| Database Server | Oracle Database | 19c | Single instance; schema HRMS; 42 tables, 200+ triggers, 15 views | README.md + DDL files | HIGH |
| Oracle Forms Runtime | Oracle Forms Services | 12c (12.2.1.4) | Fat-client rendering via WebLogic; HRMS_LOGIN.xml is entry point | README.md + form XML exports | HIGH |
| DBMS_SCHEDULER | Oracle built-in job scheduler | Oracle 19c | Job 1: PKG_NOTIFICATION.process_queue every 5 min; Job 2: PKG_LEAVE.run_monthly_accrual monthly | PKG_NOTIFICATION.pkb, PKG_LEAVE.pkb | HIGH |
| SMTP Relay | Internal mail server | Unknown | smtp.internal.company.com:25 (plaintext, no TLS/STARTTLS) | PKG_NOTIFICATION.pkb constant | HIGH |
| File System | Oracle Database OS (UTL_FILE) | Oracle 19c | 4 directory objects; paths configured as Oracle Directory Objects in DB | PKG_INTEGRATION.pkb, PKG_PAYROLL.pkb | HIGH |

### Environments Identified

| Environment | Evidence | Details |
|---|---|---|
| Production (inferred) | README, seed data, SYSTEM_PARAMETERS | 3 regional offices: HQ (New York), Chicago, San Francisco; ~200 concurrent users |
| Development/Test | Git repository present | No environment-specific config files found; no .env files; no environment differentiation in code |
| Staging | NOT DETECTED | No staging environment references found in any scanned file |

**ARCHITECTURE NOTE**: No environment separation configuration found. No .env files, no environment-specific property files, no WebLogic domain config files included in scan set. Infrastructure configuration detail is LOW — only inferred from application-level code and README.

### CI/CD Pipeline Inventory

**CI/CD LAYER: NONE DETECTED**

| Check | Result |
|---|---|
| Dockerfile | Not found |
| docker-compose.yml | Not found |
| Jenkinsfile | Not found |
| .github/workflows/*.yml | Not found |
| .gitlab-ci.yml | Not found |
| azure-pipelines.yml | Not found |
| Terraform (.tf files) | Not found |
| Ansible playbooks | Not found |
| Kubernetes manifests (.yaml) | Not found |
| Build scripts (Makefile, pom.xml, build.gradle) | Not found |
| Deployment scripts (.sh) | Not found |

**Conclusion**: This is a traditional Oracle Forms application with no modern CI/CD tooling. Deployment is presumed to be manual — DBA executes DDL/DML scripts, deploys .fmx/.rdf files to WebLogic-managed directories, applies PL/SQL package recompilation manually.

### Network Topology (Inferred)

```
[Client Browser / Java Web Start]
        |
        | HTTP/HTTPS (WebLogic HTTP listener)
        |
[Oracle WebLogic 12c — Application Server]
   - Oracle Forms Services runtime
   - Serves .fmx modules
   - Manages Forms sessions
        |
        | JDBC (Oracle thin/OCI)
        |
[Oracle Database 19c — HRMS Schema]
   - 42 tables, 200+ triggers
   - 12 PL/SQL packages
   - 4 Directory Objects (filesystem I/O)
   - DBMS_SCHEDULER jobs
        |
        |-- UTL_FILE --> [OS Filesystem / NFS share]
        |                  GL_FEED_OUT, BENEFITS_FEED_OUT,
        |                  TIME_ATTENDANCE_IN, PAYROLL_OUTPUT
        |
        |-- UTL_SMTP --> [smtp.internal.company.com:25]
                            --> Employee/manager email notifications

[External Systems — file-based, no real-time API]
   Oracle Financials GL <-- pipe-delimited .dat (batch)
   ADP Benefits <-- fixed-width 203-char (batch)
   Time & Attendance --> CSV inbound (parsing NOT implemented)
   LDAP/Active Directory <-- STUB (not implemented)
```

**Deployment Region**: United States — 3 offices (New York HQ, Chicago, San Francisco). No cloud provider, no CDN, no load balancer referenced.

---

## OUTPUT 5 — INTEGRATION & DEPENDENCY GRAPH

### External System Integrations

| # | External System | Direction | Protocol/Mechanism | Format | Status | Source | Security Notes |
|---|---|---|---|---|---|---|---|
| 1 | Oracle Financials GL | Outbound (DB → GL) | UTL_FILE to Oracle Directory GL_FEED_OUT | Pipe-delimited .dat; H/D/T record structure; debit=EARNING, credit=DEDUCTION/TAX | ACTIVE (GL_FEED_STATUS=ACTIVE in SYSTEM_PARAMETERS) | PKG_INTEGRATION.generate_gl_journal | FTP credentials stored in SYSTEM_PARAMETERS cleartext |
| 2 | ADP Benefits | Outbound (DB → ADP) | UTL_FILE to Oracle Directory BENEFITS_FEED_OUT | Fixed-width 203-char flat file; LEFT JOIN dependents | ACTIVE (BENEFITS_FEED_STATUS=ACTIVE in SYSTEM_PARAMETERS) | PKG_INTEGRATION.export_benefits_feed | FTP credentials stored in SYSTEM_PARAMETERS cleartext |
| 3 | Time & Attendance System | Inbound (T&A → DB) | UTL_FILE from Oracle Directory TIME_ATTENDANCE_IN | CSV (inbound) | STUB — parsing logic is TODO/not implemented | PKG_INTEGRATION.import_time_attendance | N/A |
| 4 | LDAP / Active Directory | Outbound (DB → LDAP) | Stub only | Unknown | STUB — not implemented | PKG_INTEGRATION.sync_org_structure | N/A |
| 5 | SMTP Email Relay | Outbound (DB → SMTP) | UTL_SMTP per-connection per-message | MIME plaintext email | ACTIVE (DBMS_SCHEDULER job every 5 min) | PKG_NOTIFICATION.process_queue | smtp.internal.company.com:25; NO TLS/STARTTLS; emails contain PII (employee names, HR actions) |

### Internal Cross-Package Dependency Graph

```
Forms Layer (HRMS_LOGIN, HRMS_MENU, HRMS_EMPLOYEE, HRMS_LEAVE, HRMS_PAYROLL, HRMS_PERFORMANCE)
    |
    |---> HRMS_COMMON_LIB.pll -----> PKG_COMMON.log_error
    |                          \---> PKG_SECURITY.is_session_valid
    |
    |---> HRMS_VALIDATION_LIB.pll -> JOB_GRADES (direct table query)
    |
    |---> PKG_SECURITY <-----------> USER_SESSIONS, EMPLOYEES
    |         |
    |         \--> DBMS_CRYPTO, SYS_CONTEXT
    |
    |---> PKG_EMPLOYEE <-- -----> EMPLOYEES, EMPLOYEE_HISTORY
    |         |  ^                SALARY_RECORDS
    |         |  | (circular)
    |         v  |
    |       PKG_PAYROLL <-------> PAYROLL_RUNS, PAYROLL_DETAILS, TAX_BRACKETS
    |         |                   UTL_FILE (PAYROLL_OUTPUT)
    |         \-----> PKG_AUDIT, PKG_NOTIFICATION
    |
    |---> PKG_LEAVE <-----------> LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_ACCRUAL_LOG
    |         \-----> PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON
    |
    |---> PKG_PERFORMANCE <-----> REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS
    |         \-----> PKG_AUDIT, PKG_NOTIFICATION
    |
    |---> PKG_REPORTING <-------> VW_ACTIVE_EMPLOYEES, SALARY_RECORDS, LEAVE_REQUESTS
    |         (refresh_reporting_tables = STUB)
    |
    |---> PKG_VALIDATION <------> JOB_GRADES, HOLIDAYS, PKG_COMMON
    |
    |---> PKG_INTEGRATION <-----> UTL_FILE (4 directory objects)
    |         \-----> PKG_AUDIT, PKG_COMMON, SYSTEM_PARAMETERS
    |
    |---> PKG_COMMON <----------> AUDIT_LOG, SYSTEM_PARAMETERS
    |
    |---> PKG_AUDIT <-----------> AUDIT_LOG (SEQ_AUDIT CACHE 100)
    |         \-----> SYS_CONTEXT
    |
    \---> PKG_NOTIFICATION <----> NOTIFICATION_QUEUE, UTL_SMTP
              \-----> DBMS_SCHEDULER
```

**Circular Dependency**: PKG_EMPLOYEE ↔ PKG_PAYROLL
- PKG_EMPLOYEE.create_employee calls PKG_PAYROLL.create_salary_record
- PKG_PAYROLL.calculate_employee_pay calls PKG_EMPLOYEE.is_active
- This creates a compile-order dependency; one package must be compiled as spec-only first

**Hub Packages** (most-depended-upon, highest blast radius for changes):
1. PKG_AUDIT — called by all domain packages and all audit triggers
2. PKG_COMMON — called by nearly all packages; base utility hub
3. PKG_NOTIFICATION — called by PKG_EMPLOYEE, PKG_LEAVE, PKG_PERFORMANCE, PKG_PAYROLL
4. PKG_SECURITY — called by all Forms modules and PKG_EMPLOYEE

### Build & Developer Toolchain

| Tool | Evidence | Notes |
|---|---|---|
| SQL*Plus or SQLcl | Implied by .sql file naming convention | Standard Oracle DDL/DML deployment tool; no explicit build file found |
| Oracle Forms Builder | .fmb source files referenced (scan has .xml exports) | .fmb → .fmx compilation required for deployment |
| Oracle Reports Builder | .rdf source files referenced | Not in scan set |
| Git | .git directory present | Version control in use; no CI hooks observed |
| No build automation | NONE DETECTED | No Maven, Gradle, Ant, Make, or shell build scripts found |

---

## OUTPUT 6 — SECURITY & CONFIGURATION SNAPSHOT

### Authentication & Authorisation Mechanisms

| Mechanism | Implementation | Location | Risk Level | Notes |
|---|---|---|---|---|
| User Authentication | PKG_SECURITY.authenticate — username (EMPLOYEES.EMAIL, case-insensitive) + password hash comparison | PKG_SECURITY.pkb | CRITICAL | Password verification logic is documented as incomplete/stub in code comments; ROWNUM=1 silently resolves duplicate email collision; no account lockout |
| Password Hashing | MD5 via DBMS_CRYPTO.HASH | PKG_SECURITY.pkb (hash_password) | CRITICAL | MD5 is cryptographically broken; susceptible to rainbow table attacks; should be bcrypt/scrypt/Argon2 |
| Session Management | SESSION_ID in USER_SESSIONS; 30-minute timeout from LOGIN_TIME (not LAST_ACTIVITY) | PKG_SECURITY.is_session_valid | HIGH | Timeout calculated from LOGIN_TIME — any active session expires 30 min from login regardless of activity; no session refresh/touch mechanism |
| Account Lockout | NONE | PKG_SECURITY.pkb | HIGH | No failed login counter; brute-force attack not mitigated |
| Password Transmission | Cleartext through Oracle Forms applet | HRMS_LOGIN.xml, README | HIGH | Oracle Forms limitation; password travels in cleartext from client to WebLogic |
| Authorisation Model | Grade-based permissions in PKG_SECURITY.has_permission | PKG_SECURITY.pkb | MEDIUM | Grade >=8: full access; Grade >=5: VIEW all modules; everyone: LEAVE CREATE/VIEW + EMPLOYEE VIEW; fine-grained action permissions (PAYROLL APPROVE etc.) checked per button/form |
| Menu/Button Security | PKG_SECURITY.has_permission checked at WHEN-NEW-FORM-INSTANCE and button triggers | HRMS_MENU.xml, HRMS_PAYROLL.xml | MEDIUM | BTN_LEAVE and BTN_PERFORMANCE in HRMS_MENU.xml have NO permission check — any authenticated user can access |
| Change Password | PKG_SECURITY.change_password — validates min 8 chars + uppercase + digit; actual credential update is stub | PKG_SECURITY.pkb | HIGH | Password change not fully implemented |

### Secrets & Configuration Management

| Secret / Config Item | Storage Location | Exposure | Risk Level | Notes |
|---|---|---|---|---|
| AES-256 Encryption Key | Hard-coded constant in PKG_SECURITY.pkb package body | Source code / compiled package body in DB | CRITICAL | Key name: `c_encryption_key` (value flagged but NOT reproduced per security policy); used for SSN encryption/decryption; rotating requires recompile + re-encryption of all stored SSNs |
| MD5 Password Hashes | EMPLOYEES.PASSWORD_HASH column | Database — accessible to any schema user with SELECT on EMPLOYEES | CRITICAL | MD5 hashes are reversible with rainbow tables |
| FTP Credentials | SYSTEM_PARAMETERS table, PARAM_KEY values (plaintext) | Database — accessible to any schema user with SELECT on SYSTEM_PARAMETERS | HIGH | Used by PKG_INTEGRATION for file transfer to GL/ADP; cleartext storage; no encryption at rest |
| SMTP Host | SYSTEM_PARAMETERS (SMTP_HOST=smtp.internal.company.com) | Database | LOW | Not a secret, but documents internal network topology |
| Session Timeout | SYSTEM_PARAMETERS (SESSION_TIMEOUT_MIN=30) | Database (readable) | INFO | Configuration, not a secret |
| Database Connection | Oracle Forms → WebLogic JDBC datasource | WebLogic config (not in scan set) | MEDIUM | Connection string/credentials not in scan set; assumed in WebLogic domain configuration |
| Bank Account Numbers | EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER/ROUTING_NUMBER | Database — encryption status UNKNOWN | HIGH | No encryption confirmed in source; SSN is encrypted but bank account status unclear |
| Oracle Directory Paths | Configured as Oracle Directory Objects in DB | DB catalog (DBA_DIRECTORIES) | MEDIUM | Physical paths not visible in scan set |

### Network Security Declarations

| Protocol/Port | Usage | TLS/Encryption | Risk | Notes |
|---|---|---|---|---|
| HTTP/HTTPS | WebLogic → Oracle Forms client | Unknown (depends on WebLogic SSL config, not in scan set) | MEDIUM | TLS configuration not confirmed from scanned files |
| SMTP port 25 | PKG_NOTIFICATION → smtp.internal.company.com | NO TLS, NO STARTTLS | HIGH | Plaintext SMTP; emails contain PII (employee names, HR workflow notifications) |
| Oracle Net (SQL*Net) | Forms/WebLogic → Oracle 19c DB | Unknown (depends on sqlnet.ora, not in scan set) | MEDIUM | Encryption configuration not confirmed |
| UTL_FILE | Database → OS filesystem | N/A (local OS) | MEDIUM | 4 directory objects; actual paths and permissions not in scan set |
| FTP (implied) | PKG_INTEGRATION → GL/ADP external systems | Unknown (FTP implies plaintext) | HIGH | FTP credentials in SYSTEM_PARAMETERS; FTP = plaintext unless SFTP/FTPS |

### Compliance & Audit Flags

| Category | Finding | Tables/Objects | Risk / Compliance Relevance |
|---|---|---|---|
| PII Inventory | SSN stored encrypted (AES-256) in EMPLOYEES and EMPLOYEE_DEPENDENTS | EMPLOYEES.SSN, EMPLOYEE_DEPENDENTS.SSN | GDPR/CCPA — encryption at rest present but key management inadequate (hard-coded) |
| PII Inventory | Bank account numbers — encryption status unconfirmed | EMPLOYEE_BANK_ACCOUNTS | PCI-DSS adjacent; HIGH risk if stored plaintext |
| PII Inventory | Gender, ethnicity, veteran_status, disability_status stored | EMPLOYEES | EEO regulatory requirement; also GDPR sensitive category data |
| PII Inventory | Date of birth, full address, emergency contacts | EMPLOYEES, EMPLOYEE_DEPENDENTS, EMERGENCY_CONTACTS | GDPR/CCPA — access control and retention policy needed |
| Audit Logging | AUDIT_LOG table captures all INSERT/UPDATE/DELETE with old/new JSON values and IP address | AUDIT_LOG, PKG_AUDIT | SOX/HR compliance positive; but failures silently swallowed (no alert on audit failure) |
| Audit Logging | 365-day default retention (PKG_AUDIT.purge_old_records) | AUDIT_LOG | May be insufficient for some regulatory frameworks (SOX = 7 years) |
| EEO Compliance | PKG_REPORTING.eeo_compliance_report — gender breakdown by EEO_CATEGORY | EMPLOYEES, JOB_TITLES | EEO-1 reporting support present |
| Tax Compliance | 2024 federal tax brackets hard-coded in PKG_PAYROLL; TAX_BRACKETS table exists but not read | PKG_PAYROLL.pkb, TAX_BRACKETS | Compliance risk — stale tax rates for any year != 2024 |
| SQL Injection | PKG_EMPLOYEE.search_employees builds dynamic SQL via string concatenation for p_last_name / p_first_name | PKG_EMPLOYEE.pkb | OWASP A03; direct DB-level injection risk; should use DBMS_SQL with bind variables |
| Access Control Gap | BTN_LEAVE and BTN_PERFORMANCE in HRMS_MENU have no permission check | HRMS_MENU.xml | Any authenticated user can open Leave and Performance forms |
| Data Integrity | DISC-001: TRG_EMP_BEFORE_UPDATE column name mismatch with EMPLOYEE_HISTORY DDL | TRG_EMPLOYEES.SQL, 01_core_tables.sql | Employee history records likely silently failing to insert; change audit trail broken |
| Data Accuracy | DISC-002: VW_LEAVE_SUMMARY AVAILABLE balance omits PENDING subtraction | hrms_views.sql, 03_leave_tables.sql | Employees and managers see inflated available leave balance in the view |
| Data Integrity | DISC-003: Hire date future limit is 90 days in form but 180 days in DB trigger | HRMS_EMPLOYEE.xml, trg_employees.sql | Form validation and DB enforcement are inconsistent; authoritative rule unclear |
| Partial Commit Risk | PKG_PAYROLL.calculate_payroll commits every 50 employees | PKG_PAYROLL.pkb | On error mid-run, some employees are paid and committed, others are not; no compensating rollback |
| Partial Commit Risk | PKG_LEAVE.run_monthly_accrual commits every 100 employees | PKG_LEAVE.pkb | Same partial-commit risk pattern |
| Race Condition | PKG_EMPLOYEE.generate_emp_number uses MAX()+1 without SELECT FOR UPDATE | PKG_EMPLOYEE.pkb | Duplicate EMP_NUMBER possible under concurrent employee creation |
| Unimplemented Features | YTD_GROSS/YTD_NET = 0 placeholders in payslip functions | PKG_PAYROLL.pkb | Year-to-date payroll figures not calculated; payslips show incorrect 0 values |
| Unimplemented Features | Time & Attendance import parsing | PKG_INTEGRATION.pkb | Inbound T&A data silently ignored |
| Unimplemented Features | LDAP sync | PKG_INTEGRATION.pkb | No automated user provisioning/deprovisioning |
| Unimplemented Features | COBRA notification on termination | PKG_EMPLOYEE.pkb (terminate_employee TODO) | Regulatory compliance gap |
| Circular Dependency | PKG_EMPLOYEE ↔ PKG_PAYROLL | PKG_EMPLOYEE.pkb, PKG_PAYROLL.pkb | Deployment/compilation order must be managed manually |

---

## VALIDATION QUEUE

Items requiring Agent 2 investigation or authoritative determination:

### DISC (Discovered Discrepancies) — Require Resolution

| ID | Type | Description | Sources in Conflict | Agent 2 Action |
|---|---|---|---|---|
| DISC-001 | Column Name Mismatch | TRG_EMP_BEFORE_UPDATE writes to HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE. EMPLOYEE_HISTORY DDL defines HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_TITLE_ID, NEW_JOB_TITLE_ID, OLD_GRADE_ID, NEW_GRADE_ID. INSERT in trigger almost certainly fails silently at runtime (ORA-00904 invalid identifier). | trg_employees.sql vs. 01_core_tables.sql | Determine authoritative column schema; assess whether employee history has NEVER been captured in production |
| DISC-002 | View Logic Bug | VW_LEAVE_SUMMARY.AVAILABLE = OPENING_BALANCE+ACCRUED-USED+ADJUSTMENT (4 terms). LEAVE_BALANCES.AVAILABLE virtual column = same 4 terms MINUS PENDING. Employees with pending leave see a higher available balance in the view than the actual balance column. | hrms_views.sql vs. 03_leave_tables.sql | Confirm correct formula; document business impact (overstated available leave visible to employees and managers via view) |
| DISC-003 | Business Rule Conflict | Hire date future limit: HRMS_EMPLOYEE.xml form trigger rejects >90 days; TRG_EMP_BEFORE_INSERT rejects >180 days. DB trigger wins for any non-Forms insert. The two limits have been coexisting — either by accident or design. | HRMS_EMPLOYEE.xml vs. trg_employees.sql | Determine authoritative rule; document which path (form vs. DB trigger) is enforced in each scenario |

### LOW Confidence Items — Require Verification

| ID | Item | Current Confidence | Why Low | What Agent 2 Should Verify |
|---|---|---|---|---|
| LC-001 | PKG_DEPARTMENT | LOW | Source file not in scan set; only referenced in README | Obtain PKG_DEPARTMENT.pks/.pkb; document its procedures, dependencies, and tables accessed |
| LC-002 | 12 Undocumented Tables | LOW | Not in scan set (DDL files incomplete) | Identify all 42 tables; document the 12 missing ones — expected candidates include EMPLOYEE_CERTIFICATIONS, EMPLOYEE_TRAINING, PAYROLL_TAX_SUMMARY, and others |
| LC-003 | 9 Undocumented Views | LOW | Only 6 of 15 views in scan set | Obtain hrms_views.sql complete file or individual view definitions |
| LC-004 | Oracle Reports (8 files) | LOW | .rdf/.rep files not in scan set | Identify 8 report modules; document data sources, parameters, distribution method |
| LC-005 | 200+ Triggers (only 6 scanned) | LOW | README states 200+ triggers; only trg_audit.sql and trg_employees.sql found | Obtain remaining trigger files; high probability of additional audit and validation triggers not yet catalogued |
| LC-006 | Bank Account Encryption | MEDIUM | EMPLOYEES.SSN confirmed AES-256 encrypted; EMPLOYEE_BANK_ACCOUNTS encryption not confirmed | Verify whether ROUTING_NUMBER/ACCOUNT_NUMBER are encrypted at rest |
| LC-007 | WebLogic TLS Configuration | LOW | WebLogic config files not in scan set | Confirm whether HTTP or HTTPS is enforced for Forms client connections |
| LC-008 | Oracle Net Encryption | LOW | sqlnet.ora not in scan set | Confirm whether Oracle Advanced Security / native network encryption is configured for DB connections |
| LC-009 | DBMS_SCHEDULER Job Definitions | MEDIUM | Inferred from PKG_NOTIFICATION.pkb and PKG_LEAVE.pkb comments | Obtain DBMS_SCHEDULER job DDL to confirm schedules, error handling, and job ownership |
| LC-010 | SEQ_LOOKUP_VALUE | LOW | 29th sequence — may be duplicate/alias of SEQ_LOOKUP | Verify whether both sequences exist in production schema; check for naming collision |
| LC-011 | FTP Mechanism | LOW | PKG_INTEGRATION references FTP credentials in SYSTEM_PARAMETERS but no FTP client code found in scan | Determine how files are actually transferred to GL/ADP — UTL_FILE writes to directory, then external FTP script? Or Oracle UTL_TCP/UTL_HTTP based transfer? |
| LC-012 | Audit Retention Compliance | MEDIUM | 365-day default retention documented; actual business requirement unknown | Confirm regulatory retention requirement for this organization; SOX = 7 years, EEOC = 1-2 years, HIPAA = 6 years |

### ARCHITECTURE NOTEs — No Scan Coverage

| ID | Note |
|---|---|
| ARCH-001 | CI/CD: No build pipeline, Dockerfile, IaC, or deployment scripts found. Manual deployment assumed. This is a significant operational risk — no repeatable, auditable deployment process. |
| ARCH-002 | Staging/UAT environment: No configuration or environment separation found. Unclear whether a non-production environment exists. |
| ARCH-003 | Disaster Recovery / High Availability: No Data Guard, GoldenGate, RMAN, or backup configuration found in scan set. HA/DR posture unknown. |
| ARCH-004 | Connection Pooling: WebLogic JDBC datasource configuration not in scan set. Connection pool settings (min/max connections, timeout) unknown. |
| ARCH-005 | Oracle Forms Version History: README documents migration path Forms 6i (2002) → 11g (2012) → 12c (current). Technical debt from 20+ years of evolution is likely present but not fully quantified from scan. |
| ARCH-006 | No API Layer: Zero REST/SOAP/GraphQL interfaces found. All integrations are file-based batch. System cannot be accessed programmatically by modern tooling without database-level connection. |

### VERSION CONFLICTs

| ID | Item | Version 1 | Version 2 | Source |
|---|---|---|---|---|
| VER-001 | Application version label | v4.2.0 (README) | v4.2 Build 2024.03.15 (HRMS_MENU.xml MI_ABOUT hard-coded string) | README.md vs. forms/xml-exports/HRMS_MENU.xml |

---

## HANDOFF NOTE TO AGENT 2 (TA Deep Analyst v2)

**From**: TA Agent 1 — Technology Stack Scout v2.0
**To**: TA Agent 2 — Deep Analyst v2
**Subject**: HRMS Oracle Forms Codebase — Layer 1 Scan Complete

---

### What Agent 1 Has Established

A complete structural scan of the HRMS Oracle Forms HRMS codebase has been performed. The system is a monolithic Oracle Forms 12c application with Oracle WebLogic 12c and Oracle Database 19c. All 11 available PL/SQL package source files have been catalogued. Six Oracle Forms XML exports, two PL/SQL library files, and all schema DDL have been fully read.

The six output files above represent the sum of Agent 1's findings. Everything in them is from direct source evidence unless marked LOW confidence or DISC/ARCH/LC.

---

### Priority Items for Agent 2

**CRITICAL — Address First:**

1. **DISC-001 (EMPLOYEE_HISTORY column mismatch)**: TRG_EMP_BEFORE_UPDATE almost certainly fails at runtime on every UPDATE to EMPLOYEES. This means the employee history trail is likely empty in production. This is the highest-priority data integrity finding.

2. **SQL Injection in PKG_EMPLOYEE.search_employees**: String concatenation of p_last_name and p_first_name into dynamic SQL. Direct database-level exploitation risk. Remediation: parameterized bind variables via DBMS_SQL or EXECUTE IMMEDIATE with bind array.

3. **Hard-coded AES-256 key in PKG_SECURITY.pkb**: The encryption key for all SSN data is compiled into the package body. Any DBA with SELECT on DBA_SOURCE can read it. Key rotation requires: recompile package, re-encrypt all SSN values in EMPLOYEES and EMPLOYEE_DEPENDENTS. Risk: if key is ever leaked, all stored SSNs are compromised retroactively.

4. **MD5 password hashing**: MD5 is trivially reversible. All 25 known employee passwords (seed data) and any production passwords are at risk. Migration path: change_password procedure should be updated to bcrypt/scrypt, force all users to reset on next login.

**HIGH — Investigate in Depth:**

5. **DISC-002 (VW_LEAVE_SUMMARY AVAILABLE formula)**: Employees and managers are likely seeing inflated available leave balances. Determine scope of business impact — does this affect leave approval decisions?

6. **DISC-003 (hire date 90 vs 180 day limit)**: Determine which value is the business requirement and align form and trigger.

7. **Partial commit risk in calculate_payroll and run_monthly_accrual**: Both procedures commit mid-loop. Design a compensating mechanism (savepoints, restart markers, or full-run atomicity).

8. **YTD fields are 0 placeholders**: No year-to-date payroll figures are computed. Payslips show $0 YTD. Employees and managers are receiving incorrect payroll documents.

9. **COBRA/access revocation stubs in terminate_employee**: Regulatory compliance gaps. Termination workflow is incomplete.

**MEDIUM — Complete the Inventory:**

10. **Obtain the 12 missing table definitions** (see LC-002). Run: `SELECT table_name FROM dba_tables WHERE owner='HRMS' ORDER BY 1;` in production to get the full list.

11. **Obtain PKG_DEPARTMENT source** (see LC-001).

12. **Obtain the 200+ trigger DDL** — particularly any triggers on PAYROLL_DETAILS, USER_SESSIONS, and NOTIFICATION_QUEUE which are not in the current scan set.

13. **Confirm bank account encryption status** (see LC-006). PCI-DSS risk if ROUTING_NUMBER/ACCOUNT_NUMBER are plaintext.

14. **Confirm DBMS_SCHEDULER job definitions** — schedules, job_action, error handling.

---

### Architectural Synthesis Observations (for Agent 2 to develop)

Agent 1 is prohibited from cross-layer synthesis. The following are enumerated facts, not conclusions — Agent 2 should synthesize:

- The grade-based permission model (PKG_SECURITY.has_permission) is the sole access control mechanism. There is no row-level security, no VPD, no Oracle Label Security. A Grade 8+ employee can read all EMPLOYEES data including SSN fields.
- All domain packages share PKG_AUDIT and PKG_COMMON as infrastructure. Changes to these two packages affect the entire system.
- The circular dependency PKG_EMPLOYEE ↔ PKG_PAYROLL means neither package can be recompiled independently without invalidating the other.
- NOCACHE on 28 of 29 sequences means every surrogate key assignment requires a serialized round-trip to SMON. Under 200 concurrent users performing inserts this creates measurable contention.
- The system has no API layer — zero REST/SOAP endpoints. Any modernization effort (mobile, SaaS integration, microservices extraction) must begin by wrapping packages in an API tier.
- DBMS_SCHEDULER is used for two recurring jobs (notification processing every 5 min, monthly leave accrual). If either job fails silently, there is no alerting mechanism visible in the scan.
- The PRAGMA AUTONOMOUS_TRANSACTION pattern used throughout (PKG_AUDIT, PKG_COMMON, PKG_NOTIFICATION) means these log/queue operations succeed even when the calling transaction rolls back. This is intentional design for audit reliability — but it also means failed business transactions still generate audit records and notification queue entries.

---

### Files Not Yet Scanned (Known Gaps)

| Gap | Impact |
|---|---|
| PKG_DEPARTMENT.pks/.pkb | Department management logic unknown |
| 12 table DDL files | Incomplete data model |
| 9 view definitions | Incomplete reporting layer |
| 8 Oracle Reports (.rdf/.rep) | Reporting logic and data exposure unknown |
| 200+ remaining trigger files | Validation and audit coverage unknown |
| WebLogic configuration | TLS, connection pooling, session config unknown |
| sqlnet.ora / tnsnames.ora | Network encryption and connectivity unknown |
| RMAN / Data Guard config | DR posture unknown |
| Any .env or property files | No environment-specific config found |
| DBMS_SCHEDULER job DDL | Scheduler configuration unknown |

---

**Agent 1 scan complete. All 6 outputs, Validation Queue, and Handoff Note delivered.**

*Scan performed by: TA Agent 1 — Technology Stack Scout v2.0*
*Codebase: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main*
*Scan date: 2026-08-04*
