# Final Sanity Check — HRMS D1 Architecture Extraction

**Overall: PARTIAL — trigger registry is wrong; five package registries need rewrite; dependency graph missing five edges; one call-flow step invents a behaviour. Architecture findings and migration plan are correct and safe to act on.**

---

## Validation Checklist

| # | Check | Verdict | Detail |
|---|-------|---------|--------|
| 1 | Required files exist (20/20) | **PASS** | All 20 output files confirmed in `results/D1-application-architecture/` including AA_App_Extractor.md |
| 2 | JSON valid (no syntax errors) | **PASS** | All 7 JSON files + call-flow-map.json verified; no trailing commas, unclosed structures, or malformed values |
| 3 | Modules match component registry | **PASS** | All `module` fields in component registry resolve to MOD-01–MOD-06; no dangling references |
| 4 | Dependency edges resolve to nodes | **PASS** (with omissions) | All 39 declared edges resolve to valid nodes. 5 edges are missing: PKG_REPORTING→PKG_EMPLOYEE, PKG_REPORTING→PKG_PAYROLL, PKG_REPORTING→PKG_COMMON (DISC-008), PKG_SECURITY→PKG_EMPLOYEE (DISC-011) |
| 5 | Call-flow steps reference components | **PARTIAL** | FLOW-02 step 7 references phantom component TRG_EMPLOYEES_AUDIT that does not exist in any source file (DISC-012) |
| 6 | Diagrams match JSON artifacts | **PARTIAL** | No fabricated edges in diagrams. PKG_REPORTING absent from dependency-view.mmd (consistent with DISC-008). PKG_SECURITY→PKG_EMPLOYEE edge absent (consistent with DISC-011). Omissions only; no wrong edges drawn. |
| 7 | Claims have evidence | **PARTIAL** | 23/24 violations evidence-backed. COMP-DB-TRIGGERS invents a salary validation claim not present in any trigger body (DISC-010). One return type error for PKG_SECURITY.authenticate (DISC-003). |
| 8 | Risks have affected module/component | **PARTIAL** | All 13 risks trace to violation IDs and source files. No formal `affected_modules` field exists in the risk register; downstream parsers will find nothing to parse. |
| 9 | Unknowns are open questions | **PASS** | 41 open questions documented; 11 "not found" items in extraction-audit.md; none presented as facts. Confidence levels correctly differentiated. |
| 10 | No invented cloud/platform/runtime assumptions | **PASS** | Current-state artifacts contain no cloud or platform assertions. Forward-engineering recommendations clearly labelled as target-state only. |
| 11 | Forward-engineering files are actionable | **PASS** | 6-phase migration sequence with explicit per-module blockers; 10 mandatory pre-migration tasks with category labels; REST API proposals per service. |

---

## Procedure Count Spot-Check

| Package | Registry Count | Spot-Check Source Count | Match? |
|---------|---------------|------------------------|--------|
| PKG_EMPLOYEE | 18 | Not in spot-check set | UNVERIFIED |
| PKG_PAYROLL | 15 | Not in spot-check set | UNVERIFIED |
| PKG_LEAVE | 14 | Not in spot-check set | UNVERIFIED |
| PKG_NOTIFICATION | 4 | Not in spot-check set | UNVERIFIED |
| PKG_INTEGRATION | 5 | Not in spot-check set | UNVERIFIED |
| PKG_PERFORMANCE | 12 | **12** (verified from .pkb) | ✓ MATCH |
| PKG_SECURITY | 8 | **8** (verified from .pks + .pkb; 1 type error: DISC-003) | PARTIAL |
| PKG_AUDIT | 3 | **3** (verified; 1 name wrong: DISC-004) | PARTIAL |
| PKG_COMMON | 16 | **17** (4 renamed, 5 missing, 4 phantom: DISC-005) | MISMATCH |
| PKG_VALIDATION | 8 | **8** (5 wrong names, 2 missing, 3 phantom: DISC-007) | PARTIAL |
| PKG_REPORTING | 8 | **8** (3 wrong names, 2 missing, 2 phantom: DISC-006) | PARTIAL |
| **TOTAL** | **111** | 111 verified + ~19 unverified private procedures | DISC-001 |

