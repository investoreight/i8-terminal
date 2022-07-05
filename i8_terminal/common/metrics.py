import os
from typing import Dict, List, Optional, Tuple

import arrow
import investor8_sdk
import numpy as np
import pandas as pd
from investor8_sdk import MetricsApi
from pandas import DataFrame, read_csv

from i8_terminal.common.layout import format_metrics_df
from i8_terminal.common.utils import is_cached_file_expired, similarity
from i8_terminal.config import APP_SETTINGS, SETTINGS_FOLDER


def get_indicators_list(indicator: Optional[str] = None) -> List[str]:
    indicators_dict = {
        "Momentum": ["ma5", "ma12", "ma26", "ma52", "ema5", "ema12", "ema26", "ema52"],
        "RSI": ["rsi_7d", "rsi_14d", "rsi_1m", "rsi_3m"],
        "Alpha": ["alpha_1w", "alpha_2w", "alpha_1m", "alpha_3m", "alpha_6m", "alpha_1y", "alpha_2y", "alpha_5y"],
        "Beta": ["beta_1w", "beta_2w", "beta_1m", "beta_3m", "beta_6m", "beta_1y", "beta_2y", "beta_5y"],
        "Volume": ["volume"],
    }
    if indicator:
        return indicators_dict.get(indicator, [""])
    else:
        return [item for sublist in indicators_dict.values() for item in sublist]


def find_similar_fin_metric(metric: str) -> Optional[str]:
    metrics_meta_data = get_all_metrics_df()[["metric_name"]]
    best_match_similarity = 0.0
    best_match = ""
    for idx, m in metrics_meta_data.iterrows():
        sim = similarity(metric.upper(), m["metric_name"].upper())
        if sim > best_match_similarity:
            best_match_similarity = sim
            best_match = m["metric_name"]
    if best_match_similarity < APP_SETTINGS["metrics"]["similarity_threshold"]:
        return None
    return best_match


def find_similar_indicator(indicator: str) -> Optional[str]:
    default_indicators = {"rsi": "rsi_14d", "alpha": "alpha_1y", "beta": "beta_1y"}
    defualt_ind = default_indicators.get(indicator)
    if defualt_ind:
        return defualt_ind
    indicators_list = get_indicators_list()
    best_match_similarity = 0.0
    best_match = ""
    for ind in indicators_list:
        sim = similarity(indicator, ind)
        if sim > best_match_similarity:
            best_match_similarity = sim
            best_match = ind
    if best_match_similarity < APP_SETTINGS["metrics"]["similarity_threshold"]:
        return None

    return best_match


def get_all_metrics_df() -> DataFrame:
    metric_path = f"{SETTINGS_FOLDER}/metrics_metadata.csv"
    if os.path.exists(metric_path) and not is_cached_file_expired(metric_path):
        df = read_csv(metric_path)
    else:
        all_metrics = MetricsApi().get_list_metrics_metadata(page_size=1000)
        df = DataFrame([m.to_dict() for m in all_metrics])
        df["categories"] = [str(cat) for cat in df["categories"]]
        df = df.drop(columns=["id", "last_modified"])
        df.to_csv(metric_path, index=False)

    return df


def get_all_financial_metrics_df() -> DataFrame:
    metric_path = f"{SETTINGS_FOLDER}/financial_metrics_metadata.csv"
    if os.path.exists(metric_path) and not is_cached_file_expired(metric_path):
        df = read_csv(metric_path)
    else:
        all_metrics = MetricsApi().get_list_financial_metrics_metadata()
        df = DataFrame([m.to_dict() for m in all_metrics])
        df.to_csv(metric_path, index=False)

    return df


def get_metrics_display_names(metrics: List[str]) -> List[str]:
    all_metrics = get_all_metrics_df()[["metric_name", "display_name"]]
    return list(set(all_metrics[all_metrics.metric_name.isin(metrics)]["display_name"]))


def get_metric_info(name: str) -> Tuple[str, str, str]:
    all_metrics = get_all_metrics_df()
    metric = all_metrics.loc[all_metrics.metric_name == name].replace(np.nan, "", regex=True).to_dict("records")[0]
    return (
        metric["display_name"],
        metric["unit"],
        metric["description"] if "description" in metric.keys() and metric["description"] else "No Description",
    )


def get_period_start_date(period: str) -> str:
    period_start_date: Dict[str, str] = {
        "1M": arrow.now().shift(months=-1).datetime.strftime("%Y-%m-%d"),
        "3M": arrow.now().shift(months=-3).datetime.strftime("%Y-%m-%d"),
        "6M": arrow.now().shift(months=-6).datetime.strftime("%Y-%m-%d"),
        "1Y": arrow.now().shift(years=-1).datetime.strftime("%Y-%m-%d"),
        "3Y": arrow.now().shift(years=-3).datetime.strftime("%Y-%m-%d"),
        "5Y": arrow.now().shift(years=-5).datetime.strftime("%Y-%m-%d"),
    }
    return period_start_date[period]


def get_current_metrics_df(tickers: str, metricsList: str) -> Optional[pd.DataFrame]:
    metrics = investor8_sdk.MetricsApi().get_current_metrics(
        symbols=tickers,
        metrics=metricsList,
    )
    if metrics.data is None:
        return None
    metrics_data_df = pd.DataFrame([m.to_dict() for m in metrics.data])
    metrics_data_df.rename(columns={"metric": "metric_name", "symbol": "Ticker"}, inplace=True)
    metrics_metadata_df = pd.DataFrame([m.to_dict() for m in metrics.metadata])
    return pd.merge(metrics_data_df, metrics_metadata_df, on="metric_name").replace("string", "str")


def prepare_current_metrics_formatted_df(df: DataFrame, target: str) -> DataFrame:
    formatted_df = format_metrics_df(df, target)
    return (
        formatted_df.pivot(index="Ticker", columns="display_name", values="value")
        .reset_index(level=0)
        .reindex(np.insert(df["display_name"].unique(), 0, "Ticker"), axis=1)
    )
