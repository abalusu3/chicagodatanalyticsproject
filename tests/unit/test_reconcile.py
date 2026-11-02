"""Behavior spec for reconcile.py. `compare` is a pure function over LayerCounts: test it
exhaustively with plain integers - no Spark, no DB.

Worked example to anchor the identities (verify by hand before coding):
    source=100, raw=100, rejected=2, duplicates_dropped=18, curated_distinct=80, warehouse=80
    -> raw = 2 + 18 + 80 holds, all checks pass.
"""

import pytest

pytestmark = pytest.mark.todo


def test_all_layers_agree():
    pytest.skip("TODO: use the worked example above")


def test_source_raw_within_tolerance_passes_and_beyond_fails():
    """tolerance 0.001: 1000 vs 1001 passes; 1000 vs 1100 fails."""
    pytest.skip("TODO")


def test_raw_identity_violation_means_rows_vanished():
    """raw=100 but rejected+dups+curated=97 -> failing outcome whose explanation says rows were
    lost/unaccounted for between raw and curated."""
    pytest.skip("TODO")


def test_warehouse_less_than_curated_flags_incomplete_load():
    pytest.skip("TODO")


def test_zero_everywhere_passes_with_note():
    pytest.skip("TODO")


def test_source_zero_raw_positive_fails():
    pytest.skip("TODO")


def test_render_names_each_count_and_what_it_means():
    """The text must define source/raw/curated/warehouse in plain English, not just numbers."""
    pytest.skip("TODO")


def test_reconcile_run_raises_with_runbook_hint_on_breach():
    pytest.skip("TODO")
