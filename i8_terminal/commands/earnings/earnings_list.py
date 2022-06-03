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


def get_hist_earnings_df(ticker: str, size: int) -> DataFrame:
    historical_earnings = investor8_sdk.EarningsApi().get_historical_earnings(ticker, size=size)
    historical_earnings = [d.to_dict() for d in historical_earnings]
    df = DataFrame(historical_earnings)
    df["period"] = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    return df


def format_hist_earnings_df(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "actual_report_time": get_formatter("date", target),
        "eps_actual": get_formatter("number", target),
        "eps_ws": get_formatter("number", target),
        "revenue_actual": get_formatter("financial", target),
        "revenue_ws": get_formatter("financial", target),
    }
    col_names = {
        "actual_report_time": "Date",
        "call_time": "Call Time",
        "period": "Period",
        "eps_actual": "EPS Actual",
        "eps_ws": "EPS Cons.",
        "revenue_actual": "Revenue Actual",
        "revenue_ws": "Revenue Cons.",
    }
    return format_df(df, col_names, formatters)


@earnings.command()
@click.option("--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Company ticker.")
@pass_command
def list(ticker: str) -> None:
    """Lists upcoming company earnings."""
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_hist_earnings_df(ticker, size=10)
    df_formatted = format_hist_earnings_df(df, "console")
    table = df2Table(df_formatted)
    console.print(table)
