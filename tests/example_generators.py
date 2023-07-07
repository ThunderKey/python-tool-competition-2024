from pathlib import Path

from python_tool_competition_2024.generation_results import (
    FailureReason,
    TestGenerationFailure,
    TestGenerationResult,
)
from python_tool_competition_2024.generators import DummyTestGenerator, TestGenerator


class FailureTestGenerator(TestGenerator):
    def build_test(self, target_file: Path) -> TestGenerationFailure:
        return TestGenerationFailure(
            (f"Some error for file {target_file}",), FailureReason.NOTHING_GENERATED
        )


class StaticTestGenerator(DummyTestGenerator):
    def build_test(self, target_file: Path) -> TestGenerationResult:
        return super().build_test(target_file)


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
