# BA Agent 2 — Deep Analyst Output
> Pair with: `BA_Structural_Scout.md` | Version: 3.0 | Produced: August 2026

---

## 🔍 Agent 2 — Analysis Summary

- **Domains analysed:** 7 — Employee Management, Payroll, Leave Management, Performance Management, Security & Access, Notifications, Reporting & Integration
- **Chunks processed:** 7 (plus Synthesis Pass)
- **Business Rules catalogued:** 120 (BR-01 through BR-120)
- **Value Streams mapped:** 4
- **Agent 1 LOW CONFIDENCE items resolved:** 14 of 20
- **Discrepancies with Agent 1:** 9 (DISC-001 through DISC-009)

---

## OUTPUT 1 — Business Capability Map

| Capability | Plain English Description | Backing Service | Domain | Agent 1 Match? |
|---|---|---|---|---|
| Hire New Employee | Register a new person in the organisation, assign them to a department and job title, set their starting pay, and notify them and their manager | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Update Employee Personal Details | Change an employee's contact information, address, phone, or email without affecting their employment record | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Transfer Employee | Move an employee to a different department, job, location, or manager, recording the change with a reason and effective date | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Promote Employee | Assign an employee a higher-level job title and increase their pay in a single recorded action | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Terminate Employee | End an employee's employment, cancel their pending leave, close their salary and pay elements, and notify their manager | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Rehire Employee | Reinstate a previously terminated employee with a new start date, department, job, and salary | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Search Employees | Find employees by name, department, status, location, or hire date range | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| View Organisation Chart | See a hierarchical reporting structure starting from any employee, up to a specified number of levels | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Count Headcount | Report the number of active employees in a department or across the organisation at any point in time | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Calculate Employee Tenure | Determine how many years an employee has been with the organisation | PKG_EMPLOYEE | Employee Management | ✅ Confirmed |
| Validate Employee Record | Confirm that an employee's required fields are complete and internally consistent | PKG_EMPLOYEE, PKG_VALIDATION | Employee Management | ✅ Confirmed |
| Create and Manage Salary Records | Record a new salary for an employee with an effective date, automatically closing the previous record | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Create Pay Periods | Generate the full calendar of pay periods for a year, with pay dates adjusted for weekends | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Close Pay Period | Mark a pay period as closed so no further changes can be made | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Create Payroll Run | Initiate a new payroll calculation batch for a given pay period | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Calculate Payroll | Compute gross pay, all tax withholdings, and all deductions for every active employee in a pay run | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Calculate Federal Income Tax | Apply 2024 IRS tax brackets, standard deductions, and W-4 allowances to determine the federal withholding amount per pay period | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Calculate State Income Tax | Apply the applicable state flat tax rate to determine state withholding per pay period | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Calculate Social Security Tax | Apply the 6.2% employee Social Security rate up to the annual wage base | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Calculate Medicare Tax | Apply the 1.45% base Medicare rate plus the 0.9% additional rate on high earners | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Approve Payroll Run | Formally authorise a completed payroll run, enabling it to move toward payment | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Reverse Payroll Run | Cancel an existing payroll run and all its detail lines, returning them to a reversed state | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Generate Payslip | Produce a per-employee pay breakdown showing gross pay, each tax type, deductions, and net pay for a given run | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Generate Pay Register | Produce a comma-separated file summarising all employee pay for a run, organised by department | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Submit Leave Request | Allow an employee to request time off, checking their balance, overlap with other requests, and whether the leave type requires approval | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Approve Leave Request | Allow a manager to approve a pending leave request, updating the employee's used balance | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Reject Leave Request | Allow a manager to decline a pending leave request, releasing the employee's pending balance | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Cancel Leave Request | Allow an employee or the system to cancel a pending or approved leave request, restoring the appropriate balance | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Accrue Leave Monthly | Run the monthly batch process that credits leave days to all eligible active employees according to their leave type rules | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Process Year-End Carryover | Transfer unused leave balances from the current year to the next year, applying per-type carryover limits | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Expire Carried-Over Leave | Remove carried-over leave that has passed its expiry date from employee balances | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Adjust Leave Balance | Allow an HR administrator to manually add or subtract days from an employee's leave balance with a recorded reason | PKG_LEAVE | Leave Management | ✅ Confirmed |
| View Team Leave Calendar | Show a manager all approved and taken leave for their direct reports within a date range | PKG_LEAVE | Leave Management | ✅ Confirmed |
| Calculate Business Days | Count the number of working days between two dates, excluding weekends and public holidays | PKG_LEAVE, PKG_COMMON | Leave Management | ✅ Confirmed |
| Create Performance Review Cycle | Define a new annual review period with start, end, self-review, and manager-review due dates | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Open Review Cycle | Release a draft review cycle so employees and managers can begin their assessments | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Close Review Cycle | Mark a review cycle as complete | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Initiate Employee Review | Create a review record linking an employee to their manager within an active cycle, notifying the employee | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Generate Reviews for Entire Cycle | Automatically create review records for all active employees who have a manager, for a given cycle | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Submit Self-Assessment | Allow an employee to record their self-assessment, advancing the review to the manager review stage | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Submit Manager Review | Allow a manager to record their assessment and assign an overall rating, completing the review | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Acknowledge Review | Allow an employee to confirm they have seen their completed review and optionally add comments | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Track Goals | Record, update, and monitor progress on individual performance goals linked to a review | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| View Rating Distribution | Show the spread of performance ratings across a review cycle, by department or organisation-wide | PKG_PERFORMANCE | Performance Management | ✅ Confirmed |
| Authenticate User | Verify a user's identity using their email and password, create a session, and record the login | PKG_SECURITY | Security & Access | ✅ Confirmed |
| Validate Session | Check whether a given session is still active and has not timed out | PKG_SECURITY | Security & Access | ✅ Confirmed |
| Terminate Session | End a user's session when they log out | PKG_SECURITY | Security & Access | ✅ Confirmed |
| Check Permission | Determine whether an employee has access to a given module and action based on their grade | PKG_SECURITY | Security & Access | ✅ Confirmed |
| Encrypt and Decrypt Sensitive Data | Protect Social Security Numbers using AES-256 encryption; decrypt only when authorised | PKG_SECURITY | Security & Access | ✅ Confirmed |
| Change Password | Allow an employee to update their password, subject to complexity rules | PKG_SECURITY | Security & Access | ⚠️ Corrected — capability exists but is a stub; the actual password update is not implemented |
| Queue Notification | Stage an email or in-app notification for delivery without blocking the calling business process | PKG_NOTIFICATION | Notifications | ✅ Confirmed |
| Send Queued Notifications | Process the pending notification queue in batches, sending emails via the internal SMTP server | PKG_NOTIFICATION | Notifications | ✅ Confirmed |
| Retry Failed Notifications | Reset failed notifications back to pending if they have not yet reached the retry limit | PKG_NOTIFICATION | Notifications | ✅ Confirmed |
| Cancel Notification | Prevent a queued notification from being sent | PKG_NOTIFICATION | Notifications | ✅ Confirmed |
| Headcount Reporting | Produce a breakdown of active employees by department, location, type, gender, and average tenure | PKG_REPORTING | Reporting & Integration | ✅ Confirmed |
| Compensation Reporting | Show salary ranges, averages, medians, and compa-ratios by department and grade | PKG_REPORTING | Reporting & Integration | ✅ Confirmed |
| Turnover Reporting | Measure voluntary and involuntary departures and turnover percentage by department over a date range | PKG_REPORTING | Reporting & Integration | ✅ Confirmed |
| New Hire Reporting | List all employees hired within a date range with their job, department, and starting salary | PKG_REPORTING | Reporting & Integration | ✅ Confirmed |
| Leave Utilisation Reporting | Show average leave entitlement, usage, and utilisation percentage by department and leave type | PKG_REPORTING | Reporting & Integration | ✅ Confirmed |
| Payroll Summary Reporting | Summarise total gross pay, taxes, deductions, and net pay by department for a pay period | PKG_REPORTING | Reporting & Integration | ✅ Confirmed |
| EEO Compliance Reporting | Report the gender breakdown of the workforce by EEO job category | PKG_REPORTING | Reporting & Integration | ✅ Confirmed |
| Generate General Ledger Feed | Produce a pipe-delimited journal file for import into Oracle Financials, mapping payroll costs and liabilities to GL account codes | PKG_INTEGRATION | Reporting & Integration | ✅ Confirmed |
| Export Benefits Enrolment Feed | Produce a fixed-width file of active employees and their dependents in ADP vendor format for benefits administration | PKG_INTEGRATION | Reporting & Integration | ✅ Confirmed |
| Import Time and Attendance | Read a CSV file of employee hours from the time-and-attendance system | PKG_INTEGRATION | Reporting & Integration | ⚠️ Corrected — file reading scaffolding exists but actual data import is a TODO; not functional |
| Synchronise Organisation Structure | Sync the reporting structure with the corporate directory (LDAP/Active Directory) | PKG_INTEGRATION | Reporting & Integration | ⚠️ Corrected — placeholder only; not implemented |
| Log System Errors and Events | Record all errors and informational events to the audit log without ever blocking the calling operation | PKG_AUDIT, PKG_COMMON | Cross-Cutting | ✅ Confirmed |
| View Change History | Retrieve the full audit trail for any record in any table, optionally filtered by date range | PKG_AUDIT | Cross-Cutting | ✅ Confirmed |
| Manage System Configuration | Read and update system-wide settings such as company name, pay frequency, and SMTP host | PKG_COMMON | Cross-Cutting | ✅ Confirmed |

### [EDGE-CASE-FOUND] Capability Corrections from Pass 2

The following capabilities were marked ✅ Confirmed in Pass 1 but second-pass code tracing revealed implementation defects that change their functional status:

| Capability | Pass 1 Status | Pass 2 Correction |
|---|---|---|
| Rehire Employee | ✅ Confirmed | ⚠️ Non-functional — TRG_EMP_BEFORE_UPDATE raises error -20503 whenever OLD status = TERMINATED and NEW status = ACTIVE. PKG_EMPLOYEE.rehire_employee executes exactly that UPDATE. The procedure cannot succeed without hitting the trigger. The capability exists in code but cannot execute. Business stakeholders must be told the rehire function does not work. |
| Expire Carried-Over Leave | ✅ Confirmed | ⚠️ Corrected — expire_carryover reduces the ADJUSTMENT column rather than OPENING_BALANCE. For employees who have already used some carried-over days, this can produce confusing negative ADJUSTMENT values. Functionally the balance maths resolve correctly but the column semantics are misleading and will confuse direct-table reporting. |
| Submit Manager Review | ✅ Confirmed | ⚠️ Corrected — submit_manager_review contains no status pre-check before overwriting the review. A manager can call this function against a review in any status (NOT_STARTED, COMPLETED, ACKNOWLEDGED) and the rating and assessment will be silently overwritten. The status guard described in the process flow is assumed business intent, not enforced code. |

---

## OUTPUT 2 — Business Process Flows

### Process: Onboard New Employee
**Domain:** Employee Management
**Trigger:** HR administrator or hiring manager initiates a new hire record
**Initiating Actor:** HR Administrator / Hiring Manager

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | HR enters the new employee's first name, last name, hire date, department, job title, employment type, and optionally salary, email, manager, and location | First name and last name are both required | System rejects the record and displays an error if either name is missing |
| 2 | System confirms the selected department is active | Department must exist with active status | System rejects with "Invalid or inactive department" |
| 3 | System confirms the selected job title is active | Job title must exist with active status | System rejects with "Invalid or inactive job" |
| 4 | System confirms the assigned manager is an active employee, if provided | Manager must have active employment status | System rejects with "Invalid or inactive manager" |
| 5 | System checks that the proposed manager does not create a circular reporting chain | No employee may report to someone who already reports to them, checked up to 15 levels | System rejects with "Circular reporting chain detected" |
| 6 | System checks that the proposed salary falls within the grade band for the job title, if a salary is provided | Salary range check is advisory only | System logs a warning but allows the hire to proceed; manager approval is assumed to have been given |
| 7 | System assigns a unique employee number in the format EMP-NNNNNN (6-digit, zero-padded) | Employee number must not already exist | On duplicate, system rejects with "Duplicate employee number — please retry" |
| 8 | System creates the employee record with status ACTIVE, active flag set to Yes, names stored in uppercase, and email stored in lowercase | — | — |
| 9 | If a salary was provided, system creates the employee's first salary record effective from the hire date | — | — |
| 10 | System writes a HIRE entry to the employment history log | — | History log failure never blocks the hire (runs in its own transaction) |
| 11 | System records the hire action in the audit trail | — | Audit failure never blocks the hire |
| 12 | System sends a welcome email to the new employee with their employee number | — | Notification failure never blocks the hire |
| 13 | If a manager was assigned, system notifies the manager that a new direct report has been added, including the hire date | Manager must be assigned | Skipped if no manager |

