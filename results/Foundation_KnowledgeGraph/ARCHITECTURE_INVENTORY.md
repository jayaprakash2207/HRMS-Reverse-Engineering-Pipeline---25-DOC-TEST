# Architecture Inventory — Acme Corporation HRMS (Oracle 19c)

**Document Version:** 1.0  
**System:** Acme Corporation Human Resources Management System  
**Platform:** Oracle 19c / Oracle Forms 12c  
**Classification:** Internal — Solution Architecture  
**Prepared By:** Solution Architecture Track  
**Source:** Multi-track analysis (BA, DA, TA, AA) — 140 business rules, 46+ data quality findings, 81+ technical debt items, 33 quality review findings

---

## Table of Contents

1. Component Inventory
2. Technology Inventory
3. Integration Inventory
4. Defect Inventory
5. Security Finding Inventory
6. Technical Debt Inventory
7. Architecture Patterns in Use
8. Component Dependency Map

---

## 1. Component Inventory

Full inventory of all PL/SQL packages, Oracle Forms modules, views, triggers, and utility libraries identified in the codebase.

Looking at the source content to find anything that should be added beyond what's already in the [GAP-FILLED] annotation, I can see one critical detail missing: the `calculate_payroll` cursor explicitly filters to `EMPLOYMENT_STATUS = 'ACTIVE'`, which means a terminated employee is excluded from the regular payroll run entirely — making `calculate_final_pay` the only possible processing path, and its absence a total dead end with no fallback.

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. [GAP-FILLED] The `calculate_payroll` outer procedure (source-confirmed) drives all pay processing through a cursor that filters strictly to `EMPLOYMENT_STATUS = 'ACTIVE'` employees — meaning a terminated employee is excluded from every regular payroll run the moment their status changes; `calculate_final_pay` is therefore the sole intended processing path for termination pay, and its complete absence creates a total dead end with no fallback: termination-triggered pay cannot be computed via the regular run nor via any special run type, leaving final-pay, vacation payout, and severance entirely unprocessable through any existing code path. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |
| COMP-008 | PKG_NOTIFICATION | PL/SQL Package | PKG_NOTIFICATION.pks / .pkb | Production — incomplete | Email/SMS notification dispatch; SMS channel not implemented |
| COMP-009 | PKG_REPORTING | PL/SQL Package | PKG_REPORTING.pks / .pkb | Production — stub partial | 7 live OLTP-query report procedures; `refresh_reporting_tables` is a no-op stub |
| COMP-010 | PKG_COMPENSATION | PL/SQL Package | PKG_COMPENSATION.pks / .pkb | Production | Salary management, grade bands |
| COMP-011 | HRMS_VALIDATION_LIB | Oracle Forms PL/SQL Library | HRMS_VALIDATION_LIB.pll.sql | Production — defective | Client-side validation library; salary range validation is soft warning only |

### 1.2 Oracle Forms Modules

| Comp ID | Component Name | Type | File | Status | Notes |
|---------|---------------|------|------|--------|-------|
| FORM-001 | HRMS_EMPLOYEE | Oracle Form | forms/xml-exports/HRMS_EMPLOYEE.xml | Production | Employee maintenance; LOV_MANAGERS has no grade constraint |
| FORM-002 | HRMS_PAYROLL | Oracle Form | forms/xml-exports/HRMS_PAYROLL.xml | Production | Payroll run management |
| FORM-003 | HRMS_LOGIN | Oracle Form | forms/xml-exports/HRMS_LOGIN.xml | Production — defective | Single WHEN OTHERS handler masks auth vs. lookup failures |
| FORM-004 | HRMS_LEAVE | Oracle Form | forms/xml-exports/ | Production | Leave request and approval |
| FORM-005 | HRMS_REPORTS | Oracle Form | forms/xml-exports/ | Production | Report launcher; calls PKG_REPORTING procedures |

### 1.3 Database Schema Objects — Core Tables (Confirmed DDL)

| Comp ID | Component Name | Type | Schema | Status | Notes |
|---------|---------------|------|--------|--------|-------|
| TBL-001 | EMPLOYEES | Table | HRMS | Production | Central aggregate root; 30+ columns; multiple encrypted PII fields |
| TBL-002 | DEPARTMENTS | Table | HRMS | Production | Org hierarchy via self-FK PARENT_DEPARTMENT_ID |
| TBL-003 | JOB_POSITIONS | Table | HRMS | Production | Job catalogue with grade range enforcement |
| TBL-004 | SALARY_RECORDS | Table | HRMS | Production | Point-in-time salary history; current = MAX(EFFECTIVE_DATE) |
| TBL-005 | PAYROLL_RUNS | Table | HRMS | Production | Payroll cycle header; missing GL_FEED_SENT_DATE/GL_FEED_SENT_FLAG |
| TBL-006 | PAYROLL_DETAILS | Table | HRMS | Production | Per-employee payroll line items; magic numbers ELEMENT_ID 100–103 |
| TBL-007 | DEDUCTION_RECORDS | Table | HRMS | Production | Employee deductions per pay run |
| TBL-008 | LEAVE_BALANCES | Table | HRMS | Production | Leave balance per employee per type |
| TBL-009 | LEAVE_REQUESTS | Table | HRMS | Production | Leave request workflow |
| TBL-010 | LEAVE_TYPES | Table | HRMS | Production — misconfigured | FMLA seed data: REQUIRES_DOCUMENT='N' (should be 'Y') |
| TBL-011 | PERFORMANCE_REVIEWS | Table | HRMS | Production — incomplete | CALIBRATED_RATING / CALIBRATION_NOTES columns never written by any procedure |
| TBL-012 | REVIEW_CYCLES | Table | HRMS | Production | Performance cycle definitions |
| TBL-013 | PERFORMANCE_GOALS | Table | HRMS | Production | Goal definitions per review cycle |
| TBL-014 | GOAL_REVIEWS | Table | HRMS | Production | Goal achievement records |
| TBL-015 | BENEFIT_PLANS | Table | HRMS | Production | Benefits plan catalogue |
| TBL-016 | BENEFIT_ENROLLMENTS | Table | HRMS | Production | Employee-to-plan enrollment |
| TBL-017 | EMPLOYEE_DEPENDENTS | Table | HRMS | Production — gap | `BENEFITS_ENROLLED` flag never read; termination does not touch this table |
| TBL-018 | EMPLOYEE_BANK_ACCOUNTS | Table | HRMS | Production — critical gap | Table fully designed; never referenced in any PL/SQL procedure |
| TBL-019 | NOTIFICATION_QUEUE | Table | HRMS | Production | Async notification dispatch queue |
| TBL-020 | NOTIFICATION_TEMPLATES | Table | HRMS | Production | Notification template registry |
| TBL-021 | USER_SESSIONS | Table | HRMS | Production — defective | Orphan sessions never swept; no background cleanup job |
| TBL-022 | USER_CREDENTIALS | Table | HRMS | Production — critical defect | PASSWORD_HASH uses MD5; authenticate() never queries this table |
| TBL-023 | AUDIT_LOG | Table | HRMS | Production | Mixed ERROR_LOG, INFO_LOG, and DML audit; no separate retention per type |
| TBL-024 | SYSTEM_PARAMETERS | Table | HRMS | Production — partially ignored | Session timeout parameter value ignored by PKG_SECURITY; hard-coded 30 min used |
| TBL-025 | LOOKUP_VALUES | Table | HRMS | Production | Shared lookup/reference values |
| TBL-026 | JOB_TITLES | Table | HRMS | Production | Job title definitions with GRADE_ID linkage |
| TBL-027 | JOB_GRADES | Table | HRMS | Production | Grade band definitions with MIN/MAX salary |
| TBL-028 | TERMINATION_CODES | Table | HRMS | Production | FK reference for EMPLOYEES.TERMINATION_REASON |
| TBL-029 | PAYROLL_ELEMENTS | Table | HRMS | Production | Pay element definitions |
| TBL-030 | LOCATIONS | Table | HRMS | Production | Physical location records |

### 1.4 Inferred / Stub Tables

| Comp ID | Component Name | Type | Status | Notes |
|---------|---------------|------|--------|-------|
| TBL-INF-001 | RPT_HEADCOUNT | Inferred Reporting Table | Never populated | Implied by PKG_REPORTING spec; refresh_reporting_tables is no-op stub |
| TBL-INF-002 | RPT_COMPENSATION | Inferred Reporting Table | Never populated | Same stub issue; MEDIAN() aggregate has no PostgreSQL equivalent |
| TBL-INF-003 | RPT_TURNOVER | Inferred Reporting Table | Never populated | Non-standard denominator in TURNOVER_PCT formula |
| TBL-INF-004 | RPT_NEW_HIRES | Inferred Reporting Table | Never populated | Co-locates salary + hire date; PII exposure risk |
| TBL-INF-005 | RPT_LEAVE_UTILIZATION | Inferred Reporting Table | Never populated | CALENDAR_YEAR missing from cursor projection |
| TBL-INF-006 | RPT_PAYROLL_SUMMARY | Inferred Reporting Table | Never populated | Magic number ELEMENT_IDs 100/101/102/103 |
| TBL-INF-007 | RPT_EEO_COMPLIANCE | Inferred Reporting Table | Never populated | EEO_CATEGORY grouping; unguarded at table level |
| TBL-INF-008 | TIME_ATTENDANCE_RECORDS | Inferred Import Target | DDL not recovered | Implied by PKG_INTEGRATION.import_time_attendance; no link to PAYROLL_DETAILS |
| TBL-INF-009 | EMPLOYEE_PAY_ELEMENTS | Inferred | Unconfirmed | Referenced in domain model; DDL not recovered |

### 1.5 Views (Confirmed)

| Comp ID | Component Name | Type | Status |
|---------|---------------|------|--------|
| VIEW-001 | VW_ACTIVE_EMPLOYEES | View | Production |
| VIEW-002 | VW_EMPLOYEE_SUMMARY | View | Production |
| VIEW-003 | VW_DEPARTMENT_HIERARCHY | View | Production — performance risk (CONNECT BY on large dataset) |
| VIEW-004 | VW_PAYROLL_SUMMARY | View | Production |
| VIEW-005 | VW_LEAVE_SUMMARY | View | Production |
| VIEW-006 | VW_PERFORMANCE_SUMMARY | View | Production |

---

## 2. Technology Inventory

### 2.1 Core Platform

| Tech ID | Technology | Version | Category | Licensing | Notes |
|---------|-----------|---------|----------|-----------|-------|
| TECH-001 | Oracle Database | 19c | RDBMS | Oracle EE | Primary data store; all business logic in PL/SQL |
| TECH-002 | Oracle Forms | 12c | UI Framework | Oracle Forms & Reports | Client-side forms; requires Forms Builder for compilation; no CI step |
| TECH-003 | Oracle PL/SQL | 19c dialect | Language | Included with DB | All application logic layer |
| TECH-004 | Oracle Reports | Implied (.rdf) | Reporting Tool | Oracle | Referenced in PKG_REPORTING spec as a caller; no .rdf files in repo |
| TECH-005 | SQL*Plus | Current | DBA/Deploy Tool | Included with DB | All schema DDL applied via SQL*Plus scripts; fully manual |
| TECH-006 | UTL_FILE | Oracle built-in | File I/O | Included with DB | Used for ADP benefits flat file, GL feed, NACHA, time attendance import |
| TECH-007 | UTL_MAIL | Oracle built-in | Email | Included with DB | Email dispatch for notifications |
| TECH-008 | DBMS_CRYPTO | Oracle built-in | Cryptography | Included with DB | AES-256 encryption for SSN, bank accounts; MD5 for passwords (weak) |
| TECH-009 | DBMS_SCHEDULER | Oracle built-in | Job Scheduler | Included with DB | Referenced for payroll queue processing; no confirmed schedule definitions in repo |
| TECH-010 | DBMS_OUTPUT | Oracle built-in | Debug Logging | Included with DB | Used as debug fallback; invisible in production |
| TECH-011 | Oracle CONNECT BY | SQL clause | Hierarchical Query | Included with DB | Department hierarchy; performance degrades >500 employees |

### 2.2 Security & Cryptography

| Tech ID | Technology | Usage | Risk Level |
|---------|-----------|-------|-----------|
| TECH-012 | AES-256-CBC-PKCS5 | SSN, bank account numbers encryption | Low — algorithm is sound; key management is CRITICAL risk (hard-coded key) |
| TECH-013 | MD5 (DBMS_CRYPTO.HASH_MD5) | Password hashing in USER_CREDENTIALS | Critical — MD5 is cryptographically broken; rainbow table attack trivial |
| TECH-014 | Hard-coded AES Key `HR$ystem_3ncrypt10n_K3y_2024!!` | Embedded in PKG_SECURITY source | Critical — key in version control; all encrypted PII at risk |

### 2.3 External Libraries and Tools

| Tech ID | Technology | Category | Present In Repo | Notes |
|---------|-----------|----------|----------------|-------|
| TECH-015 | Oracle Forms Builder 12c | Build Tool | No | Required for .fmb → .fmx compilation; not scripted |
| TECH-016 | frmcmp.sh | Build Script | No | Not present; must be documented and added |
| TECH-017 | NACHA ACH Specification | Protocol | Referenced | Implementation is stub only; no real ACH file generation |
| TECH-018 | ADP Benefits Feed Format | Protocol | Implemented | 203-character fixed-width; no version header or trailer count |

