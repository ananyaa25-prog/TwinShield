"""
Baseline SLA-violation prediction model for TWINSHIELD.

This module provides a Logistic Regression baseline for predicting
whether a flow will experience an SLA violation in the next step.
"""

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET_COLUMN = "target_sla_violation_next_step"

FEATURE_COLUMNS = [
    "timestamp",
    "rate_mbps",
    "throughput_mbps",
    "delay_ms",
    "packet_loss",
    "max_link_utilization",
    "max_queue_delay_ms",
    "flow_id",
]


def rows_to_dataframe(rows):
    """
    Convert dataset rows into a cleaned pandas DataFrame.
    """

    dataframe = pd.DataFrame(rows)

    if dataframe.empty:
        raise ValueError("Input rows cannot be empty.")

    required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    numeric_columns = [
        "timestamp",
        "rate_mbps",
        "throughput_mbps",
        "delay_ms",
        "packet_loss",
        "max_link_utilization",
        "max_queue_delay_ms",
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="raise",
        )

    dataframe[TARGET_COLUMN] = (
        dataframe[TARGET_COLUMN]
        .astype(str)
        .str.lower()
        .map({"true": 1, "false": 0})
    )

    if dataframe[TARGET_COLUMN].isna().any():
        raise ValueError(
            f"Invalid values found in {TARGET_COLUMN}."
        )

    dataframe[TARGET_COLUMN] = (
        dataframe[TARGET_COLUMN].astype(int)
    )

    return dataframe


def build_logistic_regression_pipeline():
    """
    Build the Logistic Regression baseline pipeline.

    Numeric features are standardized.
    flow_id is one-hot encoded.
    """

    numeric_features = [
        "timestamp",
        "rate_mbps",
        "throughput_mbps",
        "delay_ms",
        "packet_loss",
        "max_link_utilization",
        "max_queue_delay_ms",
    ]

    categorical_features = [
        "flow_id",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                StandardScaler(),
                numeric_features,
            ),
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features,
            ),
        ]
    )

    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def train_baseline(train_rows):
    """
    Train the Logistic Regression baseline.

    Parameters
    ----------
    train_rows : list of dict
        Rows belonging only to training episodes.

    Returns
    -------
    Pipeline
        Trained Logistic Regression pipeline.
    """

    dataframe = rows_to_dataframe(train_rows)

    X_train = dataframe[FEATURE_COLUMNS]
    y_train = dataframe[TARGET_COLUMN]

    model = build_logistic_regression_pipeline()
    model.fit(X_train, y_train)

    return model


def predict_probabilities(model, rows):
    """
    Predict the probability of next-step SLA violation.
    """

    dataframe = rows_to_dataframe(rows)
    X = dataframe[FEATURE_COLUMNS]

    probabilities = model.predict_proba(X)[:, 1]

    return probabilities


def evaluate_model(model, rows, threshold=0.5):
    """
    Evaluate the model on a dataset split.

    Parameters
    ----------
    model : Pipeline
        Trained model.

    rows : list of dict
        Validation or test rows.

    threshold : float
        Probability threshold for converting probabilities
        into binary predictions.

    Returns
    -------
    dict
        Evaluation metrics.
    """

    dataframe = rows_to_dataframe(rows)

    X = dataframe[FEATURE_COLUMNS]
    y_true = dataframe[TARGET_COLUMN]

    probabilities = model.predict_proba(X)[:, 1]
    predictions = (
        probabilities >= threshold
    ).astype(int)

    metrics = {
        "threshold": threshold,
        "accuracy": accuracy_score(
            y_true,
            predictions,
        ),
        "precision": precision_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            predictions,
        ).tolist(),
        "classification_report": classification_report(
            y_true,
            predictions,
            zero_division=0,
        ),
    }

    if len(set(y_true)) == 2:
        metrics["roc_auc"] = roc_auc_score(
            y_true,
            probabilities,
        )
        metrics["pr_auc"] = average_precision_score(
            y_true,
            probabilities,
        )
    else:
        metrics["roc_auc"] = None
        metrics["pr_auc"] = None

    return metrics


def select_threshold_by_f1(model, validation_rows):
    """
    Select a probability threshold using validation F1-score.

    The test set must not be used for threshold selection.
    """

    best_threshold = 0.5
    best_f1 = -1.0

    dataframe = rows_to_dataframe(validation_rows)

    X_validation = dataframe[FEATURE_COLUMNS]
    y_validation = dataframe[TARGET_COLUMN]

    probabilities = model.predict_proba(
        X_validation
    )[:, 1]

    for threshold in [
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
    ]:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        current_f1 = f1_score(
            y_validation,
            predictions,
            zero_division=0,
        )

        if current_f1 > best_f1:
            best_f1 = current_f1
            best_threshold = threshold

    return {
        "threshold": best_threshold,
        "validation_f1": best_f1,
    }

def train_calibrated_baseline(train_rows, method="sigmoid", cv=5):
    """
    Train a probability-calibrated logistic regression baseline.

    Parameters
    ----------
    train_rows:
        Training rows containing telemetry features and targets.

    method:
        Calibration method. "sigmoid" is preferred for the current
        relatively small dataset.

    cv:
        Number of cross-validation folds used for calibration.

    Returns
    -------
    CalibratedClassifierCV
        A fitted calibrated model.
    """
    dataframe = rows_to_dataframe(train_rows)

    X_train = dataframe.drop(
        columns=[TARGET_COLUMN]
    )
    y_train = dataframe[TARGET_COLUMN]

    base_model = build_logistic_regression_pipeline()

    calibrated_model = CalibratedClassifierCV(
        estimator=base_model,
        method=method,
        cv=cv,
    )

    calibrated_model.fit(X_train, y_train)

    return calibrated_model