# HRMS Data Flow Map

**Schema:** HRMS  **DB:** Oracle 19c  **Extracted:** 2026-08-04  
**Method:** CODE-ONLY

---

## Overview

The HRMS is a PL/SQL-first system. All business logic lives in 11 Oracle packages. Oracle Forms 4.x provides the UI; it calls packages directly. There is no middleware or web tier. External integrations use UTL_FILE for file I/O and UTL_SMTP for email.

---

## Employee Lifecycle Flows

### 1. Hire Employee

```
Oracle Forms (HR_EMPLOYEE_FORM.fmb)
  │  calls
  ▼
PKG_EMPLOYEE.create_employee(p_params)        ← CORRECTED: function is create_employee, not hire_employee
  ├── [validation inline in create_employee]  ← CORRECTED: PKG_VALIDATION.validate_hire_data() does not exist
  ├── SEQ_EMPLOYEE.NEXTVAL                    ← generates EMP_ID
  ├── MAX(EMP_NUMBER)+1  ⚠RACE CONDITION      ← generates EMP_NUMBER (should use SEQ_EMP_NUMBER)
  ├── INSERT INTO EMPLOYEES
  ├── PKG_PAYROLL.create_salary_record()      ← inserts SALARY_RECORDS row
  ├── PKG_LEAVE.initialize_balances()         ← CORRECTED: inserts LEAVE_BALANCES rows (one per LEAVE_TYPE)
  ├── PKG_NOTIFICATION.queue_notification()   ← enqueues NOTIFICATION_QUEUE (welcome email)
  └── PKG_AUDIT.log_action('INSERT','EMPLOYEES',...)  ← AUTONOMOUS_TRANSACTION audit

  Trigger fires:
  TRG_EMP_BEFORE_INSERT → validates HIRE_DATE ≤ SYSDATE+180, checks EMAIL uniqueness
```

[SUPPLEMENTED] **Dual-notification detail confirmed from PKG_EMPLOYEE.pkb:**
```
create_employee (continued)
  ├── PKG_NOTIFICATION.send_notification(p_recipient=v_emp_id, 'Welcome to the Company')
  │       Body: "Dear <first_name>, Welcome aboard! Your employee number is <EMP_NUMBER>."
  └── if p_manager_emp_id IS NOT NULL:
        PKG_NOTIFICATION.send_notification(p_recipient=p_manager_emp_id,
            'New Direct Report: <first_name> <last_name>')
        Body: "<name> has been added as your direct report, starting <hire_date>."
```

[SUPPLEMENTED] **Salary-range soft-warning (not a hard error):**
If `p_base_salary` falls outside the grade's MIN_SALARY–MAX_SALARY range, `create_employee`
emits a DBMS_OUTPUT warning (when `g_debug_mode = TRUE`) but does NOT raise an error.
The Forms trigger `WHEN-VALIDATE-ITEM` is expected to show a warning dialog and allow
manager override. The server-side package therefore permits out-of-range salaries silently.

### 2. Employee Update (Dept/Job/Manager/Status Change)

```
Oracle Forms
  │  DML UPDATE on EMPLOYEES
  ▼
TRG_EMP_BEFORE_UPDATE (fires)
  ├── Blocks TERMINATED → ACTIVE transition (-20503)
  ├── Logs STATUS_CHANGE to EMPLOYEE_HISTORY
  ├── Logs DEPARTMENT_CHANGE to EMPLOYEE_HISTORY
  └── Logs JOB_CHANGE to EMPLOYEE_HISTORY
      ⚠ Uses column names HISTORY_ID/CHANGE_DATE that differ from DDL
```

### 3. Terminate Employee

```
PKG_EMPLOYEE.terminate_employee(p_emp_id, p_date, p_reason)
  ├── UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='TERMINATED', ACTIVE_FLAG='N'
  ├── UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED' (all PENDING requests)
  │       reason = 'Auto-cancelled due to termination'
  ├── ⚠ PKG_PAYROLL.calculate_final_pay → TODO stub (not implemented)
  ├── ⚠ PKG_SECURITY.revoke_access → TODO stub (not implemented)
  └── ⚠ COBRA notification → TODO stub (not implemented)

  Trigger fires:
  TRG_EMP_INSTEAD_OF_DELETE → blocks any physical DELETE (-20504)
```

[SUPPLEMENTED] **Full cascade confirmed from PKG_EMPLOYEE.pkb:**
```
terminate_employee (additional steps confirmed)
  ├── UPDATE SALARY_RECORDS SET END_DATE=p_termination_date, ACTIVE_FLAG='N'
  │       WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'   ← ends current salary record
  ├── UPDATE EMPLOYEE_PAY_ELEMENTS SET END_DATE=p_termination_date, ACTIVE_FLAG='N'
  │       WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'   ← deactivates all pay elements
  ├── PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
  └── if MANAGER_EMP_ID IS NOT NULL:
        PKG_NOTIFICATION.send_notification(p_recipient=MANAGER_EMP_ID,
            'Employee Termination: <first_name> <last_name>')
        Body: "<name> termination effective <termination_date MM/DD/YYYY>"
```

[SUPPLEMENTED] **Three confirmed TODO stubs in terminate_employee (code comments):**
- `-- TODO: Integrate with benefits system to trigger COBRA`
- `-- TODO: Revoke system access via PKG_SECURITY`
- `-- TODO: Calculate final pay via PKG_PAYROLL.calculate_final_pay`
These are inline code comments in the procedure body, not separate stub procedures.

[GAP-FILLED] **GAP-FP-02: Payroll cutoff rules on termination — full documentation**

**Clarification: terminate_employee → salary record end-dating mechanism**

The gap description states that `terminate_employee` calls `PKG_PAYROLL.create_salary_record`
to end-date the salary record. The actual code ([SUPPLEMENTED] block above) shows
`terminate_employee` performs a **direct `UPDATE SALARY_RECORDS`**, bypassing
`create_salary_record`. The distinction is load-bearing:

`create_salary_record` end-dating logic (PKG_PAYROLL.pkb):
```sql
UPDATE SALARY_RECORDS
SET END_DATE = p_effective_date - 1,   -- one day BEFORE effective date
    ACTIVE_FLAG = 'N'
WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y'
AND EFFECTIVE_DATE < p_effective_date;
-- Then INSERTs a NEW salary row at p_effective_date (appropriate for salary changes)
```

`terminate_employee` direct DML (PKG_EMPLOYEE.pkb — confirmed from annotated source):
```sql
UPDATE SALARY_RECORDS
SET END_DATE = p_termination_date,     -- ON the termination date (inclusive)
    ACTIVE_FLAG = 'N'
WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y'
-- No INSERT follows — correct for termination; no successor record needed
```

Off-by-one distinction: `create_salary_record` closes the prior record at `p_date - 1`
because a new record takes effect on `p_date`. `terminate_employee` closes at `p_date`
itself because no successor salary record follows. Using `create_salary_record` for
termination would create an erroneous zero-salary row at `p_termination_date`.

**Pro-ration of final-period earnings: NOT IMPLEMENTED**

`calculate_payroll` (PKG_PAYROLL.pkb) restricts processing to active employees:
```sql
FOR emp_rec IN (
    SELECT e.EMP_ID
    FROM EMPLOYEES e
    WHERE e.EMPLOYMENT_STATUS = 'ACTIVE'   -- terminated employees are excluded
    AND e.ACTIVE_FLAG = 'Y'
    ORDER BY e.EMP_ID
) LOOP
```
A mid-period termination produces **no partial-period payment** from the regular payroll run.
`PKG_PAYROLL.calculate_final_pay` is the intended mechanism but is a confirmed TODO stub
with no implementation. Until implemented, a terminated employee receives:
- Their last full-period pay if `EMPLOYMENT_STATUS` was `ACTIVE` at period open time, OR
- Nothing for the final partial period if terminated after the payroll run processed them.

