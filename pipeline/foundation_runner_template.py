"""
Foundation Runner — Template-Driven
-------------------------------------
Identical to foundation_runner.py in structure and logic, but each Claude
call is told to populate the 25 enterprise templates rather than generate
free-form documents.

The 25 templates live in:
  GENERIC_25_Enterprise_Forward_Engineering_Templates_INDUSTRY_BASED/

These are fully generic, domain-neutral, industry-standard templates that
work for any project (ERP, CRM, Banking, Insurance, HRMS, etc.).

Claude reads each template, preserves every [M] mandatory section heading,
and fills the content from the source evidence.  Sections with no
evidence get:

    Status: NOT_AVAILABLE
    Evidence Class: UNKNOWN
    Confidence: 0.00
    Validation Required: YES

Run via:
    python pipeline/foundation_runner_template.py --output results_fresh/

Or via fresh_run_template.py at the project root (keeps results_fresh/ isolated).
"""

import argparse
import re as _re_top
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import call_claude, save_output, extract_deep_scan_sections, supplement_from_cache

# ── Locate the template directory ─────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATE_DIR = _REPO_ROOT / "GENERIC_25_Enterprise_Forward_Engineering_Templates_INDUSTRY_BASED"


def _load_template(filename: str) -> str:
    """Read one template file from the template directory."""
    path = _TEMPLATE_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"[Template not found: {filename}]"


def _template_block(filename: str) -> str:
    """Return the template content wrapped in a labelled block for the prompt."""
    content = _load_template(filename)
    return f"=== TEMPLATE: {filename} ===\n{content}\n=== END TEMPLATE ==="


# ── Shared population rules injected into every call ─────────────────────────

_POPULATION_RULES = """
## TEMPLATE POPULATION RULES — apply to every document

1. Load the template for each document listed below.
2. Preserve every heading exactly — do not rename, reorder, or delete any heading.
3. For every [M] mandatory section: populate it from the Oracle source evidence.
4. For every [M] section with no evidence, write exactly:

       Status: NOT_AVAILABLE
       Evidence Class: UNKNOWN
       Confidence: 0.00
       Validation Required: YES
       Note: No source evidence was identified in the analyzed Oracle artifacts.
             Validate with business stakeholders before forward engineering begins.

5. For every [C] conditional section: include it only if evidence supports it.
   If no evidence, omit the section entirely (do not write NOT_AVAILABLE for [C]).
6. Evidence classification — every material statement must carry one of:
   OBSERVED | DERIVED | INFERRED | ASSUMED | UNKNOWN | CONTRADICTED
   Confidence format — always write: 0.XX — LABEL (reason)
   Examples: 0.90 — HIGH (observed in source DDL)
             0.65 — MEDIUM (inferred from naming, verify before use)
             0.35 — LOW (assumed, validate with Business Analyst)
             0.00 — LOW (unknown — see escalation table)
7. Source references — every material claim must cite its Oracle source:
   SOURCE_FILE, OBJECT, LINE/RANGE, TABLE/COLUMN, PACKAGE.PROCEDURE, or FORM/TRIGGER.
8. Stable IDs — use the ID series defined in each template (BR-, UC-, CAP-, SVC-,
   DE-, NFR-, SEC-, ADR-, ARCH-, FEI-, TRACE-). Never invent a different series.
9. BR ID SPLIT — BR-xxx = requirements. BR-SEC-xxx = security defects. Never share a number.
10. PAYROLL_RUNS initial status = PENDING (source-confirmed from PKG_PAYROLL.pkb). Never DRAFT.
11. ORACLE FORMS VERSION = always "Oracle Forms 12c (12.2.1.4)". Never 6i or 10g.
12. COBRA = employer has 30 days to notify plan administrator;
    plan administrator has 14 days to notify qualified beneficiary.
13. TECHNOLOGY NEUTRALITY — no React, Kubernetes, AWS, Spring Boot, PostgreSQL (as target),
    Java, Python, Docker, JWT (prescribed), bcrypt (prescribed), etc.
    Exception: Oracle Forms 12c, Oracle DB 19c, PL/SQL, DBMS_CRYPTO are source facts — keep them.
14. Populate the Traceability and Evidence table at the bottom of every document.
15. Populate the Assumptions, Contradictions, and Open Questions tables.
16. Tick the Quality Gate checklist — set each item to [x] if satisfied, [ ] if not.
17. Set "Ready for downstream consumption" in the Quality Gate to:
    YES if all mandatory sections are populated and quality gates pass.
    CONDITIONAL if some mandatory sections are NOT_AVAILABLE but no blockers exist.
    NO if a critical mandatory section cannot be filled or a blocker is unresolved.
18. Do NOT invent business rules, data values, or system behaviour that cannot be
    traced to the Oracle source evidence. Mark all inferences explicitly as INFERRED.
"""

# ── Call 1 prompt: Foundation KG + docs 01–10 ────────────────────────────────

CALL1_PROMPT = """
# Foundation Synthesis Agent — Template-Driven — Part 1 of 2

You are the Foundation / Synthesis agent.  Your job is to populate the 25
enterprise-grade HRMS forward-engineering templates using the Oracle source
evidence provided by the 8 agent output files below.

""" + _POPULATION_RULES + """

## UC-002 PAYROLL USE CASES
Expand UC-002 (Process Monthly Payroll) into 8 sub-use-cases within the
Use Case Specification template:
  UC-002.1 Initiate Payroll Run
  UC-002.2 Calculate Gross Pay
  UC-002.3 Calculate Tax Deductions
  UC-002.4 Calculate Benefit Deductions
  UC-002.5 Calculate Net Pay
  UC-002.6 Approve Payroll Run
  UC-002.7 Generate GL Feed
  UC-002.8 Disburse Payments
Each sub-use-case must have Actor, Preconditions, Main Flow, Business Rules Applied.

## REQUIRED OUTPUT — PART 1

Produce ALL of the following in this exact order, separated by markers.
For each document: load the corresponding template, then populate it from evidence.

=== DOCUMENT: ENTERPRISE_KNOWLEDGE_GRAPH.json ===
(use the JSON template structure — populate all fields from evidence)

=== DOCUMENT: CANONICAL_ENTERPRISE_MODEL.md ===
(populate the 22_CANONICAL_ENTERPRISE_MODEL.md template)

=== DOCUMENT: ARCHITECTURE_INVENTORY.md ===
(populate the 23_ARCHITECTURE_INVENTORY.md template)

=== DOCUMENT: TRACEABILITY_MATRIX.md ===
(populate the 24_TRACEABILITY_MATRIX.md template)

=== DOCUMENT: FORWARD_ENGINEERING_INPUT_MAP.md ===
(populate the 25_FORWARD_ENGINEERING_INPUT_MAP.md template)

=== DOCUMENT: 01_BRD.md ===
(populate the 01_BUSINESS_REQUIREMENTS_DOCUMENT.md template)

=== DOCUMENT: 02_BUSINESS_CAPABILITY_MODEL.md ===
(populate the 02_BUSINESS_CAPABILITY_MODEL.md template)

=== DOCUMENT: 03_USE_CASE_SPECIFICATION.md ===
(populate the 03_USE_CASE_SPECIFICATION.md template — UC-002 must have 8 sub-use-cases)

=== DOCUMENT: 04_BUSINESS_PROCESS_MODEL.md ===
(populate the 04_BUSINESS_PROCESS_MODEL.md template)

=== DOCUMENT: 05_DOMAIN_MODEL.md ===
(populate the 05_DOMAIN_MODEL.md template)

=== DOCUMENT: 06_DATA_DICTIONARY.md ===
(populate the 06_DATA_DICTIONARY.md template)

=== DOCUMENT: 07_DATA_MODEL_SPECIFICATION.md ===
(populate the 07_DATA_MODEL_SPECIFICATION.md template — current Oracle schema only)

=== DOCUMENT: 08_ERD.md ===
(populate the 08_ERD_DOCUMENT.md template)

=== DOCUMENT: 09_DATA_FLOW_DIAGRAM.md ===
(populate the 09_DFD_DOCUMENT.md template)

=== DOCUMENT: 10_SERVICE_CATALOG.md ===
(populate the 10_SERVICE_CATALOG.md template)

CRITICAL OUTPUT RULES:
- Output ALL document content as plain text using the === DOCUMENT: <filename> === markers.
- Do NOT use file writing tools. Do NOT write files. Do NOT use any tools.
- Every document must appear in full — nothing else will be captured.
- Begin every document DIRECTLY with its content. No preamble.
- End your response after 10_SERVICE_CATALOG.md. Do NOT write docs 11–20 yet.

---

## TEMPLATES FOR PART 1

"""

