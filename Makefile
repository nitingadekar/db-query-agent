.PHONY: install dev test lint format run clean seed-db

install:
	uv sync

dev:
	uv sync --extra dev
	uv run pre-commit install

test:
	uv run pytest

test-cov:
	uv run pytest --cov-report=html

lint:
	uv run ruff check src/ tests/
	uv run mypy src/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

run:
	uv run uvicorn db_query_agent.api:app --reload --host 0.0.0.0 --port 8000

seed-db:
	uv run python scripts/seed_demo_db.py

clean:
	rm -rf .pytest_cache htmlcov .mypy_cache .ruff_cache __pycache__ dist
	find . -type d -name __pycache__ -exec rm -rf {} +
