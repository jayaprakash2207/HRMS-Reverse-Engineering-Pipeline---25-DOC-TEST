# 6. Data Dictionary

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
- Do NOT define data elements without a canonical name — every element needs both a source name and a canonical name.
- Do NOT leave sensitivity classification blank — every element must be Public/Internal/Confidential/Restricted.
- Do NOT omit validation rules for fields with known constraints in the source DDL.
- Do NOT invent data types not evidenced in the source schema.
- Do NOT confuse a data element (a field) with an entity (a table) — they belong in different sections.

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
| Document Type | `6. Data Dictionary` |
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
| Source system artifacts (DDL, schema, code) | All | YES |
| 05_DOMAIN_MODEL | Domain entities | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 07_DATA_MODEL_SPECIFICATION | All data elements | Model population |
| 08_ERD_DOCUMENT | Entities and attributes | ERD population |
| 11_API_CONTRACT_SPECIFICATION | Request / response schemas | Schema population |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Section 6 Data Classification | Sensitive data identification |
| 15_FORWARD_ENGINEERING_SPECIFICATION | Section 9 Data Reconstruction | |
| 24_TRACEABILITY_MATRIX | All DE-* IDs | Traceability |

## 1. Data Governance Scope [M]
## 2. Naming, Definition and Metadata Rules [M]
## 3. Data Element Catalog [M]
## 4. Data Element Specification [M]

> **Cross-reference:** DE-* IDs defined here are referenced in 07_DATA_MODEL_SPECIFICATION Section 6 (Attribute Specifications), 11_API_CONTRACT Section 5.7 (Request Schema), and 13_SECURITY_ARCHITECTURE Section 6 (Data Classification). Use the same DE-* IDs everywhere.

### Worked Example Row (generic)
| Field | Example Value |
|---|---|
| ID | `DE-001` |
| Business Name | {BUSINESS_READABLE_NAME} |
| Canonical Name | `{CANONICAL_ENTITY}.{CANONICAL_ATTRIBUTE}` |
| Definition | {PLAIN_ENGLISH_DEFINITION_OF_WHAT_THIS_DATA_MEANS}. |
| Source / Legacy Name | `{SOURCE_TABLE}.{SOURCE_COLUMN}` |
| Data Type | {TYPE} ({LENGTH} / {PRECISION},{SCALE}) |
| Nullable | YES / NO |
| Default | {DEFAULT_VALUE_OR_NONE} |
| Format / Unit | {FORMAT_PATTERN_OR_UNIT} |
| Permitted Values | {VALUE_LIST_OR_RANGE_OR_REFERENCE_SET} |
| Derivation | {FORMULA_OR_NONE} |
| Validation Rules | {VALIDATION_RULE_TEXT} |
| Sensitivity | Public / Internal / Confidential / Restricted |
| Owner | `{DATA_OWNER}` |
| Retention | {RETENTION_PERIOD} per {POLICY_OR_REGULATION} |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {TABLE}.{COLUMN} / line {LINE}` |
| Confidence | 0.95 |

| Field | Example Value — Derived/Calculated Element |
|---|---|
| ID | `DE-002` |
| Business Name | {CALCULATED_FIELD_NAME} |
| Canonical Name | `{ENTITY}.{CALCULATED_ATTRIBUTE}` |
| Definition | {CALCULATED_VALUE} derived from {BASE_FIELD_1} and {BASE_FIELD_2} at {CALCULATION_EVENT}. |
| Source / Legacy Name | `{SOURCE_TABLE}.{SOURCE_COLUMN}` |
| Data Type | {TYPE} ({PRECISION},{SCALE}) |
| Nullable | NO |
| Derivation | {FORMULA}: {BASE_FIELD_1} × {RATE} / {DIVISOR} |
| Sensitivity | Confidential |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {PROCEDURE}.{LINE}` |
| Confidence | 0.92 |

### 4.1 ID / Business Name / Canonical Name
### 4.2 Definition and Business Meaning
### 4.3 Source / Legacy Name
### 4.4 Data Type / Length / Precision / Scale
### 4.5 Requiredness / Nullability
### 4.6 Default / Format / Unit
### 4.7 Permitted Values / Value Domain
### 4.8 Derivation / Calculation
### 4.9 Validation Rules
### 4.10 Sensitivity / Classification
### 4.11 Owner / Steward
### 4.12 Retention
### 4.13 Lineage / Source Evidence
### 4.14 Quality Rules

> **Section passes QA when:** Every DE-* has all 14 sub-fields populated or explicitly marked NOT_AVAILABLE with escalation. Sensitivity classification is present on every element. No element lacks a source reference.

## 5. Data Domains / Subject Areas [M]
## 6. Code Sets and Reference Data [M]
## 7. Derived / Calculated Data [M]
## 8. Sensitive / Restricted Data [C]

> **Cross-reference:** Every field marked Confidential or Restricted here must appear in 13_SECURITY_ARCHITECTURE Section 5 (Assets) and Section 11 (Data Protection). Inconsistency between these two documents is a blocking issue.

## 9. Data Quality Rules [M]
## 10. Data Lineage [M]
## 11. Temporal / Historical Data [M]
## 12. Ownership and Stewardship [M]
## 13. Data Dictionary Validation [M]


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
| Data element catalog completeness (all critical fields documented) | 25% | | | |
| Definition quality (unambiguous, business-readable) | 20% | | | |
| Sensitivity / classification coverage | 15% | | | |
| Validation rules and permitted values | 15% | | | |
| Lineage and source reference completeness | 15% | | | |
| Retention and governance coverage | 10% | | | |
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
