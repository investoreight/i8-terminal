import enum
import os
from difflib import SequenceMatcher
from io import StringIO
from typing import Any, Callable, Dict, List, Optional, TypeVar

import arrow
import click
import pandas as pd
from prompt_toolkit.document import Document
from rich.console import Console

from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.command_parser import CompleterContext

T = TypeVar("T")


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


def status(text: str = "Fetching data...", spinner: str = "material") -> Callable[..., Callable[..., T]]:
    def decorate(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            console = Console()
            with console.status(text, spinner=spinner):
                return func(*args, **kwargs)

        return wrapper

    return decorate


def concat_and(items: List[str]) -> str:
    return " and ".join(", ".join(items).rsplit(", ", 1))


def get_matched_params(ctx: CompleterContext, command: click.Command, document: Document) -> List[click.Option]:
    if not document.is_cursor_at_the_end:
        command_string = document.current_line
        cursor_position = document.cursor_position
        options_positions = [
            (o, cursor_position - command_string.find(o))
            for c in command.params
            for o in ctx.used_options
            if cursor_position - command_string.find(o) > 0
        ]
        matched = min(options_positions, key=lambda option_position: option_position[1])  # type: ignore
        matched_params = [p for p in command.params if isinstance(p, click.Option) and matched[0] in p.opts]
    else:
        matched_params = [p for p in command.params if isinstance(p, click.Option) and ctx.last_option in p.opts]
    return matched_params
