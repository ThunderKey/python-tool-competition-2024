"""Basic helpers for mutation calculators."""

import re


def find_matching_line(
    pattern: re.Pattern[str], lines: tuple[str, ...]
) -> re.Match[str]:
    """Find the first line the fully matches the regex."""
    for line in lines:
        match = pattern.fullmatch(line)
        if match is not None:
            return match
    msg = f"No match for {pattern.pattern!r} found in {lines}"
    raise RuntimeError(msg)
