import investor8_sdk
from pandas import DataFrame
from i8_terminal.config import APP_SETTINGS, USER_SETTINGS
from i8_terminal.api.earnings.earnings_list_result import EarningsListResult

investor8_sdk.ApiClient().configuration.api_key["apiKey"] = USER_SETTINGS.get("i8_core_api_key")
investor8_sdk.ApiClient().configuration.api_key["Authorization"] = USER_SETTINGS.get("i8_core_token")
investor8_sdk.ApiClient().configuration.api_key_prefix["Authorization"] = "Bearer"

def get_earnings_list(ticker: str, size: int) -> DataFrame:
    historical_earnings = investor8_sdk.EarningsApi().get_historical_earnings(ticker, size=size)
    historical_earnings = [d.to_dict() for d in historical_earnings]
    df = DataFrame(historical_earnings)
    df["period"] = df.fyq.str[2:-2] + " " + df.fyq.str[-2:]
    df = df.dropna(axis=1)
    return EarningsListResult(df)

