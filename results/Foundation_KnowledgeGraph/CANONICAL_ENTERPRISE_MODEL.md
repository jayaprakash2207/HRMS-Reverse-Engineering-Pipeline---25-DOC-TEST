# Canonical Enterprise Model — Acme Corporation HRMS (Oracle 19c)

**Version:** 1.0 — Derived from 140-rule BA analysis, DA multi-pass review, TA deep scan, AA quality review, and domain model derivation**
**Confidence:** Evidence-based; all claims traceable to source artifacts. Unconfirmed items flagged as [INFERRED].
**Scope:** Full Oracle 19c PL/SQL HRMS covering Employee Identity, Compensation, Leave, Performance, Benefits, Security, Notifications, Reporting, and Integration.

---

## 1. Enterprise Context

### 1.1 What This System Does

The Acme Corporation Human Resources Management System (HRMS) is an Oracle 19c-hosted, PL/SQL-driven enterprise application that manages the complete employee lifecycle — from hire through termination — for the Acme Corporation workforce. It handles employee record management, payroll calculation and approval, leave accrual and request processing, performance review cycles, benefits enrollment, and outbound integrations to ADP (benefits) and Oracle Financials (GL journal feed).

The system was built as a monolithic Oracle Forms + PL/SQL application. The application tier is Oracle Forms 12c (compiled .fmb → .fmx artefacts). The data and business logic tier is entirely PL/SQL packages operating on a shared HRMS schema. There is no microservice layer, no REST API surface, and no CI/CD pipeline. All deployment is manual.

### 1.2 Who Uses This System

| Role | Access Pattern | Notes |
|------|---------------|-------|
| HR Administrators | Full lifecycle operations: hire, terminate, transfer, payroll approval | Grade ≥ 8; full schema access via RBAC |
| HR Managers (Mid-tier) | Payroll run management, department reporting, performance cycle oversight | Grade 5–7; view-all access |
| Line Managers | Submit manager reviews, view team leave requests, approve leave | Grade 3–5; own-department access |
| Employees | Self-service: leave requests, self-assessment, bank account registration, notification consumption | Grade 1–4; own-record access only |
| Payroll Administrators | Run payroll, approve GL feeds, manage deductions | Subset of HR Admin grade |
| System / Scheduled Jobs | Nightly accrual, queue processing, reporting table refresh | DBMS_SCHEDULER; no human actor |
| External: ADP | Receives fixed-width benefits feed (203-char per record) | Pull integration; no inbound |
| External: Oracle Financials | Receives pipe-delimited GL journal file | File-drop integration |
| External: Time & Attendance System | Provides CSV attendance import (stub — unimplemented) | Inbound; not yet functional |
| Self-Service Portal | Calls PKG_LEAVE procedures over DB connection | Authentication model undocumented |

### 1.3 Why This System Exists

The system centralises all people-data operations for Acme Corporation, replacing or consolidating what would otherwise be fragmented spreadsheets, manual payroll runs, and disconnected HR forms. It serves as the system of record for:

- Employee identity (EMP_ID is the canonical identifier referenced by all downstream systems)
- Compensation history (point-in-time salary records)
- Leave entitlements and actual usage
- Performance ratings that gate merit pay eligibility
- Regulatory filings (EEO, tax withholding, COBRA — though several compliance paths are currently incomplete)

### 1.4 Technology Baseline

| Layer | Technology | Version | State |
|-------|-----------|---------|-------|
| Database | Oracle | 19c | Production |
| Business Logic | PL/SQL Packages | — | 9 core packages confirmed |
| Application UI | Oracle Forms | 12c | Forms compiled manually |
| Scheduler | DBMS_SCHEDULER | Oracle native | Used for payroll, queue, accrual |
| Integration | UTL_FILE flat files | Oracle native | Outbound only; inbound stubs |
| Encryption | DBMS_CRYPTO AES-256-CBC | Oracle native | Hard-coded key — critical defect |
| Authentication | Custom PKG_SECURITY | — | Password never verified (critical defect) |
| Reporting | PKG_REPORTING REF CURSORs | — | Direct OLTP queries; RPT_* refresh is a stub |
| CI/CD | None | — | 0 of 14 pipeline capabilities present |

---

## 2. Canonical Domain Model

### 2.1 Domain Taxonomy

The system spans one **Core Domain**, two **Supporting Sub-domains**, and two **Generic Sub-domains**.

| Domain Layer | Bounded Context | Justification |
|-------------|----------------|---------------|
| **Core Domain** | Employee Identity (BC-01) | The canonical root; EMP_ID propagates to every other context |
| **Core Domain** | Compensation (BC-02) | Direct business value; payroll is primary operational output |
| **Supporting** | Leave Management (BC-03) | Statutory obligation + employee entitlement |
| **Supporting** | Performance (BC-04) | Drives merit eligibility; gates compensation |
| **Supporting** | Benefits (BC-05) | Feeds ADP; drives external compliance |
| **Generic** | Security & Access (BC-06) | Cross-cutting; grade-based RBAC consumed by all contexts |
| **Generic** | Notifications (BC-08) | Cross-cutting; shared bus via NOTIFICATION_QUEUE |
| **Ancillary** | Organisational Structure (BC-07) | Shared kernel with BC-01 |
| **Ancillary** | Integration & Export (BC-09) | Anti-corruption layer to ADP and Oracle Financials |
| **Ancillary** | Reporting (BC-10) | Derived views; no write authority |

### 2.2 Bounded Context Detail

#### BC-01 — Employee Identity

**Aggregate Root:** `EMPLOYEES`
**Owning Package(s):** `PKG_EMPLOYEE`
**Tables:** `EMPLOYEES`, `DEPARTMENTS`, `JOB_POSITIONS`, `JOB_GRADES`, `JOB_TITLES`, `EMPLOYEE_HISTORY`, `TERMINATION_CODES`, `LOCATIONS`
**Core Invariants:**
- An employee must have a valid DEPARTMENT_ID, a grade within 1–10, and an EMPLOYMENT_STATUS within the allowed set.
- Three-part active filter: `EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= :date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > :date)` — all three conditions required.
- EMP_ID is the universal foreign key anchor for all other bounded contexts.

#### BC-02 — Compensation

