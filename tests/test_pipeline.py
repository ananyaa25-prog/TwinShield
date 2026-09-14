from actions.action_schema import ReroutingAction
from decision.pipeline import DecisionPipeline
from simulation.network_state import create_initial_network_state


def create_test_action():
    return ReroutingAction(
        action_id="action_001",
        target_flow="f1",
        old_path=["n1", "n2", "n4"],
        new_path=["n1", "n3", "n4"]
    )


def test_pipeline_rejects_invalid_action():
    network_state = create_initial_network_state()

    invalid_action = ReroutingAction(
        action_id="action_invalid",
        target_flow="f1",
        old_path=["n1", "n2", "n4"],
        new_path=["n1", "n9", "n4"]
    )

    pipeline = DecisionPipeline(network_state)
    result = pipeline.evaluate(invalid_action)

    assert result["status"] == "reject"
    assert result["stage"] == "validation"


def test_pipeline_evaluates_valid_action():
    network_state = create_initial_network_state()
    action = create_test_action()

    pipeline = DecisionPipeline(network_state)
    result = pipeline.evaluate(action)

    assert result["action_id"] == "action_001"
    assert result["target_flow"] == "f1"
    assert "evaluation" in result
    assert "safety_decision" in result


def test_pipeline_returns_structured_predicted_outcomes():
    network_state = create_initial_network_state()
    action = create_test_action()

    pipeline = DecisionPipeline(network_state)
    result = pipeline.evaluate(action)

    evaluation = result["evaluation"]

    assert "predicted_outcomes" in evaluation
    assert "f1" in evaluation["predicted_outcomes"]
    assert "f2" in evaluation["predicted_outcomes"]
    assert "f3" in evaluation["predicted_outcomes"]


def test_pipeline_accepts_action_when_target_risk_improves():
    network_state = create_initial_network_state()

    # Give the target flow a nonzero baseline risk.
    for flow in network_state["flows"]:
        if flow["flow_id"] == "f1":
            flow["sla_violation_risk"] = 0.5

    action = create_test_action()

    pipeline = DecisionPipeline(network_state)

    # Replace the real evaluator with a controlled test evaluator.
    class MockEvaluator:
        def evaluate(self, action):
            return {
                "success": True,
                "action_id": action.action_id,
                "target_flow": action.target_flow,
                "old_path": action.old_path,
                "new_path": action.new_path,
                "evaluation_type": "mock_evaluation",
                "predicted_outcomes": {
                    "f1": {
                        "delay": 10.0,
                        "packet_loss": 0.0,
                        "sla_violation_risk": 0.0,
                        "risk_category": "low",
                        "uncertainty_score": 0.10,
                    },
                    "f2": {
                        "delay": 15.0,
                        "packet_loss": 0.0,
                        "sla_violation_risk": 0.0,
                        "risk_category": "low",
                        "uncertainty_score": 0.10,
                    },
                    "f3": {
                        "delay": 20.0,
                        "packet_loss": 0.0,
                        "sla_violation_risk": 0.0,
                        "risk_category": "low",
                        "uncertainty_score": 0.10,
                    },
                },
            }

    pipeline.evaluator = MockEvaluator()

    result = pipeline.evaluate(action)

    assert result["status"] == "accept"
    assert result["stage"] == "safety_selection"
    assert result["risk_before"] == 0.5
    assert result["risk_after"] == 0.0
