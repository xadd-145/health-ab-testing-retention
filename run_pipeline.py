"""
Run the Phase 1 synthetic data generation pipeline.

This script generates the synthetic patient cohort, exports it to CSV and
SQLite, and prints validation checks.
"""

import sqlite3
from pathlib import Path

import pandas as pd

from src.data_generation.distributions import COHORT_SIZE, RANDOM_SEED
from src.data_generation.generate_cohort import (
    export_cohort,
    generate_cohort,
    print_validation_summary,
)


CSV_OUTPUT_PATH = "data/processed/synthetic_patient_cohort.csv"
DB_OUTPUT_PATH = "outputs/hone_synthetic.db"


def verify_outputs(csv_path: str, db_path: str) -> None:
    """
    Verify that expected Phase 1 output files and SQLite table exist.
    """
    csv_file = Path(csv_path)
    db_file = Path(db_path)

    if not csv_file.exists():
        raise FileNotFoundError(f"CSV output not found: {csv_file}")

    if not db_file.exists():
        raise FileNotFoundError(f"SQLite output not found: {db_file}")

    csv_df = pd.read_csv(csv_file)

    with sqlite3.connect(db_file) as connection:
        table_check = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'patient_cohort';
            """,
            connection,
        )

        if table_check.empty:
            raise RuntimeError("SQLite table patient_cohort was not created.")

        row_count = pd.read_sql_query(
            "SELECT COUNT(*) AS row_count FROM patient_cohort;",
            connection,
        )["row_count"].iloc[0]

    print("\nOutput file checks:")
    print(f"CSV exists: {csv_file.exists()} -> {csv_file}")
    print(f"SQLite database exists: {db_file.exists()} -> {db_file}")
    print("SQLite table exists: patient_cohort")
    print(f"CSV row count: {len(csv_df)}")
    print(f"SQLite patient_cohort row count: {row_count}")


def main() -> None:
    """
    Execute the complete Phase 1 data generation pipeline.
    """
    print("Starting Phase 1 data generation pipeline...")

    cohort = generate_cohort(
        cohort_size=COHORT_SIZE,
        seed=RANDOM_SEED,
    )

    export_cohort(
        df=cohort,
        csv_path=CSV_OUTPUT_PATH,
        db_path=DB_OUTPUT_PATH,
    )

    print_validation_summary(cohort)
    verify_outputs(CSV_OUTPUT_PATH, DB_OUTPUT_PATH)

    print("\nPhase 1 pipeline completed successfully.")


if __name__ == "__main__":
    main()