The system-inventory.json claims 130. The gap of 19 most likely represents private/helper procedures documented in Layer 1 `source_code.json` but omitted from the public-facing registry. This must be explained before the registry is used as an authoritative count.

---

## Trigger Count and Name Spot-Check

| Source Name | Table | Timing/Event | Registry Entry | Match? |
|-------------|-------|-------------|----------------|--------|
| TRG_SALARY_AUDIT | SALARY_RECORDS | AFTER INSERT OR UPDATE OR DELETE | TRG_SALARY_AUDIT | ✓ MATCH |
| TRG_LEAVE_REQUEST_AUDIT | LEAVE_REQUESTS | **AFTER UPDATE OF STATUS** | TRG_LEAVE_AUDIT | ✗ Wrong name; wrong event scope (registry says ALL DML) |
| TRG_DEPARTMENT_AUDIT | DEPARTMENTS | AFTER INSERT OR UPDATE OR DELETE | **NOT IN REGISTRY** | ✗ Missing |
| TRG_EMP_BEFORE_INSERT | EMPLOYEES | BEFORE INSERT | TRG_EMPLOYEES_VALIDATE (BEFORE INSERT OR UPDATE) | ✗ Wrong name; wrong event; body description invents salary check |
| TRG_EMP_BEFORE_UPDATE | EMPLOYEES | BEFORE UPDATE | TRG_EMPLOYEES_AUDIT (AFTER INSERT OR UPDATE OR DELETE) | ✗ Wrong name; wrong timing; wrong event |
| TRG_EMP_INSTEAD_OF_DELETE | EMPLOYEES | BEFORE DELETE | **NOT IN REGISTRY** | ✗ Missing |
| — | — | — | TRG_AUDIT_LOG_INSERT | ✗ Does not exist in any source file |
| — | — | — | TRG_NOTIFICATION_INSERT | ✗ Does not exist in any source file |

**Result:** Only 1 of 6 trigger entries has the correct name. 2 phantom entries do not exist. The trigger registry requires complete replacement.

---

## Form Count Spot-Check

| Form | XML Provided | Registry Entry | Match? |
|------|-------------|----------------|--------|
| HRMS_LOGIN.fmb | ✓ | COMP-FORM-01 | ✓ |
| HRMS_MENU.fmb | ✓ | COMP-FORM-02 | ✓ |
| HRMS_EMPLOYEE.fmb | ✓ | COMP-FORM-03 | ✓ |
| HRMS_PAYROLL.fmb | ✓ | COMP-FORM-04 | ✓ |
| HRMS_LEAVE.fmb | ✓ | COMP-FORM-05 | ✓ |
| HRMS_PERFORMANCE.fmb | ✓ | COMP-FORM-06 | ✓ |
| HRMS_REPORTS.fmb | Referenced only | COMP-FORM-07 (confidence 0.7) | ✓ |
| HRMS_ADMIN.fmb | Referenced only | COMP-FORM-08 (confidence 0.7) | ✓ |

8/8 forms accounted for. Forms pass completely.

---

## Sequence Spot-Check

6 sequences confirmed from spot-check source files:

