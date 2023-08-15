import contextlib
import math
import os
from collections.abc import Iterator, Mapping
from functools import partial
from importlib.metadata import EntryPoint
from types import MappingProxyType
from typing import Final
from unittest import mock

from click.testing import CliRunner
from rich.console import Console, RenderableType

from python_tool_competition_2024.calculation.coverage_caluclator import Coverages
from python_tool_competition_2024.cli import main_cli
from python_tool_competition_2024.generators import DummyTestGenerator, TestGenerator
from python_tool_competition_2024.results import RatioResult

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
    mock_scores: bool = False,
) -> tuple[str, ...]:
    exit_code, stdout, stderr = run_cli(
        args,
        generators=generators,
        generators_called=generators_called,
        mock_scores=mock_scores,
    )
    assert (exit_code, stderr, stdout) == (0, (), mock.ANY)
    return stdout


def run_cli(
    args: tuple[str, ...],
    *,
    generators: Mapping[str, type[TestGenerator]] | None = _DEFAULT_GENERATORS,
    generators_called: bool = True,
    mock_scores: bool = False,
    stdin: tuple[str, ...] | None = None,
) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    with _cli_runner(
        generators=generators,
        generators_called=generators_called,
        mock_scores=mock_scores,
    ) as runner:
        result = runner.invoke(
            main_cli,
            args=args,
            catch_exceptions=False,
            input=os.linesep.join(stdin) if stdin else None,
        )
    return (
        result.exit_code,
        tuple(result.stdout.splitlines()),
        tuple(result.stderr.splitlines()),
    )


_create_console = partial(Console, width=_CLI_COLUMNS)


@contextlib.contextmanager
def _cli_runner(
    *,
    generators: Mapping[str, type[TestGenerator]] | None = _DEFAULT_GENERATORS,
    mock_scores: bool = False,
    generators_called: bool = True,
) -> Iterator[CliRunner]:
    with _register_generators(
        generators, generators_called=generators_called
    ), _register_mutation_scores(mock_scores=mock_scores), mock.patch(
        "python_tool_competition_2024.cli.helpers.Console"
    ) as console_mock:
        console_mock.side_effect = _create_console
        mock.seal(console_mock)
        yield CliRunner(mix_stderr=False)


def renderable_to_strs(renderable: RenderableType) -> tuple[str, ...]:
    console = _create_console()
    with console.capture() as capture:
        console.print(renderable)
    return tuple(capture.get().splitlines())


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


_MUTATION_SCORES = (
    RatioResult(100, 40),
    RatioResult(50, 1),
    RatioResult(1, 1),
    RatioResult(49, 0),
)

_COVERAGES = (
    Coverages(RatioResult(10, 5), RatioResult(15, 6)),
    Coverages(RatioResult(3, 0), RatioResult(8, 2)),
    Coverages(RatioResult(7, 7), RatioResult(12, 6)),
    Coverages(RatioResult(20, 5), RatioResult(25, 16)),
)


@contextlib.contextmanager
def _register_mutation_scores(*, mock_scores: bool) -> Iterator[None]:
    if not mock_scores:
        yield
        return
    with mock.patch(
        "python_tool_competition_2024.calculation.calculate_mutation"
    ) as calculate_mutation_mock, mock.patch(
        "python_tool_competition_2024.calculation.calculate_coverages"
    ) as calculate_coverages_mock:
        calculate_mutation_mock.side_effect = _MUTATION_SCORES
        mock.seal(calculate_mutation_mock)
        calculate_coverages_mock.side_effect = _COVERAGES
        mock.seal(calculate_coverages_mock)
        yield
        assert calculate_mutation_mock.call_args_list == [
            mock.call(mock.ANY, mock.ANY, "mutpy")
        ] * len(_MUTATION_SCORES)
        assert calculate_coverages_mock.call_args_list == [
            mock.call(mock.ANY, mock.ANY)
        ] * len(_COVERAGES)


def _to_entry_point(name: str, generator_cls: type[TestGenerator]) -> EntryPoint:
    return EntryPoint(
        name,
        f"{generator_cls.__module__}:{generator_cls.__qualname__}",
        ENTRY_POINT_GROUP,
    )
