```markdown
# Findings Memo: Telehealth Patient Engagement A/B Test and Churn Prediction

## 1. Executive Summary

This project evaluated whether personalized weekly check-in messages could improve 90-day treatment adherence in a simulated telehealth hormone optimization program. The simulated A/B test compared a Control arm receiving generic weekly wellness messages against a Treatment arm receiving personalized check-ins tied to patient goals, lab trends, and recommended next actions.

The Treatment arm achieved a 62.6% adherence rate compared with 52.9% in the Control arm. This produced a statistically significant absolute lift of 9.7 percentage points, with a 95% confidence interval of 5.4 to 14.0 percentage points and a p-value of 0.000006. Because treatment assignment is randomized, the primary A/B test supports a causal interpretation of the intervention effect in this simulated setting.

The recommendation is to advance personalized check-ins as the preferred engagement strategy in this simulated setting, while monitoring adherence, appointment completion, churn, and satisfaction after rollout. The strongest exploratory response patterns appeared among patients with Low testosterone, Libido goals, Energy goals, Premium subscription plans, and patients aged 35-44.

The project also built a churn prediction model to identify patients most likely to drop off within 30 days. The final logistic regression model achieved a test AUC-ROC of 0.7577 and identified 18 High-risk patients in the full 2,000-patient cohort. This creates a practical workflow where the experiment measures whether the intervention works, while the churn model helps decide which patients should receive the most proactive outreach.

---

## 2. Methodology

### Experiment Design

The analysis used a 2,000-patient synthetic telehealth cohort split evenly between Control and Treatment arms. Patients were randomized using stratification on key pre-treatment variables, including age group, treatment goal, and testosterone tier.

The Control condition represented generic weekly wellness messaging. The Treatment condition represented personalized weekly check-ins referencing the patient's treatment goal, recent lab trend, and recommended next action.

The primary outcome was 90-day treatment adherence, defined as whether the patient completed the required treatment protocol within the 90-day window. Secondary outcomes included 90-day appointment completion, 30-day churn, and day-45 satisfaction score.

### Statistical Approach

Before evaluating outcomes, the analysis ran a power analysis to confirm the cohort was large enough to detect the planned effect size. The power analysis showed that approximately 470 patients per arm were required to detect an 8 percentage point lift from a 54% baseline adherence rate with 80% power at alpha = 0.05. The simulated cohort had 1,000 patients per arm, so it was adequately powered.

Randomization checks showed the treatment and control arms were well balanced on measured pre-treatment covariates. The primary outcome was analyzed using a one-sided two-proportion z-test. Secondary outcomes were evaluated with Bonferroni correction because multiple secondary tests were performed. Subgroup analyses were treated as exploratory and used to generate rollout hypotheses rather than confirmatory claims.

### Modeling Approach

The churn model predicted 30-day churn using only pre-treatment and early patient-journey features. Features included age, baseline testosterone level, days to first lab, day-7 engagement score, support contacts, prior telehealth experience, testosterone tier, treatment goal, subscription plan, and age group.

The model excluded experiment arm, 90-day adherence, appointment completion, satisfaction score, and any churn risk fields to avoid leakage. Logistic regression was selected because it is interpretable and appropriate for stakeholder communication.

Training used an 80/20 stratified train-test split, StandardScaler fitted only on the training data, and GridSearchCV with 5-fold cross-validation to tune regularization strength. The selected operating threshold was chosen to maximize F1 while maintaining recall of at least 0.60, reflecting an outreach use case where catching likely churners is important.

### SQL Cohort Analysis

The project also included four SQL queries against a SQLite database. These queries created operational cohort views for experiment KPIs, segment adherence, high-risk patient outreach, and rolling enrollment trends. SQL results were executed from the notebook using pandas read_sql_query and saved as CSV outputs.

---

## 3. Results

### Primary Experiment Result

The Treatment arm had a 90-day adherence rate of 62.6%, compared with 52.9% in the Control arm. This produced an absolute lift of 9.7 percentage points and a relative lift of 18.3%.

The 95% confidence interval for the absolute lift was 5.4 to 14.0 percentage points, and the one-sided p-value was 0.000006. The number needed to treat was 11. In business terms, for every 11 patients receiving personalized check-ins, approximately one additional patient completed the 90-day treatment protocol.

### Secondary Outcomes

Secondary outcomes partially supported the primary finding. Appointment completion improved from 64.2% in Control to 70.5% in Treatment, a 6.3 percentage point increase that was significant after Bonferroni correction.

Day-45 satisfaction also improved from 3.55 in Control to 3.85 in Treatment, a 0.30-point increase that was significant after Bonferroni correction.

Thirty-day churn decreased from 18.1% in Control to 15.6% in Treatment, a 2.5 percentage point reduction. However, this churn reduction did not meet the Bonferroni-corrected significance threshold, so it should be treated as directionally favorable but not confirmatory.

### Subgroup Results

The strongest exploratory subgroup lift appeared among patients in the Low testosterone tier, with a 15.1 percentage point improvement in adherence. Patients aged 35-44 and patients with Libido treatment goals each showed approximately 14.0 percentage point lifts.

Patients with Energy goals showed a 12.9 percentage point lift, and Premium subscribers showed a 12.4 percentage point lift. These subgroup findings suggest that patients with more concrete symptom-driven goals may be especially responsive to personalized messaging.

These analyses are exploratory. They should be used for targeted rollout monitoring or future experiment design rather than final causal claims.

### Churn Model Results

The final logistic regression model achieved a cross-validation AUC-ROC mean of 0.7771 with a standard deviation of 0.0495. On the held-out test set, the model achieved a test AUC-ROC of 0.7577 and average precision of 0.4271.

The selected operating threshold was 0.20. At this threshold, the model achieved precision of 0.3185, recall of 0.6418, and F1 of 0.4257.

The top churn-risk signal was low day-7 engagement score. Longer days to first lab draw and Standard subscription plan status also increased predicted churn risk. Prior telehealth experience reduced predicted churn risk, which is directionally consistent with the idea that patients familiar with digital care workflows may be less likely to disengage early.

### Full Cohort Risk Scoring

The full 2,000-patient cohort was scored using the trained churn model and assigned to Low, Medium, or High churn-risk tiers.

| Risk Tier | Patient Count | Observed Churn Rate |
|---|---:|---:|
| Low risk | 1,594 | 9.1% |
| Medium risk | 388 | 45.4% |
| High risk | 18 | 88.9% |

The model created clear separation between risk tiers. The High-risk tier contained 18 patients and had an observed churn rate of 88.9%, making it useful for prioritizing proactive outreach.

### SQL Results

SQL cohort analysis translated the experiment and model outputs into operational views. The cohort summary confirmed higher adherence and appointment completion in Treatment compared with Control. Segment adherence analysis showed stronger response patterns among Energy and Libido patients, especially in younger and middle age groups.

The high-risk patient query returned a ranked list of the top 50 patients by churn risk, including all High-risk patients and the next-highest Medium-risk patients. Each patient was assigned a recommended action, such as sending a personalized care-team check-in, prioritizing lab completion reminders, or sending an automated educational message.

The rolling enrollment query produced a 7-day trailing enrollment trend that could support onboarding capacity planning.

### Business Impact Estimate

The full cohort risk scoring identified 18 High-risk patients. Applying the experiment's 9.7 percentage point adherence lift to this High-risk tier produced an estimated 1.7 additional retained or adherent patients over a 90-day horizon.

Illustrative retained revenue estimate using an assumed $150/month subscription value: approximately $786.

This is an illustrative estimate only and should not be interpreted as a real financial forecast.

---

## 4. Recommendations and Limitations

### Recommendation

In this simulated setting, personalized weekly check-ins should be advanced as the preferred engagement strategy because they produced a statistically significant and operationally meaningful improvement in 90-day adherence.

The care team should use churn-risk scores to prioritize outreach for patients most likely to disengage early. High-risk patients should receive proactive care-team check-ins, lab completion reminders, or high-touch onboarding support depending on their risk drivers.

### Limitations

First, the dataset is synthetic. The experiment and model results are useful for demonstrating methodology, but they are not empirical evidence about real patient behavior. A real rollout would require validation on actual patient data with a pre-registered analysis plan.

Second, subgroup analyses are exploratory and subject to multiple-comparison risk. The strongest subgroup lifts should guide future monitoring and experiment design, but they should not be treated as independently confirmed treatment effects.

Third, the churn model is intentionally interpretable. Logistic regression is appropriate for this project and stakeholder communication, but more complex models may perform better on real-world data if validated carefully and monitored for bias, calibration, and operational usefulness.

### Recommended Next Steps

1. Run the experiment on real patient data using a pre-registered analysis plan.
2. Monitor post-rollout adherence, appointment completion, churn, and satisfaction.
3. Explore survival analysis for time-to-churn modeling.
4. Build an uplift model to estimate heterogeneous treatment effects for more precise targeting.