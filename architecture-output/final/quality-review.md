# Quality Review — D1 Application Architecture Extraction (HRMS v4.2)

**Reviewed artifacts:** `results/D1-application-architecture/` (20 files)  
**Spot-check source files used:** PKG_AUDIT.pkb, PKG_COMMON.pkb, PKG_SECURITY.pkb, PKG_VALIDATION.pkb, PKG_REPORTING.pkb, PKG_PERFORMANCE.pkb, HRMS_EMPLOYEE.xml, HRMS_LEAVE.xml, HRMS_LOGIN.xml, HRMS_PAYROLL.xml, HRMS_PERFORMANCE.xml, HRMS_COMMON_LIB.pll.sql, HRMS_VALIDATION_LIB.pll.sql, trg_audit.sql, trg_employees.sql  
**Review date:** 2026-08-03

---

## Stated Totals (from system-inventory.json)

| Item | Claimed | Spot-Check Verified |
|------|---------|---------------------|
| PL/SQL packages | 11 | 11 ✓ |
| Procedures + functions (total) | 130 | 111 in registry — **DISC-001** (19-entry gap) |
| Oracle Forms | 8 (6 provided, 2 referenced) | 8 ✓ |
| PLL libraries | 2 | 2 ✓ |
| DB tables | 26 | Not contradicted by spot-check |
| DB views | 6 | 6 ✓ |
| DB triggers | 6 | 6 ✓ (count correct; **all names wrong except 1 — DISC-009**) |
| DB sequences | 29 | 6 directly confirmed; 23 not contradicted |
| External integrations | 3 | 3 ✓ |

**Violation count:** 24 claimed, 24 confirmed by counting VIO-SEC-01…09 + VIO-ARCH-01…09 + VIO-DATA-01…05 + VIO-OPS-01 = 24 ✓.  
The task-facing summary stated "6 security (2 CRITICAL), 8 architecture, 5 data, 2 ops" which sums to 21 and is wrong by every category. Authoritative breakdown from the register: **9 security, 9 architecture, 5 data integrity, 1 operations = 24**. Mark as **DISC-002**.

---

## Overall Verdict: **PARTIAL**

The extraction's core findings — architecture patterns, security violations, circular dependency, call flows, module boundaries, migration sequencing — are all directly evidenced from source and accurate. The verdict is PARTIAL, not PASS, because:

1. **Trigger registry accuracy failure (DISC-009):** 5 of 6 trigger entries have wrong names; 2 entries are phantom (not in any source file); 1 real trigger is absent. The register was not cross-checked against the actual `.sql` source files.
2. **Invented trigger behaviour (DISC-010):** The registry claims TRG_EMPLOYEES_VALIDATE validates `SALARY ≥ JOB_GRADES.MIN_SALARY` — this does not appear in the actual trigger body (`TRG_EMP_BEFORE_INSERT`). Salary validation is in `PKG_VALIDATION.validate_salary_for_grade`, not in any trigger.
3. **Missing dependency edge (DISC-011):** `PKG_SECURITY.authenticate` calls `PKG_EMPLOYEE.set_session_context(p_username, v_emp_id)` per the spot-check body. This edge is absent from `dependency-graph.json` and from `module-boundary-map.json` MOD-05 outbound calls. The dependency graph is incomplete.
4. **Phantom trigger in call flow (DISC-012):** `call-flow-map.json` FLOW-02 step 7 references `TRG_EMPLOYEES_AUDIT AFTER INSERT → PKG_AUDIT.log_action` — no such trigger exists in any source file. FLOW-02 step 5 also invents the salary validation claim.
5. **Component registry procedure naming (DISC-003 through DISC-008):** Five of eleven packages contain wrong names, missing entries, or phantom entries against the spot-check source. The total of 130 procedures (system-inventory) cannot be reconciled with the 111 in the registry.

None of items 1–5 undermine the architecture findings, but the component and trigger registries are not yet reliable enough to feed downstream automated tooling (API scaffolders, test generators, migration toolchains) without a second-pass reconciliation pass.

---

## Check-by-Check Results

### 1. Required files exist — **PASS**

