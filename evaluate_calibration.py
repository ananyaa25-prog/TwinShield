"""
Evaluate probability calibration for the TWINSHIELD baseline.

This script evaluates whether predicted SLA-violation probabilities
correspond reasonably well to observed outcomes.
"""

import csv

import numpy as np
from sklearn.metrics import brier_score_loss
from sklearn.calibration import calibration_curve

from simulation.splits import split_rows_by_episode
from models.baseline import (
    train_baseline,
    predict_probabilities,
)


DATA_PATH = "data/twinshield_telemetry_targets.csv"


def load_rows(path):
    """
    Load target-enhanced telemetry rows from CSV.
    """

    with open(
        path,
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


def get_targets(rows):
    """
    Extract binary target values from dataset rows.
    """

    return np.array(
        [
            1
            if str(row[
                "target_sla_violation_next_step"
            ]).lower() == "true"
            else 0
            for row in rows
        ]
    )


def print_calibration_summary(
    name,
    rows,
    probabilities,
    number_of_bins=5,
):
    """
    Print Brier score and calibration-bin statistics.
    """

    targets = get_targets(rows)

    brier_score = brier_score_loss(
        targets,
        probabilities,
    )

    fraction_of_positives, mean_predicted_values = (
        calibration_curve(
            targets,
            probabilities,
            n_bins=number_of_bins,
            strategy="uniform",
        )
    )

    print(f"\n{name}")
    print("-" * 60)
    print("Rows:", len(rows))
    print("Positive targets:", int(targets.sum()))
    print("Brier score:", round(brier_score, 6))

    print("\nCalibration bins")
    print("Bin | Mean predicted probability | Actual positive fraction")

    for index, (
        predicted_value,
        actual_fraction,
    ) in enumerate(
        zip(
            mean_predicted_values,
            fraction_of_positives,
        ),
        start=1,
    ):
        print(
            f"{index:>3} | "
            f"{predicted_value:>26.4f} | "
            f"{actual_fraction:>22.4f}"
        )


def main():
    rows = load_rows(DATA_PATH)

    train_rows, validation_rows, test_rows = (
        split_rows_by_episode(rows)
    )

    print("Training baseline...")
    model = train_baseline(train_rows)

    validation_probabilities = predict_probabilities(
        model,
        validation_rows,
    )

    test_probabilities = predict_probabilities(
        model,
        test_rows,
    )

    print_calibration_summary(
        "Validation calibration",
        validation_rows,
        validation_probabilities,
    )

    print_calibration_summary(
        "Test calibration",
        test_rows,
        test_probabilities,
    )


if __name__ == "__main__":
    main()