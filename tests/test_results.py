from unittest import mock

import pytest

from python_tool_competition_2024.errors import TotalSmallerThanSuccessfulError
from python_tool_competition_2024.results import RatioResult, Result, get_results
from tests.helpers import sealed_mock


@pytest.mark.parametrize(
    ("total", "successful", "expected_ratio"),
    ((100, 100, 1.0), (100, 50, 0.5), (50, 25, 0.5), (100, 25, 0.25)),
)
def test_ratio_result(total: int, successful: int, expected_ratio: float) -> None:
    result = RatioResult(total=total, successful=successful)
    assert result.total == total
    assert result.successful == successful
    assert result.ratio == expected_ratio


def test_ratio_result_too_small_total() -> None:
    with pytest.raises(TotalSmallerThanSuccessfulError) as error_info:
        RatioResult(total=100, successful=101)
    assert (
        error_info.value.message
        == "The total cannot be smaller than the successful items. 100 < 101"
    )


def test_results_wrapper() -> None:
    results_tuple = (_get_result_mock(), _get_result_mock(), _get_result_mock())
    results = get_results(results_tuple)
    assert len(results) == len(results_tuple)
    for i in range(len(results_tuple)):
        assert results[i] == results_tuple[i]
        assert results[i] != results[i - 1]


def _get_result_mock() -> Result:
    return sealed_mock(
        generation_result=mock.MagicMock(),
        line_coverage=_get_ratio_mock(),
        branch_coverage=_get_ratio_mock(),
        mutation_analysis=_get_ratio_mock(),
    )


def _get_ratio_mock() -> RatioResult:
    return sealed_mock(total=100, successful=10)
