The annotated file has been written. Here is a summary of every annotation inserted and the reasoning behind each:

---

### Annotations added

**`generate_gl_journal` — GL feed cursor WHERE clause**

| Tag | Location | Rule documented |
|-----|----------|-----------------|
| `-- BUSINESS:` | `pd.STATUS != 'ERROR'` | Only non-error payroll detail lines are included in the GL feed. ERROR lines are excluded to prevent bad amounts reaching the general ledger. |
| `-- BUSINESS:` | `pe.GL_ACCOUNT_CODE IS NOT NULL` | Only pay elements that have a mapped GL account code are included; unmapped elements are silently dropped from the journal. |
| `-- RULE:` | `IF rec.ELEMENT_TYPE = 'EARNING'` | EARNING-type elements are posted as debit (expense) entries; all other types (deductions, taxes) are posted as credit (liability) entries. This is the core double-entry accounting rule for payroll GL posting. |

**`export_benefits_feed` — ADP benefits cursor**

| Tag | Location | Rule documented |
|-----|----------|-----------------|
| `-- BUSINESS:` | `d.ACTIVE_FLAG = 'Y'` | Only dependents flagged as active are sent to ADP; removed or deactivated dependents are excluded. |
| `-- BUSINESS:` | `e.EMPLOYMENT_STATUS = 'ACTIVE'` | Only ACTIVE employees are included in the benefits feed; terminated or inactive employees are excluded from the ADP extract. |
| `-- VALIDATION:` | `NVL(..., ' ')` block | Every field substitutes a single space for NULL so that ADP's fixed-width parser receives a correctly padded record rather than a short or malformed line. |

**`import_time_attendance` — line-skip logic**

| Tag | Location | Rule documented |
|-----|----------|-----------------|
| `-- RULE:` | `IF v_line IS NOT NULL AND SUBSTR(v_line, 1, 1) != '#'` | Lines that are NULL or start with `#` are treated as blank separators or comment lines and are skipped — they are not counted as imported records or errors. |

---

No annotations were added to `sync_org_structure` (stub/placeholder with no logic) or `get_integration_status` (pure parameter lookup with no business conditions).
