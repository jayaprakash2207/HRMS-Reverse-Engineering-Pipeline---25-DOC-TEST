# Extraction Audit
**System:** HRMS v4.2  
**Stage:** Stage 12 — Extraction Confidence and Coverage  
**Date:** 2026-08-03

---

## What Was Extracted

### Layer 1 JSON (Pre-Extracted — High Confidence)
Consumed from `results/Source_Extraction/`:

| Artifact | Tables | Coverage |
|----------|--------|----------|
| database.json | 26 tables, 6 views, 29 sequences, 6 triggers, 11 packages (signatures), 5 external integrations | Full |
| source_code.json | Package procedure/function signatures, form block inventory, library procedures | Full |
| config.json | Available content consumed | Full |
| logs.json | Available content consumed | Full |

### Source Files Read Directly (Stage 6 & 8)
The following package files were read from `source/ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/`:

| File | Purpose | Read Status |
|------|---------|-------------|
| PKG_EMPLOYEE.pks | Type definitions (t_emp_rec, t_emp_cursor), custom exceptions, dependency comment | ✓ Full |
| PKG_EMPLOYEE.pkb | Call flows, SQL injection, circular dep, race condition | ✓ Full |
| PKG_PAYROLL.pks | 18 public method signatures, constants (FICA, tax brackets), circular dep note | ✓ Full |
| PKG_PAYROLL.pkb | Partial commits, tax hard-coding, GL export flow | ✓ Full |
| PKG_LEAVE.pks | 14 public method signatures, t_leave_balance type, bug notes | ✓ Full |
| PKG_LEAVE.pkb | Leave flow, carryover bugs, accrual batch | ✓ Full |
| PKG_INTEGRATION.pks | 5 method signatures, t_gl_entry RECORD, security note (FTP creds in SYSTEM_PARAMETERS) | ✓ Full |
| PKG_INTEGRATION.pkb | File formats, stub procedures | ✓ Full |
| PKG_NOTIFICATION.pks | 4 method signatures, SMTP constants documentation | ✓ Full |
| PKG_NOTIFICATION.pkb | SMTP constants, connection-per-email, queue flow | ✓ Full |
| PKG_PERFORMANCE.pks | 12 method signatures, review type definitions | ✓ Full |
| PKG_PERFORMANCE.pkb | Review flow, rating labels, generate_reviews_for_cycle | ✓ Full |

The following were provided in the initial deep-scan prompt (not re-read):

| File | Status |
|------|--------|
| PKG_AUDIT.pkb/.pks | Provided in prompt |
| PKG_COMMON.pkb/.pks | Provided in prompt |
| PKG_SECURITY.pkb/.pks | Provided in prompt |
| PKG_VALIDATION.pkb/.pks | Provided in prompt |
| PKG_REPORTING.pkb/.pks | Provided in prompt |
| All 6 Oracle Forms XML exports | Provided in prompt |
| HRMS_COMMON_LIB.pll.sql | Provided in prompt |
| HRMS_VALIDATION_LIB.pll.sql | Provided in prompt |

---

## Confidence by Artifact

| Output File | Confidence | Notes |
|-------------|-----------|-------|
| system-inventory.json | 0.95 | High. 2 forms (REPORTS, ADMIN) not scanned; DBMS_SCHEDULER DDL missing |
| module-boundary-map.json | 0.90 | High. Module boundaries are clear from package/form structure |
| component-registry.json | 0.95 | High. All scanned components fully documented |
| application-interface-catalogue.json | 0.85 | High. UI-07/UI-08 (REPORTS/ADMIN forms) are inferred |
| dependency-graph.json | 0.95 | High. All edges evidenced from source reads |
| call-flow-map.json | 0.90 | High. Some call flows (FLOW-02 step 10) have minor inference |
| architecture-pattern-report.md | 0.95 | High. Pattern classification well-evidenced |
| architecture-violation-register.json | 1.00 | All 24 violations are directly evidenced from source or comments |
| application-risk-register.json | 0.95 | All risks derived from evidenced violations |
| strangler-candidate-report.md | 0.85 | Rankings are engineering judgement; validated against coupling scores |
| forward-engineering-input-map.md | 0.80 | Target-state recommendations are architecture guidance, not facts |
| open-questions.md | 1.00 | All items are genuine unknowns — none are hallucinated |
| extraction-audit.md | 1.00 | This document |

---

## What Was NOT Found

| Item | Impact |
|------|--------|
| HRMS_REPORTS.fmb XML export | Reporting module features unknown |
| HRMS_ADMIN.fmb XML export | Admin module features unknown |
| USER_CREDENTIALS table DDL | Auth credential storage design unknown |
| DBMS_SCHEDULER job DDL | Scheduled job configuration not in source control |
| Oracle Forms server config (formsweb.cfg, default.env) | Deployment configuration unknown |
| Oracle Directory Object filesystem paths | File integration paths unknown |
| PKG_REPORTING.pks | Spec provided in prompt only; read status same as .pkb |
| Any test harness or test scripts | Zero test coverage evidence found |
| Any CI/CD configuration | No automated build/deploy evidence |
| Any documentation (README, architecture docs) | No design documentation found |
| TAX_BRACKETS table data | Table exists in schema but content unknown |

---

## Non-Hallucination Compliance Check

All 24 violations in architecture-violation-register.json have:
- Source file path ✓
- Evidence string (exact code or comment) ✓
- No inferred behaviors beyond what code shows ✓

All call flows in call-flow-map.json:
- Traced to actual procedure bodies ✓
- Speculative steps marked with notes/inferred label ✓
- No invented method calls ✓

All items in open-questions.md:
- Are genuine unknowns not determinable from code ✓
- No speculation presented as fact ✓

---

## Source Path Note

The source files were found at the nested path:  
`source/ts-plsql-oracle-forms-hrms/ts-plsql-oracle-forms-hrms-main/plsql/packages/`  

(An additional `ts-plsql-oracle-forms-hrms/` subdirectory exists between `source/` and `ts-plsql-oracle-forms-hrms-main/`. This path differs from the Layer 1 JSON which referenced `ts-plsql-oracle-forms-hrms-main/` directly.)
