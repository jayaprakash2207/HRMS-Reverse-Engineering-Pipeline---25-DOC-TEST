# 09 — Data Flow Diagram (DFD)
**System:** Acme Corporation HRMS (Oracle 19c)
**Version:** 1.0 — Derived from BA, DA, TA, and AA analysis tracks
**Scope:** All confirmed PL/SQL packages, schema tables, integration endpoints, and notification channels recovered from source analysis.
**Notation:** Yourdon–DeMarco. External entities in brackets `[ ]`, processes in parentheses `( )`, data stores prefixed `D:`.

---

## 0. Document Conventions

| Symbol | Meaning |
|--------|---------|
| `[ENTITY]` | External entity (outside system boundary) |
| `(P-nn)` | Process number |
| `D:TABLE_NAME` | Data store (database table or file) |
| `→` | Data flow direction |
| `⇄` | Bidirectional flow |
| `~>` | Asynchronous / queued flow |
| `✦ PII` | Flow carries personally identifiable information |
| `✧ ENC` | Data encrypted in transit or at rest |
| `⚠` | Gap, defect, or unimplemented path identified in analysis |

---

## 1. Context Diagram — Level 0 DFD

### 1.1 System Boundary

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ACME HRMS (Oracle 19c)                              ║
║                                                                              ║
║   ┌──────────────────────────────────────────────────────────────────────┐  ║
║   │  Oracle Database Boundary                                            │  ║
║   │  ● PL/SQL Packages: PKG_EMPLOYEE, PKG_PAYROLL, PKG_LEAVE,           │  ║
║   │    PKG_PERFORMANCE, PKG_SECURITY, PKG_INTEGRATION,                  │  ║
║   │    PKG_NOTIFICATION, PKG_REPORTING, PKG_COMMON                      │  ║
║   │  ● Oracle Forms: HRMS_EMPLOYEE, HRMS_PAYROLL, HRMS_LEAVE,           │  ║
║   │    HRMS_PERFORMANCE, HRMS_LOGIN, HRMS_REPORTS                       │  ║
║   │  ● Schema: HRMS (30 confirmed tables + inferred tables)             │  ║
║   └──────────────────────────────────────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### 1.2 External Entities and Boundary Flows

```
                          ┌──────────────────────────────────────┐
                          │         ACME HRMS SYSTEM             │
                          │                                      │
[HR_MANAGER] ─────────────► Employee data, payroll approvals     │
             ◄─────────────  Reports, payslips, audit logs        │
                          │                                      │
[EMPLOYEE] ───────────────► Self-assessment, leave requests,     │
           ◄───────────────  Payslips, leave balances, ack       │
                          │                                      │
[PAYROLL_ADMIN] ──────────► Payroll run commands, GL approval    │
                ◄──────────  Run status, error reports           │
                          │                                      │
[SYSTEM_ADMIN] ───────────► User setup, system config           │
               ◄───────────  Audit trail, session logs           │
                          │                                      │
[ADP_BENEFITS] ◄──────────  Benefits feed (fixed-width file)    │  ✦ PII ✧ ENC
                          │                                      │
[ORACLE_FINANCIALS] ◄─────  GL journal feed (pipe-delimited)    │
                          │                                      │
[SMTP_SERVER] ◄───────────  Notification emails                 │  ✦ PII
              ────────────► Delivery status (unimplemented ⚠)   │
                          │                                      │
[NACHA_ACH] ◄─────────────  ACH disbursement file ⚠            │  ✦ PII ✧ ENC
                          │  (UNIMPLEMENTED — design gap)        │
                          │                                      │
[TIME_CLOCK_SYSTEM] ──────► Time/attendance CSV file            │
                          │  (import stub — unimplemented ⚠)    │
                          │                                      │
[LDAP_AD] ◄───────────────  Org structure sync ⚠               │
          ────────────────►  (UNIMPLEMENTED — placeholder only) │
                          └──────────────────────────────────────┘
```

### 1.3 External Entity Register

| ID | External Entity | Direction | Data Exchanged | Implementation Status |
|----|----------------|-----------|----------------|----------------------|
| EE-01 | HR Manager | In/Out | Employee records, approvals, reports | Implemented (Oracle Forms) |
| EE-02 | Employee | In/Out | Self-service data, leave, review acknowledgement | Implemented (Forms + portal) |
| EE-03 | Payroll Admin | In/Out | Payroll commands, GL approval, run status | Implemented (Oracle Forms) |
| EE-04 | System Admin | In/Out | User configuration, audit queries | Implemented |
| EE-05 | ADP Benefits | Out only | Fixed-width 203-char benefits/dependent feed | Implemented (file written to OS dir) |
| EE-06 | Oracle Financials GL | Out only | Pipe-delimited journal entries | Implemented (file written to OS dir) |
| EE-07 | SMTP Server | Out only | Plain-text/HTML notification emails | Implemented (UTL_MAIL/UTL_SMTP) |
| EE-08 | NACHA ACH Network | Out only | ACH direct deposit file | **Not implemented** ⚠ |
| EE-09 | Time Clock System | In only | CSV time/attendance records | **Stub only** ⚠ |
| EE-10 | LDAP / Active Directory | In/Out | Org structure synchronisation | **Stub only — logs false success** ⚠ |

---

## 2. Level 1 DFD — Major Processes and Data Stores

### 2.1 Level 1 Process Inventory

| Process ID | Process Name | Owner Package | Trigger |
|-----------|--------------|---------------|---------|
| P-01 | Employee Lifecycle Management | PKG_EMPLOYEE | HR Manager action |
| P-02 | Payroll Processing | PKG_PAYROLL | Payroll Admin command |
| P-03 | Leave Management | PKG_LEAVE | Employee / Manager action |
| P-04 | Performance Review Cycle | PKG_PERFORMANCE | HR Admin / schedule |
| P-05 | Security and Session Control | PKG_SECURITY | Login event |
| P-06 | Integration and Export | PKG_INTEGRATION | Schedule / manual trigger |
| P-07 | Notifications Dispatch | PKG_NOTIFICATION | Event-driven (called by other packages) |
| P-08 | Reporting and Analytics | PKG_REPORTING | HR Manager on-demand |
| P-09 | Audit and Logging | PKG_COMMON | Called by all packages |

### 2.2 Level 1 Data Store Inventory

| Store ID | Table / Store Name | Primary Owner Process |
|---------|--------------------|-----------------------|
| D-01 | EMPLOYEES | P-01 |
| D-02 | DEPARTMENTS | P-01 |
| D-03 | JOB_POSITIONS | P-01 |
| D-04 | SALARY_RECORDS | P-01, P-02 |
| D-05 | PAYROLL_RUNS | P-02 |
| D-06 | PAYROLL_DETAILS | P-02 |
| D-07 | DEDUCTION_RECORDS | P-02 |
| D-08 | PAY_ELEMENTS | P-02 |
| D-09 | TAX_BRACKETS | P-02 |
| D-10 | LEAVE_BALANCES | P-03 |
| D-11 | LEAVE_REQUESTS | P-03 |
| D-12 | LEAVE_TYPES | P-03 |
| D-13 | PERFORMANCE_REVIEWS | P-04 |
| D-14 | REVIEW_CYCLES | P-04 |
| D-15 | PERFORMANCE_GOALS | P-04 |
| D-16 | GOAL_REVIEWS | P-04 |
| D-17 | USER_SESSIONS | P-05 |
| D-18 | USER_CREDENTIALS | P-05 |
| D-19 | AUDIT_LOG | P-09 |
| D-20 | SYSTEM_PARAMETERS | All |
| D-21 | NOTIFICATION_QUEUE | P-07 |
| D-22 | NOTIFICATION_TEMPLATES | P-07 |
| D-23 | EMPLOYEE_DEPENDENTS | P-06 |
| D-24 | EMPLOYEE_BANK_ACCOUNTS | P-02 ⚠ (unread) |
| D-25 | BENEFIT_PLANS | P-06 |
| D-26 | BENEFIT_ENROLLMENTS | P-06 |
| D-27 | EMPLOYEE_HISTORY | P-01 |
| D-28 | LOOKUP_VALUES | All |
| D-29 | TERMINATION_CODES | P-01 |
| D-30 | TIME_ATTENDANCE_RECORDS | P-06 ⚠ (stub) |
| D-F1 | BENEFITS_FEED file (OS dir) | P-06 |
| D-F2 | GL_JOURNAL file (OS dir) | P-06 |
| D-F3 | NACHA_ACH file (OS dir) | P-06 ⚠ (not written) |
| D-F4 | TIME_ATTENDANCE CSV (OS dir) | P-06 ⚠ (stub read) |

