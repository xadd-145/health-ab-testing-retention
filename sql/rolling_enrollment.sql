/*
Phase 4 SQL Analysis
File: sql/rolling_enrollment.sql

Business question:
How did patient enrollment volume trend over time?

Source table:
patient_cohort

Returned columns:
- enrollment_date
- rolling_7d_enrollments

SQLite compatibility:
This query uses a correlated subquery instead of window functions.

Date handling:
The DATE() function works correctly when enrollment_date is stored in an
ISO-compatible format such as:
- YYYY-MM-DD
- YYYY-MM-DD HH:MM:SS

The query converts enrollment_date with DATE() in both the outer query and
the correlated subquery so that timestamps like '2024-01-01 00:00:00'
are handled correctly.
*/

SELECT
    dates.enrollment_date,
    (
        SELECT
            COUNT(*)
        FROM patient_cohort AS p2
        WHERE DATE(p2.enrollment_date) BETWEEN DATE(dates.enrollment_date, '-6 days')
                                           AND DATE(dates.enrollment_date)
    ) AS rolling_7d_enrollments
FROM (
    SELECT DISTINCT
        DATE(enrollment_date) AS enrollment_date
    FROM patient_cohort
    WHERE enrollment_date IS NOT NULL
      AND DATE(enrollment_date) IS NOT NULL
) AS dates
ORDER BY
    dates.enrollment_date;