import os
from pathlib import Path

import dash_mantine_components as dmc
from dash import Dash

from app.web.callbacks import register_callbacks
from app.web.layouts.main_layout import layout
from app.web.server import server

_PAGES_DIR = Path(__file__).parent / "pages"


def create_app(
    url_base_pathname: str = os.environ.get("URL_BASE_PATHNAME", "/"),
) -> Dash:
    """Create and configure the Dash application.

    Args:
        url_base_pathname: URL prefix for the Dash app.

    Returns:
        Configured Dash application instance.
    """

    dash_app = Dash(
        name=__name__,
        title="DeltaForge",
        server=server,
        url_base_pathname=url_base_pathname,
        use_pages=True,
        pages_folder=str(_PAGES_DIR),
        external_stylesheets=[*dmc.styles.ALL],
        suppress_callback_exceptions=True,
    )

    dash_app.layout = layout

    register_callbacks(dash_app)

    return dash_app
