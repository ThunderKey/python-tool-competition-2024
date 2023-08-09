from pathlib import Path
from typing import cast

import pytest
from rich import get_console

from python_tool_competition_2024.config import GeneratorName, get_config
from python_tool_competition_2024.errors import PathNotAbsoluteError


@pytest.mark.parametrize(
    ("targets_dir", "results_dir", "error_dir"),
    (
        (Path("targets"), Path("results").absolute(), "targets"),
        (
            Path("targets").absolute(),
            Path("results"),
            "results/some_name/generated_tests",
        ),
    ),
)
def test_non_absolute_project_path(
    targets_dir: Path, results_dir: Path, error_dir: str
) -> None:
    generator_name = cast(GeneratorName, "some_name")
    with pytest.raises(PathNotAbsoluteError) as error_info:
        get_config(
            generator_name, targets_dir, results_dir, get_console(), show_commands=False
        )
    assert error_info.value.message == f"The path must be absolute: {error_dir}"
