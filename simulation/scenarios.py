"""
Scenario generation for the TWINSHIELD simulation.

The initial scenarios are deterministic and intended to create
reproducible network states for testing and dataset generation.
"""

from copy import deepcopy


SUPPORTED_SCENARIOS = {
    "normal",
    "shared_bottleneck",
    "background_surge",
}


def apply_scenario(network_state, scenario_id):
    """
    Apply a scenario to a network state.

    Parameters
    ----------
    network_state : dict
        Base network state.

    scenario_id : str
        Scenario to apply.

    Returns
    -------
    dict
        A new network state representing the selected scenario.

    Raises
    ------
    ValueError
        If the scenario is not currently supported.
    """

    if scenario_id not in SUPPORTED_SCENARIOS:
        raise ValueError(
            f"Unsupported scenario: {scenario_id}. "
            f"Supported scenarios: {sorted(SUPPORTED_SCENARIOS)}"
        )

    state = deepcopy(network_state)
    state["scenario_id"] = scenario_id

    if scenario_id == "normal":
        _apply_normal_scenario(state)

    elif scenario_id == "shared_bottleneck":
        _apply_shared_bottleneck_scenario(state)

    elif scenario_id == "background_surge":
        _apply_background_surge_scenario(state)

    return state


def _apply_normal_scenario(state):
    """
    Configure a normal operating state.

    All flows remain within their initial SLA limits and
    links have low utilization.
    """

    for link in state["links"]:
        link["utilization"] = 0.20
        link["queue_occupancy"] = 0.10
        link["queue_delay_ms"] = 1.0

    for flow in state["flows"]:
        flow["throughput_mbps"] = flow["rate_mbps"]
        flow["delay"] = 15.0
        flow["packet_loss"] = 0.0
        flow["sla_violation"] = False
        flow["sla_violation_risk"] = 0.0

def _apply_shared_bottleneck_scenario(state):
    """
    Configure a scenario where the target flow experiences
    congestion on the n2 -> n4 bottleneck link.

    The scenario adds background traffic to the bottleneck
    rather than directly forcing final telemetry values.
    """


    background_load = state["config"][
        "shared_bottleneck_background_load_mbps"
    ]

    for link in state["links"]:
        if (
            link["source"] == "n2"
            and link["destination"] == "n4"
        ):
            link["background_load_mbps"] = background_load

    for flow in state["flows"]:
        flow["sla_violation"] = False

def _apply_background_surge_scenario(state):
    """
    Configure a scenario where background traffic increases
    and causes congestion on the n2 -> n5 link.

    The scenario sets an underlying background load.
    Link and flow telemetry are calculated by the simulation engine.
    """

    background_load = (
        state["config"]["background_surge_load_mbps"]
        * state["config"]["background_surge_multiplier"]
    )

    for link in state["links"]:
        if (
            link["source"] == "n2"
            and link["destination"] == "n5"
        ):
            link["background_load_mbps"] = background_load

    for flow in state["flows"]:
        flow["sla_violation"] = False