The file doesn't exist on disk, but the full source was provided in the prompt. Annotating it now based on the supplied content.

The file contains minimal business logic — no IF/CASE conditions, no RAISE_APPLICATION_ERROR, no NVL/DECODE/CASE validations, and no status/type/category filters. What it does have:

- One **hard-coded threshold** (`365` in the default parameter for `purge_old_records`)
- One **BUSINESS-level query filter** in `get_change_history` (date range filtering)
- One **notable design constraint** in the `EXCEPTION` block of `log_action`

Here is the complete file with only the warranted annotations inserted:

```sql
CREATE OR REPLACE PACKAGE BODY HRMS.PKG_AUDIT AS
-- ============================================================================
-- PKG_AUDIT - Audit Trail Package Body
-- ============================================================================

    PROCEDURE log_action(
        p_table_name IN VARCHAR2,
        p_record_id  IN NUMBER,
        p_action     IN VARCHAR2,
        p_user       IN VARCHAR2 DEFAULT USER,
        p_old_values IN CLOB DEFAULT NULL,
        p_new_values IN CLOB DEFAULT NULL
    ) IS
        PRAGMA AUTONOMOUS_TRANSACTION;
    BEGIN
        INSERT INTO AUDIT_LOG (
            AUDIT_ID, TABLE_NAME, RECORD_ID, ACTION_TYPE,
            OLD_VALUES, NEW_VALUES, CHANGED_BY, CHANGED_DATE,
            IP_ADDRESS, SESSION_ID
        ) VALUES (
            SEQ_AUDIT.NEXTVAL, p_table_name, p_record_id, p_action,
            p_old_values, p_new_values, p_user, SYSDATE,
            SYS_CONTEXT('USERENV', 'IP_ADDRESS'),
            SYS_CONTEXT('USERENV', 'SESSIONID')
        );
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            -- RULE: Audit logging failures must be silently swallowed so that a
            --       failed audit write never rolls back or aborts the caller's
            --       business transaction.
            -- Audit logging must never fail the calling transaction
            ROLLBACK;
    END log_action;

    PROCEDURE purge_old_records(
        -- CONSTRAINT: Default retention period is 365 days (1 year); records older
        --             than this threshold are considered eligible for purge.
        p_days_to_keep IN NUMBER DEFAULT 365,
        p_user         IN VARCHAR2 DEFAULT USER
    ) IS
        v_deleted NUMBER;
    BEGIN
        -- BUSINESS: Only audit records whose change date falls before the
        --           calculated cutoff (today minus the retention window) are
        --           selected for deletion; records within the retention period
        --           are preserved.
        DELETE FROM AUDIT_LOG
        WHERE CHANGED_DATE < SYSDATE - p_days_to_keep;

        v_deleted := SQL%ROWCOUNT;
        COMMIT;

        DBMS_OUTPUT.PUT_LINE('Purged ' || v_deleted || ' audit records older than ' ||
            p_days_to_keep || ' days');
    END purge_old_records;

    FUNCTION get_change_history(
        p_table_name IN VARCHAR2,
        p_record_id  IN NUMBER,
        p_from_date  IN DATE DEFAULT NULL,
        p_to_date    IN DATE DEFAULT NULL
    ) RETURN SYS_REFCURSOR IS
        v_cursor SYS_REFCURSOR;
    BEGIN
        OPEN v_cursor FOR
            -- BUSINESS: History is scoped to a specific table and record; an
            --           optional date range further restricts results so callers
            --           can retrieve changes within a known time window.
            --           NULL boundaries are treated as open-ended (no lower or
            --           upper date limit applied).
            SELECT AUDIT_ID, TABLE_NAME, RECORD_ID, ACTION_TYPE,
                   OLD_VALUES, NEW_VALUES, CHANGED_BY, CHANGED_DATE,
                   IP_ADDRESS
            FROM AUDIT_LOG
            WHERE TABLE_NAME = p_table_name
            AND RECORD_ID = p_record_id
            AND (p_from_date IS NULL OR CHANGED_DATE >= p_from_date)
            AND (p_to_date IS NULL OR CHANGED_DATE <= p_to_date)
            ORDER BY CHANGED_DATE DESC;

        RETURN v_cursor;
    END get_change_history;

END PKG_AUDIT;
/
```

---

**Summary of annotations added (3 total):**

| Location | Tag | Rule documented |
|---|---|---|
| `log_action` EXCEPTION block | `RULE` | Audit failures must never propagate to the caller's transaction — silent swallow is intentional. |
| `purge_old_records` parameter default | `CONSTRAINT` | `365` is the system-wide audit retention period; records older than one year are purge-eligible. |
| `purge_old_records` DELETE WHERE clause | `BUSINESS` | Only records outside the retention window are deleted; in-window records are untouched. |
| `get_change_history` cursor WHERE clause | `BUSINESS` | History is always scoped to a single table+record; date bounds are optional and open-ended when NULL. |

No annotations were added for IF/CASE, RAISE_APPLICATION_ERROR, NVL/DECODE, or status/type/category filters because none exist in this file.
