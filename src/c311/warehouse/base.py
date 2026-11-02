"""Warehouse interface.

RESPONSIBILITY
    The minimal contract the loader needs from "a SQL warehouse". Postgres implements it now
    (warehouse/postgres.py); Redshift/Snowflake/BigQuery would implement it later. The loader
    (load.py) and reconcile.py depend on this Protocol only.

DESIGN DECISIONS
    - SQL stays in `sql/warehouse/*.sql` files, not Python strings. Dialect differences
      (ON CONFLICT vs MERGE, types) are then isolated to those files + the implementation.
    - `transaction()` is the unit of atomicity: "stage -> upsert -> rebuild aggregates"
      commits together or not at all. That is what makes a failed load safe to rerun.
    - Staging data arrives through `bulk_load_staging`, because the fastest path differs per
      warehouse (Postgres: COPY; Redshift: COPY from S3; BigQuery: load job).

DONE WHEN: the Postgres implementation satisfies this Protocol (mypy) and the integration
test in tests/integration/test_warehouse_postgres.py passes.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from contextlib import AbstractContextManager
from typing import Protocol


class Warehouse(Protocol):
    def transaction(self) -> AbstractContextManager[Warehouse]:
        """Context manager: commit on success, roll back on exception."""
        ...

    def execute_file(self, path: str, params: dict[str, object] | None = None) -> None:
        """Run a .sql file (one or more statements) with bound parameters."""
        ...

    def scalar(self, sql: str, params: dict[str, object] | None = None) -> object:
        """Run a query that returns one value (counts for reconciliation)."""
        ...

    def bulk_load_staging(
        self, table: str, columns: Sequence[str], rows: Iterator[Sequence[object]]
    ) -> int:
        """Load rows into a (truncated) staging table; return rows loaded."""
        ...
