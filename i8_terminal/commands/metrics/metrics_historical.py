from datetime import datetime
from typing import Any, Dict, List, Optional

import arrow
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
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from i8_terminal.app.layout import get_plot_default_layout
from i8_terminal.app.plot_server import serve_plot
from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import get_click_command_path, pass_command
from i8_terminal.common.formatting import data_format_mapper
from i8_terminal.common.layout import df2Table, format_metrics_df
from i8_terminal.common.metrics import (
    add_ticker_rank_to_df,
    get_all_metrics_type_and_data_types_df,
)
from i8_terminal.common.stock_info import get_tickers_list, validate_tickers
from i8_terminal.common.utils import PlotType, reverse_period
from i8_terminal.config import get_table_style
from i8_terminal.types.chart_param_type import ChartParamType
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.output_param_type import OutputParamType
from i8_terminal.types.period_type_param_type import PeriodTypeParamType
from i8_terminal.types.ticker_param_type import TickerParamType


def get_historical_metrics_df(
    tickers: List[str],
    metrics: List[str],
    period_type: Optional[str],
    from_date: Optional[datetime],
    to_date: Optional[datetime],
) -> DataFrame:
    if period_type:
        metrics = [f"{metric}.{period_type}" for metric in metrics]
    if from_date:
        historical_metrics = investor8_sdk.MetricsApi().get_historical_metrics(
            symbols=",".join(tickers),
            metrics=",".join(metrics),
            from_date=from_date.strftime("%Y-%m-%d"),
            to_date=to_date.strftime("%Y-%m-%d") if to_date else arrow.now().datetime.strftime("%Y-%m-%d"),
        )
    elif to_date and not from_date:
        historical_metrics = investor8_sdk.MetricsApi().get_historical_metrics(
            symbols=",".join(tickers),
            metrics=",".join(metrics),
            from_period_offset=-10,
            to_period_offset=0,
            to_date=to_date.strftime("%Y-%m-%d"),
        )
    elif not to_date and not from_date:
        historical_metrics = investor8_sdk.MetricsApi().get_historical_metrics(
            symbols=",".join(tickers),
            metrics=",".join(metrics),
            from_period_offset=-10,
            to_period_offset=0,
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
    df[["data_format", "display_format"]] = df[["data_format", "display_format"]].replace("string", "str")
    df.rename(columns={"display_name": "Metric", "Value": "value"}, inplace=True)
    df["value"] = df.apply(lambda metric: data_format_mapper(metric), axis=1)
    return df


def create_fig(
    df: DataFrame, cmd_context: Dict[str, Any], tickers: List[str], chart_type: str, metrics_type_df: DataFrame
) -> go.Figure:
    vertical_spacing = 0.02
    metrics = list(set(df["Metric"]))
    rows_num = len(metrics)
    row_width = [1] * rows_num
    layout = dict(
        title=cmd_context["plot_title"],
        autosize=False,
        width=846,
        height=400 * rows_num,
        hovermode="closest",
        legend=dict(font=dict(size=11), orientation="v"),
        margin=dict(b=20, l=50, r=65),
    )

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

    sorted_periods = df.sort_values("PeriodDateTime")["Period"].unique()
    sorted_periods_filtered = (
        sorted_periods[:: int(len(sorted_periods) / 10)] if len(sorted_periods) > 10 else sorted_periods
    )  # Get only 10,

    if "fin_metric" in set(metrics_type_df["type"]):
        # Reverse the financials periods. e.g: `FY 2020` will converted to `2020 FY``
        sorted_periods = list(map(reverse_period, sorted_periods))

    fig.update_xaxes(
        rangeslider_visible=False,
        spikemode="across",
        spikesnap="cursor",
        categoryorder="array",
        categoryarray=sorted_periods,
        tickvals=sorted_periods_filtered,
        ticktext=sorted_periods_filtered,
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


def historical_metrics_df2tree(df: DataFrame) -> Tree:
    # If the period type is daily or real-time, the df must be sorted using the PeriodDateTime
    # and if not must be sorted using reversed_period.
    if any(set(["D", "R"]) & set(df["default_period_type"].unique())):
        period_dict = dict(df[["PeriodDateTime", "Period"]].sort_values("PeriodDateTime", ascending=False).values)
        sorted_periods = [period_dict[p] for p in period_dict.keys()]
        df = df.pivot(index=["Metric", "Ticker"], columns="Period", values="value").reset_index()
    else:
        df = df.pivot(index=["Metric", "Ticker"], columns="Period", values="value").reset_index()
        reversed_periods = [reverse_period(p) for p in list(df.columns[2:])]
        reversed_periods.sort(reverse=True)
        sorted_periods = [reverse_period(rp) for rp in reversed_periods]
    col_width = 15
    plot_title = f"Historical {' and '.join(list(set(df['Metric'])))}"
    tree = Tree(Panel(plot_title, width=50))
    # Add header table to tree
    header_table = Table(
        width=55 + (col_width * (len(sorted_periods) - 1)), show_lines=False, show_header=False, box=None
    )
    header_table.add_column(width=15, style="magenta")
    for p in list(df):
        header_table.add_column(width=col_width, justify="right", style="magenta")
    header_table.add_row("Period", *sorted_periods)
    tree.add(header_table)

    table_style = get_table_style("metrics_historical")

    for metric, metric_values in df.groupby("Metric", sort=False):
        metric_branch = tree.add(f"[magenta]{metric}")
        for i, r in metric_values.reset_index().iterrows():
            t = Table(
                width=22 + (col_width * (len(sorted_periods) - 1)),
                show_lines=False,
                show_header=False,
                box=None,
                row_styles=[table_style["row_styles"][i % 2]],
            )
            t.add_column(width=11)
            for period in sorted_periods:
                t.add_column(width=col_width, justify="right")
            t.add_row(r["Ticker"], *[f"{d}" if d is not np.nan else "-" for d in r[sorted_periods].values])
            metric_branch.add(t)

    return tree


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
    help="Output can be terminal or plot.",
)
@click.option(
    "--plot_type",
    "-p",
    type=ChartParamType([("bar", "Bar chart"), ("line", "Line chart")]),
    help="Plot can be bar or line chart.",
)
@click.option("--pivot", "-pv", is_flag=True, default=False, help="Output will be pivot table.")
@click.option(
    "--period_type",
    "-t",
    type=PeriodTypeParamType(),
    help="Period by which you want to view the report. Possible values are `D` for daily, `FY` for yearly, `Q` for quarterly, `TTM` for TTM reports, `YTD` for YTD reports.",  # noqa: E501
)
@click.option("--from_date", "-f", type=DateTime(), help="Histotical metrics from date.")
@click.option("--to_date", "-t", type=DateTime(), help="Histotical metrics to date.")
@pass_command
def historical(
    ctx: click.Context,
    tickers: str,
    metrics: str,
    output: str,
    plot_type: Optional[str],
    pivot: bool,
    period_type: Optional[str],
    from_date: Optional[datetime],
    to_date: Optional[datetime],
) -> None:
    """
    Lists, compares and plots metrics of given companies. TICKERS is a comma-separated list of tickers.

    Examples:

    `i8 metrics historical --metrics net_income --tickers AMD,INTC,QCOM --output plot --plot_type bar --period_type Q`
    `i8 metrics historical --metrics total_revenue,total_assets --tickers AMD,INTC,QCOM --output terminal --period_type FY --pivot`
    """  # noqa: E501
    metrics_list = metrics.replace(" ", "").split(",")
    if output not in ["terminal", "plot"]:
        click.echo(click.style(f"`{output}` is not valid output type.", fg="yellow"))
        return
    command_path_parsed_options_dict = {
        "--tickers": tickers,
        "--metrics": metrics,
        "--output": output,
        "--plot_type": plot_type if plot_type else "line",
    }
    if period_type:
        command_path_parsed_options_dict["--period_type"] = period_type
    if from_date:
        command_path_parsed_options_dict["--from_date"] = from_date.strftime("%Y-%m-%d")
    if to_date:
        command_path_parsed_options_dict["--to_date"] = to_date.strftime("%Y-%m-%d")
    command_path = get_click_command_path(ctx, command_path_parsed_options_dict)
    tickers_list = get_tickers_list(tickers.replace(" ", "").upper())
    if len(tickers_list) > 5:
        click.echo(click.style("You can enter up to 5 tickers.", fg="yellow"))
        return
    if plot_type and plot_type not in ["bar", "line"]:
        click.echo(click.style(f"`{plot_type}` is not valid chart type.", fg="yellow"))
        return
    cmd_context = {
        "command_path": command_path,
        "tickers": tickers_list,
        "plot_type": PlotType.CHART.value,
    }

    metrics_type_df: DataFrame = get_all_metrics_type_and_data_types_df()
    metrics_type_df = metrics_type_df[metrics_type_df["metric_name"].isin(metrics_list)]

    if output == "plot" and "string" in metrics_type_df["data_format"].unique():
        click.echo(
            click.style("Metrics with type `string` cannot be plotted! Select `terminal` output instead.", fg="yellow")
        )
        return

    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        df = get_historical_metrics_df(tickers_list, metrics_list, period_type, from_date, to_date)
        df = df.sort_values(["PeriodDateTime"], ascending=False).groupby(["Ticker", "Metric", "Period"]).head(1)
        if not period_type:
            if len(df["default_period_type"].unique()) > 1:
                console.print(
                    "The `period type` of the provided metrics are not compatible. Make sure the provided metrics have the same period type or specify the period_type parameter. Check `metrics describe` command to find more about metrics.",  # noqa: E501
                    style="yellow",
                )
                return
        if len(df["metric_name"].unique()) < len(metrics_list):
            # If all of the input metrics don't have data in the input period_type
            # (eg. --metrics eps_growth,revenue_actual --period_type FY).
            console.print(
                "The `period type` of the provided metrics are not compatible. Make sure the provided metrics have the same period type or specify the period_type parameter. Check `metrics describe` command to find more about metrics.",  # noqa: E501
                style="yellow",
            )
            return
        if output == "plot" or plot_type:
            cmd_context["plot_title"] = f"Historical {' and '.join(list(set(df['Metric'])))}"
            status.update("Generating plot...")
            fig = create_fig(df, cmd_context, tickers_list, plot_type if plot_type else "line", metrics_type_df)

    if output == "plot" or plot_type:
        serve_plot(fig, cmd_context)
        return
    formatted_df = format_metrics_df(df, "console")
    if pivot:
        tree = historical_metrics_df2tree(formatted_df)
        console.print(tree)
        return
    columns_justify: Dict[str, Any] = {}
    for metric_display_name, metric_df in df.groupby("Metric"):
        columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
    # If the period type is daily or real-time, the df must be sorted using the PeriodDateTime
    # and if not must be sorted using reversed_period.
    if any(set(["D", "R"]) & set(formatted_df["default_period_type"].unique())):
        formatted_df = formatted_df.pivot(
            index=["Ticker", "Period", "PeriodDateTime"], columns="Metric", values="value"
        ).reset_index()
        formatted_df = add_ticker_rank_to_df(formatted_df, tickers_list)
        formatted_df.sort_values(["TickerRank", "PeriodDateTime"], ascending=[True, False], inplace=True)
        formatted_df.drop(columns=["TickerRank", "PeriodDateTime"], inplace=True)
    else:
        formatted_df = formatted_df.pivot(index=["Ticker", "Period"], columns="Metric", values="value").reset_index()
        formatted_df["reversed_period"] = formatted_df.apply(
            lambda row: reverse_period(row.Period),
            axis=1,
        )
        formatted_df = add_ticker_rank_to_df(formatted_df, tickers_list)
        formatted_df.sort_values(["TickerRank", "reversed_period"], ascending=[True, False], inplace=True)
        formatted_df.drop(columns=["TickerRank", "reversed_period"], inplace=True)
    metrics_order = [df.loc[df["metric_name"] == metric]["Metric"].values[0] for metric in metrics_list]
    metrics_order[:0] = ["Ticker", "Period"]
    formatted_df = formatted_df.reindex(columns=metrics_order)
    table = df2Table(
        formatted_df,
        columns_justify=columns_justify,
    )
    console.print(table)
