import click
import investor8_sdk
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame
from plotly.subplots import make_subplots
from rich.console import Console

from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.stock_info import validate_ticker
from i8_terminal.types.ticker_param_type import TickerParamType


def get_hist_earnings_df(ticker: str, size: int) -> DataFrame:
    historical_earnings = investor8_sdk.EarningsApi().get_historical_earnings(ticker, size=size)
    historical_earnings = [d.to_dict() for d in historical_earnings]
    df = DataFrame(historical_earnings)
    df["period"] = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    df["eps_beat_?"] = df.apply(lambda x: "✔️" if x.eps_actual >= x.eps_ws else "❌", axis=1)
    df["revenue_beat_?"] = df.apply(lambda x: "✔️" if x.revenue_actual >= x.revenue_ws else "❌", axis=1)
    return df


def get_historical_earnings_df(ticker: str, size: int) -> DataFrame:
    historical_earnings = investor8_sdk.EarningsApi().get_historical_earnings(ticker, size=size)
    historical_earnings = [d.to_dict() for d in historical_earnings]
    df = DataFrame(historical_earnings)
    df["period"] = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    df["eps_beat_?"] = df.apply(lambda x: "Yes" if x.eps_actual >= x.eps_ws else "No", axis=1)
    df["revenue_beat_?"] = df.apply(lambda x: "Yes" if x.revenue_actual >= x.revenue_ws else "No", axis=1)
    df["eps_surprise_%"] = (df["eps_surprise"] / df["eps_ws"]) * 100
    df["revenue_surprise_%"] = (df["revenue_surprise"] / df["revenue_ws"]) * 100
    selected = [
        "id",
        "ticker",
        "period",
        "actual_report_date",
        "fiscal_quarter",
        "eps_actual",
        "eps_ws",
        "eps_surprise",
        "eps_surprise_%",
        "eps_beat_rate",
        "revenue_actual",
        "revenue_ws",
        "revenue_surprise_%",
        "revenue_surprise",
        "revenue_beat_rate",
        "fiscal_quarter",
        "eps_beat_?",
        "revenue_beat_?",
    ]

    return df[selected]


def format_hist_earnings_df(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "actual_report_time": get_formatter("date", target),
        "eps_actual": get_formatter("number", target),
        "eps_ws": get_formatter("number", target),
        "revenue_actual": get_formatter("financial", target),
        "revenue_ws": get_formatter("financial", target),
    }
    col_names = {
        "actual_report_time": "Date",
        "call_time": "Call Time",
        "period": "Period",
        "eps_actual": "EPS Actual",
        "eps_ws": "EPS Cons.",
        "eps_beat_?": "EPS Beat?",
        "revenue_actual": "Revenue Actual",
        "revenue_ws": "Revenue Cons.",
        "revenue_beat_?": "Revenue Beat?",
    }
    return format_df(df, col_names, formatters)


