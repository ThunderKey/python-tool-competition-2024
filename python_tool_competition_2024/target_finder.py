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
"""Finds target files."""

import dataclasses
from pathlib import Path

from .config import Config
from .errors import NoTargetsFoundError
from .validation import ensure_absolute


@dataclasses.dataclass(frozen=True)
class Target:
    """Object representing a target file and its test file."""

    source: Path
    """The aboluste source file of this target."""

    relative_source: Path
    """The relative source file of this target."""

    source_module: str
    """The module name of the source file."""

    test: Path
    """The absolute test file to generate for this target."""

    test_module: str
    """The module name of the generated test file."""

    def __post_init__(self) -> None:
        """Ensure that the target is absolute."""
        ensure_absolute(self.source, self.test)


def find_targets(config: Config) -> tuple[Target, ...]:
    """Gather all targets from the `targets` dir."""
    targets = tuple(
        _find_target(source, config)
        for source in sorted(config.targets_dir.glob("**/*.py"))
    )
    if not targets:
        raise NoTargetsFoundError(config.targets_dir, config.default_targets_url)
    return targets


def _find_target(source: Path, config: Config) -> Target:
    test = _to_test_file(source, config)
    relative_source = source.relative_to(config.targets_dir)
    return Target(
        source=source,
        relative_source=relative_source,
        source_module=_path_to_module(relative_source),
        test=test,
        test_module=_path_to_module(test.relative_to(config.results_dir)),
    )


def _to_test_file(source: Path, config: Config) -> Path:
    relative_path = source.relative_to(config.targets_dir)
    if relative_path.name == "__init__.py":
        relative_path = relative_path.parent
    name = f"test_{relative_path.stem}.py"
    return config.tests_dir / relative_path.parent / name


def _path_to_module(path: Path) -> str:
    path = path.with_suffix("")
    if path.name == "__init__":
        path = path.parent
    return ".".join(path.parts)
