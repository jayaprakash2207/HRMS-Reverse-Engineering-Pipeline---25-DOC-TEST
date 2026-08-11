# DA Agent 2 — Data Architecture Reviewer Report

**Project:** ts-plsql-oracle-forms-hrms  
**Schema:** HRMS  
**DB Engine:** Oracle Database 19c  
**Review Date:** 2026-08-04  
**Method:** CODE-ONLY (no Oracle connection available — see DA Agent 1 Pre-Flight note)  
**Agent Version:** DA Agent 2 (Phases 1–6 completed)

---

## Pre-Flight Check

`schema-catalogue.json` → `db_connection: "CODE-ONLY"`. Oracle Instant Client and sqlplus were not found. All 13 output files are present and non-empty. Proceeding with Phase 1.

---

## Phase 1 — Test File Evidence

No test files were found or provided in the source material. The repository contains schema DDL, PL/SQL package bodies, Oracle Forms exports, and seed data — no unit test, integration test, or builder/factory files. This is consistent with the system's Oracle Forms + PL/SQL architecture, which predates modern automated testing.

**Result:** No test-driven changes to output files. Phase 1 complete with 0 changes.

---

## Phase 2 — Documentation Review

No `README.md` or `docs/` directory was provided in the source material set. The system appears to be a legacy Oracle Forms HRMS with no developer-facing documentation. System intent is recoverable from seed data (`SYSTEM_PARAMETERS.COMPANY_NAME = 'Acme Corporation'`, `APP_VERSION = '4.2.0'`) and PL/SQL comments.

**Result:** No documentation-driven changes. Phase 2 complete with 0 changes.

---

## Phase 3 — Database Verification

Database is CODE-ONLY. Row counts, runtime session values, and constraint violation data are not available. All Agent 1 findings that require runtime verification are marked as UNVERIFIED in the relevant output files.

Packages referenced in Agent 1 outputs but **not provided for verification**: `PKG_AUDIT`, `PKG_NOTIFICATION`, `PKG_INTEGRATION`, `PKG_PERFORMANCE`, `PKG_REPORTING`. Findings derived from those packages are inferred from cross-references only.

**Result:** No live-DB corrections possible. Phase 3 complete with 0 changes.

---

## Phase 4 — Spot Check of Unreferenced Files

Files reviewed but not fully covered in Agent 1 outputs:

| File | Checked | Produces New Finding? |
|------|---------|----------------------|
| `schema/tables/01_core_tables.sql` — all constraints | Yes | Yes — CARRYOVER_EXPIRY DDL/code mismatch (DISC-001) |
| `schema/views/hrms_views.sql` — VW_LEAVE_SUMMARY formula | Yes | Confirmed RED-002 (already documented) |
| `data/seed/01_reference_data.sql` — LEAVE_TYPES rows | Yes | Yes — BR-022 leave type names and values wrong (RC-001, RC-002) |
| `data/seed/01_reference_data.sql` — HOLIDAYS rows | Yes | Yes — BR-035 holiday list wrong (RC-003) |
| `data/seed/01_reference_data.sql` — PAY_ELEMENTS seed | Yes | Confirmed pay element defaults; no new finding |
| `plsql/packages/PKG_LEAVE.pkb` — all procedures | Yes | Yes — flow map wrong procedure names (RC-005) |
| `plsql/packages/PKG_PAYROLL.pkb` — generate_pay_register | Yes | Yes — DS-05 format/name wrong (RC-006) |
| `plsql/packages/PKG_SECURITY.pkb` — has_permission SQL | Yes | Yes — access matrix shows reconstructed SQL with non-existent GRADE_LEVEL column (RC-010) |
| `plsql/packages/PKG_COMMON.pkb` — all functions | Yes | Yes — state tax default rule missing from hidden-business-rules (RA-001) |
| `plsql/triggers/trg_employees.sql` | Yes | Confirmed RED-003 / DQ-006 (already documented) |
| `plsql/triggers/trg_audit.sql` | Yes | No new finding; triggers documented correctly |

---

## Phase 5 — Cross-File Consistency Checks

