import contextlib
import math
import os
import re
import shutil
from collections.abc import Iterator, Mapping
from importlib.metadata import EntryPoint
from pathlib import Path
from types import MappingProxyType
from typing import Final
from unittest import mock

import pytest
from click.testing import CliRunner
from rich.console import Console

from python_tool_competition_2024.cli import main_cli
from python_tool_competition_2024.generators import TestGenerator

from .example_generators import (
    FailureTestGenerator,
    LengthTestGenerator,
    StaticTestGenerator,
)

_PROJECT_ROOT = Path(__file__).parent.parent
_REAL_TARGETS_DIR = _PROJECT_ROOT / "targets"


def test_main_in_wd(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    shutil.copytree(_REAL_TARGETS_DIR, targets_dir)
    assert _run_successful_cli(("length",)) == (
        _cli_title("Using generator length"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 50.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "results" / "length"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *test_files,
        csv_file,
        wd_tmp_path / "targets" / "example1.py",
        wd_tmp_path / "targets" / "example2.py",
        wd_tmp_path / "targets" / "sub_example" / "__init__.py",
        wd_tmp_path / "targets" / "sub_example" / "example3.py",
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "total,0.5,4,2,0.0,4000,0,0.0,4000,0,0.0,4000,0",
    )
    targets = (
        targets_dir / "sub_example" / "example3.py",
        targets_dir / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


def test_main_in_wd_with_all_success(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    shutil.copytree(_REAL_TARGETS_DIR, targets_dir)
    assert _run_successful_cli(("static",)) == (
        _cli_title("Using generator static"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success  ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼──────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 100.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴──────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),  # noqa: E501
    )

    results_dir = wd_tmp_path / "results" / "static"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_example1.py",
        test_dir / "test_example2.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *test_files,
        csv_file,
        wd_tmp_path / "targets" / "example1.py",
        wd_tmp_path / "targets" / "example2.py",
        wd_tmp_path / "targets" / "sub_example" / "__init__.py",
        wd_tmp_path / "targets" / "sub_example" / "example3.py",
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "example2.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "total,1.0,4,4,0.0,4000,0,0.0,4000,0,0.0,4000,0",
    )
    targets = (
        targets_dir / "sub_example" / "example3.py",
        targets_dir / "example1.py",
        targets_dir / "example2.py",
        targets_dir / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


def test_main_in_wd_with_all_failures(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    shutil.copytree(_REAL_TARGETS_DIR, targets_dir)
    assert _run_successful_cli(("failures",)) == (
        _cli_title("Using generator failures"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✖    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 0.00 %  │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "results" / "failures"
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        csv_file,
        wd_tmp_path / "targets" / "example1.py",
        wd_tmp_path / "targets" / "example2.py",
        wd_tmp_path / "targets" / "sub_example" / "__init__.py",
        wd_tmp_path / "targets" / "sub_example" / "example3.py",
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/__init__.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/example3.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "total,0.0,4,0,0.0,4000,0,0.0,4000,0,0.0,4000,0",
    )


def test_main_with_different_targets(wd_tmp_path: Path) -> None:
    assert _run_successful_cli(("length", "--targets-dir", str(_REAL_TARGETS_DIR))) == (
        _cli_title("Using generator length"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 50.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "results" / "length"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (*test_files, csv_file)
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "total,0.5,4,2,0.0,4000,0,0.0,4000,0,0.0,4000,0",
    )
    targets = (
        _REAL_TARGETS_DIR / "sub_example" / "example3.py",
        _REAL_TARGETS_DIR / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


def test_main_with_different_targets_and_dummy(wd_tmp_path: Path) -> None:
    assert _run_successful_cli(
        ("dummy", "--targets-dir", str(_REAL_TARGETS_DIR)), generators=None
    ) == (
        _cli_title("Using generator dummy"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success  ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼──────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 100.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴──────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),  # noqa: E501
    )

    results_dir = wd_tmp_path / "results" / "dummy"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_example1.py",
        test_dir / "test_example2.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (*test_files, csv_file)
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "example2.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "total,1.0,4,4,0.0,4000,0,0.0,4000,0,0.0,4000,0",
    )
    targets = (
        _REAL_TARGETS_DIR / "sub_example" / "example3.py",
        _REAL_TARGETS_DIR / "example1.py",
        _REAL_TARGETS_DIR / "example2.py",
        _REAL_TARGETS_DIR / "sub_example" / "__init__.py",
    )
    assert {f: tuple(f.read_text().splitlines()) for f in test_files} == {
        test: (
            f"# dummy test for {target}",
            "",
            "",
            "def test_dummy() -> None:",
            "    assert True",
        )
        for test, target in zip(test_files, targets, strict=True)
    }


def test_main_with_different_targets_and_results(wd_tmp_path: Path) -> None:
    assert _run_successful_cli(
        (
            "length",
            "--targets-dir",
            str(_REAL_TARGETS_DIR),
            "--results-dir",
            "other_res",
        )
    ) == (
        _cli_title("Using generator length"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 50.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "other_res" / "length"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (*test_files, csv_file)
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "total,0.5,4,2,0.0,4000,0,0.0,4000,0,0.0,4000,0",
    )
    targets = (
        _REAL_TARGETS_DIR / "sub_example" / "example3.py",
        _REAL_TARGETS_DIR / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


@pytest.mark.parametrize("help_arg", ("-h", "--help"))
def test_main_with_help(help_arg: str) -> None:
    assert _run_successful_cli((help_arg,), generators_called=False) == (
        "Usage: main-cli [OPTIONS] GENERATOR_NAME",
        "",
        "  Run the CLI to run the tool competition.",
        "",
        "Options:",
        "  -v, --verbose            Enables verbose mode",
        "  --targets-dir DIRECTORY  The directory containing all targets.  [default:",
        "                           targets]",
        "  --results-dir DIRECTORY  The directory to store all results to.  [default:",
        "                           results]",
        "  --version                Show the version and exit.",
        "  -h, --help               Show this message and exit.",
    )


def test_main_with_version() -> None:
    assert _run_successful_cli(("--version",), generators_called=False) == (
        "main-cli, version 0.1.0",
    )


def test_main_with_unknown_generator_name() -> None:
    assert _run_cli(("missing_generator",)) == (
        1,
        (
            'The generator name "missing_generator" was not found. Available: '
            "failures, static, length",
        ),
        (),
    )


def test_main_with_invalid_generator_name() -> None:
    assert _run_cli(
        ("my generator",), generators={"my generator": LengthTestGenerator}
    ) == (
        1,
        (
            'The generator name "my generator" is invalid. '
            r"It should match \A[\w.-]+\Z",
        ),
        (),
    )


def test_main_without_any_generator() -> None:
    assert _run_cli(("my_generator",), generators={}) == (
        1,
        (
            "Could not find any available plugin for test generators. "
            f'Make sure, that it is exposed as "{_ENTRY_POINT_GROUP}"',
        ),
        (),
    )


def test_main_with_a_generator_with_a_wrong_type() -> None:
    assert _run_cli(
        ("my_generator",),
        generators={"my_generator": object},  # type: ignore[dict-item]
    ) == (
        1,
        (
            _cli_title("Using generator my_generator"),
            'Invalid plugin "my_generator": Needs to be a subclass of TestGenerator, '
            "but got: <class 'object'>",
        ),
        (),
    )


def test_main_without_targets(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    assert _run_cli(("failures",)) == (
        1,
        (
            _cli_title("Using generator failures"),
            f"Could not find any *.py files in the targets dir: {targets_dir}",
            "Please download and extract the targets from TODO",
        ),
        (),
    )


@pytest.mark.parametrize("verbose_flag", ("-v", "--verbose"))
def test_main_without_targets_verbose(wd_tmp_path: Path, verbose_flag: str) -> None:
    targets_dir = wd_tmp_path / "targets"
    exit_code, stdout, stderr = _run_cli((verbose_flag, "static"))
    assert (exit_code, stderr) == (1, ())
    assert stdout[0] == _cli_title("Using generator static")
    assert re.fullmatch(r"╭─+ Traceback \(most recent call last\) ─+╮", stdout[1])
    assert stdout[-2] == (
        "NoTargetsFoundError: "
        f"Could not find any *.py files in the targets dir: {targets_dir}"
    )
    assert stdout[-1] == "Please download and extract the targets from TODO"


_DEFAULT_GENERATORS = MappingProxyType(
    {
        "failures": FailureTestGenerator,
        "static": StaticTestGenerator,
        "length": LengthTestGenerator,
    }
)


def _run_successful_cli(
    args: tuple[str, ...],
    *,
    generators: Mapping[str, type[TestGenerator]] | None = _DEFAULT_GENERATORS,
    generators_called: bool = True,
) -> tuple[str, ...]:
    exit_code, stdout, stderr = _run_cli(
        args, generators=generators, generators_called=generators_called
    )
    assert (exit_code, stderr, stdout) == (0, (), mock.ANY)
    return stdout


def _run_cli(
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


_CLI_COLUMNS: Final = 200


@contextlib.contextmanager
def _cli_runner(
    generators: Mapping[str, type[TestGenerator]] | None = _DEFAULT_GENERATORS,
    *,
    generators_called: bool = True,
) -> Iterator[CliRunner]:
    with _register_generators(
        generators, generators_called=generators_called
    ), mock.patch("python_tool_competition_2024.cli.get_console") as get_console_mock:
        get_console_mock.return_value = Console(width=_CLI_COLUMNS)
        mock.seal(get_console_mock)
        yield CliRunner(mix_stderr=False)


def _cli_title(content: str) -> str:
    dashes = (_CLI_COLUMNS - len(content) - 2) / 2
    return f"{'─' * math.floor(dashes)} {content} {'─' * math.ceil(dashes)}"


def _find_files(directory: Path) -> tuple[Path, ...]:
    return tuple(sorted(p for p in directory.glob("**/*") if p.is_file()))


_ENTRY_POINT_GROUP = "python_tool_competition_2024.test_generators"


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
            entry_points_mock.assert_called_once_with(group=_ENTRY_POINT_GROUP)
        else:
            entry_points_mock.assert_not_called()


def _to_entry_point(name: str, generator_cls: type[TestGenerator]) -> EntryPoint:
    return EntryPoint(
        name,
        f"{generator_cls.__module__}:{generator_cls.__qualname__}",
        _ENTRY_POINT_GROUP,
    )


def _dummy_body(target_file: Path) -> str:
    return os.linesep.join(
        (
            f"# dummy test for {target_file}",
            "",
            "",
            "def test_dummy() -> None:",
            "    assert True",
        )
    )
