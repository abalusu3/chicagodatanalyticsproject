"""Monitoring hook.

RESPONSIBILITY
    A tiny seam where the pipeline reports numbers (rows extracted, rows quarantined, run
    duration, freshness lag). Today it just logs; later you can plug in StatsD/Prometheus/
    CloudWatch without touching call sites. Advanced monitoring is a LATER EXTENSION.

METRICS TO EMIT (names are part of your operational contract; keep them stable)
    c311.extract.rows            counter   rows written to raw this run
    c311.extract.pages           counter
    c311.extract.http_retries    counter   a rising trend = source degrading
    c311.transform.rows_in/out   gauge
    c311.transform.quarantined   gauge
    c311.quality.check_failed    counter   tag: check name, severity
    c311.warehouse.rows_loaded   gauge
    c311.freshness.lag_seconds   gauge     now() - max(last_modified_date) in warehouse

DONE WHEN
    - A `Metrics` implementation exists that logs via log_event, and call sites depend only
      on the Protocol (so tests can pass a fake that records calls).
"""

from __future__ import annotations

from typing import Protocol


class Metrics(Protocol):
    def incr(self, name: str, value: float = 1, **tags: str) -> None: ...
    def gauge(self, name: str, value: float, **tags: str) -> None: ...


class LogMetrics:
    """TODO(1): implement Metrics by emitting a structured log line per call.

    Why log-based first: zero infra, and it makes `docker compose logs | grep c311.` a
    functional dashboard while you build everything else.
    """

    def incr(self, name: str, value: float = 1, **tags: str) -> None:
        raise NotImplementedError

    def gauge(self, name: str, value: float, **tags: str) -> None:
        raise NotImplementedError


# TODO(2) (optional, later): airflow `on_failure_callback` helper here that formats
#   dag_id/task_id/run_id/log_url + the exception's `hint` into a message for Slack/email.