### 2.4 Absent Technology (Critical Gaps)

| Tech ID | Technology | Gap Severity | Impact |
|---------|-----------|-------------|--------|
| TECH-GAP-001 | CI/CD Pipeline (any) | Critical | Zero automated builds, tests, or deploys |
| TECH-GAP-002 | Unit Test Framework (utPLSQL, etc.) | Critical | No tests exist anywhere in repository |
| TECH-GAP-003 | SAST / Static Analysis | Critical | No SonarQube, Semgrep, CodeQL, or equivalent |
| TECH-GAP-004 | Secret Scanning (gitleaks, TruffleHog) | Critical | Hard-coded AES key and FTP credentials would have been detected |
| TECH-GAP-005 | Structured Logging / APM | High | DBMS_OUTPUT is invisible in production; no correlation IDs; no severity tiers |
| TECH-GAP-006 | Dependency Scanning | High | No Snyk or OWASP dependency-check |
| TECH-GAP-007 | Container Platform | N/A | Not applicable; no containers used |
| TECH-GAP-008 | bcrypt / Argon2 / PBKDF2 | Critical | MD5 used for passwords; must be replaced |

---

## 3. Integration Inventory

### 3.1 External System Integrations

| Int ID | Integration Name | Direction | Protocol | Format | Implemented? | Status | Owner Package |
|--------|----------------|-----------|----------|--------|-------------|--------|--------------|
| INT-001 | ADP Benefits Feed | Outbound | File Transfer (FTP implied) | Fixed-width 203-char flat file | Yes — partial | Production — defective | PKG_INTEGRATION.export_benefits_feed |
| INT-002 | Oracle Financials GL Journal Feed | Outbound | File Transfer | Pipe-delimited flat file | Yes — partial | Production — defective | PKG_INTEGRATION.generate_gl_journal |
| INT-003 | NACHA / ACH Direct Deposit | Outbound | NACHA file | NACHA ACH format | No — stub only | Not implemented | PKG_INTEGRATION (stub) |
| INT-004 | SMTP Email Notifications | Outbound | UTL_MAIL / SMTP | MIME email | Yes | Production | PKG_NOTIFICATION |
| INT-005 | SMS Notifications | Outbound | SMS gateway (unspecified) | SMS text | No — stub | Not implemented | PKG_NOTIFICATION (stub) |
| INT-006 | Time & Attendance Import | Inbound | File Import (UTL_FILE) | CSV | No — stub | Not implemented | PKG_INTEGRATION.import_time_attendance |
| INT-007 | LDAP / Active Directory Org Sync | Bidirectional | LDAP (implied) | N/A | No — stub | Not implemented | PKG_INTEGRATION.sync_org_structure |
| INT-008 | Oracle Reports (.rdf) | Internal | Oracle Reports runtime | .rdf | Uncertain | Unconfirmed in repo | PKG_REPORTING (caller) |
| INT-009 | Self-Service Portal DB Connection | Inbound | JDBC/Oracle Net | SQL / PL/SQL calls | Yes (implied) | Undeclared credentials | Calls PKG_LEAVE |

### 3.2 Integration Detail: ADP Benefits Feed (INT-001)

- **File path:** `BENEFITS_FEED_OUT` Oracle directory / `BENEFITS_YYYYMMDD.txt`
- **Record width:** 203 characters fixed-width
- **Critical defect:** No file version header; no trailer with record count; no checksum; RPAD silently truncates overlong data
- **Data gap:** `BENEFITS_ENROLLED` flag on EMPLOYEE_DEPENDENTS is never read — all active dependents exported regardless of enrollment status
- **Dependent SSN:** `SSN_ENCRYPTED` on dependents is never decrypted or included — gap if ADP requires it

### 3.3 Integration Detail: GL Journal Feed (INT-002)

- **Format:** Pipe-delimited; fields include COST_CENTER and GL_ACCOUNT_CODE
- **Critical defect:** Oracle Financials GL Journal Import requires Journal Source and Journal Category — not visible in source; missing values cause Financials to reject or misroute the batch
- **Status tracking defect:** No `GL_FEED_SENT_DATE` or `GL_FEED_SENT_FLAG` on PAYROLL_RUNS; no acknowledgement mechanism; no reconciliation query exists

### 3.4 Integration Detail: NACHA / ACH (INT-003)

- **Status:** Complete non-implementation; EMPLOYEE_BANK_ACCOUNTS table is fully designed but never referenced in any PL/SQL procedure
- **Prenote gap:** `PRENOTE_SENT` and `PRENOTE_DATE` columns exist on EMPLOYEE_BANK_ACCOUNTS; no procedure populates them — Nacha prenote compliance requirement unmet
- **Impact:** Direct deposit is entirely non-functional; every payroll disbursement requires manual bank transfer outside the system

### 3.5 Integration Detail: Time & Attendance Import (INT-006)

- **Stub behaviour:** Procedure reads CSV via UTL_FILE, logs `'Time attendance import completed'`, performs zero DML
- **Destination table:** `TIME_ATTENDANCE_RECORDS` — DDL not recovered; table existence unconfirmed
- **Missing link:** No connection between imported attendance data and PAYROLL_DETAILS or PAYROLL_RUNS
- **Audit trail defect:** `log_info` creates false success signal; monitoring cannot distinguish real import from stub run

### 3.6 Integration Detail: Org Structure Sync (INT-007)

- **Stub behaviour:** Calls `PKG_COMMON.log_info('Org structure sync completed')` and returns — entire body
- **False positive risk:** Every scheduled run logs success with no data movement; monitoring tools cannot detect failure
- **Missing:** LDAP host, port, bind DN, credentials — not defined anywhere in codebase

---

## 4. Defect Inventory

All confirmed bugs, data defects, and functional gaps identified across all analysis tracks.

### 4.1 Critical Defects

| Defect ID | Title | Severity | Location | Business Impact |
|-----------|-------|----------|----------|----------------|
| DEF-001 | Authentication stub — password never verified | Critical | PKG_SECURITY.authenticate() | Any valid username authenticates regardless of password entered; complete authentication bypass |
| DEF-002 | Hard-coded AES-256 encryption key in source | Critical | PKG_SECURITY.pkb | Key `HR$ystem_3ncrypt10n_K3y_2024!!` in version control; all SSN, bank account PII at risk |
| DEF-003 | Direct deposit non-functional | Critical | PKG_PAYROLL / EMPLOYEE_BANK_ACCOUNTS | EMPLOYEE_BANK_ACCOUNTS never read during payroll; no ACH disbursement; all net pay requires manual processing |
| DEF-004 | `calculate_final_pay` procedure does not exist | Critical | PKG_PAYROLL | Termination procedure calls non-existent procedure; every termination requires fully manual payroll outside the system |
| DEF-005 | HEAD_OF_HOUSEHOLD federal tax returns $0 | Critical | PKG_PAYROLL.calculate_employee_pay | Employees with HOH filing status have zero federal tax withheld; IRS compliance breach |
| DEF-006 | MD5 password hashing | Critical | PKG_SECURITY / USER_CREDENTIALS | MD5 is cryptographically broken; rainbow table attack trivial; all stored credentials at risk |
| DEF-007 | COBRA not implemented | Critical | PKG_EMPLOYEE.terminate_employee | Federal law requires qualified beneficiary notification within 14 days of qualifying event; every termination creates unreported event |
| DEF-008 | FTP credentials stored in plaintext | Critical | PKG_INTEGRATION.pkb | Cleartext FTP credentials embedded in source; credential compromise via version control |
| DEF-009 | `change_password` never verifies old password | Critical | PKG_SECURITY.change_password | Any authenticated session can replace any employee's credential without knowing current password |

### 4.2 High Severity Defects

| Defect ID | Title | Severity | Location | Business Impact |
|-----------|-------|----------|----------|----------------|
| DEF-010 | PAYROLL_DETAILS STATUS='PAID' orphaned — no disbursement | High | PKG_PAYROLL / EMPLOYEE_BANK_ACCOUNTS | Payroll records marked PAID but no actual disbursement occurs; financial reconciliation impossible |
| DEF-011 | Accrual retry block uses assignment instead of increment | High | PKG_LEAVE.run_monthly_accrual | Silent data corruption if retry fires on existing leave balance row |
| DEF-012 | Termination does not touch EMPLOYEE_DEPENDENTS | High | PKG_EMPLOYEE.terminate_employee | Terminated employees' dependents remain active in ADP benefits feed; continued benefit charges post-termination |
| DEF-013 | `BENEFITS_ENROLLED` flag never read in benefits feed | High | PKG_INTEGRATION.export_benefits_feed | All active dependents exported to ADP regardless of enrollment status; un-enrolled dependents may receive benefits |
| DEF-014 | Dependent SSN has no decrypt procedure | High | PKG_SECURITY / EMPLOYEE_DEPENDENTS | SSN_ENCRYPTED on dependents encrypted but cannot be decrypted; operational gap for tax/benefits reporting |
| DEF-015 | Duplicate email: TOO_MANY_ROWS silently uses MIN(EMP_ID) | High | PKG_SECURITY.authenticate | Two employees with same email: lower EMP_ID always authenticates; other employee cannot log in |
| DEF-016 | `e_account_locked` and `e_session_expired` never raised | High | PKG_SECURITY.pkb | Exception handlers in Oracle Forms callers for these named exceptions will never fire |
| DEF-017 | Orphan sessions never swept | High | USER_SESSIONS / PKG_SECURITY | Sessions remain ACTIVE indefinitely if browser closed without logout; no background cleanup |
| DEF-018 | In-flight session survives termination for 30 minutes | High | PKG_SECURITY.is_session_valid | Terminated employee with active session retains full system access until session timeout |
| DEF-019 | RPT_* tables never populated | High | PKG_REPORTING.refresh_reporting_tables | Stub logs false success; nightly refresh is no-op; any direct query of RPT_* tables returns stale or empty data |
| DEF-020 | import_time_attendance silent no-op | High | PKG_INTEGRATION.import_time_attendance | Logs false success while performing zero data import; time data never enters payroll |
| DEF-021 | `sync_org_structure` unconditional false-positive log | High | PKG_INTEGRATION.sync_org_structure | Logs success on every execution whether or not any sync occurred; monitoring cannot detect failure |
| DEF-022 | CALIBRATED_RATING and CALIBRATION_NOTES dead columns | High | PKG_PERFORMANCE / PERFORMANCE_REVIEWS | No procedure writes to these columns; calibration workflow entirely absent; rating distribution report uses pre-calibration OVERALL_RATING |
| DEF-023 | GL feed has no Journal Source/Category validation | High | PKG_INTEGRATION.generate_gl_journal | Oracle Financials may reject or misroute entire batch if source/category values incorrect |
| DEF-024 | No mechanism to detect missed GL feed | High | PKG_INTEGRATION / PAYROLL_RUNS | No GL_FEED_SENT_DATE; no acknowledgement; no reconciliation; missed feeds go undetected |
| DEF-025 | Routing numbers stored plaintext | High | EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER | Combined with encrypted account number constitutes full ACH credentials; routing number unprotected |
| DEF-026 | ACH prenote not implemented | High | EMPLOYEE_BANK_ACCOUNTS | PRENOTE_SENT/PRENOTE_DATE columns exist but never populated; Nacha compliance gap |
| DEF-027 | Salary grade validation is soft warning only | High | PKG_EMPLOYEE / HRMS_VALIDATION_LIB | `validate_salary_range` issues MESSAGE but not FORM_TRIGGER_FAILURE; employees can be created with salaries outside grade band |

### 4.3 Medium Severity Defects

| Defect ID | Title | Severity | Location | Business Impact |
|-----------|-------|----------|----------|----------------|
| DEF-028 | Session timeout hard-coded at 30 min; SYSTEM_PARAMETERS ignored | Medium | PKG_SECURITY | Configuration value in database has no effect; ops cannot change timeout without code change |
| DEF-029 | DEPARTMENT hierarchy CONNECT BY degrades >500 employees | Medium | VW_DEPARTMENT_HIERARCHY / PKG_EMPLOYEE | Recursive query without performance cap; report timeout risk at scale |
| DEF-030 | FMLA configured with REQUIRES_DOCUMENT='N' | Medium | 01_reference_data.sql | FMLA requests accepted without supporting documentation; compliance and audit risk |
| DEF-031 | LOV_MANAGERS includes all active employees (no grade filter) | Medium | HRMS_EMPLOYEE.xml | Intern (Grade 1) can be selected as manager for VP (Grade 9) |
| DEF-032 | CALENDAR_YEAR missing from leave_utilization_report cursor | Medium | PKG_REPORTING | RPT_LEAVE_UTILIZATION snapshot cannot support multi-year analysis |
| DEF-033 | No distribution total validation on bank accounts | Medium | EMPLOYEE_BANK_ACCOUNTS | Accounts summing to 80% or 120% of net pay are accepted without error |
| DEF-034 | HRMS_LOGIN single WHEN OTHERS handler | Medium | HRMS_LOGIN.xml | Auth failure and EMP_ID lookup failure indistinguishable in logs; operational diagnosis impossible |

