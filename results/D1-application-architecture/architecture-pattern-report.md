# Architecture Pattern Report — HRMS Oracle Forms Application

**Extractor:** AA Agent 1 — Application Architecture Extractor  
**Date:** 2026-08-04  
**Confidence:** 0.96  

---

## 1. Primary Detected Pattern: N-Tier Monolith (3-Tier)

**Pattern:** Three-tier monolithic architecture  
**Confidence:** 0.96  
**Evidence:**

| Tier | Technology | Components |
|------|-----------|------------|
| Presentation | Oracle Forms 12c (12.2.1.4) | 6 .fmb forms, 2 .pll libraries, 1 .mmb menu |
| Application Logic | Oracle PL/SQL packages (11 packages) | PKG_EMPLOYEE, PKG_PAYROLL, PKG_LEAVE, PKG_PERFORMANCE, PKG_NOTIFICATION, PKG_INTEGRATION, PKG_AUDIT, PKG_SECURITY, PKG_VALIDATION, PKG_COMMON, PKG_REPORTING |
| Data | Oracle RDBMS HRMS schema | 22 tables, 6 views, 29 sequences, 6 triggers |

All three tiers are deployed as a single logical unit. The Oracle Forms application connects directly to the Oracle database — there is no intermediate web service or REST API layer.

---

## 2. Secondary Detected Pattern: Big Ball of Mud (Partial)

**Pattern:** Big Ball of Mud — localized to Integration and cross-cutting modules  
**Confidence:** 0.72  
**Evidence:**
- PKG_INTEGRATION has no retry logic, no error escalation, and an unimplemented feature (import_time_attendance TODO stub)
- PKG_SECURITY contains an authentication stub — the password verification logic is incomplete
- PKG_PAYROLL has hard-coded 2024 tax brackets ignoring the TAX_BRACKETS table that was clearly designed to hold this data
- PKG_REPORTING.refresh_reporting_tables is an unimplemented stub
- TRG_EMP_BEFORE_INSERT duplicates business logic from PKG_EMPLOYEE (noted in trigger comment as anti-pattern)
- Circular dependency between PKG_EMPLOYEE and PKG_PAYROLL is a structural integrity violation

These are localized failures within an otherwise disciplined 3-tier design, rather than a system-wide Big Ball of Mud pattern.

---

## 3. Supporting Patterns Detected

