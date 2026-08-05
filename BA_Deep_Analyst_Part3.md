---

## OUTPUT 5 — Value Stream Maps

### Value Stream: Employee Lifecycle
**Trigger:** Decision to hire a new person for the organisation
**Actors Involved:** HR Administrator, Hiring Manager, Payroll Administrator, Employee, Manager, System
**Terminal Outcomes:** Employee ACTIVE and contributing; or TERMINATED with all records closed; or REHIRED after prior termination

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | New Employee Record Created | HR Administrator | Enter employee details, assign department, job, manager, and starting salary | Decision to hire made; department and job title exist and are active | Employee record created with ACTIVE status; unique employee number assigned; welcome email sent | Value-Adding |
| 2 | Employee Active | Employee, Manager, HR | Employee performs their role; personal details updated as needed; manager assigns work | Employee record in ACTIVE status | Ongoing employment; record maintained | Value-Adding |
| 3 | Department Transfer | HR Administrator | Move employee to a new department, job, or location | Employee in ACTIVE status; transfer request initiated | Employee record updated; transfer history entry written; prior assignment preserved | Value-Adding |
| 4 | Promotion | HR Administrator | Assign a higher job title and new salary | Promotion decision made | Employee job title updated; new salary record effective; promotion history written | Value-Adding |
| 5 | On Leave | Employee, Manager | Employee takes approved leave | Leave request APPROVED | Employment status remains ACTIVE; leave counted in USED balance | Wait-Queue |
| 6 | Suspended | HR Administrator | Employment suspended pending investigation or disciplinary process | HR or management decision | Employment status = SUSPENDED | Wait-Queue |
| 7 | Termination Processed | HR Administrator | Record employee departure, cancel pending leave, close salary and pay elements | Termination decision made; employee not already TERMINATED | Status = TERMINATED; salary and elements closed; manager notified; COBRA/access revocation flagged as incomplete | Value-Adding |
| 8 | Rehire | HR Administrator | Reinstate a departed employee under new terms | Employee previously TERMINATED; rehire decision made | Status = ACTIVE; new hire date; prior history preserved | Value-Adding |

**Handoff Points:**
- Stage 1 → Payroll: Salary record created in Payroll domain immediately on hire
- Stage 1 → Notifications: Welcome email to employee; new direct report email to manager
- Stage 4 → Payroll: New salary record created in Payroll domain
- Stage 7 → Notifications: Termination notification to manager

**Wait States:**
- Stage 5 (On Leave): process waits for leave period to end (no time-bound SLA in system)
- Stage 6 (Suspended): process waits for HR/management decision (no time-bound SLA in system)

**External Dependencies:** None confirmed; COBRA benefits and system access revocation are TODOs

**States Accounted For:**
- ACTIVE → Stage 2
- ON_LEAVE → Stage 5
- SUSPENDED → Stage 6
- TERMINATED → Stage 7

**Unaccounted States:** None — all four EMPLOYMENT_STATUS values are mapped

---

### Value Stream: Payroll Run
**Trigger:** Payroll administrator initiates a run for an open pay period
**Actors Involved:** Payroll Administrator, Payroll Manager, System Scheduler, Finance (GL import)
**Terminal Outcomes:** Run APPROVED and GL journal produced; or Run REVERSED; or Run in ERROR awaiting remediation

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Pay Period Open | Payroll Administrator | Select the active pay period for processing | Pay period exists with OPEN status | Pay period identified; run can be created | Value-Adding |
| 2 | Payroll Run Created | Payroll Administrator | Create the payroll run for the selected period | Pay period is OPEN | Run record created with PENDING status | Value-Adding |
| 3 | Calculation In Progress | System | Calculate gross pay, taxes, and deductions for all active employees | Run in PENDING status; administrator initiates calculation | Run status = CALCULATING; all pay detail lines written | Value-Adding |
| 4 | Calculated | Payroll Administrator | Review calculation results, check error count, inspect individual payslips | Calculation complete | Run status = CALCULATED (or ERROR if any employee failed) | Verification |
| 4a | Error Review | Payroll Administrator | Investigate employees flagged with calculation errors; correct salary records or tax data and recalculate | Run status = ERROR | Errors resolved; run recalculated | Exception |
| 5 | Approved | Payroll Manager | Approve the calculated run after verifying totals | Run status = CALCULATED; approver has APPROVE permission | Run status = APPROVED; approval date and approver recorded | Approval Gate |
| 6 | GL Journal Generated | System | Produce the pipe-delimited journal file for Oracle Financials import | Run APPROVED; GL feed integration active | Journal file written to GL_FEED_OUT directory | Value-Adding |
| 7 | Reversed | Payroll Manager | Cancel the run if an error is found post-approval | Any status | Run and all detail lines marked REVERSED | Exception |

