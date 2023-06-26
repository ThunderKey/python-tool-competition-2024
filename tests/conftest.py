from pathlib import Path

import pytest


@pytest.fixture()
def wd_tmp_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path
