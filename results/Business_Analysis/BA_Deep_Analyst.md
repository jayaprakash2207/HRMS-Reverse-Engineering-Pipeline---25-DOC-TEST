All counts check out: 140 total business rules, exactly 33 new ones (BR-108–BR-140), and 36 `[EDGE-CASE-FOUND]` markers (33 rules + 2 discrepancy entries + 1 summary section header).

The merged document is complete. Here's what was done:

---

**Merge summary**

The file `results/Business_Analysis/BA_Deep_Analyst.md` now contains the full merged analysis:

| What changed | Detail |
|---|---|
| **Header** | Version banner updated to "Merged Edition" with merge date |
| **Business Rules** | BR-01–107 unchanged (Pass 1); BR-108–140 appended (33 new rules, all marked `[EDGE-CASE-FOUND]`) |
| **Discrepancy Log** | DISC-001–007 unchanged; DISC-008 and DISC-009 added (`[EDGE-CASE-FOUND]`) |
| **New section** | "Pass 2 — Edge Case Analysis Summary" appended before the completion line — a grouped table of all 33 rules by theme and the top-5 Pass 2 findings by severity |
| **Closing block** | Pass 1 top-3 findings preserved; Pass 2 top-3 additions appended below |

**Nothing in Pass 1 was rewritten or removed.** Every new item carries `[EDGE-CASE-FOUND]` so reviewers can distinguish the two passes at a glance.


---
## [CROSS-VALIDATION SUPPLEMENT] — EMPLOYEE_DEPENDENTS
*Added by cross-track validator — this data was present in another track but missing from this document.*

The EMPLOYEE_DEPENDENTS extraction is complete. Here's a summary of everything appended to `results/Business_Analysis/BA_Deep_Analyst_Edge.md`:

---

**Table structure** — full column inventory with types, nullability, defaults, and all three constraints (`PK_EMP_DEPENDENTS`, `FK_DEP_EMP`, `CHK_RELATIONSHIP`).

**10 business rules (BR-DEP-01 to BR-DEP-10):**
- BR-DEP-03/04: soft-delete pattern; inactive dependents excluded from benefits feed
- **BR-DEP-05 (High severity):** `BENEFITS_ENROLLED` flag is collected but never read or enforced anywhere in the codebase
- **BR-DEP-06 (Critical):** dependent SSN is AES-256 encrypted but no decrypt procedure call exists for dependents — operational gap
- **BR-DEP-09 (High severity):** termination procedure does not touch dependent records — terminated employees' dependents stay active in the benefits feed

**Benefits feed export process flow** — step-by-step, with which dependent columns are exported and what is notably absent (`BENEFITS_ENROLLED`, `SSN_ENCRYPTED`).

**Integration touch-point map** — PKG_INTEGRATION is the only package that references EMPLOYEE_DEPENDENTS; PKG_EMPLOYEE, PKG_PAYROLL, and all triggers have zero references.

**5 new pain points, 4 automation opportunities, 4 validation queue items** — the most important unresolved question being VQ-DEP-04: business policy on whether dependents should be held for COBRA administration before inactivation on termination.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_INTEGRATION.sync_org_structure
*Added by cross-track validator — this data was present in another track but missing from this document.*

The extraction is complete and appended to `BA_Deep_Analyst_Edge.md`. Here is a summary of what was found and added:

---

## `PKG_INTEGRATION.sync_org_structure` — BA Analysis Track Addition

### What the procedure does (in full)
It calls `PKG_COMMON.log_info` with the hardcoded message `'Org structure sync completed'`, then returns. That is the entire body. No tables are read or written, no LDAP/AD connection is opened, no data moves.

### Key findings

| # | Finding | Severity |
|---|---|---|
| BR-ORG-01 | Capability is declared but entirely unimplemented — the comment says "placeholder" | High |
| BR-ORG-02 | Unconditionally logs `'Org structure sync completed'` — false-positive success signal every execution | High |
| BR-ORG-03 | No connection parameters exist anywhere — LDAP host, port, bind DN, credentials are all absent | Medium |
| BR-ORG-04 | Sync scope is undefined — departments, reporting lines, job titles, or all three? | Medium |
| BR-ORG-05 | Procedure interface is not production-ready — no delta-sync mode, no target OU parameter | Medium |

### New artefacts added (BR-ORG-01–05, PP-ORG-01–03, AO-ORG-01–02, VQ-ORG-01–04)

The most operationally dangerous issue is **PP-ORG-01** / **BR-ORG-02**: if this procedure is scheduled, every run writes a success log that no monitoring tool can distinguish from a real completed sync. **VQ-ORG-03** asks whether it is currently scheduled — that should be the first thing confirmed with the DBA team.



---
## [CROSS-VALIDATION SUPPLEMENT] — EMPLOYEE_BANK_ACCOUNTS
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is a complete summary of everything extracted and added to `BA_Deep_Analyst_Edge.md`.

---

## EMPLOYEE_BANK_ACCOUNTS — Extraction Summary

### What was found

**Table structure** — `HRMS.EMPLOYEE_BANK_ACCOUNTS` is a fully-designed direct deposit table supporting split-deposit across multiple accounts via four DEPOSIT_TYPEs (`FULL`, `PARTIAL_AMOUNT`, `PARTIAL_PERCENT`, `REMAINDER`) and a `PRIORITY_ORDER` column. It has standard soft-delete, audit columns, and FK to EMPLOYEES.

**The table is never referenced in any procedure, function, trigger, or view in the analysed source.** This is the single most important finding.

---

### Business Rules (BR-BA-01 through BR-BA-12)

| # | Key finding |
|---|---|
| BR-BA-03 | Schema is designed for full split-deposit (4 DEPOSIT_TYPEs) |
| BR-BA-04 | Account numbers encrypted; routing numbers stored **plain text** |
| BR-BA-05 | ACH prenote columns exist (`PRENOTE_SENT`, `PRENOTE_DATE`) but **no procedure populates them** |
| BR-BA-09 | No cross-column constraint — `PARTIAL_AMOUNT` account with NULL `DEPOSIT_AMOUNT` is valid |
| BR-BA-11 | No totalling constraint — accounts summing to 80% or 120% are accepted |
| BR-BA-12 | **Table is completely unused** in all analysed code — direct cause of DISC-009 (PAID status orphaned) |

---

### Pain Points (PP-BA-01 through PP-BA-07)

- **PP-BA-01 (Critical):** Direct deposit non-functional — bank accounts never read during payroll
- **PP-BA-02 (High):** Routing numbers in plain text
- **PP-BA-03 (High):** ACH prenote not implemented — Nacha compliance gap
- **PP-BA-04/05 (High):** No DEPOSIT_TYPE↔amount validation; no distribution total validation
- **PP-BA-06 (Medium):** No duplicate-account guard
- **PP-BA-07 (Medium):** Termination doesn't inactivate bank accounts

---

### Automation Opportunities (AO-BA-01 through AO-BA-04)

