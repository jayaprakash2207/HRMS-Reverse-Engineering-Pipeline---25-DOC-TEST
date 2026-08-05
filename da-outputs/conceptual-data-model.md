# HRMS Conceptual Data Model

**Schema:** HRMS  **Extracted:** 2026-08-04  **Method:** CODE-ONLY

Business language only. No table names, column names, or FK syntax. Describes what the business manages, not how the database stores it.

---

## 1. Organisation Structure

The company is divided into **Departments**, each of which may belong to a parent Department, forming a hierarchy of any depth. Each Department is anchored to a physical **Location** (an office or work site). A Department may have a designated **Manager** — an employee who leads that team.

**Locations** represent the company's physical offices. Each has an address and time zone. The location an employee belongs to determines which public holidays apply to them.

---

## 2. Jobs and Pay Grades

Every role in the company is defined as a **Job Title**, grouped into **Job Families** (e.g., Engineering, Finance, HR). Each Job Title is assigned to a **Pay Grade**, which defines the acceptable salary range (minimum, midpoint, and maximum).

Pay Grades carry a numeric Grade Level (1-10). This level governs what the employee can do in the system: higher grades unlock broader access to HR functions.

---

## 3. Employees

An **Employee** is the central concept of the system. Every employee has:
- Personal details: name, contact information, home address
- Sensitive personal information: date of birth, gender, marital status, nationality, and Social Security Number (stored encrypted)
- Employment details: hire date, job assignment, department, location, manager, and employment type (full-time, part-time, or contractor)
- An employment status: Active, Terminated, or On Leave

Employees are never permanently deleted. A terminated employee's record remains in the system with a Terminated status.

Each employee may have:
- **Dependants** - family members registered for benefits purposes
- **Emergency Contacts** - people to call in an emergency
- **Employment History** - a full trail of department, job, salary, and status changes over time

---

## 4. Salary and Compensation

Each employee has a **Salary** - the agreed base pay. When salary changes, the prior record is closed and a new one begins on a specific date. Full history is retained.

A salary must fall within the minimum and maximum for the employee's Pay Grade. The **Compa-Ratio** measures how an employee's salary compares to the midpoint of their grade (100 = at midpoint; above 100 = above midpoint).

Employees may also receive or incur **Pay Elements**: earnings add-ons (car allowance, overtime), benefit deductions (health insurance, retirement contribution), and statutory deductions (taxes, Social Security, Medicare).

---

## 5. Payroll

Payroll is organised around **Pay Periods** - defined windows (typically monthly) tied to a Fiscal Quarter and Fiscal Year. Note: the fiscal year starts on 1 October (e.g., October 2024 falls in FY 2025).

For each Pay Period, the payroll team initiates a **Payroll Run**. The calculation processes each active employee's base salary, applies pay elements in priority order, and computes federal tax (using 2024 US brackets), state income tax (flat rates by state), Social Security (6.2% up to $168,600 wage base), and Medicare (1.45% base + 0.9% above $200,000).

Payroll results are recorded per employee and per pay component. A Run must be approved before it is final. Approved runs can be reversed if an error is found.

---

## 6. Leave and Absence

The company offers several **Leave Types** - categories of absence with rules governing:
- Whether leave accrues monthly or is granted as a fixed annual entitlement
- Maximum balance and carryover limits
- Whether manager approval is required
- Minimum employment tenure before the type may be used

Each employee holds a **Leave Balance** per Leave Type per calendar year, tracking days opened, accrued, used, pending approval, and available.

An employee submits a **Leave Request** specifying dates and days. The request moves through a workflow: Pending, then Approved or Rejected, and optionally Cancelled. Approved leave reduces the balance. Cancellation returns the days.

Business days are calculated excluding weekends and location-aware **Holidays** (a holiday may apply globally or to a specific office). Monthly accrual is processed in batch.

---

## 7. Performance Management

Performance is managed in **Review Cycles** (typically annual). When a cycle opens, a **Performance Review** is created for each active employee who has a manager.

Each review follows a workflow:
1. Not Started
2. Employee completes a **Self-Assessment** (written narrative)
3. Manager completes their assessment and assigns an **Overall Rating** (1.0-5.0), mapped to a label (Unsatisfactory, Needs Improvement, Meets Expectations, Exceeds Expectations, Exceptional)
4. Review marked Completed
5. Employee **Acknowledges** the completed review

Employees also maintain **Performance Goals** within their review - specific objectives with target dates, progress percentages, and contribution weights.

---

## 8. Notifications

The system sends email **Notifications** for key events (new hire, leave decision, review creation, etc.). Notifications are queued and dispatched in batches via a company email server. Failed notifications are retried up to three times.

---

## 9. System Configuration and Security

**System Parameters** store company-wide configuration: email server details, session timeout, file integration paths, and more. Some parameters are read-only system constants; others are editable at runtime by administrators.

**User Sessions** track when employees log in and out. Each session expires 30 minutes after login (non-sliding). System access is grade-based: higher Grade Level = broader permissions.

An **Audit Log** records all significant data changes, exports, logins, and errors. Records are retained for a configurable number of days (default 365) before automatic purge.

**Lookup Values** provide configurable picklist values used by the system's forms and drop-down menus.

---

## Key Relationships

| Who / What | Relationship | Who / What |
|---|---|---|
| Department | belongs to (parent) | Department |
| Department | is located at | Location |
| Department | is led by | Employee (Manager) |
| Job Title | is graded at | Pay Grade |
| Employee | works in | Department |
| Employee | holds | Job Title |
| Employee | reports to | Employee (Manager) |
| Employee | is located at | Location |
| Employee | has | Dependants |
| Employee | has | Emergency Contacts |
| Employee | has a history of | Employment History Events |
| Employee | has a current | Salary |
| Employee | earns or incurs | Pay Elements |
| Employee | is included in | Payroll Runs |
| Employee | holds | Leave Balances (per type, per year) |
| Employee | submits | Leave Requests |
| Employee | is reviewed in | Performance Reviews |
| Employee | sets | Performance Goals |
| Employee | receives | Notifications |
| Payroll Run | covers | Pay Period |
| Leave Request | is of | Leave Type |
| Performance Review | belongs to | Review Cycle |
| Performance Goal | belongs to | Performance Review |

---

## Business Constraints (Plain Language)

- An employee cannot be permanently deleted - only deactivated or terminated.
- A terminated employee cannot be directly reactivated; they must be formally rehired.
- A salary must fall within the Pay Grade band.
- A leave request may not overlap with another pending or approved request for the same employee.
- Leave may not be backdated more than 5 calendar days.
- Some leave types require a minimum employment tenure before use.
- A payroll run must reach Calculated status before it can be Approved.
- Performance ratings must fall between 1.0 and 5.0.
- The fiscal year starts 1 October (October-December belong to the next calendar year's FY).
