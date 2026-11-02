"""Postgres implementation of Warehouse (psycopg 3).

RESPONSIBILITY
    Connection handling, transactions, running SQL files, and COPY-based staging loads.

TODOs (in order)
    1. __init__(dsn): store dsn; connect lazily. Never log the DSN (it contains the password).
    2. transaction(): contextmanager yielding a Warehouse bound to ONE connection with
       autocommit off; commit/rollback; always close. Nested transactions: forbid (raise)
       rather than silently flattening.
    3. execute_file(path, params): read the file, execute with named params (`%(name)s`).
       Think about multi-statement files: psycopg3 allows them only without params in some
       modes - find out and handle (split statements, or one statement per file).
    4. scalar(): fetchone()[0]; raise if no row.
    5. bulk_load_staging(): `COPY ... FROM STDIN` via cursor.copy(); stream rows (don't
       materialize 100k rows in a list). Return row count.
    6. Wrap psycopg errors in WarehouseLoadError with a hint ("transaction rolled back; safe
       to rerun the load task").

EDGE CASES: connection drops mid-COPY; NUL bytes / embedded newlines in text (COPY text
format escaping); NULL vs empty string; timestamp formatting; huge batches.

DONE WHEN: tests/integration/test_warehouse_postgres.py passes against the compose Postgres.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import AbstractContextManager


class PostgresWarehouse:
    def __init__(self, dsn: str) -> None:
        raise NotImplementedError

    def transaction(self) -> AbstractContextManager[PostgresWarehouse]:
        raise NotImplementedError

    def execute_file(self, path: str, params: dict[str, object] | None = None) -> None:
        raise NotImplementedError

    def scalar(self, sql: str, params: dict[str, object] | None = None) -> object:
        raise NotImplementedError

    def bulk_load_staging(
        self, table: str, columns: Sequence[str], rows: Iterator[Sequence[object]]
    ) -> int:
        raise NotImplementedError
