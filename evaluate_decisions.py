"""
Decision-level analysis for TWINSHIELD.

This script analyzes the results produced by
evaluate_decisions.py.

It measures:

- acceptance rate
- rejection rate
- abstention rate
- actual risk reduction
- accepted-action success
- accepted-action failure
- abstention behavior
- scenario-wise decision behavior
"""

import csv
from pathlib import Path


INPUT_PATH = Path(
    "results/twinshield_decision_evaluation.csv"
)


def load_rows():
    """Load evaluation results from CSV."""

    with open(
        INPUT_PATH,
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        return list(
            csv.DictReader(csv_file)
        )


def to_float(value):
    """Convert a CSV value to float."""

    if value is None or value == "":
        return None

    return float(value)


def analyze_decisions(rows):
    """Calculate overall decision statistics."""

    total = len(rows)

    counts = {
        "accept": 0,
        "reject": 0,
        "abstain": 0,
        "no_candidate": 0,
    }

    for row in rows:

        decision = row["decision"]

        if decision in counts:
            counts[decision] += 1

    print("\n" + "=" * 70)
    print("TWINSHIELD DECISION METRICS")
    print("=" * 70)

    print(
        f"\nTotal evaluations: {total}"
    )

    print("\nDecision distribution")
    print("-" * 40)

    for decision, count in counts.items():

        if total > 0:
            percentage = (
                count / total
            ) * 100
        else:
            percentage = 0.0

        print(
            f"{decision:15s}: "
            f"{count:2d} "
            f"({percentage:.1f}%)"
        )


def analyze_risk_reduction(rows):
    """Analyze actual risk reduction."""

    reductions = []

    for row in rows:

        value = to_float(
            row.get(
                "actual_risk_reduction"
            )
        )

        if value is not None:
            reductions.append(
                value
            )

    print("\nActual risk reduction")
    print("-" * 40)

    if not reductions:
        print(
            "No risk-reduction data available."
        )
        return

    average_reduction = (
        sum(reductions)
        / len(reductions)
    )

    positive = [
        value
        for value in reductions
        if value > 0
    ]

    negative = [
        value
        for value in reductions
        if value < 0
    ]

    print(
        f"Average risk reduction: "
        f"{average_reduction:.4f}"
    )

    print(
        f"Actions with actual improvement: "
        f"{len(positive)}"
    )

    print(
        f"Actions with actual degradation: "
        f"{len(negative)}"
    )


def analyze_accepted_actions(rows):
    """
    Determine whether accepted actions
    actually improved the target flow.
    """

    accepted = [
        row
        for row in rows
        if row["decision"] == "accept"
    ]

    successful = []
    unsuccessful = []

    for row in accepted:

        reduction = to_float(
            row.get(
                "actual_risk_reduction"
            )
        )

        if reduction is None:
            continue

        if reduction > 0:
            successful.append(row)
        else:
            unsuccessful.append(row)

    print("\nAccepted-action validation")
    print("-" * 40)

    print(
        f"Accepted actions: "
        f"{len(accepted)}"
    )

    print(
        f"Actually improved: "
        f"{len(successful)}"
    )

    print(
        f"Did not improve: "
        f"{len(unsuccessful)}"
    )

    if accepted:

        success_rate = (
            len(successful)
            / len(accepted)
        ) * 100

        print(
            f"Accepted-action success rate: "
            f"{success_rate:.1f}%"
        )


def analyze_abstentions(rows):
    """
    Analyze whether abstentions correspond
    to uncertain predictions.
    """

    abstained = [
        row
        for row in rows
        if row["decision"] == "abstain"
    ]

    print("\nAbstention analysis")
    print("-" * 40)

    print(
        f"Abstained actions: "
        f"{len(abstained)}"
    )

    uncertainties = []

    for row in abstained:

        uncertainty = to_float(
            row.get(
                "uncertainty"
            )
        )

        if uncertainty is not None:
            uncertainties.append(
                uncertainty
            )

    if uncertainties:

        average_uncertainty = (
            sum(uncertainties)
            / len(uncertainties)
        )

        print(
            f"Average uncertainty of "
            f"abstained actions: "
            f"{average_uncertainty:.4f}"
        )


def analyze_scenarios(rows):
    """Analyze decisions separately for each scenario."""

    scenarios = sorted(
        set(
            row["scenario_id"]
            for row in rows
        )
    )

    print("\nScenario-wise decision behavior")
    print("-" * 40)

    for scenario in scenarios:

        scenario_rows = [
            row
            for row in rows
            if row["scenario_id"]
            == scenario
        ]

        counts = {
            "accept": 0,
            "reject": 0,
            "abstain": 0,
        }

        for row in scenario_rows:

            decision = row["decision"]

            if decision in counts:
                counts[decision] += 1

        total = len(
            scenario_rows
        )

        print(
            f"\n{scenario}"
        )

        print(
            f"  Total:   {total}"
        )

        print(
            f"  Accept:  {counts['accept']}"
        )

        print(
            f"  Reject:  {counts['reject']}"
        )

        print(
            f"  Abstain: {counts['abstain']}"
        )


def analyze_prediction_error(rows):
    """
    Compare predicted counterfactual risk
    with actual counterfactual risk.
    """

    errors = []

    for row in rows:

        predicted = to_float(
            row.get(
                "predicted_risk_after"
            )
        )

        actual = to_float(
            row.get(
                "actual_risk_after"
            )
        )

        if (
            predicted is None
            or actual is None
        ):
            continue

        errors.append(
            abs(
                actual - predicted
            )
        )

    print("\nPrediction error")
    print("-" * 40)

    if not errors:
        print(
            "No prediction-error data available."
        )
        return

    mae = (
        sum(errors)
        / len(errors)
    )

    print(
        f"Mean absolute error: "
        f"{mae:.4f}"
    )


def main():

    print(
        "Loading TWINSHIELD decision results..."
    )

    rows = load_rows()

    print(
        f"Loaded {len(rows)} evaluation rows."
    )

    analyze_decisions(rows)

    analyze_risk_reduction(rows)

    analyze_accepted_actions(rows)

    analyze_abstentions(rows)

    analyze_scenarios(rows)

    analyze_prediction_error(rows)

    print("\n" + "=" * 70)
    print("DECISION ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()