**Aggregate Root:** `PAYROLL_RUNS`
**Owning Package(s):** `PKG_PAYROLL`, `PKG_COMPENSATION`
**Tables:** `SALARY_RECORDS`, `PAYROLL_RUNS`, `PAYROLL_DETAILS`, `DEDUCTION_RECORDS`, `JOB_GRADES`, `EMPLOYEE_BANK_ACCOUNTS` [referenced in schema; no code reads it]
**Core Invariants:**
- Monthly gross = BASE_SALARY / 12.
- Payroll runs proceed through a strict status lifecycle: DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED.
- Net pay = gross − total_deductions − federal_tax − state_tax − local_tax.
- Performance rating ≥ 3 is a gate for merit run inclusion (conformist dependency on BC-04).
- Direct deposit (EMPLOYEE_BANK_ACCOUNTS) is schema-designed but never executed — PAID status is a dead end.

#### BC-03 — Leave Management

**Aggregate Root:** `LEAVE_BALANCES`
**Owning Package(s):** `PKG_LEAVE`
**Tables:** `LEAVE_BALANCES`, `LEAVE_REQUESTS`, `LEAVE_TYPES`, `LOOKUP_VALUES`
**Core Invariants:**
- Accrual runs monthly via `run_monthly_accrual`; a defect exists where a retry INSERT uses assignment instead of increment.
- Available balance = opening + accrued − taken − pending.
- Requests with insufficient balance are rejected; FMLA leave bypasses balance check.
- FMLA leave type has `REQUIRES_DOCUMENT = 'N'` in seed data — a compliance gap.

#### BC-04 — Performance

**Aggregate Root:** `PERFORMANCE_REVIEWS`
**Owning Package(s):** `PKG_PERFORMANCE`
**Tables:** `PERFORMANCE_REVIEWS`, `REVIEW_CYCLES`, `PERFORMANCE_GOALS`, `GOAL_REVIEWS`
**Core Invariants:**
- Status lifecycle: `NOT_STARTED → SELF_REVIEW / MANAGER_REVIEW → COMPLETED → ACKNOWLEDGED`.
- OVERALL_RATING must be 1.0–5.0; RATING_LABEL is derived inline.
- `CALIBRATED_RATING` and `CALIBRATION_NOTES` exist in schema but are never written — calibration workflow is entirely absent from code.
- Reporting (`get_rating_distribution`) reads `OVERALL_RATING`, not `CALIBRATED_RATING`.

#### BC-05 — Benefits

**Aggregate Root:** `BENEFIT_ENROLLMENTS`
**Owning Package(s):** `PKG_INTEGRATION` (partial)
**Tables:** `BENEFIT_PLANS`, `BENEFIT_ENROLLMENTS`, `EMPLOYEE_DEPENDENTS`
**Core Invariants:**
- `export_benefits_feed` outputs fixed-width ADP format (203 chars/record).
- Active dependents are exported regardless of `BENEFITS_ENROLLED` flag — enrollment flag is never read.
- Dependent SSNs are stored encrypted; no decryption path for dependents confirmed.
- No file version header, record count trailer, or checksum on the ADP output file.

#### BC-06 — Security & Access

**Aggregate Root:** `USER_SESSIONS`
**Owning Package(s):** `PKG_SECURITY`
**Tables:** `USER_CREDENTIALS` [INFERRED — DDL not recovered], `USER_SESSIONS`, `AUDIT_LOG`
**Core Invariants:**
- Authentication is a stub: `authenticate()` never queries `USER_CREDENTIALS`; any valid username is authenticated regardless of password (critical defect, BR-042).
- Session validity = 30 minutes hard-coded; `SYSTEM_PARAMETERS` value is ignored.
- RBAC is grade-based: Grade ≥ 8 → full access; Grade 5–7 → view-all; Grade < 5 → own records only.
- `has_permission` uses Grade from `EMPLOYEES`, not from `USER_CREDENTIALS`.
- `change_password` never verifies old password before replacing it.
- Encryption key `HR$ystem_3ncrypt10n_K3y_2024!!` is hard-coded in source.

#### BC-07 — Organisational Structure

**Aggregate Root:** `DEPARTMENTS`
**Owning Package(s):** `PKG_EMPLOYEE` (shared)
**Tables:** `DEPARTMENTS`, `LOCATIONS`
**Core Invariants:**
- Shared kernel with BC-01: `EMPLOYEES.DEPARTMENT_ID` FK creates bidirectional dependency.
- Hierarchical query via `CONNECT BY PRIOR`; known performance degradation beyond 500 employees.
- `sync_org_structure` in PKG_INTEGRATION is a pure stub — it logs "Org structure sync completed" with no DML.

#### BC-08 — Notifications

**Aggregate Root:** `NOTIFICATION_QUEUE`
**Owning Package(s):** `PKG_NOTIFICATION`
**Tables:** `NOTIFICATION_QUEUE`, `NOTIFICATION_TEMPLATES`
**Core Invariants:**
- Queue-based delivery; retry count tracked.
- Callers construct message bodies inline; no TEMPLATE_ID or PAYLOAD column on the queue table.
- SMS channel is referenced in code but its handler is not implemented.

#### BC-09 — Integration & Export

**Aggregate Root:** (stateless; no dedicated tables)
**Owning Package(s):** `PKG_INTEGRATION`
**Core Invariants:**
- All integration is file-based outbound or stub inbound.
- `generate_gl_journal` writes pipe-delimited flat file; no GL_FEED_SENT_FLAG on `PAYROLL_RUNS`.
- `import_time_attendance` is a stub; reads a CSV path via UTL_FILE but writes no records.
- `sync_org_structure` is a stub; writes no records.

#### BC-10 — Reporting

**Aggregate Root:** `RPT_*` tables [INFERRED]
**Owning Package(s):** `PKG_REPORTING`
**Tables (inferred):** `RPT_HEADCOUNT`, `RPT_COMPENSATION`, `RPT_TURNOVER`, `RPT_NEW_HIRES`, `RPT_LEAVE_UTILIZATION`, `RPT_PAYROLL_SUMMARY`, `RPT_EEO_COMPLIANCE`
**Core Invariants:**
- All 7 report procedures query OLTP directly via REF CURSOR — RPT_* tables are never read by code.
- `refresh_reporting_tables` is a stub that only logs "Reporting tables refreshed" with no DML.
- `compensation_summary` uses Oracle `MEDIAN()` — no direct PostgreSQL/SQL Server equivalent.
- Fiscal year start is hard-coded as October 1.

---

## 3. Ubiquitous Language Dictionary

The following terms carry precise, system-specific meanings that may differ from general HR terminology. All definitions are grounded in confirmed PL/SQL source behavior.

