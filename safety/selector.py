from safety.constraints import SafetyConstraint, AbstentionPolicy


class SafetySelector:
    """
    Selects whether a candidate action should be accepted,
    rejected, or marked for abstention.

    Decision logic:
    1. The target flow must improve.
    2. Protected-flow safety constraints must remain satisfied.
    3. Relevant prediction uncertainty must be within the
       configured limit.
    """

    def __init__(self, uncertainty_limit=0.30):
        self.uncertainty_limit = uncertainty_limit
        self.abstention_policy = AbstentionPolicy(
            uncertainty_limit=uncertainty_limit
        )

    def evaluate(
        self,
        target_flow,
        risk_before,
        risk_after,
        protected_flows,
        target_uncertainty=None
    ):
        """
        Evaluate one candidate action.

        Parameters:
            target_flow: ID of the flow being improved.
            risk_before: Target flow risk before the action.
            risk_after: Target flow risk after the action.
            protected_flows: Dictionary containing risk and
                             optional uncertainty information
                             for protected flows.
            target_uncertainty: Optional uncertainty associated
                                with the target-flow prediction.

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
        # 2. Check every protected flow's safety constraint
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
        # 4. Check target-flow uncertainty, if provided
        # ---------------------------------------------------------

        if target_uncertainty is not None:
            target_abstention = self.abstention_policy.evaluate(
                target_uncertainty
            )

            if target_abstention["status"] == "abstain":
                return {
                    "status": "abstain",
                    "reason": "Target-flow prediction uncertainty is too high",
                    "target_flow": target_flow,
                    "target_risk_before": risk_before,
                    "target_risk_after": risk_after,
                    "target_uncertainty": target_uncertainty,
                    "uncertainty_limit": self.uncertainty_limit,
                    "violated_flows": []
                }

        # ---------------------------------------------------------
        # 5. Check protected-flow uncertainty, if provided
        # ---------------------------------------------------------

        uncertain_flows = []

        for flow_id, information in protected_flows.items():

            uncertainty = information.get("uncertainty")

            # Preserve backward compatibility when uncertainty
            # is not included for a protected flow.
            if uncertainty is None:
                continue

            abstention_result = self.abstention_policy.evaluate(
                uncertainty
            )

            if abstention_result["status"] == "abstain":
                uncertain_flows.append({
                    "flow_id": flow_id,
                    "uncertainty": uncertainty,
                    "uncertainty_limit": self.uncertainty_limit
                })

        if uncertain_flows:
            return {
                "status": "abstain",
                "reason": "Protected-flow prediction uncertainty is too high",
                "target_flow": target_flow,
                "target_risk_before": risk_before,
                "target_risk_after": risk_after,
                "uncertain_flows": uncertain_flows,
                "violated_flows": []
            }

        # ---------------------------------------------------------
        # 6. Accept if all checks pass
        # ---------------------------------------------------------

        return {
            "status": "accept",
            "reason": (
                "Target flow improves, all protected flows remain safe, "
                "and prediction uncertainty is acceptable"
            ),
            "target_flow": target_flow,
            "target_risk_before": risk_before,
            "target_risk_after": risk_after,
            "violated_flows": []
        }