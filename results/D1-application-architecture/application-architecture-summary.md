# Application Architecture Summary — Oracle HRMS v4.2
**System:** Oracle HRMS v4.2 (Build 2024.03.15)
**Extractor:** AA Agent 1 — Application Architecture Extractor
**Date:** 2026-08-04
**Extraction Confidence:** 0.88

---

## 1. What This System Is

Oracle HRMS v4.2 is a monolithic Human Resources Management System built entirely on the Oracle stack. It manages the full employee lifecycle — from hire to termination — including payroll calculation, leave management, performance reviews, and flat-file integrations with external systems (GL, ADP Benefits, Time & Attendance).

**Technology summary:**
- **Presentation:** Oracle Forms 12c (12.2.1.4) — 6 forms, 2 PL/SQL libraries, 1 menu module
- **Business logic:** 11 Oracle PL/SQL stored packages in schema `HRMS`
- **Data:** Oracle RDBMS (version unknown), schema `HRMS`, 22 tables, 6 views, 6 triggers, 30 sequences
- **Integration:** UTL_FILE flat-file export (GL, ADP, Payroll register), UTL_SMTP email notifications
- **Security:** Grade-based authorization; AES-256-CBC SSN encryption; MD5 password hashing

All tiers share a single Oracle Database schema. There is no REST/SOAP API layer, no microservices, no message bus, and no separate caching layer.

---

## 2. Architecture in One Picture

```
┌─────────────────────────────────────────────────────────────────┐
│  Oracle Forms 12c Runtime                                        │
│  HRMS_LOGIN → HRMS_MENU (MDI) → HRMS_EMPLOYEE                   │
│                               → HRMS_PAYROLL                    │
│                               → HRMS_LEAVE                      │
│                               → HRMS_PERFORMANCE                │
│                               → HRMS_ADMIN    [source missing]  │
│                               → HRMS_REPORTS  [source missing]  │
│  Libraries: HRMS_COMMON_LIB.pll, HRMS_VALIDATION_LIB.pll        │
└────────────────────┬────────────────────────────────────────────┘
                     │ Oracle Net (SQL*Net) — direct DB connection
┌────────────────────▼────────────────────────────────────────────┐
│  Oracle Database — Schema HRMS                                   │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │PKG_SECURI│  │PKG_EMPLOY│◄─►│PKG_PAYROL│  │PKG_LEAVE     │   │
│  │TY        │  │EE        │  │L         │  │              │   │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│                     │             │                │            │
│  ┌──────────┐  ┌────▼─────┐  ┌───▼──────┐  ┌─────▼────────┐  │
│  │PKG_PERFOR│  │PKG_NOTIFI│  │PKG_INTEGR│  │PKG_REPORTING │  │
│  │MANCE     │  │CATION    │  │ATION     │  │              │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │PKG_AUDIT │  │PKG_COMMON│  │PKG_VALIDA│  (cross-cutting)     │
│  └──────────┘  └──────────┘  │TION      │                      │
│                               └──────────┘                      │
│  Tables (22) │ Views (6) │ Sequences (30) │ Triggers (6)        │
└──────────────────────────────────────┬──────────────────────────┘
                                       │ UTL_FILE / UTL_SMTP
              ┌────────────────────────┼────────────────────────┐
              ▼                        ▼                         ▼
        GL System               ADP Benefits             SMTP Server
     (flat-file feed)          (fixed-width export)   (port 25, plaintext)
```
`◄►` = circular dependency (migration blocker)

---

## 3. Modules and Their Responsibilities

| Module | Package(s) | Form(s) | Key Responsibility |
|---|---|---|---|
| Employee Management | PKG_EMPLOYEE | HRMS_EMPLOYEE | Hire, transfer, terminate, search, org chart |
| Payroll | PKG_PAYROLL | HRMS_PAYROLL | Payroll run lifecycle, tax calculation, pay register |
| Leave Management | PKG_LEAVE | HRMS_LEAVE | Leave requests, approvals, balances, accrual batch |
| Performance Management | PKG_PERFORMANCE | HRMS_PERFORMANCE | Review cycles, goals, ratings |
| Security & Sessions | PKG_SECURITY | HRMS_LOGIN | Auth, session tokens, SSN encryption, permissions |
| Notifications | PKG_NOTIFICATION | — | Async email queue, SMTP dispatch, retry |
| Integration | PKG_INTEGRATION | — | GL feed, ADP benefits export, T&A import (TODO) |
| Reporting | PKG_REPORTING | HRMS_REPORTS? | 8 management reports via REF CURSOR |
| Audit & Compliance | PKG_AUDIT | — | Audit trail, AUDIT_LOG writes, purge |
| Common Utilities | PKG_COMMON, PKG_VALIDATION | — | Logging, config, date math, formatters, validators |
| Administration | unknown | HRMS_ADMIN? | Source not provided |

