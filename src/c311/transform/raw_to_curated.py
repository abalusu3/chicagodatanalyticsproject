"""PySpark transformation: raw JSON -> curated Delta (+ quarantine).

RESPONSIBILITY
    Read the raw files of specific, manifest-confirmed runs; parse/cast/standardize; split
    good rows from bad ones; deduplicate; MERGE into the curated Delta table idempotently.
    Pure DataFrame functions are separated from I/O so the logic is testable on tiny local
    DataFrames (mark such tests `@pytest.mark.spark`).

STAGES (implement as separate functions; each is independently testable)
    A. read_raw(spark, store, manifest_keys) -> DataFrame
         - Only files listed in the manifests (NEVER glob a prefix: orphans from failed runs
           would sneak in). Use the manifest page keys.
         - Explicit RAW_SCHEMA; add lineage columns (_run_id, _source_file via
           input_file_name() or by reading per-manifest, _ingested_at_utc).
         - multiLine=true: each page file is one JSON ARRAY, not NDJSON. Look up why that matters.
    B. parse_and_cast(df) -> DataFrame
         - Trim strings; empty string -> NULL (decide for which columns).
         - Parse timestamps with an explicit pattern (the source has milliseconds, no zone).
           try_to_timestamp-style behavior: a bad value must become NULL + a recorded reason,
           not an exception. (Spark ANSI mode on/off changes this - know which you run.)
         - Cast ward/community_area/etc. safely; `duplicate`/`legacy_record` -> boolean.
         - Compute _row_hash over business columns (for change detection / debugging).
    C. split_valid_invalid(df) -> (valid_df, rejected_df)
         - Hard-reject rows with null/blank sr_number, unparseable created/last_modified.
         - rejected_df keeps the ORIGINAL raw columns + `_reject_reasons: array<string>`.
         - Soft problems (e.g. lat/long out of Chicago) are NOT rejected here; they're flagged
           and handled by quality/checks.py with severity. Draw this line deliberately: what
           makes a row unusable vs. suspicious?
    D. dedupe_latest(df) -> DataFrame
         - Within the batch, keep one row per sr_number: the max(last_modified_ts); break ties
           deterministically (e.g. by _ingested_at_utc then _source_file). Window function
           row_number() over (partition by sr_number order by ... desc).
         - Why needed: overlapping lookback windows return the same row repeatedly.
    E. merge_into_curated(spark, df, table_path) -> MergeMetrics
         - DeltaTable.merge on sr_number.
         - whenMatchedUpdateAll ONLY IF source.last_modified_ts >= target.last_modified_ts.
           Why: an old backfill must never overwrite a newer record already in the table.
         - whenNotMatchedInsertAll.
         - Create the table first if absent (with CURATED_SCHEMA), instead of relying on the
           first write's inferred schema. Decide partitioning (or none: ~15M rows total is
           small; partitioning by created_date's month/year can hurt more than help).
         - Return counts (inserted/updated/unchanged) - read them from Delta's operation
           metrics (DESCRIBE HISTORY) rather than recounting.
    F. write_quarantine(...) append-only Delta table of rejected rows with run id + reasons.

IDEMPOTENCY
    Rerunning the same manifests must yield an identical curated table (row count AND
    contents). Prove it in a test: run E twice, compare. Note the nuance: quarantine is
    append-only, so a rerun would duplicate quarantine rows unless you key it by
    (run_id, row identity) - decide how to avoid that.

SCHEMA POLICY HOOK
    Before merging call schema.detect_drift on the raw field set; additive drift: log + proceed
    per policy; breaking: raise SchemaDriftError BEFORE touching curated.

EDGE CASES: same sr_number with identical last_modified_ts but different content (tie!);
sr_number with whitespace/case differences; a 200-OK page containing zero rows; a manifest
whose pages are already merged (rerun); very first run (table doesn't exist).

DONE WHEN
    - tests/unit/test_transform.py passes (pure-DF tests need Spark; mark accordingly).
    - Running transform twice over the same run leaves curated count unchanged.
    - quality checks (quality/checks.py) pass on the curated slice produced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from c311.config import PipelineConfig
from c311.metrics import Metrics
from c311.storage.base import ObjectStore

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


@dataclass(frozen=True)
class MergeMetrics:
    rows_in: int  # rows handed to MERGE (after dedupe)
    inserted: int
    updated: int
    skipped_stale: int  # matched but older than target -> not applied


@dataclass(frozen=True)
class TransformSummary:
    run_ids: list[str]
    raw_rows: int  # rows read from raw files
    rejected_rows: int  # -> quarantine
    deduped_rows: int  # distinct sr_number after dedupe
    merge: MergeMetrics


def read_raw(spark: SparkSession, store: ObjectStore, manifest_keys: list[str]) -> DataFrame:
    raise NotImplementedError


def parse_and_cast(df: DataFrame) -> DataFrame:
    raise NotImplementedError


def split_valid_invalid(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    raise NotImplementedError


def dedupe_latest(df: DataFrame) -> DataFrame:
    raise NotImplementedError


def merge_into_curated(spark: SparkSession, df: DataFrame, table_uri: str) -> MergeMetrics:
    raise NotImplementedError


def write_quarantine(spark: SparkSession, rejected: DataFrame, table_uri: str) -> int:
    raise NotImplementedError


def run_transform(
    *,
    spark: SparkSession,
    store: ObjectStore,
    manifest_keys: list[str],
    config: PipelineConfig,
    metrics: Metrics,
) -> TransformSummary:
    """Compose A..F. TODO: order = read -> drift check -> cast -> split -> dedupe -> quality
    gate on thresholds (max_quarantine_fraction) -> merge -> quarantine write -> summary.

    Think: should the quarantine fraction gate run BEFORE the merge (so a catastrophic batch
    never reaches curated)? Almost certainly yes. Why?
    """
    raise NotImplementedError
