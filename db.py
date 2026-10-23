import psycopg2
import psycopg2.extras

import config


class DatabaseError(Exception):
    """Raised when a parameterized query fails."""


def get_connection(database=None):
    return psycopg2.connect(
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        database=database if database is not None else config.POSTGRES_DATABASE,
    )


def fetch_all(sql, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]
    except Exception as exc:
        raise DatabaseError(str(exc)) from exc
    finally:
        conn.close()


def fetch_one(sql, params=None):
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        conn.commit()
        last_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
        cursor.close()
        return last_id
    except Exception as exc:
        conn.rollback()
        raise DatabaseError(str(exc)) from exc
    finally:
        conn.close()
