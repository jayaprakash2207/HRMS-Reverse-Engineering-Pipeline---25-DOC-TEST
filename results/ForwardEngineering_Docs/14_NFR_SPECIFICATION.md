# 14 — Non-Functional Requirements Specification
**System:** Acme Corporation HRMS (Modernised — Forward Engineering Target)
**Version:** 1.0
**Date:** 2026-08-05
**Status:** Draft for Review
**Scope:** All components replacing the Oracle 19c / Oracle Forms 12c HRMS monolith
**Author:** Solution Architecture (derived from BA_Deep_Analyst, DA_Data_Reviewer, TA_Deep_Analyst, AA_Quality_Review)

---

## Document Purpose

This specification defines the non-functional requirements (NFRs) for the modernised Acme HRMS system. These requirements govern how the system performs, scales, operates, and is secured — independent of functional behaviour. Every NFR in this document carries a measurable acceptance criterion and a traceability reference to the source analysis finding that motivated it.

NFRs in this document take precedence over convenience or cost in architectural decisions. Where a functional requirement conflicts with an NFR, the NFR governs unless explicitly waived by the business sponsor in writing.

---

## 1. Performance Requirements

### 1.1 Response Time SLAs

All response time targets are measured at the **95th percentile** of production traffic under normal load (defined as ≤ 500 concurrent users). The 99th percentile column is the hard ceiling — requests exceeding it must be logged as SLA breaches.

| Endpoint Category | P50 Target | P95 Target | P99 Hard Ceiling | Measurement Point |
|---|---|---|---|---|
| Authentication (login, token refresh) | < 200 ms | < 500 ms | < 1 000 ms | API gateway ingress |
| Employee read (single record GET) | < 100 ms | < 300 ms | < 800 ms | API gateway ingress |
| Employee list / search (paginated, ≤ 100 rows) | < 200 ms | < 600 ms | < 1 500 ms | API gateway ingress |
| Org chart hierarchy traversal (≤ 5 levels) | < 300 ms | < 800 ms | < 2 000 ms | API gateway ingress |
| Leave balance read | < 100 ms | < 300 ms | < 800 ms | API gateway ingress |
| Leave request submit (write) | < 300 ms | < 700 ms | < 1 500 ms | API gateway ingress |
| Payroll calculation (single employee) | < 500 ms | < 1 500 ms | < 3 000 ms | Service boundary |
| Payroll run status poll | < 100 ms | < 250 ms | < 600 ms | API gateway ingress |
| Performance review read | < 150 ms | < 400 ms | < 1 000 ms | API gateway ingress |
| Performance review submit / save | < 400 ms | < 900 ms | < 2 000 ms | API gateway ingress |
| Reporting dashboard (pre-aggregated) | < 500 ms | < 1 200 ms | < 3 000 ms | API gateway ingress |
| Ad-hoc report (live query, ≤ 10 000 rows) | < 2 000 ms | < 5 000 ms | < 10 000 ms | Service boundary |
| Benefits feed export (file generation) | < 30 s | < 90 s | < 180 s | Batch service boundary |
| GL journal file generation | < 60 s | < 120 s | < 300 s | Batch service boundary |
| ACH disbursement file generation | < 60 s | < 120 s | < 300 s | Batch service boundary |

**Baseline comparison (current Oracle HRMS):** The current system has no instrumented SLA baseline. TA analysis (OUTPUT 8) confirmed zero observability tooling. The first delivery milestone must include APM integration to establish a current-state baseline within 30 days of production deployment.

### 1.2 Payroll Processing Time Target

The current Oracle HRMS processes payroll as a synchronous single-threaded PL/SQL loop (`PKG_PAYROLL.calculate_payroll` iterates over all ACTIVE employees serially — confirmed BA analysis). No baseline throughput metric exists.

| Scenario | Target | Notes |
|---|---|---|
| Monthly payroll run — 1 000 employees | ≤ 5 minutes end-to-end | Includes tax calculation, deduction processing, GL entry creation |
| Monthly payroll run — 5 000 employees | ≤ 15 minutes end-to-end | Parallel worker model required |
| Monthly payroll run — 10 000 employees | ≤ 30 minutes end-to-end | Target for 3-year scale horizon |
| Off-cycle final pay (single employee termination) | ≤ 2 minutes | PKG_PAYROLL.calculate_final_pay — does not exist in current system (PP-TERM-03); must be built |
| Payroll recalculation (amendment, single employee) | ≤ 3 minutes | |

The modernised payroll engine must support **parallel employee processing** (minimum 4 workers) to achieve these targets. Sequential processing of the type found in the Oracle legacy is explicitly prohibited for batch runs exceeding 200 employees.

### 1.3 Throughput Requirements

| Metric | Target | Notes |
|---|---|---|
| Concurrent interactive users | 500 (normal) / 1 000 (peak, e.g. open enrolment) | Peak is 2× normal; system must sustain peak for ≥ 4 hours |
| API requests/second (aggregate) | ≥ 1 000 RPS at P95 ≤ 600 ms | During peak load |
| Payroll batch employee records/minute | ≥ 200 employees/minute | Serial Oracle legacy baseline estimated at ≈ 40–60/min based on PL/SQL loop analysis |
| Benefits feed export records/second | ≥ 500 employee-rows/second | Fixed-width 203-char record generation |
| Notification dispatch throughput | ≥ 50 notifications/second | NOTIFICATION_QUEUE consumer |
| Report generation (headcount, compensation, turnover) | ≤ 5 seconds for ≤ 5 000-employee datasets | Pre-aggregated path; direct OLTP path for ad-hoc |

### 1.4 Database Query Performance

All database queries must be reviewed against these targets before production release:

| Query Type | Target Execution Time | Constraint |
|---|---|---|
| Primary key lookup (any table) | < 5 ms | Index-backed; no full scans |
| Single-column indexed search | < 20 ms | |
| Join across ≤ 5 tables, indexed FKs | < 100 ms | |
| Org hierarchy (recursive / CTE, ≤ 10 levels) | < 500 ms | CONNECT BY replaced with CTE |
| Full payroll run SELECT (active employees) | < 2 s | Requires covering index on EMPLOYMENT_STATUS + HIRE_DATE |
| Reporting aggregate (headcount, compensation) | < 3 s on live OLTP | ≤ 500 ms on pre-aggregated RPT_ layer |

---

## 2. Availability and Reliability Requirements

### 2.1 Uptime SLA

| Service Tier | Uptime Target | Maximum Annual Downtime | Maximum Monthly Downtime |
|---|---|---|---|
| Core HR (employee, org chart, authentication) | 99.9% | 8.7 hours | 43.8 minutes |
| Payroll processing | 99.9% | 8.7 hours | 43.8 minutes |
| Leave management | 99.9% | 8.7 hours | 43.8 minutes |
| Reporting (dashboards) | 99.5% | 43.8 hours | 3.65 hours |
| Batch export (benefits, GL, ACH) | 99.5% | 43.8 hours | 3.65 hours |
| Self-service portal | 99.9% | 8.7 hours | 43.8 minutes |
| Administrative / config API | 99.0% | 87.6 hours | 7.3 hours |

Downtime is measured as complete unavailability of the service. **Degraded mode** (e.g. reporting unavailable while core HR is up) does not count against the core HR SLA.

Planned maintenance windows must be:
- Scheduled outside payroll processing windows (no maintenance on the 25th–last day of any month)
- Announced to system administrators ≥ 72 hours in advance
- Not to exceed 2 hours per event for core HR tier
- No more than 2 planned maintenance windows per calendar month

### 2.2 Recovery Time Objective (RTO) and Recovery Point Objective (RPO)

| Failure Scenario | RTO | RPO | Notes |
|---|---|---|---|
| Single application instance failure (pod/container crash) | < 30 seconds | 0 (stateless) | Auto-restart via orchestration platform |
| Database primary failure | < 5 minutes | < 1 minute | Requires hot standby with streaming replication |
| Complete database cluster failure | < 30 minutes | < 5 minutes | Requires automated failover to standby; no manual DBA intervention in RTO window |
| Data centre / availability zone failure | < 60 minutes | < 5 minutes | Multi-AZ deployment required |
| Full disaster recovery (DR site activation) | < 4 hours | < 15 minutes | DR site must be tested quarterly |
| Accidental bulk data deletion (≤ 10 000 rows) | < 2 hours | Point-in-time to 1 minute before event | Requires continuous WAL archiving or equivalent |
| Application deployment rollback | < 15 minutes | 0 | Blue-green or canary deployment required |

**Current system gap:** The Oracle HRMS has no documented RTO/RPO, no CI/CD pipeline, and no automated rollback (confirmed TA OUTPUT 8). Deployment is 100% manual with no rollback mechanism.

### 2.3 Disaster Recovery Requirements