All 20 files confirmed in `results/D1-application-architecture/`:  
`system-inventory.json`, `module-boundary-map.json`, `component-registry.json`, `application-interface-catalogue.json`, `dependency-graph.json`, `call-flow-map.json`, `architecture-pattern-report.md`, `architecture-violation-register.json`, `application-risk-register.json`, `strangler-candidate-report.md`, `forward-engineering-input-map.md`, `open-questions.md`, `extraction-audit.md`, `application-architecture-summary.md`, `AA_App_Extractor.md`, `diagrams/system-context.mmd`, `diagrams/container-view.mmd`, `diagrams/component-view.mmd`, `diagrams/dependency-view.mmd`, `diagrams/call-flow-view.mmd`.

---

### 2. JSON valid — **PASS**

All seven standalone JSON files (`system-inventory.json`, `module-boundary-map.json`, `component-registry.json`, `application-interface-catalogue.json`, `dependency-graph.json`, `architecture-violation-register.json`, `application-risk-register.json`) and `call-flow-map.json` were read in full. No trailing commas, unescaped quote characters, unclosed braces or brackets, or malformed numeric literals were found.

---

### 3. Modules match component registry — **PASS**

Six modules are declared in `module-boundary-map.json` (MOD-01 through MOD-06). Every `COMP-PKG-xx` and `COMP-FORM-xx` entry in the component registry carries a `module` field that resolves to one of those six IDs. No dangling module references. MOD-06 accounts for 6 packages, 3 forms, and 2 libraries — all registered.

---

### 4. Dependency edges resolve to nodes — **PARTIAL**

`dependency-graph.json` declares 23 nodes and 39 edges. All 39 `from`/`to` values resolve to declared nodes. No orphan endpoints.

**OMISSION — DISC-008:** PKG_REPORTING has zero outgoing edges despite its spec declaring PKG_EMPLOYEE, PKG_PAYROLL, and PKG_COMMON as dependencies. Three edges are missing.

**MISSING EDGE — DISC-011:** `PKG_SECURITY.authenticate` calls `PKG_EMPLOYEE.set_session_context(p_username, v_emp_id)` per the spot-check `.pkb`. No edge `PKG_SECURITY → PKG_EMPLOYEE` exists in `dependency-graph.json` or in `module-boundary-map.json` MOD-05 `outbound_calls_to`. This is a structural accuracy gap — `PKG_SECURITY` is classified as having zero domain-package dependencies when it actually depends on `PKG_EMPLOYEE`.

---

### 5. Call-flow steps reference components — **PARTIAL**

All 10 flows (FLOW-01 through FLOW-10) reference actors from the declared component set. Structural resolution passes.

**Accuracy failure — DISC-012 in FLOW-02:**
- Step 5: `actor: DB Trigger, action: TRG_EMPLOYEES_VALIDATE BEFORE INSERT — checks HIRE_DATE ≤ SYSDATE+180, salary ≥ JOB_GRADES.MIN_SALARY`. The actual trigger name is `TRG_EMP_BEFORE_INSERT`. The salary validation against `JOB_GRADES.MIN_SALARY` is an **invented claim** — not present in the actual trigger body. `TRG_EMP_BEFORE_INSERT` validates HIRE_DATE and email uniqueness only.
- Step 7: `actor: DB Trigger, action: TRG_EMPLOYEES_AUDIT AFTER INSERT → PKG_AUDIT.log_action`. `TRG_EMPLOYEES_AUDIT` does not exist in any source file. Employee audit logging on insert is performed by PKG_EMPLOYEE package code (correctly shown in step 11), not by a trigger. This step references a phantom component.

---

### 6. Diagrams match JSON artifacts — **PARTIAL**

All drawn edges in `dependency-view.mmd` and `component-view.mmd` map to real edges in the JSON. No fabricated edges found in either diagram.

Omissions (consistent with JSON gaps, not standalone errors):
- PKG_REPORTING absent from `dependency-view.mmd` — consistent with missing JSON edges (DISC-008).
- PKG_SECURITY → PKG_EMPLOYEE edge absent from both diagrams — consistent with missing JSON edge (DISC-011).

No ghost edges in the current diagrams. PARTIAL verdict is for omissions only.

---

### 7. Claims have evidence — **PARTIAL**

All 24 violations carry a `file` field and an `evidence` field. Sample verification:

