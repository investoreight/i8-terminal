from i8_terminal.commands import cli


@cli.group()
def metrics() -> None:
    """Get information about company metrics."""
    pass
