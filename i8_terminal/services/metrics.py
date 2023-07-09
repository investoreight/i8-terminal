from ast import literal_eval

import investor8_sdk
import pandas as pd

from i8_terminal.common.stock_info import get_stocks_df
from i8_terminal.common.utils import status
from i8_terminal.i8_exception import I8Exception
from i8_terminal.service_result.column_info import ColumnInfo
from i8_terminal.service_result.columns_context import ColumnsContext
from i8_terminal.service_result.metrics_current_result import MetricsCurrentResult


@status()
def get_current_metrics(tickers: str, metric_names: str) -> MetricsCurrentResult:
    stocks_peers = get_stocks_df()[["ticker", "peers"]].set_index("ticker").to_dict()["peers"]
    tickers_list = []
    for tk in tickers.split(","):
        if "peers" in tk and stocks_peers.get(tk.split(".")[0]):
            ticker_name = tk.split(".")[0]
            tickers_list.append(ticker_name)
            tickers_list.extend(literal_eval(stocks_peers.get(ticker_name)))
        else:
            tickers_list.append(tk)
    metrics = investor8_sdk.MetricsApi().get_current_metrics(
        symbols=",".join(tickers_list),
        metrics=metric_names,
    )
    if metrics.data is None:
        raise I8Exception(
            "None of the provided metrics are available for the given tickers. Make sure you are using correct metric or ticker names."
        )

    df = pd.DataFrame([m.to_dict() for m in metrics.data])
    df = df[["metric", "period", "symbol", "value"]]

    df = df.pivot_table(index=["symbol", "period"], columns="metric", values=["value"]).reset_index()
    df.columns = [l2 if l1 == "value" else l1 for l1, l2 in df.columns]

    col_infos = [
        ColumnInfo(name="symbol", col_type="context", display_name="Ticker", data_type="str", unit="string"),
        ColumnInfo(name="period", col_type="context", display_name="Period", data_type="str", unit="string"),
    ]

    input_metrics = [m.split(".")[0].lower() for m in metric_names.split(",")]
    missed_metrics = []
    for m in input_metrics:
        if m in df.columns:
            col_infos.append(ColumnInfo(name=m, col_type="metric"))
        else:
            missed_metrics.append(m)

    warning = ""
    if len(missed_metrics) > 0:
        warning = f"No data found for metric(s) `{','.join(missed_metrics)}` for the given tickers!"

    cc = ColumnsContext(col_infos)
    return MetricsCurrentResult(df, cc, warning)