| Violation | Evidence Claimed | Spot-Check Confirms |
|-----------|-----------------|---------------------|
| VIO-SEC-01 (hard-coded AES key) | `c_encryption_key CONSTANT RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!')` | ✓ confirmed in PKG_SECURITY.pkb |
| VIO-DATA-01 (90-day vs 180-day hire date) | Form: `SYSDATE + 90`; Trigger: `SYSDATE + 180` | ✓ confirmed in HRMS_EMPLOYEE.xml and TRG_EMP_BEFORE_INSERT |
| VIO-SEC-06 (auth stub) | `-- TODO: compare hashed password against stored credential` | ✓ confirmed; PKG_SECURITY.pkb body shows no hash comparison |
| VIO-ARCH-02 (partial commits) | `IF MOD(v_emp_count, 50) = 0 THEN COMMIT` | ✓ confirmed via extraction-audit.md (PKG_PAYROLL.pkb directly read) |

**DISC-003:** `component-registry.json` COMP-PKG-07 lists `authenticate` as returning `"VARCHAR2 (session_id)"`. Spot-check declares `RETURN NUMBER`.

**DISC-010:** COMP-DB-TRIGGERS lists `TRG_EMPLOYEES_VALIDATE: "validates SALARY ≥ JOB_GRADES.MIN_SALARY"`. The actual trigger (`TRG_EMP_BEFORE_INSERT`) validates only HIRE_DATE and email uniqueness. Salary validation is in `PKG_VALIDATION.validate_salary_for_grade`. This is an invented claim in the registry, not an evidence mismatch — the claim is simply absent from the source.

---

### 8. Risks have affected module/component — **PARTIAL**

All 13 risks carry an `evidence` field pointing to a specific violation ID and source file. Every risk traces to a concrete, evidence-backed finding. Severity ratings are appropriate.

Structural gap: the risk register has no formal `affected_modules` or `affected_components` field. The role description mandates explicit module/component labeling. Evidence cross-references substitute functionally, but any downstream parser expecting `affected_modules` will find nothing to parse.

---

### 9. Unknowns are open questions — **PASS**

`open-questions.md` lists 41 questions. `system-inventory.json` includes 8 inline open questions. `extraction-audit.md` lists 11 "What Was NOT Found" items. All three are cross-consistent. No unknown is presented as a fact. Confidence levels are correctly differentiated: 1.0 for fully-scanned components, 0.7 for HRMS_REPORTS/HRMS_ADMIN (inferred from OPEN_FORM calls), 0.7–0.8 for DBMS_SCHEDULER jobs (inferred from comments).

---

### 10. No invented cloud/platform/runtime assumptions — **PASS**

All current-state artifacts describe the existing Oracle Forms + Oracle DB system only. No cloud provider, container platform, or runtime is asserted as existing now. `forward-engineering-input-map.md` and `strangler-candidate-report.md` recommend specific targets (PostgreSQL, React, AWS KMS, etc.) but these are clearly labelled as target-state recommendations, not extracted facts.

---

### 11. Forward-engineering files are actionable — **PASS**

`strangler-candidate-report.md`: Six modules ranked by migration readiness with explicit coupling scores, named blockers per module, and a concrete multi-step strangler approach per module. The 6-phase migration sequence is ordered by dependency (infrastructure first, highest-risk last) and justified.

`forward-engineering-input-map.md`: Module-to-service mapping tables, proposed REST API endpoints per service, data migration notes per table, and 10 enumerated pre-migration mandatory tasks with category labels. These are immediately usable by a planning team.

---

## Discrepancy Register

All conflicts between registry and spot-check source files are documented here.

