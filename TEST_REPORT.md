# TEST REPORT — Oracle HRMS 25 Document Pipeline
### Date: 2026-08-11

---

#### TEST 1 — EXISTENCE CHECK: PASS

All 25 required files exist and are non-empty.

**FWD (20 files):** All present. Sizes range from 10,387 bytes (18_DEPLOYMENT_ARCHITECTURE.md) to 134,786 bytes (17_FORWARD_ENGINEERING_READINESS_REPORT.md). Total FWD payload: ~1.23 MB.

**KG (5 files):** All present. Sizes range from 22,396 bytes (ENTERPRISE_KNOWLEDGE_GRAPH.json) to 144,509 bytes (ARCHITECTURE_INVENTORY.md). Total KG payload: ~464 KB.

Note: An extra file `01_BRD_SUPPLEMENT.md` is present in the FWD folder (not part of the required 25). Outside test scope but flagged for awareness.

---

#### TEST 2 — STRUCTURAL CHECK: PASS (with notes)

**01_BRD.md:**
- "Purpose" as a named section heading: NOT present. Document uses "Executive Summary" (§1) as opening. "Scope" appears as §4. No section literally titled "Purpose."
- Stakeholders: PRESENT — §5 "Stakeholders & User Personas" with §5.1 Stakeholder Register and §5.2 User Personas.
- Functional Requirements: PRESENT — §6 "Business Requirements" / §6.2 Full Business Requirements Register (BR-001 through BR-048+).
- Constraints: PRESENT — §7 "Business Constraints."
- Assumptions: PRESENT — §8 "Business Assumptions & Dependencies" / §8.1 Assumptions.
- NOTE: No section literally titled "Purpose" but content is covered in Executive Summary. Structurally meets intent.

**03_USE_CASE_SPECIFICATION.md:**
- Actor Catalogue: PRESENT — §1
- Use Case Summary Table: PRESENT — §2
- UC-001 through UC-015: ALL PRESENT — §3
- Dependency Diagram: PRESENT — §4
- Business Rule Cross-Reference: PRESENT — §5

**13_SECURITY_ARCHITECTURE.md:**
- Authentication: PRESENT — §1 "[VERIFIED-SUPPLEMENT] 1. Authentication Mechanism"
- Authorization/RBAC: PRESENT — §2 "[VERIFIED-SUPPLEMENT] 2. Authorization Model"
- Encryption: PRESENT — §3 "[VERIFIED-SUPPLEMENT] 3. Encryption and Data Protection" (AES-256 CBC)

**14_NFR_SPECIFICATION.md:**
- Performance section: PRESENT — §1 "Performance Requirements" with response time SLAs, payroll processing targets, throughput, query performance tables
- Security section: PRESENT — §4 "Security Requirements"
- Measurable criteria: PRESENT — §9 "NFR Acceptance Criteria" (PERF-AC-01 through SEC-AC-05, MAINT-AC-01–06)

**17_FORWARD_ENGINEERING_READINESS_REPORT.md:**
- Readiness score/assessment: PRESENT — §2 "Readiness Scorecard" with domain scores. Overall: "CONDITIONAL — NOT READY for immediate code generation."
- Blockers: PRESENT — §4 "Critical Blockers" BLOCKER-01 through BLOCKER-07
- Gaps: PRESENT — §5 Recommended Pre-Generation Actions and §7 Assumptions Requiring Validation

---

#### TEST 3 — GOLDEN SAMPLE FACTS: FAIL (4/6 pass)

**3a — 11_API_CONTRACT_SPECIFICATION.md contains PKG_SECURITY, PKG_PAYROLL, PKG_EMPLOYEE, PKG_LEAVE:**
- PKG_SECURITY: FOUND | PKG_PAYROLL: FOUND | PKG_EMPLOYEE: FOUND | PKG_LEAVE: FOUND
- **PASS**

**3b — 07_DATA_MODEL_SPECIFICATION.md contains EMPLOYEES, SALARY_RECORDS, LEAVE_REQUESTS, PAYROLL_RUNS:**
- EMPLOYEES: FOUND | SALARY_RECORDS: FOUND | LEAVE_REQUESTS: FOUND | PAYROLL_RUNS: FOUND
- **PASS**

