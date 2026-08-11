"""
Foundation Runner
-----------------
Synthesizes all 4 layer outputs (BA, DA, TA, AA) into the
Enterprise Knowledge Graph and 4 read-only foundation views,
then generates the 20 forward-engineering documents.

Uses TWO sequential Claude calls to avoid output truncation:
  Call 1 → 5 foundation docs + forward-engineering docs 01–10
  Call 2 → forward-engineering docs 11–20 (receives KG summary as context)

Reads:
  <output>/Business_Analysis/     - BA Agent 1 + 2 output
  <output>/Data_Analysis/         - DA Agent 1 + 2 output
  <output>/Technology_Analysis/   - TA Agent 1 + 2 output
  <output>/Application_Analysis/  - AA Agent 1 + 2 output

Writes:
  <output>/Foundation_KnowledgeGraph/ENTERPRISE_KNOWLEDGE_GRAPH.json
  <output>/Foundation_KnowledgeGraph/CANONICAL_ENTERPRISE_MODEL.md
  <output>/Foundation_KnowledgeGraph/ARCHITECTURE_INVENTORY.md
  <output>/Foundation_KnowledgeGraph/TRACEABILITY_MATRIX.md
  <output>/Foundation_KnowledgeGraph/FORWARD_ENGINEERING_INPUT_MAP.md
  <output>/ForwardEngineering_Docs/01_BRD.md … 20_UI_UX_SPECIFICATION.md
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from base_runner import call_claude, save_output, extract_deep_scan_sections, supplement_from_cache, detect_and_fill_gaps

# ── Call 1 prompt: Foundation KG + docs 01–10 ─────────────────────────────────

CALL1_PROMPT = """
# Foundation Synthesis Agent — Part 1 of 2

You are the Foundation / Synthesis agent. Your job is to reconcile all four
architecture layers (Business, Data, Application, Technology) into a single
Enterprise Knowledge Graph and four read-only foundation views, then produce
the first 10 forward-engineering documents.

## Rules

1. NEVER invent facts. Every node must trace to evidence in the layer outputs provided.
2. Where the same concept appears in multiple layers (e.g. "Order" in BA, DA, AA),
   merge into ONE canonical node — do not duplicate.
3. Assign confidence: HIGH (direct code evidence), MEDIUM (inferred from patterns),
   LOW (assumed from naming), ASSUMED (no evidence found).
4. Every node must carry: id, type, owner_layer, confidence, evidence (source ref).
5. Record every cross-layer conflict in normalization_log with a DISC-### id.
6. Record every unresolved question in open_questions with an OQ-### id.
7. Assumptions that cannot be verified go in assumptions with an ASMP-### id.
8. The anti-hallucination rule: if you do not know → say unknown, not a guess.
9. COMPLETENESS RULE: Mark a field MISSING only when the information genuinely
   does not appear anywhere in the layer outputs. If a table's columns appear in
   DA Agent output, list ALL of them — do not say "columns omitted for brevity".
   If a package's procedures appear in AA Agent output, list ALL of them.
10. ENUMERATE EVERYTHING: For every domain, list every entity with every field.
    For every package, list every procedure. For every form, list every trigger.
    The forward engineering agents depend on this output — incomplete data here
    means incomplete generated code downstream.
11. BUSINESS RULES: Extract EXACT values — thresholds, limits, formulas.
    "hire_date must be within 180 days of offer" is a business rule.
    "hire date validation" is not. Always prefer the specific over the general.
12. BR-xxx ID ASSIGNMENT — assign sequential BR-xxx IDs starting from BR-001.
    CRITICAL DEFECTS must be assigned prominent, low-numbered IDs so they appear
    early in all lists. Known critical security defects found in the source code
    (e.g. authentication bypass where password is never verified, hardcoded
    encryption keys, session management bugs) must be assigned BR-xxx IDs in
    the BRD's Security Requirements section with the SAME ID used throughout
    ALL documents. Never assign the same BR-xxx number to two different
    requirements — each BR-xxx ID must have exactly one meaning across all
    25 output documents.

## Required Output — Part 1

Produce ALL of the following in this exact order, separated by markers:

=== DOCUMENT: ENTERPRISE_KNOWLEDGE_GRAPH.json ===
(full JSON — metadata, business, data, application, technology,
 cross_links, assumptions, normalization_log, open_questions)

=== DOCUMENT: CANONICAL_ENTERPRISE_MODEL.md ===
(human-readable summary of every domain, aggregate, service, API — one row per node)

=== DOCUMENT: ARCHITECTURE_INVENTORY.md ===
(deployables, databases, APIs, services, entities, tech stack, security findings, PII, debt)

