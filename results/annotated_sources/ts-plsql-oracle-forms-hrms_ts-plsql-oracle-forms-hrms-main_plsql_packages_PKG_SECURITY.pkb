The file has been annotated. Here is a summary of every comment inserted and why:

---

### `c_session_timeout_min` (line 8)
- **CONSTRAINT** — the literal `30` is a business threshold; sessions older than this are killed.

---

### `authenticate` — employee lookup query (line 45)
- **BUSINESS** — the `EMPLOYMENT_STATUS = 'ACTIVE'` filter encodes the rule that only active employees may log in.

### `authenticate` — `NO_DATA_FOUND` handler (line 50)
- **RULE** — the generic error message is an intentional design decision to prevent username enumeration, so it warrants documenting.

### `authenticate` — `TOO_MANY_ROWS` handler (line 53)
- **BUSINESS** — `MIN(EMP_ID)` tie-breaking when multiple active employees share an email is an explicit data-quality policy.

---

### `is_session_valid` — status check (line 109)
- **RULE** — only `'ACTIVE'` sessions pass; any other value (CLOSED, EXPIRED, etc.) is treated as invalid.

### `is_session_valid` — timeout check (line 114)
- **RULE** — the 30-minute inactivity rule tied to `c_session_timeout_min`.

---

### `has_permission` — grade thresholds (lines 153, 157)
- **CONSTRAINT + RULE** pair for each of the two grade cutoffs (8 = full access, 5 = view-all).

### `has_permission` — module-specific rules (lines 162, 166)
- **RULE** for each universal-access carve-out: all employees can manage their own leave, all employees can view their own profile.

---

### `change_password` — three complexity guards (lines 218, 222, 226)
- **CONSTRAINT** on the minimum length literal `8`.
- **RULE + RAISE** pair for each of the three password policy checks (length, uppercase, digit) — both the guard condition and the error call are annotated since either one could be the point of future review.
