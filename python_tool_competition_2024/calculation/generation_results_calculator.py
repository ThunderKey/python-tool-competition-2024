"""Calculator to gather generation results."""

from pathlib import Path

from click import Abort

from ..config import Config
from ..generation_results import (
    FailureReason,
    TestGenerationFailure,
    TestGenerationResult,
    TestGenerationSuccess,
)
from ..generator_plugins import find_generator
from ..generators import FileInfo
from ..target_finder import Target


def calculate_generation_result(target: Target, config: Config) -> TestGenerationResult:
    """Calculate the mutation analysis results."""
    generator = find_generator(config.generator_name)()
    try:
        result = generator.build_test(_target_to_file_info(target, config))
    except (Abort, KeyboardInterrupt):
        raise
    except Exception as exception:  # noqa: BLE001
        result = TestGenerationFailure(
            ("An unexpected error occured:", exception), FailureReason.UNEXPECTED_ERROR
        )
    if isinstance(result, TestGenerationFailure) and config.show_failures:
        config.console.print(f"Target {target.source} failed with {result.reason}")
        for line in result.error_lines:
            config.console.print("-", line)
    if isinstance(result, TestGenerationSuccess):
        _create_packages(target.test.parent)
        target.test.write_text(result.body, encoding="utf-8")
    return result


def _target_to_file_info(target: Target, config: Config) -> FileInfo:
    return FileInfo(
        absolute_path=target.source, module_name=target.source_module, config=config
    )


def _create_packages(path: Path) -> None:
    if path.exists():
        return
    _create_packages(path.parent)
    path.mkdir()
    (path / "__init__.py").touch()
