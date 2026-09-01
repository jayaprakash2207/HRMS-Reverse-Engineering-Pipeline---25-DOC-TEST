=== CHUNK METADATA ===
Chunk: 11            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-body
Expected files (2):
  1. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb (14659 chars written)
  2. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pkb (10984 chars written)
Total source content: 29803 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: Performance review lifecycle management — review cycles, self/manager reviews, goals, and reporting cursors

**STRUCTURES:**
  None — no package-level constants, types, or cursors are declared in this body; the `t_review_cursor` type used as an OUT parameter type in `get_team_reviews` is presumably declared in the package spec (PKG_PERFORMANCE.pks), not here.

**METHODS:**
  **FUNCTION create_review_cycle(p_cycle_name VARCHAR2, p_cycle_year NUMBER, p_start_date DATE, p_end_date DATE, p_self_review_due DATE DEFAULT NULL, p_manager_review_due DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L6-31]
  - What it does: Generates a new ID from SEQ_REVIEW_CYCLE.NEXTVAL [L17], inserts a REVIEW_CYCLES row with STATUS='DRAFT' [L19-27], logs the insert via PKG_AUDIT.log_action [L29], and returns the new cycle ID.
  - Business rules: Every new review cycle starts in 'DRAFT' status.
  - Numbers & thresholds: None beyond the fixed literal 'DRAFT' status.
  - Security & error handling: None — no validation of inputs; p_user defaults to session USER.
  - Data in/out: Inputs — p_cycle_name, p_cycle_year, p_start_date, p_end_date (required); p_self_review_due, p_manager_review_due, p_user (optional). Output — inserts REVIEW_CYCLES row (CYCLE_ID from SEQ_REVIEW_CYCLE.NEXTVAL); writes an audit log entry; returns v_cycle_id.

  **PROCEDURE open_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L33-51]
  - What it does: Updates REVIEW_CYCLES to STATUS='OPEN' (plus MODIFIED_BY/MODIFIED_DATE) where CYCLE_ID matches and current STATUS='DRAFT' [L39-44]; if no row matched, raises an error [L47-50].
  - Business rules: A review cycle can only transition to OPEN from DRAFT status.
  - Numbers & thresholds: -20401 (application error code for invalid state transition).
  - Security & error handling: RAISE_APPLICATION_ERROR(-20401, 'Cannot open cycle - must be in DRAFT status') when SQL%ROWCOUNT = 0.
  - Data in/out: Inputs — p_cycle_id, p_user. Output — updates REVIEW_CYCLES (STATUS, MODIFIED_BY, MODIFIED_DATE).

  **PROCEDURE close_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L53-63]
  - What it does: Updates REVIEW_CYCLES SET STATUS='CLOSED' (plus MODIFIED_BY/MODIFIED_DATE) where CYCLE_ID matches, with no prior-status restriction.
  - Business rules: None — unlike open_review_cycle, no current-status check is enforced before closing.
  - Numbers & thresholds: None.
  - Security & error handling: None — no ROWCOUNT check, so calling with a non-existent CYCLE_ID silently updates zero rows without error.
  - Data in/out: Inputs — p_cycle_id, p_user. Output — updates REVIEW_CYCLES (STATUS, MODIFIED_BY, MODIFIED_DATE).

  **FUNCTION create_review(p_cycle_id NUMBER, p_emp_id NUMBER, p_reviewer_emp_id NUMBER, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L65-96]
  - What it does: Generates a new ID from SEQ_PERF_REVIEW.NEXTVAL [L73], inserts a PERFORMANCE_REVIEWS row with REVIEW_TYPE='ANNUAL', STATUS='NOT_STARTED' [L75-83], sends an EMAIL notification to the employee announcing the review [L86-93], and returns the new review ID.
  - Business rules: Every new review is created as type 'ANNUAL' in status 'NOT_STARTED'.
  - Numbers & thresholds: None beyond the fixed literals 'ANNUAL' and 'NOT_STARTED'.
  - Security & error handling: None — no validation of p_cycle_id/p_emp_id/p_reviewer_emp_id (relies on FK constraints, if any, at the DB level).
  - Data in/out: Inputs — p_cycle_id, p_emp_id, p_reviewer_emp_id, p_user. Output — inserts PERFORMANCE_REVIEWS row (REVIEW_ID from SEQ_PERF_REVIEW.NEXTVAL); sends a notification; returns v_review_id.

  **PROCEDURE submit_self_assessment(p_review_id NUMBER, p_self_assessment CLOB, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L98-136]
  - What it does: Updates PERFORMANCE_REVIEWS SET SELF_ASSESSMENT, STATUS='MANAGER_REVIEW' where REVIEW_ID matches and current STATUS is 'NOT_STARTED' or 'SELF_REVIEW' [L105-111]; if no row matched, raises an error [L114-117]; otherwise looks up the review's REVIEWER_EMP_ID [L123-125] and sends an EMAIL notification to the manager [L127-134].
  - Business rules: A self-assessment can only be submitted while the review is in 'NOT_STARTED' or 'SELF_REVIEW' status; submission always advances the review to 'MANAGER_REVIEW'.
  - Numbers & thresholds: -20402 (application error code for missing/invalid-status review).
  - Security & error handling: RAISE_APPLICATION_ERROR(-20402, 'Review not found or not in correct status') when SQL%ROWCOUNT = 0.
  - Data in/out: Inputs — p_review_id, p_self_assessment, p_user. Output — updates PERFORMANCE_REVIEWS (SELF_ASSESSMENT, STATUS, MODIFIED_BY, MODIFIED_DATE); reads REVIEWER_EMP_ID; sends a notification.

  **PROCEDURE submit_manager_review(p_review_id NUMBER, p_overall_rating NUMBER, p_manager_assessment CLOB, p_strengths CLOB DEFAULT NULL, p_improvement_areas CLOB DEFAULT NULL, p_development_plan CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L138-194]
  - What it does: Validates p_overall_rating is within [1.0, 5.0] [L149-152]; updates PERFORMANCE_REVIEWS with OVERALL_RATING, a derived RATING_LABEL, MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN, and STATUS='COMPLETED' where REVIEW_ID matches, with no current-status restriction [L154-175]; looks up the review's EMP_ID [L181-183] and sends an EMAIL notification to the employee [L185-192].
  - Business rules: Overall rating must be between 1.0 and 5.0 inclusive. RATING_LABEL banding: score >= 4.5 → 'Exceptional'; >= 3.5 (and < 4.5) → 'Exceeds Expectations'; >= 2.5 (and < 3.5) → 'Meets Expectations'; >= 1.5 (and < 2.5) → 'Needs Improvement'; else → 'Unsatisfactory'. The update carries no status-transition guard, so a manager review can be submitted regardless of the review's current STATUS.
  - Numbers & thresholds: -20403 (application error code for out-of-range rating). Valid rating range: 1.0 to 5.0. Rating-label thresholds: 4.5, 3.5, 2.5, 1.5.
  - Security & error handling: RAISE_APPLICATION_ERROR(-20403, 'Rating must be between 1.0 and 5.0') when p_overall_rating < 1.0 OR > 5.0. No ROWCOUNT check after the UPDATE.
  - Data in/out: Inputs — p_review_id, p_overall_rating, p_manager_assessment (required); p_strengths, p_improvement_areas, p_development_plan, p_user (optional). Output — updates PERFORMANCE_REVIEWS (OVERALL_RATING, RATING_LABEL, MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN, STATUS, MODIFIED_BY, MODIFIED_DATE); reads EMP_ID; sends a notification.

  **PROCEDURE acknowledge_review(p_review_id NUMBER, p_emp_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L196-211]
  - What it does: Updates PERFORMANCE_REVIEWS SET EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE=SYSDATE, STATUS='ACKNOWLEDGED' where REVIEW_ID matches and current STATUS='COMPLETED'.
  - Business rules: An employee can only acknowledge a review that is currently in 'COMPLETED' status; reviews in any other status are silently unaffected (no error raised).
  - Numbers & thresholds: None.
  - Security & error handling: None — no ROWCOUNT check, so acknowledging a review not in 'COMPLETED' status fails silently.
  - Data in/out: Inputs — p_review_id, p_emp_comments, p_user. Output — updates PERFORMANCE_REVIEWS (EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE, STATUS, MODIFIED_BY, MODIFIED_DATE).

  **FUNCTION add_goal(p_review_id NUMBER, p_emp_id NUMBER, p_goal_title VARCHAR2, p_goal_description CLOB DEFAULT NULL, p_goal_category VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct NUMBER DEFAULT 0, p_target_date DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L213-240]
  - What it does: Generates a new ID from SEQ_PERF_GOAL.NEXTVAL [L225], inserts a PERFORMANCE_GOALS row with STATUS='NOT_STARTED' and PROGRESS_PCT=0 [L227-237], and returns the new goal ID.
  - Business rules: Every new goal starts as STATUS='NOT_STARTED' with PROGRESS_PCT=0. Default goal category is 'BUSINESS' if not supplied; default weight is 0%.
  - Numbers & thresholds: Default p_weight_pct = 0. Initial PROGRESS_PCT = 0. Default p_goal_category = 'BUSINESS'.
  - Security & error handling: None — no validation of p_weight_pct (e.g. no check that weights across a review's goals sum to 100).
  - Data in/out: Inputs — p_review_id, p_emp_id, p_goal_title (required); p_goal_description, p_goal_category, p_weight_pct, p_target_date, p_user (optional). Output — inserts PERFORMANCE_GOALS row (GOAL_ID from SEQ_PERF_GOAL.NEXTVAL); returns v_goal_id.

  **PROCEDURE update_goal_progress(p_goal_id NUMBER, p_progress_pct NUMBER, p_status VARCHAR2 DEFAULT NULL, p_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L242-265]
  - What it does: Updates PERFORMANCE_GOALS SET PROGRESS_PCT; if p_status is not supplied, derives STATUS from p_progress_pct (100+ → 'COMPLETED', >0 → 'IN_PROGRESS', else unchanged); preserves existing COMMENTS if p_comments is NULL; updates MODIFIED_BY/MODIFIED_DATE.
  - Business rules: An explicit p_status always overrides the derived status. Progress >= 100 auto-completes the goal; any progress > 0 (and < 100) marks it in progress; 0 or negative leaves STATUS unchanged. Omitting p_comments preserves the existing comment rather than clearing it.
  - Numbers & thresholds: 100 (progress threshold for auto-'COMPLETED'); 0 (progress threshold for auto-'IN_PROGRESS').
  - Security & error handling: None — no validation that p_progress_pct is within 0-100; no ROWCOUNT check.
  - Data in/out: Inputs — p_goal_id, p_progress_pct (required); p_status, p_comments, p_user (optional). Output — updates PERFORMANCE_GOALS (PROGRESS_PCT, STATUS, COMMENTS, MODIFIED_BY, MODIFIED_DATE).

  **PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id NUMBER, p_cycle_id NUMBER)** [SOURCE: L267-286]
  - What it does: Opens p_cursor over PERFORMANCE_REVIEWS joined to EMPLOYEES, JOB_TITLES, and DEPARTMENTS, returning review ID, employee name/title/department, status, rating, and rating label for one manager's reviews in one cycle, ordered by last name.
  - Business rules: Only reviews where the given employee is the designated REVIEWER_EMP_ID, scoped to a single CYCLE_ID, are returned.
  - Numbers & thresholds: None.
  - Security & error handling: None — no existence check on p_manager_id/p_cycle_id; an unmatched combination simply yields an empty cursor.
  - Data in/out: Inputs — p_manager_id, p_cycle_id. Output — p_cursor OUT REF CURSOR (t_review_cursor) opened over PERFORMANCE_REVIEWS/EMPLOYEES/JOB_TITLES/DEPARTMENTS.

  **FUNCTION get_rating_distribution(p_cycle_id NUMBER, p_dept_id NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR** [SOURCE: L288-307]
  - What it does: Opens and returns a SYS_REFCURSOR selecting RATING_LABEL, COUNT(*), and each label's percentage of the cycle's rated reviews (optionally filtered to one department), ordered by the minimum rating in each label group, descending.
  - Business rules: Only reviews with a non-NULL OVERALL_RATING (i.e. completed reviews) are included; department filter is optional (NULL = all departments).
  - Numbers & thresholds: PERCENTAGE = ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) — percentage rounded to 1 decimal place.
  - Security & error handling: None.
  - Data in/out: Inputs — p_cycle_id (required), p_dept_id (optional). Output — returns an opened SYS_REFCURSOR over PERFORMANCE_REVIEWS/EMPLOYEES.

  **PROCEDURE generate_reviews_for_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L309-339]
  - What it does: Loops over all EMPLOYEES with EMPLOYMENT_STATUS='ACTIVE' and a non-NULL MANAGER_EMP_ID; for each, calls create_review (self-call) [L327-328], incrementing a counter on success; catches DUP_VAL_ON_INDEX per employee and skips silently (review already exists) [L331-334]; commits once after the loop [L337] and prints a summary line via DBMS_OUTPUT [L338].
  - Business rules: Only ACTIVE employees with an assigned manager are eligible for bulk review generation. A duplicate review for an employee already having one in this cycle is silently skipped rather than erroring the whole batch.
  - Numbers & thresholds: None.
  - Security & error handling: Per-employee EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL — swallows the duplicate-key error without logging; no other exception handling, so any other error aborts the entire loop without committing prior inserts (COMMIT is only reached after the loop finishes successfully).
  - Data in/out: Inputs — p_cycle_id, p_user. Output — inserts PERFORMANCE_REVIEWS rows (via create_review) plus their notification side effects; COMMIT; DBMS_OUTPUT summary line.

