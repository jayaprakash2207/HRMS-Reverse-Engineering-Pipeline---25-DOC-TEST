# 12 — Technology Blueprint
**System:** Acme Corporation HRMS — Target Architecture
**Version:** 1.0
**Status:** Draft for Architecture Review
**Prepared by:** Solution Architecture Team
**Date:** 2026-08-05

---

## Executive Summary

The Acme HRMS is a monolithic Oracle 19c + Oracle Forms 12c application with zero automated testing, no CI/CD pipeline, multiple critical security vulnerabilities (hardcoded AES keys, MD5 passwords, stub authentication), and fundamental functional gaps (direct deposit never implemented, COBRA compliance absent, final pay calculation missing). This blueprint defines the target technology stack, migration strategy, and phased roadmap to replace the system with a modern, cloud-native, maintainable platform.

The recommended path is a **greenfield replacement** rather than a lift-and-shift, driven by the depth of architectural debt. Oracle Forms has no path to containerisation. The monolithic PL/SQL application embeds business logic, data access, and UI concerns in the same layer. A clean break with a well-structured backend, a purpose-built frontend, and a managed PostgreSQL database yields lower long-term TCO and eliminates the Oracle licence dependency.

---

## 1. Current vs Target Technology Stack

| Layer | Current Technology | Version | Licence Type | Target Technology | Version Target | Licence Type |
|---|---|---|---|---|---|---|
| **Database** | Oracle Database | 19c | Commercial (expensive) | PostgreSQL | 16 | Open Source |
| **ORM / Data Access** | PL/SQL packages (inline SQL) | n/a | n/a | SQLAlchemy (Python) / Prisma (Node) | latest | Open Source |
| **Backend Language** | PL/SQL | Oracle 19c dialect | Commercial | Python 3.12 | 3.12+ | Open Source |
| **Backend Framework** | None (PL/SQL packages) | n/a | n/a | FastAPI | 0.115+ | Open Source |
| **Frontend Language** | Oracle Forms PLL (proprietary) | 12.2.1.4 | Commercial | TypeScript | 5.x | Open Source |
| **Frontend Framework** | Oracle Forms 12c (client-server) | 12.2.1.4 | Commercial | React 19 + Vite | latest | Open Source |
| **UI Component Library** | Oracle Forms built-ins | proprietary | Commercial | shadcn/ui + Tailwind CSS | latest | Open Source |
| **Authentication** | Stub (password never verified) | n/a | n/a | Keycloak (OIDC/OAuth2) | 25.x | Open Source |
| **Session Management** | USER_SESSIONS table (30-min polling) | custom PL/SQL | n/a | JWT + refresh tokens (Keycloak) | n/a | Open Source |
| **Encryption** | DBMS_CRYPTO AES-256 (hardcoded key) | Oracle built-in | Commercial | AWS KMS / HashiCorp Vault | n/a | Managed / Open Source |
| **Password Hashing** | MD5 (critically broken) | Oracle DBMS_CRYPTO | Commercial | Argon2id (via passlib) | latest | Open Source |
| **Job Scheduling** | DBMS_SCHEDULER (implied, no scripts) | Oracle 19c | Commercial | Celery + Redis | 5.x / 7.x | Open Source |
| **File I/O** | UTL_FILE + Oracle directory objects | Oracle 19c | Commercial | S3-compatible object storage | n/a | Managed |
| **Email** | UTL_SMTP (smtp.internal:25, unauthenticated) | Oracle 19c | Commercial | AWS SES / SendGrid | n/a | Managed / SaaS |
| **Logging** | Free-text AUDIT_LOG table + DBMS_OUTPUT | custom | n/a | Structured JSON → CloudWatch / Loki | n/a | Open Source / Managed |
| **Monitoring** | None | — | — | Prometheus + Grafana | latest | Open Source |
| **Tracing** | None | — | — | OpenTelemetry + Jaeger / Tempo | latest | Open Source |
| **Container Runtime** | None (bare metal / VM assumed) | — | — | Docker + containerd | latest | Open Source |
| **Orchestration** | None | — | — | Kubernetes (EKS) | 1.31+ | Managed |
| **CI/CD** | None (fully manual) | — | — | GitHub Actions | n/a | SaaS (free tier) |
| **IaC** | None | — | — | Terraform + Helm | 1.9 / 3.x | Open Source |
| **Secret Management** | Hardcoded in source code | — | — | AWS Secrets Manager + Vault | n/a | Managed / Open Source |
| **API Gateway** | None | — | — | AWS API Gateway / Kong | n/a | Managed / Open Source |
| **Message Broker** | NOTIFICATION_QUEUE table (polling) | custom PL/SQL | n/a | Redis Streams / AWS SQS | n/a | Open Source / Managed |
| **Search** | Oracle SQL LIKE | — | — | PostgreSQL full-text search (phase 1); OpenSearch (phase 3) | — | Open Source |
| **Build Tooling** | Manual SQL*Plus scripts | — | — | Poetry (Python) + pnpm (Node) | latest | Open Source |

---

## 2. Recommended Technology Stack

### 2.1 Backend: Python + FastAPI

**Language:** Python 3.12+
**Framework:** FastAPI 0.115+
**Runtime:** CPython (uvicorn ASGI server, gunicorn process manager)

**Why Python over Java/Go/Node:**

| Criterion | Python + FastAPI | Java + Spring Boot | Go + Gin | Node + NestJS |
|---|---|---|---|---|
| Data manipulation (payroll rules, calculations) | Excellent (numpy, pandas available) | Good | Moderate | Moderate |
| HR domain developer availability | High | Very high | Low | Moderate |
| Automatic OpenAPI docs | Native (FastAPI) | Via Springdoc | Manual | Via Swagger plugin |
| Type safety | Strong (Pydantic v2) | Strong | Very strong | Strong (TypeScript) |
| Time-to-first-endpoint | Fastest | Moderate | Fast | Fast |
| Oracle → PostgreSQL migration libraries | psycopg2, asyncpg, SQLAlchemy | JDBC / Hibernate | pgx | pg / TypeORM |
| Built-in async support | Native (asyncio) | Reactive (WebFlux) | Native goroutines | Native (event loop) |

FastAPI was selected for: native async, first-class Pydantic validation (replaces Oracle CHECK constraints and PL/SQL validation packages), automatic OpenAPI 3.1 specification generation, and Python's strength in the financial calculation and data transformation domain that HRMS payroll requires.

