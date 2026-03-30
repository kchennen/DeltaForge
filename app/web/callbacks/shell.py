"""App-shell callbacks: navbar routing, dark-mode toggle, nav highlighting."""

from __future__ import annotations

import dash
from dash import ClientsideFunction, Input, Output, State, callback

from app.web.components.sidebars import sidebar_for
from app.web.layouts._constants import NAVBAR_WIDTH

_NAVBAR_WIDTH = NAVBAR_WIDTH


# Navbar routing ########################################################################
@callback(
    Output("app-navbar", "children"),
    Output("app-shell", "navbar"),
    Input("url", "pathname"),
)
def update_navbar(pathname: str | None) -> tuple[object, dict]:
    """Show/hide the AppShellNavbar and populate its content based on the current route."""
    sidebar = sidebar_for(pathname)
    has_sidebar = sidebar is not None
    navbar_cfg = {
        "width": _NAVBAR_WIDTH,
        "breakpoint": "sm",
        "collapsed": {"desktop": not has_sidebar, "mobile": True},
    }
    return sidebar or [], navbar_cfg



# Clientside callbacks ##################################################################
def register_clientside_callbacks(app: dash.Dash) -> None:
    """Register clientside callbacks that require the app instance to exist."""

    # Dark mode toggle
    app.clientside_callback(
        ClientsideFunction(namespace="shell", function_name="toggle_color_scheme"),
        Output("color-scheme-toggle", "id"),
        Input("color-scheme-toggle", "checked"),
    )

    # Copy to clipboard (duplicates page)
    app.clientside_callback(
        ClientsideFunction(namespace="shell", function_name="copy_to_clipboard"),
        Output("btn-dupes-copy", "disabled"),
        Input("btn-dupes-copy", "n_clicks"),
        State("store-dupes-output", "data"),
        prevent_initial_call=True,
    )

    # Active nav highlight
    app.clientside_callback(
        ClientsideFunction(namespace="shell", function_name="highlight_nav"),
        Output("url", "search"),
        Input("url", "pathname"),
        prevent_initial_call=False,
    )
