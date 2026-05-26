"""
Synthetic data generation constants for the Telehealth Patient Engagement
A/B Testing and Churn Prediction Engine.

This file intentionally contains only named constants. All assumptions that
control the synthetic cohort, experiment effect, churn behavior, appointment
completion, satisfaction response, and validation targets live here.
"""

# ---------------------------------------------------------------------------
# Reproducibility and cohort size
# ---------------------------------------------------------------------------

RANDOM_SEED = 42
COHORT_SIZE = 2000


# ---------------------------------------------------------------------------
# Demographic assumptions
# ---------------------------------------------------------------------------

AGE_MEAN = 38
AGE_STD = 9
AGE_MIN = 25
AGE_MAX = 65


# ---------------------------------------------------------------------------
# Testosterone assumptions
# ---------------------------------------------------------------------------

TESTOSTERONE_MEAN = 320
TESTOSTERONE_STD = 85
TESTOSTERONE_MIN = 150
TESTOSTERONE_MAX = 500

TESTOSTERONE_TIER_LOW_MAX = 250
TESTOSTERONE_TIER_LOW_NORMAL_MAX = 350


# ---------------------------------------------------------------------------
# Patient mix assumptions
# ---------------------------------------------------------------------------

TREATMENT_GOAL_PROBS = {
    "Energy": 0.35,
    "Libido": 0.30,
    "Body Composition": 0.25,
    "General Wellness": 0.10,
}

SUBSCRIPTION_PLAN_PROBS = {
    "Standard": 0.70,
    "Premium": 0.30,
}

PRIOR_TELEHEALTH_PROB = 0.45


# ---------------------------------------------------------------------------
# Early patient journey assumptions
# ---------------------------------------------------------------------------

DAYS_TO_LAB_GAMMA_SHAPE = 2
DAYS_TO_LAB_GAMMA_SCALE = 6
DAYS_TO_LAB_MIN = 1
DAYS_TO_LAB_MAX = 60

ENGAGEMENT_SCORE_BETA_A = 2
ENGAGEMENT_SCORE_BETA_B = 1.5

ENGAGEMENT_PREMIUM_BONUS = 0.5
ENGAGEMENT_PRIOR_TELEHEALTH_BONUS = 0.4

SUPPORT_CONTACTS_LAMBDA = 1.8


# ---------------------------------------------------------------------------
# Primary outcome: 90-day adherence assumptions
# ---------------------------------------------------------------------------

CONTROL_ADHERENCE_BASE = 0.54
TREATMENT_BASE_LIFT = 0.08

ADHERENCE_MODIFIER_HIGH_ENGAGEMENT = 0.08
ADHERENCE_MODIFIER_LOW_LAB_DAYS = 0.05
ADHERENCE_MODIFIER_LONG_LAB_DAYS = -0.06
ADHERENCE_MODIFIER_LOW_TESTOSTERONE = 0.04
ADHERENCE_MODIFIER_BORDERLINE = -0.05
ADHERENCE_MODIFIER_PREMIUM = 0.04
ADHERENCE_MODIFIER_PRIOR_TELEHEALTH = 0.03

ADHERENCE_TREATMENT_HIGH_ENGAGEMENT_BONUS = 0.04
ADHERENCE_TREATMENT_GOAL_BONUS = 0.03

TARGET_CONTROL_ADHERENCE_RATE = 0.54
TARGET_TREATMENT_ADHERENCE_RATE = 0.62


# ---------------------------------------------------------------------------
# Secondary outcome: 30-day churn assumptions
# ---------------------------------------------------------------------------

CONTROL_CHURN_BASE = 0.05
TREATMENT_CHURN_REDUCTION = 0.03

CHURN_MODIFIER_LOW_ENGAGEMENT = 0.35
CHURN_MODIFIER_LONG_LAB_DAYS = 0.28
CHURN_MODIFIER_BORDERLINE = 0.15
CHURN_MODIFIER_STANDARD_PLAN = 0.12
CHURN_MODIFIER_NO_PRIOR_TELEHEALTH = 0.12

TARGET_CONTROL_CHURN_RATE = 0.18
TARGET_TREATMENT_CHURN_RATE = 0.15


# ---------------------------------------------------------------------------
# Secondary outcome: 90-day appointment completion assumptions
# ---------------------------------------------------------------------------

APPOINTMENT_BASE = 0.62
TREATMENT_APPOINTMENT_LIFT = 0.07
APPOINTMENT_MODIFIER_HIGH_ENGAGEMENT = 0.05
APPOINTMENT_MODIFIER_CHURNED = -0.08
APPOINTMENT_MODIFIER_PREMIUM = 0.04


# ---------------------------------------------------------------------------
# Secondary outcome: day-45 satisfaction assumptions
# ---------------------------------------------------------------------------

SATISFACTION_RESPONSE_RATE = 0.60
SATISFACTION_CONTROL_MEAN = 3.6
SATISFACTION_TREATMENT_MEAN = 3.9

SATISFACTION_CONTROL_PROBS = [0.05, 0.10, 0.30, 0.35, 0.20]
SATISFACTION_TREATMENT_PROBS = [0.03, 0.08, 0.22, 0.39, 0.28]


# ---------------------------------------------------------------------------
# Probability clipping assumptions
# ---------------------------------------------------------------------------

PROBABILITY_FLOOR = 0.05
PROBABILITY_CEILING = 0.97