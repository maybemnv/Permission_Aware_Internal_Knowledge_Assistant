FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml ./
COPY apps ./apps
COPY connectors ./connectors
COPY workers ./workers
RUN pip install --no-cache-dir .

EXPOSE 8102
CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8102"]