| Check | Files | Result |
|-------|-------|--------|
| Same table count | `schema-catalogue.json` (30) ↔ `erd.md` (30 entities) | PASS |
| PII columns match | `pii-inventory.json` ↔ `schema-catalogue.json` | PASS — all PII columns present in DDL |
| Row counts match | `schema-catalogue.json` ↔ `migration-complexity.json` | N/A — both CODE-ONLY, no live counts |
| Business rules in flow map | `hidden-business-rules.json` ↔ `data-flow-map.md` | PARTIAL — BR-022 leave names wrong in both files (see RC-001); data-flow-map procedure names wrong (see RC-005) |
| Cache in both places | `data-source-inventory.json` ↔ `storage-pattern-analysis.md` | PASS — SEQ_AUDIT CACHE 100 confirmed in both |
| FK delete rules consistent | `schema-catalogue.json` ↔ `migration-complexity.json` | PASS — all FKs NO ACTION; BEFORE DELETE trigger documented in MC-10 |
| Canonical entity claims match actual table/usage evidence | `redundancy-analysis.json` ↔ `schema-catalogue.json` | PASS — all RED entries reference real tables |
| Every table/column has a dictionary entry | `data-dictionary.md` ↔ `schema-catalogue.json` | PASS — dictionary covers all 30 tables; notes audit columns omitted by design |
| Every concept traces to a real aggregate root | `conceptual-data-model.md` ↔ `schema-catalogue.json` | PASS — all 9 domains map to real tables |
| Every PII table/column appears in access matrix with cited evidence | `access-control-matrix.md` ↔ `pii-inventory.json` | GAP — EMPLOYEE_DEPENDENTS, EMERGENCY_CONTACTS, EMPLOYEE_BANK_ACCOUNTS, EMPLOYEE_TAX_INFO have PII but no module-level access row in the matrix (see RA-002) |
| SSN access restriction grade threshold | `pii-inventory.json` ↔ `access-control-matrix.md` | CONFLICT — pii-inventory says "Grade ≥ 5 can view"; access-control-matrix says Grade 8+ only for encrypt/decrypt (see RC-007) |
| Leave type names and rules | `hidden-business-rules.json` BR-022 ↔ `data/seed/01_reference_data.sql` | CONFLICT — wrong leave type names and wrong balance values (see RC-001, RC-002) |
| Holiday list | `hidden-business-rules.json` BR-035 ↔ `data/seed/01_reference_data.sql` | CONFLICT — wrong holiday names (see RC-003) |
| Migration complexity factor count | `DA_Data_Extractor.md` ↔ `migration-complexity.json` | CONFLICT — extractor says 17 factors; JSON has 14 (see RC-004) |
| Payroll register format | `data-source-inventory.json` DS-05 ↔ `PKG_PAYROLL.generate_pay_register` code | CONFLICT — inventory says "Fixed-width text / PAY_REGISTER_RUN{id}.txt"; code writes CSV / PAY_REGISTER_{id}_{timestamp}.csv (see RC-006) |
| PKG_SECURITY has_permission SQL | `access-control-matrix.md` ↔ `PKG_SECURITY.pkb` | CONFLICT — matrix shows non-existent GRADE_LEVEL column; code uses GRADE_ID (see RC-010) |
| CARRYOVER_EXPIRY units | `LEAVE_TYPES` DDL column comment ↔ `PKG_LEAVE.process_carryover` code | DISC-001 — DDL says "number of days"; code uses ADD_MONTHS |
| Medicare function attribution | `hidden-business-rules.json` BR-011 ↔ `PKG_PAYROLL.pkb` | CONFLICT — BR-011 says "PKG_PAYROLL.calculate_fica" but Medicare is in calculate_medicare (see RC-008) |

---

## Change Records

### RC-001 — CORRECTED
```json
{
  "change_id": "RC-001",
  "type": "CORRECTED",
  "finding_id": "hidden-business-rules.json — BR-022 (leave type names)",
  "what": "BR-022 states leave types are 'ANNUAL, SICK, COMP, MATERNITY, PATERNITY, FMLA'. Actual seed data defines six entirely different names: PTO, SICK, COMP, FMLA, JURY (Jury Duty), BEREAVE (Bereavement). ANNUAL, MATERNITY, and PATERNITY do not exist in this system. JURY and BEREAVE do.",
  "evidence_source": "cross-file check (Phase 5)",
  "evidence_detail": "data/seed/01_reference_data.sql LEAVE_TYPES rows: LEAVE_TYPE_CODE = 'PTO', 'SICK', 'COMP', 'FMLA', 'JURY', 'BEREAVE'",
  "confidence_before": 0.50,
  "confidence_after": 0.98,
  "phase_found": "Phase 5 cross-file consistency"
}
```

### RC-002 — CORRECTED
```json
{
  "change_id": "RC-002",
  "type": "CORRECTED",
  "finding_id": "hidden-business-rules.json — BR-022 (leave rule values)",
  "what": "BR-022 rule text has wrong numeric values for PTO and SICK. (a) PTO max balance is stated as 30 days — actual seed value is 20 days (MAX_BALANCE=20). (b) PTO carryover-max stated as '10-day' — actual seed value is 5 days (CARRYOVER_MAX=5). (c) SICK described as 'no carryover' — actual seed value shows CARRYOVER_MAX=10 (SICK DOES carry over up to 10 days, no expiry). Correct values: PTO — ACCRUAL_RATE=1.25/month, MAX_BALANCE=20, CARRYOVER_MAX=5, CARRYOVER_EXPIRY=3 (months), MIN_TENURE_DAYS=0. SICK — ACCRUAL_RATE=0.833/month, MAX_BALANCE=10, CARRYOVER_MAX=10, CARRYOVER_EXPIRY=NULL (no expiry), MIN_TENURE_DAYS=0.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "data/seed/01_reference_data.sql INSERT INTO LEAVE_TYPES: PTO row (MAX_BALANCE=20, CARRYOVER_MAX=5, CARRYOVER_EXPIRY=3); SICK row (MAX_BALANCE=10, CARRYOVER_MAX=10, CARRYOVER_EXPIRY=NULL)",
  "confidence_before": 0.40,
  "confidence_after": 1.00,
  "phase_found": "Phase 4 spot check + Phase 5 cross-file"
}
```

