from safety.constraints import SafetyConstraint


class SafetySelector:
    """
    Selects whether a candidate action should be accepted
    or rejected based on target-flow improvement and
    protected-flow safety constraints.
    """

    def __init__(self, uncertainty_limit=0.30):
        self.uncertainty_limit = uncertainty_limit

    def evaluate(
        self,
        target_flow,
        risk_before,
        risk_after,
        protected_flows
    ):
        """
        Evaluate one candidate action.

        Parameters:
            target_flow: ID of the flow being improved.
            risk_before: Target flow risk before action.
            risk_after: Target flow risk after action.
            protected_flows: Dictionary containing risk information
                             for other flows.

        Returns:
            A dictionary containing the final decision.
        """

        # ---------------------------------------------------------
        # 1. Check whether the target flow actually improves
        # ---------------------------------------------------------

        if risk_after >= risk_before:
            return {
                "status": "reject",
                "reason": "Target flow does not improve",
                "target_flow": target_flow
            }

        # ---------------------------------------------------------
        # 2. Check every protected flow
        # ---------------------------------------------------------

        violated_flows = []

        for flow_id, information in protected_flows.items():

            predicted_risk = information["risk_after"]
            allowed_risk = information["allowed_risk"]

            constraint = SafetyConstraint(
                flow_id=flow_id,
                allowed_risk=allowed_risk
            )

            if not constraint.check(predicted_risk):
                violated_flows.append({
                    "flow_id": flow_id,
                    "predicted_risk": predicted_risk,
                    "allowed_risk": allowed_risk
                })

        # ---------------------------------------------------------
        # 3. Reject if another flow becomes unsafe
        # ---------------------------------------------------------

        if violated_flows:

            return {
                "status": "reject",
                "reason": "Protected flow safety constraint violated",
                "target_flow": target_flow,
                "target_risk_before": risk_before,
                "target_risk_after": risk_after,
                "violated_flows": violated_flows
            }

        # ---------------------------------------------------------
        # 4. Otherwise accept the action
        # ---------------------------------------------------------

        return {
            "status": "accept",
            "reason": "Target flow improves and all protected flows remain safe",
            "target_flow": target_flow,
            "target_risk_before": risk_before,
            "target_risk_after": risk_after,
            "violated_flows": []
        }