**Terminal outcomes:** Employee created with ACTIVE status; hire recorded in history and audit trail; welcome notifications sent
**Cross-domain handoffs:** 🔗 Step 9 calls Payroll domain to create salary record; 🔗 Steps 10–13 call Audit and Notification domains
**Rule candidates identified:** 📌 Hire date enforced at max 90 days in the future by the form; 📌 Hire date enforced at max 180 days by the database trigger — these limits conflict (see DISC-001)

---

### Process: Transfer Employee to New Department
**Domain:** Employee Management
**Trigger:** HR Administrator initiates a department transfer
**Initiating Actor:** HR Administrator

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | System locks the employee's record to prevent simultaneous edits | Record must not be locked by another user | If locked, system immediately returns "unable to lock record — please retry" (NOWAIT) |
| 2 | System confirms the employee is currently active | Employee must have ACTIVE employment status | System rejects with "Cannot transfer non-active employee" |
| 3 | System confirms the new department is active | — | System rejects with "Invalid or inactive department" |
| 4 | If a new manager is specified, system validates the manager is active and the assignment would not create a circular chain | — | System rejects with "Invalid or inactive manager" or "Circular reporting chain detected" |
| 5 | System updates the employee's department, job (defaults to current if not changed), location (defaults to current if not changed), and manager | — | — |
| 6 | System writes a TRANSFER entry to the employment history log recording the old and new department, job, manager, and location | — | — |
| 7 | System records the update in the audit trail | — | — |

**Terminal outcomes:** Employee assigned to new department; prior assignment recorded in history
**Cross-domain handoffs:** 🔗 Audit domain called at step 7

---

### Process: Promote Employee
**Domain:** Employee Management
**Trigger:** HR Administrator initiates a promotion
**Initiating Actor:** HR Administrator

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | HR provides the new job title and new salary, with an effective date | — | — |
| 2 | System retrieves the employee's current job title and current salary for comparison | If no current salary record exists, prior salary is treated as zero for percentage calculation | — |
| 3 | System updates the employee's job title | — | — |
| 4 | System creates a new salary record effective from the promotion date, closing the prior salary record | New salary must be greater than zero | System rejects with "Salary must be positive" |
| 5 | System calculates the salary change as a percentage: ((new salary − old salary) / old salary) × 100, rounded to 2 decimal places | Only calculated when prior salary > 0 | Percentage is left blank if prior salary was zero |
| 6 | System writes a PROMOTION entry to the employment history log recording old and new job and salary | — | — |
| 7 | System records the update in the audit trail | — | — |

**Terminal outcomes:** Employee's job title and salary updated; change recorded with percentage
**Cross-domain handoffs:** 🔗 Payroll domain called at step 4 to create salary record
**Rule candidates identified:** 📌 No active-status check before promotion — employee can be promoted while suspended or on leave (contrast with transfer, which requires ACTIVE status; see DISC-005)

---

### Process: Terminate Employee
**Domain:** Employee Management
**Trigger:** HR Administrator initiates termination
**Initiating Actor:** HR Administrator

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | System locks the employee's record | — | — |
| 2 | System confirms the employee is not already terminated | Employee must not already have TERMINATED status | System rejects with "Employee is already terminated" |
| 3 | System finds all of the employee's leave requests that are currently awaiting approval | — | — |
| 4 | System automatically cancels all pending leave requests with the reason "Auto-cancelled due to termination" | Only requests in PENDING status are cancelled | — |
| 5 | System sets the employee's status to TERMINATED, sets the active flag to No, and records the termination date and reason | — | — |
| 6 | System closes all active salary records by setting their end date to the termination date | — | — |
| 7 | System closes all active pay elements by setting their end date to the termination date | — | — |
| 8 | System writes a TERMINATION entry to the employment history log | — | — |
| 9 | System records the update in the audit trail | — | — |
| 10 | System notifies the employee's manager that the employee has been terminated, including the effective date | Manager must be assigned | Skipped if no manager |
| 11 | 〰️ ASSUMED — Benefits COBRA notification: system should trigger COBRA continuation notice to the departing employee | Not yet coded; marked as TODO in the system | Integration absent |
| 12 | 〰️ ASSUMED — System access revocation: system should revoke the employee's IT access | Not yet coded; marked as TODO | Integration absent |
| 13 | 〰️ ASSUMED — Final pay calculation: system should calculate and process any outstanding pay | Not yet coded; marked as TODO | Integration absent |

**Terminal outcomes:** Employee status TERMINATED; salary and pay elements closed; pending leave cancelled; manager notified
**Cross-domain handoffs:** 🔗 Audit and Notification domains called at steps 9–10

> **[EDGE-CASE-FOUND] Termination leave-balance leak:** Step 4 cancels PENDING leave requests by writing directly to LEAVE_REQUESTS (bypassing PKG_LEAVE), so the LEAVE_BALANCES.PENDING column is never decremented. After termination, the employee's leave balance record shows a phantom pending amount. Any report reading the balance formula (OPENING + ACCRUED − USED + ADJUSTMENT − PENDING) will understate available balance for that record indefinitely.
>
> **[EDGE-CASE-FOUND] Approved future leave not cancelled:** Only PENDING leave is auto-cancelled (step 4). APPROVED future leave that will never be taken remains in the system with STATUS = 'APPROVED' after the employee is terminated. This creates stale approved records and inflates leave utilisation numbers.

---

### Process: Rehire Employee
**Domain:** Employee Management
**Trigger:** HR Administrator initiates rehire of a previously terminated employee
**Initiating Actor:** HR Administrator

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | System confirms the new department is active | — | System rejects with "Invalid or inactive department" |
| 2 | System reactivates the employee, setting status back to ACTIVE and active flag to Yes | Employee must exist | System rejects with "Employee not found for rehire" |
| 3 | System overwrites the hire date with the rehire date and clears the termination date and reason | — | — |
| 4 | System assigns the new department and job title | — | — |
| 5 | System creates a new salary record effective from the rehire date | Salary must be greater than zero | System rejects with "Salary must be positive" |
| 6 | System writes a REHIRE entry to the employment history log | — | — |
| 7 | System records the update in the audit trail | — | — |

**Terminal outcomes:** Employee reactivated with new start date, department, job, and salary; history preserved

---

### Process: Run Monthly Payroll Calculation
**Domain:** Payroll
**Trigger:** Payroll administrator creates a payroll run for an open pay period
**Initiating Actor:** Payroll Administrator

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | Administrator selects an open pay period and creates a payroll run of type REGULAR | Pay period must be in OPEN status | System rejects with "Cannot create run for closed period" |
| 2 | System creates the run record with status PENDING and returns the run identifier | — | — |
| 3 | Administrator initiates the calculation | Run must be in PENDING status | Form prevents calculation if status is not PENDING |
| 4 | System changes run status to CALCULATING and begins processing employees | — | — |
| 5 | For each active employee, system calculates the period gross pay by dividing the annual salary by the number of pay periods in the year, rounded to 2 decimal places | Employee must have an active salary record for the period | If no salary found, employee is logged as an error; processing continues for remaining employees |
| 6 | System calculates and records federal income tax using 2024 IRS brackets, standard deduction, allowances, and any additional withholding from the employee's W-4 | If no W-4 on file, single filing status with zero allowances is assumed | — |
| 7 | System calculates and records state income tax using the flat rate for the employee's state | If state not recognised, 5.00% default rate is applied | — |
| 8 | System calculates and records Social Security tax at 6.2%, stopping once the employee's year-to-date earnings reach $168,600 | — | — |
| 9 | System calculates and records Medicare tax at 1.45% on all earnings, plus an additional 0.9% on the portion of year-to-date earnings that exceeds $200,000 | — | — |
| 10 | System calculates and records each active deduction and benefit for the employee, in priority order, using override amount if set, otherwise flat amount, otherwise percentage of gross | Element must be active and effective during the pay period dates | — |
| 11 | System commits to the database every 50 employees to manage memory | — | — |
| 12 | After all employees are processed, system updates the run with total gross, total deductions, total net, and employee count | — | — |
| 13 | If any employee had an error, run status is set to ERROR; otherwise CALCULATED | — | — |

**Terminal outcomes:** Run in CALCULATED or ERROR status with full pay detail lines; administrator can review errors before proceeding
**Cross-domain handoffs:** 🔗 Audit domain called for each salary record change
**Rule candidates identified:** 📌 Tax brackets hard-coded for 2024; TAX_BRACKETS table exists but is not used (see PP-12)

---

### Process: Approve and Finalise Payroll Run
**Domain:** Payroll
**Trigger:** Payroll manager reviews the calculated run and approves it
**Initiating Actor:** Payroll Manager

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | Payroll manager reviews the calculated totals and detail lines | Run must be in CALCULATED status | System rejects approval with "Cannot approve run in status: [current status]" |
| 2 | Manager with APPROVE permission on the Payroll module approves the run | Approver must have explicit Payroll Approve permission (grade-based) | Form blocks approval with "You do not have permission to approve payroll" |
| 3 | System records the approver's name and approval date on the run and changes status to APPROVED | — | — |
| 4 | 〰️ ASSUMED — Payment disbursement: system should send net pay to each employee's bank account or issue cheques | Not coded; no direct payment integration found | — |

**Terminal outcomes:** Run status APPROVED; payment disbursement not automated

---

