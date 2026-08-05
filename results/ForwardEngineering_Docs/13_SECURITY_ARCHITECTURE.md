# 13 — Security Architecture
**System:** Acme Corporation HRMS (Oracle 19c / Oracle Forms 12c)
**Version:** 1.0 [VERIFIED-SUPPLEMENT]
**Status:** This document was MISSING from the original Foundation document set. All content below is [VERIFIED-SUPPLEMENT] sourced from TA_Stack_Scout.md, TA_Deep_Analyst.md, and TA_Deep_Analyst_Edge.md.

> **[VERIFIED-SUPPLEMENT] NOTE:** This file did not exist in the ForwardEngineering_Docs folder. It has been created in full from confirmed agent outputs. All sections are new additions to the Foundation document set and are marked [VERIFIED-SUPPLEMENT] throughout.

---

## [VERIFIED-SUPPLEMENT] 1. Authentication Mechanism

**Implementation:** PKG_SECURITY.authenticate — custom Oracle Forms session model.

| Attribute | Value | Source |
|---|---|---|
| Username field | EMPLOYEES.EMAIL (case-insensitive UPPER() match) | PKG_SECURITY.pkb confirmed |
| Password storage | MD5 hash via DBMS_CRYPTO.HASH_MD5 in USER_CREDENTIALS table | PKG_SECURITY.pkb; USER_CREDENTIALS DDL not provided |
| Session token | NUMBER(15) SESSION_ID returned from authenticate(); stored in USER_SESSIONS table | PKG_SECURITY.pkb |
| Session timeout | 30 minutes from LOGIN_TIME (not from last activity) | SYSTEM_PARAMETERS: SESSION_TIMEOUT_MIN=30; evaluated on-demand in is_session_valid() |
| Password complexity | ≥ 8 chars; at least 1 uppercase [A-Z]; at least 1 digit [0-9]; no special char requirement | PKG_SECURITY.change_password |

### [VERIFIED-SUPPLEMENT] Authentication Vulnerabilities

