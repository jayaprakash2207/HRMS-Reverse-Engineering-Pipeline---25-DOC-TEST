# Executive Summary for Review — HRMS D1 Architecture Extraction

**Verdict: PARTIAL.**  
The architectural picture, security findings, and migration guidance are trustworthy and well-evidenced. The component registry contains systematic naming errors in five of eleven packages and all six trigger entries. Three dependency edges are missing from the graph. One call flow step invents a behaviour not present in any source file. The architecture is sound; the registry is not yet reliable for automated downstream tooling.

---

## What Is Safe to Act On

The following findings are directly confirmed by spot-check source files and are safe to use in planning and remediation decisions now:

- **CRITICAL** — AES-256 SSN encryption key (`HR$ystem_3ncrypt10n_K3y_2024!!`) is a plaintext constant in `PKG_SECURITY.pkb`. Every developer with repo access can decrypt all stored employee SSNs. Key rotation is a blocking pre-migration security task independent of any other work.
- **CRITICAL** — `PKG_SECURITY.authenticate` is a stub: password hash comparison against stored credentials is not implemented. Any user who knows a valid employee email address can authenticate without the correct password in the current system.
- **SQL injection** — `PKG_EMPLOYEE.search_employees` builds dynamic SQL via string concatenation from an unsanitised `p_filter_clause` parameter. This is a full database compromise vector.
- **Circular dependency (CYCLE-01)** — `PKG_EMPLOYEE.create_employee` calls `PKG_PAYROLL.create_salary_record`; `PKG_PAYROLL.calculate_payroll` calls `PKG_EMPLOYEE.is_active`. Neither package can be independently deployed or tested. This must be broken before any service extraction begins.
- **Hire-date inconsistency (VIO-DATA-01)** — HRMS_EMPLOYEE form enforces ≤ 90 days future; `TRG_EMP_BEFORE_INSERT` DB trigger enforces ≤ **180 days**. One of these is wrong in production today. The trigger fires at the DB layer, so 90-day violations can occur via non-Forms paths. A business owner must confirm which rule is correct.
- **Partial-commit anti-pattern** — `PKG_PAYROLL.calculate_payroll` commits every 50 employees; `PKG_LEAVE.run_monthly_accrual` commits every 100. A mid-run failure leaves the system in a permanently inconsistent state with no rollback path.
- **Hard-coded 2024 tax values** — FICA wage base ($168,600) and federal tax brackets will silently produce incorrect payroll calculations for every tax year after 2024 unless a developer manually updates and redeploys the package.
- **Authentication broken at DB layer** — `TRG_EMP_INSTEAD_OF_DELETE` (BEFORE DELETE on EMPLOYEES) unconditionally raises error -20504. There is no path to delete an employee record via SQL DML. The trigger's documented workaround is to set `ACTIVE_FLAG='N'` and clear the Forms record instead.

---

## What Needs Correction Before Using the Registry

### Component Registry — Package Procedures

Five of the eleven package entries in `component-registry.json` contain procedure/function names that diverge from the spot-check source files. Authoritative correct entries are in `quality-review.md`.

| Package | Problem | Correct Count |
|---------|---------|--------------|
| PKG_COMMON | 4 entries renamed (`validate_email` → `is_valid_email`, etc.); 5 real procedures missing (`get_param_number`, `get_param_date`, `business_days_between`, `format_ssn_masked`, `format_name`); 4 phantom entries not in source | 17 |
| PKG_REPORTING | 3 wrong names (`compensation_analysis` → `compensation_summary`, etc.); 2 missing (`new_hires_report`, `eeo_compliance_report`); 2 phantom entries | 8 |
| PKG_VALIDATION | 5 wrong names; 2 missing (`validate_salary_for_grade`, `validate_emp_number_format`); 3 phantom entries | 8 |
| PKG_AUDIT | Function named `get_audit_trail`; actual name is `get_change_history` | 3 |
| PKG_SECURITY | `authenticate` return type listed as VARCHAR2; actual return type is NUMBER | 8 |

### Component Registry — Triggers

All six trigger entries in `component-registry.json` COMP-DB-TRIGGERS have wrong names or are phantom entries. The actual trigger names from `trg_audit.sql` and `trg_employees.sql` are:

| Source Trigger | Table | Event |
|----------------|-------|-------|
| TRG_SALARY_AUDIT | SALARY_RECORDS | AFTER INSERT OR UPDATE OR DELETE |
| TRG_LEAVE_REQUEST_AUDIT | LEAVE_REQUESTS | AFTER UPDATE OF STATUS (only) |
| TRG_DEPARTMENT_AUDIT | DEPARTMENTS | AFTER INSERT OR UPDATE OR DELETE |
| TRG_EMP_BEFORE_INSERT | EMPLOYEES | BEFORE INSERT |
| TRG_EMP_BEFORE_UPDATE | EMPLOYEES | BEFORE UPDATE |
| TRG_EMP_INSTEAD_OF_DELETE | EMPLOYEES | BEFORE DELETE |

