from i8_terminal.commands import cli


@cli.group()
def server() -> None:
    """Runs i8 Terminal Server"""
    pass
