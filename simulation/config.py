"""
Configuration objects for TWINSHIELD simulation episodes.

The configuration separates scenario inputs from the resulting
network telemetry.
"""


DEFAULT_SIMULATION_CONFIG = {
    "flow_rates_mbps": {
        "f1": 15.0,
        "f2": 20.0,
        "f3": 10.0,
    },
    "background_surge_multiplier": 1.0,
    "shared_bottleneck_background_load_mbps": 5.0,
    "background_surge_load_mbps": 40.0,
    "congestion_link_id": None,
    "random_seed": 42,
}


def create_simulation_config(
    flow_rates_mbps=None,
    background_surge_multiplier=1.0,
    shared_bottleneck_background_load_mbps=5.0,
    background_surge_load_mbps=40.0,
    congestion_link_id=None,
    random_seed=42,
):
    """
    Create a simulation configuration.

    Parameters
    ----------
    flow_rates_mbps : dict or None
        Sending rate for each flow.

    background_surge_multiplier : float
        Multiplier applied to background traffic.

    shared_bottleneck_background_load_mbps : float
        Background traffic added to the shared bottleneck link.

    background_surge_load_mbps : float
        Background traffic used in the background surge scenario.

    congestion_link_id : str or None
        Optional link to designate as congested.

    random_seed : int
        Seed reserved for reproducible episode generation.

    Returns
    -------
    dict
        Simulation configuration.
    """

    config = {
        "flow_rates_mbps": dict(
            DEFAULT_SIMULATION_CONFIG["flow_rates_mbps"]
        ),
        "background_surge_multiplier": background_surge_multiplier,
        "shared_bottleneck_background_load_mbps": (
            shared_bottleneck_background_load_mbps
        ),
        "background_surge_load_mbps": background_surge_load_mbps,
        "congestion_link_id": congestion_link_id,
        "random_seed": random_seed,
    }

    if flow_rates_mbps is not None:
        config["flow_rates_mbps"].update(flow_rates_mbps)

    return config