**3c — 14_NFR_SPECIFICATION.md contains "30" (timeout) and "6.2" (SS rate):**
- "30": FOUND — line 212: "Current system hard-codes 30-minute session"
- "6.2": NOT FOUND in 14_NFR_SPECIFICATION.md — the 6.2% Social Security rate is only in 03_USE_CASE_SPECIFICATION.md (lines 251, 283). NFR spec contains no payroll tax rate specifications.
- **FAIL — "6.2" absent from 14_NFR_SPECIFICATION.md**

**3d — 13_SECURITY_ARCHITECTURE.md contains "authenticate" and "AES-256":**
- authenticate: FOUND (lines 12, 26, 29, 32, extensively) | AES-256: FOUND (line 30, 64, 131)
- **PASS**

**3e — 03_USE_CASE_SPECIFICATION.md contains "BR-042", "HEAD_OF_HOUSEHOLD", "1.0" and "5.0":**
- BR-042: FOUND (lines 594, 609, 636, 640, 1076)
- HEAD_OF_HOUSEHOLD: FOUND (lines 196, 214, 268, 285, 922)
- 1.0 and 5.0: FOUND (lines 501, 514, 526 — "OVERALL_RATING (1.0–5.0 range)")
- **PASS**

**3f — 19_FRONTEND_ARCHITECTURE.md contains "HRMS_EMPLOYEE" and "HRMS_PAYROLL":**
- HRMS_EMPLOYEE: NOT FOUND — document maps to SPA route `/employees`, not Oracle Forms module name
- HRMS_PAYROLL: NOT FOUND — document maps to SPA route `/payroll`, not Oracle Forms module name
- **FAIL — Neither Oracle Forms module name appears in Frontend Architecture doc**

---

#### TEST 4 — NO ARTIFACT TEXT: FAIL

AI artifact text found in at least 18 of 25 documents.

**"Looking at the source content"** found in:
- 01_BRD.md (line 48), 04_BUSINESS_PROCESS_MODEL.md (lines 43, 45, 52, 410, 412), 07_DATA_MODEL_SPECIFICATION.md (lines 248, 252, 1228), 09_DATA_FLOW_DIAGRAM.md (lines 5, 8, 18, 1147, 1197), 11_API_CONTRACT_SPECIFICATION.md (lines 41, 2013, 2088), 12_TECHNOLOGY_BLUEPRINT.md (lines 8, 12, 830, 832, 836), 13_SECURITY_ARCHITECTURE.md (line 193), 14_NFR_SPECIFICATION.md (lines 233, 701, 733, 768), 15_FORWARD_ENGINEERING_SPECIFICATION.md (lines 37, 55, 1132), ARCHITECTURE_INVENTORY.md (lines 29, 548, 823, 842, 876), CANONICAL_ENTERPRISE_MODEL.md (line 248), FORWARD_ENGINEERING_INPUT_MAP.md (lines 1, 13)

**"Here is the updated snippet"** found in:
- 01_BRD.md (line 54), 01_BRD_SUPPLEMENT.md (line 5), 02_BUSINESS_CAPABILITY_MODEL.md (line 728), 04_BUSINESS_PROCESS_MODEL.md (lines 402, 485), 06_DATA_DICTIONARY.md (lines 325, 609), 07_DATA_MODEL_SPECIFICATION.md (line 1242), 09_DATA_FLOW_DIAGRAM.md (lines 1, 14, 1149, 1157, 1199), 11_API_CONTRACT_SPECIFICATION.md (line 2058), 12_TECHNOLOGY_BLUEPRINT.md (line 10), 14_NFR_SPECIFICATION.md (lines 703, 778), 15_FORWARD_ENGINEERING_SPECIFICATION.md (line 1098), 17_FORWARD_ENGINEERING_READINESS_REPORT.md (lines 53, 607, 649, 666, 687, 722, 775, 804, 828, 860), ARCHITECTURE_INVENTORY.md (line 842), FORWARD_ENGINEERING_INPUT_MAP.md (lines 3, 9, 19, 25, 31)

