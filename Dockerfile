FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt requirements-docker.txt /app/
RUN pip install --no-cache-dir -r /app/requirements-docker.txt

COPY . /app

RUN chmod +x /app/docker-entrypoint.sh \
    && mkdir -p /app/uploads/shard0 /app/uploads/shard1

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
