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

import json
import sys
from datetime import datetime, timezone

_HANDLER_MARK = "_c311_handler"
_SENSITIVE_KEYS = {"x-app-token", "authorization", "password", "secret", "token"}


def _redact(value: object) -> object:
    """Mask values under sensitive keys, recursively (headers dicts are nested)."""
    if isinstance(value, dict):
        return {
            k: "***" if str(k).lower() in _SENSITIVE_KEYS else _redact(v)
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(v) for v in value]
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = dict(getattr(record, "data", {}))  # extra fields first...
        payload.update(                               # ...so core keys can't be overwritten
            timestamp=datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            level=record.levelname,
            event=record.getMessage(),
            run_id=run_id_var.get(),
            stage=stage_var.get(),
            logger=record.name,
        )
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)  # default=str: never crash on odd types


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    for h in list(root.handlers):  # remove only OUR previous handler
        if getattr(h, _HANDLER_MARK, False):
            root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    setattr(handler, _HANDLER_MARK, True)
    root.addHandler(handler)
    root.setLevel(level)


def bind_run(run_id: str, stage: str) -> None:
    run_id_var.set(run_id)
    stage_var.set(stage)


def log_event(logger: logging.Logger, event: str, **fields: object) -> None:
    # Fields go under a single "data" extra, so a field named "name" or "message"
    # can't collide with LogRecord attributes.
    logger.info(event, extra={"data": _redact(fields)})
