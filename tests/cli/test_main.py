from collections.abc import Iterator
from pathlib import Path

import pytest

from .helpers import run_successful_cli


@pytest.mark.parametrize("help_arg", ("-h", "--help"))
def test_main_with_help(help_arg: str) -> None:
    assert run_successful_cli((help_arg,), generators_called=False) == (
        "Usage: main-cli [OPTIONS] COMMAND [ARGS]...",
        "",
        "  Run the main CLI of the Python Tool Competition 2024.",
        "",
        "Options:",
        "  --version   Show the version and exit.",
        "  -h, --help  Show this message and exit.",
        "",
        "Commands:",
        "  init  Interactively initialize a new project for a generator.",
        "  run   Run the tool competition with the specified generator.",
    )


def test_main_with_version() -> None:
    assert run_successful_cli(("--version",), generators_called=False) == (
        "main-cli, version 0.1.1",
    )


def _each_file(directory: Path) -> Iterator[Path]:
    for item in directory.iterdir():
        if item.is_file():
            yield item
        elif item.name not in (".pytest_competition_cache", "__pycache__"):
            yield from _each_file(item)
