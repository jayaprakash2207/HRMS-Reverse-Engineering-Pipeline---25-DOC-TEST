# 12. Technology / Solution Blueprint

**Template class:** Generic enterprise forward-engineering artifact  
**Domain:** `{DOMAIN}` — intentionally domain-neutral  
**Technology stance:** Technology-neutral unless a project explicitly defines target constraints  
**Purpose:** Structured source-evidence → semantic reconstruction → forward-engineering contract

## Document conventions [M]

- `[M]` = mandatory section
- `[C]` = conditionally mandatory when applicable
- `[O]` = optional
- `{...}` = population placeholder
- `OBSERVED` = directly supported by evidence
- `DERIVED` = deterministically derived from evidence
- `INFERRED` = interpretation requiring validation
- `ASSUMED` = explicit assumption
- `UNKNOWN` = insufficient evidence
- `CONTRADICTED` = conflicting evidence

Do not delete a mandatory section because evidence is missing. Record `UNKNOWN`, `NOT_AVAILABLE`, `NOT_APPLICABLE`, or `CONTRADICTED` with rationale.

## Common Mistakes to Avoid [M]
- Do NOT name a specific vendor, framework, cloud provider, or runtime unless the project explicitly defines a target constraint.
- Do NOT prescribe a database product for the target system — that is an architecture decision for the team.
- Do NOT describe the current source system as the target — this document is forward-looking.
- Do NOT skip architecture risks — every significant architecture decision has a risk.
- Do NOT confuse a logical component (what it does) with a deployment unit (where it runs).

### NOT_AVAILABLE Escalation Path
When a section cannot be populated from source evidence, record exactly:
```
Status: NOT_AVAILABLE
Evidence Class: UNKNOWN
Confidence: 0.00 — LOW (unknown, insufficient evidence — see escalation table)
Validation Required: YES
Escalate to: {OWNER} — see escalation table below
```

| Section Type | Escalate To | What to Ask |
|---|---|---|
| Business rules / requirements | Business Analyst | Confirm the rule exists and its exact logic |
| Data schema / DDL / tables | DBA | Provide DDL or confirm table structure |
| Security controls / auth model | CISO / Security Lead | Confirm security design decision |
| Process / workflow / approval | Process Owner / BA | Confirm process steps and actors |
| Architecture / technology choice | Solution Architect | Confirm architecture decision |
| UI / UX / screen layout | UX Lead / Product Owner | Confirm screen design |
| Performance / availability targets | System Owner / Architect | Confirm NFR targets |
| Regulatory / compliance | Legal / Compliance Officer | Confirm regulatory requirement |

## Document Control [M]

| Field | Value |
|---|---|
| Document ID | `{DOCUMENT_ID}` |
| Document Type | `12. Technology / Solution Blueprint` |
| Version | `{VERSION}` |
| Status | `{STATUS}` |
| Project | `{PROJECT}` |
| Domain | `{DOMAIN}` |
| Source System/Product | `{SOURCE_SYSTEM}` |
| Target System/Product | `{TARGET_SYSTEM}` |
| Author/Generator | `{AUTHOR_OR_GENERATOR}` |
| Reviewer | `{REVIEWER}` |
| Approver | `{APPROVER}` |
| Date | `{DATE}` |

## Revision History [M]

| Version | Date | Change | Author | Approval |
|---|---|---|---|---|
| `{VERSION}` | `{DATE}` | `{CHANGE}` | `{AUTHOR}` | `{APPROVAL}` |

## Evidence and Traceability Rules [M]

Every material statement must have:
- stable ID where applicable;
- source reference or explicit evidence classification;
- confidence score where generated/inferred;
- links to related enterprise artifacts.

Every source reference should identify the artifact and stable location where possible:
`artifact_id / object / section / line-range / element-id / record-id`.

### Confidence Calibration Guide
Use this scale consistently across all 25 documents:

