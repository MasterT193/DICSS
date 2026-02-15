# Decentralized Intelligent Cloud Storage System (DICSS)

A Flask web app for secure file storage with authentication, folder organization, encryption, and activity logging.

## Run locally (Windows)

From the repo folder:

```powershell
# create/activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python app.py
```

Dev server opens at `http://127.0.0.1:5000/`.

## Run locally (production mode)

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python serve_prod.py
```

Opens at `http://127.0.0.1:8000/`.

## Deploy on Render (no Docker)

This repo includes a `render.yaml` blueprint.

1) Push this repo to GitHub (done once).
2) In Render: **New** → **Blueprint** → pick your GitHub repo.
3) Render will install from `requirements-prod.txt` and start with Gunicorn.

Note: This project uses SQLite (`dicss.db`) and a local `uploads/` folder. On many PaaS hosts, local disk can be ephemeral.

## Docker

```bash
docker build -t dicss .
docker run --rm -p 8000:8000 -e SECRET_KEY="your-long-random-secret" dicss
```

Open `http://127.0.0.1:8000/`.
