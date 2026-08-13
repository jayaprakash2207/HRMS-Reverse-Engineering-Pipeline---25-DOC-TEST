# 14. Non-Functional Requirements (NFR) Specification

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
- Do NOT write an NFR without a measurable metric and target — "the system shall be fast" is not an NFR.
- Do NOT prescribe specific infrastructure sizing (no "4 CPU cores", no "16GB RAM") unless evidenced.
- Do NOT skip the measurement method — every NFR must state how compliance will be verified.
- Do NOT create NFR-* IDs that conflict with BR-* or BR-SEC-* series.
- Do NOT assume NFR targets without evidence — mark as ASSUMED with low confidence and escalate.

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
| Document Type | `14. Non-Functional Requirements (NFR) Specification` |
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
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 11 Non-Functional | YES |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Security requirements | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 12_TECHNOLOGY_BLUEPRINT | Section 15–16 Availability/Scalability | Architecture constraints |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: NFR |
| 18_DEPLOYMENT_ARCHITECTURE_DOCUMENT | Sections 15–17 | Deployment constraints |
| 24_TRACEABILITY_MATRIX | All NFR-* IDs | Traceability |

## 1. Purpose and Scope [M]
## 2. Quality Model and Classification [M]
## 3. NFR Identification Rules [M]
## 4. Performance Efficiency [M]
### 4.1 Response Time
### 4.2 Throughput
### 4.3 Capacity
### 4.4 Resource Utilization

## 5. Compatibility / Interoperability [C]
## 6. Usability / Interaction Capability [M]
## 7. Reliability [M]
### 7.1 Availability
### 7.2 Fault Tolerance
### 7.3 Recoverability

## 8. Security [M]

> **Cross-reference:** Security NFRs here must align with BR-SEC-* requirements in 13_SECURITY_ARCHITECTURE Section 19. If a security NFR contradicts a BR-SEC-*, flag as CONTRADICTED and escalate to CISO.

## 9. Maintainability [M]
## 10. Flexibility / Adaptability [C]
## 11. Scalability [M]
## 12. Resilience / Continuity [M]
## 13. Data Quality / Integrity [M]
## 14. Auditability / Traceability [M]
## 15. Accessibility [C]
## 16. Compliance / Retention [C]

## 17. NFR Record [M]

> **Cross-reference:** NFR-* IDs defined here feed into 12_TECHNOLOGY_BLUEPRINT Sections 15–16, 18_DEPLOYMENT_ARCHITECTURE Sections 15–17, and 17_READINESS_REPORT Section 12. Every NFR-* must appear in 24_TRACEABILITY_MATRIX.

For every `NFR-*`: statement, rationale, metric, target, threshold, conditions/workload, measurement method, verification method, priority, owner, evidence.

### Worked Example Rows — NFR (generic, based on ISO/IEC 25010 quality model)
| ID | Quality Characteristic | Sub-characteristic | Statement | Metric | Target | Threshold | Measurement Method | Priority | Evidence Class |
|---|---|---|---|---|---|---|---|---|---|
| `NFR-001` | Performance Efficiency | Time Behaviour | The system shall respond to {OPERATION} within {LATENCY_MS} ms under {LOAD_CONDITION}. | Response time (p95) | ≤ {TARGET_MS} ms | ≤ {THRESHOLD_MS} ms | Load test with {CONCURRENT_USERS} concurrent users | High | INFERRED |
| `NFR-002` | Reliability | Availability | The system shall be available ≥ {AVAILABILITY}% measured monthly excluding planned maintenance. | Monthly uptime % | ≥ {TARGET}% | ≥ {MINIMUM}% | Uptime monitoring | High | INFERRED |
| `NFR-003` | Security | Confidentiality | All {SENSITIVE_DATA_TYPE} data shall be encrypted at rest using an industry-standard symmetric algorithm with key length ≥ {KEY_LENGTH} bits. | Encryption coverage | 100% | 100% | Security scan + DBA verification | Critical | OBSERVED |
| `NFR-004` | Maintainability | Modifiability | Any single {MODULE_TYPE} shall be modifiable without requiring changes to more than {COUPLING_THRESHOLD} other modules. | Efferent coupling | ≤ {TARGET} | ≤ {THRESHOLD} | Static analysis | Medium | INFERRED |
| `NFR-005` | Usability | Learnability | A new {ACTOR_ROLE} shall be able to complete {CORE_TASK} without assistance within {ONBOARDING_TIME} of initial access. | Task completion time | ≤ {TARGET} minutes | ≤ {THRESHOLD} minutes | Usability testing | Medium | ASSUMED |

> **Section passes QA when:** Every NFR-* has quality characteristic (ISO 25010), sub-characteristic, statement, metric, target value, threshold value, measurement method, and verification method. No NFR lacks a measurable target.

## 18. NFR Acceptance Criteria [M]
## 19. NFR Verification Matrix [M]
## 20. NFR Traceability [M]

Use ISO/IEC 25010 as a quality-model reference, tailored to the product/system context.


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
| NFR catalog completeness (all ISO 25010 dimensions addressed) | 20% | | | |
| Measurable targets and thresholds defined for all NFRs | 30% | | | |
| Measurement and verification methods specified | 20% | | | |
| Security NFRs aligned with security architecture | 15% | | | |
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
