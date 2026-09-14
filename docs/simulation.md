# TWINSHIELD Simulation Environment

## 1. Purpose

The simulation environment generates network states and telemetry for training the prediction models and evaluating network-control actions.

It should represent a small multi-flow network where congestion, SLA violations, and alternate-path rerouting can be studied.

## 2. Initial Scope

The initial simulation will use:

- A small network of approximately 4–8 nodes.
- Multiple concurrent traffic flows.
- Shared bottleneck links.
- Configurable link capacities, delays, and queue sizes.
- Multiple possible routes between selected nodes.
- Fixed observation intervals.
- A prediction horizon of approximately 5 future time steps.

The simulator may use **ns-3 or Mininet**, depending on implementation feasibility.

## 3. Initial Scenarios

The simulator should support the following scenarios:

### Normal Operation

All flows operate below capacity, with no SLA violations.

### Shared Bottleneck

Multiple flows share a congested link, causing increased delay, packet loss, or reduced throughput.

### Background Traffic Surge

A background flow increases its transmission rate and causes degradation in the target flow.

### Alternate Path Available

The target flow experiences congestion while another feasible route is available.

### No Safe Action

All alternate routes either fail feasibility checks, provide insufficient improvement, or cause another flow to violate its SLA.

## 4. Telemetry Collection

At every observation time step, collect:

- Timestamp
- Scenario and episode ID
- Link capacity
- Link utilization
- Queue occupancy
- Queue delay
- Per-flow throughput
- Per-flow delay
- Per-flow packet loss
- Flow rate
- Flow route
- Flow priority
- SLA thresholds
- SLA-violation status
- Congestion indicators

## 5. Network State

The simulator should provide a common `network_state` object:

```python
network_state = {
    "timestamp": 120,
    "episode_id": "episode_001",
    "scenario_id": "shared_bottleneck",
    "topology": {...},
    "links": [...],
    "flows": [...]
}