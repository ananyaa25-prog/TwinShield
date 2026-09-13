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