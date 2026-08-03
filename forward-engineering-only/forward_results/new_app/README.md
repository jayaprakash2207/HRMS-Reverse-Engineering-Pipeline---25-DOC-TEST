# HRMS — Forward Engineering Skeleton

Java 17 / Spring Boot 3 backend, React + TypeScript frontend, PostgreSQL database. Security/Identity is the first implemented sprint: JWT-based authentication (login/refresh/logout) replacing the confirmed authentication-bypass defect, plus the shared PII-encryption infrastructure needed before any other bounded context is safe to build on.

## Layout

```
.
├── backend/           Spring Boot 3 (Java 17), Maven
├── frontend/           React + TypeScript, Vite
└── docker-compose.yml   Local PostgreSQL for development
```

## Prerequisites

- JDK 17
- Maven 3.9+
- Node.js 20 LTS + npm
- Docker (for local PostgreSQL and Testcontainers-based integration tests)

## 1. Start PostgreSQL

```
docker compose up -d
```

Starts a `postgres:16-alpine` container on `localhost:5432` with database `hrms`, user `hrms`, password `hrms`.

## 2. Configure required secrets

This sprint introduces mandatory externalized secrets - there is no hard-coded fallback, by design (see `STACK_MAPPING_CONTRACT.md`, row 6). Copy `backend/.env.example` to `backend/.env`, fill in real values, and export them into your shell before running the backend:

- `JWT_SECRET` — base64-encoded, >= 256 bits. Generate with `openssl rand -base64 32`. **Required** — the app fails to start without it.
- `HRMS_PII_ENCRYPTION_KEY` — base64-encoded 256-bit AES key backing `EncryptedStringConverter`. Not required to run this sprint's endpoints; needed once another context applies the converter to a PII column (e.g. Employee's SSN).

## 3. Run the backend

```
cd backend
mvn spring-boot:run
```

Starts the API on `http://localhost:8080`. Flyway migrations run automatically on startup against the database above (override connection details with the `DB_URL`, `DB_USERNAME`, `DB_PASSWORD` environment variables).

Verify it's up:

```
curl http://localhost:8080/api/v1/health
```

Log in (after seeding a `user_credentials` row - no self-registration endpoint exists yet; provisioning credentials is out of this sprint's scope, see Open Questions below):

```
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane.doe@example.com","password":"correct-horse-battery-staple"}'
```

Run backend tests (spins up Testcontainers Postgres for the integration test):

```
mvn test
```

## 4. Run the frontend

```
cd frontend
npm install
npm run dev
```

Starts the dev server on `http://localhost:5173`.

Run frontend tests:

```
npm test
```

Build for production:

```
npm run build
```

## Conventions

Both projects follow this repo's Stack Mapping Contract:

- **Backend:** package-by-feature (`com.clarium.hrms.{module}`), each with `controller/`, `service/`, `repository/`, `domain/`, `dto/`, `validator/` sub-packages; shared/cross-cutting code in `com.clarium.hrms.common`. Flyway is the only path for schema changes (`src/main/resources/db/migration`). Constructor injection only (no field `@Autowired`). Entities are never returned from controllers.
- **Frontend:** `src/features/{module}/{components,hooks,api,types}` per module, `src/shared/` for cross-feature code. Components `PascalCase.tsx`, hooks `useCamelCase`, tests co-located as `Xxx.test.tsx`.
- No feature modules are pre-scaffolded — they're added only once real business rules/modules are confirmed.

## Security/Identity sprint notes

- `POST /api/v1/auth/login`, `/refresh`, `/logout` are stateless-JWT (no server-side session). Access tokens carry `email`/`role`/`employeeId` claims; the JWT filter trusts these for the token's lifetime — an account locked mid-token-life stays valid until expiry, a deliberate stateless-vs-freshness tradeoff.
- `user_credentials` (migration `V1.1`) is a net-new table/entity, not a port of anything from `PKG_SECURITY` — that package's `authenticate()` is a confirmed bypass and was not used as reference for anything, including its bugs.
- **Open question carried over from the BRD (OQ-001):** no endpoint exists yet to create `user_credentials` rows — that was out of this sprint's specified contract (only login/refresh/logout are defined in `13_API_CONTRACT_SPECIFICATION.md` §6). Provisioning credentials (likely from the Employee Management context's hire flow) needs a business decision before it's built.
- `EncryptedStringConverter` / `EncryptionKeyProvider` / `SecretResolver` (`com.clarium.hrms.security.crypto`) provide the AES-256-GCM, runtime-resolved-key capability needed to close the hard-coded SSN key defect. They are not yet attached to any entity — Employee Management owns the SSN column — but the capability now exists so that context isn't tempted to reintroduce a hard-coded key.
