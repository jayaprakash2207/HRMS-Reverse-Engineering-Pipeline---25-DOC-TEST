# 25. Forward Engineering Input Map

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

## Common Mistakes to Avoid [M]
- Do NOT list an input as required if it is not actually consumed by a generation unit.
- Do NOT leave fallback as BLOCK for optional inputs — use DEGRADED for optional, BLOCK for required.
- Do NOT skip the conflict resolution rules — precedence must be defined for every overlapping input.
- Do NOT mark an input as READY if its source document is CONDITIONAL or BLOCKED.

## Document Control [M]

| Field | Value |
|---|---|
| Document ID | `{DOCUMENT_ID}` |
| Document Type | `25. Forward Engineering Input Map` |
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

### Upstream — requires ALL other 24 documents
| Document | Required Sections | Blocking? |
|---|---|---|
| All 24 content documents | All sections | YES — this document maps all inputs |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 16_GENERATION_MANIFEST | Input registry | Generation unit input specification |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | Section 18 Input Map Readiness | Readiness gate |

## 1. Purpose [M]
Define exactly which artifact and section supplies each downstream engineering activity.

## 2. Input Map Principles [M]
Precedence, explicit dependency, evidence preservation, no silent fallback, deterministic validation.

## 3. Input Registry [M]
> **Cross-reference:** Every FEI-* here must reference a real section from one of the 24 other documents. The source_document field must match the exact document filename. The source_section must match an existing section heading.

Each input receives `FEI-*`.

### Worked Example Row (generic)
| Input ID | Source Document | Source Section | Consumer (Generation Unit) | Purpose | Required? | Precedence | Validation Rule | Fallback | Blocking? |
|---|---|---|---|---|---|---|---|---|---|
| `FEI-001` | `01_BRD` | Section 7 Functional Requirements | Domain Model Generator | Provide business rule and requirement semantics for domain concept derivation | YES | 1 | All BR-* have evidence classification | BLOCK | YES |
| `FEI-002` | `06_DATA_DICTIONARY` | Section 4 Data Element Spec | Data Model Generator | Provide canonical field definitions and types | YES | 1 | All DE-* have data type and definition | BLOCK | YES |
| `FEI-003` | `03_USE_CASE_SPEC` | Section 6 Main Flow | API Contract Generator | Derive operation signatures from use case steps | YES | 2 | All UC-* have complete main flow | BLOCK | YES |
| `FEI-004` | `13_SECURITY_ARCH` | Section 19 Security Requirements | Security Implementation Generator | Apply security controls to all generated components | YES | 1 | All BR-SEC-* have target state | BLOCK | YES |
| `FEI-005` | `14_NFR_SPEC` | Section 17 NFR Record | Architecture Configuration Generator | Apply measurable quality targets to runtime configuration | YES | 2 | All NFR-* have metric and target | BLOCK | YES |

> **Section passes QA when:** Every generation unit has at least one FEI-* input. Every required input has a fallback of BLOCK. Every optional input has a fallback of DEGRADED or SKIP. No FEI-* references a non-existent document section.

## 4. Source Artifact Registry [M]
## 5. Document Dependency Graph [M]
## 6. Input-to-Generation Mapping [M]
For each generation unit capture source document, section, fields, purpose, requiredness, precedence, validation, fallback, blocking status.

## 7. Business Inputs [M]
## 8. Domain / Semantic Inputs [M]
## 9. Data Inputs [M]
## 10. Process / Behavioral Inputs [M]
## 11. Service / Interface Inputs [M]
## 12. Architecture Inputs [M]
## 13. Security Inputs [M]
## 14. Quality / NFR Inputs [M]
## 15. UX Inputs [C]
## 16. Knowledge Graph / Canonical Model Inputs [M]
## 17. Traceability Inputs [M]
## 18. Generation Manifest Inputs [M]
## 19. Conflict Resolution / Precedence Rules [M]
> **Cross-reference:** Precedence rules here must be consistent with the conflict resolution approach in 22_CANONICAL_ENTERPRISE_MODEL Section 17 (Conflicting Definitions). When the canonical model conflicts with a source artifact, the canonical model takes precedence.
## 20. Missing Input Handling [M]
### 20.1 Required Missing → BLOCKED
### 20.2 Optional Missing → DEGRADED
### 20.3 Unknown Semantic → UNKNOWN
### 20.4 Contradiction → REVIEW / BLOCK according to criticality

## 21. Confidence Handling [M]
## 22. Input Validation [M]
## 23. Forward Engineering Output Mapping [M]
## 24. Input-to-Output Traceability [M]
## 25. Readiness Conditions [M]
## 26. Machine-Readable Example [M]
```json
{
  "input_id": "FEI-001",
  "source_document": "{{DOCUMENT_ID}}",
  "source_section": "{{SECTION}}",
  "consumer": "{{GENERATION_UNIT}}",
  "purpose": "{{PURPOSE}}",
  "required": true,
  "precedence": 1,
  "validation": ["{{RULE}}"],
  "fallback": "BLOCK"
}
```


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
| All 24 upstream documents registered as inputs | 25% | | | |
| Input-to-generation mapping completeness | 25% | | | |
| Conflict resolution and precedence rules defined | 20% | | | |
| Missing input handling strategy defined | 15% | | | |
| Machine-readable input map valid | 15% | | | |
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