Pro-ration formula derivable from existing PKG_PAYROLL building blocks (forward-engineering
reference — not present in current code):
```
v_salary       := get_salary_as_of(p_emp_id, p_termination_date);
v_period_rate  := v_salary / v_periods_per_year;
v_daily_rate   := v_period_rate / (v_period_end - v_period_start + 1);
v_final_gross  := v_daily_rate * (p_termination_date - v_period_start + 1);
```
Where `v_periods_per_year` follows the existing CASE in `calculate_employee_pay`:
`WEEKLY→52 | BIWEEKLY→26 | SEMIMONTHLY→24 | MONTHLY→12`.

Existing PKG_PAYROLL symbols usable without modification for a final-pay implementation:

| Symbol | Type | Purpose |
|--------|------|---------|
| `get_salary_as_of(p_emp_id, p_termination_date)` | FUNCTION | Salary active on last day |
| `get_current_period()` | FUNCTION | Locate open period for off-cycle run |
| `create_payroll_run(p_period_id, 'FINAL_PAY')` | FUNCTION | Create distinct off-cycle run |
| `c_ss_rate` (0.062) | CONSTANT | Social Security on final gross |
| `c_medicare_rate` (0.0145) | CONSTANT | Medicare on final gross |
| `c_medicare_addl_rate` (0.009) | CONSTANT | Additional Medicare above $200k YTD |
| `PKG_AUDIT.log_action(...)` | PROCEDURE | Audit the final-pay detail row |

**Accrual payout trigger conditions: ABSENT — no code path exists**

No code in any confirmed package links `terminate_employee` to a leave balance payout.
Two confirmed structural gaps:

1. `run_monthly_accrual` (PKG_LEAVE) queries `EMPLOYMENT_STATUS = 'ACTIVE'` — accrual stops
   on termination but existing `LEAVE_BALANCES.AVAILABLE` values are left intact; no
   zero-out, no payout conversion, no downstream notification.

2. Neither `terminate_employee` nor the `calculate_final_pay` stub queries `LEAVE_BALANCES`
   or calls any `PKG_LEAVE` function. The balance rows persist indefinitely post-termination
   with no mechanism to action them.

Payout eligibility by leave type (rules not present in code — listed for forward engineering):

| Leave Type | Payout-eligible | Basis |
|------------|-----------------|-------|
| PTO | Yes (many jurisdictions mandate) | `AVAILABLE × daily_rate` |
| SICK | Employer policy (often forfeited) | Policy parameter — not in SYSTEM_PARAMETERS |
| COMP | Yes (earned time) | `AVAILABLE × daily_rate` |
| FMLA | No (unpaid entitlement) | N/A |
| JURY | No (event-based, not banked) | N/A |
| BEREAVE | No (event-based, not banked) | N/A |

The `AVAILABLE` balance is computed as
`OPENING_BALANCE + ACCRUED + ADJUSTMENT - USED - PENDING` in `PKG_LEAVE`.
Payout amount would be `AVAILABLE × get_salary_as_of(p_emp_id, p_termination_date) / 260`
(260 working days/year for salaried staff), but this formula is absent from the codebase.

**Supplemental-tax flat rate on lump-sum payouts: ABSENT**

`calculate_employee_pay` applies `calculate_federal_tax` and `calculate_state_tax` using
annualised periodic income. A lump-sum termination payout (accrued PTO, severance) is
taxable at the IRS supplemental flat rate (22% federal for amounts ≤$1M in 2024), not at
the annualised bracket rate. No supplemental-rate branch exists in any confirmed tax
calculation procedure; this gap applies to both final pro-rated earnings and any leave payout.

**Complete gap inventory for GAP-FP-02**

| Cutoff rule | Implemented? | Notes |
|-------------|-------------|-------|
| End-date salary record on termination | Yes — direct DML | PKG_EMPLOYEE.terminate_employee |
| End-date pay elements on termination | Yes — direct DML | PKG_EMPLOYEE.terminate_employee |
| Pro-rate earnings for partial final period | **No** | TODO stub: PKG_PAYROLL.calculate_final_pay |
| Final-pay off-cycle payroll run | **No** | `create_payroll_run('FINAL_PAY')` never called |
| PTO/COMP payout on termination | **No** | No code path from termination → LEAVE_BALANCES |
| SICK payout (policy-dependent) | **No** | No policy parameter exists in SYSTEM_PARAMETERS |
| Supplemental tax flat-rate on lump sums | **No** | Not branched in calculate_federal/state_tax |
| COBRA notification trigger | **No** | TODO stub comment in terminate_employee |

### 4. Rehire Employee

```
PKG_EMPLOYEE.rehire_employee(p_emp_id, p_rehire_date, p_dept_id, p_job_id)
  ├── UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='ACTIVE', HIRE_DATE=p_rehire_date
  │       ⚠ Overwrites original HIRE_DATE — tenure history lost
  ├── INSERT EMPLOYEE_HISTORY (CHANGE_TYPE='REHIRE')
  └── PKG_LEAVE.initialize_balances()  ← CORRECTED: resets leave for new hire year
```

[SUPPLEMENTED] **Full rehire flow confirmed from PKG_EMPLOYEE.pkb:**
```
rehire_employee (additional confirmed steps)
  ├── validate_dept(p_dept_id)   ← validates department is active
  ├── UPDATE EMPLOYEES SET
  │       EMPLOYMENT_STATUS='ACTIVE', HIRE_DATE=p_rehire_date,
  │       TERMINATION_DATE=NULL, TERMINATION_REASON=NULL,
  │       DEPT_ID=p_dept_id, JOB_ID=p_job_id, ACTIVE_FLAG='Y'
  ├── PKG_PAYROLL.create_salary_record(p_change_reason='REHIRE')
  ├── log_history(CHANGE_TYPE='REHIRE', new_dept, new_job, new_salary)
  └── PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
```
Note: `p_base_salary` is a required parameter for rehire (no default). Leave balance
re-initialization is handled downstream; rehire_employee itself does not call
PKG_LEAVE directly.

[GAP-FILLED] **Downstream caller for PKG_LEAVE.initialize_balances() in the rehire path:**

There is no dedicated trigger, Forms event, or wrapper procedure that explicitly calls
`initialize_balances` after a rehire. The call happens via **lazy initialization** embedded
in two PKG_LEAVE procedures, both of which guard on `SQL%ROWCOUNT = 0` after attempting
a `LEAVE_BALANCES` UPDATE for an employee that has no balance row yet:

```
Path A — next scheduled batch (primary path):
  DBMS_SCHEDULER → PKG_LEAVE.run_monthly_accrual()
    ├── FOR EACH active employee × active leave type:
    │     UPDATE LEAVE_BALANCES SET ACCRUED = ACCRUED + v_accrued
    │     WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND CALENDAR_YEAR=...
    │     IF SQL%ROWCOUNT = 0 THEN          ← rehired employee has no row yet
    │       PKG_LEAVE.initialize_balances(emp_id, year, user)
    │       UPDATE LEAVE_BALANCES SET ACCRUED = v_accrued  ← retry (not +=)
    │     END IF
    └── INSERT INTO LEAVE_ACCRUAL_LOG

Path B — HR admin manual balance adjustment (fallback path):
  PKG_LEAVE.adjust_leave_balance(p_emp_id, p_leave_type_id, p_adjustment, ...)
    ├── UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT + p_adjustment WHERE ...
    └── IF SQL%ROWCOUNT = 0 THEN            ← no row exists for this employee/year
          PKG_LEAVE.initialize_balances(p_emp_id, EXTRACT(YEAR FROM SYSDATE), p_user)
          retry UPDATE                      ← then applies the adjustment
        END IF
```

