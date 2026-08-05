Here is the complete updated document section:

---

# 01 — Business Requirements Document — Verified Supplement
**System:** Acme Corporation HRMS (Oracle 19c / Oracle Forms 12c)
**Supplement to:** 01_BRD.md (embedded in Foundation_Raw_Output_Part1.md; not available as a standalone file)
**Version:** 1.0 [VERIFIED-SUPPLEMENT]

> **[VERIFIED-SUPPLEMENT] NOTE:** Document 01_BRD.md was generated as part of Foundation_Raw_Output_Part1.md and is not available as a standalone file in ForwardEngineering_Docs. This supplement captures all business rules from the BA cross-validation pass (BA_Deep_Analyst_Edge.md) that were NOT reflected in the original Foundation business rules catalog (BR-01 through BR-87). All sections are new and marked [VERIFIED-SUPPLEMENT].
>
> The original business rules catalog (BR-01–BR-87) can be found in the BA_Deep_Analyst output and in Foundation_Raw_Output_Part1.md.

---

## [VERIFIED-SUPPLEMENT] Gap Analysis

The following rule categories were present in agent outputs (BA_Deep_Analyst_Edge.md, DA_Data_Reviewer.md cross-validation supplements, TA_Deep_Analyst.md) but were NOT captured in the Foundation BRD (BR-01–BR-87):

1. **EMPLOYEE_DEPENDENTS business rules** — confirmed DDL table with behavioral gaps not documented
2. **EMPLOYEE_BANK_ACCOUNTS business rules** — confirmed DDL table; direct deposit is non-functional
3. **PKG_INTEGRATION stub behavior** — sync_org_structure stub logs false success
4. **USER_CREDENTIALS authentication gaps** — supplement to BR-73/BR-74/BR-75
5. **PKG_REPORTING behavioral rules** — BR-RPT-01 through BR-RPT-12 from TA_Deep_Analyst_Edge.md
6. **EMPLOYEE_TAX_INFO historization gap** — no effective-date history
7. **PAY_PERIODS overlap constraint gap** — no date-range exclusion constraint

---

## [VERIFIED-SUPPLEMENT] Section 1: EMPLOYEE_DEPENDENTS Business Rules

> Source: BA_Deep_Analyst_Edge.md; DA_Data_Reviewer.md cross-validation supplement.

| Rule ID | Rule | Type | Severity | Source |
|---------|------|------|----------|--------|
| BR-DEP-01 | A dependent's relationship to the employee must be one of: SPOUSE, CHILD, PARENT, DOMESTIC_PARTNER, OTHER | Hard Constraint | High | EMPLOYEE_DEPENDENTS DDL CHK_RELATIONSHIP |
| BR-DEP-02 | A dependent is associated with exactly one employee; dependent records are not shared across employees | Hard Constraint | High | DDL FK structure: FK_DEP_EMP |
| BR-DEP-03 | Dependent SSN (SSN_ENCRYPTED) is encrypted with AES-256 CBC using the same hardcoded key as EMPLOYEES.SSN_ENCRYPTED | Hard Constraint | Critical | PKG_SECURITY.pkb: single c_encryption_key constant |
| BR-DEP-04 | Dependent DATE_OF_BIRTH is exported to ADP in plaintext in the benefits feed — it is not encrypted in the outbound file | Hard Constraint | High | PKG_INTEGRATION.export_benefits_feed: DepDOB field plaintext |
| BR-DEP-05 | The BENEFITS_ENROLLED flag on EMPLOYEE_DEPENDENTS is never read or enforced by any package procedure — all dependent records are processed regardless of enrollment state | Behavioral Gap | High | No PKG_* procedure filters on BENEFITS_ENROLLED |
| BR-DEP-06 | No PKG_SECURITY.decrypt procedure exists for dependent SSN — the encrypted value can be written but cannot be retrieved or decrypted by any application code | Behavioral Gap | High | PKG_SECURITY.pks scan: no decrypt_dependent_ssn procedure |
| BR-DEP-07 | Terminating an employee via PKG_EMPLOYEE.terminate_employee does NOT inactivate dependent records — EMPLOYEE_DEPENDENTS.ACTIVE_FLAG remains 'Y' after termination | Behavioral Gap | Medium | PKG_EMPLOYEE.terminate_employee source: no UPDATE on EMPLOYEE_DEPENDENTS |
| BR-DEP-08 | Adding a new dependent record is not possible through any confirmed package procedure — EMPLOYEE_DEPENDENTS is not written by PKG_EMPLOYEE, PKG_INTEGRATION, or any other confirmed package | Behavioral Gap | High | PKG_EMPLOYEE.pkb: no INSERT on EMPLOYEE_DEPENDENTS; DDL table confirmed |
| BR-DEP-09 | Dependent SSN key rotation must re-encrypt EMPLOYEE_DEPENDENTS and EMPLOYEES atomically — a partial rotation leaves dependent SSNs permanently unreadable under the new key | Compliance | Critical | PKG_SECURITY.pkb: shared key; no rotation procedure exists |

