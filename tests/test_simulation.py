from simulation.topology import create_initial_topology
from simulation.network_state import create_initial_network_state
from simulation.scenarios import apply_scenario

def test_initial_topology():
    topology = create_initial_topology()

    assert "nodes" in topology
    assert "links" in topology

    assert len(topology["nodes"]) == 6
    assert len(topology["links"]) == 7

    for link in topology["links"]:
        assert "link_id" in link
        assert "source" in link
        assert "destination" in link
        assert "capacity_mbps" in link
        assert "delay_ms" in link
        assert "queue_size" in link


def test_initial_network_state():
    state = create_initial_network_state()

    assert "timestamp" in state
    assert "episode_id" in state
    assert "scenario_id" in state
    assert "topology" in state
    assert "links" in state
    assert "flows" in state

    assert len(state["flows"]) == 3

    for flow in state["flows"]:
        assert "flow_id" in flow
        assert "source" in flow
        assert "destination" in flow
        assert "route" in flow
        assert "rate_mbps" in flow
        assert "throughput_mbps" in flow
        assert "delay" in flow
        assert "packet_loss" in flow
        assert "sla" in flow

def test_normal_scenario():
    base_state = create_initial_network_state()
    state = apply_scenario(base_state, "normal")

    assert state["scenario_id"] == "normal"

    target_flow = state["flows"][0]

    assert target_flow["delay"] == 15.0
    assert target_flow["packet_loss"] == 0.0
    assert target_flow["sla_violation"] is False
    assert target_flow["sla_violation_risk"] == 0.0


def test_shared_bottleneck_scenario():
    base_state = create_initial_network_state()

    state = apply_scenario(
        base_state,
        "shared_bottleneck",
    )

    assert state["scenario_id"] == "shared_bottleneck"

    bottleneck_link = next(
        link for link in state["links"]
        if link["link_id"] == "l2"
    )

    assert bottleneck_link["background_load_mbps"] == 5.0

    # The scenario modifies the copied state, not the base state.
    assert bottleneck_link["utilization"] == 0.0

    target_flow = state["flows"][0]

    # Telemetry is calculated later by the simulation engine.
    assert target_flow["delay"] == 15.0
    assert target_flow["packet_loss"] == 0.0
    assert target_flow["sla_violation"] is False

def test_scenario_does_not_modify_base_state():
    base_state = create_initial_network_state()

    original_delay = base_state["flows"][0]["delay"]
    original_utilization = base_state["links"][1]["utilization"]

    apply_scenario(base_state, "shared_bottleneck")

    assert base_state["flows"][0]["delay"] == original_delay
    assert base_state["links"][1]["utilization"] == original_utilization


def test_unsupported_scenario():
    base_state = create_initial_network_state()

    try:
        apply_scenario(base_state, "unknown_scenario")
        assert False, "Expected ValueError was not raised"
    except ValueError:
        assert True

def test_background_surge_scenario():
    base_state = create_initial_network_state()

    state = apply_scenario(
        base_state,
        "background_surge",
    )

    assert state["scenario_id"] == "background_surge"

    surge_link = [
        link
        for link in state["links"]
        if (
            link["source"] == "n2"
            and link["destination"] == "n5"
        )
    ][0]

    assert (
        surge_link["background_load_mbps"]
        == 40.0
    )

    # The scenario should configure underlying conditions.
    # Final utilization and flow telemetry are calculated
    # by the simulation engine.

def test_shared_bottleneck_creates_higher_congestion():
    from simulation.runner import run_simulation_episode

    normal_state = run_simulation_episode(
        scenario_id="normal",
        num_steps=1,
    )

    bottleneck_state = run_simulation_episode(
        scenario_id="shared_bottleneck",
        num_steps=1,
    )

    normal_l2 = next(
        link for link in normal_state["links"]
        if link["link_id"] == "l2"
    )

    bottleneck_l2 = next(
        link for link in bottleneck_state["links"]
        if link["link_id"] == "l2"
    )

    assert bottleneck_l2["utilization"] > normal_l2["utilization"]


def test_shared_bottleneck_affects_flow_quality():
    from simulation.runner import run_simulation_episode

    state = run_simulation_episode(
        scenario_id="shared_bottleneck",
        num_steps=1,
    )

    target_flow = next(
        flow for flow in state["flows"]
        if flow["flow_id"] == "f1"
    )

    assert target_flow["delay"] > 15.0
    assert target_flow["packet_loss"] > 0.0
    assert target_flow["sla_violation_risk"] > 0.0
    assert target_flow["sla_violation"] is True

def test_simulation_episode_advances_multiple_steps():
    from simulation.runner import run_simulation_episode

    state = run_simulation_episode(
        scenario_id="normal",
        num_steps=5,
        episode_id="episode_test_001",
    )

    assert state["episode_id"] == "episode_test_001"
    assert state["scenario_id"] == "normal"
    assert state["timestamp"] == 5

def test_multiple_episode_dataset_generation():
    from simulation.dataset import generate_dataset_rows

    rows = generate_dataset_rows(
        num_steps=2,
        episodes_per_scenario=2,
    )

    assert len(rows) == 54

    episode_ids = sorted(
        set(row["episode_id"] for row in rows)
    )

    scenario_ids = sorted(
        set(row["scenario_id"] for row in rows)
    )

    timestamps = sorted(
        set(row["timestamp"] for row in rows)
    )

    assert len(episode_ids) == 6
    assert scenario_ids == [
        "background_surge",
        "normal",
        "shared_bottleneck",
    ]
    assert timestamps == [0, 1, 2]