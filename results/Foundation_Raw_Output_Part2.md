```json
        "transitions": [
          {"from": "DRAFT", "to": "CALCULATED", "trigger": "calculate"},
          {"from": "CALCULATED", "to": "APPROVED", "trigger": "approve"},
          {"from": "APPROVED", "to": "GL_GENERATED", "trigger": "generate_gl"},
          {"from": "GL_GENERATED", "to": "COMPLETED", "trigger": "close"}
        ]
      },
      "columns": [
        { "name": "runId", "source_column": "RUN_ID", "type": "Long", "constraints": ["PK"] },
        { "name": "runName", "source_column": "RUN_NAME", "type": "String", "constraints": ["NOT_NULL"] },
        { "name": "payPeriodStart", "source_column": "PAY_PERIOD_START", "type": "LocalDate", "constraints": ["NOT_NULL"] },
        { "name": "payPeriodEnd", "source_column": "PAY_PERIOD_END", "type": "LocalDate", "constraints": ["NOT_NULL"] },
        { "name": "runDate", "source_column": "RUN_DATE", "type": "LocalDate", "constraints": ["NOT_NULL"] },
        { "name": "status", "source_column": "STATUS", "type": "PayrollRunStatus", "constraints": ["NOT_NULL"] },
        { "name": "totalGross", "source_column": "TOTAL_GROSS", "type": "BigDecimal" },
        { "name": "totalNet", "source_column": "TOTAL_NET", "type": "BigDecimal" },
        { "name": "totalDeductions", "source_column": "TOTAL_DEDUCTIONS", "type": "BigDecimal" },
        { "name": "calculatedDate", "source_column": "CALCULATED_DATE", "type": "LocalDateTime" },
        { "name": "approvedBy", "source_column": "APPROVED_BY", "type": "Long", "fk": "Employee.employeeId" },
        { "name": "approvedDate", "source_column": "APPROVED_DATE", "type": "LocalDateTime" },
        { "name": "createdBy", "source_column": "CREATED_BY", "type": "Long", "fk": "Employee.employeeId" },
        { "name": "createdDate", "source_column": "CREATED_DATE", "type": "LocalDateTime", "constraints": ["NOT_NULL"] }
      ]
    },
    {
      "id": "ENT-004",
      "name": "LeaveBalance",
      "source_table": "LEAVE_BALANCES",
      "status": "CONFIRMED",
      "virtual_columns": ["available"],
      "columns": [
        { "name": "balanceId", "source_column": "BALANCE_ID", "type": "Long", "constraints": ["PK"] },
        { "name": "employeeId", "source_column": "EMPLOYEE_ID", "type": "Long", "fk": "Employee.employeeId", "constraints": ["NOT_NULL"] },
        { "name": "leaveTypeId", "source_column": "LEAVE_TYPE_ID", "type": "Long", "fk": "LeaveType.leaveTypeId", "constraints": ["NOT_NULL"] },
        { "name": "leaveYear", "source_column": "LEAVE_YEAR", "type": "Integer", "constraints": ["NOT_NULL"] },
        { "name": "openingBalance", "source_column": "OPENING_BALANCE", "type": "BigDecimal", "constraints": ["NOT_NULL"] },
        { "name": "accrued", "source_column": "ACCRUED", "type": "BigDecimal", "constraints": ["NOT_NULL"] },
        { "name": "used", "source_column": "USED", "type": "BigDecimal", "constraints": ["NOT_NULL"] },
        { "name": "pending", "source_column": "PENDING", "type": "BigDecimal", "constraints": ["NOT_NULL"] },
        { "name": "adjustment", "source_column": "ADJUSTMENT", "type": "BigDecimal" },
        { "name": "available", "source_column": "AVAILABLE", "type": "BigDecimal", "virtual": true, "formula": "openingBalance + accrued - used + adjustment - pending" },
        { "name": "updatedDate", "source_column": "UPDATED_DATE", "type": "LocalDateTime" }
      ]
    },
    {
      "id": "ENT-005",
      "name": "PerformanceReview",
      "source_table": "PERFORMANCE_REVIEWS",
      "status": "CONFIRMED",
      "status_machine": {
        "states": ["PENDING", "SELF_COMPLETE", "MANAGER_COMPLETE", "CALIBRATED", "FINAL"],
        "transitions": [
          {"from": "PENDING", "to": "SELF_COMPLETE", "trigger": "self_complete"},
          {"from": "SELF_COMPLETE", "to": "MANAGER_COMPLETE", "trigger": "manager_complete"},
          {"from": "MANAGER_COMPLETE", "to": "CALIBRATED", "trigger": "calibrate"},
          {"from": "CALIBRATED", "to": "FINAL", "trigger": "finalise"},
          {"from": "MANAGER_COMPLETE", "to": "FINAL", "trigger": "finalise_uncalibrated"}
        ]
      },
      "columns": [
        { "name": "reviewId", "source_column": "REVIEW_ID", "type": "Long", "constraints": ["PK"] },
        { "name": "employeeId", "source_column": "EMPLOYEE_ID", "type": "Long", "fk": "Employee.employeeId", "constraints": ["NOT_NULL"] },
        { "name": "cycleId", "source_column": "CYCLE_ID", "type": "Long", "fk": "ReviewCycle.cycleId", "constraints": ["NOT_NULL"] },
        { "name": "selfRating", "source_column": "SELF_RATING", "type": "Integer", "validation": "min=1,max=5" },
        { "name": "managerRating", "source_column": "MANAGER_RATING", "type": "Integer", "validation": "min=1,max=5" },
        { "name": "overallRating", "source_column": "OVERALL_RATING", "type": "Integer", "constraints": ["NOT_NULL"], "validation": "min=1,max=5" },
        { "name": "calibratedRating", "source_column": "CALIBRATED_RATING", "type": "Integer", "validation": "min=1,max=5", "legacy_gap": "CALIBRATION_NO_WRITE_PATH" },
        { "name": "reviewStatus", "source_column": "REVIEW_STATUS", "type": "ReviewStatus", "constraints": ["NOT_NULL"] }
      ]
    }
  ],
  "api_endpoints": [
    { "id": "EP-001", "method": "GET",  "path": "/employees",                              "bc": "BC-01", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-002", "method": "POST", "path": "/employees",                              "bc": "BC-01", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-003", "method": "GET",  "path": "/employees/{employeeId}",                 "bc": "BC-01", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-004", "method": "PUT",  "path": "/employees/{employeeId}",                 "bc": "BC-01", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-005", "method": "POST", "path": "/employees/{employeeId}/terminate",       "bc": "BC-01", "security": "ROLE_HR_MANAGER",   "async": false },
    { "id": "EP-006", "method": "POST", "path": "/employees/{employeeId}/transfer",        "bc": "BC-01", "security": "ROLE_HR_MANAGER",   "async": false },
    { "id": "EP-007", "method": "POST", "path": "/employees/{employeeId}/status",          "bc": "BC-01", "security": "ROLE_HR_MANAGER",   "async": false },
    { "id": "EP-008", "method": "GET",  "path": "/employees/{employeeId}/history",         "bc": "BC-01", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-009", "method": "GET",  "path": "/departments",                            "bc": "BC-07", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-010", "method": "POST", "path": "/departments",                            "bc": "BC-07", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-011", "method": "GET",  "path": "/departments/{departmentId}",             "bc": "BC-07", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-012", "method": "PUT",  "path": "/departments/{departmentId}",             "bc": "BC-07", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-013", "method": "GET",  "path": "/departments/{departmentId}/employees",   "bc": "BC-07", "security": "ROLE_MANAGER",      "async": false },
    { "id": "EP-014", "method": "GET",  "path": "/positions",                              "bc": "BC-07", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-015", "method": "POST", "path": "/positions",                              "bc": "BC-07", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-016", "method": "GET",  "path": "/positions/{positionId}",                 "bc": "BC-07", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-017", "method": "PUT",  "path": "/positions/{positionId}",                 "bc": "BC-07", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-018", "method": "GET",  "path": "/org/chart",                              "bc": "BC-07", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-019", "method": "GET",  "path": "/employees/{employeeId}/salary",          "bc": "BC-02", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-020", "method": "GET",  "path": "/employees/{employeeId}/salary/history",  "bc": "BC-02", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-021", "method": "POST", "path": "/compensation/salary-records",            "bc": "BC-02", "security": "ROLE_HR_MANAGER",   "async": false },
    { "id": "EP-022", "method": "GET",  "path": "/payroll/runs",                           "bc": "BC-02", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-023", "method": "POST", "path": "/payroll/runs",                           "bc": "BC-02", "security": "ROLE_HR_MANAGER",   "async": false },
    { "id": "EP-024", "method": "GET",  "path": "/payroll/runs/{runId}",                   "bc": "BC-02", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-025", "method": "POST", "path": "/payroll/runs/{runId}/calculate",         "bc": "BC-02", "security": "ROLE_HR_MANAGER",   "async": true  },
    { "id": "EP-026", "method": "POST", "path": "/payroll/runs/{runId}/approve",           "bc": "BC-02", "security": "ROLE_HR_MANAGER",   "async": false },
    { "id": "EP-027", "method": "POST", "path": "/payroll/runs/{runId}/generate-gl",       "bc": "BC-02", "security": "ROLE_HR_ADMIN",     "async": true  },
    { "id": "EP-028", "method": "POST", "path": "/payroll/runs/{runId}/close",             "bc": "BC-02", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-029", "method": "GET",  "path": "/payroll/runs/{runId}/details",           "bc": "BC-02", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-030", "method": "GET",  "path": "/employees/{employeeId}/payroll/details", "bc": "BC-02", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-031", "method": "GET",  "path": "/leave/types",                            "bc": "BC-03", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-032", "method": "POST", "path": "/leave/types",                            "bc": "BC-03", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-033", "method": "GET",  "path": "/leave/balances",                         "bc": "BC-03", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-034", "method": "GET",  "path": "/employees/{employeeId}/leave/balances",  "bc": "BC-03", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-035", "method": "POST", "path": "/leave/requests",                         "bc": "BC-03", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-036", "method": "GET",  "path": "/leave/requests/{requestId}",             "bc": "BC-03", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-037", "method": "PUT",  "path": "/leave/requests/{requestId}/approve",     "bc": "BC-03", "security": "ROLE_MANAGER",      "async": false },
    { "id": "EP-038", "method": "PUT",  "path": "/leave/requests/{requestId}/reject",      "bc": "BC-03", "security": "ROLE_MANAGER",      "async": false },
    { "id": "EP-039", "method": "PUT",  "path": "/leave/requests/{requestId}/cancel",      "bc": "BC-03", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-040", "method": "POST", "path": "/leave/balances/accrue",                  "bc": "BC-03", "security": "ROLE_HR_ADMIN",     "async": true  },
    { "id": "EP-041", "method": "GET",  "path": "/performance/cycles",                     "bc": "BC-04", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-042", "method": "POST", "path": "/performance/cycles",                     "bc": "BC-04", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-043", "method": "GET",  "path": "/performance/cycles/{cycleId}",           "bc": "BC-04", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-044", "method": "POST", "path": "/performance/cycles/{cycleId}/close",     "bc": "BC-04", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-045", "method": "GET",  "path": "/performance/reviews",                    "bc": "BC-04", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-046", "method": "POST", "path": "/performance/reviews",                    "bc": "BC-04", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-047", "method": "GET",  "path": "/performance/reviews/{reviewId}",         "bc": "BC-04", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-048", "method": "PUT",  "path": "/performance/reviews/{reviewId}/self-complete",    "bc": "BC-04", "security": "ROLE_EMPLOYEE", "async": false },
    { "id": "EP-049", "method": "PUT",  "path": "/performance/reviews/{reviewId}/manager-complete", "bc": "BC-04", "security": "ROLE_MANAGER",  "async": false },
    { "id": "EP-050", "method": "PUT",  "path": "/performance/reviews/{reviewId}/calibrate",        "bc": "BC-04", "security": "ROLE_HR_ADMIN", "async": false, "fixes_gap": "SEC-GAP-07" },
    { "id": "EP-051", "method": "GET",  "path": "/performance/goals",                      "bc": "BC-04", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-052", "method": "POST", "path": "/performance/goals",                      "bc": "BC-04", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-053", "method": "PUT",  "path": "/performance/goals/{goalId}",             "bc": "BC-04", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-054", "method": "GET",  "path": "/benefits/plans",                         "bc": "BC-05", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-055", "method": "POST", "path": "/benefits/plans",                         "bc": "BC-05", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-056", "method": "GET",  "path": "/employees/{employeeId}/benefits",        "bc": "BC-05", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-057", "method": "POST", "path": "/benefits/enrollments",                   "bc": "BC-05", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-058", "method": "PUT",  "path": "/benefits/enrollments/{enrollmentId}/terminate", "bc": "BC-05", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-059", "method": "POST", "path": "/auth/login",                             "bc": "BC-06", "security": "PUBLIC",            "async": false },
    { "id": "EP-060", "method": "POST", "path": "/auth/logout",                            "bc": "BC-06", "security": "AUTHENTICATED",     "async": false },
    { "id": "EP-061", "method": "POST", "path": "/auth/refresh",                           "bc": "BC-06", "security": "PUBLIC",            "async": false },
    { "id": "EP-062", "method": "POST", "path": "/auth/change-password",                   "bc": "BC-06", "security": "AUTHENTICATED",     "async": false },
    { "id": "EP-063", "method": "POST", "path": "/auth/admin/reset-password",              "bc": "BC-06", "security": "ROLE_SYSTEM_ADMIN", "async": false },
    { "id": "EP-064", "method": "GET",  "path": "/notifications/templates",                "bc": "BC-08", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-065", "method": "POST", "path": "/notifications/templates",                "bc": "BC-08", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-066", "method": "GET",  "path": "/employees/{employeeId}/notifications",   "bc": "BC-08", "security": "ROLE_EMPLOYEE",     "async": false },
    { "id": "EP-067", "method": "POST", "path": "/notifications/queue/retry",              "bc": "BC-08", "security": "ROLE_HR_ADMIN",     "async": true  },
    { "id": "EP-068", "method": "POST", "path": "/integration/exports/payroll-gl",         "bc": "BC-09", "security": "ROLE_HR_ADMIN",     "async": true  },
    { "id": "EP-069", "method": "POST", "path": "/integration/exports/benefits-adp",       "bc": "BC-09", "security": "ROLE_HR_ADMIN",     "async": true  },
    { "id": "EP-070", "method": "GET",  "path": "/integration/exports/{exportId}",         "bc": "BC-09", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-071", "method": "GET",  "path": "/integration/exports/{exportId}/download","bc": "BC-09", "security": "ROLE_HR_ADMIN",     "async": false },
    { "id": "EP-072", "method": "GET",  "path": "/reports/headcount",                      "bc": "BC-10", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-073", "method": "GET",  "path": "/reports/turnover",                       "bc": "BC-10", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-074", "method": "GET",  "path": "/reports/compensation",                   "bc": "BC-10", "security": "ROLE_HR_MANAGER",   "async": false },
    { "id": "EP-075", "method": "GET",  "path": "/reports/leave",                          "bc": "BC-10", "security": "ROLE_HR_SPECIALIST", "async": false },
    { "id": "EP-076", "method": "GET",  "path": "/reports/performance",                    "bc": "BC-10", "security": "ROLE_HR_SPECIALIST", "async": false }
  ],
  "defects": [
    { "id": "DEF-001", "code": "HOH_ZERO_TAX",                    "severity": "HIGH",     "bc": "BC-02", "description": "HEAD_OF_HOUSEHOLD tax filing status returns $0 federal tax in PKG_PAYROLL", "remediation_rule": "GEN-006", "fix_required_before_phase": 3 },
    { "id": "DEF-002", "code": "NO_SESSION_INVALIDATION",          "severity": "HIGH",     "bc": "BC-06", "description": "Grade change takes effect without invalidating existing sessions", "remediation_rule": "GEN-006", "fix_required_before_phase": 1 },
    { "id": "DEF-003", "code": "PENDING_OMITTED_FROM_VIEW",        "severity": "MEDIUM",   "bc": "BC-03", "description": "VW_LEAVE_SUMMARY omits PENDING column; approved-not-taken leave invisible", "remediation_rule": "GEN-006", "fix_required_before_phase": 2 },
    { "id": "DEF-004", "code": "CALIBRATION_NO_WRITE_PATH",        "severity": "MEDIUM",   "bc": "BC-04", "description": "CALIBRATED_RATING has no application write procedure; requires direct SQL", "remediation_rule": "GEN-006", "fix_required_before_phase": 2 },
    { "id": "DEF-005", "code": "CARRY_FORWARD_UNIMPLEMENTED",      "severity": "MEDIUM",   "bc": "BC-03", "description": "LEAVE_TYPES.CARRY_FORWARD flag exists but year-end carry-forward logic not implemented", "remediation_rule": "GEN-006", "fix_required_before_phase": 2 },
    { "id": "DEF-006", "code": "PTO_PAYOUT_UNIMPLEMENTED",         "severity": "MEDIUM",   "bc": "BC-03", "description": "IS_PAID flag exists but final-pay PTO payout not implemented in termination flow", "remediation_rule": "GEN-006", "fix_required_before_phase": 3 },
    { "id": "DEF-007", "code": "NACHA_NOT_IMPLEMENTED",            "severity": "MEDIUM",   "bc": "BC-09", "description": "ACH/NACHA file generation not implemented; direct deposit impossible", "remediation_rule": "GEN-006", "fix_required_before_phase": 3 },
    { "id": "DEF-008", "code": "KEY_IN_DATABASE",                  "severity": "CRITICAL", "bc": "BC-06", "description": "AES-256 encryption key stored in SYSTEM_CONFIG in same DB as encrypted data", "remediation_rule": "GEN-006", "fix_required_before_phase": 1 }
  ],
  "inferred_tables": [
    { "table": "EMPLOYEE_PAY_ELEMENTS", "inferred_from": "PKG_PAYROLL element ID constants", "decision": "PENDING" },
    { "table": "USER_CREDENTIALS",      "inferred_from": "PKG_SECURITY authenticate procedure", "decision": "PENDING" },
    { "table": "TERMINATION_CODES",     "inferred_from": "EMPLOYEES.TERMINATION_REASON FK", "decision": "PENDING" },
    { "table": "TIME_ATTENDANCE_RECORDS","inferred_from": "Code comments referencing time import", "decision": "PENDING" },
    { "table": "RPT_HEADCOUNT_SNAPSHOT","inferred_from": "Reporting context inference", "decision": "PENDING" },
    { "table": "RPT_TURNOVER_SUMMARY",  "inferred_from": "Reporting context inference", "decision": "PENDING" },
    { "table": "RPT_PAYROLL_SUMMARY",   "inferred_from": "Reporting context inference", "decision": "PENDING" }
  ],
  "validation_gates": [
    { "id": "VG-01", "name": "Data Dictionary Completeness",  "blocking": true,  "automated": true,  "required_before_artefacts": ["ART-001", "ART-002"] },
    { "id": "VG-02", "name": "Domain Model Completeness",     "blocking": true,  "automated": true,  "required_before_artefacts": ["ART-004"] },
    { "id": "VG-03", "name": "API Contract Completeness",     "blocking": true,  "automated": true,  "required_before_artefacts": ["ART-005", "ART-006", "ART-010"] },
    { "id": "VG-04", "name": "Business Rule Mapping",         "blocking": true,  "automated": false, "required_before_artefacts": ["ART-004"] },
    { "id": "VG-05", "name": "Security Architecture Review",  "blocking": true,  "automated": false, "required_before_artefacts": ["ART-008"] },
    { "id": "VG-06", "name": "Migration Script Dry-Run",      "blocking": true,  "automated": true,  "required_before_artefacts": ["ART-001"] },
    { "id": "VG-07", "name": "Test Coverage Gate",            "blocking": true,  "automated": true,  "required_before_artefacts": [] },
    { "id": "VG-08", "name": "NFR Validation",               "blocking": true,  "automated": false, "required_before_artefacts": [] }
  ],
  "migration_phases": [
    {
      "phase": 1,
      "name": "Foundation",
      "duration_months": 3,
      "bounded_contexts": ["BC-01", "BC-06", "BC-07"],
      "critical_fixes": ["DEF-002", "DEF-008"]
    },
    {
      "phase": 2,
      "name": "Core HR Operations",
      "duration_months": 3,
      "bounded_contexts": ["BC-03", "BC-04", "BC-08"],
      "critical_fixes": ["DEF-003", "DEF-004", "DEF-005"]
    },
    {
      "phase": 3,
      "name": "Payroll and Benefits",
      "duration_months": 4,
      "bounded_contexts": ["BC-02", "BC-05", "BC-09"],
      "critical_fixes": ["DEF-001", "DEF-006", "DEF-007"]
    },
    {
      "phase": 4,
      "name": "Integration, Reporting, Hardening",
      "duration_months": 2,
      "bounded_contexts": ["BC-10"],
      "critical_fixes": []
    }
  ]
}
```