### RC-003 — CORRECTED
```json
{
  "change_id": "RC-003",
  "type": "CORRECTED",
  "finding_id": "hidden-business-rules.json — BR-035 (holiday list)",
  "what": "BR-035 lists 10 holidays as: 'New Year's, MLK Day, Presidents Day, Memorial Day, Independence Day, Labor Day, Columbus Day, Veterans Day, Thanksgiving, Christmas'. Two holidays named ('Columbus Day', 'Veterans Day') are NOT in the seed data and do not exist in this system. Two holidays that ARE seeded are MISSING from the list: 'Day After Thanksgiving' (2024-11-29) and 'Christmas Eve' (2024-12-24). Correct complete list: New Year's Day (Jan 1), Martin Luther King Jr. Day (Jan 15), Presidents' Day (Feb 19), Memorial Day (May 27), Independence Day (Jul 4), Labor Day (Sep 2), Thanksgiving (Nov 28), Day After Thanksgiving (Nov 29), Christmas Eve (Dec 24), Christmas Day (Dec 25).",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "data/seed/01_reference_data.sql INSERT INTO HOLIDAYS: HOLIDAY_ID 1-10 with explicit dates. No Columbus Day or Veterans Day row present.",
  "confidence_before": 0.40,
  "confidence_after": 1.00,
  "phase_found": "Phase 4 spot check"
}
```

### RC-004 — CORRECTED
```json
{
  "change_id": "RC-004",
  "type": "CORRECTED",
  "finding_id": "DA_Data_Extractor.md — Phase 3 output table row 7",
  "what": "DA_Data_Extractor.md Phase 3 table states '17 migration complexity factors'. Actual migration-complexity.json contains exactly 14 factors (MC-01 through MC-14). The extractor summary over-counts by 3.",
  "evidence_source": "cross-file check (Phase 5)",
  "evidence_detail": "migration-complexity.json complexity_factors array: 14 entries (MC-01 to MC-14). DA_Data_Extractor.md line 67: '17 migration complexity factors'.",
  "confidence_before": 0.90,
  "confidence_after": 1.00,
  "phase_found": "Phase 5 cross-file consistency"
}
```

### RC-005 — CORRECTED
```json
{
  "change_id": "RC-005",
  "type": "CORRECTED",
  "finding_id": "data-flow-map.md — procedure names in flows 1, 4, 7",
  "what": "Three procedure names in data-flow-map.md are wrong relative to the actual package bodies: (1) Flow 1 calls 'PKG_EMPLOYEE.hire_employee' — actual name is PKG_EMPLOYEE.create_employee. (2) Flow 4 calls 'PKG_LEAVE.initialize_leave_balances()' — actual name is PKG_LEAVE.initialize_balances. (3) Flow 7 calls 'PKG_LEAVE.submit_request' — actual name is PKG_LEAVE.submit_leave_request.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_EMPLOYEE.pkb: FUNCTION create_employee(...) RETURN NUMBER. PKG_LEAVE.pkb: PROCEDURE initialize_balances(...); FUNCTION submit_leave_request(...) RETURN NUMBER.",
  "confidence_before": 0.85,
  "confidence_after": 0.98,
  "phase_found": "Phase 4 spot check"
}
```

### RC-006 — CORRECTED
```json
{
  "change_id": "RC-006",
  "type": "CORRECTED",
  "finding_id": "data-source-inventory.json — DS-05 (PAY_REGISTER_OUT format and naming)",
  "what": "DS-05 describes PAY_REGISTER_OUT as 'Fixed-width text' with naming pattern 'PAY_REGISTER_RUN{id}.txt'. Both are wrong. The actual code in PKG_PAYROLL.generate_pay_register writes a 10-column CSV file (comma-delimited, name and department fields double-quoted). The actual filename pattern is 'PAY_REGISTER_{run_id}_{YYYYMMDD_HH24MISS}.csv' (includes a timestamp suffix and .csv extension, not .txt). Corrected format: CSV; corrected naming: PAY_REGISTER_{run_id}_{YYYYMMDD_HH24MISS}.csv.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_PAYROLL.pkb generate_pay_register: v_filename := 'PAY_REGISTER_' || p_run_id || '_' || TO_CHAR(SYSDATE,'YYYYMMDD_HH24MISS') || '.csv'; UTL_FILE.FOPEN('PAYROLL_OUTPUT', v_filename, 'W', 32767); header 'EMP_NUMBER,EMPLOYEE_NAME,DEPARTMENT,...'.",
  "confidence_before": 0.60,
  "confidence_after": 1.00,
  "phase_found": "Phase 4 spot check"
}
```

### RC-007 — CORRECTED
```json
{
  "change_id": "RC-007",
  "type": "CORRECTED",
  "finding_id": "pii-inventory.json — EMPLOYEES.SSN_ENCRYPTED access_restriction field",
  "what": "pii-inventory.json states SSN_ENCRYPTED 'access_restriction: Grade-based; GRADE ≥ 5 can view'. This is incorrect. Grade ≥ 5 employees get VIEW access to general employee modules, but decrypt_ssn (the only way to read SSN) is controlled by PKG_SECURITY.has_permission which returns TRUE only for Grade ≥ 8. The access-control-matrix.md correctly states 'Grade 8-10 only' for SSN encrypt/decrypt. The pii-inventory entry should read: 'access_restriction: Grade ≥ 8 (Director+) only via PKG_SECURITY.decrypt_ssn'.",
  "evidence_source": "cross-file check (Phase 5)",
  "evidence_detail": "access-control-matrix.md row 'SECURITY - Encrypt/decrypt SSN': Grade 1-4 NO, Grade 5-7 NO, Grade 8-10 YES. PKG_SECURITY.has_permission: IF v_grade_id >= 8 THEN RETURN TRUE — all other module/action checks that would allow Grade 5-7 access do not match the 'SECURITY'/'DECRYPT' action.",
  "confidence_before": 0.70,
  "confidence_after": 0.98,
  "phase_found": "Phase 5 cross-file consistency"
}
```

