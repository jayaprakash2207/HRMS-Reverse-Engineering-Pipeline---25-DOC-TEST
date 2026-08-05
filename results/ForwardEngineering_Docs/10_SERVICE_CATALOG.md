Looking at the source code, `g_debug_mode` appears in two locations in `PKG_EMPLOYEE.pkb` — the `create_employee` salary check and the `log_history` exception handler — but its declaration is not in the visible portion of the package body. I'll document what is confirmed from source and note the inference boundary.

Here is the complete updated document section:

---

## PACKAGE: PKG_LEAVE
**Domain:** BC-03 Leave Management
**Schema:** HRMS
**Dependencies:** PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON
**Tables Owned:** LEAVE_REQUESTS, LEAVE_BALANCES
**Tables Read:** EMPLOYEES, LEAVE_TYPES

| Procedure / Function | Signature | Returns | Description | Defects |
|---|---|---|---|---|
| submit_leave_request | p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_days_requested NUMBER, p_reason VARCHAR2 | p_request_id OUT NUMBER | Validates eligibility (status, tenure, balance); inserts LEAVE_REQUESTS (PENDING); updates LEAVE_BALANCES.PENDING | None confirmed |
| approve_leave | p_request_id NUMBER, p_approver_id NUMBER | — | Updates LEAVE_REQUESTS.STATUS='APPROVED'; updates LEAVE_BALANCES.USED+=days, PENDING-=days; sends LEAVE_APPROVED notification | None |
| reject_leave | p_request_id NUMBER, p_approver_id NUMBER, p_notes VARCHAR2 | — | Updates STATUS='REJECTED'; decrements LEAVE_BALANCES.PENDING | None |
| cancel_leave | p_request_id NUMBER | — | Updates STATUS='CANCELLED'; decrements LEAVE_BALANCES.PENDING; decrements USED if already approved | None |
| accrue_leave | p_accrual_date DATE | p_records_processed OUT NUMBER | Monthly accrual: cursors ACTIVE employees with accruing leave types; adds 1.25 (PTO) or 0.833 (SICK) days; prevents double-accrual via LAST_ACCRUAL_DATE | None |
| get_leave_balance | p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER | SYS_REFCURSOR | Returns balance summary | None |

[GAP-FILLED] **CORRECTIONS AND ADDITIONS — PKG_LEAVE.pkb now confirmed (recovered from file_cache.json):**

The procedure/function table above contains several signature and naming errors. The confirmed source establishes the following:

**Corrected procedure/function table (confirmed from source):**

