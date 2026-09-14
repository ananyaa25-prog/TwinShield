from actions.action_schema import ReroutingAction
from decision.pipeline import DecisionPipeline
from simulation.network_state import create_initial_network_state


def main():
    # Create the initial network state
    network_state = create_initial_network_state()

    # Define a rerouting action for flow f1
    action = ReroutingAction(
        action_id="demo_action_001",
        target_flow="f1",
        old_path=["n1", "n2", "n4"],
        new_path=["n1", "n3", "n4"],
    )

    # Create the decision pipeline
    pipeline = DecisionPipeline(network_state=network_state)

    # Evaluate the proposed action
    result = pipeline.evaluate(action)

    print("\n" + "=" * 60)
    print("TWINSHIELD DECISION PIPELINE DEMONSTRATION")
    print("=" * 60)

    print("\nACTION DETAILS")
    print("-" * 60)
    print(f"Action ID:       {action.action_id}")
    print(f"Action Type:     {action.action_type}")
    print(f"Target Flow:     {action.target_flow}")
    print(f"Old Path:        {action.old_path}")
    print(f"Proposed Path:   {action.new_path}")

    print("\nDECISION SUMMARY")
    print("-" * 60)
    print(f"Final Status:    {result.get('status')}")
    print(f"Decision Stage:  {result.get('stage')}")
    print(f"Reason:          {result.get('reason')}")

    print("\nRISK ANALYSIS")
    print("-" * 60)
    print(f"Risk Before:     {result.get('risk_before')}")
    print(f"Risk After:      {result.get('risk_after')}")
    print(f"Uncertainty:     {result.get('target_uncertainty')}")

    print("\nPROTECTED FLOWS")
    print("-" * 60)

    protected_flows = result.get("protected_flows", {})

    if protected_flows:
        for flow_id, information in protected_flows.items():
            print(f"Flow: {flow_id}")
            print(f"  Risk After:    {information.get('risk_after')}")
            print(f"  Allowed Risk:  {information.get('allowed_risk')}")
            print(f"  Uncertainty:   {information.get('uncertainty')}")
    else:
        print("No protected flows found.")

    print("\nEVALUATION TYPE")
    print("-" * 60)
    evaluation = result.get("evaluation", {})
    print(f"Evaluation:      {evaluation.get('evaluation_type')}")
    print(f"Success:         {evaluation.get('success')}")

    print("\nDETAILED PREDICTED OUTCOMES")
    print("-" * 60)

    predicted_outcomes = evaluation.get("predicted_outcomes", {})

    for flow_id, outcome in predicted_outcomes.items():
        print(f"\nFlow: {flow_id}")
        print(f"  Predicted delay:       {outcome.get('delay')} ms")
        print(f"  Predicted packet loss: {outcome.get('packet_loss')}")
        print(f"  SLA violation risk:    {outcome.get('sla_violation_risk')}")
        print(f"  Risk category:         {outcome.get('risk_category')}")
        print(f"  Uncertainty:           {outcome.get('uncertainty_score')}")

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()