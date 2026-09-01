=== CHUNK METADATA ===
Chunk: 01            (chunk count is budget-driven, not a fixed file count)
Type group: forms
Expected files (1):
  1. [forms] ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml (14338 chars written)
Total source content: 23864 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml ===

**IDENTITY:**
  KIND: form
  PURPOSE: Employee maintenance form — master-detail form for personal info, job assignment, and compensation history (per header comment; header also claims dependent management, but no such block is present in this export — see GAPS).

**STRUCTURES:**
  HRMS_COMMON_LIB — KIND: Attached Library; TYPE: N/A
  HRMS_VALIDATION_LIB — KIND: Attached Library; TYPE: N/A
  HRMS_MENU — KIND: Menu Module (form-level MenuModule attribute); TYPE: N/A
  EMPLOYEE — KIND: Forms block; TYPE: N/A (source/DML target HRMS.EMPLOYEES)
  SALARY — KIND: Forms block; TYPE: N/A (query-only source HRMS.SALARY_RECORDS, detail of EMPLOYEE via EMP_SALARY_REL)
  EMP_SALARY_REL — KIND: Forms relation; TYPE: N/A (SALARY.EMP_ID = EMPLOYEE.EMP_ID, cascading delete, auto-query)

  **EMPLOYEE block items:**
  EMP_ID — KIND: Forms item (hidden, primary key); TYPE: Number
  EMP_NUMBER — KIND: Forms item (display-only after insert); TYPE: Char(20)
  FIRST_NAME — KIND: Forms item; TYPE: Char(50)
  LAST_NAME — KIND: Forms item; TYPE: Char(50)
  DATE_OF_BIRTH — KIND: Forms item; TYPE: Date
  GENDER — KIND: Forms item (List Item, poplist M/F/O); TYPE: Char(1)
  MARITAL_STATUS — KIND: Forms item (List Item, poplist SINGLE/MARRIED/DIVORCED/WIDOWED); TYPE: Char(10)
  EMAIL — KIND: Forms item; TYPE: Char(100)
  PHONE_WORK — KIND: Forms item; TYPE: Char(30)
  PHONE_MOBILE — KIND: Forms item; TYPE: Char(30)
  ADDRESS_LINE1 — KIND: Forms item; TYPE: Char(200)
  ADDRESS_LINE2 — KIND: Forms item; TYPE: Char(200)
  CITY — KIND: Forms item; TYPE: Char(100)
  STATE_PROVINCE — KIND: Forms item; TYPE: Char(100)
  POSTAL_CODE — KIND: Forms item; TYPE: Char(20)
  HIRE_DATE — KIND: Forms item; TYPE: Date
  DEPT_ID — KIND: Forms item (LOV_DEPARTMENTS); TYPE: Number
  DEPT_NAME_DISP — KIND: Forms item (non-database display item); TYPE: Char(100)
  JOB_ID — KIND: Forms item (LOV_JOB_TITLES); TYPE: Number
  JOB_TITLE_DISP — KIND: Forms item (non-database display item); TYPE: Char(100)
  MANAGER_EMP_ID — KIND: Forms item (LOV_MANAGERS); TYPE: Number
  MANAGER_NAME_DISP — KIND: Forms item (non-database display item); TYPE: Char(101)
  LOCATION_CODE — KIND: Forms item (LOV_LOCATIONS); TYPE: Char(10)
  EMPLOYMENT_TYPE — KIND: Forms item (List Item, poplist FULL_TIME/PART_TIME/CONTRACT/INTERN); TYPE: Char(20)
  EMPLOYMENT_STATUS — KIND: Forms item (List Item, poplist ACTIVE/ON_LEAVE/SUSPENDED/TERMINATED, update not allowed); TYPE: Char(20)
  TERMINATION_DATE — KIND: Forms item (update not allowed); TYPE: Date
  ACTIVE_FLAG — KIND: Forms item (hidden); TYPE: Char(1)
  CREATED_BY — KIND: Forms item (hidden, update not allowed); TYPE: Char(30)
  CREATED_DATE — KIND: Forms item (hidden, update not allowed); TYPE: Date
  MODIFIED_BY — KIND: Forms item (hidden); TYPE: Char(30)
  MODIFIED_DATE — KIND: Forms item (hidden); TYPE: Date

  **SALARY block items:**
  SALARY_ID — KIND: Forms item (hidden, primary key); TYPE: N/A
  EMP_ID — KIND: Forms item (hidden, FK to EMPLOYEE); TYPE: N/A
  EFFECTIVE_DATE — KIND: Forms item (update not allowed); TYPE: Date
  END_DATE — KIND: Forms item; TYPE: Date
  BASE_SALARY — KIND: Forms item (format $999,999,990.00); TYPE: Number
  CHANGE_REASON — KIND: Forms item; TYPE: Char
  CHANGE_PCT — KIND: Forms item (format 990.00%); TYPE: Number

  **LOVs / record groups:**
  LOV_DEPARTMENTS / RG_DEPARTMENTS — KIND: Forms LOV; TYPE: N/A (source: DEPT_ID, DEPT_CODE, DEPT_NAME, COST_CENTER FROM HRMS.DEPARTMENTS WHERE ACTIVE_FLAG='Y')
  LOV_JOB_TITLES / RG_JOB_TITLES — KIND: Forms LOV; TYPE: N/A (source: JOB_ID, JOB_CODE, JOB_TITLE, GRADE_NAME FROM HRMS.JOB_TITLES JOIN HRMS.JOB_GRADES WHERE ACTIVE_FLAG='Y')
  LOV_MANAGERS / RG_MANAGERS — KIND: Forms LOV; TYPE: N/A (source: EMP_ID, EMP_NUMBER, FIRST_NAME||' '||LAST_NAME FROM HRMS.EMPLOYEES WHERE EMPLOYMENT_STATUS='ACTIVE')
  LOV_LOCATIONS / RG_LOCATIONS — KIND: Forms LOV; TYPE: N/A (source: LOCATION_CODE, LOCATION_NAME, CITY, STATE_PROVINCE FROM HRMS.LOCATIONS WHERE ACTIVE_FLAG='Y')

  **Canvases / windows / alerts:**
  CVS_MAIN — KIND: Forms canvas (Tab, 700x500; pages TP_PERSONAL, TP_JOB, TP_DEPENDENTS, TP_HISTORY); TYPE: N/A
  CVS_TOOLBAR — KIND: Forms canvas (Horizontal Toolbar, 700x38); TYPE: N/A
  WIN_EMPLOYEE — KIND: Forms window (Document, 720x550, primary canvas CVS_MAIN); TYPE: N/A
  ALT_CONFIRM_EXIT — KIND: Forms alert (Caution, buttons Save/Discard/Cancel); TYPE: N/A
  ALT_CONFIRM_DELETE — KIND: Forms alert (Stop, buttons Yes/No); TYPE: N/A

