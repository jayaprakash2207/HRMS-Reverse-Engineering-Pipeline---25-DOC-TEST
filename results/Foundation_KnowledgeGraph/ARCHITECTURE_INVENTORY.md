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
