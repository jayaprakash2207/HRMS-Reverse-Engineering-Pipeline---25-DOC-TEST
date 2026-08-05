The file is annotated. Here is a summary of every annotation inserted and the reasoning behind each:

---

**`TRG_SALARY_AUDIT`** — 5 annotations

| Location | Tag | What it documents |
|---|---|---|
| Above `IF INSERTING` | `RULE` | INSERT path must capture `EMP_ID`, `BASE_SALARY`, and `EFFECTIVE_DATE` to establish the initial compensation record |
| Above `ELSIF UPDATING` | `RULE` | UPDATE path must preserve both old and new `BASE_SALARY` + `ACTIVE_FLAG` so compensation changes can be reviewed over time |
| Above `ELSIF DELETING` | `RULE` | DELETE path must retain `EMP_ID` and last-known salary so the full compensation history is never lost |
| Above `NVL(:NEW.SALARY_ID, :OLD.SALARY_ID)` | `VALIDATION` | NVL resolves the record identity across all three DML operations — the audit entry must always point to the correct row |
| Above `NVL(:NEW.MODIFIED_BY, USER)` | `VALIDATION` | NVL ensures the actor is never blank; falls back to the DB session user when the application does not supply `MODIFIED_BY` |

---

**`TRG_LEAVE_REQUEST_AUDIT`** — 2 annotations

| Location | Tag | What it documents |
|---|---|---|
| Above `CREATE OR REPLACE TRIGGER` | `RULE` | The `AFTER UPDATE OF STATUS` column-list trigger means **only status transitions** are audited; all other field edits are invisible to this trigger — a deliberate scope decision |
| Above `NVL(:NEW.MODIFIED_BY, USER)` | `VALIDATION` | Same actor-fallback pattern as salary; ensures leave-approval workflow history is always attributable |

---

**`TRG_DEPARTMENT_AUDIT`** — 3 annotations

| Location | Tag | What it documents |
|---|---|---|
| Above `IF INSERTING` | `RULE` | All structural changes (create / rename / delete) to a department must be logged — governance and accountability requirement |
| Above `NVL(:NEW.DEPT_ID, :OLD.DEPT_ID)` | `VALIDATION` | Same NVL identity-resolution pattern; ensures the audit row is always linked to the correct department regardless of DML type |
| Above `USER` | `RULE` | Unlike `SALARY_RECORDS` and `LEAVE_REQUESTS`, `DEPARTMENTS` has no `MODIFIED_BY` column, so the DB session user is the only available actor |