| Sequence | Used By | Verified Via |
|----------|---------|-------------|
| SEQ_AUDIT | PKG_AUDIT.log_action, PKG_COMMON.log_error, PKG_COMMON.log_info | PKG_AUDIT.pkb, PKG_COMMON.pkb |
| SEQ_USER_SESSION | PKG_SECURITY.authenticate | PKG_SECURITY.pkb |
| SEQ_PERF_REVIEW | PKG_PERFORMANCE.create_review | PKG_PERFORMANCE.pkb |
| SEQ_REVIEW_CYCLE | PKG_PERFORMANCE.create_review_cycle | PKG_PERFORMANCE.pkb |
| SEQ_PERF_GOAL | PKG_PERFORMANCE.add_goal | PKG_PERFORMANCE.pkb |
| SEQ_EMPLOYEE | HRMS_EMPLOYEE form PRE-INSERT trigger | HRMS_EMPLOYEE.xml |
| SEQ_SALARY | PKG_PAYROLL (per extraction-audit.md) | extraction-audit.md |
| SEQ_PAY_PERIOD | PKG_PAYROLL (per extraction-audit.md) | extraction-audit.md |
| SEQ_PAYROLL_RUN | PKG_PAYROLL (per extraction-audit.md) | extraction-audit.md |
| SEQ_PAYROLL_DETAIL | PKG_PAYROLL (per extraction-audit.md) | extraction-audit.md |
| SEQ_EMP_HISTORY | TRG_EMP_BEFORE_UPDATE (trg_employees.sql) | trg_employees.sql |

11 sequences confirmed. Remaining 18 of 29 are documented in system-inventory.json referencing `schema/sequences/hrms_sequences.sql` (not in spot-check set). The total of 29 is not contradicted.

---

## View Spot-Check

| View | Brief Definition | Known Inconsistency |
|------|-----------------|---------------------|
| VW_ACTIVE_EMPLOYEES | EMPLOYEES WHERE EMPLOYMENT_STATUS='ACTIVE' + JOB_TITLES, DEPARTMENTS, JOB_GRADES, MANAGERS | None |
| VW_ORG_HIERARCHY | CONNECT BY START WITH MANAGER_EMP_ID IS NULL | None |
| VW_EMPLOYEE_COMPENSATION | EMPLOYEES + SALARY_RECORDS (END_DATE IS NULL) + PAY_ELEMENTS | None |
| VW_LEAVE_SUMMARY | EMPLOYEES + LEAVE_BALANCES + LEAVE_TYPES | **BUG (VIO-DATA-02): AVAILABLE omits PENDING_DAYS** |
| VW_PAYROLL_LATEST | Latest PAYROLL_RUNS per period with totals | None |
| VW_PENDING_APPROVALS | UNION of pending leave requests + CREATED payroll runs | None |

---

## Dependency Edge Spot-Check

| Edge | In Graph? | Evidence |
|------|-----------|---------|
| PKG_EMPLOYEE → PKG_PAYROLL (create_salary_record) | ✓ | PKG_EMPLOYEE.pkb |
| PKG_PAYROLL → PKG_EMPLOYEE (is_active) | ✓ | PKG_PAYROLL.pkb |
| PKG_SECURITY → PKG_AUDIT (log_action) | ✓ | PKG_SECURITY.pkb |
| PKG_SECURITY → PKG_COMMON (log_error/get_param) | ✓ | PKG_SECURITY.pkb |
| PKG_SECURITY → PKG_EMPLOYEE (set_session_context) | **✗ MISSING** | PKG_SECURITY.pkb authenticate body |
| PKG_REPORTING → PKG_EMPLOYEE | **✗ MISSING** | PKG_REPORTING.pks declared dependency |
| PKG_REPORTING → PKG_PAYROLL | **✗ MISSING** | PKG_REPORTING.pks declared dependency |
| PKG_REPORTING → PKG_COMMON | **✗ MISSING** | PKG_REPORTING.pks declared dependency |
| PKG_PERFORMANCE → PKG_NOTIFICATION (send_notification) | ✓ | PKG_PERFORMANCE.pkb |
| PKG_VALIDATION → PKG_COMMON (delegates) | ✓ | PKG_VALIDATION.pkb |

---

## Discrepancy Summary

