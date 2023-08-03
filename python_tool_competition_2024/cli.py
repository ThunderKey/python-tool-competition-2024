"""The main CLI for the Python tool competition 2024."""

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import click
from rich.console import Console

from .calculation import calculate_results
from .config import get_config
from .errors import PythonToolCompetitionError
from .generator_plugins import to_test_generator_plugin_name
from .reporters import report
from .target_finder import find_targets
from .version import VERSION


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(VERSION)
def main_cli() -> None:
    """Run the main CLI of the Python Tool Competition 2024."""


@main_cli.command
@click.argument("generator_name")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.option(
    "--targets-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    help="The directory containing all targets.",
    default=Path("targets"),
    show_default=True,
)
@click.option(
    "--results-dir",
    type=click.Path(file_okay=False, writable=True, path_type=Path),
    help="The directory to store all results to.",
    default=Path("results"),
    show_default=True,
)
@click.pass_context
def run(
    ctx: click.Context,
    *,
    generator_name: str,
    verbose: bool,
    targets_dir: Path,
    results_dir: Path,
) -> None:
    """Run the tool competition with the specified generator."""
    with _create_console(ctx, verbose=verbose) as console:
        config = get_config(
            to_test_generator_plugin_name(generator_name),
            targets_dir.absolute(),
            results_dir.absolute(),
            console,
            verbose=verbose,
        )
        console.rule(f"Using generator {config.generator_name}")
        targets = find_targets(config)
        results = calculate_results(targets, config)
        report(results, console, config)


@contextmanager
def _create_console(ctx: click.Context, *, verbose: bool) -> Iterator[Console]:
    # use the stdout explicitly to not redirect it accidentaly
    console = Console(file=sys.stdout)
    try:
        yield console
    except PythonToolCompetitionError as error:
        if verbose:
            console.print_exception()
        else:
            console.print(error.message, style="red")
        ctx.exit(1)
