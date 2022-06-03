from typing import Any, Dict, List, Optional

import click
import investor8_sdk
import numpy as np
import plotly.graph_objects as go
from pandas.core.frame import DataFrame
from rich.console import Console

from i8_terminal.app.layout import get_plot_default_layout
from i8_terminal.app.plot_server import serve_plot
from i8_terminal.commands.financials import financials
from i8_terminal.common.cli import get_click_command_path, pass_command
from i8_terminal.common.metrics import get_all_metrics_df
from i8_terminal.common.utils import PlotType, export_data
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
    identifiers_list: List[Dict[str, str]],
    statement: str,
    period_type: str,
    period_size: int = 4,
    exportize: Optional[bool] = False,
) -> Optional[Dict[str, Any]]:
    fins = []
    for idf in identifiers_list:
        resp = None
        try:
            if idf.get("fiscal_year"):
                resp = investor8_sdk.FinancialsApi().get_financials_single(
                    ticker=idf["ticker"],
                    stat_code=statement,
                    fiscal_year=idf.get("fiscal_year"),
                    fiscal_period=idf.get("fiscal_period"),
                )
            else:
                if not period_type:
                    period_type = "Q" if statement == "balance_sheet_statement" else "FY"
                resp = investor8_sdk.FinancialsApi().get_latest_standardized_financials(
                    ticker=idf["ticker"], stat_code=statement
                )[period_type]
            if resp:
                fins.append(resp)
        except Exception:
            continue
    if not fins:
        return None
    return prepare_financials_df(fins, period_size, include_ticker=True, exportize=exportize)


def create_fig(df: DataFrame, header_dict: Dict[str, List[str]], cmd_context: Dict[str, Any]) -> go.Figure:
    cells_fill_color = [["rgb(200, 212, 227)", "rgb(235, 240, 248)"]] * len(df.columns)
    cells_data = list(df.to_dict("list").values())
    # Add end_date row to cells data
    cells_data = [[(["End Date"] + header_dict["end_date"])[idx]] + d for idx, d in enumerate(cells_data)]
    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[58, 25],
                header=dict(
                    values=[""] + ["<b>" + p.replace("\n", " ") + "</b>" for p in header_dict["period"]],
                    align=["left", "center"],
                    height=32,
                    font_size=14,
                ),
                cells=dict(
                    fill_color=cells_fill_color, values=cells_data, align=["left", "right"], height=28, font_size=14
                ),
            )
        ]
    )
    fig.update_layout(
        title=cmd_context["plot_title"],
        margin=dict(b=15, l=25, r=25),
        **get_plot_default_layout(),
    )

    return fig


@financials.command()
@click.pass_context
@click.option(
    "--identifiers",
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
@click.option("--plot", is_flag=True, default=False, help="Plot results on the browser.")
@click.option("--export", "export_path", "-e", help="Filename to export the output to.")
@pass_command
def compare(
    ctx: click.Context,
    identifiers: str,
    statement: str,
    period_type: str,
    plot: bool,
    export_path: Optional[str],
) -> None:
    matched_statement = find_similar_statement(statement)
    if not matched_statement:
        click.echo(
            f"`{statement}` is not a valid statement code. \nValid statement codes: {', '.join(get_statements_codes())}"
        )
        return
    identifiers_list = identifiers.replace(" ", "").upper().split(",")
    parsed_identifiers_list = [parse_identifier(i, period_type) for i in identifiers_list]
    # Remove duplicates identifiers
    parsed_identifiers_list = [dict(t) for t in {tuple(d.items()) for d in parsed_identifiers_list}]
    tickers_list = list(set([d["ticker"] for d in parsed_identifiers_list]))
    plot_title = f"Comparison of {', '.join(tickers_list)} {get_statements_disp_name(matched_statement)}s"
    plot_title = " and ".join(plot_title.rsplit(", ", 1))
    console = Console()
    with console.status("Fetching data...", spinner="material") as status:
        fins = get_standardized_financials(
            parsed_identifiers_list,
            matched_statement,
            period_type,
            period_size=4,
            exportize=True if export_path else False,
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
        if plot:
            cmd_context = {
                "plot_title": plot_title,
                "command_path": get_click_command_path(ctx, {"--statement": matched_statement}),
                "tickers": tickers_list,
                "plot_type": PlotType.TABLE.value,
            }
            df = df[df["is_significant"] != False]
            df = df[["name", *fins["data"].columns[1:]]]
            df.rename(columns={"name": ""}, inplace=True)
            fig = create_fig(df, fins["header"], cmd_context)

    missing_tickers = set(tickers_list) - set(fins["header"].get("ticker", set()))
    if missing_tickers:
        missing_tickers_str = " and ".join(", ".join(missing_tickers).rsplit(", ", 1))
        console.print(f'The specified financials for ticker(s) "{missing_tickers_str}" are not available.')
        console.print("To see the covered financials check the [magenta]financials coverage[magenta] command.")

    if plot and export_path:
        console.print("The plot and export options are not compatible to use together")
    elif plot:
        serve_plot(fig, cmd_context)
    elif export_path:
        export_df = fin_df2export_df(df, periods_list)
        export_data(
            export_df,
            export_path,
            column_width=22,
            column_format=APP_SETTINGS["styles"]["xlsx"]["financials"]["column"],
        )
    else:
        tree = fin_df2Tree(df, fins["header"], periods_list, title=plot_title)
        console.print(tree)