- **AO-BA-01:** Implement the disbursement procedure (read accounts → NACHA ACH file → advance to PAID) — closes PP-BA-01, PP-19, DISC-009
- **AO-BA-02:** Implement prenote step on account creation/reactivation
- **AO-BA-03:** Add distribution validation (null-check, total-check) before save
- **AO-BA-04:** Auto-inactivate accounts on employee termination (mirrors AO-DEP-01)

---

### Validation Queue (VQ-BA-01 through VQ-BA-04 — all UNRESOLVED)

- **VQ-BA-01:** Confirm ACCOUNT_NUMBER_ENC uses same PKG_SECURITY key as SSN (if yes, PP-13 vulnerability extends to bank data)
- **VQ-BA-02:** Check if any unreviewed Forms screen implements prenote
- **VQ-BA-03:** Confirm intended disbursement mechanism (NACHA file / API / manual)
- **VQ-BA-04:** Business policy — inactivate accounts immediately on termination, or hold for final pay?



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_EMPLOYEE.terminate_employee (COBRA, access-revocation, and PKG_PAYROLL.calculate_final_pay sub-steps are TODOs with no BA rules)
*Added by cross-track validator — this data was present in another track but missing from this document.*

The extraction is complete and appended to `BA_Deep_Analyst_Edge.md`. Here is a summary of everything added:

---

## Supplemental Extraction: `PKG_EMPLOYEE.terminate_employee` TODO Sub-steps

### What was extracted

**Step-by-step execution map** for all 13 steps of the procedure, with exact tables read/written at each step, plus a **gap table** listing 6 tables that are never touched but should be (EMPLOYEE_DEPENDENTS, USER_SESSIONS, USER_CREDENTIALS, EMPLOYEE_BANK_ACCOUNTS, PAYROLL_RUNS/DETAILS for final pay, LEAVE_BALANCES for balance decrement).

---

### Sub-step A — COBRA (no code, complete absence)
The procedure has a single TODO comment and takes zero action. COBRA requires employee + dependent notification within 14 days of a qualifying event. Every termination processed through the system creates an unreported qualifying event. Correct sequencing (immediate inactivation vs. hold-for-COBRA-election) is a policy question — **VQ-TERM-02** cross-links to **VQ-DEP-04**.

### Sub-step B — Access Revocation (partial by side-effect)
**New logins are already blocked** by side-effect: `PKG_SECURITY.authenticate` checks `EMPLOYMENT_STATUS = 'ACTIVE'` (BR-73), so a TERMINATED employee can never log in again after the commit. The **only real gap** is the in-flight window: if a session was active at termination time, it stays valid for up to 30 minutes (BR-72). The referenced `PKG_SECURITY.revoke_access` procedure does not exist.

### Sub-step C — `PKG_PAYROLL.calculate_final_pay` (non-existent procedure)
The procedure is called in a TODO comment but has never been created. There is no prorated wage calculation, no PTO payout, no off-cycle payroll run capability, and no way to handle a CLOSED pay period for a termination date.

---

### New artefacts added

| Type | IDs | Count |
|---|---|---|
| Business Rules | BR-TERM-01 – BR-TERM-09 | 9 |
| Pain Points | PP-TERM-01 – PP-TERM-05 | 5 (2 Critical) |
| Automation Opportunities | AO-TERM-01 – AO-TERM-05 | 5 |
| Validation Queue | VQ-TERM-01 – VQ-TERM-05 | 5 (all UNRESOLVED) |

Critical findings: **PP-TERM-01** (COBRA — federal compliance gap on every termination) and **PP-TERM-03** (`calculate_final_pay` does not exist — every termination requires fully manual payroll outside the system).



---
## [CROSS-VALIDATION SUPPLEMENT] — PERFORMANCE_REVIEWS (columns CALIBRATED_RATING, CALIBRATION_NOTES exist in DA schema but no BA business rule and no AA procedure cover the calibration workflow)
*Added by cross-track validator — this data was present in another track but missing from this document.*

Looking through the provided source file now.

Here is everything extractable about `PERFORMANCE_REVIEWS.CALIBRATED_RATING` / `CALIBRATION_NOTES` and the surrounding review workflow from the given sources.

---

## Extraction: PERFORMANCE_REVIEWS Calibration Workflow Gap

### 1. Confirmed: CALIBRATED_RATING and CALIBRATION_NOTES are absent from all PKG_PERFORMANCE procedures

`plsql/packages/PKG_PERFORMANCE.pkb` contains every procedure that touches `PERFORMANCE_REVIEWS`. None of them reference `CALIBRATED_RATING` or `CALIBRATION_NOTES`:

| Procedure / Function | Columns written to PERFORMANCE_REVIEWS | Calibration columns touched? |
|---|---|---|
| `create_review` | REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE | **No** |
| `submit_self_assessment` | SELF_ASSESSMENT, STATUS, MODIFIED_BY, MODIFIED_DATE | **No** |
| `submit_manager_review` | OVERALL_RATING, RATING_LABEL, MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN, STATUS, MODIFIED_BY, MODIFIED_DATE | **No** |
| `acknowledge_review` | EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE, STATUS, MODIFIED_BY, MODIFIED_DATE | **No** |

Read-only procedures (`get_team_reviews`, `get_rating_distribution`) also only reference `OVERALL_RATING` and `RATING_LABEL`, not `CALIBRATED_RATING`.

---

### 2. Status lifecycle — calibration state is missing

The status flow implemented in code:

```
NOT_STARTED  →  SELF_REVIEW / MANAGER_REVIEW  →  COMPLETED  →  ACKNOWLEDGED
```

In standard HR practice, calibration occurs **between COMPLETED and ACKNOWLEDGED** (or between COMPLETED and a final LOCKED state). No `CALIBRATION` or `CALIBRATED` status value is written anywhere in the package. The `STATUS` column transition to `'COMPLETED'` happens inside `submit_manager_review` — immediately, with no intermediate calibration gate.

---

### 3. The rating that IS populated: OVERALL_RATING / RATING_LABEL

`submit_manager_review` enforces:

- **Range rule**: `OVERALL_RATING` must be between 1.0 and 5.0 (error -20403)
- **Label mapping** (set inline):

| OVERALL_RATING | RATING_LABEL |
|---|---|
| ≥ 4.5 | Exceptional |
| ≥ 3.5 | Exceeds Expectations |
| ≥ 2.5 | Meets Expectations |
| ≥ 1.5 | Needs Improvement |
| < 1.5 | Unsatisfactory |

`CALIBRATED_RATING` has no equivalent validation, mapping, or write path. It is a dead column in the current codebase.

---

### 4. Rating distribution report reads the wrong column

`get_rating_distribution` (used for org-wide reporting) aggregates on `OVERALL_RATING` and `RATING_LABEL`:

```sql
SELECT pr.RATING_LABEL, COUNT(*) AS COUNT,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE
FROM PERFORMANCE_REVIEWS pr
WHERE pr.OVERALL_RATING IS NOT NULL
```

If calibration is intended to replace the raw manager rating with an adjusted `CALIBRATED_RATING` for official records, this report is reading the **pre-calibration** value, which is a data correctness defect.

---

### 5. schema-catalogue.json: not recoverable

