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

import click

from ..version import VERSION
from . import init_command, run_command


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(VERSION)
def main_cli() -> None:
    """Run the main CLI of the Python Tool Competition 2024."""


main_cli.add_command(run_command.run)
main_cli.add_command(init_command.init)
