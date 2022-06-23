from typing import Any, Dict

import click
import investor8_sdk
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.company import company
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table, format_df


def search_stocks_df(keyword: str) -> DataFrame:
    results = investor8_sdk.SearchApi().search_stocks(keyword, 8)
    df = DataFrame([d.to_dict() for d in results])
    return df[["ticker", "name"]]


def format_stocks_df(df: DataFrame, target: str) -> DataFrame:
    formatters: Dict[str, Any] = {}
    col_names = {
        "ticker": "Ticker",
        "name": "Name",
    }
    return format_df(df, col_names, formatters)


@company.command()
@click.option("--keyword", "-k", required=True, help="Keyword can be ticker or company name.")
@pass_command
def search(keyword: str) -> None:
    """
    Searches and shows all securities that match with the given KEYWORD.

    Examples:

    `i8 company search --keyword apl`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = search_stocks_df(keyword)
    df_formatted = format_stocks_df(df, "console")
    table = df2Table(df_formatted)
    console.print(table)
