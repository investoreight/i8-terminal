from typing import Dict, List, Tuple

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice


def get_metrics_conditions_dict() -> Dict[str, str]:
    df = get_all_metrics_df()[["metric_name", "screening_conditions"]]
    return dict([(i, j) for i, j in zip(df.metric_name, df.screening_conditions)])


class ConditionParamType(AutoCompleteChoice):
    name = "condition"

    def get_suggestions(self, keyword: str, pre_populate: bool = True, metric: str = None) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.metrics_conditions = get_metrics_conditions_dict()
        self.set_choices([(c, "") for c in self.metrics_conditions.get(metric, "").split(",")])

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "CONDITION"
