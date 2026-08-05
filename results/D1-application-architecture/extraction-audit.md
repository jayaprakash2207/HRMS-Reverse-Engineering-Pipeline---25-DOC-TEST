# Extraction Audit — Oracle HRMS v4.2
**Extractor:** AA Agent 1 — Application Architecture Extractor
**Date:** 2026-08-04
**Pipeline Stage:** D1 — Application Architecture

---

## Summary

| Metric | Value |
|---|---|
| Source files analyzed | 38 (11 pkg specs, 11 pkg bodies, 4 DDL scripts, 1 sequences, 1 views, 2 trigger files, 2 form libraries, 1 menu, 6 form XML exports) |
| Output files produced | 20 |
| Overall extraction confidence | 0.88 |
| Critical unknowns | 4 (see open-questions.md) |
| Violations identified | 25 |
| Risks identified | 14 |

---

## Per-Component Confidence Scores

| Component | Confidence | Basis | Gaps |
|---|---|---|---|
| System inventory | 0.95 | Hard version string in HRMS_MENU.xml; all packages present; schema name explicit | Oracle DB version unknown; deployment server unknown |
| Module boundary map | 0.90 | Package names directly encode domain ownership | HRMS_ADMIN.fmb and HRMS_REPORTS.fmb not in source |
| Component registry | 0.95 | All 11 package specs + bodies present; all 6 form XMLs present | USER_CREDENTIALS table DDL absent |
| Application interface catalogue | 0.90 | Form trigger handlers explicit in XML; batch jobs inferred from package comments | Scheduler job definitions not in source |
| Dependency graph | 0.92 | Cross-package calls explicit in package bodies; circular dep documented | HRMS_ADMIN.fmb missing; may have additional undocumented calls |
| Call flow map | 0.88 | Key flows reconstructed from form triggers + package bodies | HRMS_ADMIN, HRMS_REPORTS flows unknown |
| Architecture pattern report | 0.95 | Pattern is unambiguous from source structure | Deployment topology unknown |
| Architecture violation register | 0.95 | All violations sourced from explicit code evidence | No runtime monitoring data to confirm bug reproduction rates |
| Application risk register | 0.90 | Risks grounded in violations and architectural analysis | Severity ratings are static analysis estimates — no production incident history |
| Strangler candidate report | 0.88 | Coupling scores from dependency graph; feasibility based on pattern analysis | Actual data volume unknown (affects payroll batch risk rating) |
| Forward engineering input map | 0.85 | Recommendations based on code evidence | Business process documentation not available |
| Open questions | 1.00 | All unknowns explicitly catalogued | By definition, cannot be resolved from source alone |
| Diagrams | 0.88 | C4 model derived from source; Mermaid syntax | Deployment-level topology omitted (unknown) |

---

## Source Coverage Matrix

