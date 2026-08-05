Here is the second-pass synthesis. All 14 new TD entries and 5 new implied NFRs are findings the primary analysis missed or materially underreported.

---

## Second-Pass Synthesis — Missed and Underreported Findings

**Scope:** Findings not present in AP-01–AP-41, NFR-01–NFR-85, or TD-01–TD-48. Continue numbering from TD-49 / NFR-86.

---

### New Technical Debt & Risk Items

**Critical (3 new)**

| ID | Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-49 | **PKG_LEAVE has no PKG_SECURITY.has_permission gate — any direct DB caller bypasses authorization entirely.** `submit_leave_request`, `approve_leave_request`, and `cancel_leave_request` contain zero calls to `PKG_SECURITY.has_permission`. The Forms path enforces authorization through `HRMS_COMMON_LIB.check_user_permission` called in `WHEN-NEW-FORM-INSTANCE` only. The self-service portal (and any SQL*Plus or batch caller) can approve or cancel any employee's leave regardless of grade, role, or session validity. | Security Vulnerability | **Critical** | PKG_LEAVE.pkb: no PKG_SECURITY call in any state-changing procedure. PKG_SECURITY.has_permission used only from Forms triggers. Stage 7 interaction table records portal-to-PKG_LEAVE contract as "UNKNOWN." | Add `PKG_SECURITY.has_permission(p_module=>'LEAVE', p_action=>'APPROVE')` guard at the top of `approve_leave_request` and `cancel_leave_request`. All state-changing package procedures should validate the calling session against USER_SESSIONS before acting. |
| TD-57 | **Oracle FMW 12.2.1.4 Extended Support ended October 2025 — system is running unpatched, unsupported software as of August 2026.** The primary analysis recorded this as "Sustaining Engineering" which implies ongoing (limited) support. Extended Support ended October 2025: no new bug fixes, no new security patches, no new CPUs (Critical Patch Updates) will be issued for any zero-day found after that date. | EOL Technology | **Critical** | TA_Stack_Scout.md: Oracle WebLogic 12c "Standard support end Dec 2025." Oracle Forms 12.2.1.4 Extended Support matrix confirms October 2025. Current date: August 2026. The system has been running unsupported for 10 months. | Escalate to executive sponsor immediately. Begin Oracle Forms 14c evaluation or Oracle APEX migration. Engage Oracle Support for a Sustaining Support contract with documented risk acceptance. |
| TD-58 | **Oracle Forms 12c requires Java Plugin (NPAPI) for browser delivery — Chrome removed it 2015, Firefox 2017, Edge never supported it.** Users can only run Forms 12c in-browser via Internet Explorer 11 in Enterprise Mode (IE 11 itself end-of-life June 2022) or via Java Web Start (removed from Oracle JDK 11+). No client delivery mechanism is documented in the repository. If users are on modern browsers, the application is inaccessible without an undocumented workaround. | Operational Risk | **Critical** | Oracle Forms 12c documentation requires Java Plugin. NPAPI removal timeline is a well-established browser vendor decision. No browser delivery or thin-client config found in any source file. | Document the current client delivery mechanism. If IE 11 Enterprise Mode is in use, plan for its end. Evaluate Oracle Forms Standalone Launcher (`.jnlp`/JWS path) or migration to Oracle APEX as a strategic alternative. |

---

**High (7 new)**

