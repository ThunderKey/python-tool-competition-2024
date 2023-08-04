"""The CLI command to initialize a new generator."""

import dataclasses
import re
from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .helpers import create_console


@click.command
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode")
@click.pass_context
def init(ctx: click.Context, *, verbose: bool) -> None:
    """Interactively initialize a new project for a generator."""
    with create_console(ctx, verbose=verbose) as console:
        console.print(
            "Interactively generate a new project configuration for a generator."
        )
        console.line()
        config = _gather_init_config(console)
        console.print(config.to_table())
        if not Confirm.ask("Create the project with these settings?"):
            ctx.exit(1)

        console.print("Creating Project...")


@dataclasses.dataclass(frozen=True)
class _Names:
    readable_name: str
    project_name: str
    sub_module_name: str
    class_name: str
    generator_name: str

    def to_table(self) -> Table:
        table = Table(show_header=False)
        table.add_column(style="bold")
        table.add_row("Readable Name", self.readable_name)
        table.add_row(
            "Fully Qualified Class",
            f"{self.project_name}.{self.sub_module_name}.{self.class_name}",
        )
        table.add_row("Generator Name", self.generator_name)
        return table


_VALID_NAME_CHARACTER_RANGES = "a-zA-Z0-9"
_NAME_SPLIT_REGEX = re.compile(rf"[^{_VALID_NAME_CHARACTER_RANGES}]+")
_VALID_NAME_REGEX = re.compile(rf"[{_VALID_NAME_CHARACTER_RANGES}]")


def _names_from_readable_name(readable_name: str) -> _Names:
    name_parts = _NAME_SPLIT_REGEX.split(readable_name)
    lower_name_parts = [part.lower() for part in name_parts]
    module = "_".join(lower_name_parts)
    project_name = f"python_tool_competition_2024_{module}"
    return _Names(
        readable_name=readable_name,
        project_name=project_name,
        sub_module_name=module,
        class_name="".join(part.capitalize() for part in name_parts),
        generator_name="-".join(lower_name_parts),
    )


@dataclasses.dataclass(frozen=True)
class _InitConfig(_Names):
    project_dir: Path
    author: str

    def to_table(self) -> Table:
        table = super().to_table()
        table.add_row("Target Dir", str(self.project_dir))
        table.add_row("Author", self.author)
        return table


def _gather_init_config(console: Console) -> _InitConfig:
    names = _names_from_readable_name(
        _ask_until_valid(
            console, "What is the [bold]human-readable[/bold] name of the generator?"
        )
    )
    target_dir = Path(
        _ask_or_default(
            console,
            "In what directory should the project directory be created?",
            str(Path.cwd()),
        )
    ).absolute()
    author_name = _ask_until_valid(console, "What is your full name?")
    author_email = _ask_until_valid(console, "What is your e-mail address?")

    return _InitConfig(
        **dataclasses.asdict(names),
        project_dir=target_dir / names.project_name,
        author=f"{author_name} <{author_email}>",
    )


def _ask_until_valid(console: Console, prompt: str) -> str:
    while True:
        result = Prompt.ask(prompt, console=console).strip()
        if _VALID_NAME_REGEX.match(result):
            return result
        console.print("Cannot be empty", style="red")


def _ask_or_default(console: Console, prompt: str, default: str) -> str:
    return Prompt.ask(prompt, console=console, default=default, show_default=True)
