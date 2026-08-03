# DA Agent 2 — Data Architecture Review Report
**System:** HRMS (Oracle 19c, schema HRMS)
**Source:** ts-plsql-oracle-forms-hrms-main
**Review date:** 2026-08-03
**Reviewer:** DA Agent 2 v2 (June 2026)

---

## Review Header

**Files reviewed:** 13 of 13 da-outputs/ files (both passes combined)

**Pass 1 — Package bodies (prior session):**
Package bodies read: PKG_EMPLOYEE.pkb, PKG_PAYROLL.pkb, PKG_LEAVE.pkb, PKG_INTEGRATION.pkb, PKG_NOTIFICATION.pkb, PKG_SECURITY.pkb (provided in prompt), README.md
Changes from Pass 1: 6 CORRECTED · 21 ADDED · 6 ENRICHED = 33

**Pass 2 — Full source file validation (this session):**
Files provided: PKG_SECURITY.pkb (full body), PKG_AUDIT.pkb (full body), schema/tables/01-04_*.sql (all 30 tables, full DDL), plsql/triggers/trg_employees.sql, plsql/triggers/trg_audit.sql, schema/views/hrms_views.sql (all 6 views), schema/sequences/hrms_sequences.sql (all 29 sequences)
Files not found in scan: PKG_PAYROLL.pkb, PKG_LEAVE.pkb, PKG_EMPLOYEE.pkb, PKG_INTEGRATION.pkb (covered in Pass 1)
Changes from Pass 2: 3 CORRECTED · 3 ADDED · 2 ENRICHED = 8

**Package bodies still unread:** PKG_REPORTING.pkb, PKG_COMMON.pkb, PKG_VALIDATION.pkb, PKG_PERFORMANCE.pkb
**Test files:** Zero — README.md explicitly states "No unit tests — all testing is manual via Forms" (confirmed technical debt, not a scan gap)
**DB connection:** CODE-ONLY (unchanged — no Oracle client accessible)

**Cumulative change counts: 9 CORRECTED · 24 ADDED · 8 ENRICHED = 41 total changes**

---

## Change Records

---

### RC-001 — CORRECTED

```json
{
  "change_id": "RC-001",
  "type": "CORRECTED",
  "finding_id": "data-quality-report.md — Audit action value violates check constraint",
  "what": "Agent 1 said 'every leave-status change will raise ORA-02290'. CORRECTED: PKG_AUDIT.log_action is PRAGMA AUTONOMOUS_TRANSACTION with EXCEPTION WHEN OTHERS → ROLLBACK (documented rule: 'audit logging must never fail the calling transaction'). The ORA-02290 is caught and silently swallowed. Leave operations SUCCEED; the audit write fails silently. This is a compliance gap (leave status changes are unaudited in AUDIT_LOG), not an operational blocker.",
  "evidence_source": "PKG_AUDIT.pkb body reading",
  "evidence_detail": "PKG_AUDIT.pkb: PRAGMA AUTONOMOUS_TRANSACTION + EXCEPTION WHEN OTHERS: ROLLBACK in log_action; TRG_LEAVE_REQUEST_AUDIT: calls log_action(..., 'STATUS_CHANGE', ...); CHK_AUDIT_ACTION: only INSERT/UPDATE/DELETE permitted",
  "confidence_before": 0.75,
  "confidence_after": 0.95,
  "phase_found": "Phase 2 — package body reading",
  "severity_delta": "Reduced from LAUNCH-BLOCKING to COMPLIANCE GAP — leave approval still works"
}
```

---

### RC-002 — CORRECTED

