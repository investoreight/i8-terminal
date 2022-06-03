import logging
import os
import signal
import sys
from threading import Timer
from typing import Any

import click
import investor8_sdk
from flask import Flask, redirect, request

from i8_terminal.config import APP_SETTINGS, save_user_settings

app = Flask(__name__)


def _configure_flask() -> None:
    # TODO: the following method does not disable dash logging (it should)
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)
    log.disabled = True

    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None  # type: ignore


@app.route("/")
def login() -> Any:
    verification_code = request.args.get("verificationCode")
    if verification_code:
        body = {"ReqId": app.config["REQUEST_ID"], "VerificationCode": verification_code}
        try:
            resp = investor8_sdk.UserApi().login_with_code(body=body)
            user_setting = {
                "i8_core_token": resp.token,
                "i8_core_api_key": resp.api_key,
                "user_id": resp.user_id,
                "allow_terminal_logging": resp.allow_terminal_logging,
            }
            save_user_settings(user_setting)
            click.echo("User logged in successfully!")
            Timer(4.0, shutdown_server).start()
            return redirect("https://www.investoreight.com/account/loginsuccessful")
        except Exception:
            click.echo("Login failed. Invalid request-id or verification code.")
    else:
        click.echo("Missing the required parameter 'verificationCode'!")
        shutdown_server()


def shutdown_server() -> None:
    os.kill(os.getpid(), signal.SIGINT)  # Shutdown server


def run_server(req_id: str) -> None:
    _configure_flask()
    app.config["REQUEST_ID"] = req_id
    app.debug = False
    app.run(host="localhost", port=APP_SETTINGS["app"]["port"])