| ID | Severity | Finding | Evidence | Remediation |
|---|---|---|---|---|
| SEC-01 | **CRITICAL** | Password verification is a stub — `authenticate()` does NOT check the password. Any active employee username + ANY password returns a valid session. Source comment: "In the real system, passwords are stored in a separate USER_CREDENTIALS table. For this legacy codebase, we simulate authentication." | PKG_SECURITY.pkb: authenticate body; password parameter accepted but not validated | Implement full credential lookup against USER_CREDENTIALS.PASSWORD_HASH with a constant-time compare using DBMS_CRYPTO |
| SEC-02 | **CRITICAL** | MD5 password hashing — DBMS_CRYPTO.HASH_MD5 is cryptographically broken; MD5 hashes are reversible via rainbow tables | PKG_SECURITY.pkb: hash_password source comment "WEAKNESS: Uses MD5 - should use stronger algorithm" | Replace with bcrypt or scrypt via a Java Stored Procedure, or migrate to Oracle's native DBMS_CRYPTO.HASH_SH512 as an interim measure |
| SEC-03 | **CRITICAL** | No brute-force protection — no failed-attempt counter, no account lockout, no CAPTCHA, no rate limiting | PKG_SECURITY.pkb: no lockout logic; source comment "VULNERABILITY: No brute-force protection (no lockout after N failures)" | Add FAILED_LOGIN_COUNT column to USER_CREDENTIALS; lock account after 5 consecutive failures; add exponential backoff |
| SEC-04 | **HIGH** | Timing attack — `authenticate()` follows a different code path for unknown username (NO_DATA_FOUND → -20301) vs. known username (any-password success). Response time differential allows an attacker to enumerate valid email addresses | PKG_SECURITY.pkb: different exception handlers for user-not-found vs. user-found paths | Add a constant-time delay branch so both paths take the same elapsed time regardless of outcome |
| SEC-05 | **HIGH** | Hardcoded AES-256 encryption key — `HR$ystem_3ncrypt10n_K3y_2024!!` is a plaintext constant in PKG_SECURITY package body source code. All developer with source access can decrypt every SSN and bank account number | PKG_SECURITY.pkb: `c_encryption_key RAW(32) := UTL_RAW.CAST_TO_RAW('HR$ystem_3ncrypt10n_K3y_2024!!')` | Move key to Oracle Wallet (`DBMS_CRYPTO` keystore) or Oracle Key Vault; create a key rotation stored procedure; never store keys in source code |
| SEC-06 | **MEDIUM** | Session persists indefinitely after Forms window close without logout — USER_SESSIONS rows with STATUS='ACTIVE' are only invalidated on the NEXT is_session_valid() call; a user who closes the browser/Forms launcher without using File → Exit leaves an ACTIVE session row in the database with no automatic cleanup | PKG_SECURITY.pkb: is_session_valid() evaluates timeout only when called; no background sweep | Add DBMS_SCHEDULER job sweeping USER_SESSIONS every 5 minutes: `UPDATE USER_SESSIONS SET SESSION_STATUS='EXPIRED' WHERE SESSION_STATUS='ACTIVE' AND LOGIN_TIME < SYSDATE - INTERVAL '30' MINUTE` |
| SEC-07 | **MEDIUM** | logout() has no session ownership check — any authenticated caller can close any other user's session by passing a guessed SESSION_ID (no validation that the caller owns the session) | PKG_SECURITY.pkb: logout(p_session_id NUMBER) — no comparison of p_session_id to current session context | Add: `IF p_session_id != PKG_EMPLOYEE.g_current_emp_id THEN RAISE_APPLICATION_ERROR(-20302, 'Cannot close another user session')` or validate that EMP_ID on the session matches the current session context |
| SEC-08 | **MEDIUM** | PKG_LEAVE has zero server-side authorization gates — submit_leave_request, approve_leave_request, and cancel_leave_request contain no calls to PKG_SECURITY.has_permission(). Authorization exists only inside Oracle Forms WHEN-NEW-FORM-INSTANCE triggers. Any direct DB caller (self-service portal, SQL*Plus, batch job) bypasses authorization entirely | PKG_LEAVE.pkb: no PKG_SECURITY call in any state-changing procedure; TA_Deep_Analyst_Edge TD-49 | Add `PKG_SECURITY.has_permission(p_module=>'LEAVE', p_action=>'APPROVE')` guard at top of approve_leave_request and cancel_leave_request |
| SEC-09 | **MEDIUM** | Self-service portal DB authentication model is undeclared — PKG_LEAVE header states "Called by: self-service portal" but portal's DB connection credentials, schema grants, and session context setup are absent from all source files; if portal connects as the HRMS schema owner it has unrestricted DML on all HRMS tables | PKG_LEAVE.pks header; no grant scripts in repository; TA_Deep_Analyst TD-81 | Create dedicated DB user HRMS_PORTAL_APP with EXECUTE-only grants on specific procedures; revoke direct table grants; portal must pass valid session_id on every PKG_* call |

---

## [VERIFIED-SUPPLEMENT] 2. Authorization Model

**Pattern:** Grade-based RBAC implemented in PKG_SECURITY.has_permission(). No role-permission junction table is used — permission is derived purely from job grade.

| Grade Range | Access Level | Modules |
|---|---|---|
| Grade ≥ 8 | Full access — all modules, all actions | EMPLOYEE, PAYROLL, LEAVE, PERFORMANCE, REPORTS, ADMIN |
| Grade 5–7 | VIEW access on all modules | EMPLOYEE (VIEW), PAYROLL (VIEW), LEAVE (VIEW), REPORTS (VIEW) |
| Any grade | CREATE and VIEW own LEAVE | LEAVE (CREATE, VIEW own) |
| Any grade | VIEW own EMPLOYEE profile | EMPLOYEE (VIEW own) |
| All others | Denied | Everything else |

