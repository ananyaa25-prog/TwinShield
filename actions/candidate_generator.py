import networkx as nx

from actions.action_schema import ReroutingAction
from actions.routing_actions import is_valid_rerouting_action


def generate_candidate_actions(
    topology,
    target_flow_id,
    old_path,
    max_candidates=5
):
    """
    Generate feasible alternate-path rerouting actions.

    Only actions that pass routing validation are returned.
    """

    graph = nx.Graph()

    # Build graph from topology
    for link in topology["links"]:
        source = link["source"]
        destination = link["destination"]

        graph.add_edge(source, destination)

    source = old_path[0]
    destination = old_path[-1]

    candidate_actions = []

    try:
        paths = nx.shortest_simple_paths(
            graph,
            source,
            destination
        )

        path_number = 1

        for path in paths:

            path = list(path)

            # Ignore the current route
            if path == old_path:
                continue

            # Check whether the proposed rerouting action is valid
            valid, reason = is_valid_rerouting_action(
                topology=topology,
                target_flow=target_flow_id,
                old_path=old_path,
                new_path=path
            )

            if not valid:
                continue

            action = ReroutingAction(
                action_id=f"reroute_{target_flow_id}_path_{path_number}",
                target_flow=target_flow_id,
                old_path=old_path,
                new_path=path
            )

            candidate_actions.append(action)

            path_number += 1

            if len(candidate_actions) >= max_candidates:
                break

    except nx.NetworkXNoPath:
        return []

    return candidate_actions