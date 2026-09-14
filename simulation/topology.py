"""
Initial network topology for the TWINSHIELD simulation.

The topology is intentionally small so that we can first study
multi-flow congestion, alternate routing, and SLA violations.
"""


def create_initial_topology():
    """
    Create the initial network topology.

    Returns
    -------
    dict
        Network topology containing nodes and links.
    """

    topology = {
        "nodes": [
            "n1",
            "n2",
            "n3",
            "n4",
            "n5",
            "n6"
        ],
        "links": [
            {
                "link_id": "l1",
                "source": "n1",
                "destination": "n2",
                "capacity_mbps": 100,
                "delay_ms": 5,
                "queue_size": 100
            },
            {
                "link_id": "l2",
                "source": "n2",
                "destination": "n4",
                "capacity_mbps": 20,
                "delay_ms": 10,
                "queue_size": 50
            },
            {
                "link_id": "l3",
                "source": "n1",
                "destination": "n3",
                "capacity_mbps": 100,
                "delay_ms": 5,
                "queue_size": 100
            },
            {
                "link_id": "l4",
                "source": "n3",
                "destination": "n4",
                "capacity_mbps": 100,
                "delay_ms": 10,
                "queue_size": 100
            },
            {
                "link_id": "l5",
                "source": "n4",
                "destination": "n5",
                "capacity_mbps": 100,
                "delay_ms": 5,
                "queue_size": 100
            },
            {
                "link_id": "l6",
                "source": "n5",
                "destination": "n6",
                "capacity_mbps": 100,
                "delay_ms": 5,
                "queue_size": 100
            },
            {
                "link_id": "l7",
                "source": "n2",
                "destination": "n5",
                "capacity_mbps": 50,
                "delay_ms": 15,
                "queue_size": 75
            }
        ]
    }

    return topology