"""
Shared network-state representation for TWINSHIELD.

This module creates the initial network state using configurable
flow parameters.
"""

from simulation.topology import create_initial_topology
from simulation.config import create_simulation_config


def create_initial_network_state(
    timestamp=0,
    episode_id="episode_001",
    scenario_id="normal",
    config=None,
):
    """
    Create the initial network state.

    Parameters
    ----------
    timestamp : int
        Current simulation time step.

    episode_id : str
        Identifier for the simulation episode.

    scenario_id : str
        Identifier for the current scenario.

    config : dict or None
        Simulation configuration. If None, the default configuration
        is used.

    Returns
    -------
    dict
        Network state containing topology, links, and flows.
    """

    if config is None:
        config = create_simulation_config()

    topology = create_initial_topology()

    links = []

    for link in topology["links"]:
        links.append(
            {
                "link_id": link["link_id"],
                "source": link["source"],
                "destination": link["destination"],
                "capacity_mbps": link["capacity_mbps"],
                "delay_ms": link["delay_ms"],
                "queue_size": link["queue_size"],
                "background_load_mbps": 0.0,
                "utilization": 0.0,
                "queue_occupancy": 0.0,
                "queue_delay_ms": 0.0,
            }
        )

    flow_rates = config["flow_rates_mbps"]

    flows = [
        {
            "flow_id": "f1",
            "source": "n1",
            "destination": "n4",
            "route": ["n1", "n2", "n4"],
            "rate_mbps": flow_rates["f1"],
            "priority": 1,
            "throughput_mbps": flow_rates["f1"],
            "delay": 15.0,
            "packet_loss": 0.0,
            "sla": {
                "max_delay_ms": 50.0,
                "max_packet_loss": 0.05,
            },
            "sla_violation": False,
            "sla_violation_risk": 0.0,
        },
        {
            "flow_id": "f2",
            "source": "n1",
            "destination": "n4",
            "route": ["n1", "n3", "n4"],
            "rate_mbps": flow_rates["f2"],
            "priority": 2,
            "throughput_mbps": flow_rates["f2"],
            "delay": 15.0,
            "packet_loss": 0.0,
            "sla": {
                "max_delay_ms": 60.0,
                "max_packet_loss": 0.05,
            },
            "sla_violation": False,
            "sla_violation_risk": 0.0,
        },
        {
            "flow_id": "f3",
            "source": "n2",
            "destination": "n6",
            "route": ["n2", "n5", "n6"],
            "rate_mbps": flow_rates["f3"],
            "priority": 3,
            "throughput_mbps": flow_rates["f3"],
            "delay": 25.0,
            "packet_loss": 0.0,
            "sla": {
                "max_delay_ms": 80.0,
                "max_packet_loss": 0.05,
            },
            "sla_violation": False,
            "sla_violation_risk": 0.0,
        },
    ]

    return {
        "timestamp": timestamp,
        "episode_id": episode_id,
        "scenario_id": scenario_id,
        "topology": topology,
        "links": links,
        "flows": flows,
        "config": config,
    }