**Handoff Points:**
- Stage 5 → Integration: GL journal generation triggered after approval
- Stage 5 → 〰️ ASSUMED payment disbursement to employee bank accounts (not implemented)

**Wait States:**
- Stage 4 (Calculated): waits for human review before approval — no SLA coded in system

**External Dependencies:**
- Stage 6: Oracle Financials GL import — file pickup mechanism not implemented in HRMS

**States Accounted For:**
- PENDING → Stage 2
- CALCULATING → Stage 3
- CALCULATED → Stage 4
- ERROR → Stage 4a
- APPROVED → Stage 5
- REVERSED → Stage 7

**Unaccounted States:** PAID — status exists in the data model but no transition logic found in code (⚠️ LOW — PAID status has no procedure to set it; payment disbursement is not implemented)

---

### Value Stream: Leave Request
**Trigger:** Employee submits a request for time off
**Actors Involved:** Employee, Manager (Approver), HR Administrator, System
**Terminal Outcomes:** Leave TAKEN (time used); or REJECTED (days returned); or CANCELLED (days returned); or auto-approved with no manual step

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Leave Requested | Employee | Select leave type, dates, half-day flag, and reason; submit request | Employee ACTIVE; leave type active; tenure requirement met; dates valid; no overlap; sufficient balance (accrual types) | Request created; PENDING balance increased; status = PENDING (or auto-APPROVED for no-approval types) | Value-Adding |
| 2 | Awaiting Approval | Manager | Manager reviews the pending request in their approvals queue | Request status = PENDING; leave type requires approval | Manager sees request in pending list | Wait-Queue |
| 3 | Approved | Manager | Manager approves the request | Request status = PENDING | Status = APPROVED; PENDING balance decremented; USED balance incremented; employee notified | Handoff |
| 3a | Rejected | Manager | Manager rejects the request with a reason | Request status = PENDING | Status = REJECTED; PENDING balance released; employee notified with reason | Exception |
| 4 | Cancelled | Employee or System | Employee cancels approved or pending leave; system auto-cancels on termination | Request status = PENDING or APPROVED | Status = CANCELLED; balance restored (PENDING or USED decremented accordingly) | Exception |
| 5 | Leave Taken | System / HR | Leave period passes; leave is recorded as taken | Status = APPROVED; leave dates reached | Status = TAKEN (manual or batch update) | Value-Adding |

**Handoff Points:**
- Stage 1 → Notifications: Manager notified of pending request (if approval required)
- Stage 3 → Notifications: Employee notified of approval
- Stage 3a → Notifications: Employee notified of rejection with reason

**Wait States:**
- Stage 2 (Awaiting Approval): no time-bound SLA in system for manager to respond

**External Dependencies:** None

**States Accounted For:**
- PENDING → Stage 2
- APPROVED → Stage 3
- REJECTED → Stage 3a
- CANCELLED → Stage 4
- TAKEN → Stage 5

**Unaccounted States:** None — all five LEAVE_REQUESTS status values are mapped

