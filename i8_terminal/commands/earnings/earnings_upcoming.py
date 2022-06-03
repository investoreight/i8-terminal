from typing import Optional

import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.utils import validate_ticker
from i8_terminal.types.ticker_param_type import TickerParamType


def get_upcoming_earnings_df(size: int) -> DataFrame:
    earnings = investor8_sdk.EarningsApi().get_upcoming_earnings(size=size)
    earnings = [d.to_dict() for d in earnings]
    df = DataFrame(earnings)
    return df


def get_upcoming_earnings_df_by_ticker(ticker: str) -> DataFrame:
    earnings = [investor8_sdk.EarningsApi().get_upcoming_earning(ticker).to_dict()]
    return DataFrame(earnings)


def format_upcoming_earnings_df(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "latest_price": get_formatter("number", target),
        "change": get_formatter("perc", target),
        "fyq": get_formatter("fyq", target),
        "eps_ws": get_formatter("number", target),
    }
    col_names = {
        "ticker": "Ticker",
        "name": "Name",
        "exchange": "Exchange",
        "sector": "Sector",
        "latest_price": "Price",
        "change": "Change",
        "actual_report_date": "Report Date",
        "fyq": "Period",
        "call_time": "Call Time",
        "eps_ws": "EPS Cons.",
    }
    return format_df(df, col_names, formatters)


def format_upcoming_earnings_df_by_ticker(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "actual_report_time": get_formatter("date", target),
        "fyq": get_formatter("fyq", target),
        "eps_ws": get_formatter("number", target),
        "revenue_ws": get_formatter("financial", target),
    }
    col_names = {
        "actual_report_time": "Date",
        "call_time": "Call Time",
        "fyq": "Period",
        "eps_ws": "EPS Cons.",
        "revenue_ws": "Revenue Cons.",
    }
    return format_df(df, col_names, formatters)


@earnings.command()
@click.option("--ticker", "-k", type=TickerParamType(), callback=validate_ticker, help="Company ticker.")
@pass_command
def upcoming(ticker: Optional[str]) -> None:
    """Lists upcoming company earnings."""
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_upcoming_earnings_df_by_ticker(ticker) if ticker else get_upcoming_earnings_df(size=20)
    df_formatted = (
        format_upcoming_earnings_df_by_ticker(df, "console") if ticker else format_upcoming_earnings_df(df, "console")
    )
    table = df2Table(df_formatted)
    console.print(table)
