=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_SECURITY.pks ===

**Package:** HRMS.PKG_SECURITY
**Schema:** HRMS
**Type:** Package Specification (header only; body not provided)

**Purpose:** Authentication, authorization, session management, role-based access, encryption.

**Dependencies:**
- PKG_COMMON (referenced in comments)
- PKG_AUDIT (referenced in comments)

**Called By:**
- HRMS_LOGIN form
- All forms (session validation)

---

**Known Issues / Constraints (from inline comments):**
- Password stored as MD5 hash (should be bcrypt/scrypt)
- Session timeout check uses DB server time, not application server time
- No account lockout after failed attempts
- DBMS_CRYPTO key hard-coded in package body

---

**Custom Exceptions:**

| Exception Name          | Error Code | PRAGMA Init |
|-------------------------|------------|-------------|
| e_invalid_credentials   | -20301     | Yes         |
| e_account_locked        | -20302     | Yes         |
| e_session_expired       | -20303     | Yes         |
| e_insufficient_priv     | -20304     | Yes         |

---

**Functions and Procedures:**

1. `FUNCTION authenticate(p_username IN VARCHAR2, p_password IN VARCHAR2, p_ip_address IN VARCHAR2 DEFAULT NULL) RETURN NUMBER`
   - Authenticates user by username/password; optionally records IP address; returns a session identifier (NUMBER)

2. `PROCEDURE logout(p_session_id IN NUMBER)`
   - Terminates the session identified by p_session_id

3. `FUNCTION is_session_valid(p_session_id IN NUMBER) RETURN BOOLEAN`
   - Returns TRUE if the given session is still active/not expired

4. `FUNCTION has_permission(p_emp_id IN NUMBER, p_module IN VARCHAR2, p_action IN VARCHAR2 DEFAULT 'VIEW') RETURN BOOLEAN`
   - Returns TRUE if the employee has the requested permission on the given module
   - Default action is 'VIEW'

5. `FUNCTION encrypt_ssn(p_ssn IN VARCHAR2) RETURN VARCHAR2`
   - Encrypts a plain-text SSN; returns encrypted VARCHAR2

6. `FUNCTION decrypt_ssn(p_encrypted IN VARCHAR2) RETURN VARCHAR2`
   - Decrypts an encrypted SSN; returns plain-text VARCHAR2

7. `FUNCTION hash_password(p_password IN VARCHAR2) RETURN VARCHAR2`
   - Returns a hash (MD5 per known issue) of the plain-text password

8. `PROCEDURE change_password(p_emp_id IN NUMBER, p_old_password IN VARCHAR2, p_new_password IN VARCHAR2)`
   - Changes the employee's password after verifying the old password

---

**External Packages Referenced:**
- DBMS_CRYPTO (body; key hard-coded)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pkb ===

**Package:** HRMS.PKG_VALIDATION
**Type:** Package Body

**Dependencies:**
- PKG_COMMON (called for email/phone validation)
- Tables: JOB_GRADES, EMPLOYEES, HOLIDAYS

---

**Function: validate_date_range**
```
FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN
```
Logic:
- IF p_start_date IS NULL OR p_end_date IS NULL → RETURN FALSE
- RETURN p_end_date >= p_start_date

Business Rule: Both dates required; end date must be on or after start date.

---

**Function: validate_salary_for_grade**
```
FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2
```
Logic:
- IF p_salary IS NULL OR p_grade_id IS NULL → RETURN 'Salary and grade are required'
- SELECT MIN_SALARY, MAX_SALARY, GRADE_NAME FROM JOB_GRADES WHERE GRADE_ID = p_grade_id
- IF p_salary < v_min → RETURN 'Salary ' || formatted_salary || ' is below minimum for grade ' || v_grade_name || ' (' || formatted_min || ')'
- ELSIF p_salary > v_max → RETURN 'Salary ' || formatted_salary || ' exceeds maximum for grade ' || v_grade_name || ' (' || formatted_max || ')'
- RETURN NULL (valid)
- EXCEPTION WHEN NO_DATA_FOUND → RETURN 'Invalid grade ID: ' || p_grade_id

Number format mask used: `'FM$999,999,990.00'`

Tables accessed: JOB_GRADES (columns: MIN_SALARY, MAX_SALARY, GRADE_NAME, GRADE_ID)

Business Rule: Salary must be within the min/max band defined in JOB_GRADES for the given grade.

---

**Function: validate_email_format**
```
FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN
```
Logic: Delegates entirely to PKG_COMMON.is_valid_email(p_email)

---

**Function: validate_phone_format**
```
FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN
```
Logic: Delegates entirely to PKG_COMMON.is_valid_phone(p_phone)

---

**Function: validate_emp_number_format**
```
FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN
```
Logic: RETURN REGEXP_LIKE(p_emp_number, '^EMP-\d{6}$')

Business Rule: Employee number must exactly match the pattern `EMP-` followed by exactly 6 digits. Example valid value: `EMP-001234`.

---

**Function: is_future_date**
```
FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN
```
Logic: RETURN TRUNC(p_date) > TRUNC(SYSDATE)

Business Rule: A date is "future" only if its truncated (time-stripped) value is strictly greater than today.

---

**Function: is_business_day**
```
FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN
```
Logic:
1. v_day := TO_CHAR(p_date, 'DY', 'NLS_DATE_LANGUAGE=AMERICAN')
2. IF v_day IN ('SAT', 'SUN') → RETURN FALSE
3. SELECT COUNT(*) FROM HOLIDAYS WHERE HOLIDAY_DATE = TRUNC(p_date) AND ACTIVE_FLAG = 'Y' AND (LOCATION_CODE IS NULL OR LOCATION_CODE = p_location_code)
4. RETURN v_holiday_count = 0

Tables accessed: HOLIDAYS (columns: HOLIDAY_DATE, ACTIVE_FLAG, LOCATION_CODE)

Business Rules:
- Saturday and Sunday are never business days.
- Any active holiday matching the date (either global or matching the provided location code) is not a business day.
- Location-specific holidays override nothing — both global (LOCATION_CODE IS NULL) and location-specific holidays are checked.

---

**Function: validate_required_fields**
```
FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2
```
Logic (for p_table_name = 'EMPLOYEES'):
- SELECT * FROM EMPLOYEES WHERE EMP_ID = p_record_id into v_rec
- IF v_rec.FIRST_NAME IS NULL → RETURN 'First Name is required'
- IF v_rec.LAST_NAME IS NULL → RETURN 'Last Name is required'
- IF v_rec.HIRE_DATE IS NULL → RETURN 'Hire Date is required'
- IF v_rec.DEPT_ID IS NULL → RETURN 'Department is required'
- IF v_rec.JOB_ID IS NULL → RETURN 'Job Title is required'
- EXCEPTION WHEN NO_DATA_FOUND → RETURN 'Record not found'
- RETURN NULL (all required fields populated)

Comment: "Simplified validation — in production would use data dictionary to check NOT NULL columns"
Only the EMPLOYEES table case is currently implemented.

Tables accessed: EMPLOYEES (columns: EMP_ID, FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID)

Business Rules for EMPLOYEES required fields: FIRST_NAME, LAST_NAME, HIRE_DATE, DEPT_ID, JOB_ID are all mandatory.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_VALIDATION.pks ===

**Package:** HRMS.PKG_VALIDATION
**Type:** Package Specification

**Dependencies:** PKG_COMMON

**Called By:** All forms (WHEN-VALIDATE-ITEM triggers), PKG_EMPLOYEE, PKG_PAYROLL

**Functions Declared:**

1. `FUNCTION validate_date_range(p_start_date IN DATE, p_end_date IN DATE) RETURN BOOLEAN`

2. `FUNCTION validate_salary_for_grade(p_salary IN NUMBER, p_grade_id IN NUMBER) RETURN VARCHAR2`
   - Returns NULL if valid; error message string if invalid

3. `FUNCTION validate_email_format(p_email IN VARCHAR2) RETURN BOOLEAN`

4. `FUNCTION validate_phone_format(p_phone IN VARCHAR2) RETURN BOOLEAN`

5. `FUNCTION validate_emp_number_format(p_emp_number IN VARCHAR2) RETURN BOOLEAN`

6. `FUNCTION is_future_date(p_date IN DATE) RETURN BOOLEAN`

7. `FUNCTION is_business_day(p_date IN DATE, p_location_code IN VARCHAR2 DEFAULT NULL) RETURN BOOLEAN`

8. `FUNCTION validate_required_fields(p_table_name IN VARCHAR2, p_record_id IN NUMBER) RETURN VARCHAR2`
   - Returns NULL if all required fields populated; error message otherwise

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_audit.sql ===

**File Type:** Database Triggers (3 triggers)

---

**Trigger: TRG_SALARY_AUDIT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_SALARY_AUDIT
AFTER INSERT OR UPDATE OR DELETE ON HRMS.SALARY_RECORDS
FOR EACH ROW
```
Firing: After INSERT, UPDATE, or DELETE on HRMS.SALARY_RECORDS, for each row.

Logic:
- INSERTING:
  - v_action := 'INSERT'
  - v_new_json := `{"emp_id":<:NEW.EMP_ID>,"salary":<:NEW.BASE_SALARY>,"effective":"<:NEW.EFFECTIVE_DATE YYYY-MM-DD>"}`
- UPDATING:
  - v_action := 'UPDATE'
  - v_old_json := `{"salary":<:OLD.BASE_SALARY>,"active":"<:OLD.ACTIVE_FLAG>"}`
  - v_new_json := `{"salary":<:NEW.BASE_SALARY>,"active":"<:NEW.ACTIVE_FLAG>"}`
- DELETING:
  - v_action := 'DELETE'
  - v_old_json := `{"emp_id":<:OLD.EMP_ID>,"salary":<:OLD.BASE_SALARY>}`
- Calls: PKG_AUDIT.log_action('SALARY_RECORDS', NVL(:NEW.SALARY_ID, :OLD.SALARY_ID), v_action, NVL(:NEW.MODIFIED_BY, USER), v_old_json, v_new_json)

Tables: HRMS.SALARY_RECORDS (columns referenced: EMP_ID, SALARY_ID, BASE_SALARY, EFFECTIVE_DATE, ACTIVE_FLAG, MODIFIED_BY)

External Package Called: PKG_AUDIT.log_action

Business Rule: All salary record changes (insert, update, delete) are captured in JSON format for compliance audit trail.

---

**Trigger: TRG_LEAVE_REQUEST_AUDIT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_LEAVE_REQUEST_AUDIT
AFTER UPDATE OF STATUS ON HRMS.LEAVE_REQUESTS
FOR EACH ROW
```
Firing: After UPDATE of STATUS column only on HRMS.LEAVE_REQUESTS, for each row.

Logic:
- Calls PKG_AUDIT.log_action('LEAVE_REQUESTS', :NEW.REQUEST_ID, 'STATUS_CHANGE', NVL(:NEW.MODIFIED_BY, USER), '{"status":"<:OLD.STATUS>"}', '{"status":"<:NEW.STATUS>"}')