---

### Value Stream: Annual Performance Review
**Trigger:** HR creates and opens a new performance review cycle for the year
**Actors Involved:** HR Administrator, Employee, Manager, System
**Terminal Outcomes:** Review ACKNOWLEDGED by employee; or stalled in any intermediate status (no escalation mechanism found)

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Cycle Created | HR Administrator | Define review cycle name, year, start/end dates, and due dates | Organisational decision to run annual reviews | Cycle in DRAFT status | Value-Adding |
| 2 | Cycle Opened | HR Administrator | Open the cycle to allow reviews to begin | Cycle in DRAFT status | Cycle status = OPEN; reviews generated for all eligible employees; employees notified | Value-Adding |
| 3 | Not Started | Employee | Review exists but employee has not yet begun their self-assessment | Review status = NOT_STARTED | Employee notified to begin self-assessment | Wait-Queue |
| 4 | Self-Review | Employee | Employee writes and submits their self-assessment | Review in NOT_STARTED or SELF_REVIEW status | Status = MANAGER_REVIEW; manager notified that self-assessment is ready | Value-Adding |
| 5 | Manager Review | Manager | Manager reads self-assessment, writes their assessment, assigns a rating 1.0–5.0 | Review status = MANAGER_REVIEW | Status = COMPLETED; rating label assigned; employee notified | Value-Adding |
| 6 | Completed | Employee | Employee reads the completed review and adds optional comments | Review status = COMPLETED | Status = ACKNOWLEDGED; acknowledgement date recorded | Verification |
| 7 | Acknowledged | HR Administrator | HR confirms all reviews complete; closes the cycle | All reviews ACKNOWLEDGED (or acceptable completion rate met) | Cycle status = CLOSED | Handoff |

**Handoff Points:**
- Stage 2 → Stage 3: System generates review records and sends employee notifications
- Stage 4 → Stage 5: Manager notified by email that self-assessment is ready
- Stage 5 → Stage 6: Employee notified by email that review is completed

**Wait States:**
- Stage 3 (Not Started): no SLA or escalation if employee does not begin self-assessment
- Stage 5 (Manager Review): no SLA or escalation if manager does not complete review

**External Dependencies:** None

**States Accounted For:**
- NOT_STARTED → Stage 3
- SELF_REVIEW → Stage 4 (entry condition; status in DDL but not an intermediate stop in the code path)
- MANAGER_REVIEW → Stage 5
- COMPLETED → Stage 6
- ACKNOWLEDGED → Stage 7

**Unaccounted States:**
- MEETING_SCHEDULED — status value exists in DDL but no procedure sets it; no transition logic found (⚠️ LOW — defined but unused)
- DRAFT/OPEN/IN_PROGRESS/CALIBRATION for REVIEW_CYCLES — OPEN and CLOSED are implemented; DRAFT is the initial state; IN_PROGRESS and CALIBRATION have no transition logic in the provided code (⚠️ LOW — partially implemented)

---

## OUTPUT 6 — Domain Architecture Map (Refined)

