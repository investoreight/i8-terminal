from typing import Any, Dict, List, Optional, Tuple

import click
import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.screen import screen
from i8_terminal.common.cli import is_server_call, pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    get_metric_info,
    get_view_metrics,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS
from i8_terminal.i8_exception import I8Exception
from i8_terminal.services.screen import search as screen_search
from i8_terminal.types.metric_identifier_param_type import MetricIdentifierParamType
from i8_terminal.types.metric_view_param_type import MetricViewParamType
from i8_terminal.types.screening_condition_param_type import ScreeningConditionParamType
from i8_terminal.types.screening_profile_param_type import ScreeningProfileParamType
from i8_terminal.types.sort_order_param_type import SortOrderParamType


def sort_by_tickers(df: pd.DataFrame, sorted_tickers: List[str]) -> pd.DataFrame:
    sorterIndex = dict(zip(sorted_tickers, range(len(sorted_tickers))))
    df["Rank"] = df["Ticker"].map(sorterIndex)
    df.sort_values("Rank", ascending=True, inplace=True)
    df.drop("Rank", axis=1, inplace=True)
    return df


def reindex_df(df: pd.DataFrame, metrics_include_periods: List[str]) -> pd.DataFrame:
    column_orders = list(df.columns)
    for metric_period in set(metrics_include_periods):
        column_orders.pop(column_orders.index(f"{metric_period} (Period)"))
        column_orders.insert(column_orders.index(metric_period), f"{metric_period} (Period)")
    return df.reindex(columns=column_orders)


def get_screening_profile(profile: str) -> Tuple[List[str], str, str]:
    screening_profile = investor8_sdk.ScreenerApi().get_screening_profile_by_name(profile)
    return screening_profile.conditions.split(","), screening_profile.sort_metric, screening_profile.sort_order


@screen.command()
@click.option("--profile", "profile", "-p", type=ScreeningProfileParamType(), help="Screening profile name.")
@click.option(
    "--conditions",
    "conditions",
    "-c",
    type=ScreeningConditionParamType(),
    multiple=True,
    help="Conditions of search.",
)
@click.option("--view_name", "view_name", "-v", type=MetricViewParamType(), help="Metric view name.")
@click.option(
    "--metrics",
    "metrics",
    "-m",
    type=MetricIdentifierParamType(),
    help="Comma-separated list of daily metrics.",
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@click.option(
    "--sort_by",
    "sort_by",
    "-sb",
    type=MetricIdentifierParamType(),
    help="Metric to sort the output by.",
)
@click.option("--sort_order", "sort_order", "-so", type=SortOrderParamType(), help="Order to sort the output by.")
@click.option("--include_period", "-ip", is_flag=True, default=False, help="Output will contain the periods.")
@pass_command
def search(
    profile: Optional[str],
    conditions: Optional[Tuple[str]],
    view_name: Optional[str],
    metrics: Optional[str],
    export_path: Optional[str],
    sort_by: Optional[str],
    sort_order: Optional[str],
    include_period: bool,
) -> None:
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
    if not conditions and not profile:
        console.print("The 'conditions' or 'profile' parameter must be provided", style="yellow")
        return
    if profile and conditions:
        console.print(
            "The 'conditions' or 'profile' options are mutually exclusive. Provide a value only for one of them.",
            style="yellow",
        )
        return
    if profile and sort_by:
        console.print(
            "The 'sort_by' or 'profile' options are mutually exclusive. Provide a value only for one of them.",
            style="yellow",
        )
        return
    if profile and sort_order:
        console.print(
            "The 'sort_order' or 'profile' options are mutually exclusive. Provide a value only for one of them.",
            style="yellow",
        )
        return
    if not profile and not sort_order:
        sort_order = "desc"
    if view_name:
        metrics = ",".join(get_view_metrics(view_name))

    if profile:
        conds_list, sort_by, sort_order = get_screening_profile(profile)
    else:
        conds_list = conditions.split(",")

    console = Console()
    try:
        res = screen_search(conds_list, metrics, sort_by)
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

    # TODO: implements xlsx and --include_period
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
