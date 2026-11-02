"""Cross-layer reconciliation.

RESPONSIBILITY
    Compare row counts across source -> raw -> curated -> warehouse for ONE run/window and
    explain every difference. Four numbers that look similar but mean different things;
    the discipline is knowing which differences are expected, which are tolerable, and
    which are bugs. Read docs/reconciliation.md first (it's the spec for this module).

THE FOUR COUNTS (all scoped to the same window / run set)
    source_count     count(*) from the API for the window, taken before paging.
                     Meaning: what the portal claimed existed when we started.
    raw_count        sum of page row counts in the manifests (and re-verify against the
                     files: a checksum/count mismatch means storage corruption).
                     Meaning: rows we fetched. Includes duplicates across overlapping runs.
    curated_count    distinct sr_numbers from this run's raw rows that landed in curated
                     (inserted + updated + skipped_stale), plus rejected_count (quarantine).
                     Meaning: unique business entities after dedupe.
    warehouse_count  rows in fact_service_request that this load touched / match the window.

EXPECTED RELATIONSHIPS (assertions you implement)
    1. source_count  ~= raw_count            tolerance from config (source mutates mid-run)
    2. raw_count = rejected + duplicates_dropped + curated_distinct   (exact)
       Every raw row is accounted for; nothing vanishes. Order of operations matters:
       rejected rows are removed BEFORE dedupe, so valid = raw - rejected and
       curated_distinct = valid - duplicates_dropped.
    3. curated_distinct = inserted + updated + skipped_stale          (exact, from MERGE metrics)
    4. warehouse rows for this run's keys = curated_distinct          (exact)

DESIGN DECISIONS
    - Return a structured `ReconciliationReport` (values + each check's pass/fail + a plain
      English explanation), then render it. Never just a boolean.
    - Failing reconciliation should fail the DAG *after* load but be loud and specific; decide
      whether warn-level differences (tolerance band) should page anyone.
    - Persist reports (warehouse `load_audit` or a JSON object in storage) so you can show
      trend lines: "drift is always +3 rows" is a finding.

TODOs (in order)
    1. `gather_counts(...)` - one function per layer; each is small and separately testable.
    2. `compare(counts, cfg) -> ReconciliationReport` - pure function; test it exhaustively
       with synthetic counts (no Spark/DB needed).
    3. `render(report) -> str` - the actionable message.
    4. `reconcile_run(...)` composing; raises ReconciliationError on breach.

EDGE CASES: zero rows everywhere (pass, with an explicit note); rerun of same window (raw
count doubles in total storage but not for the run); source_count 0 but raw > 0; windows
whose rows were modified after extraction.

DONE WHEN: tests/unit/test_reconcile.py passes; you can explain every line of a sample report
to an interviewer without looking at the code.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LayerCounts:
    source: int
    raw: int
    raw_rejected: int  # rows sent to quarantine
    raw_duplicates_dropped: int  # rows removed by dedupe within the batch
    curated_distinct: int  # distinct sr_number merged this run
    warehouse: int


@dataclass(frozen=True)
class CheckOutcome:
    name: str
    passed: bool
    expected: str
    actual: str
    explanation: str  # plain English: why this might differ / what to do


@dataclass(frozen=True)
class ReconciliationReport:
    run_ids: list[str]
    counts: LayerCounts
    outcomes: list[CheckOutcome] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(o.passed for o in self.outcomes)


def compare(counts: LayerCounts, source_vs_raw_tolerance_fraction: float) -> list[CheckOutcome]:
    raise NotImplementedError


def render(report: ReconciliationReport) -> str:
    raise NotImplementedError


def reconcile_run(*args: object, **kwargs: object) -> ReconciliationReport:
    """TODO: define the real signature once gather_counts exists. Raise ReconciliationError
    (with the rendered report as the message and a runbook hint) when report.ok is False."""
    raise NotImplementedError
