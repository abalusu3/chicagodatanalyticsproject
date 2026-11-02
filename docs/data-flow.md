# Data flow

One run, step by step. Each step names the module that owns it and what must be true afterwards.

## 0. Trigger
Airflow gives the run a logical interval `[data_interval_start, data_interval_end)` in UTC.

## 1. Extract (`ingestion/extract.py`)
1. Convert to the **source window** (Chicago-local, naive) and subtract `lookback_hours` from the start (`window.py`).
2. `count(*)` for the window → `source_count`.
3. Page through `GET /resource/v6vf-nfxy.json` ordered by `last_modified_date, sr_number`.
4. Write each response body, unmodified, to `chicago_311/ingest_date=…/run_id=…/page-NNNNN.json` with `put_if_absent`.
5. Write `_manifest.json` **last**.

*After:* either a complete run (manifest exists) or invisible orphan files.

## 2. Transform (`transform/raw_to_curated.py`)
1. Read **only** files named in manifests (never a prefix glob).
2. Drift check → cast → split valid / rejected → dedupe on `sr_number` (latest `last_modified_ts`).
3. Abort if the quarantine fraction exceeds the threshold.
4. `MERGE` into Delta (update only if source row is not older than target). Append rejected rows to quarantine.

*After:* curated unique by `sr_number`; rerunning gives the same table.

## 3. Quality (`quality/checks.py`)
Required fields, timestamp validity, duplicate ids, plausible values. `error` severity blocks the load; `warn` logs and emits metrics.

## 4. Load (`warehouse/load.py`)
One transaction: truncate staging → COPY → upsert fact (guarded by `last_modified_ts`) → rebuild aggregates for affected days → write `load_audit`.

## 5. Reconcile (`reconcile.py`)
Compare source / raw / curated / warehouse counts using the identities in [reconciliation.md](reconciliation.md).

## Why overlapping windows are safe
Run N reads `[start_N − lookback, end_N)`. Run N+1 starts at `end_N`, so it re-reads the last `lookback` of run N's span. Duplicates are expected in raw; dedupe + guarded merge make them harmless. This buys tolerance for rows the portal publishes late, at the cost of extra raw storage.