| ID | Item | Source A | Source B | Status |
|----|------|----------|----------|--------|
| DISC-001 | Total procedure/function count | `system-inventory.json`: **130** | `component-registry.json` sum: **111** | UNRESOLVED — 19-entry gap. Likely reflects private/helper procedures in Layer 1 `source_code.json` not reflected in the public-facing registry. |
| DISC-002 | Violation category breakdown | Task summary: "6 security, 8 architecture, 5 data, 2 ops" (sums to 21) | `architecture-violation-register.json`: **9 security, 9 architecture, 5 data, 1 ops** (sums to 24) | UNRESOLVED — task summary is wrong; register is authoritative. |
| DISC-003 | PKG_SECURITY.authenticate return type | `component-registry.json` COMP-PKG-07: `"VARCHAR2 (session_id)"` | PKG_SECURITY.pkb spot-check: `RETURN NUMBER` | RESOLVED — source spec is authoritative; registry has a type error. |
| DISC-004 | PKG_AUDIT function name | `component-registry.json` COMP-PKG-08: `get_audit_trail` | PKG_AUDIT.pkb spot-check: `get_change_history(p_table_name, p_record_id, p_from_date, p_to_date) RETURN SYS_REFCURSOR` | UNRESOLVED — source is authoritative. |
| DISC-005 | PKG_COMMON procedure names | Registry COMP-PKG-09: 16 entries with 4 renamed, 4 phantom, 4 missing | PKG_COMMON.pkb spot-check: 17 entries (see authoritative list below) | UNRESOLVED — registry needs full rewrite from authoritative list. |
| DISC-006 | PKG_REPORTING procedure names | Registry COMP-PKG-11: `compensation_analysis`, `performance_summary_report`, `department_summary_report` | PKG_REPORTING.pkb spot-check: `compensation_summary`, `new_hires_report`, `eeo_compliance_report` | UNRESOLVED — 3 wrong names; 2 missing (`new_hires_report`, `eeo_compliance_report`); 2 phantom not in source. |
| DISC-007 | PKG_VALIDATION procedure names | Registry COMP-PKG-10: `validate_positive_number`, `validate_percentage`, `validate_email_address`, `validate_phone_number`, `validate_ssn` | PKG_VALIDATION.pkb spot-check: `validate_salary_for_grade`, `validate_email_format`, `validate_phone_format`, `validate_emp_number_format`, `is_future_date` | UNRESOLVED — 5 wrong names; 2 missing; 3 phantom entries. |
| DISC-008 | PKG_REPORTING dependency edges | `dependency-graph.json`: zero outgoing edges for PKG_REPORTING | PKG_REPORTING.pks: "Dependencies: PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON" | UNRESOLVED — 3 edges missing from graph and diagrams. |
| DISC-009 | Trigger registry names vs source files | Registry COMP-DB-TRIGGERS: TRG_EMPLOYEES_AUDIT, TRG_SALARY_AUDIT, TRG_LEAVE_AUDIT, TRG_EMPLOYEES_VALIDATE, TRG_AUDIT_LOG_INSERT, TRG_NOTIFICATION_INSERT | trg_audit.sql: TRG_SALARY_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_DEPARTMENT_AUDIT; trg_employees.sql: TRG_EMP_BEFORE_INSERT, TRG_EMP_BEFORE_UPDATE, TRG_EMP_INSTEAD_OF_DELETE | UNRESOLVED — only TRG_SALARY_AUDIT matches. Registry has 2 phantom entries not in any source file (TRG_AUDIT_LOG_INSERT, TRG_NOTIFICATION_INSERT); 1 real trigger absent (TRG_DEPARTMENT_AUDIT); 4 entries have wrong names and some have wrong events. Registry was populated from Layer 1 JSON, not from the actual trigger SQL files. |
| DISC-010 | TRG_EMPLOYEES_VALIDATE body description | Registry: "validates SALARY ≥ JOB_GRADES.MIN_SALARY" | trg_employees.sql TRG_EMP_BEFORE_INSERT: validates HIRE_DATE ≤ SYSDATE+180 and email uniqueness only | UNRESOLVED — salary validation is an **invented claim**. Actual salary validation lives in `PKG_VALIDATION.validate_salary_for_grade`, not in any trigger. |
| DISC-011 | PKG_SECURITY → PKG_EMPLOYEE dependency | `dependency-graph.json` + module-boundary-map MOD-05: no edge to PKG_EMPLOYEE | PKG_SECURITY.pkb authenticate body: `PKG_EMPLOYEE.set_session_context(p_username, v_emp_id)` | UNRESOLVED — one dependency edge missing. `set_session_context` is also absent from PKG_EMPLOYEE's registry entry (COMP-PKG-01). |
| DISC-012 | FLOW-02 trigger accuracy | `call-flow-map.json` FLOW-02 step 5: TRG_EMPLOYEES_VALIDATE + salary check; step 7: TRG_EMPLOYEES_AUDIT AFTER INSERT → PKG_AUDIT | trg_employees.sql: TRG_EMP_BEFORE_INSERT (no salary check); no AFTER INSERT trigger on EMPLOYEES calls PKG_AUDIT | UNRESOLVED — step 5 has wrong name and invented body claim; step 7 references a phantom trigger. |

