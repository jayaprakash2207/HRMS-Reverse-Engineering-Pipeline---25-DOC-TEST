# 10. Service Catalog

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
- Do NOT prescribe implementation technology — services are technology-neutral at this stage.
- Do NOT create a service without linking it to a capability (CAP-*) and at least one use case (UC-*).
- Do NOT omit error conditions — every service must have at least one documented error scenario.
- Do NOT skip SLA requirements — even if unknown, mark as NOT_AVAILABLE with escalation to System Owner.
- Do NOT confuse a service (business operation) with an API endpoint (technical implementation).

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
| Document Type | `10. Service Catalog` |
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
| 04_BUSINESS_PROCESS_MODEL | Section 4 Process Catalog | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 11_API_CONTRACT_SPECIFICATION | All SVC-* entries | API contract scoping |
| 12_TECHNOLOGY_BLUEPRINT | Service layer | Architecture input |
| 15_FORWARD_ENGINEERING_SPECIFICATION | Section 10 Service Reconstruction | |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Service |
| 24_TRACEABILITY_MATRIX | All SVC-* IDs | Traceability |

## 1. Purpose and Service Taxonomy [M]
## 2. Service Inventory [M]
## 3. Service Specification [M]

> **Cross-reference:** SVC-* IDs defined here are the master service registry. 11_API_CONTRACT maps each SVC-* to one or more interface operations (IF-*/OP-*). Every SVC-* must appear in 24_TRACEABILITY_MATRIX.

### Worked Example Row (generic)
| Field | Example Value |
|---|---|
| ID | `SVC-001` |
| Name | {SERVICE_NAME} |
| Purpose | Expose {BUSINESS_CAPABILITY} as a callable operation. |
| Business Capability | `CAP-001` |
| Consumers | `{CONSUMER_ROLE}`, `{CONSUMING_SYSTEM}` |
| Owner | `{SERVICE_OWNER_ROLE}` |
| Inputs | {INPUT_ENTITY}: {FIELD_1}, {FIELD_2} |
| Outputs | {OUTPUT_ENTITY}: {RESULT_FIELDS} or error code |
| Preconditions | Caller authenticated; {INPUT_ENTITY} exists. |
| Postconditions | {ENTITY} updated; audit entry created. |
| Business Rules | `BRL-001`, `BRL-003` |
| Error Conditions | `ERR-001` {ENTITY}_NOT_FOUND; `ERR-002` INSUFFICIENT_PRIVILEGE |
| Security | Requires {PRIVILEGE_NAME}; all inputs validated before processing. |
| SLA | Response ≤ {LATENCY_MS} ms (p95); availability ≥ {AVAILABILITY}% |
| Criticality | High / Medium / Low |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {PACKAGE}.{PROCEDURE}` |
| Confidence | 0.88 |

### 3.1 Service ID / Name
### 3.2 Purpose and Business Capability
### 3.3 Consumers
### 3.4 Owner
### 3.5 Inputs / Outputs
### 3.6 Preconditions / Postconditions
### 3.7 Business Rules
### 3.8 Dependencies
### 3.9 Error Conditions
### 3.10 Security / Authorization
### 3.11 Audit
### 3.12 Service-Level Requirements
### 3.13 Criticality

> **Section passes QA when:** Every SVC-* has all 13 sub-fields. Business capability link (CAP-*) is present. At least one error condition is documented. SLA is either specified or escalated.

## 4. Service Relationships [M]
## 5. Service Dependencies [M]
## 6. Service Lifecycle [M]
## 7. Service-to-Process Mapping [M]

> **Cross-reference:** PRC-* IDs here must match 04_BUSINESS_PROCESS_MODEL Section 4. CAP-* IDs must match 02_BUSINESS_CAPABILITY_MODEL Section 4.

## 8. Service-to-Capability Mapping [M]
## 9. Service-to-Interface/API Mapping [C]
## 10. Service-to-Requirement Mapping [M]
## 11. Service Quality Requirements [M]


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
| Service inventory completeness (all major operations catalogued) | 25% | | | |
| Service specification completeness (inputs, outputs, rules, errors) | 25% | | | |
| SLA and quality requirements defined | 15% | | | |
| Service-to-capability mapping | 15% | | | |
| Evidence quality | 10% | | | |
| Service lifecycle documented | 10% | | | |
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
