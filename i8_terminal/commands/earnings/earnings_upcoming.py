from typing import Optional

import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.stock_info import validate_tickers
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.ticker_param_type import TickerParamType


def get_upcoming_earnings_df(size: int) -> DataFrame:
    earnings = investor8_sdk.EarningsApi().get_upcoming_earnings(size=size)
    earnings = [d.to_dict() for d in earnings]
    df = DataFrame(earnings)
    df["eps_beat_rate"] = df["eps_beat_rate"] * 100
    df["revenue_beat_rate"] = df["revenue_beat_rate"] * 100
    return df


def get_upcoming_earnings_df_by_ticker(tickers: str) -> DataFrame:
    upcoming_earnings = []
    for tk in tickers.replace(" ", "").upper().split(","):
        upcoming_earnings.extend([investor8_sdk.EarningsApi().get_upcoming_earning(tk)])
    df = DataFrame([h.to_dict() for h in upcoming_earnings])
    df["eps_beat_rate"] = df["eps_beat_rate"] * 100
    df["revenue_beat_rate"] = df["revenue_beat_rate"] * 100
    return df


def format_upcoming_earnings_df(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "latest_price": get_formatter("price", target),
        "change": get_formatter("perc", target),
        "fyq": get_formatter("fyq", target),
        "eps_ws": get_formatter("number", target),
        "eps_beat_rate": get_formatter("number_perc" if target == "console" else "perc", target),
        "revenue_ws": get_formatter("financial", target),
        "revenue_beat_rate": get_formatter("number_perc" if target == "console" else "perc", target),
    }
    col_names = {
        "ticker": "Ticker",
        "name": "Name",
        "latest_price": "Price",
        "change": "Change",
        "actual_report_date": "Report Date",
        "fyq": "Period",
        "call_time": "Call Time",
        "eps_ws": "EPS Estimate",
        "eps_beat_rate": "EPS Beat Rate",
        "revenue_ws": "Revenue Estimate",
        "revenue_beat_rate": "Revenue Beat Rate",
    }
    return format_df(df, col_names, formatters)


def format_upcoming_earnings_df_by_ticker(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "fyq": get_formatter("fyq", target),
        "eps_ws": get_formatter("number", target),
        "eps_beat_rate": get_formatter("number_perc" if target == "console" else "perc", target),
        "revenue_ws": get_formatter("financial", target),
        "revenue_beat_rate": get_formatter("number_perc" if target == "console" else "perc", target),
    }
    col_names = {
        "ticker": "Ticker",
        "actual_report_date": "Report Date",
        "fyq": "Period",
        "call_time": "Call Time",
        "eps_ws": "EPS Estimate",
        "eps_beat_rate": "EPS Beat Rate",
        "revenue_ws": "Revenue Estimate",
        "revenue_beat_rate": "Revenue Beat Rate",
    }
    return format_df(df, col_names, formatters)


@earnings.command()
@click.option(
    "--tickers", "-k", type=TickerParamType(), callback=validate_tickers, help="Comma-separated list of tickers."
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def upcoming(tickers: Optional[str], export_path: Optional[str]) -> None:
    """
    Lists upcoming company earnings.

    Examples:

    `i8 earnings upcoming`

    `i8 earnings upcoming --tickers AAPL,MSFT`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_upcoming_earnings_df_by_ticker(tickers) if tickers else get_upcoming_earnings_df(size=20)
    if export_path:
        if export_path.split(".")[-1] == "html":
            df_formatted = (
                format_upcoming_earnings_df_by_ticker(df, "console")
                if tickers
                else format_upcoming_earnings_df(df, "console")
            )
            table = df2Table(df_formatted)
            export_to_html(table, export_path)
            return
        export_data(
            format_upcoming_earnings_df_by_ticker(df, "store") if tickers else format_upcoming_earnings_df(df, "store"),
            export_path,
            column_width=18,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
        return
    df_formatted = (
        format_upcoming_earnings_df_by_ticker(df, "console") if tickers else format_upcoming_earnings_df(df, "console")
    )
    table = df2Table(df_formatted)
    console.print(table)
