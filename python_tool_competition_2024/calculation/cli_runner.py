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
"""Runs CLI commands."""

from __future__ import annotations

import os
import subprocess  # nosec B404
from typing import Literal, get_args, overload

from ..config import Config
from ..errors import CommandFailedError

_COMMAND = Literal["pytest", "coverage", "cosmic-ray", "cr-report", "mut.py"]
_VALID_COMMANDS = get_args(_COMMAND)


@overload
def run_command(
    config: Config,
    command: _COMMAND,
    *args: str,
    capture: Literal[True],
    show_output_on_error: bool = ...,
) -> str:
    ...


@overload
def run_command(
    config: Config,
    command: _COMMAND,
    *args: str,
    capture: Literal[False] = ...,
    show_output_on_error: bool = ...,
) -> None:
    ...


def run_command(
    config: Config,
    command: _COMMAND,
    *args: str,
    capture: Literal[True, False] = False,
    show_output_on_error: bool = True,
) -> None | str:
    """
    Run a command on the command line.

    If `config` is verbose, it will print the output on the console, otherwise only if
    it was unsuccessful.

    Args:
        config: The configuration for this run.
        command: The executable to run.
        args: The arguments to pass to the executable.
        caputre: Whether or not to return the output.

    Returns:
        `None` if `capture` is `False`, otherwise the output.
    """
    if config.show_commands:
        output = _run_command(config, command, args)
    else:
        try:
            with config.console.capture() as console_capture:
                output = _run_command(config, command, args)
        except CommandFailedError:
            if show_output_on_error:
                config.console.out(console_capture.get(), highlight=False, end="")
            raise
    return output if capture else None


def _run_command(config: Config, command: _COMMAND, args: tuple[str, ...]) -> str:
    if command not in _VALID_COMMANDS:
        msg = f"{command} not in {_VALID_COMMANDS}"
        raise ValueError(msg)
    full_command = (command, *args)
    config.console.print(f"Running: {' '.join(full_command)}")
    result = subprocess.run(  # noqa: PLW1510
        full_command,  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        cwd=config.results_dir,
        env=_extend_env(config),
    )
    config.console.out(result.stdout, highlight=False, end="")
    if result.returncode == 0:
        return result.stdout

    config.console.print(f"Exited with code {result.returncode}", style="red")
    raise CommandFailedError((command, *args))


def _extend_env(config: Config) -> dict[str, str]:
    env = os.environ | {
        "PYTHONPATH": os.pathsep.join(
            (str(config.targets_dir), str(config.results_dir))
        )
    }
    # reset the tox env to not confuse pytest
    env.pop("TOX_ENV_DIR", None)
    return env
