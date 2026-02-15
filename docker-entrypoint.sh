#!/bin/sh
set -e

# Create DB tables (SQLite file lives beside app.py)
python -c "from app import app; from extensions import db; import models; app.app_context().push(); db.create_all(); print('db ready')"

# Default to port 8000; some platforms inject PORT
: "${PORT:=8000}"

exec gunicorn app:app --bind 0.0.0.0:${PORT} --workers 2 --threads 4
