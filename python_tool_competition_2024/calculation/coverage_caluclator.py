"""Calculator to gather line and branch coverage results."""

import abc
import re
from pathlib import Path
from typing import NamedTuple

# only used for type checking
from xml.etree.ElementTree import Element  # nosec B405

from defusedxml import ElementTree

from ..calculation.cli_runner import run_command
from ..config import Config
from ..errors import ConditionCoverageError, TargetNotFoundInCoveragesError
from ..results import RatioResult
from ..target_finder import Target


class Coverages(NamedTuple):
    """A named tuple of line and branch coverages."""

    line: RatioResult
    branch: RatioResult


def calculate_coverages(target: Target, config: Config) -> Coverages:
    """Calculate the line coverage results."""
    coverage_xml = _generate_coverage_xml(target, config)
    return _parse_coverage_xml(coverage_xml, target)


def _generate_coverage_xml(target: Target, config: Config) -> Path:
    coverage_xml = config.coverages_dir / f"{target.source_module}.xml"
    coverage_xml.unlink(missing_ok=True)
    if target.test.exists():
        run_command(
            config,
            "pytest",
            str(target.test),
            f"--cov={target.source_module}",
            "--cov-branch",
            "--cov-report",
            f"xml:{coverage_xml}",
            "--color=yes",
            # reset options that are not desired
            "--cov-fail-under=0",
            "--override-ini=addopts=",
            "--override-ini=cache_dir=.pytest_competition_cache",
        )

    # if the test was not generated or it does not import the source
    if not coverage_xml.exists():
        run_command(
            config,
            "coverage",
            "run",
            "--branch",
            f"--source={config.targets_dir}",
            "-m",
            "typing",
        )
        run_command(
            config, "coverage", "xml", "-o", str(coverage_xml), str(target.source)
        )
    return coverage_xml


_CONDITION_COVERAGE_REGEX = re.compile(r"\A\d+% \((?P<covered>\d+)/(?P<total>\d+)\)\Z")


class _CoverageVisitor(abc.ABC):
    def __init__(self) -> None:
        self._total = 0
        self._covered = 0

    def visit_file(self, file: Element) -> None:
        for line in file.iter("line"):
            self.visit_line(line)

    @abc.abstractmethod
    def visit_line(self, line: Element) -> None:
        """Visit the current line."""
        raise NotImplementedError

    def get_coverages(self) -> RatioResult:
        return RatioResult(self._total, self._covered)


class _LineCoverageVisitor(_CoverageVisitor):
    def visit_line(self, line: Element) -> None:
        self._total += 1
        if line.attrib["hits"] != "0":
            self._covered += 1


class _BranchCoverageVisitor(_CoverageVisitor):
    def visit_line(self, line: Element) -> None:
        condition_coverage = line.attrib.get("condition-coverage")
        if condition_coverage is None:
            return

        match = _CONDITION_COVERAGE_REGEX.match(condition_coverage)
        if match is None:
            raise ConditionCoverageError(condition_coverage)

        total_branches = int(match["total"])
        covered_branches = int(match["covered"])
        self._total += total_branches
        self._covered += covered_branches


def _parse_coverage_xml(coverage_xml: Path, target: Target) -> Coverages:
    coverage = ElementTree.parse(coverage_xml).getroot()
    line_visitor = _LineCoverageVisitor()
    branch_visitor = _BranchCoverageVisitor()
    file_found = False
    for file in coverage.iter("class"):
        if Path(file.attrib["filename"]) != target.source:
            continue
        line_visitor.visit_file(file)
        branch_visitor.visit_file(file)
        file_found = True
    if not file_found:
        raise TargetNotFoundInCoveragesError(coverage_xml, target.source)
    return Coverages(
        line=line_visitor.get_coverages(), branch=branch_visitor.get_coverages()
    )
