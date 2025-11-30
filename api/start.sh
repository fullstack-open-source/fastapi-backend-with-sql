#!/bin/bash
set -euo pipefail

echo "Loading Gunicorn configuration from environment..."

API_PORT="${API_INTERNAL_PORT:-8000}"
G_WORKERS="${GUNICORN_WORKERS:-4}"
G_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
G_WORKER_CLASS="${WORKER_CLASS:-uvicorn.workers.UvicornWorker}"

echo "Gunicorn settings:"
echo "  Port: $API_PORT"
echo "  Workers: $G_WORKERS"
echo "  Timeout: $G_TIMEOUT"
echo "  Worker Class: $G_WORKER_CLASS"

exec gunicorn server:app \
    --workers "$G_WORKERS" \
    --worker-class "$G_WORKER_CLASS" \
    --bind "0.0.0.0:$API_PORT" \
    --timeout "$G_TIMEOUT" \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance \
    --graceful-timeout 30 \
    --preload