| ID | Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-50 | **EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED uses the same hard-coded key as EMPLOYEES.SSN_ENCRYPTED.** Key rotation (the primary mitigation for TD-02) must re-encrypt both tables atomically. No rotation procedure exists. A partial rotation leaves dependent SSNs permanently unreadable under the new key. | Security Vulnerability | **High** | schema-catalogue.json: `EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED "AES-256 encrypted SSN; PII."` PKG_SECURITY.pkb: single constant `c_encryption_key` used for all encrypt/decrypt calls across both tables. | Create a key rotation stored procedure re-encrypting both tables in a single transaction. Store key in Oracle Wallet, not a PL/SQL constant. |
| TD-51 | **ADP benefits feed transmits dependent DATE_OF_BIRTH in plaintext to an external vendor.** DEP_DOB is written as a plain date string in the fixed-width 203-character record. No TLS or file-level encryption applied to the outbound file. DOB + name + relationship constitutes HIPAA PHI when transmitted to a benefits processor. | Security Vulnerability / Compliance | **High** | NFR-50: benefits feed is a plain fixed-width text file. No encryption or secure transfer protocol in PKG_INTEGRATION.pkb or any config file. Stage 7: outbound file boundary is "Unversioned, Undocumented." | Require ADP's SFTP endpoint with TLS 1.2+ for file delivery; or PGP-encrypt the file before drop. Add DPA/BAA review confirming ADP's handling obligations for dependent DOB. |
| TD-52 | **SALARY_BASIS='HOURLY' is a valid constraint value but PKG_PAYROLL always inserts 'ANNUAL' and has no hourly calculation path.** `PAYROLL_DETAILS.HOURS_WORKED` and `RATE` are provisioned but never populated. Any hourly employee is silently processed using `BASE_SALARY / pay_periods` with no error raised and no indication that hours data is absent. | Operational Risk | **High** | CHK_SAL_BASIS allows `'ANNUAL','HOURLY'`. PKG_PAYROLL.create_salary_record always inserts 'ANNUAL'. TD-29 (stub integration) was noted but the silent payroll miscalculation consequence was not captured. | Remove 'HOURLY' from CHK_SAL_BASIS to match actual code behaviour, or implement the hourly calculation path and unblock the Time & Attendance import. Either way, document the decision. |
| TD-53 | **PAY_PERIODS has no unique or exclusion constraint preventing two OPEN periods with overlapping date ranges.** `PKG_PAYROLL.get_current_period` uses `STATUS='OPEN' AND PERIOD_START_DATE <= SYSDATE AND PERIOD_END_DATE >= SYSDATE` — a single-row assumption. Two overlapping OPEN periods raises ORA-01422, crashing `calculate_payroll` mid-run. | Architecture Anti-pattern / Data Integrity | **High** | schema-catalogue.json: PAY_PERIODS constraints list only `CHK_PERIOD_STATUS`. No unique constraint on date range or frequency. | Add a function-based unique index or before-insert trigger that rejects an OPEN period whose dates overlap any existing OPEN period of the same frequency. |
| TD-55 | **EMPLOYEE_TAX_INFO has no effective-date historization — mid-year W-4 changes permanently destroy the prior tax election.** `UK_EMP_TAX_YEAR (EMP_ID, TAX_YEAR)` enforces one row per employee per year, preventing snapshot preservation. No EFFECTIVE_DATE column, no history table, no trigger on this table. For IRS payroll audit the system cannot demonstrate what withholding basis was used for pay periods before a mid-year change. | Compliance Risk | **High** | schema-catalogue.json: EMPLOYEE_TAX_INFO columns — no EFFECTIVE_DATE, no PRIOR_* columns. No trigger on EMPLOYEE_TAX_INFO in the triggers list. | Add an EMPLOYEE_TAX_INFO_HISTORY table with EFFECTIVE_DATE/END_DATE columns, populated by a before-update trigger. Alternatively, adopt an effective-date insert-only pattern and have `calculate_employee_pay` use the row with the most recent `EFFECTIVE_DATE <= period_start_date`. |
| TD-59 | **HRMS_COMMON_LIB.pll and HRMS_VALIDATION_LIB.pll have no version numbers; deployed .plx compiled binaries may not match source.** Oracle Forms compiles .pll → .plx at deployment. No CI/CD enforces recompilation. If a developer edits a .pll but does not recompile and redeploy the .plx, the running system uses the old binary while source control shows the patch — undetectable without a manual diff. | Deployment Risk | **High** | Stage 8: "Build: Absent." No version constant found in either .pll source file. No `frmcmp_batch` call in any script. | Add a version constant to each .pll (e.g. `c_lib_version CONSTANT VARCHAR2(10) := '4.2.0'`). Add a pre-deployment check comparing source modification timestamps against deployed .plx timestamps. Include `frmcmp_batch` in any future CI/CD step. |
| TD-60 | **No acknowledgment mechanism for Oracle Financials GL file drop — silent import failures are undetectable.** `generate_gl_journal` sets `GL_FEED_STATUS='COMPLETED'` after writing the file, meaning "file written to disk" not "Oracle Financials imported it." If the Financials batch job fails, HRMS shows COMPLETED indefinitely while the GL period remains unpopulated. Discovered only at period-end reconciliation. | Operational Risk | **High** | Stage 7: GL journal interaction is "Async Fire-and-Forget, Unversioned." No inbound channel from Oracle Financials in any source file. `GL_FEED_STATUS` semantics are "file written," not "import confirmed." | Implement a two-phase handshake: drop the file → set status `PENDING_CONFIRMATION` → a DBMS_SCHEDULER job polls a `GL_FEED_ACK` directory for an acknowledgment file from Financials → update status to `CONFIRMED` or `FAILED`. |
| TD-61 | **No DBMS_SCHEDULER job DDL exists for the ADP benefits weekly export.** The trigger for this integration is unknown — either it runs only when manually invoked or a scheduler job exists in the database but is not in source control. If the manual invoker is unavailable, the benefits feed silently stops and ADP receives no update, potentially affecting employee benefits enrollment without any alert. | Operational Risk | **High** | Stage 8: "DBMS_SCHEDULER: Declared-only — no DDL." No scheduler job for benefits_feed in any source file. NFR-50: filename includes YYYYMMDD, consistent with automated generation. | Add CREATE_JOB DDL to source control for the benefits feed and GL journal jobs. Add an alert: if `BENEFITS_FEED_STATUS` is not updated within schedule+2 days, notify the payroll administrator. |

