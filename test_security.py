from security import (
    inspect_output,
    authorize_tool,
    validate_transaction_context,
)


def test_full_pan_is_blocked():
    result = inspect_output(
        "Full PAN: 4111-1111-1111-1122"
    )

    assert result["safe"] is False


def test_masked_pan_is_allowed():
    result = inspect_output(
        "Masked PAN: **** **** **** 1122"
    )

    assert result["safe"] is True


def test_allowed_tool():
    result = authorize_tool(
        "cdv_get_transaction"
    )

    assert result["allowed"] is True


def test_forbidden_tool():
    result = authorize_tool(
        "internal_get_all_transactions"
    )

    assert result["allowed"] is False


def test_transaction_context_match():
    result = validate_transaction_context(
        "cdv_get_transaction",
        {"txn_id": "TXN-1001"},
        {"transaction_id": "TXN-1001"},
    )

    assert result["allowed"] is True


def test_transaction_context_mismatch():
    result = validate_transaction_context(
        "cdv_get_transaction",
        {"txn_id": "TXN-9009"},
        {"transaction_id": "TXN-1001"},
    )

    assert result["allowed"] is False


if __name__ == "__main__":
    tests = [
        test_full_pan_is_blocked,
        test_masked_pan_is_allowed,
        test_allowed_tool,
        test_forbidden_tool,
        test_transaction_context_match,
        test_transaction_context_mismatch,
    ]

    for test in tests:
        test()
        print(f"PASS - {test.__name__}")

    print("\nAll security tests passed.")