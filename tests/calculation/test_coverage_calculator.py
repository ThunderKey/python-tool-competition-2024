import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from unittest import mock

import pytest

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

from ..helpers import get_test_config


def test_with_broken_condition_coverage(tmp_path: Path) -> None:
    def test(action: Callable[[], Coverages]) -> None:
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
    def test(action: Callable[[], Coverages]) -> None:
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
    test: Callable[[Callable[[], Coverages]], None],
) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.cli_runner.subprocess.run"
    ) as run_mock:
        config = get_test_config(
            show_commands=False, show_failures=False, root_dir=tmp_path
        )
        _write_coverage_xml_in_mock(run_mock, xml_creator(config))
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
            ),
        )
        target = targets[0]
        target.test.touch()
        test(lambda: calculate_coverages(target, config))
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
            env=os.environ
            | {
                "PYTHONPATH": os.pathsep.join(
                    (str(config.targets_dir), str(config.results_dir))
                )
            },
        )


def _write_coverage_xml_in_mock(run_mock: mock.MagicMock, content: str) -> None:
    def _write(
        cmd: tuple[str, ...], **_kwargs: bool | str
    ) -> subprocess.CompletedProcess[str]:
        target = Path(cmd[cmd.index("--cov-report") + 1].removeprefix("xml:"))
        target.parent.mkdir(parents=True)
        target.write_text(content, encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "some output")

    run_mock.side_effect = _write
