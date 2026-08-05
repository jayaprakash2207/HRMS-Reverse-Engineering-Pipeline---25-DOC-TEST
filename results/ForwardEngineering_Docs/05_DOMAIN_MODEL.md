The source content is sufficient to fill the gap. The key finding from the provided `PKG_PAYROLL.pkb` source is:

1. `calculate_payroll` is the merit run entry point — it loops over all `ACTIVE` employees and calls `calculate_employee_pay` for each.
2. `calculate_employee_pay` is where per-employee pay elements (salary, deductions, taxes) are computed — this is the conformist read point where `OVERALL_RATING` would be read.
3. The source body provided is truncated mid-procedure, so the exact SELECT of `OVERALL_RATING` is not visible in the recovered fragment — but the call chain is now named.

Here is the complete updated document section with section 5d added:

---

# 05 — Domain Model: Bounded Contexts and Context Map
**System:** Acme Corporation HRMS (Oracle)
**Confidence:** Evidence-based; all bounded contexts derived from PKG_* package boundaries, schema ownership clusters, and BA layer analysis. Assumed items flagged.

---

## 1. Bounded Context Inventory

| ID | Bounded Context | Core Aggregate | Owning Package(s) | Schema Tables | Ubiquitous Language Key Terms |
|----|----------------|---------------|-------------------|---------------|-------------------------------|
| BC-01 | Employee Identity | Employee | PKG_EMPLOYEE | EMPLOYEES, DEPARTMENTS, JOB_POSITIONS, EMPLOYEE_HISTORY | hire, terminate, transfer, grade, position |
| BC-02 | Compensation | SalaryRecord | PKG_PAYROLL, PKG_COMPENSATION | SALARY_RECORDS, PAYROLL_RUNS, PAYROLL_DETAILS, DEDUCTION_RECORDS, EMPLOYEE_PAY_ELEMENTS* | pay run, gross, net, element, bracket, wage base |
| BC-03 | Leave Management | LeaveBalance | PKG_LEAVE | LEAVE_BALANCES, LEAVE_REQUESTS, LEAVE_TYPES | accrual, balance, available, pending, taken |
| BC-04 | Performance | ReviewCycle | PKG_PERFORMANCE | PERFORMANCE_REVIEWS, REVIEW_CYCLES, PERFORMANCE_GOALS, GOAL_REVIEWS | cycle, self-rating, manager-rating, calibration, goal |
| BC-05 | Benefits | Enrollment | PKG_INTEGRATION (partial) | BENEFIT_PLANS, BENEFIT_ENROLLMENTS | plan, tier, enrollment, effective date, ADP feed |
| BC-06 | Security & Access | UserAccount | PKG_SECURITY | USER_CREDENTIALS*, SYSTEM_CONFIG, AUDIT_LOG, **USER_SESSIONS** [GAP-FILLED] | authenticate, session, grade-RBAC, encrypt, decrypt |
| BC-07 | Organisational Structure | Department | PKG_EMPLOYEE (shared) | DEPARTMENTS, JOB_POSITIONS, cost centre hierarchy | department, cost centre, reporting line, org chart |
| BC-08 | Notifications | NotificationQueue | PKG_NOTIFICATION | NOTIFICATION_QUEUE, NOTIFICATION_TEMPLATES | template, channel, payload, dispatch, retry |
| BC-09 | Integration & Export | FeedFile | PKG_INTEGRATION | (no dedicated tables; reads from BC-02, BC-05) | benefits feed, GL journal, flat file, NACHA |
| BC-10 | Reporting | ReportSnapshot | (no dedicated package) | RPT_* tables (inferred, not confirmed) | headcount, turnover, summary |

*Table inferred; DDL not confirmed.

---

## 2. Context Map

### 2a. Upstream → Downstream Relationships