| # | Term | Domain | Precise Definition |
|---|------|--------|--------------------|
| 1 | **Employee** | BC-01 | A person record in `EMPLOYEES` identified by EMP_ID. An employee may be ACTIVE, TERMINATED, ON_LEAVE, or SUSPENDED. "Employee" in business speech always means the ACTIVE subset unless qualified. |
| 2 | **Active Filter** | BC-01 | The mandatory three-part predicate applied to `EMPLOYEES`: `EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= :as_of AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > :as_of)`. All three conditions required; using only one or two is a defect. |
| 3 | **Grade** | BC-01, BC-06 | Integer 1–10 stored on `EMPLOYEES.GRADE`. Dual purpose: (a) compensation band assignment and (b) RBAC tier driver. Grade is the single field that controls system-wide access permissions. |
| 4 | **Hire** | BC-01 | The act of creating an EMPLOYEES row with EMPLOYMENT_STATUS = 'ACTIVE' and a HIRE_DATE. Triggers leave balance initialisation via PKG_LEAVE.initialize_balances. |
| 5 | **Termination** | BC-01 | The act of setting EMPLOYMENT_STATUS = 'TERMINATED' and TERMINATION_DATE on an EMPLOYEES row via PKG_EMPLOYEE.terminate_employee. In the current system: blocks new logins immediately; does NOT revoke active sessions, notify COBRA, inactivate dependents, inactivate bank accounts, or run final pay. |
| 6 | **Transfer** | BC-01 | A change to DEPARTMENT_ID, JOB_TITLE, or MANAGER_ID on an existing EMPLOYEES row. Logged to EMPLOYEE_HISTORY. |
| 7 | **Pay Run** | BC-02 | A single payroll processing execution represented by a `PAYROLL_RUNS` row. Produces one PAYROLL_DETAILS row per ACTIVE employee. |
| 8 | **Gross Pay** | BC-02 | `BASE_SALARY / 12` for monthly employees. The starting figure before all deductions and taxes. |
| 9 | **Net Pay** | BC-02 | `gross_pay − total_deductions − federal_tax − state_tax − local_tax`. The disbursable amount. In the current system, net pay reaches PAID status in PAYROLL_DETAILS but is never transferred to any bank account. |
| 10 | **Pay Element** | BC-02 | A named line item within a PAYROLL_DETAILS row identified by ELEMENT_ID. IDs 100, 101, 102, 103 are magic numbers in the payroll summary report with no descriptive cross-reference. |
| 11 | **Compa-Ratio** | BC-02 | `AVG(current_salary / grade_midpoint) × 100`. A value of 100 means average salary exactly at the grade midpoint. Used in compensation summary reports. |
| 12 | **Pay Period** | BC-02 | The date range covered by a Pay Run, defined by PAY_PERIOD_START and PAY_PERIOD_END on `PAYROLL_RUNS`. |
| 13 | **Merit Run** | BC-02 | A Pay Run where salary increases derived from performance ratings are applied. Employees with OVERALL_RATING < 3.0 are excluded from merit eligibility. |
| 14 | **Leave Balance** | BC-03 | The `LEAVE_BALANCES` row for a given employee and leave type in a given calendar year. Composed of: OPENING_BALANCE + ACCRUED − TAKEN − PENDING_APPROVAL. |
| 15 | **Accrual** | BC-03 | The monthly increment added to LEAVE_BALANCES.ACCRUED by `run_monthly_accrual`. Accrual rate varies by LEAVE_TYPE. |
| 16 | **Available Balance** | BC-03 | The computable leave an employee may take: `opening + accrued − taken − pending`. If this would go negative, requests are rejected (except FMLA). |
| 17 | **FMLA Leave** | BC-03 | Family and Medical Leave Act protected leave. In the current system, `REQUIRES_DOCUMENT = 'N'` — no documentation required. This is a compliance gap. |
| 18 | **Review Cycle** | BC-04 | A named performance appraisal period represented by a `REVIEW_CYCLES` row (e.g., "FY2024 Annual"). A cycle contains many PERFORMANCE_REVIEWS. |
| 19 | **Self-Assessment** | BC-04 | Employee-authored evaluation stored in `PERFORMANCE_REVIEWS.SELF_ASSESSMENT`. Submitted via `submit_self_assessment`; moves status to SELF_REVIEW. |
| 20 | **Overall Rating** | BC-04 | Manager-submitted numeric score (1.0–5.0) stored in `PERFORMANCE_REVIEWS.OVERALL_RATING`. Mapped to a RATING_LABEL inline. This is the operational rating used in all reports and compensation rules. |
| 21 | **Calibrated Rating** | BC-04 | An adjusted post-calibration score stored in `PERFORMANCE_REVIEWS.CALIBRATED_RATING`. In the current system, no procedure writes to this column — it is a dead column. Intended to represent HR/leadership-adjusted final rating. |
| 22 | **Acknowledgement** | BC-04 | Employee sign-off on a completed review. Stored in `EMPLOYEE_ACK_DATE`. Moves status to ACKNOWLEDGED. Final status in the current workflow. |
| 23 | **Benefits Feed** | BC-05 | The fixed-width flat file output of `PKG_INTEGRATION.export_benefits_feed`, delivered to the ADP vendor via Oracle directory `BENEFITS_FEED_OUT`. One 203-character record per employee-dependent pair. |
| 24 | **Benefits Enrolled** | BC-05 | The `EMPLOYEE_DEPENDENTS.BENEFITS_ENROLLED` flag (Y/N). In the current system, this flag is never read — all active dependents are exported regardless of this value. |
| 25 | **Session** | BC-06 | A `USER_SESSIONS` row created on successful `authenticate()` call. Valid for 30 minutes from LOGIN_TIME. Validity is only checked on next `is_session_valid()` call — no background sweep expires stale sessions. |
| 26 | **RBAC** | BC-06 | Role-Based Access Control. In this system, implemented as grade thresholds: grade ≥ 8 = full; 5–7 = view-all; < 5 = own-record only. Grade is read from `EMPLOYEES.GRADE` at runtime, not from a roles table. |
| 27 | **Encrypt / Decrypt** | BC-06 | AES-256-CBC-PKCS5 via `DBMS_CRYPTO`. Key is hard-coded as `HR$ystem_3ncrypt10n_K3y_2024!!`. Applied to SSN, bank account numbers. A key rotation mechanism does not exist. |
| 28 | **Soft Delete** | BC-01 through BC-08 | Setting `ACTIVE_FLAG = 'N'` on a row rather than issuing DELETE. All confirmed HRMS tables use this pattern. Physical rows are never deleted; history is preserved. |
| 29 | **Audit Log** | BC-06 | The `AUDIT_LOG` table receiving INSERT/UPDATE/DELETE events from triggers and ERROR/INFO messages from `PKG_COMMON.log_error` / `log_info`. All event types share one table with one retention policy — no separation by severity. |
| 30 | **Cost Centre** | BC-07 | A `DEPARTMENTS.COST_CENTER` value propagated into the Oracle Financials GL journal feed as the cost-centre field. Derived from the employee's DEPARTMENT_ID at payroll run time. |
| 31 | **Notification** | BC-08 | A `NOTIFICATION_QUEUE` row representing a pending message to an employee. Channels: EMAIL (implemented), SMS (handler absent). Body is constructed inline by the caller; no template substitution engine confirmed. |
| 32 | **Pay Stub / Payslip** | BC-02 | An email notification sent after payroll run completion. Triggered via PKG_NOTIFICATION from PKG_PAYROLL. Payslip content is not separately stored; notification body is the payslip. |
| 33 | **GL Journal** | BC-09 | A pipe-delimited flat file generated by `PKG_INTEGRATION.generate_gl_journal` containing debit/credit entries for Oracle Financials Journal Import. No GL_FEED_SENT_FLAG exists on PAYROLL_RUNS — there is no way to confirm a run's feed was consumed. |
| 34 | **Headcount** | BC-10 | Count of employees meeting the Active Filter as of a given date. Full-time, part-time, and contract employees are sub-categories in the headcount report. |
| 35 | **Turnover Rate** | BC-10 | `terminations_in_period / hires_up_to_end_date × 100`. Note: denominator is hires, not average headcount — this is non-standard vs. SHRM definition and produces non-comparable figures. |
| 36 | **Prenote** | BC-02 | A zero-dollar ACH pre-notification sent to a bank before the first live direct deposit, required by Nacha rules. `EMPLOYEE_BANK_ACCOUNTS.PRENOTE_SENT` / `PRENOTE_DATE` columns exist but no procedure populates them — Nacha compliance gap. |
| 37 | **EEO Category** | BC-01 | Equal Employment Opportunity job category assigned to a JOB_TITLE row. Used in `eeo_compliance_report`. No CHECK constraint enforces valid values — arbitrary strings can be stored. |
| 38 | **Employment Status** | BC-01 | The `EMPLOYEES.EMPLOYMENT_STATUS` column. Allowed values: ACTIVE, TERMINATED, ON_LEAVE, SUSPENDED. This is the primary gate for authentication (PKG_SECURITY checks this before allowing login), payroll inclusion, and leave request processing. |
| 39 | **Rating Label** | BC-04 | A derived text label mapped from OVERALL_RATING: ≥4.5 → Exceptional; ≥3.5 → Exceeds Expectations; ≥2.5 → Meets Expectations; ≥1.5 → Needs Improvement; <1.5 → Unsatisfactory. Computed inline in `submit_manager_review`. |
| 40 | **PAID Status** | BC-02 | A `PAYROLL_DETAILS.STATUS` value indicating payroll calculation is complete and net pay has been determined. In the current system, PAID is a terminal status only — no disbursement step follows, because `EMPLOYEE_BANK_ACCOUNTS` is never read. |
| 41 | **Qualifying Event** | BC-05 | An HR event (e.g., termination) that triggers a legal obligation under COBRA. Every termination processed by the system constitutes a qualifying event. The current `terminate_employee` procedure issues no COBRA notification — a federal compliance gap. |
| 42 | **Org Sync** | BC-07 | The `PKG_INTEGRATION.sync_org_structure` procedure, intended to synchronise org structure with an external LDAP/AD system. Currently a pure stub — it only logs a false success message. |
| 43 | **Three-Part Active Filter** | BC-01 | See entry #2. Named separately because omitting any leg of this filter is documented as a known defect pattern (DISC-001 through DISC-009). |
| 44 | **Tax Filing Status** | BC-02 | `EMPLOYEES.TAX_FILING_STATUS`. Values: SINGLE, MARRIED_FILING_JOINTLY, MARRIED_FILING_SEPARATELY, HEAD_OF_HOUSEHOLD. The HEAD_OF_HOUSEHOLD branch in the payroll tax calculation returns $0 federal tax — a confirmed defect. |

