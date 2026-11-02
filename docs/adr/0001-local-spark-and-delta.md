# ADR 0001: Spark in local mode inside the Airflow image; Delta Lake for curated data

- **Status:** Proposed (pre-filled by the scaffold; confirm or change)
- **Date:** 2026-11-02

## Context
One person, one laptop. The data is ~15M rows total (source metadata) with small incremental batches. We still want to demonstrate PySpark and Delta idioms (MERGE, time travel).

## Options considered
1. **Spark local mode in the Airflow container**: simplest; no cluster; Java in the image.
2. **Separate Spark master/worker containers**: closer to production, more moving parts.
3. **Skip Spark (pandas/DuckDB)**: faster locally but misses the stated goal.

## Decision
Option 1. Isolate session creation in `transform/spark_session.py` so a cluster is a one-file change.

## Consequences
- Good: fewer services; fast feedback.
- Bad: Spark shares memory with Airflow workers; no realistic shuffle/skew behavior.
- Revisit when: initial historical load is too slow/large for local mode.
