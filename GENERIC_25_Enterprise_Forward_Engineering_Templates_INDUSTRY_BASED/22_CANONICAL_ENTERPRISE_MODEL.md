# 22. Canonical Enterprise Model

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

## Common Mistakes to Avoid [M]
- Do NOT allow two different canonical terms to mean the same thing — enforce uniqueness.
- Do NOT use source/legacy names as canonical names — canonical names must be business-language.
- Do NOT skip the forbidden/ambiguous names column — it prevents future misinterpretation.
- Do NOT create canonical terms without evidence — mark as ASSUMED if the term is inferred.

## Document Control [M]

| Field | Value |
|---|---|
| Document ID | `{DOCUMENT_ID}` |
| Document Type | `22. Canonical Enterprise Model` |
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
| 05_DOMAIN_MODEL | All domain concepts | YES |
| 06_DATA_DICTIONARY | All data elements | YES |
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 8 Business Rules | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 21_ENTERPRISE_KNOWLEDGE_GRAPH | All concepts | Graph node vocabulary |
| 15_FORWARD_ENGINEERING_SPECIFICATION | All sections | Canonical naming in target |
| 24_TRACEABILITY_MATRIX | Canonical term IDs | Vocabulary traceability |

## 1. Purpose [M]
## 2. Canonical Modeling Principles [M]
## 3. Canonical Vocabulary [M]
> **Cross-reference:** Every canonical term defined here becomes the authoritative vocabulary for all 25 documents. If a term used in 01_BRD, 05_DOMAIN_MODEL, or 07_DATA_MODEL_SPECIFICATION conflicts with this vocabulary, the conflict must be recorded in Section 17 (Conflicting Definitions).

For each concept: canonical term, definition, synonyms, source terms, ambiguity, status.

### Worked Example Row (generic)
| Canonical Term | Definition | Synonyms | Source / Legacy Names | Forbidden / Ambiguous Names | Status |
|---|---|---|---|---|---|
| `{CANONICAL_CONCEPT}` | {UNAMBIGUOUS_DEFINITION_ONE_SENTENCE} | {SYNONYM_1}, {SYNONYM_2} | `{LEGACY_TABLE}`, `{LEGACY_FIELD}`, `{OLD_TERM}` | `{AMBIGUOUS_TERM}` (ambiguous — means {X} in {CONTEXT_A} and {Y} in {CONTEXT_B}) | ACTIVE |

> **Section passes QA when:** Every canonical term has a definition, at least one synonym or source name, and at least one forbidden/ambiguous name. No two terms share a definition.

## 4. Business Concepts [M]
## 5. Business Entities / Domain Concepts [M]
## 6. Canonical Data Entities [M]
## 7. Canonical Data Elements [M]
## 8. Value Objects / Conceptual Types [C]
## 9. Reference / Classification Concepts [M]
## 10. Organizational / Actor Concepts [C]
## 11. Transaction / Event Concepts [M]
## 12. Lifecycle / Temporal Concepts [M]
## 13. Relationships [M]
## 14. Business Rules / Constraints [M]
## 15. Canonical Identifiers [M]
## 16. Semantic Mappings [M]
> **Cross-reference:** Source-to-canonical mappings here must cover every table and column name from 07_DATA_MODEL_SPECIFICATION. Canonical-to-target mappings feed into 15_FORWARD_ENGINEERING_SPECIFICATION Section 19 (Naming/Semantic Mapping Rules).

### 16.1 Source-to-Canonical
### 16.2 Canonical-to-Target
### 16.3 Synonyms / Aliases
### 16.4 Deprecated Concepts

## 17. Conflicting Definitions [M]
## 18. Governance / Change Control [M]
## 19. Canonical Model Validation [M]


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
| Canonical vocabulary completeness (all key domain terms defined) | 25% | | | |
| Legacy-to-canonical mapping completeness | 20% | | | |
| Canonical-to-target mapping completeness | 20% | | | |
| Conflicting definitions surfaced and resolved | 15% | | | |
| Evidence quality | 10% | | | |
| Governance and change control defined | 10% | | | |
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
