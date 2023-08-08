from collections.abc import Mapping
from pathlib import Path
from typing import TypeAlias
from unittest import mock

import pytest
from rich.table import Table

from python_tool_competition_2024.cli.init_command import (
    _env_without_venv,
    _Names,
    _names_from_readable_name,
)

from .helpers import renderable_to_strs, run_cli, run_successful_cli

_EXAMPLE_PYPROJECT = """\
[tool.poetry]
name = "python-tool-competition-2024-hypothesis"
version = "0.1.0"
description = "Python Tool Competition 2024 implementation using Hypothesis"
authors = ["Test Test <test@test.com>"]
readme = "README.md"
packages = [{include = "python_tool_competition_2024_hypothesis"}]

[tool.poetry.dependencies]
python = "^3.11"
python-tool-competition-2024 = {git = \
"git@github.com:ThunderKey/python-tool-competition-2024.git"}


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
"""


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
                sub_module_name="generator",
                fqdn_module_name="python_tool_competition_2024_my_test_generator.generator",
                class_name="MyTestGenerator",
                fqdn_class_name="python_tool_competition_2024_my_test_generator.generator.MyTestGenerator",
                generator_name="my-test-generator",
            ),
        ),
        (
            "some other",
            _Names(
                readable_name="some other",
                project_name="python_tool_competition_2024_some_other",
                sub_module_name="generator",
                fqdn_module_name="python_tool_competition_2024_some_other.generator",
                class_name="SomeOther",
                fqdn_class_name="python_tool_competition_2024_some_other.generator.SomeOther",
                generator_name="some-other",
            ),
        ),
        (
            "MY-complex/NAME_plus25",
            _Names(
                readable_name="MY-complex/NAME_plus25",
                project_name="python_tool_competition_2024_my_complex_name_plus25",
                sub_module_name="generator",
                fqdn_module_name="python_tool_competition_2024_my_complex_name_plus25.generator",
                class_name="MyComplexNamePlus25",
                fqdn_class_name="python_tool_competition_2024_my_complex_name_plus25.generator.MyComplexNamePlus25",
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
    project_dir = parent_dir / "python_tool_competition_2024_some_generator"
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    output, subprocess_mock = _run_init(
        ("Some Generator", "", "Some Name", "some@test.com", "Y"), flags=("--verbose",)
    )
    assert output == (
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
            "Create the project with these settings? [y/n]: "
            "Creating File Structure...",
            "Running Command:",
            "├── Command: poetry init "
            "--name=python_tool_competition_2024_some_generator "
            "--description=Python Tool Competition 2024 implementation using Some "
            "Generator --author=Some Name <some@test.com> ",
            "│   "
            "--dependency=git+ssh://git@github.com:ThunderKey/python-tool-competition-2024.git",
            f"└── Working Dir: {project_dir}",
            "Installing Dependencies...",
            "Running Command:",
            "├── Command: poetry install --no-interaction",
            f"└── Working Dir: {project_dir}",
        ),
        (),
    )
    project_dir = parent_dir / "python_tool_competition_2024_some_generator"
    run_kwargs = {"cwd": project_dir, "env": mock.ANY, "check": True}
    assert _get_simple_args(subprocess_mock.run) == (
        (
            (
                (
                    "poetry",
                    "init",
                    "--name=python_tool_competition_2024_some_generator",
                    "--description=Python Tool Competition 2024 implementation "
                    "using Some Generator",
                    "--author=Some Name <some@test.com>",
                    "--dependency=git+ssh://git@github.com:ThunderKey/python-tool-competition-2024.git",
                ),
            ),
            run_kwargs,
        ),
        ((("poetry", "install", "--no-interaction"),), run_kwargs),
    )

    assert _list_dir(parent_dir) == {
        "python_tool_competition_2024_some_generator": {
            "README.md": "",
            "pyproject.toml": _EXAMPLE_PYPROJECT
            + """\

[tool.poetry.plugins."python_tool_competition_2024.test_generators"]
some-generator = "python_tool_competition_2024_some_generator.generator:SomeGenerator"
""",
            "python_tool_competition_2024_some_generator": {
                "__init__.py": "",
                "generator.py": """\
\"""A test generator using Some Generator.\"""

from pathlib import Path

from python_tool_competition_2024.generation_results import (
    TestGenerationFailure,
    TestGenerationResult,
    TestGenerationSuccess,
)
from python_tool_competition_2024.generators import TestGenerator


class SomeGenerator(TestGenerator):
    \"""A test generator using Some Generator.\"""

    def build_test(self, target_file: Path) -> TestGenerationResult:  # noqa: V107
        \"""
        Genereate a test for the specific target file.

        Args:
            target_file: The `pathlib.Path` of the file to generate a test for.

        Returns:
            Either a `TestGenerationSuccess` if it was successful, or a
            `TestGenerationFailure` otherwise.
        \"""
        raise NotImplementedError("Implement the test generator")
""",
            },
        }
    }


def test_init_with_tmp_file(tmp_path: Path) -> None:
    parent_dir = tmp_path
    project_dir = tmp_path / "python_tool_competition_2024_testgen"
    project_dir.mkdir()
    (project_dir / "inner_existing.py").touch()
    (tmp_path / "outer_existing.py").touch()
    table_strs = _confirmation_table_lines(
        readable_name="TestGen",
        parent_dir=parent_dir,
        author="Other Name <other@test.com>",
    )
    output, subprocess_mock = _run_init(
        ("TestGen", str(tmp_path), "Other Name", "other@test.com", "Y", "Y")
    )
    assert output == (
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
            "Create the project with these settings? [y/n]: "
            "Creating File Structure...",
            f"The project directory {project_dir} already exists. Delete? [y/n]: "
            "Installing Dependencies...",
        ),
        (),
    )
    run_kwargs = {
        "cwd": parent_dir / "python_tool_competition_2024_testgen",
        "env": mock.ANY,
        "check": True,
    }
    assert _get_simple_args(subprocess_mock.run) == (
        (
            (
                (
                    "poetry",
                    "init",
                    "--name=python_tool_competition_2024_testgen",
                    "--description=Python Tool Competition 2024 implementation "
                    "using TestGen",
                    "--author=Other Name <other@test.com>",
                    "--dependency=git+ssh://git@github.com:ThunderKey/python-tool-competition-2024.git",
                ),
            ),
            run_kwargs,
        ),
        ((("poetry", "install", "--no-interaction"),), run_kwargs),
    )

    assert _list_dir(parent_dir) == {
        "outer_existing.py": "",
        "python_tool_competition_2024_testgen": {
            "README.md": "",
            "pyproject.toml": _EXAMPLE_PYPROJECT
            + """\

[tool.poetry.plugins."python_tool_competition_2024.test_generators"]
testgen = "python_tool_competition_2024_testgen.generator:Testgen"
""",
            "python_tool_competition_2024_testgen": {
                "__init__.py": "",
                "generator.py": """\
\"""A test generator using TestGen.\"""

from pathlib import Path

from python_tool_competition_2024.generation_results import (
    TestGenerationFailure,
    TestGenerationResult,
    TestGenerationSuccess,
)
from python_tool_competition_2024.generators import TestGenerator


class Testgen(TestGenerator):
    \"""A test generator using TestGen.\"""

    def build_test(self, target_file: Path) -> TestGenerationResult:  # noqa: V107
        \"""
        Genereate a test for the specific target file.

        Args:
            target_file: The `pathlib.Path` of the file to generate a test for.

        Returns:
            Either a `TestGenerationSuccess` if it was successful, or a
            `TestGenerationFailure` otherwise.
        \"""
        raise NotImplementedError("Implement the test generator")
""",
            },
        },
    }


