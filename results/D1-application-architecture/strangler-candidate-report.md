# Strangler Candidate Report
**System:** HRMS v4.2  
**Stage:** Stage 10 — Strangler Fig / Migration Candidates  
**Date:** 2026-08-03

---

## Overview

The HRMS is a legacy Oracle Forms 12c client-server monolith with all business logic in PL/SQL packages. The Strangler Fig pattern applies by extracting one module at a time behind a new REST/service interface while the Oracle Forms client continues to call the legacy layer during the transition period.

The ranking below orders modules by migration readiness: high readiness = fewer blockers, lower coupling, cleaner boundaries, no active critical bugs in the modernization path.

---

## Module Ranking: Migration Readiness

### Rank 1 — Performance (MOD-04) ★★★★★

**Readiness: HIGH**

| Dimension | Assessment |
|-----------|------------|
| Coupling score | 3 / 10 — lowest in the system |
| Circular dependencies | None |
| External integrations | None — only SMTP notifications (shared) |
| Active bugs | None blocking; rating label hard-coding is cosmetic |
| Tables owned | 3 (REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS) |
| Batch jobs | None (generate_reviews_for_cycle is a one-time operation, not scheduled) |
| Security violations | None specific to this module |

**Why extract first:**  
PKG_PERFORMANCE has no circular dependencies, no external file I/O, no scheduled jobs, and joins only EMPLOYEES (read-only). A REST API wrapping the 12 procedures can be built and tested independently. HRMS_PERFORMANCE.fmb can then be re-pointed to the REST API with minimal change.

**Strangler approach:**  
1. Build `PerformanceService` API (REST) wrapping PKG_PERFORMANCE procedures  
2. Migrate HRMS_PERFORMANCE.fmb calls to REST (or replace form with web UI)  
3. Run old and new in parallel with feature flag  
4. Decommission PKG_PERFORMANCE once stable

**Blockers:** None

---

### Rank 2 — Leave (MOD-03) ★★★★☆

**Readiness: HIGH**

| Dimension | Assessment |
|-----------|------------|
| Coupling score | 4 / 10 |
| Circular dependencies | None |
| External integrations | None — SMTP only (shared) |
| Active bugs | 2 (expire_carryover double-subtract; calculate_business_days observed holidays) |
| Tables owned | 5 (LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS, LEAVE_ACCRUAL_LOG, HOLIDAYS) |
| Batch jobs | 1 (run_monthly_accrual — DBMS_SCHEDULER DDL missing) |

**Why extract second:**  
Clear domain boundary. PKG_EMPLOYEE.terminate_employee calls PKG_LEAVE to cancel leave — this is a one-directional dependency that can be handled via a domain event (EmployeeTerminated → cancel pending leave). The two bugs must be fixed before migration.

**Strangler approach:**  
1. Fix expire_carryover idempotency bug and calculate_business_days observed holiday bug  
2. Recover DBMS_SCHEDULER DDL (or recreate it); migrate to a cron/job service  
3. Build `LeaveService` REST API  
4. Replace PKG_EMPLOYEE.terminate_employee → PKG_LEAVE cross-call with an event  
5. Migrate HRMS_LEAVE.fmb

**Blockers:** 2 bugs to fix; scheduler DDL must be recovered before migration

---

### Rank 3 — Notification / Audit (MOD-06 partial) ★★★★☆

**Readiness: HIGH**

| Dimension | Assessment |
|-----------|------------|
| Coupling | 10 / 10 — called by everything, but this means it should be infrastructure, not a domain module |
| Critical issue | SMTP config hard-coded; no TLS; new connection per email |
| Approach | Replace the implementation, not the interface |

**Why extract early:**  
PKG_NOTIFICATION and PKG_AUDIT are the shared infrastructure kernel. They should be replaced with proper observability (structured logging service) and messaging (AWS SES, SendGrid, or similar) early in modernization — before other modules are extracted. All modules call them through a thin interface that can be swapped.

**Strangler approach:**  
1. Replace PKG_NOTIFICATION with a proper async message queue (SQS, RabbitMQ) + email service (SES/SendGrid)  
2. Replace PKG_AUDIT with structured audit log (event store or append-only audit DB)  
3. All other modules call the new interface — no code change needed in callers

**Blockers:** None blocking; SMTP config must be moved to environment variables first

---

### Rank 4 — Security / Auth (MOD-05) ★★★☆☆

**Readiness: MEDIUM**

| Dimension | Assessment |
|-----------|------------|
| Coupling | 9 / 10 — all forms call is_session_valid on every navigation |
| Critical violations | 4 CRITICAL/HIGH security violations |
| Blocker | PKG_SECURITY.authenticate is a stub — no working auth |
| Encryption | Hard-coded AES key; all SSNs must be re-encrypted on migration |

