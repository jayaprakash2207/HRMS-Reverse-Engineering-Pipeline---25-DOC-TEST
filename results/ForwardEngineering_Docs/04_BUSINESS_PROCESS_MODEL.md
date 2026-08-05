# 04 — Business Process Model

=== PROCESS 3: LEAVE REQUEST AND APPROVAL ===

Actors: Employee, Direct Manager, HR Admin
Services: PKG_LEAVE, VW_LEAVE_SUMMARY
UI: LEAVE_FORM

[STEP 1] Employee submits leave request (LEAVE_FORM)
  PKG_LEAVE.apply_for_leave(p_emp_id, p_leave_type_id, p_start_date, p_end_date, p_reason)
  Business rules checked:
    BR-CRITICAL-005: AVAILABLE balance (virtual column) ≥ requested days
    BR-CRITICAL-006: No approved leave overlapping same date range
    BR-HIGH-001: p_start_date ≥ SYSDATE (no backdated requests)
  INSERT LEAVE_REQUESTS (STATUS='PENDING', APPLIED_DATE=SYSDATE)
  INSERT NOTIFICATION_QUEUE → manager email

[STEP 2] Manager reviews (LEAVE_FORM filtered view, own direct reports)
  Grade ≥ 8: see all employees
  Grade 5–7: see own department
  Grade < 5: cannot access approval screens

  APPROVE → PKG_LEAVE.approve_leave(p_request_id, p_approved_by)
    UPDATE LEAVE_REQUESTS SET STATUS='APPROVED', APPROVED_BY, APPROVED_DATE
    UPDATE LEAVE_BALANCES: PENDING = PENDING + days_requested
    *** DEFECT: AVAILABLE virtual column deducts PENDING; so balance immediately reflects
        approved-but-not-taken leave correctly — this is INTENTIONAL per design ***

  REJECT → PKG_LEAVE.reject_leave(p_request_id, p_approved_by, p_reason)
    UPDATE LEAVE_REQUESTS SET STATUS='REJECTED'
    No LEAVE_BALANCES row touched

[STEP 3] Leave taken — return from leave
  PKG_LEAVE.record_leave_taken(p_request_id) called on leave completion date
    UPDATE LEAVE_BALANCES: USED = USED + days_taken, PENDING = PENDING - days_requested
    AVAILABLE recomputed automatically (virtual column)
    INSERT EMPLOYEE_HISTORY (CHANGE_TYPE='LEAVE_TAKEN')

[STEP 4] Monthly accrual (DBMS_SCHEDULER — inferred)
  PKG_LEAVE.accrue_leave(p_accrual_date)
  Accrual rate by leave type (LEAVE_TYPES.ACCRUAL_RATE)
  UPDATE LEAVE_BALANCES: ACCRUED = ACCRUED + accrual_amount WHERE leave year matches
  Looking at the source content, I can see the `get_leave_balance` function references `OPENING_BALANCE` in its formula (`OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING`), which is the architectural hook for carry-forward — but no procedure that populates `OPENING_BALANCE` at year-end appears in the provided code. I'll annotate G3 with that finding.

  Looking at the source content, I can confirm the absence of the rollover mechanism from PKG_LEAVE.pkb and add that confirmation as a [GAP-FILLED] finding — the schema intent is clear but the implementation is a confirmed gap.

---

  *** SCHEDULER: JOB inferred from code comments; no CREATE_JOB DDL provided ***
  [GAP-FILLED] Confirmed via full review of PKG_LEAVE.pkb: no DBMS_SCHEDULER.CREATE_JOB
  call, no scheduler-wrapper procedure, and no year-end batch invocation exist anywhere
  Looking at the source content, I can confirm `final_pay` is absent from `PKG_PAYROLL.pkb` — the package body lists `create_salary_record`, `get_current_salary`, `get_salary_as_of`, `create_pay_periods`, `close_pay_period`, `get_current_period`, `create_payroll_run`, `calculate_payroll`, and `calculate_employee_pay`, but no `final_pay` procedure body anywhere in the recovered source.

---

  in the package body. The rollover job is a confirmed implementation gap.
  [GAP-FILLED] final_pay confirmed absent from PKG_PAYROLL.pkb: the recovered
  package body contains create_salary_record, get_current_salary, get_salary_as_of,
  create_pay_periods, close_pay_period, get_current_period, create_payroll_run,
  calculate_payroll, and calculate_employee_pay — but no final_pay procedure body.
  Final pay calculation at employee termination (prorated salary for the partial
  pay period, accrued leave balance payout, and outstanding deduction clearance)
  is entirely unimplemented in PKG_PAYROLL. This is a confirmed implementation gap.