**Architectural implication — hire vs. rehire asymmetry:**
- `create_employee` calls `PKG_LEAVE.initialize_balances()` **eagerly**, synchronously,
  within the same transaction as the INSERT INTO EMPLOYEES.
- `rehire_employee` has **no equivalent eager call** — balance rows are absent until
  either (a) the next `run_monthly_accrual` batch fires, or (b) `adjust_leave_balance`
  is called manually by HR.
- During the window between rehire and first accrual run, the employee has no
  `LEAVE_BALANCES` rows. Any call to `get_leave_balance` for that employee/year will
  return 0 (NVL fallback on NO_DATA_FOUND), and `submit_leave_request` will reject
  accrual-based leave requests with "Insufficient balance".
- Evidence: `quality-review.md` classifies `initialize_balances` as "Called from
  `adjust_leave_balance` and `run_monthly_accrual`" — confirming no rehire-specific
  caller exists in the confirmed codebase.

### 4a. Transfer Employee [SUPPLEMENTED]

```
PKG_EMPLOYEE.transfer_employee(p_emp_id, p_new_dept_id, p_new_job_id,
                                p_new_manager_id, p_new_location,
                                p_effective_date, p_reason_code, p_comments)
  ├── SELECT … FOR UPDATE NOWAIT     ← locks row; raises if employee non-active
  ├── validate_dept(p_new_dept_id)
  ├── validate_manager(p_new_manager_id, p_emp_id)   ← includes circular-chain check
  ├── UPDATE EMPLOYEES (DEPT_ID, JOB_ID, MANAGER_EMP_ID, LOCATION_CODE)
  │       NULLs ignored (partial-update pattern via NVL)
  ├── log_history(CHANGE_TYPE='TRANSFER', old+new dept/job/manager/location)
  └── PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
```

[GAP-FILLED] **PKG_NOTIFICATION absence in transfer_employee — CONFIRMED ABSENT FROM CODE:**

The absence of any `PKG_NOTIFICATION.send_notification` call in `transfer_employee` is
**confirmed by direct inspection of `PKG_EMPLOYEE.pkb` lines 529–608**. The procedure body
ends at `PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)` with no notification
call of any kind. This is a **real omission in the package**, not a documentation gap.

Comparison across all employee lifecycle flows:

| Flow | Notifies new hire? | Notifies manager? |
|------|--------------------|-------------------|
| `create_employee` (hire) | Yes — welcome email to new employee | Yes — "New Direct Report" alert |
| `terminate_employee` | No | Yes — termination notice |
| `rehire_employee` | No | No |
| `transfer_employee` | No | **No — confirmed absent** |
| `promote_employee` | No | No |

The new manager (if `p_new_manager_id` is supplied) and the old manager both receive no
automated notification when a transfer occurs. Neither does the employee being transferred.

**Additional precision on the NVL/defaulting behaviour confirmed from code:**
- `p_new_job_id` and `p_new_location`: resolved to current values before the UPDATE via
  `v_new_job_id := NVL(p_new_job_id, v_old_rec.JOB_ID)` — so the UPDATE always writes
  an explicit value, not NULL.
- `p_new_manager_id`: resolved inline in the UPDATE as
  `MANAGER_EMP_ID = NVL(p_new_manager_id, MANAGER_EMP_ID)` — if NULL, existing manager
  is preserved without triggering `validate_manager`.
- `validate_manager` is called **only when `p_new_manager_id IS NOT NULL`** (conditional
  guard on line 570); omitting the manager parameter completely skips validation.

### 4b. Promote Employee [SUPPLEMENTED]

```
PKG_EMPLOYEE.promote_employee(p_emp_id, p_new_job_id, p_new_salary,
                               p_effective_date, p_comments)
  ├── SELECT JOB_ID (old_job_id) FROM EMPLOYEES WHERE EMP_ID=p_emp_id
  ├── SELECT BASE_SALARY (old_salary) FROM SALARY_RECORDS
  │       WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' ORDER BY EFFECTIVE_DATE DESC
  ├── UPDATE EMPLOYEES SET JOB_ID=p_new_job_id
  ├── PKG_PAYROLL.create_salary_record(p_change_reason='PROMOTION',
  │       p_change_pct = ROUND(((new-old)/old)*100, 2))
  ├── log_history(CHANGE_TYPE='PROMOTION', old+new job_id, old+new salary)
  └── PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
```

---

## Payroll Processing Flow

### DFD-PAY Phase 1: Pay Period Setup [GAP-FILLED]

**Actor responsibilities and annual scheduling — recovered from PKG_PAYROLL.pkb `create_pay_periods`**

```
Payroll Admin (Oracle Forms or direct call)
  │  calls once per year (typically December for following year)
  ▼
PKG_PAYROLL.create_pay_periods(p_year, p_frequency DEFAULT 'MONTHLY', p_user)
  │
  ├─ [MONTHLY path — 12 periods]
  │   FOR i IN 1..12 LOOP
  │     v_start_date := TO_DATE(p_year || '-MM-01')      ← first of each month
  │     v_end_date   := LAST_DAY(v_start_date)           ← last calendar day of month
  │     v_pay_date   := v_end_date
  │     IF pay_date falls on SAT → pay_date := pay_date - 1  (Friday)
  │     IF pay_date falls on SUN → pay_date := pay_date - 2  (Friday)
  │     INSERT PAY_PERIODS (
  │         PERIOD_ID  = SEQ_PAY_PERIOD.NEXTVAL,
  │         PERIOD_NAME = 'YYYY-MM (Mon)',
  │         PAY_FREQUENCY = 'MONTHLY',
  │         PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE,
  │         STATUS = 'OPEN'
  │     )
  │   END LOOP
  │
  ├─ [BIWEEKLY path — 26 or 27 periods]
  │   v_start := Jan 1 of p_year
  │   → advance v_start until TO_CHAR(v_start,'DY') = 'FRI'   ← first Friday of year
  │   → v_start := v_start - 13                                 ← back up to period open
  │   WHILE YEAR(v_start) <= p_year LOOP
  │     v_end_date := v_start + 13                              ← 14-day period
  │     v_pay_date := v_end_date + 5                            ← pay 5 calendar days after close
  │     IF YEAR(v_start) = p_year OR YEAR(v_end_date) = p_year THEN
  │       INSERT PAY_PERIODS (
  │           PERIOD_ID  = SEQ_PAY_PERIOD.NEXTVAL,
  │           PERIOD_NAME = 'YYYY-BW-NN',
  │           PAY_FREQUENCY = 'BIWEEKLY',
  │           PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE,
  │           STATUS = 'OPEN'
  │       )
  │     END IF
  │     v_start := v_end_date + 1
  │   END LOOP
  │
  └─ COMMIT (single commit after all periods for the year are inserted)
```

**Annual scheduling rules by frequency:**

| Rule | MONTHLY | BIWEEKLY |
|------|---------|----------|
| Periods per year | Always 12 | 26 (sometimes 27 — depends on year-start alignment) |
| Period start | 1st of each calendar month | Derived from first Friday of year − 13 days |
| Period end | LAST_DAY of month | Period start + 13 (always 14 days) |
| Pay date | Last day of month, adjusted to prior Friday if Sat/Sun | Period end + 5 calendar days (no weekend adjustment applied) |
| Period naming | `YYYY-MM (Mon)` | `YYYY-BW-NN` (NN zero-padded counter) |
| Initial status | `OPEN` | `OPEN` |
| Sequence | `SEQ_PAY_PERIOD.NEXTVAL` | `SEQ_PAY_PERIOD.NEXTVAL` |
| Commit strategy | Single COMMIT after all 12 inserts | Single COMMIT after all period inserts |

