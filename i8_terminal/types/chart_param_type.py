from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_chart_param_types() -> List[Tuple[str, str]]:
    return [("bar", "Bar chart"), ("line", "Line chart"), ("candlestick", "Candlestick chart")]


class ChartParamType(AutoCompleteChoice):
    name = "charttype"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_chart_param_types())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "CHARTTYPE"