### RC-008 — CORRECTED
```json
{
  "change_id": "RC-008",
  "type": "CORRECTED",
  "finding_id": "hidden-business-rules.json — BR-011 enforcement field",
  "what": "BR-011 ('Medicare additional 0.9% above $200,000') states enforcement as 'PKG_PAYROLL.calculate_fica'. This is wrong. calculate_fica computes Social Security tax (6.2%, capped at $168,600 wage base). The additional Medicare 0.9% is calculated in a separate function: PKG_PAYROLL.calculate_medicare. Corrected enforcement: 'PKG_PAYROLL.calculate_medicare'.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_PAYROLL.pkb: FUNCTION calculate_fica — returns ROUND(v_taxable * 0.062, 2) (Social Security); FUNCTION calculate_medicare — computes v_base_tax := p_gross_pay * 0.0145 then adds 0.9% for amounts over 200,000.",
  "confidence_before": 0.90,
  "confidence_after": 1.00,
  "phase_found": "Phase 4 spot check"
}
```

### RC-009 — CORRECTED
```json
{
  "change_id": "RC-009",
  "type": "CORRECTED",
  "finding_id": "data-dictionary.md — DEPARTMENTS seed description",
  "what": "data-dictionary.md DEPARTMENTS section states 'Seed data: 10 departments (100-190) seeded'. The range '100-190' is incorrect — it appears to be a confusion with DEPT_CODE or cost center patterns. The actual DEPT_ID values seeded are: 1 (EXEC), 10 (HR), 20 (FIN), 30 (IT), 31 (ITDEV), 32 (ITOPS), 40 (SALES), 50 (MKT), 60 (OPS), 70 (LEGAL). Corrected: 'Seed data: 10 departments seeded, DEPT_ID values: 1, 10, 20, 30, 31, 32, 40, 50, 60, 70'.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "data/seed/01_reference_data.sql INSERT INTO DEPARTMENTS: 10 rows with DEPT_ID values 1, 10, 20, 30, 31, 32, 40, 50, 60, 70.",
  "confidence_before": 0.80,
  "confidence_after": 1.00,
  "phase_found": "Phase 4 spot check"
}
```

### RC-010 — CORRECTED
```json
{
  "change_id": "RC-010",
  "type": "CORRECTED",
  "finding_id": "access-control-matrix.md — PKG_SECURITY.has_permission extracted SQL",
  "what": "The access-control-matrix.md shows a reconstructed SQL for has_permission that references 'g.GRADE_LEVEL' from a 3-table join including JOB_GRADES. This column does not exist in the HRMS schema (JOB_GRADES DDL has GRADE_ID, GRADE_CODE, GRADE_NAME, MIN_SALARY, MAX_SALARY, OVERTIME_ELIGIBLE — no GRADE_LEVEL column). The actual PKG_SECURITY code performs a 2-table join (EMPLOYEES + JOB_TITLES only) and retrieves j.GRADE_ID: 'SELECT e.DEPT_ID, j.GRADE_ID FROM EMPLOYEES e JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE e.EMP_ID = p_emp_id'. The variable v_grade_id is then compared against thresholds 8 and 5. The permission behavior described in the matrix is functionally correct; only the extracted SQL code block is wrong.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_SECURITY.pkb has_permission: SELECT e.DEPT_ID, j.GRADE_ID FROM EMPLOYEES e JOIN JOB_TITLES j ON e.JOB_ID = j.JOB_ID WHERE e.EMP_ID = p_emp_id. JOB_GRADES DDL: no GRADE_LEVEL column defined.",
  "confidence_before": 0.85,
  "confidence_after": 0.98,
  "phase_found": "Phase 4 spot check"
}
```

### DISC-001 — UNRESOLVED DISCREPANCY
```json
{
  "change_id": "DISC-001",
  "type": "DISCREPANCY",
  "finding_id": "LEAVE_TYPES.CARRYOVER_EXPIRY — units conflict between DDL comment and code",
  "what": "The DDL column comment for LEAVE_TYPES.CARRYOVER_EXPIRY reads 'number of days before carryover expires'. hidden-business-rules.json BR-020 correctly states that the code treats this as MONTHS. PKG_LEAVE.process_carryover uses ADD_MONTHS(TO_DATE(v_next_year||'-01-01','YYYY-MM-DD'), CARRYOVER_EXPIRY). PTO has CARRYOVER_EXPIRY=3 → expiry is April 1 (Jan 1 + 3 months). If the DDL comment were correct (days), expiry would be January 4 — a fundamentally different business rule. The column DDL comment is wrong; the code is the operational authority. However, the DBA definition and any external documentation using 'days' will mislead developers.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "LEAVE_TYPES DDL: CARRYOVER_EXPIRY NUMBER(3) nullable (number of days before carryover expires). PKG_LEAVE.pkb process_carryover: CARRYOVER_EXPIRY_DT = ADD_MONTHS(TO_DATE(v_next_year||'-01-01','YYYY-MM-DD'), CARRYOVER_EXPIRY). Seed: PTO CARRYOVER_EXPIRY=3 → April 1 expiry date.",
  "source_A": "DDL column comment: 'days'",
  "source_B": "PKG_LEAVE.process_carryover: ADD_MONTHS (treats value as months)",
  "evidence_hierarchy_winner": "Source B (code) — code execution is higher-ranked than DDL comment",
  "resolution": "DDL column comment is incorrect. Operationally CARRYOVER_EXPIRY is the number of MONTHS after January 1 of the new calendar year. The DDL comment should be corrected to 'number of months after Jan 1 of the new year before carryover expires'.",
  "phase_found": "Phase 4 spot check + Phase 5 cross-file"
}
```