**⚠ Biweekly weekend adjustment gap:** MONTHLY pay dates apply a Friday-shift for weekend
landings; BIWEEKLY pay dates (`v_end_date + 5`) have no equivalent weekend-shift guard.
If `v_end_date + 5` falls on a Saturday or Sunday, the stored `PAY_DATE` will be a weekend.

**Pay period lifecycle — full state machine:**

```
create_pay_periods → STATUS='OPEN'
        │
        │  [payroll run processed and approved]
        ▼
PKG_PAYROLL.close_pay_period(p_period_id, p_user)
  ├── SELECT STATUS FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id FOR UPDATE
  │       ← row-level lock; serialises concurrent close attempts
  ├── IF STATUS = 'CLOSED' → RAISE -20102 ('Period already closed: N')
  ├── UPDATE PAY_PERIODS SET
  │       STATUS    = 'CLOSED',
  │       CLOSED_BY = p_user,
  │       CLOSED_DATE = SYSDATE,
  │       MODIFIED_BY = p_user,
  │       MODIFIED_DATE = SYSDATE
  └── (no COMMIT — caller owns the transaction)

STATUS values in PAY_PERIODS: OPEN → CLOSED only (no PENDING, no REOPENED state)
```

**Locating the current period at run time:**

```
PKG_PAYROLL.get_current_period() → NUMBER (PERIOD_ID) or NULL
  └── SELECT PERIOD_ID FROM PAY_PERIODS
        WHERE SYSDATE BETWEEN PERIOD_START_DATE AND PERIOD_END_DATE
        AND STATUS = 'OPEN'
        AND ROWNUM = 1   ← ⚠ no ORDER BY — non-deterministic if two OPEN periods overlap
```

**⚠ Gap:** `get_current_period` uses `ROWNUM = 1` without `ORDER BY`. If a data-entry
error creates two overlapping OPEN periods, the function returns whichever Oracle retrieves
first. No uniqueness constraint on `(PERIOD_START_DATE, PERIOD_END_DATE)` is enforced
at the DDL level in the confirmed schema.

**Gate into payroll run creation:**

```
PKG_PAYROLL.create_payroll_run(p_period_id, p_run_type DEFAULT 'REGULAR', p_user)
  ├── SELECT STATUS FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id
  ├── IF STATUS = 'CLOSED' → RAISE -20102 ('Cannot create run for closed period: N')
  ├── v_run_id := SEQ_PAYROLL_RUN.NEXTVAL
  └── INSERT INTO PAYROLL_RUNS (
          RUN_ID, PERIOD_ID, RUN_TYPE='REGULAR'|'OFF_CYCLE'|'CORRECTION',
          RUN_DATE=SYSDATE, STATUS='PENDING',
          SUBMITTED_BY, SUBMITTED_DATE=SYSDATE
      )
      → returns v_run_id (NUMBER) to caller
```

**Complete Phase 1 actor-responsibility matrix:**

| Step | Actor | Procedure / Action | Precondition |
|------|-------|--------------------|--------------|
| 1 — Create year's periods | Payroll Admin | `create_pay_periods(year, frequency)` | No existing periods for that year (no uniqueness guard — duplicate inserts are possible) |
| 2 — Verify periods created | Payroll Admin | Query `PAY_PERIODS` where `PAY_FREQUENCY` and year | All 12 (monthly) or 26–27 (biweekly) rows present with `STATUS='OPEN'` |
| 3 — Identify current period | System / Payroll App | `get_current_period()` | `SYSDATE` falls within an `OPEN` period |
| 4 — Open a payroll run | Payroll Admin | `create_payroll_run(period_id)` | Period `STATUS='OPEN'` |
| 5 — Process payroll | System | `calculate_payroll(run_id)` | Run `STATUS='PENDING'` (see Phase 2) |
| 6 — Close period | Payroll Admin | `close_pay_period(period_id)` | All runs for period reviewed and approved |

**⚠ Missing controls:**
- No scheduler job or trigger calls `create_pay_periods` automatically; manual invocation each year is required.
- No constraint prevents creating a second set of periods for the same year/frequency.
- No `SEMIMONTHLY` or `WEEKLY` path exists in `create_pay_periods` despite those values appearing in the `v_periods_per_year` CASE in `calculate_employee_pay` (24 and 52 respectively). Employees with those pay frequencies would have no periods generated.

### 5. Run Payroll (Full Cycle)

```
PKG_PAYROLL.calculate_payroll(p_period_id)
  │
  ├─→ PAYROLL_RUNS: INSERT (STATUS='CALCULATING')
  │
  ├─→ FOR EACH active employee in EMPLOYEES:
  │     ├── PKG_PAYROLL.calculate_gross_pay()
  │     │     └── SALARY_RECORDS: SELECT current active salary
  │     ├── PKG_PAYROLL.calculate_federal_tax()
  │     │     └── ⚠ 2024 brackets HARD-CODED (TAX_BRACKETS table not read)
  │     ├── PKG_PAYROLL.calculate_state_tax()
  │     │     └── ⚠ Flat-rate simplification; not bracket-based
  │     ├── PKG_PAYROLL.calculate_fica()
  │     │     └── SS wage base $168,600 / Medicare 1.45% / Additional 0.9%
  │     ├── PAYROLL_DETAILS: INSERT per element (base, taxes, deductions)
  │     │     ELEMENT_TYPE column DENORMALIZED from PAY_ELEMENTS
  │     └── ⚠ COMMIT every 50 employees (partial commit risk)
  │
  └─→ PAYROLL_RUNS: UPDATE totals, STATUS='CALCULATED'
```

### 6. Post-Payroll Integration

```
PKG_INTEGRATION.generate_gl_journal(p_run_id)
  ├── SELECT PAYROLL_DETAILS JOIN PAY_ELEMENTS (GL_ACCOUNT_CODE)
  └── UTL_FILE.PUT_LINE → GL_FEED_OUT/GL_FEED_YYYYMMDD.dat  (pipe-delimited)

PKG_INTEGRATION.export_benefits_feed()
  ├── SELECT EMPLOYEES LEFT JOIN EMPLOYEE_DEPENDENTS (active dependents only)
  │     Fields: EMP_NUMBER, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, HIRE_DATE,
  │             EMPLOYMENT_STATUS, MARITAL_STATUS, GENDER, dep fields
  │     ⚠ RC-006 CORRECTED: SSN_ENCRYPTED NOT selected; decrypt_ssn NOT called
  │     ⚠ File contains demographic PII (DOB, gender, marital, dependent data) but NOT SSN
  └── UTL_FILE.PUT_LINE → BENEFITS_FEED_OUT/BENEFITS_YYYYMMDD.dat (203-char fixed-width)
      └── PKG_INTEGRATION.transfer_benefits_feed → FTP to ADP
              FTP creds from SYSTEM_PARAMETERS (cleartext)

PKG_INTEGRATION.generate_pay_register(p_run_id)
  └── UTL_FILE → PAY_REGISTER_OUT/PAY_REGISTER_{run_id}_{YYYYMMDD_HH24MISS}.csv  ← CORRECTED: CSV format, timestamped filename, not fixed-width .txt

PKG_INTEGRATION.import_time_attendance(p_file_name, p_user)
  ├── UTL_FILE.FOPEN(TIME_ATTENDANCE_IN, p_file_name, 'R') → read CSV line by line
  │     Skip rules: lines starting with '#'; empty lines (IS NOT NULL guard)
  │     CSV layout (comment-documented): emp_number, date, hours_regular, hours_overtime
  ├── ⚠ TODO STUB — parse + INSERT logic has placeholder comment only; no DML present
  │     Implied destination: TIME_ATTENDANCE_RECORDS (no DDL — table does not exist in codebase)
  │     Missing link: no path from imported rows → PAYROLL_DETAILS or PAYROLL_RUNS
  ├── Per-line error handling: EXCEPTION WHEN OTHERS → v_errors++ → continue (no rollback)
  └── PKG_COMMON.log_info summary on completion: 'Imported: N, Errors: M'
```

