"""Base classes and helpers for the generators."""


import abc
from pathlib import Path

from .generation_results import TestGenerationResult


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
