from datetime import datetime
from typing import Any, Dict, List, Optional, cast

import arrow
import click
import investor8_sdk
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from click.types import DateTime
from pandas.core.frame import DataFrame
from plotly.subplots import make_subplots
from rich.console import Console

from i8_terminal.app.plot_server import serve_plot
from i8_terminal.commands.price import price
from i8_terminal.common.cli import get_click_command_path, pass_command
from i8_terminal.common.price import get_historical_price_df
from i8_terminal.types.indicator_param_type import IndicatorParamType
from i8_terminal.types.price_period_param_type import PricePeriodParamType
from i8_terminal.types.ticker_param_type import TickerParamType

from i8_terminal.common.utils import PlotType, get_period_code, get_period_days, validate_ticker  # isort:skip

from i8_terminal.app.layout import get_date_range, get_plot_default_layout  # isort:skip
from i8_terminal.common.metrics import find_similar_indicator, get_indicators_list  # isort:skip
from i8_terminal.types.chart_param_type import ChartParamType, get_chart_param_types  # isort:skip


def get_matched_indicators(indicators_list: List[str]) -> List[str]:
    matched_indicators = []
    if indicators_list:
        for i in indicators_list:
            similar_indicator = find_similar_indicator(i)
            if similar_indicator:
                matched_indicators.append(similar_indicator)

    return matched_indicators


def get_indicators_df(
    tickers: List[str], indicators: str, period: str, from_date: Optional[str], to_date: Optional[str]
) -> DataFrame:
    historical_indicators = {}
    if not to_date:
        to_date = arrow.now().datetime.strftime("%Y-%m-%d")
    if not from_date:
        from_date = arrow.now().shift(days=-get_period_days(period)).datetime.strftime("%Y-%m-%d")
    for tk in tickers:
        historical_indicators[tk] = investor8_sdk.MetricsApi().get_historical_indicators(
            ticker=tk, indicators=indicators, from_date=from_date, to_date=to_date
        )

    for k, val in historical_indicators.items():
        df = DataFrame([{"Ticker": k, "timestamp": h.timestamp, **h.indicators} for h in val])
    df = df.sort_values(by=["Ticker", "timestamp"], ascending=False).reset_index(drop=True)
    df["Date"] = pd.to_datetime(df["timestamp"], unit="s").dt.tz_localize("UTC")

    return df


def get_indicator_categories(indicators: List[str]) -> Dict[str, List[str]]:
    momentums_indicators = set(get_indicators_list("Momentum")) & set(indicators)
    alpha_indicators = set(get_indicators_list("Alpha")) & set(indicators)
    beta_indicators = set(get_indicators_list("Beta")) & set(indicators)
    rsi_indicators = set(get_indicators_list("RSI")) & set(indicators)
    volume_indicators = set(get_indicators_list("Volume")) & set(indicators)
    indicator_categories = {}
    indicator_categories["Momentum"] = list(momentums_indicators)  # Because price subplot is always existed
    if volume_indicators:
        indicator_categories["Volume"] = list(volume_indicators)
    if alpha_indicators:
        indicator_categories["Alpha"] = list(alpha_indicators)
    if beta_indicators:
        indicator_categories["Beta"] = list(beta_indicators)
    if rsi_indicators:
        indicator_categories["RSI"] = list(rsi_indicators)

    return indicator_categories


def get_data_df(
    tickers: List[str], period: str, indicators: List[str], from_date: Optional[str], to_date: Optional[str]
) -> Optional[DataFrame]:
    period_code = get_period_code(period)
    hist_price_df = get_historical_price_df(tickers, period_code, from_date, to_date)
    if hist_price_df is None:
        return None
    hist_price_df = hist_price_df[["Ticker", "Date", "close", "open", "high", "low", "volume"]]
    rename_cols = {"close": "Close", "open": "Open", "high": "High", "low": "Low"}
    hist_price_df.rename(columns=rename_cols, inplace=True)
    if indicators:
        indicators_df = get_indicators_df(tickers, ",".join(indicators), period, from_date, to_date)
        merged_df = pd.merge(hist_price_df, indicators_df, on=["Ticker", "Date"])
        merged_df = merged_df.set_index("Date")
        merged_df.rename(columns={"ma12": "MA12", "ma26": "MA26", "ma52": "MA52", "rsi14_d": "RSI"}, inplace=True)
        return merged_df[list(rename_cols.values()) + indicators]
    else:
        hist_price_df = hist_price_df.set_index("Date")
        return hist_price_df[list(rename_cols.values())]


