from pathlib import Path
from unittest import mock

import pytest

from python_tool_competition_2024.calculation.mutation_calculator.cosmic_ray_calculator import (  # noqa: E501
    _gather_results,
    calculate_mutation,
)
from python_tool_competition_2024.config import Config
from python_tool_competition_2024.results import RatioResult
from python_tool_competition_2024.target_finder import find_targets

from ...helpers import TARGETS_DIR, get_test_config, sealed_mock


def test_cosmic_ray_calculator(tmp_path: Path) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.cosmic_ray_calculator.run_command"
    ) as run_command_mock:
        run_command_mock.side_effect = _OutputCounter()
        mock.seal(run_command_mock)
        generated_tests = tmp_path / "dummy" / "generated_tests"
        generated_tests.mkdir(parents=True)
        (generated_tests / "test_example1.py").touch()
        (generated_tests / "test_example2.py").touch()
        config = get_test_config(
            show_commands=False,
            show_failures=False,
            targets_dir=Path.cwd() / "targets",
            results_dir=tmp_path,
        )
        targets = find_targets(config)
        assert {
            target.source_module: calculate_mutation(target, config)
            for target in targets
        } == {
            "example1": RatioResult(10, 0),
            "example2": RatioResult(11, 1),
            "sub_example": RatioResult(12, 2),
            "sub_example.example3": RatioResult(13, 3),
        }

        assert run_command_mock.call_args_list == [
            *_cr_calls(config, "example1"),
            *_cr_calls(config, "example2"),
            *_cr_calls(config, "sub_example"),
            *_cr_calls(config, "sub_example.example3"),
        ]
        cr_path = tmp_path / "dummy" / "cosmic_ray"
        assert {
            path: path.read_text() for path in tmp_path.glob("**/*") if path.is_file()
        } == {
            cr_path
            / "example1.toml": _cr_config(
                TARGETS_DIR / "example1.py", generated_tests / "test_example1.py"
            ),
            cr_path
            / "example2.toml": _cr_config(
                TARGETS_DIR / "example2.py", generated_tests / "test_example2.py"
            ),
            cr_path
            / "sub_example.example3.toml": _cr_config(
                TARGETS_DIR / "sub_example" / "example3.py", None
            ),
            cr_path
            / "sub_example.toml": _cr_config(
                TARGETS_DIR / "sub_example" / "__init__.py", None
            ),
            tmp_path / "dummy" / "generated_tests" / "test_example1.py": "",
            tmp_path / "dummy" / "generated_tests" / "test_example2.py": "",
        }


def test_gather_results_not_started() -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.cosmic_ray_calculator.run_command"
    ) as run_command_mock:
        run_command_mock.return_value = """\
total jobs: 10
complete: 0 (0.00%)
"""
        mock.seal(run_command_mock)
        config = get_test_config(show_commands=False, show_failures=False)
        files = sealed_mock(
            db_file=Path("example db"), target=sealed_mock(test=Path("test_example"))
        )
        assert _gather_results(files, config) == RatioResult(10, 0)


def test_gather_results_not_completed() -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.cosmic_ray_calculator.run_command"
    ) as run_command_mock:
        run_command_mock.return_value = _create_report_output(10, 5, 2)
        mock.seal(run_command_mock)
        config = get_test_config(show_commands=False, show_failures=False)
        files = mock.MagicMock(db_file=Path("example db"))
        files.target.source_module = "example.module"
        files.target.test.exists.return_value = True
        mock.seal(files)
        with pytest.raises(RuntimeError) as err_info:
            _gather_results(files, config)
        assert (
            str(err_info.value)
            == "Not all tests are complete (5/10) for example.module"
        )


def _cr_calls(config: Config, target: str) -> tuple[mock._Call, ...]:
    cr_dir = config.results_dir / "cosmic_ray"
    config_file = cr_dir / f"{target}.toml"
    db_file = cr_dir / f"{target}.sqlite"
    return (
        mock.call(config, "cosmic-ray", "init", str(config_file), str(db_file)),
        mock.call(config, "cosmic-ray", "baseline", str(config_file)),
        mock.call(config, "cosmic-ray", "exec", str(config_file), str(db_file)),
        mock.call(config, "cr-report", str(db_file), capture=True),
    )


def _cr_config(target: Path, test_file: Path | None) -> str:
    if test_file is None:
        test_command = "echo no test"
    else:
        test_command = f"pytest --exitfirst {test_file}"
    return f"""\
[cosmic-ray]
module-path = "{target}"
timeout = 300
test-command = "{test_command}"

[cosmic-ray.distributor]
name = "local"
"""


class _OutputCounter:
    def __init__(self) -> None:
        self._total_count = 9
        self._successful_count = -1

    def __call__(self, _config: Config, *args: str, **_kwargs: object) -> str:
        if args[0] != "cr-report":
            return ""
        self._total_count += 1
        self._successful_count += 1
        return _create_report_output(
            self._total_count,
            self._total_count,
            self._total_count - self._successful_count,
        )


def _create_report_output(total: int, complete: int, unsuccessful: int) -> str:
    return f"""
[job-id] f168ef23dff24b75846a730858fe0111
mod.py core/NumberReplacer 0
[job-id] 929a563b613242b48dae0f2de74ad2af
mod.py core/NumberReplacer 1
total jobs: {total}
complete: {complete} (100.00%)
surviving mutants: {unsuccessful} (100.00%)
"""
