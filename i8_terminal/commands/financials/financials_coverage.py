import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.financials import financials
from i8_terminal.common.cli import pass_command
from i8_terminal.common.financials import available_fin_df2tree
from i8_terminal.common.stock_info import validate_ticker
from i8_terminal.types.ticker_param_type import TickerParamType


def get_available_financials_df(ticker: str) -> DataFrame:
    available_fins = investor8_sdk.FinancialsApi().get_list_available_standardized_financials(ticker=ticker)
    return DataFrame([d.to_dict() for d in available_fins])


@financials.command()
@click.option("--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Company ticker.")
@pass_command
def coverage(ticker: str) -> None:
    """
    Shows available financial statements of the given company.

    Examples:

    `i8 financials coverage --ticker AAPL`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        available_fin_df = get_available_financials_df(ticker)
        available_fins_tree = available_fin_df2tree(available_fin_df, ticker)
    console.print(available_fins_tree)
