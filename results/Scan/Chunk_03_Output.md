=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks ===

**Package:** HRMS.PKG_SECURITY
**Schema:** HRMS
**Type:** Package Specification

**Purpose:** Authentication & Authorization — login, session management, role-based access, encryption.

**Dependencies:**
- PKG_COMMON (referenced in comments)
- PKG_AUDIT (referenced in comments)

**Called by:** HRMS_LOGIN form, all forms (session validation)

---

**Known Issues (documented in comments):**
- Password stored as MD5 hash (should be bcrypt/scrypt)
- Session timeout check uses DB server time, not app server time
- No account lockout after failed attempts
- DBMS_CRYPTO key hard-coded in package body

---

**Custom Exceptions:**

| Exception Name         | Error Code | PRAGMA EXCEPTION_INIT |
|------------------------|------------|-----------------------|
| e_invalid_credentials  | -20301     | Yes                   |
| e_account_locked       | -20302     | Yes                   |
| e_session_expired      | -20303     | Yes                   |
| e_insufficient_priv    | -20304     | Yes                   |

---

**Function/Procedure Signatures:**

1. `FUNCTION authenticate(p_username IN VARCHAR2, p_password IN VARCHAR2, p_ip_address IN VARCHAR2 DEFAULT NULL) RETURN NUMBER`
   - Returns: NUMBER (session ID or similar numeric token)
   - p_ip_address is optional (DEFAULT NULL)

2. `PROCEDURE logout(p_session_id IN NUMBER)`
   - Ends a session by session ID

3. `FUNCTION is_session_valid(p_session_id IN NUMBER) RETURN BOOLEAN`
   - Returns: BOOLEAN indicating session validity

4. `FUNCTION has_permission(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN`
   - Returns: BOOLEAN
   - p_action defaults to 'VIEW'

5. `FUNCTION encrypt_ssn(p_ssn IN VARCHAR2) RETURN VARCHAR2`
   - Returns: encrypted SSN as VARCHAR2

6. `FUNCTION decrypt_ssn(p_encrypted IN VARCHAR2) RETURN VARCHAR2`
   - Returns: plaintext SSN as VARCHAR2

7. `FUNCTION hash_password(p_password IN VARCHAR2) RETURN VARCHAR2`
   - Returns: hashed password as VARCHAR2 (MD5 per known issues)

8. `PROCEDURE change_password(p_emp_id IN NUMBER, p_old_password IN VARCHAR2, p_new_password IN VARCHAR2)`
   - Changes password; validates old password before setting new

---

**External Services / Built-in Packages Referenced (in body, noted in spec):**
- DBMS_CRYPTO (key hard-coded in body per known issues)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb ===

**Package:** HRMS.PKG_VALIDATION
**Schema:** HRMS
**Type:** Package Body

---

**Function: validate_date_range**
```
FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN
```
- **Logic:** Returns FALSE if either p_start_date or p_end_date IS NULL. Returns TRUE if p_end_date >= p_start_date; otherwise FALSE (implied by the >= check returning a boolean).
- **Business Rule:** End date must be >= start date. Both dates are required (NULL → FALSE).

---

**Function: validate_salary_for_grade**
```
FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2
```
- **Returns:** NULL if valid; error message string if invalid.
- **Logic:**
  - If p_salary IS NULL OR p_grade_id IS NULL → returns `'Salary and grade are required'`
  - Queries table JOB_GRADES WHERE GRADE_ID = p_grade_id; selects MIN_SALARY, MAX_SALARY, GRADE_NAME into local variables v_min, v_max, v_grade_name.
  - If p_salary < v_min → returns `'Salary ' || TO_CHAR(p_salary, 'FM$999,999,990.00') || ' is below minimum for grade ' || v_grade_name || ' (' || TO_CHAR(v_min, 'FM$999,999,990.00') || ')'`
  - If p_salary > v_max → returns `'Salary ' || TO_CHAR(p_salary, 'FM$999,999,990.00') || ' exceeds maximum for grade ' || v_grade_name || ' (' || TO_CHAR(v_max, 'FM$999,999,990.00') || ')'`
  - If within range → returns NULL (valid)
  - EXCEPTION WHEN NO_DATA_FOUND → returns `'Invalid grade ID: ' || p_grade_id`
- **Tables Referenced:** JOB_GRADES (columns: GRADE_ID, MIN_SALARY, MAX_SALARY, GRADE_NAME)
- **Number Format Mask:** `'FM$999,999,990.00'` (used for both salary and grade bounds in messages)

---

**Function: validate_email_format**
```
FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN
```
- **Logic:** Delegates entirely to `PKG_COMMON.is_valid_email(p_email)`; returns its result.
- **Dependency:** PKG_COMMON.is_valid_email

---

**Function: validate_phone_format**
```
FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN
```
- **Logic:** Delegates entirely to `PKG_COMMON.is_valid_phone(p_phone)`; returns its result.
- **Dependency:** PKG_COMMON.is_valid_phone

---

**Function: validate_emp_number_format**
```
FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN
```
- **Logic:** Returns `REGEXP_LIKE(p_emp_number, '^EMP-\d{6}$')`
- **Business Rule / Format Constraint:** Employee number must match the pattern `EMP-` followed by exactly 6 digits. Example valid: `EMP-001234`.

---

**Function: is_future_date**
```
FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN
```
- **Logic:** Returns `TRUNC(p_date) > TRUNC(SYSDATE)`
- **Business Rule:** A date is considered "future" only if its truncated (date-only) value is strictly greater than today's truncated date. Same-day is NOT considered future.

---

**Function: is_business_day**
```
FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN
```
- **Logic:**
  1. v_day := TO_CHAR(p_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN')
  2. If v_day IN ('SAT', 'SUN') → RETURN FALSE
  3. SELECT COUNT(*) INTO v_holiday_count FROM HOLIDAYS WHERE HOLIDAY_DATE = TRUNC(p_date) AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)
  4. RETURN v_holiday_count = 0 (TRUE if no holiday found, FALSE if holiday exists)
- **Business Rules:**
  - Saturday and Sunday are never business days.
  - Any date matching an active holiday record (global or matching location) is not a business day.
  - p_location_code = NULL matches global holidays only; a supplied code matches global AND location-specific holidays.
- **Tables Referenced:** HOLIDAYS (columns: HOLIDAY_DATE, ACTIVE_FLAG, LOCATION_CODE)

---

**Function: validate_required_fields**
```
FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2
```
- **Returns:** NULL if all required fields are populated; error message string if not; `'Record not found'` if the record does not exist.
- **Logic (only for p_table_name = 'EMPLOYEES'):**
  - SELECTs * INTO v_rec (EMPLOYEES%ROWTYPE) FROM EMPLOYEES WHERE EMP_ID = p_record_id
  - Checks in order:
    - IF v_rec.FIRST_NAME IS NULL → RETURN `'First Name is required'`
    - IF v_rec.LAST_NAME IS NULL → RETURN `'Last Name is required'`
    - IF v_rec.HIRE_DATE IS NULL → RETURN `'Hire Date is required'`
    - IF v_rec.DEPT_ID IS NULL → RETURN `'Department is required'`
    - IF v_rec.JOB_ID IS NULL → RETURN `'Job Title is required'`
  - EXCEPTION WHEN NO_DATA_FOUND → RETURN `'Record not found'`
- **Note:** Comment states this is simplified; in production would use data dictionary to check NOT NULL columns. Only 'EMPLOYEES' table is handled; other table names fall through to RETURN NULL.
- **Tables Referenced:** EMPLOYEES (columns: FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID)
- **Required Fields for EMPLOYEES:** FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pks ===

**Package:** HRMS.PKG_VALIDATION
**Schema:** HRMS
**Type:** Package Specification

**Purpose:** Centralized validation shared between Forms triggers and PL/SQL packages.

**Dependencies:** PKG_COMMON
**Called by:** All forms (WHEN-VALIDATE-ITEM triggers), PKG_EMPLOYEE, PKG_PAYROLL

---

**Public Function/Procedure Signatures:**

1. `FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN`

2. `FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2`
   - Comment: Returns NULL if valid, error message if invalid

3. `FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN`

4. `FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN`

5. `FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN`

6. `FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN`

7. `FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN`

8. `FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2`
   - Comment: Returns NULL if all required fields populated

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql ===

**Schema:** HRMS
**Type:** Database Triggers (3 triggers)

---

**Trigger 1: TRG_SALARY_AUDIT**

- **Table:** HRMS.SALARY_RECORDS
- **Timing/Event:** AFTER INSERT OR UPDATE OR DELETE
- **For Each Row:** Yes
- **Purpose:** Tracks all salary record changes for compliance.

**Logic:**
- Declares: v_action VARCHAR2(10), v_old_json CLOB, v_new_json CLOB
- IF INSERTING:
  - v_action := 'INSERT'
  - v_new_json := `'{"emp_id":' || :NEW.EMP_ID || ',"salary":' || :NEW.BASE_SALARY || ',"effective":"' || TO_CHAR(:NEW.EFFECTIVE_DATE, 'YYYY-MM-DD') || '"}'`
- ELSIF UPDATING:
  - v_action := 'UPDATE'
  - v_old_json := `'{"salary":' || :OLD.BASE_SALARY || ',"active":"' || :OLD.ACTIVE_FLAG || '"}'`
  - v_new_json := `'{"salary":' || :NEW.BASE_SALARY || ',"active":"' || :NEW.ACTIVE_FLAG || '"}'`
- ELSIF DELETING:
  - v_action := 'DELETE'
  - v_old_json := `'{"emp_id":' || :OLD.EMP_ID || ',"salary":' || :OLD.BASE_SALARY || '}'`
- Calls: `PKG_AUDIT.log_action('SALARY_RECORDS', NVL(:NEW.SALARY_ID, :OLD.SALARY_ID), v_action, NVL(:NEW.MODIFIED_BY, USER), v_old_json, v_new_json)`
- **Columns Referenced (SALARY_RECORDS):** EMP_ID, BASE_SALARY, EFFECTIVE_DATE, ACTIVE_FLAG, SALARY_ID, MODIFIED_BY
- **Date Format Used:** 'YYYY-MM-DD'
- **Dependencies:** PKG_AUDIT.log_action

---

**Trigger 2: TRG_LEAVE_REQUEST_AUDIT**

- **Table:** HRMS.LEAVE_REQUESTS
- **Timing/Event:** AFTER UPDATE OF STATUS
- **For Each Row:** Yes
- **Purpose:** Tracks leave request status changes only.

**Logic:**
- Calls: `PKG_AUDIT.log_action('LEAVE_REQUESTS', :NEW.REQUEST_ID, 'STATUS_CHANGE', NVL(:NEW.MODIFIED_BY, USER), '{"status":"' || :OLD.STATUS || '"}', '{"status":"' || :NEW.STATUS || '"}')`
- **Columns Referenced (LEAVE_REQUESTS):** REQUEST_ID, MODIFIED_BY, STATUS
- **Action Type Logged:** 'STATUS_CHANGE' (hardcoded)
- **Dependencies:** PKG_AUDIT.log_action

---

**Trigger 3: TRG_DEPARTMENT_AUDIT**

- **Table:** HRMS.DEPARTMENTS
- **Timing/Event:** AFTER INSERT OR UPDATE OR DELETE
- **For Each Row:** Yes
- **Purpose:** Tracks department structure changes.

**Logic:**
- Declares: v_action VARCHAR2(10)
- IF INSERTING: v_action := 'INSERT'
- ELSIF UPDATING: v_action := 'UPDATE'
- ELSIF DELETING: v_action := 'DELETE'
- Calls: `PKG_AUDIT.log_action('DEPARTMENTS', NVL(:NEW.DEPT_ID, :OLD.DEPT_ID), v_action, USER)`
- Note: No old/new JSON passed (4-argument form of PKG_AUDIT.log_action).
- **Columns Referenced (DEPARTMENTS):** DEPT_ID
- **Dependencies:** PKG_AUDIT.log_action

---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_employees.sql ===

**Schema:** HRMS
**Type:** Database Triggers (3 triggers on HRMS.EMPLOYEES)

**Note (documented in file):** Business logic is duplicated between these triggers and PKG_EMPLOYEE and Forms triggers — described as a common anti-pattern in legacy Oracle Forms applications.

---