| Source File | Coverage | Notes |
|---|---|---|
| schema/tables/01_core_tables.sql | FULL | All tables enumerated |
| schema/tables/02_payroll_tables.sql | FULL | All tables enumerated — EMPLOYEE_BANK_ACCOUNTS identified as designed but unimplemented (no PL/SQL consumer; AV-024, AV-025) |
| schema/tables/03_leave_tables.sql | FULL | All tables enumerated |
| schema/tables/04_performance_tables.sql | FULL | All tables enumerated |
| schema/sequences/hrms_sequences.sql | FULL | 30 sequences |
| schema/views/hrms_views.sql | FULL | 6 views |
| plsql/packages/PKG_AUDIT.pks/.pkb | FULL | 3 public members |
| plsql/packages/PKG_COMMON.pks/.pkb | FULL | 15 public members |
| plsql/packages/PKG_EMPLOYEE.pks/.pkb | FULL | 18 members; SQL injection documented |
| plsql/packages/PKG_INTEGRATION.pks/.pkb | FULL | 5 members; TODOs documented |
| plsql/packages/PKG_LEAVE.pks/.pkb | FULL | 14 members; bugs documented |
| plsql/packages/PKG_NOTIFICATION.pks/.pkb | FULL | 4 members |
| plsql/packages/PKG_PAYROLL.pks/.pkb | FULL | 17 members; partial commit and YTD bugs documented |
| plsql/packages/PKG_PERFORMANCE.pks/.pkb | FULL | 11 members |
| plsql/packages/PKG_REPORTING.pks/.pkb | FULL | 8 members; placeholder documented |
| plsql/packages/PKG_SECURITY.pks/.pkb | FULL | 8 members; all critical bugs documented |
| plsql/packages/PKG_VALIDATION.pks/.pkb | FULL | 8 functions |
| plsql/triggers/trg_audit.sql | FULL | 3 triggers |
| plsql/triggers/trg_employees.sql | FULL | 3 triggers (BEFORE INSERT, BEFORE UPDATE, INSTEAD OF DELETE) |
| forms/libraries/HRMS_COMMON_LIB.pll.sql | FULL | All documented procedures |
| forms/libraries/HRMS_VALIDATION_LIB.pll.sql | FULL | All documented functions |
| forms/menus/HRMS_MENU.mmb.sql | FULL | Menu structure; permission checks |
| forms/xml-exports/HRMS_LOGIN.xml | FULL | Login flow; global variable setting |
| forms/xml-exports/HRMS_MENU.xml | FULL | MDI shell; module navigation |
| forms/xml-exports/HRMS_EMPLOYEE.xml | FULL | Master-detail employee form; PRE-INSERT; LOVs |
| forms/xml-exports/HRMS_LEAVE.xml | FULL | Tab canvas; all buttons |
| forms/xml-exports/HRMS_PAYROLL.xml | FULL | Payroll run lifecycle buttons |
| forms/xml-exports/HRMS_PERFORMANCE.xml | FULL | Review cycle and goal blocks |
| HRMS_ADMIN.fmb | NOT PROVIDED | Referenced in menu; content unknown |
| HRMS_REPORTS.fmb | NOT PROVIDED | Referenced in menu; content unknown |
| USER_CREDENTIALS DDL | NOT PROVIDED | Referenced in PKG_SECURITY; structure unknown |
| DBMS_SCHEDULER job definitions | NOT PROVIDED | Jobs inferred from package comments only |
| Oracle Directory OS paths | NOT PROVIDED | Directory object names known; filesystem paths unknown |
| Deployment config (sqlnet.ora, etc.) | NOT PROVIDED | Network encryption status unknown |

---

## Hallucination Controls

The following rules were applied throughout this extraction:

1. **No invented facts** — every claim in every output file is traceable to a specific source file and line reference
2. **Unknowns are marked** — wherever source evidence was absent, the value `"unknown"` was used or the question was moved to `open-questions.md`
3. **No code modification** — no legacy source code was altered, reformatted, or generated
4. **No business rule invention** — business rules are only documented when explicitly stated in the code (e.g. tax brackets, fiscal year start, SSN all-zero check)
5. **Severity ratings are evidence-based** — CRITICAL ratings require explicit code evidence of the vulnerability/bug; they are not inferred from general best-practice concerns alone

---

## Known Extraction Limitations

1. **Dynamic SQL analysis** — the SQL injection in PKG_EMPLOYEE.search_employees was identified from the string concatenation pattern; the full exploitability depends on the Oracle DB user's privileges, which are unknown
2. **Runtime behaviour** — partial commit scenarios in PKG_PAYROLL are documented as risks but actual failure rates in production are unknown
3. **Data volume** — all performance risk ratings (org chart timeout, payroll batch performance) are based on documented thresholds in source comments, not measured runtime data
4. **Schema completeness** — the 22 tables documented represent what was in the 4 DDL files provided; additional tables in the HRMS schema (e.g. USER_CREDENTIALS) may exist but were not provided
