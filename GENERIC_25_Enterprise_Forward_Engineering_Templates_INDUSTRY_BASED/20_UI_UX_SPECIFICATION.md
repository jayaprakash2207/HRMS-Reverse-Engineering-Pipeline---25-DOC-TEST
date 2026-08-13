# 20. UI/UX Specification

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
- Do NOT specify a UI framework or component library — those are implementation decisions.
- Do NOT skip loading, empty, error, and success states — all 4 must be defined per screen.
- Do NOT omit authorization states — every screen must document what changes per role.
- Do NOT describe backend service calls here — those belong in 19_FRONTEND_ARCHITECTURE Section 11.
- Do NOT invent screens not evidenced in the source system — mark as ASSUMED if inferring.

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
| Document Type | `20. UI/UX Specification` |
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
| 03_USE_CASE_SPECIFICATION | Use cases and actors | YES |
| 19_FRONTEND_ARCHITECTURE_DOCUMENT | View inventory | YES |
| 06_DATA_DICTIONARY | Field definitions | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: UX |
| 24_TRACEABILITY_MATRIX | Screen and field IDs | Traceability |

## 1. UX Objectives [M]
## 2. User Groups and Roles [M]
## 3. Personas [C]
## 4. User Goals [M]
## 5. User Journeys / Scenarios [M]
## 6. Information Architecture [M]
## 7. Navigation Model [M]
## 8. Interaction Model [M]
## 9. Screen / View Inventory [M]
> **Cross-reference:** Every screen here must map to a VIEW-* in 19_FRONTEND_ARCHITECTURE Section 8 and at least one UC-* in 03_USE_CASE_SPECIFICATION. Screen field names must match DE-* IDs from 06_DATA_DICTIONARY.
## 10. Screen / View Specification [M]

### Worked Example Row (generic)
| Sub-section | Example Content |
|---|---|
| 10.1 Purpose | Allow {ACTOR_ROLE} to {PERFORM_ACTION} on a {PRIMARY_ENTITY} record. |
| 10.2 User / Role | `ACT-001 {ROLE_NAME}` — {DESCRIPTION_OF_ROLE} |
| 10.3 Entry Conditions | Actor authenticated; {PRIMARY_ENTITY} record selected. |
| 10.4 Information Displayed | {ENTITY} {FIELD_1}, {FIELD_2}, {STATUS}; last-modified timestamp; audit history summary. |
| 10.5 Actions | [{ACTION_1}] — triggers `UC-001`; [{ACTION_2}] — triggers `UC-002`; [Cancel] — returns to list. |
| 10.6 Inputs / Forms | {FIELD_1}: {TYPE}, required, max {LENGTH}; {FIELD_2}: {TYPE}, optional. |
| 10.7 Validation | {FIELD_1} must match pattern {PATTERN}; {FIELD_2} must be ≥ 0. Inline validation on blur. |
| 10.8 Business Rules | `BRL-001`, `BRL-003` enforced on submission. |
| 10.9 States | Loading: spinner; Empty: "No {ENTITY} found"; Error: inline error banner; Success: confirmation toast. |
| 10.10 Authorization States | {PRIVILEGE_A}: full edit; {PRIVILEGE_B}: read-only; no privilege: access denied page. |
| 10.11 Confirmation | Destructive actions require confirmation dialog: "Are you sure you want to {ACTION}? This cannot be undone." Audited. |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FORM} / {CANVAS_OR_BLOCK}` |

### 10.1 Purpose
### 10.2 User / Role
### 10.3 Entry Conditions
### 10.4 Information Displayed
### 10.5 Actions
### 10.6 Inputs / Forms
### 10.7 Validation
### 10.8 Business Rules
### 10.9 Loading / Empty / Error / Success States
### 10.10 Authorization States
### 10.11 Confirmation / Audit Behavior

> **Section passes QA when:** All 11 sub-sections (10.1–10.11) are populated for every screen. Loading, empty, error, and success states are all defined. Authorization states cover all relevant roles.

## 11. Component Specifications [M]
## 12. Form / Field Specifications [M]
> **Cross-reference:** Every field specification here must reference its DE-* from 06_DATA_DICTIONARY. Validation rules here must be consistent with BRL-* rules in 01_BRD Section 8.3.
## 13. Workflow / Approval Interaction [C]
## 14. Notifications [C]
## 15. Accessibility [M]
## 16. Responsive / Device Requirements [C]
## 17. Content / Terminology [M]
## 18. Usability Requirements [M]
## 19. UX Acceptance Criteria [M]
## 20. Traceability [M]

Use human-centred design principles appropriate to the project context.


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
| Screen inventory completeness (all source modules covered) | 20% | | | |
| Screen specification completeness (all 11 sub-sections per screen) | 30% | | | |
| Accessibility requirements (WCAG 2.2 AA minimum) | 15% | | | |
| Validation and error state coverage | 15% | | | |
| Authorization state coverage | 10% | | | |
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
