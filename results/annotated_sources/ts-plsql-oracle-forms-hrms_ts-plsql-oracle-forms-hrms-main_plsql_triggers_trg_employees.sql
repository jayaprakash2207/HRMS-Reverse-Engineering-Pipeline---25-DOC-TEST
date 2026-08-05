Done. Here is a summary of every annotation added and the reasoning behind each:

---

### TRG_EMP_BEFORE_INSERT

| Location | Tag | What it documents |
|---|---|---|
| `IF :NEW.CREATED_BY IS NULL` | `RULE` | Audit field defaults to the session user; the caller may supply it, but it is never left blank. |
| `IF :NEW.CREATED_DATE IS NULL` | `RULE` | Same defaulting rule for the creation timestamp. |
| `IF :NEW.ACTIVE_FLAG IS NULL` | `RULE` | New employees are active by default — `'Y'` is the system-assumed state on insert. |
| `IF :NEW.EMPLOYMENT_STATUS IS NULL` | `RULE` | New employees default to `ACTIVE` employment status. |
| `SYSDATE + 180` | `CONSTRAINT` + `RULE` | 180-day future-hire horizon is a hard business threshold; the `RULE` above it explains the business intent. |
| `RAISE_APPLICATION_ERROR(-20501,…)` | `RULE` | Explicit error surface for the hire-date ceiling. |
| `WHERE … AND ACTIVE_FLAG = 'Y'` | `BUSINESS` | Email uniqueness is only enforced against *active* employees — inactive records do not block reuse. |
| `IF v_count > 0` | `RULE` | No two active employees may share an email address. |
| `RAISE_APPLICATION_ERROR(-20502,…)` | `RULE` | Explicit error surface for the duplicate-email check. |

### TRG_EMP_BEFORE_UPDATE

| Location | Tag | What it documents |
|---|---|---|
| `NVL(:NEW.MODIFIED_BY, USER)` | `VALIDATION` | Audit field is never left blank; defaults to session user. |
| `IF :OLD.EMPLOYMENT_STATUS = 'TERMINATED' AND :NEW.EMPLOYMENT_STATUS = 'ACTIVE'` | `RULE` | Terminated → Active transition is a protected state change that must go through the rehire package procedure. |
| `RAISE_APPLICATION_ERROR(-20503,…)` | `RULE` | Error surface for the illegal reactivation attempt. |
| `IF :OLD.EMPLOYMENT_STATUS != :NEW.EMPLOYMENT_STATUS` | `RULE` | Every status change must produce an audit history row. |
| `IF NVL(:OLD.DEPT_ID, -1) != NVL(:NEW.DEPT_ID, -1)` | `RULE` | Every department transfer (including to/from NULL) must produce an audit history row. |
| `IF NVL(:OLD.JOB_ID, -1) != NVL(:NEW.JOB_ID, -1)` | `RULE` | Every job change (including to/from NULL) must produce an audit history row. |

### TRG_EMP_INSTEAD_OF_DELETE

| Location | Tag | What it documents |
|---|---|---|
| `RAISE_APPLICATION_ERROR(-20504,…)` | `RULE` | Physical deletion is categorically forbidden; the only permitted deactivation paths are setting `ACTIVE_FLAG = 'N'` or running the termination process. |
