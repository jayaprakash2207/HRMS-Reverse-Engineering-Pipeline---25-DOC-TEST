# 15. Forward Engineering Specification

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
- Do NOT prescribe a target technology stack — this document describes WHAT to build, not HOW to build it.
- Do NOT map a source construct to a target without a transformation rationale.
- Do NOT omit excluded/retired legacy behavior — what is NOT carried forward is as important as what is.
- Do NOT skip behavioral equivalence requirements — the target must reproduce source behavior unless explicitly changed.

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
| Document Type | `15. Forward Engineering Specification` |
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

### Upstream — ALL of the following must exist
| Document | Required Sections | Blocking? |
|---|---|---|
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | All sections | YES |
| 02_BUSINESS_CAPABILITY_MODEL | All sections | YES |
| 03_USE_CASE_SPECIFICATION | All sections | YES |
| 04_BUSINESS_PROCESS_MODEL | All sections | YES |
| 05_DOMAIN_MODEL | All sections | YES |
| 06_DATA_DICTIONARY | All sections | YES |
| 07_DATA_MODEL_SPECIFICATION | All sections | YES |
| 10_SERVICE_CATALOG | All sections | YES |
| 11_API_CONTRACT_SPECIFICATION | All sections | YES |
| 12_TECHNOLOGY_BLUEPRINT | All sections | YES |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | All sections | YES |
| 14_NFR_SPECIFICATION | All sections | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 16_GENERATION_MANIFEST | All sections | Generation unit definition |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness assessment |

## 1. Purpose [M]
## 2. Source System / Product Understanding [M]
## 3. Target System / Product Scope [M]
## 4. Forward Engineering Principles [M]
## 5. Functional Reconstruction [M]
## 6. Business / Operational Reconstruction [M]
## 7. Domain Reconstruction [M]
## 8. Process Reconstruction [M]
## 9. Data Reconstruction [M]
## 10. Interface / Service Reconstruction [M]
## 11. Security Reconstruction [M]
## 12. User Experience Reconstruction [C]
## 13. Quality / NFR Reconstruction [M]
## 14. Source-to-Target Mapping [M]

> **Cross-reference:** Every source construct mapped here must exist in either 07_DATA_MODEL_SPECIFICATION (tables), 10_SERVICE_CATALOG (procedures/services), or 19_FRONTEND_ARCHITECTURE (forms/screens). Target artifacts must be consistent with 12_TECHNOLOGY_BLUEPRINT components.

### Worked Example Row — Source-to-Target Mapping (generic)
| Source Construct | Type | Semantic Interpretation | Target Artifact | Transformation Rule | Rationale | Evidence Class |
|---|---|---|---|---|---|---|
| `{SOURCE_TABLE}` | Relational table | Persists {DOMAIN_CONCEPT} lifecycle records | `{TARGET_ENTITY}` in target data model | Structural mapping; {COLUMN} renamed to {TARGET_FIELD}; {COLUMN2} split into {FIELD_A} and {FIELD_B} | Align with canonical model `DOM-001` | OBSERVED |
| `{PACKAGE}.{PROCEDURE}` | Business logic unit | Implements `BRL-003` calculation | `SVC-001 {SERVICE_NAME}` | Extract calculation into service; remove direct DB coupling | Separation of concerns; testability | OBSERVED |
| `{FORM_MODULE}` | UI module | Supports `UC-001 {USE_CASE}` | `{TARGET_VIEW_NAME}` in frontend architecture | Functional equivalence; modernised interaction model | Direct form-to-screen correspondence | OBSERVED |

> **Section passes QA when:** Every significant source construct (table, procedure, form) has a row in the mapping table. Every row has source construct, semantic interpretation, target artifact, transformation rule, and rationale.

## 15. Behavioral Equivalence Requirements [M]
## 16. Intentional Target-State Changes [M]
## 17. Excluded / Retired Legacy Behavior [M]
## 18. Transformation Rules [M]
## 19. Naming / Semantic Mapping Rules [M]
## 20. Migration / Compatibility Requirements [C]
## 21. Code / Artifact Generation Requirements [M]

> **Cross-reference:** Generation units defined here must match entries in 16_GENERATION_MANIFEST generation_units array. Naming rules here feed into 16_GENERATION_MANIFEST naming_rules array.

## 22. Verification Strategy [M]
## 23. Acceptance Criteria [M]
## 24. Open Issues / Risks [M]
## 25. Forward Engineering Traceability Contract [M]


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
| Source-to-target mapping completeness (all critical constructs mapped) | 25% | | | |
| Transformation rules completeness | 20% | | | |
| Behavioral equivalence requirements | 15% | | | |
| Excluded / retired legacy behavior documented | 10% | | | |
| Verification and acceptance strategy | 15% | | | |
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
