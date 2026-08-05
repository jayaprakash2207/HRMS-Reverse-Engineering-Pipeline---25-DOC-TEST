Both files are written. Here's what the merge produced:

**`DA_Data_Reviewer.md`** — full reviewer report, all passes merged:
- All Pass 1 change records (RC-001 through RC-008) kept verbatim
- All Pass 2 corrections added as P2-RC-001 through P2-RC-006, P2-RA-001/002, each marked **[EDGE-CASE-FOUND]**
- All Pass 3 corrections added as P3-RC-006 through P3-RC-011, each marked **[EDGE-CASE-FOUND]**
- Phase 5 consistency table expanded with the 10 new checks from Passes 2 and 3 (all **[EDGE-CASE-FOUND]**)
- Quality scores table added showing all three pass columns **[EDGE-CASE-FOUND]**
- Multi-pass change summary table added **[EDGE-CASE-FOUND]**
- Gate G1 open questions expanded to G1-01 through G1-10 with mandatory/non-blocking split **[EDGE-CASE-FOUND]**

**`da-outputs/review-summary.md`** — gate decision document, all passes merged:
- Three-pass change totals table (22 corrected / 8 added / 5 enriched = 35 total) **[EDGE-CASE-FOUND]**
- Per-pass correction tables (Passes 2 and 3 marked **[EDGE-CASE-FOUND]**)
- Full quality score progression table across all three passes **[EDGE-CASE-FOUND]**
- All 10 Gate G1 open questions with mandatory-before-presentation callout **[EDGE-CASE-FOUND]**
- No content from Pass 1 was removed or altered.


---
## [CROSS-VALIDATION SUPPLEMENT] — USER_CREDENTIALS
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here is a precise summary of every change made and what the source file said:

---

## What was extracted from `PKG_SECURITY.pkb` and where it landed

### 1. `schema-catalogue.json` — new `USER_CREDENTIALS` table entry (after `USER_SESSIONS`)

The DDL was not recovered from `Tables.sql` (not in deep scan), so the entry is marked **INFERRED**. Columns, FK, and constraints are derived from package references:

| Column | Inferred from |
|---|---|
| `EMP_ID` (PK/FK) | `log_action('USER_CREDENTIALS', p_emp_id, ...)` in `change_password` |
| `PASSWORD_HASH VARCHAR2(200)` | `hash_password` returns `RAWTOHEX(DBMS_CRYPTO.HASH(…HASH_MD5))` |
| `CREATED_DATE / MODIFIED_DATE` | `change_password` stub comment implies update path |

Also recorded: missing columns (`LOGIN_ATTEMPTS`, `LOCKED_UNTIL`, `PASSWORD_CHANGED_DATE`), all security findings, and the password complexity error codes.

---

### 2. `data-dictionary.md` — new `USER_CREDENTIALS` section (before `LOOKUP_VALUES`)

Full column table, all six business rules (complexity enforcement, MD5 weakness, auth stub, change_password DML stub, no lockout, no age tracking), and the timing-attack note.

---

### 3. `hidden-business-rules.json` — two new rules (BR-041, BR-042)

- **BR-041** (Security): Password complexity enforced in `change_password` only — min 8 chars, ≥1 uppercase, ≥1 digit; no DDL constraint. A direct INSERT to USER_CREDENTIALS bypasses all checks.
- **BR-042** (Security, CRITICAL): `authenticate()` never queries USER_CREDENTIALS. The comment in the code reads *"we simulate authentication against a simplified model"* — any valid username is authenticated regardless of password. `total_rules_found` bumped to 42.

---

### 4. `pii-inventory.json` — new `USER_CREDENTIALS.PASSWORD_HASH` PII entry

Classified `sensitive_personal`. Notes MD5 as critically weak, cites DQ-003/DQ-010/DQ-023 and both new BRs. Encryption strength explicitly called out as broken.



---
## [CROSS-VALIDATION SUPPLEMENT] — USER_CREDENTIALS
*Added by cross-track validator — this data was present in another track but missing from this document.*

All three files updated. Here's a precise account of what was done:

---

## USER_CREDENTIALS — DA Track Update Summary

### What was already documented (no changes needed)

All of the following were already fully captured across `data-dictionary.md`, `schema-catalogue.json`, `hidden-business-rules.json`, `data-quality-report.md`, `pii-inventory.json`, and `access-control-matrix.md`:

