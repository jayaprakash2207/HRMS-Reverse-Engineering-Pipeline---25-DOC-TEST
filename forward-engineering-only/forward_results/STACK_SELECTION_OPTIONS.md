## Stack Selection — Candidate Target Technology Stacks

### Grounding note on what these candidates can and cannot be justified against

The NFR Specification (`14_NFR_SPECIFICATION.md` §8) explicitly states that performance/throughput targets, availability/uptime SLAs, and scalability targets have **no evidence in the EKG** and must not be fabricated. Team familiarity is also not stated anywhere in the supplied blueprint or NFRs. Accordingly, the candidates below are justified only against what *is* evidenced: reliability (NFR-R1, NFR-R2), security (NFR-S1–S3), maintainability (NFR-M1–M3), observability/CI-CD (NFR-O1), data integrity (NFR-D1, NFR-D2), and usability/functional completeness (NFR-U1). None of these three options should be read as "sized" for a particular scale — that decision remains open pending stakeholder input, per Technology Blueprint §4.

All three options assume application-tier-owned, versioned migrations replacing trigger-based side effects (Technology Blueprint §3.1), and all three treat RDBMS vendor, backend language, and frontend framework as independently decided, per §4 of the blueprint's decision log — no candidate below should be taken as a recommendation, only as a coherent bundle.

---

## Option 1 — Stay close to Oracle, modernize the tiers

**Frontend:** React (SPA, decoupled from backend)
**Backend:** Java 17, Spring Boot
**Database:** Oracle Database (existing `SCHEMA-001` retained, no schema migration)

**Rationale:**
- Retaining Oracle avoids re-validating all 30 tables of `SCHEMA-001` under a new engine while the schema's own completeness is still uncertain (`ASMP-002`, `NFR-D2`) — lowest data-migration risk of the three options.
- Spring Security gives NFR-S1 (mandatory credential verification) and NFR-S3 (externally managed encryption keys, e.g. via Spring Cloud Vault/AWS KMS) off-the-shelf, directly replacing the hard-coded `PKG-SECURITY` AES key defect.
- Spring's `@Transactional` + an outbox/event table gives a straightforward mechanism to satisfy NFR-R2 (audit write must not fail silently) — the audit write and the business transaction commit atomically.
- Business rules (`BR-*`) map cleanly onto Spring `@Service` beans, one per rule, satisfying NFR-M1 (single-sourced rule modules) once rule content is available (`OQ-003`).
- Flyway/Liquibase (standard in the Spring ecosystem) gives the "application-tier-owned, versioned migrations" required by Technology Blueprint §3.1, replacing the trigger-based `EMPLOYEE_HISTORY` side effects that caused `TD-11`/`TD-12`.
- Spring Boot Actuator + Micrometer provides a ready path to close the 0/14 CI/CD-observability gap (NFR-O1).
- Tradeoff: continued Oracle licensing/ops cost, and this option does the *least* to escape the vendor lock-in implicit in the legacy system — appropriate only if licensing/ops constraints (explicitly out of scope for this document, per §4) favor staying on Oracle.

---

## Option 2 — Open-source relational stack, single-language full stack

**Frontend:** React (or Next.js for the same team to own SSR/SPA concerns)
**Backend:** Node.js, NestJS (TypeScript)
**Database:** PostgreSQL (migration off Oracle)

**Rationale:**
- PostgreSQL with `pgcrypto`/`pgsodium` plus an external secrets manager (Vault, AWS/GCP KMS) satisfies NFR-S3 (externalized key management) without proprietary licensing, and PostgreSQL's strict constraint/trigger-free-by-default modeling supports NFR-R1 (referential integrity must not fail as an unhandled runtime error) when enforced at the application tier instead of in DB triggers.
- NestJS's module system maps almost one-to-one onto "one rule module per `BR-*`" (NFR-M1) — its dependency-injection graph can also be introspected and diffed against architecture docs, directly supporting the CI gate required by NFR-M2 (docs must match the deployable artifact).
- TypeScript end-to-end (NestJS backend + React/Next.js frontend) means the same team can own both the manager-inbox UI required by NFR-U1 (`PP-leave-approval-gap`) and its backing API without a language switch — relevant since a currently-Oracle-Forms-only team may have limited exposure to any of these candidates equally; this reduces the *number* of new languages learned to one instead of two.
- TypeORM/Prisma migrations give the versioned, application-owned migration path required in place of trigger-driven `EMPLOYEE_HISTORY` writes.
- Tradeoff: full data migration off Oracle is the highest-risk item in this option — 28 of 30 tables are not explicitly confirmed to this synthesis (NFR-D2), so migration scripting must be validated against a full DDL dump before this path is committed to, not just the 2 confirmed tables.

---

## Option 3 — Enterprise .NET stack

**Frontend:** Angular
**Backend:** C#, ASP.NET Core (.NET 8)
**Database:** SQL Server (or PostgreSQL via Npgsql, if licensing is a concern)

**Rationale:**
- ASP.NET Core Identity + `Microsoft.AspNetCore.DataProtection` (with an external key ring provider, e.g. Azure Key Vault) directly satisfies NFR-S1–S3, replacing both the `PKG-SECURITY.authenticate` bypass and the hard-coded key defect with framework-native, externally-keyed primitives.
- EF Core migrations are a natural fit for the "application-tier-owned, versioned migrations" requirement (Technology Blueprint §3.1), and EF Core's change-tracking plus a `SaveChangesAsync` interceptor gives a clean single-transaction path for NFR-R2 (audit write cannot fail silently — interceptor fails the parent `SaveChanges` if the audit insert fails).
- Angular's opinionated, module-based structure (services, dependency injection, reactive forms) is a reasonable fit for a system whose predecessor was a forms-heavy Oracle Forms application (Technology Blueprint §3.3) — reactive forms in particular suit the still-missing manager leave-approval screen (NFR-U1) and other data-entry-heavy HR screens, without implying a literal screen-by-screen port (explicitly disallowed).
- Built-in `ILogger`/OpenTelemetry support in .NET 8 gives a direct path to closing the 0/14 CI/CD-observability gap (NFR-O1).
- Tradeoff: if SQL Server is chosen, this reintroduces a commercial-licensing consideration similar to Oracle (though typically at lower cost); choosing PostgreSQL under this option removes that concern but is less "batteries-included" with EF Core than SQL Server is.

---

### What is deliberately not decided here

Per Technology Blueprint §4, this document does not choose among these options. RDBMS vendor (stay-on-Oracle vs. migrate), sync-vs-async processing for payroll (`VS-04`), and deployment target (Technology Blueprint §3.4, `18_DEPLOYMENT_ARCHITECTURE.md`) all remain stakeholder decisions. Team familiarity with Java/Spring, TypeScript/Node, or C#/.NET was not supplied anywhere in the source material and could materially change which of these three is cheapest to execute — that input should be sought before finalizing.

```json
[
  {"id": 1, "frontend": "React", "backend": "Java 17, Spring Boot", "database": "Oracle Database (existing schema retained)"},
  {"id": 2, "frontend": "React (or Next.js)", "backend": "Node.js, NestJS (TypeScript)", "database": "PostgreSQL (migrated off Oracle)"},
  {"id": 3, "frontend": "Angular", "backend": "C#, ASP.NET Core (.NET 8)", "database": "SQL Server (or PostgreSQL via Npgsql)"}
]
```