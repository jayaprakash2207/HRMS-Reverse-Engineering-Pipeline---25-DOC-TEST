"""
Generates all missing + thin ForwardEngineering documents and KnowledgeGraph
supporting docs by calling Claude with existing analysis outputs as context.

Missing (never generated):
  02_BUSINESS_CAPABILITY_MODEL.md
  03_USE_CASE_SPECIFICATION.md
  07_DATA_MODEL_SPECIFICATION.md
  08_ERD.md
  11_API_CONTRACT_SPECIFICATION.md
  12_TECHNOLOGY_BLUEPRINT.md
  14_NFR_SPECIFICATION.md
  15_FORWARD_ENGINEERING_SPECIFICATION.md
  16_GENERATION_MANIFEST.json

Thin (exist but < 150 lines — regenerate):
  01_BRD.md                            (98 lines)
  09_DATA_FLOW_DIAGRAM.md              (89 lines)
  17_FORWARD_ENGINEERING_READINESS_REPORT.md  (117 lines)

KG missing:
  CANONICAL_ENTERPRISE_MODEL.md
  ARCHITECTURE_INVENTORY.md
  TRACEABILITY_MATRIX.md
  FORWARD_ENGINEERING_INPUT_MAP.md

Runs all docs in parallel using ThreadPoolExecutor(max_workers=5).
"""

import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Always resolve relative to this script — works from any working directory
BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR / "pipeline"))
from base_runner import call_claude

RESULTS = BASE_DIR / "results"
FWDENG  = RESULTS / "ForwardEngineering_Docs"
KG_DIR  = RESULTS / "Foundation_KnowledgeGraph"
FWDENG.mkdir(exist_ok=True)
KG_DIR.mkdir(exist_ok=True)

# ── Load all existing analysis context ──────────────────────────────────────
def load(rel_path):
    p = RESULTS / rel_path
    return p.read_text(encoding="utf-8") if p.exists() else ""

ba       = load("Business_Analysis/BA_Deep_Analyst.md")
da       = load("Data_Analysis/DA_Data_Reviewer.md")
ta       = load("Technology_Analysis/TA_Deep_Analyst.md")
aa       = load("Application_Analysis/AA_Quality_Review.md")
kg       = load("Foundation_KnowledgeGraph/ENTERPRISE_KNOWLEDGE_GRAPH.json")
brd      = load("ForwardEngineering_Docs/01_BRD.md") or load("ForwardEngineering_Docs/01_BRD_SUPPLEMENT.md")
dom      = load("ForwardEngineering_Docs/05_DOMAIN_MODEL.md")
dd       = load("ForwardEngineering_Docs/06_DATA_DICTIONARY.md")
da_ext   = load("Data_Analysis/DA_Data_Extractor.md")
ta_scout = load("Technology_Analysis/TA_Stack_Scout.md")
cv       = load("cross_validation_report.json")

def trunc(text, chars=15000):
    return text[:chars] if len(text) > chars else text

context_base = f"""
## Business Analysis (BA_Deep_Analyst)
{trunc(ba)}

## Data Analysis (DA_Data_Reviewer)
{trunc(da)}

## Technology Analysis (TA_Deep_Analyst)
{trunc(ta, 12000)}

## Application Analysis (AA_Quality_Review)
{trunc(aa)}

## Data Dictionary (06_DATA_DICTIONARY)
{trunc(dd, 8000)}

## Domain Model (05_DOMAIN_MODEL)
{trunc(dom, 5000)}
"""

def save(directory, filename, content):
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    size = path.stat().st_size
    lines = content.count("\n")
    print(f"  ✓ Saved {filename} ({lines} lines, {size:,} bytes)")
    return content

DIRECT_INSTRUCTION = """
CRITICAL INSTRUCTION: Output ONLY the raw Markdown document content.
- Start immediately with the # heading — do NOT write any introduction, preamble, or explanation
- Do NOT say "Here is the document", "I'll write", "Here's a summary", or anything like that
- Do NOT describe what you wrote after finishing
- Just output the document itself, start to finish, nothing else
- Be comprehensive and detailed — minimum 400 lines of content
"""

