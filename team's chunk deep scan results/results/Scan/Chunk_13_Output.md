=== CHUNK METADATA ===
Chunk: 13            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-spec
Expected files (9):
  1. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pks (3158 chars written)
  2. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pks (10144 chars written)
  3. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks (15318 chars written)
  4. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks (5224 chars written)
  5. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks (11549 chars written)
  6. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks (4954 chars written)
  7. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks (15431 chars written)
  8. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks (8343 chars written)
  9. [plsql-spec] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks (6684 chars written)
Total source content: 29913 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_AUDIT.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Declares the public interface for centralized audit-trail logging of DML changes, used by all other packages and database triggers.

**STRUCTURES:**
  None (this spec declares no package-level types, constants, or exceptions — only the three subprogram signatures listed under METHODS).

**METHODS:**
  **PROCEDURE log_action(p_table_name IN VARCHAR2, p_record_id IN NUMBER, p_action IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER, p_old_values IN CLOB DEFAULT NULL, p_new_values IN CLOB DEFAULT NULL)** [SOURCE: L10-17]
  - What it does: Declares the package's central audit-write entry point; per the header comment it is called by all other packages and database triggers to record a DML change. The actual insert/logic lives in the package body, which is not included in this file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (the current DB session identity) when not supplied; no other access control visible in the spec.
  - Data in/out: Inputs — p_table_name, p_record_id, p_action (required), p_user (default USER), p_old_values/p_new_values (optional CLOBs, default NULL). Output — none (procedure).

  **PROCEDURE purge_old_records(p_days_to_keep IN NUMBER DEFAULT 365, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L19-22]
  - What it does: Declares a retention-purge entry point for old audit records; implementation not present in this spec file.
  - Business rules: Default retention window is 365 days when p_days_to_keep is not supplied.
  - Numbers & thresholds: p_days_to_keep DEFAULT 365 (retention period, in days).
  - Security & error handling: p_user defaults to USER (session identity); no other access control visible in the spec.
  - Data in/out: Inputs — p_days_to_keep (default 365), p_user (default USER). Output — none (procedure).

  **FUNCTION get_change_history(p_table_name IN VARCHAR2, p_record_id IN NUMBER, p_from_date IN DATE DEFAULT NULL, p_to_date IN DATE DEFAULT NULL) RETURN SYS_REFCURSOR** [SOURCE: L24-29]
  - What it does: Declares a lookup of audit history for a given table/record, optionally bounded by a date range; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_table_name, p_record_id (required), p_from_date/p_to_date (optional, default NULL). Output — returns a SYS_REFCURSOR of change-history rows.

**DEPENDENCIES:**
  Data touched:
  - Reads: None (spec only — no SQL visible in this file)
  - Writes: None (spec only — no SQL visible in this file)

  Config/env: None
  External integrations: None

**GAPS:**
  This is a package specification only; the package body (PKG_AUDIT.pkb) with the actual logging logic, table(s) written, and error handling was not provided in this chunk — all implementation detail is NOT_ANALYZED. Header comment states "Dependencies: None (base package)", consistent with no CALLS lines above.

---

*[pipeline status — type: plsql-spec · pass: correction · attempt: 1 · coverage: 100% (numbers 1/1 · procedures 3/3 · units 3/3 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_COMMON.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Declares the shared utility interface — error/info logging, configuration-parameter access, date/business-day utilities, formatting, and validation — used by all other packages and forms.

**STRUCTURES:**
  t_error_rec — KIND: record; TYPE: RECORD(error_id NUMBER, package_name VARCHAR2(60), procedure_name VARCHAR2(60), error_message VARCHAR2(4000), error_date DATE, username VARCHAR2(30))

**METHODS:**
  **PROCEDURE log_error(p_package IN VARCHAR2, p_procedure IN VARCHAR2, p_message IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L23-28]
  - What it does: Declares the shared error-logging entry point for all packages/forms; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity) when not supplied.
  - Data in/out: Inputs — p_package, p_procedure, p_message (required), p_user (default USER). Output — none (procedure).

  **PROCEDURE log_info(p_package IN VARCHAR2, p_procedure IN VARCHAR2, p_message IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L30-35]
  - What it does: Declares the shared informational-logging entry point; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity) when not supplied.
  - Data in/out: Inputs — p_package, p_procedure, p_message (required), p_user (default USER). Output — none (procedure).

  **FUNCTION get_param(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L40-43]
  - What it does: Declares retrieval of a string configuration parameter by group/code; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_group, p_code. Output — returns the parameter value as VARCHAR2.

  **FUNCTION get_param_number(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN NUMBER** [SOURCE: L45-48]
  - What it does: Declares the numeric-typed variant of get_param; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_group, p_code. Output — returns the parameter value as NUMBER.

  **FUNCTION get_param_date(p_group IN VARCHAR2, p_code IN VARCHAR2) RETURN DATE** [SOURCE: L50-53]
  - What it does: Declares the date-typed variant of get_param; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_group, p_code. Output — returns the parameter value as DATE.

  **PROCEDURE set_param(p_group IN VARCHAR2, p_code IN VARCHAR2, p_value IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L55-60]
  - What it does: Declares a write/update of a configuration parameter; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity) when not supplied.
  - Data in/out: Inputs — p_group, p_code, p_value (required), p_user (default USER). Output — none (procedure).

  **FUNCTION business_days_between(p_start_date IN DATE, p_end_date IN DATE) RETURN NUMBER** [SOURCE: L65-68]
  - What it does: Declares a count of business days between two dates; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_start_date, p_end_date. Output — returns NUMBER count of business days.

  **FUNCTION add_business_days(p_date IN DATE, p_days IN NUMBER) RETURN DATE** [SOURCE: L70-73]
  - What it does: Declares addition of N business days to a date; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_date, p_days. Output — returns the resulting DATE.

  **FUNCTION get_fiscal_year(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER** [SOURCE: L75-77]
  - What it does: Declares derivation of the fiscal year for a date (defaults to today); implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_date (default SYSDATE). Output — returns NUMBER fiscal year.

  **FUNCTION get_fiscal_quarter(p_date IN DATE DEFAULT SYSDATE) RETURN NUMBER** [SOURCE: L79-81]
  - What it does: Declares derivation of the fiscal quarter for a date (defaults to today); implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_date (default SYSDATE). Output — returns NUMBER fiscal quarter.

  **FUNCTION format_phone(p_phone IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L86-88]
  - What it does: Declares formatting of a raw phone string into display form; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_phone. Output — returns formatted VARCHAR2.

  **FUNCTION format_ssn_masked(p_ssn IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L90-92]
  - What it does: Declares production of a masked (partially hidden) SSN representation; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file; existence of this function implies SSNs must be masked before display elsewhere.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: Masking function implies SSN is treated as sensitive PII; masking pattern itself is UNKNOWN without the body.
  - Data in/out: Input — p_ssn. Output — returns masked VARCHAR2.

  **FUNCTION format_currency(p_amount IN NUMBER, p_currency_code IN VARCHAR2 DEFAULT 'USD') RETURN VARCHAR2** [SOURCE: L94-97]
  - What it does: Declares formatting of a numeric amount as a currency string, defaulting to USD; implementation not present in this spec file.
  - Business rules: Default currency is 'USD' when p_currency_code is not supplied.
  - Numbers & thresholds: None numeric (the default is the string 'USD').
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_amount (required), p_currency_code (default 'USD'). Output — returns formatted VARCHAR2.

  **FUNCTION format_name(p_first_name IN VARCHAR2, p_last_name IN VARCHAR2, p_format IN VARCHAR2 DEFAULT 'FL') RETURN VARCHAR2** [SOURCE: L99-103]
  - What it does: Declares name formatting per a format code; implementation not present in this spec file.
  - Business rules: Default format is 'FL' (First Last); 'LF' produces "Last, First" per the inline comment at L102.
  - Numbers & thresholds: None.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_first_name, p_last_name (required), p_format (default 'FL'). Output — returns formatted VARCHAR2 name.

  **FUNCTION is_valid_email(p_email IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L108-110]
  - What it does: Declares email-format validation; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — validation rule/regex not visible in the spec.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: Acts as input validation for email fields; detail UNKNOWN without the body.
  - Data in/out: Input — p_email. Output — returns BOOLEAN.

  **FUNCTION is_valid_phone(p_phone IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L112-114]
  - What it does: Declares phone-format validation; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — validation rule/regex not visible in the spec.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: Acts as input validation for phone fields; detail UNKNOWN without the body.
  - Data in/out: Input — p_phone. Output — returns BOOLEAN.

  **FUNCTION is_valid_ssn(p_ssn IN VARCHAR2) RETURN BOOLEAN** [SOURCE: L116-118]
  - What it does: Declares SSN-format validation; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — validation rule/regex not visible in the spec.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: Acts as input validation for a sensitive PII field (SSN); detail UNKNOWN without the body.
  - Data in/out: Input — p_ssn. Output — returns BOOLEAN.

**DEPENDENCIES:**
  Data touched:
  - Reads: None (spec only — no SQL visible in this file)
  - Writes: None (spec only — no SQL visible in this file)

  Config/env: get_param/get_param_number/get_param_date/set_param imply a configuration store keyed by (group, code) — the backing table is not named in this file.
  External integrations: None

**GAPS:**
  This is a package specification only; the package body (PKG_COMMON.pkb) with actual logic (config table name, validation regexes, formatting rules, masking pattern) was not provided in this chunk — all implementation detail is NOT_ANALYZED. Header comment states "Dependencies: None (base package - no cross-package dependencies)", consistent with no CALLS lines above.

---

*[pipeline status — type: plsql-spec · pass: correction · attempt: 1 · coverage: 100% (numbers 3/3 · procedures 17/17 · units 17/17 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_EMPLOYEE.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Declares the core employee-management interface — CRUD, employment lifecycle (transfer/promote/terminate/rehire), org-chart/headcount queries, and validation — used by the HRMS_EMPLOYEE and HRMS_DEPARTMENT forms and batch jobs.

**STRUCTURES:**
  g_current_user — KIND: field (package global variable); TYPE: VARCHAR2(30)
  g_current_emp_id — KIND: field (package global variable); TYPE: NUMBER(10)
  g_current_dept_id — KIND: field (package global variable); TYPE: NUMBER(10)
  g_debug_mode — KIND: field (package global variable); TYPE: BOOLEAN, default FALSE
  e_employee_not_found — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20001)
  e_duplicate_emp_number — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20002)
  e_invalid_department — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20003)
  e_invalid_manager — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20004)
  e_termination_error — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20005)
  t_emp_rec — KIND: record; TYPE: RECORD(emp_id/emp_number/first_name/last_name/hire_date/dept_id/job_id/manager_emp_id/employment_status all %TYPE of EMPLOYEES columns; base_salary NUMBER(12,2))
  t_emp_cursor — KIND: type (ref cursor); TYPE: REF CURSOR
  t_emp_id_table — KIND: type (collection); TYPE: TABLE OF NUMBER(10) INDEX BY BINARY_INTEGER
  t_emp_rec_table — KIND: type (collection); TYPE: TABLE OF t_emp_rec INDEX BY BINARY_INTEGER

