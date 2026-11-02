"""Behavior spec for ingestion/client.py. Mock HTTP with the `responses` library; inject a fake
`sleep` that records delays instead of waiting.

Suggested helper (write it): `make_client(sleep=...)` building SodaClient from the real
config/pipeline.yaml with a fake Secrets and a recording Metrics.
"""

import pytest

pytestmark = pytest.mark.todo


def test_builds_expected_query_for_window():
    """Assert $where/$order/$limit/$offset on the first request exactly match the spec in the
    client docstring (window [start,end), order by last_modified_date, sr_number)."""
    pytest.skip("TODO")


def test_paginates_until_short_page(sample_rows):
    """page_size=5 with 12 rows served in pages 5,5,2 -> 3 Page objects, offsets 0,5,10."""
    pytest.skip("TODO")


def test_exact_multiple_of_page_size_fetches_one_extra_empty_page():
    """10 rows, page_size=5 -> requests at offsets 0,5,10; the last returns []. No 4th request."""
    pytest.skip("TODO")


def test_empty_window_yields_no_pages_and_no_error():
    pytest.skip("TODO")


def test_429_then_success_retries_with_backoff():
    """Serve 429, 429, 200. Expect 3 requests and recorded sleeps that grow (jitter: assert
    within bounds, not exact values)."""
    pytest.skip("TODO")


def test_retry_after_header_is_honored():
    pytest.skip("TODO")


def test_retries_exhausted_raises_transient_error_with_hint():
    pytest.skip("TODO")


def test_non_retryable_4xx_raises_contract_error_immediately():
    """400 -> exactly 1 request, SourceContractError."""
    pytest.skip("TODO")


def test_http_200_with_error_body_is_a_contract_error():
    """Body is a JSON object like {"error": true, "message": "..."} rather than an array."""
    pytest.skip("TODO")


def test_page_body_is_the_raw_response_bytes(sample_page_bytes):
    """Page.body == bytes served, byte for byte (so sha256 in the manifest is meaningful)."""
    pytest.skip("TODO")


def test_app_token_sent_as_header_and_never_in_url_or_params():
    pytest.skip("TODO")


def test_min_request_interval_spacing_is_applied_between_pages():
    pytest.skip("TODO")


def test_count_returns_int_from_string_payload():
    """SODA returns [{"count": "14918310"}] - a STRING. Parse it."""
    pytest.skip("TODO")
