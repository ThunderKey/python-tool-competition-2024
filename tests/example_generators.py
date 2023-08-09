from pathlib import Path

from python_tool_competition_2024.generation_results import (
    FailureReason,
    TestGenerationFailure,
    TestGenerationResult,
    TestGenerationSuccess,
)
from python_tool_competition_2024.generators import DummyTestGenerator, TestGenerator

from .helpers import TARGETS_DIR


class FailureTestGenerator(TestGenerator):
    def build_test(self, target_file: Path) -> TestGenerationFailure:
        return TestGenerationFailure(
            (f"Some error for file {target_file}",), FailureReason.NOTHING_GENERATED
        )


_REAL_TESTS = {
    TARGETS_DIR
    / "example1.py": """
import example1

def test_some_method() -> None:
    assert example1.some_method(5) == "25"
""",
    TARGETS_DIR / "example2.py": None,
    TARGETS_DIR / "sub_example" / "__init__.py": None,
    TARGETS_DIR
    / "sub_example"
    / "example3.py": """
from sub_example.example3 import example

def test_example() -> None:
    assert example("mytest") == "Got: mytest!"
""",
}


def get_static_body(target_file: Path) -> str:
    body = _REAL_TESTS[target_file]
    assert body is not None
    return body


class StaticTestGenerator(TestGenerator):
    def build_test(self, target_file: Path) -> TestGenerationResult:
        body = _REAL_TESTS[target_file]
        if body is None:
            return TestGenerationFailure(
                (f"Some error for file {target_file}",), FailureReason.NOTHING_GENERATED
            )
        return TestGenerationSuccess(body)


class LengthTestGenerator(DummyTestGenerator):
    def build_test(self, target_file: Path) -> TestGenerationResult:
        project_root = next(
            parent for parent in target_file.parents if parent.name == "targets"
        ).parent
        if len(target_file.relative_to(project_root).parts) % 2 == 0:
            return TestGenerationFailure(
                ("Not implemented...",), FailureReason.UNEXPECTED_ERROR
            )
        return super().build_test(target_file)
