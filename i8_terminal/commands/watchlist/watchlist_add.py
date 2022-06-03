from typing import List

import click
import investor8_sdk
from rich.console import Console
from rich.style import Style

from i8_terminal.app.layout import get_terminal_command_layout
from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.config import USER_SETTINGS
from i8_terminal.types.ticker_param_type import TickerParamType

from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType  # isort:skip


def add_tickers_to_watchlist(name: str, tickers: List[str]) -> None:
    wl = investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id"))
    investor8_sdk.UserApi().add_to_watchlist(body={"Id": wl.id, "Tickers": tickers})


@watchlist.command()
@click.option(
    "--name",
    "-n",
    type=UserWatchlistsParamType(),
    required=True,
    help="Name of the watchlist you want to see more details.",
)
@click.option("--tickers", "-k", type=TickerParamType(), required=True, help="Comma-separated list of tickers.")
@pass_command
def add(name: str, tickers: str) -> None:
    console = Console()
    tickers_list = tickers.replace(" ", "").upper().split(",")
    with console.status("Updating Watchlist...", spinner="material"):
        add_tickers_to_watchlist(name, tickers_list)
    console.print(
        f"✅ Ticker{'s' if len(tickers_list) > 1 else ''} [cyan]{', '.join(tickers_list)}[/cyan] added to watchlist [cyan]{name}[/cyan] successfully!"
    )
    terminal_command_style = Style(**get_terminal_command_layout())
    console.print(
        f'Try `[{terminal_command_style}]watchlist details --name "{name}"[/{terminal_command_style}]` to see the watchlist.'
    )