**METHODS:**
  **FUNCTION create_employee(p_first_name IN VARCHAR2, p_last_name IN VARCHAR2, p_hire_date IN DATE, p_dept_id IN NUMBER, p_job_id IN NUMBER, p_manager_emp_id IN NUMBER DEFAULT NULL, p_location_code IN VARCHAR2 DEFAULT NULL, p_employment_type IN VARCHAR2 DEFAULT 'FULL_TIME', p_base_salary IN NUMBER DEFAULT NULL, p_email IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L55-67]
  - What it does: Declares creation of a new employee record; implementation not present in this spec file.
  - Business rules: Default employment type is 'FULL_TIME' when not supplied.
  - Numbers & thresholds: None numeric (defaults are NULL or the string 'FULL_TIME').
  - Security & error handling: p_user defaults to USER (session identity); e_duplicate_emp_number/e_invalid_department/e_invalid_manager (ORA -20002/-20003/-20004) are declared for this package and plausibly raised here, but raise sites are UNKNOWN without the body.
  - Data in/out: Inputs — p_first_name, p_last_name, p_hire_date, p_dept_id, p_job_id (required); p_manager_emp_id, p_location_code, p_employment_type (default 'FULL_TIME'), p_base_salary, p_email, p_user (default USER) all optional. Output — returns new NUMBER emp_id.

  **PROCEDURE update_employee(p_emp_id IN NUMBER, p_first_name IN VARCHAR2 DEFAULT NULL, p_last_name IN VARCHAR2 DEFAULT NULL, p_email IN VARCHAR2 DEFAULT NULL, p_phone_work IN VARCHAR2 DEFAULT NULL, p_phone_mobile IN VARCHAR2 DEFAULT NULL, p_address_line1 IN VARCHAR2 DEFAULT NULL, p_address_line2 IN VARCHAR2 DEFAULT NULL, p_city IN VARCHAR2 DEFAULT NULL, p_state_province IN VARCHAR2 DEFAULT NULL, p_postal_code IN VARCHAR2 DEFAULT NULL, p_country_code IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L69-83]
  - What it does: Declares an update of an existing employee's contact/name/address fields; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — likely partial-update-by-NULL semantics, but not visible in the spec.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_employee_not_found (ORA -20001) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_emp_id (required); all other fields optional (default NULL), p_user (default USER). Output — none (procedure).

  **FUNCTION get_employee(p_emp_id IN NUMBER) RETURN t_emp_rec** [SOURCE: L85-87]
  - What it does: Declares a single-employee lookup by id; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: e_employee_not_found (ORA -20001) is declared for this package and plausibly raised when p_emp_id doesn't exist.
  - Data in/out: Input — p_emp_id. Output — returns t_emp_rec.

  **FUNCTION get_employee_by_number(p_emp_number IN VARCHAR2) RETURN t_emp_rec** [SOURCE: L89-91]
  - What it does: Declares a single-employee lookup by employee number; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: e_employee_not_found (ORA -20001) is declared for this package and plausibly raised when p_emp_number doesn't exist.
  - Data in/out: Input — p_emp_number. Output — returns t_emp_rec.

  **PROCEDURE search_employees(p_cursor OUT t_emp_cursor, p_last_name IN VARCHAR2 DEFAULT NULL, p_first_name IN VARCHAR2 DEFAULT NULL, p_dept_id IN NUMBER DEFAULT NULL, p_status IN VARCHAR2 DEFAULT NULL, p_location_code IN VARCHAR2 DEFAULT NULL, p_hire_date_from IN DATE DEFAULT NULL, p_hire_date_to IN DATE DEFAULT NULL)** [SOURCE: L93-102]
  - What it does: Declares a multi-criteria employee search returning a ref cursor; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — all optional filter criteria (last/first name, dept, status, location, hire-date range). Output — p_cursor OUT ref cursor of matching employees.

  **PROCEDURE transfer_employee(p_emp_id IN NUMBER, p_new_dept_id IN NUMBER, p_new_job_id IN NUMBER DEFAULT NULL, p_new_manager_id IN NUMBER DEFAULT NULL, p_new_location IN VARCHAR2 DEFAULT NULL, p_effective_date IN DATE DEFAULT SYSDATE, p_reason_code IN VARCHAR2 DEFAULT NULL, p_comments IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L107-117]
  - What it does: Declares a department/job/manager/location transfer for an employee, effective a given date (defaults to today); implementation not present in this spec file.
  - Business rules: Default effective date is SYSDATE (today) when not supplied.
  - Numbers & thresholds: None numeric.
  - Security & error handling: p_user defaults to USER (session identity); e_invalid_department/e_invalid_manager (ORA -20003/-20004) are declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_emp_id, p_new_dept_id (required); p_new_job_id, p_new_manager_id, p_new_location, p_effective_date (default SYSDATE), p_reason_code, p_comments, p_user (default USER) optional. Output — none (procedure).

  **PROCEDURE promote_employee(p_emp_id IN NUMBER, p_new_job_id IN NUMBER, p_new_salary IN NUMBER, p_effective_date IN DATE DEFAULT SYSDATE, p_comments IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L119-126]
  - What it does: Declares a job/salary promotion for an employee, effective a given date (defaults to today); implementation not present in this spec file. Header comment flags a circular dependency with PKG_PAYROLL for salary validation.
  - Business rules: Default effective date is SYSDATE (today) when not supplied. Per header, salary validation is expected to involve PKG_PAYROLL, creating a circular package dependency (known issue).
  - Numbers & thresholds: None numeric in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_employee_not_found (ORA -20001) plausibly raised here.
  - Data in/out: Inputs — p_emp_id, p_new_job_id, p_new_salary (required); p_effective_date (default SYSDATE), p_comments, p_user (default USER) optional. Output — none (procedure).

  **PROCEDURE terminate_employee(p_emp_id IN NUMBER, p_termination_date IN DATE, p_reason IN VARCHAR2, p_comments IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L128-134]
  - What it does: Declares termination of an employee's employment; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_termination_error (ORA -20005) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_emp_id, p_termination_date, p_reason (required); p_comments, p_user (default USER) optional. Output — none (procedure).

  **PROCEDURE rehire_employee(p_emp_id IN NUMBER, p_rehire_date IN DATE, p_dept_id IN NUMBER, p_job_id IN NUMBER, p_base_salary IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L136-143]
  - What it does: Declares rehiring of a previously terminated employee; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_emp_id, p_rehire_date, p_dept_id, p_job_id, p_base_salary (required), p_user (default USER). Output — none (procedure).

  **FUNCTION get_direct_reports(p_manager_emp_id IN NUMBER) RETURN t_emp_id_table** [SOURCE: L148-150]
  - What it does: Declares retrieval of the emp_id list of an employee's direct reports; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_manager_emp_id. Output — returns t_emp_id_table (collection of NUMBER(10) emp_ids).

  **FUNCTION get_org_chart(p_root_emp_id IN NUMBER, p_max_depth IN NUMBER DEFAULT 10) RETURN t_emp_cursor** [SOURCE: L152-155]
  - What it does: Declares retrieval of the org-chart hierarchy under a root employee, bounded by depth; implementation not present in this spec file. Header comment flags that this function's recursive SQL "times out for deep hierarchies" (known issue).
  - Business rules: Default max recursion depth is 10 levels when not supplied.
  - Numbers & thresholds: p_max_depth DEFAULT 10 (org-chart recursion depth cap).
  - Security & error handling: Known performance issue per header comment: recursive SQL times out for deep hierarchies; no explicit error handling visible in the spec.
  - Data in/out: Inputs — p_root_emp_id (required), p_max_depth (default 10). Output — returns t_emp_cursor of the org-chart rows.

  **FUNCTION get_headcount_by_dept(p_dept_id IN NUMBER DEFAULT NULL, p_as_of_date IN DATE DEFAULT SYSDATE) RETURN NUMBER** [SOURCE: L157-160]
  - What it does: Declares a headcount count, optionally scoped to a department and an as-of date (defaults to today); implementation not present in this spec file.
  - Business rules: Default as-of date is SYSDATE (today); p_dept_id NULL implies all departments.
  - Numbers & thresholds: None numeric besides the defaults noted.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_dept_id (default NULL/all), p_as_of_date (default SYSDATE). Output — returns NUMBER headcount.

  **FUNCTION get_tenure_years(p_emp_id IN NUMBER) RETURN NUMBER** [SOURCE: L162-164]
  - What it does: Declares computation of an employee's tenure in years; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_emp_id. Output — returns NUMBER years of tenure.

  **FUNCTION is_active(p_emp_id IN NUMBER) RETURN BOOLEAN** [SOURCE: L166-168]
  - What it does: Declares an active-employment status check; implementation not present in this spec file. Header comment (on PKG_PAYROLL) notes a circular dependency tied to this kind of "is_active" check.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_emp_id. Output — returns BOOLEAN.

  **FUNCTION validate_employee(p_emp_id IN NUMBER) RETURN BOOLEAN** [SOURCE: L173-175]
  - What it does: Declares a general employee-validity check; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_emp_id. Output — returns BOOLEAN.

  **FUNCTION emp_exists(p_emp_id IN NUMBER) RETURN BOOLEAN** [SOURCE: L177-179]
  - What it does: Declares an existence check for an emp_id; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_emp_id. Output — returns BOOLEAN.

  **FUNCTION generate_emp_number RETURN VARCHAR2** [SOURCE: L184]
  - What it does: Declares generation of a new unique employee number; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — format/sequence rule not visible in the spec.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — none. Output — returns a new VARCHAR2 employee number.

  **PROCEDURE set_session_context(p_user IN VARCHAR2, p_emp_id IN NUMBER)** [SOURCE: L186-189]
  - What it does: Declares initialization of the package's session-state globals (g_current_user/g_current_emp_id/g_current_dept_id) for the calling user/employee; implementation not present in this spec file. Referenced elsewhere (e.g. called from PKG_SECURITY.authenticate per prior chunk) to bind a session to an employee context.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_user, p_emp_id. Output — none (procedure); presumably sets g_current_user/g_current_emp_id/g_current_dept_id package globals.

