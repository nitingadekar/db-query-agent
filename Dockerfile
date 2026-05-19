FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv && \
    uv sync --no-dev --frozen --no-install-project

COPY src/ src/

RUN uv sync --no-dev --frozen


FROM python:3.12-slim

RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

COPY --from=builder /build/.venv /app/.venv
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

ENTRYPOINT ["uvicorn", "db_query_agent.api:app", "--host", "0.0.0.0", "--port", "8000"]