### Process: Submit and Approve Leave Request
**Domain:** Leave Management
**Trigger:** Employee submits a request for time off
**Initiating Actor:** Employee

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | Employee selects a leave type, start date, end date, and optionally marks the request as a half-day and provides a reason | Employee must be ACTIVE; leave type must be active | System rejects if employee is not found or inactive |
| 2 | System checks whether the employee has met the minimum tenure requirement for the leave type | Tenure in days since hire must be at least the leave type's minimum | System rejects with "Minimum tenure of [N] days not met" |
| 3 | System confirms the start date is on or before the end date | — | System rejects with "Start date must be before or equal to end date" |
| 4 | System confirms the request is not backdated by more than 5 calendar days | — | System rejects with "Cannot submit leave requests more than 5 days in the past" |
| 5 | For a full-day request, system counts the number of business days (weekdays excluding public holidays) in the range; for a half-day, system records exactly 0.5 days | At least 1 business day must fall in the range | System rejects with "No business days in the selected range" |
| 6 | System checks that the requested dates do not overlap with any other PENDING or APPROVED leave request for the same employee | — | System rejects with "Leave request overlaps with an existing request" |
| 7 | For accrual-based leave types, system checks the employee's available balance | Available balance must cover the requested days | System rejects with "Insufficient leave balance. Available: [n], Requested: [n]" |
| 8 | System creates the leave request record | — | — |
| 9 | System increases the employee's PENDING leave balance by the number of requested days | — | — |
| 10a | If the leave type requires approval: system sets status to PENDING and notifies the assigned approver (the employee's manager) | Manager must be assigned for notification to be sent | Notification skipped if no manager; request still created |
| 10b | If the leave type does not require approval (e.g. Jury Duty, Bereavement): system immediately approves the request and updates the balance | — | — |
| 11 | Manager reviews the request in their pending approvals list | — | — |
| 12 | Manager approves: system changes status to APPROVED, decrements PENDING balance, increments USED balance, and notifies the employee | Request must be in PENDING status | System rejects with "Cannot approve request in status: [current status]" |
| OR | Manager rejects: system changes status to REJECTED, decrements PENDING balance (restoring it), and notifies the employee with the rejection reason | Request must be in PENDING status | — |

**Terminal outcomes:** Leave request in APPROVED or REJECTED status; balances updated accordingly
**Cross-domain handoffs:** 🔗 Notification domain called at steps 10 and 12

---

### Process: Year-End Leave Carryover
**Domain:** Leave Management
**Trigger:** Year-end batch job run by HR or automated scheduler
**Initiating Actor:** System Scheduler / HR Administrator

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | System calculates each employee's remaining balance for the current year for every leave type | Only leave types with a positive remaining balance are processed | — |
| 2 | System determines the carryover amount: the full remaining balance, capped at the leave type's maximum carryover allowance | Maximum carryover per type: PTO = 5 days; SICK = 10 days; COMP = 0 days; FMLA = 0 days | If maximum carryover is zero, nothing is carried forward |
| 3 | System initialises the employee's next-year balance record if it does not already exist | — | — |
| 4 | System sets the carried-over amount as the next year's opening balance and records the carryover expiry date | Expiry = January 1 of next year plus the leave type's expiry period in months (PTO: 3 months = April 1) | If no expiry is defined, carried-over leave does not expire |
| 5 | At a scheduled date each year, the expiry job removes any carried-over leave that has passed its expiry date by reducing the adjustment balance | — | — |

**Terminal outcomes:** Next year's opening balance populated; expired carryover removed on schedule

---

### [EDGE-CASE-FOUND] Process: Monthly Leave Accrual (Batch)
**Domain:** Leave Management
**Trigger:** Scheduled batch job, typically on the 1st of each month
**Initiating Actor:** System (DBMS_SCHEDULER)

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | System selects all active employees (EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y') | | |
| 2 | For each employee, for each monthly-frequency accrual leave type, check if employee meets minimum tenure | Days since hire must be >= leave type's MIN_TENURE_DAYS | Employee is skipped for this leave type if tenure not met |
| 3 | Check current leave balance against maximum allowed | If adding the accrual rate would exceed MAX_BALANCE, accrue only enough to reach the cap | 0 days accrued if already at maximum |
| 4 | Increment the ACCRUED field in leave balances by the accrual amount | If no balance record exists for this year, create one first | |
| 5 | Write an accrual log entry | | |
| 6 | Commit every 100 employees processed | | Partial commit means failure leaves some employees accrued and others not in the same batch run |

**Terminal outcomes:** All qualifying employees have leave balances incremented; accrual log entries created
**Rule candidates identified:** 📌 PTO accrues 1.25 days/month (max 20); SICK accrues 0.833 days/month (max 10); COMP and FMLA do not accrue; accrual only for employees meeting minimum tenure

---

### Process: Run Annual Performance Review Cycle
**Domain:** Performance Management
**Trigger:** HR creates a new review cycle for the year
**Initiating Actor:** HR Administrator

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | HR creates a review cycle with a name, year, start date, end date, and self-review and manager-review due dates | — | — |
| 2 | System creates the cycle in DRAFT status | — | — |
| 3 | HR opens the cycle when ready to begin | Cycle must be in DRAFT status | System rejects with "Cannot open cycle — must be in DRAFT status" |
| 4 | System automatically generates a review record for every active employee who has a manager assigned | Employees without a manager do not receive a review | Duplicate reviews are silently skipped |
| 5 | Each employee is notified by email that their annual performance review has been initiated | — | — |
| 6 | Employee writes and submits their self-assessment | Review must be in NOT_STARTED or SELF_REVIEW status | System rejects with "Review not found or not in correct status" |
| 7 | System advances review status to MANAGER_REVIEW and notifies the manager that the self-assessment is ready | — | — |
| 8 | Manager reviews the self-assessment, writes their own assessment, and assigns an overall rating between 1.0 and 5.0 | Rating must be between 1.0 and 5.0 inclusive | System rejects with "Rating must be between 1.0 and 5.0" |
| 9 | System applies the rating label: 4.5–5.0 = Exceptional; 3.5–4.4 = Exceeds Expectations; 2.5–3.4 = Meets Expectations; 1.5–2.4 = Needs Improvement; 1.0–1.4 = Unsatisfactory | — | — |
| 10 | System advances review status to COMPLETED and notifies the employee that their review is ready | — | — |
| 11 | Employee reads the review and acknowledges it, optionally adding comments | Review must be in COMPLETED status | — |
| 12 | System advances review status to ACKNOWLEDGED | — | — |
| 13 | HR closes the cycle when all reviews are complete | — | — |

**Terminal outcomes:** All reviews in ACKNOWLEDGED status; cycle CLOSED
**Cross-domain handoffs:** 🔗 Notification domain called at steps 5, 7, 10

> **[EDGE-CASE-FOUND] SELF_REVIEW status unreachable:** Step 6 allows self-assessment submission from NOT_STARTED or SELF_REVIEW status. However, no procedure anywhere in PKG_PERFORMANCE or any trigger sets STATUS = 'SELF_REVIEW'. All reviews begin in NOT_STARTED and skip directly to MANAGER_REVIEW. The SELF_REVIEW status is defined in the schema DDL but is functionally dead.
>
> **[EDGE-CASE-FOUND] Manager review has no status pre-check:** submit_manager_review does not validate the review's current status before overwriting the rating and assessment. A manager can call this against an ACKNOWLEDGED review and silently overwrite a completed, signed-off record. There is no guard preventing this at the code level.
>
> **[EDGE-CASE-FOUND] CEO and top-hierarchy employees excluded from reviews:** generate_reviews_for_cycle only creates review records for employees who have MANAGER_ID IS NOT NULL. Any employee at the top of any reporting chain (not just the CEO) receives no review record regardless of how the cycle is configured.

---

### Process: User Login and Session Management
**Domain:** Security & Access
**Trigger:** User navigates to the HRMS login screen and enters credentials
**Initiating Actor:** HRMS User

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | User enters their email address and password on the login screen | Both fields are required | Form displays "Please enter username and password" |
| 2 | System looks up the employee whose email address matches the entered username (case-insensitive) | Employee must exist and have ACTIVE employment status | System returns generic "Invalid username or password" — does not distinguish between wrong email, wrong password, or inactive account |
| 3 | 〰️ ASSUMED — System verifies the password against the stored MD5 hash | Password verification code is referenced but not fully implemented in the provided source; USER_CREDENTIALS table is referenced but password check is absent | Login may proceed without password verification in current state — security risk |
| 4 | System creates a session record with a unique session identifier and records the login time and IP address | — | — |
| 5 | System sets the session context for the user's subsequent operations | — | — |
| 6 | System records the login in the audit trail | — | — |
| 7 | Application opens the main menu, disabling modules the user does not have permission to access | — | — |
| 8 | On each subsequent screen open, system checks whether the session is still active and has not exceeded 30 minutes since login | Session timeout is based on the original login time, not the most recent activity | Session marked as EXPIRED; user redirected to login |
| 9 | When user logs out, system records the logout time and closes the session | — | — |

**Terminal outcomes:** User authenticated with an active session; or rejected with a generic error message

---

### Process: Notification Delivery
**Domain:** Notifications
**Trigger:** Any business operation that requires communication (hire, termination, leave approval, review assignment, etc.)
**Initiating Actor:** System (triggered by other processes)

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | Calling process requests a notification, providing the recipient (by employee ID or direct email), subject, body, and optional priority | — | — |
| 2 | System resolves the recipient's email address from the employee record if not provided directly | — | If employee not found, email is null; notification is queued without a recipient |
| 3 | System queues the notification with PENDING status; this step is isolated in its own transaction so a notification failure never blocks the calling business process | — | Failure is silently swallowed and logged |
| 4 | Every 5 minutes, the DBMS Scheduler job calls the queue processor | — | — |
| 5 | Queue processor picks the next batch of up to 50 PENDING email notifications, in priority order (lowest number first), then oldest first | Notification must have a non-null email address | Skipped if no email address |
| 6 | For each notification, system opens an SMTP connection to the internal mail server (smtp.internal.company.com port 25), sends the email, and closes the connection | — | If sending fails: status set to FAILED, retry count incremented, error message stored |
| 7 | If the retry count is below 3, a separate retry job resets FAILED notifications back to PENDING | Retry count must be less than 3 | After 3 failures, notification remains in FAILED status permanently |

**Terminal outcomes:** Notification in SENT status; or FAILED with error message after 3 attempts

---

### Process: Generate GL Journal Feed
**Domain:** Reporting & Integration
**Trigger:** Payroll run approved; batch scheduler initiates GL feed generation
**Initiating Actor:** System Scheduler

| Step | Description | Condition (if any) | Exception Path (if any) |
|---|---|---|---|
| 1 | System reads all non-error payroll detail lines for the run, grouped by cost centre and GL account code | Element must have a GL account code assigned | Elements without GL account codes are excluded from the feed |
| 2 | System creates a pipe-delimited flat file in the GL_FEED_OUT Oracle directory | — | File creation failure logged and raised |
| 3 | System writes a header record: H\|HRMS_PAYROLL\|[date]\|[run_id] | — | — |
| 4 | For each earning element: system writes a detail record with the amount as a debit (expense accounts) | — | — |
| 5 | For each deduction, tax, or benefit: system writes a detail record with the amount as a credit (liability accounts) | — | — |
| 6 | System writes a trailer record with the total count of detail lines | — | — |
| 7 | 〰️ ASSUMED — The GL system picks up the file via a scheduled file transfer or batch import | File transfer mechanism not implemented in HRMS; DBA must configure the Oracle directory and file pickup | — |

**Terminal outcomes:** Pipe-delimited journal file produced in GL_FEED_OUT directory; awaits import by Oracle Financials

---

## OUTPUT 3 — Business Rules Catalog

| ID | Rule | Domain | Type | Severity | Confidence | Source |
|---|---|---|---|---|---|---|
| BR-01 | An employee's first name and last name are both required and cannot be blank | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.create_employee, PKG_VALIDATION.validate_required_fields |
| BR-02 | An employee's hire date is required and cannot be blank | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_VALIDATION.validate_required_fields, TRG_EMP_BEFORE_INSERT |
| BR-03 | An employee's department is required and cannot be blank | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_VALIDATION.validate_required_fields |
| BR-04 | An employee's job title is required and cannot be blank | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_VALIDATION.validate_required_fields |
| BR-05 | The department assigned to an employee must exist and must be active | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.validate_dept |
| BR-06 | The manager assigned to an employee must be currently active (employment status = ACTIVE) | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.validate_manager |
| BR-07 | An employee may not be assigned a manager if doing so would create a circular reporting chain. The chain is checked up to 15 levels deep | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.validate_manager |
| BR-08 | The job title assigned to an employee must exist and must be active | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.create_employee |
| BR-09 | An employee's proposed salary is checked against the grade band. If outside the band, the hire may still proceed — the check is advisory, not blocking. Manager approval is assumed | Employee Management | Soft Constraint | Medium | ✅ HIGH | PKG_EMPLOYEE.create_employee step 5 |
| BR-10 | Employee first name and last name are stored in uppercase. Email is stored in lowercase | Employee Management | Hard Constraint | Low | ✅ HIGH | PKG_EMPLOYEE.create_employee INSERT statement |
| BR-11 | Employee numbers follow the format EMP-NNNNNN (the prefix "EMP-" followed by exactly 6 zero-padded digits) | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.generate_emp_number, PKG_VALIDATION.validate_emp_number_format |
| BR-12 | When an employee is created, their employment status defaults to ACTIVE and their active flag defaults to Yes | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.create_employee, TRG_EMP_BEFORE_INSERT |
| BR-13 | If no location is specified at hire, the location defaults to the location of the assigned department | Employee Management | Soft Constraint | Low | ✅ HIGH | PKG_EMPLOYEE.create_employee step 6 |
| BR-14 | An employee's hire date may not be set more than 90 days in the future (enforced by the employee maintenance screen) | Employee Management | Hard Constraint | High | ✅ HIGH | HRMS_EMPLOYEE.xml WHEN-VALIDATE-ITEM |
| BR-15 | An employee's hire date may not be set more than 180 days in the future (enforced by the database trigger) | Employee Management | Hard Constraint | High | ✅ HIGH | TRG_EMP_BEFORE_INSERT |
| BR-16 | An email address must be unique across all active employees (case-insensitive) | Employee Management | Hard Constraint | High | ✅ HIGH | TRG_EMP_BEFORE_INSERT |
| BR-17 | A terminated employee cannot be directly reactivated to ACTIVE via a simple record update. The rehire process must be used | Employee Management | Hard Constraint | High | ✅ HIGH | TRG_EMP_BEFORE_UPDATE |
| BR-18 | Physical deletion of employee records is prohibited. All departures must go through termination or setting the active flag to No | Employee Management | Hard Constraint | High | ✅ HIGH | TRG_EMP_INSTEAD_OF_DELETE |
| BR-19 | Only employees with ACTIVE employment status can be transferred | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.transfer_employee step 2 |
| BR-20 | On transfer, job title defaults to the current job if not explicitly changed | Employee Management | Soft Constraint | Low | ✅ HIGH | PKG_EMPLOYEE.transfer_employee step 4 |
| BR-21 | On transfer, location defaults to the current location if not explicitly changed | Employee Management | Soft Constraint | Low | ✅ HIGH | PKG_EMPLOYEE.transfer_employee step 5 |
| BR-22 | On termination, all PENDING leave requests are auto-cancelled with reason "Auto-cancelled due to termination" | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.terminate_employee step 4 |
| BR-23 | On termination, all active salary records are end-dated to the termination date | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.terminate_employee step 6 |
| BR-24 | On termination, all active pay elements are end-dated to the termination date | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.terminate_employee step 7 |
| BR-25 | On rehire, the hire date is overwritten with the rehire date. Termination date and reason are cleared | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.rehire_employee step 2 |
| BR-26 | The org chart includes only ACTIVE employees, defaults to max depth 10, absolute max depth 15 | Employee Management | Hard Constraint | Low | ✅ HIGH | PKG_EMPLOYEE.get_org_chart |
| BR-27 | Tenure in years = MONTHS_BETWEEN(end date, hire date) / 12, rounded to 1 decimal. End date is today for active employees, termination date for terminated | Employee Management | Threshold | Low | ✅ HIGH | PKG_EMPLOYEE.get_tenure_years |
| BR-28 | Headcount excludes employees hired after the as-of date and employees terminated on or before the as-of date | Employee Management | Hard Constraint | Medium | ✅ HIGH | PKG_EMPLOYEE.get_headcount_by_dept |
| BR-29 | Valid employee: first name not null, last name not null, hire date not null, and if ACTIVE then active flag must be Yes | Employee Management | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.validate_employee |
| BR-30 | Employee salary must be greater than zero | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_salary_record |
| BR-31 | All salaries are recorded as annual amounts (SALARY_BASIS = ANNUAL) | Payroll | Hard Constraint | Low | ✅ HIGH | PKG_PAYROLL.create_salary_record |
| BR-32 | When a new salary record is created, the previous active record is closed by setting its end date to new effective date minus 1 day | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_salary_record step 2 |
| BR-33 | Default currency = USD; default pay frequency = MONTHLY | Payroll | Soft Constraint | Low | ✅ HIGH | PKG_PAYROLL.create_salary_record defaults |
| BR-34 | Monthly pay date = last day of the month, moved to the preceding Friday if it falls on a weekend | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_pay_periods MONTHLY |
| BR-35 | Biweekly periods are 14 days ending on Friday; pay date is 5 days after the period end date | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_pay_periods BIWEEKLY |
| BR-36 | A CLOSED pay period cannot be closed again | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.close_pay_period |
| BR-37 | A payroll run cannot be created for a closed pay period | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_payroll_run |
| BR-38 | Only employees with ACTIVE status and active flag Yes are included in payroll calculation | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_payroll |
| BR-39 | An error in one employee's calculation does not stop other employees. The error is recorded and processing continues | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_payroll EXCEPTION block |
| BR-40 | Period gross = ROUND(annual salary / periods per year, 2). Periods: WEEKLY=52, BIWEEKLY=26, SEMIMONTHLY=24, MONTHLY=12 | Payroll | Threshold | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-41 | If no active salary record exists for the pay period, the employee is flagged as an error | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-42 | If no W-4 is on file, federal tax defaults to single filing status, zero allowances, zero additional withholding | Payroll | Soft Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-43 | Federal tax: annualise income, subtract standard deduction ($14,600 single/MFS or $29,200 MFJ) and allowances ($4,300 each), apply bracket, de-annualise, add additional withholding | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_federal_tax |
| BR-44 | 2024 Federal brackets Single/MFS: 10% up to $11,600; 12% $11,601–$47,150; 22% $47,151–$100,525; 24% $100,526–$191,950; 32% $191,951–$243,725; 35% $243,726–$609,350; 37% above $609,350 | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_federal_tax |
| BR-45 | 2024 Federal brackets MFJ: 10% up to $23,200; 12% $23,201–$94,300; 22% $94,301–$201,050; 24% $201,051–$383,900; 32% $383,901–$487,450; 35% $487,451–$731,200; 37% above $731,200 | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_federal_tax |
| BR-46 | State flat rates: CA 7.25%; NY 6.85%; TX 0%; FL 0%; WA 0%; IL 4.95%; PA 3.07%; OH 4.00%; NJ 6.37%; MA 5.00%; all others default 5.00% | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_state_tax |
| BR-47 | Social Security (FICA): 6.2% of gross pay; stops once year-to-date gross reaches $168,600 (2024 wage base) | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_fica |
| BR-48 | Medicare: 1.45% on all gross pay (no cap); additional 0.9% on the portion of year-to-date gross that exceeds $200,000 | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_medicare |
| BR-49 | Deductions applied in priority order: override amount first, then flat amount, then percentage of period gross | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay step 15 |
| BR-50 | Only deductions active during the pay period dates are included | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay WHERE clause |
| BR-51 | Only CALCULATED runs can be approved | Payroll | Approval Gate | High | ✅ HIGH | PKG_PAYROLL.approve_payroll |
| BR-52 | Approving a payroll run requires the APPROVE action permission on the Payroll module | Payroll | Approval Gate | High | ✅ HIGH | HRMS_PAYROLL.xml BTN_APPROVE |
| BR-53 | A payroll run can be reversed from any status; all detail lines are also reversed. Reversal reason is accepted as a parameter but not stored | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.reverse_payroll |
| BR-54 | Year-to-date earnings count only EARNING elements with CALCULATED status; determined by period start date year | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.get_ytd_earnings |
| BR-55 | Payslip YTD gross and YTD net are hard-coded to zero (not yet implemented) | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.get_payslip |
| BR-56 | Default pay element amounts: 401k 6% pre-tax; Medical $250 pre-tax; Dental $45 pre-tax; Vision $15 pre-tax; Life Insurance $25 not pre-tax; HSA $150 pre-tax | Payroll | Soft Constraint | High | ✅ HIGH | seed data PAY_ELEMENTS |
| BR-57 | Leave requests may only be submitted by ACTIVE employees | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-58 | The leave type must be active | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-59 | Compensatory leave requires a minimum of 90 days of employment | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request; LEAVE_TYPES seed |
| BR-60 | FMLA requires a minimum of 365 days of employment (1 year) | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request; LEAVE_TYPES seed |
| BR-61 | Leave start date must be on or before the end date | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-62 | Leave requests may be backdated by at most 5 calendar days | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-63 | A half-day leave request counts as exactly 0.5 days | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-64 | At least 1 business day must fall in the requested date range | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-65 | A request cannot overlap with any PENDING or APPROVED request for the same employee | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.check_leave_overlap |
| BR-66 | For accrual-based leave types, available balance must cover the requested days | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-67 | Available balance = Opening Balance + Accrued − Used + Adjustment − Pending | Leave Management | Threshold | High | ✅ HIGH | PKG_LEAVE.get_leave_balance; LEAVE_BALANCES virtual column |
| BR-68 | On submission, the PENDING balance is immediately increased by the requested days | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-69 | Leave types that do not require approval (Jury Duty, Bereavement) are auto-approved at submission | Leave Management | Approval Gate | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-70 | Only PENDING requests can be approved or rejected | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.approve_leave_request; reject_leave_request |
| BR-71 | On approval, PENDING balance is decremented and USED balance is incremented | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.approve_leave_request |
| BR-72 | On rejection, PENDING balance is released (decremented) | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.reject_leave_request |
| BR-73 | Only PENDING or APPROVED requests can be cancelled | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.cancel_leave_request |
| BR-74 | Cancelling a PENDING request decrements PENDING balance; cancelling an APPROVED request decrements USED balance | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.cancel_leave_request |
| BR-75 | Business days are weekdays excluding public holidays (global and location-specific) from the HOLIDAYS table where active flag = Yes | Leave Management | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.calculate_business_days; PKG_VALIDATION.is_business_day |
| BR-76 | Monthly accrual: PTO 1.25 days/month; SICK 0.833 days/month; minimum tenure must be met | Leave Management | Threshold | High | ✅ HIGH | PKG_LEAVE.run_monthly_accrual; LEAVE_TYPES seed |
| BR-77 | Leave accrual is capped: PTO max balance 20 days; SICK max balance 10 days | Leave Management | Threshold | High | ✅ HIGH | PKG_LEAVE.run_monthly_accrual; LEAVE_TYPES seed |
| BR-78 | Year-end carryover maximums: PTO 5 days; SICK 10 days; COMP 0 days; FMLA 0 days | Leave Management | Threshold | High | ✅ HIGH | PKG_LEAVE.process_carryover; LEAVE_TYPES seed |
| BR-79 | PTO carry-over expires 3 months after the start of the new year (approx. April 1). SICK carry-over does not expire | Leave Management | SLA | High | ✅ HIGH | LEAVE_TYPES seed CARRYOVER_EXPIRY=3 months for PTO |
| BR-80 | A review cycle must be in DRAFT status to be opened | Performance Management | Approval Gate | High | ✅ HIGH | PKG_PERFORMANCE.open_review_cycle |
| BR-81 | New reviews are created with status NOT_STARTED and type ANNUAL | Performance Management | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.create_review |
| BR-82 | Self-assessment can be submitted when status is NOT_STARTED or SELF_REVIEW; advances to MANAGER_REVIEW | Performance Management | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.submit_self_assessment |
| BR-83 | Overall rating must be between 1.0 and 5.0 inclusive | Performance Management | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.submit_manager_review; CHK_RATING_RANGE |
| BR-84 | Rating labels: >=4.5 = Exceptional; >=3.5 = Exceeds Expectations; >=2.5 = Meets Expectations; >=1.5 = Needs Improvement; <1.5 = Unsatisfactory | Performance Management | Threshold | High | ✅ HIGH | PKG_PERFORMANCE.submit_manager_review |
| BR-85 | Manager review submission advances status to COMPLETED | Performance Management | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.submit_manager_review |
| BR-86 | Only COMPLETED reviews can be acknowledged; acknowledgement advances to ACKNOWLEDGED | Performance Management | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.acknowledge_review |
| BR-87 | Only active employees with a manager assigned receive a review when generating for a cycle | Performance Management | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.generate_reviews_for_cycle |
| BR-88 | Goal progress status auto-derives: 0% = unchanged; 1–99% = In Progress; 100% = Completed | Performance Management | Soft Constraint | High | ✅ HIGH | PKG_PERFORMANCE.update_goal_progress |
| BR-89 | A user session expires 30 minutes after login time (not after last activity) | Security & Access | SLA | High | ✅ HIGH | PKG_SECURITY.is_session_valid; SYSTEM_PARAMETERS SESSION_TIMEOUT_MIN=30 |
| BR-90 | Login uses employee email as username (case-insensitive). Only ACTIVE employees can log in | Security & Access | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.authenticate; HRMS_LOGIN.xml |
| BR-91 | Permissions: Grade 8+ = full access all modules; Grade 5–7 = VIEW all modules; any grade = CREATE+VIEW LEAVE and VIEW EMPLOYEE; all others = no access | Security & Access | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.has_permission |
| BR-92 | Payroll module requires VIEW permission to open; approving a run requires separate APPROVE permission | Security & Access | Approval Gate | High | ✅ HIGH | HRMS_PAYROLL.xml |
| BR-93 | Reports module requires VIEW permission. Leave and Performance have no permission gate beyond session validity | Security & Access | Hard Constraint | High | ✅ HIGH | HRMS_MENU.xml button triggers |
| BR-94 | Password complexity: minimum 8 characters; at least one uppercase letter; at least one digit | Security & Access | Compliance | High | ✅ HIGH | PKG_SECURITY.change_password |
| BR-95 | Notifications are queued asynchronously and never block or fail the calling operation | Notifications | Hard Constraint | High | ✅ HIGH | PKG_NOTIFICATION.send_notification AUTONOMOUS_TRANSACTION |
| BR-96 | Queue processor handles up to 50 notifications per run; ordered by priority (low number first) then oldest first | Notifications | Hard Constraint | High | ✅ HIGH | PKG_NOTIFICATION.process_queue |
| BR-97 | Failed notifications are retried up to 3 times. After 3 failures they remain in FAILED status permanently | Notifications | SLA | High | ✅ HIGH | PKG_NOTIFICATION.retry_failed |
| BR-98 | Only PENDING notifications can be cancelled | Notifications | Hard Constraint | High | ✅ HIGH | PKG_NOTIFICATION.cancel_notification |
| BR-99 | Default audit record retention is 365 days | Cross-Cutting | SLA | Medium | ✅ HIGH | PKG_AUDIT.purge_old_records |
| BR-100 | Audit logging uses autonomous transactions and never blocks the calling operation | Cross-Cutting | Hard Constraint | High | ✅ HIGH | PKG_AUDIT.log_action PRAGMA AUTONOMOUS_TRANSACTION |
| BR-101 | Parameters with EDITABLE_FLAG = No cannot be changed. The application version is non-editable | Cross-Cutting | Hard Constraint | High | ✅ HIGH | PKG_COMMON.set_param; SYSTEM_PARAMETERS seed |
| BR-102 | Fiscal year starts October 1. October–December dates belong to fiscal year = calendar year + 1 | Cross-Cutting | Hard Constraint | High | ✅ HIGH | PKG_COMMON.get_fiscal_year |
| BR-103 | Fiscal quarters: Q1 = Oct–Dec; Q2 = Jan–Mar; Q3 = Apr–Jun; Q4 = Jul–Sep | Cross-Cutting | Hard Constraint | High | ✅ HIGH | PKG_COMMON.get_fiscal_quarter |
| BR-104 | Grade salary bands: Grade 1 $35k–$55k; Grade 2 $45k–$70k; Grade 3 $60k–$90k; Grade 4 $80k–$120k; Grade 5 $95k–$145k; Grade 6 $110k–$170k; Grade 7 $130k–$200k; Grade 8 $160k–$250k; Grade 9 $200k–$350k; Grade 10 $300k–$600k | Employee Management, Payroll | Threshold | High | ✅ HIGH | JOB_GRADES seed data |
| BR-105 | Max salary for a grade must be >= min salary | Employee Management | Hard Constraint | High | ✅ HIGH | JOB_GRADES.CHK_SALARY_RANGE |
| BR-106 | GL feed: earnings = debits to expense accounts; deductions/taxes/benefits = credits to liability accounts; only elements with a GL account code are included | Reporting & Integration | Hard Constraint | High | ✅ HIGH | PKG_INTEGRATION.generate_gl_journal |
| BR-107 | Benefits feed: active employees only; one row per active dependent (LEFT JOIN); employees without dependents appear as one row | Reporting & Integration | Hard Constraint | High | ✅ HIGH | PKG_INTEGRATION.export_benefits_feed |
| BR-108 | All salary record changes (insert, update, delete) are captured in the audit trail in JSON format | Cross-Cutting | Compliance | High | ✅ HIGH | TRG_SALARY_AUDIT |
| BR-109 | All leave request status changes are captured in the audit trail | Cross-Cutting | Compliance | High | ✅ HIGH | TRG_LEAVE_REQUEST_AUDIT |
| BR-110 | All department record changes are captured in the audit trail | Cross-Cutting | Compliance | High | ✅ HIGH | TRG_DEPARTMENT_AUDIT |
| BR-111 | Compa-ratio = (actual salary / grade midpoint) × 100 rounded to 1 decimal; midpoint = (min + max) / 2 | Payroll, Reporting | Threshold | High | ✅ HIGH | VW_EMPLOYEE_COMPENSATION; PKG_REPORTING.compensation_summary |
| BR-112 | Turnover % = (terminations in period / employees hired on or before period end date) × 100 | Reporting | Threshold | High | ✅ HIGH | PKG_REPORTING.turnover_report |
| BR-113 | Voluntary termination = TERMINATION_REASON = 'VOLUNTARY'. All other reasons (including null) = involuntary | Reporting | Hard Constraint | High | ✅ HIGH | PKG_REPORTING.turnover_report |
| BR-114 | Leave utilisation % = (average days used / average days entitled) × 100; entitled = opening balance + accrued | Reporting | Threshold | High | ✅ HIGH | PKG_REPORTING.leave_utilization_report |
| BR-115 | EEO gender codes: M = Male, F = Female, O = Other, NULL = Not Disclosed | Reporting | Compliance | High | ✅ HIGH | PKG_REPORTING.eeo_compliance_report |
| BR-116 | Employee maintenance screen default filter shows only ACTIVE employees with active flag = Yes | Employee Management | Soft Constraint | Low | ✅ HIGH | HRMS_EMPLOYEE.xml DEFAULT_WHERE |
| BR-117 | Client-side email validation rejects subdomain addresses (e.g. user@mail.company.com). Server-side validation accepts them. These rules can diverge | Employee Management | Soft Constraint | Medium | ✅ HIGH | HRMS_VALIDATION_LIB.validate_email vs PKG_COMMON.is_valid_email |
| BR-118 | Client-side SSN validation: exactly 9 digits; none of the three segments (positions 1–3, 4–5, 6–9) may be all zeros. Server-side validation does not check for all-zero segments | Employee Management | Compliance | Medium | ✅ HIGH | HRMS_VALIDATION_LIB.validate_ssn vs PKG_COMMON.is_valid_ssn |
| BR-119 | A phone number is valid if it contains 10 or 11 digits after stripping non-digit characters | Employee Management | Soft Constraint | Low | ✅ HIGH | HRMS_VALIDATION_LIB.validate_phone; PKG_COMMON.is_valid_phone |
| BR-120 | Dependent relationships must be one of: Spouse, Child, Parent, Domestic Partner, Other | Employee Management | Hard Constraint | Low | ✅ HIGH | EMPLOYEE_DEPENDENTS.CHK_RELATIONSHIP |

### [EDGE-CASE-FOUND] Additional Business Rules — Pass 2

The following rules were confirmed by second-pass tracing and are not explicitly catalogued above:

| ID | Rule | Domain | Type | Severity | Confidence | Source |
|---|---|---|---|---|---|---|
| BR-121 | [EDGE-CASE-FOUND] Head-of-Household filers receive zero federal income tax withholding. The HOH filing status branch is absent from calculate_federal_tax; the code falls through to a zero result. This is a defect, not intended policy | Payroll | Compliance | Critical | ⚠️ LOW — confirmed defect | PKG_PAYROLL.calculate_federal_tax |
| BR-122 | [EDGE-CASE-FOUND] The additional Medicare 0.9% surtax uses a single USD 200,000 threshold for all filing statuses. The IRS threshold for married filing jointly is USD 250,000; MFJ employees earning between USD 200,000 and USD 250,000 are over-withheld by 0.9% on that band | Payroll | Compliance | High | ⚠️ LOW — confirmed defect | PKG_PAYROLL.calculate_medicare |
| BR-123 | [EDGE-CASE-FOUND] State income tax withholding ignores the W-4 state allowances and filing status fields entirely. The fields are accepted and stored in EMPLOYEE_TAX_INFO but are never read inside calculate_state_tax; only the flat rate is applied | Payroll | Compliance | High | ⚠️ LOW — confirmed defect | PKG_PAYROLL.calculate_state_tax |
| BR-124 | [EDGE-CASE-FOUND] Passwords are not verified during authentication. PKG_SECURITY.authenticate locates the employee by email, creates a session, and returns a session ID without reading USER_CREDENTIALS or comparing any password hash. Any active employee can log in with any credentials | Security & Access | Hard Constraint | Critical | ⚠️ LOW — confirmed defect | PKG_SECURITY.authenticate |
| BR-125 | [EDGE-CASE-FOUND] Password changes pass complexity validation but are never written to USER_CREDENTIALS. The UPDATE statement that would persist the new hash is absent from PKG_SECURITY.change_password. Passwords cannot be changed through any application pathway | Security & Access | Hard Constraint | Critical | ⚠️ LOW — confirmed defect | PKG_SECURITY.change_password |
| BR-126 | [EDGE-CASE-FOUND] A payroll run can be reversed from any status without a prior-status check. A PENDING, CALCULATING, or ERROR run can be reversed as readily as an APPROVED run | Payroll | Hard Constraint | Medium | ⚠️ LOW — defect | PKG_PAYROLL.reverse_payroll |
| BR-127 | [EDGE-CASE-FOUND] PKG_COMMON.business_days_between does not exclude holidays, while PKG_LEAVE.calculate_business_days does. The two functions return different counts for the same date range whenever a public holiday falls within it | Cross-Cutting | Hard Constraint | Low | ✅ HIGH — confirmed divergence | PKG_COMMON vs PKG_LEAVE |
| BR-128 | [EDGE-CASE-FOUND] Leave request backdating uses calendar days, not business days. An employee submitting on a Saturday for a Monday start 6 calendar days prior (but only 4 business days prior) is blocked, contrary to the apparent business intent of allowing 5 working days of backdating | Leave Management | Hard Constraint | Low | ✅ HIGH | PKG_LEAVE.submit_leave_request |

---

## OUTPUT 4 — Stakeholder & Role Matrix

| Technical Role ID | Plain English Name | Responsibilities | Actions They Can Trigger | Data They Can Access | Domain(s) Active In |
|---|---|---|---|---|---|
| GRADE_1_2 | Entry-Level and Junior Staff | Perform day-to-day work; manage own leave and performance activities | Submit, view, cancel own leave requests; submit self-assessment; acknowledge own review; update own goal progress | Own employee record; own leave balances and requests; own performance review and goals | Employee Management (own), Leave Management, Performance Management |
| GRADE_3_4 | Mid-Level and Senior Professional | Carry out specialist work; manage own HR activities | All Grade 1–2 actions | Own records; team calendar if assigned as approver | Employee Management (own), Leave Management, Performance Management |
| GRADE_5 | Lead / Team Lead | Lead a team; approve direct report leave; conduct performance reviews | All Grade 3–4 actions; approve/reject leave; submit manager reviews; view team calendar and pending approvals | All modules VIEW; direct report records; team leave and performance | Employee Management (view), Leave Management, Performance Management |
| GRADE_6 | Manager | Manage a department; compensation and performance decisions | All Grade 5 actions; view compensation data for team | Departmental headcount, compensation, team leave and reviews | Employee Management (view), Leave Management, Performance Management, Reporting |
| GRADE_7 | Senior Manager | Oversee multiple teams; organisational planning | All Grade 6 actions; cross-departmental reporting | All modules VIEW; cross-departmental data | All domains (VIEW) |
| GRADE_8 | Director | Full decision authority across all modules; payroll approval | All actions all modules; payroll approval; review cycle management | All tables and modules | All domains |
| GRADE_9 | Vice President | Senior executive authority | All Director actions | All data | All domains |
| GRADE_10 | C-Suite Executive | Highest authority | All actions | All data | All domains |
| HR_ADMIN | HR Administrator | Maintain employee records; manage employment lifecycle; configure leave and review cycles | Create/update/transfer/promote/terminate/rehire employees; adjust leave balances; create and open review cycles; generate cycle reviews; run year-end carryover | All employee records; all leave type and balance data; all review cycle data | Employee Management, Leave Management, Performance Management |
| PAYROLL_MANAGER | Payroll Manager | Manage end-to-end payroll; ensure accuracy and timely approval | Create pay periods; create runs; calculate payroll; approve runs; reverse runs; generate pay register and GL journal feed | All payroll data: salary records, pay periods, runs, detail lines, tax information | Payroll, Reporting & Integration |
| PAYROLL_ADMIN | Payroll Administrator | Perform payroll processing under direction of Payroll Manager; cannot approve | Create runs; initiate calculation; generate pay register | Payroll runs and detail lines; pay periods; salary records | Payroll |
| SYSTEM_SCHEDULER | Automated Scheduler | Run recurring batch processes without human intervention | Monthly leave accrual; notification queue every 5 minutes; year-end carryover; GL journal; benefits feed export | All tables involved in batch processes | Leave Management, Notifications, Reporting & Integration |
| EMPLOYEE_SELF | Employee (Self-Service) | Manage own HR activities | Submit/view/cancel own leave; view own balances; submit self-assessment; acknowledge review; update goals; change own password; view own payslip | Own employee record; own leave; own review | Employee Management (own), Leave Management, Performance Management |
| MANAGER_APPROVER | Leave Approver / Direct Manager | Approve or reject direct report leave; conduct performance reviews | Approve/reject pending leave for assigned reports; submit manager review and rating; view team calendar and pending approvals | Direct report leave requests; direct report reviews; team calendar | Leave Management, Performance Management |
| SYSTEM | HRMS Internal Processes | Automatically enforce business rules and fire inter-module integrations | Auto-cancel pending leave on termination; auto-approve no-approval leave types; queue notifications; write audit and history records | All tables | All domains |

> **[EDGE-CASE-FOUND] Anonymous / Unauthenticated actor:** No business actions are available to an unauthenticated caller. The only surface is the login endpoint. Because password verification is not implemented (BR-124), any active employee's email address is sufficient to gain a fully authenticated session — there is no password barrier at runtime.

---

## OUTPUT 5 — Value Stream Maps

### Value Stream: Employee Lifecycle
**Trigger:** Decision to hire a new person for the organisation
**Actors Involved:** HR Administrator, Hiring Manager, Payroll Administrator, Employee, Manager, System
**Terminal Outcomes:** Employee ACTIVE and contributing; or TERMINATED with all records closed; or REHIRED after prior termination

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | New Employee Record Created | HR Administrator | Enter employee details, assign department, job, manager, and starting salary | Decision to hire made; department and job title exist and are active | Employee record created with ACTIVE status; unique employee number assigned; welcome email sent | Value-Adding |
| 2 | Employee Active | Employee, Manager, HR | Employee performs their role; personal details updated as needed; manager assigns work | Employee record in ACTIVE status | Ongoing employment; record maintained | Value-Adding |
| 3 | Department Transfer | HR Administrator | Move employee to a new department, job, or location | Employee in ACTIVE status; transfer request initiated | Employee record updated; transfer history entry written; prior assignment preserved | Value-Adding |
| 4 | Promotion | HR Administrator | Assign a higher job title and new salary | Promotion decision made | Employee job title updated; new salary record effective; promotion history written | Value-Adding |
| 5 | On Leave | Employee, Manager | Employee takes approved leave | Leave request APPROVED | Employment status remains ACTIVE; leave counted in USED balance | Wait-Queue |
| 6 | Suspended | HR Administrator | Employment suspended pending investigation or disciplinary process | HR or management decision | Employment status = SUSPENDED | Wait-Queue |
| 7 | Termination Processed | HR Administrator | Record employee departure, cancel pending leave, close salary and pay elements | Termination decision made; employee not already TERMINATED | Status = TERMINATED; salary and elements closed; manager notified; COBRA/access revocation flagged as incomplete | Value-Adding |
| 8 | Rehire | HR Administrator | Reinstate a departed employee under new terms | Employee previously TERMINATED; rehire decision made | Status = ACTIVE; new hire date; prior history preserved | Value-Adding |

**Handoff Points:**
- Stage 1 → Payroll: Salary record created in Payroll domain immediately on hire
- Stage 1 → Notifications: Welcome email to employee; new direct report email to manager
- Stage 4 → Payroll: New salary record created in Payroll domain
- Stage 7 → Notifications: Termination notification to manager

**Wait States:**
- Stage 5 (On Leave): process waits for leave period to end (no time-bound SLA in system)
- Stage 6 (Suspended): process waits for HR/management decision (no time-bound SLA in system)

**External Dependencies:** None confirmed; COBRA benefits and system access revocation are TODOs

**States Accounted For:**
- ACTIVE → Stage 2
- ON_LEAVE → Stage 5
- SUSPENDED → Stage 6
- TERMINATED → Stage 7

**Unaccounted States:** None — all four EMPLOYMENT_STATUS values are mapped

---

### Value Stream: Payroll Run
**Trigger:** Payroll administrator initiates a run for an open pay period
**Actors Involved:** Payroll Administrator, Payroll Manager, System Scheduler, Finance (GL import)
**Terminal Outcomes:** Run APPROVED and GL journal produced; or Run REVERSED; or Run in ERROR awaiting remediation

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Pay Period Open | Payroll Administrator | Select the active pay period for processing | Pay period exists with OPEN status | Pay period identified; run can be created | Value-Adding |
| 2 | Payroll Run Created | Payroll Administrator | Create the payroll run for the selected period | Pay period is OPEN | Run record created with PENDING status | Value-Adding |
| 3 | Calculation In Progress | System | Calculate gross pay, taxes, and deductions for all active employees | Run in PENDING status; administrator initiates calculation | Run status = CALCULATING; all pay detail lines written | Value-Adding |
| 4 | Calculated | Payroll Administrator | Review calculation results, check error count, inspect individual payslips | Calculation complete | Run status = CALCULATED (or ERROR if any employee failed) | Verification |
| 4a | Error Review | Payroll Administrator | Investigate employees flagged with calculation errors; correct salary records or tax data and recalculate | Run status = ERROR | Errors resolved; run recalculated | Exception |
| 5 | Approved | Payroll Manager | Approve the calculated run after verifying totals | Run status = CALCULATED; approver has APPROVE permission | Run status = APPROVED; approval date and approver recorded | Approval Gate |
| 6 | GL Journal Generated | System | Produce the pipe-delimited journal file for Oracle Financials import | Run APPROVED; GL feed integration active | Journal file written to GL_FEED_OUT directory | Value-Adding |
| 7 | Reversed | Payroll Manager | Cancel the run if an error is found post-approval | Any status | Run and all detail lines marked REVERSED | Exception |

**Handoff Points:**
- Stage 5 → Integration: GL journal generation triggered after approval
- Stage 5 → 〰️ ASSUMED payment disbursement to employee bank accounts (not implemented)

**Wait States:**
- Stage 4 (Calculated): waits for human review before approval — no SLA coded in system

**External Dependencies:**
- Stage 6: Oracle Financials GL import — file pickup mechanism not implemented in HRMS

**States Accounted For:**
- PENDING → Stage 2
- CALCULATING → Stage 3
- CALCULATED → Stage 4
- ERROR → Stage 4a
- APPROVED → Stage 5
- REVERSED → Stage 7

**Unaccounted States:** PAID — status exists in the data model but no transition logic found in code (⚠️ LOW — PAID status has no procedure to set it; payment disbursement is not implemented)

---

### Value Stream: Leave Request
**Trigger:** Employee submits a request for time off
**Actors Involved:** Employee, Manager (Approver), HR Administrator, System
**Terminal Outcomes:** Leave TAKEN (time used); or REJECTED (days returned); or CANCELLED (days returned); or auto-approved with no manual step

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Leave Requested | Employee | Select leave type, dates, half-day flag, and reason; submit request | Employee ACTIVE; leave type active; tenure requirement met; dates valid; no overlap; sufficient balance (accrual types) | Request created; PENDING balance increased; status = PENDING (or auto-APPROVED for no-approval types) | Value-Adding |
| 2 | Awaiting Approval | Manager | Manager reviews the pending request in their approvals queue | Request status = PENDING; leave type requires approval | Manager sees request in pending list | Wait-Queue |
| 3 | Approved | Manager | Manager approves the request | Request status = PENDING | Status = APPROVED; PENDING balance decremented; USED balance incremented; employee notified | Handoff |
| 3a | Rejected | Manager | Manager rejects the request with a reason | Request status = PENDING | Status = REJECTED; PENDING balance released; employee notified with reason | Exception |
| 4 | Cancelled | Employee or System | Employee cancels approved or pending leave; system auto-cancels on termination | Request status = PENDING or APPROVED | Status = CANCELLED; balance restored (PENDING or USED decremented accordingly) | Exception |
| 5 | Leave Taken | System / HR | Leave period passes; leave is recorded as taken | Status = APPROVED; leave dates reached | Status = TAKEN (manual or batch update) | Value-Adding |

**Handoff Points:**
- Stage 1 → Notifications: Manager notified of pending request (if approval required)
- Stage 3 → Notifications: Employee notified of approval
- Stage 3a → Notifications: Employee notified of rejection with reason

**Wait States:**
- Stage 2 (Awaiting Approval): no time-bound SLA in system for manager to respond

**External Dependencies:** None

**States Accounted For:**
- PENDING → Stage 2
- APPROVED → Stage 3
- REJECTED → Stage 3a
- CANCELLED → Stage 4
- TAKEN → Stage 5

**Unaccounted States:** None — all five LEAVE_REQUESTS status values are mapped

---

### Value Stream: Annual Performance Review
**Trigger:** HR creates and opens a new performance review cycle for the year
**Actors Involved:** HR Administrator, Employee, Manager, System
**Terminal Outcomes:** Review ACKNOWLEDGED by employee; or stalled in any intermediate status (no escalation mechanism found)

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Cycle Created | HR Administrator | Define review cycle name, year, start/end dates, and due dates | Organisational decision to run annual reviews | Cycle in DRAFT status | Value-Adding |
| 2 | Cycle Opened | HR Administrator | Open the cycle to allow reviews to begin | Cycle in DRAFT status | Cycle status = OPEN; reviews generated for all eligible employees; employees notified | Value-Adding |
| 3 | Not Started | Employee | Review exists but employee has not yet begun their self-assessment | Review status = NOT_STARTED | Employee notified to begin self-assessment | Wait-Queue |
| 4 | Self-Review | Employee | Employee writes and submits their self-assessment | Review in NOT_STARTED or SELF_REVIEW status | Status = MANAGER_REVIEW; manager notified that self-assessment is ready | Value-Adding |
| 5 | Manager Review | Manager | Manager reads self-assessment, writes their assessment, assigns a rating 1.0–5.0 | Review status = MANAGER_REVIEW | Status = COMPLETED; rating label assigned; employee notified | Value-Adding |
| 6 | Completed | Employee | Employee reads the completed review and adds optional comments | Review status = COMPLETED | Status = ACKNOWLEDGED; acknowledgement date recorded | Verification |
| 7 | Acknowledged | HR Administrator | HR confirms all reviews complete; closes the cycle | All reviews ACKNOWLEDGED (or acceptable completion rate met) | Cycle status = CLOSED | Handoff |

**Handoff Points:**
- Stage 2 → Stage 3: System generates review records and sends employee notifications
- Stage 4 → Stage 5: Manager notified by email that self-assessment is ready
- Stage 5 → Stage 6: Employee notified by email that review is completed

**Wait States:**
- Stage 3 (Not Started): no SLA or escalation if employee does not begin self-assessment
- Stage 5 (Manager Review): no SLA or escalation if manager does not complete review

**External Dependencies:** None

**States Accounted For:**
- NOT_STARTED → Stage 3
- SELF_REVIEW → Stage 4 (entry condition; status in DDL but not an intermediate stop in the code path)
- MANAGER_REVIEW → Stage 5
- COMPLETED → Stage 6
- ACKNOWLEDGED → Stage 7

**Unaccounted States:**
- MEETING_SCHEDULED — status value exists in DDL but no procedure sets it; no transition logic found (⚠️ LOW — defined but unused)
- DRAFT/OPEN/IN_PROGRESS/CALIBRATION for REVIEW_CYCLES — OPEN and CLOSED are implemented; DRAFT is the initial state; IN_PROGRESS and CALIBRATION have no transition logic in the provided code (⚠️ LOW — partially implemented)

---

### [EDGE-CASE-FOUND] Value Stream: User Session
**Trigger:** Employee opens the HRMS Login screen and enters credentials
**Actors Involved:** Employee, System
**Terminal Outcomes:** CLOSED (explicit logout); EXPIRED (30-minute timeout elapsed)

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Login Attempt | Employee | Enter username (email) and password | Employee must be ACTIVE | Session created with ACTIVE status; session ID stored; employee context loaded | Value-Adding |
| 2 | Active Session | Employee | Use HRMS modules | Session is ACTIVE and within 30 minutes of login time | All module operations available based on grade permissions | Value-Adding |
| 3a | Explicit Logout | Employee | Click logout or close form | Session is ACTIVE | Session status = CLOSED; logout time recorded | Handoff |
| 3b | Session Expiry | System | Detect elapsed login time exceeds 30 minutes | 30 minutes elapsed since LOGIN_TIME regardless of activity | Session status = EXPIRED; user redirected to login | Exception |

**Unaccounted States:**
- No "LOCKED" state despite exception code -20302 (ACCOUNT_LOCKED) being defined in PKG_SECURITY. No lockout logic exists anywhere in the authentication or session code. Account lockout is defined in the exception catalogue but never triggered.

---

## OUTPUT 6 — Domain Architecture Map (Refined)

| Domain | Bounded Context | Core Entities | Complexity | Dependencies | Refinements from Deep Analysis |
|---|---|---|---|---|---|
| Employee Management | Core | EMPLOYEES, EMPLOYEE_HISTORY, DEPARTMENTS, JOB_TITLES, JOB_GRADES, LOCATIONS | Very High | Payroll (salary), Leave (balance init on hire), Notifications, Audit | Circular dependency confirmed with Payroll (PKG_EMPLOYEE calls PKG_PAYROLL.create_salary_record; PKG_PAYROLL calls PKG_EMPLOYEE.is_active). Promotion has no active-status pre-check (contrast with transfer). Three database triggers duplicate some package logic (common Oracle Forms anti-pattern). Dynamic SQL in search_employees creates SQL injection risk |
| Payroll | Core | SALARY_RECORDS, PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS, EMPLOYEE_TAX_INFO, EMPLOYEE_PAY_ELEMENTS, PAY_ELEMENTS | Very High | Employee Management, GL Integration, Notifications, Audit | 2024 tax brackets hard-coded despite TAX_BRACKETS table existing. PAID status in DDL has no implementation. YTD figures on payslip are zero placeholders. Partial commits every 50 employees create half-calculated state on failure |
| Leave Management | Core | LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES, LEAVE_ACCRUAL_LOG, HOLIDAYS | High | Employee Management, Notifications, Audit | Observed holiday logic does not handle observed dates (e.g. Friday substitute for Saturday holiday). Half-day overlap detection is known bug. Carryover expiry: CARRYOVER_EXPIRY column stores months (not days as Agent 1 may have inferred) |
| Performance Management | Supporting | REVIEW_CYCLES, PERFORMANCE_REVIEWS, PERFORMANCE_GOALS | Medium | Employee Management, Notifications, Audit | MEETING_SCHEDULED and CALIBRATION statuses exist in DDL but have no implementation. No SLA or escalation for stalled reviews |
| Security & Access | Cross-Cutting | USER_SESSIONS | Medium | Employee Management (email lookup), Audit | Password verification is a stub — USER_CREDENTIALS table referenced but actual check absent. No account lockout. Session timeout from login time only (no refresh). Encryption key hard-coded in source |
| Notifications | Cross-Cutting | NOTIFICATION_QUEUE | Low | Employee Management (email lookup) | No rate limiting. HTML templates hard-coded as strings. SMTP connection opened and closed per email (no pooling). Notification type SMS and IN_APP defined but only EMAIL is processed |
| Reporting & Integration | Supporting | Views, PKG_REPORTING, PKG_INTEGRATION | Medium | All core domains | Time and attendance import is a non-functional stub. Org structure sync (LDAP) is a non-functional stub. Reporting tables (RPT_*) referenced but not created in provided schema. FTP credentials stored in cleartext in SYSTEM_PARAMETERS |
| Audit & Logging | Cross-Cutting | AUDIT_LOG, SYSTEM_PARAMETERS | Low | None (called by all) | log_info has a JSON quoting bug (no quote escaping). Error logs go to TABLE_NAME='ERROR_LOG' with RECORD_ID=0; info logs to 'INFO_LOG' — these are sentinel values, not real table names |

### [EDGE-CASE-FOUND] Additional Domain Architecture Findings — Pass 2

| Domain | Finding |
|---|---|
| Payroll | EMPLOYEE_BANK_ACCOUNTS table exists and is populated with seed data, but no procedure in PKG_PAYROLL or PKG_INTEGRATION reads from it. Direct deposit is entirely unimplemented despite the table being present. |
| Payroll | TOTAL_EMPLOYER_COST column on PAYROLL_RUNS is never populated. Employer-paid benefit costs (the employer half of FICA, employer 401k match, employer medical premium) are not calculated or stored anywhere. GL journal therefore omits all employer-side costs. |
| Leave | The available balance formula diverges between VW_LEAVE_SUMMARY (omits PENDING) and the LEAVE_BALANCES virtual column (includes PENDING). Reports using the view will overstate available balance for employees with outstanding requests. |
| Security | FTP credentials for integration file transfers are stored as plaintext values in SYSTEM_PARAMETERS. Any database user with SELECT access to SYSTEM_PARAMETERS can retrieve them. |
| Notifications | SMS and IN_APP notification types are defined in the NOTIFICATION_QUEUE DDL and accepted by send_notification, but process_queue only handles TYPE = 'EMAIL'. All non-email notifications queue silently and are never delivered. |
| Reporting | RPT_* denormalised reporting tables are referenced in PKG_REPORTING.refresh_reporting_tables comments as a nightly materialisation target, but these tables do not exist in the schema DDL. The refresh function body is a stub (no INSERT/SELECT statements). |

---

## OUTPUT 7 — Pain Point Report

| # | Pain Point | Domain(s) | Severity | Evidence | Automation Opportunity |
|---|---|---|---|---|---|
| PP-01 | Hire date validation inconsistency: the screen allows dates up to 90 days in the future but the database trigger allows 180 days. Both constraints enforce different limits on the same field, creating confusion and potential data quality issues | Employee Management | High | BR-14 (90 days, form) vs BR-15 (180 days, trigger); DISC-001 | Yes — consolidate to a single enforced rule; remove the redundant check |
| PP-02 | SQL injection vulnerability in employee search: the search function builds queries by concatenating employee names directly into SQL text instead of using parameterised values. Attackers with API access could extract or corrupt data | Employee Management | High | PKG_EMPLOYEE.search_employees — documented in source code comment | Yes — replace string concatenation with bind variables; no business logic change required |
| PP-03 | Payment disbursement is not implemented: payroll runs can be approved but there is no mechanism to send net pay to employees. Three critical integrations are marked as TODO: bank account payments, COBRA benefits notification, and system access revocation on termination | Payroll, Employee Management | High | PKG_EMPLOYEE.terminate_employee TODOs; no payment processing code found | Yes — requires integration with payment processor (ACH/bank) and benefits/IT systems |
| PP-04 | Hard-coded 2024 tax brackets: federal tax rates are embedded directly in the payroll calculation code. Tax year changes require a code deployment rather than a data update. The TAX_BRACKETS table exists and is populated but is not used | Payroll | High | PKG_PAYROLL.calculate_federal_tax — TODO in code to use TAX_BRACKETS table | Yes — migrate calculation to read from TAX_BRACKETS table; update rates annually without code changes |
| PP-05 | Password verification is a stub: the authentication procedure does not actually verify the user's password. The USER_CREDENTIALS table is referenced in comments but the password check code is absent. Users may log in without a valid password | Security & Access | High | PKG_SECURITY.authenticate — password check absent from code | Yes — implement password hash comparison against USER_CREDENTIALS; existing hash_password function using MD5 should also be upgraded to a stronger algorithm |
| PP-06 | Hard-coded encryption key in source code: the AES-256 encryption key for Social Security Numbers is written directly into the package body as a string constant. Anyone with access to the source code has the key | Security & Access | High | PKG_SECURITY — c_encryption_key constant visible in source | Yes — move key to Oracle Wallet or a secure vault; do not store credentials in source code |
| PP-07 | No account lockout after failed login attempts: the system has no protection against repeated failed login attempts. An attacker can try passwords indefinitely without being blocked | Security & Access | High | PKG_SECURITY.authenticate — no attempt counter or lockout logic | Yes — implement failed-attempt counter in USER_SESSIONS or a dedicated table; lock after N failures (typically 5) |
| PP-08 | Session timeout measures from login time, not from last activity: a user who is actively working will be logged out after 30 minutes regardless. A user who walks away from their computer stays logged in for 30 minutes. Neither behaviour is ideal | Security & Access | Medium | PKG_SECURITY.is_session_valid — timeout based on LOGIN_TIME, not last activity | Yes — update last-activity timestamp on each session validation check |
| PP-09 | Payroll partial commit risk: the payroll calculation commits to the database every 50 employees. If the process fails partway through, the run is left in a half-calculated state with some employees processed and others not, requiring manual clean-up | Payroll | Medium | PKG_PAYROLL.calculate_payroll — intermediate COMMITs every 50 rows | Yes — use savepoints and a restart-from-last-commit mechanism, or process in a single transaction with a full rollback on failure |
| PP-10 | Organisation chart times out for large organisations: the hierarchical query used to build the reporting structure is documented to time out for organisations with more than 500 employees | Employee Management | Medium | PKG_EMPLOYEE.get_org_chart — known bug documented in source; VW_ORG_HIERARCHY same warning | Yes — materialise the hierarchy nightly into a flat table; query the flat table instead of running recursive SQL on demand |
| PP-11 | Employee number generation race condition: the system generates employee numbers by finding the current maximum and adding one. Under concurrent user activity, two users could generate the same number simultaneously | Employee Management | Medium | PKG_EMPLOYEE.generate_emp_number — SELECT MAX()+1 without locking; documented as known bug | Yes — use the SEQ_EMPLOYEE sequence exclusively; remove the MAX()+1 logic |
| PP-12 | No SLA on leave approval: managers have no time limit to approve or reject leave requests. Employees may wait indefinitely without knowing whether their leave is approved, preventing them from making firm plans | Leave Management | Medium | No SLA rule found in Business Rules Catalog; Stage 2 of Leave Request Value Stream is an unbounded wait | Yes — configure an escalation reminder notification after N days; auto-escalate to the manager's manager if no response within a set period |
| PP-13 | No SLA on performance review completion: neither the self-assessment stage nor the manager review stage has a time-bound escalation. Reviews can remain stalled indefinitely, reducing the value of the review programme | Performance Management | Medium | No SLA rule found for review stages; SELF_REVIEW_DUE and MANAGER_REVIEW_DUE fields exist in REVIEW_CYCLES but are not checked in any procedure | Yes — add a scheduled job that checks due dates and sends reminder notifications to employees and managers who have not completed their steps |
| PP-14 | Validation drift between client and server: email format and SSN validation are implemented differently in the Oracle Forms client library and in the server-side package. Data that passes one check may fail the other, and records entered via the API bypass client validation entirely | Employee Management | Medium | BR-117, BR-118; HRMS_VALIDATION_LIB vs PKG_COMMON; DISC-006, DISC-007 | Yes — consolidate validation to a single server-side rule; remove or align client-side checks |
| PP-15 | SMTP connection opened per email: the notification processor opens and closes a new SMTP connection for each individual email in the queue. For a batch of 50 emails this creates 50 separate connections, which is slow and places unnecessary load on the mail server | Notifications | Medium | PKG_NOTIFICATION.process_queue — connection per message, no pooling | Yes — open one SMTP connection per batch run; reuse it for all messages in the batch |
| PP-16 | No rate limiting on notifications: bulk operations such as payroll runs, which process hundreds of employees, can add hundreds of notifications to the queue simultaneously. There is no throttle to prevent flooding the mail server | Notifications | Medium | PKG_NOTIFICATION.pks known issues — no rate limiting | Yes — add a rate-limit parameter to the queue processor; or group similar notifications into digest emails |
| PP-17 | Observed holiday dates not handled: the holiday exclusion logic checks only the exact holiday date. When a holiday falls on a weekend, the observed day (e.g. Friday before or Monday after) is not automatically excluded, causing leave day counts and business day calculations to include days the business is actually closed | Leave Management | Low | PKG_LEAVE.calculate_business_days — known bug documented in source | Yes — add an OBSERVED_DATE column to HOLIDAYS or a lookup table for substituted observed dates |
| PP-18 | YTD figures missing from payslips: the year-to-date gross and year-to-date net fields on every payslip are hard-coded to zero. Employees and managers cannot see cumulative pay for the year on the payslip | Payroll | Low | PKG_PAYROLL.get_payslip — YTD_GROSS=0, YTD_NET=0 hardcoded; documented in code | Yes — implement YTD accumulation using the existing get_ytd_earnings function |
| PP-19 | Time and attendance import is non-functional: the file reading scaffolding exists but no data is actually written to the database. Hours data from the time-and-attendance system cannot be imported | Reporting & Integration | Low | PKG_INTEGRATION.import_time_attendance — TODO in code; no INSERT/UPDATE statements | Yes — implement CSV parsing and update EMPLOYEE_HOURS or PAYROLL_DETAILS with the imported hours |
| PP-20 | FTP credentials stored in cleartext: integration credentials (FTP usernames, passwords) are stored as plain text in the SYSTEM_PARAMETERS table. Anyone with SELECT access to that table can see them | Reporting & Integration | High | PKG_INTEGRATION.pks known issue; SYSTEM_PARAMETERS table | Yes — use Oracle Wallet or encrypted credentials storage; remove cleartext secrets from the database |
| PP-21 | [EDGE-CASE-FOUND] Termination pending-leave balance leak: the termination procedure cancels PENDING leave by writing directly to LEAVE_REQUESTS, bypassing PKG_LEAVE. As a result, LEAVE_BALANCES.PENDING is never decremented. The employee's balance record retains a phantom pending deduction, understating available balance for reports indefinitely | Employee / Leave | High | PKG_EMPLOYEE.terminate_employee; LEAVE_BALANCES.PENDING | No — requires code fix: either call PKG_LEAVE.cancel_leave_request for each pending request, or add explicit PENDING balance decrements in terminate_employee |
| PP-22 | [EDGE-CASE-FOUND] Approved future leave not cancelled on termination: only PENDING leave is auto-cancelled at termination. APPROVED future leave remains in STATUS = 'APPROVED' after the employee is gone, inflating utilisation figures and leave liability balances | Employee / Leave | Medium | PKG_EMPLOYEE.terminate_employee step 4 | No — requires code fix: extend the cancellation loop to include APPROVED requests with START_DATE > SYSDATE |
| PP-23 | [EDGE-CASE-FOUND] Turnover classification is case-sensitive free-text: the voluntary/involuntary classification in the turnover report does an exact match on TERMINATION_REASON = 'VOLUNTARY'. Any variation in case or phrasing (e.g. 'voluntary', 'Voluntary resignation') counts as involuntary, making the voluntary rate unreliable | Reporting | Medium | BR-113; PKG_REPORTING.turnover_report | Yes — add a constrained termination reason list (LOV / CHECK constraint) and apply UPPER() in the comparison; or replace the free-text field with a structured code |
| PP-24 | [EDGE-CASE-FOUND] Leave backdating limit uses calendar days not business days: the 5-day backdating rule is checked against calendar days. An employee submitting on Saturday for a leave that started the previous Monday is 6 calendar days back (blocked) but only 4 business days back (should be allowed under the stated 5-business-day intent) | Leave | Low | BR-128; PKG_LEAVE.submit_leave_request | No — minor code fix: replace the TRUNC(SYSDATE) − p_start_date calendar comparison with a business-day-equivalent check |

---

## OUTPUT 8 — Automation Opportunities

| # | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-01 | Automated payroll run initiation | Payroll administrator manually creates and initiates a calculation run each period | DBMS_SCHEDULER job triggers create_payroll_run and calculate_payroll on the scheduled pay date; result queued for human approval review | High — eliminates manual initiation step; reduces risk of missed payroll |
| AO-02 | Tax bracket data management | 2024 federal tax brackets are hard-coded in PL/SQL; a rate change requires a code deployment | Load bracket data into the TAX_BRACKETS table (already in schema); update calculate_federal_tax to read from it; annual updates become a data change not a code change | High — eliminates deployment risk for annual tax rate changes |
| AO-03 | Leave approval escalation | Managers have no deadline to respond; requests can wait indefinitely | Scheduled job checks PENDING requests older than a configurable threshold (e.g. 3 business days); sends reminder to manager; after a second threshold (e.g. 5 days) auto-escalates to the manager's manager | High — eliminates unbounded wait states; improves employee experience |
| AO-04 | Performance review deadline reminders | Self-review and manager-review due dates are stored but never checked | Scheduled job compares today against SELF_REVIEW_DUE and MANAGER_REVIEW_DUE in REVIEW_CYCLES; sends targeted reminders to employees or managers who have not yet completed their step | Medium — reduces reviews stalled at intermediate stages; improves cycle completion rate |
| AO-05 | Year-end leave carryover and expiry | process_carryover and expire_carryover procedures exist but must be manually triggered | DBMS_SCHEDULER job runs process_carryover on December 31 and expire_carryover on the first day of each month | Medium — eliminates risk of manual omission; ensures consistent year-end processing |
| AO-06 | Monthly leave accrual | run_monthly_accrual is designed for scheduled execution but scheduling is not confirmed in provided code | DBMS_SCHEDULER job on the 1st of each month calling run_monthly_accrual | Medium — ensures consistent, timely accrual credits |
| AO-07 | GL journal automatic delivery | GL journal file is written to a directory; actual delivery to Oracle Financials requires a separate file transfer not implemented in HRMS | Add a file transfer step (UTL_FILE + DBMS_SCHEDULER or Oracle Integration Cloud) to move the file to the Financials import drop zone after generation | Medium — removes a manual handoff; reduces payroll-to-GL latency |
| AO-08 | Notification SMTP connection pooling | Each email opens a new SMTP connection, one per message | Refactor process_queue to open one connection, send all messages in the batch, then close | Low-Medium — improves notification throughput; reduces mail server load |
| AO-09 | Employee search SQL injection fix | search_employees uses string concatenation for name parameters | Replace string concatenation with bind variables using OPEN cursor FOR v_sql USING syntax | High (security) — eliminates injection vector; no business logic change required |
| AO-10 | Org chart materialisation | Recursive hierarchy query times out for 500+ employees | Nightly job materialises the hierarchy into a flat RPT_ORG_HIERARCHY table; forms and reports query the flat table | Medium — resolves known performance issue; enables instant org chart display |

### [EDGE-CASE-FOUND] Additional Automation Opportunities — Pass 2

| # | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-11 | [EDGE-CASE-FOUND] Automate leave TAKEN status transition | Approved leave that has passed its end date remains STATUS = 'APPROVED' forever; leave utilisation reports are permanently inaccurate | Schedule a nightly DBMS_SCHEDULER job: UPDATE LEAVE_REQUESTS SET STATUS = 'TAKEN' WHERE STATUS = 'APPROVED' AND END_DATE < TRUNC(SYSDATE) | High — fixes leave utilisation reporting; removes stale APPROVED records |
| AO-12 | [EDGE-CASE-FOUND] Automate payroll disbursement confirmation (PAID status) | PAID status is defined in the schema but no procedure sets it; there is no record that employees were actually paid | Add a "Confirm Disbursement" step or batch confirmation that advances APPROVED runs to PAID after the bank file is sent; captures disbursement date | Medium — completes the payroll audit trail; enables payroll-to-bank reconciliation |
| AO-13 | [EDGE-CASE-FOUND] Automate manager notification on leave cancellation | Managers are not notified when employees cancel approved leave; a manager who planned staffing around an approved absence is not informed | Add one PKG_NOTIFICATION.send_notification call inside PKG_LEAVE.cancel_leave_request when the cancelled request was in APPROVED status | Medium — low code effort, high operational value for managers |
| AO-14 | [EDGE-CASE-FOUND] Complete time and attendance import | File reader is coded; CSV parsing and DB writes are marked TODO | Complete import_time_attendance to parse each CSV row and INSERT into a time entries table; feed hours-based pay elements from that table | High — currently all payroll calculations assume salaried employees only; this unlocks variable-hours pay |

---

## ⚠️ Validation Queue

| ID | Domain | Item | Reason for Uncertainty |
|---|---|---|---|
| VQ-OPEN-01 | Payroll | PAID status in PAYROLL_RUNS DDL has no transition procedure. It is unclear whether this status is set externally, by a process not in scope, or is simply unused | ⚠️ LOW — no SET STATUS='PAID' statement found in any package |
| VQ-OPEN-02 | Performance | MEETING_SCHEDULED status exists in PERFORMANCE_REVIEWS DDL but no code sets it. May be a planned feature not yet implemented | ⚠️ LOW — status defined, no transition logic |
| VQ-OPEN-03 | Performance | CALIBRATION and IN_PROGRESS statuses exist in REVIEW_CYCLES DDL but only DRAFT → OPEN and OPEN → CLOSED transitions are coded | ⚠️ LOW — partial implementation |
| VQ-OPEN-04 | Security | Password verification in PKG_SECURITY.authenticate appears incomplete. USER_CREDENTIALS table is referenced in comments but not in the executable body. It is unknown whether this is an intentional omission, a separate package, or a genuine implementation gap | ⚠️ LOW — security-critical gap; requires human review |
| VQ-OPEN-05 | Payroll | TOTAL_EMPLOYER_COST column exists in PAYROLL_RUNS but is never populated by any procedure in the provided code | ⚠️ LOW — column present, no write path found |
| VQ-OPEN-06 | Integration | RPT_* reporting tables are referenced in PKG_REPORTING.refresh_reporting_tables comments as a nightly denormalisation target but are not defined in the schema scripts provided | ⚠️ LOW — referenced but not found |
| VQ-OPEN-07 | Notifications | SMS and IN_APP notification types are defined in the NOTIFICATION_QUEUE DDL but only EMAIL is processed by process_queue | ⚠️ LOW — defined but unimplemented |
| VQ-OPEN-08 | Leave | The TAKEN status for leave requests is defined in the DDL. No procedure in PKG_LEAVE sets status to TAKEN. It may be set by a forms trigger, a batch job, or a missing procedure | ⚠️ LOW — status defined, no write path found in packages |
| VQ-OPEN-09 | Employee | The ACTIVE_FLAG on employees is set to 'N' on termination. However, VW_ACTIVE_EMPLOYEES filters on both EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y'. It is unclear whether ON_LEAVE and SUSPENDED employees have ACTIVE_FLAG = 'Y' or 'N' — the code only explicitly sets it to 'N' at termination | ⚠️ LOW — inconsistency between flag and status |
| VQ-OPEN-10 | Security | PKG_SECURITY.change_password validates the new password and calls PKG_AUDIT.log_action but does not contain a write to USER_CREDENTIALS. The actual password storage step is absent | ⚠️ LOW — stub implementation; security gap |

### [EDGE-CASE-FOUND] Pass 2 Validation Queue Resolutions and New Items

| ID | Domain | Item | Status |
|---|---|---|---|
| VQ-P2-01 | Employee | ON_LEAVE and SUSPENDED employment statuses exist in the schema CHECK constraint but no code path sets them | ✅ RESOLVED — both are confirmed orphaned states; no setter exists in any package or trigger |
| VQ-P2-02 | Employee | EMPLOYEE_HISTORY trigger column mismatch (CHANGE_DATE / OLD_VALUE / NEW_VALUE vs DDL typed columns) | ✅ RESOLVED — confirmed mismatch; trigger would raise "invalid identifier" at runtime; see DISC-003 |
| VQ-P2-03 | Employee | Rehire trigger conflict | ✅ RESOLVED — confirmed non-functional; TRG_EMP_BEFORE_UPDATE blocks the exact UPDATE that rehire_employee executes |
| VQ-P2-04 | Leave | TAKEN status setter | ✅ RESOLVED — no setter exists in any package or trigger; confirmed orphaned state |
| VQ-P2-05 | Payroll | PAID status setter | ✅ RESOLVED — no setter exists; confirmed orphaned state; see VQ-OPEN-01 |
| VQ-P2-06 | Performance | REVIEW_CYCLES IN_PROGRESS and CALIBRATION setters | ✅ RESOLVED — both are orphaned; only DRAFT → OPEN → CLOSED transitions are implemented |
| VQ-P2-07 | Performance | MEETING_SCHEDULED setter | ✅ RESOLVED — orphaned; no setter exists; see VQ-OPEN-02 |
| VQ-P2-08 | Employee | Manager approval workflow for out-of-band salary | ✅ RESOLVED — no approval workflow exists; salary outside band generates a soft warning only; any salary is accepted |
| VQ-P2-09 | Integration | Time import stub scope | ✅ RESOLVED — file reading is coded; CSV parsing and all DB writes are marked TODO; procedure is non-functional |
| VQ-P2-10 | Integration | Org sync stub scope | ✅ RESOLVED — only a log call exists; no LDAP/AD integration is implemented |
| VQ-P2-11 | Integration | GL employer-paid cost gap | ✅ RESOLVED — PAYROLL_DETAILS stores only employee-side amounts; employer contributions are not calculated or stored; GL journal omits employer costs |
| VQ-P2-12 | Reporting | RPT_* reporting tables | ✅ RESOLVED — no RPT_* tables exist in the DDL provided; refresh function is a stub |
| VQ-P2-13 | Reporting | Compa-ratio divergence | ✅ RESOLVED — VW_EMPLOYEE_COMPENSATION shows individual employee ratio; PKG_REPORTING.compensation_summary shows the group average; both are intentionally correct for different questions |
| VQ-P2-14 | Cross-cutting | Fiscal vs calendar year mixing | ✅ RESOLVED — payroll tax uses calendar year; business reporting uses fiscal year starting October; joins across these will produce mismatched results in October–December |
| VQ-P2-15 | Payroll | Biweekly 27-period year | ⚠️ LOW — algorithm confirmed capable of generating 27 periods; specific trigger years depend on the first Friday of each calendar year; not confirmed for any year in current seed data |

---

## 📋 Agent 1 Discrepancy Log

| ID | Agent 1 Statement | What Deep Analysis Found | Status |
|---|---|---|---|
| DISC-001 | Hire date validation limit | Agent 1 did not flag a conflict. Form enforces 90-day future limit; database trigger enforces 180-day limit. Two different values apply to the same field | ⚠️ UNRESOLVED — both rules exist; which is intended is unclear |
| DISC-002 | promote_employee active-status check | Agent 1 did not flag this gap. transfer_employee checks ACTIVE status; promote_employee does not. Employees can be promoted while SUSPENDED or ON_LEAVE | ⚠️ UNRESOLVED — likely an oversight; business intent unclear |
| DISC-003 | EMPLOYEE_HISTORY table structure | TRG_EMP_BEFORE_UPDATE inserts using columns CHANGE_DATE, OLD_VALUE, NEW_VALUE (VARCHAR2). The DDL defines EFFECTIVE_DATE and typed old/new columns. The trigger references a different column structure than the DDL | ⚠️ UNRESOLVED — trigger will fail at runtime if column names do not match; may indicate the trigger references a different version of the table |
| DISC-004 | VW_LEAVE_SUMMARY AVAILABLE formula | View calculates AVAILABLE = OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT (does not subtract PENDING). The LEAVE_BALANCES virtual column includes PENDING in its formula. Two different definitions of "available balance" exist in the same system | ⚠️ UNRESOLVED — users of the view will see a higher available balance than is accurate |
| DISC-005 | No active check on promotion | Agent 1 noted transfer requires ACTIVE status. Deep analysis confirmed promotion has no such check — discrepancy is real | ⚠️ UNRESOLVED |
| DISC-006 | Email validation divergence | Client-side (forms library) and server-side (PKG_COMMON) validate email differently. Server-side accepts subdomains; client-side rejects them | ⚠️ UNRESOLVED — same email can be valid in API calls and invalid in the form |
| DISC-007 | SSN validation divergence | Client-side checks for all-zero segments; server-side does not | ⚠️ UNRESOLVED — an SSN with all-zero area code (e.g. 000-XX-XXXX) passes server check but fails client check |
| DISC-008 | DEPT_ID=30 manager double-update | Seed data updates DEPARTMENTS.MANAGER_EMP_ID for DEPT_ID=30 twice: first to EMP_ID=3 (CIO Michael O'Connor), then immediately to EMP_ID=30 (Director Rachel Thompson). Final value is EMP_ID=30 | ✅ RESOLVED — final effective value is EMP_ID=30; first UPDATE is redundant |
| DISC-009 | reverse_payroll reason parameter not stored | PKG_PAYROLL.reverse_payroll accepts a p_reason parameter but does not store it anywhere. The reversal reason is lost | ⚠️ UNRESOLVED — compliance risk; reversal reasons should be auditable |

---

✅ Agent 2 Analysis Complete.
Documentation is ready for business review.
Highest-priority validation item: VQ-OPEN-04 — Password verification in the authentication function appears to be a non-functional stub. Users may be able to log in without supplying a correct password. This requires immediate confirmation with the development team before the system is used in a production environment.
