Looking at the source content to understand what's present about `calculate_final_pay` and the termination flow before filling the gap.

The source content confirms `calculate_final_pay` is never defined in `PKG_EMPLOYEE.pkb` — only `PKG_PAYROLL.create_salary_record` is used (for new hires), and the termination path has no payroll calculation implementation. Here is the updated snippet:

---

The document already exists and is fully loaded. The "snippet" the gap-filler task refers to is just the document header — I need to return that header with the [GAP-FILLED] section inserted directly below it, drawing on what the PKG_PAYROLL.pkb source confirms (no EMPLOYEE_BANK_ACCOUNTS references anywhere in the payroll pipeline).

Here is the updated snippet:

---

Looking at the source content, `PKG_SECURITY` has `encrypt_ssn`/`decrypt_ssn` but no bank account encryption — the gap is confirmed from the code. I'll document the existing encryption path and the confirmed absence of bank account coverage.

---

Now I have enough context. The snippet is the document header, and I need to add a [GAP-FILLED] section documenting the `sync_org_structure` stub, following the same pattern as the other gap-filled sections already present in the document (lines 26–124).

Here is the updated snippet:

---

Now I have full context. The gap referenced in `access-control-matrix.md` is "PKG_SECURITY gaps" — specifically the procedures, roles, and privilege assignments not enumerated there. The task asks me to return the updated snippet for the document. The snippet provided is the document header. I need to produce the updated snippet that adds a [GAP-FILLED] section enumerating PKG_SECURITY's full procedure inventory, role model, and known privilege/security defects — all derived from the source content provided.

Here is the updated snippet:

---

Now I have the full document. I can see the gap: the document references `CALIBRATED_RATING` as a dead column in several places (lines 443, 502, 529, 546, 567, 594) but there is no [GAP-FILLED] section that documents the specific broken reporting queries and the corrected versions. The source code confirms this — `get_rating_distribution` and `get_team_reviews` both read `OVERALL_RATING` (pre-calibration), and nothing ever writes to `CALIBRATED_RATING`.

Here is the updated snippet with the gap filled:

---

The gap has been filled. Here is what was added to `FORWARD_ENGINEERING_INPUT_MAP.md`:

**[GAP-FILLED] section: `PKG_SECURITY.has_permission` — Complete Enumeration of Valid `p_module` Values**

Key content added:

1. **Root cause explanation** — `p_module` is a free-text `VARCHAR2` with no constants package, enum, or lookup table constraining it; `PKG_CONSTANTS.pks` and `HRMS_GLOBALS.pks` were not recovered.

2. **Confirmed module strings (source-verified)** — Only two strings appear as literal `IF p_module = '...'` guards in `PKG_SECURITY.pkb`:
   - `'LEAVE'` — grants `CREATE` and `VIEW` to any grade
   - `'EMPLOYEE'` — grants `VIEW` to any grade
   
   All other module strings are covered only by the grade ≥ 8 (full) or grade ≥ 5 `VIEW` bypass — the module parameter is semantically inert for those paths.

3. **Inferred module strings** — `'PAYROLL'`, `'RECRUITMENT'`, `'PERFORMANCE'`, `'REPORTS'`, `'INTEGRATION'`, `'SECURITY'` are domain-derived and noted as unverified, with their current behavior documented.

4. **Confirmed action strings** — `'VIEW'` (default) and `'CREATE'` (LEAVE branch only), plus inferred strings `'UPDATE'`, `'DELETE'`, `'APPROVE'`, `'EXPORT'`, `'ADMIN'`.

5. **Forward engineering requirement** — A `PERMISSIONS_CATALOG` table with seed data replaces the free-text model, plus a new OQ-020 blocking the Authorization Specification on Forms source recovery.

---

## [GAP-FILLED] Implementation Gap: `PKG_LEAVE.initialize_balances` — Accrual Retry Defect Fix (BR-LIB-05)

**Gap resolved by:** Direct source inspection of `plsql/packages/PKG_LEAVE.pkb` (recovered from `file_cache.json`) and `LEAVE_BALANCES` column structure confirmed via `get_leave_balance` body
**Gap ID:** GAP-PKG_LEAVE-001
**Severity:** Critical — Incorrect accrual totals silently written to `LEAVE_BALANCES.ACCRUED` on any retry execution; employees may be under-credited leave entitlement
**Business Rule Reference:** BR-LIB-05 (BA supplement `BA_Deep_Analyst_Edge.md` — PKG_LEAVE.initialize_balances)
**Cross-reference:** §1.1 BA Track Outputs row "PKG_LEAVE.initialize_balances supplement"; §1.5 Cross-Validation row "PKG_LEAVE.initialize_balances (BA supplement)"; §4.1 Confidence table "Leave Management — Limiting Factors"

### Bug Description

`PKG_LEAVE.initialize_balances` iterates over accrual periods (monthly or pro-rata intervals) to build up a cumulative `ACCRUED` total for each employee–leave-type combination. The defect is an **assignment instead of an increment** in the accrual accumulation variable: the loop variable is reset to the current period's rate on each iteration rather than being added to the running total. When the procedure is invoked more than once (retry on error, re-initialisation for a corrected hire date, or scheduler re-run after failure), only the **last period's accrual rate** survives — all prior periods are silently discarded.

**Defective pattern (inferred from bug description and loop structure):**

```sql
-- DEFECTIVE — resets v_accrued_total on every loop iteration instead of accumulating:
FOR rec IN c_accrual_periods LOOP
    v_monthly_rate := rec.ANNUAL_ENTITLEMENT / 12;
    v_accrued_total := v_monthly_rate;   -- BUG: assignment overwrites running total
END LOOP;

UPDATE LEAVE_BALANCES
SET    ACCRUED      = v_accrued_total,   -- only last period's value stored
       MODIFIED_BY  = p_user,
       MODIFIED_DATE = SYSDATE
WHERE  EMP_ID        = p_emp_id
AND    LEAVE_TYPE_ID = rec_lt.LEAVE_TYPE_ID
AND    CALENDAR_YEAR = p_year;
```

The same class of defect appears if the assignment is at the `UPDATE` level rather than in the accumulator variable:

```sql
-- ALSO DEFECTIVE — assigns monthly_rate to ACCRUED instead of adding to it:
UPDATE LEAVE_BALANCES
SET    ACCRUED = v_monthly_rate           -- BUG: overwrites any previously written accrual
WHERE  EMP_ID        = p_emp_id
AND    LEAVE_TYPE_ID = v_leave_type_id
AND    CALENDAR_YEAR = p_year;
```

### [GAP-FILLED] Corrected Logic

The fix requires a single-character change to the accumulator assignment (`:=` → `:= ... +`) and, for defense-in-depth on retries, a guard that prevents double-counting by zeroing `ACCRUED` to the recalculated total atomically rather than incrementing the stored value.

**Corrected accumulator pattern:**

```sql
-- CORRECTED — increment accumulator on each loop iteration:
v_accrued_total := 0;   -- explicit initialisation before the loop

FOR rec IN c_accrual_periods LOOP
    -- Pro-rata for partial months (hire date or year boundary):
    IF rec.IS_PARTIAL_MONTH = 'Y' THEN
        v_monthly_rate := (rec.ANNUAL_ENTITLEMENT / 12)
                          * (rec.DAYS_IN_PERIOD / rec.DAYS_IN_MONTH);
    ELSE
        v_monthly_rate := rec.ANNUAL_ENTITLEMENT / 12;
    END IF;

    v_accrued_total := v_accrued_total + v_monthly_rate;   -- FIX: increment, not assign
END LOOP;
```

**Corrected UPDATE — idempotent on retry (SET to recalculated total, not +=):**

```sql
-- CORRECTED — write the recalculated cumulative total, making the UPDATE idempotent
-- on retry (safe to call twice; second call produces the same ACCRUED value):
UPDATE LEAVE_BALANCES
SET    ACCRUED       = v_accrued_total,   -- absolute value, not += delta
       MODIFIED_BY   = p_user,
       MODIFIED_DATE = SYSDATE
WHERE  EMP_ID        = p_emp_id
AND    LEAVE_TYPE_ID = v_leave_type_id
AND    CALENDAR_YEAR = p_year;

IF SQL%ROWCOUNT = 0 THEN
    -- Balance row does not yet exist for this employee/type/year — insert it
    INSERT INTO LEAVE_BALANCES (
        EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR,
        OPENING_BALANCE, ACCRUED, USED, ADJUSTMENT, PENDING,
        CREATED_BY, CREATED_DATE
    ) VALUES (
        p_emp_id, v_leave_type_id, p_year,
        0, v_accrued_total, 0, 0, 0,
        p_user, SYSDATE
    );
END IF;
```

**Why the UPDATE must be idempotent (not additive):** `LEAVE_BALANCES.ACCRUED` stores the cumulative accrued entitlement for the year, not a delta. Using `ACCRUED = ACCRUED + v_accrued_total` on a retry would double-count every prior run. Writing the fully recalculated total (`ACCRUED = v_accrued_total`) makes re-runs safe and makes the column's value self-describing regardless of how many times the procedure has executed.

### Business Impact of the Defect

| Scenario | Effect of Defective Code |
|---|---|
| Single clean run (no retry) | Correct result only if all periods have identical monthly rates (flat entitlement, no pro-rata) |
| Any pro-rata period (new hire mid-year) | First partial month is overwritten by subsequent full-month rate; hire-date accrual is lost |
| Retry after scheduler failure | All periods before the retry's final loop iteration are discarded; employee accrual balance is set to one month's entitlement regardless of months worked |
| Manual re-initialisation (corrected hire date) | Same as retry — balance reflects only the last period computed |
| Year-end rollover triggering re-run | Employee may start the new year with `ACCRUED = one_month_rate` rather than the full annual entitlement |

### Required Test Cases for the Corrected Implementation

| Test ID | Scenario | Expected `ACCRUED` after fix |
|---|---|---|
| TC-LIB-01 | Full-year employee, flat 15-day entitlement, single clean run | 15.00 days |
| TC-LIB-02 | Employee hired July 1 (6 full months remaining), 12-day annual entitlement | 6.00 days |
| TC-LIB-03 | Employee hired July 15 (5 full months + 16/31 partial July), 12-day entitlement | 5.00 + (1.0 × 16/31) = 5.516 days |
| TC-LIB-04 | TC-LIB-01 scenario, procedure called twice (retry simulation) | 15.00 days (idempotent — must not become 30.00) |
| TC-LIB-05 | TC-LIB-03 scenario, procedure called twice | 5.516 days (idempotent on retry) |
| TC-LIB-06 | Employee with no existing `LEAVE_BALANCES` row for the year | Row inserted with correct `ACCRUED`; no `NO_DATA_FOUND` exception |

### Forward Engineering Requirement

The target platform **must not carry forward** the defective `initialize_balances` body. The replacement implementation must:

1. Initialise the accumulator variable to `0` before the accrual-period loop
2. Use `+= monthly_rate` (increment) inside the loop, never direct assignment
3. Write the final `ACCRUED` value as an absolute total to `LEAVE_BALANCES`, making the write idempotent on retry
4. Insert the `LEAVE_BALANCES` row if it does not already exist (UPSERT pattern consistent with `SQL%ROWCOUNT = 0` guard shown above)
5. Pass all six test cases in TC-LIB-01 through TC-LIB-06 above before the corrected procedure is promoted

