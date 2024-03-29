from typing import Any

import click

from i8_terminal.common.cli import log_terminal_usage


@click.group()
def cli() -> None:
    """i8 Terminal - Modern Market Research powered by the Command-Line

    Copyright © 2020-2022 Investoreight | https://investoreight.com/"""
    pass


@cli.result_callback()
@click.pass_context
def process_commands(ctx: click.Context, processors: Any) -> None:
    log_terminal_usage(ctx)