---

## 4. Core Business Rules Summary

The following 30 rules are the most consequential for system behavior, compliance, and migration fidelity. Source citations reference the confirmed PL/SQL or DDL evidence.

| # | Rule ID | Domain | Rule Statement | Severity | Source |
|---|---------|--------|---------------|----------|--------|
| 1 | BR-01 | BC-01 | The Three-Part Active Filter is mandatory for any query that must return only currently employed staff. All three conditions (status, hire date, termination date) are required. | Critical | PKG_EMPLOYEE.pkb |
| 2 | BR-042 | BC-06 | Authentication is a stub. `PKG_SECURITY.authenticate()` never queries `USER_CREDENTIALS`. Any valid username authenticates regardless of password submitted. | Critical | PKG_SECURITY.pkb |
| 3 | BR-019 | BC-02 | Direct deposit is non-functional. `EMPLOYEE_BANK_ACCOUNTS` is never read during any payroll lifecycle step. Net pay reaches PAID status but is never disbursed to any bank account. | Critical | PKG_PAYROLL.pkb |
| 4 | BR-TERM-01 | BC-01 | COBRA notification is entirely absent. Every termination creates a qualifying event with zero action taken. Federal 14-day notification window is never triggered. | Critical | PKG_EMPLOYEE.pkb |
| 5 | BR-TERM-03 | BC-02 | `PKG_PAYROLL.calculate_final_pay` does not exist. Every employee termination requires fully manual payroll outside the system. | Critical | PKG_EMPLOYEE.pkb (TODO comment) |
| 6 | BR-044 | BC-06 | `change_password` never verifies the old password. Any authenticated session can replace any employee's credential silently. | High | PKG_SECURITY.pkb |
| 7 | BR-021 | BC-06 | RBAC is grade-based: Grade ≥ 8 → full access; Grade 5–7 → view-all employees; Grade < 5 → own records only. `has_permission` reads EMPLOYEES.GRADE at runtime. | High | PKG_SECURITY.pkb |
| 8 | BR-026 | BC-06 | Session timeout is hard-coded at 30 minutes. The `SYSTEM_PARAMETERS` row for session timeout is ignored. Timeout is only evaluated on the next `is_session_valid()` call — no background sweep. | High | PKG_SECURITY.pkb |
| 9 | BR-073 | BC-06 | Termination immediately blocks new logins: `authenticate()` checks `EMPLOYMENT_STATUS = 'ACTIVE'`. But in-flight sessions remain valid for up to 30 minutes after termination (BR-72/73 gap). | High | PKG_SECURITY.pkb |
| 10 | BR-DEP-09 | BC-05 | Termination does not inactivate dependents. Terminated employees' dependents remain ACTIVE_FLAG = 'Y' and are exported on the next ADP benefits feed. | High | PKG_INTEGRATION.pkb, PKG_EMPLOYEE.pkb |
| 11 | BR-BA-12 | BC-02 | `EMPLOYEE_BANK_ACCOUNTS` is completely unreferenced in all confirmed PL/SQL packages. Direct deposit was designed but never implemented. | High | All packages |
| 12 | BR-HOH | BC-02 | Employees with TAX_FILING_STATUS = 'HEAD_OF_HOUSEHOLD' receive $0 federal income tax withholding. This is a confirmed payroll calculation defect. | High | PKG_PAYROLL.pkb |
| 13 | BR-CAL-01 | BC-04 | CALIBRATED_RATING and CALIBRATION_NOTES exist in the PERFORMANCE_REVIEWS schema but no procedure writes to either column. The calibration workflow is entirely absent. | High | PKG_PERFORMANCE.pkb |
| 14 | BR-043 | BC-10 | `refresh_reporting_tables` is a stub that only logs a success message. RPT_* tables are never populated. All 7 reports query live OLTP tables directly. | High | PKG_REPORTING.pkb |
| 15 | BR-ORG-02 | BC-07 | `sync_org_structure` unconditionally logs 'Org structure sync completed' regardless of actual execution. If scheduled, monitoring tools receive a permanent false-positive signal. | High | PKG_INTEGRATION.pkb |
| 16 | BR-LIB-05 | BC-03 | `run_monthly_accrual` retry block uses assignment (`SET ACCRUED = v_accrued`) instead of increment (`SET ACCRUED = ACCRUED + v_accrued`). Silently destructive if the retry fires on an existing row. | High | PKG_LEAVE.pkb |
| 17 | BR-41 | BC-06 | Password complexity (min 8 chars, ≥1 uppercase, ≥1 digit) is enforced only in `change_password`. A direct INSERT to `USER_CREDENTIALS` bypasses all checks. | High | PKG_SECURITY.pkb |
| 18 | BR-03 | BC-02 | Monthly gross = BASE_SALARY / 12. This is an annual-to-monthly division. No proration for mid-period hires or terminations is implemented. | Medium | PKG_PAYROLL.pkb |
| 19 | BR-07 | BC-02 | Federal income tax uses progressive bracket lookup. State tax uses a flat rate keyed by `EMPLOYEES.STATE`. Local tax defaults to 0 for unmapped states. | Medium | PKG_PAYROLL.pkb |
| 20 | BR-08 | BC-02 | Performance rating gate for merit: OVERALL_RATING ≥ 3 is required for a merit run salary increase. Employees below threshold are excluded silently. | Medium | PKG_PAYROLL.pkb |
| 21 | BR-15 | BC-03 | Leave requests with insufficient available balance are rejected. Exception: FMLA leave bypasses the balance check entirely. | Medium | PKG_LEAVE.pkb |
| 22 | BR-22 | BC-04 | A PERFORMANCE_REVIEWS row may only be submitted by the employee (self-assessment) or their direct manager. Cross-employee submission raises an application error. | Medium | PKG_PERFORMANCE.pkb |
| 23 | BR-DEP-05 | BC-05 | `BENEFITS_ENROLLED` flag on EMPLOYEE_DEPENDENTS is collected but never read in any query or export. All active dependents are included in the ADP feed regardless of enrollment. | Medium | PKG_INTEGRATION.pkb |
| 24 | BR-BA-04 | BC-02 | Account numbers in `EMPLOYEE_BANK_ACCOUNTS` are AES-256 encrypted. Routing numbers are stored in plain text. A decrypt procedure for bank accounts has not been identified. | Medium | 02_payroll_tables.sql |
| 25 | BR-BA-05 | BC-02 | ACH prenote columns (PRENOTE_SENT, PRENOTE_DATE) exist in `EMPLOYEE_BANK_ACCOUNTS` but are never populated. Nacha prenote requirement is not met. | Medium | 02_payroll_tables.sql |
| 26 | BR-43b | BC-06 | If two ACTIVE employees share an email address, `authenticate()` silently selects the employee with the lowest EMP_ID. The second employee cannot authenticate. | Medium | PKG_SECURITY.pkb |
| 27 | BR-045 | BC-06 | `e_account_locked` (ORA-20302) and `e_session_expired` (ORA-20303) are declared but never raised. Oracle Forms handlers for these exception names will never fire. | Medium | PKG_SECURITY.pks |
| 28 | BR-74 | BC-01 | Salary-grade validation in `PKG_EMPLOYEE.create_employee` runs only when `g_debug_mode = TRUE`. In production, employees can be created with salaries outside their grade band with no error. | Medium | PKG_EMPLOYEE.pkb |
| 29 | BR-DEP-06 | BC-05 | Dependent SSNs are stored AES-256 encrypted in `EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED`, but no decrypt procedure call for dependents has been identified — the data may be unrecoverable. | High | PKG_INTEGRATION.pkb, PKG_SECURITY.pkb |
| 30 | BR-LIB-01 | BC-03 | Leave balance initialisation (`initialize_balances`) must be called at hire. If not called, the employee has no LEAVE_BALANCES row and any leave request raises an error. | Medium | PKG_LEAVE.pkb |

