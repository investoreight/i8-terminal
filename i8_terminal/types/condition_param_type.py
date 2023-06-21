import json
from typing import Dict, List, Tuple

from i8_terminal.common.formatting import format_number_v2
from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice

PERIOD_TYPES: Dict[str, str] = {
    "fy": "mry",
    "q": "mrq",
    "ttm": "ttm",
    "ytd": "ytd",
    "d": "d",
    "r": "r",
    "mry": "mry",
    "mrq": "mrq",
}


def get_metrics_conditions_dict() -> Dict[str, str]:
    df = get_all_metrics_df()[["metric_name", "screening_bounds"]]
    return dict([(i, j) for i, j in zip(df.metric_name, df.screening_bounds)])


def get_metrics_default_period_types_dict() -> Dict[str, str]:
    df = get_all_metrics_df()[["metric_name", "period_type_default"]]
    return dict([(i, j) for i, j in zip(df.metric_name, df.period_type_default)])


def get_metrics_data_format_dict() -> Dict[str, str]:
    df = get_all_metrics_df()[["metric_name", "data_format"]]
    return dict([(i, j) for i, j in zip(df.metric_name, df.data_format)])


def get_metrics_screening_categories_dict() -> Dict[str, str]:
    df = get_all_metrics_df()[["metric_name", "screening_categories"]]
    return dict([(i, j) for i, j in zip(df.metric_name, df.screening_categories)])


class ConditionParamType(AutoCompleteChoice):
    name = "condition"

    def get_suggestions(
        self, keyword: str, pre_populate: bool = True, metric: str = None, period: str = None, value_field: str = None
    ) -> List[Tuple[str, str]]:
        if not self.is_loaded:
            self.metrics_conditions = get_metrics_conditions_dict()
            self.metrics_default_period_types = get_metrics_default_period_types_dict()
            self.metrics_data_format = get_metrics_data_format_dict()
            self.metrics_screening_categories = get_metrics_screening_categories_dict()
        metric_screening_bounds_dict = json.loads(
            self.metrics_conditions.get(metric, "").replace("'", '"')  # type: ignore
        )
        if value_field in ["overall_rank", "spx_rank", "dow_rank", "sector_rank", "industry_rank"]:
            self.set_choices([("5", ""), ("10", ""), ("20", ""), ("50", ""), ("100", ""), ("500", ""), ("1000", "")])
        elif value_field in [
            "overall_percentile",
            "nasdaq_percentile",
            "spx_percentile",
            "sector_percentile",
            "industry_percentile",
            "dow_percentile",
        ]:
            self.set_choices([("1", ""), ("3", ""), ("5", ""), ("10", ""), ("20", ""), ("50", "")])
        else:
            if self.metrics_data_format.get(metric, "") == "categorical":  # type: ignore
                metric_screening_categories = json.loads(
                    self.metrics_screening_categories.get(metric, "").replace("'", '"')  # type: ignore
                )
                self.set_choices(
                    [
                        (
                            c.get("category_name", ""),
                            c.get("category_display_name", ""),
                        )
                        for c in metric_screening_categories
                    ]
                )
            else:
                self.set_choices(
                    [
                        (
                            str(c),
                            format_number_v2(c, percision=1 if c < 1000 else 0, humanize=False if c < 1000 else True),
                        )  # type: ignore
                        for c in metric_screening_bounds_dict.get(
                            PERIOD_TYPES.get(period, "mrq")
                            if period
                            else self.metrics_default_period_types.get(metric, "mrq"),  # type: ignore
                            "",
                        )
                    ]
                )

        if pre_populate and keyword.strip() == "":
            return self._choices[: self.size]
        return self.search_keyword(keyword)

    def __repr__(self) -> str:
        return "CONDITION"