The file was listed as `[Not found in deep scan]`. Column definitions for `CALIBRATED_RATING` and `CALIBRATION_NOTES` (type, nullable, constraints) cannot be confirmed from the provided sources.

---

### Summary for BA analysis track

**Gap**: The DA schema explicitly stores `CALIBRATED_RATING` and `CALIBRATION_NOTES` on `PERFORMANCE_REVIEWS`, but:

1. No procedure in `PKG_PERFORMANCE` ever writes to either column.
2. No status transition for a calibration phase exists.
3. Reporting (`get_rating_distribution`) uses `OVERALL_RATING`, which is the raw manager-submitted rating, not the calibrated value.
4. No BA business rule defines when calibration occurs, who triggers it, whether it is mandatory, or how `CALIBRATED_RATING` relates to `OVERALL_RATING`.

**Implied business process** (unimplemented): A calibration session — typically run by HR or senior leadership — adjusts individual manager ratings for cross-team fairness. The adjusted rating would be stored in `CALIBRATED_RATING` with rationale in `CALIBRATION_NOTES`. This step is entirely absent from both the application code and the documented business rules.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_LEAVE.initialize_balances
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is what was extracted and added to `BA_Deep_Analyst_Edge.md`:

---

## PKG_LEAVE.initialize_balances — Extraction Summary

**10 Business Rules (BR-LIB-01 through BR-LIB-10)**

The most important ones:

| ID | Finding |
|---|---|
| **BR-LIB-05** | **Defect** — `run_monthly_accrual` accrual retry block uses `SET ACCRUED = v_accrued` (assignment) instead of `SET ACCRUED = ACCRUED + v_accrued` (increment). Equivalent for a freshly created zero row but silently destructive if the `SQL%ROWCOUNT = 0` condition fires on an existing row due to a concurrency anomaly. |
| **BR-LIB-06** | Balance rows are never created at hire time. `hire_employee` does not call `initialize_balances`. Rows are created lazily on the first accrual/adjustment/carryover. |
| **BR-LIB-09** | `OPENING_BALANCE` is always seeded at zero. The only mechanism that sets a non-zero opening balance is `process_carryover`. There is no starter allowance path. |

**Caller Map** — `initialize_balances` is a private lazy-create fallback called by three procedures:
- `adjust_leave_balance` — called when the adjustment UPDATE hits 0 rows; then retries the UPDATE
- `run_monthly_accrual` — called when the accrual UPDATE hits 0 rows; retry has the assignment defect above
- `process_carryover` — called unconditionally before the carryover UPDATE (safe due to `DUP_VAL_ON_INDEX` suppression)

**Full balance lifecycle map** covering all 10 events from row creation through carryover expiry.

**4 Pain Points (PP-LIB-01–04):** New-hire leave gap, inapplicable leave types polluting balance view, no starter allowance mechanism, accrual retry defect risk.

**4 Automation Opportunities (AO-LIB-01–04):** Call `initialize_balances` at hire, add eligibility filtering, add optional opening balance parameter, fix the one-line accrual retry defect.

**4 Validation Queue items (VQ-LIB-01–04):** All unresolved — require business policy decisions on new-hire initialisation, leave type eligibility rules, starter allowances, and re-initialisation contract.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_PERFORMANCE.get_rating_distribution
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is a summary of everything extracted and recorded.

---

## Extraction: `PKG_PERFORMANCE.get_rating_distribution`

**Appended to:** `results/Business_Analysis/BA_Deep_Analyst_Edge.md`

### What the function does

Read-only reporting function. Opens a `SYS_REFCURSOR` over `PERFORMANCE_REVIEWS` (joined to `EMPLOYEES`) and returns one row per rating label with a count and a percentage. Optional `p_dept_id` restricts to a single department; `NULL` = org-wide.

### Key mechanics
- **Denominator = rated reviews only** — `WHERE OVERALL_RATING IS NOT NULL` excludes all in-progress reviews from both the count and the percentage denominator (BR-PERF-02).
- **Window-function percentage** — `ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)` — always sums to 100% across the rated subset.
- **Sort** — `ORDER BY MIN(pr.OVERALL_RATING) DESC` — stable Exceptional-first order derived from numeric floor, not hardcoded label strings.
- **No callers found** — exposed for direct client / reporting tool use.

### New artifacts recorded

| Type | IDs | Count |
|---|---|---|
| Business Rules | BR-PERF-01 – BR-PERF-07 | 7 |
| Pain Points | PP-PERF-01 – PP-PERF-04 | 4 |
| Automation Opportunities | AO-PERF-01 – AO-PERF-03 | 3 |
| Validation Queue | VQ-PERF-01 – VQ-PERF-04 | 4 (all UNRESOLVED) |

### Highest-priority findings

| # | Finding |
|---|---|
| BR-PERF-02 / PP-PERF-01 | Distribution percentages exclude unrated reviews silently — misleading during live cycles; callers cannot tell what fraction of the population has been rated |
| BR-PERF-07 / PP-PERF-04 | Rating band labels are hardcoded in `submit_manager_review`'s CASE expression and frozen at submission time; changing bands requires a code deploy and historical relabelling |
| BR-PERF-06 / VQ-PERF-04 | INNER JOIN silently drops completed reviews for hard-deleted employees — historical distributions may undercount |
| VQ-PERF-01 | Business must confirm whether the denominator policy (rated-only vs. full cycle headcount) is intentional |



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_PERFORMANCE.generate_reviews_for_cycle
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is the complete extraction summary for `PKG_PERFORMANCE.generate_reviews_for_cycle`:

---

## Extraction Summary

**10 Business Rules (BR-GRC-01 – BR-GRC-10)**

| ID | Rule |
|---|---|
| BR-GRC-01 | Only `EMPLOYMENT_STATUS = 'ACTIVE'` employees are included |
| BR-GRC-02 | Only employees with `MANAGER_EMP_ID IS NOT NULL` are included — top-of-hierarchy silently excluded |
| BR-GRC-03 | Reviewer is always the employee's current `MANAGER_EMP_ID` at generation time — no alternate reviewer path |
| BR-GRC-04 | All generated reviews are `REVIEW_TYPE = 'ANNUAL'`, `STATUS = 'NOT_STARTED'` |
| BR-GRC-05 | Duplicate reviews (same cycle, same employee) are silently skipped via `DUP_VAL_ON_INDEX` — procedure is idempotent *only if* the unique constraint exists |
| BR-GRC-06 | Each employee receives a "Performance Review Initiated" email at generation time, unconditionally |
| BR-GRC-07 | **Defect:** `REVIEW_CYCLES.STATUS` is never checked — procedure runs against DRAFT or CLOSED cycles with no error |
| BR-GRC-08 | Single `COMMIT` at end of loop — no savepoints; a mid-loop failure discards all work |
| BR-GRC-09 | Result count reported only via `DBMS_OUTPUT` — no OUT parameter, no audit entry at bulk level |
| BR-GRC-10 | `p_user` propagates to every `create_review` call and into `CREATED_BY` on each review row |

**2 High-severity Pain Points**
- **PP-GRC-01** — No cycle-status guard; DRAFT/CLOSED cycle generation is silently permitted
- **PP-GRC-02** — C-suite and other unmanned employees have no review path; silently excluded