Tables: HRMS.LEAVE_REQUESTS (columns: REQUEST_ID, STATUS, MODIFIED_BY)

External Package Called: PKG_AUDIT.log_action

Business Rule: All leave request status changes are audited.

---

**Trigger: TRG_DEPARTMENT_AUDIT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_DEPARTMENT_AUDIT
AFTER INSERT OR UPDATE OR DELETE ON HRMS.DEPARTMENTS
FOR EACH ROW
```
Firing: After INSERT, UPDATE, or DELETE on HRMS.DEPARTMENTS, for each row.

Logic:
- INSERTING → v_action := 'INSERT'
- UPDATING → v_action := 'UPDATE'
- DELETING → v_action := 'DELETE'
- Calls PKG_AUDIT.log_action('DEPARTMENTS', NVL(:NEW.DEPT_ID, :OLD.DEPT_ID), v_action, USER)
  - Note: no old/new JSON values passed; only USER (not MODIFIED_BY) is used as the changed_by

Tables: HRMS.DEPARTMENTS (columns: DEPT_ID)

External Package Called: PKG_AUDIT.log_action

Business Rule: All department structure changes are audited.

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/triggers/trg_employees.sql ===

**File Type:** Database Triggers (3 triggers on HRMS.EMPLOYEES)

**Comment:** Logic here duplicates PKG_EMPLOYEE and Forms triggers — noted as a common anti-pattern in legacy Oracle Forms applications.

---

**Trigger: TRG_EMP_BEFORE_INSERT**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_EMP_BEFORE_INSERT
BEFORE INSERT ON HRMS.EMPLOYEES
FOR EACH ROW
```
Firing: Before each INSERT on HRMS.EMPLOYEES.

Logic:
1. IF :NEW.CREATED_BY IS NULL → :NEW.CREATED_BY := USER
2. IF :NEW.CREATED_DATE IS NULL → :NEW.CREATED_DATE := SYSDATE
3. IF :NEW.ACTIVE_FLAG IS NULL → :NEW.ACTIVE_FLAG := 'Y'
4. IF :NEW.EMPLOYMENT_STATUS IS NULL → :NEW.EMPLOYMENT_STATUS := 'ACTIVE'
5. IF :NEW.HIRE_DATE > SYSDATE + 180 → RAISE_APPLICATION_ERROR(-20501, 'Hire date cannot be more than 180 days in the future')
6. Uniqueness check:
   - SELECT COUNT(*) FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(:NEW.EMAIL) AND ACTIVE_FLAG = 'Y'
   - IF v_count > 0 → RAISE_APPLICATION_ERROR(-20502, 'Email address already in use: ' || :NEW.EMAIL)

Business Rules:
- CREATED_BY defaults to current DB user (USER).
- CREATED_DATE defaults to SYSDATE.
- ACTIVE_FLAG defaults to 'Y'.
- EMPLOYMENT_STATUS defaults to 'ACTIVE'.
- Hire date may not be more than **180 days** in the future (error code -20501).
- Email address must be unique among active employees (case-insensitive; error code -20502). Note: also enforced by a UNIQUE constraint, but trigger gives a better message.

Tables accessed: HRMS.EMPLOYEES (SELECT for email uniqueness check; columns: EMAIL, ACTIVE_FLAG)

Custom Exceptions:
| Code   | Message                                                              |
|--------|----------------------------------------------------------------------|
| -20501 | Hire date cannot be more than 180 days in the future                |
| -20502 | Email address already in use: \<email\>                             |

---

