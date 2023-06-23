"""Calculation functions for generating results."""


from ..results import Result, Results, get_result, get_results
from ..target_finder import Target
from .coverage_caluclator import calculate_coverages
from .generation_results_calculator import calculate_generation_results
from .mutation_caluclator import calculate_mutation


def calculate_results(targets: tuple[Target, ...]) -> Results:
    """Calculate the results for all targets."""
    return get_results(map(_calculate_result, targets))


def _calculate_result(target: Target) -> Result:
    generation_result = calculate_generation_results(target)
    coverages = calculate_coverages(target)
    mutation = calculate_mutation(target)
    return get_result(
        target=target,
        generation_result=generation_result,
        line_coverage=coverages.line,
        branch_coverage=coverages.branch,
        mutation_analysis=mutation,
    )
