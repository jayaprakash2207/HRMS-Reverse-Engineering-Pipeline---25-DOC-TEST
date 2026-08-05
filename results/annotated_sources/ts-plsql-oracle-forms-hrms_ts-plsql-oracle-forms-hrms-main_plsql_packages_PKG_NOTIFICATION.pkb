The annotated file has been written. Here is a summary of every annotation added and the reasoning behind each:

---

### Annotations added

| Location | Tag | Rule documented |
|---|---|---|
| `send_notification` — outer `IF` | `RULE` | Recipient resolution: email address is looked up from `EMPLOYEES` only when no direct address was provided but an employee ID was |
| `INSERT ... 'PENDING'` | `RULE` | Every newly queued notification starts in `PENDING` status — it is not delivered immediately |
| `process_queue` cursor `WHERE` clause | `BUSINESS` | Queue processor restricts to `PENDING` / `EMAIL` / non-null address records; other types and unresolved addresses are excluded |
| `ORDER BY PRIORITY ASC, CREATED_DATE ASC` | `RULE` | Lower numeric priority value = higher urgency; within the same priority, FIFO ordering applies |
| `STATUS = 'SENT'` update | `RULE` | Successful delivery stamps the record `SENT` with an actual timestamp for SLA audit purposes |
| `STATUS = 'FAILED'` update | `RULE` | SMTP failure marks the record `FAILED` and increments `RETRY_COUNT`; the record stays failed until `retry_failed` resets it |
| `retry_failed` — `p_max_retries DEFAULT 3` | `CONSTRAINT` | Maximum 3 retries is the operational policy; beyond that a notification is permanently abandoned in `FAILED` |
| `retry_failed` — `WHERE` clause | `RULE` | Only `FAILED` records below the retry cap are re-queued; permanently failed records are untouched |
| `cancel_notification` — `AND STATUS = 'PENDING'` | `RULE` | Cancellation is only valid while the notification is still `PENDING`; sent/failed/cancelled records are immune |

No existing code or comments were modified.
