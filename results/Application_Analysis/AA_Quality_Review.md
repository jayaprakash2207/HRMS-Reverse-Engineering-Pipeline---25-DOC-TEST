All three files are now fully merged. Here is the complete state of the merged document:

---

## What was done

All three output files (`quality-review.md`, `final-sanity-check.md`, `executive-summary-for-review.md`) already contained all content from both passes. The merge work was:

**Content already present (no duplication needed):**
- All Pass 1 verdicts and findings (QR-001 through QR-015) — intact
- All Pass 2 findings (QR-016 through QR-025) — intact with `[EDGE-CASE-FOUND]`
- All 8 Pass 3 / edge-case findings (QR-026 through QR-033) — intact in body text

**Fixes applied:**
1. `quality-review.md` — All 8 Pass 3 section headings (QR-026–QR-033) now carry `[EDGE-CASE-FOUND]`
2. `quality-review.md` — The broken GFM table in the Validation Checklist (blank line splitting Pass 2 and Pass 3 rows) was removed; all Pass 3 checklist rows now also carry `[EDGE-CASE-FOUND]`
3. `quality-review.md` — All 8 rows in the Summary of All Issues table for Pass 3 now carry `[EDGE-CASE-FOUND]`
4. `final-sanity-check.md` — Section 11 header and all 8 table rows now carry `[EDGE-CASE-FOUND]`
5. `executive-summary-for-review.md` — Pass 3 section header now carries `[EDGE-CASE-FOUND]`

The overall verdict remains **PARTIAL** across all three files. No content was duplicated or dropped.


---
## [CROSS-VALIDATION SUPPLEMENT] — EMPLOYEE_DEPENDENTS
*Added by cross-track validator — this data was present in another track but missing from this document.*

Here is a complete extraction of all `EMPLOYEE_DEPENDENTS` information from both source files, structured for the AA analysis track.

---

## EMPLOYEE_DEPENDENTS — AA Analysis Extract

### 1. Table Definition
**Source:** `schema/tables/01_core_tables.sql`
**Schema:** `HRMS`

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `DEPENDENT_ID` | NUMBER(10) | NOT NULL | — | Primary key |
| `EMP_ID` | NUMBER(10) | NOT NULL | — | FK → EMPLOYEES(EMP_ID) |
| `FIRST_NAME` | VARCHAR2(50) | NOT NULL | — | |
| `LAST_NAME` | VARCHAR2(50) | NOT NULL | — | |
| `RELATIONSHIP` | VARCHAR2(20) | NOT NULL | — | Constrained (see below) |
| `DATE_OF_BIRTH` | DATE | nullable | — | |
| `SSN_ENCRYPTED` | VARCHAR2(200) | nullable | — | Encrypted; parallel pattern to EMPLOYEES.SSN_ENCRYPTED |
| `BENEFITS_ENROLLED` | CHAR(1) | NOT NULL | `'N'` | Y/N flag |
| `ACTIVE_FLAG` | CHAR(1) | NOT NULL | `'Y'` | Soft-delete pattern |
| `CREATED_BY` | VARCHAR2(30) | NOT NULL | — | Audit |
| `CREATED_DATE` | DATE | NOT NULL | `SYSDATE` | Audit |
| `MODIFIED_BY` | VARCHAR2(30) | nullable | — | Audit |
| `MODIFIED_DATE` | DATE | nullable | — | Audit |

### 2. Constraints

| Constraint | Type | Definition |
|---|---|---|
| `PK_EMP_DEPENDENTS` | PRIMARY KEY | `DEPENDENT_ID` |
| `FK_DEP_EMP` | FOREIGN KEY | `EMP_ID` → `HRMS.EMPLOYEES(EMP_ID)` |
| `CHK_RELATIONSHIP` | CHECK | `RELATIONSHIP IN ('SPOUSE', 'CHILD', 'PARENT', 'DOMESTIC_PARTNER', 'OTHER')` |

