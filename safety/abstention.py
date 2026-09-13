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

        Returns:
            True  -> abstain
            False -> continue decision process
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