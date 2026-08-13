# 2. Business Capability Model

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
- Do NOT describe how a capability is implemented — only what it achieves.
- Do NOT create capabilities that duplicate process steps — capabilities are outcomes, not activities.
- Do NOT assign a capability to more than one owner — ownership must be unambiguous.
- Do NOT invent capabilities not evidenced in the source system — mark as ASSUMED if inferring.
- Do NOT confuse capability with service — capabilities belong here, service definitions belong in 10_SERVICE_CATALOG.

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
| Document Type | `2. Business Capability Model` |
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
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 5 Capabilities, Section 6 Processes | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 03_USE_CASE_SPECIFICATION | Capability references | Use case scoping |
| 04_BUSINESS_PROCESS_MODEL | Section 3 Hierarchy | Process grouping |
| 10_SERVICE_CATALOG | Section 8 Capability mapping | Service-to-capability alignment |
| 15_FORWARD_ENGINEERING_SPECIFICATION | Section 6 Business Reconstruction | Capability reconstruction |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Capability |
| 24_TRACEABILITY_MATRIX | All CAP-* IDs | Traceability anchor |

## 1. Purpose and Scope [M]
## 2. Capability Modeling Principles [M]
## 3. Capability Hierarchy [M]
### 3.1 Enterprise / Value-Chain Level
### 3.2 Business Domain Level
### 3.3 Capability Level
### 3.4 Optional Sub-Capability Level [C]

## 4. Capability Catalog [M]
> **Cross-reference:** CAP-* IDs defined here are referenced in 03_USE_CASE_SPEC Section 2.5, 10_SERVICE_CATALOG Section 3.2, and 24_TRACEABILITY_MATRIX. Use the exact same CAP-* ID everywhere — never rename or renumber.

For each `CAP-*`: name, definition, outcome, owner, consumers, criticality, maturity, current support, target need, dependencies and evidence.

### Worked Example Row (generic — replace with project-specific content)
| Field | Example Value |
|---|---|
| ID | `CAP-001` |
| Name | {CAPABILITY_NAME} |
| Definition | The ability to {VERB} {OBJECT} in accordance with {POLICY_OR_RULE}. |
| Outcome | {MEASURABLE_BUSINESS_OUTCOME} |
| Owner | `{BUSINESS_UNIT_OR_ROLE}` |
| Consumers | `{CONSUMING_ROLE_1}`, `{CONSUMING_ROLE_2}` |
| Criticality | High / Medium / Low |
| Maturity (current) | 1 = Initial / 2 = Managed / 3 = Defined / 4 = Quantitatively Managed / 5 = Optimising |
| Current Support | Manual / Partially Automated / Fully Automated |
| Target Need | {TARGET_STATE_DESCRIPTION} |
| Dependencies | `CAP-{N}` |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {OBJECT}` |
| Confidence | 0.85 |

> **Section passes QA when:** Every CAP-* has a definition, outcome, owner, criticality, and source reference. Maturity score (1–5) is assigned. At least one mapping to a business requirement (BR-*) exists.

## 5. Capability Relationships [M]
### 5.1 Parent / Child
### 5.2 Depends On
### 5.3 Supports / Enables
### 5.4 Shared / Cross-Cutting

## 6. Capability Maturity and Current-State Assessment [M]
## 7. Capability Gaps [M]
> **Section passes QA when:** Every gap is linked to a CAP-* and has a target state description and priority. No gap is listed without evidence of what is currently missing.

## 8. Capability Prioritization [M]
## 9. Capability-to-Process Mapping [M]
## 10. Capability-to-Requirement Mapping [M]
## 11. Capability-to-Domain Mapping [M]
## 12. Capability-to-Service / Component Mapping [C]
## 13. Target-State Capability Requirements [M]
## 14. Validation and Governance [M]


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
| Capability hierarchy completeness | 20% | | | |
| CAP-* catalog completeness (all major capabilities identified) | 25% | | | |
| Evidence quality (OBSERVED / DERIVED ≥ 70%) | 15% | | | |
| Maturity and gap assessment | 15% | | | |
| Capability-to-requirement mapping | 15% | | | |
| Capability-to-process mapping | 10% | | | |
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