| Procedure / Function | Signature (confirmed) | Returns | Description | Defects |
|---|---|---|---|---|
| calculate_business_days | p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL | NUMBER | Counts weekdays between two dates, looping day-by-day; excludes weekends (SAT/SUN via NLS_DATE_LANGUAGE=AMERICAN) and active holidays from HOLIDAYS table matching LOCATION_CODE | **BUG confirmed in source comment:** does not handle "observed" holidays (e.g. if July 4 falls on Saturday, the observed Friday is not excluded) |
| check_leave_overlap | p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL | BOOLEAN | Queries LEAVE_REQUESTS for PENDING or APPROVED rows overlapping the given date range for the employee; returns TRUE if overlap exists | None |
| submit_leave_request | p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_half_day_flag CHAR DEFAULT 'N', p_half_day_period VARCHAR2 DEFAULT NULL, p_reason VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER (request_id) | Validates active employee; validates leave type (ACTIVE_FLAG='Y'); checks MIN_TENURE_DAYS; validates dates (start ≤ end; backdates capped at 5 days); calculates business days via calculate_business_days (0.5 if half-day); checks overlap via check_leave_overlap; checks balance via get_leave_balance if ACCRUAL_FLAG='Y'; inserts LEAVE_REQUESTS; updates LEAVE_BALANCES.PENDING; notifies manager via PKG_NOTIFICATION if REQUIRES_APPROVAL='Y'; auto-approves via approve_leave_request if REQUIRES_APPROVAL='N'; calls PKG_AUDIT | -20001 invalid employee; -20201 insufficient balance; -20202 overlap; -20203 invalid leave type or tenure not met; -20210 date order; -20211 backdate > 5 days; -20212 zero business days |
| approve_leave_request | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — | SELECT FOR UPDATE on LEAVE_REQUESTS; validates STATUS='PENDING'; sets STATUS='APPROVED', APPROVER_EMP_ID, APPROVAL_DATE, APPROVAL_COMMENTS; decrements LEAVE_BALANCES.PENDING and increments LEAVE_BALANCES.USED; notifies employee via PKG_NOTIFICATION; calls PKG_AUDIT | -20204 if status != PENDING |
| reject_leave_request | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER | — | SELECT FOR UPDATE on LEAVE_REQUESTS; validates STATUS='PENDING'; sets STATUS='REJECTED', APPROVER_EMP_ID, APPROVAL_DATE, APPROVAL_COMMENTS; decrements LEAVE_BALANCES.PENDING (releases held balance); notifies employee via PKG_NOTIFICATION; calls PKG_AUDIT | -20204 if status != PENDING |
| cancel_leave_request | p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — | SELECT FOR UPDATE on LEAVE_REQUESTS; validates STATUS IN ('PENDING','APPROVED'); sets STATUS='CANCELLED', CANCEL_REASON, CANCELLED_DATE; if was PENDING: decrements LEAVE_BALANCES.PENDING; if was APPROVED: decrements LEAVE_BALANCES.USED; calls PKG_AUDIT | -20204 if status not PENDING or APPROVED |
| get_leave_balance | p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER | Returns OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING from LEAVE_BALANCES; returns 0 if no row found (NO_DATA_FOUND handled) | None |

[GAP-FILLED] **Naming discrepancies vs. original table:**

| Original name | Confirmed name | Notes |
|---|---|---|
| `approve_leave` | `approve_leave_request` | Different procedure name |
| `reject_leave` | `reject_leave_request` | Different procedure name |
| `cancel_leave` | `cancel_leave_request` | Different procedure name |
| `submit_leave_request` | `submit_leave_request` | Name matches; signature differs — no `p_days_requested` parameter; actual signature uses `p_half_day_flag`/`p_half_day_period`; returns NUMBER directly (not OUT param) |
| `get_leave_balance` | `get_leave_balance` | Name matches; returns NUMBER, not SYS_REFCURSOR |
| `accrue_leave` | **NOT CONFIRMED** | Not present in the sourced PKG_LEAVE.pkb — may be in an unreviewed package (PKG_ACCRUALS, PKG_SCHEDULER) or not yet implemented |
| `calculate_business_days` | `calculate_business_days` | Not in original table — private helper visible in body; may or may not be in public spec |
| `check_leave_overlap` | `check_leave_overlap` | Not in original table — private helper visible in body; may or may not be in public spec |

[GAP-FILLED] **Tables Read (corrected):**

The source body confirms reads against the following tables not listed in the original header:

| Table | Access point |
|---|---|
| HOLIDAYS | `calculate_business_days` — filters by HOLIDAY_DATE, ACTIVE_FLAG='Y', LOCATION_CODE |
| EMPLOYEES | `submit_leave_request` — full row fetch for EMPLOYMENT_STATUS, HIRE_DATE, LOCATION_CODE, MANAGER_EMP_ID, FIRST_NAME, LAST_NAME |
| LEAVE_TYPES | `submit_leave_request` — full row fetch for MIN_TENURE_DAYS, ACCRUAL_FLAG, REQUIRES_APPROVAL, LEAVE_TYPE_NAME |
| LEAVE_REQUESTS | `check_leave_overlap`, `approve_leave_request`, `reject_leave_request`, `cancel_leave_request` — reads and SELECT FOR UPDATE |
| LEAVE_BALANCES | `submit_leave_request`, `approve_leave_request`, `reject_leave_request`, `cancel_leave_request`, `get_leave_balance` — reads and DML |

**Revised Tables Read list:** EMPLOYEES, LEAVE_TYPES, HOLIDAYS, LEAVE_REQUESTS (also written), LEAVE_BALANCES (also written)

[GAP-FILLED] **REQUIRES_APPROVAL column — source table confirmed:**