**DEPENDENCIES:**
  Data touched:
  - Reads: PERFORMANCE_REVIEWS — REVIEWER_EMP_ID lookup (submit_self_assessment), EMP_ID lookup (submit_manager_review), full rows for team/rating-distribution queries (get_team_reviews, get_rating_distribution)
  - Reads: EMPLOYEES — active employees with a manager (generate_reviews_for_cycle); joined for name/department (get_team_reviews, get_rating_distribution)
  - Reads: JOB_TITLES — joined for job title (get_team_reviews)
  - Reads: DEPARTMENTS — joined for department name (get_team_reviews)
  - Writes: REVIEW_CYCLES — insert (create_review_cycle); update status (open_review_cycle, close_review_cycle)
  - Writes: PERFORMANCE_REVIEWS — insert (create_review); update (submit_self_assessment, submit_manager_review, acknowledge_review)
  - Writes: PERFORMANCE_GOALS — insert (add_goal); update (update_goal_progress)

  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L29
  CALLS: PKG_NOTIFICATION.send_notification | EVIDENCE: OBSERVED | SOURCE: L86
  CALLS: PKG_NOTIFICATION.send_notification | EVIDENCE: OBSERVED | SOURCE: L127
  CALLS: PKG_NOTIFICATION.send_notification | EVIDENCE: OBSERVED | SOURCE: L185
  CALLS: create_review | EVIDENCE: OBSERVED | SOURCE: L327

  Config/env: None
  External integrations: None (PKG_AUDIT and PKG_NOTIFICATION are internal packages, invoked directly).

