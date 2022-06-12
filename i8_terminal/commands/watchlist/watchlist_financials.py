from typing import Any, Dict

import click
import investor8_sdk
import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table, format_metrics_df
from i8_terminal.config import USER_SETTINGS

from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType  # isort:skip


def render_watchlist_table(name: str) -> Table:
    watchlist = investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id"))
    metrics = investor8_sdk.MetricsApi().get_current_metrics(
        symbols=",".join(watchlist.tickers),
        metrics="total_revenue,net_income,basic_eps,net_cash_from_operating_activities,total_assets,total_liabilities",
    )
    metrics_data_df = pd.DataFrame([m.to_dict() for m in metrics.data])
    metrics_data_df.rename(columns={"metric": "metric_name", "symbol": "Ticker"}, inplace=True)
    metrics_metadata_df = pd.DataFrame([m.to_dict() for m in metrics.metadata])
    metrics_df = pd.merge(metrics_data_df, metrics_metadata_df, on="metric_name").replace("string", "str")
    metrics_df_formatted = format_metrics_df(metrics_df, "console")
    columns_justify: Dict[str, Any] = {}
    for metric_display_name, metric_df in metrics_df_formatted.groupby("display_name"):
        columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
    watchlist_stocks_df = (
        metrics_df_formatted.pivot(index="Ticker", columns="display_name", values="value")
        .reset_index(level=0)
        .reindex(np.insert(metrics_df["display_name"].unique(), 0, "Ticker"), axis=1)
    )
    return df2Table(watchlist_stocks_df, columns_justify=columns_justify)


@watchlist.command()
@click.option(
    "--name",
    "-n",
    type=UserWatchlistsParamType(),
    required=True,
    help="Name of the watchlist.",
)
@pass_command
def financials(name: str) -> None:
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        table = render_watchlist_table(name)
    console.print(table)