GAP SUMMARY — Process 3:
  G1: No half-day leave support (whole integer days only, no 0.5)
  G2: No FMLA / statutory leave type enforcement
  G3: Carry-forward logic not observed; year-end balance disposition unknown
      [GAP-FILLED] LEAVE_BALANCES.OPENING_BALANCE exists and is included in the
      available-balance formula inside get_leave_balance:
        available = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING
      This confirms the schema is designed to carry unused balance forward via
      OPENING_BALANCE on a per-employee/per-leave-type/per-calendar-year row.
      [GAP-FILLED] PKG_LEAVE.pkb was reviewed in full: no year_end_rollover
      procedure, no carry_forward_balances procedure, and no DBMS_SCHEDULER
      job creation for a rollover batch were found anywhere in the package body.
      OPENING_BALANCE population is a confirmed implementation gap: the column
      exists and is read by get_leave_balance, but no code path writes to it at
      year-end. New-year LEAVE_BALANCES rows are either seeded manually, populated
      by an external script outside this codebase, or left at zero — meaning the
      carry-forward design intent encoded in the schema is not currently fulfilled
      by any discovered PL/SQL procedure.
      However, no procedure or job within PKG_LEAVE populates OPENING_BALANCE
      at year-end (e.g. rolling prior year's closing balance into next year's
      OPENING_BALANCE). The population mechanism is absent from the provided
      source: no year_end_rollover, no carry_forward_balances, and no
      CREATE_JOB DDL were found. Disposition rules (cap on carry-forward days,
      leave types excluded from carry-forward, expiry date for carried days)
      remain unresolved and must be sourced from HR policy documents or a
      missing batch package.
  G4: Accrual scheduler DDL absent


=== PROCESS 4: PERFORMANCE REVIEW CYCLE ===

Actors: HR Admin, Employee, Direct Manager, Skip-Level Manager
Services: PKG_PERFORMANCE
UI: PERFORMANCE_FORM

[STEP 1] Cycle creation (HR Admin)
  PKG_PERFORMANCE.create_review_cycle(p_cycle_name, p_review_year, p_start_date, p_end_date)
  INSERT REVIEW_CYCLES (STATUS='OPEN')

[STEP 2] Self-assessment (Employee)
  PKG_PERFORMANCE.submit_self_review(p_review_id, p_rating, p_comments)
  PERFORMANCE_REVIEWS row: SELF_RATING set, SELF_COMMENTS set
  BR: OVERALL_RATING IN (1,2,3,4,5) — enforced by CHECK constraint

[STEP 3] Manager assessment
  PKG_PERFORMANCE.submit_manager_review(p_review_id, p_manager_id, p_rating, p_comments)
  UPDATE PERFORMANCE_REVIEWS: MANAGER_RATING, MANAGER_COMMENTS, REVIEWED_DATE
  INSERT NOTIFICATION_QUEUE → employee email

[STEP 4] Calibration (SCHEMA EXISTS, CODE ABSENT)
  REVIEW_CYCLES.STATUS transitions: OPEN → UNDER_REVIEW → CALIBRATING → CLOSED
  PERFORMANCE_REVIEWS.CALIBRATED_RATING column exists (NUMBER(2,1))
  PERFORMANCE_REVIEWS.CALIBRATION_NOTES column exists (VARCHAR2 500)
  *** CRITICAL GAP: no PKG_PERFORMANCE.calibrate_review() or equivalent procedure found ***
  *** CRITICAL GAP: no UI control for Calibration module in PERFORMANCE_FORM observed ***
  Calibration columns writable only via direct SQL at present

[STEP 5] Goal management
  PKG_PERFORMANCE.create_goal / update_goal / link_goal_to_review
  PERFORMANCE_GOALS: TARGET_DATE, COMPLETION_PERCENTAGE (0–100)
  GOAL_REVIEWS: pivot table linking goals to review cycles

[STEP 6] Cycle close
  PKG_PERFORMANCE.close_review_cycle(p_cycle_id)
  UPDATE REVIEW_CYCLES SET STATUS='CLOSED', CLOSE_DATE=SYSDATE
  Downstream: used by compensation module for merit increase eligibility check
    BR-HIGH-002: merit increase requires OVERALL_RATING ≥ 3

GAP SUMMARY — Process 4:
  G1: Calibration write path entirely absent
  G2: No 360-degree feedback capability
  G3: Goal completion % is free-entry integer; no validation against milestones
  G4: No forced distribution / bell curve enforcement


