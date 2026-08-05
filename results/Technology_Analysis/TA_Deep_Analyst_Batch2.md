`SELECT JOB_TITLE FROM JOB_TITLES WHERE JOB_ID = :EMPLOYEE.JOB_ID`; (3) `SELECT FIRST_NAME || ' ' || LAST_NAME FROM EMPLOYEES WHERE EMP_ID = :EMPLOYEE.MANAGER_EMP_ID`; all three fire for every row when HRMS_EMPLOYEE queries multiple records; default RecordsDisplayed=1 limits exposure but EXECUTE_QUERY in list mode still fires POST-QUERY per fetched row | Applied: HRMS_EMPLOYEE only; VW_ACTIVE_EMPLOYEES correctly joins these in a single query | HIGH | HRMS_EMPLOYEE.xml BLOCK:EMPLOYEE POST-QUERY |

---

### Stage 4 — NFR Registry Additions (Chunk 6: Oracle Forms & PLL Libraries)

| ID | NFR Name | Value | Category | Source | Confidence |
|---|---|---|---|---|---|
| NFR-78 | Forms login session ID storage type | VARCHAR2 in :GLOBAL.session_id (NUMBER cast to string); TO_NUMBER conversion in get_session_id(); VALUE_ERROR on non-numeric value returns NULL | Resource Management | HRMS_COMMON_LIB.pll.sql — get_session_id | HIGH |
| NFR-79 | Forms hire date client-side future limit | 90 days from SYSDATE (SYSDATE + 90); enforced in HRMS_EMPLOYEE.WHEN-VALIDATE-ITEM; applies only to Forms UI path | Rate | HRMS_EMPLOYEE.xml WHEN-VALIDATE-ITEM | HIGH |
| NFR-80 | LOV_MANAGERS candidate scope | All ACTIVE employees regardless of grade or department; no permission or hierarchy filter; any active employee can be designated manager via the LOV | Rate | HRMS_EMPLOYEE.xml LOV_MANAGERS query | HIGH |
| NFR-81 | US phone number digit count | 10 or 11 digits after stripping non-digit characters; implemented in HRMS_VALIDATION_LIB.validate_phone | Rate | HRMS_VALIDATION_LIB.pll.sql — validate_phone | HIGH |
| NFR-82 | SSN validation rules | Exactly 9 digits after stripping hyphens; area segment (digits 1–3) must not be '000'; group segment (digits 4–5) must not be '00'; serial segment (digits 6–9) must not be '0000' | Rate | HRMS_VALIDATION_LIB.pll.sql — validate_ssn | HIGH |
| NFR-83 | HRMS_EMPLOYEE default query filter | `EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y'`; set via SET_BLOCK_PROPERTY DEFAULT_WHERE on WHEN-NEW-FORM-INSTANCE; terminated employees not visible in default mode | Rate | HRMS_EMPLOYEE.xml WHEN-NEW-FORM-INSTANCE | HIGH |
| NFR-84 | HRMS_PAYROLL default query filter | `STATUS = 'OPEN' ORDER BY PERIOD_START_DATE DESC`; only OPEN pay periods visible by default | Rate | HRMS_PAYROLL.xml WHEN-NEW-FORM-INSTANCE | HIGH |
| NFR-85 | HRMS_PAYROLL BTN_CALCULATE status pre-check | Only runs with STATUS = 'PENDING' can be calculated; enforced in Forms trigger before PKG_PAYROLL.calculate_payroll call | Rate | HRMS_PAYROLL.xml BTN_CALCULATE WHEN-BUTTON-PRESSED | HIGH |

---

### Stage 5 — Technical Debt & Risk Register Additions (Chunk 6: Oracle Forms & PLL Libraries)

