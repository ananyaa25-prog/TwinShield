from safety.selector import SafetySelector


def test_selector_accepts_safe_rerouting():
    selector = SafetySelector()

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.82,
        risk_after=0.24,
        protected_flows={
            "F7": {
                "risk_after": 0.12,
                "allowed_risk": 0.20
            },
            "F8": {
                "risk_after": 0.10,
                "allowed_risk": 0.20
            }
        }
    )

    assert result["status"] == "accept"
    assert result["target_flow"] == "F3"
    assert result["violated_flows"] == []


def test_selector_rejects_collateral_risk():
    selector = SafetySelector()

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.82,
        risk_after=0.24,
        protected_flows={
            "F7": {
                "risk_after": 0.65,
                "allowed_risk": 0.20
            },
            "F8": {
                "risk_after": 0.12,
                "allowed_risk": 0.20
            }
        }
    )

    assert result["status"] == "reject"
    assert result["reason"] == "Protected flow safety constraint violated"
    assert len(result["violated_flows"]) == 1
    assert result["violated_flows"][0]["flow_id"] == "F7"


def test_selector_rejects_when_target_does_not_improve():
    selector = SafetySelector()

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.30,
        risk_after=0.40,
        protected_flows={
            "F7": {
                "risk_after": 0.10,
                "allowed_risk": 0.20
            }
        }
    )

    assert result["status"] == "reject"
    assert result["reason"] == "Target flow does not improve"
    assert result["target_flow"] == "F3"


def test_selector_rejects_when_target_risk_is_unchanged():
    selector = SafetySelector()

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.30,
        risk_after=0.30,
        protected_flows={}
    )

    assert result["status"] == "reject"
    assert result["reason"] == "Target flow does not improve"


def test_selector_accepts_when_protected_risk_equals_allowed_limit():
    selector = SafetySelector()

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.80,
        risk_after=0.20,
        protected_flows={
            "F7": {
                "risk_after": 0.20,
                "allowed_risk": 0.20
            }
        }
    )

    assert result["status"] == "accept"
    assert result["violated_flows"] == []

def test_selector_abstains_when_target_uncertainty_is_high():
    selector = SafetySelector(uncertainty_limit=0.30)

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.82,
        risk_after=0.24,
        target_uncertainty=0.65,
        protected_flows={
            "F7": {
                "risk_after": 0.12,
                "allowed_risk": 0.20
            }
        }
    )

    assert result["status"] == "abstain"
    assert result["reason"] == (
        "Target-flow prediction uncertainty is too high"
    )
    assert result["target_uncertainty"] == 0.65


def test_selector_abstains_when_protected_flow_uncertainty_is_high():
    selector = SafetySelector(uncertainty_limit=0.30)

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.82,
        risk_after=0.24,
        target_uncertainty=0.10,
        protected_flows={
            "F7": {
                "risk_after": 0.12,
                "allowed_risk": 0.20,
                "uncertainty": 0.75
            }
        }
    )

    assert result["status"] == "abstain"
    assert result["reason"] == (
        "Protected-flow prediction uncertainty is too high"
    )
    assert len(result["uncertain_flows"]) == 1
    assert result["uncertain_flows"][0]["flow_id"] == "F7"


def test_selector_accepts_when_uncertainty_is_within_limit():
    selector = SafetySelector(uncertainty_limit=0.30)

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.82,
        risk_after=0.24,
        target_uncertainty=0.20,
        protected_flows={
            "F7": {
                "risk_after": 0.12,
                "allowed_risk": 0.20,
                "uncertainty": 0.25
            }
        }
    )

    assert result["status"] == "accept"
    assert result["violated_flows"] == []


def test_selector_rejects_safety_violation_before_abstention():
    selector = SafetySelector(uncertainty_limit=0.30)

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.82,
        risk_after=0.24,
        target_uncertainty=0.80,
        protected_flows={
            "F7": {
                "risk_after": 0.65,
                "allowed_risk": 0.20,
                "uncertainty": 0.80
            }
        }
    )

    assert result["status"] == "reject"
    assert result["reason"] == (
        "Protected flow safety constraint violated"
    )


def test_selector_accepts_at_uncertainty_limit():
    selector = SafetySelector(uncertainty_limit=0.30)

    result = selector.evaluate(
        target_flow="F3",
        risk_before=0.82,
        risk_after=0.24,
        target_uncertainty=0.30,
        protected_flows={
            "F7": {
                "risk_after": 0.12,
                "allowed_risk": 0.20,
                "uncertainty": 0.30
            }
        }
    )

    assert result["status"] == "accept"