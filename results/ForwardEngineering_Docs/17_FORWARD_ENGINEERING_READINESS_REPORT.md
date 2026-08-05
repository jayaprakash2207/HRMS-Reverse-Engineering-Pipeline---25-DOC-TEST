# 17 — Forward Engineering Readiness Report
**System:** Acme Corporation HRMS
**Assessment Date:** Current
**Assessor:** Foundation Synthesis Agent
**Overall Readiness Score: 71 / 100 — CONDITIONAL GO**

---

## 1. Scoring Methodology

Each dimension is scored 0–10. Weights reflect criticality to a successful forward-engineering effort. Weighted score determines Go / Conditional Go / No-Go recommendation per phase.

| Dimension | Weight | Raw Score | Weighted Score | Notes |
|-----------|--------|-----------|---------------|-------|
| Data Dictionary Completeness | 15% | 8 | 1.20 | 22 confirmed tables, 6 views; 7 inferred tables unresolved |
| Domain Model Coverage | 15% | 9 | 1.35 | All 10 BCs mapped; aggregates and invariants documented |
| API Contract Coverage | 15% | 9 | 1.35 | 76 endpoints specified; all with security, schema, business rules |
| Business Rule Completeness | 15% | 8 | 1.20 | BR-01–BR-140 extracted; HOH defect and 7 gaps noted |
| Security Architecture | 10% | 6 | 0.60 | 10 gaps identified; critical gaps (key-in-DB) unresolved |
| Defect Identification | 10% | 9 | 0.90 | All 8 defects documented with remediation rules |
| NFR Specification | 5% | 9 | 0.45 | Full performance, availability, compliance NFRs defined |
| Technology Blueprint | 5% | 7 | 0.35 | Multi-option; no final stack selected (ADRs pending) |
| Test Strategy | 5% | 6 | 0.30 | Stubs and coverage targets defined; no test harness yet |
| Oracle Migration Risk | 5% | 5 | 0.25 | CONNECT BY, MEDIAN, UTL_SMTP migration paths defined but untested |

**Total: 71 / 100**

---

## 2. Readiness by Bounded Context

| BC | Name | Readiness | Confidence | Blockers |
|----|------|-----------|-----------|---------|
| BC-01 | Employee Identity | HIGH | Evidence-based | None — proceed |
| BC-02 | Compensation | MEDIUM | Evidence-based | HOH tax defect; no rollback procedure; tax bracket data needed |
| BC-03 | Leave Management | MEDIUM-HIGH | Evidence-based | Carry-forward logic unimplemented; PTO payout unimplemented |
| BC-04 | Performance | MEDIUM-HIGH | Evidence-based | Calibration write path gap; CALIBRATING status incomplete |
| BC-05 | Benefits | MEDIUM | Evidence-based | ADP field layout confirmed; NACHA still absent |
| BC-06 | Security | MEDIUM | Partial (USER_CREDENTIALS inferred) | Critical: key-in-DB; no session invalidation; USER_CREDENTIALS DDL unconfirmed |
| BC-07 | Org Structure | HIGH | Evidence-based | CONNECT BY replacement strategy defined |
| BC-08 | Notifications | MEDIUM-HIGH | Evidence-based | SMS/IN_APP handlers unimplemented; retry logic absent |
| BC-09 | Integration | LOW-MEDIUM | Evidence-based | NACHA unimplemented; no ACL on feeds |
| BC-10 | Reporting | LOW | Inferred | All tables inferred; no DDL confirmed |

---

