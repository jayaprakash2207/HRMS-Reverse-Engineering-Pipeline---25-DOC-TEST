=== CHUNK METADATA ===
Chunk: 05            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-body
Expected files (2):
  1. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pkb (4195 chars written)
  2. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb (16230 chars written)
Total source content: 15367 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: writes audit trail records, purges old audit history, and retrieves change history for a given table/record

**STRUCTURES:**
  None (no package-level declarations; all variables are local to individual procedures/functions)

**METHODS:**
  **PROCEDURE log_action(p_table_name IN VARCHAR2, p_record_id IN NUMBER, p_action IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER, p_old_values IN CLOB DEFAULT NULL, p_new_values IN CLOB DEFAULT NULL)** [SOURCE: L6-31]
  - What it does: Called by other packages/triggers whenever a change needs to be audited. Runs as an autonomous transaction (PRAGMA AUTONOMOUS_TRANSACTION, L14) so it commits independently of the caller. Inserts one row into AUDIT_LOG capturing the table/record/action, old/new values, the acting user, timestamp, and the session's IP address and session ID pulled from SYS_CONTEXT, then commits.
  - Business rules: Audit logging must never fail the calling transaction — any exception is caught and rolled back locally (L27-30) rather than propagated, so a logging failure does not block the business operation that triggered it.
  - Numbers & thresholds: None.
  - Security & error handling: Captures IP_ADDRESS and SESSION_ID via SYS_CONTEXT('USERENV', ...) for traceability (L23-24). WHEN OTHERS is caught and swallowed with only a ROLLBACK — no re-raise, no logging of the failure itself (L27-30).
  - Data in/out: Inputs — p_table_name, p_record_id, p_action (required); p_user (defaults to current DB user), p_old_values, p_new_values (CLOBs, optional). Output/side effect — one row inserted into AUDIT_LOG using SEQ_AUDIT.NEXTVAL as the ID; commits independently via autonomous transaction.

  **PROCEDURE purge_old_records(p_days_to_keep IN NUMBER DEFAULT 365, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L33-47]
  - What it does: Deletes all AUDIT_LOG rows whose CHANGED_DATE is older than SYSDATE minus the retention window, commits, and prints the number of rows purged via DBMS_OUTPUT.
  - Business rules: Default retention period is 365 days if the caller does not specify one; any AUDIT_LOG row older than that cutoff is permanently deleted.
  - Numbers & thresholds: p_days_to_keep default = 365 (days).
  - Security & error handling: None — no exception handling; a failure propagates to the caller. p_user parameter is accepted but unused in the logic.
  - Data in/out: Inputs — p_days_to_keep (default 365), p_user (default current DB user, unused). Output/side effect — deletes matching rows from AUDIT_LOG, commits, and writes a count message to DBMS_OUTPUT.

  **FUNCTION get_change_history(p_table_name IN VARCHAR2, p_record_id IN NUMBER, p_from_date IN DATE DEFAULT NULL, p_to_date IN DATE DEFAULT NULL) RETURN SYS_REFCURSOR** [SOURCE: L49-69]
  - What it does: Opens and returns a REF CURSOR over AUDIT_LOG filtered to the given table name and record ID, optionally bounded by a from/to date range, ordered by CHANGED_DATE descending (most recent first).
  - Business rules: Date filters are optional/inclusive — a NULL p_from_date or p_to_date means that bound is not applied (L64-65).
  - Numbers & thresholds: None.
  - Security & error handling: None — no exception handling; caller is responsible for consuming/closing the returned cursor.
  - Data in/out: Inputs — p_table_name, p_record_id (required); p_from_date, p_to_date (optional). Output — open SYS_REFCURSOR selecting AUDIT_ID, TABLE_NAME, RECORD_ID, ACTION_TYPE, OLD_VALUES, NEW_VALUES, CHANGED_BY, CHANGED_DATE, IP_ADDRESS from AUDIT_LOG.

