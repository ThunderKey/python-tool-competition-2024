from pathlib import Path
from unittest import mock

from python_tool_competition_2024.calculation.mutation_calculator.mutpy_calculator import (  # noqa: E501
    calculate_mutation,
)
from python_tool_competition_2024.config import Config
from python_tool_competition_2024.results import RatioResult
from python_tool_competition_2024.target_finder import find_targets

from ...helpers import get_test_config


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
            _mutpy_call(config, "example1", "generated_tests.test_example1"),
            _mutpy_call(config, "example2", "generated_tests.test_example2"),
            _mutpy_call(config, "sub_example", None),
            _mutpy_call(config, "sub_example.example3", None),
        ]


def _mutpy_call(config: Config, target: str, unit_test: str | None) -> mock._Call:
    return mock.call(
        config,
        "mut.py",
        "--target",
        target,
        "--unit-test",
        "typing" if unit_test is None else unit_test,
        "--runner",
        "pytest",
        capture=True,
    )


class _OutputCounter:
    def __init__(self) -> None:
        self._total_count = 9
        self._successful_count = -1

    def __call__(self, *_args: object, **_kwds: object) -> str:
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
   - survived: 1 (25.0%)
   - incompetent: 0 (0.0%)
   - timeout: 0 (0.0%)
"""
