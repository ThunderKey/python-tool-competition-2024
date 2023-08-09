import os
import subprocess  # nosec: B404
from collections.abc import Iterator
from contextlib import contextmanager
from unittest import mock

import pytest

from python_tool_competition_2024.calculation.cli_runner import run_command
from python_tool_competition_2024.errors import CommandFailedError

from ..helpers import get_test_config

_EXAMPLE_LINES = ("Example Line 1", "Example Line 2", "Example Line 3")


@pytest.mark.parametrize("verbose", (True, False))
def test_output(capsys: pytest.CaptureFixture[str], *, verbose: bool) -> None:
    config = get_test_config(show_commands=verbose, show_failures=verbose)
    with _patch_run(exit_code=0) as run_mock:
        run_command(config, "pytest", "some", "args")

    run_mock.assert_called_once_with(
        ("pytest", "some", "args"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        cwd=config.targets_dir,
        env=os.environ | {"PYTHONPATH": "."},
    )
    if verbose:
        assert _read_output(capsys) == (
            ("Running: pytest some args", *_EXAMPLE_LINES),
            (),
        )
    else:
        assert _read_output(capsys) == ((), ())


@pytest.mark.parametrize(("verbose", "exit_code"), ((True, 1), (False, 25)))
def test_output_with_error(
    capsys: pytest.CaptureFixture[str], *, verbose: bool, exit_code: int
) -> None:
    config = get_test_config(show_commands=verbose, show_failures=verbose)
    with _patch_run(exit_code=exit_code) as run_mock, pytest.raises(
        CommandFailedError, match=r"\AThe following command failed: pytest some args\Z"
    ):
        run_command(config, "pytest", "some", "args")

    run_mock.assert_called_once_with(
        ("pytest", "some", "args"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        cwd=config.targets_dir,
        env=os.environ | {"PYTHONPATH": "."},
    )
    assert _read_output(capsys) == (
        ("Running: pytest some args", *_EXAMPLE_LINES, f"Exited with code {exit_code}"),
        (),
    )


@pytest.mark.parametrize("verbose", (True, False))
def test_invalid_command(capsys: pytest.CaptureFixture[str], *, verbose: bool) -> None:
    with _patch_run(exit_code=0) as run_mock, pytest.raises(
        ValueError, match=r"\Aunknown not in \('pytest', 'coverage'\)\Z"
    ):
        run_command(
            get_test_config(show_commands=verbose, show_failures=verbose),
            "unknown",  # type: ignore[arg-type]
            "arg1",
            "arg2",
            "arg3",
        )

    run_mock.assert_not_called()
    assert _read_output(capsys) == ((), ())


@contextmanager
def _patch_run(*, exit_code: int) -> Iterator[mock.MagicMock]:
    with mock.patch(
        "python_tool_competition_2024.calculation.cli_runner.subprocess.run"
    ) as run_mock:
        completed_process = run_mock.return_value
        completed_process.returncode = exit_code
        completed_process.stdout = os.linesep.join((*_EXAMPLE_LINES, ""))
        mock.seal(run_mock)
        yield run_mock


def _read_output(
    capsys: pytest.CaptureFixture[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    output = capsys.readouterr()
    return (tuple(output.out.splitlines()), tuple(output.err.splitlines()))