1. **Geographic separation:** The DR site must be physically separated from the primary data centre by ≥ 100 km or in a different cloud availability zone.
2. **Replication:** Database replication to DR must be synchronous for the Payroll and Employee Identity bounded contexts, and asynchronous (lag ≤ 15 minutes) for reporting and notification contexts.
3. **DR testing:** Full DR failover test must be performed **quarterly**. Test results including actual RTO and RPO achieved must be documented and reviewed by the CISO.
4. **Runbook:** A documented, tested DR runbook must exist before go-live. The runbook must be executable by on-call engineers without DBA-level Oracle expertise (current system dependency eliminated).
5. **Backups:**
   - Full database backup: daily, retained for 30 days
   - Incremental/differential backup: every 4 hours
   - Transaction log / WAL archiving: continuous, retained for 7 days
   - Backup restoration test: monthly; results logged
6. **No single point of failure:** The following components must have no SPOF in production: authentication service, payroll calculation service, database, load balancer, file storage (for batch outputs).

### 2.4 Fault Tolerance and Graceful Degradation

| Failure | Required Graceful Behaviour |
|---|---|
| Reporting service unavailable | Core HR, payroll, leave management continue unaffected |
| Notification service unavailable | All HRMS operations continue; notifications queued for later delivery; no blocking |
| Benefits feed export failure | Payroll system continues; export retried automatically; operations alerted after 2 failed retries |
| External integration unavailable (ADP, Oracle Financials, LDAP) | HRMS operations continue; integration queued; alert raised; manual override documented |
| Individual payroll calculation error | Employee skipped with error logged; remaining employees processed; run completes with error summary |

---

## 3. Scalability Requirements

### 3.1 Employee Count Scaling Targets

| Horizon | Employee Count | Notes |
|---|---|---|
| Go-live | 1 000 | Current estimated Acme headcount |
| Year 1 | 2 500 | Organic growth + potential acquisition |
| Year 3 | 10 000 | Strategic growth target |
| Year 5 | 25 000 | Architecture ceiling; re-assessment required beyond this |

The system must meet all performance SLAs (Section 1) at each horizon **without architectural redesign**. Configuration changes (adding workers, scaling compute) must be sufficient.

### 3.2 Data Volume Scaling Targets

| Table / Entity | Go-live Rows | Year-3 Rows | Year-5 Rows |
|---|---|---|---|
| EMPLOYEES (total, including terminated) | 5 000 | 20 000 | 75 000 |
| PAYROLL_DETAILS | 60 000 | 1 200 000 | 9 000 000 |
| AUDIT_LOG | 500 000 | 10 000 000 | 50 000 000 |
| LEAVE_REQUESTS | 20 000 | 400 000 | 2 000 000 |
| PERFORMANCE_REVIEWS | 3 000 | 60 000 | 375 000 |
| NOTIFICATION_QUEUE | 100 000 | 2 000 000 | 10 000 000 |
| USER_SESSIONS (active only) | 1 000 | 5 000 | 25 000 |

Partition strategies must be implemented for PAYROLL_DETAILS, AUDIT_LOG, and NOTIFICATION_QUEUE at go-live (do not defer to Year 3).

### 3.3 Horizontal Scaling Strategy

1. **Stateless application tier:** All application services must be horizontally scalable (stateless). Session state must reside in a distributed cache (Redis or equivalent), not in application memory. The current Oracle Forms session model (TD-75: in-memory session with no background sweep) is explicitly prohibited.

2. **Minimum instance count:**

   | Service | Minimum Production Instances | Auto-scale Trigger |
   |---|---|---|
   | Core HR API | 2 | CPU > 70% or RPS > 600 |
   | Payroll service | 2 | CPU > 60% or queue depth > 10 |
   | Notification service | 2 | Queue depth > 100 |
   | Batch export workers | 1 (on-demand) | Job submitted |
   | Authentication service | 3 | Always; no scale-down below 3 |

3. **Database scaling:** The database tier must support read replicas for reporting and read-heavy workloads. Write operations go to primary only. The RPT_* reporting layer (currently a stub in `PKG_REPORTING.refresh_reporting_tables`) must be replaced with a materialised reporting schema refreshed on a configurable schedule (default: nightly).

4. **Org chart query performance:** The current `CONNECT BY` org hierarchy query degrades at > 500 employees (noted in BA analysis). The modernised system must use a closure table or materialisable hierarchy CTE that supports ≥ 25 000 employees within the P95 target of 800 ms.

5. **Concurrency model:** The payroll engine must use a worker pool model (minimum 4 workers, maximum 16). The current single-threaded PL/SQL loop model is eliminated. Worker count must be configurable without a deployment.

### 3.4 Infrastructure Scaling

- Cloud or virtualised infrastructure with auto-scaling groups
- Compute resources provisioned within 5 minutes of a scale-out trigger
- Scale-in must not begin until a node has been idle for ≥ 10 minutes (prevents thrash during burst)
- Load balancer health checks must detect a dead instance within 10 seconds

---

## 4. Security Requirements

### 4.1 Authentication Standards

| Requirement | Standard / Target | Motivation |
|---|---|---|
| Primary authentication mechanism | OAuth 2.0 with PKCE or SAML 2.0 SSO | Current system has a completely broken auth stub (BR-042: any password accepted); replacement must be real |
| Password hashing algorithm | bcrypt (cost factor ≥ 12) or Argon2id | Current system uses MD5 (DQ-010 — critically weak); upgrade mandatory |
| Minimum password complexity | 12 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special character | Current enforcement is 8 chars, 1 uppercase, 1 digit (BR-041) — strengthened |
| Multi-factor authentication (MFA) | Required for all Grade ≥ 5 users and all system administrators | Not present in current system |
| Session token lifetime | Access token: 15 minutes; Refresh token: 8 hours (configurable) | Current system hard-codes 30-minute session with no background sweep (DQ-027, TD-75) |
| Session invalidation on termination | Synchronous; within 60 seconds of employment status change | Current system relies on next-call check only — up to 30-minute exposure window (BR-TERM-07) |
| Brute-force lockout | Lock after 5 failed attempts; 15-minute lockout; CAPTCHA after 3 | No lockout exists in current system (DQ-023) |
| Re-authentication | Required for payroll approval, bulk salary changes, admin operations | |
| Old password verification | Required on password change | Current `change_password` never verifies old password (DQ-029) |

### 4.2 Authorisation

| Requirement | Details |
|---|---|
| Model | Role-Based Access Control (RBAC) with attribute conditions |
| Roles | EMPLOYEE (self-service), HR_COORDINATOR, HR_MANAGER, PAYROLL_PROCESSOR, PAYROLL_APPROVER, SYSTEM_ADMIN, REPORT_VIEWER, DEPARTMENT_MANAGER |
| Grade-based escalation | Grade ≥ 8 equivalent grants elevated access — must be mapped to explicit roles; no implicit grade integer comparisons in application code |
| Manager scope | Managers can access direct and indirect reports up to 3 levels deep by default; configurable per role |
| Least-privilege database accounts | Application must use dedicated schema users with EXECUTE grants on specific procedures only (not table-level DML access). Resolves TD-81 (self-service portal connecting as schema owner). |
| Permission changes | Require dual-approval (requester + HR Manager); logged to immutable audit trail |

### 4.3 Encryption at Rest

Looking at the PKG_PAYROLL.pkb source: `AMOUNT` values are inserted as raw computed numbers (e.g., `SUM(AMOUNT)` is called directly in SQL aggregations with no decryption wrapper, and `calculate_employee_pay` writes plain `NUMBER` variables into `PAYROLL_DETAILS` with no encryption call). No calls to `DBMS_CRYPTO`, `PKG_SECURITY`, or any encryption package appear anywhere in the payroll detail write path.

Looking at the source content, I can extract the full audit trail requirements from `PKG_AUDIT.pks` and `PKG_AUDIT.pkb`. Let me fill in the empty table.

The source content (PKG_PAYROLL.pkb) contains payroll calculation logic but no bank account decryption procedure, key management code, or caller inventory — the gap describes a procedure that does not yet exist in the codebase. Per the instructions, the snippet is returned unchanged.

The source content (`PKG_LEAVE.pkb`) contains no history table schema, no archival job, no trigger or package procedure for leave balance audit retention, and no auditor query pattern. It only shows `PKG_AUDIT.log_action` calls with no 3-year retention specification.

Per the instructions, the snippet is returned unchanged:

---

The source content covers `PKG_PERFORMANCE` in full — every INSERT and UPDATE path. `CALIBRATED_RATING` does not appear anywhere in the package body, the package spec, or the (unfound) table DDL files. The source confirms it is a dead column (never written to), but provides no information about its owning table structure, calibration workflow, or business rules that would let me fill this encryption-table gap.

Per the instructions, returning the snippet unchanged:

---

The source content provided (PKG_PAYROLL.pkb) contains payroll calculation logic — salary records, pay periods, tax computation — but no NACHA ACH file layout, batch header/control record rules, error handling, reconciliation logic, or any ACH disbursement package. The snippet shown is an encryption requirements table, not an integration table, and the gap described (NACHA ACH disbursement specification) is not present in this snippet or addressable from the source content supplied.

