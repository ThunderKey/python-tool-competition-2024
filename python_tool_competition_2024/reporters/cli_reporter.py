"""Reporter to render the results to the CLI."""

from rich.console import Console
from rich.table import Table

from ..results import Result, Results


def report_cli(results: Results, console: Console) -> None:
    """Render the results to the CLI."""
    table = Table()
    table.add_column("Target")
    table.add_column("Success", justify="center")
    table.add_column("Line Coverage", justify="right")
    table.add_column("Branch Coverage", justify="right")
    table.add_column("Mutation Score", justify="right")
    for result in results:
        table.add_row(*_result_to_table_row(result))

    table.add_section()
    table.add_row(
        "Total",
        str(results.generation_results.ratio),
        str(results.line_coverage.ratio),
        str(results.branch_coverage.ratio),
        str(results.mutation_analysis.ratio),
    )
    console.print(table)


def _result_to_table_row(result: Result) -> tuple[str, str, str, str, str]:
    return (
        str(result.target.relative_source),
        _get_generation_result_icon(result),
        str(result.line_coverage.ratio),
        str(result.branch_coverage.ratio),
        str(result.mutation_analysis.ratio),
    )


def _get_generation_result_icon(result: Result) -> str:
    if result.generation_results.successful == 0:
        return "[red]:heavy_multiplication_x:"
    return "[green]:heavy_check_mark:"