---

## 5. Enterprise Integration Map

### 5.1 External System Integrations

| Integration ID | External System | Direction | Method | Package / Procedure | Status | Format |
|---------------|----------------|-----------|--------|-------------------|--------|--------|
| INT-01 | ADP (Benefits Vendor) | Outbound | Oracle UTL_FILE flat file | `PKG_INTEGRATION.export_benefits_feed` | Active | Fixed-width, 203 chars/record, `BENEFITS_YYYYMMDD.txt` |
| INT-02 | Oracle Financials (GL) | Outbound | Oracle UTL_FILE flat file | `PKG_INTEGRATION.generate_gl_journal` | Active | Pipe-delimited Journal Import format |
| INT-03 | Time & Attendance System | Inbound | Oracle UTL_FILE CSV | `PKG_INTEGRATION.import_time_attendance` | Stub — no DML | CSV; first line skipped; 4 columns: emp_number, date, hours_regular, hours_overtime |
| INT-04 | LDAP / Active Directory | Outbound (intended) | Unknown (no credentials or connection code) | `PKG_INTEGRATION.sync_org_structure` | Stub — no connection, no DML | Undetermined |
| INT-05 | HRMS Self-Service Portal | Inbound (DB call) | Oracle DB connection | `PKG_LEAVE` procedures | Active (DB connection credentials undocumented) | PL/SQL procedure call |
| INT-06 | Oracle Reports (.rdf) | Inbound (report pull) | REF CURSOR | `PKG_REPORTING.*` | Active | REF CURSOR return |
| INT-07 | HRMS Oracle Forms | Inbound (UI) | Oracle Forms TNS connection | All packages | Active | Oracle Forms TNS |
| INT-08 | DBMS_SCHEDULER | Internal | Oracle native | `run_monthly_accrual`, `process_notification_queue`, `refresh_reporting_tables` (stub) | Active for accrual and queue | PL/SQL direct call |

