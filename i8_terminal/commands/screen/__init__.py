from i8_terminal.commands import cli


@cli.group()
def screen() -> None:
    """Screen the market to find stocks that match your criteria."""
    pass
