from typing import Any, Dict, Optional

import click
from rich.console import Console

from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import is_server_call, pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    get_view_metrics,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.common.stock_info import validate_tickers
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS
from i8_terminal.i8_exception import I8Exception
from i8_terminal.services.metrics import get_current_metrics
from i8_terminal.types.metric_identifier_param_type import MetricIdentifierParamType
from i8_terminal.types.metric_view_param_type import MetricViewParamType
from i8_terminal.types.ticker_param_type import TickerParamType


@metrics.command()
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
    type=MetricIdentifierParamType(),
    help="Comma-separated list of daily metrics.",
)
@click.option(
    "--view_name", "view_name", "-v", type=MetricViewParamType(), help="Metric view name in configuration file."
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def current(tickers: str, metrics: str, view_name: Optional[str], export_path: Optional[str]) -> None:
    """
    Lists the given metrics for a given list of companies. TICKERS is a comma-separated list of tickers.
    METRICS can be in the below format:
    {metric}.{optional period}

    Available periods:
        q = most recent quarter,
        fy = most recent fiscal year,
        ttm = trailing 12 months,
        ytd = year to date,
        p = default period type

    Examples:

    `i8 metrics current --metrics total_revenue.q,net_income.fy,close.d,total_revenue --tickers AMD,INTC,QCOM`
    """  # noqa: E501
    console = Console()
    if not metrics and not view_name:
        console.print("The 'metrics' or 'view_name' parameter must be provided", style="yellow")
        return
    if view_name and metrics:
        console.print(
            "The 'metrics' or 'view_name' options are mutually exclusive. Provide a value only for one of them.",
            style="yellow",
        )
        return
    if view_name:
        metrics = ",".join(get_view_metrics(view_name))

    try:
        res = get_current_metrics(tickers, metrics)
        if is_server_call():
            return res
    except I8Exception as ex:
        if is_server_call():
            raise
        else:
            console.print(str(ex))

    info = res.get_info()
    if info:
        console.print(info)

    if export_path:
        extension = export_path.split(".")[-1]
        if extension == "html":
            res.to_html(export_path)
        elif extension == "xlsx":
            res.to_xlsx(export_path)
        elif extension == "csv":
            res.to_csv(export_path)
        else:
            console.print("Unknown export extension!")
    else:
        res.to_console(format="humanize")
