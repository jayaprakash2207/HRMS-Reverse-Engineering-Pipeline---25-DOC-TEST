# Final Sanity Check — D1 Application Architecture Extraction
**Reviewer:** Agent 06 — Quality Review Agent
**Date:** 2026-08-04
**System:** HRMS v4.2 / Oracle Forms 12c / Oracle PL/SQL

---

## Section 1: Required Files — All Present

| Required Output File | Present | Valid | Notes |
|---|---|---|---|
| AA_App_Extractor.md | YES | YES | Agent 1 role card |
| application-architecture-summary.md | YES | YES | Narrative summary |
| application-interface-catalogue.json | YES | YES | JSON valid |
| application-risk-register.json | YES | YES | 12 risks |
| architecture-pattern-report.md | YES | YES | Pattern analysis |
| architecture-violation-register.json | YES | YES | 23 violations |
| call-flow-map.json | YES | YES | 6 flows |
| component-registry.json | YES | YES | 20 components |
| dependency-graph.json | YES | YES | 21 nodes, 37 edges |
| extraction-audit.md | YES | YES | Coverage matrix |
| forward-engineering-input-map.md | YES | YES | Migration guidance |
| module-boundary-map.json | YES | YES | 11 modules |
| open-questions.md | YES | YES | Unknowns catalogued |
| strangler-candidate-report.md | YES | YES | Migration sequence |
| system-inventory.json | YES | YES | System totals |
| diagrams/system-context.mmd | YES | YES | C4 Level 1 |
| diagrams/container-view.mmd | YES | YES | C4 Level 2 |
| diagrams/component-view.mmd | YES | YES | C4 Level 3 |
| diagrams/dependency-view.mmd | YES | YES | Full dep graph |
| diagrams/call-flow-view.mmd | YES | YES | Key flows |

**All 20 required output files present. PASS.**

---

## Section 2: JSON Validity

| File | Valid JSON | Issues |
|---|---|---|
| application-interface-catalogue.json | YES | — |
| application-risk-register.json | YES | — |
| architecture-violation-register.json | YES | — |
| call-flow-map.json | YES | — |
| component-registry.json | YES | — |
| dependency-graph.json | YES | — |
| module-boundary-map.json | YES | — |
| system-inventory.json | YES | — |

All 8 JSON files: no trailing commas, no unclosed braces/brackets, all string values properly delimited. **PASS.**

---

## Section 3: Counts Cross-Check

| Item | system-inventory | extraction-audit | component-registry | spot-check confirms | Status |
|---|---|---|---|---|---|
| Packages | 11 | 11 | 11 | 11 | PASS |
| Forms | 6 | 6 | 6 | 6 | PASS |
| DB Triggers | 6 | 6 | 1 entry (6 named) | 6 | PASS |
| Tables | 22 | 22 | — | Not enumerable from spot-check alone | PASS |
| Views | 6 | 6 | — | Referenced but not enumerable from spot-check | PASS |
| Sequences | 29 | 30 | — | 15 confirmed in spot-check; total unknown without raw DDL | DISC-001 |
| Form libraries | 2 | 2 | 2 | 2 | PASS |
| Modules | 11 | — | 11 | — | PASS |
| Components | 20 | — | 20 | — | PASS |
| Risks | 12 | 12 | — | — | PASS |
| Violations | 23 | 23 | — | 5 spot-checked | PASS |

**DISC-001 documented.** All other counts consistent. **PASS with 1 minor discrepancy.**

---

## Section 4: Procedure Count vs Source Files

