from ast import literal_eval
from typing import Dict, List, Optional

import investor8_sdk
import pandas as pd

from i8_terminal.common.metrics import get_metric_info
from i8_terminal.common.stock_info import get_stocks_df
from i8_terminal.common.utils import status
from i8_terminal.i8_exception import I8Exception
from i8_terminal.service_result.column_info import ColumnInfo
from i8_terminal.service_result.columns_context import ColumnsContext
from i8_terminal.service_result.metrics_current_result import MetricsCurrentResult
from i8_terminal.services.metrics import get_current_metrics

RELATIVE_PERIOD_TYPES: Dict[str, str] = {
    "D": ".d",
    "R": ".r",
    "FY": ".fy",
    "Q": ".q",
}


@status()
def search(
    conditions: List[str], metrics: str, sort_by: Optional[str] = None, sort_order: Optional[str] = None
) -> MetricsCurrentResult:
    max_count = 20
    for index, condition in enumerate(conditions):
        condition_parts = condition.split(":")
        metric = condition_parts[0]
        metric_parts = metric.split(".")
        if len(metric_parts) == 1:
            metric_default_period_type = get_metric_info(metric_parts[0])["default_period_type"]
            period_type = RELATIVE_PERIOD_TYPES.get(metric_default_period_type, "")
            metric_new = f"{metric}{period_type}"
            conditions[index] = conditions[index].replace(metric, metric_new)
    if not sort_by:
        sort_by = metrics.split(",")[0]
    tickers_list = investor8_sdk.ScreenerApi().search(
        conditions=",".join(conditions), order_by=sort_by, order_direction=sort_order or "desc"
    )

    return get_current_metrics(",".join(tickers_list[:max_count]), metrics)