=== DOCUMENT: 17_FORWARD_ENGINEERING_READINESS_REPORT.md ===

# 17 — Forward Engineering Readiness Report
**System:** Acme Corporation HRMS
**Assessment Date:** Current
**Assessor:** Foundation Synthesis Agent
**Overall Readiness Score: 71 / 100 — CONDITIONAL GO**

---

## 1. Scoring Methodology

Each dimension is scored 0–10. Weights reflect criticality to a successful forward-engineering effort. Weighted score determines Go / Conditional Go / No-Go recommendation per phase.

| Dimension | Weight | Raw Score | Weighted Score | Notes |
|-----------|--------|-----------|---------------|-------|
| Data Dictionary Completeness | 15% | 8 | 1.20 | 22 confirmed tables, 6 views; 7 inferred tables unresolved |
| Domain Model Coverage | 15% | 9 | 1.35 | All 10 BCs mapped; aggregates and invariants documented |
| API Contract Coverage | 15% | 9 | 1.35 | 76 endpoints specified; all with security, schema, business rules |
| Business Rule Completeness | 15% | 8 | 1.20 | BR-01–BR-140 extracted; HOH defect and 7 gaps noted |
| Security Architecture | 10% | 6 | 0.60 | 10 gaps identified; critical gaps (key-in-DB) unresolved |
| Defect Identification | 10% | 9 | 0.90 | All 8 defects documented with remediation rules |
| NFR Specification | 5% | 9 | 0.45 | Full performance, availability, compliance NFRs defined |
| Technology Blueprint | 5% | 7 | 0.35 | Multi-option; no final stack selected (ADRs pending) |
| Test Strategy | 5% | 6 | 0.30 | Stubs and coverage targets defined; no test harness yet |
| Oracle Migration Risk | 5% | 5 | 0.25 | CONNECT BY, MEDIAN, UTL_SMTP migration paths defined but untested |

