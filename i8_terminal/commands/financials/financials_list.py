from typing import Any, Dict, Optional

import click
import investor8_sdk
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from rich.console import Console

from i8_terminal.commands.financials import financials
from i8_terminal.common.cli import pass_command
from i8_terminal.common.financials import (
    fin_df2export_df,
    fin_df2Tree,
    find_similar_statement,
    get_statements_codes,
    get_statements_disp_name,
    parse_identifier,
    prepare_financials_df,
)
from i8_terminal.common.metrics import get_all_financial_metrics_df
from i8_terminal.common.utils import export_data
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.fin_identifier_param_type import FinancialsIdentifierParamType
from i8_terminal.types.fin_statement_param_type import FinancialStatementParamType
from i8_terminal.types.period_type_param_type import PeriodTypeParamType


def get_standardized_financials(
    identifiers_dict: Dict[str, str],
    statement: str,
    period_type: Optional[str],
    period_size: int = 4,
    exportize: Optional[bool] = False,
) -> Optional[Dict[str, Any]]:
    fins = []
    if identifiers_dict.get("fiscal_period"):
        fins = [
            investor8_sdk.FinancialsApi().get_financials_single(
                ticker=identifiers_dict["ticker"],
                stat_code=statement,
                fiscal_year=identifiers_dict.get("fiscal_year"),
                fiscal_period=identifiers_dict.get("fiscal_period"),
            )
        ]
    else:
        period_type = "FY" if not period_type else period_type
        fins = investor8_sdk.FinancialsApi().get_list_standardized_financials(
            ticker=identifiers_dict["ticker"],
            stat_code=statement,
            period_type=period_type,
            end_year=identifiers_dict.get("fiscal_year", ""),
        )
    if not fins:
        return None
    return prepare_financials_df(fins, period_size, include_ticker=False, exportize=exportize)


def dummy(
    identifiers_dict: Dict[str, str],
    statement: str,
    period_type: Optional[str],
    period_size: int = 4,
    exportize: Optional[bool] = False,
):
    fins = []
    if identifiers_dict.get("fiscal_period"):
        fins = [
            investor8_sdk.FinancialsApi().get_financials_single(
                ticker=identifiers_dict["ticker"],
                stat_code=statement,
                fiscal_year=identifiers_dict.get("fiscal_year"),
                fiscal_period=identifiers_dict.get("fiscal_period"),
            )
        ]
    else:
        period_type = "FY" if not period_type else period_type
        fins = investor8_sdk.FinancialsApi().get_list_standardized_financials(
            ticker=identifiers_dict["ticker"],
            stat_code=statement,
            period_type=period_type,
            end_year=identifiers_dict.get("fiscal_year", ""),
        )
        fins
    return fins


def get_financials_df(ticker: str, statement="income_statement", period_type="FY") -> pd.DataFrame:
    proper_tags = [
        "Operating Revenue",
        "Total Revenue",
        "Operating Cost of Revenue",
        "Total Cost of Revenue",
        "Total Gross Profit",
        "Selling, General & Admin Expense",
        "Research & Development Expense",
        "Total Operating Expenses",
        "Total Operating Income",
        "Other Income / (Expense), net",
        "Total Other Income / (Expense), net",
        "Total Pre-Tax Income",
        "Income Tax Expense",
        "Net Income / (Loss) Continuing Operations",
        "Consolidated Net Income / (Loss)",
        "Net Income / (Loss) Attributable to Common Shareholders",
        "Weighted Average Basic Shares Outstanding",
        "Basic Earnings per Share",
        "Weighted Average Diluted Shares Outstanding",
        "Diluted Earnings per Share",
        "Weighted Average Basic & Diluted Shares Outstanding",
        "Cash Dividends to Common per Share",
    ]
    df = get_standardized_financials(identifiers_dict={"ticker": ticker}, statement=statement, period_type=period_type)[
        "data"
    ]
    df["tag"] = proper_tags
    return df


