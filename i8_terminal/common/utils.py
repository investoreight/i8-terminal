import enum
import os
from difflib import SequenceMatcher
from io import StringIO
from typing import Any, Dict, Optional

import arrow
import pandas as pd
from rich.console import Console

from i8_terminal.config import APP_SETTINGS


class PlotType(enum.Enum):
    CHART = "chart"
    TABLE = "table"


def to_snake_case(value: str) -> str:
    return "_".join(value.lower().split())


def get_period_code(period: str) -> int:
    return {"1D": 1, "5D": 2, "1M": 3, "3M": 4, "6M": 5, "1Y": 6, "3Y": 7, "5Y": 8}.get(period, 3)


def get_period_days(period: str) -> int:
    return {"1D": 1, "5D": 5, "1M": 30, "3M": 90, "6M": 180, "1Y": 365, "3Y": 1095, "5Y": 1825}.get(period, 365)


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def export_data(
    export_df: pd.DataFrame,
    export_path: str,
    column_width: Optional[int],
    column_format: Dict[str, Any],
    index: bool = False,
) -> None:
    console = Console()
    extension = export_path.split(".")[-1]
    if extension == "csv":
        export_df.to_csv(export_path, index=index)
        console.print(f"Data is saved on: {export_path}")
    elif extension == "xlsx":
        writer = pd.ExcelWriter(export_path, engine="xlsxwriter")
        export_df.to_excel(writer, sheet_name="Sheet1", startrow=1, header=False, index=index)
        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]
        header_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["default"]["header"])
        metric_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["default"]["metric"])
        column_format = workbook.add_format(column_format)
        headers = export_df.columns.tolist()
        if index:
            headers.insert(0, (export_df.index.name, ""))
        for col_num, value in enumerate(headers):
            if type(value) is tuple:
                worksheet.merge_range(0, col_num, len(value) - 1, col_num, " ".join(reversed(value)), header_format)
            else:
                worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(0, 0, 20, metric_format)
        worksheet.set_column(
            1, len(export_df.columns) - 1 if not index else len(export_df.columns), column_width, column_format
        )
        writer.save()
        console.print(f"Data is saved on: {export_path}")
    else:
        console.print("export_path is not valid")


def is_cached_file_expired(file_path: str) -> bool:
    mtime = arrow.get(os.path.getmtime(file_path))
    return bool(mtime < arrow.utcnow().shift(hours=-APP_SETTINGS.get("cache", {}).get("age", 48)))


def reverse_period(period: str) -> str:
    """
    If period is fyq type (eg. 'Q 2021'), the function will change it to '2021 Q'.
    """
    splitted_period = period.split(" ")
    return f"{splitted_period[1]} {splitted_period[0]}" if len(splitted_period) > 1 else period


def export_to_html(data: Any, export_path: str) -> None:
    console = Console(record=True, file=StringIO())
    console.print(data)
    exported_html = console.export_html(
        inline_styles=True,
        code_format="""
        <html>
            <head>
                <title>i8 Terminal by Investor8</title>
            </head>
            <body>
                <div>
                    <img src='https://i8terminal.io/img/TerminalLogo.png' width='16%'>
                </div>
                <div>
                    <pre>{code}</pre>
                </div
            </body>
        </html>
        """,
    )
    with open(export_path, "w", encoding="utf-8") as file:
        file.write(exported_html)
    console = Console()
    console.print(f"Data is saved on: {export_path}")
