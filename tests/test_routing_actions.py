from actions.routing_actions import is_valid_rerouting_action


topology = {
    "nodes": [
        "R1",
        "R2",
        "R3",
        "R4"
    ],

    "links": [
        {
            "source": "R1",
            "destination": "R2"
        },
        {
            "source": "R2",
            "destination": "R4"
        },
        {
            "source": "R1",
            "destination": "R3"
        },
        {
            "source": "R3",
            "destination": "R4"
        }
    ]
}


print("TWINSHIELD ROUTING ACTION VALIDATION")
print("-------------------------------------")


# -------------------------------------------------
# Test 1: Valid alternate route
# -------------------------------------------------

valid, reason = is_valid_rerouting_action(
    topology=topology,
    target_flow="F3",
    old_path=["R1", "R2", "R4"],
    new_path=["R1", "R3", "R4"]
)

print("\nTest 1 - Valid alternate route")
print("Valid:", valid)
print("Reason:", reason)


# -------------------------------------------------
# Test 2: Same route
# -------------------------------------------------

valid, reason = is_valid_rerouting_action(
    topology=topology,
    target_flow="F3",
    old_path=["R1", "R2", "R4"],
    new_path=["R1", "R2", "R4"]
)

print("\nTest 2 - Same route")
print("Valid:", valid)
print("Reason:", reason)


# -------------------------------------------------
# Test 3: Invalid link
# -------------------------------------------------

valid, reason = is_valid_rerouting_action(
    topology=topology,
    target_flow="F3",
    old_path=["R1", "R2", "R4"],
    new_path=["R1", "R5", "R4"]
)

print("\nTest 3 - Invalid link")
print("Valid:", valid)
print("Reason:", reason)


# -------------------------------------------------
# Test 4: Different destination
# -------------------------------------------------

valid, reason = is_valid_rerouting_action(
    topology=topology,
    target_flow="F3",
    old_path=["R1", "R2", "R4"],
    new_path=["R1", "R3"]
)

print("\nTest 4 - Different destination")
print("Valid:", valid)
print("Reason:", reason)