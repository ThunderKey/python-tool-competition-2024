"""Finds target files."""

import dataclasses
from pathlib import Path

from .config import Config
from .errors import NoTargetsFoundError
from .validation import ensure_absolute


@dataclasses.dataclass(frozen=True)
class Target:
    """Object representing a target file and its test file."""

    source: Path
    """The aboluste source file of this target."""

    relative_source: Path
    """The relative source file of this target."""

    test: Path
    """The absolute test file to generate for this target."""

    def __post_init__(self) -> None:
        """Ensure that the target is absolute."""
        ensure_absolute(self.source, self.test)


def find_targets(config: Config) -> tuple[Target, ...]:
    """Gather all targets from the `targets` dir."""
    targets = tuple(
        _find_target(source, config)
        for source in sorted(config.targets_dir.glob("**/*.py"))
    )
    if not targets:
        raise NoTargetsFoundError(config.targets_dir, config.default_targets_url)
    return targets


def _find_target(source: Path, config: Config) -> Target:
    test = _to_test_file(source, config)
    return Target(
        source=source, relative_source=source.relative_to(config.targets_dir), test=test
    )


def _to_test_file(source: Path, config: Config) -> Path:
    relative_path = source.relative_to(config.targets_dir)
    if relative_path.name == "__init__.py":
        relative_path = relative_path.parent
    name = f"test_{relative_path.stem}.py"
    return config.tests_dir / relative_path.parent / name
