"""
Train and save the TWINSHIELD calibrated prediction model.
"""

import csv

from simulation.splits import split_rows_by_episode
from models.predictor import train_and_save_model


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

    train_rows, validation_rows, test_rows = split_rows_by_episode(
        rows
    )

    print("Total rows:", len(rows))
    print("Training rows:", len(train_rows))
    print("Validation rows:", len(validation_rows))
    print("Test rows:", len(test_rows))

    print("\nTraining calibrated predictor...")
    train_and_save_model(train_rows)

    print(
        "\nSaved calibrated model to "
        "models/artifacts/"
        "twinshield_calibrated_baseline.joblib"
    )


if __name__ == "__main__":
    main()