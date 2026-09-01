=== CHUNK METADATA ===
Chunk: 02            (chunk count is budget-driven, not a fixed file count)
Type group: forms
Expected files (4):
  1. [forms] ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml (8045 chars written)
  2. [forms] ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml (3978 chars written)
  3. [forms] ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml (7256 chars written)
  4. [forms] ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml (7336 chars written)
Total source content: 26791 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml ===

**IDENTITY:**
  KIND: form
  PURPOSE: Employee leave management — submit leave requests, cancel pending/approved requests, view leave balances, and (per header comment) approve requests and view a team calendar.

**STRUCTURES:**
  LEAVE_REQUEST — KIND: Forms block; TYPE: N/A (query block on HRMS.LEAVE_REQUESTS)
  **LEAVE_REQUEST items:**
  REQUEST_ID — KIND: Forms item; TYPE: N/A (hidden, primary key)
  EMP_ID — KIND: Forms item; TYPE: N/A (hidden)
  LEAVE_TYPE_NAME_DISP — KIND: Forms item; TYPE: Char (display-only, non-database)
  START_DATE — KIND: Forms item; TYPE: Date
  END_DATE — KIND: Forms item; TYPE: Date
  TOTAL_DAYS — KIND: Forms item; TYPE: Number
  STATUS — KIND: Forms item; TYPE: Char
  REASON — KIND: Forms item; TYPE: Char
  BTN_CANCEL_REQUEST — KIND: Forms item (Push Button); TYPE: N/A

  NEW_REQUEST — KIND: Forms block; TYPE: N/A (control block, no query data source, insert-only)
  **NEW_REQUEST items:**
  NR_LEAVE_TYPE_ID — KIND: Forms item; TYPE: Number (LOV_LEAVE_TYPES)
  NR_LEAVE_TYPE_DISP — KIND: Forms item; TYPE: Char (display-only)
  NR_START_DATE — KIND: Forms item; TYPE: Date
  NR_END_DATE — KIND: Forms item; TYPE: Date
  NR_HALF_DAY — KIND: Forms item (Check Box); TYPE: Char (Y/N)
  NR_REASON — KIND: Forms item; TYPE: Char (max length 500, multi-line)
  NR_CALC_DAYS — KIND: Forms item; TYPE: Number (display-only)
  NR_BALANCE_DISP — KIND: Forms item; TYPE: Number (display-only)
  BTN_SUBMIT — KIND: Forms item (Push Button); TYPE: N/A

  LEAVE_BALANCE — KIND: Forms block; TYPE: N/A (query block on HRMS.LEAVE_BALANCES)
  **LEAVE_BALANCE items:**
  LEAVE_TYPE_NAME_DISP — KIND: Forms item; TYPE: N/A (display-only)
  OPENING_BALANCE — KIND: Forms item; TYPE: Number
  ACCRUED — KIND: Forms item; TYPE: Number
  USED — KIND: Forms item; TYPE: Number
  PENDING — KIND: Forms item; TYPE: Number
  AVAILABLE — KIND: Forms item; TYPE: Number

  LOV_LEAVE_TYPES — KIND: Forms LOV; TYPE: N/A
  RG_LEAVE_TYPES — KIND: Forms record group; TYPE: N/A (backs LOV_LEAVE_TYPES)
  CVS_MAIN — KIND: Forms canvas (Tab); TYPE: N/A; TabPages: TP_MY_REQUESTS ("My Requests"), TP_NEW_REQUEST ("Submit Request"), TP_APPROVALS ("Pending Approvals"), TP_CALENDAR ("Team Calendar")
  WIN_LEAVE — KIND: Forms window; TYPE: N/A
  ALT_CONFIRM_CANCEL — KIND: Forms alert; TYPE: N/A

