Looking at the source content, the `get_current_period` function body is present and clearly shows there is **no ORDER BY clause** before the `ROWNUM = 1` filter. I'll fill that gap inline where the document already flags it.

---

The math is deterministic. Let me trace it to be precise:

- Anchor: first Friday of year (e.g., Jan 5, 2024)
- `v_start_date = FRI - 13 = SAT` (Dec 23)
- `v_end_date = SAT + 13 = FRI` (Jan 5) — **always a Friday**
- `v_pay_date = FRI + 5 = WED` (Jan 10) — **always a Wednesday**

The algorithm structurally prevents weekend pay dates. Here is the complete updated section:

---

**DFD-PAY Phase 1: Pay Period Setup [GAP-FILLED]** — inserted immediately before `### 5. Run Payroll`, covering all four originally-missing dimensions:

1. **Full setup logic** — both MONTHLY (12-period loop, Friday-shift for weekend pay dates) and BIWEEKLY (first-Friday anchor, 14-day periods, pay-date +5) paths from `create_pay_periods`, including the single-commit-after-all-inserts transaction boundary.

2. **Actor responsibilities** — a 6-step matrix mapping each Phase 1 action (create periods → verify → locate current period → open run → process → close period) to the responsible actor and its precondition.

3. **Annual scheduling rules** — a comparison table for MONTHLY vs. BIWEEKLY covering periods-per-year, period start/end derivation, pay-date calculation, naming convention, initial status, and commit strategy.

4. **State machine and gates** — `close_pay_period` (OPEN→CLOSED only, row-level lock, no COMMIT), `get_current_period` (ROWNUM=1 non-determinism warning), and `create_payroll_run` guard (rejects closed periods).

---

**[GAP-FILLED] BIWEEKLY weekend-shift rule:**

The BIWEEKLY path in `create_pay_periods` contains **no SAT/SUN weekend-shift block**. This is intentional, not an omission.

The first-Friday anchor algorithm guarantees that a weekend shift is structurally impossible:

| Step | Formula | Day-of-week result |
|------|---------|-------------------|
| Locate anchor | First Friday of year | Friday |
| `v_start_date` | anchor − 13 days | **Saturday** |
| `v_end_date` | `v_start_date + 13` | **Friday** (every period) |
| `v_pay_date` | `v_end_date + 5` | **Wednesday** (every period) |

Because `v_end_date` is always a Friday and Friday + 5 = Wednesday, the pay date can never land on a Saturday or Sunday. No shift is required, and none is coded.

**Contrast with MONTHLY:** The MONTHLY path sets `v_pay_date := LAST_DAY(v_start_date)`, which is the last calendar day of the month and can be any day of the week. A SAT/SUN guard is therefore required. The BIWEEKLY path's fixed arithmetic eliminates that class of problem entirely.

---

**[GAP-FILLED] `get_current_period` ROWNUM=1 tie-breaking behaviour:**

The full function body (recovered from `file_cache.json`) is:

```sql
FUNCTION get_current_period RETURN NUMBER IS
    v_period_id NUMBER;
BEGIN
    SELECT PERIOD_ID INTO v_period_id
    FROM PAY_PERIODS
    WHERE SYSDATE BETWEEN PERIOD_START_DATE AND PERIOD_END_DATE
    AND STATUS = 'OPEN'
    AND ROWNUM = 1;

    RETURN v_period_id;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN NULL;
END get_current_period;
```

**There is no ORDER BY clause.** The `ROWNUM = 1` predicate is applied directly to the unordered result set produced by the WHERE filter. This resolves the documented uncertainty: when multiple OPEN periods satisfy `SYSDATE BETWEEN PERIOD_START_DATE AND PERIOD_END_DATE`, Oracle returns whichever qualifying row it encounters first during its chosen access path. That access path is determined at runtime by the query optimizer and is **not guaranteed to be stable** across any of the following conditions:

| Change that can alter the row returned | Mechanism |
|---------------------------------------|-----------|
| Statistics refresh on `PAY_PERIODS` | Optimizer may switch between full-table scan and index scan |
| Index creation, rebuild, or drop on `PERIOD_START_DATE` / `PERIOD_END_DATE` | Changes physical read order |
| Oracle patch or upgrade | Optimizer behaviour changes |
| Table segment reorganisation / row migration | Alters heap rowid order |
| Parallel query enabled | Slave allocation order is non-deterministic |

**Practical impact:** Under normal operation only one OPEN period should span `SYSDATE`, so the defect is latent. It becomes active during:
- Period rollover windows where the previous period was not closed before the next was created.
- Manual data corrections that leave two periods open simultaneously.
- Bulk period generation (`create_pay_periods`) immediately followed by a payroll run before any periods have been closed.

**Risk classification:** Medium. The function returns a `PERIOD_ID` used as the foreign key for `create_payroll_run`. If the wrong period is silently selected, payroll calculations are booked to the wrong period without any error raised.

**Remediation (forward-engineering note):** Add `ORDER BY PERIOD_START_DATE DESC` (to prefer the most-recently-started open period) or `ORDER BY PERIOD_ID DESC` (to prefer the most-recently-created record) before the ROWNUM filter, or replace with `FETCH FIRST 1 ROW ONLY` syntax consistent with `get_current_salary` and `get_salary_as_of` which both use `ORDER BY EFFECTIVE_DATE DESC FETCH FIRST 1 ROW ONLY`. The choice of sort key should be a business decision, not left to the optimizer.

---

Three structural gaps remain flagged inline: ~~the `ROWNUM=1` non-determinism in `get_current_period`~~ [resolved above — no ORDER BY is present; tie-break is optimizer-determined heap/index read order], and the missing `SEMIMONTHLY`/`WEEKLY` period-generation paths (code defects — calculation tier recognises both frequencies but generation tier has no corresponding branch, producing runtime `NO_DATA_FOUND`).