**METHODS:**
  **TRIGGER WHEN-NEW-FORM-INSTANCE (form-level)** [SOURCE: L28-64]
  - What it does: Fires when the form instance is created. Validates the session via `PKG_SECURITY.is_session_valid(TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME)))`; on failure shows "Session expired. Please log in again." and raises FORM_TRIGGER_FAILURE. Sets the MDI window title to include `:GLOBAL.current_user`. Checks `PKG_SECURITY.has_permission(:GLOBAL.current_emp_id, 'EMPLOYEE', 'EDIT')`; if false, disables INSERT_ALLOWED/UPDATE_ALLOWED/DELETE_ALLOWED on the EMPLOYEE block. Sets EMPLOYEE block DEFAULT_WHERE to `EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y'`. Populates LOV record groups RG_DEPARTMENTS, RG_JOB_TITLES, RG_LOCATIONS, then navigates to the EMPLOYEE block and executes the query.
  - Business rules: Session must be valid or the form aborts. Only users with EDIT permission on the 'EMPLOYEE' object may insert/update/delete. Default query shows only ACTIVE employees with ACTIVE_FLAG='Y'.
  - Numbers & thresholds: None (values used are strings, not numeric literals).
  - Security & error handling: Session validated via PKG_SECURITY.is_session_valid before any other logic runs; permission-gated DML via PKG_SECURITY.has_permission; MESSAGE + RAISE FORM_TRIGGER_FAILURE on invalid session.
  - Data in/out: Input — GET_APPLICATION_PROPERTY(USERNAME), :GLOBAL.current_user, :GLOBAL.current_emp_id. Output — window title set, EMPLOYEE block DML/query properties set, LOVs populated, query executed (side effects only, no return value).

  **TRIGGER ON-ERROR (form-level)** [SOURCE: L66-88]
  - What it does: Fires on any Forms runtime error. Captures ERROR_CODE, ERROR_TYPE, ERROR_TEXT. Silently suppresses error 40202. Shows "No changes to save." for 40401. Shows "Record is locked by another user. Please try again." for 40501. For any other code, shows the raw `v_errtype-v_errcode: v_errmsg` and raises FORM_TRIGGER_FAILURE.
  - Business rules: Error 40202 ("Field is protected against update") is swallowed. Error 40401 ("No changes to save") and 40501 ("unable to reserve record"/record locked) get friendly messages without blocking. All other errors are surfaced raw and block via FORM_TRIGGER_FAILURE.
  - Numbers & thresholds: Error code 40202 (suppressed, "Field is protected against update"); error code 40401 ("No changes to save"); error code 50401... (verify) — actually 40501 ("Oracle error: unable to reserve record" / record locked).
  - Security & error handling: Central form error handler; distinguishes benign vs. blocking errors; blocking errors propagate FORM_TRIGGER_FAILURE.
  - Data in/out: Input — built-ins ERROR_CODE, ERROR_TYPE, ERROR_TEXT. Output — MESSAGE() calls, possible FORM_TRIGGER_FAILURE.

  **TRIGGER KEY-EXIT (form-level)** [SOURCE: L90-105]
  - What it does: Fires on the exit command. If `:SYSTEM.FORM_STATUS = 'CHANGED'`, shows alert ALT_CONFIRM_EXIT; if the result is ALERT_BUTTON1 ("Save") it commits the form via COMMIT_FORM; else if the result is ALERT_BUTTON2 ("Discard") — note this re-invokes SHOW_ALERT('ALT_CONFIRM_EXIT') a second time rather than reusing the first result — it clears the form with CLEAR_FORM(NO_VALIDATE); otherwise (Cancel) raises FORM_TRIGGER_FAILURE, aborting the exit. If not changed, or after handling, calls EXIT_FORM.
  - Business rules: Unsaved changes must be explicitly saved or discarded, or the exit is cancelled.
  - Numbers & thresholds: None.
  - Security & error handling: Cancel path aborts exit via FORM_TRIGGER_FAILURE; no other error handling.
  - Data in/out: Input — :SYSTEM.FORM_STATUS. Output — COMMIT_FORM / CLEAR_FORM(NO_VALIDATE) / EXIT_FORM side effects.

  **TRIGGER PRE-INSERT (EMPLOYEE block)** [SOURCE: L323-334]
  - What it does: Fires before inserting a new EMPLOYEE row. Sets EMP_ID from SEQ_EMPLOYEE.NEXTVAL, EMP_NUMBER from PKG_EMPLOYEE.generate_emp_number, ACTIVE_FLAG='Y', EMPLOYMENT_STATUS='ACTIVE', CREATED_BY=:GLOBAL.current_user, CREATED_DATE=SYSDATE.
  - Business rules: Every new employee record starts with ACTIVE_FLAG='Y' and EMPLOYMENT_STATUS='ACTIVE'.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Input — SEQ_EMPLOYEE sequence, PKG_EMPLOYEE.generate_emp_number, :GLOBAL.current_user, SYSDATE. Output — populates EMP_ID, EMP_NUMBER, ACTIVE_FLAG, EMPLOYMENT_STATUS, CREATED_BY, CREATED_DATE on the pending insert record.

  **TRIGGER PRE-UPDATE (EMPLOYEE block)** [SOURCE: L336-343]
  - What it does: Fires before updating an EMPLOYEE row; sets MODIFIED_BY=:GLOBAL.current_user and MODIFIED_DATE=SYSDATE.
  - Business rules: Every update stamps modifier and timestamp.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Input — :GLOBAL.current_user, SYSDATE. Output — MODIFIED_BY, MODIFIED_DATE set on the pending update record.

  **TRIGGER POST-QUERY (EMPLOYEE block)** [SOURCE: L345-368]
  - What it does: Fires after each row is fetched into the EMPLOYEE block. Looks up DEPT_NAME from DEPARTMENTS by DEPT_ID into DEPT_NAME_DISP; JOB_TITLE from JOB_TITLES by JOB_ID into JOB_TITLE_DISP; FIRST_NAME||' '||LAST_NAME from EMPLOYEES by MANAGER_EMP_ID into MANAGER_NAME_DISP. Each lookup independently defaults its display item to NULL if NO_DATA_FOUND.
  - Business rules: Display-only enrichment; unresolved references show blank rather than erroring the query.
  - Numbers & thresholds: None.
  - Security & error handling: Each lookup wrapped in its own BEGIN/EXCEPTION WHEN NO_DATA_FOUND block.
  - Data in/out: Input — EMPLOYEE.DEPT_ID, EMPLOYEE.JOB_ID, EMPLOYEE.MANAGER_EMP_ID. Output — EMPLOYEE.DEPT_NAME_DISP, EMPLOYEE.JOB_TITLE_DISP, EMPLOYEE.MANAGER_NAME_DISP.

  **TRIGGER WHEN-VALIDATE-ITEM (EMPLOYEE block, multi-item dispatch)** [SOURCE: L370-413]
  - What it does: Fires on item validation (item exit) for any EMPLOYEE block item; captures the firing item name into `v_item VARCHAR2(60) := :SYSTEM.TRIGGER_ITEM` and dispatches by value. For `EMPLOYEE.EMAIL`: if non-null and `PKG_VALIDATION.validate_email_format` fails, shows "Invalid email format" and raises FORM_TRIGGER_FAILURE. For `EMPLOYEE.HIRE_DATE`: if HIRE_DATE > SYSDATE + 90, shows "Hire date cannot be more than 90 days in the future" and raises FORM_TRIGGER_FAILURE. For `EMPLOYEE.DEPT_ID`: looks up DEPT_NAME from DEPARTMENTS where DEPT_ID matches and ACTIVE_FLAG='Y'; on NO_DATA_FOUND shows "Invalid department" and raises FORM_TRIGGER_FAILURE. For `EMPLOYEE.JOB_ID`: looks up JOB_TITLE from JOB_TITLES where JOB_ID matches and ACTIVE_FLAG='Y'; on NO_DATA_FOUND shows "Invalid job title" and raises FORM_TRIGGER_FAILURE.
  - Business rules: Email, if provided, must pass PKG_VALIDATION.validate_email_format. Hire date may not be more than 90 days in the future. DEPT_ID must reference an active (ACTIVE_FLAG='Y') department. JOB_ID must reference an active (ACTIVE_FLAG='Y') job title.
  - Numbers & thresholds: `v_item` local variable declared as VARCHAR2(60) — max length 60 for the trigger-item name buffer; hire-date future tolerance = SYSDATE + 90 (days).
  - Security & error handling: Each failing branch calls MESSAGE() then raises FORM_TRIGGER_FAILURE, blocking navigation out of the item; DEPT_ID/JOB_ID lookups wrapped in BEGIN/EXCEPTION WHEN NO_DATA_FOUND.
  - Data in/out: Input — :SYSTEM.TRIGGER_ITEM, EMPLOYEE.EMAIL, EMPLOYEE.HIRE_DATE, EMPLOYEE.DEPT_ID, EMPLOYEE.JOB_ID. Output — EMPLOYEE.DEPT_NAME_DISP, EMPLOYEE.JOB_TITLE_DISP updated as side effects; no return value (validation-only).

