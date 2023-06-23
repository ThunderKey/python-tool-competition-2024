from pathlib import Path
from unittest import mock

import pytest

from python_tool_competition_2024.config import get_config
from python_tool_competition_2024.errors import PathNotAbsoluteError


def test_non_absolute_project_path() -> None:
    with mock.patch("python_tool_competition_2024.config._PROJECT_ROOT", Path(".")):
        with pytest.raises(PathNotAbsoluteError) as error_info:
            get_config("some_name")
        assert error_info.value.message == "The path must be absolute: ."