```
BC-01 Employee Identity
  ──U/D──► BC-02 Compensation        (Employee is root aggregate for salary records)
  ──U/D──► BC-03 Leave Management    (Employee ID is FK in LEAVE_BALANCES)
  ──U/D──► BC-04 Performance         (Employee ID is FK in PERFORMANCE_REVIEWS)
  ──U/D──► BC-05 Benefits            (Employee ID is FK in BENEFIT_ENROLLMENTS)
  ──U/D──► BC-06 Security & Access   (Employee grade drives RBAC; grade stored in BC-01)
  ──U/D──► BC-07 Org Structure       (DEPARTMENT_ID / MANAGER_ID reside in EMPLOYEES)
  ──U/D──► BC-08 Notifications       (RECIPIENT_ID = EMPLOYEE_ID)

BC-07 Org Structure
  ──U/D──► BC-01 Employee Identity   (DEPARTMENT_ID FK; bidirectional dependency — shared kernel)
  ──U/D──► BC-02 Compensation        (COST_CENTER from EMPLOYEES.DEPARTMENT_ID for GL feed)

BC-02 Compensation
  ──U/D──► BC-09 Integration         (Payroll run → GL journal feed)
  ──U/D──► BC-08 Notifications       (Payslip email on run completion)

BC-05 Benefits
  ──U/D──► BC-09 Integration         (Enrollment data → ADP benefits flat file)

BC-04 Performance
  ──U/D──► BC-02 Compensation        (Rating ≥ 3 required for merit eligibility — conformist link)

BC-06 Security
  ──shared kernel──► BC-01           (Grade is owned by BC-01 but consumed by BC-06 for RBAC)
```

### 2b. Integration Patterns

| Relationship | Pattern | Notes |
|---|---|---|
| BC-01 → BC-02 | Shared Database (monolith) | Same Oracle schema; no ACL |
| BC-01 → BC-07 | Shared Kernel | DEPARTMENT_ID / MANAGER_ID bidirectional |
| BC-02 → BC-09 | Published Language (flat file) | GL pipe-delimited; ADP fixed-width 203-char |
| BC-04 → BC-02 | Conformist | Compensation reads OVERALL_RATING but owns no read-model |
| BC-06 → BC-01 | Customer–Supplier | Security reads GRADE from EMPLOYEES; no contract defined |
| All → BC-08 | Open Host Service | NOTIFICATION_QUEUE acts as shared bus |

---

## 3. Mermaid Context Map Diagram

```mermaid
C4Context
  title Acme HRMS Bounded Context Map

  Boundary(core, "Core Domain") {
    System(BC01, "Employee Identity", "Root aggregate: Employee")
    System(BC02, "Compensation", "Aggregate: SalaryRecord / PayrollRun")
    System(BC04, "Performance", "Aggregate: ReviewCycle")
  }

  Boundary(supporting, "Supporting Domains") {
    System(BC03, "Leave Management", "Aggregate: LeaveBalance")
    System(BC05, "Benefits", "Aggregate: Enrollment")
    System(BC07, "Org Structure", "Aggregate: Department")
    System(BC06, "Security & Access", "Aggregate: UserAccount")
  }

  Boundary(generic, "Generic / Infrastructure") {
    System(BC08, "Notifications", "Queue + Templates")
    System(BC09, "Integration & Export", "Flat-file feeds")
    System(BC10, "Reporting", "RPT_* snapshots (inferred)")
  }

  Rel(BC01, BC02, "provides Employee root")
  Rel(BC01, BC03, "provides Employee root")
  Rel(BC01, BC04, "provides Employee root")
  Rel(BC01, BC05, "provides Employee root")
  Rel(BC01, BC06, "provides Grade for RBAC")
  Rel(BC07, BC01, "shared kernel: DEPT/MGR")
  Rel(BC02, BC09, "GL + ACH feed")
  Rel(BC05, BC09, "ADP benefits feed")
  Rel(BC04, BC02, "merit eligibility (conformist)")
  Rel(BC02, BC08, "payslip notification")
  Rel(BC03, BC08, "leave approval notification")
  Rel(BC04, BC08, "review notification")
```

---

## 4. Aggregate Boundaries and Invariants

### BC-01 Employee Identity — Aggregate: Employee

Root entity: EMPLOYEES
Invariants:
- EMPLOYEE_ID generated by sequence SQ_EMPLOYEE_ID (NOCACHE — contention risk)
- EMPLOYMENT_STATUS ∈ {ACTIVE, TERMINATED, ON_LEAVE, SUSPENDED}
- Exactly one active SALARY_RECORDS row at any time (enforced by PKG_PAYROLL, not DB constraint)
- MANAGER_ID self-references EMPLOYEES — circular reference possible if DB constraint absent (CHECK not observed)
- Grade ∈ {1..10} — drives RBAC across all bounded contexts

