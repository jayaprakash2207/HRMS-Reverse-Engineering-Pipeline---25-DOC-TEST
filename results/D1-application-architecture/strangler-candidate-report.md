# Strangler Migration Candidate Report — HRMS Oracle Forms Application

**Extractor:** AA Agent 1 — Application Architecture Extractor  
**Date:** 2026-08-04  
**Strategy:** Strangler Fig Pattern — incrementally replace legacy Oracle Forms + PL/SQL modules with modern services while keeping the system operational throughout migration.

---

## 1. Migration Readiness Overview

The HRMS is a 3-tier monolith with 11 logical modules. Each module maps to one PL/SQL package and zero or one Oracle Forms form. The modules are moderately well-bounded, making a module-by-module strangler approach viable. A proposed strangler proxy (e.g., Oracle REST Data Services or a thin API gateway) would sit in front of the PL/SQL packages and gradually route calls to new services as they are built.

**Critical pre-conditions for ANY migration to begin:**

| Pre-condition | Status | Action Required |
|---|---|---|
| AES key rotation | NOT DONE | Rotate key, re-encrypt all SSN fields (VIO-001) |
| Authentication implementation | NOT DONE | Implement real password verification (VIO-003) |
| SQL injection fix | NOT DONE | Fix PKG_EMPLOYEE.search_employees (VIO-002) |
| Circular dependency broken | NOT DONE | Break PKG_EMPLOYEE ↔ PKG_PAYROLL cycle (VIO-008) |
| TAX_BRACKETS externalized | NOT DONE | Move 2024 brackets to table, implement read logic (VIO-010) |

---

## 2. Module Ranking for Strangler Migration

Modules are ranked by: **migration risk (lower = better)**, **business value unlocked (higher = better)**, **decoupling effort (lower = better)**.

### Tier 1 — Migrate First (Low Risk, High Value)

#### MOD-011: Common (PKG_COMMON)
**Migration Risk:** LOW  
**Rationale:** No inbound functional dependencies (afferent = 10, but none are behavior-coupling). Pure utilities. Can be re-implemented as a shared library or configuration service that all migrated modules import. Must be migrated first as all other modules depend on it.  
**Strangler Approach:** Replace with a configuration microservice (GET /config/{group}/{code}) + shared utility library. No UI needed.  
**Blockers:** None.  
**Estimated Effort:** Small.

#### MOD-008: Audit (PKG_AUDIT)
**Migration Risk:** LOW  
**Rationale:** Efferent coupling = 0 (no outbound dependencies). Afferent = 9 (all callers). Its AUTONOMOUS_TRANSACTION isolation means callers never wait on audit. Can be replaced with a centralized audit service (e.g., writing to an append-only event store) without touching callers initially.  
**Strangler Approach:** Introduce an audit event bus (Kafka topic or simple REST endpoint). Legacy callers continue calling PKG_AUDIT; PKG_AUDIT becomes a thin adapter writing to the new bus.  
**Blockers:** None.  
**Estimated Effort:** Small-Medium.

---

### Tier 2 — Migrate Second (Medium Risk, High Value)

#### MOD-007: Notification (PKG_NOTIFICATION)
**Migration Risk:** LOW-MEDIUM  
**Rationale:** Afferent = 4, efferent = 1 (PKG_COMMON). Queue-based design maps cleanly to modern message brokers. SMS and IN_APP notification types exist in the schema but are unimplemented — new system can implement them.  
**Strangler Approach:** Replace NOTIFICATION_QUEUE + UTL_SMTP with a notification service (email provider API). Callers still call PKG_NOTIFICATION.send_notification; the package body is redirected to call the new service via UTL_HTTP.  
**Blockers:** SMTP server migration coordination.  
**Estimated Effort:** Medium.

#### MOD-010: Validation (PKG_VALIDATION + HRMS_VALIDATION_LIB)
**Migration Risk:** LOW-MEDIUM  
**Rationale:** Validation is stateless and side-effect-free. Migrating validation unlocks resolving the client/server validation drift (VIO-013). Can be implemented as a shared validation library that both the new UI and API use.  
**Strangler Approach:** Build a validation service or shared library. Replace PKG_VALIDATION calls in new services. Remove HRMS_VALIDATION_LIB from legacy forms once those forms are migrated.  
**Blockers:** Must define canonical validation rules before building.  
**Estimated Effort:** Small.

#### MOD-001: Employee (PKG_EMPLOYEE + HRMS_EMPLOYEE form)
**Migration Risk:** MEDIUM  
**Rationale:** Core business module. Highest afferent coupling (6 callers), but the module boundary is strong. Migrating Employee unlocks self-service portals and REST APIs for HRIS integrations. The SQL injection vulnerability (VIO-002) and circular dependency (VIO-008) must be resolved first.  
**Strangler Approach:** Build an Employee Service (REST API). Route read operations first (/employees/{id}, /employees/search) while writes still go through legacy. Migrate writes once service is stable. Oracle Forms HRMS_EMPLOYEE becomes a thin client calling the new API via a proxy package.  
**Blockers:** VIO-002 (SQL injection), VIO-008 (circular dep), VIO-009 (hire date discrepancy).  
**Estimated Effort:** Large.

---

### Tier 3 — Migrate Third (Medium Risk, Significant Value)

