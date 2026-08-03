# Access Control Matrix — HRMS

`db_connection: CODE-ONLY` — see schema-catalogue.json.

**DA Agent 2 update (RC-012, E-005, E-006 — 2026-08-03):** `PKG_SECURITY.pkb` was read in the Agent 2 review pass. The grade-threshold rules below are now **CONFIRMED** from `has_permission`'s body. The LOW CONFIDENCE caveat is lifted for those sections. Two new security findings added: (1) `decrypt_ssn` has no caller permission check — see PII table below; (2) `authenticate` performs no password hash comparison — see Authentication section.

## Authorization mechanism

- Single gate function: `PKG_SECURITY.has_permission(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN`.
- Called from every form's `WHEN-NEW-FORM-INSTANCE` trigger (per README + menu comments) — authorization is **module + action** based (e.g. module='HRMS_PAYROLL', action='APPROVE'), not a named-role check like `Roles="Admin,HR"`.
- No visible ROLE or PERMISSION table exists among the 30 scanned tables — the mapping from a logged-in employee to their allowed (module, action) pairs is **not stored as inspectable data** anywhere this scan reached. It is either hard-coded in `PKG_SECURITY.pkb` (most likely, given the package's role as the sole authorization gate) or backed by a table this scan didn't discover (e.g. a `USER_ROLES`/`ROLE_PERMISSIONS` table that Layer 1 didn't extract, or entries inside the generic `LOOKUP_VALUES` table — unconfirmed, no seed data available for LOOKUP_VALUES).

## Modules referenced (from HRMS_MENU comments)

| Module | Referenced by menu | Form XML actually present in repo? |
|---|---|---|
| HRMS_EMPLOYEE | Yes | ✅ Yes |
| HRMS_PAYROLL | Yes | ✅ Yes |
| HRMS_LEAVE | Yes | ✅ Yes |
| HRMS_PERFORMANCE | Yes | ✅ Yes |
| HRMS_REPORTS | Yes | ❌ No — referenced but not shipped in this repo |
| HRMS_ADMIN | Yes ("System Parameters", "User Management" — "requires ADMIN permission") | ❌ No — referenced but not shipped in this repo |
| HRMS_LOGIN | (implicit, pre-menu) | ✅ Yes |
| HRMS_DEPARTMENT | Named in README's directory listing | ❌ No |

**Gap**: `HRMS_ADMIN` is the one place the menu source explicitly names a permission level ("ADMIN"), for System Parameters and User Management — but that form does not exist in this repo, so the ADMIN role/permission itself cannot be corroborated against any actual screen, query, or check in the scanned code. Everything else is inferred from module names only, with no named role strings (e.g. "HR_MANAGER", "PAYROLL_ADMIN") found anywhere in scanned files.

## Actions observed

| Action | Where observed |
|---|---|
| VIEW | Default value of `p_action` parameter in `has_permission` |
| (implicit CRUD actions per form: create/update/transfer/promote/terminate/rehire) | Inferred from `PKG_EMPLOYEE`'s procedure names, not confirmed as literal `p_action` string values passed to `has_permission` |
| APPROVE | `HRMS_PAYROLL`'s `BTN_APPROVE` button is described (in the payroll table cross-references) as "permission-gated" |
| ADMIN | Referenced only as a comment ("requires ADMIN permission") next to System Parameters / User Management menu items — not confirmed as a literal string constant anywhere in scanned code |

## Data-level sensitivity that access control should — but structurally cannot be confirmed to — cover

| Data | Sensitivity | Confirmed protection mechanism |
|---|---|---|
| SSN_ENCRYPTED (EMPLOYEES, EMPLOYEE_DEPENDENTS) | Critical PII | Encrypted at rest (`PKG_SECURITY.encrypt_ssn`/`decrypt_ssn` confirmed to exist); **no confirmation that decrypt_ssn itself checks the caller's permission** — the function signature takes only the encrypted value, not a caller/permission context, so any code path with EXECUTE on PKG_SECURITY could call it |
| BASE_SALARY (SALARY_RECORDS), compensation views | Sensitive financial | No column-level or row-level security found; presumably gated only at the Forms-module level (whoever can open HRMS_PAYROLL sees all salaries within it) |
| ACCOUNT_NUMBER_ENC (EMPLOYEE_BANK_ACCOUNTS) | Critical financial | Named as encrypted but no corresponding encrypt/decrypt function found in `PKG_SECURITY`'s public spec — mechanism UNKNOWN |
| Password hash | Credential | `PKG_SECURITY.hash_password` exists; self-documented as MD5 (weak) |
| AUDIT_LOG contents | Sensitive (may contain any of the above via JSON snapshot) | No access control found specific to reading AUDIT_LOG itself — presumably gated by whichever module surfaces it (unconfirmed, no "audit viewer" form found in scanned XML) |

## Confirmed authorization rules (E-005 — from PKG_SECURITY.pkb)

`has_permission` is a pure grade-band check — no named roles, no ROLE/PERMISSION junction table:

| GRADE_ID range | Access level | Details |
|---|---|---|
| ≥ 8 (Director, VP, C-Suite) | Full access — ALL modules, ALL actions | RETURN TRUE unconditionally |
| ≥ 5 (Lead, Manager, Sr. Manager) | VIEW on ALL modules | RETURN TRUE for p_action='VIEW' |
| < 5 (Individual contributors, staff) | (LEAVE, CREATE), (LEAVE, VIEW), (EMPLOYEE, VIEW) only | All other module/action combinations → RETURN FALSE |

Notes: No named roles exist anywhere in the package or schema. The code comment explicitly says "Simplified model — production should use a ROLES/PERMISSIONS junction table." ADMIN module/action referenced in HRMS_MENU comments does not appear as a distinct code path in `has_permission` — falls through to the default grade-band rules.

## Authentication defect (E-006 — CRITICAL)

`PKG_SECURITY.authenticate` queries EMPLOYEES by EMAIL and creates a session with no password hash comparison. `USER_CREDENTIALS` table is not referenced anywhere in the authenticate procedure. Current implementation accepts any password for any active employee email. This is either (a) intentional for a demo/workshop system or (b) a production security defect — confirm production state before Gate G1.

## Change records applied

| ID | Type | Summary |
|---|---|---|
| RC-012 | CORRECTED | Grade thresholds confirmed from PKG_SECURITY.pkb; confidence raised from 0.50 → 0.92 |
| E-005 | ENRICHED | Full has_permission logic documented; LOW CONFIDENCE caveat lifted |
| E-006 | ENRICHED | authenticate stub escalated — no password comparison in body |
| A-009 | ADDED | Benefits feed exports all employee+dependent PII without has_permission check |
