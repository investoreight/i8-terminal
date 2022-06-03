from rich.console import Console

from i8_terminal.commands.screen import screen
from i8_terminal.common.cli import pass_command


@screen.command()
@pass_command
def list() -> None:
    console = Console()
    console.print("The screen list command is not implemented yet!", style="yellow")
