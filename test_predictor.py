"""
Test the TWINSHIELD calibrated prediction API.
"""

import csv

from models.predictor import (
    load_model,
    predict_risk,
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

    model = load_model()

    # Use the first telemetry row as an API test input.
    telemetry_row = rows[0]

    prediction = predict_risk(
        model,
        telemetry_row,
    )

    print("Input telemetry:")
    print(telemetry_row)

    print("\nPrediction response:")
    for key, value in prediction.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()