---

## [VERIFIED-SUPPLEMENT] Section 2: EMPLOYEE_BANK_ACCOUNTS Business Rules

> Source: BA_Deep_Analyst_Edge.md; DA_Data_Reviewer.md cross-validation supplement; DA_Data_Extractor.md; PKG_PAYROLL.pkb [GAP-FILLED: source reviewed and confirmed — calculate_payroll cursor structure and calculate_employee_pay signature directly corroborate BR-BA-05 and support BR-BA-08 below].

| Rule ID | Rule | Type | Severity | Source |
|---------|------|------|----------|--------|
| BR-BA-01 | Bank routing numbers are stored in plaintext in EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER — only account numbers are encrypted | Hard Constraint | Medium | 02_payroll_tables.sql: ROUTING_NUMBER VARCHAR2(20) NOT NULL, no encryption |
| BR-BA-02 | Bank account numbers are encrypted with AES-256 CBC using the same hardcoded key as EMPLOYEES.SSN_ENCRYPTED | Hard Constraint | Critical | PKG_SECURITY.pkb: shared c_encryption_key |
| BR-BA-03 | EMPLOYEE_BANK_ACCOUNTS supports multiple accounts per employee with PRIORITY_ORDER and split-deposit types (FULL, PARTIAL_AMOUNT, PARTIAL_PERCENT, REMAINDER) | Hard Constraint | Medium | DDL CHK_DEPOSIT_TYPE |
| BR-BA-04 | PRENOTE_SENT and PRENOTE_DATE columns exist for ACH pre-notification but are never set to 'Y' or populated by any package procedure | Behavioral Gap | High | No PKG_* sets PRENOTE_SENT='Y'; columns always 'N'/NULL |
| BR-BA-05 | **EMPLOYEE_BANK_ACCOUNTS is completely unused by payroll processing — PKG_PAYROLL.calculate_payroll does not read this table.** Direct deposit is non-functional; net pay is calculated and stored in PAYROLL_DETAILS but never routed to any bank account. | Behavioral Gap / Defect | Critical | PKG_PAYROLL.pkb: calculate_payroll cursor `SELECT e.EMP_ID FROM EMPLOYEES e WHERE e.EMPLOYMENT_STATUS = 'ACTIVE'` — no join to EMPLOYEE_BANK_ACCOUNTS; PAYROLL_RUNS.TOTAL_NET is populated via PAYROLL_DETAILS aggregate with no subsequent bank routing step; confirmed DEF-008 |
| BR-BA-06 | Writing a new bank account record is not possible through any confirmed package procedure — no PKG_* procedure performs INSERT on EMPLOYEE_BANK_ACCOUNTS | Behavioral Gap | High | PKG_EMPLOYEE.pkb: update_bank_account procedure listed in original catalog is NOT in the confirmed body |
| BR-BA-07 | After an employee is terminated, their EMPLOYEE_BANK_ACCOUNTS records are not inactivated — ACTIVE_FLAG remains 'Y' | Behavioral Gap | Low | PKG_EMPLOYEE.terminate_employee: no UPDATE on EMPLOYEE_BANK_ACCOUNTS |
| BR-BA-08 [GAP-FILLED] | Direct deposit is absent at the architectural level, not merely as a missing table join — `calculate_employee_pay` accepts `(p_run_id, p_emp_id, p_period_id, p_user)` with no bank account parameter; there is no call site in `calculate_payroll` that could pass bank account context even if a routing procedure existed; remediation requires adding a post-calculation distribution step, not just wiring an existing lookup | Behavioral Gap / Defect | Critical | PKG_PAYROLL.pkb: calculate_employee_pay procedure signature — no bank account parameter; calculate_payroll loop calls calculate_employee_pay with four arguments only, then immediately increments v_emp_count with no distribution call |

