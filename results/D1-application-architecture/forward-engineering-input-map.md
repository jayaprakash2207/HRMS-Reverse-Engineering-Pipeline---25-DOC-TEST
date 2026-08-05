# Forward Engineering Input Map — HRMS Oracle Forms Application

**Extractor:** AA Agent 1 — Application Architecture Extractor  
**Date:** 2026-08-04  
**Purpose:** Maps each legacy component to its recommended target architecture equivalent. This document feeds directly into the Design and Implementation phases of the modernization project.

---

## 1. Target Architecture Overview

| Tier | Legacy | Target |
|------|--------|--------|
| UI | Oracle Forms 12c (.fmb) | React / Angular SPA or Next.js |
| API | PL/SQL packages (direct DB call from Forms) | RESTful microservices (Java/Spring Boot, Node.js, or Python FastAPI) |
| Auth | PKG_SECURITY + Oracle Forms globals | OAuth2 / OIDC (Keycloak or Auth0) |
| Data | Oracle RDBMS HRMS schema | Oracle DB (retain) or PostgreSQL (migrate) |
| Integration | UTL_FILE flat files + UTL_SMTP | REST APIs + message broker (Kafka or RabbitMQ) |
| Audit | AUDIT_LOG table + PKG_AUDIT | Append-only event store or audit service |
| Scheduler | DBMS_SCHEDULER (implied) | Kubernetes CronJob or cloud-native scheduler |

---

## 2. Module-to-Service Mapping

### 2.1 Employee Module (MOD-001 → Employee Service)

**New Service:** `employee-service`  
**API Base Path:** `/api/v1/employees`

| Legacy Procedure | Target API Endpoint | Method | Notes |
|---|---|---|---|
| PKG_EMPLOYEE.create_employee | POST /employees | POST | Input validation in API layer |
| PKG_EMPLOYEE.update_employee | PATCH /employees/{id} | PATCH | |
| PKG_EMPLOYEE.get_employee | GET /employees/{id} | GET | |
| PKG_EMPLOYEE.get_employee_by_number | GET /employees?empNumber={n} | GET | |
| PKG_EMPLOYEE.search_employees | GET /employees/search?lastName=&firstName=&deptId= | GET | Fix SQL injection: use ORM/parameterized queries |
| PKG_EMPLOYEE.transfer_employee | POST /employees/{id}/transfers | POST | Event emitted on transfer |
| PKG_EMPLOYEE.promote_employee | POST /employees/{id}/promotions | POST | |
| PKG_EMPLOYEE.terminate_employee | POST /employees/{id}/terminations | POST | Complete TODO items before migration |
| PKG_EMPLOYEE.rehire_employee | POST /employees/{id}/rehires | POST | |
| PKG_EMPLOYEE.get_org_chart | GET /employees/{id}/org-chart?maxDepth={n} | GET | Implement with graph DB or recursive CTE with timeout |
| PKG_EMPLOYEE.get_direct_reports | GET /employees/{id}/direct-reports | GET | |
| PKG_EMPLOYEE.is_active | Internalized — not a public API | N/A | Called by Payroll service via service-to-service call |

**Data Ownership:** EMPLOYEES, EMPLOYEE_HISTORY, DEPARTMENTS, LOCATIONS, JOB_TITLES, JOB_GRADES tables.

**Events Emitted:**
- `employee.created` — on hire
- `employee.transferred` — on transfer
- `employee.promoted` — on promotion
- `employee.terminated` — on termination
- `employee.rehired` — on rehire

---

### 2.2 Leave Module (MOD-002 → Leave Service)

**New Service:** `leave-service`  
**API Base Path:** `/api/v1/leave`

| Legacy Procedure | Target API Endpoint | Method | Notes |
|---|---|---|---|
| PKG_LEAVE.submit_leave_request | POST /leave/requests | POST | |
| PKG_LEAVE.approve_leave_request | POST /leave/requests/{id}/approve | POST | |
| PKG_LEAVE.reject_leave_request | POST /leave/requests/{id}/reject | POST | |
| PKG_LEAVE.cancel_leave_request | POST /leave/requests/{id}/cancel | POST | |
| PKG_LEAVE.get_leave_balance | GET /leave/balances/{empId}?year= | GET | |
| PKG_LEAVE.get_pending_requests | GET /leave/requests?approver={id}&status=PENDING | GET | |
| PKG_LEAVE.get_team_calendar | GET /leave/calendar?manager={id}&from=&to= | GET | |
| PKG_LEAVE.run_monthly_accrual | Internal scheduled task (monthly) | N/A | Kubernetes CronJob |
| PKG_LEAVE.process_carryover | Internal scheduled task (annual) | N/A | Kubernetes CronJob |

**Data Ownership:** LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS, LEAVE_ACCRUAL_LOG, HOLIDAYS tables.

**Events Consumed:** `employee.terminated` (to cancel pending leave)  
**Events Emitted:** `leave.submitted`, `leave.approved`, `leave.rejected`, `leave.cancelled`

---

