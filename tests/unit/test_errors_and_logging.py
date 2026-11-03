"""Behavior spec for c311.errors and c311.logging_utils."""

import pytest

from c311.errors import (
    DataQualityError,
    SchemaDriftError,
    TransientSourceError,
    WarehouseLoadError,
)

pytestmark = pytest.mark.todo


def test_error_str_includes_context_and_hint():
    err = TransientSourceError("429 from SODA", hint="see runbook#rate-limits", page=3)
    text = str(err)
    assert "429 from SODA" in text
    assert "page=3" in text
    assert "see runbook#rate-limits" in text


def test_retryable_flags():
    assert TransientSourceError("x").retryable is True
    assert WarehouseLoadError("x").retryable is True
    assert SchemaDriftError("x").retryable is False
    assert DataQualityError("x").retryable is False


def test_log_event_emits_one_json_line_with_run_context(capfd):
    """bind_run('r1','extract'); log_event(logger,'page_fetched',rows=3). Parse the output as JSON;
    expect run_id, stage, level, event, timestamp(UTC ISO), rows."""


def test_configure_logging_is_idempotent():
    """Call twice; exactly one handler on the root logger."""


def test_app_token_never_logged():
    """Feed a client-like log call containing headers; assert the token string is absent."""
