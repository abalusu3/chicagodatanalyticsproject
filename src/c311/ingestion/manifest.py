"""Extraction manifest: the commit record for one raw extraction run.

RESPONSIBILITY
    Define the manifest schema and (de)serialize it. The manifest is written LAST, after all
    page files; its existence means "this run's raw files are complete". Downstream code
    must only read runs that have a manifest. That is how a crash mid-extraction leaves
    harmless orphan files instead of a half-visible dataset.

RAW LAYOUT (object keys under the raw bucket)
    chicago_311/ingest_date=YYYY-MM-DD/run_id=<run_id>/page-00001.json
    chicago_311/ingest_date=YYYY-MM-DD/run_id=<run_id>/page-00002.json
    chicago_311/ingest_date=YYYY-MM-DD/run_id=<run_id>/_manifest.json     <- written last
    ingest_date is UTC date of extraction start. Files are never modified or deleted by the
    pipeline (retention is an ops policy, see runbook).

    Why page files hold the raw response bytes (not NDJSON you re-serialized): a sha256 of
    the bytes proves fidelity, and you can always re-derive any other format later.

RUN IDENTIFIER
    One run_id per extraction attempt, e.g. Airflow's run_id + try_number, or a UUID.
    DECIDE: should a retried task reuse the same run_id (so partial files are overwritten /
    detected) or get a new one (so every attempt is auditable)? With immutable put_if_absent,
    reusing means the retry must tolerate ObjectAlreadyExists. Write your choice in ADR 0003.

TODOs
    1. Fill in `ManifestPage` and `Manifest` fields where marked.
    2. `Manifest.to_json_bytes` / `from_json_bytes`: stable key order, UTC ISO timestamps,
       explicit `schema_version` so you can evolve the manifest itself.
    3. `manifest_key(run_id, ingest_date)` and `page_key(...)` helpers - the ONLY places that
       format keys, so layout changes touch one file.
    4. `validate(manifest)`: internal consistency (row_count == sum of page row_counts, page
       numbers contiguous, window.start < window.end).

DONE WHEN: tests/unit/test_manifest.py passes (round-trip, validation failures).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

MANIFEST_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ManifestPage:
    key: str
    page_number: int
    row_count: int
    sha256: str  # of the raw bytes
    size_bytes: int
    # TODO(1): add http_status, fetched_at_utc, offset


@dataclass(frozen=True)
class Manifest:
    schema_version: int
    run_id: str
    dataset_id: str
    # Window actually queried (source-local naive) and the logical interval it came from (UTC):
    window_start: str
    window_end: str
    interval_start_utc: str | None
    interval_end_utc: str | None
    started_at_utc: str
    finished_at_utc: str
    source_count: int  # count(*) for the window, taken BEFORE paging
    row_count: int  # sum of rows across pages ("raw count")
    pages: list[ManifestPage] = field(default_factory=list)
    # TODO(2): add code_version (git sha / image tag), request_params template, client
    #   settings (page_size) - things you'd want when debugging "why does this run differ?"
    # TODO(3): add max_cursor_value seen (max last_modified_date among rows) - useful for
    #   freshness monitoring and gap detection.

    def to_json_bytes(self) -> bytes:
        raise NotImplementedError

    @classmethod
    def from_json_bytes(cls, data: bytes) -> Manifest:
        raise NotImplementedError


def page_key(prefix: str, ingest_date: date, run_id: str, page_number: int) -> str:
    raise NotImplementedError


def manifest_key(prefix: str, ingest_date: date, run_id: str) -> str:
    raise NotImplementedError


def validate(manifest: Manifest) -> None:
    """Raise ValueError (or a domain error) describing the first inconsistency."""
    raise NotImplementedError


def parse_started_at(manifest: Manifest) -> datetime:
    """Convenience; implement if you need it for gap detection."""
    raise NotImplementedError
