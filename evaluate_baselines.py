"""
Baseline comparison for TWINSHIELD.

This experiment compares:

1. Naive rerouting:
   Selects the first valid alternate route.

2. Prediction-only:
   Uses the trained predictor to select an action with
   the lowest predicted post-action SLA risk.

3. TWINSHIELD:
   Uses prediction + uncertainty + protected-flow
   safety constraints + abstention.

All selected actions are evaluated against the
actual counterfactual simulation outcome.
"""

import csv
from pathlib import Path

from actions.candidate_generator import generate_candidate_actions
from decision.pipeline import DecisionPipeline
from models.predictor import load_model
from simulation.engine import advance_simulation
from simulation.network_state import create_initial_network_state
from simulation.scenarios import SUPPORTED_SCENARIOS, apply_scenario
from twin_evaluator.counterfactual import build_counterfactual_state


MODEL_PATH = Path(
    "models/artifacts/"
    "twinshield_calibrated_baseline.joblib"
)

OUTPUT_PATH = Path(
    "results/twinshield_baseline_comparison.csv"
)


def get_actual_outcome(network_state, action):
    """
    Evaluate the real counterfactual outcome of an action.
    """

    counterfactual_state = build_counterfactual_state(
        network_state,
        action,
    )

    counterfactual_state = advance_simulation(
        counterfactual_state
    )

    for flow in counterfactual_state["flows"]:
        if flow["flow_id"] == action.target_flow:
            return flow

    return None


def get_candidates(network_state, flow):
    """
    Generate valid rerouting candidates for one flow.
    """

    return generate_candidate_actions(
        topology=network_state["topology"],
        target_flow_id=flow["flow_id"],
        old_path=flow["route"],
        max_candidates=5,
    )


def get_prediction(pipeline, action):
    """
    Get TWINSHIELD's predicted outcome for an action.
    """

    result = pipeline.evaluate(action)

    predicted_outcomes = (
        result
        .get("evaluation", {})
        .get("predicted_outcomes", {})
    )

    target_outcome = predicted_outcomes.get(
        action.target_flow,
        {}
    )

    return {
        "pipeline_result": result,
        "predicted_risk": target_outcome.get(
            "sla_violation_risk"
        ),
        "uncertainty": target_outcome.get(
            "uncertainty_score"
        ),
    }


def evaluate_scenario(scenario_id, model):
    """
    Evaluate all baseline strategies in one scenario.
    """

    network_state = create_initial_network_state(
        episode_id=f"baseline_{scenario_id}",
        scenario_id=scenario_id,
    )

    network_state = apply_scenario(
        network_state,
        scenario_id,
    )

    network_state = advance_simulation(
        network_state
    )

    pipeline = DecisionPipeline(
        network_state=network_state,
        model=model,
    )

    rows = []

    for flow in network_state["flows"]:

        candidates = get_candidates(
            network_state,
            flow,
        )

        if not candidates:
            continue

        risk_before = flow.get(
            "sla_violation_risk",
            0.0,
        )

        # --------------------------------------------------
        # BASELINE 1: NAIVE REROUTING
        # --------------------------------------------------

        naive_action = candidates[0]

        naive_actual = get_actual_outcome(
            network_state,
            naive_action,
        )

        if naive_actual is not None:

            actual_risk_after = naive_actual[
                "sla_violation_risk"
            ]

            rows.append(
                {
                    "scenario_id": scenario_id,
                    "flow_id": flow["flow_id"],
                    "strategy": "naive",
                    "action_id": naive_action.action_id,
                    "old_path": str(
                        naive_action.old_path
                    ),
                    "new_path": str(
                        naive_action.new_path
                    ),
                    "risk_before": risk_before,
                    "predicted_risk_after": "",
                    "uncertainty": "",
                    "actual_risk_after": actual_risk_after,
                    "actual_risk_reduction": (
                        risk_before
                        - actual_risk_after
                    ),
                    "decision": "accept",
                    "reason": (
                        "First valid alternate "
                        "route selected"
                    ),
                }
            )

        # --------------------------------------------------
        # BASELINE 2: PREDICTION-ONLY
        # --------------------------------------------------

        prediction_candidates = []

        for action in candidates:

            prediction = get_prediction(
                pipeline,
                action,
            )

            predicted_risk = prediction[
                "predicted_risk"
            ]

            if predicted_risk is None:
                continue

            prediction_candidates.append(
                (
                    predicted_risk,
                    action,
                    prediction,
                )
            )

        if prediction_candidates:

            prediction_candidates.sort(
                key=lambda item: item[0]
            )

            (
                predicted_risk,
                prediction_action,
                prediction_data,
            ) = prediction_candidates[0]

            actual = get_actual_outcome(
                network_state,
                prediction_action,
            )

            if actual is not None:

                actual_risk_after = actual[
                    "sla_violation_risk"
                ]

                rows.append(
                    {
                        "scenario_id": scenario_id,
                        "flow_id": flow["flow_id"],
                        "strategy": "prediction_only",
                        "action_id": (
                            prediction_action.action_id
                        ),
                        "old_path": str(
                            prediction_action.old_path
                        ),
                        "new_path": str(
                            prediction_action.new_path
                        ),
                        "risk_before": risk_before,
                        "predicted_risk_after": (
                            predicted_risk
                        ),
                        "uncertainty": (
                            prediction_data[
                                "uncertainty"
                            ]
                        ),
                        "actual_risk_after": (
                            actual_risk_after
                        ),
                        "actual_risk_reduction": (
                            risk_before
                            - actual_risk_after
                        ),
                        "decision": "accept",
                        "reason": (
                            "Action with lowest "
                            "predicted risk selected"
                        ),
                    }
                )

        # --------------------------------------------------
        # TWINSHIELD
        # --------------------------------------------------

        twinshield_candidates = []

        for action in candidates:

            prediction = get_prediction(
                pipeline,
                action,
            )

            result = prediction[
                "pipeline_result"
            ]

            actual = get_actual_outcome(
                network_state,
                action,
            )

            if actual is None:
                continue

            actual_risk_after = actual[
                "sla_violation_risk"
            ]

            twinshield_candidates.append(
                (
                    result.get("status"),
                    action,
                    prediction,
                    actual_risk_after,
                )
            )

        # Prefer accepted actions.
        accepted = [
            item
            for item in twinshield_candidates
            if item[0] == "accept"
        ]

        if accepted:

            accepted.sort(
                key=lambda item: item[2][
                    "predicted_risk"
                ]
                if item[2]["predicted_risk"]
                is not None
                else float("inf")
            )

            (
                decision,
                selected_action,
                prediction,
                actual_risk_after,
            ) = accepted[0]

        else:

            abstained = [
                item
                for item in twinshield_candidates
                if item[0] == "abstain"
            ]

            if abstained:

                (
                    decision,
                    selected_action,
                    prediction,
                    actual_risk_after,
                ) = abstained[0]

            else:

                rejected = [
                    item
                    for item in twinshield_candidates
                    if item[0] == "reject"
                ]

                if not rejected:
                    continue

                (
                    decision,
                    selected_action,
                    prediction,
                    actual_risk_after,
                ) = rejected[0]

        rows.append(
            {
                "scenario_id": scenario_id,
                "flow_id": flow["flow_id"],
                "strategy": "twinshield",
                "action_id": (
                    selected_action.action_id
                ),
                "old_path": str(
                    selected_action.old_path
                ),
                "new_path": str(
                    selected_action.new_path
                ),
                "risk_before": risk_before,
                "predicted_risk_after": (
                    prediction["predicted_risk"]
                ),
                "uncertainty": (
                    prediction["uncertainty"]
                ),
                "actual_risk_after": (
                    actual_risk_after
                ),
                "actual_risk_reduction": (
                    risk_before
                    - actual_risk_after
                ),
                "decision": decision,
                "reason": prediction[
                    "pipeline_result"
                ].get("reason"),
            }
        )

    return rows


