│       ├── Compute taxable_gross = period_gross - SUM(pretax deduction amounts)
│       │       pretax_total = 401k_amount + medical_amt + dental_amt + vision_amt + hsa_amt
│       │       taxable_gross = period_gross - pretax_total
│       │
│       ├── Compute federal income tax (CRITICAL DEFECT: hard-coded 2024 brackets)
│       │       YTD_GROSS retrieved from SUM(pd.AMOUNT) WHERE pd.ELEMENT_ID=100 for prior periods
│       │       Bracket logic via nested IF/ELSIF on filing_status:
│       │         SINGLE: 10%/12%/22%/24%/32%/35%/37% brackets applied
│       │         MARRIED_FILING_JOINTLY: separate bracket set applied
│       │         HEAD_OF_HOUSEHOLD: branch EXISTS in CASE but falls through to 0
│       │                            *** SEC-009 / CRITICAL DEFECT: HOH employees pay $0 federal tax ***
│       │         MARRIED_FILING_SEPARATELY: standard bracket applied
│       │       Result: INSERT PAYROLL_DETAILS ELEMENT_ID=200 (FEDERAL_TAX), AMOUNT=federal_tax_amt
│       │
│       ├── Compute state income tax
│       │       flat-rate lookup: state_rate hard-coded per 2-char state code
│       │       state_tax = taxable_gross * state_rate
│       │       INSERT PAYROLL_DETAILS ELEMENT_ID=210 (STATE_TAX), AMOUNT=state_tax_amt
│       │       *** DEFECT: no multi-state logic; employees with mid-year state change get wrong rate ***
│       │
│       ├── Compute FICA — Social Security
│       │       YTD_SS_WAGES = SUM of prior PAYROLL_DETAILS rows for SS element
│       │       ss_wage_base = 168600 (hard-coded constant, 2024 value)
│       │       remaining_ss_wages = GREATEST(0, ss_wage_base - YTD_SS_WAGES)
│       │       ss_taxable = LEAST(taxable_gross, remaining_ss_wages)
│       │       ss_tax = ss_taxable * 0.062
│       │       INSERT PAYROLL_DETAILS ELEMENT_ID=220 (SOCIAL_SECURITY), AMOUNT=ss_tax
│       │       *** ORDERING CONTRACT: INSERT to PAYROLL_DETAILS happens BEFORE YTD call reads it
│       │           so current-period gross is included in YTD — confirmed via comment in source ***
│       │
│       ├── Compute FICA — Medicare
│       │       medicare_base = 200000 (additional Medicare threshold, hard-coded)
│       │       medicare_tax = taxable_gross * 0.0145
│       │       IF YTD_GROSS > medicare_base THEN medicare_tax += (taxable_gross * 0.009) END IF
│       │       INSERT PAYROLL_DETAILS ELEMENT_ID=230 (MEDICARE), AMOUNT=medicare_tax
│       │
│       ├── Compute post-tax deductions
│       │       Roth 401k, garnishments, charitable contributions (from DEDUCTION_RECORDS)
│       │       Each deduction: INSERT PAYROLL_DETAILS with respective ELEMENT_ID
│       │
│       ├── Compute net pay
│       │       net_pay = period_gross
│       │                 - pretax_total
│       │                 - federal_tax_amt
│       │                 - state_tax_amt
│       │                 - ss_tax
│       │                 - medicare_tax
│       │                 - SUM(post_tax_deductions)
│       │       UPDATE PAYROLL_RUNS SET TOTAL_GROSS = TOTAL_GROSS + period_gross,
│       │                               TOTAL_NET   = TOTAL_NET   + net_pay,
│       │                               TOTAL_DEDUCTIONS = TOTAL_DEDUCTIONS + (period_gross - net_pay)
│       │       *** CONCURRENCY DEFECT: row-level UPDATE races if parallel sessions run payroll;
│       │           no SELECT FOR UPDATE or DBMS_LOCK guard observed ***
│       │
│       └── END cursor loop — COMMIT (single transaction for all employees)
│           *** RISK: one bad employee row rolls back entire payroll run ***
│           *** MISSING: SAVEPOINT per employee not implemented ***
│
├── [STEP 4] Status transition → CALCULATED
│   PKG_PAYROLL.submit_payroll_run(p_run_id)
│   UPDATE PAYROLL_RUNS SET STATUS = 'CALCULATED', CALCULATED_DATE = SYSDATE
│   Notification trigger fires → NOTIFICATION_QUEUE row inserted (EMAIL, payroll_summary)
│
├── [STEP 5] Approval gate (UI: PAYROLL_FORM)
│   HR Manager (Grade ≥ 8) reviews run totals on PAYROLL_FORM
│   APPROVE action calls PKG_PAYROLL.approve_payroll_run(p_run_id, p_approved_by)
│   UPDATE PAYROLL_RUNS SET STATUS='APPROVED', APPROVED_BY=p_approved_by, APPROVED_DATE=SYSDATE
│   Gap: no escalation path if approver is unavailable; no delegation logic observed
│
├── [STEP 6] GL Journal generation
│   PKG_PAYROLL.generate_gl_feed(p_run_id) → writes UTL_FILE to PAYROLL_EXPORT dir
│   File format: pipe-delimited, record types H / D / T
│     H: journal header (batch_id, period, source='HRMS_PAYROLL')
│     D: detail per GL account code (COST_CENTER + ACCOUNT_CODE from EMPLOYEES)
│     T: trailer (record count, total_debit, total_credit)
│   *** DEFECT: balancing check uses SUM(AMOUNT) without sign convention guard;
│       if any deduction is posted as positive, file will appear out of balance ***
│   Status: UPDATE PAYROLL_RUNS SET STATUS='GL_GENERATED'
│
├── [STEP 7] ACH / Direct Deposit feed
│   *** DESIGNED BUT UNIMPLEMENTED: NACHA prenote pattern referenced in comments ***
│   *** MISSING: no PKG_PAYROLL procedure generates NACHA file ***
│   *** MISSING: BANK_ACCOUNT_NUMBER / BANK_ROUTING_NUMBER exist in EMPLOYEES table
│       (AES-256 encrypted) but no decryption+format procedure written ***
│   Current workaround: UNKNOWN — likely manual export outside system
│
└── [STEP 8] Payslip notification
    PKG_NOTIFICATION.process_notification_queue fires
    EMAIL sent via UTL_SMTP per employee (ELEMENT_ID lookup for net pay amount)
    *** DEFECT: queue processor is synchronous loop; no parallel dispatch;
        5000-employee org = 5000 sequential SMTP calls in single session ***

GAP SUMMARY — Process 2:
  G1: HEAD_OF_HOUSEHOLD federal tax = $0 (CRITICAL)
  G2: SAVEPOINT per employee missing — one failure rolls back all
  G3: NACHA/ACH file generation absent — direct deposit unimplemented
  G4: GL balance sign-convention defect
  G5: DBMS_SCHEDULER DDL not provided — scheduler existence inferred from comments only
  G6: Multi-state tax not supported