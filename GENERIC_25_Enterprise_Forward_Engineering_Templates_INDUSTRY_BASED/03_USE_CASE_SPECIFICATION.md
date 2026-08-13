# 3. Use Case Specification

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

## Common Mistakes to Avoid [M]
- Do NOT write a use case without a Primary Actor — every use case needs one.
- Do NOT skip Alternative Flows and Exception Flows — they are mandatory.
- Do NOT reference BR-* IDs that are not defined in 01_BRD.md.
- Do NOT describe UI implementation details here — screen layouts belong in 20_UI_UX_SPECIFICATION.
- Do NOT write a Main Flow without numbered steps — each step must be a discrete actor/system action.
- Do NOT create UC-* IDs that conflict with existing ones — check the UC Catalog in Section 1 first.

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

## Document Control [M]

| Field | Value |
|---|---|
| Document ID | `{DOCUMENT_ID}` |
| Document Type | `3. Use Case Specification` |
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
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 7 Functional Requirements | YES |
| 02_BUSINESS_CAPABILITY_MODEL | Section 4 Capability Catalog | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 04_BUSINESS_PROCESS_MODEL | Use case flows | Process elaboration |
| 10_SERVICE_CATALOG | Use case operations | Service derivation |
| 11_API_CONTRACT_SPECIFICATION | Use case operations | API operation mapping |
| 19_FRONTEND_ARCHITECTURE_DOCUMENT | Use case actors and flows | UI flow derivation |
| 20_UI_UX_SPECIFICATION | Use case scenarios | Screen specification |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Use Case |
| 24_TRACEABILITY_MATRIX | All UC-* IDs | Traceability anchor |

## 1. Use Case Catalog [M]
## 2. Use Case Identification [M]
> **Cross-reference:** Every UC-* defined here must appear in 24_TRACEABILITY_MATRIX. Each UC-* must link to at least one CAP-* from 02_BUSINESS_CAPABILITY_MODEL and at least one BR-* from 01_BRD.

### 2.1 ID and Name
### 2.2 Goal
### 2.3 Scope
### 2.4 Priority
### 2.5 Related Capability / Process

## 3. Actors and External Parties [M]
### 3.1 Primary Actor
### 3.2 Secondary Actors
### 3.3 Supporting Systems / Services

## 4. Preconditions [M]
## 5. Trigger [M]
## 6. Main Success Scenario [M]
Numbered actor/system interactions with business rules and data effects.

### Worked Example — Use Case (generic)
| Field | Example Value |
|---|---|
| ID | `UC-001` |
| Name | {USE_CASE_NAME} |
| Goal | {ACTOR} can {ACHIEVE_GOAL} so that {BUSINESS_VALUE}. |
| Scope | {SYSTEM_NAME} |
| Priority | Must Have |
| Related Capability | `CAP-001` |
| Primary Actor | `ACT-001 {ROLE_NAME}` |
| Secondary Actors | `ACT-002 {SUPPORTING_ROLE}` |
| Preconditions | {ENTITY} exists; actor holds {PRIVILEGE}. |
| Trigger | Actor selects "{ACTION}" on {ENTITY} record. |
| Main Flow | 1. Actor opens {VIEW_NAME}. 2. System displays {ENTITY} list. 3. Actor selects record. 4. Actor invokes action. 5. System validates via `BRL-001`. 6. System persists change. 7. System confirms success. |
| Alternative Flow 1 | Step 5: Validation fails → System displays error message → Use case restarts at step 3. |
| Exception 1 | {ENTITY} locked by another session → System displays conflict message → Use case terminates. |
| Business Rules | `BRL-001`, `BRL-003` |
| Postconditions | {ENTITY} status updated; audit entry created. |
| Acceptance Criteria | Given preconditions met, when actor completes flow, then {ENTITY} updated within 3 s and audit log entry exists. |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {FORM_OR_MODULE}` |
| Confidence | 0.88 |

| Field | Example Value — Alternative Scenario |
|---|---|
| ID | `UC-002` |
| Name | {USE_CASE_NAME_2} |
| Goal | {ACTOR} can {ACHIEVE_GOAL_2} so that {BUSINESS_VALUE_2}. |
| Primary Actor | `ACT-002 {ROLE_NAME_2}` |
| Preconditions | {ENTITY} status = {STATUS}; actor holds {PRIVILEGE_2}. |
| Trigger | Scheduled event: {SCHEDULE_TRIGGER}. |
| Main Flow | 1. System identifies eligible {ENTITY} records. 2. System applies {BRL-002}. 3. System generates {OUTPUT}. 4. System notifies {ACTOR}. |
| Business Rules | `BRL-002`, `BRL-005` |
| Postconditions | {OUTPUT} persisted; {ACTOR} notified; audit entry created. |
| Evidence Class | INFERRED |
| Confidence | 0.72 |

> **Section passes QA when:** Every step is numbered. Every step identifies whether the actor or system performs the action. Every business rule applied is referenced by BRL-* ID. Postconditions are stated.

## 7. Alternative Flows [M]
> **Section passes QA when:** At least one alternative flow exists per use case. Each alternative flow references the step number it diverges from in the Main Flow.

## 8. Exception / Error Flows [M]
> **Section passes QA when:** At least one exception flow exists covering the most likely failure scenario. Each exception references the step number it diverges from.

## 9. Business Rules [M]
> **Cross-reference:** BRL-* IDs listed here must be defined in 01_BRD.md Section 8. Do not define new business rules here — only reference existing BRL-* IDs.

## 10. Data Requirements and State Changes [M]
## 11. Postconditions [M]
## 12. Authorization and Audit Requirements [M]
> **Cross-reference:** Authorization requirements here feed directly into 13_SECURITY_ARCHITECTURE Section 10 (Authorization) and 19_FRONTEND_ARCHITECTURE Section 15 (Role-Aware Experience).

## 13. Non-Functional Constraints [C]
## 14. Acceptance Criteria [M]
## 15. Related Requirements, Processes, Domains, Services and UI [M]
## 16. Use Case Validation [M]


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
| UC-* catalog completeness (all major use cases identified) | 20% | | | |
| Main flow completeness (all steps documented) | 20% | | | |
| Alternative and exception flows documented | 15% | | | |
| Business rules linked per use case | 15% | | | |
| Actors fully identified and catalogued | 10% | | | |
| Acceptance criteria present | 10% | | | |
| Evidence quality (OBSERVED / DERIVED ≥ 70%) | 10% | | | |
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
