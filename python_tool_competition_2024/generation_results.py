"""A module containing the data structures for the results of test generation."""

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

    def __lt__(self, other: "FailureReason") -> bool:
        """Whether the other failure reason is smaller than this."""
        return self.name < other.name


# pdoc ignores the __doc__ of enum otherwise
__pdoc__ = {str(reason): reason.__doc__ for reason in FailureReason}


@dataclasses.dataclass(frozen=True)
class TestGenerationFailure(TestGenerationResult):
    """A failure result of a test generation."""

    error_lines: tuple[str, ...]  # noqa: V107
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