=== PROCESS 5: EMPLOYEE TERMINATION ===

Actors: HR Admin
Services: PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_SECURITY
UI: EMPLOYEE_FORM

[STEP 1] Initiate termination (HR Admin, EMPLOYEE_FORM)
  PKG_EMPLOYEE.terminate_employee(p_emp_id, p_termination_date, p_reason)
  Validations:
    TERMINATION_DATE ≥ HIRE_DATE
    EMPLOYMENT_STATUS must be 'ACTIVE' (cannot re-terminate)

[STEP 2] Employee record update
  UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='TERMINATED',
                       TERMINATION_DATE=p_termination_date,
                       TERMINATION_REASON=p_termination_code,
                       UPDATED_DATE=SYSDATE,
                       UPDATED_BY=USER
  ACTIVE_FLAG remains 'Y' — employee record retained for audit
  Soft-delete pattern: record survives; filtered out by 3-part active filter in reports

[STEP 3] Access revocation
  *** CRITICAL GAP: no PKG_SECURITY.revoke_access() or equivalent procedure found ***
  *** CRITICAL GAP: EMPLOYEE_USERS table (if exists) has no DEACTIVATE_DATE column ***
  *** ASSUMPTION: manual DBA action required to remove Oracle Forms user account ***
  *** SEC-011: terminated employees may retain system access until manual intervention ***

[STEP 4] Final pay calculation
  *** DESIGNED BUT UNIMPLEMENTED: no final_pay procedure in PKG_PAYROLL ***
  *** MISSING: PTO payout calculation at termination not found ***
  *** MISSING: COBRA election trigger not found ***
  Workaround: unknown — likely handled outside system

[STEP 5] Benefits termination feed
  ADP benefits feed (UTL_FILE, PAYROLL_EXPORT dir) picks up terminated employee on next
  monthly cycle via EMPLOYMENT_STATUS filter — no immediate off-cycle feed capability

[STEP 6] History preservation
  INSERT EMPLOYEE_HISTORY (CHANGE_TYPE='TERMINATION', OLD_VALUE=previous status)
  Via audit trigger on EMPLOYEES table (PRAGMA AUTONOMOUS_TRANSACTION)

GAP SUMMARY — Process 5:
  G1: Access revocation entirely absent — CRITICAL security gap
  G2: Final pay and PTO payout not implemented
  G3: COBRA enrollment notification absent
  G4: No off-cycle benefits termination feed
  G5: No checklist/workflow for equipment return, exit interview, etc.


=== PROCESS 6: NOTIFICATION DELIVERY ===

Actors: System (automated), HR Admin (manual trigger)
Services: PKG_NOTIFICATION
Infrastructure: UTL_SMTP, NOTIFICATION_QUEUE table, NOTIFICATION_TEMPLATES table

[STEP 1] Event triggers notification insert
  Any PKG_* procedure that generates a notification:
    INSERT NOTIFICATION_QUEUE (RECIPIENT_ID, TEMPLATE_ID, STATUS='PENDING',
                                CREATED_DATE=SYSDATE, PAYLOAD clob)

[STEP 2] Queue processor (DBMS_SCHEDULER — inferred)
  PKG_NOTIFICATION.process_notification_queue()
  SELECT * FROM NOTIFICATION_QUEUE WHERE STATUS='PENDING' ORDER BY CREATED_DATE
  FOR each pending notification:
    Fetch template from NOTIFICATION_TEMPLATES
    Merge PAYLOAD JSON into template placeholders
    DISPATCH based on CHANNEL:
      EMAIL → UTL_SMTP (SMTP_HOST, SMTP_PORT from SYSTEM_CONFIG)
      IN_APP → *** SCHEMA EXISTS (NOTIFICATION_CHANNEL='IN_APP') but no delivery handler ***
      SMS   → *** SCHEMA EXISTS (NOTIFICATION_CHANNEL='SMS') but no delivery handler ***
    ON success: UPDATE STATUS='SENT', SENT_DATE=SYSDATE
    ON failure: UPDATE STATUS='FAILED', ERROR_MESSAGE=SQLERRM
      *** DEFECT: no retry logic; FAILED notifications stay FAILED permanently ***
      *** DEFECT: no dead-letter queue or alerting on accumulated failures ***

[STEP 3] Retry gap
  *** MISSING: no scheduled re-processing of FAILED rows ***
  *** MISSING: no max-retry counter; no exponential backoff ***

