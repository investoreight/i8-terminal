from typing import Any, List, Optional

import plotly.express as px
from pandas import DataFrame

from i8_terminal.common.formatting import color
from i8_terminal.service_result.columns_context import ColumnsContext
from i8_terminal.service_result.service_result import ServiceResult


class EarningsListResult(ServiceResult):
    def __init__(self, data: DataFrame, columns_context: ColumnsContext):
        super().__init__(data, columns_context)

    def __repr__(self) -> str:
        return repr(self._df.head(2))

    def __create_plot_traces(self, df: DataFrame, column: str, beat_color: str) -> List[Any]:
        fig_traces = []

        fig = px.bar(
            df,
            x="period",
            y=column,
            category_orders={"period": df["period"]},
            color=beat_color,
            color_discrete_map={"Yes": color.i8_green.value, "No": color.i8_red.value},
            labels={"eps_beat_?": "Beat?", "eps_actual": "EPS $", "period": ""},
        )

        fig.update_layout(legend_title_text="EPS Beat?")
        fig.update_layout(title="EPS per Quarter", font=dict(color=color.i8_dark.value))
        for trace in range(len(fig["data"])):
            fig_traces.append(fig["data"][trace])
        return fig_traces

    def __add_traces_to_fig(self, traces: List[Any], fig: Any, row: int, col: int) -> Any:
        for trace in traces:
            fig.append_trace(trace, row=row, col=col)
        return fig

    def to_plot(self, x: str = None, y: List[str] = None, kind: str = "bar") -> Any:
        if x is None:
            x = "period"
        if y is None:
            y = ["eps_consensus", "eps_actual"]
        return self._to_plot(x, y, kind)

    def to_xlsx(self, path: str, formatter: Optional[str] = None, styler: Optional[str] = None) -> None:
        df = self.to_df()
        df.to_excel(path)
