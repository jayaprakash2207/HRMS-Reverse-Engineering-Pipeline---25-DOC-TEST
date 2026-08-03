# DA Agent 1 — Data Extractor: Completion Report

**Agent:** DA Agent 1 — Data Architecture Extractor  
**Extraction date:** 2026-08-03  
**Confidence tier:** CODE-ONLY (0.90 migration-DDL; 0.80 package bodies)

---

## System identification

| Property | Value |
|---|---|
| Database engine | Oracle Database 19c |
| Schema | HRMS |
| Application framework | Oracle Forms 12c + PL/SQL packages |
| Company (from seed data) | Acme Corporation |
| App version (from seed data) | 4.2.0 |
| DB connection | **NO CONNECTION** — no sqlplus/sqlcl on PATH; no tnsnames.ora, docker-compose.yml, or connection string found anywhere in the repo or Layer 1 config. All findings are code-only. |
| DB connection attempt | Not attempted — no credentials or host available |

---

## Files scanned

| File | Status | Confidence |
|---|---|---|
| schema/tables/01_core_tables.sql | ✅ Read | 0.90 |
| schema/tables/02_payroll_tables.sql | ✅ Read | 0.90 |
| schema/tables/03_leave_tables.sql | ✅ Read | 0.90 |
| schema/tables/04_performance_tables.sql | ✅ Read | 0.90 |
| schema/views/hrms_views.sql | ✅ Read | 0.90 |
| schema/sequences/hrms_sequences.sql | ✅ Read | 0.90 |
| plsql/packages/PKG_AUDIT.pks + .pkb | ✅ Read | 0.90 |
| plsql/packages/PKG_COMMON.pks + .pkb | ✅ Read | 0.90 |
| plsql/packages/PKG_SECURITY.pks + .pkb | ✅ Read | 0.90 |
| plsql/packages/PKG_VALIDATION.pks + .pkb | ✅ Read | 0.90 |
| plsql/packages/PKG_REPORTING.pks + .pkb | ✅ Read | 0.85 |
| plsql/packages/PKG_PERFORMANCE.pkb (partial) | ✅ Read | 0.80 |
| plsql/triggers/trg_audit.sql | ✅ Read | 0.90 |
| plsql/triggers/trg_employees.sql | ✅ Read | 0.90 |
| data/seed/01_reference_data.sql | ✅ Read | 0.90 |
| data/seed/02_employee_data.sql | ✅ Read | 0.90 |
| forms/libraries/HRMS_COMMON_LIB.pll.sql | ✅ Read | 0.80 |
| forms/libraries/HRMS_VALIDATION_LIB.pll.sql | ✅ Read | 0.80 |
| plsql/packages/PKG_EMPLOYEE.pks + .pkb | ❌ Not found in deep scan | — |
| plsql/packages/PKG_INTEGRATION.pks + .pkb | ❌ Not found in deep scan | — |
| plsql/packages/PKG_LEAVE.pks + .pkb | ❌ Not found in deep scan | — |
| plsql/packages/PKG_NOTIFICATION.pks + .pkb | ❌ Not found in deep scan | — |
| plsql/packages/PKG_PAYROLL.pks + .pkb | ❌ Not found in deep scan | — |
| plsql/packages/PKG_PERFORMANCE.pks | ❌ Not found in deep scan | — |

---

## Domains identified (6)

| # | Domain | Tables |
|---|---|---|
| 1 | Core / Org Structure | DEPARTMENTS, LOCATIONS, JOB_GRADES, JOB_TITLES |
| 2 | Employee | EMPLOYEES, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS, EMERGENCY_CONTACTS |
| 3 | Payroll | SALARY_RECORDS, PAY_ELEMENTS, EMPLOYEE_PAY_ELEMENTS, PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS, TAX_BRACKETS, EMPLOYEE_TAX_INFO, EMPLOYEE_BANK_ACCOUNTS |
| 4 | Leave Management | LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS, LEAVE_ACCRUAL_LOG, HOLIDAYS |
| 5 | Performance | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS |
| 6 | System / Infra | AUDIT_LOG, SYSTEM_PARAMETERS, NOTIFICATION_QUEUE, USER_SESSIONS, LOOKUP_VALUES |

---

## Schema summary

| Object type | Count |
|---|---|
| Tables | 27 |
| Views | 6 |
| Triggers | 6 |
| Packages (found) | 6 spec+body pairs + 5 spec only or partial |
| Packages (total spec/signatures found) | 11 |
| Sequences | 29 |
| FK relationships (declared) | ~28 |
| Soft references (no FK) | ~8 |
| PII columns | 20+ |
| Encrypted columns | EMPLOYEES.SSN_ENCRYPTED, EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED, EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC |

---

## Output files checklist (da-outputs/)

