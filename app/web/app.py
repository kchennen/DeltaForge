import os
from pathlib import Path

import dash_mantine_components as dmc
from dash import Dash

from app.web.callbacks import register_callbacks
from app.web.layouts.main_layout import layout
from app.web.server import server

_PAGES_DIR = Path(__file__).parent / "pages"

_HLJS_CSS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css"
_HLJS_JS = "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"


def create_app() -> Dash:
    """Create and configure the Dash app."""
    url_base = os.environ.get("URL_BASE_PATHNAME", "/")

    dash_app = Dash(
        name=__name__,
        server=server,
        url_base_pathname=url_base,
        use_pages=True,
        pages_folder=str(_PAGES_DIR),
        external_stylesheets=[*dmc.styles.ALL, _HLJS_CSS],
        external_scripts=[_HLJS_JS],
        suppress_callback_exceptions=True,
    )

    dash_app.layout = layout

    register_callbacks(dash_app)

    return dash_app