**GAPS:**
  t_review_cursor type used as OUT parameter type in get_team_reviews is not declared in this file — presumably in PKG_PERFORMANCE.pks — EXTERNAL/UNKNOWN.
  PKG_AUDIT.log_action and PKG_NOTIFICATION.send_notification implementations are external to this file — EXTERNAL.
  close_review_cycle enforces no prior-status check (unlike open_review_cycle) — UNRESOLVED whether this asymmetry is intentional.
  submit_manager_review updates the review regardless of its current STATUS (no WHERE STATUS = ... guard) — UNRESOLVED whether intentional or a latent gap versus the other status-gated procedures in this package.

*[pipeline status — type: plsql-body · pass: original · attempt: 1 · coverage: 100% (numbers 12/12 · procedures 12/12 · units 12/12 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: HR/payroll reporting — headcount, compensation, turnover, new hires, leave utilization, payroll summary, and EEO compliance report cursors

**STRUCTURES:**
  None — no package-level constants, types, or cursors are declared in this body; the `t_report_cursor` type used as an OUT parameter type throughout is presumably declared in the package spec (PKG_REPORTING.pks), not here.

**METHODS:**
  **PROCEDURE headcount_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE, p_dept_id NUMBER DEFAULT NULL, p_location VARCHAR2 DEFAULT NULL)** [SOURCE: L6-40]
  - What it does: Opens p_cursor over EMPLOYEES joined to DEPARTMENTS and (left-joined) LOCATIONS, grouped by department/location, returning per-group headcount, full/part-time/contract sub-counts, male/female sub-counts, and average tenure in years as of a given date, optionally filtered by department and/or location.
  - Business rules: Only ACTIVE employees hired on or before p_as_of_date and not yet terminated (TERMINATION_DATE NULL or in the future relative to p_as_of_date) are counted. Employment type is split into three mutually exclusive buckets: FULL_TIME, PART_TIME, CONTRACT. Gender is split into 'M' and 'F' counts only — any other/NULL gender code is excluded from both.
  - Numbers & thresholds: AVG_TENURE_YEARS = ROUND(AVG(MONTHS_BETWEEN(p_as_of_date, HIRE_DATE) / 12), 1) — divide by 12 to convert months to years, rounded to 1 decimal place.
  - Security & error handling: None.
  - Data in/out: Inputs — p_as_of_date (default SYSDATE), p_dept_id, p_location (both optional filters). Output — p_cursor OUT REF CURSOR opened over EMPLOYEES/DEPARTMENTS/LOCATIONS.

  **PROCEDURE compensation_summary(p_cursor OUT t_report_cursor, p_dept_id NUMBER DEFAULT NULL, p_grade_id NUMBER DEFAULT NULL)** [SOURCE: L42-72]
  - What it does: Opens p_cursor over EMPLOYEES joined to DEPARTMENTS, JOB_TITLES, JOB_GRADES, and SALARY_RECORDS (active salary only), grouped by department/grade/job title, returning employee count, grade min/max, actual min/max/average/median salary, and a compa-ratio.
  - Business rules: Only the currently active salary record (SALARY_RECORDS.ACTIVE_FLAG='Y') is used; only ACTIVE employees are included; department and grade filters are optional.
  - Numbers & thresholds: COMPA_RATIO = ROUND(AVG(BASE_SALARY / ((MIN_SALARY + MAX_SALARY) / 2)) * 100, 1) — grade midpoint is (MIN_SALARY + MAX_SALARY) / 2, ratio expressed as a percentage rounded to 1 decimal. AVG_SALARY and MEDIAN_SALARY rounded to 2 decimals.
  - Security & error handling: None.
  - Data in/out: Inputs — p_dept_id, p_grade_id (both optional filters). Output — p_cursor OUT REF CURSOR opened over EMPLOYEES/DEPARTMENTS/JOB_TITLES/JOB_GRADES/SALARY_RECORDS.

  **PROCEDURE turnover_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)** [SOURCE: L74-111]
  - What it does: Opens p_cursor over EMPLOYEES joined to DEPARTMENTS, grouped by department, returning termination count within the window, current headcount, turnover percentage, voluntary/involuntary termination counts, and average tenure at exit; departments with no employee ever hired by the period end are suppressed via HAVING.
  - Business rules: A termination counts only if TERMINATION_DATE falls between p_start_date and p_end_date inclusive. CURRENT_HC reflects live EMPLOYMENT_STATUS='ACTIVE' at query time, not a historical snapshot. Voluntary = TERMINATION_REASON='VOLUNTARY'; involuntary = any other TERMINATION_REASON value. Departments with zero employees hired on/before p_end_date are excluded entirely (HAVING clause).
  - Numbers & thresholds: TURNOVER_PCT = ROUND(terminations * 100.0 / NULLIF(count hired by end date, 0), 1) — percentage rounded to 1 decimal, NULLIF guards divide-by-zero. AVG_TENURE_AT_EXIT = ROUND(AVG(MONTHS_BETWEEN(TERMINATION_DATE, HIRE_DATE) / 12), 1) — divide by 12 to convert months to years.
  - Security & error handling: NULLIF(...,0) prevents division-by-zero errors when a department has no eligible hire history; no other error handling.
  - Data in/out: Inputs — p_start_date, p_end_date (required); p_dept_id (optional filter). Output — p_cursor OUT REF CURSOR opened over EMPLOYEES/DEPARTMENTS.

  **PROCEDURE new_hires_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)** [SOURCE: L113-138]
  - What it does: Opens p_cursor over EMPLOYEES joined to DEPARTMENTS, JOB_TITLES, (left-joined) LOCATIONS, a self-join to EMPLOYEES for the manager's name, and (left-joined) SALARY_RECORDS (active salary only), returning new-hire details for employees hired within the given window, ordered most-recent-first.
  - Business rules: Scoped to employees whose HIRE_DATE falls within [p_start_date, p_end_date]. A new hire without an active salary record still appears, with a NULL BASE_SALARY (LEFT JOIN).
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Inputs — p_start_date, p_end_date (required); p_dept_id (optional filter). Output — p_cursor OUT REF CURSOR opened over EMPLOYEES/DEPARTMENTS/JOB_TITLES/LOCATIONS/SALARY_RECORDS.

  **PROCEDURE leave_utilization_report(p_cursor OUT t_report_cursor, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE), p_dept_id NUMBER DEFAULT NULL)** [SOURCE: L140-167]
  - What it does: Opens p_cursor over LEAVE_BALANCES joined to EMPLOYEES, DEPARTMENTS, and LEAVE_TYPES, grouped by department/leave type, returning employee count, average entitled/used/remaining balance, and utilization percentage for one calendar year.
  - Business rules: Scoped to a single CALENDAR_YEAR (no cross-year combination); only ACTIVE employees are included; department filter is optional.
  - Numbers & thresholds: AVG_REMAINING = ROUND(AVG(OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT), 1). UTILIZATION_PCT = ROUND(AVG(USED) * 100.0 / NULLIF(AVG(OPENING_BALANCE + ACCRUED), 0), 1) — NULLIF guards divide-by-zero. All averages rounded to 1 decimal place.
  - Security & error handling: NULLIF(...,0) prevents division-by-zero when average entitlement is 0; no other error handling.
  - Data in/out: Inputs — p_year (default current calendar year), p_dept_id (optional filter). Output — p_cursor OUT REF CURSOR opened over LEAVE_BALANCES/EMPLOYEES/DEPARTMENTS/LEAVE_TYPES.

  **PROCEDURE payroll_summary_report(p_cursor OUT t_report_cursor, p_period_id NUMBER)** [SOURCE: L169-200]
  - What it does: Opens p_cursor over PAYROLL_DETAILS joined to PAYROLL_RUNS, EMPLOYEES, and DEPARTMENTS, grouped by department, returning employee count and payroll totals (gross, federal tax, state tax, Social Security, Medicare, total deductions, net pay) for a single pay period.
  - Business rules: TOTAL_GROSS sums only ELEMENT_TYPE='EARNING' lines. TOTAL_DEDUCTIONS sums the absolute value of ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') lines (amounts are stored negative in PAYROLL_DETAILS). TOTAL_NET is the raw sum of all line amounts. Lines with STATUS='ERROR' are excluded from every total.
  - Numbers & thresholds: ELEMENT_ID lookup table used to attribute specific tax totals: 100 = Federal Income Tax, 101 = State Income Tax, 102 = Social Security (FICA), 103 = Medicare. Each of TOTAL_FED_TAX/TOTAL_STATE_TAX/TOTAL_SS/TOTAL_MEDICARE sums ABS(AMOUNT) for its respective ELEMENT_ID.
  - Security & error handling: None.
  - Data in/out: Inputs — p_period_id (required). Output — p_cursor OUT REF CURSOR opened over PAYROLL_DETAILS/PAYROLL_RUNS/EMPLOYEES/DEPARTMENTS.

  **PROCEDURE eeo_compliance_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE)** [SOURCE: L202-227]
  - What it does: Opens p_cursor over EMPLOYEES joined to JOB_TITLES, grouped by EEO_CATEGORY, returning total headcount, gender sub-counts (male/female/other/not-disclosed), and female representation percentage as of a given date.
  - Business rules: Only ACTIVE employees hired on or before p_as_of_date are counted. Gender breakdown uses codes 'M', 'F', 'O'; employees with a NULL gender are counted separately as "not disclosed" and excluded from the M/F/O totals.
  - Numbers & thresholds: FEMALE_PCT = ROUND(SUM(CASE GENDER='F' THEN 1 ELSE 0) * 100.0 / COUNT(*), 1) — percentage rounded to 1 decimal place.
  - Security & error handling: None.
  - Data in/out: Inputs — p_as_of_date (default SYSDATE). Output — p_cursor OUT REF CURSOR opened over EMPLOYEES/JOB_TITLES.

  **PROCEDURE refresh_reporting_tables(p_user VARCHAR2 DEFAULT USER)** [SOURCE: L229-237]
  - What it does: Placeholder procedure — logs a fixed informational message via PKG_COMMON.log_info [L235-236]; the source comments state that in production this would truncate and repopulate denormalized RPT_* tables, but no such DML is present in this body.
  - Business rules: None implemented — this is a stub.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Inputs — p_user. Output — writes one log entry via PKG_COMMON.log_info; no table DML occurs despite the procedure's name.

