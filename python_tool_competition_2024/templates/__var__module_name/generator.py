"""A test generator using $readable_name."""

from python_tool_competition_2024.generation_results import (
    TestGenerationFailure,
    TestGenerationResult,
    TestGenerationSuccess,
)
from python_tool_competition_2024.generators import FileInfo, TestGenerator


class $class_name(TestGenerator):
    """A test generator using $readable_name."""

    def build_test(self, target_file_info: FileInfo) -> TestGenerationResult:
        """
        Genereate a test for the specific target file.

        Args:
            target_file: The `FileInfo` of the file to generate a test for.

        Returns:
            Either a `TestGenerationSuccess` if it was successful, or a
            `TestGenerationFailure` otherwise.
        """
        raise NotImplementedError("Implement the test generator")