**4 Automation Opportunities** — cycle-status guard (AO-GRC-01), OUT parameter for count (AO-GRC-02), per-employee savepoints (AO-GRC-03), deferred notifications (AO-GRC-04)

**4 Unresolved Validation Queue items** — VQ-GRC-01 (lifecycle call sequence), VQ-GRC-02 (top-of-hierarchy review policy), VQ-GRC-03 (UNIQUE constraint on `PERFORMANCE_REVIEWS(CYCLE_ID, EMP_ID)` not confirmed), VQ-GRC-04 (mid-cycle manager reassignment policy)

All findings appended to `results/Business_Analysis/BA_Deep_Analyst_Edge.md` and memory updated.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_SECURITY.logout
*Added by cross-track validator — data extracted directly from PKG_SECURITY.pkb source.*

---

## `PKG_SECURITY.logout` — BA Analysis Track Addition

### Procedure signature

```sql
PROCEDURE logout(
    p_session_id IN NUMBER
)
```

**Package:** `HRMS.PKG_SECURITY`
**Source file:** `plsql/packages/PKG_SECURITY.pkb`
**Visibility:** Public (declared in package spec, callable externally)

---

### Full procedure body

```sql
PROCEDURE logout(
    p_session_id IN NUMBER
) IS
BEGIN
    UPDATE USER_SESSIONS SET
        LOGOUT_TIME = SYSDATE,
        SESSION_STATUS = 'CLOSED'
    WHERE SESSION_ID = p_session_id;
END logout;
```

---

### Table touched

| Table | Operation | Columns written | Filter |
|---|---|---|---|
| `USER_SESSIONS` | `UPDATE` | `LOGOUT_TIME = SYSDATE`, `SESSION_STATUS = 'CLOSED'` | `SESSION_ID = p_session_id` |

No other tables are read or written. No sequences are consulted. No calls to `PKG_AUDIT` are made.

---

### Business Rules (BR-LGOUT-01 through BR-LGOUT-06)

| ID | Rule | Domain | Type | Severity | Confidence | Source |
|---|---|---|---|---|---|---|
| BR-LGOUT-01 | A successful logout sets `SESSION_STATUS` to `'CLOSED'` and records `LOGOUT_TIME = SYSDATE` on the `USER_SESSIONS` row. | Security | Hard Constraint | High | ✅ HIGH | `PKG_SECURITY.logout` |
| BR-LGOUT-02 | Logout accepts any `SESSION_ID` value — there is no check that the session is currently `'ACTIVE'` before applying the update. Calling `logout` on an already-EXPIRED or already-CLOSED session silently re-stamps `LOGOUT_TIME` and re-sets `SESSION_STATUS = 'CLOSED'` with no error. | Security | Hard Constraint | Medium | ✅ HIGH — confirmed defect/gap | `PKG_SECURITY.logout`; no guard clause present |
| BR-LGOUT-03 | There is no ownership check — any caller with a valid `SESSION_ID` integer can close any other user's session. The procedure does not verify that the session belongs to the currently authenticated user. | Security | Hard Constraint | Critical | ✅ HIGH — confirmed vulnerability | `PKG_SECURITY.logout`; no `EMP_ID` or `USERNAME` filter |
| BR-LGOUT-04 | Logout does not call `PKG_AUDIT.log_action`. The logout event is never recorded in the audit trail. By contrast, login (`authenticate`) calls `PKG_AUDIT.log_action('USER_SESSIONS', v_session_id, 'INSERT', p_username)` — creating an asymmetry: every login is audited, no logout is audited. | Security / Compliance | Compliance | High | ✅ HIGH | `PKG_SECURITY.logout` vs `PKG_SECURITY.authenticate` |
| BR-LGOUT-05 | If the provided `SESSION_ID` does not exist in `USER_SESSIONS`, the `UPDATE` matches zero rows and the procedure completes without error or notification. There is no `SQL%ROWCOUNT` check or `RAISE_APPLICATION_ERROR`. | Security | Soft Constraint | Medium | ✅ HIGH | `PKG_SECURITY.logout`; no post-update row-count guard |
| BR-LGOUT-06 | The transition to `'CLOSED'` is a distinct terminal state from `'EXPIRED'`. `is_session_valid` sets sessions to `'EXPIRED'` on timeout; `logout` sets them to `'CLOSED'` on explicit user action. Both are non-`'ACTIVE'` and therefore blocked by `is_session_valid`. | Security | State Machine | Medium | ✅ HIGH | `PKG_SECURITY.logout`; `PKG_SECURITY.is_session_valid` |

---

### Session state machine (complete, from PKG_SECURITY)

```
                  ┌─────────────┐
    authenticate  │             │
  ──────────────► │   ACTIVE    │
                  │             │
                  └──────┬──────┘
                         │
           ┌─────────────┴──────────────┐
           │                            │
   logout  ▼                   timeout  ▼   (SYSDATE-LOGIN_TIME)*24*60 > 30
      ┌─────────┐              ┌──────────┐
      │ CLOSED  │              │ EXPIRED  │
      └─────────┘              └──────────┘
```

Both `CLOSED` and `EXPIRED` are terminal. No procedure in the analysed source reopens or reactivates a session row; re-authentication always creates a new row via `SEQ_USER_SESSION.NEXTVAL`.

---

### Relationship to existing rules

| Existing rule | Interaction |
|---|---|
| BR-72 — 30-minute absolute timeout | Session timeout set by `is_session_valid`; `logout` provides explicit early closure before that 30-minute window elapses |
| BR-73 — ACTIVE employees only | `authenticate` enforces this at login; `logout` has no corresponding guard — it operates on a session row already in existence |
| Sub-step B (terminate_employee access revocation) | The 30-minute in-flight window gap noted there is directly caused by `terminate_employee` not calling `logout` for active sessions. `logout` IS the correct fix: termination should call `logout` for all `USER_SESSIONS` rows where `EMP_ID = p_emp_id AND SESSION_STATUS = 'ACTIVE'` |

---

### Pain Points (PP-LGOUT-01 through PP-LGOUT-04)

| ID | Description | Severity | Automatable? |
|---|---|---|---|
| PP-LGOUT-01 | **No audit trail for logout.** Every login is audited; no logout is audited. Compliance tools and forensic analysis cannot determine when a user's session ended voluntarily vs. via timeout — only that a login occurred. | High | Yes — one `PKG_AUDIT.log_action` call at the end of the procedure |
| PP-LGOUT-02 | **No ownership check — session hijack / forced logout vector.** Any code path with a guessed or stolen `SESSION_ID` can close any active session. In the current system, `SESSION_ID` is a plain incrementing sequence number (`SEQ_USER_SESSION.NEXTVAL`) which is trivially enumerable. | Critical | Yes — add `AND EMP_ID = SYS_CONTEXT('USERENV', 'CLIENT_IDENTIFIER')` or pass `p_emp_id` and validate |
| PP-LGOUT-03 | **Termination does not call logout.** An employee terminated while logged in retains full system access until the 30-minute absolute timeout. `terminate_employee` references a non-existent `PKG_SECURITY.revoke_access` procedure instead. The correct call is `logout` on all active sessions for that `EMP_ID`. | High | Yes — add a cursor loop in `terminate_employee` that calls `logout` for every `SESSION_ID` where `EMP_ID = p_emp_id AND SESSION_STATUS = 'ACTIVE'` |
| PP-LGOUT-04 | **Silent no-op on invalid session ID.** If a UI bug or race condition submits a `logout` call with a non-existent `SESSION_ID`, the call succeeds with no feedback. The user believes they are logged out; their actual session (if different) remains `ACTIVE`. | Medium | Yes — add `IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20320, 'Session not found'); END IF;` |

