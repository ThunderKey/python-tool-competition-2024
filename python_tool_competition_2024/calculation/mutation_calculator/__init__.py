#
# Copyright (c) 2023 Nicolas Erni.
#
# This file is part of python-tool-competition-2024
# (see https://github.com/ThunderKey/python-tool-competition-2024/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""Calculator to gather mutation analysis results."""

import enum
from collections.abc import Callable, Mapping

from ...config import Config
from ...results import RatioResult
from ...target_finder import Target
from . import cosmic_ray_calculator, mutpy_calculator


class MutationCalculatorName(enum.Enum):
    """A name of the calculator name to use."""

    MUTPY = "mutpy"
    """See: https://github.com/mutpy/mutpy"""

    COSMIC_RAY = "cosmic-ray"
    """See: https://cosmic-ray.readthedocs.io/"""


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
