# 11. API Contract Specification

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
- Do NOT prescribe a protocol (REST, gRPC, SOAP) — leave protocol as a target team decision.
- Do NOT invent request or response fields not evidenced in source procedures or data dictionary.
- Do NOT skip the error model — every operation must have at least one error response defined.
- Do NOT omit audit requirements — every state-changing operation must log caller identity and timestamp.
- Do NOT reference DE-* fields that are not defined in 06_DATA_DICTIONARY.

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
| Document Type | `11. API Contract Specification` |
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
| 10_SERVICE_CATALOG | All SVC-* entries | YES |
| 06_DATA_DICTIONARY | All data elements | YES |
| 07_DATA_MODEL_SPECIFICATION | Entity schemas | YES |

### Downstream
| Document | Sections Consumed | Purpose |
|---|---|---|
| 12_TECHNOLOGY_BLUEPRINT | Integration layer | Architecture input |
| 13_SECURITY_ARCHITECTURE_DOCUMENT | Section 13 Interface Security | Security scoping |
| 19_FRONTEND_ARCHITECTURE_DOCUMENT | Section 11 Data Interaction | Client-API binding |
| SCHEMA_MIGRATION_SCRIPTS | Schema deltas | Migration planning |
| 24_TRACEABILITY_MATRIX | All interface IDs | Traceability |

## 1. API Purpose and Scope [M]
## 2. API Consumers and Providers [M]
## 3. API Principles and Conventions [M]
## 4. API Inventory [M]
## 5. Interface / Operation Specification [M]

> **Cross-reference:** Every IF-*/OP-* here must map to a SVC-* in 10_SERVICE_CATALOG. Request/response field types must match DE-* definitions in 06_DATA_DICTIONARY. Auth requirements must align with 13_SECURITY_ARCHITECTURE Section 9.

### Worked Example Row (generic)
| Field | Example Value |
|---|---|
| Interface ID | `IF-001` |
| Operation ID | `OP-001` |
| Business Capability | `CAP-001 — {CAPABILITY_NAME}` |
| Endpoint / Identifier | `{INTERFACE_IDENTIFIER}` (protocol TBD by target team) |
| Method / Interaction | {INTERACTION_PATTERN} (synchronous request/response) |
| Request Fields | `{ENTITY_ID}` (required, {TYPE}); `{FIELD_1}` (required, {TYPE}); `{FIELD_2}` (optional, {TYPE}) |
| Validation | {ENTITY_ID} must resolve to an existing active {ENTITY}; {FIELD_1} in [{VALUE_LIST}]. |
| Response — Success | `{RESULT_FIELD_1}` ({TYPE}), `{RESULT_FIELD_2}` ({TYPE}), `transactionId` (UUID) |
| Response — Error | `errorCode`: {ERR_CODE}; `errorMessage`: human-readable; `traceId`: correlation ID |
| Authentication | Caller must present valid session credential with {PRIVILEGE_NAME} privilege. |
| Audit | Log caller identity, timestamp, {ENTITY_ID}, outcome on every invocation. |
| Idempotency | Retry-safe via `transactionId`; duplicate submission returns original result. |
| SLA | ≤ {LATENCY_MS} ms p95; ≥ {AVAILABILITY}% availability |
| Related Business Rules | `BRL-001`, `BRL-003` |
| Evidence Class | OBSERVED |
| Source Reference | `{SOURCE_FILE} / {PACKAGE}.{PROCEDURE}` |
| Confidence | 0.87 |

| Field | Example Value — Query Operation |
|---|---|
| Interface ID | `IF-002` |
| Operation ID | `OP-002` |
| Business Capability | `CAP-002 — {CAPABILITY_NAME_2}` |
| Method / Interaction | {READ_INTERACTION_PATTERN} (synchronous query) |
| Request Fields | `{FILTER_FIELD_1}` (optional, {TYPE}); `{FILTER_FIELD_2}` (optional, {TYPE}); `pageSize` (optional, integer, default 20) |
| Validation | At least one filter field required; pageSize ≤ 100. |
| Response — Success | Array of `{ENTITY}` records: [{FIELD_1}, {FIELD_2}, {STATUS}]; `totalCount`; `pageToken` |
| Response — Error | `ERR-003` NO_RESULTS; `ERR-004` INVALID_FILTER |
| Authentication | Read privilege required. |
| Audit | Log query parameters and result count. Do not log sensitive field values. |
| Evidence Class | DERIVED |
| Confidence | 0.80 |

> **Section passes QA when:** Every operation has request schema, response schema (success + error), authentication requirement, audit requirement, SLA, and a link to its SVC-* in the service catalog.

### 5.1 Interface and Operation IDs
### 5.2 Business Capability / Operation
### 5.3 Endpoint or Interface Identifier
### 5.4 Method / Interaction
### 5.5 Request
### 5.6 Parameters / Headers
### 5.7 Request Schema
### 5.8 Validation
### 5.9 Response Schema
### 5.10 Error Model
### 5.11 Authentication / Authorization
### 5.12 Audit
### 5.13 Idempotency / Duplicate Handling [C]
### 5.14 Concurrency / Transaction Semantics [C]
### 5.15 Pagination / Filtering / Sorting [C]
### 5.16 Versioning / Compatibility

## 6. Shared Schemas [M]
## 7. Shared Error Definitions [M]
## 8. Security Model [M]
## 9. Data Mapping [M]

> **Cross-reference:** Every field in request/response schemas must have a corresponding DE-* in 06_DATA_DICTIONARY. Do not introduce fields here that are not in the data dictionary.

## 10. Contract Lifecycle [M]
## 11. Contract Validation [M]
## 12. API-to-Service Mapping [M]
## 13. API-to-Use-Case / Requirement Mapping [M]

The contract may be serialized separately in a formal, language-agnostic API description such as OpenAPI when the interface style is HTTP.


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
| Interface inventory completeness (all operations catalogued) | 20% | | | |
| Request and response schema completeness | 25% | | | |
| Error model coverage | 15% | | | |
| Security model (auth, audit) | 15% | | | |
| SLA and quality requirements defined | 10% | | | |
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
