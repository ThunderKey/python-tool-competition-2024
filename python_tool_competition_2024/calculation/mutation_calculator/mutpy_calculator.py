"""Calculate mutation analysis using mutpy."""

import re

from ...config import Config
from ...results import RatioResult
from ...target_finder import Target
from ..cli_runner import run_command
from .helpers import find_matching_line

_TOTAL_REGEX = re.compile(r"\A\s+- all: (?P<number>\d+)\Z")
_KILLED_REGEX = re.compile(
    r"\A\s+- killed: (?P<number>\d+) \((?P<percentage>\d+\.\d+%)\)\Z"
)


def calculate_mutation(target: Target, config: Config) -> RatioResult:
    """Calculate mutation analysis using mutpy."""
    test_module = target.test_module if target.test.exists() else "typing"
    output = run_command(
        config,
        "mut.py",
        "--target",
        target.source_module,
        "--unit-test",
        test_module,
        "--runner",
        "pytest",
        capture=True,
    )
    lines = tuple(output.splitlines())
    total = int(find_matching_line(_TOTAL_REGEX, lines).group("number"))
    killed = int(find_matching_line(_KILLED_REGEX, lines).group("number"))
    return RatioResult(total, killed)
