from datetime import datetime
from time import sleep
from typing import Optional

import arrow
import click
import investor8_sdk
import pandas as pd
from pandas.core.frame import DataFrame
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from i8_terminal.commands.market import market
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import get_formatter
from i8_terminal.common.layout import df2Table, format_df


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")
    layout["root"].split(Layout(name="main"))
    layout["main"].split_row(
        Layout(name="side_left"),
        Layout(name="side_right"),
    )
    layout["side_left"].split(
        Layout(name="title", minimum_size=8, ratio=1),
        Layout(name="major_indices", minimum_size=9, ratio=1),
        Layout(name="today_winners", minimum_size=11),
    )
    layout["side_right"].split(
        Layout(name="sectors", minimum_size=17, ratio=2), Layout(name="today_losers", minimum_size=11)
    )

    return layout


def format_price_df(df: DataFrame, target: str, is_index: bool = False) -> DataFrame:
    formatters = {
        "latest_price": get_formatter("number", target),
        "change_perc": get_formatter("perc", target),
    }
    col_names = {
        "ticker": "Ticker",
        "latest_price": "Level" if is_index else "Price",
        "change_perc": "Change (%)",
    }
    if "name" in df.columns:
        df["name"] = df["name"].apply(lambda x: x if len(x) < 20 else x[:17] + "...")
        col_names["name"] = "Index" if is_index else "Company Name"
    if "price_time" in df.columns:
        col_names["price_time"] = "price_time"
    return format_df(df, col_names, formatters)


def format_sector_df(df: DataFrame, target: str) -> DataFrame:
    formatters = {
        "_return": get_formatter("perc", target),
    }
    col_names = {
        "sector": "Sector",
        "_return": "Change (%)",
    }
    return format_df(df, col_names, formatters)


def get_major_indices_df() -> Optional[DataFrame]:
    indices = {}
    try:
        indices = investor8_sdk.PriceApi().get_latest_market_indices()
    except Exception as e:
        click.echo(e.body)  # type: ignore
        return None

    df = pd.DataFrame([{"name": k, **v.to_dict()} for k, v in indices.items()])[
        ["ticker", "name", "latest_price", "change_perc"]
    ]
    return format_price_df(df, "console", is_index=True)


def get_today_top_stocks_df(top_stocks_type: str, count: int = 5) -> Optional[DataFrame]:
    stocks = []
    try:
        stocks = investor8_sdk.ScreenerApi().get_top_stocks(top_stocks_type, count=count, index="$SPX")
    except Exception as e:
        click.echo(e.body)  # type: ignore
        return None
    df = pd.DataFrame([d.to_dict() for d in stocks])[["ticker", "name", "latest_price", "change_perc"]]

    return format_price_df(df, "console")


def get_sector_returns_df() -> Optional[DataFrame]:
    sectors = None
    try:
        sectors = investor8_sdk.ScreenerApi().get_all_sectors_returns(period=1)
    except Exception as e:
        click.echo(e.body)  # type: ignore
        return None

    df = pd.DataFrame([d.to_dict() for d in sectors["1D"]])[["sector", "_return"]]

    return format_sector_df(df, "console")


def get_today_intraday_prices_df(tickers: str, indices: str, size: int = 10) -> Optional[DataFrame]:
    all_prices = {}  # type: ignore
    for tk_list in [tickers, indices]:
        try:
            prices = investor8_sdk.PriceApi().get_today_intraday_prices(tickers=tk_list, size=size)
        except Exception as e:
            click.echo(e.body)  # type: ignore
            return None
        all_prices = {**all_prices, **prices}
    prices_list = []
    for v in list(all_prices.values()):
        for p in v:
            prices_list.append(p.to_dict())
    df = pd.DataFrame(prices_list)[["ticker", "latest_price", "change_perc", "price_time"]]

    return format_price_df(df, "console")


def get_title_table(date: Optional[datetime] = None) -> Table:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=2)
    grid.add_row("[b]Investoreight[/b] Market Summary")
    dt = (
        date.strftime("%b %d %Y, %I:%M:%S %p ET").replace(":", "[blink]:[/]")
        if date
        else arrow.now("US/Eastern").datetime.strftime("%b %d %Y, %I:%M:%S %p ET").replace(":", "[blink]:[/]")
    )
    grid.add_row(
        ":stopwatch:  [magenta]" + dt,
    )
    return grid


