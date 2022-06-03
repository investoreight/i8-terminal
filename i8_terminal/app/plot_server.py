import contextlib
import logging
import os
import sys
import webbrowser
from threading import Timer
from typing import Any, Dict, List, Tuple

import dash
import dash_bootstrap_components as dbc
import investor8_sdk
import plotly.graph_objects as go
from dash import html
from dash.dependencies import Input, Output, State
from flask import request
from rich.console import Console

from i8_terminal import config
from i8_terminal.app.layout import create_plot_layout
from i8_terminal.common.formatting import make_svg_responsive
from i8_terminal.config import APP_SETTINGS, ASSETS_PATH, USER_SETTINGS

APP = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], assets_folder=ASSETS_PATH)


@APP.callback(
    Output("savePlotModal", "is_open"),
    Input("openModalBtn", "n_clicks"),
    Input("saveBtn", "n_clicks"),
    State("savePlotModal", "is_open"),
)
def toggle_modal(open_btn_clicks: int, save_btn_clicks: int, is_open: bool) -> bool:
    if not open_btn_clicks:
        return False
    return not is_open


@APP.callback(
    Output("fakeOutput", "children"),
    Input("closeServerBtn", "n_clicks"),
)
def shutdown_server(close_btn_clicks: int) -> str:
    if close_btn_clicks:
        shutdown_func = request.environ.get("werkzeug.server.shutdown")
        if shutdown_func is None:
            raise RuntimeError("Not running werkzeug")
        shutdown_func()
    return ""


@APP.callback(
    Output("saveAlert", "is_open"),
    Output("saveAlert", "children"),
    Input("saveBtn", "n_clicks"),
    State("cmdContextStore", "data"),
    State("titleInput", "value"),
    State("userNotesInput", "value"),
    State("isPublicBtn", "value"),
    State("figDict", "data"),
)
def save_button(
    save_btn_clicks: int,
    cmd_context: Dict[str, Any],
    title: str,
    user_notes: str,
    is_public: List[int],
    fig_dict: Dict[str, Any],
) -> Tuple[bool, Any]:
    if save_btn_clicks:
        fig_obj = go.Figure(fig_dict)
        fig_obj_small = go.Figure(fig_obj)
        fig_obj_small.update_layout(
            title=dict(text="", font=dict(size=14)),
            font=dict(size=9),
            legend_title=dict(font=dict(size=11)),
            legend=dict(font=dict(size=9)),
        )
        thumbnail = make_svg_responsive(fig_obj_small.to_image(format="svg", width=846, height=500).decode("utf-8"))
        tickers = cmd_context["tickers"]
        fig_obj.layout.images[0].source = config.I8_TERMINAL_LOGO_URL  # Update plot logo to url
        fig_obj.layout.title.text = title  # Update plot title
        body = {
            "Title": title,
            "Tickers": tickers if type(tickers) is list else [tickers],
            "UserId": USER_SETTINGS["user_id"],
            "PlotData": fig_obj.to_json(),
            "IsPublic": 1 in is_public,
            "I8Command": cmd_context["command_path"],
            "UserNotes": user_notes,
            "PlotType": cmd_context["plot_type"],
            "Thumbnail": thumbnail,
            # TODO: implement tags
            "Tags": [],
        }
        resp = investor8_sdk.UserApi().create_plot(body=body)
        plot_url = f"https://www.investoreight.com/plot/{resp.id}"
        alert_content = html.Div(["Your plot is saved and published at: ", html.A(plot_url, href=plot_url)])

        return True, alert_content

    return False, None


@APP.callback(
    Output("loadingGif", "hidden"),
    Input("saveBtn", "n_clicks"),
    State("loadingGif", "hidden"),
)
def show_loading(save_btn_clicks: int, hidden: bool) -> bool:
    if not save_btn_clicks:
        return True
    return not hidden


@APP.callback(
    Output("loadingGif", "style"),
    Input("saveAlert", "is_open"),
)
def hide_loading(is_open: bool) -> Dict[str, Any]:
    if is_open:
        return {"display": "none"}
    return {
        "position": "fixed",
        "width": "100%",
        "height": "100%",
        "left": 0,
        "right": 0,
        "bottom": 0,
        "background-color": "rgba(0,0,0,0.5)",
        "z-index": 2,
    }


def _configure_dash() -> None:
    # TODO: the following method does not disable dash logging (it should)
    dash_logger = logging.getLogger("dash")
    dash_logger.setLevel(logging.WARNING)
    dash_logger.disabled = True

    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None  # type: ignore


def serve_plot(fig: go.Figure, cmd_context: Dict[str, Any]) -> None:
    _configure_dash()

    APP.layout = create_plot_layout(fig, cmd_context)
    APP.title = f"i8 Terminal: {cmd_context['plot_title']}"
    app_url = f"http://localhost:{APP_SETTINGS['app']['port']}/"
    console = Console()
    with open(os.devnull, "w") as f, contextlib.redirect_stderr(f):
        Timer(2, lambda: webbrowser.open_new(app_url)).start()
        console.print(
            f'[bold green]Your plot is serving on http://127.0.0.1:{APP_SETTINGS["app"]["port"]}/[/bold green]'
        )
        console.print("Press `Ctrl + C` to stop the webserver.")
        if APP.logger.hasHandlers():
            APP.logger.handlers.clear()
        APP.run_server(debug=APP_SETTINGS["app"]["debug"])
