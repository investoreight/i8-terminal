from typing import Any, Callable, Dict, Optional, Union, Tuple

from pandas import DataFrame

from rich.table import Table

from i8_terminal.common.formatting import format_date, format_number_v2, colorize_style
from i8_terminal.common.layout import df2Table, format_df

import pandas as pd
from i8_terminal.i8_exception import I8Exception
from i8_terminal.service_result.columns_context import ColumnsContext


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
        df = self._df.copy()
        ci_list = self._cols_context.get_col_infos()
        raw_col_names = {}
        for ci in ci_list:
            raw_col_names[ci.name] = ci.name+"_raw"

        display_names, formatters = self._format_df(df, format)
        

        df_raw = self._df.copy()
        df_raw = df_raw.rename(columns=raw_col_names)

        df = pd.concat([df, df_raw], axis=1)
        stylers = self._style_df(df, style)
    
        for ci in ci_list:
            if ci.name in formatters.keys():
                df[ci.name] = df[ci.name].apply(formatters[ci.name])
            if ci.name in stylers.keys():
                # df[ci.name] = df.apply(stylers[ci.name], axis=1)
                df[ci.name] = df.apply(lambda x: x[ci.name], axis=1)
        
        return df[display_names.keys()].rename(columns=display_names)

    def to_json(self) -> Any:
        pass

    def to_console(self, format: str = "humanize") -> Table:
        df = self.to_df(format=format)
        return df2Table(df)

    def to_plot(self) -> Any:
        pass

    def to_xlsx(self, path: str, formatter: Optional[str] = None, styler: Optional[str] = None) -> Any:
        pass

    def to_csv(self, path: str, format: str = "raw") -> None:
        df = self._df.copy()
        df = self._format_df(df, format)
        df.to_csv(path, index=False)

    def _format_df(self, df: DataFrame, format: str = "default") -> Tuple[Dict[str, str], Dict[str, Any]]:
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
        return (display_names, formatters)

    def _style_df(self, df: DataFrame, style: Union[str, Any]="default") -> DataFrame:
        ci_list = self._cols_context.get_col_infos()
        stylers: Dict[str, Any] = {}
        for ci in ci_list:
            if style == "default":
                stylers[ci.name] = lambda x: x[ci.name]
            if style == "colorize":
                if ci.colorable:
                    stylers[ci.name] = lambda x: colorize_style(x, self._get_raw_name(ci.name), ci.name)
        return stylers


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

    
    def _get_raw_name(self, name):
        return name+"_raw"