**METHODS:**
  **TRIGGER WHEN-NEW-FORM-INSTANCE (form-level)** [SOURCE: L21-50]
  - What it does: Fires when the form instance is created. Validates the session via PKG_SECURITY.is_session_valid using the numeric username; sets the MDI window title to include the current user; restricts LEAVE_REQUEST's default query to the current employee's own requests ordered by CREATED_DATE DESC; populates the leave-type LOV group; queries LEAVE_REQUEST then LEAVE_BALANCE, and returns focus to LEAVE_REQUEST.
  - Business rules: Session must be valid or the form is blocked. Default LEAVE_REQUEST view shows only EMP_ID = current employee, newest first.
  - Numbers & thresholds: None.
  - Security & error handling: On invalid session, shows "Session expired." and raises FORM_TRIGGER_FAILURE, aborting form load.
  - Data in/out: Input — GET_APPLICATION_PROPERTY(USERNAME), :GLOBAL.current_user, :GLOBAL.current_emp_id. Output — window title set, LEAVE_REQUEST/LEAVE_BALANCE blocks queried, RG_LEAVE_TYPES populated.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_CANCEL_REQUEST, on LEAVE_REQUEST block)** [SOURCE: L75-91]
  - What it does: Fires on click. Verifies the selected request's STATUS is PENDING or APPROVED; if not, blocks with a message. Shows a confirmation alert (ALT_CONFIRM_CANCEL); on confirmation (ALERT_BUTTON1), calls PKG_LEAVE.cancel_leave_request with the request ID, a fixed cancellation reason, and the current user, then re-queries the block.
  - Business rules: Only requests with STATUS = 'PENDING' or 'APPROVED' can be cancelled.
  - Numbers & thresholds: None.
  - Security & error handling: Status guard raises FORM_TRIGGER_FAILURE with message "Only pending or approved requests can be cancelled." if violated; no explicit exception handling around the PKG_LEAVE call.
  - Data in/out: Input — :LEAVE_REQUEST.REQUEST_ID, :LEAVE_REQUEST.STATUS, :GLOBAL.current_user; literal reason string 'Cancelled by employee'. Output — leave request cancelled via package call; block re-queried; confirmation message shown.

  **TRIGGER POST-QUERY (on LEAVE_REQUEST block)** [SOURCE: L94-106]
  - What it does: Fires per fetched row. Looks up LEAVE_TYPE_NAME from LEAVE_TYPES joined to LEAVE_REQUESTS by LEAVE_TYPE_ID, filtered to the current row's REQUEST_ID, into the display item LEAVE_TYPE_NAME_DISP.
  - Business rules: None beyond display resolution.
  - Numbers & thresholds: None.
  - Security & error handling: NO_DATA_FOUND is caught and defaults the display value to 'Unknown'; no other exception handling.
  - Data in/out: Input — :LEAVE_REQUEST.REQUEST_ID. Output — :LEAVE_REQUEST.LEAVE_TYPE_NAME_DISP populated.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_SUBMIT, on NEW_REQUEST block)** [SOURCE: L133-170]
  - What it does: Fires on click. Validates leave type, start date, and end date are not null (each missing field blocks with its own message). Calls PKG_LEAVE.submit_leave_request with employee ID, leave type, start/end dates, half-day flag (defaulted to 'N' via NVL), reason, and current user; shows a success message with the new request ID; clears the entry block without validation; re-queries and navigates back to LEAVE_REQUEST.
  - Business rules: NR_LEAVE_TYPE_ID, NR_START_DATE, and NR_END_DATE are required fields. Half-day flag defaults to 'N' when null.
  - Numbers & thresholds: None (NR_REASON has a 500-character maximum length, enforced at the item level — see STRUCTURES).
  - Security & error handling: Each missing required field raises FORM_TRIGGER_FAILURE with a specific message; no exception handling around the PKG_LEAVE call itself.
  - Data in/out: Input — :GLOBAL.current_emp_id, :NEW_REQUEST.NR_LEAVE_TYPE_ID/NR_START_DATE/NR_END_DATE/NR_HALF_DAY/NR_REASON, :GLOBAL.current_user. Output — v_request_id from PKG_LEAVE.submit_leave_request; block cleared; LEAVE_REQUEST re-queried.

  **FILE-LEVEL EFFECT (form layout: LOV, canvas, window, alert)** [SOURCE: L193-217]
  - What it does: Defines LOV_LEAVE_TYPES as a popup list (sourced from RG_LEAVE_TYPES querying HRMS.LEAVE_TYPES where ACTIVE_FLAG='Y', ordered by name), mapping LEAVE_TYPE_ID/LEAVE_TYPE_NAME back into NEW_REQUEST.NR_LEAVE_TYPE_ID/NR_LEAVE_TYPE_DISP; defines the tabbed CVS_MAIN canvas and the WIN_LEAVE document window; defines the ALT_CONFIRM_CANCEL caution alert with Yes/No buttons.
  - Business rules: LOV only offers leave types where ACTIVE_FLAG = 'Y'.
  - Numbers & thresholds: LOV_LEAVE_TYPES popup Width=350, Height=250. CVS_MAIN tab canvas Width=700, Height=480. WIN_LEAVE window Width=720, Height=520.
  - Security & error handling: None.
  - Data in/out: Output — UI chrome only (no data written).

