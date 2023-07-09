import os
from typing import List, Optional, Tuple

import click
import investor8_sdk
import numpy as np
import pandas as pd

from i8_terminal.common.utils import is_cached_file_expired
from i8_terminal.config import SETTINGS_FOLDER


def sort_stocks(df: pd.DataFrame, include_peers: bool = False) -> pd.DataFrame:
    df["default_rank"] = 11
    if not include_peers:
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
    else:
        default_rank = {
            "A": 1,
            "A.peers": 2,
            "AAL": 3,
            "AAL.peers": 4,
            "AAP": 5,
            "AAP.peers": 6,
            "AAPL": 7,
            "AAPL.peers": 8,
            "AABV": 9,
            "AABV.peers": 10,
        }
    df["default_rank"] = df["ticker"].apply(lambda x: default_rank.get(x, 11))
    df = df.sort_values("default_rank").reset_index(drop=True)
    return df[["ticker", "name", "peers"]]


def get_stocks_df() -> pd.DataFrame:
    companies_path = f"{SETTINGS_FOLDER}/companies.csv"
    if os.path.exists(companies_path) and not is_cached_file_expired(companies_path):
        stocks_df = pd.read_csv(companies_path, keep_default_na=False)
    else:
        results = investor8_sdk.StockInfoApi().get_all_active_companies()
        stocks_df = pd.DataFrame([d.to_dict() for d in results])[["ticker", "name", "peers"]]
        stocks_df = sort_stocks(stocks_df)
        stocks_df.to_csv(companies_path, index=False)
    return stocks_df


def get_stocks(include_peers: bool) -> List[Tuple[str, str]]:
    columns_list = ["ticker", "name"]
    df = get_stocks_df().replace("", np.nan)
    if include_peers:
        df_peers = df[~df["peers"].isna()].copy()
        df_peers.loc[:, "ticker"] = df_peers["ticker"].apply(lambda x: x + ".peers")
        df_peers.loc[:, "name"] = df_peers["name"].apply(lambda x: "Peers of " + x)
        df = sort_stocks(pd.concat([df, df_peers]), include_peers)
    return list(df[columns_list].to_records(index=False))


def validate_ticker(ctx: click.Context, param: str, value: str) -> Optional[str]:
    if not ctx.resilient_parsing:
        if value and len(value.replace(" ", "").split(",")) > 1:
            click.echo(click.style(f"`{value}` is not a valid ticker name.", fg="yellow"))
            ctx.exit()
        if value and value.replace(" ", "").upper() not in set(get_stocks_df()["ticker"]):
            click.echo(click.style(f"`{value}` is not a valid ticker name.", fg="yellow"))
            ctx.exit()
    return value


def validate_tickers(ctx: click.Context, param: str, value: str) -> Optional[str]:
    tickers = {d[0] for d in get_stocks(True)}
    if not ctx.resilient_parsing:
        invalid_tickers = [*set(value.replace(" ", "").split(",")) - tickers] if value else []
        if value and invalid_tickers:
            msg = "are not valid ticker names." if len(invalid_tickers) > 1 else "is not a valid ticker name."
            click.echo(
                click.style(
                    f"`{', '.join(invalid_tickers)}` {msg}",
                    fg="yellow",
                )
            )
            ctx.exit()
    return value
