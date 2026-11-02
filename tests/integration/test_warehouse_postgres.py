"""Integration tests: need `make up` (compose Postgres). Run with `pytest -m integration`.

Design the fixture so each test gets clean tables (TRUNCATE in a fixture, or a unique schema
per test). Tests must not depend on execution order.
"""

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.todo]


def test_ddl_is_idempotent():
    """Run sql/warehouse/001_schemas_and_tables.sql twice; no error."""
    pytest.skip("TODO")


def test_transaction_rolls_back_on_error():
    """Insert, then raise inside `with wh.transaction()`; table empty afterwards."""
    pytest.skip("TODO")


def test_upsert_is_idempotent():
    """Stage + upsert the same 5 rows twice: count stays 5."""
    pytest.skip("TODO")


def test_stale_row_does_not_overwrite_newer_row():
    pytest.skip("TODO")


def test_aggregates_rebuilt_only_for_affected_days_and_match_group_by():
    """Two days loaded; reload touching one day: other day's agg rows untouched (check a marker
    column / xmin); every agg equals an independent GROUP BY on the fact table."""
    pytest.skip("TODO")


def test_status_change_on_old_created_date_updates_that_days_aggregate():
    pytest.skip("TODO")


def test_load_audit_row_written_even_for_zero_rows():
    pytest.skip("TODO")


def test_copy_handles_embedded_newlines_quotes_and_nulls():
    pytest.skip("TODO")