**Authorization gaps (confirmed from source):**

| Gap | Finding | Source | Remediation |
|---|---|---|---|
| No RBAC table | ROLE_PERMISSIONS table exists in schema but is never queried by has_permission() — permission is grade-only, with no fine-grained role assignment | PKG_SECURITY.pkb: no SELECT on ROLE_PERMISSIONS | Wire has_permission() to ROLE_PERMISSIONS for module-action pairs; retain grade as a fall-through rule |
| PERFORMANCE and LEAVE gates not enforced at package level | HRMS_PERFORMANCE and HRMS_LEAVE Forms open without any permission check (confirmed in TA_Stack_Scout.md Forms trigger analysis); server-side package procedures for these modules have no permission gates | TA_Stack_Scout.md Forms trigger analysis; PKG_LEAVE.pkb | Add PKG_SECURITY.has_permission() guards to all state-mutating procedures in PKG_LEAVE and PKG_PERFORMANCE |
| LOV_MANAGERS has no grade filter | Oracle Forms LOV_MANAGERS allows selecting any active employee as a manager, including Grade 1 interns — no seniority or IS_MANAGER constraint (TD-72) | HRMS_EMPLOYEE.xml: LOV_MANAGERS WHERE clause | Add grade filter or IS_MANAGER flag (see Document 19 §13.4) |

---

## [VERIFIED-SUPPLEMENT] 3. Encryption and Data Protection

| Data Element | Mechanism | Key Storage | Known Vulnerability |
|---|---|---|---|
| EMPLOYEES.SSN_ENCRYPTED | AES-256 CBC PKCS5 via DBMS_CRYPTO | Hardcoded constant in PKG_SECURITY.pkb | SEC-05 — key in source code; SEC-10 — no key rotation procedure |
| EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED | Same AES-256 mechanism; same key | Same hardcoded constant | SEC-10 — same key as EMPLOYEES; partial key rotation would leave dependent SSNs unreadable |
| EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC | AES-256; same key | Same hardcoded constant | ROUTING_NUMBER is stored plaintext — combined with encrypted account number = full ACH credentials in partial plaintext (TD-46) |
| USER_CREDENTIALS.PASSWORD_HASH (inferred) | MD5 via DBMS_CRYPTO.HASH_MD5 | N/A (hash, not encrypted) | SEC-02 — MD5 is reversible |
| ADP benefits feed (dependent DOB) | No encryption — plaintext in file | N/A | TD-51 — DOB + name + relationship = HIPAA PHI transmitted in plaintext to external vendor |

### [VERIFIED-SUPPLEMENT] Encryption Vulnerabilities

| ID | Severity | Finding | Evidence | Remediation |
|---|---|---|---|---|
| SEC-10 | **HIGH** | EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED uses the same hardcoded AES key as EMPLOYEES.SSN_ENCRYPTED. No key rotation procedure exists. A partial key rotation (re-encrypting EMPLOYEES but not EMPLOYEE_DEPENDENTS) leaves dependent SSNs permanently unreadable under the new key | PKG_SECURITY.pkb: single c_encryption_key constant; TA_Deep_Analyst_Edge TD-50 | Create an atomic key rotation procedure re-encrypting BOTH tables in a single transaction; store new key in Oracle Wallet |
| SEC-11 | **HIGH** | ADP benefits feed transmits EMPLOYEE_DEPENDENTS.DATE_OF_BIRTH in plaintext to an external vendor. DOB + name + relationship = HIPAA Protected Health Information (PHI) when transmitted to a benefits processor | PKG_INTEGRATION.export_benefits_feed: DepDOB field written as plain date string; no TLS on file transfer; TA_Deep_Analyst_Edge TD-51 | Require ADP SFTP with TLS 1.2+; or PGP-encrypt the outbound file; review BAA/DPA with ADP |
| SEC-12 | **LOW** | EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER is stored in plaintext — combined with the encrypted account number it constitutes complete ACH credentials, with the routing portion accessible without decryption | 02_payroll_tables.sql: ROUTING_NUMBER VARCHAR2(20) NOT NULL (no encryption); TD-46 | Evaluate encrypting ROUTING_NUMBER using the same AES mechanism; at minimum, restrict direct SELECT grants on EMPLOYEE_BANK_ACCOUNTS |

