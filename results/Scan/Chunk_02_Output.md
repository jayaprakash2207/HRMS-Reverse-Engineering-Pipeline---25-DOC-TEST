MP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, pp.PERIOD_NAME, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION', 'TAX', 'BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS, SUM(pd.AMOUNT) AS NET_PAY, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE, 0 AS YTD_GROSS, 0 AS YTD_NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND (p_emp_id IS NULL OR pd.EMP_ID = p_emp_id) GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME ORDER BY e.LAST_NAME

Business rules:
- YTD_GROSS and YTD_NET are placeholder 0 values (not yet implemented)
- ELEMENT_ID 100/101/102/103 mapped to federal/state/SS/Medicare respectively

Tables referenced: PAYROLL_DETAILS (EMP_ID, ELEMENT_TYPE, ELEMENT_ID, AMOUNT, RUN_ID, STATUS), EMPLOYEES (EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME), PAYROLL_RUNS (RUN_ID, PERIOD_ID), PAY_PERIODS (PERIOD_ID, PERIOD_NAME)

---

**FUNCTION get_ytd_earnings(p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
- SELECT NVL(SUM(pd.AMOUNT), 0) FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.EMP_ID = p_emp_id AND pd.ELEMENT_TYPE = 'EARNING' AND pd.STATUS = 'CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
- RETURN v_ytd

Business rule: YTD earnings = sum of all EARNING elements with STATUS = 'CALCULATED' in the given tax year, matched by PERIOD_START_DATE year

Tables referenced: PAYROLL_DETAILS (EMP_ID, ELEMENT_TYPE, STATUS, RUN_ID, AMOUNT), PAYROLL_RUNS (RUN_ID, PERIOD_ID), PAY_PERIODS (PERIOD_ID, PERIOD_START_DATE)

---

**PROCEDURE generate_pay_register(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Purpose: Writes CSV pay register to flat file. LEGACY — should be replaced with modern reporting.

Logic:
1. SELECT pp.PERIOD_NAME FROM PAYROLL_RUNS pr JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pr.RUN_ID = p_run_id
2. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS') || '.csv'
3. v_file := UTL_FILE.FOPEN('PAYROLL_OUTPUT', v_filename, 'W', 32767)
4. Write header: 'EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY'
5. FOR rec IN (SELECT e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, d.DEPT_NAME, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FED, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SS, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MED, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION', 'BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS DEDS, SUM(pd.AMOUNT) AS NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' GROUP BY e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, d.DEPT_NAME ORDER BY e.LAST_NAME)
6. Write CSV line: EMP_NUMBER,"{EMP_NAME}","{DEPT_NAME}",{GROSS:FM999999990.00},{FED},{STATE},{SS},{MED},{DEDS},{NET}
7. UTL_FILE.FCLOSE; DBMS_OUTPUT.PUT_LINE('Pay register generated: ' || v_filename)
8. EXCEPTION WHEN OTHERS: close file, PKG_COMMON.log_error, RAISE

Oracle directory used: 'PAYROLL_OUTPUT'
File format: CSV with quoted name fields
Tables referenced: PAYROLL_RUNS (RUN_ID, PERIOD_ID), PAY_PERIODS (PERIOD_ID, PERIOD_NAME), PAYROLL_DETAILS, EMPLOYEES (EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID), DEPARTMENTS (DEPT_ID, DEPT_NAME)
File I/O: UTL_FILE, max line 32767
External service calls: UTL_FILE, DBMS_OUTPUT.PUT_LINE, PKG_COMMON.log_error

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks ===

**Package:** HRMS.PKG_PERFORMANCE
**Schema:** HRMS
**Purpose:** Performance Review Management — review cycles, goal tracking, ratings, calibration

**Dependencies:** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
**Called by:** HRMS_PERFORMANCE form, batch calibration job

**Type:** `t_review_cursor` — REF CURSOR

**Public Method Signatures:**

`FUNCTION create_review_cycle(p_cycle_name VARCHAR2, p_cycle_year NUMBER, p_start_date DATE, p_end_date DATE, p_self_review_due DATE DEFAULT NULL, p_manager_review_due DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE open_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE close_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)`

`FUNCTION create_review(p_cycle_id NUMBER, p_emp_id NUMBER, p_reviewer_emp_id NUMBER, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE submit_self_assessment(p_review_id NUMBER, p_self_assessment CLOB, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE submit_manager_review(p_review_id NUMBER, p_overall_rating NUMBER, p_manager_assessment CLOB, p_strengths CLOB DEFAULT NULL, p_improvement_areas CLOB DEFAULT NULL, p_development_plan CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE acknowledge_review(p_review_id NUMBER, p_emp_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)`

`FUNCTION add_goal(p_review_id NUMBER, p_emp_id NUMBER, p_goal_title VARCHAR2, p_goal_description CLOB DEFAULT NULL, p_goal_category VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct NUMBER DEFAULT 0, p_target_date DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE update_goal_progress(p_goal_id NUMBER, p_progress_pct NUMBER, p_status VARCHAR2 DEFAULT NULL, p_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)`

`PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id NUMBER, p_cycle_id NUMBER)`

`FUNCTION get_rating_distribution(p_cycle_id NUMBER, p_dept_id NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR`

`PROCEDURE generate_reviews_for_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)`

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb ===

**Package Body:** HRMS.PKG_PERFORMANCE

---

**FUNCTION create_review_cycle(...) RETURN NUMBER**

Logic:
1. SELECT SEQ_REVIEW_CYCLE.NEXTVAL INTO v_cycle_id FROM DUAL
2. INSERT INTO REVIEW_CYCLES (CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_cycle_id, p_cycle_name, p_cycle_year, p_start_date, p_end_date, p_self_review_due, p_manager_review_due, 'DRAFT', p_user, SYSDATE)
3. PKG_AUDIT.log_action('REVIEW_CYCLES', v_cycle_id, 'INSERT', p_user)
4. RETURN v_cycle_id

Business rule: New review cycles start in 'DRAFT' status

Tables referenced: REVIEW_CYCLES (CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE)
Sequences used: SEQ_REVIEW_CYCLE
External service calls: PKG_AUDIT.log_action

---

**PROCEDURE open_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE REVIEW_CYCLES SET STATUS = 'OPEN', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id AND STATUS = 'DRAFT'
2. IF SQL%ROWCOUNT = 0 → RAISE_APPLICATION_ERROR(-20401, 'Cannot open cycle - must be in DRAFT status')

Business rule: Only DRAFT cycles can be opened

Tables referenced: REVIEW_CYCLES (CYCLE_ID, STATUS, MODIFIED_BY, MODIFIED_DATE)
Exceptions thrown: -20401

---

**PROCEDURE close_review_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic: UPDATE REVIEW_CYCLES SET STATUS = 'CLOSED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id

Tables referenced: REVIEW_CYCLES

---

**FUNCTION create_review(p_cycle_id NUMBER, p_emp_id NUMBER, p_reviewer_emp_id NUMBER, p_user VARCHAR2 DEFAULT USER) RETURN NUMBER**

Logic:
1. SELECT SEQ_PERF_REVIEW.NEXTVAL INTO v_review_id FROM DUAL
2. INSERT INTO PERFORMANCE_REVIEWS (REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_review_id, p_cycle_id, p_emp_id, p_reviewer_emp_id, 'ANNUAL', 'NOT_STARTED', p_user, SYSDATE)
3. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => p_emp_id, p_type => 'EMAIL', p_subject => 'Performance Review Initiated', p_body => 'Your annual performance review has been initiated. Please complete your self-assessment.', p_user => p_user)
4. RETURN v_review_id

Business rules:
- REVIEW_TYPE always 'ANNUAL' in this path
- Initial STATUS = 'NOT_STARTED'
- Employee notified on review creation

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE)
Sequences used: SEQ_PERF_REVIEW
External service calls: PKG_NOTIFICATION.send_notification

---

**PROCEDURE submit_self_assessment(p_review_id NUMBER, p_self_assessment CLOB, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_REVIEWS SET SELF_ASSESSMENT = p_self_assessment, STATUS = 'MANAGER_REVIEW', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS IN ('NOT_STARTED', 'SELF_REVIEW')
2. IF SQL%ROWCOUNT = 0 → RAISE_APPLICATION_ERROR(-20402, 'Review not found or not in correct status')
3. SELECT REVIEWER_EMP_ID FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id → v_manager_id
4. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => v_manager_id, p_type => 'EMAIL', p_subject => 'Self-Assessment Submitted - Ready for Manager Review', p_body => 'An employee has completed their self-assessment. Please proceed with the manager review.', p_user => p_user)

Business rules:
- Can submit self-assessment when status is 'NOT_STARTED' or 'SELF_REVIEW'
- Status transitions to 'MANAGER_REVIEW' on submission
- Manager notified on submission

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, SELF_ASSESSMENT, STATUS, REVIEWER_EMP_ID, MODIFIED_BY, MODIFIED_DATE)
External service calls: PKG_NOTIFICATION.send_notification
Exceptions thrown: -20402

---

**PROCEDURE submit_manager_review(...)**

Parameters: p_review_id NUMBER, p_overall_rating NUMBER, p_manager_assessment CLOB, p_strengths CLOB DEFAULT NULL, p_improvement_areas CLOB DEFAULT NULL, p_development_plan CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

Logic:
1. IF p_overall_rating < 1.0 OR p_overall_rating > 5.0 → RAISE_APPLICATION_ERROR(-20403, 'Rating must be between 1.0 and 5.0')
2. UPDATE PERFORMANCE_REVIEWS SET OVERALL_RATING = p_overall_rating, RATING_LABEL = CASE WHEN p_overall_rating >= 4.5 THEN 'Exceptional' WHEN p_overall_rating >= 3.5 THEN 'Exceeds Expectations' WHEN p_overall_rating >= 2.5 THEN 'Meets Expectations' WHEN p_overall_rating >= 1.5 THEN 'Needs Improvement' ELSE 'Unsatisfactory' END, MANAGER_ASSESSMENT = p_manager_assessment, STRENGTHS = p_strengths, AREAS_FOR_IMPROVEMENT = p_improvement_areas, DEVELOPMENT_PLAN = p_development_plan, STATUS = 'COMPLETED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id
3. SELECT EMP_ID FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id → v_emp_id
4. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => v_emp_id, p_type => 'EMAIL', p_subject => 'Performance Review Completed', p_body => 'Your manager has completed your performance review. Please review and acknowledge.', p_user => p_user)

Business rules — Rating scale (exact boundaries):
| Rating Value | Label |
|---|---|
| >= 4.5 | Exceptional |
| >= 3.5 and < 4.5 | Exceeds Expectations |
| >= 2.5 and < 3.5 | Meets Expectations |
| >= 1.5 and < 2.5 | Needs Improvement |
| < 1.5 (and >= 1.0) | Unsatisfactory |

- Valid rating range: 1.0 – 5.0 (inclusive)
- Status transitions to 'COMPLETED'
- Employee notified on completion

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, OVERALL_RATING, RATING_LABEL, MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN, STATUS, EMP_ID, MODIFIED_BY, MODIFIED_DATE)
External service calls: PKG_NOTIFICATION.send_notification
Exceptions thrown: -20403

---

**PROCEDURE acknowledge_review(p_review_id NUMBER, p_emp_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)**

Logic:
- UPDATE PERFORMANCE_REVIEWS SET EMPLOYEE_COMMENTS = p_emp_comments, EMPLOYEE_ACK_DATE = SYSDATE, STATUS = 'ACKNOWLEDGED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS = 'COMPLETED'

Business rule: Only COMPLETED reviews can be acknowledged; status transitions to 'ACKNOWLEDGED'

Tables referenced: PERFORMANCE_REVIEWS (REVIEW_ID, EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE, STATUS, MODIFIED_BY, MODIFIED_DATE)

---

**FUNCTION add_goal(...) RETURN NUMBER**

Parameters: p_review_id NUMBER, p_emp_id NUMBER, p_goal_title VARCHAR2, p_goal_description CLOB DEFAULT NULL, p_goal_category VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct NUMBER DEFAULT 0, p_target_date DATE DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

Logic:
1. SELECT SEQ_PERF_GOAL.NEXTVAL INTO v_goal_id FROM DUAL
2. INSERT INTO PERFORMANCE_GOALS (GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE) VALUES (v_goal_id, p_review_id, p_emp_id, p_goal_title, p_goal_description, p_goal_category, p_weight_pct, p_target_date, 'NOT_STARTED', 0, p_user, SYSDATE)
3. RETURN v_goal_id

Business rules:
- Default category 'BUSINESS'
- Default weight 0
- Initial STATUS = 'NOT_STARTED', PROGRESS_PCT = 0

Tables referenced: PERFORMANCE_GOALS (GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE)
Sequences used: SEQ_PERF_GOAL

---

**PROCEDURE update_goal_progress(p_goal_id NUMBER, p_progress_pct NUMBER, p_status VARCHAR2 DEFAULT NULL, p_comments CLOB DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)**

Logic:
- UPDATE PERFORMANCE_GOALS SET PROGRESS_PCT = p_progress_pct, STATUS = NVL(p_status, CASE WHEN p_progress_pct >= 100 THEN 'COMPLETED' WHEN p_progress_pct > 0 THEN 'IN_PROGRESS' ELSE STATUS END), COMMENTS = NVL(p_comments, COMMENTS), MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE GOAL_ID = p_goal_id

Business rules:
- If explicit status not provided: progress >= 100 → 'COMPLETED'; progress > 0 → 'IN_PROGRESS'; progress = 0 → unchanged
- Comments only updated if p_comments IS NOT NULL

Tables referenced: PERFORMANCE_GOALS (GOAL_ID, PROGRESS_PCT, STATUS, COMMENTS, MODIFIED_BY, MODIFIED_DATE)

---

**PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id NUMBER, p_cycle_id NUMBER)**

Logic:
- OPEN p_cursor FOR SELECT pr.REVIEW_ID, pr.EMP_ID, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME, j.JOB_TITLE, d.DEPT_NAME, pr.STATUS, pr.OVERALL_RATING, pr.RATING_LABEL FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pr.REVIEWER_EMP_ID = p_manager_id AND pr.CYCLE_ID = p_cycle_id ORDER BY e.LAST_NAME

Tables referenced: PERFORMANCE_REVIEWS, EMPLOYEES, JOB_TITLES, DEPARTMENTS

---

**FUNCTION get_rating_distribution(p_cycle_id NUMBER, p_dept_id NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR**

Logic:
- OPEN v_cursor FOR SELECT pr.RATING_LABEL, COUNT(*) AS COUNT, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID WHERE pr.CYCLE_ID = p_cycle_id AND pr.OVERALL_RATING IS NOT NULL AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) GROUP BY pr.RATING_LABEL ORDER BY MIN(pr.OVERALL_RATING) DESC
- RETURN v_cursor

Business rule: Percentage uses analytic SUM OVER () for cross-group total; ordered by minimum rating value descending

Tables referenced: PERFORMANCE_REVIEWS (CYCLE_ID, OVERALL_RATING, RATING_LABEL, EMP_ID), EMPLOYEES (EMP_ID, DEPT_ID)

---

**PROCEDURE generate_reviews_for_cycle(p_cycle_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. FOR emp_rec IN (SELECT EMP_ID, MANAGER_EMP_ID FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' AND MANAGER_EMP_ID IS NOT NULL):
   - v_review_id := create_review(p_cycle_id, emp_rec.EMP_ID, emp_rec.MANAGER_EMP_ID, p_user); v_count + 1
   - EXCEPTION WHEN DUP_VAL_ON_INDEX → NULL (review already exists)
2. COMMIT
3. DBMS_OUTPUT.PUT_LINE('Generated ' || v_count || ' reviews for cycle ' || p_cycle_id)

Business rule: Only active employees with a manager get reviews (MANAGER_EMP_ID IS NOT NULL); duplicate reviews silently skipped

Tables referenced: EMPLOYEES (EMP_ID, EMPLOYMENT_STATUS, MANAGER_EMP_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks ===

**Package:** HRMS.PKG_REPORTING
**Schema:** HRMS
**Purpose:** Report Generation — headcount, compensation, turnover, compliance reporting

**Dependencies:** PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON
**Called by:** HRMS_REPORTS form, Oracle Reports (.rdf), batch jobs

**Known issues:**
- Denormalized reporting tables refreshed nightly; stale during business hours
- Some reports use hard-coded fiscal year start (Oct 1)

**Type:** `t_report_cursor` — REF CURSOR

**Public Method Signatures:**

`PROCEDURE headcount_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE, p_dept_id NUMBER DEFAULT NULL, p_location VARCHAR2 DEFAULT NULL)`

`PROCEDURE compensation_summary(p_cursor OUT t_report_cursor, p_dept_id NUMBER DEFAULT NULL, p_grade_id NUMBER DEFAULT NULL)`

`PROCEDURE turnover_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)`

`PROCEDURE new_hires_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)`

`PROCEDURE leave_utilization_report(p_cursor OUT t_report_cursor, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE), p_dept_id NUMBER DEFAULT NULL)`

`PROCEDURE payroll_summary_report(p_cursor OUT t_report_cursor, p_period_id NUMBER)`

`PROCEDURE eeo_compliance_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE)`

`PROCEDURE refresh_reporting_tables(p_user VARCHAR2 DEFAULT USER)`

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pkb ===

**Package Body:** HRMS.PKG_REPORTING

---

**PROCEDURE headcount_report(...)**

Query: SELECT d.DEPT_NAME, d.COST_CENTER, l.LOCATION_NAME, l.CITY, l.STATE_PROVINCE, COUNT(*) AS HEADCOUNT, SUM(CASE WHEN e.EMPLOYMENT_TYPE = 'FULL_TIME' THEN 1 ELSE 0 END) AS FT_COUNT, SUM(CASE WHEN e.EMPLOYMENT_TYPE = 'PART_TIME' THEN 1 ELSE 0 END) AS PT_COUNT, SUM(CASE WHEN e.EMPLOYMENT_TYPE = 'CONTRACT' THEN 1 ELSE 0 END) AS CONTRACT_COUNT, SUM(CASE WHEN e.GENDER = 'M' THEN 1 ELSE 0 END) AS MALE_COUNT, SUM(CASE WHEN e.GENDER = 'F' THEN 1 ELSE 0 END) AS FEMALE_COUNT, ROUND(AVG(MONTHS_BETWEEN(p_as_of_date, e.HIRE_DATE) / 12), 1) AS AVG_TENURE_YEARS FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID LEFT JOIN LOCATIONS l ON e.LOCATION_CODE = l.LOCATION_CODE WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.HIRE_DATE <= p_as_of_date AND (e.TERMINATION_DATE IS NULL OR e.TERMINATION_DATE > p_as_of_date) AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) AND (p_location IS NULL OR e.LOCATION_CODE = p_location) GROUP BY d.DEPT_NAME, d.COST_CENTER, l.LOCATION_NAME, l.CITY, l.STATE_PROVINCE ORDER BY d.DEPT_NAME

Business rules:
- Active employees only, hired on or before as-of date
- Terminated on or before as-of date are excluded
- Gender codes: 'M', 'F'; others not explicitly counted
- Employment type codes: 'FULL_TIME', 'PART_TIME', 'CONTRACT'
- Average tenure in years (1 decimal place), calculated vs p_as_of_date

Tables referenced: EMPLOYEES, DEPARTMENTS, LOCATIONS

---

**PROCEDURE compensation_summary(...)**

Query: SELECT d.DEPT_NAME, g.GRADE_NAME, j.JOB_TITLE, COUNT(*) AS EMP_COUNT, g.MIN_SALARY AS GRADE_MIN, g.MAX_SALARY AS GRADE_MAX, MIN(sr.BASE_SALARY) AS ACTUAL_MIN, MAX(sr.BASE_SALARY) AS ACTUAL_MAX, ROUND(AVG(sr.BASE_SALARY), 2) AS AVG_SALARY, ROUND(MEDIAN(sr.BASE_SALARY), 2) AS MEDIAN_SALARY, ROUND(AVG(sr.BASE_SALARY / ((g.MIN_SALARY + g.MAX_SALARY) / 2)) * 100, 1) AS COMPA_RATIO FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID JOIN JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y' WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) AND (p_grade_id IS NULL OR g.GRADE_ID = p_grade_id) GROUP BY d.DEPT_NAME, g.GRADE_NAME, j.JOB_TITLE, g.MIN_SALARY, g.MAX_SALARY ORDER BY d.DEPT_NAME, g.GRADE_NAME

Business rule: Compa-ratio = AVG(actual salary / midpoint) × 100, where midpoint = (MIN_SALARY + MAX_SALARY) / 2

Tables referenced: EMPLOYEES, DEPARTMENTS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS

---

**PROCEDURE turnover_report(...)**

Query: SELECT d.DEPT_NAME, COUNT(CASE WHEN e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) AS TERMINATIONS, COUNT(CASE WHEN e.EMPLOYMENT_STATUS = 'ACTIVE' THEN 1 END) AS CURRENT_HC, ROUND(COUNT(CASE WHEN e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN e.HIRE_DATE <= p_end_date THEN 1 END), 0), 1) AS TURNOVER_PCT, COUNT(CASE WHEN e.TERMINATION_REASON = 'VOLUNTARY' AND e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) AS VOLUNTARY, COUNT(CASE WHEN e.TERMINATION_REASON != 'VOLUNTARY' AND e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN 1 END) AS INVOLUNTARY, ROUND(AVG(CASE WHEN e.TERMINATION_DATE BETWEEN p_start_date AND p_end_date THEN MONTHS_BETWEEN(e.TERMINATION_DATE, e.HIRE_DATE) / 12 END), 1) AS AVG_TENURE_AT_EXIT FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) AND e.HIRE_DATE <= p_end_date GROUP BY d.DEPT_NAME HAVING COUNT(CASE WHEN e.HIRE_DATE <= p_end_date THEN 1 END) > 0 ORDER BY TURNOVER_PCT DESC NULLS LAST

Business rules:
- Turnover % = terminations in period / all employees hired on or before end date × 100
- Voluntary = TERMINATION_REASON = 'VOLUNTARY'; involuntary = everything else (including NULL termination reason if terminated in period)
- Average tenure at exit measured in years (1 decimal)
- Groups with zero eligible employees excluded (HAVING)
- NULLS LAST in ORDER BY for departments with no terminations

Tables referenced: EMPLOYEES (EMP_ID, DEPT_ID, TERMINATION_DATE, EMPLOYMENT_STATUS, TERMINATION_REASON, HIRE_DATE), DEPARTMENTS (DEPT_ID, DEPT_NAME)

---

**PROCEDURE new_hires_report(...)**

Query: SELECT e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, e.HIRE_DATE, d.DEPT_NAME, j.JOB_TITLE, l.LOCATION_NAME, e.EMPLOYMENT_TYPE, sr.BASE_SALARY, e.MANAGER_EMP_ID, m.FIRST_NAME || ' ' || m.LAST_NAME AS MANAGER_NAME FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID LEFT JOIN LOCATIONS l ON e.LOCATION_CODE = l.LOCATION_CODE LEFT JOIN EMPLOYEES m ON e.MANAGER_EMP_ID = m.EMP_ID LEFT JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y' WHERE e.HIRE_DATE BETWEEN p_start_date AND p_end_date AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) ORDER BY e.HIRE_DATE DESC

Tables referenced: EMPLOYEES (self-join for manager), DEPARTMENTS, JOB_TITLES, LOCATIONS, SALARY_RECORDS

---

**PROCEDURE leave_utilization_report(...)**

Query: SELECT d.DEPT_NAME, lt.LEAVE_TYPE_NAME, COUNT(DISTINCT lb.EMP_ID) AS EMP_COUNT, ROUND(AVG(lb.OPENING_BALANCE + lb.ACCRUED), 1) AS AVG_ENTITLED, ROUND(AVG(lb.USED), 1) AS AVG_USED, ROUND(AVG(lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT), 1) AS AVG_REMAINING, ROUND(AVG(lb.USED) * 100.0 / NULLIF(AVG(lb.OPENING_BALANCE + lb.ACCRUED), 0), 1) AS UTILIZATION_PCT FROM LEAVE_BALANCES lb JOIN EMPLOYEES e ON lb.EMP_ID = e.EMP_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN LEAVE_TYPES lt ON lb.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID WHERE lb.CALENDAR_YEAR = p_year AND e.EMPLOYMENT_STATUS = 'ACTIVE' AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) GROUP BY d.DEPT_NAME, lt.LEAVE_TYPE_NAME ORDER BY d.DEPT_NAME, lt.LEAVE_TYPE_NAME

Business rules:
- Entitled = OPENING_BALANCE + ACCRUED
- Remaining = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT
- Utilization % = AVG_USED / AVG_ENTITLED × 100 (NULLIF prevents divide-by-zero)

Tables referenced: LEAVE_BALANCES, EMPLOYEES, DEPARTMENTS, LEAVE_TYPES

---

**PROCEDURE payroll_summary_report(p_cursor OUT t_report_cursor, p_period_id NUMBER)**

Query: SELECT d.DEPT_NAME, COUNT(DISTINCT pd.EMP_ID) AS EMP_COUNT, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS TOTAL_GROSS, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_FED_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_STATE_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_SS, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_MEDICARE, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS, SUM(pd.AMOUNT) AS TOTAL_NET FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pr.PERIOD_ID = p_period_id AND pd.STATUS != 'ERROR' GROUP BY d.DEPT_NAME ORDER BY d.DEPT_NAME

Tables referenced: PAYROLL_DETAILS, PAYROLL_RUNS, EMPLOYEES, DEPARTMENTS

---

**PROCEDURE eeo_compliance_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE)**

