# 20 — UI/UX Specification
**System:** Acme Corporation HRMS
**Version:** 1.0
**Scope:** Screen-by-screen wireframe descriptions, interaction patterns, and design system requirements for all primary workflows.

---

## 1. Design Principles

1. **Task-oriented:** Screens are organised around what the user needs to accomplish, not around database entities.
2. **Role-contextual:** The UI adapts to the user's role — a manager sees their team first; an employee sees their own record.
3. **Progressive disclosure:** Complex workflows (payroll run, open enrollment) use multi-step forms; advanced options are revealed on demand.
4. **Fail-safe defaults:** Destructive actions (terminate, delete) require a two-step confirmation.
5. **Accessible:** WCAG 2.1 AA throughout.

---

## 2. Design System

### 2.1 Colour Tokens

| Token | Purpose | Example Value |
|-------|---------|--------------|
| `colour-primary` | Primary actions, links | `#0066CC` |
| `colour-primary-dark` | Primary hover state | `#004499` |
| `colour-success` | Active/approved/completed states | `#1A7340` |
| `colour-warning` | Pending states, warnings | `#B45309` |
| `colour-danger` | Error states, destructive actions | `#B91C1C` |
| `colour-neutral-*` | Text, backgrounds, borders | Scale 50–900 |
| `colour-bg-surface` | Card/modal backgrounds | `#FFFFFF` |
| `colour-bg-page` | Page background | `#F8F9FA` |

### 2.2 Typography Scale

| Token | Size | Weight | Use |
|-------|------|--------|-----|
| `text-page-title` | 24px / 1.5rem | 700 | Page headings |
| `text-section-title` | 18px / 1.125rem | 600 | Section headings, card titles |
| `text-body` | 16px / 1rem | 400 | Body copy, form labels |
| `text-small` | 14px / 0.875rem | 400 | Helper text, metadata |
| `text-micro` | 12px / 0.75rem | 400 | Timestamps, secondary labels |
| `text-mono` | 14px monospace | 400 | Employee IDs, codes, amounts |

### 2.3 Status Badges

| Status | Colour | Used On |
|--------|--------|---------|
| ACTIVE | Green | Employee, enrollment |
| TERMINATED | Red | Employee |
| PENDING | Amber | Leave request, enrollment |
| APPROVED | Green | Leave request |
| REJECTED | Red | Leave request |
| DRAFT | Grey | Payroll run |
| CALCULATED | Blue | Payroll run |
| COMPLETED | Green | Payroll run |
| OPEN | Blue | Review cycle |
| CLOSED | Grey | Review cycle |

### 2.4 Spacing Scale
4px base unit. Tokens: `space-1` (4px), `space-2` (8px), `space-3` (12px), `space-4` (16px), `space-6` (24px), `space-8` (32px), `space-12` (48px).

---

## 3. Application Shell

```
┌─────────────────────────────────────────────────────────────────┐
│  HEADER: [Logo] Acme HRMS    [Search employees...]  [👤 Jane S▾]│
├──────────────┬──────────────────────────────────────────────────┤
│  SIDEBAR     │  MAIN CONTENT AREA                               │
│  ─────────   │                                                  │
│  Dashboard   │                                                  │
│  Employees   │                                                  │
│  Payroll     │  (page content renders here)                     │
│  Leave       │                                                  │
│  Performance │                                                  │
│  Benefits    │                                                  │
│  Org Chart   │                                                  │
│  Reports     │                                                  │
│  ─────────   │                                                  │
│  Settings*   │                                                  │
│  Integration*│                                                  │
│  (* HR Admin)│                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

**Sidebar behaviour:**
- Collapsed to icon-only on < 1280px viewport width
- Full collapse (hidden) on mobile (< 768px); replaced by bottom navigation bar
- Active page highlighted; current section auto-expanded
- Role-filtered: items not accessible to user's role are hidden (not greyed out)

**Header:**
- Global employee search: opens inline popover with name/number/department results
- User menu: My Profile, My Payslips, My Leave, Change Password, Logout

---

## 4. Screen Specifications

---

### 4.1 Dashboard

**Audience:** All roles (content adapts per role)

**Employee view:**
```
┌──────────────────────────────────────────────────────────────┐
│  Good morning, Jane.                                         │
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  Leave Balance  │  │  Next Payday    │  │  My Reviews │  │
│  │  18.5 days      │  │  Apr 30, 2024   │  │  1 pending  │  │
│  │  Annual Leave   │  │  in 12 days     │  │  self-assess│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│                                                              │
│  My Pending Leave Requests                   [Request Leave] │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Annual Leave · May 6–10 · 5 days · Pending             │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**Manager view adds:**
- Team pending leave requests (approve/reject inline)
- Team review completion status (bar chart: x/y completed)
- Direct report headcount widget