=== DOCUMENT: TRACEABILITY_MATRIX.md ===
(Capability → Process → Entity → Service → API → Database → Confidence, one row per capability)

=== DOCUMENT: FORWARD_ENGINEERING_INPUT_MAP.md ===
(what is KNOWN, INFERRED, MISSING — input spec for AI-assisted code regeneration)

=== DOCUMENT: 01_BRD.md ===
(Business Requirements Document)

=== DOCUMENT: 02_BUSINESS_CAPABILITY_MODEL.md ===

=== DOCUMENT: 03_USE_CASE_SPECIFICATION.md ===

=== DOCUMENT: 04_BUSINESS_PROCESS_MODEL.md ===

=== DOCUMENT: 05_DOMAIN_MODEL.md ===
(with DDD bounded contexts and Mermaid context maps)

=== DOCUMENT: 06_DATA_DICTIONARY.md ===

=== DOCUMENT: 07_DATA_MODEL_SPECIFICATION.md ===
(including physical schema and SQL DDL)

=== DOCUMENT: 08_ERD.md ===

=== DOCUMENT: 09_DATA_FLOW_DIAGRAM.md ===

=== DOCUMENT: 10_SERVICE_CATALOG.md ===

CRITICAL RULES:
- Output ALL document content as plain text using the === DOCUMENT: <filename> === markers.
- Do NOT use file writing tools. Do NOT write files. Do NOT use any tools at all.
- Every document must appear in full — nothing else will be captured.
- End your response after 10_SERVICE_CATALOG.md. Do NOT write docs 11–20 yet.

---
"""

# ── Call 2 prompt: docs 11–20 ─────────────────────────────────────────────────

CALL2_PROMPT = """
# Foundation Synthesis Agent — Part 2 of 2

You are given the Enterprise Knowledge Graph and foundation views already produced
in Part 1. Your job is to generate forward-engineering documents 11–20.

Each document must be:
- Grounded in the Knowledge Graph — cite node IDs where relevant
- Technology-neutral where the target stack is unresolved
- Written at senior-architect level
- Self-contained — a developer should be able to implement from each document alone
- BR-xxx IDs must be used exactly as they were defined in 01_BRD.md from Part 1.
  Never reassign a BR-xxx to a different requirement. Copy the exact IDs.

Produce ALL of the following in order, separated by markers:

=== DOCUMENT: 11_API_CONTRACT_SPECIFICATION.md ===
(full REST contracts for all endpoints)

=== DOCUMENT: 12_TECHNOLOGY_BLUEPRINT.md ===

=== DOCUMENT: 13_SECURITY_ARCHITECTURE.md ===
(including RBAC model and modernization plan)

=== DOCUMENT: 14_NFR_SPECIFICATION.md ===

=== DOCUMENT: 15_FORWARD_ENGINEERING_SPECIFICATION.md ===
(generation rules and validation gates)

=== DOCUMENT: 16_GENERATION_MANIFEST.json ===
(machine-readable JSON — leave target_stack empty)

=== DOCUMENT: 17_FORWARD_ENGINEERING_READINESS_REPORT.md ===
(scored readiness assessment)

=== DOCUMENT: 18_DEPLOYMENT_ARCHITECTURE.md ===

=== DOCUMENT: 19_FRONTEND_ARCHITECTURE.md ===

=== DOCUMENT: 20_UI_UX_SPECIFICATION.md ===

CRITICAL RULES:
- Output ALL document content as plain text using the === DOCUMENT: <filename> === markers.
- Do NOT use file writing tools. Do NOT write files. Do NOT use any tools at all.
- Every document must appear in full — nothing else will be captured.

---

# Enterprise Knowledge Graph and Foundation Views (from Part 1)

"""

# ── Call 3 prompt: verification pass ──────────────────────────────────────────

CALL3_PROMPT = """
# Foundation Synthesis Agent — Verification Pass (Part 3 of 4)

You are given all 25 generated Foundation documents plus the original 8 agent
outputs that were used to create them.

## PRIMARY TASK: Clean artifact text from every document

Before checking for missing content, scan every document for the following
strings and REMOVE them (they are AI generation artifacts, not business content):

ARTIFACT STRINGS TO REMOVE (any document that contains these must be updated):
- "Looking at the source content"
- "Here is the updated snippet"
- "Updated snippet"
- "Let me check"
- "I'll now read"
- "I need to"
- "Let me look"
- Any HTML comment block: <!-- GAP-FILLED SECTION --> or similar
- Any inline editorial marker: [GAP-FILLED] when it appears as a label rather than content
- Any line that reads like AI internal reasoning ("I can see that...", "Based on the above...")

