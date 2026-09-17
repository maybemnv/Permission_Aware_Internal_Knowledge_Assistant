FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.11.20 /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra postgres --no-install-project

COPY apps ./apps
COPY connectors ./connectors
COPY workers ./workers
RUN uv sync --frozen --no-dev --extra postgres

EXPOSE 8102
CMD ["uv", "run", "--no-sync", "python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8102"]