GAP SUMMARY — Process 6:
  G1: SMS and IN_APP channels are dead code — schema exists, handler absent
  G2: No retry for failed notifications
  G3: Synchronous SMTP loop does not scale


=== PROCESS 7: BENEFITS FEED TO ADP ===

Actors: System (automated monthly), HR Admin (manual trigger)
Services: PKG_INTEGRATION
Infrastructure: UTL_FILE, HRMS_OUTBOUND directory object, ADP SFTP (external)

[STEP 1] Extract active enrollment data
  PKG_INTEGRATION.generate_benefits_feed(p_feed_date)
  SELECT from BENEFIT_ENROLLMENTS JOIN EMPLOYEES JOIN BENEFIT_PLANS
  Filter: EMPLOYMENT_STATUS='ACTIVE', ENROLLMENT_STATUS='ENROLLED'

[STEP 2] Format fixed-width records
  Each record = 203 characters:
    Pos 1–9   : EMPLOYEE_ID (right-justified, zero-padded)
    Pos 10–49 : LAST_NAME (left-justified, space-padded)
    Pos 50–84 : FIRST_NAME
    Pos 85–94 : SSN (decrypted inline via PKG_SECURITY.decrypt_value at this step)
    Pos 95–104: BIRTH_DATE (YYYYMMDD)
    Pos 105–110: PLAN_CODE
    Pos 111–120: COVERAGE_TIER
    Pos 121–130: EFFECTIVE_DATE (YYYYMMDD)
    Pos 131–203: (reserved / filler spaces)
  *** SEC-004: SSN written in plaintext to flat file during this step ***
  *** SEC-004: file sits in HRMS_OUTBOUND directory until external pickup — no at-rest encryption ***

[STEP 3] Write file
  UTL_FILE.PUT_LINE loop to HRMS_OUTBOUND dir
  Filename: ADP_BENEFITS_YYYYMMDD.txt
  *** DEFECT: no file-level checksum or record count trailer written ***
  *** DEFECT: ADP expects a trailer record with total count; current feed omits it ***

[STEP 4] SFTP handoff
  *** OUTSIDE SYSTEM: SFTP transfer handled by OS-level scheduled script, not PL/SQL ***
  *** MISSING: no confirmation callback; system never knows if ADP received the file ***

GAP SUMMARY — Process 7:
  G1: SSN in plaintext flat file — critical PII exposure
  G2: Missing trailer record — ADP validation may reject feed silently
  G3: No delivery confirmation mechanism
  G4: SFTP logic outside application boundary — no audit trail in HRMS