Query: SELECT j.EEO_CATEGORY, COUNT(*) AS TOTAL, SUM(CASE WHEN e.GENDER = 'M' THEN 1 ELSE 0 END) AS MALE, SUM(CASE WHEN e.GENDER = 'F' THEN 1 ELSE 0 END) AS FEMALE, SUM(CASE WHEN e.GENDER = 'O' THEN 1 ELSE 0 END) AS OTHER_GENDER, SUM(CASE WHEN e.GENDER IS NULL THEN 1 ELSE 0 END) AS NOT_DISCLOSED, ROUND(SUM(CASE WHEN e.GENDER = 'F' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS FEMALE_PCT FROM EMPLOYEES e JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.HIRE_DATE <= p_as_of_date GROUP BY j.EEO_CATEGORY ORDER BY j.EEO_CATEGORY

Business rules:
- Gender codes: 'M' (male), 'F' (female), 'O' (other), NULL (not disclosed)
- Female % = female count / total × 100 (1 decimal)
- Grouped by EEO_CATEGORY from JOB_TITLES table

Tables referenced: EMPLOYEES (EMP_ID, GENDER, EMPLOYMENT_STATUS, HIRE_DATE, JOB_ID), JOB_TITLES (JOB_ID, EEO_CATEGORY)

---

**PROCEDURE refresh_reporting_tables(p_user VARCHAR2 DEFAULT USER)**

Logic: Placeholder — calls PKG_COMMON.log_info('PKG_REPORTING', 'refresh_reporting_tables', 'Reporting tables refreshed', p_user)

Note: In production, truncates and repopulates RPT_* denormalized reporting tables. Not implemented here.

External service calls: PKG_COMMON.log_info

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb ===

**Package:** HRMS.PKG_SECURITY (body only — no .pks provided in source set)
**Schema:** HRMS
**Purpose:** Authentication and Authorization

---

**Private Constants:**
- `c_encryption_key` — RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!') **VULNERABILITY: hard-coded encryption key in source**
- `c_session_timeout_min` — NUMBER := 30 (session timeout in minutes)

---

**FUNCTION hash_password(p_password VARCHAR2) RETURN VARCHAR2**

Logic: RETURN RAWTOHEX(DBMS_CRYPTO.HASH(UTL_RAW.CAST_TO_RAW(p_password), DBMS_CRYPTO.HASH_MD5))

Security weakness: Uses MD5 — should use stronger algorithm (SHA-256 or bcrypt)
External calls: DBMS_CRYPTO.HASH (HASH_MD5), UTL_RAW.CAST_TO_RAW, RAWTOHEX

---

**FUNCTION authenticate(p_username VARCHAR2, p_password VARCHAR2, p_ip_address VARCHAR2 DEFAULT NULL) RETURN NUMBER**

Logic:
1. SELECT EMP_ID FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(p_username) AND EMPLOYMENT_STATUS = 'ACTIVE'; EXCEPTION WHEN NO_DATA_FOUND → RAISE_APPLICATION_ERROR(-20301, 'Invalid username or password'); WHEN TOO_MANY_ROWS → SELECT MIN(EMP_ID) ... (picks lowest EMP_ID among duplicates)
2. SELECT SEQ_USER_SESSION.NEXTVAL INTO v_session_id FROM DUAL
3. INSERT INTO USER_SESSIONS (SESSION_ID, EMP_ID, USERNAME, LOGIN_TIME, IP_ADDRESS, SESSION_STATUS, CREATED_DATE) VALUES (v_session_id, v_emp_id, p_username, SYSDATE, p_ip_address, 'ACTIVE', SYSDATE)
4. PKG_EMPLOYEE.set_session_context(p_username, v_emp_id)
5. PKG_AUDIT.log_action('USER_SESSIONS', v_session_id, 'INSERT', p_username)
6. RETURN v_session_id

Security vulnerabilities:
- No brute-force protection (no lockout after N failed attempts)
- Timing attack: NO_DATA_FOUND (invalid user) returns immediately while valid-user/invalid-password path would differ — response times distinguishable
- Authentication appears to not actually verify p_password against a stored hash (comment says passwords in separate USER_CREDENTIALS table — actual check not implemented here)

Tables referenced: EMPLOYEES (EMAIL, EMPLOYMENT_STATUS, EMP_ID), USER_SESSIONS (SESSION_ID, EMP_ID, USERNAME, LOGIN_TIME, IP_ADDRESS, SESSION_STATUS, CREATED_DATE)
Sequences used: SEQ_USER_SESSION
External service calls: PKG_EMPLOYEE.set_session_context, PKG_AUDIT.log_action
Exceptions thrown: -20301

---

**PROCEDURE logout(p_session_id NUMBER)**

Logic: UPDATE USER_SESSIONS SET LOGOUT_TIME = SYSDATE, SESSION_STATUS = 'CLOSED' WHERE SESSION_ID = p_session_id

Tables referenced: USER_SESSIONS (SESSION_ID, LOGOUT_TIME, SESSION_STATUS)

---

**FUNCTION is_session_valid(p_session_id NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT SESSION_STATUS, LOGIN_TIME FROM USER_SESSIONS WHERE SESSION_ID = p_session_id → v_status, v_login_time
2. IF v_status != 'ACTIVE' → RETURN FALSE
3. IF (SYSDATE - v_login_time) * 24 * 60 > 30 (c_session_timeout_min): UPDATE USER_SESSIONS SET SESSION_STATUS = 'EXPIRED', LOGOUT_TIME = SYSDATE WHERE SESSION_ID = p_session_id; RETURN FALSE
4. RETURN TRUE
5. EXCEPTION WHEN NO_DATA_FOUND → RETURN FALSE

Business rule: Session expires after 30 minutes of inactivity from login time (note: based on LOGIN_TIME, not last activity — no session refresh/touch implemented)

Tables referenced: USER_SESSIONS (SESSION_ID, SESSION_STATUS, LOGIN_TIME, LOGOUT_TIME)

---

**FUNCTION has_permission(p_emp_id NUMBER, p_module VARCHAR2, p_action VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN**

Logic:
1. SELECT e.DEPT_ID, j.GRADE_ID FROM EMPLOYEES e JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE e.EMP_ID = p_emp_id
2. Permission rules (simplified grade-based model):
   - IF v_grade_id >= 8 → RETURN TRUE (senior management, full access to all modules)
   - IF p_action = 'VIEW' AND v_grade_id >= 5 → RETURN TRUE (mid-level can view all)
   - IF p_module = 'LEAVE' AND p_action IN ('CREATE', 'VIEW') → RETURN TRUE (everyone can submit/view own leave)
   - IF p_module = 'EMPLOYEE' AND p_action = 'VIEW' → RETURN TRUE (everyone can view own profile)
   - RETURN FALSE
3. EXCEPTION WHEN NO_DATA_FOUND → RETURN FALSE

Business rules — Permission tiers:
| Grade | Access Level |
|---|---|
| >= 8 | Full access to all modules and all actions |
| >= 5 and < 8 | VIEW action on all modules |
| Any grade | CREATE and VIEW on LEAVE module |
| Any grade | VIEW on EMPLOYEE module |
| All others | No access |

Note: This is declared as a simplified model; production would use a ROLES / PERMISSIONS junction table

Tables referenced: EMPLOYEES (EMP_ID, DEPT_ID, JOB_ID), JOB_TITLES (JOB_ID, GRADE_ID)

---

**FUNCTION encrypt_ssn(p_ssn VARCHAR2) RETURN VARCHAR2**

Logic:
- v_raw := DBMS_CRYPTO.ENCRYPT(src => UTL_RAW.CAST_TO_RAW(p_ssn), typ => DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC + DBMS_CRYPTO.PAD_PKCS5, key => c_encryption_key)
- RETURN RAWTOHEX(v_raw)

Algorithm: AES-256, CBC mode, PKCS5 padding
Security vulnerability: Encryption key 'HR$ystem_3ncrypt10n_K3y_2024!!' hard-coded in source

External calls: DBMS_CRYPTO.ENCRYPT, UTL_RAW.CAST_TO_RAW, RAWTOHEX

---

**FUNCTION decrypt_ssn(p_encrypted VARCHAR2) RETURN VARCHAR2**

Logic:
- v_raw := DBMS_CRYPTO.DECRYPT(src => HEXTORAW(p_encrypted), typ => DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC + DBMS_CRYPTO.PAD_PKCS5, key => c_encryption_key)
- RETURN UTL_RAW.CAST_TO_VARCHAR2(v_raw)
- EXCEPTION WHEN OTHERS → RETURN '***DECRYPT_ERROR***'

External calls: DBMS_CRYPTO.DECRYPT, HEXTORAW, UTL_RAW.CAST_TO_VARCHAR2

---

**PROCEDURE change_password(p_emp_id NUMBER, p_old_password VARCHAR2, p_new_password VARCHAR2)**

Logic:
1. IF LENGTH(p_new_password) < 8 → RAISE_APPLICATION_ERROR(-20310, 'Password must be at least 8 characters')
2. IF NOT REGEXP_LIKE(p_new_password, '[A-Z]') → RAISE_APPLICATION_ERROR(-20311, 'Password must contain an uppercase letter')
3. IF NOT REGEXP_LIKE(p_new_password, '[0-9]') → RAISE_APPLICATION_ERROR(-20312, 'Password must contain a number')
4. PKG_AUDIT.log_action('USER_CREDENTIALS', p_emp_id, 'UPDATE', USER)

Password complexity rules:
- Minimum length: 8 characters
- Must contain at least one uppercase letter [A-Z]
- Must contain at least one digit [0-9]
- No maximum length constraint
- No special character requirement
- Old password is accepted as parameter but not verified (stub implementation — actual update to USER_CREDENTIALS not implemented)

External service calls: PKG_AUDIT.log_action
Exceptions thrown: -20310 (too short), -20311 (no uppercase), -20312 (no number)


- No status pre-check; any run can be reversed
- p_reason parameter accepted but not stored (no column update with it)
- Both run and all detail lines marked 'REVERSED'

Database references:
- Table: PAYROLL_RUNS; columns: RUN_ID, STATUS, MODIFIED_BY, MODIFIED_DATE
- Table: PAYROLL_DETAILS; columns: RUN_ID, STATUS

External services called:
- PKG_AUDIT.log_action

---

**FUNCTION calculate_federal_tax(...) RETURN NUMBER**

Logic:
1. v_periods := CASE p_pay_frequency WHEN 'WEEKLY' THEN 52 WHEN 'BIWEEKLY' THEN 26 WHEN 'SEMIMONTHLY' THEN 24 WHEN 'MONTHLY' THEN 12 ELSE 12 END
2. v_annualized := p_taxable_income * v_periods
3. v_std_deduction := CASE WHEN p_filing_status IN ('MARRIED_JOINT') THEN 29200 ELSE 14600 END
4. v_taxable := v_annualized - v_std_deduction - (p_allowances * 4300)
5. IF v_taxable <= 0 THEN RETURN 0
6. Apply 2024 brackets:

**SINGLE / MARRIED_SEPARATE brackets (2024, annualized taxable income):**
| Bracket | Income Range | Tax |
|---|---|---|
| 1 | 0 – 11,600 | taxable × 0.10 |
| 2 | 11,600.01 – 47,150 | 1,160 + (taxable − 11,600) × 0.12 |
| 3 | 47,150.01 – 100,525 | 5,426 + (taxable − 47,150) × 0.22 |
| 4 | 100,525.01 – 191,950 | 17,168.50 + (taxable − 100,525) × 0.24 |
| 5 | 191,950.01 – 243,725 | 39,110.50 + (taxable − 191,950) × 0.32 |
| 6 | 243,725.01 – 609,350 | 55,678.50 + (taxable − 243,725) × 0.35 |
| 7 | 609,350.01 + | 183,647.25 + (taxable − 609,350) × 0.37 |

**MARRIED_JOINT brackets (2024, annualized taxable income):**
| Bracket | Income Range | Tax |
|---|---|---|
| 1 | 0 – 23,200 | taxable × 0.10 |
| 2 | 23,200.01 – 94,300 | 2,320 + (taxable − 23,200) × 0.12 |
| 3 | 94,300.01 – 201,050 | 10,852 + (taxable − 94,300) × 0.22 |
| 4 | 201,050.01 – 383,900 | 34,337 + (taxable − 201,050) × 0.24 |
| 5 | 383,900.01 – 487,450 | 78,221 + (taxable − 383,900) × 0.32 |
| 6 | 487,450.01 – 731,200 | 111,357 + (taxable − 487,450) × 0.35 |
| 7 | 731,200.01 + | 196,669.50 + (taxable − 731,200) × 0.37 |

7. v_tax := ROUND(v_tax / v_periods, 2)
8. v_tax := v_tax + NVL(p_additional_wh, 0)
9. RETURN v_tax

Business rules:
- Income is annualized first, then de-annualized after bracket calculation
- Standard deduction: 29,200 for MARRIED_JOINT; 14,600 for all others (SINGLE, MARRIED_SEPARATE, or any other value)
- Each allowance reduces annualized taxable income by exactly 4,300
- If v_taxable <= 0 after deductions and allowances, tax = 0
- Additional withholding (from W-4) added per-period after de-annualizing
- Filing status not in SINGLE/MARRIED_SEPARATE/MARRIED_JOINT yields v_tax = 0 (no branch matches)
- Note: TODO in code — should read from TAX_BRACKETS table instead of hard-coded values

---

**FUNCTION calculate_state_tax(...) RETURN NUMBER**

Logic:
1. v_rate := CASE p_state_code WHEN 'CA' THEN 0.0725 WHEN 'NY' THEN 0.0685 WHEN 'TX' THEN 0 WHEN 'FL' THEN 0 WHEN 'WA' THEN 0 WHEN 'IL' THEN 0.0495 WHEN 'PA' THEN 0.0307 WHEN 'OH' THEN 0.04 WHEN 'NJ' THEN 0.0637 WHEN 'MA' THEN 0.05 ELSE 0.05 END
2. RETURN ROUND(p_taxable_income * v_rate, 2)

**State flat rate table:**
| State | Rate |
|---|---|
| CA | 7.25% |
| NY | 6.85% |
| TX | 0% (no state income tax) |
| FL | 0% (no state income tax) |
| WA | 0% (no state income tax) |
| IL | 4.95% |
| PA | 3.07% |
| OH | 4.00% |
| NJ | 6.37% |
| MA | 5.00% |
| All others | 5.00% (default) |

Business rules:
- Simplified flat rates — noted in code that actual implementation would be bracket-based
- p_allowances and p_filing_status parameters accepted but NOT used in calculation
- Unknown states default to 5.00%
- Applied directly to per-period taxable income (not annualized)

---

**FUNCTION calculate_fica(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER**

Logic:
1. IF p_ytd_gross >= 168600 THEN RETURN 0 — already exceeded 2024 SS wage base
2. v_taxable := LEAST(p_gross_pay, 168600 - p_ytd_gross) — cap at remaining wage base
3. RETURN ROUND(v_taxable * 0.062, 2)

Business rules:
- 2024 Social Security wage base: **168,600**
- Employee rate: **6.2%** (0.062)
- Once YTD gross >= 168,600, no further SS tax withheld
- Partial period handling: only taxes wages up to the wage base ceiling

---

**FUNCTION calculate_medicare(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER**

Logic:
1. v_base_tax := ROUND(p_gross_pay * 0.0145, 2)
2. IF p_ytd_gross + p_gross_pay > 200000 THEN:
   - IF p_ytd_gross >= 200000 THEN: v_addl_tax := ROUND(p_gross_pay * 0.009, 2)
   - ELSE: v_addl_tax := ROUND((p_ytd_gross + p_gross_pay - 200000) * 0.009, 2)
3. RETURN v_base_tax + v_addl_tax

Business rules:
- Base Medicare rate: **1.45%** (0.0145) — no wage base cap
- Additional Medicare rate: **0.9%** (0.009) on wages above **200,000**
- Partial-period threshold crossing: only the amount above 200,000 in the current period is taxed at additional rate
- Additional tax threshold: 200,000 (note: IRS threshold is actually 200,000 for single/250,000 for MFJ — code uses single flat threshold for all filing statuses)

---

**PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)**

Logic:
1. OPEN p_cursor FOR: SELECT pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME, pp.PERIOD_NAME, SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY, SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','TAX','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS, SUM(pd.AMOUNT) AS NET_PAY, SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX, SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY, SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE, 0 AS YTD_GROSS, 0 AS YTD_NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND (p_emp_id IS NULL OR pd.EMP_ID = p_emp_id) GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME ORDER BY e.LAST_NAME

Business rules:
- YTD_GROSS and YTD_NET are hard-coded to 0 (placeholder — not yet implemented)
- Tax breakdown uses fixed ELEMENT_ID assignments: 100=federal, 101=state, 102=SS, 103=Medicare
- Excludes ERROR status payroll details
- Optional filter by p_emp_id; if NULL returns all employees in the run

Database references:
- Table: PAYROLL_DETAILS; columns: EMP_ID, RUN_ID, ELEMENT_TYPE, ELEMENT_ID, AMOUNT, STATUS
- Table: EMPLOYEES; columns: EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME
- Table: PAYROLL_RUNS; columns: RUN_ID, PERIOD_ID
- Table: PAY_PERIODS; columns: PERIOD_ID, PERIOD_NAME

---

**FUNCTION get_ytd_earnings(p_emp_id IN NUMBER, p_tax_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
1. SELECT NVL(SUM(pd.AMOUNT), 0) INTO v_ytd FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.EMP_ID = p_emp_id AND pd.ELEMENT_TYPE = 'EARNING' AND pd.STATUS = 'CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
2. RETURN v_ytd

Business rules:
- YTD uses PERIOD_START_DATE year for tax year assignment
- Only STATUS = 'CALCULATED' records counted (excludes REVERSED, ERROR)
- Only ELEMENT_TYPE = 'EARNING' amounts summed

Database references:
- Table: PAYROLL_DETAILS; columns: EMP_ID, RUN_ID, ELEMENT_TYPE, AMOUNT, STATUS
- Table: PAYROLL_RUNS; columns: RUN_ID, PERIOD_ID
- Table: PAY_PERIODS; columns: PERIOD_ID, PERIOD_START_DATE

---

**PROCEDURE generate_pay_register(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT pp.PERIOD_NAME FROM PAYROLL_RUNS pr JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pr.RUN_ID = p_run_id
2. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS') || '.csv'
3. UTL_FILE.FOPEN('PAYROLL_OUTPUT', v_filename, 'W', 32767)
4. Write CSV header: 'EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY'
5. Query: SELECT e.EMP_NUMBER, e.FIRST_NAME||' '||e.LAST_NAME AS EMP_NAME, d.DEPT_NAME, SUM(EARNING amounts) AS GROSS, SUM(ELEMENT_ID=100) AS FED, SUM(ELEMENT_ID=101) AS STATE, SUM(ELEMENT_ID=102) AS SS, SUM(ELEMENT_ID=103) AS MED, SUM(DEDUCTION/BENEFIT amounts) AS DEDS, SUM(all AMOUNT) AS NET FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e JOIN DEPARTMENTS d WHERE RUN_ID = p_run_id AND STATUS != 'ERROR' GROUP BY EMP_NUMBER, EMP_NAME, DEPT_NAME ORDER BY LAST_NAME
6. Write each row: EMP_NUMBER,"EMP_NAME","DEPT_NAME",GROSS,FED,STATE,SS,MED,DEDS,NET (amounts formatted with 'FM999999990.00')
7. UTL_FILE.FCLOSE; DBMS_OUTPUT.PUT_LINE('Pay register generated: ' || v_filename)
8. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

Business rules:
- Output directory Oracle object name: 'PAYROLL_OUTPUT'
- Filename format: PAY_REGISTER_{run_id}_{YYYYMMDD_HH24MISS}.csv
- CSV — EMPLOYEE_NAME and DEPT_NAME are double-quoted; numeric amounts are not quoted
- Amount format mask: 'FM999999990.00'
- File buffer: 32767 bytes

Database references:
- Table: PAYROLL_RUNS; columns: RUN_ID, PERIOD_ID
- Table: PAY_PERIODS; columns: PERIOD_ID, PERIOD_NAME
- Table: PAYROLL_DETAILS; columns: RUN_ID, EMP_ID, ELEMENT_TYPE, ELEMENT_ID, AMOUNT, STATUS
- Table: EMPLOYEES; columns: EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID
- Table: DEPARTMENTS; columns: DEPT_ID, DEPT_NAME

External services called:
- UTL_FILE (Oracle directory: PAYROLL_OUTPUT)
- PKG_COMMON.log_error

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks ===

**Package:** HRMS.PKG_PERFORMANCE
**Type:** Package Specification

**Type Definitions:**
`t_review_cursor IS REF CURSOR`

**Public Method Signatures:**

`FUNCTION create_review_cycle(p_cycle_name IN VARCHAR2, p_cycle_year IN NUMBER, p_start_date IN DATE, p_end_date IN DATE, p_self_review_due IN DATE DEFAULT NULL, p_manager_review_due IN DATE DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE open_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE close_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)`

`FUNCTION create_review(p_cycle_id IN NUMBER, p_emp_id IN NUMBER, p_reviewer_emp_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE submit_self_assessment(p_review_id IN NUMBER, p_self_assessment IN CLOB, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE submit_manager_review(p_review_id IN NUMBER, p_overall_rating IN NUMBER, p_manager_assessment IN CLOB, p_strengths IN CLOB DEFAULT NULL, p_improvement_areas IN CLOB DEFAULT NULL, p_development_plan IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE acknowledge_review(p_review_id IN NUMBER, p_emp_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)`

`FUNCTION add_goal(p_review_id IN NUMBER, p_emp_id IN NUMBER, p_goal_title IN VARCHAR2, p_goal_description IN CLOB DEFAULT NULL, p_goal_category IN VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct IN NUMBER DEFAULT 0, p_target_date IN DATE DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER`

`PROCEDURE update_goal_progress(p_goal_id IN NUMBER, p_progress_pct IN NUMBER, p_status IN VARCHAR2 DEFAULT NULL, p_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)`

`PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id IN NUMBER, p_cycle_id IN NUMBER)`

`FUNCTION get_rating_distribution(p_cycle_id IN NUMBER, p_dept_id IN NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR`

`PROCEDURE generate_reviews_for_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)`

**Dependencies declared in spec comments:**
- PKG_EMPLOYEE
- PKG_COMMON
- PKG_AUDIT
- PKG_NOTIFICATION

**Callers declared in spec comments:**
- HRMS_PERFORMANCE form
- batch calibration job

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb ===

**Package:** HRMS.PKG_PERFORMANCE
**Type:** Package Body

---

**FUNCTION create_review_cycle(...) RETURN NUMBER**

Logic:
1. SELECT SEQ_REVIEW_CYCLE.NEXTVAL INTO v_cycle_id FROM DUAL
2. INSERT INTO REVIEW_CYCLES (CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_cycle_id, p_cycle_name, p_cycle_year, p_start_date, p_end_date, p_self_review_due, p_manager_review_due, 'DRAFT', p_user, SYSDATE)
3. PKG_AUDIT.log_action('REVIEW_CYCLES', v_cycle_id, 'INSERT', p_user)
4. RETURN v_cycle_id

Business rules:
- Initial status: 'DRAFT'

Database references:
- Table: REVIEW_CYCLES; columns: CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, START_DATE, END_DATE, SELF_REVIEW_DUE, MANAGER_REVIEW_DUE, STATUS, CREATED_BY, CREATED_DATE
- Sequence: SEQ_REVIEW_CYCLE

External services called:
- PKG_AUDIT.log_action

---

**PROCEDURE open_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE REVIEW_CYCLES SET STATUS = 'OPEN', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id AND STATUS = 'DRAFT'
2. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20401, 'Cannot open cycle - must be in DRAFT status')

Business rules:
- Only DRAFT cycles can be opened

Exceptions thrown:
- -20401: Cannot open cycle — must be in DRAFT status

Database references:
- Table: REVIEW_CYCLES; columns: CYCLE_ID, STATUS, MODIFIED_BY, MODIFIED_DATE

---

**PROCEDURE close_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE REVIEW_CYCLES SET STATUS = 'CLOSED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE CYCLE_ID = p_cycle_id

Business rules:
- No status pre-check — any cycle can be closed regardless of current status

Database references:
- Table: REVIEW_CYCLES; columns: CYCLE_ID, STATUS, MODIFIED_BY, MODIFIED_DATE

---

**FUNCTION create_review(p_cycle_id IN NUMBER, p_emp_id IN NUMBER, p_reviewer_emp_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER**

Logic:
1. SELECT SEQ_PERF_REVIEW.NEXTVAL INTO v_review_id FROM DUAL
2. INSERT INTO PERFORMANCE_REVIEWS (REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE) VALUES (v_review_id, p_cycle_id, p_emp_id, p_reviewer_emp_id, 'ANNUAL', 'NOT_STARTED', p_user, SYSDATE)
3. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => p_emp_id, p_type => 'EMAIL', p_subject => 'Performance Review Initiated', p_body => 'Your annual performance review has been initiated. Please complete your self-assessment.')
4. RETURN v_review_id

Business rules:
- REVIEW_TYPE always set to 'ANNUAL'
- Initial STATUS: 'NOT_STARTED'
- Employee notified on review creation

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, CYCLE_ID, EMP_ID, REVIEWER_EMP_ID, REVIEW_TYPE, STATUS, CREATED_BY, CREATED_DATE
- Sequence: SEQ_PERF_REVIEW

External services called:
- PKG_NOTIFICATION.send_notification

---

**PROCEDURE submit_self_assessment(p_review_id IN NUMBER, p_self_assessment IN CLOB, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_REVIEWS SET SELF_ASSESSMENT = p_self_assessment, STATUS = 'MANAGER_REVIEW', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS IN ('NOT_STARTED', 'SELF_REVIEW')
2. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20402, 'Review not found or not in correct status')
3. SELECT REVIEWER_EMP_ID INTO v_manager_id FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id
4. PKG_NOTIFICATION.send_notification(p_recipient_emp_id => v_manager_id, p_type => 'EMAIL', p_subject => 'Self-Assessment Submitted - Ready for Manager Review', p_body => 'An employee has completed their self-assessment. Please proceed with the manager review.')

Business rules:
- Self-assessment can be submitted from NOT_STARTED or SELF_REVIEW status
- Status transitions to 'MANAGER_REVIEW' on submission
- Manager notified on self-assessment submission

Exceptions thrown:
- -20402: Review not found or not in correct status

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, STATUS, SELF_ASSESSMENT, REVIEWER_EMP_ID, MODIFIED_BY, MODIFIED_DATE

External services called:
- PKG_NOTIFICATION.send_notification

---

**PROCEDURE submit_manager_review(...)**

Logic:
1. IF p_overall_rating < 1.0 OR p_overall_rating > 5.0 THEN RAISE_APPLICATION_ERROR(-20403, 'Rating must be between 1.0 and 5.0')
2. UPDATE PERFORMANCE_REVIEWS SET OVERALL_RATING = p_overall_rating, RATING_LABEL = CASE WHEN p_overall_rating >= 4.5 THEN 'Exceptional' WHEN p_overall_rating >= 3.5 THEN 'Exceeds Expectations' WHEN p_overall_rating >= 2.5 THEN 'Meets Expectations' WHEN p_overall_rating >= 1.5 THEN 'Needs Improvement' ELSE 'Unsatisfactory' END, MANAGER_ASSESSMENT = p_manager_assessment, STRENGTHS = p_strengths, AREAS_FOR_IMPROVEMENT = p_improvement_areas, DEVELOPMENT_PLAN = p_development_plan, STATUS = 'COMPLETED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id
3. SELECT EMP_ID INTO v_emp_id FROM PERFORMANCE_REVIEWS WHERE REVIEW_ID = p_review_id
4. PKG_NOTIFICATION.send_notification(employee, 'EMAIL', 'Performance Review Completed', 'Your manager has completed your performance review. Please review and acknowledge.')

Business rules — rating scale (1.0–5.0) and labels:
| Threshold | Label |
|---|---|
| >= 4.5 | Exceptional |
| >= 3.5 (and < 4.5) | Exceeds Expectations |
| >= 2.5 (and < 3.5) | Meets Expectations |
| >= 1.5 (and < 2.5) | Needs Improvement |
| < 1.5 (1.0–1.49) | Unsatisfactory |

- Rating must be between 1.0 and 5.0 (inclusive)
- No status pre-check on the UPDATE (any review can have manager assessment submitted)
- Status set to 'COMPLETED' on submission
- Employee notified by email

Exceptions thrown:
- -20403: Rating must be between 1.0 and 5.0

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, EMP_ID, OVERALL_RATING, RATING_LABEL, MANAGER_ASSESSMENT, STRENGTHS, AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN, STATUS, MODIFIED_BY, MODIFIED_DATE

External services called:
- PKG_NOTIFICATION.send_notification

---

**PROCEDURE acknowledge_review(p_review_id IN NUMBER, p_emp_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_REVIEWS SET EMPLOYEE_COMMENTS = p_emp_comments, EMPLOYEE_ACK_DATE = SYSDATE, STATUS = 'ACKNOWLEDGED', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE REVIEW_ID = p_review_id AND STATUS = 'COMPLETED'

Business rules:
- Only COMPLETED reviews can be acknowledged
- Silently does nothing if review not in COMPLETED status (no error raised)
- EMPLOYEE_ACK_DATE recorded as SYSDATE

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, STATUS, EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE, MODIFIED_BY, MODIFIED_DATE

---

**FUNCTION add_goal(...) RETURN NUMBER**

Logic:
1. SELECT SEQ_PERF_GOAL.NEXTVAL INTO v_goal_id FROM DUAL
2. INSERT INTO PERFORMANCE_GOALS (GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE) VALUES (v_goal_id, p_review_id, p_emp_id, p_goal_title, p_goal_description, p_goal_category, p_weight_pct, p_target_date, 'NOT_STARTED', 0, p_user, SYSDATE)
3. RETURN v_goal_id

Business rules:
- Initial status: 'NOT_STARTED'
- Initial PROGRESS_PCT: 0
- Default category: 'BUSINESS'
- Default weight: 0

Database references:
- Table: PERFORMANCE_GOALS; columns: GOAL_ID, REVIEW_ID, EMP_ID, GOAL_TITLE, GOAL_DESCRIPTION, GOAL_CATEGORY, WEIGHT_PCT, TARGET_DATE, STATUS, PROGRESS_PCT, CREATED_BY, CREATED_DATE
- Sequence: SEQ_PERF_GOAL

---

**PROCEDURE update_goal_progress(p_goal_id IN NUMBER, p_progress_pct IN NUMBER, p_status IN VARCHAR2 DEFAULT NULL, p_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PERFORMANCE_GOALS SET PROGRESS_PCT = p_progress_pct, STATUS = NVL(p_status, CASE WHEN p_progress_pct >= 100 THEN 'COMPLETED' WHEN p_progress_pct > 0 THEN 'IN_PROGRESS' ELSE STATUS END), COMMENTS = NVL(p_comments, COMMENTS), MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE GOAL_ID = p_goal_id

Business rules — auto status derivation (when p_status IS NULL):
- PROGRESS_PCT >= 100 → STATUS = 'COMPLETED'
- PROGRESS_PCT > 0 (and < 100) → STATUS = 'IN_PROGRESS'
- PROGRESS_PCT = 0 → STATUS unchanged
- p_status overrides auto-derivation when provided
- p_comments: NULL input preserves existing comment

Database references:
- Table: PERFORMANCE_GOALS; columns: GOAL_ID, PROGRESS_PCT, STATUS, COMMENTS, MODIFIED_BY, MODIFIED_DATE

---

**PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id IN NUMBER, p_cycle_id IN NUMBER)**

Logic:
1. OPEN p_cursor FOR: SELECT pr.REVIEW_ID, pr.EMP_ID, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME, j.JOB_TITLE, d.DEPT_NAME, pr.STATUS, pr.OVERALL_RATING, pr.RATING_LABEL FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID WHERE pr.REVIEWER_EMP_ID = p_manager_id AND pr.CYCLE_ID = p_cycle_id ORDER BY e.LAST_NAME

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, EMP_ID, REVIEWER_EMP_ID, CYCLE_ID, STATUS, OVERALL_RATING, RATING_LABEL
- Table: EMPLOYEES; columns: EMP_ID, FIRST_NAME, LAST_NAME, JOB_ID, DEPT_ID
- Table: JOB_TITLES; columns: JOB_ID, JOB_TITLE
- Table: DEPARTMENTS; columns: DEPT_ID, DEPT_NAME

---

**FUNCTION get_rating_distribution(p_cycle_id IN NUMBER, p_dept_id IN NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR**

Logic:
1. OPEN v_cursor FOR: SELECT pr.RATING_LABEL, COUNT(*) AS COUNT, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE FROM PERFORMANCE_REVIEWS pr JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID WHERE pr.CYCLE_ID = p_cycle_id AND pr.OVERALL_RATING IS NOT NULL AND (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id) GROUP BY pr.RATING_LABEL ORDER BY MIN(pr.OVERALL_RATING) DESC
2. RETURN v_cursor

Business rules:
- Only reviews with non-null OVERALL_RATING included
- Percentage calculated using analytic SUM OVER () — window over all returned groups
- Percentage rounded to 1 decimal place
- Ordered by MIN(OVERALL_RATING) DESC — places 'Exceptional' first

Database references:
- Table: PERFORMANCE_REVIEWS; columns: REVIEW_ID, CYCLE_ID, EMP_ID, RATING_LABEL, OVERALL_RATING
- Table: EMPLOYEES; columns: EMP_ID, DEPT_ID

---

**PROCEDURE generate_reviews_for_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. Loop: SELECT EMP_ID, MANAGER_EMP_ID FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' AND MANAGER_EMP_ID IS NOT NULL
2. For each employee: v_review_id := create_review(p_cycle_id, EMP_ID, MANAGER_EMP_ID, p_user); v_count++
3. EXCEPTION WHEN DUP_VAL_ON_INDEX: NULL (review already exists — skip)
4. COMMIT
5. DBMS_OUTPUT.PUT_LINE('Generated ' || v_count || ' reviews for cycle ' || p_cycle_id)

Business rules:
- Only active employees with a manager are assigned reviews
- Top-level employees (MANAGER_EMP_ID IS NULL) are excluded
- Idempotent: duplicate reviews silently skipped via DUP_VAL_ON_INDEX handler
- Bulk commit at end (single COMMIT after all employees processed)

Database references:
- Table: EMPLOYEES; columns: EMP_ID, EMPLOYMENT_STATUS, MANAGER_EMP_ID

---

**Complete cross-package dependency map:**

| Package | Calls |
|---|---|
| PKG_EMPLOYEE | PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification, PKG_COMMON.log_error |
| PKG_PAYROLL | PKG_AUDIT.log_action, PKG_COMMON.log_error, PKG_COMMON.log_info |
| PKG_LEAVE | PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action |
| PKG_INTEGRATION | PKG_COMMON.log_info, PKG_COMMON.log_error, PKG_COMMON.get_param |
| PKG_NOTIFICATION | PKG_COMMON.log_error |
| PKG_PERFORMANCE | PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action |

**Circular dependency:** PKG_EMPLOYEE → PKG_PAYROLL.create_salary_record; PKG_PAYROLL may call PKG_EMPLOYEE.is_active for validation.

**Complete database table inventory:**

EMPLOYEES, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS, EMPLOYEE_PAY_ELEMENTS, EMPLOYEE_TAX_INFO, DEPARTMENTS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS, LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES, LEAVE_ACCRUAL_LOG, HOLIDAYS, PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS, PAY_ELEMENTS, NOTIFICATION_QUEUE, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS, REVIEW_CYCLES

**Complete sequence inventory:**

SEQ_EMPLOYEE, SEQ_EMP_HISTORY, SEQ_SALARY, SEQ_PAY_PERIOD, SEQ_PAYROLL_RUN, SEQ_PAYROLL_DETAIL, SEQ_LEAVE_REQUEST, SEQ_LEAVE_BALANCE, SEQ_LEAVE_ACCRUAL, SEQ_NOTIFICATION, SEQ_PERF_REVIEW, SEQ_PERF_GOAL, SEQ_REVIEW_CYCLE

**Oracle directory objects used:**

GL_FEED_OUT (GL journal output), BENEFITS_FEED_OUT (benefits export), TIME_ATTENDANCE_IN (time import), PAYROLL_OUTPUT (pay register)


=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks ===

**Package:** HRMS.PKG_EMPLOYEE
**Schema:** HRMS
**Type:** Package Specification

---

**Global Package Variables (session state):**
- `g_current_user` — VARCHAR2(30)
- `g_current_emp_id` — NUMBER(10)
- `g_current_dept_id` — NUMBER(10)
- `g_debug_mode` — BOOLEAN, default FALSE

---

**Custom Exceptions:**

| Name | Code | PRAGMA binding |
|---|---|---|
| e_employee_not_found | -20001 | PRAGMA EXCEPTION_INIT |
| e_duplicate_emp_number | -20002 | PRAGMA EXCEPTION_INIT |
| e_invalid_department | -20003 | PRAGMA EXCEPTION_INIT |
| e_invalid_manager | -20004 | PRAGMA EXCEPTION_INIT |
| e_termination_error | -20005 | PRAGMA EXCEPTION_INIT |

---

**Type Definitions:**

`TYPE t_emp_rec IS RECORD`:
- emp_id — EMPLOYEES.EMP_ID%TYPE
- emp_number — EMPLOYEES.EMP_NUMBER%TYPE
- first_name — EMPLOYEES.FIRST_NAME%TYPE
- last_name — EMPLOYEES.LAST_NAME%TYPE
- hire_date — EMPLOYEES.HIRE_DATE%TYPE
- dept_id — EMPLOYEES.DEPT_ID%TYPE
- job_id — EMPLOYEES.JOB_ID%TYPE
- manager_emp_id — EMPLOYEES.MANAGER_EMP_ID%TYPE
- employment_status — EMPLOYEES.EMPLOYMENT_STATUS%TYPE
- base_salary — NUMBER(12,2)

`TYPE t_emp_cursor IS REF CURSOR`

`TYPE t_emp_id_table IS TABLE OF NUMBER(10) INDEX BY BINARY_INTEGER`

`TYPE t_emp_rec_table IS TABLE OF t_emp_rec INDEX BY BINARY_INTEGER`

---

**Public Procedure/Function Signatures:**

| Name | Kind | Parameters | Returns |
|---|---|---|---|
| create_employee | FUNCTION | p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_manager_emp_id NUMBER DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_employment_type VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary NUMBER DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER |
| update_employee | PROCEDURE | p_emp_id NUMBER, p_first_name VARCHAR2 DEFAULT NULL, p_last_name VARCHAR2 DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_phone_work VARCHAR2 DEFAULT NULL, p_phone_mobile VARCHAR2 DEFAULT NULL, p_address_line1 VARCHAR2 DEFAULT NULL, p_address_line2 VARCHAR2 DEFAULT NULL, p_city VARCHAR2 DEFAULT NULL, p_state_province VARCHAR2 DEFAULT NULL, p_postal_code VARCHAR2 DEFAULT NULL, p_country_code VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| get_employee | FUNCTION | p_emp_id NUMBER | t_emp_rec |
| get_employee_by_number | FUNCTION | p_emp_number VARCHAR2 | t_emp_rec |
| search_employees | PROCEDURE | p_cursor OUT t_emp_cursor, p_last_name VARCHAR2 DEFAULT NULL, p_first_name VARCHAR2 DEFAULT NULL, p_dept_id NUMBER DEFAULT NULL, p_status VARCHAR2 DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_hire_date_from DATE DEFAULT NULL, p_hire_date_to DATE DEFAULT NULL | — |
| transfer_employee | PROCEDURE | p_emp_id NUMBER, p_new_dept_id NUMBER, p_new_job_id NUMBER DEFAULT NULL, p_new_manager_id NUMBER DEFAULT NULL, p_new_location VARCHAR2 DEFAULT NULL, p_effective_date DATE DEFAULT SYSDATE, p_reason_code VARCHAR2 DEFAULT NULL, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| promote_employee | PROCEDURE | p_emp_id NUMBER, p_new_job_id NUMBER, p_new_salary NUMBER, p_effective_date DATE DEFAULT SYSDATE, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| terminate_employee | PROCEDURE | p_emp_id NUMBER, p_termination_date DATE, p_reason VARCHAR2, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| rehire_employee | PROCEDURE | p_emp_id NUMBER, p_rehire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_base_salary NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_direct_reports | FUNCTION | p_manager_emp_id NUMBER | t_emp_id_table |
| get_org_chart | FUNCTION | p_root_emp_id NUMBER, p_max_depth NUMBER DEFAULT 10 | t_emp_cursor |
| get_headcount_by_dept | FUNCTION | p_dept_id NUMBER DEFAULT NULL, p_as_of_date DATE DEFAULT SYSDATE | NUMBER |
| get_tenure_years | FUNCTION | p_emp_id NUMBER | NUMBER |
| is_active | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| validate_employee | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| emp_exists | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| generate_emp_number | FUNCTION | (none) | VARCHAR2 |
| set_session_context | PROCEDURE | p_user VARCHAR2, p_emp_id NUMBER | — |

---

**Dependencies declared in header comments:**
- PKG_COMMON
- PKG_AUDIT
- PKG_NOTIFICATION
- PKG_PAYROLL

**Called by (per header):**
- HRMS_EMPLOYEE form
- HRMS_DEPARTMENT form
- Batch jobs

**Known issues (per header):**
- Circular dependency with PKG_PAYROLL (salary validation)
- get_org_chart uses recursive SQL that times out for deep hierarchies

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb ===

**Package:** HRMS.PKG_EMPLOYEE
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value |
|---|---|---|
| c_emp_number_prefix | VARCHAR2(3) | 'EMP' |
| c_max_hierarchy_depth | NUMBER | 15 |

---

**Private Forward Declarations:**
- PROCEDURE log_history (full signature below)
- PROCEDURE validate_dept(p_dept_id IN NUMBER)
- PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)
- FUNCTION get_next_emp_id RETURN NUMBER

---

### FUNCTION generate_emp_number RETURN VARCHAR2

**Logic:**
1. SELECT NVL(MAX(TO_NUMBER(SUBSTR(EMP_NUMBER, 5))), 0) + 1 INTO v_max_num FROM EMPLOYEES WHERE EMP_NUMBER LIKE c_emp_number_prefix || '-%' (i.e., LIKE 'EMP-%')
2. Construct: v_new_number := 'EMP' || '-' || LPAD(v_max_num, 6, '0')  — zero-padded to 6 digits, format EMP-NNNNNN
3. Return v_new_number
4. EXCEPTION WHEN OTHERS: fallback — RETURN 'EMP-' || LPAD(SEQ_EMPLOYEE.NEXTVAL, 6, '0')

**Known bug:** Race condition under concurrent inserts — no SELECT FOR UPDATE.

**Database tables accessed:** EMPLOYEES (read)
**Sequences used:** SEQ_EMPLOYEE (in exception fallback)

---

### FUNCTION get_next_emp_id RETURN NUMBER

**Logic:**
1. SELECT SEQ_EMPLOYEE.NEXTVAL INTO v_id FROM DUAL
2. RETURN v_id

**Sequences used:** SEQ_EMPLOYEE

---

### PROCEDURE validate_dept(p_dept_id IN NUMBER)

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id AND ACTIVE_FLAG = 'Y'
2. IF v_count = 0 THEN RAISE_APPLICATION_ERROR(-20003, 'Invalid or inactive department: ' || p_dept_id)

**Business rules:**
- Department must exist in DEPARTMENTS table with ACTIVE_FLAG = 'Y'

**Exceptions thrown:**
- -20003 'Invalid or inactive department: [id]' — department not found or ACTIVE_FLAG != 'Y'

**Database tables accessed:** DEPARTMENTS (read)

---

### PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)

**Logic:**
1. IF p_manager_id IS NULL THEN RETURN — NULL manager is valid (top-level employee)
2. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE EMP_ID = p_manager_id AND EMPLOYMENT_STATUS = 'ACTIVE'
3. IF v_count = 0 THEN RAISE_APPLICATION_ERROR(-20004, 'Invalid or inactive manager: ' || p_manager_id)
4. Circular reporting check (only when p_emp_id IS NOT NULL):
   - v_current_mgr := p_manager_id, v_depth := 0
   - WHILE v_current_mgr IS NOT NULL AND v_depth < 15 LOOP
     - IF v_current_mgr = p_emp_id THEN RAISE_APPLICATION_ERROR(-20004, 'Circular reporting chain detected: Employee [p_emp_id] cannot report to [p_manager_id]')
     - SELECT MANAGER_EMP_ID INTO v_current_mgr FROM EMPLOYEES WHERE EMP_ID = v_current_mgr; EXCEPTION WHEN NO_DATA_FOUND THEN v_current_mgr := NULL
     - v_depth := v_depth + 1
   - End loop at depth 15 (c_max_hierarchy_depth)

**Business rules:**
- Manager must exist in EMPLOYEES with EMPLOYMENT_STATUS = 'ACTIVE'
- Circular reporting chains are forbidden; checked up to depth 15

**Exceptions thrown:**
- -20004 'Invalid or inactive manager: [id]'
- -20004 'Circular reporting chain detected: Employee [id] cannot report to [id]'

**Database tables accessed:** EMPLOYEES (read — two separate queries)

---

### PROCEDURE log_history (PRAGMA AUTONOMOUS_TRANSACTION)

**Signature:**
```
p_emp_id        IN NUMBER,
p_change_type   IN VARCHAR2,
p_effective_date IN DATE,
p_old_dept_id   IN NUMBER DEFAULT NULL,
p_new_dept_id   IN NUMBER DEFAULT NULL,
p_old_job_id    IN NUMBER DEFAULT NULL,
p_new_job_id    IN NUMBER DEFAULT NULL,
p_old_manager   IN NUMBER DEFAULT NULL,
p_new_manager   IN NUMBER DEFAULT NULL,
p_old_salary    IN NUMBER DEFAULT NULL,
p_new_salary    IN NUMBER DEFAULT NULL,
p_old_location  IN VARCHAR2 DEFAULT NULL,
p_new_location  IN VARCHAR2 DEFAULT NULL,
p_reason_code   IN VARCHAR2 DEFAULT NULL,
p_comments      IN VARCHAR2 DEFAULT NULL,
p_user          IN VARCHAR2 DEFAULT USER
```

**Logic:**
1. INSERT INTO EMPLOYEE_HISTORY (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE) VALUES (SEQ_EMP_HISTORY.NEXTVAL, ...)
2. COMMIT
3. EXCEPTION WHEN OTHERS: ROLLBACK; IF g_debug_mode THEN print warning; END IF — history logging never fails the main transaction

**PRAGMA:** AUTONOMOUS_TRANSACTION — runs in its own transaction, independent of caller

**Sequences used:** SEQ_EMP_HISTORY

**Database tables written:** EMPLOYEE_HISTORY

---

### FUNCTION create_employee(...) RETURN NUMBER

**Full parameter list:**
- p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_manager_emp_id NUMBER DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_employment_type VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary NUMBER DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic (step by step):**
1. Validate: IF p_first_name IS NULL OR p_last_name IS NULL THEN RAISE_APPLICATION_ERROR(-20010, 'First name and last name are required')
2. Call validate_dept(p_dept_id)
3. Call validate_manager(p_manager_emp_id) — NULL is allowed
4. Validate job: SELECT GRADE_ID INTO v_grade_id FROM JOB_TITLES WHERE JOB_ID = p_job_id AND ACTIVE_FLAG = 'Y'; EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20011, 'Invalid or inactive job: ' || p_job_id)
5. Validate salary vs grade range (soft warning only, not an error):
   - IF p_base_salary IS NOT NULL THEN
     - SELECT MIN_SALARY, MAX_SALARY INTO v_min, v_max FROM JOB_GRADES WHERE GRADE_ID = v_grade_id
     - IF p_base_salary < v_min OR p_base_salary > v_max THEN IF g_debug_mode THEN print warning (no error raised — soft check, override allowed with manager approval)
6. Determine location: IF p_location_code IS NULL THEN SELECT LOCATION_CODE INTO v_location FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id; ELSE v_location := p_location_code
7. v_emp_id := get_next_emp_id()
8. v_emp_number := generate_emp_number()
9. INSERT INTO EMPLOYEES: EMP_ID=v_emp_id, EMP_NUMBER=v_emp_number, FIRST_NAME=UPPER(TRIM(p_first_name)), LAST_NAME=UPPER(TRIM(p_last_name)), HIRE_DATE=p_hire_date, DEPT_ID=p_dept_id, JOB_ID=p_job_id, MANAGER_EMP_ID=p_manager_emp_id, LOCATION_CODE=v_location, EMPLOYMENT_TYPE=p_employment_type, EMPLOYMENT_STATUS='ACTIVE', EMAIL=LOWER(TRIM(p_email)), ACTIVE_FLAG='Y', CREATED_BY=p_user, CREATED_DATE=SYSDATE
10. IF p_base_salary IS NOT NULL THEN call PKG_PAYROLL.create_salary_record(p_emp_id=>v_emp_id, p_effective_date=>p_hire_date, p_base_salary=>p_base_salary, p_change_reason=>'NEW_HIRE', p_user=>p_user)
11. Call log_history(p_emp_id=>v_emp_id, p_change_type=>'HIRE', p_effective_date=>p_hire_date, p_new_dept_id, p_new_job_id, p_new_manager, p_new_salary, p_new_location, p_user)
12. Call PKG_AUDIT.log_action(p_table_name=>'EMPLOYEES', p_record_id=>v_emp_id, p_action=>'INSERT', p_user=>p_user)
13. Call PKG_NOTIFICATION.send_notification(p_recipient_emp_id=>v_emp_id, p_type=>'EMAIL', p_subject=>'Welcome to the Company', p_body=>'Dear [first_name], Welcome aboard! Your employee number is [emp_number].', p_user=>p_user)
14. IF p_manager_emp_id IS NOT NULL THEN call PKG_NOTIFICATION.send_notification to manager with subject='New Direct Report: [first] [last]', body='[first] [last] has been added as your direct report, starting [hire_date MM/DD/YYYY].'
15. RETURN v_emp_id
16. EXCEPTION WHEN DUP_VAL_ON_INDEX THEN RAISE_APPLICATION_ERROR(-20002, 'Duplicate employee number generated. Please retry.')
17. EXCEPTION WHEN OTHERS THEN call PKG_COMMON.log_error('PKG_EMPLOYEE','create_employee',SQLERRM,p_user); RAISE

**Business rules:**
- First name and last name are required (not null)
- Department must be valid and active
- Manager (if provided) must be active; no circular chains
- Job must be active in JOB_TITLES
- Salary range check is a soft warning only; override is allowed with manager approval
- First name and last name stored as UPPER(TRIM(...))
- Email stored as LOWER(TRIM(...))
- Default EMPLOYMENT_TYPE = 'FULL_TIME'
- Default EMPLOYMENT_STATUS = 'ACTIVE' on creation
- Default ACTIVE_FLAG = 'Y' on creation
- Location defaults from department if not specified

**Exceptions thrown:**
- -20010 'First name and last name are required'
- -20003 (from validate_dept)
- -20004 (from validate_manager)
- -20011 'Invalid or inactive job: [id]'
- -20002 'Duplicate employee number generated. Please retry.'

**External services called:**
- PKG_PAYROLL.create_salary_record (if salary provided)
- PKG_AUDIT.log_action
- PKG_NOTIFICATION.send_notification (to employee and, conditionally, to manager)
- PKG_COMMON.log_error (on error)

**Sequences used:** SEQ_EMPLOYEE (via get_next_emp_id, generate_emp_number)

**Database tables written:** EMPLOYEES

**Known issue:** Circular dependency — calls PKG_PAYROLL.create_salary_record which may call PKG_EMPLOYEE.is_active for validation.

---

### PROCEDURE update_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_first_name VARCHAR2 DEFAULT NULL, p_last_name VARCHAR2 DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_phone_work VARCHAR2 DEFAULT NULL, p_phone_mobile VARCHAR2 DEFAULT NULL, p_address_line1 VARCHAR2 DEFAULT NULL, p_address_line2 VARCHAR2 DEFAULT NULL, p_city VARCHAR2 DEFAULT NULL, p_state_province VARCHAR2 DEFAULT NULL, p_postal_code VARCHAR2 DEFAULT NULL, p_country_code VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. IF NOT emp_exists(p_emp_id) THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)
2. UPDATE EMPLOYEES SET FIRST_NAME=NVL(UPPER(TRIM(p_first_name)),FIRST_NAME), LAST_NAME=NVL(UPPER(TRIM(p_last_name)),LAST_NAME), EMAIL=NVL(LOWER(TRIM(p_email)),EMAIL), PHONE_WORK=NVL(p_phone_work,PHONE_WORK), PHONE_MOBILE=NVL(p_phone_mobile,PHONE_MOBILE), ADDRESS_LINE1=NVL(p_address_line1,ADDRESS_LINE1), ADDRESS_LINE2=NVL(p_address_line2,ADDRESS_LINE2), CITY=NVL(p_city,CITY), STATE_PROVINCE=NVL(p_state_province,STATE_PROVINCE), POSTAL_CODE=NVL(p_postal_code,POSTAL_CODE), COUNTRY_CODE=NVL(p_country_code,COUNTRY_CODE), MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
3. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20001, 'Employee update failed: ' || p_emp_id)
4. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

**Business rules:**
- Partial update pattern — only non-NULL parameters overwrite existing values (NVL pattern)
- FIRST_NAME and LAST_NAME stored as UPPER(TRIM(...))
- EMAIL stored as LOWER(TRIM(...))
- Employee must exist

**Exceptions thrown:**
- -20001 'Employee not found: [id]'
- -20001 'Employee update failed: [id]'

**Database tables written:** EMPLOYEES

---

### FUNCTION get_employee(p_emp_id IN NUMBER) RETURN t_emp_rec

**Logic:**
1. SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, e.JOB_ID, e.MANAGER_EMP_ID, e.EMPLOYMENT_STATUS, (subquery for BASE_SALARY) INTO v_rec FROM EMPLOYEES e WHERE e.EMP_ID = p_emp_id
2. Subquery for BASE_SALARY: SELECT sr.BASE_SALARY FROM SALARY_RECORDS sr WHERE sr.EMP_ID = e.EMP_ID AND sr.ACTIVE_FLAG = 'Y' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE) AND ROWNUM = 1
3. RETURN v_rec
4. EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)

**Business rules:**
- Current salary = SALARY_RECORDS where ACTIVE_FLAG='Y' AND EFFECTIVE_DATE <= SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE), first row only (ROWNUM=1, no ORDER BY — non-deterministic if multiple rows)

**Exceptions thrown:**
- -20001 'Employee not found: [id]'

**Database tables accessed:** EMPLOYEES, SALARY_RECORDS

---

### FUNCTION get_employee_by_number(p_emp_number IN VARCHAR2) RETURN t_emp_rec

**Logic:**
1. SELECT EMP_ID INTO v_emp_id FROM EMPLOYEES WHERE EMP_NUMBER = p_emp_number
2. RETURN get_employee(v_emp_id)
3. EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_number)

**Database tables accessed:** EMPLOYEES

---

### PROCEDURE search_employees(...)

**Full parameter list:**
- p_cursor OUT t_emp_cursor, p_last_name VARCHAR2 DEFAULT NULL, p_first_name VARCHAR2 DEFAULT NULL, p_dept_id NUMBER DEFAULT NULL, p_status VARCHAR2 DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_hire_date_from DATE DEFAULT NULL, p_hire_date_to DATE DEFAULT NULL

**Logic — dynamic SQL construction:**
1. Base query:
   ```
   SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, d.DEPT_NAME, j.JOB_TITLE, e.EMPLOYMENT_STATUS, e.LOCATION_CODE
   FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE 1=1
   ```
2. IF p_last_name IS NOT NULL: append `AND UPPER(e.LAST_NAME) LIKE UPPER('` || p_last_name || `%')`
3. IF p_first_name IS NOT NULL: append `AND UPPER(e.FIRST_NAME) LIKE UPPER('` || p_first_name || `%')`
4. IF p_dept_id IS NOT NULL: append `AND e.DEPT_ID = ` || p_dept_id
5. IF p_status IS NOT NULL: append `AND e.EMPLOYMENT_STATUS = '` || p_status || `'`
6. IF p_location_code IS NOT NULL: append `AND e.LOCATION_CODE = '` || p_location_code || `'`
7. IF p_hire_date_from IS NOT NULL: append `AND e.HIRE_DATE >= TO_DATE('` || TO_CHAR(p_hire_date_from,'YYYY-MM-DD') || `','YYYY-MM-DD')`
8. IF p_hire_date_to IS NOT NULL: append `AND e.HIRE_DATE <= TO_DATE('` || TO_CHAR(p_hire_date_to,'YYYY-MM-DD') || `','YYYY-MM-DD')`
9. Append `ORDER BY e.LAST_NAME, e.FIRST_NAME`
10. OPEN p_cursor FOR v_sql (dynamic)

**SECURITY VULNERABILITY:** String concatenation for p_last_name and p_first_name instead of bind variables — SQL injection possible via those parameters. Note in code: "Forms LOV passes validated values, but direct calls are vulnerable."

**Database tables accessed:** EMPLOYEES, DEPARTMENTS, JOB_TITLES

---

### PROCEDURE transfer_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_new_dept_id NUMBER, p_new_job_id NUMBER DEFAULT NULL, p_new_manager_id NUMBER DEFAULT NULL, p_new_location VARCHAR2 DEFAULT NULL, p_effective_date DATE DEFAULT SYSDATE, p_reason_code VARCHAR2 DEFAULT NULL, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT * INTO v_old_rec FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE NOWAIT
2. IF v_old_rec.EMPLOYMENT_STATUS != 'ACTIVE' THEN RAISE_APPLICATION_ERROR(-20012, 'Cannot transfer non-active employee. Status: ' || v_old_rec.EMPLOYMENT_STATUS)
3. Call validate_dept(p_new_dept_id)
4. v_new_job_id := NVL(p_new_job_id, v_old_rec.JOB_ID) — defaults to current job if not provided
5. v_new_location := NVL(p_new_location, v_old_rec.LOCATION_CODE) — defaults to current location
6. IF p_new_manager_id IS NOT NULL THEN call validate_manager(p_new_manager_id, p_emp_id) — circular check included
7. UPDATE EMPLOYEES SET DEPT_ID=p_new_dept_id, JOB_ID=v_new_job_id, MANAGER_EMP_ID=NVL(p_new_manager_id, MANAGER_EMP_ID), LOCATION_CODE=v_new_location, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
8. Call log_history with CHANGE_TYPE='TRANSFER', old and new values for dept, job, manager, location
9. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error('PKG_EMPLOYEE','transfer_employee',SQLERRM,p_user); RAISE

**Business rules:**
- Only ACTIVE employees can be transferred
- Row-level locking with NOWAIT (fails immediately if locked)
- Job defaults to current if not specified
- Location defaults to current if not specified
- Manager validation (including circular chain check) only if new manager explicitly provided

**Exceptions thrown:**
- -20012 'Cannot transfer non-active employee. Status: [status]'
- -20003 (from validate_dept)
- -20004 (from validate_manager)

**Database tables accessed/written:** EMPLOYEES (lock + update), EMPLOYEE_HISTORY (via log_history)

---

### PROCEDURE promote_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_new_job_id NUMBER, p_new_salary NUMBER, p_effective_date DATE DEFAULT SYSDATE, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT JOB_ID INTO v_old_job_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. Get current salary: SELECT BASE_SALARY INTO v_old_salary FROM SALARY_RECORDS WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' AND ROWNUM=1 ORDER BY EFFECTIVE_DATE DESC; EXCEPTION WHEN NO_DATA_FOUND THEN v_old_salary := 0
3. UPDATE EMPLOYEES SET JOB_ID=p_new_job_id, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
4. Call PKG_PAYROLL.create_salary_record(p_emp_id, p_effective_date, p_new_salary, 'PROMOTION', p_change_pct=CASE WHEN v_old_salary > 0 THEN ROUND(((p_new_salary - v_old_salary) / v_old_salary) * 100, 2) ELSE NULL END, p_user)
5. Call log_history with CHANGE_TYPE='PROMOTION', old/new job_id, old/new salary
6. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

**Business rules:**
- Salary change percentage calculated as ROUND(((new - old) / old) * 100, 2) — only when old > 0
- No active-status check before promotion (contrast with transfer_employee)

**External services called:** PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action

**Database tables accessed/written:** EMPLOYEES (read + update), SALARY_RECORDS (read)

---

### PROCEDURE terminate_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_termination_date DATE, p_reason VARCHAR2, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE
2. IF v_emp.EMPLOYMENT_STATUS = 'TERMINATED' THEN RAISE_APPLICATION_ERROR(-20005, 'Employee [id] is already terminated')
3. SELECT COUNT(*) INTO v_pending_leave FROM LEAVE_REQUESTS WHERE EMP_ID=p_emp_id AND STATUS='PENDING'
4. IF v_pending_leave > 0 THEN UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON='Auto-cancelled due to termination', CANCELLED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND STATUS='PENDING'
5. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='TERMINATED', TERMINATION_DATE=p_termination_date, TERMINATION_REASON=p_reason, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
6. UPDATE SALARY_RECORDS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
7. UPDATE EMPLOYEE_PAY_ELEMENTS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
8. Call log_history with CHANGE_TYPE='TERMINATION'
9. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. IF v_emp.MANAGER_EMP_ID IS NOT NULL THEN call PKG_NOTIFICATION.send_notification to manager with subject='Employee Termination: [first] [last]', body='[first] [last] termination effective [date MM/DD/YYYY]'
11. TODOs noted: integrate with benefits system for COBRA, revoke system access via PKG_SECURITY, calculate final pay via PKG_PAYROLL.calculate_final_pay
12. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error; RAISE

**Business rules:**
- Cannot terminate an already-TERMINATED employee
- All PENDING leave requests are auto-cancelled with reason 'Auto-cancelled due to termination'
- All active salary records end-dated to p_termination_date
- All active pay elements end-dated to p_termination_date
- ACTIVE_FLAG set to 'N'
- Manager notified via email

**Exceptions thrown:**
- -20005 'Employee [id] is already terminated'

**Incomplete integrations (TODOs):**
- Benefits/COBRA
- PKG_SECURITY access revocation
- PKG_PAYROLL.calculate_final_pay

**Database tables accessed/written:** EMPLOYEES, LEAVE_REQUESTS, SALARY_RECORDS, EMPLOYEE_PAY_ELEMENTS, EMPLOYEE_HISTORY

---

### PROCEDURE rehire_employee(...)

**Full parameter list:**
- p_emp_id NUMBER, p_rehire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_base_salary NUMBER, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. Call validate_dept(p_dept_id)
2. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='ACTIVE', HIRE_DATE=p_rehire_date, TERMINATION_DATE=NULL, TERMINATION_REASON=NULL, DEPT_ID=p_dept_id, JOB_ID=p_job_id, ACTIVE_FLAG='Y', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
3. IF SQL%ROWCOUNT = 0 THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found for rehire: ' || p_emp_id)
4. Call PKG_PAYROLL.create_salary_record(p_emp_id, p_rehire_date, p_base_salary, 'REHIRE', p_user)
5. Call log_history with CHANGE_TYPE='REHIRE', new dept, job, salary
6. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

**Business rules:**
- HIRE_DATE is overwritten with p_rehire_date on rehire
- TERMINATION_DATE and TERMINATION_REASON are cleared (set to NULL)
- Department must be valid and active

**Exceptions thrown:**
- -20001 'Employee not found for rehire: [id]'
- -20003 (from validate_dept)

---

### FUNCTION get_direct_reports(p_manager_emp_id IN NUMBER) RETURN t_emp_id_table

**Logic:**
1. Initialize v_result (t_emp_id_table), v_idx := 0
2. FOR r IN (SELECT EMP_ID FROM EMPLOYEES WHERE MANAGER_EMP_ID = p_manager_emp_id AND EMPLOYMENT_STATUS = 'ACTIVE' ORDER BY LAST_NAME, FIRST_NAME) LOOP
   - v_idx := v_idx + 1; v_result(v_idx) := r.EMP_ID
3. RETURN v_result

**Business rules:**
- Only ACTIVE employees returned

**Database tables accessed:** EMPLOYEES

---

### FUNCTION get_org_chart(p_root_emp_id IN NUMBER, p_max_depth IN NUMBER DEFAULT 10) RETURN t_emp_cursor

**Logic:**
1. OPEN v_cursor FOR hierarchical query:
   ```
   SELECT LEVEL AS depth, EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID, JOB_ID, MANAGER_EMP_ID
   FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE'
   START WITH EMP_ID = p_root_emp_id
   CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID AND LEVEL <= p_max_depth
   ORDER SIBLINGS BY LAST_NAME, FIRST_NAME
   ```
2. RETURN v_cursor

**Business rules:**
- Only ACTIVE employees included
- Default max depth = 10
- Absolute max enforced via CONNECT BY condition

**Known bug:** Times out for orgs with >500 employees.

---

### FUNCTION get_headcount_by_dept(p_dept_id IN NUMBER DEFAULT NULL, p_as_of_date IN DATE DEFAULT SYSDATE) RETURN NUMBER

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE (p_dept_id IS NULL OR DEPT_ID = p_dept_id) AND EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= p_as_of_date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)
2. RETURN v_count

