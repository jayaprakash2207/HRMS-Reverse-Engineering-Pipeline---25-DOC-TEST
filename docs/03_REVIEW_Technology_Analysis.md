# Human Review — Technology Analysis

**Reviewer:** ___________________________
**Date reviewed:** ___________________________
**Sign-off:** ___________________________

**Source files:** `results/Technology_Analysis/TA_Deep_Analyst.md`, `results/Technology_Analysis/TA_Stack_Scout.md`
**Forward Engineering docs using this:** `12_TECHNOLOGY_BLUEPRINT.md`, `14_NFR_SPECIFICATION.md`, `18_DEPLOYMENT_ARCHITECTURE.md`

---

## 1. Current Technology Stack — Verify This Is Complete

| Component | AI Identified | Version | Reviewer Confirmation | Actual Version |
|-----------|--------------|---------|----------------------|----------------|
| Database | Oracle RDBMS | Unknown | | |
| PL/SQL Packages | 22 packages | | | |
| Oracle Forms | 6 .fmb files | | | |
| Encryption | AES-256 (PKG_SECURITY) | | | |
| Email | Oracle UTL_SMTP | | | |
| Direct Deposit | NACHA format (stubbed) | | | |
| ADP Integration | Custom export (stubbed) | | | |
| GL Feed | Custom (stubbed) | | | |

**Missing technology components not listed above:** ___________________________

---

## 2. Table Count Discrepancy — TA Claims 35, DA Claims 30

TA Stack Scout states: "Total tables: 35 (confirmed from DDL)"
DA Data Reviewer states: 30 tables from DDL parsing.

TA's section headings have internal inconsistencies:
- "Core Tables — 6 tables" but body has 8 rows
- "Payroll Tables — 8 tables" but body has 9 rows

| Reviewer Decision | |
|-------------------|-|
| Correct table count | |
| Reason for discrepancy (if known) | |

---

## 3. Architecture Findings — Verify These

| Finding | AI Conclusion | Reviewer Action | Correction |
|---------|--------------|-----------------|------------|
| Architecture pattern | Monolithic stored-procedure architecture — all business logic in DB | | |
| No separation of concerns | UI (Oracle Forms) calls DB directly — no service layer | | |
| Hardcoded configuration | `HRMS_AES256_KEY_2024` hardcoded in PKG_SECURITY | **CRITICAL** | |
| No connection pooling | UTL_SMTP creates new connection per email | | |
| No async processing | Payroll batch runs synchronously — 5000-employee org = 5000 sequential SMTP calls | | |
| No API layer | No REST/SOAP endpoints — Oracle Forms is the only client | | |
| No unit tests | Zero test files in source | | |

---

## 4. Architecture Violations Found

| Violation | Description | Severity | Reviewer Confirmation |
|-----------|------------|----------|-----------------------|
| ARCH-001 | Business logic in UI layer (Oracle Forms triggers contain business rules) | HIGH | |
| ARCH-002 | No service layer — all logic in DB packages | HIGH | |
| ARCH-003 | Hardcoded encryption key | CRITICAL | |
| ARCH-004 | God package pattern — PKG_EMPLOYEE has 20+ procedures | MEDIUM | |
| ARCH-005 | No event-driven integration — all integrations are synchronous | HIGH | |
| ARCH-006 | No caching layer | MEDIUM | |
| ARCH-007 | Mixed languages — some business rules in PL/SQL, some in Oracle Forms triggers | HIGH | |

---

## 5. Recommended Target Stack — Validate These Choices

The AI has recommended this target stack. A solutions architect must validate each choice:

| Layer | Recommended | Rationale | Reviewer Decision | Alternative if rejected |
|-------|-------------|-----------|-------------------|------------------------|
| Backend language | Java (Spring Boot) or Node.js | Enterprise support, hiring pool | | |
| Database | PostgreSQL | Open-source Oracle replacement, strong JSON support | | |
| ORM | Hibernate (Java) or TypeORM (Node) | Oracle → PG migration support | | |
| Frontend | React + TypeScript | Replace Oracle Forms | | |
| Infrastructure | Kubernetes on AWS/Azure | Scalability, cloud-native | | |
| CI/CD | GitHub Actions + ArgoCD | GitOps pattern | | |
| Monitoring | Prometheus + Grafana + Jaeger | Full observability stack | | |
| Message queue | RabbitMQ or Kafka | For async payroll processing | | |
| Secrets management | HashiCorp Vault | Replace hardcoded AES key | | |

---

## 6. Migration Risks — Verify These Are Real

| Risk | Description | Likelihood | Impact | Reviewer Confirmation |
|------|------------|-----------|--------|----------------------|
| RISK-001 | Oracle PL/SQL → PostgreSQL function migration complexity | HIGH | HIGH | |
| RISK-002 | Oracle Forms → Web UI — no direct migration path | HIGH | HIGH | |
| RISK-003 | Hardcoded AES key — all encrypted data needs re-encryption at cutover | HIGH | CRITICAL | |
| RISK-004 | Broken rehire procedure — business process gap | MEDIUM | HIGH | |
| RISK-005 | Synchronous payroll SMTP — new system must handle async email | HIGH | MEDIUM | |
| RISK-006 | Missing NACHA implementation — direct deposit must be built from scratch | HIGH | HIGH | |
| RISK-007 | Race condition in emp number generation — must be fixed before migration | HIGH | MEDIUM | |
| RISK-008 | Data type differences: Oracle NUMBER vs PostgreSQL NUMERIC — precision | MEDIUM | HIGH | |

---

## 7. Technology Blueprint Review

Open [results/ForwardEngineering_Docs/12_TECHNOLOGY_BLUEPRINT.md](../results/ForwardEngineering_Docs/12_TECHNOLOGY_BLUEPRINT.md):

| Section | Complete? | Approved? | Reviewer Notes |
|---------|-----------|-----------|----------------|
| Current vs Target stack table | | | |
| Technology choices justified | | | |
| Risks and mitigations | | | |
| Phased adoption roadmap | | | |

---

## 8. Open Questions for Solutions Architect

1. What cloud provider has been selected / is preferred?
2. Is there an enterprise architecture standard that mandates specific technology choices?
3. Are there existing Oracle licenses that affect the migration timeline?
4. Is there a data warehouse or BI tool receiving data from Oracle HRMS that must be preserved?
5. What is the target response time SLA for payroll processing (currently unbounded in Oracle)?
6. Is there a preference for microservices vs modular monolith for the new system?