DIRECT_INSTRUCTION_JSON = """
CRITICAL INSTRUCTION: Output ONLY valid raw JSON. No markdown fences, no explanation, no preamble.
Start with { on line 1. End with } on the last line. Nothing else.
"""

def run_doc(fname, prompt, directory=FWDENG, timeout=1200, force=False, is_json=False):
    path = directory / fname
    if not force and path.exists() and path.stat().st_size > 5000:
        print(f"  → Skipping {fname} (already exists, {path.stat().st_size:,} bytes)")
        return fname, "skipped"

    print(f"  ⟳ Generating {fname}...")
    instruction = DIRECT_INSTRUCTION_JSON if is_json else DIRECT_INSTRUCTION
    full_prompt = instruction + "\n\n" + prompt
    result = call_claude(full_prompt, label=f"Generate {fname}", timeout=timeout)

    # Detect "describes instead of writes" and retry
    bad_starts = ["the document", "here is", "here's", "i've written", "i'll", "below is", "this document", "i have"]
    if any(result.strip().lower().startswith(b) for b in bad_starts) or len(result) < 1000:
        print(f"  ⚠ {fname}: Claude described instead of writing — retrying...")
        retry_prompt = (
            f"Write the FULL CONTENT of {fname} right now. "
            f"Start with # title on line 1. No preamble. No explanation. "
            f"Just the complete document, minimum 400 lines.\n\n" + prompt
        )
        result = call_claude(retry_prompt, label=f"Generate {fname} (retry)", timeout=timeout)

    save(directory, fname, result)
    return fname, "generated"

# ── Build task list ──────────────────────────────────────────────────────────

TASKS = []

# ── 01 BRD (thin — regenerate) ───────────────────────────────────────────────
TASKS.append(("01_BRD.md", f"""
You are a business analyst. Using the analysis below, write a COMPLETE and DETAILED
Business Requirements Document (01_BRD.md) for the Oracle HRMS system modernisation.

Include ALL of the following sections (minimum 400 lines total):
1. Executive Summary
2. Project Background & Business Case
3. Business Objectives (SMART goals)
4. Scope — In Scope & Out of Scope
5. Stakeholders & User Personas
6. Business Requirements (BR-001 to BR-040 minimum — full list with priority, source, acceptance criteria)
7. Business Constraints
8. Business Assumptions & Dependencies
9. Success Metrics & KPIs
10. Risk Register (top 10 business risks)
11. Sign-off Requirements

Format: professional Markdown with tables throughout.

{context_base}
""", FWDENG, 1200, True, False))

# ── 02 Business Capability Model ────────────────────────────────────────────
TASKS.append(("02_BUSINESS_CAPABILITY_MODEL.md", f"""
You are a business architect. Using the analysis below, write a complete
Business Capability Model document (02_BUSINESS_CAPABILITY_MODEL.md).

Include (minimum 400 lines):
1. Business Capability Map — L1 and L2 capabilities (table format)
2. Capability Heat Map — which capabilities are at risk / need improvement
3. Capability-to-System Mapping — which Oracle HRMS packages support each capability
4. Capability Gaps — capabilities needed for the future system not in the current one
5. Investment Priority — which capabilities to build first in migration
6. Capability Maturity Assessment (Current vs Target)

Format: professional Markdown, use tables and headings throughout.

{context_base}
""", FWDENG, 1200, False, False))

# ── 03 Use Case Specification ────────────────────────────────────────────────
TASKS.append(("03_USE_CASE_SPECIFICATION.md", f"""
You are a business analyst. Using the analysis below, write a complete
Use Case Specification document (03_USE_CASE_SPECIFICATION.md) for Oracle HRMS.

Include (minimum 400 lines):
1. Actor Catalogue (all user roles: HR Manager, Employee, Payroll Admin, System Admin)
2. Use Case Summary Table (ID, Name, Actor, Priority, Status)
3. Detailed Use Cases for the top 15 most important flows:
   - UC-001: Hire Employee
   - UC-002: Process Monthly Payroll
   - UC-003: Submit Leave Request
   - UC-004: Approve Leave Request
   - UC-005: Terminate Employee
   - UC-006: Conduct Performance Review
   - UC-007: Update Salary
   - UC-008: Authenticate User
   - UC-009: Generate Reports
   - UC-010: Manage Benefits Enrollment
   - UC-011: Rehire Employee
   - UC-012: Process Deductions
   - UC-013: Manage Job Positions
   - UC-014: Run Payroll Audit
   - UC-015: Manage Leave Types
   Each use case: preconditions, main flow, alternate flows, postconditions, business rules
4. Use Case Dependency Diagram (text/ASCII)

Format: professional Markdown.

{context_base}
""", FWDENG, 1200, False, False))

