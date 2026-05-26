"""
Stratified experiment randomization utilities.

The experiment arm is assigned after pre-treatment patient features are created
and before outcomes are generated.
"""

import numpy as np
import pandas as pd


def assign_experiment_arms(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """
    Assign Control/Treatment experiment arms using stratified randomization.

    Stratification variables:
    - age_group
    - treatment_goal
    - testosterone_tier

    The implementation keeps the overall cohort exactly balanced when the
    cohort size is even, while maintaining near-50/50 assignment inside each
    stratum.

    Parameters
    ----------
    df : pd.DataFrame
        Patient-level DataFrame before outcomes are generated.
    seed : int
        Random seed for reproducible assignment.

    Returns
    -------
    pd.DataFrame
        Copy of the input DataFrame with experiment_arm added.
    """
    required_columns = ["age_group", "treatment_goal", "testosterone_tier"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required stratification columns: {missing_columns}")

    randomized_df = df.copy()
    rng = np.random.default_rng(seed)

    randomized_df["_stratum_key"] = (
        randomized_df["age_group"].astype(str)
        + "_"
        + randomized_df["treatment_goal"].astype(str)
        + "_"
        + randomized_df["testosterone_tier"].astype(str)
    )

    randomized_df["experiment_arm"] = ""

    odd_stratum_counter = 0

    for _, group_indices in randomized_df.groupby("_stratum_key", sort=True).groups.items():
        shuffled_indices = np.array(list(group_indices))
        rng.shuffle(shuffled_indices)

        group_size = len(shuffled_indices)
        control_count = group_size // 2
        treatment_count = group_size // 2

        if group_size % 2 == 1:
            if odd_stratum_counter % 2 == 0:
                control_count += 1
            else:
                treatment_count += 1
            odd_stratum_counter += 1

        control_indices = shuffled_indices[:control_count]
        treatment_indices = shuffled_indices[control_count : control_count + treatment_count]

        randomized_df.loc[control_indices, "experiment_arm"] = "Control"
        randomized_df.loc[treatment_indices, "experiment_arm"] = "Treatment"

    target_per_arm = len(randomized_df) // 2
    arm_counts = randomized_df["experiment_arm"].value_counts()

    if len(randomized_df) % 2 == 0 and arm_counts.get("Control", 0) > target_per_arm:
        excess = arm_counts["Control"] - target_per_arm
        flip_indices = randomized_df[randomized_df["experiment_arm"] == "Control"].sample(
            n=excess,
            random_state=seed + 999,
        ).index
        randomized_df.loc[flip_indices, "experiment_arm"] = "Treatment"

    elif len(randomized_df) % 2 == 0 and arm_counts.get("Treatment", 0) > target_per_arm:
        excess = arm_counts["Treatment"] - target_per_arm
        flip_indices = randomized_df[randomized_df["experiment_arm"] == "Treatment"].sample(
            n=excess,
            random_state=seed + 999,
        ).index
        randomized_df.loc[flip_indices, "experiment_arm"] = "Control"

    randomized_df = randomized_df.drop(columns=["_stratum_key"])

    return randomized_df