### 3.1 Repository Pattern (partial)
**Confidence:** 0.80  
PL/SQL packages act as logical repositories for their domain entities (PKG_EMPLOYEE wraps EMPLOYEES table access, PKG_LEAVE wraps LEAVE_REQUESTS, etc.). However, the pattern is impure — some forms issue direct SQL against tables (e.g., HRMS_LOGIN form queries HRMS.EMPLOYEES directly; HRMS_EMPLOYEE form's QueryDataSourceName=HRMS.EMPLOYEES bypasses the package).

### 3.2 Façade Pattern
**Confidence:** 0.88  
PKG_COMMON serves as a system-wide utility façade (17 public methods), accessed by all 10 other packages. This is a deliberate design choice — all date math, formatting, and parameter lookups are centralized. The downside is that PKG_COMMON becomes the highest-coupled node in the dependency graph (afferent coupling = 11).

### 3.3 Observer / Asynchronous Queue Pattern
**Confidence:** 0.92  
PKG_NOTIFICATION implements a queue-based observer: business events enqueue notifications using PRAGMA AUTONOMOUS_TRANSACTION (so the enqueue never fails the caller), and a separate DBMS_SCHEDULER job processes the queue independently. This is a sound architectural choice for cross-cutting notifications.

### 3.4 Soft Delete Pattern
**Confidence:** 0.99  
Physical deletion of EMPLOYEES records is blocked by TRG_EMP_INSTEAD_OF_DELETE (raises ORA-20504). Termination sets ACTIVE_FLAG='N' and EMPLOYMENT_STATUS='TERMINATED'. All active-employee queries filter on EMPLOYMENT_STATUS='ACTIVE' or ACTIVE_FLAG='Y'. This is a deliberate and consistently applied pattern.

### 3.5 Audit Log Pattern (CRUD audit table)
**Confidence:** 0.99  
All DML on significant tables routes through PKG_AUDIT.log_action (via package calls and three DB-level triggers). AUDIT_LOG stores old/new values as VARCHAR2. The pattern is sound, but silent failure swallowing in log_action means audit gaps are possible without warning.

### 3.6 Session Token Pattern
**Confidence:** 0.96  
PKG_SECURITY.authenticate creates a session row in USER_SESSIONS and returns a numeric session_id stored in Oracle Forms global variables. All forms validate the session token on each significant action via HRMS_COMMON_LIB.check_session. Weakness: session timeout is based on LOGIN_TIME, not last activity — enforcing a hard 30-minute wall-clock limit regardless of use.

---

## 4. Anti-Patterns Detected

| Anti-pattern | Location | Evidence |
|---|---|---|
| Circular Dependency | PKG_EMPLOYEE ↔ PKG_PAYROLL | create_employee calls create_salary_record; calculate_payroll calls is_active |
| God Package | PKG_COMMON | Afferent coupling = 11; 17 diverse methods |
| Magic Numbers / Hard-Coded Config | PKG_PAYROLL, PKG_SECURITY, PKG_NOTIFICATION | 2024 tax brackets; AES key literal; SMTP hostname hard-coded |
| Duplicate Business Logic | TRG_EMP_BEFORE_INSERT vs PKG_EMPLOYEE | Hire date validation and email uniqueness in both trigger and package |
| Validation Drift | HRMS_VALIDATION_LIB vs PKG_VALIDATION/PKG_COMMON | Email subdomain handling, SSN all-zero check differ between client and server |
| Row-by-Row Cursor Processing | PKG_PAYROLL.calculate_payroll, PKG_PERFORMANCE.generate_reviews_for_cycle | No BULK COLLECT + FORALL pattern used |
| TODO Stubs in Production Code | PKG_INTEGRATION.import_time_attendance, PKG_EMPLOYEE.terminate_employee | Incomplete features deployed |
| Direct Table Access from UI | HRMS_LOGIN form, HRMS_EMPLOYEE form (QueryDataSourceName) | Bypasses package abstraction layer |
| Cleartext Credentials | SYSTEM_PARAMETERS (FTP credentials) | FTP password stored in plaintext in a DB table |
| Partial Commit Anti-pattern | PKG_PAYROLL.calculate_payroll, PKG_LEAVE.run_monthly_accrual | COMMIT every N rows leaves state partially updated on failure |

---

## 5. Layer Violations

| Violation | From | To | Description |
|---|---|---|---|
| LV-001 | Presentation | Data | HRMS_LOGIN form directly queries HRMS.EMPLOYEES (SELECT EMP_ID WHERE EMAIL = :username). Should go via PKG_EMPLOYEE.get_employee_by_number. |
| LV-002 | Presentation | Data | HRMS_EMPLOYEE form uses QueryDataSourceName=HRMS.EMPLOYEES — Oracle Forms direct block-to-table binding bypasses PKG_EMPLOYEE. |
| LV-003 | Presentation | Data | HRMS_VALIDATION_LIB.validate_salary_range executes SELECT directly against JOB_GRADES table. |
| LV-004 | Data Access | Application Service | TRG_EMP_BEFORE_INSERT duplicates hire date and email uniqueness logic from PKG_EMPLOYEE (trigger comment acknowledges this). |
| LV-005 | Application Service | Application Service (cross-module) | PKG_VALIDATION.is_business_day directly queries the HOLIDAYS table (owned by Leave module), creating a cross-module data dependency. |

---

## 6. Technology Observations

- **Oracle Forms 12c (12.2.1.4):** End-of-Premier Support. Oracle Forms is a legacy technology with no cloud-native deployment path. The Java applet delivery mechanism is deprecated in modern browsers.
- **PL/SQL as Application Layer:** Business logic is 100% in the Oracle database server. This is common for legacy Oracle apps but creates vendor lock-in and prevents horizontal scaling.
- **No Service Bus / API Gateway:** All integration is flat-file based (UTL_FILE). There is no REST, SOAP, or messaging middleware.
- **No ORM:** Direct SQL throughout. Schema changes require coordinated updates to all packages.
- **No Unit Test Framework:** No utPLSQL or other PL/SQL test framework found in source.

---

## 7. Forward Engineering Implications

| Finding | Implication |
|---|---|
| 3-tier monolith | Can be strangled module-by-module. Employee and Leave are the best first candidates (loosest coupling). |
| All business logic in PL/SQL | Migrating to microservices requires re-implementing all 11 packages in a new language. The packages are well-structured and provide a clear service contract. |
| No REST API layer | Adding an API gateway (e.g., Oracle REST Data Services) as a strangler proxy is the lowest-risk first step. |
| Hard-coded AES key | Must be rotated before any migration work begins. Re-encryption of SSN data required. |
| Circular dependency | Must be broken before PKG_EMPLOYEE and PKG_PAYROLL can be split into independent services. |
| Flat-file integrations | Each flat-file integration must be replaced with API calls during migration. ADP and Oracle Financials both offer REST APIs. |
| Oracle Forms UI | Requires full rewrite — no transpilation path from Forms to web UI. |