| ID | Risk / Debt Item | Category | Affected Component(s) | Severity | Evidence | Recommended Action |
|---|---|---|---|---|---|---|
| TD-45 | HRMS_LOGIN POST-LOGIN direct EMPLOYEES query bypasses PKG_SECURITY: after authenticate() succeeds, BTN_LOGIN fires a second `SELECT EMP_ID INTO :GLOBAL.current_emp_id FROM EMPLOYEES WHERE UPPER(EMAIL) = UPPER(:LOGIN.USERNAME) AND EMPLOYMENT_STATUS = 'ACTIVE' AND ROWNUM = 1`; this replicates the authenticate() logic but reads directly from EMPLOYEES without going through the package; if authenticate() is ever updated to support non-email login or LDAP, this second query will diverge and may return a different EMP_ID than the authenticated session was created for | Architecture Anti-pattern | HRMS_LOGIN.xml BTN_LOGIN; PKG_SECURITY.authenticate | **Medium** | HRMS_LOGIN.xml BTN_LOGIN WHEN-BUTTON-PRESSED: standalone SELECT after PKG_SECURITY.authenticate call | Remove the standalone EMP_ID query from the Forms trigger; return EMP_ID from PKG_SECURITY.authenticate as an OUT parameter or package global; read it from there |
| TD-46 | LOV_MANAGERS exposes all active employees as potential manager selections with no grade filter: any ACTIVE employee at Grade 1 (Entry Level, $35k–$55k) can be selected as the manager for a Grade 10 C-Suite employee; no hierarchy or grade constraint is applied; PKG_EMPLOYEE.validate_manager only checks for circular references, not for inappropriate upward reporting | Architecture Anti-pattern | HRMS_EMPLOYEE.xml LOV_MANAGERS | **Low** | HRMS_EMPLOYEE.xml LOV_MANAGERS: `SELECT EMP_ID, EMP_NUMBER, FIRST_NAME || ' ' || LAST_NAME FROM HRMS.EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE'` — no grade or department filter | Add minimum grade filter: manager's GRADE_ID should be >= employee's GRADE_ID; or add PKG_EMPLOYEE server-side validation on MANAGER_EMP_ID set |
| TD-47 | HRMS_VALIDATION_LIB.validate_email comment incorrectly states subdomain rejection: source comment says "Only checks for one dot after '@'. Rejects valid emails with subdomains (e.g. user@mail.company.com)"; the actual code uses `INSTR(p_email, '.', v_at_pos)` which finds the FIRST dot at any position after '@'; user@mail.company.com has a dot at position 10 after '@' — the function returns TRUE (valid); the comment overstates the restriction; the real bug is that the function does not check for a dot in the domain part specifically — it accepts user@company (no TLD dot) if '@' is not first/last; the documented and actual behaviors differ | Configuration Risk | HRMS_VALIDATION_LIB.pll.sql — validate_email | **Low** | HRMS_VALIDATION_LIB.pll.sql — code comment vs INSTR logic; `INSTR(p_email, '.', v_at_pos)` finds first dot after '@' at any depth | Correct the comment; separately, consider replacing with REGEXP_LIKE to match server-side PKG_VALIDATION.validate_email pattern; align both layers |
| TD-48 | HRMS_EMPLOYEE ON-ERROR silently suppresses error code 40202 (field protected against update): any attempt to modify a read-only field produces no user feedback — the error is swallowed with NULL; users will be confused when changes to EMPLOYMENT_STATUS or TERMINATION_DATE (both UpdateAllowed=No) silently fail with no message | Operational Risk | HRMS_EMPLOYEE.xml ON-ERROR | **Low** | HRMS_EMPLOYEE.xml ON-ERROR: `IF v_errcode = 40202 THEN NULL;` — no MESSAGE call | Replace NULL with MESSAGE('This field cannot be modified.') to provide user feedback |

---

### Layer Summary — Oracle Forms & PLL Libraries

- Technologies confirmed: Oracle Forms 12c 12.2.1.4 (Active — core); HRMS_COMMON_LIB (Active — core; 16 procedures confirmed); HRMS_VALIDATION_LIB (Active — core; 5 functions confirmed; comment/code mismatch in validate_email); Oracle Forms Global Variables (Active — core; cross-form session state via :GLOBAL.*); Oracle Forms LOV (Active — core)
- Patterns found: AP-37 through AP-41 (5 patterns)
- NFR entries added: NFR-78 through NFR-85 (8 entries)
- TD entries added: TD-45 through TD-48 (4 entries — Medium: 1, Low: 3)
- Agent 1 LOW CONFIDENCE items resolved: ARCH-003 CONFIRMED — business logic split between Forms WHEN-VALIDATE-ITEM triggers (hire date 90-day, email format, FK checks) and DB packages/triggers (same rules at different thresholds); documented drift risk is real and present in HRMS_VALIDATION_LIB.pll source comment
- New LOW CONFIDENCE items raised: None
- DISCREPANCIES with Agent 1: None
- Cross-layer dependencies to carry to Synthesis: AP-39 dual-layer validation drift directly feeds TD-14 (client/server validation divergence) and DISC-001 resolution; AP-38 permission gate gap for LEAVE/PERFORMANCE modules feeds TD-14 security gap catalogue

---

Batch 2 chunk analysis complete. AP-01 through AP-41, NFR-01 through NFR-85, TD-01 through TD-48 now fully catalogued across all chunks. Synthesis Pass (Stages 6, 7, 8) and Final Response Assembly should now be run as the next step.