---

**Medium (2 new)**

| ID | Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-54 | **PERFORMANCE_GOALS.WEIGHT_PCT has no sum-to-100 constraint per review.** A manager can submit a review where goal weights total 300% or 0%. `submit_manager_review` computes `OVERALL_RATING` by summing `SELF_RATING * WEIGHT_PCT/100` across goals, so inflated weights can push the computed rating outside the 1.0–5.0 constraint, raising -20403 — but only after the weights are already accepted. | Data Integrity | **Medium** | schema-catalogue.json: PERFORMANCE_GOALS has no check constraint on WEIGHT_PCT sum. CHK_RATING_RANGE on OVERALL_RATING is a secondary constraint, not a weight guard. | Add a sum-to-100 validation in `submit_manager_review`: `SELECT SUM(WEIGHT_PCT) FROM PERFORMANCE_GOALS WHERE REVIEW_ID=p_review_id` — raise -20404 if result is not between 99.9 and 100.1. |
| TD-56 | **TRG_LEAVE_REQUEST_AUDIT fires AFTER UPDATE OF STATUS only — the initial INSERT of a leave request is never captured.** A new leave submission (STATUS='PENDING') produces no AUDIT_LOG entry via the trigger. For auto-approved leave types the INSERT goes directly to STATUS='APPROVED' with no subsequent UPDATE, producing zero audit entries for the entire transaction. | Compliance Risk | **Medium** | Trigger definition: `AFTER UPDATE OF STATUS` — column-list trigger, INSERT excluded. No `PKG_AUDIT.log_action` call in PKG_LEAVE.submit_leave_request. Auto-approve path: INSERT with STATUS='APPROVED' → no subsequent status UPDATE → trigger never fires. | Extend trigger to `AFTER INSERT OR UPDATE OF STATUS`; add an INSERT branch logging the initial submission. Alternatively, call `PKG_AUDIT.log_action` explicitly from `PKG_LEAVE.submit_leave_request` after the INSERT. |

---

**Low (2 new)**

| ID | Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-62 | **SMTP bounce handling: `UTL_SMTP.CLOSE_DATA` succeeds even when the recipient is invalid — delivery failures are never detected.** STATUS='SENT' means "relay accepted the message," not "message was delivered." Bounced messages return to the envelope sender, which is never read back by any process. Terminated employees with stale email addresses silently accumulate STATUS='SENT' notifications that were never received. | Operational Risk | **Medium** | NFR-51: one connection per email. AP-27: retry is manual. PKG_NOTIFICATION.pkb: STATUS set to 'SENT' after `UTL_SMTP.CLOSE_DATA` — no bounce polling. The SMTP relay acceptance / final delivery distinction is not modeled anywhere. | Configure a monitored bounce mailbox as the SMTP MAIL FROM address. Add a scheduler job to parse bounces and set STATUS='BOUNCED' for known-undeliverable recipients. Short-term: add a BOUNCED_FLAG column to NOTIFICATION_QUEUE. |
| TD-45 | *(Already in Batch 2 primary analysis — not duplicated here)* | — | — | — | — |

---

### New Implied Non-Functional Requirements (NFR-86 – NFR-90)