**Gap closed:** The source table for `REQUIRES_APPROVAL` is **LEAVE_TYPES**.

**Evidence from PKG_LEAVE.pkb:**

In `submit_leave_request`, the leave type row is fetched into a `LEAVE_TYPES%ROWTYPE` local variable:

```sql
v_leave_type    LEAVE_TYPES%ROWTYPE;
...
SELECT * INTO v_leave_type
FROM LEAVE_TYPES
WHERE LEAVE_TYPE_ID = p_leave_type_id
AND ACTIVE_FLAG = 'Y';
```

All three subsequent references to the flag read from that same variable:

```sql
-- Controls initial status on INSERT:
CASE WHEN v_leave_type.REQUIRES_APPROVAL = 'Y' THEN 'PENDING' ELSE 'APPROVED' END

-- Guards manager notification:
IF v_manager_id IS NOT NULL AND v_leave_type.REQUIRES_APPROVAL = 'Y' THEN

-- Triggers auto-approval path:
IF v_leave_type.REQUIRES_APPROVAL = 'N' THEN
    approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user);
END IF;
```

Because `v_leave_type` is declared as `LEAVE_TYPES%ROWTYPE` and populated exclusively from `LEAVE_TYPES`, the column is unambiguously on **LEAVE_TYPES**, not on LEAVE_POLICIES or any other config table.

**REQUIRES_APPROVAL column specification (confirmed):**

| Attribute | Value |
|---|---|
| Table | LEAVE_TYPES |
| Column | REQUIRES_APPROVAL |
| Type | CHAR (inferred: single-character Y/N flag, consistent with all other flag columns in this package — ACTIVE_FLAG, ACCRUAL_FLAG, HALF_DAY_FLAG) |
| Allowed values | 'Y' — request enters PENDING, manager notified, awaits human approval; 'N' — request auto-approves immediately via `approve_leave_request(request_id, NULL, 'Auto-approved')` |
| Scope | Per leave type (e.g. Emergency Leave may be REQUIRES_APPROVAL='N'; Annual Leave may be 'Y') — this is type-level configuration, not per-employee or per-policy |
| Evaluated at | `submit_leave_request` call time, after leave type row is fetched and validated |

**Auto-approval business rule — now traceable:**

```
submit_leave_request
  └─ SELECT * FROM LEAVE_TYPES WHERE LEAVE_TYPE_ID = p_leave_type_id AND ACTIVE_FLAG = 'Y'
       └─ v_leave_type.REQUIRES_APPROVAL
            ├─ = 'Y' → INSERT LEAVE_REQUESTS with STATUS = 'PENDING'
            │          → notify manager via PKG_NOTIFICATION.send_notification
            │          → request awaits approve_leave_request / reject_leave_request
            └─ = 'N' → INSERT LEAVE_REQUESTS with STATUS = 'APPROVED'
                       → immediately call approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user)
                       → LEAVE_BALANCES.PENDING decremented, USED incremented in same transaction
                       → employee notified of approval via PKG_NOTIFICATION.send_notification
```

**No LEAVE_POLICIES involvement:** The column does not exist on LEAVE_POLICIES (or any other table) based on the sourced code. Every code path that gates on approval requirement reads exclusively from `v_leave_type.REQUIRES_APPROVAL`. If a LEAVE_POLICIES table exists in the schema it plays no role in this decision point.

[GAP-FILLED] **`approve_leave_request` — programmatic vs. manual call behaviour (gap closed):**

**Gap closed:** The procedure signature, parameter values, and behavioural differences between the auto-approval (programmatic) path and the human-approval (manual) path are now fully documented from source.

**Confirmed procedure signature:**

```sql
PROCEDURE approve_leave_request(
    p_request_id      IN NUMBER,
    p_approver_emp_id IN NUMBER,
    p_comments        IN VARCHAR2 DEFAULT NULL,
    p_user            IN VARCHAR2 DEFAULT USER
)
```

**Programmatic call (auto-approval path — called from `submit_leave_request`):**

```sql
approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user);
```