---

## 5. Security Finding Inventory

| Sec ID | Finding | OWASP Category | Severity | Location | Recommendation |
|--------|---------|---------------|----------|----------|----------------|
| SEC-001 | Authentication stub — password never verified | A07 Identification & Auth Failures | Critical | PKG_SECURITY.authenticate | Implement actual credential verification against USER_CREDENTIALS |
| SEC-002 | Hard-coded AES encryption key in source | A02 Cryptographic Failures | Critical | PKG_SECURITY.pkb: `HR$ystem_3ncrypt10n_K3y_2024!!` | Move to Oracle Wallet or HSM; rotate all encrypted PII after key change |
| SEC-003 | FTP credentials in plaintext source | A02 Cryptographic Failures | Critical | PKG_INTEGRATION.pkb | Move credentials to SYSTEM_PARAMETERS with encrypted storage; remove from source |
| SEC-004 | MD5 password hashing | A02 Cryptographic Failures | Critical | PKG_SECURITY / USER_CREDENTIALS | Replace with bcrypt (Argon2id preferred); force password reset on migration |
| SEC-005 | `change_password` skips old-password verification | A07 Identification & Auth Failures | Critical | PKG_SECURITY.change_password | Verify p_old_password against stored hash before allowing replacement |
| SEC-006 | In-flight session not revoked on termination | A07 Identification & Auth Failures | High | PKG_EMPLOYEE.terminate_employee / PKG_SECURITY | Call PKG_SECURITY.revoke_access (create it); invalidate USER_SESSIONS rows on termination |
| SEC-007 | Orphan sessions accumulate indefinitely | A07 Identification & Auth Failures | High | USER_SESSIONS | Add DBMS_SCHEDULER sweep job to expire sessions older than 30 minutes |
| SEC-008 | Username enumeration timing attack | A07 Identification & Auth Failures | High | PKG_SECURITY.authenticate | Use constant-time comparison; return identical error for unknown user and bad password |
| SEC-009 | PKG_SECURITY.revoke_access referenced but does not exist | A07 Identification & Auth Failures | High | PKG_EMPLOYEE.terminate_employee | Implement the procedure; create spec and body |
| SEC-010 | Routing numbers stored plaintext alongside encrypted account numbers | A02 Cryptographic Failures | High | EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER | Encrypt ROUTING_NUMBER with same key as ACCOUNT_NUMBER_ENC |
| SEC-011 | Self-service portal DB credentials undeclared | A01 Broken Access Control | High | PKG_LEAVE (called by portal) | Create dedicated HRMS_PORTAL_APP schema user with EXECUTE-only grants; revoke direct table grants |
| SEC-012 | RPT_NEW_HIRES co-locates name + salary + hire date; no table-level access control | A01 Broken Access Control | High | RPT_NEW_HIRES (inferred) | Add Oracle VPD or explicit GRANT controls; salary is financial PII |
| SEC-013 | Grade-based RBAC reads EMPLOYEES.GRADE directly (no contract) | A01 Broken Access Control | Medium | PKG_SECURITY.has_permission | Define explicit RBAC contract; Grade ≥8 full, 5–7 view-all, <5 own-only — document and enforce |
| SEC-014 | PKG_SECURITY manages session timeout in code, not configuration | A05 Security Misconfiguration | Medium | PKG_SECURITY.is_session_valid | Honour SYSTEM_PARAMETERS.SESSION_TIMEOUT_MINUTES |
| SEC-015 | EMPLOYEES.BANK_ACCOUNT_NUMBER: no decrypt procedure implemented | A02 Cryptographic Failures | High | EMPLOYEES / PKG_SECURITY | Implement decrypt path; or confirm EMPLOYEE_BANK_ACCOUNTS is the canonical location and remove column from EMPLOYEES |
| SEC-016 | Dependent SSN encrypted with no corresponding decrypt procedure | A02 Cryptographic Failures | High | EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED | Implement decrypt path mirroring PKG_SECURITY pattern for employees |
| SEC-017 | AUDIT_LOG mixes ERROR, INFO, and DML audit; single purge policy | A09 Security Logging Failures | Medium | PKG_COMMON / AUDIT_LOG | Separate into distinct tables; implement per-type retention policies |
| SEC-018 | No SAST or secret scanning in CI (no CI exists) | A05 Security Misconfiguration | Critical | Repository-wide | Implement CI with gitleaks/TruffleHog and SonarQube/Semgrep as first priority |
| SEC-019 | Path traversal risk in SUPPORTING_DOC_PATH | A03 Injection | Medium | PKG_LEAVE (referenced TD-47) | Validate SUPPORTING_DOC_PATH against allowed directory whitelist; reject path traversal sequences |

---

## 6. Technical Debt Inventory

Categorized by severity. Source: TA_Deep_Analyst TD-01 through TD-81 (subset of high/critical shown in full; medium and low summarized).

### 6.1 Critical Technical Debt (Must Fix Before Migration)

| TD ID | Title | Category | Evidence | Recommended Action |
|-------|-------|----------|----------|--------------------|
| TD-01 | Hard-coded AES encryption key | Security | PKG_SECURITY.pkb literal string | Move to Oracle Wallet; rotate all encrypted data |
| TD-10 | FTP credentials in plaintext | Security | PKG_INTEGRATION.pkb | Move to SYSTEM_PARAMETERS encrypted column; remove from source |
| TD-28 | Authentication stub — password not checked | Security | PKG_SECURITY.authenticate body | Implement real credential verification |
| TD-29 | MD5 password hashing | Security | DBMS_CRYPTO.HASH_MD5 | Replace with Argon2id; force reset |
| TD-42 | No CI/CD pipeline of any kind | Operations | Repository-wide absence | Implement pipeline with build, test, SAST, secret scan, deploy |
| TD-43 | No automated tests exist | Operations | Repository-wide absence | Implement utPLSQL; minimum 80% coverage target |
| TD-44 | No SAST tooling | Security | Repository-wide absence | SonarQube or Semgrep; add to CI gate |
| TD-45 | Direct deposit non-functional | Business Logic | EMPLOYEE_BANK_ACCOUNTS never referenced | Implement ACH disbursement procedure |

### 6.2 High Technical Debt

| TD ID | Title | Category | Evidence | Recommended Action |
|-------|-------|----------|----------|--------------------|
| TD-02 | PKG_PAYROLL.calculate_employee_pay HEAD_OF_HOUSEHOLD branch returns $0 tax | Business Logic | PKG_PAYROLL.pkb | Fix HOH tax bracket logic; add regression test |
| TD-03 | COBRA not implemented (federal compliance gap) | Business Logic | PKG_EMPLOYEE.terminate_employee TODO | Implement COBRA notification workflow |
| TD-04 | `calculate_final_pay` does not exist | Business Logic | Called in TODO comment only | Create procedure: prorated wage, PTO payout, off-cycle run |
| TD-05 | Accrual retry: assignment instead of increment | Business Logic | PKG_LEAVE.run_monthly_accrual | Fix `SET ACCRUED = v_accrued` → `SET ACCRUED = ACCRUED + v_accrued` |
| TD-06 | Calibration workflow absent (CALIBRATED_RATING dead column) | Business Logic | PKG_PERFORMANCE — no calibration writes | Design and implement calibration phase; fix get_rating_distribution to use CALIBRATED_RATING |
| TD-07 | RPT_* refresh is no-op stub | Architecture | PKG_REPORTING.refresh_reporting_tables | Implement truncate-repopulate DML; or remove RPT_* layer and use on-demand reports only |
| TD-08 | import_time_attendance silent no-op | Architecture | PKG_INTEGRATION stub | Implement actual CSV parsing and PAYROLL_DETAILS linkage |
| TD-09 | sync_org_structure false-positive success log | Architecture | PKG_INTEGRATION stub | Implement or remove; never log success for an unimplemented procedure |
| TD-30 | No GL_FEED_SENT_DATE on PAYROLL_RUNS | Architecture | Schema gap | Add column; update on successful GL feed file close |
| TD-46 | Routing numbers plaintext | Security | EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER | Encrypt alongside account number |
| TD-47 | Path traversal in SUPPORTING_DOC_PATH | Security | PKG_LEAVE | Add directory whitelist validation |
| TD-60 | DEPARTMENT hierarchy CONNECT BY no depth limit | Performance | VW_DEPARTMENT_HIERARCHY | Add LEVEL ≤ N guard; consider materialized path |
| TD-64 | Orphan session rows accumulate | Operations | USER_SESSIONS / PKG_SECURITY | Add DBMS_SCHEDULER sweep every 5 minutes |
| TD-65 | Termination does not inactivate dependents or bank accounts | Business Logic | PKG_EMPLOYEE.terminate_employee | Add inactivation steps; coordinate COBRA hold policy |
| TD-81 | Self-service portal DB auth model undeclared | Security | PKG_LEAVE header | Create HRMS_PORTAL_APP user; implement EXECUTE-only grants |

### 6.3 Medium Technical Debt

| TD ID | Title | Category |
|-------|-------|----------|
| TD-11 | SQ_EMPLOYEE_ID sequence NOCACHE — serialization bottleneck at scale | Performance |
| TD-15 | AUDIT_LOG single table for all log types | Architecture |
| TD-20 | SYSTEM_PARAMETERS SESSION_TIMEOUT value ignored | Configuration |
| TD-32 | Oracle MEDIAN() aggregate has no direct PostgreSQL equivalent (migration risk) | Migration Risk |
| TD-48 | FMLA configured REQUIRES_DOCUMENT='N' | Configuration |
| TD-50 | ADP benefits feed no version header / trailer / checksum | Architecture |
| TD-68 | Payroll magic numbers ELEMENT_ID 100–103 undocumented | Architecture |
| TD-72 | LOV_MANAGERS no grade constraint | Configuration |
| TD-74 | Salary grade validation soft warning only | Business Logic |
| TD-75 | Oracle Forms session not cleaned on window close | Operational |
| TD-76 | Oracle Forms compilation not scripted | Operational |
| TD-79 | GL feed Journal Source/Category not documented | Architecture |
| TD-80 | No mechanism to detect missed GL feed | Operational |

### 6.4 Low Technical Debt

| TD ID | Title | Category |
|-------|-------|----------|
| TD-37 | AUDIT_LOG mixed purge policy | Architecture |
| TD-40 | EEO gender code no CHECK constraint | Configuration |
| TD-52 | Stale "cached" comment in HRMS_VALIDATION_LIB | Documentation |
| TD-53 | HRMS_LOGIN generic WHEN OTHERS handler | Operational |
| TD-57 | GL account coding scheme undocumented | Configuration |

---

## 7. Architecture Patterns in Use

Assessment of each pattern: whether it is fit for the new system, should be replaced, or is acceptable with modifications.

### 7.1 Pattern Inventory

