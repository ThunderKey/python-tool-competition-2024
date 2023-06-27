"""The main CLI for the Python tool competition 2024."""

import contextlib
from collections.abc import Iterator
from pathlib import Path

import click
from rich import get_console
from rich.console import Console

from .calculation import calculate_results
from .config import get_config
from .errors import PythonToolCompetitionError
from .generator_plugins import to_test_generator_plugin_name
from .reporters import report
from .target_finder import find_targets
from .version import VERSION


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
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
@click.version_option(VERSION)
@click.pass_context
def main_cli(
    ctx: click.Context,
    *,
    generator_name: str,
    verbose: bool,
    targets_dir: Path,
    results_dir: Path,
) -> None:
    """Run the CLI to run the tool competition."""
    console = get_console()
    with _handle_errors(ctx, console, verbose=verbose):
        config = get_config(
            to_test_generator_plugin_name(generator_name),
            targets_dir.absolute(),
            results_dir.absolute(),
        )
        console.rule(f"Using generator {config.generator_name}")
        targets = find_targets(config)
        results = calculate_results(targets, config)
        report(results, console, config)


@contextlib.contextmanager
def _handle_errors(
    ctx: click.Context, console: Console, *, verbose: bool
) -> Iterator[None]:
    try:
        yield
    except PythonToolCompetitionError as error:
        if verbose:
            console.print_exception()
        else:
            console.print(error.message, style="red")
        ctx.exit(1)


__all__ = ["main_cli"]
