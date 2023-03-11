from typing import Any, Callable, Dict, Optional, Union

from pandas import DataFrame

from i8_terminal.common.formatting import format_date, format_number_v2
from i8_terminal.common.layout import format_df
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
        df = self._format_df(df, format)
        df = self._style_df(df, style)
        return df

    def to_json(self) -> Any:
        pass

    def to_console(self) -> None:
        pass

    def to_plot(self) -> Any:
        pass

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

    def _style_df(self, df: DataFrame, styling: Any) -> DataFrame:
        return df

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