| ID | NFR Name | Value | Category | Evidence Basis | Confidence |
|---|---|---|---|---|---|
| NFR-86 | NOCACHE sequence serialization ceiling | 28 of 29 sequences are NOCACHE. Each NEXTVAL requires a synchronous redo log write and dictionary mutex. At 200 concurrent users performing simultaneous DML, NOCACHE sequences create a serialization point at sequence generation. On spinning disk: ~500–800 NEXTVAL/second per sequence under load. High-frequency tables (LEAVE_REQUESTS, PAYROLL_DETAILS, AUDIT_LOG, NOTIFICATION_QUEUE) all use NOCACHE sequences — sustained concurrent insert throughput is bounded by redo I/O latency, not CPU. | Throughput | schema-catalogue.json: 28 sequences explicitly NOCACHE; only SEQ_AUDIT CACHE 100. All high-frequency tables confirmed NOCACHE. | HIGH |
| NFR-87 | SEQ_AUDIT CACHE 100 — audit gap on unplanned instance restart | SEQ_AUDIT caches 100 values per cache fill. On any instance shutdown (planned or unplanned), unused cached values are lost and AUDIT_ID skips. With 11 packages all calling `PKG_AUDIT.log_action`, cache exhaustion is frequent. Post-crash AUDIT_LOG will have non-contiguous AUDIT_ID values — a compliance auditor checking for gaps to detect record suppression will see artifacts of the CACHE as false positives, making the gap-detection control unreliable. | Reliability / Compliance | SEQ_AUDIT "CACHE 100." PKG_AUDIT.log_action: `SEQ_AUDIT.NEXTVAL` on every call. CACHE semantics are an Oracle documented behaviour. | HIGH |
| NFR-88 | Oracle Net connection ceiling under 200 concurrent users | Oracle Forms 12c opens one dedicated Oracle Net session per Forms client. At 200 concurrent users the database holds exactly 200 persistent connections (dedicated server assumed — no connection pooling in repo). Oracle 19c default PROCESSES=300, SESSIONS≈335. Background processes consume ~20–40 sessions, leaving ~60–80 session headroom before ORA-00018 (maximum sessions exceeded). Headroom is unmonitored and not declared anywhere in the repository. | Resource Management | Architecture: 200 concurrent users, on-premises dedicated server, Oracle Forms thick client. No PROCESSES/SESSIONS declaration in any config file. | MEDIUM (inferred from Forms architecture) |
| NFR-89 | Notification queue maximum throughput: 600/hour; payroll run creates minimum 20-minute drain delay | 50 notifications/run × 12 runs/hour (every 5 minutes) = 600/hour. PKG_PAYROLL sends at minimum one notification per employee. For 200 employees, a payroll run injects 200 notifications simultaneously. Draining 200 at 50/run requires 4 consecutive scheduler invocations = minimum 20 minutes before payslip emails are delivered — while higher-priority notifications from other users queue behind them unless they have lower PRIORITY values. | Throughput / Rate | NFR-52: batch size DEFAULT 50. PKG_NOTIFICATION.process_queue: ORDER BY PRIORITY ASC, CREATED_DATE ASC. PKG_PAYROLL: one notification per employee. Scheduler interval unconfirmed but 5-minute is the stated pattern. | MEDIUM |
| NFR-90 | VW_ORG_HIERARCHY NOCYCLE gap: circular reference inserted outside the package layer causes ORA-01436 on all org chart queries | VW_ORG_HIERARCHY uses `CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID` without `NOCYCLE`. `PKG_EMPLOYEE.validate_manager` checks for circular chains up to depth 15 — but only when called from the package layer. TRG_EMP_BEFORE_UPDATE is currently broken (TD-32), so a direct SQL UPDATE on `EMPLOYEES.MANAGER_EMP_ID` from SQL*Plus, a data patch, or the self-service portal bypasses the circular check entirely. After such an insert, any query against VW_ORG_HIERARCHY raises ORA-01436 until the circle is manually corrected — all org chart and BI reports using the view fail. | Availability | VW_ORG_HIERARCHY: `CONNECT BY` — no NOCYCLE noted in view definition. TD-32: TRG_EMP_BEFORE_UPDATE broken. validate_manager called only from PKG_EMPLOYEE package layer, not from DB trigger. | HIGH |

---

### Second-Pass Summary

| Register | New Entries | IDs | Critical | High | Medium |
|---|---|---|---|---|---|
| Technical Debt | 14 | TD-49 – TD-62 | 3 | 7 | 2 (+ 2 Low) |
| NFR (Implied) | 5 | NFR-86 – NFR-90 | — | 3 | 2 |

**Three findings of highest priority not in the primary analysis:**

1. **TD-49 (Critical)** — PKG_LEAVE has no server-side authorization gate. Any direct DB caller (self-service portal, SQL*Plus) can approve or cancel any employee's leave. The entire authorization model exists only inside Oracle Forms triggers.
2. **TD-57 (Critical)** — The Oracle FMW 12.2.1.4 stack has been running without security patches since October 2025. The primary analysis described this as "Sustaining Engineering" without flagging that the system is currently unpatched.
3. **TD-58 (Critical)** — Oracle Forms 12c requires a Java Plugin that no modern browser supports. The delivery mechanism for 200 users is entirely undocumented and depends on end-of-life browser or Java Web Start infrastructure.

---

## PKG_REPORTING — Full Extraction (Source: plsql/packages/PKG_REPORTING.pkb)