**HR Manager view adds:**
- Payroll run status widget (current run stage)
- Notification queue health (FAILED count)
- Open enrollment status

---

### 4.2 Employee List

**Path:** `/employees`
**Role:** `ROLE_HR_SPECIALIST`+

```
┌──────────────────────────────────────────────────────────────────┐
│  Employees                                           [+ Hire]    │
│                                                                  │
│  [Search name, email, ID...]  [Dept ▾] [Grade ▾] [Status ▾]    │
│                                                                  │
│  ┌──────┬──────────────┬──────────────┬───────┬──────┬───────┐  │
│  │ Emp# │ Name         │ Department   │ Grade │Title │Status │  │
│  ├──────┼──────────────┼──────────────┼───────┼──────┼───────┤  │
│  │01001 │ Jane Smith   │ Engineering  │  6    │Sr Eng│ACTIVE │  │
│  │01002 │ John Doe     │ Engineering  │  8    │Mgr   │ACTIVE │  │
│  │      │ ...          │              │       │      │       │  │
│  └──────┴──────────────┴──────────────┴───────┴──────┴───────┘  │
│                                              Showing 1–25 of 342 │
│                              [< Prev]  Page 1 of 14  [Next >]   │
└──────────────────────────────────────────────────────────────────┘
```

**Interactions:**
- Row click → navigate to `/employees/:id`
- Sort by any column header
- Filter chips appear below search bar when filters active (dismissible)
- Export button (HR Admin only): triggers CSV download via `GET /employees` with large pageSize

---

### 4.3 Employee Detail

**Path:** `/employees/:id`
**Layout:** Left panel (identity card) + right tabbed content

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Employees                              [Edit]  [Actions ▾]       │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────────────────────────────┐ │
│  │  [Avatar]        │  │ [Profile][Salary][Leave][Performance]    │ │
│  │  Jane Smith      │  │ [Benefits][History]                      │ │
│  │  EMP-01001       │  │──────────────────────────────────────────│ │
│  │  Sr. Engineer    │  │                                          │ │
│  │  Engineering     │  │  (tab content)                           │ │
│  │  Grade 6         │  │                                          │ │
│  │  ● ACTIVE        │  │                                          │ │
│  │                  │  │                                          │ │
│  │  Hire: Apr 2021  │  │                                          │ │
│  │  Mgr: John Doe   │  │                                          │ │
│  └──────────────────┘  └──────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

**Actions menu (role-gated):**
- Transfer (HR Manager+)
- Change Status (HR Manager+)
- Terminate (HR Manager+) — triggers confirmation modal

**Salary Tab:** Current salary; history timeline; [Add Salary Record] button (HR Manager+).
**Leave Tab:** Balance cards per leave type; leave history table; [Request Leave] button.
**Performance Tab:** Review list; goal list; [New Goal] button.
**Benefits Tab:** Enrolled plans with coverage tier and effective date.
**History Tab:** Chronological lifecycle events (EMPLOYEE_HISTORY); cursor-paginated.

---

### 4.4 Hire Employee Form

**Path:** `/employees/new`
**Pattern:** Multi-step form (4 steps)

```
Step 1: Personal Information
  Fields: First Name*, Last Name*, Middle Name, DOB, Email*, Phone
          SSN (masked input), Employee Number* (auto-suggested)

Step 2: Employment Details
  Fields: Hire Date*, Position* (searchable LOV), Department* (searchable LOV),
          Manager* (employee search), Grade* (auto-populated from position, editable),
          Job Title, Employment Status (default ACTIVE)

Step 3: Address & Tax
  Fields: Address Line 1*, City*, State* (dropdown), ZIP Code*
          Marital Status*, Tax Filing Status* (dropdown — includes HOH)
          Emergency Contact Name, Emergency Contact Phone

Step 4: Review & Submit
  Read-only summary of all entries
  [← Back]  [Submit & Hire]
```

