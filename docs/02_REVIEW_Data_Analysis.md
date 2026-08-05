# Human Review — Data Analysis

**Reviewer:** ___________________________
**Date reviewed:** ___________________________
**Sign-off:** ___________________________

**Source files:** `results/Data_Analysis/DA_Data_Reviewer.md`, `results/Data_Analysis/DA_Data_Extractor.md`
**Forward Engineering docs using this:** `07_DATA_MODEL_SPECIFICATION.md`, `08_ERD.md`, `06_DATA_DICTIONARY.md`

---

## 1. Table Count Discrepancy — MUST RESOLVE

| Finding | Value | Reviewer Decision |
|---------|-------|-------------------|
| DA track table count | **30 tables** | |
| TA track table count | **35 tables** | |
| Discrepancy | **5 tables** — which is correct? | **DECIDE:** |

The TA count of 35 may be inflated — TA's own section headings have internal inconsistencies
(e.g. "Core Tables — 6 tables" but 8 rows in the table body). DA's count of 30 is derived
from direct DDL parsing and is likely more reliable.

---

## 2. Core Tables — Verify Existence and Columns

Confirm these 30 tables exist and the column counts are correct:

| Table | AI-Stated Columns | Actual Columns | Status |
|-------|------------------|----------------|--------|
| EMPLOYEES | 18 | | |
| DEPARTMENTS | 8 | | |
| JOB_POSITIONS | 7 | | |
| JOB_GRADES | 6 | | |
| SALARY_RECORDS | 9 | | |
| PAYROLL_RUNS | 10 | | |
| PAYROLL_DETAILS | 11 | | |
| DEDUCTION_TYPES | 7 | | |
| DEDUCTION_RECORDS | 8 | | |
| EMPLOYEE_BANK_ACCOUNTS | 9 | | |
| LEAVE_TYPES | 8 | | |
| LEAVE_BALANCES | 9 | | |
| LEAVE_REQUESTS | 12 | | |
| PERFORMANCE_REVIEWS | 14 | | |
| REVIEW_CYCLES | 8 | | |
| PERFORMANCE_GOALS | 10 | | |
| USER_CREDENTIALS | 10 | | |
| AUDIT_LOG | 9 | | |
| SYSTEM_CONFIG | 5 | | |
| EMPLOYEE_DEPENDENTS | 8 | | |
| EMERGENCY_CONTACTS | 8 | | |
| EMPLOYEE_HISTORY | 11 | **⚠️ COLUMN MISMATCH — see below** | |
| TAX_BRACKETS | 8 | | |
| DOCUMENTS | 7 | | |
| NOTIFICATIONS | 8 | | |
| RPT_HEADCOUNT | AI: exists as view/table | **CONFIRM: view or table?** | |
| RPT_COMPENSATION | AI: exists as view/table | **CONFIRM: view or table?** | |
| RPT_LEAVE_UTIL | AI: exists as view/table | **CONFIRM: view or table?** | |
| TIME_ATTENDANCE_RECORDS | AI: inferred, no DDL found | **CONFIRM: does this table exist?** | |
| VW_LEAVE_SUMMARY | AI: view, not table | | |

---

## 3. EMPLOYEE_HISTORY Column Mismatch — CRITICAL

**This will cause ORA-00904 on every EMPLOYEES UPDATE in production.**

| Source | Columns it references |
|--------|-----------------------|
| DDL (01_core_tables.sql) — **authoritative per DA reviewer** | EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION |
| TRG_EMP_BEFORE_UPDATE (AA component COMP-020) | CHANGE_DATE, OLD_VALUE, NEW_VALUE |

**Reviewer decision:** Which column set is correct for the NEW system?

- [ ] Use DDL columns (EFFECTIVE_DATE, OLD_DEPT_ID, etc.) — typed, queryable
- [ ] Use trigger columns (CHANGE_DATE, OLD_VALUE, NEW_VALUE) — generic, flexible
- [ ] Design new schema: ___________________________

---

## 4. Leave Balance Formula — CONTRADICTION

