600 - p_ytd_gross); rate: 6.2% (0.062); ROUND to 2 dp | Applied: all payroll runs | HIGH | PKG_PAYROLL.pkb — calculate_fica |
| AP-17 | Additional Medicare Tax Threshold | Data Access | PKG_PAYROLL.calculate_medicare | Base rate: 1.45% on all wages (no cap); additional 0.9% on wages above 200,000 YTD; partial-period crossing: `ROUND((p_ytd_gross + p_gross_pay - 200,000) * 0.009, 2)` — only amount above threshold taxed; single 200,000 threshold for all filing statuses (IRS uses 250,000 for MFJ — code does not differentiate) | Applied: all payroll runs | HIGH | PKG_PAYROLL.pkb — calculate_medicare |
| AP-18 | Circular Package Dependency | Dependency Coupling | PKG_EMPLOYEE ↔ PKG_PAYROLL | PKG_EMPLOYEE.create_employee calls PKG_PAYROLL.create_salary_record (step 10 of create_employee); PKG_EMPLOYEE.promote_employee calls PKG_PAYROLL.create_salary_record; PKG_PAYROLL.calculate_employee_pay calls PKG_EMPLOYEE (implied via is_active check); PKG_PAYROLL.create_salary_record does NOT call PKG_EMPLOYEE.is_active — Agent 1's OUTPUT 5 description is imprecise; actual circular path: PKG_EMPLOYEE creates salary via PKG_PAYROLL; PKG_PAYROLL's calculate_payroll loop queries EMPLOYEES directly rather than via PKG_EMPLOYEE | Tight coupling — bidirectional runtime dependency at package level | HIGH — create_salary_record call confirmed in PKG_EMPLOYEE.create_employee; EMPLOYEES direct SELECT confirmed in calculate_payroll | PKG_EMPLOYEE.pkb — create_employee, promote_employee; PKG_PAYROLL.pkb — calculate_payroll |
| AP-19 | Batch Commit Interval | Data Access | PKG_PAYROLL.calculate_payroll; PKG_LEAVE.run_monthly_accrual | calculate_payroll: COMMIT every 50 employees (MOD(v_emp_count, 50) = 0); run_monthly_accrual: COMMIT every 100 employees (MOD(v_total_employees, 100) = 0); intermediate commits mean a failure leaves data in a partially-committed state with no rollback mechanism | Partial — intervals differ between two batch jobs; no compensating logic on failure | HIGH — MOD(v_emp_count, 50) confirmed in calculate_payroll; MOD(v_total_employees, 100) confirmed in run_monthly_accrual | PKG_PAYROLL.pkb — calculate_payroll; PKG_LEAVE.pkb — run_monthly_accrual |
| AP-20 | Deduction Priority Ordering | Data Access | PKG_PAYROLL.calculate_employee_pay | Deductions processed in ascending PAY_ELEMENTS.PRIORITY_ORDER; deduction amount resolved by hierarchy: OVERRIDE_AMOUNT IS NOT NULL → use override; CALCULATION_TYPE='FLAT' → NVL(AMOUNT, DEFAULT_AMOUNT); CALCULATION_TYPE='PERCENTAGE' → ROUND(v_period_gross × NVL(PERCENTAGE, DEFAULT_PERCENTAGE) / 100, 2); other → NVL(AMOUNT, 0); percentage calculated against gross BEFORE pretax deductions (simplified — pretax not actually subtracted from taxable base) | Applied: all payroll runs | HIGH | PKG_PAYROLL.pkb — calculate_employee_pay |
| AP-21 | Leave Balance Accrual Cap | Data Access | PKG_LEAVE.run_monthly_accrual | Cap logic: IF MAX_BALANCE IS NULL OR v_current_balance + ACCRUAL_RATE <= MAX_BALANCE THEN v_accrued := ACCRUAL_RATE ELSE v_accrued := GREATEST(0, MAX_BALANCE - v_current_balance); GREATEST(0,...) prevents negative accrual; tenure gate enforced per leave type before any accrual: TRUNC(p_accrual_date) - emp_rec.HIRE_DATE >= lt_rec.MIN_TENURE_DAYS | Applied: run_monthly_accrual; carryover handled separately in process_carryover | HIGH | PKG_LEAVE.pkb — run_monthly_accrual |
| AP-22 | Carryover with Expiry | Data Access | PKG_LEAVE.process_carryover / expire_carryover | Carryover amount: LEAST(remaining_balance, CARRYOVER_MAX) if CARRYOVER_MAX IS NOT NULL; carryover expiry date: ADD_MONTHS(next_year-Jan-01, CARRYOVER_EXPIRY) where CARRYOVER_EXPIRY is stored as months; expire_carryover: UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT - CARRYOVER_FROM_PREV, CARRYOVER_FROM_PREV = 0 WHERE CARRYOVER_EXPIRY_DT <= TRUNC(SYSDATE) AND CARRYOVER_FROM_PREV > 0 | Applied: year-end process; expiry sweep designed for periodic execution | HIGH | PKG_LEAVE.pkb — process_carryover, expire_carryover |
| AP-23 | Rating Scale Boundary Matching | Data Access | PKG_PERFORMANCE.submit_manager_review | Rating range: 1.0–5.0 (CHK constraint on PERFORMANCE_REVIEWS; enforced in submit_manager_review at -20403); label assignment: >= 4.5 Exceptional; >= 3.5 Exceeds Expectations; >= 2.5 Meets Expectations; >= 1.5 Needs Improvement; < 1.5 Unsatisfactory; all boundaries inclusive-from | Applied: all manager review submissions | HIGH | PKG_PERFORMANCE.pkb — submit_manager_review |
| AP-24 | Dynamic SQL with String Concatenation (Anti-pattern) | Security | PKG_EMPLOYEE.search_employees | v_sql built by string concatenation for p_last_name, p_first_name, p_status, p_location_code parameters; p_dept_id and date parameters concatenated directly; OPEN p_cursor FOR v_sql — no bind variables for text search fields; p_dept_id uses numeric concatenation (no quotes) which is lower injection risk but still non-parameterised | Full coverage of search_employees function — no bind variables used on any text filter | HIGH — confirmed: `v_sql || ' AND UPPER(e.LAST_NAME) LIKE UPPER(''' || p_last_name || '%'')'` | PKG_EMPLOYEE.pkb — search_employees |

---

**DISC-001 Resolution — Hire Date Future Limit:**

Direct code evidence:
- HRMS_EMPLOYEE.xml WHEN-VALIDATE-ITEM: `HIRE_DATE > SYSDATE + 90` → client-side Oracle Forms validation, fires before INSERT
- TRG_EMP_BEFORE_INSERT (trg_employees.sql): `IF :NEW.HIRE_DATE > SYSDATE + 180` → server-side database trigger, fires on every INSERT regardless of calling path

**Resolution:** Both rules are authoritative for their respective layers. The database trigger (180 days) is the enforced hard limit — it fires on every INSERT and cannot be bypassed by any caller including direct SQL*Plus DML, integrations, and the self-service portal. The Forms trigger (90 days) is a client-side soft gate that fires only when using the Oracle Forms UI; it is stricter and provides earlier feedback. **The actual system limit is 180 days at the database layer and 90 days via the Forms UI only.** DISC-001 is partially resolved — both rules are real and correct for their layers. No single "authoritative" number exists; the limits differ by access path. This represents an architecture gap: direct PL/SQL callers (e.g. PKG_EMPLOYEE.create_employee) bypass the 90-day Forms check and are only subject to the 180-day DB trigger.

---

**DISC-003 Resolution — VW_LEAVE_SUMMARY vs LEAVE_BALANCES Virtual Column:**

Direct code evidence:
- LEAVE_BALANCES virtual column AVAILABLE: `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING`
- VW_LEAVE_SUMMARY AVAILABLE: `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT` (no PENDING deduction)
- PKG_LEAVE.get_leave_balance: `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING` — matches virtual column
- PKG_LEAVE.submit_leave_request balance check: calls get_leave_balance — uses the formula **with PENDING**

**Resolution:** The virtual column and PKG_LEAVE.get_leave_balance are consistent and represent the correct "spendable balance" (PENDING reduces available capacity). VW_LEAVE_SUMMARY is incorrect — it overstates available balance by not subtracting pending leave. **The virtual column formula (including PENDING) is authoritative.** VW_LEAVE_SUMMARY has a defect: it will display a higher balance than is actually available, allowing users to see misleadingly high balance figures in any report using that view.

---

### Stage 4 — NFR Registry Additions (Chunk 2: Application Layer)

| ID | NFR Name | Value | Category | Source | Confidence |
|---|---|---|---|---|---|
| NFR-18 | 2024 Federal tax brackets — Single/MFS: 7 brackets | 10% (0–11,600); 12% (11,601–47,150); 22% (47,151–100,525); 24% (100,526–191,950); 32% (191,951–243,725); 35% (243,726–609,350); 37% (609,351+) | Throughput | PKG_PAYROLL.calculate_federal_tax — hard-coded bracket table | HIGH |
| NFR-19 | 2024 Federal tax brackets — MARRIED_JOINT: 7 brackets | 10% (0–23,200); 12% (23,201–94,300); 22% (94,301–201,050); 24% (201,051–383,900); 32% (383,901–487,450); 35% (487,451–731,200); 37% (731,201+) | Throughput | PKG_PAYROLL.calculate_federal_tax | HIGH |
| NFR-20 | Federal standard deduction — Single/MFS | 14,600 (2024) | Throughput | PKG_PAYROLL.c_standard_deduction_single | HIGH |
| NFR-21 | Federal standard deduction — Married Filing Jointly | 29,200 (2024) | Throughput | PKG_PAYROLL.c_standard_deduction_married | HIGH |
| NFR-22 | Per-allowance income reduction | 4,300 per allowance (2024) | Throughput | PKG_PAYROLL.c_allowance_amount | HIGH |
| NFR-23 | Social Security wage base (2024) | 168,600 | Throughput | PKG_PAYROLL.c_ss_wage_base_2024 | HIGH |
| NFR-24 | Social Security employee rate | 6.2% (0.062) | Throughput | PKG_PAYROLL.c_ss_rate | HIGH |
| NFR-25 | Medicare base rate | 1.45% (0.0145) — no wage base cap | Throughput | PKG_PAYROLL.c_medicare_rate | HIGH |
| NFR-26 | Additional Medicare rate | 0.9% (0.009) on wages above 200,000 YTD | Throughput | PKG_PAYROLL.c_medicare_addl_rate, c_medicare_addl_threshold | HIGH |
| NFR-27 | Payroll batch commit interval | Every 50 employees (MOD(v_emp_count, 50) = 0) | Throughput | PKG_PAYROLL.calculate_payroll | HIGH |
| NFR-28 | Leave accrual batch commit interval | Every 100 employees (MOD(v_total_employees, 100) = 0) | Throughput | PKG_LEAVE.run_monthly_accrual | HIGH |
| NFR-29 | Leave backdating maximum | 5 days in the past; requests older than 5 days rejected (-20211) | Rate | PKG_LEAVE.submit_leave_request | HIGH |
| NFR-30 | Half-day leave value | Exactly 0.5 days (independent of business day calculation) | Throughput | PKG_LEAVE.submit_leave_request | HIGH |
| NFR-31 | Circular reporting chain check depth | 15 levels maximum (c_max_hierarchy_depth = 15) | Resource Management | PKG_EMPLOYEE.validate_manager | HIGH |
| NFR-32 | Org chart default maximum depth | 10 levels (p_max_depth DEFAULT 10) | Resource Management | PKG_EMPLOYEE.get_org_chart | HIGH |
| NFR-33 | State income tax rates (flat, 2024) | CA: 7.25%; NY: 6.85%; IL: 4.95%; PA: 3.07%; OH: 4.00%; NJ: 6.37%; MA: 5.00%; TX/FL/WA: 0%; ALL OTHERS: 5.00% default | Throughput | PKG_PAYROLL.calculate_state_tax | HIGH |
| NFR-34 | Pay period count — MONTHLY | 12 periods per year; pay date = last day of month; adjusted to preceding Friday if Saturday or Sunday | Throughput | PKG_PAYROLL.create_pay_periods | HIGH |
| NFR-35 | Pay period count — BIWEEKLY | 14-day periods ending on Friday; pay date = period end + 5 days | Throughput | PKG_PAYROLL.create_pay_periods | HIGH |
| NFR-36 | Payroll error row error message truncation | 4,000 characters (SUBSTR(SQLERRM,1,4000)) | Resource Management | PKG_PAYROLL.calculate_payroll; PKG_NOTIFICATION.process_queue | HIGH |
| NFR-37 | Notification queue default priority | 5 (lower number = higher priority; ORDER BY PRIORITY ASC) | Rate | PKG_NOTIFICATION.send_notification — p_priority DEFAULT 5 | HIGH |
| NFR-38 | Notification retry maximum | 3 attempts before permanent FAILED status | Reliability | PKG_NOTIFICATION.retry_failed — p_max_retries DEFAULT 3 | HIGH |
| NFR-39 | Session timeout constant (code) | 30 minutes — c_session_timeout_min = 30 (duplicates NFR-01; this is the package-level constant, vs NFR-01 from SYSTEM_PARAMETERS; both must be updated to change the timeout) | Availability | PKG_SECURITY.pkb — c_session_timeout_min | HIGH |
| NFR-40 | Leave type minimum tenure — COMP (Compensatory) | 90 days since hire | Rate | LEAVE_TYPES seed data — MIN_TENURE_DAYS; PKG_LEAVE.submit_leave_request tenure check | HIGH |
| NFR-41 | Leave type minimum tenure — FMLA | 365 days since hire | Rate | LEAVE_TYPES seed data — MIN_TENURE_DAYS; PKG_LEAVE.submit_leave_request tenure check | HIGH |
| NFR-42 | PTO accrual rate | 1.25 days per month | Data Freshness | LEAVE_TYPES seed data — ACCRUAL_RATE per Agent 1 | HIGH |
| NFR-43 | SICK accrual rate | 0.833 days per month | Data Freshness | LEAVE_TYPES seed data — ACCRUAL_RATE per Agent 1 | HIGH |
| NFR-44 | 401k default contribution | 6% of gross (pretax, PERCENTAGE type) | Throughput | PAY_ELEMENTS seed data per Agent 1; PKG_PAYROLL calculate_employee_pay PERCENTAGE branch | HIGH |
| NFR-45 | Medical insurance deduction default | 250 USD per period (pretax, FLAT type) | Throughput | PAY_ELEMENTS seed data per Agent 1 | HIGH |
| NFR-46 | Salary grade range validation | Hard check in PKG_VALIDATION.validate_salary_for_grade (returns message string); soft warning only in PKG_EMPLOYEE.create_employee (debug mode only); no error raised in create_employee | Rate | PKG_EMPLOYEE.create_employee — IF g_debug_mode; PKG_VALIDATION.validate_salary_for_grade | HIGH |
| NFR-47 | Employee number format | EMP-NNNNNN — prefix 'EMP-' followed by 6 zero-padded digits; validated by REGEXP_LIKE(p_emp_number, '^EMP-\d{6}$') | Resource Management | PKG_EMPLOYEE.generate_emp_number; PKG_VALIDATION.validate_emp_number_format | HIGH |
| NFR-48 | Performance review rating range | 1.0 to 5.0 inclusive (NUMBER(2,1)); enforced in submit_manager_review (-20403) and by CHK_RATING_RANGE constraint | Rate | PKG_PERFORMANCE.submit_manager_review; PERFORMANCE_REVIEWS DDL | HIGH |