@earnings.command()
@click.option("--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Company ticker.")
@pass_command
def list(ticker: str) -> None:
    """
    Lists upcoming company earnings.

    Examples:

    `i8 earnings list --ticker AAPL`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_hist_earnings_df(ticker, size=10)
    df_formatted = format_hist_earnings_df(df, "console")
    table = df2Table(df_formatted)
    console.print(table)


def visualize_earning(df: DataFrame) -> go.Figure:
    fig = make_subplots(rows=2, cols=2)
    fig_eps_traces = []
    fig_revenue_traces = []
    fig_revenue_surprise_traces = []
    fig_eps_surprise_traces = []

    df = df.sort_values("period", ascending=True)
    fig_eps = px.bar(
        df,
        x="period",
        y="eps_actual",
        category_orders={"period": df["period"]},
        color="eps_beat_?",
        color_discrete_map={"Yes": "#00cc96", "No": "#ef553b"},
        labels={"eps_beat_?": "EPS Beat?", "eps_actual": "EPS $", "period": ""},
    )
    fig_eps.update_layout(legend_title_text="EPS Beat?")
    fig_eps.update_layout(title="EPS per Quarter", font=dict(color="#015560"))
    # fig_eps.update_layout(showlegend=False)
    for trace in range(len(fig_eps["data"])):
        fig_eps_traces.append(fig_eps["data"][trace])

    fig_eps_surprise = px.bar(
        df,
        x="period",
        y="eps_surprise_%",
        category_orders={"period": df["period"]},
        color="eps_beat_?",
        color_discrete_map={"Yes": "#00cc96", "No": "#ef553b"},
        labels={"eps_beat_?": "EPS Beat?", "eps_surprise_%": "EPS Surprise (%)", "period": ""},
    )
    fig_eps_surprise.update_layout(legend_title_text="EPS Beat?")
    fig_eps_surprise.update_layout(title="EPS Surprise per Quarter", font=dict(color="#015560"))
    # fig_eps_surprise.update_layout(showlegend=False)
    for trace in range(len(fig_eps_surprise["data"])):
        fig_eps_surprise_traces.append(fig_eps_surprise["data"][trace])

    fig_revenue = px.bar(
        df.sort_values("actual_report_date"),
        x="period",
        y="revenue_actual",
        color="revenue_beat_?",
        category_orders={"period": df["period"]},
        color_discrete_map={"Yes": "#00cc96", "No": "#ef553b"},
        title="Revenue per quarter",
        labels={"revenue_beat_?": "Revenue Beat?", "revenue_actual": "Revenue $", "period": ""},
    )
    fig_revenue.update_layout(legend_title_text="Revenue Beat?")
    fig_revenue.update_layout(title="Revenue per Quarter", font=dict(color="#015560"))
    # fig_revenue.update_layout(showlegend=False)
    for trace in range(len(fig_revenue["data"])):
        fig_revenue_traces.append(fig_revenue["data"][trace])

    fig_revenue_surprise = px.bar(
        df,
        x="period",
        y="revenue_surprise_%",
        category_orders={"period": df["period"]},
        color="revenue_beat_?",
        color_discrete_map={"Yes": "#00cc96", "No": "#ef553b"},
        labels={"revenue_beat_?": "Revenue Beat?", "revenue_surprise_%": "Revenue Surprise (%)", "period": ""},
    )
    fig_revenue_surprise.update_layout(legend_title_text="Revenue Beat?")
    fig_revenue_surprise.update_layout(title="Revenue Surprise per Quarter", font=dict(color="#015560"))
    # fig_revenue_surprise.update_layout(showlegend=False)
    for trace in range(len(fig_revenue_surprise["data"])):
        fig_revenue_surprise_traces.append(fig_revenue_surprise["data"][trace])

    for traces in fig_revenue_traces:
        fig.append_trace(traces, row=1, col=1)
    for traces in fig_eps_traces:
        fig.append_trace(traces, row=1, col=2)
    for traces in fig_eps_surprise_traces:
        fig.append_trace(traces, row=2, col=2)
    for traces in fig_revenue_surprise_traces:
        fig.append_trace(traces, row=2, col=1)

    fig.update_yaxes(title_text="Revenue $", row=1, col=1)
    fig.update_yaxes(title_text="EPS $", row=1, col=2)
    fig.update_yaxes(title_text="Revenue Surprise (%)", range=[-5, 45], row=2, col=1)
    fig.update_yaxes(title_text="EPS Surprise (%)", range=[-5, 45], row=2, col=2)

    fig.update_xaxes(
        categoryorder="array", categoryarray=df["period"], showticklabels=True, row=1, col=1, tickmode="linear"
    )
    fig.update_xaxes(categoryorder="array", categoryarray=df["period"], showticklabels=True, row=1, col=2)
    fig.update_xaxes(categoryorder="array", categoryarray=df["period"], row=2, col=1)
    fig.update_xaxes(categoryorder="array", categoryarray=df["period"], row=2, col=2)

    fig.update_layout(title="Revenue and Earning History", font=dict(color="#015560"))
    fig.update_layout(width=1000, height=600, showlegend=False)
    return fig, fig_eps, fig_revenue, fig_eps_surprise, fig_revenue_surprise
