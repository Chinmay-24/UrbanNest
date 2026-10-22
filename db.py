import mysql.connector
from mysql.connector import Error

import config


class DatabaseError(Exception):
    """Raised when a parameterized query fails."""


def get_connection(database=None):
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=database if database is not None else config.MYSQL_DATABASE,
        charset="utf8mb4",
        collation="utf8mb4_unicode_ci",
        autocommit=False,
    )


def fetch_all(sql, params=None):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    except Error as exc:
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
        last_id = cursor.lastrowid
        cursor.close()
        return last_id
    except Error as exc:
        conn.rollback()
        raise DatabaseError(str(exc)) from exc
    finally:
        conn.close()
