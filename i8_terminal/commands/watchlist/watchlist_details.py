from typing import Dict, List

import click
import investor8_sdk
import pandas as pd
from rich.console import Console
from rich.table import Table

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.config import USER_SETTINGS

from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType  # isort:skip


def render_watchlist_table(name: str) -> Table:
    target = "console"
    watchlist_stocks: List[Dict[str, str]] = []
    watchlist = investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id"))
    all_stock_info = investor8_sdk.StockInfoApi().get_all_stock_info(market_index="")
    all_latest_prices = investor8_sdk.PriceApi().get_all_latest_prices()
    metrics = investor8_sdk.MetricsApi().get_current_metrics(symbols=",".join(watchlist.tickers), metrics="market_cap")
    metrics_data_df = pd.DataFrame([m.to_dict() for m in metrics.data])
    metrics_data_df.rename(columns={"metric": "metric_name", "symbol": "ticker"}, inplace=True)
    metrics_metadata_df = pd.DataFrame([m.to_dict() for m in metrics.metadata])
    metrics_df = pd.merge(metrics_data_df, metrics_metadata_df, on="metric_name")
    metrics_df["value"] = (
        metrics_df["value"]
        .astype(metrics_df["data_format"].values[0])
        .map(get_formatter(metrics_df["display_format"].values[0], target))
    )
    for ticker in watchlist.tickers:
        latest_price = all_latest_prices[ticker]
        stock_info = all_stock_info[ticker]
        watchlist_stocks.append(
            {
                "ticker": ticker,
                "company": stock_info.name,
                "exchange": stock_info.exchange,
                "latest_price": latest_price.latest_price,
                "change": latest_price.change_perc,
            }
        )
    watchlist_stocks_df = pd.DataFrame(watchlist_stocks)
    watchlist_stocks_df = pd.merge(
        watchlist_stocks_df, metrics_df.pivot(index="ticker", columns="metric_name", values="value"), on="ticker"
    )
    formatters = {
        "latest_price": get_formatter("price", target),
        "change": get_formatter("perc", target),
    }
    col_names = {
        "ticker": "Ticker",
        "company": "Company",
        "exchange": "Exchange",
        "latest_price": "Price",
        "change": "Change",
        "market_cap": "Market Cap",
    }
    df_formatted = format_df(watchlist_stocks_df, col_names, formatters)
    return df2Table(df_formatted)


@watchlist.command()
@click.option(
    "--name",
    "-n",
    type=UserWatchlistsParamType(),
    required=True,
    help="Name of the watchlist you want to see more details.",
)
@pass_command
def details(name: str) -> None:
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        table = render_watchlist_table(name)
    console.print(table)