# Templates are appended at call time (see run() function) so the prompt
# stays importable without immediately reading files.

# ── Call 2 prompt: docs 11–20 ─────────────────────────────────────────────────

CALL2_PROMPT = """
# Foundation Synthesis Agent — Template-Driven — Part 2 of 2

You are given the Enterprise Knowledge Graph and all Part 1 documents already
produced.  Your job is to populate forward-engineering documents 11–20 using
the corresponding enterprise templates.

""" + _POPULATION_RULES + """

## DOCUMENT-SPECIFIC GUIDANCE

11_API_CONTRACT_SPECIFICATION.md (template: 11_API_CONTRACT_SPECIFICATION.md):
- Map each PKG_xxx.procedure to a service operation using template section 5.
- Technology neutral — use "operation", "request payload", "response payload".
- Leave target protocol (REST/gRPC/etc.) as a decision for the team.

12_TECHNOLOGY_BLUEPRINT.md (template: 12_TECHNOLOGY_BLUEPRINT.md):
- Section 6 layers: describe current Oracle Forms / DB 19c / PL/SQL accurately.
- Section 16 Technology Selection Criteria: criteria only — no vendor prescription.
- All target-state items must be marked [DECISION REQUIRED — not yet chosen].

13_SECURITY_ARCHITECTURE.md (template: 13_SECURITY_ARCHITECTURE_DOCUMENT.md):
- Section 7 Threat Model: document all threats found in source code.
- Section 19 Security Requirements: use BR-SEC-xxx IDs for all defects.
- Modernisation: state requirements, not products (e.g. "industry-standard
  password hashing" not "bcrypt").

14_NFR_SPECIFICATION.md (template: 14_NFR_SPECIFICATION.md):
- Section 15 NFR Specification Record: every NFR must have Metric + Target + Threshold.
- Reference ISO/IEC 25010:2023 quality model as template instructs.

15_FORWARD_ENGINEERING_SPECIFICATION.md (template: 15_FORWARD_ENGINEERING_SPECIFICATION.md):
- Section 13 Legacy-to-Target Mapping: every significant Oracle source construct
  must have a row: source → semantic interpretation → target artifact → rationale.

16_GENERATION_MANIFEST.json (template: 16_GENERATION_MANIFEST.json):
- "technology_constraints": [] — empty, no vendor chosen.
- "target_system": name and scope only; language/framework/platform left null.
- Quality gates GATE-EVIDENCE, GATE-CONSISTENCY, GATE-TRACEABILITY,
  GATE-COMPLETENESS, GATE-READINESS must all be present.

17_FORWARD_ENGINEERING_READINESS_REPORT.md (template: 17_FORWARD_ENGINEERING_READINESS_REPORT.md):
- Section 25 Blocking Issues: every unresolved defect, missing DDL, and
  human-decision item must be listed.
- Section 27 Readiness Score: use a transparent weighted model.
- Section 30 Go/No-Go Decision: GO / CONDITIONAL-GO / NO-GO with rationale.

18_DEPLOYMENT_ARCHITECTURE.md (template: 18_DEPLOYMENT_ARCHITECTURE_DOCUMENT.md):
- Describe deployment requirements — no Kubernetes, Docker, AWS, Nginx etc.
- Section 3 Environment Model: Dev / Test / UAT / Production / DR as applicable.

19_FRONTEND_ARCHITECTURE.md (template: 19_FRONTEND_ARCHITECTURE_DOCUMENT.md):
- Section 8 Page/View Architecture: map every Oracle Forms module by exact name:
  HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE, HRMS_PERFORMANCE, HRMS_LOGIN, HRMS_MENU.
- No framework names (no React, Angular, Vue).

20_UI_UX_SPECIFICATION.md (template: 20_UI_UX_SPECIFICATION.md):
- Section 10 Screen Specification: use all 14 sub-sections for every screen.
- Section 11 HRMS Screen Catalog: cover all 6 Oracle Forms modules.

## REQUIRED OUTPUT — PART 2

=== DOCUMENT: 11_API_CONTRACT_SPECIFICATION.md ===
(populate the 11_API_CONTRACT_SPECIFICATION.md template)

=== DOCUMENT: 12_TECHNOLOGY_BLUEPRINT.md ===
(populate the 12_TECHNOLOGY_BLUEPRINT.md template)

=== DOCUMENT: 13_SECURITY_ARCHITECTURE.md ===
(populate the 13_SECURITY_ARCHITECTURE_DOCUMENT.md template)

=== DOCUMENT: 14_NFR_SPECIFICATION.md ===
(populate the 14_NFR_SPECIFICATION.md template)

=== DOCUMENT: 15_FORWARD_ENGINEERING_SPECIFICATION.md ===
(populate the 15_FORWARD_ENGINEERING_SPECIFICATION.md template)

=== DOCUMENT: 16_GENERATION_MANIFEST.json ===
(populate the 16_GENERATION_MANIFEST.json template — valid JSON)

=== DOCUMENT: 17_FORWARD_ENGINEERING_READINESS_REPORT.md ===
(populate the 17_FORWARD_ENGINEERING_READINESS_REPORT.md template)

=== DOCUMENT: 18_DEPLOYMENT_ARCHITECTURE.md ===
(populate the 18_DEPLOYMENT_ARCHITECTURE_DOCUMENT.md template)

=== DOCUMENT: 19_FRONTEND_ARCHITECTURE.md ===
(populate the 19_FRONTEND_ARCHITECTURE_DOCUMENT.md template — all 6 Oracle Forms modules mapped)

=== DOCUMENT: 20_UI_UX_SPECIFICATION.md ===
(populate the 20_UI_UX_SPECIFICATION.md template)

CRITICAL OUTPUT RULES:
- Output ALL document content as plain text using the === DOCUMENT: <filename> === markers.
- Do NOT use file writing tools. Do NOT write files. Do NOT use any tools.
- Every document must appear in full — nothing else will be captured.
- Begin every document DIRECTLY with its content. No preamble.

---

## TEMPLATES FOR PART 2

"""

# ── Call 3 prompt: verification + cleaning pass ────────────────────────────────

CALL3_PROMPT = """
# Foundation Synthesis Agent — Template Compliance Verification (Part 3 of 4)

You are given all 25 generated documents plus the 25 enterprise templates.

## PRIMARY TASK: Remove AI artifact text

Scan every document for these strings and REMOVE them:
- "Looking at the source content"
- "Here is the updated snippet" / "Updated snippet"
- "Let me check" / "I'll now read" / "I need to" / "Let me look"
- "I can see that" / "Based on the above" / "Based on the source"
- "I've removed" / "I've added" / "I've updated"
- <!-- GAP-FILLED SECTION --> or any HTML comment artifact
- Any line that reads like AI internal reasoning

## SECONDARY TASK: Remove duplicate sections

For each document check for any ## or ### heading appearing more than once.
Keep the FIRST occurrence. Remove all subsequent duplicate blocks.

## TERTIARY TASK: Template compliance check

For every document, verify the populated document matches its template structure:
- Every [M] mandatory heading is present
- Sections with no evidence have the correct NOT_AVAILABLE block
- Evidence classification is present on all material statements
- The Traceability and Evidence table is populated
- The Quality Gate checklist is present and filled
- IDs are consistent (BR-xxx, UC-xxx, CAP-xxx, SVC-xxx etc.)

## QUATERNARY TASK: Technology neutrality

Replace any specific technology names with generic equivalents:
| Replace | With |
|---|---|
| React, Angular, Vue, Next.js | web-based UI layer |
| Node.js, Express | service layer runtime |
| Spring Boot, Django, Rails, FastAPI | service layer framework |
| Kubernetes, K8s | container orchestration platform |
| Docker | containerisation |
| AWS, Azure, GCP | cloud or on-premise deployment |
| PostgreSQL, MySQL, MongoDB (as target) | relational database |
| JWT (prescribed) | stateless authentication token |
| bcrypt, Argon2, scrypt (prescribed) | industry-standard password hashing |
| Nginx, Apache (prescribed) | web server / reverse proxy |
| Kafka, RabbitMQ (prescribed) | message queue |

Exception: Oracle Forms 12c, Oracle DB 19c, PL/SQL, DBMS_CRYPTO are source facts — keep them.

## QUINARY TASK: Content gap check

1. Tables in agent outputs missing from 06_DATA_DICTIONARY.md or 08_ERD.md
2. Procedures in agent outputs missing from 10_SERVICE_CATALOG.md or 11_API_CONTRACT_SPECIFICATION.md
3. Business rules in BA outputs missing from 01_BRD.md or 03_USE_CASE_SPECIFICATION.md
4. Security findings missing from 13_SECURITY_ARCHITECTURE.md
5. Use cases missing Actor, Preconditions, Postconditions, Main Flow, Business Rules Applied
6. Contradictions between documents

## OUTPUT FORMAT

For each document that needs any change:
=== UPDATE: <filename> ===
<COMPLETE document content — every line from start to finish>

CRITICAL:
- Every UPDATE block must contain the FULL document, not a diff.
- Begin content directly — no preamble ("Here is the updated...").
- Mark added content with [VERIFIED-SUPPLEMENT].
- Only output UPDATE blocks for documents that actually changed.

---
"""

