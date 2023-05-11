from typing import Optional

import click
from rich.console import Console

import i8_terminal.api.earnings as earnings_api
from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.stock_info import validate_ticker
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS
from i8_terminal.service_result.earning_list_result import EarningsListResult
from i8_terminal.types.ticker_param_type import TickerParamType


@earnings.command()
@click.option("--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Company ticker.")
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def list(ticker: str, export_path: Optional[str]) -> None:
    """
    Lists upcoming company earnings.

    Examples:

    `i8 earnings list --ticker AAPL`

    """
    earnings_list: EarningsListResult = earnings_api.list(ticker, 10)
    if export_path:
        if export_path.split(".")[-1] == "html":
            df = earnings_list.to_df()
            table = df2Table(df)
            export_to_html(table, export_path)
        else:
            export_data(
                earnings_list.to_df("raw"),
                export_path,
                column_width=18,
                column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
            )
    else:
        df = earnings_list.to_df()
        console = Console()
        console.print(earnings_list._to_rich_table("humanize", "default"))
