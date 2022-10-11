from typing import Any, Dict, Optional

import click
import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.screen import screen
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.market_indice_param_type import MarketIndiceParamType
from i8_terminal.types.metric_view_param_type import MetricViewParamType


def prepare_losers_df(index: str, view_name: Optional[str]) -> Optional[pd.DataFrame]:
    metrics = APP_SETTINGS["commands"]["screen_losers"]["metrics"]
    companies_data = investor8_sdk.ScreenerApi().get_top_stocks("losers", index=index)
    if companies_data is None:
        return None
    companies = [company.ticker for company in companies_data]
    if view_name:
        metrics = metrics + "," + APP_SETTINGS["metric_view"][view_name]["metrics"]
    return get_current_metrics_df(",".join(companies), metrics)


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
@pass_command
def losers(index: str, view_name: Optional[str]) -> None:
    """
    Lists today loser companies.

    Examples:

    `i8 screen losers --index $SPX`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = prepare_losers_df(index, view_name)
    if df is None:
        console.print("No data found for today losers", style="yellow")
        return
    columns_justify: Dict[str, Any] = {}
    for metric_display_name, metric_df in df.groupby("display_name"):
        columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
    table = df2Table(
        prepare_current_metrics_formatted_df(df, "console").sort_values("Change"), columns_justify=columns_justify
    )
    console.print(table)
