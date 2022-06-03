from typing import Any, Dict, List

import dash_bootstrap_components as dbc
from dash import dcc, html
from plotly.graph_objects import Figure

from i8_terminal.common.utils import to_snake_case
from i8_terminal.config import APP_SETTINGS


def get_fig_config(cmd_context: Dict[str, Any]) -> Dict[str, Any]:
    return {"toImageButtonOptions": {"filename": f'{to_snake_case(cmd_context["plot_title"])}'}}


def create_plot_layout(fig: Figure, cmd_context: Dict[str, Any]) -> html.Div:
    fig_config = get_fig_config(cmd_context)
    return html.Div(
        [
            html.Div(dcc.Store(id="cmdContextStore", data=cmd_context)),
            html.Div(dcc.Store(id="figDict", data=fig.to_dict())),
            html.Div(
                [
                    html.Img(src="assets/i8t_logo.png", className="two columns", style={"margin": "auto"}),
                    html.A(
                        html.Button("Save / Publish Plot", id="openModalBtn", n_clicks=0, className="i8-button"),
                        className="two columns",
                        style={"margin": "auto"},
                    ),
                ],
                className="row",
            ),
            html.Div(
                dbc.Alert("", id="saveAlert", color="success", is_open=False),
                className="row",
            ),
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="mainPlot", figure=fig, responsive=True, config=fig_config)],
                        className="pretty_container",
                    )
                ],
                className="row",
            ),
            html.Div(
                [
                    html.A("", id="fakeOutput", className="two columns", style={"margin": "auto"}),
                    html.Button(
                        "Close",
                        id="closeServerBtn",
                        n_clicks=0,
                        className="btn-secondary two columns",
                        style={"margin": "auto"},
                    ),
                ],
                className="row",
                style={"margin-top": "30px", "margin-right": "15px"},
            ),
            dbc.Modal(_get_modal_layout(cmd_context), id="savePlotModal", is_open=False, size="lg"),
            html.Div(html.Img(src="assets/loading.gif", className="loadingImage"), id="loadingGif", hidden=True),
        ],
        id="mainContainer",
        style={"display": "flex", "flex-direction": "column"},
    )


def _get_modal_layout(cmd_context: Dict[str, Any]) -> List[Any]:
    return [
        dbc.ModalHeader(
            [
                dbc.ModalTitle("Save / Publish plot on your Investoreight profile"),
            ],
            id="modalheader",
        ),
        dbc.ModalBody(
            [
                html.Div(
                    [
                        dbc.Label("Plot Title", className="h4"),
                        dbc.Input(
                            id="titleInput",
                            value=cmd_context["plot_title"],
                            type="text",
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Label("Notes (Optional)", className="h4"),
                        dcc.Textarea(
                            id="userNotesInput",
                            value="",
                            style={"width": "100%", "height": 100},
                        ),
                    ],
                    className="mb-3",
                ),
                html.Div(
                    [
                        dbc.Checklist(
                            options=[
                                {"label": "Make this plot public (URL can be shared)", "value": 1},
                            ],
                            value=[1],
                            id="isPublicBtn",
                            inline=True,
                            switch=True,
                        ),
                    ],
                ),
            ],
            style={"padding": "2%"},
        ),
        dbc.ModalFooter(
            [
                dcc.Loading(
                    id="loading-2",
                    children=dbc.Alert(
                        "Chart Saved Successfully!", id="save_alert", className="ml-auto", is_open=False
                    ),
                    type="circle",
                    style={"marginRight": 60},
                ),
                dbc.Button("Save Plot", id="saveBtn", n_clicks=0, className="i8_button"),
            ]
        ),
    ]


def get_chart_layout() -> List[Dict[str, Any]]:
    return [
        dict(
            source="assets/i8t_chart_logo.png",
            xref="paper",
            yref="paper",
            x=1.01,
            y=1,
            sizex=0.2,
            sizey=0.2,
            xanchor="right",
            yanchor="bottom",
        )
    ]


def get_date_range(period_code: int) -> Dict[str, List[Dict[str, Any]]]:
    date_range: Dict[str, List[Dict[str, Any]]] = {"buttons": []}
    if period_code >= 2:
        date_range["buttons"].append(dict(count=5, label="5D", step="day", stepmode="backward"))
    elif period_code >= 3:
        date_range["buttons"].append(dict(count=1, label="1M", step="month", stepmode="backward"))
    elif period_code >= 4:
        date_range["buttons"].append(dict(count=3, label="3M", step="month", stepmode="backward"))
    elif period_code >= 5:
        date_range["buttons"].append(dict(count=6, label="6M", step="month", stepmode="backward"))
    elif period_code >= 6:
        date_range["buttons"].append(dict(count=1, label="YTD", step="year", stepmode="todate"))
        date_range["buttons"].append(dict(count=1, label="1Y", step="year", stepmode="backward"))
    elif period_code >= 7:
        date_range["buttons"].append(dict(count=3, label="3Y", step="year", stepmode="backward"))
    elif period_code >= 8:
        date_range["buttons"].append(dict(count=5, label="5Y", step="year", stepmode="backward"))
    date_range["buttons"].append(dict(step="all"))

    return date_range


def get_plot_default_layout() -> Dict[str, Any]:
    return dict(
        images=get_chart_layout(),
        paper_bgcolor=APP_SETTINGS["styles"]["plot"]["default"]["paper_bgcolor"],
        plot_bgcolor=APP_SETTINGS["styles"]["plot"]["default"]["plot_bgcolor"],
    )


def get_terminal_command_layout() -> Dict[str, Any]:
    return dict(color=APP_SETTINGS["styles"]["terminal"]["command"]["color"])
