"""
Counterfactual network-state evaluation helpers for TWINSHIELD.

This module creates a hypothetical network state after applying
a candidate rerouting action and recalculates its telemetry using
the deterministic simulation engine.
"""

from copy import deepcopy

from simulation.engine import advance_simulation


def build_counterfactual_state(network_state, action):
    """
    Build a counterfactual network state for a rerouting action.

    The original network state is not modified.

    Parameters
    ----------
    network_state : dict
        Current network state containing links and flows.

    action : ReroutingAction
        Candidate rerouting action containing target_flow and new_path.

    Returns
    -------
    dict
        Recalculated counterfactual network state.

    Raises
    ------
    ValueError
        If the target flow does not exist or the new route is invalid.
    """
    counterfactual_state = deepcopy(network_state)

    target_flow = None

    for flow in counterfactual_state.get("flows", []):
        if flow["flow_id"] == action.target_flow:
            target_flow = flow
            break

    if target_flow is None:
        raise ValueError(
            f"Target flow not found: {action.target_flow}"
        )

    new_path = action.new_path

    if not isinstance(new_path, list) or len(new_path) < 2:
        raise ValueError(
            "new_path must be a list containing at least two nodes."
        )

    if new_path[0] != target_flow["source"]:
        raise ValueError(
            "new_path must begin at the target flow's source node."
        )

    if new_path[-1] != target_flow["destination"]:
        raise ValueError(
            "new_path must end at the target flow's destination node."
        )

    target_flow["route"] = new_path

    return advance_simulation(counterfactual_state)