from i8_terminal.api.service_result import ServiceResult
from i8_terminal.common.layout import format_df
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.formatting import color

import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame
from plotly.subplots import make_subplots


class EarningsListResult(ServiceResult):
    
    def __init__(self, data, context=None):
        super().__init__(data, context)


    def _format_df(self, df):
        # TDOO: formatting and styling logic is coupled. They should be decoupled
        target = "store"
        formatters = {
            "actual_report_time": get_formatter("date", target),
            "eps_actual": get_formatter("number", target),
            "eps_ws": get_formatter("number", target),
            "eps_surprise": get_formatter("colorize_number" if target == "console" else "number", target),
            "revenue_actual": get_formatter("financial", target),
            "revenue_ws": get_formatter("financial", target),
            "revenue_surprise": get_formatter("colorize_financial" if target == "console" else "financial", target),
        }
        col_names = {
            "actual_report_time": "Date",
            "period": "Period",
            "call_time": "Call Time",
            "eps_ws": "EPS Estimate",
            "eps_actual": "EPS Actual",
            "eps_surprise": "EPS Surprise",
            "revenue_ws": "Revenue Estimate",
            "revenue_actual": "Revenue Actual",
            "revenue_surprise": "Revenue Surprise",
        }
        return format_df(df, col_names, formatters)   

    def __create_plot_traces(self, df, column, beat_color):
        fig_traces = []
        
        fig = px.bar(
            df,
            x="period",
            y=column,
            category_orders={"period": df["period"]},
            color=beat_color,
            color_discrete_map={"Yes": color.i8_green.value, "No": color.i8_red.value},
            labels={"eps_beat_?": "Beat?", "eps_actual": "EPS $", "period": ""})

        fig.update_layout(legend_title_text="EPS Beat?")
        fig.update_layout(title="EPS per Quarter", font=dict(color=color.i8_dark.value))
        for trace in range(len(fig["data"])):
            fig_traces.append(fig["data"][trace])
        return fig_traces

    def __add_traces_to_fig (self, traces, fig, row, col):
        for trace in traces:
            fig.append_trace(trace, row=row, col=col)
        return fig

    def to_plot(self):
        df = self._data
        df['eps_beat_?'] = ["Yes" if x > 0 else "No" for x in df['eps_surprise']]
        df['revenue_beat_?'] = ["Yes" if x > 0 else "No" for x in df['revenue_surprise']]
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
        fig.update_yaxes(title_text="Revenue Surprise (%)",row=2, col=1)
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

