import csv
from pathlib import Path
"""
Dataset utilities for TWINSHIELD.

This module converts simulated network states into tabular
flow-level telemetry records suitable for machine learning.
"""


def network_state_to_rows(network_state):
    """
    Convert one network state into flow-level dataset rows.

    Parameters
    ----------
    network_state : dict
        Network state containing links and flows.

    Returns
    -------
    list of dict
        One telemetry row per flow.
    """

    rows = []

    for flow in network_state["flows"]:
        route = flow["route"]

        route_links = []

        for source, destination in zip(route, route[1:]):
            for link in network_state["links"]:
                same_direction = (
                    link["source"] == source
                    and link["destination"] == destination
                )

                reverse_direction = (
                    link["source"] == destination
                    and link["destination"] == source
                )

                if same_direction or reverse_direction:
                    route_links.append(link)
                    break

        max_link_utilization = max(
            (link["utilization"] for link in route_links),
            default=0.0,
        )

        max_queue_delay_ms = max(
            (link["queue_delay_ms"] for link in route_links),
            default=0.0,
        )

        row = {
            "episode_id": network_state["episode_id"],
            "timestamp": network_state["timestamp"],
            "scenario_id": network_state["scenario_id"],
            "flow_id": flow["flow_id"],
            "source": flow["source"],
            "destination": flow["destination"],
            "rate_mbps": flow["rate_mbps"],
            "throughput_mbps": flow["throughput_mbps"],
            "delay_ms": flow["delay"],
            "packet_loss": flow["packet_loss"],
            "sla_violation_risk": flow["sla_violation_risk"],
            "sla_violation": flow["sla_violation"],
            "max_link_utilization": max_link_utilization,
            "max_queue_delay_ms": max_queue_delay_ms,
        }

        rows.append(row)

    return rows

def generate_episode_rows(
    scenario_id="normal",
    num_steps=5,
    config=None,
    episode_id="episode_001",
):
    """
    Generate flow-level telemetry rows across one simulation episode.

    The initial state at timestamp 0 is included, followed by each
    subsequent simulation step.

    Parameters
    ----------
    scenario_id : str
        Scenario to simulate.

    num_steps : int
        Number of simulation steps after the initial state.

    config : dict or None
        Optional simulation configuration.

    episode_id : str
        Identifier for the simulation episode.

    Returns
    -------
    list of dict
        Flow-level telemetry rows across all time steps.
    """

    from simulation.network_state import create_initial_network_state
    from simulation.scenarios import apply_scenario
    from simulation.engine import advance_simulation
    from simulation.config import create_simulation_config

    if num_steps < 0:
        raise ValueError("num_steps cannot be negative.")

    if config is None:
        config = create_simulation_config()

    state = create_initial_network_state(
        timestamp=0,
        episode_id=episode_id,
        scenario_id=scenario_id,
        config=config,
    )

    state = apply_scenario(
        network_state=state,
        scenario_id=scenario_id,
    )

    rows = []

    # Collect the initial state at timestamp 0.
    rows.extend(network_state_to_rows(state))

    # Advance and collect each subsequent state.
    for _ in range(num_steps):
        state = advance_simulation(state)
        rows.extend(network_state_to_rows(state))

    return rows

def generate_dataset_rows(
    scenarios=None,
    num_steps=5,
    config=None,
    episodes_per_scenario=1,
    config_variants=None,
):
    """
    Generate telemetry rows across scenarios and episodes.

    Parameters
    ----------
    scenarios : list[str] or None
        Scenarios to simulate.

    num_steps : int
        Number of simulation steps per episode.

    config : dict or None
        Default configuration used when config_variants is not supplied.

    episodes_per_scenario : int
        Number of episodes generated for each scenario.

    config_variants : list[dict] or None
        Optional list of configurations. Configurations are
        assigned cyclically across generated episodes.

    Returns
    -------
    list of dict
        Combined telemetry rows.
    """

    if scenarios is None:
        scenarios = [
            "normal",
            "shared_bottleneck",
            "background_surge",
        ]

    if episodes_per_scenario <= 0:
        raise ValueError(
            "episodes_per_scenario must be greater than zero."
        )

    if config_variants is not None and len(config_variants) == 0:
        raise ValueError(
            "config_variants cannot be empty."
        )

    all_rows = []
    episode_number = 1

    for scenario_id in scenarios:
        for _ in range(episodes_per_scenario):
            episode_id = f"episode_{episode_number:04d}"

            episode_config = config

            if config_variants is not None:
                episode_config = config_variants[
                    (episode_number - 1) % len(config_variants)
                ]

            episode_rows = generate_episode_rows(
                scenario_id=scenario_id,
                num_steps=num_steps,
                config=episode_config,
                episode_id=episode_id,
            )

            all_rows.extend(episode_rows)
            episode_number += 1

    return all_rows

def save_rows_to_csv(rows, output_path):
    """
    Save telemetry rows to a CSV file.

    Parameters
    ----------
    rows : list of dict
        Dataset rows to save.

    output_path : str or pathlib.Path
        Destination CSV file path.

    Returns
    -------
    pathlib.Path
        Path to the saved CSV file.
    """

    if not rows:
        raise ValueError("Cannot save an empty dataset.")

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = list(rows[0].keys())

    with output_path.open(
        mode="w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return output_path