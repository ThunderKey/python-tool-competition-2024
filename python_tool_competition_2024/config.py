"""A collection of configurations for this competition."""

import dataclasses
import re
from pathlib import Path
from typing import NewType, cast
from urllib.parse import ParseResult, urlparse

from .errors import InvalidGeneratorNameError
from .validation import ensure_absolute

GeneratorName = NewType("GeneratorName", str)


@dataclasses.dataclass(frozen=True)
class Config:
    """The configuraiton of the competition."""

    generator_name: GeneratorName
    targets_dir: Path
    tests_dir: Path
    csv_file: Path
    default_targets_url: ParseResult

    def __post_init__(self) -> None:
        """Ensure that the data is correct."""
        ensure_absolute(self.targets_dir, self.tests_dir, self.csv_file)


def get_config(generator_name: str, targets_dir: Path, results_dir: Path) -> Config:
    """Generate the config from the specific generator name."""
    results_dir /= generator_name
    return Config(
        generator_name=_to_generator_name(generator_name),
        targets_dir=targets_dir,
        tests_dir=results_dir / "generated_tests",
        csv_file=results_dir / "statistics.csv",
        default_targets_url=urlparse("TODO"),
    )


_GENERATOR_NAME_PATTERN = re.compile(r"\A[\w.-]+\Z")


def _to_generator_name(generator_name: str) -> GeneratorName:
    if not _GENERATOR_NAME_PATTERN.fullmatch(generator_name):
        raise InvalidGeneratorNameError(generator_name, _GENERATOR_NAME_PATTERN)
    return cast(GeneratorName, generator_name)