---

## Leave Management Flow

### 7. Submit Leave Request

```
Oracle Forms (HR_LEAVE_FORM.fmb)
  │
  ▼
PKG_LEAVE.submit_leave_request(p_emp_id, p_leave_type_id, p_start, p_end)  ← CORRECTED: function is submit_leave_request, not submit_request
  ├── Check LEAVE_TYPES.MIN_TENURE_DAYS (COMP: 90 days; FMLA: 365 days) — CORRECTED: ANNUAL does not exist; actual types are PTO/SICK (no tenure gate), COMP (90 days), FMLA (365 days), JURY/BEREAVE (no tenure gate)
  ├── Check LEAVE_BALANCES.AVAILABLE ≥ requested days
  ├── Check backdating: START_DATE ≥ SYSDATE - 5 days
  ├── PKG_LEAVE.calculate_business_days() ← counts working days, excludes HOLIDAYS
  │     ⚠ Different from PKG_COMMON.business_days_between (which does NOT exclude holidays)
  ├── INSERT INTO LEAVE_REQUESTS (STATUS='PENDING')
  ├── UPDATE LEAVE_BALANCES SET PENDING = PENDING + total_days
  └── PKG_NOTIFICATION.queue_notification() → manager notified

PKG_LEAVE.approve_request / reject_request (by manager)
  ├── UPDATE LEAVE_REQUESTS.STATUS = 'APPROVED' / 'REJECTED'
  ├── If APPROVED: UPDATE LEAVE_BALANCES SET USED=USED+days, PENDING=PENDING-days
  └── PKG_NOTIFICATION.queue_notification() → employee notified
```

### 8. Monthly Leave Accrual (Scheduled)

```
DBMS_SCHEDULER (implied) → PKG_LEAVE.run_monthly_accrual()
  ├── FOR EACH active employee:
  │     ├── SELECT LEAVE_TYPES accrual rates
  │     ├── Calculate accrual (pro-rated for partial months, tenure gates)
  │     ├── UPDATE LEAVE_BALANCES.ACCRUED
  │     ├── INSERT INTO LEAVE_ACCRUAL_LOG
  │     └── COMMIT every 100 employees
  │
  └── PKG_LEAVE.expire_carryover()
        ├── UPDATE LEAVE_BALANCES.OPENING_BALANCE (expire old carryover)
        └── ⚠ BUG: double-expiry if run twice on same day
```

---

## Performance Review Flow

### 9. Review Cycle

```
PKG_PERFORMANCE.create_reviews_for_cycle(p_cycle_id)
  └── INSERT INTO PERFORMANCE_REVIEWS (one per active employee, STATUS='NOT_STARTED')

Employee self-assessment:
  PKG_PERFORMANCE.submit_self_assessment(p_review_id, p_text)
  └── UPDATE PERFORMANCE_REVIEWS.SELF_ASSESSMENT, STATUS='MANAGER_REVIEW'

Manager assessment:
  PKG_PERFORMANCE.complete_review(p_review_id, p_rating, p_assessment)
  ├── UPDATE PERFORMANCE_REVIEWS.OVERALL_RATING, RATING_LABEL, STATUS='COMPLETED'
  └── RATING_LABEL derived from rating:
        ≥4.5 → 'Exceptional'  ≥3.5 → 'Exceeds Expectations'
        ≥2.5 → 'Meets Expectations'  ≥1.5 → 'Needs Improvement'
        <1.5 → 'Unsatisfactory'

Employee acknowledgement:
  PKG_PERFORMANCE.acknowledge_review(p_review_id)
  └── UPDATE PERFORMANCE_REVIEWS.STATUS='ACKNOWLEDGED', EMPLOYEE_ACK_DATE=SYSDATE
```

[SUPPLEMENTED] **Full performance flow confirmed from PKG_PERFORMANCE.pkb:**
```
Review Cycle Lifecycle (state machine):
  create_review_cycle() → REVIEW_CYCLES (STATUS='DRAFT')
  open_review_cycle()   → STATUS='OPEN'    (only from DRAFT; SQL%ROWCOUNT guard)
  close_review_cycle()  → STATUS='CLOSED'  (no status guard — can close from any state)

generate_reviews_for_cycle(p_cycle_id)
  ├── CURSOR: active employees WHERE MANAGER_EMP_ID IS NOT NULL
  ├── Calls create_review() for each; DUP_VAL_ON_INDEX silently skipped
  └── COMMIT after all inserts (single transaction for entire batch)

submit_self_assessment(p_review_id, p_self_assessment)
  ├── UPDATE WHERE STATUS IN ('NOT_STARTED','SELF_REVIEW') — both statuses accepted
  ├── → STATUS='MANAGER_REVIEW'
  └── Notify REVIEWER_EMP_ID: 'Self-Assessment Submitted - Ready for Manager Review'

submit_manager_review(p_review_id, p_overall_rating, p_manager_assessment,
                       p_strengths, p_improvement_areas, p_development_plan)
  ├── Validates: p_overall_rating BETWEEN 1.0 AND 5.0 (hard error -20403)
  ├── → STATUS='COMPLETED'
  ├── Sets RATING_LABEL from CASE expression (same as above)
  └── Notify EMP_ID: 'Performance Review Completed — Please review and acknowledge'

Goal Management:
  add_goal(p_review_id, p_emp_id, p_goal_title, p_category, p_weight_pct, p_target_date)
    └── INSERT INTO PERFORMANCE_GOALS (STATUS='NOT_STARTED', PROGRESS_PCT=0)
  update_goal_progress(p_goal_id, p_progress_pct, p_status)
    └── UPDATE PERFORMANCE_GOALS; auto-sets STATUS to 'COMPLETED' if progress ≥ 100

Team/Reporting queries:
  get_team_reviews(p_cursor, p_manager_id, p_cycle_id)
    └── REF CURSOR: reviews for all direct reports of p_manager_id
  get_rating_distribution(p_cycle_id, p_dept_id)
    └── SYS_REFCURSOR: rating labels with count + percentage (window function)
```

---

## Notification Flow

### 10. Async Email Delivery

```
Any package (PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE)
  │  calls
  ▼
PKG_NOTIFICATION.queue_notification(p_emp_id, p_type, p_subject, p_body)
  └── INSERT INTO NOTIFICATION_QUEUE (STATUS='PENDING')

DBMS_SCHEDULER (implied, every 5 min) → PKG_NOTIFICATION.process_queue()
  ├── SELECT NOTIFICATION_QUEUE WHERE STATUS='PENDING' ORDER BY PRIORITY, CREATED_DATE
  ├── PKG_NOTIFICATION.send_email()
  │     └── UTL_SMTP → smtp.internal.company.com:25
  └── UPDATE NOTIFICATION_QUEUE.STATUS = 'SENT' / 'FAILED'

PKG_NOTIFICATION.retry_failed()
  ├── SELECT NOTIFICATION_QUEUE WHERE STATUS='FAILED' AND RETRY_COUNT < 3
  └── Re-queues; increments RETRY_COUNT
```

