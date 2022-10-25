from typing import Any, Dict, Optional

import investor8_sdk
import pandas as pd
from rich.table import Table

from i8_terminal.common.layout import df2Table
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.common.utils import export_data, export_to_html
from i8_terminal.config import APP_SETTINGS


def get_top_stocks_df(category: str, index: str, view_name: Optional[str]) -> Optional[pd.DataFrame]:
    metrics = APP_SETTINGS["commands"]["screen_gainers"]["metrics"]
    companies_data = investor8_sdk.ScreenerApi().get_top_stocks(category, index=index)
    if companies_data is None:
        return None
    companies = [company.ticker for company in companies_data]
    if view_name:
        metrics = metrics + "," + APP_SETTINGS["metric_view"][view_name]["metrics"]
    return get_current_metrics_df(",".join(companies), metrics)


def render_top_stocks(df: pd.DataFrame, export_path: Optional[str], ascending: bool = True) -> Optional[Table]:
    columns_justify: Dict[str, Any] = {}
    for metric_display_name, metric_df in df.groupby("display_name"):
        columns_justify[metric_display_name] = "left" if metric_df["display_format"].values[0] == "str" else "right"
    change_rows = df.loc[df["metric_name"] == "change"]
    df = pd.concat(
        [
            pd.DataFrame(change_rows.replace({"change": "change_numeric", "Change": "Change Numeric", "perc": "str"})),
            df,
        ],
        ignore_index=True,
        axis=0,
    )
    if export_path:
        if export_path.split(".")[-1] == "html":
            formatted_df = prepare_current_metrics_formatted_df(df, "console").sort_values(
                "Change Numeric", ascending=ascending
            )
            formatted_df.drop("Change Numeric", axis=1, inplace=True)
            table = df2Table(
                formatted_df,
                columns_justify=columns_justify,
            )
            export_to_html(table, export_path)
            return None
        formatted_df = prepare_current_metrics_formatted_df(df, "store").sort_values(
            "Change Numeric", ascending=ascending
        )
        formatted_df.drop("Change Numeric", axis=1, inplace=True)
        export_data(
            formatted_df,
            export_path,
            column_width=18,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
        return None
    else:
        formatted_df = prepare_current_metrics_formatted_df(df, "console").sort_values(
            "Change Numeric", ascending=ascending
        )
        formatted_df.drop("Change Numeric", axis=1, inplace=True)
        table = df2Table(
            formatted_df,
            columns_justify=columns_justify,
        )
        return table