| Data | Encryption Requirement | Notes |
|---|---|---|
| [GAP-FILLED] FTP credentials (host, username, password, port) stored in SYSTEM_PARAMETERS | Must be encrypted at rest — currently stored as cleartext | PKG_INTEGRATION.pks known issues explicitly states: "FTP credentials stored in SYSTEM_PARAMETERS table (cleartext)"; SYSTEM_PARAMETERS DDL not recovered — column structure inferred from PKG_COMMON.get_param('INTEGRATION', p_integration_name \|\| '_STATUS') call pattern in get_integration_status, suggesting rows keyed by PARAM_GROUP / PARAM_NAME / PARAM_VALUE |
| [GAP-FILLED] GL journal flat file (GL_JOURNAL_\<run_id\>_YYYYMMDD.dat) written via UTL_FILE to Oracle directory GL_FEED_OUT | Must be encrypted in transit; file contains payroll cost-centre and GL account codes with debit/credit amounts | generate_gl_journal writes pipe-delimited flat file consumed by Oracle Financials batch import; no encryption or integrity check applied in current implementation |
| [GAP-FILLED] Benefits enrollment flat file (BENEFITS_YYYYMMDD.txt) written via UTL_FILE to Oracle directory BENEFITS_FEED_OUT | Must be encrypted in transit; file contains employee PII (name, DOB, hire date, marital status, gender) and dependent PII (name, relationship, DOB) | export_benefits_feed writes ADP fixed-width format file (vendor-specific); no encryption applied; PII exposure risk during transfer to ADP |
| [GAP-FILLED] Time & attendance import flat file (CSV) read via UTL_FILE from Oracle directory TIME_ATTENDANCE_IN | Must be integrity-verified (checksum or digital signature) before processing | import_time_attendance reads CSV (emp_number, date, hours_regular, hours_overtime); no file integrity or authenticity check in current implementation; parsing logic marked TODO |
| Employee SSN | AES-256-GCM with authenticated encryption | Current AES-256-CBC (no authentication tag) — upgrade to GCM |
| Dependent SSN | AES-256-GCM | Same standard as employee SSN |
| Bank account number | AES-256-GCM | Current: encrypted; decryption procedure missing (PP-BA-01) — decryption must be implemented |
| Bank routing number | AES-256-GCM | Current: stored plaintext (TD-46, PP-BA-02) — encryption required |
| Password hash | bcrypt / Argon2id (not reversible) | Not encrypted — hashed; current MD5 must be replaced |
| Payroll detail records | Database-level TDE or application-level field encryption for net pay, gross pay, deductions | [GAP-FILLED] Current: stored plaintext — PKG_PAYROLL inserts AMOUNT as raw numeric values with no encryption wrapper and aggregates via direct SUM(AMOUNT) SQL with no decryption step; no calls to DBMS_CRYPTO or any encryption package exist in the payroll detail write path — TDE or field-level encryption required |
| Benefits feed file (FTP outbound to ADP) | PGP file encryption before write to `BENEFITS_FEED_OUT`; SFTP with TLS 1.2+ replacing plain FTP | [GAP-FILLED] Current: `PKG_INTEGRATION.export_benefits_feed` writes FIRST_NAME, LAST_NAME, DATE_OF_BIRTH, HIRE_DATE, EMPLOYMENT_STATUS, MARITAL_STATUS, GENDER, dependent name, dependent DOB, and dependent RELATIONSHIP as a cleartext fixed-width flat file via UTL_FILE — confirmed PII and HIPAA-covered PHI transmitted in cleartext (TD-10, SEC-11); no DBMS_CRYPTO call or PGP wrapper exists in the procedure; no TLS on file transfer |
| GL journal feed file (FTP outbound to Oracle Financials) | SFTP with TLS 1.2+ replacing plain FTP; file integrity checksum | [GAP-FILLED] Current: `PKG_INTEGRATION.generate_gl_journal` writes pipe-delimited payroll amounts, GL account codes, and cost-center identifiers to `GL_FEED_OUT` via UTL_FILE — financial data transmitted without in-transit encryption; FTP credentials used for the transfer are stored in plaintext in SYSTEM_PARAMETERS (TD-10) |
| Time & attendance import file (FTP inbound from T&A system) | SFTP with TLS 1.2+ replacing plain FTP; file checksum or PGP signature verification before import | [GAP-FILLED] Current: `PKG_INTEGRATION.import_time_attendance` reads employee time CSV from `TIME_ATTENDANCE_IN` via UTL_FILE with no integrity check — inbound transfer mechanism undocumented beyond SYSTEM_PARAMETERS credential reference; no validation that the file was not tampered with in transit (TD-10); CSV parsing is also marked TODO in the procedure body |
| FTP/integration credentials | Oracle Wallet or dedicated secrets manager (HashiCorp Vault); never in application tables | [GAP-FILLED] Current: FTP credentials for all three integration feeds are stored as cleartext values in the SYSTEM_PARAMETERS table — confirmed by PKG_INTEGRATION.pks header comment: "FTP credentials stored in SYSTEM_PARAMETERS table (cleartext)"; any database user with SELECT privilege on SYSTEM_PARAMETERS can retrieve credentials without any additional authentication (TD-10); migration to SFTP must include re-keying credentials into a secrets manager as a prerequisite |
| All database volumes | AES-256 full-disk or TDE encryption | |
| Backup files | AES-256 encryption; keys stored separately from backup data | |

---

The NACHA ACH gap (file layout, batch header/control records, error handling, reconciliation, owning package) requires source content from an ACH disbursement package — none was present in the PKG_PAYROLL.pkb extract provided.

| Scope | Requirement |
|---|---|
| [GAP-FILLED] All DML operations on system tables | Every INSERT, UPDATE, and DELETE must be logged via PKG_AUDIT.log_action; logging executes under PRAGMA AUTONOMOUS_TRANSACTION so an audit failure can never abort the originating business transaction — the exception handler issues ROLLBACK and swallows the error silently |
| [GAP-FILLED] Who/What/When capture per audit entry | Each row written to AUDIT_LOG must record: TABLE_NAME (which table was modified), RECORD_ID (primary key of the affected row), ACTION_TYPE (INSERT / UPDATE / DELETE), OLD_VALUES (CLOB of pre-change data), NEW_VALUES (CLOB of post-change data), CHANGED_BY (database USER at time of call), CHANGED_DATE (SYSDATE), IP_ADDRESS (SYS_CONTEXT('USERENV','IP_ADDRESS')), SESSION_ID (SYS_CONTEXT('USERENV','SESSIONID')) |
| [GAP-FILLED] Trigger mechanism | PKG_AUDIT.log_action must be invoked by every package that performs DML on auditable tables and by any database-level DML trigger; no package may write to a tracked table without a corresponding log_action call in the same code path |
| [GAP-FILLED] Centralized audit storage | All audit records are stored in a single AUDIT_LOG table; primary key is generated by SEQ_AUDIT sequence; no per-table shadow tables are used |
| [GAP-FILLED] Retention period | Default retention is 365 days; purge_old_records(p_days_to_keep IN NUMBER DEFAULT 365) deletes all AUDIT_LOG rows where CHANGED_DATE < SYSDATE − p_days_to_keep; purge execution must be restricted to authorized database users only |
| [GAP-FILLED] Change history query access | get_change_history(p_table_name, p_record_id, p_from_date, p_to_date) exposes a SYS_REFCURSOR returning AUDIT_ID, TABLE_NAME, RECORD_ID, ACTION_TYPE, OLD_VALUES, NEW_VALUES, CHANGED_BY, CHANGED_DATE, IP_ADDRESS ordered by CHANGED_DATE DESC; used for compliance review and incident investigation; date range parameters are optional (NULL = unbounded) |