**DEPENDENCIES:**
  Data touched:
  - Reads: None observed in this spec file (t_emp_rec fields reference EMPLOYEES columns via %TYPE for structure only, not a data read)
  - Writes: None observed in this spec file

  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_AUDIT | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_NOTIFICATION | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_PAYROLL | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: None
  External integrations: None

**GAPS:**
  This is a package specification only; the package body (PKG_EMPLOYEE.pkb) was not provided in this chunk — all business logic, exception raise sites, and table reads/writes are NOT_ANALYZED. Header comment (L8-10) documents two known issues carried over from the body: a circular dependency with PKG_PAYROLL for salary validation, and get_org_chart's recursive SQL timing out for deep hierarchies (mitigated only by the p_max_depth=10 default, per L154).

---

*[pipeline status — type: plsql-spec · pass: correction · attempt: 1 · coverage: 100% (numbers 8/8 · procedures 18/18 · units 18/18 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_INTEGRATION.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Declares the external-system integration interface — GL journal posting, benefits-provider feed export, time & attendance import, and org-structure sync — run by the nightly/weekly batch scheduler.

**STRUCTURES:**
  t_gl_entry — KIND: record; TYPE: RECORD(journal_date DATE, account_code VARCHAR2(30), debit_amount NUMBER(15,2), credit_amount NUMBER(15,2), description VARCHAR2(200), reference VARCHAR2(100))
  t_gl_entry_table — KIND: type (collection); TYPE: TABLE OF t_gl_entry INDEX BY BINARY_INTEGER

**METHODS:**
  **PROCEDURE generate_gl_journal(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L26-29]
  - What it does: Declares generation of a GL (general ledger) journal for a payroll run; implementation not present in this spec file. Header comment states GL posting uses flat-file exchange (UTL_FILE) rather than an API (known issue).
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: Known issue per header: no retry logic for failed file transfers. p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_run_id (required), p_user (default USER). Output — none (procedure); presumably writes a flat file via UTL_FILE per header comment.

  **PROCEDURE export_benefits_feed(p_effective_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L31-34]
  - What it does: Declares export of a benefits-provider feed effective a given date (defaults to today); implementation not present in this spec file. Header comment states the feed format is vendor-specific (ADP format) (known issue).
  - Business rules: Default effective date is SYSDATE (today) when not supplied.
  - Numbers & thresholds: None numeric.
  - Security & error handling: Known issue per header: no retry logic for failed file transfers; FTP credentials for this kind of feed are stored in SYSTEM_PARAMETERS in cleartext (see GAPS/security note below). p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_effective_date (default SYSDATE), p_user (default USER). Output — none (procedure); presumably writes/transmits a vendor-formatted feed file.

  **PROCEDURE import_time_attendance(p_file_name IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L36-39]
  - What it does: Declares import of a time & attendance file by name; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); p_file_name is taken as-is with no visible path/name validation in the spec.
  - Data in/out: Inputs — p_file_name (required), p_user (default USER). Output — none (procedure); presumably writes imported time/attendance data.

  **PROCEDURE sync_org_structure(p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L41-43]
  - What it does: Declares a synchronization of organizational structure (departments/hierarchy) with an external system; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Input — p_user (default USER). Output — none (procedure); presumably reads/writes org-structure data.

  **FUNCTION get_integration_status(p_integration_name IN VARCHAR2) RETURN VARCHAR2** [SOURCE: L45-47]
  - What it does: Declares a status lookup for a named integration; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_integration_name. Output — returns VARCHAR2 status.

**DEPENDENCIES:**
  Data touched:
  - Reads: None observed in this spec file
  - Writes: None observed in this spec file

  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_PAYROLL | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_EMPLOYEE | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: Per header comment (L12), FTP credentials for the integration feeds are stored in the SYSTEM_PARAMETERS table in cleartext — a security-relevant configuration finding, though the actual key names are not visible in this spec file.
  External integrations: GL/accounting system (flat-file exchange via UTL_FILE, per header); benefits provider using ADP's feed format; time & attendance source system (file import); an external org-structure system (sync target unnamed).

**GAPS:**
  This is a package specification only; the package body (PKG_INTEGRATION.pkb) was not provided in this chunk — all implementation detail is NOT_ANALYZED. Header comment (L8-12) documents four known issues carried into the body: GL posting uses UTL_FILE flat files instead of an API; benefits feed is tied to ADP's vendor-specific format; no retry logic on failed file transfers; and FTP credentials are stored in SYSTEM_PARAMETERS in cleartext (a security vulnerability — plaintext credential storage).

---

*[pipeline status — type: plsql-spec · pass: correction · attempt: 1 · coverage: 100% (numbers 4/4 · procedures 5/5 · units 5/5 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_LEAVE.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Declares the leave-management interface — leave requests, approvals, balance tracking, and accrual/carryover batch processing — used by the HRMS_LEAVE form, self-service portal, and the batch accrual job.

**STRUCTURES:**
  e_insufficient_balance — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20201)
  e_overlapping_leave — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20202)
  e_invalid_leave_type — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20203)
  e_approval_error — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20204)
  t_leave_cursor — KIND: type (ref cursor); TYPE: REF CURSOR

