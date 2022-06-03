from i8_terminal.commands import cli


@cli.group()
def market() -> None:
    """Get information about market."""
    pass
