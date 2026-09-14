"""
End-to-end decision pipeline for TWINSHIELD.

The pipeline:
1. Validates a candidate rerouting action.
2. Evaluates the action counterfactually.
3. Extracts before/after risk and uncertainty.
4. Applies safety constraints and abstention policy.
5. Returns a structured decision.
"""

from actions.routing_actions import is_valid_rerouting_action
from safety.selector import SafetySelector
from twin_evaluator.action_evaluator import ActionEvaluator


class DecisionPipeline:
    """
    Connects action validation, counterfactual evaluation,
    and safety selection into one workflow.
    """

    def __init__(self, network_state, model=None, uncertainty_limit=0.30):
        self.network_state = network_state
        self.model = model
        self.evaluator = ActionEvaluator(
            network_state=network_state,
            model=model
        )
        self.selector = SafetySelector(
            uncertainty_limit=uncertainty_limit
        )

    def _find_flow(self, flow_id):
        """Return a flow from the current network state."""
        for flow in self.network_state.get("flows", []):
            if flow["flow_id"] == flow_id:
                return flow
        return None

    def _validate_action(self, action):
        """Validate a rerouting action against the network topology."""
        return is_valid_rerouting_action(
            topology=self.network_state["topology"],
            target_flow=action.target_flow,
            old_path=action.old_path,
            new_path=action.new_path
        )

    def _build_protected_flows(self, target_flow_id, predicted_outcomes):
        """
        Build protected-flow information for SafetySelector.

        The allowed risk is derived from the current risk of each
        non-target flow. This conservative default prevents the
        pipeline from accepting an action that increases the risk
        of another flow beyond its current level.
        """
        protected_flows = {}

        for flow in self.network_state.get("flows", []):
            flow_id = flow["flow_id"]

            if flow_id == target_flow_id:
                continue

            predicted_outcome = predicted_outcomes.get(flow_id, {})

            protected_flows[flow_id] = {
                "risk_after": predicted_outcome.get(
                    "sla_violation_risk",
                    flow.get("sla_violation_risk", 0.0)
                ),
                "allowed_risk": flow.get(
                    "sla_violation_risk",
                    0.0
                ),
                "uncertainty": predicted_outcome.get(
                    "uncertainty_score"
                )
            }

        return protected_flows

    def evaluate(self, action):
        """
        Validate and evaluate one candidate action.

        Returns
        -------
        dict
            Structured validation, evaluation, and safety decision.
        """

        # ---------------------------------------------------------
        # 1. Validate action
        # ---------------------------------------------------------

        is_valid, validation_reason = self._validate_action(action)

        if not is_valid:
            return {
                "status": "reject",
                "stage": "validation",
                "reason": validation_reason,
                "action_id": action.action_id,
                "target_flow": action.target_flow
            }

        # ---------------------------------------------------------
        # 2. Confirm target flow exists
        # ---------------------------------------------------------

        target_flow = self._find_flow(action.target_flow)

        if target_flow is None:
            return {
                "status": "reject",
                "stage": "validation",
                "reason": "Target flow not found",
                "action_id": action.action_id,
                "target_flow": action.target_flow
            }

        # ---------------------------------------------------------
        # 3. Evaluate action counterfactually
        # ---------------------------------------------------------

        evaluation = self.evaluator.evaluate(action)

        if not evaluation.get("success", False):
            return {
                "status": "reject",
                "stage": "evaluation",
                "reason": evaluation.get(
                    "reason",
                    "Action evaluation failed"
                ),
                "action_id": action.action_id,
                "target_flow": action.target_flow,
                "evaluation": evaluation
            }

        predicted_outcomes = evaluation.get(
            "predicted_outcomes",
            {}
        )

        target_outcome = predicted_outcomes.get(
            action.target_flow,
            {}
        )

        # ---------------------------------------------------------
        # 4. Extract target risk before and after
        # ---------------------------------------------------------

        risk_before = target_flow.get(
            "sla_violation_risk",
            0.0
        )

        risk_after = target_outcome.get(
            "sla_violation_risk",
            risk_before
        )

        target_uncertainty = target_outcome.get(
            "uncertainty_score"
        )

        # ---------------------------------------------------------
        # 5. Build protected-flow constraints
        # ---------------------------------------------------------

        protected_flows = self._build_protected_flows(
            target_flow_id=action.target_flow,
            predicted_outcomes=predicted_outcomes
        )

        # ---------------------------------------------------------
        # 6. Apply safety selector
        # ---------------------------------------------------------

        safety_decision = self.selector.evaluate(
            target_flow=action.target_flow,
            risk_before=risk_before,
            risk_after=risk_after,
            protected_flows=protected_flows,
            target_uncertainty=target_uncertainty
        )

        # ---------------------------------------------------------
        # 7. Return combined result
        # ---------------------------------------------------------

        return {
            "status": safety_decision["status"],
            "stage": "safety_selection",
            "reason": safety_decision["reason"],
            "action_id": action.action_id,
            "target_flow": action.target_flow,
            "old_path": action.old_path,
            "new_path": action.new_path,
            "risk_before": risk_before,
            "risk_after": risk_after,
            "target_uncertainty": target_uncertainty,
            "protected_flows": protected_flows,
            "evaluation": evaluation,
            "safety_decision": safety_decision
        }