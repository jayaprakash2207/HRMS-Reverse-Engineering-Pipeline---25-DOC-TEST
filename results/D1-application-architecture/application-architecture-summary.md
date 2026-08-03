# Application Architecture Summary
**System:** HRMS v4.2 (Build 2024.03.15)  
**Stage:** D1 — Application Architecture Extraction  
**Agent:** AA Agent 1 — Application Architecture Extractor  
**Date:** 2026-08-03  
**Confidence:** High — all findings directly evidenced from source code or Layer 1 JSON

---

## 1. System Identity

| Field | Value |
|-------|-------|
| System name | HRMS — Human Resource Management System |
| Version | v4.2 Build 2024.03.15 |
| Architecture style | Two-tier client-server Layered Monolith |
| Presentation layer | Oracle Forms 12c (12.2.1.4) — Java applet served via Oracle WebLogic/Forms Services |
| Business logic layer | Oracle PL/SQL — 11 packages, ~130 procedures/functions |
| Data layer | Oracle Database — single schema (HRMS), 26 tables, 6 views, 29 sequences, 6 triggers |
| Deployable units | 1 Oracle Forms application + 1 Oracle Database schema |
| Source repo | `ts-plsql-oracle-forms-hrms-main/` |

---

## 2. Module Structure (6 Modules)

| Module | Packages | Forms | Coupling |
|--------|----------|-------|---------|
| MOD-01 Employee | PKG_EMPLOYEE | HRMS_EMPLOYEE.fmb | 8/10 ⚠ Circular dep |
| MOD-02 Payroll | PKG_PAYROLL | HRMS_PAYROLL.fmb | 8/10 ⚠ Circular dep |
| MOD-03 Leave | PKG_LEAVE | HRMS_LEAVE.fmb | 4/10 ✓ |
| MOD-04 Performance | PKG_PERFORMANCE | HRMS_PERFORMANCE.fmb | 3/10 ✓ |
| MOD-05 Security/Auth | PKG_SECURITY | HRMS_LOGIN.fmb | 9/10 ⚠ Cross-cutting |
| MOD-06 Integration/Cross-cutting | PKG_INTEGRATION, PKG_NOTIFICATION, PKG_AUDIT, PKG_COMMON, PKG_VALIDATION, PKG_REPORTING | HRMS_MENU.fmb + 2 PLL libs | 10/10 (shared kernel) |

**Circular dependency:** PKG_EMPLOYEE.create_employee → PKG_PAYROLL.create_salary_record → PKG_EMPLOYEE.is_active (CYCLE-01)

---

## 3. Component Inventory

| Type | Count |
|------|-------|
| PL/SQL packages (spec + body) | 11 packages (22 files) |
| PL/SQL procedures/functions | ~130 |
| Oracle Forms (.fmb) — scanned | 6 |
| Oracle Forms (.fmb) — referenced only | 2 (HRMS_REPORTS, HRMS_ADMIN) |
| PLL libraries | 2 |
| Database tables | 26 |
| Database views | 6 |
| Database triggers | 6 |
| Database sequences | 29 |
| Scheduled jobs | 2 (DBMS_SCHEDULER DDL not in source control) |
| External system integrations | 3 active + 2 stubs |

---

## 4. Architecture Pattern

**Primary:** Layered Monolith / N-Tier (Presentation → Business Logic → Data)  
**Secondary characteristics:** Big Ball of Mud (business logic in form triggers, no API boundaries, package globals, infrastructure code in domain packages)  
**Notable patterns:** Transaction Script, Soft Delete, Audit Trail, Async Queue (PKG_NOTIFICATION), Façade (PKG_COMMON, HRMS_COMMON_LIB)

---

## 5. Critical Security Findings

| ID | Severity | Finding |
|----|----------|---------|
| VIO-SEC-01 | 🔴 CRITICAL | AES-256 encryption key hard-coded as plaintext constant in PKG_SECURITY.pkb |
| VIO-SEC-02 | 🔴 CRITICAL | SQL injection in PKG_EMPLOYEE.search_employees (dynamic SQL via string concat) |
| VIO-SEC-03 | 🔴 HIGH | MD5 password hashing (DBMS_CRYPTO.HASH_MD5) — cryptographically broken |
| VIO-SEC-04 | 🔴 HIGH | No brute-force protection on PKG_SECURITY.authenticate |
| VIO-SEC-05 | 🔴 HIGH | change_password does not verify old password |
| VIO-SEC-06 | 🔴 HIGH | authenticate is a stub — no actual password verification implemented |

