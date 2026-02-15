#!/bin/sh
set -e

# Initialize SQLite tables (creates dicss.db if missing)
python -c "from app import app; from extensions import db; import models; app.app_context().push(); db.create_all(); print('db ready')"

# Render injects PORT
exec gunicorn app:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4
