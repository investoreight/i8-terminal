import re
from typing import Any, Dict, List, Optional

import arrow
import pandas as pd
from investor8_sdk.models.standardized_financial import StandardizedFinancial
from pandas.core.frame import DataFrame
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from i8_terminal.common.formatting import format_number
from i8_terminal.common.layout import format_df
from i8_terminal.common.utils import similarity
from i8_terminal.config import APP_SETTINGS


def get_statements_codes() -> List[str]:
    return ["cash_flow_statement", "income_statement", "balance_sheet_statement"]


def get_statements_disp_name(stmt: str) -> Optional[str]:
    return {
        "cash_flow_statement": "Cash Flow Statement",
        "income_statement": "Income Statement",
        "balance_sheet_statement": "Balance Sheet Statement",
    }.get(stmt)


def get_period_types() -> List[str]:
    return ["FY", "Q", "TTM", "YTD"]


def get_period_type_disp_name(period: str) -> Optional[str]:
    return {
        "FY": "Annual (FY)",
        "Q": "Quarterly (Q)",
        "TTM": "TTM",
        "YTD": "YTD",
    }.get(period)


def find_similar_statement(statement: str) -> Optional[str]:
    default_indicators = {"inc": "income_statement", "bs": "balance_sheet_statement", "cf": "cash_flow_statement"}
    defualt_ind = default_indicators.get(statement.lower())
    if defualt_ind:
        return defualt_ind
    statement_dicts = {
        "cash": "cash_flow_statement",
        "cash_flow": "cash_flow_statement",
        "cash_flow_statement": "cash_flow_statement",
        "income": "income_statement",
        "income_statement": "income_statement",
        "balance": "balance_sheet_statement",
        "balance_sheet": "balance_sheet_statement",
        "balance_sheet_statement": "balance_sheet_statement",
    }
    best_match_similarity = 0.0
    best_match = ""
    for stmt in statement_dicts.keys():
        sim = similarity(statement.lower(), stmt.lower())
        if sim > best_match_similarity:
            best_match_similarity = sim
            best_match = stmt
    if best_match_similarity < APP_SETTINGS["metrics"]["similarity_threshold"]:
        return None

    return statement_dicts.get(best_match)


def parse_identifier(identifier: str, period_type: Optional[str]) -> Dict[str, str]:
    identifiers_dict = {}
    parsed_identifier = re.split("[-.,_]", identifier.replace(" ", ""))
    identifiers_dict["ticker"] = parsed_identifier[0]
    if len(parsed_identifier) == 3:
        # {ticker}_{fiscal_year}_{fiscal_period}
        identifiers_dict["fiscal_year"] = parsed_identifier[1]
        identifiers_dict["fiscal_period"] = (
            parsed_identifier[2] if parsed_identifier[2] not in ["Q4YTD", "Q4TTM"] else "FY"
        )
    elif len(parsed_identifier) == 2:
        # {ticker}_{fiscal_year}
        if parsed_identifier[1].isnumeric():
            identifiers_dict["fiscal_year"] = parsed_identifier[1]
            if not period_type or period_type.upper() == "FY":
                identifiers_dict["fiscal_period"] = "FY"
        # {ticker}_{fiscal_period}
        else:
            identifiers_dict["fiscal_period"] = parsed_identifier[1]

    return identifiers_dict


def render_metrics_table(table: Table, df: DataFrame, periods_list: List[str], col_width: int) -> Table:
    for p in periods_list:
        table.add_column(width=col_width, justify="right")
    for i, r in df.iterrows():
        if r["is_significant"]:
            table.add_row(f'[cyan]{r["name"]}[cyan]', *[f"[cyan]{d}[cyan]" for d in r[periods_list].values])
        else:
            table.add_row(r["name"], *r[periods_list].values)

    return table


def fin_df2Tree(df: DataFrame, header: Dict[str, List[str]], periods_list: List[str], title: str) -> Tree:
    col_width = 12
    tree = Tree(Panel(title, width=55))
    # Add header table to tree
    header_table = Table(
        width=85 + (col_width * (len(periods_list) - 1)), show_lines=False, show_header=False, box=None
    )
    header_table.add_column(width=64, style="magenta")
    for p in periods_list:
        header_table.add_column(width=col_width, justify="center", style="magenta")
    header_table.add_row("", *header["period"])
    header_table.add_row("Period End Date", *header["end_date"])
    tree.add(header_table)

    for sec_name, sec_metrics in df.sort_values(["section_order", "sub_section_order", "tag_order"]).groupby(
        "section_name", sort=False
    ):
        sec_branch = tree.add(f" {sec_name}")

        if sec_metrics["sub_section_order"].values[0]:  # If sub sections exists add new branch to tree
            for sub_sec_name, sub_sec_metrics in sec_metrics.sort_values(
                ["section_order", "sub_section_order", "tag_order"]
            ).groupby("sub_section_name", sort=False):
                sub_sec_branch = sec_branch.add(sub_sec_name)
                t = Table(
                    width=75 + (col_width * (len(periods_list) - 1)), show_lines=False, show_header=False, box=None
                )
                t.add_column(width=55)
                render_metrics_table(t, sub_sec_metrics, periods_list, col_width)
                sub_sec_branch.add(t)

        else:
            t = Table(width=79 + (col_width * (len(periods_list) - 1)), show_lines=False, show_header=False, box=None)
            t.add_column(width=59)
            render_metrics_table(t, sec_metrics, periods_list, col_width)
            sec_branch.add(t)

    return tree


