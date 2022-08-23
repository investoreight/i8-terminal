from datetime import datetime
from typing import Dict, List, Optional, Tuple

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice

PERIODS: Dict[str, List[Tuple[str, str]]] = {
    "summary": [],
    "price": [*[(f"{i}da", f"{i} day{'s' if i > 1 else ''} ago") for i in range(1, 3)]],
    "performance": [*[(f"{i}da", f"{i} day{'s' if i > 1 else ''} ago") for i in range(1, 3)]],
    "technical": [*[(f"{i}da", f"{i} day{'s' if i > 1 else ''} ago") for i in range(1, 3)]],
    "fin_metric": [
        ("mrq", "most recent quarter"),
        ("mry", "most recent year"),
        *[(f"{i}qa", f"{i} quarter{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"{i}ya", f"{i} year{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"q{i}_{y}", f"Fiscal quarter {i} {y}") for i in range(1, 5) for y in range(datetime.now().year, 2008, -1)],
        *[(f"fy_{y}", f"Fiscal year {y}") for y in range(datetime.now().year, 2008, -1)],
    ],
    "fin_statement": [
        ("mrq", "most recent quarter"),
        ("mry", "most recent year"),
        *[(f"{i}qa", f"{i} quarter{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"{i}ya", f"{i} year{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"q{i}_{y}", f"Fiscal quarter {i} {y}") for i in range(1, 5) for y in range(datetime.now().year, 2008, -1)],
        *[(f"fy_{y}", f"Fiscal year {y}") for y in range(datetime.now().year, 2008, -1)],
    ],
    "earnings": [
        ("mrq", "most recent quarter"),
        *[(f"{i}qa", f"{i} quarter{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"q{i}_{y}", f"Fiscal quarter {i} {y}") for i in range(1, 5) for y in range(datetime.now().year, 2008, -1)],
        ("uq", "upcoming quarter"),
    ],
}


def get_periods(metric: Optional[str]) -> List[Tuple[str, str]]:
    if not metric:
        return []
    df = get_all_metrics_df()[["metric_name", "type"]]
    type = list(df[df.metric_name == metric]["type"])[0]
    return PERIODS[type]


class PeriodParamType(AutoCompleteChoice):
    name = "period"

    def get_suggestions(self, keyword: str, pre_populate: bool = True, metric: str = None) -> List[Tuple[str, str]]:
        self.set_choices(get_periods(metric))

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "PERIOD"
