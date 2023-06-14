from io import StringIO
from typing import Optional

import click
from flask import Flask, jsonify, request
from rich.console import Console

from i8_terminal import api as i8
from i8_terminal.commands import cli
from i8_terminal.commands.server import server
from i8_terminal.common.cli import pass_command


def create_resp(result):
    res = {}
    res["text"] = "Here is a sample text response for the query."
    df = result._wide_df("humanize", "suffix")
    res["table"] = df.to_dict(orient="records")

    fig = result.to_plot(show=False)
    if fig:
        res["plot"] = fig.to_json()

    return res


@server.command()
@click.option("--port", "-p", help="HTTP port to server i8 Terminal. Default 8095")
def launch(port: Optional[int]) -> None:
    """
    Launches i8 Terminal server.
    """
    app = Flask(__name__)
    ctx = click.get_current_context()
    ctx.obj["is_server_call"] = True

    @app.route("/", defaults={"command_path": ""})
    @app.route("/<path:command_path>", methods=["GET"])
    def command_handler(command_path):
        command_names = command_path.split("/")

        # Traverse the Click command hierarchy to find the matching command
        command = cli
        for command_name in command_names:
            command = command.get_command(None, command_name.replace("-", "_"))
            if command is None:
                return f"Unknown command: {command_name}", 404

        # Parse arguments and options from the Flask request
        args = [request.args.get(arg.name) for arg in command.params if isinstance(arg, click.Argument)]
        kwargs = {
            opt.name: request.args.get(opt.name, opt.default) for opt in command.params if isinstance(opt, click.Option)
        }

        res = ctx.invoke(command, *args, **kwargs)

        return create_resp(res)

    app.run(port=port or 8085)
