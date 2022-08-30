import shlex
from typing import Callable, List, Union, cast

import click
from click import Group
from click.decorators import F
from click.shell_completion import _resolve_context
from prompt_toolkit.document import Document


class CompleterContext:
    def __init__(
        self,
        cli: Callable[[F], Group],
        click_ctx: click.Context,
        tokens: List[str],
        used_options: List[str],
        last_option: Union[str, None],
        incomplete: str,
    ) -> None:
        self.cli = cli
        self.click_ctx = click_ctx
        self.tockens = tokens
        self.used_options = used_options
        self.last_option = last_option
        self.incomplete = incomplete


class CommandParser:
    def __init__(self, cli: Callable[[F], Group]) -> None:
        self.cli = cast(Group, cli)

    def parse(self, document: Document) -> Union[CompleterContext, None]:
        tokens = document.text.split(" ")
        used_options = [p for p in tokens if p.startswith("-")]
        last_option = tokens[-2] if len(tokens) > 2 and tokens[-2].startswith("-") else None

        try:
            args = shlex.split(document.text_before_cursor)
        except ValueError:
            # Invalid command, perhaps caused by missing closing quotation.
            return None

        cursor_within_command = document.text_before_cursor.rstrip() == document.text_before_cursor

        if args and cursor_within_command:
            # We've entered some text and no space, give completions for the
            # current word.
            incomplete = args.pop()
        else:
            # We've not entered anything, either at all or for the current
            # command, so give all relevant completions for this context.
            incomplete = ""
        ctx = _resolve_context(self.cli, {}, "", args)

        return CompleterContext(self.cli, ctx, tokens, used_options, last_option, incomplete)
