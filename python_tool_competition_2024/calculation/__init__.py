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
"""Calculation functions for generating results."""


import shutil

from ..config import Config
from ..results import Result, Results, get_result, get_results
from ..target_finder import Target
from .coverage_caluclator import calculate_coverages
from .generation_results_calculator import calculate_generation_result
from .mutation_calculator import MutationCalculatorName, calculate_mutation


def calculate_results(
    targets: tuple[Target, ...],
    config: Config,
    mutation_calculator_name: MutationCalculatorName,
) -> Results:
    """Calculate the results for all targets."""
    if config.results_dir.exists():
        shutil.rmtree(config.results_dir)
    config.results_dir.mkdir(parents=True)
    return get_results(
        _calculate_result(target, config, mutation_calculator_name)
        for target in targets
    )


def _calculate_result(
    target: Target, config: Config, mutation_calculator_name: MutationCalculatorName
) -> Result:
    generation_result = calculate_generation_result(target, config)
    coverages = calculate_coverages(target, config)
    mutation = calculate_mutation(target, config, mutation_calculator_name)
    return get_result(
        target=target,
        generation_result=generation_result,
        line_coverage=coverages.line,
        branch_coverage=coverages.branch,
        mutation_analysis=mutation,
    )