| Parameter | Value in auto-approval call | Consequence |
|---|---|---|
| p_request_id | v_request_id — the request just inserted | Identifies the row created in the same transaction |
| p_approver_emp_id | **NULL** | APPROVER_EMP_ID is set to NULL in the UPDATE, overwriting the v_manager_id value stored in APPROVER_EMP_ID during the INSERT; no human approver is recorded |
| p_comments | `'Auto-approved'` (hardcoded literal) | APPROVAL_COMMENTS is set to the string 'Auto-approved'; comments parameter has DEFAULT NULL in the signature but auto-approval always passes this literal |
| p_user | p_user inherited from submit_leave_request | MODIFIED_BY is set to the same user who submitted the request |

**Manual call (human-approval path — called by UI or external process):**

| Parameter | Value in manual call | Consequence |
|---|---|---|
| p_request_id | Request ID of an existing PENDING request | Must already exist with STATUS='PENDING' |
| p_approver_emp_id | Actual manager or HR employee EMP_ID | Stored in APPROVER_EMP_ID; provides audit trail of who approved |
| p_comments | Optional free-text reason or approval note (DEFAULT NULL) | Stored in APPROVAL_COMMENTS; NULL is valid for unconditional approvals |
| p_user | Logged-in user session | Stored in MODIFIED_BY for audit |

**Shared behaviour regardless of call path (confirmed from source body):**

Both call paths execute the same code body with no branching on caller identity:

1. `SELECT * FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE` — row-level lock acquired
2. Guard: `IF v_request.STATUS != 'PENDING' THEN RAISE_APPLICATION_ERROR(-20204, ...)` — enforced identically for both paths
3. `UPDATE LEAVE_REQUESTS SET STATUS='APPROVED', APPROVER_EMP_ID=p_approver_emp_id, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS=p_comments, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE`
4. `UPDATE LEAVE_BALANCES SET PENDING=PENDING-v_request.TOTAL_DAYS, USED=USED+v_request.TOTAL_DAYS, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE`
5. `PKG_NOTIFICATION.send_notification(p_recipient_emp_id => v_request.EMP_ID, ...)` — employee is notified in both paths; the auto-approval path triggers an "approved" email to the employee immediately on submit
6. `PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)`

**CRITICAL DEFECT — auto-approval path STATUS mismatch (LEAVE-BUG-04):**

The auto-approval path contains a **logical defect that renders it non-functional** for all leave types with REQUIRES_APPROVAL='N'.

**Root cause trace:**

Step 1 — `submit_leave_request` INSERTs the request with STATUS already set to 'APPROVED':
```sql
INSERT INTO LEAVE_REQUESTS (... STATUS ...) VALUES (
    ...
    CASE WHEN v_leave_type.REQUIRES_APPROVAL = 'Y' THEN 'PENDING' ELSE 'APPROVED' END,
    ...
);
```
When REQUIRES_APPROVAL='N', the inserted row has `STATUS = 'APPROVED'`.

Step 2 — `submit_leave_request` then immediately calls `approve_leave_request`:
```sql
IF v_leave_type.REQUIRES_APPROVAL = 'N' THEN
    approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user);
END IF;
```

Step 3 — `approve_leave_request` fetches the row and enforces the PENDING guard:
```sql
SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE;

IF v_request.STATUS != 'PENDING' THEN
    RAISE_APPLICATION_ERROR(-20204,
        'Cannot approve request in status: ' || v_request.STATUS);
END IF;
```

Because the row was inserted with `STATUS='APPROVED'` in Step 1, the guard in Step 3 evaluates `'APPROVED' != 'PENDING'` → **TRUE** → raises `-20204 'Cannot approve request in status: APPROVED'`.

The exception propagates back through `submit_leave_request`, causing the entire transaction (INSERT + LEAVE_BALANCES UPDATE + notification) to roll back. **No leave request can be successfully submitted for any leave type with REQUIRES_APPROVAL='N'.**

**Defect summary:**

