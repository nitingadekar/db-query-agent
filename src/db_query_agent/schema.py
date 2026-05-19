"""Database schema introspection for agent context."""

from dataclasses import dataclass

from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class ColumnInfo:
    name: str
    type: str
    nullable: bool
    primary_key: bool


@dataclass(frozen=True)
class TableInfo:
    name: str
    columns: tuple[ColumnInfo, ...]


class SchemaIntrospector:
    """Introspects database schema to provide context to the agent."""

    def __init__(self, database_url: str) -> None:
        self._engine: Engine = create_engine(database_url)
        self._metadata = MetaData()
        self._metadata.reflect(bind=self._engine)

    @property
    def engine(self) -> Engine:
        return self._engine

    def get_tables(self) -> list[TableInfo]:
        inspector = inspect(self._engine)
        tables: list[TableInfo] = []
        for table_name in inspector.get_table_names():
            columns = tuple(
                ColumnInfo(
                    name=col["name"],
                    type=str(col["type"]),
                    nullable=col["nullable"],
                    primary_key=col.get("primary_key", False),
                )
                for col in inspector.get_columns(table_name)
            )
            tables.append(TableInfo(name=table_name, columns=columns))
        return tables

    def get_schema_description(self) -> str:
        """Generate a text description of the schema for the agent system prompt."""
        tables = self.get_tables()
        if not tables:
            return "No tables found in the database."

        lines: list[str] = ["DATABASE SCHEMA:", ""]
        for table in tables:
            lines.append(f"Table: {table.name}")
            for col in table.columns:
                pk = " [PK]" if col.primary_key else ""
                null = " NULL" if col.nullable else " NOT NULL"
                lines.append(f"  - {col.name}: {col.type}{null}{pk}")
            lines.append("")
        return "\n".join(lines)
