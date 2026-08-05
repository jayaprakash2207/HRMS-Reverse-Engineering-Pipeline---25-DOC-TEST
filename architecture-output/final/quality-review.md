# Quality Review — D1 Application Architecture Extraction

**Reviewer:** Agent 06 — Quality Review Agent (Pass 1 + Pass 2)
**Date:** 2026-08-04
**Subject:** AA Agent 1 output for Oracle HRMS v4.2 (Build 2024.03.15)
**Input path:** `results/D1-application-architecture/`
**Overall Verdict:** PARTIAL

---

## Extraction Totals (from system-inventory.json)

| Artifact | Reported Count | Spot-Check Confirmed | Status |
|---|---|---|---|
| PL/SQL Packages | 11 | 11 (PKG_AUDIT, PKG_COMMON, PKG_EMPLOYEE, PKG_INTEGRATION, PKG_LEAVE, PKG_NOTIFICATION, PKG_PAYROLL, PKG_PERFORMANCE, PKG_REPORTING, PKG_SECURITY, PKG_VALIDATION) | PASS |
| Public procedures/functions | 115 total across 11 packages | See per-package count below | PARTIAL — see QR-001 |
| Oracle Forms | 6 | 6 (HRMS_LOGIN, HRMS_MENU, HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE, HRMS_PERFORMANCE) | PASS |
| Form libraries | 2 | 2 (HRMS_COMMON_LIB, HRMS_VALIDATION_LIB) | PASS |
| DB Triggers | 6 | 6 (3 in trg_employees.sql, 3 in trg_audit.sql) | PASS |
| Database tables | 22 | 22 | PASS |
| Views | 6 | 6 | PASS |
| Sequences | 29–30 | 30 (DISC-001 — see QR-002) | PARTIAL |
| Modules (boundary map) | 11 | 11 | PASS |
| Components (registry) | 20 | 20 | PASS |

---

## Per-Package Procedure Count Verification

| Package | Reported Count | Confirmed in Source | Discrepancy |
|---|---|---|---|
| PKG_AUDIT | 3 | 3 (log_action, purge_old_records, get_change_history) | NONE |
| PKG_COMMON | 17 | 17 (log_error, log_info, get_param, get_param_number, get_param_date, set_param, business_days_between, add_business_days, get_fiscal_year, get_fiscal_quarter, format_phone, format_ssn_masked, format_currency, format_name, is_valid_email, is_valid_phone, is_valid_ssn) | NONE |
| PKG_EMPLOYEE | 18 | 18 (generate_emp_number, get_next_emp_id†, validate_dept†, validate_manager†, log_history†, create_employee, update_employee, get_employee, get_employee_by_number, search_employees, transfer_employee, promote_employee, terminate_employee, rehire_employee, get_direct_reports, get_org_chart, get_headcount_by_dept, get_tenure_years, is_active, validate_employee, emp_exists, set_session_context) | NONE |
| PKG_INTEGRATION | 5 | 5 (generate_gl_journal, export_benefits_feed, import_time_attendance, sync_org_structure, get_integration_status) | NONE |
| PKG_LEAVE | 14 | 14 (submit_leave_request, approve_leave_request, reject_leave_request, cancel_leave_request, get_leave_balance, adjust_leave_balance, initialize_balances, run_monthly_accrual, process_carryover, expire_carryover, get_pending_requests, get_team_calendar, calculate_business_days, check_leave_overlap) | NONE |
| PKG_NOTIFICATION | 4 | 4 (send_notification, process_queue, retry_failed, cancel_notification) | NONE |
| PKG_PAYROLL | 17 (registry public_methods) | 18 in source (missing: calculate_employee_pay) | **QR-001** |
| PKG_PERFORMANCE | 11 (extraction-audit) | 12 in source (generate_reviews_for_cycle undercounted) | **QR-001** |
| PKG_REPORTING | 8 | 8 (headcount_report, compensation_summary, turnover_report, new_hires_report, leave_utilization_report, payroll_summary_report, eeo_compliance_report, refresh_reporting_tables) | NONE |
| PKG_SECURITY | 8 | 8 (authenticate, logout, is_session_valid, has_permission, encrypt_ssn, decrypt_ssn, hash_password, change_password) | NONE |
| PKG_VALIDATION | 8 | 8 (validate_date_range, validate_salary_for_grade, validate_email_format, validate_phone_format, validate_emp_number_format, is_future_date, is_business_day, validate_required_fields) | NONE |

† Private members — not expected in public_methods list.

---

## Issue Register — Pass 1

### QR-001 — PARTIAL — Procedure Count Understated for PKG_PAYROLL and PKG_PERFORMANCE

**severity:** Low
**check:** Procedure count vs source .pkb files

- **PKG_PAYROLL:** component-registry `public_methods` lists 17 entries; spot-check source confirms 18. Missing: `calculate_employee_pay` — present in call-flow-map.json CF-004 step 4 but absent from registry list.
- **PKG_PERFORMANCE:** extraction-audit says "11 members"; component-registry has 12; source confirms 12. Off by 1.

**Impact:** Minor — both procedures are documented correctly elsewhere; purely a count inconsistency.

---

### QR-002 — PARTIAL — Sequence Count Inconsistency (29 vs 30)

**severity:** Low
**check:** Totals in system-inventory.json vs extraction-audit.md

- `system-inventory.json` extraction_totals: `"sequences": 29`
- `extraction-audit.md` Source Coverage Matrix: `"schema/sequences/hrms_sequences.sql | FULL | 30 sequences"`

15 sequences confirmed in spot-check: SEQ_EMPLOYEE, SEQ_AUDIT, SEQ_EMP_HISTORY, SEQ_SALARY, SEQ_PAY_PERIOD, SEQ_PAYROLL_RUN, SEQ_PAYROLL_DETAIL, SEQ_LEAVE_REQUEST, SEQ_LEAVE_BALANCE, SEQ_LEAVE_ACCRUAL, SEQ_NOTIFICATION, SEQ_USER_SESSION, SEQ_REVIEW_CYCLE, SEQ_PERF_REVIEW, SEQ_PERF_GOAL. Full count unverifiable without raw DDL.