def get_market_summary_panels(name: str, df: DataFrame) -> Panel:
    return {
        "major_ind": Panel(
            df2Table(df),
            border_style="blue",
            title="Major U.S. Indices",
        ),
        "winners": Panel(
            df2Table(df),
            border_style="green",
            title="S&P500 Winners",
        ),
        "losers": Panel(
            df2Table(df),
            border_style="red",
            title="S&P500 Losers",
        ),
    }[name]


@market.command()
@click.option("--live", is_flag=True, default=False, help="Print live results of market summary on terminal.")
@pass_command
def summary(live: bool) -> None:
    console = Console()
    price_size = 10
    with console.status("Fetching data...", spinner="material") as status:
        sectors_df = get_sector_returns_df()
        major_indices_df = get_major_indices_df()
        today_winners_df = get_today_top_stocks_df("winners")
        today_losers_df = get_today_top_stocks_df("losers")
        if sectors_df is None or major_indices_df is None or today_winners_df is None or today_losers_df is None:
            return
        tickers = ",".join(set(today_winners_df.Ticker.to_list() + today_losers_df.Ticker.to_list()))
        indices = ",".join(set(major_indices_df.Ticker.to_list()))
        layout = make_layout()
        # Initialize layout
        dt_now = arrow.now("US/Eastern")
        layout["title"].update(Panel(get_title_table(dt_now.datetime), border_style="blue", padding=(2, 2)))
        layout["sectors"].update(Panel(df2Table(sectors_df), border_style="blue", title="U.S. Sectors"))
        intraday_prices = None
        if live:
            intraday_prices = get_today_intraday_prices_df(tickers, indices, price_size)
            if intraday_prices is not None:
                stock_cols = ["Ticker", "Price", "Change (%)", "Company Name"]
                index_cols = ["Index", "Level", "Change (%)"]
                renamed_cols = {"Price_y": "Price", "Change (%)_y": "Change (%)"}
                cols = ["Ticker", "Company Name", "Price_y", "Change (%)_y", "price_time"]
                today_winners_df = today_winners_df.merge(intraday_prices, on="Ticker")[cols]
                today_winners_df.rename(columns=renamed_cols, inplace=True)
                today_losers_df = today_losers_df.merge(intraday_prices, on="Ticker")[cols]
                today_losers_df.rename(columns=renamed_cols, inplace=True)
                major_indices_df = major_indices_df.merge(intraday_prices, on="Ticker")[
                    ["Ticker", "Index", "Price", "Change (%)_y", "price_time"]
                ]
                major_indices_df.rename(columns={"Price": "Level", "Change (%)_y": "Change (%)"}, inplace=True)
                # Initialize layout
                layout["major_indices"].update(
                    get_market_summary_panels(
                        "major_ind", major_indices_df.groupby("Index").nth(0).reset_index()[index_cols]
                    )
                )
                layout["today_winners"].update(
                    get_market_summary_panels(
                        "winners", today_winners_df.groupby("Ticker").nth(0).reset_index()[stock_cols]
                    )
                )
                layout["today_losers"].update(
                    get_market_summary_panels(
                        "losers",
                        today_losers_df.groupby("Ticker").nth(0).reset_index()[stock_cols],
                    )
                )
                status.stop()
                with Live(layout, refresh_per_second=4):
                    for i in range(2, price_size * 2):
                        dt_now = dt_now.shift(seconds=+1)
                        layout["title"].update(
                            Panel(get_title_table(dt_now.datetime), border_style="blue", padding=(2, 2))
                        )
                        if i % 2 == 0:  # Update prices every two secends
                            idx = int(i / 2)
                            layout["major_indices"].update(
                                get_market_summary_panels(
                                    "major_ind", major_indices_df.groupby("Index").nth(idx).reset_index()[index_cols]
                                )
                            )
                            layout["today_winners"].update(
                                get_market_summary_panels(
                                    "winners", today_winners_df.groupby("Ticker").nth(idx).reset_index()[stock_cols]
                                )
                            )
                            layout["today_losers"].update(
                                get_market_summary_panels(
                                    "losers", today_losers_df.groupby("Ticker").nth(idx).reset_index()[stock_cols]
                                )
                            )
                        sleep(1)

        elif not live or (live and intraday_prices is None):
            status.stop()
            layout["major_indices"].update(
                Panel(df2Table(major_indices_df), border_style="blue", title="Major U.S. Indices")
            )
            layout["today_winners"].update(
                Panel(df2Table(today_winners_df), border_style="green", title="S&P500 Winners")
            )
            layout["today_losers"].update(Panel(df2Table(today_losers_df), border_style="red", title="S&P500 Losers"))
            console.print(layout)
