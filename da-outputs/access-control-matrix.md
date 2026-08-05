# HRMS Access Control Matrix

**Schema:** HRMS  **Extracted:** 2026-08-04  **Method:** CODE-ONLY  
**Source:** PKG_SECURITY.has_permission, PKG_SECURITY.authenticate, PKG_SECURITY.is_session_valid, Oracle Forms permission blocks

---

## Access Model Overview

The HRMS uses a **grade-based permission model**. Access is determined by the employee's current `JOB_TITLES.GRADE_ID` (integer 1-10), retrieved via a 2-table JOIN of EMPLOYEES→JOB_TITLES. There are no named roles or role-assignment tables. Permissions are evaluated at runtime in `PKG_SECURITY.has_permission` using hardcoded grade thresholds. **DA Agent 2 correction:** The column used is `j.GRADE_ID` from JOB_TITLES — not `g.GRADE_LEVEL` from JOB_GRADES. The column `GRADE_LEVEL` does not exist in the JOB_GRADES DDL; that table's columns are GRADE_ID, GRADE_CODE, GRADE_NAME, MIN_SALARY, MAX_SALARY, OVERTIME_ELIGIBLE. The permission code joins only EMPLOYEES→JOB_TITLES; there is no JOIN to JOB_GRADES at runtime.

**Session validity:** Sessions expire 30 minutes after `LOGIN_TIME`. No sliding-window refresh. Expired sessions are rejected by `PKG_SECURITY.is_session_valid` and also enforced by the Oracle Forms `check_session` procedure in `HRMS_COMMON_LIB`.

---

## Grade-Level Permission Tiers

| Grade Level | Tier | Access Summary |
|---|---|---|
| 1-4 | Standard Employee | Own leave requests, own profile (view), own pay stubs (view) |
| 5-7 | Manager / Senior Staff | All of Standard + view all employee data, approve leave for team, submit/approve performance reviews |
| 8-10 | Director / VP / C-Suite | Full system access — all modules read/write including payroll approval, system configuration, and integration exports |

---

## Module-Level Matrix