**Total: 71 / 100**

---

## 2. Readiness by Bounded Context

| BC | Name | Readiness | Confidence | Blockers |
|----|------|-----------|-----------|---------|
| BC-01 | Employee Identity | HIGH | Evidence-based | None — proceed |
| BC-02 | Compensation | MEDIUM | Evidence-based | HOH tax defect; no rollback procedure; tax bracket data needed |
| BC-03 | Leave Management | MEDIUM-HIGH | Evidence-based | Carry-forward logic unimplemented; PTO payout unimplemented |
| BC-04 | Performance | MEDIUM-HIGH | Evidence-based | Calibration write path gap; CALIBRATING status incomplete |
| BC-05 | Benefits | MEDIUM | Evidence-based | ADP field layout confirmed; NACHA still absent |
| BC-06 | Security | MEDIUM | Partial (USER_CREDENTIALS inferred) | Critical: key-in-DB; no session invalidation; USER_CREDENTIALS DDL unconfirmed |
| BC-07 | Org Structure | HIGH | Evidence-based | CONNECT BY replacement strategy defined |
| BC-08 | Notifications | MEDIUM-HIGH | Evidence-based | SMS/IN_APP handlers unimplemented; retry logic absent |
| BC-09 | Integration | LOW-MEDIUM | Evidence-based | NACHA unimplemented; no ACL on feeds |
| BC-10 | Reporting | LOW | Inferred | All tables inferred; no DDL confirmed |

