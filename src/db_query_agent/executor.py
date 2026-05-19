"""Safe SQL query execution with guardrails."""

import re
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Engine


MUTATION_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class QueryResult:
    columns: list[str]
    rows: list[dict[str, object]]
    row_count: int
    query: str


class QueryExecutionError(Exception):
    pass


class QueryExecutor:
    """Executes SQL queries with safety constraints."""

    def __init__(self, engine: Engine, *, allow_mutations: bool = False, max_rows: int = 100):
        self._engine = engine
        self._allow_mutations = allow_mutations
        self._max_rows = max_rows

    def execute(self, sql: str) -> QueryResult:
        """Execute a SQL query and return structured results."""
        sql = sql.strip().rstrip(";")

        if not self._allow_mutations and MUTATION_KEYWORDS.search(sql):
            raise QueryExecutionError(
                "Mutation queries are not allowed. Set allow_mutations=True to enable."
            )

        limited_sql = self._apply_limit(sql)

        with self._engine.connect() as conn:
            result = conn.execute(text(limited_sql))
            if result.returns_rows:
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
            else:
                conn.commit()
                columns = []
                rows = []

        return QueryResult(
            columns=columns,
            rows=rows,
            row_count=len(rows),
            query=limited_sql,
        )

    def _apply_limit(self, sql: str) -> str:
        """Apply row limit to SELECT queries if not already present."""
        if not re.match(r"\s*SELECT\b", sql, re.IGNORECASE):
            return sql
        if re.search(r"\bLIMIT\b", sql, re.IGNORECASE):
            return sql
        return f"{sql} LIMIT {self._max_rows}"
