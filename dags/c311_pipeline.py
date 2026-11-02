"""Airflow DAG skeleton: extract -> transform -> quality -> load -> reconcile.

RESPONSIBILITY
    Orchestration only: schedule, task order, retries, backfill rules, passing SMALL values
    (run_id, manifest keys, counts) between tasks. Business logic lives in `c311.*`; tasks
    here are thin wrappers that build config/clients and call one function each.

TARGET: Airflow 2.10 (pinned in docker/airflow/Dockerfile). Use the TaskFlow API (@task).

TASK BOUNDARIES (why each is separate: failure isolation + independent retry)
    extract      API -> raw files + manifest        retry: yes (transient network)
    transform    manifests -> curated Delta         retry: once (Spark failures are rarely
                                                    transient; but a lost executor is)
    quality      checks on the new curated slice    retry: NO (deterministic; retrying a
                                                    failed check changes nothing)
    load         curated -> warehouse (1 txn)       retry: yes (transaction rolled back)
    reconcile    compare four counts                retry: NO

SETTINGS TO DECIDE (and be ready to defend each)
    schedule          e.g. hourly or daily. Data lag + lookback_hours must be consistent with it.
    catchup           True enables automatic backfill of missed intervals. Is that what you
                      want for a source with 15M historical rows? (Probably: catchup=False and an
                      explicit, bounded `airflow dags backfill` for history - say why.)
    max_active_runs   1. Parallel runs would race on the Delta MERGE and the warehouse txn.
    default_args      retries, retry_delay (+ exponential backoff, max_retry_delay), execution_timeout,
                      on_failure_callback (hook from c311.metrics, later extension)
    depends_on_past   think about it: do you want run N+1 blocked when N failed? (With
                      overlapping lookback windows, N+1 partially heals N - another reason to
                      explain the model clearly.)

BACKFILL BEHAVIOR (docs/runbook.md must match what you build)
    `data_interval_start/end` are the ONLY time inputs to extract. No `datetime.now()` in tasks.
    Re-running a past interval must re-extract exactly that window (plus lookback), idempotently.
    Historical initial load: a separate, chunked path (e.g. monthly intervals) so one task
    never tries to pull 15M rows. Design it; implement it last.

TODOs (in order)
    1. Define the DAG (dag_id="c311_pipeline", tags, doc_md pointing to docs/runbook.md).
    2. `extract` task: build run_id (from `run_id` + `ti.try_number`, see ADR 0003), compute window
       via c311.ingestion.window.to_source_window(data_interval_*), call extract_window; return
       ExtractSummary as a dict.
    3. `transform` task: gets manifest keys (from XCom, or by listing manifests for the run_id -
       which is more robust if XCom is lost? Decide).
    4. `quality` task, `load` task, `reconcile` task.
    5. Wire dependencies. Consider a final `notify` task with trigger_rule="all_done"
       (later extension).
    6. Make sure the module imports FAST: no heavy imports (pyspark, boto3 sessions) at module
       top level; import inside task functions. The scheduler re-parses this file constantly.

DONE WHEN
    - `docker compose up` shows the DAG without import errors in the UI.
    - Unpausing and triggering one interval goes green end-to-end.
    - Clearing the extract task and rerunning does not change curated/warehouse counts.
    - `airflow dags backfill -s <d1> -e <d2> c311_pipeline` is safe to run twice.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task  # noqa: F401  (task used once you implement below)

DEFAULT_ARGS = {
    "owner": "data-eng",
    "retries": 3,  # TODO(you): per-task overrides per the table above
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=1),
}


@dag(
    dag_id="c311_pipeline",
    start_date=datetime(2026, 11, 1),  # TODO(you): choose deliberately; it anchors backfills
    schedule=None,  # TODO(you): e.g. "@hourly" / "@daily" once tasks work
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    tags=["c311"],
    doc_md=__doc__,
)
def c311_pipeline() -> None:
    # TODO(2-5): define @task functions and wire:
    #   extract_summary = extract()
    #   transformed     = transform(extract_summary)
    #   checked         = quality(transformed)
    #   loaded          = load(checked)
    #   reconcile(loaded)
    pass


c311_pipeline()
