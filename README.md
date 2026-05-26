# Telehealth Patient Engagement A/B Testing and Churn Prediction Engine

This project simulates a telehealth patient engagement experiment, evaluates the causal impact of personalized check-ins on 90-day adherence, predicts 30-day churn risk, and operationalizes results through SQL cohort analysis.

## Tech Stack

Python · Pandas · NumPy · SciPy · Statsmodels · Scikit-learn · Matplotlib · Plotly · SQL · SQLite · Jupyter Notebook

## Business Problem

Telehealth subscription programs depend on patients staying engaged long enough to complete treatment protocols, attend follow-up appointments, and realize clinical benefit. Early disengagement creates both a clinical problem and a business retention problem. This project simulates how a data scientist could evaluate whether personalized weekly check-in messages improve patient adherence and identify which patients should be prioritized for proactive outreach.

## Approach

### 1. Synthetic Patient Cohort

Generated a fully synthetic 2,000-patient telehealth cohort with clinically grounded patient features, including age, testosterone tier, treatment goal, subscription plan, prior telehealth experience, lab completion delay, early engagement score, and support contact volume.

All patient IDs are synthetic. No real patient data, names, addresses, member IDs, or PHI are used.

### 2. A/B Experiment Analysis

Simulated a randomized A/B test comparing generic weekly messages against personalized weekly check-ins. The primary outcome was 90-day treatment adherence. The analysis included power analysis, randomization checks, a two-proportion z-test, confidence interval estimation, secondary metric testing with Bonferroni correction, and exploratory subgroup analysis.

Because treatment assignment is randomized, the primary A/B test supports a causal interpretation of the intervention effect in this simulated setting.

### 3. Churn Prediction Model

Built an interpretable logistic regression model to predict 30-day churn risk using only pre-treatment and early patient-journey features. The model excluded experiment assignment and all downstream outcome variables to avoid leakage. The selected operating threshold prioritized recall so that the outreach workflow could catch a meaningful share of likely churners.

### 4. SQL Cohort Analysis

Developed four SQL queries against a SQLite database to summarize experiment KPIs, analyze segment-level adherence, generate a ranked high-risk outreach list, and calculate rolling 7-day enrollment trends. These outputs connect the statistical and machine learning results to operational decision-making.

## Key Results

### Primary A/B Test Result

| Metric | Result |
|---|---:|
| Control adherence rate | 52.9% |
| Treatment adherence rate | 62.6% |
| Absolute lift | +9.7 percentage points |
| Relative lift | +18.3% |
| 95% confidence interval | +5.4 to +14.0 percentage points |
| p-value | 0.000006 |
| Number needed to treat | 11 |

Personalized weekly check-ins significantly improved 90-day adherence. For every 11 patients receiving personalized check-ins, approximately one additional patient completed the 90-day treatment protocol.

### Secondary Metrics

| Metric | Control | Treatment | Difference | Result |
|---|---:|---:|---:|---|
| Appointment completion | 64.2% | 70.5% | +6.3 pp | Significant |
| 30-day churn | 18.1% | 15.6% | -2.5 pp | Not significant |
| Day-45 satisfaction | 3.55 | 3.85 | +0.30 | Significant |

### Exploratory Subgroup Findings

The strongest exploratory adherence lifts appeared in:

| Segment | Absolute Lift |
|---|---:|
| Low testosterone tier | +15.1 pp |
| Age 35-44 | +14.0 pp |
| Libido treatment goal | +14.0 pp |
| Energy treatment goal | +12.9 pp |
| Premium subscription plan | +12.4 pp |

These subgroup findings are exploratory and should be used for rollout prioritization or future experiment design, not as standalone confirmatory causal claims.

### Churn Model Performance

| Metric | Result |
|---|---:|
| CV AUC-ROC mean | 0.7771 |
| CV AUC-ROC standard deviation | 0.0495 |
| Test AUC-ROC | 0.7577 |
| Average precision | 0.4271 |
| Selected threshold | 0.20 |
| Precision | 0.3185 |
| Recall | 0.6418 |
| F1 | 0.4257 |

The strongest churn-risk driver was low day-7 engagement. Longer time to first lab draw and Standard subscription plan status also increased predicted churn risk.

### Full Cohort Risk Scoring

| Risk Tier | Patient Count |
|---|---:|
| Low risk | 1,594 |
| Medium risk | 388 |
| High risk | 18 |

Observed churn increased sharply by risk tier:

| Risk Tier | Observed Churn Rate |
|---|---:|
| Low risk | 9.1% |
| Medium risk | 45.4% |
| High risk | 88.9% |

### Business Impact Estimate

| Metric | Result |
|---|---:|
| High-risk patients | 18 |
| Estimated additional retained patients | 1.7 |
| Illustrative retained revenue estimate | $786 |

Illustrative retained revenue estimate using an assumed $150/month subscription value.

## Business Recommendation

Roll out personalized check-ins in this simulated setting because the intervention produced a statistically significant and operationally meaningful lift in 90-day adherence. Prioritize monitoring and follow-up testing among high-response segments such as Low testosterone tier, Libido goal, Energy goal, and ages 35-44.

Use the churn model to create a patient-success outreach queue. The model identifies 18 High-risk patients in the full cohort and can help prioritize care-team check-ins, lab reminders, and onboarding support.

## Repository Structure

```text
hone-health-ab-testing-retention/
│
├── README.md
├── requirements.txt
├── run_pipeline.py
├── .gitignore
│
├── data/
│   └── processed/
│       ├── synthetic_patient_cohort.csv
│       └── scored_patient_cohort.csv
│
├── docs/
│   ├── data_dictionary.md
│   ├── findings_memo.md
│   ├── resume_bullets.md
│   └── architecture_diagram.png
│
├── notebooks/
│   └── 01_ab_test_and_churn_analysis.ipynb
│
├── outputs/
│   ├── hone_synthetic.db
│   ├── figures/
│   │   ├── adherence_by_arm.png
│   │   ├── adherence_lift_confidence_interval.png
│   │   ├── secondary_metrics_by_arm.png
│   │   ├── subgroup_lift_heatmap.png
│   │   ├── roc_curve.png
│   │   ├── precision_recall_curve.png
│   │   ├── calibration_curve.png
│   │   ├── confusion_matrix.png
│   │   └── feature_importance.png
│   └── tables/
│       ├── power_analysis_results.csv
│       ├── randomization_balance_table.csv
│       ├── primary_metric_results.csv
│       ├── secondary_metric_results.csv
│       ├── subgroup_analysis_results.csv
│       ├── feature_importance.csv
│       ├── business_impact_estimate.csv
│       ├── sql_cohort_summary.csv
│       ├── sql_segment_adherence.csv
│       ├── sql_high_risk_patients.csv
│       └── sql_rolling_enrollment.csv
│
├── sql/
│   ├── cohort_summary.sql
│   ├── segment_adherence.sql
│   ├── high_risk_patients.sql
│   └── rolling_enrollment.sql
│
└── src/
    ├── __init__.py
    └── data_generation/
        ├── __init__.py
        ├── distributions.py
        ├── randomization.py
        └── generate_cohort.py