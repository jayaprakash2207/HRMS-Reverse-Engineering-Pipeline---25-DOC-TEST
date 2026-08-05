I'll write the full Agent 2 output directly — I have all findings in context.

---

## 🔍 Agent 2 — Analysis Summary

- **Domains analysed:** 6 — Employee Management, Payroll, Leave Management, Performance, Security/Session, Cross-cutting (Notifications, Audit, Integration, Reporting)
- **Chunks processed:** 5 (+ Synthesis Pass)
- **Business Rules catalogued:** 87 (BR-01 through BR-87)
- **Value Streams mapped:** 5 (Employee Lifecycle, Payroll Processing, Leave Request, Performance Review, User Session)
- **Agent 1 LOW CONFIDENCE items resolved:** 14 of 20
- **Discrepancies with Agent 1:** 9 (DISC-001 through DISC-009)

> **Second-pass focus:** This analysis prioritises rules implied but never explicitly stated, edge cases in exception paths, orphaned states, integration stubs, and defects where code contradicts stated intent.

---

## 📥 Agent 2 — Chunk 0 of 5 — Orientation Pass

**Domain Processing Order (by entity count and state complexity):**

| Priority | Domain | Entities | States | Notes |
|---|---|---|---|---|
| 1 | Employee Management | 7 tables, 5 views | 4 employment states | Core entity; depended on by all |
| 2 | Payroll | 8 tables | 11 states across 2 machines | Highest calculation complexity |
| 3 | Leave Management | 4 tables | 5 leave states | Complex state machine |
| 4 | Performance | 3 tables | 11 states across 2 machines | Cycle + review states |
| 5 | Cross-cutting | Audit, Security, Notifications, Integration, Reporting | Session states | Infrastructure + integration |

**Agent 1 Validation Queue Priority Targets:**
VQ-01 (ON_LEAVE/SUSPENDED setters), VQ-02 (history table column mismatch), VQ-03 (rehire trigger conflict), VQ-04 (YTD accumulation), VQ-05 (TAKEN status setter), VQ-06 (PAID status setter), VQ-07 (REVIEW_CYCLES IN_PROGRESS/CALIBRATION), VQ-08 (MEETING_SCHEDULED), VQ-09 (HR$ystem key rotation), VQ-10 (SQL injection scope), and VQ-11 through VQ-20 (salary override approval, password stub, time import stub, org sync stub, biweekly 27-period, carryover expiry, GL employer-paid gap, reporting table RPT_*, compa-ratio divergence, fiscal/calendar year mixing).

**Expected Value Stream Lifecycles:** Employee (HIRE→ACTIVE→TERMINATED/REHIRED), Payroll (OPEN period → PENDING run → CALCULATED → APPROVED → PAID), Leave (submission → PENDING → APPROVED/REJECTED → TAKEN), Performance (DRAFT cycle → OPEN → review NOT_STARTED → ACKNOWLEDGED), Session (LOGIN → ACTIVE → EXPIRED/CLOSED).

---

## OUTPUT 1 — Business Capability Map

| Capability | Plain English Description | Backing Service | Domain | Agent 1 Match? |
|---|---|---|---|---|
| Hire Employee | Create a new employee record with job, department, salary, and location; send welcome notification to employee and manager | PKG_EMPLOYEE | Employee | ✅ Confirmed |
| Update Personal Details | Change contact information, address, and name fields without affecting job or status | PKG_EMPLOYEE | Employee | ✅ Confirmed |
| Transfer Employee | Move an active employee to a different department, job, manager, and/or location on a specified effective date | PKG_EMPLOYEE | Employee | ✅ Confirmed |
| Promote Employee | Change an employee's job title and salary simultaneously, recording the percentage increase | PKG_EMPLOYEE | Employee | ✅ Confirmed |
| Terminate Employee | End an employee's employment, auto-cancel pending leave, close salary records, and notify manager | PKG_EMPLOYEE | Employee | ✅ Confirmed |
| Rehire Employee | Restore a terminated employee to active status with a new hire date, department, and salary | PKG_EMPLOYEE | Employee | ⚠️ Corrected — rehire is entirely non-functional as coded; the trigger that blocks direct reactivation fires against the very UPDATE that rehire_employee performs. Capability exists in code but cannot execute successfully |
| Search Employees | Find employees by name, department, status, location, or hire date range | PKG_EMPLOYEE | Employee | ✅ Confirmed — with security caveat: name parameters are SQL-injection vulnerable |
| View Org Chart | Display the hierarchical reporting structure from any root employee, up to a configurable depth | PKG_EMPLOYEE | Employee | ✅ Confirmed — with performance caveat: times out over 500 employees |
| Count Headcount | Count active employees as of any past or present date, for any department or company-wide | PKG_EMPLOYEE | Employee | ✅ Confirmed |
| Calculate Tenure | Calculate how many years an employee has worked, to one decimal place | PKG_EMPLOYEE | Employee | ✅ Confirmed |
| Manage Salary Records | Record a new annual salary with effective date, reason, and percentage change; end-date the previous record | PKG_PAYROLL | Payroll | ✅ Confirmed |
| Create Pay Periods | Generate monthly or biweekly pay calendar for a full year; monthly pay dates moved to Friday if weekend falls | PKG_PAYROLL | Payroll | ✅ Confirmed — with defect: biweekly algorithm can produce 27 periods in some years |
| Run Payroll Calculation | Calculate gross pay, all federal and state taxes, and benefit deductions for all active employees in a pay period | PKG_PAYROLL | Payroll | ✅ Confirmed — with defects: 2024 brackets only; HEAD_OF_HOUSEHOLD filers receive zero federal tax |
| Approve Payroll | Formally approve a completed payroll run for payment | PKG_PAYROLL | Payroll | ✅ Confirmed — PAID status after approval is an orphaned state; no procedure advances from APPROVED to PAID |
| Reverse Payroll | Mark a payroll run and all its detail lines as reversed | PKG_PAYROLL | Payroll | ⚠️ Corrected — no status pre-check; any run (including PENDING) can be reversed; reversal reason is accepted but never stored |
| Generate Pay Register | Export payroll results as a CSV file to a server-side directory | PKG_PAYROLL | Payroll | ✅ Confirmed — marked as legacy; YTD columns are always zero |
| View Payslip | Retrieve gross pay, tax breakdown, and deduction breakdown for an employee in a given run | PKG_PAYROLL | Payroll | ✅ Confirmed — YTD fields are hardcoded zero |
| Submit Leave Request | Submit a paid or unpaid leave request, checking balance, tenure, overlap, and backdating rules | PKG_LEAVE | Leave | ✅ Confirmed |
| Approve Leave Request | Approve a pending leave request; move balance from pending to used | PKG_LEAVE | Leave | ✅ Confirmed |
| Reject Leave Request | Reject a pending leave request; release the pending balance | PKG_LEAVE | Leave | ✅ Confirmed |
| Cancel Leave Request | Cancel a pending or approved leave request; restore the appropriate balance | PKG_LEAVE | Leave | ✅ Confirmed — with defect: manager is not notified of cancellation |
| Accrue Monthly Leave | Run monthly batch accrual for all active employees across all accrual-based leave types | PKG_LEAVE | Leave | ✅ Confirmed |
| Year-End Carryover | Carry unused leave balances forward to the next year, capped by leave type rules | PKG_LEAVE | Leave | ✅ Confirmed |
| Expire Carryover | Remove carried-over leave that has passed its expiry date | PKG_LEAVE | Leave | ⚠️ Corrected — reduces ADJUSTMENT (can produce confusing negative values) rather than OPENING_BALANCE; functionally correct but misleading |
| Create Review Cycle | Create an annual performance review cycle with dates and due dates | PKG_PERFORMANCE | Performance | ✅ Confirmed |
| Open Review Cycle | Transition a draft review cycle to open status, making reviews available | PKG_PERFORMANCE | Performance | ✅ Confirmed |
| Bulk Generate Reviews | Create individual performance review records for all active managed employees in a cycle | PKG_PERFORMANCE | Performance | ⚠️ Corrected — employees with no manager (including CEO) are excluded |
| Submit Self-Assessment | Allow an employee to submit their self-evaluation; notify manager | PKG_PERFORMANCE | Performance | ✅ Confirmed — only reachable from NOT_STARTED (SELF_REVIEW status is unreachable) |
| Submit Manager Review | Record a manager's rating and assessment; transition review to COMPLETED | PKG_PERFORMANCE | Performance | ⚠️ Corrected — no status pre-check; can overwrite a review in any status |
| Acknowledge Review | Allow employee to acknowledge receipt of completed review | PKG_PERFORMANCE | Performance | ✅ Confirmed |
| Track Goals | Create and update progress on performance goals with category, weight, and completion percentage | PKG_PERFORMANCE | Performance | ✅ Confirmed |
| Authenticate User | Verify a username and create an active session | PKG_SECURITY | Security | ⚠️ Corrected — password is NEVER verified; any active employee can log in with any password |
| Manage Session | Track session validity, expire sessions after 30 minutes of elapsed login time | PKG_SECURITY | Security | ⚠️ Corrected — timeout is from LOGIN_TIME, not last activity; active users are logged out after 30 minutes regardless |
| Check Permission | Determine whether an employee can perform an action on a module based on job grade | PKG_SECURITY | Security | ✅ Confirmed — grade-based model: grade ≥ 8 = full access; grade ≥ 5 = view all; everyone can submit leave and view own profile |
| Encrypt / Decrypt SSN | Protect Social Security Numbers using AES-256 encryption | PKG_SECURITY | Security | ✅ Confirmed — with critical vulnerability: encryption key is hard-coded in source |
| Queue Notification | Queue an email notification for async delivery via SMTP | PKG_NOTIFICATION | Notifications | ✅ Confirmed |
| Process Notification Queue | Send queued emails via SMTP in batches of 50; retry failed up to 3 times | PKG_NOTIFICATION | Notifications | ✅ Confirmed |
| Log Audit Event | Record every data change event with table, record, action, user, and IP address | PKG_AUDIT | Audit | ✅ Confirmed |
| Export GL Journal | Generate pipe-delimited flat file of payroll journal entries for Oracle Financials import | PKG_INTEGRATION | Integration | ✅ Confirmed — employer-paid benefit costs are not included |
| Export Benefits Feed | Generate fixed-width ADP-format benefits enrollment file for all active employees | PKG_INTEGRATION | Integration | ✅ Confirmed — legacy format |
| Import Time Data | Read time-and-attendance CSV from a file directory | PKG_INTEGRATION | Integration | 🆕 Confirmed but non-functional — file reading is implemented; CSV parsing and database writes are a TODO |
| Generate Headcount Report | Report on active employee counts by department, location, employment type, and gender | PKG_REPORTING | Reporting | ✅ Confirmed |
| Generate Compensation Summary | Report on salary ranges, average salary, and compa-ratio by department and grade | PKG_REPORTING | Reporting | ✅ Confirmed |
| Generate Turnover Report | Report on employee terminations, voluntary vs involuntary, by department and time period | PKG_REPORTING | Reporting | ⚠️ Corrected — voluntary classification is case-sensitive; free-text reasons not matching exact 'VOLUNTARY' string are counted as involuntary |

---

## OUTPUT 2 — Business Process Flows

### Process: New Employee Hire
**Domain:** Employee Management
**Trigger:** HR staff initiates new hire entry in the Employee Maintenance screen
**Initiating Actor:** HR Specialist or HR Administrator

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | HR enters employee's first name, last name, hire date, department, and job title | All five fields are mandatory | Error if any field is missing: "First name and last name are required" |
| 2 | System validates the selected department is currently active | Department must exist with active status | Error if department not found or inactive |
| 3 | System validates the manager assignment, if one is provided | Manager must be an active employee; must not create a circular reporting chain (checked up to 15 levels deep) | Error if manager is inactive or chain would loop |
| 4 | System validates the selected job title is currently active | Job must exist with active status | Error if job not found or inactive |
| 5 | System checks the proposed salary against the job grade's pay band | If salary is outside the grade band, a warning is generated; salary is not blocked | `〰️ ASSUMED — manager approval of out-of-band salary is described in a comment but no approval workflow is implemented` |
| 6 | System assigns a location from the department's default location if none is specified | Location defaults to department location | No error if no location configured |
| 7 | System generates a unique employee identifier (format: EMP-NNNNNN, six-digit zero-padded) | 📌 RULE CANDIDATE: employee number format must match EMP-NNNNNN exactly | Race condition bug exists under concurrent inserts; fallback uses sequence |
| 8 | Employee record is created; employee is set to ACTIVE status with ACTIVE_FLAG = Y | 📌 RULE CANDIDATE: new employees always start ACTIVE | Duplicate number error triggers retry message |
| 9 | If a starting salary is provided, a salary record is created effective on the hire date | Salary must be positive | Error if salary ≤ 0 |
| 10 | A welcome email is queued to the new employee | Email is queued asynchronously | Notification failure is silently swallowed; hire still succeeds |
| 11 | A new direct-report notification is queued to the employee's manager | Only if a manager was specified at hire time | No notification is sent if manager is assigned after hire |
| 12 | The hire event is recorded in the employee change history | 📌 RULE CANDIDATE: all employment changes are permanently audited | Autonomous transaction — history write cannot fail the hire |

**Terminal outcomes:** Employee record created with ACTIVE status; or error message returned and no record created
**Cross-domain handoffs:** 🔗 Salary domain — PKG_PAYROLL.create_salary_record called at step 9; 🔗 Notifications domain — PKG_NOTIFICATION.send_notification called at steps 10 and 11
**Rule candidates identified:** Employee number format, always-ACTIVE initial status, salary must be positive, manager notification on direct-report assignment

---

### Process: Employee Termination
**Domain:** Employee Management
**Trigger:** HR staff initiates termination through the Employee Maintenance screen or a direct procedure call
**Initiating Actor:** HR Specialist or HR Administrator

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | System locks the employee record for exclusive update | Employee must not already be terminated | Error: "Employee [id] is already terminated" if already TERMINATED |
| 2 | All leave requests in PENDING status are automatically cancelled with reason "Auto-cancelled due to termination" | 📌 RULE CANDIDATE: pending leave auto-cancels on termination | Note: leave balance PENDING field is NOT decremented — balance record becomes inconsistent |
| 3 | APPROVED leave requests are NOT cancelled | 📌 RULE CANDIDATE (implied): approved future leave remains in the system after termination | This is a defect — approved future leave that will never be taken remains on the record |
| 4 | Employee status is set to TERMINATED; active flag set to N; termination date and reason are recorded | 📌 RULE CANDIDATE: physical deletion of employee records is forbidden | |
| 5 | All active salary records are end-dated to the termination date | |  |
| 6 | All active pay elements (deductions, benefits) are end-dated to the termination date | | |
| 7 | The termination is recorded in the employee change history | | |
| 8 | Manager receives an email notification of the termination | Only if the employee had a manager assigned | |
| 9 | `〰️ ASSUMED — final pay calculation should occur` | Benefits system (COBRA) integration, security access revocation, and final pay calculation are all documented as TODO items in the code | Not implemented — noted in source as missing |

**Terminal outcomes:** Employee record in TERMINATED status with all pay records closed; manager notified
**Cross-domain handoffs:** 🔗 Leave domain — LEAVE_REQUESTS directly updated (bypassing PKG_LEAVE, causing balance inconsistency); 🔗 Notifications domain — manager notification queued
**Rule candidates identified:** Cannot terminate already-terminated employee; pending leave auto-cancels; physical deletion forbidden; all pay records close on termination date

---

### Process: Employee Transfer
**Domain:** Employee Management
**Trigger:** HR staff calls the transfer procedure with a new department and optional job/manager/location
**Initiating Actor:** HR Specialist or HR Administrator

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | System locks the employee record | Employee must be in ACTIVE status | Error: "Cannot transfer non-active employee" if TERMINATED, ON_LEAVE, or SUSPENDED |
| 2 | New department is validated as active | | Error if department not found or inactive |
| 3 | Job title defaults to the employee's current job if none is provided | | |
| 4 | Location defaults to the employee's current location if none is provided | | |
| 5 | Manager is validated if a new one is specified; circular chain check is run | Circular chain check traverses up to 15 levels | Error if new manager is inactive or creates a circular chain |
| 6 | Employee record is updated with the new department, job, manager, and location | | Lock contention error if another user holds the record (NOWAIT) |
| 7 | Transfer is recorded in employee change history | | |

**Terminal outcomes:** Employee record updated; history record written; or error if employee is not active / department invalid / circular chain detected
**Rule candidates identified:** Only ACTIVE employees can be transferred; row locking with immediate failure (no wait); job and location default to current values if not specified

---

### Process: Monthly Leave Accrual (Batch)
**Domain:** Leave Management
**Trigger:** Scheduled batch job, typically on the 1st of each month
**Initiating Actor:** System (DBMS_SCHEDULER)

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | System selects all active employees | EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y' | |
| 2 | For each employee, for each monthly-frequency accrual leave type, check if employee meets minimum tenure | Days since hire must be >= leave type's MIN_TENURE_DAYS | Employee is skipped for this leave type if tenure not met |
| 3 | Check current leave balance against maximum allowed | If adding the accrual rate would exceed MAX_BALANCE, accrue only enough to reach the cap | 0 days accrued if already at maximum |
| 4 | Increment the ACCRUED field in leave balances by the accrual amount | If no balance record exists for this year, create one first | |
| 5 | Write an accrual log entry | | |
| 6 | Commit every 100 employees processed | | Partial commit means failure leaves some employees accrued and others not |

**Terminal outcomes:** All qualifying employees have leave balances incremented; accrual log entries created
**Rule candidates identified:** PTO accrues 1.25 days/month (max 20); SICK accrues 0.833 days/month (max 10); COMP and FMLA do not accrue; accrual only for employees meeting minimum tenure

---