---

### Stage 5 — Technical Debt & Risk Register Additions (Chunk 2: Application Layer)

| ID | Risk / Debt Item | Category | Affected Component(s) | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|---|
| TD-15 | YTD_GROSS and YTD_NET hard-coded as 0 in all payslip output: get_payslip SELECT returns `0 AS YTD_GROSS, 0 AS YTD_NET`; payslips presented to employees via HRMS_PAYROLL form show incorrect year-to-date totals | Operational Risk | PKG_PAYROLL.get_payslip; HRMS_PAYROLL.fmb | **High** | PKG_PAYROLL.pkb: `0 AS YTD_GROSS, 0 AS YTD_NET` — source comment: "Placeholder (not implemented)"; get_ytd_earnings function exists and is correct but is not called from get_payslip | Wire get_ytd_earnings(pd.EMP_ID, EXTRACT(YEAR FROM pp.PERIOD_START_DATE)) into get_payslip SELECT |
| TD-16 | Race condition in generate_emp_number: uses MAX(TO_NUMBER(SUBSTR(EMP_NUMBER,5)))+1 instead of SEQ_EMP_NUMBER; two concurrent create_employee calls reading identical MAX() values will attempt to insert the same EMP_NUMBER; UK_EMP_NUMBER constraint will raise DUP_VAL_ON_INDEX (-20002) on the second caller; SEQ_EMP_NUMBER exists and is unused for this purpose | Architecture Anti-pattern | PKG_EMPLOYEE.generate_emp_number; PKG_EMPLOYEE.create_employee | **High** | PKG_EMPLOYEE.pkb: `SELECT NVL(MAX(TO_NUMBER(SUBSTR(EMP_NUMBER, 5))), 0) + 1 FROM EMPLOYEES WHERE EMP_NUMBER LIKE 'EMP-%'`; SEQ_EMP_NUMBER.NEXTVAL used only in exception fallback | Replace MAX()+1 with SEQ_EMP_NUMBER.NEXTVAL directly; remove exception fallback |
| TD-17 | Partial commits in calculate_payroll leave payroll in unrecoverable half-calculated state on failure: COMMIT every 50 employees; if processing fails on employee 73, employees 1–50 have committed PAYROLL_DETAILS rows while 51–73 may be partially committed; PAYROLL_RUNS.STATUS will be ERROR but data is partially persisted with no rollback mechanism | Architecture Anti-pattern | PKG_PAYROLL.calculate_payroll | **High** | PKG_PAYROLL.pkb: `IF MOD(v_emp_count, 50) = 0 THEN COMMIT`; no ROLLBACK or cleanup in outer EXCEPTION block | Replace row-by-row loop with BULK COLLECT + FORALL; if partial commits are required for memory management, record checkpoint and implement restart-from-checkpoint or pre-run cleanup |
| TD-18 | get_employee and promote_employee salary lookup uses ROWNUM=1 without ORDER BY: `SELECT BASE_SALARY FROM SALARY_RECORDS WHERE EMP_ID=p_emp_id AND ACTIVE_FLAG='Y' AND ROWNUM=1` — if multiple active salary records exist for same employee (which should not happen given end-dating logic but is not prevented by a DB constraint), result is non-deterministic | Architecture Anti-pattern | PKG_EMPLOYEE.get_employee; PKG_EMPLOYEE.promote_employee | **Medium** | PKG_EMPLOYEE.pkb: `AND ROWNUM=1` without ORDER BY in salary subquery; get_current_salary in PKG_PAYROLL correctly uses FETCH FIRST 1 ROW ONLY with ORDER BY EFFECTIVE_DATE DESC | Add ORDER BY EFFECTIVE_DATE DESC before ROWNUM=1; or use FETCH FIRST 1 ROW ONLY with ORDER BY to match PKG_PAYROLL.get_current_salary pattern |
| TD-19 | Federal tax hard-coded 2024 brackets will produce wrong results in 2025 and beyond; TAX_BRACKETS table exists with full schema; code contains `-- TODO: read from TAX_BRACKETS table` comment but reads hard-coded CASE statement | Configuration Risk | PKG_PAYROLL.calculate_federal_tax | **High** | PKG_PAYROLL.pkb: hard-coded bracket boundaries and rates in CASE statement; TAX_BRACKETS table DDL confirmed in Agent 1 OUTPUT for schema | Implement TAX_BRACKETS-based lookup; bracket table already provisioned; implement before Jan 2025 payroll |
| TD-20 | State tax uses simplified flat rates; HEAD_OF_HOUSEHOLD filing status falls into Single bracket (14,600 deduction, Single rates) rather than IRS-specified Head of Household brackets; additional Medicare tax applies flat 200,000 threshold for all filing statuses (IRS: 250,000 MFJ); may produce incorrect withholding | Configuration Risk | PKG_PAYROLL.calculate_federal_tax; PKG_PAYROLL.calculate_medicare | **High** | PKG_PAYROLL.pkb: `ELSE 14600` for non-MARRIED_JOINT (captures HoH); `c_medicare_addl_threshold = 200000` single value for all filing statuses | Add HEAD_OF_HOUSEHOLD bracket table; differentiate Medicare additional threshold by filing status (200,000 single, 250,000 MFJ, 125,000 MFS) |
| TD-21 | Pretax deductions not subtracted from federal/state taxable income in calculate_employee_pay: v_taxable_income := v_period_gross (gross pay before any deductions); 401k, medical, dental, vision, HSA are all pretax per PAY_ELEMENTS.PRETAX_FLAG='Y' but are deducted AFTER tax is calculated; employees are overtaxed by approximately the sum of their pretax deductions each period | Architecture Anti-pattern | PKG_PAYROLL.calculate_employee_pay | **High** | PKG_PAYROLL.pkb: `v_taxable_income := v_period_gross; -- Simplified: should subtract pretax deductions`; deduction loop runs after all tax insertions | Sum EMPLOYEE_PAY_ELEMENTS where PRETAX_FLAG='Y' before tax calculation; subtract from v_taxable_income; process pretax deductions before tax calculation in the deduction loop |
| TD-22 | reverse_payroll has no status pre-check: any run in any status (PENDING, CALCULATING, ERROR, APPROVED, PAID) can be reversed; reversing a PENDING or CALCULATING run produces orphaned PAYROLL_DETAILS rows with STATUS='REVERSED' while the run itself was never calculated | Architecture Anti-pattern | PKG_PAYROLL.reverse_payroll | **Medium** | PKG_PAYROLL.pkb: `UPDATE PAYROLL_RUNS SET STATUS='REVERSED'` with no WHERE STATUS check; contrast with approve_payroll which requires STATUS='CALCULATED' | Add pre-check: only allow reversal of runs with STATUS IN ('CALCULATED','APPROVED','PAID'); raise -20103 otherwise |
| TD-23 | submit_manager_review does not check review status before completing: a review in NOT_STARTED status (no self-assessment submitted) can be directly marked COMPLETED by a manager; bypasses the intended self-assessment → manager review workflow | Architecture Anti-pattern | PKG_PERFORMANCE.submit_manager_review | **Medium** | PKG_PERFORMANCE.pkb: UPDATE WHERE REVIEW_ID=p_review_id — no STATUS check in WHERE clause; contrast with submit_self_assessment which requires STATUS IN ('NOT_STARTED','SELF_REVIEW') | Add `AND STATUS = 'MANAGER_REVIEW'` to the UPDATE WHERE clause, or explicitly check status and raise -20402 |
| TD-24 | VW_LEAVE_SUMMARY overstates available leave balance by omitting PENDING deduction; reports using this view will show employees higher available balances than they can actually spend; balance check in PKG_LEAVE.submit_leave_request uses get_leave_balance (correct formula with PENDING) so the operational process is correct but reporting is misleading | Architecture Anti-pattern | VW_LEAVE_SUMMARY | **High** | DISC-003 resolved above: view formula confirmed `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT`; virtual column and PKG_LEAVE.get_leave_balance confirmed include PENDING | Correct VW_LEAVE_SUMMARY: change AVAILABLE calculation to `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING` to match virtual column and get_leave_balance |
| TD-25 | VW_ORG_HIERARCHY and get_org_chart performance degrades significantly for organisations with more than 500 employees; documented in source; CONNECT BY traversal has no pagination and returns full hierarchy subtree; PKG_EMPLOYEE.validate_manager's circular check is a separate traversal loop up to depth 15 (one DB query per level) | Scalability Constraint | PKG_EMPLOYEE.get_org_chart; VW_ORG_HIERARCHY; PKG_EMPLOYEE.validate_manager | **Medium** | PKG_EMPLOYEE.pkb — comment on get_org_chart; validate_manager loop SELECT per level; Agent 1 Infrastructure chunk: 200 concurrent users | Add WITH clause (Common Table Expression) recursive query as alternative to CONNECT BY for large hierarchies; add index on EMPLOYEES(MANAGER_EMP_ID); implement pagination parameter |
| TD-26 | Business days calculation in PKG_COMMON and PKG_LEAVE does not exclude public holidays from weekday count in PKG_COMMON.business_days_between and add_business_days; PKG_LEAVE.calculate_business_days correctly excludes holidays; creates inconsistency — leave day calculations are correct but any business day arithmetic using PKG_COMMON utilities (e.g. deadlines, SLA calculations) will overcount days | Architecture Anti-pattern | PKG_COMMON.business_days_between; PKG_COMMON.add_business_days | **Medium** | PKG_COMMON.pkb: `(Does NOT exclude public holidays — counts only weekdays)`; PKG_LEAVE.pkb: `SELECT COUNT(*) FROM HOLIDAYS ...` per day — correct implementation | Consolidate: update PKG_COMMON.business_days_between to call HOLIDAYS lookup as PKG_LEAVE.calculate_business_days does; deprecate the PKG_LEAVE version |