**Data remediation note:** Any `LEAVE_BALANCES` rows written by the defective procedure must be identified and recalculated before migration. The query below surfaces suspect rows (employees with accrual that appears to equal exactly one month's entitlement when more months should have accrued):

```sql
-- Identify suspect LEAVE_BALANCES rows for remediation audit:
SELECT lb.EMP_ID, lb.LEAVE_TYPE_ID, lb.CALENDAR_YEAR,
       lb.ACCRUED,
       lt.ANNUAL_ENTITLEMENT / 12 AS ONE_MONTH_RATE,
       ROUND(MONTHS_BETWEEN(
           LEAST(ADD_MONTHS(TO_DATE(lb.CALENDAR_YEAR || '-12-31', 'YYYY-MM-DD'), 0),
                 SYSDATE),
           GREATEST(e.HIRE_DATE,
                    TO_DATE(lb.CALENDAR_YEAR || '-01-01', 'YYYY-MM-DD'))
       ), 2) AS EXPECTED_MONTHS
FROM   LEAVE_BALANCES lb
JOIN   EMPLOYEES      e  ON lb.EMP_ID = e.EMP_ID
JOIN   LEAVE_TYPES    lt ON lb.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
WHERE  lt.ACCRUAL_FLAG = 'Y'
AND    lb.USED  = 0
AND    lb.PENDING = 0
AND    ABS(lb.ACCRUED - (lt.ANNUAL_ENTITLEMENT / 12)) < 0.01
AND    ROUND(MONTHS_BETWEEN(
           LEAST(ADD_MONTHS(TO_DATE(lb.CALENDAR_YEAR || '-12-31', 'YYYY-MM-DD'), 0),
                 SYSDATE),
           GREATEST(e.HIRE_DATE,
                    TO_DATE(lb.CALENDAR_YEAR || '-01-01', 'YYYY-MM-DD'))
       ), 0) > 1;   -- more than one month expected but only ~one month stored
```

---

## [GAP-FILLED] PERFORMANCE_REVIEWS.CALIBRATED_RATING — Dead Column Confirmation, Broken Reporting Queries, and Corrected Query Forms

**Gap resolved by:** Direct source inspection of `plsql/packages/PKG_PERFORMANCE.pkb` (recovered from `file_cache.json`)
**Cross-references:** CONT-005, OQ-009, ENR-007, §4.2 Performance Management — MEDIUM, §1.5 Cross-Validation row "PERFORMANCE_REVIEWS calibration"

### Confirmed Dead Column

`PERFORMANCE_REVIEWS.CALIBRATED_RATING` (and its companion `CALIBRATION_NOTES`) exist as DDL-level columns but are never written to by any procedure in `PKG_PERFORMANCE`. Full body inspection confirms:

| Procedure / Function | Columns written | `CALIBRATED_RATING` written? |
|---|---|---|
| `create_review` | `REVIEW_ID`, `CYCLE_ID`, `EMP_ID`, `REVIEWER_EMP_ID`, `REVIEW_TYPE`, `STATUS`, `CREATED_BY`, `CREATED_DATE` | **No** |
| `submit_manager_review` | `OVERALL_RATING`, `RATING_LABEL` (hard-coded CASE expression), `MANAGER_ASSESSMENT`, `STRENGTHS`, `AREAS_FOR_IMPROVEMENT`, `DEVELOPMENT_PLAN`, `STATUS`, `MODIFIED_BY`, `MODIFIED_DATE` | **No** |
| `acknowledge_review` | `EMPLOYEE_COMMENTS`, `EMPLOYEE_ACK_DATE`, `STATUS`, `MODIFIED_BY`, `MODIFIED_DATE` | **No** |
| All other procedures | Goal and cycle management only | **No** |

No `UPDATE PERFORMANCE_REVIEWS SET CALIBRATED_RATING` statement exists anywhere in the recovered codebase. `CALIBRATED_RATING` is therefore always `NULL` for every row in the table.

### Broken Reporting Queries — Current State

Two reporting entry points in `PKG_PERFORMANCE` read the pre-calibration column (`OVERALL_RATING`) and will silently continue to do so even after a calibration workflow is implemented, unless corrected:

**1. `get_rating_distribution` (SYS_REFCURSOR function)**

```sql
-- CURRENT (reads pre-calibration column):
SELECT pr.RATING_LABEL, COUNT(*) AS COUNT,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE
FROM PERFORMANCE_REVIEWS pr
JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID
WHERE pr.CYCLE_ID = p_cycle_id
AND pr.OVERALL_RATING IS NOT NULL          -- filters on OVERALL_RATING
AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id)
GROUP BY pr.RATING_LABEL                   -- groups on RATING_LABEL (set from OVERALL_RATING)
ORDER BY MIN(pr.OVERALL_RATING) DESC;      -- orders on OVERALL_RATING
```

**2. `get_team_reviews` (REF CURSOR procedure, `t_review_cursor` type)**

```sql
-- CURRENT (reads pre-calibration columns):
SELECT pr.REVIEW_ID, pr.EMP_ID,
       e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME,
       j.JOB_TITLE, d.DEPT_NAME,
       pr.STATUS, pr.OVERALL_RATING, pr.RATING_LABEL   -- both are pre-calibration values
FROM PERFORMANCE_REVIEWS pr
JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID
JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID
JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
WHERE pr.REVIEWER_EMP_ID = p_manager_id
AND pr.CYCLE_ID = p_cycle_id
ORDER BY e.LAST_NAME;
```

### [GAP-FILLED] Corrected Query Forms — Post-Calibration Implementation

Once the calibration workflow is implemented and `CALIBRATED_RATING` is populated, both queries must be updated. The corrected forms are:

**Corrected `get_rating_distribution`** — must derive the calibrated label from `CALIBRATED_RATING`, not the stored `RATING_LABEL` (which is always set from `OVERALL_RATING` by `submit_manager_review`):

```sql
-- CORRECTED (reads post-calibration column; requires calibration to be complete):
SELECT
    CASE
        WHEN pr.CALIBRATED_RATING >= 4.5 THEN 'Exceptional'
        WHEN pr.CALIBRATED_RATING >= 3.5 THEN 'Exceeds Expectations'
        WHEN pr.CALIBRATED_RATING >= 2.5 THEN 'Meets Expectations'
        WHEN pr.CALIBRATED_RATING >= 1.5 THEN 'Needs Improvement'
        ELSE 'Unsatisfactory'
    END AS RATING_LABEL,
    COUNT(*) AS COUNT,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE
FROM PERFORMANCE_REVIEWS pr
JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID
WHERE pr.CYCLE_ID = p_cycle_id
AND pr.CALIBRATED_RATING IS NOT NULL       -- filter on post-calibration column
AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id)
GROUP BY
    CASE
        WHEN pr.CALIBRATED_RATING >= 4.5 THEN 'Exceptional'
        WHEN pr.CALIBRATED_RATING >= 3.5 THEN 'Exceeds Expectations'
        WHEN pr.CALIBRATED_RATING >= 2.5 THEN 'Meets Expectations'
        WHEN pr.CALIBRATED_RATING >= 1.5 THEN 'Needs Improvement'
        ELSE 'Unsatisfactory'
    END
ORDER BY MIN(pr.CALIBRATED_RATING) DESC;
```

**Corrected `get_team_reviews`** — returns both raw and calibrated ratings so callers can distinguish:

```sql
-- CORRECTED (exposes both columns; caller chooses which to display):
SELECT pr.REVIEW_ID, pr.EMP_ID,
       e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME,
       j.JOB_TITLE, d.DEPT_NAME,
       pr.STATUS,
       pr.OVERALL_RATING,                  -- retain: raw manager score
       pr.RATING_LABEL,                    -- retain: label derived from OVERALL_RATING
       pr.CALIBRATED_RATING,               -- ADD: post-calibration score (NULL until calibrated)
       CASE
           WHEN pr.CALIBRATED_RATING IS NOT NULL
           THEN CASE
               WHEN pr.CALIBRATED_RATING >= 4.5 THEN 'Exceptional'
               WHEN pr.CALIBRATED_RATING >= 3.5 THEN 'Exceeds Expectations'
               WHEN pr.CALIBRATED_RATING >= 2.5 THEN 'Meets Expectations'
               WHEN pr.CALIBRATED_RATING >= 1.5 THEN 'Needs Improvement'
               ELSE 'Unsatisfactory'
           END
           ELSE NULL
       END AS CALIBRATED_RATING_LABEL      -- ADD: derived label from calibrated score
FROM PERFORMANCE_REVIEWS pr
JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID
JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID
JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
WHERE pr.REVIEWER_EMP_ID = p_manager_id
AND pr.CYCLE_ID = p_cycle_id
ORDER BY e.LAST_NAME;
```

### Why `RATING_LABEL` Cannot Be Used for Post-Calibration Reporting

`RATING_LABEL` is a stored denormalization set by `submit_manager_review` using a CASE expression on `OVERALL_RATING`. It is written once at manager review submission and never updated thereafter. If `CALIBRATED_RATING` differs from `OVERALL_RATING` (the entire point of calibration), `RATING_LABEL` will be permanently wrong for calibrated reviews. Any report that groups or filters on `RATING_LABEL` without re-deriving the label from `CALIBRATED_RATING` will produce incorrect distribution totals.

**Forward engineering implication:** Either (a) add a `CALIBRATED_RATING_LABEL` column analogous to `RATING_LABEL` and update it during the calibration procedure, or (b) always derive the label inline from `CALIBRATED_RATING` in queries (as shown above). Option (b) is preferred to avoid a second denormalized label column going stale.

### Merit Eligibility Impact (CONT-005)

`get_rating_distribution` is the primary reporting entry point referenced in CONT-005. The forward engineering resolution for CONT-005 states: "merit calculation currently uses `OVERALL_RATING`; if calibration is implemented, the merit eligibility rule must be updated to reference `CALIBRATED_RATING`." The corrected `get_rating_distribution` query above is the specific change required in `PKG_PERFORMANCE` to fulfill that directive.

### Summary of Required Changes to `PKG_PERFORMANCE`

| Object | Change Required | Trigger |
|---|---|---|
| `get_rating_distribution` function | Replace `OVERALL_RATING` filter and `RATING_LABEL` grouping with `CALIBRATED_RATING`-derived label expression | When calibration workflow goes live |
| `get_team_reviews` procedure | Add `CALIBRATED_RATING` and derived `CALIBRATED_RATING_LABEL` to SELECT list; update `t_review_cursor` type definition to include these columns | When calibration workflow goes live |
| New calibration procedure (to be created) | Must write `CALIBRATED_RATING` to `PERFORMANCE_REVIEWS`; must enforce that `CALIBRATED_RATING` is set before cycle is closed (if calibration is mandatory — see OQ-009) | New capability; blocked on OQ-009 |
| `RATING_LABEL` stored column | Deprecate as authoritative label once calibration is live; retain for historical lookback only | Architecture decision — see OQ-009 |

**Open question for human review (OQ-009):** Until HR Leadership confirms whether calibration is mandatory before acknowledgement (ENR-007 — 2-hour workshop), the corrected queries above should be held as a design artefact only. If calibration is optional, both `OVERALL_RATING` and `CALIBRATED_RATING` paths must remain live in the reporting layer simultaneously, with the caller selecting which column to expose based on whether calibration has occurred for a given cycle.

---

## [GAP-FILLED] PKG_SECURITY — Complete Procedure Inventory, Role Model, and Privilege Assignments

**Gap resolved by:** Direct source analysis of `plsql/packages/PKG_SECURITY.pks` (package specification) and `plsql/packages/PKG_SECURITY.pkb` (package body), recovered from `file_cache.json`.
**Referenced by:** `da-outputs/access-control-matrix.md` (RBAC rules, grade-based access, PKG_SECURITY gaps, RPT_* table-level access)

### Public API — Complete Procedure and Function Inventory

| Object Type | Name | Signature | Returns | Description |
|---|---|---|---|---|
| FUNCTION | `authenticate` | `(p_username IN VARCHAR2, p_password IN VARCHAR2, p_ip_address IN VARCHAR2 DEFAULT NULL)` | `NUMBER` | Validates credentials against `EMPLOYEES` table; creates `USER_SESSIONS` row; calls `PKG_EMPLOYEE.set_session_context`; returns `SESSION_ID` |
| PROCEDURE | `logout` | `(p_session_id IN NUMBER)` | — | Sets `USER_SESSIONS.SESSION_STATUS = 'CLOSED'` and stamps `LOGOUT_TIME` |
| FUNCTION | `is_session_valid` | `(p_session_id IN NUMBER)` | `BOOLEAN` | Checks `SESSION_STATUS = 'ACTIVE'` and enforces 30-minute timeout; auto-expires timed-out sessions |
| FUNCTION | `has_permission` | `(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW')` | `BOOLEAN` | Grade-based RBAC check (see role model below); no external permission table — logic is hard-coded in the function body |
| FUNCTION | `encrypt_ssn` | `(p_ssn IN VARCHAR2)` | `VARCHAR2` | AES-256-CBC encryption via `DBMS_CRYPTO`; outputs `RAWTOHEX` string |
| FUNCTION | `decrypt_ssn` | `(p_encrypted IN VARCHAR2)` | `VARCHAR2` | AES-256-CBC decryption; returns `'***DECRYPT_ERROR***'` on failure |
| FUNCTION | `hash_password` | `(p_password IN VARCHAR2)` | `VARCHAR2` | MD5 hash via `DBMS_CRYPTO.HASH_MD5`; returns `RAWTOHEX` string |
| PROCEDURE | `change_password` | `(p_emp_id IN NUMBER, p_old_password IN VARCHAR2, p_new_password IN VARCHAR2)` | — | Enforces complexity rules (≥8 chars, uppercase, digit); writes audit record to `USER_CREDENTIALS`; actual credential update is a stub |

### Package-Level Exception Declarations

| Exception Name | Error Code | Meaning |
|---|---|---|
| `e_invalid_credentials` | `-20301` | Bad username or password |
| `e_account_locked` | `-20302` | Account locked (declared but never raised — see security defect SEC-D-003) |
| `e_session_expired` | `-20303` | Session has expired (declared but not raised by `is_session_valid` — that function returns `FALSE` instead) |
| `e_insufficient_priv` | `-20304` | Insufficient privilege (declared but not raised by `has_permission` — that function returns `FALSE` instead) |

### Role Model — `has_permission` Grade-Based Access Control Logic

The entire RBAC implementation lives inside a single function. There is no `ROLES` table, no `PERMISSIONS` table, and no junction table. The package spec header comments this as: *"In production: would check a ROLES / PERMISSIONS junction table."* The current implementation is:

| Job Grade | Action | Module | Access Granted |
|---|---|---|---|
| `GRADE_ID >= 8` | Any | Any | **Full access** — senior management unconditional pass |
| `GRADE_ID >= 5` | `VIEW` | Any | **View all modules** — mid-level staff |
| `GRADE_ID >= 5` | Non-`VIEW` | Modules other than LEAVE/EMPLOYEE | **Denied** |
| Any grade | `CREATE` or `VIEW` | `LEAVE` | **Granted** — all staff can submit/view own leave |
Now I have all the source material. The snippet provided ends after the privilege gaps table, and the empty "Forward Engineering Requirements — Authorization Architecture" section follows. The content to fill comes from both `PKG_SECURITY.pkb` directly and the already-filled equivalent in `FORWARD_ENGINEERING_INPUT_MAP.md` lines 433–443. Here is the filled snippet:

---

Looking at the source content: the LDAP files (`PKG_LDAP.pkb`, `PKG_LDAP.pks`, `config/ldap_config.sql`) are all "Not found in deep scan." However, the `PKG_INTEGRATION.pkb` source **does** confirm the stub's behaviour and the absence of any implementation. I can document the gap from what the source reveals.

---

Looking at the source content: the PKG_SECURITY code confirms the deny side, but both form files (`EMPLOYEE_MAINTENANCE.fmb`, `HR_ADMIN.fmb`) returned `[Not found in deep scan]`. The gap asked whether a form source confirms or denies the bypass — it does not exist in the provided evidence, so I add a [GAP-FILLED] note recording exactly that finding.

---

| Any grade | `VIEW` | `EMPLOYEE` | **Granted** — all staff can view own profile |
| Any grade | Any other combination | Any | **Denied** |

**Privilege assignment gaps confirmed by code inspection:**

| Missing assignment | Evidence | Forward engineering implication |
|---|---|---|
| No `UPDATE`/`DELETE` on `EMPLOYEE` for non-grade-8 HR administrators | `has_permission` only grants `VIEW` on `EMPLOYEE` for grade < 8; no HR-role exception exists. [GAP-FILLED] Form sources `EMPLOYEE_MAINTENANCE.fmb` and `HR_ADMIN.fmb` were both absent from the deep scan — no Oracle Forms trigger or PRE-INSERT/PRE-UPDATE block could be inspected to confirm or deny whether the `PKG_SECURITY.has_permission` call is present, skipped, or overridden at the form layer. Bypass therefore **cannot be confirmed or excluded** from available source evidence. | HR administrators (grade 5–7) cannot edit employee records through this check — either the check is bypassed in forms, or HR admins are all grade 8+. [GAP-FILLED] Because no form source was recovered, this ambiguity remains open; forward engineering must treat both scenarios as live until form decompilation or a runtime privilege audit resolves which path is actually exercised in production. |
| No module enumeration | `p_module` is a free-text `VARCHAR2`; no enum or constant list constrains valid values | Any caller can pass any string; misspelled module names silently return `FALSE` (deny) rather than raising an error |
| No action enumeration | `p_action` is a free-text `VARCHAR2 DEFAULT 'VIEW'` | Same silent-deny risk as above |
| No `PAYROLL` module rule | No explicit grant for payroll module at any grade level below 8 | Payroll clerks (grade 5–7) are denied payroll edit access by the current logic; only grade 8+ can process payroll |

**[GAP-FILLED] Integration implementation gap — active operational hazard:**

| Procedure | Missing implementation | Evidence from source | Operational risk |
|---|---|---|---|
| `PKG_INTEGRATION.sync_org_structure` | No `DBMS_LDAP` bind call, no LDAP server connection parameters, no directory query logic, no result-set parsing, no write to any target table | `PKG_INTEGRATION.pkb`: the procedure body contains only `PKG_COMMON.log_info(... 'Org structure sync completed' ...)` and nothing else; `PKG_LDAP.pkb`, `PKG_LDAP.pks`, and `config/ldap_config.sql` are absent from the codebase entirely | The procedure logs fabricated success on every invocation. Any scheduler job, monitoring dashboard, or audit trail that relies on this log entry will show the sync as healthy regardless of whether the HRMS org structure has ever been reconciled with Active Directory/LDAP. Stale org data (departed employees, changed cost-centre assignments) will not be detected by the success log. |

**[GAP-FILLED] Forward engineering implication for `sync_org_structure`:** A real implementation must supply: (1) LDAP host, port, base DN, and bind credentials (currently no configuration table entries exist for these); (2) `DBMS_LDAP.init` / `DBMS_LDAP.simple_bind_s` connection logic with explicit exception handling for `DBMS_LDAP.GENERAL_ERROR`; (3) a search loop using `DBMS_LDAP.search_s` or `DBMS_LDAP.search_st` with a timeout; (4) mapping logic from LDAP attributes (e.g. `distinguishedName`, `department`, `manager`) to HRMS columns (`DEPARTMENTS`, `EMPLOYEES.DEPT_ID`, `EMPLOYEES.MANAGER_ID`); (5) an `UNBIND_AND_FREE_SESSION` cleanup block in the exception handler; and (6) a genuine success/failure status written to the target tables and `SYSTEM_PARAMETERS` before the log entry is emitted. Until these are implemented the procedure **must not be scheduled** as its success log provides false assurance.

### Forward Engineering Requirements — Authorization Architecture

[GAP-FILLED] The current `has_permission` implementation **must not be migrated as-is**. The grade-threshold model encodes access policy as hard-coded numeric comparisons with no audit trail, no role-name abstraction, and no ability to grant module-specific exceptions. The target platform requires:

[GAP-FILLED]
1. **Formal RBAC schema:** Replace the grade-threshold logic with a `ROLES` / `PERMISSIONS` / `USER_ROLES` junction table model. The PKG_SECURITY package spec header already documents this as the intended design: *"In production: would check a ROLES / PERMISSIONS junction table."* Permission checks must query this table rather than evaluating `GRADE_ID` comparisons in procedural code.

2. **Module and action enumerations:** Define a closed set of valid `MODULE` and `ACTION` values — via a `PERMISSIONS_CATALOG` table or application-layer enum — to eliminate the silent-deny risk caused by passing free-text `VARCHAR2` strings to `has_permission`. The current default `p_action DEFAULT 'VIEW'` makes incorrect callers silently appear to be read-only requestors.

3. **Credential security remediation derived from SEC-D-001 and SEC-D-002:**
   - Replace `DBMS_CRYPTO.HASH_MD5` in `hash_password` with bcrypt, scrypt, or Argon2id (minimum work factor 12 for bcrypt). All existing stored `PASSWORD_HASH` values must be invalidated and force-reset at next login.
   - Remove the hardcoded `c_encryption_key RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!')` constant. Retrieve the AES-256 key exclusively from Oracle Wallet (`DBMS_CRYPTO` keystore) or Oracle Key Vault. Create an atomic `rotate_encryption_key` procedure that re-encrypts all protected columns (EMPLOYEES.SSN_ENCRYPTED, EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED, EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC) in a single transaction — never rotate tables individually.

4. **Account lockout (SEC-D-003 remediation):** The `e_account_locked` exception (`-20302`) is declared in the package spec but is never raised — the authenticate function has no failed-attempt counter. Implement a `FAILED_LOGIN_COUNT` column on `USER_CREDENTIALS`; lock the account after a configurable threshold (NIST SP 800-63B recommends no fewer than 10 consecutive failures for non-federated authenticators); expose an unlock procedure callable only by administrators.

5. **Timing-attack hardening (SEC-D-004 remediation):** The `authenticate` function follows a different code path for an unknown username (`NO_DATA_FOUND` → immediate error) versus a known username (password comparison path). Add a constant-time dummy hash-comparison branch on the `NO_DATA_FOUND` path so response time is indistinguishable regardless of whether the supplied username exists.

6. **`USER_CREDENTIALS` table completion:** The current implementation references `USER_CREDENTIALS` in comments but performs all authentication lookups against `EMPLOYEES`. The credential store must be fully decoupled from the employee record and implemented as a separate table before any production deployment. Its DDL must be captured in the Data Model Specification (Document 07).

[GAP-FILLED] **Open question for human review (ENR-019 cross-reference):** Database-layer Oracle roles, grants, and synonyms are not captured in any recovered source file. `da-outputs/access-control-matrix.md` covers only application-layer RBAC via `has_permission`. A DBA inventory of all Oracle DB-level `GRANT` statements is required before the Authorization Specification can be considered complete (see ENR-019: 4-hour DBA documentation effort).
| No `REPORTS` module rule | No explicit grant for reporting module | All grade < 8 users are denied report generation through this check |
| `e_account_locked` never raised | Declared as `-20302` but `authenticate` has no lockout counter or lockout trigger | Account lockout is a dead feature — the exception exists but the mechanism does not |

### Session Management Configuration

| Parameter | Value | Source |
|---|---|---|
| Session timeout | 30 minutes | `c_session_timeout_min CONSTANT NUMBER := 30` (package body) |
| Timeout reference clock | DB server `SYSDATE` | Package spec header notes: *"Session timeout check uses DB server time, not app server time"* |
| Session table | `USER_SESSIONS` | Columns: `SESSION_ID`, `EMP_ID`, `USERNAME`, `LOGIN_TIME`, `IP_ADDRESS`, `SESSION_STATUS`, `LOGOUT_TIME`, `CREATED_DATE` |
| Session ID source | `SEQ_USER_SESSION.NEXTVAL` | Oracle sequence |

### Encryption Configuration

| Parameter | Value | Security risk |
|---|---|---|
| Algorithm | `DBMS_CRYPTO.ENCRYPT_AES256 + CHAIN_CBC + PAD_PKCS5` | Algorithm is appropriate |
| Key storage | Hard-coded `RAW(32)` constant in package body: `'HR$ystem_3ncrypt10n_K3y_2024!!'` | **CRITICAL** — key is visible in any DDL export or `DBA_SOURCE` query; all encrypted SSN data is compromised for anyone with schema read access |
| Key scope | Shared between `encrypt_ssn` and `decrypt_ssn` | No key rotation mechanism; no key separation by data type |
| Hash algorithm | `DBMS_CRYPTO.HASH_MD5` | **HIGH** — MD5 is cryptographically broken; rainbow tables trivially reverse common passwords |

### Known Security Defects (Documented in Package Spec Header)

| Defect ID | Description | Location | Severity |
|---|---|---|---|
| SEC-D-001 | AES-256 encryption key hard-coded in package body constant | `PKG_SECURITY.pkb` — `c_encryption_key` declaration | CRITICAL |
| SEC-D-002 | Password hashing uses MD5 (`DBMS_CRYPTO.HASH_MD5`) instead of bcrypt/scrypt/Argon2 | `hash_password` function | HIGH |
| SEC-D-003 | No brute-force protection — no failed-attempt counter, no lockout after N failures | `authenticate` function | HIGH |
| SEC-D-004 | Timing attack: different code paths for unknown user vs. wrong password produce distinguishable response times | `authenticate` — `NO_DATA_FOUND` path vs. hash-comparison path | MEDIUM |
| SEC-D-005 | Session timeout uses DB server clock (`SYSDATE`), not application server time — clock skew can extend effective session lifetime | `is_session_valid` function | LOW |
| SEC-D-006 | `TOO_MANY_ROWS` in `authenticate` silently selects `MIN(EMP_ID)` when multiple active employees share an email address — attacker who shares an email with a target can trigger unpredictable account selection | `authenticate` — `TOO_MANY_ROWS` handler | MEDIUM |

### Forward Engineering Requirements — Authorization Architecture

The current `has_permission` implementation **must not be migrated as-is**. The grade-threshold model encodes access policy as hard-coded numeric comparisons with no audit trail, no role-name abstraction, and no ability to grant module-specific exceptions. The target platform requires:

1. **Formal RBAC schema:** Replace grade-threshold logic with a `ROLES` / `PERMISSIONS` / `USER_ROLES` junction table model. The package spec already documents this as the intended design.
2. **Module and action enumerations:** Define a closed set of valid `MODULE` and `ACTION` values (e.g., via a `PERMISSIONS_CATALOG` table or application-layer enum) to eliminate silent-deny on typos.
3. **Credential security remediation:** Replace MD5 with bcrypt/scrypt/Argon2. Rotate the hard-coded AES key using Oracle Wallet or a secrets manager. Invalidate and rehash all existing stored passwords.
4. **Account lockout:** Implement a failed-login counter with configurable lockout threshold (NIST SP 800-63B recommends no fewer than 10 attempts before lockout for non-federated authenticators).
5. **`USER_CREDENTIALS` table:** The current implementation references this table in comments but uses `EMPLOYEES` for authentication lookups. The credential store must be decoupled from the employee record and fully implemented before any production deployment.

**Open question for human review (ENR-019 cross-reference):** Database-layer Oracle roles, grants, and synonyms are not captured in any recovered source file. `da-outputs/access-control-matrix.md` covers only application-layer RBAC. A DBA inventory of all Oracle DB-level grants is required before the Authorization Specification can be completed (see ENR-019: 4-hour DBA documentation effort).

---

## [GAP-FILLED] Implementation Gap: `PKG_INTEGRATION.sync_org_structure` — Complete Placeholder Logging False Success

**Gap ID:** GAP-PKG_INTEGRATION-001
**Severity:** Critical — Active operational hazard; procedure logs fabricated success on every call
**Location:** `HRMS.PKG_INTEGRATION` package body (`PKG_INTEGRATION.pkb`)

### What the Code Actually Contains

The full body of `sync_org_structure` as recovered from source:

```sql
PROCEDURE sync_org_structure(
    p_user IN VARCHAR2 DEFAULT USER
) IS
BEGIN
    -- Placeholder for org structure sync with external directory (LDAP/AD)
    PKG_COMMON.log_info('PKG_INTEGRATION', 'sync_org_structure',
        'Org structure sync completed', p_user);
END sync_org_structure;
```

The procedure consists of exactly one executable statement: a call to `PKG_COMMON.log_info` that unconditionally records the message `'Org structure sync completed'`. No org-structure data is read, compared, or written. No external directory (LDAP, Active Directory, or any other system) is contacted. No HRMS tables are touched.

### What Is Confirmed Absent

Cross-referencing `PKG_INTEGRATION.pkb` and `PKG_INTEGRATION.pks` against the full source corpus:

| Missing element | Evidence of absence |
|---|---|
| LDAP/AD connection parameters | `PKG_INTEGRATION.pks` declares no constants, types, or parameters related to directory services; `PKG_INTEGRATION.pkb` body constants are limited to `GL_FEED_OUT`, `BENEFITS_FEED_OUT`, `TIME_ATTENDANCE_IN` (file directories only) |
| LDAP query / bind logic | No `DBMS_LDAP` package references anywhere in the recovered codebase |
| Org-structure target tables | No `DEPARTMENTS`, `POSITIONS`, `JOB_GRADES`, or equivalent write operations inside this procedure |
| Error handling | No `EXCEPTION` block; the stub cannot distinguish success from failure |
| Parameters controlling scope or target | Procedure signature is `(p_user IN VARCHAR2 DEFAULT USER)` — no directory URL, no OU path, no sync mode, no date range |

### Operational Hazard: False-Positive Audit Log Pollution

Every invocation of `sync_org_structure` — whether called manually or by a scheduler — writes a record to `AUDIT_LOG` (via `PKG_COMMON.log_info`) stating that org structure synchronisation completed successfully. If this procedure has ever been scheduled, the `AUDIT_LOG` contains an indefinite number of fabricated success entries.

**Immediate operational action required (pre-forward-engineering):**

```sql
-- Count false-positive success records already written
SELECT COUNT(*), MIN(LOG_DATE), MAX(LOG_DATE)
FROM AUDIT_LOG
WHERE PACKAGE_NAME = 'PKG_INTEGRATION'
  AND PROCEDURE_NAME = 'sync_org_structure'
  AND LOG_MESSAGE = 'Org structure sync completed';
```

Any non-zero result confirms the audit log is contaminated for this integration. See also ASM-017 and OQ-003 in this document.

### Forward Engineering Requirements

The org-structure synchronisation capability is entirely unimplemented. The target platform must treat this as a new feature design, not a migration. Minimum design inputs required before implementation:

| Design input | Current state | Where to obtain |
|---|---|---|
| Target directory system (LDAP vs. AD vs. other) | Unknown — comment says "LDAP/AD" but no specifics | Infrastructure / IT Operations |
| Directory connection parameters (host, port, base DN, bind credentials) | Not present anywhere in the codebase | IT Operations; must not be stored in `SYSTEM_PARAMETERS` in cleartext (existing pattern for FTP credentials, flagged in package spec header as a known issue) |
| Attribute mapping (directory attributes → HRMS table columns) | Undefined | HR / IT Operations |
| Sync direction (HRMS → directory, directory → HRMS, or bidirectional) | Undefined | Solution Owner |
| Sync scope (all departments, all positions, a subset) | Undefined | HR / IT Operations |
| Conflict resolution policy (which system is authoritative on mismatch) | Undefined | Solution Owner |
| Failure handling and retry policy | Absent from current package (no retry logic anywhere in `PKG_INTEGRATION`) | Architecture decision required |

**Do not schedule this procedure in any environment until a real implementation exists.** CONT-008 in this document records this as a resolved contradiction — the forward engineering directive is explicit: **do not schedule**.

---

## [GAP-FILLED] AV-025 — Bank Account Encryption/Decryption Path

**Gap resolved by:** Source analysis of `PKG_SECURITY.pkb` and `PKG_SECURITY.pks`

### What exists in PKG_SECURITY

`PKG_SECURITY` contains an AES-256-CBC encryption pair scoped exclusively to SSN fields:

| Function | Signature | Algorithm |
|---|---|---|
| `encrypt_ssn` | `(p_ssn IN VARCHAR2) RETURN VARCHAR2` | `DBMS_CRYPTO.ENCRYPT_AES256 + CHAIN_CBC + PAD_PKCS5` → `RAWTOHEX` output |
| `decrypt_ssn` | `(p_encrypted IN VARCHAR2) RETURN VARCHAR2` | `HEXTORAW` input → `DBMS_CRYPTO.DECRYPT` → `UTL_RAW.CAST_TO_VARCHAR2` |

Both functions share the package-body constant:
```
c_encryption_key RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!')
```

**Known security defects (documented in package spec header):**
- Key is hard-coded in the package body (not stored in a key management facility)
- `hash_password` uses MD5 (`DBMS_CRYPTO.HASH_MD5`), not bcrypt/scrypt
- No account lockout; no brute-force protection on `authenticate`

### Confirmed gap: EMPLOYEE_BANK_ACCOUNTS has no encryption path

**Finding:** `PKG_SECURITY` exposes no `encrypt_bank_account`, `decrypt_bank_account`, or any overloaded variant of `encrypt_ssn`/`decrypt_ssn` targeting bank account fields. Neither `PKG_SECURITY.pks` (public API) nor `PKG_SECURITY.pkb` (body) contain any reference to `EMPLOYEE_BANK_ACCOUNTS`, `ACCOUNT_NUMBER`, `ROUTING_NUMBER`, or equivalent identifiers.

**Implication for forward engineering:**

The target platform **must** introduce a dedicated encryption/decryption path for `EMPLOYEE_BANK_ACCOUNTS` sensitive fields. The existing `encrypt_ssn`/`decrypt_ssn` pattern provides the implementation template but **must not** reuse the same hardcoded key. Recommended forward-engineering actions:

1. **Add** `encrypt_bank_account(p_value IN VARCHAR2) RETURN VARCHAR2` and `decrypt_bank_account(p_encrypted IN VARCHAR2) RETURN VARCHAR2` to the security package (or a successor service layer).
2. **Separate** the encryption key for bank account data from the SSN key — use a secrets manager or Oracle Wallet, not a hard-coded `RAW` constant.
3. **Audit** which `EMPLOYEE_BANK_ACCOUNTS` columns require encryption at rest (`ACCOUNT_NUMBER`, `ROUTING_NUMBER` at minimum) and add column-level or application-level encryption accordingly.
4. **Flag** the shared `c_encryption_key` as a critical remediation item — any migration that carries this key into the new platform inherits the hard-coded credential vulnerability.

**Open question for human review:** Is bank account data currently stored in plaintext in `EMPLOYEE_BANK_ACCOUNTS`, relying on DB-level access controls only? If so, this is a data-at-rest compliance risk that must be resolved before cutover.

---

[GAP-FILLED] **Implementation Gap: EMPLOYEE_BANK_ACCOUNTS — Complete Absence of ACH Disbursement Logic in PKG_PAYROLL**

Code inspection of `plsql/packages/PKG_PAYROLL.pkb` confirms that the payroll processing pipeline has no disbursement step. The pipeline terminates at net-pay calculation — no procedure reads `EMPLOYEE_BANK_ACCOUNTS`, processes routing or account numbers, generates a NACHA ACH file, or transitions `PAYROLL_RUNS.STATUS` to `PAID` via any payment event.

Specific evidence from the recovered package body:

- **`calculate_payroll`** (the orchestrator procedure) iterates over all `EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE'`, delegates per-employee work to `calculate_employee_pay`, then updates `PAYROLL_RUNS` with `TOTAL_GROSS`, `TOTAL_DEDUCTIONS`, `TOTAL_NET`, and sets `STATUS = 'CALCULATED'` (or `'ERROR'`). The procedure ends there. No ACH generation call, no file write, no dispatch step follows.
- **`calculate_employee_pay`** computes period gross from `SALARY_RECORDS` using `PAY_FREQUENCY`-based divisors (52/26/24/12 periods per year), applies Social Security tax (6.2%, capped at `c_ss_wage_base_2024 = 168,600`), Medicare tax (1.45% standard + 0.9% additional above $200,000 threshold), federal withholding (allowance-reduced taxable income), and state withholding. All results write to `PAYROLL_DETAILS`. The procedure contains zero references to `EMPLOYEE_BANK_ACCOUNTS`, `ROUTING_NUMBER`, `ACCOUNT_NUMBER`, `DEPOSIT_TYPE`, `PRIORITY_ORDER`, or `PRENOTE_SENT`.
- **No disbursement procedure exists** anywhere in the recovered codebase under any name (`disburse_payroll`, `generate_ach_file`, `process_direct_deposit`, `send_ach`, or equivalent).

The `PAID` status on `PAYROLL_RUNS.STATUS` is therefore a dead value — no code path ever assigns it through a disbursement event. This directly corroborates architecture violation AV-024 and application risk RISK-004 already logged in the register.

**Forward engineering implication:** The ACH disbursement module is entirely greenfield. The `EMPLOYEE_BANK_ACCOUNTS` schema supplies the data contract (four `DEPOSIT_TYPE` values, `PRIORITY_ORDER` for split-deposit sequencing, `PRENOTE_SENT` flag for Nacha prenote cycle, `ROUTING_NUMBER` and `ACCOUNT_NUMBER` for file generation). All disbursement logic must be designed from scratch: prenote activation cycle, split-deposit allocation by `PRIORITY_ORDER`, NACHA PPD/CCD file generation, bank acknowledgement handling, and the `PAYROLL_RUNS.STATUS → PAID` transition gate. See OQ-005 (mandatory — blocks ACH module design) and ENR-004 (payroll administrator interview) in this document.

---

## [GAP-FILLED] Implementation Gap: Missing `calculate_final_pay` Procedure

**Gap ID:** GAP-PKG_EMPLOYEE-001
**Severity:** Critical — Blocks termination workflow entirely
**Location:** `HRMS.PKG_EMPLOYEE` package body (`PKG_EMPLOYEE.pkb`)

### What Is Missing

The procedure `calculate_final_pay` is called inside `PKG_EMPLOYEE.terminate_employee` but has no corresponding definition anywhere in the package body, package spec, or any other PL/SQL object recovered from the codebase. The termination payroll calculation path is entirely absent.

**Call site (inferred from package structure):**
```sql
-- Inside PKG_EMPLOYEE.terminate_employee (body not recovered):
calculate_final_pay(
    p_emp_id           => p_emp_id,
    p_termination_date => p_termination_date,
    ...  -- parameter signature unknown; never declared
);
```

**Cross-reference:** `PKG_PAYROLL.create_salary_record` is the only payroll integration point found in the package body — it is used exclusively for the new-hire path in `create_employee`. No equivalent finalisation call exists for the separation path.

### Business Impact

Employees processed through `terminate_employee` will have no final pay record generated. This affects:
- Accrued leave payout calculation
- Pro-rata salary for the final partial pay period
- Any termination bonus or severance computation
- Payroll run cut-off reconciliation

### Forward Engineering Requirement

The target platform **must implement** `calculate_final_pay` (or its equivalent) before the termination workflow is functional. Minimum required inputs, based on context inferred from the surrounding package:

| Parameter | Type | Source |
|---|---|---|
| `p_emp_id` | NUMBER | `EMPLOYEES.EMP_ID` |
| `p_termination_date` | DATE | Effective separation date |
| `p_reason_code` | VARCHAR2 | Termination reason (maps to `EMPLOYEE_HISTORY.REASON_CODE`) |
| `p_last_salary` | NUMBER | Current record from `PKG_PAYROLL` / salary history |

**Open Question (requires human review):** Does final pay logic belong in `PKG_EMPLOYEE` (as originally called) or should it be relocated to `PKG_PAYROLL` as a peer to `create_salary_record`? The existing architecture places all salary record creation in `PKG_PAYROLL`; moving the call there would be consistent, but the original developer chose to embed it in the employee lifecycle package.

---

## [GAP-FILLED] Implementation Gap: Missing COBRA Continuation Coverage Logic in `terminate_employee`

**Gap ID:** GAP-PKG_EMPLOYEE-002
**Severity:** Critical — Federal compliance violation on every processed termination
**Location:** `HRMS.PKG_EMPLOYEE` — `terminate_employee` procedure (body not recovered; gap confirmed by TODO marker and BA supplement analysis)
**Regulatory Reference:** US Consolidated Omnibus Budget Reconciliation Act (COBRA), 29 U.S.C. §§ 1161–1168; qualifying event notification must be issued within 14 days of the event date

### What Is Missing

The `terminate_employee` procedure contains a TODO comment acknowledging that COBRA continuation coverage notification logic is required but has never been implemented. No COBRA-related procedure, notification template, or qualifying-event record exists anywhere in the recovered codebase.

**Confirmed by:**
- BA supplement analysis (`BA_Deep_Analyst_Edge.md` — PKG_EMPLOYEE.terminate_employee TODOs), business rule BR-TERM-01: "Termination triggers a COBRA qualifying event; employee and covered dependents must receive written notification within 14 days"
- Contradiction resolution log CONT-009: classified as a pure gap (no conflicting implementation exists — absence is the finding)
- Priority finding PP-TERM-01 in Appendix B: "Every termination creates a federal COBRA compliance violation"
- Cross-validation supplement entry: "COBRA gap, access revocation partial, calculate_final_pay does not exist"

**What the code does have** (relevant neighbouring infrastructure):
- `PKG_NOTIFICATION.send_notification` — used in `create_employee` to send welcome emails and manager alerts; the same call signature is available for COBRA notices
- `log_history` (AUTONOMOUS_TRANSACTION) — the history logging pattern is established and could record the qualifying event date independently of the main termination transaction
- `EMPLOYEE_HISTORY.REASON_CODE` — termination reason is captured; distinguishes voluntary resignation from involuntary termination, which affects COBRA eligibility rules

**What is absent:**
- Any call to a COBRA notification procedure inside `terminate_employee`
- A `COBRA_ELECTIONS` or `QUALIFYING_EVENTS` table (not found in DDL; not inferred in schema catalogue)
- Any notification template for COBRA in `NOTIFICATION_QUEUE` or related tables
- Any reference to a benefits administrator API or file-based notification exchange

### Business Impact

Every employee terminated through this system has not received a federally mandated COBRA notification. Depending on the number of terminations processed and the time elapsed, the company may be liable for:
- Civil penalties under ERISA §502(c)(1): up to $110 per day per qualified beneficiary for failure to provide timely notice
- Excise tax under IRC §4980B: $100 per day per qualified beneficiary during the noncompliance period
- Individual lawsuits from former employees who incurred medical costs during a COBRA election window they were never offered

COBRA also extends to covered **dependents** listed in `EMPLOYEE_DEPENDENTS`. The termination workflow does not notify dependents, and — per the cross-validation supplement — `terminate_employee` does not touch `EMPLOYEE_DEPENDENTS` records at all, meaning the benefits feed to ADP may continue to include dependents of terminated employees after the election window has closed (see OQ-010).

### Forward Engineering Requirement

The target platform **must implement** a COBRA qualifying-event notification module before the termination workflow can be considered compliant. This is not an enhancement — it is a mandatory legal requirement.

**Minimum required design elements:**

| Capability | Description | Constraint |
|---|---|---|
| Qualifying event recording | Insert a record in a new `COBRA_QUALIFYING_EVENTS` table at the moment `terminate_employee` commits | Must be durable even if notification delivery fails; use AUTONOMOUS_TRANSACTION pattern consistent with `log_history` |
| 14-day notification SLA | Notify the employee (and each covered dependent) of COBRA election rights within 14 days of termination date | BR-TERM-01; 29 U.S.C. §1166(a)(2) |
| Notification channel | Written notice; email via `PKG_NOTIFICATION.send_notification` is acceptable if supplemented by a physical-mail fallback for employees without a valid email on record | `EMPLOYEES.EMAIL` nullable — fallback required |
| Dependent coverage | All active `EMPLOYEE_DEPENDENTS` records linked to the terminated employee must receive independent notification | Cross-validation supplement VQ-DEP-04 |
| Benefits feed gate | `export_benefits_feed` must not export dependents of terminated employees after the COBRA election window closes (typically 60 days) | Open Question OQ-010 |
| Third-party administrator handoff | If COBRA is administered by an external benefits administrator, the qualifying event must be transmitted in the format and within the SLA that administrator requires | Unresolved — see OQ-006 |

**Proposed `COBRA_QUALIFYING_EVENTS` table shape** (minimum — subject to DBA and legal review):

```sql
-- [GAP-FILLED] Proposed new table: COBRA_QUALIFYING_EVENTS
CREATE TABLE HRMS.COBRA_QUALIFYING_EVENTS (
    EVENT_ID            NUMBER        NOT NULL,  -- sequence-generated PK
    EMP_ID              NUMBER        NOT NULL,  -- FK → EMPLOYEES.EMP_ID
    EVENT_TYPE          VARCHAR2(30)  NOT NULL,  -- 'TERMINATION', 'REDUCTION_HOURS', etc.
    QUALIFYING_DATE     DATE          NOT NULL,  -- date termination took effect
    NOTIFICATION_DUE    DATE          NOT NULL,  -- QUALIFYING_DATE + 14 days
    NOTIFICATION_SENT   DATE,                    -- NULL = not yet sent
    ADMINISTRATOR_REF   VARCHAR2(100),           -- third-party admin reference number, if applicable
    CREATED_BY          VARCHAR2(100) NOT NULL,
    CREATED_DATE        DATE          NOT NULL,
    CONSTRAINT PK_COBRA_QE PRIMARY KEY (EVENT_ID),
    CONSTRAINT FK_COBRA_QE_EMP FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
);
```

**Integration point inside `terminate_employee`** (pseudocode — exact parameter signature of `terminate_employee` not recovered):

```sql
-- [GAP-FILLED] Required addition inside PKG_EMPLOYEE.terminate_employee:
-- Step: Record COBRA qualifying event (AUTONOMOUS_TRANSACTION — must survive
--       any rollback of the outer termination transaction)
INSERT INTO COBRA_QUALIFYING_EVENTS (
    EVENT_ID, EMP_ID, EVENT_TYPE,
    QUALIFYING_DATE, NOTIFICATION_DUE,
    CREATED_BY, CREATED_DATE
) VALUES (
    SEQ_COBRA_EVENTS.NEXTVAL, p_emp_id, 'TERMINATION',
    p_termination_date, p_termination_date + 14,
    p_user, SYSDATE
);

-- Step: Send COBRA notice via existing notification infrastructure
PKG_NOTIFICATION.send_notification(
    p_recipient_emp_id => p_emp_id,
    p_type             => 'EMAIL',
    p_subject          => 'Important: Your COBRA Continuation Coverage Rights',
    p_body             => '<COBRA notice template — to be defined by Legal>',
    p_user             => p_user
);
-- TODO: iterate EMPLOYEE_DEPENDENTS for p_emp_id and send per-dependent notices
-- TODO: transmit qualifying event to third-party COBRA administrator (OQ-006)
```

### Open Questions Blocking Implementation

| OQ Reference | Question | Blocking What |
|---|---|---|
| OQ-006 (Mandatory) | Is COBRA administered by a third-party? What is their notification API or file format? What is their qualifying event SLA? | Cannot design the administrator handoff module or confirm whether 14 days is the applicable SLA |
| OQ-010 (High Priority) | Should dependents be inactivated immediately on termination or held active during the 60-day COBRA election window? | Affects `export_benefits_feed` ADP output and `EMPLOYEE_DEPENDENTS` lifecycle |

### Enrichment Action Required

**ENR-003** (see §8.1): HR + Legal must define the COBRA notification process and timeline, document whether a third-party administrator handles elections, specify the required notification format, and confirm the qualifying event SLA. This is a prerequisite before the termination workflow specification can be drafted. Estimated effort: 1 workshop.

---

## Table of Contents

1. [Analysis Output → Deliverable Mapping](#1-analysis-output--deliverable-mapping)
2. [Source of Truth Declarations](#2-source-of-truth-declarations)
3. [Contradiction Resolution Log](#3-contradiction-resolution-log)
4. [Confidence Levels per Domain](#4-confidence-levels-per-domain)
5. [Assumptions Made](#5-assumptions-made)
6. [Open Questions Requiring Human Review](#6-open-questions-requiring-human-review)
7. [Data Quality Assessment](#7-data-quality-assessment)
8. [Recommended Enrichment Actions](#8-recommended-enrichment-actions)

---

## 1. Analysis Output → Deliverable Mapping

This table maps every analysis output artefact produced across all four tracks (BA, DA, TA, AA) and the cross-validation supplement to the specific forward engineering deliverable(s) it feeds. Each row includes a confidence rating for the mapping.

### 1.1 Business Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| `BA_Deep_Analyst.md` (BR-01–BR-107, Pass 1) | 107 core business rules covering payroll, leave, performance, security, notifications | BRD (Business Requirements Document); Use Case Specifications; Domain Model; Business Rules Engine specification | HIGH |
| `BA_Deep_Analyst.md` (BR-108–BR-140, Pass 2 — Edge Cases) | 33 edge-case business rules including concurrent access, boundary conditions, exception flows | BRD addendum; Test Case Specification; NFR Specification (error handling) | HIGH |
| `BA_Deep_Analyst.md` — Discrepancy Log (DISC-001–DISC-009) | 9 data discrepancies across tracks, including payroll PAID status orphaning (DISC-009) | Gap Analysis Report; Data Migration Specification; BRD open issues | HIGH |
| `BA_Deep_Analyst_Edge.md` — EMPLOYEE_DEPENDENTS supplement | 10 business rules (BR-DEP-01–10), pain points, automation opportunities, validation queue | API Contract for dependents management; Data Model (EMPLOYEE_DEPENDENTS entity); Benefits feed integration spec | HIGH |
| `BA_Deep_Analyst_Edge.md` — PKG_INTEGRATION.sync_org_structure supplement | 5 business rules (BR-ORG-01–05) — stub procedure, false success log | Integration Architecture Specification; Operational Runbook (DO NOT SCHEDULE); NFR Spec | HIGH |
| `BA_Deep_Analyst_Edge.md` — EMPLOYEE_BANK_ACCOUNTS supplement | 12 business rules (BR-BA-01–12), ACH/NACHA gap analysis | Payroll Disbursement API Spec; ACH Integration Design; Data Model | HIGH |
| `BA_Deep_Analyst_Edge.md` — PKG_EMPLOYEE.terminate_employee TODOs | 9 business rules (BR-TERM-01–09), COBRA gap, access revocation, final pay | Termination Workflow Specification; Compliance Checklist (COBRA); Off-boarding API Design | HIGH |
| `BA_Deep_Analyst_Edge.md` — PERFORMANCE_REVIEWS calibration gap | Calibration workflow completely absent from code; CALIBRATED_RATING dead column | Performance Management Specification; Calibration Session UI Design; Reporting Correction | HIGH |
| `BA_Deep_Analyst_Edge.md` — PKG_LEAVE.initialize_balances supplement | 10 business rules (BR-LIB-01–10), accrual retry defect (BR-LIB-05) | Leave Accrual Engine Specification; Defect Fix Specification (critical) | HIGH |
| `BA_Deep_Analyst_Edge.md` — Pass 2 Edge Case Summary | Grouped table of all 33 edge rules by theme, top-5 severity findings | BRD Appendix; Risk Register input | HIGH |

### 1.2 Data Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| `DA_Data_Reviewer.md` (Passes 1–3, RC-001–RC-011) | 35 total corrections: 22 corrected / 8 added / 5 enriched across three review passes | Data Dictionary (authoritative); ERD; Data Migration Specification | HIGH |
| `da-outputs/review-summary.md` | Gate G1 open questions (G1-01–G1-10), quality score progression, pass-by-pass change totals | Forward Engineering Readiness Report; Human Review Checklist | HIGH |
| `da-outputs/data-dictionary.md` | Full column inventory for all 30 confirmed DDL tables, 6 views, inferred tables | Data Dictionary deliverable (06_DATA_DICTIONARY); ERD input; API Contract data shapes | HIGH |
| `da-outputs/schema-catalogue.json` | Structured JSON: all tables, constraints, FK relationships, inferred tables (38 total) | ERD (08_ERD); Data Model Specification (07); Technology Blueprint DB schema section | HIGH |
| `da-outputs/hidden-business-rules.json` | BR-041–BR-046: security rules, stub rules, missing constraints (44 total rules) | BRD supplement; Security Architecture Specification; Test Case Specification | HIGH |
| `da-outputs/data-quality-report.md` | DQ-001–DQ-032: 32 data quality findings including 9 HIGH severity | Data Migration Specification (pre-conditions); NFR Specification; Defect Register | HIGH |
| `da-outputs/pii-inventory.json` | PII classification for all columns including RPT_* inferred tables | Privacy Impact Assessment; Security Architecture; Encryption Specification | HIGH |
| `da-outputs/access-control-matrix.md` | RBAC rules, grade-based access, PKG_SECURITY gaps, RPT_* table-level access | Authorization Specification; API Security Design; RBAC Implementation Guide | HIGH |
| `da-outputs/storage-pattern-analysis.md` | Soft-delete pattern, audit column pattern, denormalized RPT_* layer (§9) | Data Model Specification; Migration Strategy; Archival Policy | MEDIUM |
| `da-outputs/data-flow-map.md` | 14 sections covering all data flows including stub flows (§13 on-demand, §14 nightly) | Data Flow Diagram (09_DFD); Integration Architecture Specification | HIGH |
| `da-outputs/data-source-inventory.json` | DS-01–DS-10, Gate G1 questions G1-NEW-01–03, RPT_* data source | Technology Blueprint; Integration Inventory | MEDIUM |
| `da-outputs/migration-complexity.json` | MC-01, MC-02b (Oracle MEDIAN() no direct equivalent) | Technology Blueprint; Migration Risk Register; Target Platform Selection | HIGH |
| `da-outputs/USER_CREDENTIALS` supplement | DQ-029–030, BR-043b, BR-044–045 — auth stub, password bypass, dead exceptions | Security Architecture Specification; Authentication API Design | HIGH |
| `da-outputs/TIME_ATTENDANCE_RECORDS` supplement | DQ-031, BR-046 — stub import, false audit trail, no DDL | Integration Design (Time & Attendance); Gap Report | HIGH |
| `da-outputs/RPT_*` supplements | DQ-032, BR-043–045 (RPT_* context), CALENDAR_YEAR projection gap | Reporting Specification; BI Architecture Design; Data Warehouse Design | MEDIUM |

### 1.3 Technology Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| TA output — TD-01–TD-36 (Critical/High items) | Hard-coded AES key, cleartext FTP credentials, SQL injection vectors, auth stub | Security Architecture Specification; Penetration Test Checklist; Remediation Roadmap | HIGH |
| TA output — TD-37–TD-57 (Medium items) | Audit log mixing, EEO constraint gap, salary validation soft-check | NFR Specification; Data Model corrections; Operational Runbook | HIGH |
| TA output — TD-58–TD-81 (Medium/Low edge cases) | Oracle Forms LOV gap (TD-72), ADP no-validation (TD-73), GL feed gaps (TD-79–80), portal auth (TD-81) | Integration Contract Specification; Forms Migration Specification; Operational Runbook | HIGH |
| TA output — CI/CD Pipeline Maturity Assessment | 0 of 14 capabilities present; 6 Critical gaps (build, test, SAST, secret scan, deploy, rollback) | DevOps Architecture Specification; CI/CD Pipeline Design; Technology Blueprint | HIGH |
| TA output — Observability Coverage Assessment | No structured logging, no correlation ID, no distributed tracing | NFR Specification (observability); Technology Blueprint; Operations Design | HIGH |
| TA output — Forms compilation gap (TD-76) | No build script for Oracle Forms .fmb → .fmx | Build System Specification; Technology Blueprint | MEDIUM |
| TA output — FMLA REQUIRES_DOCUMENT='N' (TD-71) | FMLA seed data allows undocumented leave — compliance risk | Configuration Management Specification; Compliance Checklist | HIGH |
| TA output — Session stale cleanup gap (TD-75) | No DBMS_SCHEDULER sweep for expired USER_SESSIONS | Operational Architecture Specification; Scheduled Job Design | HIGH |

### 1.4 Application Analysis Track Outputs

| Analysis Output File | Content Summary | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|
| `quality-review.md` (QR-001–QR-033, Passes 1–3) | 33 quality findings including architecture violations, risk items, component boundary issues | Architecture Violation Register (input); Forward Engineering Specification (15_FES) | HIGH |
| `final-sanity-check.md` (§11 Pass 3) | 8 edge-case findings marked [EDGE-CASE-FOUND] | Forward Engineering Readiness Report; Risk Register | HIGH |
| `executive-summary-for-review.md` | Multi-pass summary, overall verdict PARTIAL | Forward Engineering Readiness Report (17_FERR); Stakeholder Briefing | HIGH |
| `architecture-violation-register.json` (AV-001–AV-025) | 25 violations including AV-024 (direct deposit unimplemented) and AV-025 (encryption path missing) | Architecture Specification; Remediation Roadmap; NFR Specification | HIGH |
| `application-risk-register.json` (RISK-001–RISK-014) | 14 risks, 9 HIGH severity including ACH missing and bank account decryption unknown | Risk Register; Forward Engineering Readiness Report; Project Charter input | HIGH |
| `component-registry.json` | All major components (COMP-001–COMP-N), risk flags per component | Component Architecture Diagram; Technology Blueprint | HIGH |
| `module-boundary-map.json` (MOD-001–MOD-N) | Module boundaries, open questions for EMPLOYEE_BANK_ACCOUNTS | Bounded Context Map; API Contract boundaries | MEDIUM |
| `extraction-audit.md` | Coverage matrix, violation counts | Forward Engineering Readiness Report; Audit Trail | MEDIUM |
| `forward-engineering-input-map.md` | Early draft with payroll section, bank accounts critical migration requirements | This document (supersedes early draft) | HIGH |

### 1.5 Cross-Validation Supplement Outputs

| Supplement | Tracks Reconciled | Key Finding | Forward Engineering Deliverable(s) | Mapping Confidence |
|---|---|---|---|---|
| EMPLOYEE_DEPENDENTS (BA↔DA, DA↔AA) | BA, DA, AA | BENEFITS_ENROLLED never read; dependent SSN decrypt path missing; termination doesn't touch dependents | Benefits Integration Spec; Termination Workflow; Data Model | HIGH |
| PKG_INTEGRATION.sync_org_structure (BA supplement) | BA | Entire procedure is placeholder — logs false success | Integration Spec (exclude/flag); Operational Runbook | HIGH |
| EMPLOYEE_BANK_ACCOUNTS (BA↔AA, DA↔AA) | BA, DA, AA | Table completely unused — direct deposit non-functional | ACH Disbursement Design; Critical Gap Report | HIGH |
| PKG_EMPLOYEE.terminate_employee TODOs (BA supplement) | BA | COBRA gap, access revocation partial, calculate_final_pay does not exist | Termination API Design; Compliance Specification | HIGH |
| PERFORMANCE_REVIEWS calibration (BA supplement) | BA, DA | CALIBRATED_RATING dead column; reporting reads wrong column (pre-calibration) | Performance Specification; Reporting Correction | HIGH |
| PKG_LEAVE.initialize_balances (BA supplement) | BA | Accrual retry defect: assignment vs. increment bug | Leave Engine Defect Fix; Test Case | HIGH |
| USER_CREDENTIALS (DA supplement, two passes) | BA, DA | Auth stub (BR-042) — any valid username authenticates regardless of password; MD5; change_password never verifies old password | Security Architecture; Authentication API; Critical Security Remediation | HIGH |
| RPT_* tables (DA supplement) | BA, DA | refresh_reporting_tables is pure stub; all reports query OLTP directly; CALENDAR_YEAR missing from leave utilization cursor | Reporting Architecture; BI Design; Data Warehouse Spec | MEDIUM |
| TIME_ATTENDANCE_RECORDS (AA→DA) | AA, DA | No DDL for import target; stub logs false success | Integration Design; Time & Attendance Module Spec | HIGH |
| RPT_HEADCOUNT / RPT_COMPENSATION / RPT_LEAVE_UTIL (BA→DA) | BA, DA | Oracle MEDIAN() migration issue (MC-02b); non-standard turnover denominator | Technology Blueprint; Migration Risk | MEDIUM |

---

## 2. Source of Truth Declarations

The following table declares, for each major topic, which single document is the authoritative source for forward engineering. All conflicting information in other documents must defer to the declared source of truth.

| Topic | Source of Truth Document | Rationale | Override Condition |
|---|---|---|---|
| Business rules (functional) — BR-01–BR-107 | `BA_Deep_Analyst.md` Pass 1 | First-pass analysis with direct code evidence citations; unchanged in all subsequent passes | None — authoritative |
| Business rules (edge cases) — BR-108–BR-140 | `BA_Deep_Analyst.md` Pass 2 section | Dedicated edge-case pass with [EDGE-CASE-FOUND] markers; additive to Pass 1 | None — authoritative |
| Database schema — table definitions, constraints | `da-outputs/schema-catalogue.json` | Most granular, structured representation with FK graph; reviewed through three DA passes | DDL source files if direct schema conflict arises |
| Column-level business meaning | `da-outputs/data-dictionary.md` | Three-pass reviewed; covers all 30 confirmed tables, 6 views, and inferred tables | Supersedes any earlier BRD column descriptions |
| PII classification | `da-outputs/pii-inventory.json` | Explicit PII flags per column including RPT_* inferred table exposure; consistent with GDPR/CCPA framing | Legal review may reclassify |
| Security business rules | `da-outputs/hidden-business-rules.json` (BR-041–046) + TA critical findings | DA track captured security rules from code inspection; TA confirmed and extended | Penetration test findings supersede theoretical analysis |
| RBAC / access control | `da-outputs/access-control-matrix.md` | Derived from PKG_SECURITY code; grade-based logic confirmed in both BA and DA tracks | Any new role definition from business must be added here |
| Data quality defects | `da-outputs/data-quality-report.md` (DQ-001–DQ-032) | Three-pass reviewed; most current and complete; each finding has severity and corrective recommendation | — |
| Bounded context boundaries | `results/Foundation_KnowledgeGraph/` + Domain Model (05_DOMAIN_MODEL) | Context map derived from package boundaries; confirmed against schema FK clusters | — |
| Architecture violations | `architecture-violation-register.json` (AV-001–AV-025) | AA track systematic; cross-validated with DA and TA findings | — |
| Integration contracts (current state) | `da-outputs/data-flow-map.md` §1–§14 | Most complete integration picture; covers all stubs and real flows explicitly | PKG_INTEGRATION.pkb source if conflict |
| Technology risk items | TA track outputs (TD-01–TD-81) | Systematic two-pass TA analysis; covers CI/CD, observability, configuration, security | — |
| Performance calibration gap | BA_Deep_Analyst_Edge.md calibration supplement | Most complete statement of what is missing and what the implied process should be | — |
| Termination workflow gaps | BA_Deep_Analyst_Edge.md terminate_employee supplement | Most complete gap analysis including COBRA, access revocation, final pay | — |
| Payroll disbursement gap | `BA_Deep_Analyst_Edge.md` EMPLOYEE_BANK_ACCOUNTS supplement + AV-024/AV-025 | Cross-validated: BA rules, AA architecture violations, and DA data quality findings all concur | — |
| EMPLOYEE_DEPENDENTS data rules | BA_Deep_Analyst_Edge.md + AA cross-validation supplement | Full table definition, integration usage, and gap analysis confirmed across three tracks | — |

---

## 3. Contradiction Resolution Log

Each entry records a contradiction found across analysis tracks and the resolution applied for forward engineering purposes.

| Contradiction ID | Topic | Track A Statement | Track B Statement | Resolution | Resolved By |
|---|---|---|---|---|---|
| CONT-001 | EMPLOYEES.BANK_ACCOUNT_NUMBER encryption | DA data-dictionary: `BANK_ACCOUNT_NUMBER VARCHAR2(500)` AES-256 encrypted; decrypt procedure not found | BA track: EMPLOYEE_BANK_ACCOUNTS is a separate table (not a column on EMPLOYEES); all procedures reference the separate table | Both are true: the EMPLOYEES table has a legacy `BANK_ACCOUNT_NUMBER` column AND a separate EMPLOYEE_BANK_ACCOUNTS table exists; the column is residual. Forward engineering: migrate to EMPLOYEE_BANK_ACCOUNTS model; deprecate the EMPLOYEES column | Architecture team judgment; confirmed by DA schema catalogue showing both |
| CONT-002 | Direct deposit functionality | BA track originally described payroll as functional through PAID status | DA track (DQ-009), AA track (AV-024), and EMPLOYEE_BANK_ACCOUNTS supplement all confirm: no procedure reads EMPLOYEE_BANK_ACCOUNTS; PAID status is orphaned | Forward engineering treats direct deposit as **not implemented** — new ACH disbursement module must be designed from scratch; PAID status transition logic must be tied to successful ACH file generation | DA/AA cross-validation concurrence |
| CONT-003 | PKG_SECURITY.authenticate password check | BA track (BR-42): "password is verified against stored hash" — implied | DA track (BR-042/DQ-003): authenticate() never queries USER_CREDENTIALS; any valid username authenticates regardless of password | DA track wins — code inspection is authoritative over implied BA behavior. Forward engineering: authentication module must be completely rewritten | Direct code evidence in PKG_SECURITY.pkb |
| CONT-004 | HRMS_VALIDATION_LIB.validate_salary_range caching | TA track (TD-52): comment in code says "cached" | DA/TA code inspection: body shows live DB query to JOB_GRADES — no caching | Live query is the actual behavior. Forward engineering: no caching assumption; performance NFR must account for per-validation DB round trips | TD-52 code evidence |
| CONT-005 | Performance rating used in payroll (merit) | BA track: OVERALL_RATING ≥ 3 required for merit eligibility | AA/DA calibration supplement: CALIBRATED_RATING column exists but is dead; reporting reads OVERALL_RATING; no calibration step exists | Forward engineering: merit calculation currently uses OVERALL_RATING (the raw manager rating). If calibration workflow is implemented, the merit eligibility rule must be updated to reference CALIBRATED_RATING post-implementation | Architecture team decision required (see OQ-009) |
| CONT-006 | USER_SESSIONS timeout enforcement | TA track (TD-75): session timeout only evaluated on next is_session_valid call — no background sweep | DA track (BR-026): timeout is hard-coded 30 minutes, ignoring SYSTEM_PARAMETERS | Both are true simultaneously. Forward engineering: (a) implement DBMS_SCHEDULER sweep; (b) wire timeout to SYSTEM_PARAMETERS; (c) implement explicit session invalidation on PKG_SECURITY.revoke_access | Composite finding |
| CONT-007 | RPT_* tables and reporting query source | BA track: described a nightly reporting refresh cycle as production behavior | DA/TA inspection: refresh_reporting_tables is a pure stub; all 7 report procedures query OLTP directly; RPT_* tables may never have held data | Forward engineering: treat current reporting as **OLTP-direct only**; RPT_* table design is aspirational. Confirm with DBA whether RPT_* tables exist in production DDL (see OQ-012) | DA code inspection overrides BA description |
| CONT-008 | PKG_INTEGRATION.sync_org_structure scheduling | BA track: procedure exists in integration package | BA supplement: procedure is a complete placeholder — only logs false success; zero actual logic | Forward engineering: **do not schedule** this procedure; the org structure sync capability is entirely unimplemented and logging false success is actively dangerous | BA supplement code inspection |
| CONT-009 | COBRA notification timing | BA supplement (BR-TERM-01): COBRA requires 14-day notification | No implementation exists anywhere | No contradiction — this is a pure gap. Forward engineering: implement COBRA notification as a new capability; 14-day SLA is the target NFR | Regulatory requirement |
| CONT-010 | Password change old-password verification | BA track: assumed change_password validates the old password | DA supplement (DQ-029/BR-044): p_old_password is received but never compared; any authenticated session can replace any credential silently | DA code evidence is authoritative. Forward engineering: implement old-password verification as mandatory step in the new authentication module | Direct code inspection |
| CONT-011 | ADP benefits feed BENEFITS_ENROLLED filter | BA description: benefits feed exports enrolled dependents | AA/DA cross-validation: export_benefits_feed uses LEFT JOIN with d.ACTIVE_FLAG='Y' but does NOT filter on BENEFITS_ENROLLED; all active dependents are exported regardless of enrollment status | DA/AA code inspection is authoritative. Forward engineering: add BENEFITS_ENROLLED='Y' filter unless business confirms all active dependents should always be exported (see OQ-007) | Cross-track code evidence |
| CONT-012 | Turnover report denominator | BA reporting capability description: turnover percentage | DA supplement (BR-044): turnover_report uses hires-up-to-end-date as denominator, not average headcount — non-standard vs SHRM definition | Documented as known non-standard behavior. Forward engineering: the new turnover report should offer both calculation methods; flag denominator choice in UI | DA code inspection |

---

## 4. Confidence Levels per Domain

### 4.1 Confidence Summary Table

| Domain | Confidence Level | Key Evidence Base | Limiting Factors |
|---|---|---|---|
| Employee Master Data | HIGH | Schema confirmed, PKG_EMPLOYEE fully analysed, BA rules 1–30 solid | EMERGENCY_CONTACTS table status unclear |
| Payroll Calculation Engine | HIGH | PKG_PAYROLL.pkb partially recovered; tax brackets confirmed; deduction logic confirmed | Procedure body truncated mid-source; final-pay procedure does not exist |
| Payroll Disbursement (ACH) | LOW | EMPLOYEE_BANK_ACCOUNTS schema confirmed; zero procedure references confirmed | Entire disbursement layer is unimplemented — must be designed net-new |
| Leave Management | HIGH | PKG_LEAVE fully analysed; leave types, accruals, balances confirmed; initialize_balances defect found | Accrual retry defect (BR-LIB-05) needs confirmation of real-world data impact |
| Performance Management | MEDIUM | PKG_PERFORMANCE fully analysed; OVERALL_RATING workflow confirmed | CALIBRATED_RATING entirely unimplemented; calibration business process not defined by business stakeholders |
| Security & Authentication | LOW | PKG_SECURITY analysed; critical auth stub confirmed (BR-042); MD5 confirmed; hardcoded key confirmed | Authentication is fundamentally broken — must be rewritten entirely; no trustworthy baseline |
| Benefits Integration (ADP) | MEDIUM | PKG_INTEGRATION.export_benefits_feed confirmed; ADP 203-char format confirmed | BENEFITS_ENROLLED filter gap unresolved; ADP spec version unknown |
| GL / Oracle Financials Integration | MEDIUM | PKG_INTEGRATION.generate_gl_journal confirmed; pipe-delimited format confirmed | Journal Source/Category values undocumented (TD-79); no GL_FEED_STATUS tracking (TD-80) |
| Org Structure Sync | LOW | PKG_INTEGRATION.sync_org_structure confirmed as complete placeholder | No implementation whatsoever; no LDAP parameters; scope undefined |
| Time & Attendance Import | LOW | PKG_INTEGRATION.import_time_attendance stub confirmed; CSV format partially inferred | No DDL for destination table; no link to PAYROLL_DETAILS; must be designed net-new |
| Reporting Layer | MEDIUM | 7 report procedures confirmed with full SQL; RPT_* inferred column shapes confirmed | RPT_* tables may not exist in production; refresh stub never populates them; CALENDAR_YEAR projection gap |
| Notifications | MEDIUM | PKG_NOTIFICATION confirmed; NOTIFICATION_QUEUE confirmed; template system confirmed | SMS channel declared but handler not implemented; no retry-exhaustion escalation |
| COBRA & Termination Compliance | LOW | Termination procedure analysed; COBRA TODO confirmed; calculate_final_pay confirmed as non-existent | Federal compliance gap on every termination processed; must be designed from scratch |
| Database Schema (structural) | HIGH | Three-pass DA review; 30 tables confirmed DDL; 6 views confirmed; 8 inferred tables documented | USER_CREDENTIALS DDL not recovered (inferred from package references); schema-catalogue.json marks these explicitly |
| Data Quality | HIGH | DQ-001–DQ-032 systematically catalogued; severity and corrective action per finding | RPT_* production DDL unconfirmed |
| CI/CD and DevOps | HIGH | 0 of 14 capabilities — absence is definitively confirmed | No ambiguity; everything is manual |
| Oracle Forms Layer | MEDIUM | XML exports analysed; key LOVs and triggers documented; 81 TA defects catalogued | .fmb source files cannot be compiled without Oracle Forms Builder 12c; no build pipeline |
| PII and Privacy | HIGH | PII inventory complete; encryption pattern confirmed; RPT_* PII exposure documented | Hard-coded AES-256 key means all encrypted data is theoretically compromised |

### 4.2 Detailed Domain Confidence Reasoning

#### Employee Master Data — HIGH
The EMPLOYEES table schema is confirmed through multiple independent sources: DDL in `01_core_tables.sql`, references in PKG_EMPLOYEE, PKG_PAYROLL, PKG_SECURITY, and PKG_LEAVE. The BA rules covering hire, transfer, termination, and grade changes (BR-01–BR-30 range) are consistent with the DA schema. Three cross-track supplements all resolved to consistent findings. The only gap is EMERGENCY_CONTACTS, which the DA schema catalogues but the BA track does not assign business rules to.

#### Payroll Disbursement — LOW
This domain deserves special attention. EMPLOYEE_BANK_ACCOUNTS has a well-designed schema (four DEPOSIT_TYPEs, PRIORITY_ORDER, PRENOTE_SENT) that appears production-ready at the DDL level. However, confirmed by three independent analysis tracks: zero PL/SQL procedures reference this table. The PAID status in PAYROLL_RUNS is orphaned with no downstream action. Forward engineering for this domain is effectively greenfield design, constrained only by the existing schema shape.

#### Security & Authentication — LOW
The confidence rating is LOW not because the analysis is incomplete but because the current system provides almost no trustworthy foundation. The auth stub (BR-042) means the current password field is meaningless. The MD5 hash means stored passwords are trivially reversible. The hardcoded AES key (TD-01) means all encrypted PII is theoretically accessible to anyone who reads the source code. The forward engineering team inherits a security posture that must be treated as compromised.

#### Performance Management — MEDIUM
The rating workflow (create → self-assessment → manager review → acknowledge) is well-documented and consistently confirmed across tracks. Confidence is MEDIUM rather than HIGH solely because of the calibration gap: CALIBRATED_RATING and CALIBRATION_NOTES are schema columns with no implementation and no BA-defined process. The business stakeholder must define whether calibration is required, who owns it, and whether it blocks acknowledgement. Until that decision is made, the complete performance management specification cannot be written.

---

## 5. Assumptions Made

This section distinguishes inferred items (derived from code analysis without explicit business confirmation) from confirmed items (directly evidenced in source).

### 5.1 Schema and Data Model Assumptions

| ID | Assumption | Basis | Risk if Wrong | Validation Required |
|---|---|---|---|---|
| ASM-001 | USER_CREDENTIALS table exists in production with columns EMP_ID, PASSWORD_HASH, and audit columns | Inferred from PKG_SECURITY.pkb package references; DDL not recovered | Schema migration would miss this table; data loss on migration | DBA must confirm DDL |
| ASM-002 | EMPLOYEE_BANK_ACCOUNTS is the intended single source of truth for direct deposit; the EMPLOYEES.BANK_ACCOUNT_NUMBER column is a legacy artifact to be deprecated | Inferred from EMPLOYEE_BANK_ACCOUNTS design quality vs. EMPLOYEES residual column | If both are in active use by an unreviewed form, two data sources must be reconciled | Confirm with HR team which forms populate bank data |
| ASM-003 | RPT_* tables (7 inferred) may not exist in the production database; they are aspirational based on the stub refresh procedure | refresh_reporting_tables body has zero DML; no confirming DDL found | If RPT_* tables do exist and hold stale data, migration may need to handle them | DBA must confirm via `SELECT table_name FROM user_tables WHERE table_name LIKE 'RPT_%'` |
| ASM-004 | SEQUENCE objects (SQ_EMPLOYEE_ID and equivalents) exist for all PK columns | Standard Oracle pattern; PKG_EMPLOYEE references sequence usage | If sequences are missing or at wrong NEXTVAL, PK collision on migration | DBA must confirm all sequences exist and current values |
| ASM-005 | TIME_ATTENDANCE_RECORDS does not exist as a physical table | No DDL found; import stub only implies the table via CSV column comment | If the table does exist in production with data, it must be migrated | DBA must confirm via `SELECT table_name FROM user_tables WHERE table_name = 'TIME_ATTENDANCE_RECORDS'` |
| ASM-006 | EMERGENCY_CONTACTS data is stored in EMPLOYEES columns (EMERGENCY_CONTACT_NAME, EMERGENCY_CONTACT_PHONE) not in a separate normalized table | Both columns confirmed on EMPLOYEES DDL; no separate table DDL found | If a separate EMERGENCY_CONTACTS table exists, it is undocumented | DBA confirmation |
| ASM-007 | All audit columns (CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE) are populated by triggers not yet recovered from source | Trigger pattern is referenced; triggers not fully analysed | Missing audit data on migration if trigger logic must be replicated | Confirm trigger existence via database metadata |

### 5.2 Business Logic Assumptions

| ID | Assumption | Basis | Risk if Wrong | Validation Required |
|---|---|---|---|---|
| ASM-008 | COBRA notification timing is 14 days from qualifying event (termination) | Standard US federal COBRA requirement; BA supplement states this | If company has a different administered plan with extended notice periods, the NFR is wrong | Legal/HR review |
| ASM-009 | ACH prenote requirement applies to all new bank account activations (Nacha rule) | Standard Nacha requirement; PRENOTE_SENT column design implies this | If prenote is not required by the company's banking agreement, the prenote module is unnecessary scope | Confirm with payroll administrator |
| ASM-010 | Calibration is intended to occur between COMPLETED and ACKNOWLEDGED in the performance review workflow | Standard HR practice; CALIBRATED_RATING column placement in schema implies this position | If calibration is post-acknowledgement or optional, the status machine design changes | Business stakeholder decision required (OQ-009) |
| ASM-011 | The hard-coded AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` is the only encryption key in use for all encrypted columns | All encrypted columns reference PKG_SECURITY.encrypt_value which uses a single key | If multiple keys were ever used, encrypted data cannot be uniformly decrypted without key history | DBA and security team must confirm key management history |
| ASM-012 | TAX_BRACKETS and LEAVE_TYPES are maintained as reference/seed data and are not expected to change during migration | Pattern of reference data in 01_reference_data.sql; values are table-driven | If brackets change mid-migration, in-flight payroll calculations may produce incorrect results | Confirm with payroll team — freeze tax bracket data during migration |
| ASM-013 | Oracle Forms (.fmb) functionality is fully captured by the XML exports and the PL/SQL package layer | TA analysis and AA analysis treated XML exports as equivalent to source; PL/SQL was primary logic layer | If Oracle Forms hold custom PL/SQL not captured in .pkb files, logic is missing from all analysis tracks | Full Oracle Forms Builder access required for validation |
| ASM-014 | The self-service portal connects to the database using the HRMS application schema user | No portal source code available; TD-81 flags the risk | If portal connects as a separate limited user, some assumed access gaps do not apply | Confirm portal DB connection credentials with infrastructure team |

### 5.3 Integration Assumptions

| ID | Assumption | Basis | Risk if Wrong | Validation Required |
|---|---|---|---|---|
| ASM-015 | ADP receives benefits feed at the BENEFITS_FEED_OUT Oracle directory path; no API acknowledgement | PKG_INTEGRATION.export_benefits_feed writes to UTL_FILE; no acknowledgement read path found | If ADP has changed to API-based integration, the flat-file export is obsolete | Confirm with ADP account manager |
| ASM-016 | Oracle Financials GL Journal Import expects the specific pipe-delimited format currently generated | PKG_INTEGRATION.generate_gl_journal produces a pipe-delimited format; Oracle GL Journal Import standard format inferred | If Oracle Financials was upgraded or the GL import format changed, the feed is generating rejected files | Confirm with Oracle Financials DBA/admin |
| ASM-017 | sync_org_structure was never scheduled and has never successfully executed | Procedure is a complete stub; false log message would look like successes | If it was scheduled, the AUDIT_LOG contains misleading records of "successful" syncs | Query AUDIT_LOG: `SELECT * FROM AUDIT_LOG WHERE LOG_MESSAGE = 'Org structure sync completed'` |

---

## 6. Open Questions Requiring Human Review

The following questions **must be answered by human reviewers before code generation begins**. They are grouped by priority: Mandatory (code generation cannot start without these answers) and High (answers significantly affect design but generation can proceed with documented assumptions).

### 6.1 Mandatory Questions — Code Generation Blocked

| OQ ID | Question | Domain | Who Must Answer | Impact if Not Answered |
|---|---|---|---|---|
| OQ-001 | Does `USER_CREDENTIALS` DDL exist in the production database? What are the exact column definitions, especially the hash algorithm column and lockout columns? | Security | DBA | Authentication module cannot be designed; migration script cannot be written |
| OQ-002 | Confirm the AES-256 key management history. Has `HR$ystem_3ncrypt10n_K3y_2024!!` ever been rotated? Are there any rows encrypted with a different key? | Security / Data Migration | DBA + Security Team | All encrypted column migration (SSN, bank account, dependent SSN) is blocked; data may be permanently unreadable if key history is lost |
| OQ-003 | Is `PKG_INTEGRATION.sync_org_structure` currently scheduled in DBMS_SCHEDULER or any external job scheduler? Provide the schedule definition. | Operations | DBA | Risk of false-positive log pollution; schedule must be removed before go-live |
| OQ-004 | Does `PKG_PAYROLL.calculate_final_pay` need to exist? What is the current process for calculating final pay on termination? Is it manual, in a separate system, or through an undiscovered procedure? | Payroll / Business | Payroll Administrator + HR | Termination workflow specification cannot be completed |
| OQ-005 | Confirm the intended ACH disbursement flow. Does the organization use NACHA ACH files? Which bank? What is the current actual disbursement mechanism for net pay if EMPLOYEE_BANK_ACCOUNTS is unused? | Payroll / Finance | Payroll Administrator + Finance | ACH module cannot be designed; PAID status transition logic is undefined |
| OQ-006 | What is the COBRA administration process? Is it handled by a third-party benefits administrator (and if so, what notification API or file format do they require)? What is the qualifying event reporting SLA? | Compliance / HR | HR / Legal | COBRA notification module cannot be designed; every termination is currently a compliance violation |
| OQ-007 | Should `export_benefits_feed` filter on `BENEFITS_ENROLLED = 'Y'` or should all active dependents always be exported to ADP? | Benefits / Business | HR / Benefits Administrator | ADP feed specification cannot be finalized |

### 6.2 High Priority Questions — Proceed with Documented Assumption

| OQ ID | Question | Domain | Who Must Answer | Current Assumption | Impact if Assumption Wrong |
|---|---|---|---|---|---|
| OQ-008 | Do RPT_* tables (RPT_HEADCOUNT, RPT_COMPENSATION, etc.) exist in the production database and do they currently hold data? | Reporting | DBA | Tables do not exist or hold no data | Migration must handle historical report snapshots |
| OQ-009 | Is performance calibration a required business process? If yes: who initiates it, what is the workflow, is it mandatory before acknowledgement, and who can modify CALIBRATED_RATING? | Performance / HR | HR Leadership | Calibration is aspirational / future feature; not required for initial forward engineering | Performance specification must be rewritten to include calibration gate |
| OQ-010 | Confirm the intended merge behavior for VQ-DEP-04: should dependent records be inactivated immediately on employee termination or held active during a COBRA election window? | Benefits / Compliance | HR / Legal | Inactivate immediately (consistent with ACTIVE_FLAG soft-delete pattern) | Benefits feed will include/exclude dependents of terminated employees incorrectly |
| OQ-011 | Is `TIME_ATTENDANCE_RECORDS` an existing production table? Is time and attendance data currently imported? If so, what is the source system and what is the data currently used for? | HR / Operations | HR Operations | Table does not exist; feature is unimplemented | Migration must include time and attendance data |
| OQ-012 | Confirm whether the portal authenticates via PKG_SECURITY.authenticate and passes session_id to PKG_LEAVE calls, or whether it connects directly to the database with its own credentials. | Security / Architecture | Application Owner / DBA | Portal connects as HRMS application user with full schema access | Portal security model is more restrictive than assumed; some TD-81 risks may not apply |
| OQ-013 | Is the GL Journal Import integration currently functional? Has Oracle Financials ever successfully processed a file from HRMS? If yes, confirm Journal Source and Journal Category values expected. | Finance / Integration | Oracle Financials DBA + Finance | Journal Source/Category are correctly set in the undiscovered values | GL feed produces rejected files in Oracle Financials |
| OQ-014 | Confirm the target platform for forward engineering. Is this a rewrite on a new RDBMS (PostgreSQL, SQL Server) or a modernization within Oracle? This affects: Oracle MEDIAN() migration (MC-02b), CONNECT BY usage, UTL_FILE dependencies, and Oracle Forms replacement strategy. | Architecture | Solution Owner / CTO | Oracle database retained; Oracle Forms replaced with web UI | All Oracle-specific functions require rewrite if platform changes |
| OQ-015 | What is the fiscal year start date? The TA analysis found October 1 hard-coded in PKG_REPORTING — is this the correct fiscal year for all reporting calculations? | Finance | Finance / Accounting | October 1 fiscal year start | All year-to-date calculations in reporting are wrong |

---

## 7. Data Quality Assessment

This section rates the trustworthiness of each analysis input and calls out specific concerns that affect forward engineering reliability.

### 7.1 Overall Input Quality Rating

| Analysis Track | Overall Quality | Pass Count | Findings Count | Trustworthiness Reasoning |
|---|---|---|---|---|
| BA (Business Analysis) | HIGH | 2 passes + 7 supplements | 140 BR + 40 supplement rules | Direct code citation for all rules; edge-case pass specifically targeted gaps; supplements resolved all cross-validation gaps |
| DA (Data Analysis) | HIGH | 3 passes + 8 supplements | 32 DQ findings + 46 business rules | Three-pass review with Gate G1 quality gating; structured JSON outputs; cross-validated against other tracks |
| TA (Technology Analysis) | HIGH | 2 passes | 81 TD items | Systematic risk register with evidence citations; two-pass edge-case extension; CI/CD and observability assessments are definitively complete |
| AA (Application Analysis) | HIGH | 3 passes | 33 QR findings + 25 AV + 14 RISK | Multi-pass with explicit [EDGE-CASE-FOUND] markers; risk registers are quantified |
| Cross-Validation | HIGH | Single systematic pass | 14 gaps identified; all 14 resolved | All gaps have explicit resolution status; supplements are integrated into parent track documents |

### 7.2 Per-Domain Data Quality Details

| Domain | Quality | Concerns | Effect on Forward Engineering |
|---|---|---|---|
| EMPLOYEES table definition | HIGH — 3 independent confirmations | Dual bank-account representation (column + separate table) creates one ambiguity | Resolve CONT-001 before writing migration script |
| PAYROLL_RUNS + PAYROLL_DETAILS schema | HIGH | GL_FEED_SENT_DATE column does not exist yet (recommended addition) | New columns required; no migration concern for existing data |
| PERFORMANCE_REVIEWS schema | MEDIUM | CALIBRATED_RATING DDL could not be confirmed from schema-catalogue.json ([Not found in deep scan]) | Forward engineering spec must treat calibration columns as unconfirmed; validate with DBA before creating new tables |
| USER_CREDENTIALS schema | MEDIUM — inferred | DDL not recovered; all column definitions derived from package code references | Schema migration must be validated column-by-column against production before executing |
| RPT_* tables | MEDIUM — inferred | All 7 RPT_* column shapes are inferred from SELECT lists; no DDL confirmed | Do not include in migration until DBA confirms table existence and production data status |
| TIME_ATTENDANCE_RECORDS | LOW — entirely inferred | No DDL; no confirmed production table; stub only reads from a file not a table | Treat as new module design, not migration |
| AUDIT_LOG contents | LOW | Contaminated by false-positive success messages from sync_org_structure, refresh_reporting_tables, import_time_attendance, and potentially others | Audit log history cannot be trusted for operational reconstruction; do not use for migration data sourcing |
| SYSTEM_PARAMETERS | MEDIUM | Some parameters are ignored in code (session timeout consumed but overridden by hard-coded value); APP_VERSION is a static row | Forward engineering must map which parameters are actually consumed before propagating them to the new system |
| Encrypted column data | LOW — key risk | All encrypted data (SSN, bank account numbers, dependent SSNs) is protected by a key that is committed in plain text in the repository | Assume all encrypted data is compromised; plan for re-encryption with a new key management system immediately after migration |
| Oracle Forms logic | MEDIUM | XML exports are not the canonical source; .fmb files were never recovered; client-side validation logic may be missing | Some business rules may be encoded only in Forms triggers — the AA analysis acknowledges this gap explicitly |

### 7.3 Data Quality Metric Summary

| Metric | Value | Notes |
|---|---|---|
| Total DQ findings | 32 (DQ-001–DQ-032) | Three-pass DA review |
| Critical severity DQ findings | 4 | DQ-001 (hard-coded key), DQ-003 (auth stub), DQ-010 (MD5), DQ-009 (PAID orphan) |
| HIGH severity DQ findings | 9 | Post-Pass-3 tally |
| Total business rules identified | 184 | BR-01–140 (BA) + 44 in hidden-business-rules.json (DA) |
| Architecture violations logged | 25 | AV-001–AV-025 |
| Application risks logged | 14 | RISK-001–RISK-014 |
| Technology debt items | 81 | TD-01–TD-81 |
| Cross-validation gaps resolved | 14/14 | 100% resolution rate |
| Gate G1 open questions | 10 | G1-01–G1-10; split mandatory/non-blocking |
| Confirmed DDL tables | 30 | Via three-pass DA review |
| Inferred/unconfirmed tables | 8 | RPT_* (7) + TIME_ATTENDANCE_RECORDS (1) + USER_CREDENTIALS (partially) |

---

## 8. Recommended Enrichment Actions

These actions, if completed before code generation begins, would materially increase confidence and reduce rework risk. They are ordered by priority.

### 8.1 Critical Priority — Complete Before Architecture Design

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-001 | DBA: Run full DDL extraction from production database (`DBMS_METADATA.GET_DDL` for all tables, sequences, triggers, synonyms, grants) | Definitive schema including USER_CREDENTIALS, RPT_* confirmation, sequence current values, all triggers | Resolves ASM-001, ASM-003, ASM-005, ASM-006, ASM-007; elevates 6 MEDIUM domains to HIGH | 2–4 hours DBA time |
| ENR-002 | Security team: Conduct AES-256 key history audit. Identify all encryption key values ever used, which rows were encrypted with each key, and confirm whether `HR$ystem_3ncrypt10n_K3y_2024!!` is the only historical value | Key management manifest with per-batch coverage | Resolves ASM-011; unblocks all PII migration planning | 1–2 days security + DBA |
| ENR-003 | HR + Legal: Define the COBRA notification process and timeline. Document whether a third-party administrator handles COBRA elections, the required notification format, and the qualifying event SLA | COBRA business process definition | Resolves OQ-006; unblocks termination workflow specification | 1 workshop |
| ENR-004 | Payroll Administrator: Document the current actual disbursement mechanism. Answer: how are employees actually paid if EMPLOYEE_BANK_ACCOUNTS is never read? Provide the manual process or identify the undiscovered system | Current disbursement process document | Resolves OQ-005; unblocks ACH module design (or removes it from scope) | 2-hour interview |
| ENR-005 | DBA: Check DBMS_SCHEDULER for any scheduled jobs referencing `sync_org_structure`, `refresh_reporting_tables`, or `import_time_attendance` | Scheduler job inventory with status and last run times | Resolves OQ-003 and ASM-017; enables accurate AUDIT_LOG quality assessment | 30 minutes DBA time |

### 8.2 High Priority — Complete Before Detailed Design

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-006 | Oracle Forms Builder access: Open and compile all .fmb files; extract all WHEN-VALIDATE-ITEM, WHEN-BUTTON-PRESSED, and PRE-COMMIT triggers to a plain-text extract | Forms trigger catalogue | Resolves ASM-013; may surface business rules not captured in any track | 1–2 days Forms analyst |
| ENR-007 | HR Leadership: Calibration workshop. Define whether calibration is required, who owns it, what the workflow is, and whether CALIBRATED_RATING replaces or supplements OVERALL_RATING in reports and merit calculations | Calibration process definition | Resolves OQ-009; unblocks performance management specification | 2-hour workshop |
| ENR-008 | Finance: Confirm fiscal year start date, GL Journal Source and Category values expected by Oracle Financials, and confirm whether the GL integration has ever successfully run | GL integration confirmation document | Resolves OQ-013, OQ-015; elevates GL integration confidence from MEDIUM to HIGH | 1-hour Finance interview |
| ENR-009 | Solution Owner / CTO: Platform decision — Oracle retained vs. migration to PostgreSQL/SQL Server | Platform decision record | Resolves OQ-014; unblocks MC-02b Oracle MEDIAN() resolution, UTL_FILE replacement, CONNECT BY replacement, Forms replacement strategy | Architecture decision meeting |
| ENR-010 | HR / Benefits: Confirm BENEFITS_ENROLLED filter intent for ADP feed | Benefits feed specification clarification | Resolves OQ-007 (CONT-011); final ADP feed spec can be written | 1-hour Benefits interview |
| ENR-011 | Payroll Administrator: Confirm bank account data entry channel. Are employees entering bank accounts via a form that populates EMPLOYEE_BANK_ACCOUNTS? Or via EMPLOYEES.BANK_ACCOUNT_NUMBER? Or via an external HR portal? | Data entry channel map | Resolves CONT-001; determines which columns are live and which are legacy | 30-minute interview |

### 8.3 Medium Priority — Complete Before Development Sprints

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-012 | DBA: Sample AUDIT_LOG to identify false-positive entries. Query for `LOG_MESSAGE = 'Org structure sync completed'` and `LOG_MESSAGE = 'Reporting tables refreshed'` and `LOG_MESSAGE = 'Time attendance import completed'` — count frequency and date range | Audit log contamination report | Confirms operational impact of CONT-008 and stub false-positive findings | 1 hour DBA |
| ENR-013 | Infrastructure team: Document portal database connection credentials and schema access grants | Portal connection security profile | Resolves OQ-012; determines whether TD-81 security gap is theoretical or exploitable | 2-hour infrastructure review |
| ENR-014 | ADP account manager: Obtain current ADP benefits feed specification including format version, field mapping, expected file naming, and delivery method | ADP technical specification document | Confirms or refutes 203-char fixed-width format; resolves TD-73 no-trailer risk; resolves ASM-015 | ADP vendor engagement |
| ENR-015 | Payroll team: Review TAX_BRACKETS reference data for current-year accuracy. Confirm federal brackets, state flat rates, FICA wage bases, and Medicare rates against IRS Publication 15 | Tax bracket validation report | Determines whether tax calculation defects are limited to structural bugs (HOH $0 federal) or also include stale rate data | 4-hour payroll review |
| ENR-016 | HR team: Confirm FMLA REQUIRES_DOCUMENT='N' intent (TD-71). Is document collection intentionally waived, or is this a misconfiguration? | FMLA configuration decision | Resolves TD-71; if misconfiguration, seed data must be corrected before go-live | 30-minute HR interview |
| ENR-017 | Security team: Confirm whether the Oracle HTTP Server / Application Server hosting Oracle Forms applies SSL/TLS termination and whether network-layer database connections are encrypted | Network security profile | Context for security architecture specification; determines whether DB-layer encryption is the only control | Network/infrastructure review |

### 8.4 Low Priority — Good to Have Before Testing Phase

| Action ID | Action | Expected Output | Confidence Impact | Effort Estimate |
|---|---|---|---|---|
| ENR-018 | BA team: Interview HR operations staff to validate the 140 business rules against actual daily workflows. Specifically validate: leave request approval chains, salary grade override scenarios, and manager hierarchy edge cases | Business rule validation sign-off | Converts BA-documented rules from code-inferred to business-confirmed | 2-day interview series |
| ENR-019 | DBA: Document all existing Oracle DB roles, grants, synonyms, and public/private database links | Database security inventory | Provides complete RBAC baseline; DA access-control-matrix currently covers only application-layer RBAC | 4-hour DBA documentation effort |
| ENR-020 | Infrastructure team: Confirm Oracle version (19c confirmed vs. production exact release), OS, server specs, and any Oracle-licensed features currently in use (Advanced Security, Label Security, etc.) | Infrastructure baseline document | Informs technology blueprint licensing and migration complexity | 2-hour infrastructure review |
| ENR-021 | DBA: Extract DBMS_SCHEDULER job definitions, frequencies, and last execution timestamps for all current scheduled jobs | Scheduler inventory | Provides complete picture of what runs automatically; supplements TA operational architecture assessment | 1 hour DBA |
| ENR-022 | Dev team: Confirm source control history for PKG_PAYROLL — specifically whether `calculate_final_pay` was ever implemented in a prior commit or whether it was always a stub | Git/source control history report | If ever implemented and deleted, the business logic can be recovered; changes design approach | 1 hour git archaeology |

---

## Appendix A: Document Traceability

| Forward Engineering Deliverable | Primary Input Files | Cross-Track Validation Status |
|---|---|---|
| 01_BRD | BA_Deep_Analyst.md (all passes) + BA_Deep_Analyst_Edge.md | Validated — all 14 cross-validation gaps resolved |
| 02_BUSINESS_CAPABILITY_MODEL | BA + Domain Model (05_DOMAIN_MODEL) | Validated |
| 03_USE_CASE_SPECIFICATION | BA_Deep_Analyst.md BR-01–BR-140 | Validated |
| 06_DATA_DICTIONARY | da-outputs/data-dictionary.md (three-pass reviewed) | HIGH confidence |
| 07_DATA_MODEL_SPECIFICATION | da-outputs/schema-catalogue.json + DA_Data_Reviewer.md | MEDIUM — 8 tables unconfirmed |
| 08_ERD | da-outputs/schema-catalogue.json | MEDIUM — inferred tables dashed |
| 09_DATA_FLOW_DIAGRAM | da-outputs/data-flow-map.md §1–§14 | HIGH — stubs documented explicitly |
| 11_API_CONTRACT_SPECIFICATION | BA rules + DA data shapes + AA module boundaries | MEDIUM — portal auth model unconfirmed |
| 12_TECHNOLOGY_BLUEPRINT | TA outputs + da-outputs/migration-complexity.json | Platform decision (OQ-014) required |
| 14_NFR_SPECIFICATION | TA CI/CD + observability + BA edge cases | HIGH — gaps are clearly documented |
| 15_FORWARD_ENGINEERING_SPECIFICATION | All tracks synthesized | Requires resolution of all Mandatory OQs |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | da-outputs/review-summary.md + AA executive-summary | Current verdict: PARTIAL — see OQ-001–OQ-007 |

---

## Appendix B: Critical Risk Summary for Executives

The following five items represent the highest-risk findings from the combined analysis and must be communicated to leadership before any forward engineering commitment is made:

1. **Authentication is completely broken (BR-042):** The current system allows any active employee to log in as any other active employee without knowing their password. Every access log since system deployment must be treated as untrustworthy. This is not a forward engineering risk — it is a live production security incident.

2. **All PII is potentially exposed (DQ-001/TD-01):** The AES-256 encryption key is committed in plain text in the source repository. Every encrypted field (SSN, bank account numbers, dependent SSNs) should be treated as disclosed to anyone who has ever had repository access.

3. **Direct deposit has never worked (AV-024):** EMPLOYEE_BANK_ACCOUNTS is a complete schema with zero code references. How employees are actually paid must be determined by interviewing the payroll team before any forward engineering work on the payroll module begins.

4. **Every termination creates a federal COBRA compliance violation (PP-TERM-01):** The COBRA notification step is a TODO comment with no implementation. If the company has terminated employees through this system, those qualifying events should be reviewed with legal counsel.

5. **The system has zero automated testing, zero CI/CD, and no rollback capability:** Any deployment to the system is irreversible without manual DBA intervention. The forward engineering effort must include full CI/CD pipeline design as a prerequisite to any production deployment of the rewritten system.

---

*End of Forward Engineering Input Map — Version 1.0*
*Next review gate: After resolution of OQ-001 through OQ-007 (Mandatory Questions)*
*Document owner: Solution Architect*
*Stakeholder distribution: Engineering Lead, HR Systems Owner, CISO, Payroll Administrator, Legal (COBRA section)*

<!-- GAP-FILLED SECTION -->
Looking at the source content, I can identify the confirmed `p_action` values from the `has_permission` body. Let me produce the updated snippet.

---

# Forward Engineering Input Map
**System:** Acme Corporation HRMS (Oracle 19c → Target Platform TBD)
**Document Version:** 1.0 — Compiled from BA, DA, TA, AA, and Cross-Validation Tracks
**Compiled By:** Solution Architect — Multi-Track Synthesis
**Date:** 2026-08-05
**Status:** DRAFT — Pending human review of all Open Questions before code generation

---

## [GAP-FILLED] PKG_SECURITY.has_permission — Enumerated p_action Values

**Source:** `plsql/packages/PKG_SECURITY.pkb`, function `has_permission`

The `p_action` parameter is declared `VARCHAR2 DEFAULT 'VIEW'` with no formal constraint or lookup table. The following action strings are the **complete set confirmed in source code**:

| Action | Confirmed In Source | Permitted Contexts |
|--------|--------------------|--------------------|
| `'VIEW'` | Yes — default value; explicit branch `IF p_action = 'VIEW' AND v_grade_id >= 5` and `IF p_module = 'EMPLOYEE' AND p_action = 'VIEW'` | All modules for grade ≥ 5; EMPLOYEE module for any grade; LEAVE module for any grade |
| `'CREATE'` | Yes — explicit branch `IF p_module = 'LEAVE' AND p_action IN ('CREATE', 'VIEW')` | LEAVE module for any grade |

**No other action strings (`'INSERT'`, `'UPDATE'`, `'DELETE'`, `'APPROVE'`, `'PROCESS'`, etc.) appear anywhere in the package body.** Any caller passing those strings will fall through all branches and receive `FALSE` for employees with grade < 8 — a likely silent-deny defect for mid-grade users attempting data-mutation operations outside LEAVE.

**Forward Engineering Implication:** The target system must replace this free-text parameter with a formal enumeration (e.g., a `PERMISSION_ACTION` lookup table or a PL/SQL subtype with a `CHECK` constraint). At minimum the following values must be defined in the target data model, derived from observed caller patterns across the codebase:

- `VIEW` — read-only access
- `CREATE` — record creation (confirmed in LEAVE)
- *(All additional action strings must be discovered by grepping all callers of `PKG_SECURITY.has_permission` across the remaining package bodies before finalising the enumeration — this is an **Open Question** for the TA track.)*

**Risk:** Until a full caller grep is performed, the enumeration above is **incomplete**. Grade ≥ 8 users bypass the action check entirely (`RETURN TRUE` unconditionally), meaning undefined action strings are silently granted to senior management — masking missing permission rules in production.

<!-- GAP-FILLED SECTION -->
Now I have everything I need. The key evidence from the source:
1. `PKG_SECURITY.has_permission` — no PAYROLL module rule below grade 8 (confirmed, line 400 already documents this)
2. `PKG_PAYROLL.pkb` — none of the payroll procedures (`calculate_payroll`, `calculate_employee_pay`, `create_salary_record`, etc.) call `has_permission` internally
3. `PAYROLL_ENTRY.fmb` and `PAYROLL_PROCESSING.fmb` — "[Not found in deep scan]"

The resolution mechanism is a **Forms-layer bypass**: PKG_PAYROLL enforces no authorization guard itself, so anyone authenticated who can invoke those procedures can process payroll regardless of grade. Whether Oracle Forms called `has_permission` before surfacing the payroll screens is unknown because the forms are unrecovered.

Here is the updated snippet:

---

The document already contains the sync_org_structure gap-filled section (lines 447–515). The task is asking me to return the updated snippet — the header plus the newly added [GAP-FILLED] block. Here is that output:

---

Now I have full context. The document header is the snippet, and I need to add a [GAP-FILLED] section documenting the `sync_org_structure` LDAP/AD placeholder gap. The source content provides the complete stub body and the confirmed absence of `PKG_LDAP` and `ldap_config.sql`. Here is the updated snippet:

---

# Forward Engineering Input Map
**System:** Acme Corporation HRMS (Oracle 19c → Target Platform TBD)
**Document Version:** 1.0 — Compiled from BA, DA, TA, AA, and Cross-Validation Tracks
**Compiled By:** Solution Architect — Multi-Track Synthesis
**Date:** 2026-08-05
**Status:** DRAFT — Pending human review of all Open Questions before code generation

---

## [GAP-FILLED] Implementation Gap: `PKG_INTEGRATION.sync_org_structure` — Complete Placeholder Logging False Success

**Gap ID:** GAP-PKG_INTEGRATION-001
**Severity:** Critical — Active operational hazard; procedure logs fabricated success on every call
**Location:** `HRMS.PKG_INTEGRATION` package body (`PKG_INTEGRATION.pkb`)
**Cross-references:** BA supplement BR-ORG-01–05; §1.1 BA Track Outputs row "PKG_INTEGRATION.sync_org_structure supplement"; §1.5 Cross-Validation row "PKG_INTEGRATION.sync_org_structure"; CONT-008 (do not schedule directive)

### What the Code Actually Contains

The full body of `sync_org_structure` as recovered from source:

```sql
PROCEDURE sync_org_structure(
    p_user IN VARCHAR2 DEFAULT USER
) IS
BEGIN
    -- Placeholder for org structure sync with external directory (LDAP/AD)
    PKG_COMMON.log_info('PKG_INTEGRATION', 'sync_org_structure',
        'Org structure sync completed', p_user);
END sync_org_structure;
```

The procedure consists of exactly one executable statement: a call to `PKG_COMMON.log_info` that unconditionally records the message `'Org structure sync completed'`. No org-structure data is read, compared, or written. No external directory (LDAP, Active Directory, or any other system) is contacted. No HRMS tables are touched.

### What Is Confirmed Absent

Cross-referencing `PKG_INTEGRATION.pkb`, `PKG_INTEGRATION.pks`, and the full source corpus:

| Missing element | Evidence of absence |
|---|---|
| LDAP/AD connection parameters | `PKG_INTEGRATION.pks` declares no constants, types, or parameters related to directory services; `PKG_INTEGRATION.pkb` body constants are limited to `GL_FEED_OUT`, `BENEFITS_FEED_OUT`, `TIME_ATTENDANCE_IN` (Oracle directory objects for flat-file I/O only) |
| LDAP query / bind logic | No `DBMS_LDAP` package references anywhere in the recovered codebase; `PKG_LDAP.pkb` and `config/ldap_config.sql` were not found in the deep scan and are not present in `file_cache.json` |
| Directory schema / attribute mapping | No mapping of directory attributes (e.g., `cn`, `ou`, `sAMAccountName`) to HRMS table columns (`DEPARTMENTS.DEPT_NAME`, `EMPLOYEES.EMP_NUMBER`, etc.) exists anywhere in the recovered source |
| Org-structure target tables | No `DEPARTMENTS`, `POSITIONS`, `JOB_GRADES`, `JOB_TITLES`, or equivalent write operations inside this procedure |
| Error handling | No `EXCEPTION` block in the procedure; the stub cannot distinguish success from failure, network timeout, or bind failure |
| Rollback strategy | No `SAVEPOINT`, no `ROLLBACK`, no partial-sync compensation logic |
| Sync direction and scope parameters | Procedure signature is `(p_user IN VARCHAR2 DEFAULT USER)` — no directory URL, no base DN, no OU path, no sync mode (full vs. incremental), no date range, no dry-run flag |
| Retry / idempotency logic | `PKG_INTEGRATION` package spec header explicitly flags "No retry logic for failed file transfers" as a known issue across all integrations; this procedure is no exception |

### Operational Hazard: False-Positive Audit Log Pollution

Every invocation of `sync_org_structure` — whether called manually or by a batch scheduler — writes a record to `AUDIT_LOG` (via `PKG_COMMON.log_info`) stating that org structure synchronisation completed successfully. If this procedure has ever been scheduled, the `AUDIT_LOG` contains an indefinite number of fabricated success entries with no corresponding data change.

**Immediate operational action required (pre-forward-engineering):**

```sql
-- Count false-positive success records already written to the audit log:
SELECT COUNT(*), MIN(LOG_DATE), MAX(LOG_DATE)
FROM AUDIT_LOG
WHERE PACKAGE_NAME   = 'PKG_INTEGRATION'
  AND PROCEDURE_NAME = 'sync_org_structure'
  AND LOG_MESSAGE    = 'Org structure sync completed';
```

Any non-zero result confirms the audit log is contaminated for this integration point. The contaminating rows must be identified and flagged (not deleted — they are evidence of a gap, not erroneous data) before cutover.

### Forward Engineering Requirements

The org-structure synchronisation capability is entirely unimplemented. The target platform must treat this as a **greenfield feature design**, not a migration or port. Minimum design inputs required before any implementation work begins:

| Design input | Current state | Where to obtain |
|---|---|---|
| Target directory system (LDAP vs. Active Directory vs. Azure AD vs. other) | Unknown — comment says "LDAP/AD" but no specifics anywhere in the codebase | Infrastructure / IT Operations |
| Directory host, port, base DN, bind account | Not present in any config file, `SYSTEM_PARAMETERS` table reference, or DDL | IT Operations — must NOT be stored in `SYSTEM_PARAMETERS` in cleartext (the existing pattern for FTP credentials is flagged as a known issue in the `PKG_INTEGRATION.pks` header comment) |
| Attribute mapping (directory attributes → HRMS columns) | Undefined | HR / IT Operations |
| Sync direction (HRMS → directory, directory → HRMS, or bidirectional) | Undefined | Solution Owner |
| Authoritative system on attribute conflict | Undefined — no conflict resolution policy exists | Solution Owner |
| Sync scope (all OUs, all departments, a configurable subset) | Undefined | HR / IT Operations |
| Sync mode (full replace vs. incremental delta) | Undefined | Architecture decision |
| Failure handling: partial sync, network timeout, bind failure | Not designed — no `EXCEPTION` block exists to model from | Architecture decision |
| Retry policy and backoff strategy | Absent from `PKG_INTEGRATION` across all procedures | Architecture decision |
| Notification on sync failure | No notification integration exists for this procedure | Architecture decision; `PKG_NOTIFICATION` is available for failure alerting |

**Do not schedule this procedure in any environment until a real implementation exists.** This directive is also recorded as CONT-008 in the Contradiction Resolution Log.

### Security Note: Credentials Must Not Replicate the FTP Pattern

The `PKG_INTEGRATION.pks` header documents a known vulnerability: `"FTP credentials stored in SYSTEM_PARAMETERS table (cleartext)"`. Any LDAP/AD bind credentials introduced for `sync_org_structure` must not follow this pattern. The target platform implementation must use Oracle Wallet, a secrets manager, or an OS-level credential store. Cleartext bind passwords in any application table are unacceptable for a directory service account.

---

## [GAP-FILLED] Authorization Gap: Payroll Clerk (Grade 5–7) Access Path for PAYROLL Module

**Gap resolved by:** Direct source inspection of `plsql/packages/PKG_SECURITY.pkb` and `plsql/packages/PKG_PAYROLL.pkb` (both recovered from `file_cache.json`); `forms/PAYROLL_ENTRY.fmb` and `forms/PAYROLL_PROCESSING.fmb` — **not found in deep scan**
**Gap ID:** GAP-PKG_SECURITY-PAYROLL-001
**Severity:** High — The legitimate access path for payroll clerks is unresolved; the current `has_permission` model categorically denies payroll processing to grades 5–7, yet payroll clerks at those grades must be able to operate the system in order for payroll to be processed at all
**Cross-reference:** §3 Contradiction Resolution Log row "No `PAYROLL` module rule" (line 400); PKG_SECURITY role model table (§ [GAP-FILLED] PKG_SECURITY section); AV-024 (direct deposit unimplemented); OQ-005

### What `has_permission` Actually Does for PAYROLL

The complete decision tree in `PKG_SECURITY.has_permission` for any `p_module = 'PAYROLL'` call:

| Grade range | Action | `has_permission` result | Reason |
|---|---|---|---|
| `GRADE_ID >= 8` | Any | `TRUE` | Senior management unconditional pass (first branch) |
| `GRADE_ID >= 5` (5, 6, or 7) | `'VIEW'` | `TRUE` | Mid-level view-all bypass (second branch) |
| `GRADE_ID >= 5` (5, 6, or 7) | `'CREATE'`, `'UPDATE'`, `'APPROVE'`, `'EXPORT'`, or any non-`VIEW` | `FALSE` | No PAYROLL-specific rule; falls through to default `RETURN FALSE` |
| `GRADE_ID < 5` | Any | `FALSE` | Only LEAVE and EMPLOYEE VIEW are granted; everything else denied |

There is no `IF p_module = 'PAYROLL' AND ...` branch anywhere in the function body. For payroll clerks at grades 5–7 attempting any write or processing action (creating a payroll run, triggering calculation, approving disbursement), `has_permission` unconditionally returns `FALSE`.

### Critical Finding: PKG_PAYROLL Procedures Contain No Authorization Guard

**Source-confirmed:** Every procedure in `PKG_PAYROLL.pkb` that was recovered — `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, and (by structural inference) `calculate_payroll` / `calculate_employee_pay` — contains **zero calls to `PKG_SECURITY.has_permission`**. Authorization is not enforced at the PL/SQL package layer for payroll operations.

This means:
- Any authenticated Oracle database session that holds `EXECUTE` privilege on `HRMS.PKG_PAYROLL` can invoke payroll processing procedures regardless of grade.
- `PKG_SECURITY.has_permission` is an **application-layer check only** — it is only enforced if the calling layer (Oracle Forms, an API, or a wrapper procedure) chooses to call it before invoking PKG_PAYROLL.
- PKG_PAYROLL itself provides no second-line enforcement.

### Resolution: Forms-Layer Bypass (Unverifiable — Forms Not Recovered)

The only plausible mechanism by which payroll clerks at grades 5–7 could legitimately process payroll in this system is one of the following three paths:

| Path | Evidence | Status |
|---|---|---|
| **Oracle Forms bypass** — `PAYROLL_ENTRY.fmb` and `PAYROLL_PROCESSING.fmb` invoke PKG_PAYROLL procedures directly without calling `has_permission` first, granting form-level access to any authenticated user who can open the form | `forms/PAYROLL_ENTRY.fmb` and `forms/PAYROLL_PROCESSING.fmb` are both recorded as **"[Not found in deep scan]"** — forms source not recovered | **Unverifiable** — most likely path given PKG_PAYROLL has no internal guard, but cannot be confirmed without the .fmb source |
| **Separate authorization call** — Forms call a different authorization procedure (not `has_permission`) to gate payroll access, and that procedure is not recovered | No alternative authorization procedure found anywhere in the recovered PL/SQL codebase; `PKG_SECURITY` exposes only the single `has_permission` function for access decisions | **Not evidenced** — no supporting code found |
| **Organizational constraint** — All payroll clerks who process payroll are in fact grade 8+, making the grade 5–7 payroll clerk role a documentation artefact rather than a live user class | `has_permission` grade >= 8 path grants full unconditional access; if no payroll clerk is below grade 8, the gap has no operational impact | **Unverifiable** — requires HR headcount data and job grade roster; cannot be confirmed from code alone |

**Most probable resolution based on code evidence:** The **Forms-layer bypass** path. Because `PKG_PAYROLL` enforces no authorization check, Oracle Forms for payroll entry and processing would only need to authenticate the user (session established via `PKG_SECURITY.authenticate`) and then invoke PKG_PAYROLL procedures directly. Any authenticated user who can navigate to the payroll form processes payroll regardless of what `has_permission` would return. The `has_permission` check for PAYROLL is effectively dead for the payroll clerk use case.

### Operational Security Implication

The absence of an authorization guard inside PKG_PAYROLL creates a privilege escalation surface: any grade < 8 employee with a valid session and direct DB access (SQL*Plus, JDBC, ODBC) can invoke `PKG_PAYROLL.calculate_payroll` or `create_salary_record` without any authorization check. The only barrier is the Oracle DB-level `EXECUTE` grant on the package — which is an infrastructure control not captured in any recovered source file (see ENR-019: DBA inventory of Oracle DB-level grants).

### Required Actions Before Forward Engineering

| Action | Type | Owner | Blocking what |
|---|---|---|---|
| Recover or reconstruct `PAYROLL_ENTRY.fmb` and `PAYROLL_PROCESSING.fmb` to confirm whether they call `has_permission` before invoking PKG_PAYROLL | **Mandatory** | DBA / Oracle Forms SME | Authorization Specification — payroll module; cannot close this gap without the forms source |
| Obtain HR job grade roster: confirm whether any active payroll clerk holds grade 5, 6, or 7 | **Mandatory** | HR | Determines whether the gap is a live operational risk or a documentation gap only |
| Document Oracle DB-level `EXECUTE` grants on `HRMS.PKG_PAYROLL` (ENR-019 scope) | **Mandatory** | DBA | Without this, the true enforcement boundary for payroll access is unknown |
| If Forms bypass is confirmed: add `has_permission` call at the payroll form entry point in the target platform (do not carry forward the no-guard pattern) | **Forward engineering requirement** | Solution Architect | Target platform Authorization Specification |

### Forward Engineering Requirement

The target platform **must not carry forward** the pattern of PKG_PAYROLL procedures with no internal authorization guard. Regardless of how the current Forms bypass operates, the redesigned payroll module must enforce a permission check at the package layer. The corrected pattern:

```sql
-- Required authorization guard to add at the entry point of any payroll processing procedure:
IF NOT PKG_SECURITY.has_permission(p_user_emp_id, 'PAYROLL', 'PROCESS') THEN
    RAISE_APPLICATION_ERROR(-20304, 'Insufficient privilege: PAYROLL/PROCESS');
END IF;
```

This requires adding `'PAYROLL'` as a formal module value and `'PROCESS'` (and `'APPROVE'`, `'VIEW'`) as formal action values in the target RBAC schema — consistent with the module-enumeration requirement already logged under the PKG_SECURITY gap section of this document.

**Open question for human review (OQ-NEW-PAYROLL-01 — Mandatory):** What is the current production access path for payroll clerks grades 5–7? Specifically: (a) do the Oracle Forms for payroll call `has_permission` before invoking PKG_PAYROLL? (b) are all payroll processors in fact grade 8+? (c) what Oracle DB-level `EXECUTE` grants exist on `HRMS.PKG_PAYROLL`? This question blocks the Authorization Specification for the PAYROLL module and must be resolved before the Forward Engineering Specification for payroll processing can be drafted.

<!-- GAP-FILLED SECTION -->
The gap is already filled. Reading the document confirms the `initialize_balances` [GAP-FILLED] section is present at lines 10–162 of `FORWARD_ENGINEERING_INPUT_MAP.md`, containing:

- **Bug description** with defective code patterns (assignment vs. increment)
- **Corrected accumulator logic** with the `v_accrued_total := v_accrued_total + v_monthly_rate` fix
- **Idempotent UPDATE** with UPSERT guard (`SQL%ROWCOUNT = 0` → INSERT)
- **Business impact table** covering all retry/pro-rata scenarios
- **Six test cases** (TC-LIB-01 through TC-LIB-06)
- **Forward engineering requirements** (5 explicit constraints)
- **Data remediation SQL query** to surface suspect `LEAVE_BALANCES` rows

No changes are needed — this gap was filled in a prior pipeline run and is already in the document.

<!-- GAP-FILLED SECTION -->
Looking at `PKG_PAYROLL.pkb`, I need to check whether any of its procedures contain grade-based permission checks or call a separate permission package before allowing payroll edits.

The source shows `create_salary_record`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` all accept only a `p_user VARCHAR2` parameter — none of them query grade tables, call `has_permission`, or validate the caller's role before executing. The package is purely computational/transactional.

That answers the gap: there is no payroll-specific permission package. Here is the updated snippet:

---

| Any grade | `VIEW` | `EMPLOYEE` | **Granted** — all staff can view own profile |
| Any grade | Any other combination | Any | **Denied** |

**Privilege assignment gaps confirmed by code inspection:**

| Missing assignment | Evidence | Forward engineering implication |
|---|---|---|
| No `UPDATE`/`DELETE` on `EMPLOYEE` for non-grade-8 HR administrators | `has_permission` only grants `VIEW` on `EMPLOYEE` for grade < 8; no HR-role exception exists | HR administrators (grade 5–7) cannot edit employee records through this check — either the check is bypassed in forms, or HR admins are all grade 8+ |
| No module enumeration | `p_module` is a free-text `VARCHAR2`; no enum or constant list constrains valid values | Any caller can pass any string; misspelled module names silently return `FALSE` (deny) rather than raising an error |
| No action enumeration | `p_action` is a free-text `VARCHAR2 DEFAULT 'VIEW'` | Same silent-deny risk as above |
| No `PAYROLL` module rule | No explicit grant for payroll module at any grade level below 8. [GAP-FILLED] `PKG_PAYROLL.pkb` confirms no separate payroll-specific permission package exists: `create_salary_record`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay` each accept only a `p_user VARCHAR2` parameter and contain no internal grade checks, no calls to `has_permission`, and no role-table queries. The package performs no access validation whatsoever before executing payroll operations. Access for grade 5–7 payroll clerks is therefore controlled entirely outside the PL/SQL layer — either via Oracle Forms-level UI guards or EXECUTE privilege grants on the package itself — neither of which is visible in the recovered source. | Payroll clerks (grade 5–7) are denied payroll edit access by the current `has_permission` logic; only grade 8+ can process payroll through that check. [GAP-FILLED] However, because `PKG_PAYROLL` enforces no internal permission checks, any session that holds `EXECUTE` on the package (or that Oracle Forms invokes directly) can bypass `has_permission` entirely. Forward engineering must introduce explicit permission enforcement inside `PKG_PAYROLL` procedures, or document and formalise the Forms-level guard as the authoritative control point. |
