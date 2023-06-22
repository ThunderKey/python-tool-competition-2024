"""The main CLI for the Python tool competition 2024."""

from rich import get_console


def main_cli() -> int:
    """Run the CLI to run the tool competition."""
    console = get_console()
    console.print("hello world")
    return 0


__all__ = ["main_cli"]
