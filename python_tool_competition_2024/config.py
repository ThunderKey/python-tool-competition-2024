"""A collection of configurations for this competition."""

import dataclasses
from pathlib import Path
from typing import NewType
from urllib.parse import ParseResult, urlparse

from rich.console import Console

from .validation import ensure_absolute

GeneratorName = NewType("GeneratorName", str)


@dataclasses.dataclass(frozen=True)
class Config:
    """The configuraiton of the competition."""

    generator_name: GeneratorName
    targets_dir: Path
    tests_dir: Path
    csv_file: Path
    coverages_dir: Path
    default_targets_url: ParseResult
    console: Console
    verbose: bool

    def __post_init__(self) -> None:
        """Ensure that the data is correct."""
        ensure_absolute(self.targets_dir, self.tests_dir, self.csv_file)


def get_config(
    generator_name: GeneratorName,
    targets_dir: Path,
    results_dir: Path,
    console: Console,
    *,
    verbose: bool,
) -> Config:
    """Generate the config from the specific generator name."""
    results_dir /= generator_name
    return Config(
        generator_name=generator_name,
        targets_dir=targets_dir,
        tests_dir=results_dir / "generated_tests",
        csv_file=results_dir / "statistics.csv",
        coverages_dir=results_dir / "coverages",
        default_targets_url=urlparse("TODO"),
        console=console,
        verbose=verbose,
    )