**DEPENDENCIES:**
  Data touched:
  - Reads: HRMS.LEAVE_REQUESTS — LEAVE_REQUEST block query; LEAVE_TYPES — POST-QUERY lookup and LOV record group; HRMS.LEAVE_BALANCES — LEAVE_BALANCE block query
  - Writes: None (inserts/cancellations are performed inside PKG_LEAVE, not directly by this form)

  CALLS: PKG_SECURITY.is_session_valid | EVIDENCE: OBSERVED | SOURCE: L25
  CALLS: PKG_LEAVE.cancel_leave_request | EVIDENCE: OBSERVED | SOURCE: L84
  CALLS: PKG_LEAVE.submit_leave_request | EVIDENCE: OBSERVED | SOURCE: L152
  IMPORTS: HRMS_COMMON_LIB | EVIDENCE: OBSERVED | SOURCE: L19

  Config/env: None
  External integrations: None

**GAPS:**
  Header comment (L11-12) states 5 data blocks (including PENDING_APPROVAL, TEAM_CAL) and 3 LOVs (including Employee, Half-Day Period), but only 3 blocks (LEAVE_REQUEST, NEW_REQUEST, LEAVE_BALANCE) and 1 LOV (LOV_LEAVE_TYPES) are present in this source — PENDING_APPROVAL, TEAM_CAL, and the Employee/Half-Day Period LOVs are NOT_ANALYZED (not in provided source). TP_APPROVALS and TP_CALENDAR tab pages exist on CVS_MAIN but have no associated block/items shown — UNKNOWN.

*[pipeline status — type: forms · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 100, 110, 120, 150, 20, 200, 25, 30, 300, 60, 80, 990.0]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml ===

**IDENTITY:**
  KIND: form
  PURPOSE: Login form — authenticates a user against PKG_SECURITY and opens the main HRMS menu on success.

**STRUCTURES:**
  LOGIN — KIND: Forms block; TYPE: N/A (control block, no query data source)
  **LOGIN items:**
  COMPANY_LOGO — KIND: Forms item (Image); TYPE: Char (GIF)
  USERNAME — KIND: Forms item; TYPE: Char (max length 100, required)
  PASSWORD — KIND: Forms item; TYPE: Char (max length 100, required, ConcealData=Yes)
  ERROR_MSG — KIND: Forms item (Display Item); TYPE: Char (max length 200)
  BTN_LOGIN — KIND: Forms item (Push Button); TYPE: N/A

  CVS_LOGIN — KIND: Forms canvas (Content); TYPE: N/A
  WIN_LOGIN — KIND: Forms window; TYPE: N/A

