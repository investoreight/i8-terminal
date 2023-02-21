from datetime import datetime
from typing import Dict, List, Tuple

from i8_terminal.common.metrics import get_all_metrics_types_dict
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice

PERIODS: Dict[str, List[Tuple[str, str]]] = {
    "summary": [],
    "price": [*[(f"{i}da", f"{i} day{'s' if i > 1 else ''} ago") for i in range(1, 3)]],
    "performance": [*[(f"{i}da", f"{i} day{'s' if i > 1 else ''} ago") for i in range(1, 3)]],
    "technical": [*[(f"{i}da", f"{i} day{'s' if i > 1 else ''} ago") for i in range(1, 3)]],
    "fin_metric": [
        ("mrq", "most recent quarter"),
        ("mry", "most recent financial year"),
        ("ttm", "trailing 12 months"),
        ("ytd", "year to date"),
        *[(f"{i}qa", f"{i} quarter{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"{i}ya", f"{i} year{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"q{i}_{y}", f"Fiscal quarter {i} {y}") for i in range(1, 5) for y in range(datetime.now().year, 2008, -1)],
        *[
            (f"q{i}ttm_{y}", f"Fiscal quarter {i} {y}")
            for i in range(1, 4)
            for y in range(datetime.now().year, 2008, -1)
        ],
        *[
            (f"q{i}ytd_{y}", f"Fiscal quarter {i} {y}")
            for i in range(2, 4)
            for y in range(datetime.now().year, 2008, -1)
        ],
        *[(f"fy_{y}", f"Fiscal year {y}") for y in range(datetime.now().year, 2008, -1)],
    ],
    "fin_statement": [
        ("mrq", "most recent quarter"),
        ("mry", "most recent financial year"),
        ("ttm", "trailing 12 months"),
        ("ytd", "year to date"),
        *[(f"{i}qa", f"{i} quarter{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"{i}ya", f"{i} year{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"q{i}_{y}", f"Fiscal quarter {i} {y}") for i in range(1, 5) for y in range(datetime.now().year, 2008, -1)],
        *[
            (f"q{i}ttm_{y}", f"Fiscal quarter {i} {y}")
            for i in range(1, 4)
            for y in range(datetime.now().year, 2008, -1)
        ],
        *[
            (f"q{i}ytd_{y}", f"Fiscal quarter {i} {y}")
            for i in range(2, 4)
            for y in range(datetime.now().year, 2008, -1)
        ],
        *[(f"fy_{y}", f"Fiscal year {y}") for y in range(datetime.now().year, 2008, -1)],
    ],
    "earnings": [
        ("mrq", "most recent quarter"),
        *[(f"{i}qa", f"{i} quarter{'s' if i > 1 else ''} ago") for i in range(1, 3)],
        *[(f"q{i}_{y}", f"Fiscal quarter {i} {y}") for i in range(1, 5) for y in range(datetime.now().year, 2008, -1)],
        ("uq", "upcoming quarter"),
    ],
}


class PeriodParamType(AutoCompleteChoice):
    name = "period"
    metrics: Dict[str, str] = {}

    def get_suggestions(self, keyword: str, pre_populate: bool = True, metric: str = None) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.metrics = get_all_metrics_types_dict()
        self.set_choices(PERIODS.get(self.metrics[metric if metric else ""], []))

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "PERIOD"
