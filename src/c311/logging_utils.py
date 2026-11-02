"""Structured logging with run context.

RESPONSIBILITY
    Make every log line attributable to a `run_id` and a `stage` so that, during an incident,
    you can filter logs for one run across ingestion, Spark, and warehouse tasks.

DESIGN DECISIONS
    - Use stdlib `logging` + a JSON formatter you write (~20 lines). No new dependency.
    - run_id travels via `contextvars`, not by passing a logger everywhere.
    - Never log secrets, full request headers (X-App-Token!), or full row payloads.

DONE WHEN
    - `log_event(logger, "page_fetched", rows=1000, offset=0)` emits one JSON line containing
      run_id, stage, timestamp (UTC ISO-8601), level, event, and the extra fields.
    - tests/unit/test_logging.py passes (including "token never appears in output").
"""

from __future__ import annotations

import logging
from contextvars import ContextVar

run_id_var: ContextVar[str | None] = ContextVar("run_id", default=None)
stage_var: ContextVar[str | None] = ContextVar("stage", default=None)


def configure_logging(level: str = "INFO") -> None:
    """TODO(1): install a root handler with a JSON formatter; idempotent (calling twice must
    not duplicate handlers - Airflow tasks re-import modules).

    Formatter should add run_id/stage from the ContextVars above.
    """
    raise NotImplementedError


def bind_run(run_id: str, stage: str) -> None:
    """TODO(2): set the context vars. Airflow: call at the top of each task callable."""
    raise NotImplementedError


def log_event(logger: logging.Logger, event: str, **fields: object) -> None:
    """TODO(3): logger.info with `event` and `fields` attached as structured extras.

    EDGE CASE: field names that collide with LogRecord attributes ("name", "message"...)
    raise KeyError in stdlib logging. Namespace them (e.g. under a `data` key).
    """
    raise NotImplementedError
