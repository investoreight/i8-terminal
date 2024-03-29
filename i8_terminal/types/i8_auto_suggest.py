from typing import Callable, Optional

import click
from click import Group
from click.decorators import F
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document

from i8_terminal.common.utils import get_matched_params
from i8_terminal.types.command_parser import CommandParser
from i8_terminal.types.fin_identifier_param_type import FinancialsIdentifierParamType
from i8_terminal.types.metric_identifier_param_type import MetricIdentifierParamType


class I8AutoSuggest(AutoSuggest):
    """
    Give suggestions based on click option types.
    """

    def __init__(self, cli: Callable[[F], Group]) -> None:
        self.cli = cli

    def get_suggestion(self, buffer: Buffer, document: Document) -> Optional[Suggestion]:
        ctx = CommandParser(self.cli).parse(document)
        if not ctx:
            return None

        command = ctx.click_ctx.command

        if ctx.last_option:
            matched_params = get_matched_params(ctx, command, document)
            if matched_params and len(matched_params) > 0:
                matched_param = matched_params[0]
                if type(matched_param.type) is click.types.DateTime:
                    return Suggestion("YYYY-MM-DD"[len(ctx.incomplete) :])  # noqa: E203
                elif type(matched_param.type) is FinancialsIdentifierParamType:
                    parts_num = 3
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    sub_parts = incomplete.split("-")
                    if len(sub_parts) > 2:
                        parts_num = 1
                    elif len(sub_parts) > 1:
                        parts_num = 2

                    if len(incomplete) < 1:
                        return Suggestion("Ticker-[Fiscal Year]-[Fiscal Period]")
                    elif parts_num == 3:
                        return Suggestion("-[Fiscal Year]-[Fiscal Period]")
                    elif parts_num == 2:
                        return Suggestion("-[Fiscal Period]")
                elif matched_param.name == "export_path":
                    if len(ctx.incomplete) < 1:
                        return Suggestion("[path]/[filename].[csv|xlsx|pdf|html]")
                elif matched_param.name == "path":
                    if len(ctx.incomplete) < 1:
                        return Suggestion("[path]/[filename].[xlsx]")
                elif type(matched_param.type) is MetricIdentifierParamType:
                    parts_num = 2
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    sub_parts = incomplete.split(".")
                    if len(sub_parts) > 1:
                        parts_num = 1

                    if len(incomplete) < 1:
                        return Suggestion("Metric.[Optional Period]")
                    elif parts_num == 2:
                        return Suggestion(".[Optional Period]")

        return None
