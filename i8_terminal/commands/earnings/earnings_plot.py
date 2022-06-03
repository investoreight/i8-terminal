from typing import Any, Dict, List

import click
import investor8_sdk
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas.core.frame import DataFrame
from rich.console import Console

from i8_terminal.app.layout import get_plot_default_layout
from i8_terminal.app.plot_server import serve_plot
from i8_terminal.commands.earnings import earnings
from i8_terminal.common.cli import get_click_command_path, pass_command
from i8_terminal.common.formatting import format_number
from i8_terminal.common.utils import PlotType
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.ticker_param_type import TickerParamType


def get_historical_earnings_df(tickers: List[str], size: int) -> DataFrame:
    hist_earnings = []
    for tk in tickers:
        hist_earnings.extend(investor8_sdk.EarningsApi().get_historical_earnings(tk, size=size))
    df = pd.DataFrame([h.to_dict() for h in hist_earnings])[
        [
            "ticker",
            "fyq",
            "eps_actual",
            "eps_beat_rate",
            "eps_surprise",
            "eps_ws",
            "revenue_actual",
            "revenue_beat_rate",
            "revenue_surprise",
            "revenue_ws",
        ]
    ]
    df = df.sort_values(by=["ticker", "fyq"], ascending=True).reset_index(drop=True)
    df.fyq = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    df = df.rename(columns={"eps_actual": "Actual", "eps_ws": "Consensus"})
    return df


def create_fig(df: DataFrame, cmd_context: Dict[str, Any]) -> go.Figure:
    fig = px.bar(
        df,
        hover_data=[],
        x="fyq",
        y=["Actual", "Consensus"],
        barmode="group",
        title=cmd_context["plot_title"],
        labels={"value": "Metric Value", "fyq": "Period"},
    )
    fig.update_xaxes(
        tickvals=df.fyq.to_list(),
        ticktext=df.apply(lambda x: x.fyq + f"<br>Beat by ${format_number(x.eps_surprise, decimal=2)}", axis=1),
    )
    fig.update_traces(width=0.3, hovertemplate="%{y}%{_xother}")
    fig.update_layout(
        **get_plot_default_layout(),
        bargap=0.4,
        legend_title_text=None,
        xaxis_title=None,
        margin=dict(b=15, l=70, r=20),
    )

    return fig


@earnings.command()
@click.pass_context
@click.option("--metric", "-m", type=MetricParamType(), default="basiceps", help="Metric name.")
@click.option("--tickers", "-k", type=TickerParamType(), required=True, help="Comma-separated list of tickers.")
@pass_command
def plot(ctx: click.Context, metric: str, tickers: str) -> None:
    """Compare and plot earning metrics of given companies. TICKERS is a comma seperated list of tickers.

    Examples:

    `i8 earnings plot --metric net_ppe --tickers AMD,INTC,QCOM`
    """
    metric = metric.replace(" ", "").upper()
    tickers_list = tickers.replace(" ", "").upper().split(",")
    command_path = get_click_command_path(ctx)
    tickers_list = tickers.replace(" ", "").upper().split(",")
    plot_title = f"{', '.join(tickers_list)} - {metric} Surprise & Estimates by Quarter"
    cmd_context = {
        "command_path": command_path,
        "tickers": tickers_list,
        "plot_title": plot_title,
        "plot_type": PlotType.CHART.value,
    }

    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        df = get_historical_earnings_df(tickers_list, size=4)

        status.update("Generating plot...")
        fig = create_fig(df, cmd_context)

    serve_plot(fig, cmd_context)
