from typing import List

import click
import investor8_sdk
from rich.console import Console

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.config import USER_SETTINGS
from i8_terminal.types.ticker_param_type import TickerParamType


def create_watchlist(name: str, tickers: List[str]) -> None:
    investor8_sdk.UserApi().create_watchlist(
        body={"UserId": USER_SETTINGS.get("user_id"), "Name": name, "Tickers": tickers}
    )


@watchlist.command()
@click.option(
    "--name",
    "-n",
    help="Name of the watchlist you want to create.",
)
@click.option("--tickers", "-k", type=TickerParamType(), required=True, help="Comma-separated list of tickers.")
@pass_command
def create(name: str, tickers: str) -> None:
    console = Console()
    tickers_list = tickers.replace(" ", "").upper().split(",")
    with console.status("Creating Watchlist...", spinner="material"):
        create_watchlist(name, tickers_list)
    console.print(f"✅ Watchlist [cyan]{name}[/cyan] is created successfully!")
