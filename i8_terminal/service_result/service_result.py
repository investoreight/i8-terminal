from typing import Any, Callable, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
from rich.console import Console

from i8_terminal.common.formatting import format_date, format_number_v2
from i8_terminal.common.layout import df2Table, format_df
from i8_terminal.i8_exception import I8Exception
from i8_terminal.service_result.columns_context import ColumnsContext
from i8_terminal.utils import concat_and


def colorize_style(row, raw_col: str, formatted_col: str):
    if row[raw_col] == 0:
        return row[formatted_col]
    if row[raw_col] > 0:
        color = "green"
    else:
        color = "red"
    return f"[{color}]{row[formatted_col]}[/{color}]"


class ServiceResult:
    def __init__(self, df: DataFrame, cols_context: ColumnsContext):
        self._df = df
        self._cols_context = cols_context

    def to_df(self, format: str = "default", style: str = "default") -> DataFrame:
        """
        Args:
            formating: possible options are
                `raw`: no formating,
                `formatted`: number (e.g. 123456.7890 => 123,456.79) and display formatting (net_income => Net Income)
                `humanize`: numbers are formatted to human-friendly formats (e.g. 1200000 => $1.20 M)
            styling: possible options are
                `default`: no styling,
                `terminal`: terminal styling (e.g. positive change is green),
                `plotly`: plotly styling
        """

        df = self._wide_df(format)

        stylers = self._style_df(df, style)

        ci_list = self._cols_context.get_col_infos()
        display_names = []

        for ci in ci_list:
            display_names.append(ci.display_name)
            if ci.name in stylers.keys():
                df[ci.display_name] = df.apply(stylers[ci.name], axis=1)

        return df[display_names]

    def _style_df(self, df: DataFrame, style: Any) -> DataFrame:
        ci_list = self._cols_context.get_col_infos()
        stylers: Dict[str, Any] = {}
        for ci in ci_list:
            if style == "default":
                stylers[ci.name] = lambda x: x[ci.display_name]
            if style == "colorize":
                # TODO: remove hardcode
                if ci.colorable and ci.name == "eps_surprise":
                    stylers[ci.name] = lambda x: colorize_style(x, ci.name, ci.display_name)
        return stylers

    def _wide_df(self, format):
        df_formatted = self._format_df(self._df.copy(), format)
        df_raw = self._df.copy()

        return pd.concat([df_formatted, df_raw], axis=1)

    def to_json(self) -> Any:
        pass

    def to_console(self, format: str = "default", style: str = "default", width: int = 800) -> None:
        table = df2Table(self.to_df(format=format, style=style))
        console = Console(force_jupyter=True, width=width)
        console.print(table)

    def to_plot(self, x: str, y: List[str], kind="bar") -> Any:
        return self._to_plot(x, y, kind)

    def _to_plot(self, x: str, y: List[str], kind="bar") -> Any:
        df = self._df[[x] + y]

        df_grouped = df.groupby(x)[y].mean()
        ax = df_grouped.plot(kind=kind, figsize=(10, 6))

        cid = self._cols_context.get_col_info_dict()
        y_display_names = [cid[ci_name].display_name for ci_name in y]
        title = f"{concat_and(y_display_names)} by {cid[x].display_name}"

        ax.set_title(title)
        ax.set_xlabel(cid[x].display_name)
        ax.legend(y_display_names)

        plt.xticks(rotation=45, ha="right")
        plt.show()

        return plt

    def to_xlsx(self, path: str, formatter: Optional[str] = None, styler: Optional[str] = None) -> Any:
        pass

    def to_csv(self, path: str) -> Any:
        pass

    def _format_df(self, df: DataFrame, format: str = "default") -> DataFrame:
        ci_list = self._cols_context.get_col_infos()
        display_names: Dict[str, str] = {}
        formatters: Dict[str, Any] = {}
        for ci in ci_list:
            if ci.display_name is None or ci.data_type is None or ci.unit is None:
                raise I8Exception(f"Missing required metadata fields on colum: `{ci.name}`")

            display_names[ci.name] = ci.display_name
            if ci.data_type in ["int", "unsigned_int", "float", "unsigned_float"] and self._df[ci.name].max() < 1e6:
                if format == "raw":
                    formatters[ci.name] = self._get_formatter(ci.unit, ci.data_type, format)
                else:
                    formatters[ci.name] = self._get_formatter(ci.unit, ci.data_type, format="default")
            else:
                formatters[ci.name] = self._get_formatter(ci.unit, ci.data_type, format)
        return format_df(df, display_names, formatters)

    def _get_formatter(self, unit: str, data_type: str, format: str) -> Callable[[Any], Optional[Union[str, int, Any]]]:
        if format == "raw":
            if unit == "datetime" and data_type == "datetime":
                return lambda x: format_date(x)  # TODO: Implement a new format_date function with date format
            else:
                return lambda x: x

        if data_type == "str" or unit == "string":
            return lambda x: x

        if unit == "datetime":
            if data_type == "datetime":
                return lambda x: format_date(x)
            else:
                return lambda x: x

        if format == "default":
            if data_type in ["int", "unsigned_int"]:
                return lambda x: format_number_v2(x, percision=0, unit=unit)
            elif data_type in ["float", "unsigned_float"]:
                return lambda x: format_number_v2(x, percision=2, unit=unit)
        elif format == "humanize":
            return lambda x: format_number_v2(x, percision=2, unit=unit, humanize=True)
        elif format == "millionize":
            if data_type in ["int", "unsigned_int"]:
                return lambda x: format_number_v2(x, percision=0, unit=unit, in_millions=True)
            elif data_type in ["float", "unsigned_float"]:
                return lambda x: format_number_v2(x, percision=2, unit=unit, in_millions=True)

        return lambda x: x
