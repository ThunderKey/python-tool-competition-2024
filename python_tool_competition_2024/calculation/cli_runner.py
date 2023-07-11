"""Runs CLI commands."""

import os
import subprocess  # nosec B404
from typing import Literal, get_args

from ..config import Config
from ..errors import CommandFailedError

_COMMAND = Literal["pytest", "coverage"]
_VALID_COMMANDS = get_args(_COMMAND)


def run_command(config: Config, command: _COMMAND, *args: str) -> None:
    """
    Run a command on the command line.

    If `config` is verbose, it will print the output on the console, otherwise only if
    it was unsuccessful.

    Args:
        command: The executable to run.
        args: The arguments to pass to the executable.
        config: The configuration for this run.

    Returns:
        Whether this command was successful or not.
    """
    if config.verbose:
        _run_command(config, command, args)
        return

    try:
        with config.console.capture() as capture:
            _run_command(config, command, args)
    except CommandFailedError:
        config.console.out(capture.get(), highlight=False, end="")
        raise


def _run_command(config: Config, command: _COMMAND, args: tuple[str, ...]) -> None:
    if command not in _VALID_COMMANDS:
        msg = f"{command} not in {_VALID_COMMANDS}"
        raise ValueError(msg)
    full_command = (command, *args)
    config.console.print(f"Running: {' '.join(full_command)}")
    result = subprocess.run(
        full_command,  # noqa: S603
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        cwd=config.targets_dir,
        env=os.environ | {"PYTHONPATH": "."},
    )
    config.console.out(result.stdout, highlight=False, end="")
    if result.returncode == 0:
        return

    config.console.print(f"Exited with code {result.returncode}", style="red")
    raise CommandFailedError((command, *args))
