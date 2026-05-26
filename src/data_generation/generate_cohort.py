"""
Synthetic patient cohort generation for the Telehealth Patient Engagement
A/B Testing and Churn Prediction Engine.

This module creates a reproducible 2,000-row synthetic cohort, applies
stratified experiment randomization, generates outcomes, and exports the data
to CSV and SQLite.
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.data_generation.distributions import (
    ADHERENCE_MODIFIER_BORDERLINE,
    ADHERENCE_MODIFIER_HIGH_ENGAGEMENT,
    ADHERENCE_MODIFIER_LONG_LAB_DAYS,
    ADHERENCE_MODIFIER_LOW_LAB_DAYS,
    ADHERENCE_MODIFIER_LOW_TESTOSTERONE,
    ADHERENCE_MODIFIER_PREMIUM,
    ADHERENCE_MODIFIER_PRIOR_TELEHEALTH,
    ADHERENCE_TREATMENT_GOAL_BONUS,
    ADHERENCE_TREATMENT_HIGH_ENGAGEMENT_BONUS,
    AGE_MAX,
    AGE_MEAN,
    AGE_MIN,
    AGE_STD,
    APPOINTMENT_BASE,
    APPOINTMENT_MODIFIER_CHURNED,
    APPOINTMENT_MODIFIER_HIGH_ENGAGEMENT,
    APPOINTMENT_MODIFIER_PREMIUM,
    CHURN_MODIFIER_BORDERLINE,
    CHURN_MODIFIER_LONG_LAB_DAYS,
    CHURN_MODIFIER_LOW_ENGAGEMENT,
    CHURN_MODIFIER_NO_PRIOR_TELEHEALTH,
    CHURN_MODIFIER_STANDARD_PLAN,
    CONTROL_ADHERENCE_BASE,
    CONTROL_CHURN_BASE,
    DAYS_TO_LAB_GAMMA_SCALE,
    DAYS_TO_LAB_GAMMA_SHAPE,
    DAYS_TO_LAB_MAX,
    DAYS_TO_LAB_MIN,
    ENGAGEMENT_PREMIUM_BONUS,
    ENGAGEMENT_PRIOR_TELEHEALTH_BONUS,
    ENGAGEMENT_SCORE_BETA_A,
    ENGAGEMENT_SCORE_BETA_B,
    PRIOR_TELEHEALTH_PROB,
    PROBABILITY_CEILING,
    PROBABILITY_FLOOR,
    SATISFACTION_CONTROL_PROBS,
    SATISFACTION_RESPONSE_RATE,
    SATISFACTION_TREATMENT_PROBS,
    SUBSCRIPTION_PLAN_PROBS,
    SUPPORT_CONTACTS_LAMBDA,
    TARGET_CONTROL_ADHERENCE_RATE,
    TARGET_CONTROL_CHURN_RATE,
    TARGET_TREATMENT_ADHERENCE_RATE,
    TARGET_TREATMENT_CHURN_RATE,
    TESTOSTERONE_MAX,
    TESTOSTERONE_MEAN,
    TESTOSTERONE_MIN,
    TESTOSTERONE_STD,
    TESTOSTERONE_TIER_LOW_MAX,
    TESTOSTERONE_TIER_LOW_NORMAL_MAX,
    TREATMENT_APPOINTMENT_LIFT,
    TREATMENT_BASE_LIFT,
    TREATMENT_CHURN_REDUCTION,
    TREATMENT_GOAL_PROBS,
)
from src.data_generation.randomization import assign_experiment_arms


EXPECTED_COLUMNS = [
    "patient_id",
    "enrollment_date",
    "age",
    "age_group",
    "baseline_testosterone_level",
    "testosterone_tier",
    "treatment_goal",
    "subscription_plan",
    "prior_telehealth_experience",
    "days_to_first_lab",
    "engagement_score_day7",
    "support_contacts_30d",
    "experiment_arm",
    "adhered_90d",
    "churned_30d",
    "completed_appointment_90d",
    "satisfaction_score_day45",
]


def _weighted_enrollment_dates(rng: np.random.Generator, cohort_size: int) -> pd.Series:
    """
    Generate enrollment dates from 2024-01-01 to 2024-12-31.

    Q1 dates receive 1.4x weight to simulate New Year health-resolution demand.
    """
    day_offsets = np.arange(365)
    weights = np.ones(365)
    weights[:90] *= 1.4
    weights = weights / weights.sum()

    sampled_offsets = rng.choice(
        day_offsets,
        size=cohort_size,
        replace=True,
        p=weights,
    )

    dates = pd.Timestamp("2024-01-01") + pd.to_timedelta(sampled_offsets, unit="D")
    return pd.Series(dates).dt.strftime("%Y-%m-%d")


def _assign_age_group(age: pd.Series) -> pd.Series:
    """Bin patient ages into portfolio-friendly age groups."""
    return pd.cut(
        age,
        bins=[24, 34, 44, 54, 65],
        labels=["25-34", "35-44", "45-54", "55-65"],
        include_lowest=True,
    ).astype(str)


def _assign_testosterone_tier(testosterone_level: pd.Series) -> pd.Series:
    """Classify baseline testosterone values into clinical-style tiers."""
    return np.select(
        [
            testosterone_level < TESTOSTERONE_TIER_LOW_MAX,
            testosterone_level < TESTOSTERONE_TIER_LOW_NORMAL_MAX,
        ],
        [
            "Low",
            "Low-Normal",
        ],
        default="Borderline",
    )


def _calibrate_probability_by_arm(
    probabilities: np.ndarray,
    experiment_arm: pd.Series,
    target_rates: dict,
) -> np.ndarray:
    """
    Calibrate probabilities to arm-level target rates while preserving
    patient-level ranking signal.

    A simple additive shift followed by clipping can miss the target when many
    probabilities hit the probability floor or ceiling. This binary-search
    calibration finds the additive shift that makes each arm's clipped mean as
    close as possible to the requested target rate.
    """
    calibrated_probabilities = probabilities.copy().astype(float)

    for arm, target_rate in target_rates.items():
        arm_mask = experiment_arm.eq(arm).to_numpy()
        arm_probabilities = calibrated_probabilities[arm_mask]

        lower_shift = -1.0
        upper_shift = 1.0

        for _ in range(100):
            midpoint_shift = (lower_shift + upper_shift) / 2
            shifted_mean = np.clip(
                arm_probabilities + midpoint_shift,
                PROBABILITY_FLOOR,
                PROBABILITY_CEILING,
            ).mean()

            if shifted_mean < target_rate:
                lower_shift = midpoint_shift
            else:
                upper_shift = midpoint_shift

        final_shift = (lower_shift + upper_shift) / 2
        calibrated_probabilities[arm_mask] = np.clip(
            arm_probabilities + final_shift,
            PROBABILITY_FLOOR,
            PROBABILITY_CEILING,
        )

    return calibrated_probabilities


def generate_cohort(cohort_size: int, seed: int) -> pd.DataFrame:
    """
    Generate a fully populated synthetic telehealth patient cohort.

    Parameters
    ----------
    cohort_size : int
        Number of synthetic patients to generate.
    seed : int
        Random seed for reproducible data generation.

    Returns
    -------
    pd.DataFrame
        Fully populated synthetic cohort with features, experiment arm, and outcomes.
    """
    rng = np.random.default_rng(seed)

    df = pd.DataFrame(
        {
            "patient_id": [f"P{patient_num:06d}" for patient_num in range(1, cohort_size + 1)]
        }
    )

    df["enrollment_date"] = _weighted_enrollment_dates(rng, cohort_size)

    df["age"] = np.clip(
        np.rint(rng.normal(AGE_MEAN, AGE_STD, cohort_size)),
        AGE_MIN,
        AGE_MAX,
    ).astype(int)

    df["age_group"] = _assign_age_group(df["age"])

    df["baseline_testosterone_level"] = np.clip(
        np.rint(rng.normal(TESTOSTERONE_MEAN, TESTOSTERONE_STD, cohort_size)),
        TESTOSTERONE_MIN,
        TESTOSTERONE_MAX,
    ).astype(int)

    df["testosterone_tier"] = _assign_testosterone_tier(df["baseline_testosterone_level"])

    df["treatment_goal"] = rng.choice(
        list(TREATMENT_GOAL_PROBS.keys()),
        size=cohort_size,
        p=list(TREATMENT_GOAL_PROBS.values()),
    )

    df["subscription_plan"] = rng.choice(
        list(SUBSCRIPTION_PLAN_PROBS.keys()),
        size=cohort_size,
        p=list(SUBSCRIPTION_PLAN_PROBS.values()),
    )

    df["prior_telehealth_experience"] = rng.binomial(
        n=1,
        p=PRIOR_TELEHEALTH_PROB,
        size=cohort_size,
    ).astype(int)

    df["days_to_first_lab"] = np.clip(
        np.rint(rng.gamma(DAYS_TO_LAB_GAMMA_SHAPE, DAYS_TO_LAB_GAMMA_SCALE, cohort_size)),
        DAYS_TO_LAB_MIN,
        DAYS_TO_LAB_MAX,
    ).astype(int)

    engagement_scores = rng.beta(
        ENGAGEMENT_SCORE_BETA_A,
        ENGAGEMENT_SCORE_BETA_B,
        cohort_size,
    ) * 10

    engagement_scores += np.where(
        df["subscription_plan"].eq("Premium"),
        ENGAGEMENT_PREMIUM_BONUS,
        0,
    )

    engagement_scores += np.where(
        df["prior_telehealth_experience"].eq(1),
        ENGAGEMENT_PRIOR_TELEHEALTH_BONUS,
        0,
    )

    df["engagement_score_day7"] = np.round(np.clip(engagement_scores, 0, 10), 2)

    df["support_contacts_30d"] = rng.poisson(
        SUPPORT_CONTACTS_LAMBDA,
        cohort_size,
    ).astype(int)

    df = assign_experiment_arms(df, seed)

    adherence_probability = np.full(cohort_size, CONTROL_ADHERENCE_BASE, dtype=float)

    adherence_probability += np.where(
        df["engagement_score_day7"] > 7,
        ADHERENCE_MODIFIER_HIGH_ENGAGEMENT,
        0,
    )

    adherence_probability += np.where(
        df["days_to_first_lab"] < 10,
        ADHERENCE_MODIFIER_LOW_LAB_DAYS,
        0,
    )

    adherence_probability += np.where(
        df["days_to_first_lab"] > 20,
        ADHERENCE_MODIFIER_LONG_LAB_DAYS,
        0,
    )

    adherence_probability += np.where(
        df["testosterone_tier"].eq("Low"),
        ADHERENCE_MODIFIER_LOW_TESTOSTERONE,
        0,
    )

    adherence_probability += np.where(
        df["testosterone_tier"].eq("Borderline"),
        ADHERENCE_MODIFIER_BORDERLINE,
        0,
    )

    adherence_probability += np.where(
        df["subscription_plan"].eq("Premium"),
        ADHERENCE_MODIFIER_PREMIUM,
        0,
    )

    adherence_probability += np.where(
        df["prior_telehealth_experience"].eq(1),
        ADHERENCE_MODIFIER_PRIOR_TELEHEALTH,
        0,
    )

    adherence_probability += np.where(
        df["experiment_arm"].eq("Treatment"),
        TREATMENT_BASE_LIFT,
        0,
    )

    adherence_probability += np.where(
        df["experiment_arm"].eq("Treatment") & (df["engagement_score_day7"] > 6),
        ADHERENCE_TREATMENT_HIGH_ENGAGEMENT_BONUS,
        0,
    )

    adherence_probability += np.where(
        df["experiment_arm"].eq("Treatment") & df["treatment_goal"].isin(["Energy", "Libido"]),
        ADHERENCE_TREATMENT_GOAL_BONUS,
        0,
    )

    adherence_probability = _calibrate_probability_by_arm(
        adherence_probability,
        df["experiment_arm"],
        {
            "Control": TARGET_CONTROL_ADHERENCE_RATE,
            "Treatment": TARGET_TREATMENT_ADHERENCE_RATE,
        },
    )

    df["adhered_90d"] = rng.binomial(1, adherence_probability).astype(int)

    churn_probability = np.full(cohort_size, CONTROL_CHURN_BASE, dtype=float)

    churn_probability += np.where(
        df["engagement_score_day7"] < 3,
        CHURN_MODIFIER_LOW_ENGAGEMENT,
        0,
    )

    churn_probability += np.where(
        df["days_to_first_lab"] > 25,
        CHURN_MODIFIER_LONG_LAB_DAYS,
        0,
    )

    churn_probability += np.where(
        df["testosterone_tier"].eq("Borderline"),
        CHURN_MODIFIER_BORDERLINE,
        0,
    )

    churn_probability += np.where(
        df["subscription_plan"].eq("Standard"),
        CHURN_MODIFIER_STANDARD_PLAN,
        0,
    )

    churn_probability += np.where(
        df["prior_telehealth_experience"].eq(0),
        CHURN_MODIFIER_NO_PRIOR_TELEHEALTH,
        0,
    )

    churn_probability += np.where(
        df["experiment_arm"].eq("Treatment"),
        -TREATMENT_CHURN_REDUCTION,
        0,
    )

    # Continuous engagement signal:
    # Gives logistic regression a smooth, learnable relationship rather than only
    # a sparse binary cutoff. Higher engagement lowers churn risk.
    churn_probability -= 0.025 * df["engagement_score_day7"]

    # Medium lab-delay signal:
    # Extends churn risk signal beyond the binary >25-day long-delay threshold.
    churn_probability += 0.15 * (
        (df["days_to_first_lab"] > 12) & (df["days_to_first_lab"] <= 25)
    )

    churn_probability = _calibrate_probability_by_arm(
        churn_probability,
        df["experiment_arm"],
        {
            "Control": TARGET_CONTROL_CHURN_RATE,
            "Treatment": TARGET_TREATMENT_CHURN_RATE,
        },
    )

    df["churned_30d"] = rng.binomial(1, churn_probability).astype(int)

    appointment_probability = np.full(cohort_size, APPOINTMENT_BASE, dtype=float)

    appointment_probability += np.where(
        df["experiment_arm"].eq("Treatment"),
        TREATMENT_APPOINTMENT_LIFT,
        0,
    )

    appointment_probability += np.where(
        df["engagement_score_day7"] > 7,
        APPOINTMENT_MODIFIER_HIGH_ENGAGEMENT,
        0,
    )

    appointment_probability += np.where(
        df["churned_30d"].eq(1),
        APPOINTMENT_MODIFIER_CHURNED,
        0,
    )

    appointment_probability += np.where(
        df["subscription_plan"].eq("Premium"),
        APPOINTMENT_MODIFIER_PREMIUM,
        0,
    )

    appointment_probability = np.clip(
        appointment_probability,
        PROBABILITY_FLOOR,
        PROBABILITY_CEILING,
    )

    df["completed_appointment_90d"] = rng.binomial(1, appointment_probability).astype(int)

    satisfaction_response_mask = rng.binomial(
        n=1,
        p=SATISFACTION_RESPONSE_RATE,
        size=cohort_size,
    ).astype(bool)

    satisfaction_scores = np.full(cohort_size, np.nan)
    satisfaction_values = np.arange(1, 6)

    for arm, satisfaction_probs in {
        "Control": SATISFACTION_CONTROL_PROBS,
        "Treatment": SATISFACTION_TREATMENT_PROBS,
    }.items():
        arm_response_mask = df["experiment_arm"].eq(arm).to_numpy() & satisfaction_response_mask

        satisfaction_scores[arm_response_mask] = rng.choice(
            satisfaction_values,
            size=arm_response_mask.sum(),
            p=satisfaction_probs,
        )

    df["satisfaction_score_day45"] = satisfaction_scores

    return df[EXPECTED_COLUMNS]


def export_cohort(df: pd.DataFrame, csv_path: str, db_path: str) -> None:
    """
    Export the synthetic cohort to CSV and SQLite.

    Parameters
    ----------
    df : pd.DataFrame
        Fully generated synthetic cohort.
    csv_path : str
        Output CSV path.
    db_path : str
        Output SQLite database path.
    """
    csv_output_path = Path(csv_path)
    db_output_path = Path(db_path)

    csv_output_path.parent.mkdir(parents=True, exist_ok=True)
    db_output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(csv_output_path, index=False)

    with sqlite3.connect(db_output_path) as connection:
        df.to_sql(
            "patient_cohort",
            connection,
            if_exists="replace",
            index=False,
        )


def print_validation_summary(df: pd.DataFrame) -> None:
    """
    Print the Phase 1 validation summary required by the project blueprint.
    """
    print("\n" + "=" * 80)
    print("PHASE 1 VALIDATION SUMMARY")
    print("=" * 80)

    print("\nDataset shape:")
    print(df.shape)

    print("\nExpected column count:")
    print(len(EXPECTED_COLUMNS))

    print("\nAll expected columns present:")
    missing_columns = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
    else:
        print("Yes")

    print("\nMissing value counts:")
    print(df.isna().sum())

    non_satisfaction_missing = df.drop(columns=["satisfaction_score_day45"]).isna().sum().sum()
    satisfaction_missing = df["satisfaction_score_day45"].isna().sum()

    print("\nMissing value rule check:")
    print(f"Non-satisfaction missing values: {non_satisfaction_missing}")
    print(f"satisfaction_score_day45 missing values: {satisfaction_missing}")

    print("\nExperiment arm counts:")
    print(df["experiment_arm"].value_counts())

    print("\nOutcome rates by experiment arm:")
    outcome_summary = df.groupby("experiment_arm").agg(
        patient_count=("patient_id", "count"),
        adherence_rate_90d=("adhered_90d", "mean"),
        churn_rate_30d=("churned_30d", "mean"),
        appointment_completion_rate_90d=("completed_appointment_90d", "mean"),
        avg_satisfaction_score_day45=("satisfaction_score_day45", "mean"),
    )
    print(outcome_summary.round(4))

    control_adherence = outcome_summary.loc["Control", "adherence_rate_90d"]
    treatment_adherence = outcome_summary.loc["Treatment", "adherence_rate_90d"]
    control_churn = outcome_summary.loc["Control", "churn_rate_30d"]
    treatment_churn = outcome_summary.loc["Treatment", "churn_rate_30d"]

    print("\nDirectional outcome checks:")
    print(f"Treatment adherence higher than Control: {treatment_adherence > control_adherence}")
    print(f"Treatment churn lower than Control: {treatment_churn < control_churn}")

    print("\nAge group distribution:")
    print(df["age_group"].value_counts().sort_index())

    print("\nTreatment goal distribution - counts:")
    print(df["treatment_goal"].value_counts())

    print("\nTreatment goal distribution - proportions:")
    print(df["treatment_goal"].value_counts(normalize=True).round(4))

    print("\nTestosterone tier distribution:")
    print(df["testosterone_tier"].value_counts())

    print("\nChurn rate by key modeling signals:")

    engagement_group = pd.cut(
        df["engagement_score_day7"],
        bins=[-0.01, 3, 7, 10],
        labels=["Low engagement", "Medium engagement", "High engagement"],
    )
    print("\nEngagement group churn:")
    print(df.groupby(engagement_group, observed=True)["churned_30d"].mean().round(3))

    lab_delay_group = pd.cut(
        df["days_to_first_lab"],
        bins=[0, 7, 20, 60],
        labels=["Fast lab", "Normal lab", "Delayed lab"],
    )
    print("\nLab delay group churn:")
    print(df.groupby(lab_delay_group, observed=True)["churned_30d"].mean().round(3))

    print("\nChurn by testosterone tier:")
    print(df.groupby("testosterone_tier")["churned_30d"].mean().round(3))

    print("\nChurn by subscription plan:")
    print(df.groupby("subscription_plan")["churned_30d"].mean().round(3))

    print("\nChurn by prior telehealth experience:")
    print(df.groupby("prior_telehealth_experience")["churned_30d"].mean().round(3))

    print("\nPhase 1 completion checks:")
    checks = {
        "Dataset has 2,000 rows": len(df) == 2000,
        "Expected columns are present": len(missing_columns) == 0,
        "Only satisfaction_score_day45 has missing values": non_satisfaction_missing == 0
        and satisfaction_missing > 0,
        "Arm counts are exactly balanced": df["experiment_arm"].value_counts().nunique() == 1,
        "Treatment adherence is higher than Control": treatment_adherence > control_adherence,
        "Treatment churn is lower than Control": treatment_churn < control_churn,
    }

    for check_name, check_value in checks.items():
        print(f"{check_name}: {check_value}")

    print("=" * 80 + "\n")