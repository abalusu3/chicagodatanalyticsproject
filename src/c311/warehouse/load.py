"""Curated Delta -> warehouse analytical tables.

RESPONSIBILITY
    Select the rows changed by this run from the curated table, stage them, upsert into the
    fact table, and rebuild the aggregates that those rows affect - all in ONE warehouse
    transaction.

WAREHOUSE MODEL (see sql/warehouse/*.sql, which you also write)
    c311.fact_service_request        1 row per sr_number (upserted)
    c311.dim_sr_type                 distinct (sr_type, sr_short_code)
    c311.agg_daily_requests          day x sr_type x community_area: counts, closed counts
    c311.agg_resolution_time_daily   day x sr_type: p50/p90 hours to close (optional)
    c311.load_audit                  one row per load: run_id, rows staged, rows upserted,
                                     started/finished, status. Reconciliation reads this.

HOW TO PICK "ROWS CHANGED BY THIS RUN"
    Option 1: curated rows whose `_run_id` is in the run set  (cheap; but a row merged by an
              earlier run and unchanged by this one is correctly skipped)
    Option 2: `last_modified_ts` within the physical window  (simple; re-stages overlap rows
              each run - harmless because the upsert is idempotent)
    Option 3: Delta Change Data Feed. (Later extension; powerful, more setup.)
    Choose and document in ADR 0004. Whichever you choose, the same run must stage the same
    rows when rerun.

IDEMPOTENT LOAD PATTERN
    BEGIN;
      TRUNCATE c311_staging.service_request;                     -- staging is per-load scratch
      COPY ... INTO staging;
      INSERT INTO fact ... SELECT ... FROM staging
        ON CONFLICT (sr_number) DO UPDATE SET ...
        WHERE EXCLUDED.last_modified_ts >= fact.last_modified_ts; -- never regress a row
      -- rebuild aggregates ONLY for days touched: a modified request can move between
      -- statuses on an OLD created_date, so affected days != just "today"
      DELETE FROM agg_daily_requests WHERE day IN (SELECT DISTINCT created_date FROM staging);
      INSERT INTO agg_daily_requests SELECT ... FROM fact WHERE created_date IN (...) GROUP BY ...;
      INSERT INTO load_audit ...;
    COMMIT;

HOW DATA CROSSES FROM SPARK TO POSTGRES (pick one, explain the trade-off in a comment)
    a) Spark JDBC write to the staging table (needs the Postgres JDBC jar on Spark's classpath;
       parallel, simplest code, Spark-coupled).
    b) Collect to the driver in batches and use PostgresWarehouse.bulk_load_staging (COPY):
       warehouse-agnostic interface, fine for this volume, driver memory bound.
    The Warehouse Protocol is shaped for (b). (a) is what you'd likely do at scale.

TODOs (in order)
    1. `select_changed_rows(spark, config, run_ids/window) -> DataFrame`.
    2. `stage_rows(wh, df)`.
    3. `upsert_fact(wh)` -> uses sql/warehouse/020_upsert_fact.sql.
    4. `rebuild_aggregates(wh)` -> uses sql/warehouse/030_rebuild_aggregates.sql.
    5. `load_run(...)` composing 1-4 in a single `wh.transaction()` + audit row; return counts.

EDGE CASES: zero changed rows (still write an audit row); NULL community_area in group-by
(do you want a NULL bucket or 'Unknown'? say which); sr_number reused/case-changed;
timestamps NTZ -> Postgres `timestamp without time zone`; load interrupted -> transaction
rolled back, rerun gives identical state.

DONE WHEN
    - tests/integration/test_warehouse_postgres.py: loading the same batch twice leaves row
      counts and aggregates unchanged; a stale row (older last_modified_ts) doesn't overwrite.
    - Aggregates equal an independent `GROUP BY` over the fact table (reconciliation check).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from c311.config import PipelineConfig
from c311.metrics import Metrics
from c311.warehouse.base import Warehouse

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession


@dataclass(frozen=True)
class LoadSummary:
    run_ids: list[str]
    rows_staged: int
    fact_rows_after: int
    aggregate_days_rebuilt: int


def select_changed_rows(spark: SparkSession, curated_uri: str, run_ids: list[str]) -> DataFrame:
    raise NotImplementedError


def stage_rows(wh: Warehouse, df: DataFrame, staging_table: str) -> int:
    raise NotImplementedError


def load_run(
    *,
    spark: SparkSession,
    wh: Warehouse,
    config: PipelineConfig,
    curated_uri: str,
    run_ids: list[str],
    metrics: Metrics,
) -> LoadSummary:
    raise NotImplementedError
