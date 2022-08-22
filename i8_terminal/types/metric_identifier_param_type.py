from typing import Dict, List, Optional, Tuple

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice

PERIODS: Dict[str, List[Tuple[str, str]]] = {
    "summary": [],
    "price": [],
    "performance": [],
    "technical": [],
    "fin_metric": [
        ("mrq", "most recent quarter"),
        ("mry", "most recent year"),
        ("1qa", "1 quarter ago"),
        ("2qa", "2 quarters ago"),
        ("1ya", "1 year ago"),
    ],
    "fin_statement": [
        ("mrq", "most recent quarter"),
        ("mry", "most recent year"),
        ("1qa", "1 quarter ago"),
        ("2qa", "2 quarters ago"),
        ("1ya", "1 year ago"),
    ],
    "earnings": [
        ("mrq", "most recent quarter"),
        ("1qa", "1 quarter ago"),
        ("2qa", "2 quarters ago"),
        ("uq", "upcoming quarter"),
    ],
}


def get_metrics() -> List[Tuple[str, str]]:
    df = get_all_metrics_df()[["metric_name", "display_name"]]
    return list(df.to_records(index=False))


def get_periods(metric: Optional[str]) -> List[Tuple[str, str]]:
    if not metric:
        return []
    df = get_all_metrics_df()[["metric_name", "type"]]
    type = df[df["metric_name"] == metric.lower()]["type"].values[0]
    return PERIODS[type]


class MetricIdentifierParamType(AutoCompleteChoice):
    name = "metricidentifier"

    def get_suggestions(
        self, keyword: str, pre_populate: bool = False, param_type: str = None, metric: str = None
    ) -> List[Tuple[str, str]]:
        if param_type == "metric":
            if not self.is_loaded:
                self.set_choices(get_metrics())

            if pre_populate and keyword.strip() == "":
                return self._choices[: self.size]

            return self.search_keyword(keyword)
        else:
            return get_periods(metric)

    def __repr__(self) -> str:
        return "METRICIDENTIFIER"