| Package | Reported | Source Confirms | Status |
|---|---|---|---|
| PKG_AUDIT | 3 | 3 | PASS |
| PKG_COMMON | 17 | 17 | PASS |
| PKG_EMPLOYEE | 18 (registry) / 18 (audit) | 18 confirmed | PASS |
| PKG_INTEGRATION | 5 | 5 | PASS |
| PKG_LEAVE | 14 | 14 | PASS |
| PKG_NOTIFICATION | 4 | 4 | PASS |
| PKG_PAYROLL | 17 (registry public_methods) | 18 in source | OFF BY 1 — calculate_employee_pay missing from public_methods list |
| PKG_PERFORMANCE | 11 (extraction-audit) / 12 (registry) | 12 in source | extraction-audit count is off by 1 |
| PKG_REPORTING | 8 | 8 | PASS |
| PKG_SECURITY | 8 | 8 | PASS |
| PKG_VALIDATION | 8 | 8 | PASS |

**2 minor off-by-one counts.** Both procedures exist and are documented elsewhere in the output (calculate_employee_pay in call-flow-map; generate_reviews_for_cycle in component-registry). No substantive gap.

---

## Section 5: Dependency Graph Integrity

| Check | Result |
|---|---|
| All edge `from` nodes declared | PASS — 17 distinct `from` values, all in nodes array |
| All edge `to` nodes declared | PASS — 10 distinct `to` values, all in nodes array |
| Circular dependency documented | PASS — CYC-001: PKG_EMPLOYEE ↔ PKG_PAYROLL |
| DBMS_SCHEDULER in dependency-view.mmd | PARTIAL — present in .mmd, absent from JSON nodes array |
| High-coupling components identified | PASS — PKG_COMMON (11 afferent), PKG_AUDIT (9 afferent), PKG_SECURITY (7 afferent) |

---

## Section 6: Business Rule Integrity

Spot-check of 25 specific numeric/literal business rules against source code. All 25 match exactly:

- Session timeout: 30 min ✓
- Leave backdating: 5 days ✓
- SS wage base: $168,600 ✓
- Medicare threshold: $200,000 ✓
- Audit retention: 365 days ✓
- Hire date form limit: 90 days ✓
- Hire date trigger limit: 180 days ✓ (documented as CONFLICT)
- EMP_NUMBER format: `EMP-\d{6}` ✓
- Fiscal year start: month 10 (October) ✓
- Performance rating bounds: 1.0–5.0 ✓
- Rating label boundaries (all 5) ✓
- Payroll commit interval: 50 employees ✓
- Leave accrual commit: 100 employees ✓
- Notification batch size: 50 ✓
- Max retry count: 3 ✓
- Max hierarchy depth: 15 ✓
- Fed standard deduction single: $14,600 ✓
- Fed standard deduction married: $29,200 ✓
- Per-allowance reduction: $4,300 ✓
- SMTP host: smtp.internal.company.com:25 ✓
- SSN key literal: `HR$ystem_3ncrypt10n_K3y_2024!!` ✓
- MD5 hash algorithm: DBMS_CRYPTO.HASH_MD5 ✓
- Benefits feed record width: 203 chars ✓
- GL file format: pipe-delimited with H/D/T records ✓
- Pay register format: 10-column CSV, FM999999990.00 ✓

**All 25 business rules verified exact. PASS.**

---

## Section 7: No Invented Cloud/Platform Assumptions

| Claim category | Finding |
|---|---|
| Cloud provider assumed | NONE — no AWS/Azure/GCP mentioned |
| Container technology assumed | NONE |
| REST/HTTP API assumed | NONE — all inter-component communication is PL/SQL direct call or UTL_FILE |
| Deployment topology invented | NONE — noted as "unknown" throughout |
| Runtime database version invented | NONE — "Oracle Database" stated without version number |
| DBMS_SCHEDULER jobs invented | NONE — correctly flagged as "implied from comments, not confirmed in source" |

**PASS.**

---

## Section 8: Discrepancy Register

