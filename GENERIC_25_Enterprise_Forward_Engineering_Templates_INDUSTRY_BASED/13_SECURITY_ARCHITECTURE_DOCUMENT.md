# 13. Security Architecture Document

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
- Do NOT prescribe specific security products (no specific WAF, SIEM, HSM vendors).
- Do NOT use BR-xxx IDs for security defects — use BR-SEC-xxx exclusively for security issues.
- Do NOT omit the threat model — it is mandatory regardless of evidence availability.
- Do NOT prescribe a specific cryptographic algorithm implementation (no bcrypt, no Argon2 by name) — use "industry-standard password hashing algorithm" instead.
- Do NOT classify data sensitivity without evidence — use INFERRED with low confidence if guessing.

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
| Document Type | `13. Security Architecture Document` |
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
| 01_BUSINESS_REQUIREMENTS_DOCUMENT | Section 4 Policies | YES |
| 06_DATA_DICTIONARY | Section 8 Sensitive Data | YES |
| 07_DATA_MODEL_SPECIFICATION | Section 14 Data Classification | YES |
| 03_USE_CASE_SPECIFICATION | Section 12 Auth requirements | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 12_TECHNOLOGY_BLUEPRINT | Section 13 Security Summary | Architecture alignment |
| 14_NFR_SPECIFICATION | Section 8 Security NFRs | NFR source |
| 18_DEPLOYMENT_ARCHITECTURE_DOCUMENT | Section 11 Security Boundaries | Deployment scoping |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Security |
| 24_TRACEABILITY_MATRIX | All BR-SEC-* IDs | Security traceability |

## 1. Purpose and Scope [M]
## 2. Security Objectives [M]
## 3. Security Principles [M]
## 4. Security Boundary and Context [M]
## 5. Assets and Information [M]
## 6. Data / Information Classification [M]
## 7. Threat Model [M]

> **Cross-reference:** Threat actors here must include all actors from 03_USE_CASE_SPECIFICATION Section 3. Attack surfaces must cover all interfaces in 11_API_CONTRACT Section 4 and all data flows in 09_DFD Section 13 (Sensitive Data Flows).

### 7.1 Threat Actors
### 7.2 Attack Surfaces
### 7.3 Threat Scenarios
### 7.4 Trust Boundaries
### 7.5 Risk Assessment

> **Section passes QA when:** At least 3 threat scenarios are documented. Each scenario has a threat actor, attack surface, impact, and likelihood. Trust boundaries are defined.

## 8. Identity Architecture [M]
## 9. Authentication [M]
## 10. Authorization [M]
### 10.1 Roles / Permissions
### 10.2 Privilege Management
### 10.3 Segregation of Duties [C]

## 11. Data Protection [M]
## 12. Application / Component Security [M]
## 13. Interface / Integration Security [M]
## 14. Audit and Accountability [M]
## 15. Security Monitoring [C]
## 16. Incident / Response Requirements [C]
## 17. Privacy Requirements [C]
## 18. Security Controls [M]
## 19. Security Requirements [M]

> **Cross-reference:** Every BR-SEC-* defined here is a security defect or requirement from the source system. These IDs must appear in 24_TRACEABILITY_MATRIX and must NEVER overlap with BR-xxx requirement IDs from 01_BRD.md.

### Worked Example Row — Security Requirement (generic)
| Field | Example Value |
|---|---|
| ID | `BR-SEC-001` |
| Category | Authentication / Authorization / Data Protection / Audit / Cryptography / Input Validation |
| Statement | The system shall {SECURITY_REQUIREMENT_STATEMENT}. |
| Rationale | {THREAT_OR_RISK} identified in source system — see `THR-001`. |
| Linked Threat | `THR-001 {THREAT_NAME}` |
| Current State (Source) | {DESCRIPTION_OF_CURRENT_VULNERABLE_IMPLEMENTATION} |
| Target State | {DESCRIPTION_OF_REQUIRED_SECURE_IMPLEMENTATION — technology-neutral} |
| Verification | {HOW_TO_VERIFY_COMPLIANCE} |
| Priority | Critical / High / Medium / Low |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {VULNERABLE_CODE_LOCATION}` |
| Confidence | 0.90 |

| Field | Example Value — Data Protection Requirement |
|---|---|
| ID | `BR-SEC-002` |
| Category | Data Protection |
| Statement | All {SENSITIVE_DATA_TYPE} data transmitted between {SOURCE} and {DESTINATION} shall use industry-standard transport encryption. |
| Rationale | `THR-002` — data in transit currently unencrypted — identified in {SOURCE_FILE}. |
| Current State | {DESCRIPTION_OF_UNENCRYPTED_TRANSMISSION} |
| Target State | All {DATA_TYPE} transmissions must use a current industry-standard encryption protocol. |
| Priority | High |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / line {LINE}` |
| Confidence | 0.88 |

> **Section passes QA when:** Every BR-SEC-* has a current-state description (the vulnerability), a target-state requirement (the fix), a priority, and a source reference. No BR-SEC-* overlaps with any BR-* from 01_BRD.

## 20. Security Verification and Evidence [M]
## 21. Residual Risks [M]
## 22. Compliance Mapping [C]


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
| Threat model completeness (actors, surfaces, scenarios) | 20% | | | |
| Security requirements (BR-SEC-*) completeness | 25% | | | |
| Data classification coverage | 15% | | | |
| Identity, authentication, and authorization model | 15% | | | |
| Audit and accountability requirements | 10% | | | |
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