| Domain | Bounded Context | Core Entities | Complexity | Dependencies | Refinements from Deep Analysis |
|---|---|---|---|---|---|
| Employee Management | Core | EMPLOYEES, EMPLOYEE_HISTORY, DEPARTMENTS, JOB_TITLES, JOB_GRADES, LOCATIONS | Very High | Payroll (salary), Leave (balance init on hire), Notifications, Audit | Circular dependency confirmed with Payroll (PKG_EMPLOYEE calls PKG_PAYROLL.create_salary_record; PKG_PAYROLL calls PKG_EMPLOYEE.is_active). Promotion has no active-status pre-check (contrast with transfer). Three database triggers duplicate some package logic (common Oracle Forms anti-pattern). Dynamic SQL in search_employees creates SQL injection risk |
| Payroll | Core | SALARY_RECORDS, PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS, EMPLOYEE_TAX_INFO, EMPLOYEE_PAY_ELEMENTS, PAY_ELEMENTS | Very High | Employee Management, GL Integration, Notifications, Audit | 2024 tax brackets hard-coded despite TAX_BRACKETS table existing. PAID status in DDL has no implementation. YTD figures on payslip are zero placeholders. Partial commits every 50 employees create half-calculated state on failure |
| Leave Management | Core | LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES, LEAVE_ACCRUAL_LOG, HOLIDAYS | High | Employee Management, Notifications, Audit | Observed holiday logic does not handle observed dates (e.g. Friday substitute for Saturday holiday). Half-day overlap detection is known bug. Carryover expiry: CARRYOVER_EXPIRY column stores months (not days as Agent 1 may have inferred) |
| Performance Management | Supporting | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS | Medium | Employee Management, Notifications, Audit | MEETING_SCHEDULED and CALIBRATION statuses exist in DDL but have no implementation. No SLA or escalation for stalled reviews |
| Security & Access | Cross-Cutting | USER_SESSIONS | Medium | Employee Management (email lookup), Audit | Password verification is a stub — USER_CREDENTIALS table referenced but actual check absent. No account lockout. Session timeout from login time only (no refresh). Encryption key hard-coded in source |
| Notifications | Cross-Cutting | NOTIFICATION_QUEUE | Low | Employee Management (email lookup) | No rate limiting. HTML templates hard-coded as strings. SMTP connection opened and closed per email (no pooling). Notification type SMS and IN_APP defined but only EMAIL is processed |
| Reporting & Integration | Supporting | Views, PKG_REPORTING, PKG_INTEGRATION | Medium | All core domains | Time and attendance import is a non-functional stub. Org structure sync (LDAP) is a non-functional stub. Reporting tables (RPT_*) referenced but not created in provided schema. FTP credentials stored in cleartext in SYSTEM_PARAMETERS |
| Audit & Logging | Cross-Cutting | AUDIT_LOG, SYSTEM_PARAMETERS | Low | None (called by all) | log_info has a JSON quoting bug (no quote escaping). Error logs go to TABLE_NAME='ERROR_LOG' with RECORD_ID=0; info logs to 'INFO_LOG' — these are sentinel values, not real table names |

---

## OUTPUT 7 — Pain Point Report

