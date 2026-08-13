# 8. Entity Relationship Diagram (ERD) Document

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
- Do NOT draw relationships without stating cardinality and optionality for BOTH ends.
- Do NOT omit associative entities — many-to-many relationships must be resolved.
- Do NOT invent entities not in 07_DATA_MODEL_SPECIFICATION.
- Do NOT use implementation-specific notation without defining it in Section 2 (Modeling Conventions).

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
| Document Type | `8. Entity Relationship Diagram (ERD) Document` |
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
| 07_DATA_MODEL_SPECIFICATION | All entities and relationships | YES |
| 06_DATA_DICTIONARY | All data elements | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 09_DFD_DOCUMENT | Data stores | DFD data stores |
| 11_API_CONTRACT_SPECIFICATION | Entity schemas | Schema definitions |
| 15_FORWARD_ENGINEERING_SPECIFICATION | Section 9 Data Reconstruction | |
| SCHEMA_MIGRATION_SCRIPTS | All DDL constructs | Migration planning |
| 24_TRACEABILITY_MATRIX | Entity and relationship IDs | Traceability |

## 1. Purpose and Scope [M]
## 2. ERD Modeling Conventions [M]
## 3. Enterprise-Level ERD [M]
## 4. Subject-Area ERDs [M]
Create one per meaningful data subject area.

## 5. Entity Inventory [M]

> **Cross-reference:** Every entity here must have a corresponding ENT-* entry in 07_DATA_MODEL_SPECIFICATION Section 5. No new entities may be introduced in the ERD that do not exist in the data model.

### Worked Example Row (generic)
| Entity | PK | Key Relationships | Cardinality | Notes |
|---|---|---|---|---|
| `{ENTITY_A}` | `{PK_A}` | Has-many `{ENTITY_B}` via `{FK_COLUMN}` | 1:N (mandatory) | Source table: `{TABLE_NAME}` |
| `{ENTITY_B}` | `{PK_B}` | Belongs-to `{ENTITY_A}`; has-many `{ENTITY_C}` | N:1 / 1:N | Associative entity bridging {A} and {C} |
| `{ENTITY_C}` | `{PK_C}` | Belongs-to `{ENTITY_B}` | N:1 (optional) | Nullable FK — orphan records possible; validate during migration |

## 6. Relationship Inventory [M]

> **Cross-reference:** Every relationship here must align with FK definitions in 07_DATA_MODEL_SPECIFICATION Section 8 and domain relationships in 05_DOMAIN_MODEL Section 8.

> **Section passes QA when:** Every relationship has source entity, target entity, cardinality (e.g. 1:N), optionality (mandatory/optional) for both ends, and the FK column name.

## 7. Key and Identifier Rules [M]
## 8. Cardinality and Optionality [M]
## 9. Associative Entities [C]
## 10. Recursive Relationships [C]
## 11. Specialization / Generalization [C]
## 12. Referential Integrity [M]
## 13. Temporal Relationships [C]
## 14. ERD Validation [M]
## 15. ERD-to-Data-Model Mapping [M]
## 16. ERD-to-Data-Dictionary Mapping [M]


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
| Entity coverage (all significant entities diagrammed) | 25% | | | |
| Relationship accuracy (cardinality and optionality correct) | 25% | | | |
| Key and identifier documentation | 20% | | | |
| Subject-area ERDs (domain partitioning) | 15% | | | |
| Evidence quality | 15% | | | |
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
