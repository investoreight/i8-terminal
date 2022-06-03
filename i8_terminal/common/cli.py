import sys
from functools import update_wrapper
from typing import Any, Dict, Optional

import click
import investor8_sdk

from i8_terminal.config import USER_SETTINGS
from i8_terminal.utils import get_version


def get_click_command_path(ctx: Any, parsed_options_dict: Optional[Dict[str, str]] = None) -> str:
    command_path = ctx.command_path.replace("  ", " ")
    cm_path = f"i8 {' '.join(command_path.split(' ')[1:])}"
    params = ctx.params
    args = []
    options = {}
    for p in ctx.command.params:
        if p.param_type_name == "argument":
            args.append(params[p.name])
        elif p.param_type_name == "option" and params[p.name] is not None:
            options[f"--{p.name}"] = params[p.name] if type(params[p.name]) != bool else None

    if parsed_options_dict:
        options = {**options, **parsed_options_dict}
    return (
        f"{cm_path} {' '.join([f'{k} {val}' if val else k for (k, val) in options.items()])} {''.join(args)}".rstrip()
    )


def log_terminal_usage(ctx: click.Context, exception: Optional[str] = "") -> None:
    if USER_SETTINGS.get("allow_terminal_logging"):
        investor8_sdk.UserApi().log_terminal_usage(
            body={
                "Command": ctx.obj["command"],
                "Version": get_version(),
                "OS": sys.platform,
                "AppInstanceId": USER_SETTINGS.get("app_instance_id"),
                "Exception": exception,
            }
        )


def pass_command(f: Any) -> Any:
    @click.pass_context
    def new_func(ctx: click.Context, *args: Any, **kwargs: Any) -> Any:
        ctx.obj["command"] = get_click_command_path(ctx)
        return ctx.invoke(f, *args, **kwargs)

    return update_wrapper(new_func, f)