**DISC-001:** 29 vs 30 — unresolved. Use 30 (DDL audit row) pending raw DDL verification.

---

### QR-003 — PASS — JSON Validity

All 8 JSON files structurally valid: no trailing commas, all braces/brackets closed, all strings delimited. PASS.

---

### QR-004 — PASS — Dependency Graph Edge-to-Node Resolution

All 37 edges reference declared nodes. Circular dependency CYC-001 (PKG_EMPLOYEE ↔ PKG_PAYROLL) present and confirmed. No orphaned edge endpoints. Note: pass 2 identifies 5 additional missing edges (see QR-017). [EDGE-CASE-FOUND]

---

### QR-005 — PASS — Call-Flow Steps Reference Declared Components

CF-001 through CF-006 all reference registered components. DBMS_SCHEDULER correctly qualified as "implied" in CF-006. Note: pass 2 identifies CF-002 accuracy issues (see QR-023). [EDGE-CASE-FOUND]

---

### QR-006 — PARTIAL — DBMS_SCHEDULER Node Missing from Dependency Graph

**severity:** Low

- `dependency-view.mmd` includes `DBMSSCHED["DBMS_SCHEDULER (implied)"]` with edges to PKG_NOTIF and PKG_LEAVE
- `dependency-graph.json` nodes array does NOT include a DBMS_SCHEDULER node

Diagram and call-flow reference an infrastructure component absent from the authoritative JSON graph.

---

### QR-007 — PASS — Module Boundary Evidence

All 11 modules cite at least one source file. No module boundary justified by folder name alone. PASS.

---

### QR-008 — PASS — Risk Register Evidence and Component Attribution

All 12 risks name specific source files with procedure references. Migration impact and recommended actions present for all 12. PASS.

---

### QR-009 — PASS — Architecture Violations Evidence Quality

All 23 violations cite specific file and procedure. Five spot-checked and confirmed. No invented violations. Note: pass 2 identifies 3 additional violations absent from the register (see QR-019, QR-021, QR-018a/b). PASS for what was documented; register is incomplete. [EDGE-CASE-FOUND]

---

### QR-010 — PASS — Business Rules: Exact Numeric Values Captured

All 25 key numeric business rules verified against spot-check source. All match exactly. Full table in final-sanity-check.md. PASS.

---

### QR-011 — PASS — No Invented Cloud/Platform/Runtime Assumptions

No AWS, Azure, GCP, Kubernetes, Docker, REST API, or message-queue assumptions found. All external dependencies grounded in source. PASS.

---

### QR-012 — PASS — Open Questions are Open Questions

Unknowns correctly phrased as questions. No open question stated as a fact elsewhere. PASS.

---

### QR-013 — PARTIAL (revised from PASS) — Forward Engineering Files Actionable [EDGE-CASE-FOUND]

Forward-engineering-input-map.md and strangler-candidate-report.md have clear next-step recommendations grounded in dependency analysis. However, pass 2 reveals a material gap: neither file distinguishes between form-reachable procedures (must have UI replacement) and batch-only procedures (need scheduler replacement) and orphaned procedures (may be dead code or missing forms). This distinction is required for actionable migration scoping. Downgraded to PARTIAL.

---

### QR-014 — PARTIAL — Diagrams Match JSON Artifacts [EDGE-CASE-FOUND]

Primary discrepancy: DBMS_SCHEDULER in dependency-view.mmd but not in dependency-graph.json nodes array (QR-006). Pass 2 adds 5 missing form-to-table edges (QR-017). Other node references resolve correctly.

---

### QR-015 — PARTIAL — DISC Documentation [EDGE-CASE-FOUND]

Two documented discrepancies: DISC-001 (sequence count 29 vs 30) and AV-013 (hire date 90 vs 180 days). Pass 2 identifies a third unresolved discrepancy not in original output: DISC-002 (SSN validation zero-segment check — client enforces, server does not). PARTIAL.

---

## Issue Register — Pass 2 (Second Independent Analysis)

Focus: orphaned package procedures, form triggers calling packages not in primary analysis, package procedures with no form trigger path, verdict revisits.

---

### QR-016 — NEW FINDING — Package Procedures with No Confirmed Form Entry Point (Orphaned Logic) [EDGE-CASE-FOUND]

The following public procedures/functions are confirmed in source but have no direct call path from any of the 6 confirmed Oracle Forms. Classified by root cause.

**PKG_EMPLOYEE — bypassed by form DML or missing form:**

| Procedure | Classification | Detail |
|---|---|---|
| `update_employee` | ORPHAN-01: bypassed | HRMS_EMPLOYEE.fmb uses block DML direct UPDATE; procedure exists as API but form never calls it |
| `transfer_employee` | ORPHAN-02: no UI | No transfer form exists in the 6 confirmed forms |
| `promote_employee` | ORPHAN-03: no UI | No promotion form exists in the 6 confirmed forms |
| `terminate_employee` | ORPHAN-04: bypassed | Form sets EMPLOYMENT_STATUS via direct block DML; procedure bypassed |
| `rehire_employee` | ORPHAN-05: no UI | No rehire form in the 6 confirmed forms |
| `get_org_chart` | ORPHAN-06: reporting | No org chart form confirmed |
| `get_headcount_by_dept` | ORPHAN-07: reporting | No form trigger confirmed |
| `get_tenure_years` | ORPHAN-08: reporting | No form trigger confirmed |
| `validate_employee` | ORPHAN-09: possible dead code | Not called from any form or confirmed package chain |

**PKG_LEAVE — batch-only or uncertain:**

