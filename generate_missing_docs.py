"""
Generates the 13 missing ForwardEngineering documents by calling Claude
with the existing analysis outputs as context. No full pipeline re-run needed.

Missing docs:
  02_BUSINESS_CAPABILITY_MODEL.md
  03_USE_CASE_SPECIFICATION.md
  07_DATA_MODEL_SPECIFICATION.md
  08_ERD.md
  11_API_CONTRACT_SPECIFICATION.md
  12_TECHNOLOGY_BLUEPRINT.md
  14_NFR_SPECIFICATION.md
  15_FORWARD_ENGINEERING_SPECIFICATION.md
  16_GENERATION_MANIFEST.json

KG missing:
  CANONICAL_ENTERPRISE_MODEL.md
  ARCHITECTURE_INVENTORY.md
  TRACEABILITY_MATRIX.md
  FORWARD_ENGINEERING_INPUT_MAP.md
"""

import sys
from pathlib import Path

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

ba   = load("Business_Analysis/BA_Deep_Analyst.md")
da   = load("Data_Analysis/DA_Data_Reviewer.md")
ta   = load("Technology_Analysis/TA_Deep_Analyst.md")
aa   = load("Application_Analysis/AA_Quality_Review.md")
kg   = load("Foundation_KnowledgeGraph/ENTERPRISE_KNOWLEDGE_GRAPH.json")
brd  = load("ForwardEngineering_Docs/01_BRD.md") or load("ForwardEngineering_Docs/01_BRD_SUPPLEMENT.md")
dom  = load("ForwardEngineering_Docs/05_DOMAIN_MODEL.md")
dd   = load("ForwardEngineering_Docs/06_DATA_DICTIONARY.md")
da_ext = load("Data_Analysis/DA_Data_Extractor.md")
ta_scout = load("Technology_Analysis/TA_Stack_Scout.md")
cv   = load("cross_validation_report.json")

# Truncate large files to fit context
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
    print(f"  ✓ Saved {filename} ({len(content):,} chars)")
    return content

DIRECT_INSTRUCTION = """
CRITICAL INSTRUCTION: Output ONLY the raw Markdown document content.
- Start immediately with the # heading — do NOT write any introduction, preamble, or explanation
- Do NOT say "Here is the document", "I'll write", "Here's a summary", or anything like that
- Do NOT describe what you wrote after finishing
- Just output the document itself, start to finish, nothing else
- Be comprehensive and detailed — minimum 300 lines of content
"""

def run_doc(fname, prompt, directory=FWDENG, timeout=1200):
    path = directory / fname
    if path.exists() and path.stat().st_size > 5000:
        print(f"  → Skipping {fname} (already exists, {path.stat().st_size:,} bytes)")
        return
    print(f"\n  Generating {fname}...")
    full_prompt = DIRECT_INSTRUCTION + "\n\n" + prompt
    result = call_claude(full_prompt, label=f"Generate {fname}", timeout=timeout)
    # If Claude described instead of writing, detect and retry
    bad_starts = ["the document", "here is", "here's", "i've written", "i'll", "below is", "this document"]
    if any(result.strip().lower().startswith(b) for b in bad_starts) or len(result) < 1000:
        print(f"  ⚠ Claude described instead of writing — retrying with stronger instruction...")
        retry_prompt = f"Write the FULL CONTENT of {fname} right now. Start with # title on line 1. No preamble. No explanation. Just the complete document.\n\n" + prompt
        result = call_claude(retry_prompt, label=f"Generate {fname} (retry)", timeout=timeout)
    save(directory, fname, result)

# ────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("GENERATING MISSING FOUNDATION DOCUMENTS")
print("="*60)

# ── 02 Business Capability Model ────────────────────────────────
run_doc("02_BUSINESS_CAPABILITY_MODEL.md", f"""
You are a business architect. Using the analysis below, write a complete
Business Capability Model document (02_BUSINESS_CAPABILITY_MODEL.md).

Include:
1. Business Capability Map — L1 and L2 capabilities (table format)
2. Capability Heat Map — which capabilities are at risk / need improvement
3. Capability-to-System Mapping — which Oracle HRMS packages support each capability
4. Capability Gaps — capabilities needed for the future system not in the current one
5. Investment Priority — which capabilities to build first in migration

Format: professional Markdown, use tables and headings throughout.

{context_base}
""")