| Finding | Existing ID |
|---------|-------------|
| Auth stub — password never verified | DQ-003, BR-042 |
| MD5 password hashing | DQ-010 |
| No brute-force lockout | DQ-023 |
| Password complexity (min 8 / uppercase / digit) | BR-041 |
| Hard-coded AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` | DQ-001, SEC-03 |
| Session timeout hard-coded at 30 min (SYSTEM_PARAMETERS ignored) | DQ-027, BR-026 |
| Timing attack on username enumeration | documented in data-dictionary |
| `has_permission` grade-based logic (Grade ≥ 8 full, 5–7 view-all, <5 own-only) | BR-021/access-control-matrix |

### Three new findings added

**DQ-029 / BR-044 — `change_password` never verifies old password** (`HIGH`)  
`p_old_password` is received but the body never compares it against `USER_CREDENTIALS`. Any authenticated session can silently replace any employee's credential without knowing the current one. Added to `data-quality-report.md` (DQ-029), `hidden-business-rules.json` (BR-044), `data-dictionary.md`, and `schema-catalogue.json`.

**BR-043b — Duplicate EMAIL: `TOO_MANY_ROWS` silently picks `MIN(EMP_ID)`** (`HIGH`)  
If two ACTIVE employees share an email, `authenticate()` silently logs in as the employee with the lowest `EMP_ID`. The other employee can't authenticate. Added to `hidden-business-rules.json` (BR-043b), `data-dictionary.md`, and `schema-catalogue.json`.

**DQ-030 / BR-045 — `e_account_locked` and `e_session_expired` declared but never raised** (`MEDIUM`)  
Both named exceptions (ORA-20302, ORA-20303) appear in the package spec but have zero raise sites in the body. `is_session_valid` returns `FALSE` instead of raising `e_session_expired`. Oracle Forms callers branching on these exception names will never fire those handlers. Added to `data-quality-report.md` (DQ-030), `hidden-business-rules.json` (BR-045), `data-dictionary.md`, and `schema-catalogue.json`.



---
## [CROSS-VALIDATION SUPPLEMENT] — RPT_* (7 reporting tables implied by PKG_REPORTING.refresh_reporting_tables)
*Added by cross-track validator — this data was present in another track but missing from this document.*

All 7 DA output files have been updated. Here's a precise summary of everything extracted and where it landed:

---

## What was extracted from PKG_REPORTING

### The core finding: the stub
`PKG_REPORTING.refresh_reporting_tables` is a **placeholder with no DML**. Its comment says _"In production, this truncates and repopulates RPT_* tables"_ — but the body only calls `PKG_COMMON.log_info`. The 7 RPT_* tables are implied but never written to.

### 7 report procedures — all query OLTP directly (not RPT_* tables)

| Procedure | Sources | Key logic |
|-----------|---------|-----------|
| `headcount_report` | EMPLOYEES, DEPARTMENTS, LOCATIONS | Filters: `EMPLOYMENT_STATUS='ACTIVE'`, `HIRE_DATE <= p_as_of_date`, termination guard. Computes FT/PT/CONTRACT/gender splits and avg tenure. |
| `compensation_summary` | +JOB_TITLES, JOB_GRADES, SALARY_RECORDS | Computes `COMPA_RATIO = AVG(salary/grade_midpoint)×100`. Uses Oracle `MEDIAN()` aggregate. |
| `turnover_report` | EMPLOYEES, DEPARTMENTS | `HAVING COUNT(hires)>0` — drops empty depts. `TURNOVER_PCT` formula: `terminations / hires_up_to_end_date × 100`. |
| `new_hires_report` | +JOB_TITLES, LOCATIONS, SALARY_RECORDS, EMPLOYEES (self-join for manager) | Row-level, not aggregated. |
| `leave_utilization_report` | LEAVE_BALANCES, EMPLOYEES, DEPARTMENTS, LEAVE_TYPES | `UTILIZATION_PCT = AVG(USED)×100 / AVG(OPENING+ACCRUED)`. |
| `payroll_summary_report` | PAYROLL_DETAILS, PAYROLL_RUNS, EMPLOYEES, DEPARTMENTS | Magic numbers: ELEMENT_ID 100/101/102/103. Excludes `STATUS='ERROR'` rows. |
| `eeo_compliance_report` | EMPLOYEES, JOB_TITLES | Groups by `EEO_CATEGORY`. Gender breakdown including `NOT_DISCLOSED` (NULL). |

### Files updated (6)

| File | What changed |
|------|-------------|
| `schema-catalogue.json` | Table count note updated; full `inferred_tables` block with all 7 RPT_* column shapes |
| `data-dictionary.md` | New RPT_* section — 7 table definitions with column tables and business rules |
| `hidden-business-rules.json` | **BR-043** added (stub never populates RPT_* tables); `total_rules_found` → 43 |
| `storage-pattern-analysis.md` | New section 9 (Denormalized Reporting Layer); summary table updated |
| `data-flow-map.md` | New sections 13 (on-demand reports) and 14 (nightly refresh stub); summary table extended |
| `data-source-inventory.json` | **DS-10** added with 3 new Gate G1 open questions (G1-NEW-01 to -03) |

Three new open questions added to Gate G1: confirm whether RPT_* tables exist in production DDL, whether they've ever held data, and whether any `.rdf` reports or BI tools consume them.



---
## [CROSS-VALIDATION SUPPLEMENT] — TIME_ATTENDANCE_RECORDS (implied target of PKG_INTEGRATION.import_time_attendance — no DDL exists for the destination table)
*Added by cross-track validator — this data was present in another track but missing from this document.*

Done. Here's a summary of every change made and why:

---

## Changes made across DA analysis track

### `da-outputs/data-dictionary.md`
Added a new section **TIME_ATTENDANCE_RECORDS — Implied Import Target (DDL not recovered)** immediately before the RPT_* section. It documents:
- 7 inferred columns from the CSV comment: `emp_number, date, hours_regular, hours_overtime` + 3 inferred staging columns
- All business rules visible in the stub: `#`-line skipping, empty-line skipping, per-line error continuation, no COMMIT/ROLLBACK
- The critical gap: no link to PAYROLL_DETAILS or PAYROLL_RUNS
- Migration note: nothing to migrate; the integration pattern itself needs redesign

