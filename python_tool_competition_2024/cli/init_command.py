#
# Copyright (c) 2023 Nicolas Erni.
#
# This file is part of python-tool-competition-2024
# (see https://github.com/ThunderKey/python-tool-competition-2024/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""The CLI command to initialize a new generator."""

import dataclasses
import os
import re
import shutil
import subprocess  # nosec: B404
import sys
from collections.abc import Mapping
from pathlib import Path
from string import Template
from typing import Literal

import click
import toml
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree

from ..errors import PyprojectTomlNotCreatedError
from ..generator_plugins import ENTRY_POINT_GROUP_NAME
from .helpers import create_console

_SOURCE_DIR = Path(__file__).parent.parent
_TEMPLATES_DIR = _SOURCE_DIR / "templates"

_MIN_VERBOSITY_SHOW_COMMANDS = 1
_MIN_VERBOSITY_SHOW_FULL_ERRORS = 1


@click.command
@click.option("-v", "--verbose", count=True, help="Enables verbose mode")
@click.pass_context
def init(ctx: click.Context, *, verbose: int) -> None:
    """Interactively initialize a new project for a generator."""
    with create_console(
        ctx, show_full_errors=verbose >= _MIN_VERBOSITY_SHOW_FULL_ERRORS
    ) as console:
        console.print(
            "Interactively generate a new project configuration for a generator."
        )
        console.line()
        config = _gather_init_config(
            console, show_commands=verbose >= _MIN_VERBOSITY_SHOW_COMMANDS
        )
        console.print(config.to_table())
        if not Confirm.ask("Create the project with these settings?", console=console):
            ctx.exit(1)

        _create_project(config, console)


@dataclasses.dataclass(frozen=True)
class _Names:
    readable_name: str
    project_name: str
    module_name: str
    fqdn_module_name: str
    class_name: str
    fqdn_class_name: str
    generator_name: str

    def to_table(self) -> Table:
        table = Table(show_header=False)
        table.add_column(style="bold")
        table.add_row("Readable Name", self.readable_name)
        table.add_row("Fully Qualified Class", self.fqdn_class_name)
        table.add_row("Generator Name", self.generator_name)
        return table


_VALID_NAME_CHARACTER_RANGES = "a-zA-Z0-9"
_NAME_SPLIT_REGEX = re.compile(rf"[^{_VALID_NAME_CHARACTER_RANGES}]+")
_VALID_NAME_REGEX = re.compile(rf"[{_VALID_NAME_CHARACTER_RANGES}]")


def _names_from_readable_name(readable_name: str) -> _Names:
    name_parts = _NAME_SPLIT_REGEX.split(readable_name)
    lower_name_parts = [part.lower() for part in name_parts]
    project_name = f"python-tool-competition-2024-{'-'.join(lower_name_parts)}"
    module_name = f"python_tool_competition_2024_{'_'.join(lower_name_parts)}"
    fqdn_module_name = f"{module_name}.generator"
    class_name = "".join(part.capitalize() for part in name_parts) + "TestGenerator"
    return _Names(
        readable_name=readable_name,
        project_name=project_name,
        module_name=module_name,
        fqdn_module_name=fqdn_module_name,
        class_name=class_name,
        fqdn_class_name=f"{fqdn_module_name}.{class_name}",
        generator_name="-".join(lower_name_parts),
    )


@dataclasses.dataclass(frozen=True)
class _InitConfig(_Names):
    project_dir: Path
    author: str
    show_commands: bool

    def to_table(self) -> Table:
        table = super().to_table()
        table.add_row("Target Dir", str(self.project_dir))
        table.add_row("Author", self.author)
        return table


def _gather_init_config(console: Console, *, show_commands: bool) -> _InitConfig:
    names = _names_from_readable_name(
        _ask_until_valid(
            console, "What is the [bold]human-readable[/bold] name of the generator?"
        )
    )
    while True:
        target_dir = Path(
            _ask_or_default(
                console,
                "In what directory should the project directory be created?",
                str(Path.cwd()),
            )
        ).absolute()
        if target_dir.exists():
            break
        console.print("The parent directory of the project needs to exist", style="red")
    author_name = _ask_until_valid(console, "What is your full name?")
    author_email = _ask_until_valid(console, "What is your e-mail address?")

    return _InitConfig(
        **dataclasses.asdict(names),
        project_dir=target_dir / names.project_name,
        author=f"{author_name} <{author_email}>",
        show_commands=show_commands,
    )