---

## 3. Risk Register

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|-----------|
| RISK-001 | HOH $0 tax in production during parallel run | MEDIUM | HIGH | Fix before Phase 3 deploy; tax specialist review mandatory |
| RISK-002 | Inferred tables (7) may have divergent DDL when confirmed | MEDIUM | MEDIUM | Confirm DDL before generating migrations; hold ART-001 for these tables |
| RISK-003 | Oracle CONNECT BY replacement degrades under load for large orgs | LOW | MEDIUM | Pre-compute org tree; Redis cache; load test at 5,000 employees |
| RISK-004 | AES key migration from SYSTEM_CONFIG to KMS may break decryption of legacy SSN/bank data | HIGH | CRITICAL | Decrypt all legacy data with old key, re-encrypt with new KMS key before cutover |
| RISK-005 | ADP fixed-width format undocumented — positions 105–130 inferred | MEDIUM | HIGH | Obtain official ADP spec; validate with test enrollment records |
| RISK-006 | USER_CREDENTIALS table structure unknown — auth migration may surface schema surprises | MEDIUM | HIGH | DBA confirms DDL before Phase 1 |
| RISK-007 | Oracle MEDIAN() / SYS_CONNECT_BY_PATH used in 3 views — no equivalent tested | LOW | LOW | PostgreSQL PERCENTILE_CONT validated in migration spike |
| RISK-008 | No payroll rollback procedure exists — incorrect run may be unrecoverable | MEDIUM | HIGH | Implement rollback procedure before first production payroll run |
| RISK-009 | NOCACHE sequence contention under concurrent hire events | LOW (small org) | LOW | Resolved by default DB sequence caching in target |
| RISK-010 | NACHA implementation absent — direct deposit impossible | HIGH | MEDIUM | Phased: issue paper checks until NACHA implemented in Phase 3 |