| Pat ID | Pattern Name | Description | Currently Used In | Verdict | Rationale |
|--------|-------------|-------------|------------------|---------|-----------|
| PAT-001 | Monolithic PL/SQL Package Architecture | All business logic in Oracle-hosted PL/SQL packages; no application server tier | PKG_EMPLOYEE, PKG_PAYROLL, PKG_LEAVE, PKG_PERFORMANCE, PKG_SECURITY, PKG_INTEGRATION | **Replace** | Database as application server; untestable without Oracle; no horizontal scaling; vendor lock-in |
| PAT-002 | Oracle Forms Client-Server | Thick Oracle Forms client connects directly to Oracle DB; no HTTP tier | HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LOGIN, HRMS_LEAVE, HRMS_REPORTS | **Replace** | Oracle Forms 12c is end-of-life roadmap; no browser support; manual compilation; no CI; single-vendor |
| PAT-003 | Soft Delete Pattern | ACTIVE_FLAG CHAR(1) Y/N on all major tables | EMPLOYEES, DEPARTMENTS, EMPLOYEE_DEPENDENTS, EMPLOYEE_BANK_ACCOUNTS, LEAVE_TYPES | **Keep (adapt)** | Standard practice; carry forward as `deleted_at` timestamp in new system to support audit trail |
| PAT-004 | Shared Kernel (Bounded Contexts) | EMPLOYEES table used by all bounded contexts without ACL | All packages read EMPLOYEES directly | **Replace** | Creates tight coupling; changes to EMPLOYEES break all packages; replace with domain events and read models |
| PAT-005 | Fixed-Width Flat File Integration | Vendor file exchange via UTL_FILE fixed-width or delimited | ADP benefits feed (203-char), GL journal (pipe-delimited) | **Replace** | Brittle; no schema evolution; field truncation silent; replace with vendor API or SFTP with structured format (JSON/XML) where possible |
| PAT-006 | Grade-Based RBAC | EMPLOYEES.GRADE integer drives access level; Grade ≥8 full, 5–7 view-all, <5 own-only | PKG_SECURITY.has_permission | **Keep (formalize)** | Simple and effective model; formalize as an explicit RBAC table with defined roles; remove implicit grade-integer dependency |
| PAT-007 | Point-in-Time Salary History | SALARY_RECORDS uses effective-date + null-end-date for current record | PKG_PAYROLL, PKG_COMPENSATION | **Keep** | Correct temporal pattern; translate to bitemporal model in new system |
| PAT-008 | Sequence-Driven Surrogate Keys | NOCACHE sequences for all primary keys | All tables; SQ_EMPLOYEE_ID | **Keep (tune)** | Standard; enable CACHE (>50) in new system to eliminate serialization bottleneck |
| PAT-009 | Audit Columns Pattern | CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE on all tables | All core tables | **Keep** | Carry forward; consider audit trigger auto-population in new system |
| PAT-010 | Single Audit Log Table | All log types (ERROR, INFO, DML) in one AUDIT_LOG table | PKG_COMMON.log_error / log_info | **Replace** | Single purge policy; no structured format; no severity levels; replace with structured logging to separate stores |
| PAT-011 | CONNECT BY Recursive Hierarchy | Oracle CONNECT BY for department hierarchy | VW_DEPARTMENT_HIERARCHY | **Replace** | Oracle-specific; performance degrades at scale; replace with adjacency list + recursive CTE in new system |
| PAT-012 | Notification Queue (async dispatch) | NOTIFICATION_QUEUE table as async message bus | PKG_NOTIFICATION | **Keep (extend)** | Sound pattern; extend to support retry, dead-letter queue, and multiple channel types properly |
| PAT-013 | Stub Procedures with False-Success Logging | Unimplemented procedures that log completion | PKG_INTEGRATION.sync_org_structure, import_time_attendance, refresh_reporting_tables | **Replace immediately** | Active liability; creates false monitoring signals; stubs must either be implemented or removed before go-live |
| PAT-014 | Direct Database Integration (Shared Database) | All bounded contexts share the same Oracle schema with no ACL | All packages | **Replace** | Eliminates independent deployability; creates hidden coupling; replace with API layer between contexts |
| PAT-015 | Denormalized Reporting Layer (RPT_* tables) | Nightly truncate-repopulate of denormalized reporting tables | PKG_REPORTING / RPT_* tables | **Evaluate** | Pattern is sound if implemented; current implementation is entirely missing; evaluate against materialized views or dedicated reporting replica |
| PAT-016 | Application-Layer Encryption (AES-256) | PL/SQL encrypts/decrypts PII at point of use | PKG_SECURITY, EMPLOYEES.SSN, bank accounts | **Keep (fix key management)** | Encryption algorithm is sound; key management is critically broken; migrate to Oracle Wallet or KMS |
| PAT-017 | Configuration in SYSTEM_PARAMETERS Table | Runtime configuration stored in DB table | PKG_SECURITY (partially), PKG_COMMON | **Keep (enforce)** | Good pattern undermined by code that ignores it; enforce all runtime config reads from SYSTEM_PARAMETERS |
| PAT-018 | Payroll Status Machine | PAYROLL_RUNS.STATUS: DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED | PKG_PAYROLL | **Keep (extend)** | Clear lifecycle; add DISBURSED status once ACH is implemented; add GL_FEED_SENT tracking |

---

## 8. Component Dependency Map

### 8.1 Package-to-Package Dependencies

| Source Component | Depends On | Dependency Type | Notes |
|-----------------|-----------|----------------|-------|
| PKG_EMPLOYEE | PKG_SECURITY | Calls: authenticate, revoke_access (non-existent) | Authentication check; access revocation on terminate |
| PKG_EMPLOYEE | PKG_COMMON | Calls: log_error, log_info | Audit logging |
| PKG_EMPLOYEE | PKG_NOTIFICATION | Calls: send_notification | Hire/terminate notifications |
| PKG_PAYROLL | PKG_EMPLOYEE | Reads: EMPLOYEES (salary, status, grade) | Employee data for pay calculation |
| PKG_PAYROLL | PKG_SECURITY | Calls: authenticate | Session validation |
| PKG_PAYROLL | PKG_COMMON | Calls: log_error, log_info | Audit logging |
| PKG_PAYROLL | PKG_PERFORMANCE | Reads: OVERALL_RATING | Merit eligibility check (Rating ≥ 3) |
| PKG_LEAVE | PKG_EMPLOYEE | Reads: EMPLOYEES (status, hire_date) | Active employee validation |
| PKG_LEAVE | PKG_SECURITY | Calls: authenticate, has_permission | Session and RBAC check |
| PKG_LEAVE | PKG_COMMON | Calls: log_error, log_info | Audit logging |
| PKG_LEAVE | PKG_NOTIFICATION | Calls: send_notification | Leave approval notifications |
| PKG_PERFORMANCE | PKG_EMPLOYEE | Reads: EMPLOYEES | Review subject lookup |
| PKG_PERFORMANCE | PKG_SECURITY | Calls: has_permission | RBAC for review access |
| PKG_PERFORMANCE | PKG_COMMON | Calls: log_error, log_info | Audit logging |
| PKG_INTEGRATION | PKG_EMPLOYEE | Reads: EMPLOYEES, DEPARTMENTS | Benefits feed, GL journal |
| PKG_INTEGRATION | PKG_PAYROLL | Reads: PAYROLL_RUNS, PAYROLL_DETAILS | GL journal generation |
| PKG_INTEGRATION | PKG_COMMON | Calls: log_error, log_info | Audit logging |
| PKG_SECURITY | PKG_COMMON | Calls: log_error, log_info | Auth audit |
| PKG_REPORTING | PKG_EMPLOYEE | Reads: EMPLOYEES, DEPARTMENTS | All 7 reports |
| PKG_REPORTING | PKG_PAYROLL | Reads: PAYROLL_DETAILS, PAYROLL_RUNS | Payroll summary report |
| PKG_REPORTING | PKG_LEAVE | Reads: LEAVE_BALANCES, LEAVE_TYPES | Leave utilization report |
| PKG_REPORTING | PKG_COMMON | Calls: log_info | Stub logging |
| PKG_NOTIFICATION | PKG_COMMON | Calls: log_error, log_info | Notification audit |
| PKG_NOTIFICATION | PKG_SECURITY | Implied: reads EMPLOYEES.EMAIL | Recipient resolution |

### 8.2 Form-to-Package Dependencies

| Oracle Form | Calls Package(s) | Notes |
|------------|----------------|-------|
| HRMS_EMPLOYEE | PKG_EMPLOYEE, PKG_SECURITY, HRMS_VALIDATION_LIB | All employee CRUD; salary validation (soft) |
| HRMS_PAYROLL | PKG_PAYROLL, PKG_SECURITY, PKG_REPORTING | Payroll run management; reporting calls |
| HRMS_LOGIN | PKG_SECURITY | authenticate; EMP_ID lookup — single WHEN OTHERS handler is defect |
| HRMS_LEAVE | PKG_LEAVE, PKG_SECURITY | Leave request submission and approval |
| HRMS_REPORTS | PKG_REPORTING, PKG_SECURITY | Report launcher; 7 report procedures |

### 8.3 Table-to-Package Access Matrix (Critical Tables)

| Table | PKG_EMPLOYEE | PKG_PAYROLL | PKG_LEAVE | PKG_PERFORMANCE | PKG_INTEGRATION | PKG_SECURITY | PKG_REPORTING |
|-------|:-----------:|:-----------:|:---------:|:---------------:|:---------------:|:------------:|:-------------:|
| EMPLOYEES | R/W | R | R | R | R | R | R |
| DEPARTMENTS | R/W | R | — | — | R | — | R |
| SALARY_RECORDS | R/W | R | — | — | — | — | R |
| PAYROLL_RUNS | — | R/W | — | — | R | — | R |
| PAYROLL_DETAILS | — | R/W | — | — | R | — | R |
| LEAVE_BALANCES | — | — | R/W | — | — | — | R |
| PERFORMANCE_REVIEWS | — | R | — | R/W | — | — | — |
| EMPLOYEE_DEPENDENTS | — | — | — | — | R | — | — |
| EMPLOYEE_BANK_ACCOUNTS | — | **NONE** | — | — | — | — | — |
| USER_SESSIONS | — | — | — | — | — | R/W | — |
| USER_CREDENTIALS | — | — | — | — | — | R/W* | — |
| AUDIT_LOG | W | W | W | W | W | W | — |

*USER_CREDENTIALS: PKG_SECURITY.change_password writes; PKG_SECURITY.authenticate **never reads** (critical defect).

### 8.4 External Dependency Map

```
[Oracle Forms 12c]
    │── HRMS_EMPLOYEE.fmx ──────────────────► PKG_EMPLOYEE
    │── HRMS_PAYROLL.fmx ───────────────────► PKG_PAYROLL
    │── HRMS_LOGIN.fmx ─────────────────────► PKG_SECURITY
    │── HRMS_LEAVE.fmx ─────────────────────► PKG_LEAVE
    └── HRMS_REPORTS.fmx ───────────────────► PKG_REPORTING

[Self-Service Portal] ─── (undeclared credentials) ──► PKG_LEAVE

[PKG_INTEGRATION]
    │── export_benefits_feed ──► UTL_FILE ──► BENEFITS_YYYYMMDD.txt ──► [ADP External]
    │── generate_gl_journal ───► UTL_FILE ──► GL_FEED_YYYYMMDD.dat ───► [Oracle Financials GL]
    │── import_time_attendance ► UTL_FILE ──► CSV read ──► STUB (no DML)
    │── sync_org_structure ────► STUB (no LDAP connection)
    └── export_nacha_file ─────► STUB (no ACH file generation)

[PKG_NOTIFICATION]
    │── send_notification ─────► UTL_MAIL ──► [SMTP Server] ──► Employee email
    └── send_sms ──────────────► STUB (no SMS gateway)

[DBMS_SCHEDULER] ──► (implied) payroll queue processing ──► PKG_PAYROLL
                 ──► (implied) nightly RPT_* refresh ──► PKG_REPORTING.refresh_reporting_tables (STUB)

[Oracle Reports .rdf] ──► (implied) ──► PKG_REPORTING (REF CURSOR)
```

### 8.5 Circular / Problematic Dependencies

| Dependency | Type | Risk |
|-----------|------|------|
| BC-01 Employee ↔ BC-07 Org Structure | Bidirectional shared kernel | DEPARTMENT_ID in EMPLOYEES; MANAGER_ID in DEPARTMENTS; changes to either break both |
| PKG_SECURITY reads EMPLOYEES.GRADE | Grade owned by PKG_EMPLOYEE; consumed by PKG_SECURITY for RBAC | Grade change in employee record immediately changes access level with no approval workflow |
| PKG_PAYROLL reads PERFORMANCE_REVIEWS.OVERALL_RATING | Conformist coupling; compensation depends on performance context without a defined contract | Rating changes retroactively affect payroll eligibility |
| PKG_REPORTING queries all OLTP tables directly | Report procedures join across all bounded contexts in single queries | Any schema change breaks reports; no caching layer; OLTP load from reporting queries |

---

## Appendix A: Architecture Violation Register Summary

| AV ID | Violation | Severity | Owning Component |
|-------|-----------|----------|-----------------|
| AV-001 | Authentication bypass — password never verified | Critical | PKG_SECURITY |
| AV-002 | Hard-coded encryption key in source | Critical | PKG_SECURITY |
| AV-003 | COBRA gap — federal compliance | Critical | PKG_EMPLOYEE |
| AV-004 | calculate_final_pay does not exist | Critical | PKG_PAYROLL |
| AV-005 | Direct deposit non-functional | Critical | PKG_PAYROLL / EMPLOYEE_BANK_ACCOUNTS |
| AV-006 | HEAD_OF_HOUSEHOLD $0 federal tax | Critical | PKG_PAYROLL |
| AV-007 | No CI/CD pipeline | Critical | Repository-wide |
| AV-008 | No automated tests | Critical | Repository-wide |
| AV-009 | MD5 password hashing | Critical | PKG_SECURITY |
| AV-010 | False-success logging in three stub integrations | High | PKG_INTEGRATION |
| AV-011 | RPT_* tables never populated | High | PKG_REPORTING |
| AV-012 | Calibration workflow absent | High | PKG_PERFORMANCE |
| AV-013 | Orphan sessions never swept | High | PKG_SECURITY |
| AV-014 | GL feed no sent-date tracking | High | PKG_INTEGRATION |
| AV-015 | Routing numbers plaintext | High | EMPLOYEE_BANK_ACCOUNTS |
| AV-016 | Portal DB credentials undeclared | High | PKG_LEAVE |
| AV-017 | FMLA misconfigured (no docs required) | Medium | Reference data |
| AV-018 | SYSTEM_PARAMETERS timeout ignored | Medium | PKG_SECURITY |
| AV-019 | Oracle Forms build not scripted | Medium | Repository-wide |
| AV-020 | Accrual retry assignment vs. increment bug | High | PKG_LEAVE |
| AV-021 | EMPLOYEE_DEPENDENTS not inactivated on termination | High | PKG_EMPLOYEE |
| AV-022 | BENEFITS_ENROLLED never read | High | PKG_INTEGRATION |
| AV-023 | Salary grade validation non-blocking | Medium | PKG_EMPLOYEE / HRMS_VALIDATION_LIB |
| AV-024 | Direct deposit unimplemented | Critical | PKG_PAYROLL |
| AV-025 | Bank account decryption path missing | High | PKG_SECURITY / EMPLOYEE_BANK_ACCOUNTS |

