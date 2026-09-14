"""
Target construction utilities for TWINSHIELD datasets.

This module creates next-step prediction targets while preserving
episode and flow boundaries.
"""

from collections import defaultdict


def add_next_step_sla_target(rows):
    """
    Add a next-step SLA violation target to telemetry rows.

    Parameters
    ----------
    rows : list of dict
        Telemetry rows containing episode_id, timestamp, flow_id,
        and sla_violation.

    Returns
    -------
    list of dict
        Rows containing the additional
        target_sla_violation_next_step field.

    Notes
    -----
    The final timestamp of each episode-flow sequence is excluded
    because no next-step label is available.
    """

    grouped_rows = defaultdict(list)

    for row in rows:
        key = (
            row["episode_id"],
            row["flow_id"],
        )
        grouped_rows[key].append(row)

    target_rows = []

    for group in grouped_rows.values():
        group.sort(key=lambda row: int(row["timestamp"]))

        for index in range(len(group) - 1):
            current_row = dict(group[index])
            next_row = group[index + 1]

            current_row["target_sla_violation_next_step"] = (
                next_row["sla_violation"] == "True"
                if isinstance(next_row["sla_violation"], str)
                else bool(next_row["sla_violation"])
            )

            target_rows.append(current_row)

    return target_rows