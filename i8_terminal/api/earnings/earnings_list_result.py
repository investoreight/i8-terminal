from i8_terminal.api.service_result import ServiceResult
from i8_terminal.common.layout import format_df
from i8_terminal.common.formatting import get_formatter


class EarningsListResult(ServiceResult):
    
    def __init__(self, data, context=None):
        super().__init__(data, context)


    def _format_df(self, df):
        # TDOO: formatting and styling logic is coupled. They should be decoupled
        target = "store"
        formatters = {
            "actual_report_time": get_formatter("date", target),
            "eps_actual": get_formatter("number", target),
            "eps_ws": get_formatter("number", target),
            "eps_surprise": get_formatter("colorize_number" if target == "console" else "number", target),
            "revenue_actual": get_formatter("financial", target),
            "revenue_ws": get_formatter("financial", target),
            "revenue_surprise": get_formatter("colorize_financial" if target == "console" else "financial", target),
        }
        col_names = {
            "actual_report_time": "Date",
            "period": "Period",
            "call_time": "Call Time",
            "eps_ws": "EPS Estimate",
            "eps_actual": "EPS Actual",
            "eps_surprise": "EPS Surprise",
            "revenue_ws": "Revenue Estimate",
            "revenue_actual": "Revenue Actual",
            "revenue_surprise": "Revenue Surprise",
        }
        return format_df(df, col_names, formatters)    
