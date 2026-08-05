This file contains no executable PL/SQL code — it is entirely a structured comment block documenting the menu layout of a compiled Oracle Forms binary (`.mmb`). There are no `IF`/`CASE` conditions, no `RAISE_APPLICATION_ERROR` calls, no hard-coded threshold values, no cursors or `WHERE` clauses, and no `NVL`/`DECODE`/`CASE` expressions anywhere in the file.

Per the annotation rules: **the file is returned unchanged.**

The only business-rule-adjacent information it contains is already expressed in existing comments:

- `System Parameters` and `User Management` under the **Admin** menu require `ADMIN` permission (line 51–52) — but this is prose documentation, not executable logic.
- Menu item enable/disable logic lives at runtime via `PKG_SECURITY.has_permission()` called from `WHEN-NEW-FORM-INSTANCE` (lines 59–60) — but that trigger code is not present in this file.

To annotate the actual permission-gating logic, the trigger source (wherever `WHEN-NEW-FORM-INSTANCE` is defined for this menu) would be the right target file.
