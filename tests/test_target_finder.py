from pathlib import Path

import pytest

from python_tool_competition_2024.config import get_config
from python_tool_competition_2024.target_finder import Target, find_targets


@pytest.mark.parametrize("generator_name", ("some_example", "other_test"))
def test_find_targets(generator_name: str) -> None:
    project_root = Path.cwd()
    targets = project_root / "targets"
    tests = project_root / "results" / generator_name / "generated_tests"
    config = get_config(generator_name)
    assert find_targets(config) == (
        Target(
            source=targets / "example1.py",
            relative_source=Path("targets", "example1.py"),
            test=tests / "test_example1.py",
        ),
        Target(
            source=targets / "example2.py",
            relative_source=Path("targets", "example2.py"),
            test=tests / "test_example2.py",
        ),
        Target(
            source=targets / "sub_example" / "__init__.py",
            relative_source=Path("targets", "sub_example", "__init__.py"),
            test=tests / "test_sub_example.py",
        ),
        Target(
            source=targets / "sub_example" / "example3.py",
            relative_source=Path("targets", "sub_example", "example3.py"),
            test=tests / "sub_example" / "test_example3.py",
        ),
    )