---

## Security / Audit Flow

### 11. Authentication

```
Oracle Forms LOGIN_FORM.fmb
  │
  ▼
PKG_SECURITY.authenticate(p_username, p_password)
  ├── SELECT USER_CREDENTIALS  ← ⚠ stub: password hash not actually checked
  ├── SELECT EMPLOYEES.GRADE_ID  ← for permission level
  ├── INSERT USER_SESSIONS
  └── Return SESSION_TOKEN

PKG_SECURITY.has_permission(p_session_id, p_resource, p_action)
  ├── Validate session (LOGIN_TIME + TIMEOUT, NOT last-activity)
  ├── SELECT GRADE_ID from EMPLOYEES via USER_SESSIONS
  └── Grade-based rules:
        grade ≥ 8 → ALL actions
        grade ≥ 5 → VIEW all resources
        any grade → LEAVE (CREATE/VIEW), EMPLOYEE (VIEW)
```

[SUPPLEMENTED] **Full authentication flow confirmed from PKG_SECURITY.pkb:**
```
authenticate(p_username, p_password, p_ip_address)
  ├── SELECT EMP_ID FROM EMPLOYEES
  │       WHERE UPPER(EMAIL)=UPPER(p_username) AND EMPLOYMENT_STATUS='ACTIVE'
  │       ⚠ VULNERABILITY: different error paths for invalid user vs invalid password
  │         create timing side-channel (user enumeration)
  │       ⚠ TOO_MANY_ROWS: silently takes MIN(EMP_ID) — multiple accounts with same email
  │         resolved by picking lowest ID, not raising an error
  ├── ⚠ Password hash is NEVER CHECKED in this procedure body
  │       NOTE inline: "passwords are stored in USER_CREDENTIALS [separate table]"
  │       but no SELECT against USER_CREDENTIALS occurs
  ├── INSERT INTO USER_SESSIONS
  │       (SESSION_ID via SEQ_USER_SESSION.NEXTVAL, EMP_ID, USERNAME,
  │        LOGIN_TIME=SYSDATE, IP_ADDRESS=p_ip_address, SESSION_STATUS='ACTIVE')
  ├── PKG_EMPLOYEE.set_session_context(p_username, v_emp_id)
  │       Sets package globals: g_current_user, g_current_emp_id, g_current_dept_id
  ├── PKG_AUDIT.log_action('USER_SESSIONS', v_session_id, 'INSERT', p_username)
  └── Returns v_session_id (NUMBER)

is_session_valid(p_session_id)
  ├── SELECT SESSION_STATUS, LOGIN_TIME FROM USER_SESSIONS
  ├── If STATUS != 'ACTIVE': return FALSE
  ├── If (SYSDATE - LOGIN_TIME)*24*60 > 30: UPDATE STATUS='EXPIRED', return FALSE
  └── Returns TRUE (no last-activity sliding window — purely time-from-login)

has_permission(p_emp_id, p_module, p_action)
  ├── SELECT e.DEPT_ID, j.GRADE_ID FROM EMPLOYEES e JOIN JOB_TITLES j
  ├── grade ≥ 8 → TRUE (senior management — full access)
  ├── grade ≥ 5 AND p_action='VIEW' → TRUE
  ├── p_module='LEAVE' AND p_action IN ('CREATE','VIEW') → TRUE (all grades)
  ├── p_module='EMPLOYEE' AND p_action='VIEW' → TRUE (all grades)
  └── Otherwise → FALSE
```

[SUPPLEMENTED] **Security weaknesses confirmed from PKG_SECURITY.pkb:**
- `hash_password()` uses `DBMS_CRYPTO.HASH_MD5` — broken for password storage
- `c_encryption_key` is hard-coded as `RAW(32)` literal in the package body
- No brute-force / account lockout mechanism in any confirmed code
- `authenticate` has a known comment: "No brute-force protection (no lockout after N failures)"
- SSN encrypted with AES-256-CBC (`ENCRYPT_AES256 + CHAIN_CBC + PAD_PKCS5`) using that same hard-coded key
- `change_password()` validates complexity (≥8 chars, ≥1 uppercase, ≥1 digit) but the actual
  `UPDATE USER_CREDENTIALS` is a stub ("This is a stub for the legacy system model")

[SUPPLEMENTED] **logout confirmed:**
```
logout(p_session_id)
  └── UPDATE USER_SESSIONS SET LOGOUT_TIME=SYSDATE, SESSION_STATUS='CLOSED'
```

### 12. Audit Trail

```
All data-modifying packages call:
PKG_AUDIT.log_action(p_table, p_id, p_action, p_old, p_new)
  ├── PRAGMA AUTONOMOUS_TRANSACTION (isolated commit)
  ├── INSERT INTO AUDIT_LOG
  └── ⚠ Failures silently swallowed (no re-raise)

Triggers also write audit:
  TRG_SALARY_AUDIT → PKG_AUDIT.log_action (SALARY_RECORDS changes)
  TRG_LEAVE_REQUEST_AUDIT → PKG_AUDIT.log_action (STATUS changes)
  TRG_DEPARTMENT_AUDIT → PKG_AUDIT.log_action (DEPARTMENTS changes)
```

[SUPPLEMENTED] **log_history internal procedure (AUTONOMOUS_TRANSACTION):**
`PKG_EMPLOYEE` contains a private `log_history` procedure that writes to `EMPLOYEE_HISTORY`
directly (not via PKG_AUDIT). It uses `PRAGMA AUTONOMOUS_TRANSACTION` and silently swallows
failures (ROLLBACK + optional DBMS_OUTPUT warning). It captures old/new values for:
dept_id, job_id, manager_id, salary, location_code, reason_code, comments.

Change types written: `HIRE`, `TRANSFER`, `PROMOTION`, `TERMINATION`, `REHIRE`
(constrained by `CHK_CHANGE_TYPE` DDL CHECK on `EMPLOYEE_HISTORY`).

[SUPPLEMENTED] **Trigger-level audit gap:**
`TRG_EMP_BEFORE_UPDATE` writes to `EMPLOYEE_HISTORY` using column names
`HISTORY_ID`/`CHANGE_DATE`/`OLD_VALUE`/`NEW_VALUE` which do **not** match the DDL
(actual DDL columns: `HIST_ID`, `EFFECTIVE_DATE`, `OLD_DEPT_ID`/`NEW_DEPT_ID` etc.).
This trigger will raise `ORA-00904 invalid identifier` at runtime — `EMPLOYEES UPDATE`
events are NOT captured in `EMPLOYEE_HISTORY` via the trigger path.
`PKG_EMPLOYEE.log_history` (called explicitly from transfer/promote/terminate) is the
only reliable audit path for employee changes.

---

## Reporting Flow

### 13. On-Demand Reports (PKG_REPORTING)

All 7 report procedures open a REF CURSOR that queries OLTP tables directly at call time. They do NOT read from RPT_* tables.

