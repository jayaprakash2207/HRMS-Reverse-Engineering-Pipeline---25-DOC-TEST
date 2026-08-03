# Forward Engineering Input Map
**System:** HRMS v4.2  
**Stage:** Stage 11 — Forward Engineering Map  
**Date:** 2026-08-03

This document maps the current legacy architecture to recommended target-state patterns and services. It is intended as input to D2 (Domain Model Extraction) and D3 (Modernization Blueprint) phases.

---

## Target Architecture Summary

**Pattern:** Modular Monolith → Microservices (strangler fig, incremental)  
**Database:** PostgreSQL (per-service) or Oracle DB with separated schemas  
**Presentation:** React/Vue SPA + REST API (replaces Oracle Forms)  
**Auth:** OAuth2 / OIDC Identity Provider (replaces PKG_SECURITY)  
**Messaging:** Async event bus (replaces PRAGMA AUTONOMOUS_TRANSACTION pattern)  
**Scheduling:** Cloud-native scheduler (replaces DBMS_SCHEDULER)  
**Notifications:** Managed email service (replaces UTL_SMTP)  

---

## Module-to-Service Mapping

### MOD-01 Employee → EmployeeService

| Legacy Component | Target Replacement |
|-----------------|-------------------|
| PKG_EMPLOYEE (18 procedures) | `EmployeeService` REST API |
| HRMS_EMPLOYEE.fmb | React `EmployeeManagement` SPA page |
| EMPLOYEES, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS, EMERGENCY_CONTACTS tables | PostgreSQL `employee_db` schema |
| TRG_EMPLOYEES_VALIDATE | Application-layer validation; retain DB constraints |
| TRG_EMPLOYEES_AUDIT | Domain event → AuditService |

**Key migration notes:**
- Fix SQL injection in search_employees before API exposure
- Replace generate_emp_number MAX+1 with DB sequence
- Implement COBRA notification, access revocation, final pay (currently TODO)
- Break circular dependency with PayrollService via SalaryCreatedEvent

**Proposed API endpoints:**
```
POST   /employees                    → create_employee
PUT    /employees/{id}               → update_employee
POST   /employees/{id}/terminate     → terminate_employee
POST   /employees/{id}/rehire        → rehire_employee
GET    /employees?filter=...         → search_employees (parameterized)
GET    /employees/{id}/org-chart     → get_org_chart
GET    /employees/{id}/history       → get_employee_history
```

---

### MOD-02 Payroll → PayrollService

| Legacy Component | Target Replacement |
|-----------------|-------------------|
| PKG_PAYROLL (15 procedures) | `PayrollService` REST API |
| HRMS_PAYROLL.fmb | React `PayrollProcessing` SPA page |
| PAYROLL_RUNS, PAYROLL_DETAILS, SALARY_RECORDS, etc. | PostgreSQL `payroll_db` schema |
| Hard-coded tax brackets | `TaxConfigService` + TAX_BRACKETS table with effective dates |
| UTL_FILE GL journal | REST call to Oracle Financials API (or managed ETL) |
| UTL_FILE ADP benefits feed | Configurable benefits integration adapter |

**Key migration notes:**
- Replace partial commits with transactional payroll calculation (single unit of work)
- Replace cursor FOR loop with bulk processing
- Move tax brackets and FICA wage base to TaxConfigService
- Replace UTL_FILE with API calls or managed file transfer
- Listen for `EmployeeCreatedEvent` to create initial salary record (break circular dep)

**Critical pre-conditions:**
1. Tax bracket table must be populated with multi-year data before migration
2. GL integration contract with Oracle Financials must be documented

---

### MOD-03 Leave → LeaveService

| Legacy Component | Target Replacement |
|-----------------|-------------------|
| PKG_LEAVE (14 procedures) | `LeaveService` REST API |
| HRMS_LEAVE.fmb | React `LeaveManagement` SPA page |
| LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS, LEAVE_ACCRUAL_LOG, HOLIDAYS | PostgreSQL `leave_db` schema |
| DBMS_SCHEDULER run_monthly_accrual | Cloud scheduler (cron) → `LeaveAccrualJob` |

**Key migration notes:**
- Fix expire_carryover idempotency before migration
- Fix calculate_business_days observed holiday handling
- Subscribe to `EmployeeTerminatedEvent` to cancel pending leave (remove direct PKG_EMPLOYEE → PKG_LEAVE call)
- Fix VW_LEAVE_SUMMARY AVAILABLE formula before migrating leave balance data

