"""
Test the TWINSHIELD calibrated predictor across scenarios.
"""

import csv

from models.predictor import load_model, predict_risk


DATA_PATH = "data/twinshield_telemetry_targets.csv"


def load_rows(path):
    with open(
        path,
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


def select_row(rows, scenario_id, flow_id="f1", timestamp="1"):
    """
    Select one representative telemetry row.
    """
    for row in rows:
        if (
            row["scenario_id"] == scenario_id
            and row["flow_id"] == flow_id
            and row["timestamp"] == timestamp
        ):
            return row

    raise ValueError(
        f"No row found for scenario={scenario_id}, "
        f"flow={flow_id}, timestamp={timestamp}"
    )


def main():
    rows = load_rows(DATA_PATH)
    model = load_model()

    scenarios = [
        "normal",
        "shared_bottleneck",
        "background_surge",
    ]

    print("Testing calibrated predictor across scenarios")
    print("=" * 70)

    for scenario_id in scenarios:
        telemetry_row = select_row(
            rows,
            scenario_id=scenario_id,
            flow_id="f1",
            timestamp="1",
        )

        prediction = predict_risk(
            model,
            telemetry_row,
        )

        print(f"\nScenario: {scenario_id}")
        print(f"Flow: {prediction['flow_id']}")
        print(f"Timestamp: {prediction['timestamp']}")
        print(
              "Predicted SLA-violation probability: "
              f"{prediction['predicted_sla_violation_probability']}"
            )
        print(f"Risk category: {prediction['risk_category']}")
        print(
           "Uncertainty score: "
           f"{prediction['uncertainty_score']}"
             )
        print(
           "Confidence score: "
           f"{prediction['confidence_score']}"
        )
        print(
          "Decision status: "
          f"{prediction['decision_status']}"
        )
        print(
          "Actual next-step target: "
          f"{telemetry_row['target_sla_violation_next_step']}"
        )


if __name__ == "__main__":
    main()