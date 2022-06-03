from typing import List, Tuple

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_metrics() -> List[Tuple[str, str]]:
    df = get_all_metrics_df()[["metric_name", "display_name"]]
    return list(df.to_records(index=False))


class MetricParamType(AutoCompleteChoice):
    name = "metric"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_metrics())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]

        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "METRIC"
