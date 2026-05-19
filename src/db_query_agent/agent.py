"""Core agent using AWS Strands Agents SDK with Claude via Bedrock."""

from typing import Any

from strands import Agent, tool
from strands.models.bedrock import BedrockModel

from db_query_agent.config import Settings
from db_query_agent.executor import QueryExecutor, QueryExecutionError, QueryResult
from db_query_agent.formatters import format_result
from db_query_agent.schema import SchemaIntrospector


class DBQueryAgent:
    """Agent that translates natural language to SQL and executes queries."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._introspector = SchemaIntrospector(settings.database_url)
        self._executor = QueryExecutor(
            engine=self._introspector.engine,
            allow_mutations=settings.allow_mutations,
            max_rows=settings.max_query_rows,
        )
        self._agent = self._build_agent()

    def _build_agent(self) -> Agent:
        model = BedrockModel(
            model_id=self._settings.bedrock_model_id,
            region_name=self._settings.aws_region,
        )

        schema_desc = self._introspector.get_schema_description()

        system_prompt = f"""You are a database query assistant. Your job is to help users query a database using natural language.

{schema_desc}

RULES:
1. Always use the execute_query tool to run SQL queries.
2. Write standard SQL compatible with the database.
3. Only generate SELECT queries unless explicitly told mutations are allowed.
4. Always explain what the query does before executing.
5. If the user's request is ambiguous, ask for clarification.
6. Limit results to {self._settings.max_query_rows} rows unless the user specifies otherwise.
"""

        @tool
        def execute_query(sql: str) -> dict[str, Any]:
            """Execute a SQL query against the database.

            Args:
                sql: The SQL query to execute.

            Returns:
                Query results with columns, rows, and row count.
            """
            try:
                result: QueryResult = self._executor.execute(sql)
                return {
                    "columns": result.columns,
                    "rows": result.rows,
                    "row_count": result.row_count,
                    "query": result.query,
                }
            except QueryExecutionError as e:
                return {"error": str(e)}
            except Exception as e:
                return {"error": f"Query failed: {e}"}

        @tool
        def get_schema() -> str:
            """Get the database schema description.

            Returns:
                A text description of all tables and columns.
            """
            return schema_desc

        return Agent(
            model=model,
            system_prompt=system_prompt,
            tools=[execute_query, get_schema],
        )

    def query(self, prompt: str, response_format: str = "json") -> dict[str, Any]:
        """Process a natural language query and return formatted results."""
        result = self._agent(prompt)
        response_text = str(result)

        # Try to extract the last query result for formatting
        last_result = self._extract_last_result(response_text)

        return {
            "answer": response_text,
            "formatted_data": last_result,
            "format": response_format,
        }

    def _extract_last_result(self, response: str) -> str | None:
        """Extract structured data from agent response if available."""
        # The agent response contains the natural language answer.
        # Structured data is returned via tool calls handled by Strands.
        return None

    def query_raw(self, sql: str, response_format: str = "json") -> str:
        """Execute a raw SQL query directly (bypasses agent)."""
        result = self._executor.execute(sql)
        return format_result(result, response_format)