```json
{
  "change_id": "RC-002",
  "type": "CORRECTED",
  "finding_id": "migration-complexity.json + redundancy-analysis.json — TAX_BRACKETS usage",
  "what": "Agent 1 said TAX_BRACKETS is 'presumably read by PKG_PAYROLL's tax calculation'. CORRECTED: PKG_PAYROLL.pkb hard-codes 2024 federal tax brackets directly in calculate_federal_tax. Code comment explicitly says 'TODO: Read from TAX_BRACKETS table instead of hard-coding'. TAX_BRACKETS table is NEVER read by PKG_PAYROLL — it is currently unused/empty in practice. The full hard-coded bracket structure is now extracted (see A-002).",
  "evidence_source": "PKG_PAYROLL.pkb body reading",
  "evidence_detail": "PKG_PAYROLL.pkb lines 643-676 (Single/Married_Separate brackets) and 661-677 (Married_Joint brackets) — full hard-coded CASE block with TODO comment",
  "confidence_before": 0.6,
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### RC-003 — CORRECTED

```json
{
  "change_id": "RC-003",
  "type": "CORRECTED",
  "finding_id": "data-flow-map.md + data-source-inventory.json — batch job scheduler status",
  "what": "Agent 1 marked leave accrual batch scheduler as UNKNOWN. CORRECTED: PKG_LEAVE.pkb documents 'Typically scheduled via DBMS_SCHEDULER on the 1st of each month'. PKG_NOTIFICATION.pkb documents 'Called by DBMS_SCHEDULER job every 5 minutes'. Both scheduler jobs are confirmed to exist, though neither .sql scheduler job definition was found in the scanned repo (they may reside in a DBA-managed script not checked into source control).",
  "evidence_source": "PKG_LEAVE.pkb run_monthly_accrual header comment; PKG_NOTIFICATION.pkb process_queue header comment",
  "evidence_detail": "PKG_LEAVE.pkb: '-- Typically scheduled via DBMS_SCHEDULER on the 1st of each month'; PKG_NOTIFICATION.pkb: '-- Called by DBMS_SCHEDULER job every 5 minutes'",
  "confidence_before": 0.5,
  "confidence_after": 0.85,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### RC-004 — CORRECTED

```json
{
  "change_id": "RC-004",
  "type": "CORRECTED",
  "finding_id": "data-source-inventory.json + storage-pattern-analysis.md — SMTP configuration",
  "what": "Agent 1 said SMTP_HOST and FROM_ADDRESS in SYSTEM_PARAMETERS are the operative email configuration. CORRECTED: PKG_NOTIFICATION.pkb has its own private constants (c_smtp_host = 'smtp.internal.company.com', c_smtp_port = 25, c_from_address = 'hrms-noreply@company.com') hard-coded in the package body, and process_queue uses these constants directly — NOT PKG_COMMON.get_param(). The SYSTEM_PARAMETERS rows for SMTP_HOST/FROM_ADDRESS are therefore decorative/unused by the actual sending code. Values happen to match today, but if SYSTEM_PARAMETERS is updated, the live behavior does not change.",
  "evidence_source": "PKG_NOTIFICATION.pkb body reading",
  "evidence_detail": "PKG_NOTIFICATION.pkb lines 6-9: four private CONSTANT declarations; process_queue uses c_smtp_host and c_from_address directly throughout",
  "confidence_before": 0.75,
  "confidence_after": 0.95,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### RC-005 — CORRECTED

```json
{
  "change_id": "RC-005",
  "type": "CORRECTED",
  "finding_id": "data-quality-report.md — HEAD_OF_HOUSEHOLD filing status",
  "what": "Agent 1 did not document that HEAD_OF_HOUSEHOLD filing status — which is valid in EMPLOYEE_TAX_INFO.FILING_STATUS (CHECK constraint includes it) — produces $0 federal tax. PKG_PAYROLL.calculate_federal_tax only handles 'SINGLE', 'MARRIED_SEPARATE', and 'MARRIED_JOINT' in its CASE block. HEAD_OF_HOUSEHOLD falls through both IF conditions and v_tax remains 0. Any employee who filed W-4 as HEAD_OF_HOUSEHOLD will have $0 federal tax withheld — a potential IRS under-withholding compliance issue.",
  "evidence_source": "PKG_PAYROLL.pkb body reading",
  "evidence_detail": "PKG_PAYROLL.pkb lines 645-677: IF p_filing_status = 'SINGLE' OR p_filing_status = 'MARRIED_SEPARATE' THEN ... ELSIF p_filing_status = 'MARRIED_JOINT' THEN ... (no ELSIF/ELSE for HEAD_OF_HOUSEHOLD; v_tax stays 0)",
  "confidence_before": 0.0,
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading",
  "severity": "PAYROLL COMPLIANCE BUG — may cause IRS penalties if any employee has HEAD_OF_HOUSEHOLD filing status"
}
```

---

### RC-006 — CORRECTED

```json
{
  "change_id": "RC-006",
  "type": "CORRECTED",
  "finding_id": "data-quality-report.md + data-dictionary.md — PAYROLL_RUNS.TOTAL_NET and TOTAL_DEDUCTIONS accuracy",
  "what": "Agent 1 did not document that PAYROLL_RUNS.TOTAL_NET and TOTAL_DEDUCTIONS computed in calculate_payroll exclude BENEFIT-type elements. TOTAL_DEDUCTIONS aggregates only ELEMENT_TYPE IN ('DEDUCTION','TAX'); TOTAL_NET uses ELSE 0 for any ELEMENT_TYPE not in ('EARNING','DEDUCTION','TAX'). BENEFIT deductions (MED_EE=$250, DENTAL_EE=$45, VISION_EE=$15, LIFE_INS=$25) are inserted as negative amounts in PAYROLL_DETAILS but ignored in both PAYROLL_RUNS summary columns. The payslip NET_PAY via get_payslip correctly uses SUM(pd.AMOUNT) which captures all signed amounts including BENEFIT. Result: PAYROLL_RUNS.TOTAL_NET and TOTAL_DEDUCTIONS overstate take-home/understate deductions by the total BENEFIT cost.",
  "evidence_source": "PKG_PAYROLL.pkb calculate_payroll and calculate_employee_pay",
  "evidence_detail": "PKG_PAYROLL.pkb lines 334-344: TOTAL_DEDUCTIONS WHERE ELEMENT_TYPE IN ('DEDUCTION','TAX'); TOTAL_NET CASE ELSE 0 END for BENEFIT; lines 530-543: BENEFIT amounts inserted as -v_ded_amount",
  "confidence_before": 0.0,
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading",
  "severity": "DATA QUALITY — PAYROLL_RUNS totals are wrong for any employee with BENEFIT deductions"
}
```

---

### A-001 — ADDED

```json
{
  "change_id": "A-001",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json / access-control-matrix.md — SQL injection in employee search",
  "what": "PKG_EMPLOYEE.search_employees builds dynamic SQL by string-concatenating all search parameters (p_last_name, p_first_name, p_dept_id, p_status, p_location_code) without bind variables. Code has an explicit comment: 'VULNERABILITY: String concatenation instead of bind variable'. This is a known SQL injection point. The Forms LOV passes validated values, but any direct call to PKG_EMPLOYEE.search_employees with unvalidated input is exploitable.",
  "evidence_source": "PKG_EMPLOYEE.pkb body reading",
  "evidence_detail": "PKG_EMPLOYEE.pkb lines 466-467: v_sql || 'AND UPPER(e.LAST_NAME) LIKE UPPER(''' || p_last_name || '%'') ' with documented vulnerability comment",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading",
  "severity": "SECURITY DEFECT — SQL injection risk on employee search"
}
```

---

### A-002 — ADDED

```json
{
  "change_id": "A-002",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — Federal tax brackets (hard-coded 2024)",
  "what": "Federal income tax brackets are hard-coded in PKG_PAYROLL.calculate_federal_tax, not read from TAX_BRACKETS table (see RC-002). Full 2024 bracket structure now extracted.\n\nSingle / Married_Separate:\n  ≤ $11,600: 10%\n  $11,601–$47,150: $1,160 + 12% of excess\n  $47,151–$100,525: $5,426 + 22% of excess\n  $100,526–$191,950: $17,168.50 + 24% of excess\n  $191,951–$243,725: $39,110.50 + 32% of excess\n  $243,726–$609,350: $55,678.50 + 35% of excess\n  > $609,350: $183,647.25 + 37% of excess\n\nMarried_Joint:\n  ≤ $23,200: 10%\n  $23,201–$94,300: $2,320 + 12% of excess\n  $94,301–$201,050: $10,852 + 22% of excess\n  $201,051–$383,900: $34,337 + 24% of excess\n  $383,901–$487,450: $78,221 + 32% of excess\n  $487,451–$731,200: $111,357 + 35% of excess\n  > $731,200: $196,669.50 + 37% of excess\n\nCalculation method: annualize period gross, subtract standard deduction and (allowances × $4,300), apply brackets, divide back by periods-per-year, add additional withholding.\nStandard deduction: Single=$14,600; Married_Joint=$29,200.\nPer-allowance reduction: $4,300 each.\nNOTE: pretax deductions (401k, HSA, medical) are NOT subtracted before applying brackets — code comment says 'Simplified; should subtract pretax deductions'.",
  "evidence_source": "PKG_PAYROLL.pkb body reading",
  "evidence_detail": "PKG_PAYROLL.pkb lines 607-686: calculate_federal_tax; constants c_standard_deduction_single=14600, c_standard_deduction_married=29200, c_allowance_amount=4300",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-003 — ADDED

```json
{
  "change_id": "A-003",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — FICA and Medicare rates and thresholds",
  "what": "Hard-coded constants in PKG_PAYROLL.pkb (2024 values):\n  Social Security rate (employee share): 6.2%\n  Social Security wage base: $168,600\n  Medicare base rate (employee share): 1.45%\n  Additional Medicare rate: 0.9%\n  Additional Medicare threshold: $200,000 (YTD gross)\n\nCalculation logic:\n  FICA: MIN(period_gross, $168,600 - ytd_gross) × 6.2%; returns 0 once wage base met\n  Medicare: period_gross × 1.45% base; + (portion of period_gross that pushes YTD above $200,000) × 0.9%",
  "evidence_source": "PKG_PAYROLL.pkb body reading",
  "evidence_detail": "PKG_PAYROLL.pkb lines 3-15: c_ss_wage_base_2024=168600, c_ss_rate=0.062, c_medicare_rate=0.0145, c_medicare_addl_rate=0.009, c_medicare_addl_threshold=200000",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-004 — ADDED

```json
{
  "change_id": "A-004",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — State income tax flat rates (hard-coded)",
  "what": "PKG_PAYROLL.calculate_state_tax uses hard-coded flat rates per state code (documented as 'Simplified; in production, each state would have its own bracket structure'):\n  CA: 7.25%\n  NY: 6.85%\n  TX: 0% (no state income tax)\n  FL: 0% (no state income tax)\n  WA: 0% (no state income tax)\n  IL: 4.95%\n  PA: 3.07%\n  OH: 4.00%\n  NJ: 6.37%\n  MA: 5.00%\n  All other states: 5.00% (default catch-all)\nApplied directly to period taxable income with no annualization or allowance subtraction.",
  "evidence_source": "PKG_PAYROLL.pkb body reading",
  "evidence_detail": "PKG_PAYROLL.pkb lines 693-715: calculate_state_tax CASE block",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-005 — ADDED

```json
{
  "change_id": "A-005",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — Backdated leave request window",
  "what": "PKG_LEAVE.submit_leave_request allows leave requests up to 5 days in the past. Requests with start_date more than 5 calendar days before TRUNC(SYSDATE) are rejected with ORA-20211 'Cannot submit leave requests more than 5 days in the past'. Exact: TRUNC(SYSDATE) - p_start_date > 5.",
  "evidence_source": "PKG_LEAVE.pkb body reading",
  "evidence_detail": "PKG_LEAVE.pkb lines 120-125: IF p_start_date < TRUNC(SYSDATE) THEN IF TRUNC(SYSDATE) - p_start_date > 5 THEN RAISE_APPLICATION_ERROR(-20211, ...)",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-006 — ADDED

```json
{
  "change_id": "A-006",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — Carryover expiry date calculation",
  "what": "LEAVE_TYPES.CARRYOVER_EXPIRY stores a NUMBER of months (not days, not periods). PKG_LEAVE.process_carryover sets CARRYOVER_EXPIRY_DT = ADD_MONTHS(TO_DATE(next_year || '-01-01', 'YYYY-MM-DD'), CARRYOVER_EXPIRY). Concrete example: PTO CARRYOVER_EXPIRY=3 → carryover from year N expires on April 1 of year N+1 (3 months after January 1). expire_carryover removes balances where CARRYOVER_EXPIRY_DT <= TRUNC(SYSDATE).",
  "evidence_source": "PKG_LEAVE.pkb process_carryover",
  "evidence_detail": "PKG_LEAVE.pkb lines 587-593; seed data: PTO CARRYOVER_EXPIRY=3, SICK CARRYOVER_EXPIRY=NULL (never expires)",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-007 — ADDED

```json
{
  "change_id": "A-007",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — Termination auto-cancels pending leave",
  "what": "PKG_EMPLOYEE.terminate_employee automatically cancels all PENDING leave requests for the terminated employee before setting employment status to TERMINATED. Cancel reason set to 'Auto-cancelled due to termination', CANCELLED_DATE = SYSDATE. Does NOT cancel APPROVED (future) leave — only PENDING. Matching LEAVE_BALANCES.PENDING reduction is NOT done here (cancel_leave_request in PKG_LEAVE handles that, but terminate_employee does a direct UPDATE bypassing PKG_LEAVE).",
  "evidence_source": "PKG_EMPLOYEE.pkb terminate_employee",
  "evidence_detail": "PKG_EMPLOYEE.pkb lines 667-683: SELECT COUNT(*) pending leave; UPDATE LEAVE_REQUESTS SET STATUS='CANCELLED', CANCEL_REASON='Auto-cancelled due to termination' WHERE STATUS='PENDING'",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading",
  "secondary_finding": "PENDING balance for cancelled-at-termination requests is NOT decremented (terminate_employee does not call PKG_LEAVE.cancel_leave_request or adjust LEAVE_BALANCES.PENDING). If LEAVE_BALANCES rows exist, PENDING column will remain overstated after termination."
}
```

---

### A-008 — ADDED

```json
{
  "change_id": "A-008",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — Rehire overwrites original hire date",
  "what": "PKG_EMPLOYEE.rehire_employee sets HIRE_DATE = p_rehire_date and also sets TERMINATION_DATE = NULL and TERMINATION_REASON = NULL. This means the original hire date is permanently overwritten with the rehire date. Any tenure/seniority calculation after rehire (VW_ACTIVE_EMPLOYEES.TENURE_YEARS, PKG_EMPLOYEE.get_tenure_years, MIN_TENURE_DAYS leave eligibility check) uses only the rehire date as the baseline — original seniority is lost from the data model unless preserved in EMPLOYEE_HISTORY.",
  "evidence_source": "PKG_EMPLOYEE.pkb rehire_employee",
  "evidence_detail": "PKG_EMPLOYEE.pkb lines 760-771: HIRE_DATE = p_rehire_date, TERMINATION_DATE = NULL, TERMINATION_REASON = NULL in UPDATE EMPLOYEES",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-009 — ADDED

```json
{
  "change_id": "A-009",
  "type": "ADDED",
  "finding_id": "pii-inventory.json + access-control-matrix.md — PII export via benefits flat file bypasses has_permission",
  "what": "PKG_INTEGRATION.export_benefits_feed writes employee and dependent PII to a flat file without any PKG_SECURITY.has_permission check: EMP_NUMBER, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, HIRE_DATE, EMPLOYMENT_STATUS, MARITAL_STATUS, GENDER, and all EMPLOYEE_DEPENDENTS PII (DEP first/last name, RELATIONSHIP, DEP DOB) are exported in plaintext fixed-width ADP format to Oracle directory 'BENEFITS_FEED_OUT'. This represents an uncontrolled PII export path outside the module-level access model. Anyone with EXECUTE privilege on PKG_INTEGRATION can call export_benefits_feed and obtain the entire active employee roster with dependents.",
  "evidence_source": "PKG_INTEGRATION.pkb export_benefits_feed",
  "evidence_detail": "PKG_INTEGRATION.pkb lines 93-147: SELECT from EMPLOYEES LEFT JOIN EMPLOYEE_DEPENDENTS; no has_permission call; writes plaintext fixed-width file",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading",
  "severity": "PII / COMPLIANCE — uncontrolled bulk PII export"
}
```

---

### A-010 — ADDED

```json
{
  "change_id": "A-010",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — Manager circular chain depth limit",
  "what": "PKG_EMPLOYEE.validate_manager checks for circular reporting chains by traversing MANAGER_EMP_ID links upward. c_max_hierarchy_depth = 15. If the chain exceeds 15 levels, the loop exits WITHOUT raising an error — the circular chain check silently passes. Org hierarchies deeper than 15 levels can have circular references inserted without detection.",
  "evidence_source": "PKG_EMPLOYEE.pkb validate_manager",
  "evidence_detail": "PKG_EMPLOYEE.pkb line 6: c_max_hierarchy_depth CONSTANT NUMBER := 15; line 111: WHILE v_current_mgr IS NOT NULL AND v_depth < c_max_hierarchy_depth LOOP",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-011 — ADDED

```json
{
  "change_id": "A-011",
  "type": "ADDED",
  "finding_id": "data-source-inventory.json — GL feed integration protocol confirmed",
  "what": "PKG_INTEGRATION.generate_gl_journal writes a pipe-delimited flat file to Oracle directory object 'GL_FEED_OUT', consumed by Oracle Financials batch import. File format: H (header) | D (detail) | T (trailer) records. Debit records use EARNING element type; credit records use all other types. Grouped by COST_CENTER and GL_ACCOUNT_CODE. File naming: GL_JOURNAL_{run_id}_{YYYYMMDD}.dat. Called after payroll APPROVED — SYSTEM_PARAMETERS GL_FEED_STATUS='ACTIVE' check is done via PKG_COMMON.get_param (not hard-coded).",
  "evidence_source": "PKG_INTEGRATION.pkb generate_gl_journal",
  "evidence_detail": "PKG_INTEGRATION.pkb lines 16-83; c_gl_output_dir = 'GL_FEED_OUT'",
  "confidence_after": 0.9,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-012 — ADDED

```json
{
  "change_id": "A-012",
  "type": "ADDED",
  "finding_id": "data-source-inventory.json — Benefits feed integration protocol confirmed",
  "what": "PKG_INTEGRATION.export_benefits_feed writes fixed-width format ADP benefits file to Oracle directory 'BENEFITS_FEED_OUT'. Record layout: EmpNum(10) | FName(30) | LName(30) | DOB(10) | HireDate(10) | Status(12) | MaritalStatus(10) | Gender(1) | DepFName(30) | DepLName(30) | Relationship(20) | DepDOB(10). One row per EMPLOYEE × DEPENDENT pairing (employees with no dependents still appear with blank dependent fields). Date format: YYYY-MM-DD. File naming: BENEFITS_{YYYYMMDD}.txt.",
  "evidence_source": "PKG_INTEGRATION.pkb export_benefits_feed",
  "evidence_detail": "PKG_INTEGRATION.pkb lines 86-147",
  "confidence_after": 0.9,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-013 — ADDED

```json
{
  "change_id": "A-013",
  "type": "ADDED",
  "finding_id": "data-source-inventory.json — Time/attendance import is a stub",
  "what": "PKG_INTEGRATION.import_time_attendance reads a CSV from Oracle directory 'TIME_ATTENDANCE_IN' but contains a TODO stub — it reads lines and increments a counter but never parses the CSV or updates any database table. Format comment says 'emp_number,date,hours_regular,hours_overtime'. This integration is not functional.",
  "evidence_source": "PKG_INTEGRATION.pkb import_time_attendance",
  "evidence_detail": "PKG_INTEGRATION.pkb lines 152-194: -- TODO: Implement actual parsing and database update",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-014 — ADDED

```json
{
  "change_id": "A-014",
  "type": "ADDED",
  "finding_id": "data-source-inventory.json — LDAP/AD sync is a stub placeholder",
  "what": "PKG_INTEGRATION.sync_org_structure contains a single log_info call ('Org structure sync completed') with no actual LDAP/AD connectivity. This procedure is a named placeholder only — no sync occurs when called.",
  "evidence_source": "PKG_INTEGRATION.pkb sync_org_structure",
  "evidence_detail": "PKG_INTEGRATION.pkb lines 196-203",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-015 — ADDED

```json
{
  "change_id": "A-015",
  "type": "ADDED",
  "finding_id": "data-dictionary.md + hidden-business-rules.json — Employee names stored uppercase",
  "what": "PKG_EMPLOYEE.create_employee stores FIRST_NAME and LAST_NAME as UPPER(TRIM(p_first_name)) and UPPER(TRIM(p_last_name)). update_employee applies the same transform for any non-NULL name update. Views (VW_ACTIVE_EMPLOYEES) use first/last name directly (no INITCAP applied at storage, but PKG_COMMON.format_name applies INITCAP at display time). Seed data also uses uppercase names. This is a confirmed data storage normalization rule, not a display transform.",
  "evidence_source": "PKG_EMPLOYEE.pkb create_employee, update_employee; seed/02_employee_data.sql",
  "evidence_detail": "PKG_EMPLOYEE.pkb line 263: UPPER(TRIM(p_first_name)); line 369: NVL(UPPER(TRIM(p_first_name)), FIRST_NAME)",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-016 — ADDED

```json
{
  "change_id": "A-016",
  "type": "ADDED",
  "finding_id": "data-quality-report.md — expire_carryover double-subtract bug",
  "what": "PKG_LEAVE.expire_carryover contains a self-documented bug: 'If run twice on same day, can double-subtract'. The UPDATE subtracts CARRYOVER_FROM_PREV from ADJUSTMENT and sets CARRYOVER_FROM_PREV = 0 in the same statement. However, if called again before CARRYOVER_FROM_PREV = 0 is committed (or if run as part of a batch that re-runs on failure), the subtraction can be applied twice. No idempotency guard exists.",
  "evidence_source": "PKG_LEAVE.pkb expire_carryover",
  "evidence_detail": "PKG_LEAVE.pkb lines 612-622: -- BUG: If run twice on same day, can double-subtract",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-017 — ADDED

```json
{
  "change_id": "A-017",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — AVAILABLE formula fork occurs in THREE places, not two",
  "what": "Agent 1 documented the AVAILABLE formula fork as a two-way discrepancy (virtual column vs. VW_LEAVE_SUMMARY). A third instance now found: PKG_LEAVE.process_carryover computes remaining balance for carryover as OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT (4 terms, no PENDING subtraction) — identical to VW_LEAVE_SUMMARY's formula. Summary: LEAVE_BALANCES.AVAILABLE virtual column and PKG_LEAVE.get_leave_balance use the 5-term formula (correct, subtracts PENDING); VW_LEAVE_SUMMARY and process_carryover both use the 4-term formula (overstates by PENDING amount). Carryover amounts are therefore potentially inflated if an employee has pending leave at year-end.",
  "evidence_source": "PKG_LEAVE.pkb process_carryover",
  "evidence_detail": "PKG_LEAVE.pkb lines 566-570: OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT AS REMAINING (no PENDING); compare with get_leave_balance line 376: OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-018 — ADDED

```json
{
  "change_id": "A-018",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — Leave requests with NULL manager become permanently stuck PENDING",
  "what": "PKG_LEAVE.submit_leave_request sets APPROVER_EMP_ID = v_emp_rec.MANAGER_EMP_ID. For employees with MANAGER_EMP_ID IS NULL (e.g., the CEO, EMP_ID=1), APPROVER_EMP_ID will be NULL in LEAVE_REQUESTS. VW_PENDING_APPROVALS filters by APPROVER_EMP_ID, so NULL-approver requests never surface in any approver's queue. The request will sit in PENDING status indefinitely unless an HR administrator explicitly updates it. No warning or error is raised at submission time.",
  "evidence_source": "PKG_LEAVE.pkb submit_leave_request; schema/views/hrms_views.sql VW_PENDING_APPROVALS",
  "evidence_detail": "PKG_LEAVE.pkb line 160: v_manager_id := v_emp_rec.MANAGER_EMP_ID (NULL for top-level employees); VW_PENDING_APPROVALS: WHERE lr.APPROVER_EMP_ID = ... (NULL never equals anything)",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-019 — ADDED

```json
{
  "change_id": "A-019",
  "type": "ADDED",
  "finding_id": "data-source-inventory.json — DBMS_SCHEDULER jobs confirmed to exist",
  "what": "Two DBMS_SCHEDULER jobs are confirmed by code comments: (1) PKG_NOTIFICATION.process_queue runs every 5 minutes to dispatch email via UTL_SMTP. (2) PKG_LEAVE.run_monthly_accrual runs on the 1st of each month to post leave accrual. Neither job's CREATE DBMS_SCHEDULER script was found in the scanned repo (likely in DBA maintenance scripts outside source control). Batch size for notification processing: 50 notifications per invocation (p_batch_size default).",
  "evidence_source": "PKG_NOTIFICATION.pkb process_queue header; PKG_LEAVE.pkb run_monthly_accrual header",
  "evidence_detail": "PKG_NOTIFICATION.pkb: '-- Called by DBMS_SCHEDULER job every 5 minutes'; PKG_LEAVE.pkb: '-- Typically scheduled via DBMS_SCHEDULER on the 1st of each month'",
  "confidence_after": 0.85,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### A-020 — ADDED

```json
{
  "change_id": "A-020",
  "type": "ADDED",
  "finding_id": "data-quality-report.md — Payroll partial-commit data integrity risk",
  "what": "PKG_PAYROLL.calculate_payroll commits every 50 employees during the payroll run loop. Code comment explicitly flags this: 'ISSUE: Partial commits mean a failure leaves payroll half-calculated'. If an error occurs on employee 63 (after employee 50's commit), the first 50 employees have PAYROLL_DETAILS rows but the run cannot be cleanly retried without first reversing or deleting those rows. Combined with the row-by-row cursor (documented as 'should be refactored to bulk processing'), large payroll runs have both a correctness risk and a performance problem.",
  "evidence_source": "PKG_PAYROLL.pkb calculate_payroll",
  "evidence_detail": "PKG_PAYROLL.pkb lines 322-326: IF MOD(v_emp_count, 50) = 0 THEN COMMIT; END IF; with ISSUE comment",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading",
  "severity": "DATA INTEGRITY — payroll can be left in a partially-committed state"
}
```

---

### A-021 — ADDED

```json
{
  "change_id": "A-021",
  "type": "ADDED",
  "finding_id": "data-quality-report.md — YTD amounts on payslip are hardcoded to zero",
  "what": "PKG_PAYROLL.get_payslip returns YTD_GROSS=0 and YTD_NET=0 with an explicit 'Placeholder' comment. Payslips produced from this procedure have no year-to-date totals. get_ytd_earnings function exists and works correctly (queries PAYROLL_DETAILS by tax year), but it is not called from get_payslip.",
  "evidence_source": "PKG_PAYROLL.pkb get_payslip",
  "evidence_detail": "PKG_PAYROLL.pkb lines 784-785: 0 AS YTD_GROSS, -- Placeholder; 0 AS YTD_NET -- Placeholder",
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### E-001 — ENRICHED

```json
{
  "change_id": "E-001",
  "type": "ENRICHED",
  "finding_id": "data-quality-report.md + erd.md — EMPLOYEE_HISTORY trigger broken; fix path confirmed",
  "what": "Agent 1 correctly identified TRG_EMP_BEFORE_UPDATE as broken. Reading PKG_EMPLOYEE.pkb now confirms that PKG_EMPLOYEE.log_history uses the CORRECT EMPLOYEE_HISTORY column set (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID/NEW_DEPT_ID, etc.) with PRAGMA AUTONOMOUS_TRANSACTION. This confirms: (a) the trigger is the sole broken component — the package-level history mechanism would work correctly if the trigger did not block the UPDATE first; (b) the fix is specifically to either align TRG_EMP_BEFORE_UPDATE's INSERT column list with the actual DDL, or drop the trigger and rely entirely on PKG_EMPLOYEE.log_history. The package body represents the intended design; the trigger was never updated to match the DDL refactor.",
  "evidence_source": "PKG_EMPLOYEE.pkb log_history",
  "evidence_detail": "PKG_EMPLOYEE.pkb lines 157-169: INSERT INTO EMPLOYEE_HISTORY (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE)",
  "confidence_before": 0.9,
  "confidence_after": 0.97,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### E-002 — ENRICHED

```json
{
  "change_id": "E-002",
  "type": "ENRICHED",
  "finding_id": "data-flow-map.md — Leave accrual batch mechanism confirmed",
  "what": "Agent 1 said leave accrual mechanism was 'unscanned/unconfirmed'. PKG_LEAVE.run_monthly_accrual is now confirmed: iterates all ACTIVE employees, iterates all LEAVE_TYPES where ACCRUAL_FLAG='Y' AND ACCRUAL_FREQUENCY='MONTHLY', checks MIN_TENURE_DAYS and MAX_BALANCE caps, updates LEAVE_BALANCES.ACCRUED, writes LEAVE_ACCRUAL_LOG rows (RUN_ID column is NOT populated — always NULL from this batch path). Also confirms process_carryover (year-end) and expire_carryover (mid-year expiry) as separate procedures. LEAVE_ACCRUAL_LOG.RUN_ID is confirmed as never set — the column is currently unused (see RC-003 correction to soft-ref target).",
  "evidence_source": "PKG_LEAVE.pkb run_monthly_accrual, process_carryover, expire_carryover",
  "evidence_detail": "PKG_LEAVE.pkb lines 459-553 (run_monthly_accrual), 557-603 (process_carryover), 607-623 (expire_carryover); LEAVE_ACCRUAL_LOG INSERT at line 527 does not include RUN_ID column",
  "confidence_before": 0.5,
  "confidence_after": 0.92,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### E-003 — ENRICHED

```json
{
  "change_id": "E-003",
  "type": "ENRICHED",
  "finding_id": "data-source-inventory.json — Integration feed mechanisms confirmed as file-based",
  "what": "Agent 1 said feed mechanism was 'UNKNOWN — file drop, DB link, web service?'. Both outbound integrations are now confirmed as UTL_FILE flat file writes to Oracle Directory objects: GL feed → 'GL_FEED_OUT' (pipe-delimited for Oracle Financials); Benefits feed → 'BENEFITS_FEED_OUT' (fixed-width for ADP). A third input integration (time/attendance from 'TIME_ATTENDANCE_IN') exists but is a stub. A fourth integration (LDAP/AD via sync_org_structure) is also a stub. No DB links or web service calls found in PKG_INTEGRATION.",
  "evidence_source": "PKG_INTEGRATION.pkb",
  "evidence_detail": "PKG_INTEGRATION.pkb lines 6-8: c_gl_output_dir='GL_FEED_OUT', c_benefits_output_dir='BENEFITS_FEED_OUT', c_time_input_dir='TIME_ATTENDANCE_IN'",
  "confidence_before": 0.5,
  "confidence_after": 0.9,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### E-004 — ENRICHED

```json
{
  "change_id": "E-004",
  "type": "ENRICHED",
  "finding_id": "storage-pattern-analysis.md — generate_emp_number race condition confirmed",
  "what": "Agent 1 said MAX()+1 was inferred from a sequence file comment. Now confirmed from source: PKG_EMPLOYEE.generate_emp_number does SELECT NVL(MAX(TO_NUMBER(SUBSTR(EMP_NUMBER, 5))), 0) + 1 with no SELECT FOR UPDATE or serialization. Code contains its own comment: 'BUG: race condition under concurrent inserts - no SELECT FOR UPDATE'. Fallback on EXCEPTION uses SEQ_EMPLOYEE.NEXTVAL (wrong sequence — would generate a 10000+ ID, not an EMP-NNNNNN formatted number). Format: 'EMP-' + LPAD(max_num, 6, '0').",
  "evidence_source": "PKG_EMPLOYEE.pkb generate_emp_number",
  "evidence_detail": "PKG_EMPLOYEE.pkb lines 39-55: MAX()+1 implementation with self-documented race condition bug",
  "confidence_before": 0.7,
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### E-005 — ENRICHED

```json
{
  "change_id": "E-005",
  "type": "ENRICHED",
  "finding_id": "access-control-matrix.md — has_permission grade thresholds now confirmed",
  "what": "PKG_SECURITY.pkb was provided in the session context. The full has_permission implementation is now confirmed — upgrading access-control-matrix.md from LOW CONFIDENCE to confirmed:\n  GRADE_ID >= 8: Full access to ALL modules and ALL actions (senior management)\n  GRADE_ID >= 5: VIEW action on ALL modules (mid-level)\n  GRADE_ID < 5: Only (LEAVE, CREATE), (LEAVE, VIEW), and (EMPLOYEE, VIEW)\nNo named roles exist — authorization is purely grade-band based. The comment in the spec ('Simplified model — production should use a ROLES/PERMISSIONS junction table') is confirmed as intentional scope-down.",
  "evidence_source": "PKG_SECURITY.pkb has_permission (provided in prompt context)",
  "evidence_detail": "PKG_SECURITY.pkb has_permission: IF v_grade_id >= 8 → RETURN TRUE; IF p_action='VIEW' AND v_grade_id >= 5 → RETURN TRUE; module-specific rules for grade < 5",
  "confidence_before": 0.5,
  "confidence_after": 0.92,
  "phase_found": "Phase 2 — package body reading"
}
```

---

### E-006 — ENRICHED

```json
{
  "change_id": "E-006",
  "type": "ENRICHED",
  "finding_id": "pii-inventory.json + access-control-matrix.md — Authentication stub confirmed",
  "what": "PKG_SECURITY.authenticate was documented as having a stub password validation ('password validation logic is a stub — comments say passwords are in a separate USER_CREDENTIALS table but actual validation is not implemented'). Now confirmed from PKG_SECURITY.pkb: authenticate looks up the user by EMAIL in EMPLOYEES (does NOT query USER_CREDENTIALS at all), logs the session, and returns session_id — with no password hash comparison whatsoever in the provided body. The function creates a session for ANY valid active employee email regardless of what password is supplied, since there is no hash check in the code. This is more severe than 'stub' — it means authentication currently succeeds with any password for any active user.",
  "evidence_source": "PKG_SECURITY.pkb authenticate (provided in prompt context)",
  "evidence_detail": "PKG_SECURITY.pkb authenticate: SELECT EMP_ID WHERE UPPER(EMAIL) = UPPER(p_username) AND EMPLOYMENT_STATUS='ACTIVE' — no hash comparison, no USER_CREDENTIALS table query, immediately creates session",
  "confidence_before": 0.8,
  "confidence_after": 1.0,
  "phase_found": "Phase 2 — package body reading",
  "severity_escalation": "CRITICAL — effective no-password authentication in current implementation"
}
```

---

## Pass 2 Change Records (from full source file validation — 2026-08-03)

---

### RC-007 — CORRECTED

```json
{
  "change_id": "RC-007",
  "type": "CORRECTED",
  "finding_id": "schema-catalogue.json — sequence_count field; storage-pattern-analysis.md",
  "what": "schema-catalogue.json states 'sequence_count: 27'. The full hrms_sequences.sql contains 29 sequences (enumerated below). This is a 2-count discrepancy. The missing 2 are SEQ_SYSTEM_PARAM and SEQ_LOOKUP, both present in hrms_sequences.sql but absent from the count field. All other sequence details (NOCACHE default, SEQ_AUDIT CACHE 100) were correctly documented.",
  "evidence_source": "schema/sequences/hrms_sequences.sql",
  "evidence_detail": "hrms_sequences.sql: 29 CREATE SEQUENCE statements. Full list: SEQ_DEPARTMENT, SEQ_LOCATION, SEQ_JOB_GRADE, SEQ_JOB_TITLE, SEQ_EMPLOYEE, SEQ_EMP_HISTORY, SEQ_DEPENDENT, SEQ_EMERGENCY_CONTACT, SEQ_EMP_NUMBER, SEQ_SALARY, SEQ_PAY_ELEMENT, SEQ_EMP_PAY_ELEMENT, SEQ_PAY_PERIOD, SEQ_PAYROLL_RUN, SEQ_PAYROLL_DETAIL, SEQ_TAX_BRACKET, SEQ_LEAVE_TYPE, SEQ_LEAVE_BALANCE, SEQ_LEAVE_REQUEST, SEQ_LEAVE_ACCRUAL, SEQ_HOLIDAY, SEQ_REVIEW_CYCLE, SEQ_PERF_REVIEW, SEQ_PERF_GOAL, SEQ_AUDIT (CACHE 100), SEQ_NOTIFICATION, SEQ_USER_SESSION, SEQ_SYSTEM_PARAM, SEQ_LOOKUP",
  "confidence_before": 0.9,
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — full sequence file read"
}
```

---

### RC-008 — CORRECTED

```json
{
  "change_id": "RC-008",
  "type": "CORRECTED",
  "finding_id": "hidden-business-rules.json + storage-pattern-analysis.md — session timeout source",
  "what": "hidden-business-rules.json states the session timeout is 'configurable' via SYSTEM_PARAMETERS.SESSION_TIMEOUT_MIN. CORRECTED: PKG_SECURITY.pkb has a private constant 'c_session_timeout_min CONSTANT NUMBER := 30'. is_session_valid uses this constant directly — NOT PKG_COMMON.get_param() or any SYSTEM_PARAMETERS lookup. Identical pattern to RC-004 (SMTP host hard-coded in PKG_NOTIFICATION). The SYSTEM_PARAMETERS row for SESSION_TIMEOUT_MIN is therefore decorative — updating it has no effect on actual session expiry. Additionally: timeout is measured from LOGIN_TIME (set once at login), not from last activity — this is effectively a hard 30-minute absolute session limit regardless of user activity, not an inactivity timeout.",
  "evidence_source": "PKG_SECURITY.pkb is_session_valid (provided in this session)",
  "evidence_detail": "PKG_SECURITY.pkb: 'c_session_timeout_min CONSTANT NUMBER := 30'; is_session_valid: 'IF (SYSDATE - v_login_time) * 24 * 60 > 30' — constant literal 30, not a SYSTEM_PARAMETERS lookup. Session timeout = absolute 30-minute limit from LOGIN_TIME.",
  "confidence_before": 0.9,
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — PKG_SECURITY.pkb full body read"
}
```

---

### RC-009 — CORRECTED

```json
{
  "change_id": "RC-009",
  "type": "CORRECTED",
  "finding_id": "migration-complexity.json + hidden-business-rules.json — VW_EMPLOYEE_COMPENSATION salary join risk",
  "what": "storage-pattern-analysis.md noted VW_EMPLOYEE_COMPENSATION joins SALARY_RECORDS 'without the date-scoping that VW_ACTIVE_EMPLOYEES uses' as a data-quality risk (flagged but not fully specified). Now confirmed from hrms_views.sql: VW_EMPLOYEE_COMPENSATION joins SALARY_RECORDS with only 'sr.ACTIVE_FLAG = ''Y''' and NO effective-date filter (no 'sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE)'). If any employee has two ACTIVE_FLAG='Y' salary records (e.g. when a new salary is inserted before the old END_DATE is set, or after a bug in create_salary_record), VW_EMPLOYEE_COMPENSATION will return duplicate rows for that employee and produce incorrect COMPA_RATIO values. VW_ACTIVE_EMPLOYEES correctly uses the date-scoped join. This inconsistency between the two compensation views is a confirmed data-quality risk.",
  "evidence_source": "schema/views/hrms_views.sql VW_EMPLOYEE_COMPENSATION",
  "evidence_detail": "hrms_views.sql VW_EMPLOYEE_COMPENSATION: 'JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = ''Y''' — no EFFECTIVE_DATE or END_DATE predicate. Contrast with VW_ACTIVE_EMPLOYEES: 'LEFT JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = ''Y'' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE)'",
  "confidence_before": 0.7,
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — hrms_views.sql full read"
}
```

---

### A-022 — ADDED

```json
{
  "change_id": "A-022",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json + pii-inventory.json — change_password is a stub; USER_CREDENTIALS table never written",
  "what": "PKG_SECURITY.change_password validates password complexity (min 8 chars, uppercase required, digit required) but contains a NOTE comment explicitly stating 'actual password update is a stub — would write to USER_CREDENTIALS'. The procedure calls PKG_AUDIT.log_action('USER_CREDENTIALS', p_emp_id, 'UPDATE', USER) but never executes any INSERT or UPDATE against USER_CREDENTIALS. This means: (1) the USER_CREDENTIALS table (referenced in comments throughout PKG_SECURITY) appears to exist in the database schema but is not in the DDL files scanned — it is a referenced-but-undocumented table; (2) password changes called via this procedure have no effect; (3) the password complexity rules (8-char minimum, uppercase, digit) are enforced at validation but the enforced data is never persisted. Three ORA error codes are defined: -20310 (length), -20311 (uppercase), -20312 (digit). Lowercase and special character requirements are NOT enforced.",
  "evidence_source": "PKG_SECURITY.pkb change_password (provided in this session)",
  "evidence_detail": "PKG_SECURITY.pkb change_password: LENGTH check → ORA-20310; REGEXP_LIKE uppercase check → ORA-20311; REGEXP_LIKE digit check → ORA-20312; 'NOTE: actual password update is a stub'; PKG_AUDIT.log_action called but no DML on USER_CREDENTIALS",
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — PKG_SECURITY.pkb full body read",
  "secondary_finding": "USER_CREDENTIALS is a referenced table (in change_password comment, authenticate comment) but has no DDL in the scanned schema files. It may exist as an undocumented table or may have been planned but never created. Schema-catalogue.json table count of 30 does not include it."
}
```

---

### A-023 — ADDED

```json
{
  "change_id": "A-023",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — PKG_SECURITY.authenticate TOO_MANY_ROWS selects lowest EMP_ID",
  "what": "PKG_SECURITY.authenticate handles the case where multiple active employees share the same email address (a scenario that should be blocked by TRG_EMP_BEFORE_INSERT but could arise from direct DML or the race condition between the trigger's COUNT check and the INSERT). On TOO_MANY_ROWS: SELECT MIN(EMP_ID) INTO v_emp_id FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(p_username) AND EMPLOYMENT_STATUS = 'ACTIVE'. The user is authenticated as the employee with the lowest EMP_ID among all matching email addresses, with no error or warning logged. This is a silent collision-resolution rule that could grant a different employee's session than expected.",
  "evidence_source": "PKG_SECURITY.pkb authenticate (provided in this session)",
  "evidence_detail": "PKG_SECURITY.pkb authenticate: 'EXCEPTION WHEN TOO_MANY_ROWS: SELECT MIN(EMP_ID) INTO v_emp_id FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(p_username) AND EMPLOYMENT_STATUS = ''ACTIVE'''",
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — PKG_SECURITY.pkb full body read"
}
```

---

### A-024 — ADDED

```json
{
  "change_id": "A-024",
  "type": "ADDED",
  "finding_id": "data-quality-report.md + hidden-business-rules.json — VW_LEAVE_SUMMARY AVAILABLE formula confirmed as 4-term from view source",
  "what": "VW_LEAVE_SUMMARY's AVAILABLE column is now confirmed from the full view DDL to compute 'lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT' (4 terms, no PENDING subtraction), while the LEAVE_BALANCES virtual column computes the same as '... - PENDING' (5 terms). The view source also contains the comment 'note: does NOT subtract PENDING here, unlike the virtual column definition — potential discrepancy'. This is a developer-acknowledged inconsistency. Additionally confirmed: UTILIZATION_PCT = ROUND(lb.USED * 100 / NULLIF(lb.OPENING_BALANCE + lb.ACCRUED, 0), 1). The view filters on lb.CALENDAR_YEAR = EXTRACT(YEAR FROM SYSDATE) — only current-year balances are visible.",
  "evidence_source": "schema/views/hrms_views.sql VW_LEAVE_SUMMARY",
  "evidence_detail": "hrms_views.sql VW_LEAVE_SUMMARY: 'lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT' with inline comment 'note: does NOT subtract PENDING here'",
  "confidence_before": 0.9,
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — hrms_views.sql full read"
}
```

---

### E-007 — ENRICHED

```json
{
  "change_id": "E-007",
  "type": "ENRICHED",
  "finding_id": "data-quality-report.md + pii-inventory.json — PKG_SECURITY.pkb AES-256 key confirmed from body",
  "what": "pii-inventory.json noted 'hard-coded encryption key in PKG_SECURITY package BODY (not scanned in this pass)' with confidence 0.9. Now confirmed from PKG_SECURITY.pkb: 'c_encryption_key RAW(32) := UTL_RAW.CAST_TO_RAW(''HR$ystem_3ncrypt10n_K3y_2024!!'')'. The 32-byte key value is now fully extracted. Cipher: AES-256 CBC with PKCS5 padding (DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC + DBMS_CRYPTO.PAD_PKCS5). decrypt_ssn has an EXCEPTION WHEN OTHERS guard returning '***DECRYPT_ERROR***' — masking decrypt failures silently. The same key is used for both EMPLOYEES.SSN_ENCRYPTED and (by implication) EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED since both are described as using PKG_SECURITY. Key rotation would require re-encrypting all SSN values in both tables simultaneously.",
  "evidence_source": "PKG_SECURITY.pkb encrypt_ssn, decrypt_ssn (provided in this session)",
  "evidence_detail": "PKG_SECURITY.pkb: c_encryption_key = UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!'); encrypt_ssn: DBMS_CRYPTO.ENCRYPT with AES256+CBC+PKCS5; decrypt_ssn: DBMS_CRYPTO.DECRYPT same spec + EXCEPTION WHEN OTHERS RETURN '***DECRYPT_ERROR***'",
  "confidence_before": 0.9,
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — PKG_SECURITY.pkb full body read"
}
```

---

### E-008 — ENRICHED

```json
{
  "change_id": "E-008",
  "type": "ENRICHED",
  "finding_id": "da-outputs/erd.md + schema-catalogue.json — TRG_EMP_BEFORE_UPDATE column mismatch confirmed from both sides",
  "what": "The broken TRG_EMP_BEFORE_UPDATE finding is now confirmed from BOTH sides of the mismatch. From trg_employees.sql: the trigger INSERT uses columns (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON) and CHANGE_TYPE values 'STATUS_CHANGE', 'DEPARTMENT_CHANGE', 'JOB_CHANGE'. From 01_core_tables.sql: EMPLOYEE_HISTORY DDL defines columns (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE) with CHK_CHANGE_TYPE allowing only ('HIRE', 'TRANSFER', 'PROMOTION', 'DEMOTION', 'SALARY_CHANGE', 'TERMINATION', 'REHIRE', 'LEAVE_START', 'LEAVE_END', 'STATUS_CHANGE'). The mismatched columns are: HISTORY_ID (trigger) vs HIST_ID (DDL), CHANGE_DATE vs EFFECTIVE_DATE, OLD_VALUE vs OLD_DEPT_ID/OLD_JOB_ID (etc), NEW_VALUE vs NEW_DEPT_ID/NEW_JOB_ID (etc), CHANGED_BY vs CREATED_BY, CHANGE_REASON vs REASON_CODE/COMMENTS. Additionally DEPARTMENT_CHANGE and JOB_CHANGE are NOT in CHK_CHANGE_TYPE (ORA-02290). STATUS_CHANGE IS in CHK_CHANGE_TYPE — the status-change branch is column-mismatched but the constraint would not fire on CHANGE_TYPE itself for that branch.",
  "evidence_source": "plsql/triggers/trg_employees.sql TRG_EMP_BEFORE_UPDATE + schema/tables/01_core_tables.sql EMPLOYEE_HISTORY",
  "evidence_detail": "TRG_EMP_BEFORE_UPDATE insert columns: HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON. Actual DDL columns: HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, ..., REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE. Mismatch on every column except EMP_ID and CHANGE_TYPE.",
  "confidence_before": 0.97,
  "confidence_after": 1.0,
  "phase_found": "Pass 2 — full DDL + trigger source read"
}
```

---

## Cross-File Consistency Check Results (Phase 5)

### Pass 1 checks (prior session)

| Check | Files | Result |
|---|---|---|
| Table count matches | schema-catalogue.json (30) ↔ erd.md (30 tables covered) | PASS |
| PII columns match | pii-inventory.json ↔ schema-catalogue.json | PASS — minor gap: EMPLOYEES.NOTES (CLOB, may contain PII) not listed in pii-inventory.json |
| Row counts match | schema-catalogue.json ↔ migration-complexity.json | PASS — both CODE-ONLY, consistent |
| Business rules in flow map | hidden-business-rules.json ↔ data-flow-map.md | PASS — 5 new rules added from package bodies, both files need updates |
| Cache in both places | data-source-inventory.json ↔ storage-pattern-analysis.md | PASS — both agree no cache layer |
| FK delete rules consistent | schema-catalogue.json ↔ migration-complexity.json | PASS — both note NO CASCADE DELETE declared anywhere |
| Canonical entity claims | redundancy-analysis.json ↔ schema-catalogue.json | PASS |
| Dictionary entry for every table | data-dictionary.md ↔ schema-catalogue.json | PASS — all 30 tables present in both |
| Conceptual model traces to aggregate roots | conceptual-data-model.md ↔ schema-catalogue.json | PASS |
| Every PII column in access matrix | access-control-matrix.md ↔ pii-inventory.json | PARTIAL — benefits export PII path (A-009) not in access-control-matrix.md; now documented |

### Pass 2 checks (this session — full source file validation)

| Check | Files | Result |
|---|---|---|
| Sequence count | schema-catalogue.json ("sequence_count": 27) ↔ hrms_sequences.sql (29 sequences) | FIXED — RC-007: 2 missing (SEQ_SYSTEM_PARAM, SEQ_LOOKUP); schema-catalogue.json count corrected to 29 |
| Session timeout configurability | hidden-business-rules.json (claims SYSTEM_PARAMETERS-driven) ↔ PKG_SECURITY.pkb (hard-coded constant) | FIXED — RC-008: timeout is hard-coded c_session_timeout_min=30; SYSTEM_PARAMETERS row is decorative |
| VW_EMPLOYEE_COMPENSATION salary join | storage-pattern-analysis.md (flagged as risk) ↔ hrms_views.sql (full join definition) | FIXED — RC-009: confirmed missing date-scope predicate; VW_EMPLOYEE_COMPENSATION can return multiple rows per employee |
| VW_LEAVE_SUMMARY AVAILABLE formula | data-quality-report.md ↔ hrms_views.sql | PASS/ENRICHED — A-024: 4-term formula confirmed from view source, developer comment acknowledges discrepancy |
| TRG_EMP_BEFORE_UPDATE mismatch | erd.md/schema-catalogue.json ↔ trg_employees.sql + 01_core_tables.sql | PASS/ENRICHED — E-008: mismatch confirmed from both sides; every column except EMP_ID and CHANGE_TYPE disagrees |
| Trigger inventory completeness | schema-catalogue.json (6 triggers listed) ↔ trg_employees.sql + trg_audit.sql | PASS — 6 triggers confirmed: TRG_EMP_BEFORE_INSERT, TRG_EMP_BEFORE_UPDATE, TRG_EMP_INSTEAD_OF_DELETE (BEFORE DELETE), TRG_SALARY_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_DEPARTMENT_AUDIT |
| View count and names | schema-catalogue.json (6 views) ↔ hrms_views.sql | PASS — 6 views confirmed: VW_ACTIVE_EMPLOYEES, VW_ORG_HIERARCHY, VW_EMPLOYEE_COMPENSATION, VW_LEAVE_SUMMARY, VW_PAYROLL_LATEST, VW_PENDING_APPROVALS |
| USER_CREDENTIALS table in schema | schema-catalogue.json (30 tables, USER_CREDENTIALS not listed) ↔ PKG_SECURITY.pkb (references USER_CREDENTIALS in comments) | GAP — A-022: USER_CREDENTIALS is a referenced-but-undocumented table; not in DDL files scanned; not in schema-catalogue.json |

---

## Open Questions for Gate G1

Items requiring business intent, legal input, or infrastructure decisions — cannot be answered by reading code:

**G1-Q1 — AUTHORITATIVE AVAILABLE BALANCE FORMULA**
Three code paths use different "available" formulas: virtual column and get_leave_balance subtract PENDING (correct); VW_LEAVE_SUMMARY and process_carryover do not. Which formula is the business intent? A product owner or payroll manager must designate the canonical formula. Incorrect carryover amounts may have already been posted to employees.
*Role: HR/Payroll Product Owner*

**G1-Q2 — TAX BRACKET MIGRATION STRATEGY**
Federal/state tax brackets are hard-coded as 2024 values. When do brackets need to be updated for 2025+? Will the TAX_BRACKETS table be populated and used (the stated intent in the TODO comment), or will a package body edit be required each year? Annual release decision required before any migration or modernization.
*Role: Payroll Director + DBA*

**G1-Q3 — HEAD_OF_HOUSEHOLD EMPLOYEES**
Any employee with HEAD_OF_HOUSEHOLD filing status is currently having $0 federal tax withheld (RC-005). A DBA query on EMPLOYEE_TAX_INFO WHERE FILING_STATUS = 'HEAD_OF_HOUSEHOLD' will confirm whether any live employees are affected. If so, retroactive correction and possible IRS notification may be required.
*Role: Payroll Manager + Tax Compliance*

**G1-Q4 — AUTHENTICATION STUB IN PRODUCTION**
PKG_SECURITY.authenticate creates a valid session for any active employee's email with no password verification (E-006 escalation). If this codebase is running in production as-is, the system is effectively unauthenticated. Confirm whether a patched version of authenticate exists in production that isn't in this repo, or whether access relies entirely on Oracle Forms' built-in Oracle DB authentication layer.
*Role: CISO + DBA*

**G1-Q5 — REHIRE SENIORITY POLICY**
rehire_employee overwrites HIRE_DATE with the rehire date (A-008). Is this the intended HR policy? Many organizations preserve original hire date for seniority/benefits purposes and use a separate "rehire date" field. If continuity of service is a policy requirement, a schema change (adding ORIGINAL_HIRE_DATE) and a data correction pass are needed.
*Role: HR Director*

**G1-Q6 — BENEFITS FEED PII COMPLIANCE**
export_benefits_feed sends employee and dependent PII (names, DOBs, gender, marital status) in a plaintext flat file to an ADP vendor (A-009, A-012). Is this feed active? Does it have a current data processing agreement with ADP? Under GDPR/CCPA, dependent PII (third parties who haven't consented) in an external feed requires specific legal basis.
*Role: Legal / Data Privacy Officer*

**G1-Q7 — RIGHT TO ERASURE FOR TERMINATED EMPLOYEES**
TRG_EMP_INSTEAD_OF_DELETE unconditionally blocks all physical employee deletes. No anonymization path exists. What is the company's retention and anonymization policy for terminated employees' PII (SSN, DOB, address, bank accounts)? This is a pre-migration blocker for any GDPR/CCPA-compliant modernization.
*Role: Legal / Data Privacy Officer*

**G1-Q8 — PKG_REPORTING.pkb**
PKG_REPORTING.pkb exists in the source but was not read in either review pass. It is one of four remaining unread package bodies (also PKG_COMMON.pkb, PKG_VALIDATION.pkb, PKG_PERFORMANCE.pkb). If these contain additional business rules (e.g., headcount calculation, compensation banding, turnover thresholds, validation thresholds), those rules will be missing from the current analysis. A follow-on read is recommended before G1.
*Role: DA Agent follow-up (code-readable, not a business question)*

**G1-Q9 — USER_CREDENTIALS table existence and schema**
PKG_SECURITY.pkb references a USER_CREDENTIALS table in comments for both authenticate and change_password procedures (authenticate: "real passwords in USER_CREDENTIALS, this is a legacy stub"; change_password: "would write to USER_CREDENTIALS"). This table is not in any DDL file scanned and not in schema-catalogue.json's 30 tables. Does USER_CREDENTIALS exist in the production database? If so, provide its DDL for analysis — it contains password hashes and is central to the authentication security assessment. If not, confirm the system has never had a functioning password check.
*Role: DBA + CISO*

**G1-Q10 — Session timeout: absolute vs. inactivity (business intent)**
PKG_SECURITY.is_session_valid implements a hard 30-minute absolute session limit from login time (not last-activity inactivity timeout). A user who is actively working will be cut off after exactly 30 minutes. The SYSTEM_PARAMETERS.SESSION_TIMEOUT_MIN value is ignored at runtime (hard-coded constant in package body). Is a 30-minute absolute limit the intended business behavior? Should the clock reset on each user action?
*Role: HR System Owner + CISO*

---

## Gate G1 Recommendation

**NOT READY**

**Reason:** Six categories of unresolved issues (updated after Pass 2) block a confident Gate G1 review:

1. **3 confirmed launch-blocking defects remain unresolved from Agent 1** — the broken TRG_EMP_BEFORE_UPDATE (blocks all transfers/promotions/terminations/rehires; now confirmed from both sides in E-008), the seed/DDL column mismatches (prevents clean environment setup), and the AUDIT_LOG STATUS_CHANGE compliance gap. These must be remediated or accepted with documented workarounds before a migration design can be baselined.

2. **Critical security finding (E-006, confirmed in Pass 2)** — PKG_SECURITY.authenticate contains no password verification whatsoever in the code provided. USER_CREDENTIALS table is now confirmed as referenced-but-undocumented (A-022, G1-Q9). If this represents the production state, this is a showstopper requiring an emergency patch and security audit before the system can be presented to stakeholders.

3. **Payroll compliance defect (RC-005)** — HEAD_OF_HOUSEHOLD employees receive $0 federal tax withholding. Requires impact assessment before G1.

4. **Payroll data integrity defects (RC-006, A-020)** — PAYROLL_RUNS.TOTAL_NET/TOTAL_DEDUCTIONS are wrong for employees with BENEFIT deductions; payroll commits mid-run with no clean retry path. Requires stakeholder acknowledgement.

5. **SQL injection security defect (A-001)** — PKG_EMPLOYEE.search_employees has a documented SQL injection vulnerability that requires patching before any migration work that preserves this package.

6. **New Pass 2 finding: VW_EMPLOYEE_COMPENSATION salary join risk (RC-009)** — compensation view can return duplicate rows per employee if multiple ACTIVE_FLAG='Y' salary records exist; produces incorrect COMPA_RATIO values. Any reports or forms driven by this view may show wrong compensation data.

**When ready:** After the 3 original launch blockers are resolved or formally accepted, the authentication stub is confirmed/patched (G1-Q4, G1-Q9), the payroll compliance bug is assessed, VW_EMPLOYEE_COMPENSATION is corrected, and PKG_REPORTING.pkb + PKG_COMMON.pkb + PKG_VALIDATION.pkb + PKG_PERFORMANCE.pkb are read to complete package coverage.

---

## Appendix: Full Procedure/Function Inventory (Packages Read This Pass)

### PKG_EMPLOYEE (11 public + 4 private)
| Name | Type | Key business rule |
|---|---|---|
| create_employee | FUNCTION RETURN NUMBER | Validates dept/manager/job; generates EMP_ID via SEQ_EMPLOYEE; generates EMP_NUMBER via MAX()+1 (race condition); creates initial salary record; logs HIRE history; sends welcome + manager notifications |
| update_employee | PROCEDURE | Partial update (NVL pattern); contact fields only; audits via PKG_AUDIT |
| get_employee | FUNCTION | Returns t_emp_rec with current salary from SALARY_RECORDS |
| get_employee_by_number | FUNCTION | Delegates to get_employee |
| search_employees | PROCEDURE (cursor) | Dynamic SQL, SQL injection vulnerability |
| transfer_employee | PROCEDURE | Active-only; validates dept+manager; SELECT FOR UPDATE NOWAIT; logs TRANSFER history |
| promote_employee | PROCEDURE | Updates JOB_ID; calls PKG_PAYROLL.create_salary_record; logs PROMOTION history |
| terminate_employee | PROCEDURE | Auto-cancels PENDING leave; ends salary record; deactivates pay elements; logs TERMINATION history |
| rehire_employee | PROCEDURE | Overwrites HIRE_DATE; calls PKG_PAYROLL.create_salary_record; logs REHIRE history |
| get_direct_reports | FUNCTION | Returns ACTIVE direct reports as t_emp_id_table |
| get_org_chart | FUNCTION (cursor) | CONNECT BY recursive, max depth p_max_depth (default 10) |
| get_headcount_by_dept | FUNCTION | Count of ACTIVE employees as of given date |
| get_tenure_years | FUNCTION | ROUND(MONTHS_BETWEEN/12, 1) — note: ROUND not TRUNC |
| is_active | FUNCTION | Returns BOOLEAN |
| validate_employee | FUNCTION | Checks FIRST_NAME, LAST_NAME, HIRE_DATE, ACTIVE_FLAG consistency |
| emp_exists | FUNCTION | COUNT(*) check |
| set_session_context | PROCEDURE | Sets g_current_user, g_current_emp_id, g_current_dept_id |
| generate_emp_number | FUNCTION (private) | MAX()+1 race condition |
| get_next_emp_id | FUNCTION (private) | SEQ_EMPLOYEE.NEXTVAL |
| validate_dept | PROCEDURE (private) | ORA-20003 if inactive dept |
| validate_manager | PROCEDURE (private) | ORA-20004; circular chain check max depth 15 |
| log_history | PROCEDURE (private) | PRAGMA AUTONOMOUS_TRANSACTION; correct column set |

### PKG_PAYROLL (14 procedures/functions)
| Name | Type | Key business rule |
|---|---|---|
| create_salary_record | PROCEDURE | Ends prior active salary; inserts new; audits |
| get_current_salary | FUNCTION | EFFECTIVE_DATE <= SYSDATE; FETCH FIRST 1 ROW |
| get_salary_as_of | FUNCTION | Point-in-time salary lookup |
| create_pay_periods | PROCEDURE | Generates monthly or biweekly periods for a year; monthly pay date = last day of month, moved to Friday if weekend |
| close_pay_period | PROCEDURE | ORA-20102 if already CLOSED |
| get_current_period | FUNCTION | PERIOD_ID where SYSDATE BETWEEN start/end AND STATUS='OPEN' |
| create_payroll_run | FUNCTION | ORA-20102 if period CLOSED; returns RUN_ID |
| calculate_payroll | PROCEDURE | Row-by-row cursor; partial commits every 50 employees |
| calculate_employee_pay | PROCEDURE | Annual/periods math; federal+state+FICA+Medicare+deductions; defaults to SINGLE/0 allowances if no W-4 |
| approve_payroll | PROCEDURE | Only from CALCULATED status |
| reverse_payroll | PROCEDURE | Sets run+details to REVERSED |
| calculate_federal_tax | FUNCTION (private) | Hard-coded 2024 brackets; HEAD_OF_HOUSEHOLD returns 0 |
| calculate_state_tax | FUNCTION (private) | Flat rates by state; 5% default |
| calculate_fica | FUNCTION (private) | 6.2% up to $168,600 wage base |
| calculate_medicare | FUNCTION (private) | 1.45% base + 0.9% above $200,000 YTD |
| get_payslip | PROCEDURE (cursor) | YTD_GROSS/YTD_NET are hardcoded 0 |
| get_ytd_earnings | FUNCTION | Sum of EARNING elements for tax year |
| generate_pay_register | PROCEDURE | UTL_FILE CSV to 'PAYROLL_OUTPUT' directory |

### PKG_LEAVE (11 procedures/functions)
| Name | Type | Key business rule |
|---|---|---|
| submit_leave_request | FUNCTION | Validates tenure; allows 5-day backdating; calculates business days; checks overlap; checks balance (accrual types only); NULL approver if no manager |
| approve_leave_request | PROCEDURE | PENDING only; moves PENDING→USED in balance; notifies employee |
| reject_leave_request | PROCEDURE | PENDING only; releases PENDING balance; notifies employee |
| cancel_leave_request | PROCEDURE | PENDING or APPROVED; restores PENDING or USED balance appropriately |
| get_leave_balance | FUNCTION | 5-term formula (correct: includes -PENDING) |
| adjust_leave_balance | PROCEDURE | Adds to ADJUSTMENT; creates balance row if missing |
| initialize_balances | PROCEDURE | Creates zero-balance rows for all active leave types |
| run_monthly_accrual | PROCEDURE | Monthly batch; ACCRUAL_FLAG='Y' AND ACCRUAL_FREQUENCY='MONTHLY'; respects MIN_TENURE_DAYS and MAX_BALANCE; commits every 100 employees; does NOT populate RUN_ID in LEAVE_ACCRUAL_LOG |
| process_carryover | PROCEDURE | Year-end; uses 4-term formula (no PENDING); caps at CARRYOVER_MAX; sets CARRYOVER_EXPIRY_DT via ADD_MONTHS from Jan 1 |
| expire_carryover | PROCEDURE | Double-subtract bug if run twice same day |
| calculate_business_days | FUNCTION (private) | Excludes weekends + active holidays for location; does not handle observed holidays |
| check_leave_overlap | FUNCTION (private) | Checks PENDING + APPROVED status only |
| get_pending_requests | PROCEDURE (cursor) | Filtered by APPROVER_EMP_ID |
| get_team_calendar | PROCEDURE (cursor) | APPROVED + TAKEN for manager's direct reports |

### PKG_INTEGRATION (5 procedures/functions)
| Name | Type | Key business rule |
|---|---|---|
| generate_gl_journal | PROCEDURE | Pipe-delimited H/D/T file to 'GL_FEED_OUT'; groups by COST_CENTER + GL_ACCOUNT_CODE |
| export_benefits_feed | PROCEDURE | Fixed-width ADP format to 'BENEFITS_FEED_OUT'; exports sensitive PII without has_permission check |
| import_time_attendance | PROCEDURE | Reads from 'TIME_ATTENDANCE_IN'; TODO stub — no database writes |
| sync_org_structure | PROCEDURE | Placeholder stub — no LDAP/AD calls |
| get_integration_status | FUNCTION | Returns PKG_COMMON.get_param('INTEGRATION', name+'_STATUS') |

### PKG_NOTIFICATION (4 procedures)
| Name | Type | Key business rule |
|---|---|---|
| send_notification | PROCEDURE | PRAGMA AUTONOMOUS_TRANSACTION; resolves email from EMP_ID; inserts to NOTIFICATION_QUEUE; never blocks caller |
| process_queue | PROCEDURE | UTL_SMTP.OPEN_CONNECTION to hard-coded c_smtp_host:25; processes up to p_batch_size (default 50) PENDING EMAIL records per run; DBMS_SCHEDULER every 5 minutes |
| retry_failed | PROCEDURE | Resets STATUS='PENDING' where RETRY_COUNT < p_max_retries (default 3) |
| cancel_notification | PROCEDURE | Cancels PENDING notification only |

### PKG_SECURITY (confirmed from pkb body — Pass 2)
| Name | Type | Key business rule |
|---|---|---|
| hash_password | FUNCTION | MD5 via DBMS_CRYPTO.HASH — no salt; returns RAWTOHEX |
| authenticate | FUNCTION RETURN NUMBER | Selects EMPLOYEES by EMAIL (ACTIVE only); no password comparison; no USER_CREDENTIALS query; creates USER_SESSIONS row; returns SESSION_ID. TOO_MANY_ROWS: selects MIN(EMP_ID). |
| logout | PROCEDURE | Updates USER_SESSIONS SET SESSION_STATUS='CLOSED', LOGOUT_TIME=SYSDATE |
| is_session_valid | FUNCTION RETURN BOOLEAN | Checks SESSION_STATUS='ACTIVE'; hard 30-minute absolute limit from LOGIN_TIME (c_session_timeout_min=30, not read from SYSTEM_PARAMETERS) |
| has_permission | FUNCTION RETURN BOOLEAN | Pure grade-band: GRADE_ID>=8 full access; GRADE_ID>=5 VIEW all; <5 leave+own profile only |
| encrypt_ssn | FUNCTION | AES-256 CBC PKCS5 with hard-coded key 'HR$ystem_3ncrypt10n_K3y_2024!!'; returns RAWTOHEX |
| decrypt_ssn | FUNCTION | Inverse of encrypt_ssn; EXCEPTION WHEN OTHERS → '***DECRYPT_ERROR***' |
| change_password | PROCEDURE | Validates 8-char min, uppercase, digit; STUB — never writes to USER_CREDENTIALS; ORA-20310/20311/20312 |
| c_encryption_key (private) | CONSTANT RAW(32) | Hard-coded AES key — SECURITY VULNERABILITY |
| c_session_timeout_min (private) | CONSTANT NUMBER := 30 | Hard-coded; SYSTEM_PARAMETERS.SESSION_TIMEOUT_MIN is ignored at runtime |

### PKG_AUDIT (confirmed from pkb body — Pass 2)
| Name | Type | Key business rule |
|---|---|---|
| log_action | PROCEDURE | PRAGMA AUTONOMOUS_TRANSACTION; inserts to AUDIT_LOG via SEQ_AUDIT.NEXTVAL; captures IP from SYS_CONTEXT('USERENV','IP_ADDRESS') and session from SYS_CONTEXT('USERENV','SESSIONID'); EXCEPTION WHEN OTHERS → ROLLBACK (silently swallows failures — audit must never block caller); default retention N/A |
| purge_old_records | PROCEDURE | DELETE FROM AUDIT_LOG WHERE CHANGED_DATE < SYSDATE - p_days_to_keep; default p_days_to_keep=365; DBMS_OUTPUT confirmation; no scheduler confirmed |
| get_change_history | FUNCTION RETURN SYS_REFCURSOR | SELECT from AUDIT_LOG for table+record_id; date range optional; ORDER BY CHANGED_DATE DESC |

---

## Sequence Inventory (confirmed from hrms_sequences.sql — Pass 2)

All 29 sequences confirmed. All are NOCACHE except SEQ_AUDIT (CACHE 100). All increment by 1.

| Sequence | Start | Used By |
|---|---|---|
| SEQ_DEPARTMENT | 100 | DEPARTMENTS.DEPT_ID |
| SEQ_LOCATION | 100 | LOCATIONS.LOCATION_CODE (natural key — sequence exists but natural key is VARCHAR2) |
| SEQ_JOB_GRADE | 100 | JOB_GRADES.GRADE_ID |
| SEQ_JOB_TITLE | 100 | JOB_TITLES.JOB_ID |
| SEQ_EMPLOYEE | 10000 | EMPLOYEES.EMP_ID (via PKG_EMPLOYEE.get_next_emp_id) |
| SEQ_EMP_HISTORY | 1 | EMPLOYEE_HISTORY.HIST_ID |
| SEQ_DEPENDENT | 1 | EMPLOYEE_DEPENDENTS.DEPENDENT_ID |
| SEQ_EMERGENCY_CONTACT | 1 | EMERGENCY_CONTACTS.CONTACT_ID |
| SEQ_EMP_NUMBER | 1000 | EMPLOYEES.EMP_NUMBER format — NOT USED correctly; PKG_EMPLOYEE.generate_emp_number uses MAX()+1 instead |
| SEQ_SALARY | 1 | SALARY_RECORDS.SALARY_ID |
| SEQ_PAY_ELEMENT | 1 | PAY_ELEMENTS.ELEMENT_ID |
| SEQ_EMP_PAY_ELEMENT | 1 | EMPLOYEE_PAY_ELEMENTS.EMP_ELEMENT_ID |
| SEQ_PAY_PERIOD | 1 | PAY_PERIODS.PERIOD_ID |
| SEQ_PAYROLL_RUN | 1 | PAYROLL_RUNS.RUN_ID |
| SEQ_PAYROLL_DETAIL | 1 | PAYROLL_DETAILS.DETAIL_ID |
| SEQ_TAX_BRACKET | 1 | TAX_BRACKETS.BRACKET_ID |
| SEQ_LEAVE_TYPE | 1 | LEAVE_TYPES.LEAVE_TYPE_ID |
| SEQ_LEAVE_BALANCE | 1 | LEAVE_BALANCES.BALANCE_ID |
| SEQ_LEAVE_REQUEST | 1 | LEAVE_REQUESTS.REQUEST_ID |
| SEQ_LEAVE_ACCRUAL | 1 | LEAVE_ACCRUAL_LOG.ACCRUAL_ID |
| SEQ_HOLIDAY | 1 | HOLIDAYS.HOLIDAY_ID |
| SEQ_REVIEW_CYCLE | 1 | REVIEW_CYCLES.CYCLE_ID |
| SEQ_PERF_REVIEW | 1 | PERFORMANCE_REVIEWS.REVIEW_ID |
| SEQ_PERF_GOAL | 1 | PERFORMANCE_GOALS.GOAL_ID |
| SEQ_AUDIT | 1 | AUDIT_LOG.AUDIT_ID — **CACHE 100** (only cached sequence; high-volume table) |
| SEQ_NOTIFICATION | 1 | NOTIFICATION_QUEUE.NOTIFICATION_ID |
| SEQ_USER_SESSION | 1 | USER_SESSIONS.SESSION_ID |
| SEQ_SYSTEM_PARAM | 1 | SYSTEM_PARAMETERS.PARAM_ID |
| SEQ_LOOKUP | 1 | LOOKUP_VALUES.LOOKUP_ID |

---

*DA Reverse Engineering System — Agent 2 of 2 | v2 | June 2026*
*Pass 1 produced: 2026-08-03 | Pass 2 produced: 2026-08-03*