**Why extract fourth:**  
This module is the most urgent from a security standpoint but has the most pre-work. The authentication stub must be fixed first (or replaced by an IdP). SSN re-encryption requires a key rotation plan that cannot be rushed.

**Strangler approach:**  
1. **Before migration:** Fix authenticate stub; implement brute-force protection; rotate encryption key; re-encrypt SSNs  
2. Replace PKG_SECURITY with OAuth2 / OIDC identity provider (Okta, Azure AD, Oracle IAM)  
3. Replace grade-based RBAC with proper role/permission model  
4. Oracle Forms session check becomes JWT validation

**Blockers:** CRITICAL — authentication stub must be fixed; encryption key rotation must be completed; USER_CREDENTIALS DDL must be located

---

### Rank 5 — Employee (MOD-01) ★★★☆☆

**Readiness: MEDIUM**

| Dimension | Assessment |
|-----------|------------|
| Coupling | 8 / 10 |
| Circular dependency | CYCLE-01 with PKG_PAYROLL — must be broken first |
| SQL injection | VIO-SEC-02 — must be fixed before any API wrapper |
| Active TODOs | COBRA, access revocation, final pay |
| Tables owned | 8 core tables |

**Why fifth:**  
Employee is the core domain entity referenced by every other module. Extracting it too early creates a shared service all other modules depend on. The circular dependency with Payroll must be resolved first. The SQL injection vulnerability is a critical blocker for any REST API exposure.

**Strangler approach:**  
1. Fix SQL injection in search_employees  
2. Replace generate_emp_number with SEQ_EMPLOYEE  
3. Break CYCLE-01 (introduce a SalaryInitializationService or event-driven approach)  
4. Implement COBRA/access revocation/final pay TODOs  
5. Extract as `EmployeeService`

**Blockers:** SQL injection; circular dependency; COBRA/final pay missing

---

### Rank 6 — Payroll (MOD-02) ★★☆☆☆

**Readiness: LOW**

| Dimension | Assessment |
|-----------|------------|
| Coupling | 8 / 10 |
| Circular dependency | CYCLE-01 with PKG_EMPLOYEE |
| Partial commits | VIO-ARCH-02 — critical data integrity risk |
| Hard-coded tax values | Will be wrong every new tax year |
| External integrations | GL journal file, ADP benefits feed — both vendor-specific |

**Why last:**  
Payroll is the highest-risk module. The partial-commit anti-pattern, hard-coded tax values, and external file integrations all need resolution before extraction. Payroll errors have direct financial and legal consequences.

**Strangler approach:**  
1. Move tax brackets to TAX_BRACKETS table (already exists in schema — currently unused by calculate_payroll)  
2. Refactor calculate_payroll to use BULK COLLECT/FORALL; remove partial commits  
3. Break CYCLE-01  
4. Replace UTL_FILE GL journal and ADP exports with API integrations or a dedicated integration service  
5. Extract as `PayrollService` — last

**Blockers:** Partial commits; hard-coded tax values; circular dependency; GL/ADP file integrations

---

## Recommended Migration Sequence

```
Phase 1 (Pre-migration security):
  - Fix PKG_SECURITY.authenticate stub
  - Rotate SSN encryption key
  - Fix SQL injection in search_employees

Phase 2 (Infrastructure replacement):
  - Replace PKG_NOTIFICATION with proper email service
  - Replace PKG_AUDIT with structured event log
  - Recover/document DBMS_SCHEDULER job DDL

Phase 3 (Domain extraction — low risk first):
  - Extract PerformanceService (MOD-04)
  - Extract LeaveService (MOD-03, after fixing bugs)

Phase 4 (Security modernization):
  - Replace PKG_SECURITY with OAuth2/OIDC IdP

Phase 5 (Core domain):
  - Break CYCLE-01 (PKG_EMPLOYEE ↔ PKG_PAYROLL)
  - Extract EmployeeService (MOD-01)

Phase 6 (Highest risk):
  - Fix payroll partial-commit and tax-config issues
  - Extract PayrollService (MOD-02)
```

---

## Components NOT Recommended for Strangler Extraction

| Component | Reason |
|-----------|--------|
| PKG_COMMON | Shared utility — inline into new services or replace with standard libraries |
| PKG_VALIDATION | Merge validation into each domain service |
| PKG_REPORTING | Replace with dedicated BI/reporting tool (Power BI, Metabase, etc.) |
| Oracle Forms (.fmb) | Rewrite as modern web UI; do not wrap/proxy |
