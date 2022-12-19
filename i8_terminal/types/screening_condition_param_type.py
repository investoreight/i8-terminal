from typing import List, Tuple

from i8_terminal.types.auto_complete_choice import AutoCompleteChoice
from i8_terminal.types.condition_param_type import ConditionParamType
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.period_param_type import PeriodParamType


class ScreeningConditionParamType(AutoCompleteChoice):
    name = "screeningcondition"

    def __init__(self) -> None:
        self._metric_auto_comp = MetricParamType()
        self._period_auto_comp = PeriodParamType()
        self._condition_auto_comp = ConditionParamType()

    def get_suggestions(
        self, keyword: str, pre_populate: bool = True, param_type: str = None, metric: str = None
    ) -> List[Tuple[str, str]]:
        if param_type == "metric":
            return self._metric_auto_comp.get_suggestions(keyword)
        elif param_type == "period":
            return self._period_auto_comp.get_suggestions(keyword, metric=metric)
        else:
            return self._condition_auto_comp.get_suggestions(keyword, metric=metric)

    def __repr__(self) -> str:
        return "SCREENINGCONDITION"
