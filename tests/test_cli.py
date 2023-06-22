import pytest

from python_tool_competition_2024.cli import main_cli


def test_main(capsys: pytest.CaptureFixture[str]) -> None:
    assert _run_successful_cli(capsys) == ("hello world",)


def _run_successful_cli(capsys: pytest.CaptureFixture[str]) -> tuple[str, ...]:
    exit_code, stdout, stderr = _run_cli(capsys)
    assert (exit_code, stderr) == (0, ())
    return stdout


def _run_cli(
    capsys: pytest.CaptureFixture[str],
) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    exit_code = main_cli()
    result = capsys.readouterr()
    return exit_code, tuple(result.out.splitlines()), tuple(result.err.splitlines())
