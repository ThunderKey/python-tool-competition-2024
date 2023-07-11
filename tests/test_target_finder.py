from pathlib import Path
from typing import cast

import pytest
from rich import get_console

from python_tool_competition_2024.config import GeneratorName, get_config
from python_tool_competition_2024.target_finder import Target, find_targets


@pytest.mark.parametrize(
    "generator_name",
    (cast(GeneratorName, "some_example"), cast(GeneratorName, "other_test")),
)
def test_find_targets(generator_name: GeneratorName) -> None:
    project_root = Path.cwd()
    targets = project_root / "targets"
    results = project_root / "results"
    tests = results / generator_name / "generated_tests"
    config = get_config(generator_name, targets, results, get_console(), verbose=False)
    assert find_targets(config) == (
        Target(
            source=targets / "example1.py",
            relative_source=Path("example1.py"),
            source_module="example1",
            test=tests / "test_example1.py",
        ),
        Target(
            source=targets / "example2.py",
            relative_source=Path("example2.py"),
            source_module="example2",
            test=tests / "test_example2.py",
        ),
        Target(
            source=targets / "sub_example" / "__init__.py",
            relative_source=Path("sub_example", "__init__.py"),
            source_module="sub_example",
            test=tests / "test_sub_example.py",
        ),
        Target(
            source=targets / "sub_example" / "example3.py",
            relative_source=Path("sub_example", "example3.py"),
            source_module="sub_example.example3",
            test=tests / "sub_example" / "test_example3.py",
        ),
    )