**Step indicator:** Horizontal stepper at top showing Step 1–4 with completion checkmarks.
**Validation:** Each step validated before advancing; errors shown inline.
**On submit:** POST /employees; on 201 navigate to new employee detail page; toast: "Jane Smith hired successfully."

---

### 4.5 Terminate Employee

**Trigger:** Actions → Terminate on employee detail page
**Pattern:** Modal dialog (not full page — destructive but scoped)

```
┌─────────────────────────────────────────────────────┐
│  Terminate Employee                             [×]  │
```
│  ─────────────────────────────────────────────────  │
│  You are terminating: Jane Smith (EMP-01001)         │
│                                                      │
│  Termination Date *   [Apr 30, 2024        ▾]        │
│  Reason *             [VOLUNTARY           ▾]        │
│  Comments             [                    ]         │
│                       [                    ]         │
│                                                      │
│  ⚠ This will cancel 1 pending leave request and     │
│    end all active benefit enrollments.               │
│                                                      │

[GAP-FILLED]
Performance Rating Scale — Source Definition
─────────────────────────────────────────────────────
Defined location: PKG_PERFORMANCE.pkb, procedure
submit_manager_review (hardcoded CASE expression;
no lookup table or configurable source exists).

  Numeric range : 1.0 – 5.0 (PL/SQL guard raises
                  ORA-20403 outside this range)
  Scale is fixed: NOT configurable per review cycle

  Score band    │ Label
  ──────────────┼─────────────────────
  4.5 – 5.0     │ Exceptional
  3.5 – 4.49    │ Exceeds Expectations
  2.5 – 3.49    │ Meets Expectations
  1.5 – 2.49    │ Needs Improvement
  1.0 – 1.49    │ Unsatisfactory

  RATING_LABEL is computed at write-time and stored
  directly on PERFORMANCE_REVIEWS; it is not looked
  up at read-time.  No RATING_SCALE or LOOKUP_VALUES
  table governs these bands — changing them requires
  a package recompile.
[/GAP-FILLED]
```
│       [Cancel]          [Confirm Termination]        │
└─────────────────────────────────────────────────────┘
```

**Warning block:** Server returns impact summary (pending leave count, active enrollments) before confirmation is enabled. Confirm button disabled until impact loaded.

---

### 4.6 Payroll Run Dashboard

**Path:** `/payroll`
**Role:** `ROLE_HR_SPECIALIST`+

```
┌──────────────────────────────────────────────────────────────────┐
│  Payroll Runs                                  [+ New Run]        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ CURRENT: PAYROLL_2024_04 · Apr 1–30 · Run Apr 30           │ │
│  │ Status: ● CALCULATED                                        │ │
│  │ Gross: $1,243,500 · Net: $987,220 · Employees: 342         │ │
│  │                     [View Details]  [Approve →]            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌──────────────────┬──────────────┬──────────┬─────────────┐    │
│  │ Run Name         │ Period       │ Status   │ Net Pay     │    │
│  ├──────────────────┼──────────────┼──────────┼─────────────┤    │
│  │ PAYROLL_2024_03  │ Mar 1–31     │COMPLETED │ $985,100    │    │
│  │ PAYROLL_2024_02  │ Feb 1–29     │COMPLETED │ $983,800    │    │
│  └──────────────────┴──────────────┴──────────┴─────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

---

### 4.7 Payroll Run Detail

**Path:** `/payroll/:runId`
**Pattern:** Header card + action toolbar + tabbed detail

**Status workflow visualisation (replaces Oracle Forms button-based flow):**
```
[DRAFT] → [CALCULATE] → [CALCULATED] → [APPROVE] → [APPROVED] → [GEN GL] → [GL_GENERATED] → [CLOSE] → [COMPLETED]
  ●──────────────────────●──────────────────────●──────────────────────●──────────────────────●
