import investor8_sdk
from pandas import DataFrame

from i8_terminal.common.utils import status
from i8_terminal.service_result.column_info import ColumnInfo
from i8_terminal.service_result.columns_context import ColumnsContext
from i8_terminal.service_result.earning_list_result import EarningsListResult


@status()
def get_earnings_list(ticker: str, size: int) -> EarningsListResult:
    historical_earnings = investor8_sdk.EarningsApi().get_historical_earnings(ticker, size=size)
    historical_earnings = [d.to_dict() for d in historical_earnings]
    df = DataFrame(historical_earnings)
    df["period"] = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    df.rename(
        columns={
            "actual_report_time": "earning_date",
            "eps_ws": "eps_consensus",
            "revenue_ws": "revenue_consensus",
            "call_time": "earning_call_time",
        },
        inplace=True,
    )
    cc = ColumnsContext(
        [
            ColumnInfo(name="period", col_type="context", display_name="Period", data_type="str", unit="string"),
            ColumnInfo(name="earning_date", col_type="metric"),
            ColumnInfo(name="earning_call_time", col_type="metric"),
            ColumnInfo(name="eps_consensus", col_type="metric"),
            ColumnInfo(name="eps_actual", col_type="metric"),
            ColumnInfo(name="eps_surprise", col_type="metric"),
            ColumnInfo(name="revenue_consensus", col_type="metric"),
            ColumnInfo(name="revenue_actual", col_type="metric"),
            ColumnInfo(name="revenue_surprise", col_type="metric"),
        ]
    )
    return EarningsListResult(df, cc)