**Business rules:**
- If p_dept_id is NULL, counts all departments
- Excludes future hires (HIRE_DATE > as_of_date) and terminated employees whose termination date <= as_of_date

---

### FUNCTION get_tenure_years(p_emp_id IN NUMBER) RETURN NUMBER

**Logic:**
1. SELECT HIRE_DATE, NVL(TERMINATION_DATE, SYSDATE) INTO v_hire_date, v_end_date FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN ROUND(MONTHS_BETWEEN(v_end_date, v_hire_date) / 12, 1)
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN NULL

**Business rules:**
- Tenure calculated in years, rounded to 1 decimal place
- For active employees, end date is SYSDATE; for terminated, uses TERMINATION_DATE

---

### FUNCTION is_active(p_emp_id IN NUMBER) RETURN BOOLEAN

**Logic:**
1. SELECT EMPLOYMENT_STATUS INTO v_status FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_status = 'ACTIVE'
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN FALSE

---

### FUNCTION validate_employee(p_emp_id IN NUMBER) RETURN BOOLEAN

**Logic:**
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. IF v_emp.FIRST_NAME IS NULL OR v_emp.LAST_NAME IS NULL THEN RETURN FALSE
3. IF v_emp.HIRE_DATE IS NULL THEN RETURN FALSE
4. IF v_emp.EMPLOYMENT_STATUS = 'ACTIVE' AND v_emp.ACTIVE_FLAG != 'Y' THEN RETURN FALSE
5. RETURN TRUE
6. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN FALSE

**Business rules:**
- Valid employee: first name not null, last name not null, hire date not null
- If EMPLOYMENT_STATUS is 'ACTIVE', ACTIVE_FLAG must also be 'Y' (consistency check)

---

### FUNCTION emp_exists(p_emp_id IN NUMBER) RETURN BOOLEAN

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_count > 0

---

### PROCEDURE set_session_context(p_user IN VARCHAR2, p_emp_id IN NUMBER)

**Logic:**
1. g_current_user := p_user
2. g_current_emp_id := p_emp_id
3. SELECT DEPT_ID INTO g_current_dept_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
4. EXCEPTION WHEN NO_DATA_FOUND THEN g_current_dept_id := NULL

**Side effects:** Sets package-level global variables g_current_user, g_current_emp_id, g_current_dept_id

---

**All database tables referenced in PKG_EMPLOYEE:**

| Table | Operations |
|---|---|
| EMPLOYEES | SELECT, INSERT, UPDATE |
| DEPARTMENTS | SELECT |
| JOB_TITLES | SELECT |
| JOB_GRADES | SELECT |
| SALARY_RECORDS | SELECT |
| EMPLOYEE_HISTORY | INSERT (via log_history) |
| LEAVE_REQUESTS | SELECT, UPDATE |
| EMPLOYEE_PAY_ELEMENTS | UPDATE |

**All sequences used:**
- SEQ_EMPLOYEE
- SEQ_EMP_HISTORY

**All external packages called:**
- PKG_PAYROLL.create_salary_record
- PKG_AUDIT.log_action
- PKG_NOTIFICATION.send_notification
- PKG_COMMON.log_error

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks ===

**Package:** HRMS.PKG_INTEGRATION
**Schema:** HRMS
**Type:** Package Specification

---

**Type Definitions:**

`TYPE t_gl_entry IS RECORD`:
- journal_date — DATE
- account_code — VARCHAR2(30)
- debit_amount — NUMBER(15,2)
- credit_amount — NUMBER(15,2)
- description — VARCHAR2(200)
- reference — VARCHAR2(100)

`TYPE t_gl_entry_table IS TABLE OF t_gl_entry INDEX BY BINARY_INTEGER`

---

**Public Procedure/Function Signatures:**

| Name | Kind | Parameters |
|---|---|---|
| generate_gl_journal | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER |
| export_benefits_feed | PROCEDURE | p_effective_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER |
| import_time_attendance | PROCEDURE | p_file_name VARCHAR2, p_user VARCHAR2 DEFAULT USER |
| sync_org_structure | PROCEDURE | p_user VARCHAR2 DEFAULT USER |
| get_integration_status | FUNCTION | p_integration_name VARCHAR2 → RETURN VARCHAR2 |

---

**Dependencies (per header):** PKG_COMMON, PKG_PAYROLL, PKG_EMPLOYEE

**Called by (per header):** Batch scheduler (nightly GL feed, weekly benefits sync)

**Known issues (per header):**
- GL posting uses flat file exchange (UTL_FILE) instead of API
- Benefits feed format is vendor-specific (ADP format)
- No retry logic for failed file transfers
- FTP credentials stored in SYSTEM_PARAMETERS table (cleartext) — security vulnerability

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb ===

**Package:** HRMS.PKG_INTEGRATION
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value |
|---|---|---|
| c_gl_output_dir | VARCHAR2(30) | 'GL_FEED_OUT' |
| c_benefits_output_dir | VARCHAR2(30) | 'BENEFITS_FEED_OUT' |
| c_time_input_dir | VARCHAR2(30) | 'TIME_ATTENDANCE_IN' |

These are Oracle directory object names (mapped to OS filesystem paths by DBA).

---

### PROCEDURE generate_gl_journal(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** Creates GL journal entries from payroll run and writes to pipe-delimited flat file consumed by Oracle Financials batch import.

