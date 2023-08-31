from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from python_tool_competition_2024.calculation.mutation_calculator.mutpy_calculator import (  # noqa: E501
    calculate_mutation,
)
from python_tool_competition_2024.config import Config
from python_tool_competition_2024.errors import CommandFailedError
from python_tool_competition_2024.results import RatioResult
from python_tool_competition_2024.target_finder import find_targets

from ...helpers import TARGETS_DIR, get_test_config


def test_mutpy_calculator(tmp_path: Path) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.mutpy_calculator.run_command"
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
            targets_dir=TARGETS_DIR,
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
            _mutpy_call(
                config, TARGETS_DIR / "example1.py", "generated_tests.test_example1"
            ),
            _mutpy_call(
                config, TARGETS_DIR / "example2.py", "generated_tests.test_example2"
            ),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "__init__.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "example3.py", None),
        ]


def test_mutpy_calculator_always_failing(tmp_path: Path) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.mutpy_calculator.run_command"
    ) as run_command_mock:
        run_command_mock.side_effect = _OutputCounter(fail=True)
        mock.seal(run_command_mock)
        generated_tests = tmp_path / "dummy" / "generated_tests"
        generated_tests.mkdir(parents=True)
        (generated_tests / "test_example1.py").touch()
        (generated_tests / "test_example2.py").touch()
        config = get_test_config(
            show_commands=False,
            show_failures=False,
            targets_dir=TARGETS_DIR,
            results_dir=tmp_path,
        )
        targets = find_targets(config)

        for target in targets:
            with pytest.raises(CommandFailedError):
                calculate_mutation(target, config)

        assert run_command_mock.call_args_list == [
            _mutpy_call(
                config, TARGETS_DIR / "example1.py", "generated_tests.test_example1"
            ),
            _mutpy_call(config, TARGETS_DIR / "example1.py", None),
            _mutpy_call(
                config, TARGETS_DIR / "example2.py", "generated_tests.test_example2"
            ),
            _mutpy_call(config, TARGETS_DIR / "example2.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "__init__.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "example3.py", None),
        ]


def test_mutpy_calculator_failing(tmp_path: Path) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.mutpy_calculator.run_command"
    ) as run_command_mock:
        run_command_mock.side_effect = _OutputCounter(fail_if_not_typing=True)
        mock.seal(run_command_mock)
        generated_tests = tmp_path / "dummy" / "generated_tests"
        generated_tests.mkdir(parents=True)
        (generated_tests / "test_example1.py").touch()
        (generated_tests / "test_example2.py").touch()
        config = get_test_config(
            show_commands=False,
            show_failures=False,
            targets_dir=TARGETS_DIR,
            results_dir=tmp_path,
        )
        targets = find_targets(config)

        with config.console.capture() as capture:
            assert {
                target.source_module: calculate_mutation(target, config)
                for target in targets
            } == {
                "example1": RatioResult(10, 0),
                "example2": RatioResult(11, 1),
                "sub_example": RatioResult(12, 2),
                "sub_example.example3": RatioResult(13, 3),
            }

        assert tuple(capture.get().splitlines()) == tuple(
            (
                f"Could not run mutation testing for {module}. "
                "Add -vv to show the console output."
            )
            for module in ("example1", "example2")
        )

        assert run_command_mock.call_args_list == [
            _mutpy_call(
                config, TARGETS_DIR / "example1.py", "generated_tests.test_example1"
            ),
            _mutpy_call(config, TARGETS_DIR / "example1.py", None),
            _mutpy_call(
                config, TARGETS_DIR / "example2.py", "generated_tests.test_example2"
            ),
            _mutpy_call(config, TARGETS_DIR / "example2.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "__init__.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "example3.py", None),
        ]


def test_mutpy_calculator_failing_with_output(tmp_path: Path) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.mutpy_calculator.run_command"
    ) as run_command_mock:
        run_command_mock.side_effect = _OutputCounter(fail_if_not_typing=True)
        mock.seal(run_command_mock)
        generated_tests = tmp_path / "dummy" / "generated_tests"
        generated_tests.mkdir(parents=True)
        (generated_tests / "test_example1.py").touch()
        (generated_tests / "test_example2.py").touch()
        config = get_test_config(
            show_commands=True,
            show_failures=False,
            targets_dir=TARGETS_DIR,
            results_dir=tmp_path,
        )
        targets = find_targets(config)

        with config.console.capture() as capture:
            assert {
                target.source_module: calculate_mutation(target, config)
                for target in targets
            } == {
                "example1": RatioResult(10, 0),
                "example2": RatioResult(11, 1),
                "sub_example": RatioResult(12, 2),
                "sub_example.example3": RatioResult(13, 3),
            }

        assert tuple(capture.get().splitlines()) == tuple(
            f"Could not run mutation testing for {module}."
            for module in ("example1", "example2")
        )

        assert run_command_mock.call_args_list == [
            _mutpy_call(
                config, TARGETS_DIR / "example1.py", "generated_tests.test_example1"
            ),
            _mutpy_call(config, TARGETS_DIR / "example1.py", None),
            _mutpy_call(
                config, TARGETS_DIR / "example2.py", "generated_tests.test_example2"
            ),
            _mutpy_call(config, TARGETS_DIR / "example2.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "__init__.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "example3.py", None),
        ]


