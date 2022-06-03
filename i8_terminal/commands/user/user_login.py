import webbrowser

import click
import investor8_sdk

from i8_terminal.commands.user import user, webserver
from i8_terminal.common.cli import pass_command
from i8_terminal.config import APP_SETTINGS, save_user_settings


def get_login_authentication_request_id() -> str:
    resp = investor8_sdk.UserApi().create_login_authentication_request(body={"ReqType": 3})
    return str(resp.request_id)


def open_browser(request_id: str) -> None:
    url = f"https://www.investoreight.com/account/authorize?reqId={request_id}&redirectUrl=http://localhost:{APP_SETTINGS['app']['port']}"
    webbrowser.open(url)


def login_within_terminal() -> None:
    email = click.prompt("Email", show_default=False, type=str)
    password = click.prompt("Password", hide_input=True, show_default=False, type=str)
    body = {"Email": email, "Password": password}
    api_response = None
    try:
        api_response = investor8_sdk.UserApi().login_user(body=body)
        user_setting = {
            "user_id": api_response.user_id,
            "i8_core_token": api_response.token,
            "i8_core_api_key": api_response.api_key,
        }
        save_user_settings(user_setting)
        click.echo("User logged in successfully!")
    except Exception as e:
        click.echo(e)


@user.command()
@click.option(
    "--terminal",
    is_flag=True,
    default=False,
    help="Login with your credentials in the console (Only applicable if you have a local Investoreight account).",
)
@pass_command
def login(terminal: bool) -> None:
    if terminal:
        login_within_terminal()
    else:
        request_id = get_login_authentication_request_id()
        open_browser(request_id)
        webserver.run_server(request_id)
