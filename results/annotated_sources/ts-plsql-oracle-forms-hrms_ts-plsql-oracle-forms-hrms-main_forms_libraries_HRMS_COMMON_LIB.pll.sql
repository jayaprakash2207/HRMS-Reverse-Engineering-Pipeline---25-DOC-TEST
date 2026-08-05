The file is complete and correct. Here is a summary of every annotation added and the reasoning behind each:

---

**Annotations added (8 comment lines, zero code changes):**

| Line | Tag | Business rule documented |
|------|-----|--------------------------|
| 25 | `VALIDATION` | `NVL(:GLOBAL.current_user, USER)` in error logging — falls back to DB session user so error logs always carry a user identity, even before HRMS login completes. |
| 57 | `RULE` | `toolbar_query` toggle logic — the Query button is a two-state toggle: first press enters query mode (`NORMAL` → `ENTER-QUERY`), second press fires the query (`ENTER-QUERY` → executes). Any other mode is silently ignored. |
| 118 | `VALIDATION` | `NVL(:GLOBAL.current_user, USER)` in `get_current_user` — same fallback pattern as error logging; ensures every audit trail has a traceable identity. |
| 132 | `RULE` | `get_session_id IS NULL` check — no HRMS form operation is allowed without a session ID; missing ID means the user has never authenticated. |
| 135 | `RULE` | `RAISE FORM_TRIGGER_FAILURE` on null session — hard stop; the form cannot proceed until the user logs in. |
| 139 | `RULE` | `PKG_SECURITY.is_session_valid` check — a session ID alone is not enough; the security package must also confirm it is still valid (handles token expiry / forced logouts). |
| 142 | `RULE` | `RAISE FORM_TRIGGER_FAILURE` on expired session — hard stop; the user must re-authenticate. |
| 155 | `RULE` | `ID_NULL(FIND_GROUP(...))` guard in `refresh_lov` — the LOV record group is only repopulated when it already exists; refreshing a non-existent group would be a runtime error. |

**No annotations were added for** the pure toolbar wrappers (`COMMIT_FORM`, `CLEAR_FORM`, etc.), the date-format functions, or `get_session_id` — those contain no business logic worth annotating per the rules.
