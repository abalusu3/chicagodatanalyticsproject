"""End-to-end scenarios over the whole stack, with the HTTP API replaced by a stub server or
`responses` (never hit the real API from tests: it's slow, rate limited and not deterministic).
Needs the compose stack (MinIO + Postgres). These are your acceptance tests: when they pass,
the pipeline works.
"""

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.spark, pytest.mark.todo]


def test_happy_path_one_interval():
    """Stub API serves sample_311_page1.json. Run extract->transform->quality->load->reconcile.
    Expect: manifest in MinIO, 12 curated rows, 12 fact rows, reconciliation ok."""
    pytest.skip("TODO")


def test_rerunning_same_interval_changes_nothing_downstream():
    """Snapshot curated + warehouse (counts and a content hash); run the interval again; equal."""
    pytest.skip("TODO")


def test_overlapping_windows_dedupe_to_one_row_per_request():
    pytest.skip("TODO")


def test_updated_record_in_later_run_replaces_earlier_version():
    pytest.skip("TODO")


def test_api_outage_mid_extract_leaves_no_visible_partial_run():
    pytest.skip("TODO")


def test_additive_schema_change_proceeds_and_is_reported():
    pytest.skip("TODO")


def test_breaking_schema_change_stops_before_curated_is_touched():
    pytest.skip("TODO")


def test_backfill_of_old_interval_does_not_regress_newer_rows():
    pytest.skip("TODO")
