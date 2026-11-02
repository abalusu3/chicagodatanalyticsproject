# Chicago 311 Data Platform (learning scaffold)

Ingest City of Chicago 311 service requests → immutable raw JSON → PySpark → Delta Lake → Postgres warehouse, orchestrated by Airflow, with data quality checks and cross-layer reconciliation.

> **Status: scaffold.** The framework, configuration, specs and docs exist. The pipeline logic is deliberately **unimplemented**: every stub raises `NotImplementedError` and every test body is a skipped spec. Nothing has run end-to-end. The Docker stack has not been built.

## Source (verified 2026-11-02)
- Dataset: "311 Service Requests", id `v6vf-nfxy`
- Endpoint: `https://data.cityofchicago.org/resource/v6vf-nfxy.json` (Socrata SODA)
- ~14.9M rows; 39 columns; `created_date` from 2018-07-01
- Timestamps: Chicago local time, no timezone. Numbers arrive as strings; null fields are omitted.
- Default `$limit` 1000, max 50,000 on SODA 2.0. Optional `X-App-Token` header; throttled requests get HTTP 429.

## Architecture in one picture
See [docs/architecture.md](docs/architecture.md). Short version:

```
SODA API → [extract] → raw JSON + manifest (MinIO/S3, immutable)
         → [transform] → curated Delta + quarantine
         → [quality] → [load] → Postgres (fact + aggregates)
         → [reconcile] (source vs raw vs curated vs warehouse)
```

## Repository map
| Path | What |
|---|---|
| `src/c311/` | Guided modules: each has a docstring with responsibility, TODOs, edge cases, "done when" |
| `dags/c311_pipeline.py` | Airflow DAG skeleton |
| `sql/warehouse/` | DDL and load SQL (guided) |
| `config/pipeline.yaml` | Non-secret settings |
| `tests/` | Skipped behavior specs + real fixture sanity tests |
| `tests/fixtures/` | **Real** 12-row API sample and a **synthetic** edge-case file |
| `docs/` | Architecture, data flow, schema policy, reconciliation, runbook, setup, ADRs |
| `.github/workflows/ci.yml` | Lint + fast tests (Spark/DAG jobs disabled until you enable them) |

## Suggested implementation order
Each step is small, testable on its own, and unlocks the next.

1. `config.py`, `errors.py`, `logging_utils.py`, `metrics.py` (foundation)
2. `ingestion/window.py` (pure functions; DST!)
3. `ingestion/manifest.py`
4. `storage/s3.py` (contract tests with moto)
5. `ingestion/client.py` (HTTP, retries, paging)
6. `ingestion/extract.py` → **first real milestone: raw files + manifest in MinIO**
7. `transform/schema.py`, then `transform/raw_to_curated.py` (+ `spark_session.py`)
8. `quality/checks.py`
9. `sql/warehouse/*.sql`, `warehouse/postgres.py`, `warehouse/load.py`
10. `reconcile.py`
11. `dags/c311_pipeline.py`
12. Enable the disabled CI jobs; add integration tests

## Quick start
```bash
make venv && source .venv/bin/activate
make probe-api          # look at the real API
make test               # fast suite
make lint
cp .env.example .env    # then see docs/setup.md before `make up`
```
Find your next task: `grep -rn "TODO(" src/ | head -30`.

## How to know a module is done
Each module docstring ends with **DONE WHEN**. Convert the matching skipped tests in `tests/` into real ones, delete the `skip`, and make them pass.

## Later extensions (out of scope for v1)
Cloud deployment (S3 + managed warehouse + MWAA), Spark cluster, Delta Change Data Feed, Prometheus/Grafana metrics, raw retention/lifecycle policy, chunked historical backfill tooling.

## Docs
[Architecture](docs/architecture.md) · [Data flow](docs/data-flow.md) · [Schema policy](docs/schema-policy.md) · [Reconciliation](docs/reconciliation.md) · [Runbook](docs/runbook.md) · [Setup](docs/setup.md) · [ADRs](docs/adr/)