### 2.3 Level 1 Flow Diagram

```
[HR_MANAGER] ──employee data──► (P-01 Employee Lifecycle) ──write──► D-01 EMPLOYEES
                                                           ──write──► D-04 SALARY_RECORDS
                                                           ──write──► D-27 EMPLOYEE_HISTORY
                                  ◄──read employee, salary──
(P-01) ──reads──► D-02 DEPARTMENTS
(P-01) ──reads──► D-03 JOB_POSITIONS
(P-01) ──notify~~► (P-07 Notifications)

[PAYROLL_ADMIN] ──run command──► (P-02 Payroll Processing)
(P-02) ──read active employees──► D-01 EMPLOYEES
(P-02) ──read salary──────────► D-04 SALARY_RECORDS
(P-02) ──read performance──────► D-13 PERFORMANCE_REVIEWS
(P-02) ──read leave taken──────► D-10 LEAVE_BALANCES
(P-02) ──read tax tables──────► D-09 TAX_BRACKETS
(P-02) ──read pay elements──── ► D-08 PAY_ELEMENTS
(P-02) ──write payroll header──► D-05 PAYROLL_RUNS
(P-02) ──write payroll lines───► D-06 PAYROLL_DETAILS
(P-02) ──write deductions──────► D-07 DEDUCTION_RECORDS
(P-02) ──trigger──────────────► (P-06 Integration) ──► D-F2 GL_JOURNAL ──► [ORACLE_FINANCIALS]

[EMPLOYEE] ──leave request──► (P-03 Leave Management)
(P-03) ──read/write balance──► D-10 LEAVE_BALANCES
(P-03) ──write request──────► D-11 LEAVE_REQUESTS
(P-03) ──read leave types───► D-12 LEAVE_TYPES
(P-03) ──notify~~► (P-07 Notifications) ──► [SMTP_SERVER] ──email──► [EMPLOYEE/MANAGER]

[HR_ADMIN] ──create cycle──► (P-04 Performance Review)
(P-04) ──read/write reviews──► D-13 PERFORMANCE_REVIEWS
(P-04) ──read/write cycles───► D-14 REVIEW_CYCLES
(P-04) ──read/write goals────► D-15 PERFORMANCE_GOALS
(P-04) ──write goal reviews──► D-16 GOAL_REVIEWS

[USER] ──credentials──► (P-05 Security)
(P-05) ──read employee──► D-01 EMPLOYEES
(P-05) ──read/write session──► D-17 USER_SESSIONS
(P-05) ──read credentials──► D-18 USER_CREDENTIALS  ⚠ PASSWORD NEVER VERIFIED
(P-05) ──write audit──────► D-19 AUDIT_LOG

(P-06 Integration) ──read employees, dependents──► D-01 EMPLOYEES
                   ──read dependents──────────────► D-23 EMPLOYEE_DEPENDENTS
                   ──read enrollments─────────────► D-26 BENEFIT_ENROLLMENTS
                   ──read payroll details──────────► D-06 PAYROLL_DETAILS
                   ──write file───────────────────► D-F1 BENEFITS_FEED ──► [ADP_BENEFITS]
                   ──write file───────────────────► D-F2 GL_JOURNAL ──────► [ORACLE_FINANCIALS]
                   ──read file────────────────────► D-F4 TIME_CSV ──────── [TIME_CLOCK] ⚠
                   ──bank accts NEVER READ─────────► D-24 ⚠ (NACHA gap)

(P-07 Notifications) ──read template──► D-22 NOTIFICATION_TEMPLATES
                     ──write queue──── ► D-21 NOTIFICATION_QUEUE
                     ──dequeue/send───► [SMTP_SERVER]

(P-09 Audit/Logging) ──write──► D-19 AUDIT_LOG
                     called by all processes
```

---

## 3. Level 2 DFDs — Subsystem Detail

---

### 3.1 Employee Management — Level 2 DFD

#### 3.1.1 Processes

| ID | Process | Entry Point |
|----|---------|-------------|
| P-01.1 | Create Employee | PKG_EMPLOYEE.create_employee |
| P-01.2 | Update Employee | PKG_EMPLOYEE.update_employee |
| P-01.3 | Transfer Employee | PKG_EMPLOYEE.transfer_employee |
| P-01.4 | Terminate Employee | PKG_EMPLOYEE.terminate_employee |
| P-01.5 | Get Employee Details | PKG_EMPLOYEE.get_employee |
| P-01.6 | Search Employees | PKG_EMPLOYEE.search_employees |

#### 3.1.2 Data Flows

```
[HR_MANAGER]
    │
    ├──(first_name, last_name, hire_date, dept_id, job_id, salary, grade)──►
    │
    ▼
(P-01.1 Create Employee)
    │
    ├──validate dept──────────────────────────► D-02 DEPARTMENTS (read)
    ├──validate job──────────────────────────► D-03 JOB_POSITIONS (read)
    ├──validate salary vs grade range──────── ► D-04 SALARY_RECORDS + JOB_GRADES (read)
    │   ⚠ WARNING ONLY, NOT BLOCKING (TD-74)
    ├──generate EMP_ID (SQ_EMPLOYEE_ID)
    ├──encrypt SSN ─────────────────────────► PKG_SECURITY.encrypt_value
    │   ✦ PII ✧ ENC
    ├──INSERT employee row──────────────────► D-01 EMPLOYEES (write)
    ├──INSERT salary record─────────────────► D-04 SALARY_RECORDS (write)
    ├──INSERT history row───────────────────► D-27 EMPLOYEE_HISTORY (write)
    ├──INSERT leave balances (initialize)───► D-10 LEAVE_BALANCES (write)
    │   via PKG_LEAVE.initialize_balances
    └──log audit────────────────────────────► D-19 AUDIT_LOG (write) via PKG_COMMON
```

```
[HR_MANAGER]
    │
    ├──(emp_id, term_date, reason, final_pay_flag)──►
    │
    ▼
(P-01.4 Terminate Employee)
    │
    ├──read employee──────────────────────────► D-01 EMPLOYEES (read)
    ├──set EMPLOYMENT_STATUS='TERMINATED'
    ├──set TERMINATION_DATE = p_term_date
    ├──UPDATE employee row───────────────────► D-01 EMPLOYEES (write)
    ├──INSERT history record─────────────────► D-27 EMPLOYEE_HISTORY (write)
    ├──close open leave requests─────────────► D-11 LEAVE_REQUESTS (update)
    ├──[TODO] COBRA notification────────────► ⚠ NOT IMPLEMENTED (PP-TERM-01)
    ├──[TODO] revoke_access─────────────────► ⚠ PROCEDURE DOES NOT EXIST (PP-TERM-02)
    │   SIDE EFFECT ONLY: new logins blocked via EMPLOYMENT_STATUS check in P-05
    │   In-flight sessions remain valid up to 30 min ⚠
    ├──[TODO] calculate_final_pay────────────► ⚠ PROCEDURE DOES NOT EXIST (PP-TERM-03)
    ├──[MISSING] inactivate dependents──────► D-23 ⚠ NOT TOUCHED (BR-DEP-09)
    ├──[MISSING] inactivate bank accounts───► D-24 ⚠ NOT TOUCHED (PP-BA-07)
    └──log audit────────────────────────────► D-19 AUDIT_LOG
```