---

## 4. Gate Status Summary

| Gate | Status | Blocking |
|------|--------|---------|
| VG-01 Data Dictionary Completeness | PARTIAL — 7 inferred tables unresolved | For those tables only |
| VG-02 Domain Model Completeness | PASS | — |
| VG-03 API Contract Completeness | PASS | — |
| VG-04 Business Rule Mapping | PASS for confirmed BCs; PARTIAL for BC-10 | BC-10 only |
| VG-05 Security Architecture Review | NOT STARTED — human sign-off required | Blocks Phase 1 deployment |
| VG-06 Migration Script Dry-Run | NOT STARTED | Blocks data migration |
| VG-07 Test Coverage Gate | NOT STARTED | Blocks each phase promotion |
| VG-08 NFR Validation | NOT STARTED | Blocks production |

---

## 5. Pre-Generation Action Items

The following actions must be completed before the corresponding generation phase begins:

### Before Phase 1 Generation
| ID | Action | Owner | Priority |
|----|--------|-------|---------|
| ACT-001 | Confirm USER_CREDENTIALS DDL with DBA | DBA | P0 |
| ACT-002 | Obtain KMS service credentials; configure for Phase 1 auth | Security Architect | P0 |
| ACT-003 | Security sign-off on RBAC matrix (Doc 13 §3.2) | Security Architect | P0 |
| ACT-004 | Confirm TERMINATION_CODES lookup table DDL | DBA | P1 |
| ACT-005 | Select target database (ADR-002) | Architecture Board | P0 |
| ACT-006 | Select authentication provider (ADR-003) | Architecture Board | P0 |

