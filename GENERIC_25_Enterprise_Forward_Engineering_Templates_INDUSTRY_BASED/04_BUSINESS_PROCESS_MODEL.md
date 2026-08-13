# 4. Business Process Model

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
- Do NOT describe what a system does internally — focus on observable business activities.
- Do NOT skip the Trigger / Start Event — every process must have one.
- Do NOT create processes that duplicate use cases — processes are operational flows, use cases are interactions.
- Do NOT assign multiple owners to a single process step — one owner per step.
- Do NOT omit exception paths — every process has at least one exception scenario.

Do not delete a mandatory section because evidence is missing. Record `UNKNOWN`, `NOT_AVAILABLE`, `NOT_APPLICABLE`, or `CONTRADICTED` with rationale.

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
| Document Type | `4. Business Process Model` |
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
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 6 Processes | YES |
| 02_BUSINESS_CAPABILITY_MODEL | Section 3 Hierarchy | YES |
| 03_USE_CASE_SPECIFICATION | Use case flows | PARTIAL |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 05_DOMAIN_MODEL | Section 14 Domain-to-Process | Process-domain alignment |
| 10_SERVICE_CATALOG | Section 7 Service-to-Process | Service discovery |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Process |
| 24_TRACEABILITY_MATRIX | All process IDs | Traceability |

## 1. Process Landscape [M]
## 2. Process Modeling Method and Notation [M]
## 3. Process Hierarchy [M]
### 3.1 Enterprise / Value Chain
### 3.2 Process Group
### 3.3 Business Process
### 3.4 Subprocess / Activity [C]

## 4. Process Catalog [M]
> **Cross-reference:** PRC-* IDs defined here feed into 10_SERVICE_CATALOG Section 7 (Service-to-Process Mapping) and 09_DFD_DOCUMENT Section 8 (Processes). Use the same PRC-* IDs everywhere.

### Worked Example Row (generic)
| Field | Example Value |
|---|---|
| ID | `PRC-001` |
| Name | {PROCESS_NAME} |
| Objective | Ensure {BUSINESS_OUTCOME} is completed accurately and within {TIME_CONSTRAINT}. |
| Trigger | {TRIGGERING_EVENT} |
| Actors | `ACT-001 {INITIATOR}`, `ACT-002 {APPROVER}` |
| Inputs | {INPUT_ENTITY_OR_DATA} |
| Key Activities | 1. Initiate {ACTION}. 2. Validate {RULE}. 3. Approve if threshold exceeded. 4. Record outcome. |
| Business Rules | `BRL-001`, `BRL-004` |
| Controls | Dual authorisation for transactions > {THRESHOLD}. |
| Exceptions | If {CONDITION}, escalate to {ESCALATION_ROLE}. |
| Outputs | Updated {ENTITY}; audit record; notification to {STAKEHOLDER}. |
| KPI | {PROCESS_NAME} completion time ≤ {TARGET_DURATION}. Error rate < {ERROR_THRESHOLD}%. |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {PROCEDURE_OR_TRIGGER}` |
| Confidence | 0.82 — HIGH (observed in procedure body) |

## 5. Process Specification [M]
> **Cross-reference:** Business rules referenced in Section 5.7 must be BRL-* IDs from 01_BRD.md Section 8. Actors must be ACT-* IDs from 03_USE_CASE_SPECIFICATION Section 3.

### 5.1 Objective
### 5.2 Trigger / Start Event
### 5.3 Actors / Roles
### 5.4 Inputs
### 5.5 Activities
### 5.6 Decisions
### 5.7 Business Rules
### 5.8 Controls
### 5.9 Exceptions
### 5.10 Outputs
### 5.11 End Conditions

> **Section passes QA when:** All 11 sub-sections (5.1–5.11) are populated. Every activity references an actor. Every decision references a BRL-*. At least one exception path is documented.

## 6. Current-State Process [M]
## 7. Target-State Process Requirements [M]
## 8. Process Gaps and Improvement Opportunities [M]
## 9. Process KPIs / Measures [C]
## 10. Process-to-Capability Mapping [M]
## 11. Process-to-Requirement / Use Case Mapping [M]
## 12. Process-to-Data / Service Mapping [M]
## 13. Process Validation [M]


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
| Process hierarchy and landscape completeness | 20% | | | |
| Process specifications completeness (all steps, rules, exceptions) | 25% | | | |
| Current-state vs target-state documented | 15% | | | |
| Process-to-capability mapping | 15% | | | |
| Evidence quality | 15% | | | |
| KPIs / measures defined | 10% | | | |
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
