=== CHUNK METADATA ===
Chunk: 09            (chunk count is budget-driven, not a fixed file count)
Type group: plsql-body
Expected files (1):
  1. [plsql-body] ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb (9047 chars written)
Total source content: 7017 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb ===

**IDENTITY:**
  KIND: package body
  PURPOSE: queues outbound notifications and delivers them asynchronously via SMTP, with retry and cancellation support

**STRUCTURES:**
  c_smtp_host — KIND: constant; TYPE: VARCHAR2(100)
  c_smtp_port — KIND: constant; TYPE: NUMBER
  c_from_address — KIND: constant; TYPE: VARCHAR2(100)
  c_from_name — KIND: constant; TYPE: VARCHAR2(100)

**METHODS:**
  **PROCEDURE send_notification(p_recipient_emp_id IN NUMBER DEFAULT NULL, p_recipient_email IN VARCHAR2 DEFAULT NULL, p_type IN VARCHAR2 DEFAULT 'EMAIL', p_subject IN VARCHAR2, p_body IN CLOB, p_priority IN NUMBER DEFAULT 5, p_reference_table IN VARCHAR2 DEFAULT NULL, p_reference_id IN NUMBER DEFAULT NULL, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L16-63]
  - What it does: Runs as an autonomous transaction [L27]. If no explicit recipient email was given but a recipient employee ID was, looks up EMAIL from EMPLOYEES by EMP_ID [L31-39]; if the employee isn't found, leaves the email NULL rather than failing. Inserts one row into NOTIFICATION_QUEUE with status 'PENDING' using the next value of SEQ_NOTIFICATION as the ID, then commits [L44-56].
  - Business rules: If no recipient email is resolvable (no email passed and no matching employee), the row is still queued with a NULL RECIPIENT_EMAIL [L37-38, L41]. Notification failures must never block the calling business operation — any exception is caught, rolled back, and only logged [L57-62].
  - Numbers & thresholds: p_priority defaults to 5 [L22]. Initial STATUS on insert is the literal string 'PENDING' [L52]. Default p_type is 'EMAIL' [L19].
  - Security & error handling: No access control beyond default Oracle privileges; p_user defaults to the current session USER [L25] and is recorded as CREATED_BY. On ANY exception (WHEN OTHERS), the autonomous transaction is rolled back and the error is logged via PKG_COMMON.log_error with SQLERRM, then execution continues silently (no re-raise) [L57-62].
  - Data in/out: Inputs — p_recipient_emp_id, p_recipient_email, p_type, p_subject, p_body, p_priority, p_reference_table, p_reference_id, p_user. Output/side effect — one row inserted into NOTIFICATION_QUEUE; commits independently of the caller's transaction (PRAGMA AUTONOMOUS_TRANSACTION).

  **PROCEDURE process_queue(p_batch_size IN NUMBER DEFAULT 50, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L70-143]
  - What it does: Intended to be invoked by a DBMS_SCHEDULER job every 5 minutes (per comment, not enforced in this file) [L68]. Selects up to p_batch_size PENDING, EMAIL-type notifications with a non-null recipient email, ordered by PRIORITY ascending then CREATED_DATE ascending [L78-86]. For each, opens an SMTP connection to c_smtp_host:c_smtp_port and sends a plain-text email via UTL_SMTP [L90-107], then marks the row SENT with SENT_DATE = SYSDATE [L110-113] and increments a running sent counter. On any per-row failure, marks the row FAILED with the truncated error message and increments RETRY_COUNT, increments a running failed counter, and attempts to close the SMTP connection, swallowing any error from that close [L117-133]. After the loop, commits once [L137], then logs a summary via PKG_COMMON.log_info only if at least one notification was sent or failed [L139-142].
  - Business rules: Only rows with STATUS='PENDING', NOTIFICATION_TYPE='EMAIL', and a non-null RECIPIENT_EMAIL are processed [L82-84]. Processing order is PRIORITY ascending, then CREATED_DATE ascending [L85]. A failure sending one notification does not stop processing of the remaining batch (per-row exception handler). Summary log is only written if v_sent > 0 OR v_failed > 0 [L139].
  - Numbers & thresholds: p_batch_size defaults to 50 [L71], used as FETCH FIRST p_batch_size ROWS ONLY [L86]. v_sent initialized to 0 [L75]; v_failed initialized to 0 [L76]. c_smtp_port = 25 (via c_smtp_port constant, used at L90). Error message truncated to 4000 characters via SUBSTR(SQLERRM, 1, 4000) [L122]. RETRY_COUNT incremented by 1 on failure (RETRY_COUNT = RETRY_COUNT + 1) [L123].
  - Security & error handling: SMTP host/port/from-address/from-name are hard-coded constants rather than read from SYSTEM_PARAMETERS (flagged in the file's own header comment, L6). Per-notification exceptions are caught individually so one bad row doesn't abort the batch; on failure the row is marked FAILED with the (truncated) SQLERRM and RETRY_COUNT bumped [L117-124]. An inner exception handler attempts UTL_SMTP.QUIT to close the connection and silently ignores any error doing so (WHEN OTHERS THEN NULL) [L129-133]. No input validation on p_batch_size.
  - Data in/out: Inputs — p_batch_size, p_user (p_user is accepted but not otherwise used in the body besides the log_info call). Outputs/side effects — UPDATEs NOTIFICATION_QUEUE rows to SENT or FAILED; sends outbound SMTP email; one COMMIT for the whole batch; writes an info log entry via PKG_COMMON.log_info when applicable.

  **PROCEDURE retry_failed(p_max_retries IN NUMBER DEFAULT 3, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L148-160]
  - What it does: Resets any FAILED notification whose RETRY_COUNT is still below p_max_retries back to PENDING and clears its ERROR_MESSAGE [L153-157], then commits [L159].
  - Business rules: Only rows with STATUS='FAILED' AND RETRY_COUNT < p_max_retries are eligible for retry [L156-157]; rows that have exhausted retries are left as FAILED.
  - Numbers & thresholds: p_max_retries defaults to 3 [L149].
  - Security & error handling: None — no exception handling in this procedure; p_user is accepted but unused in the body.
  - Data in/out: Inputs — p_max_retries, p_user (unused). Output/side effect — UPDATEs eligible NOTIFICATION_QUEUE rows to STATUS='PENDING', ERROR_MESSAGE=NULL; commits.

  **PROCEDURE cancel_notification(p_notification_id IN NUMBER, p_user IN VARCHAR2 DEFAULT USER)** [SOURCE: L165-174]
  - What it does: Sets a single notification's STATUS to CANCELLED, but only if it is currently PENDING [L170-173].
  - Business rules: Only PENDING notifications can be cancelled (NOTIFICATION_ID match AND STATUS='PENDING'); already-sent, failed, or already-cancelled rows are unaffected — the UPDATE simply matches zero rows.
  - Numbers & thresholds: None.
  - Security & error handling: None — no exception handling; no explicit COMMIT in this procedure (relies on caller's transaction); p_user is accepted but unused in the body.
  - Data in/out: Inputs — p_notification_id, p_user (unused). Output/side effect — UPDATEs the matching NOTIFICATION_QUEUE row's STATUS to 'CANCELLED'.

**DEPENDENCIES:**
  Data touched:
  - Reads: EMPLOYEES — EMAIL lookup by EMP_ID (send_notification, L33-35)
  - Reads: NOTIFICATION_QUEUE — PENDING/EMAIL rows with non-null recipient email, ordered by PRIORITY/CREATED_DATE (process_queue, L78-86)
  - Writes: NOTIFICATION_QUEUE — insert new queued notification (send_notification, L44-54)
  - Writes: NOTIFICATION_QUEUE — update STATUS/SENT_DATE on success, or STATUS/ERROR_MESSAGE/RETRY_COUNT on failure (process_queue, L110-124)
  - Writes: NOTIFICATION_QUEUE — update STATUS to PENDING and clear ERROR_MESSAGE for retry-eligible rows (retry_failed, L153-157)
  - Writes: NOTIFICATION_QUEUE — update STATUS to CANCELLED for a pending row (cancel_notification, L170-173)

  CALLS: PKG_COMMON.log_error | EVIDENCE: OBSERVED | SOURCE: L61-62
  CALLS: PKG_COMMON.log_info | EVIDENCE: OBSERVED | SOURCE: L140-141
  CALLS: SEQ_NOTIFICATION.NEXTVAL | EVIDENCE: OBSERVED | SOURCE: L50
  CALLS: UTL_SMTP.OPEN_CONNECTION | EVIDENCE: OBSERVED | SOURCE: L90
  CALLS: UTL_SMTP.HELO | EVIDENCE: OBSERVED | SOURCE: L91
  CALLS: UTL_SMTP.MAIL | EVIDENCE: OBSERVED | SOURCE: L92
  CALLS: UTL_SMTP.RCPT | EVIDENCE: OBSERVED | SOURCE: L93
  CALLS: UTL_SMTP.OPEN_DATA | EVIDENCE: OBSERVED | SOURCE: L95
  CALLS: UTL_SMTP.WRITE_DATA | EVIDENCE: OBSERVED | SOURCE: L96-105
  CALLS: UTL_SMTP.CLOSE_DATA | EVIDENCE: OBSERVED | SOURCE: L106
  CALLS: UTL_SMTP.QUIT | EVIDENCE: OBSERVED | SOURCE: L107
  CALLS: UTL_SMTP.QUIT | EVIDENCE: OBSERVED | SOURCE: L130
  CALLS: UTL_TCP.CRLF | EVIDENCE: OBSERVED | SOURCE: L97

  Config/env: c_smtp_host ('smtp.internal.company.com'), c_smtp_port (25), c_from_address ('hrms-noreply@company.com'), c_from_name ('HRMS System') — hard-coded in-package per the file's own header comment noting these "should be in SYSTEM_PARAMETERS" [L6-10].
  External integrations: Outbound SMTP mail delivery to smtp.internal.company.com:25 via UTL_SMTP/UTL_TCP (process_queue).

**GAPS:**
  SEQ_NOTIFICATION — sequence referenced but not defined in this file (EXTERNAL/UNKNOWN source).
  NOTIFICATION_QUEUE, EMPLOYEES — table structures not defined in this file (EXTERNAL/UNKNOWN schema, assumed from column usage).
  PKG_COMMON.log_error / log_info — external package, not analyzed here (NOT_ANALYZED).
  DBMS_SCHEDULER job that is said to call process_queue every 5 minutes is only referenced in a comment [L68]; the actual job definition is not in this file (UNRESOLVED).
  UTL_SMTP / UTL_TCP — Oracle built-in packages (EXTERNAL, not analyzed).

*[pipeline status — type: plsql-body · pass: correction · attempt: 2 · coverage: 100% (numbers 7/7 · procedures 4/4 · units 4/4 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 1
Files delivered: 1
  Full coverage on first pass: 0
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/plsql/packages/PKG_NOTIFICATION.pkb
  Still incomplete after max attempts: 0
Raw source: 7017 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===