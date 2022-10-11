from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_market_indice_types() -> List[Tuple[str, str]]:
    return [("$DJI", "Dow 30"), ("$SPX", "S&P 500"), ("$NDX", "NASDAQ 100")]


class MarketIndiceParamType(AutoCompleteChoice):
    name = "marketindice"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_market_indice_types())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "MARKETINDICE"
