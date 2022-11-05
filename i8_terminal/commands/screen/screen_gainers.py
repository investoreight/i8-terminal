from typing import Optional

import click
from rich.console import Console

from i8_terminal.commands.screen import screen
from i8_terminal.common.cli import pass_command
from i8_terminal.common.screen import get_top_stocks_df, render_top_stocks
from i8_terminal.types.market_indice_param_type import MarketIndiceParamType
from i8_terminal.types.metric_view_param_type import MetricViewParamType


@screen.command()
@click.option(
    "--index",
    "-i",
    type=MarketIndiceParamType(),
    default="$SPX",
    help="Index of market.",
)
@click.option(
    "--view_name", "view_name", "-v", type=MetricViewParamType(), help="Metric view name in configuration file."
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def gainers(index: str, view_name: Optional[str], export_path: Optional[str]) -> None:
    """
    Lists today winner companies.

    Examples:

    `i8 screen gainers --index $SPX`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_top_stocks_df("winners", index, view_name)
    if df is None:
        console.print("No data found for today winners", style="yellow")
        return
    table = render_top_stocks(df, export_path=export_path, ascending=False)
    if table:
        console.print(table)
