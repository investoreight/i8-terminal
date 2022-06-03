from datetime import datetime
from typing import Dict, List, Optional

import investor8_sdk
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame

from i8_terminal.common.formatting import format_number


def get_historical_price_df(
    tickers: List[str],
    period_code: int,
    from_date: Optional[str],
    to_date: Optional[str],
    pivot_value: Optional[str] = None,
) -> Optional[DataFrame]:
    historical_prices = []
    if from_date:
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        for tk in tickers:
            historical_prices.extend(
                investor8_sdk.PriceApi().get_historical_prices(ticker=tk, from_date=from_date, to_date=to_date)
            )
    else:
        for tk in tickers:
            historical_prices.extend(investor8_sdk.PriceApi().get_historical_prices(ticker=tk, period=period_code))
    if not historical_prices:
        return None
    df = DataFrame([h.to_dict() for h in historical_prices])
    df = df.sort_values(by=["ticker", "timestamp"], ascending=False).reset_index(drop=True)
    df["Date"] = pd.to_datetime(df["timestamp"], unit="s").dt.tz_localize("UTC")
    if len(tickers) > 1:
        df["change_perc"] = (
            df.groupby(["ticker"])
            .apply(lambda x: (x["close"] / x["close"].iloc[-1] - 1))
            .reset_index(level=0)
            .sort_index()["close"]
        )
    else:
        df["change_perc"] = df["close"] / df["close"].iloc[-1] - 1
    df.rename(columns={"ticker": "Ticker"}, inplace=True)
    if pivot_value:
        df = pd.pivot_table(df, index="Date", columns=["Ticker"], values=pivot_value).reset_index(level=0)

    return df


def get_historical_price_export_df(
    tickers: List[str],
    period_code: int,
    from_date: Optional[str],
    to_date: Optional[str],
    compare_columns: Optional[Dict[str, str]] = None,
) -> Optional[DataFrame]:
    df = get_historical_price_df(tickers, period_code, from_date, to_date)
    if df is None:
        return None
    df["Date"] = pd.to_datetime(df["timestamp"], unit="s", utc=True).dt.date
    if compare_columns:
        if "change_perc" in compare_columns:
            if len(tickers) > 1:
                df["change_perc"] = (
                    df.groupby(["Ticker"])
                    .apply(lambda x: (x["close"] / x["close"].shift(-1) - 1))
                    .reset_index(level=0)
                    .sort_index()["close"]
                )
            else:
                df["change_perc"] = df["close"] / df["close"].shift(-1) - 1
            df = df.loc[~np.isnan(df["change_perc"])]
            df["change_perc"] = df["change_perc"].apply(lambda x: format_number(x * 100, exportize=True))
        df.rename(columns=compare_columns, inplace=True)
        df = pd.pivot_table(df, index="Date", columns=["Ticker"], values=compare_columns.values())
    return df


def get_historical_price_list_df(
    tickers: List[str],
    period_code: int,
    from_date: Optional[str],
    to_date: Optional[str],
) -> Optional[DataFrame]:
    df = get_historical_price_df(tickers, period_code, from_date, to_date)
    if df is None:
        return None
    if len(tickers) > 1:
        df["change_perc"] = (
            df.groupby(["Ticker"])
            .apply(lambda x: (x["close"] / x["close"].shift(-1) - 1))
            .reset_index(level=0)
            .sort_index()["close"]
        )
    else:
        df["change_perc"] = df["close"] / df["close"].shift(-1) - 1
    df = df.loc[~np.isnan(df["change_perc"])]
    df["change_perc"] = df["change_perc"].apply(lambda x: format_number(x * 100, exportize=True))
    return df