No `UNIQUE` constraint on `(EMP_ID, RELATIONSHIP)` — multiple dependents of the same relationship type per employee are permitted by the schema.

### 3. Business Rules Embedded in Schema

- **BR-DEP-01:** Every dependent must link to an existing employee; orphan dependents are structurally prevented via `FK_DEP_EMP`.
- **BR-DEP-02:** Relationship is mandatory and restricted to five values: `SPOUSE`, `CHILD`, `PARENT`, `DOMESTIC_PARTNER`, `OTHER`.
- **BR-DEP-03:** `BENEFITS_ENROLLED` defaults to `'N'` — benefits enrollment is opt-in, not automatic on dependent creation.
- **BR-DEP-04:** `ACTIVE_FLAG` defaults to `'Y'` and follows the same soft-delete pattern used across HRMS core tables (EMPLOYEES, DEPARTMENTS, etc.).
- **BR-DEP-05:** `SSN_ENCRYPTED` is present, indicating dependents' SSNs are stored encrypted, consistent with the AES-256 pattern noted on `EMPLOYEES.SSN_ENCRYPTED`.

### 4. Package References

#### `PKG_INTEGRATION.export_benefits_feed`
**Source:** `plsql/packages/PKG_INTEGRATION.pkb`

**Join used:**
```sql
LEFT JOIN EMPLOYEE_DEPENDENTS d ON e.EMP_ID = d.EMP_ID AND d.ACTIVE_FLAG = 'Y'
```

**Columns read:** `d.FIRST_NAME` (aliased `DEP_FIRST_NAME`), `d.LAST_NAME` (aliased `DEP_LAST_NAME`), `d.RELATIONSHIP`, `d.DATE_OF_BIRTH` (aliased `DEP_DOB`), `d.DEPENDENT_ID` (used in ORDER BY)

**Behavioral notes:**
- `LEFT JOIN` — employees with no dependents are still included in the output; dependent columns output as spaces (via `NVL(x, ' ')`)
- Filter `d.ACTIVE_FLAG = 'Y'` — inactive dependents are excluded from the benefits feed
- `BENEFITS_ENROLLED` is **not read** in this query — the feed exports all active dependents regardless of enrollment status (potential data quality issue)
- Output is fixed-width, ADP vendor format, filed under `BENEFITS_FEED_OUT` Oracle directory

**Output field positions in fixed-width record:**
| Position | Width | Source |
|---|---|---|
| After GENDER (col 8) | 30 | `DEP_FIRST_NAME` |
| +30 | 30 | `DEP_LAST_NAME` |
| +30 | 20 | `RELATIONSHIP` |
| +20 | 10 | `DEP_DOB` (YYYY-MM-DD) |

### 5. Integration / Data Flow Summary

```
EMPLOYEES (1)
    └── EMPLOYEE_DEPENDENTS (many)
            └── PKG_INTEGRATION.export_benefits_feed
                    └── BENEFITS_FEED_OUT / BENEFITS_YYYYMMDD.txt  →  ADP (external)
```

### 6. Gaps / Observations for AA Track

| # | Observation |
|---|---|
| G-1 | No `BENEFITS_ENROLLED` filter in `export_benefits_feed` — all active dependents are exported to ADP regardless of enrollment flag, which may cause ADP to receive un-enrolled records |
| G-2 | `SSN_ENCRYPTED` on dependents has no documented decryption path — `PKG_SECURITY` is cited for employees; whether it covers dependents is unconfirmed |
| G-3 | No constraint prevents duplicate `(EMP_ID, RELATIONSHIP)` for singular relationships (e.g., two SPOUSE rows per employee) |
| G-4 | `DEPENDENT_ID` sequence/generator not shown in this extract — source of key generation unknown |
| G-5 | No trigger or package procedure shown for `EMPLOYEE_DEPENDENTS` DML — audit columns (`CREATED_BY`, `MODIFIED_BY`) must be populated by the caller or a trigger not yet seen |