| Scope | Requirement |
|---|---|
| [GAP-FILLED] All DML operations (INSERT, UPDATE, DELETE) on any audited table | Every data-modifying operation must be logged via `PKG_AUDIT.log_action`; the audit write executes as an autonomous transaction (`PRAGMA AUTONOMOUS_TRANSACTION`) and must never cause the calling transaction to fail — exceptions are silently suppressed to protect business operations |
| [GAP-FILLED] Audit record content — WHO | Each audit record must capture the Oracle session user (`CHANGED_BY` = `USER`), client IP address (`IP_ADDRESS` = `SYS_CONTEXT('USERENV','IP_ADDRESS')`), and database session identifier (`SESSION_ID` = `SYS_CONTEXT('USERENV','SESSIONID')`) |
| [GAP-FILLED] Audit record content — WHAT | Each audit record must capture: `TABLE_NAME` (the audited entity), `RECORD_ID` (primary key of the changed row), `ACTION_TYPE` (INSERT / UPDATE / DELETE), `OLD_VALUES` (CLOB — full pre-change state), and `NEW_VALUES` (CLOB — full post-change state) |
| [GAP-FILLED] Audit record content — WHEN | Each audit record must capture `CHANGED_DATE` stamped with `SYSDATE` at the moment the DML operation is logged |
| [GAP-FILLED] Employee records | All changes to employee master data must be audited; trigger `trg_employees_audit` is the designated mechanism; full before/after values must be captured in `OLD_VALUES` / `NEW_VALUES` |
| [GAP-FILLED] Payroll records | All changes to payroll data must be audited; trigger `trg_payroll_audit` is the designated mechanism; full before/after values must be captured in `OLD_VALUES` / `NEW_VALUES` |
| [GAP-FILLED] Retention period | Default retention is 365 days; records older than the configured threshold are purged via `PKG_AUDIT.purge_old_records(p_days_to_keep)`; the retention window is configurable at purge execution time but must not be set below 365 days without explicit compliance approval |
| [GAP-FILLED] Change history retrieval | Full change history for any audited record must be queryable by `TABLE_NAME`, `RECORD_ID`, and optional date range (`p_from_date` / `p_to_date`) via `PKG_AUDIT.get_change_history`; results must be returned ordered by `CHANGED_DATE DESC` |
| [GAP-FILLED] Audit log integrity | Audit log rows must be committed independently of the calling transaction; no application code or trigger may delete or update `AUDIT_LOG` rows outside of the authorised `purge_old_records` procedure |
| Encryption key storage | Hardware Security Module (HSM) or cloud KMS | Current system embeds key as hardcoded string `HR$ystem_3ncrypt10n_K3y_2024!!` (DQ-001, SEC-03) — immediately prohibited |
| Key rotation | Annual minimum; rotation must not require downtime | Current system has no key rotation mechanism |

### 4.4 Encryption in Transit

| Requirement | Target |
|---|---|
| All API traffic | TLS 1.3 minimum; TLS 1.2 acceptable for legacy integration partners only, with a documented sunset date |
| Internal service-to-service traffic | Mutual TLS (mTLS) |
| Database connections | TLS-encrypted connections; plaintext database connections prohibited |
| File transfer (benefits feed, GL feed, ACH) | SFTP with key authentication or AS2; FTP cleartext strictly prohibited. Resolves TD-10 (cleartext FTP credentials). |
| Certificate validity | Certificates must be rotated ≥ 30 days before expiry; automated rotation preferred |

### 4.5 Audit Logging Requirements

Every security-relevant event and all PII-touching operations must produce an immutable, structured audit log entry. The current `AUDIT_LOG` table mixes ERROR, INFO, and DML events with a single purge policy (TD-37) — this must be replaced with segregated, retention-controlled audit streams.

| Event Category | Fields Required | Retention |
|---|---|---|
| Authentication (success and failure) | timestamp, user_id, source_ip, user_agent, outcome, failure_reason | 2 years |
| Password change | timestamp, user_id, changed_by, source_ip | 2 years |
| Employee record create / update / delete | timestamp, actor_user_id, target_employee_id, fields_changed (before/after for PII fields), source_ip | 7 years |
| Payroll run (create, calculate, approve, generate GL) | timestamp, actor_user_id, run_id, action, total_gross, total_net | 7 years (SOX) |
| Salary change | timestamp, actor_user_id, employee_id, old_salary, new_salary, approver_user_id | 7 years (SOX) |
| PII access (SSN decrypt, bank account decrypt) | timestamp, actor_user_id, target_employee_id, field_accessed, justification_code | 3 years (GDPR) |
| Role / permission change | timestamp, granting_user_id, target_user_id, role_added, role_removed | 2 years |
| Leave approval / rejection | timestamp, actor_user_id, leave_request_id, decision | 3 years |
| Export file generation (benefits feed, GL, ACH) | timestamp, actor_user_id, file_name, record_count, destination | 7 years |
| System configuration change | timestamp, actor_user_id, parameter_key, old_value, new_value | 2 years |
| Failed access attempts (repeated) | timestamp, source_ip, target_resource, attempt_count | 1 year |
| Session creation and termination | timestamp, session_id, user_id, source_ip, termination_reason | 1 year |

Audit log properties:
- **Immutable:** Audit log rows may never be updated or deleted by application code. Retention policy purges are executed only by a scheduled privileged process with a separate audit trail.
- **Tamper-evident:** Audit log rows must include a hash chain or be written to append-only storage.
- **Structured format:** All audit events must use a consistent JSON schema. Free-text log lines (current PKG_COMMON.log_info pattern) are not acceptable for security audit events.
- **Searchable within 10 seconds:** Any audit query covering a 90-day window must return within 10 seconds.

### 4.6 PII Data Handling

Derived from the DA PII inventory (pii-inventory.json). The following fields are classified as PII and are subject to the handling standards below.

| Classification | Fields | Handling Standard |
|---|---|---|
| High sensitivity (encrypt + access control + decrypt audit) | SSN (employees and dependents), ACCOUNT_NUMBER_ENC, ROUTING_NUMBER, PASSWORD_HASH, DATE_OF_BIRTH | AES-256-GCM at rest; TLS in transit; access logged per Section 4.5; never included in logs |
| Moderate sensitivity (access control + transit encryption) | FIRST_NAME, LAST_NAME, EMAIL, PHONE, ADDRESS fields, EMERGENCY_CONTACT fields, MARITAL_STATUS, TAX_FILING_STATUS, GENDER | Not stored in plaintext log lines; masked in non-production environments |
| Financial sensitivity (SOX scope) | BASE_SALARY, GROSS_PAY, NET_PAY, DEDUCTIONS, BANK details | Access restricted to Payroll Processor, Payroll Approver, and System Admin roles; RPT_NEW_HIRES report currently co-locates salary + name — access must be gated (AA_Quality_Review finding) |

PII-specific rules:
1. **Non-production data masking:** All non-production environments (dev, test, staging) must use masked or synthetic PII. Real employee SSNs, salary data, or bank details must never appear in non-production.
2. **Data minimisation:** Any new integration or export must include a data minimisation review before approval. Only fields required for the receiving system's stated purpose may be included.
3. **BENEFITS_ENROLLED filter:** The ADP benefits feed must filter on `BENEFITS_ENROLLED = 'Y'` before including dependent records. Current system exports all active dependents regardless of enrolment status (G-1 from AA cross-validation).

---

## 5. Compliance Requirements

### 5.1 GDPR / Data Privacy

| Requirement | Implementation Target |
|---|---|
| Right to access | Employees must be able to request a full export of their personal data; export generated within 5 business days; machine-readable format (JSON or CSV) |
| Right to rectification | Incorrect PII correctable via HR_COORDINATOR role; correction logged with before/after values |
| Right to erasure (where applicable) | Terminated employees: soft-delete retained for 7 years (statutory minimum for payroll records); after 7 years, PII fields anonymised rather than deleted; employment fact retained for reporting |
| Consent tracking | Where PII is processed beyond employment contract necessity, consent records must be maintained with timestamp and withdrawal path |
| Data breach notification | System must produce a breach impact report (which employees, which fields, time window) within 4 hours of detection; supports 72-hour GDPR notification requirement |
| Data residency | Employee data stored in the jurisdiction of employment; cross-border data transfer must comply with applicable adequacy decision or SCCs |
| Privacy by design | New features requiring PII collection must complete a Privacy Impact Assessment (PIA) before development |

### 5.2 SOX Compliance for Payroll

The payroll process is in scope for Sarbanes-Oxley Section 302/404 due to its direct impact on financial statements through the GL feed.

| Control | Requirement |
|---|---|
| Segregation of duties | Payroll calculation and payroll approval must be performed by different users; system must enforce this; same user cannot hold PAYROLL_PROCESSOR and PAYROLL_APPROVER roles simultaneously |
| Approval workflow | Every payroll run must require explicit approval (current system has an APPROVED_BY field but no enforcement gate validated in analysis) |
| Change control | Any change to tax tables, deduction codes, or pay element configuration requires dual approval and is fully audit logged |
| GL feed integrity | GL journal files must include record counts, control totals, and a feed acknowledgement mechanism. Current system has no GL_FEED_STATUS field on PAYROLL_RUNS (TD-80) — must be added |
| Payroll data retention | Payroll records retained for minimum 7 years |
| Access review | Quarterly review of all users with Payroll Processor or Payroll Approver role; results documented and presented to Finance leadership |
| Reconciliation | System must produce a payroll reconciliation report showing gross-to-net waterfall; must be auditor-accessible |

### 5.3 NACHA / ACH Compliance

The current system has EMPLOYEE_BANK_ACCOUNTS designed for ACH disbursement but the table is never read during payroll (PP-BA-01 — critical gap). The modernised system must implement compliant ACH processing.

| Requirement | Target |
|---|---|
| ACH prenote | New or reactivated bank accounts must trigger a zero-dollar prenote entry; live disbursements must not occur until prenote settles (3 banking days); PRENOTE_SENT and PRENOTE_DATE columns must be written by the implementation |
| NACHA file format | Standard ACH file with file header, company batch header, detail records, batch control, and file control |
| Routing number validation | Routing numbers validated against ABA RTN check digit algorithm on entry |
| Deposit total validation | Sum of all deposit allocations for an employee must equal 100% of net pay; REMAINDER account type used for residual |
| Encryption | Routing numbers encrypted (resolves TD-46, PP-BA-02) |
| Dual-custody for ACH file | ACH file transmission requires approval from a user holding PAYROLL_APPROVER role; transmission logged |