**"Updated snippet"** found in:
- 04_BUSINESS_PROCESS_MODEL.md (line 422), 07_DATA_MODEL_SPECIFICATION.md (line 1486)

**`<!-- GAP-FILLED SECTION -->`** (HTML comment) found in:
- 01_BRD.md, 02_BUSINESS_CAPABILITY_MODEL.md, 04_BUSINESS_PROCESS_MODEL.md, 06_DATA_DICTIONARY.md, 07_DATA_MODEL_SPECIFICATION.md, 09_DATA_FLOW_DIAGRAM.md, 11_API_CONTRACT_SPECIFICATION.md, 12_TECHNOLOGY_BLUEPRINT.md, ARCHITECTURE_INVENTORY.md

**"I'll now read"** and **"Let me check"**: NOT found in any document.

---

#### TEST 5 — NO DUPLICATE SECTIONS: FAIL (1 document fails)

**03_USE_CASE_SPECIFICATION.md:** No duplicate headings. PASS.
**07_DATA_MODEL_SPECIFICATION.md:** No duplicate headings. PASS.
**13_SECURITY_ARCHITECTURE.md:** No duplicate headings. PASS.
**14_NFR_SPECIFICATION.md:** No duplicate headings. PASS.

**01_BRD.md: FAIL**
- `### 2.1 System History` appears at lines 64, 472, and 492 — triplicated
- `### 2.2 Drivers for Modernisation` appears at lines 70, 478, and 498 — triplicated
- Root cause: Section 2 content was injected three times during pipeline gap-fill operations

---

#### TEST 6 — CROSS-DOCUMENT ID VALIDATION: FAIL

**6a — BR-xxx IDs from 03_USE_CASE_SPECIFICATION.md verified in 01_BRD.md:**

Checked: BR-001, BR-002, BR-003, BR-019, BR-042

- BR-001: FOUND in BRD (COBRA notification — consistent). PASS.
- BR-002: FOUND in BRD (calculate_final_pay — consistent). PASS.
- BR-003: FOUND in BRD (password verification — consistent). PASS.
- BR-019: FOUND in BRD (session timeout — consistent). PASS.
- BR-042: **ID COLLISION DEFECT**
  - In 03_USE_CASE_SPECIFICATION.md: BR-042 = "CRITICAL DEFECT — Password is NEVER verified" (authentication bypass)
  - In 01_BRD.md line 299: BR-042 = "The system shall support off-cycle payroll runs for terminated employees"
  - Same ID refers to two completely different things in two core documents
  - All downstream documents (14_NFR, 17_READINESS_REPORT, 13_SECURITY) treat BR-042 as the authentication defect, making the BRD the outlier

**6a RESULT: FAIL — BR-042 ID collision between BRD and all other documents**

**6b — UC-xxx IDs verified across documents:**
No documents outside 03_USE_CASE_SPECIFICATION.md reference UC-xxx IDs. No broken UC references. **PASS.**

**6c — 5 table names from 11_API_CONTRACT_SPECIFICATION.md verified in 07_DATA_MODEL_SPECIFICATION.md:**
- PAYROLL_RUNS: FOUND. PASS.
- USER_SESSIONS: FOUND. PASS.
- EMPLOYEES: FOUND. PASS.
- LEAVE_BALANCES: FOUND. PASS.
- PERFORMANCE_REVIEWS: FOUND. PASS.

**6c RESULT: PASS**

---

#### TEST 7 — SOURCE TRACEABILITY: PASS

- **01_BRD.md:** 18 source matches — references PKG_SECURITY, PKG_EMPLOYEE, PKG_PAYROLL, PKG_AUDIT, EMPLOYEES, USER_SESSIONS. PASS.
- **07_DATA_MODEL_SPECIFICATION.md:** 131 source matches — entire document sourced from real Oracle schema. PASS.
- **11_API_CONTRACT_SPECIFICATION.md:** 23 source matches — PKG_PAYROLL, PAYROLL_RUNS, USER_SESSIONS, PKG_VALIDATION, PKG_INTEGRATION, PKG_SECURITY. PASS.
- **13_SECURITY_ARCHITECTURE.md:** 47 source matches — PKG_SECURITY, EMPLOYEES, USER_SESSIONS, AES-256, MD5. PASS.
- **14_NFR_SPECIFICATION.md:** 42 source matches — PKG_PAYROLL, PKG_AUDIT, EMPLOYEES, PAYROLL_DETAILS, BR-042. PASS.
- **19_FRONTEND_ARCHITECTURE.md:** 5 source matches — references Oracle Forms conceptually, PKG_SECURITY (via "Replaces PKG_SECURITY.authenticate()"). Marginal but meets minimum threshold. PASS.

