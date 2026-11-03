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

import logging
from typing import Protocol

from c311.logging_utils import log_event

_logger = logging.getLogger("c311.metrics")


class Metrics(Protocol):
    def incr(self, name: str, value: float = 1, **tags: str) -> None: ...
    def gauge(self, name: str, value: float, **tags: str) -> None: ...


class LogMetrics:
    """Metrics implementation that emits one structured log line per call."""

    def incr(self, name: str, value: float = 1, **tags: str) -> None:
        log_event(_logger, "metric", metric=name, kind="counter", value=value, tags=tags)

    def gauge(self, name: str, value: float, **tags: str) -> None:
        log_event(_logger, "metric", metric=name, kind="gauge", value=value, tags=tags)


# TODO(2) (optional, later): airflow `on_failure_callback` helper here that formats
#   dag_id/task_id/run_id/log_url + the exception's `hint` into a message for Slack/email.