### 5.4 FMLA / Employment Law Compliance

| Requirement | Notes |
|---|---|
| FMLA documentation | FMLA leave type must require supporting documentation (REQUIRES_DOCUMENT = 'Y'). Current seed data sets REQUIRES_DOCUMENT = 'N' (TD-71) — corrected in modernised system. |
| COBRA notification | Employee termination must trigger a COBRA-eligible event record with notification deadline (14 calendar days). Current system has a TODO comment with no implementation (PP-TERM-01 — critical). |
| Leave balance audit | Leave balance accrual and consumption must be fully auditable; balance history retained for 3 years. |

### 5.5 Audit Trail Requirements

| Scope | Requirement |
|---|---|
| Complete change history | Every INSERT, UPDATE, and DELETE on all HRMS tables must be captured with before/after values, actor, and timestamp |
| Non-repudiation | Audit records must be cryptographically signed or stored in append-only storage to prevent tampering |
| Availability for audit | Any audit query for a defined employee and time window must be executable without DBA involvement; a self-service audit interface for HR Managers and Compliance Officers is required |
| External audit support | System must support export of audit records in a format acceptable to external auditors (CSV with column headers, JSON); export within 24 hours of request |
| Retention by category | See Section 4.5 for per-category retention periods |

---

## 6. Maintainability Requirements

### 6.1 Code Quality and Test Coverage

| Metric | Target | Notes |
|---|---|---|
| Unit test code coverage (line coverage) | ≥ 80% overall; ≥ 90% for payroll calculation, tax computation, authentication | Current system: 0% (no tests found — TA OUTPUT 8) |
| Integration test coverage | 100% of public API endpoints covered by at least one integration test | |
| End-to-end test coverage | All critical user journeys (hire, terminate, run payroll, submit leave, performance review cycle) must have automated E2E tests | |
| Test execution time (CI gate) | Unit tests: ≤ 5 minutes; Integration tests: ≤ 20 minutes; Full suite: ≤ 60 minutes | |
| Static analysis | Zero critical findings from SAST tool (SonarQube or equivalent) in main branch. Resolves TA OUTPUT 8 finding (no SAST exists). | |
| Secret scanning | Zero committed secrets in repository. Hard-coded key TD-01 and FTP credentials TD-10 must be revoked before go-live. Secret scanner runs on every commit. | |
| Dependency vulnerability scan | Zero High/Critical CVEs in production dependencies; automated weekly scan | |
| Code complexity | Cyclomatic complexity ≤ 15 per function; functions > 15 flagged in PR review | |
| Linting | All languages: zero linting errors in main branch | |

### 6.2 CI/CD Pipeline Requirements

The current system has no CI/CD pipeline (TA OUTPUT 8 — 0 of 14 capabilities present). The following capabilities are mandatory before go-live.

| Capability | Requirement |
|---|---|
| Automated build | Every commit to any branch triggers a build within 2 minutes |
| Automated tests | Unit and integration tests run on every PR; merge blocked if tests fail |
| Code coverage gate | PR merge blocked if coverage drops below thresholds (Section 6.1) |
| SAST | Static security scan on every PR; High/Critical findings block merge |
| Secret scan | Runs on every commit; any secret detection blocks merge and alerts security team |
| Dependency scan | Weekly scheduled scan; results reported to engineering lead |
| Automated deployment to staging | Successful main branch build triggers automatic staging deployment |
| Manual approval gate for production | Production deployment requires explicit approval from two individuals: Engineering Lead and Release Manager |
| Deployment rollback | One-click rollback to previous production version within 15 minutes |
| Post-deploy health check | Automated smoke tests run against production within 5 minutes of deployment; alert if they fail |

### 6.3 Deployment Frequency Targets

| Metric | Target | Notes |
|---|---|---|
| Deployment frequency (normal operations) | ≥ 1 deployment per week to staging; production as needed after approval | |
| Change failure rate | ≤ 5% of production deployments require rollback | |
| Lead time (commit to production) | ≤ 5 business days | From merge to main to production deployment |
| Mean Time to Recover (MTTR) | ≤ 1 hour for P1 incidents; ≤ 4 hours for P2 | Measured from incident detection to service restoration |
| Mean Time Between Failures (MTBF) | ≥ 30 days for P1 incidents | |

### 6.4 Observability Requirements

The current system has zero structured logging, zero metrics collection, and zero tracing (TA OUTPUT 8). The following must be present at go-live.

| Pillar | Requirement |
|---|---|
| Structured logging | All application logs in JSON format with: timestamp, level, service, trace_id, span_id, user_id (masked), message. Free-text log lines prohibited in production. |
| Metrics | RED metrics (Rate, Errors, Duration) for every API endpoint; business metrics (payroll runs processed, employees hired/terminated, leaves submitted) |
| Distributed tracing | Every API request must carry a trace ID; traces available in APM tool (Jaeger, Datadog, or equivalent) |
| Alerting | PagerDuty or equivalent; P1 alert response target < 5 minutes; on-call rotation documented |
| Dashboards | Operational dashboard (SLA compliance, error rates, latency percentiles) and business dashboard (payroll status, headcount, leave utilisation) |
| Log retention | Application logs: 90 days hot, 1 year cold archive; Security audit logs: per Section 4.5 |

### 6.5 Documentation Requirements

| Artefact | Required | Owner |
|---|---|---|
| API documentation | OpenAPI 3.0 specification for all endpoints; auto-generated from code annotations | Engineering |
| Architecture decision records (ADRs) | One ADR per significant architectural decision; stored in repository | Solution Architect |
| Runbook for each scheduled batch job | Steps to monitor, diagnose, and recover each batch operation | DevOps / Engineering |
| DR runbook | See Section 2.3 | DevOps |
| Data dictionary | Maintained for all production tables; aligned with schema | Data Engineering |
| On-call escalation playbook | Who to call, in what order, for each alert type | DevOps / Engineering |

### 6.6 Dependency Management

| Requirement | Target |
|---|---|
| Open-source licence compliance | All dependencies must have an approved licence (MIT, Apache 2.0, BSD); GPL and AGPL require legal review before inclusion |
| Dependency age | No production dependency more than 2 major versions behind latest stable |
| Framework upgrades | Major framework versions reviewed within 6 months of release |
| Oracle Forms elimination | Zero Oracle Forms components in the modernised system |

---

## 7. Usability Requirements

### 7.1 General Usability Principles

1. **Accessibility:** The UI must conform to WCAG 2.1 Level AA. This applies to the self-service portal, the HR administration interface, and any reporting dashboards.
2. **Browser support:** Latest 2 versions of Chrome, Firefox, Edge, and Safari. No Internet Explorer support.
3. **Mobile responsiveness:** The self-service portal (leave requests, payslip view, personal detail updates, performance self-assessment) must be usable on mobile devices (screen widths ≥ 375px) without a native mobile app.
4. **No Oracle Forms client dependency:** The current requirement to have Oracle Forms Builder 12c installed to compile the application (TD-76) must be eliminated. The modernised system requires only a supported web browser.

### 7.2 Task Completion Targets

| User Task | Target Completion Time (average trained user) | Error Rate Target |
|---|---|---|
| Submit a leave request | ≤ 3 minutes | < 2% |
| View payslip | ≤ 1 minute | < 1% |
| Update personal contact details | ≤ 5 minutes | < 2% |
| Complete self-assessment (performance) | ≤ 30 minutes (total; UI navigation only) | < 2% |
| Hire a new employee (HR Coordinator) | ≤ 10 minutes (data entry; excludes external approvals) | < 3% |
| Terminate an employee (all steps) | ≤ 15 minutes | < 3% |
| Run monthly payroll (Payroll Processor) | ≤ 20 minutes (initiation and monitoring; excludes processing time) | < 1% |

### 7.3 Error Messages and Feedback

1. All form validation errors must identify the specific field and the reason for failure. Generic "An error occurred" messages are prohibited where a specific cause is identifiable.
2. Long-running operations (payroll run, export generation) must display progress indicators with estimated completion time.
3. All destructive actions (terminate employee, delete record, approve payroll run) must require explicit confirmation showing the action's scope and consequences.
4. Session expiry must be warned 2 minutes before the session expires, with an option to extend. Current system has no warning (session drops silently — TD-75 equivalent).

### 7.4 Onboarding

1. New HR Coordinator users must be able to complete basic tasks (hire, leave approval, payslip view) after a maximum of 4 hours of guided onboarding.
2. In-application contextual help must be available for all non-trivial workflows.

---

## 8. Interoperability Requirements

### 8.1 Integration Standards

