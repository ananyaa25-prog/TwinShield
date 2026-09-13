from actions.candidate_generator import generate_candidate_actions


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


target_flow = "F3"

old_path = [
    "R1",
    "R2",
    "R4"
]


actions = generate_candidate_actions(
    topology=topology,
    target_flow_id=target_flow,
    old_path=old_path
)


print("TWINSHIELD CANDIDATE ACTION PIPELINE")
print("------------------------------------")

print("Target flow:", target_flow)
print("Current path:", old_path)

print("\nValid candidate actions:")

for action in actions:
    print(action.to_dict())

print("\nNumber of candidates:", len(actions))