"""Load schema, views, and sample data into PostgreSQL."""

from pathlib import Path

import psycopg2

import config
from db import get_connection

ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = ROOT / "schema"


def split_statements(sql_text):
    statements = []
    buffer = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip().rstrip(";")
            if statement:
                statements.append(statement)
            buffer = []
    trailing = "\n".join(buffer).strip()
    if trailing:
        statements.append(trailing)
    return statements


def run_file(conn, path):
    sql_text = path.read_text(encoding="utf-8")
    cursor = conn.cursor()
    for statement in split_statements(sql_text):
        cursor.execute(statement)
    conn.commit()
    cursor.close()
    print(f"Executed {path.name}")


def main():
    try:
        conn = get_connection(database='postgres')
    except Exception as exc:
        raise SystemExit(
            "Could not connect to PostgreSQL. Check POSTGRES_HOST, POSTGRES_USER, "
            f"and POSTGRES_PASSWORD.\n{exc}"
        ) from exc

    try:
        # Create database if it doesn't exist
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{config.POSTGRES_DATABASE}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {config.POSTGRES_DATABASE}")
            print(f"Created database {config.POSTGRES_DATABASE}")
        cursor.close()
        conn.close()
        
        # Connect to the new database
        conn = get_connection()
        run_file(conn, SCHEMA_DIR / "schema.sql")
        run_file(conn, SCHEMA_DIR / "views.sql")
        run_file(conn, SCHEMA_DIR / "seed.sql")
        print("Database urbannest is ready with sample data.")
    except Exception as exc:
        conn.rollback()
        raise SystemExit(f"Failed to initialize database:\n{exc}") from exc
    finally:
        conn.close()


if __name__ == "__main__":
    main()
