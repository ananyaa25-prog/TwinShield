class ActionEvaluator:
    """
    Evaluates the expected outcome of a candidate network action.

    This first version provides a deterministic prototype.
    Later, the evaluator can be connected to the Network Digital Twin
    and ML-based outcome prediction.
    """

    def __init__(self, network_state):
        self.network_state = network_state

    def evaluate(self, action):
        """
        Evaluate a rerouting action using the current network state.

        Returns predicted outcomes for the target flow and
        protected flows.
        """

        target_flow_id = action.target_flow

        flows = self.network_state.get("flows", [])

        target_flow = None

        for flow in flows:
            if flow["flow_id"] == target_flow_id:
                target_flow = flow
                break

        if target_flow is None:
            return {
                "success": False,
                "reason": "Target flow not found",
                "target_flow": target_flow_id
            }

        old_path = action.old_path
        new_path = action.new_path

        result = {
            "success": True,
            "action_id": action.action_id,
            "target_flow": target_flow_id,
            "old_path": old_path,
            "new_path": new_path,
            "predicted_outcomes": {}
        }

        # ---------------------------------------------------------
        # Simple prototype assumption:
        # Rerouting reduces the target flow's delay and packet loss.
        # ---------------------------------------------------------

        current_delay = target_flow.get("delay", 0.0)
        current_loss = target_flow.get("packet_loss", 0.0)

        predicted_target_delay = current_delay * 0.80
        predicted_target_loss = current_loss * 0.80

        result["predicted_outcomes"][target_flow_id] = {
            "delay": predicted_target_delay,
            "packet_loss": predicted_target_loss,
            "sla_violation_risk": 0.10
        }

        # ---------------------------------------------------------
        # Protected-flow outcomes.
        #
        # In this prototype, other flows are assumed unchanged.
        # Later, the Digital Twin will estimate collateral effects.
        # ---------------------------------------------------------

        for flow in flows:

            if flow["flow_id"] == target_flow_id:
                continue

            flow_id = flow["flow_id"]

            result["predicted_outcomes"][flow_id] = {
                "delay": flow.get("delay", 0.0),
                "packet_loss": flow.get("packet_loss", 0.0),
                "sla_violation_risk": flow.get(
                    "sla_violation_risk",
                    0.0
                )
            }

        return result