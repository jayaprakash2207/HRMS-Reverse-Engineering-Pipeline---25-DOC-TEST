# 19 — Frontend Architecture
**System:** Acme Corporation HRMS
**Version:** 1.0
**Context:** Replaces Oracle Forms 6i/10g UI. Oracle Forms is a thick-client, form-based UI with built-in LOV (List of Values) popups, master-detail blocks, and direct Oracle DB connectivity. The target is a modern browser-based SPA.

---

## 1. Oracle Forms Migration Mapping

Each Oracle Forms form maps to one or more SPA views. The Oracle Forms concepts that need explicit replacement:

| Oracle Forms Concept | SPA Equivalent |
|---------------------|---------------|
| Form module (.fmb) | Page / Route |
| Data block (master) | Container component with data-fetch hook |
| Data block (detail) | Nested component or tab panel |
| LOV (List of Values) popup | Async combobox / search-as-you-type dropdown |
| Canvas (tab / stacked) | Tab component or multi-step form |
| Trigger (WHEN-VALIDATE-ITEM) | Field-level validation (real-time, on-blur) |
| Trigger (ON-LOCK) | Optimistic locking via ETag / version field |
| Built-in navigation (Next Record) | Paginated table with inline row selection |
| WHEN-NEW-FORM-INSTANCE | Route `useEffect` on mount |
| PL/SQL call from button | API call from event handler |
| Alert dialog | Modal confirmation component |

---

## 2. Framework Selection

Three options evaluated. Final selection via ADR-006.

| Option | Framework | Language | Notes |
|--------|-----------|----------|-------|
| **Option A** | React 18 + TypeScript | TypeScript | Largest ecosystem; flexible; requires architectural conventions (not opinionated) |
| **Option B** | Angular 17 | TypeScript | Opinionated; built-in forms, routing, DI; good for enterprise HR applications |
| **Option C** | Vue 3 + TypeScript | TypeScript | Gentler learning curve; good for team with mixed experience |

**Recommendation:** Angular 17 if the team is building a traditional HR enterprise app and values conventions; React 18 if the team prefers composability and has frontend expertise. Both are valid.

**Framework-agnostic requirements** (apply regardless of selection):
- TypeScript strict mode
- Component-based architecture
- Declarative routing
- Form library with built-in validation
- State management for shared auth/session state
- Accessibility: WCAG 2.1 AA

---

## 3. Application Structure

```
src/
├── core/                      # Framework-independent application core
│   ├── auth/                  # JWT storage, token refresh, auth guards
│   ├── api/                   # HTTP client, interceptors, error handling
│   ├── models/                # TypeScript interfaces matching API response DTOs
│   └── validators/            # Shared field validation rules
│
├── features/                  # One directory per bounded context
│   ├── employees/             # BC-01
│   │   ├── pages/             # EmployeeListPage, EmployeeDetailPage, HireEmployeePage
│   │   ├── components/        # EmployeeCard, EmployeeStatusBadge, EmployeeSearchBar
│   │   ├── services/          # EmployeeApiService (wraps API client)
│   │   └── models/            # EmployeeDto, EmployeeSummaryDto
│   ├── payroll/               # BC-02
│   ├── leave/                 # BC-03
│   ├── performance/           # BC-04
│   ├── benefits/              # BC-05
│   ├── org/                   # BC-07
│   ├── notifications/         # BC-08
│   ├── integration/           # BC-09
│   └── reports/               # BC-10
│
├── shared/                    # Reusable UI components (no business logic)
│   ├── components/            # DataTable, Modal, Badge, LoadingSpinner, ErrorBanner
│   ├── forms/                 # FormField, DatePicker, CurrencyInput, RoleGuard
│   └── layouts/               # AppShell, SideNav, Header, PageContainer
│
└── assets/                    # Static assets
```

---

## 4. Routing Structure

```
/                               → Dashboard (role-based content)
/login                          → Login page (public)

/employees                      → Employee list
/employees/new                  → Hire employee form
/employees/:id                  → Employee detail (tabs: Profile, Salary, Leave, Performance, Benefits)
/employees/:id/edit             → Edit employee
/employees/:id/history          → History log

/payroll                        → Payroll run list
/payroll/new                    → Create payroll run
/payroll/:runId                 → Payroll run detail + approval workflow
/payroll/:runId/details         → Line-item detail view

/leave                          → Leave management (manager: team view; employee: own view)
/leave/requests/new             → Submit leave request
/leave/requests/:id             → Request detail + approval actions

/performance                    → Performance overview
/performance/cycles             → Review cycle list
/performance/cycles/:cycleId    → Cycle detail with employee reviews
/performance/reviews/:reviewId  → Individual review form (self + manager tabs)
/performance/goals              → Goal list
/performance/goals/new          → New goal form

/benefits                       → Benefits overview
/benefits/enroll                → Open enrollment flow

/org/chart                      → Interactive org chart

/reports                        → Reports dashboard
/reports/headcount              → Headcount report
/reports/compensation           → Compensation analytics
/reports/turnover               → Turnover report
/reports/leave                  → Leave utilisation report
/reports/performance            → Performance distribution report

/integration                    → Integration & export (HR Admin only)
/settings/notifications         → Notification template management (HR Admin)
/settings/system                → System configuration (System Admin)

/profile                        → Own employee profile + self-service
/profile/leave                  → Own leave balances + request form
/profile/payslips               → Own payslip history
/profile/performance            → Own review and goals
```

