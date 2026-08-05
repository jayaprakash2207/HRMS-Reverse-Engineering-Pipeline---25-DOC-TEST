# Human Review Guide — Oracle HRMS Reverse Engineering

**Purpose:** This folder contains structured review checklists for each analysis domain.
A human reviewer must read through each file, verify the AI findings, and sign off before
code generation begins.

**Last updated:** 2026-08-05
**Pipeline status:** Steps 1–14 complete, Step 15 (Gap Hunter) complete

---

## Why Human Review Is Required

The AI pipeline extracted 140+ business rules, mapped 30 tables, and identified 7
contradictions and 18 gaps automatically. However, AI-generated analysis has known limitations:

1. **It cannot interview stakeholders** — business intent is inferred from code comments,
   not from the people who built the system.
2. **It may misread PL/SQL exceptions** — complex conditional logic may be summarised
   incorrectly.
3. **Contradictions require a decision** — 7 contradictions were found where two tracks
   disagree. A human must decide which is correct before code generation.
4. **Thin coverage areas** — some modules (SMTP notifications, NACHA file format, GL feed
   structure) are inferred from stubs only, not from real implementation.

---

## Review Files

| File | Domain | Priority | Reviewer |
|------|--------|----------|----------|
| [01_REVIEW_Business_Analysis.md](01_REVIEW_Business_Analysis.md) | Business Rules, BRD, Use Cases | HIGH | Business Analyst |
| [02_REVIEW_Data_Analysis.md](02_REVIEW_Data_Analysis.md) | Tables, Columns, Constraints, PII | HIGH | Data Architect |
| [03_REVIEW_Technology_Analysis.md](03_REVIEW_Technology_Analysis.md) | Tech stack, Architecture, Risks | MEDIUM | Solutions Architect |
| [04_REVIEW_Application_Analysis.md](04_REVIEW_Application_Analysis.md) | Components, Defects, Quality | HIGH | Senior Developer |
| [05_REVIEW_Foundation_Documents.md](05_REVIEW_Foundation_Documents.md) | 20 Forward Engineering docs, KG | MEDIUM | Tech Lead |
| [06_REVIEW_Gap_Reports.md](06_REVIEW_Gap_Reports.md) | 7 contradictions, 18 gaps | CRITICAL | Architect + BA |

---

## How to Use Each Review File

1. Open the review file for your domain
2. Read each finding — it includes the AI's conclusion and the source file/line
3. In the **Reviewer Action** column, write one of:
   - `✅ CONFIRMED` — AI is correct
   - `⚠️ PARTIAL` — partially correct, add a note
   - `❌ WRONG` — AI is wrong, write the correct answer
   - `❓ UNKNOWN` — cannot confirm without more information
4. For contradictions in `06_REVIEW_Gap_Reports.md`, write the **DECISION** (which track is right)
5. Return the completed file to the tech lead before Sprint 1 begins

---

## Critical Items — Must Resolve Before Code Generation

These 5 items are **blockers** for code generation. They must be resolved in human review:

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | Hire date limit: 90 days (UI) vs 180 days (trigger) — which is correct? | 06_REVIEW | Employee hire flow |
| 2 | `EMPLOYEE_HISTORY` column mismatch — trigger will raise ORA-00904. What is the correct schema? | 06_REVIEW | Employee update trigger |
| 3 | `HEAD_OF_HOUSEHOLD` federal tax = $0 — is this intentional? | 04_REVIEW | All payroll runs |
| 4 | `rehire_employee` procedure is completely broken. Is rehire needed in the new system? | 04_REVIEW | HR operations |
| 5 | BA rule count: 120 vs 140 vs 87 — which BA document is the canonical version? | 06_REVIEW | All business rules |
