# Recovery runbook

> Written before the pipeline exists. Treat every command as a **hypothesis** and correct it the first time you actually use it. Items marked ⚠ need you to confirm behavior against your implementation.

## Principles
1. **Raw is the source of truth.** Everything downstream can be rebuilt from raw. Never delete raw during an incident.
2. Every stage is idempotent: rerunning is the default remedy.
3. Fix the cause, then rerun the smallest stage that heals the damage.

## First five minutes
1. Which task failed? (`extract` / `transform` / `quality` / `load` / `reconcile`.)
2. Read the exception's `hint` in the task log (errors carry one; see `errors.py`).
3. Filter logs by `run_id`.

## Scenarios

### A. `extract` fails (API down, 429s, timeouts)
- Cause is usually transient. Airflow retries with backoff.
- If retries are exhausted: wait, check <https://data.cityofchicago.org>, then **clear the task** in the UI (rerun the interval).
- Partial files from the failed attempt are harmless: no manifest ⇒ invisible.
- Persistent 429: set `SOCRATA_APP_TOKEN`; raise `min_request_interval_seconds`.

### B. Missed intervals / gaps
- List successful manifests and look for holes (`window.find_gaps`) ⚠.
- Backfill only the missing intervals:
  ```bash
  airflow dags backfill -s 2026-11-01 -e 2026-11-02 c311_pipeline
  ```
  ⚠ confirm flags for your Airflow version; safe to run twice because of idempotent writes.

### C. `transform` fails
- `SchemaDriftError`: see [schema-policy.md](schema-policy.md). Raw is safe. Do not loosen checks to force it through.
- Spark/S3A errors (`ClassNotFoundException`, `NoSuchMethodError`): jar version mismatch (see `spark_session.py`).
- Rerun after fixing. Curated is only changed by `MERGE`, which is idempotent.

### D. `quality` fails
- Read the failure message: check name, count, sample `sr_number`s.
- Look at the offending rows in the quarantine table / curated slice.
- If source data is genuinely bad: adjust severity/thresholds **in config with an ADR**, don't silently ignore.
- Retrying won't help; this task intentionally has `retries=0`.

### E. `load` fails
- The warehouse transaction rolled back; nothing partial exists. Clear and rerun.
- If it fails repeatedly: check Postgres connectivity, disk, and the staging table.

### F. `reconcile` fails
- See the failure table in [reconciliation.md](reconciliation.md). Identify which identity broke.
- Never "fix" by editing counts; find the missing rows.

### G. Corrupt or wrong curated table (bad deploy, bad merge)
1. Stop the DAG (pause).
2. Use Delta time travel to inspect history (`DESCRIBE HISTORY`) ⚠ and, if appropriate, `RESTORE TABLE … TO VERSION AS OF n` ⚠.
3. Or rebuild: write the table to a new path from **all** manifests, validate with reconciliation, then swap the config path.
4. Reload the warehouse for the affected range (upsert is idempotent).

### H. Wrong data in the warehouse
- Truncate nothing by hand. Re-run `load` for the affected run(s); aggregates for touched days are recomputed from the fact table.
- Whole-warehouse rebuild: reload from curated in monthly chunks ⚠ (design the chunked path in the DAG).

### I. Full rebuild from raw
```
raw (manifests) → transform (new curated path) → quality → load (new schema or truncated tables) → reconcile
```
Order manifests by `started_at_utc`; dedupe makes ordering mostly irrelevant, but the `last_modified_ts` guard protects you if it matters.

## Local stack problems
| Problem | Try |
|---|---|
| DAG not showing | scheduler logs; import error in `dags/` |
| MinIO buckets missing | `docker compose logs minio-init` |
| Postgres init not re-run | init scripts run only on an empty volume: `docker compose down -v` (**destroys local data**) |

## After every incident
Add what you learned here, and an ADR if a decision changed.
