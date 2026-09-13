from safety.abstention import AbstentionPolicy


def main():

    policy = AbstentionPolicy(
        uncertainty_limit=0.30
    )

    print("TWINSHIELD ABSTENTION POLICY TEST")
    print("---------------------------------")

    # =========================================================
    # Test 1: Low uncertainty
    # =========================================================

    uncertainty = 0.10

    result = policy.evaluate(uncertainty)

    print("\nTest 1 - Low uncertainty")
    print("Uncertainty:", uncertainty)
    print("Decision:", result["status"])
    print("Reason:", result["reason"])

    assert result["status"] == "continue"

    # =========================================================
    # Test 2: Uncertainty exactly at limit
    # =========================================================

    uncertainty = 0.30

    result = policy.evaluate(uncertainty)

    print("\nTest 2 - Uncertainty at limit")
    print("Uncertainty:", uncertainty)
    print("Decision:", result["status"])
    print("Reason:", result["reason"])

    assert result["status"] == "continue"

    # =========================================================
    # Test 3: High uncertainty
    # =========================================================

    uncertainty = 0.75

    result = policy.evaluate(uncertainty)

    print("\nTest 3 - High uncertainty")
    print("Uncertainty:", uncertainty)
    print("Decision:", result["status"])
    print("Reason:", result["reason"])

    assert result["status"] == "abstain"

    print("\nAll abstention tests passed.")


if __name__ == "__main__":
    main()