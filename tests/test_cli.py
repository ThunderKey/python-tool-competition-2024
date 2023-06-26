import contextlib
import re
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Final
from unittest import mock

import pytest
from click.testing import CliRunner
from rich.console import Console

from python_tool_competition_2024.cli import main_cli

_PROJECT_ROOT = Path(__file__).parent.parent
_REAL_TARGETS_DIR = _PROJECT_ROOT / "targets"


def test_main_in_wd(wd_tmp_path: Path) -> None:
    shutil.copytree(_REAL_TARGETS_DIR, wd_tmp_path / "targets")
    assert _run_successful_cli(("some_generator",)) == (
        _cli_title("Using generator some_generator"),
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

    csv_file = wd_tmp_path / "results" / "some_generator" / "statistics.csv"
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
        "sub_example/__init__.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,1000,0,0.0,1000,0,0.0,1000,0",
        "total,0.5,4,2,0.0,4000,0,0.0,4000,0,0.0,4000,0",
    )


def test_main_with_different_targets(wd_tmp_path: Path) -> None:
    assert _run_successful_cli(
        ("some_generator", "--targets-dir", str(_REAL_TARGETS_DIR))
    ) == (
        _cli_title("Using generator some_generator"),
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

    csv_file = wd_tmp_path / "results" / "some_generator" / "statistics.csv"
    assert _find_files(wd_tmp_path) == (csv_file,)
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


def test_main_with_different_targets_and_results(wd_tmp_path: Path) -> None:
    assert _run_successful_cli(
        (
            "some_generator",
            "--targets-dir",
            str(_REAL_TARGETS_DIR),
            "--results-dir",
            "other_res",
        )
    ) == (
        _cli_title("Using generator some_generator"),
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

    csv_file = wd_tmp_path / "other_res" / "some_generator" / "statistics.csv"
    assert _find_files(wd_tmp_path) == (csv_file,)
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


@pytest.mark.parametrize("help_arg", ("-h", "--help"))
def test_main_with_help(help_arg: str) -> None:
    assert _run_successful_cli((help_arg,)) == (
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
    assert _run_successful_cli(("--version",)) == ("main-cli, version 0.1.0",)


def test_main_with_invalid_generator_name() -> None:
    assert _run_cli(("my generator",)) == (
        1,
        (
            'The generator name "my generator" is invalid. '
            r"It should match \A[\w.-]+\Z",
        ),
        (),
    )


def test_main_without_targets(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    assert _run_cli(("some-generator",)) == (
        1,
        (
            _cli_title("Using generator some-generator"),
            f"Could not find any *.py files in the targets dir: {targets_dir}",
            "Please download and extract the targets from TODO",
        ),
        (),
    )


@pytest.mark.parametrize("verbose_flag", ("-v", "--verbose"))
def test_main_without_targets_verbose(wd_tmp_path: Path, verbose_flag: str) -> None:
    targets_dir = wd_tmp_path / "targets"
    exit_code, stdout, stderr = _run_cli((verbose_flag, "my_generator"))
    assert (exit_code, stderr) == (1, ())
    assert stdout[0] == _cli_title("Using generator my_generator")
    assert re.fullmatch(r"╭─+ Traceback \(most recent call last\) ─+╮", stdout[1])
    assert stdout[-2] == (
        "NoTargetsFoundError: "
        f"Could not find any *.py files in the targets dir: {targets_dir}"
    )
    assert stdout[-1] == "Please download and extract the targets from TODO"


def _run_successful_cli(args: tuple[str, ...]) -> tuple[str, ...]:
    exit_code, stdout, stderr = _run_cli(args)
    assert (exit_code, stderr, stdout) == (0, (), mock.ANY)
    return stdout


def _run_cli(args: tuple[str, ...]) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    with _cli_runner() as runner:
        result = runner.invoke(main_cli, args=args, catch_exceptions=False)
    return (
        result.exit_code,
        tuple(result.stdout.splitlines()),
        tuple(result.stderr.splitlines()),
    )


_CLI_COLUMNS: Final = 200


@contextlib.contextmanager
def _cli_runner() -> Iterator[CliRunner]:
    with mock.patch("python_tool_competition_2024.cli.get_console") as get_console_mock:
        get_console_mock.return_value = Console(width=_CLI_COLUMNS)
        mock.seal(get_console_mock)
        yield CliRunner(mix_stderr=False)


def _cli_title(content: str) -> str:
    dashes = "─" * int((_CLI_COLUMNS - len(content) - 2) / 2)
    return f"{dashes} {content} {dashes}"


def _find_files(directory: Path) -> tuple[Path, ...]:
    return tuple(sorted(p for p in directory.glob("**/*") if p.is_file()))
