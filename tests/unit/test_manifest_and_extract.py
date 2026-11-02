"""Behavior spec for ingestion/manifest.py and ingestion/extract.py.

Test doubles you'll want (write small ones here): FakeSodaClient with canned pages + count();
InMemoryStore and RecordingMetrics. A store wrapper that raises on the Nth write lets you
simulate a crash mid-extraction.
"""

import pytest

pytestmark = pytest.mark.todo


# --- manifest ---------------------------------------------------------------------------
def test_manifest_round_trips_through_json():
    pytest.skip("TODO")


def test_manifest_validation_rejects_row_count_mismatch():
    """row_count != sum(page.row_count) -> error naming both numbers."""
    pytest.skip("TODO")


def test_manifest_validation_rejects_non_contiguous_pages():
    pytest.skip("TODO")


def test_key_layout_is_stable():
    """chicago_311/ingest_date=2026-11-02/run_id=abc/page-00001.json and .../_manifest.json"""
    pytest.skip("TODO")


# --- extract ----------------------------------------------------------------------------
def test_extract_writes_pages_then_manifest_last(memory_store):
    """Record write order; the manifest must be the final write."""
    pytest.skip("TODO")


def test_page_files_contain_exact_response_bytes_and_sha_matches(memory_store, sample_page_bytes):
    pytest.skip("TODO")


def test_crash_before_manifest_leaves_no_visible_run(memory_store):
    """Fail the manifest write. list_successful_manifests() must not return this run, even
    though page files exist."""
    pytest.skip("TODO")


def test_retry_with_same_run_id_tolerates_existing_identical_pages(memory_store):
    """Only meaningful if you chose to reuse run_ids across retries (ADR 0003)."""
    pytest.skip("TODO")


def test_existing_page_with_different_bytes_is_an_error(memory_store):
    """Immutability: never silently overwrite."""
    pytest.skip("TODO")


def test_second_run_over_same_window_creates_new_run_and_leaves_first_untouched(memory_store):
    pytest.skip("TODO")


def test_zero_row_window_writes_manifest_with_zero_pages(memory_store):
    pytest.skip("TODO (or assert your alternative decision)")


def test_rows_fetched_vs_source_count_discrepancy_is_recorded_not_fatal(memory_store):
    pytest.skip("TODO")


def test_summary_is_small_and_json_serializable():
    """It goes through XCom."""
    pytest.skip("TODO")
