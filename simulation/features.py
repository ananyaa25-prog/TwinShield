"""
Feature preparation utilities for TWINSHIELD prediction models.

This module converts CSV-style telemetry rows into model-ready
features while keeping the next-step target separate.
"""


NUMERIC_FEATURES = [
    "timestamp",
    "rate_mbps",
    "throughput_mbps",
    "delay_ms",
    "packet_loss",
    "max_link_utilization",
    "max_queue_delay_ms",
]


CATEGORICAL_FEATURES = [
    "flow_id",
]


TARGET_COLUMN = "target_sla_violation_next_step"


def prepare_feature_rows(rows):
    """
    Prepare telemetry rows for baseline model training.

    Parameters
    ----------
    rows : list of dict
        Rows from the target-enhanced telemetry dataset.

    Returns
    -------
    tuple[list[dict], list[bool]]
        A tuple containing:
        - feature dictionaries
        - Boolean next-step SLA violation targets

    Notes
    -----
    Current SLA violation and current SLA risk are intentionally
    excluded from the initial baseline feature set to reduce
    leakage and avoid making the task trivially dependent on
    current violation persistence.
    """

    feature_rows = []
    targets = []

    for row in rows:
        features = {}

        for column in NUMERIC_FEATURES:
            features[column] = float(row[column])

        for column in CATEGORICAL_FEATURES:
            features[column] = row[column]

        target_value = row[TARGET_COLUMN]

        if isinstance(target_value, str):
            target_value = target_value == "True"

        targets.append(bool(target_value))
        feature_rows.append(features)

    return feature_rows, targets