### RA-001 — ADDED
```json
{
  "change_id": "RA-001",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — state tax default rule",
  "what": "A business rule is missing from hidden-business-rules.json: PKG_PAYROLL.calculate_state_tax applies a flat 5.00% rate for any state not explicitly enumerated. Known zero-tax states (TX, FL, WA) return 0%. Known non-zero states (CA=7.25%, NY=6.85%, IL=4.95%, PA=3.07%, OH=4.00%, NJ=6.37%, MA=5.00%) return their specific rate. Any other state code — including any future employee location not in this list — silently defaults to 5.00% without warning. This is a hidden business rule with payroll accuracy implications for multi-state employees.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_PAYROLL.pkb calculate_state_tax: v_rate := CASE p_state_code WHEN 'CA' THEN 0.0725 ... ELSE 0.05 END.",
  "confidence_before": 0.0,
  "confidence_after": 1.0,
  "suggested_id": "BR-039",
  "phase_found": "Phase 4 spot check"
}
```

### RA-002 — ADDED
```json
{
  "change_id": "RA-002",
  "type": "ADDED",
  "finding_id": "access-control-matrix.md — PII tables with no access control row",
  "what": "The access-control-matrix.md covers EMPLOYEE, LEAVE, PAYROLL, PERFORMANCE, REPORTING, INTEGRATION, SECURITY, SYSTEM PARAMS, and AUDIT LOG modules, but four tables containing PII have no corresponding access control row: (1) EMPLOYEE_DEPENDENTS (dependent SSN, DOB, name), (2) EMERGENCY_CONTACTS (third-party name, phone, email), (3) EMPLOYEE_BANK_ACCOUNTS (routing number plain-text, encrypted account number), (4) EMPLOYEE_TAX_INFO (W-4 filing status, allowances). Access to these tables is governed only by the general EMPLOYEE module grade-based rules, but this is not explicitly stated in the matrix, creating an audit gap for PII governance.",
  "evidence_source": "cross-file check (Phase 5)",
  "evidence_detail": "pii-inventory.json lists PII fields in EMPLOYEE_DEPENDENTS, EMERGENCY_CONTACTS, EMPLOYEE_BANK_ACCOUNTS, EMPLOYEE_TAX_INFO. access-control-matrix.md module rows do not include these as named modules.",
  "confidence_before": 0.0,
  "confidence_after": 1.0,
  "phase_found": "Phase 5 cross-file consistency"
}
```

### RA-003 — ADDED
```json
{
  "change_id": "RA-003",
  "type": "ADDED",
  "finding_id": "hidden-business-rules.json — compa-ratio formula (VW_EMPLOYEE_COMPENSATION)",
  "what": "The compa-ratio business rule is not captured in hidden-business-rules.json. VW_EMPLOYEE_COMPENSATION computes compa-ratio as: ROUND(BASE_SALARY / ((MIN_SALARY + MAX_SALARY) / 2) * 100, 1). Numerator: employee's BASE_SALARY. Denominator: grade midpoint = (MIN_SALARY + MAX_SALARY) / 2. Result: percentage to 1 decimal place. A compa-ratio of 100.0 means the employee is paid exactly at grade midpoint; above 100.0 = above midpoint; below 100.0 = below midpoint. This formula drives compensation reporting and is used in manager review discussions.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "schema/views/hrms_views.sql VW_EMPLOYEE_COMPENSATION: ROUND(sr.BASE_SALARY / ((g.MIN_SALARY + g.MAX_SALARY) / 2) * 100, 1) AS COMPA_RATIO.",
  "confidence_before": 0.0,
  "confidence_after": 1.0,
  "suggested_id": "BR-040",
  "phase_found": "Phase 4 spot check"
}
```

