"""Calculator to gather generation results."""

from ..generation_results import (
    FailureReason,
    TestGenerationFailure,
    TestGenerationResult,
    TestGenerationSuccess,
)
from ..target_finder import Target


def calculate_generation_results(target: Target) -> TestGenerationResult:
    """Calculate the mutation analysis results."""
    if len(target.relative_source.parts) % 2 == 1:
        return TestGenerationFailure(
            ("Not implemented...",), FailureReason.UNEXPECTED_ERROR
        )
    return TestGenerationSuccess("some body")
