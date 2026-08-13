# 18. Deployment Architecture Document

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
- Do NOT name specific cloud providers, container platforms, or orchestration tools unless the project has chosen them.
- Do NOT skip disaster recovery — even if unknown, mark as NOT_AVAILABLE and escalate to System Owner.
- Do NOT omit security boundaries — every deployable unit must have a documented security perimeter.
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
| Document Type | `18. Deployment Architecture Document` |
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
| 12_TECHNOLOGY_BLUEPRINT | Section 14 Deployment Model | YES |
| 14_NFR_SPECIFICATION | Sections 7, 11, 12 | YES |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Section 4, Section 11 | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Deployment |
| 24_TRACEABILITY_MATRIX | Deployment unit IDs | Traceability |

## 1. Purpose and Scope [M]
## 2. Deployment Principles [M]
## 3. Environment Model [M]

> **Section passes QA when:** At least Dev, Test, and Production environments are defined. Each environment has a purpose, isolation level, and data classification. DR environment is documented or escalated.

## 4. Deployable Units [M]
> **Cross-reference:** Every deployment unit here must correspond to a logical component in 12_TECHNOLOGY_BLUEPRINT Section 8 and an ARCH-* in 23_ARCHITECTURE_INVENTORY. Availability requirements must match NFR-* entries in 14_NFR_SPECIFICATION.

### Worked Example Row (generic)
| Unit ID | Name | Type | Responsibilities | Interfaces | Scaling Model | Availability Requirement | Evidence Class |
|---|---|---|---|---|---|---|---|
| `DEP-001` | `{UNIT_NAME}` | {Service / Data / UI / Integration / Security} | {WHAT_THIS_UNIT_DOES} | Exposes `{INTERFACE}`; consumes `{DEPENDENCY}` | {SCALING_APPROACH — technology-neutral, e.g. "horizontal, stateless"} | ≥ {AVAILABILITY}% monthly | INFERRED |

## 5. Runtime Components [M]
## 6. Logical Placement [M]
## 7. Network / Communication Zones [M]
## 8. Communication Paths [M]
## 9. Data Storage and Persistence [M]
## 10. External Dependencies [M]
## 11. Security Boundaries [M]
> **Cross-reference:** Security boundaries here must be consistent with trust boundaries in 13_SECURITY_ARCHITECTURE Section 7.4. Every boundary must reference the security controls that enforce it.
## 12. Identity and Access [M]
## 13. Configuration Management [M]
## 14. Secrets / Credential Handling [M]
## 15. Availability Architecture [M]
## 16. Scalability / Capacity [M]
## 17. Resilience / Failure Handling [M]
## 18. Backup / Restore [M]
## 19. Disaster Recovery / Continuity [C]
## 20. Monitoring / Logging / Observability [C]
## 21. Deployment / Release Process [M]
## 22. Rollback / Recovery Strategy [M]
## 23. Environment Matrix [M]
## 24. Deployment-to-Component Mapping [M]
## 25. Risks / Constraints [M]


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
| Environment model completeness (Dev/Test/UAT/Prod/DR) | 20% | | | |
| Deployable unit specification completeness | 20% | | | |
| Security boundaries and network zones | 20% | | | |
| Availability, resilience, and DR requirements | 20% | | | |
| Configuration and secrets management requirements | 10% | | | |
| Evidence quality | 10% | | | |
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
