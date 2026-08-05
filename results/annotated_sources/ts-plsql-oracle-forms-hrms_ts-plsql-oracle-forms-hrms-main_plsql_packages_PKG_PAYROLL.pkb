The file has been annotated. Here is a summary of every annotation added and why:

---

### Annotations inserted

**`-- CONSTRAINT:` (constants block)**
- `c_ss_wage_base_2024 = 168600` — 2024 Social Security wage ceiling; earnings above this are SS-exempt.
- `c_ss_rate = 0.062` — 6.2% employee FICA rate.
- `c_medicare_rate = 0.0145` — 1.45% base Medicare rate, no cap.
- `c_medicare_addl_rate = 0.009` — 0.9% surtax above the high-earner threshold.
- `c_medicare_addl_threshold = 200000` — $200,000 YTD threshold that triggers the surtax.
- `c_standard_deduction_single = 14600` — 2024 IRS standard deduction for single filers.
- `c_standard_deduction_married = 29200` — 2024 IRS standard deduction for MFJ filers.
- `c_allowance_amount = 4300` — Each W-4 allowance reduces annualised taxable income by $4,300.
- Biweekly pay date: pay issued 5 calendar days after the period end date.
- Batch commit size: every 50 employees.
- State flat rates table (CA, NY, TX, FL, WA, IL, PA, OH, NJ, MA, default).

**`-- RULE:` (if/case conditions and `RAISE_APPLICATION_ERROR` calls)**
- Salary must be positive (raises -20101).
- A CLOSED period cannot be closed again (raises -20102).
- A payroll run cannot be created for a CLOSED period (raises -20102).
- Only ACTIVE employees (EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y') are processed.
- A batch commit fires every 50 successfully processed employees.
- A run with any errors lands in ERROR status; otherwise it becomes CALCULATED.
- Employee must have a salary record as of period end date (raises -20104).
- No W-4 on file defaults to SINGLE, 0 allowances, no additional withholding.
- Federal/state/SS/Medicare deductions are only written when the amount > 0.
- Only positive deduction amounts are persisted; zero or negative amounts are dropped.
- A payroll run must be in CALCULATED status to be approved (raises -20103).
- MARRIED_JOINT receives the married standard deduction; all others get the single deduction.
- Allowances reduce annualised taxable income before bracket calculation.
- If annualised taxable income is ≤ 0 after deductions/allowances, tax = 0.
- Single/MFS: 2024 seven-bracket rates up to 37% at $609,350.
- MFJ: 2024 seven-bracket rates up to 37% at $731,200.
- SS: YTD ≥ wage base → no further withholding; crossing the base mid-period → only the remaining headroom is taxable.
- Medicare surtax: full period gross taxable once YTD already exceeds threshold; only excess taxable if threshold is crossed during the period.
- Weekend pay-date shift: Saturday → Friday (−1 day), Sunday → Friday (−2 days).
- Biweekly period included if start or end date falls in the target year.

**`-- BUSINESS:` (cursor/query WHERE clauses)**
- `create_salary_record` UPDATE: targets the active, prior-effective salary for end-dating.
- `get_current_salary`: active-flag + effective-date window for today.
- `get_salary_as_of`: point-in-time salary look-up.
- `calculate_payroll` cursor: only ACTIVE + ACTIVE_FLAG employees.
- `calculate_employee_pay` W-4 query: matched by employee, tax year, and active flag.
- `calculate_employee_pay` deductions cursor: active elements, type IN (DEDUCTION/BENEFIT), within effective date range, ordered by PRIORITY_ORDER.
- `get_current_period`: OPEN period that brackets today.
- `get_ytd_earnings`: CALCULATED EARNING lines whose period start year equals the tax year.
- `get_payslip`: excludes ERROR lines, optionally filtered to one employee.
- `generate_pay_register`: excludes ERROR lines, one row per employee/department.

**`-- VALIDATION:`**
- `NVL(p_additional_wh, 0)` in `calculate_federal_tax`: treats a NULL extra-withholding amount as zero.
