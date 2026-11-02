"""Behavior spec for c311.errors and c311.logging_utils."""

import pytest

pytestmark = pytest.mark.todo


def test_error_str_includes_context_and_hint():
    """str(TransientSourceError("429 from SODA", hint="see runbook#rate-limits", page=3))
    contains the message, 'page=3' and the hint."""
    pytest.skip("TODO")


def test_retryable_flags():
    """TransientSourceError/WarehouseLoadError retryable; SchemaDriftError/DataQualityError not."""
    pytest.skip("TODO")


def test_log_event_emits_one_json_line_with_run_context(capfd):
    """bind_run('r1','extract'); log_event(logger,'page_fetched',rows=3). Parse the output as JSON;
    expect run_id, stage, level, event, timestamp(UTC ISO), rows."""
    pytest.skip("TODO")


def test_configure_logging_is_idempotent():
    """Call twice; exactly one handler on the root logger."""
    pytest.skip("TODO")


def test_app_token_never_logged():
    """Feed a client-like log call containing headers; assert the token string is absent."""
    pytest.skip("TODO")