**Key backend packages:**

| Package | Purpose | Replaces |
|---|---|---|
| `fastapi` | HTTP framework, routing, dependency injection | Oracle Forms server-side triggers |
| `pydantic v2` | Request/response validation, business rule enforcement | PKG_VALIDATION, HRMS_VALIDATION_LIB |
| `sqlalchemy 2.x` (async) | ORM, migrations (Alembic) | Inline PL/SQL SQL |
| `alembic` | Database migration management | Manual SQL*Plus scripts |
| `celery + redis` | Async task queue, scheduled jobs | DBMS_SCHEDULER |
| `passlib[argon2]` | Password hashing | DBMS_CRYPTO MD5 (replacement) |
| `python-jose` | JWT handling | USER_SESSIONS table |
| `boto3` | AWS services (SES, S3, KMS, Secrets Manager) | UTL_SMTP, UTL_FILE, hardcoded keys |
| `structlog` | Structured JSON logging | PKG_COMMON.log_error free-text |
| `opentelemetry-sdk` | Distributed tracing | None (no tracing existed) |
| `httpx` | Async HTTP client for external integrations | UTL_HTTP (not used but implied) |
| `cryptography` | AES-256-GCM for PII fields | DBMS_CRYPTO (hardcoded key replaced by KMS) |

**API structure (domain-driven):**

```
api/
  v1/
    employees/          # BC-01 Employee Identity
    payroll/            # BC-02 Compensation
    leave/              # BC-03 Leave Management
    performance/        # BC-04 Performance
    benefits/           # BC-05 Benefits
    auth/               # BC-06 Security & Access
    departments/        # BC-07 Org Structure
    notifications/      # BC-08 Notifications
    integrations/       # BC-09 Integration & Export
    reports/            # BC-10 Reporting
```

---

### 2.2 Database: PostgreSQL 16

**Engine:** PostgreSQL 16 (managed: AWS RDS Aurora PostgreSQL or AWS RDS PostgreSQL Multi-AZ)
**ORM:** SQLAlchemy 2.x with asyncpg driver
**Migration tool:** Alembic

**Why PostgreSQL over MySQL / SQL Server / Oracle:**

| Criterion | PostgreSQL 16 | MySQL 8.x | SQL Server 2022 | Oracle 21c (stay) |
|---|---|---|---|---|
| Oracle feature compatibility | Best (via orafce extension) | Moderate | High (T-SQL gap) | Perfect (no migration) |
| CONNECT BY / hierarchical queries | `WITH RECURSIVE` (standard) | `WITH RECURSIVE` | `WITH` | Native |
| Window functions | Full support | Full support | Full support | Full support |
| MEDIAN() equivalent | `PERCENTILE_CONT(0.5)` | None native | `PERCENTILE_CONT` | Native |
| Row-level security | Native (RLS policies) | None | Row-level security | VPD (expensive) |
| JSON support | JSONB (best-in-class) | JSON | JSON | JSON (limited) |
| Licence cost | Free | Free | Commercial | Very expensive |
| Managed cloud offering | AWS RDS / Aurora | AWS RDS | AWS RDS | AWS RDS (expensive) |
| Full-text search | Native tsvector/tsquery | Limited | Good | Expensive option |
| Encryption at rest | TDE (AWS RDS) | TDE | TDE | TDE (extra cost) |

**Oracle-to-PostgreSQL migration notes for this system:**

| Oracle Feature | PostgreSQL Equivalent | Complexity |
|---|---|---|
| `DBMS_CRYPTO.HASH_MD5` | pgcrypto `md5()` (do not use — replace with Argon2id) | Low |
| `DBMS_CRYPTO.ENCRYPT_AES256` | Application-layer encryption via `cryptography` lib + KMS | Medium |
| `SYS_GUID()` | `gen_random_uuid()` | Low |
| `SYSDATE` | `NOW()` / `CURRENT_TIMESTAMP` | Low |
| `NVL(x, y)` | `COALESCE(x, y)` | Low |
| `CONNECT BY PRIOR` | `WITH RECURSIVE` CTE | Medium |
| `SEQUENCE` with NOCACHE | `GENERATED ALWAYS AS IDENTITY` | Low |
| `MEDIAN()` aggregate | `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY col)` | Low |
| `UTL_FILE` | S3 multipart upload via boto3 | Medium |
| `UTL_SMTP` | AWS SES / SendGrid API | Low |
| `DBMS_SCHEDULER` | Celery beat + Redis | Medium |
| `REF CURSOR` | SQLAlchemy `Result` / streaming response | Low |
| `AUTONOMOUS_TRANSACTION` (audit) | Separate async audit service / outbox pattern | High |
| PL/SQL package bodies | Python service classes | High (most effort) |
| Oracle CHECK constraints | Pydantic validators + PostgreSQL CHECK | Low |
| `RAISE_APPLICATION_ERROR` | FastAPI `HTTPException` + custom error codes | Low |
| Oracle Forms triggers | React event handlers + API calls | High |
| `RPAD`/`LPAD` fixed-width files | Python `str.ljust`/`str.rjust` | Low |
| `PKG_COMMON.log_info` (free-text) | structlog structured JSON events | Low |

**PII encryption strategy (replacing hardcoded AES key):**

All PII fields currently encrypted with the hardcoded key `HR$ystem_3ncrypt10n_K3y_2024!!` (TD-01) must be re-encrypted during migration:

1. Export all encrypted PII using the old key (decrypt in migration script).
2. Re-encrypt using application-layer AES-256-GCM with a key fetched from AWS KMS per-tenant.
3. Store ciphertext in PostgreSQL `BYTEA` or `TEXT` columns with a `key_version` integer for rotation support.
4. Routing numbers (currently plaintext — TD-46) encrypted in the same pass.

---

### 2.3 Frontend: React 19 + TypeScript

**Framework:** React 19
**Build tool:** Vite 6
**Language:** TypeScript 5.x (strict mode)
**Component library:** shadcn/ui (Radix UI primitives + Tailwind CSS)
**State management:** Zustand (local) + TanStack Query v5 (server state)
**Forms:** React Hook Form + Zod (schema validation mirrors Pydantic on backend)
**Routing:** TanStack Router (type-safe)
**Table/grid:** TanStack Table v8 (replaces Oracle Forms multi-record blocks)

**Why React over Angular / Vue / Oracle JET:**

