"""Socrata (SODA) API client.

RESPONSIBILITY
    Fetch pages of 311 records for a time window, with pagination, rate-limit handling and
    retries. Knows HTTP and SODA query syntax; knows NOTHING about S3, manifests or Airflow.

VERIFIED SOURCE FACTS (2026-11-02; re-verify if anything surprises you)
    Endpoint   GET {base_url}/resource/{dataset_id}.json
    Params     $select $where $order $limit $offset   (SODA 2.x)
    $limit     default 1000; SODA 2.0 max 50,000
    Auth       optional header `X-App-Token`; unauthenticated traffic shares an IP-based pool
               with a much lower ceiling
    Throttle   HTTP 429. Docs do not mention Retry-After: honor it if present, else back off.
    Types      Observed in the sample: numbers (ward, latitude, ...) arrive as JSON STRINGS,
               `duplicate`/`legacy_record` as real JSON booleans, `location` as a nested
               object. Absent/null fields are simply omitted from a row, so rows in one page
               can have different key sets. Do NOT convert types here - raw must stay
               faithful. Transform casts later.
    Timestamps `created_date`, `last_modified_date`, `closed_date` look like
               "2026-11-02T06:00:11.000": Chicago local time, no tz offset.
    Quirk      Whole-table aggregates (count(distinct ...), group-by) over ~15M rows can
               time out. Windowed counts (below) were fast in testing.

QUERY SHAPE for a window [start, end) (strings in source-local floating time)
    $where = last_modified_date >= '<start>' AND last_modified_date < '<end>'
    $order = last_modified_date, sr_number         <- total order; see edge cases
    $limit = page_size, $offset = n * page_size

DESIGN DECISIONS (decide, then write a sentence in ADR 0002 / code comment)
    - OFFSET paging over a *frozen* window with a *total* order is correct only if the
      result set doesn't change while you page. The upper bound `end` freezes the tail, but
      rows inside the window can still be modified mid-run (their last_modified_date jumps
      forward, OUT of the window) -> you can skip a row. Why is that acceptable here?
      (Hint: the next run's lookback re-reads it. Prove it to yourself with the window math
      in window.py.) Alternative: keyset paging (`last_modified_date, sr_number` > last seen)
      avoids OFFSET drift; compare the two and pick one.
    - Rate limiting is two layers: (a) proactive spacing between requests
      (min_request_interval_seconds), (b) reactive handling of 429/5xx with exponential
      backoff + jitter, capped by backoff_max_seconds and max_attempts.
    - Never put the app token in a URL or log it. Header only.
    - Return the raw response BYTES alongside the parsed rows. Raw files must be the bytes
      the server sent (so a checksum proves nothing was altered); parsing is for counting.

TODOs (in order)
    1. `Page` dataclass (below) - already shaped; read it.
    2. SodaClient.__init__: build a requests.Session with the token header and a
       User-Agent that identifies your project.
    3. `_request`: one HTTP GET with retry/backoff:
         - retry on config.retry_on_status and on connection/timeout errors
         - honor Retry-After when present (seconds form; consider the HTTP-date form)
         - sleep via an injectable `sleep` function so tests don't actually wait
         - after max_attempts raise TransientSourceError (with hint); on other 4xx raise
           SourceContractError (don't retry)
         - count retries via metrics.incr("c311.extract.http_retries")
    4. `count`: SELECT count(*) for the window - this is the "source count" used by
       reconciliation. Note what it is NOT (see docs/reconciliation.md).
    5. `iter_pages`: generator yielding Page objects until a short/empty page.
         pseudocode:
           offset = 0
           while True:
               body = _request(window, offset)
               rows = parse(body)
               if not rows: break
               yield Page(...)
               if len(rows) < page_size: break
               offset += page_size
    6. Validate the response *shape*: must be a JSON array of objects; a dict with an
       "error"/"message" key on HTTP 200 is a contract error, not an empty page.

EDGE CASES
    - Empty window -> zero pages, not an error.
    - Exactly page_size rows -> you must fetch one more (empty) page to know it's done.
    - Two rows with identical last_modified_date: the sr_number tiebreaker keeps order stable.
    - HTTP 200 with truncated/invalid JSON body (retry? it's transient-looking but your
      checksum can't help you; decide).
    - Clock: do not use "now" inside the client; the window is an input.

DONE WHEN
    - tests/unit/test_client.py passes (mocked HTTP via `responses`), including: 429 then
      success, retries exhausted, empty window, exact page boundary, token never in logs.
    - A manual smoke run against the real API for a 10-minute window returns pages and a
      count equal to the number of rows fetched (try it from a Python shell).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime

from c311.config import RetryConfig, Secrets, SourceConfig
from c311.metrics import Metrics


@dataclass(frozen=True)
class Window:
    """Half-open extraction window [start, end) in *source-local* naive time."""

    start: datetime  # naive, Chicago local
    end: datetime  # naive, Chicago local


@dataclass(frozen=True)
class Page:
    page_number: int  # 1-based
    offset: int
    request_params: dict[str, str]  # exactly what was sent (token NOT included)
    body: bytes  # raw response bytes, unmodified
    rows: list[dict[str, str]]  # parsed, for counting/inspection only
    http_status: int
    fetched_at_utc: datetime
    elapsed_ms: int


class SodaClient:
    def __init__(
        self,
        source: SourceConfig,
        retry: RetryConfig,
        secrets: Secrets,
        metrics: Metrics,
        *,
        sleep: Callable[[float], None] | None = None,  # injectable for tests
    ) -> None:
        raise NotImplementedError

    def count(self, window: Window) -> int:
        raise NotImplementedError

    def iter_pages(self, window: Window) -> Iterator[Page]:
        raise NotImplementedError
