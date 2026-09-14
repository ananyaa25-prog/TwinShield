"""
Deterministic simulation engine for TWINSHIELD.

This module advances a network state by one simulation step.
The current implementation is intentionally simple and deterministic.
"""

from copy import deepcopy


def advance_simulation(network_state, time_step=1):
    """
    Advance the network state by one simulation step.

    Parameters
    ----------
    network_state : dict
        Current network state containing links and flows.

    time_step : int
        Number of simulation time units to advance.

    Returns
    -------
    dict
        A new, updated network state.

    Notes
    -----
    This function does not modify the original network state.
    """

    if time_step <= 0:
        raise ValueError("time_step must be greater than zero.")

    state = deepcopy(network_state)

    # ---------------------------------------------------------
    # 1. Calculate offered traffic on every link
    # ---------------------------------------------------------

    link_traffic = {
        link["link_id"]: 0.0
        for link in state["links"]
    }

    for flow in state["flows"]:
        route = flow["route"]
        rate = flow["rate_mbps"]

        for source, destination in zip(route, route[1:]):
            for link in state["links"]:
                same_direction = (
                    link["source"] == source
                    and link["destination"] == destination
                )

                reverse_direction = (
                    link["source"] == destination
                    and link["destination"] == source
                )

                if same_direction or reverse_direction:
                    link_traffic[link["link_id"]] += rate
                    break

    # ---------------------------------------------------------
    # 2. Update link-level telemetry
    # ---------------------------------------------------------

    link_metrics = {}

    for link in state["links"]:
        link_id = link["link_id"]
        capacity = link["capacity_mbps"]
        offered_traffic = (
           link_traffic[link_id]
           + link.get("background_load_mbps", 0.0)
        )

        utilization = min(
            offered_traffic / capacity,
            1.0
        )

        queue_occupancy = min(
            utilization * 0.9,
            1.0
        )

        # Queue delay rises sharply after 70% utilization.
        congestion_factor = max(
            0.0,
            (utilization - 0.7) / 0.3
        )

        queue_delay_ms = (
            1.0
            + 40.0 * congestion_factor
        )

        link["utilization"] = round(utilization, 4)
        link["queue_occupancy"] = round(queue_occupancy, 4)
        link["queue_delay_ms"] = round(queue_delay_ms, 4)

        link_metrics[link_id] = {
            "utilization": utilization,
            "queue_delay_ms": queue_delay_ms,
        }

    # ---------------------------------------------------------
    # 3. Update flow-level telemetry
    # ---------------------------------------------------------

    for flow in state["flows"]:
        route = flow["route"]

        total_delay = 0.0
        maximum_utilization = 0.0

        for source, destination in zip(route, route[1:]):
            for link in state["links"]:
                same_direction = (
                    link["source"] == source
                    and link["destination"] == destination
                )

                reverse_direction = (
                    link["source"] == destination
                    and link["destination"] == source
                )

                if same_direction or reverse_direction:
                    total_delay += (
                        link["delay_ms"]
                        + link["queue_delay_ms"]
                    )

                    maximum_utilization = max(
                        maximum_utilization,
                        link["utilization"]
                    )

                    break

        # Packet loss begins when the most congested link
        # exceeds 85% utilization.
        packet_loss = max(
            0.0,
            (maximum_utilization - 0.85) * 0.4
        )

        packet_loss = min(packet_loss, 1.0)

        max_delay = flow["sla"]["max_delay_ms"]
        max_packet_loss = flow["sla"]["max_packet_loss"]

        delay_pressure = total_delay / max_delay
        loss_pressure = packet_loss / max_packet_loss

        # A simple deterministic risk score.
        sla_violation_risk = min(
            max(delay_pressure, loss_pressure),
            1.0
        )

        sla_violation = (
            total_delay > max_delay
            or packet_loss > max_packet_loss
        )

        # Throughput decreases when the most congested link
        # becomes heavily utilized.
        throughput_factor = max(
            0.0,
            1.0 - max(0.0, maximum_utilization - 0.8)
        )

        throughput = flow["rate_mbps"] * throughput_factor

        flow["throughput_mbps"] = round(throughput, 4)
        flow["delay"] = round(total_delay, 4)
        flow["packet_loss"] = round(packet_loss, 4)
        flow["sla_violation_risk"] = round(
            sla_violation_risk,
            4
        )
        flow["sla_violation"] = sla_violation

    # ---------------------------------------------------------
    # 4. Advance simulation time
    # ---------------------------------------------------------

    state["timestamp"] += time_step

    return state