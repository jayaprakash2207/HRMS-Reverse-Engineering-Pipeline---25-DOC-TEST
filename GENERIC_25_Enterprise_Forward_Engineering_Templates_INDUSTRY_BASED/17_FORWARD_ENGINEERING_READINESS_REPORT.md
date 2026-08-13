# 17. Forward Engineering Readiness Report

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
- Do NOT report a readiness percentage without showing the scoring calculation.
- Do NOT mark a dimension as READY if any mandatory section in that dimension's documents is NOT_AVAILABLE without an approved resolution.
- Do NOT issue a GO decision if any blocking issue is unresolved.
- Do NOT skip the remediation plan — every blocker must have an owner and a resolution path.

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
| Document Type | `17. Forward Engineering Readiness Report` |
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

### Upstream — ALL 24 other documents must be substantially complete
| Document | Minimum Readiness | Blocking? |
|---|---|---|
| All 22 content documents (01–15, 18–25) | CONDITIONAL or better | YES |
| 16_GENERATION_MANIFEST | Schema valid | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 16_GENERATION_MANIFEST | Readiness gates | Final generation authorisation |

## 1. Executive Readiness Summary [M]
## 2. Assessment Method and Scoring [M]
## 3. Source Completeness [M]
## 4. Business Requirements Readiness [M]
## 5. Capability / Process Readiness [M]
## 6. Use Case / Behavioral Readiness [M]
## 7. Domain / Semantic Readiness [M]
## 8. Data Readiness [M]
## 9. Service / Interface Readiness [M]
## 10. Architecture Readiness [M]
## 11. Security Readiness [M]
## 12. NFR / Quality Readiness [M]
## 13. User Experience Readiness [C]
## 14. Knowledge Graph / Canonical Model Readiness [M]
## 15. Architecture Inventory Readiness [M]
## 16. Traceability Readiness [M]
## 17. Generation Manifest Readiness [M]
## 18. Input Map Readiness [M]
## 19. Ambiguities and Contradictions [M]
## 20. Missing Information [M]
## 21. Unsupported Inferences [M]
## 22. Confidence Assessment [M]
## 23. Blocking Issues [M]
> **Cross-reference:** Every blocking issue here must reference the specific document, section, and ID (BR-*, UC-*, DE-*, etc.) that is blocked. Vague blocking issues (e.g. "data model incomplete") are not acceptable.

> **Section passes QA when:** Every blocker has an owner, a resolution action, and a target resolution date or condition. No blocker is listed without a path to resolution.

## 24. Non-Blocking Issues [M]
## 25. Readiness Score [M]
> **Cross-reference:** Scoring dimensions here must match the readiness_scoring_model in 16_GENERATION_MANIFEST. GO/CONDITIONAL-GO/NO-GO thresholds must match the decision_thresholds in 16_GENERATION_MANIFEST exactly.

### Readiness Score — Worked Example Structure (generic)

#### Scoring Model (ISO/IEC 25010-inspired, TOGAF ADM-aligned)
| Dimension | Weight | Raw Score (0–3) | Weighted Score | Status |
|---|---|---|---|---|
| Source evidence completeness | 20% | {0-3} | {W×S} | READY / CONDITIONAL / BLOCKED |
| Business requirements coverage | 15% | {0-3} | {W×S} | |
| Use case and process coverage | 10% | {0-3} | {W×S} | |
| Data model completeness | 10% | {0-3} | {W×S} | |
| Service and API contract completeness | 10% | {0-3} | {W×S} | |
| Security and compliance coverage | 10% | {0-3} | {W×S} | |
| NFR measurability | 5% | {0-3} | {W×S} | |
| Traceability coverage | 10% | {0-3} | {W×S} | |
| Cross-document consistency | 10% | {0-3} | {W×S} | |
| **Total** | **100%** | | **{TOTAL}/3.0** | |

**Percentage score**: {TOTAL}/3.0 × 100 = **{PERCENT}%**

#### Decision Thresholds (from 16_GENERATION_MANIFEST)
| Decision | Condition |
|---|---|
| GO | ≥ 80% AND zero blocking issues |
| CONDITIONAL-GO | ≥ 65% AND no critical blocking issues |
| NO-GO | < 65% OR any critical blocking issue |

#### Decision: {GO / CONDITIONAL-GO / NO-GO}
Rationale: {EXPLAIN}

> **Section passes QA when:** A weighted score table is present. Every dimension has a raw score (0–3), weight, and weighted score. Total percentage is calculated. GO/CONDITIONAL-GO/NO-GO decision is recorded with rationale.

## 26. Remediation Plan [M]
## 27. Go / Conditional-Go / No-Go Decision [M]
## 28. Approval [M]

Never report an unexplained readiness percentage. Show the scoring dimensions, weights, blockers and evidence.


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
| All 24 upstream documents assessed (no gaps) | 30% | | | |
| Readiness score calculated transparently | 25% | | | |
| Blocking issues fully enumerated | 20% | | | |
| Remediation plan defined for all blockers | 15% | | | |
| Go/No-Go decision recorded with rationale | 10% | | | |
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