---

### Layer Summary — Application Layer

- Technologies confirmed this chunk: PL/SQL 19c (Active — core); DBMS_SCHEDULER (Declared-only — no DDL); DBMS_OUTPUT (Active — debug fallback); CONNECT BY (Active — core); Oracle Virtual Columns (Active — secondary)
- Patterns found this chunk: AP-07 through AP-24 (18 patterns)
- NFR entries added this chunk: NFR-18 through NFR-48 (31 entries)
- Technical debt entries added this chunk: TD-15 through TD-26 (12 entries — High: 7, Medium: 4, Low: 0)
- Agent 1 LOW CONFIDENCE items resolved: DISC-001 RESOLVED — 90-day Forms / 180-day DB trigger both real, different access paths; DISC-003 RESOLVED — VW_LEAVE_SUMMARY is wrong, virtual column formula authoritative; ARCH-003 CONFIRMED — business logic duplicated across Forms triggers (date gates) and DB triggers (defaulting, reactivation guard) and packages (main logic); ARCH-004 CONFIRMED — circular dependency confirmed but actual circle is narrower than Agent 1 stated; ARCH-007 CONFIRMED — YTD_GROSS/YTD_NET are 0 placeholders; LOW-012 CONFIRMED — race condition confirmed
- New LOW CONFIDENCE items raised: AP-02 confirmed dead code; AP-12 blocking lock in terminate_employee (FOR UPDATE with no NOWAIT — will wait indefinitely under concurrent load)
- DISCREPANCIES with Agent 1: None
- Cross-layer dependencies to carry to Synthesis: AP-15 tax brackets must align with TAX_BRACKETS table (Data layer); DISC-002 (EMPLOYEE_HISTORY columns) spans triggers (Chunk 4)

---

## Agent 2 — Chunk 3 of 4 — Integration & Notification Layer

**Agent 1 Input This Chunk:**
- Technologies: UTL_FILE, UTL_SMTP, UTL_TCP
- Components: PKG_INTEGRATION, PKG_NOTIFICATION
- Integrations: Oracle Financials GL (outbound), ADP Benefits (outbound), Time & Attendance (inbound, stub), SMTP (outbound)

**Carried Forward:**
- NFR entries: NFR-01 through NFR-48
- TD entries: TD-01 through TD-26
- Unresolved: DISC-002, LOW-003 through LOW-010

---

### Stage 2 — Technology Stack Assessment (Chunk 3: Integration Layer)

| Component | Declared Version | Usage Depth | How It Is Used in This System | EOL / Support Status | Agent 1 Match? |
|---|---|---|---|---|---|
| UTL_FILE | Oracle 19c built-in | Active — core path | Four Oracle directory objects; FOPEN mode 'W' (write) for all three outbound feeds; FOPEN mode 'R' (read) for TIME_ATTENDANCE_IN; max line buffer 32767 bytes on all four; each file opened and closed within single procedure call; no parallel writes; no file locking mechanism | Supported | Confirmed |
| UTL_SMTP | Oracle 19c built-in | Active — core path | One SMTP connection opened per email in process_queue; HELO, MAIL, RCPT, OPEN_DATA, CLOSE_DATA, QUIT protocol sequence explicitly coded; no AUTH command (unauthenticated relay); no STARTTLS or SSL variant; port 25; connection failure captured per-notification without aborting batch | Supported | Confirmed |
| UTL_TCP | Oracle 19c built-in | Active — secondary | Referenced in PKG_NOTIFICATION for UTL_TCP.CRLF constant used in email header construction; no direct TCP socket operations | Supported | Confirmed |
| Oracle Directory Objects | Oracle 19c feature | Active — core path | 4 objects: GL_FEED_OUT (write), BENEFITS_FEED_OUT (write), PAYROLL_OUTPUT (write — from PKG_PAYROLL), TIME_ATTENDANCE_IN (read); OS paths managed by DBA outside this repository; no source representation of CREATE DIRECTORY statements | Supported | Confirmed |
| Oracle Financials GL Integration | External batch | Active — core path | Fully implemented: pipe-delimited .dat file with H/D/T record format; header H\|HRMS_PAYROLL\|YYYY-MM-DD\|run_id; detail D\|cost_center\|gl_account\|debit\|credit\|description\|reference; trailer T\|count; EARNINGS → debit column; DEDUCTIONS/TAXES → credit column; only elements with GL_ACCOUNT_CODE set are included | N/A | Confirmed |
| ADP Benefits Integration | External batch | Active — core path | Fully implemented: fixed-width 203-character records; one record per employee-dependent pair (LEFT JOIN); RPAD padding to exact field widths; fields: EMP_NUMBER(10), FIRST_NAME(30), LAST_NAME(30), DATE_OF_BIRTH(10), HIRE_DATE(10), EMPLOYMENT_STATUS(12), MARITAL_STATUS(10), GENDER(1), DEP_FIRST_NAME(30), DEP_LAST_NAME(30), RELATIONSHIP(20), DEP_DOB(10) | N/A | Confirmed |
| Time & Attendance Integration | External inbound | Partial — stub | UTL_FILE.FOPEN and GET_LINE loop confirmed; CSV format confirmed (emp_number, date, hours_regular, hours_overtime); comment skip on '#' prefix confirmed; actual CSV parsing and database write: TODO — not implemented | N/A | Confirmed LOW — parsing stub only |
| LDAP / Active Directory Sync | External identity | Declared-only — not implemented | sync_org_structure is a one-line placeholder calling PKG_COMMON.log_info only; no LDAP connection, no directory query, no employee sync logic | N/A | Confirmed LOW |

---

### Stage 3 — Architecture Pattern Catalog (Chunk 3: Integration Layer)

| ID | Pattern Name | Category | Applies To | Exact Configuration | Coverage | Confidence | Source |
|---|---|---|---|---|---|---|---|
| AP-25 | Outbound Flat File Integration | Communication | PKG_INTEGRATION.generate_gl_journal; PKG_INTEGRATION.export_benefits_feed; PKG_PAYROLL.generate_pay_register | GL: pipe-delimited .dat, H/D/T record structure, COST_CENTER + GL_ACCOUNT_CODE grouping, FM999999990.00 format mask, Oracle directory GL_FEED_OUT; Benefits: fixed-width 203 chars, RPAD-padded, Oracle directory BENEFITS_FEED_OUT; Pay register: CSV with quoted name fields, Oracle directory PAYROLL_OUTPUT; all use UTL_FILE.FOPEN mode 'W', max_linesize 32767; all close file in EXCEPTION handler | Applied: 3 active outbound integrations; Time & Attendance inbound is a stub | HIGH | PKG_INTEGRATION.pkb; PKG_PAYROLL.pkb |
| AP-26 | Async Notification Queue | Communication | PKG_NOTIFICATION.send_notification → NOTIFICATION_QUEUE → process_queue | send_notification: PRAGMA AUTONOMOUS_TRANSACTION; inserts into NOTIFICATION_QUEUE with STATUS='PENDING'; never sends synchronously; COMMIT in autonomous transaction; process_queue: batch size 50 (DEFAULT); ORDER BY PRIORITY ASC, CREATED_DATE ASC; processes only EMAIL + PENDING + non-null RECIPIENT_EMAIL; opens/closes one SMTP connection per email | Applied: all 11 packages route email via this queue; no direct UTL_SMTP calls from business logic except process_queue | HIGH | PKG_NOTIFICATION.pkb — send_notification, process_queue |
| AP-27 | Manual Retry with Counter | Resilience | PKG_NOTIFICATION.retry_failed | On SMTP failure: UPDATE STATUS='FAILED', RETRY_COUNT=RETRY_COUNT+1; retry_failed resets STATUS='PENDING', ERROR_MESSAGE=NULL WHERE RETRY_COUNT < p_max_retries (DEFAULT 3); retry_failed must be called manually or by scheduler — not triggered automatically after failure; no exponential backoff; no dead-letter queue beyond max_retries | Applied: email notification only; no retry mechanism for UTL_FILE operations | HIGH — retry logic confirmed; manual invocation required confirmed | PKG_NOTIFICATION.pkb — process_queue EXCEPTION handler; retry_failed |
| AP-28 | Header-Detail-Trailer File Pattern | Communication | PKG_INTEGRATION.generate_gl_journal | H record: `H\|HRMS_PAYROLL\|YYYY-MM-DD\|run_id`; D records: one per cost_center/gl_account/element_type aggregation; T record: `T\|v_entries`; v_entries counts D records written; consumer: Oracle Financials batch import validates record counts against trailer | Applied: GL journal only; benefits and payroll CSV use no trailer | HIGH | PKG_INTEGRATION.pkb — generate_gl_journal |

---

### Stage 4 — NFR Registry Additions (Chunk 3: Integration Layer)

| ID | NFR Name | Value | Category | Source | Confidence |
|---|---|---|---|---|---|
| NFR-49 | GL journal file format | Pipe-delimited; max line 32767 bytes; Oracle directory object: GL_FEED_OUT; filename: GL_JOURNAL_{run_id}_{YYYYMMDD}.dat | Throughput | PKG_INTEGRATION.generate_gl_journal | HIGH |
| NFR-50 | Benefits feed record width | 203 characters (fixed-width RPAD-padded); Oracle directory: BENEFITS_FEED_OUT; filename: BENEFITS_{YYYYMMDD}.txt | Throughput | PKG_INTEGRATION.export_benefits_feed | HIGH |
| NFR-51 | SMTP connection model | One connection opened and closed per email message; no connection pooling; no persistent connection; no AUTH; no TLS; port 25 | Resource Management | PKG_NOTIFICATION.process_queue | HIGH |
| NFR-52 | Notification batch size | 50 per process_queue invocation (DEFAULT; configurable via p_batch_size) | Throughput | PKG_NOTIFICATION.process_queue | HIGH |
| NFR-53 | Notification processing order | PRIORITY ASC (lower number = higher priority), then CREATED_DATE ASC (FIFO within same priority) | Rate | PKG_NOTIFICATION.process_queue | HIGH |
| NFR-54 | Time & Attendance inbound file format | CSV: emp_number, date, hours_regular, hours_overtime; comment lines prefixed '#'; Oracle directory: TIME_ATTENDANCE_IN; max line 32767 bytes | Throughput | PKG_INTEGRATION.import_time_attendance | HIGH |
| NFR-55 | Payroll register filename format | PAY_REGISTER_{run_id}_{YYYYMMDD_HH24MISS}.csv; Oracle directory: PAYROLL_OUTPUT | Resource Management | PKG_PAYROLL.generate_pay_register | HIGH |

---

### Stage 5 — Technical Debt & Risk Register Additions (Chunk 3: Integration Layer)