| # | Pain Point | Domain(s) | Severity | Evidence | Automation Opportunity |
|---|---|---|---|---|---|
| PP-01 | Hire date validation inconsistency: the screen allows dates up to 90 days in the future but the database trigger allows 180 days. Both constraints enforce different limits on the same field, creating confusion and potential data quality issues | Employee Management | High | BR-14 (90 days, form) vs BR-15 (180 days, trigger); DISC-001 | Yes — consolidate to a single enforced rule; remove the redundant check |
| PP-02 | SQL injection vulnerability in employee search: the search function builds queries by concatenating employee names directly into SQL text instead of using parameterised values. Attackers with API access could extract or corrupt data | Employee Management | High | PKG_EMPLOYEE.search_employees — documented in source code comment | Yes — replace string concatenation with bind variables; no business logic change required |
| PP-03 | Payment disbursement is not implemented: payroll runs can be approved but there is no mechanism to send net pay to employees. Three critical integrations are marked as TODO: bank account payments, COBRA benefits notification, and system access revocation on termination | Payroll, Employee Management | High | PKG_EMPLOYEE.terminate_employee TODOs; no payment processing code found | Yes — requires integration with payment processor (ACH/bank) and benefits/IT systems |
| PP-04 | Hard-coded 2024 tax brackets: federal tax rates are embedded directly in the payroll calculation code. Tax year changes require a code deployment rather than a data update. The TAX_BRACKETS table exists and is populated but is not used | Payroll | High | PKG_PAYROLL.calculate_federal_tax — TODO in code to use TAX_BRACKETS table | Yes — migrate calculation to read from TAX_BRACKETS table; update rates annually without code changes |
| PP-05 | Password verification is a stub: the authentication procedure does not actually verify the user's password. The USER_CREDENTIALS table is referenced in comments but the password check code is absent. Users may log in without a valid password | Security & Access | High | PKG_SECURITY.authenticate — password check absent from code | Yes — implement password hash comparison against USER_CREDENTIALS; existing hash_password function using MD5 should also be upgraded to a stronger algorithm |
| PP-06 | Hard-coded encryption key in source code: the AES-256 encryption key for Social Security Numbers is written directly into the package body as a string constant. Anyone with access to the source code has the key | Security & Access | High | PKG_SECURITY — c_encryption_key constant visible in source | Yes — move key to Oracle Wallet or a secure vault; do not store credentials in source code |
| PP-07 | No account lockout after failed login attempts: the system has no protection against repeated failed login attempts. An attacker can try passwords indefinitely without being blocked | Security & Access | High | PKG_SECURITY.authenticate — no attempt counter or lockout logic | Yes — implement failed-attempt counter in USER_SESSIONS or a dedicated table; lock after N failures (typically 5) |
| PP-08 | Session timeout measures from login time, not from last activity: a user who is actively working will be logged out after 30 minutes regardless. A user who walks away from their computer stays logged in for 30 minutes. Neither behaviour is ideal | Security & Access | Medium | PKG_SECURITY.is_session_valid — timeout based on LOGIN_TIME, not last activity | Yes — update last-activity timestamp on each session validation check |
| PP-09 | Payroll partial commit risk: the payroll calculation commits to the database every 50 employees. If the process fails partway through, the run is left in a half-calculated state with some employees processed and others not, requiring manual clean-up | Payroll | Medium | PKG_PAYROLL.calculate_payroll — intermediate COMMITs every 50 rows | Yes — use savepoints and a restart-from-last-commit mechanism, or process in a single transaction with a full rollback on failure |
| PP-10 | Organisation chart times out for large organisations: the hierarchical query used to build the reporting structure is documented to time out for organisations with more than 500 employees | Employee Management | Medium | PKG_EMPLOYEE.get_org_chart — known bug documented in source; VW_ORG_HIERARCHY same warning | Yes — materialise the hierarchy nightly into a flat table; query the flat table instead of running recursive SQL on demand |
| PP-11 | Employee number generation race condition: the system generates employee numbers by finding the current maximum and adding one. Under concurrent user activity, two users could generate the same number simultaneously | Employee Management | Medium | PKG_EMPLOYEE.generate_emp_number — SELECT MAX()+1 without locking; documented as known bug | Yes — use the SEQ_EMPLOYEE sequence exclusively; remove the MAX()+1 logic |
| PP-12 | No SLA on leave approval: managers have no time limit to approve or reject leave requests. Employees may wait indefinitely without knowing whether their leave is approved, preventing them from making firm plans | Leave Management | Medium | No SLA rule found in Business Rules Catalog; Stage 2 of Leave Request Value Stream is an unbounded wait | Yes — configure an escalation reminder notification after N days; auto-escalate to the manager's manager if no response within a set period |
| PP-13 | No SLA on performance review completion: neither the self-assessment stage nor the manager review stage has a time-bound escalation. Reviews can remain stalled indefinitely, reducing the value of the review programme | Performance Management | Medium | No SLA rule found for review stages; SELF_REVIEW_DUE and MANAGER_REVIEW_DUE fields exist in REVIEW_CYCLES but are not checked in any procedure | Yes — add a scheduled job that checks due dates and sends reminder notifications to employees and managers who have not completed their steps |
| PP-14 | Validation drift between client and server: email format and SSN validation are implemented differently in the Oracle Forms client library and in the server-side package. Data that passes one check may fail the other, and records entered via the API bypass client validation entirely | Employee Management | Medium | BR-117, BR-118; HRMS_VALIDATION_LIB vs PKG_COMMON; DISC-006, DISC-007 | Yes — consolidate validation to a single server-side rule; remove or align client-side checks |
| PP-15 | SMTP connection opened per email: the notification processor opens and closes a new SMTP connection for each individual email in the queue. For a batch of 50 emails this creates 50 separate connections, which is slow and places unnecessary load on the mail server | Notifications | Medium | PKG_NOTIFICATION.process_queue — connection per message, no pooling | Yes — open one SMTP connection per batch run; reuse it for all messages in the batch |
| PP-16 | No rate limiting on notifications: bulk operations such as payroll runs, which process hundreds of employees, can add hundreds of notifications to the queue simultaneously. There is no throttle to prevent flooding the mail server | Notifications | Medium | PKG_NOTIFICATION.pks known issues — no rate limiting | Yes — add a rate-limit parameter to the queue processor; or group similar notifications into digest emails |
| PP-17 | Observed holiday dates not handled: the holiday exclusion logic checks only the exact holiday date. When a holiday falls on a weekend, the observed day (e.g. Friday before or Monday after) is not automatically excluded, causing leave day counts and business day calculations to include days the business is actually closed | Leave Management | Low | PKG_LEAVE.calculate_business_days — known bug documented in source | Yes — add an OBSERVED_DATE column to HOLIDAYS or a lookup table for substituted observed dates |
| PP-18 | YTD figures missing from payslips: the year-to-date gross and year-to-date net fields on every payslip are hard-coded to zero. Employees and managers cannot see cumulative pay for the year on the payslip | Payroll | Low | PKG_PAYROLL.get_payslip — YTD_GROSS=0, YTD_NET=0 hardcoded; documented in code | Yes — implement YTD accumulation using the existing get_ytd_earnings function |
| PP-19 | Time and attendance import is non-functional: the file reading scaffolding exists but no data is actually written to the database. Hours data from the time-and-attendance system cannot be imported | Reporting & Integration | Low | PKG_INTEGRATION.import_time_attendance — TODO in code; no INSERT/UPDATE statements | Yes — implement CSV parsing and update EMPLOYEE_HOURS or PAYROLL_DETAILS with the imported hours |
| PP-20 | FTP credentials stored in cleartext: integration credentials (FTP usernames, passwords) are stored as plain text in the SYSTEM_PARAMETERS table. Anyone with SELECT access to that table can see them | Reporting & Integration | High | PKG_INTEGRATION.pks known issue; SYSTEM_PARAMETERS table | Yes — use Oracle Wallet or encrypted credentials storage; remove cleartext secrets from the database |