# ── Call 4 prompt: cross-document consistency + new support docs ───────────────

CALL4_PROMPT = """
# Foundation Synthesis Agent — Cross-Document Consistency Check (Part 4 of 4)

You are given all 25 generated and verified documents.

## Checks to perform

1. BR-xxx REFERENCE INTEGRITY
   Every BR-xxx referenced in any document must be defined in 01_BRD.md.
   Every BR-SEC-xxx referenced must be defined in 13_SECURITY_ARCHITECTURE.md.
   Flag collisions: same ID number used for two different things.

2. USE CASE REFERENCE INTEGRITY
   Every UC-xxx referenced must exist in 03_USE_CASE_SPECIFICATION.md.

3. TABLE REFERENCE INTEGRITY
   Every table name (UPPER_CASE) referenced must appear in 07_DATA_MODEL_SPECIFICATION.md.

4. PACKAGE/PROCEDURE REFERENCE INTEGRITY
   Every PKG_xxx.procedure referenced must appear in 11_API_CONTRACT_SPECIFICATION.md.

5. ACTOR ID INTEGRITY
   Every ACT-xxx must exist in 03_USE_CASE_SPECIFICATION.md Actor Catalogue.

6. NUMERIC FACT CONTRADICTIONS
   Same fact (session timeout, tax rates, rating ranges) stated differently
   in two documents — flag as HUMAN-DECISION-REQUIRED.

7. ORACLE FORMS MODULE COVERAGE
   All 6 modules (HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE, HRMS_PERFORMANCE,
   HRMS_LOGIN, HRMS_MENU) must appear in 19_FRONTEND_ARCHITECTURE.md or
   20_UI_UX_SPECIFICATION.md. Add any missing ones.

8. AES KEY LENGTH CHECK
   If any document quotes the AES-256 key string, count characters.
   AES-256 requires exactly 32 bytes. Flag if not 32 with:
   "AES key length mismatch — run: SELECT LENGTH(UTL_RAW.CAST_TO_RAW('<key>')) FROM DUAL;"

9. SCHEMA MIGRATION SCRIPTS
   For every column/table/constraint the API Contract requires that does NOT
   exist in 07_DATA_MODEL_SPECIFICATION.md, produce a ready-to-run SQL script:
   === DOCUMENT: SCHEMA_MIGRATION_SCRIPTS.md ===
   Format: -- Migration: [desc]  -- Required by: [doc + section]  -- BR: [BR-xxx]
   ALTER TABLE ... ;

10. DBA INVESTIGATION CHECKLIST
    For every inferred/unconfirmed table, produce:
    === DOCUMENT: DBA_CHECKLIST.md ===
    -- Check: does [TABLE_NAME] exist?
    SELECT table_name FROM user_tables WHERE table_name = '[TABLE_NAME]';
    SELECT DBMS_METADATA.GET_DDL('TABLE','[TABLE_NAME]') FROM DUAL;

11. BR CROSS-REFERENCE TABLE
    Map legacy BA BR-01..108 series to BRD BR-001..050 series.
    Flag UNMAPPEDs.
    === DOCUMENT: BR_CROSSREFERENCE.md ===

12. TRACEABILITY MATRIX COMPLETENESS (template section 22)
    Verify the Traceability Matrix covers all 7 required metrics:
    source coverage, requirement coverage, critical requirement coverage,
    bidirectional traceability, orphan rate, unresolved conflict count,
    low-confidence critical item count.
    Update 24_TRACEABILITY_MATRIX.md if any metrics are missing.

13. READINESS REPORT COMPLETENESS (template section 27 and 30)
    Verify 17_FORWARD_ENGINEERING_READINESS_REPORT.md has:
    - A scored readiness calculation (section 27)
    - An explicit GO / CONDITIONAL-GO / NO-GO decision (section 30)
    - A remediation plan (section 28)
    Update if missing.

14. GENERATION MANIFEST VALIDATION
    Validate 16_GENERATION_MANIFEST.json is valid JSON with all 5 quality
    gates present. Flag if schema is broken.

## OUTPUT FORMAT

=== CONSISTENCY_REPORT ===
## BR-xxx Broken References
| BR ID | Referenced In | Not Found In BRD | Recommendation |
|---|---|---|---|

## BR-xxx / BR-SEC-xxx ID Collisions
| BR ID | BRD Definition | Other Document + Definition | Resolution |
|---|---|---|---|

## Other Broken References
| ID / Name | Type | Referenced In | Missing From | Recommendation |
|---|---|---|---|---|

## Numeric Contradictions
| Fact | Document A says | Document B says | HUMAN-DECISION-REQUIRED? |
|---|---|---|---|

## Oracle Forms Coverage Gaps
| Form Module | Present In | Gap |
|---|---|---|

## AES Key Investigation
| Key String | Length | Required | Status |
|---|---|---|---|

## Summary
Total BR collisions: N
Total broken references: N
Total contradictions: N
Oracle Forms coverage gaps: N
Schema migrations needed: N
DBA investigation items: N
Overall assessment: CONSISTENT / ISSUES-FOUND

Then produce in this order:
1. All UPDATE blocks for documents that need fixing
2. SCHEMA_MIGRATION_SCRIPTS.md
3. DBA_CHECKLIST.md
4. BR_CROSSREFERENCE.md

=== UPDATE: <filename> ===
<complete corrected document — full file>

=== DOCUMENT: SCHEMA_MIGRATION_SCRIPTS.md ===
=== DOCUMENT: DBA_CHECKLIST.md ===
=== DOCUMENT: BR_CROSSREFERENCE.md ===

CRITICAL: Only fix genuine errors. Mark unresolvable items HUMAN-DECISION-REQUIRED.
CRITICAL: Begin every UPDATE/DOCUMENT block directly with content — no preamble.
CRITICAL: Every UPDATE block must be the FULL document, not a diff.

---
"""


# ── Artifact stripping ─────────────────────────────────────────────────────────

_ARTIFACT_LINE_PREFIXES = (
    "Looking at the source content",
    "Here is the updated snippet",
    "Here is the updated document",
    "Here is the complete updated",
    "Updated snippet",
    "Let me check",
    "I'll now read",
    "I need to",
    "Let me look",
    "I can see that",
    "Based on the above",
    "Based on the source",
    "I've removed",
    "I've added",
    "I've updated",
)

import re as _re

_ARTIFACT_HTML_COMMENT = _re.compile(r'<!--\s*GAP-FILLED SECTION\s*-->', _re.IGNORECASE)


def _strip_artifacts(content: str) -> str:
    lines = content.split('\n')
    clean = []
    for line in lines:
        stripped = line.strip()
        if any(stripped.lower().startswith(p.lower()) for p in _ARTIFACT_LINE_PREFIXES):
            continue
        line = _ARTIFACT_HTML_COMMENT.sub('', line)
        if not line.strip():
            if clean and clean[-1] != '':
                clean.append('')
            continue
        clean.append(line)
    while clean and clean[-1] == '':
        clean.pop()
    return '\n'.join(clean)


