# Architecture Pattern Report
**System:** HRMS v4.2  
**Stage:** Stage 7 — Architecture Pattern Detection  
**Date:** 2026-08-03

---

## Primary Pattern: Layered Monolith (N-Tier) with Big Ball of Mud characteristics

### Pattern Summary

The HRMS is a **two-tier client-server monolith** with a Layered Monolith structure:

| Tier | Technology | Role |
|------|------------|------|
| Presentation | Oracle Forms 12c (Java applet) | All user interaction; thin business logic in form triggers |
| Business Logic + Data | Oracle Database (PL/SQL packages) | All business rules, validation, integration, scheduling |
| External | UTL_FILE flat files, UTL_SMTP | Oracle Financials, ADP, SMTP relay |

The application exhibits strong characteristics of the **Layered N-Tier** pattern (presentation → business logic → data) but with significant **Big Ball of Mud** elements caused by years of organic growth.

---

## Layered Architecture Evidence

**Layer 1: Presentation (Oracle Forms)**  
- 6 scanned Forms (.fmb), 2 PLL libraries  
- Forms are thin delegates: button triggers call PL/SQL packages  
- `HRMS_COMMON_LIB.pll` provides toolbar, session-check, and error handling  
- `HRMS_VALIDATION_LIB.pll` provides client-side field validation  
- Evidence: All BTN_*.WHEN-BUTTON-PRESSED triggers call specific PKG_* procedures

**Layer 2: Business Logic (PL/SQL Packages)**  
- 11 packages, ~130 procedures/functions  
- All business rules, calculations, state transitions, and workflow orchestration  
- Evidence: PKG_PAYROLL.calculate_payroll, PKG_LEAVE.submit_leave_request, PKG_SECURITY.authenticate

**Layer 3: Data (Oracle Tables/Views/Triggers)**  
- 26 tables, 6 views, 6 triggers, 29 sequences  
- DB triggers enforce referential constraints and automatic audit logging  
- Evidence: TRG_EMPLOYEES_VALIDATE, TRG_EMPLOYEES_AUDIT, VW_ORG_HIERARCHY

---

## Big Ball of Mud Evidence

Despite the nominal layering, several Big Ball of Mud anti-patterns are present:

**1. Business logic in presentation layer**  
Hire date validation (90-day limit) is encoded in HRMS_EMPLOYEE.fmb form trigger, duplicating (and contradicting) the DB trigger rule. Forms are not pure presentation.

**2. Cross-layer shortcuts (DB triggers → PL/SQL packages)**  
TRG_EMPLOYEES_AUDIT calls PKG_AUDIT.log_action, coupling the data layer to the business logic layer. This creates a hidden execution path invisible to the forms layer.

**3. No API boundary between layers**  
Oracle Forms directly calls PL/SQL procedures by name. There is no service interface, no contract versioning, no API gateway. Changes to PL/SQL procedure signatures require coordinated form updates.

**4. Shared mutable state via package globals**  
PKG_EMPLOYEE uses package-level variables (g_current_user, g_current_emp_id) and Oracle Forms uses :GLOBAL.session_id / :GLOBAL.current_user. Both are process-scoped globals that create implicit coupling.

**5. Infrastructure code mixed into domain packages**  
Every domain package (Employee, Payroll, Leave, Performance) directly calls PKG_AUDIT.log_action and PKG_NOTIFICATION.send_notification. There is no domain event bus — audit and notification are wired into every procedure body.

---

## Secondary Patterns Detected

### Transaction Script
- PKG_PAYROLL.calculate_payroll, PKG_LEAVE.run_monthly_accrual  
- Each procedure is a top-to-bottom imperative script with explicit SQL and control flow  
- No domain object model; data is passed as scalar parameters and returned in REF CURSORs

### Repository Pattern (partial)
- PKG_EMPLOYEE, PKG_PAYROLL, PKG_LEAVE each own their data access (INSERT/UPDATE/SELECT) within their procedures  
- No separation of concerns: the package is simultaneously the service, the repository, and the domain object

### Façade Pattern
- PKG_COMMON is a façade over shared utilities (logging, config, date math, formatting)
- HRMS_COMMON_LIB.pll is a façade over PKG_SECURITY.is_session_valid and PKG_COMMON.log_error for the Forms layer

### Async Queue Pattern
- PKG_NOTIFICATION implements a simple async notification queue via NOTIFICATION_QUEUE table  
- Producer (send_notification with PRAGMA AUTONOMOUS_TRANSACTION) is decoupled from consumer (process_queue via DBMS_SCHEDULER)  
- Pattern is sound; implementation has issues (SMTP config hard-coded, no connection pooling)

### Soft Delete Pattern
- EMPLOYEES table uses ACTIVE_FLAG='N' and EMPLOYMENT_STATUS='TERMINATED' instead of DELETE  
- All queries filter on EMPLOYMENT_STATUS='ACTIVE' or use VW_ACTIVE_EMPLOYEES  
- Consistent throughout the codebase

### Audit Trail Pattern
- Every DML on EMPLOYEES, SALARY_RECORDS, LEAVE_REQUESTS is captured by database triggers that call PKG_AUDIT.log_action (PRAGMA AUTONOMOUS_TRANSACTION)  
- AUDIT_LOG table records: table_name, record_id, action, old_values (CLOB), new_values (CLOB), user, IP, session  
- Pattern is consistent; implementation is brittle (AUDIT_LOG lock could cascade to all DML)

---

## Observed Anti-Patterns

| Anti-Pattern | Instance | Evidence |
|--------------|----------|----------|
| Partial Commit | calculate_payroll COMMIT every 50 rows | PKG_PAYROLL.pkb |
| Partial Commit | run_monthly_accrual COMMIT every 100 rows | PKG_LEAVE.pkb |
| Magic Numbers | ELEMENT_IDs 100-103 in reporting | PKG_REPORTING.pkb |
| Magic Numbers | GRADE_ID thresholds 5, 8 in security | PKG_SECURITY.pkb |
| Hard-coded Config | SMTP host, tax brackets, FICA wage base | PKG_NOTIFICATION.pkb, PKG_PAYROLL.pkb |
| God Package | PKG_COMMON — 16 functions, called by 9 packages | PKG_COMMON.pks |
| Circular Dependency | PKG_EMPLOYEE ↔ PKG_PAYROLL | PKG_EMPLOYEE.pks comment |
| Stub Implementation | import_time_attendance, sync_org_structure | PKG_INTEGRATION.pkb |

---

## Architecture Quality Assessment

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Modularity | 4/10 | Six logical modules identified but tightly coupled via shared tables and direct package calls |
| Testability | 2/10 | No unit tests found; circular dependency; PL/SQL without test harness; Oracle Forms unautomatable |
| Deployability | 3/10 | Single Oracle schema deployment; no CI/CD evidence; Forms binary deployment manual |
| Observability | 5/10 | AUDIT_LOG is thorough; no structured metrics or distributed tracing |
| Security | 2/10 | Hard-coded key, broken auth stub, SQL injection, MD5 passwords — multiple critical issues |
| Data Integrity | 5/10 | DB triggers enforce audit; partial commits undermine transactional integrity |
| Scalability | 2/10 | Oracle Forms is not horizontally scalable; single DB schema; no caching layer |
| Maintainability | 4/10 | Package structure is clear; hard-coded values and TODO stubs reduce maintainability |