```

<!-- GAP-FILLED SECTION -->
Looking at the source, `process_queue` has a hard `AND NOTIFICATION_TYPE = 'EMAIL'` filter — IN_APP notifications queue but are never dispatched. I'll add that as G5 to the Process 3 gap summary.

  *** SCHEDULER: JOB inferred from code comments; no CREATE_JOB DDL provided ***

GAP SUMMARY — Process 3:
  G1: No half-day leave support (whole integer days only, no 0.5)
  G2: No FMLA / statutory leave type enforcement
  G3: Carry-forward logic not observed; year-end balance disposition unknown
  G4: Accrual scheduler DDL absent
  G5: [GAP-FILLED] IN_APP notification delivery handler absent — PKG_NOTIFICATION.pks declares "Email, in-app, and SMS notification management" and send_notification accepts p_type='IN_APP', queuing rows in NOTIFICATION_QUEUE; however process_queue contains a hard filter AND NOTIFICATION_TYPE = 'EMAIL', so IN_APP-typed rows accumulate in PENDING status and are never dispatched. No separate dispatch procedure for NOTIFICATION_CHANNEL='IN_APP' was found in the package body. Leave-status notifications sent as IN_APP will silently stall.


=== PROCESS 4: PERFORMANCE REVIEW CYCLE ===

[GAP-FILLED] Source: PKG_PERFORMANCE.pkb / PKG_PERFORMANCE.pks
[GAP-FILLED] Dependencies: PKG_AUDIT, PKG_NOTIFICATION, PKG_EMPLOYEE, PKG_COMMON
[GAP-FILLED] Called by: HRMS_PERFORMANCE form, batch calibration job
[GAP-FILLED] Tables: REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS
[GAP-FILLED] Sequences: SEQ_REVIEW_CYCLE, SEQ_PERF_REVIEW, SEQ_PERF_GOAL

[GAP-FILLED] --- 4.1 CYCLE LIFECYCLE ---
[GAP-FILLED] Step 1 — Create cycle (create_review_cycle):
[GAP-FILLED]   Inputs: cycle_name, cycle_year, start_date, end_date,
[GAP-FILLED]           self_review_due (optional), manager_review_due (optional)
[GAP-FILLED]   Action: allocates SEQ_REVIEW_CYCLE.NEXTVAL; inserts REVIEW_CYCLES row
[GAP-FILLED]           with STATUS = 'DRAFT'; logs INSERT via PKG_AUDIT
[GAP-FILLED]   Returns: cycle_id (NUMBER)

[GAP-FILLED] Step 2 — Open cycle (open_review_cycle):
[GAP-FILLED]   Guard: STATUS must be 'DRAFT'; raises -20401 if not
[GAP-FILLED]   Action: UPDATE STATUS → 'OPEN'; stamps MODIFIED_BY / MODIFIED_DATE

[GAP-FILLED] Step 3 — Bulk-generate individual reviews (generate_reviews_for_cycle):
[GAP-FILLED]   Action: iterates all EMPLOYEES where EMPLOYMENT_STATUS = 'ACTIVE'
[GAP-FILLED]           AND MANAGER_EMP_ID IS NOT NULL; calls create_review() for each;
[GAP-FILLED]           skips duplicates silently (DUP_VAL_ON_INDEX caught);
[GAP-FILLED]           issues COMMIT and DBMS_OUTPUT count on completion

[GAP-FILLED] Step 4 — Close cycle (close_review_cycle):
[GAP-FILLED]   Action: UPDATE STATUS → 'CLOSED' unconditionally (no guard on current status)

[GAP-FILLED] Cycle status FSM: DRAFT → OPEN → CLOSED

[GAP-FILLED] --- 4.2 INDIVIDUAL REVIEW WORKFLOW ---
[GAP-FILLED] Step A — Create review (create_review):
[GAP-FILLED]   Inputs: cycle_id, emp_id, reviewer_emp_id
[GAP-FILLED]   Action: inserts PERFORMANCE_REVIEWS row; REVIEW_TYPE = 'ANNUAL',
[GAP-FILLED]           STATUS = 'NOT_STARTED'
[GAP-FILLED]   Side-effect: EMAIL notification to employee — "Performance Review Initiated"

[GAP-FILLED] Step B — Employee self-assessment (submit_self_assessment):
[GAP-FILLED]   Guard: STATUS must be 'NOT_STARTED' or 'SELF_REVIEW'; raises -20402 otherwise
[GAP-FILLED]   Action: writes SELF_ASSESSMENT (CLOB); STATUS → 'MANAGER_REVIEW'
[GAP-FILLED]   Side-effect: EMAIL notification to REVIEWER_EMP_ID —
[GAP-FILLED]               "Self-Assessment Submitted - Ready for Manager Review"

[GAP-FILLED] Step C — Manager review (submit_manager_review):
[GAP-FILLED]   Inputs: review_id, overall_rating (1.0–5.0), manager_assessment,
[GAP-FILLED]           strengths, improvement_areas, development_plan (all CLOB, optional)
[GAP-FILLED]   Guard: rating outside [1.0, 5.0] raises -20403
[GAP-FILLED]   Rating label derivation (stored as RATING_LABEL):
[GAP-FILLED]     >= 4.5  → 'Exceptional'
[GAP-FILLED]     >= 3.5  → 'Exceeds Expectations'
[GAP-FILLED]     >= 2.5  → 'Meets Expectations'
[GAP-FILLED]     >= 1.5  → 'Needs Improvement'
[GAP-FILLED]     < 1.5   → 'Unsatisfactory'
[GAP-FILLED]   Action: updates rating fields; STATUS → 'COMPLETED'
[GAP-FILLED]   Side-effect: EMAIL notification to employee — "Performance Review Completed"

[GAP-FILLED] Step D — Employee acknowledgement (acknowledge_review):
[GAP-FILLED]   Guard: STATUS must be 'COMPLETED'
[GAP-FILLED]   Action: writes optional EMPLOYEE_COMMENTS (CLOB);
[GAP-FILLED]           stamps EMPLOYEE_ACK_DATE = SYSDATE; STATUS → 'ACKNOWLEDGED'

[GAP-FILLED] Review status FSM:
[GAP-FILLED]   NOT_STARTED → SELF_REVIEW → MANAGER_REVIEW → COMPLETED → ACKNOWLEDGED

[GAP-FILLED] --- 4.3 GOAL TRACKING ---
[GAP-FILLED] Add goal (add_goal):
[GAP-FILLED]   Inputs: review_id, emp_id, goal_title, goal_description (CLOB),
[GAP-FILLED]           goal_category (default 'BUSINESS'), weight_pct (default 0),
[GAP-FILLED]           target_date
[GAP-FILLED]   Action: inserts PERFORMANCE_GOALS; STATUS = 'NOT_STARTED', PROGRESS_PCT = 0
[GAP-FILLED]   Returns: goal_id (NUMBER)

[GAP-FILLED] Update progress (update_goal_progress):
[GAP-FILLED]   Inputs: goal_id, progress_pct, status (optional), comments (CLOB optional)
[GAP-FILLED]   Auto-status derivation when p_status is NULL:
[GAP-FILLED]     progress_pct >= 100 → 'COMPLETED'
[GAP-FILLED]     progress_pct >   0  → 'IN_PROGRESS'
[GAP-FILLED]     else                → STATUS unchanged
[GAP-FILLED]   Note: explicit p_status overrides auto-derivation via NVL

[GAP-FILLED] --- 4.4 REPORTING / QUERIES ---
[GAP-FILLED] get_team_reviews (REF CURSOR out):
[GAP-FILLED]   Filters by REVIEWER_EMP_ID = p_manager_id AND CYCLE_ID = p_cycle_id
[GAP-FILLED]   Returns: REVIEW_ID, EMP_ID, EMPLOYEE_NAME (first+last), JOB_TITLE,
[GAP-FILLED]            DEPT_NAME, STATUS, OVERALL_RATING, RATING_LABEL
[GAP-FILLED]   Ordered: LAST_NAME ASC

[GAP-FILLED] get_rating_distribution (SYS_REFCURSOR):
[GAP-FILLED]   Filters by CYCLE_ID; optional DEPT_ID filter
[GAP-FILLED]   Returns: RATING_LABEL, COUNT, PERCENTAGE (window function, 1 decimal)
[GAP-FILLED]   Only includes reviews where OVERALL_RATING IS NOT NULL
[GAP-FILLED]   Ordered: MIN(OVERALL_RATING) DESC (highest rating band first)

[GAP-FILLED] --- 4.5 GAP SUMMARY — Process 4 ---
[GAP-FILLED] G1: No mid-cycle status (e.g. 'ON_HOLD'); cycle can only be DRAFT/OPEN/CLOSED
[GAP-FILLED] G2: close_review_cycle has no guard — can close a DRAFT cycle directly,
[GAP-FILLED]     bypassing the OPEN step
[GAP-FILLED] G3: No skip-level or peer review type; REVIEW_TYPE hardcoded to 'ANNUAL'
[GAP-FILLED] G4: Calibration logic referenced in package header comment but no
[GAP-FILLED]     calibration procedure present in this package
[GAP-FILLED] G5: No rating change audit trail after submit_manager_review completes
[GAP-FILLED] G6: generate_reviews_for_cycle issues a bare COMMIT — may interfere with
[GAP-FILLED]     caller transaction boundaries

<!-- GAP-FILLED SECTION -->
*** SCHEDULER: JOB inferred from code comments; no CREATE_JOB DDL provided ***

GAP SUMMARY — Process 3:
  G1: No half-day leave support (whole integer days only, no 0.5)
  G2: No FMLA / statutory leave type enforcement
  G3: Carry-forward logic not observed; year-end balance disposition unknown
  G4: Accrual scheduler DDL absent
  G5: [GAP-FILLED] SMS notification delivery handler absent — PKG_NOTIFICATION.pks header declares "Email, in-app, and SMS notification management" and send_notification accepts p_type='SMS', queuing records into NOTIFICATION_QUEUE with NOTIFICATION_TYPE='SMS'; however process_queue hard-codes AND NOTIFICATION_TYPE = 'EMAIL' in its cursor, meaning SMS-typed records are never selected for dispatch. No UTL_HTTP call, external SMS gateway invocation, or alternative SMS-dispatch procedure exists anywhere in PKG_NOTIFICATION.pkb. Result: any SMS notification queued (e.g. leave approval alerts) remains permanently in STATUS='PENDING'. This gap affects all calling packages (PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE).


=== PROCESS 4: PERFORMANCE REVIEW CYCLE ===

<!-- GAP-FILLED SECTION -->
Looking through the source for carry-forward specifics: the `submit_leave_request` procedure checks `ACCRUAL_FLAG = 'Y'` before any balance operation, which tells us non-accrual types have no balance rows at all and are implicitly excluded. No cap or expiry logic appears anywhere in the provided source, so those two sub-items remain open.

Here is the updated snippet:

---

  The source content (PKG_PAYROLL.pkb) confirms that `final_pay` is absent from the package body — but it does not provide an implementation to fill the gap with. The snippet is the Process 3 (Leave Management) GAP SUMMARY; `final_pay` is a Payroll concern with no entry in this section to annotate. Per the instructions, the snippet is returned unchanged:

---

  Looking at the source content, `PKG_PAYROLL.calculate_payroll` only loops over `EMPLOYMENT_STATUS = 'ACTIVE'` employees — no termination payout logic is present. I'll add that as a confirmed gap entry.

  Looking at the source content retrieved and the document snippet, the snippet covers **Process 3 leave management gaps** (G1, G2, G3) — there is no SEC-011 placeholder in this extract. The files that would fill SEC-011 (`PKG_TERMINATION.pkb`, `trg_employee_status_change.trg`, `user_provisioning.sql`) were all **not found**, and `PKG_SECURITY.pkb` does not contain a termination-triggered disabling mechanism.

Per the instructions: returning the snippet unchanged.

---

  Looking at the source code, I need to determine what `PKG_LEAVE.pkb` reveals (or doesn't reveal) about FMLA enforcement, then annotate G2 accordingly.

The code confirms the gap: `submit_leave_request` only applies a generic `MIN_TENURE_DAYS` check (not FMLA's 12-month / 1,250-hour eligibility rule), has no duration-limit guard (FMLA's 12-week cap), and no certification-tracking columns or procedures appear anywhere in the package.

Updated snippet:

```
  *** SCHEDULER: JOB inferred from code comments; no CREATE_JOB DDL provided ***

