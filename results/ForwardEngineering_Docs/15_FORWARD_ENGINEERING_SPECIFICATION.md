# 15 — Forward Engineering Specification
**System:** Acme Corporation HRMS — Replacement Platform
**Version:** 1.0
**Date:** 2026-08-05
**Status:** APPROVED FOR IMPLEMENTATION
**Owner:** Platform Engineering / HR Systems Programme

---

## Table of Contents

1. [Executive Overview](#1-executive-overview)
2. [Forward Engineering Strategy — Strangler Fig Pattern](#2-forward-engineering-strategy)
3. [Migration Phases Overview](#3-migration-phases-overview)
4. [Phase 1 — Foundation (Months 1–3)](#4-phase-1--foundation-months-13)
5. [Phase 2 — Core HR (Months 4–6)](#5-phase-2--core-hr-months-46)
6. [Phase 3 — Payroll Engine (Months 7–10)](#6-phase-3--payroll-engine-months-710)
7. [Phase 4 — Integration, Reporting, and Cutover (Months 11–12)](#7-phase-4--integration-reporting-and-cutover-months-1112)
8. [Critical Defect Remediation Plan](#8-critical-defect-remediation-plan)
9. [Data Migration Strategy](#9-data-migration-strategy)
10. [Cutover Plan](#10-cutover-plan)
11. [Rollback Strategy](#11-rollback-strategy)
12. [Team Structure and Sprint Plan](#12-team-structure-and-sprint-plan)
13. [Non-Functional Requirements](#13-non-functional-requirements)
14. [Appendix A — Technology Stack Decision Record](#14-appendix-a--technology-stack-decision-record)

---

## 1. Executive Overview

This document is the master technical specification for replacing the Acme Corporation Oracle HRMS (v4.2.0) with a modern, cloud-native HR platform. The reverse-engineering programme has completed a full four-track analysis (Business Analysis, Data Analysis, Technology Analysis, Application Quality Review) and produced 140 documented business rules, 46+ hidden business rules, 80+ technical debt items, and 32 data quality issues across 30+ confirmed tables.

### 1.1 Why We Are Replacing — Not Patching

The analysis uncovered systemic failures that cannot be corrected incrementally:

| Category | Count | Worst Findings |
|---|---|---|
| Critical Security Vulnerabilities | 6 | MD5 passwords; auth stub (anyone logs in); hardcoded AES key |
| Compliance Gaps | 4 | COBRA not implemented; FMLA documentation disabled; ACH prenote absent; HOH tax = $0 |
| Unimplemented Core Features | 5 | Direct deposit (table exists, never called); org sync placeholder; calculate_final_pay missing; calibration workflow absent; time-attendance import no-op |
| Architecture Anti-Patterns | 9 | No CI/CD; monolithic PL/SQL; Oracle Forms 12c lock-in; OLTP-direct reporting |
| Broken PL/SQL Procedures | 4 | rehire_employee (ORA-00904); HOH tax branch; generate_emp_number race condition; accrual increment overwrite |

The Oracle Forms platform requires specialist tooling unavailable to most developers (Forms Builder 12c), has no automated test suite, no CI/CD pipeline, and no secret scanning — conditions that have already led to a hardcoded production encryption key embedded in source code.

### 1.2 Scope of Replacement

The new system replaces all 10 bounded contexts identified in the domain model analysis:

- BC-01 Employee Identity
- BC-02 Compensation
- BC-03 Leave Management
- BC-04 Performance
- BC-05 Benefits
- BC-06 Security and Access
- BC-07 Organisational Structure
- BC-08 Notifications
- BC-09 Integration and Export
- BC-10 Reporting

---

## 2. Forward Engineering Strategy

### 2.1 Strangler Fig Pattern — Rationale

The Strangler Fig pattern is mandated for this migration. The Oracle HRMS processes live payroll for all Acme employees. A hard-cutover "big bang" migration is impermissible because:

1. Payroll is a zero-defect domain — a single missed pay run is a legal and reputational event.
2. The legacy system contains 14+ unimplemented features that must be built from scratch in the new system before they can be migrated.
3. The absence of any test suite in the legacy system means no automated regression baseline exists.
4. The hardcoded AES encryption key (value: `HR$ystem_3ncrypt10n_K3y_2024!!`) means all encrypted columns must be re-encrypted with a new key during migration; this requires a carefully staged decryption-then-re-encryption window.

### 2.2 Strangler Fig Implementation Model

```
┌──────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY / ROUTER                          │
│         (routes by feature flag: LEGACY | NEW_SYSTEM)                │
└───────────────────┬──────────────────────────────┬───────────────────┘
                    │                              │
         ┌──────────▼───────────┐      ┌──────────▼───────────┐
         │  Oracle HRMS         │      │  New HRMS Platform    │
         │  (Oracle 19c +       │      │  (Phase N features)   │
         │   Oracle Forms 12c)  │      │                       │
         │  [LEGACY — reads     │      │  [ACTIVE — writes     │
         │   and writes until   │◄────►│   propagate back to   │
         │   feature retired]   │ sync │   Oracle via CDC]     │
         └──────────────────────┘      └───────────────────────┘
```

**Routing logic:** A feature-flag service (LaunchDarkly or equivalent) controls per-bounded-context routing. New system writes are dual-written to Oracle via a Change Data Capture (CDC) bridge during the overlap window, ensuring the legacy system retains a complete view for reporting and audit until full cutover.

### 2.3 CDC Bridge Specification

| Direction | Mechanism | Latency Target | Tables in Scope |
|---|---|---|---|
| Legacy → New | Oracle GoldenGate (or Debezium + Kafka) | < 5 seconds | All 30 confirmed tables |
| New → Legacy | Application-level dual-write service | Synchronous | EMPLOYEES, LEAVE_BALANCES, PAYROLL_RUNS |

The CDC bridge is decommissioned at the end of Phase 4 cutover.

### 2.4 Guiding Principles

1. **Fix defects in the new system only.** No patches to Oracle PL/SQL — remediation work happens once, in the forward-engineered codebase.
2. **Feature parity before feature extension.** Every one of the 140 BA business rules must pass an acceptance test before a bounded context is marked MIGRATED.
3. **Encryption key rotation at migration time.** All AES-256-CBC-encrypted columns are decrypted using the legacy key and re-encrypted with a new key generated from a secrets manager (AWS Secrets Manager / HashiCorp Vault) before writing to the new database.
4. **No Oracle Forms dependency in the new system.** All Oracle Forms `.fmb`/`.fmx` screens are replaced with React components.
5. **Observability from day one.** Every service ships with structured JSON logging, distributed tracing (OpenTelemetry), and a health endpoint before it processes production traffic.

---

## 3. Migration Phases Overview

| Phase | Months | Theme | Bounded Contexts | Go/No-Go Gate |
|---|---|---|---|---|
| 1 | 1–3 | Foundation | Auth (BC-06), Employee Identity (BC-01), Org Structure (BC-07) | Payroll not impacted; gate = all 140 BR passing for in-scope contexts |
| 2 | 4–6 | Core HR | Leave (BC-03), Performance (BC-04), Notifications (BC-08) | No payroll dependency; gate = leave balance reconciliation matches Oracle |
| 3 | 7–10 | Payroll Engine | Compensation (BC-02), Payroll, Tax, Direct Deposit | Gate = two parallel payroll runs agree to the cent |
| 4 | 11–12 | Integration, Reporting, Cutover | Integration (BC-09), Reporting (BC-10), Benefits (BC-05) | Gate = full UAT sign-off from HR, Finance, and Legal |

---

## 4. Phase 1 — Foundation (Months 1–3)

### 4.1 Bounded Contexts in Scope

| Bounded Context | Legacy Owner | New System Module |
|---|---|---|
| Security and Access (BC-06) | PKG_SECURITY, USER_CREDENTIALS | `auth-service` |
| Employee Identity (BC-01) | PKG_EMPLOYEE, EMPLOYEES | `employee-service` |
| Organisational Structure (BC-07) | PKG_EMPLOYEE (shared), DEPARTMENTS | `org-service` |

### 4.2 Critical Defects Fixed in Phase 1

#### DEF-001 — Hardcoded AES Encryption Key (CRITICAL)

**Legacy code:** `PKG_SECURITY.pkb` — raw key literal `HR$ystem_3ncrypt10n_K3y_2024!!` is embedded directly in PL/SQL package body and in Oracle Forms `.fmb` source.

**Impact:** Any developer with repository read access has the decryption key for all SSNs, bank account numbers, and dependent SSNs in production.

**New system fix:**
```
1. Key stored in AWS Secrets Manager (or HashiCorp Vault) under path:
   /hrms/prod/encryption/primary-key
2. auth-service retrieves key at startup via IAM role; key never touches application source code.
3. Rotation schedule: every 90 days via automated Vault rotation.
4. Migration window: legacy key used to DECRYPT all existing cipher values;
   new key used to RE-ENCRYPT before writing to new DB.
   This operation runs in Phase 1 data migration sprint.
```

#### DEF-002 — MD5 Password Hashing / Authentication Stub (CRITICAL)

**Legacy code:** `PKG_SECURITY.authenticate()` never checks `USER_CREDENTIALS` — any valid username authenticates regardless of password (BR-042). `change_password` uses `DBMS_CRYPTO.HASH_MD5`.

**New system fix:**
```
1. bcrypt (cost factor 12) for password storage.
2. Auth service uses email + bcrypt comparison; no username enumeration timing gap.
3. Rate limiting: 5 failed attempts → 15-minute lockout (stored in Redis).
4. Old password verification required on change_password endpoint (fixes DQ-029).
5. JWT with 1-hour expiry replaces Oracle USER_SESSIONS table.
```

#### DEF-003 — `rehire_employee` ORA-00904 Column Mismatch (HIGH)

**Legacy code:** `PKG_EMPLOYEE.rehire_employee` references a column in `EMPLOYEE_HISTORY` that does not exist in the DDL — the procedure fails with `ORA-00904: invalid identifier` on every execution.

**New system fix:**
```
1. New employee-service implements rehire as a first-class state transition:
   TERMINATED → ACTIVE with a new HIRE_DATE row in employment_history table.
2. Acceptance test: rehire an employee, verify employment_history shows both
   original termination and new hire date, verify leave balances re-initialize.
```

#### DEF-004 — Race Condition in `generate_emp_number` (HIGH)

**Legacy code:** `generate_emp_number` uses a SELECT MAX(EMPLOYEE_NUMBER) + 1 pattern without a sequence or lock. Concurrent inserts can generate duplicate `EMP_NUMBER` values.

**New system fix:**
```
1. EMPLOYEE_NUMBER generated by a database sequence (PostgreSQL SEQUENCE or
   equivalent) — atomic, no race condition possible.
2. Format preserved: EMP-{zero-padded 5 digits}.
3. Sequence starts at MAX(legacy EMPLOYEE_NUMBER) + 1 during migration seeding.
```

### 4.3 Technical Implementation Details

#### 4.3.1 `auth-service`

**Language/Framework:** Node.js 22 LTS / Fastify  
**Database:** PostgreSQL 16 (users, sessions, credentials tables)  
**Cache:** Redis 7 (session tokens, rate-limit counters)

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Email + password → JWT access + refresh token |
| POST | `/auth/logout` | Invalidate refresh token |
| POST | `/auth/refresh` | Exchange refresh token for new access token |
| POST | `/auth/change-password` | Requires current password + new password; bcrypt |
| GET | `/auth/me` | Returns employee profile from JWT claims |

**RBAC Model (replaces grade-based PKG_SECURITY.has_permission):**

| Legacy Grade | New Role | Permissions |
|---|---|---|
| Grade ≥ 8 | `HR_ADMIN` | Full read/write on all resources |
| Grade 5–7 | `HR_MANAGER` | Read all; write own department |
| Grade 1–4 | `EMPLOYEE` | Read/write own record only |

**Acceptance Tests (Phase 1 Auth Gate):**

- [ ] Login with correct credentials returns 200 + JWT
- [ ] Login with wrong password returns 401 (not 200)
- [ ] Locked account returns 429 after 5 failed attempts
- [ ] Change password without current password returns 403
- [ ] Session expires after 1 hour; refresh token valid for 7 days
- [ ] Terminated employee cannot authenticate (EMPLOYMENT_STATUS check)

#### 4.3.2 `employee-service`

**Language/Framework:** Java 21 / Spring Boot 3.3  
**Database:** PostgreSQL 16 (employees, departments, job_positions, employment_history)  
**Events:** Kafka topics: `employee.created`, `employee.terminated`, `employee.transferred`

**API Endpoints:**

| Method | Path | Description |
|---|---|---|
| POST | `/employees` | Create employee (fixes DEF-004 EMP_NUMBER race) |
| GET | `/employees/{id}` | Get employee by ID |
| PUT | `/employees/{id}` | Update employee details |
| POST | `/employees/{id}/terminate` | Terminate with reason code |
| POST | `/employees/{id}/rehire` | Rehire terminated employee (fixes DEF-003) |
| POST | `/employees/{id}/transfer` | Department/position transfer |
| GET | `/departments` | List all departments |
| POST | `/departments` | Create department |
| GET | `/departments/{id}/hierarchy` | CONNECT BY equivalent using recursive CTE |

**Key Implementation Notes:**

1. `terminate_employee` publishes `employee.terminated` event — consumed by `leave-service` (close balances), `notification-service` (send termination notification), and future `benefits-service` (COBRA trigger placeholder).
2. `employee.terminated` event includes `final_pay_required: true` flag — consumed by `payroll-service` in Phase 3.
3. Dependent records (`EMPLOYEE_DEPENDENTS`) inactivated by event handler in same transaction — fixes PP-TERM (BR-DEP-09 gap).
4. Org hierarchy uses recursive CTE (PostgreSQL `WITH RECURSIVE`) — replaces Oracle `CONNECT BY`; no 500-employee degradation.

#### 4.3.3 `org-service`

**Scope:** Departments, positions, reporting lines. Replaces the stub `PKG_INTEGRATION.sync_org_structure` with a real SCIM 2.0 integration to the corporate Active Directory/LDAP.

**SCIM 2.0 Endpoints (inbound from Active Directory):**

| Method | Path | Description |
|---|---|---|
| GET | `/scim/v2/Groups` | List departments |
| POST | `/scim/v2/Groups` | Create department from AD OU |
| PUT | `/scim/v2/Groups/{id}` | Update department / reporting line |

**Fixes for BR-ORG-01–05:** The sync procedure now performs a real delta-sync using SCIM `filter=lastModified gt {timestamp}`. A file-level audit log replaces the false-positive `'Org structure sync completed'` log entry.

### 4.4 Phase 1 Acceptance Criteria

| ID | Criterion | Verification Method |
|---|---|---|
| P1-AC-01 | All 140 BA business rules in scope (BC-01, BC-06, BC-07) pass automated tests | JUnit/Jest test suite; CI pipeline gate |
| P1-AC-02 | Zero employees can authenticate with wrong password | Penetration test + automated test |
| P1-AC-03 | `rehire_employee` succeeds and produces correct `employment_history` rows | Integration test |
| P1-AC-04 | `EMPLOYEE_NUMBER` is unique under 1000 concurrent inserts | Load test (k6 or JMeter) |
| P1-AC-05 | All SSN and bank account values re-encrypted with new key; legacy key decommissioned | DBA validation query on ciphertext prefix |
| P1-AC-06 | Org hierarchy renders correctly for 500+ employee dataset | UAT with HR team |
| P1-AC-07 | Auth service passes OWASP Top 10 automated scan (OWASP ZAP) | CI security gate |
| P1-AC-08 | CDC bridge replicating EMPLOYEES changes from Oracle to new DB with < 5s lag | Monitoring dashboard metric |

---

## 5. Phase 2 — Core HR (Months 4–6)

### 5.1 Bounded Contexts in Scope

| Bounded Context | Legacy Owner | New System Module |
|---|---|---|
| Leave Management (BC-03) | PKG_LEAVE, LEAVE_BALANCES, LEAVE_REQUESTS | `leave-service` |
| Performance Management (BC-04) | PKG_PERFORMANCE, PERFORMANCE_REVIEWS | `performance-service` |
| Notifications (BC-08) | PKG_NOTIFICATION, NOTIFICATION_QUEUE | `notification-service` |

### 5.2 Critical Defects Fixed in Phase 2

#### DEF-005 — Leave Accrual Increment Overwrite (HIGH)

**Legacy code:** `PKG_LEAVE.run_monthly_accrual` retry block uses `SET ACCRUED = v_accrued` (assignment) instead of `SET ACCRUED = ACCRUED + v_accrued` (increment). If a race condition causes the insert to miss (SQL%ROWCOUNT = 0 fires on an existing row), the entire accrual balance is silently reset to the single-month amount.

**New system fix:**
```sql
-- PostgreSQL: atomic upsert — no overwrite risk
INSERT INTO leave_balances (employee_id, leave_type_id, accrued, calendar_year)
VALUES ($1, $2, $3, $4)
ON CONFLICT (employee_id, leave_type_id, calendar_year)
DO UPDATE SET accrued = leave_balances.accrued + EXCLUDED.accrued,
              modified_date = NOW();
```

#### DEF-006 — Performance Calibration Workflow Missing (MEDIUM)

**Legacy system:** `CALIBRATED_RATING` and `CALIBRATION_NOTES` columns exist in `PERFORMANCE_REVIEWS` DDL but no procedure writes to them. `get_rating_distribution` reads `OVERALL_RATING` (pre-calibration). The status lifecycle skips the CALIBRATION state entirely.

**New system fix:**
- Full calibration workflow implemented as a distinct review phase between `COMPLETED` and `ACKNOWLEDGED`.
- New status values: `NOT_STARTED → SELF_REVIEW → MANAGER_REVIEW → COMPLETED → IN_CALIBRATION → CALIBRATED → ACKNOWLEDGED`
- Calibration endpoints require `HR_ADMIN` role; `calibrated_rating` + `calibration_notes` are required fields.
- `get_rating_distribution` queries `COALESCE(calibrated_rating, overall_rating)` so uncalibrated reviews fall back to manager rating.

#### DEF-007 — FMLA Requires-Document Flag Disabled (MEDIUM)

**Legacy config:** `01_reference_data.sql` seeds `LEAVE_TYPES` with `REQUIRES_DOCUMENT='N'` for FMLA. Any employee can submit an FMLA request with no supporting documentation.

**New system fix:**
```
1. FMLA leave type seeded with requires_document = true.
2. leave-service validates: if leave_type.requires_document = true AND
   supporting_doc_url IS NULL → reject with HTTP 422.
3. supporting_doc_url stored as S3 pre-signed URL reference (not file path —
   fixes TD-47 path traversal risk).
```

### 5.3 Technical Implementation Details

#### 5.3.1 `leave-service`

**Language/Framework:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16 (leave_balances, leave_requests, leave_types)  
**Events consumed:** `employee.created` (initialize balances), `employee.terminated` (close balances)

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| POST | `/leave/requests` | Submit leave request |
| GET | `/leave/requests/{id}` | Get request status |
| PUT | `/leave/requests/{id}/approve` | Manager approval |
| PUT | `/leave/requests/{id}/reject` | Manager rejection |
| GET | `/leave/balances/{employee_id}` | Current balances |
| POST | `/leave/balances/accrue` | Monthly accrual (scheduled job) |
| POST | `/leave/balances/initialize` | Initialize on hire (event-driven) |

**Accrual Scheduler:** AWS EventBridge Scheduler cron `0 1 1 * *` (1 AM on 1st of month). Replaces the `DBMS_SCHEDULER` job in the legacy system. A dedicated `accrual_runs` audit table records each run with start time, end time, rows processed, and any errors — replaces the false-success `log_info` pattern.

#### 5.3.2 `performance-service`

**Language/Framework:** Java 21 / Spring Boot 3.3  
**Database:** PostgreSQL 16 (performance_reviews, review_cycles, performance_goals)

**Status Machine (replaces ad-hoc PKG_PERFORMANCE transitions):**

```
NOT_STARTED
    └──[create_review]──► SELF_REVIEW
                               └──[submit_self_assessment]──► MANAGER_REVIEW
                                                                    └──[submit_manager_review]──► COMPLETED
                                                                                                      └──[open_calibration]──► IN_CALIBRATION
                                                                                                                                    └──[submit_calibration]──► CALIBRATED
                                                                                                                                                                    └──[acknowledge]──► ACKNOWLEDGED
```

Each transition is guarded by role: `EMPLOYEE` can submit self-assessment; `HR_MANAGER` submits manager review; `HR_ADMIN` opens and submits calibration.

#### 5.3.3 `notification-service`

**Language/Framework:** Node.js 22 / Fastify  
**Transport:** AWS SES (email), AWS SNS (SMS — replaces the unimplemented SMS handler)  
**Queue:** Redis Streams (replaces `NOTIFICATION_QUEUE` table polling)

**Key improvements over legacy:**
- Template variables resolved at send time via Handlebars — no inline string concatenation.
- Retry with exponential backoff (max 3 attempts) — replaces the PKG_NOTIFICATION single-attempt pattern.
- Dead-letter queue for failed notifications with alerting.
- Email verified via SES; SMS implemented (the `PHONE` channel is no longer a stub).

### 5.4 Phase 2 Acceptance Criteria

| ID | Criterion | Verification Method |
|---|---|---|
| P2-AC-01 | Leave balances for all employees in new system match Oracle to within rounding after migration | Automated reconciliation query |
| P2-AC-02 | FMLA leave request without document attachment returns 422 | Automated test |
| P2-AC-03 | Monthly accrual does not overwrite existing balance (concurrent run test) | Load test with 2 simultaneous accrual jobs |
| P2-AC-04 | Calibration workflow: `calibrated_rating` is required before status moves to CALIBRATED | Integration test |
| P2-AC-05 | `get_rating_distribution` returns calibrated ratings for calibrated reviews | API response validation |
| P2-AC-06 | Termination event triggers leave balance closure within 5 seconds | Event-driven integration test |
| P2-AC-07 | Notification retry fires 3 times on SES failure before DLQ | Chaos test (mock SES 500) |

---

## 6. Phase 3 — Payroll Engine (Months 7–10)

### 6.1 Bounded Contexts in Scope

| Bounded Context | Legacy Owner | New System Module |
|---|---|---|
| Compensation (BC-02) | PKG_PAYROLL, PKG_COMPENSATION | `payroll-service` |
| Tax Calculation | (embedded in PKG_PAYROLL) | `tax-service` |
| Direct Deposit / ACH | EMPLOYEE_BANK_ACCOUNTS (unused) | `disbursement-service` |

### 6.2 Critical Defects Fixed in Phase 3

#### DEF-008 — HOH Tax = $0 Bug (CRITICAL)

**Legacy code:** `PKG_PAYROLL.calculate_federal_tax` has a `WHEN 'HEAD_OF_HOUSEHOLD' THEN` branch that returns `0` federal tax — every employee filing as Head of Household pays zero federal income tax. This is a compliance violation affecting every affected employee's W-2.

**Root cause (from reverse engineering):** The `HEAD_OF_HOUSEHOLD` bracket lookup uses a separate `TAX_BRACKETS` query with `FILING_STATUS = 'HOH'`. No seed data exists for `HOH` brackets in `01_reference_data.sql`, causing the bracket cursor to return no rows and the fallback to silently return `0`.

**New system fix:**
```
1. tax-service uses IRS Publication 15-T bracket tables, seeded in the
   tax_brackets table with STATUS = 'HOH' for all applicable year/bracket rows.
2. If no bracket is found for a filing status → throw TaxConfigurationException
   (HTTP 500 with alert); never silently return 0.
3. Acceptance test: create employee with TAX_FILING_STATUS='HEAD_OF_HOUSEHOLD',
   run payroll, assert federal_tax > 0.
4. Retroactive correction analysis required (owned by HR/Finance, not engineering):
   identify all HOH employees in historical PAYROLL_DETAILS; produce correction
   report for payroll admin review.
```

#### DEF-009 — Direct Deposit Non-Functional (CRITICAL)

**Legacy system:** `EMPLOYEE_BANK_ACCOUNTS` table is fully designed for split-deposit (4 DEPOSIT_TYPEs, PRIORITY_ORDER, PRENOTE_SENT). Zero PL/SQL procedures reference this table. Every payroll run that marks status as `PAID` has never actually disbursed funds. This is the root cause of `DISC-009`.

**New system fix — `disbursement-service`:**
```
Phase 3A (Month 7–8): Build disbursement-service
  1. On payroll APPROVED event, disbursement-service queries employee_bank_accounts
     for all active accounts ordered by priority_order.
  2. Implements DEPOSIT_TYPE logic:
     FULL → entire net pay to this account
     PARTIAL_AMOUNT → fixed dollar amount
     PARTIAL_PERCENT → percentage of net pay
     REMAINDER → whatever remains after higher-priority accounts
  3. Validates: total of PARTIAL_AMOUNT + PARTIAL_PERCENT accounts ≤ net pay.
  4. Generates NACHA ACH file (IAT or CCD+ format per account type).
  5. Implements ACH prenote: on account creation, sends $0 prenote and sets
     PRENOTE_SENT='Y', PRENOTE_DATE=SYSDATE. Waits 3 banking days before
     live disbursement.

Phase 3B (Month 8–9): Integration and testing
  1. Bank connectivity via ACH file delivery to FTP endpoint (replaces
     the non-existent legacy ACH implementation).
  2. PAYROLL_RUNS table gains: GL_FEED_SENT_DATE, GL_FEED_FILE_NAME,
     ACH_FILE_NAME, ACH_SENT_DATE columns — fixes TD-80.
```

#### DEF-010 — `calculate_final_pay` Does Not Exist (CRITICAL)

**Legacy system:** `PKG_EMPLOYEE.terminate_employee` calls `PKG_PAYROLL.calculate_final_pay` in a TODO comment. The procedure was never created. Every termination requires completely manual off-system payroll calculation.

**New system fix:**
```
payroll-service implements final_pay_calculation endpoint:
  POST /payroll/final-pay
  Body: { employee_id, termination_date }

  Calculates:
    1. Prorated base salary for partial period
       (days_worked / days_in_period) * monthly_gross
    2. Accrued PTO payout at daily rate
    3. Any pending deductions already committed
    4. Final federal/state tax on combined amount
    5. Creates an off-cycle PAYROLL_RUN with status=FINAL_PAY

  Triggered automatically by employee.terminated event (employee-service → payroll-service).
  Payroll admin reviews and approves before disbursement.
```

#### DEF-011 — Routing Number Plaintext Storage (HIGH)

**Legacy system:** `EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER` stored as `VARCHAR2(20)` plaintext. Combined with the encrypted `ACCOUNT_NUMBER_ENC` and knowing the (previously hardcoded) key, this constitutes full ACH credentials in the clear.

**New system fix:**
```
1. Both account_number and routing_number encrypted using AES-256-GCM with key
   from Vault.
2. Decryption only within disbursement-service on approved PAYROLL_RUN.
3. Audit log entry created for every decryption event.
```

### 6.3 Technical Implementation Details

#### 6.3.1 `payroll-service`

**Language/Framework:** Java 21 / Spring Boot 3.3  
**Database:** PostgreSQL 16 (payroll_runs, payroll_details, deduction_records, salary_records)  
**Events produced:** `payroll.approved`, `payroll.completed`  
**Events consumed:** `employee.terminated` (trigger final pay)

**Payroll Run State Machine:**

```
DRAFT
  └──[calculate]──► CALCULATED
                        └──[approve]──► APPROVED
                                           └──[generate_gl]──► GL_GENERATED
                                                                    └──[disburse_ach]──► PAID
                                                                                            └──[close]──► COMPLETED
```

**Tax Service Integration:**

The `calculate_employee_pay` method calls `tax-service` via internal HTTP for each employee — tax configuration is no longer embedded in PL/SQL. This allows tax bracket updates (annual IRS publication updates) without application deployment.

```
tax-service calculates:
  federal_income_tax(gross, filing_status, ytd_wages, pay_periods_remaining)
  state_income_tax(gross, state_code, ytd_wages)
  fica_social_security(gross, ytd_fica_wages)  -- wage base ceiling
  fica_medicare(gross)
  additional_medicare(ytd_gross)               -- >$200k threshold
```

**Merit/Performance Link (replaces conformist PKG_PAYROLL → OVERALL_RATING read):**

payroll-service calls `performance-service GET /reviews/merit-eligible/{employee_id}` to check if `COALESCE(calibrated_rating, overall_rating) >= 3` before including merit increase in calculation. This is a synchronous anti-corruption layer call, not a shared database read.

#### 6.3.2 `tax-service`

**Language/Framework:** Python 3.12 / FastAPI  
**Database:** PostgreSQL 16 (tax_brackets, tax_rates — seeded from IRS Publication 15-T)  
**Key features:**
- Tax bracket data versioned by year; historical runs use year-appropriate brackets.
- HOH brackets fully seeded (fixes DEF-008).
- FICA wage base configurable via `system_config` table (not hardcoded).
- YTD earnings endpoint (`GET /tax/ytd/{employee_id}/{year}`) implements `PKG_PAYROLL.get_ytd_earnings` as a real API.

### 6.4 Phase 3 Acceptance Criteria

| ID | Criterion | Verification Method |
|---|---|---|
| P3-AC-01 | HOH employee federal tax > $0 for all gross pay values | Parameterised unit tests across all filing statuses and salary bands |
| P3-AC-02 | Parallel payroll run: new system results match Oracle PAYROLL_DETAILS to the cent for all non-HOH employees | Automated reconciliation (Python script) |
| P3-AC-03 | Parallel payroll run for HOH employees: new system result vs. manually-calculated IRS correct amount | Manual audit (Finance sign-off) |
| P3-AC-04 | ACH prenote sent on bank account creation; live disbursement blocked for 3 banking days | Integration test with mock ACH endpoint |
| P3-AC-05 | Split deposit correctly routes amounts across 3 accounts: PARTIAL_PERCENT + PARTIAL_AMOUNT + REMAINDER | Unit tests for all DEPOSIT_TYPE combinations |
| P3-AC-06 | `calculate_final_pay` produces correct prorated pay for termination on day 10 of 30-day period | Integration test |
| P3-AC-07 | PAYROLL_RUNS.ACH_FILE_NAME populated after disbursement | Database assertion test |
| P3-AC-08 | Two concurrent payroll approvals for same pay period rejected (idempotency guard) | Concurrent load test |
| P3-AC-09 | FICA withholding stops at wage base ceiling ($168,600 for 2025) | Unit test with YTD wages above ceiling |

---

## 7. Phase 4 — Integration, Reporting, and Cutover (Months 11–12)

### 7.1 Bounded Contexts in Scope

| Bounded Context | Legacy Owner | New System Module |
|---|---|---|
| Integration and Export (BC-09) | PKG_INTEGRATION | `integration-service` |
| Reporting (BC-10) | PKG_REPORTING | `reporting-service` |
| Benefits (BC-05) | PKG_INTEGRATION (partial) | `benefits-service` |

### 7.2 Defects Fixed in Phase 4

#### DEF-012 — ADP Benefits Feed: BENEFITS_ENROLLED Not Filtered (MEDIUM)

**Legacy code:** `PKG_INTEGRATION.export_benefits_feed` exports all active dependents via `LEFT JOIN EMPLOYEE_DEPENDENTS d ON ... d.ACTIVE_FLAG = 'Y'` without checking `BENEFITS_ENROLLED = 'Y'`. ADP receives un-enrolled dependents.

**New system fix:** `integration-service` benefits feed query adds `AND d.benefits_enrolled = TRUE`. Audit log records count of enrolled vs. total dependents per run.

#### DEF-013 — RPT_* Tables Never Populated (MEDIUM)

**Legacy code:** `PKG_REPORTING.refresh_reporting_tables` logs `'Reporting tables refreshed'` and returns. No DML. The RPT_* tables have never held data. All 7 report procedures query OLTP directly, causing lock contention during month-end reporting runs.

**New system fix:** `reporting-service` implements materialized views (PostgreSQL `MATERIALIZED VIEW` with `REFRESH CONCURRENTLY`) refreshed nightly via EventBridge Scheduler. Reports query the materialized views, never OLTP tables directly.

#### DEF-014 — Oracle MEDIAN() Non-portable (MEDIUM)

**Legacy code:** `compensation_summary` uses `MEDIAN()` aggregate, which has no direct PostgreSQL equivalent.

**New system fix:**
```sql
-- PostgreSQL percentile_cont equivalent:
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) AS median_salary
```

Seeded as a custom aggregate function in the reporting schema for code clarity.

### 7.3 Integration Service

**Replaces all PKG_INTEGRATION procedures:**

| Legacy Procedure | New Service Endpoint | Notes |
|---|---|---|
| `export_benefits_feed` | `POST /integrations/benefits-feed/export` | Fixes DEF-012; adds record count trailer; adds format version header (fixes TD-73) |
| `generate_gl_journal` | `POST /integrations/gl-journal/generate` | Adds GL_FEED_SENT_DATE to payroll_runs (fixes TD-80) |
| `sync_org_structure` | `POST /integrations/scim/sync` | Real LDAP/AD sync via SCIM 2.0 (fixes BR-ORG-01–05) |
| `import_time_attendance` | `POST /integrations/time-attendance/import` | Real CSV processing with transaction boundary; links to PAYROLL_DETAILS |
| `get_integration_status` | `GET /integrations/status` | Dashboard endpoint; covers all 4 integration types |

### 7.4 Phase 4 Acceptance Criteria

| ID | Criterion | Verification Method |
|---|---|---|
| P4-AC-01 | Benefits feed contains only enrolled dependents | Reconcile against benefit_enrollments table |
| P4-AC-02 | Benefits feed has format version header and record count trailer | File format validation script |
| P4-AC-03 | RPT_* materialized views refresh within 5 minutes nightly | Monitoring alert on refresh lag |
| P4-AC-04 | Compensation summary report shows same median salary as Oracle (PostgreSQL PERCENTILE_CONT) | Cross-system comparison test |
| P4-AC-05 | SCIM sync correctly updates department hierarchy from AD | Integration test with AD sandbox |
| P4-AC-06 | Time attendance import within transaction boundary; partial file failure rolls back entirely | Test with malformed CSV mid-file |
| P4-AC-07 | Full UAT sign-off from HR Director, CFO, and Legal | Signed UAT acceptance form |
| P4-AC-08 | Penetration test completed with no Critical or High findings | External pen test report |

---

## 8. Critical Defect Remediation Plan

### 8.1 Consolidated Defect Registry

| DEF-ID | Legacy Bug | CVSS / Severity | Phase Fixed | Owner | Test ID |
|---|---|---|---|---|---|
| DEF-001 | Hardcoded AES key `HR$ystem_3ncrypt10n_K3y_2024!!` | 9.8 Critical | 1 | Security Lead | P1-AC-05 |
| DEF-002 | Auth stub — password never verified; MD5 hashing | 9.8 Critical | 1 | Security Lead | P1-AC-02 |
| DEF-003 | `rehire_employee` ORA-00904 EMPLOYEE_HISTORY column mismatch | High | 1 | employee-service team | P1-AC-03 |
| DEF-004 | `generate_emp_number` race condition — duplicate EMP_NUMBERs | High | 1 | employee-service team | P1-AC-04 |
| DEF-005 | Leave accrual overwrite (`SET ACCRUED = v_accrued` instead of `+=`) | High | 2 | leave-service team | P2-AC-03 |
| DEF-006 | Calibration workflow absent — CALIBRATED_RATING never written | Medium | 2 | performance-service team | P2-AC-04 |
| DEF-007 | FMLA REQUIRES_DOCUMENT='N' — FMLA abuse risk | Medium | 2 | leave-service team | P2-AC-02 |
| DEF-008 | HOH tax = $0 — IRS compliance violation | 9.1 Critical | 3 | tax-service team | P3-AC-01 |
| DEF-009 | Direct deposit unimplemented — EMPLOYEE_BANK_ACCOUNTS never read | Critical | 3 | disbursement-service team | P3-AC-04 |
| DEF-010 | `calculate_final_pay` procedure does not exist | Critical | 3 | payroll-service team | P3-AC-06 |
| DEF-011 | Routing number stored plaintext | High | 3 | disbursement-service team | P3-AC-07 |
| DEF-012 | ADP benefits feed includes non-enrolled dependents | Medium | 4 | integration-service team | P4-AC-01 |
| DEF-013 | RPT_* tables never populated (refresh_reporting_tables stub) | Medium | 4 | reporting-service team | P4-AC-03 |
| DEF-014 | Oracle MEDIAN() non-portable to PostgreSQL | Low | 4 | reporting-service team | P4-AC-04 |

### 8.2 HOH Tax Retroactive Correction

The HOH = $0 bug requires a separate track of work outside the engineering migration:

| Step | Owner | Timeline |
|---|---|---|
| 1. Identify all employees ever filed as HEAD_OF_HOUSEHOLD in PAYROLL_DETAILS | Payroll Admin + DBA | Month 7, Week 1 |
| 2. Calculate correct federal tax for each affected pay period | Tax Specialist | Month 7, Weeks 1–3 |
| 3. Produce correction report for each affected employee | Payroll Admin | Month 7, Week 4 |
| 4. Issue corrected W-2c forms for prior tax years | Payroll / Finance | Month 8 |
| 5. Process off-cycle withholding adjustments if required | Payroll Admin | Month 8–9 |
| 6. Notify affected employees | HR Communications | Month 8 |

---

## 9. Data Migration Strategy

### 9.1 Migration Approach

A phased extract-transform-load (ETL) approach is used, with validation gates between each phase.

```
Oracle 19c (legacy)
        │
        ▼
  Oracle Exporter (GoldenGate / Debezium)
        │
        ▼
  Staging Schema (PostgreSQL)         ← raw dump; no transformation
        │
        ▼
  Transform Layer                     ← key rotation, schema mapping, validation
        │
        ▼
  New HRMS PostgreSQL                 ← production target schema
        │
        ▼
  Reconciliation Checks               ← row counts, financial totals, PII spot-check
```

### 9.2 Table Migration Map

| Oracle Table | New Table(s) | Key Transformations | Phase |
|---|---|---|---|
| EMPLOYEES | employees | Re-encrypt SSN with new key; map GRADE to role enum; normalize TAX_FILING_STATUS | 1 |
| DEPARTMENTS | departments | No change to structure | 1 |
| JOB_POSITIONS | job_positions | Rename POSITION_ID → id; add created_at/updated_at | 1 |
| USER_CREDENTIALS | user_credentials | Migrate to bcrypt (force password reset on first login) | 1 |
| USER_SESSIONS | (JWT — no migration) | Sessions not migrated; all users re-authenticate | 1 |
| EMPLOYEE_HISTORY | employment_history | Fix COLUMN_NAME mismatch (ORA-00904 root cause) | 1 |
| LEAVE_BALANCES | leave_balances | Validate all balances ≥ 0; flag negative balances for review | 2 |
| LEAVE_REQUESTS | leave_requests | Migrate STATUS codes to enum; link to new leave_types | 2 |
| PERFORMANCE_REVIEWS | performance_reviews | Map OVERALL_RATING; CALIBRATED_RATING left NULL (not yet set in legacy) | 2 |
| REVIEW_CYCLES | review_cycles | No structural change | 2 |
| SALARY_RECORDS | salary_records | Validate current salary row is unique (END_DATE IS NULL) | 3 |
| PAYROLL_RUNS | payroll_runs | Add ACH_FILE_NAME, GL_FEED_SENT_DATE columns | 3 |
| PAYROLL_DETAILS | payroll_details | Add element_type enum; map legacy ELEMENT_ID 100–103 | 3 |
| EMPLOYEE_BANK_ACCOUNTS | employee_bank_accounts | Re-encrypt ACCOUNT_NUMBER and ROUTING_NUMBER | 3 |
| TAX_BRACKETS | tax_brackets | Seed IRS 2025 data; back-fill HOH brackets | 3 |
| EMPLOYEE_DEPENDENTS | employee_dependents | Re-encrypt SSN_ENCRYPTED with new key | 3 |
| BENEFIT_PLANS | benefit_plans | No structural change | 4 |
| BENEFIT_ENROLLMENTS | benefit_enrollments | No structural change | 4 |
| AUDIT_LOG | audit_log | Partition by year; convert to structured JSON body | 4 |

### 9.3 Encryption Key Rotation Procedure

This is the highest-risk data migration operation. It must be executed in a dedicated maintenance window with DBA and Security Lead present.

```
Step 1: Stop writes to Oracle HRMS (scheduled maintenance window, 4 hours)
Step 2: Extract all rows containing encrypted columns to secure staging (encrypted tablespace)
Step 3: Decrypt each value using legacy key: HR$ystem_3ncrypt10n_K3y_2024!!
Step 4: Re-encrypt each value using new key retrieved from Vault
Step 5: Write re-encrypted values to new system staging table
Step 6: Validate: count(encrypted) == count(staged); spot-check 100 random rows decrypt correctly
Step 7: Promote staging to production
Step 8: Invalidate legacy key in Vault (set to DEPRECATED; zero copies remain)
Step 9: Resume writes to new system; CDC bridge active

Affected columns:
  EMPLOYEES.SSN (re-encrypt)
  EMPLOYEES.BANK_ACCOUNT_NUMBER (re-encrypt)
  EMPLOYEES.BANK_ROUTING_NUMBER (re-encrypt)
  EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED (re-encrypt)
  EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC (re-encrypt)
  USER_CREDENTIALS.PASSWORD_HASH (migrate to bcrypt; users must reset password)
```

### 9.4 Password Migration

`USER_CREDENTIALS.PASSWORD_HASH` stores MD5 hashes. MD5 cannot be converted to bcrypt without the plaintext. Strategy:

1. All existing password hashes are marked `requires_reset = TRUE` in the new system.
2. On first login attempt, user is redirected to a forced password reset flow.
3. New password is stored as bcrypt.
4. MD5 hash record is deleted after successful reset.
5. Users who do not reset within 30 days are sent an email reminder.
6. After 90 days, accounts with unreset passwords are suspended until reset is completed.

### 9.5 Data Validation Checklist (per Phase)

| Check | Method | Pass Criteria |
|---|---|---|
| Row count parity | `SELECT COUNT(*) FROM oracle_table` vs. new table | 100% match |
| Financial total parity | SUM(BASE_SALARY), SUM(NET_PAY) per payroll run | Match to 2 decimal places |
| PK uniqueness | `COUNT(*) vs. COUNT(DISTINCT id)` | 100% unique |
| FK integrity | No orphaned records | 0 orphans |
| Encrypted column spot-check | Decrypt 100 random SSNs; compare to Oracle | 100% match |
| Negative balance detection | `SELECT * FROM leave_balances WHERE accrued < 0` | Flag for HR review; do not block migration |
| NULL constraint enforcement | Check all NOT NULL columns | 0 nulls in NOT NULL columns |

---

## 10. Cutover Plan

### 10.1 Cutover Timeline (Month 12)

| Week | Activity | Owner | Risk |
|---|---|---|---|
| Week 1 | Final UAT; penetration test report delivered | QA + Security | High if findings emerge |
| Week 2 | Parallel payroll run (Oracle + new system, same pay period) | Payroll + Engineering | Critical — must match |
| Week 3 | Production readiness review; sign-off from HR, Finance, Legal, CTO | Programme Manager | Programme stop if not signed |
| Week 4 | Cutover weekend; CDC bridge decommission; Oracle read-only mode | DBA + Engineering | Highest risk window |

### 10.2 Cutover Weekend Runbook

```
Friday 17:00 — Freeze Oracle writes (change app config to read-only mode)
Friday 17:05 — Final CDC sync flush; verify all events consumed
Friday 17:30 — Run final reconciliation queries (row counts, financial totals)
Friday 18:00 — Go/No-Go decision call (Engineering Lead + HR Director + CFO)
              — If NO-GO: Oracle remains primary; schedule retry
              — If GO: proceed
Friday 18:15 — Update DNS / load balancer to route all traffic to new system
Friday 18:30 — Smoke tests: login, view employee, submit leave request, view payslip
Saturday 09:00 — Monitoring review: error rate, latency, queue depths
Saturday 12:00 — CDC bridge decommissioned (Oracle no longer receives writes)
Saturday 17:00 — Oracle HRMS set to archive mode (no writes; readable for 90 days)
Monday 08:00 — All users on new system; Hypercare period begins (2 weeks)
```

### 10.3 Go/No-Go Criteria

| Criterion | Pass Threshold | Owner |
|---|---|---|
| Parallel payroll run match | 100% to the cent | Finance |
| Error rate in new system | < 0.1% over 48-hour soak | Engineering |
| P95 API latency | < 500ms | Engineering |
| All P0/P1 defects resolved | 0 open P0/P1 | QA Lead |
| UAT sign-off | HR, Finance, Legal signed | Programme Manager |
| Pen test | No Critical/High open findings | Security Lead |
| Runbook walk-through completed | DBA team sign-off | DBA Lead |

---

## 11. Rollback Strategy

### 11.1 Phase-Level Rollback

Each phase maintains a rollback path until the next phase's go-live. The Strangler Fig pattern means rollback is a routing change, not a data restore.

| Phase | Rollback Trigger | Rollback Action | RTO |
|---|---|---|---|
| Phase 1 | P1 blocking defect found in production | Feature flag routes auth/employee traffic back to Oracle | < 15 minutes |
| Phase 2 | Leave balance discrepancy > 0.1% | Feature flag routes leave traffic back to Oracle | < 15 minutes |
| Phase 3 | Payroll calculation error found | Feature flag routes payroll to Oracle; new-system payroll run voided | < 30 minutes |
| Phase 4 (post-cutover) | Critical production incident | See Section 11.2 | < 4 hours |

### 11.2 Full Rollback (Post-Cutover)

Full rollback is only triggered if a P0 incident (data corruption, payroll failure, security breach) is confirmed after final cutover.

```
Step 1: Declare incident; notify HR Director and CTO
Step 2: Re-enable Oracle HRMS writes (remove read-only flag on config)
Step 3: Route all traffic back to Oracle via load balancer config change (< 5 min)
Step 4: Apply any writes made to new system since cutover back to Oracle
        (CDC bridge logs retained for 7 days post-cutover for this purpose)
Step 5: Assess root cause; schedule next cutover attempt
```

**Note:** Full rollback has an RPO risk for writes that occurred in the new system but were not yet replicated to Oracle. The CDC bridge is retained in DRAIN mode for 7 days post-cutover to minimise this risk. Any writes during the drain window are replicated with < 5-second lag.

### 11.3 Database-Level Rollback

All schema migrations use tools with explicit down migrations:

- **Flyway** for PostgreSQL schema migrations — every `V{n}__description.sql` file has a corresponding `U{n}__description.sql` undo script.
- Pre-cutover DB snapshot taken at `T-2h` and retained for 30 days.
- Point-in-time recovery (PITR) enabled on RDS PostgreSQL with 7-day retention.

---

## 12. Team Structure and Sprint Plan

### 12.1 Team Structure

| Team | Members | Phase Focus |
|---|---|---|
| Platform / Infra | 2 engineers | All phases: AWS, Terraform, CI/CD, observability |
| Security | 1 engineer (shared) | All phases: key rotation, auth, pen test |
| auth-service | 2 engineers | Phase 1 |
| employee-service | 3 engineers | Phase 1 (continues to Phase 2 for events) |
| leave-service | 2 engineers | Phase 2 |
| performance-service | 2 engineers | Phase 2 |
| notification-service | 1 engineer | Phase 2 |
| payroll-service | 3 engineers | Phase 3 |
| tax-service | 2 engineers | Phase 3 |
| disbursement-service | 2 engineers | Phase 3 |
| integration-service | 2 engineers | Phase 4 |
| reporting-service | 2 engineers | Phase 4 |
| QA (embedded) | 1 per team | All phases |
| Data Migration | 2 engineers + 1 DBA | Phases 1–4 (migration sprints) |

**Total headcount:** ~30 engineers + 1 dedicated DBA + Programme Manager

### 12.2 Sprint Plan

#### Phase 1 — Foundation (Months 1–3, 6 Sprints × 2 weeks)

| Sprint | auth-service | employee-service | Platform / Infra |
|---|---|---|---|
| S1 | Login, JWT, RBAC setup | Employee CRUD, sequence-based EMP_NUMBER | AWS setup, Terraform, PostgreSQL RDS |
| S2 | Change password (old PW required), lockout | Department CRUD, org hierarchy (recursive CTE) | CI/CD pipeline (GitHub Actions), Flyway |
| S3 | Session expiry, MFA scaffold | rehire_employee, transfer_employee | Kafka setup, CDC bridge (Debezium) |
| S4 | SCIM provisioning (Phase 1 scope) | EMPLOYEE_DEPENDENTS CRUD, inactivation on termination | Observability (OpenTelemetry, Datadog) |
| S5 | Auth pen test prep | Employment history, audit trail | Key rotation infrastructure (Vault) |
| S6 | Security hardening; P1 acceptance tests | Data migration: EMPLOYEES, DEPARTMENTS | Phase 1 migration dry-run; reconciliation |

#### Phase 2 — Core HR (Months 4–6, 6 Sprints × 2 weeks)

| Sprint | leave-service | performance-service | notification-service |
|---|---|---|---|
| S7 | Leave types, balance initialization | Review cycle creation, self-assessment | Email channel (AWS SES) |
| S8 | Leave request workflow, approval | Manager review, rating validation | SMS channel (AWS SNS) |
| S9 | Monthly accrual (atomic upsert fix) | Calibration workflow (new) | Template engine (Handlebars) |
| S10 | FMLA document enforcement | Rating distribution report (calibrated) | Retry + DLQ |
| S11 | Leave data migration; balance reconciliation | Performance data migration | Notification history |
| S12 | P2 acceptance tests | P2 acceptance tests | P2 integration tests |

#### Phase 3 — Payroll Engine (Months 7–10, 8 Sprints × 2 weeks)

| Sprint | payroll-service | tax-service | disbursement-service |
|---|---|---|---|
| S13 | Payroll run CRUD, status machine | Tax bracket seed (incl. HOH) | Employee bank account CRUD |
| S14 | calculate_employee_pay, gross calculation | Federal tax calculation (all filing statuses) | ACH prenote implementation |
| S15 | Deductions, benefit deductions | State income tax, FICA | NACHA file generation |
| S16 | Approval workflow, GL journal generation | YTD earnings API | Split deposit logic (all DEPOSIT_TYPEs) |
| S17 | calculate_final_pay (termination-triggered) | Additional Medicare, wage base ceiling | ACH file delivery |
| S18 | Parallel payroll run #1 (compare to Oracle) | HOH tax retroactive report | Routing number encryption |
| S19 | Parallel payroll run #2 (Finance sign-off) | Tax bracket annual update workflow | Disbursement reconciliation report |
| S20 | P3 acceptance tests; payroll data migration | P3 acceptance tests | P3 acceptance tests |

#### Phase 4 — Integration, Reporting, Cutover (Months 11–12, 4 Sprints × 2 weeks)

| Sprint | integration-service | reporting-service | Cutover |
|---|---|---|---|
| S21 | Benefits feed (with enrollment filter) | Materialized views for all 7 reports | UAT preparation |
| S22 | GL journal, time-attendance import, SCIM sync | Reporting API, EEO compliance report | UAT execution; pen test |
| S23 | Integration acceptance tests | Reporting acceptance tests | Parallel run sign-off; runbook rehearsal |
| S24 | Final integration validation | Final reporting validation | Cutover weekend; hypercare |

### 12.3 Definition of Done (per Story)

- [ ] All acceptance criteria from specification pass as automated tests
- [ ] Code reviewed by at least one other engineer
- [ ] No critical or high findings from SAST (Semgrep / CodeQL in CI)
- [ ] No secrets detected by gitleaks
- [ ] Structured logging implemented (JSON, correlation ID)
- [ ] Health endpoint responds 200
- [ ] Swagger/OpenAPI spec updated
- [ ] Data migration script (if applicable) has tested rollback

---

## 13. Non-Functional Requirements

### 13.1 Security

| Requirement | Standard | Implementation |
|---|---|---|
| Password storage | NIST SP 800-63B | bcrypt cost 12 |
| Encryption at rest | AES-256-GCM | AWS KMS + Vault |
| Encryption in transit | TLS 1.3 minimum | ACM certificates via ALB |
| Secret management | No secrets in source code | Vault; gitleaks in CI (blocks merge) |
| Session management | 1-hour JWT; 7-day refresh | Redis token store |
| RBAC | Role-based (HR_ADMIN, HR_MANAGER, EMPLOYEE) | JWT claims + Spring Security / FastAPI middleware |
| Audit logging | All PII access logged | Structured log to SIEM (Splunk / CloudWatch) |
| Vulnerability scanning | OWASP Top 10 | OWASP ZAP in CI; quarterly pen test |

### 13.2 Availability and Performance

| Metric | Target |
|---|---|
| Availability (SLA) | 99.9% (excluding scheduled maintenance) |
| P95 API response time | < 500ms |
| Payroll run (1000 employees) | < 10 minutes |
| Reporting query (materialized) | < 5 seconds |
| Recovery Time Objective (RTO) | < 4 hours |
| Recovery Point Objective (RPO) | < 1 hour |

### 13.3 Observability Requirements

Every service must ship with:

1. **Structured JSON logging** — all log entries include `service`, `trace_id`, `span_id`, `employee_id` (where applicable), `severity`, `message`.
2. **Distributed tracing** — OpenTelemetry SDK; traces exported to Jaeger or AWS X-Ray.
3. **Metrics** — RED metrics (Rate, Errors, Duration) per endpoint exposed via Prometheus; dashboards in Grafana.
4. **Health endpoints** — `GET /health/live` (liveness) and `GET /health/ready` (readiness) on every service.
5. **Alerting** — PagerDuty alerts for: error rate > 1%, P95 latency > 2s, payroll run failure, ACH file generation failure, CDC bridge lag > 60s.

### 13.4 Compliance Requirements

| Regulation | Requirement | Implementation |
|---|---|---|
| IRS (Federal Tax) | Correct withholding for all filing statuses | tax-service with fully seeded TAX_BRACKETS incl. HOH (fixes DEF-008) |
| Nacha (ACH) | Prenote required before first live payment | disbursement-service prenote workflow (fixes PP-BA-03) |
| COBRA | 14-day notification on qualifying event | Benefits-service COBRA notification on employee.terminated event |
| FMLA | Documentation required for FMLA leave | leave-service requires_document enforcement (fixes DEF-007) |
| SOX | Audit trail for all financial data changes | Immutable audit_log with retention policy |
| GDPR / CCPA | PII encrypted at rest; right to erasure workflow | Vault-managed encryption; pseudonymisation for terminated employee records |

---

## 14. Appendix A — Technology Stack Decision Record

| Layer | Technology | Rationale | Alternative Considered |
|---|---|---|---|
| Database | PostgreSQL 16 | Open source; excellent JSON support; no Oracle license dependency; PITR; recursive CTE replaces CONNECT BY | MySQL 8, Aurora |
| Auth service | Node.js 22 / Fastify | Fast startup; JWT libraries mature; low latency | Go / Gin |
| Core services (employee, payroll) | Java 21 / Spring Boot 3.3 | Strong typing for financial calculations; Spring Security for RBAC; mature ecosystem | Kotlin / Ktor |
| Analytical services (leave, tax, reporting) | Python 3.12 / FastAPI | Rapid iteration; pandas for reconciliation scripts; async for long-running accrual jobs | Go |
| Frontend | React 18 / TypeScript | Replaces Oracle Forms; large talent pool; component testing with Playwright | Vue 3, Next.js |
| Event bus | Apache Kafka (MSK) | Durable event log; supports CDC bridge; replay capability for audit | RabbitMQ, SQS |
| Cache / Rate-limiting | Redis 7 (ElastiCache) | Session rate limiting; notification deduplication | Memcached |
| Secrets | HashiCorp Vault (HCP) | Dynamic secrets; key rotation; audit log of every secret access | AWS Secrets Manager |
| CI/CD | GitHub Actions | Repository-native; SAST (CodeQL) and secret scanning (gitleaks) built-in; no separate server | Jenkins, GitLab CI |
| IaC | Terraform | Cross-cloud; state management; plan/apply workflow | AWS CDK |
| Observability | OpenTelemetry + Datadog | Vendor-neutral traces; single pane for logs, metrics, traces | Prometheus + Grafana + Jaeger |
| Schema migrations | Flyway | Ordered versioned migrations; undo scripts; CI integration | Liquibase |
| Load testing | k6 | JavaScript scripting; CI integration; payroll load simulation | JMeter |

---

*End of document. All 14 sections complete.*

*This specification is the authoritative forward engineering reference. Changes require approval from the Programme Manager and at least two of: HR Director, Engineering Lead, Security Lead.*