**Logic:**
1. v_filename := 'GL_JOURNAL_' || p_run_id || '_' || TO_CHAR(SYSDATE,'YYYYMMDD') || '.dat'
2. v_file := UTL_FILE.FOPEN(c_gl_output_dir [='GL_FEED_OUT'], v_filename, 'W', 32767) — write mode, max line 32767 chars
3. Write header record: `H|HRMS_PAYROLL|[YYYY-MM-DD]|[run_id]`
4. Cursor loop over aggregated payroll data:
   ```sql
   SELECT d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE,
          SUM(pd.AMOUNT) AS TOTAL_AMOUNT, pp.PERIOD_NAME
   FROM PAYROLL_DETAILS pd
   JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
   JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID
   JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
   JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
   JOIN PAY_ELEMENTS pe ON pd.ELEMENT_ID = pe.ELEMENT_ID
   WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND pe.GL_ACCOUNT_CODE IS NOT NULL
   GROUP BY d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE, pp.PERIOD_NAME
   ```
5. For each row:
   - If ELEMENT_TYPE = 'EARNING': write `D|[COST_CENTER]|[GL_ACCOUNT_CODE]|[ABS(TOTAL_AMOUNT) format FM999999990.00]|0.00|Payroll [PERIOD_NAME]|RUN-[run_id]`
   - Else (deductions/taxes/liability accounts): write `D|[COST_CENTER]|[GL_ACCOUNT_CODE]|0.00|[ABS(TOTAL_AMOUNT) format FM999999990.00]|Payroll [PERIOD_NAME]|RUN-[run_id]`
6. Write trailer record: `T|[v_entries]`
7. UTL_FILE.FCLOSE(v_file)
8. PKG_COMMON.log_info(...)
9. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

**File format (pipe-delimited):**
- Header: `H|HRMS_PAYROLL|YYYY-MM-DD|run_id`
- Detail (earning/debit): `D|cost_center|gl_account|debit_amount|0.00|description|reference`
- Detail (deduction/credit): `D|cost_center|gl_account|0.00|credit_amount|description|reference`
- Trailer: `T|count`

**Business rules:**
- Earnings → debit to expense accounts (debit column populated, credit = 0.00)
- Deductions/taxes → credit to liability accounts (debit = 0.00, credit column populated)
- ERROR rows excluded (pd.STATUS != 'ERROR')
- Only elements with GL_ACCOUNT_CODE assigned are included

**External services:** UTL_FILE (Oracle directory object 'GL_FEED_OUT'), PKG_COMMON

**Database tables accessed:** PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS, EMPLOYEES, DEPARTMENTS, PAY_ELEMENTS

---

### PROCEDURE export_benefits_feed(p_effective_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** ADP-format benefits enrollment file. LEGACY: Fixed-width format, specific to ADP vendor.

**Logic:**
1. v_filename := 'BENEFITS_' || TO_CHAR(SYSDATE,'YYYYMMDD') || '.txt'
2. v_file := UTL_FILE.FOPEN(c_benefits_output_dir [='BENEFITS_FEED_OUT'], v_filename, 'W', 32767)
3. Cursor loop:
   ```sql
   SELECT e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.DATE_OF_BIRTH, e.HIRE_DATE,
          e.EMPLOYMENT_STATUS, e.MARITAL_STATUS, e.GENDER,
          d.FIRST_NAME AS DEP_FIRST_NAME, d.LAST_NAME AS DEP_LAST_NAME,
          d.RELATIONSHIP, d.DATE_OF_BIRTH AS DEP_DOB
   FROM EMPLOYEES e LEFT JOIN EMPLOYEE_DEPENDENTS d ON e.EMP_ID = d.EMP_ID AND d.ACTIVE_FLAG = 'Y'
   WHERE e.EMPLOYMENT_STATUS = 'ACTIVE'
   ORDER BY e.EMP_NUMBER, d.DEPENDENT_ID
   ```
4. For each row, write fixed-width record:

| Field | Width | Source |
|---|---|---|
| EMP_NUMBER | 10 | RPAD |
| FIRST_NAME | 30 | RPAD |
| LAST_NAME | 30 | RPAD |
| DATE_OF_BIRTH | 10 | RPAD(TO_CHAR(...,'YYYY-MM-DD')) |
| HIRE_DATE | 10 | RPAD(TO_CHAR(...,'YYYY-MM-DD')) |
| EMPLOYMENT_STATUS | 12 | RPAD |
| MARITAL_STATUS | 10 | RPAD |
| GENDER | 1 | RPAD |
| DEP_FIRST_NAME | 30 | RPAD |
| DEP_LAST_NAME | 30 | RPAD |
| RELATIONSHIP | 20 | RPAD |
| DEP_DOB | 10 | RPAD(TO_CHAR(...,'YYYY-MM-DD')) |

Total fixed record width: 10+30+30+10+10+12+10+1+30+30+20+10 = 203 characters

5. UTL_FILE.FCLOSE; PKG_COMMON.log_info
6. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

**Business rules:**
- Only ACTIVE employees included
- Dependents joined with LEFT JOIN — employee appears once per dependent (one row per dependent, or one row if no dependents)
- Only active dependents (ACTIVE_FLAG='Y') included
- Null values padded with spaces

**Database tables accessed:** EMPLOYEES, EMPLOYEE_DEPENDENTS

---

### PROCEDURE import_time_attendance(p_file_name IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. v_file := UTL_FILE.FOPEN(c_time_input_dir [='TIME_ATTENDANCE_IN'], p_file_name, 'R', 32767)
2. LOOP:
   - UTL_FILE.GET_LINE(v_file, v_line)
   - If line not null and first character != '#' (skip comment lines)
   - Expected CSV format: emp_number, date, hours_regular, hours_overtime
   - TODO: actual parsing and database update not implemented
   - v_imported := v_imported + 1
   - EXCEPTION WHEN NO_DATA_FOUND THEN EXIT (end of file)
   - EXCEPTION WHEN OTHERS THEN v_errors := v_errors + 1; PKG_COMMON.log_error(...)
3. UTL_FILE.FCLOSE; PKG_COMMON.log_info

**Known limitation:** Actual CSV parsing and database update is a TODO — not implemented.

**File format (CSV):** emp_number, date, hours_regular, hours_overtime
**Comment prefix:** Lines beginning with '#' are skipped

---

### PROCEDURE sync_org_structure(p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
- Placeholder only — calls PKG_COMMON.log_info('Org structure sync completed')
- Intended for LDAP/AD sync but not implemented

---

### FUNCTION get_integration_status(p_integration_name IN VARCHAR2) RETURN VARCHAR2

**Logic:**
1. RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS')

**Configuration key pattern:** 'INTEGRATION', '[integration_name]_STATUS' — stored in SYSTEM_PARAMETERS (via PKG_COMMON.get_param)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks ===

**Package:** HRMS.PKG_LEAVE
**Schema:** HRMS
**Type:** Package Specification

---

**Custom Exceptions:**

| Name | Code |
|---|---|
| e_insufficient_balance | -20201 |
| e_overlapping_leave | -20202 |
| e_invalid_leave_type | -20203 |
| e_approval_error | -20204 |

`TYPE t_leave_cursor IS REF CURSOR`

---

**Public Signatures:**

| Name | Kind | Parameters | Returns |
|---|---|---|---|
| submit_leave_request | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_half_day_flag CHAR DEFAULT 'N', p_half_day_period VARCHAR2 DEFAULT NULL, p_reason VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER |
| approve_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| reject_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| cancel_leave_request | PROCEDURE | p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| get_leave_balance | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| adjust_leave_balance | PROCEDURE | p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| initialize_balances | PROCEDURE | p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| run_monthly_accrual | PROCEDURE | p_accrual_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER | — |
| process_carryover | PROCEDURE | p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| expire_carryover | PROCEDURE | p_user VARCHAR2 DEFAULT USER | — |
| get_pending_requests | PROCEDURE | p_cursor OUT t_leave_cursor, p_approver_id NUMBER | — |
| get_team_calendar | PROCEDURE | p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE | — |
| calculate_business_days | FUNCTION | p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL | NUMBER |
| check_leave_overlap | FUNCTION | p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL | BOOLEAN |

---

**Dependencies (per header):** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION

**Called by (per header):** HRMS_LEAVE form, self-service portal, batch accrual job

**Known issues:**
- Overlapping leave detection does not account for half-day requests
- Carryover expiry job sometimes double-expires if run twice on same day
- Holiday detection only checks exact date match, not observed dates

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb ===

**Package:** HRMS.PKG_LEAVE
**Schema:** HRMS
**Type:** Package Body

---

### FUNCTION calculate_business_days(p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL) RETURN NUMBER

**Logic:**
1. v_count := 0; v_date := TRUNC(p_start_date)
2. WHILE v_date <= TRUNC(p_end_date) LOOP:
   - IF TO_CHAR(v_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN') NOT IN ('SAT','SUN') THEN (skip weekends)
     - SELECT COUNT(*) INTO v_holiday_count FROM HOLIDAYS WHERE HOLIDAY_DATE = v_date AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)
     - IF v_holiday_count = 0 THEN v_count := v_count + 1
   - v_date := v_date + 1
3. RETURN v_count

**Business rules:**
- Weekends (Saturday, Sunday) are not business days
- Holidays from HOLIDAYS table (where ACTIVE_FLAG='Y') are excluded
- Holiday can be global (LOCATION_CODE IS NULL) or location-specific
- Date language for day-of-week check is always AMERICAN

**Known bug:** Does not handle "observed" holidays (e.g., if July 4 falls Saturday, observed Friday not excluded).

**Database tables accessed:** HOLIDAYS

---

### FUNCTION check_leave_overlap(p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL) RETURN BOOLEAN

**Logic:**
1. SELECT COUNT(*) INTO v_count FROM LEAVE_REQUESTS WHERE EMP_ID=p_emp_id AND STATUS IN ('PENDING','APPROVED') AND (p_exclude_request_id IS NULL OR REQUEST_ID != p_exclude_request_id) AND START_DATE <= p_end_date AND END_DATE >= p_start_date
2. RETURN v_count > 0

**Business rules:**
- Overlap exists if any PENDING or APPROVED request for same employee spans any part of requested date range
- Excludes a specific request_id (used when updating an existing request)

**Known limitation:** Does not account for half-day requests (per .pks known issues)

---

### FUNCTION submit_leave_request(...) RETURN NUMBER

**Full parameter list:**
- p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_half_day_flag CHAR DEFAULT 'N', p_half_day_period VARCHAR2 DEFAULT NULL, p_reason VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. SELECT * INTO v_emp_rec FROM EMPLOYEES WHERE EMP_ID=p_emp_id AND EMPLOYMENT_STATUS='ACTIVE'; EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20001, 'Employee not found or not active: ' || p_emp_id)
2. SELECT * INTO v_leave_type FROM LEAVE_TYPES WHERE LEAVE_TYPE_ID=p_leave_type_id AND ACTIVE_FLAG='Y'; EXCEPTION WHEN NO_DATA_FOUND THEN RAISE_APPLICATION_ERROR(-20203, 'Invalid leave type: ' || p_leave_type_id)
3. Minimum tenure check: IF v_leave_type.MIN_TENURE_DAYS > 0 AND SYSDATE - v_emp_rec.HIRE_DATE < v_leave_type.MIN_TENURE_DAYS THEN RAISE_APPLICATION_ERROR(-20203, 'Minimum tenure of [N] days not met for leave type: [name]')
4. IF p_start_date > p_end_date THEN RAISE_APPLICATION_ERROR(-20210, 'Start date must be before or equal to end date')
5. Backdating check: IF p_start_date < TRUNC(SYSDATE) AND TRUNC(SYSDATE) - p_start_date > 5 THEN RAISE_APPLICATION_ERROR(-20211, 'Cannot submit leave requests more than 5 days in the past')
6. Calculate total days:
   - IF p_half_day_flag = 'Y' THEN v_total_days := 0.5
   - ELSE v_total_days := calculate_business_days(p_start_date, p_end_date, v_emp_rec.LOCATION_CODE)
7. IF v_total_days <= 0 THEN RAISE_APPLICATION_ERROR(-20212, 'No business days in the selected range')
8. IF check_leave_overlap(p_emp_id, p_start_date, p_end_date) THEN RAISE_APPLICATION_ERROR(-20202, 'Leave request overlaps with an existing request')
9. Balance check (accrual-based types only): IF v_leave_type.ACCRUAL_FLAG = 'Y' THEN v_balance := get_leave_balance(p_emp_id, p_leave_type_id); IF v_balance < v_total_days THEN RAISE_APPLICATION_ERROR(-20201, 'Insufficient leave balance. Available: [n], Requested: [n]')
10. SELECT SEQ_LEAVE_REQUEST.NEXTVAL INTO v_request_id FROM DUAL
11. v_manager_id := v_emp_rec.MANAGER_EMP_ID
12. INSERT INTO LEAVE_REQUESTS: (REQUEST_ID, EMP_ID, LEAVE_TYPE_ID, START_DATE, END_DATE, TOTAL_DAYS, HALF_DAY_FLAG, HALF_DAY_PERIOD, STATUS, REASON, APPROVER_EMP_ID, CREATED_BY, CREATED_DATE) VALUES (..., STATUS = CASE WHEN v_leave_type.REQUIRES_APPROVAL = 'Y' THEN 'PENDING' ELSE 'APPROVED' END, ...)
13. UPDATE LEAVE_BALANCES SET PENDING = PENDING + v_total_days WHERE EMP_ID=p_emp_id AND LEAVE_TYPE_ID=p_leave_type_id AND CALENDAR_YEAR = EXTRACT(YEAR FROM p_start_date)
14. IF v_manager_id IS NOT NULL AND v_leave_type.REQUIRES_APPROVAL = 'Y' THEN send notification to manager: subject='Leave Request Pending Approval', body='[name] has requested [n] day(s) of [type] from [start MM/DD/YYYY] to [end MM/DD/YYYY].'
15. IF v_leave_type.REQUIRES_APPROVAL = 'N' THEN call approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user)
16. PKG_AUDIT.log_action('LEAVE_REQUESTS', v_request_id, 'INSERT', p_user)
17. RETURN v_request_id

**Business rules:**
- Employee must be ACTIVE
- Leave type must be active (ACTIVE_FLAG='Y')
- Minimum tenure enforced per leave type (MIN_TENURE_DAYS, in days since hire)
- Start date must be <= end date
- Backdating allowed up to **5 days** in the past; more than 5 days back is rejected
- Half-day = exactly 0.5 days (independent of business day calculation)
- At least 1 business day must be in the range
- Overlapping PENDING or APPROVED requests are blocked
- Balance checked only for ACCRUAL_FLAG='Y' leave types
- Auto-approve immediately if REQUIRES_APPROVAL='N'
- PENDING balance incremented at submission time

**Numeric literals:**
- 0.5 — half-day value
- 5 — maximum days in the past for backdated submission

**Exceptions thrown:**
- -20001 'Employee not found or not active: [id]'
- -20203 'Invalid leave type: [id]'
- -20203 'Minimum tenure of [N] days not met for leave type: [name]'
- -20210 'Start date must be before or equal to end date'
- -20211 'Cannot submit leave requests more than 5 days in the past'
- -20212 'No business days in the selected range'
- -20202 'Leave request overlaps with an existing request'
- -20201 'Insufficient leave balance. Available: [n], Requested: [n]'

**Sequences:** SEQ_LEAVE_REQUEST

**Database tables accessed/written:** EMPLOYEES (read), LEAVE_TYPES (read), LEAVE_REQUESTS (insert), LEAVE_BALANCES (update)

---