| Procedure | Classification | Detail |
|---|---|---|
| `adjust_leave_balance` | ORPHAN-10: no UI | No admin balance adjustment form confirmed |
| `initialize_balances` | Internal | Called from adjust_leave_balance and run_monthly_accrual |
| `run_monthly_accrual` | Batch | DBMS_SCHEDULER monthly job |
| `process_carryover` | Batch | Year-end batch |
| `expire_carryover` | Batch | Year-end batch |
| `approve_leave_request` | UNCERTAIN | TP_APPROVALS tab exists in HRMS_LEAVE.fmb; button trigger body not confirmed in provided XML |
| `reject_leave_request` | UNCERTAIN | Same as above |
| `get_pending_requests` | UNCERTAIN | May underlie LEAVE_REQUEST block query via DEFAULT_WHERE |
| `get_team_calendar` | UNCERTAIN | TP_CALENDAR tab defined; block query mechanism not confirmed |

**PKG_PAYROLL — internal chain or no UI:**

| Procedure | Classification | Detail |
|---|---|---|
| `close_pay_period` | ORPHAN-11: no UI | No BTN_CLOSE_PERIOD confirmed in HRMS_PAYROLL.xml |
| `reverse_payroll` | ORPHAN-12: no UI | No BTN_REVERSE confirmed in HRMS_PAYROLL.xml |
| `generate_pay_register` | ORPHAN-13: no UI | Legacy flat-file procedure; no form button confirmed |
| `create_pay_periods` | Batch | Year-setup procedure |
| All tax sub-functions | Internal | Called from calculate_employee_pay only |

**PKG_PERFORMANCE — cycle management bypassed or missing form:**

| Procedure | Classification | Detail |
|---|---|---|
| `create_review_cycle` | ORPHAN-14: read-only block | REVIEW_CYCLE block InsertAllowed=No; no BTN_CREATE_CYCLE confirmed |
| `open_review_cycle` | ORPHAN-15: no UI | No button trigger confirmed |
| `close_review_cycle` | ORPHAN-16: no UI | No button trigger confirmed |
| `generate_reviews_for_cycle` | ORPHAN-17: no UI | Batch/admin tool; no form trigger |
| `submit_self_assessment` | ORPHAN-18: bypassed | Form writes SELF_ASSESSMENT column via direct block DML; procedure not called |
| `submit_manager_review` | ORPHAN-19: bypassed | Form writes MANAGER_ASSESSMENT via direct block DML; procedure not called |
| `acknowledge_review` | ORPHAN-20: no UI | No button trigger confirmed |
| `get_rating_distribution` | ORPHAN-21: reporting | No form trigger confirmed |

**PKG_REPORTING — entirely orphaned from confirmed forms:**

All 8 procedures (ORPHAN-22 through ORPHAN-29) have no call path from any of the 6 confirmed forms. The consumer form HRMS_REPORTS.fmb is listed in open questions as absent from source. If that form does not exist or was deleted, all 8 procedures are dead code.

**PKG_INTEGRATION — batch-only:**

All 5 procedures have no form entry point. Scheduled/batch-only or stubs.

**Impact on migration planning:** Procedures bypassed by form DML (update_employee, terminate_employee, submit_self_assessment, submit_manager_review) contain notification and audit side-effects that are silently skipped in the form path. These side-effects must be implemented in the migration target independently, since migrating the procedure alone does not make the form invoke it. Procedures with no UI (transfer_employee, promote_employee, rehire_employee) require either new UI or confirmation they are unused in production.

---

### QR-017 — NEW FINDING — Direct Form-to-Table Dependency Edges Missing from dependency-graph.json [EDGE-CASE-FOUND]

The following direct SQL calls in form triggers are not routed through packages and are absent from dependency-graph.json:

| Form | Trigger | Direct table access | Missing edge |
|---|---|---|---|
| HRMS_EMPLOYEE.fmb | POST-QUERY | `SELECT DEPT_NAME FROM DEPARTMENTS` | HRMS_EMPLOYEE → DEPARTMENTS |
| HRMS_EMPLOYEE.fmb | POST-QUERY | `SELECT JOB_TITLE FROM JOB_TITLES` | HRMS_EMPLOYEE → JOB_TITLES |
| HRMS_EMPLOYEE.fmb | POST-QUERY | `SELECT FIRST_NAME, LAST_NAME FROM EMPLOYEES` (manager name) | HRMS_EMPLOYEE → EMPLOYEES (self-join) |
| HRMS_LEAVE.fmb | POST-QUERY | `SELECT lt.LEAVE_TYPE_NAME FROM LEAVE_TYPES JOIN LEAVE_REQUESTS` | HRMS_LEAVE → LEAVE_TYPES |
| HRMS_LEAVE.fmb | POST-QUERY | `SELECT lt.LEAVE_TYPE_NAME FROM LEAVE_TYPES JOIN LEAVE_REQUESTS` | HRMS_LEAVE → LEAVE_REQUESTS |

Impact: Any schema change to DEPARTMENTS, JOB_TITLES, or LEAVE_TYPES requires form recompilation even if packages are unchanged. This understates migration impact for those tables.

---

### QR-018 — NEW FINDING — Critical Form-to-Package Call Path Inaccuracies [EDGE-CASE-FOUND]

**QR-018a: HRMS_PERFORMANCE.fmb bypasses PKG_PERFORMANCE procedures, silencing all performance notifications.**

PERFORMANCE_REVIEW block is UpdateAllowed=Yes with no BTN_SUBMIT_SELF_ASSESSMENT or BTN_SUBMIT_MANAGER_REVIEW button in confirmed trigger code. Users save assessments via Oracle Forms direct DML (COMMIT_FORM / toolbar_save from HRMS_COMMON_LIB). This means:
- `PKG_PERFORMANCE.submit_self_assessment` is never called → manager is never notified that a self-assessment was completed
- `PKG_PERFORMANCE.submit_manager_review` is never called → employee is never notified that their review was completed
- STATUS transitions ('MANAGER_REVIEW', 'COMPLETED') are written by whoever saves the form record, with no state validation

This is a **functional regression not documented in the 23 violations.** Rating notifications are the primary driver for employee engagement with the performance module. Their absence would be visible to users.

