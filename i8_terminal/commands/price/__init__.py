from i8_terminal.commands import cli


@cli.group(chain=True)
def price() -> None:
    """Get the latest and historical security prices."""
    pass
