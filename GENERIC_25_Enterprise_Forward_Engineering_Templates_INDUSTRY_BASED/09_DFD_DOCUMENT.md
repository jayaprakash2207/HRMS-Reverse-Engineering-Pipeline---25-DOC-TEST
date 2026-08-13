# 9. Data Flow Diagram (DFD) Document

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
- Do NOT skip the Context Diagram (Level 0) — it is mandatory.
- Do NOT show internal system mechanics at Level 0 — only external entities and the system boundary.
- Do NOT define data flows without specifying the data content.
- Do NOT omit sensitive data flows — any flow carrying Confidential or Restricted data must be flagged.

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
| Document Type | `9. Data Flow Diagram (DFD) Document` |
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
| 04_BUSINESS_PROCESS_MODEL | Processes and flows | YES |
| 07_DATA_MODEL_SPECIFICATION | Data stores | YES |
| 10_SERVICE_CATALOG | Services and interfaces | PARTIAL |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 11_API_CONTRACT_SPECIFICATION | Data flows and interfaces | API scoping |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Sensitive data flows | Threat modelling |
| 15_FORWARD_ENGINEERING_SPECIFICATION | Section 9 Data Reconstruction | |
| 24_TRACEABILITY_MATRIX | Process and flow IDs | Traceability |

## 1. Purpose and Scope [M]
## 2. DFD Notation and Conventions [M]
## 3. Context Diagram [M]
## 4. Level-0 DFD [M]
## 5. Level-1 DFDs [M]
## 6. Level-2 DFDs [C]
## 7. External Entities [M]
## 8. Processes [M]
## 9. Data Stores [M]

> **Cross-reference:** Every data store here must correspond to an entity in 07_DATA_MODEL_SPECIFICATION. Use the same table/entity name — do not rename stores in the DFD.

## 10. Data Flows [M]

### Worked Example Row (generic)
| Flow ID | From | To | Data Content | Volume / Frequency | Sensitivity | Evidence Class |
|---|---|---|---|---|---|---|
| `DF-001` | `{ACTOR_OR_PROCESS}` | `{PROCESS_OR_STORE}` | {ENTITY} identifier, {KEY_FIELDS} | {VOLUME} per {PERIOD} | Internal | OBSERVED |
| `DF-002` | `{PROCESS}` | `{EXTERNAL_ENTITY}` | {NOTIFICATION_OR_REPORT_CONTENT} | {FREQUENCY} | Confidential | INFERRED |
| `DF-003` | `{DATA_STORE}` | `{PROCESS}` | Full {ENTITY} record including {SENSITIVE_FIELDS} | On-demand | Restricted | OBSERVED |

> **Section passes QA when:** Every flow has a source, destination, data content description, estimated volume/frequency, and sensitivity classification. No unlabelled flows.

## 11. Flow Content / Data Definitions [M]
## 12. Process Specifications [M]
## 13. Sensitive Data Flows [C]

> **Cross-reference:** Every sensitive flow identified here must be referenced in 13_SECURITY_ARCHITECTURE Section 13 (Interface/Integration Security). Missing cross-reference is a blocking issue.

## 14. Logical Trust / Control Boundaries [C]
## 15. DFD-to-Process Mapping [M]
## 16. DFD-to-Data Mapping [M]
## 17. DFD-to-Interface Mapping [C]


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
| Context diagram completeness | 15% | | | |
| Level-0 and Level-1 DFD completeness | 30% | | | |
| Data flow content definitions | 20% | | | |
| Sensitive data flow identification | 20% | | | |
| Evidence quality | 15% | | | |
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