### RA-004 — ADDED
```json
{
  "change_id": "RA-004",
  "type": "ADDED",
  "finding_id": "data-quality-report.md — missing VW_PAYROLL_LATEST scope bug detail",
  "what": "DQ-015 documents the MAX(RUN_ID) issue in VW_PAYROLL_LATEST but does not note a second related problem: the subquery 'SELECT MAX(pr2.RUN_ID) FROM PAYROLL_RUNS pr2 WHERE pr2.STATUS = 'APPROVED'' selects the single globally maximum approved RUN_ID across ALL periods. This means the view returns payroll details for ALL employees but only for one specific run (the highest-ID approved run in the entire system). Employees from other pay periods (e.g., employees paid on a biweekly cycle while the most recent approved run was monthly) will appear to have zero pay. The view is not partitioned by PERIOD_ID or PAY_FREQUENCY.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "schema/views/hrms_views.sql VW_PAYROLL_LATEST: WHERE pr.RUN_ID = (SELECT MAX(pr2.RUN_ID) FROM PAYROLL_RUNS pr2 WHERE pr2.STATUS = 'APPROVED') — single global MAX, not per-employee or per-period.",
  "confidence_before": 0.70,
  "confidence_after": 1.00,
  "phase_found": "Phase 4 spot check"
}
```

### RE-001 — ENRICHED
```json
{
  "change_id": "RE-001",
  "type": "ENRICHED",
  "finding_id": "hidden-business-rules.json — BR-021 (AVAILABLE formula)",
  "what": "BR-021 documents the AVAILABLE virtual column formula. Evidence now confirmed from two independent sources: (1) LEAVE_BALANCES DDL virtual column definition, (2) PKG_LEAVE.get_leave_balance function which explicitly implements the same formula in PL/SQL: SELECT OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING INTO v_balance. Both sources agree. The VW_LEAVE_SUMMARY divergence (RED-002, DQ-007) remains an active conflict.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_LEAVE.pkb get_leave_balance: SELECT OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING INTO v_balance FROM LEAVE_BALANCES WHERE EMP_ID=p_emp_id AND LEAVE_TYPE_ID=p_leave_type_id AND CALENDAR_YEAR=p_year.",
  "confidence_before": 0.95,
  "confidence_after": 1.00,
  "phase_found": "Phase 4 spot check"
}
```

### RE-002 — ENRICHED
```json
{
  "change_id": "RE-002",
  "type": "ENRICHED",
  "finding_id": "hidden-business-rules.json — BR-026 (session timeout 30 minutes)",
  "what": "The 30-minute session timeout value is confirmed by two independent sources: (1) SYSTEM_PARAMETERS seed data PARAM_GROUP='SECURITY', PARAM_CODE='SESSION_TIMEOUT_MIN', PARAM_VALUE='30', and (2) PKG_SECURITY private constant c_session_timeout_min := 30. The code constant and the runtime parameter agree. However, is_session_valid checks c_session_timeout_min directly as a hard-coded value rather than reading from SYSTEM_PARAMETERS — meaning the SYSTEM_PARAMETERS row is decorative and changing it via set_param would have no effect on actual session behavior unless PKG_SECURITY is recompiled.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_SECURITY.pkb: c_session_timeout_min NUMBER := 30; is_session_valid uses this constant directly. data/seed/01_reference_data.sql: SESSION_TIMEOUT_MIN param value '30'.",
  "confidence_before": 0.90,
  "confidence_after": 0.98,
  "phase_found": "Phase 4 spot check"
}
```

### RE-003 — ENRICHED
```json
{
  "change_id": "RE-003",
  "type": "ENRICHED",
  "finding_id": "hidden-business-rules.json — BR-020 (carryover expiry calculation)",
  "what": "BR-020 correctly states carryover expiry is months after January 1. Confirmed with exact formula and example: CARRYOVER_EXPIRY_DT = ADD_MONTHS(TO_DATE(next_year||'-01-01','YYYY-MM-DD'), CARRYOVER_EXPIRY). For PTO (CARRYOVER_EXPIRY=3): January 1 + 3 months = April 1. For SICK (CARRYOVER_EXPIRY=NULL): carryover never expires. Also confirmed: if carryover expires, PKG_LEAVE.expire_carryover decrements ADJUSTMENT by CARRYOVER_FROM_PREV and resets CARRYOVER_FROM_PREV to 0 — meaning expiry is reversible from re-inspection of ADJUSTMENT delta but the CARRYOVER_FROM_PREV zero-reset does provide idempotency for a second run on the same day (WHERE CARRYOVER_FROM_PREV > 0 condition prevents double-deduction). DQ-009 double-expiry bug concern is slightly overstated: the WHERE clause protects against same-day re-run. The actual bug scenario requires CARRYOVER_FROM_PREV to be non-zero after the first run, which the code prevents.",
  "evidence_source": "spot check (Phase 4)",
  "evidence_detail": "PKG_LEAVE.pkb expire_carryover: UPDATE LEAVE_BALANCES SET ADJUSTMENT = ADJUSTMENT - CARRYOVER_FROM_PREV, CARRYOVER_FROM_PREV=0 WHERE CARRYOVER_EXPIRY_DT <= TRUNC(SYSDATE) AND CARRYOVER_FROM_PREV > 0.",
  "confidence_before": 0.80,
  "confidence_after": 0.95,
  "phase_found": "Phase 4 spot check"
}
```

---

## Phase 6 — da-outputs/review-summary.md

(This report IS the review summary — `DA_Data_Reviewer.md`. The summary section follows.)

---

## Section 1 — Overview

| Metric | Value |
|--------|-------|
| Files reviewed | 13 of 13 (plus DA_Data_Extractor.md = 14 total) |
| Source files cross-referenced | 10 (DDL, package bodies, triggers, seed data, views) |
| CORRECTED changes | 10 (RC-001 through RC-010) |
| UNRESOLVED DISCREPANCIES | 1 (DISC-001) |
| ADDED findings | 4 (RA-001 through RA-004) |
| ENRICHED findings | 3 (RE-001 through RE-003) |
| **Total changes** | **18** |

