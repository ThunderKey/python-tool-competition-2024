"""The main CLI for the Python tool competition 2024."""

import click

from ..version import VERSION
from . import init_command, run_command


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(VERSION)
def main_cli() -> None:
    """Run the main CLI of the Python Tool Competition 2024."""


main_cli.add_command(run_command.run)
main_cli.add_command(init_command.init)
