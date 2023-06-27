"""Calculator to gather mutation analysis results."""

from ..results import RatioResult
from ..target_finder import Target


def calculate_mutation(_target: Target) -> RatioResult:
    """Calculate the mutation analysis results."""
    return RatioResult(1000, 0)
