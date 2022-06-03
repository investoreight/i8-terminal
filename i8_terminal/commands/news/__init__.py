from i8_terminal.commands import cli


@cli.group()
def news() -> None:
    """Get the latest financial markets news."""
    pass
