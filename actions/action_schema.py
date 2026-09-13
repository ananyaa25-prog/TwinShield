class ReroutingAction:
    """
    Represents a candidate rerouting intervention
    for a network flow.
    """

    def __init__(
        self,
        action_id,
        target_flow,
        old_path,
        new_path
    ):
        self.action_id = action_id
        self.action_type = "reroute"
        self.target_flow = target_flow
        self.old_path = old_path
        self.new_path = new_path

    def to_dict(self):
        """
        Convert the action into a dictionary so that
        other TWINSHIELD modules can easily use it.
        """
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "target_flow": self.target_flow,
            "old_path": self.old_path,
            "new_path": self.new_path
        }