---

## Appendix B: Migration Risk Summary

| Risk ID | Area | Risk | Severity | Notes |
|---------|------|------|----------|-------|
| MR-001 | Encryption | AES key must be rotated before migration; all encrypted PII must be re-encrypted | Critical | Coordinate with security team; Oracle Wallet or KMS required |
| MR-002 | Authentication | Password hashes cannot be migrated (MD5); forced password reset required | Critical | Plan user communication |
| MR-003 | Direct Deposit | EMPLOYEE_BANK_ACCOUNTS has never been used in production; data quality unknown | Critical | Verify data before ACH go-live |
| MR-004 | Oracle MEDIAN() | No direct PostgreSQL/SQL Server equivalent; report logic requires translation | Medium | Use PERCENTILE_CONT(0.5) in target platform |
| MR-005 | CONNECT BY | Oracle-specific recursive query; replace with recursive CTE | Medium | All hierarchy reports affected |
| MR-006 | Oracle Forms | .fmb source must be compiled with Forms Builder 12c; no build script exists | High | Script compilation before any environment change |
| MR-007 | CALIBRATED_RATING | Column exists but is never populated; data migration produces empty column | Medium | Decide whether to carry forward or retire |
| MR-008 | RPT_* tables | Tables likely empty; confirm before including in migration scope | Medium | Confirm with DBA whether tables have ever held data |
| MR-009 | PAYROLL_RUNS PAID status | Records marked PAID with no actual disbursement; reconciliation required pre-migration | High | Manual audit of all PAID records before cutover |

<!-- GAP-FILLED SECTION -->
Looking at the source code, I can extract all the details needed for Section 3.2. The provided snippet shows Section 1.1 (unchanged), and I'm appending the gap-filled Section 3.2 below it.

---

Looking at the source content, the PKG_INTEGRATION package spec and body contain **no NACHA/ACH procedure** — not even a stub signature. The gap description says a signature exists, but neither `.pks` nor `.pkb` has one. The source confirms complete absence, which is itself the fillable data point. I'll annotate COMP-005's Notes with that finding.

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] NACHA/ACH (INT-003): absent from both spec and body — no procedure signature, no file-generation logic, no account/routing-number handling, and no file-transmission code exist anywhere in PKG_INTEGRATION; `import_time_attendance` body contains a TODO placeholder with no CSV parsing or DB-update logic; `sync_org_structure` is an empty placeholder; FTP credentials are stored in cleartext in SYSTEM_PARAMETERS per package header comment |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |
| COMP-008 [GAP-FILLED] | PKG_REPORTING | PL/SQL Package | PKG_REPORTING.pkb (spec not found in repo) | Production — body only confirmed | 7 reporting procedures: `headcount_report` (by dept/location, FT/PT/contract/gender/tenure), `compensation_summary` (grade min/max/avg/median/compa-ratio), `turnover_report` (voluntary vs involuntary, avg tenure at exit), `new_hires_report`, `leave_utilization_report`, `payroll_summary_report` (gross/net/tax by dept), `eeo_compliance_report` (EEO category by gender); plus `refresh_reporting_tables` stub for nightly RPT_* denormalized table refresh. **Oracle Reports .rdf files: not found anywhere in repository** — report layer (formatting, scheduling, distribution) is absent; only the PL/SQL data-extraction backend exists. |

---

### 3.2 Integration Detail: ADP Benefits Feed [GAP-FILLED]

**Procedure:** `PKG_INTEGRATION.export_benefits_feed`
**Source file:** `plsql/packages/PKG_INTEGRATION.pkb`
**Vendor classification:** LEGACY — fixed-width format, ADP-specific

#### Endpoint / Output

[GAP-FILLED] Output is written to the Oracle directory object `BENEFITS_FEED_OUT`, which maps to a filesystem path on the database server. ADP retrieves the file via a separate file-transfer mechanism (not encoded in this package). There is no inbound HTTP endpoint or database link; the integration is entirely file-based.

#### Filename Pattern

[GAP-FILLED]
```
BENEFITS_YYYYMMDD.txt
```
One file is generated per invocation, named with the date of execution (`SYSDATE`). There is no run-ID suffix (unlike the GL journal feed), so multiple same-day invocations overwrite the previous file.

#### Schedule

[GAP-FILLED] No scheduler entry is visible in this package. The procedure accepts `p_effective_date IN DATE DEFAULT SYSDATE`, suggesting it is intended to be called on a specific effective date. Based on usage context it is expected to run on a regular payroll cycle cadence (e.g., bi-weekly), but no `DBMS_SCHEDULER` or `DBMS_JOB` call is present — scheduling must be configured externally or in a caller not found in this source.

#### Payload Format

[GAP-FILLED] Fixed-width flat file, one record per employee-dependent combination. Employees with no active dependents produce one record with blank dependent fields. Records are ordered by `EMP_NUMBER`, then `DEPENDENT_ID`.

No header or trailer record is written (contrast with GL journal which writes `H|...` and `T|...` delimiters).

#### Field Mapping

[GAP-FILLED]

| Position | Field | Source Column | Width | Format | Notes |
|----------|-------|---------------|-------|--------|-------|
| 1–10 | Employee Number | `EMPLOYEES.EMP_NUMBER` | 10 | Left-padded with spaces (`RPAD`) | |
| 11–40 | First Name | `EMPLOYEES.FIRST_NAME` | 30 | Left-padded | |
| 41–70 | Last Name | `EMPLOYEES.LAST_NAME` | 30 | Left-padded | |
| 71–80 | Date of Birth | `EMPLOYEES.DATE_OF_BIRTH` | 10 | `YYYY-MM-DD` | NVL to space if NULL |
| 81–90 | Hire Date | `EMPLOYEES.HIRE_DATE` | 10 | `YYYY-MM-DD` | |
| 91–102 | Employment Status | `EMPLOYEES.EMPLOYMENT_STATUS` | 12 | Left-padded | Always `ACTIVE` (filter applied) |
| 103–112 | Marital Status | `EMPLOYEES.MARITAL_STATUS` | 10 | Left-padded | |
| 113 | Gender | `EMPLOYEES.GENDER` | 1 | Single char | |
| 114–143 | Dependent First Name | `EMPLOYEE_DEPENDENTS.FIRST_NAME` | 30 | Left-padded; blank if no dependent | |
| 144–173 | Dependent Last Name | `EMPLOYEE_DEPENDENTS.LAST_NAME` | 30 | Left-padded; blank if no dependent | |
| 174–193 | Relationship | `EMPLOYEE_DEPENDENTS.RELATIONSHIP` | 20 | Left-padded; blank if no dependent | |
| 194–203 | Dependent DOB | `EMPLOYEE_DEPENDENTS.DATE_OF_BIRTH` | 10 | `YYYY-MM-DD`; blank if no dependent | |

**Total record length:** 203 characters per line.

#### Source Tables

[GAP-FILLED]
- `EMPLOYEES` — employee master; filtered to `EMPLOYMENT_STATUS = 'ACTIVE'`
- `EMPLOYEE_DEPENDENTS` — LEFT JOIN on `EMP_ID` where `ACTIVE_FLAG = 'Y'`

#### Parameters

[GAP-FILLED]

| Parameter | Direction | Type | Default | Purpose |
|-----------|-----------|------|---------|---------|
| `p_effective_date` | IN | DATE | SYSDATE | Effective date for the benefits snapshot (currently unused inside the loop — filter uses `EMPLOYMENT_STATUS = 'ACTIVE'` only, not a date predicate) |
| `p_user` | IN | VARCHAR2 | USER | Audit/logging identity passed to `PKG_COMMON.log_info` / `log_error` |

#### Error Handling

[GAP-FILLED] Single `WHEN OTHERS` handler in the outermost exception block:
1. If the UTL_FILE handle is open at the time of the error, it is closed (`UTL_FILE.FCLOSE`) to prevent file handle leaks.
2. `PKG_COMMON.log_error('PKG_INTEGRATION', 'export_benefits_feed', SQLERRM, p_user)` is called to write to the application error log.
3. The exception is re-raised (`RAISE`), propagating to the caller. There is no partial-success or retry logic; a mid-run failure leaves an incomplete file on disk with no truncation or cleanup.

There is no record-level error isolation — a single bad row will abort the entire export.

#### Known Gaps / Risks

[GAP-FILLED]
- `p_effective_date` parameter is accepted but not used in the query predicate; the feed always reflects current active employees regardless of the date passed.
- Same-day re-runs silently overwrite the previous output file; no versioning or collision guard.
- No header or trailer record; ADP consumer must rely solely on record count from the log entry.
- No file-transfer step is encoded here; the hand-off mechanism to ADP is undocumented in this codebase.

<!-- GAP-FILLED SECTION -->
### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |
| COMP-008 [GAP-FILLED] | PKG_REPORTING [GAP-FILLED] | PL/SQL Package [GAP-FILLED] | PKG_REPORTING.pks / .pkb [GAP-FILLED] | Production — critical stub [GAP-FILLED] | Seven reporting procedures: headcount, compensation summary, turnover, new hires, leave utilization, payroll summary, EEO compliance; `refresh_reporting_tables` is a no-op stub (logs a message only; no TRUNCATE/INSERT executed) — all seven denormalized tables RPT_HEADCOUNT, RPT_COMPENSATION, RPT_TURNOVER, RPT_NEW_HIRES, RPT_LEAVE_UTILIZATION, RPT_PAYROLL_SUMMARY, RPT_EEO_COMPLIANCE (TBL-INF-001 through TBL-INF-007) are consequently never populated; DDL for all seven RPT_* tables absent from source; intended nightly refresh schedule, incremental vs full-load strategy, and row-level security model are entirely undocumented; all seven live report procedures query OLTP tables directly (stale during business hours per package header); fiscal year start hard-coded to Oct 1 [GAP-FILLED] |

<!-- GAP-FILLED SECTION -->
### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent [GAP-FILLED] The package spec header explicitly declares calibration as a responsibility ("Review cycles, goal tracking, ratings, **calibration**") and names a "batch calibration job" as a caller, yet no calibration procedure or function exists anywhere in either the spec or body. Implemented procedures cover the linear review lifecycle only: `create_review_cycle` / `open_review_cycle` / `close_review_cycle`, `generate_reviews_for_cycle` (bulk-creates one review per active employee with a manager), `create_review`, `submit_self_assessment`, `submit_manager_review`, `acknowledge_review`, plus goal management (`add_goal`, `update_goal_progress`) and two read cursors (`get_team_reviews`, `get_rating_distribution`). `submit_manager_review` writes the manager's rating directly to `PERFORMANCE_REVIEWS.OVERALL_RATING` with no calibration gate — once submitted the rating is final. `get_rating_distribution` returns a read-only count/percentage breakdown per `RATING_LABEL` for a cycle and optional department but enforces no distribution targets and has no write path. Missing entirely: (1) a calibration session entity and any procedure to open/close one (`run_calibration_session` or equivalent); (2) forced-distribution enforcement — no target band percentages (e.g. top-10 / middle-70 / bottom-20) are stored or checked anywhere; (3) cross-manager normalisation — no procedure compares or adjusts ratings across managers to correct for leniency/severity bias; (4) a calibration-adjusted rating column or override path in `PERFORMANCE_REVIEWS`; (5) any audit trail for rating changes made during calibration. The referenced "batch calibration job" has no callable entry point in the package. |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. [GAP-FILLED] **USER_CREDENTIALS table — inferred schema (DDL not recovered):** The table DDL was not found in any scanned file; its full column list, constraints, and indexes remain unknown. However, `PKG_SECURITY.pkb` allows the following to be inferred with high confidence: (1) **EMP_ID NUMBER** — used as the record key in `PKG_AUDIT.log_action('USER_CREDENTIALS', p_emp_id, 'UPDATE', USER)` inside `change_password`, establishing EMP_ID as the row identifier and a probable FK to `EMPLOYEES.EMP_ID`; (2) **PASSWORD_HASH VARCHAR2(~64)** — `authenticate` declares `v_stored_hash VARCHAR2(200)` as the target for the missing credential lookup, and `hash_password` returns `RAWTOHEX(DBMS_CRYPTO.HASH(…, HASH_MD5))` which produces a 32-byte (64-character hex) string, so the stored column is almost certainly `VARCHAR2(64)` or wider; no salt column is evident from any variable name or comment, confirming the MD5-without-salt weakness. No other columns (e.g. `FAILED_ATTEMPTS`, `LOCKED_FLAG`, `PASSWORD_EXPIRY_DATE`, `LAST_CHANGED_DATE`) can be inferred from the package body — their absence from any variable declaration is consistent with the documented lack of lockout logic. **Reconstruction required** before any forward-engineering of the authentication layer. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
Looking at the provided source content for `PKG_INTEGRATION.pkb`, the `generate_gl_journal` procedure reads from `PAYROLL_RUNS` (joining on `RUN_ID` to retrieve `PERIOD_ID`) but does **not** reference `GL_FEED_SENT_DATE` or `GL_FEED_SENT_FLAG` anywhere in the recovered code. There is no `UPDATE` to `PAYROLL_RUNS` setting those columns, and no `SELECT` referencing them.

