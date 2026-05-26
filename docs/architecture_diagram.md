# Architecture Diagram

```text
                           ┌────────────────────────────┐
                           │  Synthetic Data Generation │
                           │                            │
                           │  src/data_generation/      │
                           │  - distributions.py        │
                           │  - randomization.py        │
                           │  - generate_cohort.py      │
                           └──────────────┬─────────────┘
                                          │
                                          │ run_pipeline.py
                                          ▼
                         ┌────────────────────────────────┐
                         │ Synthetic Patient Cohort        │
                         │                                │
                         │ data/processed/                │
                         │ synthetic_patient_cohort.csv   │
                         │                                │
                         │ outputs/hone_synthetic.db      │
                         │ table: patient_cohort          │
                         └──────────────┬─────────────────┘
                                        │
                                        ▼
              ┌────────────────────────────────────────────────┐
              │ Jupyter Analysis Notebook                       │
              │ notebooks/01_ab_test_and_churn_analysis.ipynb   │
              └──────────────┬─────────────────┬───────────────┘
                             │                 │
                             │                 │
                             ▼                 ▼
       ┌──────────────────────────┐   ┌────────────────────────────┐
       │ A/B Test Analysis         │   │ Churn Prediction Model      │
       │                           │   │                            │
       │ - Power analysis          │   │ - Feature engineering       │
       │ - Randomization checks    │   │ - Logistic regression       │
       │ - Primary z-test          │   │ - Cross-validation          │
       │ - Secondary metrics       │   │ - Test evaluation           │
       │ - Subgroup analysis       │   │ - Risk tier scoring         │
       └──────────────┬───────────┘   └──────────────┬─────────────┘
                      │                              │
                      ▼                              ▼
       ┌──────────────────────────┐   ┌────────────────────────────┐
       │ Experiment Outputs        │   │ Scored Cohort               │
       │                           │   │                            │
       │ outputs/figures/          │   │ data/processed/             │
       │ outputs/tables/           │   │ scored_patient_cohort.csv   │
       └──────────────┬───────────┘   │                            │
                      │               │ outputs/hone_synthetic.db    │
                      │               │ table: scored_cohort         │
                      │               └──────────────┬─────────────┘
                      │                              │
                      └──────────────┬───────────────┘
                                     ▼
                         ┌──────────────────────────┐
                         │ SQL Cohort Analysis       │
                         │                           │
                         │ sql/cohort_summary.sql    │
                         │ sql/segment_adherence.sql │
                         │ sql/high_risk_patients.sql│
                         │ sql/rolling_enrollment.sql│
                         └──────────────┬───────────┘
                                        ▼
                         ┌──────────────────────────┐
                         │ Portfolio Documentation  │
                         │                          │
                         │ README.md                │
                         │ docs/findings_memo.md    │
                         │ docs/data_dictionary.md  │
                         └──────────────────────────┘