**Trigger: TRG_EMP_BEFORE_UPDATE**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_EMP_BEFORE_UPDATE
BEFORE UPDATE ON HRMS.EMPLOYEES
FOR EACH ROW
```
Firing: Before each UPDATE on HRMS.EMPLOYEES.

Logic:
1. :NEW.MODIFIED_BY := NVL(:NEW.MODIFIED_BY, USER)
2. :NEW.MODIFIED_DATE := SYSDATE
3. IF :OLD.EMPLOYMENT_STATUS = 'TERMINATED' AND :NEW.EMPLOYMENT_STATUS = 'ACTIVE' →
   RAISE_APPLICATION_ERROR(-20503, 'Cannot directly reactivate a terminated employee. Use the rehire process.')
4. IF :OLD.EMPLOYMENT_STATUS != :NEW.EMPLOYMENT_STATUS →
   INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)
   VALUES (SEQ_EMP_HISTORY.NEXTVAL, :NEW.EMP_ID, 'STATUS_CHANGE', SYSDATE, :OLD.EMPLOYMENT_STATUS, :NEW.EMPLOYMENT_STATUS, NVL(:NEW.MODIFIED_BY, USER), 'Triggered by status update')
5. IF NVL(:OLD.DEPT_ID, -1) != NVL(:NEW.DEPT_ID, -1) →
   INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)
   VALUES (SEQ_EMP_HISTORY.NEXTVAL, :NEW.EMP_ID, 'DEPARTMENT_CHANGE', SYSDATE, TO_CHAR(:OLD.DEPT_ID), TO_CHAR(:NEW.DEPT_ID), NVL(:NEW.MODIFIED_BY, USER), 'Department transfer')
6. IF NVL(:OLD.JOB_ID, -1) != NVL(:NEW.JOB_ID, -1) →
   INSERT INTO EMPLOYEE_HISTORY (HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)
   VALUES (SEQ_EMP_HISTORY.NEXTVAL, :NEW.EMP_ID, 'JOB_CHANGE', SYSDATE, TO_CHAR(:OLD.JOB_ID), TO_CHAR(:NEW.JOB_ID), NVL(:NEW.MODIFIED_BY, USER), 'Job title change')

Business Rules:
- MODIFIED_BY and MODIFIED_DATE are auto-stamped on every update.
- Direct reactivation of a TERMINATED employee to ACTIVE via UPDATE is blocked (error -20503); must use rehire process.
- Any change to EMPLOYMENT_STATUS writes a 'STATUS_CHANGE' history record to EMPLOYEE_HISTORY.
- Any change to DEPT_ID writes a 'DEPARTMENT_CHANGE' history record to EMPLOYEE_HISTORY.
- Any change to JOB_ID writes a 'JOB_CHANGE' history record to EMPLOYEE_HISTORY.
- NULL DEPT_ID and NULL JOB_ID are compared using sentinel value -1 (i.e., NVL(col, -1)) to treat NULL→NULL as no change.

Tables accessed / written:
- HRMS.EMPLOYEES (read :OLD/:NEW values)
- HRMS.EMPLOYEE_HISTORY (INSERT; columns: HISTORY_ID, EMP_ID, CHANGE_TYPE, CHANGE_DATE, OLD_VALUE, NEW_VALUE, CHANGED_BY, CHANGE_REASON)

Sequences used: SEQ_EMP_HISTORY.NEXTVAL

Custom Exceptions:
| Code   | Message                                                                                      |
|--------|----------------------------------------------------------------------------------------------|
| -20503 | Cannot directly reactivate a terminated employee. Use the rehire process.                   |

---

**Trigger: TRG_EMP_INSTEAD_OF_DELETE (named TRG_EMP_BEFORE_DELETE in comments)**
```
CREATE OR REPLACE TRIGGER HRMS.TRG_EMP_INSTEAD_OF_DELETE
BEFORE DELETE ON HRMS.EMPLOYEES
FOR EACH ROW
```
Firing: Before each DELETE on HRMS.EMPLOYEES.

Logic:
- Unconditionally: RAISE_APPLICATION_ERROR(-20504, 'Direct deletion not allowed. Use termination process or set ACTIVE_FLAG to N.')

Business Rule: Direct physical deletion of EMPLOYEES rows is prohibited; all "deletes" must go through the termination process or set ACTIVE_FLAG = 'N' (soft delete pattern).

Known Bug (from inline comment): Trigger is declared as BEFORE DELETE (not INSTEAD OF), which prevents any DELETEs; Oracle Forms workaround is to set ACTIVE_FLAG = 'N' then CLEAR_RECORD instead of DELETE_RECORD.

Custom Exceptions:
| Code   | Message                                                                          |
|--------|----------------------------------------------------------------------------------|
| -20504 | Direct deletion not allowed. Use termination process or set ACTIVE_FLAG to N.  |

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/README.md ===

**Application Name:** HR Management System (HRMS)
**Platform:** Oracle Forms 12c / Oracle WebLogic 12c / Oracle Database 19c
**Schema:** HRMS
**Concurrent Users:** approximately 200 across 3 regional offices

**Module List:**
- Employee Records — hire, transfer, terminate, personal details, job history
- Department & Organization — department hierarchy, cost centers, reporting lines
- Payroll Processing — salary calculations, deductions, tax withholding, pay runs
- Leave Management — leave requests, approvals, balance tracking, accrual rules
- Performance Reviews — annual review cycles, ratings, goal tracking
- Reporting — headcount, compensation analysis, turnover, compliance

**Version History:**
- Originally Oracle Forms 6i, circa 2002
- Upgraded to Forms 11g in 2012
- Currently Forms 12c on Oracle Database 19c

**Architecture (from diagram):**
- Oracle Forms 12c Application Server
- Oracle WebLogic 12c Server
- Three artifact layers: Forms Modules (.fmb/.fmx) — 18 forms; PL/SQL Packages & Procedures — 12 packages; Oracle Reports (.rdf/.rep) — 8 reports
- Oracle Database 19c (HRMS schema): 42 tables, 15 views, 200+ triggers

**Forms Files (xml-exports):**
- HRMS_EMPLOYEE.xml — Employee maintenance form
- HRMS_DEPARTMENT.xml — Department management form
- HRMS_PAYROLL.xml — Payroll processing form
- HRMS_LEAVE.xml — Leave request and approval form
- HRMS_PERFORMANCE.xml — Performance review form
- HRMS_LOGIN.xml — Login and authentication form
- HRMS_MENU.xml — Main menu navigation form
- HRMS_REPORTS.xml — Report parameter and launcher form
- HRMS_LOV.xml — Shared List of Values library
- HRMS_TOOLBAR.xml — Shared toolbar object library

**PL/SQL Packages:**
- PKG_EMPLOYEE.pks/.pkb
- PKG_DEPARTMENT.pks/.pkb
- PKG_PAYROLL.pks/.pkb
- PKG_LEAVE.pks/.pkb
- PKG_PERFORMANCE.pks/.pkb
- PKG_SECURITY.pks/.pkb
- PKG_AUDIT.pks/.pkb
- PKG_NOTIFICATION.pks/.pkb
- PKG_REPORTING.pks/.pkb
- PKG_COMMON.pks/.pkb
- PKG_VALIDATION.pks/.pkb
- PKG_INTEGRATION.pks/.pkb

**Oracle Forms Technical Characteristics:**
- Triggers: WHEN-NEW-FORM-INSTANCE, WHEN-VALIDATE-ITEM, WHEN-BUTTON-PRESSED, POST-QUERY, PRE-INSERT, PRE-UPDATE
- LOV (List of Values): Record groups with dynamic WHERE clauses
- Canvas/block architecture: Multiple data blocks per form, master-detail relationships
- PLL libraries: Shared PL/SQL libraries attached to all forms
- Menu modules (.mmb): Role-based menu system with security

**PL/SQL Patterns:**
- Heavy use of DBMS_OUTPUT, UTL_FILE, UTL_MAIL built-in packages
- Cursor-based processing (row-by-row) for batch operations
- Exception handling with custom error codes (-20000 to -20999)
- Dynamic SQL via EXECUTE IMMEDIATE
- Global package variables for session state management
- Implicit cursors and %ROWTYPE / %TYPE declarations

**Database Patterns:**
- Surrogate keys via sequences + BEFORE INSERT triggers
- Soft deletes (ACTIVE_FLAG CHAR(1) DEFAULT 'Y')
- Audit columns on every table (CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE)
- History tables (_HIST suffix) for change tracking
- Denormalized reporting tables refreshed nightly by batch jobs

**Known Technical Debt:**
- No unit tests; all testing is manual via Forms
- Business logic split between Forms triggers and database packages with no clear boundary
- Several packages exceed 3,000 lines
- Hard-coded configuration values in package bodies
- VARCHAR2(4000) used as catch-all for text fields
- Mixed naming conventions (some CAMELCASE, some UNDERSCORE_CASE)
- Dead code from decommissioned modules still present
- Circular package dependencies between PKG_EMPLOYEE and PKG_PAYROLL

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/sequences/hrms_sequences.sql ===

**Schema:** HRMS
**All sequences use NOCACHE unless noted.**

**Known Bug:** SEQ_EMP_NUMBER uses NOCACHE causing gaps, but PKG_EMPLOYEE.generate_emp_number uses MAX()+1 instead, creating a race condition.

**Complete Sequence List:**

| Sequence Name            | Start With | Increment By | Cache   | Purpose                                              |
|--------------------------|------------|--------------|---------|------------------------------------------------------|
| SEQ_DEPARTMENT           | 100        | 1            | NOCACHE | DEPARTMENTS surrogate key                            |
| SEQ_LOCATION             | 100        | 1            | NOCACHE | LOCATIONS surrogate key                              |
| SEQ_JOB_GRADE            | 100        | 1            | NOCACHE | JOB_GRADES surrogate key                             |
| SEQ_JOB_TITLE            | 100        | 1            | NOCACHE | JOB_TITLES surrogate key                             |
| SEQ_EMPLOYEE             | 10000      | 1            | NOCACHE | EMPLOYEES surrogate key                              |
| SEQ_EMP_HISTORY          | 1          | 1            | NOCACHE | EMPLOYEE_HISTORY surrogate key                       |
| SEQ_DEPENDENT            | 1          | 1            | NOCACHE | EMPLOYEE_DEPENDENTS surrogate key                    |
| SEQ_EMERGENCY_CONTACT    | 1          | 1            | NOCACHE | EMERGENCY_CONTACTS surrogate key                     |
| SEQ_EMP_NUMBER           | 1000       | 1            | NOCACHE | Employee number generation (EMP-XXXXXX format); has race condition bug |
| SEQ_SALARY               | 1          | 1            | NOCACHE | SALARY_RECORDS surrogate key                         |
| SEQ_PAY_ELEMENT          | 1          | 1            | NOCACHE | PAY_ELEMENTS surrogate key                           |
| SEQ_EMP_PAY_ELEMENT      | 1          | 1            | NOCACHE | EMPLOYEE_PAY_ELEMENTS surrogate key                  |
| SEQ_PAY_PERIOD           | 1          | 1            | NOCACHE | PAY_PERIODS surrogate key                            |
| SEQ_PAYROLL_RUN          | 1          | 1            | NOCACHE | PAYROLL_RUNS surrogate key                           |
| SEQ_PAYROLL_DETAIL       | 1          | 1            | NOCACHE | PAYROLL_DETAILS surrogate key                        |
| SEQ_TAX_BRACKET          | 1          | 1            | NOCACHE | TAX_BRACKETS surrogate key                           |
| SEQ_LEAVE_TYPE           | 1          | 1            | NOCACHE | LEAVE_TYPES surrogate key                            |
| SEQ_LEAVE_BALANCE        | 1          | 1            | NOCACHE | LEAVE_BALANCES surrogate key                         |
| SEQ_LEAVE_REQUEST        | 1          | 1            | NOCACHE | LEAVE_REQUESTS surrogate key                         |
| SEQ_LEAVE_ACCRUAL        | 1          | 1            | NOCACHE | LEAVE_ACCRUAL_LOG surrogate key                      |
| SEQ_HOLIDAY              | 1          | 1            | NOCACHE | HOLIDAYS surrogate key                               |
| SEQ_REVIEW_CYCLE         | 1          | 1            | NOCACHE | REVIEW_CYCLES surrogate key                          |
| SEQ_PERF_REVIEW          | 1          | 1            | NOCACHE | PERFORMANCE_REVIEWS surrogate key                    |
| SEQ_PERF_GOAL            | 1          | 1            | NOCACHE | PERFORMANCE_GOALS surrogate key                      |
| SEQ_AUDIT                | 1          | 1            | CACHE 100 | AUDIT_LOG surrogate key (only cached sequence)     |
| SEQ_NOTIFICATION         | 1          | 1            | NOCACHE | NOTIFICATION_QUEUE surrogate key                     |
| SEQ_USER_SESSION         | 1          | 1            | NOCACHE | USER_SESSIONS surrogate key                          |
| SEQ_SYSTEM_PARAM         | 1          | 1            | NOCACHE | SYSTEM_PARAMETERS surrogate key                      |
| SEQ_LOOKUP               | 1          | 1            | NOCACHE | LOOKUP_VALUES surrogate key                          |

**Total sequences:** 29

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/01_core_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.DEPARTMENTS**

| Column           | Data Type       | Constraints / Default       | Notes                                    |
|------------------|-----------------|------------------------------|------------------------------------------|
| DEPT_ID          | NUMBER(10)      | NOT NULL, PK                |                                          |
| DEPT_CODE        | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_DEPT_CODE) |                                       |
| DEPT_NAME        | VARCHAR2(100)   | NOT NULL                    |                                          |
| PARENT_DEPT_ID   | NUMBER(10)      | nullable                    | Self-referencing FK for dept hierarchy   |
| COST_CENTER      | VARCHAR2(20)    | nullable                    | Financial cost center code for GL integration |
| MANAGER_EMP_ID   | NUMBER(10)      | nullable                    |                                          |
| LOCATION_CODE    | VARCHAR2(10)    | nullable                    |                                          |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y', CHECK IN ('Y','N') |                            |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                    |                                          |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE   |                                          |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                    |                                          |
| MODIFIED_DATE    | DATE            | nullable                    |                                          |

Constraints: PK_DEPARTMENTS (DEPT_ID), UK_DEPT_CODE (DEPT_CODE), CHK_DEPT_ACTIVE (ACTIVE_FLAG IN ('Y','N'))

Table comment: 'Organization departments and cost centers'
Column comments: PARENT_DEPT_ID — 'Self-referencing FK for department hierarchy'; COST_CENTER — 'Financial cost center code for GL integration'

---

**Table: HRMS.LOCATIONS**

| Column           | Data Type       | Constraints / Default         |
|------------------|-----------------|-------------------------------|
| LOCATION_CODE    | VARCHAR2(10)    | NOT NULL, PK                  |
| LOCATION_NAME    | VARCHAR2(100)   | NOT NULL                      |
| ADDRESS_LINE1    | VARCHAR2(200)   | nullable                      |
| ADDRESS_LINE2    | VARCHAR2(200)   | nullable                      |
| CITY             | VARCHAR2(100)   | nullable                      |
| STATE_PROVINCE   | VARCHAR2(100)   | nullable                      |
| POSTAL_CODE      | VARCHAR2(20)    | nullable                      |
| COUNTRY_CODE     | VARCHAR2(3)     | nullable                      |
| PHONE_NUMBER     | VARCHAR2(30)    | nullable                      |
| TIMEZONE         | VARCHAR2(50)    | DEFAULT 'America/New_York'    |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'         |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                      |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE     |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                      |
| MODIFIED_DATE    | DATE            | nullable                      |

Constraints: PK_LOCATIONS (LOCATION_CODE)

---

**Table: HRMS.JOB_GRADES**

| Column           | Data Type       | Constraints / Default                     |
|------------------|-----------------|-------------------------------------------|
| GRADE_ID         | NUMBER(5)       | NOT NULL, PK                              |
| GRADE_CODE       | VARCHAR2(10)    | NOT NULL, UNIQUE (UK_GRADE_CODE)          |
| GRADE_NAME       | VARCHAR2(50)    | NOT NULL                                  |
| MIN_SALARY       | NUMBER(12,2)    | NOT NULL                                  |
| MAX_SALARY       | NUMBER(12,2)    | NOT NULL                                  |
| OVERTIME_ELIGIBLE| CHAR(1)         | DEFAULT 'N'                               |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                     |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                  |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                 |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                  |
| MODIFIED_DATE    | DATE            | nullable                                  |

Constraints: PK_JOB_GRADES (GRADE_ID), UK_GRADE_CODE (GRADE_CODE), CHK_SALARY_RANGE (MAX_SALARY >= MIN_SALARY)

Business Rule: Maximum salary must be greater than or equal to minimum salary (CHECK constraint CHK_SALARY_RANGE).

---

**Table: HRMS.JOB_TITLES**

| Column           | Data Type       | Constraints / Default                        |
|------------------|-----------------|----------------------------------------------|
| JOB_ID           | NUMBER(10)      | NOT NULL, PK                                 |
| JOB_CODE         | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_JOB_CODE)               |
| JOB_TITLE        | VARCHAR2(100)   | NOT NULL                                     |
| JOB_FAMILY       | VARCHAR2(50)    | nullable                                     |
| GRADE_ID         | NUMBER(5)       | NOT NULL, FK → JOB_GRADES(GRADE_ID)          |
| EEO_CATEGORY     | VARCHAR2(10)    | nullable                                     |
| FLSA_STATUS      | VARCHAR2(10)    | DEFAULT 'EXEMPT'                             |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                        |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                     |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                    |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                     |
| MODIFIED_DATE    | DATE            | nullable                                     |

Constraints: PK_JOB_TITLES (JOB_ID), UK_JOB_CODE (JOB_CODE), FK_JOB_GRADE (GRADE_ID → JOB_GRADES.GRADE_ID)

---

**Table: HRMS.EMPLOYEES**

| Column              | Data Type       | Constraints / Default                                                                     |
|---------------------|-----------------|-------------------------------------------------------------------------------------------|
| EMP_ID              | NUMBER(10)      | NOT NULL, PK                                                                              |
| EMP_NUMBER          | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_EMP_NUMBER)                                                          |
| FIRST_NAME          | VARCHAR2(50)    | NOT NULL                                                                                  |
| MIDDLE_NAME         | VARCHAR2(50)    | nullable                                                                                  |
| LAST_NAME           | VARCHAR2(50)    | NOT NULL                                                                                  |
| DATE_OF_BIRTH       | DATE            | nullable                                                                                  |
| GENDER              | CHAR(1)         | nullable, CHECK IN ('M','F','O')                                                          |
| MARITAL_STATUS      | VARCHAR2(10)    | nullable                                                                                  |
| NATIONALITY         | VARCHAR2(50)    | nullable                                                                                  |
| SSN_ENCRYPTED       | VARCHAR2(200)   | nullable; AES-256 encrypted SSN, decrypted only in PKG_SECURITY                          |
| EMAIL               | VARCHAR2(100)   | nullable                                                                                  |
| PHONE_WORK          | VARCHAR2(30)    | nullable                                                                                  |
| PHONE_MOBILE        | VARCHAR2(30)    | nullable                                                                                  |
| ADDRESS_LINE1       | VARCHAR2(200)   | nullable                                                                                  |
| ADDRESS_LINE2       | VARCHAR2(200)   | nullable                                                                                  |
| CITY                | VARCHAR2(100)   | nullable                                                                                  |
| STATE_PROVINCE      | VARCHAR2(100)   | nullable                                                                                  |
| POSTAL_CODE         | VARCHAR2(20)    | nullable                                                                                  |
| COUNTRY_CODE        | VARCHAR2(3)     | nullable                                                                                  |
| HIRE_DATE           | DATE            | NOT NULL                                                                                  |
| TERMINATION_DATE    | DATE            | nullable                                                                                  |
| TERMINATION_REASON  | VARCHAR2(50)    | nullable                                                                                  |
| DEPT_ID             | NUMBER(10)      | NOT NULL, FK → DEPARTMENTS(DEPT_ID)                                                      |
| JOB_ID              | NUMBER(10)      | NOT NULL, FK → JOB_TITLES(JOB_ID)                                                        |
| MANAGER_EMP_ID      | NUMBER(10)      | nullable, FK → EMPLOYEES(EMP_ID) (self-referencing)                                      |
| LOCATION_CODE       | VARCHAR2(10)    | nullable, FK → LOCATIONS(LOCATION_CODE)                                                   |
| EMPLOYMENT_TYPE     | VARCHAR2(20)    | DEFAULT 'FULL_TIME', CHECK IN ('FULL_TIME','PART_TIME','CONTRACT','INTERN')               |
| EMPLOYMENT_STATUS   | VARCHAR2(20)    | DEFAULT 'ACTIVE', CHECK IN ('ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED')                 |
| PHOTO_BLOB          | BLOB            | nullable                                                                                  |
| NOTES               | CLOB            | nullable                                                                                  |
| ACTIVE_FLAG         | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                     |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                                  |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                                 |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                                  |
| MODIFIED_DATE       | DATE            | nullable                                                                                  |

Constraints:
- PK_EMPLOYEES (EMP_ID)
- UK_EMP_NUMBER (EMP_NUMBER)
- FK_EMP_DEPT → DEPARTMENTS(DEPT_ID)
- FK_EMP_JOB → JOB_TITLES(JOB_ID)
- FK_EMP_MANAGER → EMPLOYEES(EMP_ID)
- FK_EMP_LOCATION → LOCATIONS(LOCATION_CODE)
- CHK_EMP_STATUS: EMPLOYMENT_STATUS IN ('ACTIVE','ON_LEAVE','SUSPENDED','TERMINATED')
- CHK_EMP_TYPE: EMPLOYMENT_TYPE IN ('FULL_TIME','PART_TIME','CONTRACT','INTERN')
- CHK_EMP_GENDER: GENDER IN ('M','F','O')

Table comment: 'Master employee records - core entity of the HRMS system'
Column comments:
- SSN_ENCRYPTED: 'AES-256 encrypted SSN - decrypted only in PKG_SECURITY'
- EMPLOYMENT_STATUS: 'Current status: ACTIVE, ON_LEAVE, SUSPENDED, TERMINATED'

---

**Table: HRMS.EMPLOYEE_HISTORY**

| Column           | Data Type       | Constraints / Default                                                                                |
|------------------|-----------------|------------------------------------------------------------------------------------------------------|
| HIST_ID          | NUMBER(15)      | NOT NULL, PK                                                                                         |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                     |
| CHANGE_TYPE      | VARCHAR2(30)    | NOT NULL, CHECK IN ('HIRE','TRANSFER','PROMOTION','DEMOTION','SALARY_CHANGE','TERMINATION','REHIRE','LEAVE_START','LEAVE_END','STATUS_CHANGE') |
| EFFECTIVE_DATE   | DATE            | NOT NULL                                                                                             |
| OLD_DEPT_ID      | NUMBER(10)      | nullable                                                                                             |
| NEW_DEPT_ID      | NUMBER(10)      | nullable                                                                                             |
| OLD_JOB_ID       | NUMBER(10)      | nullable                                                                                             |
| NEW_JOB_ID       | NUMBER(10)      | nullable                                                                                             |
| OLD_MANAGER_ID   | NUMBER(10)      | nullable                                                                                             |
| NEW_MANAGER_ID   | NUMBER(10)      | nullable                                                                                             |
| OLD_SALARY       | NUMBER(12,2)    | nullable                                                                                             |
| NEW_SALARY       | NUMBER(12,2)    | nullable                                                                                             |
| OLD_LOCATION     | VARCHAR2(10)    | nullable                                                                                             |
| NEW_LOCATION     | VARCHAR2(10)    | nullable                                                                                             |
| REASON_CODE      | VARCHAR2(30)    | nullable                                                                                             |
| COMMENTS         | VARCHAR2(4000)  | nullable                                                                                             |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                                                                             |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                                                                            |

Constraints:
- PK_EMP_HISTORY (HIST_ID)
- FK_HIST_EMP → EMPLOYEES(EMP_ID)
- CHK_CHANGE_TYPE: CHANGE_TYPE IN ('HIRE','TRANSFER','PROMOTION','DEMOTION','SALARY_CHANGE','TERMINATION','REHIRE','LEAVE_START','LEAVE_END','STATUS_CHANGE')

Note: The trigger TRG_EMP_BEFORE_UPDATE uses a column named CHANGE_DATE (not EFFECTIVE_DATE) and writes to OLD_VALUE/NEW_VALUE (VARCHAR2) — but the DDL here has EFFECTIVE_DATE and typed old/new columns. This is a discrepancy between the trigger and the DDL (the trigger appears to be inserting into a differently-structured version of the table or columns are aliases).

---

**Table: HRMS.EMPLOYEE_DEPENDENTS**

| Column           | Data Type       | Constraints / Default                                                       |
|------------------|-----------------|-----------------------------------------------------------------------------|
| DEPENDENT_ID     | NUMBER(10)      | NOT NULL, PK                                                                |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                            |
| FIRST_NAME       | VARCHAR2(50)    | NOT NULL                                                                    |
| LAST_NAME        | VARCHAR2(50)    | NOT NULL                                                                    |
| RELATIONSHIP     | VARCHAR2(20)    | NOT NULL, CHECK IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER')   |
| DATE_OF_BIRTH    | DATE            | nullable                                                                    |
| SSN_ENCRYPTED    | VARCHAR2(200)   | nullable                                                                    |
| BENEFITS_ENROLLED| CHAR(1)         | DEFAULT 'N'                                                                 |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                       |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                                                    |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                                                   |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                                                    |
| MODIFIED_DATE    | DATE            | nullable                                                                    |

Constraints: PK_EMP_DEPENDENTS (DEPENDENT_ID), FK_DEP_EMP → EMPLOYEES(EMP_ID), CHK_RELATIONSHIP (RELATIONSHIP IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER'))

---

**Table: HRMS.EMERGENCY_CONTACTS**

| Column           | Data Type       | Constraints / Default                    |
|------------------|-----------------|------------------------------------------|
| CONTACT_ID       | NUMBER(10)      | NOT NULL, PK                             |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)         |
| CONTACT_NAME     | VARCHAR2(100)   | NOT NULL                                 |
| RELATIONSHIP     | VARCHAR2(30)    | nullable                                 |
| PHONE_PRIMARY    | VARCHAR2(30)    | NOT NULL                                 |
| PHONE_SECONDARY  | VARCHAR2(30)    | nullable                                 |
| EMAIL            | VARCHAR2(100)   | nullable                                 |
| PRIORITY_ORDER   | NUMBER(2)       | DEFAULT 1                                |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                    |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                 |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                 |
| MODIFIED_DATE    | DATE            | nullable                                 |

Constraints: PK_EMERGENCY_CONTACTS (CONTACT_ID), FK_EC_EMP → EMPLOYEES(EMP_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/02_payroll_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.SALARY_RECORDS**

| Column           | Data Type       | Constraints / Default                                                            |
|------------------|-----------------|----------------------------------------------------------------------------------|
| SALARY_ID        | NUMBER(10)      | NOT NULL, PK                                                                     |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                 |
| EFFECTIVE_DATE   | DATE            | NOT NULL                                                                         |
| END_DATE         | DATE            | nullable                                                                         |
| BASE_SALARY      | NUMBER(12,2)    | NOT NULL                                                                         |
| CURRENCY_CODE    | VARCHAR2(3)     | DEFAULT 'USD'                                                                    |
| PAY_FREQUENCY    | VARCHAR2(20)    | DEFAULT 'MONTHLY', CHECK IN ('WEEKLY','BIWEEKLY','SEMIMONTHLY','MONTHLY')        |
| SALARY_BASIS     | VARCHAR2(20)    | DEFAULT 'ANNUAL', CHECK IN ('ANNUAL','HOURLY')                                   |
| CHANGE_REASON    | VARCHAR2(50)    | nullable                                                                         |
| CHANGE_PCT       | NUMBER(5,2)     | nullable                                                                         |
| APPROVED_BY      | NUMBER(10)      | nullable                                                                         |
| APPROVAL_DATE    | DATE            | nullable                                                                         |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                            |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                                                         |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                                                        |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                                                         |
| MODIFIED_DATE    | DATE            | nullable                                                                         |

Constraints: PK_SALARY_RECORDS (SALARY_ID), FK_SAL_EMP → EMPLOYEES(EMP_ID), CHK_PAY_FREQ, CHK_SAL_BASIS

---

**Table: HRMS.PAY_ELEMENTS**

| Column             | Data Type       | Constraints / Default                                                                     |
|--------------------|-----------------|-------------------------------------------------------------------------------------------|
| ELEMENT_ID         | NUMBER(10)      | NOT NULL, PK                                                                              |
| ELEMENT_CODE       | VARCHAR2(30)    | NOT NULL, UNIQUE (UK_PAY_ELEM_CODE)                                                       |
| ELEMENT_NAME       | VARCHAR2(100)   | NOT NULL                                                                                  |
| ELEMENT_TYPE       | VARCHAR2(20)    | NOT NULL, CHECK IN ('EARNING','DEDUCTION','TAX','BENEFIT','REIMBURSEMENT')                |
| CALCULATION_TYPE   | VARCHAR2(20)    | NOT NULL, CHECK IN ('FLAT','PERCENTAGE','HOURS','FORMULA')                                |
| DEFAULT_AMOUNT     | NUMBER(12,2)    | nullable                                                                                  |
| DEFAULT_PERCENTAGE | NUMBER(5,2)     | nullable                                                                                  |
| TAXABLE_FLAG       | CHAR(1)         | DEFAULT 'Y'                                                                               |
| PRETAX_FLAG        | CHAR(1)         | DEFAULT 'N'                                                                               |
| EMPLOYER_PAID      | CHAR(1)         | DEFAULT 'N'                                                                               |
| GL_ACCOUNT_CODE    | VARCHAR2(30)    | nullable                                                                                  |
| PRIORITY_ORDER     | NUMBER(5)       | DEFAULT 100                                                                               |
| ACTIVE_FLAG        | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                     |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                                                  |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                                                 |
| MODIFIED_BY        | VARCHAR2(30)    | nullable                                                                                  |
| MODIFIED_DATE      | DATE            | nullable                                                                                  |

Constraints: PK_PAY_ELEMENTS (ELEMENT_ID), UK_PAY_ELEM_CODE (ELEMENT_CODE), CHK_ELEM_TYPE, CHK_CALC_TYPE

---

**Table: HRMS.EMPLOYEE_PAY_ELEMENTS**

| Column           | Data Type       | Constraints / Default                    |
|------------------|-----------------|------------------------------------------|
| EMP_ELEMENT_ID   | NUMBER(10)      | NOT NULL, PK                             |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)         |
| ELEMENT_ID       | NUMBER(10)      | NOT NULL, FK → PAY_ELEMENTS(ELEMENT_ID)  |
| EFFECTIVE_DATE   | DATE            | NOT NULL                                 |
| END_DATE         | DATE            | nullable                                 |
| AMOUNT           | NUMBER(12,2)    | nullable                                 |
| PERCENTAGE       | NUMBER(5,2)     | nullable                                 |
| OVERRIDE_AMOUNT  | NUMBER(12,2)    | nullable                                 |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                    |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                 |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                |
| MODIFIED_BY      | VARCHAR2(30)    | nullable                                 |
| MODIFIED_DATE    | DATE            | nullable                                 |

Constraints: PK_EMP_PAY_ELEMENTS (EMP_ELEMENT_ID), FK_EPE_EMP → EMPLOYEES(EMP_ID), FK_EPE_ELEMENT → PAY_ELEMENTS(ELEMENT_ID)

---

**Table: HRMS.PAY_PERIODS**

| Column             | Data Type       | Constraints / Default                                              |
|--------------------|-----------------|---------------------------------------------------------------------|
| PERIOD_ID          | NUMBER(10)      | NOT NULL, PK                                                        |
| PERIOD_NAME        | VARCHAR2(50)    | NOT NULL                                                            |
| PAY_FREQUENCY      | VARCHAR2(20)    | NOT NULL                                                            |
| PERIOD_START_DATE  | DATE            | NOT NULL                                                            |
| PERIOD_END_DATE    | DATE            | NOT NULL                                                            |
| PAY_DATE           | DATE            | NOT NULL                                                            |
| STATUS             | VARCHAR2(20)    | DEFAULT 'OPEN', CHECK IN ('OPEN','PROCESSING','CLOSED','REVERSED') |
| CLOSED_BY          | VARCHAR2(30)    | nullable                                                            |
| CLOSED_DATE        | DATE            | nullable                                                            |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                            |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                           |
| MODIFIED_BY        | VARCHAR2(30)    | nullable                                                            |
| MODIFIED_DATE      | DATE            | nullable                                                            |

Constraints: PK_PAY_PERIODS (PERIOD_ID), CHK_PERIOD_STATUS

---

**Table: HRMS.PAYROLL_RUNS**

| Column              | Data Type       | Constraints / Default                                                              |
|---------------------|-----------------|------------------------------------------------------------------------------------|
| RUN_ID              | NUMBER(10)      | NOT NULL, PK                                                                       |
| PERIOD_ID           | NUMBER(10)      | NOT NULL, FK → PAY_PERIODS(PERIOD_ID)                                              |
| RUN_TYPE            | VARCHAR2(20)    | DEFAULT 'REGULAR', CHECK IN ('REGULAR','SUPPLEMENTAL','BONUS','FINAL')             |
| RUN_DATE            | DATE            | NOT NULL                                                                           |
| STATUS              | VARCHAR2(20)    | DEFAULT 'PENDING', CHECK IN ('PENDING','CALCULATING','CALCULATED','APPROVED','PAID','REVERSED','ERROR') |
| TOTAL_GROSS         | NUMBER(15,2)    | nullable                                                                           |
| TOTAL_DEDUCTIONS    | NUMBER(15,2)    | nullable                                                                           |
| TOTAL_NET           | NUMBER(15,2)    | nullable                                                                           |
| TOTAL_EMPLOYER_COST | NUMBER(15,2)    | nullable                                                                           |
| EMPLOYEE_COUNT      | NUMBER(10)      | nullable                                                                           |
| ERROR_COUNT         | NUMBER(10)      | DEFAULT 0                                                                          |
| SUBMITTED_BY        | VARCHAR2(30)    | nullable                                                                           |
| SUBMITTED_DATE      | DATE            | nullable                                                                           |
| APPROVED_BY         | VARCHAR2(30)    | nullable                                                                           |
| APPROVED_DATE       | DATE            | nullable                                                                           |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                           |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                          |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                           |
| MODIFIED_DATE       | DATE            | nullable                                                                           |

Constraints: PK_PAYROLL_RUNS (RUN_ID), FK_PR_PERIOD → PAY_PERIODS(PERIOD_ID), CHK_RUN_TYPE, CHK_RUN_STATUS

---

**Table: HRMS.PAYROLL_DETAILS**

| Column           | Data Type       | Constraints / Default                        |
|------------------|-----------------|----------------------------------------------|
| DETAIL_ID        | NUMBER(15)      | NOT NULL, PK                                 |
| RUN_ID           | NUMBER(10)      | NOT NULL, FK → PAYROLL_RUNS(RUN_ID)          |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)             |
| ELEMENT_ID       | NUMBER(10)      | NOT NULL, FK → PAY_ELEMENTS(ELEMENT_ID)      |
| ELEMENT_TYPE     | VARCHAR2(20)    | NOT NULL                                     |
| HOURS_WORKED     | NUMBER(6,2)     | nullable                                     |
| RATE             | NUMBER(12,4)    | nullable                                     |
| AMOUNT           | NUMBER(12,2)    | NOT NULL                                     |
| YTD_AMOUNT       | NUMBER(15,2)    | nullable                                     |
| STATUS           | VARCHAR2(20)    | DEFAULT 'CALCULATED'                         |
| ERROR_MESSAGE    | VARCHAR2(4000)  | nullable                                     |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                     |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                    |

Constraints: PK_PAYROLL_DETAILS (DETAIL_ID), FK_PD_RUN → PAYROLL_RUNS(RUN_ID), FK_PD_EMP → EMPLOYEES(EMP_ID), FK_PD_ELEMENT → PAY_ELEMENTS(ELEMENT_ID)

---

**Table: HRMS.TAX_BRACKETS**

| Column         | Data Type       | Constraints / Default                                                                    |
|----------------|-----------------|------------------------------------------------------------------------------------------|
| BRACKET_ID     | NUMBER(10)      | NOT NULL, PK                                                                             |
| TAX_YEAR       | NUMBER(4)       | NOT NULL                                                                                 |
| FILING_STATUS  | VARCHAR2(30)    | NOT NULL, CHECK IN ('SINGLE','MARRIED_JOINT','MARRIED_SEPARATE','HEAD_OF_HOUSEHOLD')     |
| BRACKET_MIN    | NUMBER(12,2)    | NOT NULL                                                                                 |
| BRACKET_MAX    | NUMBER(12,2)    | nullable (NULL = no upper bound, i.e., top bracket)                                      |
| TAX_RATE       | NUMBER(5,4)     | NOT NULL                                                                                 |
| BASE_TAX       | NUMBER(12,2)    | DEFAULT 0                                                                                |
| STATE_CODE     | VARCHAR2(3)     | nullable (NULL = federal)                                                                |
| ACTIVE_FLAG    | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                    |
| CREATED_BY     | VARCHAR2(30)    | NOT NULL                                                                                 |
| CREATED_DATE   | DATE            | NOT NULL, DEFAULT SYSDATE                                                                |

Constraints: PK_TAX_BRACKETS (BRACKET_ID), CHK_FILING_STATUS

Note: TAX_RATE is NUMBER(5,4) — stores rates as decimal fractions (e.g., 0.2200 for 22%). BASE_TAX stores the cumulative tax already owed at the start of this bracket. Actual bracket data is populated via data/seed scripts (not present in this file).

---

**Table: HRMS.EMPLOYEE_TAX_INFO**

| Column               | Data Type       | Constraints / Default                                                                    |
|----------------------|-----------------|------------------------------------------------------------------------------------------|
| TAX_INFO_ID          | NUMBER(10)      | NOT NULL, PK                                                                             |
| EMP_ID               | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                         |
| TAX_YEAR             | NUMBER(4)       | NOT NULL                                                                                 |
| FILING_STATUS        | VARCHAR2(30)    | NOT NULL                                                                                 |
| FEDERAL_ALLOWANCES   | NUMBER(3)       | DEFAULT 0                                                                                |
| STATE_ALLOWANCES     | NUMBER(3)       | DEFAULT 0                                                                                |
| ADDITIONAL_FED_WH    | NUMBER(12,2)    | DEFAULT 0                                                                                |
| ADDITIONAL_STATE_WH  | NUMBER(12,2)    | DEFAULT 0                                                                                |
| EXEMPT_FLAG          | CHAR(1)         | DEFAULT 'N'                                                                              |
| STATE_CODE           | VARCHAR2(3)     | nullable                                                                                 |
| W4_RECEIVED_DATE     | DATE            | nullable                                                                                 |
| ACTIVE_FLAG          | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                                    |
| CREATED_BY           | VARCHAR2(30)    | NOT NULL                                                                                 |
| CREATED_DATE         | DATE            | NOT NULL, DEFAULT SYSDATE                                                                |
| MODIFIED_BY          | VARCHAR2(30)    | nullable                                                                                 |
| MODIFIED_DATE        | DATE            | nullable                                                                                 |

Constraints: PK_EMP_TAX_INFO (TAX_INFO_ID), FK_ETI_EMP → EMPLOYEES(EMP_ID), UK_EMP_TAX_YEAR (EMP_ID, TAX_YEAR) — one tax info record per employee per year.

---

**Table: HRMS.EMPLOYEE_BANK_ACCOUNTS**

| Column              | Data Type       | Constraints / Default                                                           |
|---------------------|-----------------|---------------------------------------------------------------------------------|
| BANK_ACCT_ID        | NUMBER(10)      | NOT NULL, PK                                                                    |
| EMP_ID              | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                |
| BANK_NAME           | VARCHAR2(100)   | nullable                                                                        |
| ROUTING_NUMBER      | VARCHAR2(20)    | NOT NULL                                                                        |
| ACCOUNT_NUMBER_ENC  | VARCHAR2(200)   | NOT NULL (encrypted)                                                            |
| ACCOUNT_TYPE        | VARCHAR2(20)    | DEFAULT 'CHECKING', CHECK IN ('CHECKING','SAVINGS')                             |
| DEPOSIT_TYPE        | VARCHAR2(20)    | DEFAULT 'FULL', CHECK IN ('FULL','PARTIAL_AMOUNT','PARTIAL_PERCENT','REMAINDER')|
| DEPOSIT_AMOUNT      | NUMBER(12,2)    | nullable                                                                        |
| DEPOSIT_PERCENTAGE  | NUMBER(5,2)     | nullable                                                                        |
| PRIORITY_ORDER      | NUMBER(2)       | DEFAULT 1                                                                       |
| PRENOTE_SENT        | CHAR(1)         | DEFAULT 'N'                                                                     |
| PRENOTE_DATE        | DATE            | nullable                                                                        |
| ACTIVE_FLAG         | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                           |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                        |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                       |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                        |
| MODIFIED_DATE       | DATE            | nullable                                                                        |

Constraints: PK_EMP_BANK_ACCTS (BANK_ACCT_ID), FK_BA_EMP → EMPLOYEES(EMP_ID), CHK_ACCT_TYPE, CHK_DEPOSIT_TYPE

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/03_leave_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.LEAVE_TYPES**

| Column             | Data Type       | Constraints / Default                                                  |
|--------------------|-----------------|------------------------------------------------------------------------|
| LEAVE_TYPE_ID      | NUMBER(5)       | NOT NULL, PK                                                           |
| LEAVE_TYPE_CODE    | VARCHAR2(20)    | NOT NULL, UNIQUE (UK_LEAVE_TYPE_CODE)                                  |
| LEAVE_TYPE_NAME    | VARCHAR2(50)    | NOT NULL                                                               |
| PAID_FLAG          | CHAR(1)         | DEFAULT 'Y'                                                            |
| ACCRUAL_FLAG       | CHAR(1)         | DEFAULT 'Y'                                                            |
| ACCRUAL_RATE       | NUMBER(6,2)     | nullable                                                               |
| ACCRUAL_FREQUENCY  | VARCHAR2(20)    | nullable, CHECK IN ('MONTHLY','BIWEEKLY','ANNUAL', NULL)               |
| MAX_BALANCE        | NUMBER(6,2)     | nullable                                                               |
| CARRYOVER_MAX      | NUMBER(6,2)     | nullable                                                               |
| CARRYOVER_EXPIRY   | NUMBER(3)       | nullable (number of days before carryover expires)                     |
| MIN_TENURE_DAYS    | NUMBER(5)       | DEFAULT 0                                                              |
| REQUIRES_APPROVAL  | CHAR(1)         | DEFAULT 'Y'                                                            |
| REQUIRES_DOCUMENT  | CHAR(1)         | DEFAULT 'N'                                                            |
| ACTIVE_FLAG        | CHAR(1)         | NOT NULL, DEFAULT 'Y'                                                  |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                               |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                              |
| MODIFIED_BY        | VARCHAR2(30)    | nullable                                                               |
| MODIFIED_DATE      | DATE            | nullable                                                               |

Constraints: PK_LEAVE_TYPES (LEAVE_TYPE_ID), UK_LEAVE_TYPE_CODE (LEAVE_TYPE_CODE), CHK_ACCRUAL_FREQ

Business Rules embedded:
- MIN_TENURE_DAYS: employee must have been employed at least this many days to use this leave type.
- CARRYOVER_EXPIRY: number of days after which carried-over leave expires.
- MAX_BALANCE: cap on accrued leave balance.
- CARRYOVER_MAX: maximum days allowed to carry over to next year.

---

**Table: HRMS.LEAVE_BALANCES**

| Column              | Data Type       | Constraints / Default                                                        |
|---------------------|-----------------|------------------------------------------------------------------------------|
| BALANCE_ID          | NUMBER(10)      | NOT NULL, PK                                                                 |
| EMP_ID              | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                             |
| LEAVE_TYPE_ID       | NUMBER(5)       | NOT NULL, FK → LEAVE_TYPES(LEAVE_TYPE_ID)                                    |
| CALENDAR_YEAR       | NUMBER(4)       | NOT NULL                                                                     |
| OPENING_BALANCE     | NUMBER(6,2)     | DEFAULT 0                                                                    |
| ACCRUED             | NUMBER(6,2)     | DEFAULT 0                                                                    |
| USED                | NUMBER(6,2)     | DEFAULT 0                                                                    |
| ADJUSTMENT          | NUMBER(6,2)     | DEFAULT 0                                                                    |
| PENDING             | NUMBER(6,2)     | DEFAULT 0                                                                    |
| AVAILABLE           | NUMBER(6,2)     | VIRTUAL: GENERATED ALWAYS AS (OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING) |
| CARRYOVER_FROM_PREV | NUMBER(6,2)     | DEFAULT 0                                                                    |
| CARRYOVER_EXPIRY_DT | DATE            | nullable                                                                     |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                                     |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                                    |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                                     |
| MODIFIED_DATE       | DATE            | nullable                                                                     |

Constraints: PK_LEAVE_BALANCES (BALANCE_ID), FK_LB_EMP → EMPLOYEES(EMP_ID), FK_LB_TYPE → LEAVE_TYPES(LEAVE_TYPE_ID), UK_LEAVE_BAL (EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR)

Business Rule (virtual column formula): AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING

---

**Table: HRMS.LEAVE_REQUESTS**

| Column               | Data Type       | Constraints / Default                                                       |
|----------------------|-----------------|-----------------------------------------------------------------------------|
| REQUEST_ID           | NUMBER(10)      | NOT NULL, PK                                                                |
| EMP_ID               | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                            |
| LEAVE_TYPE_ID        | NUMBER(5)       | NOT NULL, FK → LEAVE_TYPES(LEAVE_TYPE_ID)                                   |
| START_DATE           | DATE            | NOT NULL                                                                    |
| END_DATE             | DATE            | NOT NULL                                                                    |
| TOTAL_DAYS           | NUMBER(5,1)     | NOT NULL                                                                    |
| HALF_DAY_FLAG        | CHAR(1)         | DEFAULT 'N'                                                                 |
| HALF_DAY_PERIOD      | VARCHAR2(10)    | nullable, CHECK IN ('AM','PM', NULL)                                        |
| STATUS               | VARCHAR2(20)    | DEFAULT 'PENDING', CHECK IN ('PENDING','APPROVED','REJECTED','CANCELLED','TAKEN') |
| REASON               | VARCHAR2(4000)  | nullable                                                                    |
| SUPPORTING_DOC_PATH  | VARCHAR2(500)   | nullable                                                                    |
| APPROVER_EMP_ID      | NUMBER(10)      | nullable, FK → EMPLOYEES(EMP_ID)                                            |
| APPROVAL_DATE        | DATE            | nullable                                                                    |
| APPROVAL_COMMENTS    | VARCHAR2(4000)  | nullable                                                                    |
| CANCEL_REASON        | VARCHAR2(4000)  | nullable                                                                    |
| CANCELLED_DATE       | DATE            | nullable                                                                    |
| CREATED_BY           | VARCHAR2(30)    | NOT NULL                                                                    |
| CREATED_DATE         | DATE            | NOT NULL, DEFAULT SYSDATE                                                   |
| MODIFIED_BY          | VARCHAR2(30)    | nullable                                                                    |
| MODIFIED_DATE        | DATE            | nullable                                                                    |

Constraints: PK_LEAVE_REQUESTS (REQUEST_ID), FK_LR_EMP → EMPLOYEES(EMP_ID), FK_LR_TYPE → LEAVE_TYPES(LEAVE_TYPE_ID), FK_LR_APPROVER → EMPLOYEES(EMP_ID), CHK_LR_STATUS, CHK_LR_DATES (END_DATE >= START_DATE), CHK_HALF_DAY (HALF_DAY_PERIOD IN ('AM','PM', NULL))

Business Rules:
- END_DATE must be >= START_DATE (CHK_LR_DATES).
- Half-day leave must specify 'AM' or 'PM' period.
- Valid status lifecycle: PENDING → APPROVED / REJECTED / CANCELLED → TAKEN.

---

**Table: HRMS.LEAVE_ACCRUAL_LOG**

| Column           | Data Type       | Constraints / Default                            |
|------------------|-----------------|--------------------------------------------------|
| ACCRUAL_ID       | NUMBER(15)      | NOT NULL, PK                                     |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                 |
| LEAVE_TYPE_ID    | NUMBER(5)       | NOT NULL, FK → LEAVE_TYPES(LEAVE_TYPE_ID)        |
| ACCRUAL_DATE     | DATE            | NOT NULL                                         |
| ACCRUAL_AMOUNT   | NUMBER(6,2)     | NOT NULL                                         |
| BALANCE_AFTER    | NUMBER(6,2)     | nullable                                         |
| RUN_ID           | NUMBER(10)      | nullable (references a batch run, not FK defined)|
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                         |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                        |

Constraints: PK_LEAVE_ACCRUAL_LOG (ACCRUAL_ID), FK_LAL_EMP → EMPLOYEES(EMP_ID), FK_LAL_TYPE → LEAVE_TYPES(LEAVE_TYPE_ID)

---

**Table: HRMS.HOLIDAYS**

| Column           | Data Type       | Constraints / Default        |
|------------------|-----------------|------------------------------|
| HOLIDAY_ID       | NUMBER(5)       | NOT NULL, PK                 |
| HOLIDAY_DATE     | DATE            | NOT NULL                     |
| HOLIDAY_NAME     | VARCHAR2(100)   | NOT NULL                     |
| LOCATION_CODE    | VARCHAR2(10)    | nullable (NULL = global)     |
| FLOATING_FLAG    | CHAR(1)         | DEFAULT 'N'                  |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'        |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                     |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE    |

Constraints: PK_HOLIDAYS (HOLIDAY_ID)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/tables/04_performance_tables.sql ===

**Schema:** HRMS
**Database:** Oracle 19c

---

**Table: HRMS.REVIEW_CYCLES**

| Column              | Data Type       | Constraints / Default                                                  |
|---------------------|-----------------|------------------------------------------------------------------------|
| CYCLE_ID            | NUMBER(10)      | NOT NULL, PK                                                           |
| CYCLE_NAME          | VARCHAR2(100)   | NOT NULL                                                               |
| CYCLE_YEAR          | NUMBER(4)       | NOT NULL                                                               |
| START_DATE          | DATE            | NOT NULL                                                               |
| END_DATE            | DATE            | NOT NULL                                                               |
| SELF_REVIEW_DUE     | DATE            | nullable                                                               |
| MANAGER_REVIEW_DUE  | DATE            | nullable                                                               |
| CALIBRATION_DUE     | DATE            | nullable                                                               |
| STATUS              | VARCHAR2(20)    | DEFAULT 'DRAFT', CHECK IN ('DRAFT','OPEN','IN_PROGRESS','CALIBRATION','CLOSED') |
| CREATED_BY          | VARCHAR2(30)    | NOT NULL                                                               |
| CREATED_DATE        | DATE            | NOT NULL, DEFAULT SYSDATE                                              |
| MODIFIED_BY         | VARCHAR2(30)    | nullable                                                               |
| MODIFIED_DATE       | DATE            | nullable                                                               |

Constraints: PK_REVIEW_CYCLES (CYCLE_ID), CHK_CYCLE_STATUS

---

**Table: HRMS.PERFORMANCE_REVIEWS**

| Column                 | Data Type       | Constraints / Default                                                                                 |
|------------------------|-----------------|-------------------------------------------------------------------------------------------------------|
| REVIEW_ID              | NUMBER(10)      | NOT NULL, PK                                                                                          |
| CYCLE_ID               | NUMBER(10)      | NOT NULL, FK → REVIEW_CYCLES(CYCLE_ID)                                                                |
| EMP_ID                 | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                      |
| REVIEWER_EMP_ID        | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                      |
| REVIEW_TYPE            | VARCHAR2(20)    | DEFAULT 'ANNUAL'                                                                                      |
| STATUS                 | VARCHAR2(20)    | DEFAULT 'NOT_STARTED', CHECK IN ('NOT_STARTED','SELF_REVIEW','MANAGER_REVIEW','MEETING_SCHEDULED','COMPLETED','ACKNOWLEDGED') |
| OVERALL_RATING         | NUMBER(2,1)     | nullable, CHECK BETWEEN 1.0 AND 5.0                                                                   |
| RATING_LABEL           | VARCHAR2(50)    | nullable                                                                                              |
| SELF_ASSESSMENT        | CLOB            | nullable                                                                                              |
| MANAGER_ASSESSMENT     | CLOB            | nullable                                                                                              |
| STRENGTHS              | CLOB            | nullable                                                                                              |
| AREAS_FOR_IMPROVEMENT  | CLOB            | nullable                                                                                              |
| DEVELOPMENT_PLAN       | CLOB            | nullable                                                                                              |
| EMPLOYEE_COMMENTS      | CLOB            | nullable                                                                                              |
| EMPLOYEE_ACK_DATE      | DATE            | nullable                                                                                              |
| CALIBRATED_RATING      | NUMBER(2,1)     | nullable                                                                                              |
| CALIBRATION_NOTES      | VARCHAR2(4000)  | nullable                                                                                              |
| CREATED_BY             | VARCHAR2(30)    | NOT NULL                                                                                              |
| CREATED_DATE           | DATE            | NOT NULL, DEFAULT SYSDATE                                                                             |
| MODIFIED_BY            | VARCHAR2(30)    | nullable                                                                                              |
| MODIFIED_DATE          | DATE            | nullable                                                                                              |

Constraints: PK_PERFORMANCE_REVIEWS (REVIEW_ID), FK_PR_CYCLE → REVIEW_CYCLES(CYCLE_ID), FK_PR_EMP → EMPLOYEES(EMP_ID), FK_PR_REVIEWER → EMPLOYEES(EMP_ID), CHK_REVIEW_STATUS, CHK_RATING_RANGE (OVERALL_RATING BETWEEN 1.0 AND 5.0)

Business Rule: Rating must be between 1.0 and 5.0 inclusive.

---

**Table: HRMS.PERFORMANCE_GOALS**

| Column            | Data Type       | Constraints / Default                                                                               |
|-------------------|-----------------|-----------------------------------------------------------------------------------------------------|
| GOAL_ID           | NUMBER(10)      | NOT NULL, PK                                                                                        |
| REVIEW_ID         | NUMBER(10)      | NOT NULL, FK → PERFORMANCE_REVIEWS(REVIEW_ID)                                                       |
| EMP_ID            | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)                                                                    |
| GOAL_TITLE        | VARCHAR2(200)   | NOT NULL                                                                                            |
| GOAL_DESCRIPTION  | CLOB            | nullable                                                                                            |
| GOAL_CATEGORY     | VARCHAR2(30)    | nullable, CHECK IN ('BUSINESS','DEVELOPMENT','LEADERSHIP','INNOVATION','COMPLIANCE')                |
| WEIGHT_PCT        | NUMBER(5,2)     | DEFAULT 0                                                                                           |
| TARGET_DATE       | DATE            | nullable                                                                                            |
| STATUS            | VARCHAR2(20)    | DEFAULT 'NOT_STARTED', CHECK IN ('NOT_STARTED','IN_PROGRESS','COMPLETED','DEFERRED','CANCELLED')    |
| PROGRESS_PCT      | NUMBER(5,2)     | DEFAULT 0                                                                                           |
| SELF_RATING       | NUMBER(2,1)     | nullable                                                                                            |
| MANAGER_RATING    | NUMBER(2,1)     | nullable                                                                                            |
| COMMENTS          | CLOB            | nullable                                                                                            |
| CREATED_BY        | VARCHAR2(30)    | NOT NULL                                                                                            |
| CREATED_DATE      | DATE            | NOT NULL, DEFAULT SYSDATE                                                                           |
| MODIFIED_BY       | VARCHAR2(30)    | nullable                                                                                            |
| MODIFIED_DATE     | DATE            | nullable                                                                                            |

Constraints: PK_PERF_GOALS (GOAL_ID), FK_PG_REVIEW → PERFORMANCE_REVIEWS(REVIEW_ID), FK_PG_EMP → EMPLOYEES(EMP_ID), CHK_GOAL_STATUS, CHK_GOAL_CATEGORY

---

**Table: HRMS.AUDIT_LOG**

| Column         | Data Type       | Constraints / Default                             |
|----------------|-----------------|---------------------------------------------------|
| AUDIT_ID       | NUMBER(15)      | NOT NULL, PK                                      |
| TABLE_NAME     | VARCHAR2(60)    | NOT NULL                                          |
| RECORD_ID      | NUMBER(15)      | NOT NULL                                          |
| ACTION_TYPE    | VARCHAR2(10)    | NOT NULL, CHECK IN ('INSERT','UPDATE','DELETE')   |
| OLD_VALUES     | CLOB            | nullable                                          |
| NEW_VALUES     | CLOB            | nullable                                          |
| CHANGED_BY     | VARCHAR2(30)    | NOT NULL                                          |
| CHANGED_DATE   | DATE            | NOT NULL, DEFAULT SYSDATE                         |
| IP_ADDRESS     | VARCHAR2(50)    | nullable                                          |
| SESSION_ID     | VARCHAR2(100)   | nullable                                          |

Constraints: PK_AUDIT_LOG (AUDIT_ID), CHK_AUDIT_ACTION

---

**Table: HRMS.SYSTEM_PARAMETERS**

| Column            | Data Type       | Constraints / Default                            |
|-------------------|-----------------|--------------------------------------------------|
| PARAM_ID          | NUMBER(5)       | NOT NULL, PK                                     |
| PARAM_GROUP       | VARCHAR2(50)    | NOT NULL                                         |
| PARAM_CODE        | VARCHAR2(50)    | NOT NULL                                         |
| PARAM_VALUE       | VARCHAR2(4000)  | NOT NULL                                         |
| PARAM_DESCRIPTION | VARCHAR2(200)   | nullable                                         |
| DATA_TYPE         | VARCHAR2(20)    | DEFAULT 'VARCHAR2'                               |
| EDITABLE_FLAG     | CHAR(1)         | DEFAULT 'Y'                                      |
| CREATED_BY        | VARCHAR2(30)    | NOT NULL                                         |
| CREATED_DATE      | DATE            | NOT NULL, DEFAULT SYSDATE                        |
| MODIFIED_BY       | VARCHAR2(30)    | nullable                                         |
| MODIFIED_DATE     | DATE            | nullable                                         |

Constraints: PK_SYSTEM_PARAMS (PARAM_ID), UK_PARAM_CODE (PARAM_GROUP, PARAM_CODE)

---

**Table: HRMS.NOTIFICATION_QUEUE**

| Column             | Data Type       | Constraints / Default                                          |
|--------------------|-----------------|----------------------------------------------------------------|
| NOTIFICATION_ID    | NUMBER(15)      | NOT NULL, PK                                                   |
| RECIPIENT_EMP_ID   | NUMBER(10)      | nullable                                                       |
| RECIPIENT_EMAIL    | VARCHAR2(100)   | nullable                                                       |
| NOTIFICATION_TYPE  | VARCHAR2(30)    | NOT NULL, CHECK IN ('EMAIL','IN_APP','SMS')                    |
| SUBJECT            | VARCHAR2(200)   | NOT NULL                                                       |
| BODY               | CLOB            | NOT NULL                                                       |
| STATUS             | VARCHAR2(20)    | DEFAULT 'PENDING', CHECK IN ('PENDING','SENT','FAILED','CANCELLED') |
| PRIORITY           | NUMBER(2)       | DEFAULT 5                                                      |
| SENT_DATE          | DATE            | nullable                                                       |
| ERROR_MESSAGE      | VARCHAR2(4000)  | nullable                                                       |
| RETRY_COUNT        | NUMBER(3)       | DEFAULT 0                                                      |
| REFERENCE_TABLE    | VARCHAR2(60)    | nullable                                                       |
| REFERENCE_ID       | NUMBER(15)      | nullable                                                       |
| CREATED_BY         | VARCHAR2(30)    | NOT NULL                                                       |
| CREATED_DATE       | DATE            | NOT NULL, DEFAULT SYSDATE                                      |

Constraints: PK_NOTIF_QUEUE (NOTIFICATION_ID), CHK_NOTIF_STATUS, CHK_NOTIF_TYPE

---

**Table: HRMS.USER_SESSIONS**

| Column           | Data Type       | Constraints / Default                    |
|------------------|-----------------|------------------------------------------|
| SESSION_ID       | NUMBER(15)      | NOT NULL, PK                             |
| EMP_ID           | NUMBER(10)      | NOT NULL, FK → EMPLOYEES(EMP_ID)         |
| USERNAME         | VARCHAR2(30)    | NOT NULL                                 |
| LOGIN_TIME       | DATE            | NOT NULL                                 |
| LOGOUT_TIME      | DATE            | nullable                                 |
| IP_ADDRESS       | VARCHAR2(50)    | nullable                                 |
| FORMS_MODULE     | VARCHAR2(100)   | nullable                                 |
| SESSION_STATUS   | VARCHAR2(20)    | DEFAULT 'ACTIVE'                         |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                |

Constraints: PK_USER_SESSIONS (SESSION_ID), FK_US_EMP → EMPLOYEES(EMP_ID)

---

**Table: HRMS.LOOKUP_VALUES**

| Column           | Data Type       | Constraints / Default                          |
|------------------|-----------------|------------------------------------------------|
| LOOKUP_ID        | NUMBER(10)      | NOT NULL, PK                                   |
| LOOKUP_TYPE      | VARCHAR2(50)    | NOT NULL                                       |
| LOOKUP_CODE      | VARCHAR2(50)    | NOT NULL                                       |
| LOOKUP_VALUE     | VARCHAR2(200)   | NOT NULL                                       |
| DISPLAY_ORDER    | NUMBER(5)       | DEFAULT 0                                      |
| PARENT_LOOKUP_ID | NUMBER(10)      | nullable                                       |
| ACTIVE_FLAG      | CHAR(1)         | NOT NULL, DEFAULT 'Y'                          |
| CREATED_BY       | VARCHAR2(30)    | NOT NULL                                       |
| CREATED_DATE     | DATE            | NOT NULL, DEFAULT SYSDATE                      |

Constraints: PK_LOOKUP_VALUES (LOOKUP_ID), UK_LOOKUP (LOOKUP_TYPE, LOOKUP_CODE)

---

=== FILE: ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/schema/views/hrms_views.sql ===

**Schema:** HRMS
**Used by:** Oracle Reports (.rdf), Forms LOVs, external reporting tools

---

**View: HRMS.VW_ACTIVE_EMPLOYEES**

Purpose: Denormalized view of active employees with department, job, manager, location, and current salary.

Columns returned:
- e.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME, e.LAST_NAME
- e.FIRST_NAME || ' ' || e.LAST_NAME AS FULL_NAME
- e.EMAIL, e.PHONE_WORK, e.PHONE_MOBILE
- e.HIRE_DATE
- TRUNC(MONTHS_BETWEEN(SYSDATE, e.HIRE_DATE) / 12, 1) AS TENURE_YEARS
- e.EMPLOYMENT_TYPE, e.EMPLOYMENT_STATUS
- e.DEPT_ID, d.DEPT_NAME, d.DEPT_CODE, d.COST_CENTER
- e.JOB_ID, j.JOB_TITLE, j.JOB_CODE
- g.GRADE_ID, g.GRADE_NAME
- e.MANAGER_EMP_ID
- m.FIRST_NAME || ' ' || m.LAST_NAME AS MANAGER_NAME
- e.LOCATION_CODE
- l.LOCATION_NAME, l.CITY, l.STATE_PROVINCE, l.COUNTRY_CODE
- sr.BASE_SALARY AS CURRENT_SALARY
- sr.CURRENCY_CODE, sr.PAY_FREQUENCY

Joins:
- EMPLOYEES e (base)
- JOIN DEPARTMENTS d ON e.DEPT_ID = d.DEPT_ID
- JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID
- JOIN JOB_GRADES g ON j.GRADE_ID = g.GRADE_ID
- LEFT JOIN EMPLOYEES m ON e.MANAGER_EMP_ID = m.EMP_ID
- LEFT JOIN LOCATIONS l ON e.LOCATION_CODE = l.LOCATION_CODE
- LEFT JOIN SALARY_RECORDS sr ON e.EMP_ID = sr.EMP_ID AND sr.ACTIVE_FLAG = 'Y' AND sr.EFFECTIVE_DATE <= SYSDATE AND (sr.END_DATE IS NULL OR sr.END_DATE > SYSDATE)

WHERE: e.EMPLOYMENT_STATUS = 'ACTIVE' AND e.ACTIVE_FLAG = 'Y'

Tenure formula: TRUNC(MONTHS_BETWEEN(SYSDATE, HIRE_DATE) / 12, 1) — truncated to 1 decimal place in years.

Current salary logic: active salary record (ACTIVE_FLAG='Y') where EFFECTIVE_DATE <= SYSDATE and either END_DATE is NULL or END_DATE > SYSDATE.

---

**View: HRMS.VW_ORG_HIERARCHY**

Purpose: Hierarchical org chart using CONNECT BY.

Warning (from comment): Performance degrades significantly with >500 employees.

Columns: EMP_ID, EMP_NUMBER, FIRST_NAME || ' ' || LAST_NAME AS EMP_NAME, MANAGER_EMP_ID, DEPT_ID, LEVEL AS ORG_LEVEL, SYS_CONNECT_BY_PATH(FIRST_NAME || ' ' || LAST_NAME, ' > ') AS ORG_PATH, CONNECT_BY_ISLEAF AS IS_LEAF

FROM: EMPLOYEES

WHERE: EMPLOYMENT_STATUS = 'ACTIVE'

Hierarchical traversal:
- START WITH MANAGER_EMP_ID IS NULL (top of hierarchy = no manager)
- CONNECT BY PRIOR EMP_ID = MANAGER_EMP_ID
- ORDER SIBLINGS BY LAST_NAME

---

**View: HRMS.VW_EMPLOYEE_COMPENSATION**

Purpose: Current compensation with compa-ratio calculation.

Columns:
- e.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME
- d.DEPT_NAME, j.JOB_TITLE, g.GRADE_NAME
- sr.BASE_SALARY
- g.MIN_SALARY AS GRADE_MIN
- g.MAX_SALARY AS GRADE_MAX
- (g.MIN_SALARY + g.MAX_SALARY) / 2 AS GRADE_MIDPOINT
- ROUND(sr.BASE_SALARY / ((g.MIN_SALARY + g.MAX_SALARY) / 2) * 100, 1) AS COMPA_RATIO
- sr.EFFECTIVE_DATE AS SALARY_EFFECTIVE_DATE
- sr.CHANGE_REASON AS LAST_CHANGE_REASON
- sr.CHANGE_PCT AS LAST_CHANGE_PCT

Compa-ratio formula: ROUND(BASE_SALARY / ((MIN_SALARY + MAX_SALARY) / 2) * 100, 1)
- Numerator: BASE_SALARY
- Denominator: (MIN_SALARY + MAX_SALARY) / 2 (grade midpoint)
- Result: percentage, rounded to 1 decimal place.

Joins:
- EMPLOYEES e → DEPARTMENTS d (DEPT_ID)
- EMPLOYEES e → JOB_TITLES j (JOB_ID)
- JOB_TITLES j → JOB_GRADES g (GRADE_ID)
- EMPLOYEES e → SALARY_RECORDS sr (EMP_ID, ACTIVE_FLAG = 'Y')

WHERE: e.EMPLOYMENT_STATUS = 'ACTIVE'

---

**View: HRMS.VW_LEAVE_SUMMARY**

Purpose: Current calendar year leave balances with utilization percentage.

Columns:
- e.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME
- d.DEPT_NAME
- lt.LEAVE_TYPE_NAME
- lb.OPENING_BALANCE
- lb.ACCRUED
- lb.USED
- lb.ADJUSTMENT
- lb.PENDING
- lb.OPENING_BALANCE + lb.ACCRUED - lb.USED + lb.ADJUSTMENT AS AVAILABLE
- ROUND(lb.USED * 100 / NULLIF(lb.OPENING_BALANCE + lb.ACCRUED, 0), 1) AS UTILIZATION_PCT

Note: AVAILABLE formula in this view does NOT subtract PENDING (unlike the virtual column in LEAVE_BALANCES which does subtract PENDING). This is a discrepancy between the view and the table definition.

Utilization formula: ROUND(USED * 100 / NULLIF(OPENING_BALANCE + ACCRUED, 0), 1) — protected against divide-by-zero via NULLIF.

WHERE: lb.CALENDAR_YEAR = EXTRACT(YEAR FROM SYSDATE) AND e.EMPLOYMENT_STATUS = 'ACTIVE'

---

**View: HRMS.VW_PAYROLL_LATEST**

Purpose: Latest approved payroll run details per employee with gross/tax/deduction/net breakdown.

Columns:
- pd.EMP_ID, e.EMP_NUMBER
- e.FIRST_NAME || ' ' || e.LAST_NAME AS EMP_NAME
- pp.PERIOD_NAME
- SUM(CASE WHEN pd.ELEMENT_TYPE = 'EARNING' THEN pd.AMOUNT ELSE 0 END) AS GROSS_PAY
- SUM(CASE WHEN pd.ELEMENT_TYPE = 'TAX' THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_TAXES
- SUM(CASE WHEN pd.ELEMENT_TYPE IN ('DEDUCTION','BENEFIT') THEN ABS(pd.AMOUNT) ELSE 0 END) AS TOTAL_DEDUCTIONS
- SUM(pd.AMOUNT) AS NET_PAY

Logic:
- "Latest" is determined by: pr.RUN_ID = (SELECT MAX(pr2.RUN_ID) FROM PAYROLL_RUNS pr2 WHERE pr2.STATUS = 'APPROVED')
- Excludes detail rows with pd.STATUS = 'ERROR'
- TAX and DEDUCTION/BENEFIT amounts are shown as absolute values (ABS)
- NET_PAY = sum of all signed amounts (earnings positive, deductions/taxes negative)

GROUP BY: pd.EMP_ID, e.EMP_NUMBER, e.FIRST_NAME || ' ' || e.LAST_NAME, pp.PERIOD_NAME

---

**View: HRMS.VW_PENDING_APPROVALS**

Purpose: Unified view of items pending approval across leave and performance modules.

Columns: APPROVAL_TYPE, ITEM_ID, APPROVER_ID, REQUESTOR_NAME, ITEM_DESCRIPTION, REQUEST_DATE, DETAILS

Part 1 — Leave requests:
- APPROVAL_TYPE = 'LEAVE'
- ITEM_ID = lr.REQUEST_ID
- APPROVER_ID = lr.APPROVER_EMP_ID
- REQUESTOR_NAME = e.FIRST_NAME || ' ' || e.LAST_NAME
- ITEM_DESCRIPTION = lt.LEAVE_TYPE_NAME
- REQUEST_DATE = lr.CREATED_DATE
- DETAILS = lr.TOTAL_DAYS || ' day(s) ' || TO_CHAR(lr.START_DATE, 'MM/DD') || '-' || TO_CHAR(lr.END_DATE, 'MM/DD')
- WHERE lr.STATUS = 'PENDING'

Part 2 — Performance reviews:
- APPROVAL_TYPE = 'PERFORMANCE'
- ITEM_ID = pr.REVIEW_ID
- APPROVER_ID = pr.REVIEWER_EMP_ID
- REQUESTOR_NAME = e.FIRST_NAME || ' ' || e.LAST_NAME
- ITEM_DESCRIPTION = 'Performance Review - ' || rc.CYCLE_NAME
- REQUEST_DATE = pr.CREATED_DATE
- DETAILS = pr.STATUS
- WHERE pr.STATUS = 'MANAGER_REVIEW'

Combined via UNION ALL.
