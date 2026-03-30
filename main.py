import os

from app.web import app

if __name__ == "__main__":
    host = os.environ.get("HOST", "localhost")
    port = int(os.environ.get("PORT", "8055"))
    app.run(debug=True, host=host, port=port)
