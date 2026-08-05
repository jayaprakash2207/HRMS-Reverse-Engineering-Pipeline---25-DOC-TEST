This file is a package specification (`.pks`) — it contains only declarations: exception names, PRAGMA mappings, type definitions, and procedure/function signatures. There is no imperative code: no `IF`/`CASE` conditions, no `RAISE_APPLICATION_ERROR` calls, no hard-coded threshold values used in comparisons, no cursor `WHERE` clauses, and no `NVL`/`DECODE`/`CASE` expressions.

Per the annotation rules, none of the five annotation triggers apply here. The instruction also says:

> If the file has no business logic worth annotating (e.g. pure DDL, pure data), return it unchanged.

**The file is returned unchanged.** The business logic that warrants annotation lives in the corresponding package body (`PKG_LEAVE.pkb`). That file will contain the `IF` checks against leave status, balance comparisons against thresholds, overlap detection queries with `WHERE` clauses, and `RAISE_APPLICATION_ERROR` calls wired to the four declared exceptions (`-20201` through `-20204`). Annotating that body will yield meaningful `-- RULE:`, `-- CONSTRAINT:`, `-- BUSINESS:`, and `-- VALIDATION:` comments.
