=== CHUNK METADATA ===
Chunk: 03            (chunk count is budget-driven, not a fixed file count)
Type group: forms
Expected files (1):
  1. [forms] ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PERFORMANCE.xml (6509 chars written)
Total source content: 6055 characters (budget: 30000)
=== END METADATA ===


---

=== FILE: ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PERFORMANCE.xml ===

**IDENTITY:**
  KIND: form
  PURPOSE: performance review management — review cycles, self-assessments, manager reviews, goal tracking, and rating calibration

**STRUCTURES:**
  **Form-level:**
  HRMS_PERFORMANCE — KIND: Forms module; TYPE: N/A (FirstNavigationBlock=REVIEW_CYCLE, MenuModule=HRMS_MENU, MenuSource=File)
  HRMS_COMMON_LIB — KIND: attached library; TYPE: N/A

  **REVIEW_CYCLE block** (source HRMS.REVIEW_CYCLES; RecordsDisplayed=5; InsertAllowed=No; UpdateAllowed=No; DeleteAllowed=No) — KIND: Forms block; TYPE: N/A
  CYCLE_ID — KIND: Forms item; TYPE: N/A (hidden, PrimaryKey)
  CYCLE_NAME — KIND: Forms item; TYPE: Char (Width=200)
  CYCLE_YEAR — KIND: Forms item; TYPE: Number (Width=50)
  START_DATE — KIND: Forms item; TYPE: Date (FormatMask=MM/DD/YYYY, Width=100)
  END_DATE — KIND: Forms item; TYPE: Date (FormatMask=MM/DD/YYYY, Width=100)
  STATUS (REVIEW_CYCLE) — KIND: Forms item; TYPE: Char (Width=80)

  **PERFORMANCE_REVIEW block** (source HRMS.PERFORMANCE_REVIEWS; RecordsDisplayed=8; InsertAllowed=No; UpdateAllowed=Yes; DeleteAllowed=No) — KIND: Forms block; TYPE: N/A
  REVIEW_ID — KIND: Forms item; TYPE: N/A (hidden, PrimaryKey)
  CYCLE_ID (PERFORMANCE_REVIEW) — KIND: Forms item; TYPE: N/A (hidden)
  EMP_ID — KIND: Forms item; TYPE: N/A (hidden)
  EMP_NAME_DISP — KIND: Forms item (Display Item); TYPE: Char (Width=180)
  STATUS (PERFORMANCE_REVIEW) — KIND: Forms item; TYPE: Char (Width=120, UpdateAllowed=No)
  OVERALL_RATING — KIND: Forms item; TYPE: Number (FormatMask=9.0, Width=50)
  RATING_LABEL — KIND: Forms item (Display Item); TYPE: Char (Width=150)
  SELF_ASSESSMENT — KIND: Forms item; TYPE: Char (Width=300, Height=80, MultiLine=Yes)
  MANAGER_ASSESSMENT — KIND: Forms item; TYPE: Char (Width=300, Height=80, MultiLine=Yes)
  CYCLE_REVIEW_REL — KIND: Forms relation; TYPE: N/A (master REVIEW_CYCLE → detail PERFORMANCE_REVIEW, JoinCondition PERFORMANCE_REVIEW.CYCLE_ID = REVIEW_CYCLE.CYCLE_ID, AutoQuery=Yes)

  **PERFORMANCE_GOAL block** (source HRMS.PERFORMANCE_GOALS; RecordsDisplayed=5; InsertAllowed=Yes; UpdateAllowed=Yes; DeleteAllowed=No) — KIND: Forms block; TYPE: N/A
  GOAL_ID — KIND: Forms item; TYPE: N/A (hidden, PrimaryKey)
  REVIEW_ID (PERFORMANCE_GOAL) — KIND: Forms item; TYPE: N/A (hidden)
  GOAL_TITLE — KIND: Forms item; TYPE: Char (Width=250)
  GOAL_CATEGORY — KIND: Forms item (List Item, Poplist); TYPE: Char (Width=100); values: Business=BUSINESS, Development=DEVELOPMENT, Leadership=LEADERSHIP
  WEIGHT_PCT — KIND: Forms item; TYPE: Number (FormatMask=990, Width=50)
  PROGRESS_PCT — KIND: Forms item; TYPE: Number (FormatMask=990, Width=50)
  STATUS (PERFORMANCE_GOAL) — KIND: Forms item; TYPE: Char (Width=100)
  REVIEW_GOAL_REL — KIND: Forms relation; TYPE: N/A (master PERFORMANCE_REVIEW → detail PERFORMANCE_GOAL, JoinCondition PERFORMANCE_GOAL.REVIEW_ID = PERFORMANCE_REVIEW.REVIEW_ID, AutoQuery=Yes)

  **Layout:**
  CVS_MAIN — KIND: Canvas (Tab); TYPE: N/A (Width=750, Height=520); tab pages: TP_CYCLES "Review Cycles", TP_REVIEWS "My Reviews", TP_GOALS "Goals"
  WIN_PERFORMANCE — KIND: Forms window; TYPE: N/A (WindowStyle=Document, Width=770, Height=560, PrimaryCanvas=CVS_MAIN, Title="Performance Management")