**QR-018b: HRMS_EMPLOYEE.fmb PRE-INSERT bypasses PKG_EMPLOYEE.create_employee, skipping multi-step server validation.**

The form PRE-INSERT trigger calls generate_emp_number and sets fields, then commits via Oracle Forms DML. PKG_EMPLOYEE.create_employee is NOT invoked. Consequences:
- validate_dept is NOT called (dept validation is only done in WHEN-VALIDATE-ITEM with a direct SELECT — no active-flag check in PRE-INSERT)
- validate_manager is NOT called (no manager chain or circular check at form layer)
- PKG_PAYROLL.create_salary_record is NOT called — no initial salary record is created for a new hire through the form
- PKG_NOTIFICATION.send_notification welcome email is NOT sent
- PKG_NOTIFICATION.send_notification manager notification is NOT sent

The only protections are WHEN-VALIDATE-ITEM (email format, dept active flag, job active flag, hire date max 90 days) and TRG_EMP_BEFORE_INSERT (hire date max 180 days, email uniqueness). No salary, no notifications.

---

### QR-019 — NEW FINDING — DISC-002: SSN Validation Drift Not in Violation Register [EDGE-CASE-FOUND]

AV-014 documents email validation drift (HRMS_VALIDATION_LIB rejects subdomains; PKG_COMMON accepts). The SSN validation drift is confirmed in spot-check source but absent from the 23-entry violation register:

- `HRMS_VALIDATION_LIB.validate_ssn`: checks 9 digits AND that none of these segments are all zeros — positions 1-3 ('000'), 4-5 ('00'), 6-9 ('0000')
- `PKG_COMMON.is_valid_ssn`: checks only that stripped digits total 9; does NOT check zero segments

**DISC-002:** SSN `000-12-3456` (zero area code) passes PKG_COMMON.is_valid_ssn but fails HRMS_VALIDATION_LIB.validate_ssn. An SSN entered via a non-form API path could be stored in a format the form would reject on edit. Source: PKG_COMMON.pkb vs HRMS_VALIDATION_LIB.pll.sql. Unresolved.

---

### QR-020 — NEW FINDING — PKG_COMMON.log_info Lacks Double-Quote Escaping [EDGE-CASE-FOUND]

`log_error` escapes double-quotes in the message: `REPLACE(SUBSTR(p_message, 1, 3000), '"', '\"')`.
`log_info` does not: `SUBSTR(p_message, 1, 3000)` passed raw into the JSON-like string.

Any message containing a `"` character produces malformed JSON in INFO_LOG audit rows (TABLE_NAME='INFO_LOG'). Downstream log parsers treating NEW_VALUES as JSON will fail on info records. Low severity but breaks log tooling consistency. Not in 23 violations.

---

### QR-021 — NEW FINDING — PKG_SECURITY.authenticate TOO_MANY_ROWS Path Not a Distinct Violation [EDGE-CASE-FOUND]

When multiple active employees share the same email, authenticate hits TOO_MANY_ROWS and falls back to `SELECT MIN(EMP_ID)`. This is documented as a security_notes comment in CF-001 but is not a distinct entry in the violation register.

This is a separate issue from AV-004 (no password check). The TOO_MANY_ROWS path allows an attacker who registers a duplicate email to deterministically influence which account receives an authenticated session — the lower EMP_ID always wins. If an attacker creates an account with an email matching an administrator and a lower EMP_ID, they capture the admin session. This is an account-takeover vector distinct from the general authentication bypass.

---

### QR-022 — NEW FINDING — PKG_PAYROLL.reverse_payroll Discards p_reason Silently [EDGE-CASE-FOUND]

`reverse_payroll(p_run_id, p_reason, p_user)` accepts p_reason but the body writes only STATUS='REVERSED' to PAYROLL_RUNS and PAYROLL_DETAILS. p_reason is passed to no column and not forwarded to PKG_AUDIT. PKG_AUDIT.log_action is called with ACTION_TYPE='UPDATE' and no old/new values. A payroll reversal has no recorded justification. Compliance audits of reversal events cannot determine why a run was reversed. Not in 23 violations.

---

### QR-023 — VERDICT REVISIT — CF-002 (Hire New Employee) Accuracy [EDGE-CASE-FOUND]

CF-002 step trigger is "HRMS_EMPLOYEE.fmb PRE-INSERT trigger" but steps 5–7 describe what PKG_EMPLOYEE.create_employee would do:
- Step 5: "PKG_EMPLOYEE.create_employee calls PKG_PAYROLL.create_salary_record" — does not occur via form; HRMS_EMPLOYEE.fmb PRE-INSERT does not call create_employee
- Step 6: "PKG_EMPLOYEE.create_employee calls PKG_AUDIT.log_action" — does not occur via form
- Step 7: "PKG_EMPLOYEE.create_employee calls PKG_NOTIFICATION.send_notification" — welcome email and manager notification are never sent through the form hire path

CF-002 conflates two distinct paths: the Oracle Forms DML path (what happens when a user creates an employee through the screen) and the package API path (what create_employee would do if called programmatically). These are different code paths with different side-effects.

**The actual form hire path is:** PRE-INSERT sets EMP_ID, EMP_NUMBER, ACTIVE_FLAG, EMPLOYMENT_STATUS, CREATED_BY, CREATED_DATE → commit → TRG_EMP_BEFORE_INSERT fires (validates hire date, checks email uniqueness, sets defaults) → EMPLOYEES row inserted. No salary, no notifications.

---

### QR-024 — VERDICT REVISIT — AV-018 Scope Understated [EDGE-CASE-FOUND]

AV-018 ("BTN_LEAVE and BTN_PERFORMANCE in HRMS_MENU.fmb have no permission check") is correct but understates the issue:

- HRMS_LEAVE.fmb WHEN-NEW-FORM-INSTANCE does NOT call `has_permission` before loading the form — any authenticated session accesses leave management
- HRMS_PERFORMANCE.fmb WHEN-NEW-FORM-INSTANCE does NOT call `has_permission` before loading the form — any authenticated session accesses performance management
- Contrast: HRMS_EMPLOYEE.fmb calls `has_permission('EMPLOYEE','EDIT')` and disables DML if false; HRMS_PAYROLL.fmb calls `has_permission('PAYROLL','VIEW')` and blocks entry entirely