```
Oracle Forms (report form / Oracle Reports .rdf)
  │  calls
  ▼
PKG_REPORTING.<report_procedure>(p_cursor OUT, p_params...)
  │
  ├── headcount_report(p_as_of_date, p_dept_id, p_location)
  │     └── SELECT EMPLOYEES JOIN DEPARTMENTS LEFT JOIN LOCATIONS
  │           WHERE EMPLOYMENT_STATUS='ACTIVE' AND HIRE_DATE <= p_as_of_date
  │           AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)
  │
  ├── compensation_summary(p_dept_id, p_grade_id)
  │     └── SELECT EMPLOYEES JOIN DEPARTMENTS JOIN JOB_TITLES JOIN JOB_GRADES
  │                          JOIN SALARY_RECORDS (ACTIVE_FLAG='Y')
  │           WHERE EMPLOYMENT_STATUS='ACTIVE'
  │           Computes: COMPA_RATIO = AVG(BASE_SALARY / grade_midpoint) * 100
  │
  ├── turnover_report(p_start_date, p_end_date, p_dept_id)
  │     └── SELECT EMPLOYEES JOIN DEPARTMENTS
  │           Computes: TURNOVER_PCT = terminations / hires_up_to_end × 100
  │           HAVING COUNT(hires) > 0  ← departments with no history excluded
  │
  ├── new_hires_report(p_start_date, p_end_date, p_dept_id)
  │     └── SELECT EMPLOYEES JOIN DEPARTMENTS JOIN JOB_TITLES
  │                          LEFT JOIN LOCATIONS LEFT JOIN EMPLOYEES m (manager)
  │                          LEFT JOIN SALARY_RECORDS (ACTIVE_FLAG='Y')
  │           WHERE HIRE_DATE BETWEEN p_start_date AND p_end_date
  │
  ├── leave_utilization_report(p_year, p_dept_id)
  │     └── SELECT LEAVE_BALANCES JOIN EMPLOYEES JOIN DEPARTMENTS JOIN LEAVE_TYPES
  │           WHERE CALENDAR_YEAR = p_year AND EMPLOYMENT_STATUS='ACTIVE'
  │
  ├── payroll_summary_report(p_period_id)
  │     └── SELECT PAYROLL_DETAILS JOIN PAYROLL_RUNS JOIN EMPLOYEES JOIN DEPARTMENTS
  │           WHERE PERIOD_ID = p_period_id AND pd.STATUS != 'ERROR'
  │           ⚠ Magic numbers: ELEMENT_ID 100=FED_TAX, 101=STATE_TAX, 102=SS, 103=MEDICARE
  │
  └── eeo_compliance_report(p_as_of_date)
        └── SELECT EMPLOYEES JOIN JOB_TITLES
              WHERE EMPLOYMENT_STATUS='ACTIVE' AND HIRE_DATE <= p_as_of_date
              GROUP BY j.EEO_CATEGORY
```

### 14. Nightly Reporting Table Refresh (Stub — NOT IMPLEMENTED)

```
DBMS_SCHEDULER (implied nightly job) → PKG_REPORTING.refresh_reporting_tables(p_user)
  └── ⚠ STUB — only calls PKG_COMMON.log_info('PKG_REPORTING','refresh_reporting_tables',
                  'Reporting tables refreshed', p_user)
      No TRUNCATE, no INSERT, no SELECT.
      RPT_HEADCOUNT / RPT_COMPENSATION / RPT_TURNOVER / RPT_NEW_HIRES /
      RPT_LEAVE_UTILIZATION / RPT_PAYROLL_SUMMARY / RPT_EEO_COMPLIANCE
      are NEVER POPULATED by this procedure.
```

---

## Data Flow Summary Table

| Flow | Source | Destination | Transform | Frequency |
|------|--------|-------------|-----------|-----------|
| Employee hire | Oracle Forms | EMPLOYEES, SALARY_RECORDS, LEAVE_BALANCES | PKG_EMPLOYEE | On demand |
| Payroll calc | EMPLOYEES, SALARY_RECORDS, PAY_ELEMENTS | PAYROLL_DETAILS | PKG_PAYROLL | Monthly/biweekly |
| GL journal | PAYROLL_DETAILS | GL_FEED_OUT (file) | PKG_INTEGRATION | Post payroll run |
| Benefits feed | EMPLOYEES, EMPLOYEE_DEPENDENTS | BENEFITS_FEED_OUT (ADP) | PKG_INTEGRATION | Periodic |
| Leave accrual | LEAVE_TYPES | LEAVE_BALANCES, LEAVE_ACCRUAL_LOG | PKG_LEAVE | Monthly (scheduled) |
| Notification | Any package | NOTIFICATION_QUEUE → SMTP → email | PKG_NOTIFICATION | Near real-time (5 min) |
| Audit | All DML | AUDIT_LOG | PKG_AUDIT | Every DML event |
| Time import | TIME_ATTENDANCE_IN (CSV file) | TIME_ATTENDANCE_RECORDS (implied — no DDL) | PKG_INTEGRATION.import_time_attendance (TODO STUB — no DML) | Periodic (TODO — frequency undefined) |
| On-demand reports | OLTP tables (direct) | REF CURSOR → Oracle Forms | PKG_REPORTING (7 procs) | On demand |
| RPT_* refresh | OLTP tables | RPT_* (7 tables — inferred) | PKG_REPORTING.refresh_reporting_tables | Nightly (STUB — never runs) |

---

## [SUPPLEMENTED] PKG_COMMON Utility Flows

PKG_COMMON provides cross-cutting services called by all other packages.

### SYSTEM_PARAMETERS Read/Write

```
PKG_COMMON.get_param(p_group, p_code) → VARCHAR2
PKG_COMMON.get_param_number(p_group, p_code) → NUMBER
PKG_COMMON.get_param_date(p_group, p_code) → DATE
  └── SELECT PARAM_VALUE FROM SYSTEM_PARAMETERS WHERE PARAM_GROUP=p_group AND PARAM_CODE=p_code

PKG_COMMON.set_param(p_group, p_code, p_value, p_user)
  └── UPDATE SYSTEM_PARAMETERS WHERE EDITABLE_FLAG='Y'
      ⚠ Raises -20900 if param not found or EDITABLE_FLAG='N'
```

Known SYSTEM_PARAMETERS values (from seed data):
| PARAM_GROUP  | PARAM_CODE             | VALUE                          |
|-------------|------------------------|--------------------------------|
| SYSTEM      | APP_VERSION            | 4.2.0                          |
| SYSTEM      | COMPANY_NAME           | Acme Corporation               |
| PAYROLL     | DEFAULT_PAY_FREQUENCY  | MONTHLY                        |
| PAYROLL     | FISCAL_YEAR_START      | 10 (October)                   |
| SECURITY    | SESSION_TIMEOUT_MIN    | 30                             |
| SECURITY    | PASSWORD_MIN_LENGTH    | 8                              |
| NOTIFICATION| SMTP_HOST              | smtp.internal.company.com      |
| NOTIFICATION| FROM_ADDRESS           | hrms-noreply@company.com       |
| INTEGRATION | GL_FEED_STATUS         | ACTIVE                         |
| INTEGRATION | BENEFITS_FEED_STATUS   | ACTIVE                         |

### Date / Fiscal Utility Functions

```
PKG_COMMON.get_fiscal_year(p_date)   → month ≥ Oct: year+1, else year
PKG_COMMON.get_fiscal_quarter(p_date)
  → Oct/Nov/Dec = Q1 | Jan/Feb/Mar = Q2 | Apr/May/Jun = Q3 | Jul/Aug/Sep = Q4
PKG_COMMON.business_days_between(p_start, p_end)
  → day-loop counting Mon–Fri ONLY (does NOT exclude HOLIDAYS table)
  ⚠ Different from PKG_LEAVE.calculate_business_days() which does exclude HOLIDAYS
PKG_COMMON.add_business_days(p_date, p_days)
  → same loop logic, returns resulting date
```

### Logging

