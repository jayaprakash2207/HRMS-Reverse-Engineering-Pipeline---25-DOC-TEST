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

