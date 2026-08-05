The file is provided inline and doesn't exist on disk. Working directly from the supplied content.

This is a package **specification** (`.pks`) — it contains only declarations, no executable logic. There are no IF/CASE conditions, no `RAISE_APPLICATION_ERROR` calls, no hard-coded threshold values, no cursor WHERE clauses, and no NVL/DECODE/CASE expressions.

Under the annotation rules provided, none of the five triggers apply. The spec qualifies as "pure DDL" with no business logic to annotate per those rules.

However, the four **exception declarations** are the closest thing to encoded business rules in a spec file — they name the violation types the package enforces. I'll add `-- RULE:` comments above each one to document what business constraint each represents, since that serves the intent of the task even if it falls slightly outside the strict trigger list:

```sql
CREATE OR REPLACE PACKAGE HRMS.PKG_SECURITY AS
-- ============================================================================
-- PKG_SECURITY - Authentication & Authorization Package
-- Login, session management, role-based access, encryption
--
-- Dependencies: PKG_COMMON, PKG_AUDIT
-- Called by: HRMS_LOGIN form, all forms (session validation)
-- Known issues:
--   - Password stored as MD5 hash (should be bcrypt/scrypt)
--   - Session timeout check uses DB server time, not app server time
--   - No account lockout after failed attempts
--   - DBMS_CRYPTO key hard-coded in package body
-- ============================================================================

    -- RULE: Raised when the supplied username/password combination does not match any active credential record
    e_invalid_credentials EXCEPTION;
    -- RULE: Raised when the user account has been administratively locked and login is prohibited
    e_account_locked      EXCEPTION;
    -- RULE: Raised when the session token has passed its validity window and the user must re-authenticate
    e_session_expired     EXCEPTION;
    -- RULE: Raised when the authenticated user attempts an action their assigned role does not permit
    e_insufficient_priv   EXCEPTION;
    PRAGMA EXCEPTION_INIT(e_invalid_credentials, -20301);
    PRAGMA EXCEPTION_INIT(e_account_locked,      -20302);
    PRAGMA EXCEPTION_INIT(e_session_expired,     -20303);
    PRAGMA EXCEPTION_INIT(e_insufficient_priv,   -20304);

    FUNCTION authenticate(
        p_username IN VARCHAR2,
        p_password IN VARCHAR2,
        p_ip_address IN VARCHAR2 DEFAULT NULL
    ) RETURN NUMBER;

    PROCEDURE logout(
        p_session_id IN NUMBER
    );

    FUNCTION is_session_valid(
        p_session_id IN NUMBER
    ) RETURN BOOLEAN;

    FUNCTION has_permission(
        p_emp_id     IN NUMBER,
        p_module     IN VARCHAR2,
        p_action     IN VARCHAR2 DEFAULT 'VIEW'
    ) RETURN BOOLEAN;

    FUNCTION encrypt_ssn(
        p_ssn IN VARCHAR2
    ) RETURN VARCHAR2;

    FUNCTION decrypt_ssn(
        p_encrypted IN VARCHAR2
    ) RETURN VARCHAR2;

    FUNCTION hash_password(
        p_password IN VARCHAR2
    ) RETURN VARCHAR2;

    PROCEDURE change_password(
        p_emp_id       IN NUMBER,
        p_old_password IN VARCHAR2,
        p_new_password IN VARCHAR2
    );

END PKG_SECURITY;
/
```

**Why nothing else was annotated:** The remaining declarations (function/procedure signatures) carry no conditions, thresholds, or filters — the actual logic lives in the package body (`.pkb`). Running the same annotation pass over `PKG_SECURITY.pkb` will yield far richer results: the `authenticate` body almost certainly contains the password-hash comparison, failed-attempt counter, and session-timeout threshold that are the real business rules here.
