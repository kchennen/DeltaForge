import os

_host = os.environ.get("HOST", "localhost")
_port = os.environ.get("PORT", "8055")

bind = f"{_host}:{_port}"
workers = 4
worker_class = "gthread"
threads = 2
timeout = 120
