from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_price_periods() -> List[Tuple[str, str]]:
    return [
        ("1M", "One Month"),
        ("3M", "Three Months"),
        ("6M", "Six Months"),
        ("1Y", "One Year"),
        ("3Y", "Three Years"),
        ("5Y", "Five Years"),
    ]


class PricePeriodParamType(AutoCompleteChoice):
    name = "priceperiod"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_price_periods())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "PRICEPERIOD"
