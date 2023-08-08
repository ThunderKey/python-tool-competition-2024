"""Handling of plugins."""

import re
from functools import cache
from importlib.metadata import EntryPoint, entry_points
from typing import cast

from .config import GeneratorName
from .errors import (
    GeneratorNotFoundError,
    GeneratorTypeError,
    InvalidGeneratorNameError,
    NoGeneratorFoundError,
)
from .generators import TestGenerator

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
