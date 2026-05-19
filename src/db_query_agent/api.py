"""FastAPI application for the DB Query Agent."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from db_query_agent.agent import DBQueryAgent
from db_query_agent.config import ResponseFormat, get_settings
from db_query_agent.executor import QueryExecutionError
from db_query_agent.formatters import format_result


class QueryRequest(BaseModel):
    prompt: str
    format: ResponseFormat = ResponseFormat.JSON


class RawQueryRequest(BaseModel):
    sql: str
    format: ResponseFormat = ResponseFormat.JSON


class QueryResponse(BaseModel):
    answer: str
    formatted_data: str | None = None
    format: str
    sql: str | None = None


class SchemaResponse(BaseModel):
    tables: list[dict[str, Any]]


_agent: DBQueryAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    global _agent
    settings = get_settings()
    _agent = DBQueryAgent(settings)
    yield
    _agent = None


app = FastAPI(
    title="DB Query Agent",
    description="Natural language database query agent powered by Claude via AWS Bedrock",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    result = _agent.query(request.prompt, response_format=request.format.value)
    return QueryResponse(
        answer=result["answer"],
        formatted_data=result["formatted_data"],
        format=request.format.value,
    )


@app.post("/query/raw", response_model=QueryResponse)
def query_raw(request: RawQueryRequest) -> QueryResponse:
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        formatted = _agent.query_raw(request.sql, response_format=request.format.value)
        return QueryResponse(
            answer=f"Executed: {request.sql}",
            formatted_data=formatted,
            format=request.format.value,
            sql=request.sql,
        )
    except QueryExecutionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/schema", response_model=SchemaResponse)
def get_schema() -> SchemaResponse:
    if _agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    settings = get_settings()
    from db_query_agent.schema import SchemaIntrospector

    introspector = SchemaIntrospector(settings.database_url)
    tables = introspector.get_tables()
    return SchemaResponse(
        tables=[
            {
                "name": t.name,
                "columns": [
                    {"name": c.name, "type": c.type, "nullable": c.nullable, "primary_key": c.primary_key}
                    for c in t.columns
                ],
            }
            for t in tables
        ]
    )


def mount_frontend(app: FastAPI) -> None:
    """Mount static frontend files."""
    import os
    frontend_dir = os.environ.get(
        "DQA_FRONTEND_DIR",
        os.path.join(os.path.dirname(__file__), "..", "..", "frontend"),
    )
    if os.path.isdir(frontend_dir):
        app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


# Mount frontend after API routes
mount_frontend(app)
