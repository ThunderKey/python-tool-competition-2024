from __future__ import annotations

import re

import pytest

from python_tool_competition_2024.calculation.mutation_calculator.helpers import (
    find_matching_line,
)


@pytest.mark.parametrize(
    ("regex", "lines", "expected_line"),
    (
        (r".*2.*", ("Line1", "Line2", "Line3"), "Line2"),
        (r"Line.*", ("Line1", "Line2", "Line3"), "Line1"),
        (r"2.*", ("Line1", "Line2", "Line3"), None),
        (r".*test.*", ("Line1", "Line2", "Line3"), None),
    ),
)
def test_find_matching_line(
    regex: str, lines: tuple[str, ...], expected_line: str | None
) -> None:
    pattern = re.compile(regex)
    if expected_line is None:
        with pytest.raises(RuntimeError) as exc_info:
            find_matching_line(pattern, lines)
        assert str(exc_info.value) == f"No match for {regex!r} found in {lines}"
    else:
        assert find_matching_line(pattern, lines).string == expected_line
