"""Extraction window math.

RESPONSIBILITY
    Pure functions that turn an Airflow data interval (or manual dates) into the source query
    window, including the lookback overlap, and that find gaps between successful runs.
    No I/O, no clock reads -> trivially unit-testable. This is the heart of "incremental
    extraction" and "backfill behavior", so get it right before touching anything else.

THE MODEL (ADR 0002)
    - Each run owns a *logical interval* [interval_start, interval_end) from Airflow.
    - It queries a *physical window* [interval_start - lookback, interval_end).
    - Overlaps between consecutive runs are intentional: they re-fetch recently modified rows
      that the portal published late. Duplicates are removed downstream (merge on sr_number).
    - Backfilling an old interval re-extracts the same physical window: deterministic.

TIMEZONES (the classic bug factory)
    Airflow gives tz-aware UTC datetimes. The source speaks Chicago local time with NO offset.
    Convert at exactly one boundary - here - using zoneinfo("America/Chicago"), then drop the
    tzinfo for the query string. Think about DST:
      - spring forward: 02:00-03:00 local doesn't exist
      - fall back: 01:00-02:00 local happens twice (floating timestamps are ambiguous!)
    Decide what you do (e.g. widen the window by the DST shift rather than try to be exact,
    relying on dedup) and write it in a comment.

TODOs (in order)
    1. to_source_window(interval_start_utc, interval_end_utc, lookback_hours, tz_name) -> Window
    2. format_soda_timestamp(dt) -> str  e.g. "2026-11-02T06:00:11.000" (match the source format)
    3. find_gaps(successful_intervals) -> list[tuple[datetime, datetime]]: detect holes
       between manifests so the runbook can say "these intervals need backfilling".

EDGE CASES: lookback_hours=0; interval shorter than lookback; interval crossing DST change;
naive datetime input (reject it - raise ValueError with a clear message).

DONE WHEN: tests/unit/test_window.py passes, including the DST cases.
"""

from __future__ import annotations

from datetime import datetime

from c311.ingestion.client import Window


def to_source_window(
    interval_start_utc: datetime,
    interval_end_utc: datetime,
    lookback_hours: int,
    tz_name: str,
) -> Window:
    raise NotImplementedError


def format_soda_timestamp(dt: datetime) -> str:
    raise NotImplementedError


def find_gaps(
    successful_intervals: list[tuple[datetime, datetime]],
) -> list[tuple[datetime, datetime]]:
    raise NotImplementedError