# ── 07 Data Model Specification ──────────────────────────────────────────────
TASKS.append(("07_DATA_MODEL_SPECIFICATION.md", f"""
You are a data architect. Using the analysis below, write a complete
Data Model Specification document (07_DATA_MODEL_SPECIFICATION.md).

Include (minimum 400 lines):
1. Conceptual Data Model — major entities and relationships
2. Logical Data Model — all 30 tables with:
   - Column names, data types, constraints
   - Primary keys, foreign keys
   - Business rules embedded in schema
3. Data Model Decisions — why each key design decision was made
4. Migration Mapping — Oracle column → target system column for each table
5. Data Quality Issues found in current schema
6. Recommended schema improvements for the new system
7. Data Lifecycle Management (retention, archival, purge)

Format: professional Markdown with tables.

{context_base}

## Data Extractor Output
{trunc(da_ext, 8000)}
""", FWDENG, 1200, False, False))

# ── 08 ERD ──────────────────────────────────────────────────────────────────
TASKS.append(("08_ERD.md", f"""
You are a data architect. Using the analysis below, write a complete
Entity Relationship Diagram document (08_ERD.md).

Include (minimum 400 lines):
1. Full ERD in Mermaid erDiagram format — ALL 30 tables with their relationships
2. ERD narrative — explain each entity and its key relationships
3. Core Entity Cluster diagrams (separate Mermaid diagrams for):
   - Employee core cluster (EMPLOYEES, DEPARTMENTS, JOB_POSITIONS, JOB_GRADES)
   - Payroll cluster (PAYROLL_RUNS, PAYROLL_DETAILS, DEDUCTION_RECORDS, SALARY_RECORDS)
   - Leave cluster (LEAVE_TYPES, LEAVE_BALANCES, LEAVE_REQUESTS)
   - Performance cluster (PERFORMANCE_REVIEWS, REVIEW_CYCLES, PERFORMANCE_GOALS)
   - Security cluster (USER_CREDENTIALS, AUDIT_LOG, SYSTEM_CONFIG)
4. Relationship cardinalities explained
5. Referential integrity gaps found
6. Recommended new tables for the modernised system

Format: professional Markdown with Mermaid code blocks.

{context_base}

## Data Extractor Output
{trunc(da_ext, 8000)}
""", FWDENG, 1200, False, False))

# ── 09 Data Flow Diagram (thin — regenerate) ────────────────────────────────
TASKS.append(("09_DATA_FLOW_DIAGRAM.md", f"""
You are a solution architect. Using the analysis below, write a COMPLETE and DETAILED
Data Flow Diagram document (09_DATA_FLOW_DIAGRAM.md) for Oracle HRMS.

Include (minimum 400 lines):
1. Context Diagram (Level 0 DFD) — system boundary and external entities
2. Level 1 DFD — all major processes and data stores
3. Level 2 DFDs for each major subsystem:
   - Employee Management data flows
   - Payroll Processing data flows (full cycle from input to disbursement)
   - Leave Management data flows
   - Performance Management data flows
   - Security & Audit data flows
4. Data Store Catalogue (all tables, their producers and consumers)
5. External Data Flows (ADP integration, GL feed, SMTP, NACHA)
6. Data Transformation Points (where data is calculated/derived)
7. PII Data Flow Map (which PII flows where — for GDPR compliance)

Format: professional Markdown with ASCII/text diagrams and tables.

{context_base}
""", FWDENG, 1200, True, False))

