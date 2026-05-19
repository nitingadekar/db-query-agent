"""Seed a demo SQLite database for local testing."""

from sqlalchemy import create_engine, text

DB_URL = "sqlite:///./demo.db"


def seed() -> None:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                country TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES customers(id),
                product TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT NOT NULL,
                ordered_at TEXT NOT NULL
            )
        """))

        conn.execute(text("DELETE FROM orders"))
        conn.execute(text("DELETE FROM customers"))

        conn.execute(text("""
            INSERT INTO customers (id, name, email, country, created_at) VALUES
            (1, 'Alice Johnson', 'alice@example.com', 'UK', '2024-01-15'),
            (2, 'Bob Smith', 'bob@example.com', 'US', '2024-02-20'),
            (3, 'Charlie Brown', 'charlie@example.com', 'AU', '2024-03-10'),
            (4, 'Diana Prince', 'diana@example.com', 'UK', '2024-04-05'),
            (5, 'Eve Wilson', 'eve@example.com', 'DE', '2024-05-12')
        """))

        conn.execute(text("""
            INSERT INTO orders (id, customer_id, product, amount, status, ordered_at) VALUES
            (1, 1, 'Widget Pro', 49.99, 'completed', '2024-06-01'),
            (2, 1, 'Gadget X', 129.99, 'completed', '2024-06-15'),
            (3, 2, 'Widget Pro', 49.99, 'shipped', '2024-07-01'),
            (4, 3, 'Super Bundle', 299.99, 'completed', '2024-07-10'),
            (5, 4, 'Gadget X', 129.99, 'pending', '2024-08-01'),
            (6, 5, 'Widget Pro', 49.99, 'completed', '2024-08-15'),
            (7, 2, 'Super Bundle', 299.99, 'completed', '2024-09-01'),
            (8, 1, 'Widget Pro', 49.99, 'shipped', '2024-09-10')
        """))
        conn.commit()

    print(f"Demo database seeded at {DB_URL}")


if __name__ == "__main__":
    seed()