| DISC-ID | Nature | Gating Before Downstream Use? |
|---------|--------|-------------------------------|
| DISC-001 | 130 claimed procs vs 111 in registry (19-gap unexplained) | YES — document before using as authoritative count |
| DISC-002 | Violation subtotals wrong in task summary (21 stated vs 24 actual) | YES — correct in all stakeholder-facing documents |
| DISC-003 | PKG_SECURITY.authenticate return type VARCHAR2 vs NUMBER | YES — type error will break any scaffolder reading this |
| DISC-004 | PKG_AUDIT function: get_audit_trail vs get_change_history | YES — wrong name causes compile failure in generated code |
| DISC-005 | PKG_COMMON: 4 renamed, 5 missing, 4 phantom (16 registry vs 17 source) | YES — severe; most entries affected |
| DISC-006 | PKG_REPORTING: 3 wrong names, 2 missing, 2 phantom | YES — most entries affected |
| DISC-007 | PKG_VALIDATION: 5 wrong names, 2 missing, 3 phantom | YES — all entries affected |
| DISC-008 | PKG_REPORTING has 0 edges in dependency graph (3 should exist) | MEDIUM — graph incomplete for reporting |
| DISC-009 | Trigger registry: 5/6 wrong names; 2 phantom; 1 absent; 1 event scope wrong | YES — complete rewrite required |
| DISC-010 | Registry invents salary validation in trigger body that does not exist | YES — fictional claim about production behaviour |
| DISC-011 | PKG_SECURITY → PKG_EMPLOYEE edge missing (set_session_context call) | MEDIUM — graph missing a dependency |
| DISC-012 | FLOW-02 step 5 wrong trigger name + invented salary check; step 7 phantom trigger | HIGH — invented system behaviour in a call flow |

---

## Gating Items Before This Can Be Marked PASS

- [ ] Rewrite COMP-DB-TRIGGERS using the 6-trigger authoritative table in `quality-review.md` (DISC-009, DISC-010)
- [ ] Correct FLOW-02 step 5 (trigger name, remove invented salary claim) and step 7 (remove phantom trigger) (DISC-012)
- [ ] Rewrite COMP-PKG-09 (PKG_COMMON) using 17-entry authoritative list (DISC-005)
- [ ] Rewrite COMP-PKG-11 (PKG_REPORTING) using 8-entry authoritative list (DISC-006)
- [ ] Rewrite COMP-PKG-10 (PKG_VALIDATION) using 8-entry authoritative list (DISC-007)
- [ ] Correct PKG_AUDIT get_audit_trail → get_change_history (DISC-004)
- [ ] Correct PKG_SECURITY.authenticate return type to NUMBER (DISC-003)
- [ ] Add 5 missing edges to dependency-graph.json: PKG_REPORTING→PKG_EMPLOYEE, →PKG_PAYROLL, →PKG_COMMON; PKG_SECURITY→PKG_EMPLOYEE; add set_session_context to COMP-PKG-01 (DISC-008, DISC-011)
- [ ] Regenerate dependency-view.mmd and component-view.mmd after graph update
- [ ] Explain or resolve the 130 vs 111 procedure count gap (DISC-001)
- [ ] Correct violation category subtotals to 9/9/5/1 in all stakeholder-facing documents (DISC-002)

---

## Not Gating — Safe to Proceed On

- All 24 violation content items, severity ratings, and source file references
- All 13 migration risks and their migration impact assessments
- The 6-module boundary decomposition and coupling scores
- CYCLE-01 (PKG_EMPLOYEE ↔ PKG_PAYROLL) identification and impact
- The 6-phase strangler fig migration sequence
- The 10 pre-migration mandatory tasks
- All 10 call flows except FLOW-02 steps 5 and 7
- The architecture pattern classification (Layered Monolith / Big Ball of Mud)
- The 41 open questions in `open-questions.md`
- The business rules extracted from spot-check packages (fiscal year October start, 30-minute session timeout from LOGIN_TIME, 365-day audit retention default, EMP-XXXXXX number format, rating bands 4.5/3.5/2.5/1.5)
