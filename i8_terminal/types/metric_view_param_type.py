from typing import List, Tuple

from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_metric_view_names() -> List[Tuple[str, str]]:
    return [(view_name, "") for view_name in APP_SETTINGS["metric_view"]]


class MetricViewParamType(AutoCompleteChoice):
    name = "metricview"

    def get_suggestions(self, keyword: str, pre_populate: bool = True) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.set_choices(get_metric_view_names())

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "METRICVIEW"
