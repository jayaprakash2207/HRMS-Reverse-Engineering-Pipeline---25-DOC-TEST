# Human Review — Gap Reports and Contradictions

**Reviewer:** ___________________________
**Date reviewed:** ___________________________
**Sign-off:** ___________________________

**Source file:** `results/cross_validation_report.json`
**This is the CRITICAL review file — all contradictions must be resolved before code generation.**

---

## Summary

The Step 13 Cross Validator compared all 4 analysis tracks (BA, DA, TA, AA) and found:

| Type | Count | Resolved by AI | Needs Human Decision |
|------|-------|---------------|---------------------|
| Gaps (entity in one track, missing in another) | 18 | 13 auto-resolved | 5 unresolved |
| Contradictions (two tracks disagree on same fact) | 7 | 0 auto-resolved | **7 all need human decision** |

---

## CONTRADICTIONS — All 7 Require Human Decision

### CONTRADICTION 1 — Leave Balance Formula (HIGH)

**The problem:** Three different formulas calculate "available leave balance" across the system:

| Source | Formula | Includes PENDING? |
|--------|---------|-------------------|
| `VW_LEAVE_SUMMARY` (reporting view) | `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT` | ❌ No |
| `LEAVE_BALANCES.AVAILABLE` (virtual column) | `OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING` | ✅ Yes |
| `PKG_LEAVE` (application logic) | Uses virtual column | ✅ Yes |

**Impact:** Any employee with pending leave requests will see different balance figures
depending on which source is queried. Reporting (via view) shows more balance than
the application shows — employees and managers get contradictory numbers.

**Human Decision Required:**

- [ ] Use formula WITH PENDING (subtract pending — more conservative, recommended)
- [ ] Use formula WITHOUT PENDING (show full balance until approved)
- [ ] Other: ___________________________

**Decision:** ___________________________
**Decided by:** ___________________________

---

### CONTRADICTION 2 — Hire Date Future Limit (HIGH) ⚠️ MUST RESOLVE

**The problem:** Two different maximum future dates for hire date:

| Source | Limit | Location |
|--------|-------|----------|
| Oracle Forms (UI) WHEN-VALIDATE-ITEM | **90 days** | `HRMS_EMPLOYEE` form |
| `TRG_EMP_BEFORE_INSERT` (DB trigger) | **180 days** | `schema/triggers/` |

**Impact:** If a hire date between 91–180 days in the future is entered:
- The UI will **reject** it (90-day rule)
- But if bypassed, the DB will **accept** it (180-day rule)
- The form and trigger are in direct conflict.

The DA reviewer flagged the trigger as authoritative. TA tagged this as DISC-001.

**Human Decision Required:**

- [ ] 90 days is correct — the trigger has a bug and should be updated to 90 days
- [ ] 180 days is correct — the form has a bug and should be updated to 180 days
- [ ] Both are intentional for different hire types: ___________________________

**Decision:** ___________________________
**Decided by:** ___________________________

---

### CONTRADICTION 3 — EMPLOYEE_HISTORY Column Structure (HIGH) ⚠️ MUST RESOLVE

**The problem:** The trigger and DDL disagree on the EMPLOYEE_HISTORY table structure:

| Source | Columns |
|--------|---------|
| `01_core_tables.sql` DDL (authoritative per DA) | `EFFECTIVE_DATE, OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID, NEW_JOB_ID, OLD_MANAGER_ID, NEW_MANAGER_ID, OLD_SALARY, NEW_SALARY, OLD_LOCATION, NEW_LOCATION` |
| `TRG_EMP_BEFORE_UPDATE` (AA component COMP-020) | `CHANGE_DATE, OLD_VALUE, NEW_VALUE` |

**Impact:** Every `UPDATE` to the `EMPLOYEES` table will raise `ORA-00904: "CHANGE_DATE": invalid identifier`
because the trigger references columns that don't exist in the DDL.

**Human Decision Required:**

- [ ] DDL is correct — rewrite the trigger to use the DDL column structure
- [ ] Trigger is correct — alter the DDL to use CHANGE_DATE/OLD_VALUE/NEW_VALUE generic columns
- [ ] Design a new EMPLOYEE_HISTORY schema for the new system: ___________________________

**Decision:** ___________________________
**Decided by:** ___________________________

---

### CONTRADICTION 4 — rehire_employee: Functional or Broken? (HIGH)

**The problem:**

| Source | Claim |
|--------|-------|
| AA component registry (COMP-001) | `rehire_employee` is a confirmed public method, no non-functional flag |
| BA Pass 2 (explicit finding) | `rehire_employee` is entirely non-functional — trigger blocks TERMINATED→ACTIVE status change |
| TA (DISC-002) | Documents this as a confirmed defect |

**Impact:** AA incorrectly classifies a broken procedure as healthy. The rehire business
process is impossible in the current system.

**Human Decision Required:**