**METHODS:**
  **TRIGGER WHEN-NEW-FORM-INSTANCE (form-level)** [SOURCE: L19-27]
  - What it does: Sets the MDI window title to "HRMS Login", sets WIN_LOGIN to NORMAL state, and moves focus to LOGIN.USERNAME.
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Output — window title/state set; cursor positioned on USERNAME.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_LOGIN, on LOGIN block)** [SOURCE: L62-104]
  - What it does: Fires on click. Clears any prior error message. Requires both USERNAME and PASSWORD to be non-null. Calls PKG_SECURITY.authenticate with username, password, and the client host; on success stores the returned session ID and username into :GLOBAL.session_id/:GLOBAL.current_user, looks up the active employee's EMP_ID from EMPLOYEES by case-insensitive email match (first row only), and opens HRMS_MENU (ACTIVATE, SESSION).
  - Business rules: Username and password are required. Employee lookup restricts to EMPLOYMENT_STATUS = 'ACTIVE' and takes only the first matching row (ROWNUM = 1).
  - Numbers & thresholds: None.
  - Security & error handling: Per the file's header comment, the password field is transmitted in cleartext (a known Forms-applet limitation), there is no account lockout after repeated failed attempts, and no CAPTCHA/2FA is supported. Missing username/password blocks with a message and FORM_TRIGGER_FAILURE. Any exception during authentication or lookup (WHEN OTHERS) is swallowed into a generic "Invalid username or password." message, clears the password field, refocuses it, and raises FORM_TRIGGER_FAILURE — this masks the real error (including unexpected DB errors) as an auth failure.
  - Data in/out: Input — :LOGIN.USERNAME, :LOGIN.PASSWORD, GET_APPLICATION_PROPERTY(CLIENT_HOST). Output — :GLOBAL.session_id, :GLOBAL.current_user, :GLOBAL.current_emp_id set; HRMS_MENU form opened.

  **TRIGGER KEY-NEXT-ITEM (on LOGIN block)** [SOURCE: L108-118]
  - What it does: Fires on the Next-Item key. If the cursor is on LOGIN.PASSWORD, simulates pressing the login button (DO_KEY('WHEN-BUTTON-PRESSED')); otherwise performs normal NEXT_ITEM navigation.
  - Business rules: Pressing Enter/Next-Item while in the password field submits the login.
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Input — :SYSTEM.CURSOR_ITEM. Output — either triggers login or advances to the next item.

  **FILE-LEVEL EFFECT (form layout: canvas, window)** [SOURCE: L121-128]
  - What it does: Defines the CVS_LOGIN content canvas (white background) and the WIN_LOGIN dialog window (non-closeable, non-minimizable, non-maximizable, movable, non-resizable) as the primary canvas.
  - Business rules: None.
  - Numbers & thresholds: CVS_LOGIN canvas Width=700, Height=300. WIN_LOGIN window Width=700, Height=320.
  - Security & error handling: None.
  - Data in/out: Output — UI chrome only.

**DEPENDENCIES:**
  Data touched:
  - Reads: EMPLOYEES — EMP_ID lookup by UPPER(EMAIL) = UPPER(username), EMPLOYMENT_STATUS = 'ACTIVE', ROWNUM = 1
  - Writes: None

  CALLS: PKG_SECURITY.authenticate | EVIDENCE: OBSERVED | SOURCE: L75
  CALLS: HRMS_MENU (OPEN_FORM) | EVIDENCE: OBSERVED | SOURCE: L93

  Config/env: None
  External integrations: None

**GAPS:** None

*[pipeline status — type: forms · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 120, 155, 195, 20, 230, 24, 250, 280, 30, 60, 80]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml ===

**IDENTITY:**
  KIND: form
  PURPOSE: MDI parent/main-menu form — application shell after login; sets permission-based menu item visibility and launches all HRMS child modules.

**STRUCTURES:**
  MENU_CONTROL — KIND: Forms block; TYPE: N/A (control block, no query data source)
  **MENU_CONTROL items:**
  WELCOME_TEXT — KIND: Forms item (Display Item); TYPE: Char
  USER_INFO — KIND: Forms item (Display Item); TYPE: Char
  BTN_EMPLOYEES — KIND: Forms item (Push Button); TYPE: N/A
  BTN_PAYROLL — KIND: Forms item (Push Button); TYPE: N/A
  BTN_LEAVE — KIND: Forms item (Push Button); TYPE: N/A
  BTN_PERFORMANCE — KIND: Forms item (Push Button); TYPE: N/A
  BTN_REPORTS — KIND: Forms item (Push Button); TYPE: N/A
  BTN_LOGOUT — KIND: Forms item (Push Button); TYPE: N/A

  CVS_MAIN — KIND: Forms canvas (Content); TYPE: N/A
  WIN_MAIN — KIND: Forms window; TYPE: N/A
  MENU_MAIN — KIND: Forms menu module; TYPE: N/A
  **MENU_MAIN structure:**
  FILE_MENU ("File") — KIND: Forms menu; TYPE: N/A — item MI_LOGOUT
  MODULES_MENU ("Modules") — KIND: Forms menu; TYPE: N/A — items MI_EMPLOYEES, MI_PAYROLL, MI_LEAVE, MI_PERFORMANCE, MI_REPORTS
  ADMIN_MENU ("Admin") — KIND: Forms menu; TYPE: N/A — items MI_ADMIN, MI_CHANGE_PWD
  HELP_MENU ("Help") — KIND: Forms menu; TYPE: N/A — item MI_ABOUT