---

#### TEST 8 — COMPLETENESS COVERAGE: PASS

All 20 entities found in at least one document.

**Packages:**
| Entity | Found | Documents |
|---|---|---|
| PKG_EMPLOYEE | YES | 03_USE_CASE_SPECIFICATION.md, 01_BRD.md, others |
| PKG_PAYROLL | YES | 01_BRD.md, 02_BUSINESS_CAPABILITY_MODEL.md, 10+ others |
| PKG_SECURITY | YES | 01_BRD.md, 03_USE_CASE_SPECIFICATION.md, 13_SECURITY_ARCHITECTURE.md |
| PKG_LEAVE | YES | 03_USE_CASE_SPECIFICATION.md, 10_SERVICE_CATALOG.md, others |
| PKG_PERFORMANCE | YES | 01_BRD.md, 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md |
| PKG_REPORTING | YES | 01_BRD.md, 02_BUSINESS_CAPABILITY_MODEL.md, others |
| PKG_INTEGRATION | YES | 01_BRD.md, 02_BUSINESS_CAPABILITY_MODEL.md, others |
| PKG_NOTIFICATION | YES | 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, others |

**Forms:**
| Entity | Found | Documents |
|---|---|---|
| HRMS_EMPLOYEE | YES | 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, 09_DATA_FLOW_DIAGRAM.md |
| HRMS_PAYROLL | YES | 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, 09_DATA_FLOW_DIAGRAM.md |
| HRMS_LEAVE | YES | 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, 09_DATA_FLOW_DIAGRAM.md |
| HRMS_PERFORMANCE | YES | 02_BUSINESS_CAPABILITY_MODEL.md, 04_BUSINESS_PROCESS_MODEL.md, 09_DATA_FLOW_DIAGRAM.md |
| HRMS_LOGIN | YES | 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, 09_DATA_FLOW_DIAGRAM.md |
| HRMS_MENU | YES | 12_TECHNOLOGY_BLUEPRINT.md (sparse — found in 1 document only) |

**Tables:**
| Entity | Found | Documents |
|---|---|---|
| EMPLOYEES | YES | 01_BRD.md, 07_DATA_MODEL_SPECIFICATION.md, 15+ others |
| SALARY_RECORDS | YES | 01_BRD_SUPPLEMENT.md, 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, 07_DATA_MODEL_SPECIFICATION.md |
| LEAVE_REQUESTS | YES | 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, 07_DATA_MODEL_SPECIFICATION.md |
| PAYROLL_RUNS | YES | 01_BRD.md, 07_DATA_MODEL_SPECIFICATION.md, 11_API_CONTRACT_SPECIFICATION.md |
| PERFORMANCE_REVIEWS | YES | 01_BRD.md, 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md, 07_DATA_MODEL_SPECIFICATION.md |
| AUDIT_LOG | YES | 01_BRD.md, 02_BUSINESS_CAPABILITY_MODEL.md, 03_USE_CASE_SPECIFICATION.md |

Note: HRMS_MENU coverage is sparse (1 document). Not a failure but worth noting.

---

#### TEST 9 — CONTRADICTION CHECK: PASS (with advisory)