The source content does not contain the missing data, so the snippet is returned unchanged per instructions:

---

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] `import_time_attendance` is an unfinished stub: it opens a file from the `TIME_ATTENDANCE_IN` Oracle directory object, reads lines, and skips comment lines (prefix `#`), but the body contains only a counter increment and an explicit `-- TODO: Implement actual parsing and database update` comment — no INSERT or UPDATE statement was ever written. The CSV format is documented in that same comment as four columns: `emp_number, date, hours_regular, hours_overtime`; these four fields represent the de-facto logical schema for any `TIME_ATTENDANCE_RECORDS` staging table, but the DDL file (`sql/ddl/TIME_ATTENDANCE_RECORDS.sql`) was not found in any scan and must be considered unrecovered. Because no DML was implemented, the link between `TIME_ATTENDANCE_RECORDS` and `PAYROLL_DETAILS` is entirely absent from the codebase — the column mapping, foreign-key relationship, and update logic for `PAYROLL_DETAILS` rows based on imported hours remain unknown and would need to be designed from scratch. |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
Looking at the source code, I can extract the ADP benefits feed details from `export_benefits_feed` and construct the missing Section 3.2. I'll append it after the existing table snippet with [GAP-FILLED] markers.

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

---

### 3.2 Integration Detail: ADP Benefits Feed (INT-001) [GAP-FILLED]

**Integration ID:** INT-001
**Direction:** Outbound (HRMS → ADP)
**Mechanism:** Flat-file export via Oracle `UTL_FILE` written to Oracle directory object `BENEFITS_FEED_OUT`
**Format:** Fixed-width text — legacy ADP vendor format; no header or trailer records (code comment: *"LEGACY: Fixed-width format, specific to ADP vendor"*)
**Entry point:** `HRMS.PKG_INTEGRATION.export_benefits_feed(p_effective_date IN DATE, p_user IN VARCHAR2)`
**Schedule:** No scheduler job found in PL/SQL source; export is triggered on-demand (assumed via external scheduler or manual invocation post-payroll run)

#### Field Layout — fixed-width, one record per employee–dependent row

| Start | End | Field | Width | Source Column | Format / Notes |
|-------|-----|-------|-------|---------------|----------------|
| 1 | 10 | Employee Number | 10 | `EMPLOYEES.EMP_NUMBER` | `RPAD(NVL(…,' '),10)` |
| 11 | 40 | First Name | 30 | `EMPLOYEES.FIRST_NAME` | `RPAD(NVL(…,' '),30)` |
| 41 | 70 | Last Name | 30 | `EMPLOYEES.LAST_NAME` | `RPAD(NVL(…,' '),30)` |
| 71 | 80 | Date of Birth | 10 | `EMPLOYEES.DATE_OF_BIRTH` | `YYYY-MM-DD` via `TO_CHAR` |
| 81 | 90 | Hire Date | 10 | `EMPLOYEES.HIRE_DATE` | `YYYY-MM-DD` via `TO_CHAR` |
| 91 | 102 | Employment Status | 12 | `EMPLOYEES.EMPLOYMENT_STATUS` | `RPAD(NVL(…,' '),12)` |
| 103 | 112 | Marital Status | 10 | `EMPLOYEES.MARITAL_STATUS` | `RPAD(NVL(…,' '),10)` |
| 113 | 113 | Gender | 1 | `EMPLOYEES.GENDER` | Single character |
| 114 | 143 | Dependent First Name | 30 | `EMPLOYEE_DEPENDENTS.FIRST_NAME` | Blank-padded if no dependent |
| 144 | 173 | Dependent Last Name | 30 | `EMPLOYEE_DEPENDENTS.LAST_NAME` | Blank-padded if no dependent |
| 174 | 193 | Relationship | 20 | `EMPLOYEE_DEPENDENTS.RELATIONSHIP` | Blank-padded if no dependent |
| 194 | 203 | Dependent Date of Birth | 10 | `EMPLOYEE_DEPENDENTS.DATE_OF_BIRTH` | `YYYY-MM-DD`; blank if none |

**Total record width:** 203 characters per line

#### Data Selection

- **Source tables:** `EMPLOYEES` LEFT JOIN `EMPLOYEE_DEPENDENTS` on `EMP_ID`, filtered by `EMPLOYEE_DEPENDENTS.ACTIVE_FLAG = 'Y'`
- **Employee filter:** `EMPLOYEES.EMPLOYMENT_STATUS = 'ACTIVE'` — terminated/inactive employees excluded
- **Sort order:** `EMP_NUMBER ASC`, `DEPENDENT_ID ASC`
- **Cardinality:** One output row per employee–dependent pair; an employee with no active dependents produces one row with blank dependent fields (LEFT JOIN)

#### File Naming

Pattern: `BENEFITS_YYYYMMDD.txt` — date suffix derived from `SYSDATE` at time of export; file written to Oracle directory object `BENEFITS_FEED_OUT` (server-side OS path mapped externally to this object name)

#### Error Handling

- **File-level:** `WHEN OTHERS` exception block guards `UTL_FILE.IS_OPEN` before closing the handle, then calls `PKG_COMMON.log_error('PKG_INTEGRATION', 'export_benefits_feed', SQLERRM, p_user)` and re-raises
- **No partial-write recovery:** a mid-export failure leaves an incomplete file on disk with no rollback or rename-to-error mechanism
- **No record-level isolation:** a single row failure aborts the entire export; there is no skip-and-continue logic
- **Success logging:** on clean completion, `PKG_COMMON.log_info` records the exported record count and filename

#### Known Gaps / Risks

- **No push/delivery mechanism found:** source code writes the file locally only; no SFTP, MQ, or API call to ADP is present — delivery is assumed to be handled externally
- **No record-count trailer:** unlike the GL journal feed (which writes a `T|<count>` trailer), the benefits file has no trailer record; ADP-side validation of completeness is not possible from the file alone
- **No scheduling definition in source:** trigger mechanism is unknown; a missed execution would silently skip an enrollment sync cycle
- **Legacy format lock-in:** the fixed-width layout is explicitly marked as vendor-specific; any ADP format upgrade requires rewriting the entire procedure
| COMP-008 | PKG_REPORTING | PL/SQL Package | PKG_REPORTING.pks / .pkb | Production — known issues | [GAP-FILLED] Headcount, compensation, turnover, and compliance reporting package. Exposes a single shared `t_report_cursor` REF CURSOR type. Eight procedures: `headcount_report` (active headcount by dept/location with FT/PT/contract and gender splits, average tenure); `compensation_summary` (salary ranges, averages, median, and compa-ratio by dept/grade/job); `turnover_report` (terminations, turnover %, voluntary vs. involuntary, average tenure at exit by dept); `new_hires_report` (hire listing with dept, job, location, salary, and manager); `leave_utilization_report` (entitled vs. used vs. remaining days and utilisation % by dept/leave-type for a calendar year); `payroll_summary_report` (gross, federal/state/SS/Medicare taxes, total deductions, and net by dept for a payroll period); `eeo_compliance_report` (headcount by EEO category with gender breakdown and female %); `refresh_reporting_tables` (nightly truncate-and-repopulate of all RPT_* denormalised tables — stub body delegates to `PKG_COMMON.log_info`). Dependencies: PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON. Called by: HRMS_REPORTS Oracle Form, Oracle Reports (.rdf) batch jobs (INT-008). Known defects: (1) RPT_* reporting tables refreshed nightly — data is stale throughout the business day; (2) fiscal year start hard-coded to 1 Oct in report logic, not configurable. |

<!-- GAP-FILLED SECTION -->
The gap for COMP-006 is already fully addressed in the document snippet — the existing `[GAP-FILLED]` annotation covers every point raised in the gap description (missing `USER_CREDENTIALS` lookup, unused `p_password`, unpopulated hash variables, disconnected `hash_password` call path, hard-coded encryption key, absent lockout counter, timing-attack vector). The source content confirms all of these findings but adds no new information beyond what is already documented.

Returning the snippet unchanged per instructions:

---

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent [GAP-FILLED] Package body (recovered from file_cache.json) confirms the following procedures and functions are implemented: `create_review_cycle` (inserts REVIEW_CYCLES in DRAFT status), `open_review_cycle` (DRAFT→OPEN transition with guard), `close_review_cycle`, `create_review` (inserts PERFORMANCE_REVIEWS with status NOT_STARTED and fires email notification to employee via PKG_NOTIFICATION), `submit_self_assessment` (transitions to MANAGER_REVIEW and notifies reviewer), `submit_manager_review` (applies 1.0–5.0 numeric rating with five-tier label mapping: Exceptional ≥4.5 / Exceeds Expectations ≥3.5 / Meets Expectations ≥2.5 / Needs Improvement ≥1.5 / Unsatisfactory <1.5; transitions to COMPLETED; notifies employee), `acknowledge_review` (COMPLETED→ACKNOWLEDGED, stores employee comments and ACK timestamp), `add_goal` / `update_goal_progress` (PERFORMANCE_GOALS with weight, category, progress percentage), `get_team_reviews` (manager-scoped REF CURSOR join across EMPLOYEES/JOB_TITLES/DEPARTMENTS), `get_rating_distribution` (department-filterable percentage breakdown by RATING_LABEL), and `generate_reviews_for_cycle` (bulk-inserts reviews for all ACTIVE employees with a non-null MANAGER_EMP_ID, skipping duplicates via DUP_VAL_ON_INDEX). The calibration workflow is entirely absent: the package spec header explicitly lists "calibration" as a function and states the package is "Called by: HRMS_PERFORMANCE form, **batch calibration job**", yet no `calibrate_ratings`, `adjust_rating`, `submit_calibration`, `lock_calibrated_ratings`, or equivalent procedure exists in either the spec or the body. `get_rating_distribution` returns distribution percentages and is the only infrastructure that could support calibration analysis, but it is read-only — there is no mechanism to apply cross-manager rating adjustments, enforce forced-ranking or bell-curve targets, record a calibration state, or transition reviews to a CALIBRATED status. Any batch calibration job referencing this package will fail at compile time with `PLS-00302` for every calibration entry-point it attempts to call. |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] Package body (recovered from file_cache.json) confirms two procedures are fully implemented and three are non-functional stubs; NACHA/ACH is entirely absent. Detailed breakdown: (1) `generate_gl_journal` — FUNCTIONAL: reads `PAYROLL_DETAILS` joined to `DEPARTMENTS`/`PAY_ELEMENTS`, writes pipe-delimited flat file (`GL_JOURNAL_<run_id>_<date>.dat`) to Oracle directory object `GL_FEED_OUT` via `UTL_FILE`; header record (`H|`), per-department debit/credit detail records (`D|`) with EARNING→debit / non-EARNING→credit logic, and trailer record (`T|entries`); consumed by Oracle Financials batch import. Known limitation: uses flat-file UTL_FILE exchange rather than direct API, and there is no retry logic for failed file transfers. (2) `export_benefits_feed` — FUNCTIONAL: writes fixed-width ADP-format enrollment file (`BENEFITS_<date>.txt`) to `BENEFITS_FEED_OUT` for all active employees including dependents; field layout: EmpNum(10), FName(30), LName(30), DOB(10), HireDate(10), Status(12), MaritalStatus(10), Gender(1), DepFName(30), DepLName(30), Relationship(20), DepDOB(10); marked LEGACY in source comments. (3) `import_time_attendance` — STUB: opens CSV from directory object `TIME_ATTENDANCE_IN`, loops through non-comment lines, and increments a counter — but contains an explicit `TODO: Implement actual parsing and database update` comment; CSV field order (emp_number, date, hours_regular, hours_overtime) is documented in a comment but no parsing logic exists; no `EMPLOYEE_TIME_ENTRIES` or equivalent table is populated; consequence: time-based pay inputs from the external T&A system never reach payroll processing. (4) `sync_org_structure` — STUB: body contains only a single `PKG_COMMON.log_info` call logging `'Org structure sync completed'`; no LDAP/AD query, no directory object, no `DEPARTMENTS` or `EMPLOYEES` update; the package spec comment identifies the target as `LDAP/AD` but no connection or API call of any kind is present; org hierarchy changes in the external directory are never reflected in HRMS. (5) NACHA/ACH — ENTIRELY ABSENT: neither the package spec nor the package body declares any procedure for NACHA/ACH direct-deposit file generation; no `t_nacha_*` type, no `generate_nacha_file` or equivalent procedure exists anywhere in the package; the current notes label it a stub but it is not even stubbed — it is a missing feature with zero implementation; consequence: direct-deposit payment disbursement has no outbound ACH file path, meaning any downstream bank transmission process has no callable entry point in the HRMS package layer. Additional cross-cutting defects noted in the package spec header: FTP credentials for file transfer are stored in the `SYSTEM_PARAMETERS` table in cleartext; no retry or idempotency logic exists for any of the file-based integrations. |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] `import_time_attendance` procedure reads CSV files from Oracle directory object `TIME_ATTENDANCE_IN` (constant `c_time_input_dir`); the expected CSV layout is inferred from an inline code comment: `emp_number,date,hours_regular,hours_overtime`. However, the procedure body contains only file-open, line-read, and comment-skip logic followed by a `TODO: Implement actual parsing and database update` comment — no `INSERT`, `UPDATE`, or `MERGE` DML is present. Consequently: (1) the `TIME_ATTENDANCE_RECORDS` DDL was never created or is entirely absent from the source base, consistent with the DDL file not being found; (2) no link to `PAYROLL_DETAILS` is established at any point in the package — the procedure counts imported lines (`v_imported`) and logs the count but writes nothing to any table; (3) the four fields implied by the CSV format (`EMP_NUMBER`, `WORK_DATE`, `HOURS_REGULAR`, `HOURS_OVERTIME`) represent the intended table columns but remain unconfirmed by any schema artefact. Operational consequence: time and attendance data read from the external feed is silently discarded — downstream payroll calculations in `PKG_PAYROLL` receive no hours input from this integration path, meaning overtime and irregular-hours pay elements cannot be system-driven and must be entered by another means. |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |
| COMP-008 | PKG_REPORTING | PL/SQL Package | PKG_REPORTING.pks / .pkb | Production — non-functional (refresh stub) | Headcount, compensation, turnover, new-hires, leave utilisation, payroll summary, and EEO compliance reports; called by HRMS_REPORTS form, Oracle Reports (.rdf), and batch jobs; dependencies: PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON [GAP-FILLED] `refresh_reporting_tables` is a no-op stub: the procedure body contains only a `PKG_COMMON.log_info` call and an inline comment (*"In production, this truncates and repopulates RPT_* tables"*) — no `TRUNCATE`, `INSERT`, `MERGE`, or `DELETE` statement is present, so all seven RPT_* denormalised reporting tables are never populated. Consequence: any downstream consumer (Oracle Reports .rdf, HRMS_REPORTS form, batch extracts) that reads pre-aggregated data from RPT_* tables will return empty result sets regardless of the nightly job schedule; the seven live-query procedures (`headcount_report`, `compensation_summary`, `turnover_report`, `new_hires_report`, `leave_utilization_report`, `payroll_summary_report`, `eeo_compliance_report`) bypass RPT_* tables entirely and query OLTP tables directly via REF CURSOR, so they remain individually functional but bypass the intended denormalisation layer and impose full OLTP query load at report time. Additional known issues recorded in the package spec: denormalised tables are stale during business hours even if the refresh were implemented (nightly-only cadence), and fiscal-year start is hard-coded to October 1 with no parameter override. |