The remediation in AV-018 states "Add has_permission checks for LEAVE and PERFORMANCE modules consistent with other buttons" — but the fix also requires WHEN-NEW-FORM-INSTANCE changes in both forms, not just menu button changes. Severity MEDIUM is correct; remediation scope is incomplete.

---

### QR-025 — VERDICT REVISIT — Risk Register Missing Entry for Lifecycle Procedures Orphaned from Forms [EDGE-CASE-FOUND]

The 12-risk register has no entry for the fact that terminate_employee, transfer_employee, and promote_employee are not called from any form, meaning:
- Manager notifications on termination (PKG_NOTIFICATION.send_notification to manager) never fire through the form path
- Manager notifications on promotion never fire
- PKG_PAYROLL.create_salary_record on promotion never fires through form (compensation changes written via direct SALARY_RECORDS block DML if at all)
- Benefits COBRA TODO, access revocation TODO, and final pay TODO in terminate_employee are therefore never even reached

This is a medium-severity finding affecting data integrity (salary records not linked to promotions) and compliance (COBRA integration, access revocation). Should be Risk 13 in the register.

---

## Issue Register — Pass 3 (Third Independent Analysis)

Focus: schema-level divergences, non-idempotent batch operations, unchecked status gates, silent queue gaps, and double-write patterns not covered in prior passes.

---

### QR-026 — NEW FINDING — DISC-003: EMPLOYEE_HISTORY Primary Key Column Name Divergence [EDGE-CASE-FOUND]

**severity:** High
**check:** TRG_EMP_BEFORE_UPDATE vs PKG_EMPLOYEE.log_history INSERT column lists

The two write paths to EMPLOYEE_HISTORY use different column names for the same primary key column AND a completely different column schema:

- `TRG_EMP_BEFORE_UPDATE` (trg_employees.sql): `INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON) VALUES (SEQ_EMP_HISTORY.NEXTVAL, ...)`
- `PKG_EMPLOYEE.log_history` (PKG_EMPLOYEE.pkb): `INSERT INTO EMPLOYEE_HISTORY (HIST_ID, EMP_ID, CHANGE_TYPE, EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION, REASON_CODE, COMMENTS, CREATED_BY, CREATED_DATE) VALUES (SEQ_EMP_HISTORY.NEXTVAL, ...)`

The PK column name is `HISTORY_ID` in the trigger and `HIST_ID` in the package. Both paths use SEQ_EMP_HISTORY. At least one of these INSERT statements fails at runtime with ORA-00904 "invalid column name". The trigger also uses a two-column generic model (OLD_VALUE VARCHAR2 / NEW_VALUE VARCHAR2) while the package uses a strongly typed multi-column model. These cannot coexist in a single physical table as described. This is a CRITICAL schema inconsistency that, if real, means one entire write path is broken in production.

**DISC-003:** HISTORY_ID (trigger) vs HIST_ID (package) in EMPLOYEE_HISTORY — unresolved column name conflict. Source: trg_employees.sql TRG_EMP_BEFORE_UPDATE; PKG_EMPLOYEE.pkb log_history. One INSERT path is broken.

---

### QR-027 — NEW FINDING — Business-Day Counting Divergence: PKG_COMMON Ignores Holidays; PKG_LEAVE Does Not [EDGE-CASE-FOUND]

**severity:** Medium
**check:** PKG_COMMON.business_days_between vs PKG_LEAVE.calculate_business_days behavior on a holiday date

Two functions compute business days, with different holiday awareness:

| Function | Source | Excludes Weekends | Excludes Holidays |
|---|---|---|---|
| PKG_COMMON.business_days_between | PKG_COMMON.pkb | YES | **NO** |
| PKG_COMMON.add_business_days | PKG_COMMON.pkb | YES | **NO** |
| PKG_LEAVE.calculate_business_days | PKG_LEAVE.pkb | YES | YES (HOLIDAYS table) |

PKG_COMMON date utilities are called anywhere business-day deadlines are computed outside the leave module. Any SLA window, hire date arithmetic, or notification deadline that calls `PKG_COMMON.business_days_between` will count public holidays as working days. The forward-engineering map notes "replace with standard library functions per language" but does not flag that the holiday-exclusion behavior is present only in PKG_LEAVE and must be explicitly replicated in the migration target.

---

### QR-028 — NEW FINDING — PKG_PAYROLL.reverse_payroll Has No Status Pre-Check [EDGE-CASE-FOUND]

**severity:** Medium
**check:** reverse_payroll body vs every other status-gated PKG_PAYROLL procedure

Every other state-changing PKG_PAYROLL procedure has a status guard:
- `create_payroll_run`: period STATUS != 'CLOSED'
- `close_pay_period`: STATUS != 'CLOSED'
- `approve_payroll`: STATUS = 'CALCULATED' exactly

`reverse_payroll` has no guard. Its body is unconditional:
```sql
UPDATE PAYROLL_RUNS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id;
UPDATE PAYROLL_DETAILS SET STATUS='REVERSED' WHERE RUN_ID=p_run_id;
```

A run in PENDING (never calculated), APPROVED (already funded), or already REVERSED status can be reversed without restriction. An approved and GL-exported payroll can be reversed post-funding with no authorization gate. Combined with QR-022 (p_reason discarded, no audit trail), any authenticated session can silently reverse any payroll run at any time with no logged justification. This is a distinct gap from QR-022 — that finding is about missing audit trail; this is about missing status validation. Together they constitute an integrity gap in payroll reversal.

Should be added as AV-024 MEDIUM.

---

### QR-029 — NEW FINDING — Non-EMAIL Notifications Queue Forever; process_queue Never Dispatches Them [EDGE-CASE-FOUND]

