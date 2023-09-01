#
# Copyright (c) 2023 Nicolas Erni.
#
# This file is part of python-tool-competition-2024
# (see https://github.com/ThunderKey/python-tool-competition-2024/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""The CLI command to run the Python tool competition 2024."""

from pathlib import Path

import click

from ..calculation import calculate_results
from ..calculation.mutation_calculator import MutationCalculatorName
from ..config import get_config
from ..generator_plugins import plugin_names, to_test_generator_plugin_name
from ..reporters import report
from ..target_finder import find_targets
from .helpers import create_console

_MIN_VERBOSITY_SHOW_COMMANDS = 2
_MIN_VERBOSITY_SHOW_FAILURES = 1
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
@click.option(
    "--mutation-calculator",
    type=click.Choice(tuple(name.value for name in MutationCalculatorName)),
    help="The calculator to run mutation analysis.",
    default=MutationCalculatorName.COSMIC_RAY.value,
    show_default=True,
)
@click.pass_context
def run(  # noqa: PLR0913
    ctx: click.Context,
    *,
    generator_name: str,
    verbose: int,
    targets_dir: Path,
    results_dir: Path,
    mutation_calculator: str,
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
            show_failures=verbose >= _MIN_VERBOSITY_SHOW_FAILURES,
        )
        console.rule(f"Using generator {config.generator_name}")
        targets = find_targets(config)
        results = calculate_results(
            targets, config, MutationCalculatorName(mutation_calculator)
        )
        report(results, console, config)
        if not config.show_failures and (
            results.generation_results.total != results.generation_results.successful
        ):
            console.print("Add -v to show the failed generation results.")


def _extend_help(command: click.Command, extend_with: str) -> None:
    command.help += extend_with  # type: ignore[operator]  # noqa: V101


_extend_help(
    run,
    f"""

GENERATOR_NAME is the name of the generator to use
(detected: {", ".join(plugin_names())})
""",
)
