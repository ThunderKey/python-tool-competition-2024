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
"""Calculate mutation analysis using mutpy."""

import os
import re

from ...config import Config
from ...errors import CommandFailedError
from ...results import RatioResult
from ...target_finder import Target
from ..cli_runner import run_command
from .helpers import find_matching_line


def _mutpy_line_regex(name: str) -> re.Pattern[str]:
    name = re.escape(name)
    return re.compile(
        rf"\A\s+- {name}: (?P<number>\d+) \((?P<percentage>\d+\.\d+%)\)\Z"
    )


_TOTAL_REGEX = re.compile(r"\A\s+- all: (?P<number>\d+)\Z")
_KILLED_REGEX = _mutpy_line_regex("killed")
_SURVIVED_REGEX = _mutpy_line_regex("survived")
_INCOMPETENT_REGEX = _mutpy_line_regex("incompetent")
_TIMEOUT_REGEX = _mutpy_line_regex("timeout")
_EMPTY_MODULE = "typing"


def calculate_mutation(target: Target, config: Config) -> RatioResult:
    """Calculate mutation analysis using mutpy."""
    test_module = target.test_module if target.test.exists() else _EMPTY_MODULE
    try:
        output = _run_mutpy(target, config, test_module)
    except CommandFailedError:
        if test_module == _EMPTY_MODULE:
            raise
        msg = f"Could not run mutation testing for {target.source_module}."
        if not config.show_commands:
            msg = f"{msg} Add -vv to show the console output."
        config.console.print(msg, style="red")
        output = _run_mutpy(target, config, _EMPTY_MODULE)
    lines = tuple(output.splitlines())
    total = _find_number(_TOTAL_REGEX, lines)
    killed = _find_number(_KILLED_REGEX, lines)
    survived = _find_number(_SURVIVED_REGEX, lines)
    incompetent = _find_number(_INCOMPETENT_REGEX, lines)
    timeout = _find_number(_TIMEOUT_REGEX, lines)
    ratio = RatioResult(total - incompetent, killed + timeout)
    if ratio.total - ratio.successful == survived:
        return ratio
    msg = os.linesep.join(
        (
            "The total and killed does not match the survived mutants:",
            f"  - total: {total}",
            f"  - killed: {killed}",
            f"  - survived: {survived}",
            f"  - incompetent: {incompetent}",
            f"  - timeout: {timeout}",
        )
    )
    raise RuntimeError(msg)


def _find_number(pattern: re.Pattern[str], lines: tuple[str, ...]) -> int:
    return int(find_matching_line(pattern, lines).group("number"))


def _run_mutpy(target: Target, config: Config, test_module: str) -> str:
    return run_command(
        config,
        "mut.py",
        "--target",
        str(target.source),
        "--unit-test",
        test_module,
        "--runner",
        "pytest",
        capture=True,
        show_output_on_error=False,
    )