### 5.2 Integration Risk Summary

| Integration | Critical Gaps |
|------------|--------------|
| ADP Benefits Feed (INT-01) | No file version header; no record count trailer; no checksum; BENEFITS_ENROLLED flag not applied; dependent SSN not exported; no error if record exceeds 203 chars |
| Oracle Financials GL (INT-02) | No GL_FEED_SENT_FLAG on PAYROLL_RUNS; Journal Source/Category values undocumented; no missed-feed detection; no reconciliation |
| Time & Attendance (INT-03) | Complete stub; CSV rows are parsed and silently discarded; logs false success; no link to PAYROLL_DETAILS |
| LDAP/AD Sync (INT-04) | Complete stub; no connection parameters exist anywhere in source; logs false success on every call |
| Self-Service Portal (INT-05) | DB authentication model undocumented; if portal connects as schema owner, it has unrestricted DML on all HRMS tables |
| Reporting (INT-06) | RPT_* refresh is a stub; all report procedures hit live OLTP — no separation from transactional load |

---

## 6. Current System Strengths

The following capabilities represent working, tested, and value-delivering functionality that must be preserved in any migration or modernisation effort.

| # | Strength | Evidence | Migration Guidance |
|---|----------|----------|--------------------|
| S-01 | **Mature soft-delete pattern** | Consistent `ACTIVE_FLAG` across all core tables; history is fully preserved | Replicate soft-delete on all migrated tables; do not convert to hard-delete |
| S-02 | **Complete payroll calculation engine** | `PKG_PAYROLL.calculate_employee_pay` handles gross, deductions, federal bracket tax, state flat tax, local tax — all confirmed working | Extract and port the tax bracket logic; validate against historical run outputs |
| S-03 | **Grade-based RBAC is simple and consistent** | Single grade field on EMPLOYEES drives all permission checks; easy to reason about | Map to role-based claims in a modern auth system; preserve the grade-tier semantics |
| S-04 | **Robust leave request lifecycle** | `PKG_LEAVE` covers creation, approval, rejection, cancellation, and balance enforcement with consistent state transitions | Port the status machine and balance enforcement logic exactly |
| S-05 | **Performance review lifecycle** | `PKG_PERFORMANCE` covers self-assessment, manager review, acknowledgement with rating validation | Preserve the status machine; add the missing calibration step in migration |
| S-06 | **Comprehensive audit trail** | Triggers on major tables write to `AUDIT_LOG` with old/new values; all package actions log via PKG_COMMON | Migrate the trigger-based audit pattern; separate ERROR/INFO/DML into distinct tables in new system |
| S-07 | **AES-256 encryption for PII** | SSN and account numbers encrypted via DBMS_CRYPTO AES-256-CBC | Migrate to a proper key management system (AWS KMS / Azure Key Vault); preserve encryption scope |
| S-08 | **Queue-based notification delivery** | `NOTIFICATION_QUEUE` decouples senders from delivery; retry logic present | Migrate to a managed message queue (SQS, Azure Service Bus); preserve retry semantics |
| S-09 | **Monthly accrual scheduler** | `run_monthly_accrual` reliably accrues leave balances monthly via DBMS_SCHEDULER | Port accrual logic; fix the retry increment defect (BR-LIB-05) before migration |
| S-10 | **Seven operational reports with clear business logic** | All 7 `PKG_REPORTING` procedures are documented, correct (mostly), and actively used | Port each report query; replace Oracle MEDIAN() with a platform-native equivalent; fix fiscal year hard-coding |
| S-11 | **Structured salary history** | `SALARY_RECORDS` is a proper slowly-changing dimension (Type 2) for salary | Preserve full history; do not collapse to a single current-salary column |
| S-12 | **Split-deposit schema design** | `EMPLOYEE_BANK_ACCOUNTS` supports 4 DEPOSIT_TYPEs and PRIORITY_ORDER — a sophisticated design ready for implementation | Implement the missing disbursement step against this schema rather than redesigning |
| S-13 | **Dependent management schema** | `EMPLOYEE_DEPENDENTS` correctly models spouse/child/parent/domestic-partner/other with soft-delete | Preserve; implement the missing COBRA notification and benefits enrollment gate |
| S-14 | **Payroll status lifecycle** | DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED is a clean, auditable state machine | Port the lifecycle; add GL_FEED_SENT_DATE as a new terminal column |

---

## 7. Current System Weaknesses

The following are systemic defects, compliance gaps, architecture anti-patterns, and technical debts that migration must resolve — not carry forward.