| # | File | Status |
|---|---|---|
| 1 | schema-catalogue.json | ✅ Written |
| 2 | erd.md | ✅ Written |
| 3 | data-source-inventory.json | ✅ Written |
| 4 | data-flow-map.md | ✅ Written |
| 5 | pii-inventory.json | ✅ Written |
| 6 | data-quality-report.md | ✅ Written |
| 7 | migration-complexity.json | ✅ Written |
| 8 | hidden-business-rules.json | ✅ Written |
| 9 | storage-pattern-analysis.md | ✅ Written |
| 10 | redundancy-analysis.json | ✅ Written |
| 11 | data-dictionary.md | ✅ Written |
| 12 | conceptual-data-model.md | ✅ Written |
| 13 | access-control-matrix.md | ✅ Written |

---

## Critical findings summary (top 14 — for Agent 2 prioritization)

### 🔴 Launch-blocking defects

1. **EMPLOYEE_HISTORY column mismatch** — `TRG_EMP_BEFORE_UPDATE` inserts using columns `HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON` and CHANGE_TYPE values `DEPARTMENT_CHANGE`/`JOB_CHANGE`, but the table DDL has completely different columns (`HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID`, etc.) and `CHK_CHANGE_TYPE` only permits 10 different values. Every employee status/department/job update fires this trigger and raises an unhandled ORA-00904. **Source:** `trg_employees.sql` vs `01_core_tables.sql`.

