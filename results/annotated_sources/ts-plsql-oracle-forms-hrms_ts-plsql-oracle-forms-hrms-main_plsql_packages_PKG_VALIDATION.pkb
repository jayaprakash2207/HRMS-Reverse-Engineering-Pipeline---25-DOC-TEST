The file has been annotated. Here is a summary of every annotation inserted and the reasoning:

---

### Annotations added (13 total, zero code lines changed)

| Location | Tag | Rule documented |
|---|---|---|
| `validate_date_range` — null guard | `RULE` | Both dates must be non-null; either null makes the range invalid |
| `validate_date_range` — comparison | `RULE` | End date must be on or after start date |
| `validate_salary_for_grade` — null guard | `RULE` | Both salary and grade must be supplied before validation can run |
| `validate_salary_for_grade` — SELECT | `BUSINESS` | Query retrieves the pay band boundaries from `JOB_GRADES` for the specified grade |
| `validate_salary_for_grade` — below min | `RULE` | Salary must not fall below the grade's minimum pay band |
| `validate_salary_for_grade` — above max | `RULE` | Salary must not exceed the grade's maximum pay band |
| `validate_emp_number_format` — regex | `RULE` | Employee numbers must match `EMP-` followed by exactly 6 digits |
| `is_future_date` — comparison | `RULE` | Same-day dates are not future; only strictly later calendar days qualify |
| `is_business_day` — weekend check | `RULE` | Saturday and Sunday are never business days, unconditionally |
| `is_business_day` — SELECT | `BUSINESS` | Only active holidays (`ACTIVE_FLAG = 'Y'`) that are global or location-matched block a date |
| `is_business_day` — count check | `RULE` | A weekday is only a business day when no matching active holiday exists |
| `validate_required_fields` — table guard | `RULE` | Validation is currently implemented only for `EMPLOYEES`; all other tables pass through silently |
| `validate_required_fields` — null checks | `RULE` | Five fields are mandatory on every employee record: First Name, Last Name, Hire Date, Department, Job Title |

**Skipped (no annotation warranted):**
- `validate_email_format` and `validate_phone_format` — pure delegation to `PKG_COMMON`; no business logic visible here
- `NO_DATA_FOUND` handlers — error handling for invalid lookup keys, not an independent business rule
