"""Tests for query executor."""

import pytest
from sqlalchemy import create_engine, text

from db_query_agent.executor import QueryExecutionError, QueryExecutor


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    with eng.connect() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"))
        conn.execute(text("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')"))
        conn.execute(text("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')"))
        conn.commit()
    return eng


@pytest.fixture
def executor(engine):
    return QueryExecutor(engine, allow_mutations=False, max_rows=10)


class TestQueryExecutor:
    def test_select_query(self, executor):
        result = executor.execute("SELECT * FROM users")
        assert result.row_count == 2
        assert result.columns == ["id", "name", "email"]
        assert result.rows[0]["name"] == "Alice"

    def test_mutation_blocked(self, executor):
        with pytest.raises(QueryExecutionError, match="Mutation queries are not allowed"):
            executor.execute("DELETE FROM users WHERE id = 1")

    def test_mutation_allowed(self, engine):
        executor = QueryExecutor(engine, allow_mutations=True, max_rows=10)
        executor.execute("DELETE FROM users WHERE id = 1")
        result = executor.execute("SELECT * FROM users")
        assert result.row_count == 1

    def test_limit_applied(self, executor):
        result = executor.execute("SELECT * FROM users")
        assert "LIMIT" in result.query

    def test_existing_limit_preserved(self, executor):
        result = executor.execute("SELECT * FROM users LIMIT 1")
        assert result.row_count == 1
