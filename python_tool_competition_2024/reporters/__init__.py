"""Reporters to render the results."""

from rich.console import Console

from ..config import Config
from ..results import Results
from .cli_reporter import report_cli
from .csv_reporter import report_csv


def report(results: Results, console: Console, config: Config) -> None:
    """Report the results to the CLI and a CSV file."""
    report_cli(results, console)
    report_csv(results, config)
