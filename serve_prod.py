import os

from waitress import serve

from app import app
from extensions import db
import models  # noqa: F401


def init_db() -> None:
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    init_db()

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))

    serve(app, host=host, port=port)
