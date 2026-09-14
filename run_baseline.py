"""
Train and evaluate the TWINSHIELD Logistic Regression baseline.
"""

import csv

from simulation.splits import split_rows_by_episode
from models.baseline import (
    train_baseline,
    evaluate_model,
    select_threshold_by_f1,
)


DATA_PATH = "data/twinshield_telemetry_targets.csv"


def load_rows(path):
    """
    Load CSV rows as a list of dictionaries.
    """

    with open(
        path,
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


def main():
    rows = load_rows(DATA_PATH)

    train_rows, validation_rows, test_rows = (
        split_rows_by_episode(rows)
    )

    print("Dataset summary")
    print("----------------")
    print("Total rows:", len(rows))
    print("Train rows:", len(train_rows))
    print("Validation rows:", len(validation_rows))
    print("Test rows:", len(test_rows))

    print("\nTraining Logistic Regression baseline...")
    model = train_baseline(train_rows)

    print("Training completed.")

    threshold_result = select_threshold_by_f1(
        model,
        validation_rows,
    )

    threshold = threshold_result["threshold"]
    validation_f1 = threshold_result["validation_f1"]

    print("\nThreshold selection")
    print("-------------------")
    print("Selected threshold:", threshold)
    print("Validation F1:", round(validation_f1, 4))

    validation_metrics = evaluate_model(
        model,
        validation_rows,
        threshold=threshold,
    )

    test_metrics = evaluate_model(
        model,
        test_rows,
        threshold=threshold,
    )

    print("\nValidation metrics")
    print("------------------")
    print("Accuracy:", round(validation_metrics["accuracy"], 4))
    print("Precision:", round(validation_metrics["precision"], 4))
    print("Recall:", round(validation_metrics["recall"], 4))
    print("F1:", round(validation_metrics["f1"], 4))
    print("ROC-AUC:", validation_metrics["roc_auc"])
    print("PR-AUC:", validation_metrics["pr_auc"])
    print(
        "Confusion matrix:",
        validation_metrics["confusion_matrix"],
    )

    print("\nTest metrics")
    print("------------")
    print("Accuracy:", round(test_metrics["accuracy"], 4))
    print("Precision:", round(test_metrics["precision"], 4))
    print("Recall:", round(test_metrics["recall"], 4))
    print("F1:", round(test_metrics["f1"], 4))
    print("ROC-AUC:", test_metrics["roc_auc"])
    print("PR-AUC:", test_metrics["pr_auc"])
    print(
        "Confusion matrix:",
        test_metrics["confusion_matrix"],
    )

    print("\nDetailed test classification report")
    print("------------------------------------")
    print(test_metrics["classification_report"])


if __name__ == "__main__":
    main()