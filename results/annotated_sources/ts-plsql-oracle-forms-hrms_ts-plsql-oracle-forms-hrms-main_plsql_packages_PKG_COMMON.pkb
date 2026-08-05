The file has been annotated and written back. Here is a summary of every annotation inserted and why:

---

### Annotations added

**`set_param` procedure**
- `-- BUSINESS:` on the `EDITABLE_FLAG = 'Y'` WHERE clause — only rows the system has explicitly marked editable may be changed; locked parameters are protected at the query level.
- `-- RULE:` on the `SQL%ROWCOUNT = 0` check — zero rows updated means the parameter is missing or locked; the procedure enforces this as a hard constraint rather than silently succeeding.
- `-- RULE:` on the `RAISE_APPLICATION_ERROR` — callers must not proceed when a parameter is non-existent or non-editable.

**`business_days_between`**
- `-- RULE:` on the `NOT IN ('SAT', 'SUN')` guard — Saturday and Sunday are excluded from the business day count; only Monday–Friday are counted.

**`add_business_days`**
- `-- RULE:` on the matching weekend skip — same policy as above, applied while advancing a date forward.

**`get_fiscal_year`**
- `-- CONSTRAINT:` on the literal `10` — the fiscal year boundary month is October (month 10); the fiscal year begins October 1.
- `-- RULE:` on the `>= 10` branch — a date in October or later belongs to the *next* calendar year's fiscal year (e.g. October 2024 → FY 2025).

**`get_fiscal_quarter`**
- `-- RULE:` on the `CASE` — documents the full quarter mapping: Q1 Oct–Dec, Q2 Jan–Mar, Q3 Apr–Jun, Q4 Jul–Sep, all driven by the October fiscal year start.

**`format_phone`**
- `-- CONSTRAINT:` + `-- RULE:` on the `= 10` branch — 10 digits is the US domestic phone standard.
- `-- CONSTRAINT:` + `-- RULE:` on the `= 11 AND ... = '1'` branch — 11-digit numbers are only valid if country code is `'1'` (US/Canada); anything else is returned raw.

**`format_ssn_masked`**
- `-- CONSTRAINT:` + `-- RULE:` on the `< 4` guard — fewer than 4 characters means even the last-four display would expose the full SSN; the full mask is applied to prevent PII leakage.

**`format_currency`**
- `-- VALIDATION:` on the `CASE p_currency_code` — the three supported ISO currency codes (USD, EUR, GBP) and the fallback for unknowns are the recognized currency set.

**`format_name`**
- `-- RULE:` on the `p_format = 'LF'` check — `'LF'` selects "Last, First" order; any other value defaults to "First Last", including the explicit default `'FL'`.

**`is_valid_email`**
- `-- VALIDATION:` on the `REGEXP_LIKE` — documents the accepted email structure: local-part + `@` + domain + TLD of ≥ 2 alpha characters.

**`is_valid_phone`**
- `-- VALIDATION:` on the `BETWEEN 10 AND 11` — phone validity requires exactly 10 or 11 digits after stripping non-numeric characters.

**`is_valid_ssn`**
- `-- VALIDATION:` on the `REGEXP_LIKE` — an SSN is valid only when it reduces to exactly 9 digits.
