"""Real, passing tests that validate the provided fixtures (not your pipeline).

These pin down facts the rest of the suite relies on. If one fails after you refresh the
sample, update the fixture README and any assumptions that depended on it.
"""

from __future__ import annotations

import json


def test_sample_is_a_json_array_of_unique_sr_numbers(sample_rows):
    assert len(sample_rows) == 12
    keys = [r["sr_number"] for r in sample_rows]
    assert len(keys) == len(set(keys))


def test_sample_numbers_are_strings_and_booleans_are_not(sample_rows):
    # Documented in ingestion/client.py: numbers arrive as strings, flags as JSON booleans.
    row = next(r for r in sample_rows if "ward" in r)
    assert isinstance(row["ward"], str)
    assert isinstance(row["duplicate"], bool)


def test_sample_timestamps_have_millis_and_no_timezone(sample_rows):
    ts = sample_rows[0]["created_date"]
    assert len(ts) == len("2026-11-02T06:00:11.000")
    assert not ts.endswith("Z") and "+" not in ts


def test_sample_rows_may_omit_fields(sample_rows):
    # Missing values are omitted, not null -> drift detection must not treat absence in one
    # batch as removal.
    key_sets = {frozenset(r) for r in sample_rows}
    assert len(key_sets) > 1


def test_sample_bytes_round_trip(sample_page_bytes, sample_rows):
    assert json.loads(sample_page_bytes) == sample_rows


def test_messy_fixture_has_expected_cases(messy_rows):
    keys = [r.get("sr_number") for r in messy_rows]
    assert keys.count("SR-TEST-002") == 2  # the dedupe pair
    assert None in keys or any("sr_number" not in r for r in messy_rows)  # the missing-key row
