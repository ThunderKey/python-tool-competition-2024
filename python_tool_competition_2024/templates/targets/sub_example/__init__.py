"""The sub example pacakge."""

from __future__ import annotations


def helper(text: str) -> str | None:
    """Add an exclamation mark if the text is not empty, `None` otherwise."""
    if text:
        return text + "!"
    return None
