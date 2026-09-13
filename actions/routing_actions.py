import networkx as nx


def build_graph(topology):
    """
    Build a NetworkX graph from the TWINSHIELD
    network topology.
    """

    graph = nx.Graph()

    for link in topology["links"]:
        source = link["source"]
        destination = link["destination"]

        graph.add_edge(source, destination)

    return graph


def is_valid_path(graph, path):
    """
    Check whether every consecutive pair of nodes
    in a path is connected in the network.
    """

    if not path or len(path) < 2:
        return False

    for i in range(len(path) - 1):

        source = path[i]
        destination = path[i + 1]

        if not graph.has_edge(source, destination):
            return False

    return True


def is_valid_rerouting_action(
    topology,
    target_flow,
    old_path,
    new_path
):
    """
    Validate a proposed rerouting action.

    Returns
    -------
    tuple
        (True, "Valid action") when valid.

        (False, reason) when invalid.
    """

    # -------------------------------------------------
    # Check 1: Target flow
    # -------------------------------------------------

    if not target_flow:
        return False, "Target flow is missing"

    # -------------------------------------------------
    # Check 2: Path length
    # -------------------------------------------------

    if not old_path or len(old_path) < 2:
        return False, "Old path is invalid"

    if not new_path or len(new_path) < 2:
        return False, "New path is invalid"

    # -------------------------------------------------
    # Check 3: New path must be different
    # -------------------------------------------------

    if old_path == new_path:
        return False, "New path is identical to old path"

    # -------------------------------------------------
    # Build network graph
    # -------------------------------------------------

    graph = build_graph(topology)

    # -------------------------------------------------
    # Check 4: Old path must exist
    # -------------------------------------------------

    if not is_valid_path(graph, old_path):
        return False, "Old path contains an invalid network link"

    # -------------------------------------------------
    # Check 5: New path must exist
    # -------------------------------------------------

    if not is_valid_path(graph, new_path):
        return False, "New path contains an invalid network link"

    # -------------------------------------------------
    # Check 6: Source must remain the same
    # -------------------------------------------------

    if old_path[0] != new_path[0]:
        return False, "New path has a different source"

    # -------------------------------------------------
    # Check 7: Destination must remain the same
    # -------------------------------------------------

    if old_path[-1] != new_path[-1]:
        return False, "New path has a different destination"

    return True, "Valid rerouting action"