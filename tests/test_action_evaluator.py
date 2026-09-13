from actions.action_schema import ReroutingAction
from twin_evaluator.action_evaluator import ActionEvaluator


network_state = {
    "flows": [
        {
            "flow_id": "F3",
            "delay": 0.050,
            "packet_loss": 0.020,
            "sla_violation_risk": 0.70
        },
        {
            "flow_id": "F7",
            "delay": 0.030,
            "packet_loss": 0.010,
            "sla_violation_risk": 0.10
        }
    ]
}


action = ReroutingAction(
    action_id="reroute_F3_path_1",
    target_flow="F3",
    old_path=["R1", "R2", "R4"],
    new_path=["R1", "R3", "R4"]
)


evaluator = ActionEvaluator(network_state)

result = evaluator.evaluate(action)


print("TWINSHIELD ACTION EVALUATOR TEST")
print("---------------------------------")

print("Action:", result["action_id"])
print("Target flow:", result["target_flow"])

print("\nPredicted outcomes:")

for flow_id, outcome in result["predicted_outcomes"].items():

    print(
        flow_id,
        "→ delay:",
        outcome["delay"],
        "| packet loss:",
        outcome["packet_loss"],
        "| SLA risk:",
        outcome["sla_violation_risk"]
    )


assert result["success"] is True

assert result["target_flow"] == "F3"

assert result["predicted_outcomes"]["F3"]["delay"] < 0.050

assert result["predicted_outcomes"]["F3"]["packet_loss"] < 0.020

print("\nAction evaluator test passed.")