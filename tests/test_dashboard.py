"""
Tests for dashboard visualization and helper utilities.
"""

import pytest
from simulation.runner import run_simulation_episode
from dashboard import build_topology_figure, get_calibrated_model


def test_model_loads_or_trains():
    """Verify that model loading returns a trained predictor."""
    model = get_calibrated_model()
    assert model is not None


@pytest.mark.parametrize("scenario_id", ["normal", "shared_bottleneck", "background_surge"])
def test_build_topology_figure_all_scenarios(scenario_id):
    """Verify topology figure generation across all three scenarios."""
    state = run_simulation_episode(scenario_id)
    fig = build_topology_figure(state, selected_flow_id="f1")
    assert fig is not None
    # Figure should contain traces for base links, midpoint annotations, and nodes
    assert len(fig.data) >= 7


def test_build_topology_figure_with_proposed_route():
    """Verify proposed route overlay is included in figure traces."""
    state = run_simulation_episode("shared_bottleneck")
    proposed = ["n1", "n3", "n4"]
    fig = build_topology_figure(state, selected_flow_id="f1", proposed_route=proposed)
    assert fig is not None
    # Traces should exist
    assert len(fig.data) > 7
