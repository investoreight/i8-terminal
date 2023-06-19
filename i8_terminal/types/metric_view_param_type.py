from typing import List, Tuple

import investor8_sdk
import pandas as pd

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_metric_view_names() -> List[Tuple[str, str]]:
    results = investor8_sdk.MetricsApi().get_list_metric_views()
    df = pd.DataFrame([d.to_dict() for d in results])[["view_name", "display_name"]]
    return list(df.to_records(index=False))


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
