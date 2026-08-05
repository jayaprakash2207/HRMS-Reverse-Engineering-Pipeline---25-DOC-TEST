# HRMS Storage Pattern Analysis

**Schema:** HRMS  **DB:** Oracle 19c  **Extracted:** 2026-08-04  
**Method:** CODE-ONLY

---

## 1. Relational Tables (Primary Storage)

### Pattern: Surrogate PK + ACTIVE_FLAG Soft Delete

All 30 tables follow the same structural template:
- Surrogate PK from a dedicated `SEQ_*` sequence
- `ACTIVE_FLAG CHAR(1) DEFAULT 'Y'` — logical delete via Y/N
- Audit columns: `CREATED_BY`, `CREATED_DATE`, `MODIFIED_BY`, `MODIFIED_DATE`
- No physical row ever deleted (also enforced by INSTEAD_OF_DELETE trigger on EMPLOYEES)

**Implication for migration:** Data volumes will grow without bound. No archival or partitioning strategy is evident in the code. AUDIT_LOG is the only table with an explicit purge mechanism (365 days via PKG_AUDIT.purge_old_records).

---

## 2. Sequence Strategy

### All Sequences: NOCACHE (except SEQ_AUDIT)

| Sequence | Cache | Traffic Level |
|----------|-------|---------------|
| SEQ_AUDIT | CACHE 100 | Very high (every DML event) |
| SEQ_PAYROLL_DETAIL | NOCACHE | High (50+ rows per payroll run) |
| SEQ_LEAVE_ACCRUAL | NOCACHE | High (monthly batch, 1 row per emp per type) |
| SEQ_NOTIFICATION | NOCACHE | Medium (triggered by business events) |
| SEQ_EMP_HISTORY | NOCACHE | Medium (triggered by employee changes) |
| All others | NOCACHE | Low-Medium |

**Issue:** NOCACHE on high-traffic sequences causes a redo log write per fetch. Under a 500-employee payroll run with 6 elements each = 3,000 `SEQ_PAYROLL_DETAIL.NEXTVAL` calls in a single batch. Combined with the existing partial-commit pattern, this creates sustained I/O pressure.

**SEQ_EMP_NUMBER anomaly:** This sequence exists but PKG_EMPLOYEE uses `MAX(EMP_NUMBER)+1` instead of `SEQ_EMP_NUMBER.NEXTVAL`, creating a race condition (see DQ-005). The sequence is entirely unused.

---

## 3. LOB Storage

### Large Object Columns

| Table | Column | Type | Typical Size | Notes |
|-------|--------|------|-------------|-------|
| EMPLOYEES | PHOTO_BLOB | BLOB | Variable (JPEG/PNG photo) | No size limit defined in DDL |
| EMPLOYEES | NOTES | CLOB | Variable | Free-text HR notes |
| PERFORMANCE_REVIEWS | SELF_ASSESSMENT | CLOB | Medium | Free-text narrative |
| PERFORMANCE_REVIEWS | MANAGER_ASSESSMENT | CLOB | Medium | Free-text narrative |
| PERFORMANCE_REVIEWS | STRENGTHS | CLOB | Medium | Free-text narrative |
| PERFORMANCE_REVIEWS | AREAS_FOR_IMPROVEMENT | CLOB | Medium | Free-text narrative |
| PERFORMANCE_REVIEWS | DEVELOPMENT_PLAN | CLOB | Medium | Free-text narrative |
| PERFORMANCE_REVIEWS | EMPLOYEE_COMMENTS | CLOB | Medium | Free-text narrative |
| PERFORMANCE_GOALS | GOAL_DESCRIPTION | CLOB | Medium | Free-text |
| PERFORMANCE_GOALS | COMMENTS | CLOB | Medium | Free-text |
| AUDIT_LOG | OLD_VALUES | CLOB | Small-Medium | JSON old state |
| AUDIT_LOG | NEW_VALUES | CLOB | Small-Medium | JSON new state |
| NOTIFICATION_QUEUE | BODY | CLOB | Small-Medium | Email HTML body |
| LEAVE_REQUESTS | REASON | VARCHAR2(4000) | Small | Fits in row — not LOB |
| PAYROLL_DETAILS | ERROR_MESSAGE | VARCHAR2(4000) | Small | Fits in row — not LOB |

**Storage concern:** No LOB storage clauses (TABLESPACE, CHUNK, COMPRESS) are defined in the DDL. LOBs default to inline/deduplicate OFF. For a 500-employee company, 6+ CLOBs per review cycle review × 500 employees per year = 3,000+ CLOB rows in PERFORMANCE_REVIEWS. Photo BLOBs in EMPLOYEES have no size limit — a single upload of a 10MB photo is possible.

