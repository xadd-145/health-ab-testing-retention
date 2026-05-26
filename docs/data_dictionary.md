# Data Dictionary

This dataset is fully synthetic. No real patient data, real patient identifiers, PHI, addresses, names, or medical records are used.

| Column Name | Data Type | Description | Generation Logic | Used in A/B Test | Used in Churn Model |
|---|---:|---|---|---|---|
| patient_id | string | Synthetic patient identifier. | Generated sequentially as P000001 through P002000. | no | no |
| enrollment_date | date/string | Patient enrollment date. | Random date between 2024-01-01 and 2024-12-31, with Q1 weighted 1.4x to reflect New Year health-resolution demand. | no | no |
| age | integer | Patient age in years. | Drawn from a normal distribution with mean 38 and standard deviation 9, clipped to 25-65. | yes | yes |
| age_group | string | Binned age segment. | Derived from age using bins 25-34, 35-44, 45-54, and 55-65. | yes | yes |
| baseline_testosterone_level | integer | Baseline testosterone level in ng/dL. | Drawn from a normal distribution with mean 320 and standard deviation 85, clipped to 150-500. | yes | yes |
| testosterone_tier | string | Testosterone segment. | Low if below 250, Low-Normal if 250-349, and Borderline if 350-500. | yes | yes |
| treatment_goal | string | Patient-stated treatment goal. | Randomly assigned using probabilities: Energy 35%, Libido 30%, Body Composition 25%, General Wellness 10%. | yes | yes |
| subscription_plan | string | Patient subscription tier. | Randomly assigned using probabilities: Standard 70%, Premium 30%. | yes | yes |
| prior_telehealth_experience | integer | Whether the patient previously used telehealth. | Bernoulli draw with 45% prevalence. | yes | yes |
| days_to_first_lab | integer | Number of days from enrollment to first lab completion. | Drawn from a gamma distribution with shape 2 and scale 6, rounded and clipped to 1-60. | yes | yes |
| engagement_score_day7 | float | Early engagement score from 0 to 10. | Drawn from a beta distribution scaled to 0-10, with bonuses for Premium plan and prior telehealth experience. | yes | yes |
| support_contacts_30d | integer | Count of inbound support contacts in first 30 days. | Drawn from a Poisson distribution with lambda 1.8. | yes | yes |
| experiment_arm | string | Randomized A/B test assignment. | Assigned using stratified randomization on age_group, treatment_goal, and testosterone_tier. | yes | no |
| adhered_90d | integer | Primary outcome: whether patient completed at least 2 of 3 scheduled labs within 90 days. | Bernoulli draw from an adherence probability using base rate, feature modifiers, and treatment lift. | yes | no |
| churned_30d | integer | Secondary outcome and churn model target: whether patient cancelled within 30 days. | Bernoulli draw from a churn probability using base rate, feature modifiers, and treatment reduction. | yes | target |
| completed_appointment_90d | integer | Secondary outcome: whether patient completed at least one follow-up appointment within 90 days. | Bernoulli draw from appointment probability using base rate, treatment lift, engagement, churn, and plan modifiers. | yes | no |
| satisfaction_score_day45 | float | Patient-reported satisfaction score from 1 to 5 at day 45. | Available for approximately 60% of patients; non-respondents are set to missing. Respondent scores are drawn from arm-specific probability distributions. | yes | no |