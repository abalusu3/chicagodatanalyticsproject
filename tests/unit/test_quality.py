"""Behavior spec for quality/checks.py. Each test builds a 3-6 row DataFrame (Spark needed,
so marked) from the curated schema, runs ONE check, asserts on the CheckResult.

Tip: write a `make_curated_df(spark, **overrides)` helper that returns a valid baseline row
you can tweak - then every test is one line of arrange.
"""

import pytest

pytestmark = [pytest.mark.todo, pytest.mark.spark]


def test_required_fields_pass_on_clean_data(spark):
    pytest.skip("TODO")


def test_required_fields_flag_null_and_blank(spark):
    """Both NULL and '   ' count as missing. failing_rows and sample_keys populated."""
    pytest.skip("TODO")


def test_created_after_last_modified_is_flagged(spark):
    """SR-TEST-004."""
    pytest.skip("TODO")


def test_closed_before_created_is_flagged(spark):
    """SR-TEST-005. Also: open requests (closed_ts NULL) are fine."""
    pytest.skip("TODO")


def test_future_timestamp_beyond_skew_is_flagged_but_within_skew_passes(spark):
    pytest.skip("TODO")


def test_duplicate_identifiers_detected(spark):
    pytest.skip("TODO")


def test_ward_and_community_area_out_of_range_flagged_but_null_is_not(spark):
    pytest.skip("TODO")


def test_coordinates_outside_chicago_box_flagged_but_null_coords_are_not(spark):
    pytest.skip("TODO")


def test_unseen_status_value_is_warn_not_error(spark):
    pytest.skip("TODO")


def test_sample_keys_are_capped_and_contain_no_addresses(spark):
    """Results must never leak full rows."""
    pytest.skip("TODO")


def test_enforce_raises_once_listing_all_error_failures(spark):
    """Two failing error-severity checks -> ONE DataQualityError mentioning both."""
    pytest.skip("TODO")


def test_enforce_does_not_raise_for_warn_only(spark):
    pytest.skip("TODO")