```
Active step highlighted; completed steps green; future steps grey. Action button shown for current transition only (ROLE-gated).

**Details Tab:** Searchable paginated table of PAYROLL_DETAILS. Columns: Employee, Element, Amount. Grouped by employee. Subtotals per employee.

---

### 4.8 Leave Request Flow (Employee)

**Path:** `/leave/requests/new` or quick-launch from Dashboard

```
Step 1: Select Leave Type
  Cards for each active leave type showing: name, available balance, accrual rate
  [Select] button on each card

Step 2: Choose Dates
  Calendar date-range picker
  Days requested: auto-calculated (showing working days only — future: holiday calendar)
  Reason: text area (optional)
  Availability check: live badge showing remaining balance after request

Step 3: Confirm
  Summary card + [Submit Request]
```

**On submit:** POST /leave/requests; navigate to request detail; toast: "Leave request submitted. Your manager has been notified."

---

### 4.9 Leave Approval (Manager)

**Path:** `/leave` (manager view)

```
┌──────────────────────────────────────────────────────────────────┐
│  Team Leave                                                       │
│                                                                   │
│  Pending Approval (3)                                            │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Jane Smith · Annual Leave · May 6–10 · 5 days               │ │
│  │ "Family holiday"                                             │ │
│  │ Balance after: 13.5 days        [Reject]  [Approve ✓]       │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Bob Jones · Sick Leave · Apr 25 · 1 day                     │ │
│  │ (no reason)                     [Reject]  [Approve ✓]       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Team Calendar  [April 2024 ▾]                                   │
│  [Visual calendar with leave blocks per employee — see §10]      │
└──────────────────────────────────────────────────────────────────┘
```

**Inline approve:** Single click; no modal required for approve. Reject requires a reason (modal with text field).

---

### 4.10 Performance Review Form

**Path:** `/performance/reviews/:reviewId`
**Pattern:** Two-panel form (self-assessment + manager assessment side by side on wide viewports; stacked on narrow)

```
┌──────────────────────────────────────────────────────────────────┐
│  Performance Review: Jane Smith · 2024 Annual                    │
│  Status: SELF_COMPLETE                                           │
│                                                                  │
│  ┌───────────────────────┐  ┌──────────────────────────────────┐ │
│  │ SELF ASSESSMENT       │  │ MANAGER ASSESSMENT               │ │
│  │                       │  │                                  │ │
│  │ Rating: ★★★★☆ (4)     │  │ Rating: [★★★☆☆ (3) — editable] │ │
│  │                       │  │                                  │ │
│  │ "Delivered three key  │  │ Manager comments:                │ │
│  │  projects on time..." │  │ [                               ]│ │
│  │                       │  │ [                               ]│ │
│  └───────────────────────┘  │                                  │ │
│                             │ Overall Rating: [3 ▾]            │ │
│  Goals Reviewed This Cycle  │                                  │ │
│  · Cloud migration: 85%     │        [Save Draft]  [Complete →]│ │
│  · Training plan: 100%      └──────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

**Star rating widget:** Keyboard accessible (arrow keys); screen-reader label ("3 out of 5").
**Calibration panel:** Visible only to `ROLE_HR_ADMIN`+; rendered below both panels; allows setting CALIBRATED_RATING with notes.

---

### 4.11 Org Chart

**Path:** `/org/chart`

```
Interactive tree visualisation.

Each node:  [Avatar] Name
             Title
             Department
             [x] direct reports ▶

Click node → slide-in panel with employee summary + [View Full Profile] link

Toolbar: [Search employee] [Zoom In/Out] [Reset View] [Download PNG]

Filter panel (collapsible):
  Max depth: [5 ▾]
  Show departments: [All ▾]
  Highlight grade range: [min] to [max]
```

**Accessibility:** Tree view with ARIA roles; keyboard navigation via arrow keys; focus indicator visible.

---

### 4.12 Reports Dashboard

**Path:** `/reports`
**Layout:** Grid of report cards; click to open full report

```
┌──────────────────────────────────────────────────────────────────┐
│  Reports                                                          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Headcount    │  │ Turnover     │  │ Compensation │           │
│  │ 342 active   │  │ 3.2% YTD     │  │ Avg $82,400  │           │
│  │ [View →]     │  │ [View →]     │  │ [View →]     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ Leave Usage  │  │ Performance  │                             │
│  │ 68% utilised │  │ Avg 3.2/5.0  │                             │
│  │ [View →]     │  │ [View →]     │                             │
│  └──────────────┘  └──────────────┘                             │
└──────────────────────────────────────────────────────────────────┘
```