#### 3.1.3 Employee History Trigger Flow

```
[DML on EMPLOYEES table]
    │
    ▼
TRG_EMPLOYEES_AUDIT (Row-level AFTER trigger)
    │
    ├──capture OLD/NEW column values
    ├──capture SYSDATE, USER
    └──INSERT INTO D-27 EMPLOYEE_HISTORY
```

---

### 3.2 Payroll Processing — Level 2 DFD (Full Cycle)

#### 3.2.1 Payroll Process Map

```
Phase 1: DRAFT          Phase 2: CALCULATE       Phase 3: APPROVE
──────────────          ──────────────────        ────────────────
[PAYROLL_ADMIN]         [PAYROLL_ADMIN]            [HR_MANAGER]
    │                       │                          │
    ▼                       ▼                          ▼
(P-02.1 Create Run)    (P-02.2 Calculate)         (P-02.3 Approve)
    │                       │                          │
    ▼                       ▼                          ▼
D-05 PAYROLL_RUNS      D-06 PAYROLL_DETAILS        D-05 (status→APPROVED)
STATUS=DRAFT           STATUS=CALCULATED


Phase 4: GL FEED         Phase 5: DISBURSE
────────────────         ─────────────────
[PAYROLL_ADMIN]          [PAYROLL_ADMIN]
    │                        │
    ▼                        ▼
(P-06.1 GL Journal)      (P-02.4 Disburse) ⚠ NOT IMPLEMENTED
    │                        │
    ▼                        ▼
D-F2 GL file             D-24 EMPLOYEE_BANK_ACCOUNTS ⚠ NEVER READ
    │                    D-F3 NACHA file ⚠ NOT WRITTEN
    ▼
[ORACLE_FINANCIALS]
```

#### 3.2.2 P-02.2 Calculate Payroll — Detailed Flow

```
(P-02.2 Calculate Payroll)
    │
    ├──validate run status = DRAFT──────────► D-05 PAYROLL_RUNS (read)
    │
    ├──cursor: all ACTIVE employees
    │   WHERE EMPLOYMENT_STATUS='ACTIVE'
    │   AND HIRE_DATE <= pay_period_end
    │   AND (TERMINATION_DATE IS NULL OR TERMINATION_DATE > pay_period_start)
    │
    └──FOR EACH EMPLOYEE:
        │
        ├──(P-02.2a Read Gross Pay)
        │   ├──read current salary──────────► D-04 SALARY_RECORDS (read)
        │   │   WHERE END_DATE IS NULL
        │   ├──read salary_type (MONTHLY/HOURLY/CONTRACT)
        │   └──compute GROSS = BASE_SALARY / 12 (monthly)
        │
        ├──(P-02.2b Deduction Calculation)
        │   ├──read health deduction ────────► D-07 DEDUCTION_RECORDS (read)
        │   │   ELEMENT_ID=100 (health insurance) ⚠ magic number
        │   ├──read dental deduction─────────► ELEMENT_ID=101 ⚠ magic number
        │   ├──read vision deduction─────────► ELEMENT_ID=102 ⚠ magic number
        │   ├──read 401k deduction────────────► ELEMENT_ID=103 ⚠ magic number
        │   └──SUM all deductions → TOTAL_DEDUCTIONS
        │
        ├──(P-02.2c Tax Calculation)
        │   ├──read TAX_FILING_STATUS──────── ► D-01 EMPLOYEES (read)
        │   │   ✦ PII — drives federal bracket
        │   ├──read STATE──────────────────── ► D-01 EMPLOYEES (read)
        │   │   ✦ PII — drives state flat-rate
        │   ├──read federal brackets──────────► D-09 TAX_BRACKETS (read)
        │   │   WHERE TAX_TYPE='FEDERAL'
        │   ├──compute FEDERAL_TAX (progressive bracket lookup)
        │   │   ⚠ HEAD_OF_HOUSEHOLD returns $0 (defect BR-107)
        │   ├──compute STATE_TAX = GROSS * state_rate
        │   ├──compute FICA_SOCIAL = MIN(GROSS, FICA_WAGE_BASE) * 0.062
        │   └──compute FICA_MEDICARE = GROSS * 0.0145
        │
        ├──(P-02.2d Merit Eligibility Check)
        │   ├──read OVERALL_RATING──────────── ► D-13 PERFORMANCE_REVIEWS (read)
        │   │   WHERE STATUS='COMPLETED' AND most recent cycle
        │   └──IF RATING >= 3.0 THEN eligible_for_merit = TRUE
        │       ⚠ CALIBRATED_RATING never read (dead column)
        │
        ├──(P-02.2e Write Results)
        │   ├──INSERT payroll detail row──────► D-06 PAYROLL_DETAILS (write)
        │   │   (EMP_ID, RUN_ID, GROSS, NET, deductions, taxes, STATUS='CALCULATED')
        │   └──log info──────────────────────► D-19 AUDIT_LOG
        │
        └──(P-02.2f Run Totals)
            ├──UPDATE PAYROLL_RUNS.TOTAL_GROSS
            ├──UPDATE PAYROLL_RUNS.TOTAL_NET
            ├──UPDATE PAYROLL_RUNS.TOTAL_DEDUCTIONS
            └──UPDATE STATUS='CALCULATED'
```

#### 3.2.3 Net Pay Formula (Transformation Point)

```
GROSS_PAY
  = BASE_SALARY / 12                    (monthly salary type)
  = HOURLY_RATE × HOURS_WORKED          (hourly type — unimplemented ⚠)
  = CONTRACT_AMOUNT                     (contract type — unimplemented ⚠)

FEDERAL_TAX   = bracket_lookup(GROSS, TAX_FILING_STATUS)
STATE_TAX     = GROSS × state_rate[STATE]
FICA_SS       = MIN(GROSS, FICA_WAGE_BASE) × 0.062
FICA_MEDICARE = GROSS × 0.0145
TOTAL_TAX     = FEDERAL_TAX + STATE_TAX + FICA_SS + FICA_MEDICARE

TOTAL_DEDUCTIONS = health + dental + vision + 401k

NET_PAY = GROSS_PAY − TOTAL_TAX − TOTAL_DEDUCTIONS
```

---

### 3.3 Leave Management — Level 2 DFD

#### 3.3.1 Leave Lifecycle

```
Phase 1: INITIALIZE         Phase 2: ACCRUE           Phase 3: REQUEST
───────────────────         ───────────────           ────────────────
(on hire)                   (monthly batch)           (employee action)
    │                           │                          │
    ▼                           ▼                          ▼
(P-03.1 Init Balances)     (P-03.2 Monthly Accrual)   (P-03.3 Submit Request)
    │                           │                          │
    ▼                           ▼                          ▼
D-10 LEAVE_BALANCES         D-10 (ACCRUED+)            D-11 LEAVE_REQUESTS
(OPENING, ACCRUED,                                     STATUS=PENDING
 USED, AVAILABLE)
                                Phase 4: APPROVE         Phase 5: CONSUME
                                ─────────────────        ────────────────
                                (manager action)          (leave taken)
                                    │                         │
                                    ▼                         ▼
                               (P-03.4 Approve)          (P-03.5 Consume)
                                    │                         │
                                    ▼                         ▼
                               D-11 STATUS=APPROVED      D-10 USED += days
                                                         D-11 STATUS=TAKEN
```

#### 3.3.2 P-03.1 Initialize Balances — Detailed Flow

```
(P-03.1 PKG_LEAVE.initialize_balances — called at hire)
    │
    ├──read leave types────────────────────► D-12 LEAVE_TYPES (read)
    │   WHERE ACTIVE_FLAG='Y'
    │
    └──FOR EACH leave type:
        ├──compute OPENING_BALANCE
        │   (pro-rated from ANNUAL_DAYS based on hire_date vs. calendar year)
        ├──INSERT leave balance row────────► D-10 LEAVE_BALANCES (write)
        │   (EMP_ID, LEAVE_TYPE_ID, CALENDAR_YEAR, OPENING, ACCRUED=0,
        │    USED=0, PENDING=0, AVAILABLE=OPENING)
        └──log info─────────────────────── ► D-19 AUDIT_LOG
```