| ID | Risk / Debt Item | Category | Affected Component(s) | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|---|
| TD-27 | SMTP relay on port 25 with no authentication and no TLS: PKG_NOTIFICATION.process_queue connects to smtp.internal.company.com:25; no AUTH command issued; no STARTTLS; email content (including employee names, leave dates, salary context) transmitted in cleartext on the internal network | Security Vulnerability | PKG_NOTIFICATION.process_queue → smtp.internal.company.com:25 | **High** | PKG_NOTIFICATION.pkb: UTL_SMTP.OPEN_CONNECTION('smtp.internal.company.com', 25); no AUTH call; no SSL variant | Enable STARTTLS or switch to port 587 with AUTH; alternatively implement SMTP AUTH PLAIN/LOGIN for the relay; assess whether internal relay truly requires no auth |
| TD-28 | One SMTP connection per email — inefficient for bulk notification batches: process_queue opens and closes a full TCP+SMTP handshake for each of up to 50 emails per batch run; during payroll runs where hundreds of notifications are queued, this creates N×(TCP open + HELO + MAIL + RCPT + DATA + QUIT + TCP close) round trips | Scalability Constraint | PKG_NOTIFICATION.process_queue | **Medium** | PKG_NOTIFICATION.pkb: UTL_SMTP.OPEN_CONNECTION / QUIT inside per-notification loop | Refactor process_queue to open one connection per batch, reusing it across multiple MAIL/RCPT/DATA sequences (UTL_SMTP supports this); close once after batch loop |
| TD-29 | Time & Attendance inbound integration is a stub: import_time_attendance reads and counts lines but performs no CSV parsing and no database write; if this integration is expected to feed hours into payroll calculations, payroll is operating without actual worked hours data | Operational Risk | PKG_INTEGRATION.import_time_attendance → (unwritten) payroll hours update | **High** | PKG_INTEGRATION.pkb: loop body contains only `-- TODO: parse CSV and update database`; v_imported incremented but no INSERT/UPDATE performed | Implement CSV parsing; write to a staging table or directly update PAYROLL_DETAILS; validate EMP_NUMBER before insert; ensure hours feed into calculate_employee_pay for hourly employees |
| TD-30 | No timeout on UTL_SMTP operations: UTL_SMTP.OPEN_CONNECTION does not specify a timeout parameter; if the SMTP relay is slow or unreachable, process_queue will hang indefinitely on the first failing email, blocking the entire batch and the DBMS_SCHEDULER job slot | Scalability Constraint | PKG_NOTIFICATION.process_queue | **Medium** | PKG_NOTIFICATION.pkb: `UTL_SMTP.OPEN_CONNECTION('smtp.internal.company.com', 25)` — no third parameter (timeout); UTL_SMTP.OPEN_CONNECTION accepts optional tx_timeout NUMBER parameter | Add tx_timeout: UTL_SMTP.OPEN_CONNECTION(c_smtp_host, c_smtp_port, tx_timeout => 30) — 30 seconds suggested |
| TD-31 | No file conflict handling in UTL_FILE outbound integrations: filenames for GL journal (GL_JOURNAL_{run_id}_{YYYYMMDD}.dat) include date but not time; if generate_gl_journal is called twice for the same run on the same day, the second call silently overwrites the first file with no error or archive copy | Operational Risk | PKG_INTEGRATION.generate_gl_journal; PKG_PAYROLL.generate_pay_register | **Low** | PKG_INTEGRATION.pkb: `v_filename := 'GL_JOURNAL_' \|\| p_run_id \|\| '_' \|\| TO_CHAR(SYSDATE,'YYYYMMDD') \|\| '.dat'`; UTL_FILE.FOPEN mode 'W' overwrites existing file; pay register filename includes HH24MISS so is lower risk | Add timestamp (HH24MISS) to GL journal filename; or check for file existence before writing (UTL_FILE.FGETATTR); archive previous version before overwrite |

---

### Layer Summary — Integration & Notification Layer

- Technologies confirmed: UTL_FILE (Active — core); UTL_SMTP (Active — core); UTL_TCP (Active — secondary); Oracle Directory Objects (Active — core); GL integration (Active — fully implemented); ADP Benefits (Active — fully implemented); Time & Attendance (Partial — stub); LDAP (Declared-only — not implemented)
- Patterns found: AP-25 through AP-28 (4 patterns)
- NFR entries added: NFR-49 through NFR-55 (7 entries)
- TD entries added: TD-27 through TD-31 (5 entries — High: 3, Medium: 2, Low: 1)
- Agent 1 items resolved: LOW-009 PARTIALLY RESOLVED — FTP credentials in SYSTEM_PARAMETERS confirmed referenced but key names still not in source; integration status flags GL_FEED_STATUS and BENEFITS_FEED_STATUS confirmed via get_integration_status
- Cross-layer dependencies: AP-26 async queue depends on DBMS_SCHEDULER job (no DDL — LOW-008 carries forward)

---

## Agent 2 — Chunk 4 of 4 — Data / Trigger Layer

**Agent 1 Input This Chunk:**
- Technologies: Oracle triggers (trg_employees.sql, trg_audit.sql), Oracle DDL, Oracle sequences
- Components: TRG_EMP_BEFORE_INSERT, TRG_EMP_BEFORE_UPDATE, TRG_EMP_INSTEAD_OF_DELETE, TRG_SALARY_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_DEPARTMENT_AUDIT
- DISC-002 resolution: EMPLOYEE_HISTORY column layout

---

### Stage 2 — Technology Stack Assessment (Chunk 4: Data/Trigger Layer)

| Component | Declared Version | Usage Depth | How It Is Used in This System | EOL / Support Status | Agent 1 Match? |
|---|---|---|---|---|---|
| Oracle Row-Level Triggers | Oracle 19c DDL | Active — core path | 6 triggers in source set: 3 on EMPLOYEES (defaulting, audit history, block delete), 3 on other tables (salary audit, leave status audit, department audit); all are row-level (FOR EACH ROW); timing: BEFORE (EMPLOYEES), AFTER (audit triggers); all audit triggers call PKG_AUDIT.log_action which is AUTONOMOUS_TRANSACTION | Supported | Confirmed |
| EMPLOYEE_HISTORY table — trigger layout | Project DDL | Active — core path | TRG_EMP_BEFORE_UPDATE inserts into EMPLOYEE_HISTORY using columns: HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE (VARCHAR2 flat string), NEW_VALUE (VARCHAR2 flat string), CHANGED_BY, CHANGE_REASON — this is the flat-string layout | Supported | DISCREPANCY — see DISC-002 resolution below |

---

**DISC-002 Resolution — EMPLOYEE_HISTORY Column Layout:**

Direct code evidence:
- DDL (01_core_tables.sql per Agent 1 Chunk 2): `HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE` — typed columns
- TRG_EMP_BEFORE_UPDATE (trg_employees.sql — direct read this chunk): `INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)` — flat string columns
- PKG_EMPLOYEE.log_history (PKG_EMPLOYEE.pkb — read in Chunk 2): `INSERT INTO EMPLOYEE_HISTORY (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE)` — matches DDL typed columns

**Resolution:** Two different INSERT patterns are writing to EMPLOYEE_HISTORY: (1) PKG_EMPLOYEE.log_history uses the DDL typed-column layout (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID, etc.) — these inserts succeed; (2) TRG_EMP_BEFORE_UPDATE uses a different flat-string layout (HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE) that does NOT match the DDL — these trigger inserts will fail at runtime with ORA-00904 (invalid column name) for HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE. **The DDL layout is authoritative. TRG_EMP_BEFORE_UPDATE has a runtime-fatal column name mismatch.** Every EMPLOYEES UPDATE (status change, dept change, job change) will raise an exception from the trigger, blocking the UPDATE. This is a **Critical production defect**.

---

### Stage 3 — Architecture Pattern Catalog (Chunk 4: Data/Trigger Layer)

| ID | Pattern Name | Category | Applies To | Exact Configuration | Coverage | Confidence | Source |
|---|---|---|---|---|---|---|---|
| AP-29 | Trigger-Based Audit Trail | Observability | TRG_SALARY_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_DEPARTMENT_AUDIT | TRG_SALARY_AUDIT: AFTER INSERT/UPDATE/DELETE on SALARY_RECORDS; captures JSON-formatted old/new values for salary and active_flag; TRG_LEAVE_REQUEST_AUDIT: AFTER UPDATE OF STATUS on LEAVE_REQUESTS (column-level trigger — only STATUS column changes fire it); TRG_DEPARTMENT_AUDIT: AFTER INSERT/UPDATE/DELETE on DEPARTMENTS — NO old/new values captured (passes only USER, not MODIFIED_BY); all delegate to PKG_AUDIT.log_action (AUTONOMOUS_TRANSACTION) | Partial — 3 of ~200 triggers; EMPLOYEES audit captured via PKG_EMPLOYEE.log_history and PKG_AUDIT.log_action calls in package code; remaining ~194 triggers not in source | HIGH — all 3 trigger bodies confirmed | trg_audit.sql |
| AP-30 | Trigger-Based Defaulting | Deployment | TRG_EMP_BEFORE_INSERT | Defaults: CREATED_BY := USER; CREATED_DATE := SYSDATE; ACTIVE_FLAG := 'Y'; EMPLOYMENT_STATUS := 'ACTIVE'; only applied when :NEW value IS NULL (non-destructive); these same defaults also set in PKG_EMPLOYEE.create_employee body (logic duplication) | Applied: all EMPLOYEES INSERT operations regardless of calling path | HIGH — confirmed in TRG_EMP_BEFORE_INSERT | trg_employees.sql |
| AP-31 | Trigger-Based Constraint Enforcement | Data Access | TRG_EMP_BEFORE_INSERT (hire date, email uniqueness); TRG_EMP_BEFORE_UPDATE (reactivation block, history logging) | TRG_EMP_BEFORE_INSERT: hire_date > SYSDATE+180 → -20501; email uniqueness among ACTIVE employees → -20502 (application-level unique, distinct from DB unique constraint); TRG_EMP_BEFORE_UPDATE: TERMINATED→ACTIVE transition blocked → -20503; TRG_EMP_INSTEAD_OF_DELETE: unconditional block → -20504 | Applied: all DML on EMPLOYEES regardless of path; TRG_EMP_BEFORE_UPDATE history insert is broken (DISC-002) | HIGH — all exception codes confirmed | trg_employees.sql |
| AP-32 | JSON Serialisation in Trigger Audit | Observability | TRG_SALARY_AUDIT | Manual string concatenation to produce JSON: `'{"emp_id":' \|\| :NEW.EMP_ID \|\| ',"salary":' \|\| :NEW.BASE_SALARY \|\| ',"effective":"' \|\| TO_CHAR(:NEW.EFFECTIVE_DATE,'YYYY-MM-DD') \|\| '"}'`; no escaping of string values; DATE formatted as YYYY-MM-DD; numeric values unquoted; DELETE captures emp_id and salary | Applied: SALARY_RECORDS only; TRG_DEPARTMENT_AUDIT passes NULL for old/new values | HIGH — JSON construction confirmed in trg_audit.sql | trg_audit.sql |

---

### Stage 4 — NFR Registry Additions (Chunk 4: Data/Trigger Layer)

| ID | NFR Name | Value | Category | Source | Confidence |
|---|---|---|---|---|---|
| NFR-56 | Maximum hire date future offset (database layer) | 180 days from SYSDATE (TRG_EMP_BEFORE_INSERT; error -20501) | Rate | trg_employees.sql — TRG_EMP_BEFORE_INSERT | HIGH |
| NFR-57 | Maximum hire date future offset (Forms UI layer) | 90 days from SYSDATE (HRMS_EMPLOYEE WHEN-VALIDATE-ITEM; DISC-001 resolved — this is the Forms-layer gate only) | Rate | HRMS_EMPLOYEE.xml — WHEN-VALIDATE-ITEM per Agent 1 | HIGH |
| NFR-58 | Email uniqueness scope | Case-insensitive; enforced among ACTIVE employees only (ACTIVE_FLAG='Y'); -20502 on duplicate | Rate | trg_employees.sql — TRG_EMP_BEFORE_INSERT | HIGH |
| NFR-59 | Audit JSON date format | YYYY-MM-DD (TO_CHAR with 'YYYY-MM-DD' mask) | Resource Management | trg_audit.sql — TRG_SALARY_AUDIT | HIGH |

---

### Stage 5 — Technical Debt & Risk Register Additions (Chunk 4: Data/Trigger Layer)