When removing artifact text, do NOT leave a blank line or break the document structure.
Remove the artifact line completely and join cleanly to the surrounding content.

## SECONDARY TASK: Check for duplicate sections

For each document, check for any ## or ### heading that appears more than once.
If found: keep the FIRST occurrence only. Delete all subsequent duplicate blocks
(from the duplicate heading down to the next same-level heading).

## TERTIARY TASK: Check for missing content from agent outputs

1. Tables documented in agent outputs but NOT in 06_DATA_DICTIONARY.md or 08_ERD.md
2. Procedures documented in agent outputs but NOT in 10_SERVICE_CATALOG.md or 11_API_CONTRACT_SPECIFICATION.md
3. Business rules in BA agent output NOT reflected in 01_BRD.md or 03_USE_CASE_SPECIFICATION.md
4. Security findings in TA agent output NOT in 13_SECURITY_ARCHITECTURE.md
5. Form triggers or UI patterns NOT in 19_FRONTEND_ARCHITECTURE.md or 20_UI_UX_SPECIFICATION.md
6. Any use case in 03_USE_CASE_SPECIFICATION.md missing: Actor, Preconditions, Postconditions, Main Flow, Alternate Flows, Business Rules Applied, or Defects/Gaps
7. Contradictions between documents — same rule stated differently in two documents

## OUTPUT FORMAT

For each document that needs any change (artifact removal, dedup, or content addition):
=== UPDATE: <filename> ===
<the COMPLETE updated document content — every line, from start to finish>

CRITICAL OUTPUT RULES:
- Every UPDATE block must contain the FULL document from the very first line to the very last line.
  Do NOT produce a partial document or a diff. The entire file content goes in the UPDATE block.
- Do NOT begin the document content with phrases like "Here is the updated document:" or
  "I've removed the artifacts from". Start directly with the document content (e.g., # Document Title).
- Only output UPDATE blocks for documents that actually changed.
- Mark all ADDED content with [VERIFIED-SUPPLEMENT] so new additions are visible.
- Do NOT add [VERIFIED-SUPPLEMENT] to existing content that you are keeping unchanged.

---
"""

# ── Call 4 prompt: cross-document consistency check ───────────────────────────

CALL4_PROMPT = """
# Foundation Synthesis Agent — Cross-Document Consistency Check (Part 4 of 4)

You are given all 25 generated Foundation documents.

Your job: validate that every ID reference, every fact, and every table/procedure
name is consistent across all 25 documents. This is a cross-document link
validation and ID collision detection pass.

## Checks to perform

1. BR-xxx REFERENCE INTEGRITY
   a) Every BR-xxx ID mentioned in any document must exist in 01_BRD.md.
      Flag any BR-xxx that is referenced elsewhere but not defined in the BRD.
   b) ID COLLISION CHECK — each BR-xxx number must mean exactly one thing.
      If 01_BRD.md defines BR-042 as Requirement A, and 03_USE_CASE_SPECIFICATION.md
      uses BR-042 to mean Requirement B, that is a collision.
      For collisions: the BRD is authoritative for the requirement text.
      All other documents must use the BRD's definition, or the BRD must be corrected.
      Flag every collision as a HUMAN-DECISION-REQUIRED item.

2. USE CASE REFERENCE INTEGRITY
   Every UC-xxx ID mentioned in any document must exist in 03_USE_CASE_SPECIFICATION.md.
   Flag any UC-xxx that is referenced but not defined.

3. TABLE REFERENCE INTEGRITY
   Every table name (UPPER_CASE naming) mentioned in any document must appear in
   07_DATA_MODEL_SPECIFICATION.md. Flag any table referenced but not in the data model.

4. PACKAGE/PROCEDURE REFERENCE INTEGRITY
   Every PKG_xxx.procedure_name mentioned in any document must appear in
   11_API_CONTRACT_SPECIFICATION.md. Flag any that are missing.

5. ACTOR ID INTEGRITY
   Every ACT-xxx ID must exist in 03_USE_CASE_SPECIFICATION.md Actor Catalogue.

6. NUMERIC FACT CONTRADICTIONS
   Find cases where the same numeric fact appears with different values in two documents:
   - Session timeout values (e.g. 30 minutes vs 60 minutes for the SAME system)
   - Tax rates (SS, Medicare, FUTA)
   - Rating ranges (performance review scale)
   - Salary/deduction limits or thresholds
   Note: it is NOT a contradiction if one value is the current/legacy system and
   another is the proposed/new system, as long as both documents clearly label which
   system the value applies to.