---

## OUTPUT 8 — Automation Opportunities

| # | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-01 | Automated payroll run initiation | Payroll administrator manually creates and initiates a calculation run each period | DBMS_SCHEDULER job triggers create_payroll_run and calculate_payroll on the scheduled pay date; result queued for human approval review | High — eliminates manual initiation step; reduces risk of missed payroll |
| AO-02 | Tax bracket data management | 2024 federal tax brackets are hard-coded in PL/SQL; a rate change requires a code deployment | Load bracket data into the TAX_BRACKETS table (already in schema); update calculate_federal_tax to read from it; annual updates become a data change not a code change | High — eliminates deployment risk for annual tax rate changes |
| AO-03 | Leave approval escalation | Managers have no deadline to respond; requests can wait indefinitely | Scheduled job checks PENDING requests older than a configurable threshold (e.g. 3 business days); sends reminder to manager; after a second threshold (e.g. 5 days) auto-escalates to the manager's manager | High — eliminates unbounded wait states; improves employee experience |
| AO-04 | Performance review deadline reminders | Self-review and manager-review due dates are stored but never checked | Scheduled job compares today against SELF_REVIEW_DUE and MANAGER_REVIEW_DUE in REVIEW_CYCLES; sends targeted reminders to employees or managers who have not yet completed their step | Medium — reduces reviews stalled at intermediate stages; improves cycle completion rate |
| AO-05 | Year-end leave carryover and expiry | process_carryover and expire_carryover procedures exist but must be manually triggered | DBMS_SCHEDULER job runs process_carryover on December 31 and expire_carryover on the first day of each month | Medium — eliminates risk of manual omission; ensures consistent year-end processing |
| AO-06 | Monthly leave accrual | run_monthly_accrual is designed for scheduled execution but scheduling is not confirmed in provided code | DBMS_SCHEDULER job on the 1st of each month calling run_monthly_accrual | Medium — ensures consistent, timely accrual credits |
| AO-07 | GL journal automatic delivery | GL journal file is written to a directory; actual delivery to Oracle Financials requires a separate file transfer not implemented in HRMS | Add a file transfer step (UTL_FILE + DBMS_SCHEDULER or Oracle Integration Cloud) to move the file to the Financials import drop zone after generation | Medium — removes a manual handoff; reduces payroll-to-GL latency |
| AO-08 | Notification SMTP connection pooling | Each email opens a new SMTP connection, one per message | Refactor process_queue to open one connection, send all messages in the batch, then close | Low-Medium — improves notification throughput; reduces mail server load |
| AO-09 | Employee search SQL injection fix | search_employees uses string concatenation for name parameters | Replace string concatenation with bind variables using OPEN cursor FOR v_sql USING syntax | High (security) — eliminates injection vector; no business logic change |
| AO-10 | Org chart materialisation | Recursive hierarchy query times out for 500+ employees | Nightly job materialises the hierarchy into a flat RPT_ORG_HIERARCHY table; forms and reports query the flat table | Medium — resolves known performance issue; enables instant org chart display |

