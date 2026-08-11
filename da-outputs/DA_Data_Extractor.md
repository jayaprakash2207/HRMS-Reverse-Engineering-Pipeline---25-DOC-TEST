# DA Agent 1 — Data Architecture Extractor Report

**Project:** ts-plsql-oracle-forms-hrms  
**Schema:** HRMS  
**DB Engine:** Oracle Database 19c  
**UI Layer:** Oracle Forms 12c (12.2.1.4)  
**Extraction Date:** 2026-08-04  
**Method:** CODE-ONLY  
**Agent Version:** DA Agent 1 (Phase 0-4 completed)

---

## Phase 0: Auto-Detection Summary

| Property | Detected Value |
|---|---|
| Database engine | Oracle 19c |
| ORM | None |
| UI framework | Oracle Forms 12c |
| PL/SQL packages | 11 |
| Tables | 30 |
| Views | 6 |
| Triggers | 6 |
| Sequences | 29 |
| External integrations | UTL_FILE (GL + ADP feeds), UTL_SMTP (email) |
| Live DB connection | NOT AVAILABLE |
| DB connection reason | No Oracle connection string in config.json (empty array); no sqlplus or Oracle Instant Client found on PATH |

---

## Phase 1: Code Discovery Summary

All source files read and catalogued:

| File Category | Files |
|---|---|
| Schema DDL | 4 (01_core_tables, 02_payroll_tables, 03_leave_tables, 04_performance_tables) |
| Views | 1 (hrms_views.sql) |
| Sequences | 1 (hrms_sequences.sql) |
| PL/SQL packages (spec + body) | 22 files across 11 packages |
| Triggers | 2 files (trg_audit.sql, trg_employees.sql) |
| Oracle Forms | 7 files (5 form XML exports + 2 PLL libraries) |
| Seed data | 2 files (01_reference_data, 02_employee_data) |

---

## Phase 2: Database Connection

**Status:** CODE-ONLY

**Reason:** No Oracle connection string found in `config.json` (value is empty array `[]`). No `sqlplus` found on PATH. No Oracle Instant Client found at standard Windows install paths.

**Impact:** All extraction is based on DDL source files and PL/SQL package bodies. Row counts, runtime values, and actual index statistics are not available.

---

## Phase 3: Output Files Written

All 13 output files have been written to `da-outputs/`:

| # | File | Contents |
|---|---|---|
| 1 | `schema-catalogue.json` | 30 tables with all columns, data types, constraints, FKs, sequences, views, packages, triggers |
| 2 | `erd.md` | Mermaid ERD with all FK relationships, soft references, warnings |
| 3 | `data-source-inventory.json` | Oracle DB, Oracle Forms, UTL_FILE directories, UTL_SMTP, SYSTEM_PARAMETERS config store |
| 4 | `data-flow-map.md` | All data flows: Forms->DB, PKG_INTEGRATION->GL/ADP/Time files, PKG_NOTIFICATION->SMTP |
| 5 | `pii-inventory.json` | All PII fields with category, encryption status, and regulatory notes |
| 6 | `data-quality-report.md` | All data quality issues: trigger/DDL mismatches, view bugs, race conditions, known defects |
| 7 | `migration-complexity.json` | 14 migration complexity factors across Oracle Forms, DBMS_CRYPTO, CONNECT BY, UTL_FILE, circular deps, and security tech debt *(CORRECTED by DA Agent 2 — prior text said 17; actual JSON contains MC-01 through MC-14 = 14 factors)* |
| 8 | `hidden-business-rules.json` | 37 business rules embedded in PL/SQL and triggers not visible in DDL |
| 9 | `storage-pattern-analysis.md` | Oracle DB (primary), BLOB/CLOB, UTL_FILE flat files, async notification queue, key-value config store |
| 10 | `redundancy-analysis.json` | 12 redundancies: denormalised columns, formula discrepancies, validation divergences, stale objects |
| 11 | `data-dictionary.md` | Business definitions for all 30 tables and their significant columns |
| 12 | `conceptual-data-model.md` | Business-language domain model with 9 domains and relationship table |
| 13 | `access-control-matrix.md` | Grade-based permission model, module-level matrix, Oracle Forms restrictions, 10 security weaknesses |

---

## Phase 4: Self-Check

### Coverage Verification

| Check | Result |
|---|---|
| All 30 DDL tables documented in schema-catalogue | PASS |
| All 6 views documented | PASS |
| All 29 sequences documented | PASS |
| All 11 packages listed with dependencies | PASS |
| All 6 triggers listed with affected tables | PASS |
| PII fields identified across all tables | PASS |
| Known code bugs documented | PASS |
| DB connection attempted and outcome stated | PASS |
| Extraction method (CODE-ONLY) stated in all files | PASS |

