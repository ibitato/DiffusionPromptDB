"""
PostgreSQL database helpers.

This module replaces the previous SQLite-only utilities with a lightweight
adapter that keeps the same API surface (`connection.execute(...).fetchone()`,
`.commit()`, etc.) so that the rest of the codebase can continue to treat the
database layer as if it were SQLite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Sequence

import psycopg
from psycopg import Error as PsycopgError, IntegrityError as PsycopgIntegrityError

from .config import settings

DatabaseError = PsycopgError
IntegrityConstraintError = PsycopgIntegrityError


def _convert_qmark_sql(query: str) -> str:
    """Translate SQLite-style '?' placeholders into psycopg '%s' markers."""
    return query.replace("?", "%s") if "?" in query else query


def _normalize_params(params: Any) -> Any:
    """Normalize parameter sequences for psycopg."""
    if params is None:
        return None
    if isinstance(params, (bytes, str)):
        return (params,)
    if isinstance(params, Sequence):
        return tuple(params)
    return (params,)


def _normalize_param_seq(items: Iterable[Sequence[Any]]) -> Iterable[tuple[Any, ...]]:
    for item in items:
        yield tuple(item)


class SQLiteRow(dict):
    """Row object that mimics sqlite3.Row indexing semantics."""

    __slots__ = ("_ordered", "_column_names")

    def __init__(self, columns: Sequence[str], values: Sequence[Any]):
        data = dict(zip(columns, values))
        super().__init__(data)
        self._ordered = tuple(values)
        self._column_names = tuple(columns)

    def __getitem__(self, key: Any) -> Any:
        if isinstance(key, int):
            return self._ordered[key]
        return super().__getitem__(key)

    def __iter__(self):
        return iter(self._ordered)

    def keys(self):
        return self._column_names

    def values(self):
        return self._ordered

    def items(self):
        return zip(self._column_names, self._ordered)

    def keys(self):
        return self.__class__.keys.__wrapped__(self) if hasattr(self.__class__.keys, "__wrapped__") else super().keys()


@dataclass
class DatabaseCursor:
    """SQLite-compatible cursor facade on top of psycopg."""

    _cursor: psycopg.Cursor
    _columns: tuple[str, ...] = ()

    def execute(self, query: str, params: Any = None) -> "DatabaseCursor":
        sql = _convert_qmark_sql(query)
        normalized = _normalize_params(params)
        self._cursor.execute(sql, normalized)
        if self._cursor.description:
            self._columns = tuple(desc.name for desc in self._cursor.description)
        else:
            self._columns = ()
        return self

    def executemany(
        self, query: str, param_seq: Iterable[Sequence[Any]]
    ) -> "DatabaseCursor":
        sql = _convert_qmark_sql(query)
        normalized_seq = list(_normalize_param_seq(param_seq))
        self._cursor.executemany(sql, normalized_seq)
        return self

    def _wrap_row(self, row: Sequence[Any] | None):
        if row is None or not self._columns:
            return row
        return SQLiteRow(self._columns, row)

    def fetchone(self):
        row = self._cursor.fetchone()
        return self._wrap_row(row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [self._wrap_row(row) for row in rows] if self._columns else rows

    def fetchmany(self, size: int | None = None):
        rows = self._cursor.fetchmany(size)
        return [self._wrap_row(row) for row in rows] if self._columns else rows

    @property
    def description(self):
        return self._cursor.description

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def close(self) -> None:
        self._cursor.close()

    def __iter__(self):
        return iter(self.fetchall())


class DatabaseConnection:
    """SQLite-like connection wrapper backed by psycopg."""

    def __init__(self, conn: psycopg.Connection[Any]):
        self._conn = conn

    def cursor(self) -> DatabaseCursor:
        return DatabaseCursor(self._conn.cursor())

    def execute(self, query: str, params: Any = None) -> DatabaseCursor:
        cursor = self.cursor()
        return cursor.execute(query, params)

    def executemany(self, query: str, param_seq: Iterable[Sequence[Any]]) -> None:
        cursor = self.cursor()
        cursor.executemany(query, param_seq)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()


def _open_connection(conninfo: str) -> DatabaseConnection:
    conn = psycopg.connect(conninfo)
    return DatabaseConnection(conn)


def get_users_db():
    """FastAPI dependency that yields a connection to the users database."""
    conn = _open_connection(settings.users_db_url)
    try:
        yield conn
    finally:
        conn.close()


def get_prompts_db():
    """FastAPI dependency that yields a connection to the prompts/catalog DB."""
    conn = _open_connection(settings.prompts_db_url)
    try:
        yield conn
    finally:
        conn.close()


def get_prompts_db_connection() -> DatabaseConnection:
    """Utility helper for scripts/services that need an immediate connection."""
    return _open_connection(settings.prompts_db_url)
