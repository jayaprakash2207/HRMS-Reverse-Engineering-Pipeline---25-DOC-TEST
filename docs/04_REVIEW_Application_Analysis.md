# Human Review — Application Analysis

**Reviewer:** ___________________________
**Date reviewed:** ___________________________
**Sign-off:** ___________________________

**Source files:** `results/Application_Analysis/AA_Quality_Review.md`, `results/Application_Analysis/AA_App_Extractor.md`
**Forward Engineering docs using this:** `13_SECURITY_ARCHITECTURE.md`, `15_FORWARD_ENGINEERING_SPECIFICATION.md`

---

## 1. Critical Bugs — Must Fix Before / During Migration

These bugs exist in the current Oracle HRMS system and MUST be fixed in the new system.
A senior developer must confirm each one is real by checking the source code.

### BUG-001: HEAD_OF_HOUSEHOLD Federal Tax = $0 (CRITICAL)

| Item | Detail |
|------|--------|
| Location | `PKG_PAYROLL.calculate_federal_tax` |
| Description | When `filing_status = 'HEAD_OF_HOUSEHOLD'`, the function returns 0 as federal tax. No tax bracket handles HOH status — it falls through all CASE branches with no default. |
| Impact | All HOH employees pay $0 federal tax. This is a payroll compliance violation. |
| Source file | `plsql/packages/PKG_PAYROLL.pkb` |
| Reviewer — Is this real? | |
| Reviewer — Is this intentional? | |
| Fix for new system | |

---

### BUG-002: EMPLOYEE_HISTORY Column Mismatch — ORA-00904 (CRITICAL)

| Item | Detail |
|------|--------|
| Location | `TRG_EMP_BEFORE_UPDATE` vs `01_core_tables.sql` |
| Description | The trigger references columns `CHANGE_DATE, OLD_VALUE, NEW_VALUE` but the DDL defines `EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, ...` — completely different column names. Every EMPLOYEES UPDATE raises ORA-00904 at runtime. |
| Impact | Employee record updates silently fail or error on every update |
| Source files | `schema/tables/01_core_tables.sql`, `schema/triggers/TRG_EMP_BEFORE_UPDATE` |
| Reviewer — Is this real? | |
| Reviewer — Does the current prod DB have the trigger disabled? | |
| Fix for new system | |

---

### BUG-003: rehire_employee Procedure Broken (HIGH)

| Item | Detail |
|------|--------|
| Location | `PKG_EMPLOYEE.rehire_employee` |
| Description | `TRG_EMP_BEFORE_UPDATE` raises exception -20503 when status changes from `TERMINATED` to `ACTIVE`. This is exactly what `rehire_employee` does. The trigger prevents the procedure from ever succeeding. |
| Impact | Rehiring terminated employees is impossible in the current system |
| Source files | `plsql/packages/PKG_EMPLOYEE.pkb`, trigger file |
| Reviewer — Is rehire currently possible in production? | |
| Reviewer — Is rehire needed in new system? | |
| Fix for new system | |

---

### BUG-004: Race Condition in Employee Number Generation (HIGH)

| Item | Detail |
|------|--------|
| Location | `PKG_EMPLOYEE.generate_emp_number` |
| Description | Does `SELECT MAX(emp_id) + 1 FROM EMPLOYEES` then uses that value in INSERT, with no `SELECT FOR UPDATE` or sequence. Under concurrent hire transactions, two employees can receive the same employee number. |
| Impact | Duplicate employee numbers in high-concurrency hire scenarios |
| Source file | `plsql/packages/PKG_EMPLOYEE.pkb` |
| Reviewer — Has this caused duplicates in production? | |
| Fix for new system | Use DB sequence or UUID |

---

### BUG-005: Hardcoded AES-256 Encryption Key (CRITICAL SECURITY)

| Item | Detail |
|------|--------|
| Location | `PKG_SECURITY` |
| Description | AES-256 encryption key is hardcoded as `'HRMS_AES256_KEY_2024'` in the package body. Anyone with SELECT access to the package source can decrypt all employee data. |
| Impact | All encrypted fields (bank accounts, national IDs, etc.) are effectively unencrypted |
| Source file | `plsql/packages/PKG_SECURITY.pkb` |
| Reviewer — Confirmed? | |
| Fix for new system | Use HashiCorp Vault or cloud KMS for key management |