def save_results(rows):
    """
    Save comparison results to CSV.
    """

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "scenario_id",
        "flow_id",
        "strategy",
        "action_id",
        "old_path",
        "new_path",
        "risk_before",
        "predicted_risk_after",
        "uncertainty",
        "actual_risk_after",
        "actual_risk_reduction",
        "decision",
        "reason",
    ]

    with open(
        OUTPUT_PATH,
        mode="w",
        encoding="utf-8",
        newline="",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def print_summary(rows):
    """
    Print strategy-level comparison.
    """

    print("\n" + "=" * 70)
    print("TWINSHIELD BASELINE COMPARISON")
    print("=" * 70)

    strategies = sorted(
        set(
            row["strategy"]
            for row in rows
        )
    )

    for strategy in strategies:

        strategy_rows = [
            row
            for row in rows
            if row["strategy"] == strategy
        ]

        improvements = [
            float(
                row["actual_risk_reduction"]
            )
            for row in strategy_rows
            if row["actual_risk_reduction"]
            != ""
            and float(
                row["actual_risk_reduction"]
            ) > 0
        ]

        degradations = [
            float(
                row["actual_risk_reduction"]
            )
            for row in strategy_rows
            if row["actual_risk_reduction"]
            != ""
            and float(
                row["actual_risk_reduction"]
            ) < 0
        ]

        average_reduction = 0.0

        if strategy_rows:
            average_reduction = (
                sum(
                    float(
                        row[
                            "actual_risk_reduction"
                        ]
                    )
                    for row in strategy_rows
                )
                / len(strategy_rows)
            )

        print(
            f"\nStrategy: {strategy}"
        )
        print("-" * 40)

        print(
            f"Evaluations: "
            f"{len(strategy_rows)}"
        )

        print(
            f"Average actual risk reduction: "
            f"{average_reduction:.4f}"
        )

        print(
            f"Actual improvements: "
            f"{len(improvements)}"
        )

        print(
            f"Actual degradations: "
            f"{len(degradations)}"
        )

        if strategy == "twinshield":

            decisions = {}

            for row in strategy_rows:

                decision = row["decision"]

                decisions[decision] = (
                    decisions.get(
                        decision,
                        0,
                    )
                    + 1
                )

            print(
                "Decisions:"
            )

            for decision, count in sorted(
                decisions.items()
            ):

                print(
                    f"  {decision}: "
                    f"{count}"
                )

    print("\nResults saved to:")
    print(OUTPUT_PATH)

    print("\n" + "=" * 70)
    print("BASELINE COMPARISON COMPLETE")
    print("=" * 70)


def main():

    print(
        "Loading trained TWINSHIELD model..."
    )

    model = load_model(
        MODEL_PATH
    )

    print(
        "Model loaded successfully."
    )

    all_rows = []

    for scenario_id in sorted(
        SUPPORTED_SCENARIOS
    ):

        print(
            f"\nEvaluating scenario: "
            f"{scenario_id}"
        )

        scenario_rows = evaluate_scenario(
            scenario_id,
            model,
        )

        all_rows.extend(
            scenario_rows
        )

    save_results(
        all_rows
    )

    print_summary(
        all_rows
    )


if __name__ == "__main__":
    main()