| Module / Function | Grade 1-4 | Grade 5-7 | Grade 8-10 | Notes |
|---|---|---|---|---|
| EMPLOYEE - View own record | YES | YES | YES | |
| EMPLOYEE - View other records | NO | YES | YES | Grade >= 5 |
| EMPLOYEE - Create new employee | NO | NO | YES | Grade >= 8 |
| EMPLOYEE - Update employee | NO | NO | YES | Grade >= 8 |
| EMPLOYEE - Terminate employee | NO | NO | YES | Grade >= 8 |
| EMPLOYEE - Rehire employee | NO | NO | YES | Grade >= 8 |
| EMPLOYEE - Transfer employee | NO | NO | YES | Grade >= 8 |
| EMPLOYEE - Promote employee | NO | NO | YES | Grade >= 8 |
| EMPLOYEE - Search employees | YES | YES | YES | SQL injection vulnerability in PKG_EMPLOYEE.search_employees |
| LEAVE - Submit own request | YES | YES | YES | All grades |
| LEAVE - View own requests | YES | YES | YES | All grades; HRMS_LEAVE form DEFAULT_WHERE filters to current_emp_id |
| LEAVE - Approve / Reject leave | NO | YES | YES | Grade >= 5; must be assigned approver |
| LEAVE - Run monthly accrual | NO | NO | YES | Grade >= 8 |
| LEAVE - Process carryover | NO | NO | YES | Grade >= 8 |
| PAYROLL - View own pay stub | YES | YES | YES | |
| PAYROLL - View all payroll data | NO | YES | YES | Grade >= 5 |
| PAYROLL - Calculate payroll run | NO | NO | YES | Grade >= 8; HRMS_PAYROLL form BTN_CALCULATE requires PENDING status |
| PAYROLL - Approve payroll run | NO | NO | YES | Grade >= 8; PKG_SECURITY.has_permission(...,'PAYROLL','APPROVE'); HRMS_PAYROLL form BTN_APPROVE |
| PAYROLL - Reverse payroll run | NO | NO | YES | Grade >= 8; NOTE: no status check in reverse_payroll - any run can be reversed |
| PERFORMANCE - View own review | YES | YES | YES | |
| PERFORMANCE - Submit self-assessment | YES | YES | YES | Employee on the review |
| PERFORMANCE - Submit manager review | NO | YES | YES | Must be assigned reviewer |
| PERFORMANCE - Create review cycle | NO | NO | YES | Grade >= 8 |
| PERFORMANCE - Acknowledge review | YES | YES | YES | Employee on the review |
| REPORTING - View standard reports | NO | YES | YES | Grade >= 5; enforced via PKG_REPORTING procedures |
| REPORTING - EEO compliance report | NO | NO | YES | Grade >= 8 |
| REPORTING - Direct SELECT on RPT_* tables | UNKNOWN | UNKNOWN | UNKNOWN | *ADDED from PKG_REPORTING.pkb analysis — no PKG_SECURITY check exists on the RPT_* tables themselves. PKG_REPORTING.has_permission gates the package procedures, but Oracle Reports (.rdf) or BI tools querying RPT_* tables directly bypass all PL/SQL access checks. If Oracle schema-level GRANT/REVOKE controls are not in place, any Oracle user with connect access can read RPT_NEW_HIRES (contains salary PII) and RPT_EEO_COMPLIANCE. Schema-level grants not visible in recovered source files.* |
| INTEGRATION - GL export | NO | NO | YES | Grade >= 8; PKG_INTEGRATION.generate_gl_journal |
| INTEGRATION - ADP benefits export | NO | NO | YES | Grade >= 8 |
| SECURITY - Encrypt/decrypt SSN | NO | NO | YES | PKG_SECURITY.encrypt_ssn / decrypt_ssn; key hard-coded in package body |
| SYSTEM PARAMS - Read | YES | YES | YES | PKG_COMMON.get_param - no access check |
| SYSTEM PARAMS - Update | NO | NO | YES | PKG_COMMON.set_param - EDITABLE_FLAG='Y' guard only; no grade check |
| AUDIT LOG - View | NO | NO | YES | Grade >= 8 |
| AUDIT LOG - Purge | NO | NO | YES | PKG_AUDIT.purge_old_records |
| EMPLOYEE_DEPENDENTS - View/Edit | NO | NO | YES | *ADDED by DA Agent 2 — no explicit access row existed. Contains SSN, DOB, full name (PII). Governed by general EMPLOYEE module Grade ≥ 8 rule; Grade 5-7 VIEW access is ambiguous.* |
| EMERGENCY_CONTACTS - View/Edit | YES (own) | YES | YES | *ADDED by DA Agent 2 — no explicit access row existed. Contains third-party name, phone, email (PII). Likely Grade ≥ 5 to view all; Grade ≥ 8 to modify. Not enforced by PKG_SECURITY.* |
| EMPLOYEE_BANK_ACCOUNTS - View/Edit | NO | NO | YES | *ADDED by DA Agent 2 — no explicit access row existed. Contains encrypted account number (PII) and plain-text ROUTING_NUMBER. Grade ≥ 8 implied by payroll access model; no explicit PKG_SECURITY check found.* |
| EMPLOYEE_TAX_INFO - View/Edit | NO | NO | YES | *ADDED by DA Agent 2 — no explicit access row existed. Contains W-4 filing status, allowances, withholding election (PII). Grade ≥ 8 implied; no explicit PKG_SECURITY check found.* |

---

## PKG_SECURITY.has_permission Logic (Extracted)