### Before Phase 2 Generation
| ID | Action | Owner | Priority |
|----|--------|-------|---------|
| ACT-007 | Confirm carry-forward policy with HR (days cap, same leave type vs any) | HR Policy Owner | P1 |
| ACT-008 | Confirm PTO payout calculation (full balance vs capped) | HR Policy Owner + Legal | P1 |
| ACT-009 | Obtain official ADP benefits feed specification document | Benefits Administrator | P1 |

### Before Phase 3 Generation
| ID | Action | Owner | Priority |
|----|--------|-------|---------|
| ACT-010 | Engage payroll tax specialist to validate HOH fix and all brackets | Payroll Specialist | P0 |
| ACT-011 | Obtain NACHA ACH spec v2; confirm bank origination agreement | Treasury | P0 |
| ACT-012 | Confirm all RPT_* table DDL for BC-10 | DBA | P1 |
| ACT-013 | Design payroll rollback procedure with Payroll Manager | Payroll Manager | P0 |

---

## 6. Overall Recommendation

**Conditional Go — Phase 1 may begin after ACT-001 through ACT-006 are resolved.**

Phase 2 and Phase 3 are blocked on their respective action items. Phase 3 (payroll) carries the highest financial and compliance risk and must not enter production without tax specialist sign-off and a parallel-run of at least two full pay cycles against the legacy system.

BC-10 (Reporting) should be considered a Phase 4 effort; insufficient confirmed data to generate with confidence.

---

=== DOCUMENT: 18_DEPLOYMENT_ARCHITECTURE.md ===

