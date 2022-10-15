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
from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType


def prepare_watchlist_stocks_df(name: str) -> Optional[pd.DataFrame]:
    watchlist = investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id"))
    watchlist_stocks_df = get_current_metrics_df(
        ",".join(watchlist.tickers),
        APP_SETTINGS["metric_view"]["watchlist_financials"]["metrics"],
    )
    return watchlist_stocks_df


@watchlist.command()
@click.option(
    "--name",
    "-n",
    type=UserWatchlistsParamType(),
    required=True,
    help="Name of the watchlist.",
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def financials(name: str, export_path: Optional[str]) -> None:
    """
    Lists financial metrics for a given watchlist.

    Examples:

    `i8 watchlist financials --name MyWatchlist`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = prepare_watchlist_stocks_df(name)
    if df is None:
        console.print("No data found for metrics with selected tickers", style="yellow")
        return
    period_rows = []
    for ticker, ticker_df in df.groupby("Ticker"):
        period_rows.append(
            {
                "Ticker": ticker,
                "metric_name": "period",
                "value": ticker_df["period"].values[0],
                "display_name": "Period",
                "data_format": "str",
                "display_format": "str",
            }
        )
    df = pd.concat([pd.DataFrame(period_rows), df], ignore_index=True, axis=0)
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