@financials.command()
@click.option(
    "--identifier",
    "-i",
    type=FinancialsIdentifierParamType(),
    required=True,
    help="Comma-separated list of identifiers.",
)
@click.option(
    "--statement",
    "-s",
    type=FinancialStatementParamType(),
    default="income",
    help="Type of financial statement.",
)
@click.option(
    "--period_type",
    "-m",
    type=PeriodTypeParamType(),
    help="Period by which you want to view the report. Possible values are `FY` for yearly, `Q` for quarterly, and `TTM` for TTM reports.",
)
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def list(identifier: str, statement: str, period_type: Optional[str], export_path: Optional[str]) -> None:
    """
    Lists financial metrics of a given company.

    Examples:

    `i8 financials list --period_type FY --statement income --identifier AAPL-2020-FY`

    """
    matched_statement = find_similar_statement(statement)
    if not matched_statement:
        click.echo(
            f"`{statement}` is not a valid statement code. \nValid statement codes: {', '.join(get_statements_codes())}"
        )
        click.echo("Unknown Statement Code!")
        return
    identifiers_dict = parse_identifier(identifier, period_type)
    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        fins = get_standardized_financials(
            identifiers_dict, matched_statement, period_type, period_size=4, exportize=True if export_path else False
        )
        if fins is None:
            status.stop()
            click.echo("No data found!")
            return
        periods_list = fins["data"].columns[1:].to_list()
        df_metrics = get_all_financial_metrics_df()
        df = fins["data"].merge(df_metrics, on="tag", how="left")
        df["section_name"] = df["section_name"].apply(lambda x: "Others" if not x or x == "-" else x)
        df = df.astype(object).replace(np.nan, None)  # Replace nan with None

    if export_path:
        export_df = fin_df2export_df(df, periods_list)
        export_data(
            export_df,
            export_path,
            column_width=18,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
    else:
        tree = fin_df2Tree(
            df,
            fins["header"],
            periods_list,
            title=f"{identifiers_dict['ticker'].upper()} {get_statements_disp_name(matched_statement)}",
        )
        console.print(tree)


def visualize_financials(df, ticker):
    fig = make_subplots(
        rows=5,
        cols=1,
        # subplot_titles=('Revenue', 'title 2', 'title 3','title 4', 'title 5')
    )
    visible = ["tag", "2021\n(Annual)", "2020\n(Annual)", "2019\n(Annual)", "2018\n(Annual)"]
    revenu_filter = [
        "Operating Revenue",
        "Total Revenue",
        "Operating Cost of Revenue",
        "Total Cost of Revenue",
        "Total Gross Profit",
    ]
    net_incom_filter = ["Consolidated Net Income / (Loss)", "Net Income / (Loss) Continuing Operations"]
    expense_filter = ["Selling, General & Admin Expense", "Research & Development Expense", "Total Operating Expenses"]
    income_filtere = [
        "Total Operating Income",
        "Other Income / (Expense), net",
        "Total Other Income / (Expense), net",
        "Total Pre-Tax Income",
        "Income Tax Expense",
        "Net Income / (Loss) Continuing Operations",
        "Consolidated Net Income / (Loss) ",
        "Net Income / (Loss) Attributable to Common Shareholders",
    ]
    suplements_filter = [
        "Weighted Average Basic Shares Outstanding",
        "Basic Earnings per Share",
        "Weighted Average Diluted Shares Outstanding",
        "Diluted Earnings per Share",
        "Weighted Average Basic & Diluted Shares Outstanding",
        "Cash Dividends to Common per Share",
    ]

    df_revenue = df.loc[df["tag"].isin(revenu_filter)]
    df_net_income = df.loc[df["tag"].isin(net_incom_filter)]
    df_expense = df.loc[df["tag"].isin(expense_filter)]
    df_income = df.loc[df["tag"].isin(income_filtere)]
    df_suplement = df.loc[df["tag"].isin(suplements_filter)]

    fig_revenue = make_table_figure(df_revenue, visible, "Revenue", ticker)
    # fig_net_income = make_table_figure(df_net_income, visible, "Net Income", ticker)
    fig_expense = make_table_figure(df_expense, visible, "Expense", ticker)
    fig_income = make_table_figure(df_income, visible, "Income", ticker)
    fig_supplement = make_table_figure(df_suplement, visible, "Supplements", ticker)

    return fig_revenue, fig_expense, fig_income, fig_supplement


def make_table_figure(df, visible, name, ticker):
    fig_table = go.Figure(
        data=[
            go.Table(
                columnwidth=[5, 3, 3, 3, 3],
                header=dict(
                    values=["" if v == "tag" else f"<b>{v}</b>" for v in visible],
                    font=dict(color="white", size=12),
                    fill_color="#015560",
                    align="center",
                ),
                cells=dict(
                    values=[df[c] for c in visible],
                    fill_color=[["#00b08f"] * 5, ["white"] * 20],
                    align=["left"] * df.shape[0] + ["center"] * df.shape[0] * (df.shape[1] - 1),
                ),
            )
        ]
    )
    fig_table.update_layout(title=f"{ticker} - {name}", font=dict(color="#015560"))
    fig_table.update_layout(width=1000, height=500)
    return fig_table