| Integration | Protocol | Format | Authentication | Notes |
|---|---|---|---|---|
| ADP benefits feed | SFTP | Fixed-width flat file (203-char records); format version header required | SSH key authentication | Current system has no format version or record count trailer (TD-73) — both required in modernised system |
| Oracle Financials GL | SFTP or Oracle DB link | Pipe-delimited with Journal Source and Journal Category fields (TD-79) | Service account with least-privilege | GL_FEED_SENT_DATE and GL_FEED_FILE_NAME must be written to PAYROLL_RUNS on success (TD-80) |
| NACHA ACH disbursement | SFTP to bank or API | Standard NACHA CCD/PPD format | SSH key or mutual TLS | New implementation required (PP-BA-01) |
| LDAP / Active Directory | LDAP over TLS or SCIM 2.0 | — | Service account with read-only bind | `PKG_INTEGRATION.sync_org_structure` is a placeholder with no implementation (BR-ORG-01) — must be fully implemented |
| Time and attendance import | SFTP or API | CSV with header validation; not UTL_FILE | Service account | Current stub `import_time_attendance` is non-functional (DQ-031) — full redesign required |
| Notification email delivery | SMTP/TLS or provider API (SendGrid, SES) | HTML + plain text | API key | Current SMS channel referenced but not implemented; descoped unless business requirement confirmed |
| Self-service portal | REST API | JSON / OpenAPI 3.0 | OAuth 2.0 bearer token | Portal must use a dedicated least-privilege DB user (TD-81) |
| Reporting / BI tools | REST API or direct read-only DB user on RPT_ schema | — | OAuth 2.0 or read-only service account | RPT_* tables currently unpopulated (BR-043) — refresh job must be implemented |

### 8.2 API Design Standards

1. All new APIs must conform to the OpenAPI 3.0 specification.
2. RESTful resource naming: plural nouns, hierarchical paths (e.g. `/employees/{id}/leave-requests`).
3. Versioning: URL-path versioning (`/v1/`, `/v2/`) for all public and integration APIs.
4. Pagination: All list endpoints must support cursor-based or offset+limit pagination. Default page size: 50. Maximum page size: 500.
5. Error format: RFC 7807 Problem Details for HTTP APIs (`application/problem+json`).
6. Idempotency: All write operations must support idempotency keys. Payroll calculation, file exports, and notification dispatch must be idempotent to support safe retry.
7. Deprecation: APIs deprecated with ≥ 6 months notice; deprecated endpoints must return a `Sunset` header.

### 8.3 Data Format Interoperability

1. All dates exchanged in APIs use ISO 8601 format (`YYYY-MM-DD`).
2. All currency values use `NUMBER(15,2)` precision; currency code transmitted as ISO 4217 (e.g. "USD").
3. All timestamps include timezone offset (UTC preferred for internal systems).
4. Character encoding: UTF-8 throughout. Oracle `NVARCHAR2` or equivalent for fields that may contain non-ASCII characters (names, addresses).

### 8.4 Future Interoperability Readiness

1. The architecture must support an event-driven integration model. Core state changes (employee hired, employee terminated, payroll run approved, leave approved) must produce domain events to a message broker (Kafka, SQS, or equivalent) for downstream consumption without polling.
2. The `PKG_INTEGRATION.sync_org_structure` replacement must support delta-sync (changed records only) as well as full-sync modes (BR-ORG-04, BR-ORG-05).

---

## 9. NFR Acceptance Criteria

The following table defines testable acceptance criteria for each NFR category. All criteria must be verified before production go-live sign-off.

### 9.1 Performance Acceptance Criteria

| ID | Acceptance Test | Pass Condition | Test Method |
|---|---|---|---|
| PERF-AC-01 | Load test: 500 concurrent users performing mixed read/write operations (60% reads, 40% writes) for 30 minutes | P95 response time ≤ targets in Section 1.1 for all endpoint categories; error rate < 0.1% | k6, JMeter, or Gatling load test with production-scale data |
| PERF-AC-02 | Payroll run: process 1 000 employees with full tax and deduction calculation | Completes in ≤ 5 minutes; all employee records processed; no calculation errors | Automated payroll run test with verified expected outputs |
| PERF-AC-03 | Payroll run: process 5 000 employees | Completes in ≤ 15 minutes | Same as PERF-AC-02 with 5k dataset |
| PERF-AC-04 | Off-cycle final pay: single employee with active pay period | Completes in ≤ 2 minutes; correct proration and PTO payout | Unit + integration test for `calculate_final_pay` |
| PERF-AC-05 | Org chart query: retrieve hierarchy for 10 000-employee org to 5 levels | P95 ≤ 800 ms | Load test with hierarchy data |
| PERF-AC-06 | Benefits feed export: 5 000 employees | File generated in ≤ 90 seconds; record count in trailer matches database count | Integration test against staging |
| PERF-AC-07 | Database query: primary key lookup on any table with 1M rows | ≤ 5 ms execution time (measured via EXPLAIN ANALYZE) | Query plan review + execution test |

### 9.2 Availability Acceptance Criteria

| ID | Acceptance Test | Pass Condition |
|---|---|---|
| AVAIL-AC-01 | Simulate application instance crash (kill pod/container) | New instance starts and is healthy within 30 seconds; no requests lost after 30 seconds; measured via continuous probe |
| AVAIL-AC-02 | Simulate database primary failure (kill primary) | Automatic failover completes; service resumes within 5 minutes; data loss < 1 minute of transactions |
| AVAIL-AC-03 | Simulate availability zone failure | Service continues from surviving AZ within 60 minutes; RPO < 5 minutes |
| AVAIL-AC-04 | Execute full DR test (activate DR site) | RTO ≤ 4 hours; RPO ≤ 15 minutes; documented results |
| AVAIL-AC-05 | Deploy application update and immediately rollback | Rollback to previous version completes within 15 minutes; no data corruption |
| AVAIL-AC-06 | Reporting service killed during active payroll run | Payroll run continues to completion; reporting service automatically restarts; payroll data integrity confirmed |
| AVAIL-AC-07 | Notification service killed during payroll run | Payroll run continues; notifications queued; delivered within 10 minutes of notification service recovery |

### 9.3 Scalability Acceptance Criteria

| ID | Acceptance Test | Pass Condition |
|---|---|---|
| SCALE-AC-01 | Load test with 1 000 concurrent users | All SLAs met; auto-scale adds instances within 5 minutes of CPU > 70% |
| SCALE-AC-02 | Scale-in test: reduce load to baseline | Instances scale down after 10 minutes of low load; no disruption to active users |
| SCALE-AC-03 | Payroll run with parallel workers: 4 workers vs 8 workers | 8-worker run completes in ≤ 60% of 4-worker run time (linear scaling validation) |
| SCALE-AC-04 | Data volume test: execute all queries against 10M-row PAYROLL_DETAILS table (partitioned) | No query exceeds its P95 SLA target; partition pruning confirmed in query plans |

### 9.4 Security Acceptance Criteria

| ID | Acceptance Test | Pass Condition |
|---|---|---|
| SEC-AC-01 | Attempt authentication with correct username and any password (tests BR-042 fix) | Authentication rejected; failed attempt logged |
| SEC-AC-02 | Attempt 6 consecutive failed logins | Account locked after 5th failure; 6th attempt returns locked error; lock persists for 15 minutes |
| SEC-AC-03 | Attempt to change password without providing current password (tests DQ-029 fix) | Request rejected with appropriate error |
| SEC-AC-04 | Terminate employee; attempt to use active session within 60 seconds | Session invalidated; subsequent API calls return 401 |
| SEC-AC-05 | Submit a secret (AWS key pattern) in a commit | Secret scanner blocks merge; security alert raised |
| SEC-AC-06 | Verify hard-coded encryption key TD-01 is not present in any source file or config | `grep -r 'HR\$ystem_3ncrypt10n_K3y_2024!!'` returns zero results |
| SEC-AC-07 | Attempt to access another employee's payslip as a Grade 3 employee | 403 Forbidden returned; attempt logged in audit trail |
| SEC-AC-08 | Inspect database connection string used by self-service portal | Connection uses dedicated HRMS_PORTAL_APP user with EXECUTE-only grants; no direct table access |
| SEC-AC-09 | Verify routing numbers are encrypted at rest | Direct SELECT on EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER returns ciphertext; plaintext only available via authorised decrypt procedure |
| SEC-AC-10 | SAST tool scan of main branch | Zero Critical, zero High findings |
| SEC-AC-11 | TLS version check on all endpoints | TLS 1.0 and TLS 1.1 connections rejected; TLS 1.3 supported |
| SEC-AC-12 | Access audit log for employee ID 42 over last 90 days | Results returned within 10 seconds; all expected events present |

### 9.5 Compliance Acceptance Criteria