**METHODS:**
  **TRIGGER WHEN-NEW-FORM-INSTANCE (form-level)** [SOURCE: L18-41]
  - What it does: Sets the MDI window title to include app version, current user, and session ID. Checks PKG_SECURITY.has_permission for the current employee against PAYROLL/VIEW, ADMIN/VIEW, and REPORTS/VIEW; for each missing permission, disables the corresponding menu item (MI_PAYROLL, MI_ADMIN, MI_REPORTS). Navigates to MENU_CONTROL.
  - Business rules: Menu items for Payroll, Admin, and Reports modules are enabled only if the current employee has the respective VIEW permission.
  - Numbers & thresholds: None.
  - Security & error handling: Permission-gated menu item disabling via PKG_SECURITY.has_permission; no explicit error handling.
  - Data in/out: Input — :GLOBAL.current_emp_id, :GLOBAL.current_user, :GLOBAL.session_id. Output — window title set; MI_PAYROLL/MI_ADMIN/MI_REPORTS ENABLED property possibly set to PROPERTY_FALSE.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_EMPLOYEES)** [SOURCE: L60-66]
  - What it does: Opens HRMS_EMPLOYEE (ACTIVATE, SESSION).
  - Business rules: None (no permission check).
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Output — HRMS_EMPLOYEE form opened.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_PAYROLL)** [SOURCE: L72-82]
  - What it does: Checks PKG_SECURITY.has_permission for PAYROLL/VIEW; if denied, blocks with "Access denied." Otherwise opens HRMS_PAYROLL (ACTIVATE, SESSION).
  - Business rules: Requires PAYROLL/VIEW permission.
  - Numbers & thresholds: None.
  - Security & error handling: Denies access and raises FORM_TRIGGER_FAILURE if permission check fails.
  - Data in/out: Input — :GLOBAL.current_emp_id. Output — HRMS_PAYROLL form opened.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_LEAVE)** [SOURCE: L88-94]
  - What it does: Opens HRMS_LEAVE (ACTIVATE, SESSION).
  - Business rules: None (no permission check).
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Output — HRMS_LEAVE form opened.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_PERFORMANCE)** [SOURCE: L100-106]
  - What it does: Opens HRMS_PERFORMANCE (ACTIVATE, SESSION).
  - Business rules: None (no permission check).
  - Numbers & thresholds: None.
  - Security & error handling: None.
  - Data in/out: Output — HRMS_PERFORMANCE form opened.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_REPORTS)** [SOURCE: L112-122]
  - What it does: Checks PKG_SECURITY.has_permission for REPORTS/VIEW; if denied, blocks with "Access denied." Otherwise opens HRMS_REPORTS (ACTIVATE, SESSION).
  - Business rules: Requires REPORTS/VIEW permission.
  - Numbers & thresholds: None.
  - Security & error handling: Denies access and raises FORM_TRIGGER_FAILURE if permission check fails.
  - Data in/out: Input — :GLOBAL.current_emp_id. Output — HRMS_REPORTS form opened.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_LOGOUT)** [SOURCE: L128-135]
  - What it does: Calls PKG_SECURITY.logout with the numeric session ID, then exits the form (EXIT_FORM).
  - Business rules: None.
  - Numbers & thresholds: None.
  - Security & error handling: Terminates the session server-side before exiting the client.
  - Data in/out: Input — :GLOBAL.session_id. Output — session logged out; form exits.

  **MENU COMMANDS (MENU_MAIN menu items)** [SOURCE: L146-172]
  - What it does: MI_LOGOUT calls PKG_SECURITY.logout(session_id) then EXIT_FORM. MI_EMPLOYEES/MI_PAYROLL/MI_LEAVE/MI_PERFORMANCE/MI_REPORTS each OPEN_FORM the corresponding module (HRMS_EMPLOYEE/HRMS_PAYROLL/HRMS_LEAVE/HRMS_PERFORMANCE/HRMS_REPORTS) with ACTIVATE, SESSION. MI_ADMIN opens HRMS_ADMIN (ACTIVATE, SESSION). MI_CHANGE_PWD shows the WIN_CHANGE_PWD window. MI_ABOUT displays a static message.
  - Business rules: These are direct menu-bar equivalents of the module buttons; unlike the BTN_PAYROLL/BTN_REPORTS buttons, the menu items themselves carry no visible permission check in their CommandText (permission is only enforced indirectly by disabling MI_PAYROLL/MI_ADMIN/MI_REPORTS at form startup).
  - Numbers & thresholds: None.
  - Security & error handling: None beyond the startup-time ENABLED-property gating described in WHEN-NEW-FORM-INSTANCE.
  - Data in/out: Output — target forms opened, session logged out, or WIN_CHANGE_PWD window shown, per item.

  **FILE-LEVEL EFFECT (form layout: canvas, window)** [SOURCE: L139-143]
  - What it does: Defines the CVS_MAIN content canvas and the WIN_MAIN document window as the primary canvas.
  - Business rules: None.
  - Numbers & thresholds: CVS_MAIN canvas Width=740, Height=400. WIN_MAIN window Width=760, Height=420.
  - Security & error handling: None.
  - Data in/out: Output — UI chrome only.

