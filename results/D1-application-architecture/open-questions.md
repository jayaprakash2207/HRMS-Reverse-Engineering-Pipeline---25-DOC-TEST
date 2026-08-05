# Open Questions — HRMS Application Architecture Extraction

**Extractor:** AA Agent 1 — Application Architecture Extractor  
**Date:** 2026-08-04  
**Status:** Requires human review / additional source discovery

---

## OQ-001: Missing HRMS_REPORTS.fmb Form
**Category:** Completeness  
**Severity:** HIGH  
**Description:** HRMS_MENU.xml contains a menu item that calls `OPEN_FORM('HRMS_REPORTS')`, but `HRMS_REPORTS.fmb` and its XML export are not present in the source set. This form presumably surfaces PKG_REPORTING data.  
**Required Action:** Locate and provide `forms/xml-exports/HRMS_REPORTS.xml`. If the form was never completed, document as incomplete feature.  
**Impact on Analysis:** PKG_REPORTING (MOD-005) has no identified UI caller. The 11 report procedures in PKG_REPORTING have unknown invocation paths.

---

## OQ-002: Missing HRMS_ADMIN.fmb Form
**Category:** Completeness  
**Severity:** HIGH  
**Description:** HRMS_MENU.xml contains an admin menu item (only visible to ADMIN permission holders), but `HRMS_ADMIN.fmb` is not in the source set. Admin functions typically include user management, system parameter configuration, and scheduler job control.  
**Required Action:** Locate and provide `forms/xml-exports/HRMS_ADMIN.xml`.  
**Impact on Analysis:** Admin functions (creating users, setting SYSTEM_PARAMETERS, controlling DBMS_SCHEDULER jobs) are uncharted.

---

## OQ-003: USER_CREDENTIALS Table Absent from Schema
**Category:** Data Integrity / Security  
**Severity:** CRITICAL  
**Description:** PKG_SECURITY.authenticate and hash_password reference a USER_CREDENTIALS table for password storage and verification. This table is not defined in any of the 4 schema DDL files provided (01_core_tables.sql through 04_performance_tables.sql). Either: (a) the table was never created and authentication is truly a stub, or (b) the DDL file is missing from the source set.  
**Required Action:** Confirm whether USER_CREDENTIALS table exists in the production Oracle schema (`SELECT * FROM ALL_TABLES WHERE TABLE_NAME='USER_CREDENTIALS'`). If it exists, provide DDL. If not, confirm that authentication is effectively bypassed in production.  
**Impact on Analysis:** VIO-003 severity is CRITICAL — if table is genuinely missing, the system has no functional password authentication.

---

## OQ-004: DBMS_SCHEDULER Job Definitions
**Category:** Completeness  
**Severity:** HIGH  
**Description:** Multiple scheduled operations are inferred from package comments (monthly leave accrual, carryover process, notification queue processor every 5 minutes, nightly GL feed, weekly benefits feed, audit purge), but no DBMS_SCHEDULER CREATE_JOB DDL scripts were found in the source set.  
**Required Action:** Export scheduler job definitions: `SELECT JOB_NAME, JOB_TYPE, JOB_ACTION, START_DATE, REPEAT_INTERVAL, ENABLED FROM DBA_SCHEDULER_JOBS WHERE OWNER='HRMS'`.  
**Impact on Analysis:** Scheduled job frequency, error handling, and failure notification cannot be assessed.

---

## OQ-005: Oracle Forms Deployment Configuration
**Category:** Infrastructure  
**Severity:** MEDIUM  
**Description:** The Oracle Forms 12c application deployment infrastructure (WebLogic Server or OC4J version, Forms Servlet configuration, database connection pool config, Oracle HTTP Server / Apache config) is not in the source set.  
**Required Action:** Provide `formsweb.cfg` and WebLogic domain configuration. Document whether deployment uses web browser (Java applet via browser plugin, JNLP, or webstart).  
**Impact on Analysis:** Cannot assess deployment risk or infrastructure migration complexity.

---

