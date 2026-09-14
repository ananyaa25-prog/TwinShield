"""
Tests for the TWINSHIELD action evaluator.
"""

from actions.action_schema import ReroutingAction
from twin_evaluator.action_evaluator import ActionEvaluator


def create_minimal_network_state():
    """
    Create a minimal prototype state for fallback evaluation.
    """
    return {
        "flows": [
            {
                "flow_id": "F3",
                "delay": 0.050,
                "packet_loss": 0.020,
                "sla_violation_risk": 0.70,
            },
            {
                "flow_id": "F7",
                "delay": 0.030,
                "packet_loss": 0.010,
                "sla_violation_risk": 0.10,
            },
        ]
    }


def create_test_action():
    """
    Create a sample rerouting action.
    """
    return ReroutingAction(
        action_id="reroute_F3_path_1",
        target_flow="F3",
        old_path=["R1", "R2", "R4"],
        new_path=["R1", "R3", "R4"],
    )


def test_action_evaluator_success():
    network_state = create_minimal_network_state()
    action = create_test_action()

    evaluator = ActionEvaluator(network_state)
    result = evaluator.evaluate(action)

    assert result["success"] is True
    assert result["action_id"] == "reroute_F3_path_1"
    assert result["target_flow"] == "F3"


def test_action_evaluator_target_delay_improves():
    network_state = create_minimal_network_state()
    action = create_test_action()

    evaluator = ActionEvaluator(network_state)
    result = evaluator.evaluate(action)

    predicted_delay = result["predicted_outcomes"]["F3"]["delay"]

    assert predicted_delay < 0.050


def test_action_evaluator_target_packet_loss_improves():
    network_state = create_minimal_network_state()
    action = create_test_action()

    evaluator = ActionEvaluator(network_state)
    result = evaluator.evaluate(action)

    predicted_loss = result["predicted_outcomes"]["F3"]["packet_loss"]

    assert predicted_loss < 0.020


def test_action_evaluator_preserves_legacy_risk_key():
    network_state = create_minimal_network_state()
    action = create_test_action()

    evaluator = ActionEvaluator(network_state)
    result = evaluator.evaluate(action)

    outcome = result["predicted_outcomes"]["F3"]

    assert "sla_violation_risk" in outcome
    assert outcome["sla_violation_risk"] == 0.70


def test_action_evaluator_reports_fallback_mode():
    network_state = create_minimal_network_state()
    action = create_test_action()

    evaluator = ActionEvaluator(network_state)
    result = evaluator.evaluate(action)

    assert result["evaluation_type"] == "deterministic_fallback"


def test_action_evaluator_missing_target_flow():
    network_state = create_minimal_network_state()

    action = ReroutingAction(
        action_id="reroute_unknown",
        target_flow="UNKNOWN",
        old_path=["R1", "R2"],
        new_path=["R1", "R3"],
    )

    evaluator = ActionEvaluator(network_state)
    result = evaluator.evaluate(action)

    assert result["success"] is False
    assert result["reason"] == "Target flow not found"