from typing import Tuple

import click
import investor8_sdk
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
