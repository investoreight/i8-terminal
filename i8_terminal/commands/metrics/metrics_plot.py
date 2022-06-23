from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import click
import investor8_sdk
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from click.types import DateTime
from pandas import DataFrame
from plotly.subplots import make_subplots
from rich.console import Console

from i8_terminal.app.layout import get_plot_default_layout
from i8_terminal.app.plot_server import serve_plot
from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import get_click_command_path, pass_command
from i8_terminal.common.metrics import get_period_start_date
from i8_terminal.common.utils import PlotType
from i8_terminal.types.chart_param_type import ChartParamType
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.period_type_param_type import PeriodTypeParamType
from i8_terminal.types.price_period_param_type import PricePeriodParamType
from i8_terminal.types.ticker_param_type import TickerParamType


def get_historical_metrics_df(
    tickers: List[str],
    metrics: List[str],
    period: str,
    period_type: str,
    from_date: Optional[str],
    to_date: Optional[str],
) -> DataFrame:
    metrics_period_type = (
        [f"{metric}.{period_type}" for metric in metrics] if period_type else [metric for metric in metrics]
    )
    if from_date:
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        historical_metrics = investor8_sdk.MetricsApi().get_historical_metrics(
            symbols=",".join(tickers),
            metrics=",".join(metrics_period_type),
            from_date=from_date,
            to_date=to_date,
        )
    else:
        from_date = get_period_start_date(period)
        to_date = datetime.now().strftime("%Y-%m-%d")
        historical_metrics = investor8_sdk.MetricsApi().get_historical_metrics(
            symbols=",".join(tickers),
            metrics=",".join(metrics_period_type),
            from_date=from_date,
            to_date=to_date,
        )
    df = pd.DataFrame.from_records(
        [
            (ticker, metric, period_value.period, period_value.period_date_time, period_value.value)
            for ticker, metric_dict in historical_metrics.data.items()
            for metric, period_value_list in metric_dict.items()
            for period_value in period_value_list
        ],
        columns=["Ticker", "metric_name", "Period", "PeriodDateTime", "Value"],
    )
    metadata_df = pd.DataFrame([h.to_dict() for h in historical_metrics.metadata])
    df = pd.merge(df, metadata_df, on="metric_name")
    df.rename(columns={"display_name": "Metric"}, inplace=True)
    df["Value"] = df["Value"].astype(df["data_format"].values[0])
    return df


def create_fig(
    df: DataFrame,
    cmd_context: Dict[str, Any],
    tickers: List[str],
    chart_type: str,
) -> go.Figure:
    vertical_spacing = 0.02
    layout = dict(
        title=cmd_context["plot_title"],
        autosize=True,
        hovermode="closest",
        legend=dict(font=dict(size=11), orientation="v"),
        margin=dict(b=20, l=50, r=65),
    )
    metrics = list(set(df["Metric"]))
    rows_num = len(metrics)

    if rows_num == 2:
        row_width = [0.5, 0.5]
    else:
        row_width = [1]

    fig = make_subplots(
        rows=rows_num,
        cols=1,
        shared_xaxes=False if len(list(set(df["default_period_type"]))) > 1 else True,
        vertical_spacing=vertical_spacing,
        row_width=row_width,
    )

    for metric, metric_df in df.groupby("Metric"):
        metric_idx = metrics.index(metric)
        for ticker, ticker_df in metric_df.sort_values(["PeriodDateTime"]).groupby("Ticker"):
            idx = tickers.index(ticker)
            if chart_type == "bar":
                fig.add_trace(
                    go.Bar(
                        x=ticker_df["Period"],
                        y=ticker_df["Value"],
                        name=ticker,
                        marker=dict(color=px.colors.qualitative.Plotly[idx]),
                        legendgroup=f"group{idx}",
                        showlegend=True if metrics.index(metric) == 0 else False,
                    ),
                    row=metrics.index(metric) + 1,
                    col=1,
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=ticker_df["Period"],
                        y=ticker_df["Value"],
                        name=ticker,
                        marker=dict(color=px.colors.qualitative.Plotly[idx]),
                        legendgroup=f"group{idx}",
                        showlegend=True if metrics.index(metric) == 0 else False,
                    ),
                    row=metrics.index(metric) + 1,
                    col=1,
                )
        if len(metrics) > 1:
            fig["layout"][f"xaxis{metric_idx+1}"]["dtick"] = round(len(metric_df["Period"]) / 10)

    fig.update_traces(hovertemplate="%{y:.2f} %{x}")
    fig.update_xaxes(
        rangeslider_visible=False,
        spikemode="across",
        spikesnap="cursor",
    )

    fig.update_layout(
        **layout,
        **get_plot_default_layout(),
        legend_title_text=None,
        xaxis_title=None,
        yaxis_title=None,
    )

    # Add yaxis titles
    for idx, r in enumerate(np.cumsum(row_width)[::-1]):
        fig["layout"][f"yaxis{idx+1}"]["title"] = metrics[idx]

    fig.update_annotations(
        dict(
            font_size=10,
            font_color="#525252",
        )
    )
    fig.update_yaxes(
        title_font_size=10,
    )

    return fig


