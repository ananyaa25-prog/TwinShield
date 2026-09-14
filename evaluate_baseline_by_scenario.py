"""
Evaluate the TWINSHIELD baseline separately for each scenario.
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

    model = train_baseline(train_rows)

    threshold_result = select_threshold_by_f1(
        model,
        validation_rows,
    )

    threshold = threshold_result["threshold"]

    print("Selected threshold:", threshold)
    print("\nPer-scenario test performance")
    print("=" * 70)

    scenarios = sorted(
        set(row["scenario_id"] for row in test_rows)
    )

    for scenario_id in scenarios:
        scenario_rows = [
            row
            for row in test_rows
            if row["scenario_id"] == scenario_id
        ]

        metrics = evaluate_model(
            model,
            scenario_rows,
            threshold=threshold,
        )

        print(f"\nScenario: {scenario_id}")
        print("-" * 40)
        print("Rows:", len(scenario_rows))
        print("Accuracy:", round(metrics["accuracy"], 4))
        print("Precision:", round(metrics["precision"], 4))
        print("Recall:", round(metrics["recall"], 4))
        print("F1:", round(metrics["f1"], 4))
        print("ROC-AUC:", metrics["roc_auc"])
        print("PR-AUC:", metrics["pr_auc"])
        print(
            "Confusion matrix:",
            metrics["confusion_matrix"],
        )


if __name__ == "__main__":
    main()