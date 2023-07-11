"""A collection of all errors in this project."""

import abc
import os
from pathlib import Path
from re import Pattern
from urllib.parse import ParseResult


class PythonToolCompetitionError(RuntimeError, abc.ABC):
    """Base error for all errors raised in this project."""

    def __init__(self, message: str) -> None:
        self._message = message
        super().__init__(message)

    @property
    def message(self) -> str:
        """The printable lmessage of this error."""
        return self._message


class NoTargetsFoundError(PythonToolCompetitionError):
    """Raised if no target files could be found."""

    def __init__(self, targets_dir: Path, targets_url: ParseResult) -> None:
        url = targets_url.geturl()
        super().__init__(
            os.linesep.join(
                (
                    f"Could not find any *.py files in the targets dir: {targets_dir}",
                    f"Please download and extract the targets from {url}",
                )
            )
        )


class TotalSmallerThanSuccessfulError(PythonToolCompetitionError):
    """Raised if the total is smaller than the successful items."""

    def __init__(self, total: int, successful: int) -> None:
        super().__init__(
            "The total cannot be smaller than the successful items. "
            f"{total} < {successful}"
        )


class PathNotAbsoluteError(PythonToolCompetitionError):
    """Raised if a path is not absolute."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"The path must be absolute: {path}")


class InvalidGeneratorNameError(PythonToolCompetitionError):
    """Raised if the generator name is not valid."""

    def __init__(self, name: str, regex: Pattern[str]) -> None:
        super().__init__(
            f'The generator name "{name}" is invalid. It should match {regex.pattern}'
        )


class GeneratorNotFoundError(PythonToolCompetitionError):
    """Raised if the generator name is not valid."""

    def __init__(self, name: str, available_names: tuple[str, ...]) -> None:
        available = ", ".join(available_names)
        super().__init__(
            f'The generator name "{name}" was not found. Available: {available}'
        )


class GeneratorTypeError(PythonToolCompetitionError):
    """Raised if a plugin does not inherit from TestGenerator."""

    def __init__(self, plugin_name: str, test_generator_cls: type[object]) -> None:
        super().__init__(
            f'Invalid plugin "{plugin_name}": '
            "Needs to be a subclass of TestGenerator, "
            f"but got: {test_generator_cls}"
        )


class NoGeneratorFoundError(PythonToolCompetitionError):
    """Raised if no plugin was defined."""

    def __init__(self, entry_point_group_name: str) -> None:
        super().__init__(
            "Could not find any available plugin for test generators. "
            f'Make sure, that it is exposed as "{entry_point_group_name}"'
        )


class CommandFailedError(PythonToolCompetitionError):
    """Raised if a CLI command execution failed."""

    def __init__(self, cmd: tuple[str, ...]) -> None:
        super().__init__(f"The following command failed: {' '.join(cmd)}")


class ConditionCoverageError(PythonToolCompetitionError):
    """Raised if the condition coverage is invalid."""

    def __init__(self, condition_coverage: str) -> None:
        super().__init__(f"Invalid condition coverage: {condition_coverage}")


class TargetNotFoundInCoveragesError(PythonToolCompetitionError):
    """Raised if the condition coverage is invalid."""

    def __init__(self, coverage_xml: Path, source: Path) -> None:
        super().__init__(f"Could not find {source} in {coverage_xml}")