---

## 2. Quality Findings — Confirm These

| Finding ID | Description | Severity | Reviewer Confirmation |
|------------|------------|----------|-----------------------|
| Q-001 | No unit tests or test harness in codebase | HIGH | |
| Q-002 | No error handling in PKG_INTEGRATION — failures silently swallowed | HIGH | |
| Q-003 | SMTP called synchronously in payroll loop — 5000 employees = 5000 blocking SMTP calls | HIGH | |
| Q-004 | PKG_REPORTING.refresh_reporting_tables is a stub — no implementation | HIGH | |
| Q-005 | NACHA file generation is not implemented — only comments describing intent | HIGH | |
| Q-006 | No pagination in any query — full table scans likely on large EMPLOYEES table | MEDIUM | |
| Q-007 | Inconsistent date format handling across packages | MEDIUM | |
| Q-008 | PKG_EMPLOYEE has 20+ procedures — violates single responsibility principle | MEDIUM | |
| Q-009 | No logging framework — only AUDIT_LOG table, no structured application logs | MEDIUM | |
| Q-010 | Dead code: several commented-out procedures in PKG_EMPLOYEE | LOW | |

---

## 3. Security Architecture Review

Open [results/ForwardEngineering_Docs/13_SECURITY_ARCHITECTURE.md](../results/ForwardEngineering_Docs/13_SECURITY_ARCHITECTURE.md):

| Section | Complete? | Accurate? | Reviewer Notes |
|---------|-----------|-----------|----------------|
| Current security model described | | | |
| Target security architecture defined | | | |
| JWT / OAuth2 strategy | | | |
| PII encryption approach | | | |
| Audit trail requirements | | | |
| Hardcoded key remediation plan | | | |

---

## 4. Component Registry — Verify Key Components

These components were identified by the AA track. Confirm health status:

| Component | Package | AI Health Status | Reviewer Confirmed Health |
|-----------|---------|-----------------|--------------------------|
| hire_employee | PKG_EMPLOYEE | HEALTHY | |
| terminate_employee | PKG_EMPLOYEE | HEALTHY | |
| rehire_employee | PKG_EMPLOYEE | **BROKEN** | |
| generate_emp_number | PKG_EMPLOYEE | HEALTHY (race condition noted) | |
| calculate_federal_tax | PKG_PAYROLL | **CRITICAL BUG (HOH)** | |
| process_payroll | PKG_PAYROLL | HEALTHY (slow, synchronous) | |
| submit_leave_request | PKG_LEAVE | HEALTHY | |
| approve_leave | PKG_LEAVE | HEALTHY | |
| authenticate | PKG_SECURITY | HEALTHY | |
| encrypt_data | PKG_SECURITY | HEALTHY (hardcoded key) | |
| import_time_attendance | PKG_INTEGRATION | PARTIAL (missing target table) | |
| send_notification | PKG_NOTIFICATIONS | HEALTHY (synchronous) | |
| refresh_reporting_tables | PKG_REPORTING | **STUB — not implemented** | |

---

## 5. Forward Engineering Specification Review

Open [results/ForwardEngineering_Docs/15_FORWARD_ENGINEERING_SPECIFICATION.md](../results/ForwardEngineering_Docs/15_FORWARD_ENGINEERING_SPECIFICATION.md):

| Section | Complete? | Approved? | Reviewer Notes |
|---------|-----------|-----------|----------------|
| Migration strategy (Strangler Fig) | | | |
| Phase 1 scope and acceptance criteria | | | |
| Phase 2 scope and acceptance criteria | | | |
| Phase 3 scope and acceptance criteria | | | |
| Critical defect fix plan | | | |
| Data migration strategy | | | |
| Cutover and rollback plan | | | |

---

## 6. Open Questions for Senior Developer

1. Is the HOH tax = $0 bug present in the current production database (not just in source files)?
2. Has the EMPLOYEE_HISTORY trigger ever been triggered in production, or is it disabled?
3. Are there any additional PL/SQL packages, triggers, or views not captured in the 42 source files?
4. What is the current Oracle HRMS production data volume? (Number of employees, payroll runs, leave records)
5. Are there any external systems reading directly from the Oracle DB that would break at cutover?
6. Is there a current Oracle HRMS test environment with realistic data?