**DEPENDENCIES:**
  Data touched:
  - Reads: HRMS.EMPLOYEES — EMPLOYEE block query source
  - Reads: HRMS.SALARY_RECORDS — SALARY block query source (read-only: InsertAllowed/UpdateAllowed/DeleteAllowed all "No", no DML target)
  - Reads: DEPARTMENTS — POST-QUERY and WHEN-VALIDATE-ITEM lookups for DEPT_NAME_DISP / department validation
  - Reads: JOB_TITLES — POST-QUERY and WHEN-VALIDATE-ITEM lookups for JOB_TITLE_DISP / job title validation
  - Reads: EMPLOYEES — POST-QUERY manager-name lookup by MANAGER_EMP_ID
  - Reads: HRMS.DEPARTMENTS — LOV_DEPARTMENTS record group source
  - Reads: HRMS.JOB_TITLES, HRMS.JOB_GRADES — LOV_JOB_TITLES record group source (joined)
  - Reads: HRMS.EMPLOYEES — LOV_MANAGERS record group source
  - Reads: HRMS.LOCATIONS — LOV_LOCATIONS record group source
  - Reads: SEQ_EMPLOYEE — sequence consumed in PRE-INSERT
  - Writes: HRMS.EMPLOYEES — EMPLOYEE block DML target (insert/update/delete)

  CALLS: PKG_SECURITY.is_session_valid | EVIDENCE: OBSERVED | SOURCE: L35
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L45
  CALLS: PKG_EMPLOYEE.generate_emp_number | EVIDENCE: OBSERVED | SOURCE: L327
  CALLS: PKG_VALIDATION.validate_email_format | EVIDENCE: OBSERVED | SOURCE: L377
  IMPORTS: HRMS_COMMON_LIB | EVIDENCE: OBSERVED | SOURCE: L22
  IMPORTS: HRMS_VALIDATION_LIB | EVIDENCE: OBSERVED | SOURCE: L23
  IMPORTS: HRMS_MENU | EVIDENCE: OBSERVED | SOURCE: L16

  Config/env: None.
  External integrations: None.

