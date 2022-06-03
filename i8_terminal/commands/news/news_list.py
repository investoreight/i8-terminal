from typing import Any, Dict, List

import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.news import news
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import format_number, get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.utils import validate_ticker
from i8_terminal.types.ticker_param_type import TickerParamType


def get_news_df(identifier: str, page_size: int) -> DataFrame:
    if identifier:
        news = investor8_sdk.NewsApi().get_ticker_news(identifier)
    else:
        news = investor8_sdk.NewsApi().get_latest_news(page_size=page_size)
    df = DataFrame([d.to_dict() for d in news])
    df["news_source"] = df["news_source"].apply(map_news_source)
    df["stock_prices"] = df["stock_prices"].apply(lambda x: format_stock_prices(x))
    return df


def format_stock_prices(prices: List[Dict[str, Any]]) -> str:
    formatted_stock_prices = []
    for p in prices:
        formatted_stock_prices.append(
            f'{p["ticker"]} {format_number(p["latest_price"])} ({format_number(p["change_perc"], unit="percentage")})'
        )
    return "\n".join(formatted_stock_prices)


def format_news_df(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "publication_timestamp": get_formatter("date", target),
    }
    col_names = {
        "news_source": "Source",
        "publication_timestamp": "Date",
        "title": "Title",
        "stock_prices": "Tickers",
    }
    return format_df(df, col_names, formatters)


def map_news_source(news_source: int) -> str:
    if news_source == 0:
        return "InvestorEight"
    elif news_source == 1:
        return "Yahoo!Finance"
    elif news_source == 2:
        return "Highlights"
    else:
        return "-"


@news.command()
@click.option(
    "--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Ticker or company name."
)
@pass_command
def list(ticker: str) -> None:
    """Lists the latest market news. If ticker is provided, the news are filtered based on the give ticker."""
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_news_df(ticker, page_size=10)
    df_formatted = format_news_df(df, "console")
    table = df2Table(df_formatted)
    console.print(table)
