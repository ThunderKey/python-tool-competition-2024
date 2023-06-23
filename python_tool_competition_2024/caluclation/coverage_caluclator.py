"""Calculator to gather line and branch coverage results."""

from typing import NamedTuple

from ..results import RatioResult
from ..target_finder import Target


class Coverages(NamedTuple):
    """A named tuple of line and branch coverages."""

    line: RatioResult
    branch: RatioResult


def calculate_coverages(_target: Target) -> Coverages:
    """Calculate the line coverage results."""
    return Coverages(RatioResult(1000, 0), RatioResult(1000, 0))
