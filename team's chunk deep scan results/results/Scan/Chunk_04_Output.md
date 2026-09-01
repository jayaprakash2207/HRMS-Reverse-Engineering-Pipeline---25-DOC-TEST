=== CHUNK METADATA ===
Chunk: 04            (chunk count is budget-driven, not a fixed file count)
Type group: other
Expected files (1):
  1. [other] ts-plsql-oracle-forms-hrms-main/README.md (2091 chars written)
Total source content: 6347 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/README.md ===

**IDENTITY:**
  KIND: documentation (README)
  PURPOSE: describes the overall architecture, directory layout, and technical characteristics of the Oracle Forms 11g/12c legacy HRMS application

**STRUCTURES:**
  None — this file contains no code declarations, only prose/documentation and an illustrated directory tree.

**METHODS:**
  **FILE-LEVEL EFFECT** [SOURCE: L1-131]
  - What it does: Documents the HRMS application for modernization/migration analysis: describes the six functional modules (Employee Records, Department & Organization, Payroll Processing, Leave Management, Performance Reviews, Reporting), the deployment architecture (Oracle Forms 12c App Server -> Oracle WebLogic 12c Server -> Forms Modules/PL/SQL Packages/Oracle Reports -> Oracle Database 19c HRMS schema), the repository's directory structure (forms/, plsql/, schema/, data/, config/, docs/), Oracle Forms specifics (trigger types, LOV record groups, canvas/block architecture, PLL libraries, menu modules), PL/SQL patterns used, database patterns used, and a list of known technical debt items.
  - Business rules: None — descriptive documentation only, no enforced logic.
  - Numbers & thresholds: Originally built in Oracle Forms 6i circa 2002; upgraded to Forms 11g in 2012; currently on Forms 12c with Oracle Database 19c. Serves approximately 200 concurrent users across 3 regional offices. Codebase contains 18 forms, 12 PL/SQL packages, 8 Oracle Reports, 42 tables, 15 views, 200+ triggers. Custom exception handling uses error codes in the range -20000 to -20999. `VARCHAR2(4000)` is used as a catch-all for text fields. Several packages exceed 3,000 lines.
  - Security & error handling: None — this is descriptive documentation, not executable logic; it notes (as technical debt) that exception handling uses custom error codes -20000 to -20999 but does not implement any handling itself.
  - Data in/out: None — no inputs/outputs; the file is static documentation.

**DEPENDENCIES:**
  Data touched:
  - Reads: None
  - Writes: None

  Config/env: None
  External integrations: None

**GAPS:** None

*[pipeline status — type: other · pass: correction · attempt: 2 · coverage: 100% (numbers 11/11 · units 1/1 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 1
Files delivered: 1
  Full coverage on first pass: 0
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/README.md
  Still incomplete after max attempts: 0
Raw source: 6347 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===