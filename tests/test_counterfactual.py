"""
Tests for TWINSHIELD counterfactual state generation.
"""

from copy import deepcopy

import pytest

from actions.action_schema import ReroutingAction
from simulation.network_state import create_initial_network_state
from simulation.scenarios import apply_scenario
from twin_evaluator.counterfactual import build_counterfactual_state


def create_test_state():
    """
    Create a simulated state suitable for counterfactual testing.
    """
    state = create_initial_network_state(
        scenario_id="normal",
    )

    return apply_scenario(
        network_state=state,
        scenario_id="normal",
    )


def find_flow(state, flow_id):
    """
    Find a flow by ID.
    """
    for flow in state["flows"]:
        if flow["flow_id"] == flow_id:
            return flow

    return None


def test_counterfactual_changes_target_route():
    state = create_test_state()

    action = ReroutingAction(
        action_id="test_reroute_f1",
        target_flow="f1",
        old_path=["n1", "n2", "n4"],
        new_path=["n1", "n3", "n4"],
    )

    counterfactual_state = build_counterfactual_state(
        network_state=state,
        action=action,
    )

    original_flow = find_flow(state, "f1")
    counterfactual_flow = find_flow(counterfactual_state, "f1")

    assert original_flow["route"] == ["n1", "n2", "n4"]
    assert counterfactual_flow["route"] == ["n1", "n3", "n4"]


def test_counterfactual_does_not_mutate_original_state():
    state = create_test_state()
    original_state = deepcopy(state)

    action = ReroutingAction(
        action_id="test_reroute_f1",
        target_flow="f1",
        old_path=["n1", "n2", "n4"],
        new_path=["n1", "n3", "n4"],
    )

    build_counterfactual_state(
        network_state=state,
        action=action,
    )

    assert state == original_state


def test_counterfactual_recalculates_timestamp():
    state = create_test_state()

    action = ReroutingAction(
        action_id="test_reroute_f1",
        target_flow="f1",
        old_path=["n1", "n2", "n4"],
        new_path=["n1", "n3", "n4"],
    )

    counterfactual_state = build_counterfactual_state(
        network_state=state,
        action=action,
    )

    assert counterfactual_state["timestamp"] == (
        state["timestamp"] + 1
    )


def test_counterfactual_rejects_missing_target_flow():
    state = create_test_state()

    action = ReroutingAction(
        action_id="test_missing_flow",
        target_flow="unknown_flow",
        old_path=["n1", "n2"],
        new_path=["n1", "n3"],
    )

    with pytest.raises(ValueError, match="Target flow not found"):
        build_counterfactual_state(
            network_state=state,
            action=action,
        )


def test_counterfactual_rejects_invalid_route():
    state = create_test_state()

    action = ReroutingAction(
        action_id="test_invalid_route",
        target_flow="f1",
        old_path=["n1", "n2", "n4"],
        new_path=["n2", "n4"],
    )

    with pytest.raises(
        ValueError,
        match="must begin at the target flow's source",
    ):
        build_counterfactual_state(
            network_state=state,
            action=action,
        )