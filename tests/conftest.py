from pathlib import Path

import pytest

from python_tool_competition_2024.generator_plugins import _load_plugins

# let pytest show the assertions in tests.cli.helpers
pytest.register_assert_rewrite("tests.cli.helpers")


@pytest.fixture(autouse=True)
def _reset_caches() -> None:
    _load_plugins.cache_clear()


@pytest.fixture()
def wd_tmp_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path