| Evidence Source | Confidence Range | Label | Teammate Action |
|---|---|---|---|
| Directly observed in DDL / source file (exact match) | 0.90 – 0.95 | **HIGH** | Trust it — no review needed |
| Observed in procedure body / trigger / form logic | 0.80 – 0.90 | **HIGH** | Trust it — no review needed |
| Derived deterministically from two or more observed facts | 0.75 – 0.85 | **HIGH** | Trust it — no review needed |
| Inferred from naming convention, pattern, or context | 0.50 – 0.70 | **MEDIUM** | Review before using |
| Assumed — no evidence, but standard practice | 0.30 – 0.50 | **LOW** | Must validate — check escalation table |
| Unknown — insufficient evidence | 0.00 – 0.30 | **LOW** | Must validate — check escalation table |
| Contradicted — conflicting evidence exists | 0.00 | **LOW** | Must validate — check escalation table |

**Label thresholds:**
- **HIGH** (0.75–1.00) — Evidence is solid. Safe to use without review.
- **MEDIUM** (0.50–0.74) — Inferred from context. A teammate should verify before using.
- **LOW** (0.00–0.49) — Assumed or unknown. Must be validated with the named stakeholder in the escalation table.

Never assign confidence > 0.70 to an INFERRED statement.
Never assign confidence > 0.50 to an ASSUMED statement.
Always assign confidence = 0.00 to UNKNOWN and CONTRADICTED.

Write confidence scores in this format throughout the document:
`0.90 — HIGH (observed in source DDL)`
`0.65 — MEDIUM (inferred from naming convention, verify before use)`
`0.35 — LOW (assumed, no source evidence — validate with Business Analyst)`
`0.00 — LOW (unknown, insufficient evidence — see escalation table)`

## Document Dependencies [M]

### Upstream
| Document | Required Sections | Blocking? |
|---|---|---|
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 4, Section 11 | YES |
| 14_NFR_SPECIFICATION | All NFR-* | YES |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Security architecture | YES |
| 23_ARCHITECTURE_INVENTORY | Current-state inventory | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 18_DEPLOYMENT_ARCHITECTURE_DOCUMENT | Runtime model | Deployment scoping |
| 19_FRONTEND_ARCHITECTURE_DOCUMENT | Client architecture | Frontend scoping |
| 15_FORWARD_ENGINEERING_SPECIFICATION | All sections | Primary specification input |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Architecture |

## 1. Purpose and Scope [M]
## 2. Architecture Drivers [M]
## 3. Architectural Principles [M]
## 4. Stakeholders and Architecture Concerns [M]
## 5. Target Architecture Overview [M]
## 6. Architecture Context [M]
## 7. Architecture Layers / Domains [M]
### 7.1 Business / Functional
### 7.2 Application / Service
### 7. Data / Information
### 7. Integration
### 7. Technology / Runtime
### 7. Security / Cross-Cutting

> **Section passes QA when:** All 6 layers (Business, Application, Data, Integration, Technology, Security) are described. No vendor or product name appears unless explicitly provided as a project constraint.

## 8. Logical Components / Building Blocks [M]

> **Cross-reference:** Components defined here must appear in 23_ARCHITECTURE_INVENTORY Section 4 (Component Inventory) as ARCH-* entries. Deployment constraints feed into 18_DEPLOYMENT_ARCHITECTURE Section 4.

### Worked Example Row (generic)
| Component | Type | Responsibility | Interfaces | Key Constraints | Evidence Class |
|---|---|---|---|---|---|
| `{COMPONENT_NAME}` | {TYPE: Presentation / Service / Data / Integration / Security} | {WHAT_IT_DOES} | Consumes `{UPSTREAM}`; exposes `{DOWNSTREAM}` | {CONSTRAINTS — technology-neutral, e.g. "must support concurrent sessions ≥ N"} | INFERRED |

