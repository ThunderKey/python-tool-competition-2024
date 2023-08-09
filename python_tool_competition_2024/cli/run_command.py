"""The CLI command to run the Python tool competition 2024."""

from pathlib import Path

import click

from ..calculation import calculate_results
from ..config import get_config
from ..generator_plugins import plugin_names, to_test_generator_plugin_name
from ..reporters import report
from ..target_finder import find_targets
from .helpers import create_console

_MIN_VERBOSITY_SHOW_COMMANDS = 2
_MIN_VERBOSITY_SHOW_FULL_ERRORS = 1


@click.command
@click.argument("generator_name")
@click.option(
    "-v", "--verbose", count=True, help="Enables verbose mode. Can be repeated."
)
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
    verbose: int,
    targets_dir: Path,
    results_dir: Path,
) -> None:
    """Run the tool competition with the specified generator."""
    with create_console(
        ctx, show_full_errors=verbose >= _MIN_VERBOSITY_SHOW_FULL_ERRORS
    ) as console:
        config = get_config(
            to_test_generator_plugin_name(generator_name),
            targets_dir.absolute(),
            results_dir.absolute(),
            console,
            show_commands=verbose >= _MIN_VERBOSITY_SHOW_COMMANDS,
        )
        console.rule(f"Using generator {config.generator_name}")
        targets = find_targets(config)
        results = calculate_results(targets, config)
        report(results, console, config)


def _extend_help(command: click.Command, extend_with: str) -> None:
    command.help += extend_with  # type: ignore[operator]  # noqa: V101


_extend_help(
    run,
    f"""

GENERATOR_NAME is the name of the generator to use
(detected: {", ".join(plugin_names())})
""",
)
