The file has been annotated. Here is a summary of every annotation inserted and its rationale:

---

### `validate_email`

| Tag | Location | Description |
|-----|----------|-------------|
| `RULE` | `IF p_email IS NULL` | Email is optional — NULL bypasses all format checks |
| `RULE` | `IF v_at_pos = 0 OR ...` | The `@` symbol must exist, must not be first, must not be last — enforces non-empty local-part and domain |
| `RULE` | `IF v_dot_pos = 0 OR ...` | The domain must contain a dot, which must not immediately follow `@` and must not be the trailing character — enforces a valid TLD |

---

### `validate_phone`

| Tag | Location | Description |
|-----|----------|-------------|
| `RULE` | `IF p_phone IS NULL` | Phone is optional — NULL is valid |
| `CONSTRAINT` | `IF LENGTH(v_digits) NOT IN (10, 11)` | Valid US phone must be exactly 10 digits (no country code) or 11 digits (with leading country code) |

---

### `validate_ssn`

| Tag | Location | Description |
|-----|----------|-------------|
| `RULE` | `IF p_ssn IS NULL` | SSN is optional — NULL is valid |
| `CONSTRAINT` | `IF LENGTH(v_digits) != 9` | After stripping dashes, exactly 9 digits are required |
| `RULE` | `IF SUBSTR(...) = '000' OR ...` | All three SSN segments (area, group, serial) must have at least one non-zero digit, per SSA issuance rules |

---

### `validate_date_not_future`

| Tag | Location | Description |
|-----|----------|-------------|
| `RULE` | `RETURN p_date IS NULL OR ...` | Date must not be in the future; today or any prior date is accepted; NULL bypasses the check |

---

### `validate_salary_range`

| Tag | Location | Description |
|-----|----------|-------------|
| `RULE` | `IF p_salary IS NULL OR p_grade_id IS NULL` | Both salary and grade ID must be present before the range check runs |
| `BUSINESS` | `SELECT ... FROM JOB_GRADES WHERE GRADE_ID = p_grade_id` | Allowable pay bounds are driven by the employee's job grade, sourced from the `JOB_GRADES` reference table |
| `RULE` | `IF p_salary < v_min` | Salary must meet the grade's minimum pay floor |
| `RULE` | `ELSIF p_salary > v_max` | Salary must not exceed the grade's maximum pay ceiling |