#### MOD-002: Leave (PKG_LEAVE + HRMS_LEAVE form)
**Migration Risk:** MEDIUM  
**Rationale:** Well-bounded module. Business rules are complex (accrual, carryover, holiday handling) but self-contained. Mobile self-service leave (referenced in PKG_LEAVE comments) is a strong business driver. Depends on Employee being migrated first.  
**Strangler Approach:** Build Leave Service. Migrate HRMS_LEAVE form to web UI as part of the same effort. Monthly accrual and carryover jobs become scheduled tasks in the new service.  
**Blockers:** Employee service must be migrated first (PKG_LEAVE calls PKG_EMPLOYEE implicitly via EMPLOYEES table queries).  
**Estimated Effort:** Large.

#### MOD-004: Performance (PKG_PERFORMANCE + HRMS_PERFORMANCE form)
**Migration Risk:** MEDIUM  
**Rationale:** Lowest afferent coupling of functional modules (1 caller). Performance reviews are a natural candidate for a dedicated SaaS integration or standalone service. Blocked only by Employee being available.  
**Strangler Approach:** Build Performance Service. Migrate HRMS_PERFORMANCE form to web UI. Notification integration is clean (already queue-based).  
**Blockers:** Employee service.  
**Estimated Effort:** Medium-Large.

---

### Tier 4 — Migrate Last (High Risk, Complex)

#### MOD-003: Payroll (PKG_PAYROLL + HRMS_PAYROLL form)
**Migration Risk:** HIGH  
**Rationale:** Highest compliance and financial risk. Hard-coded tax brackets (VIO-010), placeholder YTD fields (VIO-011), and the circular dependency with Employee (VIO-008) must all be resolved first. Row-by-row processing (VIO-018) needs re-architecture. Consider commercial payroll SaaS (ADP, Paylocity) rather than custom migration.  
**Strangler Approach:** (Option A) Replace with payroll SaaS, reroute ADP integration; (Option B) Build Payroll Service with externalized tax tables. Option A strongly preferred.  
**Blockers:** VIO-008 (circular dep), VIO-010 (tax brackets), VIO-011 (YTD), Employee service fully migrated.  
**Estimated Effort:** Very Large (or SaaS replacement).

#### MOD-006: Integration (PKG_INTEGRATION)
**Migration Risk:** HIGH  
**Rationale:** All three integration points need redesigning: GL (flat file → API), ADP (FTP → API), Time & Attendance (TODO stub). Depends on Employee, Payroll, and Leave being migrated. FTP credentials (VIO-005) must be resolved.  
**Strangler Approach:** Replace each integration point independently using the respective system's REST API. Build an integration middleware layer.  
**Blockers:** All upstream modules migrated; VIO-005 (cleartext creds).  
**Estimated Effort:** Large per integration point.

#### MOD-009: Security (PKG_SECURITY)
**Migration Risk:** HIGH  
**Rationale:** Cannot be migrated until authentication is actually implemented (VIO-003). Migration of Security should coincide with replacing Oracle Forms session management with a standards-based auth provider (OAuth2/OIDC). This is a prerequisite for all web-facing services.  
**Strangler Approach:** Introduce OAuth2 / OIDC provider (e.g., Keycloak, Auth0, Oracle IAM). Replace PKG_SECURITY.authenticate with SSO token validation in each new service. Legacy Forms can authenticate via a SAML adapter.  
**Blockers:** VIO-003 (auth stub), VIO-001 (encryption key), VIO-004 (MD5 hash).  
**Estimated Effort:** Large.

#### MOD-005: Reporting (PKG_REPORTING)
**Migration Risk:** MEDIUM  
**Rationale:** Pure read-only queries. The main blocker is that RPT_* reporting tables are referenced but not defined in schema. refresh_reporting_tables is a stub. Reporting is best migrated by connecting a BI/reporting tool (e.g., Oracle Analytics, Power BI) directly to the new services' data stores, rendering PKG_REPORTING obsolete.  
**Strangler Approach:** Expose read APIs from each migrated service. Connect BI tool. Retire PKG_REPORTING.  
**Blockers:** Other modules migrated first (reporting needs data from them).  
**Estimated Effort:** Medium (mostly BI configuration, not code).

---

## 3. Recommended Migration Sequence

```
Phase 0 (Security Remediation — mandatory before any migration):
  Fix VIO-001, VIO-002, VIO-003, VIO-004, VIO-008, VIO-010, VIO-011

Phase 1 (Infrastructure services):
  MOD-011 Common → configuration service + shared lib
  MOD-008 Audit  → audit event service / event bus
  MOD-009 Security → OAuth2/OIDC provider (Identity service)

Phase 2 (Core HR):
  MOD-010 Validation → shared validation library
  MOD-007 Notification → notification service
  MOD-001 Employee → Employee Service + web UI

Phase 3 (Workflow modules):
  MOD-002 Leave → Leave Service + web UI (self-service)
  MOD-004 Performance → Performance Service + web UI

Phase 4 (Financial and Integration):
  MOD-003 Payroll → SaaS replacement preferred
  MOD-006 Integration → API-based integration layer
  MOD-005 Reporting → BI tool integration
```

---

## 4. Oracle Forms Decommission Path

Oracle Forms cannot be incrementally strangled — it must be replaced module-by-module as each corresponding service is built. Recommended approach:
1. Build new web UI for each module as part of the module's service migration (Phase 2-4)
2. Run both old form and new web UI in parallel for UAT period
3. Disable old form once new UI is accepted
4. Decommission Oracle Forms server and WebLogic/OC4J instance after all forms are retired

**HRMS_REPORTS.fmb and HRMS_ADMIN.fmb** — these forms are referenced in the menu but not in the source set. They must be located and inventoried before migration planning is finalized.
