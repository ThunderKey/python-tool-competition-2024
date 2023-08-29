#
# Copyright (c) 2023 Nicolas Erni.
#
# This file is part of python-tool-competition-2024
# (see https://github.com/ThunderKey/python-tool-competition-2024/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
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
