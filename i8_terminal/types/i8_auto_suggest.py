from typing import Callable, Optional

import click
from click import Group
from click.decorators import F
from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document

from i8_terminal.types.command_parser import CommandParser

from i8_terminal.types.fin_identifier_param_type import FinancialsIdentifierParamType  # isort:skip


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
            matched_params = [p for p in command.params if isinstance(p, click.Option) and ctx.last_option in p.opts]
            if len(matched_params) > 0:
                matched_param = matched_params[0]
                if type(matched_param.type) is click.types.DateTime:
                    return Suggestion("YYYY-MM-DD"[len(ctx.incomplete) :])
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
                        return Suggestion("[path]/[filename].[csv|xlsx|pdf]")

        return None
