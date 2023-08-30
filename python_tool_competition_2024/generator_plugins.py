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
"""Handling of plugins."""

import re
import sys
from functools import cache
from typing import cast

from .config import GeneratorName
from .errors import (
    GeneratorNotFoundError,
    GeneratorTypeError,
    InvalidGeneratorNameError,
    NoGeneratorFoundError,
)
from .generators import TestGenerator

if sys.version_info[0:2] >= (3, 10):
    from importlib.metadata import EntryPoint, entry_points  # pragma: no cover
else:
    from importlib_metadata import EntryPoint, entry_points  # pragma: no cover

ENTRY_POINT_GROUP_NAME = "python_tool_competition_2024.test_generators"


def plugin_names() -> tuple[GeneratorName, ...]:
    """Get the list of all loaded plugins."""
    return tuple(_load_plugins().names)


def to_test_generator_plugin_name(name: str) -> GeneratorName:
    """Convert the string to a test generator plugin name."""
    plugins = _load_plugins()
    generator_name = cast(GeneratorName, name)
    if generator_name in plugins:
        return generator_name
    if not plugins:
        raise NoGeneratorFoundError(ENTRY_POINT_GROUP_NAME)
    raise GeneratorNotFoundError(name, plugin_names())


def find_generator(name: GeneratorName) -> type[TestGenerator]:
    """Find the test generator by the name form any plugin."""
    return _load_plugins()[name]


class _Plugins:
    def __init__(self, generator_entry_points: dict[GeneratorName, EntryPoint]) -> None:
        self.__entry_points = generator_entry_points
        self.__plugins: dict[GeneratorName, type[TestGenerator]] = {}
        self.__names = tuple(self.__entry_points.keys())

    @property
    def names(self) -> tuple[GeneratorName, ...]:
        return self.__names

    def __len__(self) -> int:
        return len(self.__names)

    def __contains__(self, name: GeneratorName) -> bool:
        return name in self.__names

    def __getitem__(self, name: GeneratorName) -> type[TestGenerator]:
        if name not in self.__plugins:
            entry_point = self.__entry_points.pop(name)
            test_generator_cls = entry_point.load()
            if not issubclass(test_generator_cls, TestGenerator):
                raise GeneratorTypeError(name, test_generator_cls)
            self.__plugins[name] = test_generator_cls
        return self.__plugins[name]


_GENERATOR_NAME_PATTERN = re.compile(r"\A[\w.-]+\Z")


@cache
def _load_plugins() -> _Plugins:
    plugins = {}
    for entry_point in entry_points(group=ENTRY_POINT_GROUP_NAME):
        if not _GENERATOR_NAME_PATTERN.fullmatch(entry_point.name):
            raise InvalidGeneratorNameError(entry_point.name, _GENERATOR_NAME_PATTERN)
        plugins[cast(GeneratorName, entry_point.name)] = entry_point
    return _Plugins(plugins)
