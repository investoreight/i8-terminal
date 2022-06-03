from typing import Any, Dict, Optional

import click
import investor8_sdk
import numpy as np
from rich.console import Console

from i8_terminal.commands.financials import financials
from i8_terminal.common.cli import pass_command
from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.common.utils import export_data
from i8_terminal.config import APP_SETTINGS
from i8_terminal.types.period_type_param_type import PeriodTypeParamType

from i8_terminal.types.fin_statement_param_type import FinancialStatementParamType  # isort:skip

from i8_terminal.types.fin_identifier_param_type import FinancialsIdentifierParamType  # isort:skip

from i8_terminal.common.financials import (  # isort:skip
    find_similar_statement,
    get_statements_codes,
    get_statements_disp_name,
    fin_df2export_df,
    fin_df2Tree,
    parse_identifier,
    prepare_financials_df,
)


def get_standardized_financials(
    identifiers_dict: Dict[str, str],
    statement: str,
    period_type: Optional[str],
    period_size: int = 4,
    exportize: Optional[bool] = False,
) -> Optional[Dict[str, Any]]:
    fins = []
    try:
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
    except Exception:
        pass
    if not fins:
        return None
    return prepare_financials_df(fins, period_size, include_ticker=False, exportize=exportize)


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
        df_metrics = get_all_metrics_df()
        df = fins["data"].merge(df_metrics, on="tag_fullname", how="left")
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
