from typing import Any, List

import pandas as pd
import plotly.express as px
from pandas import DataFrame
from plotly.subplots import make_subplots

from i8_terminal.service_result import ServiceResult
from i8_terminal.common.formatting import color, get_formatter
from i8_terminal.common.layout import format_df
from i8_terminal.config import METRICS_METADATA_PATH


class EarningsListResult(ServiceResult):
    def __init__(self, data: DataFrame, context: Any = None):
        super().__init__(data, context)

    def _format_df(self, df: DataFrame, target: str) -> DataFrame:
        metadata = pd.read_csv(METRICS_METADATA_PATH, delimiter=";")
        formatters = {}
        col_names = {}

        columns = df.columns.to_list()

        for col in columns:
            if col not in list(metadata["metric_name"]):
                continue

            metric = metadata[metadata["metric_name"] == col]
            display_format = metric["display_format"].iloc[0]
            display_name = metric["display_name"].iloc[0]

            if not pd.isna(display_format):
                formatters[col] = get_formatter(display_format, target)

            if not pd.isna(display_name):
                col_names[col] = display_name

        return format_df(df, col_names, formatters)

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

    def to_plot(self) -> Any:
        df = self._data
        df["eps_beat_?"] = ["Yes" if x > 0 else "No" for x in df["eps_surprise"]]
        df["revenue_beat_?"] = ["Yes" if x > 0 else "No" for x in df["revenue_surprise"]]
        fig = make_subplots(rows=2, cols=2)
        fig_eps_traces = self.__create_plot_traces(df, "eps_actual", "eps_beat_?")
        fig_revenue_traces = self.__create_plot_traces(df, "revenue_actual", "revenue_beat_?")
        fig_eps_surprise_traces = self.__create_plot_traces(df, "eps_surprise", "eps_beat_?")
        fig_revenue_surprise_traces = self.__create_plot_traces(df, "revenue_surprise", "revenue_beat_?")

        fig = self.__add_traces_to_fig(fig_revenue_traces, fig, row=1, col=1)
        fig = self.__add_traces_to_fig(fig_eps_traces, fig, row=1, col=2)
        fig = self.__add_traces_to_fig(fig_revenue_surprise_traces, fig, row=2, col=1)
        fig = self.__add_traces_to_fig(fig_eps_surprise_traces, fig, row=2, col=2)

        fig.update_yaxes(title_text="Revenue $", row=1, col=1)
        fig.update_yaxes(title_text="EPS $", row=1, col=2)
        fig.update_yaxes(title_text="Revenue Surprise (%)", row=2, col=1)
        fig.update_yaxes(title_text="EPS Surprise (%)", row=2, col=2)

        fig.update_xaxes(
            categoryorder="array", categoryarray=df["period"], showticklabels=True, row=1, col=1, tickmode="linear"
        )
        fig.update_xaxes(categoryorder="array", categoryarray=df["period"], showticklabels=True, row=1, col=2)
        fig.update_xaxes(categoryorder="array", categoryarray=df["period"], row=2, col=1)
        fig.update_xaxes(categoryorder="array", categoryarray=df["period"], row=2, col=2)

        fig.update_layout(title="Revenue and Earning History", font=dict(color=color.i8_dark.value))
        fig.update_layout(width=1000, height=600, showlegend=False)
        return fig

    def to_csv(self, path: str) -> None:
        self._data.to_csv(path)

    def to_xlsx(self, path: str, formatter=None, styler=None) -> None:
        df = self.to_df()
        df.to_excel(path)
