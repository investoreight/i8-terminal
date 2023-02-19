from typing import Any

from pandas import DataFrame

from i8_terminal.service_result.columns_context import ColumnsContext


class ServiceResult:
    def __init__(self, df: DataFrame, cols_context: ColumnsContext):
        self._df = df
        self._cols_context = cols_context

    def to_df(self, formatting: str = "formatted", styling: str = "default") -> DataFrame:
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

        df = self._data.copy()
        if formatting != "raw":
            df = self._format_df(df, target)
        if styling != "default":
            df = self._style_df(df, styling)

        return df

    def to_json(self) -> Any:
        pass

    def to_console(self) -> None:
        pass

    def to_plot(self) -> Any:
        pass

    def to_xlsx(self, path: str, formatter=None, styler=None) -> Any:
        pass

    def to_csv(self, path: str) -> Any:
        pass

    def _format_df(self, df: DataFrame) -> DataFrame:
        ci_list = self._cols_context.get_col_infos()
        # rename
        # call format

    def _style_df(self, df: DataFrame, styling: Any) -> DataFrame:
        pass