---

## Spot-Check Procedure Inventory (Authoritative)

The following counts and names are from the spot-check source files and override the component registry where they conflict.

**PKG_AUDIT** (3 entries — count correct; 1 name error: DISC-004)
- `log_action(p_table_name, p_record_id, p_action, p_user DEFAULT USER, p_old_values DEFAULT NULL, p_new_values DEFAULT NULL)` — PROCEDURE. PRAGMA AUTONOMOUS_TRANSACTION. Captures IP and session via SYS_CONTEXT.
- `purge_old_records(p_days_to_keep IN NUMBER DEFAULT 365, p_user IN VARCHAR2 DEFAULT USER)` — PROCEDURE. Deletes AUDIT_LOG records older than p_days_to_keep days. Default retention: **365 days**.
- `get_change_history(p_table_name, p_record_id, p_from_date DEFAULT NULL, p_to_date DEFAULT NULL) RETURN SYS_REFCURSOR` — FUNCTION. *(Registry incorrectly names this `get_audit_trail` — DISC-004)*

**PKG_COMMON** (17 entries — DISC-005: registry has 16, misnames 4, omits 5, invents 4)
- `log_error(p_package, p_procedure, p_message, p_user DEFAULT USER)` — PROCEDURE. PRAGMA AUTONOMOUS_TRANSACTION; message truncated to 3000 chars; inserts into AUDIT_LOG with TABLE_NAME='ERROR_LOG'.
- `log_info(p_package, p_procedure, p_message, p_user DEFAULT USER)` — PROCEDURE. PRAGMA AUTONOMOUS_TRANSACTION.
- `get_param(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN VARCHAR2` — FUNCTION. Reads SYSTEM_PARAMETERS.
- `get_param_number(p_group, p_code) RETURN NUMBER` — FUNCTION. *(missing from registry)*
- `get_param_date(p_group, p_code) RETURN DATE` — FUNCTION. Format: 'YYYY-MM-DD'. *(missing from registry)*
- `set_param(p_group, p_code, p_value, p_user DEFAULT USER)` — PROCEDURE. Only EDITABLE_FLAG='Y' parameters can be updated; error -20900 otherwise.
- `business_days_between(p_start_date IN DATE, p_end_date IN DATE) RETURN NUMBER` — FUNCTION. Counts Mon–Fri inclusive; NLS forced to AMERICAN. *(missing from registry)*
- `add_business_days(p_date IN DATE, p_days IN NUMBER) RETURN DATE` — FUNCTION.
- `get_fiscal_year(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER` — FUNCTION. Fiscal year starts **October (month 10)**; Oct–Dec of year N = fiscal year N+1.
- `get_fiscal_quarter(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER` — FUNCTION. Q1=Oct–Dec, Q2=Jan–Mar, Q3=Apr–Jun, Q4=Jul–Sep.
- `format_phone(p_phone IN VARCHAR2) RETURN VARCHAR2` — FUNCTION. 10-digit: `(NXX) NXX-XXXX`; 11-digit starting with 1: `+1 (NXX) NXX-XXXX`.
- `format_ssn_masked(p_ssn IN VARCHAR2) RETURN VARCHAR2` — FUNCTION. Returns `***-**-XXXX` (last 4 digits only). *(missing from registry)*
- `format_currency(p_amount IN NUMBER, p_currency_code IN VARCHAR2 DEFAULT 'USD') RETURN VARCHAR2` — FUNCTION. USD, EUR (€), GBP (£) supported.
- `format_name(p_first_name, p_last_name, p_format DEFAULT 'FL') RETURN VARCHAR2` — FUNCTION. *(missing from registry)*
- `is_valid_email(p_email IN VARCHAR2) RETURN BOOLEAN` — FUNCTION. REGEXP_LIKE pattern: `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$`. *(registry calls this `validate_email`)*
- `is_valid_phone(p_phone IN VARCHAR2) RETURN BOOLEAN` — FUNCTION. 10–11 digits. *(registry calls this `validate_phone`)*
- `is_valid_ssn(p_ssn IN VARCHAR2) RETURN BOOLEAN` — FUNCTION. Must be 9 digits after stripping non-numeric characters. *(registry calls this `validate_ssn`)*
*(Registry adds 4 phantom entries not in source: `get_lookup_values`, `get_next_sequence`, `is_business_day`, `get_active_employees_count`)*

