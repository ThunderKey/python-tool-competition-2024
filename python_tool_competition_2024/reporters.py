"""Reporters to render the results."""

import csv
from pathlib import Path
from typing import Literal, TypeAlias

from rich.console import Console
from rich.table import Table

from .config import Config
from .results import RatioResults, Result, Results


def report(results: Results, console: Console, config: Config) -> None:
    """Report the results to the CLI and a CSV file."""
    _report_cli(results, console)
    _report_csv(results, config)


def _report_cli(results: Results, console: Console) -> None:
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


def _report_csv(results: Results, config: Config) -> None:
    config.csv_file.parent.mkdir(exist_ok=True, parents=True)
    with config.csv_file.open("w+", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(
            (
                "target",
                "successful ratio",
                "files",
                "successful files",
                "line coverage",
                "lines",
                "covered lines",
                "branch coverage",
                "branches",
                "covered branches",
                "mutation score",
                "mutants",
                "killed mutants",
            )
        )
        writer.writerows(
            _result_to_csv_row(result.target.relative_source, result)
            for result in results
        )
        writer.writerow(_result_to_csv_row("total", results))


_CSV_ROW: TypeAlias = tuple[
    Path | Literal["total"],
    float,
    int,
    int,
    float,
    int,
    int,
    float,
    int,
    int,
    float,
    int,
    int,
]


def _result_to_csv_row(
    target: Path | Literal["total"], ratios: RatioResults
) -> _CSV_ROW:
    return (
        target,
        ratios.generation_results.ratio,
        ratios.generation_results.total,
        ratios.generation_results.successful,
        ratios.line_coverage.ratio,
        ratios.line_coverage.total,
        ratios.line_coverage.successful,
        ratios.branch_coverage.ratio,
        ratios.branch_coverage.total,
        ratios.branch_coverage.successful,
        ratios.mutation_analysis.ratio,
        ratios.mutation_analysis.total,
        ratios.mutation_analysis.successful,
    )
