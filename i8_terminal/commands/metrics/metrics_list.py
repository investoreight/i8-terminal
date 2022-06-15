from typing import Any, Dict, Optional

import click
import investor8_sdk
import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table

from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table, format_metrics_df
from i8_terminal.common.utils import export_data
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.ticker_param_type import TickerParamType

from i8_terminal.common.metrics import get_current_metrics_df, prepare_current_metrics_formatted_df  # isort:skip


def render_metrics_table(tickers: str, metricsList: str) -> Optional[Table]:
    console = Console()
    metrics = investor8_sdk.MetricsApi().get_current_metrics(
        symbols=tickers,
        metrics=metricsList,
    )
    if metrics.data is None:
        return None
    metrics_data_df = pd.DataFrame([m.to_dict() for m in metrics.data])
    metrics_data_df.rename(columns={"metric": "metric_name", "symbol": "Ticker"}, inplace=True)
    metrics_metadata_df = pd.DataFrame([m.to_dict() for m in metrics.metadata])
    metrics_df = pd.merge(metrics_data_df, metrics_metadata_df, on="metric_name").replace("string", "str")
    metrics_df_formatted = format_metrics_df(metrics_df, "console")
    for m in [*set(metricsList.split(",")) - set(metrics_df_formatted["metric_name"])]:
        console.print(f"\nNo data found for metric {m} with selected tickers", style="yellow")
    columns_justify: Dict[str, Any] = {}
    for metric_display_name, metric_df in metrics_df_formatted.groupby("display_name"):
        columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
    metrics_stocks_df = (
        metrics_df_formatted.pivot(index="Ticker", columns="display_name", values="value")
        .reset_index(level=0)
        .reindex(np.insert(metrics_df["display_name"].unique(), 0, "Ticker"), axis=1)
    )
    return df2Table(metrics_stocks_df, columns_justify=columns_justify)


@metrics.command()
@click.option("--tickers", "-k", type=TickerParamType(), required=True, help="Comma-separated list of tickers.")
@click.option(
    "--metrics",
    "-m",
    type=MetricParamType(),
    default="pe_ratio_ttm",
    help="Comma-separated list of daily metrics.",
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def list(tickers: str, metrics: str, export_path: Optional[str]) -> None:
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = get_current_metrics_df(tickers, metrics)
    if df is None:
        console.print("No data found for metrics with selected tickers", style="yellow")
    else:
        for m in [*set(metrics.split(",")) - set(df["metric_name"])]:
            console.print(f"\nNo data found for metric {m} with selected tickers", style="yellow")
        if export_path:
            export_data(
                prepare_current_metrics_formatted_df(df, "store"),
                export_path,
                column_width=18,
                column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
            )
        else:
            columns_justify: Dict[str, Any] = {}
            for metric_display_name, metric_df in df.groupby("display_name"):
                columns_justify[metric_display_name] = (
                    "left" if metric_df["display_format"].values[0] == "str" else "right"
                )
            table = df2Table(prepare_current_metrics_formatted_df(df, "console"), columns_justify=columns_justify)
            console.print(table)