### Key Findings — Critical Items for Downstream Agents

The following are the most significant findings from this extraction, ranked by downstream impact:

**CRITICAL — Security:**
1. AES-256 encryption key hard-coded in `PKG_SECURITY` as a string literal (`HR$ystem_3ncrypt10n_K3y_2024!!`). All encrypted SSN and bank account data is at risk if the source code is exposed.
2. MD5 password hashing. MD5 is cryptographically broken for password storage.
3. SQL injection in `PKG_EMPLOYEE.search_employees` — dynamic SQL built by string concatenation of user-supplied `p_last_name` and `p_first_name` parameters.
4. No account lockout after failed logins.
5. FTP credentials stored in cleartext in `SYSTEM_PARAMETERS` table.

**CRITICAL — Data Integrity:**
6. `TRG_EMP_BEFORE_UPDATE` references wrong column names for `EMPLOYEE_HISTORY` (uses `HISTORY_ID`, `CHANGE_DATE` instead of DDL-defined `HIST_ID`, `EFFECTIVE_DATE`). Trigger raises `ORA-00904` at runtime — employee change history is likely empty.
7. `PKG_EMPLOYEE.generate_emp_number` uses `MAX(EMP_NUMBER)+1` instead of `SEQ_EMP_NUMBER` — race condition under concurrent inserts can produce duplicate employee numbers.
8. `VW_LEAVE_SUMMARY.AVAILABLE` omits `PENDING_DAYS` from its formula — overstates available leave balance for employees with pending requests.

**HIGH — Payroll:**
9. 2024 US federal tax brackets hard-coded in `PKG_PAYROLL`. `TAX_BRACKETS` table exists but is unused. Payroll calculations become incorrect starting 2025 without a code change.
10. `YTD_GROSS` and `YTD_NET` in `PAYROLL_DETAILS` are always written as `0` — YTD accumulation not implemented.
11. `PKG_PAYROLL.reverse_payroll` has no status check — any run in any status can be reversed.

**HIGH — Architecture:**
12. Circular package dependency: `PKG_EMPLOYEE` calls `PKG_PAYROLL.create_salary_record`; `PKG_PAYROLL` references `PKG_EMPLOYEE`. Oracle tolerates this at runtime but it must be restructured before migrating to any other platform.
13. Full Oracle Forms UI — no web tier. Any migration requires a complete UI rewrite.

**MEDIUM — Leave:**
14. `PKG_LEAVE.expire_carryover` double-expire bug — running the procedure twice deducts carryover twice.
15. `PKG_COMMON.business_days_between` does not exclude public holidays; `PKG_LEAVE.calculate_business_days` does. Two divergent business-day calculations exist in the system.

---

## Confidence Assessment

| Output File | Confidence | Basis |
|---|---|---|
| schema-catalogue.json | HIGH (0.95) | Full DDL source files present |
| erd.md | HIGH (0.95) | FK constraints explicit in DDL |
| data-source-inventory.json | HIGH (0.90) | UTL_FILE/UTL_SMTP usage confirmed in package bodies |
| data-flow-map.md | HIGH (0.90) | Package bodies fully read |
| pii-inventory.json | HIGH (0.95) | DDL column notes and encryption package confirmed |
| data-quality-report.md | HIGH (0.95) | Bugs noted in source file comments confirmed by code |
| migration-complexity.json | HIGH (0.90) | Oracle-specific constructs confirmed by code |
| hidden-business-rules.json | HIGH (0.95) | All rules traced to specific package/trigger lines |
| storage-pattern-analysis.md | HIGH (0.90) | Storage mechanisms confirmed in code |
| redundancy-analysis.json | HIGH (0.90) | Redundancies confirmed across DDL + package bodies |
| data-dictionary.md | HIGH (0.90) | Combined DDL + seed data + package bodies |
| conceptual-data-model.md | MEDIUM (0.85) | Business intent inferred from code; no BRD available |
| access-control-matrix.md | HIGH (0.95) | PKG_SECURITY code fully analysed |

**Overall extraction confidence: HIGH (0.92)**

Confidence would increase to 0.98+ with live Oracle connection (row counts, actual constraint validation, index statistics, runtime session context values).

---

*DA Agent 1 extraction complete. 13 output files written to `da-outputs/`. This file is the Phase 4 summary.*