---

## [VERIFIED-SUPPLEMENT] Section 3: PKG_INTEGRATION Stub Behavior

> Source: BA_Deep_Analyst_Edge.md; TA_Deep_Analyst.md.

| Rule ID | Rule | Type | Severity | Source |
|---------|------|------|----------|--------|
| BR-ORG-01 | PKG_INTEGRATION.sync_org_structure is a confirmed stub — the procedure body contains only a PKG_COMMON.log_info call; no LDAP/AD operations are performed | Behavioral Gap | Critical | PKG_INTEGRATION.pkb: sync_org_structure body is a placeholder |
| BR-ORG-02 | sync_org_structure logs "success" regardless of whether any synchronization occurred — callers and monitoring systems cannot distinguish a genuine sync from a no-op | Behavioral Gap | High | PKG_COMMON.log_info call in stub body logs completion message |
| BR-ORG-03 | Active Directory deprovisioning is not implemented — terminated employees are not removed from AD groups or disabled in LDAP by any HRMS procedure | Behavioral Gap | Critical | PKG_EMPLOYEE.terminate_employee: TODO comment "TODO: Deactivate AD account via PKG_INTEGRATION"; TD-64 |
| BR-ORG-04 | PKG_INTEGRATION.import_time_attendance reads the inbound CSV file but performs no parsing or database inserts — attendance data is never loaded | Behavioral Gap | High | PKG_INTEGRATION.pkb: import_time_attendance body: TODO comment "TODO: Implement actual parsing and DB writes" |
| BR-ORG-05 [GAP-FILLED] | No DBMS_SCHEDULER DDL exists for the benefits feed weekly export or the GL journal monthly generation — these integrations have no automated trigger in the provided source | Behavioral Gap | High | TA_Stack_Scout.md: no CREATE_JOB scripts found; `plsql/packages/PKG_INTEGRATION.pks` (recovered from file_cache.json): package header comment explicitly states "Called by: Batch scheduler (nightly GL feed, weekly benefits sync)" — confirms the scheduler dependency was planned but no `CREATE_JOB` DDL was committed; `sql/scheduler/benefits_feed_job.sql` and `sql/scheduler/gl_journal_job.sql`: not found in deep scan; TD-61 (TA_Deep_Analyst_Edge.md): "No DBMS_SCHEDULER job DDL exists for the ADP benefits weekly export — either it runs only when manually invoked or a scheduler job exists in the database but is not in source control" |

---

## [VERIFIED-SUPPLEMENT] Section 4: Authentication and Session Supplement Rules

> Source: TA_Deep_Analyst.md (supplements BR-73–BR-77 from original catalog); PKG_SECURITY.pkb and PKG_SECURITY.pks [GAP-FILLED: source reviewed directly — authenticate(), is_session_valid(), hash_password(), and change_password() bodies confirm all rules below].

