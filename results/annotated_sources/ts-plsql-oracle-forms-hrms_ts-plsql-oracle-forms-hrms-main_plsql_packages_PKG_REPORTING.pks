This file is a package specification (`.pks`) — it contains only procedure signatures and type declarations, with no executable body. There are no IF/CASE conditions, no `RAISE_APPLICATION_ERROR` calls, no hard-coded threshold comparisons, no cursor WHERE clauses, and no NVL/DECODE/CASE expressions.

Per the annotation rules, the file should be returned unchanged:

```sql
CREATE OR REPLACE PACKAGE HRMS.PKG_REPORTING AS
-- ============================================================================
-- PKG_REPORTING - Report Generation Package
-- Headcount, compensation, turnover, compliance reporting
--
-- Dependencies: PKG_EMPLOYEE, PKG_PAYROLL, PKG_COMMON
-- Called by: HRMS_REPORTS form, Oracle Reports (.rdf), batch jobs
-- Known issues:
--   - Denormalized reporting tables refreshed nightly; stale during business hours
--   - Some reports use hard-coded fiscal year start (Oct 1)
-- ============================================================================

    TYPE t_report_cursor IS REF CURSOR;

    PROCEDURE headcount_report(
        p_cursor     OUT t_report_cursor,
        p_as_of_date IN DATE DEFAULT SYSDATE,
        p_dept_id    IN NUMBER DEFAULT NULL,
        p_location   IN VARCHAR2 DEFAULT NULL
    );

    PROCEDURE compensation_summary(
        p_cursor   OUT t_report_cursor,
        p_dept_id  IN NUMBER DEFAULT NULL,
        p_grade_id IN NUMBER DEFAULT NULL
    );

    PROCEDURE turnover_report(
        p_cursor     OUT t_report_cursor,
        p_start_date IN DATE,
        p_end_date   IN DATE,
        p_dept_id    IN NUMBER DEFAULT NULL
    );

    PROCEDURE new_hires_report(
        p_cursor     OUT t_report_cursor,
        p_start_date IN DATE,
        p_end_date   IN DATE,
        p_dept_id    IN NUMBER DEFAULT NULL
    );

    PROCEDURE leave_utilization_report(
        p_cursor  OUT t_report_cursor,
        p_year    IN NUMBER DEFAULT EXTRACT(YEAR FROM SYSDATE),
        p_dept_id IN NUMBER DEFAULT NULL
    );

    PROCEDURE payroll_summary_report(
        p_cursor    OUT t_report_cursor,
        p_period_id IN NUMBER
    );

    PROCEDURE eeo_compliance_report(
        p_cursor     OUT t_report_cursor,
        p_as_of_date IN DATE DEFAULT SYSDATE
    );

    PROCEDURE refresh_reporting_tables(
        p_user IN VARCHAR2 DEFAULT USER
    );

END PKG_REPORTING;
/
```

**Why no annotations were added:** The annotation rules target executable logic — conditions, error raises, literal thresholds, filtered queries, and expressions — none of which appear in a `.pks` spec file. The business logic worth annotating lives in the corresponding `.pkb` body file where those procedures are implemented. Annotating `PKG_REPORTING.pkb` will yield meaningful results.