GAP SUMMARY — Process 3:
  G1: No half-day leave support (whole integer days only, no 0.5)
  G2: No FMLA / statutory leave type enforcement
      [GAP-FILLED] PKG_LEAVE.submit_leave_request was examined in full.
      The only statutory-adjacent check present is a generic MIN_TENURE_DAYS
      gate (LEAVE_TYPES.MIN_TENURE_DAYS compared against SYSDATE - HIRE_DATE).
      This is NOT equivalent to FMLA eligibility, which requires 12 months of
      employment AND 1,250 hours worked in the preceding 12-month period AND
      a 50-employee threshold at the worksite — none of those conditions are
      evaluated. No duration-limit guard (FMLA 12-week annual cap) exists; the
      package imposes no ceiling on days requested for any leave type. No
      medical-certification tracking columns or procedures appear in the package
      body. LEAVE_TYPES is queried only for ACTIVE_FLAG, MIN_TENURE_DAYS,
      ACCRUAL_FLAG, and REQUIRES_APPROVAL — no FMLA_FLAG or STATUTORY_TYPE
      discriminator is read. Conclusion: FMLA and other statutory leave types
      are at most a data category in LEAVE_TYPES; all eligibility, duration,
      and certification enforcement must be handled outside this system (e.g.,
      manual HR process or a third-party absence-management tool).
  G3: Carry-forward logic not observed; year-end balance disposition unknown
      [GAP-FILLED] LEAVE_BALANCES.OPENING_BALANCE exists and is included in the
      available-balance formula inside get_leave_balance:
        available = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING
      This confirms the schema is designed to carry unused balance forward via
      OPENING_BALANCE on a per-employee/per-leave-type/per-calendar-year row.
