"""Exception hierarchy.

RESPONSIBILITY
    Give every failure a *type* that says what the orchestrator should do next. Airflow's
    retry policy is blunt (retry N times); these classes let your code decide whether
    retrying can possibly help, and let messages tell the on-call human what to do.

DESIGN DECISIONS
    - Transient vs permanent is the core split. Retrying a schema-drift error 3 times just
      delays the page; not retrying a 503 wastes a perfectly recoverable run.
    - Every error carries `hint`: one actionable sentence (which runbook section, which
      command). "Actionable failure messages" is a stated requirement.

DONE WHEN
    - Every `raise` elsewhere in the project uses one of these (grep for bare
      `raise Exception` / `raise RuntimeError` should find nothing).
    - `str(err)` for each class includes context + hint (see tests/unit/test_errors.py).
"""

from __future__ import annotations


class PipelineError(Exception):
    """Base class. `context` is structured data for logs; `hint` is for humans."""

    retryable: bool = False

    def __init__(self, message: str, *, hint: str | None = None, **context: object) -> None:
        super().__init__(message)
        self.hint = hint
        self.context = context

    # TODO(1): override __str__ so it renders "message | key=value ... | hint: ...".
    #   Why: Airflow shows only str(exception) in the task log summary. If the hint is not in
    #   that string, nobody sees it.


class TransientSourceError(PipelineError):
    """Network blips, 429, 5xx. Safe to retry."""

    retryable = True


class SourceContractError(PipelineError):
    """Source responded, but not in a way we can use (bad JSON, unexpected shape, 4xx other
    than 429). Retrying won't help."""


class SchemaDriftError(PipelineError):
    """Breaking schema change detected. See docs/schema-policy.md."""


class DataQualityError(PipelineError):
    """A quality check at `error` severity failed. Carries which check and how many rows."""


class ReconciliationError(PipelineError):
    """Counts across layers disagree beyond tolerance. See docs/reconciliation.md."""


class WarehouseLoadError(PipelineError):
    """Warehouse write failed. Transaction must have rolled back; safe to rerun."""

    retryable = True
