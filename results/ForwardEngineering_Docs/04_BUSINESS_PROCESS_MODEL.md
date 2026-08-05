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
  *** SCHEDULER: JOB inferred from code comments; no CREATE_JOB DDL provided ***

GAP SUMMARY — Process 3:
  G1: No half-day leave support (whole integer days only, no 0.5)
  G2: No FMLA / statutory leave type enforcement
  G3: Carry-forward logic not observed; year-end balance disposition unknown
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