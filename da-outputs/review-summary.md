# DA Agent 2 Review Summary
**System:** HRMS | **Schema:** HRMS | **Platform:** Oracle 19c + Forms 12c
**Review date:** 2026-08-03
**DB connection:** CODE-ONLY throughout (no Oracle client available)

---

## Overview

DA Agent 2 reviewed all 13 of 13 output files across two passes.

**Pass 1** read 7 source files not scanned by Agent 1: PKG_EMPLOYEE.pkb, PKG_PAYROLL.pkb, PKG_LEAVE.pkb, PKG_INTEGRATION.pkb, PKG_NOTIFICATION.pkb, PKG_SECURITY.pkb, README.md.

**Pass 2** validated findings against full source: PKG_SECURITY.pkb (full body), PKG_AUDIT.pkb (full body), all 4 schema/tables/*.sql files (30 tables full DDL), plsql/triggers/trg_employees.sql, plsql/triggers/trg_audit.sql, schema/views/hrms_views.sql (6 views full definition), schema/sequences/hrms_sequences.sql (29 sequences).

Package bodies still unread: PKG_REPORTING.pkb, PKG_COMMON.pkb, PKG_VALIDATION.pkb, PKG_PERFORMANCE.pkb.

Zero test files exist in this codebase — README.md explicitly states "No unit tests — all testing is manual via Forms." This is confirmed technical debt, not a scan gap.

**Cumulative change records: 41** (9 CORRECTED · 24 ADDED · 8 ENRICHED)

---

## Quality Scores

| Domain | Before Review | After Pass 1 | After Pass 2 | Total Movement |
|---|---|---|---|---|
| Schema / DDL coverage | 0.85 | 0.88 | 0.93 | +0.08 (sequence count corrected, USER_CREDENTIALS gap found, view joins confirmed) |
| Business rules | 0.62 | 0.91 | 0.93 | +0.31 (12 new rules Pass 1; 3 new rules Pass 2: session timeout source, change_password stub, VW_EMPLOYEE_COMPENSATION join risk) |
| PII inventory | 0.75 | 0.82 | 0.87 | +0.12 (E-007: AES-256 key extracted and confirmed; A-022: change_password stub confirmed) |
| Access control | 0.50 | 0.90 | 0.92 | +0.42 (E-005/E-006 confirmed in Pass 1; A-023: TOO_MANY_ROWS silent auth collision added in Pass 2) |
| Data quality findings | 0.80 | 0.87 | 0.90 | +0.10 (RC-009: compensation view salary join; A-024: AVAILABLE fork confirmed from source) |
| Storage patterns | 0.70 | 0.80 | 0.83 | +0.13 (RC-008: session timeout source confirmed; RC-009: VW_EMPLOYEE_COMPENSATION risk confirmed) |
| Integration inventory | 0.40 | 0.90 | 0.90 | +0.50 (unchanged in Pass 2 — all integrations confirmed in Pass 1) |
| Migration complexity | 0.78 | 0.82 | 0.85 | +0.07 (E-008: trigger mismatch confirmed from both sides; 4 package bodies still unread) |
| **OVERALL** | **0.68** | **0.87** | **0.89** | **+0.21** |

---

## Key Corrections (Agent 1 findings that changed)

### Severity Reduced

**RC-001 — AUDIT_LOG STATUS_CHANGE constraint**
Agent 1 classified as LAUNCH-BLOCKING ("every leave-status change will raise ORA-02290"). Corrected: PKG_AUDIT.log_action uses PRAGMA AUTONOMOUS_TRANSACTION with EXCEPTION WHEN OTHERS → ROLLBACK and an explicit design comment "audit logging must never fail the calling transaction." Leave approvals succeed; the audit record is silently dropped. This is a compliance gap (leave status changes are unaudited), not an operational blocker. Confidence raised from 0.75 → 0.95.

**RC-002 — TAX_BRACKETS table usage**
Agent 1 wrote "TAX_BRACKETS is presumably read by PKG_PAYROLL." Corrected: TAX_BRACKETS is never read. All 2024 federal brackets are hard-coded in calculate_federal_tax with an explicit TODO comment. The table exists but is currently unused/empty. See A-002 for full bracket extraction.

### Severity Escalated

**E-006 — Authentication stub**
Agent 1 said "password validation is a stub — passwords are in USER_CREDENTIALS." Escalated: PKG_SECURITY.authenticate does not query USER_CREDENTIALS at all in the code provided. It selects by EMAIL from EMPLOYEES and immediately creates a session with no password hash comparison. The current implementation accepts any password for any active employee. Confidence raised from 0.80 → 1.00. Severity escalated to CRITICAL SECURITY DEFECT.

**E-001 — EMPLOYEE_HISTORY trigger**
Agent 1 correctly identified TRG_EMP_BEFORE_UPDATE as broken. Enriched: PKG_EMPLOYEE.log_history uses the CORRECT column set. The trigger is the sole broken component — it fires first on UPDATE and fails, blocking the correctly-implemented package-level history. Fix path confirmed: align the trigger's INSERT column list with actual DDL, or drop the trigger.

---

## Key New Findings (not in Agent 1 outputs)

**Critical security:**
- A-001: SQL injection in PKG_EMPLOYEE.search_employees (self-documented in source)
- A-009: Benefits feed exports all employee + dependent PII without has_permission check

**Critical payroll compliance:**
- RC-005: HEAD_OF_HOUSEHOLD filing status produces $0 federal tax withholding (CASE block does not handle it)
- RC-006: PAYROLL_RUNS.TOTAL_NET/TOTAL_DEDUCTIONS exclude BENEFIT element type (payslip correct; run summary wrong)
- A-002: Full 2024 federal tax bracket structure extracted (single/married-separate, married-joint)
- A-003: FICA/Medicare hard-coded 2024 thresholds extracted
- A-004: State tax flat rates extracted (10 states + default)
- A-015: Pretax deductions (401k, HSA) NOT subtracted before bracket calculation (documented as "simplified")
- A-020: calculate_payroll commits every 50 employees — half-calculated state on failure
- A-021: get_payslip returns hardcoded YTD_GROSS=0, YTD_NET=0 (placeholder values)

**Critical leave:**
- A-005: Leave backdating window: 5 calendar days
- A-016: expire_carryover double-subtract bug if run twice same day (self-documented)
- A-017: AVAILABLE formula fork now occurs in THREE places, not two (process_carryover also uses 4-term formula)
- A-018: Employees with no manager (e.g. CEO) have leave requests that become permanently PENDING

**Integration:**
- A-011 / A-012: GL feed and benefits feed protocols fully confirmed (file formats, field layouts)
- A-013: import_time_attendance is a stub — CSV is opened but never parsed or written to DB
- A-014: sync_org_structure is a stub — no LDAP/AD calls
- A-019: Both DBMS_SCHEDULER jobs confirmed (5-minute email queue, monthly accrual) — scheduler scripts not in repo

**HR rules:**
- A-007: Termination auto-cancels PENDING leave but does NOT adjust LEAVE_BALANCES.PENDING
- A-008: Rehire overwrites original HIRE_DATE — seniority data is lost
- A-010: Manager circular chain detection silently fails for orgs deeper than 15 levels

---

## Cross-File Consistency Results

| # | Files checked | Result |
|---|---|---|
| 1 | schema-catalogue.json ↔ erd.md | PASS |
| 2 | pii-inventory.json ↔ schema-catalogue.json | PASS (minor: EMPLOYEES.NOTES not listed) |
| 3 | schema-catalogue.json ↔ migration-complexity.json row count basis | PASS |
| 4 | hidden-business-rules.json ↔ data-flow-map.md | PASS — both updated with new rules |
| 5 | data-source-inventory.json ↔ storage-pattern-analysis.md (cache) | PASS |
| 6 | schema-catalogue.json ↔ migration-complexity.json (cascade delete) | PASS |
| 7 | redundancy-analysis.json ↔ schema-catalogue.json | PASS |
| 8 | data-dictionary.md ↔ schema-catalogue.json (table coverage) | PASS — all 30 tables present |
| 9 | conceptual-data-model.md ↔ schema-catalogue.json | PASS |
| 10 | access-control-matrix.md ↔ pii-inventory.json | PARTIAL — benefits export PII path added (A-009) |

---

## Open Questions for Gate G1

| ID | Question | Role |
|---|---|---|
| G1-Q1 | Which AVAILABLE formula is authoritative — 5-term (virtual column, get_leave_balance) or 4-term (VW_LEAVE_SUMMARY, process_carryover)? | HR/Payroll Product Owner |
| G1-Q2 | How are tax brackets updated annually — TAX_BRACKETS table or manual package edit? | Payroll Director + DBA |
| G1-Q3 | Are any active employees using HEAD_OF_HOUSEHOLD filing status? If so, retroactive correction needed. | Payroll Manager + Tax Compliance |
| G1-Q4 | Does PKG_SECURITY.authenticate in production match the source (no password check), or is a patched version deployed? | CISO + DBA |
| G1-Q5 | Does the rehire process intentionally overwrite original HIRE_DATE, or should ORIGINAL_HIRE_DATE be preserved? | HR Director |
| G1-Q6 | Is the ADP benefits feed active? Does it have a current DPA? Dependent PII export may require GDPR legal basis. | Legal / Data Privacy Officer |
| G1-Q7 | What is the retention and anonymization policy for terminated employee PII given the blocking INSTEAD OF DELETE trigger? | Legal / Data Privacy Officer |
| G1-Q8 | PKG_REPORTING.pkb, PKG_COMMON.pkb, PKG_VALIDATION.pkb, PKG_PERFORMANCE.pkb unread — requires one additional scan pass before G1. | DA Agent follow-up |
| G1-Q9 | Does USER_CREDENTIALS table exist in production? If so, provide its DDL — it holds password hashes and is central to the authentication security assessment. | DBA + CISO |
| G1-Q10 | Is the 30-minute absolute session limit (from login time, not last activity) the intended behavior? SYSTEM_PARAMETERS.SESSION_TIMEOUT_MIN is ignored at runtime. | HR System Owner + CISO |

---

## Gate G1 Recommendation: NOT READY

Six unresolved categories (updated after Pass 2) block a confident Gate G1 passage:

1. **3 original launch-blocking defects from Agent 1 still open** — TRG_EMP_BEFORE_UPDATE column mismatch (now confirmed from both DDL and trigger source in E-008), 3 seed/DDL column drifts, and the AUDIT_LOG status change compliance gap.
2. **Critical security: PKG_SECURITY.authenticate contains no password verification in current source** — USER_CREDENTIALS table is now confirmed as referenced-but-absent from DDL. Potential CRITICAL exposure depending on production state (see G1-Q4, G1-Q9).
3. **Critical payroll compliance: HEAD_OF_HOUSEHOLD = $0 federal tax** — IRS under-withholding risk if any employees have this status.
4. **Data integrity: PAYROLL_RUNS totals exclude BENEFIT elements; partial payroll commits on failure.**
5. **SQL injection in PKG_EMPLOYEE.search_employees** — must be patched before any migration that preserves this package.
6. **Pass 2 new: VW_EMPLOYEE_COMPENSATION missing salary date-scope predicate (RC-009)** — compensation view can return duplicate rows producing incorrect COMPA_RATIO. Requires fix before any compensation analytics or migration relying on this view.

When ready: resolve/accept the 3 original blockers, confirm authentication production state and USER_CREDENTIALS DDL, assess HEAD_OF_HOUSEHOLD impact, fix VW_EMPLOYEE_COMPENSATION, and read the 4 remaining package bodies.

---

*DA Reverse Engineering System — Agent 2 of 2 | v2 | June 2026*
*Pass 1 produced: 2026-08-03 | Pass 2 produced: 2026-08-03*