def prepare_financials_df(
    financials_list: List[StandardizedFinancial],
    period_size: int,
    include_ticker: bool = False,
    exportize: Optional[bool] = False,
) -> Dict[str, Any]:
    # Get financial rows
    df = DataFrame([d.to_dict() for d in financials_list])[
        ["ticker", "fiscal_year", "fiscal_period", "type", "filing_date", "end_date", "financial_tags"]
    ]
    df = df.sort_values(by=["fiscal_year", "fiscal_period", "filing_date"], ascending=False)
    df = df.groupby(["ticker", "fiscal_year", "fiscal_period"]).head(1)

    fins_dict: Dict[str, Dict[str, Any]] = {}
    header_dict: Dict[str, List[str]] = {"end_date": [], "period": [], "ticker": []}
    for idx, fin in df[:period_size].iterrows():
        period = fin.fiscal_year
        period = f"{fin.ticker} {period}" if include_ticker else period
        header_dict["end_date"].append(arrow.get(fin.end_date).datetime.strftime("%d %b %Y"))
        fiscal_period = "Annual" if fin.fiscal_period == "FY" else fin.fiscal_period
        idf = f"{period}\n({fiscal_period})"  # Identifier: {ticker} {fiscal_year} \n{fiscal_period}
        header_dict["period"].append(idf)
        header_dict["ticker"].append(fin.ticker)
        fins_dict[idf] = {}
        for tag in fin.financial_tags:
            fins_dict[idf][tag["tag_name"]] = format_number(
                tag["value"], tag["unit"], humanize=True, exportize=exportize
            )

    df_rows = DataFrame(fins_dict.values(), index=fins_dict.keys()).T
    df_rows = df_rows.where(pd.notnull(df_rows), "-")  # Fill nan with `-`
    df_rows.index = df_rows.index.set_names(["tag_fullname"])
    df_rows = df_rows.reset_index()

    return {"header": header_dict, "data": df_rows}


def fin_df2export_df(df: pd.DataFrame, periods_list: List[str]) -> pd.DataFrame:
    col_names = {
        "name": "",
    }
    for column in periods_list:
        col_names[column] = column.replace("\n", " ")
    return format_df(df, col_names, {})


def available_fin_df2tree(df: pd.DataFrame, ticker: str) -> Tree:
    col_width = 25
    tree = Tree(Panel(f"{ticker} Financial Statements Coverage", width=40))
    statement_codes = get_statements_codes()
    statement_codes.sort(reverse=True)
    # Add header table to tree
    header_table = Table(
        width=50 + (col_width * (len(statement_codes) - 1)), show_lines=False, show_header=False, box=None
    )
    header_table.add_column(width=20, style="magenta")
    for p in statement_codes:
        header_table.add_column(width=col_width, justify="center", style="magenta")
    header_table.add_row(
        "Statement Code", *[get_statements_disp_name(statement_code) for statement_code in statement_codes]
    )
    tree.add(header_table)

    for fiscal_year, available_fins_year_df in df.sort_values(["fiscal_year"], ascending=False).groupby(
        "fiscal_year", sort=False
    ):
        year_branch = tree.add(f" {fiscal_year}")

        has_fy = False
        for period_type, period_type_df in available_fins_year_df.merge(
            DataFrame(get_period_types(), columns=["period_type"]), on="period_type", how="right"
        ).groupby("period_type", sort=False):
            period_type_df = period_type_df.merge(
                DataFrame(get_statements_codes(), columns=["statement_code"]), on="statement_code", how="right"
            )
            period_type_disp_name = f" {get_period_type_disp_name(period_type)}"
            t = Table(
                width=46 + (col_width * (len(statement_codes) - 1)),
                show_lines=False,
                show_header=False,
                box=None,
                style="cyan" if period_type == "FY" or period_type == "TTM" else None,
            )
            t.add_column(width=16)
            for st in statement_codes:
                t.add_column(width=col_width, justify="center")
            if period_type_df.empty:
                t.add_row(period_type_disp_name, *["❌", "❌", "❌"])
            else:
                row_text = []
                fiscal_period_df = period_type_df[["statement_code", "fiscal_period"]].groupby(
                    "statement_code", sort=False
                )
                if period_type == "FY":
                    for statement_code in get_statements_codes():
                        if pd.isnull(
                            fiscal_period_df.get_group(statement_code)["fiscal_period"].reset_index(drop=True)[0]
                        ):
                            row_text.append("❌")
                        else:
                            row_text.append("✔️")
                            has_fy = True
                else:
                    for statement_code in get_statements_codes():
                        if pd.isnull(
                            fiscal_period_df.get_group(statement_code)["fiscal_period"].reset_index(drop=True)[0]
                        ):
                            row_text.append(
                                "NA"
                                if (
                                    statement_code == "balance_sheet_statement"
                                    and (period_type == "TTM" or period_type == "YTD")
                                )
                                else "❌"
                            )
                        else:
                            available_fiscal_periods = []
                            for fiscal_period in fiscal_period_df.get_group(statement_code)["fiscal_period"]:
                                available_fiscal_periods.append(f"{fiscal_period[0:2]}")
                            available_fiscal_periods = list(dict.fromkeys(available_fiscal_periods))
                            available_fiscal_periods.sort()
                            row_text.append(
                                "Q1-Q4"
                                if available_fiscal_periods == ["Q1", "Q2", "Q3", "Q4"]
                                or (period_type == "TTM" and available_fiscal_periods == ["Q1", "Q2", "Q3"] and has_fy)
                                else ",".join(available_fiscal_periods)
                            )
                t.add_row(period_type_disp_name, *row_text)

            year_branch.add(t)

    return tree
