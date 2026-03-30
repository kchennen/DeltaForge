from dash import Dash

from app.web.callbacks.shell import register_clientside_callbacks


def register_callbacks(dash_app: Dash) -> None:
    import app.web.callbacks.shell  # noqa: F401  — @callback decorators register on import
    import app.web.callbacks.text  # noqa: F401

    register_clientside_callbacks(dash_app)
