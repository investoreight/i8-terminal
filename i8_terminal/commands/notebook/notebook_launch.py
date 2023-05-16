import os

import click
import nbformat as nbf
from rich.console import Console

from i8_terminal.commands.notebook import notebook
from i8_terminal.common.cli import pass_command


@notebook.command()
@click.option("--name", "-n", help="Notebook file name.")
@pass_command
def launch(name: str) -> None:
    """
    Launches jupyter notebook.

    Examples:

    `i8 notebook launch --name mynotebook`

    """
    console = Console()
    with console.status("Launching notebook...", spinner="material"):
        nb = nbf.v4.new_notebook()
        text = "Welcome to notebook of i8 Terminal."

        code = (
            "from i8_terminal.config import init_notebook\n" "from i8_terminal import api as i8\n\n" "init_notebook()"
        )

        nb["cells"] = [nbf.v4.new_markdown_cell(text), nbf.v4.new_code_cell(code)]
        fname = f"{name}.ipynb"

        with open(fname, "w") as f:
            nbf.write(nb, f)

        os.system(f"jupyter notebook {name}.ipynb")
