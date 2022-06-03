from typing import List, Tuple

import investor8_sdk

from i8_terminal.common.stock_info import get_stocks
from i8_terminal.config import USER_SETTINGS
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_user_watchlist_tickers() -> List[Tuple[str, str]]:
    results = investor8_sdk.UserApi().get_watchlists_by_user(user_id=USER_SETTINGS.get("user_id"))
    tickers = set(ticker for wl in results.watchlists for ticker in wl.tickers)
    stocks = get_stocks()
    return [(tk, name) for (tk, name) in stocks if tk in tickers]


class UserWatchlistTickersParamType(AutoCompleteChoice):
    name = "userwatchlisttickers"

    def get_suggestions(self, keyword: str, pre_populate: bool = False) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_user_watchlist_tickers())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]

        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "USERWATCHLISTTICKERS"
