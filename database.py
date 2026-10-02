"""
Database module for the Expense Tracker System (PostgreSQL via psycopg2 with automatic SQLite fallback).

Provides:
  * get_db_connection()  - opens connection (PostgreSQL or SQLite connection)
  * init_db()            - runs database/schema.sql (tables + sample data)
  * execute_query()      - SELECT helper returning dicts
  * execute_non_query()  - INSERT / UPDATE / DELETE helper
"""

import os
import re
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

import config

SCHEMA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "schema.sql")
SQLITE_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "expense_tracker.db")

_USE_SQLITE = None


def _check_postgres() -> bool:
    if not PSYCOPG2_AVAILABLE:
        return False
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception:
        return False


def is_sqlite() -> bool:
    global _USE_SQLITE
    if _USE_SQLITE is None:
        _USE_SQLITE = not _check_postgres()
        if _USE_SQLITE:
            print("[DB] PostgreSQL connection unavailable. Falling back to local SQLite database.")
        else:
            print("[DB] PostgreSQL database connected successfully.")
    return _USE_SQLITE


def convert_schema_to_sqlite(pg_sql: str) -> str:
    lines = []
    for line in pg_sql.splitlines():
        if "setval(" in line or "pg_get_serial_sequence" in line:
            continue
        lines.append(line)
    sql = "\n".join(lines)
    sql = re.sub(r'SERIAL\s+PRIMARY\s+KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bTIMESTAMP\b', 'DATETIME', sql, flags=re.IGNORECASE)
    return sql


def translate_query_for_sqlite(query: str) -> str:
    q = query
    filter_pattern = r'COALESCE\s*\(\s*SUM\s*\(\s*e\.amount\s*\)\s*FILTER\s*\(\s*WHERE\s+TO_CHAR\s*\(\s*e\.expense_date\s*,\s*\'YYYY-MM\'\s*\)\s*=\s*TO_CHAR\s*\(\s*CURRENT_DATE\s*,\s*\'YYYY-MM\'\s*\)\s*\)\s*,\s*0\.00\s*\)'
    q = re.sub(filter_pattern, "COALESCE(SUM(CASE WHEN strftime('%Y-%m', e.expense_date) = strftime('%Y-%m', 'now') THEN e.amount ELSE 0 END), 0.00)", q, flags=re.IGNORECASE)
    q = re.sub(r"TO_CHAR\s*\(\s*([e\w\.]+)\s*,\s*'IYYY-\"W\"IW'\s*\)", r"strftime('%Y-W%W', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"TO_CHAR\s*\(\s*([e\w\.]+)\s*,\s*'YYYY-MM'\s*\)", r"strftime('%Y-%m', \1)", q, flags=re.IGNORECASE)
    q = re.sub(r"TO_CHAR\s*\(\s*CURRENT_DATE\s*,\s*'YYYY-MM'\s*\)", "strftime('%Y-%m', 'now')", q, flags=re.IGNORECASE)
    q = re.sub(r'\bILIKE\b', 'LIKE', q, flags=re.IGNORECASE)
    q = re.sub(r'\s+RETURNING\s+id\b', '', q, flags=re.IGNORECASE)
    q = q.replace('%s', '?')
    return q


def get_db_connection():
    """Open a new PostgreSQL connection (credentials come from environment variables)."""
    if is_sqlite():
        conn = sqlite3.connect(SQLITE_DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )


def _clean_value(value: Any) -> Any:
    """Convert DB types into plain Python/JSON friendly values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    return value


def _clean_row(row: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return {k: _clean_value(v) for k, v in row.items()} if row else None


def tables_exist() -> bool:
    """True if the main tables are already present in the database."""
    if is_sqlite():
        conn = sqlite3.connect(SQLITE_DB_FILE)
        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'expenses')")
            rows = cur.fetchall()
            return len(rows) == 2
        finally:
            conn.close()
    else:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT to_regclass('public.users'), to_regclass('public.expenses')")
                users, expenses = cur.fetchone()
                return users is not None and expenses is not None
        finally:
            conn.close()


def init_db(force: bool = False) -> None:
    """Create tables and load sample data from database/schema.sql.
    Runs only when the tables are missing, unless force=True (which RESETS all data)."""
    if not force and tables_exist():
        print("[DB] Tables already exist - skipping initialisation.")
        return
    print("[DB] Creating tables and loading sample data ...")
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    if is_sqlite():
        os.makedirs(os.path.dirname(SQLITE_DB_FILE), exist_ok=True)
        converted_sql = convert_schema_to_sqlite(schema_sql)
        conn = sqlite3.connect(SQLITE_DB_FILE)
        try:
            conn.executescript(converted_sql)
            conn.commit()
            print("[DB] SQLite database ready.")
        finally:
            conn.close()
    else:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()
            print("[DB] Database ready.")
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def execute_query(query: str, params: Sequence = (), fetch_all: bool = True):
    """Run a SELECT. Returns a list of dicts (fetch_all=True) or one dict / None."""
    if is_sqlite():
        sq_query = translate_query_for_sqlite(query)
        conn = sqlite3.connect(SQLITE_DB_FILE)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.cursor()
            cur.execute(sq_query, params)
            if fetch_all:
                return [_clean_row(dict(r)) for r in cur.fetchall()]
            row = cur.fetchone()
            return _clean_row(dict(row)) if row else None
        finally:
            conn.close()
    else:
        conn = get_db_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch_all:
                    return [_clean_row(r) for r in cur.fetchall()]
                return _clean_row(cur.fetchone())
        finally:
            conn.close()


def execute_non_query(query: str, params: Sequence = ()) -> int:
    """Run INSERT / UPDATE / DELETE.
    Returns the new id when the query has RETURNING id, otherwise the affected row count."""
    if is_sqlite():
        sq_query = translate_query_for_sqlite(query)
        conn = sqlite3.connect(SQLITE_DB_FILE)
        try:
            cur = conn.cursor()
            cur.execute(sq_query, params)
            res = cur.lastrowid if "INSERT INTO" in query.upper() else cur.rowcount
            conn.commit()
            return res
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchone()[0] if cur.description else cur.rowcount
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