---

### Automation Opportunities (AO-LGOUT-01 through AO-LGOUT-03)

| ID | Action | Effort | Value |
|---|---|---|---|
| AO-LGOUT-01 | Add `PKG_AUDIT.log_action('USER_SESSIONS', p_session_id, 'LOGOUT', SYS_CONTEXT(...))` at end of `logout` — closes PP-LGOUT-01 | Low (1 line) | High — restores audit symmetry with login |
| AO-LGOUT-02 | Add `p_emp_id IN NUMBER` parameter and `AND EMP_ID = p_emp_id` to the UPDATE predicate — closes PP-LGOUT-02 | Low (2-line change + spec update) | Critical — eliminates the forced-logout vulnerability |
| AO-LGOUT-03 | Add a bulk-logout helper (or extend `logout` to accept `NULL` = all sessions for an `EMP_ID`) and call it from `terminate_employee` in place of the non-existent `revoke_access` — closes PP-LGOUT-03 and the access-revocation gap in BR-TERM noted in the termination supplement | Medium | High — closes the 30-minute post-termination window |

---

### Validation Queue (VQ-LGOUT-01 through VQ-LGOUT-03 — all UNRESOLVED)

- **VQ-LGOUT-01:** Is there a UI-layer session token (cookie / Oracle Forms session) that is also invalidated on logout, independent of the `USER_SESSIONS` row? If yes, the forced-logout risk (PP-LGOUT-02) may be partially mitigated at the application tier; if no, it is fully exposed.
- **VQ-LGOUT-02:** Does the system currently log the `SESSION_ID` value on the client side in a way accessible to users? If sequence values are visible in URLs or responses, PP-LGOUT-02 is immediately exploitable by any authenticated user.
- **VQ-LGOUT-03:** Business policy — should a voluntary logout (`'CLOSED'`) and an automatic timeout (`'EXPIRED'`) appear as distinct events in compliance reports, or is any non-active session treated identically? This determines whether the existing two-state terminal model is sufficient or whether audit enrichment (VQ-LGOUT-01 + AO-LGOUT-01) also needs to distinguish the reason for closure.



---
## [CROSS-VALIDATION SUPPLEMENT] — EMERGENCY_CONTACTS
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is a summary of everything extracted and added.

---

## EMERGENCY_CONTACTS — BA Analysis Output

The following has been appended to `results/Business_Analysis/BA_Deep_Analyst_Edge.md`.

### Business Rules: BR-EC-01 through BR-EC-10

| ID | Rule |
|---|---|
| BR-EC-01 | FK to EMPLOYEES — ON DELETE NO ACTION blocks hard-deletes of employees with contacts |
| BR-EC-02 | PHONE_PRIMARY NOT NULL — primary phone mandatory; no format validation |
| BR-EC-03 | CONTACT_NAME NOT NULL — name mandatory; duplicates allowed per employee |
| BR-EC-04 | RELATIONSHIP unconstrained free-text — inconsistent with EMPLOYEE_DEPENDENTS which enforces a controlled vocabulary |
| BR-EC-05 | PRIORITY_ORDER defaults to 1 with no UNIQUE constraint — multiple contacts can share the same priority |
| BR-EC-06 | ACTIVE_FLAG defaults 'Y'; soft-delete intended — but no CHECK constraint, unlike every other ACTIVE_FLAG in the schema |
| BR-EC-07 | Multiple contacts per employee permitted; no cap |
| BR-EC-08 | PHONE_SECONDARY and EMAIL optional — only PHONE_PRIMARY required |
| BR-EC-09 | Standard audit trail present; no history table — any update irreversibly overwrites prior contact data |
| BR-EC-10 | CONTACT_ID PK with no visible sequence/trigger in source — generation mechanism unconfirmed |

### Key Finding
EMERGENCY_CONTACTS is never read by any PL/SQL procedure in the codebase. Like EMPLOYEE_BANK_ACCOUNTS, it is a data-capture table with no operational read path — the emergency notification workflow is entirely absent from the application layer.

### Outputs added
- **10 business rules** (BR-EC-01 – BR-EC-10)
- **5 pain points** (PP-EC-01 – PP-EC-05; 2 high: no read path, non-unique priority)
- **4 automation opportunities** (AO-EC-01 – AO-EC-04: get_primary contact function, UNIQUE constraint, ACTIVE_FLAG CHECK, terminate inactivation)
- **4 validation queue items** (VQ-EC-01 – VQ-EC-04: all UNRESOLVED — require business policy decisions)
- Memory updated with VQ-EC-01 through VQ-EC-04 added to the unresolved items list.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_SECURITY.logout
*Added by cross-track validator — this data was present in another track but missing from this document.*

The `PKG_SECURITY.logout` extraction is complete and appended to `results/Business_Analysis/BA_Deep_Analyst.md`. Here is a summary of everything added:

---

## What was extracted

**Procedure:** `HRMS.PKG_SECURITY.logout(p_session_id IN NUMBER)`

**Table touched:** `USER_SESSIONS` — sets `LOGOUT_TIME = SYSDATE` and `SESSION_STATUS = 'CLOSED'` filtered by `SESSION_ID`. No other tables, no audit call, no ownership check.

---

### 6 Business Rules (BR-LGOUT-01 through BR-LGOUT-06)

| ID | Finding |
|---|---|
| BR-LGOUT-01 | Successful logout writes `CLOSED` status + `LOGOUT_TIME` |
| BR-LGOUT-02 | No pre-check for `ACTIVE` status — re-logout is silently accepted |
| **BR-LGOUT-03 (Critical)** | No ownership check — any caller can close any session by ID |
| **BR-LGOUT-04 (High)** | No `PKG_AUDIT.log_action` call — logout is never audited; login is, creating an asymmetry |
| BR-LGOUT-05 | Invalid `SESSION_ID` silently does nothing — zero-rows UPDATE raises no error |
| BR-LGOUT-06 | `CLOSED` (voluntary) and `EXPIRED` (timeout) are distinct terminal states; both block `is_session_valid` |

---

### 4 Pain Points — top two

- **PP-LGOUT-02 (Critical):** `SESSION_ID` is a plain incrementing sequence; any caller can force-close any user's session.
- **PP-LGOUT-03 (High):** `terminate_employee` never calls `logout`, leaving terminated employees active for up to 30 minutes — directly tied to the access-revocation gap already noted in the termination supplement.

---

### Cross-links to existing rules