**severity:** Low
**check:** send_notification p_type parameter vs process_queue WHERE clause

`send_notification` inserts with any NOTIFICATION_TYPE value (default 'EMAIL', but accepts 'SMS', 'IN_APP', or any string). `process_queue` selects only: `WHERE STATUS='PENDING' AND NOTIFICATION_TYPE='EMAIL' AND RECIPIENT_EMAIL IS NOT NULL`. `retry_failed` resets FAILED records to PENDING — but non-EMAIL records never fail; they stay PENDING indefinitely.

Any non-EMAIL notification inserted into NOTIFICATION_QUEUE will never be dispatched and will never time out. The table grows without bound. There is no process_sms or process_in_app procedure. The "SMS unimplemented" note in forward-engineering-input-map.md is correct but understates the problem: non-EMAIL records already in the queue (from any call to send_notification with p_type != 'EMAIL') will silently disappear from the user's perspective while persisting in the database forever.

---

### QR-030 — NEW FINDING — PKG_LEAVE.run_monthly_accrual Is Non-Idempotent — Double-Run Produces Double Accrual [EDGE-CASE-FOUND]

**severity:** Medium
**check:** run_monthly_accrual idempotency vs AV-016 (expire_carryover)

`run_monthly_accrual` increments `LEAVE_BALANCES.ACCRUED = ACCRUED + v_accrued` and inserts a new LEAVE_ACCRUAL_LOG row per employee per leave type. There is no check whether accrual has already been run for the current month/year combination. If the DBMS_SCHEDULER job fires twice in the same month (scheduler misfire, manual re-run, or duplicate job definition), every active employee receives double accrual. LEAVE_ACCRUAL_LOG will contain two entries per employee per month.

AV-016 documents the identical idempotency gap for `expire_carryover`. The same gap in `run_monthly_accrual` — which processes all active employees monthly and is a higher-volume, higher-risk operation — is not in the 23 violations.

Remediation: before inserting accrual, check `SELECT COUNT(*) FROM LEAVE_ACCRUAL_LOG WHERE EMP_ID=... AND LEAVE_TYPE_ID=... AND EXTRACT(MONTH FROM ACCRUAL_DATE)=... AND EXTRACT(YEAR FROM ACCRUAL_DATE)=...` and skip if already accrued for this period.

---

### QR-031 — NEW FINDING — PKG_EMPLOYEE.promote_employee Has No EMPLOYMENT_STATUS Pre-Check [EDGE-CASE-FOUND]

**severity:** Low
**check:** promote_employee entry validation vs transfer_employee (status checked) and terminate_employee (status checked)

- `transfer_employee`: locks row with FOR UPDATE NOWAIT, then raises -20012 if `EMPLOYMENT_STATUS != 'ACTIVE'`
- `terminate_employee`: locks row with FOR UPDATE, then raises -20005 if `EMPLOYMENT_STATUS = 'TERMINATED'`
- `promote_employee`: reads `v_old_job_id` and `v_old_salary`, then immediately updates `EMPLOYEES.JOB_ID` and calls `PKG_PAYROLL.create_salary_record` with no status check

A TERMINATED or SUSPENDED employee can receive a promotion: a new salary record is created (ACTIVE_FLAG='Y') and JOB_ID is updated. This partially de-terminates the employee at the DB level without going through the rehire process (which would reset HIRE_DATE and clear termination fields). component-registry.json COMP-001 risk_flags notes this, but it is absent from the 23 violations.

Should be added as AV-025 LOW.

---

### QR-032 — NEW FINDING — PKG_SECURITY.change_password Does Not Verify the Old Password — Privilege Escalation Vector [EDGE-CASE-FOUND]

**severity:** Medium
**check:** change_password body for old-password verification step

AV-008 notes that `change_password` does not persist the new hash. There is a separate, exploitable gap not in AV-008: `p_old_password` is accepted as a parameter but is never compared to the stored hash. The procedure runs complexity checks on `p_new_password` only, with no SELECT from USER_CREDENTIALS to verify the caller knows the current password.

Consequence: any authenticated session can call `PKG_SECURITY.change_password(any_emp_id, 'anything', 'Valid1pw')` and the call succeeds (modulo the AV-008 persistence bug). Once AV-004 is fixed (password check implemented), this immediately enables a privilege escalation path: a low-grade user resets an administrator's password without knowing it, then authenticates as that administrator. The fix order matters: fixing AV-004 before fixing this makes the system vulnerable to privilege escalation.

Source: PKG_SECURITY.pkb change_password — p_old_password parameter unused; no query against USER_CREDENTIALS before complexity checks.

Should be added as AV-026 MEDIUM with explicit note about fix-order dependency.

---

### QR-033 — NEW FINDING — Double EMPLOYEE_HISTORY Writes from Package + Trigger on Same Lifecycle Operations [EDGE-CASE-FOUND]

**severity:** Low
**check:** PKG_EMPLOYEE lifecycle procedures + TRG_EMP_BEFORE_UPDATE combined firing analysis

`TRG_EMP_BEFORE_UPDATE` fires on every EMPLOYEES UPDATE and inserts EMPLOYEE_HISTORY rows whenever STATUS, DEPT_ID, or JOB_ID changes. The package lifecycle procedures that perform those very updates also call `log_history` explicitly before the UPDATE:

- `transfer_employee`: calls `log_history(CHANGE_TYPE='TRANSFER')` → UPDATE EMPLOYEES (DEPT_ID, JOB_ID change) → trigger inserts DEPARTMENT_CHANGE + JOB_CHANGE rows
- `terminate_employee`: calls `log_history(CHANGE_TYPE='TERMINATION')` → UPDATE EMPLOYEES (STATUS changes) → trigger inserts STATUS_CHANGE row
- `promote_employee`: calls `log_history(CHANGE_TYPE='PROMOTION')` → UPDATE EMPLOYEES (JOB_ID changes) → trigger inserts JOB_CHANGE row

