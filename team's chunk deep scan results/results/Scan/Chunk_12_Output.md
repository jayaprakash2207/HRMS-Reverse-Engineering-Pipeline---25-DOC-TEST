=== CHUNK METADATA ===
Chunk: 12            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-body
Expected files (2):
  1. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb (12825 chars written)
  2. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb (6600 chars written)
Total source content: 16497 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: Authentication, session lifecycle management, role/permission checks, SSN encryption, and password policy enforcement for the HRMS system.

**STRUCTURES:**
  c_encryption_key — KIND: constant; TYPE: RAW(32)
  c_session_timeout_min — KIND: constant; TYPE: NUMBER

**METHODS:**
  **FUNCTION hash_password(p_password IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L15-25]
  - What it does: Converts the input password to RAW, runs it through DBMS_CRYPTO.HASH using the MD5 algorithm, and returns the result as a hex string via RAWTOHEX.
  - Business rules: None beyond "password is hashed with MD5 before comparison/storage."
  - Numbers & thresholds: Uses DBMS_CRYPTO.HASH_MD5 as the hash algorithm identifier (named constant, not a numeric literal in this file). No other hardcoded numbers.
  - Security & error handling: WEAKNESS (per inline comment): uses MD5, a cryptographically broken/weak algorithm for password hashing — no salting, no adaptive/slow hash (e.g. bcrypt/PBKDF2) is used. No error handling present.
  - Data in/out: Input — p_password (VARCHAR2). Output — returns the MD5 hash of the password as a hex-encoded VARCHAR2.

  **FUNCTION authenticate(p_username IN VARCHAR2, p_password IN VARCHAR2, p_ip_address IN VARCHAR2 DEFAULT NULL) RETURN NUMBER** [SOURCE: L31-84]
  - What it does: Called to log a user in. Looks up EMPLOYEES by UPPER(EMAIL) = UPPER(p_username) restricted to EMPLOYMENT_STATUS = 'ACTIVE'. If no match, raises an application error with a generic "invalid username or password" message (to avoid username enumeration, per inline comment) — though the code comment also flags a timing-attack vulnerability since the two failure paths (bad user vs. bad password) take different code paths/time. If multiple active employees share the same email, picks the one with MIN(EMP_ID). Generates a new session id from SEQ_USER_SESSION, inserts a USER_SESSIONS row with status 'ACTIVE', calls PKG_EMPLOYEE.set_session_context and PKG_AUDIT.log_action, then returns the session id. Note: p_password itself is never actually checked/compared anywhere in this function body — the inline comments state real password storage would live in a separate USER_CREDENTIALS table and that this authenticate logic is a simplified stand-in ("simulate authentication against a simplified model") for the legacy codebase.
  - Business rules: Only employees with EMPLOYMENT_STATUS = 'ACTIVE' are eligible to authenticate [L47]. On no match, authentication fails with a generic error (no user enumeration) [L53]. On multiple active employees sharing an email, the lowest EMP_ID is selected as the authenticated user [L56-60].
  - Numbers & thresholds: RAISE_APPLICATION_ERROR code -20301 for "Invalid username or password" [L53]. (Oracle custom application error numbers are always in the -20000 to -20999 range; this package uses the -203xx/-231x sub-ranges for its distinct error conditions.)
  - Security & error handling: VULNERABILITY (per inline comment): no brute-force/lockout protection after repeated failed attempts [L29]. VULNERABILITY (per inline comment): timing attack — invalid-username and invalid-password cases are not constant-time [L50-51]. Password is accepted as a parameter but never actually validated/compared against a stored hash in this function. Session row is written with p_ip_address as supplied (no validation).
  - Data in/out: Inputs — p_username, p_password, p_ip_address (optional). Reads EMPLOYEES; writes a new row to USER_SESSIONS (via SEQ_USER_SESSION.NEXTVAL for the id); calls PKG_EMPLOYEE.set_session_context and PKG_AUDIT.log_action. Output — returns the new SESSION_ID (NUMBER).

  **PROCEDURE logout(p_session_id IN NUMBER)** [SOURCE: L89-97]
  - What it does: Updates the USER_SESSIONS row for the given session id, setting LOGOUT_TIME = SYSDATE and SESSION_STATUS = 'CLOSED'.
  - Business rules: A logged-out session is marked 'CLOSED' with a logout timestamp.
  - Numbers & thresholds: None.
  - Security & error handling: None — no check that the session exists or belongs to the caller before updating.
  - Data in/out: Input — p_session_id (NUMBER). Output — updates USER_SESSIONS (LOGOUT_TIME, SESSION_STATUS); no return value.

  **FUNCTION is_session_valid(p_session_id IN NUMBER) RETURN BOOLEAN** [SOURCE: L102-133]
  - What it does: Reads SESSION_STATUS and LOGIN_TIME for the given session. Returns FALSE if status isn't 'ACTIVE'. Otherwise computes elapsed minutes since LOGIN_TIME; if that exceeds the session timeout, auto-expires the session (sets SESSION_STATUS = 'EXPIRED', LOGOUT_TIME = SYSDATE) and returns FALSE. Otherwise returns TRUE. Returns FALSE if no session row is found.
  - Business rules: A session is valid only when SESSION_STATUS = 'ACTIVE' [L114]. A session auto-expires once more than 30 minutes have elapsed since LOGIN_TIME [L120].
  - Numbers & thresholds: c_session_timeout_min = 30 (minutes) [L9, L120]. Elapsed-time calculation: (SYSDATE - v_login_time) * 24 * 60 to convert days to minutes.
  - Security & error handling: NO_DATA_FOUND is caught and treated as an invalid session (returns FALSE) rather than raising an error.
  - Data in/out: Input — p_session_id (NUMBER). Reads USER_SESSIONS; may write (UPDATE) USER_SESSIONS to auto-expire. Output — returns BOOLEAN (session validity).

  **FUNCTION has_permission(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN** [SOURCE: L140-186]
  - What it does: Looks up the employee's DEPT_ID and (via JOB_TITLES join) GRADE_ID. Applies a simplified, hardcoded role model (per inline comment, a stand-in for a real ROLES/PERMISSIONS junction table): grade ≥ 8 gets full access to everything; grade ≥ 5 gets VIEW access to everything; any employee can CREATE/VIEW their own LEAVE-module records; any employee can VIEW the EMPLOYEE module (own profile). Otherwise returns FALSE. Returns FALSE if the employee isn't found.
  - Business rules: Job grade ≥ 8 → full access to all modules/actions (senior management) [L159-162]. Job grade ≥ 5 → VIEW access to all modules [L165-169]. Module = 'LEAVE' and action IN ('CREATE','VIEW') → allowed for everyone [L172-175]. Module = 'EMPLOYEE' and action = 'VIEW' → allowed for everyone [L177-180]. All other combinations → denied.
  - Numbers & thresholds: Grade threshold 8 (full access) [L161]; grade threshold 5 (view-all access) [L167]. Default p_action = 'VIEW'.
  - Security & error handling: NO_DATA_FOUND is caught and treated as "no permission" (returns FALSE). No check that p_module/p_action are valid/known values — unrecognized combinations simply fall through to FALSE.
  - Data in/out: Inputs — p_emp_id, p_module, p_action (defaults to 'VIEW'). Reads EMPLOYEES joined to JOB_TITLES. Output — returns BOOLEAN (permission granted/denied).

  **FUNCTION encrypt_ssn(p_ssn IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L191-202]
  - What it does: Encrypts the input SSN using DBMS_CRYPTO.ENCRYPT with AES-256 in CBC mode with PKCS5 padding, using the hardcoded package-level key, and returns the ciphertext as a hex string.
  - Business rules: None beyond "SSNs are stored encrypted, not in plaintext."
  - Numbers & thresholds: v_raw buffer declared as RAW(2000) [L194]. Algorithm = DBMS_CRYPTO.ENCRYPT_AES256 + DBMS_CRYPTO.CHAIN_CBC + DBMS_CRYPTO.PAD_PKCS5 (named constants, summed as the typ parameter).
  - Security & error handling: VULNERABILITY (per inline comment at L6-7): the AES-256 encryption key (c_encryption_key, RAW(32), derived from the literal string 'HR$ystem_3ncrypt10n_K3y_2024!!') is hard-coded directly in source rather than pulled from a secure key vault/wallet — anyone with source/package access can decrypt all SSNs. No error handling in this function.
  - Data in/out: Input — p_ssn (VARCHAR2, plaintext SSN). Output — returns hex-encoded AES-256-CBC ciphertext (VARCHAR2).

  **FUNCTION decrypt_ssn(p_encrypted IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L204-218]
  - What it does: Reverses encrypt_ssn — converts the hex ciphertext back to RAW, decrypts with DBMS_CRYPTO.DECRYPT using the same AES-256/CBC/PKCS5 scheme and the same hardcoded key, and casts the result back to VARCHAR2.
  - Business rules: None beyond reversing encrypt_ssn's encoding.
  - Numbers & thresholds: v_raw buffer declared as RAW(2000) [L207]. Same algorithm constants as encrypt_ssn (ENCRYPT_AES256 + CHAIN_CBC + PAD_PKCS5).
  - Security & error handling: Uses the same hard-coded encryption key as encrypt_ssn (see VULNERABILITY above). WHEN OTHERS catches any decryption failure and returns the literal string '***DECRYPT_ERROR***' instead of raising — this swallows all error detail/root cause.
  - Data in/out: Input — p_encrypted (VARCHAR2, hex ciphertext). Output — returns decrypted plaintext SSN (VARCHAR2), or '***DECRYPT_ERROR***' on any failure.

  **PROCEDURE change_password(p_emp_id IN NUMBER, p_old_password IN VARCHAR2, p_new_password IN VARCHAR2)** [SOURCE: L223-253]
  - What it does: Validates the new password against three complexity rules (length, uppercase, digit), raising a distinct application error for each violation. If all checks pass, calls PKG_AUDIT.log_action to record the change. Per inline comment, the actual password update to a USER_CREDENTIALS table is not implemented — this is a stub, and p_old_password is never checked/compared anywhere in the body.
  - Business rules: New password must be at least 8 characters long [L232]. New password must contain at least one uppercase letter (regex '[A-Z]') [L238]. New password must contain at least one numeric digit (regex '[0-9]') [L244]. p_old_password is accepted as a parameter but is not verified against any stored credential in this implementation.
  - Numbers & thresholds: Minimum password length = 8 [L232]. RAISE_APPLICATION_ERROR codes: -20310 "Password must be at least 8 characters" [L234], -20311 "Password must contain an uppercase letter" [L240], -20312 "Password must contain a number" [L246].
  - Security & error handling: Enforces basic password complexity (length ≥ 8, 1 uppercase, 1 digit) before allowing a change; raises specific -203xx errors for each failed rule. Does not verify p_old_password, so this stub as written would allow a password change without proving knowledge of the current password. No actual credential store write occurs (stub only, per comment at L249-250).
  - Data in/out: Inputs — p_emp_id, p_old_password (unused for verification), p_new_password. Output — no direct table write to a credentials table (stub); calls PKG_AUDIT.log_action to record the 'UPDATE' action against 'USER_CREDENTIALS' for p_emp_id, attributed to USER.

**DEPENDENCIES:**
  Data touched:
  - Reads: EMPLOYEES — lookup by UPPER(EMAIL) and EMPLOYMENT_STATUS = 'ACTIVE' (authenticate); EMPLOYEES joined to JOB_TITLES — DEPT_ID/GRADE_ID lookup by EMP_ID (has_permission); USER_SESSIONS — SESSION_STATUS/LOGIN_TIME lookup by SESSION_ID (is_session_valid); SEQ_USER_SESSION — sequence NEXTVAL for new session id (authenticate)
  - Writes: USER_SESSIONS — INSERT of new session row (authenticate); USER_SESSIONS — UPDATE LOGOUT_TIME/SESSION_STATUS='CLOSED' (logout); USER_SESSIONS — UPDATE SESSION_STATUS='EXPIRED'/LOGOUT_TIME on timeout (is_session_valid)

CALLS: DBMS_CRYPTO.HASH | EVIDENCE: EXTERNAL | SOURCE: L20
CALLS: UTL_RAW.CAST_TO_RAW | EVIDENCE: EXTERNAL | SOURCE: L7
CALLS: PKG_EMPLOYEE.set_session_context | EVIDENCE: OBSERVED | SOURCE: L79
CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L81
CALLS: DBMS_CRYPTO.ENCRYPT | EVIDENCE: EXTERNAL | SOURCE: L196
CALLS: DBMS_CRYPTO.DECRYPT | EVIDENCE: EXTERNAL | SOURCE: L209
CALLS: UTL_RAW.CAST_TO_VARCHAR2 | EVIDENCE: EXTERNAL | SOURCE: L214
CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L252

  Config/env: None (no environment variables or config keys referenced; the encryption key is a hardcoded source constant rather than an externalized config value — see GAPS).
  External integrations: DBMS_CRYPTO (Oracle built-in cryptography package) for MD5 password hashing and AES-256-CBC SSN encryption/decryption; UTL_RAW for RAW/VARCHAR2 conversions.

**GAPS:**
  UNRESOLVED: p_password is never actually compared/verified against any stored credential inside authenticate — the real credential check is stated in comments to live in a separate USER_CREDENTIALS table that this file does not implement; behavior of that missing check is UNKNOWN. UNRESOLVED: p_old_password in change_password is likewise never verified. NOT_ANALYZED: internals of PKG_EMPLOYEE.set_session_context and PKG_AUDIT.log_action (bodies not in this file). UNKNOWN: whether c_encryption_key is meant to be replaced by a wallet/vault-sourced key in production, or whether this hardcoded value is actually deployed as-is (flagged as a VULNERABILITY by the file's own inline comments).

*[pipeline status — type: plsql-body · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 20, 200]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: Centralized field/business-rule validation routines (dates, salary bands, email/phone/employee-number formats, business-day/holiday checks, required-field checks) used across HRMS.

**STRUCTURES:**
  None (only local variables scoped to individual functions; no package-level constants, types, or cursors declared).

**METHODS:**
  **FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN** [SOURCE: L6-17]
  - What it does: Returns FALSE if either date is NULL; otherwise returns TRUE only if p_end_date >= p_start_date.
  - Business rules: Both start and end dates are required. End date must be on or after start date.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Inputs — p_start_date, p_end_date (DATE). Output — returns BOOLEAN.

  **FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2** [SOURCE: L19-54]
  - What it does: Returns an error message if p_salary or p_grade_id is NULL. Otherwise looks up MIN_SALARY, MAX_SALARY, GRADE_NAME from JOB_GRADES for p_grade_id. Returns a formatted "below minimum" message if salary < min, a formatted "exceeds maximum" message if salary > max, otherwise returns NULL (valid). Returns "Invalid grade ID" message if the grade doesn't exist.
  - Business rules: Salary must fall within [MIN_SALARY, MAX_SALARY] for the employee's job grade. Salary and grade are both required inputs.
  - Numbers & thresholds: v_grade_name declared as VARCHAR2(50); salary values formatted with mask 'FM$999,999,990.00'. Actual MIN_SALARY/MAX_SALARY bounds are data-driven from JOB_GRADES, not literals in this function.
  - Security & error handling: NO_DATA_FOUND caught and returns 'Invalid grade ID: ' || p_grade_id instead of raising.
  - Data in/out: Inputs — p_salary (NUMBER), p_grade_id (NUMBER). Output — returns VARCHAR2 error message, or NULL if valid.

  **FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L56-61]
  - What it does: Delegates directly to PKG_COMMON.is_valid_email(p_email) and returns its result.
  - Business rules: Email validity rule itself lives in PKG_COMMON.is_valid_email (not in this file).
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Input — p_email (VARCHAR2). Output — returns BOOLEAN.

  **FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L63-68]
  - What it does: Delegates directly to PKG_COMMON.is_valid_phone(p_phone) and returns its result.
  - Business rules: Phone validity rule itself lives in PKG_COMMON.is_valid_phone (not in this file).
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Input — p_phone (VARCHAR2). Output — returns BOOLEAN.

  **FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L70-76]
  - What it does: Returns TRUE if p_emp_number matches the regex '^EMP-\d{6}$', FALSE otherwise.
  - Business rules: Employee number must be the literal prefix "EMP-" followed by exactly 6 digits, e.g. "EMP-001234".
  - Numbers & thresholds: Regex requires exactly 6 digits after "EMP-" (\d{6}); example format given in source comment is EMP-001234.
  - Security & error handling: None.
  - Data in/out: Input — p_emp_number (VARCHAR2). Output — returns BOOLEAN.

  **FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN** [SOURCE: L78-84]
  - What it does: Returns TRUE if TRUNC(p_date) is strictly after TRUNC(SYSDATE).
  - Business rules: A date counts as "future" only if its calendar day is strictly after today; same-day dates are not future.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Input — p_date (DATE). Output — returns BOOLEAN.

  **FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN** [SOURCE: L86-108]
  - What it does: Computes the day abbreviation for p_date (AMERICAN date language); returns FALSE immediately if it's 'SAT' or 'SUN'. Otherwise counts active HOLIDAYS rows for that TRUNC'd date where the holiday is global (LOCATION_CODE IS NULL) or matches p_location_code; returns TRUE only if that count is 0.
  - Business rules: Saturdays and Sundays are never business days, regardless of location/holidays. A weekday is a business day only if no active (ACTIVE_FLAG='Y') holiday applies globally or to the given location on that date.
  - Numbers & thresholds: None (day-of-week and holiday match are logic-driven, not numeric literals).
  - Security & error handling: None.
  - Data in/out: Inputs — p_date (DATE), p_location_code (VARCHAR2, optional). Output — returns BOOLEAN.

  **FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2** [SOURCE: L110-135]
  - What it does: If p_table_name = 'EMPLOYEES', selects the full row from EMPLOYEES by EMP_ID into a %ROWTYPE record and returns the first missing-field message among FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID (checked in that order); returns 'Record not found' if the employee doesn't exist. For any other table name, returns NULL (no check performed).
  - Business rules: For EMPLOYEES, First Name, Last Name, Hire Date, Department, and Job Title are all required. Comment notes this is a simplified stand-in for a generic data-dictionary-driven NOT NULL check that production would use; only EMPLOYEES is actually implemented — other tables pass through unchecked.
  - Numbers & thresholds: None.
  - Security & error handling: NO_DATA_FOUND caught and returns 'Record not found' instead of raising.
  - Data in/out: Inputs — p_table_name (VARCHAR2), p_record_id (NUMBER). Output — returns VARCHAR2 error message describing the first missing field, or NULL if valid/table not checked.

**DEPENDENCIES:**
  Data touched:
  - Reads: JOB_GRADES — MIN_SALARY/MAX_SALARY/GRADE_NAME lookup in validate_salary_for_grade; HOLIDAYS — active holiday lookup in is_business_day; EMPLOYEES — full row lookup in validate_required_fields
  - Writes: None

  CALLS: PKG_COMMON.is_valid_email | EVIDENCE: OBSERVED | SOURCE: L60
  CALLS: PKG_COMMON.is_valid_phone | EVIDENCE: OBSERVED | SOURCE: L67

  Config/env: None
  External integrations: None

**GAPS:**
  validate_required_fields only implements required-field checks for the EMPLOYEES table; behavior for any other table is "no check" (returns NULL) by design per the source comment, not a gap in extraction — but which other tables production intends to cover is UNKNOWN/NOT_ANALYZED (out of scope of this file).

*[pipeline status — type: plsql-body · pass: correction · attempt: 2 · coverage: 100% (numbers 5/5 · procedures 8/8 · units 8/8 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 2
Files delivered: 2
  Full coverage on first pass: 0
  Required correction: 2 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb
  Still incomplete after max attempts: 1 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb
Raw source: 16497 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===