7. ORACLE FORMS MODULE COVERAGE
   Every Oracle Forms module name (HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE,
   HRMS_PERFORMANCE, HRMS_LOGIN, HRMS_MENU) must appear in at least one of:
   19_FRONTEND_ARCHITECTURE.md, 20_UI_UX_SPECIFICATION.md.
   If a form module is absent, flag it — the frontend doc must reference each
   source form by its original Oracle Forms name.

## Output format

=== CONSISTENCY_REPORT ===
## BR-xxx Broken References
| BR ID | Referenced In | Not Found In BRD | Recommendation |
|---|---|---|---|

## BR-xxx ID Collisions
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

## Summary
Total BR collisions: N
Total broken references: N
Total contradictions: N
Oracle Forms coverage gaps: N
Documents needing update: list them
Overall assessment: CONSISTENT / ISSUES-FOUND

Then for each document that needs fixing, produce the corrected version:
=== UPDATE: <filename> ===
<complete corrected document content — full file from first line to last>

CRITICAL: Only fix genuine errors. Do not rewrite correct content.
CRITICAL: If a contradiction cannot be resolved from the documents alone, mark it HUMAN-DECISION-REQUIRED.
CRITICAL: Do NOT begin any UPDATE block with conversational text. Start directly with the document content.
CRITICAL: Every UPDATE block must contain the FULL document, not a diff or excerpt.