**Trigger 1: TRG_EMP_BEFORE_INSERT**

- **Table:** HRMS.EMPLOYEES
- **Timing/Event:** BEFORE INSERT
- **For Each Row:** Yes
- **Purpose:** Sets audit columns and validates required fields before insert.

**Logic:**
1. IF :NEW.CREATED_BY IS NULL → :NEW.CREATED_BY := USER
2. IF :NEW.CREATED_DATE IS NULL → :NEW.CREATED_DATE := SYSDATE
3. IF :NEW.ACTIVE_FLAG IS NULL → :NEW.ACTIVE_FLAG := 'Y'
4. IF :NEW.EMPLOYMENT_STATUS IS NULL → :NEW.EMPLOYMENT_STATUS := 'ACTIVE'
5. Hire date future limit check:
   - IF :NEW.HIRE_DATE > SYSDATE + **180** → RAISE_APPLICATION_ERROR(-20501, `'Hire date cannot be more than 180 days in the future'`)
   - **Business Rule:** Hire date cannot be more than 180 days in the future.
6. Email uniqueness check (inline DECLARE block):
   - SELECT COUNT(*) INTO v_count FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(:NEW.EMAIL) AND ACTIVE_FLAG = 'Y'
   - IF v_count > 0 → RAISE_APPLICATION_ERROR(-20502, `'Email address already in use: ' || :NEW.EMAIL`)
   - **Business Rule:** Email must be unique among active employees (case-insensitive comparison).
   - Note: Also enforced by unique constraint, but trigger provides a better error message.

**Columns Set/Validated:** CREATED_BY, CREATED_DATE, ACTIVE_FLAG, EMPLOYMENT_STATUS, HIRE_DATE, EMAIL

**Error Codes:**
- -20501: Hire date more than 180 days in the future
- -20502: Email address already in use

---

**Trigger 2: TRG_EMP_BEFORE_UPDATE**

- **Table:** HRMS.EMPLOYEES
- **Timing/Event:** BEFORE UPDATE
- **For Each Row:** Yes
- **Purpose:** Sets modification audit columns and validates state transitions; logs history.

**Logic:**
1. :NEW.MODIFIED_BY := NVL(:NEW.MODIFIED_BY, USER)
2. :NEW.MODIFIED_DATE := SYSDATE
3. **Reactivation prevention:**
   - IF :OLD.EMPLOYMENT_STATUS = 'TERMINATED' AND :NEW.EMPLOYMENT_STATUS = 'ACTIVE' → RAISE_APPLICATION_ERROR(-20503, `'Cannot directly reactivate a terminated employee. Use the rehire process.'`)
   - **Business Rule:** Terminated employees cannot be directly reactivated via UPDATE; must use PKG_EMPLOYEE.rehire_employee.
4. **Status change history logging:**
   - IF :OLD.EMPLOYMENT_STATUS != :NEW.EMPLOYMENT_STATUS → INSERT INTO EMPLOYEE_HISTORY:
     - HISTORY_ID = SEQ_EMP_HISTORY.NEXTVAL
     - EMP_ID = :NEW.EMP_ID
     - CHANGE_TYPE = 'STATUS_CHANGE'
     - CHANGE_DATE = SYSDATE
     - OLD_VALUE = :OLD.EMPLOYMENT_STATUS
     - NEW_VALUE = :NEW.EMPLOYMENT_STATUS
     - CHANGED_BY = NVL(:NEW.MODIFIED_BY, USER)
     - CHANGE_REASON = `'Triggered by status update'`
5. **Department transfer history logging:**
   - IF NVL(:OLD.DEPT_ID, -1) != NVL(:NEW.DEPT_ID, -1) → INSERT INTO EMPLOYEE_HISTORY:
     - HISTORY_ID = SEQ_EMP_HISTORY.NEXTVAL
     - EMP_ID = :NEW.EMP_ID
     - CHANGE_TYPE = 'DEPARTMENT_CHANGE'
     - CHANGE_DATE = SYSDATE
     - OLD_VALUE = TO_CHAR(:OLD.DEPT_ID)
     - NEW_VALUE = TO_CHAR(:NEW.DEPT_ID)
     - CHANGED_BY = NVL(:NEW.MODIFIED_BY, USER)
     - CHANGE_REASON = `'Department transfer'`
6. **Job change history logging:**
   - IF NVL(:OLD.JOB_ID, -1) != NVL(:NEW.JOB_ID, -1) → INSERT INTO EMPLOYEE_HISTORY:
     - HISTORY_ID = SEQ_EMP_HISTORY.NEXTVAL
     - EMP_ID = :NEW.EMP_ID
     - CHANGE_TYPE = 'JOB_CHANGE'
     - CHANGE_DATE = SYSDATE
     - OLD_VALUE = TO_CHAR(:OLD.JOB_ID)
     - NEW_VALUE = TO_CHAR(:NEW.JOB_ID)
     - CHANGED_BY = NVL(:NEW.MODIFIED_BY, USER)
     - CHANGE_REASON = `'Job title change'`

**Null sentinel for change detection:** -1 (used for DEPT_ID and JOB_ID NULL comparison via NVL)

**Sequences Used:** SEQ_EMP_HISTORY.NEXTVAL

**Tables Written:** EMPLOYEE_HISTORY (columns: HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)

**Error Codes:**
- -20503: Direct reactivation of terminated employee attempted

---

**Trigger 3: TRG_EMP_INSTEAD_OF_DELETE (named "TRG_EMP_BEFORE_DELETE" in comment but BEFORE DELETE in DDL)**

- **Table:** HRMS.EMPLOYEES
- **Timing/Event:** BEFORE DELETE (named TRG_EMP_INSTEAD_OF_DELETE)
- **For Each Row:** Yes
- **Purpose:** Prevents direct deletion; enforces soft-delete pattern.

**Logic:**
- Unconditionally raises: RAISE_APPLICATION_ERROR(-20504, `'Direct deletion not allowed. Use termination process or set ACTIVE_FLAG to N.'`)

**Known Bug (documented):** Trigger prevents deletion entirely. Forms expects DELETE to succeed. Workaround in Forms: set ACTIVE_FLAG = 'N' then CLEAR_RECORD instead of DELETE_RECORD.

**Error Codes:**
- -20504: Direct deletion not allowed

---

=== FILE: ts-plsql-oracle-forms-hrms-main/README.md ===

**Application:** HRMS — HR Management System
**Technology:** Oracle Forms 12c, Oracle Database 19c, Oracle WebLogic 12c

**History:**
- Originally built: Oracle Forms 6i, circa 2002
- Upgraded to: Forms 11g, 2012
- Current: Forms 12c with Oracle Database 19c

**Scale:** ~200 concurrent users, 3 regional offices

---

**Architecture Layers:**
- Oracle Forms 12c Application Server
- Oracle WebLogic 12c Server
- Forms Modules (.fmb/.fmx): 18 forms
- PL/SQL Packages & Procedures: 12 packages
- Oracle Reports (.rdf/.rep): 8 reports
- Oracle Database 19c (HRMS schema): 42 tables, 15 views, 200+ triggers

---

**Forms (18 total):**
- HRMS_EMPLOYEE.xml — Employee maintenance
- HRMS_DEPARTMENT.xml — Department management
- HRMS_PAYROLL.xml — Payroll processing
- HRMS_LEAVE.xml — Leave request and approval
- HRMS_PERFORMANCE.xml — Performance review
- HRMS_LOGIN.xml — Login and authentication
- HRMS_MENU.xml — Main menu navigation
- HRMS_REPORTS.xml — Report parameter and launcher
- HRMS_LOV.xml — Shared List of Values library
- HRMS_TOOLBAR.xml — Shared toolbar object library

**PL/SQL Packages (12 total):**
- PKG_EMPLOYEE (.pks/.pkb)
- PKG_DEPARTMENT (.pks/.pkb)
- PKG_PAYROLL (.pks/.pkb)
- PKG_LEAVE (.pks/.pkb)
- PKG_PERFORMANCE (.pks/.pkb)
- PKG_SECURITY (.pks/.pkb)
- PKG_AUDIT (.pks/.pkb)
- PKG_NOTIFICATION (.pks/.pkb)
- PKG_REPORTING (.pks/.pkb)
- PKG_COMMON (.pks/.pkb)
- PKG_VALIDATION (.pks/.pkb)
- PKG_INTEGRATION (.pks/.pkb)

---

**Modules (functional areas):**
1. Employee Records — hire, transfer, terminate, personal details, job history
2. Department & Organization — department hierarchy, cost centers, reporting lines
3. Payroll Processing — salary calculations, deductions, tax withholding, pay runs
4. Leave Management — leave requests, approvals, balance tracking, accrual rules
5. Performance Reviews — annual review cycles, ratings, goal tracking
6. Reporting — headcount, compensation analysis, turnover, compliance

---

**Key Oracle Forms Trigger Types Used:**
- WHEN-NEW-FORM-INSTANCE
- WHEN-VALIDATE-ITEM
- WHEN-BUTTON-PRESSED
- POST-QUERY
- PRE-INSERT
- PRE-UPDATE

**PL/SQL Built-in Packages Used:** DBMS_OUTPUT, UTL_FILE, UTL_MAIL

**Custom Error Code Range:** -20000 to -20999

**Database Patterns:**
- Surrogate keys via sequences + BEFORE INSERT triggers
- Soft deletes (ACTIVE_FLAG CHAR(1) DEFAULT 'Y')
- Audit columns on every table: CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE
- History tables (_HIST suffix) for change tracking
- Denormalized reporting tables refreshed nightly by batch jobs

**Known Technical Debt:**
- No unit tests (all testing is manual via Forms)
- Business logic split between Forms triggers and database packages
- Several packages exceed 3,000 lines
- Hard-coded configuration values in package bodies
- VARCHAR2(4000) used as catch-all for text fields
- Mixed naming conventions (CAMELCASE and UNDERSCORE_CASE)
- Dead code from decommissioned modules
- Circular package dependency between PKG_EMPLOYEE and PKG_PAYROLL

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/sequences/hrms_sequences.sql ===

**Schema:** HRMS
**Type:** Sequence Definitions

**Note:** Uses simple incrementing sequences (no UUID/GUID), typical for Oracle Forms applications of this era. NOCACHE on most sequences means gaps can occur.

**Known Bug:** SEQ_EMP_NUMBER is NOCACHE, but PKG_EMPLOYEE.generate_emp_number uses MAX()+1 instead of the sequence, creating a race condition.

