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
from i8_terminal.types.sort_order_param_type import SortOrderParamType

# def prepare_screen_df(
#     conditions: List[str], metrics: str, sort_by: Optional[str], sort_order: Optional[str]
# ) -> Tuple[List[str], Optional[pd.DataFrame]]:
#     max_count = 20
#     for index, condition in enumerate(conditions):
#         condition_parts = condition.split(":")
#         metric = condition_parts[0]
#         metric_parts = metric.split(".")
#         if len(metric_parts) == 1:
#             metric_default_period_type = get_metric_info(metric_parts[0])["default_period_type"]
#             period_type = RELATIVE_PERIOD_TYPES.get(metric_default_period_type, "")
#             metric_new = f"{metric}{period_type}"
#             conditions[index] = conditions[index].replace(metric, metric_new)
#     if not sort_by:
#         sort_by = metrics.split(",")[0]
#     tickers_list = investor8_sdk.ScreenerApi().search(
#         conditions=",".join(conditions), order_by=sort_by, order_direction=sort_order
#     )
#     screen_df = get_current_metrics_df(",".join(tickers_list[:max_count]), metrics)
#     return tickers_list, screen_df


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


@screen.command()
@click.option(
    "--conditions",
    "conditions",
    "-c",
    required=True,
    type=ScreeningConditionParamType(),
    multiple=True,
    help="Conditions of search.",
)
@click.option(
    "--view_name", "view_name", "-v", type=MetricViewParamType(), help="Metric view name in configuration file."
)
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
@click.option(
    "--sort_order", "sort_order", "-so", type=SortOrderParamType(), help="Order to sort the output by.", default="desc"
)
@click.option("--include_period", "-ip", is_flag=True, default=False, help="Output will contain the periods.")
@pass_command
def search(
    conditions: str,
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
    if view_name:
        metrics = ",".join(get_view_metrics(view_name))

    console = Console()
    try:
        res = screen_search(conditions, metrics, sort_by)
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

    return

    with console.status("Fetching data...", spinner="material"):
        sorted_tickers, df = prepare_screen_df(list(condition), metrics, sort_by, sort_order)  # type: ignore
    if df is None:
        console.print("No data found for the provided screen conditions", style="yellow")
        return
    no_data_metrics = [
        *set(metric.split(".")[0] for metric in set(metrics.split(","))) - set(df["metric_name"])  # type: ignore
    ]
    for m in no_data_metrics:
        console.print(f"\nNo data found for metric {m} with selected tickers", style="yellow")
    columns_justify: Dict[str, Any] = {}
    df["display_name"] = df.apply(
        lambda metric: f'{metric["display_name"]} - {metric["input_metric"].split(".")[-1].upper()}'
        if len(metric["input_metric"].split(".")) > 1
        else metric["display_name"],
        axis=1,
    )
    metric_names: List[str] = []
    if include_period:
        period_rows = []
        for index, row in df.iterrows():
            if row["display_format"] not in ["str"]:
                metric_names.append(row["display_name"])
                period_rows.append(
                    {
                        "Ticker": row["Ticker"],
                        "metric_name": row["metric_name"],
                        "input_metric": row["input_metric"],
                        "value": row["period"],
                        "display_name": f"{row['display_name']} (Period)",
                        "data_format": "str",
                        "display_format": "str",
                    }
                )
        df = pd.concat([pd.DataFrame(period_rows), df], ignore_index=True, axis=0)
    if export_path:
        if export_path.split(".")[-1] == "html":
            for metric_display_name, metric_df in df.groupby("display_name"):
                columns_justify[metric_display_name] = (
                    "left" if metric_df["display_format"].values[0] == "str" else "right"
                )
            df_result = sort_by_tickers(prepare_current_metrics_formatted_df(df, "console"), sorted_tickers)
            if include_period:
                df_result = reindex_df(df_result, metric_names)
            table = df2Table(
                df_result,
                columns_justify=columns_justify,
            )
            export_to_html(table, export_path)
            return
        df_result = sort_by_tickers(prepare_current_metrics_formatted_df(df, "store"), sorted_tickers)
        if include_period:
            df_result = reindex_df(df_result, metric_names)
        export_data(
            df_result,
            export_path,
            column_width=18,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
    else:
        for metric_display_name, metric_df in df.groupby("display_name"):
            columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
        df_result = sort_by_tickers(prepare_current_metrics_formatted_df(df, "console"), sorted_tickers)
        if include_period:
            df_result = reindex_df(df_result, metric_names)
        table = df2Table(
            df_result,
            columns_justify=columns_justify,
        )
        console.print(table)