**METHODS:**
  **FUNCTION submit_leave_request(p_emp_id IN NUMBER, p_leave_type_id IN NUMBER, p_start_date IN DATE, p_end_date IN DATE, p_half_day_flag IN CHAR DEFAULT 'N', p_half_day_period IN VARCHAR2 DEFAULT NULL, p_reason IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L28-37]
  - What it does: Declares submission of a new leave request, with optional half-day flag; implementation not present in this spec file. Header comment flags that overlapping-leave detection does not account for half-day requests (known issue).
  - Business rules: Default half-day flag is 'N' (full day) when not supplied. Known issue: half-day requests are not correctly accounted for in overlap detection (see check_leave_overlap).
  - Numbers & thresholds: None numeric.
  - Security & error handling: p_user defaults to USER (session identity); e_overlapping_leave/e_invalid_leave_type (ORA -20202/-20203) are declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_emp_id, p_leave_type_id, p_start_date, p_end_date (required); p_half_day_flag (default 'N'), p_half_day_period, p_reason, p_user (default USER) optional. Output — returns new NUMBER request_id.

  **PROCEDURE approve_leave_request(p_request_id IN NUMBER, p_approver_emp_id IN NUMBER, p_comments IN VARCHAR2 DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L39-44]
  - What it does: Declares approval of a pending leave request; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_approval_error (ORA -20204) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_request_id, p_approver_emp_id (required), p_comments, p_user (default USER) optional. Output — none (procedure).

  **PROCEDURE reject_leave_request(p_request_id IN NUMBER, p_approver_emp_id IN NUMBER, p_comments IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L46-51]
  - What it does: Declares rejection of a pending leave request, with a required comment; implementation not present in this spec file.
  - Business rules: A rejection comment (p_comments) is mandatory (no default), unlike approve_leave_request where it's optional.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_approval_error (ORA -20204) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_request_id, p_approver_emp_id, p_comments (all required), p_user (default USER). Output — none (procedure).

  **PROCEDURE cancel_leave_request(p_request_id IN NUMBER, p_reason IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L53-57]
  - What it does: Declares cancellation of a leave request, with a required reason; implementation not present in this spec file.
  - Business rules: A cancellation reason (p_reason) is mandatory (no default).
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_request_id, p_reason (required), p_user (default USER). Output — none (procedure).

  **FUNCTION get_leave_balance(p_emp_id IN NUMBER, p_leave_type_id IN NUMBER, p_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER** [SOURCE: L62-66]
  - What it does: Declares retrieval of an employee's leave balance for a type/year (defaults to the current year); implementation not present in this spec file.
  - Business rules: Default year is the current calendar year (EXTRACT(YEAR FROM SYSDATE)) when not supplied.
  - Numbers & thresholds: None hardcoded (year default is computed from SYSDATE, not a literal).
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_emp_id, p_leave_type_id (required), p_year (default current year). Output — returns NUMBER balance.

  **PROCEDURE adjust_leave_balance(p_emp_id IN NUMBER, p_leave_type_id IN NUMBER, p_adjustment IN NUMBER, p_reason IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L68-74]
  - What it does: Declares a manual adjustment (positive or negative) to a leave balance, with a required reason; implementation not present in this spec file.
  - Business rules: An adjustment reason (p_reason) is mandatory (no default).
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_emp_id, p_leave_type_id, p_adjustment, p_reason (required), p_user (default USER). Output — none (procedure).

  **PROCEDURE initialize_balances(p_emp_id IN NUMBER, p_year IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L76-80]
  - What it does: Declares initialization of leave balances for an employee/year; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_emp_id, p_year (required), p_user (default USER). Output — none (procedure).

  **PROCEDURE run_monthly_accrual(p_accrual_date IN DATE DEFAULT SYSDATE, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L85-88]
  - What it does: Declares the batch monthly leave-accrual run, defaulting to today's date; implementation not present in this spec file.
  - Business rules: Default accrual date is SYSDATE (today) when not supplied.
  - Numbers & thresholds: None numeric in this declaration (accrual rate(s) are UNKNOWN without the body).
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_accrual_date (default SYSDATE), p_user (default USER). Output — none (procedure).

  **PROCEDURE process_carryover(p_year IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L90-93]
  - What it does: Declares the batch year-end leave-carryover process; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — carryover cap/rule not visible in the spec.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_year (required), p_user (default USER). Output — none (procedure).

  **PROCEDURE expire_carryover(p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L95-97]
  - What it does: Declares the batch job that expires previously carried-over leave; implementation not present in this spec file. Header comment flags that this job "sometimes double-expires if run twice on same day" (known issue).
  - Business rules: Known issue: re-running this job on the same day can double-expire carryover balances (no idempotency guard, per header).
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); no idempotency/guard against duplicate same-day runs is documented.
  - Data in/out: Input — p_user (default USER). Output — none (procedure).

  **PROCEDURE get_pending_requests(p_cursor OUT t_leave_cursor, p_approver_id IN NUMBER)** [SOURCE: L102-105]
  - What it does: Declares retrieval of pending leave requests awaiting a given approver; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_approver_id. Output — p_cursor OUT ref cursor of pending requests.

  **PROCEDURE get_team_calendar(p_cursor OUT t_leave_cursor, p_manager_id IN NUMBER, p_start_date IN DATE, p_end_date IN DATE)** [SOURCE: L107-112]
  - What it does: Declares retrieval of a team's leave calendar for a manager over a date range; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_manager_id, p_start_date, p_end_date. Output — p_cursor OUT ref cursor of team leave rows.

  **FUNCTION calculate_business_days(p_start_date IN DATE, p_end_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN NUMBER** [SOURCE: L114-118]
  - What it does: Declares a business-day count between two dates, optionally location-aware (for holidays); implementation not present in this spec file. Header comment flags that holiday detection only checks exact date match, not observed dates (known issue).
  - Business rules: Known issue: holiday matching is by exact date only — it does not account for "observed" holiday dates (e.g. a holiday moved to the nearest weekday).
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_start_date, p_end_date (required), p_location_code (optional). Output — returns NUMBER business-day count.

  **FUNCTION check_leave_overlap(p_emp_id IN NUMBER, p_start_date IN DATE, p_end_date IN DATE, p_exclude_request_id IN NUMBER DEFAULT NULL) RETURN BOOLEAN** [SOURCE: L120-125]
  - What it does: Declares a check for overlapping leave requests for an employee, optionally excluding one request id (e.g. the one being edited); implementation not present in this spec file. Header comment flags that this detection does not account for half-day requests (known issue).
  - Business rules: Known issue: overlap detection does not correctly distinguish half-day requests, so two half-day requests on the same date may be incorrectly flagged (or not flagged) as overlapping.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_emp_id, p_start_date, p_end_date (required), p_exclude_request_id (optional). Output — returns BOOLEAN (overlap found).

**DEPENDENCIES:**
  Data touched:
  - Reads: None observed in this spec file
  - Writes: None observed in this spec file

  CALLS: PKG_EMPLOYEE | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_AUDIT | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_NOTIFICATION | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: None
  External integrations: None

**GAPS:**
  This is a package specification only; the package body (PKG_LEAVE.pkb) was not provided in this chunk — all business logic, accrual rates/caps, and table reads/writes are NOT_ANALYZED. Header comment (L8-11) documents three known issues carried into the body: overlapping-leave detection ignores half-day requests; the carryover-expiry job can double-expire if run twice in one day; and holiday detection matches exact dates only, not observed/shifted holiday dates.

---

*[pipeline status — type: plsql-spec · pass: correction · attempt: 1 · coverage: 100% (numbers 4/4 · procedures 14/14 · units 14/14 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Declares the notification-queue interface — sending, batch processing, retry, and cancellation of email/in-app/SMS notifications — used by PKG_EMPLOYEE, PKG_LEAVE, PKG_PAYROLL, and PKG_PERFORMANCE.

**STRUCTURES:**
  None (this spec declares no package-level types, constants, or exceptions — only the four subprogram signatures listed under METHODS).

**METHODS:**
  **PROCEDURE send_notification(p_recipient_emp_id IN NUMBER DEFAULT NULL, p_recipient_email IN VARCHAR2 DEFAULT NULL, p_type IN VARCHAR2 DEFAULT 'EMAIL', p_subject IN VARCHAR2, p_body IN CLOB, p_priority IN NUMBER DEFAULT 5, p_reference_table IN VARCHAR2 DEFAULT NULL, p_reference_id IN NUMBER DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L14-24]
  - What it does: Declares enqueuing of a notification to a recipient (by emp_id or raw email), of a given type, with a priority; implementation not present in this spec file. Header comment flags HTML email templates are stored as string constants (maintenance nightmare) and that UTL_MAIL config is hard-coded to a legacy SMTP server (known issues).
  - Business rules: Default notification type is 'EMAIL'. Default priority is 5. p_recipient_emp_id and p_recipient_email are both optional/nullable — at least one is presumably expected to be supplied, though that constraint is not visible in the spec.
  - Numbers & thresholds: p_priority DEFAULT 5.
  - Security & error handling: p_user defaults to USER (session identity); no rate limiting is documented (header notes bulk operations can flood the queue — known issue).
  - Data in/out: Inputs — p_subject, p_body (required); p_recipient_emp_id, p_recipient_email, p_type (default 'EMAIL'), p_priority (default 5), p_reference_table, p_reference_id, p_user (default USER) optional. Output — none (procedure); presumably inserts a queued-notification row.

  **PROCEDURE process_queue(p_batch_size IN NUMBER DEFAULT 50, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L26-29]
  - What it does: Declares batch processing/dispatch of queued notifications, a batch at a time; implementation not present in this spec file.
  - Business rules: Default batch size is 50 notifications per run when not supplied.
  - Numbers & thresholds: p_batch_size DEFAULT 50.
  - Security & error handling: p_user defaults to USER (session identity); header comment notes no rate limiting exists elsewhere in the package, so large batches could flood downstream channels (known issue).
  - Data in/out: Inputs — p_batch_size (default 50), p_user (default USER). Output — none (procedure); presumably updates queued-notification rows to sent/failed and dispatches via UTL_MAIL or similar.

  **PROCEDURE retry_failed(p_max_retries IN NUMBER DEFAULT 3, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L31-34]
  - What it does: Declares retry of previously failed notifications up to a maximum retry count; implementation not present in this spec file.
  - Business rules: Default maximum retry count is 3 attempts when not supplied.
  - Numbers & thresholds: p_max_retries DEFAULT 3.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_max_retries (default 3), p_user (default USER). Output — none (procedure); presumably updates failed-notification rows and re-attempts delivery.

  **PROCEDURE cancel_notification(p_notification_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L36-39]
  - What it does: Declares cancellation of a queued (not-yet-sent) notification by id; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_notification_id (required), p_user (default USER). Output — none (procedure); presumably updates the notification row to a cancelled status.

**DEPENDENCIES:**
  Data touched:
  - Reads: None observed in this spec file
  - Writes: None observed in this spec file

  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: UTL_MAIL SMTP server configuration is, per header comment (L9), hard-coded to a legacy SMTP server rather than externalized — the actual config key/value is not visible in this spec file.
  External integrations: UTL_MAIL (or equivalent) for email dispatch, per header comment; SMS/in-app channels implied by p_type but not detailed in this spec.

**GAPS:**
  This is a package specification only; the package body (PKG_NOTIFICATION.pkb) was not provided in this chunk — all queue-table structure, dispatch logic, and error handling are NOT_ANALYZED. Header comment (L9-11) documents three known issues carried into the body: UTL_MAIL configuration hard-coded to a legacy SMTP server; no rate limiting, so bulk operations can flood the queue; and HTML email templates stored as string constants (maintenance burden).

---

*[pipeline status — type: plsql-spec · pass: correction · attempt: 1 · coverage: 100% (numbers 3/3 · procedures 4/4 · units 4/4 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Declares the payroll-processing interface — salary records, pay-period management, payroll-run calculation/approval/reversal, tax withholding calculations, and payslip/pay-register reporting — used by the HRMS_PAYROLL form and the DBMS_SCHEDULER batch scheduler.

**STRUCTURES:**
  e_invalid_salary — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20101)
  e_period_closed — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20102)
  e_run_already_paid — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20103)
  e_calculation_error — KIND: exception; TYPE: N/A (PRAGMA EXCEPTION_INIT to ORA -20104)
  t_payslip_rec — KIND: record; TYPE: RECORD(emp_id NUMBER(10), emp_number VARCHAR2(20), emp_name VARCHAR2(101), period_name VARCHAR2(50), gross_pay NUMBER(12,2), total_deductions NUMBER(12,2), net_pay NUMBER(12,2), federal_tax NUMBER(12,2), state_tax NUMBER(12,2), social_security NUMBER(12,2), medicare NUMBER(12,2), ytd_gross NUMBER(15,2), ytd_net NUMBER(15,2))
  t_payslip_cursor — KIND: type (ref cursor); TYPE: REF CURSOR

**METHODS:**
  **PROCEDURE create_salary_record(p_emp_id IN NUMBER, p_effective_date IN DATE, p_base_salary IN NUMBER, p_change_reason IN VARCHAR2 DEFAULT NULL, p_change_pct IN NUMBER DEFAULT NULL, p_currency_code IN VARCHAR2 DEFAULT 'USD', p_pay_frequency IN VARCHAR2 DEFAULT 'MONTHLY', p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L47-56]
  - What it does: Declares creation of a new salary record for an employee, effective a given date; implementation not present in this spec file.
  - Business rules: Default currency is 'USD'; default pay frequency is 'MONTHLY' when not supplied.
  - Numbers & thresholds: None numeric (defaults are the strings 'USD'/'MONTHLY').
  - Security & error handling: p_user defaults to USER (session identity); e_invalid_salary (ORA -20101) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_emp_id, p_effective_date, p_base_salary (required); p_change_reason, p_change_pct, p_currency_code (default 'USD'), p_pay_frequency (default 'MONTHLY'), p_user (default USER) optional. Output — none (procedure).

  **FUNCTION get_current_salary(p_emp_id IN NUMBER) RETURN NUMBER** [SOURCE: L58-60]
  - What it does: Declares retrieval of an employee's current base salary; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Input — p_emp_id. Output — returns NUMBER salary.

  **FUNCTION get_salary_as_of(p_emp_id IN NUMBER, p_as_of IN DATE) RETURN NUMBER** [SOURCE: L62-65]
  - What it does: Declares retrieval of an employee's salary as of a given historical date; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_emp_id, p_as_of. Output — returns NUMBER salary as of that date.

  **PROCEDURE create_pay_periods(p_year IN NUMBER, p_frequency IN VARCHAR2 DEFAULT 'MONTHLY', p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L70-74]
  - What it does: Declares generation of a year's worth of pay periods at a given frequency (defaults to monthly); implementation not present in this spec file.
  - Business rules: Default pay frequency is 'MONTHLY' when not supplied.
  - Numbers & thresholds: None numeric in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_year (required), p_frequency (default 'MONTHLY'), p_user (default USER). Output — none (procedure); presumably inserts pay-period rows.

  **PROCEDURE close_pay_period(p_period_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L76-79]
  - What it does: Declares closing of a pay period (locking it from further changes); implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_period_closed (ORA -20102) is declared for this package, plausibly raised elsewhere when an operation targets an already-closed period.
  - Data in/out: Input — p_period_id (required), p_user (default USER). Output — none (procedure); presumably updates the pay period's status.

  **FUNCTION get_current_period RETURN NUMBER** [SOURCE: L81]
  - What it does: Declares retrieval of the currently open pay period's id; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — none. Output — returns NUMBER period id.

  **FUNCTION create_payroll_run(p_period_id IN NUMBER, p_run_type IN VARCHAR2 DEFAULT 'REGULAR', p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L86-90]
  - What it does: Declares creation of a new payroll run for a pay period, defaulting to a 'REGULAR' run type; implementation not present in this spec file.
  - Business rules: Default run type is 'REGULAR' when not supplied.
  - Numbers & thresholds: None numeric in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_period_id (required), p_run_type (default 'REGULAR'), p_user (default USER). Output — returns new NUMBER run_id.

  **PROCEDURE calculate_payroll(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L92-95]
  - What it does: Declares the main payroll-calculation entry point for an entire run; implementation not present in this spec file. Header comment flags YTD accumulation resets incorrectly for mid-year hires in some edge cases (known issue).
  - Business rules: Known issue: YTD (year-to-date) accumulation can reset incorrectly for employees hired mid-year, in some edge cases.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_calculation_error (ORA -20104) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_run_id (required), p_user (default USER). Output — none (procedure); presumably invokes calculate_employee_pay per employee and writes payroll results.

  **PROCEDURE calculate_employee_pay(p_run_id IN NUMBER, p_emp_id IN NUMBER, p_period_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L97-102]
  - What it does: Declares per-employee pay calculation within a run/period; implementation not present in this spec file. Header comment flags that overtime calculation does not account for holidays correctly (known issue).
  - Business rules: Known issue: overtime calculation does not correctly account for holidays.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_calculation_error (ORA -20104) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_run_id, p_emp_id, p_period_id (required), p_user (default USER). Output — none (procedure); presumably writes the employee's pay-run result row(s).

  **PROCEDURE approve_payroll(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L104-107]
  - What it does: Declares approval of a calculated payroll run; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_run_already_paid (ORA -20103) is declared for this package, plausibly raised if approval is attempted on an already-paid run.
  - Data in/out: Input — p_run_id (required), p_user (default USER). Output — none (procedure); presumably updates the run's approval status.

  **PROCEDURE reverse_payroll(p_run_id IN NUMBER, p_reason IN VARCHAR2, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L109-113]
  - What it does: Declares reversal of a previously processed/approved payroll run, with a required reason; implementation not present in this spec file.
  - Business rules: A reversal reason (p_reason) is mandatory (no default).
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity); e_run_already_paid (ORA -20103) is declared for this package, plausibly raised if reversal is attempted on a run in an invalid state.
  - Data in/out: Inputs — p_run_id, p_reason (required), p_user (default USER). Output — none (procedure); presumably reverts the run's payroll results.

  **FUNCTION calculate_federal_tax(p_taxable_income IN NUMBER, p_filing_status IN VARCHAR2, p_allowances IN NUMBER DEFAULT 0, p_additional_wh IN NUMBER DEFAULT 0, p_pay_frequency IN VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER** [SOURCE: L118-124]
  - What it does: Declares federal tax withholding calculation from taxable income, filing status, allowances, and additional withholding; implementation not present in this spec file. Header comment flags that tax calculation uses hard-coded 2024 brackets in some paths (known issue).
  - Business rules: Default allowances is 0; default additional withholding is 0; default pay frequency is 'MONTHLY'. Known issue: hard-codes 2024 tax brackets in some code paths (bracket values themselves are in the body, not this spec).
  - Numbers & thresholds: p_allowances DEFAULT 0; p_additional_wh DEFAULT 0. Actual 2024 bracket rates/thresholds are NOT_ANALYZED — not visible in this spec file (body not included in this chunk).
  - Security & error handling: e_calculation_error (ORA -20104) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_taxable_income, p_filing_status (required); p_allowances (default 0), p_additional_wh (default 0), p_pay_frequency (default 'MONTHLY') optional. Output — returns NUMBER computed federal tax.

  **FUNCTION calculate_state_tax(p_taxable_income IN NUMBER, p_state_code IN VARCHAR2, p_filing_status IN VARCHAR2, p_allowances IN NUMBER DEFAULT 0, p_pay_frequency IN VARCHAR2 DEFAULT 'MONTHLY') RETURN NUMBER** [SOURCE: L126-132]
  - What it does: Declares state tax withholding calculation from taxable income, state code, filing status, and allowances; implementation not present in this spec file.
  - Business rules: Default allowances is 0; default pay frequency is 'MONTHLY'.
  - Numbers & thresholds: p_allowances DEFAULT 0. Actual per-state bracket rates/thresholds are NOT_ANALYZED — not visible in this spec file.
  - Security & error handling: e_calculation_error (ORA -20104) is declared for this package and plausibly raised here.
  - Data in/out: Inputs — p_taxable_income, p_state_code, p_filing_status (required); p_allowances (default 0), p_pay_frequency (default 'MONTHLY') optional. Output — returns NUMBER computed state tax.

  **FUNCTION calculate_fica(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER** [SOURCE: L134-137]
  - What it does: Declares Social Security (FICA) tax calculation from gross pay and YTD gross; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — FICA rate/wage base is not visible in this spec file (body not included in this chunk).
  - Numbers & thresholds: None in this declaration — the FICA rate and Social Security wage base are NOT_ANALYZED here.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_gross_pay, p_ytd_gross. Output — returns NUMBER computed FICA/Social Security tax.

  **FUNCTION calculate_medicare(p_gross_pay IN NUMBER, p_ytd_gross IN NUMBER) RETURN NUMBER** [SOURCE: L139-142]
  - What it does: Declares Medicare tax calculation from gross pay and YTD gross; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — Medicare rate (and any additional-Medicare surtax threshold) is not visible in this spec file.
  - Numbers & thresholds: None in this declaration — the Medicare rate is NOT_ANALYZED here.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_gross_pay, p_ytd_gross. Output — returns NUMBER computed Medicare tax.

  **PROCEDURE get_payslip(p_cursor OUT t_payslip_cursor, p_run_id IN NUMBER, p_emp_id IN NUMBER DEFAULT NULL)** [SOURCE: L147-151]
  - What it does: Declares retrieval of payslip row(s) for a run, optionally scoped to one employee; implementation not present in this spec file.
  - Business rules: p_emp_id NULL implies all employees in the run.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_run_id (required), p_emp_id (optional). Output — p_cursor OUT ref cursor of t_payslip_rec-shaped rows.

  **FUNCTION get_ytd_earnings(p_emp_id IN NUMBER, p_tax_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)) RETURN NUMBER** [SOURCE: L153-156]
  - What it does: Declares retrieval of an employee's year-to-date earnings for a tax year (defaults to the current year); implementation not present in this spec file. Header comment flags YTD accumulation resets incorrectly for mid-year hires in some edge cases (known issue, shared with calculate_payroll).
  - Business rules: Default tax year is the current calendar year. Known issue: YTD accumulation can reset incorrectly for mid-year hires in some edge cases.
  - Numbers & thresholds: None hardcoded (year default is computed from SYSDATE, not a literal).
  - Security & error handling: None visible in the spec.
  - Data in/out: Inputs — p_emp_id (required), p_tax_year (default current year). Output — returns NUMBER YTD earnings.

  **PROCEDURE generate_pay_register(p_run_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L158-161]
  - What it does: Declares generation of a pay register report for a run; implementation not present in this spec file.
  - Business rules: NOT_ANALYZED — body not present in this file.
  - Numbers & thresholds: None in this declaration.
  - Security & error handling: p_user defaults to USER (session identity).
  - Data in/out: Inputs — p_run_id (required), p_user (default USER). Output — none (procedure); presumably produces/writes a pay-register report.

**DEPENDENCIES:**
  Data touched:
  - Reads: None observed in this spec file
  - Writes: None observed in this spec file

  CALLS: PKG_EMPLOYEE | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_AUDIT | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_NOTIFICATION | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: None
  External integrations: None

**GAPS:**
  This is a package specification only; the package body (PKG_PAYROLL.pkb) was not provided in this chunk — the actual 2024 federal/state tax bracket tables, FICA/Medicare rates and wage bases, and all other calculation logic are NOT_ANALYZED (they must be captured when that body file is scanned). Header comment (L9-12) documents four known issues carried into the body: circular dependency with PKG_EMPLOYEE for the is_active check; hard-coded 2024 tax brackets in some code paths; overtime calculation not correctly accounting for holidays; and YTD accumulation resetting incorrectly for mid-year hires in some edge cases.

*[pipeline status — type: plsql-spec · pass: correction · attempt: 1 · coverage: 100% (numbers 12/12 · procedures 18/18 · units 18/18 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PERFORMANCE.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Performance review management — review cycles, self/manager assessments, goal tracking, and rating distribution/calibration.

**STRUCTURES:**
  t_review_cursor — KIND: type; TYPE: REF CURSOR

**METHODS:**
  **FUNCTION create_review_cycle(p_cycle_name IN VARCHAR2, p_cycle_year IN NUMBER, p_start_date IN DATE, p_end_date IN DATE, p_self_review_due IN DATE DEFAULT NULL, p_manager_review_due IN DATE DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L12-20]
  - What it does: Package spec only — signature indicates creating a new performance review cycle for a year, with a date range and optional self/manager review due dates, returning the generated cycle ID. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_cycle_name, p_cycle_year, p_start_date, p_end_date (required); due dates, user (optional). Output — NUMBER new cycle_id.

  **PROCEDURE open_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L22-25]
  - What it does: Package spec only — signature indicates opening a review cycle, making it active for submissions. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Input — p_cycle_id (required); p_user (optional). No return value.

  **PROCEDURE close_review_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L27-30]
  - What it does: Package spec only — signature indicates closing a review cycle, ending the submission window. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Input — p_cycle_id (required); p_user (optional). No return value.

  **FUNCTION create_review(p_cycle_id IN NUMBER, p_emp_id IN NUMBER, p_reviewer_emp_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L32-37]
  - What it does: Package spec only — signature indicates creating a single review instance for an employee/reviewer pair within a cycle, returning the generated review ID. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_cycle_id, p_emp_id, p_reviewer_emp_id (required); p_user (optional). Output — NUMBER new review_id.

  **PROCEDURE submit_self_assessment(p_review_id IN NUMBER, p_self_assessment IN CLOB, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L39-43]
  - What it does: Package spec only — signature indicates recording an employee's self-assessment text against a review. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_review_id, p_self_assessment (required); p_user (optional). No return value.

  **PROCEDURE submit_manager_review(p_review_id IN NUMBER, p_overall_rating IN NUMBER, p_manager_assessment IN CLOB, p_strengths IN CLOB DEFAULT NULL, p_improvement_areas IN CLOB DEFAULT NULL, p_development_plan IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L45-53]
  - What it does: Package spec only — signature indicates recording a manager's review — an overall rating plus assessment text, with optional strengths/improvement areas/development plan. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED — the rating scale/bounds for p_overall_rating are not visible in this spec.
  - Numbers & thresholds: None visible in this spec (rating scale not defined here).
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_review_id, p_overall_rating, p_manager_assessment (required); strengths, improvement areas, development plan, user (optional). No return value.

  **PROCEDURE acknowledge_review(p_review_id IN NUMBER, p_emp_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L55-59]
  - What it does: Package spec only — signature indicates recording an employee's acknowledgement of a completed review, with optional comments. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Input — p_review_id (required); comments, user (optional). No return value.

  **FUNCTION add_goal(p_review_id IN NUMBER, p_emp_id IN NUMBER, p_goal_title IN VARCHAR2, p_goal_description IN CLOB DEFAULT NULL, p_goal_category IN VARCHAR2 DEFAULT 'BUSINESS', p_weight_pct IN NUMBER DEFAULT 0, p_target_date IN DATE DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER) RETURN NUMBER** [SOURCE: L61-70]
  - What it does: Package spec only — signature indicates adding a goal to a review, with a category (defaults to 'BUSINESS') and a weight percentage (defaults to 0), returning the generated goal ID. Logic is in the package body (.pkb), not provided.
  - Business rules: Default goal category = 'BUSINESS'; default weight_pct = 0.
  - Numbers & thresholds: p_weight_pct default = 0.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_review_id, p_emp_id, p_goal_title (required); description, category, weight, target date, user (optional). Output — NUMBER new goal_id.

  **PROCEDURE update_goal_progress(p_goal_id IN NUMBER, p_progress_pct IN NUMBER, p_status IN VARCHAR2 DEFAULT NULL, p_comments IN CLOB DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L72-78]
  - What it does: Package spec only — signature indicates updating a goal's progress percentage/status/comments. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_goal_id, p_progress_pct (required); status, comments, user (optional). No return value.

  **PROCEDURE get_team_reviews(p_cursor OUT t_review_cursor, p_manager_id IN NUMBER, p_cycle_id IN NUMBER)** [SOURCE: L80-84]
  - What it does: Package spec only — signature indicates returning all reviews for a manager's team within a given cycle. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_manager_id, p_cycle_id. Output — p_cursor (OUT REF CURSOR) of team reviews.

  **FUNCTION get_rating_distribution(p_cycle_id IN NUMBER, p_dept_id IN NUMBER DEFAULT NULL) RETURN SYS_REFCURSOR** [SOURCE: L86-89]
  - What it does: Package spec only — signature indicates returning the distribution of ratings for a cycle, optionally filtered by department. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Input — p_cycle_id (required); p_dept_id (optional). Output — SYS_REFCURSOR of rating distribution.

  **PROCEDURE generate_reviews_for_cycle(p_cycle_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L91-94]
  - What it does: Package spec only — signature indicates bulk-generating review instances for all eligible employees in a cycle, likely calling create_review per employee. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Input — p_cycle_id (required); p_user (optional). No return value.

**DEPENDENCIES:**
  Data touched:
  - Reads: None visible in spec
  - Writes: None visible in spec

  CALLS: PKG_EMPLOYEE | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_AUDIT | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_NOTIFICATION | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: None
  External integrations: None

**GAPS:**
  Package body (PKG_PERFORMANCE.pkb) not provided — all subprogram logic, the rating scale/bounds, and calibration rules are UNRESOLVED/NOT_ANALYZED.

*[pipeline status — type: plsql-spec · pass: original · attempt: 1 · coverage: 100% (numbers 1/1 · procedures 12/12 · units 12/12 · structure 5/5)]*

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_REPORTING.pks ===

**IDENTITY:**
  KIND: package spec
  PURPOSE: Report generation — headcount, compensation, turnover, new hires, leave utilization, payroll summary, and EEO compliance reporting.

**STRUCTURES:**
  t_report_cursor — KIND: type; TYPE: REF CURSOR

**METHODS:**
  **PROCEDURE headcount_report(p_cursor OUT t_report_cursor, p_as_of_date IN DATE DEFAULT SYSDATE, p_dept_id IN NUMBER DEFAULT NULL, p_location IN VARCHAR2 DEFAULT NULL)** [SOURCE: L15-20]
  - What it does: Package spec only — signature indicates returning headcount as of a date (defaults to today), optionally filtered by department/location. Logic is in the package body (.pkb), not provided.
  - Business rules: As-of date defaults to SYSDATE.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_as_of_date (default SYSDATE); dept_id, location (optional filters). Output — p_cursor (OUT REF CURSOR) of headcount data.

  **PROCEDURE compensation_summary(p_cursor OUT t_report_cursor, p_dept_id IN NUMBER DEFAULT NULL, p_grade_id IN NUMBER DEFAULT NULL)** [SOURCE: L22-26]
  - What it does: Package spec only — signature indicates returning a compensation summary, optionally filtered by department/grade. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — dept_id, grade_id (optional filters). Output — p_cursor (OUT REF CURSOR) of compensation data.

  **PROCEDURE turnover_report(p_cursor OUT t_report_cursor, p_start_date IN DATE, p_end_date IN DATE, p_dept_id IN NUMBER DEFAULT NULL)** [SOURCE: L28-33]
  - What it does: Package spec only — signature indicates returning turnover data for a date range, optionally filtered by department. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_start_date, p_end_date (required); p_dept_id (optional). Output — p_cursor (OUT REF CURSOR) of turnover data.

  **PROCEDURE new_hires_report(p_cursor OUT t_report_cursor, p_start_date IN DATE, p_end_date IN DATE, p_dept_id IN NUMBER DEFAULT NULL)** [SOURCE: L35-40]
  - What it does: Package spec only — signature indicates returning new-hire data for a date range, optionally filtered by department. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Inputs — p_start_date, p_end_date (required); p_dept_id (optional). Output — p_cursor (OUT REF CURSOR) of new-hire data.

  **PROCEDURE leave_utilization_report(p_cursor OUT t_report_cursor, p_year IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE), p_dept_id IN NUMBER DEFAULT NULL)** [SOURCE: L42-46]
  - What it does: Package spec only — signature indicates returning leave utilization data for a year (defaults to current year), optionally filtered by department. Logic is in the package body (.pkb), not provided.
  - Business rules: Year defaults to current calendar year (EXTRACT(YEAR FROM SYSDATE)).
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Input — p_year (default current year); p_dept_id (optional). Output — p_cursor (OUT REF CURSOR) of leave utilization data.

  **PROCEDURE payroll_summary_report(p_cursor OUT t_report_cursor, p_period_id IN NUMBER)** [SOURCE: L48-51]
  - What it does: Package spec only — signature indicates returning a payroll summary for a specific pay period. Logic is in the package body (.pkb), not provided.
  - Business rules: NOT_ANALYZED.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED.
  - Data in/out: Input — p_period_id (required). Output — p_cursor (OUT REF CURSOR) of payroll summary data.

  **PROCEDURE eeo_compliance_report(p_cursor OUT t_report_cursor, p_as_of_date IN DATE DEFAULT SYSDATE)** [SOURCE: L53-56]
  - What it does: Package spec only — signature indicates returning an EEO compliance report as of a date (defaults to today). Logic is in the package body (.pkb), not provided.
  - Business rules: As-of date defaults to SYSDATE.
  - Numbers & thresholds: None visible.
  - Security & error handling: NOT_ANALYZED — EEO data is regulated/sensitive demographic data; access control is not visible in this spec.
  - Data in/out: Input — p_as_of_date (default SYSDATE). Output — p_cursor (OUT REF CURSOR) of EEO compliance data.

  **PROCEDURE refresh_reporting_tables(p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L58-60]
  - What it does: Package spec only — signature indicates refreshing denormalized reporting tables; header comment [L9] notes these are refreshed nightly and are stale during business hours (known limitation), and [L10] notes some reports use a hard-coded fiscal year start of October 1. Logic is in the package body (.pkb), not provided.
  - Business rules: Reporting tables refresh on a nightly cadence (per header comment), so intra-day data is stale. Some reports assume a fiscal year starting October 1 (hard-coded, per header comment [L10]).
  - Numbers & thresholds: Fiscal year start = October 1 (hard-coded in some reports, per header comment [L10] — exact usage NOT_ANALYZED; not shown in this spec's executable code since a .pks has none).
  - Security & error handling: Known limitation — denormalized reporting tables are stale during business hours, refreshed only nightly [L9, header comment].
  - Data in/out: Input — p_user (default USER). Output — side effect: refreshes reporting tables (denormalized copies); no return value.

**DEPENDENCIES:**
  Data touched:
  - Reads: None visible in spec
  - Writes: None visible in spec (refresh_reporting_tables presumably writes denormalized reporting tables per header comment; exact table names NOT_ANALYZED)

  CALLS: PKG_EMPLOYEE | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_PAYROLL | EVIDENCE: INFERRED | SOURCE: L6
  CALLS: PKG_COMMON | EVIDENCE: INFERRED | SOURCE: L6

  Config/env: None visible in this spec.
  External integrations: Oracle Reports (.rdf) noted as a caller in header comment [L7] — that is inbound, not an outbound integration from this package.

**GAPS:**
  Package body (PKG_REPORTING.pkb) not provided — all subprogram logic, the denormalized reporting table names/schema, and the exact fiscal-year-start usage are UNRESOLVED/NOT_ANALYZED.

All 9 package spec files have now been fully processed (PKG_AUDIT, PKG_COMMON, PKG_EMPLOYEE, PKG_INTEGRATION, PKG_LEAVE, PKG_NOTIFICATION, PKG_PAYROLL, PKG_PERFORMANCE, PKG_REPORTING).

*[pipeline status — type: plsql-spec · pass: original · attempt: 1 · coverage: 100% (numbers 0/0 · procedures 8/8 · units 8/8 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 9
Files delivered: 9
  Full coverage on first pass: 9
  Required correction: 0
  Still incomplete after max attempts: 0
Raw source: 29913 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===