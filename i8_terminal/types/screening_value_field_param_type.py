from typing import Dict, List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_value_fields() -> List[Tuple[str, str]]:
    return [
        ("value_numeric", "Absolute Value Numeric"),
        ("value", "Absolute Value"),
        ("overall_rank", "Overall Rank"),
        ("spx_rank", "Spx Rank"),
        ("dow_rank", "Dow Rank"),
        ("sector_rank", "Sector Rank"),
        ("industry_rank", "Industry Rank"),
        ("overall_percentile", "Overall Percentile"),
        ("spx_percentile", "Spx Percentile"),
        ("nasdaq_percentile", "Nasdaq Percentile"),
        ("dow_percentile", "Dow Percentile"),
        ("sector_percentile", "Sector Percentile"),
        ("industry_percentile", "Industry Percentile"),
    ]


class ScreeningValueFieldParamType(AutoCompleteChoice):
    name = "screeningvaluefield"
    metrics_default_pt: Dict[str, str] = {}

    def get_suggestions(self, keyword: str, pre_populate: bool = True, metric: str = None) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_value_fields())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "SCREENINGVALUEFIELD"