### 2.3 Payroll Module (MOD-003 → Payroll Service or SaaS)

**Recommendation:** Replace with payroll SaaS (ADP Workforce Now API, Paylocity, Gusto) rather than building a custom service. Custom payroll tax calculation is high-compliance-risk.

If custom service is required:

**New Service:** `payroll-service`  
**API Base Path:** `/api/v1/payroll`

| Legacy Procedure | Target API Endpoint | Method | Notes |
|---|---|---|---|
| PKG_PAYROLL.create_payroll_run | POST /payroll/runs | POST | |
| PKG_PAYROLL.calculate_payroll | POST /payroll/runs/{id}/calculate | POST | Async job — return 202 Accepted + job ID |
| PKG_PAYROLL.approve_payroll | POST /payroll/runs/{id}/approve | POST | |
| PKG_PAYROLL.get_payslip | GET /payroll/payslips/{runId}/{empId} | GET | Fix YTD placeholder before migration |
| PKG_PAYROLL.get_ytd_earnings | GET /payroll/ytd/{empId}?year= | GET | |
| Tax calculation | External tax engine (e.g., Avalara, Vertex) | N/A | Replace hard-coded brackets |

**Critical Migration Requirements:**
- Replace hard-coded 2024 tax brackets with external tax engine API
- Implement YTD calculation (currently placeholder zeros)
- Rewrite as async job (not synchronous blocking call)
- Implement ACH direct deposit disbursement: EMPLOYEE_BANK_ACCOUNTS is fully designed but zero code reads it. Target system must add bank account CRUD, split-deposit resolution (PRIORITY_ORDER, DEPOSIT_TYPE logic), prenote/pre-notification workflow, and NACHA file generation or payroll SaaS API call. See AV-024, RISK-013.
- Identify and document bank account decryption path (ACCOUNT_NUMBER_ENC) before migration — decryption key/mechanism is absent from all source packages. See AV-025, RISK-014.

**New APIs Required (not present in legacy codebase):**

| Target API Endpoint | Method | Purpose |
|---|---|---|
| POST /payroll/employees/{id}/bank-accounts | POST | Add direct deposit account |
| PUT /payroll/employees/{id}/bank-accounts/{acctId} | PUT | Update account or deposit split |
| DELETE /payroll/employees/{id}/bank-accounts/{acctId} | DELETE | Deactivate account |
| GET /payroll/employees/{id}/bank-accounts | GET | List active bank accounts |
| POST /payroll/runs/{id}/disburse | POST | Trigger ACH disbursement after approval |

---

### 2.4 Performance Module (MOD-004 → Performance Service)

**New Service:** `performance-service`  
**API Base Path:** `/api/v1/performance`

| Legacy Procedure | Target API Endpoint | Method | Notes |
|---|---|---|---|
| PKG_PERFORMANCE.create_review_cycle | POST /performance/cycles | POST | |
| PKG_PERFORMANCE.open_review_cycle | POST /performance/cycles/{id}/open | POST | |
| PKG_PERFORMANCE.close_review_cycle | POST /performance/cycles/{id}/close | POST | |
| PKG_PERFORMANCE.submit_self_assessment | POST /performance/reviews/{id}/self-assessment | POST | |
| PKG_PERFORMANCE.submit_manager_review | POST /performance/reviews/{id}/manager-review | POST | |
| PKG_PERFORMANCE.acknowledge_review | POST /performance/reviews/{id}/acknowledge | POST | |
| PKG_PERFORMANCE.add_goal | POST /performance/reviews/{id}/goals | POST | |
| PKG_PERFORMANCE.get_rating_distribution | GET /performance/cycles/{id}/rating-distribution | GET | |
| PKG_PERFORMANCE.generate_reviews_for_cycle | POST /performance/cycles/{id}/generate-reviews | POST | Async job for large orgs |

---

### 2.5 Reporting Module (MOD-005 → BI Integration)

**Recommendation:** Decommission PKG_REPORTING. Expose read endpoints from each service and connect a BI tool (Power BI, Oracle Analytics Cloud, Metabase).

| Legacy Procedure | Target Approach |
|---|---|
| PKG_REPORTING.headcount_report | Power BI dataset from Employee Service |
| PKG_REPORTING.compensation_summary | Power BI dataset from Employee + Payroll Service |
| PKG_REPORTING.turnover_report | Power BI dataset from Employee Service events |
| PKG_REPORTING.leave_utilization_report | Power BI dataset from Leave Service |
| PKG_REPORTING.payroll_summary_report | Power BI dataset from Payroll Service |
| PKG_REPORTING.eeo_compliance_report | Power BI dataset — requires EEO data (GENDER, ETHNICITY from EMPLOYEES) |

---

### 2.6 Integration Module (MOD-006 → Integration Middleware)

| Legacy Integration | Current Mechanism | Target Mechanism |
|---|---|---|
| Oracle Financials GL | Flat file (UTL_FILE pipe-delimited) | Oracle Financials REST API or Oracle Integration Cloud |
| ADP Benefits | Fixed-width FTP file | ADP API (ADP Marketplace REST APIs) |
| Time & Attendance | TODO stub (not implemented) | Time system REST API |

