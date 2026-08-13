# 24. Traceability Matrix

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
- Do NOT create trace links without evidence — every link must cite a source document and section.
- Do NOT skip orphan analysis — items with no trace links are a quality signal.
- Do NOT create one-directional traces only — bidirectional traceability is required for critical items.
- Do NOT use unstable IDs (auto-incremented row numbers) — use the stable ID series (BR-*, UC-*, etc.).

## Document Control [M]

| Field | Value |
|---|---|
| Document ID | `{DOCUMENT_ID}` |
| Document Type | `24. Traceability Matrix` |
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

### Upstream — requires ALL other 24 documents to be substantially complete
| Document | Required Sections | Blocking? |
|---|---|---|
| All 24 content documents | All stable IDs (BR-*, UC-*, CAP-*, SVC-*, DE-*, NFR-*, ARCH-*, DOM-*, PRC-*) | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 17_FORWARD_ENGINEERING_READINESS_REPORT | Section 16 Traceability Readiness | Readiness input |
| 16_GENERATION_MANIFEST | Traceability gate | Generation gate |

## 1. Purpose and Objectives [M]
## 2. Traceability Model [M]
Define node types and permitted relationship types.

## 3. Source Artifact Inventory [M]
## 4. Source-to-Requirement Traceability [M]
> **Cross-reference:** Every BR-* traced here must be defined in 01_BRD Section 7. Every UC-* must be defined in 03_USE_CASE_SPECIFICATION Section 1. Every CAP-* must be in 02_BUSINESS_CAPABILITY_MODEL Section 4. Missing IDs are broken references — fix before marking this document READY.

> **Section passes QA when:** Source coverage ≥ 80%. Critical requirement coverage ≥ 95%. Orphan rate ≤ 5%. Every metric in Section 22 is calculated and populated.

## 5. Requirement-to-Capability [M]
## 6. Requirement-to-Process [M]
## 7. Requirement-to-Use-Case [M]
## 8. Requirement-to-Domain [M]
## 9. Requirement-to-Data [M]
## 10. Requirement-to-Service [M]
## 11. Requirement-to-Interface/API [C]
## 12. Requirement-to-Security [M]
## 13. Requirement-to-NFR [M]
## 14. Requirement-to-UI/UX [C]
## 15. Requirement-to-Architecture [M]
## 16. Source-to-Target Forward Engineering Traceability [M]
## 17. Bidirectional Traceability [M]
## 18. Coverage Analysis [M]
## 19. Orphan Analysis [M]
## 20. Conflict Analysis [M]
## 21. Missing Traceability [M]
## 22. Traceability Metrics [M]
> **Cross-reference:** Metrics calculated here feed directly into 17_READINESS_REPORT Section 16 (Traceability Readiness) and 16_GENERATION_MANIFEST quality gate GATE-TRACEABILITY. If coverage < 80%, the readiness gate CANNOT pass.

Recommended metrics: source coverage, critical requirement coverage, bidirectional coverage, orphan rate, unresolved conflicts, low-confidence critical items.

## 23. Machine-Readable Row Schema [M]
`TRACE-ID | SOURCE-ID | SOURCE-TYPE | RELATIONSHIP | TARGET-ID | TARGET-TYPE | EVIDENCE | CONFIDENCE | STATUS`

### Worked Example Rows (generic)
| TRACE-ID | SOURCE-ID | SOURCE-TYPE | TARGET-ID | TARGET-TYPE | RELATIONSHIP | EVIDENCE | CONFIDENCE | STATUS |
|---|---|---|---|---|---|---|---:|---|
| `TR-001` | `BR-001` | Requirement | `UC-001` | UseCase | `implements` | `01_BRD section 7` | 0.90 | Validated |
| `TR-002` | `UC-001` | UseCase | `SVC-001` | Service | `realized_by` | `10_SERVICE_CATALOG section 3` | 0.88 | Validated |
| `TR-003` | `SVC-001` | Service | `OP-001` | APIOperation | `exposed_as` | `11_API_CONTRACT section 5` | 0.87 | Validated |
| `TR-004` | `BR-001` | Requirement | `DE-001` | DataElement | `constrains` | `01_BRD BRL-001` | 0.85 | Validated |
| `TR-005` | `BR-SEC-001` | SecurityRequirement | `NFR-003` | NFR | `related_to` | `13_SECURITY_ARCH section 19` | 0.90 | Validated |

### Coverage Metrics Formula
```
source_coverage = (source_items_with_at_least_one_link / total_source_items) × 100
requirement_coverage = (requirements_with_at_least_one_link / total_requirements) × 100
critical_req_coverage = (critical_requirements_fully_traced / total_critical_requirements) × 100
bidirectional_rate = (items_with_both_forward_and_backward_links / total_items) × 100
orphan_rate = (items_with_zero_links / total_items) × 100
```
Target: source_coverage ≥ 80%; requirement_coverage ≥ 95% for critical items; orphan_rate ≤ 5%.

## 24. Certification / Approval [M]


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
| Source coverage ≥ 80% | 20% | | | |
| Critical requirement coverage ≥ 95% | 25% | | | |
| Bidirectional traceability rate ≥ 70% | 20% | | | |
| Orphan rate ≤ 5% | 15% | | | |
| Conflict analysis completeness | 10% | | | |
| Metrics calculated and reported | 10% | | | |
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
