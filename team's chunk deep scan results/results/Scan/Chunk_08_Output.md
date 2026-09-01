=== CHUNK METADATA ===
Chunk: 08            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-body
Expected files (1):
  1. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb (22361 chars written)
Total source content: 34342 characters (budget: 30000)  (over budget — a single large file couldn't be split)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: leave management — request submission/approval workflow, balance tracking, monthly accrual, and year-end carryover for HRMS employees

**STRUCTURES:**
  None (all declared items — v_count, v_date, v_request, v_balance, etc. — are local variables scoped to individual procedures/functions; the t_leave_cursor type used in OUT parameters is declared in the package spec, not this body)

**METHODS:**

**FUNCTION calculate_business_days(p_start_date IN DATE, p_end_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN NUMBER** [SOURCE: L12-43]
- What it does: Called by submit_leave_request to size a non-half-day request. Walks each calendar date from p_start_date to p_end_date; skips Saturdays/Sundays; for remaining days, counts it as a business day only if no active HOLIDAYS row matches that date for the given location (or a global, location-independent holiday).
- Business rules: Only holidays with ACTIVE_FLAG = 'Y' are excluded from the count; inactive/retired holidays are ignored. A holiday with LOCATION_CODE IS NULL applies globally to all locations. KNOWN BUG (per source comment): does not handle "observed" holidays — e.g., if July 4 falls on a Saturday, the observed Friday is not excluded.
- Numbers & thresholds: None (no numeric literals; weekend detection uses day-name strings 'SAT'/'SUN', not numbers).
- Security & error handling: None — no input validation on the date range or location code.
- Data in/out: Inputs — p_start_date, p_end_date (required DATE), p_location_code (optional VARCHAR2). Reads HOLIDAYS. Output — returns NUMBER count of business days.

**FUNCTION check_leave_overlap(p_emp_id IN NUMBER, p_start_date IN DATE, p_end_date IN DATE, p_exclude_request_id IN NUMBER DEFAULT NULL) RETURN BOOLEAN** [SOURCE: L48-68]
- What it does: Called by submit_leave_request. Counts existing LEAVE_REQUESTS for the employee whose status is PENDING or APPROVED and whose date range overlaps [p_start_date, p_end_date], optionally excluding one request id (used when re-checking during edits).
- Business rules: An employee's date range conflicts only against requests in PENDING or APPROVED status; CANCELLED and REJECTED requests never block new submissions.
- Numbers & thresholds: None.
- Security & error handling: None.
- Data in/out: Inputs — p_emp_id, p_start_date, p_end_date (required), p_exclude_request_id (optional). Reads LEAVE_REQUESTS. Output — returns TRUE if v_count > 0, else FALSE.

**FUNCTION submit_leave_request(p_emp_id IN NUMBER, p_leave_type_id IN NUMBER, p_start_date IN DATE, p_end_date IN DATE, p_half_day_flag IN CHAR DEFAULT 'N', p_half_day_period IN VARCHAR2 DEFAULT NULL, p_reason IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L73-254]
- What it does: Entry point for creating a leave request. Validates the employee is ACTIVE, validates the leave type is active, checks minimum tenure, validates the date range, computes total business days (or 0.5 for half-day), checks for overlapping requests, checks balance for accrual-based leave types, inserts the LEAVE_REQUESTS row (PENDING or APPROVED depending on whether approval is required), updates the PENDING column on LEAVE_BALANCES, notifies the manager by email if approval is required, auto-approves via approve_leave_request if not, and logs the insert via PKG_AUDIT.
- Business rules: Employee must exist and have EMPLOYMENT_STATUS = 'ACTIVE' [L92-97,101]. Leave type must exist and have ACTIVE_FLAG = 'Y' [L106-111,115]. If the leave type has MIN_TENURE_DAYS > 0, the employee's tenure (SYSDATE - HIRE_DATE) must meet or exceed it, else rejected [L121-129] (comment example only, illustrative: "e.g., parental leave after 90 days" — 90 is not itself a hardcoded threshold in this file; MIN_TENURE_DAYS is data-driven from LEAVE_TYPES). Start date must not be after end date [L134-137]. Backdated requests are allowed only up to a fixed number of days in the past [L141-151]. Half-day requests are always counted as exactly 0.5 days regardless of the date range [L156-157]. Non-half-day requests must span at least one business day after excluding weekends/holidays, else rejected [L165-169]. Requests cannot overlap an existing PENDING/APPROVED request for the same employee [L174-179]. Balance is checked only for accrual-based leave types (ACCRUAL_FLAG = 'Y'); non-accrual types (e.g., unpaid leave) skip the balance check [L185-194]. Requests for leave types requiring approval (REQUIRES_APPROVAL = 'Y') are created as PENDING and routed to the employee's manager; otherwise created as APPROVED and auto-approved immediately [L213,230,247-249]. Manager notification is sent only if a manager is assigned AND the leave type requires approval [L230].
- Numbers & thresholds: Backdating limit = 5 days (`TRUNC(SYSDATE) - p_start_date > 5` at L145, restated in error message "Cannot submit leave requests more than 5 days in the past" at L149). Half-day duration = 0.5 days (L157). Minimum valid total days = 0 (v_total_days <= 0 rejected, L165). Comment-only illustrative figure: 90 days ("e.g., parental leave after 90 days", L120) — not an enforced literal in this file, the actual threshold comes from LEAVE_TYPES.MIN_TENURE_DAYS. Error codes: -20001 (employee not found/not active), -20203 (invalid leave type; also reused for minimum-tenure-not-met), -20210 (start date after end date), -20211 (backdate > 5 days), -20212 (no business days in range), -20202 (overlapping request), -20201 (insufficient balance).
- Security & error handling: RAISE_APPLICATION_ERROR on: employee not found/inactive (-20001), invalid/inactive leave type (-20203), tenure not met (-20203), start>end date (-20210), backdate >5 days (-20211), zero business days (-20212), overlapping request (-20202), insufficient balance (-20201). No explicit SQL-injection surface (bind variables only); p_user defaults to session USER.
- Data in/out: Inputs — p_emp_id, p_leave_type_id, p_start_date, p_end_date (required); p_half_day_flag, p_half_day_period, p_reason, p_user (optional, p_user defaults to USER). Reads EMPLOYEES, LEAVE_TYPES; calls calculate_business_days and check_leave_overlap. Writes LEAVE_REQUESTS (INSERT), LEAVE_BALANCES (UPDATE PENDING). Output — returns new REQUEST_ID (from SEQ_LEAVE_REQUEST.NEXTVAL); side effects: possible email notification and auto-approval, audit log entry.

**PROCEDURE approve_leave_request(p_request_id IN NUMBER, p_approver_emp_id IN NUMBER, p_comments IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L259-313]
- What it does: Called by submit_leave_request (auto-approve path) or directly by an approver. Locks the LEAVE_REQUESTS row (FOR UPDATE), verifies it is PENDING, sets it to APPROVED with approver/comments/date, moves the request's TOTAL_DAYS from PENDING to USED on LEAVE_BALANCES, emails the employee, and logs the update via PKG_AUDIT.
- Business rules: Only a request currently in PENDING status can be approved; any other status is rejected [L274-278].
- Numbers & thresholds: Error code -20204 ("Cannot approve request in status: ...").
- Security & error handling: RAISE_APPLICATION_ERROR -20204 if status is not PENDING. Row is locked with FOR UPDATE to prevent concurrent approve/reject/cancel races.
- Data in/out: Inputs — p_request_id (required), p_approver_emp_id, p_comments, p_user (p_user defaults to USER). Reads/locks LEAVE_REQUESTS. Writes LEAVE_REQUESTS (UPDATE), LEAVE_BALANCES (UPDATE PENDING/USED). Output — none (procedure); side effects: email notification, audit log entry.

**PROCEDURE reject_leave_request(p_request_id IN NUMBER, p_approver_emp_id IN NUMBER, p_comments IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L318-367]
- What it does: Locks the LEAVE_REQUESTS row, verifies it is PENDING, sets it to REJECTED with approver/comments/date, releases the PENDING balance reservation on LEAVE_BALANCES, emails the employee with the rejection reason, and logs the update via PKG_AUDIT.
- Business rules: Only a request currently in PENDING status can be rejected; approved/cancelled/already-rejected requests cannot be rejected again [L333-337].
- Numbers & thresholds: Error code -20204 ("Cannot reject request in status: ...").
- Security & error handling: RAISE_APPLICATION_ERROR -20204 if status is not PENDING. Row locked with FOR UPDATE.
- Data in/out: Inputs — p_request_id, p_approver_emp_id, p_comments (required), p_user (defaults to USER). Reads/locks LEAVE_REQUESTS. Writes LEAVE_REQUESTS (UPDATE), LEAVE_BALANCES (UPDATE PENDING). Output — none; side effects: email notification, audit log entry.

**PROCEDURE cancel_leave_request(p_request_id IN NUMBER, p_reason IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L372-425]
- What it does: Locks the LEAVE_REQUESTS row, verifies it is PENDING or APPROVED, sets it to CANCELLED with reason/date, and restores the balance: if it had been PENDING, releases the PENDING reservation; if APPROVED, credits the days back by reducing USED. Logs the update via PKG_AUDIT.
- Business rules: Only requests in PENDING or APPROVED status can be cancelled; REJECTED/CANCELLED/TAKEN requests cannot be cancelled [L387-391]. Cancelling a PENDING request releases the reserved PENDING balance [L404-411]; cancelling an APPROVED request credits back the USED balance [L412-421].
- Numbers & thresholds: Error code -20204 ("Cannot cancel request in status: ...").
- Security & error handling: RAISE_APPLICATION_ERROR -20204 if status is not PENDING/APPROVED. Row locked with FOR UPDATE.
- Data in/out: Inputs — p_request_id, p_reason (required), p_user (defaults to USER). Reads/locks LEAVE_REQUESTS. Writes LEAVE_REQUESTS (UPDATE), LEAVE_BALANCES (UPDATE PENDING or USED). Output — none; side effect: audit log entry (no employee notification in this procedure).

**FUNCTION get_leave_balance(p_emp_id IN NUMBER, p_leave_type_id IN NUMBER, p_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER** [SOURCE: L430-450]
- What it does: Called by run_monthly_accrual (and available generally). Computes available balance as OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING from LEAVE_BALANCES for the given employee/leave type/year.
- Business rules: A NULL computed result is treated as 0 available days rather than an error [L446]. If no LEAVE_BALANCES row exists (NO_DATA_FOUND), returns 0 rather than raising [L448-449].
- Numbers & thresholds: Default fallback value = 0 (both NVL(v_balance,0) and the NO_DATA_FOUND handler).
- Security & error handling: NO_DATA_FOUND is caught and suppressed (returns 0); no other error handling.
- Data in/out: Inputs — p_emp_id, p_leave_type_id (required), p_year (optional, defaults to current year). Reads LEAVE_BALANCES. Output — returns NUMBER balance (never NULL).

**PROCEDURE adjust_leave_balance(p_emp_id IN NUMBER, p_leave_type_id IN NUMBER, p_adjustment IN NUMBER, p_reason IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L455-485]
- What it does: Adds p_adjustment to the ADJUSTMENT column of the current-year LEAVE_BALANCES row for the employee/leave type. If no row exists (SQL%ROWCOUNT = 0), calls initialize_balances to create rows for the year and retries the update. Logs the change via PKG_AUDIT.
- Business rules: If no balance record exists for the employee/leave type/current year, one is created via initialize_balances before the adjustment is applied [L471-482].
- Numbers & thresholds: None beyond the caller-supplied p_adjustment value itself.
- Security & error handling: None explicit; p_reason is accepted but not persisted anywhere in this procedure body shown.
- Data in/out: Inputs — p_emp_id, p_leave_type_id, p_adjustment, p_reason (required), p_user (defaults to USER). Writes LEAVE_BALANCES (UPDATE ADJUSTMENT); may trigger initialize_balances (INSERT into LEAVE_BALANCES). Output — none; side effect: audit log entry.

**PROCEDURE initialize_balances(p_emp_id IN NUMBER, p_year IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L491-518]
- What it does: For every leave type with ACTIVE_FLAG = 'Y', inserts a new LEAVE_BALANCES row for the employee/year with all balance columns initialized to zero; silently skips any leave type that already has a row (DUP_VAL_ON_INDEX).
- Business rules: Balance records are created only for currently active leave types (ACTIVE_FLAG = 'Y'); inactive leave types are excluded [L500-501]. Duplicate rows are silently ignored rather than erroring [L513-515].
- Numbers & thresholds: All five balance columns (OPENING_BALANCE, ACCRUED, USED, ADJUSTMENT, PENDING) are initialized to 0 (L510).
- Security & error handling: DUP_VAL_ON_INDEX exception is caught per leave type and suppressed (NULL) so one duplicate doesn't abort the loop.
- Data in/out: Inputs — p_emp_id, p_year (required), p_user (defaults to USER). Reads LEAVE_TYPES. Writes LEAVE_BALANCES (INSERT, BALANCE_ID from SEQ_LEAVE_BALANCE.NEXTVAL). Output — none.

**PROCEDURE run_monthly_accrual(p_accrual_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L525-630]
- What it does: Batch job (typically scheduled via DBMS_SCHEDULER on the 1st of each month). For every employee with EMPLOYMENT_STATUS = 'ACTIVE' and ACTIVE_FLAG = 'Y', and for every leave type that is active, ACCRUAL_FLAG = 'Y', and ACCRUAL_FREQUENCY = 'MONTHLY', checks tenure, computes the accrual amount capped at MAX_BALANCE, updates LEAVE_BALANCES.ACCRUED (initializing the balance row first if missing), logs the accrual to LEAVE_ACCRUAL_LOG, and commits periodically and at the end.
- Business rules: Accrual runs only for employees who are both EMPLOYMENT_STATUS = 'ACTIVE' and ACTIVE_FLAG = 'Y' [L542-543]. Only leave types that are ACTIVE_FLAG = 'Y', ACCRUAL_FLAG = 'Y', and ACCRUAL_FREQUENCY = 'MONTHLY' are processed [L554-556]. An employee must have been employed at least MIN_TENURE_DAYS (from LEAVE_TYPES) as of the accrual date to accrue that leave type [L561]. If MAX_BALANCE is NULL, the full ACCRUAL_RATE is applied; otherwise accrual is capped so the balance does not exceed MAX_BALANCE — accrual amount is GREATEST(0, MAX_BALANCE - current balance) when the full rate would breach the cap [L573-578]. If the UPDATE affects no rows, the balance is initialized via initialize_balances and the accrual is applied via a second UPDATE (overwriting ACCRUED to v_accrued rather than adding) [L590-601].
- Numbers & thresholds: Commit batch size = every 100 employees (`MOD(v_total_employees, 100) = 0` at L621), plus a final COMMIT at the end (L626). Accrual floor = 0 (GREATEST(0, ...) at L577). Initial counters v_accrued, v_total_employees, v_total_accrued all start at 0 (L529-531). ACCRUAL_RATE and MAX_BALANCE values themselves are data-driven from LEAVE_TYPES, not literals in this file.
- Security & error handling: None explicit (no exception handling shown around the per-employee/per-leave-type loop body); DBMS_OUTPUT.PUT_LINE used for start/end progress logging only.
- Data in/out: Inputs — p_accrual_date (defaults to SYSDATE), p_user (defaults to USER). Reads EMPLOYEES, LEAVE_TYPES; calls get_leave_balance, initialize_balances. Writes LEAVE_BALANCES (UPDATE ACCRUED), LEAVE_ACCRUAL_LOG (INSERT, ACCRUAL_ID from SEQ_LEAVE_ACCRUAL.NEXTVAL). Output — none; side effects: periodic and final COMMIT, console output via DBMS_OUTPUT.

**PROCEDURE process_carryover(p_year IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L636-689]
- What it does: Year-end batch job. For every LEAVE_BALANCES row in p_year with a positive remaining balance (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT > 0), caps the remaining amount at the leave type's CARRYOVER_MAX (if set), initializes the next year's balance row, and sets CARRYOVER_FROM_PREV / OPENING_BALANCE to the carryover amount, with an optional CARRYOVER_EXPIRY_DT computed from the leave type's CARRYOVER_EXPIRY (in months). Commits at the end.
- Business rules: Only employees with a positive remaining balance at year-end are eligible for carryover; zero/negative balances are excluded [L646-653]. When a leave type defines a CARRYOVER_MAX, any unused balance above that ceiling is forfeited [L660-662]. Carried-over days get an expiry date only if the leave type specifies CARRYOVER_EXPIRY (months); otherwise they never expire [L672-679].
- Numbers & thresholds: Next year = p_year + 1 (L640). Carryover expiry base date is hardcoded to January 1 of next year via string literal '-01-01' concatenated as `TO_DATE(v_next_year || '-01-01', 'YYYY-MM-DD')` (L677), then advanced by CARRYOVER_EXPIRY months (data-driven from LEAVE_TYPES). CARRYOVER_MAX itself is data-driven, not a literal in this file.
- Security & error handling: None explicit.
- Data in/out: Inputs — p_year (required), p_user (defaults to USER). Reads LEAVE_BALANCES joined to LEAVE_TYPES; calls initialize_balances. Writes LEAVE_BALANCES (UPDATE CARRYOVER_FROM_PREV, OPENING_BALANCE, CARRYOVER_EXPIRY_DT for next year). Output — none; side effect: COMMIT.

**PROCEDURE expire_carryover(p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L696-712]
- What it does: For every LEAVE_BALANCES row whose CARRYOVER_EXPIRY_DT has passed (<= TRUNC(SYSDATE)) and whose CARRYOVER_FROM_PREV is still positive, deducts CARRYOVER_FROM_PREV from ADJUSTMENT and zeroes CARRYOVER_FROM_PREV. Commits.
- Business rules: Only rows with an expired CARRYOVER_EXPIRY_DT and a positive CARRYOVER_FROM_PREV are affected [L708-709]. KNOWN BUG (per source comment): if run twice on the same day, can double-subtract, since the first run already zeroes CARRYOVER_FROM_PREV but if run before that commit is visible/twice in same transaction window it could re-deduct.
- Numbers & thresholds: Threshold for "still has unexpired carryover to forfeit" = CARRYOVER_FROM_PREV > 0 (L709); reset value = 0 (L705).
- Security & error handling: None.
- Data in/out: Inputs — p_user (defaults to USER). Writes LEAVE_BALANCES (UPDATE ADJUSTMENT, CARRYOVER_FROM_PREV). Output — none; side effect: COMMIT.

**PROCEDURE get_pending_requests(p_cursor OUT t_leave_cursor, p_approver_id IN NUMBER)** [SOURCE: L717-737]
- What it does: Opens p_cursor as a REF CURSOR over LEAVE_REQUESTS joined to EMPLOYEES and LEAVE_TYPES, filtered to STATUS = 'PENDING' and APPROVER_EMP_ID = p_approver_id, ordered by CREATED_DATE.
- Business rules: Only PENDING requests assigned to the specified approver are returned; other statuses or other approvers' requests are excluded [L734-735].
- Numbers & thresholds: None.
- Security & error handling: None — no check that p_approver_id is a valid/authorized approver beyond the WHERE filter.
- Data in/out: Inputs — p_approver_id (required). Reads LEAVE_REQUESTS, EMPLOYEES, LEAVE_TYPES. Output — p_cursor (OUT REF CURSOR) with REQUEST_ID, EMP_ID, EMPLOYEE_NAME, LEAVE_TYPE_NAME, START_DATE, END_DATE, TOTAL_DAYS, REASON, CREATED_DATE.

**PROCEDURE get_team_calendar(p_cursor OUT t_leave_cursor, p_manager_id IN NUMBER, p_start_date IN DATE, p_end_date IN DATE)** [SOURCE: L742-765]
- What it does: Opens p_cursor as a REF CURSOR over LEAVE_REQUESTS joined to EMPLOYEES and LEAVE_TYPES, filtered to direct reports of p_manager_id whose STATUS is APPROVED or TAKEN and whose date range overlaps [p_start_date, p_end_date], ordered by START_DATE then LAST_NAME.
- Business rules: Only APPROVED or TAKEN leave is shown on the team calendar; PENDING and REJECTED requests are excluded [L761].
- Numbers & thresholds: None.
- Security & error handling: None — no check that p_manager_id is a valid/authorized manager beyond the WHERE filter.
- Data in/out: Inputs — p_manager_id, p_start_date, p_end_date (required). Reads LEAVE_REQUESTS, EMPLOYEES, LEAVE_TYPES. Output — p_cursor (OUT REF CURSOR) with EMP_ID, EMPLOYEE_NAME, LEAVE_TYPE_NAME, LEAVE_TYPE_CODE, START_DATE, END_DATE, TOTAL_DAYS, STATUS, HALF_DAY_FLAG.

**DEPENDENCIES:**
  Data touched:
  - Reads: HOLIDAYS — active holiday dates for business-day calculation
  - Reads: LEAVE_REQUESTS — overlap checks, pending/team-calendar queries, row locking for approve/reject/cancel
  - Reads: EMPLOYEES — employee active status, hire date, location code, manager id
  - Reads: LEAVE_TYPES — leave type config (active flag, accrual flag/rate/frequency, min tenure, max balance, carryover max/expiry, requires-approval)
  - Reads: LEAVE_BALANCES — current balance components for get_leave_balance and process_carryover
  - Reads: DUAL — sequence value selects (SEQ_LEAVE_REQUEST.NEXTVAL)
  - Writes: LEAVE_REQUESTS — INSERT on submit; UPDATE on approve/reject/cancel
  - Writes: LEAVE_BALANCES — UPDATE PENDING/USED/ACCRUED/ADJUSTMENT/OPENING_BALANCE/CARRYOVER_FROM_PREV/CARRYOVER_EXPIRY_DT; INSERT via initialize_balances
  - Writes: LEAVE_ACCRUAL_LOG — INSERT per accrual applied in run_monthly_accrual

  CALLS: calculate_business_days | EVIDENCE: OBSERVED | SOURCE: L159
  CALLS: check_leave_overlap | EVIDENCE: OBSERVED | SOURCE: L174
  CALLS: approve_leave_request | EVIDENCE: OBSERVED | SOURCE: L248
  CALLS: PKG_NOTIFICATION.send_notification | EVIDENCE: OBSERVED | SOURCE: L231
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L251
  CALLS: PKG_NOTIFICATION.send_notification | EVIDENCE: OBSERVED | SOURCE: L301
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L312
  CALLS: PKG_NOTIFICATION.send_notification | EVIDENCE: OBSERVED | SOURCE: L358
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L366
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L424
  CALLS: initialize_balances | EVIDENCE: OBSERVED | SOURCE: L473
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L484
  CALLS: get_leave_balance | EVIDENCE: OBSERVED | SOURCE: L566
  CALLS: initialize_balances | EVIDENCE: OBSERVED | SOURCE: L592
  CALLS: initialize_balances | EVIDENCE: OBSERVED | SOURCE: L666
  CALLS: DBMS_OUTPUT.PUT_LINE | EVIDENCE: OBSERVED | SOURCE: L533
  CALLS: DBMS_SCHEDULER | EVIDENCE: INFERRED | SOURCE: L523

  Config/env: None
  External integrations: None

**GAPS:**
  t_leave_cursor type definition is not visible in this file (declared in the package spec, PKG_LEAVE.pks) — NOT_ANALYZED here. Whether run_monthly_accrual/process_carryover/expire_carryover are actually wired into DBMS_SCHEDULER jobs is UNKNOWN from this file alone (comment states "typically scheduled" but no scheduler DDL is present). PKG_NOTIFICATION and PKG_AUDIT internals are EXTERNAL to this file.

*[pipeline status — type: plsql-body · pass: correction · attempt: 2 · coverage: 100% (numbers 14/14 · procedures 14/14 · units 14/14 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 1
Files delivered: 1
  Full coverage on first pass: 0
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb
  Still incomplete after max attempts: 0
Raw source: 34342 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===