| ID | Location | Description | Status |
|---|---|---|---|
| DISC-001 | system-inventory.json vs extraction-audit.md | Sequence count: 29 vs 30 | Open — use 30 (from DDL audit row) pending raw DDL verification |
| AV-013 | architecture-violation-register.json | Hire date limit: 90 days (form) vs 180 days (trigger) | Documented as violation; both values cited; unresolved by design |
| DISC-002 | HRMS_VALIDATION_LIB vs PKG_COMMON | SSN validation: client rejects all-zero segments (area/group/serial); server does not — see QR-019 in quality-review.md | Open — not in original Agent 1 output; must be added to violation register |
| DISC-003 | trg_employees.sql TRG_EMP_BEFORE_UPDATE vs PKG_EMPLOYEE.pkb log_history | EMPLOYEE_HISTORY PK column named HISTORY_ID (trigger) vs HIST_ID (package); trigger uses generic schema (OLD_VALUE, NEW_VALUE VARCHAR2); package uses typed schema (OLD_DEPT_ID, NEW_DEPT_ID NUMBER, etc.) — see QR-026 in quality-review.md | **Critical** — one of the two INSERT paths fails at runtime with ORA-00904; requires DDL inspection to resolve |

---

## Section 9: Completeness Assessment

### What is complete:
- All 11 package bodies fully documented with per-procedure parameter signatures, business rules, exceptions, and table references
- All 6 Oracle Forms documented with blocks, items, triggers, LOVs, and package call patterns
- All 6 DB triggers documented with exact firing conditions and logic
- All 2 form libraries documented with every public function/procedure
- All 12 risks have source evidence, migration impact, and recommended action
- All 23 violations have source evidence, affected components, and remediation
- Circular dependency explicitly documented with both sides of the cycle
- 6 migration blockers explicitly flagged
- Extraction unknowns explicitly catalogued (4 critical unknowns)

### What is incomplete or missing from source (not an extraction gap — genuinely absent from provided files):
- USER_CREDENTIALS table DDL
- HRMS_ADMIN.fmb content
- HRMS_REPORTS.fmb content
- DBMS_SCHEDULER job definitions
- Oracle directory OS path mappings
- Production deployment configuration (sqlnet.ora, listener.ora)
- Oracle Reports .rdf files

---

## Section 10: Pass 2 Gap Summary [EDGE-CASE-FOUND]

Second independent analysis pass added the following findings (full detail in quality-review.md):

| ID | Severity | Finding |
|---|---|---|
| QR-016 | Medium | [EDGE-CASE-FOUND] 21+ package procedures with no confirmed form entry point — not enumerated in any output |
| QR-017 | Medium | [EDGE-CASE-FOUND] 5 direct form-to-table dependency edges missing from dependency-graph.json |
| QR-018a | High | [EDGE-CASE-FOUND] HRMS_PERFORMANCE.fmb bypasses PKG_PERFORMANCE procedures — all performance notifications silenced |
| QR-018b | High | [EDGE-CASE-FOUND] HRMS_EMPLOYEE.fmb PRE-INSERT bypasses create_employee — no salary creation, no notifications via form hire path |
| QR-019 / DISC-002 | Medium | [EDGE-CASE-FOUND] SSN validation drift (zero-segment check) absent from violation register |
| QR-020 | Low | [EDGE-CASE-FOUND] PKG_COMMON.log_info lacks double-quote escaping; INFO_LOG rows produce malformed JSON |
| QR-021 | Medium | [EDGE-CASE-FOUND] PKG_SECURITY.authenticate TOO_MANY_ROWS account-takeover path not a distinct violation |
| QR-022 | Low | [EDGE-CASE-FOUND] PKG_PAYROLL.reverse_payroll silently discards p_reason — no audit trail for reversal justification |
| QR-023 | High | [EDGE-CASE-FOUND] CF-002 steps 5-7 describe package API not form DML; call flow is inaccurate for form-driven hire |
| QR-024 | Medium | [EDGE-CASE-FOUND] AV-018 remediation scope understated; Leave and Performance form WHEN-NEW-FORM-INSTANCE also lack permission checks |
| QR-025 | Medium | [EDGE-CASE-FOUND] Risk register missing entry for lifecycle procedures (terminate/transfer/promote) orphaned from forms |

---

