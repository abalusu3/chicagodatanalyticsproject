# ADR 0002: Interval-driven extraction windows with a lookback overlap

- **Status:** Proposed (confirm after you implement `window.py` and can prove the claims)
- **Date:** 2026-11-02

## Context
The source exposes `last_modified_date` (Chicago local, no timezone). Records can be updated after creation, and the portal may publish changes with lag. We need incremental extraction that is also safely backfillable.

## Options considered
1. **Stored high-water mark** (read last max `last_modified_date`): simple, but depends on mutable state, can't deterministically replay a past interval, and silently skips late-published rows.
2. **Airflow interval windows, no overlap**: deterministic replay, but late-published rows are lost.
3. **Interval windows + lookback overlap** (chosen): deterministic and tolerant of late rows; duplicates handled by idempotent merge.

## Decision
Option 3. Window = `[interval_start − lookback_hours, interval_end)`. Manifests record the window, enabling gap detection.

## Consequences
- Good: replayable; no external state; self-healing within the lookback.
- Bad: extra raw storage and API calls proportional to lookback / interval.
- Open questions to settle: lookback size (measure real publish lag before choosing 6h); OFFSET vs keyset paging; DST handling.
- Revisit when: measured publish lag exceeds the lookback.
