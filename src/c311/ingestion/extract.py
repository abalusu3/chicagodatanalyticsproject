"""Extraction orchestrator: API -> immutable raw files + manifest.

RESPONSIBILITY
    Glue between SodaClient (HTTP), ObjectStore (storage) and manifest.py (commit record).
    This is the function the Airflow `extract` task calls. It owns the ORDER of operations,
    which is what makes the stage safe to rerun.

ORDER OF OPERATIONS (the point of this module)
    1. Compute the physical window (window.to_source_window).
    2. Ask the source for count(*) in the window -> `source_count`.
    3. Stream pages; for each page compute sha256, write page file with put_if_absent.
       (Streaming: never hold all pages in memory.)
    4. Build the Manifest from what you ACTUALLY wrote and write it LAST.
    5. Emit metrics/logs; return a small summary (run_id, manifest key, counts) for XCom.
       Keep the return value small - XCom is not a data channel.

IDEMPOTENCY / RERUN STORY (answer these in code comments)
    - Task retried after crash at page 7 of 12: what exists in storage? What does the retry do?
    - Same interval backfilled a week later: new run_id, new files, new manifest. Is that
      fine? (Yes, if downstream dedup is correct. State why raw growth is acceptable.)
    - Manifest write fails after all pages succeeded: orphan pages, no manifest -> invisible
      to downstream. The retry must not leave two *visible* copies.

TODOs (in order)
    1. `extract_window(...)` implement steps 1-5 above.
    2. Decide empty-window behavior: write a manifest with zero pages (recommended: it
       proves the window was checked, and gap detection needs it) - or not. Justify.
    3. Add a sanity guard: if source_count == 0 for a window that is much older than
       "now - a few hours" but the previous run for an adjacent window had rows, log a
       warning. (Optional, nice for the interview story.)
    4. Compare rows_fetched to source_count; if they differ beyond tolerance, still write the
       manifest (the data is real) but record the discrepancy so reconcile.py can explain it.

EDGE CASES: page file write succeeds but process dies before manifest; ObjectAlreadyExists
for identical bytes vs different bytes; source returns more rows than count() said (rows
were added during the run); zero rows.

DONE WHEN
    - tests/unit/test_extract.py passes using a fake client + in-memory store.
    - A real run against the API for a short window produces page files + one manifest in
      MinIO, and re-running the same window creates a second run_id without touching the first.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from c311.config import PipelineConfig
from c311.ingestion.client import SodaClient, Window
from c311.metrics import Metrics
from c311.storage.base import ObjectStore


@dataclass(frozen=True)
class ExtractSummary:
    run_id: str
    manifest_key: str
    source_count: int
    row_count: int
    page_count: int


def extract_window(
    *,
    run_id: str,
    window: Window,
    interval_start_utc: datetime | None,
    interval_end_utc: datetime | None,
    config: PipelineConfig,
    client: SodaClient,
    store: ObjectStore,
    metrics: Metrics,
    now: datetime | None = None,  # inject for deterministic tests
) -> ExtractSummary:
    raise NotImplementedError


def list_successful_manifests(store: ObjectStore, prefix: str) -> list[str]:
    """Return keys of all `_manifest.json` files under prefix (sorted).

    TODO: implement via store.list_keys. Used by transform (which runs to process), the
    runbook's gap check, and reconcile. Mind: a run directory WITHOUT a manifest is
    incomplete and must not be returned.
    """
    raise NotImplementedError