# 18 — Deployment Architecture
**System:** Acme Corporation HRMS
**Version:** 1.0
**Target:** Cloud-hosted (cloud-provider agnostic; AWS, Azure, and GCP equivalents noted). Container-native.

---

## 1. Environment Strategy

| Environment | Purpose | Data | Parity to Prod |
|-------------|---------|------|---------------|
| `dev` | Developer daily work | Synthetic data only | Low — fast-cycle |
| `test` | Automated CI pipeline | Synthetic + anonymised subset | Medium |
| `staging` | Pre-production validation; NFR testing | Anonymised production copy | HIGH — must match prod topology |
| `production` | Live system | Real data | — |

**Data governance:**
- PII must NEVER appear in dev or test environments
- Staging uses a fully anonymised copy generated by an automated anonymisation pipeline (SSN, bank data, DOB replaced with realistic but non-real values)

---

## 2. Container Architecture

### 2.1 Application Container

```dockerfile
# Multi-stage build example (language-agnostic description)
# Stage 1: Build
#   - Copy source
#   - Install dependencies
#   - Compile / package
# Stage 2: Runtime
#   - Non-root user (UID 1000)
#   - Distroless or alpine base
#   - Copy compiled artefact only
#   - Health check: GET /health
#   - Expose port 8080 (HTTP)
#   ENTRYPOINT ["app-binary"]
```

**Container requirements:**
- Non-root user; no privilege escalation
- Read-only filesystem where possible; explicit writable volumes for temp files
- No secrets in image layers; secrets injected via environment or mounted volume at runtime
- Image signed and scanned for CVEs before push to registry

### 2.2 Container Registry

- All images stored in a private registry (AWS ECR, GCR, ACR, or Docker Hub private)
- Image tags: `{semver}-{git-sha}` (e.g. `1.2.3-a4f9b2c`); never `latest` in non-dev environments
- Retention policy: keep last 10 images per tag prefix; clean up dev images after 30 days

---

## 3. Kubernetes Deployment

### 3.1 Namespace Layout

```
hrms-prod          # Production workloads
hrms-staging       # Staging
hrms-test          # Automated test runs
hrms-monitoring    # Prometheus, Grafana, Alertmanager
hrms-infra         # Redis, migration jobs (if self-hosted)
```

### 3.2 Application Deployment

```yaml
# Deployment (descriptive — actual YAML generated from manifest)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hrms-api
  namespace: hrms-prod
spec:
  replicas: 3                    # Minimum; HPA scales to 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    spec:
      containers:
        - name: hrms-api
          image: registry/hrms-api:{tag}
          ports:
            - containerPort: 8080
          readinessProbe:
            httpGet: { path: /health/ready, port: 8080 }
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet: { path: /health/live, port: 8080 }
            initialDelaySeconds: 30
            periodSeconds: 10
          resources:
            requests: { cpu: "250m", memory: "512Mi" }
            limits:   { cpu: "1000m", memory: "1Gi" }
          env:
            - name: DB_URL
              valueFrom:
                secretKeyRef: { name: hrms-db-secret, key: url }
            - name: KMS_KEY_ID
              valueFrom:
                secretKeyRef: { name: hrms-kms-secret, key: key_id }
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            readOnlyRootFilesystem: true
            allowPrivilegeEscalation: false
```

### 3.3 Horizontal Pod Autoscaler

```yaml
# HPA targets 60% CPU utilisation; scales 3–10 replicas
minReplicas: 3
maxReplicas: 10
metrics:
  - type: Resource
    resource:
      name: cpu
      target: { type: Utilization, averageUtilization: 60 }
  - type: Resource
    resource:
      name: memory
      target: { type: Utilization, averageUtilization: 70 }
```

### 3.4 Pod Disruption Budget

```yaml
# Ensures at least 2 replicas remain available during node maintenance
minAvailable: 2
```

---

## 4. Ingress and API Gateway

```
Internet
  │ HTTPS (443)
  ▼
CDN / WAF (CloudFront, Cloudflare, or equivalent)
  │ — OWASP ruleset; rate limiting; DDoS protection
  ▼
Load Balancer (cloud-native; TLS termination)
  │ HTTP (internal)
  ▼
Ingress Controller (Nginx Ingress / AWS ALB Ingress)
  │
  ├─ /api/v1/* → hrms-api Service (ClusterIP, port 8080)
  └─ /* → hrms-frontend Service (ClusterIP, port 3000)
```

**TLS:** Certificates managed by cert-manager + Let's Encrypt (public) or internal PKI (private).

**Rate limiting:** Applied at WAF layer (coarse) and API gateway layer (per-user, per-endpoint as per Document 13 §6.1).

---

## 5. Database Deployment

### 5.1 PostgreSQL Topology (Production)

```
                    ┌──────────────────────┐
                    │   Primary (writer)   │
                    │   PostgreSQL 16      │
                    │   Multi-AZ           │
                    └───────┬──────────────┘
                            │ Synchronous replication
               ┌────────────┘
               ▼
   ┌──────────────────────────┐
   │   Read Replica (reader)  │
   │   Async replication      │
   │   Used for: reports,     │
   │   dashboards, exports    │
   └──────────────────────────┘
```