**DEPENDENCIES:**
  Data touched:
  - Reads: AUDIT_LOG — change history rows filtered by table/record/date range (get_change_history); SEQ_AUDIT — NEXTVAL used to generate new AUDIT_ID (log_action)
  - Writes: AUDIT_LOG — inserts new audit record (log_action); AUDIT_LOG — deletes records older than retention cutoff (purge_old_records)

  CALLS: DBMS_OUTPUT.PUT_LINE | EVIDENCE: OBSERVED | SOURCE: L45

  Config/env: SYS_CONTEXT('USERENV', 'IP_ADDRESS'), SYS_CONTEXT('USERENV', 'SESSIONID')
  External integrations: None

**GAPS:**
  SEQ_AUDIT sequence definition not present in this file — EXTERNAL. AUDIT_LOG table schema not present in this file — EXTERNAL.

*[pipeline status — type: plsql-body · pass: original · attempt: 1 · coverage: 100% (numbers 1/1 · procedures 3/3 · units 3/3 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: shared utility functions for HRMS — audit logging, system parameter access, business-day date math, fiscal period calculation, and formatting/validation of phone, SSN, currency, name, and email values

**STRUCTURES:**
  None — no package-level constants, types, or cursors declared in this body; all declarations are local to individual procedures/functions.

**METHODS:**
  **PROCEDURE log_error(p_package IN VARCHAR2, p_procedure IN VARCHAR2, p_message IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L10-35]
  - What it does: Called by other package code (and external callers) to record an error. Runs as an autonomous transaction so the log survives even if the caller's transaction rolls back. Inserts a row into AUDIT_LOG with TABLE_NAME='ERROR_LOG', RECORD_ID=0, ACTION_TYPE='INSERT', and NEW_VALUES built as a JSON-ish string embedding package/procedure/message, then commits.
  - Business rules: Logging runs in its own autonomous transaction so a failure/rollback in the caller does not lose the error record.
  - Numbers & thresholds: Message text truncated to 3000 characters via SUBSTR(p_message, 1, 3000) before storage; RECORD_ID hardcoded to 0.
  - Security & error handling: p_user defaults to the current session USER if not supplied. Embedded double quotes in the message are escaped via REPLACE(...,'"','\"') before building the pseudo-JSON string. On any exception (WHEN OTHERS), falls back to DBMS_OUTPUT.PUT_LINE as a last resort and rolls back the autonomous transaction — the error-logging call itself never propagates an exception to the caller.
  - Data in/out: Inputs — p_package, p_procedure, p_message (required), p_user (optional, defaults to USER). Output/side effect — inserts one row into AUDIT_LOG using SEQ_AUDIT.NEXTVAL for AUDIT_ID, then COMMIT (autonomous).

  **PROCEDURE log_info(p_package IN VARCHAR2, p_procedure IN VARCHAR2, p_message IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L40-61]
  - What it does: Same pattern as log_error but for informational logging. Runs as an autonomous transaction; inserts into AUDIT_LOG with TABLE_NAME='INFO_LOG', RECORD_ID=0, ACTION_TYPE='INSERT', NEW_VALUES holding package/procedure/message, then commits.
  - Business rules: Logging runs in its own autonomous transaction, isolated from the caller's transaction state.
  - Numbers & thresholds: Message text truncated to 3000 characters via SUBSTR(p_message, 1, 3000); RECORD_ID hardcoded to 0.
  - Security & error handling: p_user defaults to current session USER. On any exception (WHEN OTHERS), silently rolls back the autonomous transaction with no fallback output (unlike log_error, no DBMS_OUTPUT fallback here) — logging failures are swallowed.
  - Data in/out: Inputs — p_package, p_procedure, p_message (required), p_user (optional, defaults to USER). Output/side effect — inserts one row into AUDIT_LOG using SEQ_AUDIT.NEXTVAL for AUDIT_ID, then COMMIT (autonomous).

  **FUNCTION get_param(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L66-81]
  - What it does: Looks up a single configuration value from SYSTEM_PARAMETERS by PARAM_GROUP and PARAM_CODE and returns PARAM_VALUE.
  - Business rules: None beyond exact-match lookup on group+code.
  - Numbers & thresholds: None.
  - Security & error handling: If no matching row is found (NO_DATA_FOUND), returns NULL instead of raising an error.
  - Data in/out: Inputs — p_group, p_code. Output — returns PARAM_VALUE as VARCHAR2(4000), or NULL if not found.

  **FUNCTION get_param_number(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN NUMBER** [SOURCE: L83-92]
  - What it does: Calls get_param to fetch the raw string value, then converts it to NUMBER via TO_NUMBER.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: If the stored value is not numeric (VALUE_ERROR), returns NULL instead of raising.
  - Data in/out: Inputs — p_group, p_code. Output — returns the parameter value as NUMBER, or NULL if missing/non-numeric.

  **FUNCTION get_param_date(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN DATE** [SOURCE: L94-103]
  - What it does: Calls get_param to fetch the raw string value, then converts it to DATE using format mask 'YYYY-MM-DD'.
  - Business rules: Stored date parameters must be in 'YYYY-MM-DD' format to parse correctly.
  - Numbers & thresholds: None (format mask 'YYYY-MM-DD' is a format string, not a numeric literal).
  - Security & error handling: On any exception (WHEN OTHERS) — e.g. malformed date string or missing parameter — returns NULL instead of raising.
  - Data in/out: Inputs — p_group, p_code. Output — returns the parameter value as DATE, or NULL if missing/unparseable.

  **PROCEDURE set_param(p_group IN VARCHAR2, p_code IN VARCHAR2, p_value IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L108-130]
  - What it does: Updates PARAM_VALUE, MODIFIED_BY, and MODIFIED_DATE on SYSTEM_PARAMETERS for the row matching PARAM_GROUP/PARAM_CODE, but only if that row's EDITABLE_FLAG = 'Y'. Checks SQL%ROWCOUNT after the UPDATE and raises an error if zero rows were affected.
  - Business rules: Only parameters explicitly flagged EDITABLE_FLAG = 'Y' may be modified; non-editable parameters are protected from update. A call that matches zero editable rows (parameter doesn't exist in that group/code, or exists but is locked non-editable) is treated as a fatal error rather than silently ignored.
  - Numbers & thresholds: Custom error code -20900 raised on failure.
  - Security & error handling: p_user defaults to current session USER (used to stamp MODIFIED_BY). If SQL%ROWCOUNT = 0, raises RAISE_APPLICATION_ERROR(-20900, 'Parameter not found or not editable: ' || p_group || '.' || p_code) — no COMMIT is issued by this procedure itself.
  - Data in/out: Inputs — p_group, p_code, p_value (required), p_user (optional, defaults to USER). Output/side effect — updates one row in SYSTEM_PARAMETERS (PARAM_VALUE, MODIFIED_BY, MODIFIED_DATE) when the row exists and is editable; raises an exception otherwise.

  **FUNCTION business_days_between(p_start_date IN DATE, p_end_date IN DATE) RETURN NUMBER** [SOURCE: L135-150]
  - What it does: Iterates day-by-day from TRUNC(p_start_date) through TRUNC(p_end_date) inclusive, incrementing a counter for each day that is not Saturday or Sunday, and returns the total count.
  - Business rules: Saturday and Sunday are excluded from the business-day count; only Monday–Friday count. Both start and end dates are truncated to remove time components before comparison.
  - Numbers & thresholds: None (day-of-week check uses string comparison against 'SAT'/'SUN', not numeric literals).
  - Security & error handling: None — no explicit error handling; an end date before the start date would simply produce a zero-iteration loop returning 0.
  - Data in/out: Inputs — p_start_date, p_end_date (both DATE). Output — returns NUMBER count of business days in the inclusive range.

  **FUNCTION add_business_days(p_date IN DATE, p_days IN NUMBER) RETURN DATE** [SOURCE: L155-170]
  - What it does: Starting from TRUNC(p_date), advances one calendar day at a time, incrementing a counter only when the new day is not Saturday or Sunday, until the counter reaches p_days; returns the resulting date.
  - Business rules: Saturday and Sunday are skipped and do not count toward the requested number of business days added; only weekdays advance the counter.
  - Numbers & thresholds: None (day-of-week check uses string comparison against 'SAT'/'SUN', not numeric literals).
  - Security & error handling: None — no explicit error handling; a non-positive or NULL p_days is not explicitly guarded (loop condition p_added < p_days would simply not execute for p_days <= 0).
  - Data in/out: Inputs — p_date (DATE), p_days (NUMBER). Output — returns DATE that is p_days business days after p_date.

  **FUNCTION get_fiscal_year(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER** [SOURCE: L175-186]
  - What it does: Extracts the month from p_date; if the month is October or later, returns the calendar year + 1, otherwise returns the calendar year as-is.
  - Business rules: The organization's fiscal year begins October 1. Any date in October, November, or December belongs to the fiscal year of the following calendar year — e.g. a date in October 2024 falls in fiscal year 2025 (per the in-code example comment); dates from January through September belong to the fiscal year matching the calendar year.
  - Numbers & thresholds: Fiscal year boundary month = 10 (October); month >= 10 adds 1 to the calendar year. Worked example from code comments: October 2024 → fiscal year 2025.
  - Security & error handling: None.
  - Data in/out: Input — p_date (DATE, defaults to SYSDATE if not supplied). Output — returns NUMBER fiscal year.

  **FUNCTION get_fiscal_quarter(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER** [SOURCE: L191-203]
  - What it does: Extracts the month from p_date and maps it to a fiscal quarter number aligned to the October 1 fiscal year start.
  - Business rules: Fiscal Q1 = October, November, December (months 10,11,12); Fiscal Q2 = January, February, March (months 1,2,3); Fiscal Q3 = April, May, June (months 4,5,6); Fiscal Q4 = July, August, September (months 7,8,9).
  - Numbers & thresholds: Month-to-quarter mapping: months (10,11,12)→1; (1,2,3)→2; (4,5,6)→3; (7,8,9)→4.
  - Security & error handling: None — if month falls outside all listed sets (not possible for a valid DATE), CASE would return NULL with no ELSE branch.
  - Data in/out: Input — p_date (DATE, defaults to SYSDATE if not supplied). Output — returns NUMBER fiscal quarter (1-4).

  **FUNCTION format_phone(p_phone IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L208-227]
  - What it does: Strips all non-digit characters from p_phone via REGEXP_REPLACE, then formats the resulting digit string based on its length.
  - Business rules: A standard US domestic phone number must contain exactly 10 digits, formatted as "(NXX) NXX-XXXX". An 11-digit number is only recognized as a valid US/Canada international number if it begins with country code '1', formatted as "+1 (NXX) NXX-XXXX". Any other digit length or leading digit is returned unmodified (original p_phone value, not the stripped digits).
  - Numbers & thresholds: 10-digit US domestic format threshold; 11-digit international threshold requiring leading digit '1'. Format substring positions: for 10-digit — chars 1-3, 4-6, 7-10; for 11-digit — chars 2-4, 5-7, 8-11.
  - Security & error handling: None — no validation beyond length/prefix checks; malformed input falls through to the ELSE branch and is returned unchanged.
  - Data in/out: Input — p_phone (VARCHAR2). Output — returns formatted phone string, or the original input if it doesn't match a recognized pattern.

  **FUNCTION format_ssn_masked(p_ssn IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L232-242]
  - What it does: Masks an SSN for display, showing only the last 4 characters.
  - Business rules: A NULL SSN or one with fewer than 4 characters cannot be partially unmasked; the entire value is replaced with the full mask to avoid partial PII exposure. Otherwise, the SSN is returned as "***-**-" followed by the last 4 characters.
  - Numbers & thresholds: Minimum length threshold of 4 characters required for partial unmasking; last-4-characters extraction via SUBSTR(p_ssn, -4).
  - Security & error handling: PII protection control — ensures SSNs are never displayed in full; short/NULL inputs default to the fully-masked value '***-**-****' rather than exposing a partial or malformed value.
  - Data in/out: Input — p_ssn (VARCHAR2). Output — returns masked SSN string.

  **FUNCTION format_currency(p_amount IN NUMBER, p_currency_code IN VARCHAR2 DEFAULT 'USD') RETURN VARCHAR2** [SOURCE: L247-259]
  - What it does: Resolves a currency symbol from p_currency_code and concatenates it with p_amount formatted to two decimal places with thousands separators.
  - Business rules: Currency symbol resolved by ISO code: USD → '$', EUR → euro sign (CHR(8364)), GBP → pound sign (CHR(163)); any unrecognized code is used as a literal text prefix followed by a space (p_currency_code || ' ').
  - Numbers & thresholds: Character codes CHR(8364) for EUR, CHR(163) for GBP. Number format mask 'FM999,999,990.00' (fixed 2 decimal places, thousands-separated, no leading zero-suppression beyond one digit).
  - Security & error handling: None.
  - Data in/out: Inputs — p_amount (NUMBER, required), p_currency_code (VARCHAR2, defaults to 'USD'). Output — returns formatted currency string.

  **FUNCTION format_name(p_first_name IN VARCHAR2, p_last_name IN VARCHAR2, p_format IN VARCHAR2 DEFAULT 'FL') RETURN VARCHAR2** [SOURCE: L264-276]
  - What it does: Formats first/last name into a display string, capitalized via INITCAP, in the order controlled by p_format.
  - Business rules: Format code 'LF' produces "Last, First" order; any other value (including the default 'FL') produces "First Last" order.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Inputs — p_first_name, p_last_name (required), p_format (optional, defaults to 'FL'). Output — returns formatted, INITCAP-cased name string.

  **FUNCTION is_valid_email(p_email IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L281-285]
  - What it does: Validates p_email against a regular expression pattern.
  - Business rules: A valid email must have a non-empty local part, an '@' symbol, a domain name, and a top-level domain of at least two alphabetic characters.
  - Numbers & thresholds: TLD minimum length = 2 characters (regex quantifier {2,}).
  - Security & error handling: Regex pattern: `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$`. Used as input validation, not as a security control per se.
  - Data in/out: Input — p_email (VARCHAR2). Output — returns BOOLEAN (TRUE if the pattern matches).

  **FUNCTION is_valid_phone(p_phone IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L287-293]
  - What it does: Strips non-digit characters from p_phone, then checks whether the resulting digit count falls within an accepted range.
  - Business rules: A valid phone number must contain exactly 10 digits (US domestic) or 11 digits (US/Canada with country code) after stripping non-numeric characters.
  - Numbers & thresholds: Valid digit-length range: 10 to 11 (inclusive, via BETWEEN).
  - Security & error handling: None.
  - Data in/out: Input — p_phone (VARCHAR2). Output — returns BOOLEAN.

  **FUNCTION is_valid_ssn(p_ssn IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L295-299]
  - What it does: Strips non-digit characters from p_ssn, then checks the result matches exactly 9 digits via regex.
  - Business rules: A valid SSN must consist of exactly 9 digits after removing dashes, spaces, and other non-numeric characters.
  - Numbers & thresholds: Required digit count = 9 (regex `^\d{9}$`).
  - Security & error handling: None.
  - Data in/out: Input — p_ssn (VARCHAR2). Output — returns BOOLEAN.

**DEPENDENCIES:**
  Data touched:
  - Reads: SYSTEM_PARAMETERS — looked up by PARAM_GROUP/PARAM_CODE to return PARAM_VALUE (get_param, transitively get_param_number/get_param_date); SEQ_AUDIT — NEXTVAL consumed to generate AUDIT_ID (log_error, log_info)
  - Writes: AUDIT_LOG — inserts ERROR_LOG and INFO_LOG entries with package/procedure/message payloads (log_error, log_info); SYSTEM_PARAMETERS — updates PARAM_VALUE, MODIFIED_BY, MODIFIED_DATE where EDITABLE_FLAG = 'Y' (set_param)

  CALLS: PKG_COMMON.get_param | EVIDENCE: OBSERVED | SOURCE: L88
  CALLS: PKG_COMMON.get_param | EVIDENCE: OBSERVED | SOURCE: L99
  CALLS: DBMS_OUTPUT.PUT_LINE | EVIDENCE: OBSERVED | SOURCE: L32

  Config/env: SYSTEM_PARAMETERS table functions as an application configuration store, keyed by PARAM_GROUP/PARAM_CODE, accessed via get_param/get_param_number/get_param_date/set_param.
  External integrations: None

**GAPS:**
  Package spec (.pks) not included in this source — full public signatures, parameter defaults, and any additional declared constants/types at the spec level are UNRESOLVED/NOT_ANALYZED from this body alone. AUDIT_LOG and SYSTEM_PARAMETERS full column definitions are UNKNOWN beyond the columns referenced here.

*[pipeline status — type: plsql-body · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 20]*

---

=== CHUNK STATUS ===
Files expected: 2
Files delivered: 2
  Full coverage on first pass: 1
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb
  Still incomplete after max attempts: 1 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb
Raw source: 15367 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===