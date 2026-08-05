This is a package specification (`.pks`) — it contains only procedure/function signatures with no executable code: no IF/CASE branches, no RAISE_APPLICATION_ERROR, no cursors, no NVL/DECODE/CASE expressions. The one annotatable item is the `DEFAULT 365` on `purge_old_records`, which encodes a data retention policy even as a parameter default.

```sql
CREATE OR REPLACE PACKAGE HRMS.PKG_AUDIT AS
-- ============================================================================
-- PKG_AUDIT - Audit Trail Package
-- Centralized audit logging for all DML operations
--
-- Dependencies: None (base package)
-- Called by: All other packages, database triggers
-- ============================================================================

    PROCEDURE log_action(
        p_table_name IN VARCHAR2,
        p_record_id  IN NUMBER,
        p_action     IN VARCHAR2,
        p_user       IN VARCHAR2 DEFAULT USER,
        p_old_values IN CLOB DEFAULT NULL,
        p_new_values IN CLOB DEFAULT NULL
    );

    -- CONSTRAINT: Default audit retention period is 365 days (1 year); callers
    --             may override but the policy baseline is one full calendar year
    PROCEDURE purge_old_records(
        p_days_to_keep IN NUMBER DEFAULT 365,
        p_user         IN VARCHAR2 DEFAULT USER
    );

    FUNCTION get_change_history(
        p_table_name IN VARCHAR2,
        p_record_id  IN NUMBER,
        p_from_date  IN DATE DEFAULT NULL,
        p_to_date    IN DATE DEFAULT NULL
    ) RETURN SYS_REFCURSOR;

END PKG_AUDIT;
/
```

Only one annotation was added. The rest of the file is pure interface declaration — all business logic (status checks, comparisons, error raises, query filters) lives in the corresponding package body (`PKG_AUDIT.pkb`), which is where the bulk of annotations would apply.
