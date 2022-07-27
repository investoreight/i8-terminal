from typing import Any, Dict, Tuple

import click
import investor8_sdk
import pandas as pd
import plotly.graph_objects as go
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from i8_terminal.commands.company import company
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import format_number
from i8_terminal.common.stock_info import validate_ticker
from i8_terminal.types.ticker_param_type import TickerParamType


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="main", ratio=2),
    )
    layout["main"].split_row(
        Layout(name="company_info", ratio=2),
        Layout(name="about_company", ratio=2, minimum_size=50),
    )
    layout["company_info"].split(Layout(name="summary_box"), Layout(name="price_box"))
    return layout


def get_stock_info(ticker: str) -> Tuple[investor8_sdk.StockInfoApi, investor8_sdk.StockInfoApi]:
    si = investor8_sdk.StockInfoApi().get_stock_summary(ticker)
    ci = investor8_sdk.StockInfoApi().get_company_info(ticker)

    return si, ci


def get_price_details_content(si: investor8_sdk.StockInfoApi) -> Table:
    price_details = Table.grid()
    price_details.add_column(justify="left", width=18)
    price_details.add_column(justify="center")
    price_details.add_row("Price", str(si.current_price))
    price_details.add_row("Change Percent", str(format_number(si.change_perc, unit="percentage")))
    price_details.add_row("Low", str(si.low52_w))
    price_details.add_row("High", str(si.high52_w))

    return price_details


def get_stock_info_dataframe(ticker: str) -> Tuple[Dict[str, Any], Dict[str, Any], go.Figure, go.Figure]:
    si, ci = get_stock_info(ticker)
    si_df = pd.DataFrame(
        {
            "Ticker": [si.ticker],
            "Exchange": [si.exchange],
            "Company Name": [si.name],
            "Sector": [si.sector],
            "52W High": [si.high52_w],
            "52W Low": [si.low52_w],
            "EPS": [si.basic_eps],
            "Market Cap": [si.market_cap],
            "P/E (TTM)": [si.pe_ratio_ttm],
            "Dividend Yeild (TTM)": [si.dividend_yield_ttm],
            "Current Price": [si.current_price],
            "Change": [si.change],
            "Change (%)": [si.change_perc],
            "Previous Close": [si.previous_close],
        }
    )
    ci_df = pd.DataFrame(
        {
            "Ticker": [ci.ticker],
            "Sector": [ci.sector],
            "Industry Category": [ci.industry_category],
            "Industry Group": [ci.industry_group],
            "Employee": [ci.employees],
            "Market Cap": [si.market_cap],
            "Description": [ci.description],
        }
    )

    market_cap = si.market_cap
    # TODO: formatting and visualization has to be done dynamically
    visible = ["Current Price", "Change (%)", "52W High", "52W Low", "EPS", "P/E (TTM)", "Dividend Yeild (TTM)"]
    format = ["$", ".2%", "$", "$", ".2", ".2", ".2"]
    widths = [3, 3, 2.5, 2, 2, 2.5, 4]
    fig_si = go.Figure(
        data=[
            go.Table(
                columnwidth=widths,
                header=dict(values=[f"<b>{v}</b>" for v in visible], fill_color="#00b08f", align="center"),
                cells=dict(values=[si_df[c] for c in visible], fill_color="white", align="center", format=format),
            )
        ]
    )
    company_name = si_df["Company Name"][0]
    exchange = si_df["Exchange"][0]
    fig_si.update_layout(title=f"Key Data: {ticker} - {company_name} ({exchange})", font=dict(color="#015560"))

    ci_df_vis = ci_df.copy()
    mc_format = "M"
    if market_cap > 1e12:
        market_cap /= 1e12
        mc_format = "T"
    elif market_cap > 1e9:
        market_cap /= 1e9
        mc_format = "B"
    elif market_cap > 1e6:
        market_cap /= 1e6

    ci_df_vis["Market Cap"] = "${:.2f}{}".format(market_cap, mc_format)
    desc = ci_df_vis.columns
    ci_df_vis = ci_df_vis.T
    ci_df_vis["description"] = desc
    ci_df_vis.columns = ["Info", "Description"]
    widths = [90, 400]
    fig_ci = go.Figure(
        data=[
            go.Table(
                columnwidth=widths,
                header=dict(
                    values=["<b>Description</b>", "<b>Information</b>"],
                    font=dict(color="white", size=12),
                    fill_color="#015560",
                    align="left",
                ),
                cells=dict(
                    values=[ci_df_vis[c] for c in ["Description", "Info"]],
                    fill_color=[["#00b08f"] * ci_df_vis.shape[0], ["white"] * ci_df_vis.shape[0]],
                    align="left",
                ),
            )
        ]
    )
    company_name = si_df["Company Name"][0]
    exchange = si_df["Exchange"][0]
    fig_ci.update_layout(title=f" Company Info: {ticker} - {company_name} ({exchange})", font=dict(color="#015560"))
    fig_si.update_layout(height=280)
    return si_df, ci_df, fig_si, fig_ci


@company.command()
@click.option(
    "--ticker", "-k", type=TickerParamType(), required=True, callback=validate_ticker, help="Ticker or company name."
)
@pass_command
def details(ticker: str) -> None:
    """
    Get details for a given company.

    Examples:

    `i8 company details --ticker MSFT`

    """
    template = """
# {0}
- Ticker: {1}
- Exchange: {2}
- Sector: {3}
- [https://www.investoreight.com/stock/{1}](https://www.investoreight.com/stock/{1})
"""
    console = Console()
    si, ci = get_stock_info(ticker)

    md = Markdown(template.format(si.name, si.ticker, si.exchange, si.sector))
    price_details = get_price_details_content(si)
    about_company = Text.from_markup(ci.description)

    layout = make_layout()
    layout["summary_box"].update(Panel(md, border_style="green", title="Summary"))
    layout["price_box"].update(
        Panel(Align.center(price_details, vertical="middle"), border_style="green", title="Price")
    )
    layout["about_company"].update(Panel(about_company, border_style="green", title="About Company"))
    console.print(layout)