@metrics.command()
@click.pass_context
@click.option("--tickers", "-k", type=TickerParamType(), required=True, help="Comma-separated list of tickers.")
@click.option(
    "--metrics",
    "-m",
    type=MetricParamType(),
    default="pe_ratio_ttm",
    help="Comma-separated list of daily metrics.",
)
@click.option(
    "--period",
    "-p",
    type=PricePeriodParamType(),
    default="1Y",
    help="Historical price period.",
)
@click.option(
    "--period_type",
    "-m",
    type=PeriodTypeParamType(),
    help="Period by which you want to view the report. Possible values are `FY` for yearly, `Q` for quarterly, and `TTM` for TTM reports.",
)
@click.option("--from_date", "-f", type=DateTime(), help="Histotical financials from date.")
@click.option("--to_date", "-t", type=DateTime(), help="Histotical financials to date.")
@click.option(
    "--chart_type",
    "-c",
    type=ChartParamType([("bar", "Bar chart"), ("line", "Line chart")]),
    default="line",
    help="Chart can be bar or line chart.",
)
@pass_command
def plot(
    ctx: click.Context,
    tickers: str,
    metrics: str,
    chart_type: str,
    period: str,
    period_type: str,
    from_date: Optional[datetime],
    to_date: Optional[datetime],
) -> None:
    """
    Compares and plots daily metrics of given companies. TICKERS is a comma-separated list of tickers.

    Examples:

    `i8 metrics plot --metrics price_to_earnings --period 5Y --tickers AMD,INTC,QCOM`
    """
    period = period.replace(" ", "").upper()
    metrics_list = metrics.replace(" ", "").split(",")
    if len(metrics_list) > 2:
        click.echo("You can enter up to 2 daily metrics.")
        return
    command_path_parsed_options_dict = {}
    if from_date:
        command_path_parsed_options_dict["--from_date"] = from_date.strftime("%Y-%m-%d")
    if to_date:
        command_path_parsed_options_dict["--to_date"] = to_date.strftime("%Y-%m-%d")
    command_path = get_click_command_path(ctx, command_path_parsed_options_dict)
    tickers_list = tickers.replace(" ", "").upper().split(",")
    if len(tickers_list) > 5:
        click.echo("You can enter up to 5 tickers.")
        return
    if not chart_type in ["bar", "line"]:
        click.echo(f"`{chart_type}` is not valid chart type.")
        return
    cmd_context = {
        "command_path": command_path,
        "tickers": tickers_list,
        "plot_type": PlotType.CHART.value,
    }

    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        df = get_historical_metrics_df(
            tickers_list, metrics_list, period, period_type, cast(str, from_date), cast(str, to_date)
        )
        cmd_context["plot_title"] = f"Historical {' and '.join(list(set(df['Metric'])))}"
        status.update("Generating plot...")
        fig = create_fig(df, cmd_context, tickers_list, chart_type)

    serve_plot(fig, cmd_context)