### PROCEDURE approve_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID=p_request_id FOR UPDATE
2. IF v_request.STATUS != 'PENDING' THEN RAISE_APPLICATION_ERROR(-20204, 'Cannot approve request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='APPROVED', APPROVER_EMP_ID=p_approver_emp_id, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS=p_comments, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE REQUEST_ID=p_request_id
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS, USED = USED + v_request.TOTAL_DAYS WHERE EMP_ID=v_request.EMP_ID AND LEAVE_TYPE_ID=v_request.LEAVE_TYPE_ID AND CALENDAR_YEAR = EXTRACT(YEAR FROM v_request.START_DATE)
5. Send notification to employee: subject='Leave Request Approved', body='Your leave request from [start MM/DD/YYYY] to [end MM/DD/YYYY] has been approved.'
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

**Business rules:**
- Only PENDING requests can be approved
- On approval: PENDING balance decremented, USED balance incremented by TOTAL_DAYS

**Exceptions thrown:** -20204 'Cannot approve request in status: [status]'

---

### PROCEDURE reject_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID=p_request_id FOR UPDATE
2. IF v_request.STATUS != 'PENDING' THEN RAISE_APPLICATION_ERROR(-20204, 'Cannot reject request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='REJECTED', APPROVER_EMP_ID, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS, MODIFIED_BY, MODIFIED_DATE WHERE REQUEST_ID=p_request_id
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND CALENDAR_YEAR=EXTRACT(YEAR FROM v_request.START_DATE)
5. Send notification to employee: subject='Leave Request Rejected', body='Your leave request has been rejected. Reason: [comments]'
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

**Business rules:**
- Only PENDING requests can be rejected
- On rejection: PENDING balance released (decremented)

**Exceptions thrown:** -20204 'Cannot reject request in status: [status]'

---

### PROCEDURE cancel_leave_request(p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID=p_request_id FOR UPDATE
2. IF v_request.STATUS NOT IN ('PENDING','APPROVED') THEN RAISE_APPLICATION_ERROR(-20204, 'Cannot cancel request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON=p_reason, CANCELLED_DATE=SYSDATE, MODIFIED_BY, MODIFIED_DATE WHERE REQUEST_ID=p_request_id
4. Balance restoration:
   - IF v_request.STATUS = 'PENDING' THEN UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS ... (release pending)
   - ELSIF v_request.STATUS = 'APPROVED' THEN UPDATE LEAVE_BALANCES SET USED = USED - v_request.TOTAL_DAYS ... (restore used back)
5. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

**Business rules:**
- Only PENDING or APPROVED requests can be cancelled (not REJECTED, CANCELLED, TAKEN)
- Cancelled PENDING request: PENDING balance decremented
- Cancelled APPROVED request: USED balance decremented (balance restored)

**Exceptions thrown:** -20204 'Cannot cancel request in status: [status]'

---

### FUNCTION get_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER

**Logic:**
1. SELECT OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING INTO v_balance FROM LEAVE_BALANCES WHERE EMP_ID=p_emp_id AND LEAVE_TYPE_ID=p_leave_type_id AND CALENDAR_YEAR=p_year
2. RETURN NVL(v_balance, 0)
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0

**Balance formula:** OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING

---

### PROCEDURE adjust_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT + p_adjustment WHERE EMP_ID=p_emp_id AND LEAVE_TYPE_ID=p_leave_type_id AND CALENDAR_YEAR=EXTRACT(YEAR FROM SYSDATE)
2. IF SQL%ROWCOUNT = 0 THEN call initialize_balances(p_emp_id, EXTRACT(YEAR FROM SYSDATE), p_user); then retry UPDATE
3. PKG_AUDIT.log_action('LEAVE_BALANCES', p_emp_id, 'UPDATE', p_user)

---

### PROCEDURE initialize_balances(p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. FOR lt IN (SELECT LEAVE_TYPE_ID FROM LEAVE_TYPES WHERE ACTIVE_FLAG='Y') LOOP:
   - INSERT INTO LEAVE_BALANCES: (BALANCE_ID=SEQ_LEAVE_BALANCE.NEXTVAL, EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR=p_year, OPENING_BALANCE=0, ACCRUED=0, USED=0, ADJUSTMENT=0, PENDING=0, CREATED_BY, CREATED_DATE)
   - EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL (skip if already exists)

**Sequences:** SEQ_LEAVE_BALANCE

---

### PROCEDURE run_monthly_accrual(p_accrual_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** Batch job — accrues leave for all active employees. Typically scheduled via DBMS_SCHEDULER on the 1st of each month.

**Logic:**
1. For each active employee (EMPLOYMENT_STATUS='ACTIVE' AND ACTIVE_FLAG='Y'):
   - For each leave type with ACCRUAL_FLAG='Y' AND ACCRUAL_FREQUENCY='MONTHLY':
     - Check tenure: IF TRUNC(p_accrual_date) - emp_rec.HIRE_DATE >= lt_rec.MIN_TENURE_DAYS THEN:
       - v_current_balance := get_leave_balance(emp_rec.EMP_ID, lt_rec.LEAVE_TYPE_ID, EXTRACT(YEAR FROM p_accrual_date))
       - If MAX_BALANCE is NULL OR v_current_balance + ACCRUAL_RATE <= MAX_BALANCE: v_accrued := ACCRUAL_RATE
       - Else: v_accrued := GREATEST(0, MAX_BALANCE - v_current_balance) — cap to not exceed max
       - IF v_accrued > 0:
         - UPDATE LEAVE_BALANCES SET ACCRUED = ACCRUED + v_accrued WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND CALENDAR_YEAR=EXTRACT(YEAR FROM p_accrual_date)
         - IF SQL%ROWCOUNT=0: call initialize_balances and retry with ACCRUED=v_accrued (not +=)
         - INSERT INTO LEAVE_ACCRUAL_LOG: (ACCRUAL_ID=SEQ_LEAVE_ACCRUAL.NEXTVAL, EMP_ID, LEAVE_TYPE_ID, ACCRUAL_DATE=p_accrual_date, ACCRUAL_AMOUNT=v_accrued, CREATED_BY, CREATED_DATE)
   - COMMIT every 100 employees (MOD(v_total_employees, 100) = 0)
2. Final COMMIT

**Business rules:**
- Only employees with EMPLOYMENT_STATUS='ACTIVE' AND ACTIVE_FLAG='Y' are processed
- Only MONTHLY frequency accrual types processed (separate runs would handle WEEKLY etc.)
- Minimum tenure enforced per leave type (days since hire)
- Accrual amount capped to MAX_BALANCE if specified
- GREATEST(0,...) prevents negative accrual

**Numeric literals:**
- 100 — commit batch size

**Sequences used:** SEQ_LEAVE_ACCRUAL

**Database tables accessed/written:** EMPLOYEES (read), LEAVE_TYPES (read), LEAVE_BALANCES (update), LEAVE_ACCRUAL_LOG (insert)

---

### PROCEDURE process_carryover(p_year NUMBER, p_user VARCHAR2 DEFAULT USER)

**Purpose:** Runs at year-end to carry over unused leave to next year.

**Logic:**
1. v_next_year := p_year + 1
2. FOR bal_rec IN (SELECT lb.EMP_ID, lb.LEAVE_TYPE_ID, lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT AS REMAINING, lt.CARRYOVER_MAX, lt.CARRYOVER_EXPIRY FROM LEAVE_BALANCES lb JOIN LEAVE_TYPES lt ON lb.LEAVE_TYPE_ID=lt.LEAVE_TYPE_ID WHERE lb.CALENDAR_YEAR=p_year AND REMAINING > 0) LOOP:
   - v_carryover := bal_rec.REMAINING
   - IF CARRYOVER_MAX IS NOT NULL THEN v_carryover := LEAST(v_carryover, CARRYOVER_MAX) — cap carryover
   - IF v_carryover > 0 THEN:
     - initialize_balances(EMP_ID, v_next_year, p_user)
     - UPDATE LEAVE_BALANCES SET CARRYOVER_FROM_PREV=v_carryover, OPENING_BALANCE=v_carryover, CARRYOVER_EXPIRY_DT = CASE WHEN CARRYOVER_EXPIRY IS NOT NULL THEN ADD_MONTHS(TO_DATE(v_next_year||'-01-01','YYYY-MM-DD'), CARRYOVER_EXPIRY) ELSE NULL END WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND CALENDAR_YEAR=v_next_year
3. COMMIT

**Business rules:**
- Carryover is remaining balance (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT), not counting PENDING
- Capped at CARRYOVER_MAX if specified per leave type
- Carryover expiry date = next_year Jan 1 + CARRYOVER_EXPIRY months

---

### PROCEDURE expire_carryover(p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT - CARRYOVER_FROM_PREV, CARRYOVER_FROM_PREV=0 WHERE CARRYOVER_EXPIRY_DT <= TRUNC(SYSDATE) AND CARRYOVER_FROM_PREV > 0
2. COMMIT

**Known bug:** If run twice on same day, can double-subtract (since CARRYOVER_FROM_PREV is set to 0 only on the first run, but a second run would still match rows where... wait, actually CARRYOVER_FROM_PREV = 0 after first run so WHERE CARRYOVER_FROM_PREV > 0 would not match. The bug described in the header may refer to a different scenario, or the bug exists if the COMMIT doesn't happen before a second call within the same session).

---

### PROCEDURE get_pending_requests(p_cursor OUT t_leave_cursor, p_approver_id NUMBER)

**Logic:**
1. OPEN p_cursor FOR:
   ```sql
   SELECT lr.REQUEST_ID, lr.EMP_ID, e.FIRST_NAME||' '||e.LAST_NAME AS EMPLOYEE_NAME,
          lt.LEAVE_TYPE_NAME, lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS,
          lr.REASON, lr.CREATED_DATE
   FROM LEAVE_REQUESTS lr
   JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
   JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
   WHERE lr.STATUS = 'PENDING' AND lr.APPROVER_EMP_ID = p_approver_id
   ORDER BY lr.CREATED_DATE
   ```

---

### PROCEDURE get_team_calendar(p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE)

**Logic:**
1. OPEN p_cursor FOR:
   ```sql
   SELECT e.EMP_ID, e.FIRST_NAME||' '||e.LAST_NAME AS EMPLOYEE_NAME,
          lt.LEAVE_TYPE_NAME, lt.LEAVE_TYPE_CODE,
          lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS, lr.STATUS, lr.HALF_DAY_FLAG
   FROM LEAVE_REQUESTS lr
   JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
   JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
   WHERE e.MANAGER_EMP_ID = p_manager_id
   AND lr.STATUS IN ('APPROVED','TAKEN')
   AND lr.START_DATE <= p_end_date AND lr.END_DATE >= p_start_date
   ORDER BY lr.START_DATE, e.LAST_NAME
   ```

---

**All database tables referenced in PKG_LEAVE:**

| Table | Operations |
|---|---|
| EMPLOYEES | SELECT |
| LEAVE_TYPES | SELECT |
| LEAVE_REQUESTS | SELECT, INSERT, UPDATE |
| LEAVE_BALANCES | SELECT, INSERT, UPDATE |
| LEAVE_ACCRUAL_LOG | INSERT |
| HOLIDAYS | SELECT |

**Sequences:** SEQ_LEAVE_REQUEST, SEQ_LEAVE_BALANCE, SEQ_LEAVE_ACCRUAL

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks ===

**Package:** HRMS.PKG_NOTIFICATION
**Schema:** HRMS
**Type:** Package Specification

**Dependencies (per header):** PKG_COMMON
**Called by (per header):** PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE

**Known issues (per header):**
- UTL_MAIL configuration hard-coded to legacy SMTP server
- No rate limiting — bulk operations can flood the queue
- HTML email templates stored as string constants (maintenance nightmare)

---

**Public Signatures:**

| Name | Kind | Parameters |
|---|---|---|
| send_notification | PROCEDURE | p_recipient_emp_id NUMBER DEFAULT NULL, p_recipient_email VARCHAR2 DEFAULT NULL, p_type VARCHAR2 DEFAULT 'EMAIL', p_subject VARCHAR2, p_body CLOB, p_priority NUMBER DEFAULT 5, p_reference_table VARCHAR2 DEFAULT NULL, p_reference_id NUMBER DEFAULT NULL, p_user VARCHAR2 DEFAULT USER |
| process_queue | PROCEDURE | p_batch_size NUMBER DEFAULT 50, p_user VARCHAR2 DEFAULT USER |
| retry_failed | PROCEDURE | p_max_retries NUMBER DEFAULT 3, p_user VARCHAR2 DEFAULT USER |
| cancel_notification | PROCEDURE | p_notification_id NUMBER, p_user VARCHAR2 DEFAULT USER |

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb ===

**Package:** HRMS.PKG_NOTIFICATION
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value |
|---|---|---|
| c_smtp_host | VARCHAR2(100) | 'smtp.internal.company.com' |
| c_smtp_port | NUMBER | 25 |
| c_from_address | VARCHAR2(100) | 'hrms-noreply@company.com' |
| c_from_name | VARCHAR2(100) | 'HRMS System' |

---

### PROCEDURE send_notification(...) — PRAGMA AUTONOMOUS_TRANSACTION

**Full parameter list:**
- p_recipient_emp_id NUMBER DEFAULT NULL, p_recipient_email VARCHAR2 DEFAULT NULL, p_type VARCHAR2 DEFAULT 'EMAIL', p_subject VARCHAR2, p_body CLOB, p_priority NUMBER DEFAULT 5, p_reference_table VARCHAR2 DEFAULT NULL, p_reference_id NUMBER DEFAULT NULL, p_user VARCHAR2 DEFAULT USER

**Logic:**
1. PRAGMA AUTONOMOUS_TRANSACTION
2. Email resolution: IF p_recipient_email IS NULL AND p_recipient_emp_id IS NOT NULL THEN SELECT EMAIL INTO v_email FROM EMPLOYEES WHERE EMP_ID=p_recipient_emp_id; EXCEPTION WHEN NO_DATA_FOUND THEN v_email := NULL; ELSE v_email := p_recipient_email
3. INSERT INTO NOTIFICATION_QUEUE: (NOTIFICATION_ID=SEQ_NOTIFICATION.NEXTVAL, RECIPIENT_EMP_ID, RECIPIENT_EMAIL=v_email, NOTIFICATION_TYPE=p_type, SUBJECT, BODY, STATUS='PENDING', PRIORITY=p_priority, REFERENCE_TABLE, REFERENCE_ID, CREATED_BY=p_user, CREATED_DATE=SYSDATE)
4. COMMIT
5. EXCEPTION WHEN OTHERS: ROLLBACK; PKG_COMMON.log_error('PKG_NOTIFICATION','send_notification','Failed to queue notification: '||SQLERRM, p_user) — notification failures never block business operations

**Business rules:**
- Notification is queued, not sent immediately (async delivery)
- Default priority = 5
- Default type = 'EMAIL'
- Notification failure is silently swallowed (never propagates to caller)
- Email resolved from employee record if not provided directly

**Sequences:** SEQ_NOTIFICATION

**Database tables written:** NOTIFICATION_QUEUE
**Database tables accessed:** EMPLOYEES (read, for email lookup)

---

### PROCEDURE process_queue(p_batch_size IN NUMBER DEFAULT 50, p_user IN VARCHAR2 DEFAULT USER)

**Purpose:** Sends pending notifications via UTL_SMTP. Called by DBMS_SCHEDULER job every 5 minutes.

**Logic:**
1. FOR notif_rec IN (SELECT NOTIFICATION_ID, RECIPIENT_EMAIL, SUBJECT, BODY, NOTIFICATION_TYPE FROM NOTIFICATION_QUEUE WHERE STATUS='PENDING' AND NOTIFICATION_TYPE='EMAIL' AND RECIPIENT_EMAIL IS NOT NULL ORDER BY PRIORITY ASC, CREATED_DATE ASC FETCH FIRST p_batch_size ROWS ONLY) LOOP:
   - v_connection := UTL_SMTP.OPEN_CONNECTION('smtp.internal.company.com', 25)
   - UTL_SMTP.HELO(v_connection, 'smtp.internal.company.com')
   - UTL_SMTP.MAIL(v_connection, 'hrms-noreply@company.com')
   - UTL_SMTP.RCPT(v_connection, RECIPIENT_EMAIL)
   - UTL_SMTP.OPEN_DATA; write headers: From, To, Subject, Content-Type: text/plain; charset=UTF-8; blank line; Body
   - UTL_SMTP.CLOSE_DATA; UTL_SMTP.QUIT
   - UPDATE NOTIFICATION_QUEUE SET STATUS='SENT', SENT_DATE=SYSDATE WHERE NOTIFICATION_ID=...
   - v_sent := v_sent + 1
   - EXCEPTION WHEN OTHERS: UPDATE NOTIFICATION_QUEUE SET STATUS='FAILED', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000), RETRY_COUNT=RETRY_COUNT+1 WHERE NOTIFICATION_ID=...; v_failed := v_failed + 1; try UTL_SMTP.QUIT(v_connection)
2. COMMIT
3. Log if any sent or failed

**Business rules:**
- Only processes EMAIL type, PENDING status, with non-null RECIPIENT_EMAIL
- Processing order: lowest priority number first (ORDER BY PRIORITY ASC), then oldest first
- Default batch size = 50 per invocation
- Each email opens/closes its own SMTP connection (no connection pooling)
- SMTP connection per email — inefficient but isolated failures
- Failed emails: STATUS='FAILED', RETRY_COUNT incremented, ERROR_MESSAGE stored (truncated to 4000 chars)

**Numeric literals:**
- 50 — default batch size
- 4000 — max error message length (SUBSTR)

**External services called:** UTL_SMTP (to smtp.internal.company.com:25), UTL_TCP (for CRLF constant)

**Database tables written:** NOTIFICATION_QUEUE

---

### PROCEDURE retry_failed(p_max_retries IN NUMBER DEFAULT 3, p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE NOTIFICATION_QUEUE SET STATUS='PENDING', ERROR_MESSAGE=NULL WHERE STATUS='FAILED' AND RETRY_COUNT < p_max_retries
2. COMMIT

**Business rules:**
- Maximum retry attempts = 3 (default)
- Resets failed notifications back to PENDING if under retry limit
- Clears error message on reset

---

### PROCEDURE cancel_notification(p_notification_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE NOTIFICATION_QUEUE SET STATUS='CANCELLED' WHERE NOTIFICATION_ID=p_notification_id AND STATUS='PENDING'
2. (No COMMIT — relies on caller's transaction)

**Business rules:**
- Only PENDING notifications can be cancelled

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks ===

**Package:** HRMS.PKG_PAYROLL
**Schema:** HRMS
**Type:** Package Specification

---

**Custom Exceptions:**

| Name | Code |
|---|---|
| e_invalid_salary | -20101 |
| e_period_closed | -20102 |
| e_run_already_paid | -20103 |
| e_calculation_error | -20104 |

---

**Type Definitions:**

`TYPE t_payslip_rec IS RECORD`:
- emp_id — NUMBER(10)
- emp_number — VARCHAR2(20)
- emp_name — VARCHAR2(101)
- period_name — VARCHAR2(50)
- gross_pay — NUMBER(12,2)
- total_deductions — NUMBER(12,2)
- net_pay — NUMBER(12,2)
- federal_tax — NUMBER(12,2)
- state_tax — NUMBER(12,2)
- social_security — NUMBER(12,2)
- medicare — NUMBER(12,2)
- ytd_gross — NUMBER(15,2)
- ytd_net — NUMBER(15,2)

`TYPE t_payslip_cursor IS REF CURSOR`

---

**Public Signatures:**

| Name | Kind | Parameters | Returns |
|---|---|---|---|
| create_salary_record | PROCEDURE | p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2 DEFAULT NULL, p_change_pct NUMBER DEFAULT NULL, p_currency_code VARCHAR2 DEFAULT 'USD', p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| get_current_salary | FUNCTION | p_emp_id NUMBER | NUMBER |
| get_salary_as_of | FUNCTION | p_emp_id NUMBER, p_as_of DATE | NUMBER |
| create_pay_periods | PROCEDURE | p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| close_pay_period | PROCEDURE | p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_current_period | FUNCTION | (none) | NUMBER |
| create_payroll_run | FUNCTION | p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER | NUMBER |
| calculate_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| calculate_employee_pay | PROCEDURE | p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| approve_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| reverse_payroll | PROCEDURE | p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| calculate_federal_tax | FUNCTION | p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_state_tax | FUNCTION | p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_fica | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| calculate_medicare | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| get_payslip | PROCEDURE | p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL | — |
| get_ytd_earnings | FUNCTION | p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| generate_pay_register | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |

---

**Dependencies (per header):** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION

**Known issues (per header):**
- Circular dependency with PKG_EMPLOYEE (is_active check)
- Tax calculation uses hard-coded 2024 brackets in some paths
- Overtime calculation does not account for holidays correctly
- YTD accumulation resets incorrectly for mid-year hires in some edge cases

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb ===

**Package:** HRMS.PKG_PAYROLL
**Schema:** HRMS
**Type:** Package Body

---

**Private Constants:**

| Name | Type | Value | Description |
|---|---|---|---|
| c_ss_wage_base_2024 | NUMBER | 168600 | Social Security 2024 wage base |
| c_ss_rate | NUMBER | 0.062 | Employee SS rate (6.2%) |
| c_medicare_rate | NUMBER | 0.0145 | Employee Medicare rate (1.45%) |
| c_medicare_addl_rate | NUMBER | 0.009 | Additional Medicare tax rate (0.9%) |
| c_medicare_addl_threshold | NUMBER | 200000 | Threshold triggering additional Medicare tax |
| c_standard_deduction_single | NUMBER | 14600 | 2024 standard deduction for Single/MFS |
| c_standard_deduction_married | NUMBER | 29200 | 2024 standard deduction for Married Filing Jointly |
| c_allowance_amount | NUMBER | 4300 | Per-allowance reduction amount |

---

### PROCEDURE create_salary_record(...)

**Full parameter list:**
- p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2 DEFAULT NULL, p_change_pct NUMBER DEFAULT NULL, p_currency_code VARCHAR2 DEFAULT 'USD', p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER

**Logic:**
1. IF p_base_salary <= 0 THEN RAISE_APPLICATION_ERROR(-20101, 'Salary must be positive: ' || p_base_salary)
2. UPDATE SALARY_RECORDS SET END_DATE=p_effective_date-1, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' AND EFFECTIVE_DATE < p_effective_date — end-date previous active salary record
3. INSERT INTO SALARY_RECORDS: (SALARY_ID=SEQ_SALARY.NEXTVAL, EMP_ID, EFFECTIVE_DATE, BASE_SALARY, CURRENCY_CODE, PAY_FREQUENCY, SALARY_BASIS='ANNUAL', CHANGE_REASON, CHANGE_PCT, ACTIVE_FLAG='Y', CREATED_BY, CREATED_DATE)
4. PKG_AUDIT.log_action('SALARY_RECORDS', SEQ_SALARY.CURRVAL, 'INSERT', p_user)

**Business rules:**
- Salary must be > 0
- SALARY_BASIS is always 'ANNUAL'
- Default currency = 'USD'
- Default pay frequency = 'MONTHLY'
- Previous active record for that employee end-dated to effective_date - 1

**Exceptions thrown:** -20101 'Salary must be positive: [n]'

**Sequences:** SEQ_SALARY

**Database tables accessed/written:** SALARY_RECORDS

---

### FUNCTION get_current_salary(p_emp_id IN NUMBER) RETURN NUMBER

**Logic:**
1. SELECT BASE_SALARY INTO v_salary FROM SALARY_RECORDS WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' AND EFFECTIVE_DATE <= SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. RETURN v_salary
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0

---

### FUNCTION get_salary_as_of(p_emp_id IN NUMBER, p_as_of IN DATE) RETURN NUMBER

**Logic:**
1. SELECT BASE_SALARY INTO v_salary FROM SALARY_RECORDS WHERE EMP_ID=p_emp_id AND EFFECTIVE_DATE <= p_as_of AND (END_DATE IS NULL OR END_DATE >= p_as_of) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. RETURN v_salary
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN 0

---

### PROCEDURE create_pay_periods(p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER)

**Logic (MONTHLY):**
1. FOR i IN 1..12 LOOP:
   - v_start_date := TO_DATE(year||'-'||LPAD(i,2,'0')||'-01','YYYY-MM-DD')
   - v_end_date := LAST_DAY(v_start_date)
   - v_pay_date := v_end_date
   - IF TO_CHAR(v_pay_date,'DY') = 'SAT' THEN v_pay_date := v_pay_date - 1 (move to Friday)
   - ELSIF TO_CHAR(v_pay_date,'DY') = 'SUN' THEN v_pay_date := v_pay_date - 2 (move to Friday)
   - v_period_num := v_period_num + 1
   - INSERT INTO PAY_PERIODS: (PERIOD_ID=SEQ_PAY_PERIOD.NEXTVAL, PERIOD_NAME=year||'-'||LPAD(i,2,'0')||' ('||Mon||')', PAY_FREQUENCY, PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE, STATUS='OPEN', CREATED_BY, CREATED_DATE)

**Logic (BIWEEKLY):**
1. v_start_date := TO_DATE(year||'-01-01','YYYY-MM-DD')
2. WHILE TO_CHAR(v_start_date,'DY') != 'FRI' LOOP v_start_date := v_start_date + 1 END LOOP — find first Friday
3. v_start_date := v_start_date - 13 — back to start of pay period (period ends on Friday, starts 2 weeks prior day)
4. WHILE EXTRACT(YEAR FROM v_start_date) <= p_year LOOP:
   - v_end_date := v_start_date + 13 — 14-day period (0..13)
   - v_pay_date := v_end_date + 5 — pay 5 days after period end
   - v_period_num := v_period_num + 1
   - IF year of start OR end = p_year THEN INSERT INTO PAY_PERIODS: (PERIOD_NAME=year||'-BW-'||LPAD(num,2,'0'), STATUS='OPEN', ...)
   - v_start_date := v_end_date + 1
5. COMMIT

**Business rules:**
- MONTHLY: 12 periods per year, each covering full calendar month
- MONTHLY: Pay date = last day of month, moved to preceding Friday if weekend
- BIWEEKLY: 14-day periods ending on Friday
- BIWEEKLY: Pay date = 5 days after period end
- All new periods have STATUS='OPEN'

**Sequences:** SEQ_PAY_PERIOD

---

### PROCEDURE close_pay_period(p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT STATUS INTO v_status FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id FOR UPDATE
2. IF v_status = 'CLOSED' THEN RAISE_APPLICATION_ERROR(-20102, 'Period already closed: ' || p_period_id)
3. UPDATE PAY_PERIODS SET STATUS='CLOSED', CLOSED_BY=p_user, CLOSED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE PERIOD_ID=p_period_id

**Exceptions thrown:** -20102 'Period already closed: [id]'

---

### FUNCTION get_current_period RETURN NUMBER

**Logic:**
1. SELECT PERIOD_ID INTO v_period_id FROM PAY_PERIODS WHERE SYSDATE BETWEEN PERIOD_START_DATE AND PERIOD_END_DATE AND STATUS='OPEN' AND ROWNUM=1
2. RETURN v_period_id
3. EXCEPTION WHEN NO_DATA_FOUND THEN RETURN NULL

---

### FUNCTION create_payroll_run(p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER) RETURN NUMBER

**Logic:**
1. SELECT STATUS INTO v_status FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id
2. IF v_status = 'CLOSED' THEN RAISE_APPLICATION_ERROR(-20102, 'Cannot create run for closed period: ' || p_period_id)
3. SELECT SEQ_PAYROLL_RUN.NEXTVAL INTO v_run_id FROM DUAL
4. INSERT INTO PAYROLL_RUNS: (RUN_ID, PERIOD_ID, RUN_TYPE, RUN_DATE=SYSDATE, STATUS='PENDING', SUBMITTED_BY=p_user, SUBMITTED_DATE=SYSDATE, CREATED_BY, CREATED_DATE)
5. RETURN v_run_id

**Exceptions thrown:** -20102 'Cannot create run for closed period: [id]'

**Sequences:** SEQ_PAYROLL_RUN

---

### PROCEDURE calculate_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT PERIOD_ID, RUN_TYPE INTO v_period_id, v_run_type FROM PAYROLL_RUNS WHERE RUN_ID=p_run_id
2. UPDATE PAYROLL_RUNS SET STATUS='CALCULATING' WHERE RUN_ID=p_run_id; COMMIT
3. FOR emp_rec IN (SELECT e.EMP_ID FROM EMPLOYEES e WHERE e.EMPLOYMENT_STATUS='ACTIVE' AND e.ACTIVE_FLAG='Y' ORDER BY e.EMP_ID) LOOP:
   - BEGIN calculate_employee_pay(p_run_id, emp_rec.EMP_ID, v_period_id, p_user); v_emp_count := v_emp_count+1
   - EXCEPTION WHEN OTHERS: v_error_count := v_error_count+1; INSERT INTO PAYROLL_DETAILS error row (ELEMENT_ID=0, ELEMENT_TYPE='ERROR', AMOUNT=0, STATUS='ERROR', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000))
   - IF MOD(v_emp_count, 50) = 0 THEN COMMIT (every 50 employees)
4. UPDATE PAYROLL_RUNS SET STATUS = CASE WHEN v_error_count > 0 THEN 'ERROR' ELSE 'CALCULATED' END, EMPLOYEE_COUNT=v_emp_count, ERROR_COUNT=v_error_count, TOTAL_GROSS=(SUM of EARNING elements excluding ERROR status), TOTAL_DEDUCTIONS=(SUM of DEDUCTION/TAX elements excluding ERROR), TOTAL_NET=(net sum), MODIFIED_BY, MODIFIED_DATE WHERE RUN_ID=p_run_id
5. COMMIT

**Business rules:**
- Processes only ACTIVE employees with ACTIVE_FLAG='Y'
- Error in one employee does not stop processing of others
- TOTAL_GROSS = SUM of ELEMENT_TYPE='EARNING' WHERE STATUS != 'ERROR'
- TOTAL_DEDUCTIONS = SUM ABS of ELEMENT_TYPE IN ('DEDUCTION','TAX') WHERE STATUS != 'ERROR'
- TOTAL_NET = SUM of (EARNING amounts + -(DEDUCTION/TAX amounts)) WHERE STATUS != 'ERROR'
- Final STATUS = 'ERROR' if any employee errored, else 'CALCULATED'

**Numeric literals:**
- 50 — commit batch interval
- 4000 — max error message length

**Known issues:**
- Row-by-row cursor loop — should use BULK COLLECT + FORALL
- Partial commits mean a failure leaves payroll half-calculated

---

### PROCEDURE calculate_employee_pay(p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT PERIOD_START_DATE, PERIOD_END_DATE, PAY_FREQUENCY INTO ... FROM PAY_PERIODS WHERE PERIOD_ID=p_period_id
2. v_periods_per_year := CASE PAY_FREQUENCY WHEN 'WEEKLY' THEN 52 WHEN 'BIWEEKLY' THEN 26 WHEN 'SEMIMONTHLY' THEN 24 WHEN 'MONTHLY' THEN 12 ELSE 12 END
3. v_annual_salary := get_salary_as_of(p_emp_id, v_period_end)
4. IF v_annual_salary = 0 THEN RAISE_APPLICATION_ERROR(-20104, 'No active salary record for employee ' || p_emp_id)
5. v_period_gross := ROUND(v_annual_salary / v_periods_per_year, 2)
6. INSERT INTO PAYROLL_DETAILS: (ELEMENT_ID=1, ELEMENT_TYPE='EARNING', AMOUNT=v_period_gross, STATUS='CALCULATED')
7. v_ytd_gross := get_ytd_earnings(p_emp_id, EXTRACT(YEAR FROM v_period_end))
8. Get tax info from EMPLOYEE_TAX_INFO WHERE EMP_ID=p_emp_id AND TAX_YEAR=year AND ACTIVE_FLAG='Y'; DEFAULT IF NONE: filing_status='SINGLE', fed_allowances=0, state_code=NULL, state_allowances=0, addl_fed_wh=0
9. v_taxable_income := v_period_gross (simplified — should subtract pretax deductions)
10. v_federal_tax := calculate_federal_tax(v_taxable_income, v_filing_status, v_fed_allowances, v_addl_fed_wh, v_pay_frequency)
11. IF v_federal_tax > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=100, ELEMENT_TYPE='TAX', AMOUNT=-v_federal_tax)
12. IF v_state_code IS NOT NULL: v_state_tax := calculate_state_tax(v_taxable_income, v_state_code, v_filing_status, v_state_allowances, v_pay_frequency); IF v_state_tax > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=101, ELEMENT_TYPE='TAX', AMOUNT=-v_state_tax)
13. v_ss_tax := calculate_fica(v_period_gross, v_ytd_gross); IF > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=102, ELEMENT_TYPE='TAX', AMOUNT=-v_ss_tax)
14. v_medicare_tax := calculate_medicare(v_period_gross, v_ytd_gross); IF > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID=103, ELEMENT_TYPE='TAX', AMOUNT=-v_medicare_tax)
15. FOR ded_rec IN (SELECT ... FROM EMPLOYEE_PAY_ELEMENTS epe JOIN PAY_ELEMENTS pe ON epe.ELEMENT_ID=pe.ELEMENT_ID WHERE epe.EMP_ID=p_emp_id AND epe.ACTIVE_FLAG='Y' AND pe.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') AND epe.EFFECTIVE_DATE <= v_period_end AND (epe.END_DATE IS NULL OR epe.END_DATE >= v_period_start) ORDER BY pe.PRIORITY_ORDER) LOOP:
    - IF OVERRIDE_AMOUNT IS NOT NULL: v_ded_amount := OVERRIDE_AMOUNT
    - ELSIF CALCULATION_TYPE = 'FLAT': v_ded_amount := NVL(AMOUNT, DEFAULT_AMOUNT)
    - ELSIF CALCULATION_TYPE = 'PERCENTAGE': v_ded_amount := ROUND(v_period_gross * NVL(PERCENTAGE, DEFAULT_PERCENTAGE) / 100, 2)
    - ELSE: v_ded_amount := NVL(AMOUNT, 0)
    - IF v_ded_amount > 0: INSERT PAYROLL_DETAILS (ELEMENT_ID, ELEMENT_TYPE, AMOUNT=-v_ded_amount)
16. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error; RAISE

**Fixed ELEMENT_ID assignments:**

| Element ID | Meaning |
|---|---|
| 1 | Base gross pay (EARNING) |
| 100 | Federal income tax (TAX) |
| 101 | State income tax (TAX) |
| 102 | Social Security / FICA (TAX) |
| 103 | Medicare (TAX) |

**Business rules:**
- Period gross = ROUND(annual_salary / periods_per_year, 2)
- Deduction amounts: override > flat > percentage; percentage is of period gross
- Tax amounts stored as negative values in PAYROLL_DETAILS
- Deductions processed in PRIORITY_ORDER
- Only elements effective during the period (EFFECTIVE_DATE <= end AND END_DATE >= start or null) are included
- Default filing status 'SINGLE' with 0 allowances if no EMPLOYEE_TAX_INFO record

**Known issue:** v_taxable_income = v_period_gross (pretax deductions not subtracted — simplified)

---

### FUNCTION calculate_federal_tax(p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER

**Logic:**
1. v_periods := CASE p_pay_frequency WHEN 'WEEKLY' THEN 52 WHEN 'BIWEEKLY' THEN 26 WHEN 'SEMIMONTHLY' THEN 24 WHEN 'MONTHLY' THEN 12 ELSE 12 END
2. v_annualized := p_taxable_income * v_periods
3. v_std_deduction := CASE WHEN p_filing_status IN ('MARRIED_JOINT') THEN 29200 ELSE 14600 END
4. v_taxable := v_annualized - v_std_deduction - (p_allowances * 4300)
5. IF v_taxable <= 0 THEN RETURN 0

**2024 Federal Tax Brackets — SINGLE or MARRIED_SEPARATE:**

| Taxable Income Range | Tax Calculation |
|---|---|
| 0 – 11,600 | taxable × 0.10 |
| 11,601 – 47,150 | 1,160 + (taxable − 11,600) × 0.12 |
| 47,151 – 100,525 | 5,426 + (taxable − 47,150) × 0.22 |
| 100,526 – 191,950 | 17,168.50 + (taxable − 100,525) × 0.24 |
| 191,951 – 243,725 | 39,110.50 + (taxable − 191,950) × 0.32 |
| 243,726 – 609,350 | 55,678.50 + (taxable − 243,725) × 0.35 |
| 609,351 and above | 183,647.25 + (taxable − 609,350) × 0.37 |

**2024 Federal Tax Brackets — MARRIED_JOINT:**

| Taxable Income Range | Tax Calculation |
|---|---|
| 0 – 23,200 | taxable × 0.10 |
| 23,201 – 94,300 | 2,320 + (taxable − 23,200) × 0.12 |
| 94,301 – 201,050 | 10,852 + (taxable − 94,300) × 0.22 |
| 201,051 – 383,900 | 34,337 + (taxable − 201,050) × 0.24 |
| 383,901 – 487,450 | 78,221 + (taxable − 383,900) × 0.32 |
| 487,451 – 731,200 | 111,357 + (taxable − 487,450) × 0.35 |
| 731,201 and above | 196,669.50 + (taxable − 731,200) × 0.37 |

6. v_tax := ROUND(v_tax / v_periods, 2) — convert annual tax back to per-period
7. v_tax := v_tax + NVL(p_additional_wh, 0) — add any additional withholding
8. RETURN v_tax

**Business rules:**
- Annualize income, apply standard deduction and allowances, apply bracket, de-annualize
- Standard deduction: 14,600 (single/MFS), 29,200 (married joint)
- Per-allowance reduction: 4,300
- Additional withholding added on top of bracket-calculated amount
- Brackets are 2024 rates, hard-coded (TODO: read from TAX_BRACKETS table)

---

### FUNCTION calculate_state_tax(p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER

**Logic:**
1. v_rate := CASE p_state_code:
   - 'CA' → 0.0725 (7.25%)
   - 'NY' → 0.0685 (6.85%)
   - 'TX' → 0 (no state income tax)
   - 'FL' → 0 (no state income tax)
   - 'WA' → 0 (no state income tax)
   - 'IL' → 0.0495 (4.95%)
   - 'PA' → 0.0307 (3.07%)
   - 'OH' → 0.04 (4.00%)
   - 'NJ' → 0.0637 (6.37%)
   - 'MA' → 0.05 (5.00%)
   - ELSE → 0.05 (5.00% default for unknown states)
2. RETURN ROUND(p_taxable_income * v_rate, 2)

**Business rules:**
- Simplified flat-rate by state; no progressive brackets (noted as simplified)
- Unknown/unrecognized state codes default to 5.00% flat rate
- TX, FL, WA have no state income tax (0%)

---

### FUNCTION calculate_fica(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER

**Logic:**
1. IF p_ytd_gross >= 168600 THEN RETURN 0 — already exceeded SS wage base
2. v_taxable := LEAST(p_gross_pay, 168600 - p_ytd_gross) — cap at remaining wage base
3. RETURN ROUND(v_taxable * 0.062, 2) — 6.2% employee share

**Business rules:**
- Social Security wage base 2024: 168,600
- Rate: 6.2% (employee portion only)
- Earnings above the wage base are not subject to SS tax

---

### FUNCTION calculate_medicare(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER

**Logic:**
1. v_base_tax := ROUND(p_gross_pay * 0.0145, 2) — 1.45% on all earnings (no wage base)
2. Additional Medicare (0.9%) on high earners:
   - IF p_ytd_gross + p_gross_pay > 200,000 THEN:
     - IF p_ytd_gross >= 200,000 THEN v_addl_tax := ROUND(p_gross_pay * 0.009, 2) — entire period over threshold
     - ELSE v_addl_tax := ROUND((p_ytd_gross + p_gross_pay - 200,000) * 0.009, 2) — only the portion above threshold
3. RETURN v_base_tax + v_addl_tax

**Business rules:**
- Base Medicare: 1.45% on all wages, no cap
- Additional Medicare: 0.9% on wages exceeding 200,000 YTD
- Additional rate applies only to the portion of current period wages that pushed YTD over 200,000

---

### PROCEDURE approve_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. SELECT STATUS INTO v_status FROM PAYROLL_RUNS WHERE RUN_ID=p_run_id FOR UPDATE
2. IF v_status NOT IN ('CALCULATED') THEN RAISE_APPLICATION_ERROR(-20103, 'Cannot approve run in status: ' || v_status)
3. UPDATE PAYROLL_RUNS SET STATUS='APPROVED', APPROVED_BY=p_user, APPROVED_DATE=SYSDATE WHERE RUN_ID=p_run_id

**Business rules:**
- Only 'CALCULATED' runs can be approved (not PENDING, ERROR, REVERSED, etc.)

**Exceptions thrown:** -20103 'Cannot approve run in status: [status]'

---

### PROCEDURE reverse_payroll(p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)

**Logic:**
1. UPDATE PAYROLL_RUNS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id
2. UPDATE PAYROLL_DETAILS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id
3. PKG_AUDIT.log_action('PAYROLL_RUNS', p_run_id, 'UPDATE', p_user)

**Business rules:**
- No status check before reversing (can reverse from any status)
- All detail lines set to 'REVERSED'

---

### PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL)

**Logic:**
1. OPEN p_cursor FOR:
   ```sql
   SELECT pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME||' '||e.LAST_NAME AS EMP_NAME,
          pp.PERIOD_NAME,
          SUM(CASE WHEN pd.ELEMENT_TYPE='EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY,
          SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','TAX','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS,
          SUM(pd.AMOUNT) AS NET_PAY,
          SUM(CASE WHEN pd.ELEMENT_ID=100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX,
          SUM(CASE WHEN pd.ELEMENT_ID=101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX,
          SUM(CASE WHEN pd.ELEMENT_ID=102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY,
          SUM(CASE WHEN pd.ELEMENT_ID=103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE,
          0 AS YTD_GROSS,  -- Placeholder (not implemented)
          0 AS YTD_NET     -- Placeholder (not implemented)
   FROM PAYROLL_DETAILS pd JOIN EMPLOYEES e ... JOIN PAYROLL_RUNS pr ... JOIN PAY_PERIODS pp ...
   WHERE pd.RUN_ID=p_run_id AND pd.STATUS != 'ERROR' AND (p_emp_id IS NULL OR pd.EMP_ID=p_emp_id)
   GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME||' '||e.LAST_NAME, pp.PERIOD_NAME
   ORDER BY e.LAST_NAME
   ```

**Known limitations:** YTD_GROSS and YTD_NET are hard-coded 0 (placeholders not implemented)

---

### FUNCTION get_ytd_earnings(p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER

**Logic:**
1. SELECT NVL(SUM(pd.AMOUNT),0) INTO v_ytd FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ... JOIN PAY_PERIODS pp ... WHERE pd.EMP_ID=p_emp_id AND pd.ELEMENT_TYPE='EARNING' AND pd.STATUS='CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
2. RETURN v_ytd

---

### PROCEDURE generate_pay_register(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)

**Purpose:** Writes pay register to UTL_FILE CSV output. LEGACY: flat file — should be replaced with modern reporting.

**Logic:**
1. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE,'YYYYMMDD_HH24MISS') || '.csv'
2. v_file := UTL_FILE.FOPEN('PAYROLL_OUTPUT', v_filename, 'W', 32767)
3. Write CSV header: `EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY`
4. FOR rec IN (aggregated pay data per employee with dept) LOOP:
   - Write CSV line: EMP_NUMBER,"EMPLOYEE_NAME","DEPT_NAME",GROSS,FED,STATE,SS,MED,DEDS,NET (amounts formatted FM999999990.00)
5. UTL_FILE.FCLOSE; DBMS_OUTPUT.PUT_LINE confirmation message
6. EXCEPTION WHEN OTHERS: close file; PKG_COMMON.log_error; RAISE

**Oracle directory object used:** 'PAYROLL_OUTPUT'

**File format (CSV):**
- Header row with 10 columns
- Detail: EMP_NUMBER (unquoted), EMP_NAME (double-quoted), DEPT_NAME (double-quoted), 8 numeric columns

---

**All database tables referenced in PKG_PAYROLL:**

| Table | Operations |
|---|---|
| SALARY_RECORDS | SELECT, INSERT, UPDATE |
| PAY_PERIODS | SELECT, INSERT, UPDATE |
| PAYROLL_RUNS | SELECT, INSERT, UPDATE |
| PAYROLL_DETAILS | SELECT, INSERT, UPDATE |
| EMPLOYEES | SELECT |
| DEPARTMENTS | SELECT |
| EMPLOYEE_TAX_INFO | SELECT |
| EMPLOYEE_PAY_ELEMENTS | SELECT |
| PAY_ELEMENTS | SELECT |

**All sequences:**
- SEQ_SALARY
- SEQ_PAY_PERIOD
- SEQ_PAYROLL_RUN
- SEQ_PAYROLL_DETAIL

**External packages called:**
- PKG_AUDIT.log_action
- PKG_COMMON.log_error, PKG_COMMON.log_info

**External Oracle features used:**
- UTL_FILE (directory objects: PAYROLL_OUTPUT)
- DBMS_SCHEDULER (implied — scheduler calls process_queue every 5 minutes per PKG_NOTIFICATION)

---

**Cross-package dependency summary:**

| Package | Calls | Called by |
|---|---|---|
| PKG_EMPLOYEE | PKG_PAYROLL, PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON | PKG_LEAVE (employee validation), PKG_PAYROLL (is_active), forms, batch |
| PKG_PAYROLL | PKG_EMPLOYEE (is_active — circular), PKG_AUDIT, PKG_COMMON | PKG_EMPLOYEE (create_salary_record), forms, batch |
| PKG_LEAVE | PKG_EMPLOYEE, PKG_AUDIT, PKG_NOTIFICATION, PKG_COMMON | Forms, self-service portal, batch |
| PKG_NOTIFICATION | PKG_COMMON, UTL_SMTP | PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE |
| PKG_INTEGRATION | PKG_COMMON, UTL_FILE | Batch scheduler |

**Referenced but not provided in source:**
- PKG_AUDIT (log_action)
- PKG_COMMON (log_error, log_info, get_param)
- PKG_PERFORMANCE (referenced in PKG_NOTIFICATION header)
- PKG_SECURITY (TODO in terminate_employee)
- DBMS_SCHEDULER (scheduling context)
- SYSTEM_PARAMETERS table (FTP credentials stored here per integration header)


=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks ===

**Package:** HRMS.PKG_EMPLOYEE
**Schema:** HRMS

**Package-Level Global Variables:**
- `g_current_user` VARCHAR2(30) — session state
- `g_current_emp_id` NUMBER(10) — session state
- `g_current_dept_id` NUMBER(10) — session state
- `g_debug_mode` BOOLEAN := FALSE — session state

**Custom Exceptions:**
| Exception Name | Error Code | PRAGMA |
|---|---|---|
| e_employee_not_found | -20001 | PRAGMA EXCEPTION_INIT |
| e_duplicate_emp_number | -20002 | PRAGMA EXCEPTION_INIT |
| e_invalid_department | -20003 | PRAGMA EXCEPTION_INIT |
| e_invalid_manager | -20004 | PRAGMA EXCEPTION_INIT |
| e_termination_error | -20005 | PRAGMA EXCEPTION_INIT |

**Types:**

`TYPE t_emp_rec IS RECORD:`
- emp_id: EMPLOYEES.EMP_ID%TYPE
- emp_number: EMPLOYEES.EMP_NUMBER%TYPE
- first_name: EMPLOYEES.FIRST_NAME%TYPE
- last_name: EMPLOYEES.LAST_NAME%TYPE
- hire_date: EMPLOYEES.HIRE_DATE%TYPE
- dept_id: EMPLOYEES.DEPT_ID%TYPE
- job_id: EMPLOYEES.JOB_ID%TYPE
- manager_emp_id: EMPLOYEES.MANAGER_EMP_ID%TYPE
- employment_status: EMPLOYEES.EMPLOYMENT_STATUS%TYPE
- base_salary: NUMBER(12,2)

`TYPE t_emp_cursor IS REF CURSOR`

`TYPE t_emp_id_table IS TABLE OF NUMBER(10) INDEX BY BINARY_INTEGER`

`TYPE t_emp_rec_table IS TABLE OF t_emp_rec INDEX BY BINARY_INTEGER`

**Public Method Signatures:**