```
  [GAP-FILLED]
  G4: No PTO payout calculation at termination — PKG_PAYROLL.calculate_payroll
      iterates exclusively over employees WHERE EMPLOYMENT_STATUS = 'ACTIVE';
      terminating employees are excluded from every regular payroll run. No
      separate procedure, payroll element, or formula was found in
      PKG_PAYROLL.pkb that reads a departing employee's accrued-but-unused PTO
      balance and converts it to a monetary payout for inclusion in final pay.
      The gap is confirmed: remaining PTO owed at separation is not computed
      anywhere in the retrieved payroll package.

      [GAP-FILLED] Excluded leave types: submit_leave_request only performs a
      balance check when LEAVE_TYPES.ACCRUAL_FLAG = 'Y'. Leave types with
      ACCRUAL_FLAG = 'N' never receive a LEAVE_BALANCES row, so they have no
      balance to carry forward and are implicitly excluded from carry-forward
      processing. No explicit exclusion list or flag named "carry_forward" was
      found; exclusion is a side-effect of the non-accrual classification.

      [STILL UNRESOLVED] Maximum carry-forward cap: no cap constant, column
      (e.g. MAX_CARRY_FORWARD on LEAVE_TYPES), or enforcement logic was found
      in the provided source. The year-end job that writes OPENING_BALANCE for
      the next year was not supplied; whether it applies a cap at that point is
      unknown.

      [STILL UNRESOLVED] Expiry date for carried balances: no expiry column,
      date comparison, or purge logic for carried OPENING_BALANCE was found in
      PKG_LEAVE. Whether carried days expire mid-year (e.g., "use by March 31")
      cannot be determined from the available source.

<!-- GAP-FILLED SECTION -->
The source content (PKG_PAYROLL.pkb) covers salary management, pay period generation, payroll run creation, and per-employee pay calculation — but contains no procedure for computing or recording accrued PTO balance payout at termination. Per the instructions, the snippet is returned unchanged.

---

  Now I have the full picture. Here is the updated snippet with the gap filled:

---

  in the package body. The rollover job is a confirmed implementation gap.

GAP SUMMARY — Process 3:
  G1: No half-day leave support (whole integer days only, no 0.5)
  G2: No FMLA / statutory leave type enforcement
      [GAP-FILLED] Confirmed by inspection of PKG_LEAVE.submit_leave_request and
      the LEAVE_TYPES row-type fields referenced therein. The only leave-type
      attributes the package acts on are:
        - MIN_TENURE_DAYS  (tenure gate)
        - ACCRUAL_FLAG     (balance check toggle)
        - REQUIRES_APPROVAL (approval routing)
      None of these columns encode a statutory / FMLA designation. The package
      performs no FMLA-specific enforcement at any point:
        • No 12-week rolling-year entitlement cap
        • No qualifying-reason or medical-certification gate
        • No employer-coverage threshold check (50+ employees)
        • No intermittent-leave hour tracking
        • No FMLA designation notice or paperwork trigger
      submit_leave_request treats every leave type identically — a leave row
      whose LEAVE_TYPE_NAME happens to be "FMLA" would receive the same
      MIN_TENURE / balance / approval logic as any discretionary leave type,
      with none of the federal protections or limits applied in code. The gap
      is confirmed as a pure application-logic omission; there is no compensating
      trigger or constraint visible in the recovered source.
  G3: Carry-forward logic not observed; year-end balance disposition unknown
      [GAP-FILLED] LEAVE_BALANCES.OPENING_BALANCE exists and is included in the
      available-balance formula inside get_leave_balance:
        available = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING
      This confirms the schema is designed to carry unused balance forward via
      OPENING_BALANCE on a per-employee/per-leave-type/per-calendar-year row.

[GAP-FILLED] SEC-011: No automated Oracle Forms account deactivation on termination — manual DBA action required, leaving a window where terminated employees retain system access.

      Source evidence from PKG_SECURITY.pkb:
      - PKG_TERMINATION.pkb was NOT FOUND in the codebase (deep scan confirmed
        absent) — no dedicated termination-driven access-revocation package exists.
      - PKG_SECURITY.authenticate filters on EMPLOYMENT_STATUS = 'ACTIVE':
          SELECT EMP_ID INTO v_emp_id
          FROM EMPLOYEES
          WHERE UPPER(EMAIL) = UPPER(p_username)
          AND EMPLOYMENT_STATUS = 'ACTIVE';
        This provides a partial mitigation: once EMPLOYMENT_STATUS is flipped to
        'TERMINATED' (by PKG_EMPLOYEE.terminate_employee), new login attempts will
        fail with "Invalid username or password". However:
        (a) Any existing USER_SESSIONS rows with SESSION_STATUS = 'ACTIVE' at the
            moment of termination are NOT invalidated by the termination procedure —
            no session-kill step was found in the codebase. A terminated employee
            with an open session retains access until the 30-minute idle timeout
            (c_session_timeout_min = 30) naturally expires the session.
        (b) No PKG_SECURITY.revoke_access() or equivalent procedure was found.
        (c) No trigger on EMPLOYEES.EMPLOYMENT_STATUS change to call logout() or
            invalidate sessions was found.
        (d) Oracle Forms database user account management (CREATE/DROP USER,
            GRANT/REVOKE) is entirely absent from the PL/SQL codebase — confirming
            that Oracle DB account deactivation remains a manual DBA action.
      Risk window: up to 30 minutes of continued access via an active session, plus
      indefinite access via the Oracle DB-level account until a DBA acts manually.