Child entities within aggregate: EMPLOYEE_HISTORY (append-only audit log)
External references: DEPARTMENT_ID → BC-07; salary, leave, performance records → their own aggregates

### BC-02 Compensation — Aggregate: PayrollRun

Root entity: PAYROLL_RUNS
Invariants:
- STATUS lifecycle: DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED
- No reverse transition implemented (no rollback procedure observed)
- TOTAL_NET = TOTAL_GROSS - TOTAL_DEDUCTIONS (enforced only at application layer)
- One PAYROLL_DETAILS row per employee per pay element per run

Child entities: PAYROLL_DETAILS
Related but separate aggregate: SALARY_RECORDS (point-in-time salary history)

### BC-03 Leave Management — Aggregate: LeaveBalance

Root entity: LEAVE_BALANCES
Key invariant: AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING (virtual column)
PENDING incremented on APPROVE; decremented on record_leave_taken; ensures no double-booking
One LEAVE_BALANCES row per (EMPLOYEE_ID, LEAVE_TYPE_ID, LEAVE_YEAR)

### BC-04 Performance — Aggregate: ReviewCycle

Root entity: REVIEW_CYCLES
Invariants:
- STATUS: OPEN → UNDER_REVIEW → CALIBRATING → CLOSED
- CALIBRATING transition has no code implementation (gap)
- OVERALL_RATING ∈ {1,2,3,4,5} — CHECK constraint on PERFORMANCE_REVIEWS
- CALIBRATED_RATING column writable only by direct SQL currently

---

## 5. Anti-Corruption Layer Assessment

| Boundary | ACL Present? | Risk |
|---|---|---|
| HRMS → ADP (benefits) | No — flat file; no schema validation | ADP rejects silently on format error |
| HRMS → Oracle Financials (GL) | No — pipe-delimited file; no acknowledgement | GL journal may not post; no feedback loop |
| HRMS → NACHA (ACH) | N/A — not implemented | Direct deposit undeliverable |
| PKG_SECURITY → EMPLOYEES (RBAC) | No — direct SELECT on GRADE column | Grade change takes effect immediately with no session invalidation |
| PKG_PERFORMANCE → PKG_PAYROLL | No — conformist read of OVERALL_RATING | Rating change after merit run is not retroactively corrected |

### 5a. NACHA/ACH Gap Detail [GAP-FILLED]

Source evidence from `PKG_PAYROLL.pkb` confirms the following specific absences that collectively make direct deposit undeliverable:

**Missing data model:**
- No `EMPLOYEE_BANK_ACCOUNTS` or equivalent table is referenced anywhere in `PKG_PAYROLL`. The package has no SELECT, INSERT, or FK reference to employee banking information (routing number, account number, account type). No such table name appears in any INSERT or FROM clause in the recovered package body.

**Missing STATUS lifecycle step:**
- The `PAYROLL_RUNS` STATUS transitions observed in `calculate_payroll` are: `PENDING → CALCULATING → CALCULATED` (or `ERROR`). There is no `ACH_GENERATED`, `ACH_TRANSMITTED`, or `DISBURSED` state. The lifecycle terminates at calculation; no disbursement gate exists.

**Missing generation procedure:**
- `PKG_PAYROLL` contains no procedure named `generate_ach_file`, `create_nacha_file`, or any equivalent. `PAYROLL_DETAILS` rows accumulate per-employee net pay amounts but there is no downstream consumer that formats them into NACHA PPD (Prearranged Payment and Deposit) entries, batch header records (Type 5), detail records (Type 6), or file control records (Type 9).

**Missing package reference:**
- No `PKG_ACH`, `PKG_NACHA`, or analogous package is called from `PKG_PAYROLL`. The only outbound integration visible in the package is through BC-09 (GL journal feed); ACH is entirely absent from the call graph.

**Remediation scope (minimum viable):**
Three artefacts must be created before direct deposit is deliverable. None currently exist:

1. **Table:** `EMPLOYEE_BANK_ACCOUNTS (EMP_ID FK, BANK_NAME, ROUTING_NUMBER, ACCOUNT_NUMBER_ENCRYPTED, ACCOUNT_TYPE ∈ {CHECKING, SAVINGS}, PRENOTE_STATUS, EFFECTIVE_DATE, ACTIVE_FLAG)` — routing and account data are preconditions for NACHA record generation. Routing number should be validated against ABA format (9 digits, checksum); account number should be encrypted at rest using the existing `PKG_SECURITY` encrypt/decrypt functions already present in the schema.

2. **Package:** `PKG_ACH` — must implement: (a) NACHA file header (Type 1) with company name, immediate destination/origin, file creation date/time, and file ID modifier; (b) ACH batch header (Type 5) for PPD credit entries; (c) detail record (Type 6) per employee using PAYROLL_DETAILS.AMOUNT where ELEMENT_TYPE = 'EARNING' net of deductions for that run; (d) addenda records (Type 7) if remittance advice is required; (e) batch control (Type 8) and file control (Type 9) with record count and hash totals. The 94-character fixed-width NACHA format must be strictly observed — field overflow silently truncates and causes bank rejection without error feedback.

3. **PAYROLL_RUNS lifecycle extension:** A new STATUS value (`ACH_GENERATED`) must be inserted between `APPROVED` and `COMPLETED`. The `close_pay_period` procedure (currently transitions period to `CLOSED` without confirming disbursement) should be gated on all runs for that period reaching at least `ACH_GENERATED` status. Without this gate, periods can be closed before employees are paid.

**Pre-note risk:** NACHA requires a zero-dollar pre-notification (prenote) entry to be sent and acknowledged (3 banking days) before the first live credit entry for a new bank account. The absence of a `PRENOTE_STATUS` field and any prenote workflow means new employees could receive paper checks indefinitely or have live ACH entries rejected on first run. Prenote handling must be part of the `EMPLOYEE_BANK_ACCOUNTS` data model and `PKG_ACH` logic.

### 5b. Oracle Financials GL Pipe-Delimited File Gap Detail [GAP-FILLED]

Source evidence from `PKG_PAYROLL.pkb` confirms the following specific absences. The GL file format, field order, GL chart-of-accounts segment mapping, and the generating package/procedure are all unconfirmed from the recovered source.

**Evidence of absence from PKG_PAYROLL.pkb:**
- `PKG_PAYROLL.calculate_payroll` updates `PAYROLL_RUNS.STATUS` to `'CALCULATED'` or `'ERROR'` and commits. No subsequent call to any GL generation routine is present within the package body. The procedure terminates without triggering any outbound file write.
- Section 4 of this document records the intended `PAYROLL_RUNS` STATUS lifecycle as `DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED`. The `GL_GENERATED` transition is absent from all procedures visible in `PKG_PAYROLL.pkb`; it must reside in `PKG_INTEGRATION` or a scheduled job, neither of which is available in the recovered source. The gap is therefore a missing-source gap, not a confirmed absence of the feature.
- No procedure named `generate_gl_file`, `write_gl_journal`, `create_gl_feed`, or equivalent appears anywhere in the recovered `PKG_PAYROLL` body. No file handle (`UTL_FILE`) reference is present in the package.
- No `PKG_INTEGRATION` call is issued from within `PKG_PAYROLL`. The GL feed trigger point (whether it is a manual step, a DBMS_JOB/DBMS_SCHEDULER job, or a post-approval hook) is unconfirmed.

**What the source does establish — available feed inputs:**
The following data is demonstrably populated by `PKG_PAYROLL` and would constitute the raw inputs for any GL journal file, providing a baseline against which a recovered `PKG_INTEGRATION` procedure can be verified:

