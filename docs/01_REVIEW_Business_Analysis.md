# Human Review — Business Analysis

**Reviewer:** ___________________________
**Date reviewed:** ___________________________
**Sign-off:** ___________________________

**Source files:** `results/Business_Analysis/BA_Deep_Analyst.md`, `results/Business_Analysis/BA_Deep_Analyst_Pass2.md`
**Forward Engineering docs using this:** `01_BRD.md`, `02_BUSINESS_CAPABILITY_MODEL.md`, `03_USE_CASE_SPECIFICATION.md`

---

## 1. Business Rule Inventory

The AI extracted business rules from PL/SQL code, form validations, and triggers.
Verify the count and completeness.

| Finding | AI Conclusion | Reviewer Action | Notes |
|---------|--------------|-----------------|-------|
| Total business rules extracted | 140 rules (BR-001 to BR-140) | | |
| Rules from BA_Deep_Analyst_FINAL.md (root) | 120 rules | | |
| Rules from BA_Deep_Analyst_Edge.md | 87 rules | | |
| **Which file is the canonical BA output?** | AMBIGUOUS — 3 versions exist | **DECIDE:** | |
| Domains covered | Employee Mgmt, Payroll, Leave, Performance, Security, Integration, Reporting | | |

**⚠️ CONTRADICTION (see 06_REVIEW): The three BA files have different rule counts (87/120/140). A human must designate one as canonical.**

---

## 2. Key Business Rules — Verify These

| Rule ID | Rule Statement | Source | Reviewer Action | Correct Value (if wrong) |
|---------|---------------|--------|-----------------|--------------------------|
| BR-001 | Employee number format: EMP + 5-digit zero-padded sequential number (e.g. EMP00001) | PKG_EMPLOYEE.generate_emp_number | | |
| BR-002 | Hire date cannot be more than 90 days in the future (UI validation) | HRMS_EMPLOYEE form WHEN-VALIDATE-ITEM | **⚠️ CONFLICT** | |
| BR-003 | Hire date cannot be more than 180 days in the future (DB trigger) | TRG_EMP_BEFORE_INSERT | **⚠️ CONFLICT** | |
| BR-004 | Employee salary must be positive | TRG_EMP_BEFORE_INSERT | | |
| BR-005 | Manager must be in same department as employee | PKG_EMPLOYEE | | |
| BR-006 | Active employee cannot be deleted — only terminated | TRG_EMP_BEFORE_DELETE | | |
| BR-007 | Federal tax for HEAD_OF_HOUSEHOLD filing status = $0 | PKG_PAYROLL.calculate_federal_tax | **⚠️ CRITICAL BUG — is this intentional?** | |
| BR-008 | Payroll cannot be approved by same person who created it | PKG_PAYROLL | | |
| BR-009 | Leave balance cannot go below 0 | PKG_LEAVE | | |
| BR-010 | Employee cannot approve their own leave | PKG_LEAVE | | |
| BR-011 | Performance review required annually | PKG_PERFORMANCE | | |
| BR-012 | Salary change requires approval workflow | PKG_EMPLOYEE | | |
| BR-013 | Password must be at least 8 characters | PKG_SECURITY | | |
| BR-014 | Account locked after 5 failed login attempts | PKG_SECURITY | | |
| BR-015 | Rehire requires 30-day waiting period after termination | PKG_EMPLOYEE.rehire_employee | **⚠️ PROCEDURE IS BROKEN** | |

---

## 3. Business Processes — Verify These

| Process | AI Description | Reviewer Action | Missing Steps / Corrections |
|---------|---------------|-----------------|------------------------------|
| Hire Employee | Generate emp number → Insert employee → Send welcome email → Create credentials | | |
| Process Payroll | Calculate gross → Apply deductions → Calculate taxes → Net pay → Create payroll details | | |
| Submit Leave | Check balance → Create request → Notify manager → Update balance on approval | | |
| Terminate Employee | Block if active loan/payroll → Set status TERMINATED → Revoke credentials | | |
| Rehire Employee | Check waiting period → Reset status to ACTIVE → Restore credentials | **BROKEN — trigger blocks this** | |
| Approve Leave | Check approver authority → Update status → Adjust balance | | |
| Performance Review | Create cycle → Assign employees → Submit self-assessment → Manager review → Calibration | | |

---

## 4. Actor / User Role Inventory

Confirm these are all the roles in the system:

| Role | Confirmed in code? | AI confidence | Reviewer Action |
|------|--------------------|---------------|-----------------|
| HR Manager | Yes (PKG_EMPLOYEE, form validations) | HIGH | |
| Employee (self-service) | Yes (PKG_LEAVE self-service patterns) | HIGH | |
| Payroll Administrator | Yes (PKG_PAYROLL) | HIGH | |
| System Administrator | Yes (PKG_SECURITY) | HIGH | |
| Department Manager (approver) | Yes (leave approval, performance) | HIGH | |
| Executive / Report Consumer | Inferred from PKG_REPORTING | MEDIUM | |
| Finance / GL Recipient | Inferred from PKG_INTEGRATION GL feed stub | LOW | |

**Missing roles not found in code:** ___________________________

---

## 5. Integration Points — Verify These

| Integration | Direction | AI Confidence | Reviewer Action |
|-------------|-----------|---------------|-----------------|
| ADP Payroll export | Outbound | MEDIUM — stub only, no real ADP format | |
| SMTP email notifications | Outbound | HIGH — UTL_SMTP calls confirmed | |
| GL (General Ledger) feed | Outbound | LOW — refresh_reporting_tables stub only | |
| NACHA direct deposit file | Outbound | LOW — referenced in comments, no implementation | |
| Time & Attendance import | Inbound | MEDIUM — PKG_INTEGRATION.import_time_attendance exists but target table missing | |

---

## 6. BRD Review

Open [results/ForwardEngineering_Docs/01_BRD.md](../results/ForwardEngineering_Docs/01_BRD.md) and check:

| Section | Complete? | Accurate? | Reviewer Notes |
|---------|-----------|-----------|----------------|
| Executive Summary | | | |
| Business Objectives | | | |
| Business Requirements (BR-001 to BR-040+) | | | |
| Stakeholders | | | |
| Success Metrics | | | |
| Risk Register | | | |

---

## 7. Open Questions for Business Stakeholders

These cannot be answered from code alone. A business stakeholder must answer them:

1. Is the HEAD_OF_HOUSEHOLD = $0 tax result intentional (a special program) or a bug?
2. What is the correct maximum hire date in the future — 90 days or 180 days?
3. Is the rehire employee feature required in the new system? If yes, what is the correct business process?
4. Are hourly-basis employees supported? (The DB schema has `SALARY_BASIS IN ('ANNUAL','HOURLY')` but payroll code only processes annual.)
5. What is the correct canonical set of business rules — which BA document should be used?
6. Does the new system need to support multi-state tax calculations? (Currently only single state is supported.)
7. What are the actual concurrent user targets for performance sizing?
