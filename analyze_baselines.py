"""
Decision-safety analysis for TWINSHIELD baseline comparison.

Compares:
- naive rerouting
- prediction-only selection
- TWINSHIELD

Focuses on whether accepted actions actually improve
the target flow.
"""

import csv
from pathlib import Path


INPUT_PATH = Path(
    "results/twinshield_baseline_comparison.csv"
)


def load_rows():
    with open(
        INPUT_PATH,
        mode="r",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        return list(csv.DictReader(csv_file))


def analyze_strategy(rows, strategy):
    strategy_rows = [
        row
        for row in rows
        if row["strategy"] == strategy
    ]

    accepted = [
        row
        for row in strategy_rows
        if row["decision"] == "accept"
    ]

    abstained = [
        row
        for row in strategy_rows
        if row["decision"] == "abstain"
    ]

    rejected = [
        row
        for row in strategy_rows
        if row["decision"] == "reject"
    ]

    improvements = [
        row
        for row in accepted
        if float(row["actual_risk_reduction"]) > 0
    ]

    harmful = [
        row
        for row in accepted
        if float(row["actual_risk_reduction"]) < 0
    ]

    neutral = [
        row
        for row in accepted
        if float(row["actual_risk_reduction"]) == 0
    ]

    print(f"\nStrategy: {strategy}")
    print("-" * 50)

    print(
        f"Total cases:              "
        f"{len(strategy_rows)}"
    )

    print(
        f"Accepted actions:         "
        f"{len(accepted)}"
    )

    print(
        f"Abstained actions:        "
        f"{len(abstained)}"
    )

    print(
        f"Rejected actions:         "
        f"{len(rejected)}"
    )

    print(
        f"Actually beneficial:      "
        f"{len(improvements)}"
    )

    print(
        f"Harmful accepted:         "
        f"{len(harmful)}"
    )

    print(
        f"Neutral accepted:         "
        f"{len(neutral)}"
    )

    if accepted:

        success_rate = (
            len(improvements)
            / len(accepted)
        ) * 100

        unsafe_rate = (
            len(harmful)
            / len(accepted)
        ) * 100

        print(
            f"Accepted-action success:  "
            f"{success_rate:.1f}%"
        )

        print(
            f"Unsafe accepted rate:     "
            f"{unsafe_rate:.1f}%"
        )

    if strategy == "twinshield":

        abstention_rate = (
            len(abstained)
            / len(strategy_rows)
        ) * 100

        print(
            f"Abstention rate:          "
            f"{abstention_rate:.1f}%"
        )


def print_case_comparison(rows):
    """
    Print cases where prediction-only accepted
    but TWINSHIELD did not accept.
    """

    print("\n" + "=" * 70)
    print("CASES WHERE TWINSHIELD PREVENTED EXECUTION")
    print("=" * 70)

    prediction_rows = {
        (
            row["scenario_id"],
            row["flow_id"],
        ): row
        for row in rows
        if row["strategy"] == "prediction_only"
    }

    twinshield_rows = {
        (
            row["scenario_id"],
            row["flow_id"],
        ): row
        for row in rows
        if row["strategy"] == "twinshield"
    }

    for key, prediction_row in prediction_rows.items():

        twinshield_row = twinshield_rows.get(key)

        if twinshield_row is None:
            continue

        if (
            prediction_row["decision"] == "accept"
            and twinshield_row["decision"] != "accept"
        ):

            print(
                f"\nScenario: {key[0]}"
            )

            print(
                f"Flow:     {key[1]}"
            )

            print(
                f"Prediction-only: "
                f"{prediction_row['decision']}"
            )

            print(
                f"TWINSHIELD:      "
                f"{twinshield_row['decision']}"
            )

            print(
                f"Actual risk reduction: "
                f"{prediction_row['actual_risk_reduction']}"
            )

            print(
                f"TWINSHIELD reason: "
                f"{twinshield_row['reason']}"
            )


def main():

    print(
        "Loading baseline comparison results..."
    )

    rows = load_rows()

    print(
        f"Loaded {len(rows)} rows."
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "TWINSHIELD DECISION-SAFETY COMPARISON"
    )

    print(
        "=" * 70
    )

    for strategy in [
        "naive",
        "prediction_only",
        "twinshield",
    ]:

        analyze_strategy(
            rows,
            strategy,
        )

    print_case_comparison(
        rows
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "BASELINE ANALYSIS COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()