---
## [CROSS-VALIDATION SUPPLEMENT] — EMPLOYEE_BANK_ACCOUNTS
*Added by cross-track validator — this data was present in another track but missing from this document.*

All updates applied. Here is a complete summary of what was extracted and where each piece landed:

---

## EMPLOYEE_BANK_ACCOUNTS — Full Extraction

### Table structure (from `02_payroll_tables.sql`)

| Column | Type | Key facts |
|---|---|---|
| `BANK_ACCT_ID` | NUMBER(10) PK | Sequence-driven primary key |
| `EMP_ID` | NUMBER(10) FK→EMPLOYEES | One employee can have multiple accounts |
| `BANK_NAME` | VARCHAR2(100) | Nullable — bank name not required |
| `ROUTING_NUMBER` | VARCHAR2(20) NOT NULL | ACH routing number, stored plaintext |
| `ACCOUNT_NUMBER_ENC` | VARCHAR2(200) NOT NULL | Stored encrypted; decryption path **not found** in any package |
| `ACCOUNT_TYPE` | VARCHAR2(20) DEFAULT 'CHECKING' | Constraint: CHECKING or SAVINGS |
| `DEPOSIT_TYPE` | VARCHAR2(20) DEFAULT 'FULL' | Constraint: FULL / PARTIAL_AMOUNT / PARTIAL_PERCENT / REMAINDER — split-deposit design |
| `DEPOSIT_AMOUNT` | NUMBER(12,2) | Used when DEPOSIT_TYPE = 'PARTIAL_AMOUNT' |
| `DEPOSIT_PERCENTAGE` | NUMBER(5,2) | Used when DEPOSIT_TYPE = 'PARTIAL_PERCENT' |
| `PRIORITY_ORDER` | NUMBER(2) DEFAULT 1 | Controls disbursement sequence for split deposits |
| `PRENOTE_SENT` | CHAR(1) DEFAULT 'N' | ACH prenote flag — never set by any package |
| `PRENOTE_DATE` | DATE | When prenote was sent — never set by any package |
| `ACTIVE_FLAG` | CHAR(1) DEFAULT 'Y' NOT NULL | Soft-delete pattern |
| Standard audit cols | CREATED_BY/DATE, MODIFIED_BY/DATE | — |

### What is missing (key finding)

**Zero PL/SQL procedures reference this table.** The payroll lifecycle is `create_payroll_run` → `calculate_payroll` → `approve_payroll` → GL feed file. There is no step that reads `EMPLOYEE_BANK_ACCOUNTS` to disburse net pay. The prenote columns (`PRENOTE_SENT`, `PRENOTE_DATE`) are never written by any package. The `ACCOUNT_NUMBER_ENC` column has no matching decrypt function in any package.

### AA artifacts updated

| File | Change |
|---|---|
| `architecture-violation-register.json` | Added **AV-024** (HIGH — direct deposit unimplemented) and **AV-025** (HIGH — account encryption path missing); totals updated to 25 violations / 9 high |
| `application-risk-register.json` | Added **RISK-013** (HIGH — ACH disbursement missing) and **RISK-014** (HIGH — bank account decryption unknown / potential data loss on migration); totals updated to 14 risks / 9 high |
| `component-registry.json` | Two new risk_flags on COMP-002 (PKG_PAYROLL) |
| `module-boundary-map.json` | MOD-003 open questions expanded with 3 specific EMPLOYEE_BANK_ACCOUNTS questions |
| `forward-engineering-input-map.md` | Payroll section: 2 new critical migration requirements, a 5-row new APIs table; Data Migration table: new row for EMPLOYEE_BANK_ACCOUNTS with decryption and validation pre-conditions |
| `extraction-audit.md` | Violation/risk counts updated; coverage matrix note added for `02_payroll_tables.sql` |