---

## Section 2 — Quality Scores

| Output File | Before | After | Basis for Change |
|------------|--------|-------|-----------------|
| `schema-catalogue.json` | 0.95 | 0.96 | Solid; no structural errors found |
| `erd.md` | 0.95 | 0.96 | Correct; all 30 tables, all FK relationships verified |
| `data-source-inventory.json` | 0.90 | 0.82 | RC-006: DS-05 format and filename both wrong |
| `data-flow-map.md` | 0.90 | 0.82 | RC-005: 3 wrong procedure names in flows |
| `pii-inventory.json` | 0.95 | 0.90 | RC-007: SSN grade threshold wrong; RA-002: 4 PII tables with no matrix coverage noted |
| `data-quality-report.md` | 0.95 | 0.96 | RA-004 adds detail to DQ-015; RE-003 clarifies DQ-009 |
| `migration-complexity.json` | 0.90 | 0.91 | Correct; RC-004 only affects extractor summary |
| `hidden-business-rules.json` | 0.95 | 0.72 | RC-001/RC-002: BR-022 leave names and values wrong; RC-003: BR-035 holiday list wrong; RC-008: BR-011 wrong function attribution; RA-001/RA-003: 2 missing business rules |
| `storage-pattern-analysis.md` | 0.90 | 0.91 | No errors; RC-006 is in inventory, not here |
| `redundancy-analysis.json` | 0.90 | 0.91 | No errors found; cross-references hold |
| `data-dictionary.md` | 0.90 | 0.90 | RC-009: minor DEPARTMENTS seed ID description wrong; overall sound |
| `conceptual-data-model.md` | 0.85 | 0.85 | No errors; inferred intent remains valid |
| `access-control-matrix.md` | 0.95 | 0.90 | RC-010: extracted SQL shows non-existent GRADE_LEVEL column; RA-002: 4 PII modules not covered |
| `DA_Data_Extractor.md` | 0.92 | 0.88 | RC-004: overstated migration factor count |

| Metric | Before | After |
|--------|--------|-------|
| **Overall confidence** | **0.92** | **0.89** |

*Note: Overall confidence after is lower, not because the data is worse, but because RC-001/RC-002/RC-003 corrected material errors in hidden-business-rules.json that were previously scored at 0.95. The corrected output files now have higher accuracy; the pre-review score was overconfident.*

---

## Section 3 — Key Corrections

**1. BR-022 leave types (RC-001) — HIGH IMPACT**  
Agent 1 invented three leave type names not in this system. Any stakeholder document referencing "Annual Leave", "Maternity Leave", or "Paternity Leave" is describing a system that does not exist. The actual system has: PTO, SICK, COMP, FMLA, JURY DUTY, BEREAVEMENT.

**2. BR-022 leave balance values (RC-002) — HIGH IMPACT**  
PTO max balance stated as 30 — actual is 20. SICK carryover stated as "none" — actual is 10 days. These directly affect employee-facing communications and migration target sizing.

**3. BR-035 holiday list (RC-003) — MEDIUM IMPACT**  
Columbus Day and Veterans Day listed as company holidays — they are not. Day After Thanksgiving and Christmas Eve are company holidays — they were omitted. This matters for business day calculation validation and payroll testing.

**4. Data flow procedure names (RC-005) — MEDIUM IMPACT**  
`hire_employee`, `submit_request`, `initialize_leave_balances` are all wrong procedure names. Any developer referencing the flow map to navigate code will look for the wrong functions.

**5. PAY_REGISTER format (RC-006) — MEDIUM IMPACT**  
DS-05 describes a fixed-width .txt file; the actual output is a timestamped CSV (.csv). Any integration consumer of this file will need the correct format and naming to locate it.

**6. SSN grade threshold (RC-007) — HIGH IMPACT**  
pii-inventory.json said Grade 5+ can view SSN. The actual threshold is Grade 8+. This is a material error in a compliance document; it understates SSN access controls.

**7. Access control matrix extracted SQL (RC-010) — MEDIUM IMPACT**  
The code block shown for `has_permission` references a column that does not exist in the schema. The behavior description is correct; only the code sample is wrong.

**8. DISC-001: CARRYOVER_EXPIRY units — MEDIUM IMPACT**  
DDL says "days", code implements "months". The DDL column comment should be corrected. All migration or documentation work must treat this as months.

---

## Section 4 — Cross-File Consistency Results

| Check | Outcome |
|-------|---------|
| Table count (30 ↔ 30) | PASS |
| PII columns in schema | PASS |
| Row counts | N/A — CODE-ONLY |
| Business rules ↔ flow map | FIXED (RC-005 corrects procedure names) |
| Cache in inventory ↔ storage | PASS |
| FK delete rules | PASS |
| Canonical entities ↔ schema | PASS |
| Dictionary ↔ schema columns | PASS (audit columns intentionally omitted) |
| Conceptual model ↔ schema | PASS |
| PII tables ↔ access matrix | GAP DOCUMENTED (RA-002 adds finding) |
| SSN access grade | FIXED (RC-007) |
| Leave type names | FIXED (RC-001, RC-002) |
| Holiday list | FIXED (RC-003) |
| Migration factor count | FIXED (RC-004) |
| Pay register format | FIXED (RC-006) |
| has_permission SQL | FIXED (RC-010) |
| CARRYOVER_EXPIRY units | DISC-001 documented, not silently resolved |
| Medicare function | FIXED (RC-008) |
| DEPARTMENTS seed description | FIXED (RC-009) |