| Method | Kind | Parameters | Returns |
|---|---|---|---|
| create_employee | FUNCTION | p_first_name VARCHAR2, p_last_name VARCHAR2, p_hire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_manager_emp_id NUMBER DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_employment_type VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary NUMBER DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER |
| update_employee | PROCEDURE | p_emp_id NUMBER, p_first_name VARCHAR2 DEFAULT NULL, p_last_name VARCHAR2 DEFAULT NULL, p_email VARCHAR2 DEFAULT NULL, p_phone_work VARCHAR2 DEFAULT NULL, p_phone_mobile VARCHAR2 DEFAULT NULL, p_address_line1 VARCHAR2 DEFAULT NULL, p_address_line2 VARCHAR2 DEFAULT NULL, p_city VARCHAR2 DEFAULT NULL, p_state_province VARCHAR2 DEFAULT NULL, p_postal_code VARCHAR2 DEFAULT NULL, p_country_code VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| get_employee | FUNCTION | p_emp_id NUMBER | t_emp_rec |
| get_employee_by_number | FUNCTION | p_emp_number VARCHAR2 | t_emp_rec |
| search_employees | PROCEDURE | p_cursor OUT t_emp_cursor, p_last_name VARCHAR2 DEFAULT NULL, p_first_name VARCHAR2 DEFAULT NULL, p_dept_id NUMBER DEFAULT NULL, p_status VARCHAR2 DEFAULT NULL, p_location_code VARCHAR2 DEFAULT NULL, p_hire_date_from DATE DEFAULT NULL, p_hire_date_to DATE DEFAULT NULL | — |
| transfer_employee | PROCEDURE | p_emp_id NUMBER, p_new_dept_id NUMBER, p_new_job_id NUMBER DEFAULT NULL, p_new_manager_id NUMBER DEFAULT NULL, p_new_location VARCHAR2 DEFAULT NULL, p_effective_date DATE DEFAULT SYSDATE, p_reason_code VARCHAR2 DEFAULT NULL, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| promote_employee | PROCEDURE | p_emp_id NUMBER, p_new_job_id NUMBER, p_new_salary NUMBER, p_effective_date DATE DEFAULT SYSDATE, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| terminate_employee | PROCEDURE | p_emp_id NUMBER, p_termination_date DATE, p_reason VARCHAR2, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| rehire_employee | PROCEDURE | p_emp_id NUMBER, p_rehire_date DATE, p_dept_id NUMBER, p_job_id NUMBER, p_base_salary NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_direct_reports | FUNCTION | p_manager_emp_id NUMBER | t_emp_id_table |
| get_org_chart | FUNCTION | p_root_emp_id NUMBER, p_max_depth NUMBER DEFAULT 10 | t_emp_cursor |
| get_headcount_by_dept | FUNCTION | p_dept_id NUMBER DEFAULT NULL, p_as_of_date DATE DEFAULT SYSDATE | NUMBER |
| get_tenure_years | FUNCTION | p_emp_id NUMBER | NUMBER |
| is_active | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| validate_employee | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| emp_exists | FUNCTION | p_emp_id NUMBER | BOOLEAN |
| generate_emp_number | FUNCTION | (none) | VARCHAR2 |
| set_session_context | PROCEDURE | p_user VARCHAR2, p_emp_id NUMBER | — |

**Dependencies declared in header:**
- PKG_COMMON
- PKG_AUDIT
- PKG_NOTIFICATION
- PKG_PAYROLL

**Callers declared in header:**
- HRMS_EMPLOYEE form
- HRMS_DEPARTMENT form
- Batch jobs

**Known issues documented in header:**
- Circular dependency with PKG_PAYROLL (salary validation)
- get_org_chart uses recursive SQL that times out for deep hierarchies

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb ===

**Package:** HRMS.PKG_EMPLOYEE (body)

**Private Constants:**
| Constant | Type | Value |
|---|---|---|
| c_emp_number_prefix | VARCHAR2(3) | 'EMP' |
| c_max_hierarchy_depth | NUMBER | 15 |

**Private Forward Declarations:**
- PROCEDURE log_history(...) — full signature matches public-facing logic below
- PROCEDURE validate_dept(p_dept_id IN NUMBER)
- PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)
- FUNCTION get_next_emp_id RETURN NUMBER

---

**FUNCTION generate_emp_number RETURN VARCHAR2**

Logic:
1. SELECT NVL(MAX(TO_NUMBER(SUBSTR(EMP_NUMBER, 5))), 0) + 1 INTO v_max_num FROM EMPLOYEES WHERE EMP_NUMBER LIKE 'EMP-%'
   - Parses numeric suffix starting at character position 5 (after 'EMP-')
2. Formats as: 'EMP-' || LPAD(v_max_num, 6, '0') — zero-padded to 6 digits
3. EXCEPTION WHEN OTHERS: fallback to 'EMP-' || LPAD(SEQ_EMPLOYEE.NEXTVAL, 6, '0')

Documented bug: race condition under concurrent inserts — no SELECT FOR UPDATE.

Database tables read: EMPLOYEES
Sequences used: SEQ_EMPLOYEE

---

**FUNCTION get_next_emp_id RETURN NUMBER**

Logic:
1. SELECT SEQ_EMPLOYEE.NEXTVAL INTO v_id FROM DUAL
2. RETURN v_id

Sequences used: SEQ_EMPLOYEE

---

**PROCEDURE validate_dept(p_dept_id IN NUMBER)**

Logic:
1. SELECT COUNT(*) INTO v_count FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id AND ACTIVE_FLAG = 'Y'
2. IF v_count = 0 THEN RAISE_APPLICATION_ERROR(-20003, 'Invalid or inactive department: ' || p_dept_id)

Business rule: Department must exist and have ACTIVE_FLAG = 'Y'.

Database tables read: DEPARTMENTS (DEPT_ID, ACTIVE_FLAG)
Exceptions thrown: -20003 — department not found or inactive

---

**PROCEDURE validate_manager(p_manager_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)**

Logic:
1. IF p_manager_id IS NULL THEN RETURN — NULL manager is valid (top-level employee)
2. SELECT COUNT(*) FROM EMPLOYEES WHERE EMP_ID = p_manager_id AND EMPLOYMENT_STATUS = 'ACTIVE'
   - If count = 0: RAISE_APPLICATION_ERROR(-20004, 'Invalid or inactive manager: ' || p_manager_id)
3. Circular chain check (only when p_emp_id IS NOT NULL):
   - v_current_mgr := p_manager_id; v_depth := 0
   - WHILE v_current_mgr IS NOT NULL AND v_depth < 15 LOOP
     - IF v_current_mgr = p_emp_id: RAISE_APPLICATION_ERROR(-20004, 'Circular reporting chain detected: Employee ' || p_emp_id || ' cannot report to ' || p_manager_id)
     - SELECT MANAGER_EMP_ID INTO v_current_mgr FROM EMPLOYEES WHERE EMP_ID = v_current_mgr
       - EXCEPTION WHEN NO_DATA_FOUND: v_current_mgr := NULL
     - v_depth := v_depth + 1
   - Loop terminates when v_current_mgr IS NULL or v_depth reaches 15 (c_max_hierarchy_depth)

Business rules:
- Manager must be an ACTIVE employee.
- Hierarchy must not be circular.
- Circular detection traverses at most 15 levels deep.

Database tables read: EMPLOYEES (EMP_ID, EMPLOYMENT_STATUS, MANAGER_EMP_ID)
Exceptions thrown:
- -20004 — invalid/inactive manager
- -20004 — circular reporting chain detected

---

**PROCEDURE log_history(...) — PRAGMA AUTONOMOUS_TRANSACTION**

Parameters (all):
- p_emp_id IN NUMBER
- p_change_type IN VARCHAR2
- p_effective_date IN DATE
- p_old_dept_id IN NUMBER DEFAULT NULL
- p_new_dept_id IN NUMBER DEFAULT NULL
- p_old_job_id IN NUMBER DEFAULT NULL
- p_new_job_id IN NUMBER DEFAULT NULL
- p_old_manager IN NUMBER DEFAULT NULL
- p_new_manager IN NUMBER DEFAULT NULL
- p_old_salary IN NUMBER DEFAULT NULL
- p_new_salary IN NUMBER DEFAULT NULL
- p_old_location IN VARCHAR2 DEFAULT NULL
- p_new_location IN VARCHAR2 DEFAULT NULL
- p_reason_code IN VARCHAR2 DEFAULT NULL
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. PRAGMA AUTONOMOUS_TRANSACTION — runs in a separate transaction
2. INSERT INTO EMPLOYEE_HISTORY (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE) VALUES (SEQ_EMP_HISTORY.NEXTVAL, ...)
3. COMMIT
4. EXCEPTION WHEN OTHERS: ROLLBACK; if g_debug_mode then DBMS_OUTPUT.PUT_LINE warning; end

Business rule: History logging never fails the main transaction (exceptions are swallowed).

Database tables written: EMPLOYEE_HISTORY
Sequences used: SEQ_EMP_HISTORY
Columns inserted: HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE

---

**FUNCTION create_employee(...) RETURN NUMBER**

Parameters:
- p_first_name IN VARCHAR2
- p_last_name IN VARCHAR2
- p_hire_date IN DATE
- p_dept_id IN NUMBER
- p_job_id IN NUMBER
- p_manager_emp_id IN NUMBER DEFAULT NULL
- p_location_code IN VARCHAR2 DEFAULT NULL
- p_employment_type IN VARCHAR2 DEFAULT 'FULL_TIME'
- p_base_salary IN NUMBER DEFAULT NULL
- p_email IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. Validate p_first_name IS NOT NULL AND p_last_name IS NOT NULL — else RAISE_APPLICATION_ERROR(-20010, 'First name and last name are required')
2. Call validate_dept(p_dept_id)
3. Call validate_manager(p_manager_emp_id) — no p_emp_id passed (new hire, no circular check needed)
4. SELECT GRADE_ID INTO v_grade_id FROM JOB_TITLES WHERE JOB_ID = p_job_id AND ACTIVE_FLAG = 'Y'
   - EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20011, 'Invalid or inactive job: ' || p_job_id)
5. Salary vs. grade validation (soft warning, not an error):
   - If p_base_salary IS NOT NULL:
     - SELECT MIN_SALARY, MAX_SALARY INTO v_min, v_max FROM JOB_GRADES WHERE GRADE_ID = v_grade_id
     - IF p_base_salary < v_min OR p_base_salary > v_max: log debug warning only
     - Business rule: Salary outside grade range is a WARNING, not a hard error; override allowed with manager approval; the Forms trigger WHEN-VALIDATE-ITEM shows a warning dialog
6. Default location from department if p_location_code IS NULL:
   - SELECT LOCATION_CODE INTO v_location FROM DEPARTMENTS WHERE DEPT_ID = p_dept_id
7. v_emp_id := get_next_emp_id()
8. v_emp_number := generate_emp_number()
9. INSERT INTO EMPLOYEES (EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID, MANAGER_EMP_ID, LOCATION_CODE, EMPLOYMENT_TYPE, EMPLOYMENT_STATUS, EMAIL, ACTIVE_FLAG, CREATED_BY, CREATED_DATE)
   - FIRST_NAME stored as UPPER(TRIM(p_first_name))
   - LAST_NAME stored as UPPER(TRIM(p_last_name))
   - EMAIL stored as LOWER(TRIM(p_email))
   - EMPLOYMENT_STATUS = 'ACTIVE'
   - ACTIVE_FLAG = 'Y'
10. If p_base_salary IS NOT NULL: call PKG_PAYROLL.create_salary_record(p_emp_id, p_hire_date, p_base_salary, 'NEW_HIRE', p_user)
    - Documented circular dependency: PKG_PAYROLL.create_salary_record may call PKG_EMPLOYEE.is_active
11. Call log_history(p_emp_id, 'HIRE', p_hire_date, new_dept/job/manager/salary/location)
12. Call PKG_AUDIT.log_action('EMPLOYEES', v_emp_id, 'INSERT', p_user)
13. Call PKG_NOTIFICATION.send_notification to employee: type='EMAIL', subject='Welcome to the Company', body includes first_name and emp_number
14. If p_manager_emp_id IS NOT NULL: call PKG_NOTIFICATION.send_notification to manager: subject='New Direct Report: <first> <last>', body includes hire_date formatted as MM/DD/YYYY
15. RETURN v_emp_id

Exceptions:
- -20010 — first/last name null
- -20011 — invalid/inactive job
- DUP_VAL_ON_INDEX → RAISE_APPLICATION_ERROR(-20002, 'Duplicate employee number generated. Please retry.')
- WHEN OTHERS → PKG_COMMON.log_error('PKG_EMPLOYEE', 'create_employee', SQLERRM, p_user) then RAISE

Database tables read: DEPARTMENTS (DEPT_ID, ACTIVE_FLAG, LOCATION_CODE), JOB_TITLES (JOB_ID, ACTIVE_FLAG, GRADE_ID), JOB_GRADES (GRADE_ID, MIN_SALARY, MAX_SALARY)
Database tables written: EMPLOYEES
Sequences: SEQ_EMPLOYEE (via get_next_emp_id), implicit via generate_emp_number
External services called: PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification (twice)

---

**PROCEDURE update_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_first_name IN VARCHAR2 DEFAULT NULL
- p_last_name IN VARCHAR2 DEFAULT NULL
- p_email IN VARCHAR2 DEFAULT NULL
- p_phone_work IN VARCHAR2 DEFAULT NULL
- p_phone_mobile IN VARCHAR2 DEFAULT NULL
- p_address_line1 IN VARCHAR2 DEFAULT NULL
- p_address_line2 IN VARCHAR2 DEFAULT NULL
- p_city IN VARCHAR2 DEFAULT NULL
- p_state_province IN VARCHAR2 DEFAULT NULL
- p_postal_code IN VARCHAR2 DEFAULT NULL
- p_country_code IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. Call emp_exists(p_emp_id); if FALSE: RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)
2. UPDATE EMPLOYEES SET:
   - FIRST_NAME = NVL(UPPER(TRIM(p_first_name)), FIRST_NAME)
   - LAST_NAME = NVL(UPPER(TRIM(p_last_name)), LAST_NAME)
   - EMAIL = NVL(LOWER(TRIM(p_email)), EMAIL)
   - PHONE_WORK = NVL(p_phone_work, PHONE_WORK)
   - PHONE_MOBILE = NVL(p_phone_mobile, PHONE_MOBILE)
   - ADDRESS_LINE1 = NVL(p_address_line1, ADDRESS_LINE1)
   - ADDRESS_LINE2 = NVL(p_address_line2, ADDRESS_LINE2)
   - CITY = NVL(p_city, CITY)
   - STATE_PROVINCE = NVL(p_state_province, STATE_PROVINCE)
   - POSTAL_CODE = NVL(p_postal_code, POSTAL_CODE)
   - COUNTRY_CODE = NVL(p_country_code, COUNTRY_CODE)
   - MODIFIED_BY = p_user
   - MODIFIED_DATE = SYSDATE
   WHERE EMP_ID = p_emp_id
3. IF SQL%ROWCOUNT = 0: RAISE_APPLICATION_ERROR(-20001, 'Employee update failed: ' || p_emp_id)
4. Call PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

Business rule: Partial update pattern — only non-NULL input parameters overwrite existing values (NVL pattern).

Database tables written: EMPLOYEES
External services: PKG_AUDIT.log_action

---

**FUNCTION get_employee(p_emp_id IN NUMBER) RETURN t_emp_rec**

Logic:
1. SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, e.JOB_ID, e.MANAGER_EMP_ID, e.EMPLOYMENT_STATUS, (subquery for BASE_SALARY) FROM EMPLOYEES e WHERE e.EMP_ID = p_emp_id
2. Salary subquery: SELECT sr.BASE_SALARY FROM SALARY_RECORDS sr WHERE sr.EMP_ID = e.EMP_ID AND sr.ACTIVE_FLAG = 'Y' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE) AND ROWNUM = 1
3. EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_id)

Database tables read: EMPLOYEES, SALARY_RECORDS

---

**FUNCTION get_employee_by_number(p_emp_number IN VARCHAR2) RETURN t_emp_rec**

Logic:
1. SELECT EMP_ID INTO v_emp_id FROM EMPLOYEES WHERE EMP_NUMBER = p_emp_number
2. RETURN get_employee(v_emp_id)
3. EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20001, 'Employee not found: ' || p_emp_number)

Database tables read: EMPLOYEES

---

**PROCEDURE search_employees(...)**

Parameters:
- p_cursor OUT t_emp_cursor
- p_last_name IN VARCHAR2 DEFAULT NULL
- p_first_name IN VARCHAR2 DEFAULT NULL
- p_dept_id IN NUMBER DEFAULT NULL
- p_status IN VARCHAR2 DEFAULT NULL
- p_location_code IN VARCHAR2 DEFAULT NULL
- p_hire_date_from IN DATE DEFAULT NULL
- p_hire_date_to IN DATE DEFAULT NULL

Logic (dynamic SQL via string concatenation):
1. Base query: SELECT e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.HIRE_DATE, e.DEPT_ID, d.DEPT_NAME, j.JOB_TITLE, e.EMPLOYMENT_STATUS, e.LOCATION_CODE FROM EMPLOYEES e JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE 1=1
2. If p_last_name IS NOT NULL: AND UPPER(e.LAST_NAME) LIKE UPPER('<p_last_name>%') — VULNERABILITY: string concatenation, not bind variable
3. If p_first_name IS NOT NULL: AND UPPER(e.FIRST_NAME) LIKE UPPER('<p_first_name>%') — VULNERABILITY: string concatenation
4. If p_dept_id IS NOT NULL: AND e.DEPT_ID = <p_dept_id>
5. If p_status IS NOT NULL: AND e.EMPLOYMENT_STATUS = '<p_status>' — VULNERABILITY: string concatenation
6. If p_location_code IS NOT NULL: AND e.LOCATION_CODE = '<p_location_code>' — VULNERABILITY: string concatenation
7. If p_hire_date_from IS NOT NULL: AND e.HIRE_DATE >= TO_DATE('<YYYY-MM-DD>', 'YYYY-MM-DD')
8. If p_hire_date_to IS NOT NULL: AND e.HIRE_DATE <= TO_DATE('<YYYY-MM-DD>', 'YYYY-MM-DD')
9. ORDER BY e.LAST_NAME, e.FIRST_NAME
10. OPEN p_cursor FOR v_sql (dynamic OPEN)

Documented bug: SQL injection possible via p_last_name (and all other VARCHAR2 parameters). Forms LOV passes validated values; direct PL/SQL calls are vulnerable.

Database tables read: EMPLOYEES, DEPARTMENTS, JOB_TITLES

---

**PROCEDURE transfer_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_new_dept_id IN NUMBER
- p_new_job_id IN NUMBER DEFAULT NULL
- p_new_manager_id IN NUMBER DEFAULT NULL
- p_new_location IN VARCHAR2 DEFAULT NULL
- p_effective_date IN DATE DEFAULT SYSDATE
- p_reason_code IN VARCHAR2 DEFAULT NULL
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT * INTO v_old_rec FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE NOWAIT
2. IF v_old_rec.EMPLOYMENT_STATUS != 'ACTIVE': RAISE_APPLICATION_ERROR(-20012, 'Cannot transfer non-active employee. Status: ' || v_old_rec.EMPLOYMENT_STATUS)
3. validate_dept(p_new_dept_id)
4. v_new_job_id := NVL(p_new_job_id, v_old_rec.JOB_ID)
5. v_new_location := NVL(p_new_location, v_old_rec.LOCATION_CODE)
6. If p_new_manager_id IS NOT NULL: validate_manager(p_new_manager_id, p_emp_id)
7. UPDATE EMPLOYEES SET DEPT_ID=p_new_dept_id, JOB_ID=v_new_job_id, MANAGER_EMP_ID=NVL(p_new_manager_id, MANAGER_EMP_ID), LOCATION_CODE=v_new_location, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
8. log_history(p_emp_id, 'TRANSFER', p_effective_date, old/new dept/job/manager/location, reason, comments)
9. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error then RAISE

Business rules:
- Only ACTIVE employees can be transferred.
- Locking via FOR UPDATE NOWAIT (fails immediately if row locked).
- Job and location default to current values if not specified.

Exceptions thrown:
- -20012 — cannot transfer non-active employee
- -20003 — invalid department (from validate_dept)
- -20004 — invalid manager or circular chain (from validate_manager)

Database tables read/written: EMPLOYEES
External services: PKG_AUDIT.log_action, PKG_COMMON.log_error

---

**PROCEDURE promote_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_new_job_id IN NUMBER
- p_new_salary IN NUMBER
- p_effective_date IN DATE DEFAULT SYSDATE
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT JOB_ID INTO v_old_job_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. SELECT BASE_SALARY INTO v_old_salary FROM SALARY_RECORDS WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y' AND ROWNUM = 1 ORDER BY EFFECTIVE_DATE DESC
   - EXCEPTION WHEN NO_DATA_FOUND: v_old_salary := 0
3. UPDATE EMPLOYEES SET JOB_ID = p_new_job_id, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID = p_emp_id
4. PKG_PAYROLL.create_salary_record(p_emp_id, p_effective_date, p_new_salary, 'PROMOTION', p_change_pct=ROUND(((p_new_salary - v_old_salary) / v_old_salary) * 100, 2) when v_old_salary > 0 else NULL, p_user)
5. log_history(p_emp_id, 'PROMOTION', p_effective_date, old/new job, old/new salary, comments)
6. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

Business rule: Change percentage computed as ROUND(((new - old) / old) * 100, 2); only computed when old_salary > 0.

Database tables read: EMPLOYEES, SALARY_RECORDS
Database tables written: EMPLOYEES
External services: PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action

---

**PROCEDURE terminate_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_termination_date IN DATE
- p_reason IN VARCHAR2
- p_comments IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE
2. IF v_emp.EMPLOYMENT_STATUS = 'TERMINATED': RAISE_APPLICATION_ERROR(-20005, 'Employee ' || p_emp_id || ' is already terminated')
3. SELECT COUNT(*) INTO v_pending_leave FROM LEAVE_REQUESTS WHERE EMP_ID = p_emp_id AND STATUS = 'PENDING'
4. If v_pending_leave > 0: UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON='Auto-cancelled due to termination', CANCELLED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND STATUS='PENDING'
5. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='TERMINATED', TERMINATION_DATE=p_termination_date, TERMINATION_REASON=p_reason, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
6. UPDATE SALARY_RECORDS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
7. UPDATE EMPLOYEE_PAY_ELEMENTS SET END_DATE=p_termination_date, ACTIVE_FLAG='N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y'
8. log_history(p_emp_id, 'TERMINATION', p_termination_date, reason, comments)
9. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)
10. If v_emp.MANAGER_EMP_ID IS NOT NULL: PKG_NOTIFICATION.send_notification to manager: subject='Employee Termination: <first> <last>', body includes termination date formatted MM/DD/YYYY
11. TODO comments (not implemented): benefits system COBRA integration, security access revocation via PKG_SECURITY, final pay via PKG_PAYROLL.calculate_final_pay
12. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error then RAISE

Business rules:
- Already-terminated employee cannot be terminated again.
- All PENDING leave requests are auto-cancelled on termination.
- Active salary record end-dated to p_termination_date.
- All active pay elements end-dated to p_termination_date.

Exceptions: -20005 — already terminated

Database tables read/written: EMPLOYEES, LEAVE_REQUESTS, SALARY_RECORDS, EMPLOYEE_PAY_ELEMENTS
External services: PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action, PKG_COMMON.log_error

---

**PROCEDURE rehire_employee(...)**

Parameters:
- p_emp_id IN NUMBER
- p_rehire_date IN DATE
- p_dept_id IN NUMBER
- p_job_id IN NUMBER
- p_base_salary IN NUMBER
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. validate_dept(p_dept_id)
2. UPDATE EMPLOYEES SET EMPLOYMENT_STATUS='ACTIVE', HIRE_DATE=p_rehire_date, TERMINATION_DATE=NULL, TERMINATION_REASON=NULL, DEPT_ID=p_dept_id, JOB_ID=p_job_id, ACTIVE_FLAG='Y', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID=p_emp_id
3. IF SQL%ROWCOUNT = 0: RAISE_APPLICATION_ERROR(-20001, 'Employee not found for rehire: ' || p_emp_id)
4. PKG_PAYROLL.create_salary_record(p_emp_id, p_rehire_date, p_base_salary, 'REHIRE', p_user)
5. log_history(p_emp_id, 'REHIRE', p_rehire_date, new_dept/job/salary)
6. PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)

Business rule: Rehire clears TERMINATION_DATE and TERMINATION_REASON; resets HIRE_DATE to rehire date; sets ACTIVE_FLAG='Y'.

Database tables written: EMPLOYEES
External services: PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action

---

**FUNCTION get_direct_reports(p_manager_emp_id IN NUMBER) RETURN t_emp_id_table**

Logic:
1. Cursor loop: SELECT EMP_ID FROM EMPLOYEES WHERE MANAGER_EMP_ID = p_manager_emp_id AND EMPLOYMENT_STATUS = 'ACTIVE' ORDER BY LAST_NAME, FIRST_NAME
2. Accumulates into indexed table v_result(v_idx) := r.EMP_ID
3. Returns populated table

Business rule: Only ACTIVE employees are included.

Database tables read: EMPLOYEES

---

**FUNCTION get_org_chart(p_root_emp_id IN NUMBER, p_max_depth IN NUMBER DEFAULT 10) RETURN t_emp_cursor**

Logic:
1. Opens ref cursor with hierarchical query:
   SELECT LEVEL AS depth, EMP_ID, EMP_NUMBER, FIRST_NAME, LAST_NAME, DEPT_ID, JOB_ID, MANAGER_EMP_ID FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' START WITH EMP_ID = p_root_emp_id CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID AND LEVEL <= p_max_depth ORDER SIBLINGS BY LAST_NAME, FIRST_NAME

Documented issue: Known to time out for orgs with >500 employees.

Database tables read: EMPLOYEES

---

**FUNCTION get_headcount_by_dept(p_dept_id IN NUMBER DEFAULT NULL, p_as_of_date IN DATE DEFAULT SYSDATE) RETURN NUMBER**

Logic:
1. SELECT COUNT(*) FROM EMPLOYEES WHERE (p_dept_id IS NULL OR DEPT_ID = p_dept_id) AND EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= p_as_of_date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date)

Business rule: Active employees hired on or before as_of_date, and either not terminated or terminated after as_of_date.

Database tables read: EMPLOYEES

---

**FUNCTION get_tenure_years(p_emp_id IN NUMBER) RETURN NUMBER**

Logic:
1. SELECT HIRE_DATE, NVL(TERMINATION_DATE, SYSDATE) INTO v_hire_date, v_end_date FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN ROUND(MONTHS_BETWEEN(v_end_date, v_hire_date) / 12, 1)
3. EXCEPTION WHEN NO_DATA_FOUND: RETURN NULL

Business rule: Tenure in years = ROUND(MONTHS_BETWEEN(end_date, hire_date) / 12, 1). Uses SYSDATE as end date for active employees.

Database tables read: EMPLOYEES

---