## 3. Risk Register

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|-----------|
| RISK-001 | HOH $0 tax in production during parallel run | MEDIUM | HIGH | Fix before Phase 3 deploy; tax specialist review mandatory |
| RISK-002 | Inferred tables (7) may have divergent DDL when confirmed | MEDIUM | MEDIUM | Confirm DDL before generating migrations; hold ART-001 for these tables |
| RISK-003 | Oracle CONNECT BY replacement degrades under load for large orgs | LOW | MEDIUM | Pre-compute org tree; Redis cache; load test at 5,000 employees |
| RISK-004 | AES key migration from SYSTEM_CONFIG to KMS may break decryption of legacy SSN/bank data | HIGH | CRITICAL | Decrypt all legacy data with old key, re-encrypt with new KMS key before cutover |
| RISK-005 | ADP fixed-width format undocumented — positions 105–130 inferred | MEDIUM | HIGH | Obtain official ADP spec; validate with test enrollment records |
| RISK-006 | USER_CREDENTIALS table structure unknown — auth migration may surface schema surprises | MEDIUM | HIGH | DBA confirms DDL before Phase 1 |
| RISK-007 | Oracle MEDIAN() / SYS_CONNECT_BY_PATH used in 3 views — no equivalent tested | LOW | LOW | PostgreSQL PERCENTILE_CONT validated in migration spike |
| RISK-008 | No payroll rollback procedure exists — incorrect run may be unrecoverable | MEDIUM | HIGH | Implement rollback procedure before first production payroll run |
| RISK-009 | NOCACHE sequence contention under concurrent hire events | LOW (small org) | LOW | Resolved by default DB sequence caching in target |
| RISK-010 | NACHA implementation absent — direct deposit impossible | HIGH | MEDIUM | Phased: issue paper checks until NACHA implemented in Phase 3 |

---

## 4. Gate Status Summary

| Gate | Status | Blocking |
|------|--------|---------|
| VG-01 Data Dictionary Completeness | PARTIAL — 7 inferred tables unresolved | For those tables only |
| VG-02 Domain Model Completeness | PASS | — |
| VG-03 API Contract Completeness | PASS | — |
| VG-04 Business Rule Mapping | PASS for confirmed BCs; PARTIAL for BC-10 | BC-10 only |
| VG-05 Security Architecture Review | NOT STARTED — human sign-off required | Blocks Phase 1 deployment |
| VG-06 Migration Script Dry-Run | NOT STARTED | Blocks data migration |
| VG-07 Test Coverage Gate | NOT STARTED | Blocks each phase promotion |
| VG-08 NFR Validation | NOT STARTED | Blocks production |

---

## 5. Pre-Generation Action Items

The following actions must be completed before the corresponding generation phase begins:

### Before Phase 1 Generation
| ID | Action | Owner | Priority |
|----|--------|-------|---------|
| ACT-001 | Confirm USER_CREDENTIALS DDL with DBA | DBA | P0 |
| ACT-002 | Obtain KMS service credentials; configure for Phase 1 auth | Security Architect | P0 |
| ACT-003 | Security sign-off on RBAC matrix (Doc 13 §3.2) | Security Architect | P0 |
| ACT-004 | Confirm TERMINATION_CODES lookup table DDL | DBA | P1 |
| ACT-005 | Select target database (ADR-002) | Architecture Board | P0 |
| ACT-006 | Select authentication provider (ADR-003) | Architecture Board | P0 |

### Before Phase 2 Generation
| ID | Action | Owner | Priority |
|----|--------|-------|---------|
| ACT-007 | Confirm carry-forward policy with HR (days cap, same leave type vs any) | HR Policy Owner | P1 |
| ACT-008 | Confirm PTO payout calculation (full balance vs capped) | HR Policy Owner + Legal | P1 |
| ACT-009 | Obtain official ADP benefits feed specification document | Benefits Administrator | P1 |

### Before Phase 3 Generation
| ID | Action | Owner | Priority |
|----|--------|-------|---------|
| ACT-010 | Engage payroll tax specialist to validate HOH fix and all brackets | Payroll Specialist | P0 |
| ACT-011 | Obtain NACHA ACH spec v2; confirm bank origination agreement | Treasury | P0 |
| ACT-012 | Confirm all RPT_* table DDL for BC-10 | DBA | P1 |
| ACT-013 | Design payroll rollback procedure with Payroll Manager | Payroll Manager | P0 |

---

## 6. Overall Recommendation

**Conditional Go — Phase 1 may begin after ACT-001 through ACT-006 are resolved.**

Phase 2 and Phase 3 are blocked on their respective action items. Phase 3 (payroll) carries the highest financial and compliance risk and must not enter production without tax specialist sign-off and a parallel-run of at least two full pay cycles against the legacy system.

BC-10 (Reporting) should be considered a Phase 4 effort; insufficient confirmed data to generate with confidence.

---