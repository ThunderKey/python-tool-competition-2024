"""The main CLI for the Python tool competition 2024."""

import sys
from collections.abc import Iterator
from contextlib import contextmanager

import click
from rich.console import Console

from ..errors import PythonToolCompetitionError


@contextmanager
def create_console(ctx: click.Context, *, verbose: bool) -> Iterator[Console]:
    """
    Create a rich console and report errors.

    Args:
        verbose: If `True` show the entire exception, otherwise only the message.
    """
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