**PKG_SECURITY** (8 entries — names correct; 1 type error: DISC-003)
- `hash_password(p_password IN VARCHAR2) RETURN VARCHAR2` — MD5 via DBMS_CRYPTO. ⚠ Weak algorithm.
- `authenticate(p_username IN VARCHAR2, p_password IN VARCHAR2, p_ip_address IN VARCHAR2 DEFAULT NULL) RETURN NUMBER` — FUNCTION. Matches EMPLOYEES.EMAIL case-insensitively; inserts USER_SESSIONS; calls `PKG_EMPLOYEE.set_session_context` (see DISC-011); calls PKG_AUDIT.log_action. *(Registry says RETURN VARCHAR2 — DISC-003)*
- `logout(p_session_id IN NUMBER)` — PROCEDURE.
- `is_session_valid(p_session_id IN NUMBER) RETURN BOOLEAN` — FUNCTION. Timeout: **30 minutes from LOGIN_TIME** (not last activity).
- `has_permission(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN` — FUNCTION. GRADE_ID ≥ 8: full access; ≥ 5: VIEW all; any grade: LEAVE CREATE/VIEW + EMPLOYEE VIEW; else DENY.
- `encrypt_ssn(p_ssn IN VARCHAR2) RETURN VARCHAR2` — AES-256-CBC PKCS5, hard-coded 32-byte key 'HR$ystem_3ncrypt10n_K3y_2024!!'.
- `decrypt_ssn(p_encrypted IN VARCHAR2) RETURN VARCHAR2` — Returns '`***DECRYPT_ERROR***`' on failure.
- `change_password(p_emp_id IN NUMBER, p_old_password IN VARCHAR2, p_new_password IN VARCHAR2)` — PROCEDURE. Minimum 8 chars (-20310); requires uppercase (-20311); requires digit (-20312). Does NOT verify old password.

**PKG_VALIDATION** (8 entries — DISC-007: registry misnames 5, omits 2, invents 3)
- `validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN` — FUNCTION. FALSE if either NULL or if end < start.
- `validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2` — FUNCTION. Returns NULL if valid; error string with format `FM$999,999,990.00` if outside grade band. *(missing from registry)*
- `validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN` — FUNCTION. Delegates to PKG_COMMON.is_valid_email. *(registry calls this `validate_email_address`)*
- `validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN` — FUNCTION. Delegates to PKG_COMMON.is_valid_phone. *(registry calls this `validate_phone_number`)*
- `validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN` — FUNCTION. Regex: `^EMP-\d{6}$`. *(missing from registry)*
- `is_future_date(p_date IN DATE) RETURN BOOLEAN` — FUNCTION. TRUNC(p_date) > TRUNC(SYSDATE); same-day is NOT future. *(missing from registry)*
- `is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN` — FUNCTION. Checks SAT/SUN + HOLIDAYS table (ACTIVE_FLAG='Y').
- `validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2` — FUNCTION. Only handles table='EMPLOYEES'; all others silently return NULL.
*(Registry adds 3 phantom entries not in source: `validate_positive_number`, `validate_percentage`, `validate_ssn`)*

