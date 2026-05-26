/*
Phase 4 SQL Analysis
File: sql/segment_adherence.sql

Business question:
Which patient segments show the strongest or weakest 90-day adherence by experiment arm?

Source table:
patient_cohort

Returned columns:
- age_group
- treatment_goal
- experiment_arm
- patient_count
- adherence_rate_90d
*/

SELECT
    age_group,
    treatment_goal,
    experiment_arm,
    COUNT(*) AS patient_count,
    ROUND(AVG(CAST(adhered_90d AS REAL)), 4) AS adherence_rate_90d
FROM patient_cohort
GROUP BY
    age_group,
    treatment_goal,
    experiment_arm
ORDER BY
    age_group,
    treatment_goal,
    experiment_arm;