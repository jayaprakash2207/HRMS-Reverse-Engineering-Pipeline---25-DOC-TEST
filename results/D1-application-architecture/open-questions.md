# Open Questions
**System:** HRMS v4.2  
**Stage:** Stage 12 — Unknowns Requiring Human Review  
**Date:** 2026-08-03

All items below cannot be determined from the available codebase. They require human input (DBA, HR team, operations, or product owner) before migration planning can be completed.

---

## Infrastructure / Deployment

| ID | Question | Why It Matters |
|----|----------|---------------|
| OQ-INF-01 | Where is Oracle Forms 12c deployed? (Oracle WebLogic version, server OS, JDK version) | Determines migration window and compatibility constraints |
| OQ-INF-02 | What are the filesystem paths for Oracle Directory Objects: GL_FEED_OUT, BENEFITS_FEED_OUT, TIME_ATTENDANCE_IN, PAYROLL_OUTPUT? | Required to migrate file-based integrations; these paths are OS-level |
| OQ-INF-03 | What is the Oracle Database version (exact: 12cR1, 12cR2, 19c, 21c)? | Affects available features and migration tooling |
| OQ-INF-04 | Is there a DR/standby database? | Migration downtime window and switchover strategy |
| OQ-INF-05 | How many concurrent users typically use the system? What is peak load? | Capacity planning for the replacement system |
| OQ-INF-06 | What is the Oracle Forms deployment model: Oracle HTTP Server applet, Forms Standalone Launcher (JNLP), or WebSocket thin client? | Affects client compatibility during coexistence phase |

---

## Missing Source Files

| ID | Question | Why It Matters |
|----|----------|---------------|
| OQ-SRC-01 | HRMS_REPORTS.fmb — Can the full XML export be provided? | Feature inventory for the reporting module is unknown |
| OQ-SRC-02 | HRMS_ADMIN.fmb — Can the full XML export be provided? | Admin module features are unknown |
| OQ-SRC-03 | DBMS_SCHEDULER job DDL (for HRMS_NOTIFICATION_JOB and HRMS_LEAVE_ACCRUAL_JOB) — Can a DBA extract these from the live DB? | Without DDL, jobs will be lost on any environment rebuild |
| OQ-SRC-04 | USER_CREDENTIALS table DDL — referenced in PKG_SECURITY but not found in schema files | Password storage design is unknown; critical for auth migration |
| OQ-SRC-05 | Oracle Forms .fmb binary files — Are these version-controlled alongside the XML exports? | Binary files needed for Oracle Forms Builder; XML exports are read-only |
| OQ-SRC-06 | Oracle Forms configuration files (default.env, formsweb.cfg) — Are these in source control? | Required to understand environment configuration and connection strings |
| OQ-SRC-07 | TAX_BRACKETS table contents — Is the table currently populated with data? | PKG_PAYROLL has a TODO to read from this table but uses hard-coded values instead |

---

## Business Rules

| ID | Question | Why It Matters |
|----|----------|---------------|
| OQ-BIZ-01 | What is the correct hire date future limit: 90 days (form) or 180 days (DB trigger)? | Inconsistency VIO-DATA-01 must be resolved before migration |
| OQ-BIZ-02 | What is the intended behavior of VW_LEAVE_SUMMARY AVAILABLE — should it include or exclude PENDING days? | Inconsistency VIO-DATA-02 affects leave balance accuracy |
| OQ-BIZ-03 | What leave types are accrual-based vs. granted? What are the accrual rates per tenure bracket? | Needed for LeaveService implementation; PKG_LEAVE reads from LEAVE_TYPES but the data content is unknown |
| OQ-BIZ-04 | Is COBRA notification legally required? Has it been tracked/handled outside the HRMS? | The TODO in terminate_employee is a potential compliance gap |
| OQ-BIZ-05 | Is the fiscal year (October start) correct for all reporting? Or does it vary by report type? | PKG_COMMON.get_fiscal_year hard-codes month 10; affects all fiscal reporting |
| OQ-BIZ-06 | What is the intended RBAC model? The current GRADE_ID thresholds (5, 8) appear to be a simplification — is the business expectation more granular? | Critical for replacing PKG_SECURITY.has_permission with proper RBAC |
| OQ-BIZ-07 | What are the performance review cycle frequency options? Is ANNUAL the only type, or are there interim/probationary reviews? | PERFORMANCE_REVIEWS.REVIEW_TYPE is hard-coded to 'ANNUAL' in create_review |
| OQ-BIZ-08 | What happens to performance goals when a review is terminated mid-cycle (e.g., employee termination)? | No logic found for this scenario in PKG_PERFORMANCE |

---

## External Integrations

| ID | Question | Why It Matters |
|----|----------|---------------|
| OQ-INT-01 | What Oracle Financials (ERP) version is the GL journal file sent to? Does it have an API that could replace the flat-file approach? | Migration path for SYS-01 GL integration |
| OQ-INT-02 | What is the exact ADP product/version receiving the benefits feed? Is there an ADP API available? | Migration path for SYS-02 ADP integration |
| OQ-INT-03 | What time & attendance system is the intended source for import_time_attendance? | The stub procedure has no vendor identified |
| OQ-INT-04 | What LDAP/Active Directory system was intended for sync_org_structure? Is this feature planned or abandoned? | The stub procedure may be dead code |
| OQ-INT-05 | Is the GL journal file currently being processed by Oracle Financials? What is the file pickup mechanism (FTP, shared folder, manual)? | Needed to understand end-to-end integration flow |

---

## Security / Compliance

| ID | Question | Why It Matters |
|----|----------|---------------|
| OQ-SEC-01 | Is PKG_SECURITY.authenticate's password stub a known issue? Is there a separate authentication mechanism in use? | If auth is broken, there may be an undiscovered bypass (SSO, DB auth) |
| OQ-SEC-02 | When was the SSN encryption key last rotated? Is the hard-coded key still in use? | Pre-migration key rotation plan requires knowing the current state |
| OQ-SEC-03 | Has a penetration test been performed on the HRMS? Are the SQL injection and auth vulnerabilities already known? | Contextualizes urgency of VIO-SEC-01 and VIO-SEC-02 |
| OQ-SEC-04 | Is there a data retention policy for AUDIT_LOG? PKG_AUDIT.purge_old_records exists but its scheduling is unknown | Needed for AUDIT_LOG migration strategy |
| OQ-SEC-05 | Are there any active sessions currently using the system? How many total users are in the EMPLOYEES table? | Migration downtime planning |

---

## Data Quality

| ID | Question | Why It Matters |
|----|----------|---------------|
| OQ-DATA-01 | How many rows are in EMPLOYEES, PAYROLL_DETAILS, LEAVE_REQUESTS, AUDIT_LOG? | Migration time estimates and ETL sizing |
| OQ-DATA-02 | Are there any EMPLOYEES with duplicate usernames? (TOO_MANY_ROWS in authenticate suggests this may exist) | Must be resolved before authentication migration |
| OQ-DATA-03 | Has expire_carryover ever been run twice on the same day? Are any LEAVE_BALANCES double-subtracted? | Data quality check before LeaveService migration |
| OQ-DATA-04 | Are there any payroll runs in STATUS='PROCESSING' or partial states from past failures? | Must be resolved before PayrollService migration |
| OQ-DATA-05 | Is the HRMS_REPORTS form currently in use? What reports are most frequently run? | Determines reporting migration priority |