**PKG_REPORTING** (8 entries — DISC-006: 3 wrong names; 2 missing; 2 phantom)
- `headcount_report(...)` — PROCEDURE. ✓ name correct.
- `compensation_summary(p_cursor OUT t_report_cursor, p_dept_id NUMBER DEFAULT NULL, p_grade_id NUMBER DEFAULT NULL)` — PROCEDURE. Compa-ratio = `AVG(BASE_SALARY / ((MIN_SALARY + MAX_SALARY) / 2)) × 100`, rounded to 1 decimal. *(registry calls this `compensation_analysis`)*
- `turnover_report(...)` — PROCEDURE. Turnover % = terminations_in_period / employees_hired_by_end_date × 100. ✓ name correct.
- `new_hires_report(p_cursor OUT t_report_cursor, p_start_date DATE, p_end_date DATE, p_dept_id NUMBER DEFAULT NULL)` — PROCEDURE. *(missing from registry)*
- `leave_utilization_report(...)` — PROCEDURE. Utilization % = AVG(USED) / AVG(OPENING_BALANCE + ACCRUED) × 100. ✓ name correct.
- `payroll_summary_report(p_cursor OUT t_report_cursor, p_period_id NUMBER)` — PROCEDURE. Hard-coded ELEMENT_IDs: 100=federal, 101=state, 102=SS, 103=Medicare. ✓ name correct.
- `eeo_compliance_report(p_cursor OUT t_report_cursor, p_as_of_date DATE DEFAULT SYSDATE)` — PROCEDURE. Gender codes: M, F, O, NULL (not disclosed). Female %: females/total × 100. *(missing from registry)*
- `refresh_reporting_tables(p_user IN VARCHAR2 DEFAULT USER)` — PROCEDURE. Stub only. ✓ name correct.
*(Registry adds 2 phantom entries not in source: `performance_summary_report`, `department_summary_report`)*

**PKG_PERFORMANCE** (12 entries — EXACT MATCH with registry)
`create_review_cycle`, `open_review_cycle`, `close_review_cycle`, `create_review`, `submit_self_assessment`, `submit_manager_review`, `acknowledge_review`, `add_goal`, `update_goal_progress`, `get_team_reviews`, `get_rating_distribution`, `generate_reviews_for_cycle`.  
Rating range: 1.0–5.0. Labels: ≥4.5→Exceptional, ≥3.5→Exceeds Expectations, ≥2.5→Meets Expectations, ≥1.5→Needs Improvement, <1.5→Unsatisfactory.

---

## Spot-Check Trigger Inventory (Authoritative)

The following trigger names and definitions are from the spot-check source files. The component registry's COMP-DB-TRIGGERS entry should be entirely rewritten from this table.

| Actual Name | Table | Timing / Event | Key Action | Registry Name (Wrong) |
|-------------|-------|---------------|------------|----------------------|
| TRG_SALARY_AUDIT | SALARY_RECORDS | AFTER INSERT OR UPDATE OR DELETE | Calls PKG_AUDIT.log_action with JSON old/new salary | TRG_SALARY_AUDIT ✓ (only correct entry) |
| TRG_LEAVE_REQUEST_AUDIT | LEAVE_REQUESTS | **AFTER UPDATE OF STATUS** | Calls PKG_AUDIT.log_action with old/new status JSON | TRG_LEAVE_AUDIT ✗ (wrong name AND wrong event scope) |
| TRG_DEPARTMENT_AUDIT | DEPARTMENTS | AFTER INSERT OR UPDATE OR DELETE | Calls PKG_AUDIT.log_action | **ABSENT from registry** |
| TRG_EMP_BEFORE_INSERT | EMPLOYEES | BEFORE INSERT | Sets CREATED_BY, CREATED_DATE, ACTIVE_FLAG='Y', EMPLOYMENT_STATUS='ACTIVE'; validates HIRE_DATE ≤ SYSDATE+**180** (-20501); validates email uniqueness among ACTIVE employees (-20502) | TRG_EMPLOYEES_VALIDATE ✗ (wrong name; description adds invented salary check) |
| TRG_EMP_BEFORE_UPDATE | EMPLOYEES | BEFORE UPDATE | Sets MODIFIED_BY/DATE; prevents reactivation of TERMINATED employees (-20503); inserts into EMPLOYEE_HISTORY for STATUS_CHANGE, DEPARTMENT_CHANGE, JOB_CHANGE | TRG_EMPLOYEES_AUDIT ✗ (completely wrong name and wrong event) |
| TRG_EMP_INSTEAD_OF_DELETE | EMPLOYEES | BEFORE DELETE | Raises -20504 unconditionally; enforces soft-delete pattern | **ABSENT from registry** (TRG_AUDIT_LOG_INSERT and TRG_NOTIFICATION_INSERT are phantom entries not in source) |

