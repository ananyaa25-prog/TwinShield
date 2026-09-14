"""
Simulation runner for TWINSHIELD.

This module provides a high-level interface for creating,
configuring, and advancing simulation episodes.
"""

from simulation.network_state import create_initial_network_state
from simulation.scenarios import apply_scenario
from simulation.engine import advance_simulation
from simulation.config import create_simulation_config


def run_simulation_episode(
    scenario_id="normal",
    num_steps=1,
    config=None,
    episode_id="episode_001",
):
    """
    Run a simulation episode for a selected scenario.

    Parameters
    ----------
    scenario_id : str
        Scenario to simulate.

    num_steps : int
        Number of simulation steps to execute.

    config : dict or None
        Simulation configuration. If None, default configuration
        is used.

    episode_id : str
        Identifier for the simulation episode.

    Returns
    -------
    dict
        Final network state after the requested number of steps.

    Raises
    ------
    ValueError
        If num_steps is less than zero.
    """

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

    for _ in range(num_steps):
        state = advance_simulation(state)

    return state