---

### MOD-04 Performance → PerformanceService

| Legacy Component | Target Replacement |
|-----------------|-------------------|
| PKG_PERFORMANCE (12 procedures) | `PerformanceService` REST API |
| HRMS_PERFORMANCE.fmb | React `PerformanceReviews` SPA page |
| REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS | PostgreSQL `performance_db` schema |

**Key migration notes:**
- Move rating label thresholds to configuration (currently hard-coded CASE expression)
- Goals currently not deletable (DeleteAllowed=No in form) — carry this constraint to new service

---

### MOD-05 Security → IdentityService (IdP)

| Legacy Component | Target Replacement |
|-----------------|-------------------|
| PKG_SECURITY.authenticate | OAuth2/OIDC Provider (Azure AD, Okta, Auth0) |
| PKG_SECURITY.is_session_valid | JWT validation middleware |
| PKG_SECURITY.has_permission | Role-based access control (RBAC) with permissions claims in JWT |
| PKG_SECURITY.encrypt_ssn / decrypt_ssn | AWS KMS / Azure Key Vault + application-layer encryption |
| PKG_SECURITY.hash_password | bcrypt / Argon2 in IdP |
| USER_SESSIONS table | IdP session management |
| :GLOBAL.session_id in Forms | JWT Bearer token in HTTP header |

**Key migration notes:**
- Hard-coded encryption key must be rotated BEFORE migration; all SSNs re-encrypted
- Grade-based RBAC must be mapped to explicit role definitions (HR_ADMIN, PAYROLL_ADMIN, EMPLOYEE, MANAGER)
- PKG_SECURITY.authenticate stub means current auth is broken — this is actually a migration enabler (less legacy to replicate)

---

### MOD-06 Integration / Cross-Cutting → Shared Services

| Legacy Component | Target Replacement |
|-----------------|-------------------|
| PKG_NOTIFICATION + DBMS_SCHEDULER | Message queue (SQS/RabbitMQ) + `NotificationService` + SES/SendGrid |
| PKG_AUDIT | Event-sourced `AuditService` with append-only store |
| PKG_COMMON | Standard library functions (date utils, formatting) inlined into each service |
| PKG_VALIDATION | Input validation in each service's API layer (Joi, Zod, Bean Validation) |
| PKG_REPORTING | Dedicated BI tool (Metabase, Power BI) connected to read replica |
| PKG_INTEGRATION | `IntegrationService` with pluggable adapters per vendor |
| HRMS_COMMON_LIB.pll | React shared hooks/components library |
| HRMS_VALIDATION_LIB.pll | Zod/Yup schemas in React form library |

---

## Data Migration Considerations

| Table | Rows (est.) | Migration Notes |
|-------|-------------|-----------------|
| EMPLOYEES | unknown | Include TERMINATED employees (soft-delete pattern — retain history) |
| SALARY_RECORDS | unknown | Multiple records per employee (history); carry all |
| LEAVE_BALANCES | unknown | Recalculate AVAILABLE before migration using correct formula |
| AUDIT_LOG | potentially millions | Migrate to time-series audit store; may need archival strategy |
| SSN data (encrypted) | unknown | Must re-encrypt with new key before migration |
| TAX_BRACKETS | currently unused by code | Populate with historical + current year data |

---

## Pre-Migration Mandatory Tasks

These must be completed before any service extraction begins:

1. **[SECURITY]** Fix PKG_SECURITY.authenticate stub — implement actual password verification  
2. **[SECURITY]** Rotate AES encryption key; re-encrypt all SSNs  
3. **[SECURITY]** Fix SQL injection in PKG_EMPLOYEE.search_employees  
4. **[COMPLIANCE]** Implement COBRA notification in terminate_employee  
5. **[COMPLIANCE]** Implement system access revocation in terminate_employee  
6. **[DATA]** Fix VW_LEAVE_SUMMARY AVAILABLE formula  
7. **[DATA]** Fix expire_carryover idempotency bug  
8. **[OPS]** Extract DBMS_SCHEDULER job DDL into source control  
9. **[OPS]** Document Oracle Directory object filesystem paths  
10. **[OPS]** Locate USER_CREDENTIALS table DDL (not found in repo)  
