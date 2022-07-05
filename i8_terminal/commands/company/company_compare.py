from typing import Optional

import click
import numpy as np
import pandas as pd
from pandas import DataFrame
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from i8_terminal.commands.company import company
from i8_terminal.common.cli import pass_command
from i8_terminal.common.layout import format_metrics_df
from i8_terminal.common.metrics import get_current_metrics_df
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.ticker_param_type import TickerParamType

metrics = {
    "Summary": "company_name,stock_exchange,sector,industry_group,marketcap,pe_ratio_ttm,price,change",
    "Financials": "operating_revenue,total_revenue,total_gross_profit,other_income,basic_eps,diluted_eps,adj_basic_eps",
    "Price Returns": "return_1w,return_1m,return_3m,return_6m,return_ytd,return_1y,return_2y,return_5y",
}


def get_section_stock_infos_df(tickers: str, target: str, section: str) -> Optional[DataFrame]:
    df = get_current_metrics_df(tickers, APP_SETTINGS["commands"]["company_compare"]["metrics"][section])
    if df is None:
        return None
    if section == "Financials":
        fyq_rows = []
        for ticker, ticker_df in df.groupby("Ticker"):
            fyq_rows.append(
                {
                    "Ticker": ticker,
                    "metric_name": "fyq",
                    "value": ticker_df["period"].values[0],
                    "display_name": "FYQ",
                    "data_format": "str",
                    "display_format": "str",
                }
            )
        df = pd.concat([pd.DataFrame(fyq_rows), df], ignore_index=True, axis=0)
    formatted_df = format_metrics_df(df, target)
    formatted_df = formatted_df.pivot(index="display_name", columns="Ticker", values="value").reset_index(level=0)
    formatted_df["Section"] = section
    sorter = df["display_name"].unique()
    sorter_index = dict(zip(sorter, range(len(sorter))))
    formatted_df["Rank"] = formatted_df["display_name"].map(sorter_index)
    formatted_df.sort_values("Rank", inplace=True)
    formatted_df.drop("Rank", axis=1, inplace=True)
    return formatted_df


def get_stock_infos_df(tickers: str, target: str) -> Optional[DataFrame]:
    return (
        pd.concat(
            [
                get_section_stock_infos_df(tickers, target, section)
                for section in APP_SETTINGS["commands"]["company_compare"]["metrics"]
            ]
        )
        .rename(columns={"display_name": "Name"})
        .astype(object)
        .replace(np.nan, "N/A")
    )


def companies_df2tree(df: DataFrame, tickers: str) -> Tree:
    tickers_list = tickers.replace(" ", "").upper().split(",")
    col_width = 40
    plot_title = f"Comparison of {', '.join(tickers_list)}"
    plot_title = " and ".join(plot_title.rsplit(", ", 1))
    tree = Tree(Panel(plot_title, width=50))
    # Add header table to tree
    header_table = Table(
        width=50 + (col_width * (len(tickers_list) - 1)), show_lines=False, show_header=False, box=None
    )
    header_table.add_column(width=35, style="magenta")
    for p in tickers_list:
        header_table.add_column(width=col_width, justify="right", style="magenta")
    header_table.add_row("Ticker", *tickers_list)
    tree.add(header_table)

    for sec_name, sec_values in df.groupby("Section", sort=False):
        sec_branch = tree.add(f"[cyan]{sec_name}")
        for i, r in sec_values.iterrows():
            t = Table(width=46 + (col_width * (len(tickers_list) - 1)), show_lines=False, show_header=False, box=None)
            t.add_column(width=31)
            for tk in tickers_list:
                t.add_column(width=col_width, justify="right")
            t.add_row(r["Name"], *[f"{d}" for d in r[tickers_list].values])
            sec_branch.add(t)

    return tree


def export_companies_data(
    export_df: pd.DataFrame,
    export_path: str,
) -> None:
    console = Console()
    extension = export_path.split(".")[-1]
    if extension == "csv":
        export_df.drop(columns=["Section"], inplace=True)  # type: ignore
        export_df.to_csv(export_path, index=False)
        console.print(f"Data is saved on: {export_path}")
    elif extension == "xlsx":
        writer = pd.ExcelWriter(export_path, engine="xlsxwriter")
        for sec_name, sec_values in export_df.groupby("Section", sort=False):
            sec_values.drop(columns=["Section"], inplace=True)  # type: ignore
            sec_values.rename(columns={"Name": ""}, inplace=True)
            sec_values.to_excel(writer, sheet_name=sec_name, startrow=1, header=False, index=False)
            workbook = writer.book
            column_width = 18
            header_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["default"]["header"])
            metric_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["default"]["metric"])
            column_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["company"]["column"])
            worksheet = writer.sheets[sec_name]
            headers = sec_values.columns.tolist()
            for col_num, value in enumerate(headers):
                if type(value) is tuple:
                    worksheet.merge_range(0, col_num, len(value) - 1, col_num, " ".join(reversed(value)), header_format)
                else:
                    worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(0, 0, 20, metric_format)
            worksheet.set_column(1, len(sec_values.columns) - 1, column_width, column_format)
        writer.save()
        console.print(f"Data is saved on: {export_path}")
    else:
        console.print("export_path is not valid")


@company.command()
@click.option("--tickers", "-k", type=TickerParamType(), required=True, help="Comma-separated list of tickers.")
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def compare(tickers: str, export_path: Optional[str]) -> None:
    """
    Compare details of the given companies.

    Examples:

    `i8 company compare --tickers MSFT,AAPL`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        stock_infos_df = get_stock_infos_df(tickers, target="store" if export_path else "console")
        if stock_infos_df is None:
            status.stop()
            click.echo("No data found!")
            return
    if export_path:
        export_companies_data(
            stock_infos_df,
            export_path,
        )
    else:
        tree = companies_df2tree(stock_infos_df, tickers)
        console.print(tree)
