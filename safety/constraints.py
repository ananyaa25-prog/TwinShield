class SafetyConstraint:
    """
    Represents a safety constraint for a network flow.

    A flow is considered safe when its predicted SLA
    violation risk does not exceed its allowed risk.
    """

    def __init__(self, flow_id, allowed_risk):
        self.flow_id = flow_id
        self.allowed_risk = allowed_risk

    def check(self, predicted_risk):
        """
        Check whether the predicted SLA violation risk
        satisfies the safety constraint.

        Returns:
            True  -> safe
            False -> unsafe
        """

        return predicted_risk <= self.allowed_risk

    def to_dict(self):
        """
        Convert the constraint into a dictionary.
        """

        return {
            "flow_id": self.flow_id,
            "allowed_risk": self.allowed_risk
        }

class AbstentionPolicy:
    """
    Determines whether TWINSHIELD should abstain from
    making an automated decision because prediction
    uncertainty is too high.
    """

    def __init__(self, uncertainty_limit=0.30):
        self.uncertainty_limit = uncertainty_limit

    def should_abstain(self, uncertainty):
        """
        Check whether uncertainty is high enough
        to require abstention.
        """

        return uncertainty > self.uncertainty_limit

    def evaluate(self, uncertainty):
        """
        Return a structured abstention decision.
        """

        if self.should_abstain(uncertainty):
            return {
                "status": "abstain",
                "reason": "Prediction uncertainty is too high",
                "uncertainty": uncertainty,
                "uncertainty_limit": self.uncertainty_limit
            }

        return {
            "status": "continue",
            "reason": "Prediction uncertainty is within acceptable limit",
            "uncertainty": uncertainty,
            "uncertainty_limit": self.uncertainty_limit
        }