---

## 4. Flat File I/O (Oracle Directory Objects)

### Oracle Directory Objects — Write-Only Integration Pattern

The HRMS uses Oracle Directory Objects (CREATE DIRECTORY in Oracle DB) to map logical names to OS filesystem paths. The application writes to named directories via UTL_FILE; no path is hard-coded in the PL/SQL.

| Directory Object | Direction | Format | Naming Pattern | Consumer |
|-----------------|-----------|--------|---------------|---------|
| GL_FEED_OUT | WRITE | Pipe-delimited | GL_FEED_YYYYMMDD.dat | ERP/GL system |
| BENEFITS_FEED_OUT | WRITE | Fixed-width 203 chars (ADP) | BENEFITS_YYYYMMDD.dat | ADP via FTP |
| TIME_ATTENDANCE_IN | READ | CSV | TIME_IMPORT_YYYYMMDD.csv | HRMS (unimplemented) |
| PAY_REGISTER_OUT | WRITE | CSV | PAY_REGISTER_{run_id}_{YYYYMMDD_HH24MISS}.csv | Print/archive |

**Security concern (RC-006 corrected):** The benefits file does NOT contain decrypted SSN. `export_benefits_feed` writes demographic and dependent data only (names, DOB, hire date, marital status, gender). The prior claim about "SSN in plain text at positions 66-74" was false — SSN_ENCRYPTED is not selected and `PKG_SECURITY.decrypt_ssn` is not called. The file is still PII-sensitive (unencrypted demographic data) but the SSN risk was overstated. The filesystem path must still be secured at OS level.

**Operational concern:** File cleanup is not implemented in any package — old files accumulate on the Oracle server filesystem indefinitely.

---

## 5. Asynchronous Queue (NOTIFICATION_QUEUE Table)

### Table-as-Queue Pattern

NOTIFICATION_QUEUE implements a classic table-as-queue pattern:
- New notifications are INSERT'd (STATUS='PENDING') via PKG_NOTIFICATION.queue_notification
- A background processor (DBMS_SCHEDULER, implied every 5 minutes) calls PKG_NOTIFICATION.process_queue
- Processing uses PRAGMA AUTONOMOUS_TRANSACTION for isolation
- Failures set STATUS='FAILED'; up to 3 retries via PKG_NOTIFICATION.retry_failed

**Pattern strengths:** Simple; auditable; no external message broker required.

**Pattern weaknesses:**
- No dead-letter queue — failed messages after 3 retries are permanently stranded
- No consumer group / SKIP LOCKED — under concurrent processing, multiple scheduler invocations can pick up the same row
- No message ordering guarantee beyond PRIORITY + CREATED_DATE sort
- No bulk delivery batching — each notification triggers a separate SMTP connection

**Row accumulation:** NOTIFICATION_QUEUE has no purge procedure. SENT rows accumulate forever.

---

## 6. Configuration Store (SYSTEM_PARAMETERS Table)

### Key-Value Store Pattern

SYSTEM_PARAMETERS is a typed key-value store:
- `PARAM_GROUP` + `PARAM_CODE` = unique key (UK_PARAM_CODE constraint)
- `PARAM_VALUE` is VARCHAR2(4000) — all values stored as strings regardless of type
- `DATA_TYPE` column provides type hint (VARCHAR2/NUMBER/DATE/BOOLEAN) but is not enforced
- `EDITABLE_FLAG='N'` rows are protected from update via PKG_COMMON.set_param

**Known seed entries:**
- SMTP host/port for email delivery
- FTP credentials (cleartext — DQ-004)
- Audit retention days
- Session timeout minutes
- Payroll processing parameters

**Pattern concern:** Configuration and secrets (FTP password) are co-located in the same table without access-tier separation. Any Oracle user with SELECT on SYSTEM_PARAMETERS can read FTP credentials.

---

## 7. Audit Log (AUDIT_LOG Table)

### Append-Only Audit Trail