Each lifecycle operation produces two EMPLOYEE_HISTORY entries for the same change: one from log_history (strongly typed, CHANGE_TYPE='TRANSFER'/'TERMINATION'/'PROMOTION') and one from the trigger (generic OLD_VALUE/NEW_VALUE strings, CHANGE_TYPE='DEPARTMENT_CHANGE'/'STATUS_CHANGE'/'JOB_CHANGE'). Audit queries counting lifecycle events will return double the actual count. Migration tooling reconstructing employee history will see duplicate events — compounded by the DISC-003 column-name gap (QR-026) where the two paths may not even be writing to compatible columns.

---

## Validation Checklist — Pass 2 Combined

| Check | Result | Notes |
|---|---|---|
| Procedure count: PKG_PAYROLL — source confirms? | PARTIAL | 17 in registry public_methods; 18 in source |
| Procedure count: PKG_PERFORMANCE — source confirms? | PARTIAL | 11 in extraction-audit; 12 in source |
| Package count: 11 — confirmed | PASS | All 11 confirmed |
| Form count: 6 — confirmed | PASS | All 6 confirmed |
| Trigger count: 6 — confirmed | PASS | 3 + 3 confirmed |
| Module boundaries justified with file evidence | PASS | All 11 cite source files |
| Every risk names specific source files | PASS | All 12 risks have evidence |
| JSON blocks valid | PASS | All 8 JSON files valid |
| Dependency graph edges reference declared nodes | PARTIAL | DBMS_SCHEDULER in .mmd not in JSON; 5 direct form-to-table edges missing |
| Discrepancies documented as DISC-### | PARTIAL | AV-013 and DISC-001 documented; DISC-002 (SSN drift) not in original output |
| Procedures defined but never called from forms | NEW GAP | [EDGE-CASE-FOUND] 21+ orphaned procedures identified; not enumerated in any output document |
| Form triggers calling packages not in primary analysis | PARTIAL | [EDGE-CASE-FOUND] 5 direct form-to-table edges missing; HRMS_PERFORMANCE bypasses PKG_PERFORMANCE entirely |
| CF-002 accurately reflects form hire path | FAIL | [EDGE-CASE-FOUND] Steps 5-7 describe package API, not form DML path; create_employee not called from form |
| SSN validation drift documented as violation | FAIL | [EDGE-CASE-FOUND] AV-014 covers email drift; SSN drift absent |
| Performance form bypass documented | FAIL | [EDGE-CASE-FOUND] Not in any output document |
| reverse_payroll reason discarded | NEW GAP | [EDGE-CASE-FOUND] Not in 23 violations |
| PKG_SECURITY.authenticate TOO_MANY_ROWS as distinct violation | PARTIAL | [EDGE-CASE-FOUND] In CF-001 notes only; not in violation register |
| EMPLOYEE_HISTORY write-path schema consistency | **FAIL** | [EDGE-CASE-FOUND] HISTORY_ID vs HIST_ID column name conflict (QR-026 / DISC-003) — one path broken at runtime |
| run_monthly_accrual idempotency | FAIL | [EDGE-CASE-FOUND] Non-idempotent; double-run doubles balances (QR-030) |
| reverse_payroll status gate | FAIL | [EDGE-CASE-FOUND] No status pre-check (QR-028) |
| change_password old-password verification | FAIL | [EDGE-CASE-FOUND] p_old_password never checked (QR-032) |
| Business-day function holiday parity | PARTIAL | [EDGE-CASE-FOUND] PKG_COMMON ignores holidays; PKG_LEAVE does not (QR-027) |
| promote_employee status check | PARTIAL | [EDGE-CASE-FOUND] No EMPLOYMENT_STATUS pre-check (QR-031) |
| Non-EMAIL notification dispatch | PARTIAL | [EDGE-CASE-FOUND] Queued forever, never dispatched (QR-029) |
| Double history writes from package + trigger | PARTIAL | [EDGE-CASE-FOUND] Audit counts inflated (QR-033) |

**Score: PARTIAL** — Core structural extraction is correct and complete. Pass 2 identifies material gaps in the analysis layer: (1) CF-002 conflates form DML path with package API path; (2) HRMS_PERFORMANCE.fmb bypass of PKG_PERFORMANCE silences all performance notifications; (3) 21+ orphaned procedures not enumerated; (4) 5 missing dependency edges; (5) 3 additional violations absent from register (SSN drift DISC-002, performance bypass, reverse_payroll reason loss). Pass 3 adds 8 further findings including one critical schema inconsistency (DISC-003: EMPLOYEE_HISTORY broken write path), two medium idempotency/authorization gaps, and a privilege escalation vector in change_password.

---

## Summary of All Issues — Combined Passes

