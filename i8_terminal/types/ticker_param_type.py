from typing import List, Tuple

from i8_terminal.common.stock_info import get_stocks
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


class TickerParamType(AutoCompleteChoice):
    name = "ticker"

    def get_suggestions(self, keyword: str, pre_populate: bool = False) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_stocks())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]

        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "TICKER"