### Process: Leave Request Submission and Approval
**Domain:** Leave Management
**Trigger:** Employee submits a leave request through the Leave Management screen
**Initiating Actor:** Employee

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | System verifies the employee is active | Employee must be ACTIVE | Error: "Employee not found or not active" |
| 2 | System validates the leave type is active | | Error: "Invalid leave type" |
| 3 | System checks employee has met the minimum tenure for this leave type | Days since hire >= leave type's MIN_TENURE_DAYS | Error: "Minimum tenure of [N] days not met" — COMP requires 90 days; FMLA requires 365 days |
| 4 | System validates that the start date is not after the end date | | Error: "Start date must be before or equal to end date" |
| 5 | System checks that the start date is not more than 5 calendar days in the past | 📌 RULE CANDIDATE: maximum backdating is 5 calendar days | Error: "Cannot submit leave requests more than 5 days in the past" |
| 6 | System calculates the number of business days (excluding weekends and public holidays specific to the employee's location) | Half-day requests are always 0.5 days, regardless of business day calculation | Error: "No business days in the selected range" if result is zero |
| 7 | System checks for overlapping requests in PENDING or APPROVED status | | Error: "Leave request overlaps with an existing request" |
| 8 | System checks available balance if the leave type is accrual-based | Balance check: OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING >= requested days | Error: "Insufficient leave balance. Available: [n], Requested: [n]" |
| 9 | Leave request is created in PENDING status; PENDING balance is incremented | | |
| 10a | If the leave type requires approval: manager is notified; request waits in PENDING | | |
| 10b | If the leave type does not require approval (Jury Duty, Bereavement): request is immediately auto-approved | | |

**Approval sub-flow (Step 10a continuation):**

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 11 | Manager reviews pending requests for their team | | |
| 12 | Manager approves the request | Request must still be in PENDING status | Error if already approved, rejected, or cancelled |
| 13 | PENDING balance is decremented; USED balance is incremented | | |
| 14 | Employee is notified of approval | | |

**Terminal outcomes:** Request reaches APPROVED status (and employee notified); or REJECTED (with reason); or CANCELLED before action
**Cross-domain handoffs:** 🔗 Notifications domain — manager notified on submission; employee notified on approval/rejection
**Rule candidates identified:** 5-day backdating limit; JURY and BEREAVEMENT are auto-approved; FMLA requires 365 days tenure; COMP requires 90 days tenure; balance checked only for accrual types

---

### Process: Payroll Run
**Domain:** Payroll
**Trigger:** Payroll staff creates a run for an open pay period
**Initiating Actor:** Payroll Manager

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | Staff selects an open pay period and creates a payroll run | Pay period must be in OPEN status | Error: "Cannot create run for closed period" |
| 2 | Run is created in PENDING status | | |
| 3 | Staff triggers calculation | Run must be in PENDING status (form-level check) | Form blocks calculation if not PENDING |
| 4 | System sets run status to CALCULATING | | |
| 5 | For each active employee: calculates period gross (annual salary ÷ periods per year, rounded to 2 decimal places), applies federal tax brackets, applies state flat rate, calculates FICA (6.2% up to $168,600 annual wage base), calculates Medicare (1.45% base + 0.9% above $200,000 YTD) | Processes only ACTIVE employees with ACTIVE_FLAG = 'Y' | Individual employee errors are captured and counted; processing continues |
| 6 | For each employee: deductions are applied in PRIORITY_ORDER; override amount takes precedence over flat amount which takes precedence over percentage | | |
| 7 | System commits every 50 employees | 📌 RULE CANDIDATE: partial commits mean a failed run leaves partial results in the database | |
| 8 | Run status is set to CALCULATED (or ERROR if any employee failed) | | |
| 9 | Payroll approver reviews totals | Approver needs PAYROLL APPROVE permission (distinct from VIEW) | |
| 10 | Approver approves the run | Run must be in CALCULATED status | Error: "Cannot approve run in status: [status]" |
| 11 | Run status is set to APPROVED | | |
| 12 | `〰️ ASSUMED — payment disbursement occurs` | No procedure advances APPROVED to PAID; PAID is an orphaned status | Not implemented |
| 13 | GL journal file is generated and exported to the GL_FEED_OUT directory | | |

**Terminal outcomes:** Run reaches APPROVED status; payroll can be reversed from any status; PAID status exists but is unreachable
**Rule candidates identified:** Only CALCULATED runs can be approved; both VIEW and APPROVE permissions required separately; tax and deductions stored as negative amounts; period gross = ROUND(annual ÷ periods, 2)

---

### Process: Performance Review Cycle
**Domain:** Performance
**Trigger:** HR creates a review cycle for a given year
**Initiating Actor:** HR Administrator

| Step | Description | Condition | Exception Path |
|---|---|---|---|
| 1 | HR creates a review cycle with dates; cycle starts in DRAFT status | | |
| 2 | HR opens the cycle | Cycle must be in DRAFT status | Error: "Cannot open cycle — must be in DRAFT status" |
| 3 | HR triggers bulk generation of individual review records for all active employees who have a manager | Employees with no manager (e.g. CEO) are excluded | Duplicate reviews for same employee+cycle are silently skipped |
| 4 | Each employee is notified that their review has been initiated and they should complete their self-assessment | | |
| 5 | Employee submits their self-assessment | Review must be in NOT_STARTED status (SELF_REVIEW status cannot be reached through normal flow) | Error if review not in correct status |
| 6 | Manager is notified that the self-assessment is ready for review | | |
| 7 | Manager records their rating (1.0–5.0) and written assessment | Rating must be between 1.0 and 5.0 inclusive; no prior status check prevents overwriting | Error: "Rating must be between 1.0 and 5.0" |
| 8 | Rating label is assigned: 4.5+ = Exceptional; 3.5–4.4 = Exceeds Expectations; 2.5–3.4 = Meets Expectations; 1.5–2.4 = Needs Improvement; below 1.5 = Unsatisfactory | | |
| 9 | Review status is set to COMPLETED; employee is notified | | |
| 10 | Employee acknowledges the review (optionally adds comments) | Review must be in COMPLETED status | |
| 11 | Review status is set to ACKNOWLEDGED | | |
| 12 | HR closes the cycle | | |

**Terminal outcomes:** All reviews reach ACKNOWLEDGED or remain stuck at COMPLETED if employee never acknowledges
**Rule candidates identified:** Only active managed employees get reviews; rating range 1.0–5.0; exact boundary for each label (4.5/3.5/2.5/1.5); no meeting scheduling in current system

---

## OUTPUT 3 — Business Rules Catalog

| ID | Rule | Domain | Type | Severity | Confidence | Source |
|---|---|---|---|---|---|---|
| BR-01 | An employee's first name and last name are both required when creating an employee record | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.create_employee |
| BR-02 | An employee's department must exist and be currently active at the time of hire, transfer, or rehire | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.validate_dept |
| BR-03 | An employee's manager (if assigned) must be an active employee — an inactive or terminated person cannot be assigned as a manager | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.validate_manager |
| BR-04 | A reporting chain cannot be circular — if assigning a manager would create a loop at any depth up to 15 levels, the assignment is rejected | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.validate_manager |
| BR-05 | An employee's job title must exist and be currently active | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.create_employee |
| BR-06 | An employee's salary is checked against the job grade's pay band; a salary outside the band generates a warning but does not block the record | Employee | Soft Constraint | Medium | ✅ HIGH | PKG_EMPLOYEE.create_employee |
| BR-07 | If no location is specified when hiring an employee, the employee inherits the location of their assigned department | Employee | Soft Constraint | Low | ✅ HIGH | PKG_EMPLOYEE.create_employee |
| BR-08 | Employee numbers are formatted as EMP- followed by exactly 6 zero-padded digits (example: EMP-001234) | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.generate_emp_number; PKG_VALIDATION.validate_emp_number_format |
| BR-09 | First name and last name are stored in all-uppercase; email address is stored in all-lowercase | Employee | Soft Constraint | Low | ✅ HIGH | PKG_EMPLOYEE.create_employee |
| BR-10 | New employees are always created with ACTIVE employment status and an active flag | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.create_employee; TRG_EMP_BEFORE_INSERT |
| BR-11 | An email address must be unique among all employees with an active flag of Y (case-insensitive) | Employee | Hard Constraint | High | ✅ HIGH | TRG_EMP_BEFORE_INSERT |
| BR-12 | A hire date may not be set more than 180 days in the future (database enforcement) | Employee | Hard Constraint | High | ✅ HIGH | TRG_EMP_BEFORE_INSERT |
| BR-13 | A hire date may not be set more than 90 days in the future (screen enforcement) | Employee | Hard Constraint | High | ✅ HIGH | HRMS_EMPLOYEE form WHEN-VALIDATE-ITEM |
| BR-14 | Only active employees can be transferred; employees who are terminated, suspended, or on leave cannot be transferred | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.transfer_employee |
| BR-15 | A terminated employee cannot be directly reactivated by changing their status; the formal rehire procedure must be used | Employee | Hard Constraint | High | ✅ HIGH | TRG_EMP_BEFORE_UPDATE |
| BR-16 | Direct physical deletion of employee records is prohibited; records must be deactivated via termination or by setting the active flag to N | Employee | Hard Constraint | High | ✅ HIGH | TRG_EMP_INSTEAD_OF_DELETE |
| BR-17 | When an employee is terminated, all their pending leave requests are automatically cancelled with the reason "Auto-cancelled due to termination" | Employee / Leave | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.terminate_employee |
| BR-18 | When an employee is terminated, all their active salary records and active pay elements are end-dated to the termination date | Employee / Payroll | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.terminate_employee |
| BR-19 | A terminated employee's manager is notified by email when the termination is processed | Employee | Soft Constraint | Medium | ✅ HIGH | PKG_EMPLOYEE.terminate_employee |
| BR-20 | When an employee is rehired, their hire date is overwritten with the new rehire date; the original hire date and all prior tenure calculations are discarded | Employee | Hard Constraint | High | ✅ HIGH | PKG_EMPLOYEE.rehire_employee |
| BR-21 | An employee's salary percentage change is calculated as ROUND(((new salary − old salary) ÷ old salary) × 100, 2) — only when the prior salary is greater than zero | Payroll | Threshold | Medium | ✅ HIGH | PKG_EMPLOYEE.promote_employee |
| BR-22 | Organisational chart traversal is limited to a maximum depth of 10 levels by default (configurable to a maximum of 15) | Employee | Threshold | Low | ✅ HIGH | PKG_EMPLOYEE.get_org_chart |
| BR-23 | A salary record must have a positive value (greater than zero) | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_salary_record |
| BR-24 | All salary records are stored on an annual basis regardless of the employee's pay frequency | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_salary_record |
| BR-25 | When a new salary record is created, the previous active salary record for that employee is end-dated to one day before the new record's effective date | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.create_salary_record |
| BR-26 | Monthly pay periods: the pay date is the last calendar day of the month, moved to the preceding Friday if the last day falls on a Saturday or Sunday | Payroll | Threshold | High | ✅ HIGH | PKG_PAYROLL.create_pay_periods |
| BR-27 | Biweekly pay periods: each period is exactly 14 days ending on a Friday; the pay date is 5 calendar days after the period ends | Payroll | Threshold | High | ✅ HIGH | PKG_PAYROLL.create_pay_periods |
| BR-28 | Period gross pay is calculated as ROUND(annual salary ÷ periods per year, 2), where periods per year is 52 (weekly), 26 (biweekly), 24 (semimonthly), or 12 (monthly) | Payroll | Threshold | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-29 | Federal income tax is calculated by annualising the period income, applying the standard deduction (USD 14,600 for single/married separate; USD 29,200 for married filing jointly), subtracting USD 4,300 per withholding allowance, applying 2024 progressive brackets, then dividing back to the period amount | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_federal_tax |
| BR-30 | Federal tax brackets (2024, Single/Married Separate): 10% up to USD 11,600; 12% on USD 11,601–47,150; 22% on USD 47,151–100,525; 24% on USD 100,526–191,950; 32% on USD 191,951–243,725; 35% on USD 243,726–609,350; 37% above USD 609,350 | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_federal_tax |
| BR-31 | Federal tax brackets (2024, Married Filing Jointly): 10% up to USD 23,200; 12% on USD 23,201–94,300; 22% on USD 94,301–201,050; 24% on USD 201,051–383,900; 32% on USD 383,901–487,450; 35% on USD 487,451–731,200; 37% above USD 731,200 | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_federal_tax |
| BR-32 | Head-of-Household filers receive zero federal income tax withholding due to a missing code branch | Payroll | Compliance | Critical | ⚠️ LOW — defect, not policy | PKG_PAYROLL.calculate_federal_tax |
| BR-33 | Social Security tax rate is 6.2% of gross wages; no Social Security tax is withheld once year-to-date gross earnings exceed USD 168,600 | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_fica |
| BR-34 | Medicare base rate is 1.45% of all gross wages with no annual cap | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_medicare |
| BR-35 | An additional Medicare rate of 0.9% applies to the portion of gross wages that pushes year-to-date earnings above USD 200,000; only the amount above the threshold is taxed at the additional rate | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_medicare |
| BR-36 | The additional Medicare 0.9% rate uses a single USD 200,000 threshold for all filing statuses; the IRS threshold for married filing jointly (USD 250,000) is not applied | Payroll | Compliance | High | ⚠️ LOW — defect; MFJ employees over-withheld between $200k–$250k | PKG_PAYROLL.calculate_medicare |
| BR-37 | State income tax rates (flat, simplified): CA 7.25%; NY 6.85%; TX 0%; FL 0%; WA 0%; IL 4.95%; PA 3.07%; OH 4.00%; NJ 6.37%; MA 5.00%; all other states default 5.00% | Payroll | Compliance | High | ✅ HIGH | PKG_PAYROLL.calculate_state_tax |
| BR-38 | State tax does not apply allowances or filing status adjustments; W-4 state withholding configuration is accepted but never used in the calculation | Payroll | Compliance | High | ⚠️ LOW — defect | PKG_PAYROLL.calculate_state_tax |
| BR-39 | If no tax information record exists for an employee, default withholding is Single filing status with zero allowances | Payroll | Soft Constraint | Medium | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-40 | Deductions are applied in priority order (lowest number first); an override amount takes precedence over a flat amount, which takes precedence over a percentage of gross | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-41 | A deduction or benefit element applies only if its effective date is on or before the pay period end date AND either its end date is null or its end date is on or after the pay period start date | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-42 | Tax and deduction amounts are stored as negative values in the payroll details table; earning amounts are stored as positive values | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.calculate_employee_pay |
| BR-43 | Only a run in CALCULATED status can be approved | Payroll | Hard Constraint | High | ✅ HIGH | PKG_PAYROLL.approve_payroll |
| BR-44 | A payroll run can be reversed from any status (no prior status check); the stated reason for reversal is not recorded anywhere in the system | Payroll | Hard Constraint | Medium | ⚠️ LOW — reversal reason acceptance without storage is a defect | PKG_PAYROLL.reverse_payroll |
| BR-45 | Year-to-date earnings shown on payslips are always zero; this is an unimplemented placeholder | Payroll | Hard Constraint | Critical | ✅ HIGH — confirmed defect | PKG_PAYROLL.get_payslip |
| BR-46 | The default employee pay elements at enrolment are: 401(k) employee contribution 6% of gross (pre-tax); medical USD 250/period (pre-tax); dental USD 45/period (pre-tax); vision USD 15/period (pre-tax); life insurance USD 25/period (not pre-tax); HSA USD 150/period (pre-tax) | Payroll | Soft Constraint | Medium | ✅ HIGH | seed data / PAY_ELEMENTS |
| BR-47 | Job grade salary bands: Grade 1 (Entry Level) USD 35,000–55,000; Grade 2 (Junior) USD 45,000–70,000; Grade 3 (Mid-Level) USD 60,000–90,000; Grade 4 (Senior) USD 80,000–120,000; Grade 5 (Lead) USD 95,000–145,000; Grade 6 (Manager) USD 110,000–170,000; Grade 7 (Senior Manager) USD 130,000–200,000; Grade 8 (Director) USD 160,000–250,000; Grade 9 (VP) USD 200,000–350,000; Grade 10 (C-Suite) USD 300,000–600,000 | Payroll | Threshold | High | ✅ HIGH | JOB_GRADES seed data |
| BR-48 | The company's fiscal year begins on October 1; October–December of a given calendar year belongs to the fiscal year of the following calendar year (e.g. October 2024 is in FY2025) | Cross-cutting | Threshold | Medium | ✅ HIGH | PKG_COMMON.get_fiscal_year |
| BR-49 | Fiscal quarters: October–December = Q1; January–March = Q2; April–June = Q3; July–September = Q4 | Cross-cutting | Threshold | Low | ✅ HIGH | PKG_COMMON.get_fiscal_quarter |
| BR-50 | A leave request may not have a start date earlier than 5 calendar days before today | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-51 | A half-day leave request is always counted as exactly 0.5 days regardless of the number of business days in the selected range | Leave | Threshold | Medium | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-52 | Leave requests cannot overlap with any existing PENDING or APPROVED request for the same employee | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.check_leave_overlap |
| BR-53 | For accrual-based leave types, an employee must have sufficient available balance (Opening Balance + Accrued − Used + Adjustment − Pending) to cover the requested days | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-54 | Leave types that do not require approval (Jury Duty, Bereavement) are automatically approved at the moment of submission | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.submit_leave_request |
| BR-55 | A leave request can only be approved if it is currently in PENDING status | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.approve_leave_request |
| BR-56 | A leave request can only be rejected if it is currently in PENDING status | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.reject_leave_request |
| BR-57 | A leave request can be cancelled only if it is in PENDING or APPROVED status; a cancelled PENDING request releases the pending balance; a cancelled APPROVED request restores the used balance | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.cancel_leave_request |
| BR-58 | Available leave balance = Opening Balance + Accrued − Used + Adjustment − Pending | Leave | Threshold | High | ✅ HIGH | LEAVE_BALANCES virtual column |
| BR-59 | PTO accrues at 1.25 days per month to a maximum balance of 20 days; maximum carryover to next year is 5 days; carryover expires 3 months into the new year | Leave | Threshold | High | ✅ HIGH | LEAVE_TYPES seed data |
| BR-60 | Sick Leave accrues at 0.833 days per month to a maximum balance of 10 days; maximum carryover is 10 days with no expiry date | Leave | Threshold | High | ✅ HIGH | LEAVE_TYPES seed data |
| BR-61 | Compensatory Time does not accrue; requires a minimum of 90 days of employment; no carryover | Leave | Threshold | High | ✅ HIGH | LEAVE_TYPES seed data |
| BR-62 | Family Medical Leave does not accrue; requires a minimum of 365 days of employment (approximately 1 year); no carryover | Leave | Threshold | High | ✅ HIGH | LEAVE_TYPES seed data |
| BR-63 | Business days exclude weekends (Saturday and Sunday) and public holidays from the HOLIDAYS table; holidays may be global (affecting all locations) or location-specific | Leave | Hard Constraint | High | ✅ HIGH | PKG_LEAVE.calculate_business_days; PKG_VALIDATION.is_business_day |
| BR-64 | Year-end carryover amount is capped at the leave type's maximum carryover allowance; the carryover expiry date is calculated as January 1 of the new year plus the leave type's carryover expiry number of months | Leave | Threshold | High | ✅ HIGH | PKG_LEAVE.process_carryover |
| BR-65 | All performance review cycles begin as DRAFT; only DRAFT cycles can be opened; opening is a one-way transition | Performance | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.open_review_cycle |
| BR-66 | Individual performance review records are created only for active employees who have a manager assigned; employees at the top of the hierarchy (no manager) are excluded | Performance | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.generate_reviews_for_cycle |
| BR-67 | A self-assessment can be submitted when the review is in NOT_STARTED or SELF_REVIEW status (SELF_REVIEW is currently unreachable — only NOT_STARTED is functionally accessible) | Performance | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.submit_self_assessment |
| BR-68 | An overall performance rating must be between 1.0 and 5.0 inclusive | Performance | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.submit_manager_review; PERFORMANCE_REVIEWS DDL |
| BR-69 | Rating labels: score ≥ 4.5 = Exceptional; ≥ 3.5 and < 4.5 = Exceeds Expectations; ≥ 2.5 and < 3.5 = Meets Expectations; ≥ 1.5 and < 2.5 = Needs Improvement; ≥ 1.0 and < 1.5 = Unsatisfactory | Performance | Threshold | High | ✅ HIGH | PKG_PERFORMANCE.submit_manager_review |
| BR-70 | A performance review can be acknowledged only when it is in COMPLETED status | Performance | Hard Constraint | High | ✅ HIGH | PKG_PERFORMANCE.acknowledge_review |
| BR-71 | Goal progress reaching 100% automatically sets the goal status to COMPLETED; any progress above 0% and below 100% sets status to IN_PROGRESS; 0% leaves status unchanged | Performance | Soft Constraint | Low | ✅ HIGH | PKG_PERFORMANCE.update_goal_progress |
| BR-72 | An employee session expires 30 minutes after login regardless of whether the user is actively working; there is no mechanism to extend a session | Security | Threshold | High | ✅ HIGH | PKG_SECURITY.is_session_valid |
| BR-73 | Only employees in ACTIVE employment status can log in | Security | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.authenticate |
| BR-74 | Login username is matched against the employee's email address (case-insensitive) | Security | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.authenticate; HRMS_LOGIN form |
| BR-75 | Passwords are not verified during authentication; any value is accepted for any active user | Security | Hard Constraint | Critical | ⚠️ LOW — confirmed defect; not intended policy | PKG_SECURITY.authenticate |
| BR-76 | Password complexity rules (applied at change time only): minimum 8 characters; must contain at least one uppercase letter; must contain at least one digit; no maximum length; no special character requirement | Security | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.change_password |
| BR-77 | Password changes are validated but not actually applied; the update to the credentials table is not implemented | Security | Hard Constraint | Critical | ⚠️ LOW — confirmed defect | PKG_SECURITY.change_password |
| BR-78 | Employees at grade 8 or above (Director, VP, C-Suite) have full access to all modules and actions | Security | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.has_permission |
| BR-79 | Employees at grade 5–7 (Lead, Manager, Senior Manager) can view all modules | Security | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.has_permission |
| BR-80 | All employees can submit and view their own leave requests and view their own employee profile | Security | Hard Constraint | High | ✅ HIGH | PKG_SECURITY.has_permission |
| BR-81 | Payroll module requires explicit permission to view; payroll approval requires a separate, higher-level permission check | Security | Hard Constraint | High | ✅ HIGH | HRMS_PAYROLL form; PKG_SECURITY.has_permission |
| BR-82 | Audit records are retained for a default of 365 days before being purged | Cross-cutting | Compliance | Medium | ✅ HIGH | PKG_AUDIT.purge_old_records |
| BR-83 | System parameters marked as non-editable (EDITABLE_FLAG = N) cannot be changed through the application; only editable parameters can be updated | Cross-cutting | Hard Constraint | Medium | ✅ HIGH | PKG_COMMON.set_param |
| BR-84 | Notifications are queued asynchronously and delivered in batches of up to 50 per processing cycle; failed notifications are retried up to a maximum of 3 attempts | Notifications | SLA | Medium | ✅ HIGH | PKG_NOTIFICATION.process_queue; PKG_NOTIFICATION.retry_failed |
| BR-85 | The GL journal separates earning amounts (debit column) from deduction and tax amounts (credit column) in a pipe-delimited format; only payroll elements with a GL account code are included | Integration | Hard Constraint | High | ✅ HIGH | PKG_INTEGRATION.generate_gl_journal |
| BR-86 | Compa-ratio for an employee is calculated as: (employee's current salary ÷ grade midpoint) × 100, where grade midpoint = (minimum salary + maximum salary) ÷ 2 | Reporting | Threshold | Medium | ✅ HIGH | VW_EMPLOYEE_COMPENSATION; PKG_REPORTING.compensation_summary |
| BR-87 | Turnover percentage is calculated as: (number of terminations in period ÷ number of employees hired on or before the end of the period) × 100; terminations with TERMINATION_REASON = 'VOLUNTARY' (exact case match) are classified as voluntary; all others including null are classified as involuntary | Reporting | Threshold | Medium | ✅ HIGH | PKG_REPORTING.turnover_report |

---

## OUTPUT 4 — Stakeholder & Role Matrix

| Technical Role | Plain English Name | Responsibilities | Actions They Can Trigger | Data They Can Access | Domain(s) Active In |
|---|---|---|---|---|---|
| GRADE_1–GRADE_4 (Grades 1–4) | Staff Employee | Day-to-day operational work. Can manage their own leave requests and view their own employment information. | Submit leave requests; cancel own leave requests; view own leave balance; complete own self-assessment; acknowledge own performance review; update own performance goals; change own password | Own employee record; own leave balances and requests; own payslip (via their manager's review); own performance review and goals | Leave, Performance |
| GRADE_5–GRADE_7 (Grades 5–7) | Line Manager / Senior Manager | Manage a team. Responsible for approving team leave, completing performance reviews, and viewing operational reports. Can view all modules. | All Staff actions plus: approve/reject team leave requests; submit manager performance reviews; generate team performance reports; view team calendar; access all reporting functions | All modules in view mode; team leave requests; team performance reviews; own payslip data | Employee, Leave, Performance, Reporting |
| GRADE_8 (Grade 8) | Director | Departmental leadership. Full system access. | All Manager actions plus: all write/edit/approve actions across all modules | Full access to all data across all modules | All |
| GRADE_9–GRADE_10 (Grades 9–10) | VP / C-Suite Executive | Corporate leadership. Full system access including payroll approval. | All Director actions; payroll run approval | Full access including compensation data across all departments | All |
| PAYROLL_ROLE (Payroll-permissioned staff) | Payroll Administrator | Process payroll runs for each pay period. Requires explicit PAYROLL VIEW permission from grade-based check. | Create payroll runs; trigger payroll calculation; generate pay register; generate GL journal; export benefits feed | Pay periods; payroll runs; payroll details; salary records | Payroll, Integration |
| PAYROLL_APPROVER | Payroll Approver | Approve completed payroll runs for disbursement. Requires PAYROLL APPROVE permission (separate check). | Approve payroll runs | Payroll run totals; calculated details | Payroll |
| HR_ROLE (HR-assigned staff) | HR Specialist | Manage employee records, leave administration, and reporting. Access granted through grade (typically Grade 5+). | Create, update, and transfer employees; initiate and manage leave adjustments; run HR reports; initialize leave balances | Employee records; leave balances; leave requests across all employees; HR reports | Employee, Leave, Reporting |
| SYSTEM (batch context) | Automated Batch Process | Runs scheduled jobs. Not a human user — executes with system privileges. | Run monthly leave accrual; process year-end carryover; expire carryover; process notification queue; retry failed notifications; generate GL journal; export benefits feed | All operational data | All |
| `⚠️ LOW — no gated actions found` | Anonymous / Unauthenticated | No business actions available. | Login attempt only | None | Security |

---

## OUTPUT 5 — Value Stream Maps

### Value Stream: Employee Lifecycle
**Trigger:** HR staff creates a new employee record
**Actors Involved:** HR Specialist, Line Manager, Employee, System
**Terminal Outcomes:** ACTIVE (ongoing employment); TERMINATED (employment ends); `〰️ ASSUMED — ON_LEAVE and SUSPENDED are defined terminal/transient states but no flow reaches them`

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Hiring | HR Specialist | Create employee record with job, department, salary, and manager | All mandatory fields provided; department and job are active | Employee record created; welcome email sent to employee; notification sent to manager | Value-Adding |
| 2 | Active Employment | Employee / Manager / HR | Work, manage performance, take leave, receive pay | Employee status is ACTIVE | Employment continues; changes recorded in history | Value-Adding |
| 3 | Transfer | HR Specialist | Reassign employee to a new department, job, or manager | Employee must be ACTIVE | Dept, job, manager, location updated; history written | Value-Adding |
| 4 | Promotion | HR Specialist | Change job title and salary simultaneously | Employee record must exist (no active-status check — defect) | Job and salary updated; history written | Value-Adding |
| 5 | Termination | HR Specialist | Record termination date and reason; close salary and pay elements | Employee must not already be TERMINATED | Status = TERMINATED; ACTIVE_FLAG = N; pending leave cancelled; manager notified | Exception |
| 6 | Rehire | HR Specialist | Restore a terminated employee with a new hire date, department, and salary | `⚠️ LOW — rehire procedure is non-functional due to trigger conflict (DISC-001)` | `〰️ ASSUMED — would restore ACTIVE status and create new salary record` | Value-Adding |

**Handoff Points:**
- Stage 1 → Stage 2: HR completes the record; payroll creates the first salary record
- Stage 5 → End: PKG_EMPLOYEE directly updates leave requests (bypassing PKG_LEAVE balance logic)

**Wait States:**
- Stage 2: Ongoing — no time-bound trigger to advance

**External Dependencies:**
- Stage 1: PKG_PAYROLL.create_salary_record — creates first salary record on hire date
- Stage 5: Benefits/COBRA integration, security access revocation, final pay calculation — all documented as TODO; not implemented

**States Accounted For:**
- ACTIVE → Stage 2
- TERMINATED → Stage 5

**Unaccounted States:**
- ON_LEAVE: No procedure or trigger sets this status; state is unreachable through normal operations
- SUSPENDED: No procedure or trigger sets this status; state is unreachable through normal operations

---

### Value Stream: Payroll Processing
**Trigger:** Payroll Administrator selects an open pay period and creates a run
**Actors Involved:** Payroll Administrator, Payroll Approver, System
**Terminal Outcomes:** APPROVED (payroll ready for disbursement); REVERSED (payroll voided); ERROR (calculation failed for one or more employees)

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Pay Period Setup | System | Create pay calendar (monthly or biweekly) for the year; set all periods to OPEN | HR/Payroll admin triggers year setup | 12 monthly or ~26 biweekly periods created; all OPEN | Value-Adding |
| 2 | Run Creation | Payroll Administrator | Create a payroll run for the current pay period | Pay period must be OPEN | Run created in PENDING status | Value-Adding |
| 3 | Calculation | System | Calculate gross, taxes, and deductions for all active employees | Run must be in PENDING status | Run advances to CALCULATING then CALCULATED (or ERROR) | Value-Adding |
| 4 | Review | Payroll Administrator | Review run totals, employee counts, and error records | Run is CALCULATED or ERROR | Decision to approve or correct | Verification |
| 5 | Approval | Payroll Approver | Formally approve the run | Run must be in CALCULATED status; approver needs PAYROLL APPROVE permission | Run status = APPROVED | Approval Gate |
| 6 | Disbursement | `〰️ ASSUMED` | Distribute net pay to employees | `〰️ ASSUMED — PAID status exists but no procedure advances from APPROVED to PAID` | `〰️ ASSUMED — pay distributed` | Value-Adding |
| 6a | Reversal | Payroll Approver / HR | Void a payroll run from any status | No status pre-check — any run can be reversed | Run and all detail lines marked REVERSED; reason not stored | Exception |

**Handoff Points:**
- Stage 5 → Stage 6: No automated handoff; PAID status is orphaned
- Stage 3 → Integration: After approval, GL journal is exported for Oracle Financials

**Wait States:**
- Stage 4: Manual review period with no SLA enforced

**External Dependencies:**
- Post-Stage 5: PKG_INTEGRATION.generate_gl_journal — writes journal file to GL_FEED_OUT directory for Oracle Financials import

**States Accounted For:**
- OPEN (PAY_PERIODS) → Stage 1
- PENDING (PAYROLL_RUNS) → Stage 2
- CALCULATING → Stage 3 (internal transition)
- CALCULATED → Stage 4
- ERROR → Stage 4 (exception path)
- APPROVED → Stage 5

**Unaccounted States:**
- PAID: No procedure sets this status; the payroll lifecycle has no implemented payment step
- PROCESSING (PAY_PERIODS): No procedure sets pay period to PROCESSING; only OPEN and CLOSED are used
- REVERSED (PAY_PERIODS): No procedure sets a pay period to REVERSED; only PAYROLL_RUNS has a reverse function

---

### Value Stream: Leave Request
**Trigger:** Employee submits a leave request through the Leave Management screen
**Actors Involved:** Employee, Line Manager, System
**Terminal Outcomes:** APPROVED (leave granted); REJECTED (leave denied); CANCELLED (leave withdrawn); TAKEN (leave occurred — currently an unreachable state in the system)

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Submission | Employee | Select leave type, dates, and half-day option; submit request | Employee is ACTIVE; leave type is active; tenure requirement met; dates valid; no overlap; sufficient balance (if accrual type) | Request created in PENDING; PENDING balance incremented; manager notified | Value-Adding |
| 2 | Pending Review | Manager | Review leave request via the Pending Approvals tab | Request is in PENDING status | Manager decides to approve or reject | Wait-Queue |
| 3a | Approval | Manager | Approve the request | Request must be PENDING | Status = APPROVED; PENDING balance decremented; USED balance incremented; employee notified | Value-Adding |
| 3b | Rejection | Manager | Reject the request with a reason | Request must be PENDING | Status = REJECTED; PENDING balance released; employee notified | Exception |
| 4 | Cancellation | Employee | Cancel a pending or approved request | Request must be PENDING or APPROVED | Status = CANCELLED; balance restored; `⚠️ LOW — manager is not notified of cancellation` | Exception |
| 5 | Leave Taken | System | `〰️ ASSUMED — mark leave as actually taken` | `〰️ ASSUMED — TAKEN status would be set when the leave dates pass` | `〰️ ASSUMED — TAKEN status` | Value-Adding |

**Handoff Points:**
- Stage 1 → Stage 2: System queues notification to manager's approvals queue
- Auto-approval (Jury Duty, Bereavement): Stages 1 and 3a merge; request is immediately approved

**Wait States:**
- Stage 2: No SLA rule in business rules catalog for how long a manager has to respond to a pending leave request

**External Dependencies:**
- None (all internal)

**States Accounted For:**
- PENDING → Stage 1/2
- APPROVED → Stage 3a
- REJECTED → Stage 3b
- CANCELLED → Stage 4

**Unaccounted States:**
- TAKEN: No procedure or trigger in the system sets STATUS = 'TAKEN'; approved leave remains APPROVED indefinitely after the dates have passed

---

### Value Stream: Performance Review
**Trigger:** HR creates and opens a review cycle for the year
**Actors Involved:** HR Administrator, Employee, Line Manager, System
**Terminal Outcomes:** ACKNOWLEDGED (review complete); COMPLETED (manager done but employee not yet acknowledged); `〰️ ASSUMED — CALIBRATION stage exists in schema but no procedures implement it`

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Cycle Creation | HR Administrator | Create review cycle with dates and due dates | — | Cycle in DRAFT status | Value-Adding |
| 2 | Cycle Opening | HR Administrator | Open the cycle for employees | Cycle must be in DRAFT status | Cycle status = OPEN | Handoff |
| 3 | Review Generation | System | Bulk-create individual review records for all active employees with a manager | Cycle is OPEN | Reviews created in NOT_STARTED; employees notified | Value-Adding |
| 4 | Self-Assessment | Employee | Complete and submit self-evaluation | Review is in NOT_STARTED status | Status = MANAGER_REVIEW; manager notified | Value-Adding |
| 5 | Manager Review | Manager | Record rating (1.0–5.0) and written assessment | Review is in MANAGER_REVIEW status (`〰️ ASSUMED — no actual check enforced`) | Status = COMPLETED; rating label assigned; employee notified | Verification |
| 6 | Employee Acknowledgement | Employee | Read review and submit any comments | Review must be in COMPLETED status | Status = ACKNOWLEDGED | Value-Adding |
| 7 | Cycle Closure | HR Administrator | Close the review cycle | — | Cycle status = CLOSED | Handoff |

**Handoff Points:**
- Stage 3 → Stage 4: Each employee receives an email prompting self-assessment
- Stage 4 → Stage 5: Manager receives email when self-assessment is submitted
- Stage 5 → Stage 6: Employee receives email when manager review is complete

**Wait States:**
- Stage 4: Employee self-assessment — no automated reminder; no time-bound SLA in business rules catalog
- Stage 5: Manager review — MANAGER_REVIEW_DUE date stored in cycle but not enforced by any procedure

**External Dependencies:**
- None (all internal)

**States Accounted For (REVIEW_CYCLES):**
- DRAFT → Stage 1
- OPEN → Stage 2/3
- CLOSED → Stage 7

**Unaccounted States (REVIEW_CYCLES):**
- IN_PROGRESS: No procedure sets this status; only OPEN and CLOSED are used by procedures
- CALIBRATION: No procedure sets this status; CALIBRATION_DUE column and CALIBRATED_RATING column exist in schema but no calibration workflow is implemented

**States Accounted For (PERFORMANCE_REVIEWS):**
- NOT_STARTED → Stage 3/4
- MANAGER_REVIEW → Stage 4/5
- COMPLETED → Stage 5/6
- ACKNOWLEDGED → Stage 6

**Unaccounted States (PERFORMANCE_REVIEWS):**
- SELF_REVIEW: submit_self_assessment accepts this status as input but no procedure sets it; functionally unreachable
- MEETING_SCHEDULED: No procedure sets this status; column exists in schema only

---

### Value Stream: User Session
**Trigger:** Employee opens the HRMS Login screen and enters credentials
**Actors Involved:** Employee, System
**Terminal Outcomes:** CLOSED (explicit logout); EXPIRED (30-minute timeout elapsed)

| # | Stage Name | Actor | Business Action | Entry Condition | Exit Output | Stage Type |
|---|---|---|---|---|---|---|
| 1 | Login Attempt | Employee | Enter username (email) and password | Employee must be ACTIVE | Session created with ACTIVE status; session ID stored; employee context loaded | Value-Adding |
| 2 | Active Session | Employee | Use HRMS modules | Session is ACTIVE and within 30 minutes of login time | All module operations available based on grade permissions | Value-Adding |
| 3a | Explicit Logout | Employee | Click logout or close form | Session is ACTIVE | Session status = CLOSED; logout time recorded | Handoff |
| 3b | Session Expiry | System | Detect elapsed login time exceeds 30 minutes | 30 minutes elapsed since login regardless of activity | Session status = EXPIRED; user redirected to login | Exception |

**Unaccounted States:**
- No "locked" state despite LOCKED exception code (-20302) being defined in PKG_SECURITY; no lockout logic exists anywhere in the code

---

## OUTPUT 6 — Domain Architecture Map (Refined)

| Domain | Core Entities | Complexity | Cross-Domain Dependencies | Refinements vs Agent 1 |
|---|---|---|---|---|
| Employee Management | EMPLOYEES, EMPLOYEE_HISTORY, EMPLOYEE_DEPENDENTS, EMERGENCY_CONTACTS, JOB_TITLES, JOB_GRADES, DEPARTMENTS, LOCATIONS | High | Payroll (salary), Leave (auto-cancel on terminate), Notifications (hire/terminate events), Security (session context) | Rehire is non-functional (DISC-001); ON_LEAVE and SUSPENDED are orphaned states; EMPLOYEE_HISTORY has column mismatch with trigger (DISC-005); dual history writes on all lifecycle events (DISC-004) |
| Payroll | SALARY_RECORDS, PAY_PERIODS, PAYROLL_RUNS, PAYROLL_DETAILS, PAY_ELEMENTS, EMPLOYEE_PAY_ELEMENTS, EMPLOYEE_TAX_INFO, EMPLOYEE_BANK_ACCOUNTS, TAX_BRACKETS | High | Employee (active status, salary); Integration (GL export) | TAX_BRACKETS table exists but is never queried; PAID status is orphaned; YTD always returns zero; HEAD_OF_HOUSEHOLD gets zero federal tax; EMPLOYEE_BANK_ACCOUNTS exists but direct deposit never implemented |
| Leave Management | LEAVE_REQUESTS, LEAVE_BALANCES, LEAVE_TYPES, LEAVE_ACCRUAL_LOG, HOLIDAYS | Medium | Employee (active status, termination); Notifications (approval workflow) | TAKEN status is orphaned; termination bypasses leave balance logic causing PENDING balance leak; manager not notified of cancellations; available balance calculation diverges between view and table virtual column |
| Performance | PERFORMANCE_REVIEWS, REVIEW_CYCLES, PERFORMANCE_GOALS | Medium | Employee (active status, manager relationship); Notifications (status change emails) | SELF_REVIEW, MEETING_SCHEDULED, IN_PROGRESS, CALIBRATION are all orphaned states; top-level executives excluded from reviews; manager review has no status pre-check |
| Security | USER_SESSIONS, EMPLOYEES (via authentication) | Medium | Employee (email lookup); Audit (session events) | Password authentication is entirely unimplemented; account lockout defined in exceptions but never triggered; session timeout from login time, not last activity |
| Notifications | NOTIFICATION_QUEUE | Low | All domains (called for events) | Fully asynchronous queue model; no rate limiting; no HTML templates |
| Audit | AUDIT_LOG | Low | All domains | Triple-purpose table (audit + error log + info log); same 365-day retention for all types |
| Integration | (file-based, no dedicated tables) | Low | Payroll (GL export); Employee (benefits export) | Time import is a stub; org sync is a stub; GL omits employer-paid costs; benefits feed is legacy fixed-width ADP format; FTP credentials stored in plaintext |
| Reporting | (views + cursors) | Low | All domains | Reporting tables (RPT_*) referenced in comments but don't exist; refresh function is a stub; compa-ratio diverges between view and report |
| Cross-cutting | SYSTEM_PARAMETERS, LOOKUP_VALUES | Low | All domains | Fiscal year starts October; PKG_COMMON business days excludes holidays (unlike PKG_LEAVE); email/SSN validation diverges between client and server |

**Circular Dependency (confirmed):** PKG_EMPLOYEE.create_employee → PKG_PAYROLL.create_salary_record → PKG_EMPLOYEE.is_active. In normal execution the loop is harmless (is_active is a simple SELECT), but it means neither package can be compiled independently.

---

## OUTPUT 7 — Pain Point Report

| # | Pain Point | Domain(s) | Severity | Evidence | Automation Opportunity |
|---|---|---|---|---|---|
| PP-01 | The rehire process is entirely non-functional — a database trigger blocks the exact SQL that the rehire procedure executes. Any attempt to rehire a terminated employee fails silently or with a confusing error | Employee | High | DISC-001; TRG_EMP_BEFORE_UPDATE vs PKG_EMPLOYEE.rehire_employee | No — requires immediate code fix: the trigger must exempt the rehire procedure (via a package-level flag or AUTONOMOUS_TRANSACTION) |
| PP-02 | Passwords are never verified during login — any active employee can access the system with any password | Security | Critical | BR-75; PKG_SECURITY.authenticate | No — requires immediate security fix: USER_CREDENTIALS table integration must be completed |
| PP-03 | Password changes pass validation but do not actually update the database — the update statement is missing | Security | Critical | BR-77; PKG_SECURITY.change_password | No — requires immediate code fix |
| PP-04 | Year-to-date payslip figures are hardcoded to zero on every employee's payslip | Payroll | High | BR-45; PKG_PAYROLL.get_payslip | No — requires YTD accumulation logic to be implemented |
| PP-05 | Employees who file as Head of Household receive zero federal tax withholding due to a missing code branch | Payroll | Critical | BR-32; PKG_PAYROLL.calculate_federal_tax | No — requires immediate code fix: add HEAD_OF_HOUSEHOLD tax brackets |
| PP-06 | Tax brackets are hard-coded for 2024 and cannot be updated without a code change — the TAX_BRACKETS database table exists but is never used | Payroll | High | BR-29–BR-31; PKG_PAYROLL.calculate_federal_tax | Yes — refactor tax calculation to read from the TAX_BRACKETS table; enables annual bracket updates without code deployment |
| PP-07 | Payroll calculation uses partial commits every 50 employees — a mid-run failure leaves some employees calculated and others not, in a state that cannot be cleanly rolled back or resumed | Payroll | High | BR-44; PAY-007 | Yes — refactor using BULK COLLECT + FORALL with a single commit at the end; if Oracle version supports it, use SAVEPOINT per employee with full rollback on failure |
| PP-08 | A terminated employee's pending leave balance is not released — the termination procedure bypasses the leave cancellation logic, leaving phantom balance figures in reports | Employee / Leave | High | LEAVE-001; PKG_EMPLOYEE.terminate_employee | No — requires code fix: call PKG_LEAVE.cancel_leave_request for each pending request, or include balance decrements directly in the termination procedure |
| PP-09 | Approved future leave is not cancelled when an employee is terminated — leaves remain APPROVED in the system forever | Employee / Leave | Medium | LEAVE-002; PKG_EMPLOYEE.terminate_employee | No — requires code fix: extend termination to cancel APPROVED future leave |
| PP-10 | The TAKEN leave status is never set — all approved leave that an employee actually takes remains APPROVED forever, making leave utilisation figures inaccurate | Leave | High | LEAVE-005; LEAVE_REQUESTS.STATUS check | Yes — schedule a nightly job that sets APPROVED requests with END_DATE < SYSDATE to TAKEN |
| PP-11 | Session timeout is measured from login time, not last activity — users actively working for 31 minutes are logged out | Security | High | BR-72; PKG_SECURITY.is_session_valid | No — requires code fix: add a LAST_ACTIVITY_DATE column to USER_SESSIONS and update it on each validated request |
| PP-12 | The employee search function is vulnerable to SQL injection via last name and first name parameters — any caller bypassing the Oracle Forms interface can exploit this | Employee | High | SEC-003; PKG_EMPLOYEE.search_employees | No — requires code fix: replace string concatenation with DBMS_SQL bind variables |
| PP-13 | The AES-256 encryption key for Social Security Numbers is hard-coded in the package body source — any developer with source access can decrypt all SSN data | Security | Critical | SEC-002; PKG_SECURITY | No — requires Oracle Wallet or external key management integration |
| PP-14 | The available leave balance shown in the Leave Summary report does not subtract pending requests, overstating available leave for employees with outstanding requests | Leave | Medium | DISC-003; VW_LEAVE_SUMMARY | No — requires view fix: add `- PENDING` to the AVAILABLE formula in VW_LEAVE_SUMMARY |
| PP-15 | Managers are not notified when an employee cancels an approved leave request — a manager who planned around an employee's approved absence is not informed of the change | Leave | Medium | LEAVE-003; PKG_LEAVE.cancel_leave_request | Yes — add a notification call to cancel_leave_request for the approver |
| PP-16 | Two different hire date maximum-future thresholds are enforced: 90 days in the form, 180 days at the database level — records created outside the form (via direct procedure call) accept hire dates up to 180 days in the future | Employee | Medium | DISC-002; TRG_EMP_BEFORE_INSERT vs HRMS_EMPLOYEE form | No — harmonise to a single threshold (recommend 90 days at database level) |
| PP-17 | Promoted employees have no active-status check — a terminated or suspended employee can receive a promotion, creating inconsistent data | Employee | Medium | EMP-001; PKG_EMPLOYEE.promote_employee | No — requires code fix: add status check to promote_employee consistent with transfer_employee |
| PP-18 | Every transfer, promotion, and status change generates duplicate history records — once from the package's log_history call and once from the database trigger | Employee | Medium | DISC-004; TRG_EMP_BEFORE_UPDATE + PKG_EMPLOYEE | No — requires architectural decision: either remove history writes from triggers and let the packages own it, or remove history writes from packages and let the triggers own it |
| PP-19 | The payroll PAID status and the leave TAKEN status are unreachable through normal operations — the system cannot represent "paid" or "leave actually occurred" | Payroll / Leave | Medium | PAYROLL_RUNS.STATUS; LEAVE_REQUESTS.STATUS | Yes — implement a scheduled job or direct payment confirmation step; implement a nightly TAKEN status job |
| PP-20 | State tax withholding ignores W-4 state allowances and filing status entirely — employees with dependents or higher allowances are over-withheld for state taxes | Payroll | Medium | BR-38; PKG_PAYROLL.calculate_state_tax | No — requires refactor of state tax calculation to apply allowances |
| PP-21 | Turnover classification is case-sensitive and uses free-text matching — any termination reason other than the exact string 'VOLUNTARY' counts as involuntary, making turnover reports unreliable | Reporting | Medium | BR-87; PKG_REPORTING.turnover_report | Yes — add a constrained TERMINATION_REASON list (LOV or CHECK constraint) and apply UPPER() in the comparison |
| PP-22 | The time and attendance import and LDAP/AD org sync are stub functions — time data cannot enter the system and org changes in Active Directory are not reflected | Integration | Medium | INT-002; INT-003 | Yes — the file-reading infrastructure is in place; completing the CSV parsing and DB writes is the remaining work for time import |
| PP-23 | Leave request backdating uses calendar days, not business days — an employee submitting leave started the previous Monday on a Saturday is blocked (5 calendar days, 4 business days) when the intent was to allow 5 working days | Leave | Low | LEAVE-006; PKG_LEAVE.submit_leave_request | No — requires minor code fix: replace calendar day check with business day comparison |
| PP-24 | PKG_COMMON.business_days_between does not exclude holidays, while PKG_LEAVE.calculate_business_days does — the two functions return different counts for the same date range when holidays are present | Cross-cutting | Low | CROSS-001; PKG_COMMON; PKG_LEAVE | No — requires code fix: add holiday exclusion to PKG_COMMON.business_days_between, or route all callers to the PKG_LEAVE version |

---

## OUTPUT 8 — Automation Opportunities

| # | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-01 | Automate leave TAKEN status transition | Approved leave that has passed its dates remains APPROVED forever; leave utilisation reports are permanently inaccurate | Schedule a nightly database job that sets STATUS = 'TAKEN' for all APPROVED leave requests where END_DATE < SYSDATE | High — fixes all leave utilisation reporting and removes stale APPROVED records |
| AO-02 | Move tax brackets to database table | 2024 federal tax brackets are hard-coded; the system cannot process payroll for 2025 without a code deployment | Read from the existing TAX_BRACKETS table (already in schema); populate annually; zero code changes required for annual bracket updates | High — removes an annual mandatory code change; enables IRS bracket updates without developer involvement |
| AO-03 | Automate session activity refresh | Sessions expire 30 minutes from login regardless of activity; active users are interrupted without warning | Add LAST_ACTIVITY_DATE column to USER_SESSIONS; update on each is_session_valid call; calculate timeout from last activity | Medium — significant UX improvement for users in longer workflows |
| AO-04 | Automate voluntary/involuntary termination classification | Free-text reason field means voluntary departures are misclassified in turnover reports | Add a structured termination reason LOV (Voluntary, Involuntary, Retirement, End of Contract, etc.) enforced at the form level and via a CHECK constraint | Medium — makes turnover analytics reliable without report query changes |
| AO-05 | Automate payroll disbursement confirmation | PAID status is defined but unreachable; payroll has no record that payment actually occurred | Add a "Mark as Paid" button or batch confirmation step that advances APPROVED runs to PAID after bank file generation | Medium — completes the audit trail; enables payroll reconciliation |
| AO-06 | Automate notification to manager on leave cancellation | Managers are not told when employees cancel approved leave; managers may fail to reassign coverage | Add one PKG_NOTIFICATION.send_notification call to PKG_LEAVE.cancel_leave_request when the cancelled request was APPROVED | Medium — low effort, high operational value |
| AO-07 | Replace flat file GL integration with API | GL journal is written to a flat file for Oracle Financials import; no retry, no delivery confirmation | Integrate with Oracle Financials REST API or Oracle Integration Cloud; replace UTL_FILE writes with API calls | Medium — reduces manual DBA intervention; adds delivery confirmation |
| AO-08 | Replace legacy ADP benefits feed with modern format | Fixed-width 203-character ADP format requires vendor-specific handling | Replace with a configurable benefits connector (API or modern CSV) supported by current benefits platforms | Medium — enables vendor flexibility and reduces field-width maintenance |
| AO-09 | Complete time and attendance import | File reader is in place but CSV parsing and database writes are TODOs | Complete the import_time_attendance procedure to parse the CSV and write to a time entries table; use it to feed overtime and hours-based pay elements | High — enables the system to calculate variable pay; currently all calculations assume salaried employees only |
| AO-10 | Add leave self-service portal reminders | No automated reminders for pending leave approvals; managers may miss requests | Add a scheduled job querying LEAVE_REQUESTS where STATUS = 'PENDING' and CREATED_DATE < SYSDATE - 2; send reminder to approver | Low — improves leave processing timeliness with minimal development effort |

---

## ⚠️ Validation Queue

Items that remain unresolved or carry low confidence after this analysis:

| ID | Chunk | Domain | Item | Status |
|---|---|---|---|---|
| VQ-01 | Ch1 | Employee | ON_LEAVE and SUSPENDED employment statuses exist in the schema CHECK constraint but no code path sets them — confirmed as orphaned states | ✅ RESOLVED — both are orphaned; no setter exists anywhere |
| VQ-02 | Ch1 | Employee | EMPLOYEE_HISTORY trigger uses column names (CHANGE_DATE, OLD_VALUE, NEW_VALUE) that do not match the DDL (EFFECTIVE_DATE, OLD_DEPT_ID typed columns) | ✅ RESOLVED — confirmed mismatch; trigger would fail at runtime; see DISC-005 |
| VQ-03 | Ch1 | Employee | Rehire process — trigger may block the procedure | ✅ RESOLVED — confirmed non-functional; see DISC-001 |
| VQ-04 | Synth | Payroll | YTD accumulation resets incorrectly for mid-year hires | ⚠️ LOW — get_ytd_earnings uses calendar year from PERIOD_START_DATE; a mid-year hire would correctly show partial year; the bug may manifest in edge cases where a period spans a year boundary; insufficient evidence to confirm fully |
| VQ-05 | Ch3 | Leave | TAKEN status setter | ✅ RESOLVED — no setter exists; confirmed orphaned |
| VQ-06 | Synth | Payroll | PAID status setter | ✅ RESOLVED — no setter exists; confirmed orphaned |
| VQ-07 | Ch4 | Performance | REVIEW_CYCLES IN_PROGRESS and CALIBRATION setters | ✅ RESOLVED — both are orphaned; no setter exists |
| VQ-08 | Ch4 | Performance | MEETING_SCHEDULED setter | ✅ RESOLVED — orphaned; no setter exists |
| VQ-09 | Ch5 | Security | Encryption key rotation | ⚠️ LOW — key is hard-coded in source; no key management mechanism exists; confirmed risk but resolution path (Oracle Wallet) not evidenced in current code |
| VQ-10 | Ch1 | Employee | SQL injection scope | ✅ RESOLVED — confirmed to search_employees p_last_name and p_first_name parameters only; other search functions use bind variables |
| VQ-11 | Ch1 | Employee | Manager approval workflow for out-of-band salary | ✅ RESOLVED — no approval workflow exists; soft warning only; any salary accepted |
| VQ-12 | Ch5 | Security | Password change stub | ✅ RESOLVED — update statement genuinely missing; passwords cannot be changed |
| VQ-13 | Synth | Integration | Time import stub | ✅ RESOLVED — file reading only; no parsing or DB writes |
| VQ-14 | Synth | Integration | Org sync stub | ✅ RESOLVED — log call only; no LDAP/AD integration |
| VQ-15 | Synth | Payroll | Biweekly 27-period year | ⚠️ LOW — algorithm confirmed capable of generating 27 periods; specific trigger years depend on the first Friday calculation for each calendar year; not confirmed for a specific year in current seed data |
| VQ-16 | Ch3 | Leave | Carryover expiry double-run | ⚠️ LOW — code analysis suggests the WHERE CARRYOVER_FROM_PREV > 0 guard prevents double-subtraction within a single day if CARRYOVER_FROM_PREV is set to 0 on first run; the bug as described in headers may refer to a concurrent session scenario not covered by the guard |
| VQ-17 | Synth | Integration | GL employer-paid cost gap | ✅ RESOLVED — PAYROLL_DETAILS only contains employee-side amounts; employer contributions are not calculated or stored |
| VQ-18 | Synth | Reporting | RPT_* denormalized tables | ✅ RESOLVED — no RPT_* tables exist in the DDL provided; refresh function is a stub |
| VQ-19 | Synth | Reporting | Compa-ratio divergence between view and report | ✅ RESOLVED — VW_EMPLOYEE_COMPENSATION shows individual ratio; PKG_REPORTING.compensation_summary shows group average; both are correct but answer different questions |
| VQ-20 | Synth | Cross-cutting | Fiscal vs calendar year mixing in queries | ✅ RESOLVED — confirmed: payroll tax uses calendar year; business reporting uses fiscal year starting October; queries that join these will return mismatched results in October–December |

---

## 📋 Agent 1 Discrepancy Log

| ID | What Agent 1 Said | What Deep Analysis Shows | Resolution |
|---|---|---|---|
| DISC-001 | rehire_employee described as a working procedure to restore terminated employees | TRG_EMP_BEFORE_UPDATE fires before any UPDATE on EMPLOYEES and raises error -20503 if OLD status = TERMINATED and NEW status = ACTIVE. PKG_EMPLOYEE.rehire_employee does exactly this UPDATE. The procedure cannot execute without hitting the trigger. | Unresolved — requires code change; business stakeholders should be told the rehire function does not work |
| DISC-002 | Hire date validation was listed as a single rule | Two separate thresholds exist: 90 days (form-level WHEN-VALIDATE-ITEM) and 180 days (TRG_EMP_BEFORE_INSERT). Calls via direct procedure bypass form validation and accept up to 180 days future | Unresolved — recommend harmonising to 90 days at database level |
| DISC-003 | VW_LEAVE_SUMMARY described as showing available balance | View calculates AVAILABLE = OPENING + ACCRUED − USED + ADJUSTMENT (without PENDING); the LEAVE_BALANCES virtual column definition subtracts PENDING as well | Unresolved — view is incorrect; will overstate available balance for employees with outstanding requests |
| DISC-004 | History writing described as occurring in PKG_EMPLOYEE packages | TRG_EMP_BEFORE_UPDATE independently writes STATUS_CHANGE, DEPARTMENT_CHANGE, and JOB_CHANGE records for the same operations that PKG_EMPLOYEE packages write TRANSFER, PROMOTION, and TERMINATION records for | Unresolved — duplicate history entries exist; one mechanism should be removed |
| DISC-005 | EMPLOYEE_HISTORY table described as having typed columns OLD_DEPT_ID, NEW_DEPT_ID, OLD_JOB_ID etc. | TRG_EMP_BEFORE_UPDATE inserts into CHANGE_DATE (not EFFECTIVE_DATE) and OLD_VALUE / NEW_VALUE (VARCHAR2 generic fields); these column names do not match the DDL | Unresolved — trigger would fail at runtime with "invalid identifier" |
| DISC-006 | Agent 1 described PKG_SECURITY.authenticate as performing password verification | The function body looks up the employee by email, creates a session, and returns without ever comparing a password hash against USER_CREDENTIALS | Unresolved — critical security defect; system is effectively unauthenticated |
| DISC-007 | PKG_PAYROLL described as calculating taxes using the TAX_BRACKETS reference table | Tax brackets are hard-coded constants in the calculate_federal_tax function body; TAX_BRACKETS table exists in schema but is never queried | Unresolved — system cannot process 2025 payroll without a code change |
| DISC-008 | leave_request TAKEN status included in Agent 1's State Registry | No procedure anywhere in PKG_LEAVE, PKG_EMPLOYEE, or any trigger sets STATUS = 'TAKEN' on a leave request | Confirmed orphaned state — TAKEN is defined in the schema constraint but unreachable |
| DISC-009 | PAYROLL_RUNS PAID status included in Agent 1's State Registry | No procedure advances a payroll run from APPROVED to PAID; the disbursement step is entirely absent | Confirmed orphaned state — PAID is defined in the schema constraint but unreachable |

---

✅ **Agent 2 Analysis Complete.**
Documentation is ready for business review.
**Highest-priority validation item:** DISC-006 — the authentication system does not verify passwords; the HRMS is accessible to any active employee with any credentials. This must be resolved before any production use.

---

## SUPPLEMENTAL EXTRACTION — EMPLOYEE_DEPENDENTS

> **Source files analysed:** `schema/tables/01_core_tables.sql`, `plsql/packages/PKG_INTEGRATION.pkb`
> **Extraction date:** 2026-08-04

---

### Table Definition

**`HRMS.EMPLOYEE_DEPENDENTS`** — stores personal records of an employee's family members and domestic partners who may be enrolled in company benefits.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `DEPENDENT_ID` | NUMBER(10) | NOT NULL | — | Primary key |
| `EMP_ID` | NUMBER(10) | NOT NULL | — | FK → HRMS.EMPLOYEES(EMP_ID) |
| `FIRST_NAME` | VARCHAR2(50) | NOT NULL | — | |
| `LAST_NAME` | VARCHAR2(50) | NOT NULL | — | |
| `RELATIONSHIP` | VARCHAR2(20) | NOT NULL | — | Constrained — see CHK_RELATIONSHIP |
| `DATE_OF_BIRTH` | DATE | NULL | — | Optional; used in benefits feed |
| `SSN_ENCRYPTED` | VARCHAR2(200) | NULL | — | AES-256 encrypted (same pattern as EMPLOYEES.SSN_ENCRYPTED) |
| `BENEFITS_ENROLLED` | CHAR(1) | NULL | `'N'` | Flag: 'Y' = enrolled in at least one benefit plan |
| `ACTIVE_FLAG` | CHAR(1) | NOT NULL | `'Y'` | Soft-delete; 'N' removes from feeds but keeps record |
| `CREATED_BY` | VARCHAR2(30) | NOT NULL | — | Audit column |
| `CREATED_DATE` | DATE | NOT NULL | `SYSDATE` | Audit column |
| `MODIFIED_BY` | VARCHAR2(30) | NULL | — | Audit column |
| `MODIFIED_DATE` | DATE | NULL | — | Audit column |

**Constraints:**

| Constraint | Type | Definition |
|---|---|---|
| `PK_EMP_DEPENDENTS` | PRIMARY KEY | `DEPENDENT_ID` |
| `FK_DEP_EMP` | FOREIGN KEY | `EMP_ID` → `HRMS.EMPLOYEES(EMP_ID)` |
| `CHK_RELATIONSHIP` | CHECK | `RELATIONSHIP IN ('SPOUSE', 'CHILD', 'PARENT', 'DOMESTIC_PARTNER', 'OTHER')` |

**No unique constraint** exists on (EMP_ID, FIRST_NAME, LAST_NAME) or (EMP_ID, SSN_ENCRYPTED). A dependent can be added multiple times without a database-level duplicate guard.

---

### Business Rules Extracted

| ID | Rule | Source | Confidence | Severity |
|---|---|---|---|---|
| BR-DEP-01 | An employee may have zero or more dependents; there is no minimum or maximum count enforced at the database level. | `PK_EMP_DEPENDENTS` + `FK_DEP_EMP` (no cardinality constraint) | ✅ HIGH | Low |
| BR-DEP-02 | A dependent's relationship to the employee must be one of exactly five values: SPOUSE, CHILD, PARENT, DOMESTIC_PARTNER, OTHER. Any other value is rejected at the database constraint level. | `CHK_RELATIONSHIP` | ✅ HIGH | Medium |
| BR-DEP-03 | A dependent record is never physically deleted. Removal is performed by setting `ACTIVE_FLAG = 'N'` (soft-delete pattern, consistent with EMPLOYEES). | `ACTIVE_FLAG CHAR(1) DEFAULT 'Y' NOT NULL` + benefits feed filter `d.ACTIVE_FLAG = 'Y'` | ✅ HIGH | Medium |
| BR-DEP-04 | Only dependents with `ACTIVE_FLAG = 'Y'` are included in the ADP benefits enrollment feed exported to the external benefits vendor. Inactive dependents are silently excluded from the export. | `export_benefits_feed`: `LEFT JOIN EMPLOYEE_DEPENDENTS d ON e.EMP_ID = d.EMP_ID AND d.ACTIVE_FLAG = 'Y'` | ✅ HIGH | High |
| BR-DEP-05 | The `BENEFITS_ENROLLED` flag (`'Y'`/`'N'`) is stored per dependent but is **never read or filtered in any procedure**. It is captured as data but has no operational effect in any current code path. | Column exists; zero references to it in any package or trigger in the analysed source | ✅ HIGH | High — data is collected but never enforced or used |
| BR-DEP-06 | A dependent's SSN is stored encrypted (VARCHAR2(200)), following the same AES-256 pattern as `EMPLOYEES.SSN_ENCRYPTED`. However, no decrypt call is present for dependents anywhere in the analysed packages; the encryption key hard-coded in PKG_SECURITY applies (same vulnerability as BR-SECURITY). | `SSN_ENCRYPTED VARCHAR2(200)` column; cross-reference to `EMPLOYEES.SSN_ENCRYPTED` comment "AES-256 encrypted SSN — decrypted only in PKG_SECURITY" | ✅ HIGH | Critical — encrypted PII present; no decryption path confirmed; key is hard-coded |
| BR-DEP-07 | The benefits feed exports dependent data via a `LEFT JOIN`, meaning employees with **no dependents** still appear in the feed — once per employee row with all dependent columns blank-padded. This is by design for the ADP fixed-width format. | `export_benefits_feed`: `LEFT JOIN EMPLOYEE_DEPENDENTS` | ✅ HIGH | Low — expected for ADP format |
| BR-DEP-08 | There is no uniqueness constraint preventing the same dependent from being registered twice under the same employee (e.g., duplicate CHILD records for the same person). The database will accept duplicate inserts. | Absence of UNIQUE constraint on (EMP_ID, FIRST_NAME, LAST_NAME) or (EMP_ID, SSN_ENCRYPTED) | ✅ HIGH | Medium — duplicate enrollments could generate duplicate benefit costs |
| BR-DEP-09 | When an employee is terminated, dependent records are **not touched**: no cascade delete, no ACTIVE_FLAG update, no benefits disenrollment. Dependents remain ACTIVE_FLAG = 'Y' and would continue to appear in future benefits feeds unless manually inactivated. | `terminate_employee` procedure (PKG_EMPLOYEE) — reviewed in prior analysis; no reference to EMPLOYEE_DEPENDENTS | ✅ HIGH | High — COBRA/benefits-disenrollment compliance gap |
| BR-DEP-10 | The `DATE_OF_BIRTH` field for dependents is optional (nullable). Age-based eligibility rules (e.g., CHILD coverage cutoff at age 26) cannot be enforced by the system when DOB is absent. | `DATE_OF_BIRTH DATE` (nullable, no NOT NULL constraint) | ✅ HIGH | Medium — eligibility enforcement gap |

---

### Process: Benefits Feed Export (Dependent Data Pathway)

**Source procedure:** `PKG_INTEGRATION.export_benefits_feed`
**Trigger:** Manual call or scheduled batch; writes fixed-width file to `BENEFITS_FEED_OUT` directory object

| Step | Description | Dependent-Specific Logic |
|---|---|---|
| 1 | Query all ACTIVE employees (`EMPLOYMENT_STATUS = 'ACTIVE'`) | Employee filter only; no dependent-specific filter at this step |
| 2 | LEFT JOIN to `EMPLOYEE_DEPENDENTS` where `ACTIVE_FLAG = 'Y'` | Inactive dependents excluded; employees with no dependents get one row with blank dependent fields |
| 3 | Write one fixed-width record per (employee, dependent) pair | Dependent columns: `DEP_FIRST_NAME` (30 chars), `DEP_LAST_NAME` (30 chars), `RELATIONSHIP` (20 chars), `DEP_DOB` (10 chars) |
| 4 | File named `BENEFITS_YYYYMMDD.txt`; written to Oracle directory object `BENEFITS_FEED_OUT` | No FTP or push step in this procedure; delivery mechanism is external |
| 5 | Record count logged via PKG_COMMON.log_info | Count is (employee rows × dependent rows per employee) + (employees with no dependents × 1) |

**Fields NOT included in benefits feed from EMPLOYEE_DEPENDENTS:** `DEPENDENT_ID`, `SSN_ENCRYPTED`, `BENEFITS_ENROLLED`, `ACTIVE_FLAG`, `CREATED_BY`, `CREATED_DATE`, `MODIFIED_BY`, `MODIFIED_DATE`.

**Notable gap:** `BENEFITS_ENROLLED` flag is collected but never exported to the ADP feed. The benefits vendor receives relationship and DOB but no explicit enrollment flag — enrollment status is inferred entirely by record presence in the feed.

---

### Integration Touch Points

| Package / Object | How EMPLOYEE_DEPENDENTS Is Used |
|---|---|
| `PKG_INTEGRATION.export_benefits_feed` | LEFT JOIN on EMP_ID with ACTIVE_FLAG = 'Y' filter; exports FIRST_NAME, LAST_NAME, RELATIONSHIP, DATE_OF_BIRTH to ADP feed |
| `PKG_EMPLOYEE` (all lifecycle procedures) | **No reference.** Hire, terminate, transfer, promote — none touch EMPLOYEE_DEPENDENTS. |
| `PKG_PAYROLL` | **No reference.** Benefit deduction elements exist in PAY_ELEMENTS but are not joined to EMPLOYEE_DEPENDENTS. |
| `PKG_SECURITY` | Implicit — SSN_ENCRYPTED column present; no decrypt procedure call confirmed for dependents. |
| Triggers | No trigger references EMPLOYEE_DEPENDENTS in the analysed source. |

---

### Pain Points (New — EMPLOYEE_DEPENDENTS)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-DEP-01 | `BENEFITS_ENROLLED` flag is stored but never used — enrollment status is inferred from feed presence rather than an explicit flag. Any system that queries this column expecting a reliable value will get stale or meaningless data. | Business and compliance reporting on benefit enrollment counts is unreliable. | High |
| PP-DEP-02 | Termination procedure does not inactivate dependents. Terminated employees' dependents remain `ACTIVE_FLAG = 'Y'` and continue appearing in benefits feeds until manually corrected. | Potential regulatory exposure (COBRA notification windows, incorrect benefit billing). | High |
| PP-DEP-03 | No duplicate-dependent guard. Same person can be enrolled twice, generating duplicate benefit cost per dependent. | Financial risk if benefits vendor charges per enrolled dependent record. | Medium |
| PP-DEP-04 | `DATE_OF_BIRTH` is nullable, preventing age-based eligibility enforcement (e.g., CHILD coverage age 26 cutoff). | Cannot automate CHILD dependent ageing-off; requires manual audit. | Medium |
| PP-DEP-05 | Dependent SSN is encrypted but there is no confirmed decrypt path in the analysed packages. If a business process requires SSN retrieval for a dependent (e.g., insurance filing), there is no procedure to call. | Operational gap for benefits administration requiring dependent SSN. | Medium |

---

### Automation Opportunities (New — EMPLOYEE_DEPENDENTS)

| ID | Opportunity | Benefit |
|---|---|---|
| AO-DEP-01 | Auto-inactivate dependents (`ACTIVE_FLAG = 'N'`) when the parent employee is terminated, inside `PKG_EMPLOYEE.terminate_employee`. | Eliminates PP-DEP-02 compliance gap; ensures benefits feed is accurate immediately after termination. |
| AO-DEP-02 | Add a unique constraint or application-level duplicate check on (EMP_ID, FIRST_NAME, LAST_NAME, DATE_OF_BIRTH) to prevent duplicate dependent registrations. | Eliminates PP-DEP-03 financial risk. |
| AO-DEP-03 | Wire `BENEFITS_ENROLLED` flag to a real enrollment status: set to 'Y' when a dependent is added to a benefit plan, 'N' when removed. Export the flag in the benefits feed. | Makes enrollment reporting reliable and removes the need to infer enrollment from feed presence. |
| AO-DEP-04 | Add a scheduled job to age-off CHILD dependents when they reach 26 (or the configured age threshold): set `ACTIVE_FLAG = 'N'` and queue a notification to the employee and HR. Requires `DATE_OF_BIRTH` to be NOT NULL (or handle NULL as manual review). | Automates a currently manual compliance task. |

---

### Validation Queue Items (New — EMPLOYEE_DEPENDENTS)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-DEP-01 | Supplemental | Employee / Integration | Confirm whether any other package (not in the analysed source) manages `BENEFITS_ENROLLED` — it may be maintained by a form or report not yet reviewed. | ❓ UNRESOLVED |
| VQ-DEP-02 | Supplemental | Employee / Security | Confirm whether `PKG_SECURITY.decrypt_ssn` (or equivalent) accepts a dependent SSN as input or is restricted to employee records only. | ❓ UNRESOLVED |
| VQ-DEP-03 | Supplemental | Integration | Confirm whether the ADP benefits vendor expects BENEFITS_ENROLLED in the fixed-width format in a field position not yet mapped — the 203-character record format has not been fully reverse-engineered. | ❓ UNRESOLVED |
| VQ-DEP-04 | Supplemental | Employee | Confirm business policy: should dependents of a terminated employee be automatically inactivated, or held for COBRA administration before inactivation? | ❓ UNRESOLVED — policy decision required |

---

## SUPPLEMENTAL EXTRACTION — PKG_INTEGRATION.sync_org_structure

> **Source files analysed:** `plsql/packages/PKG_INTEGRATION.pkb` (recovered from file_cache.json)
> **Extraction date:** 2026-08-04
> **Cross-references:** VQ-14 (resolved stub confirmation), PP-22 (integration stub pain point), Domain Architecture Map — Integration row

---

### Procedure Definition

**`HRMS.PKG_INTEGRATION.sync_org_structure`** — declared integration point for synchronising HRMS organisational structure with an external directory service (LDAP / Active Directory).

```sql
PROCEDURE sync_org_structure(
    p_user IN VARCHAR2 DEFAULT USER
) IS
BEGIN
    -- Placeholder for org structure sync with external directory (LDAP/AD)
    PKG_COMMON.log_info('PKG_INTEGRATION', 'sync_org_structure',
        'Org structure sync completed', p_user);
END sync_org_structure;
```

**Signature summary:**

| Element | Value | Notes |
|---|---|---|
| Package | `HRMS.PKG_INTEGRATION` | Integration domain |
| Procedure | `sync_org_structure` | |
| Parameter | `p_user IN VARCHAR2 DEFAULT USER` | Audit/log context only; defaults to Oracle session user |
| Returns | Nothing (PROCEDURE) | |
| Direction | Inbound — external directory → HRMS (implied by intent) | Never verified; no actual data flow exists |
| External system | LDAP / Active Directory (comment-stated) | No connection parameters present |

---

### What the Procedure Actually Does

| Step | Code | Effect |
|---|---|---|
| 1 | `PKG_COMMON.log_info(...)` | Writes one INFO log entry with the message `'Org structure sync completed'` | 
| 2 | `END sync_org_structure` | Returns immediately |

**The procedure contains no business logic.** It reads no tables, writes no tables, opens no network connections, calls no LDAP API, and performs no DBMS_LDAP or UTL_HTTP operations. The only observable side effect is a single log entry that states the sync completed when nothing was synced.

---

### Tables and Objects Accessed

| Object | Access Type | Notes |
|---|---|---|
| `PKG_COMMON.log_info` | EXECUTE | Writes to `AUDIT_LOG` (INFO level) — the only side effect |
| `DEPARTMENTS` | None | Not read or written; would be the primary target of any real sync |
| `EMPLOYEES` (reporting lines) | None | Not read or written; manager assignments would be a sync target |
| `JOB_TITLES` | None | Not read or written |
| LDAP / Active Directory | None | No DBMS_LDAP, UTL_HTTP, UTL_TCP, or database link present |
| `SYSTEM_PARAMETERS` | None | Not queried for connection details |

---

### Business Rules Extracted

| ID | Rule | Source | Confidence | Severity |
|---|---|---|---|---|
| BR-ORG-01 | Org structure synchronisation with an external LDAP/Active Directory is a declared integration capability of `PKG_INTEGRATION` but is entirely unimplemented. The procedure body is a placeholder. | Comment in `sync_org_structure`: `"Placeholder for org structure sync with external directory (LDAP/AD)"` | ✅ HIGH | High — capability is absent despite being declared |
| BR-ORG-02 | The procedure unconditionally logs `'Org structure sync completed'` regardless of whether any sync was attempted or succeeded. Any monitoring that checks this log message for sync health will receive a false-positive confirmation every time the procedure is called. | `PKG_COMMON.log_info(... 'Org structure sync completed' ...)` — only line in procedure body | ✅ HIGH | High — misleading operational signal |
| BR-ORG-03 | No connection parameters (host, port, base DN, bind credentials, or Oracle directory object) are defined anywhere in the procedure or referenced from `SYSTEM_PARAMETERS`. Implementing real LDAP sync would require a schema design decision on where connection details are stored. | Absence of any parameter, cursor, or PKG_COMMON.get_param call in the procedure | ✅ HIGH | Medium — design gap blocking implementation |
| BR-ORG-04 | The scope of "org structure" is undefined in the code — it is unknown whether the intended sync covers: department hierarchy, employee-to-manager reporting lines, job titles, OU-to-department mapping, or all of these. | Comment uses "org structure" without further definition; no target tables or columns are referenced | ⚠️ LOW — inferred from integration context | Medium — ambiguous scope |
| BR-ORG-05 | The procedure accepts only a `p_user` parameter (for logging) and has no parameters for sync mode (full vs. delta), target OU, or date filter. A real implementation would require at minimum a delta-sync option to avoid replacing all HRMS org data on every call. | Procedure signature: single optional parameter `p_user` | ✅ HIGH — absence is confirmed | Medium — interface is not production-ready |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| VQ-14 (RESOLVED) | Confirmed: "log call only; no LDAP/AD integration" — this extraction provides the complete evidence base for that resolution |
| PP-22 | Partially covers this: "LDAP/AD org sync [is a] stub function — org changes in Active Directory are not reflected" — the new BR-ORG-02 (misleading log) and BR-ORG-03 (no connection parameters) are additional findings not present in PP-22 |
| Domain Architecture Map — Integration | Confirmed: "org sync is a stub" — the supplemental extraction expands this with specifics on what is and is not implemented |
| `PKG_INTEGRATION.generate_gl_journal` | The GL journal procedure in the same package is fully implemented — this org sync stub is the only fully-unimplemented procedure in the package alongside `import_time_attendance` (file reading only, no DB writes) |

---

### Pain Points (New — sync_org_structure)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-ORG-01 | The log message `'Org structure sync completed'` is written unconditionally. Any scheduled job, monitoring script, or operations team checking the log for sync health receives a false-positive success signal on every execution. A real sync failure is indistinguishable from a "successful" stub run. | Operational monitoring is blind to the absence of the capability; the system silently pretends the sync is working. | High |
| PP-ORG-02 | No connection parameters exist — the procedure has no mechanism to be told where the LDAP/AD server is, what credentials to use, or what OU to read. The procedure cannot be extended without both a schema change (add SYSTEM_PARAMETERS entries or a new config table) and a code rewrite. | Implementing the sync is a non-trivial project, not a simple code addition. | Medium |
| PP-ORG-03 | The scope of sync (departments, reporting lines, job titles) is undefined in any schema comment, requirement document reference, or code comment beyond the phrase "org structure". Any implementation effort must first produce a scope definition with stakeholders before writing a line of code. | Risk of implementing the wrong sync if built without requirements clarification. | Medium |

---

### Automation Opportunities (New — sync_org_structure)

| ID | Opportunity | Benefit |
|---|---|---|
| AO-ORG-01 | Implement the LDAP/AD sync using Oracle's `DBMS_LDAP` package: read department OUs and manager attributes from Active Directory; update `DEPARTMENTS.DEPT_NAME`, `EMPLOYEES.MANAGER_ID`, and optionally `JOB_TITLES` when changes are detected. Store LDAP connection details in `SYSTEM_PARAMETERS` (editable, non-sensitive fields) and bind credentials in Oracle Wallet. | Eliminates manual HR overhead for org chart maintenance; keeps HRMS reporting lines consistent with Active Directory; resolves PP-ORG-01 by making the log message only fire on a real sync. |
| AO-ORG-02 | Replace the unconditional success log with conditional logging: log `'Org structure sync completed — N departments updated, M reporting lines changed'` on success; log an error via `PKG_COMMON.log_error` on exception. This can be done as a low-effort interim step before full implementation. | Immediately fixes PP-ORG-01 — monitoring can trust the log output. |

---

### Validation Queue Items (New — sync_org_structure)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-ORG-01 | Supplemental | Integration | Confirm the intended scope of "org structure sync": does it cover (a) department hierarchy only, (b) employee-to-manager reporting lines, (c) job title mapping from AD job attributes, or (d) all of the above? This is a business/stakeholder question, not resolvable from code alone. | ❓ UNRESOLVED — stakeholder input required |
| VQ-ORG-02 | Supplemental | Integration | Confirm where LDAP/AD connection details are intended to be stored — `SYSTEM_PARAMETERS`, a dedicated config table, Oracle Wallet, or a database link. This determines the implementation approach for `AO-ORG-01`. | ❓ UNRESOLVED — architecture decision required |
| VQ-ORG-03 | Supplemental | Integration | Confirm whether `sync_org_structure` is currently scheduled (e.g., via DBMS_SCHEDULER) or called manually. If it is scheduled, every execution is silently writing a false-positive success log. | ❓ UNRESOLVED — requires scheduler audit |
| VQ-ORG-04 | Supplemental | Integration | Confirm sync direction: LDAP/AD → HRMS (HRMS as the consumer), HRMS → LDAP/AD (HRMS as the source of truth), or bidirectional. The comment implies inbound only but the intended data-of-record system is not stated. | ❓ UNRESOLVED — business policy question |

---

## SUPPLEMENTAL EXTRACTION — EMPLOYEE_BANK_ACCOUNTS

> **Source files analysed:** `schema/tables/02_payroll_tables.sql` (recovered from file_cache.json)
> **Prior cross-references in main analysis:** OUTPUT 6 Payroll domain note; Payroll Process Flow Stage 6 (disbursement gap); DISC-009 (PAID status orphaned); PP-19 (PAID/TAKEN unreachable)
> **Extraction date:** 2026-08-04

---

### Table Definition

**`HRMS.EMPLOYEE_BANK_ACCOUNTS`** — stores direct deposit bank account records for employees. Schema supports split-deposit across multiple accounts via DEPOSIT_TYPE and PRIORITY_ORDER. The table is never referenced by any procedure, function, trigger, or view in the analysed source.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `BANK_ACCT_ID` | NUMBER(10) | NOT NULL | — | Primary key |
| `EMP_ID` | NUMBER(10) | NOT NULL | — | FK → HRMS.EMPLOYEES(EMP_ID) |
| `BANK_NAME` | VARCHAR2(100) | NULL | — | Optional; informational only |
| `ROUTING_NUMBER` | VARCHAR2(20) | NOT NULL | — | Plain text — not encrypted |
| `ACCOUNT_NUMBER_ENC` | VARCHAR2(200) | NOT NULL | — | Encrypted; pattern matches EMPLOYEES.SSN_ENCRYPTED — same AES-256 key likely applies |
| `ACCOUNT_TYPE` | VARCHAR2(20) | NULL | `'CHECKING'` | Constrained — CHK_ACCT_TYPE |
| `DEPOSIT_TYPE` | VARCHAR2(20) | NULL | `'FULL'` | Constrained — CHK_DEPOSIT_TYPE |
| `DEPOSIT_AMOUNT` | NUMBER(12,2) | NULL | — | Used when DEPOSIT_TYPE = 'PARTIAL_AMOUNT'; nullable with no cross-column enforcement |
| `DEPOSIT_PERCENTAGE` | NUMBER(5,2) | NULL | — | Used when DEPOSIT_TYPE = 'PARTIAL_PERCENT'; nullable with no cross-column enforcement |
| `PRIORITY_ORDER` | NUMBER(2) | NULL | `1` | Disbursement sequence across multiple accounts |
| `PRENOTE_SENT` | CHAR(1) | NULL | `'N'` | ACH prenote tracking flag; no procedure confirmed to set 'Y' |
| `PRENOTE_DATE` | DATE | NULL | — | Date prenote was sent; no procedure confirmed to populate this |
| `ACTIVE_FLAG` | CHAR(1) | NOT NULL | `'Y'` | Soft-delete pattern |
| `CREATED_BY` | VARCHAR2(30) | NOT NULL | — | Audit column |
| `CREATED_DATE` | DATE | NOT NULL | `SYSDATE` | Audit column |
| `MODIFIED_BY` | VARCHAR2(30) | NULL | — | Audit column |
| `MODIFIED_DATE` | DATE | NULL | — | Audit column |

**Constraints:**

| Constraint | Type | Definition |
|---|---|---|
| `PK_EMP_BANK_ACCTS` | PRIMARY KEY | `BANK_ACCT_ID` |
| `FK_BA_EMP` | FOREIGN KEY | `EMP_ID` → `HRMS.EMPLOYEES(EMP_ID)` |
| `CHK_ACCT_TYPE` | CHECK | `ACCOUNT_TYPE IN ('CHECKING', 'SAVINGS')` |
| `CHK_DEPOSIT_TYPE` | CHECK | `DEPOSIT_TYPE IN ('FULL', 'PARTIAL_AMOUNT', 'PARTIAL_PERCENT', 'REMAINDER')` |

**Absent constraints (design gaps):**
- No UNIQUE constraint on `(EMP_ID, ROUTING_NUMBER, ACCOUNT_NUMBER_ENC)` — same account can be registered twice for the same employee.
- No cross-column CHECK constraint linking DEPOSIT_TYPE to DEPOSIT_AMOUNT / DEPOSIT_PERCENTAGE — a PARTIAL_AMOUNT account can be saved with NULL DEPOSIT_AMOUNT without error.
- No distribution totalling constraint — accounts whose amounts or percentages do not sum to net pay / 100% are accepted without error.

---

### Business Rules Extracted

| ID | Rule | Source | Confidence | Severity |
|---|---|---|---|---|
| BR-BA-01 | An employee may have zero or more bank accounts registered for direct deposit; there is no minimum or maximum count enforced at the database level. | FK_BA_EMP; no cardinality constraint | ✅ HIGH | Low |
| BR-BA-02 | Account type must be either CHECKING or SAVINGS; no other values are accepted at the database level. | CHK_ACCT_TYPE | ✅ HIGH | Medium |
| BR-BA-03 | Deposit type must be one of four values: FULL (entire net pay to this account), PARTIAL_AMOUNT (fixed dollar amount), PARTIAL_PERCENT (percentage of net pay), REMAINDER (net pay minus all other disbursements). The schema is designed to support split direct deposit across multiple accounts. | CHK_DEPOSIT_TYPE; PRIORITY_ORDER column | ✅ HIGH | High |
| BR-BA-04 | Account numbers are stored encrypted (ACCOUNT_NUMBER_ENC VARCHAR2(200)); routing numbers are stored as plain text (ROUTING_NUMBER VARCHAR2(20)). The column length and naming pattern match EMPLOYEES.SSN_ENCRYPTED — the AES-256 key hard-coded in PKG_SECURITY almost certainly encrypts account numbers too, but no explicit encrypt/decrypt call for bank account numbers is confirmed in the analysed source. | Column definitions; cross-reference to PP-13, SEC-002 | ⚠️ MEDIUM — encryption method not explicitly confirmed for bank accounts | Critical |
| BR-BA-05 | An ACH prenote workflow was designed into the schema: PRENOTE_SENT (CHAR(1), default 'N') and PRENOTE_DATE (DATE) columns track whether a zero-dollar test transaction was sent before the first live deposit. No procedure in the analysed source sets PRENOTE_SENT = 'Y' or populates PRENOTE_DATE — the prenote step is a schema design that was never implemented in code. | PRENOTE_SENT DEFAULT 'N'; PRENOTE_DATE nullable; zero references in all analysed packages | ✅ HIGH | High — ACH prenote is a Nacha regulatory requirement for new direct deposit accounts |
| BR-BA-06 | When an employee has multiple active bank accounts, they are funded in ascending PRIORITY_ORDER sequence during disbursement. | PRIORITY_ORDER NUMBER(2) DEFAULT 1 | ✅ HIGH | Medium |
| BR-BA-07 | Bank name is optional and not required for a valid account record; it is informational only and plays no role in disbursement. | BANK_NAME NULL | ✅ HIGH | Low |
| BR-BA-08 | Bank account records are never physically deleted; inactivation is performed by setting ACTIVE_FLAG = 'N', consistent with the soft-delete pattern used for EMPLOYEES and EMPLOYEE_DEPENDENTS. | ACTIVE_FLAG CHAR(1) NOT NULL DEFAULT 'Y' | ✅ HIGH | Medium |
| BR-BA-09 | DEPOSIT_AMOUNT and DEPOSIT_PERCENTAGE are both nullable. No cross-column constraint requires DEPOSIT_AMOUNT to be populated when DEPOSIT_TYPE = 'PARTIAL_AMOUNT', or DEPOSIT_PERCENTAGE to be populated when DEPOSIT_TYPE = 'PARTIAL_PERCENT'. Invalid partial-deposit records can be created without triggering a database error. | Column nullability; absence of any CHECK constraint linking DEPOSIT_TYPE to amount/percentage fields | ✅ HIGH | High — any disbursement procedure built on this table would encounter silent invalid records |
| BR-BA-10 | There is no uniqueness constraint preventing the same bank account (routing number + account number) from being registered twice under the same employee. The database accepts duplicate inserts. | Absence of UNIQUE constraint on (EMP_ID, ROUTING_NUMBER, ACCOUNT_NUMBER_ENC) | ✅ HIGH | Medium |
| BR-BA-11 | No constraint ensures that the deposit amounts or percentages across all active accounts for an employee sum to net pay. Over-distribution (e.g., two FULL accounts) and under-distribution (e.g., PARTIAL accounts totalling 80% with no REMAINDER) are both undetected at the database level. | Absence of any totalling constraint | ✅ HIGH | High — would cause incorrect pay disbursement when the disbursement layer is built |
| BR-BA-12 | EMPLOYEE_BANK_ACCOUNTS is never referenced in any procedure, function, trigger, or view in the analysed source. The table exists with a complete schema but direct deposit disbursement is entirely absent from the codebase. This is the direct cause of PAYROLL_RUNS.STATUS = 'PAID' being an orphaned, unreachable state (DISC-009). | Cross-reference to OUTPUT 6 Payroll domain note; PKG_PAYROLL disbursement gap; DISC-009; PP-19 | ✅ HIGH | Critical |

---

### Process Gap: Direct Deposit Disbursement (Not Implemented)

**Expected process (schema designed for it; code entirely absent):**

| Step | Expected Behaviour | What Exists in Code |
|---|---|---|
| 1 | When a new bank account is added, queue an ACH prenote (zero-dollar test deposit) and record PRENOTE_SENT / PRENOTE_DATE | Schema columns present; no procedure to populate them |
| 2 | After prenote confirms, allow account for live disbursement | Not implemented |
| 3 | After payroll run reaches APPROVED, read active bank accounts per employee in PRIORITY_ORDER | Not implemented; no procedure reads EMPLOYEE_BANK_ACCOUNTS at all |
| 4 | Distribute net pay per DEPOSIT_TYPE (FULL / PARTIAL_AMOUNT / PARTIAL_PERCENT / REMAINDER) | Not implemented |
| 5 | Generate NACHA ACH file or equivalent; advance PAYROLL_RUNS.STATUS from APPROVED to PAID | Not implemented — PAID is an orphaned status (DISC-009) |

**This is not a partial implementation.** There is no code that reads from EMPLOYEE_BANK_ACCOUNTS in any payroll context. The disbursement layer is entirely missing.

---

### Integration Touch Points

| Package / Object | How EMPLOYEE_BANK_ACCOUNTS Is Used |
|---|---|
| `PKG_PAYROLL` | **No reference.** Calculation, approval, and reversal procedures do not query EMPLOYEE_BANK_ACCOUNTS. |
| `PKG_EMPLOYEE` | **No reference.** Hire, terminate, transfer, promote — none touch EMPLOYEE_BANK_ACCOUNTS. |
| `PKG_INTEGRATION` | **No reference.** GL journal and benefits feed exports do not include bank account data. |
| `PKG_SECURITY` | Implicit only — ACCOUNT_NUMBER_ENC column is present; no explicit encrypt/decrypt call for bank account numbers confirmed in analysed source. |
| Triggers | No trigger references EMPLOYEE_BANK_ACCOUNTS in the analysed source. |

---

### Pain Points (New — EMPLOYEE_BANK_ACCOUNTS)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-BA-01 | Direct deposit is entirely non-functional — the disbursement step between APPROVED and PAID is absent; EMPLOYEE_BANK_ACCOUNTS is never read during payroll processing. Any bank accounts employees have registered are completely ignored at pay time. | Employees receive no electronic direct deposit. Compounds PP-19 (PAID status orphaned) and DISC-009. | Critical |
| PP-BA-02 | Routing numbers are stored in plain text. Routing numbers together with encrypted account numbers constitute sensitive financial identifiers; routing numbers have no encryption protection. | Financial data exposure if the database or a backup is accessed by unauthorised parties. | High |
| PP-BA-03 | The ACH prenote step is designed into the schema (PRENOTE_SENT, PRENOTE_DATE columns) but not implemented. Sending a live ACH deposit without a prenote violates Nacha operating rules for new direct deposit accounts, exposing the company to transaction rejection and compliance penalties once direct deposit is built. | Regulatory and compliance risk for ACH transactions. | High |
| PP-BA-04 | No cross-column constraint ties DEPOSIT_TYPE to the required amount or percentage field. A PARTIAL_AMOUNT account with NULL DEPOSIT_AMOUNT is a valid database record. Any disbursement logic added later will encounter these silently and either fail, skip the account, or disburse nothing. | Data integrity risk that surfaces as a runtime bug when disbursement is implemented. | High |
| PP-BA-05 | No distribution totalling rule is enforced. Employees can accumulate accounts totalling more or less than 100% of net pay, with no error until disbursement is attempted. | Over- or under-payment risk when disbursement is implemented. | High |
| PP-BA-06 | No duplicate-account guard. The same bank account can be registered twice for the same employee, potentially causing double disbursement to that account. | Financial risk (double payment) when disbursement is implemented. | Medium |
| PP-BA-07 | Termination procedure does not close or inactivate bank account records. Terminated employees' accounts remain ACTIVE_FLAG = 'Y'. If direct deposit is later implemented, erroneous final-pay or post-termination deposits could be sent to former employees. | Financial risk and data hygiene gap; mirrors PP-DEP-02 for dependents. | Medium |

---

### Automation Opportunities (New — EMPLOYEE_BANK_ACCOUNTS)

| ID | Opportunity | Benefit |
|---|---|---|
| AO-BA-01 | Implement the missing disbursement procedure: after payroll approval, read each active employee's bank accounts (ACTIVE_FLAG = 'Y', ordered by PRIORITY_ORDER), distribute net pay by DEPOSIT_TYPE, generate a NACHA ACH file, and advance PAYROLL_RUNS.STATUS to PAID. | Closes the most critical gap in the payroll lifecycle; resolves PP-BA-01, PP-19, and DISC-009. |
| AO-BA-02 | Implement the ACH prenote step: when a new bank account is added or reactivated, automatically queue a zero-dollar prenote ACH record and set PRENOTE_SENT = 'Y' / PRENOTE_DATE = SYSDATE on confirmation. Block the account from live disbursement until prenote clears. | Addresses PP-BA-03; brings direct deposit into Nacha ACH compliance for new accounts. |
| AO-BA-03 | Add distribution validation at the application layer (PKG_PAYROLL or a dedicated validate_bank_accounts procedure): verify at most one FULL account per employee; DEPOSIT_AMOUNT / DEPOSIT_PERCENTAGE is not null for the relevant DEPOSIT_TYPE; total distribution does not exceed net pay; at most one REMAINDER account exists. | Addresses PP-BA-04 and PP-BA-05; prevents invalid configurations before disbursement logic encounters them. |
| AO-BA-04 | Auto-inactivate bank accounts (ACTIVE_FLAG = 'N') when an employee is terminated, inside PKG_EMPLOYEE.terminate_employee — consistent with the AO-DEP-01 pattern for dependents. | Addresses PP-BA-07; prevents stale bank account records from being used in post-termination disbursements. |

---

### Validation Queue Items (New — EMPLOYEE_BANK_ACCOUNTS)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-BA-01 | Supplemental | Payroll / Security | Confirm whether ACCOUNT_NUMBER_ENC uses the same PKG_SECURITY encrypt/decrypt function as EMPLOYEES.SSN_ENCRYPTED. If confirmed, the hard-coded AES-256 key vulnerability (PP-13, SEC-002) extends to all employee bank account numbers. | ❓ UNRESOLVED |
| VQ-BA-02 | Supplemental | Payroll | Confirm whether any unreviewed Oracle Forms screen (e.g., a Banking or Direct Deposit tab on HRMS_EMPLOYEE form) sets PRENOTE_SENT = 'Y' or calls an unreviewed prenote procedure not in the analysed packages. | ❓ UNRESOLVED |
| VQ-BA-03 | Supplemental | Payroll / Integration | Confirm the intended disbursement mechanism: NACHA ACH flat-file (most likely given the GL journal and benefits feed file-based patterns), third-party payroll processor API, or manual bank upload outside the system. The answer determines the scope and approach for AO-BA-01. | ❓ UNRESOLVED — architecture decision required |
| VQ-BA-04 | Supplemental | Payroll / Employee | Confirm business policy: when an employee is terminated, should bank accounts be immediately inactivated, or held open for final-pay disbursement before inactivation? Determines whether AO-BA-04 should precede or follow disbursement. | ❓ UNRESOLVED — policy decision required |

---

## SUPPLEMENTAL EXTRACTION — PKG_EMPLOYEE.terminate_employee (TODO Sub-steps: COBRA, Access Revocation, Final Pay)

> **Source files analysed:** `plsql/packages/PKG_EMPLOYEE.pkb` (recovered from file_cache.json)
> **Extraction date:** 2026-08-04
> **Cross-references:** BR-17, BR-18, BR-19 (existing termination rules); PP-08, PP-09 (leave balance gaps); BR-DEP-09, PP-DEP-02 (dependent inactivation gap); PP-BA-07 (bank account inactivation gap); Process: Employee Termination step 9; Value Stream: Employee Lifecycle stage 5 external dependencies

---

### Procedure Definition

**`HRMS.PKG_EMPLOYEE.terminate_employee`** — ends an employee's employment, auto-cancels pending leave, closes salary and pay element records, logs history, and notifies the employee's manager. Three integration sub-steps are declared as TODO comments and are entirely unimplemented.

**Signature:**

| Element | Value | Notes |
|---|---|---|
| Package | `HRMS.PKG_EMPLOYEE` | Employee Management domain |
| Procedure | `terminate_employee` | |
| `p_emp_id` | `IN NUMBER` | Employee to terminate |
| `p_termination_date` | `IN DATE` | Effective termination date (may be past, present, or future) |
| `p_reason` | `IN VARCHAR2` | Free-text reason; stored in `EMPLOYEES.TERMINATION_REASON`; also used as `REASON_CODE` in history |
| `p_comments` | `IN VARCHAR2 DEFAULT NULL` | Optional additional comments; written to history only |
| `p_user` | `IN VARCHAR2 DEFAULT USER` | Audit context; defaults to Oracle session user |
| Returns | Nothing (PROCEDURE) | |

---

### Step-by-Step Execution Map

| Step | Code Action | Tables Affected | Notes |
|---|---|---|---|
| 1 | `SELECT * FROM EMPLOYEES WHERE EMP_ID = p_emp_id FOR UPDATE` | `EMPLOYEES` (read + lock) | Uses `FOR UPDATE` **without** `NOWAIT` — unlike `transfer_employee` which uses `FOR UPDATE NOWAIT`. Concurrent callers will block indefinitely rather than fail immediately. |
| 2 | Check `v_emp.EMPLOYMENT_STATUS = 'TERMINATED'` → raise `-20005` | — | Only guard: double-termination check. No guard for ON_LEAVE or SUSPENDED. |
| 3 | `SELECT COUNT(*) FROM LEAVE_REQUESTS WHERE STATUS = 'PENDING'` | `LEAVE_REQUESTS` (read) | Count only — no read of APPROVED leave. |
| 4 | `UPDATE LEAVE_REQUESTS SET STATUS = 'CANCELLED' … WHERE STATUS = 'PENDING'` | `LEAVE_REQUESTS` (write) | Sets `CANCEL_REASON = 'Auto-cancelled due to termination'`. Does **not** decrement `LEAVE_BALANCES.PENDING` — existing PP-08. |
| 5 | `UPDATE EMPLOYEES SET EMPLOYMENT_STATUS = 'TERMINATED', TERMINATION_DATE, TERMINATION_REASON, ACTIVE_FLAG = 'N'` | `EMPLOYEES` (write) | Core status change. |
| 6 | `UPDATE SALARY_RECORDS SET END_DATE = p_termination_date, ACTIVE_FLAG = 'N' WHERE ACTIVE_FLAG = 'Y'` | `SALARY_RECORDS` (write) | Ends all active salary records. Salary beyond termination date is not calculated here. |
| 7 | `UPDATE EMPLOYEE_PAY_ELEMENTS SET END_DATE = p_termination_date, ACTIVE_FLAG = 'N' WHERE ACTIVE_FLAG = 'Y'` | `EMPLOYEE_PAY_ELEMENTS` (write) | Deactivates all active pay elements (deductions, benefits). |
| 8 | `log_history(... CHANGE_TYPE = 'TERMINATION' ...)` | `EMPLOYEE_HISTORY` (write via AUTONOMOUS_TRANSACTION) | History written autonomously; cannot fail the main transaction. |
| 9 | `PKG_AUDIT.log_action('EMPLOYEES', p_emp_id, 'UPDATE', p_user)` | `AUDIT_LOG` (write) | Standard audit entry. |
| 10 | `PKG_NOTIFICATION.send_notification(... p_recipient_emp_id => v_emp.MANAGER_EMP_ID ...)` | `NOTIFICATION_QUEUE` (write) | Manager-only; conditional on `MANAGER_EMP_ID IS NOT NULL`. Employee is NOT notified of their own termination. |
| 11 | `-- TODO: Integrate with benefits system to trigger COBRA` | **Nothing** | No code executes. No benefits tables, no external call, no stub. |
| 12 | `-- TODO: Revoke system access via PKG_SECURITY` | **Nothing** | No code executes. No `USER_SESSIONS` update, no `USER_CREDENTIALS` update, no `PKG_SECURITY` call. |
| 13 | `-- TODO: Calculate final pay via PKG_PAYROLL.calculate_final_pay` | **Nothing** | No code executes. `PKG_PAYROLL.calculate_final_pay` is referenced but does not exist as a procedure in `PKG_PAYROLL`. |

---

### Tables Accessed

| Table | Operation | Step | Notes |
|---|---|---|---|
| `EMPLOYEES` | SELECT FOR UPDATE, UPDATE | 1, 5 | Locks row for duration of transaction |
| `LEAVE_REQUESTS` | SELECT (count), UPDATE | 3, 4 | PENDING only; APPROVED not touched |
| `SALARY_RECORDS` | UPDATE | 6 | All rows with ACTIVE_FLAG = 'Y' |
| `EMPLOYEE_PAY_ELEMENTS` | UPDATE | 7 | All rows with ACTIVE_FLAG = 'Y' |
| `EMPLOYEE_HISTORY` | INSERT (autonomous) | 8 | Via private `log_history` |
| `AUDIT_LOG` | INSERT | 9 | Via PKG_AUDIT.log_action |
| `NOTIFICATION_QUEUE` | INSERT | 10 | Via PKG_NOTIFICATION.send_notification |

**Tables NOT accessed (gaps):**

| Table | Expected Action | Why It Is Missing |
|---|---|---|
| `EMPLOYEE_DEPENDENTS` | Set `ACTIVE_FLAG = 'N'`; trigger COBRA for covered dependents | Not implemented — see BR-DEP-09 and PP-DEP-02 |
| `USER_SESSIONS` | Close / expire active sessions for the terminated employee | Not implemented — access revocation TODO |
| `USER_CREDENTIALS` | Deactivate credentials to prevent future login | Not implemented — access revocation TODO; table DDL not confirmed from analysed source (VQ-20) |
| `EMPLOYEE_BANK_ACCOUNTS` | Set `ACTIVE_FLAG = 'N'` to prevent post-termination disbursement | Not implemented — see PP-BA-07 |
| `PAYROLL_RUNS` / `PAYROLL_DETAILS` | Create a final pay run for wages through termination date | Not implemented — final pay TODO; `PKG_PAYROLL.calculate_final_pay` does not exist |
| `LEAVE_BALANCES` | Decrement `PENDING` field when PENDING leave is auto-cancelled | Not implemented — existing defect PP-08 |

---

### TODO Sub-step Deep Dive

#### Sub-step A: COBRA Integration

**Comment in source:** `-- TODO: Integrate with benefits system to trigger COBRA`

COBRA (Consolidated Omnibus Budget Reconciliation Act, 29 U.S.C. §§ 1161–1169) requires employers with ≥20 employees to offer continuation of health coverage to employees who lose coverage due to a qualifying event such as termination. The following table captures what the HRMS would need to implement, derived from the code structure and compliance context:

| Element | Expected Behaviour | Current State |
|---|---|---|
| Qualifying event detection | `terminate_employee` is called → termination is a qualifying event | Nothing is detected; no call made |
| Employee notification | Employee must be notified of COBRA election right within 14 days of the qualifying event | No notification to the terminated employee at all (only manager is notified) |
| Dependent coverage | COBRA applies to enrolled dependents; their records must be included in the notice | `EMPLOYEE_DEPENDENTS` is not touched; dependents remain ACTIVE with no COBRA notice |
| Election window | Employee has 60 days to elect COBRA continuation | No election tracking exists in the schema |
| Coverage duration | COBRA typically provides 18 months of continuation coverage after termination | No duration tracking in schema |
| Benefits system call | A benefits vendor or internal benefits module must receive the termination event | No benefits system integration exists; `PKG_INTEGRATION.export_benefits_feed` pushes no termination event |
| Dependent inactivation | Covered dependents' benefits should be held pending COBRA election, not immediately dropped | Currently dependents are left ACTIVE (BR-DEP-09); the correct sequencing (hold-for-COBRA vs. immediate-inactivation) is unresolved policy — see VQ-TERM-02 and VQ-DEP-04 |

#### Sub-step B: Access Revocation via PKG_SECURITY

**Comment in source:** `-- TODO: Revoke system access via PKG_SECURITY`

PKG_SECURITY provides session management and permission checking but has no `revoke_access` or equivalent procedure. The following table captures what access revocation would require:

| Element | Expected Behaviour | Current State |
|---|---|---|
| Terminate active sessions | All `USER_SESSIONS` rows for the employee with `STATUS = 'ACTIVE'` should be set to `CLOSED` or `EXPIRED` | Nothing is done; an employee who is mid-session at the moment of termination retains full system access until the 30-minute session timeout elapses (BR-72) |
| Block new logins | `PKG_SECURITY.authenticate` checks `EMPLOYMENT_STATUS = 'ACTIVE'` (BR-73); because the termination sets status to `TERMINATED`, the employee cannot log in after the procedure commits | This aspect works correctly by side-effect — the status check in `authenticate` implicitly prevents future login without any explicit credential revocation |
| Credential invalidation | A dedicated `USER_CREDENTIALS.ACTIVE_FLAG` or similar column may exist; setting it to `'N'` would provide a belt-and-suspenders block independent of employment status | Not implemented; `USER_CREDENTIALS` table structure is unconfirmed from analysed source (VQ-20) |
| Audit of revocation | An explicit access-revocation audit event should be logged, distinct from the generic `EMPLOYEES UPDATE` audit | Not implemented |
| Scope of PKG_SECURITY | No procedure named `revoke_access`, `deactivate_user`, or similar exists in the analysed `PKG_SECURITY` source | The TODO references a procedure that does not yet exist |

**Key finding:** New logins are already blocked by side-effect (EMPLOYMENT_STATUS = 'TERMINATED' fails the authenticate check). The residual risk is exclusively the in-flight session window — a terminated employee retains access for up to 30 minutes if a session was active at termination time.

#### Sub-step C: PKG_PAYROLL.calculate_final_pay

**Comment in source:** `-- TODO: Calculate final pay via PKG_PAYROLL.calculate_final_pay`

`PKG_PAYROLL.calculate_final_pay` is referenced as the target procedure but does not appear anywhere in the analysed `PKG_PAYROLL` source. This is a reference to a procedure that has not been created.

| Element | Expected Behaviour | Current State |
|---|---|---|
| Procedure existence | `PKG_PAYROLL.calculate_final_pay(p_emp_id, p_termination_date, …)` should exist | Does not exist; the TODO is a forward reference to a non-existent procedure |
| Earned wages calculation | Prorate the employee's period salary to cover only the days worked through `p_termination_date` within the current pay period | Not implemented; salary records are end-dated but no partial-period amount is calculated |
| PTO payout | Many jurisdictions require accrued but unused PTO to be paid out on termination (policy varies by state); the current leave balance in `LEAVE_BALANCES` contains the accrued balance | No PTO payout calculation exists; `LEAVE_BALANCES` data is available but unused by payroll on termination |
| Deduction pro-ration | Benefit and tax deductions must be prorated to the same partial period | Not implemented |
| Off-cycle payroll run | Final pay typically requires an off-cycle payroll run outside the normal pay period schedule | No off-cycle run capability exists; `create_payroll_run` requires an `OPEN` pay period |
| Pay period for final pay | The current pay period for `p_termination_date` may already be CLOSED (termination processed late) or a final pay period may need to be created | No mechanism to create or reopen a pay period for a specific employee's final pay |
| Tax withholding on final pay | Final pay is subject to the same federal and state withholding rules; lump-sum PTO payout may be subject to supplemental federal rate (22%) | No calculation logic exists |

---

### Business Rules Extracted (TODO Sub-steps)

| ID | Rule | Domain | Type | Severity | Confidence | Source |
|---|---|---|---|---|---|---|
| BR-TERM-01 | When an employee is terminated, a COBRA qualifying-event notification must be triggered to the employee and all covered dependents; the system currently generates no employee notification and makes no benefits system call at the time of termination. | Employee / Benefits | Compliance | Critical | ⚠️ LOW — policy not implemented; rule derived from federal COBRA requirement (29 U.S.C. §1166) | `terminate_employee` TODO comment; absence of any benefits call or employee notification |
| BR-TERM-02 | COBRA election rights apply to the terminated employee AND to any covered dependents enrolled in company health benefits; all such dependents must be included in the qualifying-event notification. | Employee / Benefits | Compliance | Critical | ⚠️ LOW — not implemented; cross-references BR-DEP-09 | `terminate_employee` TODO comment; `EMPLOYEE_DEPENDENTS` not touched by the procedure |
| BR-TERM-03 | The HRMS must revoke system access when an employee is terminated. New logins are blocked by side-effect (authenticate checks EMPLOYMENT_STATUS = 'ACTIVE'), but active sessions at the time of termination remain valid for up to 30 minutes. Explicit session closure is not implemented. | Employee / Security | Compliance | High | ✅ HIGH — login block confirmed; session gap confirmed | `PKG_SECURITY.authenticate` BR-73; `is_session_valid` BR-72; `terminate_employee` TODO comment |
| BR-TERM-04 | `PKG_PAYROLL.calculate_final_pay` is cited in `terminate_employee` as the target for final pay calculation; this procedure does not exist in `PKG_PAYROLL`. Final pay — including prorated wages through the termination date and any accrued PTO payout — is not calculated anywhere in the system. | Employee / Payroll | Compliance | Critical | ✅ HIGH — confirmed by absence of procedure in PKG_PAYROLL source | `terminate_employee` TODO comment; PKG_PAYROLL source contains no `calculate_final_pay` |
| BR-TERM-05 | Final pay must include at minimum: (a) prorated salary for the partial pay period through the termination date; (b) a payout of accrued but unused PTO balance (policy-dependent, required in some jurisdictions); and (c) cessation of recurring deductions as of the termination date. None of these calculations are currently performed. | Payroll | Compliance | Critical | ⚠️ LOW — inferred from standard HR/payroll practice; no implementation exists | `terminate_employee` deactivates salary records and pay elements but performs no pro-ration calculation |
| BR-TERM-06 | The `terminate_employee` procedure uses `SELECT … FOR UPDATE` without a `NOWAIT` or `WAIT n` clause. Any concurrent session holding a lock on the same employee record will block the termination call indefinitely. This contrasts with `transfer_employee`, which uses `FOR UPDATE NOWAIT` and fails immediately if the lock is held. | Employee | Operational | Medium | ✅ HIGH | `terminate_employee`: `FOR UPDATE` (no qualifier); `transfer_employee`: `FOR UPDATE NOWAIT` |
| BR-TERM-07 | The employee whose employment is terminated does not receive any notification from the system. Only the employee's manager is notified. Whether an employee notification is a business requirement is not evidenced in the code. | Employee | Soft Constraint | Medium | ✅ HIGH — confirmed by absence | `terminate_employee`: notification sent to `v_emp.MANAGER_EMP_ID` only |
| BR-TERM-08 | `p_reason` is a free-text VARCHAR2 parameter with no constrained value list. The same field drives `EMPLOYEES.TERMINATION_REASON`, which is used in turnover classification (BR-87). Voluntary terminations are classified only by exact string match `'VOLUNTARY'`. A free-text reason with any other casing or phrasing is counted as involuntary. | Employee / Reporting | Hard Constraint | Medium | ✅ HIGH | `terminate_employee` parameter definition; `PKG_REPORTING.turnover_report` BR-87 |
| BR-TERM-09 | `APPROVED` leave requests are not cancelled when an employee is terminated. Only `PENDING` leave is cancelled. Approved future leave remains in `STATUS = 'APPROVED'` indefinitely after termination. | Employee / Leave | Hard Constraint | Medium | ✅ HIGH — confirmed defect | `terminate_employee`: `WHERE STATUS = 'PENDING'` filter only; no handling of `STATUS = 'APPROVED'`; cross-references PP-09 |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-17 | Covered — auto-cancel of PENDING leave on termination; supplemental extraction adds BR-TERM-09 (APPROVED leave gap) and detail on balance inconsistency |
| BR-18 | Covered — end-dating of salary records and pay elements; supplemental extraction adds BR-TERM-05 (no prorated final pay) |
| BR-19 | Covered — manager notification; supplemental extraction adds BR-TERM-07 (employee not notified) |
| PP-08 | PENDING balance not decremented on auto-cancel — confirmed by step-by-step map; this extraction adds detailed table evidence |
| PP-09 | APPROVED leave not cancelled — confirmed; BR-TERM-09 added |
| BR-DEP-09, PP-DEP-02 | Dependents not inactivated — supplemental extraction adds BR-TERM-01 and BR-TERM-02 as the COBRA compliance consequence |
| PP-BA-07 | Bank accounts not inactivated — this extraction adds it to the Tables NOT Accessed gap list |
| VQ-20 (original) | `USER_CREDENTIALS` structure unconfirmed; access revocation analysis (BR-TERM-03) depends on this |
| Process: Employee Termination step 9 | Step 9 already notes TODOs; this extraction provides the full procedure-level evidence base, new BRs, and implementation gap analysis |
| Value Stream: Employee Lifecycle stage 5 | External dependencies notes COBRA/access/final pay as TODOs; this extraction expands all three |

---

### Pain Points (New — terminate_employee TODOs)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-TERM-01 | COBRA notification is not triggered on employee termination. The system has no mechanism to notify the employee or covered dependents of COBRA election rights. This is a federal compliance requirement (29 U.S.C. §1166). Any termination processed through the system creates an unreported qualifying event. | Potential DOL/IRS penalty exposure; manual COBRA notification process required outside the HRMS. | Critical |
| PP-TERM-02 | Active HRMS sessions are not closed when an employee is terminated. A terminated employee who was mid-session retains full system access for up to 30 minutes after the termination is committed. The window is bounded by the existing session timeout but is non-zero. | Security gap: a terminated employee with insider knowledge has a window to read or export data before expiry. | High |
| PP-TERM-03 | `PKG_PAYROLL.calculate_final_pay` is referenced in the termination procedure but does not exist. There is no mechanism to calculate prorated final wages or PTO payout. Payroll for a termination period must be handled entirely outside the HRMS. | Operational gap: every termination requires manual payroll calculation; risk of incorrect or late final pay, with potential state labour law penalties. | Critical |
| PP-TERM-04 | `terminate_employee` uses `FOR UPDATE` without `NOWAIT`. If another session holds a lock on the employee record, the termination call blocks indefinitely with no timeout and no user-visible message. This is inconsistent with `transfer_employee`, which uses `FOR UPDATE NOWAIT`. | Operational: HR may initiate a termination that appears to hang with no feedback until the blocking session releases the lock. | Medium |
| PP-TERM-05 | The termination reason field (`p_reason`) accepts free-text with no constrained value list. Because turnover reporting classifies voluntary vs. involuntary by exact match on `'VOLUNTARY'` (BR-87), any variation in reason text (e.g., `'Voluntary Resignation'`, `'voluntary'`) causes a voluntary termination to be counted as involuntary. | Turnover analytics are unreliable; voluntary attrition rates are systematically understated. Cross-references PP-21. | Medium |

---

### Automation Opportunities (New — terminate_employee TODOs)

| ID | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-TERM-01 | Implement COBRA notification trigger within `terminate_employee` | No COBRA notification of any kind | Add `PKG_NOTIFICATION.send_notification` call to the terminated employee with COBRA-specific content; add a corresponding notification to each active dependent (`EMPLOYEE_DEPENDENTS` where `ACTIVE_FLAG = 'Y'`); store the qualifying event date and COBRA election deadline (qualifying event date + 60 days) in a benefits events table | High — closes a federal compliance gap on every future termination |
| AO-TERM-02 | Implement active session closure on termination within `terminate_employee` | Active sessions persist for up to 30 minutes after termination | Add a call (e.g., `PKG_SECURITY.close_all_sessions(p_emp_id)`) that sets `USER_SESSIONS.STATUS = 'CLOSED'` for all ACTIVE sessions belonging to the terminated employee; implement the procedure in `PKG_SECURITY` if it does not exist | High — closes the access window immediately; low implementation effort |
| AO-TERM-03 | Implement `PKG_PAYROLL.calculate_final_pay` | Procedure referenced but does not exist | Create the procedure to: (a) prorate the current period salary to days worked through the termination date; (b) retrieve `LEAVE_BALANCES.ACCRUED - USED - PENDING` for PTO leave type and calculate a payout amount; (c) create a final payroll detail record; requires an off-cycle pay period mechanism or a special-purpose final-pay run type | High — eliminates all manual final pay calculation outside the HRMS |
| AO-TERM-04 | Replace free-text termination reason with a constrained LOV | `p_reason` is unconstrained free-text | Add a `LOOKUP_VALUES` category for termination reasons (VOLUNTARY, INVOLUNTARY, RESIGNATION, RETIREMENT, END_OF_CONTRACT, etc.); enforce at form level and optionally via a CHECK constraint on `EMPLOYEES.TERMINATION_REASON`; update turnover report to use the structured field | Medium — makes turnover analytics reliable; resolves PP-TERM-05 and PP-21 |
| AO-TERM-05 | Change `FOR UPDATE` to `FOR UPDATE WAIT 5` in `terminate_employee` | Indefinite blocking under lock contention | Replace `FOR UPDATE` with `FOR UPDATE WAIT 5` (5-second wait before raising `ORA-30006`); catch the exception and raise a meaningful application error: "Employee record is currently being edited. Please retry." | Low effort — consistent with `transfer_employee` pattern; prevents indefinite hangs |

---

### Validation Queue Items (New — terminate_employee TODOs)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-TERM-01 | Supplemental | Employee / Benefits | Confirm the COBRA notification policy: should the system send the COBRA notice directly (email to employee and dependents), or trigger a benefits administration workflow in an external system? If external, confirm the integration target (benefits vendor API, ADP feed event, or other). | ❓ UNRESOLVED — policy and integration target unknown |
| VQ-TERM-02 | Supplemental | Employee / Benefits | Confirm whether dependents of a terminated employee should be inactivated immediately on termination or held as ACTIVE pending COBRA election. Current state leaves them ACTIVE (BR-DEP-09); the correct sequencing requires a business policy decision (cross-reference VQ-DEP-04). | ❓ UNRESOLVED — business policy question |
| VQ-TERM-03 | Supplemental | Employee / Security | Confirm the `USER_CREDENTIALS` table structure. Specifically: does it have an `ACTIVE_FLAG`, a `LOCKED` column, or equivalent? Session closure alone (AO-TERM-02) covers the immediate gap, but credential-level lockout may be desirable as a belt-and-suspenders control. | ❓ UNRESOLVED — table DDL not confirmed; related to VQ-20 (original) |
| VQ-TERM-04 | Supplemental | Payroll | Confirm the business policy for PTO payout on termination. Some states (e.g., California) mandate payment of all accrued PTO; others do not. Confirm whether a payout multiplier (e.g., daily rate = annual salary / 260 working days) is the intended calculation method for `PKG_PAYROLL.calculate_final_pay`. | ❓ UNRESOLVED — policy decision required before `calculate_final_pay` can be specified |
| VQ-TERM-05 | Supplemental | Payroll | Confirm how off-cycle final pay runs should be created. The existing `PKG_PAYROLL.create_payroll_run` requires an `OPEN` pay period; a terminated employee's final pay may fall in a CLOSED or CALCULATING period. Confirm whether a special final-pay period type is intended, or whether the existing period should be used with a partial-run flag. | ❓ UNRESOLVED — architecture decision required for `PKG_PAYROLL.calculate_final_pay` design |

---

## Supplemental Extraction — PKG_LEAVE.initialize_balances (2026-08-04)

**Source file:** `plsql/packages/PKG_LEAVE.pkb`  
**Focus:** `PKG_LEAVE.initialize_balances` — all logic, tables, callers, and business rules associated with this procedure, plus the balance-management subsystem it underpins.

---

### Procedure Signature

```sql
PROCEDURE initialize_balances(
    p_emp_id IN NUMBER,
    p_year   IN NUMBER,
    p_user   IN VARCHAR2 DEFAULT USER
)
```

**Package:** `HRMS.PKG_LEAVE`  
**Visibility:** Internal (not exposed in the package spec as a public API; called only from within `PKG_LEAVE`)  
**Purpose:** Creates one `LEAVE_BALANCES` row per active leave type for a given employee and calendar year. All balance columns are initialised to zero. Duplicate inserts are silently swallowed via `DUP_VAL_ON_INDEX` exception handling.

---

### Step-by-Step Logic

| Step | Action | Table / Object | Notes |
|---|---|---|---|
| 1 | Open cursor over all leave types with `ACTIVE_FLAG = 'Y'` | `LEAVE_TYPES` | No ordering; processes all active types regardless of accrual flag |
| 2 | For each leave type: attempt `INSERT INTO LEAVE_BALANCES` | `LEAVE_BALANCES` | Uses `SEQ_LEAVE_BALANCE.NEXTVAL` for the primary key |
| 3 | Initialise all balance columns to zero | `LEAVE_BALANCES` | `OPENING_BALANCE = 0`, `ACCRUED = 0`, `USED = 0`, `ADJUSTMENT = 0`, `PENDING = 0` |
| 4 | Set audit columns | `LEAVE_BALANCES` | `CREATED_BY = p_user`, `CREATED_DATE = SYSDATE` |
| 5 | If `DUP_VAL_ON_INDEX` raised, swallow exception and continue | — | The `UNIQUE` constraint on `(EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR)` triggers this; the row already exists and is left unchanged |
| 6 | Loop continues to next leave type | — | No commit inside `initialize_balances`; transaction control is caller's responsibility |

---

### Tables Accessed

| Table | Operation | Columns Written | Notes |
|---|---|---|---|
| `LEAVE_TYPES` | SELECT (cursor) | — | Filter: `ACTIVE_FLAG = 'Y'`; reads `LEAVE_TYPE_ID` only |
| `LEAVE_BALANCES` | INSERT | `BALANCE_ID`, `EMP_ID`, `LEAVE_TYPE_ID`, `CALENDAR_YEAR`, `OPENING_BALANCE`, `ACCRUED`, `USED`, `ADJUSTMENT`, `PENDING`, `CREATED_BY`, `CREATED_DATE` | PK generated from `SEQ_LEAVE_BALANCE.NEXTVAL` |

**Not accessed by initialize_balances:** `EMPLOYEES`, `LEAVE_REQUESTS`, `LEAVE_ACCRUAL_LOG`, `HOLIDAYS`

---

### Caller Map (within PKG_LEAVE)

`initialize_balances` is called as a fallback pattern in three other procedures when an `UPDATE … WHERE EMP_ID = … AND LEAVE_TYPE_ID = … AND CALENDAR_YEAR = …` affects zero rows (`SQL%ROWCOUNT = 0`), meaning no balance record exists yet.

| Caller | Trigger Condition | Action After initialize_balances |
|---|---|---|
| `adjust_leave_balance` | `UPDATE LEAVE_BALANCES … SET ADJUSTMENT = ADJUSTMENT + p_adjustment` returns 0 rows | `initialize_balances` called; then the `UPDATE` is retried for the specific `LEAVE_TYPE_ID` |
| `run_monthly_accrual` | Inner loop: `UPDATE LEAVE_BALANCES … SET ACCRUED = ACCRUED + v_accrued` returns 0 rows | `initialize_balances` called; then the `UPDATE` is retried with `ACCRUED = v_accrued` (not `ACCRUED + v_accrued`) — see defect BR-LIB-05 |
| `process_carryover` | Before the `UPDATE` that sets `CARRYOVER_FROM_PREV` / `OPENING_BALANCE` in the target year | `initialize_balances` called unconditionally for the next year's record; no `SQL%ROWCOUNT` guard — it always runs before the `UPDATE` |

---

### Business Rules Extracted

| ID | Rule | Domain | Type | Severity | Confidence | Source |
|---|---|---|---|---|---|---|
| BR-LIB-01 | `initialize_balances` creates exactly one `LEAVE_BALANCES` row per active leave type (filtered by `LEAVE_TYPES.ACTIVE_FLAG = 'Y'`) for the specified employee and calendar year. All five balance columns (`OPENING_BALANCE`, `ACCRUED`, `USED`, `ADJUSTMENT`, `PENDING`) are set to zero at creation. | Leave / Balances | Hard Constraint | Low | ✅ HIGH | `initialize_balances` body |
| BR-LIB-02 | If a balance row for the given `(EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR)` already exists when `initialize_balances` is called, the existing row is left entirely unchanged. The `DUP_VAL_ON_INDEX` exception is caught and silently discarded (`NULL`). There is no merge or update path. | Leave / Balances | Hard Constraint | Low | ✅ HIGH | `initialize_balances` exception handler |
| BR-LIB-03 | Balance rows are created for ALL active leave types at once — including non-accrual types (where `ACCRUAL_FLAG = 'N'`). The procedure does not discriminate by accrual flag, carryover flag, or any other leave-type property. A row is created for every type with `ACTIVE_FLAG = 'Y'`. | Leave / Balances | Hard Constraint | Low | ✅ HIGH | `initialize_balances`: `SELECT LEAVE_TYPE_ID FROM LEAVE_TYPES WHERE ACTIVE_FLAG = 'Y'` — no additional filter |
| BR-LIB-04 | `initialize_balances` performs no commit. Transaction control is entirely delegated to the calling procedure. In `run_monthly_accrual`, a commit is issued every 100 employees; in `process_carryover`, a single commit is issued at the end. In `adjust_leave_balance`, there is no explicit commit — the caller is expected to commit. | Leave / Balances | Operational | Low | ✅ HIGH | Absence of `COMMIT` in `initialize_balances`; commit pattern in each caller |
| BR-LIB-05 | **Defect — accrual retry uses `ACCRUED = v_accrued` instead of `ACCRUED + v_accrued`.** In `run_monthly_accrual`, after `initialize_balances` is called, the retry UPDATE sets `ACCRUED = v_accrued` (assignment), not `ACCRUED = ACCRUED + v_accrued` (increment). For a freshly created row this is equivalent (the row starts at zero). However, if the row was created by a prior call and `SQL%ROWCOUNT = 0` was returned erroneously (e.g., due to a transaction isolation issue), the retry would overwrite any previously accrued value rather than adding to it. | Leave / Payroll | Defect | Medium | ✅ HIGH — confirmed by direct code comparison | `run_monthly_accrual` retry block: `SET ACCRUED = v_accrued` vs. first-attempt block: `SET ACCRUED = ACCRUED + v_accrued` |
| BR-LIB-06 | Leave balance rows are never created at hire time. The `hire_employee` procedure (in `PKG_EMPLOYEE`) does not call `initialize_balances`. Balance records are created lazily: either when the first accrual, adjustment, or carryover operation is attempted and finds no row. An employee who has never had a leave operation will have no `LEAVE_BALANCES` rows. | Leave / Employee Lifecycle | Soft Constraint | Medium | ✅ HIGH — confirmed by absence of `initialize_balances` call in `hire_employee` path; caller map shows all calls are in-band within `PKG_LEAVE` only |
| BR-LIB-07 | `initialize_balances` is an internal procedure; it is not intended to be called as a public API. It carries no input validation: negative years, non-existent employee IDs, and NULL values for `p_emp_id` or `p_year` will propagate to the `INSERT` statement and raise database-level constraint errors uncaught at the procedure level. | Leave / Balances | Hard Constraint | Low | ✅ HIGH | No validation logic in `initialize_balances` body |
| BR-LIB-08 | The leave balance formula used throughout `PKG_LEAVE` is: **Available = OPENING_BALANCE + ACCRUED − USED + ADJUSTMENT − PENDING**. `initialize_balances` seeds all five components at zero, making the initial available balance exactly zero for every leave type. | Leave / Balances | Hard Constraint | Low | ✅ HIGH | `get_leave_balance`: `SELECT OPENING_BALANCE + ACCRUED - USED + ADJUSTMENT - PENDING` |
| BR-LIB-09 | `OPENING_BALANCE` is not set by `initialize_balances` except to zero. The only mechanism that sets a non-zero `OPENING_BALANCE` is `process_carryover`, which copies the prior year's remaining balance into the new year's `OPENING_BALANCE`. A new employee hired mid-year will always start with `OPENING_BALANCE = 0` for all leave types; there is no mechanism to set an initial opening balance at hire (e.g., a policy-granted starter allowance). | Leave / Employee Lifecycle | Soft Constraint | Medium | ✅ HIGH | `initialize_balances` hardcodes `OPENING_BALANCE = 0`; `process_carryover` is the only setter of a non-zero `OPENING_BALANCE` |
| BR-LIB-10 | When `process_carryover` calls `initialize_balances`, it does so unconditionally before executing the UPDATE that sets `CARRYOVER_FROM_PREV` and `OPENING_BALANCE`. Because `initialize_balances` uses `DUP_VAL_ON_INDEX` suppression (BR-LIB-02), this is safe to call even when the target row already exists — the existing row is left untouched and the subsequent UPDATE proceeds. This pattern is the correct safe-initialise-before-update idiom in this codebase. | Leave / Balances | Operational | Low | ✅ HIGH | `process_carryover` body: `initialize_balances(bal_rec.EMP_ID, v_next_year, p_user)` immediately before `UPDATE LEAVE_BALANCES … WHERE CALENDAR_YEAR = v_next_year` |

---

### Balance Lifecycle Map

The following shows how `LEAVE_BALANCES` columns are set and modified across the full lifecycle of a balance record, anchored to `initialize_balances` as the creation point.

| Lifecycle Event | Procedure | Column(s) Changed |
|---|---|---|
| **Row creation** | `initialize_balances` | All columns set to 0 |
| **Monthly accrual** | `run_monthly_accrual` | `ACCRUED += accrual_rate` (capped at `MAX_BALANCE`) |
| **Leave submitted (pending)** | `submit_leave_request` | `PENDING += total_days` |
| **Leave approved** | `approve_leave_request` | `PENDING -= total_days`; `USED += total_days` |
| **Leave rejected** | `reject_leave_request` | `PENDING -= total_days` |
| **Leave cancelled (was PENDING)** | `cancel_leave_request` | `PENDING -= total_days` |
| **Leave cancelled (was APPROVED)** | `cancel_leave_request` | `USED -= total_days` |
| **Manual adjustment** | `adjust_leave_balance` | `ADJUSTMENT += p_adjustment` (positive or negative) |
| **Year-end carryover** | `process_carryover` | `OPENING_BALANCE = carryover_amount`; `CARRYOVER_FROM_PREV = carryover_amount`; `CARRYOVER_EXPIRY_DT` optionally set |
| **Carryover expiry** | `expire_carryover` | `ADJUSTMENT -= CARRYOVER_FROM_PREV`; `CARRYOVER_FROM_PREV = 0` |

**Defect note on `expire_carryover`:** Expiry reduces `ADJUSTMENT` (not `OPENING_BALANCE`), which can produce a confusing negative `ADJUSTMENT` value. If run twice on the same day, it double-subtracts. Identified in the capability map (⚠️ Corrected row for "Expire Carryover").

---

### Pain Points (New — initialize_balances)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-LIB-01 | Leave balance rows are created lazily (on first accrual or adjustment), not at hire time. If an employee is eligible for leave immediately on hire but no accrual or adjustment is run before they try to submit a request, `get_leave_balance` returns 0 (the `NO_DATA_FOUND` branch) and `submit_leave_request` rejects the request with "Insufficient leave balance" for any accrual-based leave type. | New hires may be unable to submit leave in the gap between hire and first accrual run, even if they are policy-eligible. HR must manually trigger an adjustment or wait for the monthly accrual batch. | Medium |
| PP-LIB-02 | `initialize_balances` creates rows for ALL active leave types, including types that are not applicable to a specific employee (e.g., maternity leave for male employees, or leave types restricted to specific countries/grades). The system has no concept of per-employee leave type eligibility filtering in balance initialisation. This creates zero-balance rows for inapplicable leave types, which pollute the employee's leave balance view and may appear in self-service portals. | Data quality issue; employees may see leave types they are not entitled to. | Low |
| PP-LIB-03 | There is no mechanism to set a non-zero `OPENING_BALANCE` at hire for policy-granted starter allowances (e.g., "employees receive 5 days of PTO immediately on hire"). `initialize_balances` always sets `OPENING_BALANCE = 0`; the only non-zero setter is `process_carryover`. Any starter allowance must currently be applied as a manual `adjust_leave_balance` call after the row is created. | New hire leave entitlements require a separate manual step; risk of omission. | Medium |
| PP-LIB-04 | The accrual retry in `run_monthly_accrual` uses `ACCRUED = v_accrued` instead of `ACCRUED = ACCRUED + v_accrued` (BR-LIB-05). While this is equivalent for a freshly initialised row, it is logically incorrect and becomes data-destructive if the `SQL%ROWCOUNT = 0` condition is ever triggered on an existing row due to a concurrent-write race or isolation anomaly. The inconsistency will confuse future maintainers and is a silent data integrity risk. | Potential accrual data loss in edge cases; code intent is unclear and inconsistent with the first-attempt UPDATE. | Medium |

---

### Automation Opportunities (New — initialize_balances)

| ID | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-LIB-01 | Call `initialize_balances` from `hire_employee` at hire time | Balance rows are created lazily; new hires cannot submit leave until the first accrual or adjustment runs | Add `PKG_LEAVE.initialize_balances(p_emp_id, EXTRACT(YEAR FROM SYSDATE), p_user)` as a final step in `hire_employee`; this ensures every new employee has balance rows from day one and removes the eligibility gap | Medium — eliminates the new-hire leave submission gap (PP-LIB-01) |
| AO-LIB-02 | Add per-employee leave type eligibility filtering to `initialize_balances` | All active leave types receive a balance row regardless of applicability | Introduce a join or filter condition (e.g., against an `EMPLOYEE_LEAVE_ELIGIBILITY` table or by `LEAVE_TYPES.GENDER_RESTRICTION`, `GRADE_MINIMUM`) so that inapplicable types are excluded at initialisation | Low — reduces data clutter; dependent on whether eligibility rules are being stored anywhere in the schema |
| AO-LIB-03 | Add an optional `p_opening_balance` parameter to `initialize_balances` | Opening balance is always zero; starter allowances require a separate `adjust_leave_balance` call | Accept an optional `p_opening_balance IN NUMBER DEFAULT 0` parameter and use it in the `INSERT`; update callers to pass 0 explicitly; HR configuration screen passes the policy value for each leave type at hire | Low–Medium — eliminates the manual starter allowance step (PP-LIB-03) |
| AO-LIB-04 | Fix the accrual retry assignment defect in `run_monthly_accrual` | `ACCRUED = v_accrued` instead of `ACCRUED = ACCRUED + v_accrued` in the retry path | Change the retry UPDATE to `SET ACCRUED = ACCRUED + v_accrued` to match the first-attempt pattern | Low effort — one-line fix; eliminates BR-LIB-05 and PP-LIB-04 |

---

### Validation Queue Items (New — initialize_balances)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-LIB-01 | Supplemental | Leave / Employee Lifecycle | Confirm whether the business requires leave balance rows to be created at hire time. If yes, `AO-LIB-01` (add `initialize_balances` call to `hire_employee`) should be implemented. If no, confirm the intended workflow for new hires submitting leave before the first monthly accrual run. | ❓ UNRESOLVED — business policy decision required |
| VQ-LIB-02 | Supplemental | Leave / Balances | Confirm whether any leave types should be restricted to specific employee subsets (e.g., by gender, grade, country) and whether those eligibility rules exist anywhere in the schema. This would inform whether `AO-LIB-02` (per-employee filtering in `initialize_balances`) is feasible. | ❓ UNRESOLVED — eligibility rules not evidenced in analysed source |
| VQ-LIB-03 | Supplemental | Leave / Employee Lifecycle | Confirm whether any leave type has a policy-granted starter allowance (i.e., non-zero opening balance at hire). If yes, confirm how the allowance amount is stored — in `LEAVE_TYPES` or elsewhere — and whether `AO-LIB-03` (optional `p_opening_balance` parameter) is the right delivery mechanism. | ❓ UNRESOLVED — not evidenced in source; business policy decision |
| VQ-LIB-04 | Supplemental | Leave / Balances | Confirm the intended behaviour when `initialize_balances` is called for a year that already has complete balance records (all leave types present). Current behaviour: silent no-op per type (DUP_VAL_ON_INDEX suppression). Is this the correct idempotency contract, or should re-initialisation to zero be possible in some circumstances (e.g., year-end reset)? | ❓ UNRESOLVED — the current silent-skip behaviour may be correct but should be confirmed as intentional |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-38 through BR-48 (Leave Management rules from first pass) | `initialize_balances` is the balance row factory underpinning all leave balance operations; these rules assume balance rows exist — `initialize_balances` is the gate |
| PP-08 | PENDING balance not decremented on PENDING leave auto-cancel during termination — the balance row must exist for this to matter; `initialize_balances` is the row's origin |
| PP-09 | APPROVED leave not cancelled on termination — same dependency |
| VQ-TERM-04 | PTO payout on termination depends on `LEAVE_BALANCES.ACCRUED - USED - PENDING` being accurate; the accuracy of that formula depends on `initialize_balances` having been called and the accrual retry defect (BR-LIB-05) not having corrupted `ACCRUED` |
| AO-TERM-03 | `calculate_final_pay` implementation would read `LEAVE_BALANCES` — correct initialisation (AO-LIB-01) and the retry fix (AO-LIB-04) are prerequisites for reliable final-pay PTO payout |

---

---

## Supplemental Extraction — `PKG_PERFORMANCE.get_rating_distribution`

**Source:** `plsql/packages/PKG_PERFORMANCE.pkb` (recovered from file_cache.json)
**Package:** `HRMS.PKG_PERFORMANCE`
**Date extracted:** 2026-08-04

---

### Function Signature

```sql
FUNCTION get_rating_distribution(
    p_cycle_id IN NUMBER,
    p_dept_id  IN NUMBER DEFAULT NULL
) RETURN SYS_REFCURSOR
```

- Returns a `SYS_REFCURSOR` (not a named type cursor; callers receive a weakly-typed ref cursor).
- `p_dept_id` is optional — `NULL` means all departments.

---

### Tables Accessed

| Table | Join Type | Columns Read | Purpose |
|---|---|---|---|
| `PERFORMANCE_REVIEWS` | Primary (driving) | `RATING_LABEL`, `OVERALL_RATING`, `CYCLE_ID`, `EMP_ID` | Source of rating data; filtered by cycle and non-null rating |
| `EMPLOYEES` | INNER JOIN on `EMP_ID` | `EMP_ID`, `DEPT_ID` | Required only when `p_dept_id IS NOT NULL` — provides department filter |

No writes, no DML. Read-only query.

---

### Full Query Logic

```sql
SELECT pr.RATING_LABEL,
       COUNT(*) AS COUNT,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS PERCENTAGE
FROM   PERFORMANCE_REVIEWS pr
JOIN   EMPLOYEES e ON pr.EMP_ID = e.EMP_ID
WHERE  pr.CYCLE_ID    = p_cycle_id
AND    pr.OVERALL_RATING IS NOT NULL
AND    (p_dept_id IS NULL OR e.DEPT_ID = p_dept_id)
GROUP BY pr.RATING_LABEL
ORDER BY MIN(pr.OVERALL_RATING) DESC
```

**Key mechanics:**

1. **Null-rating exclusion** — `pr.OVERALL_RATING IS NOT NULL` filters out reviews that have not yet received a manager rating (status `NOT_STARTED`, `SELF_REVIEW`, `MANAGER_REVIEW`). Only `COMPLETED` and `ACKNOWLEDGED` reviews contribute to the distribution.
2. **Analytic percentage** — `SUM(COUNT(*)) OVER ()` is a window function computing the total row count across all groups. The percentage is therefore relative to the filtered set, not the full cycle population. Reviews with null ratings are excluded from the denominator.
3. **Optional department filter** — `(p_dept_id IS NULL OR e.DEPT_ID = p_dept_id)` short-circuits to all departments when `p_dept_id` is omitted. The `JOIN EMPLOYEES` is always executed even when no department filter is applied — a minor but unnecessary join when `p_dept_id IS NULL`.
4. **Sort order** — `ORDER BY MIN(pr.OVERALL_RATING) DESC` sorts labels by their numeric floor descending, so "Exceptional" (≥ 4.5) appears first and "Unsatisfactory" (< 1.5) last, matching the rating band hierarchy from `submit_manager_review`.

---

### Rating Label Mapping (from `submit_manager_review`)

The `RATING_LABEL` column is populated by `submit_manager_review` using this CASE expression:

| Numeric Range | Label |
|---|---|
| ≥ 4.5 | `Exceptional` |
| ≥ 3.5 and < 4.5 | `Exceeds Expectations` |
| ≥ 2.5 and < 3.5 | `Meets Expectations` |
| ≥ 1.5 and < 2.5 | `Needs Improvement` |
| < 1.5 | `Unsatisfactory` |

Ratings must be between 1.0 and 5.0 (enforced by `submit_manager_review` with error -20403). The mapping is hardcoded in `submit_manager_review` and not stored in a configuration table.

---

### Business Rules (New — `get_rating_distribution`)

| ID | Rule | Source | Notes |
|---|---|---|---|
| BR-PERF-01 | Only reviews with a non-null `OVERALL_RATING` are included in the distribution | `WHERE pr.OVERALL_RATING IS NOT NULL` | Reviews in status `NOT_STARTED`, `SELF_REVIEW`, `MANAGER_REVIEW` are silently excluded; the denominator reflects only rated reviews, not all reviews in the cycle |
| BR-PERF-02 | Distribution percentages are relative to the rated-review population, not the full cycle headcount | `SUM(COUNT(*)) OVER ()` window function | If 100 employees are in a cycle but only 60 have been rated, percentages sum to 100% across those 60; the 40 unrated are invisible |
| BR-PERF-03 | `p_dept_id = NULL` returns the organisation-wide distribution; any non-null value restricts to that department | `(p_dept_id IS NULL OR e.DEPT_ID = p_dept_id)` | No multi-department slice or hierarchy roll-up is supported; department-group aggregations require multiple calls |
| BR-PERF-04 | Rating labels are always sorted Exceptional → Unsatisfactory (descending by numeric floor) | `ORDER BY MIN(pr.OVERALL_RATING) DESC` | This is a presentational rule: callers receive rows in a fixed descending order regardless of label frequency |
| BR-PERF-05 | Ratings are bounded to [1.0, 5.0] and mapped to five discrete labels | `submit_manager_review` CASE expression + error -20403 guard | The five labels are the only possible values in `RATING_LABEL`; no free-text or partial labels can appear |
| BR-PERF-06 | The distribution excludes employees who have left the organisation if their `EMPLOYEES` row has been hard-deleted | `JOIN EMPLOYEES e ON pr.EMP_ID = e.EMP_ID` (INNER JOIN) | If an employee row is removed after a review is completed, that review is silently dropped from the distribution — potential undercount for historical cycles |
| BR-PERF-07 | Rating label is denormalised onto `PERFORMANCE_REVIEWS.RATING_LABEL` at the time of manager submission | `submit_manager_review` UPDATE | The label is not computed at query time; if the label boundaries were ever changed, historical `RATING_LABEL` values would not be recalculated retroactively |

---

### Process Context — Where `get_rating_distribution` Fits

```
Cycle lifecycle:
  DRAFT → OPEN → (reviews generated) → reviews completed → CLOSED

get_rating_distribution is a reporting/analytics read at any point after
reviews reach COMPLETED status. It is typically called:
  • During cycle close — HR calibration view of the draft distribution
  • After cycle close — final distribution for HR records / reporting
  • By department — manager or HR BP view of their slice

It has no side effects and is safe to call at any cycle status.
```

**Callers not evidenced in source** — no procedure in the analysed source calls `get_rating_distribution`. It is exposed as a package function for direct client invocation (application layer, reporting tool, or ad-hoc SQL).

---

### Related Procedures in `PKG_PERFORMANCE`

| Procedure / Function | Relationship to `get_rating_distribution` |
|---|---|
| `submit_manager_review` | Populates `OVERALL_RATING` and `RATING_LABEL` — the two columns this function aggregates; also enforces the [1.0, 5.0] range and the five-label mapping |
| `create_review_cycle` | Creates the `REVIEW_CYCLES` row that `p_cycle_id` references |
| `open_review_cycle` / `close_review_cycle` | Manage cycle status; `get_rating_distribution` is useful as a pre-close calibration check |
| `generate_reviews_for_cycle` | Bulk-creates `PERFORMANCE_REVIEWS` rows; the unrated rows it creates are excluded from the distribution by BR-PERF-01 |
| `get_team_reviews` | Returns individual review rows for a manager's team; `get_rating_distribution` is the aggregate complement — team-level vs. org/dept-level summary |

---

### Pain Points (New — `get_rating_distribution`)

| ID | Description | Severity | Root Cause |
|---|---|---|---|
| PP-PERF-01 | The denominator excludes unrated reviews, so a department with many in-progress reviews shows a distribution that looks complete but covers only a subset of its population — misleading during mid-cycle calibration | Medium | BR-PERF-02: `OVERALL_RATING IS NOT NULL` filter removes unrated reviews from both numerator and denominator silently |
| PP-PERF-02 | No multi-department or hierarchy roll-up: getting a division-level distribution requires one call per department and manual aggregation by the caller | Low–Medium | BR-PERF-03: `p_dept_id` is a scalar equality filter; no `IN` list, no org-hierarchy join |
| PP-PERF-03 | The `JOIN EMPLOYEES` is unconditional — even for an org-wide query (`p_dept_id IS NULL`) the join is always executed, adding unnecessary overhead on large employee tables | Low | Minor query design issue; the join is needed only for the department filter |
| PP-PERF-04 | Rating label boundaries are hardcoded in `submit_manager_review`'s CASE expression and not stored in a configuration table; changing them requires a code deployment and does not retroactively relabel historical reviews (BR-PERF-07) | Medium | Denormalised label design; no `RATING_BANDS` or equivalent reference table |

---

### Automation Opportunities (New — `get_rating_distribution`)

| ID | Opportunity | Problem Solved | Implementation Sketch | Effort / Impact |
|---|---|---|---|---|
| AO-PERF-01 | Add a `p_include_unrated IN BOOLEAN DEFAULT FALSE` parameter and expose an `UNRATED_COUNT` column alongside the distribution | PP-PERF-01: callers currently cannot tell how many employees have not yet been rated; the denominator silently excludes them | Add a UNION or outer-query branch that counts `OVERALL_RATING IS NULL` rows and includes them as a pseudo-label row (or as a separate OUT parameter); expose completion percentage = rated / total | Low–Medium effort; high reporting value during live cycles |
| AO-PERF-02 | Replace the scalar `p_dept_id` with an optional `p_dept_ids SYS.ODCINUMBERLIST` parameter to allow multi-department slicing in one call | PP-PERF-02 | Change filter to `(p_dept_id IS NULL OR e.DEPT_ID MEMBER OF p_dept_ids)` using collection membership; maintain backward-compatibility with a scalar overload | Medium effort; eliminates N-call pattern for division-level views |
| AO-PERF-03 | Externalise rating band boundaries into a `RATING_BANDS` configuration table and compute `RATING_LABEL` at query time | PP-PERF-04 | Create `RATING_BANDS (BAND_ID, LABEL, MIN_SCORE, MAX_SCORE, SORT_ORDER)`; change `submit_manager_review` to look up label at submission time; `get_rating_distribution` can then join `RATING_BANDS` for the sort key instead of `MIN(pr.OVERALL_RATING)` | High effort; eliminates hardcoded label rule; enables runtime reconfiguration without redeployment |

---

### Validation Queue Items (New — `get_rating_distribution`)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-PERF-01 | Supplemental | Performance / Reporting | Confirm whether the business expects the distribution percentage to be calculated against all employees in the cycle (including unrated) or only those with a completed rating. Current behaviour (BR-PERF-02) uses rated-only as the denominator — this may be intentional for calibration purposes but should be confirmed with HR stakeholders. | ❓ UNRESOLVED — business policy decision required |
| VQ-PERF-02 | Supplemental | Performance / Reporting | Confirm whether any reporting requirement calls for a division-level or cross-department distribution view. If yes, AO-PERF-02 (collection-parameter overload) should be prioritised. | ❓ UNRESOLVED — no evidence of multi-department use in analysed source |
| VQ-PERF-03 | Supplemental | Performance / Data Integrity | Confirm whether `RATING_LABEL` should ever be recomputed for historical reviews if rating band boundaries change. Current design (BR-PERF-07) freezes the label at submission time. An `UPDATE PERFORMANCE_REVIEWS SET RATING_LABEL = ...` migration script would be needed if bands are retroactively adjusted. | ❓ UNRESOLVED — policy decision; depends on whether band boundaries are fixed or HR-configurable |
| VQ-PERF-04 | Supplemental | Performance / Data Integrity | Confirm referential integrity between `PERFORMANCE_REVIEWS.EMP_ID` and `EMPLOYEES.EMP_ID`. The INNER JOIN in `get_rating_distribution` silently drops completed reviews for any employee whose row has been hard-deleted (BR-PERF-06). Determine whether the schema enforces a FK constraint and whether soft-delete is the intended employee-removal pattern. | ❓ UNRESOLVED — FK constraint presence not confirmed in analysed source |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-01 through BR-107 (first pass — general HRMS rules) | `get_rating_distribution` is a read-only reporting function; it does not create or modify the data those rules govern |
| PP-PERF-01 | Connects to the broader pattern of silent data exclusion seen in `EMPLOYEE_DEPENDENTS` (`BENEFITS_ENROLLED` never read, VQ-DEP-01) and bank accounts (never read, VQ-BA-03) — a recurring theme of incomplete visibility into actual system state |
| PP-PERF-04 (hardcoded rating bands) | Mirrors the hardcoded label design in `submit_manager_review`; same root cause; addressed together by AO-PERF-03 |
| VQ-TERM-04 | PTO payout on termination requires accurate leave balances; by analogy, a final-cycle distribution snapshot at termination time would require `get_rating_distribution` to be called before `close_review_cycle` |
| AO-TERM-03 | `calculate_final_pay` (non-existent) would need the employee's current rating for merit-pay or severance calculations — making `get_rating_distribution` (or the underlying `OVERALL_RATING`) a data dependency for that future implementation |
| VQ-20 (original), VQ-6 (PAID status) | Unrelated — those concern payroll and session state, not leave balances |

---

---

## Supplemental Extraction — `PKG_PERFORMANCE.generate_reviews_for_cycle`

**Source:** `plsql/packages/PKG_PERFORMANCE.pkb` (recovered from `file_cache.json`)
**Extraction date:** 2026-08-04

---

### Procedure Signature

```sql
PROCEDURE generate_reviews_for_cycle(
    p_cycle_id IN NUMBER,
    p_user     IN VARCHAR2 DEFAULT USER
)
```

**Purpose:** Bulk-creates one `PERFORMANCE_REVIEWS` row per active employee who has a manager, for a given review cycle. Intended to be called once after a cycle is opened (`open_review_cycle`) to seed the review population for the cycle.

---

### Execution Flow (Step-by-Step)

| Step | Action | Detail |
|---|---|---|
| 1 | Declare counter | `v_count NUMBER := 0` — tracks how many reviews were successfully created |
| 2 | Open implicit cursor | `SELECT EMP_ID, MANAGER_EMP_ID FROM EMPLOYEES WHERE EMPLOYMENT_STATUS = 'ACTIVE' AND MANAGER_EMP_ID IS NOT NULL` — iterates over every active, managed employee |
| 3 | For each employee: call `create_review` | Delegates to `PKG_PERFORMANCE.create_review(p_cycle_id, emp_rec.EMP_ID, emp_rec.MANAGER_EMP_ID, p_user)` — inserts one `PERFORMANCE_REVIEWS` row per employee and sends an email notification to the employee |
| 4 | Increment counter | `v_count := v_count + 1` on each successful creation |
| 5 | Suppress duplicates | `EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL` — silently skips employees who already have a review for this cycle; re-runs are idempotent |
| 6 | COMMIT | Issues a hard `COMMIT` at the end of the loop — commits all inserted rows in a single transaction |
| 7 | Emit output line | `DBMS_OUTPUT.PUT_LINE('Generated ' || v_count || ' reviews for cycle ' || p_cycle_id)` — reports to console only; no structured return value |

---

### Tables Accessed

| Table | Operation | Condition |
|---|---|---|
| `EMPLOYEES` | SELECT (implicit cursor) | `EMPLOYMENT_STATUS = 'ACTIVE' AND MANAGER_EMP_ID IS NOT NULL` |
| `PERFORMANCE_REVIEWS` | INSERT (via `create_review`) | One row per qualifying employee |
| `REVIEW_CYCLES` | None directly | `p_cycle_id` is passed through to `create_review` but not validated here |
| Notification table (via `PKG_NOTIFICATION`) | INSERT/UPDATE (side-effect of `create_review`) | Email notification sent to each employee |

---

### Business Rules (New — `generate_reviews_for_cycle`)

| ID | Rule | Evidence |
|---|---|---|
| BR-GRC-01 | Only employees with `EMPLOYMENT_STATUS = 'ACTIVE'` are included in a review cycle bulk-generation. Inactive, terminated, or suspended employees do not receive a review record. | Cursor WHERE clause: `EMPLOYMENT_STATUS = 'ACTIVE'` |
| BR-GRC-02 | Only employees who have a direct manager (`MANAGER_EMP_ID IS NOT NULL`) are included. Top-of-hierarchy employees (e.g., CEO) with no manager are silently excluded. | Cursor WHERE clause: `MANAGER_EMP_ID IS NOT NULL` |
| BR-GRC-03 | The reviewer assigned to each generated review is always the employee's current direct manager (`MANAGER_EMP_ID`). There is no provision to assign an alternate or skip-level reviewer at generation time. | `create_review(p_cycle_id, emp_rec.EMP_ID, emp_rec.MANAGER_EMP_ID, p_user)` |
| BR-GRC-04 | All generated reviews are created with `REVIEW_TYPE = 'ANNUAL'` and initial `STATUS = 'NOT_STARTED'` (enforced inside `create_review`). | See `create_review` INSERT values |
| BR-GRC-05 | If a review already exists for an employee in this cycle (detected by a unique index violation), the duplicate is silently skipped and the existing review is left unchanged. The procedure is therefore idempotent — calling it multiple times for the same cycle is safe. | `EXCEPTION WHEN DUP_VAL_ON_INDEX THEN NULL` |
| BR-GRC-06 | Each employee receives an email notification ("Performance Review Initiated") at generation time, fired inside `create_review` via `PKG_NOTIFICATION.send_notification`. Notifications are sent even on a re-run if the unique index does not fire (i.e., if the review was manually deleted and re-created). | `PKG_NOTIFICATION.send_notification` call in `create_review` |
| BR-GRC-07 | The cycle's status (`REVIEW_CYCLES.STATUS`) is **not validated** before generating reviews. The procedure will silently create reviews for a `DRAFT`, `OPEN`, or even `CLOSED` cycle without error. | No check against `REVIEW_CYCLES` in this procedure |
| BR-GRC-08 | All inserts are committed in a single `COMMIT` at the end of the loop. There is no savepoint or partial rollback: if the commit fails, no reviews are persisted. Conversely, any failure after the commit (e.g., in the `DBMS_OUTPUT` call) leaves all inserted rows permanently committed. | `COMMIT;` at the end of the loop body |
| BR-GRC-09 | The count of reviews actually created (`v_count`) is reported only via `DBMS_OUTPUT`. There is no OUT parameter, no return value, and no logging to the audit table (`PKG_AUDIT.log_action` is called inside `create_review` per-row, not at the bulk level). | `DBMS_OUTPUT.PUT_LINE(...)` — no structured output |
| BR-GRC-10 | The procedure uses the caller-supplied `p_user` value (defaulting to `USER`) for both `create_review` calls and the audit trail. The generated-by identity propagates to each individual review's `CREATED_BY` column. | `p_user` passed through to `create_review` |

---

### Process Flow — Bulk Review Generation

```
HR Administrator
      │
      ▼
open_review_cycle(p_cycle_id)          ← precondition (not enforced in code)
      │
      ▼
generate_reviews_for_cycle(p_cycle_id)
      │
      ├── SELECT active employees with manager (EMPLOYEES)
      │         │
      │         └── FOR EACH employee_rec
      │               │
      │               ├── create_review(cycle_id, emp_id, manager_id)
      │               │         │
      │               │         ├── INSERT PERFORMANCE_REVIEWS (STATUS='NOT_STARTED')
      │               │         └── PKG_NOTIFICATION → email to employee
      │               │
      │               ├── v_count++
      │               │
      │               └── (DUP_VAL_ON_INDEX → skip silently)
      │
      ├── COMMIT
      │
      └── DBMS_OUTPUT: "Generated N reviews for cycle C"
```

---

### Caller Map

No callers found in the analysed source. The procedure is designed for direct invocation by an HR administrator or a scheduling job. It is the expected entry point after `open_review_cycle` but there is no enforced call chain.

---

### Pain Points (New — `generate_reviews_for_cycle`)

| ID | Description | Severity | Root Cause |
|---|---|---|---|
| PP-GRC-01 | The cycle's status is never checked before generating reviews. An HR user could call this against a `DRAFT` cycle (not yet open) or a `CLOSED` cycle, creating reviews in an incorrect lifecycle state with no warning. | High | BR-GRC-07: no `REVIEW_CYCLES.STATUS` guard |
| PP-GRC-02 | Top-of-hierarchy employees (`MANAGER_EMP_ID IS NULL`) are silently excluded. There is no record that they were skipped and no mechanism to create reviews for them with a designated reviewer (e.g., board member or peer review). C-suite and other top-level roles have no review path. | High | BR-GRC-02: `MANAGER_EMP_ID IS NOT NULL` filter; no alternate reviewer assignment |
| PP-GRC-03 | Email notifications fire for every employee at generation time, regardless of whether the cycle is actually ready for employee action. If called against a `DRAFT` cycle (PP-GRC-01), employees receive "Performance Review Initiated" emails for a cycle that is not yet open. | Medium | BR-GRC-06 + BR-GRC-07: notifications unconditional; no cycle-status gate |
| PP-GRC-04 | The result count is only available via `DBMS_OUTPUT`, which is invisible to calling applications (web UIs, scheduled jobs, APIs). The caller has no programmatic way to know how many reviews were created vs. skipped, making operational monitoring impossible without session-level output capture. | Medium | BR-GRC-09: no OUT parameter or audit entry at bulk level |
| PP-GRC-05 | The single `COMMIT` at the end of the loop means a partial failure mid-loop (e.g., `PKG_NOTIFICATION` throwing an unhandled exception) would roll back all review inserts for the current transaction — losing all work done so far. Conversely, a notification failure after the COMMIT cannot be rolled back, leaving reviews without their corresponding notifications. | Medium | BR-GRC-08: single COMMIT with no savepoints or partial-failure handling |
| PP-GRC-06 | Manager assignment is frozen at generation time using `MANAGER_EMP_ID` from `EMPLOYEES`. If a manager changes between cycle opening and generation (or between generation and the review period), the reviewer on the `PERFORMANCE_REVIEWS` row is stale. There is no mechanism to refresh reviewer assignments for in-progress cycles. | Medium | BR-GRC-03: reviewer = `MANAGER_EMP_ID` at generation time only |

---

### Automation Opportunities (New — `generate_reviews_for_cycle`)

| ID | Opportunity | Problem Solved | Implementation Sketch | Effort / Impact |
|---|---|---|---|---|
| AO-GRC-01 | Add cycle-status validation guard at the top of the procedure | PP-GRC-01: prevents accidental generation against DRAFT or CLOSED cycles | `SELECT STATUS INTO v_status FROM REVIEW_CYCLES WHERE CYCLE_ID = p_cycle_id; IF v_status != 'OPEN' THEN RAISE_APPLICATION_ERROR(-20410, ...); END IF;` | Low effort; high risk mitigation |
| AO-GRC-02 | Add an `p_count OUT NUMBER` parameter and replace `DBMS_OUTPUT` with it | PP-GRC-04: enables programmatic monitoring of bulk generation results | Change `v_count` to an OUT parameter; remove `DBMS_OUTPUT.PUT_LINE`; add a `PKG_AUDIT.log_action` bulk-level entry for the generation event | Low effort; high operational value |
| AO-GRC-03 | Add a savepoint inside the loop and rollback per-employee on failure rather than aborting the whole batch | PP-GRC-05: partial failures currently abort all inserts for the current transaction | `SAVEPOINT sp_emp; ... EXCEPTION WHEN OTHERS THEN ROLLBACK TO sp_emp; log_error(...);` — continue to next employee | Medium effort; improves resilience |
| AO-GRC-04 | Separate notification dispatch from review creation; send notifications only after the cycle is confirmed open and reviews are committed | PP-GRC-03: premature notifications on DRAFT cycles | Add a distinct `notify_cycle_participants(p_cycle_id)` procedure called after `open_review_cycle`; suppress notification in `create_review` when called from bulk-generation context | Medium effort; eliminates premature notification risk |

---

### Validation Queue Items (New — `generate_reviews_for_cycle`)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-GRC-01 | Supplemental | Performance / Process | Confirm the intended call sequence: is `generate_reviews_for_cycle` supposed to be callable only after `open_review_cycle`? If yes, the cycle-status guard (AO-GRC-01) should be added and the current unguarded behaviour treated as a defect. | ❓ UNRESOLVED — lifecycle policy decision required |
| VQ-GRC-02 | Supplemental | Performance / Coverage | Confirm the intended review path for top-of-hierarchy employees (`MANAGER_EMP_ID IS NULL`). Do C-suite roles undergo peer review, board review, or no review? If they require a review, an alternate reviewer-assignment mechanism must be designed. | ❓ UNRESOLVED — no evidence of alternate reviewer pattern in analysed source |
| VQ-GRC-03 | Supplemental | Performance / Operations | Confirm whether a `UNIQUE` constraint exists on `(CYCLE_ID, EMP_ID)` in `PERFORMANCE_REVIEWS` — the idempotency of `generate_reviews_for_cycle` (BR-GRC-05) depends entirely on a `DUP_VAL_ON_INDEX` exception being raised on duplicate inserts. If the constraint does not exist, duplicate reviews will be silently created. | ❓ UNRESOLVED — constraint presence not confirmed in analysed source |
| VQ-GRC-04 | Supplemental | Performance / Operations | Confirm whether manager-reassignment mid-cycle is a known scenario. If yes, determine whether a `refresh_cycle_reviewers` operation (updating `REVIEWER_EMP_ID` on in-progress reviews when `EMPLOYEES.MANAGER_EMP_ID` changes) is required, or whether the assigned reviewer is considered frozen at generation time. | ❓ UNRESOLVED — no reviewer-refresh mechanism found in analysed source |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-PERF-01 to BR-PERF-07 (`get_rating_distribution`) | `generate_reviews_for_cycle` creates the `PERFORMANCE_REVIEWS` rows that `get_rating_distribution` later aggregates. Rows created for `MANAGER_EMP_ID IS NULL` employees that are excluded here (BR-GRC-02) will never appear in the distribution — a coverage gap compounding PP-PERF-01 (denominator only counts rated reviews) |
| PP-PERF-01 (silent exclusion of unrated reviews) | The employees excluded by BR-GRC-02 (no manager) also have no review row, making them invisible not just to the distribution function but to the entire review cycle — a deeper coverage gap than PP-PERF-01 alone |
| PP-TERM-02 / AO-TERM-03 (`calculate_final_pay` non-existent) | If termination triggers a mid-cycle review closure, `generate_reviews_for_cycle` may have already created a review for the to-be-terminated employee. The termination path does not cancel or close the orphaned review (no evidence found). |
| VQ-PERF-03 (rating band retroactive relabelling) | Rating labels are assigned inside `create_review` → `submit_manager_review`; `generate_reviews_for_cycle` is upstream — it creates blank reviews before any rating is assigned, so this VQ does not directly affect generation but is part of the same review lifecycle |
| AO-TERM-01 / BR-TERM-01 (`terminate_employee`) | Termination sets `EMPLOYMENT_STATUS` to something other than `'ACTIVE'`; any subsequent call to `generate_reviews_for_cycle` will correctly exclude the terminated employee (BR-GRC-01). However, reviews already created for an employee who is later terminated are not cleaned up. |

---

---

## Supplemental Extraction — EMERGENCY_CONTACTS (2026-08-04)

**Source:** `schema/tables/01_core_tables.sql` (recovered from file_cache.json)
**Entity:** `HRMS.EMERGENCY_CONTACTS`

---

### Table Definition

```sql
CREATE TABLE HRMS.EMERGENCY_CONTACTS (
    CONTACT_ID           NUMBER(10)      NOT NULL,
    EMP_ID               NUMBER(10)      NOT NULL,
    CONTACT_NAME         VARCHAR2(100)   NOT NULL,
    RELATIONSHIP         VARCHAR2(30),
    PHONE_PRIMARY        VARCHAR2(30)    NOT NULL,
    PHONE_SECONDARY      VARCHAR2(30),
    EMAIL                VARCHAR2(100),
    PRIORITY_ORDER       NUMBER(2)       DEFAULT 1,
    ACTIVE_FLAG          CHAR(1)         DEFAULT 'Y' NOT NULL,
    CREATED_BY           VARCHAR2(30)    NOT NULL,
    CREATED_DATE         DATE            DEFAULT SYSDATE NOT NULL,
    MODIFIED_BY          VARCHAR2(30),
    MODIFIED_DATE        DATE,
    CONSTRAINT PK_EMERGENCY_CONTACTS PRIMARY KEY (CONTACT_ID),
    CONSTRAINT FK_EC_EMP FOREIGN KEY (EMP_ID) REFERENCES HRMS.EMPLOYEES(EMP_ID)
);
```

**Columns:**

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| CONTACT_ID | NUMBER(10) | NOT NULL | — | PK; synthetic surrogate key |
| EMP_ID | NUMBER(10) | NOT NULL | — | FK → HRMS.EMPLOYEES(EMP_ID) |
| CONTACT_NAME | VARCHAR2(100) | NOT NULL | — | Full name of the emergency contact |
| RELATIONSHIP | VARCHAR2(30) | NULL | — | Free-text; no CHECK constraint |
| PHONE_PRIMARY | VARCHAR2(30) | NOT NULL | — | Must be provided; no format validation |
| PHONE_SECONDARY | VARCHAR2(30) | NULL | — | Optional second phone |
| EMAIL | VARCHAR2(100) | NULL | — | Optional; no format validation |
| PRIORITY_ORDER | NUMBER(2) | NULL | 1 | Sort key for multi-contact employees |
| ACTIVE_FLAG | CHAR(1) | NOT NULL | 'Y' | Soft-delete flag |
| CREATED_BY | VARCHAR2(30) | NOT NULL | — | Standard audit column |
| CREATED_DATE | DATE | NOT NULL | SYSDATE | Standard audit column |
| MODIFIED_BY | VARCHAR2(30) | NULL | — | Standard audit column |
| MODIFIED_DATE | DATE | NULL | — | Standard audit column |

**Constraints:**

| Constraint | Type | Definition |
|---|---|---|
| PK_EMERGENCY_CONTACTS | PRIMARY KEY | CONTACT_ID |
| FK_EC_EMP | FOREIGN KEY | EMP_ID → HRMS.EMPLOYEES(EMP_ID) |

**Notable absences:** No UNIQUE constraint on (EMP_ID, PRIORITY_ORDER). No CHECK constraint on RELATIONSHIP values. No CHECK constraint on ACTIVE_FLAG. No index on EMP_ID (Oracle does not auto-create indexes on FK columns).

---

### Business Rules (New — EMERGENCY_CONTACTS)

| ID | Rule | Source | Confidence | Notes |
|---|---|---|---|---|
| BR-EC-01 | Every emergency contact record must be associated with an existing employee. FK_EC_EMP enforces referential integrity to HRMS.EMPLOYEES(EMP_ID). Oracle's default ON DELETE NO ACTION applies — deleting an employee with existing emergency contacts raises ORA-02292. | Schema constraint | HIGH | Physical delete of a parent employee is blocked; inactivation via ACTIVE_FLAG is the only safe removal path. |
| BR-EC-02 | Every emergency contact must supply a primary phone number (PHONE_PRIMARY NOT NULL). A contact record cannot be saved without it. No format, country-code, or length validation is enforced beyond VARCHAR2(30). | Schema constraint | HIGH | A single space satisfies the constraint — data quality risk. |
| BR-EC-03 | CONTACT_NAME is mandatory (NOT NULL). A contact cannot exist without a name. No uniqueness constraint exists — duplicate names are permitted for the same employee. | Schema constraint | HIGH | — |
| BR-EC-04 | RELATIONSHIP is nullable and unconstrained (VARCHAR2(30), no CHECK). Any string or NULL is acceptable. This diverges from EMPLOYEE_DEPENDENTS.RELATIONSHIP, which enforces ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER'). Two tables covering overlapping relationship semantics apply different data quality standards. | Schema column; contrast with EMPLOYEE_DEPENDENTS | HIGH | Inconsistency creates risk for any future reporting or notification logic branching on relationship type. |
| BR-EC-05 | PRIORITY_ORDER defaults to 1 for every new row. No UNIQUE constraint on (EMP_ID, PRIORITY_ORDER) exists, so multiple contacts for the same employee can share the same priority number. The system has no guaranteed mechanism to identify a single "highest-priority" contact without additional application logic. | Schema column; absence of UNIQUE constraint | HIGH | A `WHERE PRIORITY_ORDER = 1` query may return multiple rows for the same employee with no tiebreaker. |
| BR-EC-06 | ACTIVE_FLAG defaults to 'Y'. Logical deletes are the intended pattern — contacts should be inactivated rather than physically deleted, consistent with EMPLOYEES and EMPLOYEE_DEPENDENTS. However, no CHECK constraint enforces 'Y'/'N'. EMERGENCY_CONTACTS is the only entity in the schema with ACTIVE_FLAG but without a corresponding CHK_ constraint (all other ACTIVE_FLAG columns — DEPARTMENTS, LOCATIONS, JOB_GRADES, EMPLOYEES — carry one). | Schema column; cross-table comparison | MEDIUM | Invalid values ('X', '1', NULL) are database-legal and will silently break `WHERE ACTIVE_FLAG = 'Y'` filters. |
| BR-EC-07 | An employee may have multiple emergency contacts (no UNIQUE constraint on EMP_ID alone). The intended retrieval order is PRIORITY_ORDER ascending. No cap on contacts per employee exists in the schema. | Schema structure | HIGH | — |
| BR-EC-08 | PHONE_SECONDARY and EMAIL are both optional. A contact record with only PHONE_PRIMARY is valid. No rule requires at least two contact methods. | Schema column definitions (nullable) | HIGH | — |
| BR-EC-09 | Standard audit trail is present: CREATED_BY, CREATED_DATE (default SYSDATE), MODIFIED_BY, MODIFIED_DATE. No history table equivalent to EMPLOYEE_HISTORY exists for EMERGENCY_CONTACTS. Any overwrite of CONTACT_NAME, PHONE_PRIMARY, or RELATIONSHIP permanently loses the prior value. | Schema column definitions; absence of history table | HIGH | Point-in-time reconstruction of contact information (e.g., at the time of an incident) is impossible. |
| BR-EC-10 | CONTACT_ID is a NUMBER(10) surrogate PK. No sequence or trigger DDL is present in the source file. The mechanism for generating CONTACT_ID values (application sequence, trigger, or manual assignment) is not evidenced. | Schema definition; absence of sequence/trigger DDL | MEDIUM | If multiple application layers insert rows without a shared sequence, PK collisions are possible. |

---

### Code Reference Gap Map

| Procedure / Package | Expected Interaction | Evidence Found |
|---|---|---|
| `hire_employee` | Insert initial emergency contact(s) on hire | No reference found in analysed source |
| `terminate_employee` | Inactivate contacts on termination | No reference — `terminate_employee` does not touch EMERGENCY_CONTACTS |
| Self-service / Forms module | Employee-facing CRUD for own contacts | Not evidenced in analysed PL/SQL source |
| Emergency notification dispatch | Read contacts ordered by PRIORITY_ORDER | No procedure references this table |
| Reporting | Include contact on HR record or pay stub | Not evidenced |

**Finding:** EMERGENCY_CONTACTS is a data-capture table with no procedural consumers in the analysed codebase. The table is populated (presumably via forms or direct INSERT) but never read by any PL/SQL package or procedure. This is the same pattern as EMPLOYEE_BANK_ACCOUNTS (see PP-BA-07).

---

### Process Gap Map — Emergency Notification Pathway

```
Employee record created
        │
        ▼
EMERGENCY_CONTACTS row inserted
(via HR data-entry form — assumed, not evidenced)
        │
        ▼
Emergency event occurs
        │
        ▼
HR staff need to reach next-of-kin
        │
        ▼
[GAP] No procedure reads EMERGENCY_CONTACTS
        │
        ▼
Manual lookup required (HR queries the table directly
or uses a report — neither evidenced in source)
        │
        ▼
Contact reached externally
```

The full notification pathway is absent from the application layer. The table is a passive data store; no workflow, trigger, notification, or automated escalation reads from it.

---

### Pain Points (New — EMERGENCY_CONTACTS)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-EC-01 | No procedure or package reads EMERGENCY_CONTACTS. In an actual emergency, HR staff must query the table directly via SQL or a separate report. There is no integrated notification workflow, escalation path, or "retrieve primary contact" API. | Emergency response depends on ad-hoc database access; contact data may not be available to non-technical HR staff in a timely manner. | High |
| PP-EC-02 | PRIORITY_ORDER is not unique per employee — multiple contacts can share PRIORITY_ORDER = 1 with no defined tiebreaker. Any query using `WHERE PRIORITY_ORDER = 1` may return multiple rows, producing indeterminate behaviour (first-row-wins, error, or duplicated notifications). | Ambiguous primary contact identification; potential for missed or duplicate emergency notifications. | High |
| PP-EC-03 | RELATIONSHIP is free-text with no CHECK constraint. Data entered by different operators will use inconsistent values ('Spouse', 'SPOUSE', 'Wife', 'spouse'). Any future notification or reporting logic branching on relationship type cannot rely on this column without prior data cleansing. | Data quality degrades over time; relationship-based filtering is unreliable. | Medium |
| PP-EC-04 | No history table for EMERGENCY_CONTACTS. An update to PHONE_PRIMARY or CONTACT_NAME permanently overwrites the prior value. Point-in-time reconstruction (e.g., what contact was on record at the time of an incident) is impossible. | Irreversible data loss on update; no audit trail for contact information changes. | Medium |
| PP-EC-05 | ACTIVE_FLAG has no CHECK constraint. Invalid values ('X', '1', 'y', NULL) are database-legal and will silently break `WHERE ACTIVE_FLAG = 'Y'` active-record filters. EMERGENCY_CONTACTS is the only entity in the schema with ACTIVE_FLAG but without this guard. | Risk of corrupt flag values causing active contacts to be excluded silently. | Low |

---

### Automation Opportunities (New — EMERGENCY_CONTACTS)

| ID | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-EC-01 | Add a `get_primary_emergency_contact` function to retrieve the highest-priority active contact for an employee | No read path exists; HR must query directly | Create `PKG_HR.get_primary_emergency_contact(p_emp_id IN NUMBER) RETURN SYS_REFCURSOR` — `SELECT ... WHERE EMP_ID = p_emp_id AND ACTIVE_FLAG = 'Y' ORDER BY PRIORITY_ORDER ASC FETCH FIRST 1 ROW ONLY`; expose in self-service and HR portal | High — provides a deterministic read API; prerequisite for any notification integration |
| AO-EC-02 | Enforce UNIQUE (EMP_ID, PRIORITY_ORDER) at schema level | Multiple contacts can share the same priority with no error | Add `CONSTRAINT UK_EC_EMP_PRIORITY UNIQUE (EMP_ID, PRIORITY_ORDER)` after resolving any existing duplicate values via a one-time data fix | Medium — eliminates ambiguous primary contact retrieval (PP-EC-02) |
| AO-EC-03 | Add `CHECK (ACTIVE_FLAG IN ('Y','N'))` consistent with all other ACTIVE_FLAG columns in the schema | No constraint; any character is valid | `ALTER TABLE HRMS.EMERGENCY_CONTACTS ADD CONSTRAINT CHK_EC_ACTIVE CHECK (ACTIVE_FLAG IN ('Y', 'N'))` after a data audit confirms no invalid values exist | Low — one-line DDL fix; eliminates PP-EC-05 |
| AO-EC-04 | Inactivate emergency contacts as part of `terminate_employee` | `terminate_employee` does not touch EMERGENCY_CONTACTS; contacts remain ACTIVE_FLAG = 'Y' after termination indefinitely | Add `UPDATE HRMS.EMERGENCY_CONTACTS SET ACTIVE_FLAG = 'N', MODIFIED_BY = p_user, MODIFIED_DATE = SYSDATE WHERE EMP_ID = p_emp_id` as a step in `terminate_employee` | Medium — prevents terminated-employee contacts from appearing in active queries; consistent with soft-delete pattern |

---

### Validation Queue Items (New — EMERGENCY_CONTACTS)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-EC-01 | Supplemental | Employee Management / Emergency Response | Confirm whether any PL/SQL package, Forms module, or reporting layer reads EMERGENCY_CONTACTS outside the analysed source. If not, confirm whether this is a known gap or in-scope for the modernisation project. | ❓ UNRESOLVED — no references found in analysed source |
| VQ-EC-02 | Supplemental | Employee Management / Data Quality | Confirm the intended controlled vocabulary for EMERGENCY_CONTACTS.RELATIONSHIP. Should it match EMPLOYEE_DEPENDENTS ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER') or use a broader/different set? A CHECK constraint or FK to a reference table should be added once agreed. | ❓ UNRESOLVED — business policy decision required |
| VQ-EC-03 | Supplemental | Employee Management / Audit | Confirm whether point-in-time audit of emergency contact changes is required (e.g., for HR compliance or incident investigations). If yes, an EMERGENCY_CONTACTS_HISTORY table or audit trigger should be introduced, consistent with EMPLOYEE_HISTORY. | ❓ UNRESOLVED — compliance/audit policy decision required |
| VQ-EC-04 | Supplemental | Employee Management / Lifecycle | Confirm the intended behaviour for emergency contacts when an employee is terminated. Current: contacts remain ACTIVE_FLAG = 'Y' indefinitely. Proposed: inactivate as part of `terminate_employee` (AO-EC-04). Confirm before implementing. | ❓ UNRESOLVED — business process decision required |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-TERM-01 through BR-TERM-09 | `terminate_employee` has no step for EMERGENCY_CONTACTS — AO-EC-04 and VQ-EC-04 extend the termination gap map with a fourth uncovered step alongside COBRA, access revocation, and final pay |
| PP-BA-07 (EMPLOYEE_BANK_ACCOUNTS never read) | EMERGENCY_CONTACTS exhibits the identical "data captured, never consumed" pattern — both tables are orphaned from the procedural layer |
| EMPLOYEE_DEPENDENTS.RELATIONSHIP CHECK constraint | EMERGENCY_CONTACTS.RELATIONSHIP has no equivalent CHECK — BR-EC-04 documents the inconsistency; VQ-EC-02 requests resolution |
| CHK_DEPT_ACTIVE and all other ACTIVE_FLAG CHECK constraints in the schema | EMERGENCY_CONTACTS is the sole entity whose ACTIVE_FLAG has no CHECK constraint — BR-EC-06 and AO-EC-03 address this |
| VQ-TERM-01 (COBRA), VQ-TERM-02 (access revocation), VQ-TERM-05 (off-cycle payroll) | Termination gap list now gains VQ-EC-04 (emergency contact inactivation) as an additional uncovered termination step |

---

---

## Supplemental Extraction — `PKG_INTEGRATION.get_integration_status`

**Source files:** `plsql/packages/PKG_INTEGRATION.pkb`, `plsql/packages/PKG_INTEGRATION.pks`
**Package:** `HRMS.PKG_INTEGRATION`
**Object type:** Public function

---

### Function Signature

```sql
FUNCTION get_integration_status(
    p_integration_name IN VARCHAR2
) RETURN VARCHAR2;
```

Declared `PUBLIC` in the package spec (`PKG_INTEGRATION.pks`) — callable by any schema object or client with `EXECUTE` on `PKG_INTEGRATION`.

---

### Full Body

```sql
FUNCTION get_integration_status(
    p_integration_name IN VARCHAR2
) RETURN VARCHAR2 IS
BEGIN
    RETURN PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS');
END get_integration_status;
```

Three lines of executable code. No local variables, no exception handler, no logging.

---

### Execution Flow

```
Caller passes p_integration_name (e.g. 'GL_FEED')
        │
        ▼
PKG_COMMON.get_param('INTEGRATION', p_integration_name || '_STATUS')
        │
        ▼
SYSTEM_PARAMETERS table lookup
  WHERE PARAM_GROUP = 'INTEGRATION'
    AND PARAM_NAME  = <p_integration_name> || '_STATUS'
        │
        ▼
Returns VARCHAR2 status value (or NULL if row absent)
```

The function is a thin wrapper — all persistence and lookup logic resides in `PKG_COMMON.get_param`.

---

### Tables Accessed (Indirect — via PKG_COMMON.get_param)

| Table | Access | Via |
|---|---|---|
| `SYSTEM_PARAMETERS` | SELECT | `PKG_COMMON.get_param('INTEGRATION', ...)` |

No direct DML. No direct table reference in the function body.

---

### Parameters

| Parameter | Direction | Type | Notes |
|---|---|---|---|
| `p_integration_name` | IN | VARCHAR2 | Name of the integration endpoint (e.g. `'GL_FEED'`, `'BENEFITS'`, `'TIME_ATTENDANCE'`). No length constraint in spec. |
| *(return value)* | — | VARCHAR2 | Status string stored in `SYSTEM_PARAMETERS`; NULL if no matching row exists. |

---

### SYSTEM_PARAMETERS Key Convention

The function constructs the parameter name as:

```
PARAM_GROUP = 'INTEGRATION'
PARAM_NAME  = <p_integration_name> || '_STATUS'
```

For the three integrations declared in the package:

| Integration | Expected PARAM_NAME in SYSTEM_PARAMETERS |
|---|---|
| GL journal feed (`generate_gl_journal`) | `GL_FEED_STATUS` |
| Benefits feed export (`export_benefits_feed`) | `BENEFITS_STATUS` |
| Time & attendance import (`import_time_attendance`) | `TIME_ATTENDANCE_STATUS` |
| Org structure sync (`sync_org_structure`) | `ORG_SYNC_STATUS` |

These are inferred from the Oracle directory constants and procedure names in the package body. No procedure in `PKG_INTEGRATION` calls `get_integration_status` — none of the four sibling procedures update their own `_STATUS` parameter.

---

### Business Rules (New — PKG_INTEGRATION.get_integration_status)

| ID | Rule | Source | Confidence |
|---|---|---|---|
| BR-GIS-01 | The status of any named integration endpoint is stored as a VARCHAR2 parameter in the `SYSTEM_PARAMETERS` table under `PARAM_GROUP = 'INTEGRATION'` and `PARAM_NAME = <integration_name> || '_STATUS'`. There is no dedicated integration-status table or typed status column. | `.pkb` body | High |
| BR-GIS-02 | `get_integration_status` performs a read-only lookup; it never writes, updates, or deletes any row. The function has no side effects. | `.pkb` body | High |
| BR-GIS-03 | If `SYSTEM_PARAMETERS` contains no row matching the constructed key, `PKG_COMMON.get_param` returns NULL (standard Oracle NVL-absent behaviour inferred from the single-expression return). The caller receives NULL with no error or warning. | `.pkb` body + `PKG_COMMON` pattern | High |
| BR-GIS-04 | No procedure inside `PKG_INTEGRATION` ever calls `get_integration_status`. The four operational procedures (`generate_gl_journal`, `export_benefits_feed`, `import_time_attendance`, `sync_org_structure`) do not read integration status before executing, and do not update it after completing. Status checking is fully decoupled from execution. | `.pkb` full body | High |
| BR-GIS-05 | No procedure inside `PKG_INTEGRATION` calls `PKG_COMMON.set_param` or any equivalent to write a `_STATUS` value. The status values in `SYSTEM_PARAMETERS` cannot be populated or updated by the integration package itself. They must be maintained by an external mechanism (manual SQL, a separate admin package, or the batch scheduler). | `.pkb` full body | High |
| BR-GIS-06 | The function has no exception handler. Any exception raised by `PKG_COMMON.get_param` (e.g., `NO_DATA_FOUND` if the inner implementation raises rather than returns NULL, or any unexpected error) propagates unhandled to the caller. | `.pkb` body | High |
| BR-GIS-07 | `p_integration_name` is unbounded VARCHAR2 with no length validation. Passing a name that causes `p_integration_name || '_STATUS'` to exceed the `PARAM_NAME` column width in `SYSTEM_PARAMETERS` will raise `ORA-01401` (inserted value too large) or a silent truncation depending on column definition and NLS settings. | `.pkb` + `.pks` | Medium |
| BR-GIS-08 | The package spec notes that FTP credentials are stored in the `SYSTEM_PARAMETERS` table in cleartext. `get_integration_status` uses the same table and same `PKG_COMMON.get_param` access path. The function's parameter naming convention (`_STATUS` suffix) co-exists with credential rows in the same table, separated only by `PARAM_NAME` convention — there is no physical separation of secrets from status values. | `.pks` known issues note | High |

---

### Process Flow: Integration Status Check

```
[Scheduler / Admin / Caller]
        │
        ▼
get_integration_status('GL_FEED')
        │
        ▼
PKG_COMMON.get_param('INTEGRATION', 'GL_FEED_STATUS')
        │
        ├── Row found ──► Return status value (e.g. 'ACTIVE', 'DISABLED', 'ERROR', ...)
        │
        └── No row ─────► Return NULL  (no error, no log entry)
```

The status vocabulary (what values `_STATUS` can hold) is not defined anywhere in the analysed source. There is no CHECK constraint, no enumeration type, and no consuming code that branches on the returned value.

---

### Pain Points (New — PKG_INTEGRATION.get_integration_status)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-GIS-01 | No procedure in `PKG_INTEGRATION` reads or writes integration status. `generate_gl_journal`, `export_benefits_feed`, `import_time_attendance`, and `sync_org_structure` all execute unconditionally regardless of any status flag. The function exists but is never used by the package it belongs to — integrations run whether enabled, disabled, or in an error state. | Operators cannot disable a broken integration via a status flag; a "DISABLED" status has no enforcement mechanism. | High |
| PP-GIS-02 | No procedure in `PKG_INTEGRATION` updates `_STATUS` after execution. Whether a GL journal run succeeded or failed, the status in `SYSTEM_PARAMETERS` is unchanged. The only status information is in `PKG_COMMON.log_info` / `PKG_COMMON.log_error` audit log entries, not in a queryable status column. | `get_integration_status` always returns a static, manually-maintained value — it reflects what an administrator last set, not the actual last-run outcome. | High |
| PP-GIS-03 | No exception handler in `get_integration_status`. If `PKG_COMMON.get_param` raises (rather than returning NULL on no-row), the exception propagates to the scheduler or calling client with no logging, no context, and no graceful degradation. | Silent failure at query time; calling client may crash or log a cryptic error rather than "integration status unavailable". | Medium |
| PP-GIS-04 | Status vocabulary is undefined. No code, comment, or constraint documents what values `_STATUS` can hold. Different administrators may write `'ACTIVE'`, `'ENABLED'`, `'OK'`, `'Y'`, or any other string. Any future consumer branching on the value cannot do so reliably. | Inconsistent status semantics across environments and over time; any status-driven control flow will require data cleansing first. | Medium |
| PP-GIS-05 | FTP credentials and integration status values co-exist in `SYSTEM_PARAMETERS` under the `INTEGRATION` group, separated only by `PARAM_NAME` naming convention. There is no role-based or structural separation between secrets and operational metadata. A query on `PARAM_GROUP = 'INTEGRATION'` returns both status values and cleartext credentials in the same result set. | Secrets exposure risk whenever integration status is queried; violates principle of least privilege if status queries are granted to non-admin roles. | High |

---

### Automation Opportunities (New — PKG_INTEGRATION.get_integration_status)

| ID | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-GIS-01 | Add a pre-execution status guard to each integration procedure | All four procedures run unconditionally | At the start of each procedure, call `get_integration_status(p_integration_name)` and raise an application error (or log and return) if status = `'DISABLED'` or `'ERROR'`; standardise the status vocabulary with a CHECK constraint or reference table | High — makes the existing status mechanism functional; enables operator-controlled integration toggling |
| AO-GIS-02 | Add a post-execution status update to each integration procedure | No procedure updates `_STATUS` after running | After success: `PKG_COMMON.set_param('INTEGRATION', <name> || '_STATUS', 'OK')`. After exception: set to `'ERROR'` with timestamp. This turns `get_integration_status` from a static label into a live health indicator | High — `get_integration_status` becomes a real-time integration health check rather than a manual flag |
| AO-GIS-03 | Add an exception handler to `get_integration_status` with safe-default return | Unhandled exceptions propagate to caller | Wrap the `RETURN` in a `BEGIN...EXCEPTION WHEN OTHERS THEN RETURN 'UNKNOWN'; END` block; optionally log via `PKG_COMMON.log_error` | Low — defensive coding; prevents scheduler crashes on missing parameter rows |
| AO-GIS-04 | Separate FTP/integration credentials from status parameters in `SYSTEM_PARAMETERS` | Credentials and status co-exist in `PARAM_GROUP = 'INTEGRATION'`; cleartext storage noted in spec | Introduce a `PARAM_GROUP = 'INTEGRATION_CREDS'` group and encrypt values using the existing `PKG_SECURITY` infrastructure (or migrate to Oracle Wallet / a secrets manager); separate `get_integration_status` queries to status-only rows | High — eliminates cleartext credential exposure (documented in package spec known issues); reduces blast radius of status queries |

---

### Validation Queue Items (New — PKG_INTEGRATION.get_integration_status)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-GIS-01 | Supplemental | Integration / Operational Control | Confirm whether any external caller (scheduler, Forms module, reporting layer, admin UI) calls `get_integration_status` outside the analysed PL/SQL source. If a caller exists, identify what status vocabulary it expects and whether it enforces pre-execution guards. | ❓ UNRESOLVED — no callers found in analysed source |
| VQ-GIS-02 | Supplemental | Integration / Status Vocabulary | Confirm the intended controlled vocabulary for `_STATUS` values (e.g., `'ACTIVE'`, `'DISABLED'`, `'ERROR'`, `'RUNNING'`). A CHECK constraint or reference lookup should be introduced once agreed; without it, `get_integration_status` cannot be used for reliable branching logic. | ❓ UNRESOLVED — business/operational decision required |
| VQ-GIS-03 | Supplemental | Integration / `SYSTEM_PARAMETERS` Security | Confirm whether FTP/integration credentials stored in `SYSTEM_PARAMETERS` under `PARAM_GROUP = 'INTEGRATION'` are encrypted at rest or accessible to roles beyond DBA. If cleartext storage is confirmed, this is a security remediation item for the modernisation scope. | ❓ UNRESOLVED — security audit required; flagged in package spec known issues |
| VQ-GIS-04 | Supplemental | Integration / Status Write Path | Confirm the intended mechanism for setting `_STATUS` values: manual SQL by an administrator, a separate admin package, the batch scheduler, or the integration procedures themselves. Until the write path is defined, AO-GIS-02 (post-execution status update) cannot be implemented. | ❓ UNRESOLVED — operational process decision required |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-ORG-01 through BR-ORG-05 (`sync_org_structure` stub) | `sync_org_structure` is one of the four procedures that BR-GIS-04 shows never calls `get_integration_status` — it runs unconditionally despite being a complete no-op stub; PP-GIS-01 now covers all four procedures |
| VQ-20 (`SYSTEM_PARAMETERS` credential storage) | VQ-GIS-03 extends VQ-20 with the specific co-location concern: status values and cleartext FTP credentials share the same `PARAM_GROUP = 'INTEGRATION'` namespace |
| PP-BA-07, PP-EC-01 ("data captured, never consumed") | `get_integration_status` is the inverse pattern: a *read function* that is never called. The status data it would return is also never written by the package. Both ends of the status update loop are broken. |
| AO-ORG-02 (implement `sync_org_structure`) | Any real implementation of `sync_org_structure` should incorporate the pre/post-execution status guards described in AO-GIS-01 and AO-GIS-02 as part of the same implementation task |

---

## Supplemental Extraction — `PKG_PAYROLL.get_ytd_earnings`

**Source files:** `plsql/packages/PKG_PAYROLL.pkb`, `plsql/packages/PKG_PAYROLL.pks`
**Extraction date:** 2026-08-04

---

### Overview

`get_ytd_earnings` is a public function in `HRMS.PKG_PAYROLL` that returns the total year-to-date gross earnings for a single employee within a given tax year. It is a critical prerequisite for payroll tax calculations: it is called inside `calculate_employee_pay` to supply the `p_ytd_gross` argument to both `calculate_fica` (Social Security cap check) and `calculate_medicare` (Additional Medicare threshold check). The function is also exposed in the package specification for direct use by reporting layers or external callers.

---

### Signature

```sql
FUNCTION get_ytd_earnings(
    p_emp_id    IN NUMBER,
    p_tax_year  IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)
) RETURN NUMBER
```

**Parameters:**

| Parameter | Type | Direction | Default | Description |
|---|---|---|---|---|
| `p_emp_id` | NUMBER | IN | required | Employee identifier — foreign key to `EMPLOYEES.EMP_ID` |
| `p_tax_year` | NUMBER | IN | `EXTRACT(YEAR FROM SYSDATE)` | Four-digit tax year to accumulate against; defaults to the current calendar year |

**Returns:** `NUMBER` — sum of all `EARNING`-type `PAYROLL_DETAILS.AMOUNT` rows that match the employee and tax year; `0` if no qualifying rows exist (via `NVL`).

---

### Full SQL Body

```sql
SELECT NVL(SUM(pd.AMOUNT), 0)
INTO v_ytd
FROM PAYROLL_DETAILS pd
JOIN PAYROLL_RUNS pr ON pd.RUN_ID = pr.RUN_ID
JOIN PAY_PERIODS pp ON pr.PERIOD_ID = pp.PERIOD_ID
WHERE pd.EMP_ID = p_emp_id
AND pd.ELEMENT_TYPE = 'EARNING'
AND pd.STATUS = 'CALCULATED'
AND EXTRACT(YEAR FROM pp.PERIOD_START_DATE) = p_tax_year;
```

---

### Tables Accessed

| Table | Join / Filter | Columns Used | Access Type |
|---|---|---|---|
| `PAYROLL_DETAILS` | Base table | `EMP_ID`, `RUN_ID`, `ELEMENT_TYPE`, `AMOUNT`, `STATUS` | SELECT |
| `PAYROLL_RUNS` | JOIN on `pd.RUN_ID = pr.RUN_ID` | `RUN_ID`, `PERIOD_ID` | SELECT (navigation only) |
| `PAY_PERIODS` | JOIN on `pr.PERIOD_ID = pp.PERIOD_ID` | `PERIOD_ID`, `PERIOD_START_DATE` | SELECT (date filter) |

No DML. No sequences. No calls to other packages.

---

### Execution Flow

```
get_ytd_earnings(p_emp_id, p_tax_year)
        │
        ▼
Aggregate PAYROLL_DETAILS
   WHERE EMP_ID = p_emp_id
     AND ELEMENT_TYPE = 'EARNING'
     AND STATUS = 'CALCULATED'
     AND YEAR(PAY_PERIOD.PERIOD_START_DATE) = p_tax_year
        │
        ├── Rows found ──► RETURN NVL(SUM(AMOUNT), 0)
        │
        └── No rows ─────► RETURN 0   (NVL handles this — no EXCEPTION block needed)
```

No exception handler is declared. If a JOIN produces an unexpected error (e.g., referential integrity violation), the exception propagates unhandled to `calculate_employee_pay`, where it is caught by the outer `WHEN OTHERS` block and logged via `PKG_COMMON.log_error`.

---

### Call Graph

**Callers (within PKG_PAYROLL.pkb):**

`calculate_employee_pay` calls `get_ytd_earnings` once per employee per pay run, immediately after inserting the gross `EARNING` record for the current period:

```sql
-- Get YTD gross for tax calculations
v_ytd_gross := get_ytd_earnings(p_emp_id, EXTRACT(YEAR FROM v_period_end));
```

The result is passed directly as `p_ytd_gross` to:
1. `calculate_fica(v_period_gross, v_ytd_gross)` — determines whether the employee has reached the Social Security wage base ($168,600 for 2024) and how much of this period's gross is still taxable.
2. `calculate_medicare(v_period_gross, v_ytd_gross)` — determines whether the Additional Medicare Tax threshold ($200,000) has been crossed and, if so, calculates the blended 0.9% surcharge.

**External callers (package spec):** `get_ytd_earnings` is declared PUBLIC. It may be called by the `HRMS_PAYROLL` Oracle Forms module or the batch scheduler to populate YTD totals on payslips or reports. The `get_payslip` procedure does NOT call it — it substitutes hardcoded `0 AS YTD_GROSS` and `0 AS YTD_NET` placeholders instead (see BR-YTD-07 below).

---

### Business Rules (BR-YTD-01 through BR-YTD-11)

| ID | Rule | Source | Confidence |
|---|---|---|---|
| BR-YTD-01 | YTD gross is the sum of all `PAYROLL_DETAILS` rows with `ELEMENT_TYPE = 'EARNING'` and `STATUS = 'CALCULATED'` for a given employee and tax year. Rows in `ERROR`, `REVERSED`, or any other status are excluded. | `get_ytd_earnings` WHERE clause | HIGH |
| BR-YTD-02 | The tax year boundary is determined by `EXTRACT(YEAR FROM pp.PERIOD_START_DATE)`. A pay period that starts on 31 December and ends on 6 January is counted as a prior-year period. Pay periods that start in the new year are counted as the new year, regardless of when they were paid. | `get_ytd_earnings` filter | HIGH |
| BR-YTD-03 | YTD earnings include only the employee share of gross pay (`ELEMENT_TYPE = 'EARNING'`). Deductions, taxes (`TAX`), and benefits (`BENEFIT`) are excluded from the YTD accumulation used for FICA and Medicare purposes. | `get_ytd_earnings` filter + `calculate_fica` / `calculate_medicare` usage | HIGH |
| BR-YTD-04 | The function returns `0` (not `NULL`) when no qualifying earnings records exist, ensuring FICA and Medicare calculations never receive a NULL YTD input. | `NVL(SUM(...), 0)` | HIGH |
| BR-YTD-05 | The Social Security wage base cap is enforced by comparing `p_ytd_gross` (from `get_ytd_earnings`) against the constant `c_ss_wage_base_2024 = 168600`. If `p_ytd_gross >= 168600`, no FICA tax is calculated for the period. If `p_ytd_gross < 168600`, only the portion of current gross up to the remaining cap is taxed at 6.2%. | `calculate_fica` using `get_ytd_earnings` result | HIGH |
| BR-YTD-06 | The Additional Medicare Tax (0.9%) applies when combined YTD gross plus current period gross exceeds `c_medicare_addl_threshold = 200000`. The function calculates the exact taxable amount at the threshold boundary: if only part of this period's pay crosses $200,000, only that part bears the surcharge. | `calculate_medicare` using `get_ytd_earnings` result | HIGH |
| BR-YTD-07 | `get_payslip` does NOT call `get_ytd_earnings`. YTD columns in the payslip cursor (`YTD_GROSS`, `YTD_NET`) are hardcoded to `0`. This is an explicitly documented placeholder — payslips always show $0.00 for year-to-date totals regardless of actual earnings history. | `get_payslip` SELECT clause: `0 AS YTD_GROSS`, `0 AS YTD_NET` | HIGH — confirmed defect |
| BR-YTD-08 | The current period's gross pay (`v_period_gross` just inserted into `PAYROLL_DETAILS`) is included in the YTD sum returned by `get_ytd_earnings`. The INSERT for the gross `EARNING` record occurs before `get_ytd_earnings` is called within `calculate_employee_pay`. This means the YTD figure passed to `calculate_fica` and `calculate_medicare` already includes the current period's earnings. | `calculate_employee_pay` code order: INSERT gross → call `get_ytd_earnings` | HIGH — ordering is critical to FICA cap logic |
| BR-YTD-09 | YTD accumulation is scoped to the tax year defined by `PERIOD_START_DATE`, not `PAY_DATE` or `PERIOD_END_DATE`. For most configurations these will be the same calendar year, but for biweekly periods that straddle a year boundary, `PERIOD_START_DATE` is the tiebreaker. | `get_ytd_earnings` filter: `EXTRACT(YEAR FROM pp.PERIOD_START_DATE)` | HIGH |
| BR-YTD-10 | The package specification documents a known edge case: "YTD accumulation resets incorrectly for mid-year hires in some edge cases." The specific trigger is not documented in code. Given the query logic, the most likely scenario is that a mid-year hire's first pay period has a `PERIOD_START_DATE` falling in the prior year (e.g., a biweekly period that started before the hire date) or the function is called for a tax year before any `SALARY_RECORDS` row exists, causing `get_salary_as_of` to return 0 before `get_ytd_earnings` is ever reached. | PKG_PAYROLL.pks known issues comment | MEDIUM — defect acknowledged, root cause inferred |
| BR-YTD-11 | `REVERSED` payroll runs remain in `PAYROLL_DETAILS` with `STATUS = 'REVERSED'`. Because `get_ytd_earnings` filters to `STATUS = 'CALCULATED'` only, reversed earnings are correctly excluded from YTD. A payroll reversal therefore reduces the effective YTD gross on the next run. | `get_ytd_earnings` STATUS filter | HIGH |

---

### Process Context: YTD Earnings Within the Payroll Calculation Flow

```
calculate_payroll(p_run_id)
        │
        └── FOR each ACTIVE employee ──►  calculate_employee_pay(run, emp, period)
                                                    │
                                            1. Get annual salary
                                               (get_salary_as_of)
                                            2. Divide by periods/year → v_period_gross
                                            3. INSERT gross EARNING row
                                               into PAYROLL_DETAILS  ◄── current period included
                                            4. Call get_ytd_earnings  ◄── returns YTD incl. step 3
                                            5. Call calculate_fica(period_gross, ytd)
                                            6. Call calculate_medicare(period_gross, ytd)
                                            7. Apply deductions / benefits
```

The INSERT at step 3 happens in the same database session and (since no COMMIT has occurred) in the same transaction as step 4. Therefore `get_ytd_earnings` sees the current period's gross pay in its SUM. This is the intended design for capping FICA at the wage base mid-period, but creates a subtle contract: `get_ytd_earnings` is **not** a "prior YTD" function; it is a "YTD through and including this period" function.

---

### Known Issues and Defects

| Issue | Location | Severity | Details |
|---|---|---|---|
| YTD placeholders in payslip | `get_payslip` | High | `YTD_GROSS = 0` and `YTD_NET = 0` are hardcoded. Employees receive payslips showing $0 year-to-date figures. `get_ytd_earnings` is never called by `get_payslip`. |
| Mid-year hire YTD reset | `PKG_PAYROLL.pks` known issues | Medium | YTD accumulation "resets incorrectly for mid-year hires in some edge cases" — acknowledged in spec but not fixed. |
| REVERSED rows excluded but no tombstone | `get_ytd_earnings` | Low | A reversal drops the reversed period from YTD silently. There is no separate reversed-YTD or correction flag to distinguish "never paid" from "paid then reversed." |
| No index guidance | `PAYROLL_DETAILS` | Medium | The function performs a full three-table aggregation on `PAYROLL_DETAILS` for every employee on every pay run. With no index documented on `(EMP_ID, ELEMENT_TYPE, STATUS)` or an index on `PAY_PERIODS(PERIOD_START_DATE)`, this scales as O(n × m) where n = employees and m = total detail rows per year. The parent procedure `calculate_payroll` calls this inside a cursor loop (row-by-row); performance degrades with employee count and pay run history depth. |

---

### Pain Points (New — `PKG_PAYROLL.get_ytd_earnings`)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-YTD-01 | `get_payslip` hardcodes `0 AS YTD_GROSS` and `0 AS YTD_NET` instead of calling `get_ytd_earnings`. Every payslip produced by the system shows $0.00 for both YTD fields regardless of actual earnings history. Employees, managers, and payroll staff have no accurate YTD view from a standard payslip. | Compliance and employee trust impact; YTD figures are required on W-2 preparation and are expected on standard pay advices; any auditor examining payslip output will flag this immediately. | High |
| PP-YTD-02 | `get_ytd_earnings` is called inside a cursor-loop (`calculate_employee_pay` is itself called row-by-row from `calculate_payroll`). For a company of 1,000 employees, the function runs 1,000 separate three-table aggregations against `PAYROLL_DETAILS` per pay run. As historical rows accumulate over the year, each call scans more rows. This is the dominant performance bottleneck in the payroll calculation path. | Payroll runs slow down progressively through the year; December runs may time out for large employee populations. | High |
| PP-YTD-03 | The function includes the current period's gross in the YTD total (because the INSERT happens before the call within the same transaction). This is correct for FICA wage base enforcement, but the semantics are non-obvious and undocumented. A future developer modifying call order could silently break wage-base capping by moving the INSERT after `get_ytd_earnings`. | Latent fragility; incorrect FICA withholding if call order is changed without understanding the dependency. | Medium |
| PP-YTD-04 | Mid-year hire YTD reset is acknowledged in the package spec but unresolved. The specific edge case is not documented, there is no test harness, and no compensating fix exists in the current code. Mid-year new hires may have incorrect Social Security or Medicare withholding for their first full year of employment. | Tax compliance risk for new hires; could generate IRS Form 941 discrepancies and require W-2 corrections. | Medium |

---

### Automation Opportunities (New — `PKG_PAYROLL.get_ytd_earnings`)

| ID | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-YTD-01 | Fix YTD figures in `get_payslip` by replacing hardcoded `0` with calls to `get_ytd_earnings` | `get_payslip` returns `0 AS YTD_GROSS` and `0 AS YTD_NET` for every payslip | Replace the two `0` literals with subquery or post-fetch calculation using `get_ytd_earnings(pd.EMP_ID, EXTRACT(YEAR FROM pp.PERIOD_START_DATE))`; also compute YTD net by subtracting YTD deductions | High — makes payslips legally accurate; required for W-2 readiness |
| AO-YTD-02 | Pre-aggregate YTD earnings in bulk at the start of `calculate_payroll` rather than per-employee per-run | One three-table aggregation per employee inside a cursor loop — O(n) queries per run | Before the cursor loop, execute a single GROUP BY query over `PAYROLL_DETAILS` for all active employees in the current tax year and store results in a PL/SQL associative array; pass the pre-fetched value into `calculate_employee_pay` as a new parameter | High — reduces n separate aggregations to 1 per run; eliminates the dominant scalability bottleneck |
| AO-YTD-03 | Document and add a code comment pinning the required INSERT-before-call ordering | Silent ordering dependency between the EARNING INSERT and the `get_ytd_earnings` call | Add a one-line comment above the `get_ytd_earnings` call: `-- NOTE: current period gross already inserted above; ytd includes this period by design for FICA cap enforcement`; add an assertion or reference in the package spec | Low — defensive; prevents silent regression in future refactors |
| AO-YTD-04 | Investigate and fix mid-year hire YTD reset | Known defect, unresolved | Reproduce using a test employee hired mid-year (e.g., 1 July) in a biweekly schedule; add a targeted fix — likely either a `MAX(HIRE_DATE, PERIOD_START_DATE)` guard in the YTD query or a hire-year boundary check before calling `get_ytd_earnings` with the default tax year | Medium — FICA/Medicare accuracy for new hires; required for first-year W-2 correctness |

---

### Validation Queue Items (New — `PKG_PAYROLL.get_ytd_earnings`)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-YTD-01 | Supplemental | Payroll / YTD Reporting | Confirm whether `get_payslip` YTD placeholders are intentional (to be filled by a separate reporting layer) or an unfinished implementation. If intentional, identify which component is responsible for populating YTD on employee-facing payslips. | ❓ UNRESOLVED — comment says "Placeholder" but no companion component found |
| VQ-YTD-02 | Supplemental | Payroll / Tax Compliance | Confirm the exact mid-year hire edge case that triggers the acknowledged YTD reset defect. Determine whether it affects FICA withholding amounts (SS/Medicare) or only the YTD reporting figure. Provide a test case and expected vs. actual result. | ❓ UNRESOLVED — defect acknowledged in spec, root cause not documented |
| VQ-YTD-03 | Supplemental | Payroll / REVERSED Runs | Confirm whether a reversed payroll run should remove the reversed period from YTD (current behaviour via STATUS filter) or whether a separate reversing entry should be tracked. Clarify how reversed earnings interact with W-2 annual totals. | ❓ UNRESOLVED — business/tax policy decision required |
| VQ-YTD-04 | Supplemental | Payroll / Performance | Confirm whether `PAYROLL_DETAILS` has a composite index on `(EMP_ID, ELEMENT_TYPE, STATUS)` and whether `PAY_PERIODS` has an index on `PERIOD_START_DATE`. Without these, `get_ytd_earnings` performs a full scan per employee per run. | ❓ UNRESOLVED — index DDL not in analysed source |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| VQ-04 (YTD accumulation — from Agent 1 Validation Queue) | VQ-04 asked whether YTD accumulation worked correctly; this deep-dive resolves the structural question (it works for FICA/Medicare cap enforcement) but surfaces VQ-YTD-01 (payslip placeholders) and VQ-YTD-02 (mid-year hire defect) as the open items |
| BR-111 (pre-tax deductions never reduce taxable income) | `get_ytd_earnings` accumulates gross `EARNING` amounts; it does not account for pre-tax deductions. `calculate_employee_pay` also applies federal tax to `v_period_gross` directly (comment: "Simplified; should subtract pretax deductions"). The YTD gross passed to FICA/Medicare is therefore overstated by the pre-tax deduction amounts, compounding the BR-111 over-withholding defect across the full year |
| VQ-TERM-05 (off-cycle payroll for final pay — `calculate_final_pay` non-existent) | `calculate_final_pay` does not exist. When implemented, it would need to call `get_ytd_earnings` with the correct tax year to correctly cap FICA on the final paycheck. This is a forward dependency on fixing the non-existent procedure |
| PP-GRC-05 (single end-of-loop COMMIT in `generate_reviews_for_cycle`) | `calculate_payroll` has an analogous pattern: commits every 50 employees. A partial run leaves some employees with `STATUS = 'CALCULATED'` detail rows that `get_ytd_earnings` will include in subsequent re-runs, potentially double-counting a period's earnings in the YTD total if the run is restarted without reversing the partial output |

---

## Supplemental Extraction — PKG_NOTIFICATION (SMS/IN_APP type gap)

**Source:** `plsql/packages/PKG_NOTIFICATION.pkb`
**Topic:** Notification type handling — `NOTIFICATION_QUEUE` declares `SMS` and `IN_APP` types but `process_queue` only processes `EMAIL`; no business rule governs fallback or routing for non-EMAIL types.

---

### Package Overview

`PKG_NOTIFICATION` is the HRMS notification subsystem. It provides four procedures:

| Procedure | Purpose |
|---|---|
| `send_notification` | Enqueues a notification row into `NOTIFICATION_QUEUE` (AUTONOMOUS_TRANSACTION) |
| `process_queue` | Batch-dequeues and delivers PENDING EMAIL notifications via UTL_SMTP; called every 5 minutes by a DBMS_SCHEDULER job |
| `retry_failed` | Resets FAILED rows to PENDING if `RETRY_COUNT < p_max_retries` |
| `cancel_notification` | Marks a PENDING row as CANCELLED |

---

### Table: NOTIFICATION_QUEUE (schema as visible from package body)

| Column | Notes from package DML |
|---|---|
| `NOTIFICATION_ID` | PK, sourced from `SEQ_NOTIFICATION.NEXTVAL` |
| `RECIPIENT_EMP_ID` | Optional; used to resolve `EMAIL` from `EMPLOYEES` if `RECIPIENT_EMAIL` not provided |
| `RECIPIENT_EMAIL` | VARCHAR2(100); may be resolved at queue-time from `EMPLOYEES.EMAIL` |
| `NOTIFICATION_TYPE` | VARCHAR2; caller-supplied; default `'EMAIL'` in `send_notification`; filtered to `'EMAIL'` in `process_queue` |
| `SUBJECT` | VARCHAR2 |
| `BODY` | CLOB |
| `STATUS` | `'PENDING'` → `'SENT'` / `'FAILED'` / `'CANCELLED'` |
| `PRIORITY` | NUMBER; lower value = higher priority (ORDER BY PRIORITY ASC) |
| `REFERENCE_TABLE` | Optional context FK (table name string) |
| `REFERENCE_ID` | Optional context FK (row ID) |
| `CREATED_BY` | VARCHAR2 |
| `CREATED_DATE` | DATE |
| `SENT_DATE` | DATE; set on successful send |
| `ERROR_MESSAGE` | VARCHAR2(4000); set on failure |
| `RETRY_COUNT` | NUMBER; incremented on each failure |

---

### Critical Gap: NOTIFICATION_TYPE Filter in process_queue

The `process_queue` cursor contains an explicit hard-coded type filter:

```sql
WHERE STATUS = 'PENDING'
AND NOTIFICATION_TYPE = 'EMAIL'
AND RECIPIENT_EMAIL IS NOT NULL
```

This means:
- Any row inserted with `NOTIFICATION_TYPE = 'SMS'` will **never** be processed.
- Any row inserted with `NOTIFICATION_TYPE = 'IN_APP'` will **never** be processed.
- These rows remain permanently in `STATUS = 'PENDING'` with no transition path to `SENT`, `FAILED`, or `CANCELLED`.
- `retry_failed` resets `FAILED` rows to `PENDING` — but SMS/IN_APP rows never reach `FAILED`; they are trapped in `PENDING` indefinitely.
- `cancel_notification` can manually cancel a specific `PENDING` row, but there is no bulk cleanup path.

---

### Business Rules (New — PKG_NOTIFICATION notification type handling)

| ID | Rule | Source | Confidence |
|---|---|---|---|
| BR-NOTIF-01 | Any caller may submit a notification of any type (`p_type` is unconstrained VARCHAR2 defaulting to `'EMAIL'`) via `send_notification`. The queue accepts `SMS`, `IN_APP`, or any other string without validation or rejection. | `.pkb` `send_notification` signature | High |
| BR-NOTIF-02 | `process_queue` exclusively processes rows where `NOTIFICATION_TYPE = 'EMAIL'`. This filter is hard-coded in the cursor WHERE clause and cannot be overridden by any parameter. No other procedure processes non-EMAIL rows. | `.pkb` `process_queue` cursor | High |
| BR-NOTIF-03 | A notification row inserted with `NOTIFICATION_TYPE = 'SMS'` or `'IN_APP'` will remain in `STATUS = 'PENDING'` permanently. There is no delivery path, no failure path, and no automatic expiry for these rows in the current codebase. | `.pkb` full body | High |
| BR-NOTIF-04 | Email delivery uses UTL_SMTP with hard-coded SMTP configuration constants (`c_smtp_host = 'smtp.internal.company.com'`, `c_smtp_port = 25`, `c_from_address = 'hrms-noreply@company.com'`). These values are embedded in the package body and cannot be changed without a DDL recompile. No equivalent delivery configuration exists for SMS or IN_APP. | `.pkb` constants block | High |
| BR-NOTIF-05 | If `p_recipient_email` is NULL and `p_recipient_emp_id` is provided, `send_notification` resolves the email address from `EMPLOYEES.EMAIL` at queue-time. If the employee does not exist, `v_email` is set to NULL and the row is inserted with `RECIPIENT_EMAIL = NULL`. | `.pkb` `send_notification` email-resolve block | High |
| BR-NOTIF-06 | A PENDING EMAIL row where `RECIPIENT_EMAIL IS NULL` is silently excluded from `process_queue` processing by the `AND RECIPIENT_EMAIL IS NOT NULL` filter. The row remains PENDING indefinitely with no error, no failure record, and no notification to the inserting caller. | `.pkb` `process_queue` cursor | High |
| BR-NOTIF-07 | `send_notification` executes as an AUTONOMOUS_TRANSACTION. It always issues a COMMIT (success path) or ROLLBACK (exception path) independent of the caller's transaction. A caller that rolls back its own transaction will still have the notification row committed in `NOTIFICATION_QUEUE`. | `.pkb` `PRAGMA AUTONOMOUS_TRANSACTION` + COMMIT/ROLLBACK | High |
| BR-NOTIF-08 | Notification failures inside `send_notification` are swallowed: the exception handler performs a ROLLBACK and calls `PKG_COMMON.log_error`, but does not re-raise. The calling business procedure receives no indication that notification queuing failed. | `.pkb` `send_notification` EXCEPTION block | High |
| BR-NOTIF-09 | `process_queue` opens a new UTL_SMTP connection per notification row. There is no connection reuse or connection pooling across rows in the batch. Each email incurs full SMTP handshake overhead. | `.pkb` `process_queue` loop body | High |
| BR-NOTIF-10 | On SMTP failure, the row is marked `STATUS = 'FAILED'` and `RETRY_COUNT` is incremented. `retry_failed` can reset the row to `PENDING` if `RETRY_COUNT < p_max_retries` (default 3). After 3 failures the row remains permanently FAILED — there is no dead-letter or escalation path. | `.pkb` `process_queue` exception + `retry_failed` | High |
| BR-NOTIF-11 | `process_queue` issues a single COMMIT after the entire batch loop. If the Oracle session terminates mid-batch, all STATUS updates for that batch are lost and rows revert to PENDING, allowing them to be reprocessed. This makes delivery at-most-once within a single successful batch run. | `.pkb` `process_queue` post-loop COMMIT | High |
| BR-NOTIF-12 | Notifications are delivered in priority ascending, created date ascending order (`ORDER BY PRIORITY ASC, CREATED_DATE ASC`). Lower priority numbers are processed first. No starvation prevention exists for high-priority-number rows if lower-priority rows accumulate faster than the batch size. | `.pkb` `process_queue` cursor ORDER BY | High |

---

### Process Flow: Notification Lifecycle

```
[Business Procedure / Caller]
        |
        v  send_notification(p_type='EMAIL'|'SMS'|'IN_APP', ...)
        |  [AUTONOMOUS_TRANSACTION -- always commits independently]
        v
NOTIFICATION_QUEUE row inserted (STATUS='PENDING')
        |
        +-- NOTIFICATION_TYPE = 'EMAIL' AND RECIPIENT_EMAIL IS NOT NULL
        |         |
        |         v  [DBMS_SCHEDULER every 5 min -> process_queue]
        |    UTL_SMTP delivery attempt
        |         +-- Success -> STATUS='SENT', SENT_DATE=SYSDATE
        |         +-- Failure -> STATUS='FAILED', ERROR_MESSAGE=SQLERRM, RETRY_COUNT+1
        |                   |
        |                   +-- retry_failed (RETRY_COUNT < 3)
        |                             +-- STATUS reset to 'PENDING' -> re-enters flow above
        |                             (after 3 failures: row stays FAILED permanently)
        |
        +-- NOTIFICATION_TYPE = 'EMAIL' AND RECIPIENT_EMAIL IS NULL
        |         +-- WARNING: Row stays PENDING indefinitely -- excluded by cursor filter; no error logged
        |
        +-- NOTIFICATION_TYPE = 'SMS'
        |         +-- WARNING: Row stays PENDING indefinitely -- no processor exists; no error
        |
        +-- NOTIFICATION_TYPE = 'IN_APP'
                  +-- WARNING: Row stays PENDING indefinitely -- no processor exists; no error
```

---

### Pain Points (New — PKG_NOTIFICATION)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-NOTIF-01 | `NOTIFICATION_QUEUE` schema accepts `SMS` and `IN_APP` notification types, but `process_queue` only processes `EMAIL`. Any SMS or IN_APP row inserted by a business procedure accumulates in PENDING state permanently with no delivery, no failure flag, and no cleanup mechanism. The queue will grow without bound if non-EMAIL types are ever used. | Silent data accumulation; notification SLA unmet for SMS/IN_APP channels; potential table bloat over time | Critical |
| PP-NOTIF-02 | No business rule or code comment specifies the intended routing for `SMS` or `IN_APP` types. It is unclear whether these types were planned for future implementation, were part of a removed feature, or were mistakenly declared. The schema implies an intent to support multi-channel delivery that is not implemented. | Requirements ambiguity for modernisation: the migration scope cannot be confirmed without business input on whether SMS/IN_APP channels are in-scope | High |
| PP-NOTIF-03 | Hard-coded SMTP constants (`c_smtp_host`, `c_smtp_port`, `c_from_address`, `c_from_name`) are embedded in the package body. Changing the SMTP relay, port, or sender identity requires a DDL recompile and redeployment — it cannot be done via `SYSTEM_PARAMETERS` at runtime. | Operational inflexibility; environment-specific values (dev/test/prod) require separate compiled packages or manual constant updates | High |
| PP-NOTIF-04 | EMAIL rows where `RECIPIENT_EMAIL IS NULL` are silently excluded from `process_queue` without any status change or log entry. A notification queued for an employee whose `EMPLOYEES.EMAIL` is NULL will never be delivered and will never show as FAILED, making it invisible in operational monitoring. | Undetectable notification gaps; employees with missing email addresses receive no notifications and the system provides no alert | High |
| PP-NOTIF-05 | `process_queue` opens a new UTL_SMTP connection for every row in the batch. For a batch of 50 notifications this means 50 full SMTP handshakes. Under load (e.g., performance review cycle generation triggering bulk notifications), this is a significant latency and connection-exhaustion risk. | Performance bottleneck for bulk notification events; potential SMTP server connection limit exhaustion | Medium |
| PP-NOTIF-06 | `send_notification` swallows all queuing exceptions. If `NOTIFICATION_QUEUE` is locked or the sequence is exhausted, the caller proceeds as if notification was successfully queued. The business operation completes but the notification is silently lost. | Invisible notification loss; no operational visibility into queue failures | Medium |
| PP-NOTIF-07 | `process_queue` commits once after the entire batch. An interrupted mid-batch run discards all STATUS updates for that batch. Rows revert to PENDING and may be reprocessed, risking duplicate email delivery for rows that were sent but not yet committed. | Duplicate email risk on session interruption; potential compliance issue if duplicates contain sensitive payroll or benefits data | Medium |

---

### Automation Opportunities (New — PKG_NOTIFICATION)

| ID | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-NOTIF-01 | Implement SMS delivery processor | No SMS delivery path; SMS rows stay PENDING indefinitely | Add a `process_sms_queue` procedure (or extend `process_queue` with a type dispatch) integrating with an SMS gateway via UTL_HTTP; register in the DBMS_SCHEDULER job | High — activates declared schema capability; eliminates silent queue accumulation |
| AO-NOTIF-02 | Implement IN_APP delivery processor | No IN_APP delivery path; IN_APP rows stay PENDING indefinitely | Add a `process_inapp_queue` procedure that marks rows for client-side polling or pushes to a web notification endpoint; exact mechanism depends on front-end architecture | High — activates declared capability; required for web/mobile modernisation |
| AO-NOTIF-03 | Move SMTP configuration to `SYSTEM_PARAMETERS` | Four constants hardcoded in package body | Read `c_smtp_host`, `c_smtp_port`, `c_from_address`, `c_from_name` from `SYSTEM_PARAMETERS` at procedure start via `PKG_COMMON.get_param`; allows per-environment configuration without recompile | Medium — operational improvement; eliminates deployment step for config changes |
| AO-NOTIF-04 | Add a `NOTIFICATION_TYPE` CHECK constraint on `NOTIFICATION_QUEUE` | Column is unconstrained VARCHAR2; any value is accepted silently | Add `CONSTRAINT chk_notif_type CHECK (NOTIFICATION_TYPE IN ('EMAIL','SMS','IN_APP'))` or introduce a `NOTIFICATION_TYPES` reference table; reject invalid types at insert rather than silently accumulating unprocessable rows | Medium — prevents future invalid-type accumulation; forces explicit intent on new channel additions |
| AO-NOTIF-05 | Mark undeliverable rows explicitly (NULL email, unsupported type) | These rows stay PENDING forever with no differentiation from legitimately queued rows | Add a `validate_queue` procedure that marks non-processable rows as `STATUS='UNDELIVERABLE'` with a descriptive `ERROR_MESSAGE`; run as part of the scheduler job | Medium — operational monitoring improvement; allows DBA/admin to identify and investigate accumulating non-EMAIL rows |
| AO-NOTIF-06 | Implement per-row commit in `process_queue` | Single end-of-batch COMMIT; duplicate send risk on interruption | Commit after each successful `UPDATE ... SET STATUS='SENT'` inside the inner loop; makes delivery idempotent across session interruptions | Medium — eliminates duplicate email risk; trade-off is more frequent commit overhead |

---

### Validation Queue Items (New — PKG_NOTIFICATION)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-NOTIF-01 | Supplemental | Notification / Channel Strategy | Confirm whether SMS and IN_APP notification types are intended for future implementation, were part of a removed feature, or are dead schema artefacts. This determines whether AO-NOTIF-01 and AO-NOTIF-02 are in-scope for modernisation. | UNRESOLVED — business/product decision required |
| VQ-NOTIF-02 | Supplemental | Notification / Schema Constraint | Confirm whether `NOTIFICATION_QUEUE.NOTIFICATION_TYPE` has a CHECK constraint in the live schema (not visible from package body alone). If unconstrained, confirm whether adding `CHECK (NOTIFICATION_TYPE IN ('EMAIL','SMS','IN_APP'))` is acceptable or whether additional channel types exist or are planned. | UNRESOLVED — schema DDL audit required |
| VQ-NOTIF-03 | Supplemental | Notification / Operational Backlog | Determine whether any SMS or IN_APP rows currently exist in `NOTIFICATION_QUEUE` with `STATUS='PENDING'`. If so, quantify the backlog and decide whether to bulk-cancel, archive, or retain for future delivery. | UNRESOLVED — operational data audit required |
| VQ-NOTIF-04 | Supplemental | Notification / SMTP Configuration | Confirm whether `smtp.internal.company.com:25` is the correct and current SMTP relay for all environments (dev/test/prod). If environment-specific values differ, this is a regression risk — the same compiled package body applies to all environments. | UNRESOLVED — infrastructure/DevOps confirmation required |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-GRC-06 / PP-GRC-03 (`generate_reviews_for_cycle` fires notifications against DRAFT cycles) | Notifications triggered unconditionally by `generate_reviews_for_cycle` call `send_notification`; if those calls specify a non-EMAIL type or the employee email is NULL, the notification is silently lost — PP-NOTIF-04 and PP-NOTIF-06 compound PP-GRC-03 |
| PP-BA-07 / PP-EC-01 (schema capabilities declared but never consumed) | SMS and IN_APP types follow the same pattern: declared in the schema domain, accepted at insert time, but never processed — identical structural gap to EMPLOYEE_BANK_ACCOUNTS and EMERGENCY_CONTACTS |
| BR-GIS-04 / PP-GIS-01 (integration procedures run unconditionally) | Both findings share the root pattern of a capability designed with multi-channel/multi-state intent but implemented with a single hard-coded path; `process_queue` mirrors the integration procedures' lack of routing logic |

---

---

## Supplemental Extraction — `HRMS.TAX_BRACKETS` + `calculate_federal_tax` / `calculate_state_tax`

**Source files:** `schema/tables/02_payroll_tables.sql`, `plsql/packages/PKG_PAYROLL.pkb`
**Analysis date:** 2026-08-04

---

### Table Definition — `HRMS.TAX_BRACKETS`

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| BRACKET_ID | NUMBER(10) | NOT NULL | — | Primary key |
| TAX_YEAR | NUMBER(4) | NOT NULL | — | Calendar year the bracket applies to |
| FILING_STATUS | VARCHAR2(30) | NOT NULL | — | Constrained: SINGLE / MARRIED_JOINT / MARRIED_SEPARATE / HEAD_OF_HOUSEHOLD |
| BRACKET_MIN | NUMBER(12,2) | NOT NULL | — | Lower bound of income bracket (inclusive) |
| BRACKET_MAX | NUMBER(12,2) | NULL | — | Upper bound; NULL = unbounded top bracket |
| TAX_RATE | NUMBER(5,4) | NOT NULL | — | Marginal rate as decimal (e.g. 0.2200 = 22%) |
| BASE_TAX | NUMBER(12,2) | NULL | 0 | Pre-computed cumulative tax at bracket floor; enables shortcut `BASE_TAX + (income - BRACKET_MIN) × TAX_RATE` |
| STATE_CODE | VARCHAR2(3) | NULL | — | NULL = federal bracket; populated = state-level bracket |
| ACTIVE_FLAG | CHAR(1) | NOT NULL | 'Y' | Year-over-year versioning; prior-year rows expected to be inactivated |
| CREATED_BY | VARCHAR2(30) | NOT NULL | — | Audit |
| CREATED_DATE | DATE | NOT NULL | SYSDATE | Audit |

**Constraints:**
- `PK_TAX_BRACKETS` — PRIMARY KEY (BRACKET_ID)
- `CHK_FILING_STATUS` — FILING_STATUS IN ('SINGLE', 'MARRIED_JOINT', 'MARRIED_SEPARATE', 'HEAD_OF_HOUSEHOLD')

**Notable absences:**
- No UNIQUE constraint on `(TAX_YEAR, FILING_STATUS, BRACKET_MIN, STATE_CODE)` — duplicate bracket rows are structurally permitted.
- No CHECK constraint ensuring `BRACKET_MIN < BRACKET_MAX` when BRACKET_MAX is not NULL.
- No CHECK constraint validating `TAX_RATE` is in range (0, 1].
- No foreign key to any jurisdiction or state reference table — STATE_CODE is free-form VARCHAR2(3).
- No sequence name documented for BRACKET_ID generation (presumably `SEQ_TAX_BRACKETS.NEXTVAL` by convention; not confirmed in analysed source).

---

### Designed Use vs. Actual Use — The Central Finding

TAX_BRACKETS exists to provide a data-driven source for tax bracket lookups. `calculate_federal_tax` contains explicit acknowledgement that this design was never fulfilled:

```sql
-- NOTE: Hard-coded 2024 brackets - should read from TAX_BRACKETS table
-- TODO: Read from TAX_BRACKETS table instead of hard-coding
```

**Despite TAX_BRACKETS existing in the schema, `calculate_federal_tax` never queries it.** All bracket logic is encoded as a hard-coded IF/ELSIF chain. `calculate_state_tax` also ignores the table entirely, using a hard-coded CASE expression of flat rates. **TAX_BRACKETS is a dead table — no procedure in the analysed source inserts into it or reads from it.**

---

### Hard-Coded Federal Brackets in `calculate_federal_tax` (2024 values)

**Filing Status: SINGLE or MARRIED_SEPARATE**

| Bracket Min | Bracket Max | Rate | Base Tax (encoded) |
|---|---|---|---|
| $0 | $11,600 | 10% | $0 |
| $11,601 | $47,150 | 12% | $1,160.00 |
| $47,151 | $100,525 | 22% | $5,426.00 |
| $100,526 | $191,950 | 24% | $17,168.50 |
| $191,951 | $243,725 | 32% | $39,110.50 |
| $243,726 | $609,350 | 35% | $55,678.50 |
| $609,351 | ∞ | 37% | $183,647.25 |

**Filing Status: MARRIED_JOINT**

| Bracket Min | Bracket Max | Rate | Base Tax (encoded) |
|---|---|---|---|
| $0 | $23,200 | 10% | $0 |
| $23,201 | $94,300 | 12% | $2,320.00 |
| $94,301 | $201,050 | 22% | $10,852.00 |
| $201,051 | $383,900 | 24% | $34,337.00 |
| $383,901 | $487,450 | 32% | $78,221.00 |
| $487,451 | $731,200 | 35% | $111,357.00 |
| $731,201 | ∞ | 37% | $196,669.50 |

**Notable absence: No bracket chain exists for `HEAD_OF_HOUSEHOLD`.** The filing status is a valid value in `CHK_FILING_STATUS` and in `EMPLOYEE_TAX_INFO`, but `calculate_federal_tax` has no corresponding IF branch. Any employee with this filing status falls through all conditions and returns `v_tax = 0` — zero federal withholding regardless of income.

---

### `calculate_federal_tax` — Full Logic Flow

```
calculate_federal_tax(p_taxable_income, p_filing_status, p_allowances, p_additional_wh, p_pay_frequency)
        │
        ├─ 1. Determine v_periods from p_pay_frequency
        │      WEEKLY=52 | BIWEEKLY=26 | SEMIMONTHLY=24 | MONTHLY=12 | else=12
        │
        ├─ 2. Annualize: v_annualized = p_taxable_income × v_periods
        │
        ├─ 3. Standard deduction:
        │      MARRIED_JOINT  →  $29,200 (c_standard_deduction_married)
        │      All others     →  $14,600 (c_standard_deduction_single)
        │
        ├─ 4. Allowances: v_taxable = v_annualized - std_deduction - (p_allowances × $4,300)
        │
        ├─ 5. Guard: if v_taxable ≤ 0  →  RETURN 0
        │
        ├─ 6. Apply progressive brackets (hard-coded IF/ELSIF)
        │      HEAD_OF_HOUSEHOLD  →  no branch  →  v_tax remains 0
        │
        ├─ 7. De-annualize: v_tax = ROUND(v_tax / v_periods, 2)
        │
        └─ 8. Add additional WH: v_tax = v_tax + NVL(p_additional_wh, 0)
               RETURN v_tax
```

Input source: called from `calculate_employee_pay` with `v_taxable_income = v_period_gross` — no pre-tax deductions subtracted before the call (see BR-111 / BR-TAX-16).

---

### `calculate_state_tax` — Full Logic Flow

```
calculate_state_tax(p_taxable_income, p_state_code, p_filing_status, p_allowances, p_pay_frequency)
        │
        ├─ Hard-coded CASE on p_state_code:
        │      CA=7.25% | NY=6.85% | TX=0% | FL=0% | WA=0%
        │      IL=4.95% | PA=3.07% | OH=4.00% | NJ=6.37% | MA=5.00%
        │      ELSE=5.00% (default for any unrecognised code)
        │
        ├─ p_allowances   → UNUSED (parameter accepted, never applied)
        ├─ p_pay_frequency → UNUSED (parameter accepted, never applied)
        │
        └─ RETURN ROUND(p_taxable_income × v_rate, 2)
```

TAX_BRACKETS is not queried. STATE_CODE column in TAX_BRACKETS is designed to hold state bracket rows; this function never reads from it.

---

### Business Rules (New — TAX_BRACKETS)

| ID | Rule | Source | Confidence |
|---|---|---|---|
| BR-TAX-01 | TAX_BRACKETS is partitioned by TAX_YEAR, allowing multi-year bracket history in a single table. ACTIVE_FLAG = 'Y' designates the operative year's rows. | DDL: TAX_BRACKETS | High |
| BR-TAX-02 | FILING_STATUS is constrained to exactly four values: SINGLE, MARRIED_JOINT, MARRIED_SEPARATE, HEAD_OF_HOUSEHOLD. | DDL: CHK_FILING_STATUS | High |
| BR-TAX-03 | TAX_BRACKETS supports both federal and state brackets via STATE_CODE: NULL = federal; a three-character state code = state-level bracket. | DDL: TAX_BRACKETS.STATE_CODE | High |
| BR-TAX-04 | BASE_TAX encodes the pre-computed cumulative tax at the bracket floor, enabling the shortcut `BASE_TAX + (income - BRACKET_MIN) × TAX_RATE` without iterating lower brackets. | DDL: TAX_BRACKETS.BASE_TAX | High |
| BR-TAX-05 | Despite the table existing, `calculate_federal_tax` never queries TAX_BRACKETS. 2024 federal brackets are hard-coded as a seven-level IF/ELSIF chain. Both a NOTE and a TODO comment explicitly acknowledge this gap in the function body. | PKG_PAYROLL.pkb: calculate_federal_tax | High — explicit in source |
| BR-TAX-06 | `calculate_state_tax` never queries TAX_BRACKETS. State tax is a flat rate per state code using a hard-coded CASE; the ELSE branch applies a default 5% to any unrecognised state. | PKG_PAYROLL.pkb: calculate_state_tax | High |
| BR-TAX-07 | Federal tax is calculated on annualized income: per-period gross × periods-per-year, brackets applied, result divided back to a per-period amount. | PKG_PAYROLL.pkb: calculate_federal_tax | High |
| BR-TAX-08 | Standard deductions are hard-coded as package-level constants: $14,600 (SINGLE/MARRIED_SEPARATE/HEAD_OF_HOUSEHOLD), $29,200 (MARRIED_JOINT). These are 2024 IRS values. | PKG_PAYROLL.pkb: constants | High |
| BR-TAX-09 | Each FEDERAL_ALLOWANCES unit reduces annualized taxable income by $4,300 (c_allowance_amount) before brackets are applied. | PKG_PAYROLL.pkb: calculate_federal_tax | High |
| BR-TAX-10 | If annualized taxable income after standard deduction and allowances is zero or negative, `calculate_federal_tax` returns 0. | PKG_PAYROLL.pkb: calculate_federal_tax guard | High |
| BR-TAX-11 | ADDITIONAL_FED_WH is added as a flat per-period supplement after all bracket calculations. | PKG_PAYROLL.pkb: calculate_federal_tax | High |
| BR-TAX-12 | HEAD_OF_HOUSEHOLD has no bracket branch in `calculate_federal_tax`. An employee with this filing status will have $0 federal income tax withheld regardless of earnings. | PKG_PAYROLL.pkb: calculate_federal_tax | High — confirmed by code inspection |
| BR-TAX-13 | STATE_ALLOWANCES and pay-frequency annualization are accepted as parameters to `calculate_state_tax` but neither is used. State tax is applied as a flat rate on the raw per-period gross. | PKG_PAYROLL.pkb: calculate_state_tax | High |
| BR-TAX-14 | Any state code not explicitly listed in `calculate_state_tax` receives a 5% flat default rate, including territories, non-US countries, and future states. No warning or error is raised for unrecognised codes. | PKG_PAYROLL.pkb: calculate_state_tax ELSE | High |
| BR-TAX-15 | TAX_BRACKETS.BRACKET_MAX is nullable; NULL signifies the topmost unbounded bracket, mirroring the final ELSE branch of the hard-coded IF/ELSIF chain. | DDL: TAX_BRACKETS | High |
| BR-TAX-16 | `calculate_employee_pay` passes `v_period_gross` directly as `p_taxable_income` to `calculate_federal_tax` without first subtracting pre-tax deductions. Code comment acknowledges: "Simplified; should subtract pretax deductions." This causes over-withholding for all employees with pre-tax benefit deductions. | PKG_PAYROLL.pkb: calculate_employee_pay | High — explicit in source |

---

### Defect Summary

| Issue | Location | Severity | Details |
|---|---|---|---|
| TAX_BRACKETS never queried | `calculate_federal_tax`, `calculate_state_tax` | Critical | The table is designed as the bracket data store but neither function reads from it. Annual tax-year updates require a code release, not a data change. |
| HEAD_OF_HOUSEHOLD produces zero withholding | `calculate_federal_tax` | Critical | No IF branch for this filing status. Employees filing as HEAD_OF_HOUSEHOLD receive $0 federal withholding every period. Under-withholding at this scale generates IRS penalties (employee underpayment, employer failure-to-withhold liability) and requires W-2 corrections. |
| State allowances silently ignored | `calculate_state_tax` | High | `p_allowances` accepted but discarded. Employees in allowance-based states (CA, NY, NJ) are systematically over-withheld for state tax. |
| State tax not annualized | `calculate_state_tax` | High | Flat rate applied to per-period income. States with progressive brackets (CA, NY) require annualized income for bracket determination; the flat-rate approach is correct only for flat-tax states. |
| Hard-coded 2024 brackets — no year resolution | `calculate_federal_tax` | High | No TAX_YEAR parameter; no lookup from TAX_BRACKETS. Payroll runs in 2025 and beyond use 2024 brackets. IRS adjusts brackets annually for inflation. |
| No UNIQUE constraint on TAX_BRACKETS | DDL | Medium | Duplicate rows for `(TAX_YEAR, FILING_STATUS, BRACKET_MIN, STATE_CODE)` are permitted. If the table is activated for live queries, ambiguous rows produce non-deterministic results. |
| BASE_TAX DEFAULT 0 may mislead | DDL | Low | A missing BASE_TAX entry produces a silently wrong shortcut calculation rather than an error. NULL sentinel would make the data gap explicit and force explicit handling. |

---

### Pain Points (New — TAX_BRACKETS)

| ID | Pain Point | Impact | Severity |
|---|---|---|---|
| PP-TAX-01 | Tax brackets are hard-coded in PL/SQL source rather than loaded from TAX_BRACKETS. Every IRS annual inflation adjustment requires a developer edit and redeployment of `PKG_PAYROLL`. For 2025 onwards the 2024 brackets are already stale. | Annual compliance risk; incorrect withholding generates under/over-payment, W-2 corrections, IRS reconciliation effort. | Critical |
| PP-TAX-02 | Employees filing HEAD_OF_HOUSEHOLD receive zero federal income tax withholding. No error is raised, no warning is logged; the only observable signal is an employee examining their payslip. Payslips show $0 federal tax in ELEMENT_ID 100 — the same slot as all other employees. | Employer failure-to-withhold liability; employee underpayment penalties; W-2 corrections at year-end. | Critical |
| PP-TAX-03 | State allowances accepted as parameter to `calculate_state_tax` but never applied. Employees in allowance-based states are over-withheld for state tax throughout the year. | Employee financial impact; payroll credibility; potential state agency enquiries if aggregate withholding is materially over-remitted. | High |
| PP-TAX-04 | `calculate_state_tax` applies a 5% default to any unrecognised state code — including territories (PR, GU, VI) and any state added after the code was written. Rate is incorrect for most of these jurisdictions. | Compliance risk for employees in territories or unlisted states; state tax agency notifications likely for affected employees. | High |
| PP-TAX-05 | TAX_BRACKETS is presumably populated (or intended to be populated) but never read. Any data entered into the table has no effect on payroll. Administrators updating TAX_BRACKETS to adjust for a new year will be invisibly wrong — hard-coded brackets continue to govern all withholding. | Data integrity risk; administrator confidence erosion; double maintenance burden (code and data both require updates, but only code actually matters). | High |

---

### Automation Opportunities (New — TAX_BRACKETS)

| ID | Opportunity | Current State | Suggested Approach | Expected Impact |
|---|---|---|---|---|
| AO-TAX-01 | Replace hard-coded IF/ELSIF bracket chain in `calculate_federal_tax` with a dynamic lookup from TAX_BRACKETS | Seven-level hard-coded chain, 2024 values only, no year resolution | Add `p_tax_year NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE)` parameter; SELECT brackets `WHERE TAX_YEAR = p_tax_year AND FILING_STATUS = p_filing_status AND STATE_CODE IS NULL ORDER BY BRACKET_MIN`; iterate cursor and apply `BASE_TAX + (v_taxable - BRACKET_MIN) × TAX_RATE` shortcut on the matching row | Critical — makes annual bracket updates a data-only change; eliminates annual code-release requirement; activates TAX_BRACKETS as designed |
| AO-TAX-02 | Fix HEAD_OF_HOUSEHOLD zero-withholding defect | No IF branch for this filing status | Add an explicit IF branch using the 2024 IRS HEAD_OF_HOUSEHOLD table (or, after AO-TAX-01, the lookup handles it automatically if bracket rows are loaded for that filing status) | Critical — stops silent under-withholding for a statutory W-4 category |
| AO-TAX-03 | Add annualization and allowance logic to `calculate_state_tax` | Flat rate on per-period gross; allowances ignored; `p_allowances` and `p_pay_frequency` dead parameters | Apply the same annualize → deduct allowances → bracket lookup → de-annualize pattern as the federal path; use TAX_BRACKETS with `STATE_CODE = p_state_code` once AO-TAX-01 is in place | High — makes state withholding accurate for progressive-bracket states; correctly applies state allowances |
| AO-TAX-04 | Add UNIQUE constraint to TAX_BRACKETS on `(TAX_YEAR, FILING_STATUS, BRACKET_MIN, STATE_CODE)` | No uniqueness enforcement | `ALTER TABLE HRMS.TAX_BRACKETS ADD CONSTRAINT UK_TAX_BRACKET UNIQUE (TAX_YEAR, FILING_STATUS, BRACKET_MIN, STATE_CODE)` | Medium — prevents duplicate-bracket ambiguity when the table is activated for live queries |

---

### Validation Queue Items (New — TAX_BRACKETS)

| ID | Pass | Domain | Item | Status |
|---|---|---|---|---|
| VQ-TAX-01 | Supplemental | Payroll / Tax Compliance | Confirm whether TAX_BRACKETS is currently populated with any rows. If so, confirm which process inserts rows (manual DML, a seed script, or a procedure not in the analysed source) and the intended maintenance cadence (annual, per-IRS-publication, ad-hoc). | ❓ UNRESOLVED — no INSERT or SELECT targeting TAX_BRACKETS found in analysed source |
| VQ-TAX-02 | Supplemental | Payroll / Tax Compliance | Confirm the business rule for HEAD_OF_HOUSEHOLD employees: is zero withholding intentional (exempt treatment) or a defect? If a defect, confirm the correct bracket set (IRS provides a separate HEAD_OF_HOUSEHOLD table; some implementations approximate with the SINGLE table). | ❓ UNRESOLVED — likely a defect; requires payroll tax SME confirmation |
| VQ-TAX-03 | Supplemental | Payroll / Tax Compliance | Confirm which sequence populates TAX_BRACKETS.BRACKET_ID. Convention suggests `SEQ_TAX_BRACKETS.NEXTVAL` but no such sequence DDL is present in the analysed source. | ❓ UNRESOLVED — sequence DDL not found |
| VQ-TAX-04 | Supplemental | Payroll / State Tax | Confirm the correct treatment for state allowances in each state where EMPLOYEE_TAX_INFO.STATE_ALLOWANCES is recorded. Determine whether `calculate_state_tax` should mirror the federal annualize → deduct → bracket → de-annualize logic or whether a flat-rate approach is intentionally correct for all states the company operates in. | ❓ UNRESOLVED — requires state-by-state payroll tax policy confirmation |

---

### Relationship to Existing Findings

| Existing Item | Relationship |
|---|---|
| BR-111 (pre-tax deductions never reduce taxable income) | The federal tax over-withholding from BR-111 and the TAX_BRACKETS under-utilisation are compounding defects. Federal tax is computed on inflated gross (no pre-tax deductions subtracted) using stale brackets (hard-coded 2024 values). Both errors bias in the same direction: over-collection of federal income tax. |
| PP-YTD-01 (payslip YTD placeholders) | When YTD federal tax placeholders are fixed (AO-YTD-01), the per-period federal tax feeding into YTD will itself be incorrect (stale brackets, zero for HEAD_OF_HOUSEHOLD). Fixing the YTD display makes the bracket defects more visible to employees and auditors. |
| VQ-04 (YTD accumulation — Agent 1) | `get_ytd_earnings` accumulates raw gross; stale bracket over-withholding does not affect the YTD gross amount, but does inflate YTD tax deductions. This makes YTD figures appear inconsistently high relative to net once placeholders are fixed. |
| VQ-TERM-05 (`calculate_final_pay` non-existent) | When `calculate_final_pay` is implemented it will call `calculate_federal_tax`. If brackets remain hard-coded, any final paycheck processed after 2024 uses wrong bracket values. |
| AO-TAX-01 (this extraction) | Implementing the TAX_BRACKETS lookup for `calculate_federal_tax` also resolves the annual update path for `calculate_state_tax` if state bracket rows are loaded — making both functions fully data-driven with a single schema change. |
| VQ-20 / VQ-GIS-03 (SYSTEM_PARAMETERS credential and config storage) | Hard-coded SMTP constants in the package body (PP-NOTIF-03) are the notification-layer equivalent of the integration layer's cleartext FTP credentials in `SYSTEM_PARAMETERS` — both represent configuration that should be externalised |
