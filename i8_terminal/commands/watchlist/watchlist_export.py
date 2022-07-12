import click
import investor8_sdk
import pandas as pd
from rich.console import Console

from i8_terminal.commands.watchlist import watchlist
from i8_terminal.common.cli import pass_command
from i8_terminal.common.metrics import (
    get_current_metrics_df,
    prepare_current_metrics_formatted_df,
)
from i8_terminal.config import APP_SETTINGS, USER_SETTINGS
from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType


def export_watchlist_data(
    name: str,
    path: str,
) -> None:
    console = Console()
    extension = path.split(".")[-1]
    if extension != "xlsx":
        console.print("\n⚠ Error: path is not valid", style="yellow")
        return
    writer = pd.ExcelWriter(path, engine="xlsxwriter")
    workbook = writer.book
    column_width = 18
    header_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["default"]["header"])
    metric_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["default"]["metric"])
    column_format = workbook.add_format(APP_SETTINGS["styles"]["xlsx"]["company"]["column"])
    tickers = (
        investor8_sdk.UserApi().get_watchlist_by_name_user_id(name=name, user_id=USER_SETTINGS.get("user_id")).tickers
    )
    summary_df = prepare_current_metrics_formatted_df(
        get_current_metrics_df(
            ",".join(tickers), "company_name,stock_exchange,price.r,change,52_week_low,52_week_high,marketcap"
        ),
        "store",
    )
    summary_df.to_excel(writer, sheet_name="Summary", startrow=1, header=False, index=False)
    worksheet = writer.sheets["Summary"]
    headers = summary_df.columns.tolist()
    for col_num, value in enumerate(headers):
        if type(value) is tuple:
            worksheet.merge_range(0, col_num, len(value) - 1, col_num, " ".join(reversed(value)), header_format)
        else:
            worksheet.write(0, col_num, value, header_format)
    worksheet.set_column(0, 0, 20, metric_format)
    worksheet.set_column(1, len(summary_df.columns) - 1, column_width, column_format)
    financials_df = prepare_current_metrics_formatted_df(
        get_current_metrics_df(
            ",".join(tickers),
            "total_revenue,net_income,basic_eps,net_cash_from_operating_activities,total_assets,total_liabilities",
        ),
        "store",
    )
    financials_df.to_excel(writer, sheet_name="Financials", startrow=1, header=False, index=False)
    worksheet = writer.sheets["Financials"]
    headers = financials_df.columns.tolist()
    for col_num, value in enumerate(headers):
        if type(value) is tuple:
            worksheet.merge_range(0, col_num, len(value) - 1, col_num, " ".join(reversed(value)), header_format)
        else:
            worksheet.write(0, col_num, value, header_format)
    worksheet.set_column(0, 0, 20, metric_format)
    worksheet.set_column(1, len(financials_df.columns) - 1, column_width, column_format)
    writer.save()
    console.print(f"\nData is saved on: {path}")


@watchlist.command()
@click.option(
    "--name",
    "-n",
    type=UserWatchlistsParamType(),
    required=True,
    help="Name of the watchlist.",
)
@click.option("--path", "path", "-p", required=True, help="Filename to export the output to.")
@pass_command
def export(name: str, path: str) -> None:
    """
    Exports a given watchlist to an excel file.

    Examples:

    `i8 watchlist export --name MyWatchlist --path MyWatchlist.xlsx`

    """
    console = Console()
    with console.status("Fetching data...", spinner="material"):
        export_watchlist_data(name, path)
