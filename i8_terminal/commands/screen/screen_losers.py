from typing import Optional, cast

import arrow
import click
from click.types import DateTime
from rich.console import Console

from i8_terminal.commands.screen import screen
from i8_terminal.common.cli import pass_command
from i8_terminal.common.screen import get_top_stocks_df, render_top_stocks
from i8_terminal.types.market_indice_param_type import MarketIndiceParamType
from i8_terminal.types.metric_identifier_param_type import MetricIdentifierParamType
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
@click.option("--metrics", "metrics", "-m", type=MetricIdentifierParamType(), help="Additional metrices to analyse.")
@click.option("--count", "count", "-c", default=10, help="Number of results shown.")
@click.option("--date", "date", "-d", type=DateTime(), help="Date on which the analysis is perfomed on.")
@pass_command
def losers(
    index: str,
    view_name: Optional[str],
    date: Optional[DateTime],
    metrics: Optional[str],
    count: Optional[int],
    export_path: Optional[str],
) -> None:
    """
    Lists today loser companies.

    Examples:

    `i8 screen losers --index $SPX`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_top_stocks_df("losers", index, view_name, arrow.get(date).datetime, count, metrics)
    if df is None:
        console.print("No data found for today losers", style="yellow")
        return
    table = render_top_stocks(df, export_path=export_path)
    if table:
        console.print(table)
