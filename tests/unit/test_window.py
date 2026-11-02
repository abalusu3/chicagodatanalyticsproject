"""Behavior spec for ingestion/window.py. Pure functions: these tests should be your fastest,
and the DST cases are the ones that matter.

Useful constants (2026): US DST starts Sunday 2026-03-08 (02:00 local skipped) and ends
Sunday 2026-11-01 (01:00-02:00 local happens twice). Verify these yourself.
"""

import pytest

pytestmark = pytest.mark.todo


def test_basic_window_applies_lookback_to_start_only():
    """interval [10:00Z, 11:00Z), lookback 6h -> local window start is 6h earlier, end unchanged."""
    pytest.skip("TODO")


def test_converts_utc_to_chicago_local_naive():
    """Result datetimes are naive (tzinfo None) and in America/Chicago local time."""
    pytest.skip("TODO")


def test_naive_input_is_rejected():
    pytest.skip("TODO")


def test_zero_lookback():
    pytest.skip("TODO")


def test_lookback_longer_than_interval():
    pytest.skip("TODO")


def test_window_across_spring_forward_does_not_lose_rows():
    pytest.skip(
        "TODO: assert your chosen policy (e.g. window is at least as wide as the true span)"
    )


def test_window_across_fall_back_does_not_lose_rows():
    pytest.skip("TODO")


def test_format_soda_timestamp_matches_source_format():
    """format_soda_timestamp(datetime(2026,11,2,6,0,11)) == '2026-11-02T06:00:11.000'."""
    pytest.skip("TODO")


def test_consecutive_intervals_overlap_by_exactly_lookback():
    """Windows of run N and N+1 overlap by lookback_hours: no gaps, ever."""
    pytest.skip("TODO")


def test_find_gaps_detects_missing_interval():
    """Intervals [0,1),[1,2),[3,4) -> gap (2,3). Contiguous input -> []."""
    pytest.skip("TODO")