---
"""


# ── Artifact stripping ────────────────────────────────────────────────────────

# Exact strings that are AI generation artifacts — never valid document content.
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
    """
    Remove AI generation artifact text from a document.
    Operates line-by-line so surrounding content is preserved exactly.
    Also removes <!-- GAP-FILLED SECTION --> HTML comments.
    """
    lines = content.split('\n')
    clean = []
    for line in lines:
        stripped = line.strip()
        # Check line-prefix artifacts (case-insensitive)
        if any(stripped.lower().startswith(p.lower()) for p in _ARTIFACT_LINE_PREFIXES):
            continue
        # Remove HTML comment artifact markers
        line = _ARTIFACT_HTML_COMMENT.sub('', line)
        # Skip lines that became empty after comment removal
        if not line.strip():
            # Only add blank line if previous line wasn't also blank
            if clean and clean[-1] != '':
                clean.append('')
            continue
        clean.append(line)
    # Remove trailing blank lines
    while clean and clean[-1] == '':
        clean.pop()
    return '\n'.join(clean)


def _deduplicate_headings(content: str) -> str:
    """
    Remove duplicate ## or ### sections within a single document.
    When a heading appears more than once, keeps the first occurrence only.
    Removes all subsequent occurrences from that heading down to the next
    heading at the same or higher level.
    """
    lines = content.split('\n')
    seen_headings = set()
    result = []
    skip_until_level = None  # heading level we are skipping

    for line in lines:
        heading_match = _re.match(r'^(#{1,6})\s+(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()

            # If we are currently skipping, check if we should stop
            if skip_until_level is not None:
                if level <= skip_until_level:
                    # Reached a heading at same or higher level — stop skipping
                    skip_until_level = None
                else:
                    continue  # still inside the duplicate block

            key = (level, heading_text.lower())
            if key in seen_headings:
                # Start skipping this duplicate block
                skip_until_level = level
                continue
            else:
                seen_headings.add(key)
                result.append(line)
        else:
            if skip_until_level is not None:
                continue  # inside duplicate block — skip content
            result.append(line)

    return '\n'.join(result)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _load_layer_outputs(output_dir: str) -> dict:
    """Load both Agent 1 and Agent 2 outputs for maximum completeness."""
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
    """Parse Call 3 output which uses === UPDATE: <filename> === markers."""
    import re
    docs = {}
    pattern = re.compile(r"=== UPDATE:\s*(.+?)\s*===", re.IGNORECASE)
    parts = pattern.split(text)
    i = 1
    while i < len(parts) - 1:
        filename = parts[i].strip()
        content  = parts[i + 1].strip()
        docs[filename] = content
        i += 2
    return docs


def _clean_document(filename: str, content: str) -> str:
    """Strip artifact text and deduplicate headings. Skip JSON files."""
    if filename.endswith('.json'):
        return content
    content = _strip_artifacts(content)
    content = _deduplicate_headings(content)
    return content


def _save_docs(docs: dict, foundation_dir: Path, fwd_eng_dir: Path,
               output_dir: str = None) -> list:
    foundation_files = {
        "ENTERPRISE_KNOWLEDGE_GRAPH.json",
        "CANONICAL_ENTERPRISE_MODEL.md",
        "ARCHITECTURE_INVENTORY.md",
        "TRACEABILITY_MATRIX.md",
        "FORWARD_ENGINEERING_INPUT_MAP.md",
    }
    saved = []
    for filename, content in docs.items():
        # Per-document gap detection: independently fill gaps in each document
        # before writing to disk. Falls back DEEP_SCAN → file_cache → source.
        if output_dir:
            content = _fill_document_gaps(filename, content, output_dir)
        # Strip artifact text and deduplicate headings on every document
        content = _clean_document(filename, content)
        if filename in foundation_files:
            path = foundation_dir / filename
        else:
            path = fwd_eng_dir / filename
        path.write_text(content, encoding="utf-8")
        saved.append(str(path))
        print(f"  Saved → {path}")
    return saved


def _fill_document_gaps(doc_name: str, doc_content: str, output_dir: str) -> str:
    """
    Per-document gap detection: scan one Foundation document for missing/thin
    sections, fetch the relevant source files from DEEP_SCAN → file_cache,
    then ask Claude to fill only those gaps.

    Operates independently on each of the 25 output documents so a gap in
    one document never prevents another from being complete.
    Never raises — returns the original content on any error.
    """
    # Quick heuristic: skip gap-fill if the document is already substantial
    # (> 3000 chars) AND contains no obvious gap markers.
    gap_markers = [
        "MISSING", "not found", "no data", "unknown", "could not locate",
        "not available", "insufficient", "incomplete", "TODO", "[MISSING]",
        "no procedures found", "no tables found", "no business rules found",
    ]
    has_gap_marker = any(m.lower() in doc_content.lower() for m in gap_markers)
    if len(doc_content) > 3000 and not has_gap_marker:
        return doc_content

    print(f"  [Foundation Gap] {doc_name} — gap markers detected, running targeted fill...")

    gap_prompt = (
        f"The following Foundation document has been generated but may be incomplete.\n"
        f"Document name: {doc_name}\n\n"
        f"Identify any sections that are MISSING, INCOMPLETE, or reference entities/procedures "
        f"for which no data was provided. Return ONLY a JSON array of source file paths "
        f"(e.g. 'ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_PAYROLL.pkb') that "
        f"would contain the missing data. Return [] if the document is already complete.\n\n"
        f"Document content:\n{doc_content[:40000]}"
    )

    try:
        import re as _re
        import json as _json

        gap_response = call_claude(gap_prompt, label=f"Foundation gap-detect {doc_name}", timeout=300)

        gap_files = []
        try:
            gap_files = _json.loads(gap_response.strip())
            if not isinstance(gap_files, list):
                gap_files = []
        except Exception:
            matches = _re.findall(r'\[[\s\S]*?\]', gap_response)
            for candidate in matches:
                try:
                    parsed = _json.loads(candidate)
                    if isinstance(parsed, list) and len(parsed) > len(gap_files):
                        gap_files = parsed
                except Exception:
                    pass

        if not gap_files:
            return doc_content

        print(f"  [Foundation Gap] {doc_name} — fetching {len(gap_files)} file(s) from DEEP_SCAN/cache...")
        sections = extract_deep_scan_sections(output_dir, gap_files)
        sections = supplement_from_cache(output_dir, gap_files, sections)

        # Only proceed if we actually got real content
        has_real = any(
            "[Not found in deep scan]" not in part
            for part in sections.split("=== FILE:")[1:]
        )
        if not has_real:
            print(f"  [Foundation Gap] {doc_name} — no additional content found in fallback sources.")
            return doc_content

        fill_prompt = (
            f"The following Foundation document has gaps or missing sections.\n"
            f"Additional source file contents are provided below to fill those gaps.\n\n"
            f"Rules:\n"
            f"- Keep ALL existing content — do not remove or rewrite anything\n"
            f"- Only ADD new data that fills the identified gaps\n"
            f"- Mark newly added content with [SUPPLEMENTED] so it is visible\n"
            f"- If a section was MISSING or INCOMPLETE, fill it in from the source files\n"
            f"- CRITICAL: Begin your response DIRECTLY with the document content.\n"
            f"  Do NOT write any preamble, explanation, or commentary before the document.\n"
            f"  Do NOT write 'Here is the updated document:' or similar.\n"
            f"  The very first character of your response must be part of the document.\n"
            f"- CRITICAL: Do NOT include any of these strings anywhere in your output:\n"
            f"  'Looking at the source content', 'Here is the updated snippet',\n"
            f"  'Updated snippet', 'Let me check', 'I need to', 'Based on the above'\n\n"
            f"# Additional Source Files (retrieved via fallback chain)\n\n{sections}\n\n"
            f"# Document to Supplement: {doc_name}\n\n{doc_content}"
        )

        filled = call_claude(fill_prompt, label=f"Foundation fill {doc_name}", timeout=1800)
        print(f"  [Foundation Gap] {doc_name} — gaps filled successfully.")
        return filled

    except Exception as exc:
        print(f"  [Foundation Gap] {doc_name} — gap fill skipped ({exc}).")
        return doc_content


def _reload_filled_docs(docs_raw: dict, foundation_dir: Path, fwd_eng_dir: Path) -> dict:
    """
    Re-read every Call 1 document from disk after _save_docs() has run.
    _save_docs() calls _fill_document_gaps() on each doc before writing,
    so the disk versions are the complete gap-filled versions.
    This ensures Call 2 receives the enriched content, not the raw output.
    Falls back to the raw in-memory value if the file doesn't exist on disk.
    """
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
            filled[filename] = raw_content  # fallback to raw if disk write failed
    return filled


def _build_fallback_supplement(output_dir: str) -> str:
    """
    Build a supplementary context block from DEEP_SCAN_OUTPUT.md and file_cache.json
    to fill any gaps in the 8 agent output files.
    Called only when one or more agent outputs are empty or missing.
    """
    supplement_parts = []

    # Layer 1: try DEEP_SCAN_OUTPUT.md
    deep_scan_path = Path(output_dir) / "DEEP_SCAN_OUTPUT.md"
    if deep_scan_path.exists() and deep_scan_path.stat().st_size > 0:
        deep_scan_text = deep_scan_path.read_text(encoding="utf-8")
        supplement_parts.append(
            f"## DEEP_SCAN_OUTPUT.md (fallback — agent outputs incomplete)\n\n{deep_scan_text}"
        )
        print(f"  [Foundation Fallback] Added DEEP_SCAN_OUTPUT.md ({len(deep_scan_text)} chars)")
    else:
        # Layer 2: try file_cache.json raw content
        cache_path = Path(output_dir) / "file_cache.json"
        if cache_path.exists():
            import json as _json
            with open(cache_path, encoding="utf-8") as f:
                cache = _json.load(f)
            raw_parts = []
            for file_path, content in cache.items():
                raw_parts.append(f"=== FILE: {file_path} ===\n{content}")
            raw_text = "\n\n".join(raw_parts)
            supplement_parts.append(
                f"## file_cache.json raw source (fallback — deep scan unavailable)\n\n{raw_text}"
            )
            print(f"  [Foundation Fallback] Added {len(cache)} files from file_cache.json")

    return "\n\n".join(supplement_parts)


# ── Main ───────────────────────────────────────────────────────────────────────

def run(output_dir: str) -> None:
    print("\n[Foundation] Loading all layer outputs...")
    layers = _load_layer_outputs(output_dir)

    all_layer_text = "\n\n".join(
        f"## {key}\n\n{content}"
        for key, content in layers.items()
        if content
    )

    # Check if any critical agent outputs are missing — if so, supplement from DEEP_SCAN / file_cache
    missing_agents = [k for k, v in layers.items() if not v]
    if missing_agents:
        print(f"\n  [Foundation] WARNING: {len(missing_agents)} agent output(s) missing: {missing_agents}")
        print(f"  [Foundation] Activating fallback — supplementing from DEEP_SCAN / file_cache...")
        fallback_text = _build_fallback_supplement(output_dir)
        if fallback_text:
            all_layer_text = all_layer_text + "\n\n" + fallback_text
            print(f"  [Foundation] Fallback supplement added ({len(fallback_text)} chars)")
    else:
        print(f"  [Foundation] All 8 agent outputs loaded — no fallback needed.")

    foundation_dir = Path(output_dir) / "Foundation_KnowledgeGraph"
    fwd_eng_dir    = Path(output_dir) / "ForwardEngineering_Docs"
    foundation_dir.mkdir(parents=True, exist_ok=True)
    fwd_eng_dir.mkdir(parents=True, exist_ok=True)

    part1_raw = Path(output_dir) / "Foundation_Raw_Output_Part1.md"
    part2_raw = Path(output_dir) / "Foundation_Raw_Output_Part2.md"

    # ── Call 1: KG + foundation docs + docs 01–10 ─────────────────────────────
    if part1_raw.exists() and part1_raw.stat().st_size > 0:
        print("\n[Foundation] Call 1 — already done, loading saved output...")
        call1_output = part1_raw.read_text(encoding="utf-8")
        docs1 = _split_documents(call1_output)
        print(f"  Loaded {len(docs1)} documents from previous run.")
    else:
        print("\n[Foundation] Call 1 — Enterprise Knowledge Graph + docs 01–10...")
        call1_prompt = (
            f"{CALL1_PROMPT}\n\n"
            f"# All Layer Outputs\n\n"
            f"{all_layer_text}\n\n"
            f"Begin Part 1 now."
        )
        call1_output = call_claude(call1_prompt, label="Foundation Call 1 (KG + docs 01-10)", timeout=5400, allow_tools=False)
        save_output(output_dir, "Foundation_Raw_Output_Part1.md", call1_output)
        docs1 = _split_documents(call1_output)
        saved1 = _save_docs(docs1, foundation_dir, fwd_eng_dir, output_dir)
        print(f"  Call 1: {len(saved1)} documents saved.")
        if not docs1:
            print("  [Warning] Call 1 — no markers found. Saving raw output.")
            save_output(str(foundation_dir), "Foundation_Call1_Raw.md", call1_output)

    # Re-read gap-filled versions from disk so Call 2 receives complete content,
    # not the raw pre-gap-fill snapshot that docs1 was parsed from.
    # In the resume path the disk already has the filled versions from the prior run.
    print("\n[Foundation] Reloading gap-filled Call 1 docs from disk for Call 2 context...")
    docs1_filled = _reload_filled_docs(docs1, foundation_dir, fwd_eng_dir)
    print(f"  Reloaded {len(docs1_filled)} gap-filled document(s).")

    # ── Call 2: docs 11–20 (receives KG JSON only, not full Call 1 output) ──────
    if part2_raw.exists() and part2_raw.stat().st_size > 0:
        print("\n[Foundation] Call 2 — already done, loading saved output...")
        call2_output = part2_raw.read_text(encoding="utf-8")
        docs2 = _split_documents(call2_output)
        print(f"  Loaded {len(docs2)} documents from previous run.")
    else:
        # Send gap-filled KG JSON + all gap-filled docs 1-10 to Call 2
        kg_json = docs1_filled.get("ENTERPRISE_KNOWLEDGE_GRAPH.json", "")
        kg_context_parts = []
        if kg_json:
            kg_context_parts.append(f"## Enterprise Knowledge Graph\n\n```json\n{kg_json}\n```")
        # Include all gap-filled docs 1-10 that were produced
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
        if kg_context_parts:
            kg_context = "\n\n---\n\n".join(kg_context_parts)
        else:
            kg_context = call1_output  # full fallback, no truncation

        print("\n[Foundation] Call 2 — docs 11–20...")
        call2_prompt = (
            f"{CALL2_PROMPT}"
            f"{kg_context}\n\n"
            f"Begin Part 2 now."
        )
        call2_output = call_claude(call2_prompt, label="Foundation Call 2 (docs 11-20)", timeout=5400, allow_tools=False)
        save_output(output_dir, "Foundation_Raw_Output_Part2.md", call2_output)
        docs2 = _split_documents(call2_output)
        saved2 = _save_docs(docs2, foundation_dir, fwd_eng_dir, output_dir)
        print(f"  Call 2: {len(saved2)} documents saved.")
        if not docs2:
            print("  [Warning] Call 2 — no markers found. Saving raw output.")
            save_output(str(fwd_eng_dir), "Foundation_Call2_Raw.md", call2_output)

    # ── Call 3: Verification pass — cross-check all 25 docs against agent outputs ──
    part3_raw = Path(output_dir) / "Foundation_Raw_Output_Part3.md"
    if part3_raw.exists() and part3_raw.stat().st_size > 0:
        print("\n[Foundation] Call 3 — already done, loading saved output...")
        call3_output = part3_raw.read_text(encoding="utf-8")
        docs3 = _split_documents_updates(call3_output)
        print(f"  Loaded {len(docs3)} document update(s) from previous run.")
    else:
        print("\n[Foundation] Call 3 — Verification pass (cross-checking 25 docs against agent outputs)...")

        # Build context: all 25 generated docs + original 8 agent outputs (truncated)
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
            f"# All 25 Generated Documents (check these for completeness)\n\n"
            f"{generated_docs_text}\n\n"
            f"# Original 8 Agent Outputs (source of truth)\n\n"
            f"{agent_outputs_text}\n\n"
            f"Begin verification pass now. Only output documents that need changes."
        )

        call3_output = call_claude(call3_prompt, label="Foundation Call 3 (verification)", timeout=5400, allow_tools=False)
        save_output(output_dir, "Foundation_Raw_Output_Part3.md", call3_output)
        docs3 = _split_documents_updates(call3_output)

        # Apply updates to the affected documents on disk
        updated_count = 0
        for filename, updated_content in docs3.items():
            if filename in {"ENTERPRISE_KNOWLEDGE_GRAPH.json", "CANONICAL_ENTERPRISE_MODEL.md",
                            "ARCHITECTURE_INVENTORY.md", "TRACEABILITY_MATRIX.md",
                            "FORWARD_ENGINEERING_INPUT_MAP.md"}:
                path = foundation_dir / filename
            else:
                path = fwd_eng_dir / filename
            if path.exists() and updated_content.strip():
                updated_content = _clean_document(filename, updated_content)
                path.write_text(updated_content, encoding="utf-8")
                updated_count += 1
                print(f"  Updated → {path}")
        print(f"  Call 3: {updated_count} document(s) updated with verified supplements.")

    # ── Call 4: Cross-document consistency check ──────────────────────────────
    part4_raw = Path(output_dir) / "Foundation_Raw_Output_Part4.md"
    if part4_raw.exists() and part4_raw.stat().st_size > 0:
        print("\n[Foundation] Call 4 — already done, loading saved output...")
        call4_output = part4_raw.read_text(encoding="utf-8")
        docs4 = _split_documents_updates(call4_output)
        print(f"  Loaded {len(docs4)} document update(s) from previous run.")
    else:
        print("\n[Foundation] Call 4 — Cross-document consistency check...")

        # Build context: all 25 final docs after Call 3 updates applied
        all_final_docs = {}
        all_final_docs.update(docs1_filled)
        for filename, content in docs2.items():
            all_final_docs[filename] = content
        # Overlay any Call 3 updates
        if 'docs3' in dir():
            for filename, content in docs3.items():
                if content.strip():
                    all_final_docs[filename] = content

        # Re-read from disk to get the latest saved versions
        for filename in list(all_final_docs.keys()):
            if filename in {"ENTERPRISE_KNOWLEDGE_GRAPH.json", "CANONICAL_ENTERPRISE_MODEL.md",
                            "ARCHITECTURE_INVENTORY.md", "TRACEABILITY_MATRIX.md",
                            "FORWARD_ENGINEERING_INPUT_MAP.md"}:
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
            f"# All 25 Final Documents (after verification pass)\n\n"
            f"{final_docs_text}\n\n"
            f"Begin cross-document consistency check now."
        )

        call4_output = call_claude(call4_prompt, label="Foundation Call 4 (consistency check)", timeout=5400, allow_tools=False)
        save_output(output_dir, "Foundation_Raw_Output_Part4.md", call4_output)
        docs4 = _split_documents_updates(call4_output)

        # Save consistency report
        import re as _re
        consistency_match = _re.search(
            r"=== CONSISTENCY_REPORT ===(.*?)(?====\s*UPDATE:|$)",
            call4_output, _re.DOTALL
        )
        if consistency_match:
            report_content = consistency_match.group(1).strip()
            report_path = foundation_dir / "CONSISTENCY_REPORT.md"
            report_path.write_text(
                f"# Cross-Document Consistency Report\n\n{report_content}",
                encoding="utf-8"
            )
            print(f"  Saved consistency report → {report_path}")

        # Apply Call 4 updates to affected documents
        updated4_count = 0
        for filename, updated_content in docs4.items():
            if filename in {"ENTERPRISE_KNOWLEDGE_GRAPH.json", "CANONICAL_ENTERPRISE_MODEL.md",
                            "ARCHITECTURE_INVENTORY.md", "TRACEABILITY_MATRIX.md",
                            "FORWARD_ENGINEERING_INPUT_MAP.md"}:
                path = foundation_dir / filename
            else:
                path = fwd_eng_dir / filename
            if path.exists() and updated_content.strip():
                updated_content = _clean_document(filename, updated_content)
                path.write_text(updated_content, encoding="utf-8")
                updated4_count += 1
                print(f"  Updated → {path}")
        print(f"  Call 4: {updated4_count} document(s) updated after consistency check.")

    total = len(docs1) + len(docs2)
    verified = len(docs3) if 'docs3' in dir() else 0
    consistency = len(docs4) if 'docs4' in dir() else 0
    print(f"\n[Foundation] Complete — {total} documents generated, {verified} updated by verification pass, {consistency} updated by consistency check.")
    print(f"  Foundation_KnowledgeGraph: {foundation_dir}")
    print(f"  ForwardEngineering_Docs:   {fwd_eng_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Foundation Runner — synthesise all layers into Enterprise Knowledge Graph"
    )
    parser.add_argument("--output", required=True,
                        help="Root output directory containing the *_Analysis/ folders")
    args = parser.parse_args()
    run(args.output)
