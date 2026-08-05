The file already contained a substantial set of annotations from a prior pipeline run. I verified them all and added two that were missing:

- **`rehire_employee`** — `RULE:` noting that the rehire date overwrites the original hire date and clears all termination data.
- **`get_org_chart`** — `CONSTRAINT:` on the default `p_max_depth` of 10 levels and its timeout risk.

Here is a full summary of every annotation now present in the file:

| Location | Tag | Rule documented |
|---|---|---|
| `c_max_hierarchy_depth` constant | `CONSTRAINT` | Hierarchy depth capped at 15 to bound circular-ref traversal |
| `validate_dept` — query | `BUSINESS` | Only `ACTIVE_FLAG = 'Y'` departments are valid for assignment |
| `validate_dept` — IF count=0 | `RULE` | Department must exist and be active |
| `validate_dept` — RAISE | `RULE` | Inactive/non-existent department raises error |
| `validate_manager` — NULL check | `RULE` | NULL manager is valid (top-level employee) |
| `validate_manager` — query | `BUSINESS` | Only `EMPLOYMENT_STATUS = 'ACTIVE'` employees may be managers |
| `validate_manager` — IF count=0 | `RULE` | Manager must exist and be active |
| `validate_manager` — RAISE inactive | `RULE` | Inactive/non-existent manager raises error |
| `validate_manager` — circular check | `RULE` | Updating an employee must not create a circular chain |
| `validate_manager` — IF circular | `RULE` | Employee cannot directly or indirectly report to themselves |
| `validate_manager` — RAISE circular | `RULE` | Circular chain raises error |
| `create_employee` — name check | `RULE` | First and last name are mandatory at hire |
| `create_employee` — RAISE name | `RULE` | Missing name raises error |
| `create_employee` — job query | `BUSINESS` | Only active job titles (`ACTIVE_FLAG = 'Y'`) valid at hire |
| `create_employee` — RAISE job | `RULE` | Inactive/non-existent job raises error |
| `create_employee` — salary range | `RULE` | Starting salary must fall within the job grade range (soft warning, override allowed) |
| `create_employee` — location default | `VALIDATION` | Location defaults to the department's location when not provided |
| `create_employee` — salary IF | `RULE` | Salary record only created when a starting salary is explicitly supplied |
| `create_employee` — DUP_VAL | `RULE` | Duplicate employee numbers require caller retry |
| `update_employee` — exists check | `RULE` | Employee must exist before contact details can be updated |
| `update_employee` — RAISE exists | `RULE` | Non-existent employee raises error |
| `update_employee` — NVL SET | `VALIDATION` | NULL parameters preserve existing values (partial-update pattern) |
| `update_employee` — rowcount=0 | `RULE` | Zero rows after existence check signals concurrent deletion |
| `update_employee` — RAISE rowcount | `RULE` | Zero-row update raises error |
| `get_employee` — salary subquery | `BUSINESS` | Current salary = active record effective on/before today, not yet ended |
| `get_employee` — RAISE | `RULE` | Non-existent employee ID raises error |
| `get_employee_by_number` — RAISE | `RULE` | Non-existent employee number raises error |
| `search_employees` — status filter | `BUSINESS` | Status filter restricts results to specified `EMPLOYMENT_STATUS` value |
| `transfer_employee` — status check | `RULE` | Only `ACTIVE` employees may be transferred |
| `transfer_employee` — RAISE status | `RULE` | Non-active employee transfer raises error |
| `transfer_employee` — NVL defaults | `VALIDATION` | Job and location default to current values when not provided |
| `transfer_employee` — manager IF | `RULE` | New manager validated only when explicitly provided |
| `promote_employee` — salary query | `BUSINESS` | Most recent active salary record used as promotion baseline |
| `promote_employee` — CASE pct | `VALIDATION` | Change % computed only when prior salary > 0; zero/missing salary yields NULL |
| `terminate_employee` — status check | `RULE` | Already-terminated employee cannot be terminated again |
| `terminate_employee` — RAISE status | `RULE` | Re-termination raises error |
| `terminate_employee` — leave query | `BUSINESS` | Only `PENDING` leave requests identified for auto-cancellation |
| `terminate_employee` — leave IF | `RULE` | All pending leave requests auto-cancelled on termination |
| `terminate_employee` — salary UPDATE | `BUSINESS` | Only active salary records closed at termination |
| `terminate_employee` — pay elements UPDATE | `BUSINESS` | Only active pay elements deactivated at termination |
| `terminate_employee` — manager IF | `RULE` | Manager notification sent only when a manager is assigned |
| `rehire_employee` — UPDATE | `RULE` | Rehire overwrites hire date and clears termination data |
| `rehire_employee` — RAISE rowcount | `RULE` | Non-existent employee ID raises error on rehire |
| `get_direct_reports` — query | `BUSINESS` | Only `ACTIVE` employees returned as direct reports |
| `get_org_chart` — depth default | `CONSTRAINT` | Default traversal depth of 10 levels; deeper risks timeout |
| `get_org_chart` — WHERE | `BUSINESS` | Only `ACTIVE` employees included in the org chart hierarchy |
| `get_headcount_by_dept` — query | `BUSINESS` | Headcount counts employees hired on/before and not yet terminated as of the as-of date |
| `get_tenure_years` — NVL | `VALIDATION` | Active employees with no termination date use today as the tenure end point |
| `is_active` — RETURN | `RULE` | Employee is active if and only if `EMPLOYMENT_STATUS = 'ACTIVE'` |
| `validate_employee` — name check | `RULE` | Record invalid if first or last name is absent |
| `validate_employee` — hire date | `RULE` | Record invalid if hire date is absent |
| `validate_employee` — flag mismatch | `RULE` | `EMPLOYMENT_STATUS = 'ACTIVE'` with `ACTIVE_FLAG != 'Y'` is an inconsistent record |