---

## 6. Critical Architecture Violations

| ID | Severity | Finding |
|----|----------|---------|
| VIO-ARCH-01 | HIGH | Circular dependency PKG_EMPLOYEE ↔ PKG_PAYROLL |
| VIO-ARCH-02 | HIGH | Partial commits in calculate_payroll (every 50 rows) — data corruption on failure |
| VIO-ARCH-03 | HIGH | Partial commits in run_monthly_accrual (every 100 rows) |
| VIO-ARCH-04 | MEDIUM | Business logic (hire date validation) in Oracle Forms trigger |
| VIO-ARCH-05 | MEDIUM | Hard-coded config: SMTP host, 2024 tax brackets, FICA wage base $168,600 |
| VIO-DATA-01 | HIGH | Hire date limit inconsistency: Form=90 days, DB trigger=180 days |
| VIO-DATA-02 | MEDIUM | VW_LEAVE_SUMMARY AVAILABLE omits PENDING days |
| VIO-DATA-03 | MEDIUM | Race condition in generate_emp_number (no SELECT FOR UPDATE) |
| VIO-DATA-04 | MEDIUM | expire_carryover double-subtract bug (no idempotency guard) |
| VIO-OPS-01 | MEDIUM | import_time_attendance and sync_org_structure are unimplemented stubs |

**Total violations: 24** (see architecture-violation-register.json for complete list)

---

## 7. External Interfaces

| ID | Direction | Target | Mechanism | Status |
|----|-----------|--------|-----------|--------|
| SYS-01 | Outbound | Oracle Financials | UTL_FILE pipe-delimited flat file | Active |
| SYS-02 | Outbound | ADP Benefits | UTL_FILE fixed-width (legacy format) | Active |
| SYS-03 | Inbound | Time & Attendance | UTL_FILE CSV | Stub — not implemented |
| SYS-04 | Outbound | LDAP / Active Directory | Unknown | Stub — not implemented |
| SYS-05 | Outbound | SMTP Relay (port 25) | UTL_SMTP, new connection per email | Active; no TLS |
| SYS-06 | Outbound | Filesystem (pay register) | UTL_FILE CSV | Active |

---

## 8. Scheduled Jobs

| Job | Procedure | Schedule | DDL in Source |
|-----|-----------|----------|---------------|
| HRMS_NOTIFICATION_JOB | PKG_NOTIFICATION.process_queue | Every 5 minutes | ❌ Not found |
| HRMS_LEAVE_ACCRUAL_JOB | PKG_LEAVE.run_monthly_accrual | 1st of each month | ❌ Not found |

---

## 9. Key Call Flows Traced

1. **User Login** — HRMS_LOGIN → PKG_SECURITY.authenticate → :GLOBAL session setup → HRMS_MENU
2. **Hire Employee** — HRMS_EMPLOYEE → PKG_EMPLOYEE.create_employee → DB trigger → PKG_PAYROLL.create_salary_record (CYCLE-01)
3. **Terminate Employee** — PKG_EMPLOYEE.terminate_employee → PKG_LEAVE (cancel), PKG_PAYROLL (end salary) → PKG_NOTIFICATION (notify manager)
4. **Payroll Run** — HRMS_PAYROLL → PKG_PAYROLL.calculate_payroll (row-by-row, partial commits) → PKG_PAYROLL.approve_payroll → PKG_INTEGRATION.generate_gl_journal (UTL_FILE)
5. **Submit Leave** — HRMS_LEAVE → PKG_LEAVE.submit_leave_request (validate, overlap check, balance check) → NOTIFICATION_QUEUE
6. **Performance Review** — PKG_PERFORMANCE.generate_reviews_for_cycle → create_review per employee → self-assessment → manager review → acknowledge
7. **Notification Dispatch** — DBMS_SCHEDULER → PKG_NOTIFICATION.process_queue → UTL_SMTP (new connection per email)

---

## 10. Strangler Candidate Ranking

| Rank | Module | Readiness | Blockers |
|------|--------|-----------|---------|
| 1 | MOD-04 Performance | HIGH ★★★★★ | None |
| 2 | MOD-03 Leave | HIGH ★★★★☆ | 2 bugs; scheduler DDL missing |
| 3 | MOD-06 Notification/Audit | HIGH ★★★★☆ | None (infrastructure replacement) |
| 4 | MOD-05 Security | MEDIUM ★★★☆☆ | Auth stub; key rotation required |
| 5 | MOD-01 Employee | MEDIUM ★★★☆☆ | SQL injection; circular dep; COBRA TODO |
| 6 | MOD-02 Payroll | LOW ★★☆☆☆ | Partial commits; hard-coded tax; circular dep; file integrations |