**METHODS:**
  **TRIGGER WHEN-NEW-FORM-INSTANCE** [SOURCE: L20-38]
  - What it does: Fires once when the form instance opens. Validates the current session via PKG_SECURITY.is_session_valid using the numeric application username; if invalid, shows "Session expired." and raises FORM_TRIGGER_FAILURE, aborting form startup. Otherwise sets the MDI window title to include :GLOBAL.current_user, navigates to REVIEW_CYCLE, sets that block's DEFAULT_WHERE to restrict rows to STATUS IN ('OPEN','DRAFT') ordered by CYCLE_YEAR DESC, and executes the query.
  - Business rules: Form requires a valid session (PKG_SECURITY.is_session_valid) to open. REVIEW_CYCLE block only ever displays cycles with STATUS 'OPEN' or 'DRAFT', ordered by CYCLE_YEAR descending.
  - Numbers & thresholds: None (WHERE clause values are the strings 'OPEN'/'DRAFT', not numeric).
  - Security & error handling: Session validity check via PKG_SECURITY.is_session_valid(TO_NUMBER(GET_APPLICATION_PROPERTY(USERNAME))); on failure raises FORM_TRIGGER_FAILURE after messaging the user, blocking form use.
  - Data in/out: Input — application USERNAME property, :GLOBAL.current_user. Output — window title set; REVIEW_CYCLE block queried and populated (side effect via EXECUTE_QUERY).

  **TRIGGER POST-QUERY (on PERFORMANCE_REVIEW)** [SOURCE: L79-88]
  - What it does: Fires per fetched PERFORMANCE_REVIEW row. Looks up the employee's FIRST_NAME || ' ' || LAST_NAME from EMPLOYEES by EMP_ID and stores it in the display-only EMP_NAME_DISP item; if no matching employee is found, sets EMP_NAME_DISP to 'Unknown'.
  - Business rules: Every queried review row must display a resolved employee name, falling back to "Unknown" rather than failing the query.
  - Numbers & thresholds: None.
  - Security & error handling: Handles NO_DATA_FOUND explicitly (sets 'Unknown'); no other exception handling.
  - Data in/out: Input — :PERFORMANCE_REVIEW.EMP_ID. Output — :PERFORMANCE_REVIEW.EMP_NAME_DISP (display item, not persisted to DB).

**DEPENDENCIES:**
  Data touched:
  - Reads: HRMS.REVIEW_CYCLES — REVIEW_CYCLE block query, filtered to STATUS IN ('OPEN','DRAFT') ordered by CYCLE_YEAR DESC
  - Reads: HRMS.PERFORMANCE_REVIEWS — PERFORMANCE_REVIEW block query, detail of REVIEW_CYCLE via CYCLE_REVIEW_REL
  - Reads: HRMS.PERFORMANCE_GOALS — PERFORMANCE_GOAL block query, detail of PERFORMANCE_REVIEW via REVIEW_GOAL_REL
  - Reads: EMPLOYEES — FIRST_NAME/LAST_NAME lookup by EMP_ID in POST-QUERY trigger
  - Writes: HRMS.PERFORMANCE_REVIEWS — PERFORMANCE_REVIEW block allows UpdateAllowed=Yes (STATUS is UpdateAllowed=No)
  - Writes: HRMS.PERFORMANCE_GOALS — PERFORMANCE_GOAL block allows InsertAllowed=Yes and UpdateAllowed=Yes

  CALLS: PKG_SECURITY.is_session_valid | EVIDENCE: OBSERVED | SOURCE: L23
  IMPORTS: HRMS_COMMON_LIB | EVIDENCE: OBSERVED | SOURCE: L18
  IMPORTS: HRMS_MENU | EVIDENCE: OBSERVED | SOURCE: L15

  Config/env: :GLOBAL.current_user (global variable used in window title)
  External integrations: None

**GAPS:**
  UNKNOWN — PKG_SECURITY.is_session_valid implementation is external to this file (EXTERNAL). RATING_LABEL and OVERALL_RATING derivation logic (how RATING_LABEL is computed from OVERALL_RATING) is not present in this file — NOT_ANALYZED / likely computed elsewhere (trigger, view, or package not included here).

*[pipeline status — type: forms · pass: correction · attempt: 2 · coverage: 100% (numbers 14/14 · fields 18/18 · required_fields 0/0 · units 2/2 · structure 5/5)]*

---

=== CHUNK STATUS ===
Files expected: 1
Files delivered: 1
  Full coverage on first pass: 0
  Required correction: 1 -> ts-plsql-oracle-forms-hrms-main/forms/xml-exports/HRMS_PERFORMANCE.xml
  Still incomplete after max attempts: 0
Raw source: 6055 chars (budget target: 30000)
Duplicate sections in this chunk: 0
=== END STATUS ===