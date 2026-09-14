"""
Action evaluator for TWINSHIELD.

The evaluator supports:
1. Counterfactual simulation when a complete network state is available.
2. A backward-compatible deterministic fallback for minimal prototype states.
"""

from models.predictor import predict_sla_risk
from twin_evaluator.counterfactual import build_counterfactual_state


class ActionEvaluator:
    """
    Evaluate candidate network actions.

    Parameters
    ----------
    network_state : dict
        Current network state.

    model : optional
        Calibrated prediction model. If supplied, it is used for
        post-action risk prediction when complete telemetry is available.
    """

    def __init__(self, network_state, model=None):
        self.network_state = network_state
        self.model = model

    def _find_flow(self, flow_id, network_state=None):
        """
        Find a flow by ID.
        """
        state = (
            self.network_state
            if network_state is None
            else network_state
        )

        for flow in state.get("flows", []):
            if flow["flow_id"] == flow_id:
                return flow

        return None

    def _has_complete_simulation_state(self):
        """
        Check whether the state contains the fields required for
        counterfactual simulation.
        """
        required_state_keys = {"links", "flows", "timestamp"}

        if not required_state_keys.issubset(self.network_state):
            return False

        flows = self.network_state.get("flows", [])

        if not flows:
            return False

        required_flow_keys = {
            "flow_id",
            "source",
            "destination",
            "route",
            "rate_mbps",
            "sla",
        }

        return all(
            required_flow_keys.issubset(flow)
            for flow in flows
        )

    def _build_telemetry_row(self, flow, network_state):
        """
        Convert a simulated flow into predictor-compatible telemetry.
        """
        return {
            "timestamp": network_state.get("timestamp", 0),
            "scenario_id": network_state.get(
                "scenario_id",
                "unknown",
            ),
            "flow_id": flow["flow_id"],
            "rate_mbps": flow.get("rate_mbps", 0.0),
            "throughput_mbps": flow.get(
                "throughput_mbps",
                flow.get("rate_mbps", 0.0),
            ),
            "delay_ms": flow.get("delay", 0.0),
            "packet_loss": flow.get("packet_loss", 0.0),
            "max_link_utilization": flow.get(
                "max_link_utilization",
                0.0,
            ),
            "max_queue_delay_ms": flow.get(
                "max_queue_delay_ms",
                0.0,
            ),
        }

    def _predict_flow_risk(self, flow, network_state):
        """
        Predict risk using the calibrated model when available.
        """
        if self.model is None:
            return {
                "predicted_sla_violation_probability": flow.get(
                    "sla_violation_risk",
                    0.0,
                ),
                "risk_category": "unknown",
                "uncertainty_score": None,
                "confidence_score": None,
                "decision_status": "not_available",
            }

        telemetry_row = self._build_telemetry_row(
            flow,
            network_state,
        )

        return predict_sla_risk(
            self.model,
            telemetry_row,
        )

    def _evaluate_with_counterfactual(self, action):
        """
        Evaluate an action using a recalculated counterfactual state.
        """
        counterfactual_state = build_counterfactual_state(
            network_state=self.network_state,
            action=action,
        )

        target_flow_id = action.target_flow
        target_flow = self._find_flow(
            target_flow_id,
            counterfactual_state,
        )

        result = {
            "success": True,
            "action_id": action.action_id,
            "target_flow": target_flow_id,
            "old_path": action.old_path,
            "new_path": action.new_path,
            "evaluation_type": "counterfactual_simulation",
            "predicted_outcomes": {},
        }

        for flow in counterfactual_state["flows"]:
            flow_id = flow["flow_id"]
            risk = self._predict_flow_risk(
                flow,
                counterfactual_state,
            )

            result["predicted_outcomes"][flow_id] = {
                "delay": flow.get("delay", 0.0),
                "packet_loss": flow.get("packet_loss", 0.0),
                "sla_violation_risk": risk[
                    "predicted_sla_violation_probability"
                ],
                **risk,
            }

        return result

    def _evaluate_with_fallback(self, action):
        """
        Preserve the original deterministic behavior for minimal
        prototype network states.
        """
        target_flow_id = action.target_flow
        target_flow = self._find_flow(target_flow_id)

        if target_flow is None:
            return {
                "success": False,
                "reason": "Target flow not found",
                "target_flow": target_flow_id,
            }

        result = {
            "success": True,
            "action_id": action.action_id,
            "target_flow": target_flow_id,
            "old_path": action.old_path,
            "new_path": action.new_path,
            "evaluation_type": "deterministic_fallback",
            "predicted_outcomes": {},
        }

        current_delay = target_flow.get("delay", 0.0)
        current_loss = target_flow.get("packet_loss", 0.0)

        predicted_target_delay = current_delay * 0.80
        predicted_target_loss = current_loss * 0.80

        target_risk = self._predict_flow_risk(
            target_flow,
            self.network_state,
        )

        result["predicted_outcomes"][target_flow_id] = {
            "delay": predicted_target_delay,
            "packet_loss": predicted_target_loss,
            "sla_violation_risk": target_risk[
                "predicted_sla_violation_probability"
            ],
            **target_risk,
        }

        for flow in self.network_state.get("flows", []):
            if flow["flow_id"] == target_flow_id:
                continue

            flow_id = flow["flow_id"]
            protected_risk = self._predict_flow_risk(
                flow,
                self.network_state,
            )

            result["predicted_outcomes"][flow_id] = {
                "delay": flow.get("delay", 0.0),
                "packet_loss": flow.get("packet_loss", 0.0),
                "sla_violation_risk": protected_risk[
                    "predicted_sla_violation_probability"
                ],
                **protected_risk,
            }

        return result

    def evaluate(self, action):
        """
        Evaluate a candidate action using the appropriate mode.
        """
        target_flow_id = action.target_flow

        if self._find_flow(target_flow_id) is None:
            return {
                "success": False,
                "reason": "Target flow not found",
                "target_flow": target_flow_id,
            }

        if self._has_complete_simulation_state():
            return self._evaluate_with_counterfactual(action)

        return self._evaluate_with_fallback(action)