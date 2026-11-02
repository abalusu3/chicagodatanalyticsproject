# ADR 0004: How the warehouse load selects changed rows

- **Status:** Proposed (you decide; see options)
- **Date:** 2026-11-02

## Context
After transform, only some curated rows need to reach the warehouse. The selection must be the same on a rerun of the same run.

## Options considered
1. **By `_run_id`**: exact set merged by this run; cheap; misses rows if a previous load failed after transform succeeded for an earlier run (need to load all unloaded runs).
2. **By `last_modified_ts` in the physical window**: simple, re-stages overlap rows; harmless due to idempotent upsert.
3. **Delta Change Data Feed**: precise and scalable; extra setup. Later extension.

## Decision
TODO(you). Whichever you choose, state how a failed-then-skipped load gets healed.

## Consequences
TODO(you).
