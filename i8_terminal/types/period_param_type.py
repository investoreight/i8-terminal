from typing import Dict, List, Tuple

from i8_terminal.common.metrics import get_all_metrics_default_period_types_dict
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice

PERIOD_TYPES: Dict[str, List[Tuple[str, str]]] = {
    "D": [("p", "Default period type (daily)")],
    "R": [("p", "Default period type (realtime)")],
    "FY": [
        ("fy", "most recent fiscal year (default)"),
        ("q", "most recent quarter"),
        ("ttm", "trailing 12 months"),
        ("ytd", "year to date"),
    ],
    "Q": [
        ("q", "most recent quarter (default)"),
        ("fy", "most recent fiscal year"),
        ("ttm", "trailing 12 months"),
        ("ytd", "year to date"),
    ],
    "TTM": [
        ("ttm", "trailing 12 months (default)"),
        ("fy", "most recent fiscal year"),
        ("q", "most recent quarter"),
        ("ytd", "year to date"),
    ],
    "YTD": [
        ("ytd", "year to date (default)"),
        ("fy", "most recent fiscal year"),
        ("q", "most recent quarter"),
        ("ttm", "trailing 12 months"),
    ],
}


class PeriodParamType(AutoCompleteChoice):
    name = "period"
    metrics_default_pt: Dict[str, str] = {}

    def get_suggestions(self, keyword: str, pre_populate: bool = True, metric: str = None) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.metrics_default_pt = get_all_metrics_default_period_types_dict()
        self.set_choices(
            PERIOD_TYPES.get(self.metrics_default_pt[metric if metric else ""], [("p", "Default period type (NA)")])
        )

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "PERIOD"
