import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.stock_info import get_stocks_df


def get_recent_earnings_df(size: int) -> pd.DataFrame:
    earnings = investor8_sdk.EarningsApi().get_recent_earnings(size=size)
    earnings = [d.to_dict() for d in earnings]
    df = pd.DataFrame(earnings)
    stocks_df = get_stocks_df()
    return pd.merge(df, stocks_df, on="ticker")


def format_recent_earnings_df(df: pd.DataFrame, target: str) -> pd.DataFrame:
    formatters = {
        "latest_price": get_formatter("number", target),
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
        "eps_ws": "Eps Cons.",
        "eps_actual": "Eps Actual.",
        "revenue_ws": "Revenue Cons.",
        "revenue_actual": "Revenue Actual.",
    }
    return format_df(df, col_names, formatters)


@earnings.command()
@pass_command
def recent() -> None:
    """Lists recent company earnings."""
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_recent_earnings_df(size=20)
    df_formatted = format_recent_earnings_df(df, "console")
    table = df2Table(df_formatted)
    console.print(table)
