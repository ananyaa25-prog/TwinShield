from safety.constraints import SafetyConstraint


def main():
    constraint = SafetyConstraint(
        flow_id="F7",
        allowed_risk=0.20
    )

    print("TWINSHIELD SAFETY CONSTRAINT TEST")
    print("----------------------------------")

    # Test 1: Safe prediction
    risk = 0.10
    result = constraint.check(risk)

    print("\nTest 1 - Risk below allowed limit")
    print("Flow:", constraint.flow_id)
    print("Predicted risk:", risk)
    print("Allowed risk:", constraint.allowed_risk)
    print("Safe:", result)

    assert result is True

    # Test 2: Risk exactly at the limit
    risk = 0.20
    result = constraint.check(risk)

    print("\nTest 2 - Risk exactly at allowed limit")
    print("Predicted risk:", risk)
    print("Allowed risk:", constraint.allowed_risk)
    print("Safe:", result)

    assert result is True

    # Test 3: Unsafe prediction
    risk = 0.65
    result = constraint.check(risk)

    print("\nTest 3 - Risk above allowed limit")
    print("Predicted risk:", risk)
    print("Allowed risk:", constraint.allowed_risk)
    print("Safe:", result)

    assert result is False

    print("\nAll safety constraint tests passed.")


if __name__ == "__main__":
    main()