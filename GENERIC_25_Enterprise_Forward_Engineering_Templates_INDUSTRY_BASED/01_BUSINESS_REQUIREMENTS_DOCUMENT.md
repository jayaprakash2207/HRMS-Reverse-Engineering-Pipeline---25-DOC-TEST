# 1. Business Requirements Document (BRD)

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
- Do NOT prescribe technology solutions (no React, no PostgreSQL, no AWS) — this is a business document.
- Do NOT copy a requirement from the source code without linking it to a BR-* ID.
- Do NOT invent business rules that cannot be traced to source evidence — mark as ASSUMED if needed.
- Do NOT put data model details here — those belong in 06_DATA_DICTIONARY and 07_DATA_MODEL_SPECIFICATION.
- Do NOT merge BR-xxx (requirements) and BR-SEC-xxx (security defects) — they are separate ID series.
- Do NOT mark a section NOT_AVAILABLE without specifying which stakeholder must supply the missing content.

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
| Document Type | `1. Business Requirements Document (BRD)` |
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

### Upstream — must exist before this document can be completed
| Document | Required Sections | Blocking? |
|---|---|---|
| Source system artifacts / evidence | All available | YES — this is the primary input |

### Downstream — this document feeds into
| Document | Sections Consumed | Purpose |
|---|---|---|
| 02_BUSINESS_CAPABILITY_MODEL | Section 5 Capabilities | Capability identification |
| 03_USE_CASE_SPECIFICATION | Section 7 Functional Requirements | Use case derivation |
| 04_BUSINESS_PROCESS_MODEL | Section 6 Processes | Process reconstruction |
| 10_SERVICE_CATALOG | Section 7 Functional Requirements | Service identification |
| 13_SECURITY_ARCHITECTURE | Section 4 Policies, Section 7 Functional | Security requirement source |
| 14_NFR_SPECIFICATION | Section 11 Non-Functional | NFR source |
| 15_FORWARD_ENGINEERING_SPECIFICATION | All sections | Primary input |
| 17_FORWARD_ENGINEERING_READINESS_REPORT | All sections | Readiness dimension: Business Requirements |
| 24_TRACEABILITY_MATRIX | All BR-* IDs | Traceability anchor |

## 1. Executive Summary [M]
### 1.1 Business Context
### 1.2 Business Problem / Opportunity
### 1.3 Business Objectives
### 1.4 Expected Outcomes and Benefits
### 1.5 Success Measures

## 2. Scope and Boundaries [M]
### 2.1 In Scope
### 2.2 Out of Scope
### 2.3 Business Boundary
### 2.4 System/Product Boundary
### 2.5 Organizational/Geographic Boundary [C]

## 3. Stakeholders and Governance [M]
### 3.1 Stakeholder Register
### 3.2 Roles, Responsibilities and Concerns
### 3.3 Decision Rights
### 3.4 Approval and Governance

## 4. Business Context [M]
### 4.1 Operating Context
### 4.2 Business Events and Drivers
### 4.3 External Parties and Dependencies
### 4.4 Policies / Regulatory Context [C]

## 5. Business Capabilities [M]
For each capability capture ID, definition, outcome, owner, criticality, current support, target need, dependencies and evidence.

## 6. Business Processes and Value Streams [M]
Capture process/value-stream ID, objective, trigger, actors, inputs, outputs, controls, decisions, exceptions, KPIs and evidence.

## 7. Functional Business Requirements [M]
> **Cross-reference:** Every BR-* ID defined here is the master. All other documents (03, 10, 11, 13, 14, 15, 24) must reference these exact IDs. Never create a new BR-* in another document.

For each `BR-*`: statement, rationale, actor, trigger, preconditions, inputs, behavior, outcome, business rules, priority, acceptance criteria, evidence, confidence.