AUDIT_LOG stores before/after JSON snapshots for all audited DML:
- Populated via PRAGMA AUTONOMOUS_TRANSACTION (isolated from caller's transaction)
- SEQ_AUDIT uses CACHE 100 — the only cached sequence in the system
- OLD_VALUES / NEW_VALUES are CLOBs containing JSON strings
- TABLE_NAME='ERROR_LOG' and 'INFO_LOG' (RECORD_ID=0) co-mingle application logs with audit records
- No index on CHANGED_DATE — range queries on large tables will be full-table scans
- Purge: PKG_AUDIT.purge_old_records deletes rows older than 365 days (c_retention_days constant)

**Storage growth estimate:** At ~500 employees with ~50 audited events/year each = 25,000 audit rows/year (excluding payroll runs). A payroll run alone generates 500+ audit rows (one per PAYROLL_DETAILS row). High-growth table.

---

## 8. Session Store (USER_SESSIONS Table)

### Database-Backed Session Table

Sessions are stored in USER_SESSIONS table, not in Oracle's built-in session management:
- Each login inserts a row with SESSION_ID (from SEQ_USER_SESSION)
- SESSION_STATUS transitions: ACTIVE → EXPIRED / CLOSED
- Timeout validated by PKG_SECURITY.is_session_valid on every operation
- Old sessions are never purged — USER_SESSIONS grows unbounded

**Pattern concern:** No cleanup procedure found. After years of use, USER_SESSIONS will contain millions of EXPIRED/CLOSED rows. No index on LOGIN_TIME for cleanup queries.

---

## 9. Denormalized Reporting Layer (RPT_* Tables — Inferred, Stub-Only)

### Implied Truncate-and-Repopulate Pattern

`PKG_REPORTING.refresh_reporting_tables` contains this comment: _"In production, this truncates and repopulates RPT_* tables."_ The procedure body, however, contains only a `PKG_COMMON.log_info` call — **no TRUNCATE, no INSERT, no SELECT**. The 7 RPT_* tables implied are:

| Implied Table | Source Procedure | OLTP Tables Read |
|--------------|-----------------|-----------------|
| RPT_HEADCOUNT | headcount_report | EMPLOYEES, DEPARTMENTS, LOCATIONS |
| RPT_COMPENSATION | compensation_summary | EMPLOYEES, DEPARTMENTS, JOB_TITLES, JOB_GRADES, SALARY_RECORDS |
| RPT_TURNOVER | turnover_report | EMPLOYEES, DEPARTMENTS |
| RPT_NEW_HIRES | new_hires_report | EMPLOYEES, DEPARTMENTS, JOB_TITLES, LOCATIONS, SALARY_RECORDS |
| RPT_LEAVE_UTILIZATION | leave_utilization_report | LEAVE_BALANCES, EMPLOYEES, DEPARTMENTS, LEAVE_TYPES |
| RPT_PAYROLL_SUMMARY | payroll_summary_report | PAYROLL_DETAILS, PAYROLL_RUNS, EMPLOYEES, DEPARTMENTS |
| RPT_EEO_COMPLIANCE | eeo_compliance_report | EMPLOYEES, JOB_TITLES |

**DDL status:** Not found in Tables.sql. Whether these tables were ever created in the production Oracle instance is unknown.

**Operational impact:**
- The 7 report procedures operate by opening REF CURSOR queries directly against OLTP tables; they do not reference RPT_* tables. Reports work today without this layer.
- If any Oracle Reports (.rdf) or external consumer expects RPT_* to be populated before it runs, it will find ORA-00942 (table not found) or empty rows — depending on whether the DDL was deployed separately.
- The stub logs `'Reporting tables refreshed'` regardless of outcome, masking non-execution.

**Migration note:** If RPT_* tables never existed in production, there is no data to migrate for this layer. If they do exist and hold historical snapshots, each table is a separate migration target. The column shapes must be confirmed against production DDL before migration design. The truncate-and-repopulate pattern (if implemented) means these tables hold no state that cannot be regenerated from OLTP data.

---

## 10. Summary of Storage Patterns

| Pattern | Tables/Objects | Oracle-Specific | Migration Complexity |
|---------|---------------|-----------------|---------------------|
| Relational rows + ACTIVE_FLAG | 30 confirmed tables | No | Low |
| Inferred denormalized RPT_* layer | 7 implied tables (stub only) | No | Low–Medium (if DDL confirmed) |
| NOCACHE sequences | 28 sequences | Yes | Low |
| LOB storage (BLOB/CLOB) | 14 columns | Yes (syntax) | Medium |
| Oracle Directory + UTL_FILE | 4 directories | Yes | High |
| Table-as-queue | NOTIFICATION_QUEUE | No | Low |
| Key-value config | SYSTEM_PARAMETERS | No | Low |
| Append-only audit log | AUDIT_LOG | No | Low |
| DB-backed sessions | USER_SESSIONS | No | Low |
| Implicit scheduler | DBMS_SCHEDULER | Yes | Medium |
