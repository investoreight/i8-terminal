from typing import Any
from pandas import DataFrame


class ServiceResult():

    def __init__(self, data, context):
        self._data = data
        self._context = context

    
    def to_df(self, formating="formatted", styling="default"):
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
        if type(self._data) is not DataFrame:
            raise f"{type(self)} does not support 'to_df()'"

        df = self._data
        if formating != "raw":
            self._format_df(df)
        if styling != "default":
            self._style_df(df, styling)

        return df


    def to_json(self):
        pass


    def to_console(self):
        pass


    def to_plot(self):
        pass
    

    def to_xlsx(self, path: str, formatter=None, styler=None):
        pass

    
    def to_csv(self, path: str):
        pass


    def _format_df(self, df):
        pass        

    def _style_df(self, df, styling):
        pass