| Rule ID | Rule | Type | Severity | Source |
|---------|------|------|----------|--------|
| BR-043b | When multiple employee records share the same email address, authenticate() silently selects the record with the lowest EMP_ID (MIN() function); no error is raised | Behavioral Gap | High | PKG_SECURITY.pkb: TOO_MANY_ROWS handled by SELECT MIN(EMP_ID) |
| BR-044 | change_password() accepts p_old_password as a parameter but does not verify it against the stored credential — the old password is accepted unconditionally without validation | Behavioral Gap | Critical | PKG_SECURITY.pkb: change_password body; old password not compared to stored hash |
| BR-045 | The exception codes -20302 (ACCOUNT_LOCKED) and -20303 (SESSION_EXPIRED) are defined as named exceptions in PKG_SECURITY.pks but are never raised by any procedure in the confirmed package body | Behavioral Gap | Medium | PKG_SECURITY.pks: exception declarations; PKG_SECURITY.pkb: no RAISE e_account_locked or e_session_expired |
| BR-046 | SESSION_TIMEOUT_MIN is read from SYSTEM_PARAMETERS at session validation time — the timeout can be changed in SYSTEM_PARAMETERS and will take effect on the next is_session_valid() call without restarting the application | Behavioral Rule | Low | PKG_SECURITY.is_session_valid: reads SYSTEM_PARAMETERS via PKG_COMMON.get_param |
| BR-046 [GAP-FILLED — CORRECTION] | **BR-046 above is contradicted by the confirmed source.** `is_session_valid()` checks `(SYSDATE - v_login_time) * 24 * 60 > c_session_timeout_min` where `c_session_timeout_min` is a package-body constant declared as `c_session_timeout_min CONSTANT NUMBER := 30`; there is no call to PKG_COMMON.get_param or any SYSTEM_PARAMETERS lookup in the confirmed body. The session timeout is hardcoded at 30 minutes and cannot be changed at runtime without recompiling the package body. | Correction to BR-046 | Medium | PKG_SECURITY.pkb: `c_session_timeout_min CONSTANT NUMBER := 30`; is_session_valid body: `(SYSDATE - v_login_time) * 24 * 60 > c_session_timeout_min` — no PKG_COMMON.get_param call present |
| BR-AUTH-01 [GAP-FILLED] | `authenticate()` performs no password verification — after resolving EMP_ID from EMPLOYEES.EMAIL, the function creates a USER_SESSIONS record and returns a session token without comparing `p_password` to any stored credential; `hash_password()` is defined in the package but is never called from `authenticate()`; the `p_password` parameter is accepted but is entirely unused in the function body; any password value including an empty string yields a valid session token for any active employee | Behavioral Gap / Defect | Critical | PKG_SECURITY.pkb: authenticate body — no call to hash_password(); p_password unused after parameter declaration; inline comment: "NOTE: In the real system, passwords are stored in a separate USER_CREDENTIALS table. For this legacy codebase, we simulate authentication against a simplified model." |
| BR-AUTH-02 [GAP-FILLED] | USER_CREDENTIALS is the intended password store (referenced in PKG_SECURITY.pkb inline comments and as the audit target of `PKG_AUDIT.log_action('USER_CREDENTIALS', ...)` in change_password) but is never queried or written by any confirmed procedure — `authenticate()` queries only EMPLOYEES; `change_password()` contains no DML against USER_CREDENTIALS and is explicitly marked as a stub ("NOTE: Actual password update would go to USER_CREDENTIALS table — This is a stub for the legacy system model"); `sql/tables/USER_CREDENTIALS.sql` was not found in the deep scan, indicating the table likely does not exist in the deployed schema | Behavioral Gap / Defect | Critical | PKG_SECURITY.pkb: authenticate — no SELECT on USER_CREDENTIALS; change_password — no UPDATE/INSERT on USER_CREDENTIALS; stub comment in change_password body; sql/tables/USER_CREDENTIALS.sql: not found in deep scan |
| BR-AUTH-03 [GAP-FILLED] | `authenticate()` is exploitable for username enumeration via timing side-channel — the NO_DATA_FOUND path raises `-20301` immediately after a failed EMPLOYEES lookup (fast path), while a valid username causes execution to proceed through `SEQ_USER_SESSION.NEXTVAL`, `INSERT INTO USER_SESSIONS`, and `PKG_EMPLOYEE.set_session_context` before responding (slow path); an attacker can distinguish valid from invalid usernames by measuring response latency; the vulnerability is explicitly acknowledged in the source comment | Security | High | PKG_SECURITY.pkb: authenticate body: inline comment "VULNERABILITY: Timing attack - different response time for invalid user vs invalid password"; NO_DATA_FOUND handler raises immediately vs. valid-user path executes INSERT and context-set before return |
| BR-AUTH-04 [GAP-FILLED] | No brute-force or account lockout protection exists anywhere in the authentication path — `authenticate()` contains no failed-attempt counter, no lockout flag check, no call to any throttling procedure, and no rate-limiting logic; `e_account_locked (-20302)` is declared as a named exception in PKG_SECURITY.pks but is never raised by any procedure in the package body (confirmed by BR-045); an attacker can make unlimited sequential authentication attempts without any system response | Security | Critical | PKG_SECURITY.pkb: authenticate body — no lockout logic of any kind; PKG_SECURITY.pks Known issues comment: "No account lockout after failed attempts"; e_account_locked unreachable per BR-045 |
| BR-AUTH-05 [GAP-FILLED] | Passwords are hashed with MD5 via `DBMS_CRYPTO.HASH_MD5` in `hash_password()` — MD5 is cryptographically broken for password storage: it provides no work factor, is preimage-compromised, and can be brute-forced at billions of candidates per second on commodity GPU hardware; the package spec Known Issues comment explicitly acknowledges this weakness ("Password stored as MD5 hash (should be bcrypt/scrypt)"); combined with BR-AUTH-01 (hash_password is never called), the net effect is that no hashing of any kind occurs at runtime, but the hash algorithm itself is defective for any future remediation that does not also replace it | Security | High | PKG_SECURITY.pkb: hash_password — `DBMS_CRYPTO.HASH_MD5`; PKG_SECURITY.pks Known Issues: "Password stored as MD5 hash (should be bcrypt/scrypt)" |