> Source recovered from file_cache.json. This package was listed in LOW-007 (RPT_* stub) and LOW-NFR-44 (nightly refresh comment) but never deeply analyzed. The following records all procedures, business rules, table usage, and implied NFRs from the package body.

---

### Procedures (8 total)

| Procedure | Signature | Purpose | Return Type |
|---|---|---|---|
| `headcount_report` | `p_cursor OUT t_report_cursor, p_as_of_date IN DATE DEFAULT SYSDATE, p_dept_id IN NUMBER DEFAULT NULL, p_location IN VARCHAR2 DEFAULT NULL` | Point-in-time headcount by department and location; breakdowns by employment type and gender | REF CURSOR |
| `compensation_summary` | `p_cursor OUT t_report_cursor, p_dept_id IN NUMBER DEFAULT NULL, p_grade_id IN NUMBER DEFAULT NULL` | Salary analytics by department/grade/job — actual vs grade band, compa-ratio | REF CURSOR |
| `turnover_report` | `p_cursor OUT t_report_cursor, p_start_date IN DATE, p_end_date IN DATE, p_dept_id IN NUMBER DEFAULT NULL` | Termination rate, voluntary/involuntary split, average tenure at exit per department | REF CURSOR |
| `new_hires_report` | `p_cursor OUT t_report_cursor, p_start_date IN DATE, p_end_date IN DATE, p_dept_id IN NUMBER DEFAULT NULL` | Detail listing of employees hired in date range with job, location, salary, and manager | REF CURSOR |
| `leave_utilization_report` | `p_cursor OUT t_report_cursor, p_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE), p_dept_id IN NUMBER DEFAULT NULL` | Leave entitlement vs usage by department and leave type for a calendar year | REF CURSOR |
| `payroll_summary_report` | `p_cursor OUT t_report_cursor, p_period_id IN NUMBER` | Gross pay, individual tax lines (Fed/State/SS/Medicare), total deductions, and net pay by department for a payroll period | REF CURSOR |
| `eeo_compliance_report` | `p_cursor OUT t_report_cursor, p_as_of_date IN DATE DEFAULT SYSDATE` | EEO headcount by job category and gender (M/F/O/NULL) with female percentage | REF CURSOR |
| `refresh_reporting_tables` | `p_user IN VARCHAR2 DEFAULT USER` | Stub: intended to truncate/repopulate RPT_* denormalized tables nightly; body is placeholder only; logs via `PKG_COMMON.log_info` | VOID |

---

### Tables Read by PKG_REPORTING

| Table | Procedures That Access It | Columns Used |
|---|---|---|
| `EMPLOYEES` | All 7 report procedures | `EMP_ID`, `EMP_NUMBER`, `FIRST_NAME`, `LAST_NAME`, `HIRE_DATE`, `TERMINATION_DATE`, `TERMINATION_REASON`, `EMPLOYMENT_STATUS`, `EMPLOYMENT_TYPE`, `GENDER`, `DEPT_ID`, `LOCATION_CODE`, `JOB_ID`, `MANAGER_EMP_ID` |
| `DEPARTMENTS` | All 7 report procedures | `DEPT_ID`, `DEPT_NAME`, `COST_CENTER` |
| `LOCATIONS` | `headcount_report`, `new_hires_report` | `LOCATION_CODE`, `LOCATION_NAME`, `CITY`, `STATE_PROVINCE` |
| `JOB_TITLES` | `compensation_summary`, `new_hires_report`, `eeo_compliance_report` | `JOB_ID`, `JOB_TITLE`, `GRADE_ID`, `EEO_CATEGORY` |
| `JOB_GRADES` | `compensation_summary` | `GRADE_ID`, `GRADE_NAME`, `MIN_SALARY`, `MAX_SALARY` |
| `SALARY_RECORDS` | `compensation_summary`, `new_hires_report` | `EMP_ID`, `BASE_SALARY`, `ACTIVE_FLAG` |
| `LEAVE_BALANCES` | `leave_utilization_report` | `EMP_ID`, `LEAVE_TYPE_ID`, `CALENDAR_YEAR`, `OPENING_BALANCE`, `ACCRUED`, `USED`, `ADJUSTMENT` |
| `LEAVE_TYPES` | `leave_utilization_report` | `LEAVE_TYPE_ID`, `LEAVE_TYPE_NAME` |
| `PAYROLL_DETAILS` | `payroll_summary_report` | `EMP_ID`, `RUN_ID`, `ELEMENT_TYPE`, `ELEMENT_ID`, `AMOUNT`, `STATUS` |
| `PAYROLL_RUNS` | `payroll_summary_report` | `RUN_ID`, `PERIOD_ID` |

