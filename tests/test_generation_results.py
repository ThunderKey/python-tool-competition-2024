from python_tool_competition_2024.generation_results import FailureReason


def test_failure_reason_order() -> None:
    assert tuple(FailureReason) == (
        FailureReason.UNSUPPORTED_FEATURE_USED,
        FailureReason.NOTHING_GENERATED,
        FailureReason.UNEXPECTED_ERROR,
    )
    assert tuple(sorted(FailureReason)) == (
        FailureReason.NOTHING_GENERATED,
        FailureReason.UNEXPECTED_ERROR,
        FailureReason.UNSUPPORTED_FEATURE_USED,
    )
