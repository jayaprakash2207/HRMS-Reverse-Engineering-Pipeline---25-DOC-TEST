# 5. Domain Model

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

## Common Mistakes to Avoid [M]
- Do NOT confuse domain entities with database tables — domain entities are business concepts, not storage structures.
- Do NOT define relationships without cardinality and optionality.
- Do NOT invent domain concepts not evidenced in the source — mark as ASSUMED if inferring.
- Do NOT skip domain invariants — every entity must have at least one invariant or constraint.
- Do NOT use technology-specific terms (no "foreign key", "index", "stored procedure") — use business language.

Do not delete a mandatory section because evidence is missing. Record `UNKNOWN`, `NOT_AVAILABLE`, `NOT_APPLICABLE`, or `CONTRADICTED` with rationale.

### NOT_AVAILABLE Escalation Path
When a section cannot be populated from source evidence, record exactly:
```
Status: NOT_AVAILABLE
Evidence Class: UNKNOWN
Confidence: 0.00
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
| Document Type | `5. Domain Model` |
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

| Evidence Source | Confidence Range |
|---|---|
| Directly observed in DDL / source file (exact match) | 0.90 – 0.95 |
| Observed in procedure body / trigger / form logic | 0.80 – 0.90 |
| Derived deterministically from two or more observed facts | 0.75 – 0.85 |
| Inferred from naming convention, pattern, or context | 0.50 – 0.70 |
| Assumed — no evidence, but standard practice | 0.30 – 0.50 |
| Unknown — insufficient evidence | 0.00 – 0.30 |
| Contradicted — conflicting evidence exists | 0.00 |

Never assign confidence > 0.70 to an INFERRED statement.
Never assign confidence > 0.50 to an ASSUMED statement.
Always assign confidence = 0.00 to UNKNOWN and CONTRADICTED.

## Document Dependencies [M]

### Upstream
| Document | Required Sections | Blocking? |
|---|---|---|
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 7, Section 8 | YES |
| 06_DATA_DICTIONARY | All data elements | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 07_DATA_MODEL_SPECIFICATION | Domain entities | Data model scoping |
| 08_ERD_DOCUMENT | Domain entities and relationships | ERD scoping |
| 22_CANONICAL_ENTERPRISE_MODEL | All domain concepts | Canonical vocabulary |
| 15_FORWARD_ENGINEERING_SPECIFICATION | Section 7 Domain Reconstruction | |
| 24_TRACEABILITY_MATRIX | All DOM-* IDs | Traceability |

## 1. Domain Overview [M]
## 2. Domain Modeling Principles [M]
## 3. Domain Boundaries / Subdomains [M]
## 4. Domain Concept Catalog [M]
> **Cross-reference:** DOM-* IDs defined here are used in 07_DATA_MODEL_SPECIFICATION Section 5 (Entity Specifications) and 22_CANONICAL_ENTERPRISE_MODEL Section 5. Keep DOM-* IDs stable — renaming breaks traceability.

For each `DOM-*`: definition, business meaning, identity, owner, lifecycle, attributes, relationships, rules, evidence.

### Worked Example Row (generic)
| Field | Example Value |
|---|---|
| ID | `DOM-001` |
| Name | {DOMAIN_CONCEPT_NAME} |
| Definition | A {DESCRIPTION} that {DEFINES_ROLE_OR_PURPOSE} within the {SUBDOMAIN} subdomain. |
| Business Meaning | Represents {WHAT_IT_MEANS_TO_THE_BUSINESS}. |
| Identity | Identified by {IDENTIFIER_FIELD}. Unique within {SCOPE}. |
| Owner | `{BUSINESS_UNIT}` |
| Lifecycle States | {STATE_1} → {STATE_2} → {STATE_3} |
| Key Attributes | {ATTR_1}, {ATTR_2}, {ATTR_3} |
| Relationships | Has-many {DOM-002}; belongs-to {DOM-003} |
| Invariants | {ATTR_X} must be > 0 when status = {STATE}. |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {TABLE_OR_CLASS}` |
| Confidence | 0.90 |

> **Section passes QA when:** Every DOM-* has a definition, business meaning, identity key, lifecycle states, at least one relationship, and at least one invariant. Source reference is present.

## 5. Entities [M]
## 6. Value Objects / Conceptual Types [C]
## 7. Aggregates / Consistency Boundaries [C]
## 8. Relationships [M]
> **Cross-reference:** Relationships defined here must align with foreign key relationships in 07_DATA_MODEL_SPECIFICATION Section 8 and diagram relationships in 08_ERD_DOCUMENT Section 6.

Association, composition, dependency, specialization/generalization, cardinality and optionality.

## 9. Domain Invariants [M]
## 10. Domain Rules [M]
## 11. Entity / Object Lifecycle [M]
## 12. Domain Events [C]
## 13. Cross-Domain Relationships [M]
## 14. Domain-to-Process Mapping [M]
## 15. Domain-to-Data Mapping [M]
## 16. Domain-to-Capability Mapping [M]
## 17. Domain-to-Service Mapping [C]
## 18. Open Semantic Questions [M]


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
| Domain concept catalog completeness | 25% | | | |
| Entity and relationship coverage | 20% | | | |
| Domain invariants and rules documented | 15% | | | |
| Lifecycle / temporal concepts covered | 15% | | | |
| Evidence quality | 15% | | | |
| Domain-to-process and data mappings | 10% | | | |
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
