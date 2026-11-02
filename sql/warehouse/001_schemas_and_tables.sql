-- DDL for the analytical warehouse (Postgres dialect). YOU write the table definitions.
-- Must be idempotent: CREATE ... IF NOT EXISTS, safe to run on every deploy.
-- Keep dialect-specific bits (types, ON CONFLICT) in these files so a cloud warehouse swap is
-- a rewrite of sql/, not of Python.

-- TODO(1): CREATE SCHEMA IF NOT EXISTS c311; CREATE SCHEMA IF NOT EXISTS c311_staging;

-- TODO(2): c311.fact_service_request
--   PRIMARY KEY (sr_number)  <- this is what makes upserts idempotent
--   Columns mirror curated (see src/c311/transform/schema.py): timestamps as
--   `timestamp without time zone` (source is Chicago local; do NOT silently use timestamptz),
--   zip_code / police_district as TEXT (leading zeros), ward/community_area SMALLINT.
--   Add `created_date DATE` and an index that helps agg rebuilds (created_date).
--   Add _run_id, _loaded_at (default now()).

-- TODO(3): c311.dim_sr_type (sr_type PK, sr_short_code). How do you populate it idempotently?

-- TODO(4): c311.agg_daily_requests
--   PRIMARY KEY (day, sr_type, community_area)  -- NULL community_area breaks PK semantics in
--   Postgres; decide: COALESCE to a sentinel (e.g. -1 / 'Unknown') or a surrogate key.
--   Measures: requests_created, requests_closed, requests_open_at_load.

-- TODO(5): c311.load_audit (run_id, started_at, finished_at, rows_staged, status, ...)
--   Reconciliation reads the warehouse count from here and from the fact table.

-- TODO(6): c311_staging.service_request: same columns as the fact minus lineage defaults,
--   no constraints (it's scratch; truncated each load). UNLOGGED is a reasonable Postgres choice.
