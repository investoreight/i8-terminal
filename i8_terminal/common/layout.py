from typing import Any, Dict

from pandas import DataFrame
from rich.table import Table

from i8_terminal.config import get_table_style


def format_df(df: DataFrame, cols_map: Dict[str, str], cols_formatters: Dict[str, Any]) -> DataFrame:
    for c, f in cols_formatters.items():
        df[c] = df[c].map(f)
    return df[cols_map.keys()].rename(columns=cols_map)


def df2Table(df: DataFrame, style_profile: str = "default", columns_justify: Dict[str, Any] = {}) -> Table:
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
    }
    for c in df.columns:
        table.add_column(c, justify=columns_justify.get(c, default_justify.get(c, "left")))
    for _, r in df.iterrows():
        row = [r[c] for c in df.columns]
        table.add_row(*row)
    return table