**New Component:** `integration-service` or Oracle Integration Cloud (OIC) flows per external system.

---

### 2.7 Notification Module (MOD-007 → Notification Service)

**New Service:** `notification-service`  
**Mechanism:** Replace UTL_SMTP with email provider API (SendGrid, AWS SES, Mailgun).

| Legacy | Target |
|---|---|
| NOTIFICATION_QUEUE table | Message broker topic (Kafka `notifications` topic) |
| UTL_SMTP | SendGrid / AWS SES REST API |
| SMS type (unimplemented) | Twilio API |
| IN_APP type (unimplemented) | WebSocket push or Server-Sent Events |

---

### 2.8 Audit Module (MOD-008 → Audit Service)

**New Component:** `audit-service` or structured event log.

| Legacy | Target |
|---|---|
| AUDIT_LOG table | Append-only event store (EventStoreDB, or Kafka compacted topic) |
| PKG_AUDIT.log_action | Each service emits audit events on state change |
| PKG_AUDIT.purge_old_records | Retention policy in event store (e.g., 7-year GDPR retention) |
| PKG_AUDIT.get_change_history | GET /audit/changes?entity=EMPLOYEES&recordId={id}&from=&to= |

---

### 2.9 Security Module (MOD-009 → Identity Service)

| Legacy | Target |
|---|---|
| PKG_SECURITY.authenticate | OAuth2 /token endpoint (Keycloak or Auth0) |
| PKG_SECURITY.is_session_valid | JWT token validation (middleware in each service) |
| PKG_SECURITY.has_permission | RBAC claims in JWT token |
| PKG_SECURITY.encrypt_ssn / decrypt_ssn | AWS KMS or HashiCorp Vault transit encryption |
| PKG_SECURITY.hash_password | bcrypt (rounds=12) |
| USER_SESSIONS table | OAuth2 refresh tokens (stateless JWT access tokens) |

---

### 2.10 Common Module (MOD-011 → Shared Library + Config Service)

| Legacy | Target |
|---|---|
| PKG_COMMON.get_param / set_param | Config service (Spring Cloud Config, or AWS Parameter Store) |
| PKG_COMMON date utilities | Standard library functions per language |
| PKG_COMMON.format_* | Shared utility library (npm package or Maven artifact) |
| PKG_COMMON.is_valid_* | Shared validation library (resolve client/server drift at this point) |
| PKG_COMMON.log_error / log_info | Structured logging (JSON → ELK Stack / CloudWatch) |

---

## 3. Data Migration Notes

| Table Group | Target | Migration Notes |
|---|---|---|
| EMPLOYEES, EMPLOYEE_HISTORY, DEPARTMENTS, JOB_TITLES, JOB_GRADES, LOCATIONS | Employee Service DB | Decrypt SSNs during migration with new key (resolve VIO-001 first) |
| SALARY_RECORDS, PAY_ELEMENTS, EMPLOYEE_PAY_ELEMENTS, PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS, TAX_BRACKETS | Payroll Service DB or SaaS import | TAX_BRACKETS must be populated with historical data |
| EMPLOYEE_BANK_ACCOUNTS | Payroll Service DB or SaaS import | ACCOUNT_NUMBER_ENC must be decrypted before migration (decryption key/mechanism not found in source — resolve RISK-014 first). Validate split-deposit logic: every employee should have exactly one FULL or REMAINDER account and no conflicting DEPOSIT_PERCENTAGE/DEPOSIT_AMOUNT sums. PRENOTE_SENT flags should be audited against actual ACH prenote history before import. |
| LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS, LEAVE_ACCRUAL_LOG, HOLIDAYS | Leave Service DB | LEAVE_BALANCES are point-in-time snapshots — migrate last in cycle |
| REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS | Performance Service DB | |
| AUDIT_LOG | Audit Service / event store | Preserve for compliance; do not delete |
| NOTIFICATION_QUEUE | Message broker | Drain queue before migration |
| USER_SESSIONS | Discard | Replace with OAuth2 tokens |
| SYSTEM_PARAMETERS | Config service | Scrub FTP credentials before migration |
| LOOKUP_VALUES | Per-service reference data | |

---

## 4. Oracle Forms UI Migration

| Legacy Form | Target Web Component | Framework |
|---|---|---|
| HRMS_LOGIN.fmb | Login page with OAuth2 redirect | React |
| HRMS_MENU.fmb | Navigation shell / sidebar | React |
| HRMS_EMPLOYEE.fmb | Employee management module | React |
| HRMS_PAYROLL.fmb | Payroll management module | React |
| HRMS_LEAVE.fmb | Leave self-service portal | React |
| HRMS_PERFORMANCE.fmb | Performance review module | React |
| HRMS_REPORTS.fmb (not in source) | BI tool embedded reports | Power BI or Metabase |
| HRMS_ADMIN.fmb (not in source) | Admin console | React |
