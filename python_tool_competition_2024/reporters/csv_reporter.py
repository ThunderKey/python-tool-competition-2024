"""Reporter to write a CSV file."""

import csv
from pathlib import Path
from typing import Literal, TypeAlias

from ..config import Config
from ..results import RatioResults, Results


def report_csv(results: Results, config: Config) -> None:
    """Report the results as a CSV to the file configured in `Config`."""
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