**PKG_REPORTING is read-only against all HRMS tables** — no INSERT, UPDATE, DELETE, or MERGE found anywhere in the package body.

---

### Business Rules Embedded in Query Logic

| Rule ID | Rule | Location | Notes |
|---|---|---|---|
| BR-RPT-01 | Active employee definition for headcount: `EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= p_as_of_date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)` | `headcount_report` | Three-part active check; point-in-time aware via `p_as_of_date` parameter |
| BR-RPT-02 | Current salary definition: `SALARY_RECORDS.ACTIVE_FLAG = 'Y'` with no date filter — if multiple ACTIVE_FLAG='Y' rows exist for an employee, both will appear in `compensation_summary` and `new_hires_report` (causing row multiplication) | `compensation_summary`, `new_hires_report` | No `EFFECTIVE_DATE <= SYSDATE` guard; relies on `PKG_PAYROLL` correctly maintaining only one ACTIVE_FLAG='Y' row |
| BR-RPT-03 | Compa-ratio formula: `AVG(BASE_SALARY) / ((MIN_SALARY + MAX_SALARY) / 2) * 100` — midpoint ratio using simple average of grade band | `compensation_summary` | Industry standard; midpoint is arithmetic mean, not a configured value |
| BR-RPT-04 | Turnover denominator: `COUNT(CASE WHEN HIRE_DATE <= p_end_date THEN 1 END)` — headcount base is all employees ever hired up to period end, not average headcount over the period; this produces a conservative (lower) turnover percentage vs. the standard average-headcount denominator | `turnover_report` | Non-standard denominator; will understate turnover relative to SHRM formula |
| BR-RPT-05 | Turnover voluntary/involuntary split: `TERMINATION_REASON = 'VOLUNTARY'` vs `TERMINATION_REASON != 'VOLUNTARY'` — involuntary bucket includes NULL termination reason, meaning unknown reasons are silently counted as involuntary | `turnover_report` | NULL coalesced into involuntary; could distort involuntary count if TERMINATION_REASON is sometimes unset |
| BR-RPT-06 | Turnover report HAVING clause: `COUNT(CASE WHEN HIRE_DATE <= p_end_date THEN 1 END) > 0` — excludes departments that had no employees up to the period end date | `turnover_report` | Prevents divide-by-zero in TURNOVER_PCT; also suppresses departments created after period end |
| BR-RPT-07 | Leave utilization formula: `AVG(USED) / AVG(OPENING_BALANCE + ACCRUED)` — averages over the department rather than summing totals; a department with one employee who used 100% and one who used 0% shows 50% utilization, which matches expected HR reporting convention | `leave_utilization_report` | Average-of-individuals, not total-used / total-entitled |
| BR-RPT-08 | Payroll summary tax identification by hard-coded ELEMENT_ID constants: Federal Tax = 100, State Tax = 101, Social Security = 102, Medicare = 103 | `payroll_summary_report` | These IDs are literals in the query — not derived from PAY_ELEMENTS or SYSTEM_PARAMETERS; any re-seeding or addition of new pay elements that shifts these IDs will silently break the tax column calculations with no error |
| BR-RPT-09 | Payroll net pay: `SUM(pd.AMOUNT)` across all element types — earnings are positive, deductions/taxes are stored as negative AMOUNT values; net = gross earnings + (negative deductions) | `payroll_summary_report` | Relies on sign convention in PAYROLL_DETAILS; if any deduction is stored as a positive amount, net pay will be overstated |
| BR-RPT-10 | EEO active employee filter: `EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= p_as_of_date` — no TERMINATION_DATE check; relies entirely on EMPLOYMENT_STATUS being correctly set to 'TERMINATED' on exit | `eeo_compliance_report` | Single-field filter; contrast with BR-RPT-01's three-field filter in `headcount_report` — inconsistency between reports |
| BR-RPT-11 | EEO gender buckets: explicit counts for 'M', 'F', 'O' (other), and NULL (not disclosed) — no catch-all for invalid values such as 'N' or any arbitrary string entered before a CHECK constraint was in place | `eeo_compliance_report` | Cross-reference TD-40: no CHECK constraint on EMPLOYEES.GENDER; arbitrary values are counted in none of the four buckets — EEO totals will not reconcile to overall headcount |
| BR-RPT-12 | `refresh_reporting_tables` is a placeholder stub — the body contains only a `PKG_COMMON.log_info` call; no RPT_* table truncation or repopulation logic is implemented | `refresh_reporting_tables` | Confirms LOW-007 (RPT_* DDL absent) and LOW-NFR-44 (nightly refresh unconfirmed); the RPT_* tables referenced in the spec do not exist and the refresh mechanism is not implemented |