# ── 11 API Contract Specification ───────────────────────────────────────────
TASKS.append(("11_API_CONTRACT_SPECIFICATION.md", f"""
You are an API architect. Using the analysis below, write a complete
API Contract Specification document (11_API_CONTRACT_SPECIFICATION.md)
for the NEW system that will replace Oracle HRMS.

Include (minimum 400 lines):
1. API Design Principles (REST, versioning strategy, auth approach)
2. API Groups summary table
3. Full API Contracts for all major endpoints — grouped by domain:
   - Employee Management APIs (CRUD + hire/terminate/rehire)
   - Payroll APIs (run payroll, approve, get payslip, YTD earnings)
   - Leave Management APIs (submit, approve, reject, balance)
   - Performance APIs (create review, submit goals, calibrate)
   - Security APIs (login, logout, change password, session)
   - Reporting APIs (headcount, compensation, leave utilization)
   Each endpoint: HTTP method, path, request body, response body, error codes, business rules
4. Authentication & Authorization spec (JWT structure, role-based access)
5. Error Response Standard
6. Rate Limiting Policy
7. Pagination & Filtering standards
8. Webhook events for async notifications

Format: professional Markdown with tables and JSON examples.

{context_base}

## Technology Stack
{trunc(ta_scout, 5000)}
""", FWDENG, 1200, False, False))

# ── 12 Technology Blueprint ──────────────────────────────────────────────────
TASKS.append(("12_TECHNOLOGY_BLUEPRINT.md", f"""
You are a solution architect. Using the analysis below, write a complete
Technology Blueprint document (12_TECHNOLOGY_BLUEPRINT.md) for the new system.

Include (minimum 400 lines):
1. Current vs Target Technology Stack (comparison table)
2. Recommended Technology Stack:
   - Backend: language, framework, why chosen
   - Database: PostgreSQL migration from Oracle, ORM
   - Frontend: framework choice, why Oracle Forms replacement
   - Infrastructure: Kubernetes, cloud provider recommendation
   - CI/CD: pipeline tools, stages
   - Monitoring: observability stack
3. Architecture Patterns to adopt (replacing Oracle HRMS patterns)
4. Technology Risks and Mitigations
5. Build vs Buy decisions for each component
6. Technology Roadmap (phased adoption)
7. Proof of Concept recommendations
8. Vendor Evaluation Matrix

Format: professional Markdown with tables.

{context_base}

## TA Stack Scout
{trunc(ta_scout, 8000)}
""", FWDENG, 1200, False, False))

# ── 14 NFR Specification ─────────────────────────────────────────────────────
TASKS.append(("14_NFR_SPECIFICATION.md", f"""
You are a solution architect. Using the analysis below, write a complete
Non-Functional Requirements Specification (14_NFR_SPECIFICATION.md).

Include (minimum 400 lines):
1. Performance Requirements
   - Response time SLAs per endpoint type
   - Throughput requirements (concurrent users, batch sizes)
   - Payroll processing time target (vs current Oracle HRMS baseline)
2. Availability & Reliability
   - Uptime SLA (99.9% target)
   - RTO / RPO targets
   - Disaster recovery requirements
3. Scalability Requirements
   - Employee count scaling targets
   - Horizontal scaling strategy
4. Security Requirements
   - Authentication standards
   - Encryption at rest and in transit
   - Audit logging requirements
   - PII data handling (derived from PII inventory in DA)
5. Compliance Requirements
   - GDPR / data privacy
   - SOX compliance for payroll
   - Audit trail requirements
6. Maintainability Requirements
   - Code coverage targets
   - Deployment frequency targets
   - Mean time to recover
7. Usability Requirements
8. Interoperability Requirements
9. NFR Acceptance Criteria — testable metrics for each NFR

Format: professional Markdown with tables and measurable targets.

{context_base}
""", FWDENG, 1200, False, False))

# ── 15 Forward Engineering Specification ─────────────────────────────────────
TASKS.append(("15_FORWARD_ENGINEERING_SPECIFICATION.md", f"""
You are a solution architect. Using the analysis below, write a complete
Forward Engineering Specification (15_FORWARD_ENGINEERING_SPECIFICATION.md).

This is the master technical specification for building the NEW system
that replaces Oracle HRMS. Include (minimum 400 lines):

1. Forward Engineering Strategy (Strangler Fig pattern)
2. Migration Phases:
   Phase 1 (Months 1-3): Foundation — Auth, Employee CRUD, Departments
   Phase 2 (Months 4-6): Core HR — Leave, Performance, Notifications
   Phase 3 (Months 7-10): Payroll — Payroll engine, Tax, Direct deposit
   Phase 4 (Months 11-12): Integration, Reporting, Cutover
3. For each phase:
   - Bounded contexts in scope
   - Critical defects to fix (from cross-validation report)
   - Technical implementation details
   - Acceptance criteria
4. Critical Defects to Fix:
   - HOH tax = $0 bug
   - EMPLOYEE_HISTORY column mismatch (ORA-00904)
   - rehire_employee broken procedure
   - Race condition in generate_emp_number
   - Hardcoded AES key
5. Data Migration Strategy
6. Cutover Plan
7. Rollback Strategy
8. Team Structure & Sprint Plan

Format: professional Markdown with tables.

{context_base}

## Cross Validation Findings
{trunc(cv, 5000)}
""", FWDENG, 1200, False, False))