---

## 11. Mandatory Pre-Migration Tasks

1. Fix PKG_SECURITY.authenticate — implement actual password hash verification
2. Rotate AES-256 SSN encryption key and re-encrypt all stored SSNs
3. Fix SQL injection in PKG_EMPLOYEE.search_employees
4. Extract DBMS_SCHEDULER job DDL into source control (DBA action)
5. Locate USER_CREDENTIALS table DDL
6. Implement COBRA notification and access revocation in terminate_employee
7. Fix VW_LEAVE_SUMMARY AVAILABLE formula (subtract PENDING_DAYS)
8. Fix expire_carryover idempotency bug

---

## 12. Open Questions (Summary)

**Infrastructure:** Oracle DB exact version, Forms deployment model, directory object filesystem paths, DR/standby topology, user count  
**Business rules:** Correct hire date future limit (90 vs 180 days), leave AVAILABLE formula intent, RBAC granularity beyond grade thresholds, fiscal year applicability  
**Source gaps:** HRMS_REPORTS.fmb, HRMS_ADMIN.fmb, USER_CREDENTIALS DDL, scheduler job DDL, TAX_BRACKETS table data  
**Integrations:** Oracle Financials API availability, ADP API availability, time & attendance vendor identity  

See open-questions.md for the full list (41 questions across 5 categories).

---

## 13. Architecture Quality Assessment

| Dimension | Score | Key Issue |
|-----------|-------|-----------|
| Security | 2/10 | Hard-coded key, broken auth, SQL injection, MD5 |
| Data Integrity | 5/10 | Partial commits, race conditions, view formula bug |
| Modularity | 4/10 | Circular dependency; shared tables; no API boundary |
| Testability | 2/10 | No test harness found; circular deps; Forms unautomatable |
| Deployability | 3/10 | Single schema; no CI/CD evidence |
| Maintainability | 4/10 | Clear package structure; TODO stubs; hard-coded values |
| Scalability | 2/10 | Oracle Forms non-scalable; single DB; no caching |
| Observability | 5/10 | AUDIT_LOG thorough; no metrics/tracing |

---

## 14. Output Files Generated

| File | Description |
|------|-------------|
| system-inventory.json | Full system and component inventory |
| module-boundary-map.json | 6 modules with coupling scores and dependency edges |
| component-registry.json | All 22 packages, 8 forms, 2 libraries, triggers, views, scheduler jobs |
| application-interface-catalogue.json | 8 user interfaces + 6 system interfaces + 2 scheduled jobs |
| dependency-graph.json | Nodes, edges, cycles, high-coupling components |
| call-flow-map.json | 10 traced call flows with step-by-step breakdown |
| architecture-pattern-report.md | Layered Monolith + Big Ball of Mud analysis |
| architecture-violation-register.json | 24 violations (9 security, 8 architecture, 5 data, 2 operations) |
| application-risk-register.json | 13 migration risks with severity, likelihood, and migration impact |
| strangler-candidate-report.md | Module migration ranking with recommended sequence |
| forward-engineering-input-map.md | Target service map and pre-migration task list |
| open-questions.md | 41 open questions for human review |
| extraction-audit.md | Coverage, confidence, non-hallucination compliance |
| diagrams/system-context.mmd | C4 Level 1 — system in environment |
| diagrams/container-view.mmd | C4 Level 2 — Forms client vs DB container |
| diagrams/component-view.mmd | C4 Level 3 — all packages, forms, integrations |
| diagrams/dependency-view.mmd | Package dependency graph with cycle annotation |
| diagrams/call-flow-view.mmd | Sequence diagram: login, hire, payroll, leave, notification |
| application-architecture-summary.md | This file |

---

## 15. Extraction Confidence

**Overall confidence: HIGH (0.91 average across all artifacts)**

All violations, call flows, and architectural findings are directly evidenced from source code or authoritative Layer 1 JSON. No behaviors, ownership, or business rules were invented. Items that could not be determined from code are logged in open-questions.md and marked as `"unknown"` in JSON artifacts.

Two forms (HRMS_REPORTS, HRMS_ADMIN) were not scanned — their features are marked at 0.5-0.7 confidence.  
DBMS_SCHEDULER DDL was not found in source — scheduler jobs are marked at 0.7-0.8 confidence from code comments.
