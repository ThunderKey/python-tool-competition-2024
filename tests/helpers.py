from pathlib import Path
from unittest import mock

from rich import get_console

from python_tool_competition_2024.config import Config, get_config
from python_tool_competition_2024.generator_plugins import to_test_generator_plugin_name


def sealed_mock(**kwargs: object) -> mock.MagicMock:
    magic_mock = mock.MagicMock(**kwargs)
    mock.seal(magic_mock)
    return magic_mock


def get_test_config(*, verbose: bool, root_dir: Path | None = None) -> Config:
    if root_dir is None:
        root_dir = Path.cwd() / "inexisting"
    targets = root_dir / "targets"
    results = root_dir / "results"
    console = get_console()
    return get_config(
        to_test_generator_plugin_name("dummy"),
        targets,
        results,
        console,
        verbose=verbose,
    )