| Criterion | React 19 | Angular 18 | Vue 3 | Oracle JET |
|---|---|---|---|---|
| Ecosystem size | Largest | Large | Large | Very small |
| TypeScript support | Excellent | Native | Excellent | Moderate |
| Oracle Forms conceptual replacement | Good (forms library) | Good | Good | Designed for it (but Oracle-locked) |
| Talent availability | Highest | High | High | Very low |
| Long-term vendor risk | Low (Meta + community) | Low (Google) | Low (community) | High (Oracle roadmap) |
| WCAG accessibility | shadcn/Radix are accessible | CDK accessible | Limited | Adequate |
| Mobile / responsive | Yes (Tailwind) | Yes | Yes | Limited |

**Oracle Forms replacement mapping:**

| Oracle Forms Concept | React Equivalent |
|---|---|
| Multi-record block (grid) | TanStack Table with pagination |
| LOV (List of Values) | Combobox with async search (shadcn/ui Command) |
| Alert / MESSAGE built-in | Toast notifications (sonner) |
| FORM_TRIGGER_FAILURE | Zod validation error / React Hook Form field error |
| KEY-NEXT-ITEM | Native tab order + React refs |
| WHEN-NEW-FORM-INSTANCE | `useEffect` on mount + API call |
| POST-QUERY | TanStack Query `useQuery` with `select` transform |
| OPEN_FORM (MDI navigation) | TanStack Router `<Link>` / programmatic `navigate()` |
| PRE-INSERT / PRE-UPDATE | React Hook Form `handleSubmit` + Zod schema |
| Oracle Forms canvas | React layout with Tailwind grid/flex |
| HRMS_MENU.fmb MDI shell | React Layout component + sidebar navigation |

---

### 2.4 Infrastructure: Kubernetes on AWS (EKS)

**Cloud provider:** AWS
**Orchestration:** Amazon EKS (Elastic Kubernetes Service) — Kubernetes 1.31+
**Container runtime:** containerd
**Service mesh:** AWS App Mesh (phase 2) or Istio (phase 3)
**Ingress:** AWS Load Balancer Controller + ALB Ingress
**DNS:** AWS Route 53
**CDN:** AWS CloudFront (React SPA + static assets)
**Object storage:** AWS S3 (replaces UTL_FILE Oracle directories)
**Secrets:** AWS Secrets Manager + External Secrets Operator
**Encryption keys:** AWS KMS (replaces hardcoded `HR$ystem_3ncrypt10n_K3y_2024!!`)
**Email:** AWS SES (replaces UTL_SMTP to smtp.internal:25)
**Queue:** AWS SQS + Redis (Elasticache) for Celery

**Why AWS over Azure / GCP:**

| Criterion | AWS | Azure | GCP |
|---|---|---|---|
| Managed PostgreSQL | Aurora PostgreSQL (best-in-class) | Azure Database for PostgreSQL | Cloud SQL PostgreSQL |
| EKS / managed K8s | EKS (mature) | AKS (mature) | GKE (most automated) |
| Oracle migration tooling | AWS DMS + Schema Conversion Tool | SSMA | Database Migration Service |
| Secrets management | AWS Secrets Manager | Key Vault | Secret Manager |
| HR/Payroll compliance (SOC 2, HIPAA BAA) | All three are compliant | All three | All three |
| Market share (enterprise) | 33% (largest) | 23% | 11% |

**AWS DMS (Database Migration Service)** will be used for the Oracle → PostgreSQL data migration, with the AWS Schema Conversion Tool (SCT) to generate PostgreSQL DDL from Oracle DDL and flag incompatibilities.

**Kubernetes workload topology:**

```
eks-cluster (hrms-prod)
├── namespace: hrms-backend
│   ├── Deployment: hrms-api          (FastAPI, 3 replicas min, HPA)
│   ├── Deployment: hrms-worker       (Celery worker, 2 replicas)
│   ├── Deployment: hrms-beat         (Celery beat, 1 replica)
│   └── Deployment: hrms-notification (notification service, 2 replicas)
├── namespace: hrms-frontend
│   └── Deployment: hrms-web          (Nginx serving React SPA, 2 replicas)
├── namespace: hrms-auth
│   └── StatefulSet: keycloak         (2 replicas + RDS PostgreSQL backend)
├── namespace: hrms-data
│   ├── (AWS RDS — external to cluster, accessed via VPC)
│   └── StatefulSet: redis            (Elasticache preferred for prod)
└── namespace: hrms-monitoring
    ├── Deployment: prometheus
    ├── Deployment: grafana
    ├── Deployment: loki
    └── Deployment: tempo
```

**IaC toolchain:**