**Failover:** Automatic promotion of synchronous replica; < 30-second RTO (meets AVAIL-003).
**Backups:** Continuous WAL archiving + daily base backup; 30-day retention; PITR to any point.
**Connection pooling:** PgBouncer in transaction mode in front of primary; max 100 server connections; app instances use pool (max 20 connections per pod × 3 pods = stays well under DB max_connections).

### 5.2 Database Migration Execution

```
Kubernetes Job: hrms-db-migrate
  - Runs as init job before application deployment
  - Image: flyway:{version}
  - Mounts migration scripts from ConfigMap or image layer
  - Fails deployment if migration fails (blocking pre-condition)
  - Idempotent: Flyway checksums prevent re-run
```

---

## 6. Caching Layer

```
Redis 7 Cluster (3 primary + 3 replica shards for HA)
  │
  ├── Cache DB 0: Application cache (org chart, SYSTEM_CONFIG, tax brackets)
  │     TTL: org chart 5 min; config 60 min; tax brackets 24 h
  ├── Cache DB 1: Session management (token version counter per employee)
  │     TTL: aligned to JWT access token lifetime (1 h)
  └── Cache DB 2: Rate limiting counters
        TTL: per rate-limit window (15 min for login; 1 min for API)
```

**Failover:** Redis Sentinel or Redis Cluster native failover; < 5 seconds.

---

## 7. Storage

| Purpose | Solution | Retention | Encryption |
|---------|---------|-----------|-----------|
| GL export files | Object storage (S3/GCS/Blob) | 7 years | SSE-KMS |
| ADP benefits files | Object storage | 7 years | SSE-KMS |
| NACHA ACH files | Object storage | 7 years | SSE-KMS |
| Application logs | Log aggregation service (CloudWatch Logs, Loki) | 1 year | At-rest encryption |
| Audit logs | DB table (partitioned) + object storage archive | 7 years | DB encryption |
| DB backups | Cloud-native backup (RDS/CloudSQL) | 30 days PITR | SSE-KMS |

---

## 8. Secret Management

```
Secrets flow:
  KMS → generates/stores master keys
  Vault or Secrets Manager → stores app secrets (DB password, SMTP creds, API keys)
  Kubernetes ExternalSecrets operator → syncs secrets into K8s Secrets
  Pods → mount K8s Secrets as env vars or files
  Secrets never in code, never in ConfigMaps, never in Docker images
```

**Secret rotation:** DB passwords rotated every 90 days via automated rotation in Secrets Manager; KMS DEK rotated annually.

---

## 9. CI/CD Pipeline

```
Developer push → Git PR
  │
  ├── Pre-merge checks (automated):
  │     SAST scan (Semgrep / SonarQube)
  │     Dependency CVE scan (Snyk / Trivy)
  │     Unit tests + coverage gate (VG-07)
  │     Build Docker image
  │
  ├── Merge to main → Build pipeline:
  │     Run integration tests against test environment
  │     Migration dry-run (VG-06)
  │     Push image to registry (tagged with semver + SHA)
  │
  └── Deploy pipeline (staged):
        Deploy to staging (automated)
        Run smoke tests
        Run performance tests (PERF-001–PERF-008 subset)
        Manual approval gate → Deploy to production
        Canary deployment: 5% traffic → 20% → 100% (over 30 min)
        Auto-rollback on error rate spike > 2%
```

---

## 10. Health Check Endpoints

| Endpoint | Purpose | Response |
|----------|---------|---------|
| `GET /health/live` | Liveness: is the process alive? | 200 OK `{"status":"UP"}` |
| `GET /health/ready` | Readiness: can the pod accept traffic? | 200 OK if DB+Redis reachable; 503 if not |
| `GET /metrics` | Prometheus metrics scrape | 200 OK (internal network only; not exposed externally) |

---

## 11. Disaster Recovery Runbook (Summary)

| Scenario | Detection | Response | RTO |
|----------|-----------|----------|-----|
| Pod crash | K8s liveness probe fails → pod restarted | Automatic restart; HPA maintains replica count | < 1 min |
| Node failure | K8s reschedules pods to healthy nodes | Automatic; PDB ensures ≥ 2 replicas | < 2 min |
| DB primary failure | Synchronous replica promoted | Automatic failover via RDS Multi-AZ or Patroni | < 30 sec |
| Region failure | DNS failover to DR region | Manual approval → automated DNS switch | < 4 hours |
| Data corruption | Detected via application error rate spike | Restore from PITR backup; replay WAL to clean point | < 1 hour |
| Secrets compromise | Vault audit alert | Rotate all affected secrets; invalidate all sessions; security incident declared | < 30 min for rotation |

---

=== DOCUMENT: 19_FRONTEND_ARCHITECTURE.md ===

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

=== DOCUMENT: 20_UI_UX_SPECIFICATION.md ===

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
