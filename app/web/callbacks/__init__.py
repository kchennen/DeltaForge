from dash import Dash

from app.web.callbacks.shell import register_clientside_callbacks


def register_callbacks(dash_app: Dash) -> None:
    import app.web.callbacks.duplicates  # noqa: F401
    import app.web.callbacks.excel  # noqa: F401
    import app.web.callbacks.image  # noqa: F401
    import app.web.callbacks.pdf  # noqa: F401
    import app.web.callbacks.shell  # noqa: F401  — @callback decorators register on import
    import app.web.callbacks.text  # noqa: F401

    register_clientside_callbacks(dash_app)

    from app.web.callbacks.image import register_image_clientside_callbacks

    register_image_clientside_callbacks(dash_app)
