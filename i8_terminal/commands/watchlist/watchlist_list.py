from typing import Dict, List

import investor8_sdk
from investor8_sdk.models import WatchlistDto
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.config import USER_SETTINGS


def get_user_watchlists() -> DataFrame:
    results = investor8_sdk.UserApi().get_watchlists_by_user(user_id=USER_SETTINGS.get("user_id"))
    return prepare_watchlists_df(results.watchlists)


def prepare_watchlists_df(watchlists: List[WatchlistDto]) -> DataFrame:
    wls: List[Dict[str, str]] = []
    for wl in watchlists:
        wls.append(
            {
                "name": wl.name,
                "tickers": f"{', '.join(str(ticker) for ticker in wl.tickers[:5])} {f'and {len(wl.tickers)-5} more' if len(wl.tickers) > 5 else ''}",
            }
        )
    watchlists_df = DataFrame(wls)
    col_names = {
        "name": "Name",
        "tickers": "Tickers",
    }
    return format_df(watchlists_df, col_names, {})


@watchlist.command()
@pass_command
def list() -> None:
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_user_watchlists()
    table = df2Table(df)
    console.print(table)