**DEPENDENCIES:**
  Data touched:
  - Reads: EMPLOYEES — headcount/compensation/turnover/new-hires/leave/EEO source rows (headcount_report, compensation_summary, turnover_report, new_hires_report, leave_utilization_report, payroll_summary_report via join, eeo_compliance_report), including a self-join for manager name (new_hires_report)
  - Reads: DEPARTMENTS — department name/cost center grouping (headcount_report, compensation_summary, turnover_report, new_hires_report, leave_utilization_report, payroll_summary_report)
  - Reads: LOCATIONS — location name/city/state (headcount_report, new_hires_report)
  - Reads: JOB_TITLES — job title / EEO category (compensation_summary, new_hires_report, eeo_compliance_report)
  - Reads: JOB_GRADES — grade name and min/max salary band (compensation_summary)
  - Reads: SALARY_RECORDS — active base salary (compensation_summary, new_hires_report)
  - Reads: LEAVE_BALANCES — opening balance/accrued/used/adjustment (leave_utilization_report)
  - Reads: LEAVE_TYPES — leave type name (leave_utilization_report)
  - Reads: PAYROLL_DETAILS — payroll line amounts/element IDs/status (payroll_summary_report)
  - Reads: PAYROLL_RUNS — period linkage (payroll_summary_report)
  - Writes: None (this package is read-only reporting; refresh_reporting_tables is a stub that performs no DML)

  CALLS: PKG_COMMON.log_info | EVIDENCE: OBSERVED | SOURCE: L235

  Config/env: None
  External integrations: None

**GAPS:**
  refresh_reporting_tables is explicitly a placeholder — the comment at L233-234 states production behavior (truncate/repopulate RPT_* tables) that is not implemented in this body — NOT_ANALYZED / UNRESOLVED whether a real implementation exists elsewhere.
  PKG_COMMON.log_info implementation is external to this file — EXTERNAL.
  t_report_cursor type is referenced throughout but not declared in this file — presumably in PKG_REPORTING.pks — EXTERNAL/UNKNOWN.

*[pipeline status — type: plsql-body · pass: original · attempt: 1 · coverage: 100% (numbers 7/7 · procedures 8/8 · units 8/8 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 2
Files delivered: 2
  Full coverage on first pass: 2
  Required correction: 0
  Still incomplete after max attempts: 0
Raw source: 29803 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===