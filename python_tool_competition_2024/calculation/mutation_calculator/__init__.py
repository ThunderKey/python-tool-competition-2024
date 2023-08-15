"""Calculator to gather mutation analysis results."""

import enum
from collections.abc import Callable, Mapping

from ...config import Config
from ...results import RatioResult
from ...target_finder import Target
from . import cosmic_ray_calculator, mutpy_calculator


class MutationCalculatorName(enum.Enum):
    """A name of the calculator name to use."""

    COSMIC_RAY = enum.auto()
    """See: https://cosmic-ray.readthedocs.io/"""

    MUTPY = enum.auto()
    """See: https://github.com/mutpy/mutpy"""


def calculate_mutation(
    target: Target, config: Config, mutation_calculator_name: MutationCalculatorName
) -> RatioResult:
    """Calculate the mutation analysis results."""
    return _MUTATION_CALCULATORS[mutation_calculator_name](target, config)


_MUTATION_CALCULATORS: Mapping[
    MutationCalculatorName, Callable[[Target, Config], RatioResult]
] = {
    MutationCalculatorName.COSMIC_RAY: cosmic_ray_calculator.calculate_mutation,
    MutationCalculatorName.MUTPY: mutpy_calculator.calculate_mutation,
}
