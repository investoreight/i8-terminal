from rich.console import Console

from i8_terminal.commands.notebook import notebook
from i8_terminal.common.cli import pass_command


@notebook.command()
@pass_command
def launch() -> None:
    """
    Launches jupyter notebook.

    Examples:

    `i8 notebook launch`

    """
    console = Console()
    with console.status("Launching notebook...", spinner="material"):
        pass