| ID | Risk / Debt Item | Category | Affected Component(s) | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|---|
| TD-32 | TRG_EMP_BEFORE_UPDATE runtime-fatal column name mismatch with EMPLOYEE_HISTORY DDL: trigger inserts into columns HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE; DDL defines HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID (typed columns); every UPDATE to EMPLOYEES that changes STATUS, DEPT_ID, or JOB_ID will raise ORA-00904 from this trigger, blocking the UPDATE | Security Vulnerability / Architecture Anti-pattern | TRG_EMP_BEFORE_UPDATE; all UPDATE operations on EMPLOYEES | **Critical** | trg_employees.sql: `INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)` — HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE do not exist in DDL | Fix trigger to use DDL column names: HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID/NEW_DEPT_ID, OLD_JOB_ID/NEW_JOB_ID; preserve old/new typed values rather than TO_CHAR conversions |
| TD-33 | TRG_DEPARTMENT_AUDIT does not capture old or new values in audit log: passes NULL for both p_old_values and p_new_values to PKG_AUDIT.log_action; department name, cost centre, and manager changes are audited only as action type (INSERT/UPDATE/DELETE) with no before/after state | Operational Risk | TRG_DEPARTMENT_AUDIT → AUDIT_LOG | **Medium** | trg_audit.sql: `PKG_AUDIT.log_action('DEPARTMENTS', NVL(:NEW.DEPT_ID, :OLD.DEPT_ID), v_action, USER)` — no v_old_json / v_new_json | Add JSON serialisation of :OLD/:NEW values as in TRG_SALARY_AUDIT pattern; at minimum capture DEPT_NAME, COST_CENTER, MANAGER_EMP_ID changes |
| TD-34 | TRG_DEPARTMENT_AUDIT uses USER (DB login) not MODIFIED_BY: passes `USER` (Oracle database session login name) as changed_by; PKG_AUDIT.log_action default is also USER; but application-level username (Forms login email) is tracked in MODIFIED_BY column; audit trail for department changes identifies the Oracle schema account (likely 'HRMS'), not the individual user | Operational Risk | TRG_DEPARTMENT_AUDIT → AUDIT_LOG | **Medium** | trg_audit.sql: `PKG_AUDIT.log_action('DEPARTMENTS', NVL(:NEW.DEPT_ID, :OLD.DEPT_ID), v_action, USER)` — USER vs NVL(:NEW.MODIFIED_BY, USER) as used in TRG_SALARY_AUDIT | Change to `NVL(:NEW.MODIFIED_BY, :OLD.MODIFIED_BY)` to capture application-level username |
| TD-35 | TRG_EMP_INSTEAD_OF_DELETE declared as BEFORE DELETE not INSTEAD OF: trigger name says INSTEAD_OF but DDL is `BEFORE DELETE ON HRMS.EMPLOYEES`; a BEFORE DELETE trigger cannot suppress the DELETE — it raises an exception which does prevent the delete but leaves a confusing error message if called from Forms DELETE_RECORD action | Architecture Anti-pattern | TRG_EMP_INSTEAD_OF_DELETE | **Low** | trg_employees.sql: `CREATE OR REPLACE TRIGGER HRMS.TRG_EMP_INSTEAD_OF_DELETE BEFORE DELETE ON HRMS.EMPLOYEES FOR EACH ROW`; source comment notes the naming inconsistency and Forms workaround | Rename to TRG_EMP_BEFORE_DELETE to match actual trigger type; or convert to a true INSTEAD OF trigger on a view if Oracle Forms architecture permits |
| TD-36 | Logic duplication between TRG_EMP_BEFORE_INSERT and PKG_EMPLOYEE.create_employee: both set ACTIVE_FLAG='Y', EMPLOYMENT_STATUS='ACTIVE', CREATED_BY, CREATED_DATE; the trigger provides a safety net for all INSERT paths, but the package body also sets these values; if the business rules change (e.g. new default status), they must be updated in two places | Architecture Anti-pattern | TRG_EMP_BEFORE_INSERT; PKG_EMPLOYEE.create_employee | **Low** | trg_employees.sql: `:NEW.ACTIVE_FLAG := 'Y'`; PKG_EMPLOYEE.pkb: `EMPLOYMENT_STATUS='ACTIVE', ACTIVE_FLAG='Y'` in INSERT | Designate trigger as the canonical source for defaulting; remove redundant assignments from package INSERT; or document that trigger is a safety net and keep both |

---

### Layer Summary — Data / Trigger Layer

- Technologies confirmed: Oracle row-level triggers (Active — core); EMPLOYEE_HISTORY flat-string layout confirmed in TRG_EMP_BEFORE_UPDATE (mismatches DDL)
- Patterns found: AP-29 through AP-32 (4 patterns)
- NFR entries added: NFR-56 through NFR-59 (4 entries)
- TD entries added: TD-32 through TD-36 (5 entries — Critical: 1, Medium: 2, Low: 2)
- Agent 1 LOW CONFIDENCE items resolved: DISC-002 RESOLVED — TRG_EMP_BEFORE_UPDATE uses flat-string column names that do NOT exist in DDL; this is a runtime-fatal defect; PKG_EMPLOYEE.log_history correctly uses typed DDL columns
- DISCREPANCIES with Agent 1: DISC-002 — Agent 1 flagged as uncertain; direct code read confirms the trigger column names are incorrect
- Cross-layer dependencies: TD-32 affects every UPDATE on EMPLOYEES; affects transfer, terminate, rehire, promote flows in PKG_EMPLOYEE

---

## Synthesis Pass

### Stage 6 — Architecture Pattern Catalog (Final)

Full consolidated catalog across all chunks:

| ID | Pattern Name | Category | Applies To | Exact Configuration | Coverage | Confidence | Source |
|---|---|---|---|---|---|---|---|
| AP-01 | AES-256 CBC Symmetric Encryption | Security | SSN and bank account fields | ENCRYPT_AES256+CHAIN_CBC+PAD_PKCS5; 32-byte key; key hard-coded as 'HR$ystem_3ncrypt10n_K3y_2024!!' | Partial — SSN/bank encrypted; gender/DOB/marital/nationality cleartext | HIGH | PKG_SECURITY.pkb |
| AP-02 | MD5 Password Hashing | Security | hash_password function | HASH_MD5; dead code — never called in authenticate() | Declared-but-unused | HIGH | PKG_SECURITY.pkb |
| AP-03 | Custom Session Table Authentication | Security | All Forms modules | USER_SESSIONS table; SEQ_USER_SESSION; 30-minute timeout from LOGIN_TIME; NO password verification | Applied everywhere; authentication bypass present | HIGH | PKG_SECURITY.pkb |
| AP-04 | Grade-Based Authorization | Security | All Forms modules | Grade >= 8: full; grade >= 5: VIEW all; any grade: LEAVE CREATE/VIEW + EMPLOYEE VIEW; thresholds 5 and 8 hard-coded | Partial — LEAVE and PERFORMANCE have no form-open check | HIGH | PKG_SECURITY.pkb |
| AP-05 | Autonomous Transaction | Cross-cutting | PKG_AUDIT.log_action; PKG_COMMON.log_error/log_info; PKG_EMPLOYEE.log_history; PKG_NOTIFICATION.send_notification | PRAGMA AUTONOMOUS_TRANSACTION on all 5; COMMIT on success; ROLLBACK on exception; failures silently swallowed | Applied: all 11 packages | HIGH | Multiple .pkb files |
| AP-06 | Configuration-as-Data | Deployment | SYSTEM_PARAMETERS → PKG_COMMON.get_param/set_param | EDITABLE_FLAG guard; typed accessors; -20900 on non-editable write; 10 seed params | Applied: SMTP, integration status, session policy, password policy | HIGH | PKG_COMMON.pkb |
| AP-07 | State Machine — Leave Request | Communication | LEAVE_REQUESTS.STATUS | PENDING→APPROVED/REJECTED; PENDING/APPROVED→CANCELLED; auto-approve if REQUIRES_APPROVAL='N' | Applied: all leave mutations | HIGH | PKG_LEAVE.pkb |
| AP-08 | State Machine — Payroll Run | Communication | PAYROLL_RUNS.STATUS | PENDING→CALCULATING→CALCULATED/ERROR→APPROVED→PAID→REVERSED; APPROVED requires CALCULATED; REVERSED has no pre-check | Partial — reverse has no guard | HIGH | PKG_PAYROLL.pkb |
| AP-09 | State Machine — Performance Review | Communication | PERFORMANCE_REVIEWS.STATUS | NOT_STARTED→MANAGER_REVIEW→COMPLETED→ACKNOWLEDGED; manager review has no status check | Partial — manager review guard missing | HIGH | PKG_PERFORMANCE.pkb |
| AP-10 | State Machine — Pay Period | Communication | PAY_PERIODS.STATUS | OPEN→CLOSED; -20102 on re-close; cannot create run for CLOSED period | Applied | HIGH | PKG_PAYROLL.pkb |
| AP-11 | Soft Delete | Data Access | All major tables | ACTIVE_FLAG CHAR(1) DEFAULT 'Y'; physical DELETE on EMPLOYEES blocked by trigger | Applied across all tables | HIGH | PKG_EMPLOYEE.pkb; trg_employees.sql |
| AP-12 | Row-Level Locking | Data Access | transfer_employee (NOWAIT); terminate_employee (blocking); leave approval | NOWAIT on transfer; blocking on terminate (indefinite wait risk) | Applied on key mutation paths | HIGH | PKG_EMPLOYEE.pkb; PKG_LEAVE.pkb |
| AP-13 | Partial Update via NVL | Data Access | PKG_EMPLOYEE.update_employee | NVL(p_param, existing_column) pattern for all updatable fields | update_employee only | HIGH | PKG_EMPLOYEE.pkb |
| AP-14 | Hierarchical Org Query (CONNECT BY) | Data Access | get_org_chart; VW_ORG_HIERARCHY | CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID; LEVEL <= p_max_depth (default 10); circular check to depth 15 via validate_manager loop | Applied; degrades >500 employees | HIGH | PKG_EMPLOYEE.pkb |
| AP-15 | Federal Tax Bracket Calculation | Data Access | calculate_federal_tax | Annualize → deduct → bracket → de-annualize → add extra WH; 2024 brackets hard-coded; 7 brackets each for Single and MFJ | Applied: all payroll runs | HIGH | PKG_PAYROLL.pkb |
| AP-16 | FICA Wage Base Capping | Data Access | calculate_fica | SS cap 168,600; 6.2% employee; LEAST() for partial period | Applied | HIGH | PKG_PAYROLL.pkb |
| AP-17 | Additional Medicare Tax | Data Access | calculate_medicare | Base 1.45%; addl 0.9% above 200,000 YTD; partial crossing handled | Applied | HIGH | PKG_PAYROLL.pkb |
| AP-18 | Circular Package Dependency | Dependency Coupling | PKG_EMPLOYEE ↔ PKG_PAYROLL | PKG_EMPLOYEE calls PKG_PAYROLL.create_salary_record; PKG_PAYROLL.calculate_payroll queries EMPLOYEES directly | Tight coupling | HIGH | PKG_EMPLOYEE.pkb; PKG_PAYROLL.pkb |
| AP-19 | Batch Commit Interval | Data Access | calculate_payroll (50); run_monthly_accrual (100) | Partial commits; no rollback on failure | Applied to both batch jobs; different intervals | HIGH | PKG_PAYROLL.pkb; PKG_LEAVE.pkb |
| AP-20 | Deduction Priority Ordering | Data Access | calculate_employee_pay | Priority ascending; override > flat > percentage; percentage of gross pre-pretax | Applied | HIGH | PKG_PAYROLL.pkb |
| AP-21 | Leave Balance Accrual Cap | Data Access | run_monthly_accrual | GREATEST(0, MAX_BALANCE - current) cap; tenure gate per leave type | Applied | HIGH | PKG_LEAVE.pkb |
| AP-22 | Carryover with Expiry | Data Access | process_carryover / expire_carryover | LEAST(remaining, CARRYOVER_MAX); expiry = Jan 1 next year + CARRYOVER_EXPIRY months | Applied | HIGH | PKG_LEAVE.pkb |
| AP-23 | Rating Scale Boundary Matching | Data Access | submit_manager_review | 1.0–5.0; 5 labels; >= boundaries; -20403 | Applied | HIGH | PKG_PERFORMANCE.pkb |
| AP-24 | Dynamic SQL with String Concatenation | Security (Anti-pattern) | search_employees | String concat for p_last_name, p_first_name; SQL injection possible | Only search function | HIGH | PKG_EMPLOYEE.pkb |
| AP-25 | Outbound Flat File Integration | Communication | generate_gl_journal; export_benefits_feed; generate_pay_register | GL: pipe-delimited .dat; Benefits: 203-char fixed-width; Payroll: CSV; all UTL_FILE FOPEN 'W' 32767 | 3 active outbound; inbound stub | HIGH | PKG_INTEGRATION.pkb; PKG_PAYROLL.pkb |
| AP-26 | Async Notification Queue | Communication | NOTIFICATION_QUEUE → process_queue | Async insert; batch 50; PRIORITY ASC; one SMTP connection per email | Applied: all 11 packages | HIGH | PKG_NOTIFICATION.pkb |
| AP-27 | Manual Retry with Counter | Resilience | retry_failed | Max 3 retries; manual invocation; no backoff; no DLQ | Email only; no retry for UTL_FILE | HIGH | PKG_NOTIFICATION.pkb |
| AP-28 | Header-Detail-Trailer File Pattern | Communication | generate_gl_journal | H/D/T records; D count in trailer | GL journal only | HIGH | PKG_INTEGRATION.pkb |
| AP-29 | Trigger-Based Audit Trail | Observability | TRG_SALARY_AUDIT; TRG_LEAVE_REQUEST_AUDIT; TRG_DEPARTMENT_AUDIT | After DML; delegates to PKG_AUDIT.log_action (autonomous tx); TRG_LEAVE is column-level (STATUS only) | 3 of ~200 triggers; departments missing old/new values | HIGH | trg_audit.sql |
| AP-30 | Trigger-Based Defaulting | Deployment | TRG_EMP_BEFORE_INSERT | CREATED_BY, CREATED_DATE, ACTIVE_FLAG, EMPLOYMENT_STATUS defaulted if NULL | All EMPLOYEES INSERT paths | HIGH | trg_employees.sql |
| AP-31 | Trigger-Based Constraint Enforcement | Data Access | TRG_EMP_BEFORE_INSERT; TRG_EMP_BEFORE_UPDATE; TRG_EMP_INSTEAD_OF_DELETE | Hire date 180-day limit; email uniqueness; reactivation block; delete block | All EMPLOYEES DML paths | HIGH | trg_employees.sql |
| AP-32 | JSON Serialisation in Trigger Audit | Observability | TRG_SALARY_AUDIT | Manual string concat JSON; numeric unquoted; date YYYY-MM-DD | SALARY_RECORDS only | HIGH | trg_audit.sql |

