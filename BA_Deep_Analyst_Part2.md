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