**FUNCTION is_active(p_emp_id IN NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT EMPLOYMENT_STATUS INTO v_status FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_status = 'ACTIVE'
3. EXCEPTION WHEN NO_DATA_FOUND: RETURN FALSE

Database tables read: EMPLOYEES

---

**FUNCTION validate_employee(p_emp_id IN NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT * INTO v_emp FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. IF v_emp.FIRST_NAME IS NULL OR v_emp.LAST_NAME IS NULL: RETURN FALSE
3. IF v_emp.HIRE_DATE IS NULL: RETURN FALSE
4. IF v_emp.EMPLOYMENT_STATUS = 'ACTIVE' AND v_emp.ACTIVE_FLAG != 'Y': RETURN FALSE
5. RETURN TRUE
6. EXCEPTION WHEN NO_DATA_FOUND: RETURN FALSE

Business rules:
- Must have first and last name.
- Must have hire date.
- If EMPLOYMENT_STATUS = 'ACTIVE', ACTIVE_FLAG must be 'Y'.

Database tables read: EMPLOYEES

---

**FUNCTION emp_exists(p_emp_id IN NUMBER) RETURN BOOLEAN**

Logic:
1. SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE EMP_ID = p_emp_id
2. RETURN v_count > 0

Database tables read: EMPLOYEES

---

**PROCEDURE set_session_context(p_user IN VARCHAR2, p_emp_id IN NUMBER)**

Logic:
1. g_current_user := p_user
2. g_current_emp_id := p_emp_id
3. SELECT DEPT_ID INTO g_current_dept_id FROM EMPLOYEES WHERE EMP_ID = p_emp_id
4. EXCEPTION WHEN NO_DATA_FOUND: g_current_dept_id := NULL

Database tables read: EMPLOYEES

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks ===

**Package:** HRMS.PKG_INTEGRATION

**Types:**

`TYPE t_gl_entry IS RECORD:`
- journal_date: DATE
- account_code: VARCHAR2(30)
- debit_amount: NUMBER(15,2)
- credit_amount: NUMBER(15,2)
- description: VARCHAR2(200)
- reference: VARCHAR2(100)

`TYPE t_gl_entry_table IS TABLE OF t_gl_entry INDEX BY BINARY_INTEGER`

**Public Method Signatures:**

| Method | Kind | Parameters |
|---|---|---|
| generate_gl_journal | PROCEDURE | p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER |
| export_benefits_feed | PROCEDURE | p_effective_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER |
| import_time_attendance | PROCEDURE | p_file_name IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER |
| sync_org_structure | PROCEDURE | p_user IN VARCHAR2 DEFAULT USER |
| get_integration_status | FUNCTION | p_integration_name IN VARCHAR2 → RETURN VARCHAR2 |

**Dependencies:** PKG_COMMON, PKG_PAYROLL, PKG_EMPLOYEE
**Callers:** Batch scheduler (nightly GL feed, weekly benefits sync)

**Known issues documented:**
- GL posting uses flat file exchange (UTL_FILE) instead of API
- Benefits feed format is vendor-specific (ADP format)
- No retry logic for failed file transfers
- FTP credentials stored in SYSTEM_PARAMETERS table (cleartext)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb ===

**Package:** HRMS.PKG_INTEGRATION (body)

**Private Constants:**
| Constant | Type | Value |
|---|---|---|
| c_gl_output_dir | VARCHAR2(30) | 'GL_FEED_OUT' |
| c_benefits_output_dir | VARCHAR2(30) | 'BENEFITS_FEED_OUT' |
| c_time_input_dir | VARCHAR2(30) | 'TIME_ATTENDANCE_IN' |

These map to Oracle directory objects.

---

**PROCEDURE generate_gl_journal(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. v_filename := 'GL_JOURNAL_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD') || '.dat'
2. Open UTL_FILE in directory 'GL_FEED_OUT', mode 'W', buffer 32767
3. Write header: 'H|HRMS_PAYROLL|<YYYY-MM-DD>|<p_run_id>'
4. Cursor query:
   ```
   SELECT d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE,
          SUM(pd.AMOUNT) AS TOTAL_AMOUNT, pp.PERIOD_NAME
   FROM PAYROLL_DETAILS pd
   JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
   JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID
   JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
   JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
   JOIN PAY_ELEMENTS pe ON pd.ELEMENT_ID = pe.ELEMENT_ID
   WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR' AND pe.GL_ACCOUNT_CODE IS NOT NULL
   GROUP BY d.COST_CENTER, pe.GL_ACCOUNT_CODE, pe.ELEMENT_TYPE, pp.PERIOD_NAME
   ```
5. For each row:
   - If ELEMENT_TYPE = 'EARNING': write 'D|<COST_CENTER>|<GL_ACCOUNT_CODE>|<debit_amount>|0.00|Payroll <PERIOD_NAME>|RUN-<p_run_id>'
   - Else: write 'D|<COST_CENTER>|<GL_ACCOUNT_CODE>|0.00|<credit_amount>|Payroll <PERIOD_NAME>|RUN-<p_run_id>'
   - Amounts formatted with TO_CHAR(ABS(TOTAL_AMOUNT), 'FM999999990.00')
6. Write trailer: 'T|<v_entries>'
7. Close file
8. Log info via PKG_COMMON.log_info
9. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

File format: Pipe-delimited. Consumed by Oracle Financials batch import.
Business rule: Earnings generate debit entries to expense accounts; Deductions/Taxes generate credit entries to liability accounts.

Database tables read: PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS, EMPLOYEES, DEPARTMENTS, PAY_ELEMENTS
External file I/O: UTL_FILE write to Oracle directory 'GL_FEED_OUT'
External services: PKG_COMMON.log_info, PKG_COMMON.log_error

---

**PROCEDURE export_benefits_feed(p_effective_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. v_filename := 'BENEFITS_' || TO_CHAR(SYSDATE, 'YYYYMMDD') || '.txt'
2. Open UTL_FILE in directory 'BENEFITS_FEED_OUT', mode 'W', buffer 32767
3. Cursor query:
   ```
   SELECT e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME, e.DATE_OF_BIRTH, e.HIRE_DATE,
          e.EMPLOYMENT_STATUS, e.MARITAL_STATUS, e.GENDER,
          d.FIRST_NAME AS DEP_FIRST_NAME, d.LAST_NAME AS DEP_LAST_NAME,
          d.RELATIONSHIP, d.DATE_OF_BIRTH AS DEP_DOB
   FROM EMPLOYEES e
   LEFT JOIN EMPLOYEE_DEPENDENTS d ON e.EMP_ID = d.EMP_ID AND d.ACTIVE_FLAG = 'Y'
   WHERE e.EMPLOYMENT_STATUS = 'ACTIVE'
   ORDER BY e.EMP_NUMBER, d.DEPENDENT_ID
   ```
4. For each row, write fixed-width record:

   | Field | Width | Notes |
   |---|---|---|
   | EMP_NUMBER | 10 (RPAD) | |
   | FIRST_NAME | 30 (RPAD) | |
   | LAST_NAME | 30 (RPAD) | |
   | DATE_OF_BIRTH | 10 (RPAD) | formatted 'YYYY-MM-DD' |
   | HIRE_DATE | 10 (RPAD) | formatted 'YYYY-MM-DD' |
   | EMPLOYMENT_STATUS | 12 (RPAD) | |
   | MARITAL_STATUS | 10 (RPAD) | |
   | GENDER | 1 (RPAD) | |
   | DEP_FIRST_NAME | 30 (RPAD) | |
   | DEP_LAST_NAME | 30 (RPAD) | |
   | RELATIONSHIP | 20 (RPAD) | |
   | DEP_DOB | 10 (RPAD) | formatted 'YYYY-MM-DD' |
   | **Total record width** | **193** | |

5. Close file; log info; EXCEPTION WHEN OTHERS: close file; log_error; RAISE

File format: Fixed-width, ADP vendor format (legacy).

Database tables read: EMPLOYEES (EMP_NUMBER, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, HIRE_DATE, EMPLOYMENT_STATUS, MARITAL_STATUS, GENDER), EMPLOYEE_DEPENDENTS (EMP_ID, ACTIVE_FLAG, FIRST_NAME, LAST_NAME, RELATIONSHIP, DATE_OF_BIRTH, DEPENDENT_ID)
External file I/O: UTL_FILE write to Oracle directory 'BENEFITS_FEED_OUT'
External services: PKG_COMMON.log_info, PKG_COMMON.log_error

---

**PROCEDURE import_time_attendance(p_file_name IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. Open UTL_FILE in directory 'TIME_ATTENDANCE_IN', filename p_file_name, mode 'R', buffer 32767
2. Loop:
   - UTL_FILE.GET_LINE(v_file, v_line)
   - EXCEPTION WHEN NO_DATA_FOUND: EXIT (end of file)
   - Skip blank lines and lines starting with '#'
   - TODO: Parse CSV: emp_number, date, hours_regular, hours_overtime — actual parsing and database update NOT implemented
   - v_imported := v_imported + 1 on each valid-looking line
   - EXCEPTION WHEN OTHERS per line: v_errors := v_errors + 1; PKG_COMMON.log_error per line
3. Close file; log summary (Imported: N, Errors: N)
4. EXCEPTION WHEN OTHERS: close file; log_error; RAISE

Business rule: Lines beginning with '#' are treated as comments and skipped.
Note: Actual parsing and DB update is NOT implemented (TODO).

External file I/O: UTL_FILE read from Oracle directory 'TIME_ATTENDANCE_IN'
External services: PKG_COMMON.log_error, PKG_COMMON.log_info

---

**PROCEDURE sync_org_structure(p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. Placeholder only — logs 'Org structure sync completed'
2. PKG_COMMON.log_info('PKG_INTEGRATION', 'sync_org_structure', 'Org structure sync completed', p_user)

Note: Intended for LDAP/Active Directory sync; not implemented.

External services: PKG_COMMON.log_info

---

**FUNCTION get_integration_status(p_integration_name IN VARCHAR2) RETURN VARCHAR2**

Logic:
1. RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS')

Configuration key pattern: INTEGRATION.<p_integration_name>_STATUS (from SYSTEM_PARAMETERS via PKG_COMMON.get_param)

External services: PKG_COMMON.get_param

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks ===

**Package:** HRMS.PKG_LEAVE

**Custom Exceptions:**
| Exception Name | Error Code |
|---|---|
| e_insufficient_balance | -20201 |
| e_overlapping_leave | -20202 |
| e_invalid_leave_type | -20203 |
| e_approval_error | -20204 |

**Types:**
`TYPE t_leave_cursor IS REF CURSOR`

**Public Method Signatures:**

| Method | Kind | Parameters | Returns |
|---|---|---|---|
| submit_leave_request | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_start_date DATE, p_end_date DATE, p_half_day_flag CHAR DEFAULT 'N', p_half_day_period VARCHAR2 DEFAULT NULL, p_reason VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | NUMBER (request_id) |
| approve_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER | — |
| reject_leave_request | PROCEDURE | p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| cancel_leave_request | PROCEDURE | p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| get_leave_balance | FUNCTION | p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| adjust_leave_balance | PROCEDURE | p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| initialize_balances | PROCEDURE | p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| run_monthly_accrual | PROCEDURE | p_accrual_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER | — |
| process_carryover | PROCEDURE | p_year NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| expire_carryover | PROCEDURE | p_user VARCHAR2 DEFAULT USER | — |
| get_pending_requests | PROCEDURE | p_cursor OUT t_leave_cursor, p_approver_id NUMBER | — |
| get_team_calendar | PROCEDURE | p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE | — |
| calculate_business_days | FUNCTION | p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL | NUMBER |
| check_leave_overlap | FUNCTION | p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL | BOOLEAN |

**Dependencies:** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
**Callers:** HRMS_LEAVE form, self-service portal, batch accrual job

**Known issues documented:**
- Overlapping leave detection does not account for half-day requests
- Carryover expiry job sometimes double-expires if run twice on same day
- Holiday detection only checks exact date match, not observed dates

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb ===

**Package:** HRMS.PKG_LEAVE (body)

---

**FUNCTION calculate_business_days(p_start_date DATE, p_end_date DATE, p_location_code VARCHAR2 DEFAULT NULL) RETURN NUMBER**

Logic:
1. v_date := TRUNC(p_start_date)
2. WHILE v_date <= TRUNC(p_end_date) LOOP:
   - IF TO_CHAR(v_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN') NOT IN ('SAT', 'SUN') THEN:
     - SELECT COUNT(*) FROM HOLIDAYS WHERE HOLIDAY_DATE = v_date AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)
     - If holiday count = 0: v_count := v_count + 1
   - v_date := v_date + 1
3. RETURN v_count

Business rules:
- Weekends (SAT, SUN) are not business days.
- Dates in HOLIDAYS table with ACTIVE_FLAG='Y' and matching LOCATION_CODE (or global holidays where LOCATION_CODE IS NULL) are excluded.

Documented bug: Does not handle "observed" holidays (e.g., if July 4 falls on Saturday, the observed Friday is not excluded).

Database tables read: HOLIDAYS (HOLIDAY_DATE, ACTIVE_FLAG, LOCATION_CODE)

---

**FUNCTION check_leave_overlap(p_emp_id NUMBER, p_start_date DATE, p_end_date DATE, p_exclude_request_id NUMBER DEFAULT NULL) RETURN BOOLEAN**

Logic:
1. SELECT COUNT(*) FROM LEAVE_REQUESTS WHERE EMP_ID = p_emp_id AND STATUS IN ('PENDING', 'APPROVED') AND (p_exclude_request_id IS NULL OR REQUEST_ID != p_exclude_request_id) AND START_DATE <= p_end_date AND END_DATE >= p_start_date
2. RETURN v_count > 0

Business rule: Overlap check covers PENDING and APPROVED requests using date range intersection.

Database tables read: LEAVE_REQUESTS (EMP_ID, STATUS, REQUEST_ID, START_DATE, END_DATE)

---

**FUNCTION submit_leave_request(...) RETURN NUMBER**

Parameters:
- p_emp_id IN NUMBER
- p_leave_type_id IN NUMBER
- p_start_date IN DATE
- p_end_date IN DATE
- p_half_day_flag IN CHAR DEFAULT 'N'
- p_half_day_period IN VARCHAR2 DEFAULT NULL
- p_reason IN VARCHAR2 DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. SELECT * INTO v_emp_rec FROM EMPLOYEES WHERE EMP_ID = p_emp_id AND EMPLOYMENT_STATUS = 'ACTIVE'
   - EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20001, 'Employee not found or not active: ' || p_emp_id)
2. SELECT * INTO v_leave_type FROM LEAVE_TYPES WHERE LEAVE_TYPE_ID = p_leave_type_id AND ACTIVE_FLAG = 'Y'
   - EXCEPTION WHEN NO_DATA_FOUND: RAISE_APPLICATION_ERROR(-20203, 'Invalid leave type: ' || p_leave_type_id)
3. Tenure check: IF v_leave_type.MIN_TENURE_DAYS > 0 AND SYSDATE - v_emp_rec.HIRE_DATE < v_leave_type.MIN_TENURE_DAYS THEN RAISE_APPLICATION_ERROR(-20203, 'Minimum tenure of ' || MIN_TENURE_DAYS || ' days not met for leave type: ' || LEAVE_TYPE_NAME)
4. Validate dates: IF p_start_date > p_end_date: RAISE_APPLICATION_ERROR(-20210, 'Start date must be before or equal to end date')
5. Backdated request limit: IF p_start_date < TRUNC(SYSDATE) AND TRUNC(SYSDATE) - p_start_date > 5: RAISE_APPLICATION_ERROR(-20211, 'Cannot submit leave requests more than 5 days in the past')
6. Calculate total days:
   - If p_half_day_flag = 'Y': v_total_days := 0.5
   - Else: v_total_days := calculate_business_days(p_start_date, p_end_date, v_emp_rec.LOCATION_CODE)
7. IF v_total_days <= 0: RAISE_APPLICATION_ERROR(-20212, 'No business days in the selected range')
8. Overlap check: IF check_leave_overlap(p_emp_id, p_start_date, p_end_date): RAISE_APPLICATION_ERROR(-20202, 'Leave request overlaps with an existing request')
9. Balance check (only if v_leave_type.ACCRUAL_FLAG = 'Y'):
   - v_balance := get_leave_balance(p_emp_id, p_leave_type_id)
   - IF v_balance < v_total_days: RAISE_APPLICATION_ERROR(-20201, 'Insufficient leave balance. Available: ' || v_balance || ', Requested: ' || v_total_days)
10. SELECT SEQ_LEAVE_REQUEST.NEXTVAL INTO v_request_id FROM DUAL
11. v_manager_id := v_emp_rec.MANAGER_EMP_ID
12. INSERT INTO LEAVE_REQUESTS (REQUEST_ID, EMP_ID, LEAVE_TYPE_ID, START_DATE, END_DATE, TOTAL_DAYS, HALF_DAY_FLAG, HALF_DAY_PERIOD, STATUS, REASON, APPROVER_EMP_ID, CREATED_BY, CREATED_DATE)
    - STATUS = CASE WHEN v_leave_type.REQUIRES_APPROVAL = 'Y' THEN 'PENDING' ELSE 'APPROVED' END
13. UPDATE LEAVE_BALANCES SET PENDING = PENDING + v_total_days WHERE EMP_ID = p_emp_id AND LEAVE_TYPE_ID = p_leave_type_id AND CALENDAR_YEAR = EXTRACT(YEAR FROM p_start_date)
14. If v_manager_id IS NOT NULL AND REQUIRES_APPROVAL = 'Y': PKG_NOTIFICATION.send_notification to manager: subject='Leave Request Pending Approval', body includes employee name, days, leave type name, dates in MM/DD/YYYY format
15. If REQUIRES_APPROVAL = 'N': call approve_leave_request(v_request_id, NULL, 'Auto-approved', p_user)
16. PKG_AUDIT.log_action('LEAVE_REQUESTS', v_request_id, 'INSERT', p_user)
17. RETURN v_request_id

Business rules:
- Employee must be ACTIVE.
- Leave type must be ACTIVE.
- Minimum tenure (in days) must be met.
- End date must be >= start date.
- Backdating limit: maximum 5 days in the past.
- Half-day requests = 0.5 days (fixed); full requests = calculated business days.
- Zero business days is rejected.
- Overlapping PENDING or APPROVED requests block submission.
- Balance check applies only to accrual-based leave types (ACCRUAL_FLAG = 'Y').
- If REQUIRES_APPROVAL = 'N', auto-approved immediately.
- LEAVE_BALANCES.PENDING incremented on submission (regardless of REQUIRES_APPROVAL).

Exceptions:
- -20001 — employee not found or not active
- -20203 — invalid leave type or tenure not met
- -20210 — start date after end date
- -20211 — more than 5 days in the past
- -20212 — no business days in range
- -20202 — overlapping leave request
- -20201 — insufficient balance

Sequences: SEQ_LEAVE_REQUEST
Database tables read: EMPLOYEES, LEAVE_TYPES, LEAVE_BALANCES
Database tables written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_NOTIFICATION.send_notification, approve_leave_request (self-call), PKG_AUDIT.log_action

---

**PROCEDURE approve_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2 DEFAULT NULL, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT * INTO v_request FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE
2. IF v_request.STATUS != 'PENDING': RAISE_APPLICATION_ERROR(-20204, 'Cannot approve request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='APPROVED', APPROVER_EMP_ID=p_approver_emp_id, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS=p_comments, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE REQUEST_ID=p_request_id
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS, USED = USED + v_request.TOTAL_DAYS WHERE EMP_ID=v_request.EMP_ID AND LEAVE_TYPE_ID=v_request.LEAVE_TYPE_ID AND CALENDAR_YEAR=EXTRACT(YEAR FROM v_request.START_DATE)
5. PKG_NOTIFICATION.send_notification to employee: subject='Leave Request Approved', body includes start/end dates in MM/DD/YYYY
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

Business rules:
- Only PENDING requests can be approved.
- Balance moves from PENDING to USED on approval.

Exceptions: -20204 — cannot approve in current status

Database tables read/written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action

---

**PROCEDURE reject_leave_request(p_request_id NUMBER, p_approver_emp_id NUMBER, p_comments VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT * FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE
2. IF STATUS != 'PENDING': RAISE_APPLICATION_ERROR(-20204, 'Cannot reject request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='REJECTED', APPROVER_EMP_ID=p_approver_emp_id, APPROVAL_DATE=SYSDATE, APPROVAL_COMMENTS=p_comments, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE
4. UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS (release pending balance)
5. PKG_NOTIFICATION.send_notification to employee: subject='Leave Request Rejected', body='Your leave request has been rejected. Reason: ' || p_comments
6. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

Business rules:
- Only PENDING requests can be rejected.
- Pending balance released on rejection.

Exceptions: -20204 — cannot reject in current status

Database tables written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action

---

**PROCEDURE cancel_leave_request(p_request_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT * FROM LEAVE_REQUESTS WHERE REQUEST_ID = p_request_id FOR UPDATE
2. IF STATUS NOT IN ('PENDING', 'APPROVED'): RAISE_APPLICATION_ERROR(-20204, 'Cannot cancel request in status: ' || v_request.STATUS)
3. UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON=p_reason, CANCELLED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE
4. Balance restoration:
   - If was PENDING: UPDATE LEAVE_BALANCES SET PENDING = PENDING - v_request.TOTAL_DAYS
   - If was APPROVED: UPDATE LEAVE_BALANCES SET USED = USED - v_request.TOTAL_DAYS
5. PKG_AUDIT.log_action('LEAVE_REQUESTS', p_request_id, 'UPDATE', p_user)

Business rules:
- Only PENDING or APPROVED requests can be cancelled.
- Cancelling PENDING restores PENDING balance.
- Cancelling APPROVED restores USED balance.

Exceptions: -20204 — cannot cancel in current status

Database tables written: LEAVE_REQUESTS, LEAVE_BALANCES
External services: PKG_AUDIT.log_action

---

**FUNCTION get_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
1. SELECT OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING INTO v_balance FROM LEAVE_BALANCES WHERE EMP_ID = p_emp_id AND LEAVE_TYPE_ID = p_leave_type_id AND CALENDAR_YEAR = p_year
2. RETURN NVL(v_balance, 0)
3. EXCEPTION WHEN NO_DATA_FOUND: RETURN 0

Business rule (balance formula): Available Balance = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING

Database tables read: LEAVE_BALANCES (OPENING_BALANCE, ACCRUED, USED, ADJUSTMENT, PENDING)

---

**PROCEDURE adjust_leave_balance(p_emp_id NUMBER, p_leave_type_id NUMBER, p_adjustment NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT + p_adjustment WHERE EMP_ID = p_emp_id AND LEAVE_TYPE_ID = p_leave_type_id AND CALENDAR_YEAR = EXTRACT(YEAR FROM SYSDATE)
2. IF SQL%ROWCOUNT = 0: initialize_balances(p_emp_id, EXTRACT(YEAR FROM SYSDATE), p_user) then retry same UPDATE
3. PKG_AUDIT.log_action('LEAVE_BALANCES', p_emp_id, 'UPDATE', p_user)

Database tables written: LEAVE_BALANCES
External services: PKG_AUDIT.log_action

---

**PROCEDURE initialize_balances(p_emp_id NUMBER, p_year NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. For each LEAVE_TYPES row where ACTIVE_FLAG = 'Y':
   - INSERT INTO LEAVE_BALANCES (BALANCE_ID, EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR, OPENING_BALANCE, ACCRUED, USED, ADJUSTMENT, PENDING, CREATED_BY, CREATED_DATE) VALUES (SEQ_LEAVE_BALANCE.NEXTVAL, p_emp_id, lt.LEAVE_TYPE_ID, p_year, 0, 0, 0, 0, 0, p_user, SYSDATE)
   - EXCEPTION WHEN DUP_VAL_ON_INDEX: NULL (skip if already exists)

Business rule: All active leave types get a balance record initialized to zeros.

Sequences: SEQ_LEAVE_BALANCE
Database tables read: LEAVE_TYPES (LEAVE_TYPE_ID, ACTIVE_FLAG)
Database tables written: LEAVE_BALANCES

---

**PROCEDURE run_monthly_accrual(p_accrual_date DATE DEFAULT SYSDATE, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. Outer cursor: all ACTIVE employees with ACTIVE_FLAG = 'Y'
2. Inner cursor: LEAVE_TYPES where ACTIVE_FLAG='Y' AND ACCRUAL_FLAG='Y' AND ACCRUAL_FREQUENCY='MONTHLY'
   - Columns read: LEAVE_TYPE_ID, ACCRUAL_RATE, ACCRUAL_FREQUENCY, MAX_BALANCE, MIN_TENURE_DAYS
3. For each employee × leave type:
   a. Check tenure: IF TRUNC(p_accrual_date) - emp.HIRE_DATE >= lt.MIN_TENURE_DAYS
   b. Get current balance via get_leave_balance(emp.EMP_ID, lt.LEAVE_TYPE_ID, EXTRACT(YEAR FROM p_accrual_date))
   c. Determine accrual amount:
      - If MAX_BALANCE IS NULL OR current_balance + ACCRUAL_RATE <= MAX_BALANCE: v_accrued := ACCRUAL_RATE
      - Else: v_accrued := GREATEST(0, MAX_BALANCE - current_balance)  — caps at maximum
   d. If v_accrued > 0:
      - UPDATE LEAVE_BALANCES SET ACCRUED = ACCRUED + v_accrued WHERE EMP_ID=emp.EMP_ID AND LEAVE_TYPE_ID=lt.LEAVE_TYPE_ID AND CALENDAR_YEAR=EXTRACT(YEAR FROM p_accrual_date)
      - If SQL%ROWCOUNT = 0: initialize_balances then retry UPDATE with ACCRUED = v_accrued (not += on retry)
      - INSERT INTO LEAVE_ACCRUAL_LOG (ACCRUAL_ID, EMP_ID, LEAVE_TYPE_ID, ACCRUAL_DATE, ACCRUAL_AMOUNT, CREATED_BY, CREATED_DATE)
4. COMMIT every 100 employees (MOD(v_total_employees, 100) = 0)
5. Final COMMIT
6. DBMS_OUTPUT progress messages

Business rules:
- Only MONTHLY accrual frequency processed.
- Tenure gate: employee must meet MIN_TENURE_DAYS before accruing.
- Accrual is capped at MAX_BALANCE; partial accrual allowed (GREATEST(0, MAX_BALANCE - current)).
- Commits every 100 employees (partial-commit risk on failure).

Sequences: SEQ_LEAVE_ACCRUAL
Database tables read: EMPLOYEES, LEAVE_TYPES, LEAVE_BALANCES
Database tables written: LEAVE_BALANCES, LEAVE_ACCRUAL_LOG

---

**PROCEDURE process_carryover(p_year NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. v_next_year := p_year + 1
2. Cursor:
   ```
   SELECT lb.EMP_ID, lb.LEAVE_TYPE_ID,
          lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT AS REMAINING,
          lt.CARRYOVER_MAX, lt.CARRYOVER_EXPIRY
   FROM LEAVE_BALANCES lb
   JOIN LEAVE_TYPES lt ON lb.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
   WHERE lb.CALENDAR_YEAR = p_year
   AND lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT > 0
   ```
3. v_carryover := bal_rec.REMAINING
4. If CARRYOVER_MAX IS NOT NULL: v_carryover := LEAST(v_carryover, CARRYOVER_MAX)
5. If v_carryover > 0:
   - initialize_balances(emp_id, next_year, p_user)
   - UPDATE LEAVE_BALANCES SET CARRYOVER_FROM_PREV = v_carryover, OPENING_BALANCE = v_carryover, CARRYOVER_EXPIRY_DT = CASE WHEN CARRYOVER_EXPIRY IS NOT NULL THEN ADD_MONTHS(TO_DATE(next_year || '-01-01', 'YYYY-MM-DD'), CARRYOVER_EXPIRY) ELSE NULL END WHERE EMP_ID=emp_id AND LEAVE_TYPE_ID=lt_id AND CALENDAR_YEAR=next_year
6. COMMIT

Business rules:
- Only positive remaining balances are carried over.
- Carryover is capped by CARRYOVER_MAX if set.
- Expiry date = January 1 of next year + CARRYOVER_EXPIRY months (if set).
- OPENING_BALANCE for next year is set to carryover amount.

Database tables read: LEAVE_BALANCES, LEAVE_TYPES
Database tables written: LEAVE_BALANCES

---

**PROCEDURE expire_carryover(p_user IN VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT - CARRYOVER_FROM_PREV, CARRYOVER_FROM_PREV = 0, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE CARRYOVER_EXPIRY_DT <= TRUNC(SYSDATE) AND CARRYOVER_FROM_PREV > 0
2. COMMIT

Documented bug: If run twice on same day, can double-subtract (CARRYOVER_FROM_PREV is set to 0 after first run so second run WHERE CARRYOVER_FROM_PREV > 0 would not match — the bug is actually in the description but examining the code: after setting CARRYOVER_FROM_PREV = 0, second run WHERE CARRYOVER_FROM_PREV > 0 should not match. However, the expiry date check <= SYSDATE means within a single transaction window it could be a concern).

Database tables written: LEAVE_BALANCES

---

**PROCEDURE get_pending_requests(p_cursor OUT t_leave_cursor, p_approver_id NUMBER)**

Logic: Opens ref cursor:
```sql
SELECT lr.REQUEST_ID, lr.EMP_ID,
       e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME,
       lt.LEAVE_TYPE_NAME,
       lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS,
       lr.REASON, lr.CREATED_DATE
FROM LEAVE_REQUESTS lr
JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
WHERE lr.STATUS = 'PENDING'
AND lr.APPROVER_EMP_ID = p_approver_id
ORDER BY lr.CREATED_DATE
```

Database tables read: LEAVE_REQUESTS, EMPLOYEES, LEAVE_TYPES

---

**PROCEDURE get_team_calendar(p_cursor OUT t_leave_cursor, p_manager_id NUMBER, p_start_date DATE, p_end_date DATE)**

Logic: Opens ref cursor:
```sql
SELECT e.EMP_ID, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMPLOYEE_NAME,
       lt.LEAVE_TYPE_NAME, lt.LEAVE_TYPE_CODE,
       lr.START_DATE, lr.END_DATE, lr.TOTAL_DAYS,
       lr.STATUS, lr.HALF_DAY_FLAG
FROM LEAVE_REQUESTS lr
JOIN EMPLOYEES e ON lr.EMP_ID = e.EMP_ID
JOIN LEAVE_TYPES lt ON lr.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID
WHERE e.MANAGER_EMP_ID = p_manager_id
AND lr.STATUS IN ('APPROVED', 'TAKEN')
AND lr.START_DATE <= p_end_date
AND lr.END_DATE >= p_start_date
ORDER BY lr.START_DATE, e.LAST_NAME
```

Database tables read: LEAVE_REQUESTS, EMPLOYEES, LEAVE_TYPES

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks ===

**Package:** HRMS.PKG_NOTIFICATION

**Dependencies:** PKG_COMMON
**Callers:** PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE

**Known issues:**
- UTL_MAIL configuration hard-coded to legacy SMTP server
- No rate limiting — bulk operations can flood the queue
- HTML email templates stored as string constants (maintenance nightmare)

**Public Method Signatures:**

| Method | Kind | Parameters |
|---|---|---|
| send_notification | PROCEDURE | p_recipient_emp_id NUMBER DEFAULT NULL, p_recipient_email VARCHAR2 DEFAULT NULL, p_type VARCHAR2 DEFAULT 'EMAIL', p_subject VARCHAR2, p_body CLOB, p_priority NUMBER DEFAULT 5, p_reference_table VARCHAR2 DEFAULT NULL, p_reference_id NUMBER DEFAULT NULL, p_user VARCHAR2 DEFAULT USER |
| process_queue | PROCEDURE | p_batch_size NUMBER DEFAULT 50, p_user VARCHAR2 DEFAULT USER |
| retry_failed | PROCEDURE | p_max_retries NUMBER DEFAULT 3, p_user VARCHAR2 DEFAULT USER |
| cancel_notification | PROCEDURE | p_notification_id NUMBER, p_user VARCHAR2 DEFAULT USER |

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb ===

**Package:** HRMS.PKG_NOTIFICATION (body)

**Private Constants:**
| Constant | Type | Value |
|---|---|---|
| c_smtp_host | VARCHAR2(100) | 'smtp.internal.company.com' |
| c_smtp_port | NUMBER | 25 |
| c_from_address | VARCHAR2(100) | 'hrms-noreply@company.com' |
| c_from_name | VARCHAR2(100) | 'HRMS System' |

Note: Hard-coded values; documented that they should be in SYSTEM_PARAMETERS.

---

**PROCEDURE send_notification(...) — PRAGMA AUTONOMOUS_TRANSACTION**

Parameters:
- p_recipient_emp_id IN NUMBER DEFAULT NULL
- p_recipient_email IN VARCHAR2 DEFAULT NULL
- p_type IN VARCHAR2 DEFAULT 'EMAIL'
- p_subject IN VARCHAR2
- p_body IN CLOB
- p_priority IN NUMBER DEFAULT 5
- p_reference_table IN VARCHAR2 DEFAULT NULL
- p_reference_id IN NUMBER DEFAULT NULL
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. PRAGMA AUTONOMOUS_TRANSACTION
2. Resolve email: if p_recipient_email IS NULL AND p_recipient_emp_id IS NOT NULL: SELECT EMAIL INTO v_email FROM EMPLOYEES WHERE EMP_ID = p_recipient_emp_id; EXCEPTION WHEN NO_DATA_FOUND: v_email := NULL
3. Else: v_email := p_recipient_email
4. INSERT INTO NOTIFICATION_QUEUE (NOTIFICATION_ID, RECIPIENT_EMP_ID, RECIPIENT_EMAIL, NOTIFICATION_TYPE, SUBJECT, BODY, STATUS, PRIORITY, REFERENCE_TABLE, REFERENCE_ID, CREATED_BY, CREATED_DATE) VALUES (SEQ_NOTIFICATION.NEXTVAL, ..., 'PENDING', p_priority, ...)
5. COMMIT
6. EXCEPTION WHEN OTHERS: ROLLBACK; PKG_COMMON.log_error — notification failures never block business operations

Business rules:
- Email resolved from EMPLOYEES table if not provided directly.
- Notification is async — written to queue with STATUS='PENDING'.
- Errors are silently swallowed (autonomous transaction rolls back; main transaction unaffected).
- Default priority: 5.

Sequences: SEQ_NOTIFICATION
Database tables read: EMPLOYEES (EMAIL)
Database tables written: NOTIFICATION_QUEUE
External services: PKG_COMMON.log_error

---

**PROCEDURE process_queue(p_batch_size NUMBER DEFAULT 50, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. Cursor: SELECT NOTIFICATION_ID, RECIPIENT_EMAIL, SUBJECT, BODY, NOTIFICATION_TYPE FROM NOTIFICATION_QUEUE WHERE STATUS='PENDING' AND NOTIFICATION_TYPE='EMAIL' AND RECIPIENT_EMAIL IS NOT NULL ORDER BY PRIORITY ASC, CREATED_DATE ASC FETCH FIRST p_batch_size ROWS ONLY
2. For each notification:
   a. v_connection := UTL_SMTP.OPEN_CONNECTION('smtp.internal.company.com', 25)
   b. UTL_SMTP.HELO(v_connection, 'smtp.internal.company.com')
   c. UTL_SMTP.MAIL(v_connection, 'hrms-noreply@company.com')
   d. UTL_SMTP.RCPT(v_connection, RECIPIENT_EMAIL)
   e. UTL_SMTP.OPEN_DATA(v_connection)
   f. Write headers:
      - 'From: HRMS System <hrms-noreply@company.com>' + CRLF
      - 'To: ' + RECIPIENT_EMAIL + CRLF
      - 'Subject: ' + SUBJECT + CRLF
      - 'Content-Type: text/plain; charset=UTF-8' + CRLF
      - CRLF (blank line)
   g. Write body
   h. UTL_SMTP.CLOSE_DATA; UTL_SMTP.QUIT
   i. UPDATE NOTIFICATION_QUEUE SET STATUS='SENT', SENT_DATE=SYSDATE WHERE NOTIFICATION_ID=...
   j. v_sent := v_sent + 1
   k. EXCEPTION WHEN OTHERS: UPDATE NOTIFICATION_QUEUE SET STATUS='FAILED', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000), RETRY_COUNT=RETRY_COUNT+1; v_failed++; try UTL_SMTP.QUIT
3. COMMIT
4. Log if sent > 0 OR failed > 0 via PKG_COMMON.log_info

Business rules:
- Batch size default: 50 records per invocation.
- Only EMAIL type with non-null RECIPIENT_EMAIL are processed.
- Priority order: lower number = higher priority (ORDER BY PRIORITY ASC).
- Within same priority: oldest first (CREATED_DATE ASC).
- One SMTP connection opened per message (inefficient; no connection reuse).
- Failed messages have RETRY_COUNT incremented.

External services called: UTL_SMTP (OPEN_CONNECTION, HELO, MAIL, RCPT, OPEN_DATA, WRITE_DATA, CLOSE_DATA, QUIT), UTL_TCP (CRLF constant), PKG_COMMON.log_info
Database tables written: NOTIFICATION_QUEUE

---

**PROCEDURE retry_failed(p_max_retries NUMBER DEFAULT 3, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE NOTIFICATION_QUEUE SET STATUS='PENDING', ERROR_MESSAGE=NULL WHERE STATUS='FAILED' AND RETRY_COUNT < p_max_retries
2. COMMIT

Business rule: Failed notifications with RETRY_COUNT < 3 (default) are reset to PENDING for reprocessing.

Database tables written: NOTIFICATION_QUEUE

---

**PROCEDURE cancel_notification(p_notification_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE NOTIFICATION_QUEUE SET STATUS='CANCELLED' WHERE NOTIFICATION_ID = p_notification_id AND STATUS = 'PENDING'

Business rule: Only PENDING notifications can be cancelled.

Database tables written: NOTIFICATION_QUEUE

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks ===

**Package:** HRMS.PKG_PAYROLL

**Custom Exceptions:**
| Exception Name | Error Code |
|---|---|
| e_invalid_salary | -20101 |
| e_period_closed | -20102 |
| e_run_already_paid | -20103 |
| e_calculation_error | -20104 |

**Types:**

`TYPE t_payslip_rec IS RECORD:`
- emp_id: NUMBER(10)
- emp_number: VARCHAR2(20)
- emp_name: VARCHAR2(101)
- period_name: VARCHAR2(50)
- gross_pay: NUMBER(12,2)
- total_deductions: NUMBER(12,2)
- net_pay: NUMBER(12,2)
- federal_tax: NUMBER(12,2)
- state_tax: NUMBER(12,2)
- social_security: NUMBER(12,2)
- medicare: NUMBER(12,2)
- ytd_gross: NUMBER(15,2)
- ytd_net: NUMBER(15,2)

`TYPE t_payslip_cursor IS REF CURSOR`

**Public Method Signatures:**

| Method | Kind | Parameters | Returns |
|---|---|---|---|
| create_salary_record | PROCEDURE | p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2 DEFAULT NULL, p_change_pct NUMBER DEFAULT NULL, p_currency_code VARCHAR2 DEFAULT 'USD', p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| get_current_salary | FUNCTION | p_emp_id NUMBER | NUMBER |
| get_salary_as_of | FUNCTION | p_emp_id NUMBER, p_as_of DATE | NUMBER |
| create_pay_periods | PROCEDURE | p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER | — |
| close_pay_period | PROCEDURE | p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| get_current_period | FUNCTION | (none) | NUMBER |
| create_payroll_run | FUNCTION | p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER | NUMBER |
| calculate_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| calculate_employee_pay | PROCEDURE | p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| approve_payroll | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |
| reverse_payroll | PROCEDURE | p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER | — |
| calculate_federal_tax | FUNCTION | p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_state_tax | FUNCTION | p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY' | NUMBER |
| calculate_fica | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| calculate_medicare | FUNCTION | p_gross_pay NUMBER, p_ytd_gross NUMBER | NUMBER |
| get_payslip | PROCEDURE | p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL | — |
| get_ytd_earnings | FUNCTION | p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE) | NUMBER |
| generate_pay_register | PROCEDURE | p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER | — |

**Dependencies:** PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
**Callers:** HRMS_PAYROLL form, batch scheduler (DBMS_SCHEDULER)

**Known issues documented:**
- Circular dependency with PKG_EMPLOYEE (is_active check)
- Tax calculation uses hard-coded 2024 brackets in some paths
- Overtime calculation does not account for holidays correctly
- YTD accumulation resets incorrectly for mid-year hires in some edge cases

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb ===

**Package:** HRMS.PKG_PAYROLL (body)

**Private Constants:**
| Constant | Type | Value | Description |
|---|---|---|---|
| c_ss_wage_base_2024 | NUMBER | 168600 | Social Security wage base (2024) |
| c_ss_rate | NUMBER | 0.062 | Employee SS share: 6.2% |
| c_medicare_rate | NUMBER | 0.0145 | Employee Medicare share: 1.45% |
| c_medicare_addl_rate | NUMBER | 0.009 | Additional Medicare tax: 0.9% |
| c_medicare_addl_threshold | NUMBER | 200000 | Threshold for additional Medicare tax |
| c_standard_deduction_single | NUMBER | 14600 | 2024 standard deduction — single/separate |
| c_standard_deduction_married | NUMBER | 29200 | 2024 standard deduction — married filing jointly |
| c_allowance_amount | NUMBER | 4300 | Per-allowance reduction amount |

---

**PROCEDURE create_salary_record(...)**

Parameters:
- p_emp_id IN NUMBER
- p_effective_date IN DATE
- p_base_salary IN NUMBER
- p_change_reason IN VARCHAR2 DEFAULT NULL
- p_change_pct IN NUMBER DEFAULT NULL
- p_currency_code IN VARCHAR2 DEFAULT 'USD'
- p_pay_frequency IN VARCHAR2 DEFAULT 'MONTHLY'
- p_user IN VARCHAR2 DEFAULT USER

Logic:
1. IF p_base_salary <= 0: RAISE_APPLICATION_ERROR(-20101, 'Salary must be positive: ' || p_base_salary)
2. UPDATE SALARY_RECORDS SET END_DATE = p_effective_date - 1, ACTIVE_FLAG = 'N', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y' AND EFFECTIVE_DATE < p_effective_date
3. INSERT INTO SALARY_RECORDS (SALARY_ID, EMP_ID, EFFECTIVE_DATE, BASE_SALARY, CURRENCY_CODE, PAY_FREQUENCY, SALARY_BASIS, CHANGE_REASON, CHANGE_PCT, ACTIVE_FLAG, CREATED_BY, CREATED_DATE) VALUES (SEQ_SALARY.NEXTVAL, p_emp_id, p_effective_date, p_base_salary, p_currency_code, p_pay_frequency, 'ANNUAL', p_change_reason, p_change_pct, 'Y', p_user, SYSDATE)
4. PKG_AUDIT.log_action('SALARY_RECORDS', SEQ_SALARY.CURRVAL, 'INSERT', p_user)

Business rules:
- Salary must be positive (> 0).
- Previous active salary end-dated to p_effective_date - 1.
- SALARY_BASIS always stored as 'ANNUAL'.
- Default currency: 'USD'. Default frequency: 'MONTHLY'.

Exceptions: -20101 — salary must be positive

Sequences: SEQ_SALARY
Database tables written: SALARY_RECORDS
External services: PKG_AUDIT.log_action

---

**FUNCTION get_current_salary(p_emp_id NUMBER) RETURN NUMBER**

Logic:
1. SELECT BASE_SALARY FROM SALARY_RECORDS WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y' AND EFFECTIVE_DATE <= SYSDATE AND (END_DATE IS NULL OR END_DATE > SYSDATE) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. EXCEPTION WHEN NO_DATA_FOUND: RETURN 0

Database tables read: SALARY_RECORDS

---

**FUNCTION get_salary_as_of(p_emp_id NUMBER, p_as_of DATE) RETURN NUMBER**

Logic:
1. SELECT BASE_SALARY FROM SALARY_RECORDS WHERE EMP_ID = p_emp_id AND EFFECTIVE_DATE <= p_as_of AND (END_DATE IS NULL OR END_DATE >= p_as_of) ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY
2. EXCEPTION WHEN NO_DATA_FOUND: RETURN 0

Database tables read: SALARY_RECORDS

---

**PROCEDURE create_pay_periods(p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER)**

Logic — MONTHLY branch:
- Loop i IN 1..12:
  - v_start_date := TO_DATE(p_year || '-' || LPAD(i, 2, '0') || '-01', 'YYYY-MM-DD')
  - v_end_date := LAST_DAY(v_start_date)
  - v_pay_date := v_end_date
  - If pay date = SAT: v_pay_date := v_pay_date - 1 (move to Friday)
  - If pay date = SUN: v_pay_date := v_pay_date - 2 (move to Friday)
  - v_period_num := v_period_num + 1
  - INSERT INTO PAY_PERIODS (PERIOD_ID, PERIOD_NAME, PAY_FREQUENCY, PERIOD_START_DATE, PERIOD_END_DATE, PAY_DATE, STATUS, CREATED_BY, CREATED_DATE)
    - PERIOD_NAME = '<year>-<MM> (<Mon>)'
    - STATUS = 'OPEN'

Logic — BIWEEKLY branch:
- Start from Jan 1 of year; advance to first Friday of year
- Back up 13 days to start of that pay period (v_start_date := first_friday - 13)
- Loop while EXTRACT(YEAR FROM v_start_date) <= p_year:
  - v_end_date := v_start_date + 13 (14-day period: days 0-13)
  - v_pay_date := v_end_date + 5 (pay 5 days after period end)
  - v_period_num := v_period_num + 1
  - Insert if start or end is in target year:
    - PERIOD_NAME = '<year>-BW-<NN>'
    - STATUS = 'OPEN'
  - v_start_date := v_end_date + 1
- COMMIT at end

Business rules:
- Monthly periods: pay date = last day of month, adjusted to Friday if weekend.
- Biweekly periods: 14-day periods, pay date = period end + 5 days.
- All new periods start with STATUS = 'OPEN'.

Sequences: SEQ_PAY_PERIOD
Database tables written: PAY_PERIODS

---

**PROCEDURE close_pay_period(p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT STATUS FROM PAY_PERIODS WHERE PERIOD_ID = p_period_id FOR UPDATE
2. IF STATUS = 'CLOSED': RAISE_APPLICATION_ERROR(-20102, 'Period already closed: ' || p_period_id)
3. UPDATE PAY_PERIODS SET STATUS='CLOSED', CLOSED_BY=p_user, CLOSED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE PERIOD_ID=p_period_id

Exceptions: -20102 — period already closed

Database tables written: PAY_PERIODS

---

**FUNCTION get_current_period RETURN NUMBER**

Logic:
1. SELECT PERIOD_ID FROM PAY_PERIODS WHERE SYSDATE BETWEEN PERIOD_START_DATE AND PERIOD_END_DATE AND STATUS = 'OPEN' AND ROWNUM = 1
2. EXCEPTION WHEN NO_DATA_FOUND: RETURN NULL

Database tables read: PAY_PERIODS

---

**FUNCTION create_payroll_run(p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER) RETURN NUMBER**

Logic:
1. SELECT STATUS FROM PAY_PERIODS WHERE PERIOD_ID = p_period_id
2. IF STATUS = 'CLOSED': RAISE_APPLICATION_ERROR(-20102, 'Cannot create run for closed period: ' || p_period_id)
3. SELECT SEQ_PAYROLL_RUN.NEXTVAL INTO v_run_id FROM DUAL
4. INSERT INTO PAYROLL_RUNS (RUN_ID, PERIOD_ID, RUN_TYPE, RUN_DATE, STATUS, SUBMITTED_BY, SUBMITTED_DATE, CREATED_BY, CREATED_DATE) VALUES (v_run_id, p_period_id, p_run_type, SYSDATE, 'PENDING', p_user, SYSDATE, p_user, SYSDATE)
5. RETURN v_run_id

Exceptions: -20102 — cannot create run for closed period

Sequences: SEQ_PAYROLL_RUN
Database tables read: PAY_PERIODS
Database tables written: PAYROLL_RUNS

---

**PROCEDURE calculate_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT PERIOD_ID, RUN_TYPE FROM PAYROLL_RUNS WHERE RUN_ID = p_run_id
2. UPDATE PAYROLL_RUNS SET STATUS='CALCULATING' WHERE RUN_ID=p_run_id; COMMIT
3. Cursor loop (documented bug: should use BULK COLLECT + FORALL):
   SELECT e.EMP_ID FROM EMPLOYEES e WHERE e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.ACTIVE_FLAG = 'Y' ORDER BY e.EMP_ID
4. For each employee: call calculate_employee_pay(p_run_id, emp_rec.EMP_ID, v_period_id, p_user)
   - EXCEPTION WHEN OTHERS: INSERT error record into PAYROLL_DETAILS (ELEMENT_ID=0, ELEMENT_TYPE='ERROR', AMOUNT=0, STATUS='ERROR', ERROR_MESSAGE=SUBSTR(SQLERRM,1,4000)); v_error_count++
5. COMMIT every 50 employees (MOD(v_emp_count, 50) = 0)
   - Documented issue: partial commits mean failure leaves payroll half-calculated
6. UPDATE PAYROLL_RUNS SET:
   - STATUS = CASE WHEN v_error_count > 0 THEN 'ERROR' ELSE 'CALCULATED' END
   - EMPLOYEE_COUNT = v_emp_count
   - ERROR_COUNT = v_error_count
   - TOTAL_GROSS = SUM of PAYROLL_DETAILS WHERE ELEMENT_TYPE='EARNING' AND STATUS!='ERROR'
   - TOTAL_DEDUCTIONS = SUM of ABS(AMOUNT) WHERE ELEMENT_TYPE IN ('DEDUCTION','TAX') AND STATUS!='ERROR'
   - TOTAL_NET = SUM of CASE WHEN EARNING THEN AMOUNT WHEN DEDUCTION/TAX THEN -ABS(AMOUNT) ELSE 0 END WHERE STATUS!='ERROR'
7. COMMIT

Business rules:
- All ACTIVE + ACTIVE_FLAG='Y' employees are processed.
- Individual employee errors are recorded but do not stop the run.
- Run status = 'ERROR' if any employee failed; 'CALCULATED' if all succeeded.

Database tables read: PAYROLL_RUNS, EMPLOYEES
Database tables written: PAYROLL_RUNS, PAYROLL_DETAILS
External services: calculate_employee_pay (internal)

---

**PROCEDURE calculate_employee_pay(p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT PERIOD_START_DATE, PERIOD_END_DATE, PAY_FREQUENCY FROM PAY_PERIODS WHERE PERIOD_ID = p_period_id
2. Determine v_periods_per_year:
   | PAY_FREQUENCY | v_periods_per_year |
   |---|---|
   | 'WEEKLY' | 52 |
   | 'BIWEEKLY' | 26 |
   | 'SEMIMONTHLY' | 24 |
   | 'MONTHLY' | 12 |
   | default | 12 |
3. v_annual_salary := get_salary_as_of(p_emp_id, v_period_end)
4. IF v_annual_salary = 0: RAISE_APPLICATION_ERROR(-20104, 'No active salary record for employee ' || p_emp_id)
5. v_period_gross := ROUND(v_annual_salary / v_periods_per_year, 2)
6. INSERT PAYROLL_DETAILS: ELEMENT_ID=1, ELEMENT_TYPE='EARNING', AMOUNT=v_period_gross, STATUS='CALCULATED'
7. v_ytd_gross := get_ytd_earnings(p_emp_id, EXTRACT(YEAR FROM v_period_end))
8. Get tax info from EMPLOYEE_TAX_INFO WHERE EMP_ID=p_emp_id AND TAX_YEAR=EXTRACT(YEAR FROM v_period_end) AND ACTIVE_FLAG='Y'
   - Fields: FILING_STATUS, FEDERAL_ALLOWANCES, STATE_CODE, STATE_ALLOWANCES, ADDITIONAL_FED_WH
   - EXCEPTION WHEN NO_DATA_FOUND: defaults: FILING_STATUS='SINGLE', FEDERAL_ALLOWANCES=0, STATE_CODE=NULL, STATE_ALLOWANCES=0, ADDITIONAL_FED_WH=0
9. v_taxable_income := v_period_gross (simplified — does not subtract pretax deductions)
10. v_federal_tax := calculate_federal_tax(v_taxable_income, v_filing_status, v_fed_allowances, v_addl_fed_wh, v_pay_frequency)
11. If v_federal_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=100, ELEMENT_TYPE='TAX', AMOUNT=-v_federal_tax
12. If v_state_code IS NOT NULL:
    - v_state_tax := calculate_state_tax(v_taxable_income, v_state_code, v_filing_status, v_state_allowances, v_pay_frequency)
    - If v_state_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=101, ELEMENT_TYPE='TAX', AMOUNT=-v_state_tax
13. v_ss_tax := calculate_fica(v_period_gross, v_ytd_gross)
    - If v_ss_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=102, ELEMENT_TYPE='TAX', AMOUNT=-v_ss_tax
14. v_medicare_tax := calculate_medicare(v_period_gross, v_ytd_gross)
    - If v_medicare_tax > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=103, ELEMENT_TYPE='TAX', AMOUNT=-v_medicare_tax
15. Deductions loop: SELECT FROM EMPLOYEE_PAY_ELEMENTS epe JOIN PAY_ELEMENTS pe WHERE epe.EMP_ID=p_emp_id AND epe.ACTIVE_FLAG='Y' AND pe.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') AND epe.EFFECTIVE_DATE <= v_period_end AND (epe.END_DATE IS NULL OR epe.END_DATE >= v_period_start) ORDER BY pe.PRIORITY_ORDER
    - For each: calculate v_ded_amount:
      - If OVERRIDE_AMOUNT IS NOT NULL: v_ded_amount := OVERRIDE_AMOUNT
      - Elif CALCULATION_TYPE = 'FLAT': v_ded_amount := NVL(AMOUNT, DEFAULT_AMOUNT)
      - Elif CALCULATION_TYPE = 'PERCENTAGE': v_ded_amount := ROUND(v_period_gross * NVL(PERCENTAGE, DEFAULT_PERCENTAGE) / 100, 2)
      - Else: v_ded_amount := NVL(AMOUNT, 0)
    - If v_ded_amount > 0: INSERT PAYROLL_DETAILS: ELEMENT_ID=ded_rec.ELEMENT_ID, ELEMENT_TYPE=ded_rec.ELEMENT_TYPE, AMOUNT=-v_ded_amount
16. EXCEPTION WHEN OTHERS: PKG_COMMON.log_error; RAISE

**PAYROLL_DETAILS ELEMENT_ID assignments (hard-coded):**
| ELEMENT_ID | Type | Description |
|---|---|---|
| 1 | EARNING | Base gross pay |
| 0 | ERROR | Error placeholder |
| 100 | TAX | Federal income tax |
| 101 | TAX | State income tax |
| 102 | TAX | Social Security (FICA) |
| 103 | TAX | Medicare |

Business rules:
- No active salary = error, stops employee processing.
- W-4 defaults if no EMPLOYEE_TAX_INFO on file: SINGLE, 0 allowances, no additional withholding.
- Taxable income simplified to gross (pretax deductions NOT subtracted — documented simplification).
- Deductions applied in PRIORITY_ORDER.
- Override amount takes precedence over all other calculation methods.
- Deduction amounts stored as negative values in PAYROLL_DETAILS.

Exceptions: -20104 — no active salary record

Database tables read: PAY_PERIODS, SALARY_RECORDS (via get_salary_as_of), EMPLOYEE_TAX_INFO, EMPLOYEE_PAY_ELEMENTS, PAY_ELEMENTS
Database tables written: PAYROLL_DETAILS
External services: PKG_COMMON.log_error

---

**PROCEDURE approve_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT STATUS FROM PAYROLL_RUNS WHERE RUN_ID = p_run_id FOR UPDATE
2. IF STATUS NOT IN ('CALCULATED'): RAISE_APPLICATION_ERROR(-20103, 'Cannot approve run in status: ' || v_status)
3. UPDATE PAYROLL_RUNS SET STATUS='APPROVED', APPROVED_BY=p_user, APPROVED_DATE=SYSDATE, MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE

Business rule: Only CALCULATED runs can be approved.

Exceptions: -20103 — run not in CALCULATED status

Database tables written: PAYROLL_RUNS

---

**PROCEDURE reverse_payroll(p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. UPDATE PAYROLL_RUNS SET STATUS='REVERSED', MODIFIED_BY=p_user, MODIFIED_DATE=SYSDATE WHERE RUN_ID=p_run_id
2. UPDATE PAYROLL_DETAILS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id
3. PKG_AUDIT.log_action('PAYROLL_RUNS', p_run_id, 'UPDATE', p_user)

Database tables written: PAYROLL_RUNS, PAYROLL_DETAILS
External services: PKG_AUDIT.log_action

---

**FUNCTION calculate_federal_tax(p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER**

Logic:
1. Determine v_periods:
   | p_pay_frequency | v_periods |
   |---|---|
   | 'WEEKLY' | 52 |
   | 'BIWEEKLY' | 26 |
   | 'SEMIMONTHLY' | 24 |
   | 'MONTHLY' | 12 |
   | default | 12 |
2. v_annualized := p_taxable_income * v_periods
3. v_std_deduction := 29200 if p_filing_status = 'MARRIED_JOINT'; else 14600
4. v_taxable := v_annualized - v_std_deduction - (p_allowances * 4300)
5. IF v_taxable <= 0: RETURN 0
6. Apply 2024 tax brackets:

   **SINGLE or MARRIED_SEPARATE:**
   | Bracket | Annual Taxable Income Range | Tax Calculation |
   |---|---|---|
   | 1 | 0 – 11,600 | v_taxable * 0.10 |
   | 2 | 11,600.01 – 47,150 | 1,160 + (v_taxable - 11,600) * 0.12 |
   | 3 | 47,150.01 – 100,525 | 5,426 + (v_taxable - 47,150) * 0.22 |
   | 4 | 100,525.01 – 191,950 | 17,168.50 + (v_taxable - 100,525) * 0.24 |
   | 5 | 191,950.01 – 243,725 | 39,110.50 + (v_taxable - 191,950) * 0.32 |
   | 6 | 243,725.01 – 609,350 | 55,678.50 + (v_taxable - 243,725) * 0.35 |
   | 7 | > 609,350 | 183,647.25 + (v_taxable - 609,350) * 0.37 |

   **MARRIED_JOINT:**
   | Bracket | Annual Taxable Income Range | Tax Calculation |
   |---|---|---|
   | 1 | 0 – 23,200 | v_taxable * 0.10 |
   | 2 | 23,200.01 – 94,300 | 2,320 + (v_taxable - 23,200) * 0.12 |
   | 3 | 94,300.01 – 201,050 | 10,852 + (v_taxable - 94,300) * 0.22 |
   | 4 | 201,050.01 – 383,900 | 34,337 + (v_taxable - 201,050) * 0.24 |
   | 5 | 383,900.01 – 487,450 | 78,221 + (v_taxable - 383,900) * 0.32 |
   | 6 | 487,450.01 – 731,200 | 111,357 + (v_taxable - 487,450) * 0.35 |
   | 7 | > 731,200 | 196,669.50 + (v_taxable - 731,200) * 0.37 |

7. v_tax := ROUND(v_tax / v_periods, 2) — convert annual tax back to per-period
8. v_tax := v_tax + NVL(p_additional_wh, 0) — add additional withholding
9. RETURN v_tax

Business rules:
- Income annualized before bracket lookup.
- Standard deduction subtracted: 14,600 (single/separate), 29,200 (married joint).
- Each W-4 allowance reduces taxable income by 4,300.
- Brackets are hard-coded 2024 values.
- Head-of-household and other filing statuses not modeled (fall into single/default path or no branch matches → v_tax remains 0).

---

**FUNCTION calculate_state_tax(p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER**

Logic: Flat rate lookup by state code (simplified; documented as not bracket-based):

| State Code | Rate |
|---|---|
| 'CA' | 0.0725 (7.25%) |
| 'NY' | 0.0685 (6.85%) |
| 'TX' | 0 (no state income tax) |
| 'FL' | 0 (no state income tax) |
| 'WA' | 0 (no state income tax) |
| 'IL' | 0.0495 (4.95%) |
| 'PA' | 0.0307 (3.07%) |
| 'OH' | 0.04 (4.00%) |
| 'NJ' | 0.0637 (6.37%) |
| 'MA' | 0.05 (5.00%) |
| default (any other state) | 0.05 (5.00%) |

Returns: ROUND(p_taxable_income * v_rate, 2)

Business rule: p_filing_status and p_allowances are accepted parameters but NOT used in the calculation (flat rate only).

---

**FUNCTION calculate_fica(p_gross_pay NUMBER, p_ytd_gross NUMBER) RETURN NUMBER**

Logic:
1. IF p_ytd_gross >= 168600: RETURN 0 (already exceeded 2024 SS wage base)
2. v_taxable := LEAST(p_gross_pay, 168600 - p_ytd_gross) — cap at remaining wage base
3. RETURN ROUND(v_taxable * 0.062, 2)

Business rules:
- 2024 Social Security wage base: 168,600
- Employee SS rate: 6.2%
- No SS tax once YTD exceeds 168,600.
- Partial period calculation when crossing the wage base.

---

**FUNCTION calculate_medicare(p_gross_pay NUMBER, p_ytd_gross NUMBER) RETURN NUMBER**

Logic:
1. v_base_tax := ROUND(p_gross_pay * 0.0145, 2)
2. Additional Medicare (0.9%) on high earners:
   - IF p_ytd_gross + p_gross_pay > 200,000 THEN:
     - IF p_ytd_gross >= 200,000: v_addl_tax := ROUND(p_gross_pay * 0.009, 2) — full period above threshold
     - ELSE: v_addl_tax := ROUND((p_ytd_gross + p_gross_pay - 200,000) * 0.009, 2) — partial period crossing threshold
   - ELSE: v_addl_tax := 0
3. RETURN v_base_tax + v_addl_tax

Business rules:
- Base Medicare rate: 1.45% on all wages (no wage base cap).
- Additional Medicare rate: 0.9% on wages exceeding 200,000 YTD.
- Partial period calculation when crossing the 200,000 threshold.

---

**PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL)**

Logic: Opens ref cursor with aggregation query:
```sql
SELECT pd.EMP_ID, e.EMP_NUMBER,
       e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME,
       pp.PERIOD_NAME,
       SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY,
       SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','TAX','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS,
       SUM(pd.AMOUNT) AS NET_PAY,
       SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FEDERAL_TAX,
       SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE_TAX,
       SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SOCIAL_SECURITY,
       SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MEDICARE,
       0 AS YTD_GROSS,  -- Placeholder (not calculated)
       0 AS YTD_NET     -- Placeholder (not calculated)
FROM PAYROLL_DETAILS pd
JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID
WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR'
AND (p_emp_id IS NULL OR pd.EMP_ID = p_emp_id)
GROUP BY pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME
ORDER BY e.LAST_NAME
```

Note: YTD_GROSS and YTD_NET are hard-coded 0 (placeholders, not implemented).

Database tables read: PAYROLL_DETAILS, EMPLOYEES, PAYROLL_RUNS, PAY_PERIODS

---

**FUNCTION get_ytd_earnings(p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER**

Logic:
1. SELECT NVL(SUM(pd.AMOUNT), 0) FROM PAYROLL_DETAILS pd JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pd.EMP_ID = p_emp_id AND pd.ELEMENT_TYPE = 'EARNING' AND pd.STATUS = 'CALCULATED' AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year
2. RETURN v_ytd

Database tables read: PAYROLL_DETAILS, PAYROLL_RUNS, PAY_PERIODS

---

**PROCEDURE generate_pay_register(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)**

Logic:
1. SELECT pp.PERIOD_NAME FROM PAYROLL_RUNS pr JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID WHERE pr.RUN_ID = p_run_id
2. v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS') || '.csv'
3. Open UTL_FILE in directory 'PAYROLL_OUTPUT', mode 'W', buffer 32767
4. Write CSV header: 'EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,GROSS_PAY,FED_TAX,STATE_TAX,SS_TAX,MEDICARE,DEDUCTIONS,NET_PAY'
5. Detail query (aggregated per employee):
   ```sql
   SELECT e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME,
          d.DEPT_NAME,
          SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS,
          SUM(CASE WHEN pd.ELEMENT_ID = 100 THEN ABS(pd.AMOUNT) ELSE 0 END) AS FED,
          SUM(CASE WHEN pd.ELEMENT_ID = 101 THEN ABS(pd.AMOUNT) ELSE 0 END) AS STATE,
          SUM(CASE WHEN pd.ELEMENT_ID = 102 THEN ABS(pd.AMOUNT) ELSE 0 END) AS SS,
          SUM(CASE WHEN pd.ELEMENT_ID = 103 THEN ABS(pd.AMOUNT) ELSE 0 END) AS MED,
          SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS DEDS,
          SUM(pd.AMOUNT) AS NET
   FROM PAYROLL_DETAILS pd
   JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
   JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
   WHERE pd.RUN_ID = p_run_id AND pd.STATUS != 'ERROR'
   GROUP BY e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, d.DEPT_NAME
   ORDER BY e.LAST_NAME
   ```
6. Each line: EMP_NUMBER,"EMPLOYEE_NAME","DEPT_NAME",GROSS,FED,STATE,SS,MED,DEDS,NET — amounts with TO_CHAR format 'FM999999990.00'
7. Close file; DBMS_OUTPUT.PUT_LINE('Pay register generated: ' || v_filename)
8. EXCEPTION WHEN OTHERS: close file if open; PKG_COMMON.log_error; RAISE

Note: TAX-type amounts (ELEMENT_ID 100-103) are excluded from the DEDS column in the register; DEDS only covers DEDUCTION and BENEFIT types.

Oracle directory object used: 'PAYROLL_OUTPUT'

Database tables read: PAYROLL_RUNS, PAY_PERIODS, PAYROLL_DETAILS, EMPLOYEES, DEPARTMENTS
External file I/O: UTL_FILE write to Oracle directory 'PAYROLL_OUTPUT'
External services: PKG_COMMON.log_error, DBMS_OUTPUT.PUT_LINE

---

**Summary of all database tables referenced across all files:**

| Table | Operations |
|---|---|
| EMPLOYEES | SELECT, INSERT, UPDATE |
| EMPLOYEE_HISTORY | INSERT |
| EMPLOYEE_DEPENDENTS | SELECT |
| EMPLOYEE_TAX_INFO | SELECT |
| EMPLOYEE_PAY_ELEMENTS | SELECT, UPDATE |
| DEPARTMENTS | SELECT |
| JOB_TITLES | SELECT |
| JOB_GRADES | SELECT |
| SALARY_RECORDS | SELECT, INSERT, UPDATE |
| LEAVE_REQUESTS | SELECT, INSERT, UPDATE |
| LEAVE_BALANCES | SELECT, INSERT, UPDATE |
| LEAVE_TYPES | SELECT |
| LEAVE_ACCRUAL_LOG | INSERT |
| HOLIDAYS | SELECT |
| PAYROLL_RUNS | SELECT, INSERT, UPDATE |
| PAYROLL_DETAILS | SELECT, INSERT, UPDATE |
| PAY_PERIODS | SELECT, INSERT, UPDATE |
| PAY_ELEMENTS | SELECT |
| NOTIFICATION_QUEUE | SELECT, INSERT, UPDATE |

**Summary of all sequences referenced:**

| Sequence | Used In |
|---|---|
| SEQ_EMPLOYEE | generate_emp_number, get_next_emp_id |
| SEQ_EMP_HISTORY | log_history |
| SEQ_LEAVE_REQUEST | submit_leave_request |
| SEQ_LEAVE_BALANCE | initialize_balances |
| SEQ_LEAVE_ACCRUAL | run_monthly_accrual |
| SEQ_SALARY | create_salary_record |
| SEQ_PAY_PERIOD | create_pay_periods |
| SEQ_PAYROLL_RUN | create_payroll_run |
| SEQ_PAYROLL_DETAIL | calculate_employee_pay, calculate_payroll |
| SEQ_NOTIFICATION | send_notification |

**Summary of all external packages/services called:**

| Package | Methods Called From |
|---|---|
| PKG_PAYROLL.create_salary_record | PKG_EMPLOYEE (create_employee, promote_employee, rehire_employee) |
| PKG_AUDIT.log_action | PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL (many procedures) |
| PKG_NOTIFICATION.send_notification | PKG_EMPLOYEE (create_employee, terminate_employee), PKG_LEAVE (submit, approve, reject) |
| PKG_COMMON.log_error | PKG_EMPLOYEE, PKG_INTEGRATION, PKG_LEAVE (none direct), PKG_PAYROLL, PKG_NOTIFICATION |
| PKG_COMMON.log_info | PKG_INTEGRATION, PKG_NOTIFICATION |
| PKG_COMMON.get_param | PKG_INTEGRATION.get_integration_status |
| UTL_FILE | PKG_INTEGRATION (generate_gl_journal, export_benefits_feed, import_time_attendance), PKG_PAYROLL (generate_pay_register) |
| UTL_SMTP | PKG_NOTIFICATION.process_queue |
| UTL_TCP | PKG_NOTIFICATION.process_queue (CRLF constant) |
| DBMS_OUTPUT | PKG_LEAVE.run_monthly_accrual, PKG_PAYROLL.generate_pay_register, PKG_EMPLOYEE.log_history (debug) |