def create_fig(
    df: DataFrame,
    period: str,
    indicator_categories: Dict[str, List[str]],
    cmd_context: Dict[str, Any],
    chart_type: str,
    range_selector: bool = True,
) -> go.Figure:
    vertical_spacing = 0.02
    layout = dict(
        title=cmd_context["plot_title"],
        autosize=True,
        hovermode="closest",
        legend=dict(font=dict(size=11), orientation="v"),
        margin=dict(b=20, l=50, r=65),
    )
    rows_num = len(indicator_categories)

    if rows_num == 2:
        row_width = [0.4, 0.6]
    elif rows_num == 3:
        row_width = [0.25, 0.25, 0.5]
    elif rows_num == 4:
        row_width = [0.2, 0.2, 0.2, 0.4]
    else:
        row_width = [1]

    fig = make_subplots(
        rows=rows_num,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=vertical_spacing,
        row_width=row_width,
    )
    if chart_type == "candlestick":
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price",
                showlegend=False,
            ),
            row=1,
            col=1,
        )
    else:
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"), row=1, col=1)
        fig.update_traces(hovertemplate="%{y:$.2f} %{x}")

    for idx, (k, ind) in enumerate(indicator_categories.items()):
        for m in ind:
            if m == "volume":
                fig.add_trace(go.Bar(x=df.index, y=df[m], name="Volume", showlegend=False), row=idx + 1, col=1)
            else:
                fig.add_trace(go.Scatter(x=df.index, y=df[m], name=m), row=idx + 1, col=1)

    dt_all = pd.date_range(start=df.index[-1], end=df.index[0])
    dt_obs = [d.strftime("%Y-%m-%d") for d in df.index]
    dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]

    fig.update_xaxes(
        rangeslider_visible=False, spikemode="across", spikesnap="cursor", rangebreaks=[dict(values=dt_breaks)]
    )
    if range_selector:
        fig.update_xaxes(rangeselector=get_date_range(get_period_code(period)))
    fig.update_layout(
        **layout,
        **get_plot_default_layout(),
        legend_title_text=None,
        xaxis_title=None,
        yaxis_title=None,
    )

    # Add an anotation in top of the plot
    for idx, r in enumerate(np.cumsum(row_width)[::-1]):
        if len(row_width) == 1:
            subplot_title = "Close Price"
        else:
            subplot_title = list(indicator_categories.keys())[idx]
            subplot_title = "Close Price" if subplot_title == "Momentum" else subplot_title
        fig.add_annotation(
            dict(
                x=0,
                y=r - idx * vertical_spacing,
                xref="paper",
                yref="paper",
                text=f"<b>{subplot_title}</b>",
                showarrow=False,
            )
        )
    fig.update_annotations(
        dict(
            font_size=10,
            font_color="#525252",
        )
    )

    return fig


@price.command()
@click.pass_context
@click.option("--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Company ticker.")
@click.option(
    "--period",
    "-p",
    type=PricePeriodParamType(),
    default="1M",
    help="Historical price period.",
)
@click.option(
    "--indicators",
    "-i",
    type=IndicatorParamType(),
    help="Optional technical indicators to enrich the chart.",
)
@click.option("--from_date", "-f", type=DateTime(), help="Histotical price from date.")
@click.option("--to_date", "-t", type=DateTime(), help="Histotical price to date.")
@click.option(
    "--chart_type",
    "-c",
    type=ChartParamType([("line", "Line chart"), ("candlestick", "Candlestick chart")]),
    default="line",
    help="Chart can be candlestick or line chart.",
)
@pass_command
def plot(
    ctx: click.Context,
    ticker: str,
    period: str,
    indicators: str,
    from_date: Optional[datetime],
    to_date: Optional[datetime],
    chart_type: str,
) -> None:
    """Plot historical prices of given company.

    Examples:

    `i8 price plot --period 1M --indicators volume --ticker MSFT --chart_type candlestick`
    """
    if not chart_type in [t[0] for t in get_chart_param_types()]:
        click.echo(f"`{chart_type}` is not valid chart type.")
        return
    period = period.replace(" ", "").upper()
    indicators_list = indicators.replace(" ", "").upper().split(",") if indicators else []
    indicators_list = get_matched_indicators(indicators_list)
    indicator_categories = get_indicator_categories(indicators_list)
    ticker = ticker.upper()
    plot_title = f"{ticker} historical prices"
    command_path_parsed_options_dict = {"--indicators": ",".join(indicators_list)}
    if from_date:
        command_path_parsed_options_dict["--from_date"] = from_date.strftime("%Y-%m-%d")
    if to_date:
        command_path_parsed_options_dict["--to_date"] = to_date.strftime("%Y-%m-%d")
    command_path = get_click_command_path(ctx, command_path_parsed_options_dict)
    cmd_context = {
        "command_path": command_path,
        "tickers": ticker,
        "plot_title": plot_title,
        "plot_type": PlotType.CHART.value,
    }

    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        df = get_data_df([ticker], period, indicators_list, cast(str, from_date), cast(str, to_date))
        if df is None:
            status.stop()
            console.print("No data found!")
            return
        status.update("Generating plot...")
        fig = create_fig(df, period, indicator_categories, cmd_context, chart_type, range_selector=False)

    serve_plot(fig, cmd_context)