# ── 16 Generation Manifest ───────────────────────────────────────────────────
TASKS.append(("16_GENERATION_MANIFEST.json", f"""
You are a solution architect. Produce a Generation Manifest JSON file.

Output ONLY valid raw JSON — no markdown fences, no explanation, no preamble.
Start with {{ on line 1. End with }} on the last line. Nothing else.

Structure:
{{
  "manifest_version": "1.0",
  "system_name": "HRMS_MODERNISATION",
  "source_system": "Oracle HRMS PL/SQL",
  "target_stack": {{
    "backend": "...",
    "database": "...",
    "frontend": "...",
    "infrastructure": "..."
  }},
  "bounded_contexts": [
    {{
      "id": "BC-01",
      "name": "...",
      "phase": 1,
      "entities": [...],
      "services": [...],
      "apis": [...],
      "migration_complexity": "HIGH",
      "critical_fixes": [...]
    }}
  ],
  "data_migrations": [...],
  "critical_defects": [...],
  "validation_gates": [...],
  "artifacts": [...]
}}

Be comprehensive — include ALL bounded contexts, entities, APIs, and critical defects
found in the analysis below.

{context_base}
""", FWDENG, 1200, False, True))

# ── 17 Readiness Report (thin — regenerate) ──────────────────────────────────
TASKS.append(("17_FORWARD_ENGINEERING_READINESS_REPORT.md", f"""
You are a solution architect. Using the analysis below, write a COMPLETE and DETAILED
Forward Engineering Readiness Report (17_FORWARD_ENGINEERING_READINESS_REPORT.md).

Include (minimum 400 lines):
1. Executive Readiness Summary
2. Readiness Scorecard (domain-by-domain: Business, Data, Technology, Application)
3. Analysis Completeness Assessment — what was found vs what gaps remain
4. Critical Blockers before code generation can start
5. Recommended Pre-generation Actions (ordered by priority)
6. Confidence Levels per domain (HIGH/MEDIUM/LOW with evidence)
7. Assumptions Requiring Validation
8. Open Questions for Business Stakeholders
9. Open Questions for Technical Stakeholders
10. Risk Assessment for forward engineering
11. Recommended Pilot / POC scope
12. Go / No-Go Recommendation with conditions

Format: professional Markdown with tables and scoring.

{context_base}

## Cross Validation Findings
{trunc(cv, 5000)}
""", FWDENG, 1200, True, False))

# ── KG: Canonical Enterprise Model ──────────────────────────────────────────
TASKS.append(("CANONICAL_ENTERPRISE_MODEL.md", f"""
You are an enterprise architect. Using the analysis below, write a complete
Canonical Enterprise Model document.

Include (minimum 400 lines):
1. Enterprise Context — what this system does, who uses it, why it exists
2. Canonical Domain Model — all business domains mapped with their bounded contexts
3. Ubiquitous Language Dictionary — key business terms and their precise definitions (min 40 terms)
4. Core Business Rules Summary — the 30 most important rules that govern this system
5. Enterprise Integration Map — how this system connects to external systems
6. Current System Strengths (what to preserve in migration)
7. Current System Weaknesses (what to fix in migration)
8. Domain Events Catalogue

Format: professional Markdown with tables.

{context_base}
""", KG_DIR, 1200, False, False))

