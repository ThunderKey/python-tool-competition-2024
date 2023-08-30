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
"""A module containing the data structures for the results of test generation."""

from __future__ import annotations

import abc
import dataclasses
import enum
from functools import total_ordering


class TestGenerationResult(abc.ABC):  # noqa: B024
    """An abstract version of a test generation result."""


@total_ordering
class FailureReason(enum.Enum):
    """A reason of why the test generation failed."""

    def __init__(self, _value: int, doc: str) -> None:
        """Create a `FailureReason` with a value and the corresponding docstring."""
        super().__init__()
        # need to set the doc manually, otherwise it is not available
        self.__doc__ = doc

    UNSUPPORTED_FEATURE_USED = (  # noqa: V107
        enum.auto(),
        "Unsupported types or language features were used.",
    )
    NOTHING_GENERATED = (  # noqa: V107
        enum.auto(),
        "The test generator could not generate anything.",
    )
    UNEXPECTED_ERROR = (  # noqa: V107
        enum.auto(),
        "An unexpected error occurred during test generation.",
    )

    def __lt__(self, other: FailureReason) -> bool:
        """Whether the other failure reason is smaller than this."""
        return self.name < other.name


# pdoc ignores the __doc__ of enum otherwise
__pdoc__ = {str(reason): reason.__doc__ for reason in FailureReason}


@dataclasses.dataclass(frozen=True)
class TestGenerationFailure(TestGenerationResult):
    """A failure result of a test generation."""

    error_lines: tuple[str | BaseException, ...]  # noqa: V107
    """The description of the failures."""

    reason: FailureReason
    """The reason of the failure."""


@dataclasses.dataclass(frozen=True)
class TestGenerationSuccess(TestGenerationResult):
    """A successful result of a test generation."""

    body: str  # noqa: V107
    """The body of the generated test."""


__all__ = [
    "FailureReason",
    "TestGenerationResult",
    "TestGenerationFailure",
    "TestGenerationSuccess",
]
