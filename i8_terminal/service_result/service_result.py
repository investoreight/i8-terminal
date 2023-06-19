from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import plotly.express as px
from pandas import DataFrame
from rich.console import Console
from rich.table import Table

from i8_terminal.app.layout import get_plot_default_layout
from i8_terminal.common.formatting import format_date, format_number_v2
from i8_terminal.common.layout import format_df
from i8_terminal.common.utils import concat_and
from i8_terminal.config import get_table_style
from i8_terminal.i8_exception import I8Exception
from i8_terminal.service_result.column_info import ColumnInfo
from i8_terminal.service_result.columns_context import ColumnsContext


class ServiceResult:
    def __init__(self, df: DataFrame, cols_context: ColumnsContext):
        self._df = df
        self._cols_context = cols_context

    def to_df(self, format: str = "default") -> DataFrame:
        """
        Args:
            formating: possible options are
                `raw`: no formating,
                `default`: number (e.g. 123456.7890 => 123,456.79) and display formatting (net_income => Net Income)
                `humanize`: numbers are formatted to human-friendly formats (e.g. 1200000 => $1.20 M)
        """
        return self._format_df(self._df.copy(), format)

    def _wide_df(self, format: str) -> DataFrame:
        df_formatted = self._format_df(self._df.copy(), format)
        df_raw = self._df.copy()

        return pd.concat([df_formatted, df_raw], axis=1)

    def to_json(self) -> Any:
        pass

    def to_console(self, format: str = "default", style_profile: str = "default", width: int = 800) -> None:
        table = self._to_rich_table(format, style_profile)
        console = Console(force_jupyter=True, width=width)
        console.print(table)

    def _to_rich_table(self, format: str, style_profile: str) -> Table:
        style = get_table_style(style_profile)
        table = Table(**style)
        df = self._wide_df(format)
        ci_list = self._cols_context.get_col_infos()
        non_num_dts = ["str", "string", "datetime"]

        for ci in ci_list:
            table.add_column(ci.display_name, justify="left" if ci.data_type in non_num_dts else "right")

        def _process_value(raw: Union[int, float], formatted: str, ci: ColumnInfo) -> str:
            if raw is np.nan or raw is None:
                return "-"
            value = raw if format == "raw" else formatted
            if ci.colorable and ci.data_type not in non_num_dts and raw != 0:
                color = "green" if raw > 0 else "red"
                return f"[{color}]{value}[/{color}]"
            return str(value)

        for _, r in df.iterrows():
            row = [_process_value(r[ci.name], r[ci.display_name], ci) for ci in ci_list]
            table.add_row(*row)

        return table

    def to_plot(self, x: str, y: List[str], kind: str = "bar") -> Any:
        return self._to_plot(x, y, kind)

    def _to_plot(self, x: str, y: List[str], kind: str = "bar") -> Any:
        df = self._df[[x] + y]
        df_grouped = df.groupby(x)[y].mean().reset_index()

        cid = self._cols_context.get_col_info_dict()
        y_display_names = [cid[ci_name].display_name for ci_name in y]
        title = f"{concat_and(y_display_names)} by {cid[x].display_name}"  # type: ignore

        fig = None
        if kind == "bar":
            fig = px.bar(
                df_grouped,
                hover_data=[],
                x=x,
                y=y,
                barmode="group",
                title=title,
                labels={"value": "Metric Value", x: "Period"},
            )
        if not fig:
            return

        fig.update_traces(width=0.3, hovertemplate="%{y}%{_xother}")
        fig.update_layout(
            **get_plot_default_layout(),
            bargap=0.4,
            legend_title_text=None,
            xaxis_title=None,
            margin=dict(b=15, l=70, r=20),
        )
        fig.show()

        return fig

    def to_xlsx(self, path: str, formatter: Optional[str] = None, styler: Optional[str] = None) -> Any:
        pass

    def to_csv(self, path: str, format: str = "raw") -> None:
        df = self._df.copy()
        df = self._format_df(df, format)
        df.to_csv(path, index=False)

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
