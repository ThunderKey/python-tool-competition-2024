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
"""Calculator to gather generation results."""

from pathlib import Path

from click import Abort

from ..config import Config
from ..generation_results import (
    FailureReason,
    TestGenerationFailure,
    TestGenerationResult,
    TestGenerationSuccess,
)
from ..generator_plugins import find_generator
from ..generators import FileInfo
from ..target_finder import Target


def calculate_generation_result(target: Target, config: Config) -> TestGenerationResult:
    """Calculate the mutation analysis results."""
    generator = find_generator(config.generator_name)()
    try:
        result = generator.build_test(_target_to_file_info(target, config))
    except (Abort, KeyboardInterrupt):
        raise
    except Exception as exception:  # noqa: BLE001
        result = TestGenerationFailure(
            ("An unexpected error occured:", exception), FailureReason.UNEXPECTED_ERROR
        )
    if isinstance(result, TestGenerationFailure) and config.show_failures:
        config.console.print(f"Target {target.source} failed with {result.reason}")
        for line in result.error_lines:
            config.console.print("-", line)
    if isinstance(result, TestGenerationSuccess):
        _create_packages(target.test.parent)
        target.test.write_text(result.body, encoding="utf-8")
    return result


def _target_to_file_info(target: Target, config: Config) -> FileInfo:
    return FileInfo(
        absolute_path=target.source, module_name=target.source_module, config=config
    )


def _create_packages(path: Path) -> None:
    if path.exists():
        return
    _create_packages(path.parent)
    path.mkdir()
    (path / "__init__.py").touch()