---

### Implied NFRs from PKG_REPORTING

| ID | NFR Name | Value | Category | Evidence | Confidence |
|---|---|---|---|---|---|
| NFR-91 | All report procedures are read-only / no side effects | All 7 report procedures are pure SELECTs via REF CURSOR; no DML; only `refresh_reporting_tables` modifies state (stub log call) | Correctness | PKG_REPORTING.pkb: no INSERT/UPDATE/DELETE found in any report procedure | HIGH |
| NFR-92 | Headcount report is point-in-time as-of-date aware | `headcount_report` accepts `p_as_of_date IN DATE DEFAULT SYSDATE`; all active-employee filters are evaluated against this parameter, not SYSDATE | Temporal Correctness | `headcount_report`: `HIRE_DATE <= p_as_of_date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)` | HIGH |
| NFR-93 | Compensation report compa-ratio uses arithmetic grade midpoint | Grade midpoint = `(MIN_SALARY + MAX_SALARY) / 2`; not a separately stored or configurable value | Calculation | `compensation_summary`: COMPA_RATIO expression | HIGH |
| NFR-94 | Turnover percentage uses ever-hired base, not average headcount | Denominator is `COUNT(HIRE_DATE <= p_end_date)`, not `(opening + closing) / 2` | Calculation | `turnover_report` | HIGH |
| NFR-95 | Payroll tax line IDs are hard-coded literals (100–103) | Federal/State/SS/Medicare identified by hard-coded ELEMENT_ID integers, not a lookup | Configuration | `payroll_summary_report`: ELEMENT_ID IN (100, 101, 102, 103) literals | HIGH |
| NFR-96 | EEO report active-employee filter is single-field only | Uses `EMPLOYMENT_STATUS = 'ACTIVE'` without TERMINATION_DATE guard — weaker than the three-part filter in `headcount_report` | Correctness | `eeo_compliance_report` vs `headcount_report` | HIGH |

---

### New Technical Debt & Risk Items from PKG_REPORTING Analysis

| ID | Risk / Debt Item | Category | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|
| TD-82 | **Payroll tax line identification by hard-coded ELEMENT_ID literals (100–103) in `payroll_summary_report`** — Federal Tax = 100, State Tax = 101, SS = 102, Medicare = 103 are integer literals embedded directly in the SQL. If any of these PAY_ELEMENTS rows are reseeded, renumbered during a data migration, or if new tax elements are inserted with lower IDs that push existing ones to different positions, the four tax columns in the payroll summary will silently zero out or aggregate wrong elements. No error is raised. | Configuration Risk | **High** | `payroll_summary_report`: `CASE WHEN pd.ELEMENT_ID = 100 THEN ...` — four separate hard-coded IDs; no join to PAY_ELEMENTS for validation | Replace hard-coded IDs with a subquery or SYSTEM_PARAMETERS lookup: `WHERE PARAM_NAME = 'TAX_ELEMENT_FED_ID'`; expose all four IDs as configurable SYSTEM_PARAMETERS entries in the 'PAYROLL' group |
| TD-83 | **`eeo_compliance_report` active filter is weaker than `headcount_report`** — uses only `EMPLOYMENT_STATUS = 'ACTIVE'` with no TERMINATION_DATE guard. An employee whose EMPLOYMENT_STATUS was not updated correctly on termination (e.g. direct SQL update bypassing PKG_EMPLOYEE, or the broken TRG_EMP_BEFORE_UPDATE) will appear in EEO counts but not in headcount counts, causing the two reports to disagree. This is a compliance-reportable discrepancy. | Compliance Risk | **Medium** | `eeo_compliance_report`: `WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.HIRE_DATE <= p_as_of_date` — no TERMINATION_DATE check. Compare with `headcount_report`: full three-part check | Align `eeo_compliance_report` filter with `headcount_report`: add `AND (e.TERMINATION_DATE IS NULL OR e.TERMINATION_DATE > p_as_of_date)` |
| TD-84 | **Turnover involuntary bucket silently absorbs NULL TERMINATION_REASON** — `TERMINATION_REASON != 'VOLUNTARY'` evaluates NULL as a non-match, meaning employees terminated without a recorded reason are counted as involuntary terminations. If TERMINATION_REASON is routinely left blank during quick-exit terminations, involuntary turnover will be overstated with no data quality indicator | Data Quality / Compliance | **Medium** | `turnover_report`: `TERMINATION_REASON != 'VOLUNTARY'` — three-valued logic; NULL != 'VOLUNTARY' is NULL (false in WHERE), but inside CASE WHEN it evaluates the same way in Oracle; both voluntary and involuntary counts use CASE WHEN pattern — the != 'VOLUNTARY' case fires for any non-null non-VOLUNTARY value plus NULL | Add an explicit NULL bucket: add `COUNT(CASE WHEN e.TERMINATION_REASON IS NULL AND e.TERMINATION_DATE BETWEEN ... THEN 1 END) AS UNKNOWN_REASON` to `turnover_report`; add a NOT NULL constraint or FK on TERMINATION_REASON for terminated employees |
| TD-85 | **`compensation_summary` and `new_hires_report` use `SALARY_RECORDS.ACTIVE_FLAG = 'Y'` with no date guard** — if the ACTIVE_FLAG maintenance by `PKG_PAYROLL` ever creates a duplicate ACTIVE_FLAG='Y' row (e.g. during a failed salary change that set the new row to ACTIVE but failed to set the old row to INACTIVE before a ROLLBACK, or via direct INSERT), both salary rows join to the same employee, doubling that employee in COUNT(*) and distorting all averages. No uniqueness constraint on `(EMP_ID, ACTIVE_FLAG)` is mentioned in the schema catalogue. | Data Integrity | **Medium** | `compensation_summary`: `JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y'` — no ROWNUM=1 or MAX() guard; cross-reference schema-catalogue.json for SALARY_RECORDS unique constraints | Add a unique function-based index: `CREATE UNIQUE INDEX UQ_SAL_ACTIVE ON SALARY_RECORDS (CASE WHEN ACTIVE_FLAG='Y' THEN EMP_ID END)` — enforces at most one active salary record per employee at the DB level |
| TD-86 | **Turnover denominator is non-standard — uses ever-hired base, not average headcount** — the formula `terminations / ever_hired` is lower than the industry-standard SHRM formula `terminations / ((opening_hc + closing_hc) / 2)`. If HR benchmarks against published industry data using the SHRM formula, the HRMS figures will appear systematically lower, potentially masking a retention problem. This is undocumented and invisible to report consumers. | Operational Risk | **Low** | `turnover_report` TURNOVER_PCT: `COUNT(termination) / NULLIF(COUNT(hire_date <= p_end_date), 0)` — denominator is cumulative hire count, not average headcount | Document the non-standard denominator in a report header or SYSTEM_PARAMETERS description; or add an alternative TURNOVER_PCT_SHRM column using `(opening_hc + closing_hc) / 2` as denominator |

