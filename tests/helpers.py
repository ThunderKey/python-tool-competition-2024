from pathlib import Path
from unittest import mock

from rich import get_console

from python_tool_competition_2024.config import Config, get_config
from python_tool_competition_2024.generator_plugins import to_test_generator_plugin_name

_SOURCE_DIR = Path(__file__).parent.parent / "python_tool_competition_2024"
TARGETS_DIR = _SOURCE_DIR / "targets"


def sealed_mock(**kwargs: object) -> mock.MagicMock:
    magic_mock = mock.MagicMock(**kwargs)
    mock.seal(magic_mock)
    return magic_mock


def get_test_config(
    *,
    show_commands: bool,
    show_failures: bool,
    root_dir: Path | None = None,
    targets_dir: Path | None = None,
    results_dir: Path | None = None,
) -> Config:
    if root_dir is None:
        root_dir = Path.cwd() / "inexisting"
    if targets_dir is None:
        targets_dir = root_dir / "targets"
    if results_dir is None:
        results_dir = root_dir / "results"
    console = get_console()
    return get_config(
        to_test_generator_plugin_name("dummy"),
        targets_dir,
        results_dir,
        console,
        show_commands=show_commands,
        show_failures=show_failures,
    )