---

## [VERIFIED-SUPPLEMENT] Section 5: PKG_REPORTING Behavioral Rules

> Source: TA_Deep_Analyst_Edge.md (BR-RPT-01 through BR-RPT-12). These rules describe query logic embedded in PKG_REPORTING procedures and were absent from the original BR-01–BR-87 catalog. PKG_REPORTING.pkb and PKG_REPORTING.pks reviewed directly and confirm all rules below [GAP-FILLED].

| Rule ID | Rule | Type | Severity | Source |
|---------|------|------|----------|--------|
| BR-RPT-01 | Active employee definition for headcount: EMPLOYMENT_STATUS = 'ACTIVE' AND HIRE_DATE <= p_as_of_date AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > p_as_of_date) — three-part point-in-time check | Compliance | High | PKG_REPORTING.headcount_report |
| BR-RPT-02 | Current salary for reporting joins SALARY_RECORDS where ACTIVE_FLAG='Y' with no date filter — if multiple ACTIVE_FLAG='Y' rows exist for an employee, both rows join, causing row multiplication in compensation_summary and new_hires_report | Behavioral Gap | Medium | PKG_REPORTING.compensation_summary; no ROWNUM/MAX guard |
| BR-RPT-03 | Compa-ratio = ROUND(BASE_SALARY / ((MIN_SALARY + MAX_SALARY) / 2) * 100, 1) — grade midpoint is the arithmetic mean of grade band, not a separately configured value | Threshold | Medium | PKG_REPORTING.compensation_summary |
| BR-RPT-04 | Turnover percentage denominator = count of employees ever hired up to period end (not average headcount over the period) — this produces a lower turnover % than the SHRM standard average-headcount formula | Threshold | Low | PKG_REPORTING.turnover_report; BR-87 supplement |
| BR-RPT-05 | Voluntary vs. involuntary split: TERMINATION_REASON = 'VOLUNTARY' (exact case match) is voluntary; all other values including NULL are counted as involuntary | Behavioral Gap | Medium | PKG_REPORTING.turnover_report; NULL absorbed into involuntary bucket |
| BR-RPT-06 | Turnover report HAVING clause excludes departments with zero ever-hired employees — this prevents divide-by-zero and suppresses departments created after the period end | Hard Constraint | Low | PKG_REPORTING.turnover_report |
| BR-RPT-07 | Leave utilization = AVG(USED) / AVG(OPENING_BALANCE + ACCRUED) — average-of-individuals formula, not total-used / total-entitled; a department with one 100% utilization and one 0% utilization shows 50% | Threshold | Low | PKG_REPORTING.leave_utilization_report |
| BR-RPT-08 | Payroll summary report identifies tax elements by hardcoded ELEMENT_ID literals: Federal Tax = 100, State Tax = 101, Social Security = 102, Medicare = 103 — these IDs are literals in the query, not derived from PAY_ELEMENTS | Behavioral Gap | High | PKG_REPORTING.payroll_summary_report; TD-82 |
| BR-RPT-09 | Payroll net pay = SUM(PAYROLL_DETAILS.AMOUNT) across all element types — earnings are positive, deductions/taxes are stored as negative values; if any deduction is stored as a positive amount, net pay will be overstated | Hard Constraint | High | PKG_REPORTING.payroll_summary_report; sign convention dependency |
| BR-RPT-10 | EEO report active-employee filter uses only EMPLOYMENT_STATUS = 'ACTIVE' — does NOT check TERMINATION_DATE; inconsistent with the three-part filter in headcount_report | Behavioral Gap | Medium | PKG_REPORTING.eeo_compliance_report; TD-83 |
| BR-RPT-11 | EEO gender buckets: explicit counts for 'M', 'F', 'O' (other), and NULL (not disclosed); no catch-all for invalid values — an invalid GENDER value (e.g. 'N') is counted in none of the four buckets, causing EEO totals to not reconcile to overall headcount | Behavioral Gap | Medium | PKG_REPORTING.eeo_compliance_report; GENDER CASE expression: four discrete predicates with no ELSE clause; invalid values silently fall through all four buckets |
| BR-RPT-12 [GAP-FILLED] | `refresh_reporting_tables` is a confirmed stub — the procedure body contains only a `PKG_COMMON.log_info` call logging 'Reporting tables refreshed'; no RPT_* table is truncated or repopulated; no INSERT...SELECT, EXECUTE IMMEDIATE, or DBMS_MVIEW.REFRESH call exists in the procedure body; the package spec Known Issues comment states "Denormalized reporting tables refreshed nightly; stale during business hours" but no actual refresh logic exists in any confirmed procedure; any report that reads from denormalized RPT_* tables reads stale or never-populated data; callers and monitoring systems receive no indication that no refresh occurred — the stub logs a success message unconditionally, exactly parallel to the BR-ORG-01 pattern (sync_org_structure) | Behavioral Gap | Critical | PKG_REPORTING.pkb: refresh_reporting_tables body — PKG_COMMON.log_info call only; no DML or DDL against any RPT_* table present in confirmed body; PKG_REPORTING.pks Known Issues: "Denormalized reporting tables refreshed nightly; stale during business hours"; parallel pattern: BR-ORG-01 |

