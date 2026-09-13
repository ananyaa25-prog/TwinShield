from actions.action_schema import ReroutingAction


action = ReroutingAction(
    action_id="reroute_F3_path_2",
    target_flow="F3",
    old_path=["R1", "R2", "R4"],
    new_path=["R1", "R3", "R4"]
)

print("TWINSHIELD ACTION")
print("-----------------")
print(action.to_dict())