**DEPENDENCIES:**
  Data touched:
  - Reads: None
  - Writes: None

  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L26
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L30
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L34
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L75
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L115
  CALLS: PKG_SECURITY.logout | EVIDENCE: OBSERVED | SOURCE: L131
  CALLS: PKG_SECURITY.logout | EVIDENCE: OBSERVED | SOURCE: L149
  CALLS: HRMS_EMPLOYEE (OPEN_FORM) | EVIDENCE: OBSERVED | SOURCE: L63
  CALLS: HRMS_PAYROLL (OPEN_FORM) | EVIDENCE: OBSERVED | SOURCE: L79
  CALLS: HRMS_LEAVE (OPEN_FORM) | EVIDENCE: OBSERVED | SOURCE: L91
  CALLS: HRMS_PERFORMANCE (OPEN_FORM) | EVIDENCE: OBSERVED | SOURCE: L103
  CALLS: HRMS_REPORTS (OPEN_FORM) | EVIDENCE: OBSERVED | SOURCE: L119
  CALLS: HRMS_ADMIN (OPEN_FORM) | EVIDENCE: OBSERVED | SOURCE: L165
  IMPORTS: HRMS_COMMON_LIB | EVIDENCE: OBSERVED | SOURCE: L16

  Config/env: None
  External integrations: None

**GAPS:**
  MI_CHANGE_PWD's CommandText calls SHOW_WINDOW('WIN_CHANGE_PWD') (L167), but WIN_CHANGE_PWD is not defined anywhere in this file — UNKNOWN/likely defined in another form module not in this source.

*[pipeline status — type: forms · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 120, 14, 15, 20, 200, 2024.03, 270, 30, 490, 50, 60, 600, 70]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml ===

**IDENTITY:**
  KIND: form
  PURPOSE: Payroll processing form — pay-period listing, payroll run creation/calculation/approval, and (per header comment) pay-detail/payslip viewing.