#### 3.3.3 P-03.2 Monthly Accrual — Detailed Flow

```
(P-03.2 PKG_LEAVE.run_monthly_accrual — scheduled job)
    │
    ├──read all active employees───────────► D-01 EMPLOYEES (read)
    │   WHERE EMPLOYMENT_STATUS='ACTIVE'
    │
    ├──read accrual rates──────────────────► D-12 LEAVE_TYPES (read)
    │
    └──FOR EACH employee × leave type:
        ├──compute v_accrued = ANNUAL_DAYS / 12
        ├──UPDATE LEAVE_BALANCES SET ACCRUED = ACCRUED + v_accrued
        │   ⚠ DEFECT: retry branch uses SET ACCRUED = v_accrued (not += )
        │   (BR-LIB-05 — silent overwrite if concurrent retry fires on existing row)
        ├──UPDATE AVAILABLE = OPENING + ACCRUED - USED - PENDING
        └──log──────────────────────────────► D-19 AUDIT_LOG
```

#### 3.3.4 P-03.3 Submit Leave Request — Detailed Flow

```
[EMPLOYEE] ──(emp_id, leave_type_id, start_date, end_date, reason)──►

(P-03.3 PKG_LEAVE.submit_leave_request)
    │
    ├──read current balance────────────────► D-10 LEAVE_BALANCES (read)
    │
    ├──check AVAILABLE >= requested_days
    │   RAISE -20301 if insufficient
    │
    ├──check REQUIRES_DOCUMENT────────────► D-12 LEAVE_TYPES (read)
    │   ⚠ FMLA REQUIRES_DOCUMENT='N' (seed data defect TD-71)
    │
    ├──INSERT leave request────────────────► D-11 LEAVE_REQUESTS (write)
    │   STATUS='PENDING'
    │
    ├──UPDATE LEAVE_BALANCES.PENDING += days► D-10 LEAVE_BALANCES (write)
    │
    └──queue notification─────────────────► D-21 NOTIFICATION_QUEUE (write)
        → manager receives pending request email
```

---

### 3.4 Performance Management — Level 2 DFD

#### 3.4.1 Review Lifecycle

```
STATUS FLOW:
NOT_STARTED → SELF_REVIEW → MANAGER_REVIEW → COMPLETED → ACKNOWLEDGED
                                                ↑
                             ⚠ CALIBRATION phase missing here
                             CALIBRATED_RATING column exists but is never written
```

#### 3.4.2 Process Flows

```
[HR_ADMIN] ──(cycle_id, cycle_name, start_date, end_date)──►

(P-04.1 PKG_PERFORMANCE.create_review_cycle)
    │
    ├──INSERT review cycle──────────────────► D-14 REVIEW_CYCLES (write)
    │
    └──FOR EACH active employee in scope:
        ├──INSERT performance review────────► D-13 PERFORMANCE_REVIEWS (write)
        │   STATUS='NOT_STARTED'
        │   OVERALL_RATING = NULL
        │   CALIBRATED_RATING = NULL ⚠ (never populated)
        └──queue notification~~~~~~~~~~~~~~~~► D-21 NOTIFICATION_QUEUE
```

```
[EMPLOYEE] ──(review_id, self_assessment_text)──►

(P-04.2 PKG_PERFORMANCE.submit_self_assessment)
    │
    ├──read review────────────────────────────► D-13 PERFORMANCE_REVIEWS (read)
    │   validate STATUS='NOT_STARTED'
    │
    ├──UPDATE SELF_ASSESSMENT────────────────► D-13 PERFORMANCE_REVIEWS (write)
    │   STATUS → 'SELF_REVIEW'
    │
    └──queue notification~~~~~~~~~~~~~~~~~~~~~► D-21 NOTIFICATION_QUEUE
        → manager notified of self-assessment completion
```

```
[MANAGER] ──(review_id, overall_rating, assessment, strengths, development_plan)──►

(P-04.3 PKG_PERFORMANCE.submit_manager_review)
    │
    ├──validate OVERALL_RATING BETWEEN 1.0 AND 5.0
    │   RAISE -20403 if out of range
    │
    ├──derive RATING_LABEL (transformation point):
    │   ≥4.5 → 'Exceptional'
    │   ≥3.5 → 'Exceeds Expectations'
    │   ≥2.5 → 'Meets Expectations'
    │   ≥1.5 → 'Needs Improvement'
    │   <1.5 → 'Unsatisfactory'
    │
    ├──UPDATE PERFORMANCE_REVIEWS────────────► D-13 (write)
    │   OVERALL_RATING, RATING_LABEL,
    │   MANAGER_ASSESSMENT, STRENGTHS,
    │   AREAS_FOR_IMPROVEMENT, DEVELOPMENT_PLAN
    │   STATUS → 'COMPLETED'
    │   ⚠ CALIBRATED_RATING never set here
    │
    └──queue notification~~~~~~~~~~~~~~~~~~~~~► D-21 NOTIFICATION_QUEUE
        → employee notified review is ready
```

```
⚠ MISSING FLOW — Calibration (dead code / dead column)
───────────────────────────────────────────────────────
[HR_ADMIN / SENIOR_LEADER] ──(calibrated_rating, calibration_notes)──►
(P-04.X MISSING: calibrate_review) ──would write──► D-13.CALIBRATED_RATING
                                    ──would write──► D-13.CALIBRATION_NOTES
                                    ──would set──── ► STATUS → 'CALIBRATED'

This process does not exist. The column exists in DDL but no procedure writes to it.
```

```
[EMPLOYEE] ──(review_id, employee_comments)──►

(P-04.4 PKG_PERFORMANCE.acknowledge_review)
    │
    ├──validate STATUS = 'COMPLETED'
    ├──UPDATE PERFORMANCE_REVIEWS────────────► D-13 (write)
    │   EMPLOYEE_COMMENTS, EMPLOYEE_ACK_DATE
    │   STATUS → 'ACKNOWLEDGED'
    └──queue notification~~~~~~~~~~~~~~~~~~~~~► D-21 NOTIFICATION_QUEUE
```

#### 3.4.3 Performance → Payroll Cross-Context Flow

```
D-13 PERFORMANCE_REVIEWS
    │
    │   (read by PKG_PAYROLL.calculate_employee_pay)
    ▼
OVERALL_RATING value
    │
    ├── IF OVERALL_RATING >= 3.0 → merit_eligible = TRUE
    │       → included in payroll merit-increase logic
    │
    └── IF OVERALL_RATING < 3.0 OR NULL → merit_eligible = FALSE
        ⚠ CALIBRATED_RATING is never substituted here
        ⚠ get_rating_distribution report also reads OVERALL_RATING, not CALIBRATED_RATING
```

---

### 3.5 Security and Audit — Level 2 DFD

#### 3.5.1 Authentication Flow

```
[USER] ──(p_username = email, p_password)──►

(P-05.1 PKG_SECURITY.authenticate)
    │
    ├──SELECT EMP_ID FROM EMPLOYEES WHERE EMAIL = p_username
    │   ✦ PII — email used as identity key
    │   ⚠ IF duplicate EMAIL: MIN(EMP_ID) silently selected (BR-043b)
    │   RAISE -20301 if not found
    │
    ├──check EMPLOYMENT_STATUS = 'ACTIVE'────► D-01 EMPLOYEES (read)
    │   RAISE -20302 if not active
    │
    ├──read USER_CREDENTIALS─────────────────► D-18 USER_CREDENTIALS (read)
    │   ⚠ PASSWORD HASH IS NEVER COMPARED (BR-042 — CRITICAL)
    │   Any valid username is authenticated regardless of password
    │
    ├──generate session_id (SYS_GUID)
    ├──INSERT session row─────────────────── ► D-17 USER_SESSIONS (write)
    │   STATUS='ACTIVE', LOGIN_TIME=SYSDATE
    │
    ├──read GRADE from EMPLOYEES─────────────► D-01 EMPLOYEES (read)
    │   Grade ≥ 8 → full access
    │   Grade 5–7 → view-all access
    │   Grade < 5 → own-data-only
    │
    └──log audit────────────────────────────► D-19 AUDIT_LOG (write)
```

