/*
Phase 4 SQL Analysis
File: sql/cohort_summary.sql

Business question:
How do the main experiment KPIs compare between the Control and Treatment groups?

Source table:
patient_cohort

Returned columns:
- experiment_arm
- patient_count
- adherence_rate_90d
- churn_rate_30d
- appointment_completion_rate_90d
- avg_engagement_score_day7
*/

SELECT
    experiment_arm,
    COUNT(*) AS patient_count,
    ROUND(AVG(CAST(adhered_90d AS REAL)), 4) AS adherence_rate_90d,
    ROUND(AVG(CAST(churned_30d AS REAL)), 4) AS churn_rate_30d,
    ROUND(AVG(CAST(completed_appointment_90d AS REAL)), 4) AS appointment_completion_rate_90d,
    ROUND(AVG(CAST(engagement_score_day7 AS REAL)), 2) AS avg_engagement_score_day7
FROM patient_cohort
GROUP BY
    experiment_arm
ORDER BY
    experiment_arm;