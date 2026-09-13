from safety.selector import SafetySelector


def main():

    selector = SafetySelector()

    print("TWINSHIELD SAFETY SELECTOR TEST")
    print("--------------------------------")

    # =========================================================
    # Test 1: Safe rerouting
    # =========================================================

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

    print("\nTest 1 - Safe rerouting")
    print("Decision:", result["status"])
    print("Reason:", result["reason"])

    assert result["status"] == "accept"

    # =========================================================
    # Test 2: Target improves but another flow becomes unsafe
    # =========================================================

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

    print("\nTest 2 - Collateral risk")
    print("Decision:", result["status"])
    print("Reason:", result["reason"])
    print("Violated flows:", result["violated_flows"])

    assert result["status"] == "reject"

    # =========================================================
    # Test 3: Target flow does not improve
    # =========================================================

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

    print("\nTest 3 - Target does not improve")
    print("Decision:", result["status"])
    print("Reason:", result["reason"])

    assert result["status"] == "reject"

    print("\nAll selector tests passed.")


if __name__ == "__main__":
    main()