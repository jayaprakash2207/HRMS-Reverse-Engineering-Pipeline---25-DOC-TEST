The file has been annotated. Here is a summary of every comment inserted and why:

---

### `headcount_report`
| Tag | Location | What it documents |
|---|---|---|
| `RULE` | `EMPLOYMENT_TYPE` CASE expressions | Three employment classifications (FULL_TIME / PART_TIME / CONTRACT) are mutually exclusive; other types are silently excluded |
| `RULE` | `GENDER` CASE expressions | Gender codes 'M' and 'F' are the only two counted; any other code falls outside both totals |
| `VALIDATION` | `AVG_TENURE_YEARS` | Tenure formula — MONTHS_BETWEEN ÷ 12, rounded to 1 dp |
| `BUSINESS` | `WHERE EMPLOYMENT_STATUS = 'ACTIVE'` | Inactive/terminated records are excluded from headcount |
| `RULE` | `HIRE_DATE <= p_as_of_date` | Employee must have started on or before the snapshot date |
| `RULE` | `TERMINATION_DATE IS NULL OR > p_as_of_date` | NULL and future termination dates both count as still-active |

### `compensation_summary`
| Tag | Location | What it documents |
|---|---|---|
| `VALIDATION` | `COMPA_RATIO` | Ratio formula — average salary as % of grade midpoint |
| `BUSINESS` | `SALARY_RECORDS sr … ACTIVE_FLAG = 'Y'` | Only the live salary row is used; history rows are excluded |
| `BUSINESS` | `WHERE EMPLOYMENT_STATUS = 'ACTIVE'` | Compensation analysis is active-employees-only |

### `turnover_report`
| Tag | Location | What it documents |
|---|---|---|
| `RULE` | `TERMINATION_DATE BETWEEN` | Termination must fall within the reporting window to count |
| `RULE` | `EMPLOYMENT_STATUS = 'ACTIVE'` in CURRENT_HC | Current headcount is real-time, not a historical snapshot |
| `VALIDATION` | `TURNOVER_PCT` | Turnover formula; NULLIF guards division-by-zero |
| `RULE` | `TERMINATION_REASON = 'VOLUNTARY'` | Voluntary departure classification |
| `RULE` | `TERMINATION_REASON != 'VOLUNTARY'` | Involuntary departure classification |
| `RULE` | `HAVING COUNT(…) > 0` | Departments with no historical employees are suppressed |

### `new_hires_report`
| Tag | Location | What it documents |
|---|---|---|
| `BUSINESS` | `LEFT JOIN SALARY_RECORDS … ACTIVE_FLAG = 'Y'` | Active salary only; LEFT JOIN preserves new hires without a salary record |
| `BUSINESS` | `WHERE HIRE_DATE BETWEEN` | Report scope is defined by hire date falling within the window |

### `leave_utilization_report`
| Tag | Location | What it documents |
|---|---|---|
| `VALIDATION` | `AVG_REMAINING` | Four-component balance formula (opening + accrued − used + adjustment) |
| `VALIDATION` | `UTILIZATION_PCT` | Utilisation formula; NULLIF prevents divide-by-zero when entitlement is zero |
| `BUSINESS` | `WHERE CALENDAR_YEAR = p_year` | Balances are scoped to a single calendar year |
| `BUSINESS` | `AND EMPLOYMENT_STATUS = 'ACTIVE'` | Departed employees' balances are excluded |

### `payroll_summary_report`
| Tag | Location | What it documents |
|---|---|---|
| `RULE` | `ELEMENT_TYPE = 'EARNING'` | Gross pay excludes tax, deduction, and benefit lines |
| `CONSTRAINT` | `ELEMENT_ID = 100` | Hard-coded identifier for Federal Income Tax |
| `CONSTRAINT` | `ELEMENT_ID = 101` | Hard-coded identifier for State Income Tax |
| `CONSTRAINT` | `ELEMENT_ID = 102` | Hard-coded identifier for Social Security (FICA) |
| `CONSTRAINT` | `ELEMENT_ID = 103` | Hard-coded identifier for Medicare |
| `RULE` | `ELEMENT_TYPE IN ('DEDUCTION','BENEFIT')` | Deduction total covers both DEDUCTION and BENEFIT lines; ABS() applied because they are stored negative |
| `RULE` | `STATUS != 'ERROR'` | Error-flagged payroll lines are excluded from all totals |

### `eeo_compliance_report`
| Tag | Location | What it documents |
|---|---|---|
| `RULE` | `GENDER` CASE expressions | Three declared codes ('M', 'F', 'O') plus a NULL/not-disclosed bucket |
| `RULE` | `GENDER IS NULL` | NULL gender is counted separately, not merged into any declared category |
| `VALIDATION` | `FEMALE_PCT` | Female representation formula; × 100.0 ensures decimal arithmetic |
| `BUSINESS` | `WHERE EMPLOYMENT_STATUS = 'ACTIVE'` | EEO counts are active-employees-only |
| `RULE` | `HIRE_DATE <= p_as_of_date` | Future-dated hires are excluded from compliance figures |