- [ ] Confirmed BROKEN — rehire functionality does not work in production
- [ ] The procedure works in production (meaning the trigger was disabled or bypassed)
- [ ] Rehire is not needed in the new system — remove it entirely
- [ ] Rehire IS needed — this is a P1 defect to fix in Phase 1

**Decision:** ___________________________
**Decided by:** ___________________________

---

### CONTRADICTION 5 — Table Count: 30 (DA) vs 35 (TA) (MEDIUM)

**The problem:**

| Source | Table Count |
|--------|------------|
| DA Data Reviewer (DDL parsing) | **30 tables** |
| TA Stack Scout | **35 tables** — but TA's own section headings have internal inconsistencies |

TA's headings: "Core Tables — 6 tables" (but body has 8 rows), "Payroll Tables — 8 tables" (but body has 9 rows).
This suggests the TA count of 35 is unreliable.

**Human Decision Required:**

- [ ] 30 tables is correct — TA overcounted
- [ ] 35 tables is correct — DA missed 5 tables
- [ ] Actual count confirmed by checking DDL directly: ___________________________

**Decision:** ___________________________
**Decided by:** ___________________________

---

### CONTRADICTION 6 — BA Document Version: Which Is Canonical? (MEDIUM) ⚠️ MUST RESOLVE

**The problem:** Three BA documents exist with different business rule counts:

| File | Rule Count |
|------|-----------|
| `BA_Deep_Analyst_FINAL.md` (repo root) | 120 rules (BR-01 to BR-120) |
| `results/Business_Analysis/BA_Deep_Analyst.md` (merged) | **140 rules** (BR-01 to BR-140) |
| `BA_Deep_Analyst_Edge.md` | 87 rules |

Any cross-track reference to "BA output" is ambiguous. The forward engineering docs
(BRD, capability model, etc.) were generated using the 140-rule version.

**Human Decision Required:**

- [ ] 140 rules (merged file) is canonical — this is what the pipeline used
- [ ] 120 rules (FINAL file) is canonical — the extra 20 in the merged are duplicates
- [ ] 87 rules (edge file) is canonical
- [ ] All three are valid; merged is the definitive version going forward

**Decision:** ___________________________
**Decided by:** ___________________________

---

### CONTRADICTION 7 — HOURLY Salary Basis: Supported or Not? (MEDIUM)

**The problem:**

| Source | Claim |
|--------|-------|
| `DA schema` | `SALARY_RECORDS.SALARY_BASIS CHECK IN ('ANNUAL','HOURLY')` — HOURLY is a valid, expected value |
| `AA component-registry` (COMP-002 PKG_PAYROLL) | `SALARY_BASIS` is always silently overwritten to `'ANNUAL'` regardless of input |
| `BA payroll process flow` | No business rule for hourly-basis payroll at all |

**Impact:** If any employees are on HOURLY basis, their salary basis is silently overwritten
and their pay calculated incorrectly.

**Human Decision Required:**

- [ ] HOURLY employees don't exist — the schema constraint is future-proofing only; safe to ignore
- [ ] HOURLY employees DO exist — this is a critical payroll bug that must be fixed
- [ ] The new system should support HOURLY basis — build it correctly from scratch

**Decision:** ___________________________
**Decided by:** ___________________________

---

## UNRESOLVED GAPS (5 items needing investigation)

These 13 of 18 gaps were auto-resolved by the pipeline. The 5 below still need human confirmation:

| Gap | Description | Action Required |
|-----|------------|-----------------|
| G-14 | `TIME_ATTENDANCE_RECORDS` table referenced in `PKG_INTEGRATION` but no DDL found | Confirm: does this table exist in production? |
| G-15 | `RPT_HEADCOUNT`, `RPT_COMPENSATION`, `RPT_LEAVE_UTIL` — views or physical tables? | Confirm their type and structure |
| G-16 | `PKG_INTEGRATION.get_integration_status` — BA and TA don't mention this function | Is this used by anything? Should it be in the new system? |
| G-17 | `PKG_PAYROLL.get_ytd_earnings` — BA has no business rule for YTD earnings display | Is YTD reporting a business requirement? |
| G-18 | Calibration columns `CALIBRATED_RATING`, `CALIBRATION_NOTES` in `PERFORMANCE_REVIEWS` — no BA rule | Is performance calibration a required business process? |

---

## Post-Resolution Checklist

Once all decisions above are made:

- [ ] Update `results/ForwardEngineering_Docs/01_BRD.md` with canonical business rule count
- [ ] Update `results/ForwardEngineering_Docs/07_DATA_MODEL_SPECIFICATION.md` with correct EMPLOYEE_HISTORY schema
- [ ] Update `results/ForwardEngineering_Docs/15_FORWARD_ENGINEERING_SPECIFICATION.md` with hire date decision
- [ ] Update `results/Foundation_KnowledgeGraph/CANONICAL_ENTERPRISE_MODEL.md` with confirmed table count
- [ ] Update `results/ForwardEngineering_Docs/16_GENERATION_MANIFEST.json` if bounded contexts or entities change
- [ ] Notify tech lead that all contradictions are resolved and code generation can begin