- **BR-72** (30-minute timeout), **BR-73** (ACTIVE-only login), **Sub-step B of terminate_employee** — `logout` is the correct implementation for the `revoke_access` call that currently references a non-existent procedure.



---
## [CROSS-VALIDATION SUPPLEMENT] — PERFORMANCE_REVIEWS.CALIBRATED_RATING + PERFORMANCE_REVIEWS.CALIBRATION_NOTES + REVIEW_CYCLES.CALIBRATION_DUE — columns and due-date exist in schema but no BA business rule describes the calibration process
*Added by cross-track validator — this data was present in another track but missing from this document.*

Here is everything the two source files reveal about the calibration subsystem, plus the gaps.

---

## Schema Evidence

### `REVIEW_CYCLES.CALIBRATION_DUE`
- **Type:** `DATE`, nullable, no default, no constraint.
- **Lifecycle relevance:** The cycle's `STATUS` check constraint includes `'CALIBRATION'` as a valid state — `CHECK (STATUS IN ('DRAFT', 'OPEN', 'IN_PROGRESS', 'CALIBRATION', 'CLOSED'))` — meaning calibration is a formal, named phase in the cycle lifecycle.
- **Gap:** `create_review_cycle()` in `PKG_PERFORMANCE.pkb` accepts `p_self_review_due` and `p_manager_review_due` as parameters but **has no `p_calibration_due` parameter**, and the `INSERT` statement omits `CALIBRATION_DUE` entirely. The column can only be populated by a direct DML statement outside this package, or by a procedure not present in the files provided.

### `PERFORMANCE_REVIEWS.CALIBRATED_RATING`
- **Type:** `NUMBER(2,1)`, nullable, **no range check constraint**. Compare with `OVERALL_RATING`, which has `CONSTRAINT CHK_RATING_RANGE CHECK (OVERALL_RATING BETWEEN 1.0 AND 5.0)`. The absence of a range constraint on `CALIBRATED_RATING` is a schema-level gap — there is nothing preventing an out-of-range value being written.
- **Semantic intent:** Structurally parallel to `OVERALL_RATING`, implying it stores the post-calibration adjustment to a manager's original rating.

### `PERFORMANCE_REVIEWS.CALIBRATION_NOTES`
- **Type:** `VARCHAR2(4000)`, nullable. Notably uses `VARCHAR2` rather than `CLOB` (unlike `SELF_ASSESSMENT`, `MANAGER_ASSESSMENT`, `STRENGTHS`, `AREAS_FOR_IMPROVEMENT`, `DEVELOPMENT_PLAN`, `EMPLOYEE_COMMENTS` which are all `CLOB`). This implies calibration notes are expected to be brief — consistent with meeting minutes or a rationale note, not a full narrative.

---

## PL/SQL Package Evidence (`PKG_PERFORMANCE.pkb`)

### What is present
- **`submit_manager_review`** writes `OVERALL_RATING` and `RATING_LABEL`, transitions status to `'COMPLETED'`.
- **`get_rating_distribution`** queries `OVERALL_RATING` (not `CALIBRATED_RATING`). This means the rating distribution report reflects manager ratings, not calibrated ratings — suggesting distribution analysis is either a pre-calibration input tool or the calibrated values are unused in reporting.
- **`get_team_reviews`** returns `OVERALL_RATING` and `RATING_LABEL`, no calibration columns.

### What is absent — the complete list of missing calibration procedures
| Missing capability | Evidence of absence |
|---|---|
| Transition cycle to `'CALIBRATION'` status | Only `open_review_cycle` (DRAFT→OPEN) and `close_review_cycle` (→CLOSED) exist. No procedure sets STATUS = 'CALIBRATION'. |
| Set `CALIBRATION_DUE` on a cycle | `create_review_cycle` has no parameter for it; no `update_cycle` or `set_calibration_due` procedure present. |
| Write `CALIBRATED_RATING` | No procedure exists that UPDATEs `CALIBRATED_RATING`. |
| Write `CALIBRATION_NOTES` | No procedure exists that UPDATEs `CALIBRATION_NOTES`. |
| Bulk calibration submission | No procedure accepts a set of review IDs with adjusted ratings (a common calibration meeting workflow). |
| Calibration access control | No role/permission check gates who can set `CALIBRATED_RATING`. |
| Post-calibration notification | `submit_manager_review` and `acknowledge_review` have notification calls; no equivalent exists for calibration completion. |
| Rating distribution using calibrated values | `get_rating_distribution` uses `OVERALL_RATING`; no variant queries `CALIBRATED_RATING`. |

---

## Inferences for BA Analysis

1. **Calibration is a cycle-level phase, not a per-review status.** The `'CALIBRATION'` value appears only in `REVIEW_CYCLES.STATUS`, not in `PERFORMANCE_REVIEWS.STATUS`. Individual reviews have no calibration state — only the cycle does. The business process likely convenes a panel that reviews all ratings in a cycle and writes adjusted values back.

2. **`CALIBRATED_RATING` can override `OVERALL_RATING` but the rule governing when/whether it applies is undocumented.** The schema carries both columns simultaneously with no constraint enforcing their relationship (e.g., no trigger ensuring `CALIBRATED_RATING` is only set when cycle is in `'CALIBRATION'` status).

3. **`CALIBRATION_DUE` is effectively a dead column** in the current codebase — no path through the package populates it. It may be populated by a Forms module directly via DML, by a missing package, or it was planned but never implemented.

4. **Rating-label recalculation after calibration is unresolved.** `submit_manager_review` derives `RATING_LABEL` from `OVERALL_RATING` using a CASE expression. If `CALIBRATED_RATING` differs, there is no corresponding `CALIBRATED_RATING_LABEL` column and no procedure to recompute the label — the displayed label would be inconsistent with the calibrated score.

5. **The `CALIBRATION_NOTES` size limit (4000 bytes) vs. CLOB pattern** suggests the design intent is a short rationale entered at a calibration meeting, not a full narrative justification.

---

## Suggested BA Business Rules to Draft

| Rule ID | Rule |
|---|---|
| BR-NEW-1 | A review cycle must transition to `CALIBRATION` status before `CALIBRATED_RATING` or `CALIBRATION_NOTES` may be written on any review in that cycle. |
| BR-NEW-2 | Only designated HR calibration officers (role TBD) may update `CALIBRATED_RATING` and `CALIBRATION_NOTES`. |
| BR-NEW-3 | `CALIBRATED_RATING` must satisfy the same 1.0–5.0 range as `OVERALL_RATING`. A schema constraint should be added. |
| BR-NEW-4 | When `CALIBRATED_RATING` differs from `OVERALL_RATING`, the effective rating used in compensation and promotion decisions is `CALIBRATED_RATING`. |
| BR-NEW-5 | `CALIBRATION_DUE` on the cycle record must be set at cycle creation and must fall after `MANAGER_REVIEW_DUE`. |
| BR-NEW-6 | Downstream reporting (rating distribution, compensation inputs) must read `CALIBRATED_RATING` where populated, falling back to `OVERALL_RATING` — not always `OVERALL_RATING` as the current `get_rating_distribution` does. |
| BR-NEW-7 | An employee-facing notification should fire when their `CALIBRATED_RATING` is set, if it differs from `OVERALL_RATING`. |