---

## ⚠️ Validation Queue

| ID | Domain | Item | Reason for Uncertainty |
|---|---|---|---|
| VQ-OPEN-01 | Payroll | PAID status in PAYROLL_RUNS DDL has no transition procedure. It is unclear whether this status is set externally, by a process not in scope, or is simply unused | ⚠️ LOW — no SET STATUS='PAID' statement found in any package |
| VQ-OPEN-02 | Performance | MEETING_SCHEDULED status exists in PERFORMANCE_REVIEWS DDL but no code sets it. May be a planned feature not yet implemented | ⚠️ LOW — status defined, no transition logic |
| VQ-OPEN-03 | Performance | CALIBRATION and IN_PROGRESS statuses exist in REVIEW_CYCLES DDL but only DRAFT → OPEN and OPEN → CLOSED transitions are coded | ⚠️ LOW — partial implementation |
| VQ-OPEN-04 | Security | Password verification in PKG_SECURITY.authenticate appears incomplete. USER_CREDENTIALS table is referenced in comments but not in the executable body. It is unknown whether this is an intentional omission, a separate package, or a genuine implementation gap | ⚠️ LOW — security-critical gap; requires human review |
| VQ-OPEN-05 | Payroll | TOTAL_EMPLOYER_COST column exists in PAYROLL_RUNS but is never populated by any procedure in the provided code | ⚠️ LOW — column present, no write path found |
| VQ-OPEN-06 | Integration | RPT_* reporting tables are referenced in PKG_REPORTING.refresh_reporting_tables comments as a nightly denormalisation target but are not defined in the schema scripts provided | ⚠️ LOW — referenced but not found |
| VQ-OPEN-07 | Notifications | SMS and IN_APP notification types are defined in the NOTIFICATION_QUEUE DDL but only EMAIL is processed by process_queue | ⚠️ LOW — defined but unimplemented |
| VQ-OPEN-08 | Leave | The TAKEN status for leave requests is defined in the DDL. No procedure in PKG_LEAVE sets status to TAKEN. It may be set by a forms trigger, a batch job, or a missing procedure | ⚠️ LOW — status defined, no write path found in packages |
| VQ-OPEN-09 | Employee | The ACTIVE_FLAG on employees is set to 'N' on termination. However, VW_ACTIVE_EMPLOYEES filters on both EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y'. It is unclear whether ON_LEAVE and SUSPENDED employees have ACTIVE_FLAG = 'Y' or 'N' — the code only explicitly sets it to 'N' at termination | ⚠️ LOW — inconsistency between flag and status |
| VQ-OPEN-10 | Security | PKG_SECURITY.change_password validates the new password and calls PKG_AUDIT.log_action but does not contain a write to USER_CREDENTIALS. The actual password storage step is absent | ⚠️ LOW — stub implementation; security gap |

