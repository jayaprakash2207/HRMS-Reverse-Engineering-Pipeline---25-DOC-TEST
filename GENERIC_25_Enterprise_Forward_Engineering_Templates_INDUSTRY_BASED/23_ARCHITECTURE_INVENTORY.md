# 23. Architecture Inventory

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
- Do NOT invent components not evidenced in the source system.
- Do NOT assign a component to multiple types — pick the primary type only.
- Do NOT skip the current-state vs target-state distinction — they must be documented separately.
- Do NOT omit deprecated or retiring components — they are important for migration planning.

## Document Control [M]

| Field | Value |
|---|---|
| Document ID | `{DOCUMENT_ID}` |
| Document Type | `23. Architecture Inventory` |
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
| Source system artifacts | All | YES |
| 12_TECHNOLOGY_BLUEPRINT | Section 8 Components | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 12_TECHNOLOGY_BLUEPRINT | Architecture views | Blueprint alignment |
| 15_FORWARD_ENGINEERING_SPECIFICATION | Source-to-target mapping | |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Architecture Inventory |
| 24_TRACEABILITY_MATRIX | All ARCH-* IDs | Traceability |

## 1. Inventory Scope [M]
## 2. Inventory Taxonomy [M]
## 3. Inventory Classification [M]
## 4. Business Components [M]
## 5. Application / Functional Components [M]
## 6. Service Components [C]
## 7. Interface / Integration Components [M]
## 8. Data / Information Components [M]
## 9. Security Components [C]
## 10. User Experience Components [C]
## 11. Technology / Runtime Components [C]
## 12. External Systems / Products [C]

## 13. Component Specification [M]
> **Cross-reference:** Every ARCH-* here must appear in 12_TECHNOLOGY_BLUEPRINT Section 8 (Logical Components). Security components must be cross-referenced with 13_SECURITY_ARCHITECTURE Section 18 (Security Controls).

### Worked Example Row (generic)
| Field | Example Value |
|---|---|
| ID | `ARCH-001` |
| Name | `{COMPONENT_NAME}` |
| Type | Business / Application / Service / Interface / Data / Security / UI / External |
| Responsibility | {WHAT_THIS_COMPONENT_DOES} |
| Owner | `{BUSINESS_OR_TECHNICAL_OWNER}` |
| Lifecycle | Active / Deprecated / Retiring |
| Criticality | High / Medium / Low |
| Inputs | From `{UPSTREAM_COMPONENT}` — {DATA_OR_EVENT} |
| Outputs | To `{DOWNSTREAM_COMPONENT}` — {DATA_OR_EVENT} |
| Security | {SECURITY_CONTROLS_APPLIED} |
| Deployment Role | {ROLE_IN_DEPLOYMENT_TOPOLOGY} |
| Source Evidence | `{SOURCE_FILE} / {OBJECT}` |
| Evidence Class | OBSERVED |
| Confidence | 0.90 |

### 13.1 ID / Name / Type
### 13.2 Responsibility
### 13.3 Owner
### 13.4 Lifecycle / Status
### 13.5 Criticality
### 13.6 Inputs / Outputs
### 13.7 Interfaces
### 13.8 Data
### 13.9 Dependencies
### 13.10 Security
### 13.11 Deployment Role
### 13.12 Source Evidence
### 13.13 Confidence

> **Section passes QA when:** Every ARCH-* has all 13 sub-fields (13.1–13.13) populated or escalated. Criticality is assigned. Source evidence reference is present.

## 14. Component Relationships [M]
## 15. Architecture Views / Viewpoints [M]
## 16. Current-State Inventory [M]
> **Cross-reference:** Every source artifact (form, package, table, trigger) from the 8 agent input files must appear in the current-state inventory. Gaps between source artifacts and inventory entries are blocking issues.
## 17. Target-State Inventory [M]
## 18. Gaps / Duplicates / Obsolete Elements [M]
## 19. Inventory-to-Architecture Mapping [M]


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
| Component inventory completeness (all source constructs catalogued) | 25% | | | |
| Component specification completeness (all 13 fields) | 20% | | | |
| Current-state vs target-state inventory | 20% | | | |
| Gaps, duplicates, and obsolete elements documented | 15% | | | |
| Evidence quality | 10% | | | |
| Architecture views / viewpoints defined | 10% | | | |
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