## OQ-006: Oracle Reports (.rdf) Definition Files
**Category:** Completeness  
**Severity:** MEDIUM  
**Description:** PKG_REPORTING provides 8 report data queries via REF CURSORs. Oracle Forms commonly launches Oracle Reports for formatted output (PDF, RTF, HTML). No `.rdf` files were found in the source set. It is unclear whether Oracle Reports is used alongside this system.  
**Required Action:** Confirm whether Oracle Reports is deployed. If yes, provide `.rdf` files.  
**Impact on Analysis:** Reporting migration strategy may need to include Oracle Reports runtime in addition to PKG_REPORTING.

---

## OQ-007: Self-Service Employee Portal Reference
**Category:** Completeness  
**Severity:** MEDIUM  
**Description:** A comment in `PKG_LEAVE.pkb` header references "Employee self-service portal integration". No self-service web application code (JSP, JSF, APEX, or modern web) was found in the source set.  
**Required Action:** Determine whether a self-service portal exists (e.g., Oracle APEX application, separate web app). If it exists, provide source for architecture review.  
**Impact on Analysis:** Unknown additional entry points into PKG_LEAVE and potentially PKG_EMPLOYEE.

---

## OQ-008: RPT_* Reporting Tables Not in Schema
**Category:** Data Integrity  
**Severity:** MEDIUM  
**Description:** PKG_REPORTING.refresh_reporting_tables (a stub) references denormalized reporting tables with an RPT_ prefix. No RPT_* tables are defined in the schema DDL files provided.  
**Required Action:** Check production schema for RPT_* tables: `SELECT TABLE_NAME FROM ALL_TABLES WHERE OWNER='HRMS' AND TABLE_NAME LIKE 'RPT_%'`. Provide DDL if they exist.  
**Impact on Analysis:** If these tables exist and are queried by Oracle Reports or HRMS_REPORTS.fmb, their structure affects reporting migration.

---

## OQ-009: EMPLOYEE_HISTORY.HISTORY_ID vs HIST_ID Column Name
**Category:** Data Integrity  
**Severity:** LOW  
**Description:** TRG_EMP_BEFORE_UPDATE inserts a row into EMPLOYEE_HISTORY using a column called `HISTORY_ID`. The Layer 1 JSON schema for EMPLOYEE_HISTORY lists `HIST_ID` (not `HISTORY_ID`). This may be a column name mismatch that would cause the trigger to fail at runtime.  
**Required Action:** Confirm actual column name in production: `SELECT COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE OWNER='HRMS' AND TABLE_NAME='EMPLOYEE_HISTORY' AND COLUMN_NAME LIKE '%HIST%'`.  
**Impact on Analysis:** If the column name is wrong, TRG_EMP_BEFORE_UPDATE silently fails (audit trail for status/dept/job changes is broken).

---

## OQ-010: Production Instance Count and Employee Volume
**Category:** Performance Assessment  
**Severity:** MEDIUM  
**Description:** Several performance risk assessments (row-by-row payroll loop, org chart >500 employees, notification queue flush time) depend on the employee headcount in production. The source code does not contain this data.  
**Required Action:** Provide approximate active employee count and peak concurrent user count.  
**Impact on Analysis:** Performance risk severity (VIO-018, CF-004 notes) depends heavily on org size.

---

## OQ-011: Encryption Key Rotation History
**Category:** Security  
**Severity:** HIGH  
**Description:** The hard-coded AES key contains the string `2024` suggesting it was introduced or last updated in 2024. It is unknown whether SSN data was ever encrypted with a different key (prior to 2024) and whether all records use the current key.  
**Required Action:** Determine from development team: has the encryption key ever been rotated? If so, are there any SSN records encrypted with the old key?  
**Impact on Analysis:** Re-encryption strategy for migration depends on this answer.

---

## OQ-012: Database Character Set and NLS Settings
**Category:** Migration  
**Severity:** LOW  
**Description:** Oracle database character set (AL32UTF8 vs WE8MSWIN1252, etc.) and NLS settings (NLS_DATE_FORMAT, NLS_CURRENCY) are not documented. These affect data migration to a new database platform.  
**Required Action:** `SELECT * FROM NLS_DATABASE_PARAMETERS` and `SELECT VALUE FROM NLS_DATABASE_PARAMETERS WHERE PARAMETER='NLS_CHARACTERSET'`.  
**Impact on Analysis:** Affects data migration scripts for any non-Oracle target.
