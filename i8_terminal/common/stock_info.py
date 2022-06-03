import os
from typing import List, Tuple

import investor8_sdk
import pandas as pd

from i8_terminal.common.utils import is_cached_file_expired
from i8_terminal.config import SETTINGS_FOLDER


def sort_stocks(df: pd.DataFrame) -> pd.DataFrame:
    df["default_rank"] = 11
    default_rank = {
        "A": 1,
        "AAL": 2,
        "AAP": 3,
        "AAPL": 4,
        "AABV": 5,
        "ABC": 6,
        "ABMD": 7,
        "ABT": 8,
        "ACN": 9,
        "ADBE": 10,
    }
    df["default_rank"] = df["ticker"].apply(lambda x: default_rank.get(x, 11))
    df = df.sort_values("default_rank").reset_index(drop=True)
    return df[["ticker", "name"]]


def get_stocks_df() -> pd.DataFrame:
    companies_path = f"{SETTINGS_FOLDER}/companies.csv"
    if os.path.exists(companies_path) and not is_cached_file_expired(companies_path):
        stocks_df = pd.read_csv(companies_path)
    else:
        results = investor8_sdk.StockInfoApi().get_all_active_companies()
        stocks_df = pd.DataFrame([d.to_dict() for d in results])[["ticker", "name"]]
        stocks_df = sort_stocks(stocks_df)
        stocks_df.to_csv(companies_path, index=False)
    return stocks_df


def get_stocks() -> List[Tuple[str, str]]:
    df = get_stocks_df()
    return list(df.to_records(index=False))
