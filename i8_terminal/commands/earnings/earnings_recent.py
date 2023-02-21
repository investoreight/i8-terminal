from typing import Optional

import click
import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.stock_info import get_stocks_df
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS


def get_recent_earnings_df(size: int) -> pd.DataFrame:
    earnings = investor8_sdk.EarningsApi().get_recent_earnings(size=size)
    earnings = [d.to_dict() for d in earnings]
    df = pd.DataFrame(earnings)
    stocks_df = get_stocks_df()
    return pd.merge(df, stocks_df, on="ticker")


def format_recent_earnings_df(df: pd.DataFrame, target: str) -> pd.DataFrame:
    formatters = {
        "latest_price": get_formatter("price", target),
        "change": get_formatter("perc", target),
        "fyq": get_formatter("fyq", target),
        "eps_ws": get_formatter("number", target),
        "eps_actual": get_formatter("number", target),
        "revenue_ws": get_formatter("financial", target),
        "revenue_actual": get_formatter("financial", target),
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
        "eps_actual": "EPS Actual",
        "revenue_ws": "Revenue Estimate",
        "revenue_actual": "Revenue Actual",
    }
    return format_df(df, col_names, formatters)


@earnings.command()
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def recent(export_path: Optional[str]) -> None:
    """
    Lists recent company earnings.

    Examples:

    `i8 earnings recent`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_recent_earnings_df(size=20)
    if export_path:
        if export_path.split(".")[-1] == "html":
            df_formatted = format_recent_earnings_df(df, "console")
            table = df2Table(df_formatted)
            export_to_html(table, export_path)
            return
        export_data(
            format_recent_earnings_df(df, "store"),
            export_path,
            column_width=18,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
        return
    df_formatted = format_recent_earnings_df(df, "console")
    table = df2Table(df_formatted)
    console.print(table)