| Value | Expected | Documents Checked | Result |
|---|---|---|---|
| Session timeout | 30 minutes | 13_SECURITY_ARCHITECTURE.md (line 19), 03_USE_CASE_SPECIFICATION.md (line 634), 01_BRD.md (line 268) | CONSISTENT — all agree legacy timeout = 30 min. NFR proposes 15 min for NEW system but explicitly labels it as new-system target — not a contradiction. |
| Social Security rate | 6.2% | 03_USE_CASE_SPECIFICATION.md (lines 251, 283) | CONSISTENT — only one document states it; no contradicting value found elsewhere. |
| Medicare rate | 1.45% | 03_USE_CASE_SPECIFICATION.md (line 284) | CONSISTENT — only one document states it; no contradicting value found elsewhere. |
| Rating range | 1.0–5.0 | 03_USE_CASE_SPECIFICATION.md (lines 501, 514, 526) | CONSISTENT — other docs reference OVERALL_RATING without specifying range; no contradictions. |
| BR-042 = critical defect | All docs calling it critical agree | 03_USE_CASE_SPECIFICATION.md, 14_NFR_SPECIFICATION.md, 17_FORWARD_ENGINEERING_READINESS_REPORT.md | CONSISTENT where mentioned. BRD assigns BR-042 to a different requirement entirely (ID collision already flagged in Test 6). |

Advisory: BR-042 ID collision is a metadata inconsistency (same ID = two different things), not a value contradiction. No document claims password bypass is NOT critical.

---

#### TEST 10 — FORWARD ENGINEERING READINESS GATE: PASS

- **Readiness score present:** YES — §2.1 Domain-by-Domain Scorecard. Overall: "CONDITIONAL — NOT READY for immediate code generation." §12: "Current Status: NO-GO."
- **Blockers listed:** YES — BLOCKER-01 through BLOCKER-07 each with severity, evidence, finding, resolution required.
- **BR-042 unresolved:** YES — BLOCKER-01 "Authentication Bypass" cites "Evidence: BR-042." Explicitly unresolved.
- **Does NOT falsely claim ready:** CONFIRMED — "NO-GO" language confirmed. No "fully ready" or "no blockers" text found.

---

## OVERALL SUMMARY

| # | Test | Result |
|---|---|---|
| 1 | Existence Check | **PASS** |
| 2 | Structural Check | **PASS** (minor: no "Purpose" heading in BRD) |
| 3 | Golden Sample Facts | **FAIL** (4/6 pass — "6.2" absent from NFR, HRMS_EMPLOYEE/HRMS_PAYROLL absent from Frontend doc) |
| 4 | No Artifact Text | **FAIL** (18+ of 25 documents contaminated) |
| 5 | No Duplicate Sections | **FAIL** (01_BRD.md has triplicated Section 2 headings) |
| 6 | Cross-Document ID Validation | **FAIL** (BR-042 ID collision: BRD vs all other documents) |
| 7 | Source Traceability | **PASS** |
| 8 | Completeness Coverage | **PASS** |
| 9 | Contradiction Check | **PASS** (with advisory on BR-042 ID collision) |
| 10 | Forward Engineering Readiness Gate | **PASS** |

**Tests passed: 6/10**  
**Tests failed: 4/10**

---

## CRITICAL FAILURES

### 1. Test 4 — AI Artifact Text in 18+ of 25 Documents (BLOCKING)

Raw AI generation process text is embedded directly in document bodies. This is a pipeline output-cleaning failure.

Artifacts found:
- `"Looking at the source content"` — 12 documents
- `"Here is the updated snippet"` — 15+ documents (17_FORWARD_ENGINEERING_READINESS_REPORT.md has 8+ occurrences alone)
- `"Updated snippet"` — 2 documents
- `<!-- GAP-FILLED SECTION -->` HTML comments — 9 documents

**Impact:** When these documents are fed to the forward engineering code generator, the AI will read "Looking at the source content to find any reference to EMPLOYEE_BANK_ACCOUNTS" as if it were a business requirement. These artifacts corrupt the signal.

**Fix required:** Post-processing script to strip all artifact strings from all 25 documents.

---

### 2. Test 5 — Duplicate Sections in 01_BRD.md (BLOCKING)

`### 2.1 System History` and `### 2.2 Drivers for Modernisation` each appear 3 times (lines 64/472/492 and 70/478/498).

**Impact:** The BRD is non-compliant for document delivery. Section 2 content was injected three times during pipeline gap-fill operations.

**Fix required:** Remove the two duplicate injections of Section 2 content from 01_BRD.md.

---

### 3. Test 6 — BR-042 ID Collision (CRITICAL — requires human decision)

