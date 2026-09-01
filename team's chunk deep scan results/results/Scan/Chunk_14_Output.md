=== CHUNK METADATA ===
Chunk: 14            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-spec
Expected files (2):
  1. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks (7048 chars written)
  2. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pks (5275 chars written)
Total source content: 3355 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Public interface for authentication, session management, role-based authorization, and SSN/password encryption in HRMS.

**STRUCTURES:**
  e_invalid_credentials — KIND: exception; TYPE: N/A (ORA-20301)
  e_account_locked — KIND: exception; TYPE: N/A (ORA-20302)
  e_session_expired — KIND: exception; TYPE: N/A (ORA-20303)
  e_insufficient_priv — KIND: exception; TYPE: N/A (ORA-20304)

**METHODS:**
  **FUNCTION authenticate(p_username IN VARCHAR2, p_password IN VARCHAR2, p_ip_address IN VARCHAR2 DEFAULT NULL) RETURN NUMBER** [SOURCE: L24-28]
  - What it does: Declared entry point for logging a user in by username/password, with an optional IP address (for logging/lockout tracking). Per the file header, it is called by the HRMS_LOGIN form [L7]. Implementation logic is in PKG_SECURITY.pkb, not present in this file.
  - Business rules: Header comment flags a known issue that there is no account lockout after failed attempts [L11].
  - Numbers & thresholds: Raises e_invalid_credentials (ORA-20301) / e_account_locked (ORA-20302) on failure (codes declared here, raised by the body — NOT_ANALYZED for exact trigger conditions).
  - Security & error handling: Header notes password is stored as an MD5 hash rather than bcrypt/scrypt [L9], and the DBMS_CRYPTO key is hard-coded in the package body [L12] — both flagged as known weaknesses. No account lockout is enforced [L11].
  - Data in/out: Inputs — p_username, p_password (required), p_ip_address (optional, defaults NULL). Output — returns NUMBER (presumably a session ID).

  **PROCEDURE logout(p_session_id IN NUMBER)** [SOURCE: L30-32]
  - What it does: Declared entry point to terminate/invalidate a session by ID. Implementation in PKG_SECURITY.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None.
  - Security & error handling: None declared beyond the package-level exceptions.
  - Data in/out: Input — p_session_id. Output — none (procedure; side effect presumably invalidates the session).

  **FUNCTION is_session_valid(p_session_id IN NUMBER) RETURN BOOLEAN** [SOURCE: L34-36]
  - What it does: Declared entry point to check whether a session is still valid; per header comment, called by all forms for session validation [L7].
  - Business rules: Header flags a known issue that the session timeout check uses DB server time, not app server time [L10].
  - Numbers & thresholds: Associated with e_session_expired (ORA-20303), declared here for use by the implementation.
  - Security & error handling: Timeout comparison is server-time based (DB, not app server) per known-issues note [L10] — potential clock-skew risk, not fixed in this spec.
  - Data in/out: Input — p_session_id. Output — returns BOOLEAN.

  **FUNCTION has_permission(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN** [SOURCE: L38-42]
  - What it does: Declared entry point for role-based access control — checks whether an employee may perform an action on a module. Implementation in PKG_SECURITY.pkb, not present in this file.
  - Business rules: Default checked action is 'VIEW' when p_action is not supplied [L41].
  - Numbers & thresholds: Associated with e_insufficient_priv (ORA-20304), presumably raised by callers when this returns FALSE.
  - Security & error handling: This is the package's core authorization gate; no additional access control declared in the spec itself.
  - Data in/out: Inputs — p_emp_id, p_module (required), p_action (optional, default 'VIEW'). Output — returns BOOLEAN.

  **FUNCTION encrypt_ssn(p_ssn IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L44-46]
  - What it does: Declared entry point to encrypt a Social Security Number for storage, using DBMS_CRYPTO per the header comment [L12]. Implementation in PKG_SECURITY.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None in this spec (encryption key value is hard-coded in the package body per header note [L12], not visible here).
  - Security & error handling: Header explicitly flags the DBMS_CRYPTO key as hard-coded in the package body [L12] — a secrets-management weakness affecting this function.
  - Data in/out: Input — p_ssn (plaintext). Output — returns VARCHAR2 (encrypted value).

  **FUNCTION decrypt_ssn(p_encrypted IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L48-50]
  - What it does: Declared entry point to decrypt a previously encrypted SSN. Implementation in PKG_SECURITY.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None in this spec.
  - Security & error handling: Same hard-coded DBMS_CRYPTO key concern noted for encrypt_ssn [L12].
  - Data in/out: Input — p_encrypted. Output — returns VARCHAR2 (plaintext SSN).

  **FUNCTION hash_password(p_password IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L52-54]
  - What it does: Declared entry point to hash a plaintext password before storage. Implementation in PKG_SECURITY.pkb, not present in this file.
  - Business rules: Header states the password is stored as an MD5 hash rather than bcrypt/scrypt [L9] — a known weak-hashing issue.
  - Numbers & thresholds: None in this spec.
  - Security & error handling: MD5 is a cryptographically weak algorithm for password hashing; flagged as a known issue in the header itself [L9].
  - Data in/out: Input — p_password (plaintext). Output — returns VARCHAR2 (hash).

  **PROCEDURE change_password(p_emp_id IN NUMBER, p_old_password IN VARCHAR2, p_new_password IN VARCHAR2)** [SOURCE: L56-60]
  - What it does: Declared entry point to change an employee's password, presumably verifying p_old_password before applying p_new_password. Implementation in PKG_SECURITY.pkb, not present in this file.
  - Business rules: None visible in spec beyond requiring the old password as an argument.
  - Numbers & thresholds: None.
  - Security & error handling: Likely raises e_invalid_credentials (ORA-20301) if p_old_password doesn't match (INFERRED from naming/exception set — not observed, body not present).
  - Data in/out: Inputs — p_emp_id, p_old_password, p_new_password. Output — none (procedure); side effect presumably updates the stored password hash.

**DEPENDENCIES:**
  Data touched:
  - Reads: None (spec only — no implementation body in this file)
  - Writes: None (spec only — no implementation body in this file)

  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_AUDIT | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: None
  External integrations: DBMS_CRYPTO (Oracle built-in cryptography package) — mentioned only in the header comment as used by the package body for SSN/password encryption [L12]; not observed directly in this spec file.

**GAPS:**
  Implementation logic, lockout/timeout rules, and the hard-coded DBMS_CRYPTO key referenced in the header live in PKG_SECURITY.pkb (package body), which is not provided here — NOT_ANALYZED. Exact PKG_COMMON/PKG_AUDIT calls are UNKNOWN beyond the header's general dependency statement.

*[pipeline status — type: plsql-spec · pass: original · attempt: 1 · coverage: 100% (numbers 4/4 · procedures 8/8 · units 8/8 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Public interface for centralized business-rule validation shared between Forms WHEN-VALIDATE-ITEM triggers and PL/SQL packages (date ranges, salary-to-grade, email/phone/employee-number formats, future-date/business-day checks, required-field checks).

**STRUCTURES:**
  None (no constants, types, exceptions, or fields declared in this spec — only function signatures)

**METHODS:**
  **FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN** [SOURCE: L10-13]
  - What it does: Declared entry point to check whether p_start_date/p_end_date form a valid range. Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: None visible in spec (implementation not present).
  - Numbers & thresholds: None.
  - Security & error handling: None declared.
  - Data in/out: Inputs — p_start_date, p_end_date. Output — returns BOOLEAN.

  **FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2** [SOURCE: L15-18]
  - What it does: Declared entry point to validate a salary against the salary band of a job grade; per the inline comment, returns NULL if valid, an error message if invalid [L18]. Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: Returns NULL if valid, error message string if invalid [L18]. The actual band lookup (presumably against a JOB_GRADES-style table) is not visible in this spec.
  - Numbers & thresholds: None in this spec.
  - Security & error handling: None declared.
  - Data in/out: Inputs — p_salary, p_grade_id. Output — returns VARCHAR2 (NULL or error message).

  **FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L20-22]
  - What it does: Declared entry point to check whether p_email is a validly formatted email address. Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None.
  - Security & error handling: None declared.
  - Data in/out: Input — p_email. Output — returns BOOLEAN.

  **FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L24-26]
  - What it does: Declared entry point to check whether p_phone is a validly formatted phone number. Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None.
  - Security & error handling: None declared.
  - Data in/out: Input — p_phone. Output — returns BOOLEAN.

  **FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L28-30]
  - What it does: Declared entry point to check whether p_emp_number matches the expected employee-number format. Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None.
  - Security & error handling: None declared.
  - Data in/out: Input — p_emp_number. Output — returns BOOLEAN.

  **FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN** [SOURCE: L32-34]
  - What it does: Declared entry point to check whether p_date is in the future (presumably relative to SYSDATE). Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None.
  - Security & error handling: None declared.
  - Data in/out: Input — p_date. Output — returns BOOLEAN.

  **FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN** [SOURCE: L36-39]
  - What it does: Declared entry point to check whether p_date is a business day, optionally scoped to a location code (e.g. for location-specific holidays/weekends). Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: None visible in spec.
  - Numbers & thresholds: None.
  - Security & error handling: None declared.
  - Data in/out: Inputs — p_date (required), p_location_code (optional, defaults NULL). Output — returns BOOLEAN.

  **FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2** [SOURCE: L41-44]
  - What it does: Declared entry point to check that all required fields are populated for a given record in a given table; per the inline comment, returns NULL if all required fields are populated [L44]. Implementation in PKG_VALIDATION.pkb, not present in this file.
  - Business rules: Returns NULL if all required fields are populated; otherwise (INFERRED, not stated) an error message [L44].
  - Numbers & thresholds: None in this spec.
  - Security & error handling: None declared. The p_table_name parameter suggests the implementation may use dynamic SQL — NOT_ANALYZED, body not present.
  - Data in/out: Inputs — p_table_name, p_record_id. Output — returns VARCHAR2 (NULL or error message).

**DEPENDENCIES:**
  Data touched:
  - Reads: None (spec only — no implementation body in this file)
  - Writes: None

  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: None
  External integrations: None

**GAPS:**
  Implementation logic (email/phone/employee-number format rules, business-day/holiday rules, per-table required-field lists) is in PKG_VALIDATION.pkb, which is not provided here — NOT_ANALYZED.

*[pipeline status — type: plsql-spec · pass: original · attempt: 1 · coverage: 100% (numbers 0/0 · procedures 8/8 · units 8/8 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 2
Files delivered: 2
  Full coverage on first pass: 2
  Required correction: 0
  Still incomplete after max attempts: 0
Raw source: 3355 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===