from typing import Any, Dict, Optional

import click
import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS, USER_SETTINGS
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.metric_view_param_type import MetricViewParamType
from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType


def prepare_watchlist_stocks_df(name: str, metrics: str) -> Optional[pd.DataFrame]:
    watchlist = investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id"))
    watchlist_stocks_df = get_current_metrics_df(",".join(watchlist.tickers), metrics)
    return watchlist_stocks_df


@watchlist.command()
@click.option(
    "--name",
    "-n",
    type=UserWatchlistsParamType(),
    required=True,
    help="Name of the watchlist.",
)
@click.option(
    "--metrics",
    "-m",
    type=MetricParamType(),
    help="Comma-separated list of daily metrics.",
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@click.option(
    "--view_name", "view_name", "-v", type=MetricViewParamType(), help="Metric view name in configuration file."
)
@pass_command
def metrics(name: str, metrics: str, export_path: Optional[str], view_name: Optional[str]) -> None:
    """
    Lists and compares watchlist companies based on a given list of metrics.

    Examples:

    `i8 watchlist metrics --name MyWatchlist --metrics total_revenue,net_income,price_to_earnings`

    """
    console = Console()
    if not metrics and not view_name:
        console.print("The 'metrics' or 'view_name' parameter must be provided", style="yellow")
        return
    if view_name and metrics:
        console.print("The 'metrics' or 'view_name' options are mutually exclusive", style="yellow")
        return
    if view_name:
        metrics = APP_SETTINGS["metric_view"][view_name]["metrics"]
    with console.status("Fetching data...", spinner="material"):
        df = prepare_watchlist_stocks_df(name, metrics)
    if df is None:
        console.print("No data found for metrics with selected tickers", style="yellow")
        return
    for m in [*set(metric.split(".")[0] for metric in set(metrics.split(","))) - set(df["metric_name"])]:
        console.print(f"\nNo data found for metric {m} with selected tickers", style="yellow")
    columns_justify: Dict[str, Any] = {}
    if export_path:
        if export_path.split(".")[-1] == "html":
            for metric_display_name, metric_df in df.groupby("display_name"):
                columns_justify[metric_display_name] = (
                    "left" if metric_df["display_format"].values[0] == "str" else "right"
                )
            table = df2Table(prepare_current_metrics_formatted_df(df, "console"), columns_justify=columns_justify)
            export_to_html(table, export_path)
            return
        export_data(
            prepare_current_metrics_formatted_df(df, "store"),
            export_path,
            column_width=18,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
    else:
        for metric_display_name, metric_df in df.groupby("display_name"):
            columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
        table = df2Table(prepare_current_metrics_formatted_df(df, "console"), columns_justify=columns_justify)
        console.print(table)
