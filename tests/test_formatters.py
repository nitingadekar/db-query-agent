"""Tests for response formatters."""

import json

from db_query_agent.executor import QueryResult
from db_query_agent.formatters import format_csv, format_json, format_summary, format_table


def _sample_result() -> QueryResult:
    return QueryResult(
        columns=["id", "name"],
        rows=[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
        row_count=2,
        query="SELECT id, name FROM users",
    )


class TestFormatters:
    def test_format_json(self):
        result = format_json(_sample_result())
        parsed = json.loads(result)
        assert parsed["count"] == 2
        assert parsed["columns"] == ["id", "name"]
        assert len(parsed["rows"]) == 2

    def test_format_csv(self):
        result = format_csv(_sample_result())
        lines = result.strip().splitlines()
        assert lines[0] == "id,name"
        assert lines[1] == "1,Alice"

    def test_format_table(self):
        result = format_table(_sample_result())
        assert "Alice" in result
        assert "---" in result

    def test_format_table_empty(self):
        empty = QueryResult(columns=["id"], rows=[], row_count=0, query="SELECT id FROM x")
        assert format_table(empty) == "(no results)"

    def test_format_summary(self):
        result = format_summary(_sample_result())
        assert "2 row(s)" in result
        assert "2 column(s)" in result
