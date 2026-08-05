The file has been annotated. Here is a summary of every comment inserted and why:

---

### `open_review_cycle`
- **RULE** above `AND STATUS = 'DRAFT'` — a cycle must be in DRAFT before it can be opened; this WHERE clause enforces the state-machine transition.
- **RULE** above `IF SQL%ROWCOUNT = 0` — explains what zero-row-update means in business terms.
- **RULE** above `RAISE_APPLICATION_ERROR(-20401, …)` — documents the hard error thrown when the status pre-condition fails.

### `submit_self_assessment`
- **RULE** above `AND STATUS IN ('NOT_STARTED', 'SELF_REVIEW')` — only these two statuses allow a self-assessment; the update also advances the status to MANAGER_REVIEW.
- **RULE** above `IF SQL%ROWCOUNT = 0` — explains the guard.
- **RULE** above `RAISE_APPLICATION_ERROR(-20402, …)` — documents the error path.

### `submit_manager_review`
- **RULE** above `IF p_overall_rating < 1.0 OR p_overall_rating > 5.0` — the rating scale is bounded to [1.0, 5.0].
- **RULE** above `RAISE_APPLICATION_ERROR(-20403, …)` — documents the out-of-range error.
- **VALIDATION** above the `RATING_LABEL = CASE` block — the CASE derives a label from the numeric score.
- **CONSTRAINT** on each of the four `WHEN p_overall_rating >= …` thresholds (4.5, 3.5, 2.5, 1.5) — documents each performance band boundary in plain English.

### `acknowledge_review`
- **RULE** above `AND STATUS = 'COMPLETED'` — an employee can only acknowledge a review that the manager has already completed.

### `update_goal_progress`
- **VALIDATION** above `STATUS = NVL(p_status, CASE …)` — when no explicit status is passed, status is auto-derived from the progress percentage.
- **CONSTRAINT** on `>= 100` — reaching 100% automatically marks the goal COMPLETED.
- **CONSTRAINT** on `> 0` — any non-zero progress below 100 sets the goal to IN_PROGRESS.
- **VALIDATION** above `COMMENTS = NVL(p_comments, COMMENTS)` — existing comments are preserved when no new value is supplied.

### `get_team_reviews`
- **BUSINESS** above the `WHERE` clause — the query is scoped to a specific reviewer (manager) within a specific cycle.

### `get_rating_distribution`
- **BUSINESS** above the `WHERE` clause — only completed (rated) reviews are included; optionally filtered to one department.

### `generate_reviews_for_cycle`
- **BUSINESS** above `WHERE EMPLOYMENT_STATUS = 'ACTIVE'` — only active employees are candidates for bulk review generation.
- **RULE** above `AND MANAGER_EMP_ID IS NOT NULL` — employees without a manager assignment are excluded, because a manager is required to act as the reviewer.
