from typing import Optional

import click
import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.screen import screen
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.metric_view_param_type import MetricViewParamType


def prepare_losers_df(view_name: Optional[str]) -> Optional[pd.DataFrame]:
    companies = investor8_sdk.ScreenerApi().get_top_stocks("losers")
    if companies is None:
        return None
    companies_data_df = pd.DataFrame([m.to_dict() for m in companies])
    if view_name:
        metrics_data_df = get_current_metrics_df(
            ",".join(list(companies_data_df["ticker"])), APP_SETTINGS["metric_view"][view_name]["metrics"]
        )
        metrics_formatted_df = prepare_current_metrics_formatted_df(metrics_data_df, "console")
    return companies_data_df


@screen.command()
@click.option(
    "--view_name", "view_name", "-v", type=MetricViewParamType(), help="Metric view name in configuration file."
)
@pass_command
def losers(view_name: Optional[str]) -> None:
    """
    Lists today loser companies.

    Examples:

    `i8 screen losers`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        df = prepare_losers_df(view_name)
    table = df2Table(df)
    console.print(table)
