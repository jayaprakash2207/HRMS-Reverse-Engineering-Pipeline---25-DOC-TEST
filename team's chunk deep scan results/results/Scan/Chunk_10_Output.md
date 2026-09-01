=== CHUNK METADATA ===
Chunk: 10            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-body
Expected files (1):
  1. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb (25889 chars written)
Total source content: 46030 characters (budget: 30000)  (over budget — a single large file couldn't be split)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: Payroll processing — salary history, pay period/run lifecycle, tax and deduction calculation, payslip and pay register reporting

**STRUCTURES:**
  c_ss_wage_base_2024 — KIND: constant; TYPE: NUMBER
  c_ss_rate — KIND: constant; TYPE: NUMBER
  c_medicare_rate — KIND: constant; TYPE: NUMBER
  c_medicare_addl_rate — KIND: constant; TYPE: NUMBER
  c_medicare_addl_threshold — KIND: constant; TYPE: NUMBER
  c_standard_deduction_single — KIND: constant; TYPE: NUMBER
  c_standard_deduction_married — KIND: constant; TYPE: NUMBER
  c_allowance_amount — KIND: constant; TYPE: NUMBER

**METHODS:**
  **PROCEDURE create_salary_record(p_emp_id NUMBER, p_effective_date DATE, p_base_salary NUMBER, p_change_reason VARCHAR2 DEFAULT NULL, p_change_pct NUMBER DEFAULT NULL, p_currency_code VARCHAR2 DEFAULT 'USD', p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER)** [SOURCE: L27-70]
  - What it does: Validates p_base_salary is positive; end-dates the employee's currently active SALARY_RECORDS row (ACTIVE_FLAG='Y', EFFECTIVE_DATE < new effective date) by setting END_DATE to the day before the new effective date and ACTIVE_FLAG='N' [L47-54]; inserts a new SALARY_RECORDS row with ACTIVE_FLAG='Y', SALARY_BASIS='ANNUAL' [L57-67]; logs the insert via PKG_AUDIT.log_action [L69].
  - Business rules: Base salary must be positive, else error -20101 [L40-42]. Only one salary record is active per employee at a time — the prior active record is end-dated the day before the new one starts.
  - Numbers & thresholds: -20101 (error code for non-positive salary). Default p_currency_code = 'USD'. Default p_pay_frequency = 'MONTHLY'. SALARY_BASIS hardcoded to 'ANNUAL'. END_DATE = p_effective_date - 1.
  - Security & error handling: RAISE_APPLICATION_ERROR(-20101, 'Salary must be positive: ' || p_base_salary) if p_base_salary <= 0; no other input validation; p_user defaults to session USER.
  - Data in/out: Inputs — p_emp_id, p_effective_date, p_base_salary (required); p_change_reason, p_change_pct, p_currency_code, p_pay_frequency, p_user (optional). Output — updates then inserts SALARY_RECORDS (SALARY_ID from SEQ_SALARY.NEXTVAL); writes an audit log entry.

  **FUNCTION get_current_salary(p_emp_id NUMBER) RETURN NUMBER** [SOURCE: L75-96]
  - What it does: Selects BASE_SALARY from SALARY_RECORDS where ACTIVE_FLAG='Y', EFFECTIVE_DATE <= SYSDATE, and (END_DATE IS NULL OR END_DATE > SYSDATE), ordered by EFFECTIVE_DATE DESC, taking the first row.
  - Business rules: A salary record is "current" only if active, already effective, and not yet expired.
  - Numbers & thresholds: FETCH FIRST 1 ROW ONLY.
  - Security & error handling: NO_DATA_FOUND caught, returns 0 instead of propagating.
  - Data in/out: Input — p_emp_id. Output — returns BASE_SALARY (NUMBER), or 0 if none found.

  **FUNCTION get_salary_as_of(p_emp_id NUMBER, p_as_of DATE) RETURN NUMBER** [SOURCE: L101-122]
  - What it does: Selects BASE_SALARY from SALARY_RECORDS where EFFECTIVE_DATE <= p_as_of and (END_DATE IS NULL OR END_DATE >= p_as_of), ordered by EFFECTIVE_DATE DESC, taking the first row — a point-in-time lookup not restricted to ACTIVE_FLAG.
  - Business rules: Salary as of a date is the most recent record whose effective range covers that date.
  - Numbers & thresholds: FETCH FIRST 1 ROW ONLY.
  - Security & error handling: NO_DATA_FOUND caught, returns 0.
  - Data in/out: Inputs — p_emp_id, p_as_of. Output — returns BASE_SALARY (NUMBER), or 0 if none found.

  **PROCEDURE create_pay_periods(p_year NUMBER, p_frequency VARCHAR2 DEFAULT 'MONTHLY', p_user VARCHAR2 DEFAULT USER)** [SOURCE: L128-208]
  - What it does: For MONTHLY, loops months 1 through 12, sets start = 1st of month, end = LAST_DAY(start), pay date = end adjusted for weekends, inserts one PAY_PERIODS row per month with STATUS='OPEN' [L140-167]. For BIWEEKLY, finds the first Friday of p_year, backs up 13 days to anchor the first period, then loops 14-day periods (end = start+13, pay date = end+5), inserting a row when the period's start or end year matches p_year, while EXTRACT(YEAR FROM start) <= p_year [L171-204]. Commits at the end [L207].
  - Business rules: Monthly pay date moves to Friday if it falls on Saturday (-1 day) or Sunday (-2 days). Biweekly periods are Friday-anchored, 14 days long; a biweekly period is kept only if its start or end date falls in the target year.
  - Numbers & thresholds: 12 (months per year, loop 1..12). Saturday pay-date shift = -1 day; Sunday pay-date shift = -2 days. Biweekly period span: v_end_date = v_start_date + 13 (14-day period). Biweekly anchor back-up = 13 days. Biweekly pay date = period end + 5 days.
  - Security & error handling: None — no validation of p_year or p_frequency; an unrecognized frequency inserts nothing.
  - Data in/out: Inputs — p_year, p_frequency (default 'MONTHLY'), p_user. Output — inserts PAY_PERIODS rows (PERIOD_ID from SEQ_PAY_PERIOD.NEXTVAL, STATUS='OPEN'); COMMIT.

  **PROCEDURE close_pay_period(p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L213-237]
  - What it does: Locks and reads the period's STATUS (SELECT ... FOR UPDATE); if already 'CLOSED' raises an error; otherwise updates STATUS to 'CLOSED' with CLOSED_BY/CLOSED_DATE and MODIFIED_BY/MODIFIED_DATE.
  - Business rules: A period already CLOSED cannot be closed again.
  - Numbers & thresholds: -20102 (error code).
  - Security & error handling: RAISE_APPLICATION_ERROR(-20102, 'Period already closed: ' || p_period_id); row locked via FOR UPDATE against concurrent close.
  - Data in/out: Inputs — p_period_id, p_user. Output — updates PAY_PERIODS (STATUS, CLOSED_BY, CLOSED_DATE, MODIFIED_BY, MODIFIED_DATE).

  **FUNCTION get_current_period RETURN NUMBER** [SOURCE: L242-257]
  - What it does: Selects PERIOD_ID from PAY_PERIODS where SYSDATE is between PERIOD_START_DATE and PERIOD_END_DATE and STATUS='OPEN', limited with ROWNUM = 1.
  - Business rules: The "current" period is the OPEN period whose range contains today.
  - Numbers & thresholds: ROWNUM = 1.
  - Security & error handling: NO_DATA_FOUND caught, returns NULL.
  - Data in/out: Input — none (uses SYSDATE). Output — returns PERIOD_ID or NULL.

  **FUNCTION create_payroll_run(p_period_id NUMBER, p_run_type VARCHAR2 DEFAULT 'REGULAR', p_user VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L262-295]
  - What it does: Reads the period's STATUS; if 'CLOSED' raises an error; otherwise generates RUN_ID from SEQ_PAYROLL_RUN.NEXTVAL and inserts a PAYROLL_RUNS row with STATUS='PENDING'.
  - Business rules: A payroll run cannot be created for a closed pay period.
  - Numbers & thresholds: -20102 (error code).
  - Security & error handling: RAISE_APPLICATION_ERROR(-20102, 'Cannot create run for closed period: ' || p_period_id).
  - Data in/out: Inputs — p_period_id, p_run_type (default 'REGULAR'), p_user. Output — inserts PAYROLL_RUNS row; returns new RUN_ID.

  **PROCEDURE calculate_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L303-387]
  - What it does: Looks up PERIOD_ID/RUN_TYPE for the run; sets STATUS='CALCULATING' and commits [L318-324]. Loops (row-by-row cursor) over EMPLOYEES with EMPLOYMENT_STATUS='ACTIVE' and ACTIVE_FLAG='Y', ordered by EMP_ID, calling calculate_employee_pay per employee; on a per-employee exception, increments an error counter and inserts an ERROR-status PAYROLL_DETAILS row with SQLERRM, then continues [L330-354]. Commits every 50 employees [L359-361]. Afterward updates PAYROLL_RUNS with STATUS ('ERROR' if any employee error occurred else 'CALCULATED'), EMPLOYEE_COUNT, ERROR_COUNT, and TOTAL_GROSS/TOTAL_DEDUCTIONS/TOTAL_NET aggregates, then commits [L370-386].
  - Business rules: Only EMPLOYMENT_STATUS='ACTIVE', ACTIVE_FLAG='Y' employees are processed. A single employee failure doesn't abort the run — logged and processing continues. The run is marked 'ERROR' if any employee-level error occurred, else 'CALCULATED'. TOTAL_GROSS sums EARNING-type lines; TOTAL_DEDUCTIONS sums absolute DEDUCTION/TAX line amounts; TOTAL_NET sums EARNING amounts minus absolute DEDUCTION/TAX amounts; all three exclude ERROR-status lines.
  - Numbers & thresholds: Commit batch size = 50 (MOD(v_emp_count, 50) = 0). Error-row insert uses ELEMENT_ID = 0, ELEMENT_TYPE='ERROR', AMOUNT = 0. SQLERRM truncated via SUBSTR(SQLERRM, 1, 4000).
  - Security & error handling: Per-employee EXCEPTION WHEN OTHERS catches and logs into PAYROLL_DETAILS without stopping the loop (row-by-row cursor, not bulk — noted as a refactor candidate). Partial commits every 50 employees mean a mid-run failure leaves payroll half-calculated (flagged in source as an issue).
  - Data in/out: Inputs — p_run_id, p_user. Output — updates PAYROLL_RUNS status/counts/totals; inserts error rows into PAYROLL_DETAILS; multiple COMMITs.

  **PROCEDURE calculate_employee_pay(p_run_id NUMBER, p_emp_id NUMBER, p_period_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L393-620]
  - What it does: Reads the period's dates/frequency; derives periods-per-year; gets the employee's annual salary as of period end via get_salary_as_of — errors if none found; computes period gross = ROUND(annual_salary / periods_per_year, 2) and inserts it as an EARNING line (ELEMENT_ID=1); gets YTD gross via get_ytd_earnings; looks up EMPLOYEE_TAX_INFO for the tax year (defaults if no W-4 on file); computes and conditionally inserts federal tax (ELEMENT_ID=100), state tax (ELEMENT_ID=101, only if a state code exists), FICA/SS tax (ELEMENT_ID=102), and Medicare tax (ELEMENT_ID=103); loops active EMPLOYEE_PAY_ELEMENTS/PAY_ELEMENTS of type DEDUCTION/BENEFIT in effect for the period (ordered by PRIORITY_ORDER), computing each amount and inserting a line if it's greater than 0. On any unhandled exception, logs via PKG_COMMON.log_error and re-raises.
  - Business rules: Periods-per-year: WEEKLY=52, BIWEEKLY=26, SEMIMONTHLY=24, MONTHLY=12, else 12. Employee must have an active salary as of period end (else error -20104). No W-4 on file defaults to filing status SINGLE, 0 federal allowances, NULL state code, 0 state allowances, 0 additional federal withholding. Federal/state/SS/Medicare tax lines are written only when the computed amount is greater than 0. State tax is only computed when a state code exists. Deduction/benefit elements apply only if ACTIVE_FLAG='Y', EFFECTIVE_DATE <= period end, and (END_DATE IS NULL OR END_DATE >= period start); applied in PRIORITY_ORDER. Override amount beats FLAT/PERCENTAGE calculation; FLAT uses employee AMOUNT else DEFAULT_AMOUNT; PERCENTAGE uses employee PERCENTAGE else DEFAULT_PERCENTAGE applied to period gross / 100; only positive deduction amounts are recorded.
  - Numbers & thresholds: Periods per year — WEEKLY=52, BIWEEKLY=26, SEMIMONTHLY=24, MONTHLY=12, default=12. -20104 (error code, no active salary record). ELEMENT_ID constants: 1=gross EARNING, 100=federal TAX, 101=state TAX, 102=SS TAX, 103=Medicare TAX. Percentage-deduction divisor = 100. All monetary values rounded via ROUND(...,2).
  - Security & error handling: RAISE_APPLICATION_ERROR(-20104, 'No active salary record for employee ' || p_emp_id) when v_annual_salary = 0. Inner EXCEPTION WHEN NO_DATA_FOUND on the tax-info lookup falls back to SINGLE/0/NULL/0/0 defaults instead of failing. Outer EXCEPTION WHEN OTHERS logs 'EMP_ID=' || p_emp_id || ': ' || SQLERRM via PKG_COMMON.log_error, then RAISE re-propagates (caught by calculate_payroll's per-employee handler).
  - Data in/out: Inputs — p_run_id, p_emp_id, p_period_id, p_user. Output — inserts multiple PAYROLL_DETAILS rows (gross earning, federal/state/SS/Medicare tax, deductions/benefits); reads PAY_PERIODS, EMPLOYEE_TAX_INFO, EMPLOYEE_PAY_ELEMENTS, PAY_ELEMENTS; calls get_salary_as_of and get_ytd_earnings.

  **PROCEDURE approve_payroll(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L625-651]
  - What it does: Locks and reads the run's STATUS (SELECT ... FOR UPDATE); if not 'CALCULATED' raises an error; otherwise updates STATUS to 'APPROVED' with APPROVED_BY/APPROVED_DATE and MODIFIED_BY/MODIFIED_DATE.
  - Business rules: Only a run in CALCULATED status can be approved.
  - Numbers & thresholds: -20103 (error code).
  - Security & error handling: RAISE_APPLICATION_ERROR(-20103, 'Cannot approve run in status: ' || v_status); row locked via FOR UPDATE.
  - Data in/out: Inputs — p_run_id, p_user. Output — updates PAYROLL_RUNS (STATUS, APPROVED_BY, APPROVED_DATE, MODIFIED_BY, MODIFIED_DATE).

  **PROCEDURE reverse_payroll(p_run_id NUMBER, p_reason VARCHAR2, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L656-673]
  - What it does: Updates PAYROLL_RUNS STATUS to 'REVERSED'; updates all PAYROLL_DETAILS rows for the run to STATUS='REVERSED'; logs the update via PKG_AUDIT.log_action.
  - Business rules: p_reason is accepted as a parameter but not persisted to any column in this procedure.
  - Numbers & thresholds: None.
  - Security & error handling: None — no status-transition validation (a run in any status can be reversed) and no explicit exception handling or COMMIT in this procedure.
  - Data in/out: Inputs — p_run_id, p_reason, p_user. Output — updates PAYROLL_RUNS and PAYROLL_DETAILS; writes an audit log entry.

  **FUNCTION calculate_federal_tax(p_taxable_income NUMBER, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_additional_wh NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER** [SOURCE: L680-774]
  - What it does: Maps pay frequency to periods-per-year; annualizes the per-period income; subtracts the standard deduction (MARRIED_JOINT gets the married deduction, all else get the single deduction) and allowances × per-allowance amount; if the result is <= 0 returns 0; otherwise applies the 2024 progressive bracket table for SINGLE/MARRIED_SEPARATE or for MARRIED_JOINT (tables below), converts back to a per-period amount, and adds any additional flat withholding.
  - Business rules: MARRIED_JOINT filers use the married standard deduction; all other statuses use the single standard deduction. Each allowance reduces annualized taxable income by the per-allowance amount. Non-positive taxable income after deductions/allowances results in zero tax. Brackets differ by filing status; hardcoded 2024 values (source TODO notes these should instead be read from a TAX_BRACKETS table).
  - Numbers & thresholds:
    Periods per year: WEEKLY=52, BIWEEKLY=26, SEMIMONTHLY=24, MONTHLY=12, else 12.
    Standard deduction: single/other = 14600; MARRIED_JOINT = 29200.
    Per-allowance reduction: 4300.
    2024 SINGLE / MARRIED_SEPARATE bracket table (annualized taxable income):
    | Taxable income up to | Rate | Base tax added |
    |---|---|---|
    | 11600 | 10% | 0 |
    | 47150 | 12% | 1160 |
    | 100525 | 22% | 5426 |
    | 191950 | 24% | 17168.50 |
    | 243725 | 32% | 39110.50 |
    | 609350 | 35% | 55678.50 |
    | above 609350 | 37% | 183647.25 |
    2024 MARRIED_JOINT bracket table (annualized taxable income):
    | Taxable income up to | Rate | Base tax added |
    |---|---|---|
    | 23200 | 10% | 0 |
    | 94300 | 12% | 2320 |
    | 201050 | 22% | 10852 |
    | 383900 | 24% | 34337 |
    | 487450 | 32% | 78221 |
    | 731200 | 35% | 111357 |
    | above 731200 | 37% | 196669.50 |
    Final per-period tax = ROUND(v_tax / v_periods, 2), then + NVL(p_additional_wh, 0).
  - Security & error handling: None — no validation of p_filing_status; a status matching neither IF/ELSIF branch (i.e. not SINGLE/MARRIED_SEPARATE/MARRIED_JOINT) leaves v_tax at its initialized 0.
  - Data in/out: Inputs — p_taxable_income, p_filing_status, p_allowances (default 0), p_additional_wh (default 0), p_pay_frequency (default 'MONTHLY'). Output — returns computed per-period federal tax as NUMBER.

  **FUNCTION calculate_state_tax(p_taxable_income NUMBER, p_state_code VARCHAR2, p_filing_status VARCHAR2, p_allowances NUMBER DEFAULT 0, p_pay_frequency VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER** [SOURCE: L781-811]
  - What it does: Looks up a flat withholding rate by state code and returns taxable income × rate, rounded to 2 decimals. p_filing_status, p_allowances, and p_pay_frequency are accepted but unused in the calculation.
  - Business rules: TX, FL, and WA have no state income tax. Unrecognized/other state codes default to a flat 5% rate. Simplified flat-rate model (source comment notes real implementation would be bracket-based per state).
  - Numbers & thresholds: State flat rates — CA 0.0725 (7.25%), NY 0.0685 (6.85%), TX 0 (0%), FL 0 (0%), WA 0 (0%), IL 0.0495 (4.95%), PA 0.0307 (3.07%), OH 0.04 (4.00%), NJ 0.0637 (6.37%), MA 0.05 (5.00%), unknown/default state 0.05 (5.00%).
  - Security & error handling: None — no validation of p_state_code beyond the CASE ELSE fallback.
  - Data in/out: Inputs — p_taxable_income, p_state_code, p_filing_status (unused), p_allowances (unused, default 0), p_pay_frequency (unused, default 'MONTHLY'). Output — returns ROUND(p_taxable_income * v_rate, 2).

  **FUNCTION calculate_fica(p_gross_pay NUMBER, p_ytd_gross NUMBER) RETURN NUMBER** [SOURCE: L816-834]
  - What it does: If YTD gross already meets/exceeds the Social Security wage base, returns 0. Otherwise taxes only the portion of gross pay that brings YTD up to (not over) the wage base — v_taxable = LEAST(p_gross_pay, c_ss_wage_base_2024 - p_ytd_gross) — and returns v_taxable × c_ss_rate, rounded to 2 decimals.
  - Business rules: Social Security tax stops once YTD earnings reach the annual wage base; a period straddling the cap is only partially taxed.
  - Numbers & thresholds: 2024 SS wage base c_ss_wage_base_2024 = 168600. Employee SS rate c_ss_rate = 0.062 (6.2%).
  - Security & error handling: None.
  - Data in/out: Inputs — p_gross_pay, p_ytd_gross. Output — returns computed SS tax as NUMBER (0 if wage base already exceeded).

  **FUNCTION calculate_medicare(p_gross_pay NUMBER, p_ytd_gross NUMBER) RETURN NUMBER** [SOURCE: L839-865]
  - What it does: Computes base Medicare tax = p_gross_pay × c_medicare_rate. If (p_ytd_gross + p_gross_pay) exceeds c_medicare_addl_threshold, computes an additional surtax: if p_ytd_gross alone already exceeds the threshold, the surtax applies to the full period gross; otherwise it applies only to the portion of (YTD + gross) exceeding the threshold. Returns base + additional tax.
  - Business rules: Standard Medicare tax has no wage cap. The additional 0.9% surtax applies once cumulative YTD+current earnings exceed the threshold; only the excess over the threshold is surtaxed when the threshold is crossed mid-period, otherwise the whole period gross is surtaxed once YTD alone already exceeds it.
  - Numbers & thresholds: Standard Medicare rate c_medicare_rate = 0.0145 (1.45%). Additional Medicare rate c_medicare_addl_rate = 0.009 (0.9%). Additional Medicare threshold c_medicare_addl_threshold = 200000.
  - Security & error handling: None.
  - Data in/out: Inputs — p_gross_pay, p_ytd_gross. Output — returns v_base_tax + v_addl_tax as NUMBER, both components ROUND(...,2).

  **PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id NUMBER, p_emp_id NUMBER DEFAULT NULL)** [SOURCE: L870-906]
  - What it does: Opens a REF CURSOR selecting, per employee (optionally filtered to one), employee number/name, pay period name, gross pay (sum of EARNING lines), total deductions (sum of absolute DEDUCTION/TAX/BENEFIT lines), net pay (sum of all line amounts), and federal/state/SS/Medicare tax amounts (via ELEMENT_ID 100/101/102/103), plus placeholder YTD_GROSS/YTD_NET columns, for the given run, excluding ERROR-status lines, grouped by employee/period, ordered by last name.
  - Business rules: Payslip excludes PAYROLL_DETAILS lines in ERROR status. Scoped to one employee via p_emp_id, or all employees on the run when p_emp_id is NULL.
  - Numbers & thresholds: ELEMENT_ID lookups: 100=federal tax, 101=state tax, 102=Social Security, 103=Medicare. YTD_GROSS and YTD_NET are hardcoded placeholder value 0.
  - Security & error handling: None.
  - Data in/out: Inputs — p_run_id, p_emp_id (optional filter). Output — p_cursor OUT REF CURSOR opened over PAYROLL_DETAILS/EMPLOYEES/PAYROLL_RUNS/PAY_PERIODS.

  **FUNCTION get_ytd_earnings(p_emp_id NUMBER, p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER** [SOURCE: L911-931]
  - What it does: Sums PAYROLL_DETAILS.AMOUNT for the employee where ELEMENT_TYPE='EARNING', STATUS='CALCULATED', and the joined period's PERIOD_START_DATE year matches p_tax_year.
  - Business rules: Only CALCULATED (not ERROR or REVERSED) EARNING lines count toward YTD; year is determined by the pay period's start date.
  - Numbers & thresholds: None beyond the tax-year filter (defaults to current calendar year).
  - Security & error handling: None; NVL(SUM(...),0) guarantees a numeric result with no rows.
  - Data in/out: Inputs — p_emp_id, p_tax_year (default current year). Output — returns summed YTD earnings as NUMBER.

  **PROCEDURE generate_pay_register(p_run_id NUMBER, p_user VARCHAR2 DEFAULT USER)** [SOURCE: L938-1008]
  - What it does: Looks up the run's period name; builds filename 'PAY_REGISTER_' || p_run_id || '_' || <timestamp> || '.csv'; opens the file via UTL_FILE.FOPEN against directory object 'PAYROLL_OUTPUT' for write with max line size 32767; writes a CSV header; loops per-employee/department aggregated totals (gross, federal, state, SS, Medicare, deductions, net) for the run excluding ERROR-status lines, writing one formatted CSV line per employee; closes the file; prints a confirmation via DBMS_OUTPUT.PUT_LINE. On exception, closes the file if open, logs via PKG_COMMON.log_error, and re-raises.
  - Business rules: Pay register excludes PAYROLL_DETAILS lines in ERROR status; one row per employee per department.
  - Numbers & thresholds: UTL_FILE.FOPEN max line size = 32767. Filename timestamp format 'YYYYMMDD_HH24MISS'. Amount format mask 'FM999999990.00'.
  - Security & error handling: Writes to OS-level directory object 'PAYROLL_OUTPUT' (external file I/O, access controlled by the DB directory grant, not validated here). EXCEPTION WHEN OTHERS: closes the file handle if UTL_FILE.IS_OPEN, logs SQLERRM via PKG_COMMON.log_error, then RAISE re-propagates.
  - Data in/out: Inputs — p_run_id, p_user. Output — writes a CSV file to the PAYROLL_OUTPUT directory (external side effect); no DML.

**DEPENDENCIES:**
  Data touched:
  - Reads: SALARY_RECORDS — current/point-in-time salary lookups (get_current_salary, get_salary_as_of)
  - Reads: PAY_PERIODS — period dates/frequency/status lookups (close_pay_period, get_current_period, create_payroll_run, calculate_employee_pay, get_payslip, generate_pay_register)
  - Reads: PAYROLL_RUNS — run status/period lookups (calculate_payroll, approve_payroll, generate_pay_register)
  - Reads: EMPLOYEES — active employee list and names (calculate_payroll, get_payslip, generate_pay_register)
  - Reads: PAYROLL_DETAILS — aggregation for run totals/payslip/register/YTD (calculate_payroll, get_payslip, get_ytd_earnings, generate_pay_register)
  - Reads: EMPLOYEE_TAX_INFO — W-4 filing status/allowances/state code (calculate_employee_pay)
  - Reads: EMPLOYEE_PAY_ELEMENTS — employee-specific deduction/benefit assignments (calculate_employee_pay)
  - Reads: PAY_ELEMENTS — deduction/benefit element definitions (calculate_employee_pay)
  - Reads: DEPARTMENTS — department name for pay register (generate_pay_register)
  - Writes: SALARY_RECORDS — end-date prior record, insert new record (create_salary_record)
  - Writes: PAY_PERIODS — insert new periods, update status to CLOSED (create_pay_periods, close_pay_period)
  - Writes: PAYROLL_RUNS — insert new run, update status/totals/approval/reversal (create_payroll_run, calculate_payroll, approve_payroll, reverse_payroll)
  - Writes: PAYROLL_DETAILS — insert earning/tax/deduction/error lines, update lines to REVERSED (calculate_payroll, calculate_employee_pay, reverse_payroll)

  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L69
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L672
  CALLS: calculate_employee_pay | EVIDENCE: OBSERVED | SOURCE: L338
  CALLS: get_salary_as_of | EVIDENCE: OBSERVED | SOURCE: L437
  CALLS: get_ytd_earnings | EVIDENCE: OBSERVED | SOURCE: L460
  CALLS: calculate_federal_tax | EVIDENCE: OBSERVED | SOURCE: L488
  CALLS: calculate_state_tax | EVIDENCE: OBSERVED | SOURCE: L509
  CALLS: calculate_fica | EVIDENCE: OBSERVED | SOURCE: L528
  CALLS: calculate_medicare | EVIDENCE: OBSERVED | SOURCE: L545
  CALLS: PKG_COMMON.log_error | EVIDENCE: OBSERVED | SOURCE: L617
  CALLS: PKG_COMMON.log_error | EVIDENCE: OBSERVED | SOURCE: L1006
  CALLS: UTL_FILE.FOPEN | EVIDENCE: OBSERVED | SOURCE: L954
  CALLS: UTL_FILE.PUT_LINE | EVIDENCE: OBSERVED | SOURCE: L957
  CALLS: UTL_FILE.FCLOSE | EVIDENCE: OBSERVED | SOURCE: L997
  CALLS: UTL_FILE.IS_OPEN | EVIDENCE: OBSERVED | SOURCE: L1003
  CALLS: DBMS_OUTPUT.PUT_LINE | EVIDENCE: OBSERVED | SOURCE: L999

  Config/env: PAYROLL_OUTPUT — Oracle directory object referenced by UTL_FILE.FOPEN [L954] for CSV pay-register output.
  External integrations: UTL_FILE (OS file-system I/O via DB directory object), DBMS_OUTPUT (session console output), sequences SEQ_SALARY, SEQ_PAY_PERIOD, SEQ_PAYROLL_RUN, SEQ_PAYROLL_DETAIL.

**GAPS:**
  t_payslip_cursor type is used as an OUT parameter type in get_payslip but not declared in this file — presumably declared in the package spec (PKG_PAYROLL.pks) — UNKNOWN/EXTERNAL.
  PKG_AUDIT.log_action and PKG_COMMON.log_error implementations are external to this file — EXTERNAL.
  p_reason parameter in reverse_payroll is accepted but never written to any column — UNRESOLVED whether this is intentional or a latent bug.
  A TAX_BRACKETS table is referenced only in a source comment/TODO as a future data-driven replacement for the hardcoded federal brackets; it is not read anywhere in this file — NOT_ANALYZED.

*[pipeline status — type: plsql-body · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 000, 01, 050, 11, 150, 168, 191, 20, 200, 201, 23, 243, 29, 30, 300]*

---

=== CHUNK STATUS ===
Files expected: 1
Files delivered: 1
  Full coverage on first pass: 0
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb
  Still incomplete after max attempts: 1 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb
Raw source: 46030 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===