def test_init_without_overwriting_exsiting(tmp_path: Path) -> None:
    parent_dir = tmp_path
    project_dir = tmp_path / "python_tool_competition_2024_some_generator"
    project_dir.mkdir()
    (project_dir / "inner_existing.py").touch()
    (tmp_path / "outer_existing.py").touch()
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Other Name <other@test.com>",
    )
    output, subprocess_mock = _run_init(
        ("Some Generator", str(tmp_path), "Other Name", "other@test.com", "Y", "N")
    )
    assert output == (
        1,
        (
            "Interactively generate a new project configuration for a generator.",
            "",
            "What is the human-readable name of the generator?: "
            "In what directory should the project directory be created? "
            f"({Path.cwd()}): "
            "What is your full name?: "
            "What is your e-mail address?: " + table_strs[0],
            *table_strs[1:],
            "Create the project with these settings? [y/n]: "
            "Creating File Structure...",
            f"The project directory {project_dir} already exists. Delete? [y/n]: ",
        ),
        (),
    )
    subprocess_mock.run.assert_not_called()

    assert _list_dir(parent_dir) == {
        "outer_existing.py": "",
        "python_tool_competition_2024_some_generator": {"inner_existing.py": ""},
    }


def test_init_with_no_confirm() -> None:
    parent_dir = Path.cwd()
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    output, subprocess_mock = _run_init(
        ("Some Generator", "", "Some Name", "some@test.com", "N")
    )
    assert output == (
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
    subprocess_mock.run.assert_not_called()


def test_init_with_invalid_names() -> None:
    parent_dir = Path.cwd()
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    output, subprocess_mock = _run_init(
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
    )
    assert output == (
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
    subprocess_mock.run.assert_not_called()


def test_init_with_missing_target_dir(tmp_path: Path) -> None:
    inexisting_dir = tmp_path / "inexistings"
    parent_dir = tmp_path
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    output, subprocess_mock = _run_init(
        (
            "Some Generator",
            str(inexisting_dir),
            str(parent_dir),
            "Some Name",
            "some@test.com",
            "N",
        )
    )
    assert output == (
        1,
        (
            "Interactively generate a new project configuration for a generator.",
            "",
            "What is the human-readable name of the generator?: "
            "In what directory should the project directory be created? "
            f"({Path.cwd()}): The parent directory of the project needs to exist",
            "In what directory should the project directory be created? "
            f"({Path.cwd()}): "
            "What is your full name?: What is your e-mail address?: " + table_strs[0],
            *table_strs[1:],
            "Create the project with these settings? [y/n]: ",
        ),
        (),
    )
    subprocess_mock.run.assert_not_called()


def test_init_with_failing_init(tmp_path: Path) -> None:
    parent_dir = tmp_path
    project_dir = parent_dir / "python_tool_competition_2024_some_generator"
    pyproject_path = project_dir / "pyproject.toml"
    table_strs = _confirmation_table_lines(
        readable_name="Some Generator",
        parent_dir=parent_dir,
        author="Some Name <some@test.com>",
    )
    output, subprocess_mock = _run_init(
        ("Some Generator", str(tmp_path), "Some Name", "some@test.com", "Y"),
        create_pyproject=False,
    )
    assert output == (
        1,
        (
            "Interactively generate a new project configuration for a generator.",
            "",
            "What is the human-readable name of the generator?: "
            "In what directory should the project directory be created? "
            f"({Path.cwd()}): "
            "What is your full name?: "
            "What is your e-mail address?: " + table_strs[0],
            *table_strs[1:],
            "Create the project with these settings? [y/n]: Creating File Structure...",
            f"Poetry init was not able to create the file {pyproject_path}",
        ),
        (),
    )

    run_kwargs = {"cwd": project_dir, "env": mock.ANY, "check": True}
    assert _get_simple_args(subprocess_mock.run) == (
        (
            (
                (
                    "poetry",
                    "init",
                    "--name=python_tool_competition_2024_some_generator",
                    "--description=Python Tool Competition 2024 implementation "
                    "using Some Generator",
                    "--author=Some Name <some@test.com>",
                    "--dependency=git+ssh://git@github.com:ThunderKey/python-tool-competition-2024.git",
                ),
            ),
            run_kwargs,
        ),
    )


@pytest.mark.parametrize(
    ("original_env", "expected_env"),
    (
        pytest.param({}, {}, id="empty"),
        pytest.param({"EXAMPLE": "test"}, {"EXAMPLE": "test"}, id="no venv"),
        # virtual env without path
        pytest.param(
            {"VIRTUAL_ENV": "/some_test/dir", "EXAMPLE": "test"},
            {"EXAMPLE": "test"},
            id="venv without path",
        ),
        # virtual env with path
        pytest.param(
            {
                "VIRTUAL_ENV": "/some_test/dir",
                "PATH": "/some/bin:/some_test/dir/bin:/other_bin/:./some_test/dir/bin",
                "OTHER": "value",
            },
            {"OTHER": "value", "PATH": "/some/bin:/other_bin/:./some_test/dir/bin"},
            id="venv with path",
        ),
        # virtual env not in path
        pytest.param(
            {"VIRTUAL_ENV": "/some_test/dir", "PATH": "/some/bin:/other/bin/:mytest"},
            {"PATH": "/some/bin:/other/bin/:mytest"},
            id="venv not in path",
        ),
    ),
)
def test_env_without_venv(
    original_env: Mapping[str, str], expected_env: Mapping[str, str]
) -> None:
    with mock.patch("python_tool_competition_2024.cli.init_command.os") as os_mock:
        os_mock.pathsep = ":"
        os_mock.environ = dict(original_env)
        mock.seal(os_mock)
        assert _env_without_venv() == expected_env
        assert os_mock.environ == original_env


def _run_init(
    stdin: tuple[str, ...],
    *,
    flags: tuple[str, ...] = (),
    create_pyproject: bool = True,
) -> tuple[tuple[int, tuple[str, ...], tuple[str, ...]], mock.MagicMock]:
    with mock.patch(
        "python_tool_competition_2024.cli.init_command.subprocess"
    ) as subprocess_mock:

        def mocked_run(
            cmd: tuple[str, ...], *_args: object, cwd: Path, **_kwargs: object
        ) -> None:
            if create_pyproject and cmd[0:2] == ("poetry", "init"):
                (cwd / "pyproject.toml").write_text(_EXAMPLE_PYPROJECT)

        subprocess_mock.run.side_effect = mocked_run
        mock.seal(subprocess_mock)
        return (
            run_cli(("init", *flags), generators_called=False, stdin=stdin),
            subprocess_mock,
        )


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


_DirList: TypeAlias = str | Mapping[str, "_DirList"]


def _list_dir(path: Path) -> _DirList:
    if path.is_file():
        return path.read_text()
    return {sub_path.name: _list_dir(sub_path) for sub_path in path.iterdir()}


def _get_simple_args(
    mock: mock.MagicMock,
) -> tuple[tuple[tuple[object, ...], Mapping[str, object]], ...]:
    return tuple((call.args, call.kwargs) for call in mock.call_args_list)
