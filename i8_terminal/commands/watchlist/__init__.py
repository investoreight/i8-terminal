from i8_terminal.commands import cli


@cli.group()
def watchlist() -> None:
    """Get information about user watchlists."""
    pass