`01_BRD.md` line 299 assigns BR-042 = "off-cycle payroll runs for terminated employees."  
All other documents (03_USE_CASE_SPECIFICATION.md, 14_NFR_SPECIFICATION.md, 17_FORWARD_ENGINEERING_READINESS_REPORT.md, 13_SECURITY_ARCHITECTURE.md) assign BR-042 = "authentication bypass — password never verified."

**Impact:** Anyone following BR-042 from the BRD finds a payroll requirement instead of the most critical security defect in the system. This will cause the authentication bypass to be treated as a payroll feature during forward engineering.

**Fix required:** Human decision — renumber one BR-042 to eliminate the collision. Recommendation: keep BR-042 = authentication defect (matches majority of documents), renumber BRD's off-cycle payroll requirement to BR-049 or next available.

---

## WARNINGS

1. **Test 3c — Social Security rate (6.2%) absent from NFR spec.** Rate is correctly documented in 03_USE_CASE_SPECIFICATION.md but not cross-referenced in the NFR compliance section despite SOX compliance being mentioned.

2. **Test 3f — HRMS_EMPLOYEE / HRMS_PAYROLL absent from 19_FRONTEND_ARCHITECTURE.md.** Frontend doc maps Oracle Forms to SPA routes but never names the original Oracle Forms modules. A form-to-feature traceability section is missing.

3. **17_FORWARD_ENGINEERING_READINESS_REPORT.md structural noise.** Multiple identical "Integration Completeness" table rows (35/100, with full GAP-FILLED content) appear at least 8 times. Multi-pass merge artifact where each pass appended rather than replaced.

4. **19_FRONTEND_ARCHITECTURE.md thinness.** At 11,814 bytes, this is one of the smallest documents and has the weakest source traceability (5 source references vs. 47 in Security Architecture).

5. **HRMS_MENU sparse coverage.** Oracle Forms menu module found in only 1 document (12_TECHNOLOGY_BLUEPRINT.md). Consider whether this is sufficient for forward engineering the navigation layer.

---

## ITEMS REQUIRING HUMAN RESOLUTION BEFORE FORWARD ENGINEERING

| # | Item | Type |
|---|---|---|
| 1 | BR-042 ID renumbering — BRD vs all other documents | **Human decision — affects all security cross-references** |
| 2 | Artifact text cleanup script — strip from all 25 documents | Technical cleanup — can be scripted |
| 3 | 01_BRD.md Section 2 deduplication — remove 2 of 3 injections | Technical cleanup — file edit |
| 4 | BLOCKER-01: Authentication architecture decision (fix PKG_SECURITY / LDAP / OAuth2) | Stakeholder decision |
| 5 | BLOCKER-02/04: Direct deposit and final pay calculation policies | Legal/Payroll decision |
| 6 | BLOCKER-03: COBRA notification policy and timing | Legal/HR decision |
| 7 | BLOCKER-05: AES-256 key migration and re-encryption plan | Security/Architecture decision |
| 8 | Add Oracle Forms-to-SPA mapping section to 19_FRONTEND_ARCHITECTURE.md | Pipeline enhancement |
| 9 | Add payroll tax rates (6.2%, 1.45%) to 14_NFR_SPECIFICATION.md compliance section | Document update |

---

## RECOMMENDATION: NOT READY FOR FORWARD ENGINEERING

**Reason:** Two test categories (Tests 4 and 5) represent pipeline output quality failures that must be corrected before documents can be used as forward engineering inputs. Artifact text in 18/25 documents will corrupt the code generation signal. The BR-042 ID collision will cause the most critical security finding (authentication bypass) to be misrouted during implementation. The 7 hard blockers in the readiness report are correctly documented known-open items — those are expected. The pipeline output quality issues are the primary gate.

**Minimum required before proceeding:**
1. Strip artifact text from all 25 documents (Tests 4 + 5)
2. Resolve BR-042 ID collision (Test 6)
3. Human sign-off on BLOCKER-01 (authentication architecture) — this blocks all auth-related code generation

---

*Generated by: Oracle HRMS Reverse Engineering Pipeline — Test Oracle v1.0 — 2026-08-11*
