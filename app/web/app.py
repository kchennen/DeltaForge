from pathlib import Path

from dash import Dash

from app.web.callbacks import register_callbacks
from app.web.layouts.main_layout import layout
from app.web.server import server

app = Dash(
    __name__,
    server=server,
    use_pages=True,
    pages_folder=str(Path(__file__).parent / "pages"),
)

app.layout = layout

register_callbacks(app)
