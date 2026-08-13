# 7. Data Model Specification

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
- Do NOT prescribe a target database technology — document the source schema only.
- Do NOT omit primary keys — every entity must have one.
- Do NOT skip referential integrity rules — every foreign key relationship must be documented.
- Do NOT invent columns not in the source DDL — mark as ASSUMED if inferring from procedure usage.
- Do NOT confuse logical model (business meaning) with physical model (storage) — keep them separate in sections 3 and 4.

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
| Document Type | `7. Data Model Specification` |
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
| 06_DATA_DICTIONARY | All data elements | YES |
| 05_DOMAIN_MODEL | Entities and relationships | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 08_ERD_DOCUMENT | Entity and relationship specs | ERD rendering |
| 09_DFD_DOCUMENT | Data stores | DFD population |
| 11_API_CONTRACT_SPECIFICATION | Entity schemas | API request/response schemas |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Data classification | Security scoping |
| SCHEMA_MIGRATION_SCRIPTS | All entities | Migration planning |
| 24_TRACEABILITY_MATRIX | All entity / attribute IDs | Traceability |

## 1. Scope and Objectives [M]
## 2. Modeling Conventions [M]
## 3. Conceptual Data Model [M]
## 4. Logical Data Model [M]
## 5. Entity Specifications [M]

> **Cross-reference:** Entity names here must match DOM-* concepts in 05_DOMAIN_MODEL. DE-* attribute IDs must match 06_DATA_DICTIONARY. Every table listed here must appear in 08_ERD_DOCUMENT Section 5 (Entity Inventory).

### Worked Example Row (generic)
| Field | Example Value |
|---|---|
| Entity ID | `ENT-001` |
| Name | `{ENTITY_NAME}` |
| Definition | Represents a {DESCRIPTION} in the {SUBDOMAIN} domain. |
| Source Table | `{SOURCE_SCHEMA}.{SOURCE_TABLE}` |
| Primary Key | `{PK_COLUMN}` ({PK_TYPE}) — system-generated / business key |
| Business Key | `{BK_COLUMN}` — unique within {SCOPE} |
| Critical Attributes | `{ATTR_1}` ({TYPE}, NOT NULL), `{ATTR_2}` ({TYPE}, nullable) |
| Foreign Keys | `{FK_COLUMN}` → `{PARENT_TABLE}.{PARENT_PK}` (ON DELETE {ACTION}) |
| Constraints | `{CONSTRAINT_NAME}`: {CONSTRAINT_DEFINITION} |
| Lifecycle States | {STATE_1} → {STATE_2} → {STATE_3} |
| Temporal / History | Effective-dated using {EFF_DATE_COL} / {END_DATE_COL} / audit table `{AUDIT_TABLE}` |
| Row Volume Estimate | {APPROXIMATE_ROW_COUNT} current rows; {GROWTH_RATE} per {PERIOD} |
| Evidence Class | OBSERVED |
| Source Reference | `{DDL_FILE} / CREATE TABLE {TABLE_NAME}` |
| Confidence | 0.95 — HIGH (observed in source DDL) |

### 5.1 Entity Identity and Definition
### 5.2 Purpose and Ownership
### 5.3 Attributes
### 5.4 Relationships
### 5.5 Lifecycle
### 5.6 History / Temporal Requirements
### 5.7 Constraints
### 5.8 Source Evidence

> **Section passes QA when:** Every entity has PK defined, at least one FK relationship documented, lifecycle states listed, and a source DDL reference. Row volume estimate is present.

## 6. Attribute Specifications [M]
## 7. Identifier and Key Specifications [M]
### 7.1 Business Keys
### 7.2 Candidate / Alternate Keys
### 7.3 Primary Identity
### 7.4 Foreign Keys / References

## 8. Relationship Specifications [M]
## 9. Referential Integrity [M]

> **Cross-reference:** Every FK relationship documented here must be reflected in 08_ERD_DOCUMENT Section 6 (Relationship Inventory) and may require an entry in SCHEMA_MIGRATION_SCRIPTS.md if not confirmed by DDL.

> **Section passes QA when:** Every FK relationship has ON DELETE / ON UPDATE behaviour documented. Orphan risk is assessed for every nullable FK.

## 10. Temporal / Effective-Dated Modeling [C]
## 11. Transactional Data Semantics [M]
## 12. Reference Data [M]
## 13. Audit / History Data [C]
## 14. Data Classification and Protection [M]
## 15. Data Quality / Validation [M]
## 16. Migration / Transformation Requirements [C]
## 17. Model-to-Dictionary Mapping [M]
## 18. Model-to-Requirement Mapping [M]


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
| Entity catalog completeness | 20% | | | |
| Attribute specification completeness | 20% | | | |
| Key and referential integrity documentation | 20% | | | |
| Temporal / history modeling documented | 15% | | | |
| Evidence quality | 15% | | | |
| Model-to-dictionary alignment | 10% | | | |
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
