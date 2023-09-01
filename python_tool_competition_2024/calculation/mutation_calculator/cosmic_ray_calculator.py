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
"""Calculate mutation analysis using cosmic-ray."""

import re
import shlex
from pathlib import Path
from typing import NamedTuple

import toml

from ...config import Config
from ...errors import CommandFailedError
from ...results import RatioResult
from ...target_finder import Target
from ..cli_runner import run_command
from .helpers import find_matching_line


class _CosmicRayFiles(NamedTuple):
    config_file: Path
    db_file: Path
    target: Target


def calculate_mutation(target: Target, config: Config) -> RatioResult:
    """Calculate mutation analysis using cosmic-ray."""
    files = _get_files(target, config)
    _prepare_config_file(files)
    run_command(
        config, "cosmic-ray", "init", str(files.config_file), str(files.db_file)
    )
    try:
        run_command(
            config,
            "cosmic-ray",
            "baseline",
            str(files.config_file),
            show_output_on_error=False,
        )
    except CommandFailedError:
        msg = f"Could not run mutation testing for {target.source_module}."
        if not config.show_commands:
            msg = f"{msg} Add -vv to show the console output."
        config.console.print(msg, style="red")
    else:
        run_command(
            config, "cosmic-ray", "exec", str(files.config_file), str(files.db_file)
        )
    return _gather_results(files, config)


def _get_files(target: Target, config: Config) -> _CosmicRayFiles:
    cosmic_ray_dir = config.results_dir / "cosmic_ray"
    cosmic_ray_dir.mkdir(exist_ok=True)
    files = _CosmicRayFiles(
        config_file=cosmic_ray_dir / f"{target.source_module}.toml",
        db_file=cosmic_ray_dir / f"{target.source_module}.sqlite",
        target=target,
    )
    files.config_file.unlink(missing_ok=True)
    files.db_file.unlink(missing_ok=True)
    return files


def _prepare_config_file(files: _CosmicRayFiles) -> None:
    if files.target.test.exists():
        test_command = shlex.join(("pytest", "--exitfirst", str(files.target.test)))
    else:
        test_command = "echo no test"
    timeout_minutes = 5
    with files.config_file.open("w", encoding="utf-8") as fp:
        toml.dump(
            {
                "cosmic-ray": {
                    "module-path": str(files.target.source),
                    "timeout": 60 * timeout_minutes,
                    "test-command": test_command,
                    "distributor": {"name": "local"},
                }
            },
            fp,
        )


# total jobs: 222
# complete: 222 (100.00%)
# surviving mutants: 222 (100.00%)
_LINE_REGEX = re.compile(r"\Atotal jobs: (?P<number>\d+)\Z")
_COMPLETE_REGEX = re.compile(
    r"\Acomplete: (?P<number>\d+) \((?P<percentage>\d+\.\d{2}%)\)\Z"
)
_SURVIVING_REGEX = re.compile(
    r"\Asurviving mutants: (?P<number>\d+) \((?P<percentage>\d+\.\d{2}%)\)\Z"
)


def _gather_results(files: _CosmicRayFiles, config: Config) -> RatioResult:
    output = run_command(config, "cr-report", str(files.db_file), capture=True)
    lines = tuple(output.splitlines())
    total = int(find_matching_line(_LINE_REGEX, lines).group("number"))
    if len(lines) == 2:  # noqa: PLR2004
        complete = 0
        survived = total
    else:
        complete = int(find_matching_line(_COMPLETE_REGEX, lines).group("number"))
        survived = int(find_matching_line(_SURVIVING_REGEX, lines).group("number"))
    if total != complete and complete != 0 and files.target.test.exists():
        msg = (
            f"Not all tests are complete ({complete}/{total}) for "
            f"{files.target.source_module}"
        )
        raise RuntimeError(msg)
    return RatioResult(total, total - survived)