#### 3.5.2 Session Validation Flow

```
(P-05.2 PKG_SECURITY.is_session_valid — called on every secured operation)
    │
    ├──SELECT session FROM D-17 USER_SESSIONS WHERE SESSION_ID = p_session_id
    │
    ├──check STATUS = 'ACTIVE'
    │   RETURN FALSE if expired/invalid (⚠ does NOT raise e_session_expired — BR-045)
    │
    ├──check LOGIN_TIME + INTERVAL '30' MINUTE >= SYSDATE
    │   ⚠ Hard-coded 30 min — SYSTEM_PARAMETERS.SESSION_TIMEOUT_MINUTES ignored (DQ-027)
    │   RETURN FALSE if timed out
    │
    ├──check EMPLOYMENT_STATUS = 'ACTIVE' (re-check on each call)────► D-01
    │
    └──RETURN TRUE / FALSE
```

#### 3.5.3 Permission Check Flow

```
(P-05.3 PKG_SECURITY.has_permission)
    │
    ├──validate session (calls P-05.2)
    │
    ├──read GRADE from EMPLOYEES──────────── ► D-01 EMPLOYEES (read)
    │
    ├──Grade-based RBAC (no role table — inline logic):
    │   IF GRADE >= 8 → RETURN TRUE (all operations)
    │   IF GRADE BETWEEN 5 AND 7 → view-all granted, admin denied
    │   IF GRADE < 5 → own data only
    │
    └──write permission check to audit───────► D-19 AUDIT_LOG (write)
```

#### 3.5.4 Encryption Data Flows

```
(P-05.4 PKG_SECURITY.encrypt_value)
    │
    ├──INPUT: plaintext value (SSN, bank account number)  ✦ PII
    ├──KEY: hard-coded 'HR$ystem_3ncrypt10n_K3y_2024!!'  ⚠ CRITICAL (TD-01)
    │   stored in package body source, visible to anyone with DDL access
    ├──ALGORITHM: AES-256-CBC-PKCS5 via DBMS_CRYPTO
    └──OUTPUT: encrypted ciphertext → caller stores in ENC column  ✧ ENC

(P-05.5 PKG_SECURITY.decrypt_value)
    │
    ├──INPUT: ciphertext from ENC column  ✧ ENC
    ├──KEY: same hard-coded key
    └──OUTPUT: plaintext  ✦ PII
        ⚠ No decrypt procedure confirmed for EMPLOYEE_DEPENDENTS.SSN_ENCRYPTED
        ⚠ No decrypt procedure confirmed for EMPLOYEE_BANK_ACCOUNTS.ACCOUNT_NUMBER_ENC
```

#### 3.5.5 Audit Log Flow

```
(P-09 PKG_COMMON — called by all packages)
    │
    ├──log_error(p_module, p_action, p_error_msg)
    │   INSERT INTO D-19 AUDIT_LOG (TABLE_NAME='ERROR_LOG', ...)
    │
    ├──log_info(p_module, p_action, p_message)
    │   INSERT INTO D-19 AUDIT_LOG (TABLE_NAME='INFO_LOG', ...)
    │
    └──log_action(p_table_name, p_row_id, p_action, p_user)
        INSERT INTO D-19 AUDIT_LOG (DML audit event)

⚠ All log types share one table — no structured format, no JSON, no severity levels
⚠ No correlation ID — cannot trace one business transaction across multiple log lines
⚠ DBMS_OUTPUT also used as debug fallback — invisible in production
```

---

## 4. Data Store Catalogue

Full inventory of all data stores, their producer processes, and consumer processes.

| Store | Table / File | Producer Processes | Consumer Processes | PII | Notes |
|-------|-------------|-------------------|-------------------|-----|-------|
| D-01 | EMPLOYEES | P-01.1, P-01.2, P-01.3, P-01.4 | P-02, P-03, P-04, P-05, P-06, P-08 | Yes — SSN✧, name, address, DOB | Core aggregate root |
| D-02 | DEPARTMENTS | HR Admin setup | P-01, P-02, P-06, P-08 | No | |
| D-03 | JOB_POSITIONS | HR Admin setup | P-01 | No | |
| D-04 | SALARY_RECORDS | P-01.1, P-01.2 | P-02.2, P-08 | No | Current = MAX(EFFECTIVE_DATE) WHERE END_DATE IS NULL |
| D-05 | PAYROLL_RUNS | P-02.1 | P-02.2, P-02.3, P-06.1, P-08 | No | Status: DRAFT→CALCULATED→APPROVED→GL_GENERATED→COMPLETED |
| D-06 | PAYROLL_DETAILS | P-02.2 | P-06.1, P-08 | No | One row per employee per run |
| D-07 | DEDUCTION_RECORDS | HR Admin / benefits events | P-02.2 | No | ELEMENT_ID magic numbers: 100=health, 101=dental, 102=vision, 103=401k ⚠ |
| D-08 | PAY_ELEMENTS | Reference data setup | P-02.2 | No | |
| D-09 | TAX_BRACKETS | Reference data setup | P-02.2 | No | Federal progressive brackets; state flat rates |
| D-10 | LEAVE_BALANCES | P-03.1, P-03.2, P-03.5 | P-03.3, P-03.4, P-08 | No | Per employee per leave type per year |
| D-11 | LEAVE_REQUESTS | P-03.3 | P-03.4, P-03.5, P-08 | No | Status: PENDING→APPROVED→REJECTED→TAKEN→CANCELLED |
| D-12 | LEAVE_TYPES | Reference data setup | P-03.1, P-03.2, P-03.3 | No | REQUIRES_DOCUMENT; FMLA seed defect ⚠ |
| D-13 | PERFORMANCE_REVIEWS | P-04.1, P-04.2, P-04.3, P-04.4 | P-02.2, P-08 | No | CALIBRATED_RATING dead column ⚠ |
| D-14 | REVIEW_CYCLES | P-04.1 | P-04.1, P-08 | No | |
| D-15 | PERFORMANCE_GOALS | P-04 goal procedures | P-04, P-08 | No | |
| D-16 | GOAL_REVIEWS | P-04 review procedures | P-08 | No | |
| D-17 | USER_SESSIONS | P-05.1 | P-05.2 | No — but links to PII via EMP_ID | STATUS=ACTIVE/EXPIRED; timeout=30 min hard-coded ⚠ |
| D-18 | USER_CREDENTIALS | (change_password only) | P-05.1 ⚠ (NEVER READ for auth) | Yes — PASSWORD_HASH (MD5) ✦ | Auth stub: password never verified ⚠ |
| D-19 | AUDIT_LOG | P-09 (all packages) | P-08 audit queries, security review | Partial — EMP_ID, action context | Single table for all log types ⚠ |
| D-20 | SYSTEM_PARAMETERS | Admin setup | All packages (many ignored ⚠) | No | SESSION_TIMEOUT_MINUTES ignored; AES key hard-coded instead ⚠ |
| D-21 | NOTIFICATION_QUEUE | P-07 (all packages via enqueue) | P-07 dispatcher | Yes — RECIPIENT_ID, body may contain name ✦ | Inline body construction; no TEMPLATE_ID ⚠ |
| D-22 | NOTIFICATION_TEMPLATES | Reference data setup | P-07 | No | |
| D-23 | EMPLOYEE_DEPENDENTS | HR Admin / portal | P-06 (export only) | Yes — name, DOB, SSN✧, relationship ✦ | BENEFITS_ENROLLED never read in export ⚠; SSN decrypt path unknown ⚠ |
| D-24 | EMPLOYEE_BANK_ACCOUNTS | Portal / HR Admin | **NEVER READ** ⚠ | Yes — ACCOUNT_NUMBER✧, ROUTING plain-text ✦ | Direct deposit entirely unimplemented ⚠ |
| D-25 | BENEFIT_PLANS | Reference data setup | P-06 | No | |
| D-26 | BENEFIT_ENROLLMENTS | HR Admin / benefits events | P-06 | No | |
| D-27 | EMPLOYEE_HISTORY | TRG_EMPLOYEES_AUDIT, P-01.4 | P-08, audit | Yes — same columns as EMPLOYEES ✦ | Immutable audit trail of EMPLOYEES changes |
| D-28 | LOOKUP_VALUES | Reference data setup | All packages | No | |
| D-29 | TERMINATION_CODES | Reference data setup | P-01.4 | No | |
| D-30 | TIME_ATTENDANCE_RECORDS | P-06 import stub | Nothing ⚠ | No | Inferred destination; DDL not confirmed; import never commits ⚠ |
| D-F1 | BENEFITS_FEED file | P-06.2 | EE-05 ADP | Yes ✦ | 203-char fixed-width; written to BENEFITS_FEED_OUT Oracle dir |
| D-F2 | GL_JOURNAL file | P-06.1 | EE-06 Oracle Financials | No | Pipe-delimited; no Journal Source/Category validation ⚠ |
| D-F3 | NACHA ACH file | NOT WRITTEN ⚠ | EE-08 NACHA | Yes ✦ | Prenote unimplemented; disbursement unimplemented |
| D-F4 | TIME CSV file | EE-09 Time Clock | P-06 import stub | No | Read via UTL_FILE; stub does nothing after parse ⚠ |