def _deduplicate_headings(content: str) -> str:
    lines = content.split('\n')
    seen_headings = set()
    result = []
    skip_until_level = None

    for line in lines:
        heading_match = _re.match(r'^(#{1,6})\s+(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if skip_until_level is not None:
                if level <= skip_until_level:
                    skip_until_level = None
                else:
                    continue
            key = (level, heading_text.lower())
            if key in seen_headings:
                skip_until_level = level
                continue
            else:
                seen_headings.add(key)
                result.append(line)
        else:
            if skip_until_level is not None:
                continue
            result.append(line)

    return '\n'.join(result)


# ── Shared constants ───────────────────────────────────────────────────────────

_FOUNDATION_FILES = {
    "ENTERPRISE_KNOWLEDGE_GRAPH.json",
    "CANONICAL_ENTERPRISE_MODEL.md",
    "ARCHITECTURE_INVENTORY.md",
    "TRACEABILITY_MATRIX.md",
    "FORWARD_ENGINEERING_INPUT_MAP.md",
    "CONSISTENCY_REPORT.md",
    "SCHEMA_MIGRATION_SCRIPTS.md",
    "DBA_CHECKLIST.md",
    "BR_CROSSREFERENCE.md",
}

# Templates needed for Part 1 calls
_PART1_TEMPLATES = [
    ("ENTERPRISE_KNOWLEDGE_GRAPH.json",    "21_ENTERPRISE_KNOWLEDGE_GRAPH.json"),
    ("CANONICAL_ENTERPRISE_MODEL.md",      "22_CANONICAL_ENTERPRISE_MODEL.md"),
    ("ARCHITECTURE_INVENTORY.md",          "23_ARCHITECTURE_INVENTORY.md"),
    ("TRACEABILITY_MATRIX.md",             "24_TRACEABILITY_MATRIX.md"),
    ("FORWARD_ENGINEERING_INPUT_MAP.md",   "25_FORWARD_ENGINEERING_INPUT_MAP.md"),
    ("01_BRD.md",                          "01_BUSINESS_REQUIREMENTS_DOCUMENT.md"),
    ("02_BUSINESS_CAPABILITY_MODEL.md",    "02_BUSINESS_CAPABILITY_MODEL.md"),
    ("03_USE_CASE_SPECIFICATION.md",       "03_USE_CASE_SPECIFICATION.md"),
    ("04_BUSINESS_PROCESS_MODEL.md",       "04_BUSINESS_PROCESS_MODEL.md"),
    ("05_DOMAIN_MODEL.md",                 "05_DOMAIN_MODEL.md"),
    ("06_DATA_DICTIONARY.md",              "06_DATA_DICTIONARY.md"),
    ("07_DATA_MODEL_SPECIFICATION.md",     "07_DATA_MODEL_SPECIFICATION.md"),
    ("08_ERD.md",                          "08_ERD_DOCUMENT.md"),
    ("09_DATA_FLOW_DIAGRAM.md",            "09_DFD_DOCUMENT.md"),
    ("10_SERVICE_CATALOG.md",              "10_SERVICE_CATALOG.md"),
]

# Templates needed for Part 2 calls
_PART2_TEMPLATES = [
    ("11_API_CONTRACT_SPECIFICATION.md",        "11_API_CONTRACT_SPECIFICATION.md"),
    ("12_TECHNOLOGY_BLUEPRINT.md",              "12_TECHNOLOGY_BLUEPRINT.md"),
    ("13_SECURITY_ARCHITECTURE.md",             "13_SECURITY_ARCHITECTURE_DOCUMENT.md"),
    ("14_NFR_SPECIFICATION.md",                 "14_NFR_SPECIFICATION.md"),
    ("15_FORWARD_ENGINEERING_SPECIFICATION.md", "15_FORWARD_ENGINEERING_SPECIFICATION.md"),
    ("16_GENERATION_MANIFEST.json",             "16_GENERATION_MANIFEST.json"),
    ("17_FORWARD_ENGINEERING_READINESS_REPORT.md", "17_FORWARD_ENGINEERING_READINESS_REPORT.md"),
    ("18_DEPLOYMENT_ARCHITECTURE.md",           "18_DEPLOYMENT_ARCHITECTURE_DOCUMENT.md"),
    ("19_FRONTEND_ARCHITECTURE.md",             "19_FRONTEND_ARCHITECTURE_DOCUMENT.md"),
    ("20_UI_UX_SPECIFICATION.md",               "20_UI_UX_SPECIFICATION.md"),
]


def _build_template_appendix(template_list: list) -> str:
    """Build the template appendix injected at the end of Call 1 and Call 2 prompts."""
    parts = []
    for _output_name, template_file in template_list:
        parts.append(_template_block(template_file))
    return "\n\n".join(parts)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_layer_outputs(output_dir: str) -> dict:
    base = Path(output_dir)
    layers = {}
    for folder, key in [
        ("Business_Analysis",    "BA_Structural_Scout.md"),
        ("Business_Analysis",    "BA_Deep_Analyst.md"),
        ("Data_Analysis",        "DA_Data_Extractor.md"),
        ("Data_Analysis",        "DA_Data_Reviewer.md"),
        ("Technology_Analysis",  "TA_Stack_Scout.md"),
        ("Technology_Analysis",  "TA_Deep_Analyst.md"),
        ("Application_Analysis", "AA_App_Extractor.md"),
        ("Application_Analysis", "AA_Quality_Review.md"),
    ]:
        path = base / folder / key
        if path.exists():
            layers[key] = path.read_text(encoding="utf-8")
            print(f"  Loaded: {folder}/{key} ({len(layers[key])} chars)")
        else:
            print(f"  Missing (will proceed without): {folder}/{key}")
            layers[key] = ""
    return layers


def _split_documents(text: str) -> dict:
    import re
    docs = {}
    pattern = re.compile(r"=== DOCUMENT:\s*(.+?)\s*===", re.IGNORECASE)
    parts = pattern.split(text)
    i = 1
    while i < len(parts) - 1:
        filename = parts[i].strip()
        content  = parts[i + 1].strip()
        docs[filename] = content
        i += 2
    return docs


def _split_documents_updates(text: str) -> dict:
    import re
    docs = {}
    pattern = re.compile(r"===\s*(?:UPDATE|DOCUMENT):\s*(.+?)\s*===", re.IGNORECASE)
    parts = pattern.split(text)
    i = 1
    while i < len(parts) - 1:
        filename = parts[i].strip()
        content  = parts[i + 1].strip()
        docs[filename] = content
        i += 2
    return docs


def _clean_document(filename: str, content: str) -> str:
    if filename.endswith('.json'):
        return content
    content = _strip_artifacts(content)
    content = _deduplicate_headings(content)
    return content


def _save_docs(docs: dict, foundation_dir: Path, fwd_eng_dir: Path) -> list:
    saved = []
    for filename, content in docs.items():
        content = _clean_document(filename, content)
        if filename in _FOUNDATION_FILES:
            path = foundation_dir / filename
        else:
            path = fwd_eng_dir / filename
        path.write_text(content, encoding="utf-8")
        saved.append(str(path))
        print(f"  Saved → {path}")
    return saved


def _reload_docs(docs_raw: dict, foundation_dir: Path, fwd_eng_dir: Path) -> dict:
    foundation_files = {
        "ENTERPRISE_KNOWLEDGE_GRAPH.json",
        "CANONICAL_ENTERPRISE_MODEL.md",
        "ARCHITECTURE_INVENTORY.md",
        "TRACEABILITY_MATRIX.md",
        "FORWARD_ENGINEERING_INPUT_MAP.md",
    }
    filled = {}
    for filename, raw_content in docs_raw.items():
        if filename in foundation_files:
            path = foundation_dir / filename
        else:
            path = fwd_eng_dir / filename
        if path.exists() and path.stat().st_size > 0:
            filled[filename] = path.read_text(encoding="utf-8")
        else:
            filled[filename] = raw_content
    return filled


def _build_fallback_supplement(output_dir: str) -> str:
    supplement_parts = []
    deep_scan_path = Path(output_dir) / "DEEP_SCAN_OUTPUT.md"
    if deep_scan_path.exists() and deep_scan_path.stat().st_size > 0:
        deep_scan_text = deep_scan_path.read_text(encoding="utf-8")
        supplement_parts.append(
            f"## DEEP_SCAN_OUTPUT.md (fallback)\n\n{deep_scan_text}"
        )
        print(f"  [Fallback] Added DEEP_SCAN_OUTPUT.md ({len(deep_scan_text)} chars)")
    else:
        cache_path = Path(output_dir) / "file_cache.json"
        if cache_path.exists():
            import json as _json
            with open(cache_path, encoding="utf-8") as f:
                cache = _json.load(f)
            raw_parts = [f"=== FILE: {fp} ===\n{c}" for fp, c in cache.items()]
            raw_text = "\n\n".join(raw_parts)
            supplement_parts.append(
                f"## file_cache.json raw source (fallback)\n\n{raw_text}"
            )
            print(f"  [Fallback] Added {len(cache)} files from file_cache.json")
    return "\n\n".join(supplement_parts)


# ── Hybrid Source Coverage Engine ─────────────────────────────────────────────
#
# Option 1 (Claude)  : during Call 3, Claude counts evidence tags per document
#                      and includes a ## Source Coverage Estimate section.
# Option 2 (Python)  : after all 4 calls, Python re-reads every saved file,
#                      counts evidence tags programmatically, appends/overwrites
#                      the ## Source Coverage Report section with exact counts,
#                      and writes COVERAGE_SUMMARY.md.
#
# Hybrid = Option 1 runs first (Claude's semantic estimate), then Option 2 runs
# and OVERWRITES it with the accurate Python count.  Result: 100% accurate
# figures with zero hallucination risk.

_COVERAGE_CALL3_INSTRUCTION = """
## COVERAGE ANALYSIS TASK (perform AFTER all 5 verification tasks)

For EVERY document you output as an UPDATE block, append a ## Source Coverage
Estimate section at the very end of the document (before any trailing tables).

Format exactly:
## Source Coverage Estimate [AUTO]
| Evidence Class | Count | % of Total |
|---|---:|---:|
| OBSERVED | {N} | {P}% |
| DERIVED | {N} | {P}% |
| INFERRED | {N} | {P}% |
| ASSUMED | {N} | {P}% |
| UNKNOWN | {N} | {P}% |
| CONTRADICTED | {N} | {P}% |
| NOT_AVAILABLE sections | {N} | — |
| **Source Match % (OBS+DER)** | — | **{P}%** |
| **Avg Confidence Score** | — | **{V}** |

Note: These are semantic estimates. Python post-processing will replace this
section with exact programmatic counts after all calls complete.
"""

# ── Call 5: Self-correction prompt ────────────────────────────────────────────

_SELF_CORRECT_PROMPT = """
# Self-Correction Agent — LOW Confidence Sections

You are a self-correction agent. Below are sections from generated documents
that were marked LOW confidence (score < 0.50). These sections are either
ASSUMED (no evidence) or UNKNOWN (insufficient evidence).

Your job:
1. Re-examine each LOW section against the original source evidence provided.
2. For each section, do ONE of the following:
   a) UPGRADE — if you find evidence you missed before, rewrite the section
      with the upgraded content and a higher confidence score + label.
   b) CONFIRM NOT_AVAILABLE — if there is genuinely no evidence, confirm it
      and add the exact escalation contact from this table:

      | Section Type | Escalate To |
      |---|---|
      | Business rules / requirements | Business Analyst |
      | Data schema / DDL / tables | DBA |
      | Security controls / auth model | CISO / Security Lead |
      | Process / workflow / approval | Process Owner / BA |
      | Architecture / technology choice | Solution Architect |
      | UI / UX / screen layout | UX Lead / Product Owner |
      | Performance / availability targets | System Owner / Architect |
      | Regulatory / compliance | Legal / Compliance Officer |

CONFIDENCE FORMAT — always use: `0.XX — LABEL (reason)`
Examples:
  0.90 — HIGH (observed in source DDL, PKG_PAYROLL line 142)
  0.65 — MEDIUM (inferred from naming convention, verify before use)
  0.35 — LOW (assumed, no source evidence — validate with Business Analyst)
  0.00 — LOW (unknown, insufficient evidence — see escalation table)

OUTPUT FORMAT — for each corrected section, output:

=== CORRECTION: <filename> | <section_heading> ===
<corrected section content — full section, not a diff>
=== END CORRECTION ===

If a section cannot be improved at all, still output the block with the
original content plus an explicit escalation contact added.

POPULATION RULES — same as main generation:
- Technology-neutral (no React, AWS, Spring Boot, etc.)
- BR-xxx = requirements only. BR-SEC-xxx = security defects only.
- Every claim needs evidence class + source reference + confidence label.
"""

_EVIDENCE_CLASSES = [
    "OBSERVED",
    "DERIVED",
    "INFERRED",
    "ASSUMED",
    "UNKNOWN",
    "CONTRADICTED",
]

_CONFIDENCE_PATTERN = _re_top.compile(
    r'(?:confidence|confidence_score|Confidence)[:\s|]+([0-9]\.[0-9]+)',
    _re_top.IGNORECASE
)

# Also matches inline format: "0.90 — HIGH" or "0.65 — MEDIUM" or "0.35 — LOW"
_CONFIDENCE_LABEL_PATTERN = _re_top.compile(
    r'([0-9]\.[0-9]+)\s*[—–-]+\s*(HIGH|MEDIUM|LOW)',
    _re_top.IGNORECASE
)

_NOT_AVAILABLE_PATTERN = _re_top.compile(
    r'Status:\s*NOT_AVAILABLE',
    _re_top.IGNORECASE
)

_LOW_CONFIDENCE_SECTION_PATTERN = _re_top.compile(
    r'([0-9]\.[0-9]+)\s*[—–-]+\s*LOW',
    _re_top.IGNORECASE
)

_SOURCE_COVERAGE_SECTION = _re_top.compile(
    r'## Source Coverage (?:Estimate|Report).*?(?=\n## |\Z)',
    _re_top.DOTALL | _re_top.IGNORECASE
)


def _compute_coverage(content: str) -> dict:
    """Count evidence class occurrences and confidence scores in a document."""
    counts = {ec: 0 for ec in _EVIDENCE_CLASSES}
    for ec in _EVIDENCE_CLASSES:
        counts[ec] = len(_re_top.findall(
            rf'\b{ec}\b', content, _re_top.IGNORECASE
        ))

    total = sum(counts.values())
    source_match_count = counts["OBSERVED"] + counts["DERIVED"]
    source_match_pct = round(source_match_count / total * 100, 1) if total > 0 else 0.0

    confidence_values = [
        float(m) for m in _CONFIDENCE_PATTERN.findall(content)
        if 0.0 <= float(m) <= 1.0
    ]
    # Also extract from label format: "0.90 — HIGH"
    label_values = [
        float(m[0]) for m in _CONFIDENCE_LABEL_PATTERN.findall(content)
        if 0.0 <= float(m[0]) <= 1.0
    ]
    confidence_values = list(set(confidence_values + label_values))
    avg_confidence = round(sum(confidence_values) / len(confidence_values), 3) \
        if confidence_values else 0.0

    not_available_count = len(_NOT_AVAILABLE_PATTERN.findall(content))

    return {
        "counts": counts,
        "total": total,
        "source_match_pct": source_match_pct,
        "avg_confidence": avg_confidence,
        "not_available": not_available_count,
    }


def _build_coverage_section(filename: str, cov: dict) -> str:
    """Build the ## Source Coverage Report markdown table."""
    counts = cov["counts"]
    total = cov["total"]
    rows = ""
    for ec in _EVIDENCE_CLASSES:
        n = counts[ec]
        pct = round(n / total * 100, 1) if total > 0 else 0.0
        rows += f"| {ec} | {n} | {pct}% |\n"

    readiness = (
        "HIGH" if cov["source_match_pct"] >= 80 else
        "MEDIUM" if cov["source_match_pct"] >= 60 else
        "LOW — human review required"
    )

    return (
        f"\n\n## Source Coverage Report [VERIFIED]\n\n"
        f"| Evidence Class | Count | % of Total |\n"
        f"|---|---:|---:|\n"
        f"{rows}"
        f"| NOT_AVAILABLE sections | {cov['not_available']} | — |\n"
        f"| **Source Match % (OBS+DER)** | — | **{cov['source_match_pct']}%** |\n"
        f"| **Avg Confidence Score** | — | **{cov['avg_confidence']} — {'HIGH' if cov['avg_confidence'] >= 0.75 else 'MEDIUM' if cov['avg_confidence'] >= 0.50 else 'LOW'}** |\n"
        f"| **Total Evidence Tags** | {total} | 100% |\n\n"
        f"**Readiness signal:** {readiness}\n\n"
        f"_Counts are programmatically verified from the saved document file._\n"
    )


def _append_coverage_to_doc(path: Path) -> dict:
    """Read a document, compute coverage, append/replace the report section."""
    content = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return {"filename": path.name, "skipped": True}

    cov = _compute_coverage(content)
    coverage_section = _build_coverage_section(path.name, cov)

    # Remove any prior Claude estimate or Python report, then append fresh
    content_clean = _SOURCE_COVERAGE_SECTION.sub("", content).rstrip()
    content_final = content_clean + coverage_section
    path.write_text(content_final, encoding="utf-8")

    return {
        "filename": path.name,
        "source_match_pct": cov["source_match_pct"],
        "avg_confidence": cov["avg_confidence"],
        "not_available": cov["not_available"],
        "total_tags": cov["total"],
        "readiness": (
            "HIGH" if cov["source_match_pct"] >= 80 else
            "MEDIUM" if cov["source_match_pct"] >= 60 else
            "LOW"
        ),
    }


def _run_coverage_pass(foundation_dir: Path, fwd_eng_dir: Path, output_dir: str) -> None:
    """
    Option 2 — Python coverage pass.
    Reads every saved .md file, computes exact evidence counts,
    overwrites the Source Coverage section, and writes COVERAGE_SUMMARY.md.
    """
    print("\n[Coverage Pass] Computing source coverage for all documents...")

    results = []
    for directory in [foundation_dir, fwd_eng_dir]:
        for path in sorted(directory.glob("*.md")):
            result = _append_coverage_to_doc(path)
            if not result.get("skipped"):
                results.append(result)
                signal = result["readiness"]
                pct = result["source_match_pct"]
                print(f"  {path.name:<55} {pct:>6.1f}%  [{signal}]")

    if not results:
        print("  [Coverage Pass] No documents found.")
        return

    # Sort by source match % ascending — lowest first so reviewers see
    # the weakest documents at the top of the summary
    results.sort(key=lambda r: r["source_match_pct"])

    avg_overall = round(
        sum(r["source_match_pct"] for r in results) / len(results), 1
    )
    high_count    = sum(1 for r in results if r["readiness"] == "HIGH")
    medium_count  = sum(1 for r in results if r["readiness"] == "MEDIUM")
    low_count     = sum(1 for r in results if r["readiness"] == "LOW")

    rows = ""
    for r in results:
        signal_icon = {"HIGH": "✓", "MEDIUM": "~", "LOW": "!"}.get(r["readiness"], "?")
        rows += (
            f"| {r['filename']:<55} | {r['source_match_pct']:>6.1f}% "
            f"| {r['avg_confidence']:>5.3f} "
            f"| {r['not_available']:>3} "
            f"| {r['total_tags']:>5} "
            f"| {signal_icon} {r['readiness']} |\n"
        )

    # Build dedicated human review sections
    low_docs    = [r for r in results if r["readiness"] == "LOW"]
    medium_docs = [r for r in results if r["readiness"] == "MEDIUM"]
    not_avail_docs = sorted(
        [r for r in results if r["not_available"] > 0],
        key=lambda r: -r["not_available"]
    )

    def _review_rows(docs, reason):
        if not docs:
            return f"_None — all documents meet the {reason} threshold._\n"
        out = f"| # | Document | Source Match % | NOT_AVAILABLE | Action Required |\n"
        out += f"|---|---|---:|---:|---|\n"
        for i, r in enumerate(docs, 1):
            out += (
                f"| {i} | `{r['filename']}` "
                f"| {r['source_match_pct']}% "
                f"| {r['not_available']} "
                f"| {reason} |\n"
            )
        return out

    human_review_section = (
        f"## ⚠ HUMAN REVIEW REQUIRED — CRITICAL (Source Match < 60%)\n\n"
        f"These documents have insufficient source evidence. "
        f"**Do NOT use for forward engineering without human validation.**\n\n"
        f"{_review_rows(low_docs, 'Validate all content against source before use')}\n"
        f"## ~ HUMAN REVIEW RECOMMENDED — MEDIUM (Source Match 60–79%)\n\n"
        f"These documents are usable but have gaps. "
        f"A reviewer should check INFERRED and ASSUMED sections.\n\n"
        f"{_review_rows(medium_docs, 'Review INFERRED/ASSUMED sections')}\n"
        f"## NOT_AVAILABLE Sections — Stakeholder Input Needed\n\n"
        f"These documents have sections where no source evidence was found. "
        f"A business stakeholder or SME must supply the missing information.\n\n"
        f"{_review_rows(not_avail_docs, 'Supply missing information — see NOT_AVAILABLE sections')}\n"
    )

    summary = (
        f"# Source Coverage Summary\n\n"
        f"Generated by hybrid coverage engine "
        f"(Option 1: Claude semantic estimate → Option 2: Python exact counts).\n"
        f"Documents sorted by Source Match % ascending — **lowest confidence first**.\n\n"
        f"## Overall\n\n"
        f"| Metric | Value |\n"
        f"|---|---|\n"
        f"| Total documents analysed | {len(results)} |\n"
        f"| Average source match % | {avg_overall}% |\n"
        f"| ✓ HIGH — safe for forward engineering (≥ 80%) | {high_count} |\n"
        f"| ~ MEDIUM — review recommended (60–79%) | {medium_count} |\n"
        f"| ! LOW — human review REQUIRED (< 60%) | {low_count} |\n\n"
        f"{human_review_section}"
        f"## Full Document Report (lowest match first)\n\n"
        f"| Document | Source Match % | Avg Confidence | NOT_AVAILABLE | Total Tags | Readiness |\n"
        f"|---|---:|---:|---:|---:|---|\n"
        f"{rows}\n"
        f"## Readiness Legend\n\n"
        f"| Signal | Meaning |\n"
        f"|---|---|\n"
        f"| ✓ HIGH | ≥ 80% source-matched — safe for forward engineering |\n"
        f"| ~ MEDIUM | 60–79% — usable with targeted human review |\n"
        f"| ! LOW | < 60% — significant gaps; human review required before use |\n\n"
        f"_Source Match % = (OBSERVED + DERIVED) / total evidence tags × 100_\n"
        f"_Counts are exact programmatic values from saved document files._\n"
    )

    summary_path = Path(output_dir) / "COVERAGE_SUMMARY.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"\n[Coverage Pass] Complete.")
    print(f"  Overall average source match: {avg_overall}%")
    print(f"  HIGH: {high_count}  MEDIUM: {medium_count}  LOW: {low_count}")
    print(f"  Coverage summary → {summary_path}")


def _run_self_correction_pass(
    foundation_dir: Path,
    fwd_eng_dir: Path,
    output_dir: str,
    layers: dict,
) -> int:
    """
    Call 5 — Self-correction pass.
    Scans all documents for LOW confidence sections, re-runs Claude on them,
    saves corrections, returns count of sections corrected.
    """
    import re as _re5

    print("\n[Self-Correction] Scanning all documents for LOW confidence sections...")

    # Collect LOW sections across all documents
    low_sections = []
    for directory in [foundation_dir, fwd_eng_dir]:
        for path in sorted(directory.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            # Find all LOW confidence occurrences
            low_matches = _LOW_CONFIDENCE_SECTION_PATTERN.findall(content)
            if low_matches:
                low_sections.append({
                    "filename": path.name,
                    "path": path,
                    "content": content,
                    "low_count": len(low_matches),
                })
                print(f"  {path.name} — {len(low_matches)} LOW confidence section(s)")

    if not low_sections:
        print("[Self-Correction] No LOW confidence sections found — all documents meet threshold.")
        return 0

    print(f"\n[Self-Correction] Found {sum(d['low_count'] for d in low_sections)} LOW section(s) across {len(low_sections)} document(s).")
    print("[Self-Correction] Running Call 5 — targeted re-examination...")

    # Build the LOW sections block for Claude
    low_sections_text = ""
    for doc in low_sections:
        low_sections_text += f"\n\n## Document: {doc['filename']}\n\n"
        # Extract just the paragraphs/rows containing LOW
        lines = doc["content"].split("\n")
        context_lines = []
        for i, line in enumerate(lines):
            if _LOW_CONFIDENCE_SECTION_PATTERN.search(line):
                # Include surrounding context (heading + content)
                start = max(0, i - 10)
                end = min(len(lines), i + 5)
                context_lines.append(f"[Lines {start}–{end}]")
                context_lines.extend(lines[start:end])
                context_lines.append("---")
        low_sections_text += "\n".join(context_lines)

    # Build source evidence summary
    source_evidence = "\n\n".join(
        f"## {key}\n\n{content[:4000]}"
        for key, content in layers.items()
        if content
    )

    call5_prompt = (
        f"{_SELF_CORRECT_PROMPT}\n\n"
        f"# LOW Confidence Sections to Re-examine\n\n"
        f"{low_sections_text}\n\n"
        f"# Original Source Evidence\n\n"
        f"{source_evidence}\n\n"
        f"Begin self-correction now. Output one === CORRECTION === block per section."
    )

    call5_output = call_claude(
        call5_prompt,
        label="Foundation Template Call 5 (self-correction of LOW sections)",
        timeout=3600,
        allow_tools=False,
    )
    save_output(output_dir, "Foundation_Raw_Output_Part5.md", call5_output)

    # Parse and apply corrections
    correction_pattern = _re5.compile(
        r'=== CORRECTION:\s*([^|]+)\|\s*([^=]+)\s*===(.*?)=== END CORRECTION ===',
        _re5.DOTALL
    )
    corrections = correction_pattern.findall(call5_output)
    applied = 0

    for filename_raw, section_heading, corrected_content in corrections:
        filename = filename_raw.strip()
        section_heading = section_heading.strip()
        corrected_content = corrected_content.strip()

        # Find the file
        if filename in [d["filename"] for d in low_sections if d["filename"] == filename]:
            path = next((d["path"] for d in low_sections if d["filename"] == filename), None)
            if path and path.exists():
                original = path.read_text(encoding="utf-8")
                # Find and replace the section
                heading_escaped = _re5.escape(section_heading)
                section_re = _re5.compile(
                    rf'(#+\s*{heading_escaped}[^\n]*\n)(.*?)(?=\n#+\s|\Z)',
                    _re5.DOTALL
                )
                new_content = section_re.sub(
                    lambda m: m.group(1) + corrected_content + "\n\n",
                    original,
                    count=1
                )
                if new_content != original:
                    path.write_text(new_content, encoding="utf-8")
                    applied += 1
                    print(f"  Corrected: {filename} — {section_heading}")

    print(f"\n[Self-Correction] Complete — {applied} section(s) corrected out of {len(corrections)} correction(s) returned.")
    return applied


# ── Main ───────────────────────────────────────────────────────────────────────

def run(output_dir: str) -> None:
    print("\n[Foundation Template] Loading all layer outputs...")
    layers = _load_layer_outputs(output_dir)

    all_layer_text = "\n\n".join(
        f"## {key}\n\n{content}"
        for key, content in layers.items()
        if content
    )

    missing_agents = [k for k, v in layers.items() if not v]
    if missing_agents:
        print(f"\n  WARNING: {len(missing_agents)} agent output(s) missing: {missing_agents}")
        print(f"  Activating fallback from DEEP_SCAN / file_cache...")
        fallback_text = _build_fallback_supplement(output_dir)
        if fallback_text:
            all_layer_text = all_layer_text + "\n\n" + fallback_text
            print(f"  Fallback supplement added ({len(fallback_text)} chars)")
    else:
        print(f"  All 8 agent outputs loaded — no fallback needed.")

    # Check templates exist
    if not _TEMPLATE_DIR.exists():
        print(f"\n  ERROR: Template directory not found: {_TEMPLATE_DIR}")
        print(f"  Expected: GENERIC_25_Enterprise_Forward_Engineering_Templates_INDUSTRY_BASED/")
        sys.exit(1)
    print(f"  Template directory found: {_TEMPLATE_DIR}")

    foundation_dir = Path(output_dir) / "Foundation_KnowledgeGraph"
    fwd_eng_dir    = Path(output_dir) / "ForwardEngineering_Docs"
    foundation_dir.mkdir(parents=True, exist_ok=True)
    fwd_eng_dir.mkdir(parents=True, exist_ok=True)

    part1_raw = Path(output_dir) / "Foundation_Raw_Output_Part1.md"
    part2_raw = Path(output_dir) / "Foundation_Raw_Output_Part2.md"

    # ── Call 1: KG + foundation docs + docs 01–10 ─────────────────────────────
    if part1_raw.exists() and part1_raw.stat().st_size > 0:
        print("\n[Foundation Template] Call 1 — already done, loading saved output...")
        call1_output = part1_raw.read_text(encoding="utf-8")
        docs1 = _split_documents(call1_output)
        print(f"  Loaded {len(docs1)} documents from previous run.")
    else:
        print("\n[Foundation Template] Call 1 — populating templates 01–10 + KG...")
        template_appendix_1 = _build_template_appendix(_PART1_TEMPLATES)
        call1_prompt = (
            f"{CALL1_PROMPT}"
            f"{template_appendix_1}\n\n"
            f"---\n\n"
            f"# All Layer Outputs (Oracle Source Evidence)\n\n"
            f"{all_layer_text}\n\n"
            f"Begin Part 1 now. Populate each template from the evidence above."
        )
        call1_output = call_claude(
            call1_prompt,
            label="Foundation Template Call 1 (KG + templates 01-10)",
            timeout=5400,
            allow_tools=False
        )
        save_output(output_dir, "Foundation_Raw_Output_Part1.md", call1_output)
        docs1 = _split_documents(call1_output)
        saved1 = _save_docs(docs1, foundation_dir, fwd_eng_dir)
        print(f"  Call 1: {len(saved1)} documents saved.")
        if not docs1:
            print("  [Warning] Call 1 — no markers found. Saving raw output.")
            save_output(str(foundation_dir), "Foundation_Template_Call1_Raw.md", call1_output)

    print("\n[Foundation Template] Reloading Call 1 docs from disk for Call 2 context...")
    docs1_filled = _reload_docs(docs1, foundation_dir, fwd_eng_dir)
    print(f"  Reloaded {len(docs1_filled)} document(s).")

    # ── Call 2: docs 11–20 ─────────────────────────────────────────────────────
    if part2_raw.exists() and part2_raw.stat().st_size > 0:
        print("\n[Foundation Template] Call 2 — already done, loading saved output...")
        call2_output = part2_raw.read_text(encoding="utf-8")
        docs2 = _split_documents(call2_output)
        print(f"  Loaded {len(docs2)} documents from previous run.")
    else:
        kg_json = docs1_filled.get("ENTERPRISE_KNOWLEDGE_GRAPH.json", "")
        kg_context_parts = []
        if kg_json:
            kg_context_parts.append(f"## Enterprise Knowledge Graph\n\n```json\n{kg_json}\n```")
        doc_order = [
            "CANONICAL_ENTERPRISE_MODEL.md", "ARCHITECTURE_INVENTORY.md",
            "TRACEABILITY_MATRIX.md", "FORWARD_ENGINEERING_INPUT_MAP.md",
            "01_BRD.md", "02_BUSINESS_CAPABILITY_MODEL.md", "03_USE_CASE_SPECIFICATION.md",
            "04_BUSINESS_PROCESS_MODEL.md", "05_DOMAIN_MODEL.md", "06_DATA_DICTIONARY.md",
            "07_DATA_MODEL_SPECIFICATION.md", "08_ERD.md", "09_DATA_FLOW_DIAGRAM.md",
            "10_SERVICE_CATALOG.md",
        ]
        for doc_name in doc_order:
            if doc_name in docs1_filled and docs1_filled[doc_name]:
                kg_context_parts.append(f"## {doc_name}\n\n{docs1_filled[doc_name]}")
        kg_context = "\n\n---\n\n".join(kg_context_parts) if kg_context_parts else call1_output

        print("\n[Foundation Template] Call 2 — populating templates 11–20...")
        template_appendix_2 = _build_template_appendix(_PART2_TEMPLATES)
        call2_prompt = (
            f"{CALL2_PROMPT}"
            f"{template_appendix_2}\n\n"
            f"---\n\n"
            f"# Part 1 Documents (context — do not regenerate these)\n\n"
            f"{kg_context}\n\n"
            f"Begin Part 2 now. Populate each template from the evidence above."
        )
        call2_output = call_claude(
            call2_prompt,
            label="Foundation Template Call 2 (templates 11-20)",
            timeout=5400,
            allow_tools=False
        )
        save_output(output_dir, "Foundation_Raw_Output_Part2.md", call2_output)
        docs2 = _split_documents(call2_output)
        saved2 = _save_docs(docs2, foundation_dir, fwd_eng_dir)
        print(f"  Call 2: {len(saved2)} documents saved.")
        if not docs2:
            print("  [Warning] Call 2 — no markers found. Saving raw output.")
            save_output(str(fwd_eng_dir), "Foundation_Template_Call2_Raw.md", call2_output)

    # ── Call 3: Template compliance verification + cleaning ────────────────────
    part3_raw = Path(output_dir) / "Foundation_Raw_Output_Part3.md"
    if part3_raw.exists() and part3_raw.stat().st_size > 0:
        print("\n[Foundation Template] Call 3 — already done, loading saved output...")
        call3_output = part3_raw.read_text(encoding="utf-8")
        docs3 = _split_documents_updates(call3_output)
        print(f"  Loaded {len(docs3)} update(s) from previous run.")
    else:
        print("\n[Foundation Template] Call 3 — Template compliance verification...")

        all_25_docs = {}
        all_25_docs.update(docs1_filled)
        for filename, content in docs2.items():
            all_25_docs[filename] = content

        generated_docs_text = "\n\n---\n\n".join(
            f"## {fname}\n\n{content[:8000]}"
            for fname, content in all_25_docs.items()
            if content
        )
        agent_outputs_text = "\n\n---\n\n".join(
            f"## {key}\n\n{content[:6000]}"
            for key, content in layers.items()
            if content
        )

        call3_prompt = (
            f"{CALL3_PROMPT}\n\n"
            f"{_COVERAGE_CALL3_INSTRUCTION}\n\n"
            f"# All 25 Generated Documents\n\n"
            f"{generated_docs_text}\n\n"
            f"# Original 8 Agent Outputs (source of truth)\n\n"
            f"{agent_outputs_text}\n\n"
            f"Begin verification pass now."
        )

        call3_output = call_claude(
            call3_prompt,
            label="Foundation Template Call 3 (verification)",
            timeout=5400,
            allow_tools=False
        )
        save_output(output_dir, "Foundation_Raw_Output_Part3.md", call3_output)
        docs3 = _split_documents_updates(call3_output)

        updated_count = 0
        for filename, updated_content in docs3.items():
            if filename in _FOUNDATION_FILES:
                path = foundation_dir / filename
            else:
                path = fwd_eng_dir / filename
            if path.exists() and updated_content.strip():
                updated_content = _clean_document(filename, updated_content)
                path.write_text(updated_content, encoding="utf-8")
                updated_count += 1
                print(f"  Updated → {path}")
        print(f"  Call 3: {updated_count} document(s) updated.")

    # ── Call 4: Cross-document consistency check ───────────────────────────────
    part4_raw = Path(output_dir) / "Foundation_Raw_Output_Part4.md"
    if part4_raw.exists() and part4_raw.stat().st_size > 0:
        print("\n[Foundation Template] Call 4 — already done, loading saved output...")
        call4_output = part4_raw.read_text(encoding="utf-8")
        docs4 = _split_documents_updates(call4_output)
        print(f"  Loaded {len(docs4)} update(s) from previous run.")
    else:
        print("\n[Foundation Template] Call 4 — Cross-document consistency check...")

        all_final_docs = {}
        all_final_docs.update(docs1_filled)
        for filename, content in docs2.items():
            all_final_docs[filename] = content
        if 'docs3' in dir():
            for filename, content in docs3.items():
                if content.strip():
                    all_final_docs[filename] = content

        for filename in list(all_final_docs.keys()):
            if filename in _FOUNDATION_FILES:
                path = foundation_dir / filename
            else:
                path = fwd_eng_dir / filename
            if path.exists() and path.stat().st_size > 0:
                all_final_docs[filename] = path.read_text(encoding="utf-8")

        final_docs_text = "\n\n---\n\n".join(
            f"## {fname}\n\n{content[:10000]}"
            for fname, content in all_final_docs.items()
            if content
        )

        call4_prompt = (
            f"{CALL4_PROMPT}\n\n"
            f"# All 25 Final Documents\n\n"
            f"{final_docs_text}\n\n"
            f"Begin cross-document consistency check now."
        )

        call4_output = call_claude(
            call4_prompt,
            label="Foundation Template Call 4 (consistency check)",
            timeout=5400,
            allow_tools=False
        )
        save_output(output_dir, "Foundation_Raw_Output_Part4.md", call4_output)
        docs4 = _split_documents_updates(call4_output)

        # Save consistency report
        if "CONSISTENCY_REPORT.md" not in docs4:
            import re as _re4
            consistency_match = _re4.search(
                r"=== CONSISTENCY_REPORT ===(.*?)(?====\s*(?:UPDATE|DOCUMENT):|$)",
                call4_output, _re4.DOTALL
            )
            if consistency_match:
                report_content = consistency_match.group(1).strip()
                report_path = foundation_dir / "CONSISTENCY_REPORT.md"
                report_path.write_text(
                    f"# Cross-Document Consistency Report\n\n{report_content}",
                    encoding="utf-8"
                )
                print(f"  Saved consistency report → {report_path}")

        updated4_count = 0
        for filename, updated_content in docs4.items():
            if filename in _FOUNDATION_FILES:
                path = foundation_dir / filename
            else:
                path = fwd_eng_dir / filename
            if updated_content.strip():
                updated_content = _clean_document(filename, updated_content)
                path.write_text(updated_content, encoding="utf-8")
                updated4_count += 1
                print(f"  Saved/Updated → {path}")
        print(f"  Call 4: {updated4_count} document(s) updated after consistency check.")

    total = len(docs1) + len(docs2)
    verified  = len(docs3) if 'docs3' in dir() else 0
    consistent = len(docs4) if 'docs4' in dir() else 0
    print(f"\n[Foundation Template] Complete — {total} documents generated, "
          f"{verified} updated by verification, {consistent} updated by consistency check.")
    print(f"  Foundation_KnowledgeGraph: {foundation_dir}")
    print(f"  ForwardEngineering_Docs:   {fwd_eng_dir}")

    # ── Hybrid Coverage Pass (Option 2 — Python exact counts) ─────────────────
    # Option 1 (Claude estimate) was injected into Call 3 prompt above.
    # Option 2 (Python exact counts) runs now — overwrites Claude's estimates
    # with programmatically verified figures and writes COVERAGE_SUMMARY.md.
    _run_coverage_pass(foundation_dir, fwd_eng_dir, output_dir)
    print(f"\n  COVERAGE_SUMMARY.md → {Path(output_dir) / 'COVERAGE_SUMMARY.md'}")

    # ── Call 5: Self-Correction Pass ───────────────────────────────────────────
    # Scans all documents for LOW confidence sections (score < 0.50),
    # re-runs Claude on those specific sections to upgrade or confirm NOT_AVAILABLE,
    # then re-runs the coverage pass to update COVERAGE_SUMMARY.md with final scores.
    part5_raw = Path(output_dir) / "Foundation_Raw_Output_Part5.md"
    if part5_raw.exists() and part5_raw.stat().st_size > 0:
        print("\n[Self-Correction] Call 5 — already done, skipping (delete Part5 to re-run).")
    else:
        corrected = _run_self_correction_pass(foundation_dir, fwd_eng_dir, output_dir, layers)
        if corrected > 0:
            print("\n[Coverage Pass] Re-running after self-correction to update final scores...")
            _run_coverage_pass(foundation_dir, fwd_eng_dir, output_dir)
            print(f"  Final COVERAGE_SUMMARY.md → {Path(output_dir) / 'COVERAGE_SUMMARY.md'}")
        else:
            print("\n[Self-Correction] No corrections applied — COVERAGE_SUMMARY.md unchanged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Foundation Runner (Template-Driven) — populate 25 enterprise templates"
    )
    parser.add_argument(
        "--output", required=True,
        help="Root output directory containing the *_Analysis/ folders"
    )
    args = parser.parse_args()
    run(args.output)
