from i8_terminal.commands import cli


@cli.group()
def earnings() -> None:
    """Get information about company earnings."""
    pass