**Pattern Coverage Gaps:**

| Gap | Affected Integration / Component | Severity | Recommendation |
|---|---|---|---|
| No password verification in authenticate() | PKG_SECURITY.authenticate → all Forms users | Critical | Implement USER_CREDENTIALS SELECT + hash comparison immediately |
| No retry/circuit breaker on UTL_FILE operations | PKG_INTEGRATION, PKG_PAYROLL | High | Wrap UTL_FILE calls with retry on UTL_FILE.INVALID_OPERATION; alert on repeated failures |
| No timeout on UTL_SMTP.OPEN_CONNECTION | PKG_NOTIFICATION.process_queue | High | Add tx_timeout parameter to OPEN_CONNECTION |
| No rollback/compensation on partial batch commits | PKG_PAYROLL.calculate_payroll; PKG_LEAVE.run_monthly_accrual | High | Implement savepoint-based restart or pre-run cleanup |
| No rate limiting on any API entry point | Oracle Forms — no web API layer | Low — N/A for thick client | No action required for current architecture; relevant if self-service portal adds HTTP API |
| Missing CI/CD pipeline — all capabilities | Entire codebase | Critical (operational) | Implement source control gates: at minimum SQL*Plus syntax check + Oracle Forms compiler check; add PKG_SECURITY test for authentication before any deployment |

**Declared-But-Unused Libraries:**

| Library | Declared In | No Usage Found In | Risk |
|---|---|---|---|
| hash_password (HASH_MD5) | PKG_SECURITY.pkb | authenticate(), change_password() | Dead security code — creates false impression that passwords are hashed when they are not |
| PKG_VALIDATION.validate_required_fields | PKG_VALIDATION.pkb | No caller found in provided source | Dead validation — EMPLOYEES required fields not enforced via this path at runtime |
| TAX_BRACKETS table | DDL schema | PKG_PAYROLL.calculate_federal_tax | Table provisioned but ignored; hard-coded values used instead |
| EMPLOYEE_TAX_INFO.FILING_STATUS (HEAD_OF_HOUSEHOLD) | DDL CHK constraint allows | calculate_federal_tax ELSE branch (yields SINGLE rates) | HoH filing status falls into wrong bracket silently |

---

### Stage 7 — Component Interaction & Contract Map

| Caller | Target | Protocol | Interaction Type | Coupling Strength | Contract | Timeout Declared? | Error Handling | Notes |
|---|---|---|---|---|---|---|---|---|
| Oracle Forms (all modules) | PKG_SECURITY.is_session_valid | In-process PL/SQL | Sync Request-Response | Tight — direct call, no interface | Undocumented | No | Forms ON-ERROR handles -20301 | Called on every WHEN-NEW-FORM-INSTANCE via HRMS_COMMON_LIB |
| Oracle Forms (HRMS_EMPLOYEE) | PKG_EMPLOYEE | In-process PL/SQL | Sync Request-Response | Tight — direct call | Undocumented | No | ON-ERROR trigger | create_employee, update_employee, search_employees |
| Oracle Forms (HRMS_LEAVE) | PKG_LEAVE | In-process PL/SQL | Sync Request-Response | Tight | Undocumented | No | ON-ERROR trigger | submit_leave_request, cancel_leave_request |
| Oracle Forms (HRMS_PAYROLL) | PKG_PAYROLL | In-process PL/SQL | Sync Request-Response | Tight | Undocumented | No | ON-ERROR trigger | create_payroll_run, calculate_payroll, approve_payroll |
| PKG_EMPLOYEE | PKG_PAYROLL.create_salary_record | In-process PL/SQL | Sync | Tight — direct package call | Undocumented | No | EXCEPTION WHEN OTHERS → log + RAISE | Circular: PKG_PAYROLL also queries EMPLOYEES directly |
| PKG_EMPLOYEE | PKG_AUDIT.log_action | In-process PL/SQL | Async (autonomous tx) | Loose — autonomous transaction isolates | Undocumented | No | Silently swallowed in PKG_AUDIT | Called on all mutations |
| PKG_EMPLOYEE | PKG_NOTIFICATION.send_notification | In-process PL/SQL | Async (queue) | Loose — writes to queue; decoupled | Undocumented | No | Silently swallowed in PKG_NOTIFICATION | New hire, termination alerts |
| PKG_NOTIFICATION.process_queue | smtp.internal.company.com:25 | SMTP / UTL_SMTP | Async Fire-and-Forget | Loose — failure logged per notification | Undocumented | No — risk | STATUS='FAILED' + RETRY_COUNT++ | One connection per email; no TLS; no auth |
| PKG_INTEGRATION.generate_gl_journal | GL_FEED_OUT (OS filesystem) | Flat file / UTL_FILE | Async Fire-and-Forget | Loose — file dropped; Oracle Financials polls | Undocumented | No | EXCEPTION: close file + log_error + RAISE | Consumer: Oracle Financials batch import |
| PKG_INTEGRATION.export_benefits_feed | BENEFITS_FEED_OUT (OS filesystem) | Flat file / UTL_FILE | Async Fire-and-Forget | Loose | Undocumented | No | EXCEPTION: close file + log_error + RAISE | Consumer: ADP Benefits system; fixed-width 203 chars |
| PKG_INTEGRATION.import_time_attendance | TIME_ATTENDANCE_IN (OS filesystem) | Flat file / UTL_FILE | Sync (read) | Loose | Undocumented | No | Per-line error count; continues on line errors | Parsing stub — no DB write implemented |
| All packages | PKG_COMMON.log_error | In-process PL/SQL | Async (autonomous tx) | Loose | Undocumented | No | Silently swallowed; DBMS_OUTPUT fallback | Base error logging utility |
| PKG_SECURITY.authenticate | PKG_EMPLOYEE.set_session_context | In-process PL/SQL | Sync | Tight | Undocumented | No | None | Sets g_current_user, g_current_emp_id, g_current_dept_id package globals |

**Coupling Hotspots:**

| Component | Inbound Dependencies | Outbound Dependencies | Coupling Risk |
|---|---|---|---|
| PKG_AUDIT.log_action | Called by all 11 packages + 3 DB triggers | AUDIT_LOG table; SYS_CONTEXT | High — single point of failure; if AUDIT_LOG is unavailable, all business operations silently lose audit trail (exceptions swallowed) |
| PKG_COMMON (log_error, get_param) | Called by all 11 packages | AUDIT_LOG; SYSTEM_PARAMETERS | High — shared utility; SYSTEM_PARAMETERS inaccessibility would cascade to all config reads |
| EMPLOYEES table | Read/written by PKG_EMPLOYEE, PKG_PAYROLL, PKG_SECURITY, PKG_LEAVE, PKG_REPORTING, PKG_PERFORMANCE, PKG_INTEGRATION, 3 DB triggers | All business data | High — shared mutable state; no service boundary; all business processes have direct DML access |
| PKG_NOTIFICATION.send_notification | Called by PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE | NOTIFICATION_QUEUE; EMPLOYEES (email lookup) | Medium — async queue provides loose coupling |

**API Contract Inventory:**