| Tool | Purpose |
|---|---|
| Terraform | AWS resource provisioning (VPC, EKS, RDS, S3, KMS, IAM) |
| Helm | Kubernetes application packaging and deployment |
| ArgoCD | GitOps continuous delivery to cluster |
| `terraform-aws-modules/eks` | EKS cluster module |
| `aws-load-balancer-controller` | ALB Ingress integration |
| `external-secrets-operator` | Sync AWS Secrets Manager → Kubernetes Secrets |
| `cert-manager` | TLS certificate automation (Let's Encrypt / ACM) |

---

### 2.5 CI/CD Pipeline

**Primary tool:** GitHub Actions
**GitOps delivery:** ArgoCD
**Container registry:** Amazon ECR

**Pipeline stages:**

```
Trigger: push to feature branch / PR to main
│
├── Stage 1: Code Quality (parallel)
│   ├── ruff lint + black format check (Python)
│   ├── mypy type checking (strict)
│   ├── ESLint + Prettier check (TypeScript/React)
│   └── detect-secrets scan (blocks hardcoded credentials)
│
├── Stage 2: Security Scan (parallel)
│   ├── Bandit SAST (Python security)
│   ├── Semgrep SAST (custom rules for OWASP Top 10)
│   ├── Trivy container image scan
│   └── pip-audit / npm audit (dependency CVEs)
│
├── Stage 3: Unit Tests
│   ├── pytest (Python, ≥80% coverage gate)
│   └── Vitest (React components)
│
├── Stage 4: Integration Tests
│   ├── pytest with testcontainers-python (PostgreSQL 16)
│   └── Playwright E2E tests (critical flows only)
│
├── Stage 5: Build
│   ├── docker build --target=production (multi-stage Dockerfile)
│   ├── docker push to ECR (tagged with git SHA)
│   └── vite build (React SPA → S3/CloudFront)
│
├── Stage 6: Deploy to Staging (ArgoCD sync)
│   └── helm upgrade --install hrms-api ... (staging namespace)
│
└── Stage 7: Deploy to Production (manual approval gate)
    ├── Require 2 approvals (PR review + release gate)
    ├── helm upgrade (production namespace via ArgoCD)
    └── Post-deploy smoke test (k6 synthetic transaction)
```

**Workflow files:**

| File | Trigger | Purpose |
|---|---|---|
| `.github/workflows/ci.yml` | push, pull_request | Stages 1–4 |
| `.github/workflows/build-push.yml` | merge to main | Stage 5 |
| `.github/workflows/deploy-staging.yml` | merge to main | Stage 6 |
| `.github/workflows/deploy-prod.yml` | manual dispatch | Stage 7 |
| `.github/workflows/dependency-update.yml` | weekly cron | Dependabot + auto-PR |

**Branch strategy:** GitHub Flow (main is always deployable; feature branches merge via PR with required review + passing CI).

---

### 2.6 Monitoring: Observability Stack

**Metrics:** Prometheus + Grafana
**Logs:** Loki (log aggregation) + Promtail (log shipper) + Grafana
**Traces:** OpenTelemetry SDK → Tempo (distributed tracing) + Grafana
**Alerting:** Grafana Alerting → PagerDuty (on-call) + Slack (non-critical)
**Synthetic monitoring:** k6 Cloud or Grafana k6 (post-deploy smoke tests)
**Uptime:** AWS CloudWatch Synthetics (external health checks)
**APM:** Grafana Faro (Real User Monitoring for the React SPA)

**The Grafana stack (Loki + Tempo + Prometheus + Grafana) is preferred** over the ELK stack for this system because:
- Single UI for logs, metrics, and traces (reduces context switching)
- Loki is significantly cheaper than Elasticsearch for log storage (index-free)
- Native integration with OpenTelemetry (no vendor lock-in)
- Lower operational complexity for a small-to-medium team

**Key dashboards to build (day-1 requirements):**

| Dashboard | Key Metrics | Replaces |
|---|---|---|
| Payroll Run Health | run duration, error rate, employee count, GL feed status | Manual PAYROLL_RUNS table query |
| Leave Balance Coverage | request queue depth, approval SLA, balance anomalies | None (no monitoring existed) |
| Authentication & Security | failed login rate, locked account count, session anomalies | USER_SESSIONS table manual query |
| Integration Feed Status | benefits feed size, GL feed success/fail, ACH prenote rate | None (all silent stubs) |
| API Latency / Availability | p50/p95/p99, error rate by endpoint (RED method) | None |
| Database Health | connection pool, slow queries, replication lag | None |

**Structured log format (replacing free-text AUDIT_LOG):**

```json
{
  "timestamp": "2026-08-05T14:32:01.123Z",
  "level": "INFO",
  "service": "hrms-api",
  "trace_id": "4bf92f3577b34da6",
  "span_id": "00f067aa0ba902b7",
  "event": "payroll.run.approved",
  "run_id": 4821,
  "approved_by_emp_id": 102,
  "employee_count": 487,
  "total_gross": 1482934.50,
  "duration_ms": 3421
}
```

---

## 3. Architecture Patterns to Adopt

### 3.1 Patterns Replacing Oracle HRMS Anti-Patterns

| Current Anti-Pattern | Problem | Replacement Pattern |
|---|---|---|
| God package (PKG_PAYROLL does everything) | Untestable, undeployable in isolation | Domain-driven service decomposition |
| Business logic in PL/SQL packages | Database = only deployment unit | Application-layer service classes (Python) |
| Oracle Forms UI coupled to DB | Impossible to test UI independently | API-first: UI calls REST; backend is headless |
| Hardcoded encryption keys in source | Immediate credential leak on repo access | Externalized secrets (AWS KMS + Secrets Manager) |
| Free-text AUDIT_LOG table | Unqueryable, single purge policy | Structured event log (OpenTelemetry events + Loki) |
| Stub procedures logging false success | Silent operational failures | Health checks; distinguish "not implemented" from "succeeded" |
| DBMS_SCHEDULER with no monitoring | Jobs fail silently | Celery with result backend; Flower dashboard; dead-letter queues |
| UTL_FILE to Oracle directory objects | Filesystem coupling, no versioning | S3 with object versioning + event notifications |
| NOTIFICATION_QUEUE table polling every 5 min | 5-minute notification latency | Redis Streams / SQS with near-real-time delivery |
| Single AUDIT_LOG for all event types | Impossible to set retention policies per type | Separate audit event stream per domain (structured logs) |
| Grade-based RBAC in application code | No policy enforcement at DB layer | Row-level security in PostgreSQL + OIDC scopes in Keycloak |
| Session management via USER_SESSIONS table | In-flight sessions survive termination | JWT with short expiry (15 min) + Keycloak session revocation |
| Oracle CONNECT BY for org hierarchy | N+1 query risk, performance degrades >500 employees | PostgreSQL `WITH RECURSIVE` CTE + materialised closure table for deep hierarchies |

### 3.2 Domain-Driven Design (DDD)

The Oracle monolith has natural bounded context boundaries already implied by the PL/SQL package structure (PKG_EMPLOYEE, PKG_PAYROLL, etc.). These map directly to application modules with well-defined internal APIs. Phase 1 keeps all modules in a single deployable (modular monolith). Phase 3 extracts high-churn or high-scale modules as separate services.

**Aggregate root per bounded context:**

| Bounded Context | Aggregate Root | Key Domain Events |
|---|---|---|
| Employee Identity | `Employee` | `EmployeeHired`, `EmployeeTransferred`, `EmployeeTerminated` |
| Compensation | `PayrollRun` | `PayrollCalculated`, `PayrollApproved`, `PayslipGenerated` |
| Leave Management | `LeaveBalance` | `LeaveRequested`, `LeaveApproved`, `LeaveAccrued` |
| Performance | `ReviewCycle` | `CycleOpened`, `ReviewSubmitted`, `ReviewCalibrated` |
| Benefits | `BenefitEnrollment` | `EnrollmentChanged`, `BenefitsFeedExported` |
| Security & Access | `UserCredential` | `UserAuthenticated`, `PasswordChanged`, `SessionRevoked` |

### 3.3 Outbox Pattern for Audit and Notifications

The Oracle system uses `AUTONOMOUS_TRANSACTION` blocks for audit logging — this is fundamentally broken because autonomous transactions commit independently, creating split-brain scenarios. The replacement is the **Transactional Outbox Pattern**:

1. Domain events are written to an `outbox_events` table within the same transaction as the domain change.
2. A Celery worker polls `outbox_events` and dispatches to notification service or audit event stream.
3. Delivery is at-least-once; idempotency keys prevent duplicate processing.

### 3.4 Repository Pattern (replacing inline PL/SQL SQL)

All database access goes through repository classes. Service classes never write SQL directly. This makes unit testing possible (repositories can be mocked) and enables future database changes without touching business logic.

### 3.5 CQRS (Command Query Responsibility Segregation) for Reporting

The RPT_* tables in the Oracle system are a failed attempt at CQRS — the `refresh_reporting_tables` procedure is a stub that never runs. The replacement implements CQRS properly:

- **Write side:** Domain service methods update normalised PostgreSQL tables.
- **Read side:** PostgreSQL materialised views replace RPT_* tables. Refresh is triggered by domain events (after payroll approval, after headcount change) rather than a nightly stub.
- **Reporting API:** Read-only endpoints backed by materialised views return pre-aggregated data within milliseconds.

---

## 4. Technology Risks and Mitigations

| ID | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| TR-01 | Oracle PL/SQL business logic is too complex to fully reverse-engineer before migration | High | Critical | Run BA analysis track to completion first; generate test oracle from existing system; use property-based testing (Hypothesis) to validate Python reimplementation |
| TR-02 | PII migration: hardcoded AES key means all encrypted data must be decrypted and re-encrypted during migration | High | Critical | Migration script runs decrypt (old key) → re-encrypt (KMS) atomically; run in staging first; rollback plan preserves Oracle as source-of-truth until cutover |
| TR-03 | Oracle Forms business logic hidden in PLL libraries not fully documented | High | High | HRMS_VALIDATION_LIB and HRMS_COMMON_LIB fully decompiled; all validation rules captured in BA analysis; Pydantic validators provide equivalent enforcement |
| TR-04 | DISC-001/DISC-002 unresolved (hire date limit 90 vs 180 days; EMPLOYEE_HISTORY column layout mismatch) | Medium | High | Resolve with DBA and HR team before building equivalent validations; document authoritative rule in ADR |
| TR-05 | VQ-BA-01 unresolved: ACCOUNT_NUMBER_ENC key not confirmed — if same key as SSN, entire encryption posture is compromised | High | Critical | Assume same key until confirmed otherwise; treat all encrypted columns as needing re-encryption in migration |
| TR-06 | Oracle MEDIAN() used in compensation_summary — no direct PostgreSQL equivalent | Low | Medium | Replace with `PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary)` — verified equivalent; add unit test comparing output on seed data |
| TR-07 | Users trained on Oracle Forms will resist browser-based UI | Medium | High | Phased rollout with parallel running; UX research on power-user workflows (LOV navigation, grid editing); training programme |
| TR-08 | Celery job scheduler may miss jobs during Redis failover | Low | High | Use Redis Sentinel or Elasticache with Multi-AZ; Celery result backend persists task state; dead-letter queue captures failed tasks |
| TR-09 | AWS DMS may not handle all Oracle 19c data types correctly (BLOB, CLOB, XMLTYPE) | Medium | Medium | PHOTO_BLOB migrated separately via S3 pre-migration; CLOB (NOTES, CLOB columns) tested in DMS task before cutover |
| TR-10 | COBRA compliance gap (PP-TERM-01) is a federal violation on every termination — must be implemented before go-live | High | Critical | COBRA notification service is a mandatory phase 2 deliverable; legal must confirm 14-day clock mechanics before build |
| TR-11 | Direct deposit (ACH) never implemented in Oracle system — new system must implement from scratch | High | High | Nacha ACH file generation is a phase 2 deliverable; use validated Nacha library (nacha-python); prenote flow required before first live ACH |
| TR-12 | Keycloak adds operational complexity the team may not have experience with | Medium | Medium | Consider Auth0 or AWS Cognito (managed SaaS) for phase 1 to reduce ops burden; migrate to self-hosted Keycloak in phase 2 if cost justifies |
| TR-13 | React learning curve for team experienced in Oracle Forms | Medium | Medium | Pair programming during phase 1; leverage shadcn/ui patterns to reduce custom component work; Oracle Forms→React mapping guide in onboarding docs |
| TR-14 | PostgreSQL row-level security (RLS) must replicate Oracle grade-based RBAC exactly | Medium | High | Map BR-021 (Grade ≥ 8 full access, 5–7 view-all, <5 own-only) to RLS policies; validate with integration tests before cutover |

---

## 5. Build vs Buy Decisions

| Component | Decision | Rationale | Chosen Vendor/Tool | Alternative Considered |
|---|---|---|---|---|
| **HR Core (employee, payroll, leave)** | Build | Deep custom logic; direct deposit unimplemented; payroll tax calculations bespoke | Custom (FastAPI + PostgreSQL) | Workday, SAP SuccessFactors — overkill and costly for this scale |
| **Authentication & SSO** | Buy (managed) | Do not reimplement authentication — existing system has stub auth (BR-042); no value in custom OAuth2 server | Auth0 (phase 1) → Keycloak (phase 2) | Custom JWT — ruled out after reviewing current auth gaps |
| **Email delivery** | Buy (managed) | UTL_SMTP to port 25 unauthenticated is a deliverability and compliance risk | AWS SES | SendGrid, Mailgun — all acceptable; SES preferred for AWS-native integration |
| **Secret / key management** | Buy (managed) | Hardcoded keys in source code is critical risk; do not implement custom key rotation | AWS KMS + Secrets Manager | HashiCorp Vault — viable for multi-cloud; adds ops complexity in phase 1 |
| **ACH / Nacha file generation** | Buy (library) | Nacha file format is standardised; validated libraries exist; do not hand-code format | `nacha` Python library | Custom formatter — ruled out; format errors cause bank rejection |
| **PDF payslip generation** | Buy (library) | Standard document generation; no value in custom renderer | WeasyPrint or ReportLab | Puppeteer (adds Node dependency) |
| **Full-text employee search** | Build (phase 1) | PostgreSQL tsvector handles name/number search at this scale | PostgreSQL `tsvector` + GIN index | OpenSearch — deferred to phase 3 when search complexity justifies it |
| **Reporting / BI** | Buy (SaaS) | RPT_* tables were never populated; no reporting infrastructure exists; buying avoids rebuilding | Metabase (self-hosted) or AWS QuickSight | Custom React charts — deferred; Metabase gives HR team self-service reporting faster |
| **Container registry** | Buy (managed) | No value in running a private registry | Amazon ECR | Docker Hub — security concern; JFrog Artifactory — overkill |
| **Monitoring / observability** | Build (open source) | Grafana stack is open source and sufficient; vendor lock-in concern with Datadog/New Relic at this scale | Prometheus + Grafana + Loki + Tempo | Datadog — $$$; New Relic — $$$; viable if team prefers SaaS ops |
| **CI/CD** | Buy (SaaS) | GitHub Actions is free for the scale; no value in self-hosted Jenkins | GitHub Actions + ArgoCD | Jenkins — operational overhead; CircleCI — viable alternative |
| **Background jobs** | Build (open source library) | Celery is the standard Python task queue; no value in custom scheduler | Celery + Redis | AWS Lambda + EventBridge — increases cost and cold-start latency for payroll batch |
| **UI component library** | Buy (open source) | shadcn/ui provides accessible, production-quality components; do not build data tables and comboboxes from scratch | shadcn/ui + Radix UI | Ant Design, MUI — heavier bundle; MUI has more Oracle-Forms-like grid components (consider for phase 1 if team prefers) |
| **LDAP / AD sync** | Buy (Keycloak) | `sync_org_structure` in Oracle is a stub; Keycloak has native LDAP/AD federation built in | Keycloak user federation | Custom LDAP client — ruled out; BR-ORG-01 shows the stub was never implemented |

---

## 6. Technology Roadmap (Phased Adoption)

### Phase 0 — Foundation (Months 1–2)
*Goal: CI/CD, IaC, dev environment. Zero production user impact.*

| Task | Owner | Tool/Technology | Exit Criteria |
|---|---|---|---|
| Set up GitHub repository with branch protection | DevOps | GitHub | Main branch requires PR + passing CI |
| Implement secret scanning in CI | DevOps | detect-secrets, gitleaks | Hardcoded key pattern blocked on commit |
| Provision AWS VPC, EKS cluster, RDS PostgreSQL (staging) | DevOps | Terraform | Staging cluster accessible; RDS reachable from EKS |
| Set up ECR container registry | DevOps | Terraform | Push/pull from GitHub Actions working |
| Configure ArgoCD for GitOps delivery | DevOps | Helm, ArgoCD | Staging deploy triggered by merge to main |
| Deploy Grafana observability stack to staging | DevOps | Helm | Prometheus scraping, Loki receiving, Grafana accessible |
| Document Oracle→PostgreSQL type mapping decisions | Architect | ADR documents | All DISC-001/DISC-002 discrepancies resolved |
| Run AWS Schema Conversion Tool on Oracle DDL | Migration | AWS SCT | PostgreSQL DDL generated; incompatibilities listed |

### Phase 1 — Core Backend + Auth (Months 3–6)
*Goal: Functional API covering employee lifecycle, leave, and authentication. No Oracle Forms replacement yet.*

| Module | Key Deliverables | Critical Path Items |
|---|---|---|
| Auth service | Keycloak deployment; JWT issuance; grade→RBAC scope mapping; password Argon2id; MFA support | Replace BR-042 (stub auth) before any production traffic |
| Employee API | CRUD endpoints; EMPLOYEE_HISTORY write path; hire/transfer/terminate flows | Resolve DISC-001 (hire date limit) before building validation |
| PostgreSQL schema | All 30+ confirmed tables migrated via Alembic; RLS policies for RBAC; PII columns using KMS-backed encryption | Key rotation capability required from day 1 |
| Leave API | Balance initialisation; accrual (fix BR-LIB-05 overwrite bug); request/approval workflow | `run_monthly_accrual` increment bug must be fixed — do not port defect |
| Audit log | Structured event log via structlog → Loki; outbox pattern for async events | Replace free-text AUDIT_LOG before cutover |
| CI pipeline | All stages 1–4 (lint, security scan, tests, coverage gate) | 80% unit test coverage gate before phase 2 begins |
| Data migration (staging) | DMS task for non-PII tables; PII re-encryption script tested on staging | AWS DMS full-load test with validation query counts |

### Phase 2 — Payroll, Compliance, and Integrations (Months 7–11)
*Goal: Implement the unimplemented — direct deposit, COBRA, final pay. Replace UTL_FILE integrations.*

| Module | Key Deliverables | Critical Path Items |
|---|---|---|
| Payroll engine | `calculate_payroll` Python reimplementation; fix HOH federal tax $0 defect; fix PAID orphan (DISC-009) | Test oracle: run parallel on Oracle and Python; compare net pay to 6 decimal places |
| Direct deposit (ACH) | EMPLOYEE_BANK_ACCOUNTS read path; Nacha prenote flow; ACH file generation; disbursement status on PAYROLL_RUNS | VQ-BA-01 must be resolved (encryption key confirmation) before build |
| COBRA notification | Qualifying event detection on termination; 14-day notification workflow; dependent inactivation policy | Legal sign-off on VQ-TERM-02 (immediate vs held-for-election) before build |
| Final pay calculation | `calculate_final_pay` implementation (did not exist in Oracle); proration; off-cycle run support | VQ-TERM-04 (PTO payout policy) must be confirmed before build |
| ADP benefits feed | S3-based fixed-width file generation; add `BENEFITS_ENROLLED` filter (currently missing); SFTP delivery to ADP | Confirm ADP specification version (TD-73) |
| GL journal feed | PostgreSQL-based journal generation; `GL_FEED_SENT_DATE` tracking on PAYROLL_RUNS | Oracle Financials Journal Source/Category confirmation (TD-79) |
| Performance management | Review cycle + calibration workflow; `CALIBRATED_RATING` write path; `get_rating_distribution` reads calibrated not raw rating | Confirm calibration business process with HR before building status machine |
| React frontend (phase 1 screens) | Employee master; leave request/approval; payroll run monitoring dashboard | Oracle Forms UX research must complete before sprint 1 of UI build |

### Phase 3 — Frontend Completion and Production Cutover (Months 12–16)
*Goal: Full Oracle Forms replacement. Production cutover with parallel running.*

| Task | Key Deliverables |
|---|---|
| Complete React frontend | All Oracle Forms screens replaced; Playwright E2E tests covering golden paths |
| Reporting / BI | Materialised views replacing RPT_* tables; Metabase dashboards for HR team |
| LDAP/AD sync | Keycloak LDAP federation replacing `sync_org_structure` stub (BR-ORG-01) |
| Org hierarchy | `WITH RECURSIVE` PostgreSQL CTE + closure table for deep hierarchy; replaces CONNECT BY |
| Production data migration | DMS full-load + CDC replication; PII re-encryption; cutover weekend with rollback plan |
| Oracle decommission | Oracle licence termination; HRMS schema drop; Oracle Forms server decommission |
| Post-go-live observability | SLA dashboard live; on-call runbook published; Grafana Faro RUM monitoring active |

### Phase 4 — Optimisation (Months 17–20)
*Goal: Performance, scale, and operational maturity.*

| Task | Technology |
|---|---|
| OpenSearch for employee search | OpenSearch + Logstash pipeline from PostgreSQL |
| Payroll performance test | k6 load test simulating 10,000-employee payroll run; tune connection pool |
| Event-driven notifications | Migrate from outbox polling to event-driven (SNS + SQS fan-out) |
| Service extraction (optional) | Extract notification service and reporting service from modular monolith if scale requires |
| DR drill | RDS failover test; EKS node failure test; runbook validation |

---

## 7. Proof of Concept Recommendations

The following PoCs should be completed during Phase 0 / early Phase 1 before full investment in each area. Each PoC has a fixed time-box and a go/no-go decision point.

### PoC-01: Oracle PL/SQL → Python Payroll Calculation (3-week time-box)

**Question:** Can the payroll calculation (`calculate_employee_pay`) be reimplemented in Python with results that match Oracle to 6 decimal places on a representative dataset?

**Success criteria:**
- Seed 50 employee records with known Oracle output (gross, net, taxes, deductions)
- Python implementation produces identical output within floating-point tolerance
- HOH federal tax defect fixed and verified in Python output
- MARRIED_FILING_JOINTLY and SINGLE paths both validated

**Risk if PoC fails:** Unknown PL/SQL logic not captured in BA analysis; extend analysis phase before build.

---

### PoC-02: Oracle → PostgreSQL Data Migration (2-week time-box)

**Question:** Can AWS DMS migrate the Oracle HRMS schema to PostgreSQL without data loss, with PII re-encryption intact?

**Success criteria:**
- DMS full-load task completes without error on staging Oracle instance
- Row counts match on all 30+ tables
- PII re-encryption script runs in under 4 hours on full dataset size
- Alembic migrations apply cleanly on fresh PostgreSQL instance

**Risk if PoC fails:** Manual migration scripts required; extend Phase 0 timeline.

---

### PoC-03: Keycloak Grade-Based RBAC (1-week time-box)

**Question:** Can Keycloak issue JWTs with grade-derived scopes that the FastAPI middleware can enforce at endpoint level, replicating BR-021?

**Success criteria:**
- Grade 9 user JWT contains `hrms:employees:write:all` scope
- Grade 6 user JWT contains `hrms:employees:read:all` but not `write:all`
- Grade 3 user JWT contains `hrms:employees:read:own` only
- FastAPI dependency decorator enforces scope without hitting the database

**Risk if PoC fails:** Custom RBAC middleware required; add 2-week buffer to Phase 1 auth track.

---

### PoC-04: React Oracle Forms Replacement (2-week time-box)

**Question:** Can the HRMS_EMPLOYEE Oracle Form (most complex: multi-record blocks, LOVs, nested detail blocks) be replicated in React with TanStack Table and shadcn/ui within a realistic sprint?

**Success criteria:**
- Employee list with pagination and column sort (replaces multi-record block)
- Employee detail form with field validation (replaces WHEN-VALIDATE-ITEM triggers)
- Department LOV with async search (replaces LOV_DEPARTMENTS)
- Salary history tab with read-only grid (replaces SALARY_RECORDS detail block)

**Risk if PoC fails:** Evaluate MUI DataGrid as an alternative to TanStack Table; may require more sprint capacity than planned.

---

### PoC-05: Nacha ACH File Generation (1-week time-box)

**Question:** Can the Python `nacha` library generate a valid Nacha PPD ACH file for a sample 10-employee payroll run that passes an ACH validation tool?

**Success criteria:**
- Generate PPD batch file for 10 employees with FULL and PARTIAL_PERCENT deposit types
- File validates with Nacha validation tool (no format errors)
- Prenote entry generated for new account (P-00 code)
- Balanced against control totals

**Risk if PoC fails:** Evaluate `achgateway` (Go-based) as an alternative; or buy ACH-as-a-service (Plaid, Modern Treasury).

---

## 8. Vendor Evaluation Matrix

### 8.1 Cloud Provider

| Criterion | Weight | AWS | Azure | GCP | Score (AWS) | Score (Azure) | Score (GCP) |
|---|---|---|---|---|---|---|---|
| Managed PostgreSQL quality | 20% | Aurora PostgreSQL | Azure DB for PostgreSQL | Cloud SQL | 9 | 8 | 8 |
| Oracle migration tooling (DMS + SCT) | 20% | AWS DMS (native Oracle source) | SSMA (SQL Server focus) | Database Migration Service | 9 | 6 | 7 |
| EKS / Managed K8s maturity | 15% | EKS (mature) | AKS (mature) | GKE (most automated) | 8 | 8 | 9 |
| Secrets management | 10% | Secrets Manager + KMS | Key Vault | Secret Manager | 9 | 9 | 8 |
| HR/payroll compliance certs | 10% | SOC2, HIPAA, PCI | SOC2, HIPAA, PCI | SOC2, HIPAA, PCI | 9 | 9 | 9 |
| Team familiarity | 15% | Depends on team | Depends on team | Depends on team | 7 | 7 | 7 |
| Cost at 500-employee scale | 10% | Moderate | Moderate | Slightly lower | 7 | 7 | 8 |
| **Weighted total** | 100% | | | | **8.4** | **7.6** | **7.9** |

**Recommendation: AWS** — highest score driven by Oracle DMS tooling quality and Aurora PostgreSQL reliability. Revisit if team has strong Azure or GCP expertise.

---

### 8.2 Authentication Provider

| Criterion | Weight | Auth0 | Keycloak (self-hosted) | AWS Cognito | Okta |
|---|---|---|---|---|---|
| LDAP/AD federation | 15% | 9 | 10 | 6 | 9 |
| OIDC / OAuth2 compliance | 20% | 10 | 10 | 9 | 10 |
| MFA support | 10% | 10 | 9 | 8 | 10 |
| Fine-grained authorisation (RBAC scopes) | 20% | 8 | 10 | 7 | 9 |
| Operational complexity | 15% | 2 (SaaS — low ops) | 8 (high ops) | 3 (moderate) | 2 (SaaS — low ops) |
| Cost at 500-user scale | 15% | 6 ($$$) | 10 (free) | 9 (low cost) | 5 ($$$) |
| Phase 1 speed to implement | 5% | 9 | 6 | 8 | 9 |
| **Weighted total** | 100% | **7.5** | **9.2** | **7.3** | **7.9** |

**Phase 1 recommendation: Auth0** (lower operational burden while team ramps up). **Phase 2 recommendation: Migrate to self-hosted Keycloak** once ops team is ready, driven by cost and LDAP federation quality for `sync_org_structure` replacement.

---

### 8.3 Monitoring / Observability Stack

| Criterion | Weight | Grafana OSS Stack | Datadog | New Relic | AWS CloudWatch |
|---|---|---|---|---|---|
| Metrics (Prometheus-native) | 20% | 10 | 9 | 8 | 6 |
| Log aggregation | 20% | 9 (Loki) | 9 | 9 | 7 |
| Distributed tracing | 20% | 9 (Tempo + OTel) | 9 | 8 | 6 (X-Ray) |
| Alerting | 10% | 8 | 10 | 9 | 7 |
| Cost at this scale | 20% | 10 (free OSS) | 4 ($$$) | 5 ($$) | 7 (pay-per-use) |
| Operational complexity | 10% | 6 (self-managed) | 10 (SaaS) | 10 (SaaS) | 8 (managed) |
| **Weighted total** | 100% | **9.0** | **8.2** | **8.2** | **6.7** |

**Recommendation: Grafana OSS stack** (Prometheus + Loki + Tempo + Grafana). Cost advantage is decisive at this scale. If operational overhead becomes a problem post-phase-1, evaluate Grafana Cloud (managed version of the same stack).

---

### 8.4 Background Job Queue

| Criterion | Weight | Celery + Redis | AWS SQS + Lambda | Bull (Node) | Temporal |
|---|---|---|---|---|---|
| Python-native integration | 25% | 10 | 7 | 2 | 8 |
| Scheduled jobs (cron replacement for DBMS_SCHEDULER) | 25% | 9 (beat) | 8 (EventBridge) | 7 | 9 |
| Long-running payroll batch jobs | 20% | 9 | 6 (15-min Lambda limit) | 6 | 10 |
| Operational complexity | 15% | 7 | 9 | 7 | 5 |
| Dead-letter queue / retry | 15% | 8 | 10 | 8 | 10 |
| **Weighted total** | 100% | **8.9** | **7.7** | **5.3** | **8.5** |

**Recommendation: Celery + Redis** for phases 1–2. Evaluate **Temporal** for phase 3 if payroll workflow orchestration complexity grows (Temporal excels at multi-step long-running workflows like the payroll lifecycle).

---

## Appendix A: Immediate Pre-Migration Technical Decisions Required

The following decisions from the BA/DA/TA analysis must be resolved before implementation begins. Each carries an owner and a deadline relative to Phase 1 start.

| ID | Decision Required | Source Finding | Owner | Deadline |
|---|---|---|---|---|
| ADR-01 | Hire date future limit: 90 days (Forms) or 180 days (DB trigger)? | DISC-001 | HR Business Owner | Phase 0, Week 2 |
| ADR-02 | EMPLOYEE_HISTORY column layout: typed columns (DDL) or VARCHAR2 old/new value? | DISC-002 | DBA + Architect | Phase 0, Week 2 |
| ADR-03 | ACCOUNT_NUMBER_ENC: same AES key as SSN_ENCRYPTED? | VQ-BA-01 | DBA | Phase 0, Week 1 |
| ADR-04 | COBRA: inactivate dependents immediately on termination, or hold for election period? | VQ-DEP-04, VQ-TERM-02 | Legal + HR | Phase 1, Month 2 |
| ADR-05 | Is `sync_org_structure` currently scheduled? Does any monitoring tool read its log? | VQ-ORG-03 | DBA | Phase 0, Week 2 |
| ADR-06 | Are RPT_* tables present in production DDL and do they contain data? | G1-NEW-01 | DBA | Phase 0, Week 2 |
| ADR-07 | Oracle Financials GL feed: correct Journal Source and Category values | TD-79 | Finance IT | Phase 2, Month 1 |
| ADR-08 | Direct deposit: NACHA ACH file or bank API or manual? | VQ-BA-03 | Finance + Payroll | Phase 1, Month 3 |
| ADR-09 | Performance calibration: mandatory gate or optional? Who triggers it? | (Performance gap) | HR Business Owner | Phase 2, Month 1 |
| ADR-10 | PTO payout on termination: cash out, forfeit, or depends on state? | VQ-TERM-04 | Legal + HR | Phase 2, Month 1 |

---

## Appendix B: Security Debt Cleared by Migration

This table confirms that all critical security findings from the TA analysis are remediated by the target stack.

| Finding ID | Vulnerability | Current Risk | Target Stack Resolution |
|---|---|---|---|
| TD-01 | Hardcoded AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` | Critical | AWS KMS — keys never in source code |
| TD-10 | FTP credentials in cleartext | Critical | AWS Secrets Manager — no credentials in code |
| BR-042 | Authentication stub — password never verified | Critical | Keycloak OIDC — proper credential verification |
| DQ-010 | MD5 password hashing | Critical | Argon2id via passlib |
| DQ-003 | Auth stub — any username authenticated | Critical | Keycloak replaces entire auth path |
| DQ-029 | `change_password` never verifies old password | High | Keycloak change-password flow enforces old credential |
| BR-043b | Duplicate email → silent login as wrong employee | High | Keycloak unique-username enforcement at IdP level |
| TD-46 | Routing numbers stored plaintext | Low | Encrypted with KMS-backed key in migration |
| TD-81 | Portal connects as schema owner | Medium | Dedicated IAM role + least-privilege DB user |
| PP-BA-03 | ACH prenote not implemented (Nacha compliance) | High | Implemented in Phase 2 Nacha integration |
| PP-TERM-01 | COBRA qualifying events not reported | Critical | Implemented in Phase 2 COBRA notification service |
| TD-75 | Stale sessions never cleaned up | Medium | JWT expiry (15 min) + Keycloak session revocation |
