from typing import Any, Dict, List, Optional, cast

import click
import plotly.express as px
from click.types import DateTime
from pandas.core.frame import DataFrame
from plotly.graph_objects import Figure
from rich.console import Console

from i8_terminal.app.layout import get_date_range, get_plot_default_layout
from i8_terminal.app.plot_server import serve_plot
from i8_terminal.commands.price import price
from i8_terminal.common.cli import get_click_command_path, pass_command
from i8_terminal.common.layout import df2Table
from i8_terminal.common.price import (
    get_historical_price_df,
    get_historical_price_export_df,
)
from i8_terminal.common.stock_info import validate_tickers
from i8_terminal.common.utils import (
    PlotType,
    export_data,
    export_to_html,
    get_period_code,
)
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.price_period_param_type import PricePeriodParamType
from i8_terminal.types.ticker_param_type import TickerParamType


def get_price_data(
    tickers: List[str], period_code: int, from_date: Optional[str], to_date: Optional[str]
) -> Optional[DataFrame]:
    hist_price_df = get_historical_price_df(tickers, period_code, from_date, to_date, pivot_value="change_perc")
    # FIXME: use realtime price in future
    # realtime_price_df = get_historical_price_df(tickers, 1)
    # df = hist_price_df.append(realtime_price_df)
    if hist_price_df is None:
        return None
    hist_price_df = hist_price_df.dropna()

    return hist_price_df.sort_values("Date")


def get_export_data(
    tickers: List[str], period_code: int, from_date: Optional[str], to_date: Optional[str]
) -> Optional[DataFrame]:
    compare_columns = {"change_perc": "Change (%)", "close": "Close"}
    export_price_df = get_historical_price_export_df(
        tickers, period_code, from_date, to_date, compare_columns=compare_columns
    )
    if export_price_df is None:
        return None
    return export_price_df.sort_values("Date")


def create_fig(df: DataFrame, period_code: int, cmd_context: Dict[str, Any], range_selector: bool = False) -> Figure:
    layout = dict(
        autosize=True,
        hovermode="closest",
        legend=dict(font=dict(size=11), orientation="h", yanchor="top", y=0.98, xanchor="left", x=0.01),
    )
    fig = px.line(
        df,
        x="Date",
        y=df.columns,
        title=cmd_context["plot_title"],
        labels={"value": "Change (%)"},
    )
    fig.update_xaxes(
        rangeslider_visible=False,
        spikemode="across",
        spikesnap="cursor",
    )
    if range_selector:
        fig.update_xaxes(rangeselector=get_date_range(period_code))
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(
        **layout,
        xaxis_title=None,
        **get_plot_default_layout(),
        margin=dict(b=15, l=90, r=20),
    )

    return fig


@price.command()
@click.pass_context
@click.option(
    "--period",
    "-p",
    type=PricePeriodParamType(),
    default="1M",
    help="Historical price period.",
)
@click.option("--from_date", "-f", type=DateTime(), help="Histotical price from date.")
@click.option("--to_date", "-t", type=DateTime(), help="Histotical price to date.")
@click.option(
    "--tickers",
    "-k",
    type=TickerParamType(),
    required=True,
    callback=validate_tickers,
    help="Comma-separated list of tickers.",
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def compare(
    ctx: click.Context,
    period: str,
    from_date: Optional[DateTime],
    to_date: Optional[DateTime],
    tickers: str,
    export_path: Optional[str],
) -> None:
    """
    Compares historical prices of given companies. TICKERS is a comma-separated list of tickers.

    Examples:

    `i8 price compare --period 3Y --tickers AMD,INTC,QCOM`
    """
    command_path = get_click_command_path(ctx)
    period = period.replace(" ", "").upper()
    period_code = get_period_code(period)
    tickers_list = tickers.replace(" ", "").upper().split(",")
    plot_title = f"Comparison of {', '.join(tickers_list)} prices"
    plot_title = " and ".join(plot_title.rsplit(", ", 1))

    cmd_context = {
        "command_path": command_path,
        "tickers": tickers_list,
        "plot_title": plot_title,
        "plot_type": PlotType.CHART.value,
    }

    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        if export_path:
            df = get_export_data(tickers_list, period_code, cast(str, from_date), cast(str, to_date))
            if df is None:
                status.stop()
                console.print("No data found!")
                return
        else:
            df = get_price_data(tickers_list, period_code, cast(str, from_date), cast(str, to_date))
            if df is None:
                status.stop()
                console.print("No data found!")
                return
            status.update("Generating plot...")
            fig = create_fig(df, period_code, cmd_context)

    if export_path:
        if export_path.split(".")[-1] == "html":
            table = df2Table(df)
            export_to_html(table, export_path)
            return
        export_data(
            df,
            export_path,
            index=True,
            column_width=20,
            column_format=APP_SETTINGS["styles"]["xlsx"]["price"]["column"],
        )
    else:
        serve_plot(fig, cmd_context)
