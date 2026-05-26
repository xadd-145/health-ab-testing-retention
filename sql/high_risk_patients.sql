/*
Phase 4 SQL Analysis
File: sql/high_risk_patients.sql

Business question:
Which patients should the care team prioritize based on predicted churn risk?

Source table:
scored_cohort

Returned columns:
- patient_id
- churn_risk_score
- churn_risk_tier
- treatment_goal
- testosterone_tier
- age_group
- days_to_first_lab
- engagement_score_day7
- recommended_action

Notes:
The scored cohort may contain fewer than 50 High-risk patients.
This query still returns the top 50 patients by churn_risk_score descending,
so the output can include High-risk patients first and then the next-highest
Medium-risk patients.
*/

SELECT
    patient_id,
    ROUND(CAST(churn_risk_score AS REAL), 4) AS churn_risk_score,
    churn_risk_tier,
    treatment_goal,
    testosterone_tier,
    age_group,
    days_to_first_lab,
    ROUND(CAST(engagement_score_day7 AS REAL), 1) AS engagement_score_day7,
    CASE
        WHEN churn_risk_tier = 'High'
             AND CAST(engagement_score_day7 AS REAL) < 3
            THEN 'Send personalized care-team check-in immediately'

        WHEN churn_risk_tier = 'High'
             AND CAST(days_to_first_lab AS REAL) > 20
            THEN 'Prioritize lab completion reminder'

        WHEN churn_risk_tier = 'High'
            THEN 'Enroll in high-touch onboarding sequence'

        WHEN churn_risk_tier = 'Medium'
            THEN 'Send automated educational message at day 14'

        ELSE 'Continue standard engagement cadence'
    END AS recommended_action
FROM scored_cohort
ORDER BY
    CAST(churn_risk_score AS REAL) DESC
LIMIT 50;