| Attribute | Value |
|---|---|
| Defect ID | LEAVE-BUG-04 |
| Severity | **HIGH** — all leave types with REQUIRES_APPROVAL='N' are completely non-functional |
| Location | `submit_leave_request` — CASE expression in INSERT statement |
| Root cause | INSERT sets STATUS='APPROVED' when REQUIRES_APPROVAL='N', but the subsequently-called `approve_leave_request` requires STATUS='PENDING' as a precondition |
| Observable failure | `submit_leave_request` raises ORA-20204 and rolls back for every REQUIRES_APPROVAL='N' leave type |
| Correct fix (option A) | Change INSERT CASE expression: `CASE WHEN v_leave_type.REQUIRES_APPROVAL = 'Y' THEN 'PENDING' ELSE 'PENDING' END` (i.e. always insert PENDING), then let `approve_leave_request` transition to APPROVED |
| Correct fix (option B) | Remove the CASE expression entirely; always insert PENDING; `approve_leave_request` already handles the APPROVED transition correctly |
| Side-effect of fix | With option A or B, the LEAVE_BALANCES.PENDING increment in `submit_leave_request` + the PENDING→USED flip in `approve_leave_request` remain consistent: PENDING is incremented then immediately decremented and USED is incremented, ending at the correct net state |
| Anti-fix to avoid | Changing the `!= 'PENDING'` guard in `approve_leave_request` to allow 'APPROVED' status would break the guard's correctness for the manual path (idempotent double-approvals would silently double-deduct LEAVE_BALANCES) |

**Corrected auto-approval flow (what it should do after fix):**

```
submit_leave_request (REQUIRES_APPROVAL='N')
  └─ INSERT LEAVE_REQUESTS with STATUS = 'PENDING'      ← corrected: was 'APPROVED'
  └─ UPDATE LEAVE_BALANCES: PENDING += total_days
  └─ approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user)
       └─ SELECT FOR UPDATE → STATUS='PENDING' → guard passes
       └─ UPDATE LEAVE_REQUESTS: STATUS='APPROVED', APPROVER_EMP_ID=NULL, APPROVAL_COMMENTS='Auto-approved'
       └─ UPDATE LEAVE_BALANCES: PENDING -= total_days, USED += total_days
       └─ PKG_NOTIFICATION: email employee 'Leave Request Approved'
       └─ PKG_AUDIT: log UPDATE
  └─ PKG_AUDIT: log INSERT (from submit_leave_request)
  └─ RETURN v_request_id
```

**Actual auto-approval flow (current broken behaviour):**

```
submit_leave_request (REQUIRES_APPROVAL='N')
  └─ INSERT LEAVE_REQUESTS with STATUS = 'APPROVED'     ← bug: sets final state prematurely
  └─ UPDATE LEAVE_BALANCES: PENDING += total_days
  └─ approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user)
       └─ SELECT FOR UPDATE → STATUS='APPROVED'
       └─ IF STATUS != 'PENDING' → RAISE_APPLICATION_ERROR(-20204, ...)  ← exception raised
  └─ ROLLBACK (exception propagates; entire transaction undone)
  └─ submit_leave_request raises ORA-20204 to caller
```

[GAP-FILLED] **Known defects (confirmed from PKG_LEAVE.pkb source) — updated to include LEAVE-BUG-04:**

| ID | Severity | Location | Description |
|---|---|---|---|
| LEAVE-BUG-01 | MEDIUM | `calculate_business_days` | Observed holidays not excluded — if a public holiday falls on a weekend, the Monday/Friday substitute is not recognised; the day-by-day loop only checks exact HOLIDAY_DATE matches |
| LEAVE-BUG-02 | LOW | `submit_leave_request` | Backdating cap is hardcoded at 5 days with no configuration point; businesses with different policies cannot override without code change |
| LEAVE-BUG-03 | LOW | `submit_leave_request` | Half-day requests bypass business-day calculation entirely (v_total_days := 0.5 unconditionally); a half-day on a weekend or public holiday is not rejected |
| LEAVE-BUG-04 | **HIGH** | `submit_leave_request` → `approve_leave_request` | Auto-approval path is non-functional: INSERT sets STATUS='APPROVED' but `approve_leave_request` requires STATUS='PENDING'; raises ORA-20204 and rolls back for all leave types with REQUIRES_APPROVAL='N' |