| ID | Acceptance Test | Pass Condition |
|---|---|---|
| COMP-AC-01 | Run payroll as PAYROLL_PROCESSOR user; attempt to approve own run | System rejects approval by same user who initiated run |
| COMP-AC-02 | Create FMLA leave request without attaching documentation | System rejects submission with "documentation required" error |
| COMP-AC-03 | Terminate employee; verify COBRA event record created | COBRA_EVENTS table has record with 14-day notification deadline; event is queryable by HR Compliance |
| COMP-AC-04 | Create new bank account; verify prenote flag and process | PRENOTE_SENT = 'N' on creation; prenote record sent before first disbursement; PRENOTE_SENT updated to 'Y' with date |
| COMP-AC-05 | Employee PII data export request | Complete export of employee's own data generated in ≤ 5 business days in JSON/CSV format |
| COMP-AC-06 | GL feed generated for payroll run | PAYROLL_RUNS.GL_FEED_SENT_DATE populated; file contains Journal Source, Journal Category, and control total |
| COMP-AC-07 | Verify audit records for a payroll approval exist and are immutable | Audit record for payroll approval exists with all required fields; attempt to UPDATE the record fails |

### 9.6 Maintainability Acceptance Criteria

| ID | Acceptance Test | Pass Condition |
|---|---|---|
| MAINT-AC-01 | Execute full CI pipeline from commit to staging deploy | Pipeline completes in ≤ 60 minutes; all stages green |
| MAINT-AC-02 | Run unit test suite in isolation | Executes in ≤ 5 minutes; coverage ≥ 80% overall, ≥ 90% for payroll and auth |
| MAINT-AC-03 | Simulate P1 incident: database unreachable | Alert fires within 5 minutes of failure; incident channel notified; runbook link included in alert |
| MAINT-AC-04 | Production deployment with immediate rollback | Rollback to prior version completes within 15 minutes; no data loss |
| MAINT-AC-05 | Review APM dashboard during load test | RED metrics for all endpoints visible; latency percentiles (P50, P95, P99) available per endpoint |
| MAINT-AC-06 | Non-production environment PII check | `grep -r 'SSN\|social_security'` on non-production data returns no real values; all masked or synthetic |

### 9.7 Interoperability Acceptance Criteria

| ID | Acceptance Test | Pass Condition |
|---|---|---|
| INTER-AC-01 | Generate ADP benefits feed and validate format | File has format version header; trailer record with employee count; every record exactly 203 characters; no truncation |
| INTER-AC-02 | Sync org structure from LDAP | Department hierarchy, reporting lines, and job titles updated in HRMS; delta-sync imports only changed records; no false-success log on empty sync |
| INTER-AC-03 | Import time and attendance CSV | Records imported to TIME_ATTENDANCE_RECORDS; import errors per line logged individually; batch continues; final count logged accurately |
| INTER-AC-04 | Call deprecated API endpoint | Response includes `Sunset` header with deprecation date; functional response still returned |
| INTER-AC-05 | RPT_* tables after nightly refresh job | All 7 RPT_ tables contain data matching live OLTP queries; refresh job logs actual record count (not the current stub log) |

---

## 10. NFR Priority and Dependency Summary

| Priority | NFR Category | Rationale |
|---|---|---|
| P0 — Blocker for go-live | Security (4.1 authentication fix, 4.3 key management) | Current system has broken auth (BR-042) and hardcoded encryption key (TD-01) — must be fixed before any production use |
| P0 — Blocker for go-live | SOX compliance (5.2) | Payroll system without segregation of duties cannot go live in a SOX-audited environment |
| P0 — Blocker for go-live | NACHA ACH implementation (5.3) | Direct deposit is completely non-functional (PP-BA-01) |
| P0 — Blocker for go-live | COBRA notification (5.4) | Every termination without COBRA notification creates a federal compliance violation |
| P1 — Required before first payroll run | Payroll performance (1.2), Parallel processing (3.3) | Payroll run must complete within window |
| P1 — Required before first payroll run | GL feed integrity (5.2), ACH disbursement | Financial controls |
| P2 — Required within 90 days | Full CI/CD pipeline (6.2) | Zero pipeline is the root cause of current system's quality debt |
| P2 — Required within 90 days | Observability (6.4) | Cannot manage SLAs without metrics |
| P3 — Required within 180 days | LDAP sync implementation | BR-ORG-01 placeholder must be replaced |
| P3 — Required within 180 days | Performance calibration workflow | CALIBRATED_RATING column remains a dead column until implemented |

---

## Appendix A: NFR Traceability Matrix

| NFR Section | Source Finding | Source Document |
|---|---|---|
| 4.1 Authentication | BR-042 (auth never verifies password) | DA_Data_Reviewer / hidden-business-rules.json |
| 4.1 Password hashing | DQ-010 (MD5 hashing) | DA_Data_Reviewer / data-quality-report.md |
| 4.1 Session management | DQ-027, TD-75 (30-min session, no sweep) | DA, TA |
| 4.1 Brute-force lockout | DQ-023 (no lockout) | DA_Data_Reviewer |
| 4.1 Old password verification | DQ-029 | DA_Data_Reviewer |
| 4.3 Encryption key management | DQ-001, SEC-03 (hardcoded key) | DA_Data_Reviewer |
| 4.3 Routing number encryption | TD-46, PP-BA-02 | TA_Deep_Analyst, BA_Deep_Analyst |
| 4.3 Bank account decryption | PP-BA-01, BR-BA-12 | BA_Deep_Analyst |
| 4.5 Audit log segregation | TD-37 | TA_Deep_Analyst |
| 4.6 BENEFITS_ENROLLED filter | G-1 (AA cross-validation) | AA_Quality_Review |
| 5.2 Segregation of duties | SOX analysis | BA_Deep_Analyst |
| 5.2 GL feed status | TD-80 | TA_Deep_Analyst |
| 5.3 NACHA prenote | PP-BA-03, BR-BA-05 | BA_Deep_Analyst |
| 5.4 FMLA documentation | TD-71 | TA_Deep_Analyst |
| 5.4 COBRA notification | PP-TERM-01 | BA_Deep_Analyst |
| 6.2 CI/CD pipeline | TA OUTPUT 8 (0 of 14 capabilities) | TA_Deep_Analyst |
| 6.4 Observability | TA OUTPUT 8 (zero observability) | TA_Deep_Analyst |
| 8.1 ADP feed format version | TD-73 | TA_Deep_Analyst |
| 8.1 LDAP sync | BR-ORG-01 (placeholder) | BA_Deep_Analyst cross-validation |
| 8.1 Time/attendance import | DQ-031, BR-046 | DA_Data_Reviewer |
| 8.1 FTP → SFTP | TD-10 (cleartext FTP) | TA_Deep_Analyst |
| 8.1 Portal DB user | TD-81 | TA_Deep_Analyst |
| 8.4 Event-driven readiness | Integration architecture gap | TA_Deep_Analyst |

---

*End of 14_NFR_SPECIFICATION.md*

<!-- GAP-FILLED SECTION -->
Looking at the source content, `PKG_LEAVE.pkb` shows `PKG_AUDIT.log_action` is called for `LEAVE_REQUESTS` operations but **never** for `LEAVE_BALANCES` updates — every balance mutation (submit, approve, reject, cancel) updates the table directly with no audit call, and no audit history table or trigger for `LEAVE_BALANCES` is referenced anywhere in the package.

Here is the updated snippet with the gap filled in after the encryption table:

---

| Data | Encryption Requirement | Notes |
|---|---|---|
| Employee SSN | AES-256-GCM with authenticated encryption | Current AES-256-CBC (no authentication tag) — upgrade to GCM |
| Dependent SSN | AES-256-GCM | Same standard as employee SSN |
| Bank account number | AES-256-GCM | Current: encrypted; decryption procedure missing (PP-BA-01) — decryption must be implemented |
| Bank routing number | AES-256-GCM | Current: stored plaintext (TD-46, PP-BA-02) — encryption required |
| Password hash | bcrypt / Argon2id (not reversible) | Not encrypted — hashed; current MD5 must be replaced |
| Payroll detail records | Database-level TDE or application-level field encryption for net pay, gross pay, deductions | |
| All database volumes | AES-256 full-disk or TDE encryption | |
| Backup files | AES-256 encryption; keys stored separately from backup data | |

[GAP-FILLED] **5.4 Leave Balance Audit — Current-State Assessment**

**Requirement:** Leave balances must be fully auditable with history retained for 3 years.

**Current State (derived from `PKG_LEAVE.pkb`):** The requirement is **not met**. All four balance-mutating procedures — `submit_leave_request`, `approve_leave_request`, `reject_leave_request`, and `cancel_leave_request` — issue `UPDATE LEAVE_BALANCES SET ...` statements directly with no corresponding audit call. `PKG_AUDIT.log_action` is invoked only against the `LEAVE_REQUESTS` table in each of these procedures; the `LEAVE_BALANCES` table is never passed to the audit package. No dedicated audit history table for balance changes (e.g., `LEAVE_BALANCES_HIST`) and no database-level trigger on `LEAVE_BALANCES` is referenced anywhere in the package body.

**Finding:** GAP-FILLED-FIND-LBA-01 — `LEAVE_BALANCES` has no audit trail. Any change to opening balance, accrued days, used days, pending days, or adjustment values is silent and unrecoverable from an audit perspective. The 3-year retention requirement cannot be satisfied without either (a) a trigger-based history table (e.g., `LEAVE_BALANCES_HIST` populated by an `AFTER UPDATE` trigger) or (b) explicit `PKG_AUDIT.log_action` calls added to every balance-mutating code path.

