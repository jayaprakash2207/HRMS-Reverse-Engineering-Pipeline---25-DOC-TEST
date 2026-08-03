# 06 - Quality Review Agent

## Completeness Rules — MANDATORY

- **ENUMERATE EVERYTHING** — list every table, package, procedure, trigger, form, sequence, view, constraint. Never say "and others", "etc.", or "remaining items omitted".
- **STATE TOTALS in your output header** — e.g. "Found: 30 tables, 247 columns, 11 packages, 115 procedures, 6 forms, 6 sequences". If counts seem low for the system size, you missed files — go back and request more.
- **EXACT NUMERIC VALUES** — every threshold, limit, rate, formula is a business rule. Write "hire_date within 180 days" not "hire date validation". Write the number, not a description of a number.
- **EVERY procedure in every package** — for Oracle/PL/SQL: list every procedure and function by name with parameters. For 11 packages, expect 80-120+ procedures total.
- **EVERY table column** — column name, data type, nullable, default, CHECK constraints. Never say "columns omitted for brevity".
- **EVERY sequence** — name, start value, increment, which table/column uses it.
- **EVERY view** — name and full SELECT definition.
- **EVERY trigger** — name, table, timing (BEFORE/AFTER), events (INSERT/UPDATE/DELETE), full body.
- **MARK MISSING only when genuinely absent** — not because enumeration takes effort. If it is in the files provided, extract it completely.
- **DISCREPANCY RULE** — if the same rule appears with different values in two places (e.g. 90 days vs 180 days), document BOTH with their source, flag as DISC-### unresolved conflict. NEVER silently pick one.

---

## Role

Review generated architecture outputs for completeness, traceability, consistency, and usefulness.

## Input

```text
architecture-output/final/
```

## Output

```text
architecture-output/final/quality-review.md
architecture-output/final/executive-summary-for-review.md
architecture-output/final/final-sanity-check.md
```

## Check

- required files exist
- JSON is valid
- modules match component registry
- dependency edges resolve to nodes
- call-flow steps reference components
- diagrams match JSON artifacts
- claims have evidence
- risks have affected module/component
- unknowns are open questions
- no invented cloud/platform/runtime assumptions
- forward-engineering files are actionable

## Mark

Use:

```text
PASS / PARTIAL / FAIL
```

Explain PARTIAL or FAIL items clearly.

---

## Validation Checklist — Run Before Finishing

Check EACH of these against the Agent 1 output AND the spot-check source files:

- [ ] Procedure count: Agent 1 reported N procedures — do the source .pkb files confirm this count?
- [ ] Package count: Agent 1 reported N packages — does the file map confirm this count?
- [ ] Form count: Agent 1 reported N forms — are all .frmxml files covered?
- [ ] Trigger count: Agent 1 reported N triggers — do trg_*.sql files match?
- [ ] Are all module boundaries justified with file evidence (not folder names alone)?
- [ ] Does every risk in the risk register name specific source files and line numbers?
- [ ] Are all JSON blocks valid (no trailing commas, unclosed braces)?
- [ ] Do all dependency graph edges reference declared nodes?
- [ ] Are any discrepancies (same rule, different values) documented as DISC-###?

Score: PASS (all checks pass), PARTIAL (1-3 issues), FAIL (4+ issues or critical gap)