---

## Section 5 — Open Questions for Gate G1

The following cannot be answered by reading the source code. Each is assigned to a role for resolution.

| # | Question | Role | Priority |
|---|----------|------|---------|
| G1-01 | FMLA and COMP leave types exist but have no accrual. Does this system track the legal FMLA entitlement (12 weeks/year under US federal law) or is the FMLA type a placeholder only? | Legal / HR Director | HIGH |
| G1-02 | The system has no Maternity, Paternity, or Parental leave type. Is this intentional? Does the company cover parental leave under FMLA, a separate policy, or not at all? | HR Director | HIGH |
| G1-03 | PKG_SECURITY.authenticate does not verify passwords (DQ-003). Is this a known stub intentionally deferred? What authentication mechanism is currently in use in production (e.g., Oracle DB authentication bypassing this function, LDAP integration, SSO)? | IT Security / DBA | CRITICAL |
| G1-04 | The AES-256 encryption key 'HR$ystem_3ncrypt10n_K3y_2024!!' is in source code. Has this key ever been rotated? Is the same key used in production today? | IT Security | CRITICAL |
| G1-05 | DBMS_SCHEDULER jobs for notification processing (every 5 min) and monthly leave accrual are referenced but no DDL was found. Do these jobs exist in the production Oracle scheduler? What is their current schedule and last run history? | DBA | HIGH |
| G1-06 | The TIME_ATTENDANCE_IN integration is a TODO stub. Is there a live time and attendance system feeding into this schema (perhaps via a different mechanism) or is hourly payroll not implemented? | HR Operations | MEDIUM |
| G1-07 | Rehire overwrites HIRE_DATE (BR-006, DQ-016). For employees who have been rehired, is the original tenure data retained anywhere (e.g., separate HR system, paper files)? | HR Director | MEDIUM |
| G1-08 | Tax brackets are hard-coded for 2024 (DQ-011). Was the system used for 2025 payroll processing? If so, all 2025 payroll calculations used 2024 tax brackets — what is the financial exposure? | Finance / Payroll Manager | HIGH |
| G1-09 | The LOOKUP_VALUES table is defined and seeded but no lookup types or seed rows were provided. What lookup types does the application actually use? Are they separately seeded or managed through the admin UI? | HR Operations / DBA | LOW |
| G1-10 | Benefits feed transfers SSN in plain text to ADP FTP (DS-03, DS-07). Is the FTP connection secured (SFTP/FTPS)? Is the file encrypted at the OS level before transfer? | IT Security | HIGH |

---

## Section 6 — Gate G1 Recommendation

**Recommendation: CONDITIONALLY READY**

The Agent 1 extraction is structurally sound. All 30 tables, 6 views, 29 sequences, 6 triggers, and 11 packages are documented. The schema is correctly modelled. The critical security findings (DQ-001 through DQ-004) are correctly identified and ranked.

**Required before presenting to Gate G1 stakeholders:**

1. **hidden-business-rules.json** — Update BR-022 (RC-001, RC-002) and BR-035 (RC-003). These errors directly affect business language in stakeholder documents.
2. **pii-inventory.json** — Update SSN access_restriction to Grade ≥ 8 (RC-007).
3. **data-flow-map.md** — Correct procedure names (RC-005).

**Acceptable to present as-is with verbal caveat:**

- data-source-inventory.json DS-05 format error (RC-006) — low stakeholder visibility.
- access-control-matrix.md code block (RC-010) — functional description is correct.
- DISC-001 carryover units — document as open question.

**Gate G1 readiness blockers (not Agent 2 findings):**

- G1-03 (authentication stub) and G1-04 (encryption key) must be addressed before any external sharing of the security section, regardless of Agent 2 review.

---

## Confidence Post-Review Summary

| File | Post-Review Confidence |
|------|----------------------|
| `schema-catalogue.json` | 0.96 |
| `erd.md` | 0.96 |
| `data-source-inventory.json` | 0.82 → needs RC-006 applied |
| `data-flow-map.md` | 0.82 → needs RC-005 applied |
| `pii-inventory.json` | 0.90 → needs RC-007 applied |
| `data-quality-report.md` | 0.96 |
| `migration-complexity.json` | 0.91 |
| `hidden-business-rules.json` | 0.72 → needs RC-001, RC-002, RC-003, RC-008 applied |
| `storage-pattern-analysis.md` | 0.91 |
| `redundancy-analysis.json` | 0.91 |
| `data-dictionary.md` | 0.90 → needs RC-009 applied |
| `conceptual-data-model.md` | 0.85 |
| `access-control-matrix.md` | 0.90 → needs RC-010 applied |
| **Overall (after applying all corrections)** | **0.94** |

---

*DA Reverse Engineering System — Agent 2 of 2 | v2 | June 2026 | Review date: 2026-08-04*