These seven rules cover the full gap. They should be confirmed with the HR process owner before being treated as authoritative.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_INTEGRATION.get_integration_status
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is a complete summary of what was extracted and appended.

---

## `PKG_INTEGRATION.get_integration_status` — Extraction Summary

### What the function does

A three-line public function that is a pure thin wrapper:

```sql
RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS');
```

It looks up a row in `SYSTEM_PARAMETERS` where `PARAM_GROUP = 'INTEGRATION'` and `PARAM_NAME = <p_integration_name> || '_STATUS'`. Returns the stored VARCHAR2 value, or NULL if no row exists.

---

### Key findings (8 business rules, 5 pain points, 4 automation opportunities, 4 VQ items)

| Finding | ID | Severity |
|---|---|---|
| None of the 4 sibling procedures ever calls `get_integration_status` — integrations run unconditionally, status flag has zero enforcement | BR-GIS-04 / PP-GIS-01 | **High** |
| No procedure in the package ever writes a `_STATUS` value — the function returns a static, manually-maintained label, not the actual last-run outcome | BR-GIS-05 / PP-GIS-02 | **High** |
| FTP credentials and status values co-exist in the same `SYSTEM_PARAMETERS` group under `PARAM_GROUP = 'INTEGRATION'` (cleartext, no structural separation) | BR-GIS-08 / PP-GIS-05 | **High** |
| No exception handler — any `PKG_COMMON.get_param` failure propagates unhandled to the caller | BR-GIS-06 / PP-GIS-03 | Medium |
| Status vocabulary (`'ACTIVE'`, `'DISABLED'`, `'ERROR'`, etc.) is entirely undefined — no constraint, no enum, no documentation | PP-GIS-04 / VQ-GIS-02 | Medium |

### Four expected `SYSTEM_PARAMETERS` keys (inferred)

| Integration Procedure | Expected PARAM_NAME |
|---|---|
| `generate_gl_journal` | `GL_FEED_STATUS` |
| `export_benefits_feed` | `BENEFITS_STATUS` |
| `import_time_attendance` | `TIME_ATTENDANCE_STATUS` |
| `sync_org_structure` | `ORG_SYNC_STATUS` |

None of these rows are written by any code in the analysed source.

All findings appended to `results/Business_Analysis/BA_Deep_Analyst_Edge.md` and memory updated.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_INTEGRATION.get_integration_status
*Added by cross-track validator — this data was present in another track but missing from this document.*

The memory file already has the `get_integration_status` entry and the `How to apply` section already includes the four VQ-GIS items. The extraction was already completed and persisted in a prior session. Here is a complete summary of everything recorded:

---

## `PKG_INTEGRATION.get_integration_status` — BA Analysis Summary

**Location:** `results/Business_Analysis/BA_Deep_Analyst_Edge.md`, lines 1850–2023

---

### Function

```sql
FUNCTION get_integration_status(p_integration_name IN VARCHAR2) RETURN VARCHAR2 IS
BEGIN
    RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS');
END get_integration_status;
```

Three lines. No variables, no exception handler, no logging.

---

### Table Access

| Table | Access | Path |
|---|---|---|
| `SYSTEM_PARAMETERS` | SELECT | Indirect — via `PKG_COMMON.get_param('INTEGRATION', ...)` |

**Key convention:** `PARAM_GROUP = 'INTEGRATION'`, `PARAM_NAME = <name> || '_STATUS'`

Inferred rows: `GL_FEED_STATUS`, `BENEFITS_STATUS`, `TIME_ATTENDANCE_STATUS`, `ORG_SYNC_STATUS`

---

### Business Rules (BR-GIS-01 – BR-GIS-08)

| ID | Rule | Confidence |
|---|---|---|
| BR-GIS-01 | Integration status is stored as a VARCHAR2 in `SYSTEM_PARAMETERS`; no dedicated status table or typed column | High |
| BR-GIS-02 | Function is read-only; no writes, no side effects | High |
| BR-GIS-03 | Returns NULL (no error) if no matching row in `SYSTEM_PARAMETERS` | High |
| BR-GIS-04 | None of the four sibling procedures (`generate_gl_journal`, `export_benefits_feed`, `import_time_attendance`, `sync_org_structure`) ever calls `get_integration_status` — all run unconditionally | High |
| BR-GIS-05 | No procedure in the package calls `set_param` or any equivalent to write a `_STATUS` value; status must be maintained externally | High |
| BR-GIS-06 | No exception handler — any exception from `PKG_COMMON.get_param` propagates unhandled to the caller | High |
| BR-GIS-07 | `p_integration_name` is unbounded VARCHAR2; oversized value can cause `ORA-01401` or silent truncation depending on column definition | Medium |
| BR-GIS-08 | Cleartext FTP credentials co-exist with status values under `PARAM_GROUP = 'INTEGRATION'` — separated only by `PARAM_NAME` naming convention, no physical or access-control separation | High |

---

### Pain Points (PP-GIS-01 – PP-GIS-05)

| ID | Issue | Severity |
|---|---|---|
| PP-GIS-01 | Status flag is never enforced — all four integrations run unconditionally; `'DISABLED'` has no effect | High |
| PP-GIS-02 | Status is never written after execution — function always returns a static, manually-maintained label | High |
| PP-GIS-03 | No exception handler — `PKG_COMMON.get_param` failures propagate to caller with no logging or graceful degradation | Medium |
| PP-GIS-04 | Status vocabulary is undefined — no CHECK constraint, no documentation; free-text values inconsistent across environments | Medium |
| PP-GIS-05 | Cleartext FTP credentials and status values share the same `PARAM_GROUP = 'INTEGRATION'` namespace; status queries expose credentials | High |

---

### Automation Opportunities (AO-GIS-01 – AO-GIS-04)

| ID | Opportunity | Impact |
|---|---|---|
| AO-GIS-01 | Add pre-execution status guard to all four procedures | High — makes status enforcement functional |
| AO-GIS-02 | Add post-execution status write (OK/ERROR) to all four procedures | High — turns function into live health indicator |
| AO-GIS-03 | Add exception handler with `RETURN 'UNKNOWN'` safe default | Low — defensive coding |
| AO-GIS-04 | Separate credentials into `PARAM_GROUP = 'INTEGRATION_CREDS'` with encryption | High — eliminates cleartext credential exposure |

---

### Validation Queue (VQ-GIS-01 – VQ-GIS-04, all UNRESOLVED)

| ID | Question |
|---|---|
| VQ-GIS-01 | Any external caller (scheduler, Forms, reporting) calling `get_integration_status`? |
| VQ-GIS-02 | Intended controlled vocabulary for `_STATUS` values? |
| VQ-GIS-03 | Are credentials in `SYSTEM_PARAMETERS` encrypted at rest, or accessible beyond DBA? |
| VQ-GIS-04 | Intended mechanism for writing `_STATUS` values (manual SQL, admin package, scheduler, procedures)? |

---

The extraction was already in the edge file from a prior session. The memory index has been confirmed up to date with all four VQ-GIS items in the unresolved list.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_PAYROLL.get_ytd_earnings
*Added by cross-track validator — this data was present in another track but missing from this document.*