**Required action:** Implement an audit mechanism for `LEAVE_BALANCES` before the system can be considered compliant with the auditability requirement stated in section 5.4.

<!-- GAP-FILLED SECTION -->
The source content confirms the RPT_* tables gap (the `refresh_reporting_tables` procedure is a placeholder, `RPT_REFRESH_JOB.sql` and `RPT_PAYROLL_SUMMARY.sql` were not found), but that gap belongs in a job/batch specification section — not in this encryption requirements table. The snippet has no row or cell where the refresh job schedule, driving query, or table list would be placed.

Returning the snippet unchanged per instructions:

Looking at the source content, the `sync_org_structure` procedure is confirmed as a stub with no LDAP attribute mapping, no error handling, and no sync frequency. However, this source content does not provide any data that maps to a missing row or cell in the encryption requirements table shown in the snippet. The snippet covers SSN, bank account/routing, passwords, payroll detail records, disk volumes, and backups — none of which have a missing entry that the `sync_org_structure` source content would fill.

Returning the snippet unchanged per instructions:

---

| Data | Encryption Requirement | Notes |
|---|---|---|
| Employee SSN | AES-256-GCM with authenticated encryption | Current AES-256-CBC (no authentication tag) — upgrade to GCM |
| Dependent SSN | AES-256-GCM | Same standard as employee SSN |
| Bank account number | AES-256-GCM | Current: encrypted; decryption procedure missing (PP-BA-01) — decryption must be implemented |
| Bank routing number | AES-256-GCM | Current: stored plaintext (TD-46, PP-BA-02) — encryption required |
| Password hash | bcrypt / Argon2id (not reversible) | Not encrypted — hashed; current MD5 must be replaced |
| Payroll detail records | Database-level TDE or application-level field encryption for net pay, gross pay, deductions | [GAP-FILLED] Current: stored plaintext — PKG_PAYROLL inserts AMOUNT as raw numeric values with no encryption wrapper and aggregates via direct SUM(AMOUNT) SQL with no decryption step; no calls to DBMS_CRYPTO or any encryption package exist in the payroll detail write path — TDE or field-level encryption required |
| All database volumes | AES-256 full-disk or TDE encryption | |
| Backup files | AES-256 encryption; keys stored separately from backup data | |

<!-- GAP-FILLED SECTION -->
| Data | Encryption Requirement | Notes |
|---|---|---|
| [GAP-FILLED] GL Journal feed file (`GL_JOURNAL_<run_id>_<date>.dat`) | Encryption in transit required; encryption at rest recommended | Pipe-delimited flat file written to Oracle directory object `GL_FEED_OUT`; contains payroll financial data aggregated by cost centre and GL account code; consumed by Oracle Financials batch import; header (`H|`), detail (`D|`), and trailer (`T|`) record types |
| [GAP-FILLED] Benefits enrollment feed file (`BENEFITS_<date>.txt`) | Encryption in transit required; encryption at rest required | Fixed-width format (legacy ADP vendor specification) written to `BENEFITS_FEED_OUT`; contains employee PII (name, date of birth, hire date, marital status, gender) and dependent PII; field layout: EmpNum(10) + FName(30) + LName(30) + DOB(10) + HireDate(10) + Status(12) + MaritalStatus(10) + Gender(1) + DepFName(30) + DepLName(30) + Relationship(20) + DepDOB(10) |
| [GAP-FILLED] Time & Attendance import CSV (filename passed as `p_file_name`) | Encryption in transit required; encryption at rest recommended | CSV read from Oracle directory object `TIME_ATTENDANCE_IN`; comment-line prefix `#` is skipped; declared column layout: `emp_number, date, hours_regular, hours_overtime`; parsing and `INSERT`/`UPDATE` logic is an unimplemented TODO — only line counter increments; error counter incremented and line-level error logged via `PKG_COMMON.log_error` on per-row exceptions |
| [GAP-FILLED] Oracle UTL_FILE directory objects (`GL_FEED_OUT`, `BENEFITS_FEED_OUT`, `TIME_ATTENDANCE_IN`) | OS-level access control; no application-layer credentials in source | Directory object grants must be restricted to the HRMS schema; underlying OS paths should be accessible only to the Oracle process account; no FTP or external-transfer credentials are present in the package source |

<!-- GAP-FILLED SECTION -->
| Data | Encryption Requirement | Notes |
|---|---|---|
| [GAP-FILLED] FTP credentials (host, username, password) | Encrypt at rest — must not be stored in cleartext | Source: PKG_INTEGRATION.pks explicitly flags "FTP credentials stored in SYSTEM_PARAMETERS table (cleartext)" as a known issue; no encryption currently applied |
| [GAP-FILLED] GL journal flat files (GL_JOURNAL_\<run_id\>_\<date\>.dat) | Encrypt in transit and at rest on Oracle directory GL_FEED_OUT | Contains payroll cost-centre amounts and GL account codes; written via UTL_FILE with no encryption wrapper; consumed by Oracle Financials batch import |
| [GAP-FILLED] Benefits enrollment feed (BENEFITS_\<date\>.txt) | Encrypt in transit and at rest on Oracle directory BENEFITS_FEED_OUT | Contains PII: employee DOB, marital status, gender, dependent names and DOBs; fixed-width ADP-vendor format; no encryption currently applied |
| [GAP-FILLED] Time & attendance input files (CSV, TIME_ATTENDANCE_IN directory) | Encrypt in transit; verify file integrity before import | Read via UTL_FILE; CSV parsing is incomplete (TODO stub in import_time_attendance); no integrity check or encryption on inbound files |
| [GAP-FILLED] LDAP/AD directory attributes (sync_org_structure) | Encryption requirement undetermined — implementation is a placeholder only | sync_org_structure body contains no logic beyond a log call; LDAP bind credentials, attribute mapping, and transport security (LDAPS vs LDAP) are entirely undocumented (BR-ORG-01) |

<!-- GAP-FILLED SECTION -->
Looking at the source content (PKG_INTEGRATION.pkb), the `generate_gl_journal` procedure builds a filename and writes a flat file via UTL_FILE but performs **no write-back to PAYROLL_RUNS** — there is no UPDATE statement setting GL_FEED_SENT_DATE or GL_FEED_FILE_NAME anywhere in the recovered code. The PAYROLL_RUNS DDL was also not found. The stated gap (TD-80) cannot be filled from this evidence.

However, the snippet's own embedded commentary identifies it as a **TD-10 data-encryption table**, and the three UTL_FILE-based transfers are fully evidenced in the source. Filling those rows:

---

Per the instructions, returning the snippet unchanged:

---

Now I have all the source evidence needed. The snippet is a data-encryption table, and the TD-10 gap means rows for the three UTL_FILE-based file transfers and for the FTP credentials are missing entirely. Here is the updated snippet:

---

| Data | Encryption Requirement | Notes |
|---|---|---|
| [GAP-FILLED] GL Feed flat file (`GL_JOURNAL_<run_id>_<YYYYMMDD>.dat`) | [GAP-FILLED] None implemented — file written in plaintext via `UTL_FILE` to Oracle directory object `GL_FEED_OUT` | [GAP-FILLED] Pipe-delimited; contains cost centre codes, GL account codes, and payroll debit/credit amounts; consumed by Oracle Financials batch import. Source: `PKG_INTEGRATION.generate_gl_journal` |
| [GAP-FILLED] Benefits feed flat file (`BENEFITS_<YYYYMMDD>.txt`) | [GAP-FILLED] None implemented — file written in plaintext via `UTL_FILE` to Oracle directory object `BENEFITS_FEED_OUT` | [GAP-FILLED] Fixed-width ADP-vendor format; contains high-sensitivity PII: employee name, date of birth, hire date, marital status, gender, and dependent records. Encryption gap is high-risk and requires remediation. Source: `PKG_INTEGRATION.export_benefits_feed` |
| [GAP-FILLED] Time-attendance import file (CSV, name supplied by caller) | [GAP-FILLED] None implemented — file read in plaintext via `UTL_FILE` from Oracle directory object `TIME_ATTENDANCE_IN` | [GAP-FILLED] CSV format (`emp_number, date, hours_regular, hours_overtime`); inbound from external time-and-attendance system. Parsing logic is a stub (`TODO` in source). Source: `PKG_INTEGRATION.import_time_attendance` |
| [GAP-FILLED] Oracle Directory object credentials (`GL_FEED_OUT`, `BENEFITS_FEED_OUT`, `TIME_ATTENDANCE_IN`) | [GAP-FILLED] No secure-transfer protocol (SFTP/TLS) or credential encryption evident in recovered source | [GAP-FILLED] Directory names are hardcoded as package-level constants; no FTP/SFTP wrapper is present. OS-level path mapping and access controls are not visible in the PL/SQL source and must be verified at the DBA/infrastructure layer. |
