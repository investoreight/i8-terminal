from typing import Any, Dict, Optional

import click
import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.utils import export_data
from i8_terminal.config import APP_SETTINGS, USER_SETTINGS

from i8_terminal.common.metrics import get_current_metrics_df, prepare_current_metrics_formatted_df  # isort:skip

from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType  # isort:skip


def prepare_watchlist_stocks_df(name: str) -> Optional[pd.DataFrame]:
    watchlist = investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id"))
    watchlist_stocks_df = get_current_metrics_df(
        ",".join(watchlist.tickers),
        "total_revenue,net_income,basic_eps,net_cash_from_operating_activities,total_assets,total_liabilities",
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
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = prepare_watchlist_stocks_df(name)
    if df is None:
        console.print("No data found for metrics with selected tickers", style="yellow")
    elif export_path:
        export_data(
            prepare_current_metrics_formatted_df(df, "store"),
            export_path,
            column_width=18,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
    else:
        columns_justify: Dict[str, Any] = {}
        for metric_display_name, metric_df in df.groupby("display_name"):
            columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
        table = df2Table(prepare_current_metrics_formatted_df(df, "console"), columns_justify=columns_justify)
        console.print(table)