| Issue | Severity | Pass | Status |
|---|---|---|---|
| QR-001 | Low | 1 | Procedure count off by 1: PKG_PAYROLL (17 vs 18) and PKG_PERFORMANCE (11 vs 12) |
| QR-002 / DISC-001 | Low | 1 | Sequence count 29 vs 30 between two Agent 1 output files |
| QR-006 | Low | 1 | DBMS_SCHEDULER in dependency diagram but not in JSON nodes array |
| QR-016 | Medium | 2 | [EDGE-CASE-FOUND] 21+ package procedures with no confirmed form entry point — not enumerated in any output |
| QR-017 | Medium | 2 | [EDGE-CASE-FOUND] 5 direct form-to-table dependency edges missing from dependency-graph.json |
| QR-018a | High | 2 | [EDGE-CASE-FOUND] HRMS_PERFORMANCE.fmb bypasses PKG_PERFORMANCE procedures — all performance notifications silenced |
| QR-018b | High | 2 | [EDGE-CASE-FOUND] HRMS_EMPLOYEE.fmb PRE-INSERT bypasses create_employee — no salary creation, no welcome notifications via form |
| QR-019 / DISC-002 | Medium | 2 | [EDGE-CASE-FOUND] SSN validation drift (client rejects zero-segments; server does not) not in violation register |
| QR-020 | Low | 2 | [EDGE-CASE-FOUND] PKG_COMMON.log_info lacks double-quote escaping — malformed JSON in INFO_LOG audit rows |
| QR-021 | Medium | 2 | [EDGE-CASE-FOUND] PKG_SECURITY.authenticate TOO_MANY_ROWS account-takeover path not a distinct violation |
| QR-022 | Low | 2 | [EDGE-CASE-FOUND] PKG_PAYROLL.reverse_payroll silently discards p_reason — no audit trail for reversal justification |
| QR-023 | High | 2 | [EDGE-CASE-FOUND] CF-002 steps 5-7 describe package API not form DML path — call flow is inaccurate for the form-driven hire |
| QR-024 | Medium | 2 | [EDGE-CASE-FOUND] AV-018 remediation scope understated — Leave and Performance forms also lack entry-point permission checks |
| QR-025 | Medium | 2 | Risk register missing entry for lifecycle procedures (terminate/transfer/promote) orphaned from forms |
| QR-026 / DISC-003 | **High** | 3 | [EDGE-CASE-FOUND] EMPLOYEE_HISTORY PK column named HISTORY_ID (trigger) vs HIST_ID (package) — one INSERT path is broken at runtime |
| QR-027 | Medium | 3 | [EDGE-CASE-FOUND] PKG_COMMON business-day functions ignore holidays; PKG_LEAVE does not — divergent behavior not flagged in forward-engineering map |
| QR-028 | Medium | 3 | [EDGE-CASE-FOUND] PKG_PAYROLL.reverse_payroll has no status pre-check — any authenticated session can reverse any run including funded/approved runs |
| QR-029 | Low | 3 | [EDGE-CASE-FOUND] Non-EMAIL notifications queue forever; process_queue never dispatches them — unbounded table growth, silent drop |
| QR-030 | Medium | 3 | [EDGE-CASE-FOUND] PKG_LEAVE.run_monthly_accrual non-idempotent — double-run produces double accrual for all active employees |
| QR-031 | Low | 3 | [EDGE-CASE-FOUND] PKG_EMPLOYEE.promote_employee has no EMPLOYMENT_STATUS check — terminated employees can receive promotions |
| QR-032 | Medium | 3 | [EDGE-CASE-FOUND] PKG_SECURITY.change_password does not verify old password — privilege escalation vector once AV-004 is fixed |
| QR-033 | Low | 3 | [EDGE-CASE-FOUND] Double EMPLOYEE_HISTORY writes from package log_history + TRG_EMP_BEFORE_UPDATE on same lifecycle operations |

---

## Overall Verdict: PARTIAL

The structural extraction (all 11 packages, 6 forms, 6 triggers, 22 tables, 6 views, 30 sequences) is correct and complete. All 5 critical security violations are accurately identified and sourced. All 25 business rule numeric values are exact.

Pass 2 reveals substantive gaps in the **analysis layer**:

**High-severity gaps:**
1. CF-002 is misleading. The form hire path does not invoke create_employee. Steps 5–7 (salary creation, audit, welcome notification) do not fire through the form. Migration teams building a hire endpoint based on CF-002 will ship without salary setup and without onboarding notifications.
2. HRMS_PERFORMANCE.fmb is a silent bypass. The form commits assessment data directly via block DML, completely bypassing PKG_PERFORMANCE procedures. No performance review notifications fire in the form-driven path. This should be a HIGH violation, not a missing observation.

**Medium-severity gaps:**
3. 21+ public procedures have no confirmed form path. Lifecycle operations (terminate, transfer, promote) contain notifications and integrations that are never triggered through the UI. If the package procedures are the canonical implementation and the form is calling them in production (in a complete-source scenario), this analysis is correct. If the form truly uses direct DML as confirmed in the spot-check XMLs, those side-effects are never firing.
4. DISC-002 (SSN validation zero-segment drift) is an unresolved conflict comparable to the documented email drift (AV-014) and should be formally registered.
5. PKG_SECURITY.authenticate's TOO_MANY_ROWS path is an account-takeover vector distinct from the general auth bypass.

These Pass 2 findings do not invalidate the migration sequence or the 5 critical security findings. They require targeted corrections to CF-002, additions to the violation register (4 new items), and an orphaned-procedure inventory before forward engineering begins.

**Pass 3 adds 8 further findings (QR-026 through QR-033):**

**High-severity addition:**
- QR-026 / DISC-003: EMPLOYEE_HISTORY has two incompatible write schemas (HISTORY_ID vs HIST_ID; generic vs typed columns). One of the two INSERT paths is broken at runtime with ORA-00904. This is not a theoretical risk — one code path produces no history records in production. Must be resolved before any data migration that reads EMPLOYEE_HISTORY.

**Medium-severity additions:**
- QR-030: run_monthly_accrual is non-idempotent. A duplicate scheduler fire doubles accrual balances for all employees. The same pattern flagged in AV-016 (expire_carryover) is present here at larger scale.
- QR-027: PKG_COMMON business-day utilities ignore holidays. Any downstream system that replaces PKG_COMMON date functions with standard library equivalents without also replicating holiday-exclusion logic will silently compute wrong business-day counts.
- QR-028: reverse_payroll has no status gate. An approved, GL-exported payroll can be reversed by any authenticated session.
- QR-032: change_password does not verify the old password. Post-AV-004-fix this becomes a privilege escalation path. Fix order: AV-004 must not be fixed without simultaneously fixing this.

**Low-severity additions:**
- QR-033: Double EMPLOYEE_HISTORY writes (package + trigger) inflate lifecycle event counts and will confuse migration tooling.
- QR-031: promote_employee allows promotion of terminated employees.
- QR-029: Non-EMAIL notifications accumulate indefinitely in NOTIFICATION_QUEUE.

Total violations identified across three passes that are absent from the original 23-entry register: **10 new violations** (QR-018a/b covered as one in register, QR-019, QR-020, QR-021, QR-022, QR-026/DISC-003, QR-028, QR-030, QR-031, QR-032). The structural extraction remains correct. All new findings are at the analysis and correctness layer.
