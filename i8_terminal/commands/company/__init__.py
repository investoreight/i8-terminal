from i8_terminal.commands import cli


@cli.group()
def company() -> None:
    """Get information about all U.S companies and securities listed in the main U.S exchanges."""
    pass
