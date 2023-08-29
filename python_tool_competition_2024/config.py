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
"""A collection of configurations for this competition."""

import dataclasses
from pathlib import Path
from typing import NewType
from urllib.parse import ParseResult, urlparse

from rich.console import Console

from .validation import ensure_absolute

GeneratorName = NewType("GeneratorName", str)


@dataclasses.dataclass(frozen=True)
class Config:
    """The configuraiton of the competition."""

    generator_name: GeneratorName
    targets_dir: Path
    results_dir: Path
    tests_dir: Path
    csv_file: Path
    coverages_dir: Path
    default_targets_url: ParseResult
    console: Console
    show_commands: bool
    show_failures: bool

    def __post_init__(self) -> None:
        """Ensure that the data is correct."""
        ensure_absolute(self.targets_dir, self.tests_dir, self.csv_file)


def get_config(  # noqa: PLR0913
    generator_name: GeneratorName,
    targets_dir: Path,
    results_dir: Path,
    console: Console,
    *,
    show_commands: bool,
    show_failures: bool,
) -> Config:
    """Generate the config from the specific generator name."""
    results_dir /= generator_name
    return Config(
        generator_name=generator_name,
        targets_dir=targets_dir,
        results_dir=results_dir,
        tests_dir=results_dir / "generated_tests",
        csv_file=results_dir / "statistics.csv",
        coverages_dir=results_dir / "coverages",
        default_targets_url=urlparse(
            "https://github.com/ThunderKey/python-tool-competition-2024/tree/main/python_tool_competition_2024/targets"
        ),
        console=console,
        show_commands=show_commands,
        show_failures=show_failures,
    )
