from typing import Any, Dict

import numpy as np
from pandas import DataFrame
from rich.table import Table

from i8_terminal.common.formatting import data_format_mapper, get_formatter
from i8_terminal.config import get_table_style


def format_df(df: DataFrame, cols_map: Dict[str, str], cols_formatters: Dict[str, Any]) -> DataFrame:
    for c, f in cols_formatters.items():
        df[c] = df[c].map(f)
    return df[cols_map.keys()].rename(columns=cols_map)


def format_metrics_df(df: DataFrame, target: str) -> DataFrame:
    df["value"] = df.apply(
        lambda metric: get_formatter(
            "number_int"
            if metric.data_format == "int" and metric.display_format == "number"
            else metric.display_format,
            target,
        )(data_format_mapper(metric)),
        axis=1,
    )
    return df


def df2Table(df: DataFrame, style_profile: str = "default", columns_justify: Dict[str, Any] = {}) -> Table:
    MIN_COL_LENGTH = 13
    style = get_table_style(style_profile)
    table = Table(**style)
    default_justify = {
        "Price": "right",
        "Open": "right",
        "Close": "right",
        "Low": "right",
        "High": "right",
        "Volume": "right",
        "Change": "right",
        "Change (%)": "right",
        "Market Cap": "right",
        "EPS Cons.": "right",
        "EPS Actual": "right",
        "Revenue Cons.": "right",
        "Revenue Actual": "right",
        "Level": "right",
        "EPS Estimate": "right",
        "Revenue Estimate": "right",
        "EPS Beat Rate": "right",
        "Revenue Beat Rate": "right",
        "EPS Surprise": "right",
        "Revenue Surprise": "right",
        "EPS Consensus": "right",
        "Revenue Consensus": "right",
        "Eps Surprise": "right",
    }
    for c in df.columns:
        table.add_column(
            c,
            justify=columns_justify.get(c, default_justify.get(c, "left")),
            min_width=min(max(df[c].str.len().max(), len(df[c].name)), MIN_COL_LENGTH),
        )
    for _, r in df.iterrows():
        row = [r[c] if r[c] is not np.nan and r[c] is not None else "-" for c in df.columns]
        table.add_row(*row)
    return table