Registry entries TRG_AUDIT_LOG_INSERT and TRG_NOTIFICATION_INSERT do not exist in any source file.

The registry description of TRG_EMPLOYEES_VALIDATE also claims it validates `SALARY ≥ JOB_GRADES.MIN_SALARY`. This claim is invented — it is not in any trigger body. Salary validation is in `PKG_VALIDATION.validate_salary_for_grade`.

### Dependency Graph

- PKG_REPORTING has zero outgoing edges despite declaring PKG_EMPLOYEE, PKG_PAYROLL, and PKG_COMMON as dependencies. Three edges are missing.
- `PKG_SECURITY.authenticate` calls `PKG_EMPLOYEE.set_session_context(p_username, v_emp_id)` per the spot-check body. No `PKG_SECURITY → PKG_EMPLOYEE` edge exists in the graph or in MOD-05's outbound call list.

### Call Flow

`call-flow-map.json` FLOW-02 step 7 references `TRG_EMPLOYEES_AUDIT AFTER INSERT → PKG_AUDIT.log_action`. This trigger does not exist. Employee audit logging on insert is performed by PKG_EMPLOYEE package code, not a trigger. Step 5 also misnames the trigger as TRG_EMPLOYEES_VALIDATE and invents a salary check that is not in its body.

---

## Violation Count Correction

The task-facing summary stated "6 security (2 CRITICAL), 8 architecture, 5 data, 2 ops." This is incorrect. The authoritative count from `architecture-violation-register.json`:

| Category | Count | CRITICAL | HIGH | MEDIUM | LOW |
|----------|-------|----------|------|--------|-----|
| Security | 9 | 2 (VIO-SEC-01, VIO-SEC-02) | 4 | 3 | 0 |
| Architecture | 9 | 0 | 3 | 5 | 1 |
| Data Integrity | 5 | 0 | 1 | 3 | 1 |
| Operations | 1 | 0 | 0 | 1 | 0 |
| **Total** | **24** | **2** | **8** | **12** | **2** |

---

## Decisions Required from a Human

1. **Hire-date rule:** 90 days (form trigger) or 180 days (DB trigger, confirmed from source) — which is the intended business rule? The form is stricter than the database, so direct inserts can create records that fail form validation.
2. **Authentication stub:** Is the broken authentication state in `PKG_SECURITY.authenticate` known to operations? If the system is live, there is effectively no password enforcement. Identify whether there is an undiscovered SSO/DB-auth mechanism in use (OQ-SEC-01).
3. **Missing source files:** Can `HRMS_REPORTS.xml`, `HRMS_ADMIN.xml`, USER_CREDENTIALS DDL, and DBMS_SCHEDULER job DDL be supplied? These are the four remaining source gaps.
4. **set_session_context:** `PKG_SECURITY.authenticate` calls `PKG_EMPLOYEE.set_session_context` — this procedure is not listed in PKG_EMPLOYEE's public spec in the component registry. Is it a private procedure or does it appear in the spec? This affects the DISC-011 dependency edge.

---

## Confidence Summary

| Area | Confidence | Basis |
|------|-----------|-------|
| Architecture pattern (Layered Monolith / Big Ball of Mud) | 0.95 | Well-evidenced from package structure and dependency graph |
| Security violations (VIO-SEC-01 through VIO-SEC-09) | 1.00 | All confirmed by spot-check source files |
| Module boundary decomposition | 0.90 | Clear from package/form structure |
| Call flows (FLOW-01 through FLOW-10) | 0.85 avg | FLOW-02 steps 5+7 contain trigger name errors and an invented claim |
| Component registry — procedure names | 0.60 | Five of eleven packages have naming errors vs source |
| Component registry — trigger names/events | 0.15 | Only 1 of 6 trigger entries matches source files |
| HRMS_REPORTS / HRMS_ADMIN features | 0.55 | Forms not provided; features inferred only |

---

## Recommended Next Steps

In priority order:

1. **Immediately:** Rotate the SSN encryption key and implement password hash verification in PKG_SECURITY.authenticate. These are active production security failures, not migration concerns.
2. **Before D2:** Rewrite component-registry.json COMP-DB-TRIGGERS and COMP-PKG-09/10/11 using the authoritative lists in `quality-review.md`. Add the 5 missing dependency edges to `dependency-graph.json` and regenerate the two affected Mermaid diagrams.
3. **For migration planning:** The architectural findings, violation register, risk register, strangler fig ranking, and 6-phase migration sequence are ready to use now. The procedure-level registry is not yet ready to drive automated tooling.