```
PKG_COMMON.log_error(p_package, p_procedure, p_message, p_user)
  └── PRAGMA AUTONOMOUS_TRANSACTION → INSERT INTO AUDIT_LOG (ACTION_TYPE='INSERT',
      TABLE_NAME='ERROR_LOG', NEW_VALUES=JSON with package/procedure/message)
      ⚠ On failure: DBMS_OUTPUT.PUT_LINE (last resort — silently lost in batch)

PKG_COMMON.log_info(p_package, p_procedure, p_message, p_user)
  └── PRAGMA AUTONOMOUS_TRANSACTION → INSERT INTO AUDIT_LOG (TABLE_NAME='INFO_LOG')
      ⚠ On failure: silently ROLLBACK (no fallback output)
```

### Format Utilities

```
PKG_COMMON.format_phone(p_phone)    → "(NXX) NXX-XXXX" or "+1 (NXX) NXX-XXXX"
PKG_COMMON.format_ssn_masked(p_ssn) → "***-**-NNNN" (last 4 digits only)
PKG_COMMON.format_currency(p_amount, p_code) → "$NNN,NNN.NN" (USD default)
PKG_COMMON.format_name(p_first, p_last, p_format)
  → 'FL' (default): "First Last"  |  'LF': "Last, First"

PKG_COMMON.is_valid_email(p_email) → REGEXP_LIKE (server-side, permissive)
PKG_COMMON.is_valid_phone(p_phone) → 10–11 stripped digits
PKG_COMMON.is_valid_ssn(p_ssn)    → 9 stripped digits
```

---

## [SUPPLEMENTED] Employee Query Flows

### Search Employees (Dynamic SQL — SQL Injection Risk)

```
PKG_EMPLOYEE.search_employees(p_cursor OUT, p_last_name, p_first_name,
                               p_dept_id, p_status, p_location_code,
                               p_hire_date_from, p_hire_date_to)
  ├── Builds VARCHAR2(4000) SQL string via concatenation
  ├── ⚠ VULNERABILITY: p_last_name, p_first_name, p_status, p_location_code
  │       injected as string literals (not bind variables)
  │   Comment in code: "Forms LOV passes validated values, but direct calls are vulnerable"
  └── OPEN p_cursor FOR v_sql (native dynamic SQL)
```

### Org Chart / Hierarchy Queries

```
PKG_EMPLOYEE.get_org_chart(p_root_emp_id, p_max_depth DEFAULT 10)
  └── CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID
      WHERE EMPLOYMENT_STATUS='ACTIVE'
      START WITH EMP_ID=p_root_emp_id
      AND LEVEL <= p_max_depth
      ⚠ Known to time out for orgs > 500 employees

PKG_EMPLOYEE.get_direct_reports(p_manager_emp_id) → t_emp_id_table
  └── SELECT EMP_ID FROM EMPLOYEES WHERE MANAGER_EMP_ID=p_manager_emp_id
      AND EMPLOYMENT_STATUS='ACTIVE'

PKG_EMPLOYEE.get_headcount_by_dept(p_dept_id, p_as_of_date)
  └── COUNT(*) WHERE EMPLOYMENT_STATUS='ACTIVE' AND HIRE_DATE <= p_as_of_date
      AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)

PKG_EMPLOYEE.get_tenure_years(p_emp_id)
  └── ROUND(MONTHS_BETWEEN(NVL(TERMINATION_DATE,SYSDATE), HIRE_DATE) / 12, 1)
```

### Session / Context

```
PKG_EMPLOYEE.set_session_context(p_user, p_emp_id)
  ├── Sets package globals: g_current_user, g_current_emp_id
  └── SELECT DEPT_ID INTO g_current_dept_id FROM EMPLOYEES WHERE EMP_ID=p_emp_id

PKG_EMPLOYEE.is_active(p_emp_id) → BOOLEAN
  └── EMPLOYMENT_STATUS='ACTIVE'; returns FALSE on NO_DATA_FOUND

PKG_EMPLOYEE.emp_exists(p_emp_id) → BOOLEAN
  └── COUNT(*) > 0

PKG_EMPLOYEE.validate_employee(p_emp_id) → BOOLEAN
  └── Checks FIRST_NAME/LAST_NAME/HIRE_DATE NOT NULL, ACTIVE_FLAG='Y' when status ACTIVE
```

---

## [SUPPLEMENTED] Reference Data (Seed Values)

### Locations (3 confirmed)
| CODE | NAME | CITY | STATE |
|------|------|------|-------|
| HQ   | Corporate Headquarters | New York | NY |
| CHI  | Chicago Regional Office | Chicago | IL |
| SF   | San Francisco Branch | San Francisco | CA |

### Job Grades (10 levels, salary bands from seed)
| Grade | Name | Min Salary | Max Salary |
|-------|------|-----------|-----------|
| 1 | Entry Level | $35,000 | $55,000 |
| 2 | Junior | $45,000 | $70,000 |
| 3 | Mid-Level | $60,000 | $90,000 |
| 4 | Senior | $80,000 | $120,000 |
| 5 | Lead | $95,000 | $145,000 |
| 6 | Manager | $110,000 | $170,000 |
| 7 | Senior Manager | $130,000 | $200,000 |
| 8 | Director | $160,000 | $250,000 |
| 9 | VP | $200,000 | $350,000 |
| 10 | C-Suite | $300,000 | $600,000 |

Permission threshold: Grade ≥ 8 = full system access; Grade ≥ 5 = view all.

### Leave Types (6 confirmed)
| Code | Name | Accrual Rate | Tenure Gate | Carryover Max |
|------|------|-------------|-------------|---------------|
| PTO | Paid Time Off | 1.25 days/month | none | 5 days |
| SICK | Sick Leave | 0.833 days/month | none | 10 days |
| COMP | Compensatory Time | none (earned) | 90 days | 0 |
| FMLA | Family Medical Leave | none | 365 days | 0 |
| JURY | Jury Duty | none | none | 0 |
| BEREAVE | Bereavement | none | none | 0 |

### Pay Elements (confirmed IDs — used as magic numbers in PKG_REPORTING)
| ID | Code | Type | Calculation |
|----|------|------|-------------|
| 1 | BASE_PAY | EARNING | FLAT |
| 100 | FED_TAX | TAX | FORMULA |
| 101 | STATE_TAX | TAX | FORMULA |
| 102 | FICA | TAX | FORMULA |
| 103 | MEDICARE | TAX | FORMULA |
| 200 | 401K_EE | DEDUCTION | PERCENTAGE (6%, pre-tax) |
| 201 | MED_EE | BENEFIT | FLAT ($250/month, pre-tax) |
| 202 | DENTAL_EE | BENEFIT | FLAT ($45/month, pre-tax) |
| 203 | VISION_EE | BENEFIT | FLAT ($15/month, pre-tax) |
| 204 | LIFE_INS | BENEFIT | FLAT ($25/month, post-tax) |
| 205 | HSA | DEDUCTION | FLAT ($150/month, pre-tax) |

### Departments (10 confirmed)
| ID | Code | Name | Parent | Location |
|----|------|------|--------|----------|
| 1 | EXEC | Executive Office | — | HQ |
| 10 | HR | Human Resources | EXEC | HQ |
| 20 | FIN | Finance & Accounting | EXEC | HQ |
| 30 | IT | Information Technology | EXEC | CHI |
| 31 | ITDEV | IT - Development | IT | CHI |
| 32 | ITOPS | IT - Operations | IT | CHI |
| 40 | SALES | Sales | EXEC | SF |
| 50 | MKT | Marketing | EXEC | SF |
| 60 | OPS | Operations | EXEC | CHI |
| 70 | LEGAL | Legal & Compliance | EXEC | HQ |