<!-- GAP-FILLED SECTION -->
Looking at the source content provided: the DDL file is explicitly marked as not found, and the PKG_PAYROLL.pkb excerpt — while recovered — is truncated before any SELECT statement in `calculate_employee_pay` appears. The visible portion references `SALARY_RECORDS`, `PAY_PERIODS`, `PAYROLL_RUNS`, `PAYROLL_DETAILS`, and `EMPLOYEES`, but `EMPLOYEE_PAY_ELEMENTS` is never named in the shown code.

Per the instructions: the source content does not contain the missing data, so the snippet is returned unchanged.

---

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] `export_benefits_feed` is the ADP benefits enrollment feed (INT-001): writes a fixed-width flat file to Oracle directory object `BENEFITS_FEED_OUT` under filename pattern `BENEFITS_YYYYMMDD.txt`. Record layout is 203 chars per line — EmpNum(10), FirstName(30), LastName(30), DOB(10), HireDate(10), EmploymentStatus(12), MaritalStatus(10), Gender(1), DepFirstName(30), DepLastName(30), Relationship(20), DepDOB(10) — padded with `RPAD`/`NVL` to guarantee fixed width. Data source: `EMPLOYEES LEFT JOIN EMPLOYEE_DEPENDENTS` (active dependents, `ACTIVE_FLAG='Y'`); scope filter: `EMPLOYMENT_STATUS='ACTIVE'` employees only; ordered by `EMP_NUMBER, DEPENDENT_ID` so one row is emitted per employee-dependent combination. The procedure is explicitly annotated `LEGACY` in the package body comment. `generate_gl_journal` writes a pipe-delimited flat file (H-header / D-detail debit-credit rows / T-trailer with record count) to Oracle directory `GL_FEED_OUT` for consumption by Oracle Financials batch import; debit/credit assignment is determined by `PAY_ELEMENTS.ELEMENT_TYPE` (`'EARNING'` → debit expense account, all others → credit liability account). `import_time_attendance` (CSV input from directory `TIME_ATTENDANCE_IN`) and `sync_org_structure` (LDAP/AD placeholder) are non-functional stubs — both bodies contain only TODO/placeholder comments with zero implemented logic. NACHA is absent from both package spec and body (no procedure declared or implemented) despite being referenced in the component inventory. Known defects declared in package spec header: (1) no retry logic for failed file transfers; (2) FTP credentials stored in cleartext in the `SYSTEM_PARAMETERS` table. |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
Looking at the `PKG_INTEGRATION.pkb` source, the `generate_gl_journal` procedure queries `PAYROLL_RUNS` (joins it for the run's period info) and writes the flat file, but **never issues any UPDATE back to `PAYROLL_RUNS`** after the file is written — no `GL_FEED_SENT_FLAG`, no `GL_FEED_SENT_DATE`, no status column of any kind is set. This directly confirms the gap. Here is the updated snippet:

---

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] `PAYROLL_RUNS` table is missing `GL_FEED_SENT_DATE` and `GL_FEED_SENT_FLAG` columns — GL feed tracking state cannot be determined from the table. Confirmed by inspecting `generate_gl_journal` in the recovered package body: the procedure generates the pipe-delimited flat file (written via `UTL_FILE` to the `GL_FEED_OUT` Oracle directory object, named `GL_JOURNAL_<run_id>_<YYYYMMDD>.dat`) and logs success via `PKG_COMMON.log_info`, but **issues no UPDATE to `PAYROLL_RUNS`** after the file is written — there is no `SET GL_FEED_SENT_FLAG`, `GL_FEED_SENT_DATE`, or any equivalent status column stamped on the run record. Consequence: there is no reliable programmatic way to determine, for a given payroll run, whether its GL journal file has already been generated and dispatched to Oracle Financials; re-running `generate_gl_journal` for the same `p_run_id` will silently overwrite the previously generated file (same naming scheme) with no duplicate-send guard, creating a double-posting risk in the downstream GL batch import. Reconciliation between payroll runs and posted GL journals must currently be performed out-of-band (e.g., by checking the filesystem for the `.dat` file or querying `SYS_LOG` entries), rather than by querying `PAYROLL_RUNS` directly. |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
The source content for `PKG_PAYROLL.pkb` is truncated mid-procedure — it cuts off inside `calculate_employee_pay` before reaching the `INSERT INTO PAYROLL_DETAILS` statements where ELEMENT_ID values 100–103 would be assigned. The constants and variable declarations (`v_federal_tax`, `v_ss_tax`, `v_medicare_tax`, `v_period_gross`) suggest the four IDs likely correspond to those four pay components, but no explicit mapping appears in the recovered source. Per the fill instructions, the snippet is returned unchanged.

---

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production — seed data defect | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect [GAP-FILLED] `sql/seed/LEAVE_TYPES.sql` was not found in the deep scan — the corrected seed script is absent from the repository. The FMLA leave type record contains `REQUIRES_DOCUMENT='N'`, which is a misconfiguration: FMLA (Family and Medical Leave Act) legally mandates medical certification/documentation under 29 U.S.C. § 2613, so the flag must be `'Y'`. Compounding the seed defect, the recovered `PKG_LEAVE.pkb` body confirms that `submit_leave_request` fetches the full `LEAVE_TYPES%ROWTYPE` into `v_leave_type` and inspects `v_leave_type.REQUIRES_APPROVAL`, `v_leave_type.ACCRUAL_FLAG`, and `v_leave_type.MIN_TENURE_DAYS` — but **never references `v_leave_type.REQUIRES_DOCUMENT`** anywhere in the procedure. This means the enforcement path is entirely absent: even if the FMLA seed row were corrected to `REQUIRES_DOCUMENT='Y'`, the package would not prompt for, validate, or store any supporting documentation at submission time. The dual gap (wrong seed value + no package enforcement) means FMLA requests can be submitted and approved without any documentation check, exposing the organisation to compliance risk. |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

<!-- GAP-FILLED SECTION -->
Looking at the source content, I can see the `PKG_LEAVE.pkb` file is truncated — it ends mid-function inside `get_leave_balance` at the `NO_DATA_FOUND` exception handler, and the `initialize_balances` procedure is not present in the recovered fragment. There is no source material in the provided content from which to derive the nature, trigger condition, or impact of the accrual retry defect.

Per the instructions, returning the snippet unchanged:

---

The source content does not contain the missing data for INT-009. `portal_user.sql` was not found, and `PKG_LEAVE.pks` only confirms the self-service portal calls the package (header comment: *"Called by: HRMS_LEAVE form, self-service portal, batch accrual job"*) — it reveals nothing about the portal's DB connection account, granted privileges, or whether a dedicated schema/role exists.

Returning the snippet unchanged per instructions:

The existing COMP-006 row mentions the hard-coded key but doesn't cover the absent key rotation and key storage details. Here is the updated snippet with that elaboration appended as a second [GAP-FILLED] block:

---

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. [GAP-FILLED] Key rotation and secure storage detail: `c_encryption_key` is declared as a package-level `RAW(32)` constant initialised at compile time from a hardcoded string literal (`UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!'))` — the plaintext key is therefore embedded in the package body source and visible to any DBA with `SELECT` privilege on `DBA_SOURCE` or access to the source file, with no runtime indirection. No key rotation procedure exists anywhere in the package or in the wider codebase: there is no `rotate_encryption_key`, no re-encryption utility, and no versioned-key column on the tables that store encrypted SSNs; a key change would require a full-table decrypt-and-re-encrypt operation with no supporting code path. No secure key storage integration is present: there is no reference to Oracle Wallet (`ADMINISTER KEY MANAGEMENT` / `MKSTORE`), Oracle Transparent Data Encryption master key, Hardware Security Module (HSM) linkage, or any external vault (e.g. HashiCorp Vault, Oracle Key Vault); the key is a static compile-time artefact with a lifetime tied to the package source rather than to any key-management lifecycle. Combined consequence: the SSN values encrypted by `encrypt_ssn` / `decrypt_ssn` are protected only by database source-code access controls; a single source-code disclosure event exposes every encrypted SSN in the system simultaneously; there is no remediation path (rotation, re-keying, or revocation) short of a manual DBA intervention with custom one-off scripts. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |
| COMP-008 | PKG_REPORTING | PL/SQL Package | PKG_REPORTING.pks / .pkb | Production — Oracle Reports bindings unconfirmed [GAP-FILLED] Package body recovered from file_cache.json; no corresponding `reports/*.rdf` files found anywhere in the repository deep scan (INT-008 status confirmed Uncertain — .rdf layer is absent). The PL/SQL layer is fully implemented and contains eight procedures: `headcount_report` (ref-cursor output; active headcount by dept/location broken down by employment type FT/PT/Contract and gender, with average tenure; filterable by `p_dept_id` and `p_location`); `compensation_summary` (ref-cursor; salary min/max/avg/median and compa-ratio by dept/grade/job title, joining `SALARY_RECORDS` where `ACTIVE_FLAG='Y'`; filterable by dept and grade); `turnover_report` (ref-cursor; terminations, current headcount, turnover %, voluntary vs. involuntary split, and average tenure at exit over a date range; filterable by dept); `new_hires_report` (ref-cursor; hire listing with dept, job title, location, employment type, base salary, and manager name over a date range; filterable by dept); `leave_utilization_report` (ref-cursor; avg entitled/used/remaining and utilization % by dept and leave type for a given calendar year; filterable by dept); `payroll_summary_report` (ref-cursor; gross pay, federal/state tax, Social Security, Medicare, total deductions, and net pay aggregated by dept for a given `p_period_id`, sourced from `PAYROLL_DETAILS` joined to `PAYROLL_RUNS`); `eeo_compliance_report` (ref-cursor; EEO category breakdown by gender counts and female %, joining `JOB_TITLES.EEO_CATEGORY`); and `refresh_reporting_tables` (stub only — body contains a single `PKG_COMMON.log_info` call with a comment acknowledging that the production implementation should truncate and repopulate `RPT_*` denormalized tables, but no such logic is present). Binding gap: because no `.rdf` files exist in the repository, it is unknown which Oracle Reports layouts consume these ref-cursor outputs, what parameter forms invoke them, or whether any report was ever deployed to an Oracle Reports Server. The eight PL/SQL procedures are ready to be called but have no confirmed front-end delivery mechanism within the recovered codebase. |

<!-- GAP-FILLED SECTION -->
Looking at the source code, `leave_utilization_report` uses `lb.CALENDAR_YEAR = p_year` in the `WHERE` clause but never projects `CALENDAR_YEAR` into the `SELECT` list, and the `GROUP BY` only covers `(d.DEPT_NAME, lt.LEAVE_TYPE_NAME)` — leaving the year invisible to consumers and the grouping incomplete for multi-year use. PKG_REPORTING is also entirely absent from the component table, so I'll add it with the gap filled.

Looking at the source code for `generate_gl_journal` to identify the specific defect before writing the gap-fill.

The defect is clear: both branches of the debit/credit conditional write `'D|'` as the record-type prefix. The `ELSE` branch (deductions/taxes/liabilities) has the comment "credits to liability accounts" but the code writes `'D|'` instead of `'C|'`. Here is the updated snippet:

---

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] `generate_gl_journal` (INT-002) contains a definitive logic error in the debit/credit record-type field: both the EARNING branch and the ELSE branch (deductions, taxes, liabilities) write `'D|'` as the first field of every detail record. The inline comment explicitly states "Deductions/taxes are credits to liability accounts" yet the ELSE branch emits `'D|'` instead of `'C|'`. Consequence: the output pipe-delimited file contains exclusively debit (`D`) records — no credit (`C`) records are ever written regardless of element type. Oracle Financials batch import receiving this file will produce a journal with no offsetting credit side; the journal cannot post and will fail GL balancing validation. The pipe-delimited structure itself (7 fields per detail line: record-type, cost-center, GL account, debit-amount, credit-amount, description, run-reference) is internally consistent in field count — the corruption is confined to the record-type field being hardcoded to `D` in both branches. The trailer record (`T|` + entry count) reflects only total lines written and provides no debit/credit balance check, so the defect cannot self-detect. The `import_time_attendance` procedure also contains an unimplemented stub (`TODO: Implement actual parsing and database update`), meaning time-attendance data is read from file but never written to any table. |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |
| COMP-008 | PKG_REPORTING | PL/SQL Package | PKG_REPORTING.pks / .pkb | Production — defect | Report generation: headcount, compensation summary, turnover, new hires, leave utilization, payroll summary, EEO compliance; `refresh_reporting_tables` is a stub placeholder only. [GAP-FILLED] `leave_utilization_report` cursor projection (`RPT_LEAVE_UTILIZATION`) is missing `CALENDAR_YEAR` in both the `SELECT` list and the `GROUP BY` clause. The procedure accepts `p_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)` and correctly restricts rows with `WHERE lb.CALENDAR_YEAR = p_year`, but `CALENDAR_YEAR` / `p_year` is never projected into the cursor output — consumers of the open cursor receive aggregated leave-balance columns (`AVG_ENTITLED`, `AVG_USED`, `AVG_REMAINING`, `UTILIZATION_PCT`) grouped only by `(d.DEPT_NAME, lt.LEAVE_TYPE_NAME)` with no year column visible. Consequence (correctness): report output is year-ambiguous — any downstream display layer, export, or audit log cannot determine which calendar year the figures represent without passing the year value as a separate out-of-band parameter, which the procedure signature does not include in its `t_report_cursor` contract. Consequence (grouping logic): the `GROUP BY (d.DEPT_NAME, lt.LEAVE_TYPE_NAME)` is incomplete relative to the data model; removing or relaxing the `WHERE lb.CALENDAR_YEAR = p_year` predicate (e.g. for year-over-year trend analysis) would silently collapse multiple calendar years into a single aggregated row per department/leave-type pair, producing arithmetically incorrect averages across year boundaries. Fix required: add `lb.CALENDAR_YEAR` to both the `SELECT` projection (as `CALENDAR_YEAR`) and the `GROUP BY` clause; the `ORDER BY` should likewise be extended to `ORDER BY lb.CALENDAR_YEAR, d.DEPT_NAME, lt.LEAVE_TYPE_NAME` to produce deterministic, year-segregated output. |
| COMP-008 | PKG_REPORTING | PL/SQL Package | PKG_REPORTING.pks / .pkb | Production — migration risk | Headcount, compensation summary, turnover, new-hires, leave utilisation, payroll summary, EEO compliance reports; nightly `refresh_reporting_tables` stub present. [GAP-FILLED] The `compensation_summary` procedure (RPT_COMPENSATION) contains `ROUND(MEDIAN(sr.BASE_SALARY), 2) AS MEDIAN_SALARY` — `MEDIAN()` is an Oracle-proprietary aggregate function with **no direct equivalent in PostgreSQL**. The migration target dialect is unspecified in all recovered source artefacts; `sql/ddl/RPT_COMPENSATION.sql` was not found in the deep scan, so no DDL-level commentary on the column exists. Compatibility impact: if the migration target is PostgreSQL, `MEDIAN()` must be rewritten as `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY sr.BASE_SALARY)` — the ordered-set aggregate syntax differs structurally, requires explicit `GROUP BY` cooperation, and will fail silently if a naive text substitution is attempted. If the target is SQL Server or MySQL 8+, neither offers a native `MEDIAN()` aggregate either; both require an equivalent ordered-set or window-function rewrite (`PERCENTILE_CONT` in SQL Server; a subquery or `AVG` of the middle rows in MySQL). No other Oracle-proprietary aggregates (`LISTAGG`, `RATIO_TO_REPORT`, etc.) were found in this package. Migration action required: (1) confirm target dialect; (2) substitute `MEDIAN()` with the dialect-appropriate ordered-set expression before any cross-database deployment; (3) add a regression test asserting that `MEDIAN_SALARY` for a known salary distribution matches the expected value, since the rewritten expression produces identical results only when the `WITHIN GROUP` order direction matches Oracle's internal sort. |

<!-- GAP-FILLED SECTION -->
Looking at the source code and the gap description, I need to:
1. Enhance the COMP-005 row with detailed `[GAP-FILLED]` notes (the component table gap)
2. Add a new Integration Inventory section with the INT-001 row (the missing integration row)

### 1.1 PL/SQL Packages

| Comp ID | Component Name | Type | Package / File | Status | Notes |
|---------|---------------|------|----------------|--------|-------|
| COMP-001 | PKG_EMPLOYEE | PL/SQL Package | PKG_EMPLOYEE.pks / .pkb | Production | Core aggregate for hire, terminate, transfer, grade management |
| COMP-002 | PKG_PAYROLL | PL/SQL Package | PKG_PAYROLL.pks / .pkb | Production — partial | Payroll run, calculation, approval; `calculate_final_pay` procedure MISSING [GAP-FILLED] Package body (recovered from file_cache.json) contains: `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` — `calculate_final_pay` is entirely absent from the package body, confirming the gap is real and not a recovery artefact. Consequence: any termination workflow that calls `PKG_PAYROLL.calculate_final_pay` will raise `PLS-00302` (component must be declared) at compile time and will be non-functional at runtime; prorated final-period earnings, accrued-vacation payout, and severance calculations that should be performed at termination have no implementation path. The surrounding `calculate_employee_pay` procedure (present in the body) handles regular periodic pay via CASE-based frequency logic and YTD tax accumulators but contains no branch for termination-type runs; the `PAYROLL_RUNS.RUN_TYPE` column distinguishes `'REGULAR'` from other run types (e.g. `'FINAL'`) but no procedure exists to act on a final-pay run type. |
| COMP-003 | PKG_LEAVE | PL/SQL Package | PKG_LEAVE.pks / .pkb | Production | Leave balance, accrual, request, approval; `initialize_balances` has accrual retry defect |
| COMP-004 | PKG_PERFORMANCE | PL/SQL Package | PKG_PERFORMANCE.pks / .pkb | Production — incomplete | Review cycle, self/manager assessment; calibration workflow entirely absent |
| COMP-005 | PKG_INTEGRATION | PL/SQL Package | PKG_INTEGRATION.pks / .pkb | Production — partial | ADP benefits feed, GL journal, NACHA stub, time attendance stub, org structure stub [GAP-FILLED] Package body (recovered from file_cache.json) exposes five procedures and one function. `generate_gl_journal(p_run_id)`: produces pipe-delimited flat files (header `H\|`, detail `D\|`, trailer `T\|`) written to Oracle directory object `GL_FEED_OUT`; consumed by Oracle Financials batch import; queries PAYROLL_DETAILS → PAYROLL_RUNS → PAY_PERIODS → EMPLOYEES → DEPARTMENTS → PAY_ELEMENTS grouped by cost-centre and GL account; earnings become debits to expense accounts, deductions/taxes become credits to liability accounts; triggered nightly per scheduler. `export_benefits_feed(p_effective_date)`: LEGACY fixed-width ADP vendor format; filename pattern `BENEFITS_YYYYMMDD.txt` written to Oracle directory object `BENEFITS_FEED_OUT`; record layout (all RPAD-padded): EmpNum(10) \| FName(30) \| LName(30) \| DOB(10) \| HireDate(10) \| Status(12) \| Marital(10) \| Gender(1) \| DepFName(30) \| DepLName(30) \| Relationship(20) \| DepDOB(10); sources EMPLOYEES LEFT JOIN EMPLOYEE_DEPENDENTS (ACTIVE\_FLAG='Y') for all active employees and their dependents, ordered by EMP\_NUMBER; triggered on weekly schedule. `import_time_attendance(p_file_name)`: reads CSV from `TIME_ATTENDANCE_IN` (comment documents columns: emp\_number, date, hours\_regular, hours\_overtime); CSV parsing and database update logic is marked `TODO` — stub only; individual line errors are caught and logged via PKG\_COMMON.log\_error without aborting the file. `sync_org_structure`: placeholder stub for LDAP/AD directory sync — no implementation beyond a log\_info call. `get_integration_status`: reads named integration status flag from SYSTEM\_PARAMETERS via PKG\_COMMON.get\_param. Known defects declared in package spec: (1) GL posting and benefits exchange use UTL\_FILE flat files rather than direct API calls; (2) no retry logic for failed file transfers; (3) FTP credentials stored as cleartext in SYSTEM\_PARAMETERS table — active security risk. |
| COMP-006 | PKG_SECURITY | PL/SQL Package | PKG_SECURITY.pks / .pkb | Production — critical defects | Authentication (stub — password never verified), session, encryption, RBAC [GAP-FILLED] `authenticate` resolves the employee by `UPPER(EMAIL)` against `EMPLOYEES` where `EMPLOYMENT_STATUS='ACTIVE'`, then jumps directly to session creation — `p_password` is accepted but never used; local variables `v_stored_hash` / `v_input_hash` are declared but never populated or compared; the `USER_CREDENTIALS` table lookup that should supply the stored hash is entirely absent (acknowledged in a code comment: *"In the real system, passwords are stored in a separate USER_CREDENTIALS table"*). `hash_password` (MD5 via `DBMS_CRYPTO.HASH_MD5`) and `hash_password`/`authenticate` are disconnected — no call path exists between them. Additional security defects: AES-256 encryption key hard-coded as a RAW literal in package body (`HR$ystem_3ncrypt10n_K3y_2024!!`); no failed-login counter or account lockout (e_account_locked exception defined in spec but never raised); timing-attack vector — `NO_DATA_FOUND` on invalid username raises immediately while a valid-username/wrong-password path would differ in timing once the credential check is added. |
| COMP-007 | PKG_COMMON | PL/SQL Package | PKG_COMMON.pks / .pkb | Production | Logging (log_error, log_info), shared utilities |

### 1.2 Integration Inventory [GAP-FILLED]

| Int ID | Integration Name | Direction | Mechanism | Format | Frequency | Source | Target | Oracle Directory | Status | Notes |
|--------|-----------------|-----------|-----------|--------|-----------|--------|--------|-----------------|--------|-------|
| INT-001 | ADP Benefits Enrollment Feed | Outbound | UTL_FILE flat file | Fixed-width text (`BENEFITS_YYYYMMDD.txt`) | Weekly (batch scheduler) | HRMS (`PKG_INTEGRATION.export_benefits_feed`) | ADP Benefits Platform | `BENEFITS_FEED_OUT` | Production — Legacy | Record layout: EmpNum(10) \| FName(30) \| LName(30) \| DOB(10) \| HireDate(10) \| Status(12) \| Marital(10) \| Gender(1) \| DepFName(30) \| DepLName(30) \| Relationship(20) \| DepDOB(10); sources EMPLOYEES and EMPLOYEE_DEPENDENTS; vendor-specific format locked to ADP; no retry logic; FTP credentials stored as cleartext in SYSTEM_PARAMETERS |
| INT-002 | Oracle Financials GL Journal Feed | Outbound | UTL_FILE flat file | Pipe-delimited (`GL_JOURNAL_<run_id>_YYYYMMDD.dat`) | Nightly (batch scheduler, per payroll run) | HRMS (`PKG_INTEGRATION.generate_gl_journal`) | Oracle Financials | `GL_FEED_OUT` | Production | Header/detail/trailer pattern; debits for earnings, credits for deductions/taxes; no API path — file hand-off only |
| INT-003 | Time & Attendance Import | Inbound | UTL_FILE CSV read | CSV (emp\_number, date, hours\_regular, hours\_overtime) | Ad hoc (file drop) | External T&A system | HRMS (`PKG_INTEGRATION.import_time_attendance`) | `TIME_ATTENDANCE_IN` | Stub — incomplete | Parsing and DB update logic marked TODO; error logging per line is present but no actual data is written to the database |
| INT-004 | Org Structure Sync (LDAP/AD) | Outbound/Inbound | Placeholder | N/A | Unknown | HRMS (`PKG_INTEGRATION.sync_org_structure`) | LDAP / Active Directory | N/A | Stub — no implementation | Procedure body contains only a PKG\_COMMON.log\_info call; no directory connection, attribute mapping, or sync logic |
