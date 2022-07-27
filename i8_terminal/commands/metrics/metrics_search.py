from typing import Any, Dict, Optional

import click
from pandas import DataFrame
from rich.console import Console

from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.common.metrics import get_all_metrics_df


def search_metrics_df(keyword: str) -> Optional[DataFrame]:
    keyword = keyword.lower()
    metrics_df = get_all_metrics_df()
    metrics_df["lower_display_name"] = metrics_df["display_name"].str.lower()
    result = metrics_df[
        metrics_df["metric_name"].str.contains(keyword) | metrics_df["lower_display_name"].str.contains(keyword)
    ]
    if result.empty:
        return None
    return result


def format_metrics_df(df: DataFrame) -> DataFrame:
    formatters: Dict[str, Any] = {}
    col_names = {
        "metric_name": "Metric Name",
        "display_name": "Display Name",
        "unit": "Unit",
        "type": "Type",
        "display_format": "Display Format",
        "data_format": "Data Format",
        "period_type_default": "Default Period Type",
    }
    return format_df(df, col_names, formatters)


@metrics.command()
@click.option("--keyword", "-k", required=True, help="Keyword can be metric name.")
@pass_command
def search(keyword: str) -> None:
    """
    Searches and shows all metrics that match with the given KEYWORD.

    Examples:

    `i8 metrics search --keyword return`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = search_metrics_df(keyword)
    if df is None:
        console.print(f"No metrics found for keyword '{keyword}'", style="yellow")
        return
    df_formatted = format_metrics_df(df)
    table = df2Table(df_formatted)
    console.print(table)
