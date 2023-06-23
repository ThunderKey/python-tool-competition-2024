"""Calculator to gather generation results."""

from ..generation_results import (
    FailureReason,
    TestGenerationFailure,
    TestGenerationResult,
)
from ..target_finder import Target


def calculate_generation_results(_target: Target) -> TestGenerationResult:
    """Calculate the mutation analysis results."""
    return TestGenerationFailure(
        ("Not implemented...",), FailureReason.UNEXPECTED_ERROR
    )
