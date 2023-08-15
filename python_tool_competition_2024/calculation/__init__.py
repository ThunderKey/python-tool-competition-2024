"""Calculation functions for generating results."""


import shutil

from ..config import Config
from ..results import Result, Results, get_result, get_results
from ..target_finder import Target
from .coverage_caluclator import calculate_coverages
from .generation_results_calculator import calculate_generation_result
from .mutation_calculator import MutationCalculatorName, calculate_mutation


def calculate_results(targets: tuple[Target, ...], config: Config) -> Results:
    """Calculate the results for all targets."""
    if config.results_dir.exists():
        shutil.rmtree(config.results_dir)
    config.results_dir.mkdir(parents=True)
    return get_results(_calculate_result(target, config) for target in targets)


def _calculate_result(target: Target, config: Config) -> Result:
    generation_result = calculate_generation_result(target, config)
    coverages = calculate_coverages(target, config)
    mutation = calculate_mutation(target, config, MutationCalculatorName.MUTPY)
    return get_result(
        target=target,
        generation_result=generation_result,
        line_coverage=coverages.line,
        branch_coverage=coverages.branch,
        mutation_analysis=mutation,
    )