### Worked Example Row (generic — replace with project-specific content)
| Field | Example Value |
|---|---|
| ID | `BR-001` |
| Statement | The system shall allow an authorised user to initiate a {PROCESS_NAME} transaction for a given {PRIMARY_ENTITY}. |
| Rationale | Business operation cannot proceed without this action; currently performed manually with no audit trail. |
| Actor | `ACT-002 {ROLE_NAME}` |
| Trigger | User selects "{ACTION}" on the {PRIMARY_ENTITY} record. |
| Preconditions | {PRIMARY_ENTITY} status = ACTIVE; actor holds {ROLE_NAME} privilege. |
| Inputs | {PRIMARY_ENTITY} identifier, {KEY_FIELD}, effective date. |
| Behavior | System validates inputs, applies {BUSINESS_RULE_ID}, records the transaction, updates status, and emits an audit event. |
| Outcome | Transaction recorded; status updated; audit log entry created; confirmation returned to actor. |
| Business Rules Applied | `BRL-001`, `BRL-005` |
| Priority | Must Have (MoSCoW) |
| Acceptance Criteria | Given a valid {PRIMARY_ENTITY} record and authorised actor, when the action is invoked, then the transaction is persisted and status updated within 3 seconds with an audit entry. |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {OBJECT} / line {LINE}` |
| Confidence | 0.90 |

> **Section passes QA when:** Every BR-* has a statement, actor, trigger, acceptance criteria, evidence class, source reference, and confidence score. No BR-* is missing any of these fields.

## 8. Business Rules and Policies [M]
> **Cross-reference:** BRL-* IDs defined here feed into 03_USE_CASE_SPECIFICATION Section 9, 10_SERVICE_CATALOG Section 3.7, and 11_API_CONTRACT Section 5.8. Use the same BRL-* ID everywhere.

### 8.1 Rule Catalog

#### Worked Example Rows (generic — replace with project-specific content)
| ID | Category | Statement | Trigger | Source | Evidence Class | Confidence |
|---|---|---|---|---|---|---|
| `BRL-001` | Validation | {PRIMARY_ENTITY} {KEY_FIELD} must be unique across all active records. | Record creation / update | `{SOURCE_FILE} / {OBJECT}` | OBSERVED | 0.95 |
| `BRL-002` | Eligibility | A {ACTOR_ROLE} may only act on a {PRIMARY_ENTITY} assigned to their {ORGANIZATIONAL_UNIT}. | Transaction initiation | `{SOURCE_FILE} / {PROCEDURE}` | INFERRED | 0.75 |
| `BRL-003` | Calculation | {DERIVED_VALUE} = {BASE_VALUE} × {RATE_FIELD} / {DIVISOR}. Effective from {EFFECTIVE_DATE_FIELD}. | Calculation event | `{SOURCE_FILE} / line {LINE}` | OBSERVED | 0.90 |
| `BRL-004` | Approval | Any {PROCESS_NAME} above threshold {THRESHOLD_VALUE} requires dual authorisation from {APPROVER_ROLE}. | Transaction submission | `{SOURCE_FILE} / {TRIGGER_NAME}` | INFERRED | 0.70 |
| `BRL-005` | Temporal | {EFFECTIVE_DATE_FIELD} must not precede the {REFERENCE_DATE_FIELD} of the parent {ENTITY_NAME}. | Date entry | `{SOURCE_FILE} / {CONSTRAINT_NAME}` | DERIVED | 0.85 |
| `BRL-006` | Temporal | Effective date of {ENTITY} record must not be in the future at time of creation unless explicitly approved by {APPROVER_ROLE}. | Record creation | `{SOURCE_FILE} / {CONSTRAINT}` | INFERRED | 0.65 |

### 8.2 Eligibility / Decision Rules [C]
### 8.3 Validation Rules
### 8.4 Approval / Control Rules [C]
### 8.5 Calculation / Derivation Rules [C]
### 8.6 Temporal / Effective-Date Rules [C]

> **Section passes QA when:** Every BRL-* has a category (Validation/Calculation/Eligibility/Approval/Temporal), a statement, a source reference, and an evidence class. No invented rules without ASSUMED classification.

## 9. Information and Reporting Requirements [M]
Reports, analytics, operational information, filters, calculations, frequency, audience and security.

## 10. Interface and Dependency Requirements [C]
External parties/systems, information exchanged, timing, failure handling and ownership.

## 11. Non-Functional Business Requirements [M]
Business-level expectations for performance, availability, security, usability, compliance, continuity and other quality needs.

## 12. Assumptions, Constraints and Dependencies [M]
## 13. Risks and Opportunities [M]
## 14. Prioritization [M]
## 15. Acceptance and Approval Criteria [M]
## 16. Requirements Traceability [M]


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
| Business context and objectives completeness | 10% | | | |
| Functional requirements completeness (BR coverage) | 20% | | | |
| Business rules completeness | 15% | | | |
| Evidence quality (OBSERVED / DERIVED ≥ 70%) | 15% | | | |
| Acceptance criteria completeness | 10% | | | |
| Stakeholder and actor identification | 10% | | | |
| Non-functional and regulatory coverage | 10% | | | |
| Traceability to source evidence | 10% | | | |
| **Total** | **100%** | | **/30** | |

**Readiness Decision:**
- ≥ 24/30, no 0s → **READY**
- 18–23/30, no critical 0s → **CONDITIONAL** (list conditions)
- < 18/30 or any critical dimension = 0 → **BLOCKED** (list blockers)

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
- [ ] Readiness score calculated and decision recorded.
- [ ] Artifact is `READY / CONDITIONAL / BLOCKED`.

## Traceability Matrix [M]

| Trace ID | Source | Relationship | Target | Evidence | Confidence | Status |
|---|---|---|---|---|---:|---|
| `TR-001` | `{{SOURCE_ID}}` | `{{RELATIONSHIP}}` | `{{TARGET_ID}}` | `{{EVIDENCE}}` | `0.00` | `{{STATUS}}` |

## References / Standards Basis [M]

Use the standards relevant to this artifact and record their versions in the project standards register. Do not claim that this custom template is itself an official standard.