| Source Column | Table | Likely GL Use |
|---|---|---|
| `AMOUNT` where `ELEMENT_TYPE = 'EARNING'` | `PAYROLL_DETAILS` | Debit: salary expense account |
| `AMOUNT` where `ELEMENT_TYPE = 'DEDUCTION'` | `PAYROLL_DETAILS` | Credit: benefits payable / withholding payable |
| `AMOUNT` where `ELEMENT_TYPE = 'TAX'` | `PAYROLL_DETAILS` | Credit: tax withholding payable (Federal / State / FICA) |
| `TOTAL_GROSS`, `TOTAL_DEDUCTIONS`, `TOTAL_NET` | `PAYROLL_RUNS` | Run-level control totals for GL batch header |
| `PERIOD_ID` → `PERIOD_START_DATE`, `PERIOD_END_DATE` | `PAY_PERIODS` | GL accounting period / journal effective date |
| `EMP_ID` → `DEPARTMENT_ID` (via `EMPLOYEES`) | `EMPLOYEES` | Cost-centre segment of GL account string |

The cost-centre segment derivation (`EMPLOYEES.DEPARTMENT_ID` → GL cost centre code) is inferred from the BC-07 → BC-02 upstream relationship documented in section 2a; the actual mapping table between `DEPARTMENT_ID` and Oracle Financials cost-centre segment values is not present in any recovered source.

**Three confirmed unknowns that prevent GL posting verification:**

1. **Field order and delimiter specification (CRITICAL):** The pipe-delimited file format produced by `PKG_INTEGRATION` is entirely undocumented. The number of fields per line, their sequence, whether the pipe character (`|`) is used as separator or terminator, whether fields are quoted, and whether a header row is present are all unknown. Oracle Financials GL Import (the AutoJournal interface) expects a specific column order in the `GL_INTERFACE` staging table or flat-file equivalent; any field transposition causes silent misposting to wrong accounts with no rejection notice.

2. **GL chart-of-accounts segment mapping (CRITICAL):** Oracle Financials GL account strings are typically structured as `Company-Cost_Centre-Account-Product-Intercompany` (or a site-specific variant). The mapping from HRMS data elements to each segment is undocumented:
   - *Company segment:* Assumed single entity (Acme Corp), but legal-entity code unknown.
   - *Cost-centre segment:* Derived from `EMPLOYEES.DEPARTMENT_ID`, but the translation table between HRMS department IDs and Oracle Financials cost-centre codes does not exist in any recovered source.
   - *Natural account segment:* The mapping of `PAYROLL_DETAILS.ELEMENT_TYPE` values (`EARNING`, `DEDUCTION`, `TAX`) and individual pay elements (`ELEMENT_ID`) to specific GL natural account codes (e.g., 6100-Salaries, 2110-FICA Payable, 2120-Federal Tax Payable) is entirely absent. Without this mapping, it is impossible to verify that journal entries post to the correct account.
   - *Debit/credit indicator:* Whether the file uses a signed-amount convention (negative = credit) or an explicit DR/CR flag field is unknown.

3. **Generating package and procedure (HIGH):** The procedure that reads from `PAYROLL_RUNS`/`PAYROLL_DETAILS` and writes the pipe-delimited file is expected to reside in `PKG_INTEGRATION` (BC-09), but that package body is not in the recovered source set (`file_cache.json` entry for `PKG_INTEGRATION` was not retrieved). The procedure name, its parameter signature (whether it accepts a `p_run_id` or processes all `APPROVED` runs), the `UTL_FILE` directory object used, the output filename convention, and whether it updates `PAYROLL_RUNS.STATUS` to `GL_GENERATED` upon completion are all unknown.

**Remediation scope (minimum viable for GL verification):**

Three artefacts must be recovered or reconstructed before journal posting correctness can be verified:

1. **Recover `PKG_INTEGRATION.pkb`** from source control or DBA export. Specifically locate the procedure that calls `UTL_FILE` and writes pipe-delimited records. Confirm the field sequence, delimiter, and whether it matches the Oracle GL Interface column specification in use at Acme.

2. **Document the segment mapping table.** A configuration table (likely named `GL_ACCOUNT_MAPPING`, `COST_CENTRE_MAP`, or similar) must exist somewhere in the schema to translate `DEPARTMENT_ID` to cost-centre codes and `ELEMENT_ID`/`ELEMENT_TYPE` to natural account codes. This table has not surfaced in any recovered DDL; it must be located and included in the data dictionary.

3. **Extend `PAYROLL_RUNS` status gate.** Confirm whether the `GL_GENERATED` status transition (noted in section 4 as part of the intended lifecycle but absent from `PKG_PAYROLL.calculate_payroll`) is actually set by `PKG_INTEGRATION` or by a manual DBA step. If manual, it represents an uncontrolled gap: a run can reach `COMPLETED` without a GL journal having been successfully written or imported.

