"""Validation functions."""


from pathlib import Path

from python_tool_competition_2024.errors import PathNotAbsoluteError


def ensure_absolute(*paths: Path) -> None:
    """Ensure that all paths are absolute."""
    for path in paths:
        if not path.is_absolute():
            raise PathNotAbsoluteError(path)
