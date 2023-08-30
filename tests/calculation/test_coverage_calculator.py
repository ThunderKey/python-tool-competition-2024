import subprocess  # nosec B404
from collections.abc import Callable
from pathlib import Path
from unittest import mock

import pytest

from python_tool_competition_2024.calculation.cli_runner import _extend_env
from python_tool_competition_2024.calculation.coverage_caluclator import (
    Coverages,
    calculate_coverages,
)
from python_tool_competition_2024.config import Config
from python_tool_competition_2024.errors import (
    ConditionCoverageError,
    TargetNotFoundInCoveragesError,
)
from python_tool_competition_2024.target_finder import Target, find_targets

from ..cli.helpers import renderable_to_strs
from ..helpers import get_test_config


def test_with_command_failing(tmp_path: Path) -> None:
    def test(action: Callable[[], Coverages], config: Config) -> None:
        with config.console.capture() as capture:
            action()
        assert tuple(capture.get().splitlines()) == (
            "Could not run pytest for example. Add -vv to show the console output.",
        )

    _run_with_coverage_xml(tmp_path, _successful_xml_creator, test, return_code=1)


def test_with_command_failing_with_console_output(tmp_path: Path) -> None:
    def test(action: Callable[[], Coverages], config: Config) -> None:
        with config.console.capture() as capture:
            action()
        assert tuple(capture.get().splitlines()) == (
            *renderable_to_strs(
                "Running: pytest "
                f"{tmp_path}/results/dummy/generated_tests/test_example.py "
                "--cov=example --cov-branch --cov-report "
                f"xml:{tmp_path}/results/dummy/coverages/example.xml "
                "--color=yes --cov-fail-under=0 "
                "--override-ini=addopts= "
                "--override-ini=cache_dir=.pytest_competition_cache"
            ),
            "some outputExited with code 1",
            "Could not run pytest for example.",
        )

    _run_with_coverage_xml(
        tmp_path, _successful_xml_creator, test, return_code=1, show_commands=True
    )


def test_with_broken_condition_coverage(tmp_path: Path) -> None:
    def test(action: Callable[[], Coverages], _config: Config) -> None:
        with pytest.raises(
            ConditionCoverageError,
            match=r"\AInvalid condition coverage: unexpected text\Z",
        ):
            action()

    def xml_creator(config: Config) -> str:
        file = config.targets_dir / "example.py"
        return f"""<?xml version="1.0" ?>
<coverage>
    <packages>
        <package>
            <classes>
                <class line-rate="1.0" filename="{file}">
                    <lines>
                        <line hits="1" condition-coverage="unexpected text" />
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    _run_with_coverage_xml(tmp_path, xml_creator, test)


def test_with_missing_file(tmp_path: Path) -> None:
    def test(action: Callable[[], Coverages], _config: Config) -> None:
        with pytest.raises(
            TargetNotFoundInCoveragesError,
            match=r"\ACould not find [\w/\\-]+.py in [\w/\\.-]+\.xml\Z",
        ):
            action()

    def xml_creator(config: Config) -> str:
        file = config.targets_dir / "other_example.py"
        return f"""<?xml version="1.0" ?>
<coverage>
    <packages>
        <package>
            <classes>
                <class line-rate="1.0" filename="{file}">
                    <lines>
                        <line hits="1" condition-coverage="unexpected text" />
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""

    _run_with_coverage_xml(tmp_path, xml_creator, test)


def _run_with_coverage_xml(
    tmp_path: Path,
    xml_creator: Callable[[Config], str],
    test: Callable[[Callable[[], Coverages], Config], None],
    *,
    return_code: int = 0,
    show_commands: bool = False,
) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.cli_runner.subprocess.run"
    ) as run_mock:
        config = get_test_config(
            show_commands=show_commands, show_failures=False, root_dir=tmp_path
        )
        _write_coverage_xml_in_mock(run_mock, xml_creator(config), return_code)
        mock.seal(run_mock)
        config.targets_dir.mkdir()
        config.tests_dir.mkdir(parents=True)
        (config.targets_dir / "example.py").touch()
        targets = find_targets(config)
        assert targets == (
            Target(
                source=config.targets_dir / "example.py",
                relative_source=Path("example.py"),
                source_module="example",
                test=config.tests_dir / "test_example.py",
                test_module="generated_tests.test_example",
            ),
        )
        target = targets[0]
        target.test.touch()
        test(lambda: calculate_coverages(target, config), config)
        run_mock.assert_called_once_with(
            (
                "pytest",
                str(config.tests_dir / "test_example.py"),
                "--cov=example",
                "--cov-branch",
                "--cov-report",
                mock.ANY,
                "--color=yes",
                "--cov-fail-under=0",
                "--override-ini=addopts=",
                "--override-ini=cache_dir=.pytest_competition_cache",
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            cwd=config.results_dir,
            env=_extend_env(config),
        )


def _write_coverage_xml_in_mock(
    run_mock: mock.MagicMock, content: str, return_code: int
) -> None:
    def _write(
        cmd: tuple[str, ...], **_kwargs: bool | str
    ) -> subprocess.CompletedProcess[str]:
        target = Path(cmd[cmd.index("--cov-report") + 1].removeprefix("xml:"))
        target.parent.mkdir(parents=True)
        target.write_text(content, encoding="utf-8")
        return subprocess.CompletedProcess(cmd, return_code, "some output")

    run_mock.side_effect = _write


def _successful_xml_creator(config: Config) -> str:
    file = config.targets_dir / "example.py"
    return f"""<?xml version="1.0" ?>
<coverage>
    <packages>
        <package>
            <classes>
                <class line-rate="1.0" filename="{file}">
                    <lines>
                        <line hits="1" condition-coverage="50% (10/20)" />
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""
