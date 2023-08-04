from pathlib import Path

import pytest
from rich.table import Table

from python_tool_competition_2024.cli.init_command import (
    _Names,
    _names_from_readable_name,
)

from .helpers import renderable_to_strs, run_cli, run_successful_cli


@pytest.mark.parametrize("help_arg", ("-h", "--help"))
def test_init_with_help(help_arg: str) -> None:
    assert run_successful_cli(("init", help_arg), generators_called=False) == (
        "Usage: main-cli init [OPTIONS]",
        "",
        "  Interactively initialize a new project for a generator.",
        "",
        "Options:",
        "  -v, --verbose  Enables verbose mode",
        "  -h, --help     Show this message and exit.",
    )


@pytest.mark.parametrize(
    ("readable_name", "expected_names"),
    (
        (
            "My Test Generator",
            _Names(
                readable_name="My Test Generator",
                project_name="python_tool_competition_2024_my_test_generator",
                sub_module_name="my_test_generator",
                class_name="MyTestGenerator",
                generator_name="my-test-generator",
            ),
        ),
        (
            "some other",
            _Names(
                readable_name="some other",
                project_name="python_tool_competition_2024_some_other",
                sub_module_name="some_other",
                class_name="SomeOther",
                generator_name="some-other",
            ),
        ),
        (
            "MY-complex/NAME_plus25",
            _Names(
                readable_name="MY-complex/NAME_plus25",
                project_name="python_tool_competition_2024_my_complex_name_plus25",
                sub_module_name="my_complex_name_plus25",
                class_name="MyComplexNamePlus25",
                generator_name="my-complex-name-plus25",
            ),
        ),
    ),
)
def test_names_from_readable_name(readable_name: str, expected_names: _Names) -> None:
    assert _names_from_readable_name(readable_name) == expected_names


def test_init_with_confirm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    parent_dir = tmp_path
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    assert _run_init(("Some Generator", "", "Some Name", "some@test.com", "Y")) == (
        0,
        (
            "Interactively generate a new project configuration for a generator.",
            "",
            "What is the human-readable name of the generator?: "
            "In what directory should the project directory be created? "
            f"({parent_dir}): "
            "What is your full name?: "
            "What is your e-mail address?: " + table_strs[0],
            *table_strs[1:],
            "Create the project with these settings? [y/n]: Creating Project...",
        ),
        (),
    )


def test_init_with_tmp_file(tmp_path: Path) -> None:
    parent_dir = tmp_path
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    assert _run_init(
        ("Some Generator", str(tmp_path), "Some Name", "some@test.com", "Y")
    ) == (
        0,
        (
            "Interactively generate a new project configuration for a generator.",
            "",
            "What is the human-readable name of the generator?: "
            "In what directory should the project directory be created? "
            f"({Path.cwd()}): "
            "What is your full name?: "
            "What is your e-mail address?: " + table_strs[0],
            *table_strs[1:],
            "Create the project with these settings? [y/n]: Creating Project...",
        ),
        (),
    )


def test_init_with_no_confirm() -> None:
    parent_dir = Path.cwd()
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    assert _run_init(("Some Generator", "", "Some Name", "some@test.com", "N")) == (
        1,
        (
            "Interactively generate a new project configuration for a generator.",
            "",
            "What is the human-readable name of the generator?: "
            "In what directory should the project directory be created? "
            f"({parent_dir}): "
            "What is your full name?: "
            "What is your e-mail address?: " + table_strs[0],
            *table_strs[1:],
            "Create the project with these settings? [y/n]: ",
        ),
        (),
    )


def test_init_with_invalid_names() -> None:
    parent_dir = Path.cwd()
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    assert _run_init(
        (
            "\t      ",
            "Some Generator",
            "",
            "",
            "Some Name",
            "_-_^_$",
            "some@test.com",
            "N",
        )
    ) == (
        1,
        (
            "Interactively generate a new project configuration for a generator.",
            "",
            "What is the human-readable name of the generator?: Cannot be empty",
            "What is the human-readable name of the generator?: "
            "In what directory should the project directory be created? "
            f"({parent_dir}): "
            "What is your full name?: Cannot be empty",
            "What is your full name?: What is your e-mail address?: Cannot be empty",
            "What is your e-mail address?: " + table_strs[0],
            *table_strs[1:],
            "Create the project with these settings? [y/n]: ",
        ),
        (),
    )


def _run_init(stdin: tuple[str, ...]) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
    return run_cli(("init",), generators_called=False, stdin=stdin)


def _confirmation_table_lines(
    *, readable_name: str, parent_dir: Path, author: str
) -> tuple[str, ...]:
    names = _names_from_readable_name(readable_name)
    table = Table(show_header=False)
    table.add_row("Readable Name", names.readable_name)
    table.add_row(
        "Fully Qualified Class",
        f"{names.project_name}.{names.sub_module_name}.{names.class_name}",
    )
    table.add_row("Generator Name", names.generator_name)
    table.add_row("Target Dir", str(parent_dir / names.project_name))
    table.add_row("Author", author)
    return renderable_to_strs(table)
