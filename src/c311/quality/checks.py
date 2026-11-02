"""Data quality checks.

RESPONSIBILITY
    Declarative checks over a curated DataFrame slice, each returning a `CheckResult`.
    A runner aggregates results, emits metrics, and raises DataQualityError if any
    `error`-severity check failed. Checks don't fix data; they report.

CHECKS REQUIRED
    1. required_fields      sr_number, sr_type, status, created_ts, last_modified_ts, owner_department
                            non-null and non-blank. (Source metadata showed 0 nulls for these;
                            VERIFY on your data, don't just trust it.) severity: error
    2. valid_timestamps     - parsed (not null) - created_ts <= last_modified_ts
                            - closed_ts >= created_ts when present
                            - not in the future beyond max_future_skew_minutes
                            - not before 2018-07-01 (verified min created_date) -> warn
                            Real data is messy: measure how often each fails BEFORE choosing
                            error vs warn. A check that always fails gets ignored.
    3. duplicate_identifiers  count of sr_number appearing >1 time in curated. severity: error
                            (curated must be unique by construction; a hit means the merge is
                            broken). Also report duplicates in the *incoming batch* (expected
                            after lookback overlap; informational).
    4. reasonable_values    - ward in 1..50, community_area in 1..77, created_hour 0..23,
                              created_day_of_week 1..7 (observed 1=Sunday in one sample; verify)
                            - lat/long inside config.quality.chicago_bbox (rows w/ NULL coords are
                              legitimately common: ~14k nulls in metadata; don't flag nulls here)
                            - status / origin within the *observed* value set -> warn on unseen
                              values (a new status is a business change worth knowing, not a failure).
                              You must discover the observed set yourself (my group-by query timed out).
    5. (optional) freshness  max(last_modified_ts) vs now -> warn if stale.

DESIGN DECISIONS
    - Return failing COUNTS and a small sample of offending keys (never whole rows - PII-ish
      addresses). Actionable message = what failed + how many + example sr_numbers + hint.
    - Severity is data (config), not hard-coded `if`s, so you can tune without code changes.
    - Express checks as functions DataFrame -> CheckResult so each unit test needs a 5-row DF.

TODOs (in order)
    1. Implement each check function below.
    2. `run_checks(df, config, metrics) -> list[CheckResult]`.
    3. `enforce(results)`: raise DataQualityError summarizing ALL failures at once (not just
       the first) with hints.
    4. Decide where it runs: on the batch BEFORE merge (blocks bad data) or on the table
       AFTER (finds systemic problems)? Probably both with different checks; write that down.

DONE WHEN: tests/unit/test_quality.py passes; a deliberately corrupted fixture yields a message
you'd be happy to see at 3am.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from c311.config import QualityConfig
from c311.metrics import Metrics

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


class Severity(StrEnum):
    ERROR = "error"
    WARN = "warn"


@dataclass(frozen=True)
class CheckResult:
    name: str
    severity: Severity
    passed: bool
    failing_rows: int
    total_rows: int
    sample_keys: list[str] = field(default_factory=list)  # a few sr_numbers, max ~5
    message: str = ""


def check_required_fields(df: DataFrame) -> CheckResult:
    raise NotImplementedError


def check_valid_timestamps(df: DataFrame, cfg: QualityConfig) -> CheckResult:
    raise NotImplementedError


def check_duplicate_identifiers(df: DataFrame) -> CheckResult:
    raise NotImplementedError


def check_reasonable_values(df: DataFrame, cfg: QualityConfig) -> CheckResult:
    raise NotImplementedError


def run_checks(df: DataFrame, cfg: QualityConfig, metrics: Metrics) -> list[CheckResult]:
    raise NotImplementedError


def enforce(results: list[CheckResult]) -> None:
    raise NotImplementedError