---

## 5. Authentication Flow (SPA)

```
1. User lands on any protected route
2. Auth guard checks for valid access token in memory (NOT localStorage)
3. If no token or expired:
   a. Redirect to /login
   b. Store intended route in session for post-login redirect
4. POST /auth/login with credentials
5. Store tokens in memory (access token) and httpOnly cookie (refresh token)
   - Access token: in-memory only (prevents XSS token theft)
   - Refresh token: httpOnly secure cookie (server-set; JS cannot read)
6. On 401 response: attempt silent refresh via POST /auth/refresh
7. On refresh failure: clear state; redirect to /login
8. On logout: POST /auth/logout; clear all in-memory state; navigate to /login
```

**Security notes:**
- No tokens in localStorage (XSS risk)
- No tokens in URL parameters
- CSRF protection on refresh endpoint (SameSite=Strict cookie + custom header)

---

## 6. API Client

**Pattern:** Singleton HTTP client with:
- Base URL from environment configuration
- `Authorization: Bearer {token}` injected by interceptor on all authenticated requests
- Request correlation ID (`X-Request-Id: uuid`) on every request
- 401 interceptor: triggers silent token refresh; queues concurrent requests
- Error normalisation: maps RFC 7807 ProblemDetail to application error model
- Retry: 1 automatic retry on 503 with exponential backoff; no retry on 4xx

**TypeScript contract:** Every API call is typed against DTO interfaces generated from API contract (Document 11). No `any` types on API responses.

---

## 7. State Management

| State Type | Where Stored | Notes |
|-----------|-------------|-------|
| Auth (access token, user identity, roles) | In-memory store (Zustand/NgRx/Pinia) | Cleared on logout; not persisted |
| Server data (employee lists, payroll runs) | Server state library (React Query, TanStack Query, Apollo) | Cache with TTL; invalidate on mutation |
| Form state | Local component state | Not lifted unless cross-component sharing required |
| UI state (sidebar open, active tab) | Local component state | Never in global store |
| Toast/notification alerts | Global UI store | Ephemeral; auto-dismiss |

**Avoid:** Redux/NgRx for server data — use a dedicated server-state library. Reduces boilerplate; automatic cache invalidation on mutation.

---

## 8. Role-Based UI

The UI enforces role-based visibility rules that mirror the API's RBAC (Document 13 §3). The UI is a defence-in-depth layer — the API is the authoritative enforcement point.

**Pattern:**
```typescript
// RoleGuard component hides children if user lacks required role
<RoleGuard roles={['ROLE_HR_MANAGER', 'ROLE_HR_ADMIN']}>
  <ApprovePayrollButton />
</RoleGuard>

// usePermission hook for conditional rendering
const { can } = usePermission()
{can('approve:payroll') && <ApproveButton />}
```

**Grade-sensitive fields:** PII fields (SSN, DOB, bank details) rendered only when `includePii` permission is present. Display masked values otherwise (e.g. `***-**-6789`).

---

## 9. Form Architecture

All data-entry forms use a form library (React Hook Form, Angular Reactive Forms, or VeeValidate) with:

- **Schema validation:** Zod (TypeScript) or Yup schemas derived from API contract field validations
- **Async validation:** email uniqueness, employee number uniqueness, position grade range — server-side via debounced API calls
- **Optimistic UI:** Disabled for financial transactions (payroll approve, salary change) — always await confirmation
- **Dirty state tracking:** Warn on unsaved changes before navigation (fixes Oracle Forms auto-commit behaviour gap)
- **Error display:** Inline error messages below each field; summary error at top for submission failures

---

## 10. Key Component Specifications

### EmployeeSearchBar
- Debounced API call to `GET /employees?search={term}`
- Returns name, employee number, department, grade
- Used in: leave approval (select employee), salary change, transfer

### PayrollRunStatusWidget
- Polls `GET /payroll/runs/{runId}` every 10 seconds while status is `CALCULATING`
- Displays progress spinner during async operation
- Switches to status badge when complete

### OrgChartViewer
- Renders pre-computed tree from `GET /org/chart`
- Interactive: click node to navigate to employee detail
- Depth limited to 5 by default (expandable)
- Accessibility: keyboard navigable; screen reader friendly

### LeaveCalendar
- Visual calendar showing leave requests for team
- Colour-coded by status (PENDING=amber, APPROVED=green, TAKEN=grey)
- Used by managers on leave approval page

### PayslipViewer
- Read-only formatted view of payroll details for one employee + run
- Print-friendly CSS layout (replaces Oracle Reports payslip)

---

## 11. Performance Strategy

| Technique | Applied To |
|-----------|-----------|
| Code splitting by route | All feature modules |
| Lazy loading | All routes except /login and /dashboard |
| Virtual scrolling | Employee list (> 100 rows), audit log |
| Memoisation | Org chart tree nodes; static reference data dropdowns |
| Prefetch on hover | Employee detail prefetched when cursor hovers list row |
| Service worker (offline shell) | Cache app shell for fast reload; data fetches always online |
| Gzip / Brotli compression | All JS/CSS bundles at CDN layer |

---