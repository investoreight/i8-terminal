import investor8_sdk
from pandas import DataFrame

from i8_terminal.service_result import EarningsListResult


def get_earnings_list(ticker: str, size: int) -> EarningsListResult:
    historical_earnings = investor8_sdk.EarningsApi().get_historical_earnings(ticker, size=size)
    historical_earnings = [d.to_dict() for d in historical_earnings]
    df = DataFrame(historical_earnings)
    df["period"] = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    df = df.dropna(axis=1)
    return EarningsListResult(df)