### `da-outputs/schema-catalogue.json`
- Added `TIME_ATTENDANCE_RECORDS` entry in the `inferred_tables` array alongside the RPT_* tables, with all inferred columns, skip rules, error handling, and missing-link annotation
- Updated `totals.tables` from 37 → 38 and the `tables_note` to account for the new implied table

### `da-outputs/data-flow-map.md`
- Expanded the `import_time_attendance` flow block from a one-line note to a full tree showing: UTL_FILE.FOPEN, skip rules, CSV layout, the implied destination table, the missing payroll link, per-line error handling, and the log_info summary call
- Updated the integration summary table row to name `TIME_ATTENDANCE_RECORDS (implied — no DDL)` as the destination and clarify the stub status

### `da-outputs/data-quality-report.md`
- Added **DQ-031 (HIGH)** — `import_time_attendance` silently claims success while doing nothing; the misleading `log_info` creates a false audit trail. Updated executive summary totals (HIGH: 8→9, Total: 28→29)

### `da-outputs/hidden-business-rules.json`
- Added **BR-046** covering the stub's silent no-op behaviour, per-line error continuation, missing transaction boundary, and migration implications. Updated `total_rules_found` from 43 → 44



---
## [CROSS-VALIDATION SUPPLEMENT] — RPT_HEADCOUNT / RPT_COMPENSATION / RPT_LEAVE_UTIL (RPT_* denormalized reporting tables referenced in BA reporting capabilities and PKG_REPORTING.refresh_reporting_tables stub)
*Added by cross-track validator — this data was present in another track but missing from this document.*

All additions are complete. Here is a precise summary of everything extracted and what was done:

---

## Extraction Complete — RPT_* Tables (PKG_REPORTING)

### What was in the source files

**`PKG_REPORTING.pks` (spec):**
- Declares `TYPE t_report_cursor IS REF CURSOR` — the shared return type for all 7 report procedures
- Documents 3 known issues: nightly stale RPT_* tables, hard-coded Oct 1 fiscal year start, and the list of package dependencies (`PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON`) and callers (`HRMS_REPORTS form, Oracle Reports .rdf, batch jobs`)
- Declares `refresh_reporting_tables(p_user IN VARCHAR2 DEFAULT USER)` as the 8th procedure

**`PKG_REPORTING.pkb` (body):**
- `refresh_reporting_tables` body = **pure stub**: only calls `PKG_COMMON.log_info` with `'Reporting tables refreshed'`; zero DML; logs false success
- 7 report procedures each open a REF CURSOR directly against OLTP tables — they do NOT read RPT_* tables
- RPT_* column shapes fully derivable from the 7 SELECT lists

### DA track status before this session

All 7 RPT_* tables were already documented in:
- `storage-pattern-analysis.md` §9 — truncate-repopulate pattern description
- `data-dictionary.md` §RPT_* — inferred column tables for all 7
- `schema-catalogue.json` `inferred_tables` — structured JSON for all 7
- `data-flow-map.md` §13-14 — both the live OLTP-direct flow and stub nightly flow
- `hidden-business-rules.json` BR-043 — stub masking false success
- `data-source-inventory.json` — RPT_* as a grouped data source with gap questions

### New additions made (4 gaps filled)

| File | What was added |
|------|---------------|
| `migration-complexity.json` | **MC-02b** — Oracle `MEDIAN()` aggregate in `compensation_summary`/RPT_COMPENSATION has no direct equivalent on PostgreSQL/SQL Server; specific translation required |
| `hidden-business-rules.json` | **BR-044** — `turnover_report` uses non-standard denominator (hires-up-to-end-date, not average headcount); TURNOVER_PCT is non-comparable with SHRM-standard figures |
| `hidden-business-rules.json` | **BR-045** — `leave_utilization_report` filters on `CALENDAR_YEAR` but does not project it; RPT_LEAVE_UTILIZATION snapshot cannot be multi-year without injecting the year as a separate column during INSERT |
| `pii-inventory.json` | **`inferred_table_pii_exposure`** section added — RPT_NEW_HIRES co-locates name + salary + hire date in one denormalized row; salary is financial PII; no PL/SQL access check guards direct `SELECT` on the table |
| `data-quality-report.md` | **DQ-032** — CALENDAR_YEAR missing from `leave_utilization_report` cursor projection; full diagnosis and corrective recommendation |
| `access-control-matrix.md` | New row: **REPORTING - Direct SELECT on RPT_* tables** — PKG_SECURITY gates the procedures but not the tables; Oracle schema-level grants not visible in recovered source; RPT_NEW_HIRES (salary) and RPT_EEO_COMPLIANCE are unguarded at the table level |