The extraction is complete. Here is a summary of everything added to `BA_Deep_Analyst_Edge.md`:

---

## `PKG_PAYROLL.get_ytd_earnings` — Extraction Summary

**11 Business Rules (BR-YTD-01 to BR-YTD-11)**

The most important:

- **BR-YTD-08** — The current period's gross is already inserted into `PAYROLL_DETAILS` *before* `get_ytd_earnings` is called within `calculate_employee_pay`. The function therefore returns YTD *including* the current period — this is by design for correct FICA wage-base enforcement, but it is a silent ordering contract with no documentation.
- **BR-YTD-05 / BR-YTD-06** — The YTD figure is the direct input to Social Security cap enforcement ($168,600) and Additional Medicare threshold logic ($200,000). Errors in YTD propagate directly into FICA withholding.
- **BR-YTD-07 (confirmed defect)** — `get_payslip` hardcodes `0 AS YTD_GROSS` and `0 AS YTD_NET`. The function exists and works, but is never called from the payslip procedure.
- **BR-YTD-10** — Mid-year hire YTD reset defect is acknowledged in the package spec (`pks`) but is unfixed and undocumented.

**4 Pain Points (PP-YTD-01 to PP-YTD-04)**
- PP-YTD-01 (High): Payslips always show $0.00 for YTD — compliance and W-2 readiness risk.
- PP-YTD-02 (High): One three-table aggregation per employee per run inside a cursor loop — dominant performance bottleneck; degrades through the year.
- PP-YTD-03 (Medium): Silent INSERT-before-call ordering dependency that breaks FICA cap enforcement if ever reordered.
- PP-YTD-04 (Medium): Mid-year hire tax compliance risk — FICA/Medicare may be incorrect for new hires in their first year.

**4 Automation Opportunities (AO-YTD-01 to AO-YTD-04)**
- AO-YTD-01: Fix payslip YTD fields (high impact).
- AO-YTD-02: Pre-aggregate YTD for all employees in one query at the top of `calculate_payroll` instead of n individual queries (high impact).
- AO-YTD-03: Add a comment pinning the ordering contract.
- AO-YTD-04: Investigate and fix mid-year hire edge case with a test case.

**4 Validation Queue Items (VQ-YTD-01 to VQ-YTD-04)** — all UNRESOLVED

VQ-04 from the original Agent 1 pass (YTD accumulation) is now structurally resolved; the two open sub-items are tracked as VQ-YTD-01 and VQ-YTD-02.



---
## [CROSS-VALIDATION SUPPLEMENT] — PKG_NOTIFICATION (SMS and IN_APP types declared in NOTIFICATION_QUEUE schema but PKG_NOTIFICATION.process_queue only handles EMAIL — no BA rule differentiates these types or governs fallback)
*Added by cross-track validator — this data was present in another track but missing from this document.*

The extraction is complete. Here is a summary of everything added to `BA_Deep_Analyst_Edge.md`:

---

**PKG_NOTIFICATION supplemental extraction appended** (358 new lines, file now 2,381 lines).

**What was extracted from the source:**

**12 Business Rules (BR-NOTIF-01 – BR-NOTIF-12):**
- BR-NOTIF-01/02: `send_notification` accepts any type unconstrained; `process_queue` hard-codes `AND NOTIFICATION_TYPE = 'EMAIL'` — this is the core gap.
- BR-NOTIF-03: SMS and IN_APP rows are permanently trapped in `STATUS='PENDING'` with no delivery path.
- BR-NOTIF-04: All SMTP config (host, port, from-address, from-name) is embedded as package constants — no runtime override.
- BR-NOTIF-05/06: NULL email is resolved at queue-time from `EMPLOYEES`; if still NULL, the row is silently excluded from `process_queue` with no `FAILED` transition.
- BR-NOTIF-07: `send_notification` is `AUTONOMOUS_TRANSACTION` — its commit is independent of the caller's transaction.
- BR-NOTIF-08: Queuing exceptions are swallowed; callers never know notification failed.
- BR-NOTIF-09: One UTL_SMTP connection opened per row — no connection reuse.
- BR-NOTIF-10: Retry cap at 3; permanently FAILED after that, no dead-letter path.
- BR-NOTIF-11: Single post-batch COMMIT — session interruption risks duplicate delivery.
- BR-NOTIF-12: Priority-first, FIFO ordering; no starvation guard.

**Process flow** documenting all four lifecycle branches (EMAIL delivered, EMAIL null-excluded, SMS dead-end, IN_APP dead-end).

**7 Pain Points** (PP-NOTIF-01 Critical, PP-NOTIF-02/03/04 High, PP-NOTIF-05/06/07 Medium).

**6 Automation Opportunities** including SMS processor, IN_APP processor, SMTP externalisation, type CHECK constraint, undeliverable-row marking, and per-row commit.

**4 Validation Queue items** (VQ-NOTIF-01–04) — all UNRESOLVED, covering channel strategy, schema constraint, operational backlog, and SMTP config per-environment.



---
## [CROSS-VALIDATION SUPPLEMENT] — TAX_BRACKETS
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is a complete summary of what was extracted and recorded.

---

## TAX_BRACKETS extraction — complete

### What was found

**Table (`HRMS.TAX_BRACKETS`)** — 10 columns, designed as a multi-year, multi-jurisdiction bracket store. Supports federal (STATE_CODE = NULL) and state (STATE_CODE = 'XX') brackets, partitioned by TAX_YEAR, with BASE_TAX shortcut column for progressive calculation. Constrained filing status to 4 values. Notable absences: no UNIQUE key, no range-validity CHECK, no rate-range CHECK, no state FK.

**The central defect — TAX_BRACKETS is dead.** Neither `calculate_federal_tax` nor `calculate_state_tax` reads from it. Both functions contain explicit acknowledgement:

> `-- NOTE: Hard-coded 2024 brackets - should read from TAX_BRACKETS table`  
> `-- TODO: Read from TAX_BRACKETS table instead of hard-coding`

### All findings catalogued (appended to `BA_Deep_Analyst_Edge.md`)

| Category | Count | Highlights |
|---|---|---|
| Business Rules (BR-TAX-01–16) | 16 | Bracket logic, annualization, allowances, state flat-rate, filing status gaps |
| Defects | 7 | 2 Critical, 3 High, 1 Medium, 1 Low |
| Pain Points (PP-TAX-01–05) | 5 | 2 Critical |
| Automation Opportunities (AO-TAX-01–04) | 4 | AO-TAX-01 activates the table as designed |
| Validation Queue (VQ-TAX-01–04) | 4 | All UNRESOLVED |

### Two critical defects

1. **HEAD_OF_HOUSEHOLD → $0 federal withholding.** No IF branch exists for this filing status. Employees on W-4 HEAD_OF_HOUSEHOLD receive zero federal income tax withheld every period — silent employer failure-to-withhold liability.

2. **Hard-coded 2024 brackets in code, not data.** Every IRS annual inflation adjustment requires a developer edit and code deployment. 2025 payroll runs are already using stale 2024 brackets.

