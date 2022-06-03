import os
import sys

from rich.console import Console

from i8_terminal.common.cli import log_terminal_usage, pass_command
from i8_terminal.config import USER_SETTINGS, is_user_logged_in
from i8_terminal.utils import get_version

console = Console(force_terminal=True, color_system="truecolor")
if set(["i8"]) == set(sys.argv[1:]):
    console.print(f"\n👋 Welcome to i8 Terminal! Version: {get_version()}", style="yellow")
    console.print("Copyright © 2020-2022 Investoreight | https://www.i8terminal.io/\n")
    console.print("- Enter [magenta]i8 shell[/magenta] to run i8 Terminal shell.")
    os._exit(0)
if set(["i8", "version"]) == set(sys.argv[1:]):
    console.print(f"Version: {get_version()}", style="yellow")
    os._exit(0)
status = console.status("Starting Up...", spinner="material")
status.start()


import click
import investor8_sdk
from click_repl import repl
from investor8_sdk.rest import ApiException

from i8_terminal.commands import cli
from i8_terminal.types.i8_auto_suggest import I8AutoSuggest
from i8_terminal.types.i8_completer import I8Completer


def init_commands() -> None:
    status.start()
    app_dir = os.path.join(os.path.join(os.path.dirname(sys.executable), "lib"), "i8_terminal")
    sys.path.append(app_dir)
    commands_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands")
    commands_dir = commands_dir if os.path.exists(commands_dir) else os.path.join(app_dir, "commands")
    ignore_dir = ["__pycache__"]
    for cmd in [p for p in os.listdir(commands_dir) if os.path.isdir(os.path.join(commands_dir, p))]:
        if cmd not in ignore_dir:
            for sub_cmd in os.listdir(os.path.join(commands_dir, cmd)):
                sub_cmd_splitted = sub_cmd.split(".")
                if (sub_cmd_splitted[-1] in ["py", "pyc"]) and sub_cmd_splitted[0] not in ["__init__"]:
                    __import__(f"i8_terminal.commands.{cmd}.{''.join(sub_cmd_splitted[:-1])}")
    status.stop()

    @cli.command()
    def shell() -> None:
        """Open i8-shell."""
        print_welcome_msg()
        prompt_kwargs = {"completer": I8Completer(cli), "auto_suggest": I8AutoSuggest(cli)}

        while True:
            try:
                repl(click.get_current_context(), prompt_kwargs=prompt_kwargs)
            except ApiException as e:
                if "apiKey" in e.body.decode("utf-8"):
                    console.print(
                        "You need to login before using i8 Terminal. Please login to i8 Terminal using [magenta]user login[/magenta] command."
                    )
                else:
                    console.print(f"⚠ Error: {e.body.decode('utf-8')}", style="yellow")
                log_terminal_usage(click.get_current_context(), e.body.decode("utf-8"))
            except Exception as e:
                display_error = f"- Type: {type(e).__name__}\n- Message: {e}"
                log_terminal_usage(click.get_current_context(), display_error)
                console.print(f"⚠ Error:\n{display_error}", style="yellow")

    @cli.command()
    def exit() -> None:
        """Exit the terminal."""
        os._exit(0)

    @cli.command()
    @pass_command
    def version() -> None:
        """Get i8-terminal version."""
        click.echo(get_version())

    @cli.command()
    @click.option("--all", "-a", is_flag=True, default=False, help="Clear entire screen.")
    @pass_command
    def clear(all: bool) -> None:
        """Clear the console screen."""
        cls_screen()
        if not all:
            print_welcome_msg()


def print_welcome_msg() -> None:
    console.print(f"\n👋 Welcome to i8 Terminal! Version: {get_version()}", style="yellow")
    console.print("Copyright © 2020-2022 Investoreight | https://www.i8terminal.io/")
    console.print("- Enter [magenta]?[/magenta] to get the list of commands.")
    console.print("- Enter [magenta]exit[/magenta] to exit the shell.\n")
    if is_user_logged_in():
        console.print(f'Logged in as "{USER_SETTINGS["user_id"]}".\n')
    else:
        console.print(
            "You are not logged in. Please login to i8 Terminal using [magenta]user login[/magenta] command.\n"
        )


def cls_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def check_version() -> None:
    resp = None
    try:
        resp = investor8_sdk.SettingsApi().check_i8t_version(get_version())
    except:
        pass
    if not resp or not resp.to_dict().get("version_supported"):
        status.stop()
        console.print(
            "[yellow]You are using an old version of i8 Terminal that is not supported anymore.[/yellow]",
            "[yellow]Please update i8 Terminal with the following command to be able to use the application.[/yellow]\n",
            "[magenta]i8update[/magenta]\n",
            "If you are using Python pip, you can run the following command to update i8 Terminal:\n",
            "[magenta]pip install --upgrade i8-terminal[/magenta]",
        )
        os._exit(0)


def main() -> None:
    check_version()
    init_commands()

    if is_user_logged_in():
        investor8_sdk.ApiClient().configuration.api_key["apiKey"] = USER_SETTINGS.get("i8_core_api_key")
        investor8_sdk.ApiClient().configuration.api_key["Authorization"] = USER_SETTINGS.get("i8_core_token")
        investor8_sdk.ApiClient().configuration.api_key_prefix["Authorization"] = "Bearer"

    cli(obj={})


if __name__ == "__main__":
    main()
else:
    init_commands()