---

## [VERIFIED-SUPPLEMENT] 4. Network Security

| Layer | Mechanism | Known Vulnerability |
|---|---|---|
| Oracle Forms to DB | Oracle Net (TNS) within the WebLogic JVM | No network security configuration found in any source file |
| SMTP email delivery | UTL_SMTP port 25, plain text, no TLS, no authentication | **CRITICAL** — email notifications including payslip notifications transmitted without encryption; SEC-13 |
| Benefits feed transmission | File drop to Oracle directory object (BENEFITS_FEED_OUT) — no secure transfer protocol | TD-51 — plaintext file with HIPAA PHI |
| GL feed transmission | File drop to Oracle directory object (GL_FEED_OUT) — no secure transfer protocol | Financial data in plaintext on the filesystem |
| Self-service portal to DB | Unknown — no network topology documented | SEC-09 — portal authentication model undeclared |

### [VERIFIED-SUPPLEMENT] Network Vulnerability

| ID | Severity | Finding | Evidence | Remediation |
|---|---|---|---|---|
| SEC-13 | **HIGH** | SMTP transmission uses port 25 with no TLS — email notifications (payslip ready, leave approval, etc.) are sent in plaintext | PKG_NOTIFICATION.pkb: c_smtp_port = 25; UTL_SMTP.OPEN_CONNECTION; no TLS/STARTTLS call; TA_Deep_Analyst TD-14 | Upgrade to port 587 (STARTTLS) or port 465 (TLS); use Oracle's UTL_TCP with SSL context or migrate to a modern mail relay that supports STARTTLS |

---

## [VERIFIED-SUPPLEMENT] 5. Audit Trail

**Mechanism:** AUDIT_LOG table (single table for DML audit, error log, and info log) populated via:
- `PKG_AUDIT.log_action()` (PRAGMA AUTONOMOUS_TRANSACTION) — called by all 11 packages
- `TRG_SALARY_AUDIT`, `TRG_LEAVE_REQUEST_AUDIT`, `TRG_DEPARTMENT_AUDIT` (3 of 200+ declared triggers)
- `PKG_COMMON.log_error()` / `PKG_COMMON.log_info()` — write synthetic entries with TABLE_NAME='ERROR_LOG'/'INFO_LOG'

**Audit trail gaps:**

| Gap | Severity | Finding | Source |
|---|---|---|---|
| IP address is WebLogic server IP | **HIGH** | AUDIT_LOG.IP_ADDRESS captures `SYS_CONTEXT('USERENV','IP_ADDRESS')` — this returns the WebLogic application server IP, not the client's IP, because Oracle Forms is a reverse-proxy topology. Every audit entry shows the same server IP regardless of which user took the action — the audit trail has zero evidentiary value for user attribution | TA_Deep_Analyst TD-63 |
| TRG_EMP_BEFORE_UPDATE is broken | **CRITICAL** | Trigger inserts into columns CHANGE_DATE, OLD_VALUE, NEW_VALUE that do not exist in the EMPLOYEE_HISTORY DDL; all EMPLOYEES updates that fire the trigger will raise ORA-00904 in production | TA_Stack_Scout DISC-002; TA_Deep_Analyst TD-41 |
| Leave request INSERT not audited | **MEDIUM** | TRG_LEAVE_REQUEST_AUDIT fires only on UPDATE OF STATUS — the initial INSERT (new leave request) is never captured by the trigger. For auto-approved leave types, a single INSERT with STATUS='APPROVED' produces zero audit entries | TA_Deep_Analyst_Edge TD-56 |
| TRG_DEPARTMENT_AUDIT has no field-value capture | **LOW** | Department trigger fires but passes no OLD_VALUES/NEW_VALUES to PKG_AUDIT.log_action — audit records show that the department changed but not what changed | TA_Deep_Analyst TD-36 |
| 194+ triggers not provided | **MEDIUM** | README states 200+ triggers; only 6 are in the source set. Audit coverage of the remaining 194+ triggers is entirely unknown | TA_Stack_Scout.md |
| Audit retention is 365 days (default) | **LOW** | PKG_AUDIT.purge_old_records deletes entries older than p_days_to_keep (default 365). No scheduler DDL confirms this job runs. If the purge job never runs, AUDIT_LOG grows without bound | TA_Deep_Analyst TD-35 |

