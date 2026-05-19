# DB Query Agent

Natural language database query agent powered by [AWS Strands Agents SDK](https://github.com/strands-agents/sdk-python) and Claude via Amazon Bedrock.

## Features

- **Natural language queries** — Ask questions in plain English, get SQL results
- **Schema-aware** — Agent introspects your database schema for accurate queries
- **Multiple output formats** — JSON, CSV, Markdown table, or summary
- **Safety guardrails** — Read-only by default, configurable mutation allowlist
- **FastAPI backend** — OpenAPI docs at `/docs`
- **Simple chat UI** — Browser-based interface for interactive querying

## Quick Start

```bash
# Install dependencies
make dev

# Seed demo database
make seed-db

# Copy and configure environment
cp .env.example .env

# Run the server
make run
```

Open http://localhost:8000 for the chat UI, or http://localhost:8000/docs for the API.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- AWS credentials configured with Bedrock access (sandbox account)

## Configuration

All settings via environment variables (prefix `DQA_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DQA_AWS_REGION` | `eu-west-2` | AWS region for Bedrock |
| `DQA_BEDROCK_MODEL_ID` | `anthropic.claude-sonnet-4-20250514` | Bedrock model ID |
| `DQA_DATABASE_URL` | `sqlite:///./demo.db` | SQLAlchemy connection string |
| `DQA_MAX_QUERY_ROWS` | `100` | Max rows returned per query |
| `DQA_ALLOW_MUTATIONS` | `false` | Allow INSERT/UPDATE/DELETE |
| `DQA_DEFAULT_FORMAT` | `json` | Default response format |

## Development

```bash
make test        # Run tests
make lint        # Ruff + mypy
make format      # Auto-format code
```

## Architecture

```
src/db_query_agent/
├── agent.py       # Strands Agent with tools
├── api.py         # FastAPI application
├── config.py      # Pydantic settings
├── executor.py    # Safe SQL execution
├── formatters.py  # Output formatters
└── schema.py      # DB schema introspection
```

## License

MIT
