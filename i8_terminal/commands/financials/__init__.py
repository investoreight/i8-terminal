from i8_terminal.commands import cli


@cli.group()
def financials() -> None:
    """Get information about company financials."""
    pass