```
FUNCTION has_permission(p_emp_id, p_module, p_action) RETURN BOOLEAN IS
  v_grade  NUMBER;
BEGIN
  -- CORRECTED by DA Agent 2: actual code is a 2-table JOIN (EMPLOYEES→JOB_TITLES only).
  -- The prior version incorrectly showed a 3-table JOIN using g.GRADE_LEVEL from JOB_GRADES.
  -- GRADE_LEVEL does not exist in the JOB_GRADES DDL. The actual column is j.GRADE_ID.
  SELECT j.GRADE_ID INTO v_grade
  FROM EMPLOYEES e JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID
  WHERE e.EMP_ID = p_emp_id AND e.EMPLOYMENT_STATUS = 'ACTIVE';

  -- Grade >= 8: full access
  IF v_grade >= 8 THEN RETURN TRUE; END IF;

  -- Grade >= 5: VIEW all modules
  IF v_grade >= 5 AND p_action = 'VIEW' THEN RETURN TRUE; END IF;

  -- Any grade: own leave and own employee view
  IF p_module = 'LEAVE'    AND p_action IN ('CREATE','VIEW') THEN RETURN TRUE; END IF;
  IF p_module = 'EMPLOYEE' AND p_action = 'VIEW'             THEN RETURN TRUE; END IF;

  RETURN FALSE;
END;
```

**Note:** The `PAYROLL APPROVE` check in `HRMS_PAYROLL.xml` calls `PKG_SECURITY.has_permission(...,'PAYROLL','APPROVE')`. Under the logic above, this only passes for Grade >= 8. Grade 5-7 managers cannot approve payroll.

---

## Oracle Forms Layer Enforcement

The Oracle Forms UI enforces additional access restrictions independent of PKG_SECURITY:

| Form | Restriction |
|---|---|
| HRMS_EMPLOYEE | SALARY block: `InsertAllowed=No`, `UpdateAllowed=No` — salary changes must go through a dedicated flow |
| HRMS_EMPLOYEE | EMP_HISTORY block: `InsertAllowed=No`, `UpdateAllowed=No`, `DeleteAllowed=No` — read-only |
| HRMS_LEAVE | TP_MY_REQUESTS tab: `DEFAULT_WHERE = EMP_ID = :GLOBAL.current_emp_id` — employees only see their own requests |
| HRMS_PAYROLL | BTN_CALCULATE: disabled unless `PAYROLL_RUNS.STATUS = 'PENDING'` |
| HRMS_PAYROLL | BTN_APPROVE: requires `PKG_SECURITY.has_permission(...,'PAYROLL','APPROVE') = TRUE` |
| HRMS_PERFORMANCE | PERFORMANCE_REVIEW block: `UpdateAllowed` set dynamically based on review status |
| HRMS_LOGIN | No lockout mechanism. Password transmitted in cleartext variable. |

---

## Known Security Weaknesses

| ID | Severity | Issue |
|---|---|---|
| SEC-01 | CRITICAL | MD5 password hashing in PKG_SECURITY.hash_password. MD5 is broken for password storage. |
| SEC-02 | CRITICAL | SQL injection in PKG_EMPLOYEE.search_employees (p_last_name, p_first_name concatenated into dynamic SQL). |
| SEC-03 | CRITICAL | AES-256 encryption key hard-coded as string literal in PKG_SECURITY: `HR$ystem_3ncrypt10n_K3y_2024!!` |
| SEC-04 | HIGH | No account lockout after failed login attempts in PKG_SECURITY.authenticate. |
| SEC-05 | HIGH | FTP credentials stored cleartext in SYSTEM_PARAMETERS (keys FTP_USERNAME, FTP_PASSWORD). |
| SEC-06 | HIGH | Session timeout is 30 min from LOGIN_TIME (no sliding window). Active users are abruptly timed out. |
| SEC-07 | MEDIUM | HRMS_LOGIN form passes password in cleartext Oracle Forms variable (no hashing at client). |
| SEC-08 | MEDIUM | PKG_SECURITY.authenticate stub: on TOO_MANY_ROWS exception selects `MIN(EMP_ID)` as fallback — could authenticate as wrong user. |
| SEC-09 | MEDIUM | SYSTEM_PARAMETERS.PARAM_VALUE has no access control check in `get_param` — any authenticated session can read all parameters including credentials. |
| SEC-10 | LOW | SMTP connection to port 25 (no TLS) in PKG_NOTIFICATION.process_queue. Notification content transmitted in cleartext. |