| # | Weakness | Severity | Domain | Recommended Resolution |
|---|----------|----------|--------|----------------------|
| W-01 | Authentication is a stub — any username authenticates regardless of password | Critical | BC-06 | Implement real credential verification; adopt bcrypt or Argon2 for password hashing; retire MD5 |
| W-02 | AES-256 encryption key hard-coded in source (`HR$ystem_3ncrypt10n_K3y_2024!!`) | Critical | BC-06 | Migrate key to a managed key vault; implement key rotation; re-encrypt all affected columns |
| W-03 | COBRA notification entirely absent — every termination is a federal compliance violation | Critical | BC-01 | Implement COBRA qualifying event notification as a mandatory step in `terminate_employee` |
| W-04 | Direct deposit non-functional — EMPLOYEE_BANK_ACCOUNTS never read during payroll | Critical | BC-02 | Implement the disbursement step (read accounts → NACHA ACH file → advance to PAID) |
| W-05 | `calculate_final_pay` does not exist — all termination payroll is fully manual | Critical | BC-02 | Build the procedure; handle proration, PTO payout, and off-cycle run capability |
| W-06 | HEAD_OF_HOUSEHOLD tax filing status returns $0 federal tax — payroll defect | Critical | BC-02 | Fix the HOH branch in the tax bracket calculation; audit all HOH employees for back-withholding |
| W-07 | No CI/CD pipeline — 0 of 14 capabilities present; no automated build, test, deploy, or rollback | Critical | All | Establish a baseline pipeline with at minimum: SQL linting, schema migration versioning, automated smoke test, and secret scanning |
| W-08 | Nacha ACH prenote not implemented — Nacha compliance gap on every new bank account | High | BC-02 | Implement prenote step on account creation; integrate with ACH processor |
| W-09 | Calibrated rating is a dead column — calibration workflow entirely absent | High | BC-04 | Implement the calibration phase (status gate, write path, HR/leadership role) before migration |
| W-10 | `sync_org_structure` is a stub that logs false success — operational blind spot | High | BC-07 | Either implement the LDAP/AD sync or remove the procedure and its schedule; never leave a false-success stub running |
| W-11 | `refresh_reporting_tables` is a stub — RPT_* tables are never populated | High | BC-10 | Implement the ETL refresh or remove the RPT_* layer and formalise the direct-OLTP-query approach |
| W-12 | `import_time_attendance` is a stub — reads a CSV and discards all data | High | BC-09 | Implement the import with a proper staging table and PAYROLL_DETAILS link |
| W-13 | Routing numbers stored in plain text alongside encrypted account numbers | High | BC-02 | Encrypt routing numbers with the same mechanism (once key management is fixed) |
| W-14 | `change_password` does not verify old password before replacement | High | BC-06 | Add old-password verification as the first step |
| W-15 | Terminated employees' dependents remain active in ADP benefits feed | High | BC-05 | Add dependent inactivation to `terminate_employee`; policy question on COBRA hold period |
| W-16 | Leave accrual retry block uses assignment instead of increment (BR-LIB-05) — data corruption risk | High | BC-03 | Fix `SET ACCRUED = ACCRUED + v_accrued`; audit historical balances for affected employees |
| W-17 | `get_rating_distribution` reads pre-calibration OVERALL_RATING — reporting correctness defect | High | BC-04 | After implementing calibration, update the report to read CALIBRATED_RATING (or COALESCE) |
| W-18 | Grade-based RBAC implemented via a single integer field with no formal role definitions | Medium | BC-06 | Formalise roles; add IS_MANAGER flag to JOB_TITLES; remove grade-as-RBAC anti-pattern |
| W-19 | Session timeout is hard-coded; SYSTEM_PARAMETERS value ignored | Medium | BC-06 | Read timeout from SYSTEM_PARAMETERS; add a background sweep job for stale sessions |
| W-20 | GL feed has no sent-status tracking — missed feeds are undetectable | Medium | BC-09 | Add GL_FEED_SENT_DATE and GL_FEED_FILE_NAME to PAYROLL_RUNS |
| W-21 | Self-service portal DB connection credentials and grants are undocumented | Medium | BC-09 | Document and audit portal DB grants; create a dedicated least-privilege DB user |
| W-22 | No CI/CD secret scanning — hard-coded key persisted in git history | Critical | All | Run secret scanner retroactively on git history; rotate all exposed credentials |
| W-23 | FMLA leave requires no documentation (`REQUIRES_DOCUMENT = 'N'`) — audit compliance gap | Medium | BC-03 | Update seed data; implement supporting document enforcement in the request flow |
| W-24 | Salary-grade validation is debug-only — production allows out-of-band salaries silently | Medium | BC-01 | Elevate to a blocking error for all callers |
| W-25 | Oracle CONNECT BY hierarchy degrades beyond 500 employees | Medium | BC-07 | Replace with a closure table or path enumeration pattern in the target platform |
| W-26 | ADP benefits feed has no file header, trailer, or record count validation | Medium | BC-09 | Add version header, trailer with count, and per-record length assertion |
| W-27 | Password hashing uses MD5 — cryptographically broken | High | BC-06 | Replace with bcrypt (cost ≥ 12) or Argon2id |
| W-28 | No structured logging — all logs are free-text in a single AUDIT_LOG table with no correlation ID | Medium | All | Adopt structured JSON logging; add a correlation/request ID; separate error, info, and DML audit streams |
| W-29 | Oracle Forms compilation is manual with no documented build script | Medium | All | Document and script the Forms compilation process; include in CI pipeline |
| W-30 | BENEFITS_ENROLLED flag is collected but never enforced — ADP receives un-enrolled dependents | Medium | BC-05 | Apply `BENEFITS_ENROLLED = 'Y'` filter in `export_benefits_feed` |

---

## 8. Domain Events Catalogue

Domain events represent significant state transitions that have occurred or must occur within the system. Events marked **[UNIMPLEMENTED]** are implied by the schema or business rules but produce no actual event in the current codebase.

