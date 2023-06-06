from typing import Dict, List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_value_fields() -> List[Tuple[str, str]]:
    return [
        ("value_numeric", ""),
        ("value", ""),
        ("overall_rank", ""),
        ("spx_rank", ""),
        ("dow_rank", ""),
        ("sector_rank", ""),
        ("industry_rank", ""),
        ("overall_percentile", ""),
        ("spx_percentile", ""),
        ("nasdaq_percentile", ""),
        ("dow_percentile", ""),
        ("sector_percentile", ""),
        ("industry_percentile", ""),
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
