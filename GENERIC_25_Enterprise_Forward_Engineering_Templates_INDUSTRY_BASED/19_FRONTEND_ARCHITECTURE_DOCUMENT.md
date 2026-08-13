# 19. Frontend / Client Architecture Document

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
- Do NOT name a specific frontend framework (no React, Angular, Vue, Next.js) — leave as team decision.
- Do NOT skip source module mapping — every source UI module must appear in Section 8 (Page/View Architecture).
- Do NOT omit role-aware experience — every view must document what changes per user role.
- Do NOT describe backend logic here — service calls belong in Section 11 (Data Interaction Model) only.

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
| Document Type | `19. Frontend / Client Architecture Document` |
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
| 03_USE_CASE_SPECIFICATION | All use cases and actors | YES |
| 11_API_CONTRACT_SPECIFICATION | All interfaces | YES |
| 20_UI_UX_SPECIFICATION | Screen inventory | YES |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Auth model | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Frontend |
| 24_TRACEABILITY_MATRIX | UI component IDs | Traceability |

## 1. Purpose and Scope [M]
## 2. Client Architecture Principles [M]
## 3. User Groups / Personas [M]
## 4. User Journeys [M]
## 5. Client Application Structure [M]
## 6. Presentation Architecture [M]
## 7. Navigation Architecture [M]
## 8. Page / View Architecture [M]
> **Cross-reference:** Every source UI module listed here must be traceable to at least one UC-* in 03_USE_CASE_SPECIFICATION and one screen specification in 20_UI_UX_SPECIFICATION. No source module may be omitted without a documented reason.

### Worked Example Row (generic)
| View ID | Name | Source Module | Primary Actor | Supported Use Cases | Key Data Displayed | Key Actions | Auth Required | Evidence Class |
|---|---|---|---|---|---|---|---|---|
| `VIEW-001` | `{VIEW_NAME}` | `{SOURCE_FORM_OR_MODULE}` | `ACT-001 {ROLE}` | `UC-001`, `UC-002` | {ENTITY} list: {FIELD_1}, {FIELD_2}, {STATUS} | {ACTION_1}, {ACTION_2} | YES — {PRIVILEGE_NAME} | OBSERVED |

> **Section passes QA when:** Every source UI module has a corresponding target view entry. Every view has primary actor, supported use cases, key data displayed, and auth requirement.

## 9. Component Architecture [M]
## 10. Client-Side State Model [M]
## 11. Data Interaction Model [M]
## 12. Validation Architecture [M]
## 13. Error / Exception Handling [M]
## 14. Authentication / Session [M]
> **Cross-reference:** Auth model here must align with 13_SECURITY_ARCHITECTURE Section 9 (Authentication). Session timeout values must match NFR-* entries in 14_NFR_SPECIFICATION.
## 15. Authorization / Role-Aware Experience [M]
## 16. Accessibility [M]
## 17. Internationalization / Localization [C]
## 18. Responsive / Device Behavior [C]
## 19. Client Performance [M]
## 20. Client Security [M]
## 21. Observability [C]
## 22. Client-to-Service Mapping [M]
## 23. UI-to-Use-Case Mapping [M]
## 24. UI-to-Requirement Mapping [M]
## 25. Testing Strategy [M]


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
| All source UI modules mapped to target views | 25% | | | |
| Page / view architecture completeness | 20% | | | |
| Component architecture and navigation | 15% | | | |
| Client security (auth, session, role-aware) | 20% | | | |
| Accessibility requirements | 10% | | | |
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
