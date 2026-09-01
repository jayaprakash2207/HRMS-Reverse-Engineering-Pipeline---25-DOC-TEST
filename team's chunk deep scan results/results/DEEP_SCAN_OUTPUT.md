=== DEEP SCAN SUMMARY ===
Total files in roster: 42
Connections resolved: 276
Connections unresolved/ambiguous: 43
=== END SUMMARY ===


=== FILE: ts-plsql-oracle-forms-hrms-main/data/seed/01_reference_data.sql ===
IDENTITY: seed — reference data load for locations, job grades, departments, job titles, leave types, pay elements, holidays, and system parameters (run order 01, before employee data)
CHUNK: 18  (full detail: Chunk_18_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/data/seed/02_employee_data.sql ===
IDENTITY: seed — loads 24 sample HRMS employees (executives, HR, Finance, IT, Sales, plus one terminated employee) with their current salary records, and updates department manager assignments
CHUNK: 19  (full detail: Chunk_19_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql ===
IDENTITY: schema — Shared toolbar button handlers, global error handling, date formatting, and session/LOV helper routines attached to every HRMS form via ATTACH_LIBRARY.
CHUNK: 15  (full detail: Chunk_15_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: PKG_COMMON.log_error, PKG_SECURITY.is_session_valid
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_VALIDATION_LIB.pll.sql ===
IDENTITY: schema — client-side validation functions (email, phone, SSN, date, salary range) shared across Oracle Forms, used for immediate on-form feedback ahead of/alongside server-side validation
CHUNK: 15  (full detail: Chunk_15_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/menus/HRMS_MENU.mmb.sql ===
IDENTITY: schema — Documents the main application menu bar structure (File, Edit, Query, Navigate, Modules, Admin, Help) and the Forms built-in or module action bound to each item
CHUNK: 15  (full detail: Chunk_15_Output.md)
SHAPE: CONTENTS, EXIT, MAIN_MENUBAR, PRINT, SAVE, SUPPORT
CONNECTIONS:
  CALLS: HRMS_EMPLOYEE (OPEN_FORM), HRMS_PAYROLL (OPEN_FORM), HRMS_LEAVE (OPEN_FORM), HRMS_PERFORMANCE (OPEN_FORM), HRMS_REPORTS (OPEN_FORM), HRMS_ADMIN (OPEN_FORM), PKG_SECURITY.has_permission
  CALLED_BY: (none)
  UNRESOLVED: HRMS_EMPLOYEE (OPEN_FORM), HRMS_PAYROLL (OPEN_FORM), HRMS_LEAVE (OPEN_FORM), HRMS_PERFORMANCE (OPEN_FORM), HRMS_REPORTS (OPEN_FORM), HRMS_ADMIN (OPEN_FORM)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml ===
IDENTITY: forms — Employee maintenance form — master-detail form for personal info, job assignment, and compensation history (per header comment; header also claims dependent management, but no such block is present in this export — see GAPS).
CHUNK: 01  (full detail: Chunk_01_Output.md)
SHAPE: ACTIVE_FLAG, ADDRESS_LINE1, ADDRESS_LINE2, ALT_CONFIRM_DELETE, ALT_CONFIRM_EXIT, BASE_SALARY, CHANGE_PCT, CHANGE_REASON, CITY, CREATED_BY, CREATED_DATE, CVS_MAIN, CVS_TOOLBAR, DATE_OF_BIRTH, DEPT_ID, DEPT_NAME_DISP, EFFECTIVE_DATE, EMAIL, EMPLOYEE, EMPLOYMENT_STATUS, EMPLOYMENT_TYPE, EMP_ID, EMP_NUMBER, EMP_SALARY_REL, END_DATE, FIRST_NAME, GENDER, HIRE_DATE, HRMS_COMMON_LIB, HRMS_MENU, HRMS_VALIDATION_LIB, JOB_ID, JOB_TITLE_DISP, LAST_NAME, LOCATION_CODE, MANAGER_EMP_ID, MANAGER_NAME_DISP, MARITAL_STATUS, MODIFIED_BY, MODIFIED_DATE, PHONE_MOBILE, PHONE_WORK, POSTAL_CODE, SALARY, SALARY_ID, STATE_PROVINCE, TERMINATION_DATE, WIN_EMPLOYEE
CONNECTIONS:
  CALLS: PKG_SECURITY.is_session_valid, PKG_SECURITY.has_permission, PKG_EMPLOYEE.generate_emp_number, PKG_VALIDATION.validate_email_format
  CALLED_BY: (none)
  UNRESOLVED: HRMS_COMMON_LIB
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml ===
IDENTITY: forms — Employee leave management — submit leave requests, cancel pending/approved requests, view leave balances, and (per header comment) approve requests and view a team calendar.
CHUNK: 02  (full detail: Chunk_02_Output.md)
SHAPE: ACCRUED, ALT_CONFIRM_CANCEL, AVAILABLE, BTN_CANCEL_REQUEST, BTN_SUBMIT, CVS_MAIN, EMP_ID, END_DATE, LEAVE_BALANCE, LEAVE_REQUEST, LEAVE_TYPE_NAME_DISP, LOV_LEAVE_TYPES, NEW_REQUEST, NR_BALANCE_DISP, NR_CALC_DAYS, NR_END_DATE, NR_HALF_DAY, NR_LEAVE_TYPE_DISP, NR_LEAVE_TYPE_ID, NR_REASON, NR_START_DATE, OPENING_BALANCE, PENDING, REASON, REQUEST_ID, RG_LEAVE_TYPES, START_DATE, STATUS, TOTAL_DAYS, USED, WIN_LEAVE
CONNECTIONS:
  CALLS: PKG_SECURITY.is_session_valid, PKG_LEAVE.cancel_leave_request, PKG_LEAVE.submit_leave_request
  CALLED_BY: (none)
  UNRESOLVED: HRMS_COMMON_LIB
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml ===
IDENTITY: forms — Login form — authenticates a user against PKG_SECURITY and opens the main HRMS menu on success.
CHUNK: 02  (full detail: Chunk_02_Output.md)
SHAPE: BTN_LOGIN, COMPANY_LOGO, CVS_LOGIN, ERROR_MSG, LOGIN, PASSWORD, USERNAME, WIN_LOGIN
CONNECTIONS:
  CALLS: PKG_SECURITY.authenticate, HRMS_MENU (OPEN_FORM)
  CALLED_BY: (none)
  UNRESOLVED: HRMS_MENU (OPEN_FORM)
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml ===
IDENTITY: forms — MDI parent/main-menu form — application shell after login; sets permission-based menu item visibility and launches all HRMS child modules.
CHUNK: 02  (full detail: Chunk_02_Output.md)
SHAPE: BTN_EMPLOYEES, BTN_LEAVE, BTN_LOGOUT, BTN_PAYROLL, BTN_PERFORMANCE, BTN_REPORTS, CVS_MAIN, MENU_CONTROL, MENU_MAIN, USER_INFO, WELCOME_TEXT, WIN_MAIN
CONNECTIONS:
  CALLS: PKG_SECURITY.has_permission, PKG_SECURITY.has_permission, PKG_SECURITY.has_permission, PKG_SECURITY.has_permission, PKG_SECURITY.has_permission, PKG_SECURITY.logout, PKG_SECURITY.logout, HRMS_EMPLOYEE (OPEN_FORM), HRMS_PAYROLL (OPEN_FORM), HRMS_LEAVE (OPEN_FORM), HRMS_PERFORMANCE (OPEN_FORM), HRMS_REPORTS (OPEN_FORM), HRMS_ADMIN (OPEN_FORM)
  CALLED_BY: (none)
  UNRESOLVED: HRMS_EMPLOYEE (OPEN_FORM), HRMS_PAYROLL (OPEN_FORM), HRMS_LEAVE (OPEN_FORM), HRMS_PERFORMANCE (OPEN_FORM), HRMS_REPORTS (OPEN_FORM), HRMS_ADMIN (OPEN_FORM), HRMS_COMMON_LIB
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml ===
IDENTITY: forms — Payroll processing form — pay-period listing, payroll run creation/calculation/approval, and (per header comment) pay-detail/payslip viewing.
CHUNK: 02  (full detail: Chunk_02_Output.md)
SHAPE: BTN_APPROVE, BTN_CALCULATE, BTN_CREATE_RUN, CVS_MAIN, EMPLOYEE_COUNT, PAYROLL_RUN, PAY_DATE, PAY_PERIOD, PERIOD_END_DATE, PERIOD_ID, PERIOD_NAME, PERIOD_RUN_REL, PERIOD_START_DATE, RUN_DATE, RUN_ID, RUN_TYPE, STATUS, TOTAL_GROSS, TOTAL_NET, WIN_PAYROLL
CONNECTIONS:
  CALLS: PKG_SECURITY.is_session_valid, PKG_SECURITY.has_permission, PKG_SECURITY.has_permission, PKG_PAYROLL.create_payroll_run, PKG_PAYROLL.calculate_payroll, PKG_PAYROLL.approve_payroll
  CALLED_BY: (none)
  UNRESOLVED: HRMS_COMMON_LIB
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PERFORMANCE.xml ===
IDENTITY: forms — performance review management — review cycles, self-assessments, manager reviews, goal tracking, and rating calibration
CHUNK: 03  (full detail: Chunk_03_Output.md)
SHAPE: CVS_MAIN, CYCLE_ID, CYCLE_NAME, CYCLE_REVIEW_REL, CYCLE_YEAR, EMP_ID, EMP_NAME_DISP, END_DATE, GOAL_CATEGORY, GOAL_ID, GOAL_TITLE, HRMS_COMMON_LIB, HRMS_PERFORMANCE, MANAGER_ASSESSMENT, OVERALL_RATING, PROGRESS_PCT, RATING_LABEL, REVIEW_GOAL_REL, REVIEW_ID, SELF_ASSESSMENT, START_DATE, WEIGHT_PCT, WIN_PERFORMANCE
CONNECTIONS:
  CALLS: PKG_SECURITY.is_session_valid
  CALLED_BY: (none)
  UNRESOLVED: HRMS_COMMON_LIB
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pkb ===
IDENTITY: plsql-body — writes audit trail records, purges old audit history, and retrieves change history for a given table/record
CHUNK: 05  (full detail: Chunk_05_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: DBMS_OUTPUT.PUT_LINE
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks
  UNRESOLVED: DBMS_OUTPUT.PUT_LINE
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pks ===
IDENTITY: plsql-spec — Declares the public interface for centralized audit-trail logging of DML changes, used by all other packages and database triggers.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb, ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql, ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql, ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb ===
IDENTITY: plsql-body — shared utility functions for HRMS — audit logging, system parameter access, business-day date math, fiscal period calculation, and formatting/validation of phone, SSN, currency, name, and email values
CHUNK: 05  (full detail: Chunk_05_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: PKG_COMMON.get_param, PKG_COMMON.get_param, DBMS_OUTPUT.PUT_LINE
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pks
  UNRESOLVED: DBMS_OUTPUT.PUT_LINE
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pks ===
IDENTITY: plsql-spec — Declares the shared utility interface — error/info logging, configuration-parameter access, date/business-day utilities, formatting, and validation — used by all other packages and forms.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: T_ERROR_REC
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb ===
IDENTITY: plsql-body — employee lifecycle management (hire, update, transfer, promote, terminate, rehire) and employee/org-chart lookups for the HRMS schema
CHUNK: 06  (full detail: Chunk_06_Output.md)
SHAPE: C_EMP_NUMBER_PREFIX, C_MAX_HIERARCHY_DEPTH
CONNECTIONS:
  CALLS: PKG_PAYROLL.create_salary_record, PKG_PAYROLL.create_salary_record, PKG_PAYROLL.create_salary_record, PKG_AUDIT.log_action, PKG_AUDIT.log_action, PKG_AUDIT.log_action, PKG_AUDIT.log_action, PKG_AUDIT.log_action, PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification, PKG_NOTIFICATION.send_notification, PKG_NOTIFICATION.send_notification, PKG_COMMON.log_error, PKG_COMMON.log_error, PKG_COMMON.log_error
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks ===
IDENTITY: plsql-spec — Declares the core employee-management interface — CRUD, employment lifecycle (transfer/promote/terminate/rehire), org-chart/headcount queries, and validation — used by the HRMS_EMPLOYEE and HRMS_DEPARTMENT forms and batch jobs.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: E_DUPLICATE_EMP_NUMBER, E_EMPLOYEE_NOT_FOUND, E_INVALID_DEPARTMENT, E_INVALID_MANAGER, E_TERMINATION_ERROR, G_CURRENT_DEPT_ID, G_CURRENT_EMP_ID, G_CURRENT_USER, G_DEBUG_MODE, T_EMP_CURSOR, T_EMP_ID_TABLE, T_EMP_REC, T_EMP_REC_TABLE
CONNECTIONS:
  CALLS: PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION, PKG_PAYROLL
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pkb ===
IDENTITY: plsql-body — outbound/inbound integration with external systems — GL journal export, benefits feed export, time & attendance import, org structure sync, and integration status lookup
CHUNK: 07  (full detail: Chunk_07_Output.md)
SHAPE: C_BENEFITS_OUTPUT_DIR, C_GL_OUTPUT_DIR, C_TIME_INPUT_DIR
CONNECTIONS:
  CALLS: PKG_COMMON.log_info, PKG_COMMON.log_error, PKG_COMMON.log_info, PKG_COMMON.log_error, PKG_COMMON.log_error, PKG_COMMON.log_info, PKG_COMMON.log_error, PKG_COMMON.log_info, PKG_COMMON.get_param
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks ===
IDENTITY: plsql-spec — Declares the external-system integration interface — GL journal posting, benefits-provider feed export, time & attendance import, and org-structure sync — run by the nightly/weekly batch scheduler.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: T_GL_ENTRY, T_GL_ENTRY_TABLE
CONNECTIONS:
  CALLS: PKG_COMMON, PKG_PAYROLL, PKG_EMPLOYEE
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb ===
IDENTITY: plsql-body — leave management — request submission/approval workflow, balance tracking, monthly accrual, and year-end carryover for HRMS employees
CHUNK: 08  (full detail: Chunk_08_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: calculate_business_days, check_leave_overlap, approve_leave_request, PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification, PKG_AUDIT.log_action, PKG_AUDIT.log_action, initialize_balances, PKG_AUDIT.log_action, get_leave_balance, initialize_balances, initialize_balances, DBMS_OUTPUT.PUT_LINE, DBMS_SCHEDULER
  CALLED_BY: (none)
  UNRESOLVED: DBMS_OUTPUT.PUT_LINE, DBMS_SCHEDULER
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks ===
IDENTITY: plsql-spec — Declares the leave-management interface — leave requests, approvals, balance tracking, and accrual/carryover batch processing — used by the HRMS_LEAVE form, self-service portal, and the batch accrual job.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: E_APPROVAL_ERROR, E_INSUFFICIENT_BALANCE, E_INVALID_LEAVE_TYPE, E_OVERLAPPING_LEAVE, T_LEAVE_CURSOR
CONNECTIONS:
  CALLS: PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb ===
IDENTITY: plsql-body — queues outbound notifications and delivers them asynchronously via SMTP, with retry and cancellation support
CHUNK: 09  (full detail: Chunk_09_Output.md)
SHAPE: C_FROM_ADDRESS, C_FROM_NAME, C_SMTP_HOST, C_SMTP_PORT
CONNECTIONS:
  CALLS: PKG_COMMON.log_error, PKG_COMMON.log_info, SEQ_NOTIFICATION.NEXTVAL, UTL_SMTP.OPEN_CONNECTION, UTL_SMTP.HELO, UTL_SMTP.MAIL, UTL_SMTP.RCPT, UTL_SMTP.OPEN_DATA, UTL_SMTP.WRITE_DATA, UTL_SMTP.CLOSE_DATA, UTL_SMTP.QUIT, UTL_SMTP.QUIT, UTL_TCP.CRLF
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks
  UNRESOLVED: SEQ_NOTIFICATION.NEXTVAL, UTL_SMTP.OPEN_CONNECTION, UTL_SMTP.HELO, UTL_SMTP.MAIL, UTL_SMTP.RCPT, UTL_SMTP.OPEN_DATA, UTL_SMTP.WRITE_DATA, UTL_SMTP.CLOSE_DATA, UTL_SMTP.QUIT, UTL_SMTP.QUIT, UTL_TCP.CRLF
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks ===
IDENTITY: plsql-spec — Declares the notification-queue interface — sending, batch processing, retry, and cancellation of email/in-app/SMS notifications — used by PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, and PKG_PERFORMANCE.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: PKG_COMMON
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb ===
IDENTITY: plsql-body — Payroll processing — salary history, pay period/run lifecycle, tax and deduction calculation, payslip and pay register reporting
CHUNK: 10  (full detail: Chunk_10_Output.md)
SHAPE: C_ALLOWANCE_AMOUNT, C_MEDICARE_ADDL_RATE, C_MEDICARE_ADDL_THRESHOLD, C_MEDICARE_RATE, C_SS_RATE, C_SS_WAGE_BASE_2024, C_STANDARD_DEDUCTION_MARRIED, C_STANDARD_DEDUCTION_SINGLE
CONNECTIONS:
  CALLS: PKG_AUDIT.log_action, PKG_AUDIT.log_action, calculate_employee_pay, get_salary_as_of, get_ytd_earnings, calculate_federal_tax, calculate_state_tax, calculate_fica, calculate_medicare, PKG_COMMON.log_error, PKG_COMMON.log_error, UTL_FILE.FOPEN, UTL_FILE.PUT_LINE, UTL_FILE.FCLOSE, UTL_FILE.IS_OPEN, DBMS_OUTPUT.PUT_LINE
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks
  UNRESOLVED: UTL_FILE.FOPEN, UTL_FILE.PUT_LINE, UTL_FILE.FCLOSE, UTL_FILE.IS_OPEN, DBMS_OUTPUT.PUT_LINE
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks ===
IDENTITY: plsql-spec — Declares the payroll-processing interface — salary records, pay-period management, payroll-run calculation/approval/reversal, tax withholding calculations, and payslip/pay-register reporting — used by the HRMS_PAYROLL form and the DBMS_SCHEDULER batch scheduler.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: E_CALCULATION_ERROR, E_INVALID_SALARY, E_PERIOD_CLOSED, E_RUN_ALREADY_PAID, T_PAYSLIP_CURSOR, T_PAYSLIP_REC
CONNECTIONS:
  CALLS: PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb, ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb ===
IDENTITY: plsql-body — Performance review lifecycle management — review cycles, self/manager reviews, goals, and reporting cursors
CHUNK: 11  (full detail: Chunk_11_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: PKG_AUDIT.log_action, PKG_NOTIFICATION.send_notification, PKG_NOTIFICATION.send_notification, PKG_NOTIFICATION.send_notification, create_review
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks ===
IDENTITY: plsql-spec — Performance review management — review cycles, self/manager assessments, goal tracking, and rating distribution/calibration.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: T_REVIEW_CURSOR
CONNECTIONS:
  CALLS: PKG_EMPLOYEE, PKG_COMMON, PKG_AUDIT, PKG_NOTIFICATION
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pkb
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pkb ===
IDENTITY: plsql-body — HR/payroll reporting — headcount, compensation, turnover, new hires, leave utilization, payroll summary, and EEO compliance report cursors
CHUNK: 11  (full detail: Chunk_11_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: PKG_COMMON.log_info
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks ===
IDENTITY: plsql-spec — Report generation — headcount, compensation, turnover, new hires, leave utilization, payroll summary, and EEO compliance reporting.
CHUNK: 13  (full detail: Chunk_13_Output.md)
SHAPE: T_REPORT_CURSOR
CONNECTIONS:
  CALLS: PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pkb ===
IDENTITY: plsql-body — Authentication, session lifecycle management, role/permission checks, SSN encryption, and password policy enforcement for the HRMS system.
CHUNK: 12  (full detail: Chunk_12_Output.md)
SHAPE: C_ENCRYPTION_KEY, C_SESSION_TIMEOUT_MIN
CONNECTIONS:
  CALLS: DBMS_CRYPTO.HASH, UTL_RAW.CAST_TO_RAW, PKG_EMPLOYEE.set_session_context, PKG_AUDIT.log_action, DBMS_CRYPTO.ENCRYPT, DBMS_CRYPTO.DECRYPT, UTL_RAW.CAST_TO_VARCHAR2, PKG_AUDIT.log_action
  CALLED_BY: (none)
  UNRESOLVED: DBMS_CRYPTO.HASH, UTL_RAW.CAST_TO_RAW, DBMS_CRYPTO.ENCRYPT, DBMS_CRYPTO.DECRYPT, UTL_RAW.CAST_TO_VARCHAR2
COVERAGE: INCOMPLETE
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks ===
IDENTITY: plsql-spec — Public interface for authentication, session management, role-based authorization, and SSN/password encryption in HRMS.
CHUNK: 14  (full detail: Chunk_14_Output.md)
SHAPE: E_ACCOUNT_LOCKED, E_INSUFFICIENT_PRIV, E_INVALID_CREDENTIALS, E_SESSION_EXPIRED
CONNECTIONS:
  CALLS: PKG_COMMON, PKG_AUDIT
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/forms/libraries/HRMS_COMMON_LIB.pll.sql, ts-plsql-oracle-forms-hrms-main/forms/menus/HRMS_MENU.mmb.sql, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LEAVE.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_LOGIN.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_MENU.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PAYROLL.xml, ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PERFORMANCE.xml
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb ===
IDENTITY: plsql-body — Centralized field/business-rule validation routines (dates, salary bands, email/phone/employee-number formats, business-day/holiday checks, required-field checks) used across HRMS.
CHUNK: 12  (full detail: Chunk_12_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: PKG_COMMON.is_valid_email, PKG_COMMON.is_valid_phone
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pks ===
IDENTITY: plsql-spec — Public interface for centralized business-rule validation shared between Forms WHEN-VALIDATE-ITEM triggers and PL/SQL packages (date ranges, salary-to-grade, email/phone/employee-number formats, future-date/business-day checks, required-field checks).
CHUNK: 14  (full detail: Chunk_14_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: PKG_COMMON
  CALLED_BY: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_EMPLOYEE.xml
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql ===
IDENTITY: schema — Generic audit-trail triggers that record INSERT/UPDATE/DELETE changes on SALARY_RECORDS, status changes on LEAVE_REQUESTS, and INSERT/UPDATE/DELETE changes on DEPARTMENTS, via PKG_AUDIT.log_action.
CHUNK: 15  (full detail: Chunk_15_Output.md)
SHAPE: TRG_DEPARTMENT_AUDIT, TRG_LEAVE_REQUEST_AUDIT, TRG_SALARY_AUDIT
CONNECTIONS:
  CALLS: PKG_AUDIT.log_action, PKG_AUDIT.log_action, PKG_AUDIT.log_action
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_employees.sql ===
IDENTITY: schema — Database-level triggers enforcing employee insert/update validation, audit-column defaults, status/department/job change history logging, and a soft-delete guard on HRMS.EMPLOYEES — duplicating logic that also exists in PKG_EMPLOYEE and Forms triggers.
CHUNK: 15  (full detail: Chunk_15_Output.md)
SHAPE: TRG_EMP_BEFORE_INSERT, TRG_EMP_BEFORE_UPDATE, TRG_EMP_INSTEAD_OF_DELETE
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/README.md ===
IDENTITY: other — describes the overall architecture, directory layout, and technical characteristics of the Oracle Forms 11g/12c legacy HRMS application
CHUNK: 04  (full detail: Chunk_04_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/sequences/hrms_sequences.sql ===
IDENTITY: schema — Creates all surrogate-key sequences used across the HRMS schema's tables (employee, payroll, leave, performance, and system/audit domains)
CHUNK: 15  (full detail: Chunk_15_Output.md)
SHAPE: SEQ_AUDIT, SEQ_DEPARTMENT, SEQ_DEPENDENT, SEQ_EMERGENCY_CONTACT, SEQ_EMPLOYEE, SEQ_EMP_HISTORY, SEQ_EMP_NUMBER, SEQ_EMP_PAY_ELEMENT, SEQ_HOLIDAY, SEQ_JOB_GRADE, SEQ_JOB_TITLE, SEQ_LEAVE_ACCRUAL, SEQ_LEAVE_BALANCE, SEQ_LEAVE_REQUEST, SEQ_LEAVE_TYPE, SEQ_LOCATION, SEQ_LOOKUP, SEQ_NOTIFICATION, SEQ_PAYROLL_DETAIL, SEQ_PAYROLL_RUN, SEQ_PAY_ELEMENT, SEQ_PAY_PERIOD, SEQ_PERF_GOAL, SEQ_PERF_REVIEW, SEQ_REVIEW_CYCLE, SEQ_SALARY, SEQ_SYSTEM_PARAM, SEQ_TAX_BRACKET, SEQ_USER_SESSION
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/01_core_tables.sql ===
IDENTITY: schema — DDL defining the HRMS core entity tables — departments, locations, job grades/titles, employees, employee history, dependents, and emergency contacts
CHUNK: 16  (full detail: Chunk_16_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/02_payroll_tables.sql ===
IDENTITY: schema — DDL defining the HRMS payroll subsystem tables — salary history, pay elements, pay periods/runs, tax brackets, employee tax info, and bank accounts for direct deposit
CHUNK: 16  (full detail: Chunk_16_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/03_leave_tables.sql ===
IDENTITY: schema — DDL defining the HRMS leave-management tables — leave types, balances, requests, accrual log, and company holidays
CHUNK: 16  (full detail: Chunk_16_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/04_performance_tables.sql ===
IDENTITY: schema — creates HRMS performance-management, audit, configuration, notification, session-tracking, and generic lookup tables
CHUNK: 17  (full detail: Chunk_17_Output.md)
SHAPE: ACTION_TYPE, ACTIVE_FLAG, AREAS_FOR_IMPROVEMENT, AUDIT_ID, AUDIT_LOG, BODY, CALIBRATED_RATING, CALIBRATION_DUE, CALIBRATION_NOTES, CHANGED_BY, CHANGED_DATE, COMMENTS, CREATED_BY, CREATED_DATE, CYCLE_ID, CYCLE_NAME, CYCLE_YEAR, DATA_TYPE, DEVELOPMENT_PLAN, DISPLAY_ORDER, EDITABLE_FLAG, EMPLOYEE_ACK_DATE, EMPLOYEE_COMMENTS, EMP_ID, END_DATE, ERROR_MESSAGE, FORMS_MODULE, GOAL_CATEGORY, GOAL_DESCRIPTION, GOAL_ID, GOAL_TITLE, IP_ADDRESS, LOGIN_TIME, LOGOUT_TIME, LOOKUP_CODE, LOOKUP_ID, LOOKUP_TYPE, LOOKUP_VALUE, LOOKUP_VALUES, MANAGER_ASSESSMENT, MANAGER_RATING, MANAGER_REVIEW_DUE, MODIFIED_BY, MODIFIED_DATE, NEW_VALUES, NOTIFICATION_ID, NOTIFICATION_QUEUE, NOTIFICATION_TYPE, OLD_VALUES, OVERALL_RATING, PARAM_CODE, PARAM_DESCRIPTION, PARAM_GROUP, PARAM_ID, PARAM_VALUE, PARENT_LOOKUP_ID, PERFORMANCE_GOALS, PERFORMANCE_REVIEWS, PRIORITY, PROGRESS_PCT, RATING_LABEL, RECIPIENT_EMAIL, RECIPIENT_EMP_ID, RECORD_ID, REFERENCE_ID, REFERENCE_TABLE, RETRY_COUNT, REVIEWER_EMP_ID, REVIEW_CYCLES, REVIEW_ID, REVIEW_TYPE, SELF_ASSESSMENT, SELF_RATING, SELF_REVIEW_DUE, SENT_DATE, SESSION_ID, SESSION_STATUS, START_DATE, STATUS, STRENGTHS, SUBJECT, SYSTEM_PARAMETERS, TABLE_NAME, TARGET_DATE, USERNAME, USER_SESSIONS, WEIGHT_PCT
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/views/hrms_views.sql ===
IDENTITY: schema — Creates reporting/lookup views over the HRMS schema for use by Oracle Reports (.rdf), Forms LOVs, and external reporting tools.
CHUNK: 17  (full detail: Chunk_17_Output.md)
SHAPE: (none)
CONNECTIONS:
  CALLS: (none)
  CALLED_BY: (none)
COVERAGE: OK
=== END FILE ===
