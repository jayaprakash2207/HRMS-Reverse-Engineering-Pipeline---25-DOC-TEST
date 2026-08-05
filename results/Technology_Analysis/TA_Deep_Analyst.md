FMLA request with no supporting documentation, exposing the company to FMLA abuse claims and audit non-compliance | Configuration Risk | Medium | 01_reference_data.sql: FMLA REQUIRES_DOCUMENT='N' | Update FMLA seed data to REQUIRES_DOCUMENT='Y'; implement SUPPORTING_DOC_PATH not-null enforcement in PKG_LEAVE.submit_leave_request when REQUIRES_DOCUMENT='Y'; coordinate with TD-47 (path traversal fix for SUPPORTING_DOC_PATH) |
| TD-72 **[EDGE-CASE-FOUND]** | Oracle Forms LOV_MANAGERS includes all active employees regardless of grade — an Intern (Grade 1) can be selected as the reporting manager for a VP (Grade 9); no minimum grade check, no seniority validation, no IS_MANAGER flag | Configuration Risk | Medium | HRMS_EMPLOYEE.xml: LOV_MANAGERS: WHERE EMPLOYMENT_STATUS='ACTIVE' with no GRADE_ID or JOB_ID constraint | Add grade-based filter to LOV_MANAGERS: WHERE EMPLOYMENT_STATUS='ACTIVE' AND JOB_ID IN (SELECT JOB_ID FROM JOB_TITLES jt WHERE jt.GRADE_ID >= (SELECT GRADE_ID FROM JOB_TITLES WHERE JOB_ID = :EMPLOYEE.JOB_ID)); or introduce IS_MANAGER CHAR(1) flag on JOB_TITLES |
| TD-73 **[EDGE-CASE-FOUND]** | ADP benefits feed has no format version or record count validation — the 203-character fixed-width output contains no file version header, no record count trailer, and no checksum; if field widths change, RPAD silently truncates data without error | Architecture Anti-pattern | Medium | PKG_INTEGRATION.pkb: export_benefits_feed() — header record contains only DATE; no ADP specification version; no trailer with expected record count; no LENGTHB validation before RPAD | Add file header with format version; add trailer record with employee count; add per-record LENGTHB validation that each generated record is exactly 203 characters before writing; alert if any record would be truncated |
| TD-74 **[EDGE-CASE-FOUND]** | Salary grade validation in HRMS_VALIDATION_LIB is a soft warning only — PKG_EMPLOYEE.create_employee checks salary vs. grade range in debug mode only; HRMS_VALIDATION_LIB.validate_salary_range emits a MESSAGE warning, not RAISE FORM_TRIGGER_FAILURE; employees can be created or promoted with salaries outside their grade band without any blocking | Configuration Risk | Medium | PKG_EMPLOYEE.pkb: IF g_debug_mode THEN print_warning; HRMS_VALIDATION_LIB: validate_salary_range issues MESSAGE but no FORM_TRIGGER_FAILURE | Elevate salary-grade validation to a blocking error at both layers: RAISE_APPLICATION_ERROR(-20015, 'Salary NNN is outside grade band MIN-MAX') in PKG_EMPLOYEE.create_employee for all callers; RAISE FORM_TRIGGER_FAILURE in validate_salary_range |
| TD-75 **[EDGE-CASE-FOUND]** | Oracle Forms session persists after Forms window is closed without logout — USER_SESSIONS rows with STATUS='ACTIVE' are only invalidated via explicit PKG_SECURITY.logout or the 30-minute timeout check on next is_session_valid call; if a user closes the browser/Forms launcher without using the exit button, the session row remains ACTIVE indefinitely; no background cleanup job found | Operational Risk | Medium | PKG_SECURITY.pkb: is_session_valid() checks LOGIN_TIME + INTERVAL '30' MINUTE >= SYSDATE — timeout is only evaluated on the next call, not by a background sweep; no scheduled cleanup of stale sessions | Add DBMS_SCHEDULER job to sweep USER_SESSIONS and set STATUS='EXPIRED' for rows where LOGIN_TIME < SYSDATE - INTERVAL '30' MINUTE AND STATUS='ACTIVE'; frequency: every 5 minutes (piggyback on process_queue scheduler timing) |
| TD-76 **[EDGE-CASE-FOUND]** | Oracle Forms XML export metadata does not constitute a build-reproducible artifact — deploying the system requires Oracle Forms Builder 12c to compile .fmb → .fmx; no build script, Makefile, or CI step for Forms compilation exists; any developer without Forms Builder 12c installed cannot build the application layer | Operational Risk | Medium | No Makefile, build.sh, or Oracle Forms compile script found anywhere in repository; forms/xml-exports/*.xml are the only Forms source artifacts | Document and script the Forms compilation process: frmcmp.sh module=HRMS_EMPLOYEE.fmb userid=user/pass@db module_type=form output_file=HRMS_EMPLOYEE.fmx; include Forms Builder version requirement in README |
| TD-79 **[EDGE-CASE-FOUND]** | Oracle Financials GL feed has no Journal Source or Category validation — Oracle GL Journal Import requires specific Journal Source and Journal Category values in the .dat file; the HRMS GL feed hard-codes values derived from COST_CENTER and GL_ACCOUNT_CODE but neither Journal Source nor Journal Category field values are visible in the PKG_INTEGRATION source; an incorrect value causes Oracle Financials to reject or misroute the entire batch | Architecture Anti-pattern | Medium | PKG_INTEGRATION.pkb: pipe-delimited detail format includes cost_center and gl_account_code but Oracle GL Journal Import D-record format requires specific position-mapped fields; Journal Source/Category not documented in code | Document the Oracle Financials Journal Source and Journal Category expected by the GL import; add these as SYSTEM_PARAMETERS entries (INTEGRATION group); validate against Oracle Financials lookup before file generation |
| TD-80 **[EDGE-CASE-FOUND]** | No mechanism to detect or recover from a missed payroll GL feed — if generate_gl_journal fails or Oracle Financials rejects the file, the HRMS system has no indicator that the GL feed for a given run was not successfully consumed; PAYROLL_RUNS has no GL_FEED_STATUS field; no acknowledgement file; no reconciliation query | Operational Risk | Medium | PKG_INTEGRATION.pkb: generate_gl_journal returns no value and writes no status to PAYROLL_RUNS or any other table on completion; PAYROLL_RUNS has no GL_FEED_SENT_FLAG column | Add GL_FEED_SENT_DATE and GL_FEED_FILE_NAME columns to PAYROLL_RUNS; update them at successful UTL_FILE.FCLOSE; expose in HRMS_PAYROLL form so payroll admins can see which runs have been fed to GL |
| TD-81 **[EDGE-CASE-FOUND]** | Self-service portal DB authentication model is undeclared — PKG_LEAVE is called by the portal but the portal's DB connection credentials, schema access grants, and session context setup are not in any source file; if the portal connects as the HRMS application user (full schema owner), it has unrestricted INSERT/UPDATE/DELETE on all HRMS tables | Security Vulnerability | Medium | PKG_LEAVE.pks header: "Called by: self-service portal" with no authentication specification; no grant scripts in repository; no dedicated read-limited DB user defined anywhere in source | Create a dedicated Oracle DB schema user (HRMS_PORTAL_APP) with EXECUTE grants only on specific PKG_LEAVE procedures; revoke any direct table grants; portal must obtain a session_id via PKG_SECURITY and pass it on every PKG_LEAVE call |

---

### Low (6 items)

| ID | Risk / Debt Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-37 | Audit log uses single table for all log types — ERROR_LOG, INFO_LOG, and DML audit mixed; single purge policy | Architecture Anti-pattern | Low | PKG_COMMON.pkb: TABLE_NAME='ERROR_LOG'/'INFO_LOG' in same AUDIT_LOG as DML events | Separate ERROR_LOG and INFO_LOG into dedicated tables; independent retention policies |
| TD-40 | EEO report gender codes: 'O' category exists but no constraint enforces valid values; arbitrary values distort EEO reporting | Configuration Risk | Low | PKG_REPORTING.pkb: explicit count for 'M','F','O',NULL; no CHECK constraint in DDL | Add CHECK constraint EMPLOYEES.GENDER IN ('M','F','O','N') or FK to GENDER_CODES lookup |
| TD-46 | EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER stored plaintext — combined with encrypted ACCOUNT_NUMBER_ENC constitutes full ACH credentials | Security Vulnerability | Low | 02_payroll_tables.sql: ROUTING_NUMBER VARCHAR2(20) NOT NULL — no encryption | Evaluate encrypting ROUTING_NUMBER alongside ACCOUNT_NUMBER_ENC |
| TD-52 | HRMS_VALIDATION_LIB.validate_salary_range comment says "cached" but code shows live DB query — stale comment misleads maintainers | Configuration Risk | Low | HRMS_VALIDATION_LIB.pll.sql: comment "hard-coded cache"; body: direct SELECT FROM JOB_GRADES | Remove stale comment; document actual live query behaviour |
| TD-53 | HRMS_LOGIN error message is generic for both authentication failure and EMP_ID lookup failure — prevents operational diagnosis | Operational Risk | Low | HRMS_LOGIN.xml: single WHEN OTHERS handler covers both PKG_SECURITY.authenticate and SELECT EMP_ID | Separate error handling by exception range; log failed logins to AUDIT_LOG from Forms layer |
| TD-57 | Pay element GL account coding scheme (5100/2100/2200) is undocumented in-schema — no constraint or comment; developer adding new pay element may assign incorrect GL account | Configuration Risk | Low | 01_reference_data.sql: GL_ACCOUNT_CODE follows numeric convention; no CHECK or COMMENT | Add GL_ACCOUNT_CODES reference table or COMMENT on GL_ACCOUNT_CODE column |

---

## OUTPUT 8 — Operational Architecture Assessment

### CI/CD Pipeline Maturity

> This system has **no CI/CD pipeline** of any kind. No `.github/workflows/`, no `Jenkinsfile`, no `.gitlab-ci.yml`, no `azure-pipelines.yml`, no `.circleci/`, no `bitbucket-pipelines.yml`, and no pipeline shell scripts were found anywhere in the repository.

| Capability | Present? | Evidence | Runs On | Gap Severity |
|---|---|---|---|---|
| Build | Absent | No build pipeline found. Oracle Forms .fmb → .fmx compilation and PL/SQL package compilation are manual | Manual only | Critical |
| Unit Tests | Absent | No test files found in repository. No test framework dependency in any manifest | Manual only | Critical |
| Integration Tests | Absent | No test automation found | Manual only | Critical |
| Code Coverage Gate | Absent | No coverage tooling found | Manual only | High |
| SAST (Static Security) | Absent | No SonarQube, Semgrep, CodeQL, or equivalent configuration found | Manual only | Critical |
| Dependency Scan | Absent | No Snyk, OWASP dependency-check, or equivalent | Manual only | High |
| Container / Image Scan | Absent | No containers exist in this system; not applicable | N/A | — |
| Secret / Credential Scan | Absent | No TruffleHog, gitleaks, detect-secrets, or equivalent; the hard-coded AES key (TD-01) and cleartext FTP credentials (TD-10) would have been flagged immediately by any secret scanner | Manual only | Critical — absence of secret scanning directly enabled the hard-coded key situation |
| Infrastructure Scan (IaC) | Absent | No IaC files exist; not applicable | N/A — no IaC | — |
| Lint / Code Quality | Absent | No automated linting; no PL/SQL static analysis tooling configured | Manual only | Medium |
| Automated Deploy | Absent | All deployment is manual: Oracle Forms Builder compiles .fmx; DBA applies SQL*Plus scripts | Manual only | Critical |
| Smoke / Health Check Post-Deploy | Absent | No post-deploy verification | Manual only | High |
| Auto Rollback | Absent | No rollback mechanism; reverting a schema change requires manual DBA intervention | Manual only | Critical |
| Manual Approval Gate | Absent | No pipeline to gate; deployment is 100% manual with no documented approval process | Manual only | Medium |
| Release / Versioning Automation | Absent | APP_VERSION=4.2.0 is a static SYSTEM_PARAMETERS row; no semantic-release or git tagging | Manual only | Low |
| Notification (pipeline failure) | Absent | No pipeline to notify about | N/A | — |

**Summary: 0 of 14 capabilities present. 6 Critical gaps (no builds, tests, SAST, secret scanning, automated deploy, rollback).**

---

### Observability Coverage

| Concern | Component | Present? | Tool / Library | Gap? |
|---|---|---|---|---|
| Structured Logging | All packages | Absent | DBMS_OUTPUT (debug fallback only); PKG_COMMON.log_error writes free-text to AUDIT_LOG | GAP — no structured log format; no JSON fields; no severity levels beyond ERROR/INFO; no correlation ID; DBMS_OUTPUT is invisible in production |
| Distributed Tracing | All packages | Absent | None — no OpenTelemetry, Jaeger, Zipkin, or Oracle trace integration | GAP — monolith with no service boundaries; no request correlation ID within a single session |
| Metrics Export | All packages | Absent | None — no Prometheus, Micrometer, Datadog, or Oracle metrics export | GAP — no application-level metrics; no throughput counters; no error rate metrics |
| Correlation ID Propagation | All packages | Absent | SYS_CONTEXT('USERENV','SESSIONID') is captured in AUDIT_LOG but is the Oracle DB session ID, not a business correlation ID; does not propagate through notification or integration file paths | GAP — no end-to-end correlation across payroll run → GL feed → ADP feed chain |
| Health / Readiness Endpoints | All forms | Absent (N/A) | Thick-client Oracle Forms architecture has no HTTP endpoints | N/A for Forms architecture |
| Alerting Rules | Monitoring system | Absent | No Alertmanager, CloudWatch, or PagerDuty configuration in repository | GAP — no operational alerting; payroll errors, SMTP failures, or UTL_FILE write failures are logged to AUDIT_LOG but no alert is raised |
| Application Performance Monitoring | All packages | Absent | No APM agent; known performance issue (VW_ORG_HIERARCHY degradation at >500 employees) is documented in source but not instrumented | GAP — no response time visibility; no slow query alerting |
| Audit Trail (business operations) | All tables | Present | AUDIT_LOG table: captures all DML via PKG_AUDIT.log_action (PRAGMA AUTONOMOUS_TRANSACTION); captures IP_ADDRESS and SESSIONID; 365-day default retention; TRG_SALARY_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_DEPARTMENT_AUDIT | Partial — DML audit exists but 194+ triggers not in source set; TRG_DEPARTMENT_AUDIT has no field-value capture (TD-36); TRG_EMP_BEFORE_UPDATE is broken (TD-41); IP_ADDRESS captures WebLogic proxy IP not client IP (TD-63) **[EDGE-CASE-FOUND]** |

---

### Deployment Safety

| Practice | Present? | Evidence | Risk If Absent |
|---|---|---|---|
| Graceful Shutdown | No | No graceful shutdown logic found; Oracle Forms sessions disconnect abruptly if WebLogic is stopped | Request loss; in-flight payroll calculations may leave PAYROLL_RUNS in CALCULATING state on unplanned WebLogic restart |
| Readiness Probe | No | No Kubernetes or load-balancer health check declared; thick-client architecture on bare WebLogic | Traffic loss or connection error if Forms AS is starting up |
| Liveness Probe | No | Same — no container runtime; no health check endpoint | Hung WebLogic processes not automatically restarted; requires manual DBA intervention |
| Blue-Green / Canary Deploy | No | Not found in any source or configuration; all deployment is manual | 100% traffic impact on every deployment; no safe rollback path for failed Forms .fmx deployments |
| Feature Flags | No | No feature flag integration found | No ability to decouple deployment from feature activation |
| Schema Migration Tooling | No | No Flyway, Liquibase, or equivalent; schema changes applied via ad-hoc SQL*Plus scripts | No migration history; no repeatable schema deployment; no drift detection between environments |
| Connection Pool Configuration | Unknown | WebLogic JDBC datasource manages the Oracle connection pool; pool settings not present in any file in this repository | Risk of unbounded connections or starvation under load — current settings entirely unknown |

---

### Disaster Recovery Posture

| Item | Declared? | Detail | Source |
|---|---|---|---|
| Database backup configuration | Unknown | No RMAN backup scripts, no Data Guard configuration, no backup policy found | NOT FOUND |
| Multi-region / multi-AZ config | No | Single on-premises deployment; no cloud; no geographic redundancy declared | README.md (on-premises deployment confirmed); no IaC |
| Database replication | Unknown | No Oracle Data Guard, GoldenGate, or Streams configuration found | NOT FOUND |
| RTO / RPO declarations | Unknown | No SLA, RTO, or RPO values found in any source file, comment, or documentation | NOT FOUND |
| Backup of Oracle Directory files | Unknown | PAYROLL_OUTPUT, GL_FEED_OUT, BENEFITS_FEED_OUT contain payroll and financial data; OS-level backup policy is unknown | NOT FOUND |
| Encryption key backup / escrow | No | AES-256 key is a hard-coded string in PKG_SECURITY.pkb; if the source code is lost, encrypted SSNs and bank account numbers cannot be decrypted | PKG_SECURITY.pkb: c_encryption_key literal — key is in source control but this is itself a security risk (TD-01) |

---

## Validation Queue (Unresolved Items)

| ID | Item | Reason for Uncertainty |
|---|---|---|
| LOW-001 | PKG_DEPARTMENT — declared in README; not in provided source set | Missing source file |
| LOW-002 | HRMS_REPORTS, HRMS_ADMIN, HRMS_DEPARTMENT forms — referenced via OPEN_FORM; not in provided source set | Missing source files |
| LOW-003 | Oracle Reports 8× .rdf files — declared in README; not in provided source set | Missing source files |
| LOW-004 | 194+ database triggers — README states 200+; only 6 provided; pattern coverage of the remaining 194 triggers is entirely unknown | Missing source files |
| LOW-005 | 9 missing views — README states 15; only 6 provided; the 9 unseen views may contain additional business rules or discrepancies | Missing source files |
| LOW-007 | RPT_* denormalized reporting tables — referenced in PKG_REPORTING.refresh_reporting_tables (stub); no DDL provided | Missing DDL |
| LOW-008 | DBMS_SCHEDULER job DDL — two jobs referenced in comments (process_queue every 5 min; run_monthly_accrual monthly); no CREATE_JOB scripts in repository | Missing DDL |
| LOW-009 | FTP credential key names in SYSTEM_PARAMETERS — referenced in PKG_INTEGRATION.pks header; exact PARAM_CODE values not visible in any provided source | Incomplete source |
| LOW-010 | Self-service portal — referenced in PKG_LEAVE.pks; no source, URL, technology stack, or configuration in this repository; its security posture and access model are unknown | Missing source |
| LOW-011 | USER_CREDENTIALS table — referenced in PKG_SECURITY.change_password and authenticate; DDL not provided; column structure (password hash column name, salt column if any, account lockout columns) unknown | Missing DDL |
| LOW-012 | SEQ_EMP_NUMBER race condition — sequence defined; PKG_EMPLOYEE.generate_emp_number uses MAX()+1 instead of .NEXTVAL; concurrent insert behaviour under production load not deterministically characterised from static analysis alone | Known bug; no runtime data |
| LOW-013 | Oracle Enterprise Manager or equivalent DBA monitoring — implied by production Oracle 19c deployment; no OEM configuration, alert thresholds, or dashboard definitions in this repository | No observability-as-code found |
| LOW-NFR-05 | DBMS_SCHEDULER 5-minute poll interval — declared in PKG_NOTIFICATION.pks header comment only; no CREATE_JOB DDL confirms the interval is actually configured | Comment-only evidence |
| LOW-NFR-44 | RPT_* reporting table refresh "nightly" — declared in PKG_REPORTING.pks header comment; refresh_reporting_tables body is a stub; nightly scheduling is not confirmed by any DDL or scheduler script | Comment-only evidence; stub body |

---

## Agent 1 Discrepancy Log

| ID | What Agent 1 Said | What Implementation Showed | Resolution |
|---|---|---|---|
| DISC-001 | Hire date future limit: 90 days in HRMS_EMPLOYEE WHEN-VALIDATE-ITEM; 180 days in TRG_EMP_BEFORE_INSERT; flagged as unresolved conflict | Both values are correct and intentional: Forms layer enforces 90-day limit for all UI users; DB trigger enforces 180-day backstop for non-Forms access (direct SQL, bulk loads, APIs). Layered validation — not a contradiction. | RESOLVED — No runtime conflict. Effective business rule for users: 90 days. Final safety net for all other insert paths: 180 days. |
| DISC-002 | EMPLOYEE_HISTORY column layout: DDL has EFFECTIVE_DATE + typed OLD_/NEW_ columns; TRG_EMP_BEFORE_UPDATE inserts into CHANGE_DATE, OLD_VALUE, NEW_VALUE (VARCHAR2 flat strings); flagged as "one of them would fail at runtime" | DDL is authoritative. CHANGE_DATE, OLD_VALUE, NEW_VALUE do not exist in the DDL. TRG_EMP_BEFORE_UPDATE will throw ORA-00904 on every EMPLOYEES UPDATE until the trigger is rewritten. This is a Critical runtime defect (TD-41). | RESOLVED — DDL is authoritative. Trigger must be rewritten to use EFFECTIVE_DATE + typed OLD_DEPT_ID/NEW_DEPT_ID/etc. columns. |
| DISC-003 | VW_LEAVE_SUMMARY AVAILABLE formula omits PENDING deduction; LEAVE_BALANCES virtual column includes PENDING; flagged as "which is authoritative" | LEAVE_BALANCES virtual column (GENERATED ALWAYS AS) is authoritative. VW_LEAVE_SUMMARY is incorrect: it overstates available leave by exactly the PENDING amount for any employee with submitted-but-unapproved requests. | RESOLVED — Virtual column is authoritative. VW_LEAVE_SUMMARY must be corrected (TD-42). |

---

## Document Totals

| Counter | Pass 1 | Pass 2 Added | Grand Total |
|---|---|---|---|
| Architecture Patterns | AP-41 – AP-57 (17) | AP-58 – AP-65 (8) | **65** |
| NFR entries | NFR-01 – NFR-87 (87) | NFR-88 – NFR-116 (29) | **116** |
| Technical Debt entries | TD-01 – TD-57 (57) | TD-58 – TD-81 (24) | **81** |
| Critical TD | 8 | 0 | **8** |
| High TD | 21 | 11 | **32** |
| Medium TD | 22 | 14 | **36** |
| Low TD | 6 | 0 | **6** |

**Highest-priority action items (unchanged from Pass 1, reinforced by Pass 2):**

1. **TD-03** — authenticate() issues valid session tokens without password verification. Any username + any password = authenticated session.
2. **TD-01** — AES-256 key is in source code. All SSNs and bank account numbers are trivially decryptable by any developer.
3. **TD-63** `[EDGE-CASE-FOUND]` — AUDIT_LOG.IP_ADDRESS captures the WebLogic server IP for every user. The forensic audit trail has zero evidentiary value for user attribution.
4. **TD-64** `[EDGE-CASE-FOUND]` — Terminated employees are not deprovisioned from Active Directory. Post-termination access is uncontrolled.
5. **TD-41** — TRG_EMP_BEFORE_UPDATE throws ORA-00904 on every EMPLOYEES UPDATE. All employee lifecycle operations that pass through the trigger are broken in production.
6. **TD-59** `[EDGE-CASE-FOUND]` — 28 NOCACHE sequences will produce SQ enqueue lock contention at payroll run scale. Likely the dominant payroll performance bottleneck beyond the row-by-row cursor.


---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_REPORTING
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here's a summary of everything extracted and recorded:

---

## What was added to `results/Technology_Analysis/TA_Deep_Analyst_Edge.md`

### 8 Procedures fully catalogued

All procedures with full signatures, purpose, and return types: `headcount_report`, `compensation_summary`, `turnover_report`, `new_hires_report`, `leave_utilization_report`, `payroll_summary_report`, `eeo_compliance_report`, `refresh_reporting_tables`.

### 10 Tables read (read-only — no DML anywhere in the package)

EMPLOYEES, DEPARTMENTS, LOCATIONS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS, LEAVE_BALANCES, LEAVE_TYPES, PAYROLL_DETAILS, PAYROLL_RUNS — with exact columns used per procedure.

### 12 Business rules extracted (BR-RPT-01 – BR-RPT-12)

Notable rules:
- **BR-RPT-01** — three-part active employee check (status + hire + termination date)
- **BR-RPT-04** — turnover denominator uses ever-hired base, not SHRM average headcount
- **BR-RPT-05** — NULL `TERMINATION_REASON` silently counts as involuntary
- **BR-RPT-08** — Federal/State/SS/Medicare tax lines identified by hard-coded ELEMENT_IDs 100–103
- **BR-RPT-10** — EEO active filter is weaker (single-field) vs headcount's three-part filter
- **BR-RPT-12** — `refresh_reporting_tables` is a confirmed stub with no RPT_* logic

### 6 New NFRs (NFR-91 – NFR-96)

### 5 New Technical Debt items (TD-82 – TD-86)

| ID | Severity | Finding |
|---|---|---|
| TD-82 | **High** | Hard-coded ELEMENT_IDs 100–103 in payroll tax summary — silent miscalculation if IDs shift |
| TD-83 | **Medium** | EEO filter weaker than headcount filter — compliance-reportable reconciliation gap |
| TD-84 | **Medium** | NULL `TERMINATION_REASON` silently inflates involuntary turnover count |
| TD-85 | **Medium** | No unique constraint on active salary record — duplicate ACTIVE_FLAG='Y' rows corrupt compensation averages |
| TD-86 | **Low** | Non-standard turnover denominator undocumented — systematically understates vs SHRM formula |

### 2 Validation queue items closed

LOW-007 (RPT_* DDL) and LOW-NFR-44 (nightly refresh) are both **confirmed unimplemented** — the stub body is now the authoritative evidence.

---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_VALIDATION
*Added by cross-track validator — source recovered from file_cache.json (plsql/packages/PKG_VALIDATION.pkb). This data was present in the source cache but not analysed in this document.*

---

### Package Overview

| Attribute | Value |
|---|---|
| Package | `HRMS.PKG_VALIDATION` |
| Type | Centralized validation utility — pure functions, no DML |
| Source file | `plsql/packages/PKG_VALIDATION.pkb` (body); `.pks` (spec) |
| Called by | All Oracle Forms (`WHEN-VALIDATE-ITEM` triggers), `PKG_EMPLOYEE`, `PKG_PAYROLL` (per `.pks` header) |
| Dependencies | `JOB_GRADES` table (direct SELECT), `HOLIDAYS` table (direct SELECT), `PKG_COMMON` (delegates email and phone validation) |
| Side effects | None — all functions are read-only |

---

### Function Catalogue (8 functions)

#### 1. `validate_date_range(p_start_date DATE, p_end_date DATE) RETURN BOOLEAN`

| Attribute | Detail |
|---|---|
| Purpose | Confirms a date range is non-null and end ≥ start |
| NULL handling | Returns `FALSE` if either input is NULL (not an exception — callers must treat FALSE as "invalid") |
| Core rule | `RETURN p_end_date >= p_start_date` — same-day ranges (start = end) are **valid** |
| Callers | Form date-range fields (e.g. pay period, leave request, review cycle dates); any package validating overlapping periods |

---

#### 2. `validate_salary_for_grade(p_salary NUMBER, p_grade_id NUMBER) RETURN VARCHAR2`

| Attribute | Detail |
|---|---|
| Purpose | Checks whether a salary falls within the JOB_GRADES band for a given grade |
| Return contract | `NULL` = valid; non-null string = user-facing error message |
| NULL handling | Both parameters required — returns `'Salary and grade are required'` if either is NULL |
| Table accessed | `JOB_GRADES` — reads `MIN_SALARY`, `MAX_SALARY`, `GRADE_NAME` for `GRADE_ID = p_grade_id` |
| Below-minimum message | `'Salary $NNN,NNN.NN is below minimum for grade <GRADE_NAME> ($NNN,NNN.NN)'` |
| Above-maximum message | `'Salary $NNN,NNN.NN exceeds maximum for grade <GRADE_NAME> ($NNN,NNN.NN)'` |
| Number format | `FM$999,999,990.00` — suppresses leading spaces; always shows two decimal places |
| Exception | `NO_DATA_FOUND` → returns `'Invalid grade ID: <n>'` |
| Architecture note | This is the **only** function in the package that performs a database query. All other functions are either pure logic or delegate to `PKG_COMMON`. |
| Related debt | **TD-74** — `PKG_EMPLOYEE.create_employee` only calls the equivalent salary-range check in debug mode; `HRMS_VALIDATION_LIB.validate_salary_range` issues a soft `MESSAGE` warning, not a blocking error. This function provides the correct blocking logic but is not consistently invoked at all entry points. |

---

#### 3. `validate_email_format(p_email VARCHAR2) RETURN BOOLEAN`

| Attribute | Detail |
|---|---|
| Purpose | Validates email address format |
| Implementation | Delegates entirely to `PKG_COMMON.is_valid_email(p_email)` — no local logic |
| Known defect | `HRMS_VALIDATION_LIB.pll.sql` contains a **separate, divergent** email validation that rejects subdomain addresses (e.g. `user@mail.company.com`). This function delegates to `PKG_COMMON` which is presumed correct. The two validation paths produce different results for the same input. (Referenced in TA_Stack_Scout.md, Component Map row 8.) |

---

#### 4. `validate_phone_format(p_phone VARCHAR2) RETURN BOOLEAN`

| Attribute | Detail |
|---|---|
| Purpose | Validates phone number format |
| Implementation | Delegates entirely to `PKG_COMMON.is_valid_phone(p_phone)` — no local logic |
| Note | Phone format rules are defined once in `PKG_COMMON`; this function is a named pass-through so Forms triggers can call a consistently-named validation entry point |

---

#### 5. `validate_emp_number_format(p_emp_number VARCHAR2) RETURN BOOLEAN`

| Attribute | Detail |
|---|---|
| Purpose | Enforces the `EMP-NNNNNN` employee number format |
| Implementation | `REGEXP_LIKE(p_emp_number, '^EMP-\d{6}$')` — pure regex, no DB access |
| Format rule | Prefix `EMP-` followed by **exactly 6 digits** — no more, no fewer |
| NULL handling | `REGEXP_LIKE` with a NULL input returns NULL (falsy) — not an explicit guard; callers should pre-validate for NULL |
| Related item | `PKG_EMPLOYEE.generate_emp_number` uses `MAX(EMP_NUMBER)+1` (no `SELECT FOR UPDATE`) which is a race condition (TD-13 / TA_Stack_Scout race condition note). This regex is the format gate — it would catch a malformed number but cannot prevent a duplicate one. |

---

#### 6. `is_future_date(p_date DATE) RETURN BOOLEAN`

| Attribute | Detail |
|---|---|
| Purpose | Returns TRUE if the given date is strictly in the future (after today) |
| Implementation | `RETURN TRUNC(p_date) > TRUNC(SYSDATE)` |
| Boundary | Today's date returns **FALSE** (not a future date) — callers that need "today or later" must use a different check |
| NULL handling | No explicit NULL guard — `TRUNC(NULL) > TRUNC(SYSDATE)` evaluates to NULL (falsy); calling code must handle this |

---

#### 7. `is_business_day(p_date DATE, p_location_code VARCHAR2 DEFAULT NULL) RETURN BOOLEAN`

| Attribute | Detail |
|---|---|
| Purpose | Returns TRUE if the given date is a working day (not a weekend, not a public holiday) |
| Weekend check | `TO_CHAR(p_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN')` — explicitly uses `AMERICAN` locale to ensure `SAT`/`SUN` string constants are reliable regardless of DB NLS settings |
| Holiday lookup | `SELECT COUNT(*) FROM HOLIDAYS WHERE HOLIDAY_DATE = TRUNC(p_date) AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)` |
| Location scoping | `p_location_code DEFAULT NULL` — when NULL, only global holidays (`LOCATION_CODE IS NULL`) apply; when provided, both global holidays and location-specific holidays block the date |
| Holiday seed data | All 10 seed rows in HOLIDAYS have `IS_GLOBAL='Y'`; no location-specific holidays are currently seeded |
| Tables accessed | `HOLIDAYS` — reads `HOLIDAY_DATE`, `ACTIVE_FLAG`, `LOCATION_CODE` |
| NULL handling | No explicit guard on `p_date` — `TRUNC(NULL)` would match no HOLIDAYS rows, and `TO_CHAR(NULL,'DY')` returns NULL (not `SAT`/`SUN`), so a NULL input returns TRUE (incorrectly treated as a business day) |
| Callers | Expected callers include payroll pay-date calculation (PAY_PERIODS.PAY_DATE moved to Friday if weekend — see TA_Stack_Scout table registry) and leave request business-day counting |

---

#### 8. `validate_required_fields(p_table_name VARCHAR2, p_record_id NUMBER) RETURN VARCHAR2`

| Attribute | Detail |
|---|---|
| Purpose | Checks that mandatory fields are populated for a given record |
| Return contract | `NULL` = all required fields present; non-null = first missing field name as a user-facing message |
| Implementation scope | **Only `EMPLOYEES` is implemented.** The function has an `IF p_table_name = 'EMPLOYEES' THEN` branch; all other table names fall through and return `NULL` (silently treated as valid) |
| EMPLOYEES checks | `FIRST_NAME`, `LAST_NAME`, `HIRE_DATE`, `DEPT_ID`, `JOB_ID` — returns the first NULL field found |
| Exception | `NO_DATA_FOUND` → returns `'Record not found'` |
| Architecture gap | The package spec comment states "Business rule validation shared between Forms triggers and PL/SQL packages" — the intent is a generic required-field gate for all tables. Only `EMPLOYEES` is wired up. Any call with `p_table_name != 'EMPLOYEES'` silently passes validation regardless of actual field content. |
| Technical debt | See **TD-VAL-01** below. |

---

### Business Rules Extracted (BR-VAL-01 – BR-VAL-09)

| ID | Rule | Source Location |
|---|---|---|
| BR-VAL-01 | A date range is valid if and only if both dates are non-null AND `end_date >= start_date`. Same-day ranges are valid. | `validate_date_range` |
| BR-VAL-02 | Employee salary must be ≥ `JOB_GRADES.MIN_SALARY` and ≤ `JOB_GRADES.MAX_SALARY` for the assigned grade. | `validate_salary_for_grade` |
| BR-VAL-03 | A null or unrecognised `GRADE_ID` is a validation error (not a silent pass). | `validate_salary_for_grade` — `NO_DATA_FOUND` handler |
| BR-VAL-04 | Employee numbers must match the pattern `EMP-` followed by exactly 6 digits (`^EMP-\d{6}$`). | `validate_emp_number_format` |
| BR-VAL-05 | A date is a future date if and only if `TRUNC(date) > TRUNC(SYSDATE)`. Today is not a future date. | `is_future_date` |
| BR-VAL-06 | Saturday and Sunday are never business days, regardless of location or holiday calendar. | `is_business_day` — weekend check |
| BR-VAL-07 | A date matching any `HOLIDAYS` row with `ACTIVE_FLAG='Y'` is not a business day. Global holidays (`LOCATION_CODE IS NULL`) apply to all employees; location-specific holidays apply only when `p_location_code` matches. | `is_business_day` — holiday query |
| BR-VAL-08 | For `EMPLOYEES` records, `FIRST_NAME`, `LAST_NAME`, `HIRE_DATE`, `DEPT_ID`, and `JOB_ID` are required fields. | `validate_required_fields` |
| BR-VAL-09 | Email format validation and phone format validation are governed by `PKG_COMMON` — `PKG_VALIDATION` has no independent rules for these. | `validate_email_format`, `validate_phone_format` |

---

### Tables Accessed by PKG_VALIDATION

| Table | Access Type | Function | Columns Read |
|---|---|---|---|
| `JOB_GRADES` | SELECT (single row) | `validate_salary_for_grade` | `MIN_SALARY`, `MAX_SALARY`, `GRADE_NAME` |
| `HOLIDAYS` | SELECT COUNT(*) | `is_business_day` | `HOLIDAY_DATE`, `ACTIVE_FLAG`, `LOCATION_CODE` |
| `EMPLOYEES` | SELECT * (single row via `%ROWTYPE`) | `validate_required_fields` | `FIRST_NAME`, `LAST_NAME`, `HIRE_DATE`, `DEPT_ID`, `JOB_ID` |

No INSERT, UPDATE, or DELETE operations anywhere in this package.

---

### New Technical Debt Items (TD-VAL-01 – TD-VAL-04)

| ID | Risk / Debt Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-VAL-01 | `validate_required_fields` only implements `EMPLOYEES` — all other table names silently return NULL (valid) regardless of actual field content. The function signature promises generic table validation but delivers only one table. Any caller passing `p_table_name = 'LEAVE_REQUESTS'` or any other table will never receive a validation error. | Architecture Anti-pattern | **Medium** | `PKG_VALIDATION.pkb`: `IF p_table_name = 'EMPLOYEES' THEN ... END IF; RETURN NULL;` — no ELSE, no other branch | Either restrict the function contract to `EMPLOYEES` explicitly (rename to `validate_employee_required_fields`) or implement the remaining tables. The current gap means the function gives false assurance of coverage. |
| TD-VAL-02 | `is_business_day` has no NULL guard on `p_date` — a NULL input is silently treated as a business day (returns TRUE). Any caller that passes an unvalidated date (e.g. a NULL `TERMINATION_DATE`) will receive an incorrect TRUE result without error. | Data Quality | **Medium** | `PKG_VALIDATION.pkb`: no `IF p_date IS NULL` check before the `TO_CHAR` and `SELECT COUNT(*)` calls. `TRUNC(NULL)` never matches a HOLIDAYS row; weekend check on NULL returns NULL (falsy), so the function falls through to `RETURN v_holiday_count = 0` which evaluates as `0 = 0 = TRUE`. | Add `IF p_date IS NULL THEN RETURN FALSE; END IF;` as the first statement of `is_business_day`. |
| TD-VAL-03 | `validate_emp_number_format` has no NULL guard — `REGEXP_LIKE(NULL, '^EMP-\d{6}$')` returns NULL (neither TRUE nor FALSE), which Oracle treats as falsy in a BOOLEAN context but may behave unexpectedly if callers use it in a PL/SQL `IF` or pass the result to a VARCHAR2 column. | Data Quality | **Low** | `PKG_VALIDATION.pkb`: `RETURN REGEXP_LIKE(p_emp_number, '^EMP-\d{6}$');` — no prior NULL check | Add `IF p_emp_number IS NULL THEN RETURN FALSE; END IF;` before the `REGEXP_LIKE` call. |
| TD-VAL-04 | `validate_salary_for_grade` error messages embed live salary and grade data in user-visible strings using `TO_CHAR(p_salary, 'FM$999,999,990.00')`. If a salary value exceeds 9 digits before the decimal point (> $999,999,990), `TO_CHAR` will return a string of `#` characters, producing an unintelligible error message with no indication of the actual salary. While an HRMS salary exceeding ~$1B is unlikely, the format mask provides no safety net. | Operational Risk | **Low** | `PKG_VALIDATION.pkb`: `'FM$999,999,990.00'` format mask applied to `p_salary`; Oracle returns `#####` on overflow without raising an exception | Widen format mask to `FM$9,999,999,990.00` or add a `NVL(TO_CHAR(p_salary,'FM$999,999,990.00'), TO_CHAR(p_salary))` fallback. |

---

### New NFR Items (NFR-VAL-01 – NFR-VAL-03)

| ID | NFR | Category | Evidence |
|---|---|---|---|
| NFR-VAL-01 | `is_business_day` performs a live `SELECT COUNT(*)` against `HOLIDAYS` on every invocation — no caching. In a high-volume payroll run iterating 200 employees, this produces 200+ identical queries for the same pay date. | Performance | `PKG_VALIDATION.pkb`: `is_business_day` body; no package-level cache variable |
| NFR-VAL-02 | `validate_salary_for_grade` performs a live `SELECT` against `JOB_GRADES` on every call. `JOB_GRADES` is a low-cardinality reference table (10 rows by seed data) that changes infrequently. Repeated invocations during bulk operations repeat the same lookup without caching. | Performance | `PKG_VALIDATION.pkb`: `SELECT MIN_SALARY, MAX_SALARY, GRADE_NAME FROM JOB_GRADES WHERE GRADE_ID = p_grade_id` — no package-state cache |
| NFR-VAL-03 | Email and phone validation are entirely opaque from `PKG_VALIDATION`'s perspective — the validation contract is whatever `PKG_COMMON.is_valid_email` and `PKG_COMMON.is_valid_phone` implement. A change to `PKG_COMMON`'s validation logic silently changes `PKG_VALIDATION`'s behaviour with no indication in `PKG_VALIDATION` itself. | Maintainability | `PKG_VALIDATION.pkb`: `RETURN PKG_COMMON.is_valid_email(p_email)` / `RETURN PKG_COMMON.is_valid_phone(p_phone)` — pure pass-through with no local rule documentation |

---

### Cross-Reference: Email Validation Inconsistency

The email validation discrepancy between `PKG_VALIDATION`/`PKG_COMMON` and `HRMS_VALIDATION_LIB` is documented in TA_Stack_Scout.md (Component Map, row 8). To be precise:

- **`PKG_VALIDATION.validate_email_format`** → delegates to **`PKG_COMMON.is_valid_email`** (implementation not in this scan set, assumed correct)
- **`HRMS_VALIDATION_LIB.pll.sql`** → contains its own email regex that **rejects subdomains** (e.g. `user@mail.company.com` fails)
- **Result**: The same email address passes `PKG_VALIDATION` but fails `HRMS_VALIDATION_LIB`. Since `HRMS_VALIDATION_LIB` is attached to the Oracle Forms `WHEN-VALIDATE-ITEM` trigger, a valid corporate email (with a subdomain) can be rejected at the UI layer but would be accepted by any non-Forms caller (direct PL/SQL, API, bulk load). This is an existing finding; it is reproduced here for completeness in the PKG_VALIDATION context.

---

### Document Totals Update

| Counter | Prior Total | Added This Supplement | New Grand Total |
|---|---|---|---|
| Business rules (BR-VAL) | — | 9 | +9 |
| Technical Debt entries | **86** (TD-01–TD-86) | 4 (TD-VAL-01–TD-VAL-04) | **90** |
| NFR entries | **116** (NFR-01–NFR-116) | 3 (NFR-VAL-01–NFR-VAL-03) | **119** |

---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_INTEGRATION.get_integration_status
*Added from recovered source — plsql/packages/PKG_INTEGRATION.pkb (file_cache.json). This function was present in the source cache but not previously analysed in this document.*

---

### Function Overview

| Attribute | Value |
|---|---|
| Package | `HRMS.PKG_INTEGRATION` |
| Function | `get_integration_status` |
| Source file | `plsql/packages/PKG_INTEGRATION.pkb` (body); `.pks` (spec not in scan set) |
| Return type | `VARCHAR2` |
| Parameters | `p_integration_name IN VARCHAR2` |
| Purpose | Retrieve the operational status of a named external integration from `SYSTEM_PARAMETERS` |
| Side effects | None — read-only; delegates entirely to `PKG_COMMON.get_param` |
| Called by | Not explicitly referenced in any provided source file; intended callers are integration orchestrators or status-check routines that gate batch operations on integration availability |

---

### Full Implementation

```sql
FUNCTION get_integration_status(
    p_integration_name IN VARCHAR2
) RETURN VARCHAR2 IS
BEGIN
    RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS');
END get_integration_status;
```

The function constructs a `SYSTEM_PARAMETERS` lookup key by appending the literal `'_STATUS'` to `p_integration_name` and delegates entirely to `PKG_COMMON.get_param`. There is no local logic, no DML, and no exception handling.

---

### Key Lookup Convention

| Call | Constructed PARAM_KEY | SYSTEM_PARAMETERS Seed Value |
|---|---|---|
| `get_integration_status('GL_FEED')` | `GL_FEED_STATUS` | `ACTIVE` |
| `get_integration_status('BENEFITS_FEED')` | `BENEFITS_FEED_STATUS` | `ACTIVE` |
| `get_integration_status('TIME_ATTENDANCE')` | `TIME_ATTENDANCE_STATUS` | Not in seed data — returns NULL or propagates exception |
| `get_integration_status('LDAP')` | `LDAP_STATUS` | Not in seed data — returns NULL or propagates exception |

The first argument `'INTEGRATION'` passed to `PKG_COMMON.get_param` is a category/group qualifier. Because `SYSTEM_PARAMETERS` uses a single-column `PARAM_KEY VARCHAR2(100) NOT NULL UNIQUE` design (no separate group column), it is unclear whether `PKG_COMMON.get_param` uses the first argument as a group filter, a namespace prefix, or ignores it entirely. The `PKG_COMMON.pkb` source is not in the scan set; this is tracked under LOW-009 and expanded in TD-INT-03 below.

---

### Business Rules Extracted (BR-INT-STATUS-01 – BR-INT-STATUS-02)

| ID | Rule | Source Location |
|---|---|---|
| BR-INT-STATUS-01 | The active/inactive state of every external integration is stored as a `SYSTEM_PARAMETERS` row with key `<INTEGRATION_NAME>_STATUS`. Callers consult this value to determine whether an integration is available before executing batch operations. | `PKG_INTEGRATION.pkb: get_integration_status`; `SYSTEM_PARAMETERS` seed data (GL_FEED_STATUS=ACTIVE, BENEFITS_FEED_STATUS=ACTIVE) |
| BR-INT-STATUS-02 | The `<NAME>_STATUS` naming convention is implicit and enforced only by code convention — no schema constraint, column comment, or CHECK constraint governs the pattern. A new integration that registers its status key under a different naming scheme (e.g. `GL_FEED_ENABLED`) will be invisible to `get_integration_status` and will always return NULL. | `PKG_INTEGRATION.pkb: p_integration_name \|\| '_STATUS'` — no format validation |

---

### Tables Accessed

| Table | Access Type | Columns | Via |
|---|---|---|---|
| `SYSTEM_PARAMETERS` | SELECT (delegated) | `PARAM_KEY`, `PARAM_VALUE` | `PKG_COMMON.get_param('INTEGRATION', <key>)` |

No direct DML. No other tables accessed.

---

### Technical Debt Items (TD-INT-01 – TD-INT-03)

| ID | Risk / Debt Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-INT-01 | `get_integration_status` has no NULL guard on `p_integration_name`. Passing NULL constructs the key `'_STATUS'`, which almost certainly does not exist in `SYSTEM_PARAMETERS`, causing either a silent NULL return or an unhandled exception from `PKG_COMMON.get_param`. Any caller that passes an uninitialised variable receives an unknown-status result with no diagnostic. | Data Quality | **Medium** | `PKG_INTEGRATION.pkb: p_integration_name \|\| '_STATUS'` — no prior NULL check | Add `IF p_integration_name IS NULL THEN RETURN NULL; END IF;` (or `RAISE_APPLICATION_ERROR(-20020, 'Integration name required')`) as the first statement of the function. |
| TD-INT-02 | No exception handling — if `PKG_COMMON.get_param` raises any exception (e.g. `NO_DATA_FOUND` for an unrecognised integration name), the exception propagates uncaught to the caller. There is no safe default return value (e.g. `'INACTIVE'` or `'UNKNOWN'`) for an unregistered integration. A caller gate-checking `'ACTIVE'` status would receive a fatal exception rather than a negative response. | Operational Risk | **Medium** | `PKG_INTEGRATION.pkb: get_integration_status` — no EXCEPTION block | Wrap the delegate in `BEGIN ... EXCEPTION WHEN OTHERS THEN RETURN 'UNKNOWN'; END;` or explicitly document that callers are required to handle exceptions raised by this function. |
| TD-INT-03 | The `'INTEGRATION'` category argument passed to `PKG_COMMON.get_param` is inconsistent with the `SYSTEM_PARAMETERS` DDL, which defines `PARAM_KEY` as the sole UNIQUE lookup column (no `PARAM_GROUP` column). If `get_param` ignores the first argument, it is dead documentation that misleads maintainers. If it uses it as a group filter, the `SYSTEM_PARAMETERS` schema does not enforce that grouping, so any row can be mis-categorised without error. | Architecture Anti-pattern | **Low** | `PKG_INTEGRATION.pkb: PKG_COMMON.get_param('INTEGRATION', ...)` vs. `SYSTEM_PARAMETERS` DDL: `PARAM_KEY VARCHAR2(100) NOT NULL UNIQUE` with no `PARAM_GROUP` column | Resolve by reading `PKG_COMMON.pkb` source (not in scan set). If the first argument is decorative, remove it. If it implies a grouping contract, add a `PARAM_GROUP VARCHAR2(50)` column to `SYSTEM_PARAMETERS` and a composite unique key `(PARAM_GROUP, PARAM_KEY)` to enforce it. |

---

### NFR Items (NFR-INT-01)

| ID | NFR | Category | Evidence |
|---|---|---|---|
| NFR-INT-01 | `get_integration_status` performs a live `SYSTEM_PARAMETERS` lookup on every invocation via `PKG_COMMON.get_param`. Integration status values are effectively static configuration flags that change only during administrative updates. Any caller that invokes this function repeatedly within a loop (e.g. checking `GL_FEED` status once per payroll-detail row during `generate_gl_journal`) generates unnecessary repeated identical queries against a near-static table. | Performance | `PKG_INTEGRATION.pkb: get_integration_status` — pure delegate with no package-level cache variable |

---

### Validation Queue Update

**LOW-009** (FTP credential key names in SYSTEM_PARAMETERS) is partially addressed: the `_STATUS` naming convention for integration state keys is now confirmed. Known status keys: `GL_FEED_STATUS`, `BENEFITS_FEED_STATUS`. FTP credential PARAM_KEY names remain unknown — no source file exposes them by name.

---

### Document Totals Update

| Counter | Prior Total | Added This Supplement | New Grand Total |
|---|---|---|---|
| Business rules (BR-INT-STATUS) | — | 2 | +2 |
| Technical Debt entries | **90** (TD-01 through TD-VAL-04) | 3 (TD-INT-01–TD-INT-03) | **93** |
| NFR entries | **119** (NFR-01 through NFR-VAL-03) | 1 (NFR-INT-01) | **120** |



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_VALIDATION
*Added by cross-track validator — this data was present in another track but missing from this document.*

The PKG_VALIDATION supplement has been appended to `results/Technology_Analysis/TA_Deep_Analyst.md`. Here's what was added:

---

### What was added

**Package overview** — confirms PKG_VALIDATION is a pure read-only utility called by all Oracle Forms `WHEN-VALIDATE-ITEM` triggers plus `PKG_EMPLOYEE`/`PKG_PAYROLL`. No DML anywhere.

**8 functions fully catalogued:**

| Function | Key detail |
|---|---|
| `validate_date_range` | Returns FALSE for NULLs; same-day ranges are valid |
| `validate_salary_for_grade` | Queries `JOB_GRADES`; returns null on pass, user-facing message on fail; NO_DATA_FOUND → "Invalid grade ID" |
| `validate_email_format` | Pure delegate to `PKG_COMMON.is_valid_email` — diverges from `HRMS_VALIDATION_LIB` |
| `validate_phone_format` | Pure delegate to `PKG_COMMON.is_valid_phone` |
| `validate_emp_number_format` | Regex `^EMP-\d{6}$` — no NULL guard |
| `is_future_date` | `TRUNC(date) > TRUNC(SYSDATE)` — today is NOT a future date |
| `is_business_day` | Weekend check (NLS-safe `AMERICAN` locale) + `HOLIDAYS` query; location-scoped; NULL date silently returns TRUE |
| `validate_required_fields` | Only `EMPLOYEES` implemented; all other tables silently pass |

**9 business rules** (BR-VAL-01–09), **3 tables accessed** (JOB_GRADES, HOLIDAYS, EMPLOYEES — read-only), **4 new TD items** (TD-VAL-01–04), **3 new NFRs** (NFR-VAL-01–03), and updated document totals (TD: 86→90, NFR: 116→119).



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_INTEGRATION.get_integration_status
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here's what was added to `results/Technology_Analysis/TA_Deep_Analyst.md`:

---

### What was recorded for `PKG_INTEGRATION.get_integration_status`

**Full implementation reproduced** — the function is a pure one-liner delegate: constructs key `p_integration_name || '_STATUS'` and calls `PKG_COMMON.get_param('INTEGRATION', key)`. No DML, no local logic, no exception handling.

**Key lookup table** — maps the four known/expected call patterns to their constructed `SYSTEM_PARAMETERS` keys:
- `GL_FEED` → `GL_FEED_STATUS` (seeded as `ACTIVE`)
- `BENEFITS_FEED` → `BENEFITS_FEED_STATUS` (seeded as `ACTIVE`)
- `TIME_ATTENDANCE` / `LDAP` → not seeded → returns NULL or throws

**2 business rules** (BR-INT-STATUS-01–02):
- The `<NAME>_STATUS` SYSTEM_PARAMETERS convention is the sole integration on/off gate
- The naming convention is enforced only by code — no schema constraint guards it

**1 table accessed**: `SYSTEM_PARAMETERS` (read-only, via `PKG_COMMON`)

**3 new TD items** (TD-INT-01–03):
| ID | Severity | Finding |
|---|---|---|
| TD-INT-01 | Medium | No NULL guard on `p_integration_name` — NULL input constructs key `'_STATUS'`, returns unknown result silently |
| TD-INT-02 | Medium | No exception handler — unregistered integration names propagate a fatal exception to the caller instead of returning a safe `'UNKNOWN'` default |
| TD-INT-03 | Low | `'INTEGRATION'` category arg to `get_param` is inconsistent with the `SYSTEM_PARAMETERS` DDL (no `PARAM_GROUP` column) — either dead code or an unenforced grouping contract |

**1 new NFR** (NFR-INT-01): Live `SYSTEM_PARAMETERS` lookup per call with no caching — a static config flag that shouldn't require repeated round-trips.

**Totals updated**: TD 90 → 93, NFR 119 → 120.