# ── KG: Architecture Inventory ───────────────────────────────────────────────
TASKS.append(("ARCHITECTURE_INVENTORY.md", f"""
You are a solution architect. Using the analysis below, write a complete
Architecture Inventory document.

Include (minimum 400 lines):
1. Component Inventory (full table: component ID, name, type, package, status)
2. Technology Inventory (all tech components: DB, language, framework, tools)
3. Integration Inventory (all external integrations: ADP, SMTP, GL feed, NACHA)
4. Defect Inventory (all bugs and critical issues found — full details)
5. Security Finding Inventory
6. Technical Debt Inventory (categorized by severity)
7. Architecture Patterns in use (and whether to keep or replace in new system)
8. Component Dependency Map

Format: professional Markdown with tables.

{context_base}
""", KG_DIR, 1200, False, False))

# ── KG: Traceability Matrix ──────────────────────────────────────────────────
TASKS.append(("TRACEABILITY_MATRIX.md", f"""
You are a business analyst. Using the analysis below, write a complete
Traceability Matrix document.

Include (minimum 400 lines):
1. Business Requirement → Source Code Traceability
   (which PL/SQL package/procedure implements which business requirement)
2. Business Rule → Database Constraint Traceability
   (which schema constraints enforce which business rules)
3. Use Case → API Endpoint Traceability
   (which API endpoints implement which use cases)
4. Oracle HRMS Component → New System Component Mapping
   (strangler fig replacement map)
5. Data Table → Bounded Context Traceability
   (which bounded context owns which table)
6. Gap → Remediation Traceability
   (which gaps found → which new system feature addresses them)

Format: professional Markdown with tables.

{context_base}
""", KG_DIR, 1200, False, False))

# ── KG: Forward Engineering Input Map ───────────────────────────────────────
TASKS.append(("FORWARD_ENGINEERING_INPUT_MAP.md", f"""
You are a solution architect. Using the analysis below, write a complete
Forward Engineering Input Map document.

Include (minimum 400 lines):
1. Analysis Output → Deliverable Mapping table
   (every analysis output file → which forward engineering doc it feeds)
2. Source of Truth declarations (which document is authoritative for each topic)
3. Contradiction Resolution Log (how each contradiction was resolved)
4. Confidence Levels per domain (HIGH/MEDIUM/LOW with detailed reasoning)
5. Assumptions Made (what was inferred vs confirmed from source code)
6. Open Questions requiring human review before code generation
7. Data Quality Assessment (how trustworthy is each analysis input)
8. Recommended Enrichment Actions (what to gather to increase confidence)

Format: professional Markdown with tables.

{context_base}

## Cross Validation Findings
{trunc(cv, 5000)}
""", KG_DIR, 1200, False, False))

# ── Parallel runner ──────────────────────────────────────────────────────────

print("\n" + "="*60)
print("GENERATING ALL MISSING + THIN DOCUMENTS (parallel, 5 workers)")
print(f"Total tasks: {len(TASKS)}")
print("="*60)

results_summary = []

with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_name = {}
    for task in TASKS:
        fname = task[0]
        future = executor.submit(run_doc, *task)
        future_to_name[future] = fname

    for future in as_completed(future_to_name):
        fname = future_to_name[future]
        try:
            name, status = future.result()
            results_summary.append((name, status))
        except Exception as e:
            print(f"  ✗ ERROR generating {fname}: {e}")
            results_summary.append((fname, f"ERROR: {e}"))

# ── Final summary ────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("COMPLETE — Final document inventory:")

print("\nForwardEngineering_Docs/:")
for f in sorted(FWDENG.iterdir()):
    size = f.stat().st_size
    lines = f.read_text(encoding="utf-8").count("\n")
    flag = "✅" if size > 10000 else ("⚠️ thin" if size > 3000 else "❌ empty")
    print(f"  {flag}  {f.name:60s} {lines:4d} lines  {size:>8,} bytes")

print("\nFoundation_KnowledgeGraph/:")
for f in sorted(KG_DIR.iterdir()):
    size = f.stat().st_size
    lines = f.read_text(encoding="utf-8").count("\n")
    flag = "✅" if size > 10000 else ("⚠️ thin" if size > 3000 else "❌ empty")
    print(f"  {flag}  {f.name:60s} {lines:4d} lines  {size:>8,} bytes")

print("\nGeneration results:")
for name, status in sorted(results_summary):
    print(f"  {name}: {status}")
