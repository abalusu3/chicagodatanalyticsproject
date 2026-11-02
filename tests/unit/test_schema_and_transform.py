"""Behavior spec for transform/schema.py and transform/raw_to_curated.py.

Pure-Python parts (drift detection) run in the fast job. DataFrame tests need Spark: mark them
`@pytest.mark.spark` so the fast CI job skips them. Build tiny DataFrames from `messy_rows`
with the explicit RAW_SCHEMA (never inferSchema).
"""

import pytest

pytestmark = pytest.mark.todo


# --- drift (no Spark needed) ------------------------------------------------------------
def test_sample_fixture_has_no_drift(sample_rows):
    """Union of keys in the real sample is a subset of EXPECTED_RAW_FIELDS -> no additive,
    no breaking. (Fields absent from this small batch are NOT 'missing'.)"""
    pytest.skip("TODO")


def test_new_field_is_additive_drift(messy_rows):
    """SR-TEST-012 carries `brand_new_field` -> report.additive == ['brand_new_field'], not breaking."""
    pytest.skip("TODO")


def test_entirely_absent_core_field_is_breaking():
    """e.g. no row has `sr_number` over a large batch -> breaking; raise_if_breaking raises
    SchemaDriftError whose hint references docs/schema-policy.md."""
    pytest.skip("TODO")


# --- Spark: parse / split ---------------------------------------------------------------
@pytest.mark.spark
def test_parse_timestamps_with_millis_and_no_zone(spark):
    pytest.skip("TODO")


@pytest.mark.spark
def test_unparseable_timestamp_row_is_rejected_with_reason(spark, messy_rows):
    """SR-TEST-006 lands in rejected_df with reason mentioning created_date; valid_df lacks it."""
    pytest.skip("TODO")


@pytest.mark.spark
def test_missing_sr_number_is_rejected(spark, messy_rows):
    pytest.skip("TODO")


@pytest.mark.spark
def test_leading_zeros_preserved_in_zip_and_police_district(spark, messy_rows):
    """SR-TEST-011: '06010' and '06' remain strings."""
    pytest.skip("TODO")


@pytest.mark.spark
def test_booleans_and_missing_fields_become_typed_nulls(spark, sample_rows):
    pytest.skip("TODO")


@pytest.mark.spark
def test_suspicious_but_parseable_rows_are_not_rejected(spark, messy_rows):
    """SR-TEST-007 (bad coords) and SR-TEST-008 (out-of-range ward) stay in valid_df: they're
    quality-check territory, not rejection."""
    pytest.skip("TODO")


# --- Spark: dedupe ----------------------------------------------------------------------
@pytest.mark.spark
def test_dedupe_keeps_latest_last_modified(spark, messy_rows):
    """Of the two SR-TEST-002 rows, the Completed one (15:30) survives."""
    pytest.skip("TODO")


@pytest.mark.spark
def test_dedupe_tie_break_is_deterministic(spark):
    """Same sr_number and same last_modified_ts, different content: result is the same on
    every run and every input ordering (shuffle the input rows)."""
    pytest.skip("TODO")


# --- Spark + Delta: merge ---------------------------------------------------------------
@pytest.mark.spark
def test_first_run_creates_table_with_curated_schema(spark, tmp_path):
    pytest.skip("TODO")


@pytest.mark.spark
def test_merge_twice_is_idempotent(spark, tmp_path):
    """Merge the same batch twice: row count and table contents identical (compare sorted rows)."""
    pytest.skip("TODO")


@pytest.mark.spark
def test_older_batch_does_not_overwrite_newer_row(spark, tmp_path):
    """Merge Completed(15:30), then the Open(09:00) copy of the same key -> still Completed;
    MergeMetrics.skipped_stale == 1."""
    pytest.skip("TODO")


@pytest.mark.spark
def test_merge_updates_changed_row_and_inserts_new_row(spark, tmp_path):
    pytest.skip("TODO")


@pytest.mark.spark
def test_quarantine_not_duplicated_on_rerun(spark, tmp_path):
    pytest.skip("TODO (depends on the keying decision you made)")


@pytest.mark.spark
def test_high_quarantine_fraction_aborts_before_touching_curated(spark, tmp_path):
    """Exceed max_quarantine_fraction -> error raised, curated table unchanged."""
    pytest.skip("TODO")


@pytest.mark.spark
def test_read_raw_only_reads_files_listed_in_manifests(spark, memory_store):
    """Plant an orphan page file (no manifest) under the raw prefix; it must not appear."""
    pytest.skip("TODO")
