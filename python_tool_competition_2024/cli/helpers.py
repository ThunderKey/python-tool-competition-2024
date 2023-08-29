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
"""The main CLI for the Python tool competition 2024."""

import sys
from collections.abc import Iterator
from contextlib import contextmanager

import click
from rich.console import Console

from ..errors import PythonToolCompetitionError


@contextmanager
def create_console(ctx: click.Context, *, show_full_errors: bool) -> Iterator[Console]:
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
        if show_full_errors:
            console.print_exception()
        else:
            console.print(error.message, style="red")
        ctx.exit(1)
