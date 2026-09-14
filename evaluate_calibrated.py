"""
Compare the original and calibrated TWINSHIELD baseline probabilities.
"""

import csv

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss, roc_auc_score, average_precision_score

from simulation.splits import split_rows_by_episode
from models.baseline import (
    train_baseline,
    predict_probabilities,
)

DATA_PATH = "data/twinshield_telemetry_targets.csv"


def load_rows(path):
    with open(path, mode="r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def get_targets(rows):
    return np.array([
        1
        if str(row["target_sla_violation_next_step"]).lower() == "true"
        else 0
        for row in rows
    ])


def print_metrics(name, rows, probabilities):
    targets = get_targets(rows)

    brier = brier_score_loss(targets, probabilities)

    print(f"\n{name}")
    print("-" * 60)
    print("Rows:", len(rows))
    print("Positive targets:", int(targets.sum()))
    print("Brier score:", round(brier, 6))

    if len(np.unique(targets)) == 2:
        print("ROC-AUC:", round(roc_auc_score(targets, probabilities), 6))
        print(
            "PR-AUC:",
            round(average_precision_score(targets, probabilities), 6),
        )
    else:
        print("ROC-AUC: None")
        print("PR-AUC: None")


def main():
    rows = load_rows(DATA_PATH)

    train_rows, validation_rows, test_rows = split_rows_by_episode(rows)

    print("Training original baseline...")
    original_model = train_baseline(train_rows)

    # Original, uncalibrated probabilities
    original_test_probabilities = predict_probabilities(
        original_model,
        test_rows,
    )

    # Calibrate the already-trained baseline using cross-validation
    # on the training data.
    print("Training calibrated baseline...")

    calibrated_model = CalibratedClassifierCV(
        estimator=original_model,
        method="sigmoid",
        cv=5,
    )

    # Convert training rows into the format expected by the pipeline.
    from models.baseline import rows_to_dataframe

    train_dataframe = rows_to_dataframe(train_rows)

    X_train = train_dataframe.drop(
        columns=["target_sla_violation_next_step"]
    )
    y_train = train_dataframe["target_sla_violation_next_step"]

    calibrated_model.fit(X_train, y_train)

    calibrated_test_probabilities = calibrated_model.predict_proba(
        rows_to_dataframe(test_rows).drop(
            columns=["target_sla_violation_next_step"]
        )
    )[:, 1]

    print_metrics(
        "Original baseline - Test",
        test_rows,
        original_test_probabilities,
    )

    print_metrics(
        "Calibrated baseline - Test",
        test_rows,
        calibrated_test_probabilities,
    )


if __name__ == "__main__":
    main()