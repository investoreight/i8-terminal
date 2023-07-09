from typing import Any, List, Optional

from pandas import DataFrame

from i8_terminal.common.formatting import color
from i8_terminal.service_result.columns_context import ColumnsContext
from i8_terminal.service_result.service_result import ServiceResult


class MetricsCurrentResult(ServiceResult):
    def __init__(self, data: DataFrame, columns_context: ColumnsContext, info: str = ""):
        super().__init__(data, columns_context, info)

    def __repr__(self) -> str:
        return repr(self._df.head(2))

    def to_plot(self, show=False) -> Any:
        return None