# ── 03 Use Case Specification ────────────────────────────────────
run_doc("03_USE_CASE_SPECIFICATION.md", f"""
You are a business analyst. Using the analysis below, write a complete
Use Case Specification document (03_USE_CASE_SPECIFICATION.md) for an Oracle HRMS system.

Include:
1. Actor Catalogue (all user roles: HR Manager, Employee, Payroll Admin, System Admin)
2. Use Case Summary Table (ID, Name, Actor, Priority, Status)
3. Detailed Use Cases for the top 10 most important flows:
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
   Each use case: preconditions, main flow, alternate flows, postconditions, business rules
4. Use Case Dependency Diagram (text/ASCII)

Format: professional Markdown.

{context_base}
""")

# ── 07 Data Model Specification ──────────────────────────────────
run_doc("07_DATA_MODEL_SPECIFICATION.md", f"""
You are a data architect. Using the analysis below, write a complete
Data Model Specification document (07_DATA_MODEL_SPECIFICATION.md).

Include:
1. Conceptual Data Model — major entities and relationships
2. Logical Data Model — all 30 tables with:
   - Column names, data types, constraints
   - Primary keys, foreign keys
   - Business rules embedded in schema
3. Data Model Decisions — why each key design decision was made
4. Migration Mapping — Oracle column → target system column for each table
5. Data Quality Issues found in current schema
6. Recommended schema improvements for the new system

Format: professional Markdown with tables.

{context_base}

## Data Extractor Output
{trunc(da_ext, 8000)}
""")

# ── 08 ERD ──────────────────────────────────────────────────────
run_doc("08_ERD.md", f"""
You are a data architect. Using the analysis below, write a complete
Entity Relationship Diagram document (08_ERD.md).

Include:
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

Format: professional Markdown with Mermaid code blocks.

{context_base}

## Data Extractor Output
{trunc(da_ext, 8000)}
""")

# ── 11 API Contract Specification ───────────────────────────────
run_doc("11_API_CONTRACT_SPECIFICATION.md", f"""
You are an API architect. Using the analysis below, write a complete
API Contract Specification document (11_API_CONTRACT_SPECIFICATION.md)
for the NEW system that will replace Oracle HRMS.

Include:
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

Format: professional Markdown with tables and JSON examples.

{context_base}

## Technology Stack
{trunc(ta_scout, 5000)}
""")

# ── 12 Technology Blueprint ──────────────────────────────────────
run_doc("12_TECHNOLOGY_BLUEPRINT.md", f"""
You are a solution architect. Using the analysis below, write a complete
Technology Blueprint document (12_TECHNOLOGY_BLUEPRINT.md) for the new system.

Include:
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
5. Build vs Buy decisions
6. Technology Roadmap (phased adoption)
7. Proof of Concept recommendations

Format: professional Markdown with tables.

{context_base}

## TA Stack Scout
{trunc(ta_scout, 8000)}
""")

# ── 14 NFR Specification ─────────────────────────────────────────
run_doc("14_NFR_SPECIFICATION.md", f"""
You are a solution architect. Using the analysis below, write a complete
Non-Functional Requirements Specification (14_NFR_SPECIFICATION.md).

Include:
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
7. NFR Acceptance Criteria — testable metrics for each NFR

Format: professional Markdown with tables and measurable targets.

{context_base}
""")

# ── 15 Forward Engineering Specification ─────────────────────────
run_doc("15_FORWARD_ENGINEERING_SPECIFICATION.md", f"""
You are a solution architect. Using the analysis below, write a complete
Forward Engineering Specification (15_FORWARD_ENGINEERING_SPECIFICATION.md).

This is the master technical specification for building the NEW system
that replaces Oracle HRMS. Include:

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
4. Critical Defects to Fix (derived from contradictions found):
   - HOH tax = $0 bug
   - EMPLOYEE_HISTORY column mismatch (ORA-00904)
   - rehire_employee broken procedure
   - Race condition in generate_emp_number
   - Hardcoded AES key
5. Data Migration Strategy
6. Cutover Plan
7. Rollback Strategy

Format: professional Markdown with tables.

{context_base}

## Cross Validation Findings
{trunc(cv, 5000)}
""")