**GAPS:**
  KEY-EXIT trigger calls `SHOW_ALERT('ALT_CONFIRM_EXIT')` twice (once in the IF, again in the ELSIF) instead of storing the result once — UNRESOLVED, likely re-displays the alert a second time on the Discard path rather than reflecting the original click.
  Header comment claims 5 data blocks (EMPLOYEE, SALARY, DEPENDENTS, EMERGENCY_CONTACTS, EMP_HISTORY) and 8 LOVs (incl. Status, Gender, Marital, Country), but this export only defines the EMPLOYEE and SALARY blocks and 4 LOVs (Department, Job Title, Manager, Location) — the DEPENDENTS/EMERGENCY_CONTACTS/EMP_HISTORY blocks, TP_DEPENDENTS/TP_HISTORY tab content, and the remaining 4 LOVs are NOT_ANALYZED / UNKNOWN (not present in this file, possibly defined elsewhere or omitted from the export).
  Implementations of PKG_SECURITY, PKG_EMPLOYEE, PKG_VALIDATION, HRMS_COMMON_LIB, HRMS_VALIDATION_LIB, and HRMS_MENU are EXTERNAL to this file.

*[pipeline status — type: forms · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 11, 120, 145, 150, 170, 195, 210, 220, 250, 255, 280, 300, 305, 330, 38]*

---

=== CHUNK STATUS ===
Files expected: 1
Files delivered: 1
  Full coverage on first pass: 0
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml
  Still incomplete after max attempts: 1 -> ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml
Raw source: 23864 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===