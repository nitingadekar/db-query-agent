"""Response formatters for query results."""

import csv
import io
import json
from typing import Any

from db_query_agent.executor import QueryResult


def format_json(result: QueryResult) -> str:
    return json.dumps({"columns": result.columns, "rows": result.rows, "count": result.row_count})


def format_csv(result: QueryResult) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=result.columns)
    writer.writeheader()
    writer.writerows(result.rows)
    return output.getvalue()


def format_table(result: QueryResult) -> str:
    if not result.rows:
        return "(no results)"

    col_widths = {col: len(col) for col in result.columns}
    for row in result.rows:
        for col in result.columns:
            col_widths[col] = max(col_widths[col], len(str(row.get(col, ""))))

    header = " | ".join(col.ljust(col_widths[col]) for col in result.columns)
    separator = "-+-".join("-" * col_widths[col] for col in result.columns)
    lines = [header, separator]
    for row in result.rows:
        lines.append(" | ".join(str(row.get(col, "")).ljust(col_widths[col]) for col in result.columns))
    return "\n".join(lines)


def format_summary(result: QueryResult) -> str:
    return f"Query returned {result.row_count} row(s) across {len(result.columns)} column(s): {', '.join(result.columns)}"


FORMATTERS: dict[str, Any] = {
    "json": format_json,
    "csv": format_csv,
    "table": format_table,
    "summary": format_summary,
}


def format_result(result: QueryResult, fmt: str = "json") -> str:
    formatter = FORMATTERS.get(fmt)
    if not formatter:
        raise ValueError(f"Unknown format: {fmt}. Available: {list(FORMATTERS.keys())}")
    return formatter(result)
