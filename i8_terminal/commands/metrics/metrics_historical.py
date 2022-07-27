from pydoc import locate
from typing import Any, Dict, List

import click
import investor8_sdk
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame
from plotly.subplots import make_subplots
from rich.console import Console

from i8_terminal.app.layout import get_plot_default_layout
from i8_terminal.app.plot_server import serve_plot
from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import get_click_command_path, pass_command
from i8_terminal.common.layout import df2Table, format_metrics_df
from i8_terminal.common.stock_info import validate_tickers
from i8_terminal.common.utils import PlotType
from i8_terminal.types.chart_param_type import ChartParamType
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.output_param_type import OutputParamType
from i8_terminal.types.ticker_param_type import TickerParamType


def get_historical_metrics_df(
    tickers: List[str],
    metrics: List[str],
) -> DataFrame:
    historical_metrics = investor8_sdk.MetricsApi().get_historical_metrics(
        symbols=",".join(tickers), metrics=",".join(metrics), from_period_offset=-10, to_period_offset=0
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
    df.rename(columns={"display_name": "Metric", "Value": "value"}, inplace=True)
    df["value"] = df.apply(
        lambda metric: locate(metric.data_format)(locate("float")(metric.value) if metric.data_format == "int" else metric.value), axis=1  # type: ignore
    )
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

    for metric, metric_df in df.groupby("Metric", sort=False):
        metric_idx = metrics.index(metric)
        for ticker, ticker_df in metric_df.sort_values(["PeriodDateTime"]).groupby("Ticker"):
            idx = tickers.index(ticker)
            if chart_type == "bar":
                fig.add_trace(
                    go.Bar(
                        x=ticker_df["Period"],
                        y=ticker_df["value"],
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
                        y=ticker_df["value"],
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

    fig.update_traces(hovertemplate="%{y} %{x}")
    df["Reversed Period"] = df.apply(lambda row: f"{row.Period.split(' ')[1]} {row.Period.split(' ')[0]}", axis=1)
    sorted_periods = [
        f"{reversed_period.split(' ')[1]} {reversed_period.split(' ')[0]}"
        for reversed_period in sorted(set(df["Reversed Period"]))
    ]
    fig.update_xaxes(
        rangeslider_visible=False,
        spikemode="across",
        spikesnap="cursor",
        categoryorder="array",
        categoryarray=sorted_periods,
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
@click.option(
    "--tickers",
    "-k",
    type=TickerParamType(),
    required=True,
    callback=validate_tickers,
    help="Comma-separated list of tickers.",
)
@click.option(
    "--metrics",
    "-m",
    type=MetricParamType(),
    default="pe_ratio_ttm",
    help="Comma-separated list of daily metrics.",
)
@click.option(
    "--output",
    "-o",
    type=OutputParamType(),
    default="terminal",
    help="Output can be terminal or plot type.",
)
@click.option(
    "--plot_type",
    "-p",
    type=ChartParamType([("bar", "Bar chart"), ("line", "Line chart")]),
    default="line",
    help="Plot can be bar or line chart.",
)
@pass_command
def historical(
    ctx: click.Context,
    tickers: str,
    metrics: str,
    output: str,
    plot_type: str,
) -> None:
    """
    Compares and plots daily metrics of given companies. TICKERS is a comma-separated list of tickers.

    Examples:

    `i8 metrics historical --metrics price_to_earnings --period 5Y --tickers AMD,INTC,QCOM`
    """
    metrics_list = metrics.replace(" ", "").split(",")
    if not output in ["terminal", "plot"]:
        click.echo(click.style(f"`{output}` is not valid output type.", fg="yellow"))
        return
    if output == "plot" and len(metrics_list) > 2:
        click.echo(click.style("For the `plot` output type you can enter up to only two metrics.", fg="yellow"))
        return
    command_path_parsed_options_dict = {
        "--tickers": tickers,
        "--metrics": metrics,
        "--output": output,
        "--plot_type": plot_type,
    }
    command_path = get_click_command_path(ctx, command_path_parsed_options_dict)
    tickers_list = tickers.replace(" ", "").upper().split(",")
    if len(tickers_list) > 5:
        click.echo(click.style("You can enter up to 5 tickers.", fg="yellow"))
        return
    if not plot_type in ["bar", "line"]:
        click.echo(click.style(f"`{plot_type}` is not valid chart type.", fg="yellow"))
        return
    cmd_context = {
        "command_path": command_path,
        "tickers": tickers_list,
        "plot_type": PlotType.CHART.value,
    }

    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        df = get_historical_metrics_df(tickers_list, metrics_list)
        if output == "plot":
            cmd_context["plot_title"] = f"Historical {' and '.join(list(set(df['Metric'])))}"
            status.update("Generating plot...")
            fig = create_fig(df, cmd_context, tickers_list, plot_type)

    if output == "plot":
        serve_plot(fig, cmd_context)
        return

    columns_justify: Dict[str, Any] = {}
    for metric_display_name, metric_df in df.groupby("Metric"):
        columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
    formatted_df = (
        format_metrics_df(df, "console")
        .pivot(index=["Ticker", "Period"], columns="Metric", values="value")
        .reset_index()
    )
    formatted_df["reversed_period"] = formatted_df.apply(
        lambda row: f"{row.Period.split(' ')[1]} {row.Period.split(' ')[0]}", axis=1
    )
    formatted_df.sort_values(["Ticker", "reversed_period"], ascending=False, inplace=True)
    formatted_df.drop(columns=["reversed_period"], inplace=True)
    table = df2Table(
        formatted_df,
        columns_justify=columns_justify,
    )
    console.print(table)
