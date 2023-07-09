from typing import Any, Dict, Optional

import click
from rich.console import Console

from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import is_server_call, pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.common.stock_info import validate_tickers
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS
from i8_terminal.i8_exception import I8Exception
from i8_terminal.services.metrics import get_current_metrics
from i8_terminal.types.metric_identifier_param_type import MetricIdentifierParamType
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
    default="pe_ratio_ttm",
    help="Comma-separated list of daily metrics.",
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def current(tickers: str, metrics: str, export_path: Optional[str]) -> None:
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