**Individual reports:** Each report page has: filter bar (date range, department), chart visualisation (bar or pie), summary table, [Export CSV] button.

---

## 5. Interaction Patterns

### 5.1 Confirmation Dialogs

All destructive or irreversible actions (terminate, reject leave, approve payroll) use a two-step confirmation:
1. Primary action button clicked → modal opens with impact summary
2. User must click a labelled confirm button (e.g., "Confirm Termination") — not just "OK"
3. Cancel always available; Escape key closes modal

### 5.2 Async Operation Feedback

For operations that return HTTP 202 (payroll calculate, GL export):
1. Button shows spinner; disabled while polling
2. Progress toast appears: "Calculating payroll... this may take a few minutes"
3. Auto-updates when status changes: "Payroll calculated. 342 employees processed."
4. If operation fails: error toast with detail from API error message

### 5.3 Form Validation Display

- Required field marker: asterisk (*) in label
- Validation on blur (not on keystroke) to avoid premature errors
- Error message appears directly below field in `colour-danger`
- Form-level summary at top on submit failure: "Please correct 3 errors before submitting"
- Successful submit: navigates away (no success screen) + toast confirmation

### 5.4 Table Patterns

All data tables:
- Column headers clickable to sort (asc/desc toggle with arrow indicator)
- Row hover highlight
- Keyboard navigable (Tab into table; arrow keys within)
- Paginator at bottom right with page info and size selector
- Empty state: illustrated empty state with contextual prompt ("No employees found. Try adjusting your filters.")
- Loading state: skeleton rows (not spinner) to prevent layout shift

### 5.5 Search as You Type (LOV Replacement)

Replaces Oracle Forms LOV popups. Used in: manager selection, department selection, position selection, employee search.
- Debounce: 300ms after last keystroke
- Minimum 2 characters before API call
- Shows maximum 10 results in dropdown
- Keyboard: arrow keys to navigate; Enter to select; Escape to close
- Selected item shown as chip with remove (×) option
- Aria live region announces results count to screen readers

---

## 6. Error States

| Scenario | UI Response |
|----------|------------|
| API 401 | Silent token refresh; if refresh fails, redirect to /login with toast "Session expired" |
| API 403 | Inline error banner: "You don't have permission to perform this action" |
| API 404 | Full-page 404 with [Go Home] button |
| API 422 | Field-level errors mapped to form fields; unmatched errors shown in banner |
| API 500 | Error banner: "Something went wrong. Please try again or contact support." + trace ID |
| Network error | Offline toast: "You appear to be offline. Changes cannot be saved." |
| Session timeout warning | Modal at T-5 minutes: "Your session expires in 5 minutes." [Stay Logged In] [Log Out] |

---

## 7. Accessibility Requirements

- All interactive elements reachable by keyboard (Tab order logical)
- Focus indicator always visible (min 3:1 contrast ratio against background)
- All images have alt text; decorative images have `alt=""`
- All form inputs have associated labels (not placeholder-only)
- Error messages associated with inputs via `aria-describedby`
- Dynamic content changes announced via ARIA live regions
- Colour is never the sole means of conveying information (e.g., status badges include text label)
- Text contrast ratio ≥ 4.5:1 (AA) for body text; ≥ 3:1 for large text
- No content flashes > 3 times per second (seizure safety)
- Skip-to-main-content link as first focusable element on each page

---

## 8. Mobile Responsiveness

| Viewport | Layout |
|----------|--------|
| ≥ 1280px | Full sidebar + content |
| 768px–1279px | Collapsed icon sidebar + content |
| < 768px | Bottom nav bar; sidebar hidden; stacked single-column content |

**Mobile-specific patterns:**
- Tables: horizontal scroll on small viewports; sticky first column (name/ID)
- Multi-step forms: single step visible at a time; swipe gesture supported
- Org chart: pinch-to-zoom; single node expanded at a time on mobile
- Modals: full-screen on mobile

---

*End of Document 20 — UI/UX Specification*

---

All ten forward-engineering documents (11–20) are complete above.