# ── 16 Generation Manifest ───────────────────────────────────────
run_doc("16_GENERATION_MANIFEST.json", f"""
You are a solution architect. Using the analysis below, produce a
Generation Manifest JSON file (16_GENERATION_MANIFEST.json).

This JSON file tells a code generator what to build. Output ONLY valid JSON,
no markdown, no explanation — just the JSON object.

Structure:
{{
  "manifest_version": "1.0",
  "system_name": "HRMS_MODERNISATION",
  "source_system": "Oracle HRMS PL/SQL",
  "target_stack": {{...}},
  "bounded_contexts": [
    {{
      "id": "BC-01",
      "name": "...",
      "phase": 1,
      "entities": [...],
      "services": [...],
      "apis": [...],
      "migration_complexity": "HIGH|MEDIUM|LOW",
      "critical_fixes": [...]
    }}
  ],
  "data_migrations": [...],
  "critical_defects": [...],
  "validation_gates": [...],
  "artifacts": [...]
}}

Be comprehensive — include all bounded contexts from the domain model,
all entities from the data model, all APIs from the API contract.

{context_base}
""")

# ── KG Supporting docs ───────────────────────────────────────────
print("\n--- Generating Knowledge Graph supporting documents ---")

run_doc("CANONICAL_ENTERPRISE_MODEL.md", f"""
You are an enterprise architect. Using the analysis below, write a complete
Canonical Enterprise Model document.

Include:
1. Enterprise Context — what this system does, who uses it, why it exists
2. Canonical Domain Model — all business domains mapped with their bounded contexts
3. Ubiquitous Language Dictionary — key business terms and their precise definitions
4. Core Business Rules Summary — the 20 most important rules that govern this system
5. Enterprise Integration Map — how this system connects to external systems
6. Current System Strengths (what to preserve in migration)
7. Current System Weaknesses (what to fix in migration)

Format: professional Markdown with tables.

{context_base}
""", directory=KG_DIR)

run_doc("ARCHITECTURE_INVENTORY.md", f"""
You are a solution architect. Using the analysis below, write a complete
Architecture Inventory document.

Include:
1. Component Inventory (full table: component ID, name, type, package, status)
2. Technology Inventory (all tech components: DB, language, framework, tools)
3. Integration Inventory (all external integrations: ADP, SMTP, GL feed, etc.)
4. Defect Inventory (all bugs and critical issues found)
5. Security Finding Inventory
6. Technical Debt Inventory
7. Architecture Patterns in use (and whether to keep or replace in new system)

Format: professional Markdown with tables.

{context_base}
""", directory=KG_DIR)

run_doc("TRACEABILITY_MATRIX.md", f"""
You are a business analyst. Using the analysis below, write a complete
Traceability Matrix document.

Include:
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

Format: professional Markdown with tables.

{context_base}
""", directory=KG_DIR)

run_doc("FORWARD_ENGINEERING_INPUT_MAP.md", f"""
You are a solution architect. Using the analysis below, write a complete
Forward Engineering Input Map document.

This document maps every piece of analysis output to the forward engineering
deliverable it feeds into.

Include:
1. Analysis Output → Deliverable Mapping table
2. Source of Truth declarations (which document is authoritative for each topic)
3. Contradiction Resolution Log (from cross-validation — how each was resolved)
4. Confidence Levels per domain (HIGH/MEDIUM/LOW with reasoning)
5. Assumptions Made (what was inferred vs confirmed from source)
6. Open Questions requiring human review before code generation

Format: professional Markdown with tables.

{context_base}

## Cross Validation Findings
{trunc(cv, 5000)}
""", directory=KG_DIR)

# ── Final summary ────────────────────────────────────────────────
print("\n" + "="*60)
print("COMPLETE — Final document inventory:")
print("\nForwardEngineering_Docs/:")
for f in sorted(FWDENG.iterdir()):
    print(f"  {f.name:55s} {f.stat().st_size:>8,} bytes")
print("\nFoundation_KnowledgeGraph/:")
for f in sorted(KG_DIR.iterdir()):
    print(f"  {f.name:55s} {f.stat().st_size:>8,} bytes")