---

## 5. External Data Flows

### 5.1 ADP Benefits Feed (Outbound)

```
Trigger: PKG_INTEGRATION.export_benefits_feed (scheduled or manual)

Data Sources:
  D-01 EMPLOYEES (active employees, demographic columns)  ✦ PII
  D-23 EMPLOYEE_DEPENDENTS (active dependents)            ✦ PII
  D-26 BENEFIT_ENROLLMENTS (enrollment status)

Transformation:
  JOIN employees + dependents (LEFT JOIN — employees with no dependents included)
  Filter: EMPLOYMENT_STATUS='ACTIVE' AND d.ACTIVE_FLAG='Y'
  Format: fixed-width 203-char per record
  Field layout:
    Pos  1–20:  EMPLOYEE_NUMBER                   (padded with RPAD)
    Pos 21–70:  FIRST_NAME + LAST_NAME             ✦ PII
    Pos 71–80:  DATE_OF_BIRTH (YYYY-MM-DD)         ✦ PII
    Pos 81–81:  GENDER (M/F/O)                     ✦ PII
    Pos 82–111: DEP_FIRST_NAME                     ✦ PII
    Pos 112–141: DEP_LAST_NAME                     ✦ PII
    Pos 142–161: RELATIONSHIP
    Pos 162–171: DEP_DOB                           ✦ PII

Output: BENEFITS_FEED_OUT Oracle directory
        BENEFITS_YYYYMMDD.txt  →  [ADP_BENEFITS]

Known gaps:
  ⚠ BENEFITS_ENROLLED column not read — all active dependents exported regardless of enrollment
  ⚠ No file version header; no record count trailer; no checksum (TD-73)
  ⚠ Dependent SSN not exported — ADP may require SSN for coverage verification
  ⚠ RPAD silently truncates if field width misconfigured
```

### 5.2 Oracle Financials GL Feed (Outbound)

```
Trigger: PKG_INTEGRATION.generate_gl_journal (after payroll APPROVED)

Data Sources:
  D-05 PAYROLL_RUNS (run header, run_id, pay period dates)
  D-06 PAYROLL_DETAILS (per-employee gross, net, taxes, deductions)
  D-01 EMPLOYEES (DEPARTMENT_ID for cost centre routing)  ✦ PII (indirect)
  D-02 DEPARTMENTS (COST_CENTER, DEPARTMENT_CODE)

Transformation:
  For each department: SUM(gross), SUM(net), SUM(deductions)
  Produce pipe-delimited journal entry:
    H|journal_date|HRMS_PAYROLL|run_name
    D|cost_center|gl_account_code|amount|description
  GL account codes: 5100 (salary expense), 2100 (tax payable), 2200 (deduction payable)
  ⚠ GL account scheme undocumented; no reference table; developer can assign wrong codes

Output: GL_FEED_OUT Oracle directory
        GL_JOURNAL_YYYYMMDD.dat  →  [ORACLE_FINANCIALS]

Known gaps:
  ⚠ No Journal Source / Journal Category fields (required by Oracle Financials — TD-79)
  ⚠ No GL_FEED_SENT_DATE on PAYROLL_RUNS — no audit trail of successful submission (TD-80)
  ⚠ No acknowledgement file expected back from Oracle Financials
  ⚠ Missed/rejected feeds are undetectable from HRMS side
```

### 5.3 SMTP Email Notifications (Outbound)

```
Trigger: PKG_NOTIFICATION.send_notification (called by all packages via queue)

Data Flow:
  D-21 NOTIFICATION_QUEUE  (dequeued by dispatcher)
  D-22 NOTIFICATION_TEMPLATES  (template text; merged with runtime values inline)
  D-01 EMPLOYEES  (recipient email lookup)  ✦ PII

Transformation:
  Inline string concatenation for email body (no TEMPLATE_ID join at send time)
  UTL_MAIL or UTL_SMTP → [SMTP_SERVER]

Notification Events:
  Event                          Recipient(s)       Trigger Package
  ──────────────────────────────────────────────────────────────────
  Hire confirmation              Employee, HR Mgr   PKG_EMPLOYEE
  Termination notification       Employee, HR Mgr   PKG_EMPLOYEE
  Leave request submitted        Manager            PKG_LEAVE
  Leave request approved/denied  Employee           PKG_LEAVE
  Payslip available              Employee           PKG_PAYROLL
  Review cycle opened            Employee           PKG_PERFORMANCE
  Self-assessment submitted      Manager            PKG_PERFORMANCE
  Manager review complete        Employee           PKG_PERFORMANCE

Known gaps:
  ⚠ Delivery status not confirmed — no bounce handling
  ⚠ SMS channel referenced (PHONE column) but handler not implemented
  ⚠ e_account_locked and e_session_expired exceptions declared but never raised (BR-045)
```

### 5.4 NACHA ACH Direct Deposit (Gap — Not Implemented)

```
Intended flow (design intent, not implemented):

  D-24 EMPLOYEE_BANK_ACCOUNTS  ──► (disbursement procedure — DOES NOT EXIST ⚠)
      ├── ROUTING_NUMBER (plain text)       ✦ PII
      ├── ACCOUNT_NUMBER_ENC (encrypted)   ✦ PII ✧ ENC
      ├── DEPOSIT_TYPE (FULL/PARTIAL_AMOUNT/PARTIAL_PERCENT/REMAINDER)
      ├── DEPOSIT_AMOUNT / DEPOSIT_PERCENTAGE
      └── PRIORITY_ORDER

  Expected NACHA file fields (never generated):
    File Header Record (1-record)
    Company Batch Header (5-record)
    Entry Detail (6-record): routing, account, amount, employee name
    Prenote Entry (⚠ PRENOTE_SENT/PRENOTE_DATE columns exist but never set)
    Batch Control (8-record)
    File Control (9-record)

Current state:
  PAYROLL_RUNS reaches STATUS='COMPLETED' with TOTAL_NET calculated
  but no disbursement ever occurs.
  STATUS='PAID' is referenced in discrepancy log (DISC-009) as orphaned state.
  No NACHA file is ever written.
  ACH prenote compliance gap (BR-BA-05, PP-BA-03).

⚠ CRITICAL — Direct deposit is entirely non-functional despite full schema design.
```

