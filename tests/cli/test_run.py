import os
import re
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

from ..example_generators import LengthTestGenerator, get_static_body
from ..helpers import TARGETS_DIR
from .helpers import ENTRY_POINT_GROUP, cli_title, run_cli, run_successful_cli

_TARGETS_URL = (
    "https://github.com/ThunderKey/python-tool-competition-2024/tree/main/targets"
)


def test_run_in_wd(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    shutil.copytree(TARGETS_DIR, targets_dir)
    assert run_successful_cli(("run", "length", "-v")) == (
        cli_title("Using generator length"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 50.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "results" / "length"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *_coverages_files(results_dir),
        *test_files,
        csv_file,
        wd_tmp_path / "targets" / ".coverage",
        wd_tmp_path / "targets" / "example1.py",
        wd_tmp_path / "targets" / "example2.py",
        wd_tmp_path / "targets" / "sub_example" / "__init__.py",
        wd_tmp_path / "targets" / "sub_example" / "example3.py",
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,9,0,0.0,4,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,2,0,0.0,0,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,4,0,0.0,0,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,3,0,0.0,0,0,0.0,1000,0",
        "total,0.5,4,2,0.0,18,0,0.0,4,0,0.0,4000,0",
    )
    targets = (
        targets_dir / "sub_example" / "example3.py",
        targets_dir / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


def test_run_in_wd_with_all_success(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    shutil.copytree(TARGETS_DIR, targets_dir)
    assert run_successful_cli(("run", "dummy")) == (
        cli_title("Using generator dummy"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success  ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼──────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 100.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴──────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),  # noqa: E501
    )

    results_dir = wd_tmp_path / "results" / "dummy"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_example1.py",
        test_dir / "test_example2.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *_coverages_files(results_dir),
        *test_files,
        csv_file,
        wd_tmp_path / "targets" / ".coverage",
        wd_tmp_path / "targets" / "example1.py",
        wd_tmp_path / "targets" / "example2.py",
        wd_tmp_path / "targets" / "sub_example" / "__init__.py",
        wd_tmp_path / "targets" / "sub_example" / "example3.py",
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,1.0,1,1,0.0,9,0,0.0,4,0,0.0,1000,0",
        "example2.py,1.0,1,1,0.0,2,0,0.0,0,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,4,0,0.0,0,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,3,0,0.0,0,0,0.0,1000,0",
        "total,1.0,4,4,0.0,18,0,0.0,4,0,0.0,4000,0",
    )
    targets = (
        targets_dir / "sub_example" / "example3.py",
        targets_dir / "example1.py",
        targets_dir / "example2.py",
        targets_dir / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


def test_run_in_wd_with_all_failures(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    shutil.copytree(TARGETS_DIR, targets_dir)
    assert run_successful_cli(("run", "failures")) == (
        cli_title("Using generator failures"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✖    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 0.00 %  │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "results" / "failures"
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *_coverages_files(results_dir),
        csv_file,
        wd_tmp_path / "targets" / ".coverage",
        wd_tmp_path / "targets" / "example1.py",
        wd_tmp_path / "targets" / "example2.py",
        wd_tmp_path / "targets" / "sub_example" / "__init__.py",
        wd_tmp_path / "targets" / "sub_example" / "example3.py",
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,9,0,0.0,4,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,2,0,0.0,0,0,0.0,1000,0",
        "sub_example/__init__.py,0.0,1,0,0.0,4,0,0.0,2,0,0.0,1000,0",
        "sub_example/example3.py,0.0,1,0,0.0,3,0,0.0,0,0,0.0,1000,0",
        "total,0.0,4,0,0.0,18,0,0.0,6,0,0.0,4000,0",
    )


def test_run_with_different_targets(wd_tmp_path: Path) -> None:
    assert run_successful_cli(("run", "length", "--targets-dir", str(TARGETS_DIR))) == (
        cli_title("Using generator length"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 50.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "results" / "length"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *_coverages_files(results_dir),
        *test_files,
        csv_file,
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,9,0,0.0,4,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,2,0,0.0,0,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,4,0,0.0,0,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,3,0,0.0,0,0,0.0,1000,0",
        "total,0.5,4,2,0.0,18,0,0.0,4,0,0.0,4000,0",
    )
    targets = (
        TARGETS_DIR / "sub_example" / "example3.py",
        TARGETS_DIR / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


def test_run_with_real_tests(wd_tmp_path: Path) -> None:
    assert run_successful_cli(("run", "static", "--targets-dir", str(TARGETS_DIR))) == (
        cli_title("Using generator static"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✔    │       44.44 % │         25.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔    │      100.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 50.00 % │       38.89 % │         16.67 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "results" / "static"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_example1.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *_coverages_files(results_dir),
        *test_files,
        csv_file,
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,1.0,1,1,0.4444444444444444,9,4,0.25,4,1,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,2,0,0.0,0,0,0.0,1000,0",
        "sub_example/__init__.py,0.0,1,0,0.0,4,0,0.0,2,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,1.0,3,3,0.0,0,0,0.0,1000,0",
        "total,0.5,4,2,0.3888888888888889,18,7,0.16666666666666666,6,1,0.0,4000,0",
    )
    targets = (TARGETS_DIR / "sub_example" / "example3.py", TARGETS_DIR / "example1.py")
    assert {f: f.read_text() for f in test_files} == {
        test: get_static_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


def test_run_with_different_targets_and_dummy(wd_tmp_path: Path) -> None:
    assert run_successful_cli(
        ("run", "dummy", "--targets-dir", str(TARGETS_DIR)), generators=None
    ) == (
        cli_title("Using generator dummy"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success  ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔     │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼──────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 100.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴──────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),  # noqa: E501
    )

    results_dir = wd_tmp_path / "results" / "dummy"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_example1.py",
        test_dir / "test_example2.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *_coverages_files(results_dir),
        *test_files,
        csv_file,
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,1.0,1,1,0.0,9,0,0.0,4,0,0.0,1000,0",
        "example2.py,1.0,1,1,0.0,2,0,0.0,0,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,4,0,0.0,0,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,3,0,0.0,0,0,0.0,1000,0",
        "total,1.0,4,4,0.0,18,0,0.0,4,0,0.0,4000,0",
    )
    targets = (
        TARGETS_DIR / "sub_example" / "example3.py",
        TARGETS_DIR / "example1.py",
        TARGETS_DIR / "example2.py",
        TARGETS_DIR / "sub_example" / "__init__.py",
    )
    assert {f: tuple(f.read_text().splitlines()) for f in test_files} == {
        test: (
            f"# dummy test for {target}",
            "",
            "",
            "def test_dummy() -> None:",
            "    assert True",
        )
        for test, target in zip(test_files, targets, strict=True)
    }


def test_run_with_different_targets_and_results(wd_tmp_path: Path) -> None:
    assert run_successful_cli(
        (
            "run",
            "length",
            "--targets-dir",
            str(TARGETS_DIR),
            "--results-dir",
            "other_res",
        )
    ) == (
        cli_title("Using generator length"),
        *"""\
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Target                  ┃ Success ┃ Line Coverage ┃ Branch Coverage ┃ Mutation Score ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ example1.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ example2.py             │    ✖    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/__init__.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
│ sub_example/example3.py │    ✔    │        0.00 % │          0.00 % │         0.00 % │
├─────────────────────────┼─────────┼───────────────┼─────────────────┼────────────────┤
│ Total                   │ 50.00 % │        0.00 % │          0.00 % │         0.00 % │
└─────────────────────────┴─────────┴───────────────┴─────────────────┴────────────────┘
""".splitlines(),
    )

    results_dir = wd_tmp_path / "other_res" / "length"
    test_dir = results_dir / "generated_tests"
    test_files = (
        test_dir / "sub_example" / "test_example3.py",
        test_dir / "test_sub_example.py",
    )
    csv_file = results_dir / "statistics.csv"
    assert _find_files(wd_tmp_path) == (
        *_coverages_files(results_dir),
        *test_files,
        csv_file,
    )
    assert tuple(csv_file.read_text().splitlines()) == (
        (
            "target,"
            "successful ratio,files,successful files,"
            "line coverage,lines,covered lines,"
            "branch coverage,branches,covered branches,"
            "mutation score,mutants,killed mutants"
        ),
        "example1.py,0.0,1,0,0.0,9,0,0.0,4,0,0.0,1000,0",
        "example2.py,0.0,1,0,0.0,2,0,0.0,0,0,0.0,1000,0",
        "sub_example/__init__.py,1.0,1,1,0.0,4,0,0.0,0,0,0.0,1000,0",
        "sub_example/example3.py,1.0,1,1,0.0,3,0,0.0,0,0,0.0,1000,0",
        "total,0.5,4,2,0.0,18,0,0.0,4,0,0.0,4000,0",
    )
    targets = (
        TARGETS_DIR / "sub_example" / "example3.py",
        TARGETS_DIR / "sub_example" / "__init__.py",
    )
    assert {f: f.read_text() for f in test_files} == {
        test: _dummy_body(target)
        for test, target in zip(test_files, targets, strict=True)
    }


@pytest.mark.parametrize("help_arg", ("-h", "--help"))
def test_run_with_help(help_arg: str) -> None:
    assert run_successful_cli(("run", help_arg), generators_called=False) == (
        "Usage: main-cli run [OPTIONS] GENERATOR_NAME",
        "",
        "  Run the tool competition with the specified generator.",
        "",
        "  GENERATOR_NAME is the name of the generator to use (detected: dummy)",
        "",
        "Options:",
        "  -v, --verbose            Enables verbose mode. Can be repeated.",
        "  --targets-dir DIRECTORY  The directory containing all targets.  [default:",
        "                           targets]",
        "  --results-dir DIRECTORY  The directory to store all results to.  [default:",
        "                           results]",
        "  -h, --help               Show this message and exit.",
    )


def test_run_with_unknown_generator_name() -> None:
    assert run_cli(("run", "missing_generator")) == (
        1,
        (
            'The generator name "missing_generator" was not found. Available: '
            "dummy, failures, static, length",
        ),
        (),
    )


def test_run_with_invalid_generator_name() -> None:
    assert run_cli(
        ("run", "my generator"), generators={"my generator": LengthTestGenerator}
    ) == (
        1,
        (
            'The generator name "my generator" is invalid. '
            r"It should match \A[\w.-]+\Z",
        ),
        (),
    )


def test_run_without_any_generator() -> None:
    assert run_cli(("run", "my_generator"), generators={}) == (
        1,
        (
            "Could not find any available plugin for test generators. "
            f'Make sure, that it is exposed as "{ENTRY_POINT_GROUP}"',
        ),
        (),
    )


def test_run_with_a_generator_with_a_wrong_type() -> None:
    assert run_cli(
        ("run", "my_generator"),
        generators={"my_generator": object},  # type: ignore[dict-item]
    ) == (
        1,
        (
            cli_title("Using generator my_generator"),
            'Invalid plugin "my_generator": Needs to be a subclass of TestGenerator, '
            "but got: <class 'object'>",
        ),
        (),
    )


def test_run_without_targets(wd_tmp_path: Path) -> None:
    targets_dir = wd_tmp_path / "targets"
    assert run_cli(("run", "failures")) == (
        1,
        (
            cli_title("Using generator failures"),
            f"Could not find any *.py files in the targets dir: {targets_dir}",
            f"Please download the targets from {_TARGETS_URL}",
        ),
        (),
    )


@pytest.mark.parametrize("verbose_flag", ("-v", "--verbose"))
def test_run_without_targets_verbose(wd_tmp_path: Path, verbose_flag: str) -> None:
    targets_dir = wd_tmp_path / "targets"
    exit_code, stdout, stderr = run_cli(("run", verbose_flag, "dummy"))
    assert (exit_code, stderr) == (1, ())
    assert stdout[0] == cli_title("Using generator dummy")
    assert re.fullmatch(r"╭─+ Traceback \(most recent call last\) ─+╮", stdout[1])
    assert stdout[-2] == (
        "NoTargetsFoundError: "
        f"Could not find any *.py files in the targets dir: {targets_dir}"
    )
    assert stdout[-1] == f"Please download the targets from {_TARGETS_URL}"


def _find_files(directory: Path) -> tuple[Path, ...]:
    return tuple(sorted(_each_file(directory)))


def _each_file(directory: Path) -> Iterator[Path]:
    for item in directory.iterdir():
        if item.is_file():
            yield item
        elif item.name not in (".pytest_competition_cache", "__pycache__"):
            yield from _each_file(item)


def _dummy_body(target_file: Path) -> str:
    return os.linesep.join(
        (
            f"# dummy test for {target_file}",
            "",
            "",
            "def test_dummy() -> None:",
            "    assert True",
        )
    )


def _coverages_files(results_dir: Path) -> tuple[Path, ...]:
    return (
        results_dir / "coverages" / "example1.xml",
        results_dir / "coverages" / "example2.xml",
        results_dir / "coverages" / "sub_example.__init__.xml",
        results_dir / "coverages" / "sub_example.example3.xml",
    )
