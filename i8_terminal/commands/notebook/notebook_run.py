from typing import Any, Dict, List

import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.notebook import notebook
from i8_terminal.common.cli import pass_command
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os

@notebook.command()
@click.option(
    "--name", "-n", help="Name of the notebook."
)
@click.option(
    "--params", "-p", help="Parameters for the notebook."
)
@pass_command
def run(name: str, params: str) -> None:
    """
    Runs and browse the specified notebook.

    Examples:

    `i8 notebook run --name analysis1.ipynb --params TICKER=MSFT`

    """
    if params:
        ticker = params.split('=')[0]
    else:
        ticker = 'MSFT'

    console = Console()
    with console.status("Running notebook...", spinner="material"):
        with open(f'notebooks/{name}.ipynb') as f:
            nb = nbformat.read(f, as_version=4)
            
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

        ep.preprocess(nb)

        with open(f'notebooks/{name}_exe.ipynb', 'wt') as f:
            nbformat.write(nb, f)

    console.print("Completed")