### 5.5 Time/Attendance Import (Stub — Not Implemented)

```
Trigger: PKG_INTEGRATION.import_time_attendance

Data Source:
  D-F4 TIME_ATTENDANCE CSV  (UTL_FILE.FOPEN from TIME_IMPORT_DIR Oracle dir)
  Format: emp_number,date,hours_regular,hours_overtime (inferred from comment)
  Skip rules: lines starting with '#'; empty lines

Current stub body:
  1. Opens file
  2. Reads lines, skips '#' and blank lines
  3. Parses CSV — no INSERT to any table
  4. On parse error: continues to next line (no rollback, no transaction)
  5. Calls PKG_COMMON.log_info('Time attendance import completed')
  6. Returns

⚠ No INSERT to TIME_ATTENDANCE_RECORDS or PAYROLL_DETAILS ever occurs
⚠ No link to payroll calculation — hours-worked never reaches P-02.2
⚠ False success audit log on every execution (DQ-031)
⚠ No COMMIT / ROLLBACK — no transaction boundary
```

---

## 6. Data Transformation Points

Catalogue of all locations where data is calculated, derived, or converted.

| ID | Transformation | Location | Input | Output | Notes |
|----|---------------|----------|-------|--------|-------|
| TX-01 | Gross pay calculation | PKG_PAYROLL.calculate_employee_pay | BASE_SALARY, SALARY_TYPE | GROSS_PAY | MONTHLY: /12; HOURLY: unimplemented ⚠; CONTRACT: unimplemented ⚠ |
| TX-02 | Federal income tax (progressive) | PKG_PAYROLL.calculate_employee_pay | GROSS, TAX_FILING_STATUS, TAX_BRACKETS | FEDERAL_TAX | HOH returns $0 — defect ⚠ |
| TX-03 | State income tax (flat rate) | PKG_PAYROLL.calculate_employee_pay | GROSS, STATE | STATE_TAX | Flat rate per state; lookup from EMPLOYEES.STATE |
| TX-04 | FICA Social Security | PKG_PAYROLL.calculate_employee_pay | GROSS, FICA_WAGE_BASE constant | FICA_SS | 6.2% capped at wage base |
| TX-05 | FICA Medicare | PKG_PAYROLL.calculate_employee_pay | GROSS | FICA_MEDICARE | 1.45% uncapped |
| TX-06 | Net pay derivation | PKG_PAYROLL.calculate_employee_pay | GROSS, TOTAL_TAX, TOTAL_DEDUCTIONS | NET_PAY | NET = GROSS − TAX − DEDUCTIONS |
| TX-07 | Rating label derivation | PKG_PERFORMANCE.submit_manager_review | OVERALL_RATING (1.0–5.0) | RATING_LABEL | 5-bucket breakpoints: 4.5/3.5/2.5/1.5 |
| TX-08 | Leave accrual | PKG_LEAVE.run_monthly_accrual | ANNUAL_DAYS, LEAVE_TYPE | ACCRUED += ANNUAL_DAYS/12 | Defect: retry branch uses = not += ⚠ |
| TX-09 | Leave available balance | PKG_LEAVE | OPENING + ACCRUED − USED − PENDING | AVAILABLE | Recalculated on each request/approval |
| TX-10 | Pro-rated opening leave balance | PKG_LEAVE.initialize_balances | HIRE_DATE, ANNUAL_DAYS, calendar year | OPENING_BALANCE | Pro-rated from hire date to year-end |
| TX-11 | SSN encryption | PKG_SECURITY.encrypt_value | SSN plaintext ✦ PII | AES-256 ciphertext ✧ ENC | Key hard-coded in package body ⚠ |
| TX-12 | Password hash | PKG_SECURITY.hash_password | p_password | MD5 hash via DBMS_CRYPTO ⚠ | MD5 is critically weak (DQ-010) |
| TX-13 | Session token generation | PKG_SECURITY.authenticate | — | SYS_GUID() session_id | Used as bearer token in Forms |
| TX-14 | ADP fixed-width record assembly | PKG_INTEGRATION.export_benefits_feed | Employee + dependent columns | 203-char string | RPAD to exact width; no LENGTHB validation ⚠ |
| TX-15 | GL journal aggregation | PKG_INTEGRATION.generate_gl_journal | Per-employee pay details | Department-level SUM by GL account | Magic GL codes: 5100/2100/2200 ⚠ |
| TX-16 | Compa-ratio | PKG_REPORTING.compensation_summary | SALARY, grade midpoint | COMPA_RATIO = AVG(salary/midpoint)×100 | Uses Oracle MEDIAN() — no PostgreSQL equivalent ⚠ |
| TX-17 | Turnover percentage | PKG_REPORTING.turnover_report | terminations, hires up to end date | TURNOVER_PCT = terminations/hires×100 | Non-standard denominator vs. SHRM definition ⚠ |
| TX-18 | Leave utilisation percentage | PKG_REPORTING.leave_utilization_report | USED, OPENING+ACCRUED | UTILIZATION_PCT = AVG(USED)/AVG(balance)×100 | CALENDAR_YEAR missing from projection ⚠ |
| TX-19 | Rating distribution | PKG_REPORTING.get_rating_distribution | OVERALL_RATING, RATING_LABEL | COUNT, PERCENTAGE per label | Reads OVERALL_RATING not CALIBRATED_RATING ⚠ |
| TX-20 | Org hierarchy traversal | PKG_EMPLOYEE / DEPARTMENTS | PARENT_DEPARTMENT_ID (self-ref) | Org tree via CONNECT BY | Performance degrades >500 employees ⚠ |

---

## 7. PII Data Flow Map

Mapping of all Personally Identifiable Information flows for GDPR / privacy compliance.

### 7.1 PII Inventory

| PII Field | Table | Classification | Encrypted at Rest | Decryption Path Confirmed | Flows To |
|-----------|-------|---------------|-------------------|--------------------------|----------|
| FIRST_NAME | EMPLOYEES | Personal | No | N/A | All processes; ADP feed |
| LAST_NAME | EMPLOYEES | Personal | No | N/A | All processes; ADP feed |
| MIDDLE_NAME | EMPLOYEES | Personal | No | N/A | HR forms |
| DATE_OF_BIRTH | EMPLOYEES | Sensitive | No | N/A | Benefits feed; HR forms |
| SSN | EMPLOYEES | Highly Sensitive | Yes (AES-256) ✧ | Yes — PKG_SECURITY.decrypt_value | Benefits feed (decrypted); tax reporting |
| EMAIL | EMPLOYEES | Personal | No | N/A | Authentication; notifications; HR forms |
| PHONE | EMPLOYEES | Personal | No | N/A | HR forms; SMS (unimplemented) |
| ADDRESS_LINE1/2 | EMPLOYEES | Personal | No | N/A | HR forms; not in feeds |
| CITY, STATE, ZIP_CODE | EMPLOYEES | Personal | No | N/A | Tax calculation (STATE); HR forms |
| BANK_ACCOUNT_NUMBER | EMPLOYEES | Financial | Yes (AES-256) ✧ | **Not confirmed** ⚠ | Not currently used |
| BANK_ROUTING_NUMBER | EMPLOYEES | Financial | Yes (AES-256) ✧ | **Not confirmed** ⚠ | Not currently used |
| EMERGENCY_CONTACT_NAME | EMPLOYEES | Personal (3rd party) | No | N/A | HR forms only |
| EMERGENCY_CONTACT_PHONE | EMPLOYEES | Personal (3rd party) | No | N/A | HR forms only |
| MARITAL_STATUS | EMPLOYEES | Sensitive | No | N/A | Payroll tax calculation |
| TAX_FILING_STATUS | EMPLOYEES | Sensitive | No | N/A | Payroll tax calculation |
| GENDER | EMPLOYEES | Sensitive | No | N/A | ADP feed; EEO report |
| DEPENDENT.FIRST_NAME | EMPLOYEE_DEPENDENTS | Personal | No | N/A | ADP benefits feed |
| DEPENDENT.LAST_NAME | EMPLOYEE_DEPENDENTS | Personal | No | N/A | ADP benefits feed |
| DEPENDENT.DATE_OF_BIRTH | EMPLOYEE_DEPENDENTS | Sensitive | No | N/A | ADP benefits feed |
| DEPENDENT.RELATIONSHIP | EMPLOYEE_DEPENDENTS | Sensitive | No | N/A | ADP benefits feed |
| DEPENDENT.SSN_ENCRYPTED | EMPLOYEE_DEPENDENTS | Highly Sensitive | Yes (AES-256) ✧ | **Not confirmed** ⚠ | Not exported in any confirmed flow |
| ROUTING_NUMBER | EMPLOYEE_BANK_ACCOUNTS | Financial | No (plain text) ⚠ | N/A | Not used |
| ACCOUNT_NUMBER_ENC | EMPLOYEE_BANK_ACCOUNTS | Financial | Yes (AES-256) ✧ | **Not confirmed** ⚠ | Not used |
| PASSWORD_HASH | USER_CREDENTIALS | Security Credential | No (MD5 — weak) ⚠ | N/A | Auth stub; hash exposed if schema breach |
| SELF_ASSESSMENT | PERFORMANCE_REVIEWS | Sensitive | No | N/A | HR forms; manager review |
| MANAGER_ASSESSMENT | PERFORMANCE_REVIEWS | Sensitive | No | N/A | Employee acknowledgement; reports |
| EMPLOYEE_COMMENTS | PERFORMANCE_REVIEWS | Sensitive | No | N/A | HR forms |
| NAME + SALARY (co-located) | RPT_NEW_HIRES (inferred) | Financial + Personal | No | N/A | Reports; direct SELECT unguarded ⚠ |