Two formulas exist for calculating available leave balance:

| Source | Formula |
|--------|---------|
| VW_LEAVE_SUMMARY (view) | `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT` (excludes PENDING) |
| LEAVE_BALANCES.AVAILABLE (virtual column) | `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING` |
| PKG_LEAVE (application logic) | Uses virtual column (includes PENDING) |

**Reviewer decision:** Which formula is the correct "available balance" shown to employees?

- [ ] Include PENDING (subtract pending requests from balance — more conservative)
- [ ] Exclude PENDING (show balance without pending deducted — more permissive)
- [ ] Decision: ___________________________

---

## 5. PII Data Inventory — Verify and Classify

The following PII fields were identified. Confirm classification is correct for GDPR/compliance:

| Table | Column | PII Type | GDPR Category | Reviewer Confirmation |
|-------|--------|----------|--------------|----------------------|
| EMPLOYEES | FIRST_NAME, LAST_NAME | Direct PII | Personal | |
| EMPLOYEES | NATIONAL_ID | Government ID | Sensitive | |
| EMPLOYEES | DATE_OF_BIRTH | Personal | Sensitive | |
| EMPLOYEES | EMAIL, PHONE | Contact | Personal | |
| EMPLOYEES | HOME_ADDRESS | Location | Personal | |
| EMPLOYEE_BANK_ACCOUNTS | BANK_ACCOUNT_NUMBER, ROUTING_NUMBER | Financial | Sensitive | |
| USER_CREDENTIALS | PASSWORD_HASH, SALT | Security | Restricted | |
| EMERGENCY_CONTACTS | NAME, PHONE, RELATIONSHIP | Third-party PII | Personal | |
| EMPLOYEE_DEPENDENTS | FULL_NAME, DATE_OF_BIRTH, RELATIONSHIP | Third-party PII | Sensitive | |
| AUDIT_LOG | USER_ID, IP_ADDRESS | Behavioural | Personal | |
| PAYROLL_DETAILS | NET_PAY, GROSS_PAY | Financial | Sensitive | |
| TAX_BRACKETS | (no PII) | N/A | N/A | |

**Additional PII fields not listed above:** ___________________________

---

## 6. Data Quality Issues — Confirm These Are Real

| Issue | Description | Severity | Reviewer Confirmation |
|-------|------------|----------|-----------------------|
| Encryption key hardcoded | PKG_SECURITY: AES-256 key hardcoded as `'HRMS_AES256_KEY_2024'` | CRITICAL | |
| Race condition in emp number | `generate_emp_number` does SELECT MAX + INSERT without lock — concurrent users could get same number | HIGH | |
| HOURLY salary silently overwritten | PKG_PAYROLL overwrites HOURLY basis with ANNUAL, ignoring actual input | HIGH | |
| Missing NACHA implementation | NACHA direct deposit file generation is not implemented (comments only) | HIGH | |
| TIME_ATTENDANCE_RECORDS missing DDL | PKG_INTEGRATION imports time data but destination table has no DDL | MEDIUM | |

---

## 7. Data Dictionary Review

Open [results/ForwardEngineering_Docs/06_DATA_DICTIONARY.md](../results/ForwardEngineering_Docs/06_DATA_DICTIONARY.md):

| Section | Complete? | Accurate? | Reviewer Notes |
|---------|-----------|-----------|----------------|
| All 30 tables documented | | | |
| Column descriptions accurate | | | |
| Business rules on columns correct | | | |
| FK relationships correct | | | |

---

## 8. Open Questions for Data Architect

1. Do the RPT_* tables exist as physical tables or are they views? (Source code only shows a stub procedure `refresh_reporting_tables`.)
2. Does TIME_ATTENDANCE_RECORDS have a DDL somewhere not captured in the 42 source files?
3. Is EMPLOYEE_HISTORY used in any reporting queries that must be preserved?
4. Are there any Oracle sequences, packages, or functions not included in the 42 source files?
5. What is the Oracle DB version? (Affects migration tooling choice.)