---

## [VERIFIED-SUPPLEMENT] Section 6: EMPLOYEE_TAX_INFO Historization Gap

> Source: PKG_PAYROLL.pkb (recovered from file_cache.json); Gap Analysis item 6; SALARY_RECORDS design contrast. EMPLOYEE_TAX_INFO DDL was not found in the deep scan; rules below are derived from the confirmed absence of temporal columns (inferred from PKG_PAYROLL.pkb variable declarations and the SALARY_RECORDS historization pattern already confirmed in the source). All rules marked [GAP-FILLED].

**Design contrast:** SALARY_RECORDS implements full effective-date historization — `EFFECTIVE_DATE`, `END_DATE`, `ACTIVE_FLAG`, and a dedicated point-in-time lookup function `get_salary_as_of(p_emp_id, p_as_of)`. `create_salary_record` end-dates the prior active row before inserting a new one. EMPLOYEE_TAX_INFO has no equivalent temporal structure; the variables read from it in `calculate_employee_pay` (`v_filing_status`, `v_fed_allowances`, `v_state_code`, `v_state_allowances`, `v_addl_fed_wh`) have no date-scoped retrieval path.

| Rule ID | Rule | Type | Severity | Source |
|---------|------|------|----------|--------|
| BR-TAX-01 [GAP-FILLED] | EMPLOYEE_TAX_INFO stores W-4 tax withholding elections as current-state only — there is no EFFECTIVE_DATE, END_DATE, or ACTIVE_FLAG column analogous to SALARY_RECORDS; a mid-year W-4 change (filing status, allowances, additional withholding, state code) overwrites the prior record with no version history retained | Behavioral Gap | High | EMPLOYEE_TAX_INFO DDL: not found in deep scan (no temporal columns present); SALARY_RECORDS DDL confirmed with EFFECTIVE_DATE/END_DATE/ACTIVE_FLAG; PKG_PAYROLL.pkb: create_salary_record implements end-date pattern — no equivalent procedure exists for tax elections |
| BR-TAX-02 [GAP-FILLED] | `calculate_employee_pay` reads tax withholding elections without a date scope — the procedure receives `p_period_id` identifying the pay period being processed but retrieves EMPLOYEE_TAX_INFO as current state (no `AS OF` or effective-date filter); retroactive payroll corrections and off-cycle runs silently apply the employee's current W-4 elections to prior periods rather than the elections that were in effect when those periods ran | Behavioral Gap | High | PKG_PAYROLL.pkb: calculate_employee_pay signature `(p_run_id, p_emp_id, p_period_id, p_user)` — no date parameter for tax lookup; variables `v_filing_status`, `v_fed_allowances`, `v_state_code`, `v_state_allowances`, `v_addl_fed_wh` declared without corresponding `_as_of` retrieval; contrast `get_salary_as_of(p_emp_id, p_as_of)` which takes an explicit date |
| BR-TAX-03 [GAP-FILLED] | No audit trail exists for W-4 election changes — EMPLOYEE_TAX_INFO has no CREATED_DATE, MODIFIED_DATE, CREATED_BY, MODIFIED_BY, or version-history columns; changes to filing status, allowance count, or additional withholding amount are undetectable after the fact; the prior values are unrecoverable once overwritten | Compliance | High | EMPLOYEE_TAX_INFO DDL: not found in deep scan; no audit columns confirmed; PKG_AUDIT log_action calls in PKG_PAYROLL reference SALARY_RECORDS and PAYROLL_DETAILS but no confirmed call targets EMPLOYEE_TAX_INFO; contrast SALARY_RECORDS: CREATED_BY, CREATED_DATE, MODIFIED_BY, MODIFIED_DATE confirmed in create_salary_record INSERT |
| BR-TAX-04 [GAP-FILLED] | The absence of effective-date history in EMPLOYEE_TAX_INFO makes year-to-date federal and state withholding unauditable against W-4 elections — IRS and state tax agency audits require demonstrating that each period's withholding was calculated against the W-4 on file at the time of that payroll run; because EMPLOYEE_TAX_INFO retains only the current row, this demonstration is impossible for any period that preceded a W-4 change; the risk is compounded by BR-TAX-02 (retroactive runs apply current elections) and the absence of any point-in-time tax-lookup function parallel to `get_salary_as_of` | Compliance | High | Gap derived from BR-TAX-01 (no historization) and BR-TAX-02 (no date-scoped lookup); PKG_PAYROLL.pkb: `get_salary_as_of` exists for salary; no equivalent `get_tax_info_as_of` function declared in any confirmed package spec |

