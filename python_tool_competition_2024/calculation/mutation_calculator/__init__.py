"""Calculator to gather mutation analysis results."""

from collections.abc import Callable, Mapping
from typing import Literal

from ...config import Config
from ...results import RatioResult
from ...target_finder import Target
from . import cosmic_ray_calculator, mutpy_calculator

MutationCalculatorName = Literal["cosmic-ray", "mutpy"]


def calculate_mutation(
    target: Target, config: Config, mutation_calculator_name: MutationCalculatorName
) -> RatioResult:
    """Calculate the mutation analysis results."""
    return _MUTATION_CALCULATORS[mutation_calculator_name](target, config)


_MUTATION_CALCULATORS: Mapping[
    MutationCalculatorName, Callable[[Target, Config], RatioResult]
] = {
    "cosmic-ray": cosmic_ray_calculator.calculate_mutation,
    "mutpy": mutpy_calculator.calculate_mutation,
}
