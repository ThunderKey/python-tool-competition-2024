"""The main CLI for the Python tool competition 2024."""

import contextlib
from collections.abc import Iterator

import click
from rich import get_console
from rich.console import Console

from python_tool_competition_2024.config import get_config

from .caluclation import calculate_results
from .errors import PythonToolCompetitionError
from .reporters import report
from .target_finder import find_targets


@click.command()
@click.argument("generator_name")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.pass_context
def main_cli(ctx: click.Context, *, generator_name: str, verbose: bool) -> None:
    """Run the CLI to run the tool competition."""
    console = get_console()
    with _handle_errors(ctx, console, verbose=verbose):
        config = get_config(generator_name)
        console.rule(f"Using generator {config.generator_name}")
        targets = find_targets(config)
        results = calculate_results(targets)
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
