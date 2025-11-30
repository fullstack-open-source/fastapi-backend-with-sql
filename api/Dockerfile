
FROM python:3.11-slim AS builder

ARG DEBIAN_FRONTEND=noninteractive
ARG PYTHONUNBUFFERED=1
ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

FROM python:3.11-slim AS runtime

LABEL maintainer="mrdas"
LABEL description="FastAPI Backend - Production Image"
LABEL version="1.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/api:$PYTHONPATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        ffmpeg \
        curl \
    ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY --from=builder /opt/venv /opt/venv

RUN groupadd -r mrdas && \
    useradd -r -g mrdas -u 1000 -d /home/mrdas -s /bin/bash mrdas && \
    mkdir -p /home/mrdas /api /api/logs /api/uploads /api/temp /api/tmp && \
    chown -R mrdas:mrdas /home/mrdas /api

WORKDIR /api

COPY --chown=mrdas:mrdas . /api

RUN chown -R mrdas:mrdas /api && \
    chmod -R 755 /api && \
    chmod +x /api/start.sh && \
    chmod +x /api/wait-for-health.sh || true

RUN test -f /api/server.py || (echo "ERROR: server.py not found!" && exit 1)

USER mrdas

EXPOSE 8000

CMD ["/api/start.sh"]

