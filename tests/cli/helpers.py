import contextlib
import math
from collections.abc import Iterator, Mapping
from functools import partial
from importlib.metadata import EntryPoint
from types import MappingProxyType
from typing import Final
from unittest import mock

from click.testing import CliRunner
from rich.console import Console

from python_tool_competition_2024.cli import main_cli
from python_tool_competition_2024.generators import DummyTestGenerator, TestGenerator

from ..example_generators import (
    FailureTestGenerator,
    LengthTestGenerator,
    StaticTestGenerator,
)

_CLI_COLUMNS: Final = 200


_DEFAULT_GENERATORS = MappingProxyType(
    {
        "dummy": DummyTestGenerator,
        "failures": FailureTestGenerator,
        "static": StaticTestGenerator,
        "length": LengthTestGenerator,
    }
)


def run_successful_cli(
    args: tuple[str, ...],
    *,
    generators: Mapping[str, type[TestGenerator]] | None = _DEFAULT_GENERATORS,
    generators_called: bool = True,
) -> tuple[str, ...]:
    exit_code, stdout, stderr = run_cli(
        args, generators=generators, generators_called=generators_called
    )
    assert (exit_code, stderr, stdout) == (0, (), mock.ANY)
    return stdout


def run_cli(
    args: tuple[str, ...],
    *,
    generators: Mapping[str, type[TestGenerator]] | None = _DEFAULT_GENERATORS,
    generators_called: bool = True,
) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    with _cli_runner(generators, generators_called=generators_called) as runner:
        result = runner.invoke(main_cli, args=args, catch_exceptions=False)
    return (
        result.exit_code,
        tuple(result.stdout.splitlines()),
        tuple(result.stderr.splitlines()),
    )


@contextlib.contextmanager
def _cli_runner(
    generators: Mapping[str, type[TestGenerator]] | None = _DEFAULT_GENERATORS,
    *,
    generators_called: bool = True,
) -> Iterator[CliRunner]:
    with _register_generators(
        generators, generators_called=generators_called
    ), mock.patch("python_tool_competition_2024.cli.Console") as console_mock:
        console_mock.side_effect = partial(Console, width=_CLI_COLUMNS)
        mock.seal(console_mock)
        yield CliRunner(mix_stderr=False)


def cli_title(content: str) -> str:
    dashes = (_CLI_COLUMNS - len(content) - 2) / 2
    return f"{'─' * math.floor(dashes)} {content} {'─' * math.ceil(dashes)}"


ENTRY_POINT_GROUP = "python_tool_competition_2024.test_generators"


@contextlib.contextmanager
def _register_generators(
    generators: Mapping[str, type[TestGenerator]] | None, *, generators_called: bool
) -> Iterator[None]:
    if generators is None:
        yield
        return
    with mock.patch(
        "python_tool_competition_2024.generator_plugins.entry_points"
    ) as entry_points_mock:
        entry_points_mock.return_value = tuple(
            _to_entry_point(name, generator_cls)
            for name, generator_cls in generators.items()
        )
        mock.seal(entry_points_mock)
        yield
        if generators_called:
            entry_points_mock.assert_called_once_with(group=ENTRY_POINT_GROUP)
        else:
            entry_points_mock.assert_not_called()


def _to_entry_point(name: str, generator_cls: type[TestGenerator]) -> EntryPoint:
    return EntryPoint(
        name,
        f"{generator_cls.__module__}:{generator_cls.__qualname__}",
        ENTRY_POINT_GROUP,
    )