| Sequence Name          | Start With | Increment By | Cache  | Purpose                                              |
|------------------------|------------|--------------|--------|------------------------------------------------------|
| SEQ_DEPARTMENT         | 100        | 1            | NOCACHE| Surrogate key for DEPARTMENTS                        |
| SEQ_LOCATION           | 100        | 1            | NOCACHE| Surrogate key for LOCATIONS                          |
| SEQ_JOB_GRADE          | 100        | 1            | NOCACHE| Surrogate key for JOB_GRADES                         |
| SEQ_JOB_TITLE          | 100        | 1            | NOCACHE| Surrogate key for JOB_TITLES                         |
| SEQ_EMPLOYEE           | 10000      | 1            | NOCACHE| Surrogate key for EMPLOYEES                          |
| SEQ_EMP_HISTORY        | 1          | 1            | NOCACHE| Surrogate key for EMPLOYEE_HISTORY                   |
| SEQ_DEPENDENT          | 1          | 1            | NOCACHE| Surrogate key for EMPLOYEE_DEPENDENTS                |
| SEQ_EMERGENCY_CONTACT  | 1          | 1            | NOCACHE| Surrogate key for EMERGENCY_CONTACTS                 |
| SEQ_EMP_NUMBER         | 1000       | 1            | NOCACHE| Generates EMP-XXXXXX format (not used correctly — see bug) |
| SEQ_SALARY             | 1          | 1            | NOCACHE| Surrogate key for SALARY_RECORDS                     |
| SEQ_PAY_ELEMENT        | 1          | 1            | NOCACHE| Surrogate key for PAY_ELEMENTS                       |
| SEQ_EMP_PAY_ELEMENT    | 1          | 1            | NOCACHE| Surrogate key for EMPLOYEE_PAY_ELEMENTS              |
| SEQ_PAY_PERIOD         | 1          | 1            | NOCACHE| Surrogate key for PAY_PERIODS                        |
| SEQ_PAYROLL_RUN        | 1          | 1            | NOCACHE| Surrogate key for PAYROLL_RUNS                       |
| SEQ_PAYROLL_DETAIL     | 1          | 1            | NOCACHE| Surrogate key for PAYROLL_DETAILS                    |
| SEQ_TAX_BRACKET        | 1          | 1            | NOCACHE| Surrogate key for TAX_BRACKETS                       |
| SEQ_LEAVE_TYPE         | 1          | 1            | NOCACHE| Surrogate key for LEAVE_TYPES                        |
| SEQ_LEAVE_BALANCE      | 1          | 1            | NOCACHE| Surrogate key for LEAVE_BALANCES                     |
| SEQ_LEAVE_REQUEST      | 1          | 1            | NOCACHE| Surrogate key for LEAVE_REQUESTS                     |
| SEQ_LEAVE_ACCRUAL      | 1          | 1            | NOCACHE| Surrogate key for LEAVE_ACCRUAL_LOG                  |
| SEQ_HOLIDAY            | 1          | 1            | NOCACHE| Surrogate key for HOLIDAYS                           |
| SEQ_REVIEW_CYCLE       | 1          | 1            | NOCACHE| Surrogate key for REVIEW_CYCLES                      |
| SEQ_PERF_REVIEW        | 1          | 1            | NOCACHE| Surrogate key for PERFORMANCE_REVIEWS                |
| SEQ_PERF_GOAL          | 1          | 1            | NOCACHE| Surrogate key for PERFORMANCE_GOALS                  |
| SEQ_AUDIT              | 1          | 1            | CACHE 100 | Surrogate key for AUDIT_LOG (only sequence with cache) |
| SEQ_NOTIFICATION       | 1          | 1            | NOCACHE| Surrogate key for NOTIFICATION_QUEUE                 |
| SEQ_USER_SESSION       | 1          | 1            | NOCACHE| Surrogate key for USER_SESSIONS                      |
| SEQ_SYSTEM_PARAM       | 1          | 1            | NOCACHE| Surrogate key for SYSTEM_PARAMETERS                  |
| SEQ_LOOKUP             | 1          | 1            | NOCACHE| Surrogate key for LOOKUP_VALUES                      |

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/01_core_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.DEPARTMENTS**

| Column           | Data Type       | Nullable | Default  | Notes                                    |
|------------------|-----------------|----------|----------|------------------------------------------|
| DEPT_ID          | NUMBER(10)      | NOT NULL |          | PK                                       |
| DEPT_CODE        | VARCHAR2(20)    | NOT NULL |          | UK                                       |
| DEPT_NAME        | VARCHAR2(100)   | NOT NULL |          |                                          |
| PARENT_DEPT_ID   | NUMBER(10)      | NULL     |          | Self-referencing FK for hierarchy        |
| COST_CENTER      | VARCHAR2(20)    | NULL     |          | Financial cost center code for GL        |
| MANAGER_EMP_ID   | NUMBER(10)      | NULL     |          |                                          |
| LOCATION_CODE    | VARCHAR2(10)    | NULL     |          |                                          |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL | 'Y'      | CHECK IN ('Y','N')                       |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL |          |                                          |
| CREATED_DATE     | DATE            | NOT NULL | SYSDATE  |                                          |
| MODIFIED_BY      | VARCHAR2(30)    | NULL     |          |                                          |
| MODIFIED_DATE    | DATE            | NULL     |          |                                          |

**Constraints:**
- PK_DEPARTMENTS: PRIMARY KEY (DEPT_ID)
- UK_DEPT_CODE: UNIQUE (DEPT_CODE)
- CHK_DEPT_ACTIVE: CHECK (ACTIVE_FLAG IN ('Y', 'N'))

**Comments:** Table: 'Organization departments and cost centers'; PARENT_DEPT_ID: 'Self-referencing FK for department hierarchy'; COST_CENTER: 'Financial cost center code for GL integration'

---

**Table: HRMS.LOCATIONS**

| Column          | Data Type       | Nullable | Default              | Notes     |
|-----------------|-----------------|----------|----------------------|-----------|
| LOCATION_CODE   | VARCHAR2(10)    | NOT NULL |                      | PK        |
| LOCATION_NAME   | VARCHAR2(100)   | NOT NULL |                      |           |
| ADDRESS_LINE1   | VARCHAR2(200)   | NULL     |                      |           |
| ADDRESS_LINE2   | VARCHAR2(200)   | NULL     |                      |           |
| CITY            | VARCHAR2(100)   | NULL     |                      |           |
| STATE_PROVINCE  | VARCHAR2(100)   | NULL     |                      |           |
| POSTAL_CODE     | VARCHAR2(20)    | NULL     |                      |           |
| COUNTRY_CODE    | VARCHAR2(3)     | NULL     |                      |           |
| PHONE_NUMBER    | VARCHAR2(30)    | NULL     |                      |           |
| TIMEZONE        | VARCHAR2(50)    | NULL     | 'America/New_York'   | Default timezone |
| ACTIVE_FLAG     | CHAR(1)         | NOT NULL | 'Y'                  |           |
| CREATED_BY      | VARCHAR2(30)    | NOT NULL |                      |           |
| CREATED_DATE    | DATE            | NOT NULL | SYSDATE              |           |
| MODIFIED_BY     | VARCHAR2(30)    | NULL     |                      |           |
| MODIFIED_DATE   | DATE            | NULL     |                      |           |

**Constraints:**
- PK_LOCATIONS: PRIMARY KEY (LOCATION_CODE)

---

**Table: HRMS.JOB_GRADES**

| Column            | Data Type     | Nullable | Default | Notes                            |
|-------------------|---------------|----------|---------|----------------------------------|
| GRADE_ID          | NUMBER(5)     | NOT NULL |         | PK                               |
| GRADE_CODE        | VARCHAR2(10)  | NOT NULL |         | UK                               |
| GRADE_NAME        | VARCHAR2(50)  | NOT NULL |         |                                  |
| MIN_SALARY        | NUMBER(12,2)  | NOT NULL |         |                                  |
| MAX_SALARY        | NUMBER(12,2)  | NOT NULL |         |                                  |
| OVERTIME_ELIGIBLE | CHAR(1)       | NULL     | 'N'     |                                  |
| ACTIVE_FLAG       | CHAR(1)       | NOT NULL | 'Y'     |                                  |
| CREATED_BY        | VARCHAR2(30)  | NOT NULL |         |                                  |
| CREATED_DATE      | DATE          | NOT NULL | SYSDATE |                                  |
| MODIFIED_BY       | VARCHAR2(30)  | NULL     |         |                                  |
| MODIFIED_DATE     | DATE          | NULL     |         |                                  |

**Constraints:**
- PK_JOB_GRADES: PRIMARY KEY (GRADE_ID)
- UK_GRADE_CODE: UNIQUE (GRADE_CODE)
- CHK_SALARY_RANGE: CHECK (MAX_SALARY >= MIN_SALARY)

---

**Table: HRMS.JOB_TITLES**

| Column       | Data Type     | Nullable | Default   | Notes                    |
|--------------|---------------|----------|-----------|--------------------------|
| JOB_ID       | NUMBER(10)    | NOT NULL |           | PK                       |
| JOB_CODE     | VARCHAR2(20)  | NOT NULL |           | UK                       |
| JOB_TITLE    | VARCHAR2(100) | NOT NULL |           |                          |
| JOB_FAMILY   | VARCHAR2(50)  | NULL     |           |                          |
| GRADE_ID     | NUMBER(5)     | NOT NULL |           | FK → JOB_GRADES(GRADE_ID)|
| EEO_CATEGORY | VARCHAR2(10)  | NULL     |           |                          |
| FLSA_STATUS  | VARCHAR2(10)  | NULL     | 'EXEMPT'  |                          |
| ACTIVE_FLAG  | CHAR(1)       | NOT NULL | 'Y'       |                          |
| CREATED_BY   | VARCHAR2(30)  | NOT NULL |           |                          |
| CREATED_DATE | DATE          | NOT NULL | SYSDATE   |                          |
| MODIFIED_BY  | VARCHAR2(30)  | NULL     |           |                          |
| MODIFIED_DATE| DATE          | NULL     |           |                          |

**Constraints:**
- PK_JOB_TITLES: PRIMARY KEY (JOB_ID)
- UK_JOB_CODE: UNIQUE (JOB_CODE)
- FK_JOB_GRADE: FOREIGN KEY (GRADE_ID) REFERENCES HRMS.JOB_GRADES(GRADE_ID)

---

**Table: HRMS.EMPLOYEES**

| Column             | Data Type      | Nullable | Default      | Notes                                                |
|--------------------|----------------|----------|--------------|------------------------------------------------------|
| EMP_ID             | NUMBER(10)     | NOT NULL |              | PK                                                   |
| EMP_NUMBER         | VARCHAR2(20)   | NOT NULL |              | UK                                                   |
| FIRST_NAME         | VARCHAR2(50)   | NOT NULL |              |                                                      |
| MIDDLE_NAME        | VARCHAR2(50)   | NULL     |              |                                                      |
| LAST_NAME          | VARCHAR2(50)   | NOT NULL |              |                                                      |
| DATE_OF_BIRTH      | DATE           | NULL     |              |                                                      |
| GENDER             | CHAR(1)        | NULL     |              | CHECK IN ('M','F','O')                               |
| MARITAL_STATUS     | VARCHAR2(10)   | NULL     |              |                                                      |
| NATIONALITY        | VARCHAR2(50)   | NULL     |              |                                                      |
| SSN_ENCRYPTED      | VARCHAR2(200)  | NULL     |              | AES-256 encrypted; decrypted only in PKG_SECURITY    |
| EMAIL              | VARCHAR2(100)  | NULL     |              |                                                      |
| PHONE_WORK         | VARCHAR2(30)   | NULL     |              |                                                      |
| PHONE_MOBILE       | VARCHAR2(30)   | NULL     |              |                                                      |
| ADDRESS_LINE1      | VARCHAR2(200)  | NULL     |              |                                                      |
| ADDRESS_LINE2      | VARCHAR2(200)  | NULL     |              |                                                      |
| CITY               | VARCHAR2(100)  | NULL     |              |                                                      |
| STATE_PROVINCE     | VARCHAR2(100)  | NULL     |              |                                                      |
| POSTAL_CODE        | VARCHAR2(20)   | NULL     |              |                                                      |
| COUNTRY_CODE       | VARCHAR2(3)    | NULL     |              |                                                      |
| HIRE_DATE          | DATE           | NOT NULL |              |                                                      |
| TERMINATION_DATE   | DATE           | NULL     |              |                                                      |
| TERMINATION_REASON | VARCHAR2(50)   | NULL     |              |                                                      |
| DEPT_ID            | NUMBER(10)     | NOT NULL |              | FK → DEPARTMENTS(DEPT_ID)                            |
| JOB_ID             | NUMBER(10)     | NOT NULL |              | FK → JOB_TITLES(JOB_ID)                              |
| MANAGER_EMP_ID     | NUMBER(10)     | NULL     |              | Self-referencing FK → EMPLOYEES(EMP_ID)              |
| LOCATION_CODE      | VARCHAR2(10)   | NULL     |              | FK → LOCATIONS(LOCATION_CODE)                        |
| EMPLOYMENT_TYPE    | VARCHAR2(20)   | NULL     | 'FULL_TIME'  | CHECK IN ('FULL_TIME','PART_TIME','CONTRACT','INTERN')|
| EMPLOYMENT_STATUS  | VARCHAR2(20)   | NULL     | 'ACTIVE'     | CHECK IN ('ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED')|
| PHOTO_BLOB         | BLOB           | NULL     |              |                                                      |
| NOTES              | CLOB           | NULL     |              |                                                      |
| ACTIVE_FLAG        | CHAR(1)        | NOT NULL | 'Y'          |                                                      |
| CREATED_BY         | VARCHAR2(30)   | NOT NULL |              |                                                      |
| CREATED_DATE       | DATE           | NOT NULL | SYSDATE      |                                                      |
| MODIFIED_BY        | VARCHAR2(30)   | NULL     |              |                                                      |
| MODIFIED_DATE      | DATE           | NULL     |              |                                                      |

