FROM python:3.14-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.5 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=/tmp/poetry_cache \
    poetry install --no-root --only main

FROM python:3.14-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 10001 appgroup \
    && useradd --system --uid 10001 --gid appgroup --shell /usr/sbin/nologin appuser \
    && mkdir -p /app && chown -R appuser:appgroup /app

COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000


HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]