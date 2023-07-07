"""Base classes and helpers for the generators."""


import abc
import os
from pathlib import Path

from .generation_results import TestGenerationResult, TestGenerationSuccess


class TestGenerator(abc.ABC):
    """A base test generator to generate tests for specific files."""

    @abc.abstractmethod
    def build_test(self, target_file: Path) -> TestGenerationResult:  # noqa: V107
        """
        Genereate a test for the specific target file.

        Args:
            target_file: The `pathlib.Path` of the file to generate a test for.

        Returns:
            Either a `TestGenerationSuccess` if it was successful, or a
            `TestGenerationFailure` otherwise.
        """
        raise NotImplementedError


class DummyTestGenerator(TestGenerator):
    """A test generator that generates dummy tests that do nothing."""

    def build_test(self, target_file: Path) -> TestGenerationResult:
        """
        Genereate a dummy test for the specific target file.

        The test file will only contain a comment and a test with `assert True`.

        Args:
            target_file: The `pathlib.Path` of the file to generate a test for.

        Returns:
            A `TestGenerationSuccess` containing the dummy content.
        """
        return TestGenerationSuccess(
            os.linesep.join(
                (
                    f"# dummy test for {target_file}",
                    "",
                    "",
                    "def test_dummy() -> None:",
                    "    assert True",
                )
            )
        )


__all__ = ["TestGenerator", "DummyTestGenerator"]