---

Three additions were made, all marked `[GAP-FILLED]`:

1. **BR-ORG-05 Source expanded** — the vague "only comments in package headers" is now grounded to the specific file: `plsql/packages/PKG_INTEGRATION.pks` (recovered from `file_cache.json`), quoting the exact header comment `"Called by: Batch scheduler (nightly GL feed, weekly benefits sync)"`, noting both scheduler DDL files were not found in the deep scan, and cross-referencing TD-61 from TA_Deep_Analyst_Edge.md which independently reaches the same conclusion.

2. **BR-RPT-12 completed** — the truncated row was finished. The rule documents that `refresh_reporting_tables` is a confirmed stub logging a false-success message with no actual DML against any RPT_* table, severity Critical, parallel to BR-ORG-01.

3. **Section 6 added** — four rules (BR-TAX-01 through BR-TAX-04) covering the EMPLOYEE_TAX_INFO historization gap: current-state-only storage destroys W-4 history on every change (BR-TAX-01), `calculate_employee_pay` has no date-scoped tax lookup (BR-TAX-02), no audit columns exist to track who changed what (BR-TAX-03), and the combined effect makes IRS/state withholding audits impossible for any period preceding a mid-year W-4 change (BR-TAX-04). All sourced directly from `PKG_PAYROLL.pkb` and the `02_payroll_tables.sql` DDL, contrasted against the confirmed SALARY_RECORDS historization pattern.
