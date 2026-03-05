from app.web.app import create_app
from app.web.server import server

app = create_app()

__all__ = ["app", "server"]