def _ask_until_valid(console: Console, prompt: str) -> str:
    while True:
        result = Prompt.ask(prompt, console=console).strip()
        if _VALID_NAME_REGEX.match(result):
            return result
        console.print("Cannot be empty", style="red")


def _ask_or_default(console: Console, prompt: str, default: str) -> str:
    return Prompt.ask(prompt, console=console, default=default, show_default=True)


def _create_project(config: _InitConfig, console: Console) -> None:
    console.print("Creating File Structure...")
    if config.project_dir.exists():
        if not Confirm.ask(
            f"The project directory {config.project_dir} already exists. Delete?",
            console=console,
        ):
            sys.exit(1)
        shutil.rmtree(config.project_dir)
    config.project_dir.mkdir()
    _copy_templates(_TEMPLATES_DIR, config.project_dir, config)
    _create_pyproject_toml(config, console)

    console.print("Installing Dependencies...")
    _run_poetry(config, console, "install")


def _create_pyproject_toml(config: _InitConfig, console: Console) -> None:
    _run_poetry(
        config,
        console,
        "init",
        f"--name={config.project_name}",
        "--description=Python Tool Competition 2024 "
        f"implementation using {config.readable_name}",
        f"--author={config.author}",
        "--dependency=python-tool-competition-2024",
    )

    pyproject_path = config.project_dir / "pyproject.toml"
    if not pyproject_path.exists():
        raise PyprojectTomlNotCreatedError(pyproject_path)

    generator_class = f"{config.fqdn_module_name}:{config.class_name}"
    plugin_config = {
        "tool": {
            "poetry": {
                "plugins": {
                    ENTRY_POINT_GROUP_NAME: {config.generator_name: generator_class}
                }
            }
        }
    }
    with pyproject_path.open("a") as fp:
        fp.write(os.linesep)
        toml.dump(plugin_config, fp)


def _run_poetry(
    config: _InitConfig,
    console: Console,
    # whitelist specific sub commands
    sub_command: Literal["init", "install"],
    *args: str,
) -> None:
    cmd = ("poetry", sub_command, *args)
    cwd = config.project_dir
    # reset env to ignore current virtualenv
    env = _env_without_venv()
    if config.show_commands:
        tree = Tree("Running Command:")
        tree.add(f"Command: {' '.join(cmd)}")
        tree.add(f"Working Dir: {cwd}")
        console.print(tree)
    subprocess.run(cmd, cwd=cwd, env=env, check=True)  # noqa: S603


def _env_without_venv() -> Mapping[str, str]:
    env = dict(os.environ)
    if "VIRTUAL_ENV" in env:
        virtual_env = env.pop("VIRTUAL_ENV")
        if "PATH" in env:
            env["PATH"] = os.pathsep.join(
                path
                for path in env.pop("PATH").split(os.pathsep)
                if not path.lstrip().startswith(virtual_env)
            )
    return env


_VAR_FILE_PREFIX = "__var__"


def _copy_templates(template_dir: Path, target_dir: Path, names: _Names) -> None:
    names_dict = dataclasses.asdict(names)
    for path in template_dir.iterdir():
        if path.name == "__pycache__":
            continue
        target_path = target_dir / path.name
        if target_path.stem.startswith(_VAR_FILE_PREFIX):
            target_path = target_path.with_stem(
                names_dict[target_path.stem.removeprefix(_VAR_FILE_PREFIX)]
            )
        if path.is_file():
            _copy_template(path, target_path, names_dict)
        else:
            target_path.mkdir()
            _copy_templates(path, target_path, names)


def _copy_template(
    template_path: Path, target: Path, substitutes: Mapping[str, str]
) -> None:
    template = Template(template_path.read_text())
    target.write_text(template.substitute(substitutes))
