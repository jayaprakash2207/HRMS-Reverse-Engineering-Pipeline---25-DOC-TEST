=== CHUNK METADATA ===
Chunk: 15            (chunk count is budget-driven, not a fixed file count)
Type group: schema
Expected files (6):
  1. [schema] ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql (10804 chars written)
  2. [schema] ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_VALIDATION_LIB.pll.sql (7520 chars written)
  3. [schema] ts-plsql-oracle-forms-hrms-main/forms/menus/HRMS_MENU.mmb.sql (4736 chars written)
  4. [schema] ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql (4815 chars written)
  5. [schema] ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_employees.sql (7173 chars written)
  6. [schema] ts-plsql-oracle-forms-hrms-main/schema/sequences/hrms_sequences.sql (4959 chars written)
Total source content: 29518 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql ===

**IDENTITY:**
  KIND: PL/SQL library (PLL) — Forms client-side shared code, exported as source
  PURPOSE: Shared toolbar button handlers, global error handling, date formatting, and session/LOV helper routines attached to every HRMS form via ATTACH_LIBRARY.

**STRUCTURES:**
  None — this file declares only standalone procedures/functions; each uses local variables that don't outlive their own call.

**METHODS:**
  **PROCEDURE handle_error(p_module IN VARCHAR2, p_location IN VARCHAR2)** [SOURCE: L16-39]
  - What it does: Global exception handler wrapping all form-level errors. Logs the error via PKG_COMMON.log_error inside its own sub-block (swallowing any logging failure so it can't recurse), then displays the message twice via MESSAGE (Forms status-bar quirk requiring a double call), then raises FORM_TRIGGER_FAILURE to halt processing.
  - Business rules: Logging failures must never propagate (WHEN OTHERS THEN NULL around the log call) so the original error is always still shown to the user. The calling form/trigger is always aborted (FORM_TRIGGER_FAILURE) after an error is handled — there is no "continue" path.
  - Numbers & thresholds: v_errmsg is capped at VARCHAR2(500) [L21] — SQLERRM text longer than 500 chars would be silently truncated.
  - Security & error handling: Falls back to the Oracle DB session user (USER) when :GLOBAL.current_user is not set [L27], so every logged error has a user identity. Inner logging block explicitly catches WHEN OTHERS to prevent a logging failure from masking/recursing the original error. Always terminates by raising FORM_TRIGGER_FAILURE [L38].
  - Data in/out: Inputs — p_module, p_location (both VARCHAR2, identify where the error occurred). Reads SQLCODE/SQLERRM implicitly. Output — none (side effects: audit log write via PKG_COMMON.log_error, user-facing MESSAGE, then raises FORM_TRIGGER_FAILURE).

  **PROCEDURE toolbar_save** [SOURCE: L45-48]
  - What it does: Called from the HRMS_TOOLBAR canvas Save button. Calls the Forms built-in COMMIT_FORM.
  - Business rules: None beyond delegating to standard Forms commit.
  - Numbers & thresholds: None.
  - Security & error handling: None — no explicit error handling; relies on Forms' own commit error dialogs.
  - Data in/out: No inputs. Output — commits the current form's pending DML.

  **PROCEDURE toolbar_clear** [SOURCE: L50-53]
  - What it does: Called from the toolbar Clear button. Calls CLEAR_FORM(ASK_COMMIT), which prompts to save unsaved changes before clearing.
  - Business rules: User is prompted to commit (ASK_COMMIT) before the form is cleared.
  - Numbers & thresholds: None.
  - Security & error handling: None explicit.
  - Data in/out: No inputs/outputs beyond clearing the form's in-memory state.

  **PROCEDURE toolbar_query** [SOURCE: L55-63]
  - What it does: Called from the toolbar Query button. If the form is in NORMAL mode, enters query mode (ENTER_QUERY); if already in ENTER-QUERY mode, executes the query (EXECUTE_QUERY).
  - Business rules: Toggle behavior — first press opens query-entry mode, second press (while in query-entry mode) runs the query. No action in any other :SYSTEM.MODE state.
  - Numbers & thresholds: None.
  - Security & error handling: None explicit.
  - Data in/out: Input — implicit :SYSTEM.MODE. Output — form transitions to query-entry mode or executes a query.

  **PROCEDURE toolbar_first** [SOURCE: L65-68]
  - What it does: Calls FIRST_RECORD Forms built-in.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: No inputs; navigates cursor to the first record.

  **PROCEDURE toolbar_prev** [SOURCE: L70-73]
  - What it does: Calls PREVIOUS_RECORD Forms built-in.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: No inputs; navigates cursor to the previous record.

  **PROCEDURE toolbar_next** [SOURCE: L75-78]
  - What it does: Calls NEXT_RECORD Forms built-in.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: No inputs; navigates cursor to the next record.

  **PROCEDURE toolbar_last** [SOURCE: L80-83]
  - What it does: Calls LAST_RECORD Forms built-in.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: No inputs; navigates cursor to the last record.

  **PROCEDURE toolbar_insert** [SOURCE: L85-88]
  - What it does: Calls CREATE_RECORD Forms built-in.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: No inputs; creates a new blank record in the current block.

  **PROCEDURE toolbar_delete** [SOURCE: L90-93]
  - What it does: Calls DELETE_RECORD Forms built-in.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: No inputs; marks the current record for deletion.

  **PROCEDURE toolbar_exit** [SOURCE: L95-98]
  - What it does: Calls EXIT_FORM(ASK_COMMIT).
  - Business rules: User is prompted to commit unsaved changes before exiting.
  - Numbers & thresholds: None.
  - Security & error handling: None explicit.
  - Data in/out: No inputs; exits the form.

  **FUNCTION format_date(p_date IN DATE) RETURN VARCHAR2** [SOURCE: L103-106]
  - What it does: Formats a date using TO_CHAR with mask 'MM/DD/YYYY'.
  - Business rules: Standard display format is MM/DD/YYYY across the application.
  - Numbers & thresholds: None (format mask is not a numeric literal/threshold).
  - Security & error handling: None.
  - Data in/out: Input — p_date (DATE). Output — formatted VARCHAR2 string.

  **FUNCTION format_datetime(p_date IN DATE) RETURN VARCHAR2** [SOURCE: L108-111]
  - What it does: Formats a date/time using TO_CHAR with mask 'MM/DD/YYYY HH24:MI:SS'.
  - Business rules: Standard display format for timestamps across the application.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Input — p_date (DATE). Output — formatted VARCHAR2 string.

  **FUNCTION get_current_user RETURN VARCHAR2** [SOURCE: L116-120]
  - What it does: Returns the current application user, falling back to the Oracle session user.
  - Business rules: Falls back to the DB session user (USER) when the HRMS application-level global user (:GLOBAL.current_user) is not populated, so every operation has a traceable identity.
  - Numbers & thresholds: None.
  - Security & error handling: None explicit; NVL fallback prevents a NULL identity.
  - Data in/out: No inputs. Output — VARCHAR2 user identifier.

  **FUNCTION get_session_id RETURN NUMBER** [SOURCE: L122-128]
  - What it does: Converts the :GLOBAL.session_id global variable (stored as text) to a NUMBER via TO_NUMBER.
  - Business rules: None beyond conversion.
  - Numbers & thresholds: None.
  - Security & error handling: Catches VALUE_ERROR (non-numeric/absent session id) and returns NULL rather than raising, so callers must treat NULL as "no session."
  - Data in/out: No inputs (reads :GLOBAL.session_id). Output — NUMBER or NULL.

  **PROCEDURE check_session** [SOURCE: L130-145]
  - What it does: Called at the start of form operations requiring an authenticated user. Checks get_session_id for NULL (no session) and, if present, validates it against PKG_SECURITY.is_session_valid.
  - Business rules: A valid HRMS session ID must exist in the global context before any form operation is permitted. Even when a session ID is present, it must pass PKG_SECURITY.is_session_valid or it's treated as expired.
  - Numbers & thresholds: None.
  - Security & error handling: No session → message "No active session. Please log in." then RAISE FORM_TRIGGER_FAILURE [L134-136]. Invalid/expired session → message "Session has expired. Please log in again." then RAISE FORM_TRIGGER_FAILURE [L141-143]. This is the library's core access-control gate.
  - Data in/out: No explicit inputs (reads global session state via get_session_id). Output — none; aborts form processing on failure.

  **PROCEDURE refresh_lov(p_lov_name IN VARCHAR2)** [SOURCE: L150-159]
  - What it does: Derives a record group name by stripping an 'LOV_' prefix from p_lov_name, upper-casing it, and prefixing 'RG_'. If that record group exists in the form (ID_NULL(FIND_GROUP(...)) is false), repopulates it via POPULATE_GROUP.
  - Business rules: A record group is only refreshed if it already exists in the form; refreshing a non-existent group is skipped rather than erroring.
  - Numbers & thresholds: v_rg_name is capped at VARCHAR2(60) [L151] — derived record-group names longer than 60 chars would be truncated.
  - Security & error handling: Existence check (ID_NULL/FIND_GROUP) guards against a runtime error from populating a non-existent group; no other error handling.
  - Data in/out: Input — p_lov_name (VARCHAR2, e.g. 'LOV_DEPARTMENT'). Output — none directly; side effect is repopulating the derived record group (e.g. RG_DEPARTMENT) if it exists.

  **FILE-LEVEL EFFECT** [SOURCE: L1-159]
  - What it does: Represents the compiled HRMS_COMMON_LIB.pll, attached via ATTACH_LIBRARY to every HRMS form. Loading/attaching it makes all of the above procedures/functions available as shared subprograms callable from any form-level trigger (toolbar handlers, error handling, date formatting, session/LOV helpers) without each form needing its own copy.
  - Business rules: Centralizes session-gating (check_session) and error handling (handle_error) so all forms share one authentication/error contract.
  - Numbers & thresholds: VARCHAR2(500) cap on error message buffer in handle_error [L21]; VARCHAR2(60) cap on derived record-group name buffer in refresh_lov [L151].
  - Security & error handling: See check_session and handle_error above — this library is the shared point where session validity and error propagation are enforced for all attached forms.
  - Data in/out: No file-level inputs/outputs beyond making the subprograms above available to attaching forms.

**DEPENDENCIES:**
  Data touched:
  - Reads: None (reads only Forms globals :GLOBAL.current_user / :GLOBAL.session_id, not database tables)
  - Writes: None

  CALLS: PKG_COMMON.log_error | EVIDENCE: OBSERVED | SOURCE: L26
  CALLS: PKG_SECURITY.is_session_valid | EVIDENCE: OBSERVED | SOURCE: L140

  Config/env: :GLOBAL.current_user, :GLOBAL.session_id (Forms global context variables)
  External integrations: None

**GAPS:**
  UNKNOWN: exact set of forms that ATTACH_LIBRARY this PLL — comment states "All HRMS forms" but this is not verifiable from this file alone.
  UNKNOWN: where :GLOBAL.current_user and :GLOBAL.session_id are populated (presumably a login form, not present in this file).
  NOT_ANALYZED: PKG_SECURITY.is_session_valid and PKG_COMMON.log_error internals (defined in other files).

*[pipeline status — type: schema · pass: correction · attempt: 2 · coverage: 100% (numbers 2/2 · tables 0/0 · units 1/1 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_VALIDATION_LIB.pll.sql ===

**IDENTITY:**
  KIND: Forms library (PLL source export)
  PURPOSE: client-side validation functions (email, phone, SSN, date, salary range) shared across Oracle Forms, used for immediate on-form feedback ahead of/alongside server-side validation

**STRUCTURES:**
  None (file declares only standalone functions with local, per-call variables; no package-level constants, fields, types, or cursors)

**METHODS:**
  **FUNCTION validate_email(p_email IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L21-44]
  - What it does: Client-side email format check, called from form-item validation triggers. If `p_email` is NULL, returns TRUE immediately. Otherwise finds the `@` position; if invalid, returns FALSE. Then finds the next `.` after the `@`; if invalid, returns FALSE. Otherwise returns TRUE.
  - Business rules: NULL email is not required and is treated as valid, bypassing all format checks [L25-28]. Email must contain exactly one meaningful `@` that is not absent, not the first character, and not the last character of the string [L31-34]. The domain (after `@`) must contain a `.` that is not absent, not immediately following `@`, and not the final character [L36-40]. Known bug/drift: only checks for one dot after `@`, so it wrongly rejects valid subdomain emails (e.g., user@mail.company.com); server-side `PKG_VALIDATION` uses a more permissive `REGEXP_LIKE` pattern, so the two can disagree [L8-11, L17-19, L42].
  - Numbers & thresholds: `v_at_pos = 0` → invalid (no `@` found) [L32]. `v_at_pos = 1` → invalid (`@` is the first character) [L32]. `v_at_pos = LENGTH(p_email)` → invalid (`@` is the last character) [L32]. `v_dot_pos = 0` → invalid (no `.` found after `@`) [L38]. `v_dot_pos = v_at_pos + 1` → invalid (`.` immediately follows `@`) [L38]. `v_dot_pos = LENGTH(p_email)` → invalid (`.` is the last character) [L38].
  - Security & error handling: No access control or secrets involved. No exception handling — pure string-position logic. Functions purely as client-side input validation; can drift from the server-side equivalent in `PKG_VALIDATION`.
  - Data in/out: Input — `p_email VARCHAR2`. Output — returns `BOOLEAN` (TRUE if NULL or well-formed, FALSE otherwise).

  **FUNCTION validate_phone(p_phone IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L50-68]
  - What it does: Client-side US phone format check. If `p_phone` is NULL, returns TRUE. Otherwise strips all non-digit characters via `TRANSLATE` and checks the resulting digit count.
  - Business rules: NULL phone is not required and is treated as valid [L53-56]. A valid US phone number must have exactly 10 digits (local format, no country code) or 11 digits (including a leading country-code digit); any other count is rejected [L61-65].
  - Numbers & thresholds: Accepted stripped-digit lengths: `10` or `11` [L63]. `TRANSLATE(p_phone, '0123456789()-. +x', '0123456789')` strips the characters `(`, `)`, `-`, `.`, space, `+`, `x` down to bare digits [L59].
  - Security & error handling: No access control or secrets. No exception handling.
  - Data in/out: Input — `p_phone VARCHAR2`. Output — returns `BOOLEAN` (TRUE if NULL or 10/11 digits, FALSE otherwise).

  **FUNCTION validate_ssn(p_ssn IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L74-98]
  - What it does: Client-side SSN format check. If `p_ssn` is NULL, returns TRUE. Strips non-digit/dash characters via `TRANSLATE`, checks digit count, then checks that no SSA segment is all zeros.
  - Business rules: NULL SSN is not required and is treated as valid [L77-80]. SSN must be exactly 9 numeric digits after stripping dashes [L84-87]. None of the three SSA-issuance segments may be all zeros: area number (digits 1-3), group number (digits 4-5), serial number (digits 6-9) [L89-95].
  - Numbers & thresholds: Required stripped-digit length: `9` [L85]. Area segment = `SUBSTR(v_digits, 1, 3)`, invalid if equal to `'000'` [L91]. Group segment = `SUBSTR(v_digits, 4, 2)`, invalid if equal to `'00'` [L92]. Serial segment = `SUBSTR(v_digits, 6, 4)`, invalid if equal to `'0000'` [L93].
  - Security & error handling: No access control or secrets, though it client-side-validates a sensitive PII field (SSN). No exception handling.
  - Data in/out: Input — `p_ssn VARCHAR2`. Output — returns `BOOLEAN` (TRUE if NULL or a valid 9-digit SSN, FALSE otherwise).

  **FUNCTION validate_date_not_future(p_date IN DATE) RETURN BOOLEAN** [SOURCE: L104-108]
  - What it does: Single-expression check validating that a date is not in the future. Returns TRUE if `p_date` is NULL, or if its truncated value is on or before today's truncated system date.
  - Business rules: NULL date is not required and is treated as valid [L107]. A non-NULL date must be today or earlier; time-of-day is ignored via `TRUNC` on both sides [L107].
  - Numbers & thresholds: None.
  - Security & error handling: None; relies on `SYSDATE` for the current server date, no exception handling.
  - Data in/out: Input — `p_date DATE`. Output — returns `BOOLEAN`.

  **FUNCTION validate_salary_range(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2** [SOURCE: L117-148]
  - What it does: Validates an entered salary against the salary band of its job grade. Returns NULL immediately if either `p_salary` or `p_grade_id` is NULL. Otherwise runs a direct `SELECT MIN_SALARY, MAX_SALARY` against `JOB_GRADES` for the given `GRADE_ID` (despite the header/inline comments claiming a form-startup cache is used — the actual code queries the database on every call, a comment/code mismatch [L111-115, L130-131]). Returns an error string if salary is below the minimum or above the maximum; returns NULL if within range; returns `'Invalid grade'` if the grade lookup fails.
  - Business rules: Validation is skipped (returns NULL) if either `p_salary` or `p_grade_id` is NULL [L125-128]. Salary must not be below the job grade's `MIN_SALARY` [L136-138]. Salary must not exceed the job grade's `MAX_SALARY` [L139-141]. An unmatched `GRADE_ID` (`NO_DATA_FOUND`) is reported as `'Invalid grade'` rather than being treated as valid [L145-147].
  - Numbers & thresholds: `MIN_SALARY`/`MAX_SALARY` themselves are not hardcoded — they are read per-row from `JOB_GRADES` by `GRADE_ID` [L133-134]. Number formatting mask used in both error messages: `'FM$999,999'` [L138, L141].
  - Security & error handling: No access control or secrets. Explicit exception handler for `NO_DATA_FOUND`, returning `'Invalid grade'` [L145-147]; no other exceptions are trapped.
  - Data in/out: Inputs — `p_salary NUMBER`, `p_grade_id NUMBER`. Output — returns `VARCHAR2`: NULL if valid/skipped, an error message otherwise. Side effect — read-only `SELECT` against `JOB_GRADES`.

**DEPENDENCIES:**
  Data touched:
  - Reads: JOB_GRADES — MIN_SALARY, MAX_SALARY looked up by GRADE_ID in `validate_salary_range` [L133-134]
  - Writes: None

  Config/env: None
  External integrations: None

**GAPS:**
  UNKNOWN: which .fmb form modules attach/reference `HRMS_VALIDATION_LIB.pll` — not visible from this source export.
  UNRESOLVED: header and inline comments for `validate_salary_range` describe a "hard-coded cache... populated at form startup" that goes stale [L111-115], but the actual code issues a live `SELECT` against `JOB_GRADES` on every call [L130-134] — comment and code disagree; the code (no caching, always fresh) is treated as authoritative.
  EXTERNAL: `PKG_VALIDATION` is referenced only in comments as the server-side counterpart with a "more permissive" `REGEXP_LIKE` email pattern [L8-11, L17-19] — not analyzed as part of this file.

*[pipeline status — type: schema · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 20; units missing: FILE-LEVEL EFFECT]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/menus/HRMS_MENU.mmb.sql ===

**IDENTITY:**
  KIND: Forms menu module — comment-only source representation of the compiled binary HRMS_MENU.mmb (no executable PL/SQL in this file)
  PURPOSE: Documents the main application menu bar structure (File, Edit, Query, Navigate, Modules, Admin, Help) and the Forms built-in or module action bound to each item

**STRUCTURES:**
  MAIN_MENUBAR — KIND: Forms menu; TYPE: N/A

  **File menu items:**
  Save — KIND: Forms menu item; TYPE: N/A (action: COMMIT_FORM)
  Save & Exit — KIND: Forms menu item; TYPE: N/A (action: COMMIT_FORM; EXIT_FORM)
  Print — KIND: Forms menu item; TYPE: N/A (action: RUN_PRODUCT)
  Exit — KIND: Forms menu item; TYPE: N/A (action: EXIT_FORM)

  **Edit menu items:**
  Clear Record — KIND: Forms menu item; TYPE: N/A (action: CLEAR_RECORD)
  Duplicate Record — KIND: Forms menu item; TYPE: N/A (action: DUPLICATE_RECORD)
  Delete Record — KIND: Forms menu item; TYPE: N/A (action: DELETE_RECORD)
  Insert Record — KIND: Forms menu item; TYPE: N/A (action: CREATE_RECORD)

  **Query menu items:**
  Enter Query — KIND: Forms menu item; TYPE: N/A (action: ENTER_QUERY)
  Execute Query — KIND: Forms menu item; TYPE: N/A (action: EXECUTE_QUERY)
  Cancel Query — KIND: Forms menu item; TYPE: N/A (action: EXIT_FORM)
  Count Matching — KIND: Forms menu item; TYPE: N/A (action: COUNT_QUERY)
  Fetch Next Set — KIND: Forms menu item; TYPE: N/A (action: SCROLL_DOWN)

  **Navigate menu items:**
  First Record — KIND: Forms menu item; TYPE: N/A (action: FIRST_RECORD)
  Previous Record — KIND: Forms menu item; TYPE: N/A (action: PREVIOUS_RECORD)
  Next Record — KIND: Forms menu item; TYPE: N/A (action: NEXT_RECORD)
  Last Record — KIND: Forms menu item; TYPE: N/A (action: LAST_RECORD)
  Previous Block — KIND: Forms menu item; TYPE: N/A (action: PREVIOUS_BLOCK)
  Next Block — KIND: Forms menu item; TYPE: N/A (action: NEXT_BLOCK)

  **Modules menu items:**
  Employee Management — KIND: Forms menu item; TYPE: N/A (action: OPEN_FORM('HRMS_EMPLOYEE'))
  Payroll Processing — KIND: Forms menu item; TYPE: N/A (action: OPEN_FORM('HRMS_PAYROLL'))
  Leave Management — KIND: Forms menu item; TYPE: N/A (action: OPEN_FORM('HRMS_LEAVE'))
  Performance Reviews — KIND: Forms menu item; TYPE: N/A (action: OPEN_FORM('HRMS_PERFORMANCE'))
  Reports & Analytics — KIND: Forms menu item; TYPE: N/A (action: OPEN_FORM('HRMS_REPORTS'))
  System Admin — KIND: Forms menu item; TYPE: N/A (action: OPEN_FORM('HRMS_ADMIN'))

  **Admin menu items:**
  Change Password — KIND: Forms menu item; TYPE: N/A (action: SHOW_WINDOW('WIN_CHANGE_PWD'))
  System Parameters — KIND: Forms menu item; TYPE: N/A (requires ADMIN permission)
  User Management — KIND: Forms menu item; TYPE: N/A (requires ADMIN permission)

  **Help menu items:**
  Contents — KIND: Forms menu item; TYPE: N/A (action: WEB.SHOW_DOCUMENT)
  About HRMS — KIND: Forms menu item; TYPE: N/A (action: SHOW_ALERT('ALT_ABOUT'))
  Support — KIND: Forms menu item; TYPE: N/A (action: WEB.SHOW_DOCUMENT)

**METHODS:**
  **FILE-LEVEL EFFECT** [SOURCE: L1-60]
  - What it does: Documents, but does not implement, the MAIN_MENUBAR hierarchy described above — this .sql file is a human-readable export/diagram of the compiled .mmb menu module, not executable code.
  - Business rules: Modules menu items open other HRMS forms by name. Admin menu's "System Parameters" and "User Management" require ADMIN permission. Per the trailing comment, menu items are enabled/disabled at runtime based on PKG_SECURITY.has_permission() checks performed in WHEN-NEW-FORM-INSTANCE (not in this file).
  - Numbers & thresholds: None.
  - Security & error handling: Admin-tier menu items are permission-gated (ADMIN permission required), enforced elsewhere.
  - Data in/out: Input — none. Output — none; describes UI navigation bindings only.

**DEPENDENCIES:**
  Data touched:
  - Reads: None
  - Writes: None

  CALLS: HRMS_EMPLOYEE (OPEN_FORM) | EVIDENCE: INFERRED | SOURCE: L42
  CALLS: HRMS_PAYROLL (OPEN_FORM) | EVIDENCE: INFERRED | SOURCE: L43
  CALLS: HRMS_LEAVE (OPEN_FORM) | EVIDENCE: INFERRED | SOURCE: L44
  CALLS: HRMS_PERFORMANCE (OPEN_FORM) | EVIDENCE: INFERRED | SOURCE: L45
  CALLS: HRMS_REPORTS (OPEN_FORM) | EVIDENCE: INFERRED | SOURCE: L46
  CALLS: HRMS_ADMIN (OPEN_FORM) | EVIDENCE: INFERRED | SOURCE: L47
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: INFERRED | SOURCE: L60

  Config/env: None
  External integrations: WEB.SHOW_DOCUMENT (Help > Contents, Help > Support — external browser/document viewer)

**GAPS:**
  This file is a comment-only description of a compiled binary menu module; the actual WHEN-NEW-FORM-INSTANCE permission-check trigger and exact bound PL/SQL for each item (e.g. RUN_PRODUCT parameters) are not present — NOT_ANALYZED/EXTERNAL.

*[pipeline status — type: schema · pass: original · attempt: 1 · coverage: 100% (numbers 0/0 · tables 0/0 · units 1/1 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql ===

**IDENTITY:**
  KIND: trigger (schema script defining 3 database triggers)
  PURPOSE: Generic audit-trail triggers that record INSERT/UPDATE/DELETE changes on SALARY_RECORDS, status changes on LEAVE_REQUESTS, and INSERT/UPDATE/DELETE changes on DEPARTMENTS, via PKG_AUDIT.log_action.

**STRUCTURES:**
  TRG_SALARY_AUDIT — KIND: trigger; TYPE: N/A
  TRG_LEAVE_REQUEST_AUDIT — KIND: trigger; TYPE: N/A
  TRG_DEPARTMENT_AUDIT — KIND: trigger; TYPE: N/A

**METHODS:**
  **TRIGGER HRMS.TRG_SALARY_AUDIT (AFTER INSERT OR UPDATE OR DELETE ON HRMS.SALARY_RECORDS)** [SOURCE: L10-46]
  - What it does: Fires after any INSERT, UPDATE, or DELETE on SALARY_RECORDS. Builds a JSON snippet of the affected data (new values on INSERT, old+new on UPDATE, old values on DELETE) and calls PKG_AUDIT.log_action to persist the audit entry.
  - Business rules: INSERT audit captures emp_id, salary, and effective date. UPDATE audit captures both old and new base salary and active status. DELETE audit captures employee id and last known salary.
  - Numbers & thresholds: v_action is declared as VARCHAR2(10) [L14] — action labels ('INSERT'/'UPDATE'/'DELETE') must fit within 10 characters.
  - Security & error handling: None explicit — no exception handling in the trigger body; a failure in PKG_AUDIT.log_action would propagate and fail the triggering DML.
  - Data in/out: Inputs — :NEW/:OLD row values (EMP_ID, BASE_SALARY, EFFECTIVE_DATE, ACTIVE_FLAG, SALARY_ID, MODIFIED_BY) depending on operation. Output — calls PKG_AUDIT.log_action with table name 'SALARY_RECORDS', resolved SALARY_ID, action, actor, and old/new JSON.

  **TRIGGER HRMS.TRG_LEAVE_REQUEST_AUDIT (AFTER UPDATE OF STATUS ON HRMS.LEAVE_REQUESTS)** [SOURCE: L53-67]
  - What it does: Fires only when the STATUS column of a LEAVE_REQUESTS row is updated. Calls PKG_AUDIT.log_action with the old and new status values as JSON.
  - Business rules: Only STATUS column changes are audited on this table — updates to other columns (comments, dates, etc.) do not generate an audit record (enforced by the trigger's `UPDATE OF STATUS` clause, not by logic inside the body).
  - Numbers & thresholds: None.
  - Security & error handling: None explicit.
  - Data in/out: Inputs — :NEW.REQUEST_ID, :NEW.MODIFIED_BY, :OLD.STATUS, :NEW.STATUS. Output — calls PKG_AUDIT.log_action with table name 'LEAVE_REQUESTS', REQUEST_ID, action 'STATUS_CHANGE', actor, and old/new status JSON.

  **TRIGGER HRMS.TRG_DEPARTMENT_AUDIT (AFTER INSERT OR UPDATE OR DELETE ON HRMS.DEPARTMENTS)** [SOURCE: L73-94]
  - What it does: Fires after any INSERT, UPDATE, or DELETE on DEPARTMENTS. Determines the action type and calls PKG_AUDIT.log_action with the department id and the database session user as actor.
  - Business rules: Every structural change to a department record (create/modify/remove) must be captured in the audit log. Unlike the other two triggers, the actor is always the raw database USER — there is no application-supplied MODIFIED_BY column on this table.
  - Numbers & thresholds: None.
  - Security & error handling: None explicit.
  - Data in/out: Inputs — :NEW.DEPT_ID / :OLD.DEPT_ID depending on operation. Output — calls PKG_AUDIT.log_action with table name 'DEPARTMENTS', resolved DEPT_ID, action, and USER as actor (no old/new value JSON is passed for this trigger).

  **FILE-LEVEL EFFECT** [SOURCE: L1-94]
  - What it does: Running this script creates/replaces three AFTER triggers on HRMS.SALARY_RECORDS, HRMS.LEAVE_REQUESTS, and HRMS.DEPARTMENTS, wiring all subsequent DML on those tables into the shared PKG_AUDIT.log_action audit trail.
  - Business rules: Salary and department changes are audited on every INSERT/UPDATE/DELETE; leave request changes are audited only on STATUS updates.
  - Numbers & thresholds: v_action VARCHAR2(10) buffer used in both TRG_SALARY_AUDIT [L14] and TRG_DEPARTMENT_AUDIT [L77].
  - Security & error handling: None of the three triggers contain exception handlers — any failure in PKG_AUDIT.log_action aborts the triggering DML.
  - Data in/out: No file-level inputs/outputs beyond installing the three triggers described above.

**DEPENDENCIES:**
  Data touched:
  - Reads: None (uses :NEW/:OLD row images only, no separate SELECTs)
  - Writes: None directly (audit persistence is delegated to PKG_AUDIT.log_action)

  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L35
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L57
  CALLS: PKG_AUDIT.log_action | EVIDENCE: OBSERVED | SOURCE: L85

  Config/env: None
  External integrations: None

**GAPS:**
  NOT_ANALYZED: PKG_AUDIT.log_action's internals (target audit table, column list) — not in this file.
  UNKNOWN: full column definitions of SALARY_RECORDS, LEAVE_REQUESTS, and DEPARTMENTS — only the columns referenced by these triggers are visible here.

*[pipeline status — type: schema · pass: correction · attempt: 2 · coverage: 100% (numbers 1/1 · tables 3/3 · units 1/1 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_employees.sql ===

**IDENTITY:**
  KIND: trigger (schema script defining 3 database triggers)
  PURPOSE: Database-level triggers enforcing employee insert/update validation, audit-column defaults, status/department/job change history logging, and a soft-delete guard on HRMS.EMPLOYEES — duplicating logic that also exists in PKG_EMPLOYEE and Forms triggers.

**STRUCTURES:**
  TRG_EMP_BEFORE_INSERT — KIND: trigger; TYPE: N/A
  TRG_EMP_BEFORE_UPDATE — KIND: trigger; TYPE: N/A
  TRG_EMP_INSTEAD_OF_DELETE — KIND: trigger; TYPE: N/A (named as if INSTEAD OF, but declared as a BEFORE DELETE trigger — see GAPS)

**METHODS:**
  **TRIGGER HRMS.TRG_EMP_BEFORE_INSERT (BEFORE INSERT ON HRMS.EMPLOYEES)** [SOURCE: L12-66]
  - What it does: Fires before every EMPLOYEES insert. Defaults CREATED_BY/CREATED_DATE if not supplied, defaults ACTIVE_FLAG to 'Y' and EMPLOYMENT_STATUS to 'ACTIVE' if not supplied, validates HIRE_DATE is not too far in the future, and checks EMAIL uniqueness among active employees.
  - Business rules: CREATED_BY defaults to USER if NULL. CREATED_DATE defaults to SYSDATE if NULL. ACTIVE_FLAG defaults to 'Y' if NULL. EMPLOYMENT_STATUS defaults to 'ACTIVE' if NULL. HIRE_DATE cannot be more than 180 days in the future. Email uniqueness is checked only against employees where ACTIVE_FLAG = 'Y' — inactive/terminated employees' emails do not block reuse.
  - Numbers & thresholds: Maximum future hire date offset: SYSDATE + 180 (days) [L41]. Email-in-use check threshold: v_count > 0 [L59]. Error codes raised: -20501 (hire date too far in future) [L43], -20502 (email already in use) [L61].
  - Security & error handling: RAISE_APPLICATION_ERROR(-20501, 'Hire date cannot be more than 180 days in the future') if HIRE_DATE > SYSDATE + 180 [L41-45]. RAISE_APPLICATION_ERROR(-20502, 'Email address already in use: ' || :NEW.EMAIL) if an active employee already has that email (case-insensitive, via UPPER comparison) [L59-63]. Email uniqueness is also enforced by a unique constraint at the DB level; this trigger exists purely to give a friendlier error message.
  - Data in/out: Inputs — :NEW row values (CREATED_BY, CREATED_DATE, ACTIVE_FLAG, EMPLOYMENT_STATUS, HIRE_DATE, EMAIL). Reads EMPLOYEES (COUNT by UPPER(EMAIL) and ACTIVE_FLAG='Y'). Output — mutates :NEW.CREATED_BY/CREATED_DATE/ACTIVE_FLAG/EMPLOYMENT_STATUS in place, or raises an application error blocking the insert.

  **TRIGGER HRMS.TRG_EMP_BEFORE_UPDATE (BEFORE UPDATE ON HRMS.EMPLOYEES)** [SOURCE: L72-128]
  - What it does: Fires before every EMPLOYEES update. Sets MODIFIED_BY/MODIFIED_DATE, blocks direct reactivation of terminated employees, and logs EMPLOYMENT_STATUS, DEPT_ID, and JOB_ID changes to EMPLOYEE_HISTORY.
  - Business rules: MODIFIED_BY defaults to USER if not supplied. MODIFIED_DATE is always set to SYSDATE. A terminated employee (EMPLOYMENT_STATUS = 'TERMINATED') cannot be directly changed to 'ACTIVE' via plain UPDATE — must go through PKG_EMPLOYEE.rehire_employee instead. Every EMPLOYMENT_STATUS change is logged to EMPLOYEE_HISTORY as a STATUS_CHANGE event. Every DEPT_ID change (including to/from NULL) is logged as a DEPARTMENT_CHANGE event. Every JOB_ID change (including to/from NULL) is logged as a JOB_CHANGE event.
  - Numbers & thresholds: NULL-safe comparison sentinel -1 used for both DEPT_ID (NVL(:OLD.DEPT_ID,-1) != NVL(:NEW.DEPT_ID,-1)) [L104] and JOB_ID (NVL(:OLD.JOB_ID,-1) != NVL(:NEW.JOB_ID,-1)) [L117], so a NULL-to-value or value-to-NULL transition is still detected as a change. Error code raised: -20503 (illegal reactivation) [L85].
  - Security & error handling: RAISE_APPLICATION_ERROR(-20503, 'Cannot directly reactivate a terminated employee. Use the rehire process.') if :OLD.EMPLOYMENT_STATUS = 'TERMINATED' AND :NEW.EMPLOYMENT_STATUS = 'ACTIVE' [L83-87], blocking the update.
  - Data in/out: Inputs — :OLD/:NEW row values (EMPLOYMENT_STATUS, DEPT_ID, JOB_ID, MODIFIED_BY). Output — mutates :NEW.MODIFIED_BY/MODIFIED_DATE in place; inserts up to 3 rows into EMPLOYEE_HISTORY (HISTORY_ID via SEQ_EMP_HISTORY.NEXTVAL, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON) for status/department/job changes; or raises an application error blocking the update.

  **TRIGGER HRMS.TRG_EMP_INSTEAD_OF_DELETE (BEFORE DELETE ON HRMS.EMPLOYEES)** [SOURCE: L136-146]
  - What it does: Fires before any DELETE on EMPLOYEES and unconditionally raises an application error, preventing the delete from ever completing.
  - Business rules: Physical deletion of employee records is never permitted. Callers must instead set ACTIVE_FLAG = 'N' (soft delete) or run the formal termination process; the documented Forms workaround is to set ACTIVE_FLAG='N' then CLEAR_RECORD instead of DELETE_RECORD.
  - Numbers & thresholds: Error code raised: -20504 [L144].
  - Security & error handling: RAISE_APPLICATION_ERROR(-20504, 'Direct deletion not allowed. Use termination process or set ACTIVE_FLAG to N.') on every invocation [L144-145] — unconditionally blocks all deletes.
  - Data in/out: No inputs consumed. Output — none; always raises, blocking the delete.

  **FILE-LEVEL EFFECT** [SOURCE: L1-147]
  - What it does: Running this script creates/replaces three BEFORE-timing triggers on HRMS.EMPLOYEES that together enforce audit-column defaults, hire-date and email-uniqueness validation on insert, reactivation and change-history rules on update, and a hard block on physical deletion.
  - Business rules: See the three trigger entries above — defaults on insert, reactivation guard + 3-way history logging on update, unconditional delete block.
  - Numbers & thresholds: 180-day future hire-date limit [L41]; v_count > 0 email-in-use check [L59]; -1 NULL-safe sentinel for DEPT_ID/JOB_ID change detection [L104, L117]; error codes -20501, -20502, -20503, -20504 [L43, L61, L85, L144].
  - Security & error handling: This file is the primary DB-level enforcement point preventing terminated-employee reactivation and any physical deletion of EMPLOYEES rows; see individual trigger entries for exact error codes/messages.
  - Data in/out: No file-level inputs/outputs beyond installing the three triggers described above.

**DEPENDENCIES:**
  Data touched:
  - Reads: EMPLOYEES — COUNT(*) WHERE UPPER(EMAIL)=UPPER(:NEW.EMAIL) AND ACTIVE_FLAG='Y' (email uniqueness check) [L53-56]
  - Writes: EMPLOYEE_HISTORY — inserts HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON for STATUS_CHANGE [L92-100], DEPARTMENT_CHANGE [L105-113], and JOB_CHANGE [L118-126] events

  Config/env: None
  External integrations: None

**GAPS:**
  UNRESOLVED: TRG_EMP_INSTEAD_OF_DELETE is named as if it were an INSTEAD OF trigger, but is declared as `BEFORE DELETE ... FOR EACH ROW` on what appears to be a base table — Oracle only supports INSTEAD OF triggers on views. Unclear whether HRMS.EMPLOYEES is actually a view (not shown in this file) or the name is simply misleading/stale.
  NOT_ANALYZED: PKG_EMPLOYEE.rehire_employee, referenced only in a comment [L82] as the correct reactivation path — not called from this file, defined elsewhere.
  UNKNOWN: SEQ_EMP_HISTORY sequence definition (not in this file).

*[pipeline status — type: schema · pass: correction · attempt: 2 · coverage: 100% (numbers 6/6 · tables 2/2 · units 1/1 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/sequences/hrms_sequences.sql ===

**IDENTITY:**
  KIND: schema script (DDL)
  PURPOSE: Creates all surrogate-key sequences used across the HRMS schema's tables (employee, payroll, leave, performance, and system/audit domains)

**STRUCTURES:**
  **Core Employee sequences:**
  SEQ_DEPARTMENT — KIND: sequence; TYPE: NUMBER (START WITH 100, INCREMENT BY 1, NOCACHE)
  SEQ_LOCATION — KIND: sequence; TYPE: NUMBER (START WITH 100, INCREMENT BY 1, NOCACHE)
  SEQ_JOB_GRADE — KIND: sequence; TYPE: NUMBER (START WITH 100, INCREMENT BY 1, NOCACHE)
  SEQ_JOB_TITLE — KIND: sequence; TYPE: NUMBER (START WITH 100, INCREMENT BY 1, NOCACHE)
  SEQ_EMPLOYEE — KIND: sequence; TYPE: NUMBER (START WITH 10000, INCREMENT BY 1, NOCACHE)
  SEQ_EMP_HISTORY — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_DEPENDENT — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_EMERGENCY_CONTACT — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)

  **Employee number sequence:**
  SEQ_EMP_NUMBER — KIND: sequence; TYPE: NUMBER (START WITH 1000, INCREMENT BY 1, NOCACHE)

  **Payroll sequences:**
  SEQ_SALARY — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_PAY_ELEMENT — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_EMP_PAY_ELEMENT — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_PAY_PERIOD — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_PAYROLL_RUN — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_PAYROLL_DETAIL — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_TAX_BRACKET — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)

  **Leave sequences:**
  SEQ_LEAVE_TYPE — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_LEAVE_BALANCE — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_LEAVE_REQUEST — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_LEAVE_ACCRUAL — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_HOLIDAY — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)

  **Performance sequences:**
  SEQ_REVIEW_CYCLE — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_PERF_REVIEW — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_PERF_GOAL — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)

  **System sequences:**
  SEQ_AUDIT — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, CACHE 100)
  SEQ_NOTIFICATION — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_USER_SESSION — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_SYSTEM_PARAM — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)
  SEQ_LOOKUP — KIND: sequence; TYPE: NUMBER (START WITH 1, INCREMENT BY 1, NOCACHE)

**METHODS:**
  **FILE-LEVEL EFFECT** [SOURCE: L1-49]
  - What it does: Creates 29 standalone Oracle sequences in the HRMS schema as simple incrementing surrogate-key generators for every major table domain.
  - Business rules: None beyond the numbering scheme — simple incrementing integers only, no UUID/GUID, per the header comment.
  - Numbers & thresholds: SEQ_DEPARTMENT, SEQ_LOCATION, SEQ_JOB_GRADE, SEQ_JOB_TITLE — START WITH 100, INCREMENT BY 1, NOCACHE. SEQ_EMPLOYEE — START WITH 10000, INCREMENT BY 1, NOCACHE. SEQ_EMP_HISTORY, SEQ_DEPENDENT, SEQ_EMERGENCY_CONTACT — START WITH 1, INCREMENT BY 1, NOCACHE. SEQ_EMP_NUMBER — START WITH 1000, INCREMENT BY 1, NOCACHE. SEQ_SALARY, SEQ_PAY_ELEMENT, SEQ_EMP_PAY_ELEMENT, SEQ_PAY_PERIOD, SEQ_PAYROLL_RUN, SEQ_PAYROLL_DETAIL, SEQ_TAX_BRACKET — START WITH 1, INCREMENT BY 1, NOCACHE. SEQ_LEAVE_TYPE, SEQ_LEAVE_BALANCE, SEQ_LEAVE_REQUEST, SEQ_LEAVE_ACCRUAL, SEQ_HOLIDAY — START WITH 1, INCREMENT BY 1, NOCACHE. SEQ_REVIEW_CYCLE, SEQ_PERF_REVIEW, SEQ_PERF_GOAL — START WITH 1, INCREMENT BY 1, NOCACHE. SEQ_AUDIT — START WITH 1, INCREMENT BY 1, CACHE 100 (the only cached sequence in the file). SEQ_NOTIFICATION, SEQ_USER_SESSION, SEQ_SYSTEM_PARAM, SEQ_LOOKUP — START WITH 1, INCREMENT BY 1, NOCACHE.
  - Security & error handling: None.
  - Data in/out: Input — none. Output — 29 sequence objects created in the HRMS schema, available for NEXTVAL elsewhere (e.g. SEQ_EMP_HISTORY.NEXTVAL is consumed by TRG_EMP_BEFORE_UPDATE in trg_employees.sql).

**DEPENDENCIES:**
  Data touched:
  - Reads: None
  - Writes: None (creates schema objects, not table rows)

  Config/env: None
  External integrations: None

**GAPS:**
  Documented bug per inline comment (L19-20): SEQ_EMP_NUMBER is NOCACHE (gaps expected/normal), but generate_emp_number in PKG_EMPLOYEE is said to use MAX()+1 instead of this sequence, creating a race condition — PKG_EMPLOYEE.generate_emp_number is not present in this file, so this cannot be verified here — EXTERNAL/NOT_ANALYZED.

*[pipeline status — type: schema · pass: original · attempt: 1 · coverage: 100% (numbers 3/3 · tables 0/0 · units 1/1 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 6
Files delivered: 6
  Full coverage on first pass: 2
  Required correction: 4 -> ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql, ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_VALIDATION_LIB.pll.sql, ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql, ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_employees.sql
  Still incomplete after max attempts: 1 -> ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_VALIDATION_LIB.pll.sql
Raw source: 29518 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===