**STRUCTURES:**
  PAY_PERIOD — KIND: Forms block; TYPE: N/A (query block on HRMS.PAY_PERIODS)
  **PAY_PERIOD items:**
  PERIOD_ID — KIND: Forms item; TYPE: N/A (hidden, primary key)
  PERIOD_NAME — KIND: Forms item; TYPE: Char
  PERIOD_START_DATE — KIND: Forms item; TYPE: Date
  PERIOD_END_DATE — KIND: Forms item; TYPE: Date
  PAY_DATE — KIND: Forms item; TYPE: Date
  STATUS — KIND: Forms item; TYPE: Char

  PAYROLL_RUN — KIND: Forms block; TYPE: N/A (query block on HRMS.PAYROLL_RUNS, detail of PAY_PERIOD via PERIOD_RUN_REL)
  **PAYROLL_RUN items:**
  RUN_ID — KIND: Forms item; TYPE: N/A (hidden, primary key)
  PERIOD_ID — KIND: Forms item; TYPE: N/A (hidden)
  RUN_TYPE — KIND: Forms item; TYPE: Char
  RUN_DATE — KIND: Forms item; TYPE: Date
  STATUS — KIND: Forms item; TYPE: Char
  EMPLOYEE_COUNT — KIND: Forms item; TYPE: Number
  TOTAL_GROSS — KIND: Forms item; TYPE: Number
  TOTAL_NET — KIND: Forms item; TYPE: Number
  BTN_CREATE_RUN — KIND: Forms item (Push Button); TYPE: N/A
  BTN_CALCULATE — KIND: Forms item (Push Button); TYPE: N/A
  BTN_APPROVE — KIND: Forms item (Push Button); TYPE: N/A

  PERIOD_RUN_REL — KIND: Forms block relation; TYPE: N/A (master-detail, PAY_PERIOD → PAYROLL_RUN, auto-query)
  CVS_MAIN — KIND: Forms canvas (Tab); TYPE: N/A; TabPages: TP_PERIODS ("Pay Periods"), TP_RUNS ("Payroll Runs"), TP_DETAILS ("Pay Details")
  WIN_PAYROLL — KIND: Forms window; TYPE: N/A

**METHODS:**
  **TRIGGER WHEN-NEW-FORM-INSTANCE (form-level)** [SOURCE: L22-48]
  - What it does: Fires when the form instance is created. Validates the session via PKG_SECURITY.is_session_valid; requires PAYROLL/VIEW permission for the current employee, blocking access if absent. Sets the MDI window title with the current user. Navigates to PAY_PERIOD, sets its default WHERE clause to STATUS = 'OPEN' ordered by PERIOD_START_DATE DESC, and executes the query.
  - Business rules: Session must be valid. Current employee must have PAYROLL/VIEW permission to open the module. Default PAY_PERIOD view shows only OPEN periods, newest first.
  - Numbers & thresholds: None.
  - Security & error handling: Invalid session shows "Session expired. Please log in again." and raises FORM_TRIGGER_FAILURE. Missing PAYROLL/VIEW permission shows "You do not have permission to access the Payroll module." and raises FORM_TRIGGER_FAILURE.
  - Data in/out: Input — GET_APPLICATION_PROPERTY(USERNAME), :GLOBAL.current_emp_id, :GLOBAL.current_user. Output — window title set; PAY_PERIOD block queried with OPEN-status filter.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_CREATE_RUN, on PAYROLL_RUN block)** [SOURCE: L93-104]
  - What it does: Calls PKG_PAYROLL.create_payroll_run with the selected PAY_PERIOD.PERIOD_ID, a fixed run type 'REGULAR', and the current user; shows a success message with the new run ID; re-queries PAYROLL_RUN.
  - Business rules: New runs are always created with RUN_TYPE = 'REGULAR' from this button.
  - Numbers & thresholds: None.
  - Security & error handling: None (no exception handling shown).
  - Data in/out: Input — :PAY_PERIOD.PERIOD_ID, :GLOBAL.current_user, literal 'REGULAR'. Output — v_run_id from PKG_PAYROLL.create_payroll_run; PAYROLL_RUN re-queried.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_CALCULATE, on PAYROLL_RUN block)** [SOURCE: L111-127]
  - What it does: Fires on click. Requires the selected run's STATUS to be 'PENDING'; if not, blocks with a message. Shows a "Calculating..." message, forces a client sync (SYNCHRONIZE), calls PKG_PAYROLL.calculate_payroll with the run ID and current user, then shows a completion message and re-queries.
  - Business rules: Payroll can only be calculated for runs in STATUS = 'PENDING'.
  - Numbers & thresholds: None.
  - Security & error handling: Status guard raises FORM_TRIGGER_FAILURE with "Can only calculate runs in PENDING status." if violated; no exception handling around the calculation call itself.
  - Data in/out: Input — :PAYROLL_RUN.RUN_ID, :PAYROLL_RUN.STATUS, :GLOBAL.current_user. Output — payroll calculated via package call; PAYROLL_RUN re-queried.

  **TRIGGER WHEN-BUTTON-PRESSED (BTN_APPROVE, on PAYROLL_RUN block)** [SOURCE: L134-147]
  - What it does: Fires on click. Requires PAYROLL/APPROVE permission for the current employee; if absent, blocks with a message. Calls PKG_PAYROLL.approve_payroll with the run ID and current user; shows a confirmation message; re-queries.
  - Business rules: Approving a payroll run requires PAYROLL/APPROVE permission.
  - Numbers & thresholds: None.
  - Security & error handling: Missing permission raises FORM_TRIGGER_FAILURE with "You do not have permission to approve payroll."; no exception handling around the approval call itself.
  - Data in/out: Input — :GLOBAL.current_emp_id, :PAYROLL_RUN.RUN_ID, :GLOBAL.current_user. Output — payroll run approved via package call; PAYROLL_RUN re-queried.

  **FILE-LEVEL EFFECT (block display/relation config, form layout)** [SOURCE: L51-164]
  - What it does: Configures PAY_PERIOD to display 10 records at a time (change-record navigation, no insert/update/delete); configures PAYROLL_RUN to display 5 records at a time (same restrictions) with monetary display formats and a master-detail relation (PERIOD_RUN_REL) to PAY_PERIOD with auto-query; defines the tabbed CVS_MAIN canvas and the WIN_PAYROLL document window.
  - Business rules: PAY_PERIOD and PAYROLL_RUN blocks are read-only (no insert/update/delete via the form; all mutations go through PKG_PAYROLL calls). PAYROLL_RUN rows auto-query as detail of the selected PAY_PERIOD row.
  - Numbers & thresholds: PAY_PERIOD RecordsDisplayed = 10. PAYROLL_RUN RecordsDisplayed = 5. TOTAL_GROSS/TOTAL_NET display format $999,999,990.00. CVS_MAIN tab canvas Width=750, Height=520. WIN_PAYROLL window Width=770, Height=560.
  - Security & error handling: None.
  - Data in/out: Output — UI chrome and block query configuration only.

