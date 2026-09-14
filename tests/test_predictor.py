"""
Formal tests for the TWINSHIELD prediction API.
"""

import csv
from pathlib import Path

import pytest

from models.predictor import load_model, predict_risk


DATA_PATH = "data/twinshield_telemetry_targets.csv"
MODEL_PATH = Path(
    "models/artifacts/twinshield_calibrated_baseline.joblib"
)



def load_rows(path):
    with open(
        path,
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


@pytest.fixture(scope="module")
def model():
    return load_model(MODEL_PATH)


@pytest.fixture(scope="module")
def telemetry_row():
    rows = load_rows(DATA_PATH)
    return rows[0]


def test_prediction_returns_required_fields(model, telemetry_row):
    prediction = predict_risk(model, telemetry_row)

    required_fields = {
        "flow_id",
        "timestamp",
        "predicted_sla_violation_probability",
        "risk_category",
        "uncertainty_score",
        "confidence_score",
        "decision_status",
        "model_type",
    }

    assert required_fields.issubset(prediction.keys())


def test_probability_is_between_zero_and_one(model, telemetry_row):
    prediction = predict_risk(model, telemetry_row)

    probability = prediction[
        "predicted_sla_violation_probability"
    ]

    assert 0.0 <= probability <= 1.0


def test_uncertainty_and_confidence_are_valid(model, telemetry_row):
    prediction = predict_risk(model, telemetry_row)

    uncertainty = prediction["uncertainty_score"]
    confidence = prediction["confidence_score"]

    assert 0.0 <= uncertainty <= 1.0
    assert 0.0 <= confidence <= 1.0

    # For the current ambiguity proxy, they should sum to 1.
    assert uncertainty + confidence == pytest.approx(1.0)


def test_risk_category_is_valid(model, telemetry_row):
    prediction = predict_risk(model, telemetry_row)

    assert prediction["risk_category"] in {
        "low",
        "medium",
        "high",
    }


def test_decision_status_is_valid(model, telemetry_row):
    prediction = predict_risk(model, telemetry_row)

    assert prediction["decision_status"] in {
        "predict",
        "abstain",
    }


def test_missing_feature_raises_error(model, telemetry_row):
    incomplete_row = dict(telemetry_row)

    del incomplete_row["delay_ms"]

    with pytest.raises(ValueError, match="Missing required features"):
        predict_risk(model, incomplete_row)


def test_prediction_is_deterministic(model, telemetry_row):
    first_prediction = predict_risk(model, telemetry_row)
    second_prediction = predict_risk(model, telemetry_row)

    assert first_prediction == second_prediction