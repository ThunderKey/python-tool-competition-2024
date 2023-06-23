import contextlib
import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Final
from unittest import mock

from click.testing import CliRunner
from rich.console import Console

from python_tool_competition_2024.cli import main_cli

_PROJECT_ROOT = Path(__file__).parent.parent
_REAL_TARGETS_DIR = _PROJECT_ROOT / "targets"


def test_main(tmp_path: Path) -> None:
    with mock.patch("python_tool_competition_2024.config._PROJECT_ROOT", tmp_path):
        shutil.copytree(_REAL_TARGETS_DIR, tmp_path / "targets")
        assert _run_successful_cli(("some_generator",), tmp_path) == (
            _cli_title("Using generator some_generator"),
            *"""\
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target              ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ targets/example1.py │    ✖    │           0.0 │             0.0 │            0.0 │
│ targets/example2.py │    ✖    │           0.0 │             0.0 │            0.0 │
├─────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total               │   0.0   │           0.0 │             0.0 │            0.0 │
└─────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
        )

        csv_file = tmp_path / "results" / "some_generator" / "statistics.csv"
        assert _find_files(tmp_path) == (
            csv_file,
            tmp_path / "targets" / "example1.py",
            tmp_path / "targets" / "example2.py",
        )
        assert tuple(csv_file.read_text().splitlines()) == (
            (
                "target,"
                "successful ratio,files,successful files,"
                "line coverage,lines,covered lines,"
                "branch coverage,branches,covered branches,"
                "mutation score,mutants,killed mutants"
            ),
            "targets/example1.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
            "targets/example2.py,0.0,1,0,0.0,1000,0,0.0,1000,0,0.0,1000,0",
            "total,0.0,2,0,0.0,2000,0,0.0,2000,0,0.0,2000,0",
        )


def _run_successful_cli(args: tuple[str, ...], tmp_path: Path) -> tuple[str, ...]:
    exit_code, stdout, stderr = _run_cli(args, tmp_path)
    assert (exit_code, stderr, stdout) == (0, (), mock.ANY)
    return stdout


def _run_cli(
    args: tuple[str, ...], tmp_path: Path
) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    with _cli_runner() as runner, runner.isolated_filesystem(tmp_path):
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