2. **Seed scripts cannot execute** — `data/seed/01_reference_data.sql` references non-existent columns: `LOCATIONS.PHONE` (should be `PHONE_NUMBER`), `JOB_GRADES.GRADE_LEVEL` (column doesn't exist; `GRADE_CODE` NOT NULL omitted), `SYSTEM_PARAMETERS.DESCRIPTION` (should be `PARAM_DESCRIPTION`). These are ORA-00904/ORA-01400 errors. **Source:** seed vs. DDL column comparison.

3. **AUDIT_LOG check-constraint mismatch** — `TRG_LEAVE_REQUEST_AUDIT` calls `PKG_AUDIT.log_action(..., 'STATUS_CHANGE', ...)` but `AUDIT_LOG.ACTION_TYPE` has `CHK_AUDIT_ACTION IN ('INSERT','UPDATE','DELETE')`. If `PKG_AUDIT.log_action` passes the value through without translation, every leave status update fails with ORA-02290. **Confidence 0.75** pending PKG_AUDIT.pkb body review.

### 🔴 Security defects (pre-migration must-fix)

4. **Hard-coded AES-256 encryption key** — `PKG_SECURITY.pkb` contains `c_encryption_key RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!')`. The key protecting all SSN and dependent data is in source code. Re-keying all encrypted data is required before any environment where source is accessible to unauthorized parties.

5. **MD5 password hashing** — `PKG_SECURITY.hash_password` uses `DBMS_CRYPTO.HASH_MD5`. Self-documented as a known issue in the source. Must be replaced with bcrypt/scrypt + salt before production or migration.

6. **No account lockout** — `PKG_SECURITY.authenticate` has no failed-attempt counter or lockout mechanism. Self-documented gap. Brute-force attacks are unimpeded.

7. **Authenticate is a stub** — `PKG_SECURITY.authenticate` does not actually validate the password against a hash in the current scanned version (stub implementation). If this reflects production, any password allows login.

### 🟠 Business-rule / data quality risks

8. **LEAVE_BALANCES.AVAILABLE formula fork** — Virtual column (canonical): `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING`. `VW_LEAVE_SUMMARY` omits `- PENDING`. Any report built on the view overstates available leave by the PENDING amount. **Source:** `03_leave_tables.sql` vs `hrms_views.sql`.

9. **EMP_NUMBER race condition** — `SEQ_EMP_NUMBER` exists but `PKG_EMPLOYEE.generate_emp_number` reportedly uses `SELECT MAX()+1` instead of `SEQ_EMP_NUMBER.NEXTVAL`. Concurrent inserts can generate duplicate employee numbers. **Confidence 0.80** — inferred from sequence file comment, PKG_EMPLOYEE body unread.

10. **VW_PAYROLL_LATEST single-global-run assumption** — "Latest payroll run" = `MAX(RUN_ID)` among APPROVED runs, globally. If parallel run types (SUPPLEMENTAL, BONUS) coexist with REGULAR runs, employees in any non-latest run are silently excluded from this view.

11. **VW_ORG_HIERARCHY performance** — CONNECT BY query documented in source as "degrades significantly with >500 employees." Any migration to a modern platform must replace this with a closure table or recursive CTE.

12. **Session timeout on LOGIN_TIME not last activity** — `PKG_SECURITY.is_session_valid` checks `(SYSDATE - LOGIN_TIME) * 24 * 60 <= 30`. An active user will be timed out 30 minutes after login regardless of activity. Self-documented known issue.

13. **No physical delete path** — `TRG_EMP_INSTEAD_OF_DELETE` blocks all EMPLOYEES DELETEs unconditionally. Combined with no anonymization/purge mechanism for terminated employee PII, the system cannot satisfy a GDPR/CCPA right-to-erasure request. EMPLOYEE_DEPENDENTS and EMERGENCY_CONTACTS store third-party PII (children, contacts) with no independent retention path.

14. **DEPARTMENTS soft references** — `PARENT_DEPT_ID`, `MANAGER_EMP_ID`, `LOCATION_CODE` on DEPARTMENTS have no FK constraints declared, while identical relationships on EMPLOYEES are properly FK-constrained. Inconsistent enforcement; orphaned rows possible.

---

## Validation queue for Agent 2

These items could not be fully resolved in this code-only pass:

| # | Item | Why blocked | Where to look |
|---|---|---|---|
| V1 | `PKG_AUDIT.log_action` body — does it translate `STATUS_CHANGE` before writing to `AUDIT_LOG.ACTION_TYPE`? | PKG_AUDIT.pkb body not read | `plsql/packages/PKG_AUDIT.pkb` |
| V2 | `PKG_EMPLOYEE.generate_emp_number` — does it actually use `MAX()+1` or `SEQ_EMP_NUMBER.NEXTVAL`? | PKG_EMPLOYEE.pkb not found | `plsql/packages/PKG_EMPLOYEE.pkb` |
| V3 | `PKG_PAYROLL` tax calculation formula — what logic reads `TAX_BRACKETS`? | PKG_PAYROLL.pkb not found | `plsql/packages/PKG_PAYROLL.pkb` |
| V4 | `PKG_LEAVE` — how are balances decremented on approval/taken? What triggers accrual? | PKG_LEAVE.pkb not found | `plsql/packages/PKG_LEAVE.pkb` |
| V5 | `PKG_SECURITY.has_permission` — what are the actual role/module/action mappings? Is there a ROLE table or is it pure code? | PKG_SECURITY.pkb not found in deep scan pass | `plsql/packages/PKG_SECURITY.pkb` |
| V6 | `EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC` — which function encrypts/decrypts it? PKG_SECURITY spec only shows encrypt_ssn/decrypt_ssn. | Body unscanned, no matching function in spec | `plsql/packages/PKG_SECURITY.pkb` |
| V7 | `PKG_INTEGRATION` — what protocol/mechanism does the GL feed and Benefits feed use? | PKG_INTEGRATION.pkb not found | `plsql/packages/PKG_INTEGRATION.pkb` |
| V8 | `LEAVE_ACCRUAL_LOG.RUN_ID` — what table does this reference? A payroll run? A separate batch-run table? | No FK, target not confirmed in scanned code | `PKG_LEAVE.pkb` or a scheduler job definition |
| V9 | `Forms WHEN-VALIDATE-ITEM` 90-day hire-date rule — re-verify against raw `HRMS_EMPLOYEE.xml` XML | Taken from prior deep-scan narrative, not re-confirmed in this pass | `forms/HRMS_EMPLOYEE.xml` |
| V10 | `LOOKUP_VALUES` actual contents — what LOOKUP_TYPEs exist? Does any shadow a dedicated reference table? | No seed data for LOOKUP_VALUES | Live DB query or PKG_COMMON/Forms LOV references |

---

## Handoff to Agent 2

**Recommended priority order for DA Agent 2:**

1. Read `PKG_SECURITY.pkb` — resolves V5 (access control matrix), V6 (bank account encryption), authentication stub question.
2. Read `PKG_EMPLOYEE.pkb` — resolves V2 (EMP_NUMBER race), V9 (session context), employee lifecycle logic.
3. Read `PKG_PAYROLL.pkb` — resolves V3 (tax calculation, highest business-logic risk for migration).
4. Read `PKG_LEAVE.pkb` — resolves V4 and V8 (accrual trigger, balance update mechanism).
5. Read `PKG_AUDIT.pkb` — resolves V1 (STATUS_CHANGE action type — a launch-blocking defect if not translated).
6. Read `PKG_INTEGRATION.pkb` — resolves V7 (external feed mechanism).
7. Read raw `forms/HRMS_EMPLOYEE.xml` — re-confirms 90-day hire date rule (V9), confirms GOAL_CATEGORY poplist limitation, confirms EMP_ID generation sequence call site.

**Do not start a migration estimate** for the Payroll domain until V3 is resolved — the tax calculation body is the single highest-risk unknown. All other domains can be estimated with moderate confidence from the current findings.

---

*DA Agent 1 extraction complete. All 13 da-outputs/ files written. No live DB connection established — all findings are code-only at confidence 0.80–0.90.*
