FROM python:3.12-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
COPY src/ src/

RUN pip install --no-cache-dir uv && \
    uv sync --no-dev --frozen


FROM python:3.12-slim

RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY frontend/ /app/frontend/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DQA_FRONTEND_DIR=/app/frontend \
    DQA_API_HOST=0.0.0.0 \
    DQA_API_PORT=8000

EXPOSE 8000

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

ENTRYPOINT ["python", "-m", "uvicorn", "db_query_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
