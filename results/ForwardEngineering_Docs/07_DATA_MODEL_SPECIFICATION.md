# 07 — Data Model Specification
**System:** Acme Corporation HRMS (Oracle 19c → Target Migration)
**Document Version:** 1.0
**Analysis Basis:** BA_Deep_Analyst (BR-01–BR-140), DA_Data_Extractor, DA_Data_Reviewer (DQ-001–DQ-032), AA_Quality_Review, TA_Deep_Analyst
**Scope:** 30 confirmed DDL tables, 6 views, 7 inferred RPT_* tables, 3 additional inferred tables (TIME_ATTENDANCE_RECORDS, USER_CREDENTIALS, EMPLOYEE_PAY_ELEMENTS)

---

## Table of Contents

1. [Conceptual Data Model](#1-conceptual-data-model)
2. [Logical Data Model — All 30 Tables](#2-logical-data-model)
3. [Data Model Decisions](#3-data-model-decisions)
4. [Migration Mapping — Oracle → Target](#4-migration-mapping)
5. [Data Quality Issues](#5-data-quality-issues)
6. [Recommended Schema Improvements](#6-recommended-schema-improvements)
7. [Data Lifecycle Management](#7-data-lifecycle-management)

---

## 1. Conceptual Data Model

### 1.1 Major Entities

The Acme HRMS conceptual model organises around **eight business entity clusters**. Each cluster maps to one or more bounded contexts identified in the domain model.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ACME HRMS — CONCEPTUAL MODEL                         │
│                                                                             │
│  ┌───────────┐    employs    ┌──────────────┐   belongs to  ┌────────────┐  │
│  │ORGANISATION│◄────────────►│   EMPLOYEE   │◄─────────────►│DEPARTMENT  │  │
│  │  (root)   │               │  (aggregate  │               │            │  │
│  └───────────┘               │   root)      │               └────────────┘  │
│                              └──────┬───────┘                               │
│                    ┌───────────────┬┴──────────────────────┐                │
│                    │               │                        │                │
│            ┌───────▼───┐   ┌──────▼──────┐       ┌────────▼──────┐         │
│            │COMPENSATION│   │    LEAVE    │       │  PERFORMANCE  │         │
│            │  (salary,  │   │ (balance,   │       │  (review,     │         │
│            │  payroll)  │   │  request)   │       │   goal)       │         │
│            └───────┬───┘   └─────────────┘       └───────────────┘         │
│                    │                                                         │
│            ┌───────▼───────────────────────────────┐                        │
│            │           INTEGRATION LAYER            │                        │
│            │  (benefits feed, GL journal, ACH file) │                        │
│            └───────────────────────────────────────┘                        │
│                                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐  ┌───────────────┐  │
│  │  SECURITY & │   │   BENEFITS   │   │  DEPENDENTS  │  │ NOTIFICATION  │  │
│  │   ACCESS    │   │  ENROLLMENT  │   │              │  │    QUEUE      │  │
│  └─────────────┘   └──────────────┘   └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Entity Relationship Summary

| Entity | Cardinality | Related To | Relationship |
|--------|-------------|------------|--------------|
| EMPLOYEE | 1 | DEPARTMENT | Many-to-one (assigned to one department) |
| EMPLOYEE | 1..* | SALARY_RECORD | One-to-many (salary history, append-only) |
| EMPLOYEE | 1..* | PAYROLL_DETAIL | One-to-many (one row per pay period) |
| EMPLOYEE | 0..* | LEAVE_BALANCE | One-to-many (one per leave type) |
| EMPLOYEE | 0..* | LEAVE_REQUEST | One-to-many (submitted requests) |
| EMPLOYEE | 0..* | PERFORMANCE_REVIEW | One-to-many (reviews across cycles) |
| EMPLOYEE | 0..* | PERFORMANCE_GOAL | One-to-many (goals per cycle) |
| EMPLOYEE | 0..* | EMPLOYEE_DEPENDENT | One-to-many (family members) |
| EMPLOYEE | 0..* | EMPLOYEE_BANK_ACCOUNT | One-to-many (split-deposit accounts) |
| EMPLOYEE | 0..* | BENEFIT_ENROLLMENT | One-to-many (plan enrollments) |
| PAYROLL_RUN | 1..* | PAYROLL_DETAIL | One-to-many (all employee lines per run) |
| REVIEW_CYCLE | 1..* | PERFORMANCE_REVIEW | One-to-many (all reviews in a cycle) |
| DEPARTMENT | 0..1 | DEPARTMENT (self) | Self-referencing hierarchy (PARENT_DEPARTMENT_ID) |
| EMPLOYEE | 0..1 | EMPLOYEE (self) | Self-referencing manager hierarchy (MANAGER_ID) |
| LEAVE_TYPE | 1..* | LEAVE_BALANCE | One-to-many (one balance per type per employee) |
| LEAVE_TYPE | 1..* | LEAVE_REQUEST | One-to-many (requests reference leave type) |
| BENEFIT_PLAN | 1..* | BENEFIT_ENROLLMENT | One-to-many (enrollments per plan) |

### 1.3 Core Business Rules — Conceptual Level

| Rule ID | Statement |
|---------|-----------|
| CBR-01 | Every Employee must belong to exactly one Department at all times. |
| CBR-02 | An Employee's salary history is append-only; no record is ever deleted. |
| CBR-03 | Leave balances are maintained per employee per leave type; accrual is time-based. |
| CBR-04 | A Performance Review cycle is a container; reviews exist within cycles. |
| CBR-05 | Benefits enrollment is optional; employees may have zero or many enrollments. |
| CBR-06 | Dependents are associated with an employee and may be enrolled in benefits independently. |
| CBR-07 | Payroll is processed in batch runs; a run spans a defined pay period. |
| CBR-08 | All deletions are logical (soft-delete via ACTIVE_FLAG); physical deletion is prohibited. |
| CBR-09 | Access to employee data is controlled by the accessing user's Grade (1–10). |
| CBR-10 | All PII fields (SSN, bank account) are encrypted at rest; plaintext is never persisted. |

---

## 2. Logical Data Model

### 2.1 Core HR Tables

---

#### Table: EMPLOYEES

**Purpose:** Master employee record. Aggregate root for the entire system.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| EMP_ID | NUMBER(10) | NO | SQ_EMPLOYEE_ID.NEXTVAL | PK | — | No |
| EMPLOYEE_NUMBER | VARCHAR2(20) | NO | — | UK | — | No |
| FIRST_NAME | VARCHAR2(50) | NO | — | — | — | Yes |
| LAST_NAME | VARCHAR2(50) | NO | — | — | — | Yes |
| MIDDLE_NAME | VARCHAR2(50) | YES | — | — | — | Yes |
| DATE_OF_BIRTH | DATE | YES | — | — | — | Yes |
| SSN_ENCRYPTED | VARCHAR2(500) | YES | — | — | AES-256-CBC | Yes/ENC |
| EMAIL | VARCHAR2(100) | YES | — | UK | — | Yes |
| PHONE | VARCHAR2(20) | YES | — | — | — | Yes |
| ADDRESS_LINE1 | VARCHAR2(200) | YES | — | — | — | Yes |
| ADDRESS_LINE2 | VARCHAR2(200) | YES | — | — | — | Yes |
| CITY | VARCHAR2(100) | YES | — | — | — | Yes |
| STATE | VARCHAR2(2) | YES | — | — | — | Yes |
| ZIP_CODE | VARCHAR2(10) | YES | — | — | — | Yes |
| HIRE_DATE | DATE | NO | — | — | — | No |
| TERMINATION_DATE | DATE | YES | — | — | — | No |
| EMPLOYMENT_STATUS | VARCHAR2(20) | NO | 'ACTIVE' | — | CHK IN ('ACTIVE','TERMINATED','ON_LEAVE','SUSPENDED') | No |
| JOB_TITLE | VARCHAR2(100) | YES | — | — | — | No |
| DEPARTMENT_ID | NUMBER(10) | YES | — | FK→DEPARTMENTS | — | No |
| MANAGER_ID | NUMBER(10) | YES | — | FK→EMPLOYEES | Self-referencing | No |
| GRADE | NUMBER(2) | NO | — | — | CHK BETWEEN 1 AND 10 | No |
| BANK_ACCOUNT_NUMBER | VARCHAR2(500) | YES | — | — | AES-256 (denorm, gap) | Yes/ENC |
| BANK_ROUTING_NUMBER | VARCHAR2(500) | YES | — | — | AES-256 (denorm, gap) | Yes/ENC |
| MARITAL_STATUS | VARCHAR2(20) | YES | — | — | — | No |
| TAX_FILING_STATUS | VARCHAR2(30) | YES | — | — | CHK IN ('SINGLE','MARRIED_FILING_JOINTLY','MARRIED_FILING_SEPARATELY','HEAD_OF_HOUSEHOLD') | No |
| EMERGENCY_CONTACT_NAME | VARCHAR2(100) | YES | — | — | — | Yes |
| EMERGENCY_CONTACT_PHONE | VARCHAR2(20) | YES | — | — | — | Yes |
| TERMINATION_REASON | VARCHAR2(10) | YES | — | FK→TERMINATION_CODES | — | No |
| ACTIVE_FLAG | VARCHAR2(1) | NO | 'Y' | — | CHK IN ('Y','N') | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |
| UPDATED_DATE | DATE | YES | — | — | Set by trigger | No |
| UPDATED_BY | VARCHAR2(50) | YES | — | — | Set by trigger | No |

**Embedded Business Rules:**
- BR-01: EMPLOYMENT_STATUS controls eligibility for all downstream processes.
- BR-02: Three-part active filter = `EMPLOYMENT_STATUS = 'ACTIVE' AND ACTIVE_FLAG = 'Y' AND TERMINATION_DATE IS NULL`.
- BR-03: GRADE ≥ 8 grants full access; Grade 5–7 grants view-all; Grade < 5 restricts to own record.
- **DEFECT (DQ-003):** BANK_ACCOUNT_NUMBER and BANK_ROUTING_NUMBER on EMPLOYEES table are denormalised duplicates of EMPLOYEE_BANK_ACCOUNTS. No decrypt procedure exists in any package.

---

#### Table: DEPARTMENTS

**Purpose:** Organisational unit registry. Supports recursive hierarchy via self-referencing FK.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| DEPARTMENT_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| DEPARTMENT_NAME | VARCHAR2(100) | NO | — | UK | — | No |
| DEPARTMENT_CODE | VARCHAR2(20) | YES | — | UK | — | No |
| PARENT_DEPARTMENT_ID | NUMBER(10) | YES | — | FK→DEPARTMENTS | Self-ref | No |
| MANAGER_ID | NUMBER(10) | YES | — | FK→EMPLOYEES | — | No |
| COST_CENTER | VARCHAR2(20) | YES | — | — | — | No |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | CHK('Y','N') | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |

**Embedded Business Rules:**
- Hierarchy uses CONNECT BY; degrades beyond 500 employees (BR-TA-22).
- COST_CENTER feeds Oracle Financials GL journal routing.

---

#### Table: JOB_POSITIONS

**Purpose:** Job catalogue defining grade bands and canonical titles.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| POSITION_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| POSITION_TITLE | VARCHAR2(100) | NO | — | — | — | No |
| POSITION_CODE | VARCHAR2(20) | YES | — | UK | — | No |
| MIN_GRADE | NUMBER(2) | NO | — | — | CHK BETWEEN 1 AND 10 | No |
| MAX_GRADE | NUMBER(2) | NO | — | — | CHK BETWEEN 1 AND 10; MAX >= MIN | No |
| DEPARTMENT_ID | NUMBER(10) | YES | — | FK→DEPARTMENTS | — | No |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | CHK('Y','N') | No |

---

#### Table: EMPLOYEE_HISTORY

**Purpose:** Immutable audit trail of all changes to EMPLOYEES rows. Written by audit trigger.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| HISTORY_ID | NUMBER(10) | NO | Sequence | PK | — |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — |
| FIELD_NAME | VARCHAR2(50) | NO | — | — | Column that changed |
| OLD_VALUE | VARCHAR2(4000) | YES | — | — | Pre-change value (text cast) |
| NEW_VALUE | VARCHAR2(4000) | YES | — | — | Post-change value |
| CHANGED_BY | VARCHAR2(50) | NO | — | — | Oracle session user |
| CHANGED_DATE | DATE | NO | SYSDATE | — | — |
| ACTION_TYPE | VARCHAR2(10) | NO | — | — | INSERT / UPDATE / DELETE |

---

### 2.2 Compensation Tables

---

#### Table: SALARY_RECORDS

**Purpose:** Append-only salary history. Current salary = MAX(EFFECTIVE_DATE) where END_DATE IS NULL.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| SALARY_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| BASE_SALARY | NUMBER(12,2) | NO | — | — | CHK > 0 | No |
| EFFECTIVE_DATE | DATE | NO | — | — | — | No |
| END_DATE | DATE | YES | — | — | NULL = current | No |
| SALARY_TYPE | VARCHAR2(20) | YES | 'MONTHLY' | — | CHK IN ('MONTHLY','HOURLY','CONTRACT') | No |
| CHANGE_REASON | VARCHAR2(200) | YES | — | — | — | No |
| APPROVED_BY | NUMBER(10) | YES | — | FK→EMPLOYEES | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |

**Embedded Business Rules:**
- Current record identified by END_DATE IS NULL (only one should exist per employee — no DDL enforcement).
- BASE_SALARY / 12 = monthly gross used in payroll calculation.
- COMPA_RATIO = (BASE_SALARY / grade_midpoint) × 100 — computed at reporting time by PKG_REPORTING.

---

#### Table: PAYROLL_RUNS

**Purpose:** Pay run header. One row per payroll execution cycle.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| RUN_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| RUN_NAME | VARCHAR2(100) | NO | — | — | — | No |
| PAY_PERIOD_START | DATE | NO | — | — | — | No |
| PAY_PERIOD_END | DATE | NO | — | — | — | No |
| RUN_DATE | DATE | NO | — | — | — | No |
| STATUS | VARCHAR2(20) | NO | 'DRAFT' | — | CHK IN ('DRAFT','CALCULATED','APPROVED','GL_GENERATED','COMPLETED') | No |
| TOTAL_GROSS | NUMBER(15,2) | YES | — | — | — | No |
| TOTAL_NET | NUMBER(15,2) | YES | — | — | — | No |
| TOTAL_DEDUCTIONS | NUMBER(15,2) | YES | — | — | — | No |
| CALCULATED_DATE | DATE | YES | — | — | — | No |
| APPROVED_BY | NUMBER(10) | YES | — | FK→EMPLOYEES | — | No |
| APPROVED_DATE | DATE | YES | — | — | — | No |

**Embedded Business Rules:**
- Status lifecycle is linear: DRAFT → CALCULATED → APPROVED → GL_GENERATED → COMPLETED.
- No reverse transition is implemented in code (no un-approve capability).
- PAID status referenced in DISC-009 but no disbursement procedure exists (EMPLOYEE_BANK_ACCOUNTS never read).
- **Missing columns (data quality):** GL_FEED_SENT_DATE, GL_FEED_FILE_NAME not present; feed delivery untrackable (TD-80).

---

#### Table: PAYROLL_DETAILS

**Purpose:** Line-level employee payroll data per run. One row per employee per run.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| DETAIL_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| RUN_ID | NUMBER(10) | NO | — | FK→PAYROLL_RUNS | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| GROSS_PAY | NUMBER(12,2) | YES | — | — | — | No |
| NET_PAY | NUMBER(12,2) | YES | — | — | — | No |
| FEDERAL_TAX | NUMBER(10,2) | YES | — | — | — | No |
| STATE_TAX | NUMBER(10,2) | YES | — | — | — | No |
| SOCIAL_SECURITY | NUMBER(10,2) | YES | — | — | — | No |
| MEDICARE | NUMBER(10,2) | YES | — | — | — | No |
| TOTAL_DEDUCTIONS | NUMBER(10,2) | YES | — | — | — | No |
| STATUS | VARCHAR2(20) | YES | — | — | CHK IN ('CALCULATED','ERROR','APPROVED') | No |
| ERROR_MESSAGE | VARCHAR2(500) | YES | — | — | — | No |
| ELEMENT_ID | NUMBER(5) | YES | — | — | Magic numbers: 100=base,101=OT,102=bonus,103=deduction | No |

**Embedded Business Rules:**
- HEAD_OF_HOUSEHOLD TAX_FILING_STATUS returns $0 federal tax — defect in calculate_employee_pay (BR-108).
- Flat-rate state tax driven by EMPLOYEES.STATE field value; no bracket table for state.
- ELEMENT_ID magic numbers 100/101/102/103 are undocumented in schema; PKG_REPORTING.payroll_summary_report hard-codes them (TD-57 analogue).

---

#### Table: DEDUCTION_RECORDS

**Purpose:** Individual deduction line items for an employee per pay period.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| DEDUCTION_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| RUN_ID | NUMBER(10) | NO | — | FK→PAYROLL_RUNS | — | No |
| DEDUCTION_TYPE | VARCHAR2(50) | NO | — | — | — | No |
| AMOUNT | NUMBER(10,2) | NO | — | — | CHK > 0 | No |
| EFFECTIVE_DATE | DATE | NO | — | — | — | No |
| END_DATE | DATE | YES | — | — | NULL = ongoing | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |

---

#### Table: EMPLOYEE_BANK_ACCOUNTS

**Purpose:** Direct deposit account registry. Supports split-deposit across multiple accounts.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| BANK_ACCT_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| BANK_NAME | VARCHAR2(100) | YES | — | — | — | No |
| ROUTING_NUMBER | VARCHAR2(20) | NO | — | — | **PLAINTEXT** — security gap | Yes |
| ACCOUNT_NUMBER_ENC | VARCHAR2(200) | NO | — | — | AES-256; no decrypt procedure found | Yes/ENC |
| ACCOUNT_TYPE | VARCHAR2(20) | YES | 'CHECKING' | — | CHK IN ('CHECKING','SAVINGS') | No |
| DEPOSIT_TYPE | VARCHAR2(20) | YES | 'FULL' | — | CHK IN ('FULL','PARTIAL_AMOUNT','PARTIAL_PERCENT','REMAINDER') | No |
| DEPOSIT_AMOUNT | NUMBER(12,2) | YES | — | — | No cross-column validation to DEPOSIT_TYPE | No |
| DEPOSIT_PERCENTAGE | NUMBER(5,2) | YES | — | — | No range constraint (can exceed 100%) | No |
| PRIORITY_ORDER | NUMBER(2) | YES | 1 | — | — | No |
| PRENOTE_SENT | CHAR(1) | YES | 'N' | — | Never written by any package | No |
| PRENOTE_DATE | DATE | YES | — | — | Never written by any package | No |
| ACTIVE_FLAG | CHAR(1) | NO | 'Y' | — | CHK('Y','N') | No |
| CREATED_BY | VARCHAR2(30) | NO | — | — | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |
| MODIFIED_BY | VARCHAR2(30) | YES | — | — | — | No |
| MODIFIED_DATE | DATE | YES | — | — | — | No |

**Critical Finding:** This table is never referenced by any PL/SQL package, trigger, or view. Direct deposit is non-functional (BR-BA-12, PP-BA-01 Critical).

---

### 2.3 Leave Management Tables

---

#### Table: LEAVE_TYPES

**Purpose:** Reference table defining all leave categories and their rules.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| LEAVE_TYPE_ID | NUMBER(5) | NO | Sequence | PK | — | No |
| LEAVE_TYPE_CODE | VARCHAR2(20) | NO | — | UK | — | No |
| LEAVE_TYPE_NAME | VARCHAR2(100) | NO | — | — | — | No |
| ACCRUAL_RATE | NUMBER(5,2) | YES | — | — | Days per month | No |
| MAX_BALANCE | NUMBER(5,1) | YES | — | — | Cap on carried balance | No |
| REQUIRES_DOCUMENT | VARCHAR2(1) | YES | 'N' | — | CHK('Y','N') — FMLA seeded as 'N': TD-71 | No |
| PAID_LEAVE | VARCHAR2(1) | YES | 'Y' | — | CHK('Y','N') | No |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | CHK('Y','N') | No |

---

#### Table: LEAVE_BALANCES

**Purpose:** Per-employee, per-leave-type balance ledger.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| BALANCE_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| LEAVE_TYPE_ID | NUMBER(5) | NO | — | FK→LEAVE_TYPES | — | No |
| CALENDAR_YEAR | NUMBER(4) | NO | — | — | — | No |
| OPENING_BALANCE | NUMBER(5,1) | YES | 0 | — | — | No |
| ACCRUED | NUMBER(5,1) | YES | 0 | — | Defect: retry overwrites, not increments (BR-LIB-05) | No |
| TAKEN | NUMBER(5,1) | YES | 0 | — | — | No |
| AVAILABLE | NUMBER(5,1) | YES | — | — | VIR: OPENING_BALANCE + ACCRUED - TAKEN | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |
| MODIFIED_DATE | DATE | YES | — | — | — | No |

**Embedded Business Rules:**
- AVAILABLE is a computed virtual column; formula inconsistency vs. PKG_LEAVE calculation is documented as DISC-002.
- ACCRUAL retry bug: the `SQL%ROWCOUNT = 0` branch assigns `SET ACCRUED = v_accrued` instead of `SET ACCRUED = ACCRUED + v_accrued` (BR-LIB-05).

---

#### Table: LEAVE_REQUESTS

**Purpose:** Individual leave request submissions and their approval workflow state.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| REQUEST_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| LEAVE_TYPE_ID | NUMBER(5) | NO | — | FK→LEAVE_TYPES | — | No |
| START_DATE | DATE | NO | — | — | — | No |
| END_DATE | DATE | NO | — | — | CHK END_DATE >= START_DATE | No |
| DAYS_REQUESTED | NUMBER(4,1) | NO | — | — | — | No |
| STATUS | VARCHAR2(20) | NO | 'PENDING' | — | CHK IN ('PENDING','APPROVED','REJECTED','CANCELLED') | No |
| REASON | VARCHAR2(500) | YES | — | — | — | No |
| SUPPORTING_DOC_PATH | VARCHAR2(500) | YES | — | — | Path traversal risk: TD-47 | No |
| APPROVED_BY | NUMBER(10) | YES | — | FK→EMPLOYEES | — | No |
| APPROVED_DATE | DATE | YES | — | — | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |
| MODIFIED_DATE | DATE | YES | — | — | — | No |

---

### 2.4 Performance Management Tables

---

#### Table: REVIEW_CYCLES

**Purpose:** Container defining a performance review period (typically annual or semi-annual).

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| CYCLE_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| CYCLE_NAME | VARCHAR2(100) | NO | — | UK | — | No |
| CYCLE_YEAR | NUMBER(4) | NO | — | — | — | No |
| START_DATE | DATE | NO | — | — | — | No |
| END_DATE | DATE | NO | — | — | CHK END_DATE > START_DATE | No |
| STATUS | VARCHAR2(20) | NO | 'PLANNING' | — | CHK IN ('PLANNING','ACTIVE','CALIBRATION','CLOSED') | No |
| CREATED_BY | VARCHAR2(30) | NO | — | — | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |

---

#### Table: PERFORMANCE_REVIEWS

**Purpose:** Individual employee review records within a cycle. Multi-stage workflow document.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| REVIEW_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| CYCLE_ID | NUMBER(10) | NO | — | FK→REVIEW_CYCLES | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| REVIEWER_EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| REVIEW_TYPE | VARCHAR2(20) | NO | — | — | CHK IN ('ANNUAL','MID_YEAR','PROBATION') | No |
| SELF_ASSESSMENT | CLOB | YES | — | — | — | No |
| OVERALL_RATING | NUMBER(3,1) | YES | — | — | CHK BETWEEN 1.0 AND 5.0 | No |
| RATING_LABEL | VARCHAR2(30) | YES | — | — | Derived from OVERALL_RATING; set inline | No |
| CALIBRATED_RATING | NUMBER(3,1) | YES | — | — | **Dead column — never written by any procedure** | No |
| CALIBRATION_NOTES | VARCHAR2(2000) | YES | — | — | **Dead column — never written** | No |
| MANAGER_ASSESSMENT | CLOB | YES | — | — | — | No |
| STRENGTHS | VARCHAR2(2000) | YES | — | — | — | No |
| AREAS_FOR_IMPROVEMENT | VARCHAR2(2000) | YES | — | — | — | No |
| DEVELOPMENT_PLAN | VARCHAR2(2000) | YES | — | — | — | No |
| EMPLOYEE_COMMENTS | VARCHAR2(2000) | YES | — | — | — | No |
| EMPLOYEE_ACK_DATE | DATE | YES | — | — | — | No |
| STATUS | VARCHAR2(20) | NO | 'NOT_STARTED' | — | CHK IN ('NOT_STARTED','SELF_REVIEW','MANAGER_REVIEW','COMPLETED','ACKNOWLEDGED') | No |
| CREATED_BY | VARCHAR2(30) | NO | — | — | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |
| MODIFIED_BY | VARCHAR2(30) | YES | — | — | — | No |
| MODIFIED_DATE | DATE | YES | — | — | — | No |

**Critical Gap:** `CALIBRATED_RATING` and `CALIBRATION_NOTES` are schema columns with no corresponding write path in PKG_PERFORMANCE. The reporting procedure `get_rating_distribution` reads `OVERALL_RATING` (raw manager rating), not `CALIBRATED_RATING`. If calibration is used, distribution reports are pre-calibration data.

---

#### Table: PERFORMANCE_GOALS

**Purpose:** Individual goals set per employee per cycle. Linked to review for scoring.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| GOAL_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| CYCLE_ID | NUMBER(10) | NO | — | FK→REVIEW_CYCLES | — | No |
| GOAL_TITLE | VARCHAR2(200) | NO | — | — | — | No |
| GOAL_DESCRIPTION | CLOB | YES | — | — | — | No |
| WEIGHT | NUMBER(5,2) | YES | — | — | Intended 0–100; no CHK constraint | No |
| TARGET_DATE | DATE | YES | — | — | — | No |
| STATUS | VARCHAR2(20) | YES | 'ACTIVE' | — | — | No |
| COMPLETION_SCORE | NUMBER(3,1) | YES | — | — | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |

---

#### Table: GOAL_REVIEWS

**Purpose:** Manager scoring of individual goals at review time.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| GOAL_REVIEW_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| GOAL_ID | NUMBER(10) | NO | — | FK→PERFORMANCE_GOALS | — | No |
| REVIEW_ID | NUMBER(10) | NO | — | FK→PERFORMANCE_REVIEWS | — | No |
| SCORE | NUMBER(3,1) | YES | — | — | — | No |
| COMMENTS | VARCHAR2(2000) | YES | — | — | — | No |
| REVIEWED_DATE | DATE | YES | — | — | — | No |

---

### 2.5 Benefits Tables

---

#### Table: BENEFIT_PLANS

**Purpose:** Master catalogue of available benefit plans.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| PLAN_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| PLAN_NAME | VARCHAR2(100) | NO | — | UK | — | No |
| PLAN_TYPE | VARCHAR2(50) | NO | — | — | CHK IN ('MEDICAL','DENTAL','VISION','LIFE','401K') | No |
| CARRIER | VARCHAR2(100) | YES | — | — | — | No |
| EMPLOYEE_COST | NUMBER(8,2) | YES | — | — | — | No |
| EMPLOYER_COST | NUMBER(8,2) | YES | — | — | — | No |
| EFFECTIVE_DATE | DATE | NO | — | — | — | No |
| END_DATE | DATE | YES | — | — | NULL = current | No |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | CHK('Y','N') | No |

---

#### Table: BENEFIT_ENROLLMENTS

**Purpose:** Employee-plan enrollment records with coverage dates.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| ENROLLMENT_ID | NUMBER(10) | NO | Sequence | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| PLAN_ID | NUMBER(10) | NO | — | FK→BENEFIT_PLANS | — | No |
| COVERAGE_TIER | VARCHAR2(20) | NO | — | — | CHK IN ('EMPLOYEE_ONLY','EMPLOYEE_SPOUSE','EMPLOYEE_CHILD','FAMILY') | No |
| EFFECTIVE_DATE | DATE | NO | — | — | — | No |
| END_DATE | DATE | YES | — | — | NULL = active | No |
| ENROLLED_BY | VARCHAR2(30) | YES | — | — | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |

---

#### Table: EMPLOYEE_DEPENDENTS

**Purpose:** Dependent registry for benefits eligibility and ADP benefits feed.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| DEPENDENT_ID | NUMBER(10) | NO | Sequence | PK PK_EMP_DEPENDENTS | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES FK_DEP_EMP | — | No |
| FIRST_NAME | VARCHAR2(50) | NO | — | — | — | Yes |
| LAST_NAME | VARCHAR2(50) | NO | — | — | — | Yes |
| RELATIONSHIP | VARCHAR2(20) | NO | — | — | CHK_RELATIONSHIP IN ('SPOUSE','CHILD','PARENT','DOMESTIC_PARTNER','OTHER') | No |
| DATE_OF_BIRTH | DATE | YES | — | — | — | Yes |
| SSN_ENCRYPTED | VARCHAR2(200) | YES | — | — | AES-256; no decrypt procedure for dependents | Yes/ENC |
| BENEFITS_ENROLLED | CHAR(1) | NO | 'N' | — | CHK('Y','N') — never read by export_benefits_feed | No |
| ACTIVE_FLAG | CHAR(1) | NO | 'Y' | — | CHK('Y','N') | No |
| CREATED_BY | VARCHAR2(30) | NO | — | — | — | No |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |
| MODIFIED_BY | VARCHAR2(30) | YES | — | — | — | No |
| MODIFIED_DATE | DATE | YES | — | — | — | No |

**Known Gaps:** No unique constraint on (EMP_ID, RELATIONSHIP) — multiple SPOUSE rows are schema-valid. BENEFITS_ENROLLED flag is never filtered in the ADP export. Termination procedure does not touch dependent records (BR-DEP-09).

---

### 2.6 Security and Access Tables

---

#### Table: USER_SESSIONS

**Purpose:** Active session registry. Authentication token management.

| Column | Data Type | Nullable | Default | PK/FK/UK | Constraint | PII |
|--------|-----------|----------|---------|----------|------------|-----|
| SESSION_ID | VARCHAR2(100) | NO | — | PK | — | No |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — | No |
| LOGIN_TIME | DATE | NO | SYSDATE | — | — | No |
| LAST_ACTIVITY | DATE | YES | — | — | — | No |
| STATUS | VARCHAR2(20) | NO | 'ACTIVE' | — | CHK IN ('ACTIVE','EXPIRED','LOGGED_OUT') | No |
| IP_ADDRESS | VARCHAR2(50) | YES | — | — | — | Yes |
| CREATED_DATE | DATE | NO | SYSDATE | — | — | No |

**Business Rules:**
- Session timeout is hard-coded to 30 minutes — SYSTEM_PARAMETERS.SESSION_TIMEOUT_MINUTES is ignored (BR-026, DQ-027).
- Expired sessions are only detected on next call to `is_session_valid`; no background cleanup job exists (TD-75).
- `e_session_expired` exception declared in spec but never raised — returns FALSE instead (BR-045, DQ-030).

---

#### Table: USER_CREDENTIALS

**Purpose:** Password storage for employee authentication. (Inferred — DDL not recovered from source.)

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| EMP_ID | NUMBER(10) | NO | — | PK/FK→EMPLOYEES | — |
| PASSWORD_HASH | VARCHAR2(200) | NO | — | — | MD5 via DBMS_CRYPTO.HASH_MD5 — critically weak (DQ-010) |
| CREATED_DATE | DATE | NO | SYSDATE | — | — |
| MODIFIED_DATE | DATE | YES | — | — | — |

**Critical Findings:**
- `authenticate()` never queries this table — authentication is a stub (BR-042, DQ-003).
- `change_password` never verifies old password before replacement (BR-044, DQ-029).
- No LOGIN_ATTEMPTS, LOCKED_UNTIL, or PASSWORD_CHANGED_DATE columns exist — no lockout, no password aging.

---

#### Table: AUDIT_LOG

**Purpose:** Combined audit trail for all DML events, INFO logging, and ERROR logging. Single-table design mixes log types.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| LOG_ID | NUMBER(10) | NO | Sequence | PK | — |
| LOG_TYPE | VARCHAR2(20) | NO | — | — | CHK IN ('ERROR','INFO','AUDIT') |
| TABLE_NAME | VARCHAR2(50) | YES | — | — | — |
| RECORD_ID | NUMBER(10) | YES | — | — | — |
| ACTION | VARCHAR2(20) | YES | — | — | INSERT/UPDATE/DELETE |
| OLD_VALUES | CLOB | YES | — | — | — |
| NEW_VALUES | CLOB | YES | — | — | — |
| USER_NAME | VARCHAR2(50) | YES | — | — | — |
| LOG_DATE | DATE | NO | SYSDATE | — | — |
| MESSAGE | VARCHAR2(4000) | YES | — | — | Free-text; no JSON structure |
| SESSION_ID | VARCHAR2(100) | YES | — | — | — |

**Data Quality Issue (TD-37):** Single table mixed log types prevent independent retention policies per log class.

---

### 2.7 Reference / Lookup Tables

---

#### Table: LOOKUP_VALUES

**Purpose:** Generic key-value reference table. Drives drop-down validation across Forms screens.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| LOOKUP_ID | NUMBER(10) | NO | Sequence | PK | — |
| LOOKUP_TYPE | VARCHAR2(50) | NO | — | — | Category key |
| LOOKUP_CODE | VARCHAR2(30) | NO | — | UK(LOOKUP_TYPE,LOOKUP_CODE) | — |
| LOOKUP_VALUE | VARCHAR2(200) | NO | — | — | Display label |
| DISPLAY_ORDER | NUMBER(3) | YES | — | — | — |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | — |

---

#### Table: TERMINATION_CODES

**Purpose:** Controlled vocabulary for employee termination reasons.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| CODE | VARCHAR2(10) | NO | — | PK | — |
| DESCRIPTION | VARCHAR2(100) | NO | — | — | — |
| VOLUNTARY | VARCHAR2(1) | YES | — | — | Y/N |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | — |

---

#### Table: JOB_GRADES

**Purpose:** Compensation band definitions. Min/max salary per grade used for compa-ratio calculation.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| GRADE_ID | NUMBER(2) | NO | — | PK | Range 1–10 |
| GRADE_NAME | VARCHAR2(50) | NO | — | — | — |
| MIN_SALARY | NUMBER(12,2) | NO | — | — | — |
| MID_SALARY | NUMBER(12,2) | NO | — | — | Used in COMPA_RATIO formula |
| MAX_SALARY | NUMBER(12,2) | NO | — | — | — |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | — |

---

#### Table: JOB_TITLES

**Purpose:** Canonical title catalogue with EEO classification. Referenced by reporting.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| JOB_ID | NUMBER(10) | NO | Sequence | PK | — |
| JOB_CODE | VARCHAR2(20) | NO | — | UK | — |
| JOB_TITLE | VARCHAR2(100) | NO | — | — | — |
| GRADE_ID | NUMBER(2) | YES | — | FK→JOB_GRADES | — |
| EEO_CATEGORY | VARCHAR2(50) | YES | — | — | EEO-1 category string |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | — |

---

#### Table: LOCATIONS

**Purpose:** Physical office locations. Referenced in reporting and hire records.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| LOCATION_ID | NUMBER(10) | NO | Sequence | PK | — |
| LOCATION_NAME | VARCHAR2(100) | NO | — | — | — |
| ADDRESS | VARCHAR2(200) | YES | — | — | — |
| CITY | VARCHAR2(100) | YES | — | — | — |
| STATE | VARCHAR2(2) | YES | — | — | — |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | — |

---

#### Table: SYSTEM_PARAMETERS

**Purpose:** Key-value configuration store. Many values are overridden by hard-coded literals in application code.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| PARAM_GROUP | VARCHAR2(50) | NO | — | PK(GROUP,KEY) | — |
| PARAM_KEY | VARCHAR2(100) | NO | — | PK | — |
| PARAM_VALUE | VARCHAR2(500) | YES | — | — | — |
| DESCRIPTION | VARCHAR2(500) | YES | — | — | — |
| MODIFIED_DATE | DATE | YES | — | — | — |

**Known Issues:** SESSION_TIMEOUT_MINUTES ignored (hard-coded 30 min). APP_VERSION static row not auto-incremented. FTP_PASSWORD stored as plaintext in table (TD-10).

---

#### Table: NOTIFICATION_TEMPLATES

**Purpose:** Email/SMS notification templates. Body constructed inline by callers, not by template engine.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| TEMPLATE_ID | NUMBER(10) | NO | Sequence | PK | — |
| TEMPLATE_CODE | VARCHAR2(50) | NO | — | UK | — |
| SUBJECT | VARCHAR2(200) | YES | — | — | — |
| BODY_TEMPLATE | CLOB | YES | — | — | — |
| CHANNEL | VARCHAR2(20) | YES | — | — | CHK IN ('EMAIL','SMS','BOTH') |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | — |

---

#### Table: NOTIFICATION_QUEUE

**Purpose:** Asynchronous notification dispatch queue.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| NOTIFICATION_ID | NUMBER(10) | NO | Sequence | PK | — |
| EMP_ID | NUMBER(10) | NO | — | FK→EMPLOYEES | — |
| NOTIFICATION_TYPE | VARCHAR2(50) | NO | — | — | — |
| SUBJECT | VARCHAR2(200) | YES | — | — | — |
| BODY | CLOB | YES | — | — | Full body passed by caller — no TEMPLATE_ID column |
| CHANNEL | VARCHAR2(20) | YES | — | — | — |
| STATUS | VARCHAR2(20) | NO | 'PENDING' | — | CHK IN ('PENDING','SENT','FAILED','RETRY') |
| RETRY_COUNT | NUMBER(2) | YES | 0 | — | — |
| SCHEDULED_DATE | DATE | YES | — | — | — |
| SENT_DATE | DATE | YES | — | — | — |
| ERROR_MESSAGE | VARCHAR2(500) | YES | — | — | — |
| CREATED_DATE | DATE | NO | SYSDATE | — | — |

**Note:** No PAYLOAD column, no TEMPLATE_ID FK — the body is assembled by callers via string concatenation before INSERT.

---

### 2.8 Payroll Reference Tables

---

#### Table: TAX_BRACKETS

**Purpose:** Federal income tax progressive rate brackets.

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| BRACKET_ID | NUMBER(5) | NO | Sequence | PK | — |
| FILING_STATUS | VARCHAR2(30) | NO | — | — | Matches EMPLOYEES.TAX_FILING_STATUS |
| MIN_INCOME | NUMBER(12,2) | NO | — | — | — |
| MAX_INCOME | NUMBER(12,2) | YES | — | — | NULL = no ceiling (top bracket) |
| TAX_RATE | NUMBER(5,4) | NO | — | — | Fractional rate e.g. 0.2200 |
| BASE_TAX | NUMBER(12,2) | YES | 0 | — | — |
| EFFECTIVE_YEAR | NUMBER(4) | NO | — | — | — |

**Known Issue:** HOH (HEAD_OF_HOUSEHOLD) branches in PKG_PAYROLL return $0 — brackets may not have corresponding HOH rows (BR-108, DQ-019).

---

#### Table: PAY_ELEMENTS

**Purpose:** Pay component type registry (base salary, overtime, bonuses, deductions).

| Column | Data Type | Nullable | Default | PK/FK/UK | Notes |
|--------|-----------|----------|---------|----------|-------|
| ELEMENT_ID | NUMBER(5) | NO | — | PK | — |
| ELEMENT_CODE | VARCHAR2(30) | NO | — | UK | — |
| ELEMENT_NAME | VARCHAR2(100) | NO | — | — | — |
| ELEMENT_TYPE | VARCHAR2(20) | NO | — | — | CHK IN ('EARNINGS','DEDUCTION','TAX','BENEFIT') |
| GL_ACCOUNT_CODE | VARCHAR2(20) | YES | — | — | Numeric convention 5100/2100/2200 undocumented |
| ACTIVE_FLAG | VARCHAR2(1) | YES | 'Y' | — | — |

---

## 3. Data Model Decisions

| Decision ID | Decision | Rationale | Trade-offs |
|-------------|----------|-----------|-----------|
| DM-01 | Soft-delete via ACTIVE_FLAG across all tables | Preserves full historical audit trail; regulatory requirement for HR data | Queries require `ACTIVE_FLAG = 'Y'` filter everywhere; partial enforcement — some queries omit it |
| DM-02 | Append-only salary history (SALARY_RECORDS) | Enables point-in-time payroll recalculation and compliance audit | END_DATE IS NULL convention for "current" record has no DDL uniqueness enforcement |
| DM-03 | Grade-based RBAC embedded in EMPLOYEES.GRADE | Simple integer comparison; no separate role table to maintain | Grade changes require immediate security re-evaluation; shared kernel between BC-01 and BC-06 creates coupling |
| DM-04 | AES-256 encryption for SSN and bank account numbers at application layer | Satisfies PII protection requirements; encrypts at point-of-write | Hard-coded key `HR$ystem_3ncrypt10n_K3y_2024!!` invalidates all encryption benefit (DQ-001); no key rotation mechanism |
| DM-05 | Single AUDIT_LOG table for ERROR, INFO, and DML audit events | Simplicity of a single write target | Cannot apply independent retention policies per log class; mixed log types in same table (TD-37) |
| DM-06 | Self-referencing FK on DEPARTMENTS for hierarchy | Standard Oracle CONNECT BY query pattern | Performance degrades beyond 500 employees; no depth limit constraint |
| DM-07 | Self-referencing FK on EMPLOYEES.MANAGER_ID | Natural representation of reporting line | Circular reference is structurally possible (no acyclic constraint); CONNECT BY required for traversal |
| DM-08 | SYSTEM_PARAMETERS key-value store for configuration | Single location for operational parameters | Bypassed by hard-coded values throughout application code; not a reliable configuration source |
| DM-09 | No dedicated COBRA or SESSION_REVOCATION tables | Scope was not implemented | Critical compliance gap — every termination creates an unreported COBRA qualifying event (PP-TERM-01) |
| DM-10 | Fixed-width 203-character ADP benefits feed format | Matches ADP vendor specification at time of build | No version header, no trailer record count — field changes silently truncate data (TD-73) |
| DM-11 | NOTIFICATION_QUEUE without TEMPLATE_ID FK | Body assembled inline by callers | Template versioning impossible; schema-level decoupling between NOTIFICATION_TEMPLATES and queue rows |
| DM-12 | RPT_* reporting tables as denormalised snapshots | Standard OLAP layer design | Refresh procedure is a stub; all 7 report procedures query OLTP directly, defeating the purpose |

---

## 4. Migration Mapping — Oracle Column → Target System Column

The following mapping covers all 30 source tables. **Source** = Oracle 19c column. **Target** = recommended column name and type for a PostgreSQL 15 (or equivalent) target system.

### 4.1 EMPLOYEES Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| EMP_ID | NUMBER(10) | employee_id | BIGINT | SEQUENCE → BIGSERIAL or UUID |
| EMPLOYEE_NUMBER | VARCHAR2(20) | employee_number | VARCHAR(20) | No change |
| FIRST_NAME | VARCHAR2(50) | first_name | VARCHAR(50) | No change |
| LAST_NAME | VARCHAR2(50) | last_name | VARCHAR(50) | No change |
| SSN_ENCRYPTED | VARCHAR2(500) | ssn_encrypted | TEXT | Re-encrypt with new key before migration |
| EMAIL | VARCHAR2(100) | email | VARCHAR(100) | Deduplicate first — MIN(EMP_ID) collision bug (BR-043b) |
| HIRE_DATE | DATE | hire_date | DATE | No change |
| EMPLOYMENT_STATUS | VARCHAR2(20) | employment_status | employment_status_enum | Create enum type |
| DEPARTMENT_ID | NUMBER(10) | department_id | BIGINT | FK remapped |
| MANAGER_ID | NUMBER(10) | manager_id | BIGINT | Self-ref FK |
| GRADE | NUMBER(2) | grade | SMALLINT | Range validation: 1–10 |
| BANK_ACCOUNT_NUMBER | VARCHAR2(500) | — | REMOVED | Move to employee_bank_accounts; decrypt/re-encrypt |
| BANK_ROUTING_NUMBER | VARCHAR2(500) | — | REMOVED | Move to employee_bank_accounts |
| TAX_FILING_STATUS | VARCHAR2(30) | tax_filing_status | tax_filing_status_enum | Validate HOH $0 defect before migration |
| ACTIVE_FLAG | VARCHAR2(1) | is_active | BOOLEAN | 'Y'/'N' → TRUE/FALSE |
| CREATED_DATE | DATE | created_at | TIMESTAMPTZ | Add timezone |
| UPDATED_DATE | DATE | updated_at | TIMESTAMPTZ | Add timezone |
| UPDATED_BY | VARCHAR2(50) | updated_by | VARCHAR(50) | No change |

---

### 4.2 SALARY_RECORDS Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| SALARY_ID | NUMBER(10) | salary_id | BIGINT | — |
| EMP_ID | NUMBER(10) | employee_id | BIGINT | FK renamed |
| BASE_SALARY | NUMBER(12,2) | base_salary | NUMERIC(12,2) | No change |
| EFFECTIVE_DATE | DATE | effective_date | DATE | No change |
| END_DATE | DATE | end_date | DATE | Validate only one NULL per employee |
| SALARY_TYPE | VARCHAR2(20) | salary_type | salary_type_enum | Create enum |
| APPROVED_BY | NUMBER(10) | approved_by_id | BIGINT | FK to employees |

---

### 4.3 PAYROLL_RUNS Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| RUN_ID | NUMBER(10) | payroll_run_id | BIGINT | — |
| STATUS | VARCHAR2(20) | status | payroll_status_enum | Add GL_FEED_SENT state to enum |
| TOTAL_GROSS | NUMBER(15,2) | total_gross | NUMERIC(15,2) | No change |
| — | — | gl_feed_sent_at | TIMESTAMPTZ | New column — TD-80 remediation |
| — | — | gl_feed_file_name | VARCHAR(255) | New column — TD-80 remediation |

---

### 4.4 PAYROLL_DETAILS Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| ELEMENT_ID | NUMBER(5) | pay_element_id | BIGINT | Replace magic numbers 100/101/102/103 with FK to pay_elements |
| FEDERAL_TAX | NUMBER(10,2) | federal_income_tax | NUMERIC(10,2) | Rename for clarity |
| SOCIAL_SECURITY | NUMBER(10,2) | social_security_tax | NUMERIC(10,2) | Rename for clarity |
| MEDICARE | NUMBER(10,2) | medicare_tax | NUMERIC(10,2) | Rename for clarity |

---

### 4.5 EMPLOYEE_BANK_ACCOUNTS Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| BANK_ACCT_ID | NUMBER(10) | bank_account_id | BIGINT | — |
| ROUTING_NUMBER | VARCHAR2(20) | routing_number_enc | TEXT | **Encrypt before migration** — currently plaintext |
| ACCOUNT_NUMBER_ENC | VARCHAR2(200) | account_number_enc | TEXT | Re-encrypt with new key |
| DEPOSIT_TYPE | VARCHAR2(20) | deposit_type | deposit_type_enum | Create enum |
| PRENOTE_SENT | CHAR(1) | prenote_sent | BOOLEAN | 'Y'/'N' → TRUE/FALSE |
| PRENOTE_DATE | DATE | prenote_sent_at | TIMESTAMPTZ | Add timezone |

---

### 4.6 PERFORMANCE_REVIEWS Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| OVERALL_RATING | NUMBER(3,1) | overall_rating | NUMERIC(3,1) | Validate range 1.0–5.0 |
| CALIBRATED_RATING | NUMBER(3,1) | calibrated_rating | NUMERIC(3,1) | Migrate as nullable; implement write path before using |
| CALIBRATION_NOTES | VARCHAR2(2000) | calibration_notes | TEXT | Migrate as nullable |
| RATING_LABEL | VARCHAR2(30) | — | REMOVED (computed) | Generate at query time from OVERALL_RATING or CALIBRATED_RATING |
| STATUS | VARCHAR2(20) | status | review_status_enum | Add 'CALIBRATION' state to enum |
| SELF_ASSESSMENT | CLOB | self_assessment | TEXT | CLOB → TEXT |
| MANAGER_ASSESSMENT | CLOB | manager_assessment | TEXT | CLOB → TEXT |

---

### 4.7 LEAVE_BALANCES Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| AVAILABLE | NUMBER(5,1) | — | GENERATED ALWAYS AS (opening_balance + accrued - taken) | Replace virtual column with generated column; verify formula against PKG_LEAVE |
| ACCRUED | NUMBER(5,1) | accrued | NUMERIC(5,1) | Fix accrual retry defect (BR-LIB-05) before migrating accrual logic |

---

### 4.8 USER_SESSIONS Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| SESSION_ID | VARCHAR2(100) | session_id | UUID | Replace VARCHAR with UUID type |
| STATUS | VARCHAR2(20) | status | session_status_enum | Create enum |
| LOGIN_TIME | DATE | logged_in_at | TIMESTAMPTZ | Add timezone |

---

### 4.9 AUDIT_LOG Migration Mapping

| Oracle Column | Oracle Type | Target Column | Target Type | Transformation Notes |
|---------------|-------------|---------------|-------------|----------------------|
| LOG_TYPE | VARCHAR2(20) | — | Split into 3 tables | Separate: application_errors, audit_events, info_log — independent retention |
| OLD_VALUES | CLOB | old_values | JSONB | Structured JSON; enables indexing |
| NEW_VALUES | CLOB | new_values | JSONB | Structured JSON |
| MESSAGE | VARCHAR2(4000) | message | TEXT | No change |

---

## 5. Data Quality Issues

The following issues were identified across the BA, DA, and AA analysis tracks. Issues are ranked by severity.

### 5.1 Critical Issues

| DQ-ID | Table / Column | Issue | Impact | Root Cause |
|-------|---------------|-------|--------|------------|
| DQ-001 | SYSTEM_PARAMETERS / PKG_SECURITY | Hard-coded AES-256 key `HR$ystem_3ncrypt10n_K3y_2024!!` in source code | All encrypted PII (SSN, bank accounts) accessible to anyone with source access | Key not stored in Oracle Wallet or HSM; embedded in PKG_SECURITY.pkb |
| DQ-003 | USER_CREDENTIALS | `authenticate()` never queries USER_CREDENTIALS — password verification is a stub | Any valid username authenticates regardless of password supplied | Developer stub never completed |
| DQ-010 | USER_CREDENTIALS.PASSWORD_HASH | MD5 hashing (`DBMS_CRYPTO.HASH_MD5`) — cryptographically broken | Credential database compromise trivially reversible | MD5 chosen at build time; never upgraded |
| DQ-019 | TAX_BRACKETS / PKG_PAYROLL | HEAD_OF_HOUSEHOLD branch returns $0 federal tax | Employees with HOH filing status receive zero federal withholding | Code branch logic defect |

---

### 5.2 High-Severity Issues

| DQ-ID | Table / Column | Issue | Impact |
|-------|---------------|-------|--------|
| DQ-023 | USER_CREDENTIALS | No brute-force lockout mechanism | Credential stuffing attacks have no rate limiting |
| DQ-027 | USER_SESSIONS | SESSION_TIMEOUT_MINUTES in SYSTEM_PARAMETERS ignored; 30-minute timeout hard-coded | Parameter table is non-functional for session control |
| DQ-029 | USER_CREDENTIALS | `change_password` never verifies old password | Authenticated session can replace any employee's password silently |
| DQ-031 | TIME_ATTENDANCE_RECORDS (implied) | `import_time_attendance` logs success but performs no DML | Time attendance data silently discarded; false audit trail |
| DQ-032 | LEAVE_BALANCES / RPT_LEAVE_UTIL | CALENDAR_YEAR missing from leave utilisation cursor projection | Multi-year snapshots indistinguishable; report data ambiguous |
| BR-BA-12 | EMPLOYEE_BANK_ACCOUNTS | Table never referenced by payroll — direct deposit non-functional | Payroll runs complete without disbursing to bank accounts |
| BR-043b | EMPLOYEES.EMAIL | Duplicate email causes `TOO_MANY_ROWS`; `authenticate()` silently picks MIN(EMP_ID) | Affected employee cannot log in; no error surfaced |
| BR-LIB-05 | LEAVE_BALANCES.ACCRUED | Accrual retry block assigns rather than increments ACCRUED | Data loss on concurrent accrual retry |

---

### 5.3 Medium-Severity Issues

| DQ-ID | Table / Column | Issue |
|-------|---------------|-------|
| DQ-002 | EMPLOYEES.BANK_* | Denormalised bank fields on EMPLOYEES duplicate EMPLOYEE_BANK_ACCOUNTS with no sync mechanism |
| DQ-005 | SALARY_RECORDS | No DDL uniqueness constraint on (EMP_ID, END_DATE IS NULL) — multiple current salary rows possible |
| DQ-006 | EMPLOYEE_DEPENDENTS | BENEFITS_ENROLLED never read by export_benefits_feed — unenrolled dependents exported to ADP |
| DQ-007 | PERFORMANCE_REVIEWS | CALIBRATED_RATING / CALIBRATION_NOTES are dead columns — no write path exists |
| DQ-009 | PERFORMANCE_REVIEWS | `get_rating_distribution` reads OVERALL_RATING not CALIBRATED_RATING; org reports reflect pre-calibration data |
| DQ-013 | SYSTEM_PARAMETERS | FTP credentials stored plaintext (TD-10) |
| DQ-020 | EMPLOYEE_BANK_ACCOUNTS | ROUTING_NUMBER stored plaintext — full ACH credential pair accessible (TD-46) |
| DQ-025 | LEAVE_REQUESTS.SUPPORTING_DOC_PATH | Path traversal risk — no sanitisation of file path input (TD-47) |
| DQ-030 | PKG_SECURITY | `e_account_locked` / `e_session_expired` declared but never raised — Forms error handlers never fire |

---

### 5.4 Low-Severity Issues

| DQ-ID | Table / Column | Issue |
|-------|---------------|-------|
| DQ-014 | AUDIT_LOG | Single table for all log types — no independent retention control |
| DQ-015 | EMPLOYEES.GENDER | No CHECK constraint; arbitrary values distort EEO-1 reporting (TD-40) |
| DQ-016 | GOAL_WEIGHT | No range constraint on PERFORMANCE_GOALS.WEIGHT — values exceeding 100% are schema-valid |
| DQ-017 | JOB_GRADES.GL_ACCOUNT_CODE | Numeric convention 5100/2100/2200 undocumented; no reference table or COMMENT |
| DQ-018 | DEPARTMENTS | Recursive CONNECT BY hierarchy has no maximum depth guard |

---

## 6. Recommended Schema Improvements

### 6.1 Security Improvements

| Rec-ID | Priority | Recommendation | Affected Tables |
|--------|----------|---------------|-----------------|
| REC-S01 | Critical | Replace hard-coded AES key with Oracle Wallet / AWS KMS / HashiCorp Vault key reference; rotate all encrypted values post-migration | EMPLOYEES, EMPLOYEE_DEPENDENTS, EMPLOYEE_BANK_ACCOUNTS, USER_CREDENTIALS |
| REC-S02 | Critical | Replace MD5 with bcrypt (cost factor ≥ 12) or Argon2id for password hashing | USER_CREDENTIALS |
| REC-S03 | Critical | Implement authentication by actually querying USER_CREDENTIALS — current stub must be replaced | USER_CREDENTIALS, PKG_SECURITY |
| REC-S04 | High | Add LOGIN_ATTEMPTS, LOCKED_UNTIL, PASSWORD_CHANGED_DATE columns to USER_CREDENTIALS | USER_CREDENTIALS |
| REC-S05 | High | Encrypt ROUTING_NUMBER using same mechanism as ACCOUNT_NUMBER_ENC | EMPLOYEE_BANK_ACCOUNTS |
| REC-S06 | High | Move FTP_PASSWORD out of SYSTEM_PARAMETERS to a secrets manager | SYSTEM_PARAMETERS |
| REC-S07 | Medium | Add background job to sweep USER_SESSIONS and expire stale rows (>30 min since LOGIN_TIME) | USER_SESSIONS |
| REC-S08 | Medium | Add implement of old-password verification in change_password before allowing hash replacement | USER_CREDENTIALS |

---

### 6.2 Schema Structural Improvements

| Rec-ID | Priority | Recommendation | Rationale |
|--------|----------|---------------|-----------|
| REC-D01 | High | Remove BANK_ACCOUNT_NUMBER / BANK_ROUTING_NUMBER from EMPLOYEES; these are fully duplicated in EMPLOYEE_BANK_ACCOUNTS | Eliminates denormalisation and synchronisation gap |
| REC-D02 | High | Add UNIQUE constraint on EMPLOYEES.EMAIL and add pre-insert duplicate check with clear error — eliminate MIN(EMP_ID) silent fallback | Prevents authentication collision (BR-043b) |
| REC-D03 | High | Add UNIQUE constraint on SALARY_RECORDS(EMP_ID) WHERE END_DATE IS NULL (partial unique index) | Enforces single-current-salary invariant at DDL level |
| REC-D04 | High | Implement CALIBRATED_RATING write path in PKG_PERFORMANCE; add CALIBRATION status to PERFORMANCE_REVIEWS.STATUS enum; update get_rating_distribution to read CALIBRATED_RATING when non-null | Makes calibration columns functional |
| REC-D05 | High | Add GL_FEED_SENT_AT, GL_FEED_FILE_NAME columns to PAYROLL_RUNS | Enables GL feed delivery tracking (TD-80) |
| REC-D06 | High | Add UNIQUE constraint on EMPLOYEE_DEPENDENTS(EMP_ID, RELATIONSHIP) for singular relationship types (SPOUSE, DOMESTIC_PARTNER) | Prevents two-SPOUSE anomaly |
| REC-D07 | Medium | Add CHECK constraint on EMPLOYEE_BANK_ACCOUNTS: when DEPOSIT_TYPE = 'PARTIAL_AMOUNT' then DEPOSIT_AMOUNT IS NOT NULL; when DEPOSIT_TYPE = 'PARTIAL_PERCENT' then DEPOSIT_PERCENTAGE IS NOT NULL AND DEPOSIT_PERCENTAGE BETWEEN 0.01 AND 100.00 | Enforces split-deposit business logic at DDL level |
| REC-D08 | Medium | Add distribution validation trigger on EMPLOYEE_BANK_ACCOUNTS: total of all active account allocations per employee must equal 100% | Prevents over- and under-allocation (PP-BA-04/05) |
| REC-D09 | Medium | Split AUDIT_LOG into three tables: application_errors, audit_events, info_log | Enables independent retention and indexing strategies |
| REC-D10 | Medium | Materialise LEAVE_BALANCES.AVAILABLE as a database-generated column (GENERATED ALWAYS AS) | Removes formula inconsistency risk between schema and application code |
| REC-D11 | Medium | Add CHECK constraint on EMPLOYEES.GENDER IN ('M','F','O','N') | Prevents arbitrary values distorting EEO-1 compliance reports (TD-40) |
| REC-D12 | Medium | Add COBRA_NOTIFICATION_STATUS table (EMP_ID, TERMINATION_DATE, NOTIFICATION_SENT_AT, ELECTION_DEADLINE_DATE) | Creates audit trail for COBRA qualifying event compliance (PP-TERM-01) |
| REC-D13 | Low | Add COMMENT on PAY_ELEMENTS.GL_ACCOUNT_CODE documenting 5100=labor expense, 2100=payroll liability, 2200=benefits liability | Eliminates silent miscoding risk for new pay elements |
| REC-D14 | Low | Add PERFORMANCE_GOALS.WEIGHT CHECK constraint: BETWEEN 0 AND 100; add trigger summing weights per cycle to validate total = 100 per employee | Enforces goal-weighting business rule |
| REC-D15 | Low | Create GENDER_CODES lookup table; add FK from EMPLOYEES.GENDER | Normalises gender values; links to LOOKUP_VALUES pattern already used |

---

### 6.3 Missing Implementations Required for Production

| Rec-ID | Priority | Recommendation | Missing Artefact |
|--------|----------|---------------|-----------------|
| REC-I01 | Critical | Implement PKG_PAYROLL.calculate_final_pay procedure | Missing entirely — every termination requires fully manual payroll (PP-TERM-03) |
| REC-I02 | Critical | Implement ACH disbursement procedure reading EMPLOYEE_BANK_ACCOUNTS | EMPLOYEE_BANK_ACCOUNTS never read — direct deposit non-functional (PP-BA-01) |
| REC-I03 | Critical | Implement COBRA notification workflow: identify qualifying events on termination, queue notification within 14-day window, record election deadline | No COBRA logic exists (PP-TERM-01) |
| REC-I04 | High | Implement PKG_INTEGRATION.sync_org_structure (currently a no-op stub that logs false success) | Org sync does nothing; monitoring indistinguishable from success (BR-ORG-02) |
| REC-I05 | High | Implement RPT_* table population in refresh_reporting_tables (currently no-op stub) | All 7 RPT_* tables perpetually empty; reports hit OLTP directly |
| REC-I06 | High | Implement ACH prenote procedure on EMPLOYEE_BANK_ACCOUNTS creation | PRENOTE_SENT/PRENOTE_DATE never written — Nacha compliance gap (PP-BA-03) |
| REC-I07 | High | Implement TIME_ATTENDANCE_RECORDS processing with payroll linkage | CSV import is a stub — attendance data silently discarded (DQ-031) |
| REC-I08 | Medium | Implement PKG_SECURITY.revoke_access (referenced in terminate_employee but does not exist) | Session revocation gap; in-flight sessions survive up to 30 minutes post-termination |

---

## 7. Data Lifecycle Management

### 7.1 Retention Policy by Data Category

| Table / Category | Retention Period | Policy Basis | Archive Action | Purge Action |
|-----------------|-----------------|--------------|---------------|--------------|
| EMPLOYEES (active) | Indefinite while active | HR operational requirement | — | Soft-delete only |
| EMPLOYEES (terminated) | 7 years post-termination | IRS / FLSA records retention | Archive to cold storage after Year 3 | Physical delete after Year 7 |
| SALARY_RECORDS | 7 years from pay period | FLSA / IRS W-2 retention | Archive after Year 3 | Purge after Year 7 |
| PAYROLL_RUNS / PAYROLL_DETAILS | 7 years from run date | FLSA / IRS | Archive after Year 3 | Purge after Year 7 |
| DEDUCTION_RECORDS | 7 years | FLSA / Benefits compliance | Archive after Year 3 | Purge after Year 7 |
| LEAVE_BALANCES | 3 years post-termination | FMLA requires 3-year records | Archive on termination+3yr | Purge after 3 years archived |
| LEAVE_REQUESTS | 3 years post-request | FMLA record-keeping | Archive after Year 2 | Purge after Year 3 |
| PERFORMANCE_REVIEWS | 5 years | Internal HR policy (no federal mandate) | Archive after Year 3 | Purge after Year 5 |
| PERFORMANCE_GOALS | 5 years | Internal HR policy | Archive with review | Purge after Year 5 |
| BENEFIT_ENROLLMENTS | 6 years post-coverage | ERISA 6-year records requirement | Archive after Year 3 | Purge after Year 6 |
| EMPLOYEE_DEPENDENTS | 6 years post-coverage end | ERISA / COBRA | Archive with enrollment | Purge after Year 6 |
| EMPLOYEE_BANK_ACCOUNTS | Until account inactivation + 7 years | NACHA requirement | Archive on inactivation | Purge after 7 years |
| AUDIT_LOG (AUDIT type) | 7 years | SOX / internal compliance | Archive after Year 2 | Purge after Year 7 |
| AUDIT_LOG (ERROR type) | 2 years | Operational support | Archive after Year 1 | Purge after Year 2 |
| AUDIT_LOG (INFO type) | 90 days | Operational support | — | Purge after 90 days |
| USER_SESSIONS | 90 days | Security forensics | — | Purge after 90 days |
| USER_CREDENTIALS | Until employment end + 7 years | Security compliance | Archive on termination | Purge after 7 years |
| NOTIFICATION_QUEUE (SENT) | 180 days | Operational troubleshooting | — | Purge after 180 days |
| NOTIFICATION_QUEUE (FAILED) | 1 year | Compliance evidence | Archive after 180 days | Purge after 1 year |
| RPT_* tables | Rolling 13 months | Reporting freshness | Archive prior year | Purge on annual refresh |

---

### 7.2 Archival Strategy

| Phase | Description | Mechanism |
|-------|-------------|-----------|
| Active Tier | All rows within retention window, frequently queried | Primary Oracle schema / target OLTP database |
| Archive Tier | Rows beyond operational window but within legal retention | Partitioned archive tables or separate archive schema; read-only grants |
| Cold Tier | Rows in years 4–7 for financial data | Compressed flat files (Parquet) on object storage; catalogued in data inventory |
| Purge | Physical DELETE after retention expiry | Scheduled PKG_PURGE procedure (to be built); requires compliance sign-off per run |

---

### 7.3 Archival Prerequisites for Current System

The following actions must be completed before any archival or purge schedule is activated:

| Prerequisite | Reason |
|-------------|--------|
| Encrypt ROUTING_NUMBER on EMPLOYEE_BANK_ACCOUNTS before archiving | Plaintext ACH routing data in archive files is a data breach |
| Rotate AES encryption key before archiving any EMPLOYEES or DEPENDENTS rows | Current key is embedded in plaintext source; archived ciphertext would use compromised key |
| Resolve EMPLOYEE_DEPENDENTS termination gap (BR-DEP-09) | Terminated employees' dependents must be inactivated before COBRA period tracking begins — unresolved state blocks accurate archive timestamping |
| Confirm COBRA election period before archiving BENEFIT_ENROLLMENTS | ERISA requires records be kept for the COBRA election window; premature archive violates this |
| Implement AUDIT_LOG table split (REC-D09) before activating 90-day INFO purge | Mixed log types in single table make selective purge unsafe without the split |

---

### 7.4 PII-Specific Data Lifecycle

All PII fields are subject to additional constraints beyond standard retention:

| PII Field | Tables | At Termination | At Archive | At Purge |
|-----------|--------|---------------|------------|----------|
| SSN_ENCRYPTED | EMPLOYEES, EMPLOYEE_DEPENDENTS | Retain encrypted | Retain encrypted; do not export key alongside data | Physical delete of ciphertext; key rotation before purge |
| ACCOUNT_NUMBER_ENC | EMPLOYEE_BANK_ACCOUNTS | Retain for final pay period | Retain encrypted in archive | Physical delete on purge date |
| ROUTING_NUMBER | EMPLOYEE_BANK_ACCOUNTS | **Must be encrypted first** (currently plaintext — REC-S05) | Encrypt before any archive operation | Physical delete |
| FIRST_NAME, LAST_NAME | EMPLOYEES, EMPLOYEE_DEPENDENTS | Retain for legal records | Retain in archive | Pseudonymise or delete at purge |
| DATE_OF_BIRTH | EMPLOYEES, EMPLOYEE_DEPENDENTS | Retain for COBRA/benefits | Retain in archive | Delete at purge |
| EMAIL, PHONE | EMPLOYEES | Retain while employed | Anonymise at archive if not needed for compliance | Delete at purge |
| IP_ADDRESS | USER_SESSIONS | Retain 90 days | Not archived | Purge at 90-day mark |

---

### 7.5 Retention Control Implementation

The current system has no scheduled purge job and no partition-based archival. The recommended target-state lifecycle architecture:

```
┌──────────────────────┐   nightly   ┌────────────────────┐   quarterly  ┌──────────────┐
│  OLTP Primary Tables │────────────►│  archive.* schema  │─────────────►│ object store │
│  (active tier)       │             │  (read-only)        │             │  (cold tier) │
└──────────────────────┘             └────────────────────┘             └──────────────┘
         │                                    │
         │  DBMS_SCHEDULER nightly            │  DBMS_SCHEDULER quarterly
         │  ├─ insert_to_archive()            │  ├─ export_to_parquet()
         │  └─ soft-flag archived rows        │  └─ drop archived rows from archive schema
         │
         │  DBMS_SCHEDULER weekly
         │  └─ purge_expired()
         │     ├─ DELETE AUDIT_LOG INFO rows > 90d
         │     └─ DELETE USER_SESSIONS rows > 90d
```

All purge procedures must:
1. Log the purge execution (row count, table, timestamp) to `audit_events` before DELETE.
2. Require dual-approval sign-off from Data Privacy Officer and IT Security for initial activation.
3. Run in autonomous transactions to allow rollback without affecting parent transaction.
4. Produce a reconciliation report matching archive counts to source deletion counts.

---

*Document end — 07_DATA_MODEL_SPECIFICATION.md*
*Generated from: BA_Deep_Analyst (BR-01–BR-140), DA_Data_Extractor, DA_Data_Reviewer (DQ-001–DQ-032), AA_Quality_Review (QR-001–QR-033), TA_Deep_Analyst (TD-01–TD-81)*
