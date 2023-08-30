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
"""Helpers for handling results."""

from __future__ import annotations

import abc
import dataclasses
from collections.abc import Callable, Iterable, Sequence
from typing import overload

from .errors import TotalSmallerThanSuccessfulError
from .generation_results import TestGenerationResult, TestGenerationSuccess
from .target_finder import Target


@dataclasses.dataclass(frozen=True)
class RatioResult:
    """A basic record of a coverage."""

    total: int
    """
    The total number of elements.

    For coverage this is the total number of branches or lines and for
    mutation analysis this is the total number of mutants.
    """

    successful: int
    """
    The successful number of elements.

    For coverage this is the covered number of branches or lines and for
    mutation analysis this is the number of killed mutants.
    """

    def __post_init__(self) -> None:
        """Verify the data of the object directly after it is created."""
        if self.total < self.successful:
            raise TotalSmallerThanSuccessfulError(self.total, self.successful)

    @property
    def ratio(self) -> float:
        """The total covarage. The value is between 0.0 and 1.0."""
        return 1.0 if self.total == 0 else self.successful / self.total

    def __add__(self, other: RatioResult) -> RatioResult:
        """Add the results together."""
        return RatioResult(
            total=self.total + other.total,
            successful=self.successful + other.successful,
        )


@dataclasses.dataclass(frozen=True)
class RatioResults(abc.ABC):
    """A collection of result ratios."""

    line_coverage: RatioResult
    """The calculated line coverages."""

    branch_coverage: RatioResult
    """The calculated branch coverages."""

    mutation_analysis: RatioResult
    """The calculated mutation analysis."""

    generation_results: RatioResult
    """The calculated test generation ratio."""


@dataclasses.dataclass(frozen=True)
class Result(RatioResults):
    """A full result for a specific target file."""

    target: Target
    """The target this result is for."""

    generation_result: TestGenerationResult
    """The test generation result for this target."""


def get_result(
    *,
    target: Target,
    generation_result: TestGenerationResult,
    line_coverage: RatioResult,
    branch_coverage: RatioResult,
    mutation_analysis: RatioResult,
) -> Result:
    """Build a result with the given results."""
    return Result(
        line_coverage=line_coverage,
        branch_coverage=branch_coverage,
        mutation_analysis=mutation_analysis,
        generation_results=RatioResult(
            1, 1 if isinstance(generation_result, TestGenerationSuccess) else 0
        ),
        target=target,
        generation_result=generation_result,
    )


@dataclasses.dataclass(frozen=True)
class Results(RatioResults, Sequence[Result]):
    """A tuple of all results for an entire run."""

    results: tuple[Result, ...]

    @overload
    def __getitem__(self, index: int) -> Result:
        return self.results[index]

    @overload
    def __getitem__(self, index: slice) -> Sequence[Result]:
        return self.results[index]

    def __getitem__(self, index: int | slice) -> Result | Sequence[Result]:
        """Get the result at the specified index or slice."""
        return self.results[index]

    def __len__(self) -> int:
        """Get the number of results."""
        return len(self.results)


def get_results(results: Iterable[Result]) -> Results:
    """Create a new instance of `Results` with the specified results."""
    all_results = tuple(results)
    return Results(
        results=all_results,
        generation_results=RatioResult(
            total=len(all_results),
            successful=sum(
                1
                for result in all_results
                if isinstance(result.generation_result, TestGenerationSuccess)
            ),
        ),
        line_coverage=_merge_ratios(lambda r: r.line_coverage, all_results),
        branch_coverage=_merge_ratios(lambda r: r.branch_coverage, all_results),
        mutation_analysis=_merge_ratios(lambda r: r.mutation_analysis, all_results),
    )


def _merge_ratios(
    getter: Callable[[Result], RatioResult], results: tuple[Result, ...]
) -> RatioResult:
    return sum(map(getter, results), RatioResult(0, 0))