---

## 4. Critical Findings

### Security (CRITICAL — must fix before any migration)

| ID | Finding |
|---|---|
| AV-004 | Authentication not implemented — any password accepted |
| AV-002 | SSN encryption key hard-coded in source ('HR$ystem_3ncrypt10n_K3y_2024!!') |
| AV-003 | MD5 used for password hashing — cryptographically broken |
| AV-001 | SQL injection in PKG_EMPLOYEE.search_employees via string concatenation |
| AV-005 | FTP credentials stored cleartext in SYSTEM_PARAMETERS |

### Architecture (HIGH — migration blockers)

| ID | Finding |
|---|---|
| AV-010 | PKG_EMPLOYEE ↔ PKG_PAYROLL circular dependency |
| RISK-012 | DBMS_SCHEDULER job definitions not in source — must be captured from production |

### Data Integrity (HIGH)

| ID | Finding |
|---|---|
| AV-009 | PAYROLL_DETAILS.YTD_AMOUNT always 0 — YTD accumulation not implemented |
| AV-011 | Partial commits in payroll batch — run failure leaves inconsistent state |

### Unimplemented Features

| ID | Finding |
|---|---|
| AV-006 | Time & Attendance CSV import — TODO, never implemented |
| AV-007 | PKG_INTEGRATION.sync_org_structure — placeholder only |
| AV-008 | PKG_SECURITY.change_password — does not update credentials |

---

## 5. Integration Surface

| Integration | Direction | Format | Status |
|---|---|---|---|
| GL Journal Feed | Outbound | Pipe-delimited flat file | Implemented |
| ADP Benefits Feed | Outbound | Fixed-width 203-char | Implemented |
| Payroll Register | Outbound | CSV | Implemented |
| Time & Attendance | Inbound | CSV | NOT IMPLEMENTED |
| Email Notifications | Outbound | SMTP port 25 | Implemented |

---

## 6. Migration Readiness Score

| Dimension | Score | Notes |
|---|---|---|
| Security posture | 1/5 | Auth non-functional; key exposed; SQL injection present |
| Modularity | 2/5 | Circular dep; coarse permissions; shared schema |
| Data integrity | 3/5 | Good trigger coverage; YTD bug and partial commits are risks |
| Feature completeness | 3/5 | Most features implemented; T&A, admin, reporting gaps |
| Testability | 1/5 | No test harness; partial commits untestable without prod data |
| Documentation (code) | 3/5 | Packages have reasonable inline comments; known bugs documented |
| Integration readiness | 2/5 | Flat-file only; no API surface |

**Overall migration readiness: 2.1/5 — requires significant remediation before safe extraction**

---

## 7. Recommended Next Steps

1. **Security remediation sprint** — fix AV-001 through AV-005 before any internet-facing deployment
2. **Production audit** — query DBA_SCHEDULER_JOBS and capture all job definitions
3. **Break circular dependency** — introduce PKG_CORE_DATA or similar to decouple PKG_EMPLOYEE and PKG_PAYROLL
4. **Data quality check** — scan EMPLOYEES for duplicate EMP_NUMBERs; scan PAYROLL_RUNS for partially-calculated states
5. **Begin strangler extraction** — start with Notifications and Audit (lowest coupling, highest isolation)

---

## 8. Output Files Produced

| File | Description |
|---|---|
| system-inventory.json | Full system and external dependency inventory |
| module-boundary-map.json | 10 modules with coupling scores and boundary quality |
| component-registry.json | All 38 components classified by type and layer |
| application-interface-catalogue.json | All form entry points and batch jobs |
| dependency-graph.json | Package-to-package dependency graph |
| call-flow-map.json | 6 key end-to-end flows with step-by-step breakdown |
| architecture-pattern-report.md | Pattern identification and anti-pattern inventory |
| architecture-violation-register.json | 23 violations with severity and remediation |
| application-risk-register.json | 12 risks with likelihood, impact, and migration impact |
| strangler-candidate-report.md | Module ranking and migration sequence |
| forward-engineering-input-map.md | Modernization guidance per module |
| open-questions.md | 30+ questions requiring human/production input |
| extraction-audit.md | Confidence scores, coverage matrix, hallucination controls |
| diagrams/system-context.mmd | C4 System Context diagram |
| diagrams/container-view.mmd | C4 Container diagram |
| diagrams/component-view.mmd | C4 Component diagram |
| diagrams/dependency-view.mmd | Full dependency graph with circular dep highlighted |
| diagrams/call-flow-view.mmd | Sequence diagram for key flows |
| AA_App_Extractor.md | Agent execution log and methodology |