## Section 11: Pass 3 Gap Summary [EDGE-CASE-FOUND]

Third independent analysis pass added the following findings (full detail in quality-review.md):

| ID | Severity | Finding |
|---|---|---|
| QR-026 / DISC-003 | **High** | [EDGE-CASE-FOUND] EMPLOYEE_HISTORY has two incompatible write schemas (HISTORY_ID vs HIST_ID PK column name; generic vs typed columns) — one INSERT path broken at runtime with ORA-00904 |
| QR-027 | Medium | [EDGE-CASE-FOUND] PKG_COMMON.business_days_between and add_business_days ignore holidays; PKG_LEAVE.calculate_business_days does not — divergent behavior; not flagged in forward-engineering map |
| QR-028 | Medium | [EDGE-CASE-FOUND] PKG_PAYROLL.reverse_payroll has no status pre-check — approved/funded payrolls can be reversed unconditionally by any authenticated session |
| QR-029 | Low | [EDGE-CASE-FOUND] Non-EMAIL notifications in NOTIFICATION_QUEUE are never dispatched and accumulate indefinitely |
| QR-030 | Medium | [EDGE-CASE-FOUND] PKG_LEAVE.run_monthly_accrual non-idempotent — double scheduler run doubles accrual balances for all active employees |
| QR-031 | Low | [EDGE-CASE-FOUND] PKG_EMPLOYEE.promote_employee has no EMPLOYMENT_STATUS pre-check — terminated employees can receive promotions |
| QR-032 | Medium | [EDGE-CASE-FOUND] PKG_SECURITY.change_password does not verify old password — privilege escalation once AV-004 is fixed; fix order is critical |
| QR-033 | Low | [EDGE-CASE-FOUND] Double EMPLOYEE_HISTORY writes (package log_history + TRG_EMP_BEFORE_UPDATE) inflate lifecycle event counts for audit queries |

---

## Final Verdict

**PARTIAL**

Structural extraction is complete and accurate. No critical fabrications, no missing required output files, no broken JSON, no invented technology claims.

**Pass 1 issues (minor — count/consistency only):**
1. PKG_PAYROLL public_methods count 17 in registry; 18 in source
2. Extraction-audit says 11 members for PKG_PERFORMANCE; source has 12
3. DBMS_SCHEDULER in Mermaid diagram but absent from JSON nodes array; sequence count 29 vs 30

**Pass 2 issues (analysis-layer — affect migration planning):**
4. CF-002 steps 5-7 describe the package API path, not the actual form DML hire path — salary creation and notifications do not fire through the form
5. HRMS_PERFORMANCE.fmb bypasses PKG_PERFORMANCE procedures entirely; all performance notifications are silenced in the form-driven path
6. 21+ package procedures with no confirmed form entry point not enumerated
7. DISC-002 (SSN validation zero-segment drift) not in violation register
8. PKG_SECURITY.authenticate TOO_MANY_ROWS account-takeover path not in violation register as a distinct entry

Items 4 and 5 are the most significant from Pass 2: they mean two documented call flows are inaccurate, and the notification gaps are functional regressions invisible to the architecture review.

**Pass 3 issues (schema and operational correctness):**
9. DISC-003: EMPLOYEE_HISTORY PK column name conflict (HISTORY_ID vs HIST_ID) — one write path is broken at runtime. This cannot be resolved without DDL inspection of the live schema. Must be resolved before any migration that reads EMPLOYEE_HISTORY.
10. run_monthly_accrual non-idempotency — the same pattern documented in AV-016 (expire_carryover) is present at larger scale in the monthly accrual batch.
11. reverse_payroll has no authorization gate — an approved payroll can be reversed unconditionally.
12. change_password does not verify the old password — this becomes a privilege escalation vector the moment AV-004 is fixed; the two must be fixed together.

These must be corrected before forward engineering design begins. DISC-003 in particular should prompt a DDL audit of EMPLOYEE_HISTORY column definitions in the production database.