**Constraints:**
- PK_EMPLOYEES: PRIMARY KEY (EMP_ID)
- UK_EMP_NUMBER: UNIQUE (EMP_NUMBER)
- FK_EMP_DEPT: FOREIGN KEY (DEPT_ID) REFERENCES HRMS.DEPARTMENTS(DEPT_ID)
- FK_EMP_JOB: FOREIGN KEY (JOB_ID) REFERENCES HRMS.JOB_TITLES(JOB_ID)
- FK_EMP_MANAGER: FOREIGN KEY (MANAGER_EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- FK_EMP_LOCATION: FOREIGN KEY (LOCATION_CODE) REFERENCES HRMS.LOCATIONS(LOCATION_CODE)
- CHK_EMP_STATUS: CHECK (EMPLOYMENT_STATUS IN ('ACTIVE', 'ON_LEAVE', 'SUSPENDED', 'TERMINATED'))
- CHK_EMP_TYPE: CHECK (EMPLOYMENT_TYPE IN ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERN'))
- CHK_EMP_GENDER: CHECK (GENDER IN ('M', 'F', 'O'))

**Comments:** Table: 'Master employee records - core entity of the HRMS system'; SSN_ENCRYPTED: 'AES-256 encrypted SSN - decrypted only in PKG_SECURITY'; EMPLOYMENT_STATUS: 'Current status: ACTIVE, ON_LEAVE, SUSPENDED, TERMINATED'

---

**Table: HRMS.EMPLOYEE_HISTORY**

| Column         | Data Type     | Nullable | Default  | Notes                                       |
|----------------|---------------|----------|----------|---------------------------------------------|
| HIST_ID        | NUMBER(15)    | NOT NULL |          | PK                                          |
| EMP_ID         | NUMBER(10)    | NOT NULL |          | FK → EMPLOYEES(EMP_ID)                      |
| CHANGE_TYPE    | VARCHAR2(30)  | NOT NULL |          | CHECK (see allowed values below)            |
| EFFECTIVE_DATE | DATE          | NOT NULL |          |                                             |
| OLD_DEPT_ID    | NUMBER(10)    | NULL     |          |                                             |
| NEW_DEPT_ID    | NUMBER(10)    | NULL     |          |                                             |
| OLD_JOB_ID     | NUMBER(10)    | NULL     |          |                                             |
| NEW_JOB_ID     | NUMBER(10)    | NULL     |          |                                             |
| OLD_MANAGER_ID | NUMBER(10)    | NULL     |          |                                             |
| NEW_MANAGER_ID | NUMBER(10)    | NULL     |          |                                             |
| OLD_SALARY     | NUMBER(12,2)  | NULL     |          |                                             |
| NEW_SALARY     | NUMBER(12,2)  | NULL     |          |                                             |
| OLD_LOCATION   | VARCHAR2(10)  | NULL     |          |                                             |
| NEW_LOCATION   | VARCHAR2(10)  | NULL     |          |                                             |
| REASON_CODE    | VARCHAR2(30)  | NULL     |          |                                             |
| COMMENTS       | VARCHAR2(4000)| NULL     |          |                                             |
| CREATED_BY     | VARCHAR2(30)  | NOT NULL |          |                                             |
| CREATED_DATE   | DATE          | NOT NULL | SYSDATE  |                                             |

**Constraints:**
- PK_EMP_HISTORY: PRIMARY KEY (HIST_ID)
- FK_HIST_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- CHK_CHANGE_TYPE: CHECK (CHANGE_TYPE IN ('HIRE', 'TRANSFER', 'PROMOTION', 'DEMOTION', 'SALARY_CHANGE', 'TERMINATION', 'REHIRE', 'LEAVE_START', 'LEAVE_END', 'STATUS_CHANGE'))

**Note:** The trigger TRG_EMP_BEFORE_UPDATE uses a different column set (HISTORY_ID, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON) from what is defined in this DDL (HIST_ID, EFFECTIVE_DATE, OLD_DEPT_ID, etc.) — this is a discrepancy in the codebase.

---

**Table: HRMS.EMPLOYEE_DEPENDENTS**

| Column           | Data Type     | Nullable | Default | Notes                                        |
|------------------|---------------|----------|---------|----------------------------------------------|
| DEPENDENT_ID     | NUMBER(10)    | NOT NULL |         | PK                                           |
| EMP_ID           | NUMBER(10)    | NOT NULL |         | FK → EMPLOYEES(EMP_ID)                       |
| FIRST_NAME       | VARCHAR2(50)  | NOT NULL |         |                                              |
| LAST_NAME        | VARCHAR2(50)  | NOT NULL |         |                                              |
| RELATIONSHIP     | VARCHAR2(20)  | NOT NULL |         | CHECK IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER') |
| DATE_OF_BIRTH    | DATE          | NULL     |         |                                              |
| SSN_ENCRYPTED    | VARCHAR2(200) | NULL     |         |                                              |
| BENEFITS_ENROLLED| CHAR(1)       | NULL     | 'N'     |                                              |
| ACTIVE_FLAG      | CHAR(1)       | NOT NULL | 'Y'     |                                              |
| CREATED_BY       | VARCHAR2(30)  | NOT NULL |         |                                              |
| CREATED_DATE     | DATE          | NOT NULL | SYSDATE |                                              |
| MODIFIED_BY      | VARCHAR2(30)  | NULL     |         |                                              |
| MODIFIED_DATE    | DATE          | NULL     |         |                                              |

**Constraints:**
- PK_EMP_DEPENDENTS: PRIMARY KEY (DEPENDENT_ID)
- FK_DEP_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- CHK_RELATIONSHIP: CHECK (RELATIONSHIP IN ('SPOUSE', 'CHILD', 'PARENT', 'DOMESTIC_PARTNER', 'OTHER'))

---

**Table: HRMS.EMERGENCY_CONTACTS**

| Column           | Data Type     | Nullable | Default | Notes                    |
|------------------|---------------|----------|---------|--------------------------|
| CONTACT_ID       | NUMBER(10)    | NOT NULL |         | PK                       |
| EMP_ID           | NUMBER(10)    | NOT NULL |         | FK → EMPLOYEES(EMP_ID)   |
| CONTACT_NAME     | VARCHAR2(100) | NOT NULL |         |                          |
| RELATIONSHIP     | VARCHAR2(30)  | NULL     |         |                          |
| PHONE_PRIMARY    | VARCHAR2(30)  | NOT NULL |         |                          |
| PHONE_SECONDARY  | VARCHAR2(30)  | NULL     |         |                          |
| EMAIL            | VARCHAR2(100) | NULL     |         |                          |
| PRIORITY_ORDER   | NUMBER(2)     | NULL     | 1       |                          |
| ACTIVE_FLAG      | CHAR(1)       | NOT NULL | 'Y'     |                          |
| CREATED_BY       | VARCHAR2(30)  | NOT NULL |         |                          |
| CREATED_DATE     | DATE          | NOT NULL | SYSDATE |                          |
| MODIFIED_BY      | VARCHAR2(30)  | NULL     |         |                          |
| MODIFIED_DATE    | DATE          | NULL     |         |                          |

**Constraints:**
- PK_EMERGENCY_CONTACTS: PRIMARY KEY (CONTACT_ID)
- FK_EC_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/02_payroll_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.SALARY_RECORDS**

| Column          | Data Type     | Nullable | Default    | Notes                                               |
|-----------------|---------------|----------|------------|-----------------------------------------------------|
| SALARY_ID       | NUMBER(10)    | NOT NULL |            | PK                                                  |
| EMP_ID          | NUMBER(10)    | NOT NULL |            | FK → EMPLOYEES(EMP_ID)                              |
| EFFECTIVE_DATE  | DATE          | NOT NULL |            |                                                     |
| END_DATE        | DATE          | NULL     |            |                                                     |
| BASE_SALARY     | NUMBER(12,2)  | NOT NULL |            |                                                     |
| CURRENCY_CODE   | VARCHAR2(3)   | NULL     | 'USD'      |                                                     |
| PAY_FREQUENCY   | VARCHAR2(20)  | NULL     | 'MONTHLY'  | CHECK IN ('WEEKLY','BIWEEKLY','SEMIMONTHLY','MONTHLY') |
| SALARY_BASIS    | VARCHAR2(20)  | NULL     | 'ANNUAL'   | CHECK IN ('ANNUAL','HOURLY')                        |
| CHANGE_REASON   | VARCHAR2(50)  | NULL     |            |                                                     |
| CHANGE_PCT      | NUMBER(5,2)   | NULL     |            |                                                     |
| APPROVED_BY     | NUMBER(10)    | NULL     |            |                                                     |
| APPROVAL_DATE   | DATE          | NULL     |            |                                                     |
| ACTIVE_FLAG     | CHAR(1)       | NOT NULL | 'Y'        |                                                     |
| CREATED_BY      | VARCHAR2(30)  | NOT NULL |            |                                                     |
| CREATED_DATE    | DATE          | NOT NULL | SYSDATE    |                                                     |
| MODIFIED_BY     | VARCHAR2(30)  | NULL     |            |                                                     |
| MODIFIED_DATE   | DATE          | NULL     |            |                                                     |

**Constraints:**
- PK_SALARY_RECORDS: PRIMARY KEY (SALARY_ID)
- FK_SAL_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- CHK_PAY_FREQ: CHECK (PAY_FREQUENCY IN ('WEEKLY', 'BIWEEKLY', 'SEMIMONTHLY', 'MONTHLY'))
- CHK_SAL_BASIS: CHECK (SALARY_BASIS IN ('ANNUAL', 'HOURLY'))

---

**Table: HRMS.PAY_ELEMENTS**

| Column              | Data Type     | Nullable | Default | Notes                                                    |
|---------------------|---------------|----------|---------|----------------------------------------------------------|
| ELEMENT_ID          | NUMBER(10)    | NOT NULL |         | PK                                                       |
| ELEMENT_CODE        | VARCHAR2(30)  | NOT NULL |         | UK                                                       |
| ELEMENT_NAME        | VARCHAR2(100) | NOT NULL |         |                                                          |
| ELEMENT_TYPE        | VARCHAR2(20)  | NOT NULL |         | CHECK IN ('EARNING','DEDUCTION','TAX','BENEFIT','REIMBURSEMENT') |
| CALCULATION_TYPE    | VARCHAR2(20)  | NOT NULL |         | CHECK IN ('FLAT','PERCENTAGE','HOURS','FORMULA')         |
| DEFAULT_AMOUNT      | NUMBER(12,2)  | NULL     |         |                                                          |
| DEFAULT_PERCENTAGE  | NUMBER(5,2)   | NULL     |         |                                                          |
| TAXABLE_FLAG        | CHAR(1)       | NULL     | 'Y'     |                                                          |
| PRETAX_FLAG         | CHAR(1)       | NULL     | 'N'     |                                                          |
| EMPLOYER_PAID       | CHAR(1)       | NULL     | 'N'     |                                                          |
| GL_ACCOUNT_CODE     | VARCHAR2(30)  | NULL     |         |                                                          |
| PRIORITY_ORDER      | NUMBER(5)     | NULL     | 100     |                                                          |
| ACTIVE_FLAG         | CHAR(1)       | NOT NULL | 'Y'     |                                                          |
| CREATED_BY          | VARCHAR2(30)  | NOT NULL |         |                                                          |
| CREATED_DATE        | DATE          | NOT NULL | SYSDATE |                                                          |
| MODIFIED_BY         | VARCHAR2(30)  | NULL     |         |                                                          |
| MODIFIED_DATE       | DATE          | NULL     |         |                                                          |

**Constraints:**
- PK_PAY_ELEMENTS: PRIMARY KEY (ELEMENT_ID)
- UK_PAY_ELEM_CODE: UNIQUE (ELEMENT_CODE)
- CHK_ELEM_TYPE: CHECK (ELEMENT_TYPE IN ('EARNING', 'DEDUCTION', 'TAX', 'BENEFIT', 'REIMBURSEMENT'))
- CHK_CALC_TYPE: CHECK (CALCULATION_TYPE IN ('FLAT', 'PERCENTAGE', 'HOURS', 'FORMULA'))

---

**Table: HRMS.EMPLOYEE_PAY_ELEMENTS**

| Column          | Data Type    | Nullable | Default | Notes                              |
|-----------------|--------------|----------|---------|------------------------------------|
| EMP_ELEMENT_ID  | NUMBER(10)   | NOT NULL |         | PK                                 |
| EMP_ID          | NUMBER(10)   | NOT NULL |         | FK → EMPLOYEES(EMP_ID)             |
| ELEMENT_ID      | NUMBER(10)   | NOT NULL |         | FK → PAY_ELEMENTS(ELEMENT_ID)      |
| EFFECTIVE_DATE  | DATE         | NOT NULL |         |                                    |
| END_DATE        | DATE         | NULL     |         |                                    |
| AMOUNT          | NUMBER(12,2) | NULL     |         |                                    |
| PERCENTAGE      | NUMBER(5,2)  | NULL     |         |                                    |
| OVERRIDE_AMOUNT | NUMBER(12,2) | NULL     |         |                                    |
| ACTIVE_FLAG     | CHAR(1)      | NOT NULL | 'Y'     |                                    |
| CREATED_BY      | VARCHAR2(30) | NOT NULL |         |                                    |
| CREATED_DATE    | DATE         | NOT NULL | SYSDATE |                                    |
| MODIFIED_BY     | VARCHAR2(30) | NULL     |         |                                    |
| MODIFIED_DATE   | DATE         | NULL     |         |                                    |

**Constraints:**
- PK_EMP_PAY_ELEMENTS: PRIMARY KEY (EMP_ELEMENT_ID)
- FK_EPE_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- FK_EPE_ELEMENT: FOREIGN KEY (ELEMENT_ID) REFERENCES HRMS.PAY_ELEMENTS(ELEMENT_ID)

---

**Table: HRMS.PAY_PERIODS**

| Column             | Data Type     | Nullable | Default       | Notes                                          |
|--------------------|---------------|----------|---------------|------------------------------------------------|
| PERIOD_ID          | NUMBER(10)    | NOT NULL |               | PK                                             |
| PERIOD_NAME        | VARCHAR2(50)  | NOT NULL |               |                                                |
| PAY_FREQUENCY      | VARCHAR2(20)  | NOT NULL |               |                                                |
| PERIOD_START_DATE  | DATE          | NOT NULL |               |                                                |
| PERIOD_END_DATE    | DATE          | NOT NULL |               |                                                |
| PAY_DATE           | DATE          | NOT NULL |               |                                                |
| STATUS             | VARCHAR2(20)  | NULL     | 'OPEN'        | CHECK IN ('OPEN','PROCESSING','CLOSED','REVERSED') |
| CLOSED_BY          | VARCHAR2(30)  | NULL     |               |                                                |
| CLOSED_DATE        | DATE          | NULL     |               |                                                |
| CREATED_BY         | VARCHAR2(30)  | NOT NULL |               |                                                |
| CREATED_DATE       | DATE          | NOT NULL | SYSDATE       |                                                |
| MODIFIED_BY        | VARCHAR2(30)  | NULL     |               |                                                |
| MODIFIED_DATE      | DATE          | NULL     |               |                                                |

**Constraints:**
- PK_PAY_PERIODS: PRIMARY KEY (PERIOD_ID)
- CHK_PERIOD_STATUS: CHECK (STATUS IN ('OPEN', 'PROCESSING', 'CLOSED', 'REVERSED'))

---

**Table: HRMS.PAYROLL_RUNS**

| Column              | Data Type     | Nullable | Default     | Notes                                                               |
|---------------------|---------------|----------|-------------|---------------------------------------------------------------------|
| RUN_ID              | NUMBER(10)    | NOT NULL |             | PK                                                                  |
| PERIOD_ID           | NUMBER(10)    | NOT NULL |             | FK → PAY_PERIODS(PERIOD_ID)                                         |
| RUN_TYPE            | VARCHAR2(20)  | NULL     | 'REGULAR'   | CHECK IN ('REGULAR','SUPPLEMENTAL','BONUS','FINAL')                 |
| RUN_DATE            | DATE          | NOT NULL |             |                                                                     |
| STATUS              | VARCHAR2(20)  | NULL     | 'PENDING'   | CHECK IN ('PENDING','CALCULATING','CALCULATED','APPROVED','PAID','REVERSED','ERROR') |
| TOTAL_GROSS         | NUMBER(15,2)  | NULL     |             |                                                                     |
| TOTAL_DEDUCTIONS    | NUMBER(15,2)  | NULL     |             |                                                                     |
| TOTAL_NET           | NUMBER(15,2)  | NULL     |             |                                                                     |
| TOTAL_EMPLOYER_COST | NUMBER(15,2)  | NULL     |             |                                                                     |
| EMPLOYEE_COUNT      | NUMBER(10)    | NULL     |             |                                                                     |
| ERROR_COUNT         | NUMBER(10)    | NULL     | 0           |                                                                     |
| SUBMITTED_BY        | VARCHAR2(30)  | NULL     |             |                                                                     |
| SUBMITTED_DATE      | DATE          | NULL     |             |                                                                     |
| APPROVED_BY         | VARCHAR2(30)  | NULL     |             |                                                                     |
| APPROVED_DATE       | DATE          | NULL     |             |                                                                     |
| CREATED_BY          | VARCHAR2(30)  | NOT NULL |             |                                                                     |
| CREATED_DATE        | DATE          | NOT NULL | SYSDATE     |                                                                     |
| MODIFIED_BY         | VARCHAR2(30)  | NULL     |             |                                                                     |
| MODIFIED_DATE       | DATE          | NULL     |             |                                                                     |

**Constraints:**
- PK_PAYROLL_RUNS: PRIMARY KEY (RUN_ID)
- FK_PR_PERIOD: FOREIGN KEY (PERIOD_ID) REFERENCES HRMS.PAY_PERIODS(PERIOD_ID)
- CHK_RUN_TYPE: CHECK (RUN_TYPE IN ('REGULAR', 'SUPPLEMENTAL', 'BONUS', 'FINAL'))
- CHK_RUN_STATUS: CHECK (STATUS IN ('PENDING', 'CALCULATING', 'CALCULATED', 'APPROVED', 'PAID', 'REVERSED', 'ERROR'))

---

**Table: HRMS.PAYROLL_DETAILS**

| Column        | Data Type      | Nullable | Default        | Notes                                 |
|---------------|----------------|----------|----------------|---------------------------------------|
| DETAIL_ID     | NUMBER(15)     | NOT NULL |                | PK                                    |
| RUN_ID        | NUMBER(10)     | NOT NULL |                | FK → PAYROLL_RUNS(RUN_ID)             |
| EMP_ID        | NUMBER(10)     | NOT NULL |                | FK → EMPLOYEES(EMP_ID)                |
| ELEMENT_ID    | NUMBER(10)     | NOT NULL |                | FK → PAY_ELEMENTS(ELEMENT_ID)         |
| ELEMENT_TYPE  | VARCHAR2(20)   | NOT NULL |                |                                       |
| HOURS_WORKED  | NUMBER(6,2)    | NULL     |                |                                       |
| RATE          | NUMBER(12,4)   | NULL     |                |                                       |
| AMOUNT        | NUMBER(12,2)   | NOT NULL |                |                                       |
| YTD_AMOUNT    | NUMBER(15,2)   | NULL     |                |                                       |
| STATUS        | VARCHAR2(20)   | NULL     | 'CALCULATED'   |                                       |
| ERROR_MESSAGE | VARCHAR2(4000) | NULL     |                |                                       |
| CREATED_BY    | VARCHAR2(30)   | NOT NULL |                |                                       |
| CREATED_DATE  | DATE           | NOT NULL | SYSDATE        |                                       |

**Constraints:**
- PK_PAYROLL_DETAILS: PRIMARY KEY (DETAIL_ID)
- FK_PD_RUN: FOREIGN KEY (RUN_ID) REFERENCES HRMS.PAYROLL_RUNS(RUN_ID)
- FK_PD_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- FK_PD_ELEMENT: FOREIGN KEY (ELEMENT_ID) REFERENCES HRMS.PAY_ELEMENTS(ELEMENT_ID)

---

**Table: HRMS.TAX_BRACKETS**

| Column        | Data Type    | Nullable | Default | Notes                                                               |
|---------------|--------------|----------|---------|---------------------------------------------------------------------|
| BRACKET_ID    | NUMBER(10)   | NOT NULL |         | PK                                                                  |
| TAX_YEAR      | NUMBER(4)    | NOT NULL |         |                                                                     |
| FILING_STATUS | VARCHAR2(30) | NOT NULL |         | CHECK IN ('SINGLE','MARRIED_JOINT','MARRIED_SEPARATE','HEAD_OF_HOUSEHOLD') |
| BRACKET_MIN   | NUMBER(12,2) | NOT NULL |         |                                                                     |
| BRACKET_MAX   | NUMBER(12,2) | NULL     |         | NULL = no upper limit (top bracket)                                 |
| TAX_RATE      | NUMBER(5,4)  | NOT NULL |         |                                                                     |
| BASE_TAX      | NUMBER(12,2) | NULL     | 0       |                                                                     |
| STATE_CODE    | VARCHAR2(3)  | NULL     |         | NULL = federal; populated = state-specific                          |
| ACTIVE_FLAG   | CHAR(1)      | NOT NULL | 'Y'     |                                                                     |
| CREATED_BY    | VARCHAR2(30) | NOT NULL |         |                                                                     |
| CREATED_DATE  | DATE         | NOT NULL | SYSDATE |                                                                     |

**Constraints:**
- PK_TAX_BRACKETS: PRIMARY KEY (BRACKET_ID)
- CHK_FILING_STATUS: CHECK (FILING_STATUS IN ('SINGLE', 'MARRIED_JOINT', 'MARRIED_SEPARATE', 'HEAD_OF_HOUSEHOLD'))

---

**Table: HRMS.EMPLOYEE_TAX_INFO**

| Column               | Data Type    | Nullable | Default | Notes                                                               |
|----------------------|--------------|----------|---------|---------------------------------------------------------------------|
| TAX_INFO_ID          | NUMBER(10)   | NOT NULL |         | PK                                                                  |
| EMP_ID               | NUMBER(10)   | NOT NULL |         | FK → EMPLOYEES(EMP_ID)                                              |
| TAX_YEAR             | NUMBER(4)    | NOT NULL |         |                                                                     |
| FILING_STATUS        | VARCHAR2(30) | NOT NULL |         |                                                                     |
| FEDERAL_ALLOWANCES   | NUMBER(3)    | NULL     | 0       |                                                                     |
| STATE_ALLOWANCES     | NUMBER(3)    | NULL     | 0       |                                                                     |
| ADDITIONAL_FED_WH    | NUMBER(12,2) | NULL     | 0       |                                                                     |
| ADDITIONAL_STATE_WH  | NUMBER(12,2) | NULL     | 0       |                                                                     |
| EXEMPT_FLAG          | CHAR(1)      | NULL     | 'N'     |                                                                     |
| STATE_CODE           | VARCHAR2(3)  | NULL     |         |                                                                     |
| W4_RECEIVED_DATE     | DATE         | NULL     |         |                                                                     |
| ACTIVE_FLAG          | CHAR(1)      | NOT NULL | 'Y'     |                                                                     |
| CREATED_BY           | VARCHAR2(30) | NOT NULL |         |                                                                     |
| CREATED_DATE         | DATE         | NOT NULL | SYSDATE |                                                                     |
| MODIFIED_BY          | VARCHAR2(30) | NULL     |         |                                                                     |
| MODIFIED_DATE        | DATE         | NULL     |         |                                                                     |

**Constraints:**
- PK_EMP_TAX_INFO: PRIMARY KEY (TAX_INFO_ID)
- FK_ETI_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- UK_EMP_TAX_YEAR: UNIQUE (EMP_ID, TAX_YEAR)

---

**Table: HRMS.EMPLOYEE_BANK_ACCOUNTS**

| Column              | Data Type     | Nullable | Default     | Notes                                                     |
|---------------------|---------------|----------|-------------|-----------------------------------------------------------|
| BANK_ACCT_ID        | NUMBER(10)    | NOT NULL |             | PK                                                        |
| EMP_ID              | NUMBER(10)    | NOT NULL |             | FK → EMPLOYEES(EMP_ID)                                    |
| BANK_NAME           | VARCHAR2(100) | NULL     |             |                                                           |
| ROUTING_NUMBER      | VARCHAR2(20)  | NOT NULL |             |                                                           |
| ACCOUNT_NUMBER_ENC  | VARCHAR2(200) | NOT NULL |             | Encrypted                                                 |
| ACCOUNT_TYPE        | VARCHAR2(20)  | NULL     | 'CHECKING'  | CHECK IN ('CHECKING','SAVINGS')                           |
| DEPOSIT_TYPE        | VARCHAR2(20)  | NULL     | 'FULL'      | CHECK IN ('FULL','PARTIAL_AMOUNT','PARTIAL_PERCENT','REMAINDER') |
| DEPOSIT_AMOUNT      | NUMBER(12,2)  | NULL     |             |                                                           |
| DEPOSIT_PERCENTAGE  | NUMBER(5,2)   | NULL     |             |                                                           |
| PRIORITY_ORDER      | NUMBER(2)     | NULL     | 1           |                                                           |
| PRENOTE_SENT        | CHAR(1)       | NULL     | 'N'         |                                                           |
| PRENOTE_DATE        | DATE          | NULL     |             |                                                           |
| ACTIVE_FLAG         | CHAR(1)       | NOT NULL | 'Y'         |                                                           |
| CREATED_BY          | VARCHAR2(30)  | NOT NULL |             |                                                           |
| CREATED_DATE        | DATE          | NOT NULL | SYSDATE     |                                                           |
| MODIFIED_BY         | VARCHAR2(30)  | NULL     |             |                                                           |
| MODIFIED_DATE       | DATE          | NULL     |             |                                                           |

**Constraints:**
- PK_EMP_BANK_ACCTS: PRIMARY KEY (BANK_ACCT_ID)
- FK_BA_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- CHK_ACCT_TYPE: CHECK (ACCOUNT_TYPE IN ('CHECKING', 'SAVINGS'))
- CHK_DEPOSIT_TYPE: CHECK (DEPOSIT_TYPE IN ('FULL', 'PARTIAL_AMOUNT', 'PARTIAL_PERCENT', 'REMAINDER'))

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/03_leave_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.LEAVE_TYPES**

| Column             | Data Type     | Nullable | Default | Notes                                              |
|--------------------|---------------|----------|---------|----------------------------------------------------|
| LEAVE_TYPE_ID      | NUMBER(5)     | NOT NULL |         | PK                                                 |
| LEAVE_TYPE_CODE    | VARCHAR2(20)  | NOT NULL |         | UK                                                 |
| LEAVE_TYPE_NAME    | VARCHAR2(50)  | NOT NULL |         |                                                    |
| PAID_FLAG          | CHAR(1)       | NULL     | 'Y'     |                                                    |
| ACCRUAL_FLAG       | CHAR(1)       | NULL     | 'Y'     |                                                    |
| ACCRUAL_RATE       | NUMBER(6,2)   | NULL     |         |                                                    |
| ACCRUAL_FREQUENCY  | VARCHAR2(20)  | NULL     |         | CHECK IN ('MONTHLY','BIWEEKLY','ANNUAL', NULL)     |
| MAX_BALANCE        | NUMBER(6,2)   | NULL     |         |                                                    |
| CARRYOVER_MAX      | NUMBER(6,2)   | NULL     |         |                                                    |
| CARRYOVER_EXPIRY   | NUMBER(3)     | NULL     |         |                                                    |
| MIN_TENURE_DAYS    | NUMBER(5)     | NULL     | 0       |                                                    |
| REQUIRES_APPROVAL  | CHAR(1)       | NULL     | 'Y'     |                                                    |
| REQUIRES_DOCUMENT  | CHAR(1)       | NULL     | 'N'     |                                                    |
| ACTIVE_FLAG        | CHAR(1)       | NOT NULL | 'Y'     |                                                    |
| CREATED_BY         | VARCHAR2(30)  | NOT NULL |         |                                                    |
| CREATED_DATE       | DATE          | NOT NULL | SYSDATE |                                                    |
| MODIFIED_BY        | VARCHAR2(30)  | NULL     |         |                                                    |
| MODIFIED_DATE      | DATE          | NULL     |         |                                                    |

**Constraints:**
- PK_LEAVE_TYPES: PRIMARY KEY (LEAVE_TYPE_ID)
- UK_LEAVE_TYPE_CODE: UNIQUE (LEAVE_TYPE_CODE)
- CHK_ACCRUAL_FREQ: CHECK (ACCRUAL_FREQUENCY IN ('MONTHLY', 'BIWEEKLY', 'ANNUAL', NULL))

---

**Table: HRMS.LEAVE_BALANCES**

| Column              | Data Type    | Nullable | Default | Notes                                                  |
|---------------------|--------------|----------|---------|--------------------------------------------------------|
| BALANCE_ID          | NUMBER(10)   | NOT NULL |         | PK                                                     |
| EMP_ID              | NUMBER(10)   | NOT NULL |         | FK → EMPLOYEES(EMP_ID)                                 |
| LEAVE_TYPE_ID       | NUMBER(5)    | NOT NULL |         | FK → LEAVE_TYPES(LEAVE_TYPE_ID)                        |
| CALENDAR_YEAR       | NUMBER(4)    | NOT NULL |         |                                                        |
| OPENING_BALANCE     | NUMBER(6,2)  | NULL     | 0       |                                                        |
| ACCRUED             | NUMBER(6,2)  | NULL     | 0       |                                                        |
| USED                | NUMBER(6,2)  | NULL     | 0       |                                                        |
| ADJUSTMENT          | NUMBER(6,2)  | NULL     | 0       |                                                        |
| PENDING             | NUMBER(6,2)  | NULL     | 0       |                                                        |
| AVAILABLE           | NUMBER(6,2)  | VIRTUAL  |         | GENERATED ALWAYS AS (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING) |
| CARRYOVER_FROM_PREV | NUMBER(6,2)  | NULL     | 0       |                                                        |
| CARRYOVER_EXPIRY_DT | DATE         | NULL     |         |                                                        |
| CREATED_BY          | VARCHAR2(30) | NOT NULL |         |                                                        |
| CREATED_DATE        | DATE         | NOT NULL | SYSDATE |                                                        |
| MODIFIED_BY         | VARCHAR2(30) | NULL     |         |                                                        |
| MODIFIED_DATE       | DATE         | NULL     |         |                                                        |

**Virtual Column Formula:** AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING

**Constraints:**
- PK_LEAVE_BALANCES: PRIMARY KEY (BALANCE_ID)
- FK_LB_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- FK_LB_TYPE: FOREIGN KEY (LEAVE_TYPE_ID) REFERENCES HRMS.LEAVE_TYPES(LEAVE_TYPE_ID)
- UK_LEAVE_BAL: UNIQUE (EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR)

---

**Table: HRMS.LEAVE_REQUESTS**

| Column              | Data Type      | Nullable | Default    | Notes                                                         |
|---------------------|----------------|----------|------------|---------------------------------------------------------------|
| REQUEST_ID          | NUMBER(10)     | NOT NULL |            | PK                                                            |
| EMP_ID              | NUMBER(10)     | NOT NULL |            | FK → EMPLOYEES(EMP_ID)                                        |
| LEAVE_TYPE_ID       | NUMBER(5)      | NOT NULL |            | FK → LEAVE_TYPES(LEAVE_TYPE_ID)                               |
| START_DATE          | DATE           | NOT NULL |            |                                                               |
| END_DATE            | DATE           | NOT NULL |            |                                                               |
| TOTAL_DAYS          | NUMBER(5,1)    | NOT NULL |            |                                                               |
| HALF_DAY_FLAG       | CHAR(1)        | NULL     | 'N'        |                                                               |
| HALF_DAY_PERIOD     | VARCHAR2(10)   | NULL     |            | CHECK IN ('AM','PM',NULL)                                     |
| STATUS              | VARCHAR2(20)   | NULL     | 'PENDING'  | CHECK IN ('PENDING','APPROVED','REJECTED','CANCELLED','TAKEN')|
| REASON              | VARCHAR2(4000) | NULL     |            |                                                               |
| SUPPORTING_DOC_PATH | VARCHAR2(500)  | NULL     |            |                                                               |
| APPROVER_EMP_ID     | NUMBER(10)     | NULL     |            | FK → EMPLOYEES(EMP_ID)                                        |
| APPROVAL_DATE       | DATE           | NULL     |            |                                                               |
| APPROVAL_COMMENTS   | VARCHAR2(4000) | NULL     |            |                                                               |
| CANCEL_REASON       | VARCHAR2(4000) | NULL     |            |                                                               |
| CANCELLED_DATE      | DATE           | NULL     |            |                                                               |
| CREATED_BY          | VARCHAR2(30)   | NOT NULL |            |                                                               |
| CREATED_DATE        | DATE           | NOT NULL | SYSDATE    |                                                               |
| MODIFIED_BY         | VARCHAR2(30)   | NULL     |            |                                                               |
| MODIFIED_DATE       | DATE           | NULL     |            |                                                               |

**Constraints:**
- PK_LEAVE_REQUESTS: PRIMARY KEY (REQUEST_ID)
- FK_LR_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- FK_LR_TYPE: FOREIGN KEY (LEAVE_TYPE_ID) REFERENCES HRMS.LEAVE_TYPES(LEAVE_TYPE_ID)
- FK_LR_APPROVER: FOREIGN KEY (APPROVER_EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- CHK_LR_STATUS: CHECK (STATUS IN ('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', 'TAKEN'))
- CHK_LR_DATES: CHECK (END_DATE >= START_DATE)
- CHK_HALF_DAY: CHECK (HALF_DAY_PERIOD IN ('AM', 'PM', NULL))

---

**Table: HRMS.LEAVE_ACCRUAL_LOG**

| Column          | Data Type    | Nullable | Default | Notes                              |
|-----------------|--------------|----------|---------|------------------------------------|
| ACCRUAL_ID      | NUMBER(15)   | NOT NULL |         | PK                                 |
| EMP_ID          | NUMBER(10)   | NOT NULL |         | FK → EMPLOYEES(EMP_ID)             |
| LEAVE_TYPE_ID   | NUMBER(5)    | NOT NULL |         | FK → LEAVE_TYPES(LEAVE_TYPE_ID)    |
| ACCRUAL_DATE    | DATE         | NOT NULL |         |                                    |
| ACCRUAL_AMOUNT  | NUMBER(6,2)  | NOT NULL |         |                                    |
| BALANCE_AFTER   | NUMBER(6,2)  | NULL     |         |                                    |
| RUN_ID          | NUMBER(10)   | NULL     |         |                                    |
| CREATED_BY      | VARCHAR2(30) | NOT NULL |         |                                    |
| CREATED_DATE    | DATE         | NOT NULL | SYSDATE |                                    |

**Constraints:**
- PK_LEAVE_ACCRUAL_LOG: PRIMARY KEY (ACCRUAL_ID)
- FK_LAL_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- FK_LAL_TYPE: FOREIGN KEY (LEAVE_TYPE_ID) REFERENCES HRMS.LEAVE_TYPES(LEAVE_TYPE_ID)

---

**Table: HRMS.HOLIDAYS**

| Column        | Data Type     | Nullable | Default | Notes                              |
|---------------|---------------|----------|---------|------------------------------------|
| HOLIDAY_ID    | NUMBER(5)     | NOT NULL |         | PK                                 |
| HOLIDAY_DATE  | DATE          | NOT NULL |         |                                    |
| HOLIDAY_NAME  | VARCHAR2(100) | NOT NULL |         |                                    |
| LOCATION_CODE | VARCHAR2(10)  | NULL     |         | NULL = global holiday              |
| FLOATING_FLAG | CHAR(1)       | NULL     | 'N'     |                                    |
| ACTIVE_FLAG   | CHAR(1)       | NOT NULL | 'Y'     |                                    |
| CREATED_BY    | VARCHAR2(30)  | NOT NULL |         |                                    |
| CREATED_DATE  | DATE          | NOT NULL | SYSDATE |                                    |

**Constraints:**
- PK_HOLIDAYS: PRIMARY KEY (HOLIDAY_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/tables/04_performance_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.REVIEW_CYCLES**

| Column              | Data Type     | Nullable | Default  | Notes                                                    |
|---------------------|---------------|----------|----------|----------------------------------------------------------|
| CYCLE_ID            | NUMBER(10)    | NOT NULL |          | PK                                                       |
| CYCLE_NAME          | VARCHAR2(100) | NOT NULL |          |                                                          |
| CYCLE_YEAR          | NUMBER(4)     | NOT NULL |          |                                                          |
| START_DATE          | DATE          | NOT NULL |          |                                                          |
| END_DATE            | DATE          | NOT NULL |          |                                                          |
| SELF_REVIEW_DUE     | DATE          | NULL     |          |                                                          |
| MANAGER_REVIEW_DUE  | DATE          | NULL     |          |                                                          |
| CALIBRATION_DUE     | DATE          | NULL     |          |                                                          |
| STATUS              | VARCHAR2(20)  | NULL     | 'DRAFT'  | CHECK IN ('DRAFT','OPEN','IN_PROGRESS','CALIBRATION','CLOSED') |
| CREATED_BY          | VARCHAR2(30)  | NOT NULL |          |                                                          |
| CREATED_DATE        | DATE          | NOT NULL | SYSDATE  |                                                          |
| MODIFIED_BY         | VARCHAR2(30)  | NULL     |          |                                                          |
| MODIFIED_DATE       | DATE          | NULL     |          |                                                          |

**Constraints:**
- PK_REVIEW_CYCLES: PRIMARY KEY (CYCLE_ID)
- CHK_CYCLE_STATUS: CHECK (STATUS IN ('DRAFT', 'OPEN', 'IN_PROGRESS', 'CALIBRATION', 'CLOSED'))

---

**Table: HRMS.PERFORMANCE_REVIEWS**

| Column                  | Data Type     | Nullable | Default        | Notes                                                                        |
|-------------------------|---------------|----------|----------------|------------------------------------------------------------------------------|
| REVIEW_ID               | NUMBER(10)    | NOT NULL |                | PK                                                                           |
| CYCLE_ID                | NUMBER(10)    | NOT NULL |                | FK → REVIEW_CYCLES(CYCLE_ID)                                                 |
| EMP_ID                  | NUMBER(10)    | NOT NULL |                | FK → EMPLOYEES(EMP_ID)                                                       |
| REVIEWER_EMP_ID         | NUMBER(10)    | NOT NULL |                | FK → EMPLOYEES(EMP_ID)                                                       |
| REVIEW_TYPE             | VARCHAR2(20)  | NULL     | 'ANNUAL'       |                                                                              |
| STATUS                  | VARCHAR2(20)  | NULL     | 'NOT_STARTED'  | CHECK (see below)                                                            |
| OVERALL_RATING          | NUMBER(2,1)   | NULL     |                | CHECK BETWEEN 1.0 AND 5.0                                                    |
| RATING_LABEL            | VARCHAR2(50)  | NULL     |                |                                                                              |
| SELF_ASSESSMENT         | CLOB          | NULL     |                |                                                                              |
| MANAGER_ASSESSMENT      | CLOB          | NULL     |                |                                                                              |
| STRENGTHS               | CLOB          | NULL     |                |                                                                              |
| AREAS_FOR_IMPROVEMENT   | CLOB          | NULL     |                |                                                                              |
| DEVELOPMENT_PLAN        | CLOB          | NULL     |                |                                                                              |
| EMPLOYEE_COMMENTS       | CLOB          | NULL     |                |                                                                              |
| EMPLOYEE_ACK_DATE       | DATE          | NULL     |                |                                                                              |
| CALIBRATED_RATING       | NUMBER(2,1)   | NULL     |                |                                                                              |
| CALIBRATION_NOTES       | VARCHAR2(4000)| NULL     |                |                                                                              |
| CREATED_BY              | VARCHAR2(30)  | NOT NULL |                |                                                                              |
| CREATED_DATE            | DATE          | NOT NULL | SYSDATE        |                                                                              |
| MODIFIED_BY             | VARCHAR2(30)  | NULL     |                |                                                                              |
| MODIFIED_DATE           | DATE          | NULL     |                |                                                                              |

**Constraints:**
- PK_PERFORMANCE_REVIEWS: PRIMARY KEY (REVIEW_ID)
- FK_PR_CYCLE: FOREIGN KEY (CYCLE_ID) REFERENCES HRMS.REVIEW_CYCLES(CYCLE_ID)
- FK_PR_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- FK_PR_REVIEWER: FOREIGN KEY (REVIEWER_EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- CHK_REVIEW_STATUS: CHECK (STATUS IN ('NOT_STARTED', 'SELF_REVIEW', 'MANAGER_REVIEW', 'MEETING_SCHEDULED', 'COMPLETED', 'ACKNOWLEDGED'))
- CHK_RATING_RANGE: CHECK (OVERALL_RATING BETWEEN 1.0 AND 5.0)

**Business Rule:** Overall rating must be between 1.0 and 5.0 inclusive.

---

**Table: HRMS.PERFORMANCE_GOALS**

| Column            | Data Type      | Nullable | Default        | Notes                                                                           |
|-------------------|----------------|----------|----------------|---------------------------------------------------------------------------------|
| GOAL_ID           | NUMBER(10)     | NOT NULL |                | PK                                                                              |
| REVIEW_ID         | NUMBER(10)     | NOT NULL |                | FK → PERFORMANCE_REVIEWS(REVIEW_ID)                                             |
| EMP_ID            | NUMBER(10)     | NOT NULL |                | FK → EMPLOYEES(EMP_ID)                                                          |
| GOAL_TITLE        | VARCHAR2(200)  | NOT NULL |                |                                                                                 |
| GOAL_DESCRIPTION  | CLOB           | NULL     |                |                                                                                 |
| GOAL_CATEGORY     | VARCHAR2(30)   | NULL     |                | CHECK IN ('BUSINESS','DEVELOPMENT','LEADERSHIP','INNOVATION','COMPLIANCE')      |
| WEIGHT_PCT        | NUMBER(5,2)    | NULL     | 0              |                                                                                 |
| TARGET_DATE       | DATE           | NULL     |                |                                                                                 |
| STATUS            | VARCHAR2(20)   | NULL     | 'NOT_STARTED'  | CHECK IN ('NOT_STARTED','IN_PROGRESS','COMPLETED','DEFERRED','CANCELLED')       |
| PROGRESS_PCT      | NUMBER(5,2)    | NULL     | 0              |                                                                                 |
| SELF_RATING       | NUMBER(2,1)    | NULL     |                |                                                                                 |
| MANAGER_RATING    | NUMBER(2,1)    | NULL     |                |                                                                                 |
| COMMENTS          | CLOB           | NULL     |                |                                                                                 |
| CREATED_BY        | VARCHAR2(30)   | NOT NULL |                |                                                                                 |
| CREATED_DATE      | DATE           | NOT NULL | SYSDATE        |                                                                                 |
| MODIFIED_BY       | VARCHAR2(30)   | NULL     |                |                                                                                 |
| MODIFIED_DATE     | DATE           | NULL     |                |                                                                                 |

**Constraints:**
- PK_PERF_GOALS: PRIMARY KEY (GOAL_ID)
- FK_PG_REVIEW: FOREIGN KEY (REVIEW_ID) REFERENCES HRMS.PERFORMANCE_REVIEWS(REVIEW_ID)
- FK_PG_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
- CHK_GOAL_STATUS: CHECK (STATUS IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'DEFERRED', 'CANCELLED'))
- CHK_GOAL_CATEGORY: CHECK (GOAL_CATEGORY IN ('BUSINESS', 'DEVELOPMENT', 'LEADERSHIP', 'INNOVATION', 'COMPLIANCE'))

---

**Table: HRMS.AUDIT_LOG**

| Column        | Data Type      | Nullable | Default  | Notes                                    |
|---------------|----------------|----------|----------|------------------------------------------|
| AUDIT_ID      | NUMBER(15)     | NOT NULL |          | PK                                       |
| TABLE_NAME    | VARCHAR2(60)   | NOT NULL |          |                                          |
| RECORD_ID     | NUMBER(15)     | NOT NULL |          |                                          |
| ACTION_TYPE   | VARCHAR2(10)   | NOT NULL |          | CHECK IN ('INSERT','UPDATE','DELETE')    |
| OLD_VALUES    | CLOB           | NULL     |          |                                          |
| NEW_VALUES    | CLOB           | NULL     |          |                                          |
| CHANGED_BY    | VARCHAR2(30)   | NOT NULL |          |                                          |
| CHANGED_DATE  | DATE           | NOT NULL | SYSDATE  |                                          |
| IP_ADDRESS    | VARCHAR2(50)   | NULL     |          |                                          |
| SESSION_ID    | VARCHAR2(100)  | NULL     |          |                                          |

**Constraints:**
- PK_AUDIT_LOG: PRIMARY KEY (AUDIT_ID)
- CHK_AUDIT_ACTION: CHECK (ACTION_TYPE IN ('INSERT', 'UPDATE', 'DELETE'))

---

**Table: HRMS.SYSTEM_PARAMETERS**

| Column            | Data Type      | Nullable | Default      | Notes                          |
|-------------------|----------------|----------|--------------|--------------------------------|
| PARAM_ID          | NUMBER(5)      | NOT NULL |              | PK                             |
| PARAM_GROUP       | VARCHAR2(50)   | NOT NULL |              |                                |
| PARAM_CODE        | VARCHAR2(50)   | NOT NULL |              |                                |
| PARAM_VALUE       | VARCHAR2(4000) | NOT NULL |              |                                |
| PARAM_DESCRIPTION | VARCHAR2(200)  | NULL     |              |                                |
| DATA_TYPE         | VARCHAR2(20)   | NULL     | 'VARCHAR2'   |                                |
| EDITABLE_FLAG     | CHAR(1)        | NULL     | 'Y'          |                                |
| CREATED_BY        | VARCHAR2(30)   | NOT NULL |              |                                |
| CREATED_DATE      | DATE           | NOT NULL | SYSDATE      |                                |
| MODIFIED_BY       | VARCHAR2(30)   | NULL     |              |                                |
| MODIFIED_DATE     | DATE           | NULL     |              |                                |

**Constraints:**
- PK_SYSTEM_PARAMS: PRIMARY KEY (PARAM_ID)
- UK_PARAM_CODE: UNIQUE (PARAM_GROUP, PARAM_CODE)

---

**Table: HRMS.NOTIFICATION_QUEUE**

| Column              | Data Type      | Nullable | Default    | Notes                                          |
|---------------------|----------------|----------|------------|------------------------------------------------|
| NOTIFICATION_ID     | NUMBER(15)     | NOT NULL |            | PK                                             |
| RECIPIENT_EMP_ID    | NUMBER(10)     | NULL     |            |                                                |
| RECIPIENT_EMAIL     | VARCHAR2(100)  | NULL     |            |                                                |
| NOTIFICATION_TYPE   | VARCHAR2(30)   | NOT NULL |            | CHECK IN ('EMAIL','IN_APP','SMS')              |
| SUBJECT             | VARCHAR2(200)  | NOT NULL |            |                                                |
| BODY                | CLOB           | NOT NULL |            |                                                |
| STATUS              | VARCHAR2(20)   | NULL     | 'PENDING'  | CHECK IN ('PENDING','SENT','FAILED','CANCELLED')|
| PRIORITY            | NUMBER(2)      | NULL     | 5          |                                                |
| SENT_DATE           | DATE           | NULL     |            |                                                |
| ERROR_MESSAGE       | VARCHAR2(4000) | NULL     |            |                                                |
| RETRY_COUNT         | NUMBER(3)      | NULL     | 0          |                                                |
| REFERENCE_TABLE     | VARCHAR2(60)   | NULL     |            |                                                |
| REFERENCE_ID        | NUMBER(15)     | NULL     |            |                                                |
| CREATED_BY          | VARCHAR2(30)   | NOT NULL |            |                                                |
| CREATED_DATE        | DATE           | NOT NULL | SYSDATE    |                                                |

**Constraints:**
- PK_NOTIF_QUEUE: PRIMARY KEY (NOTIFICATION_ID)
- CHK_NOTIF_STATUS: CHECK (STATUS IN ('PENDING', 'SENT', 'FAILED', 'CANCELLED'))
- CHK_NOTIF_TYPE: CHECK (NOTIFICATION_TYPE IN ('EMAIL', 'IN_APP', 'SMS'))

**Business Rule (numeric):** Default priority = 5 (scale not defined in DDL); retry count starts at 0.

---

**Table: HRMS.USER_SESSIONS**

| Column          | Data Type      | Nullable | Default    | Notes                              |
|-----------------|----------------|----------|------------|------------------------------------|
| SESSION_ID      | NUMBER(15)     | NOT NULL |            | PK                                 |
| EMP_ID          | NUMBER(10)     | NOT NULL |            | FK → EMPLOYEES(EMP_ID)             |
| USERNAME        | VARCHAR2(30)   | NOT NULL |            |                                    |
| LOGIN_TIME      | DATE           | NOT NULL |            |                                    |
| LOGOUT_TIME     | DATE           | NULL     |            |                                    |
| IP_ADDRESS      | VARCHAR2(50)   | NULL     |            |                                    |
| FORMS_MODULE    | VARCHAR2(100)  | NULL     |            |                                    |
| SESSION_STATUS  | VARCHAR2(20)   | NULL     | 'ACTIVE'   |                                    |
| CREATED_DATE    | DATE           | NOT NULL | SYSDATE    |                                    |

**Constraints:**
- PK_USER_SESSIONS: PRIMARY KEY (SESSION_ID)
- FK_US_EMP: FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)

---

**Table: HRMS.LOOKUP_VALUES**

| Column           | Data Type     | Nullable | Default | Notes                              |
|------------------|---------------|----------|---------|------------------------------------|
| LOOKUP_ID        | NUMBER(10)    | NOT NULL |         | PK                                 |
| LOOKUP_TYPE      | VARCHAR2(50)  | NOT NULL |         |                                    |
| LOOKUP_CODE      | VARCHAR2(50)  | NOT NULL |         |                                    |
| LOOKUP_VALUE     | VARCHAR2(200) | NOT NULL |         |                                    |
| DISPLAY_ORDER    | NUMBER(5)     | NULL     | 0       |                                    |
| PARENT_LOOKUP_ID | NUMBER(10)    | NULL     |         |                                    |
| ACTIVE_FLAG      | CHAR(1)       | NOT NULL | 'Y'     |                                    |
| CREATED_BY       | VARCHAR2(30)  | NOT NULL |         |                                    |
| CREATED_DATE     | DATE          | NOT NULL | SYSDATE |                                    |

**Constraints:**
- PK_LOOKUP_VALUES: PRIMARY KEY (LOOKUP_ID)
- UK_LOOKUP: UNIQUE (LOOKUP_TYPE, LOOKUP_CODE)

---

=== FILE: ts-plsql-oracle-forms-hrms-main/schema/views/hrms_views.sql ===

**Schema:** HRMS
**Used by:** Oracle Reports (.rdf), Forms LOVs, external reporting tools

---

**View: HRMS.VW_ACTIVE_EMPLOYEES**

**Purpose:** Denormalized view of active employees with department, job, manager, location, and salary.

**Columns Returned:**
- e.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME, e.LAST_NAME
- FULL_NAME: `e.FIRST_NAME || ' ' || e.LAST_NAME`
- e.EMAIL, e.PHONE_WORK, e.PHONE_MOBILE
- e.HIRE_DATE
- TENURE_YEARS: `TRUNC(MONTHS_BETWEEN(SYSDATE, e.HIRE_DATE) / 12, 1)` — truncated to 1 decimal place
- e.EMPLOYMENT_TYPE, e.EMPLOYMENT_STATUS
- e.DEPT_ID, d.DEPT_NAME, d.DEPT_CODE, d.COST_CENTER
- e.JOB_ID, j.JOB_TITLE, j.JOB_CODE
- g.GRADE_ID, g.GRADE_NAME
- e.MANAGER_EMP_ID
- MANAGER_NAME: `m.FIRST_NAME || ' ' || m.LAST_NAME`
- e.LOCATION_CODE, l.LOCATION_NAME, l.CITY, l.STATE_PROVINCE, l.COUNTRY_CODE
- CURRENT_SALARY: `sr.BASE_SALARY`
- sr.CURRENCY_CODE, sr.PAY_FREQUENCY

**Joins:**
- FROM EMPLOYEES e
- JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
- JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID
- JOIN JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID
- LEFT JOIN EMPLOYEES m ON e.MANAGER_EMP_ID = m.EMP_ID
- LEFT JOIN LOCATIONS l ON e.LOCATION_CODE = l.LOCATION_CODE
- LEFT JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE)

**Filter:** e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.ACTIVE_FLAG = 'Y'

**Business Rules for salary join:** Active salary record where EFFECTIVE_DATE <= SYSDATE and (END_DATE is null or END_DATE > SYSDATE).

**Tenure Calculation:** TRUNC(MONTHS_BETWEEN(SYSDATE, HIRE_DATE) / 12, 1) — expressed in years, 1 decimal, truncated (not rounded).

---

**View: HRMS.VW_ORG_HIERARCHY**

**Purpose:** Hierarchical org chart.

**Performance Warning (documented):** Degrades significantly with >500 employees.

**Columns Returned:**
- EMP_ID, EMP_NUMBER
- EMP_NAME: `FIRST_NAME || ' ' || LAST_NAME`
- MANAGER_EMP_ID, DEPT_ID
- ORG_LEVEL: `LEVEL` (Oracle CONNECT BY level pseudocolumn)
- ORG_PATH: `SYS_CONNECT_BY_PATH(FIRST_NAME || ' ' || LAST_NAME, ' > ')` — separator is ` > ` (space-greater-space)
- IS_LEAF: `CONNECT_BY_ISLEAF`

**Filter:** EMPLOYMENT_STATUS = 'ACTIVE'
**Hierarchy:** START WITH MANAGER_EMP_ID IS NULL; CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID
**Order:** ORDER SIBLINGS BY LAST_NAME

---

**View: HRMS.VW_EMPLOYEE_COMPENSATION**

**Purpose:** Current compensation details with compa-ratio.

**Columns Returned:**
- e.EMP_ID, e.EMP_NUMBER
- EMP_NAME: `e.FIRST_NAME || ' ' || e.LAST_NAME`
- d.DEPT_NAME, j.JOB_TITLE, g.GRADE_NAME
- sr.BASE_SALARY
- GRADE_MIN: g.MIN_SALARY
- GRADE_MAX: g.MAX_SALARY
- GRADE_MIDPOINT: `(g.MIN_SALARY + g.MAX_SALARY) / 2`
- COMPA_RATIO: `ROUND(sr.BASE_SALARY / ((g.MIN_SALARY + g.MAX_SALARY) / 2) * 100, 1)` — rounded to 1 decimal, expressed as a percentage
- SALARY_EFFECTIVE_DATE: sr.EFFECTIVE_DATE
- LAST_CHANGE_REASON: sr.CHANGE_REASON
- LAST_CHANGE_PCT: sr.CHANGE_PCT

**Joins:**
- FROM EMPLOYEES e
- JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
- JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID
- JOIN JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID
- JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y'

**Filter:** e.EMPLOYMENT_STATUS = 'ACTIVE'

**Compa-ratio formula:** (BASE_SALARY / midpoint) * 100, rounded to 1 decimal. Midpoint = (MIN_SALARY + MAX_SALARY) / 2.

---

**View: HRMS.VW_LEAVE_SUMMARY**

**Purpose:** Current year leave balances with utilization.

**Columns Returned:**
- e.EMP_ID, e.EMP_NUMBER
- EMP_NAME: `e.FIRST_NAME || ' ' || e.LAST_NAME`
- d.DEPT_NAME
- lt.LEAVE_TYPE_NAME
- lb.OPENING_BALANCE, lb.ACCRUED, lb.USED, lb.ADJUSTMENT, lb.PENDING
- AVAILABLE: `lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT` (note: does NOT subtract PENDING here, unlike the virtual column definition — potential discrepancy)
- UTILIZATION_PCT: `ROUND(lb.USED * 100 / NULLIF(lb.OPENING_BALANCE + lb.ACCRUED, 0), 1)` — NULLIF used to prevent divide-by-zero; rounded to 1 decimal

**Joins:**
- FROM LEAVE_BALANCES lb
- JOIN EMPLOYEES e ON lb.EMP_ID = e.EMP_ID
- JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
- JOIN LEAVE_TYPES lt ON lb.LEAVE_TYPE_ID = lt.LEAVE_TYPE_ID

**Filter:** lb.CALENDAR_YEAR = EXTRACT(YEAR FROM SYSDATE) AND e.EMPLOYMENT_STATUS = 'ACTIVE'

**Discrepancy noted:** The AVAILABLE column in the view computes `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT` (4 terms), while the LEAVE_BALANCES virtual column computes `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING` (5 terms, subtracting PENDING). The view omits the PENDING deduction.

---

**View: HRMS.VW_PAYROLL_LATEST**

**Purpose:** Latest payroll run details per employee.

**Columns Returned:**
- pd.EMP_ID, e.EMP_NUMBER
- EMP_NAME: `e.FIRST_NAME || ' ' || e.LAST_NAME`
- pp.PERIOD_NAME
- GROSS_PAY: `SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END)`
- TOTAL_TAXES: `SUM(CASE WHEN pd.ELEMENT_TYPE = 'TAX' THEN ABS(pd.AMOUNT) ELSE 0 END)`
- TOTAL_DEDUCTIONS: `SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END)`
- NET_PAY: `SUM(pd.AMOUNT)`

**Joins:**
- FROM PAYROLL_DETAILS pd
- JOIN EMPLOYEES e ON pd.EMP_ID = e.EMP_ID
- JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
- JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID

**Filter:**
- pr.RUN_ID = (SELECT MAX(pr2.RUN_ID) FROM PAYROLL_RUNS pr2 WHERE pr2.STATUS = 'APPROVED') — only the single latest approved payroll run
- pd.STATUS != 'ERROR' — excludes error rows

**Group By:** pd.EMP_ID, e.EMP_NUMBER, `e.FIRST_NAME || ' ' || e.LAST_NAME`, pp.PERIOD_NAME

**Business Rule:** "Latest" is determined by MAX(RUN_ID) among APPROVED runs. BENEFIT-type elements are aggregated with DEDUCTION into TOTAL_DEDUCTIONS. ABS() applied to TAX and DEDUCTION/BENEFIT amounts (stored as negative).

---

**View: HRMS.VW_PENDING_APPROVALS**

**Purpose:** Unified view of items pending approval across modules (LEAVE and PERFORMANCE).

**Columns Returned (both UNION ALL branches):**
- APPROVAL_TYPE (literal: 'LEAVE' or 'PERFORMANCE')
- ITEM_ID
- APPROVER_ID
- REQUESTOR_NAME
- ITEM_DESCRIPTION
- REQUEST_DATE
- DETAILS

**Branch 1 — LEAVE:**
- APPROVAL_TYPE: 'LEAVE'
- ITEM_ID: lr.REQUEST_ID
- APPROVER_ID: lr.APPROVER_EMP_ID
- REQUESTOR_NAME: `e.FIRST_NAME || ' ' || e.LAST_NAME`
- ITEM_DESCRIPTION: lt.LEAVE_TYPE_NAME
- REQUEST_DATE: lr.CREATED_DATE
- DETAILS: `lr.TOTAL_DAYS || ' day(s) ' || TO_CHAR(lr.START_DATE, 'MM/DD') || '-' || TO_CHAR(lr.END_DATE, 'MM/DD')`
- Filter: lr.STATUS = 'PENDING'
- Joins: LEAVE_REQUESTS lr, EMPLOYEES e (on EMP_ID), LEAVE_TYPES lt (on LEAVE_TYPE_ID)

**Branch 2 — PERFORMANCE:**
- APPROVAL_TYPE: 'PERFORMANCE'
- ITEM_ID: pr.REVIEW_ID
- APPROVER_ID: pr.REVIEWER_EMP_ID
- REQUESTOR_NAME: `e.FIRST_NAME || ' ' || e.LAST_NAME`
- ITEM_DESCRIPTION: `'Performance Review - ' || rc.CYCLE_NAME`
- REQUEST_DATE: pr.CREATED_DATE
- DETAILS: pr.STATUS
- Filter: pr.STATUS = 'MANAGER_REVIEW'
- Joins: PERFORMANCE_REVIEWS pr, EMPLOYEES e (on EMP_ID), REVIEW_CYCLES rc (on CYCLE_ID)

**Date Format for leave details:** 'MM/DD' (no year)