def test_mutpy_calculator_failing_with_wrong_numbers(tmp_path: Path) -> None:
    with mock.patch(
        "python_tool_competition_2024.calculation.mutation_calculator.mutpy_calculator.run_command"
    ) as run_command_mock:
        run_command_mock.return_value = """
[*] Mutation score [0.21818 s]: 75.0%
   - all: 100
   - killed: 50 (50.0%)
   - survived: 20 (25.0%)
   - incompetent: 2 (0.0%)
   - timeout: 3 (0.0%)
"""
        mock.seal(run_command_mock)
        generated_tests = tmp_path / "dummy" / "generated_tests"
        generated_tests.mkdir(parents=True)
        (generated_tests / "test_example1.py").touch()
        (generated_tests / "test_example2.py").touch()
        config = get_test_config(
            show_commands=True,
            show_failures=False,
            targets_dir=TARGETS_DIR,
            results_dir=tmp_path,
        )
        targets = find_targets(config)

        for target in targets:
            with pytest.raises(RuntimeError) as error_info:
                calculate_mutation(target, config)
            assert (
                str(error_info.value)
                == """\
The total and killed does not match the survived mutants:
  - total: 100
  - killed: 50
  - survived: 20
  - incompetent: 2
  - timeout: 3\
"""
            )

        assert run_command_mock.call_args_list == [
            _mutpy_call(
                config, TARGETS_DIR / "example1.py", "generated_tests.test_example1"
            ),
            _mutpy_call(
                config, TARGETS_DIR / "example2.py", "generated_tests.test_example2"
            ),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "__init__.py", None),
            _mutpy_call(config, TARGETS_DIR / "sub_example" / "example3.py", None),
        ]


def _mutpy_call(config: Config, target: Path, unit_test: str | None) -> mock._Call:
    return mock.call(
        config,
        "mut.py",
        "--target",
        str(target),
        "--unit-test",
        "typing" if unit_test is None else unit_test,
        "--runner",
        "pytest",
        capture=True,
        show_output_on_error=False,
    )


class _OutputCounter:
    def __init__(self, *, fail: bool = False, fail_if_not_typing: bool = False) -> None:
        self._total_count = 9
        self._successful_count = -1
        self._fail = fail
        self._fail_if_not_typing = fail_if_not_typing

    def __call__(self, _config: Config, *args: str, **_kwds: object) -> str:
        if self._fail or (self._fail_if_not_typing and "typing" not in args):
            raise CommandFailedError(args)
        self._total_count += 1
        self._successful_count += 1
        return f"""
[*] Start mutation process:
   - targets: calculator
   - tests: test_calculator
[*] All tests passed:
   - test_calculator [0.00031 s]
[*] Start mutants generation and execution:
   - [#   1] AOR calculator.py:2  :
--------------------------------------------------------------------------------
 1: def mul(x, y):
~2:     return x / y
--------------------------------------------------------------------------------
[0.02944 s] killed by test_mul (test_calculator.CalculatorTest)
   - [#   2] AOR calculator.py:2  :
--------------------------------------------------------------------------------
 1: def mul(x, y):
~2:     return x // y
--------------------------------------------------------------------------------
[0.02073 s] killed by test_mul (test_calculator.CalculatorTest)
   - [#   3] AOR calculator.py:2  :
--------------------------------------------------------------------------------
 1: def mul(x, y):
~2:     return x ** y
--------------------------------------------------------------------------------
[0.01152 s] survived
   - [#   4] SDL calculator.py:2  :
--------------------------------------------------------------------------------
 1: def mul(x, y):
~2:     pass
--------------------------------------------------------------------------------
[0.01437 s] killed by test_mul (test_calculator.CalculatorTest)
[*] Mutation score [0.21818 s]: 75.0%
   - all: {self._total_count}
   - killed: {self._successful_count} (75.0%)
   - survived: {self._total_count - self._successful_count} (25.0%)
   - incompetent: 0 (0.0%)
   - timeout: 0 (0.0%)
"""