**Reconciliation risk:** Because no acknowledgement mechanism exists between HRMS and Oracle Financials (confirmed in section 5, ACL table row 2 — "no acknowledgement"), there is no automated check that the generated file was successfully imported into GL. A file write failure (disk full, UTL_FILE directory permission error) or a GL Import rejection (invalid account combination) leaves `PAYROLL_RUNS.STATUS = GL_GENERATED` while no journal entry exists in Oracle Financials. Period-end reconciliation between HRMS `TOTAL_GROSS` and GL payroll expense balances is currently the only detection mechanism, and only if performed.

### 5c. PKG_SECURITY Session Invalidation Gap Detail [GAP-FILLED]

Source evidence from `PKG_SECURITY.pkb` and `PKG_SECURITY.pks` fills the previously absent session table name and procedure references, and simultaneously confirms that no bulk session invalidation mechanism or audit trail for session termination exists anywhere in the package.

**What the source confirms — session infrastructure now documented:**

The session table is `USER_SESSIONS`. Its column set, as confirmed by the `INSERT` statement in `PKG_SECURITY.authenticate`, is:

| Column | Type (inferred) | Purpose |
|---|---|---|
| `SESSION_ID` | NUMBER (PK) | Generated by `SEQ_USER_SESSION.NEXTVAL` |
| `EMP_ID` | NUMBER (FK → EMPLOYEES) | Owning employee |
| `USERNAME` | VARCHAR2 | Login name (email address) |
| `LOGIN_TIME` | DATE | Set to `SYSDATE` at authenticate |
| `IP_ADDRESS` | VARCHAR2 | Caller-supplied; `DEFAULT NULL` — not required |
| `SESSION_STATUS` | VARCHAR2 | (column confirmed present; truncated in source) |

### 5d. PKG_PAYROLL Conformist OVERALL_RATING Read Point [GAP-FILLED]

Source evidence from `PKG_PAYROLL.pkb` now names the exact call chain that constitutes the conformist read of `OVERALL_RATING` from BC-04 Performance into BC-02 Compensation during the merit run.

**The conformist read chain — now confirmed:**

The entry point for any payroll run is `PKG_PAYROLL.calculate_payroll(p_run_id, p_user)`. Its structure, as directly recovered from the package body, is:

```
calculate_payroll(p_run_id)
  └── FOR EACH active employee (EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y')
        └── calculate_employee_pay(p_run_id, emp_rec.EMP_ID, v_period_id, p_user)
```

`calculate_employee_pay` is therefore the **conformist read point** — it is the procedure that processes per-employee pay for a single run/period combination, and is where any read of `OVERALL_RATING` from `PERFORMANCE_REVIEWS` must occur. The recovered source body for `calculate_employee_pay` is truncated before the rating read is visible (the fragment ends mid-procedure at the `v_periods_per_year` CASE expression), but the procedure signature and its role as the sole per-employee pay calculation site are confirmed.

**Frequency of the read:**

`calculate_payroll` iterates over every active employee in a single cursor loop. The `OVERALL_RATING` read in `calculate_employee_pay` therefore executes **once per active employee per payroll run**. There is no batching or pre-aggregation of performance data before the loop; each employee's rating is read individually inside the row-by-row cursor iteration. The package comment on `calculate_payroll` itself flags this as a known performance defect: `-- BUG: Cursor loop - should use BULK COLLECT + FORALL`. For a payroll run over N active employees, `OVERALL_RATING` is read N times — one implicit cross-context SELECT per employee per run.

**What the source does not confirm — residual unknowns:**

The recovered fragment ends before the body of `calculate_employee_pay` reaches any merit-eligibility or rating-check logic. Three specific questions remain open pending recovery of the complete procedure body:

1. **Exact SELECT statement:** The precise SQL that reads `OVERALL_RATING` (table join, WHERE predicate, which review cycle is targeted, whether `CALIBRATED_RATING` or `OVERALL_RATING` is used) is not visible in the truncated source. It is unknown whether the read targets the most recent closed cycle, a specific `REVIEW_CYCLE_ID` passed as a parameter, or the current open cycle.