| Event ID | Event Name | Domain | Trigger | Published To / Downstream Effect | Status |
|----------|-----------|--------|---------|----------------------------------|--------|
| DE-01 | EmployeeHired | BC-01 | `PKG_EMPLOYEE.create_employee` completes | Leave balances initialised (PKG_LEAVE); notification queued; audit log written | Active |
| DE-02 | EmployeeTerminated | BC-01 | `PKG_EMPLOYEE.terminate_employee` completes | EMPLOYMENT_STATUS → TERMINATED; new logins blocked; audit log written | Active (partial) |
| DE-03 | EmployeeTransferred | BC-01 | Department / position change in PKG_EMPLOYEE | EMPLOYEE_HISTORY row written; audit log | Active |
| DE-04 | SalaryChanged | BC-02 | New SALARY_RECORDS row inserted | Previous row END_DATE set; audit log | Active |
| DE-05 | PayrollRunCreated | BC-02 | `PKG_PAYROLL.create_payroll_run` | Status = DRAFT; notification planned | Active |
| DE-06 | PayrollCalculated | BC-02 | `PKG_PAYROLL.calculate_payroll` completes | Status → CALCULATED; PAYROLL_DETAILS rows written | Active |
| DE-07 | PayrollApproved | BC-02 | `PKG_PAYROLL.approve_payroll` | Status → APPROVED; payslip notifications queued | Active |
| DE-08 | GLJournalGenerated | BC-09 | `PKG_INTEGRATION.generate_gl_journal` | Status → GL_GENERATED; flat file written to Oracle directory | Active |
| DE-09 | PayrollCompleted | BC-02 | Final status transition | Status → COMPLETED | Active |
| DE-10 | DirectDepositDisbursed | BC-02 | — | Net pay transferred to bank accounts via ACH | **[UNIMPLEMENTED]** |
| DE-11 | LeaveRequested | BC-03 | `PKG_LEAVE.submit_leave_request` | Status = PENDING; manager notification queued | Active |
| DE-12 | LeaveApproved | BC-03 | `PKG_LEAVE.approve_leave_request` | Status = APPROVED; LEAVE_BALANCES.pending incremented | Active |
| DE-13 | LeaveRejected | BC-03 | `PKG_LEAVE.reject_leave_request` | Status = REJECTED; balance unchanged; notification queued | Active |
| DE-14 | LeaveTaken | BC-03 | Leave end date passes / status set to TAKEN | LEAVE_BALANCES.taken incremented; pending decremented | Active |
| DE-15 | LeaveBalanceAccrued | BC-03 | `PKG_LEAVE.run_monthly_accrual` (DBMS_SCHEDULER) | LEAVE_BALANCES.accrued incremented | Active (defect in retry path) |
| DE-16 | ReviewCycleOpened | BC-04 | `PKG_PERFORMANCE.create_review` | PERFORMANCE_REVIEWS rows created with status NOT_STARTED | Active |
| DE-17 | SelfAssessmentSubmitted | BC-04 | `PKG_PERFORMANCE.submit_self_assessment` | Status → SELF_REVIEW | Active |
| DE-18 | ManagerReviewSubmitted | BC-04 | `PKG_PERFORMANCE.submit_manager_review` | Status → COMPLETED; OVERALL_RATING and RATING_LABEL set | Active |
| DE-19 | ReviewCalibrated | BC-04 | HR/leadership adjusts CALIBRATED_RATING | CALIBRATED_RATING and CALIBRATION_NOTES set; status → CALIBRATED | **[UNIMPLEMENTED]** |
| DE-20 | ReviewAcknowledged | BC-04 | `PKG_PERFORMANCE.acknowledge_review` | Status → ACKNOWLEDGED; EMPLOYEE_ACK_DATE set | Active |
| DE-21 | BenefitsFeedExported | BC-05 | `PKG_INTEGRATION.export_benefits_feed` | Fixed-width file written to BENEFITS_FEED_OUT directory; ADP receives | Active |
| DE-22 | DependentAdded | BC-05 | INSERT to EMPLOYEE_DEPENDENTS | ACTIVE_FLAG = 'Y'; included in next benefits feed | Active |
| DE-23 | DependentInactivated | BC-05 | ACTIVE_FLAG set to 'N' | Excluded from future benefits feed | Active (manual only; termination does not trigger this) |
| DE-24 | COBRAQualifyingEvent | BC-05 | Employee termination | 14-day notification window; COBRA election period begins | **[UNIMPLEMENTED]** |
| DE-25 | BankAccountRegistered | BC-02 | INSERT to EMPLOYEE_BANK_ACCOUNTS | Account ready for direct deposit; prenote should be sent | Active (schema); **[UNIMPLEMENTED]** (prenote + disbursement) |
| DE-26 | PasswordChanged | BC-06 | `PKG_SECURITY.change_password` | PASSWORD_HASH updated in USER_CREDENTIALS | Active (old password not verified) |
| DE-27 | SessionStarted | BC-06 | `PKG_SECURITY.authenticate` | USER_SESSIONS row created; session_id returned to caller | Active (password not verified) |
| DE-28 | SessionExpired | BC-06 | `is_session_valid` check fails due to 30-min timeout | Status → EXPIRED (lazy; no active expiry sweep) | Active (lazy only) |
| DE-29 | AccountLocked | BC-06 | Brute-force lockout threshold exceeded | LOGIN_ATTEMPTS incremented; LOCKED_UNTIL set | **[UNIMPLEMENTED]** |
| DE-30 | NotificationQueued | BC-08 | `PKG_NOTIFICATION.send_notification` | Row inserted to NOTIFICATION_QUEUE | Active |
| DE-31 | NotificationDelivered | BC-08 | `PKG_NOTIFICATION.process_queue` (DBMS_SCHEDULER) | EMAIL sent via UTL_SMTP or equivalent; STATUS → SENT | Active (EMAIL); SMS **[UNIMPLEMENTED]** |
| DE-32 | NotificationFailed | BC-08 | Delivery attempt fails | RETRY_COUNT incremented; re-queued for next cycle | Active |
| DE-33 | OrgSyncCompleted | BC-07 | `PKG_INTEGRATION.sync_org_structure` | False-positive log entry written; no actual sync | **[STUB — false event]** |
| DE-34 | ReportingTablesRefreshed | BC-10 | `PKG_REPORTING.refresh_reporting_tables` (scheduled) | False-positive log entry; RPT_* tables never populated | **[STUB — false event]** |
| DE-35 | TimeAttendanceImported | BC-09 | `PKG_INTEGRATION.import_time_attendance` | False-positive log entry; no rows written to any table | **[STUB — false event]** |
| DE-36 | AuditEventLogged | All | Any DML trigger or `PKG_COMMON.log_error` / `log_info` | Row inserted to AUDIT_LOG | Active |
| DE-37 | MeritEligibilityConfirmed | BC-04 → BC-02 | OVERALL_RATING ≥ 3.0 at merit run time | Employee included in merit salary increase calculation | Active (conformist integration) |
| DE-38 | MeritEligibilityDenied | BC-04 → BC-02 | OVERALL_RATING < 3.0 at merit run time | Employee silently excluded from merit run | Active |
| DE-39 | FinalPayCalculated | BC-02 | `PKG_PAYROLL.calculate_final_pay` | Prorated wages + PTO payout computed for terminated employee | **[UNIMPLEMENTED — procedure does not exist]** |
| DE-40 | AccessRevoked | BC-06 | `PKG_SECURITY.revoke_access` | All active sessions invalidated; USER_CREDENTIALS locked | **[UNIMPLEMENTED — procedure does not exist]** |

---

*Canonical Enterprise Model compiled from BA_Deep_Analyst.md (140 rules, 2-pass), DA_Data_Reviewer.md (3-pass, 44 hidden rules, 32 DQ findings), TA_Deep_Analyst.md (81 technical debts), AA_Quality_Review.md (33 findings), and the derived Domain Model (BC-01 through BC-10). All evidence is traceable to confirmed DDL, PL/SQL package bodies, or Oracle Forms XML exports.*