---

## 📋 Agent 1 Discrepancy Log

| ID | Agent 1 Statement | What Deep Analysis Found | Status |
|---|---|---|---|
| DISC-001 | Hire date validation limit | Agent 1 did not flag a conflict. Form enforces 90-day future limit; database trigger enforces 180-day limit. Two different values apply to the same field | ⚠️ UNRESOLVED — both rules exist; which is intended is unclear |
| DISC-002 | promote_employee active-status check | Agent 1 did not flag this gap. transfer_employee checks ACTIVE status; promote_employee does not. Employees can be promoted while SUSPENDED or ON_LEAVE | ⚠️ UNRESOLVED — likely an oversight; business intent unclear |
| DISC-003 | EMPLOYEE_HISTORY table structure | TRG_EMP_BEFORE_UPDATE inserts using columns CHANGE_DATE, OLD_VALUE, NEW_VALUE (VARCHAR2). The DDL defines EFFECTIVE_DATE and typed old/new columns. The trigger references a different column structure than the DDL | ⚠️ UNRESOLVED — trigger will fail at runtime if column names do not match; may indicate the trigger references a different version of the table |
| DISC-004 | VW_LEAVE_SUMMARY AVAILABLE formula | View calculates AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT (does not subtract PENDING). The LEAVE_BALANCES virtual column includes PENDING in its formula. Two different definitions of "available balance" exist in the same system | ⚠️ UNRESOLVED — users of the view will see a higher available balance than is accurate |
| DISC-005 | No active check on promotion | Agent 1 noted transfer requires ACTIVE status. Deep analysis confirmed promotion has no such check — discrepancy is real | ⚠️ UNRESOLVED |
| DISC-006 | Email validation divergence | Client-side (forms library) and server-side (PKG_COMMON) validate email differently. Server-side accepts subdomains; client-side rejects them | ⚠️ UNRESOLVED — same email can be valid in API calls and invalid in the form |
| DISC-007 | SSN validation divergence | Client-side checks for all-zero segments; server-side does not | ⚠️ UNRESOLVED — an SSN with all-zero area code (e.g. 000-XX-XXXX) passes server check but fails client check |
| DISC-008 | DEPT_ID=30 manager double-update | Seed data updates DEPARTMENTS.MANAGER_EMP_ID for DEPT_ID=30 twice: first to EMP_ID=3 (CIO Michael O'Connor), then immediately to EMP_ID=30 (Director Rachel Thompson). Final value is EMP_ID=30 | ✅ RESOLVED — final effective value is EMP_ID=30; first UPDATE is redundant |
| DISC-009 | reverse_payroll reason parameter not stored | PKG_PAYROLL.reverse_payroll accepts a p_reason parameter but does not store it anywhere. The reversal reason is lost | ⚠️ UNRESOLVED — compliance risk; reversal reasons should be auditable |

---

✅ Agent 2 Analysis Complete.
Documentation is ready for business review.
Highest-priority validation item: VQ-OPEN-04 — Password verification in the authentication function appears to be a non-functional stub. Users may be able to log in without supplying a correct password. This requires immediate confirmation with the development team before the system is used in a production environment.