## 9. Component Responsibilities [M]
## 10. Interactions and Dependencies [M]
## 11. Information / Data Architecture Summary [M]
## 12. Integration Architecture [M]
## 13. Security Architecture Summary [M]
## 14. Deployment / Runtime Model [M]
## 15. Availability / Resilience [M]
## 16. Scalability / Capacity [M]
## 17. Observability [C]
## 18. Technology Constraints and Selection Criteria [M]

> **Cross-reference:** Constraints defined here become mandatory inputs to 15_FORWARD_ENGINEERING_SPECIFICATION Section 4 (Forward Engineering Principles) and 16_GENERATION_MANIFEST technology_constraints array.

## 19. Architecture Decisions and Rationale [M]

> **Section passes QA when:** Every decision has a rationale, alternatives considered, and consequences. No decision is recorded without evidence of why it was made.

## 20. Alternatives and Trade-offs [M]
## 21. Architecture Risks [M]
## 22. Architecture Views / Viewpoints [M]
## 23. Target-State Traceability [M]

Do not hard-code a vendor, framework, cloud provider, database, language, or runtime unless the project explicitly provides it as a target constraint.


## Assumptions [M]

| ID | Assumption | Reason | Impact | Owner | Resolution |
|---|---|---|---|---|---|
| `ASM-001` | `{{ASSUMPTION}}` | `{{REASON}}` | `{{IMPACT}}` | `{{OWNER}}` | `{{RESOLUTION}}` |

## Contradictions [M]

| ID | Evidence A | Evidence B | Conflict | Resolution | Status |
|---|---|---|---|---|---|
| `CON-001` | `{{A}}` | `{{B}}` | `{{CONFLICT}}` | `{{RESOLUTION}}` | `OPEN/RESOLVED` |

## Open Questions [M]

| ID | Question | Impact | Evidence Needed | Owner | Status |
|---|---|---|---|---|---|
| `Q-001` | `{{QUESTION}}` | `{{IMPACT}}` | `{{EVIDENCE}}` | `{{OWNER}}` | `OPEN/RESOLVED` |

## Readiness Scoring [M]

Score each dimension 0–3 using the rubric below. Minimum passing score to proceed to forward engineering: **21 / 30** with no dimension scoring 0.

| Score | Meaning |
|---|---|
| 3 | Complete — all items present, evidence-backed, validated |
| 2 | Substantial — minor gaps, no blockers |
| 1 | Partial — significant gaps, workaround possible |
| 0 | Absent / blocking — cannot proceed without resolution |

| Dimension | Weight | Score (0–3) | Weighted Score | Notes |
|---|---|---|---|---|
| Architecture layers fully described (all 6 layers) | 20% | | | |
| Logical components and responsibilities | 20% | | | |
| Technology selection criteria defined (no vendor prescribed) | 15% | | | |
| Architecture decisions and rationale | 15% | | | |
| Risks and alternatives documented | 15% | | | |
| NFR and security architecture alignment | 15% | | | |
| **Total** | **100%** | | **/30** | |

## Quality and Validation [M]

- [ ] Mandatory sections are present.
- [ ] IDs are unique and stable.
- [ ] Material claims have evidence or explicit uncertainty classification.
- [ ] No unsupported domain rule has been invented.
- [ ] Cross-document references resolve.
- [ ] Terminology agrees with the canonical model.
- [ ] Contradictions are surfaced rather than silently normalized.
- [ ] Machine-readable portions validate against their schema where applicable.
- [ ] Traceability coverage has been measured.
- [ ] Artifact is `READY / CONDITIONAL / BLOCKED`.

## Traceability Matrix [M]

| Trace ID | Source | Relationship | Target | Evidence | Confidence | Status |
|---|---|---|---|---|---:|---|
| `TR-001` | `{{SOURCE_ID}}` | `{{RELATIONSHIP}}` | `{{TARGET_ID}}` | `{{EVIDENCE}}` | `0.00` | `{{STATUS}}` |

## References / Standards Basis [M]

Use the standards relevant to this artifact and record their versions in the project standards register. Do not claim that this custom template is itself an official standard.