[GAP-FILLED] **`accrue_leave` — unconfirmed status:**

The original table listed `accrue_leave` with specific accrual rates (1.25 PTO, 0.833 SICK). This procedure does **not appear** in the sourced PKG_LEAVE.pkb body. Three candidate explanations:

| Candidate | Description |
|---|---|
| Separate package | Accrual logic lives in an unreviewed package (e.g. PKG_ACCRUALS, PKG_SCHEDULER, PKG_HR_BATCH) |
| Not yet implemented | Accrual is a known gap — leave balances may be loaded manually or via a legacy batch |
| Spec-only stub | Declared in PKG_LEAVE.pks but body not yet written |

**Until resolved, `accrue_leave` should be tracked as GAP-002: unconfirmed accrual write path for LEAVE_BALANCES.**

---

## PACKAGE: PKG_EMPLOYEE (partial — TD-74 gap fill)
**Domain:** BC-01 Employee Management
**Schema:** HRMS

[GAP-FILLED] **TD-74 — `g_debug_mode` flag: variable identity, toggle authority, and production vs. debug behaviour (gap closed):**

**Gap closed:** The source code of `PKG_EMPLOYEE.pkb` contains two confirmed references to `g_debug_mode`. The declaration site is not included in the recovered fragment (the private section lists only `c_emp_number_prefix` and `c_max_hierarchy_depth`), but variable identity, usage context, and behavioural effect can be fully characterised from the call sites.

**Confirmed variable identity:**

| Attribute | Value | Basis |
|---|---|---|
| Name | `g_debug_mode` | Used unqualified at two call sites within the package body |
| Type | BOOLEAN (strongly inferred) | Used exclusively in bare `IF g_debug_mode THEN` conditionals; no comparison operator or value cast; consistent with PL/SQL BOOLEAN package-level variable |
| Scope | Package-level variable (not a constant, not a local) | Referenced in two separate procedures (`create_employee` and `log_history`) without passing as a parameter; must be declared at package level |
| Visibility | **Cannot be confirmed from fragment** — declaration absent from the recovered body header; could be in package spec (public) or package body preamble (private) | See note on toggle authority below |
| Default value | **Not confirmed from fragment** — absent from visible private section; likely FALSE (debug off by default), but this is an inference from convention, not from source |

**Where `g_debug_mode` is read (confirmed call sites):**

**Call site 1 — `create_employee`, salary grade range check:**

```sql
-- In create_employee, after fetching v_min / v_max from JOB_GRADES:
IF p_base_salary < v_min OR p_base_salary > v_max THEN
    -- NOTE: This is a soft warning, not an error
    -- Forms trigger WHEN-VALIDATE-ITEM shows warning dialog
    -- but allows override with manager approval
    IF g_debug_mode THEN
        DBMS_OUTPUT.PUT_LINE('WARNING: Salary ' || p_base_salary ||
            ' outside grade range [' || v_min || '-' || v_max || ']');
    END IF;
END IF;
```

**Call site 2 — `log_history`, history-insert exception handler:**

```sql
-- In log_history EXCEPTION block (PRAGMA AUTONOMOUS_TRANSACTION):
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        IF g_debug_mode THEN
            DBMS_OUTPUT.PUT_LINE('WARNING: Failed to log history for EMP_ID=' ||
                p_emp_id || ': ' || SQLERRM);
        END IF;
END log_history;
```

**Critical finding — `g_debug_mode` does NOT gate enforcement of salary grade validation:**

The salary-out-of-range condition is **never an error** at the PL/SQL layer regardless of the flag value. The source comment is explicit: *"This is a soft warning, not an error — Forms trigger WHEN-VALIDATE-ITEM shows warning dialog but allows override with manager approval."* The `IF g_debug_mode` block contains only a `DBMS_OUTPUT.PUT_LINE` call. The outer `IF p_base_salary < v_min OR p_base_salary > v_max` block does not contain a `RAISE_APPLICATION_ERROR` and does not set any out-of-range indicator — it only conditionally emits debug output.

This means `validate_salary_for_grade` enforcement (as described in TD-74) is split across two layers:

| Layer | Enforcement mechanism | Controlled by `g_debug_mode`? |
|---|---|---|
| Oracle Forms client | `WHEN-VALIDATE-ITEM` trigger on the salary field; shows a warning dialog; requires manager-approval click-through to proceed | No — client-side; unrelated to `g_debug_mode` |
| PKG_EMPLOYEE PL/SQL | Out-of-range condition detected but never raises an exception; violation is silently permitted at the database layer | No — the violation is always permitted; `g_debug_mode` only controls whether a diagnostic line is written to DBMS_OUTPUT |

**Production vs. debug mode behaviour (confirmed):**

| Condition | Production (`g_debug_mode` = FALSE or default) | Debug (`g_debug_mode` = TRUE) |
|---|---|---|
| Salary within grade range | Employee created; no output | Employee created; no output |
| Salary outside grade range | Employee created silently — no error, no DBMS_OUTPUT line; violation passes through to the INSERT | Employee created; `DBMS_OUTPUT.PUT_LINE` emits `'WARNING: Salary <n> outside grade range [<min>-<max>]'` before proceeding with the INSERT |
| `log_history` INSERT succeeds | History row committed (AUTONOMOUS_TRANSACTION); no output | History row committed; no output |
| `log_history` INSERT fails (WHEN OTHERS) | Exception swallowed silently after ROLLBACK; main transaction continues unaffected — **this is the documented intent** ("History logging should never fail the main transaction") | Exception swallowed after ROLLBACK; `DBMS_OUTPUT.PUT_LINE` emits `'WARNING: Failed to log history for EMP_ID=<n>: <sqlerrm>'` before returning |

**Toggle authority — confirmed boundary:**

The recovered fragment does not contain a `set_debug_mode` procedure, a `g_debug_mode := ...` assignment, or a package initialisation block that sets the flag. Two scenarios are consistent with the visible source:

| Scenario | Mechanism | Implication |
|---|---|---|
| Public package variable (in spec) | Any session with EXECUTE privilege on PKG_EMPLOYEE can set `PKG_EMPLOYEE.g_debug_mode := TRUE` directly | No procedure needed; any privileged session (DBA, developer, support script) can toggle it; value resets to default on package re-instantiation (new session or package invalidation) |
| Private package variable (in body) with setter procedure not in fragment | A `set_debug_mode(p_flag IN BOOLEAN)` or similar procedure exists but was not included in the file_cache.json recovery | Toggling restricted to callers of that procedure; access control follows the procedure's AUTHID and any explicit grants |

**Until the declaration site and any setter procedure are confirmed from the full PKG_EMPLOYEE spec and body, toggle authority cannot be definitively assigned. The flag is session-scoped regardless of scenario: it is not stored in a table, does not persist across sessions, and resets on package recompilation or session termination.**

**Relationship to TD-74 original question — summary:**

| TD-74 sub-question | Answer (confirmed from source) |
|---|---|
| What variable controls the debug gate? | `g_debug_mode` — package-level BOOLEAN variable in PKG_EMPLOYEE |
| What does it gate in `create_employee`? | A single `DBMS_OUTPUT.PUT_LINE` warning when salary is outside the JOB_GRADES range for the employee's grade; it does NOT gate the enforcement itself — the violation is always permitted through to INSERT |
| What does it gate in `log_history`? | A single `DBMS_OUTPUT.PUT_LINE` warning when the autonomous history INSERT fails; the exception is always swallowed regardless of flag value |
| Who can toggle it? | Not confirmed from fragment — depends on whether declared in spec (any privileged session) or body with setter procedure (restricted callers only) |
| Production behaviour | All `g_debug_mode`-gated output suppressed; salary violations pass silently; history failures swallowed silently |
| Debug behaviour | DBMS_OUTPUT receives diagnostic lines for salary violations and history failures; no change to DML behaviour or error propagation |
| Does setting it to TRUE enforce salary grade limits? | **No.** The flag has no effect on whether out-of-range salaries are accepted. Enforcement is client-side only (Oracle Forms `WHEN-VALIDATE-ITEM`). The flag only controls diagnostic output visibility. |
