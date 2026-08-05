The file has been annotated. Here is a summary of every annotation added and why:

---

### `calculate_business_days`
- **BUSINESS** on the `HOLIDAYS` query — documents that only active holidays apply, and that a NULL `LOCATION_CODE` means the holiday is global (applies to all offices).

---

### `check_leave_overlap`
- **BUSINESS** on the `STATUS IN ('PENDING', 'APPROVED')` filter — clarifies that CANCELLED and REJECTED requests are intentionally invisible to the overlap check.

---

### `submit_leave_request`
| Location | Tag | Rule documented |
|---|---|---|
| `EMPLOYMENT_STATUS = 'ACTIVE'` query | BUSINESS | Only active employees can submit leave |
| `NO_DATA_FOUND` on employee | RULE + RAISE | Employee must exist and be active |
| `ACTIVE_FLAG = 'Y'` on leave type | BUSINESS | Only active leave types are selectable |
| `NO_DATA_FOUND` on leave type | RULE + RAISE | Leave type must exist and be active |
| `MIN_TENURE_DAYS > 0` outer IF | RULE | Some leave types have a tenure gate |
| `HIRE_DATE` tenure check | RULE + RAISE | Employee must meet tenure threshold |
| `p_start_date > p_end_date` | RULE + RAISE | Date range must be logically ordered |
| `p_start_date < TRUNC(SYSDATE)` | RULE | Backdate window is enforced |
| `> 5` threshold | CONSTRAINT + RAISE | Hard limit of 5 calendar days for backdating |
| `p_half_day_flag = 'Y'` | RULE | Half-day always counts as 0.5 regardless of date range |
| `v_total_days <= 0` | RULE + RAISE | Date range must contain at least one working day |
| `check_leave_overlap` call | RULE + RAISE | No concurrent PENDING/APPROVED leave for same dates |
| `ACCRUAL_FLAG = 'Y'` | RULE | Balance check only applies to accrual-based leave |
| `v_balance < v_total_days` | RULE + RAISE | Insufficient balance blocks request |
| `REQUIRES_APPROVAL` CASE in INSERT | VALIDATION | Controls whether request starts PENDING or APPROVED |
| Manager notification IF | RULE | Notification sent only when approval required and manager exists |
| Auto-approve IF | RULE | Non-approval leave types are auto-approved immediately |

---

### `approve_leave_request`
- **RULE + RAISE** on `STATUS != 'PENDING'` — only PENDING requests can be approved.

### `reject_leave_request`
- **RULE + RAISE** on `STATUS != 'PENDING'` — only PENDING requests can be rejected.

### `cancel_leave_request`
- **RULE + RAISE** on `STATUS NOT IN ('PENDING', 'APPROVED')` — only live requests can be cancelled.
- **RULE** on `STATUS = 'PENDING'` branch — pending balance is released.
- **RULE** on `STATUS = 'APPROVED'` branch — used balance is reversed.

### `get_leave_balance`
- **VALIDATION** on `NVL(v_balance, 0)` — a NULL formula result is treated as zero days available.

### `initialize_balances`
- **BUSINESS** on `ACTIVE_FLAG = 'Y'` — only active leave types get balance rows created.

### `run_monthly_accrual`
- **BUSINESS** on the employee cursor `ACTIVE` + `ACTIVE_FLAG = 'Y'` — two separate active flags must both be true for accrual to run.
- **BUSINESS** on the leave type cursor — accrual only runs for monthly-frequency, accrual-enabled, active leave types.
- **RULE** on `MIN_TENURE_DAYS` check — employees must have sufficient tenure before accruing.
- **RULE** on `MAX_BALANCE` check — accrual is capped to avoid exceeding the configured ceiling.
- **CONSTRAINT** on `MOD(..., 100)` — batch commits every 100 employees to manage transaction size.

### `process_carryover`
- **BUSINESS** on the balance cursor `> 0` filter — only employees with a positive remaining balance are eligible for carryover.
- **RULE** on `CARRYOVER_MAX` cap — balances above the carryover ceiling are forfeited.
- **VALIDATION** on the `CARRYOVER_EXPIRY_DT` CASE — expiry date is only set when the leave type defines one; otherwise carried days never expire.

### `expire_carryover`
- **RULE** on the UPDATE — expired carryover days are forfeited via the adjustment column; only records with a positive remaining carryover amount are touched.

### `get_pending_requests`
- **BUSINESS** on `STATUS = 'PENDING'` and `APPROVER_EMP_ID` filter — the cursor is scoped to the specific approver's pending queue only.

### `get_team_calendar`
- **BUSINESS** on `STATUS IN ('APPROVED', 'TAKEN')` — calendar shows only confirmed/completed leave; pending and rejected requests are hidden.