### 7.2 PII Flow Diagram

```
                    ┌─── D-01 EMPLOYEES (PII anchor) ───┐
                    │   SSN✧, name, DOB, address, email │
                    │   bank_acct✧, tax_status, gender  │
                    └─────────────────┬─────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────────┐
          │                           │                               │
          ▼                           ▼                               ▼
  (PKG_PAYROLL)              (PKG_INTEGRATION)              (PKG_NOTIFICATION)
  reads: STATE ✦              reads: name, DOB               reads: EMAIL ✦
  reads: TAX_FILING ✦         reads: GENDER ✦                sends: name in body ✦
  reads: GRADE                reads: SSN (decrypt) ✦ ✧
                                   │
                                   ├──► D-F1 ADP FEED ──► [ADP_BENEFITS]
                                   │    name, DOB, gender ✦
                                   │    dependent name, DOB ✦
                                   │    (SSN NOT included in feed)
                                   │
                                   └──► D-F2 GL FEED ──► [ORACLE_FINANCIALS]
                                        No PII (aggregated dept totals only)

D-23 EMPLOYEE_DEPENDENTS
    name, DOB, relationship ✦ ──► ADP feed
    SSN_ENCRYPTED ✦ ✧ ──────────► NOT EXPORTED (decryption path unconfirmed ⚠)

D-24 EMPLOYEE_BANK_ACCOUNTS
    ACCOUNT_NUMBER_ENC ✦ ✧ ──────► NEVER READ ⚠
    ROUTING_NUMBER ✦ (plain) ──────► NEVER READ ⚠

D-18 USER_CREDENTIALS
    PASSWORD_HASH (MD5) ✦ ─────────► AUTH STUB (hash never checked ⚠)
    if schema breach: hash visible to attacker

D-27 EMPLOYEE_HISTORY
    All EMPLOYEES columns including PII ✦ ──► HR Admin queries only
    Audit trigger writes on every EMPLOYEES DML
```

### 7.3 PII Risk Summary

| Risk | Severity | Detail |
|------|----------|--------|
| Hard-coded AES-256 key | Critical | Anyone with DDL access to PKG_SECURITY can decrypt all SSNs and bank numbers |
| MD5 password hashing | Critical | Passwords are trivially reversible from hash; rainbow table attacks feasible |
| Auth stub — password never checked | Critical | Any username is valid regardless of password; credential theft irrelevant |
| Routing number in plain text | High | EMPLOYEE_BANK_ACCOUNTS.ROUTING_NUMBER unencrypted; full ACH credentials exposed if table accessed |
| Dependent SSN — no decrypt path | High | Data may be irrecoverable on system migration |
| Bank account decryption path unconfirmed | High | Same migration risk |
| RPT_NEW_HIRES — salary + name co-located, unguarded at table level | Medium | Direct SELECT grants not visible; financial PII accessible if table-level grants over-provisioned |
| Email used as auth identity — TOO_MANY_ROWS silently picks MIN(EMP_ID) | High | Duplicate email causes silent identity collision |
| In-flight session survives termination for up to 30 min | Medium | Terminated employee retains access within active session window |
| No stale session cleanup job | Medium | USER_SESSIONS rows accumulate; orphaned ACTIVE rows if Forms closed without logout |

---

## 8. Summary: Data Flow Gap Register

Critical unimplemented or defective data flows identified across all analysis tracks.

| Gap ID | Area | Description | Severity | Business Impact |
|--------|------|-------------|----------|----------------|
| DFG-01 | Payroll Disbursement | EMPLOYEE_BANK_ACCOUNTS never read; NACHA file never generated | Critical | Direct deposit non-functional; manual off-system disbursement required |
| DFG-02 | Authentication | PKG_SECURITY.authenticate never verifies password against USER_CREDENTIALS | Critical | Any valid username authenticates; zero credential security |
| DFG-03 | Termination | COBRA notification not implemented; calculate_final_pay does not exist | Critical | Federal compliance violation on every termination |
| DFG-04 | Time Import | import_time_attendance reads CSV but inserts nothing; logs false success | High | Hours worked never reaches payroll; hourly employees cannot be processed |
| DFG-05 | Performance Calibration | CALIBRATED_RATING dead column; no calibration workflow exists | High | Official ratings are uncalibrated raw manager scores; distribution report misleading |
| DFG-06 | GL Feed Audit | No GL_FEED_SENT_DATE on PAYROLL_RUNS; missed feeds undetectable | High | Payroll amounts may not reach Oracle Financials; no recovery mechanism |
| DFG-07 | Org Sync | sync_org_structure is a stub; logs false success on every call | High | LDAP/AD never synchronised; false audit trail |
| DFG-08 | ACH Prenote | PRENOTE_SENT/PRENOTE_DATE columns exist but never populated | High | Nacha compliance gap for all new bank accounts |
| DFG-09 | Dependent SSN | SSN_ENCRYPTED on EMPLOYEE_DEPENDENTS; no decryption procedure confirmed | High | Data potentially irrecoverable on migration |
| DFG-10 | Session Cleanup | No DBMS_SCHEDULER job to expire stale USER_SESSIONS | Medium | Orphaned ACTIVE sessions accumulate; security hygiene gap |
| DFG-11 | ADP Feed Enrollment | BENEFITS_ENROLLED not filtered in export_benefits_feed | Medium | ADP receives unenrolled dependents; plan administration errors |
| DFG-12 | HOH Tax | HEAD_OF_HOUSEHOLD tax filing status returns $0 federal tax | High | Employees with HOH status pay no federal tax; under-withholding liability |
| DFG-13 | Leave Accrual Retry | run_monthly_accrual retry branch uses = not += for ACCRUED | High | Concurrent retry silently overwrites accrued balance to monthly increment only |
| DFG-14 | FMLA Document Flag | FMLA leave type seeded with REQUIRES_DOCUMENT='N' | Medium | FMLA requests accepted with no supporting documentation |

---

*End of document — 09_DATA_FLOW_DIAGRAM.md*
*Generated from: BA_Deep_Analyst, DA_Data_Reviewer, TA_Deep_Analyst, AA_Quality_Review analysis tracks*
*Oracle HRMS v4.2.0 — Acme Corporation*
