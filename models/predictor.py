"""
Prediction interface for the TWINSHIELD calibrated baseline.

This module provides a stable interface for:
- training and saving the calibrated model
- loading the trained model
- predicting next-step SLA-violation risk
"""

from pathlib import Path

import joblib
import pandas as pd

from models.baseline import (
    FEATURE_COLUMNS,
    train_calibrated_baseline,
)


MODEL_PATH = Path(
    "models/artifacts/twinshield_calibrated_baseline.joblib"
)


def train_and_save_model(train_rows, model_path=MODEL_PATH):
    """
    Train the calibrated baseline model and save it to disk.
    """
    model = train_calibrated_baseline(train_rows)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    return model


def load_model(model_path=MODEL_PATH):
    """
    Load a previously saved calibrated model.
    """
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model file not found: {model_path}. "
            "Train and save the model first."
        )

    return joblib.load(model_path)


def predict_risk(model, telemetry_row):
    """
    Predict next-step SLA-violation risk for one telemetry row.

    The uncertainty score is a simple probability-ambiguity proxy:
    - near 0.0 or 1.0 probability -> low uncertainty
    - near 0.5 probability -> high uncertainty

    This is not a substitute for ensemble, Bayesian, or
    conformal uncertainty estimation.
    """
    missing_features = [
        column
        for column in FEATURE_COLUMNS
        if column not in telemetry_row
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    feature_row = {
        column: telemetry_row[column]
        for column in FEATURE_COLUMNS
    }

    dataframe = pd.DataFrame([feature_row])

    probability = float(
        model.predict_proba(dataframe)[0, 1]
    )

    # Probability-based ambiguity:
    # 0.0 means highly decisive, 1.0 means maximally ambiguous.
    uncertainty_score = 1.0 - abs(
        2.0 * probability - 1.0
    )

    confidence_score = 1.0 - uncertainty_score

    if probability < 0.30:
        risk_category = "low"
    elif probability < 0.70:
        risk_category = "medium"
    else:
        risk_category = "high"

    # Abstain when the probability is too close to the decision boundary.
    if 0.40 <= probability <= 0.60:
        decision_status = "abstain"
    else:
        decision_status = "predict"

    return {
        "flow_id": telemetry_row["flow_id"],
        "timestamp": int(telemetry_row["timestamp"]),
        "predicted_sla_violation_probability": round(
            probability,
            6,
        ),
        "risk_category": risk_category,
        "uncertainty_score": round(
            uncertainty_score,
            6,
        ),
        "confidence_score": round(
            confidence_score,
            6,
        ),
        "decision_status": decision_status,
        "model_type": "calibrated_logistic_regression",
    }

def predict_sla_risk(model, telemetry_row):
    """
    Return the predicted SLA-violation risk in a compact format
    suitable for integration with the action evaluator.
    """
    prediction = predict_risk(model, telemetry_row)

    return {
        "predicted_sla_violation_probability": (
            prediction["predicted_sla_violation_probability"]
        ),
        "risk_category": prediction["risk_category"],
        "uncertainty_score": prediction["uncertainty_score"],
        "confidence_score": prediction["confidence_score"],
        "decision_status": prediction["decision_status"],
    }