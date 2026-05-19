"""Tests for schema introspection."""

from sqlalchemy import create_engine, text

from db_query_agent.schema import SchemaIntrospector


def test_get_tables():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE orders (id INTEGER PRIMARY KEY, amount REAL NOT NULL)"))
        conn.commit()

    introspector = SchemaIntrospector("sqlite:///:memory:")
    # Use the engine we created
    introspector._engine = engine
    introspector._metadata.reflect(bind=engine)

    tables = introspector.get_tables()
    assert len(tables) == 1
    assert tables[0].name == "orders"
    assert len(tables[0].columns) == 2


def test_schema_description():
    engine = create_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT)"))
        conn.commit()

    introspector = SchemaIntrospector("sqlite:///:memory:")
    introspector._engine = engine
    introspector._metadata.reflect(bind=engine)

    desc = introspector.get_schema_description()
    assert "products" in desc
    assert "name" in desc