**DEPENDENCIES:**
  Data touched:
  - Reads: HRMS.PAY_PERIODS — PAY_PERIOD block query (filtered to STATUS='OPEN'); HRMS.PAYROLL_RUNS — PAYROLL_RUN block query (auto-queried as detail of PAY_PERIOD)
  - Writes: None (run creation/calculation/approval are performed inside PKG_PAYROLL, not directly by this form)

  CALLS: PKG_SECURITY.is_session_valid | EVIDENCE: OBSERVED | SOURCE: L28
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L34
  CALLS: PKG_SECURITY.has_permission | EVIDENCE: OBSERVED | SOURCE: L137
  CALLS: PKG_PAYROLL.create_payroll_run | EVIDENCE: OBSERVED | SOURCE: L98
  CALLS: PKG_PAYROLL.calculate_payroll | EVIDENCE: OBSERVED | SOURCE: L122
  CALLS: PKG_PAYROLL.approve_payroll | EVIDENCE: OBSERVED | SOURCE: L142
  IMPORTS: HRMS_COMMON_LIB | EVIDENCE: OBSERVED | SOURCE: L19

  Config/env: None
  External integrations: None

**GAPS:**
  Header comment (L10-12) states 4 data blocks (including PAYROLL_DETAIL, PAYSLIP_SUMMARY) and 3 LOVs (Period, Run Type, Employee), but only 2 blocks (PAY_PERIOD, PAYROLL_RUN) and 0 LOVs are present in this source — PAYROLL_DETAIL, PAYSLIP_SUMMARY, and all 3 LOVs are NOT_ANALYZED (not in provided source). TP_DETAILS tab page exists on CVS_MAIN but has no associated block/items shown — UNKNOWN.

*[pipeline status — type: forms · pass: correction · attempt: 3 · coverage: INCOMPLETE — numbers missing: 100, 120, 140, 150, 25, 60, 80]*

---

=== CHUNK STATUS ===
Files expected: 4
Files delivered: 4
  Full coverage on first pass: 0
  Required correction: 4 -> ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml
  Still incomplete after max attempts: 4 -> ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml
Raw source: 26791 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===