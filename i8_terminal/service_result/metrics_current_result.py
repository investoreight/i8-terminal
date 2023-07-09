from typing import Any, List, Optional

import plotly.express as px
from pandas import DataFrame

from i8_terminal.common.formatting import color
from i8_terminal.service_result.columns_context import ColumnsContext
from i8_terminal.service_result.service_result import ServiceResult


class MetricsCurrentResult(ServiceResult):
    def __init__(self, data: DataFrame, columns_context: ColumnsContext):
        super().__init__(data, columns_context)

    def __repr__(self) -> str:
        return repr(self._df.head(2))