---

### Resolved Validation Queue Item

| ID | Prior Status | Resolution |
|---|---|---|
| LOW-007 | RPT_* denormalized reporting tables — DDL absent; `refresh_reporting_tables` referenced nightly refresh | **CONFIRMED STUB** — `refresh_reporting_tables` body contains only a `PKG_COMMON.log_info` call and a comment explaining that in production this "truncates and repopulates RPT_* tables." No DDL for RPT_* tables exists in the source set, and the refresh logic is entirely unimplemented. RPT_* tables are a planned-but-not-built capability. |
| LOW-NFR-44 | RPT_* nightly refresh — comment-only evidence; stub body | **CONFIRMED UNIMPLEMENTED** — the `refresh_reporting_tables` stub confirms the comment was aspirational. No scheduler DDL and no truncate/repopulate logic found. |

---

### PKG_REPORTING Layer Summary

- **Source:** `plsql/packages/PKG_REPORTING.pkb` (recovered from file_cache.json)
- **Package type:** Read-only reporting layer; all procedures return REF CURSORs; no DML
- **Procedures catalogued:** 8 (headcount_report, compensation_summary, turnover_report, new_hires_report, leave_utilization_report, payroll_summary_report, eeo_compliance_report, refresh_reporting_tables)
- **Tables read:** 10 (EMPLOYEES, DEPARTMENTS, LOCATIONS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS, LEAVE_BALANCES, LEAVE_TYPES, PAYROLL_DETAILS, PAYROLL_RUNS)
- **Business rules extracted:** 12 (BR-RPT-01 through BR-RPT-12)
- **NFR entries added:** 6 (NFR-91 through NFR-96)
- **TD entries added:** 5 (TD-82 through TD-86) — 0 Critical, 1 High, 3 Medium, 1 Low
- **Prior findings updated:** TD-40 (EEO gender — evidence strengthened by BR-RPT-11); LOW-007 resolved; LOW-NFR-44 resolved
- **Cross-references:** TD-40 (EEO gender constraint), TD-32 (broken trigger feeds EEO filter inconsistency in TD-83), LOW-007 (RPT_* stub confirmed)