---

## [VERIFIED-SUPPLEMENT] 6. Input Validation and Injection

| Finding | Severity | Evidence | Remediation |
|---|---|---|---|
| SQL injection in PKG_EMPLOYEE.search_employees | **CRITICAL** | p_last_name, p_first_name, p_status, and p_location_code are concatenated into dynamic SQL without bind variables. Source comment explicitly states: "BUG: SQL injection possible via p_last_name if called with unvalidated input" | PKG_EMPLOYEE.pkb: EXECUTE IMMEDIATE '... WHERE LAST_NAME LIKE ''' \|\| p_last_name \|\| ''''; confirmed by TA_Stack_Scout | Replace all concatenated parameters with bind variables: `USING p_last_name, p_first_name, p_status` |
| SUPPORTING_DOC_PATH path traversal | **MEDIUM** | LEAVE_REQUESTS.SUPPORTING_DOC_PATH accepts free-text filesystem paths; no validation against directory traversal sequences (../, \\..\\); Oracle Forms HRMS_LEAVE stores whatever the user types; path could reference files outside the intended directory | TA_Deep_Analyst TD-47 | Whitelist SUPPORTING_DOC_PATH to a configurable allowed-prefix pattern; never use stored paths as direct OS read paths without validation |

---

## [VERIFIED-SUPPLEMENT] 7. Secrets Management

| Secret | Storage | Risk |
|---|---|---|
| AES-256 encryption key | Hardcoded in PKG_SECURITY.pkb source code | Any developer with source access can decrypt all SSNs and bank account numbers (SEC-05) |
| FTP/SFTP credentials for integration | SYSTEM_PARAMETERS table (plaintext), referenced in PKG_INTEGRATION.pks header comment | Credentials in database accessible to any user with SELECT on SYSTEM_PARAMETERS |
| Oracle database connection credentials | WebLogic JDBC datasource — configuration file not in repository | Unknown security posture; likely in WebLogic config.xml |
| SMTP relay details | SYSTEM_PARAMETERS (params 7-8) AND hardcoded in PKG_NOTIFICATION — both sources | Redundant storage; SYSTEM_PARAMETERS values are unused by the code |

**Recommendations:**
1. Oracle Wallet for encryption keys — remove all key material from source code and stored procedures
2. Oracle Key Vault or a dedicated secrets manager (HashiCorp Vault) for integration credentials
3. Credential scan in CI/CD to detect future secrets committed to source control
4. SYSTEM_PARAMETERS rows containing sensitive values (FTP credentials) should have EDITABLE_FLAG='N' with decrypted values accessible only via a keyed API, not plain SELECT

---

## [VERIFIED-SUPPLEMENT] 8. Compliance Posture

| Area | Status | Finding |
|---|---|---|
| PII inventory | Partially compliant | SSN encrypted at rest on EMPLOYEES and EMPLOYEE_DEPENDENTS; bank account number encrypted; audit log captures changes; PII columns inventoried |
| HIPAA (benefits data) | **Non-compliant** | Dependent DOB (PHI) transmitted to ADP in plaintext with no secure transport (SEC-11); no Business Associate Agreement verification against current transmission mechanism |
| IRS payroll audit trail | **Non-compliant** | EMPLOYEE_TAX_INFO has no effective-date history — mid-year W-4 changes permanently overwrite the prior election; pre-change withholding basis cannot be reconstructed (TD-55) |
| FMLA compliance | **At risk** | FMLA leave type has REQUIRES_DOCUMENT='N' — FMLA leave is accepted without documentation; exposes company to abuse claims and DOL audit findings (TD-71) |
| EEO reporting accuracy | **At risk** | EMPLOYEES.GENDER has no CHECK constraint; arbitrary values distort EEO compliance report counts (TD-40); eeo_compliance_report uses weaker active-employee filter than headcount_report (TD-83) |
| Soft delete / data retention | Compliant | Physical deletes blocked by TRG_EMP_INSTEAD_OF_DELETE; ACTIVE_FLAG pattern used consistently; 365-day AUDIT_LOG retention (if purge job runs) |

---

## [VERIFIED-SUPPLEMENT] 9. EOL Technology Risk

| Component | Status | Risk |
|---|---|---|
| Oracle Forms 12.2.1.4 | **Extended Support ended October 2025** | System has been running unsupported for 10+ months (as of August 2026). No new security patches, no CPU (Critical Patch Update) for any zero-day found after October 2025 (TD-57). |
| Oracle WebLogic 12c | Standard support end December 2025 | Same timeline — new vulnerabilities in WebLogic 12c will receive no fixes. |
| Java Plugin (NPAPI) for browser Forms delivery | Removed from Chrome (2015), Firefox (2017); Edge never supported it | Oracle Forms 12c requires Java Plugin for in-browser delivery. Supported delivery path (IE 11 Enterprise Mode / Java Web Start) uses EOL components (IE 11 EOL June 2022, JWS removed from JDK 11+). Delivery mechanism for 200 users is entirely undocumented (TD-58). |

**Recommended immediate actions:**
1. Escalate EOL status to executive sponsor — obtain risk acceptance sign-off or begin Oracle Forms migration
2. Document the current client delivery mechanism (IE 11 Enterprise Mode? Java Web Start? Oracle Forms Standalone Launcher?)
3. Engage Oracle Support for a Sustaining Support contract to receive at least advisory-level guidance on critical vulnerabilities

---

## [VERIFIED-SUPPLEMENT] 10. Security Architecture for Forward-Engineering (Target State)

The following requirements apply to the replacement SPA + REST API architecture. They are derived from legacy vulnerabilities identified above and from industry best practices.

| Requirement | Implementation Guidance |
|---|---|
| Authentication | OAuth 2.0 + OIDC with a corporate IdP (Azure AD, Okta, etc.); no custom credential storage; Oracle Forms custom session model not reproduced |
| Token storage | Access token in-memory only (no localStorage); refresh token in httpOnly secure cookie (SameSite=Strict) — already specified in Document 19 §5 |
| Session management | JWT expiry enforced server-side; sliding expiry (refresh on activity) replaces the fixed-from-login-time model |
| Password storage | Delegated to IdP; if local auth required: bcrypt with work factor ≥ 12 |
| Encryption key management | Oracle Wallet or dedicated KMS (AWS KMS, Azure Key Vault, HashiCorp Vault); never in application source code |
| Authorization | Role-based with database-backed permission table; grade threshold as a fallback tier, not the primary mechanism |
| Input validation | All API endpoints validate inputs server-side using parameterized queries / ORM; dynamic SQL with string concatenation is prohibited |
| Transport security | TLS 1.2+ minimum on all connections (API, SMTP, file transfers to ADP and Oracle Financials) |
| Audit trail | Structured audit log with correlation ID; client IP captured at API gateway (not at DB layer to avoid proxy-IP problem); append-only design |
| Secret scanning | CI/CD pipeline must include secret scanning (TruffleHog, gitleaks) — prevents recurrence of the hardcoded-key pattern |
| Dependency scanning | All SPA and API dependencies scanned for known CVEs in CI pipeline |

END OF DOCUMENT 13_SECURITY_ARCHITECTURE.md