Error codes introduced by triggers (all from trg_employees.sql):
- **-20501** Hire date more than 180 days in future
- **-20502** Email address already in use (duplicate among ACTIVE employees)
- **-20503** Cannot directly reactivate a terminated employee
- **-20504** Direct deletion not allowed; use termination process or ACTIVE_FLAG='N'

---

## What Does Not Need Fixing

- The 6-module boundary decomposition and all coupling scores.
- CYCLE-01 (PKG_EMPLOYEE ↔ PKG_PAYROLL) identification and evidence.
- All 24 violations: content, severity, file citations, and evidence strings are correct where verifiable.
- All 13 migration risks: severity ratings and migration impact statements are appropriate.
- The strangler fig ranking (Performance first, Payroll last) and the 6-phase migration sequence.
- The 10 pre-migration mandatory tasks in `forward-engineering-input-map.md`.
- VIO-DATA-01 (hire date 90 vs 180 days) correctly documented (trigger source file confirms 180).
- All 10 call flows: structure is accurate except FLOW-02 steps 5 and 7 (DISC-012).
- The 41 open questions in `open-questions.md` are genuine and appropriate.

---

## Findings Requiring Correction Before Downstream Use

| Priority | ID | Finding | File(s) | Action Required |
|----------|----|---------|---------|-----------------|
| HIGH | DISC-009 | Trigger registry: 5 of 6 names wrong; 2 phantom entries; 1 real trigger absent | `component-registry.json` COMP-DB-TRIGGERS | Rewrite using the 6-trigger authoritative table above |
| HIGH | DISC-010 | TRG_EMPLOYEES_VALIDATE description invents salary validation against JOB_GRADES | `component-registry.json` COMP-DB-TRIGGERS | Remove salary validation claim; update to reflect actual TRG_EMP_BEFORE_INSERT behaviour |
| HIGH | DISC-005 | PKG_COMMON: 4 renamed, 5 missing, 4 phantom entries (16 in registry vs 17 in source) | `component-registry.json` COMP-PKG-09 | Rewrite using the 17-entry authoritative list above |
| HIGH | DISC-006 | PKG_REPORTING: 3 wrong names, 2 missing procedures, 2 phantom entries | `component-registry.json` COMP-PKG-11 | Rewrite using the 8-entry authoritative list above |
| HIGH | DISC-007 | PKG_VALIDATION: 5 wrong names, 2 missing, 3 phantom entries | `component-registry.json` COMP-PKG-10 | Rewrite using the 8-entry authoritative list above |
| HIGH | DISC-012 | FLOW-02 step 5 wrong trigger name + invented salary check; step 7 phantom trigger | `call-flow-map.json` | Step 5: change name to TRG_EMP_BEFORE_INSERT, remove salary check; step 7: remove phantom trigger, note audit is from PKG_EMPLOYEE package code |
| MEDIUM | DISC-011 | PKG_SECURITY → PKG_EMPLOYEE edge missing from graph (set_session_context call) | `dependency-graph.json`, `module-boundary-map.json` | Add edge; add set_session_context to COMP-PKG-01 (PKG_EMPLOYEE) procedure list |
| MEDIUM | DISC-008 | PKG_REPORTING has 0 edges in dependency graph despite declared dependencies | `dependency-graph.json`, diagrams | Add 3 edges: PKG_REPORTING → PKG_EMPLOYEE, → PKG_PAYROLL, → PKG_COMMON; regenerate diagrams |
| MEDIUM | DISC-004 | PKG_AUDIT function named get_audit_trail; actual name is get_change_history | `component-registry.json` COMP-PKG-08 | Correct function name |
| MEDIUM | DISC-003 | PKG_SECURITY.authenticate return type VARCHAR2; actual is NUMBER | `component-registry.json` COMP-PKG-07 | Correct return type to NUMBER |
| MEDIUM | DISC-002 | Violation subtotals wrong in all stakeholder-facing summaries | `application-architecture-summary.md`, any downstream docs | Correct to: 9 security (2 CRITICAL), 9 architecture, 5 data integrity, 1 operations = 24 |
| LOW | DISC-001 | 130 claimed procedures vs 111 in registry (19-entry gap) | `system-inventory.json` | Document which 19 are private/internal (consult Layer 1 source_code.json) |
| LOW | — | Risk register lacks `affected_modules` field | `application-risk-register.json` | Add `affected_modules` array to each risk entry |
