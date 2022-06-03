import os

import click

from i8_terminal.commands.user import user
from i8_terminal.common.cli import pass_command
from i8_terminal.config import USER_SETTINGS, restore_user_settings


@user.command()
@pass_command
def logout() -> None:
    if USER_SETTINGS:
        restore_user_settings()
        click.echo("✅ User logged out successfully!")
        os._exit(0)
    else:
        click.echo("You are already logged out!")
