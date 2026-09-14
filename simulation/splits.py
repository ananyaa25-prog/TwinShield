"""
Dataset splitting utilities for TWINSHIELD.

Splits are performed at the episode level to prevent related
timestamps from the same episode appearing in different splits.
Scenario-wise splitting preserves scenario representation.
"""

from collections import defaultdict


def split_rows_by_episode(
    rows,
    train_fraction=0.7,
    validation_fraction=0.1,
    test_fraction=0.2,
):
    """
    Split telemetry rows into train, validation, and test sets.

    Splitting is performed separately within each scenario and
    at the complete-episode level.

    Parameters
    ----------
    rows : list of dict
        Target-enhanced telemetry rows.

    train_fraction : float
        Fraction of episodes assigned to training.

    validation_fraction : float
        Fraction of episodes assigned to validation.

    test_fraction : float
        Fraction of episodes assigned to testing.

    Returns
    -------
    tuple[list[dict], list[dict], list[dict]]
        Training, validation, and test rows.

    Raises
    ------
    ValueError
        If fractions are invalid or do not sum to one.
    """

    fractions = (
        train_fraction,
        validation_fraction,
        test_fraction,
    )

    if any(fraction < 0 for fraction in fractions):
        raise ValueError("Split fractions cannot be negative.")

    if abs(sum(fractions) - 1.0) > 1e-9:
        raise ValueError(
            "Split fractions must sum to 1.0."
        )

    grouped = defaultdict(lambda: defaultdict(list))

    for row in rows:
        scenario_id = row["scenario_id"]
        episode_id = row["episode_id"]
        grouped[scenario_id][episode_id].append(row)

    train_rows = []
    validation_rows = []
    test_rows = []

    for scenario_id in sorted(grouped):
        episodes = sorted(grouped[scenario_id])

        total_episodes = len(episodes)

        train_count = int(total_episodes * train_fraction)
        validation_count = int(
            total_episodes * validation_fraction
        )

        # Ensure the remaining episodes go to the test split.
        test_start = train_count + validation_count

        train_episodes = episodes[:train_count]
        validation_episodes = episodes[
            train_count:test_start
        ]
        test_episodes = episodes[test_start:]

        for episode_id in train_episodes:
            train_rows.extend(
                grouped[scenario_id][episode_id]
            )

        for episode_id in validation_episodes:
            validation_rows.extend(
                grouped[scenario_id][episode_id]
            )

        for episode_id in test_episodes:
            test_rows.extend(
                grouped[scenario_id][episode_id]
            )

    return train_rows, validation_rows, test_rows