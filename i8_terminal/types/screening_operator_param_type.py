from typing import Dict, List, Tuple

from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice

SCREENING_OPERATORS: Dict[str, List[Tuple[str, str]]] = {
    "Numeric": [
        ("gt", "greater than"),
        ("lt", "less than"),
        ("bw", "between"),
    ],
    "Non-Numeric": [
        ("eq", "equal"),
    ],
}


def get_metrics_data_format_dict() -> Dict[str, str]:
    df = get_all_metrics_df()[["metric_name", "data_format"]]
    return dict([(i, j) for i, j in zip(df.metric_name, df.data_format)])


class ScreeningOperatorParamType(AutoCompleteChoice):
    name = "screeningoperator"
    metrics_default_pt: Dict[str, str] = {}

    def get_suggestions(self, keyword: str, pre_populate: bool = True, metric: str = None) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.metrics_data_formats = get_metrics_data_format_dict()
        self.set_choices(
            SCREENING_OPERATORS.get(
                "Numeric"
                if self.metrics_data_formats.get(metric, "str") in ["float", "int", "unsigned_int"]  # type: ignore
                else "Non-Numeric"
            )
        )  # type: ignore

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "SCREENINGOPERATOR"
