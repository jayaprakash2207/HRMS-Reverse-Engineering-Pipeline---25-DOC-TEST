# 11 — API Contract Specification
**System:** Acme Corporation HRMS — New System (Replacement for Oracle HRMS 19c / Oracle Forms 12c)
**Version:** 1.0.0
**Status:** Draft — Forward Engineering
**Prepared By:** API Architecture Track
**Source Analysis:** BA_Deep_Analyst (BR-01–BR-140), DA_Data_Reviewer, TA_Deep_Analyst, AA_Quality_Review, Domain Model BC-01–BC-10
**Date:** 2026-08-05

---

## Table of Contents

1. [API Design Principles](#1-api-design-principles)
2. [API Groups Summary](#2-api-groups-summary)
3. [Authentication & Authorization](#3-authentication--authorization)
4. [Error Response Standard](#4-error-response-standard)
5. [Rate Limiting Policy](#5-rate-limiting-policy)
6. [Pagination & Filtering](#6-pagination--filtering)
7. [Employee Management APIs](#7-employee-management-apis)
8. [Payroll APIs](#8-payroll-apis)
9. [Leave Management APIs](#9-leave-management-apis)
10. [Performance APIs](#10-performance-apis)
11. [Security APIs](#11-security-apis)
12. [Reporting APIs](#12-reporting-apis)
13. [Webhook Events](#13-webhook-events)

---

## 1. API Design Principles

### 1.1 Architectural Style

The replacement HRMS exposes a **RESTful HTTP/1.1 API** using JSON as the canonical data format. All endpoints follow resource-oriented design: nouns in paths, HTTP verbs for intent.

| Principle | Decision | Rationale |
|-----------|----------|-----------|
Looking at the source, `create_payroll_run` returns a `RUN_ID` (from `SEQ_PAYROLL_RUN.NEXTVAL`) and `calculate_payroll` transitions `STATUS` through `PENDING → CALCULATING → CALCULATED / ERROR`. I'll use those to fill the async contract row.

---

Looking at the source content, `PKG_PAYROLL.pkb` explicitly writes three of the four statuses (`PENDING` in `create_payroll_run`, `CALCULATING` and then `CALCULATED`/`ERROR` in `calculate_payroll`). The DDL file `PAYROLL_RUNS.sql` was not found, so exhaustiveness cannot be confirmed from a constraint. I'll add a targeted [GAP-FILLED] annotation to the existing async-operations cell.

---

| Style | REST over HTTPS (TLS 1.3 minimum) | Replaces Oracle Forms RPC; interoperable with self-service portal, mobile, and BI tools |
| Data Format | `application/json` for all request/response bodies | Replaces Oracle fixed-width flat files and pipe-delimited GL feeds |
| Versioning | URI path prefix (`/api/v1/`) | Breaking changes get `/v2/`; v1 supported minimum 24 months after v2 GA |
| Encoding | UTF-8 throughout | Replaces Oracle NLS_CHARACTERSET-dependent Forms output |
| Idempotency | `Idempotency-Key` header required on POST operations that create records or trigger financial transactions | Prevents duplicate payroll runs (addresses DISC-009 / BR-BA-12 — orphaned PAID status) |
| Nullability | JSON fields explicitly `null` when absent; missing keys indicate field not returned in this view | Distinguishes "not set" from "not applicable" |
| Time | All timestamps in ISO 8601 UTC (`2024-01-15T09:30:00Z`); all date-only fields in `YYYY-MM-DD` | Replaces Oracle `DATE` type with implicit server timezone |
| Currency | All monetary values as JSON number with 2 decimal places; currency code separate field | Replaces Oracle `NUMBER(12,2)` implicit USD |
| [GAP-FILLED] Async Operations | `202 Accepted` responses for long-running operations (payroll run, report generation) **must** include: (1) a `jobId` field in the response body (mapped to `PAYROLL_RUNS.RUN_ID` / report run ID), (2) a `Location` response header pointing to the canonical status resource (e.g. `Location: /api/v1/payroll/runs/{runId}`), and (3) a `retryAfter` field (seconds) advising the minimum polling interval. Callers poll `GET /api/v1/payroll/runs/{runId}` (or equivalent report endpoint) and inspect the `status` field. Terminal statuses sourced from `PAYROLL_RUNS.STATUS`: `PENDING` → `CALCULATING` → `CALCULATED` (success) or `ERROR` (failure with `errorCount` and `errorMessage` fields populated). [GAP-FILLED] **Status enum source verification:** All four statuses are confirmed present in `PKG_PAYROLL.pkb`: `PENDING` is written by `create_payroll_run` at INSERT time; `CALCULATING`, `CALCULATED`, and `ERROR` are written by `calculate_payroll` during and after the cursor loop. No additional statuses (`CANCELLED`, `APPROVED`, `REVERSED`, `POSTED`) were found in the recovered package body. However, `PAYROLL_RUNS.sql` (the table DDL) was not located in the deep scan, so a CHECK constraint or inline comment defining the full allowed set could not be verified — the enum **must be treated as potentially non-exhaustive** until the DDL is recovered. API consumers should treat any unrecognised `status` value as a non-terminal intermediate state and continue polling rather than erroring. [END GAP-FILLED] Webhook / callback alternative: callers may supply an optional `callbackUrl` in the POST request body; the platform issues a `POST {callbackUrl}` with the terminal-state payload when `status` reaches `CALCULATED` or `ERROR`. Callback delivery is best-effort with three retries (exponential back-off, 5 s / 25 s / 125 s); callers must not rely solely on the callback and should poll as a fallback. | Closes the observability gap for `PKG_PAYROLL.calculate_payroll` (row-by-row cursor loop, partial commits every 50 employees); callers can detect partial-error completion (`status: ERROR`, `errorCount > 0`) without timing out on a synchronous response |

### 1.2 Versioning Strategy

```
/api/v{major}/
```

- **Minor/patch changes** (additive fields, new optional parameters): deployed without version bump; clients must tolerate unknown fields.
- **Breaking changes** (field removal, type change, required field added, status code change): require new major version.
- **Deprecation timeline:** Deprecated endpoints return `Deprecation: true` and `Sunset: <RFC 7231 date>` headers with minimum 12-month runway.
- **Current version:** `v1`

### 1.3 Base URL

```
https://hrms.acme.com/api/v1
```

All paths in this document are relative to the base URL.

### 1.4 Authentication Approach

- **Primary:** JWT Bearer tokens issued by `/auth/login`
- **Service-to-Service:** OAuth 2.0 Client Credentials flow for integration partners (replaces PKG_INTEGRATION flat-file push model)
- **Session Model:** Stateless JWT; no server-side session table (replaces `USER_SESSIONS` table dependency and the 30-minute timeout bug — BR-72, DQ-027)
- **Token Lifetime:** Access token 15 minutes; Refresh token 8 hours (workday-aligned)

### 1.5 Design Rules Derived from Legacy Analysis

The following design rules are **directly derived from documented defects** in the Oracle HRMS source analysis:

| Rule | Legacy Defect Addressed |
|------|------------------------|
| `HEAD_OF_HOUSEHOLD` tax filing status must return a computed federal tax amount; API rejects payroll run if HOH employees have $0 federal tax | BR-40 / HOH returns $0 federal tax defect |
| Bank account routing number must be stored encrypted; API rejects account records with plain-text routing | TD-46 / BR-BA-04 — routing number stored plaintext |
| Disbursement step is mandatory before a payroll run reaches `COMPLETED`; API enforces NACHA ACH file generation | BR-BA-12 / PP-BA-01 — direct deposit non-functional |
| Calibration workflow is a first-class API state; `CALIBRATED_RATING` is writeable via dedicated calibration endpoint | PERFORMANCE_REVIEWS calibration gap |
| `change_password` must verify current password before accepting new password | DQ-029 / BR-044 — old password never verified |
| `org_sync` endpoint returns 422 if LDAP connection parameters are not configured | BR-ORG-01 — org sync stub |
| Termination triggers COBRA notification event synchronously within the same transaction | PP-TERM-01 — COBRA federal compliance gap |

---

## 2. API Groups Summary

| Group | Path Prefix | Bounded Context | Auth Required | Primary Consumers |
|-------|-------------|-----------------|---------------|-------------------|
| Authentication | `/auth` | BC-06 Security | Partial (login/refresh public) | All clients |
| Employee Management | `/employees` | BC-01 Employee Identity | Yes | HR Admin, Manager |
| Payroll | `/payroll` | BC-02 Compensation | Yes | Payroll Admin, Finance |
| Leave Management | `/leave` | BC-03 Leave Management | Yes | Employee, Manager, HR |
| Performance | `/performance` | BC-04 Performance | Yes | Employee, Manager, HR |
| Benefits | `/benefits` | BC-05 Benefits | Yes | HR Admin, Employee |
| Departments | `/departments` | BC-07 Org Structure | Yes | HR Admin, Manager |
| Reporting | `/reports` | BC-10 Reporting | Yes (Grade ≥ 5) | HR Admin, Finance, Executive |
| Integrations | `/integrations` | BC-09 Integration | Service Account | Payroll system, ADP, GL |
| Webhooks | `/webhooks` | All | Yes (Admin) | External subscribers |
| Admin | `/admin` | BC-06 Security | Yes (Grade ≥ 8) | System Admin |

**Total Endpoints Specified in This Document:** 58

---

## 3. Authentication & Authorization

### 3.1 JWT Token Structure

**Header:**
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "hrms-signing-key-v1"
}
```

**Payload (Access Token):**
```json
{
  "sub": "emp_00042",
  "employee_id": 42,
  "employee_number": "EMP-00042",
  "email": "jane.doe@acme.com",
  "grade": 7,
  "department_id": 10,
  "roles": ["EMPLOYEE", "MANAGER"],
  "permissions": [
    "employee:read:own",
    "employee:read:reports",
    "leave:submit",
    "leave:approve",
    "payroll:view:own"
  ],
  "iat": 1720166400,
  "exp": 1720167300,
  "jti": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "iss": "https://hrms.acme.com",
  "aud": "https://hrms.acme.com/api"
}
```

**Refresh Token Payload:**
```json
{
  "sub": "emp_00042",
  "token_family": "rf_xyz789",
  "iat": 1720166400,
  "exp": 1720195200,
  "jti": "refresh-jti-unique"
}
```

### 3.2 Role-Based Access Control

Roles are derived from the legacy `GRADE`-based access model (BR-021) but expressed as explicit role names to avoid the "Grade ≥ 8 = full access" anti-pattern.

| Role | Grade Equivalent | Description |
|------|-----------------|-------------|
| `EMPLOYEE` | 1–10 (all) | Read own records; submit leave; view own payslip |
| `MANAGER` | Grade with direct reports | All EMPLOYEE permissions + read/approve team data |
| `HR_SPECIALIST` | Designated HR staff | Create/update employees; view all leave; run payroll |
| `PAYROLL_ADMIN` | Designated payroll staff | Full payroll lifecycle; approve runs; generate disbursement |
| `HR_MANAGER` | Senior HR | All HR_SPECIALIST + compensation changes; terminate employees |
| `FINANCE_ANALYST` | Finance designation | Read compensation reports; view GL feeds |
| `EXECUTIVE` | Grade 9–10 | Org-wide reporting; headcount; compensation summary |
| `SYSTEM_ADMIN` | Grade 10 equivalent | User management; system parameters; webhook config |

### 3.3 Permission Matrix

| Endpoint Group | EMPLOYEE | MANAGER | HR_SPECIALIST | PAYROLL_ADMIN | HR_MANAGER | SYSTEM_ADMIN |
|----------------|----------|---------|---------------|---------------|------------|--------------|
| GET /employees/:id (own) | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| GET /employees/:id (reports) | — | ✓ | ✓ | — | ✓ | ✓ |
| GET /employees/:id (any) | — | — | ✓ | — | ✓ | ✓ |
| POST /employees | — | — | ✓ | — | ✓ | ✓ |
| POST /employees/:id/terminate | — | — | — | — | ✓ | ✓ |
| GET /payroll/runs | — | — | — | ✓ | ✓ | ✓ |
| GET /payroll/payslips/own | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| POST /payroll/runs | — | — | — | ✓ | — | ✓ |
| POST /payroll/runs/:id/approve | — | — | — | ✓ | — | ✓ |
| POST /leave/requests | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| POST /leave/requests/:id/approve | — | ✓ | ✓ | — | ✓ | ✓ |
| GET /leave/balance (own) | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| POST /performance/reviews | — | ✓ | ✓ | — | ✓ | ✓ |
| POST /performance/calibration | — | — | — | — | ✓ | ✓ |
| GET /reports/* | — | — | ✓ | ✓ | ✓ | ✓ |

### 3.4 Authorization Header

```
Authorization: Bearer <access_token>
```

All endpoints (except `/auth/login` and `/auth/refresh`) require this header. Missing or expired tokens receive `401 Unauthorized`. Insufficient permissions receive `403 Forbidden`.

---

## 4. Error Response Standard

All error responses use a consistent envelope regardless of HTTP status code.

### 4.1 Error Response Schema

```json
{
  "error": {
    "code": "EMPLOYEE_NOT_FOUND",
    "message": "No employee found with ID 9999.",
    "details": [],
    "request_id": "req_a1b2c3d4e5f6",
    "timestamp": "2024-01-15T09:30:00Z",
    "documentation_url": "https://hrms.acme.com/docs/errors#EMPLOYEE_NOT_FOUND"
  }
}
```

**Validation error with field-level details:**
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "One or more fields failed validation.",
    "details": [
      {
        "field": "salary",
        "code": "SALARY_OUTSIDE_GRADE_BAND",
        "message": "Salary $75,000 is outside the grade 5 band ($50,000–$70,000).",
        "value": 75000
      },
      {
        "field": "hire_date",
        "code": "HIRE_DATE_TOO_FAR_FUTURE",
        "message": "Hire date cannot be more than 90 days in the future.",
        "value": "2025-06-01"
      }
    ],
    "request_id": "req_xyz789",
    "timestamp": "2024-01-15T09:30:00Z"
  }
}
```

### 4.2 HTTP Status Code Usage

| Status | When Used |
|--------|-----------|
| `200 OK` | Successful GET, PUT, PATCH |
| `201 Created` | Successful POST that created a resource |
| `202 Accepted` | Long-running operation accepted (payroll run, report generation) |
| `204 No Content` | Successful DELETE |
| `400 Bad Request` | Malformed request body or invalid JSON |
| `401 Unauthorized` | Missing or invalid JWT |
| `403 Forbidden` | Valid JWT but insufficient permissions |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | State conflict (duplicate idempotency key; payroll run already in progress) |
| `422 Unprocessable Entity` | Request is syntactically valid but fails business rule validation |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server error (never leaks stack traces to client) |
| `503 Service Unavailable` | Downstream dependency unavailable (payroll engine, ACH provider) |

### 4.3 Standard Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `EMPLOYEE_NOT_FOUND` | 404 | No employee matching the given ID |
| `VALIDATION_FAILED` | 422 | One or more fields failed validation |
| `SALARY_OUTSIDE_GRADE_BAND` | 422 | Salary not within job grade min/max |
| `HIRE_DATE_TOO_FAR_FUTURE` | 422 | Hire date > 90 days in the future |
| `DUPLICATE_EMAIL` | 409 | Email already registered to active employee |
| `PAYROLL_RUN_IN_PROGRESS` | 409 | Cannot start a new run while one is CALCULATING |
| `PAYROLL_RUN_NOT_APPROVABLE` | 422 | Run is not in CALCULATED status |
| `LEAVE_INSUFFICIENT_BALANCE` | 422 | Requested days exceed available balance |
| `LEAVE_OVERLAP` | 409 | Leave request overlaps an existing approved request |
| `REVIEW_ALREADY_EXISTS` | 409 | A review for this employee in this cycle already exists |
| `CALIBRATION_NOT_PERMITTED` | 422 | Review not in COMPLETED status; calibration not possible |
| `COBRA_NOTIFICATION_REQUIRED` | 422 | Termination cannot complete without COBRA notification acknowledgement |
| `BANK_ACCOUNT_INVALID` | 422 | Routing number failed ABA checksum or account type invalid |
| `PRENOTE_REQUIRED` | 422 | New bank account requires ACH prenote before disbursement |
| `UNAUTHORIZED` | 401 | JWT missing, malformed, or expired |
| `FORBIDDEN` | 403 | Authenticated but action not permitted for role |
| `IDEMPOTENCY_CONFLICT` | 409 | Idempotency key already used with different request body |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests; see Retry-After header |

---

## 5. Rate Limiting Policy

### 5.1 Limits by Client Type

| Client Type | Requests / Minute | Requests / Hour | Burst |
|-------------|-------------------|-----------------|-------|
| Individual User (JWT) | 120 | 3,000 | 20 |
| Manager (team operations) | 300 | 10,000 | 50 |
| HR / Payroll Admin | 600 | 20,000 | 100 |
| Service Account (integration) | 1,200 | 60,000 | 200 |
| System Admin | 2,400 | 120,000 | 500 |

### 5.2 Rate Limit Headers

All responses include:

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1720166460
Retry-After: 34
```

`Retry-After` only present on `429` responses.

### 5.3 Special Limits

- **`POST /payroll/runs`** — maximum 1 concurrent run per legal entity; 429 returned if run is in progress regardless of per-user limit.
- **`POST /reports/*`** — report generation requests are queued; maximum 5 concurrent report jobs per tenant.
- **`GET /employees` (bulk list)** — page size capped at 200 records per request.

---

## 6. Pagination & Filtering

### 6.1 Pagination

All list endpoints use **cursor-based pagination** for large collections (employees, payroll details) and **offset pagination** for bounded collections (leave requests for one employee).

**Cursor-based response envelope:**
```json
{
  "data": [ ... ],
  "pagination": {
    "total": 1452,
    "page_size": 50,
    "next_cursor": "eyJlbXBfaWQiOjE1MH0=",
    "prev_cursor": "eyJlbXBfaWQiOjEwMH0=",
    "has_next": true,
    "has_prev": true
  }
}
```

**Offset-based response envelope:**
```json
{
  "data": [ ... ],
  "pagination": {
    "total": 24,
    "page": 2,
    "page_size": 10,
    "total_pages": 3
  }
}
```

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page_size` | integer | 50 | Records per page; max 200 |
| `cursor` | string | — | Opaque cursor from previous response |
| `page` | integer | 1 | For offset pagination |

### 6.2 Filtering

Filters are passed as query parameters. Complex filters use a standardised syntax:

| Pattern | Example | Meaning |
|---------|---------|---------|
| Equality | `?status=ACTIVE` | Exact match |
| Multiple values | `?status=ACTIVE,ON_LEAVE` | OR match |
| Date range | `?hire_date_from=2024-01-01&hire_date_to=2024-12-31` | Inclusive range |
| Numeric range | `?grade_min=5&grade_max=8` | Inclusive range |
| Free-text search | `?q=jane` | Searches name, email, employee_number |
| Null check | `?manager_id=null` | Field is null |

### 6.3 Sorting

```
?sort=last_name:asc,hire_date:desc
```

Default sort is specified per endpoint. Unknown sort fields return `400`.

### 6.4 Field Selection (Sparse Fieldsets)

```
?fields=employee_id,employee_number,first_name,last_name,email
```

Reduces payload size for list operations. Relationships (nested objects) excluded by default unless requested via `include` parameter:

```
?include=department,manager,current_salary
```

---

## 7. Employee Management APIs

### 7.1 List Employees

```
GET /employees
```

**Query Parameters:** `status`, `department_id`, `grade_min`, `grade_max`, `hire_date_from`, `hire_date_to`, `q`, `page_size`, `cursor`, `sort`, `fields`, `include`

**Permissions:** `HR_SPECIALIST`, `HR_MANAGER`, `SYSTEM_ADMIN`; MANAGER returns only direct reports.

**Response `200 OK`:**
```json
{
  "data": [
    {
      "employee_id": 42,
      "employee_number": "EMP-00042",
      "first_name": "Jane",
      "last_name": "Doe",
      "email": "jane.doe@acme.com",
      "employment_status": "ACTIVE",
      "grade": 7,
      "hire_date": "2019-03-15",
      "department": {
        "department_id": 10,
        "department_name": "Engineering",
        "department_code": "ENG"
      },
      "job_title": "Senior Engineer",
      "manager": {
        "employee_id": 15,
        "employee_number": "EMP-00015",
        "full_name": "John Smith"
      }
    }
  ],
  "pagination": { ... }
}
```

**Error Codes:** `UNAUTHORIZED (401)`, `FORBIDDEN (403)`

---

### 7.2 Get Employee

```
GET /employees/{employee_id}
```

**Path Parameters:** `employee_id` (integer)

**Query Parameters:** `include` (department, manager, current_salary, leave_balances, direct_reports)

**Permissions:** Employee can read own record. Manager can read direct reports. HR roles can read all.

**Response `200 OK`:**
```json
{
  "employee_id": 42,
  "employee_number": "EMP-00042",
  "first_name": "Jane",
  "last_name": "Doe",
  "middle_name": null,
  "email": "jane.doe@acme.com",
  "phone": "+1-555-0100",
  "employment_status": "ACTIVE",
  "grade": 7,
  "hire_date": "2019-03-15",
  "termination_date": null,
  "job_title": "Senior Engineer",
  "department_id": 10,
  "manager_id": 15,
  "marital_status": "MARRIED",
  "tax_filing_status": "MARRIED_FILING_JOINTLY",
  "address": {
    "line1": "123 Main St",
    "line2": null,
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94105"
  },
  "emergency_contact": {
    "name": "John Doe",
    "phone": "+1-555-0101"
  },
  "active_flag": true,
  "created_at": "2019-03-15T08:00:00Z",
  "updated_at": "2023-06-01T14:22:00Z"
}
```

**Error Codes:** `EMPLOYEE_NOT_FOUND (404)`, `UNAUTHORIZED (401)`, `FORBIDDEN (403)`

**Business Rules:**
- SSN, bank account numbers are never returned in this endpoint; separate PII endpoints with elevated audit logging.
- `date_of_birth` only returned with `include=pii` permission (HR_MANAGER and above).

---

### 7.3 Create Employee (Hire)

```
POST /employees
```

**Headers:** `Idempotency-Key: <uuid>`

**Permissions:** `HR_SPECIALIST`, `HR_MANAGER`, `SYSTEM_ADMIN`

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "middle_name": null,
  "email": "jane.doe@acme.com",
  "phone": "+1-555-0100",
  "hire_date": "2024-02-01",
  "job_title": "Senior Engineer",
  "department_id": 10,
  "manager_id": 15,
  "grade": 7,
  "salary": {
    "amount": 95000.00,
    "currency": "USD",
    "salary_type": "MONTHLY",
    "effective_date": "2024-02-01"
  },
  "marital_status": "SINGLE",
  "tax_filing_status": "SINGLE",
  "address": {
    "line1": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zip_code": "94105"
  },
  "employment_type": "FULL_TIME"
}
```

**Response `201 Created`:**
```json
{
  "employee_id": 1453,
  "employee_number": "EMP-01453",
  "employment_status": "ACTIVE",
  "hire_date": "2024-02-01",
  "created_at": "2024-01-15T09:30:00Z"
}
```

**Error Codes:** `VALIDATION_FAILED (422)`, `DUPLICATE_EMAIL (409)`, `SALARY_OUTSIDE_GRADE_BAND (422)`, `HIRE_DATE_TOO_FAR_FUTURE (422)`, `IDEMPOTENCY_CONFLICT (409)`

**Business Rules:**
- `hire_date` must not be more than **90 days** in the future (authoritative rule — resolves DISC-001 in favour of Forms layer).
- `salary.amount` must be within the grade band `MIN_SALARY`–`MAX_SALARY` for `grade`. This is a **blocking error**, not a warning (resolves TD-74).
- `tax_filing_status = HEAD_OF_HOUSEHOLD` requires at least one qualifying dependent record before the first payroll run; API validates at payroll time.
- `email` must be unique across all employees with `employment_status != 'TERMINATED'`.
- System auto-generates `employee_number` in format `EMP-{zero-padded 5-digit sequence}`.
- Leave balances for all active leave types are initialised upon successful hire (replaces `PKG_LEAVE.initialize_balances`).

---

### 7.4 Update Employee

```
PATCH /employees/{employee_id}
```

**Permissions:** `HR_SPECIALIST` for most fields; `HR_MANAGER` required for grade changes and salary changes.

**Request Body (partial update — only include changed fields):**
```json
{
  "phone": "+1-555-0199",
  "address": {
    "line1": "456 Oak Ave",
    "city": "Oakland",
    "state": "CA",
    "zip_code": "94607"
  },
  "tax_filing_status": "MARRIED_FILING_JOINTLY"
}
```

**Response `200 OK`:** Full updated employee object (same schema as GET).

**Error Codes:** `EMPLOYEE_NOT_FOUND (404)`, `VALIDATION_FAILED (422)`, `FORBIDDEN (403)`

**Business Rules:**
- `employment_status` is NOT patchable directly; use dedicated lifecycle endpoints (`/hire`, `/terminate`, `/rehire`).
- `grade` changes require `HR_MANAGER` role and trigger a salary-grade validation check.
- All changes are audit-logged with the requesting user's `employee_id`.

---

### 7.5 Terminate Employee

```
POST /employees/{employee_id}/terminate
```

**Headers:** `Idempotency-Key: <uuid>`

**Permissions:** `HR_MANAGER`, `SYSTEM_ADMIN`

**Request Body:**
```json
{
  "termination_date": "2024-02-29",
  "termination_reason_code": "VOLUNTARY",
  "termination_notes": "Resigned to pursue other opportunities.",
  "last_working_day": "2024-02-29",
  "cobra_notification_acknowledged": true,
  "final_pay_period_id": 48,
  "pto_payout_days": 5.5
}
```

**Response `202 Accepted`:**
```json
{
  "employee_id": 42,
  "employment_status": "TERMINATED",
  "termination_date": "2024-02-29",
  "termination_reason_code": "VOLUNTARY",
  "downstream_tasks": [
    {
      "task": "COBRA_NOTIFICATION",
      "status": "TRIGGERED",
      "deadline": "2024-03-14"
    },
    {
      "task": "FINAL_PAY_CALCULATION",
      "status": "PENDING",
      "payroll_run_id": null
    },
    {
      "task": "BENEFITS_FEED_UPDATE",
      "status": "QUEUED"
    },
    {
      "task": "ACCESS_REVOCATION",
      "status": "COMPLETED"
    }
  ]
}
```

**Error Codes:** `EMPLOYEE_NOT_FOUND (404)`, `COBRA_NOTIFICATION_REQUIRED (422)`, `VALIDATION_FAILED (422)`

**Business Rules:**
- `cobra_notification_acknowledged: true` is **required**; missing or `false` returns `COBRA_NOTIFICATION_REQUIRED (422)`. Resolves PP-TERM-01 federal compliance gap.
- Access tokens for the terminated employee are invalidated synchronously (resolves PP-TERM-02 — in-flight session gap). All existing refresh tokens for this employee_id are revoked.
- `final_pay_period_id` or `pto_payout_days` triggers a final pay calculation job. Resolves PP-TERM-03 — `calculate_final_pay` non-existent.
- Dependent records are flagged for COBRA review but remain active until HR explicitly inactivates them (resolves VQ-DEP-04).
- Bank accounts for the terminated employee are marked `PENDING_INACTIVATION`; auto-inactivate after final pay disbursement.

---

### 7.6 Rehire Employee

```
POST /employees/{employee_id}/rehire
```

**Headers:** `Idempotency-Key: <uuid>`

**Permissions:** `HR_MANAGER`, `SYSTEM_ADMIN`

**Request Body:**
```json
{
  "rehire_date": "2024-06-01",
  "department_id": 12,
  "manager_id": 20,
  "grade": 7,
  "salary": {
    "amount": 98000.00,
    "currency": "USD",
    "salary_type": "MONTHLY",
    "effective_date": "2024-06-01"
  },
  "job_title": "Senior Engineer II"
}
```

**Response `200 OK`:** Updated employee object with `employment_status: "ACTIVE"`.

**Error Codes:** `EMPLOYEE_NOT_FOUND (404)`, `VALIDATION_FAILED (422)` (e.g. employee is not TERMINATED)

**Business Rules:**
- Only employees with `employment_status = 'TERMINATED'` can be rehired.
- Leave balances are re-initialised for the new hire date.
- Service continuity (prior tenure) is preserved in `EMPLOYEE_HISTORY`.

---

### 7.7 Transfer Employee

```
POST /employees/{employee_id}/transfer
```

**Permissions:** `HR_SPECIALIST`, `HR_MANAGER`

**Request Body:**
```json
{
  "effective_date": "2024-03-01",
  "new_department_id": 15,
  "new_manager_id": 25,
  "new_job_title": "Lead Engineer",
  "new_grade": 8,
  "salary_change": {
    "amount": 110000.00,
    "currency": "USD",
    "change_reason": "Promotion at transfer"
  }
}
```

**Response `200 OK`:** Updated employee object.

**Business Rules:**
- Creates a record in `EMPLOYEE_HISTORY` for both old and new state.
- `salary_change` is optional; if omitted, existing salary carries forward.

---

### 7.8 Get Employee Org Chart

```
GET /employees/{employee_id}/org-chart
```

**Query Parameters:** `depth` (integer, 1–5, default 2)

**Response `200 OK`:** Nested tree structure with direct reports and their reports up to `depth` levels.

---

## 8. Payroll APIs

### 8.1 List Payroll Runs

```
GET /payroll/runs
```

**Query Parameters:** `status`, `pay_period_from`, `pay_period_to`, `page_size`, `cursor`

**Permissions:** `PAYROLL_ADMIN`, `HR_MANAGER`, `FINANCE_ANALYST`

**Response `200 OK`:**
```json
{
  "data": [
    {
      "run_id": 48,
      "run_name": "PAYROLL_2024_01",
      "pay_period_start": "2024-01-01",
      "pay_period_end": "2024-01-31",
      "run_date": "2024-01-28",
      "status": "APPROVED",
      "totals": {
        "gross": 1250000.00,
        "net": 975000.00,
        "deductions": 275000.00,
        "currency": "USD"
      },
      "employee_count": 450,
      "approved_by": {
        "employee_id": 15,
        "full_name": "John Smith"
      },
      "approved_at": "2024-01-29T14:00:00Z"
    }
  ],
  "pagination": { ... }
}
```

---

### 8.2 Create Payroll Run

```
POST /payroll/runs
```

**Headers:** `Idempotency-Key: <uuid>`

**Permissions:** `PAYROLL_ADMIN`

**Request Body:**
```json
{
  "run_name": "PAYROLL_2024_02",
  "pay_period_start": "2024-02-01",
  "pay_period_end": "2024-02-29",
  "run_date": "2024-02-26",
  "include_departments": null,
  "exclude_employee_ids": []
}
```

**Response `202 Accepted`:**
```json
{
  "run_id": 49,
  "status": "CALCULATING",
  "estimated_completion_seconds": 120,
  "status_url": "/api/v1/payroll/runs/49"
}
```

**Error Codes:** `PAYROLL_RUN_IN_PROGRESS (409)`, `VALIDATION_FAILED (422)`, `IDEMPOTENCY_CONFLICT (409)`

**Business Rules:**
- Only one run per pay period allowed. Duplicate pay period returns `409 Conflict`.
- `HEAD_OF_HOUSEHOLD` employees must have a non-zero federal tax computed; run fails with `VALIDATION_FAILED` if any HOH employee would receive $0 federal tax (resolves the HOH tax defect).
- Merit increase eligibility requires `CALIBRATED_RATING >= 3.0` (not `OVERALL_RATING`) to prevent pre-calibration merit payments.

---

### 8.3 Get Payroll Run Details

```
GET /payroll/runs/{run_id}
```

**Response `200 OK`:**
```json
{
  "run_id": 48,
  "run_name": "PAYROLL_2024_01",
  "status": "APPROVED",
  "pay_period_start": "2024-01-01",
  "pay_period_end": "2024-01-31",
  "totals": {
    "gross": 1250000.00,
    "net": 975000.00,
    "federal_tax": 125000.00,
    "state_tax": 62500.00,
    "social_security": 77500.00,
    "medicare": 18125.00,
    "other_deductions": 42500.00,
    "currency": "USD"
  },
  "gl_feed": {
    "status": "SENT",
    "file_name": "GL_FEED_20240129.dat",
    "sent_at": "2024-01-29T15:00:00Z"
  },
  "disbursement": {
    "status": "COMPLETED",
    "nacha_file": "ACH_20240130.ach",
    "disbursed_at": "2024-01-30T06:00:00Z"
  }
}
```

---

### 8.4 Approve Payroll Run

```
POST /payroll/runs/{run_id}/approve
```

**Permissions:** `PAYROLL_ADMIN` (cannot approve a run they created — four-eyes principle)

**Request Body:**
```json
{
  "approval_notes": "Reviewed and approved. No exceptions."
}
```

**Response `200 OK`:**
```json
{
  "run_id": 48,
  "status": "APPROVED",
  "approved_by": { "employee_id": 15, "full_name": "John Smith" },
  "approved_at": "2024-01-29T14:00:00Z"
}
```

**Error Codes:** `PAYROLL_RUN_NOT_APPROVABLE (422)` (run not in CALCULATED status), `FORBIDDEN (403)` (approver is the same person who created the run)

---

### 8.5 Generate Disbursement (ACH)

```
POST /payroll/runs/{run_id}/disburse
```

**Headers:** `Idempotency-Key: <uuid>`

**Permissions:** `PAYROLL_ADMIN`

**Request Body:**
```json
{
  "effective_date": "2024-01-30",
  "prenote_check": true
}
```

**Response `202 Accepted`:**
```json
{
  "run_id": 48,
  "disbursement_id": "DISB-20240130-048",
  "status": "GENERATING",
  "nacha_file_name": "ACH_20240130.ach",
  "employees_with_prenote_hold": 2,
  "estimated_completion_seconds": 30
}
```

**Error Codes:** `PRENOTE_REQUIRED (422)` if `prenote_check=true` and employees have unverified accounts; `PAYROLL_RUN_NOT_APPROVABLE (422)` if run not in APPROVED status.

**Business Rules:**
- Run must be in `APPROVED` status before disbursement.
- Employees with bank accounts where `PRENOTE_SENT = false` and `prenote_check = true` are held; others proceed.
- Routing numbers validated against ABA checksum before NACHA file generation.
- `PAYROLL_RUNS.gl_feed_sent_date` and `nacha_file_name` updated upon completion (resolves TD-80).

---

### 8.6 Get Payslip

```
GET /payroll/payslips/{employee_id}/{run_id}
```

**Permissions:** Employee can retrieve own payslips. `PAYROLL_ADMIN`, `HR_MANAGER` can retrieve any.

**Response `200 OK`:**
```json
{
  "payslip_id": "PS-048-00042",
  "employee_id": 42,
  "employee_number": "EMP-00042",
  "full_name": "Jane Doe",
  "run_id": 48,
  "pay_period": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "earnings": {
    "base_salary": 7916.67,
    "overtime": 0.00,
    "bonus": 0.00,
    "gross": 7916.67,
    "currency": "USD"
  },
  "deductions": {
    "federal_income_tax": 1187.50,
    "state_income_tax": 395.83,
    "social_security": 490.83,
    "medicare": 114.79,
    "health_insurance": 250.00,
    "total": 2438.95
  },
  "net_pay": 5477.72,
  "ytd": {
    "gross": 7916.67,
    "federal_tax": 1187.50,
    "net": 5477.72
  }
}
```

---

### 8.7 Get YTD Earnings

```
GET /payroll/employees/{employee_id}/ytd
```

**Query Parameters:** `year` (integer, default: current year)

**Response `200 OK`:**
```json
{
  "employee_id": 42,
  "year": 2024,
  "gross_earnings": 95000.00,
  "federal_tax_withheld": 14250.00,
  "state_tax_withheld": 4750.00,
  "social_security_withheld": 5890.00,
  "medicare_withheld": 1377.50,
  "total_deductions": 33017.50,
  "net_earnings": 61982.50,
  "currency": "USD",
  "as_of_run_id": 48
}
```

---

## 9. Leave Management APIs

### 9.1 Get Leave Balances

```
GET /leave/balances/{employee_id}
```

**Query Parameters:** `leave_type_code`, `as_of_date`

**Permissions:** Employee for own; Manager for direct reports; HR roles for all.

**Response `200 OK`:**
```json
{
  "employee_id": 42,
  "as_of_date": "2024-01-15",
  "balances": [
    {
      "leave_type_code": "ANNUAL",
      "leave_type_name": "Annual Leave",
      "opening_balance": 15.00,
      "accrued_ytd": 1.25,
      "taken_ytd": 3.00,
      "pending_approval": 2.00,
      "available": 11.25,
      "unit": "DAYS"
    },
    {
      "leave_type_code": "SICK",
      "leave_type_name": "Sick Leave",
      "opening_balance": 10.00,
      "accrued_ytd": 0.83,
      "taken_ytd": 0.00,
      "pending_approval": 0.00,
      "available": 10.83,
      "unit": "DAYS"
    },
    {
      "leave_type_code": "FMLA",
      "leave_type_name": "FMLA",
      "opening_balance": 480.00,
      "accrued_ytd": 0.00,
      "taken_ytd": 0.00,
      "pending_approval": 0.00,
      "available": 480.00,
      "unit": "HOURS"
    }
  ]
}
```

---

### 9.2 Submit Leave Request

```
POST /leave/requests
```

**Headers:** `Idempotency-Key: <uuid>`

**Permissions:** All authenticated employees.

**Request Body:**
```json
{
  "employee_id": 42,
  "leave_type_code": "ANNUAL",
  "start_date": "2024-02-05",
  "end_date": "2024-02-09",
  "days_requested": 5.0,
  "reason": "Family vacation",
  "supporting_document_url": null
}
```

**Response `201 Created`:**
```json
{
  "request_id": "LR-2024-00312",
  "employee_id": 42,
  "leave_type_code": "ANNUAL",
  "start_date": "2024-02-05",
  "end_date": "2024-02-09",
  "days_requested": 5.0,
  "status": "PENDING",
  "submitted_at": "2024-01-15T09:30:00Z",
  "manager_id": 15,
  "required_document": false
}
```

**Error Codes:** `LEAVE_INSUFFICIENT_BALANCE (422)`, `LEAVE_OVERLAP (409)`, `VALIDATION_FAILED (422)`

**Business Rules:**
- `days_requested` must not exceed `available` balance.
- Start and end dates must not overlap any approved or pending leave for this employee.
- FMLA requests (`leave_type_code = 'FMLA'`) require `supporting_document_url` to be non-null (resolves TD-71 — FMLA `REQUIRES_DOCUMENT='N'` seed data defect).
- Weekend days are excluded from working day calculation based on the employee's work schedule.
- Notification sent to manager's email upon submission (replaces UTL_SMTP notification).

---

### 9.3 Approve Leave Request

```
POST /leave/requests/{request_id}/approve
```

**Permissions:** `MANAGER` (for direct reports), `HR_SPECIALIST`, `HR_MANAGER`

**Request Body:**
```json
{
  "approval_notes": "Approved. Team coverage confirmed."
}
```

**Response `200 OK`:**
```json
{
  "request_id": "LR-2024-00312",
  "status": "APPROVED",
  "approved_by": { "employee_id": 15, "full_name": "John Smith" },
  "approved_at": "2024-01-16T10:00:00Z"
}
```

**Error Codes:** `LEAVE_REQUEST_NOT_FOUND (404)`, `FORBIDDEN (403)`, `VALIDATION_FAILED (422)` (request not in PENDING status)

**Business Rules:**
- Leave balance is decremented upon approval; `LEAVE_BALANCES.taken_ytd` updated.
- Employee receives notification on approval.

---

### 9.4 Reject Leave Request

```
POST /leave/requests/{request_id}/reject
```

**Permissions:** `MANAGER` (direct reports), `HR_SPECIALIST`, `HR_MANAGER`

**Request Body:**
```json
{
  "rejection_reason": "Insufficient staffing during requested period."
}
```

**Response `200 OK`:**
```json
{
  "request_id": "LR-2024-00312",
  "status": "REJECTED",
  "rejected_by": { "employee_id": 15 },
  "rejected_at": "2024-01-16T10:05:00Z",
  "rejection_reason": "Insufficient staffing during requested period."
}
```

**Business Rules:**
- `rejection_reason` is required; minimum 10 characters.
- `pending_approval` balance is returned to `available` upon rejection.
- Employee receives notification on rejection.

---

### 9.5 Cancel Leave Request

```
POST /leave/requests/{request_id}/cancel
```

**Permissions:** Employee (own request only, while status is PENDING or APPROVED and start_date is in the future)

**Response `200 OK`:** Updated leave request with `status: "CANCELLED"`.

**Business Rules:**
- Cancellation of an APPROVED request restores balance to `available`.
- Cancellation of a started leave (current date > `start_date`) requires `HR_SPECIALIST`.

---

### 9.6 List Leave Requests

```
GET /leave/requests
```

**Query Parameters:** `employee_id`, `status`, `leave_type_code`, `start_date_from`, `start_date_to`, `page_size`, `cursor`

**Permissions:** Employee sees own; Manager sees team; HR sees all.

---

## 10. Performance APIs

### 10.1 List Review Cycles

```
GET /performance/cycles
```

**Response `200 OK`:**
```json
{
  "data": [
    {
      "cycle_id": 5,
      "cycle_name": "2024 Annual Review",
      "review_type": "ANNUAL",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "self_review_deadline": "2024-12-15",
      "manager_review_deadline": "2024-12-22",
      "calibration_deadline": "2025-01-10",
      "status": "ACTIVE"
    }
  ]
}
```

---

### 10.2 Create Performance Review

```
POST /performance/reviews
```

**Permissions:** `HR_SPECIALIST`, `HR_MANAGER` (bulk creation); Manager for own team.

**Request Body:**
```json
{
  "cycle_id": 5,
  "employee_id": 42,
  "reviewer_employee_id": 15,
  "review_type": "ANNUAL"
}
```

**Response `201 Created`:**
```json
{
  "review_id": 201,
  "cycle_id": 5,
  "employee_id": 42,
  "reviewer_employee_id": 15,
  "status": "NOT_STARTED",
  "created_at": "2024-01-15T09:30:00Z"
}
```

**Error Codes:** `REVIEW_ALREADY_EXISTS (409)`, `EMPLOYEE_NOT_FOUND (404)`

---

### 10.3 Submit Self-Assessment

```
POST /performance/reviews/{review_id}/self-assessment
```

**Permissions:** The employee named in the review only.

**Request Body:**
```json
{
  "self_assessment": "This year I delivered the payment processing migration on time...",
  "self_rating": 4.0
}
```

**Response `200 OK`:**
```json
{
  "review_id": 201,
  "status": "SELF_REVIEW",
  "self_assessment_submitted_at": "2024-12-10T11:00:00Z"
}
```

---

### 10.4 Submit Manager Review

```
POST /performance/reviews/{review_id}/manager-review
```

**Permissions:** The reviewer named in the review only.

**Request Body:**
```json
{
  "overall_rating": 4.2,
  "manager_assessment": "Jane consistently delivered above expectations...",
  "strengths": "Technical leadership, mentoring junior engineers, delivery focus.",
  "areas_for_improvement": "Cross-functional communication during incidents.",
  "development_plan": "Attend leadership training Q2; present at one external conference."
}
```

**Response `200 OK`:**
```json
{
  "review_id": 201,
  "status": "COMPLETED",
  "overall_rating": 4.2,
  "rating_label": "Exceeds Expectations",
  "manager_review_submitted_at": "2024-12-20T16:00:00Z"
}
```

**Business Rules:**
- `overall_rating` must be in range `[1.0, 5.0]`; otherwise `VALIDATION_FAILED`.
- Rating label is server-computed: `>= 4.5` → Exceptional; `>= 3.5` → Exceeds Expectations; `>= 2.5` → Meets Expectations; `>= 1.5` → Needs Improvement; `< 1.5` → Unsatisfactory.
- Status moves to `COMPLETED`; review is queued for calibration.

---

### 10.5 Submit Calibration

```
POST /performance/reviews/{review_id}/calibrate
```

**Permissions:** `HR_MANAGER`, `SYSTEM_ADMIN` (resolves the calibration workflow gap — `CALIBRATED_RATING` dead column)

**Request Body:**
```json
{
  "calibrated_rating": 4.0,
  "calibration_notes": "Adjusted from 4.2 to 4.0 for cross-team fairness during calibration session 2025-01-08.",
  "calibrated_by_committee": true
}
```

**Response `200 OK`:**
```json
{
  "review_id": 201,
  "status": "CALIBRATED",
  "overall_rating": 4.2,
  "calibrated_rating": 4.0,
  "calibration_notes": "Adjusted from 4.2 to 4.0 for cross-team fairness...",
  "calibrated_at": "2025-01-08T15:00:00Z",
  "calibrated_by": { "employee_id": 8, "full_name": "Patricia Lee" }
}
```

**Error Codes:** `CALIBRATION_NOT_PERMITTED (422)` if review not in `COMPLETED` or `CALIBRATED` status.

**Business Rules:**
- Only reviews in `COMPLETED` or `CALIBRATED` status may be calibrated.
- `calibrated_rating` replaces `overall_rating` as the authoritative rating for: merit eligibility, reporting, and employee acknowledgement.
- Reporting endpoint `/reports/performance` uses `calibrated_rating` where available, falling back to `overall_rating` only if `calibrated_rating` is null.
- Status moves to `CALIBRATED`.

---

### 10.6 Acknowledge Review

```
POST /performance/reviews/{review_id}/acknowledge
```

**Permissions:** The employee named in the review.

**Request Body:**
```json
{
  "employee_comments": "Thank you for the feedback. I look forward to the development plan."
}
```

**Response `200 OK`:**
```json
{
  "review_id": 201,
  "status": "ACKNOWLEDGED",
  "acknowledged_at": "2025-01-15T09:00:00Z"
}
```

**Business Rules:**
- Review must be in `CALIBRATED` status (or `COMPLETED` if calibration is waived for the cycle) before acknowledgement is accepted.
- `employee_comments` is optional.

---

### 10.7 Submit Performance Goal

```
POST /performance/goals
```

**Permissions:** Employee (own goals); Manager (team goals).

**Request Body:**
```json
{
  "employee_id": 42,
  "cycle_id": 5,
  "goal_title": "Complete AWS Solutions Architect certification",
  "goal_description": "Pass the SAA-C03 exam by Q3 2024.",
  "weight": 20,
  "target_date": "2024-09-30",
  "measurement_criteria": "Exam pass certificate uploaded to HR portal."
}
```

**Response `201 Created`:** Created goal object with `goal_id` and `status: "DRAFT"`.

---

## 11. Security APIs

### 11.1 Login

```
POST /auth/login
```

**No authentication required.**

**Request Body:**
```json
{
  "email": "jane.doe@acme.com",
  "password": "SecurePassword1!"
}
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 900,
  "employee_id": 42,
  "employee_number": "EMP-00042",
  "roles": ["EMPLOYEE", "MANAGER"]
}
```

**Error Codes:** `401 Unauthorized` with generic message (no user enumeration — timing-safe comparison; resolves DQ-003, BR-042, BR-043b)

**Business Rules:**
- Authentication must verify the password hash against the stored credential. Stub authentication (`authenticate()` that never checks password — BR-042) is **not reimplemented**.
- Passwords hashed using **bcrypt** with cost factor 12 (replaces MD5 — DQ-010).
- Failed login attempts increment a counter; account locks after 5 consecutive failures (lockout duration 15 minutes). Resolves DQ-023 — no lockout.
- On success, `EMPLOYMENT_STATUS` must be `ACTIVE`. Terminated or suspended employees receive generic `401`.
- No response field distinguishes "bad password" from "user not found" — both return identical `401` response and take identical server-side time (resolves timing attack noted in DA track).

---

### 11.2 Refresh Token

```
POST /auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiJ9..."
}
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiJ9...",
  "expires_in": 900
}
```

**Business Rules:**
- Refresh token rotation: issuing a new access token also issues a new refresh token. The old refresh token is immediately invalidated (token family rotation — detects refresh token theft).
- Refresh tokens may not be used after employee termination.

---

### 11.3 Logout

```
POST /auth/logout
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJSUzI1NiJ9..."
}
```

**Response `204 No Content`**

**Business Rules:**
- Refresh token added to a short-lived revocation list (TTL = remaining token lifetime).
- Access tokens are short-lived (15 minutes); no server-side revocation required for access tokens.

---

### 11.4 Change Password

```
POST /auth/change-password
```

**Permissions:** Authenticated employee (own password only).

**Request Body:**
```json
{
  "current_password": "OldSecurePassword1!",
  "new_password": "NewSecurePassword2!",
  "new_password_confirm": "NewSecurePassword2!"
}
```

**Response `204 No Content`**

**Error Codes:** `401 Unauthorized` (current_password incorrect), `VALIDATION_FAILED (422)` (new_password does not meet complexity)

**Business Rules:**
- `current_password` **must be verified** against stored hash before accepting `new_password`. Resolves DQ-029 / BR-044.
- Password complexity: minimum 8 characters, at least 1 uppercase, at least 1 digit, at least 1 special character.
- Password history: cannot reuse any of last 5 passwords.
- All active refresh tokens for this employee are revoked on successful password change.

---

### 11.5 Admin: Reset Password

```
POST /admin/employees/{employee_id}/reset-password
```

**Permissions:** `SYSTEM_ADMIN` only

**Request Body:**
```json
{
  "temporary_password": null,
  "force_change_on_next_login": true
}
```

**Response `200 OK`:** Returns one-time temporary password if `temporary_password` is null (system-generated).

---

### 11.6 Validate Session

```
GET /auth/me
```

Returns current authenticated user's profile. Used by front-end to validate token and refresh user context.

**Response `200 OK`:** Compact employee profile with roles and permissions.

---

## 12. Reporting APIs

All reporting endpoints return data computed at query time against the OLTP tables. A separate `/reports/snapshots` endpoint triggers background snapshot generation into reporting tables (replaces `refresh_reporting_tables` stub — BR-043).

**Business Rule:** All reports use `CALIBRATED_RATING` where available; fall back to `OVERALL_RATING` only if calibration has not occurred for a cycle (resolves get_rating_distribution reading pre-calibration values).

---

### 12.1 Headcount Report

```
GET /reports/headcount
```

**Query Parameters:** `as_of_date`, `department_id`, `location`, `employment_type`

**Permissions:** `HR_SPECIALIST`, `HR_MANAGER`, `EXECUTIVE`, `FINANCE_ANALYST`

**Response `200 OK`:**
```json
{
  "report_name": "Headcount Report",
  "generated_at": "2024-01-15T10:00:00Z",
  "as_of_date": "2024-01-15",
  "totals": {
    "active_employees": 1452,
    "full_time": 1200,
    "part_time": 180,
    "contractors": 72,
    "gender_breakdown": {
      "male": 720,
      "female": 684,
      "other": 24,
      "not_disclosed": 24
    },
    "average_tenure_years": 4.2
  },
  "by_department": [
    {
      "department_id": 10,
      "department_name": "Engineering",
      "headcount": 320,
      "full_time": 290,
      "part_time": 20,
      "contractors": 10
    }
  ]
}
```

---

### 12.2 Compensation Summary Report

```
GET /reports/compensation
```

**Query Parameters:** `department_id`, `grade_min`, `grade_max`, `as_of_date`

**Permissions:** `HR_MANAGER`, `EXECUTIVE`, `FINANCE_ANALYST`

**Response `200 OK`:**
```json
{
  "report_name": "Compensation Summary",
  "generated_at": "2024-01-15T10:00:00Z",
  "summary": {
    "total_annual_payroll": 125000000.00,
    "average_salary": 86000.00,
    "median_salary": 82000.00,
    "currency": "USD"
  },
  "by_grade": [
    {
      "grade": 7,
      "headcount": 180,
      "average_salary": 95000.00,
      "median_salary": 93000.00,
      "grade_midpoint": 90000.00,
      "compa_ratio": 105.6
    }
  ]
}
```

**Business Rules:**
- Median computed server-side using SQL window functions (platform-appropriate equivalent of Oracle `MEDIAN()`).

---

### 12.3 Leave Utilisation Report

```
GET /reports/leave-utilisation
```

**Query Parameters:** `department_id`, `leave_type_code`, `year` (required)

**Response `200 OK`:**
```json
{
  "report_name": "Leave Utilisation Report",
  "year": 2024,
  "generated_at": "2024-01-15T10:00:00Z",
  "by_department": [
    {
      "department_id": 10,
      "department_name": "Engineering",
      "leave_type_code": "ANNUAL",
      "average_balance": 12.5,
      "average_taken": 8.2,
      "utilisation_pct": 65.6
    }
  ]
}
```

**Business Rules:**
- `year` parameter is required to avoid multi-year data ambiguity (resolves DQ-032 — `CALENDAR_YEAR` missing from projection).

---

### 12.4 Turnover Report

```
GET /reports/turnover
```

**Query Parameters:** `period_start`, `period_end`, `department_id`

**Response `200 OK`:**
```json
{
  "report_name": "Turnover Report",
  "period_start": "2024-01-01",
  "period_end": "2024-12-31",
  "methodology": "SHRM_STANDARD",
  "by_department": [
    {
      "department_id": 10,
      "department_name": "Engineering",
      "hires": 45,
      "terminations": 12,
      "average_headcount": 320,
      "turnover_pct": 3.75
    }
  ]
}
```

**Business Rules:**
- `turnover_pct` computed as `terminations / average_headcount * 100` (SHRM standard denominator, replacing the legacy non-standard hires-as-denominator — BR-044).
- Report includes a `methodology` field documenting the denominator so consumers can interpret correctly.

---

### 12.5 Performance Rating Distribution

```
GET /reports/performance/rating-distribution
```

**Query Parameters:** `cycle_id` (required), `department_id`

**Response `200 OK`:**
```json
{
  "cycle_id": 5,
  "cycle_name": "2024 Annual Review",
  "rating_source": "CALIBRATED_RATING",
  "distribution": [
    { "rating_label": "Exceptional", "count": 45, "percentage": 3.1 },
    { "rating_label": "Exceeds Expectations", "count": 320, "percentage": 22.0 },
    { "rating_label": "Meets Expectations", "count": 870, "percentage": 59.9 },
    { "rating_label": "Needs Improvement", "count": 185, "percentage": 12.7 },
    { "rating_label": "Unsatisfactory", "count": 33, "percentage": 2.3 }
  ],
  "total_reviews": 1453,
  "calibrated_count": 1453,
  "uncalibrated_count": 0
}
```

---

### 12.6 EEO Compliance Report

```
GET /reports/eeo-compliance
```

**Query Parameters:** `as_of_date`, `eeo_category`

**Permissions:** `HR_MANAGER`, `SYSTEM_ADMIN`

**Response `200 OK`:** EEO category breakdown by gender and job category, with `NOT_DISCLOSED` segment included and documented in the response.

---

## 13. Webhook Events

Webhooks provide asynchronous notifications to registered subscribers for significant HRMS events. They replace the UTL_SMTP synchronous email calls embedded in PL/SQL packages and decouple integration consumers from the HRMS core.

### 13.1 Webhook Registration

```
POST /webhooks/subscriptions
```

**Permissions:** `SYSTEM_ADMIN`

**Request Body:**
```json
{
  "url": "https://integrations.acme.com/hrms-events",
  "events": [
    "employee.hired",
    "employee.terminated",
    "payroll.run.completed",
    "leave.request.approved"
  ],
  "secret": "whsec_abcdef123456",
  "description": "ADP integration receiver"
}
```

**Response `201 Created`:**
```json
{
  "subscription_id": "wh_sub_001",
  "url": "https://integrations.acme.com/hrms-events",
  "events": ["employee.hired", "employee.terminated", "payroll.run.completed", "leave.request.approved"],
  "status": "ACTIVE",
  "created_at": "2024-01-15T09:30:00Z"
}
```

### 13.2 Webhook Delivery

All webhook events are delivered via `POST` to the subscriber's URL with:

**Headers:**
```
Content-Type: application/json
X-HRMS-Event: employee.terminated
X-HRMS-Delivery: del_a1b2c3d4
X-HRMS-Signature-256: sha256=<HMAC-SHA256 of body using subscription secret>
X-HRMS-Timestamp: 1720166400
```

**Retry policy:** Exponential backoff — immediate, 5 min, 30 min, 2 hours, 24 hours. After 5 failures, subscription is marked `DEGRADED` and SYSTEM_ADMIN is notified.

**Signature verification:** Subscribers must verify `X-HRMS-Signature-256` against the request body to prevent spoofing.

### 13.3 Event Catalogue

| Event | Trigger | Payload Key Fields |
|-------|---------|-------------------|
| `employee.hired` | Successful `POST /employees` | `employee_id`, `employee_number`, `hire_date`, `department_id`, `grade` |
| `employee.terminated` | Successful `POST /employees/:id/terminate` | `employee_id`, `termination_date`, `termination_reason_code`, `cobra_deadline` |
| `employee.rehired` | Successful `POST /employees/:id/rehire` | `employee_id`, `rehire_date`, `department_id` |
| `employee.transferred` | Successful `POST /employees/:id/transfer` | `employee_id`, `effective_date`, `old_department_id`, `new_department_id` |
| `employee.updated` | Significant field change (grade, salary, status) | `employee_id`, `changed_fields`, `effective_date` |
| `payroll.run.started` | Payroll run moves to CALCULATING | `run_id`, `run_name`, `pay_period_start`, `pay_period_end` |
| `payroll.run.completed` | Payroll run moves to APPROVED | `run_id`, `totals`, `employee_count` |
| `payroll.disbursement.completed` | ACH NACHA file generated and sent | `run_id`, `disbursement_id`, `nacha_file_name`, `effective_date` |
| `payroll.gl_feed.sent` | GL feed file generated | `run_id`, `file_name`, `sent_at` |
| `leave.request.submitted` | New leave request created | `request_id`, `employee_id`, `leave_type_code`, `start_date`, `end_date`, `days` |
| `leave.request.approved` | Leave request approved | `request_id`, `employee_id`, `approved_by_id`, `approved_at` |
| `leave.request.rejected` | Leave request rejected | `request_id`, `employee_id`, `rejection_reason` |
| `performance.review.completed` | Manager submits review | `review_id`, `employee_id`, `cycle_id`, `overall_rating`, `rating_label` |
| `performance.review.calibrated` | Calibration submitted | `review_id`, `employee_id`, `calibrated_rating`, `calibrated_at` |
| `performance.review.acknowledged` | Employee acknowledges | `review_id`, `employee_id`, `acknowledged_at` |
| `bank_account.prenote_required` | New bank account added; prenote needed | `employee_id`, `bank_acct_id`, `prenote_deadline` |
| `cobra.notification.due` | 14 days before COBRA deadline | `employee_id`, `termination_date`, `cobra_deadline` |
| `security.password_changed` | Employee changes password | `employee_id`, `changed_at` (no password data) |
| `security.account_locked` | Account locked after failed attempts | `employee_id`, `locked_until`, `failed_attempts` |
| `org.sync.completed` | Org structure sync completes successfully | `sync_id`, `departments_synced`, `completed_at` |
| `org.sync.failed` | Org structure sync fails | `sync_id`, `error_code`, `error_message` |

### 13.4 Sample Event Payload

**`employee.terminated`:**
```json
{
  "event": "employee.terminated",
  "delivery_id": "del_a1b2c3d4",
  "timestamp": "2024-01-15T14:30:00Z",
  "api_version": "v1",
  "data": {
    "employee_id": 42,
    "employee_number": "EMP-00042",
    "full_name": "Jane Doe",
    "termination_date": "2024-01-15",
    "termination_reason_code": "VOLUNTARY",
    "department_id": 10,
    "cobra_deadline": "2024-01-29",
    "final_pay_run_id": null,
    "benefits_feed_queued": true
  }
}
```

---

## Appendix A — Endpoint Index

| # | Method | Path | Summary |
|---|--------|------|---------|
| 1 | GET | /employees | List employees |
| 2 | POST | /employees | Hire employee |
| 3 | GET | /employees/{id} | Get employee |
| 4 | PATCH | /employees/{id} | Update employee |
| 5 | POST | /employees/{id}/terminate | Terminate employee |
| 6 | POST | /employees/{id}/rehire | Rehire employee |
| 7 | POST | /employees/{id}/transfer | Transfer employee |
| 8 | GET | /employees/{id}/org-chart | Get org chart |
| 9 | GET | /payroll/runs | List payroll runs |
| 10 | POST | /payroll/runs | Create payroll run |
| 11 | GET | /payroll/runs/{id} | Get payroll run |
| 12 | POST | /payroll/runs/{id}/approve | Approve payroll run |
| 13 | POST | /payroll/runs/{id}/disburse | Generate ACH disbursement |
| 14 | GET | /payroll/payslips/{emp_id}/{run_id} | Get payslip |
| 15 | GET | /payroll/employees/{emp_id}/ytd | Get YTD earnings |
| 16 | GET | /leave/balances/{emp_id} | Get leave balances |
| 17 | GET | /leave/requests | List leave requests |
| 18 | POST | /leave/requests | Submit leave request |
| 19 | POST | /leave/requests/{id}/approve | Approve leave |
| 20 | POST | /leave/requests/{id}/reject | Reject leave |
| 21 | POST | /leave/requests/{id}/cancel | Cancel leave |
| 22 | GET | /performance/cycles | List review cycles |
| 23 | POST | /performance/reviews | Create review |
| 24 | POST | /performance/reviews/{id}/self-assessment | Submit self-assessment |
| 25 | POST | /performance/reviews/{id}/manager-review | Submit manager review |
| 26 | POST | /performance/reviews/{id}/calibrate | Submit calibration |
| 27 | POST | /performance/reviews/{id}/acknowledge | Acknowledge review |
| 28 | POST | /performance/goals | Submit goal |
| 29 | POST | /auth/login | Login |
| 30 | POST | /auth/refresh | Refresh token |
| 31 | POST | /auth/logout | Logout |
| 32 | POST | /auth/change-password | Change password |
| 33 | GET | /auth/me | Validate session |
| 34 | POST | /admin/employees/{id}/reset-password | Admin reset password |
| 35 | GET | /reports/headcount | Headcount report |
| 36 | GET | /reports/compensation | Compensation report |
| 37 | GET | /reports/leave-utilisation | Leave utilisation report |
| 38 | GET | /reports/turnover | Turnover report |
| 39 | GET | /reports/performance/rating-distribution | Rating distribution |
| 40 | GET | /reports/eeo-compliance | EEO compliance report |
| 41 | POST | /webhooks/subscriptions | Register webhook |
| 42 | GET | /webhooks/subscriptions | List webhooks |
| 43 | DELETE | /webhooks/subscriptions/{id} | Delete webhook |
| 44 | GET | /webhooks/deliveries | List delivery history |
| 45 | POST | /webhooks/subscriptions/{id}/test | Send test event |

---

## Appendix B — Legacy Defect → API Design Traceability

| Legacy Defect ID | Severity | API Design Resolution |
|-----------------|----------|-----------------------|
| BR-042 (auth stub — never checks password) | Critical | `POST /auth/login` mandates bcrypt verify |
| DQ-029 / BR-044 (change_password skips old password) | High | `POST /auth/change-password` requires `current_password` field |
| DQ-010 (MD5 password hash) | Critical | bcrypt cost 12 mandated in spec |
| DQ-023 (no lockout) | High | 5-attempt lockout built into `/auth/login` |
| PP-BA-01 (direct deposit non-functional) | Critical | `POST /payroll/runs/{id}/disburse` is mandatory lifecycle step |
| BR-BA-04 (routing number plaintext) | High | API encrypts routing at rest; never returns plaintext |
| PP-TERM-01 (COBRA gap) | Critical | `cobra_notification_acknowledged: true` required on terminate |
| PP-TERM-03 (calculate_final_pay non-existent) | Critical | `final_pay_period_id` on terminate triggers calculation job |
| Calibration dead column | High | `POST /performance/reviews/{id}/calibrate` dedicated endpoint |
| BR-043 (get_rating_distribution reads pre-calibration value) | High | Reports use `CALIBRATED_RATING` with `OVERALL_RATING` fallback |
| BR-044 (turnover non-SHRM denominator) | Medium | `/reports/turnover` uses average headcount denominator; `methodology` field documents it |
| DQ-032 (CALENDAR_YEAR missing from leave util) | Medium | `year` parameter required on `/reports/leave-utilisation` |
| TD-80 (no GL feed status on payroll run) | Medium | `gl_feed` object in `GET /payroll/runs/{id}` response |
| BR-ORG-01 (org sync stub) | High | `POST /integrations/org-sync` returns `422` if LDAP not configured |
| TD-71 (FMLA REQUIRES_DOCUMENT='N') | Medium | FMLA requests validate `supporting_document_url` non-null |
| BR-072 / DQ-027 (30-min session timeout bug) | High | Stateless JWT; no server-side session table; 15-min access token |
| BR-043b (duplicate email picks MIN(EMP_ID)) | High | `DUPLICATE_EMAIL (409)` on hire/update; timing-safe auth |

---

*End of document — 11_API_CONTRACT_SPECIFICATION.md*

<!-- GAP-FILLED SECTION -->
| Style | REST over HTTPS (TLS 1.3 minimum) | Replaces Oracle Forms RPC; interoperable with self-service portal, mobile, and BI tools |
| Data Format | `application/json` for all request/response bodies | Replaces Oracle fixed-width flat files and pipe-delimited GL feeds |
| Versioning | URI path prefix (`/api/v1/`) | Breaking changes get `/v2/`; v1 supported minimum 24 months after v2 GA |
| Encoding | UTF-8 throughout | Replaces Oracle NLS_CHARACTERSET-dependent Forms output |
| Idempotency | `Idempotency-Key` header required on POST operations that create records or trigger financial transactions | Prevents duplicate payroll runs (addresses DISC-009 / BR-BA-12 — orphaned PAID status) |
| Nullability | JSON fields explicitly `null` when absent; missing keys indicate field not returned in this view | Distinguishes "not set" from "not applicable" |
| Time | All timestamps in ISO 8601 UTC (`2024-01-15T09:30:00Z`); all date-only fields in `YYYY-MM-DD` | Replaces Oracle `DATE` type with implicit server timezone |
| Currency | All monetary values as JSON number with 2 decimal places; currency code separate field | Replaces Oracle `NUMBER(12,2)` implicit USD |
| Error Details | [GAP-FILLED] `details` array items in 422 (Unprocessable Entity) and 409 (Conflict) responses MUST conform to the structure: `{ "field": string, "constraint": string, "rejected_value": any \| null, "message": string }` — `field` is the dot-path of the offending request property (e.g. `"salary"`, `"hire_date"`); `constraint` is a machine-readable code (e.g. `"BELOW_MINIMUM"`, `"ABOVE_MAXIMUM"`, `"REQUIRED"`, `"FORMAT_INVALID"`, `"RANGE_INVALID"`, `"DUPLICATE_KEY"`); `rejected_value` is the literal value submitted; `message` is the human-readable explanation as produced by `PKG_VALIDATION` (e.g. `"Salary $45,000.00 is below minimum for grade G3 ($52,000.00)"`) | [GAP-FILLED] Derived from `PKG_VALIDATION.validate_salary_for_grade`, `validate_required_fields`, and `validate_email_format` error-message patterns; structured items allow clients to highlight specific form fields and display constraint-aware messages without string parsing |

> **[GAP-FILLED] Error `details` item schema (422 / 409)**
>
> ```json
> {
>   "field":          "salary",
>   "constraint":     "BELOW_MINIMUM",
>   "rejected_value": 45000.00,
>   "message":        "Salary $45,000.00 is below minimum for grade G3 ($52,000.00)"
> }
> ```
>
> `constraint` enumeration sourced from `PKG_VALIDATION` logic:
>
> | Code | Triggered by |
> |------|-------------|
> | `REQUIRED` | `validate_required_fields` — `FIRST_NAME`, `LAST_NAME`, `HIRE_DATE`, `DEPT_ID`, `JOB_ID` null checks |
> | `BELOW_MINIMUM` | `validate_salary_for_grade` — `p_salary < v_min` |
> | `ABOVE_MAXIMUM` | `validate_salary_for_grade` — `p_salary > v_max` |
> | `FORMAT_INVALID` | `validate_email_format`, `validate_phone_format`, `validate_emp_number_format` (pattern `^EMP-\d{6}$`) |
> | `RANGE_INVALID` | `validate_date_range` — end date before start date or either null |
> | `INVALID_REFERENCE` | `validate_salary_for_grade` `NO_DATA_FOUND` — unknown `grade_id` |
> | `DUPLICATE_KEY` | 409 Conflict — unique constraint violation on natural keys (employee number, period overlap) |
>
> When a single request triggers multiple violations, all are returned in the `details` array in a single 422 response; callers MUST iterate the full array.

### 1.2 Versioning Strategy

<!-- GAP-FILLED SECTION -->
Looking at the source content from PKG_PAYROLL.pkb, I can extract two explicit `RAISE_APPLICATION_ERROR` calls with their Oracle error numbers and map them to API-level error codes. I'll add the error code catalogue table between the conventions table and the versioning section header.

| Style | REST over HTTPS (TLS 1.3 minimum) | Replaces Oracle Forms RPC; interoperable with self-service portal, mobile, and BI tools |
| Data Format | `application/json` for all request/response bodies | Replaces Oracle fixed-width flat files and pipe-delimited GL feeds |
| Versioning | URI path prefix (`/api/v1/`) | Breaking changes get `/v2/`; v1 supported minimum 24 months after v2 GA |
| Encoding | UTF-8 throughout | Replaces Oracle NLS_CHARACTERSET-dependent Forms output |
| Idempotency | `Idempotency-Key` header required on POST operations that create records or trigger financial transactions | Prevents duplicate payroll runs (addresses DISC-009 / BR-BA-12 — orphaned PAID status) |
| Nullability | JSON fields explicitly `null` when absent; missing keys indicate field not returned in this view | Distinguishes "not set" from "not applicable" |
| Time | All timestamps in ISO 8601 UTC (`2024-01-15T09:30:00Z`); all date-only fields in `YYYY-MM-DD` | Replaces Oracle `DATE` type with implicit server timezone |
| Currency | All monetary values as JSON number with 2 decimal places; currency code separate field | Replaces Oracle `NUMBER(12,2)` implicit USD |

[GAP-FILLED]
#### 1.1.1 Application-Level Error Code Catalogue

All error responses carry a machine-readable `error.code` string. Clients **must** branch on `error.code`, not on `message` (which is human-readable and may change). The following codes are exhaustively enumerated by domain:

**Employee domain**

| `error.code` | HTTP Status | Oracle source | Trigger condition |
|---|---|---|---|
| `EMPLOYEE_NOT_FOUND` | 404 | — | Requested `emp_id` does not exist or is inactive |

**Payroll domain** *(recovered from `PKG_PAYROLL` — Oracle codes `-20101`, `-20102`)*

| `error.code` | HTTP Status | Oracle source | Trigger condition |
|---|---|---|---|
| `SALARY_INVALID` | 422 | `PKG_PAYROLL` `-20101` | `base_salary` submitted as zero or negative in `create_salary_record` |
| `PERIOD_ALREADY_CLOSED` | 409 | `PKG_PAYROLL` `-20102` | Attempt to close an already-closed pay period, or to create a payroll run against a closed period |

> **Source coverage note:** Error codes for the **leave management** (`PKG_LEAVE`), **GL posting** (`PKG_GL`), and **authentication/authorisation** subsystems were not recoverable from the current deep scan — `PKG_ERROR_CODES.pks` was not found and those package bodies were not in the file cache. The codes below must be populated once those packages are retrieved; until then, clients should treat any unrecognised `error.code` value in those domains as a retryable server-side fault (`500`) rather than a logic branch.

| `error.code` (placeholder) | Domain | Status |
|---|---|---|
| `LEAVE_REQUEST_OVERLAP` | Leave | Pending source recovery |
| `LEAVE_BALANCE_INSUFFICIENT` | Leave | Pending source recovery |
| `GL_PERIOD_NOT_OPEN` | GL Posting | Pending source recovery |
| `GL_ACCOUNT_INVALID` | GL Posting | Pending source recovery |
| `AUTH_TOKEN_EXPIRED` | Authentication | Pending source recovery |
| `AUTH_INSUFFICIENT_PRIVILEGE` | Authorisation | Pending source recovery |

### 1.2 Versioning Strategy

<!-- GAP-FILLED SECTION -->
Now I have the full picture. Section 11 already defines these endpoints in detail — the gap is in the **design principles table** (section 1.1), which covers every cross-cutting concern (encoding, idempotency, async, etc.) but has no row documenting authentication endpoint conventions, token lifetime, refresh lifecycle, or revocation. I'll add that row drawn directly from `PKG_SECURITY.pkb`.

Here is the updated snippet:

---

| Style | REST over HTTPS (TLS 1.3 minimum) | Replaces Oracle Forms RPC; interoperable with self-service portal, mobile, and BI tools |
| Data Format | `application/json` for all request/response bodies | Replaces Oracle fixed-width flat files and pipe-delimited GL feeds |
| Versioning | URI path prefix (`/api/v1/`) | Breaking changes get `/v2/`; v1 supported minimum 24 months after v2 GA |
| Encoding | UTF-8 throughout | Replaces Oracle NLS_CHARACTERSET-dependent Forms output |
| Idempotency | `Idempotency-Key` header required on POST operations that create records or trigger financial transactions | Prevents duplicate payroll runs (addresses DISC-009 / BR-BA-12 — orphaned PAID status) |
| Nullability | JSON fields explicitly `null` when absent; missing keys indicate field not returned in this view | Distinguishes "not set" from "not applicable" |
| Time | All timestamps in ISO 8601 UTC (`2024-01-15T09:30:00Z`); all date-only fields in `YYYY-MM-DD` | Replaces Oracle `DATE` type with implicit server timezone |
| Currency | All monetary values as JSON number with 2 decimal places; currency code separate field | Replaces Oracle `NUMBER(12,2)` implicit USD |
| [GAP-FILLED] Async Operations | `202 Accepted` responses for long-running operations (payroll run, report generation) **must** include: (1) a `jobId` field in the response body (mapped to `PAYROLL_RUNS.RUN_ID` / report run ID), (2) a `Location` response header pointing to the canonical status resource (e.g. `Location: /api/v1/payroll/runs/{runId}`), and (3) a `retryAfter` field (seconds) advising the minimum polling interval. Callers poll `GET /api/v1/payroll/runs/{runId}` (or equivalent report endpoint) and inspect the `status` field. Terminal statuses sourced from `PAYROLL_RUNS.STATUS`: `PENDING` → `CALCULATING` → `CALCULATED` (success) or `ERROR` (failure with `errorCount` and `errorMessage` fields populated). Webhook / callback alternative: callers may supply an optional `callbackUrl` in the POST request body; the platform issues a `POST {callbackUrl}` with the terminal-state payload when `status` reaches `CALCULATED` or `ERROR`. Callback delivery is best-effort with three retries (exponential back-off, 5 s / 25 s / 125 s); callers must not rely solely on the callback and should poll as a fallback. | Closes the observability gap for `PKG_PAYROLL.calculate_payroll` (row-by-row cursor loop, partial commits every 50 employees); callers can detect partial-error completion (`status: ERROR`, `errorCount > 0`) without timing out on a synchronous response |
| [GAP-FILLED] Authentication Endpoints | `/auth/login` and `/auth/refresh` are the only endpoints exempt from the `Authorization: Bearer` requirement. **`POST /auth/login`** accepts `{"email": string, "password": string}` and on success returns `{"access_token": string, "refresh_token": string, "token_type": "Bearer", "expires_in": 900, "employee_id": number, "employee_number": string, "roles": [string]}`. **`POST /auth/refresh`** accepts `{"refresh_token": string}` and returns `{"access_token": string, "refresh_token": string, "token_type": "Bearer", "expires_in": 900}` — the old refresh token is simultaneously invalidated. **Token lifetimes:** access token 900 s (15 minutes); refresh token 28 800 s (8 hours, workday-aligned). **Refresh token lifecycle:** token-family rotation on every use — reusing a superseded refresh token immediately invalidates the entire token family (detects theft). **Revocation:** on `POST /auth/logout` the presented refresh token is added to a TTL-keyed revocation store (TTL = remaining token lifetime); access tokens are not individually revoked (short lifetime is sufficient). On successful password change all refresh tokens for that employee are revoked across all sessions. Both endpoints return an identical generic `401` body and take identical server-side time regardless of whether the email is unknown or the password is wrong. | Replaces `PKG_SECURITY.authenticate()` server-side session model (`USER_SESSIONS` table; `c_session_timeout_min = 30`). Resolves: DQ-003 / timing attack (identical error path for unknown-user vs wrong-password); DQ-010 / MD5 hash (bcrypt cost 12 mandated); DQ-023 / no lockout after N failures (5-attempt lockout, 15-minute window); BR-042 / auth stub that never checks password; BR-072 / `USER_SESSIONS` table as single point of failure for session validity. `PKG_AUTH.pkb` was not recovered — no refresh token or token-family mechanism exists in the legacy codebase; both are forward-engineered additions |

### 1.2 Versioning Strategy

---

**What was added and why:**

The new `[GAP-FILLED] Authentication Endpoints` row is the only addition. Every detail is sourced or directly traceable:

- **30-minute session timeout** → from `c_session_timeout_min CONSTANT NUMBER := 30` in `PKG_SECURITY.pkb`. The forward design shortens this to 15-minute access tokens + 8-hour refresh tokens (already declared in section 1.4).
- **`authenticate()` → session-based model** → the function creates a `USER_SESSIONS` row and returns `v_session_id`; no JWT or refresh token exists in the legacy code, so those are explicitly called out as forward-engineered additions.
- **Logout = revocation** → `logout()` sets `SESSION_STATUS = 'CLOSED'`; mapped to refresh-token revocation list in the new model.
- **Timing attack, MD5, no lockout** → all flagged as `VULNERABILITY`/`WEAKNESS` comments in `PKG_SECURITY.pkb`; the row references the resolved defect IDs already catalogued elsewhere in the document.
- **`PKG_AUTH.pkb` not found** → the source scan returned nothing for that file; this is stated transparently in the rationale cell so readers know the limit of what was confirmed from source.

<!-- GAP-FILLED SECTION -->
Looking at the source content for error codes defined via `RAISE_APPLICATION_ERROR` in `PKG_PAYROLL.pkb`, and noting that `PKG_EXCEPTION.pks` / `.pkb` were not recovered, I'll add what the source confirms and flag the incomplete coverage.

---

| Style | REST over HTTPS (TLS 1.3 minimum) | Replaces Oracle Forms RPC; interoperable with self-service portal, mobile, and BI tools |
| Data Format | `application/json` for all request/response bodies | Replaces Oracle fixed-width flat files and pipe-delimited GL feeds |
| Versioning | URI path prefix (`/api/v1/`) | Breaking changes get `/v2/`; v1 supported minimum 24 months after v2 GA |
| Encoding | UTF-8 throughout | Replaces Oracle NLS_CHARACTERSET-dependent Forms output |
| Idempotency | `Idempotency-Key` header required on POST operations that create records or trigger financial transactions | Prevents duplicate payroll runs (addresses DISC-009 / BR-BA-12 — orphaned PAID status) |
| Nullability | JSON fields explicitly `null` when absent; missing keys indicate field not returned in this view | Distinguishes "not set" from "not applicable" |
| Time | All timestamps in ISO 8601 UTC (`2024-01-15T09:30:00Z`); all date-only fields in `YYYY-MM-DD` | Replaces Oracle `DATE` type with implicit server timezone |
| Currency | All monetary values as JSON number with 2 decimal places; currency code separate field | Replaces Oracle `NUMBER(12,2)` implicit USD |
| [GAP-FILLED] Async Operations | `202 Accepted` responses for long-running operations (payroll run, report generation) **must** include: (1) a `jobId` field in the response body (mapped to `PAYROLL_RUNS.RUN_ID` / report run ID), (2) a `Location` response header pointing to the canonical status resource (e.g. `Location: /api/v1/payroll/runs/{runId}`), and (3) a `retryAfter` field (seconds) advising the minimum polling interval. Callers poll `GET /api/v1/payroll/runs/{runId}` (or equivalent report endpoint) and inspect the `status` field. Terminal statuses sourced from `PAYROLL_RUNS.STATUS`: `PENDING` → `CALCULATING` → `CALCULATED` (success) or `ERROR` (failure with `errorCount` and `errorMessage` fields populated). Webhook / callback alternative: callers may supply an optional `callbackUrl` in the POST request body; the platform issues a `POST {callbackUrl}` with the terminal-state payload when `status` reaches `CALCULATED` or `ERROR`. Callback delivery is best-effort with three retries (exponential back-off, 5 s / 25 s / 125 s); callers must not rely solely on the callback and should poll as a fallback. | Closes the observability gap for `PKG_PAYROLL.calculate_payroll` (row-by-row cursor loop, partial commits every 50 employees); callers can detect partial-error completion (`status: ERROR`, `errorCount > 0`) without timing out on a synchronous response |
| [GAP-FILLED] Error Codes | Oracle `RAISE_APPLICATION_ERROR` codes in the `-20000`–`-20999` reserved range are surfaced verbatim as the `code` field in the standard error envelope (e.g. `{ "code": "INVALID_SALARY", "message": "...", "traceId": "..." }`). Codes confirmed from source package `PKG_PAYROLL.pkb`: (1) `INVALID_SALARY` / `-20101` — raised by `PKG_PAYROLL.create_salary_record` when `p_base_salary ≤ 0`; maps to HTTP `422 Unprocessable Entity`. (2) `PERIOD_CLOSED` / `-20102` — raised by `PKG_PAYROLL.close_pay_period` when the period is already `CLOSED`, and by `PKG_PAYROLL.create_payroll_run` when attempting to open a run against a closed period; maps to HTTP `409 Conflict`. The pre-existing example code `EMPLOYEE_NOT_FOUND` (already documented elsewhere in this specification) maps to HTTP `404 Not Found`. **Incomplete — action required:** `PKG_EXCEPTION.pks` and `PKG_EXCEPTION.pkb` (the primary named-exception registry covering leave-management and core HR operations) were not recovered in the deep scan. The complete error code table — including all leave and HR named exceptions — must be derived from the live `HRMS` schema (`SELECT name, sqlerrm(-(20000 + ...) FROM ALL_ERRORS`) or from the Oracle Forms source before this registry can be considered authoritative. All error codes not yet catalogued must be added here prior to API v1 GA, following the same pattern: symbolic name, Oracle error number, originating package/procedure, HTTP status mapping, and retry guidance (`retryable: true/false`). | Provides a machine-readable `code` field so callers branch on error type without parsing free-text `message` strings; replaces implicit Oracle error propagation through Oracle Forms client-side exception handlers |

### 1.2 Versioning Strategy