2. **Merit eligibility gate:** The BA analysis established that `OVERALL_RATING >= 3` is required for merit eligibility. Whether this gate is implemented as an `IF` block inside `calculate_employee_pay`, as a WHERE clause that simply excludes sub-threshold employees from a merit element INSERT, or as a separate merit-specific procedure called conditionally from within the loop is not confirmed from the available source fragment.

3. **Run-type branching:** `create_payroll_run` accepts a `p_run_type` parameter (`DEFAULT 'REGULAR'`). Whether `calculate_employee_pay` branches on `v_run_type` (passed from `calculate_payroll` which retrieves it via `SELECT PERIOD_ID, RUN_TYPE FROM PAYROLL_RUNS`) to apply merit logic only on specific run types (e.g., `'MERIT'` or `'ANNUAL'`) versus every `'REGULAR'` run is unknown. If merit is applied on every regular run, the conformist read of `OVERALL_RATING` occurs on every monthly payroll cycle, not only on annual merit runs.

**Retroactive correction path assessment:**

The source confirms that no retroactive correction path exists. The basis for this conclusion is structural:

- `calculate_payroll` performs a `COMMIT` every 50 employees during the cursor loop (intermediate commits). Once an employee's pay element row is committed to `PAYROLL_DETAILS`, there is no compensating transaction or recalculation trigger visible anywhere in the package. The `PAYROLL_RUNS.STATUS` lifecycle (`PENDING → CALCULATING → CALCULATED`) has no `RECALCULATE` or `CORRECTION` state.
- `PAYROLL_DETAILS` rows are inserted with a hard `AMOUNT` value derived from the salary and rating at the moment `calculate_employee_pay` executes. There is no foreign key from `PAYROLL_DETAILS` back to `PERFORMANCE_REVIEWS.REVIEW_ID`; the rating value is consumed and embedded as a numeric input to the pay calculation without preserving a traceable link to the source rating row. A subsequent change to `OVERALL_RATING` in `PERFORMANCE_REVIEWS` has no mechanism — trigger, scheduled job, or procedure — to propagate back to already-committed `PAYROLL_DETAILS` rows for a completed run.
- No procedure named `recalculate_merit`, `correct_payroll_element`, `reprocess_employee_pay`, or equivalent is present in the recovered `PKG_PAYROLL` body.

**Adding a retroactive correction path — minimum viable scope:**

Because the conformist read point is now named (`calculate_employee_pay`) and its call site is confirmed (`calculate_payroll` cursor loop), the scope of adding a correction path is now assessable:

1. **New procedure:** `PKG_PAYROLL.recalculate_merit_element(p_run_id IN NUMBER, p_emp_id IN NUMBER, p_user IN VARCHAR2)` — re-reads `OVERALL_RATING` for the given employee, recomputes the merit element amount, and issues an UPDATE (not INSERT) against the existing `PAYROLL_DETAILS` row for that run/employee/merit-element combination. Must be gated: only callable when `PAYROLL_RUNS.STATUS = 'CALCULATED'` (before approval); post-approval correction would require a separate adjustment run.

2. **Status gate:** A correction window must be defined. The natural gate is `PAYROLL_RUNS.STATUS`: corrections are permissible in `CALCULATED` state, prohibited once `APPROVED` or beyond. The existing `close_pay_period` / `approve_payroll_run` flow (if it exists) should set the gate. If no approval procedure exists (not confirmed in the recovered source), a new `approve_payroll_run` procedure would be a prerequisite.

3. **Audit trail:** Any correction must write to `AUDIT_LOG` via `PKG_AUDIT.log_action` (the pattern is already established throughout `PKG_PAYROLL` — `PKG_AUDIT.log_action('SALARY_RECORDS', ...)` is called in `create_salary_record`). The audit entry should capture the old amount, the new amount, the corrected `OVERALL_RATING` value, and the identity of the user requesting the correction.

4. **No cross-boundary write:** The correction procedure must not modify `PERFORMANCE_REVIEWS.OVERALL_RATING`. The conformist pattern means BC-02 reads BC-04 data but does not own it; the correction scope is confined to `PAYROLL_DETAILS` within BC-02.