| Boundary | Contract Type | Version | Location | Breaking Change Risk |
|---|---|---|---|---|
| GL journal file to Oracle Financials | Flat file (pipe-delimited, H/D/T) | UNVERSIONED | PKG_INTEGRATION.pkb (schema inline) | High — format changes break Oracle Financials import without coordination |
| Benefits feed to ADP | Fixed-width 203-char | UNVERSIONED | PKG_INTEGRATION.pkb (field widths inline) | High — ADP expects exact field positions; any layout change breaks vendor parse |
| Oracle Forms to PL/SQL packages | PL/SQL package spec | UNVERSIONED | plsql/packages/*.pks (not in provided source) | High — package spec changes break compiled Forms .fmx binaries |
| Self-service portal to PKG_LEAVE | UNKNOWN | UNKNOWN | Not in repository | High — portal calls PKG_LEAVE but contract is undocumented |
| SMTP email format | RFC 5321 (implicit) | N/A | PKG_NOTIFICATION.pkb | Low |

---

### Stage 8 — Operational Architecture Assessment

**CI/CD Pipeline Maturity**

> No CI/CD pipeline files found in repository. All capabilities assessed Absent. Stage 8 CI/CD evidence is sourced from Agent 1 Chunk 4 (LAYER NOT FOUND) and confirmed by direct check in this analysis.

| Capability | Present? | Evidence | Runs On | Gap Severity |
|---|---|---|---|---|
| Build | Absent | No docker build, mvn, gradle, dotnet build, npm run build, or make found in any file | — | Critical |
| Unit Tests | Absent | No jest, pytest, utPLSQL, SQL*Unit, or any test framework found | — | Critical |
| Integration Tests | Absent | No testcontainers, newman, or integration test runner found | — | Critical |
| Code Coverage Gate | Absent | No coverage tool found | — | High |
| SAST (Static Security) | Absent | No sonar, semgrep, codeql, snyk code found | — | Critical — system has confirmed SQL injection and authentication bypass |
| Dependency Scan | Absent | No snyk test, npm audit, owasp dependency-check found | — | High |
| Container / Image Scan | Absent | No container infrastructure; N/A for on-premises deployment | — | N/A |
| Secret / Credential Scan | Absent | No trufflehog, gitleaks, detect-secrets found; hard-coded AES key in source was not detected by any automated tool | — | Critical — hard-coded key currently undetected |
| Infrastructure Scan (IaC) | Absent | No IaC present; N/A | — | N/A |
| Automated Deploy | Absent | No deploy automation found; deployment is presumed manual Oracle DBA process | — | High |
| Smoke / Health Check Post-Deploy | Absent | No health check endpoints (thick client — no HTTP); no post-deploy test script | — | High |
| Auto Rollback | Absent | No rollback mechanism found | — | High |
| Manual Approval Gate | Absent | No gating mechanism in repository | — | Medium |
| Release / Versioning Automation | Absent | No semantic-release, git tag automation; APP_VERSION=4.2.0 set manually in SYSTEM_PARAMETERS | — | Low |

**Observability Coverage**

| Concern | Component | Present? | Tool / Library | Gap? |
|---|---|---|---|---|
| Structured Logging | All packages | Absent | DBMS_OUTPUT (unstructured debug); PKG_COMMON.log_error writes JSON-like string to AUDIT_LOG but not to a log aggregator | GAP — no structured log output; no log aggregation; logs visible only via AUDIT_LOG SELECT or SQL*Plus session |
| Distributed Tracing | All components | Absent | No OpenTelemetry, Jaeger, or any trace library | GAP — N/A for single-node Oracle monolith; Oracle AWR/ASH provides DB-level tracing if OEM configured |
| Metrics Export | All components | Absent | No Prometheus, Micrometer, StatsD | GAP — no application metrics; Oracle OEM may provide DB-level metrics externally |
| Correlation ID Propagation | All packages | Absent | No correlation ID pattern; SYS_CONTEXT SESSION_ID provides Oracle session correlation but not request-level | GAP |
| Health / Readiness Endpoints | All components | Absent | Oracle Forms thick client — no HTTP endpoints; no health check concept | GAP — operational health must be inferred from DB availability |
| Alerting Rules | System | Absent | No Alertmanager, CloudWatch, or alerting config in source | GAP — assumed Oracle OEM (LOW-013) |

**Deployment Safety**

| Practice | Present? | Evidence | Risk If Absent |
|---|---|---|---|
| Graceful Shutdown | No | No shutdown hook, no DBMS_SCHEDULER job stop sequence, no graceful drain | In-flight payroll calculations or leave approvals interrupted on DB restart |
| Readiness Probe | No | No k8s manifests; on-premises deployment — N/A for Kubernetes probes | N/A for current architecture |
| Liveness Probe | No | No k8s manifests — N/A | N/A for current architecture |
| Blue-Green / Canary | No | No deployment strategy declared; Oracle Forms deployment is all-or-nothing .fmx file replacement | Full traffic exposure on every Forms binary deployment |
| Feature Flags | No | No feature flag provider; GL_FEED_STATUS and BENEFITS_FEED_STATUS in SYSTEM_PARAMETERS function as manual on/off switches for integrations (not true feature flags) | No decoupled release; all changes immediately live on deployment |

**Disaster Recovery Posture**

| Item | Declared? | Detail | Source |
|---|---|---|---|
| Database backup configuration | No | No RMAN, Data Guard, or backup schedule in repository | NOT FOUND in any source file |
| Multi-region / multi-AZ config | No | On-premises single-site deployment per Agent 1 infrastructure analysis | NOT FOUND |
| Database replication | No | No Data Guard, GoldenGate, or replication configuration | NOT FOUND |
| RTO / RPO declarations | No | Not declared in any source file or README | NOT FOUND |

---

## Agent 2 — Final Analysis Summary

```
Layers analysed:                        4 — Security, Application, Integration, Data/Triggers
Chunks processed:                       4 (plus Chunk 0 Orientation)
Technologies assessed:                  17
Architecture patterns catalogued:       32 (AP-01 through AP-32)
NFR entries recorded:                   59 (NFR-01 through NFR-59)
Technical debt items identified:        36 (TD-01 through TD-36)
                                        Critical: 5, High: 18, Medium: 8, Low: 5
CI/CD pipeline files directly read:     0
CI/CD capabilities confirmed present:   0 of 14
Agent 1 LOW CONFIDENCE items resolved:  8 (DISC-001, DISC-002, DISC-003, ARCH-003,
                                        ARCH-004, ARCH-005, ARCH-006, ARCH-007)
Discrepancies with Agent 1:             1 — DISC-002 (TRG_EMP_BEFORE_UPDATE column
                                        mismatch confirmed as runtime-fatal)
```

---

## OUTPUT 1 — Technology Stack Assessment

| Component | Declared Version | Usage Depth | How It Is Used | EOL / Support Status | Agent 1 Match? |
|---|---|---|---|---|---|
| Oracle Database | 19c | Active — core path | Single HRMS schema; all 35+ tables; 29 sequences; 6 views; 6 triggers in source; all PL/SQL packages | Supported — Oracle 19c LTS until 2027 | Confirmed |
| PL/SQL | Oracle 19c | Active — core path | 11 packages; 80+ procedures; PRAGMA AUTONOMOUS_TRANSACTION; FOR UPDATE; dynamic SQL; CONNECT BY | Supported | Confirmed |
| Oracle Forms | 12c (12.2.1.4) | Active — core path | 6 of 18 form modules in source; WHEN-* triggers; PLL libraries; MDI shell navigation | Oracle Sustaining Engineering; standard support limited | Confirmed |
| Oracle WebLogic | 12c | Active — infrastructure | Hosts Oracle Forms Application Server | Standard support end Dec 2025 — HIGH EOL risk | Confirmed |
| DBMS_CRYPTO | Oracle 19c built-in | Active — core path | AES-256 CBC PKCS5 encryption (SSN, bank); HASH_MD5 (hash_password — dead code) | Supported; HASH_MD5 deprecated for security use | Confirmed |
| DBMS_OUTPUT | Oracle 19c built-in | Active — secondary (debug) | Fallback in log_error; batch job completion messages | Supported | Confirmed |
| DBMS_SCHEDULER | Oracle 19c built-in | Declared-only | Two jobs referenced in comments; no DDL in source | Supported | LOW — no DDL |
| UTL_FILE | Oracle 19c built-in | Active — core path | 4 Oracle directory objects; 3 outbound flat files; 1 inbound CSV (stub) | Supported | Confirmed |
| UTL_SMTP | Oracle 19c built-in | Active — core path | Email delivery; one connection per message; port 25; no TLS; no auth | Supported | Confirmed |
| UTL_RAW | Oracle 19c built-in | Active — secondary | Input conversion for DBMS_CRYPTO operations | Supported | Confirmed |
| UTL_TCP | Oracle 19c built-in | Active — secondary | CRLF constant for email headers only | Supported | Confirmed |
| SYS_CONTEXT | Oracle 19c built-in | Active — core path | IP_ADDRESS and SESSIONID capture in every PKG_AUDIT.log_action call | Supported | Confirmed |
| HRMS_COMMON_LIB | Project PLL | Active — core path | Toolbar, error handling, session check, date/name formatting; attached to all Forms except HRMS_LOGIN | N/A | Confirmed |
| HRMS_VALIDATION_LIB | Project PLL | Active — core path | Client-side validation; direct SELECT on JOB_GRADES; stricter than server-side counterparts | N/A | Confirmed |
| SYSTEM_PARAMETERS table | Project | Active — core path | Runtime config store via PKG_COMMON.get_param/set_param; 10 seed entries | N/A | Confirmed |
| USER_SESSIONS table | Project | Active — core path | Custom session management; SEQ_USER_SESSION; 30-min timeout | N/A | Confirmed |
| USER_CREDENTIALS table | Project | Declared-only — stub | DDL not in source; change_password references but does not write to it; authenticate does not read from it | UNKNOWN — DDL absent | LOW |

---

## OUTPUT 2 — Architecture Pattern Catalog

*(Full catalog in Stage 6 above — AP-01 through AP-32)*

### Pattern Coverage Gaps

| Gap | Affected Component | Severity | Recommendation |
|---|---|---|---|
| No password verification in authenticate() | PKG_SECURITY.authenticate | Critical | Implement USER_CREDENTIALS lookup + SHA-256 hash comparison |
| No secret scanning in CI/CD | Entire repository | Critical | Add gitleaks or detect-secrets to any pipeline; hard-coded key undetected |
| No retry on UTL_FILE operations | PKG_INTEGRATION, PKG_PAYROLL | High | Wrap FOPEN with retry on INVALID_OPERATION |
| No SMTP connection timeout | PKG_NOTIFICATION.process_queue | High | Add tx_timeout => 30 to UTL_SMTP.OPEN_CONNECTION |
| No rollback/compensation on batch partial commits | calculate_payroll, run_monthly_accrual | High | Savepoint-based restart or pre-run cleanup |
| No rate limiting | N/A for thick client | Low — N/A | Relevant only if HTTP API added |

### Declared-But-Unused Libraries

| Library | Declared In | No Usage Found In | Risk |
|---|---|---|---|
| hash_password (HASH_MD5) | PKG_SECURITY.pkb | authenticate(), change_password() | Dead security code — creates false impression passwords are hashed |
| PKG_VALIDATION.validate_required_fields | PKG_VALIDATION.pkb | No caller in provided source | EMPLOYEES required fields not enforced via this path |
| TAX_BRACKETS table | Schema DDL | PKG_PAYROLL.calculate_federal_tax | Table provisioned; hard-coded brackets used instead; will produce wrong results in 2025 |

---

## OUTPUT 3 — Component Interaction & Contract Map

*(Full interaction table and coupling hotspots in Stage 7 above)*

---

## OUTPUT 4 — Data Architecture Assessment

### Data Store Deep Dive

| Store | Access Pattern | ORM / Query Style | Transaction Scope | Consistency Model | Connection Pool Config | Migration State | Agent 1 Match? |
|---|---|---|---|---|---|---|---|
| Oracle DB 19c — HRMS schema | Repository (all access via PL/SQL packages) | Raw PL/SQL SQL (no ORM); cursors; REF CURSOR return; FOR UPDATE row locks | Method-level: each package procedure controls its own COMMIT/ROLLBACK; PRAGMA AUTONOMOUS_TRANSACTION for audit/notification; partial commits in batch jobs | Strong — Oracle serializable default; FOR UPDATE NOWAIT on transfer; blocking FOR UPDATE on terminate | DEFAULT — no Hikari or JDBC pool config in source; Oracle Forms uses Oracle Net; pool managed by WebLogic/Oracle Forms AS outside this repo | Migrations present (DDL SQL files); README states 42 tables but only 35 DDL-confirmed; 7 tables referenced in code but DDL absent | Confirmed |

### Data Ownership Map

| Entity / Table | Owning Service | Other Services With Access | Access Type | Coupling Risk |
|---|---|---|---|---|
| EMPLOYEES | PKG_EMPLOYEE | PKG_PAYROLL, PKG_SECURITY, PKG_LEAVE, PKG_PERFORMANCE, PKG_REPORTING, PKG_INTEGRATION, PKG_AUDIT (via triggers), PKG_NOTIFICATION | Read-write by PKG_EMPLOYEE; read by all others | ANTIPATTERN — shared mutable table with no service boundary |
| SALARY_RECORDS | PKG_PAYROLL | PKG_EMPLOYEE (create_salary_record call), PKG_REPORTING | PKG_EMPLOYEE writes via PKG_PAYROLL; PKG_PAYROLL owns; PKG_REPORTING reads | Tight — cross-package write via explicit dependency |
| LEAVE_REQUESTS | PKG_LEAVE | PKG_EMPLOYEE (cancel pending on terminate) | PKG_LEAVE owns write; PKG_EMPLOYEE writes on termination | Tight — PKG_EMPLOYEE bypasses PKG_LEAVE for termination cancellation |
| EMPLOYEE_HISTORY | PKG_EMPLOYEE.log_history | TRG_EMP_BEFORE_UPDATE (broken — TD-32) | PKG_EMPLOYEE owns; trigger has non-functional write | Tight — duplicated write paths, one broken |
| AUDIT_LOG | PKG_AUDIT | All 11 packages + 3 DB triggers | All write only; PKG_AUDIT owns read/purge | Tight — single audit table for all audit, error, and info logs |
| NOTIFICATION_QUEUE | PKG_NOTIFICATION | PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, PKG_PERFORMANCE (write via send_notification) | PKG_NOTIFICATION owns; all others write asynchronously | Loose — async queue pattern |
| SYSTEM_PARAMETERS | PKG_COMMON | All packages read via get_param | PKG_COMMON owns write (set_param); all others read | Medium — central config store; shared read |

### Data Flow & Consistency Notes

- LEAVE_BALANCES.AVAILABLE is a virtual column (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING); VW_LEAVE_SUMMARY uses an incorrect formula omitting PENDING — **defect confirmed (TD-24)**
- SALARY_RECORDS uses an end-date pattern for historisation: on any salary change, previous record gains END_DATE=effective_date-1, ACTIVE_FLAG='N'; current salary = WHERE ACTIVE_FLAG='Y' AND EFFECTIVE_DATE<=SYSDATE AND (END_DATE IS NULL OR END_DATE>SYSDATE)
- EMPLOYEE_HISTORY has two incompatible insert patterns (PKG_EMPLOYEE.log_history and TRG_EMP_BEFORE_UPDATE); the trigger version is runtime-fatal
- YTD accruals use PAYROLL_DETAILS joined to PAY_PERIODS.PERIOD_START_DATE YEAR — cross-year payroll periods (biweekly spanning December/January) will attribute earnings to the period start year, which may differ from pay date year
- All sequences are NOCACHE except SEQ_AUDIT (CACHE 100); NOCACHE sequences create serialization contention under concurrent inserts (each NEXTVAL requires a DB checkpoint); for 200 concurrent users this is a throughput risk on high-volume tables

---

## OUTPUT 5 — Security Architecture Assessment

### Authentication & Authorisation Implementation

| Mechanism | Declared (Agent 1) | Implemented How | Validation Completeness | Gaps | Severity |
|---|---|---|---|---|---|
| Oracle Forms Custom Session Auth | Custom Oracle Forms session via PKG_SECURITY + USER_SESSIONS | SELECT from EMPLOYEES WHERE UPPER(EMAIL)=UPPER(p_username) AND EMPLOYMENT_STATUS='ACTIVE'; insert USER_SESSIONS row; NO password verification | Minimal — username match only; p_password parameter accepted but unused | No USER_CREDENTIALS lookup; no hash comparison; complete authentication bypass | Critical |
| MD5 Password Hash | Oracle DBMS_CRYPTO.HASH_MD5 | hash_password function exists but is dead code — not called from authenticate() or change_password() | None — function exists but is never invoked in any security path | MD5 not used; authentication requires no password at all | Critical |
| Grade-based Permission | PKG_SECURITY.has_permission (grade thresholds) | Hard-coded grade thresholds: >=8 full, >=5 VIEW, any grade LEAVE/EMPLOYEE VIEW | Partial — module-level checks; no row-level or data-level access control; LEAVE and PERFORMANCE modules have no form-open check | LEAVE and PERFORMANCE accessible to all authenticated users; no check on what data rows each user can access | High |
| AES-256 CBC PKCS5 SSN Encryption | Oracle DBMS_CRYPTO.ENCRYPT_AES256 | Correctly implemented — ENCRYPT_AES256 + CHAIN_CBC + PAD_PKCS5; decrypt fallback returns '***DECRYPT_ERROR***' | Partial — SSN and bank accounts encrypted; gender, DOB, marital status, nationality stored cleartext | Encryption key hard-coded in source (TD-02); no key rotation mechanism | Critical |

### Secrets Posture

| Item | Finding | Severity | Evidence |
|---|---|---|---|
| AES-256 encryption key | Hard-coded in PKG_SECURITY package body: 'HR$ystem_3ncrypt10n_K3y_2024!!' | Critical | PKG_SECURITY.pkb: c_encryption_key CONSTANT RAW(32) |
| FTP integration credentials | Stored in SYSTEM_PARAMETERS table (plaintext) | High | PKG_INTEGRATION.pks header comment; SYSTEM_PARAMETERS not encrypted |
| SMTP relay | No credential (unauthenticated relay on port 25) | Medium | PKG_NOTIFICATION.pkb: no AUTH call |
| DB connection credentials | Not in source (managed by WebLogic datasource externally) | Low — managed | README / Agent 1: outside repository scope |

### Attack Surface Summary

| Surface | Exposure | Mitigations Found | Gaps |
|---|---|---|---|
| Oracle Forms login | Complete authentication bypass — any known active employee email grants a session | Session table (USER_SESSIONS); session timeout 30 min from LOGIN_TIME | No password verification; no account lockout; password cleartext over HTTP; timing attack |
| PKG_EMPLOYEE.search_employees | SQL injection via p_last_name and p_first_name parameters | Oracle Forms LOV passes pre-validated values (partial mitigation for Forms users only) | Direct PL/SQL callers fully vulnerable; bind variables not used |
| SSN and bank account data | Encrypted at column level with AES-256 | AES-256 CBC PKCS5 implemented correctly | Key hard-coded in source; any developer can decrypt all PII |
| SMTP notifications | Email content in cleartext; unauthenticated relay | NOTIFICATION_QUEUE async pattern limits synchronous exposure | No TLS; no AUTH; employee PII in email bodies |
| SYSTEM_PARAMETERS table | FTP credentials in plaintext; readable by any DB user with SELECT privilege | EDITABLE_FLAG write guard | No encryption of sensitive parameter values |
| PII data (unencrypted) | GENDER, DATE_OF_BIRTH, MARITAL_STATUS, NATIONALITY stored as cleartext columns | ACTIVE_FLAG soft delete; AUDIT_LOG captures access | No column-level encryption or masking for cleartext PII |

---

## OUTPUT 6 — NFR Registry

*(Full registry: NFR-01 through NFR-59 — see per-chunk Stage 4 outputs above for complete table. Summary below.)*

| Range | Layer / Area |
|---|---|
| NFR-01 – NFR-17 | Security Layer (session timeout, password policy, encryption specs, audit retention, fiscal year) |
| NFR-18 – NFR-48 | Application Layer (tax brackets, payroll rates, batch intervals, leave rules, employee number format, performance rating) |
| NFR-49 – NFR-55 | Integration Layer (file formats, SMTP model, batch sizes) |
| NFR-56 – NFR-59 | Data/Trigger Layer (hire date offsets, email uniqueness, audit date format) |

---

## OUTPUT 7 — Technical Debt & Risk Register

*(Sorted by severity descending)*

**Critical (5):**

| ID | Item | Category |
|---|---|---|
| TD-01 | Authentication bypass in PKG_SECURITY.authenticate — p_password never verified | Security Vulnerability |
| TD-02 | AES-256 key hard-coded: 'HR$ystem_3ncrypt10n_K3y_2024!!' in package body | Security Vulnerability |
| TD-03 | SQL injection in PKG_EMPLOYEE.search_employees — p_last_name/p_first_name string-concatenated | Security Vulnerability |
| TD-04 | MD5 hash_password function is dead code; authenticate grants sessions without any password check | Security Vulnerability |
| TD-32 | TRG_EMP_BEFORE_UPDATE inserts into EMPLOYEE_HISTORY with wrong column names — runtime-fatal ORA-00904 on every STATUS/DEPT/JOB change | Architecture Anti-pattern |

**High (18):**

| ID | Item | Category |
|---|---|---|
| TD-05 | FTP credentials in plaintext in SYSTEM_PARAMETERS | Security Vulnerability |
| TD-06 | No account lockout on failed authentication attempts | Security Vulnerability |
| TD-07 | Session timeout from LOGIN_TIME not last activity | Security Vulnerability |
| TD-08 | Duplicate email ROWNUM=1 silently picks MIN(EMP_ID) | Security Vulnerability |
| TD-09 | Oracle WebLogic 12c standard support ends Dec 2025 | EOL Technology |
| TD-10 | Oracle Forms 12c in Sustaining Engineering | EOL Technology |
| TD-11 | Password transmitted in cleartext (Oracle Forms HTTP) | Security Vulnerability |
| TD-15 | YTD_GROSS/YTD_NET hard-coded 0 on all payslips | Operational Risk |
| TD-16 | Race condition in generate_emp_number (MAX+1 not sequence) | Architecture Anti-pattern |
| TD-17 | Partial commits in calculate_payroll leave unrecoverable half-calculated state | Architecture Anti-pattern |
| TD-19 | Federal tax brackets hard-coded 2024 — wrong in 2025 | Configuration Risk |
| TD-20 | HoH filing status uses wrong brackets; Medicare uses wrong MFJ threshold | Configuration Risk |
| TD-21 | Pretax deductions not subtracted from taxable income — employees overtaxed | Architecture Anti-pattern |
| TD-24 | VW_LEAVE_SUMMARY overstates available balance (missing PENDING) | Architecture Anti-pattern |
| TD-27 | SMTP port 25 no auth no TLS | Security Vulnerability |
| TD-29 | Time & Attendance inbound integration is a stub — no DB write | Operational Risk |
| TD-30 | No timeout on UTL_SMTP.OPEN_CONNECTION — can hang indefinitely | Scalability Constraint |
| TD-31 | GL journal overwritten by same-day re-run (no file conflict handling) | Operational Risk |

**Medium (8):** TD-12 (timing attack), TD-14 (client/server validation drift), TD-18 (non-deterministic salary ROWNUM), TD-22 (reverse_payroll no status check), TD-23 (manager review no status check), TD-25 (CONNECT BY degrades >500 employees), TD-26 (PKG_COMMON business_days excludes holidays), TD-33 (TRG_DEPARTMENT_AUDIT no old/new values), TD-34 (TRG_DEPARTMENT_AUDIT uses USER not MODIFIED_BY)

**Low (5):** TD-13 (log_info missing quote escaping), TD-28 (one SMTP connection per email inefficiency), TD-35 (trigger named INSTEAD_OF but declared BEFORE DELETE), TD-36 (defaulting logic duplicated in trigger and package)

---

## OUTPUT 8 — Operational Architecture Assessment

*(Full four-section assessment in Stage 8 above)*

---

## Validation Queue

| ID | Item | Chunk | Reason |
|---|---|---|---|
| LOW-001 | PKG_DEPARTMENT — source not provided | 1 | Missing source; inferred from package cross-references |
| LOW-002 | HRMS_REPORTS, HRMS_ADMIN, HRMS_DEPARTMENT forms | 1 | Referenced via OPEN_FORM; source not provided |
| LOW-003 | Oracle Reports 8×.rdf files | 3 | Named in README; not in source |
| LOW-004 | 194+ database triggers | 4 | README states 200+; only 6 provided |
| LOW-005 | 9 missing views | 4 | 15 declared in README; 6 provided |
| LOW-006 | EMPLOYEE_PAY_ELEMENTS DDL | 2 | Referenced in PKG_PAYROLL; DDL not provided |
| LOW-007 | RPT_* reporting tables | 2 | Referenced in PKG_REPORTING.refresh_reporting_tables; no DDL |
| LOW-008 | DBMS_SCHEDULER job DDL | 3 | process_queue and run_monthly_accrual in comments; no CREATE JOB |
| LOW-009 | FTP credential key names in SYSTEM_PARAMETERS | 3 | Header comment only; key names not in source |
| LOW-010 | Self-service portal | 3 | Referenced in PKG_LEAVE.pks; no source or URL |
| LOW-011 | USER_CREDENTIALS table DDL | 1 | Referenced in change_password; no DDL; authentication confirmed as stub |
| LOW-013 | Oracle Enterprise Manager monitoring | 4 | Assumed; no config in repository |
| ASSUMED-01 | Oracle Forms AS HTTPS configuration | Security | Oracle Forms AS/WebLogic SSL capability assumed available but no config in source; TCP transport to client is likely HTTP not HTTPS |

---

## Agent 1 Discrepancy Log

| # | What Agent 1 Said | What Code Shows | Status |
|---|---|---|---|
| DISC-001 | Hire date limit: 90 days (Forms) vs 180 days (DB trigger) | Both correct for their layers: 90 days is the Forms UI client-side gate; 180 days is the DB trigger hard limit enforced for all callers; PKG_EMPLOYEE.create_employee bypasses the 90-day Forms check and is only subject to 180-day trigger | RESOLVED — both rules are real; different limits by access path |
| DISC-002 | EMPLOYEE_HISTORY: DDL has typed columns (OLD_DEPT_ID etc.); TRG_EMP_BEFORE_UPDATE inserts flat strings (OLD_VALUE, NEW_VALUE) | TRG_EMP_BEFORE_UPDATE uses HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE which do NOT exist in DDL; runtime-fatal ORA-00904; PKG_EMPLOYEE.log_history correctly uses DDL column names | RESOLVED — trigger is wrong; DDL is authoritative; trigger blocks all EMPLOYEES UPDATEs that change STATUS/DEPT/JOB |
| DISC-003 | VW_LEAVE_SUMMARY AVAILABLE omits PENDING; virtual column includes PENDING | PKG_LEAVE.get_leave_balance also includes PENDING; VW_LEAVE_SUMMARY is the defective party; overstates available leave balance in all reports using that view | RESOLVED — virtual column and get_leave_balance are authoritative; VW_LEAVE_SUMMARY has a defect (TD-24) |

---

Agent 2 Analysis Complete.
Documentation is ready for technical review.

**Highest-priority action items (in order):**
1. **TD-32 / DISC-002 — Critical production defect:** TRG_EMP_BEFORE_UPDATE blocks all EMPLOYEES UPDATE operations that change STATUS, DEPT_ID, or JOB_ID with ORA-00904. Every transfer, termination, and job change is currently failing at the database trigger layer. Fix column names to match DDL immediately.
2. **TD-01 — Authentication bypass:** PKG_SECURITY.authenticate grants sessions without password verification. System has no authentication. Disable external access until fixed.
3. **TD-02 — Exposed encryption key:** Hard-coded AES-256 key in source means all SSNs and bank account numbers are decryptable by anyone with source access. Rotate key and re-encrypt all protected columns.
